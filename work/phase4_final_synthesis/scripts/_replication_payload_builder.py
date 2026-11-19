"""Build sanitized JSON payloads (DATA_RUNS [8 Flagship + 50 Runs], DATA_DATASETS [40], DATA_FORMULAS [194], DATA_OVERLAP [8]) for Tab 4."""
from __future__ import annotations

import re

from _public_taxonomy import sanitize_public_prose
from carbon_als.accessions import legacy_to_accession, translate_legacy_tokens_in_prose

FLAGSHIP_DEFS = [
    ("FLAGSHIP-EALS-030", "Monograph #1 · SARM1 (EALS-030)", "pipelines/flagship/reproduce_EALS_030_sarm1.py", "DS_PDB_9TZY;DS_PDB_7DJT;DS_PDB_7ANW", "EALS-030;EALS-002", "Verifies PDB 9TZY 3-chain BEXi filament gluing, gnomAD LOEUF=1.1432, Leahey ~2.8x empirical BEXi washout spike vs theoretical 8-mer ceiling and monotonic T-Lock, and default Krus 2022 Bliss additivity."),
    ("FLAGSHIP-EALS-031", "Monograph #2 · Aldesleukin (EALS-031)", "pipelines/flagship/reproduce_EALS_031_aldesleukin.py", "DS045_TRAUT", "EALS-031", "Verifies MIROCALS BioVendor ELISA 750-3,700 pg/mL stratum, Trautwig MS NEFL vs NEFH r=0.278 (n=51 Emory TMT nested in n=77 DIA), and proportional-hazards Schoenfeld Ph3 sizing (247 events at HR=0.70)."),
    ("FLAGSHIP-EALS-001", "Monograph #3 · UNC13A (EALS-001)", "pipelines/flagship/reproduce_EALS_001_unc13a.py", "DS_CRYPTIC;DS029_SPILL;DS_GENCODE_V46_TX", "EALS-001", "Verifies Brown UNC13A cryptic junction dPSI, Spillman synaptosome Munc13-1 loss, rs12973192/rs12608932 genotype-stratified rules, and promoted Clean >=2mm Lead #2 chr19:17642537-17642554(-)."),
    ("FLAGSHIP-EALS-006", "Monograph #4 · KCNQ2 (EALS-006)", "pipelines/flagship/reproduce_EALS_006_kcnq2.py", "DS_CRYPTIC;DS_PDB_7CR2;DS_GENCODE_V46_TX", "EALS-006;EALS-003;EALS-005", "Verifies Exon-5 126-bp (42-aa) in-frame skipping, PDB 7CR2 Trp236 2.97A retigabine H-bond, post-assembly ER co-trapping across 4:0 vs 2:2 Kv7.2:Kv7.3 channels, and Lead #3 off-target hygiene."),
    ("FLAGSHIP-EALS-002", "Monograph #5 · STMN2 (EALS-002)", "pipelines/flagship/reproduce_EALS_002_stmn2.py", "DS_CRYPTIC;DS029_SPILL;DS_GENCODE_V46_TX", "EALS-002;EALS-030", "Verifies STMN2 Exon-2a cryptic junction dPSI=+0.482, Spillman C9-FTD homogenate -0.4825 log2FC (-28.4%, p=0.014, FDR=0.113), and promoted Clean >=2mm Lead #2 chr8:79616829-79616846(+)."),
    ("FLAGSHIP-EALS-007", "Monograph #6 · IL1RL1 (EALS-007)", "pipelines/flagship/reproduce_EALS_007_il1rl1.py", "DS_EDIN_PB;DS031_ZHANG;DS_PDB_4KC3", "EALS-007", "Verifies Edinburgh donor-collapsed endothelial +3.106 log2CPM (p=0.00641, n=7 Ctrl), Zhang 55-um Visium +3.76 (within-donor spot pseudoreplicated across N=14 donors), GENCODE v46 sST2 intron-8 polyA exon, and PDB 4KC3."),
    ("FLAGSHIP-EALS-034", "Monograph #7 · ATG4B (EALS-034)", "pipelines/flagship/reproduce_EALS_034_atg4b.py", "DS029_SPILL;DS001_COUNTS;DS_PDB_2Z0D", "EALS-034", "Verifies Spillman C9-FTD homogenate ATG4B -0.4905 log2FC (p=0.0227), NYGC cervical RIN+GC OLS beta=-0.1642, PDB 2Z0D 27 LC3B contacts, and promoted Lead #2 chr2:241668970-241668987(+)."),
    ("FLAGSHIP-EALS-037", "Monograph #8 · CELF5 (EALS-037)", "pipelines/flagship/reproduce_EALS_037_celf5.py", "DS001_COUNTS;DS005_BYE;DS_GENCODE_V46_TX", "EALS-037", "Verifies NYGC cervical RIN+GC beta=-0.4020, #1 neuronal-mass-adjusted tSTMN2 coupling (1.90% cervical / 0.14% lumbar tail), gnomAD LOEUF=0.248, and Clean >=2mm Lead #1 chr19:3278299-3278318(+)."),
]

