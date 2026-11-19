"""Build sanitized JSON payloads (DATA_RUNS [8 Flagship + 50 Runs], DATA_DATASETS [40], DATA_FORMULAS [194], DATA_OVERLAP [8]) for Tab 4."""
from __future__ import annotations

import re

FLAGSHIP_DEFS = [
    ("FLAGSHIP-S06", "Monograph #1 · S06 (SARM1)", "pipelines/flagship/reproduce_S06_sarm1.py", "DS_PDB_9TZY;DS_PDB_7DJT;DS_PDB_7ANW", "S06;C002", "Verifies PDB 9TZY 3-chain BEXi filament gluing, gnomAD LOEUF=1.1432, Leahey ~2.8x empirical BEXi washout spike vs theoretical 8-mer ceiling and monotonic T-Lock, and default Krus 2022 Bliss additivity."),
    ("FLAGSHIP-S07", "Monograph #2 · S07 (Aldesleukin)", "pipelines/flagship/reproduce_S07_aldesleukin.py", "DS045_TRAUT", "S07", "Verifies MIROCALS BioVendor ELISA 750-3,700 pg/mL stratum, Trautwig MS NEFL vs NEFH r=0.278 (n=51 Emory TMT nested in n=77 DIA), and proportional-hazards Schoenfeld Ph3 sizing (247 events at HR=0.70)."),
    ("FLAGSHIP-C001", "Monograph #3 · C001 (UNC13A)", "pipelines/flagship/reproduce_C001_unc13a.py", "DS_CRYPTIC;DS029_SPILL;DS_GENCODE_V46_TX", "C001", "Verifies Brown UNC13A cryptic junction dPSI, Spillman synaptosome Munc13-1 loss, rs12973192/rs12608932 genotype-stratified rules, and promoted Clean >=2mm Lead #2 chr19:17642537-17642554(-)."),
    ("FLAGSHIP-C006", "Monograph #4 · C006 (KCNQ2)", "pipelines/flagship/reproduce_C006_kcnq2.py", "DS_CRYPTIC;DS_PDB_7CR2;DS_GENCODE_V46_TX", "C006;C003;C005", "Verifies Exon-5 126-bp (42-aa) in-frame skipping, PDB 7CR2 Trp236 2.97A retigabine H-bond, post-assembly ER co-trapping across 4:0 vs 2:2 Kv7.2:Kv7.3 channels, and Lead #3 off-target hygiene."),
    ("FLAGSHIP-C002", "Monograph #5 · C002 (STMN2)", "pipelines/flagship/reproduce_C002_stmn2.py", "DS_CRYPTIC;DS029_SPILL;DS_GENCODE_V46_TX", "C002;S06", "Verifies STMN2 Exon-2a cryptic junction dPSI=+0.482, Spillman C9-FTD homogenate -0.4825 log2FC (-28.4%, p=0.014, FDR=0.113), and promoted Clean >=2mm Lead #2 chr8:79616829-79616846(+)."),
    ("FLAGSHIP-C007", "Monograph #6 · C007 (IL1RL1)", "pipelines/flagship/reproduce_C007_il1rl1.py", "DS_EDIN_PB;DS031_ZHANG;DS_PDB_4KC3", "C007", "Verifies Edinburgh donor-collapsed endothelial +3.106 log2CPM (p=0.00641, n=7 Ctrl), Zhang 55-um Visium +3.76 (within-donor spot pseudoreplicated across N=14 donors), GENCODE v46 sST2 intron-8 polyA exon, and PDB 4KC3."),
    ("FLAGSHIP-DN01", "Monograph #7 · DN-01 (ATG4B)", "pipelines/flagship/reproduce_DN01_atg4b.py", "DS029_SPILL;DS001_COUNTS;DS_PDB_2Z0D", "DN-01", "Verifies Spillman C9-FTD homogenate ATG4B -0.4905 log2FC (p=0.0227), NYGC cervical RIN+GC OLS beta=-0.1642, PDB 2Z0D 27 LC3B contacts, and promoted Lead #2 chr2:241668970-241668987(+)."),
    ("FLAGSHIP-DN04", "Monograph #8 · DN-04 (CELF5)", "pipelines/flagship/reproduce_DN04_celf5.py", "DS001_COUNTS;DS005_BYE;DS_GENCODE_V46_TX", "DN-04", "Verifies NYGC cervical RIN+GC beta=-0.4020, #1 neuronal-mass-adjusted tSTMN2 coupling (1.90% cervical / 0.14% lumbar tail), gnomAD LOEUF=0.248, and Clean >=2mm Lead #1 chr19:3278299-3278318(+)."),
]