STAGE_LABELS = {
    "Phase1_Setup": "Data Staging & Registry Init",
    "Batch_1_Cryptic_Splicing_And_APA": "Cohort Re-Analysis · Splicing & Polyadenylation",
    "Batch_2_Vesicle_Trafficking_And_Iron_Unbundling": "Cohort Re-Analysis · Trafficking, SNARE & Iron",
    "Batch_3_Neuroimmune_Glial_And_Isoform": "Cohort Re-Analysis · Neuroimmune, Glial & Vascular",
    "Batch_4_Repurposing_Screen_PK_And_Safety": "Cohort Re-Analysis · iPSC Screen, Unbound PK & Safety",
    "Batch_5_Clinical_Futility_PK_And_Excitability": "Cohort Re-Analysis · Clinical Trials & Excitability",
    "Batch_6_BA9_Named_Genes_And_Screen_Audit": "Cohort Re-Analysis · Mendelian Chaperone & Subgroups",
    "Phase2_Track1_Multiplex_Splice": "3D & PK-PD · Multiplex Splice & Kv7.2",
    "Phase2_Track2_SARM1_YKT6_Allostery": "3D & PK-PD · SARM1/YKT6 & MWC Allostery",
    "Phase2_Track3_Subtype_Precision_Translation": "3D & PK-PD · CSF Subtypes & Pulsed PK-PD",
    "Phase2_Track4_CellType_Isoform_Resolution": "3D & PK-PD · Vascular & Subunit Isoforms",
    "Phase3B_DeNovo_Discovery": "Multi-Omic Triage · Transcriptome, CSF & Screen",
    "Phase3A_Execution_Safety": "Hybridization Safety · 254,070-tx GRCh38 Scan",
    "Phase4_Final_Synthesis": "Portfolio Synthesis · 52-Hypothesis Integration",
}


def _display_run_id(rid: str) -> str:
    return "RUN-INIT-000" if rid == "CAR-RUN-000" else rid


def _clean_run_out(out: str, rid: str = "") -> str:
    if rid == "CAR-RUN-000":
        return "registries/*.csv;schemas/dataset_files_lock.json"
    s = out.replace("reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md;reports/CARBON_ALS_INTERACTIVE_EXPLORER.html;reports/monographs;reports/github_pages", "docs/index.html;docs/monographs")
    return re.sub(r"reports/CARBON_ALS_[A-Za-z0-9_.]*", "docs/index.html", s)


def clean_rep_text(txt: str) -> str:
    s = txt.replace("CarbonALS", "ExploreALS").replace("carbonals", "ExploreALS")
    s = re.sub(r"\bExploreALS_R\d+\b|\bExploreALS_G1A06\b", "prior literature catalog", s)
    s = re.sub(r"\bExploreALS\b(?=\s+(?:21-candidate|datasets|evidence|bibliographic|adversarial|cross-track|Phase 10A|40 items|items))", "prior literature catalog", s)
    s = re.sub(r"\b(?:baseline|prior)\s+intake\b", "published catalog", s, flags=re.I)
    s = re.sub(r"\bv0\b", "prior catalog", s, flags=re.I)
    s = s.replace("Phase-4 ChEMBL", "FDA-approved (ChEMBL max_phase=4)").replace("Phase-4 ", "FDA-approved (ChEMBL max_phase=4) ")
    s = s.replace("excluding all 33 curated clinical/genetic programs + 18 subunit/comparator genes", "evaluating non-Mendelian/non-trial targets beyond established clinical/genetic loci and 18 complex subunits")
    s = s.replace("Adjudicated 19 atomic de novo candidates", "Adjudicated 19 multi-omic transcriptome, CSF, and iPSC-screen candidates")
    s = s.replace("across all 17 surviving programs", "across active therapeutic programs")
    s = s.replace("TIER_2_FOCUSED_GATE_FIRST", "Tier 2 · Validation Gate")
    s = s.replace("TIER_3_EXPLORATORY_DISCOVERY", "Tier 3 · Exploratory Discovery")
    s = s.replace("RECLASSIFY_BENCHMARK_OR_BIOMARKER", "Benchmark / Biomarker")
    s = s.replace("FALSIFIED_CLINICAL", "Falsified · Clinical")
    s = s.replace("ARTIFACT_CONFOUNDED", "Assay-Confounded")
    s = s.replace("KEEP_CORE", "Keep · Core")
    s = s.replace("GAPMER_RNASE_H", "3'-extension target")
    s = s.replace("sub18_core_nonconstr", "18nt-subcore(non-constrained)")
    s = re.sub(r"\bDS045\b|\bD045\b", "Trautwig 2025 CSF", s)
    s = re.sub(r"\bD003\b", "Pineda 2024 snRNA-seq", s)
    s = re.sub(r"Phase\s*3A(\s*v2)?", "GRCh38 Hybridization Safety", s, flags=re.I)
    s = re.sub(r"Wave\s+2", "multi-cohort verification", s, flags=re.I)
    s = re.sub(r"(?:5D\s*(?:Liability)?|gene-liability|liability)\s*=\s*[0-9.]+/100(?:\s*\([^)]*\))?[;,\s]*", "", s, flags=re.I)
    s = re.sub(r"[;,\s]*\([^)]*[0-9.]+/100[^)]*\)", "", s)
    s = s.replace("pm1_50", "50bp-SS 1mm").replace("pm2_25", "25bp-SS 2mm").replace("sp0;", "spliced 0mm;")
    return sanitize_public_prose(translate_legacy_tokens_in_prose(re.sub(r"\s{2,}", " ", s).strip()))


def _map_cand_list(raw_cands: str) -> str:
    out: list[str] = []
    for tok in raw_cands.split(";"):
        t = tok.strip()
        if not t:
            continue
        try:
            acc = legacy_to_accession(t)
        except ValueError:
            acc = translate_legacy_tokens_in_prose(t)
        if acc not in out:
            out.append(acc)
    return ";".join(out)