STAGE_LABELS = {
    "Phase1_Setup": "Stage 1 · Open-Data Staging & Registry Init",
    "Batch_1_Cryptic_Splicing_And_APA": "Batch 1 · Cryptic Splicing & APA",
    "Batch_2_Vesicle_Trafficking_And_Iron_Unbundling": "Batch 2 · Trafficking, SNARE & Iron Dissection",
    "Batch_3_Neuroimmune_Glial_And_Isoform": "Batch 3 · Neuroimmune, Glial & Isoform",
    "Batch_4_Repurposing_Screen_PK_And_Safety": "Batch 4 · Screen, Unbound PK & Safety",
    "Batch_5_Clinical_Futility_PK_And_Excitability": "Batch 5 · Clinical Futility & Excitability",
    "Batch_6_BA9_Named_Genes_And_Screen_Audit": "Batch 6 · Mendelian Chaperone & Screen Survivors",
    "Phase2_Track1_Multiplex_Splice": "Stage 2 · Multiplex Cis-Splice & Kv7.2 3D",
    "Phase2_Track2_SARM1_YKT6_Allostery": "Stage 2 · SARM1/YKT6 3D & MWC Allostery",
    "Phase2_Track3_Subtype_Precision_Translation": "Stage 2 · Subtype CSF & Pulsed PK-PD",
    "Phase2_Track4_CellType_Isoform_Resolution": "Stage 2 · Cell-Type & Isoform Resolution",
    "Phase3B_DeNovo_Discovery": "Stage 3B · Genome-Wide De Novo Discovery",
    "Phase3A_Execution_Safety": "Stage 3A · 254,070-tx Off-Target & Readiness",
    "Phase4_Final_Synthesis": "Stage 4 · Unified 52-Hypothesis Synthesis",
}


def clean_rep_text(txt: str) -> str:
    s = txt.replace("CarbonALS", "ExploreALS").replace("carbonals", "ExploreALS")
    s = re.sub(r"\bExploreALS_R\d+\b|\bExploreALS_G1A06\b", "Frozen Baseline", s)
    s = re.sub(r"\bExploreALS\b(?=\s+(?:21-candidate|datasets|evidence|bibliographic|adversarial|cross-track|Phase 10A|40 items|items))", "Upstream Baseline", s)
    s = re.sub(r"\b(?:baseline|prior)\s+intake\b", "baseline annotation", s, flags=re.I)
    s = re.sub(r"\bv0\b", "baseline", s, flags=re.I)
    s = s.replace("sub18_core_nonconstr", "18nt-subcore(non-constrained)")
    s = re.sub(r"\bDS045\b|\bD045\b", "DS045_TRAUT", s)
    s = re.sub(r"\bD003\b", "DS003_PB", s)
    s = re.sub(r"Phase\s*3A(\s*v2)?", "6-Tier Cis-Safety", s, flags=re.I)
    s = re.sub(r"Wave\s+2", "Round 2", s, flags=re.I)
    s = re.sub(r"(?:5D\s*(?:Liability)?|gene-liability|liability)\s*=\s*[0-9.]+/100(?:\s*\([^)]*\))?[;,\s]*", "", s, flags=re.I)
    s = re.sub(r"[;,\s]*\([^)]*[0-9.]+/100[^)]*\)", "", s)
    s = s.replace("pm1_50", "50bp-SS 1mm").replace("pm2_25", "25bp-SS 2mm").replace("sp0;", "spliced 0mm;")
    return re.sub(r"\s{2,}", " ", s).strip()


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
        cid = e["carbon_id"].strip()
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
            "id": rid,
            "grp": STAGE_LABELS.get(r["phase_batch"], r["phase_batch"].replace("_", " ")),
            "script": r["script_relpath"],
            "out": r["output_artifacts"],
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
            "sha": d["sha256"], "cands": d["relevant_candidates"], "desc": clean_rep_text(d["description"]),
            "tier": d["redistribution_tier"], "url": d["canonical_fetch_url_or_instructions"],
        }
        for d in ds_rows
    ]
    js_formulas = [
        {
            "eid": s["evidence_id"], "cid": ev_cid_map.get(s["evidence_id"], ""), "run": s["analysis_run_id"],
            "cls": s["inference_class"], "unit": s["statistical_unit"], "nu": s["n_statistical_units"],
            "ndon": s["n_unique_donors_or_participants"], "con": clean_rep_text(s["exact_contrast"]),
            "mod": clean_rep_text(s["model_formula_or_test"]), "est": clean_rep_text(s["effect_estimate"]),
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