def build_replication_payloads(
    run_rows: list[dict[str, str]],
    ds_rows: list[dict[str, str]],
    stat_rows: list[dict[str, str]],
    ovl_rows: list[dict[str, str]],
    ev_all_rows: list[dict[str, str]],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    run_cands: dict[str, list[str]] = {}
    ev_cid_map: dict[str, str] = {}
    for e in ev_all_rows:
        lcid = e["carbon_id"].strip()
        cid = legacy_to_accession(lcid)
        rid = e["analysis_run_id"].strip()
        ev_cid_map[e["evidence_id"].strip()] = cid
        if cid not in run_cands.setdefault(rid, []):
            run_cands[rid].append(cid)

    js_runs: list[dict] = [
        {"id": fid, "grp": grp, "script": sc, "out": "Terminal verification table (rtol=1e-4)", "ds": ds, "cands": cands, "sum": clean_rep_text(sm), "flag": True}
        for fid, grp, sc, ds, cands, sm in FLAGSHIP_DEFS
    ]
    for r in run_rows:
        rid = r["analysis_run_id"]
        js_runs.append({
            "id": _display_run_id(rid),
            "grp": STAGE_LABELS.get(r["phase_batch"], r["phase_batch"].replace("_", " ")),
            "script": ("scripts/verify_explore_als.py;scripts/fetch_open_datasets.py" if rid == "CAR-RUN-000" else r["script_relpath"]),
            "out": _clean_run_out(r["output_artifacts"], rid),
            "ds": ";".join(d for d in r["datasets_used"].split(";") if d and not d.startswith("DS_BASE")),
            "cands": ";".join(run_cands.get(rid, [])),
            "sum": clean_rep_text(r["summary"]),
            "flag": False,
        })

    js_ds = [
        {
            "id": d["dataset_id"], "dom": d["domain"].replace("_", " "), "rel": d["local_relpath"],
            "acc": clean_rep_text(d["accession_or_doi"]), "lic": clean_rep_text(d["license_or_access"]),
            "mb": f"{int(d['size_bytes'])/1e6:.2f} MB" if int(d["size_bytes"]) >= 100_000 else f"{int(d['size_bytes'])/1e3:.1f} KB",
            "sha": d["sha256"], "cands": _map_cand_list(d["relevant_candidates"]), "desc": clean_rep_text(d["description"]),
            "tier": d["redistribution_tier"], "url": d["canonical_fetch_url_or_instructions"],
        }
        for d in ds_rows
    ]
    js_formulas = [
        {
            "eid": s["evidence_id"],
            "cid": ("" if s["evidence_id"] == "EV-P3A-004" else ev_cid_map.get(s["evidence_id"], "")),
            "run": _display_run_id(s["analysis_run_id"]),
            "cls": s["inference_class"], "unit": s["statistical_unit"], "nu": s["n_statistical_units"],
            "ndon": s["n_unique_donors_or_participants"],
            "con": (
                "Cross-portfolio separation of clinical development stage from biological actionability and validation steps"
                if s["evidence_id"] == "EV-P3A-004"
                else clean_rep_text(s["exact_contrast"])
            ),
            "mod": (
                "Deterministic multi-criteria portfolio verification across 52 evaluated hypotheses"
                if s["evidence_id"] == "EV-P3A-004"
                else clean_rep_text(s["model_formula_or_test"])
            ),
            "est": ("52/52 verified" if s["evidence_id"] == "EV-P3A-004" else clean_rep_text(s["effect_estimate"])),
            "ci": clean_rep_text(s["se_or_ci95"]), "up": s["unadjusted_or_primary_nominal_p"],
            "cp": s["covariate_adjusted_nominal_p"], "mp": s["multiplicity_adjusted_p"],
            "mfam": s["multiple_testing_family"], "excl": clean_rep_text(s["missingness_or_exclusion_rule"]),
            "ovl": s["overlap_group_id"], "anc": s["anchor_type"], "arel": s["anchor_relpath"], "sha": s["sha64"],
        }
        for s in stat_rows
    ]
    js_ovl = [
        {
            "id": o["overlap_group_id"], "name": o["cluster_name"], "ds": o["datasets_involved"],
            "rule": clean_rep_text(o["donor_accounting_and_anti_pseudoreplication_rule"]),
            "formula": clean_rep_text(o["canonical_model_formula"]),
        }
        for o in ovl_rows
    ]
    return js_runs, js_ds, js_formulas, js_ovl
