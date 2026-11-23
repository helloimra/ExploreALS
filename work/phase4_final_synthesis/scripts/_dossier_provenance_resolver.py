"""FAIR + W3C PROV provenance & 4-level Evidence Design Tier resolver for all 59 ExploreALS candidates (216 evidence rows)."""
from __future__ import annotations

import re

SUBKEY_OVERRIDES: list[tuple[str, str, list[str]]] = [
    ("DS_CRYPTIC:Brown2022", "Brown et al. 2022 (Nature)", ["PMID:35197628", "DOI:10.1038/s41586-022-04436-3"]),
    ("DS_CRYPTIC:Ma2022", "Ma et al. 2022 (Nature)", ["PMID:35197626"]),
    ("DS_CRYPTIC:Klim2019", "Klim et al. 2019 (Cell Stem Cell)", ["PMID:30643292"]),
    ("DS_CRYPTIC:Melamed2019", "Melamed et al. 2019 (Nat Neurosci)", ["PMID:30643298"]),
    ("DS_CONS2026:Tsitkov", "Tsitkov et al. 2026 (Answer ALS)", ["PMC12919128"]),
    ("DS_CONS2026:Grozdanov", "Grozdanov/Lee et al. 2026 (M1 Multiome)", ["PMC12982666"]),
    ("DS_CONS2026:Lee", "Grozdanov/Lee et al. 2026 (M1 Multiome)", ["PMC12982666"]),
    ("DS_CONS2026:Zhang", "Zhang et al. 2026 (Spatial)", ["PMC13337491"]),
]

DS_LABELS: dict[str, tuple[str, list[str]]] = {
    "DS001_COUNTS": ("NYGC ALS Consortium", ["GSE153960", "PMID:36482247"]),
    "DS001_META": ("NYGC ALS Consortium", ["GSE153960"]),
    "DS001_FEAT": ("NYGC ALS Consortium", ["GSE153960"]),
    "DS001_FLAGSHIP": ("NYGC ALS Consortium", ["PMID:36482247", "GSE153960"]),
    "DS001_ONEILL": ("O'Neill et al. 2025 Subtypes", ["PMID:40067829", "DOI:10.1016/j.celrep.2025.115402"]),
    "DS001_TAM": ("Tam et al. 2019 Subtypes", ["PMID:31665631", "GSE124439"]),
    "DS003_PB": ("Pineda et al. 2024 snRNA-seq", ["PMID:38521060", "PRJNA1073234"]),
    "DS003_SUPP": ("Pineda et al. 2024 snRNA-seq", ["PMID:38521060"]),
    "DS_EDIN_PB": ("Edinburgh Cortex snRNA-seq", ["PMID:42551425", "GSE290359"]),
    "DS014_PRUD": ("Prudencio et al. 2015", ["GSE67196"]),
    "DS_CONS2026": ("2026 ALS Multiome Consortia", ["PMC12919128", "PMC12982666"]),
    "DS031_ZHANG": ("Zhang et al. 2026 Spatial", ["PMID:42135512", "GSE288365"]),
    "DS_CRYPTIC": ("Brown & Ma 2022 Cryptic Atlas", ["PMID:35197628", "PMID:35197626"]),
    "DS_ZENG_APA": ("Zeng et al. 2025 TDP-43 APA", ["PMID:41120750", "DOI:10.1038/s41593-025-02049-3"]),
    "DS_BRYCE_APA": ("Bryce-Smith et al. 2025 APA/CE", ["PMID:41120751"]),
    "DS026_FUJITA": ("Fujita et al. ROSMAP eQTL", ["syn52335732"]),
    "DS045_TRAUT": ("Trautwig et al. 2025 CSF", ["PMC12082929", "PMID:40375307"]),
    "DS045_XML": ("Trautwig et al. 2025 CSF", ["PMC12082929"]),
    "DS046_OH_XML": ("Oh et al. 2023 CSF PRM", ["PMC10215566", "PMID:37238921"]),
    "DS029_SPILL": ("Spillman et al. 2026 DIA", ["PMID:42789089", "PXD083082", "DOI:10.1007/s00401-026-03084-5"]),
    "DS005_BYE": ("Bye et al. 2025 iPSC-MN Screen", ["PMID:41286450", "DOI:10.1038/s41593-025-02118-7"]),
    "DS_ROPALS": ("Morimoto et al. 2023 ROPALS", ["PMID:37267913"]),
    "DS_AFDB": ("AlphaFold Protein Structure DB v6", []),
    "DS_PDB": ("RCSB PDB Experimental Structures", []),
    "DS_GENCODE_V46_TX": ("GENCODE v46 Reference", []),
    "DS_GENCODE_V46_GTF": ("GENCODE v46 Reference", []),
    "DS_GENCODE_V46_COMP_GTF": ("GENCODE v46 Reference", []),
    "DS_GNOMAD_V41_CONSTRAINT": ("gnomAD v4.1 Constraint", []),
}

SPLIT_RE = re.compile(r"[;|]|\+(?=(?:OpenTargets|AlphaGenome|ChEMBL|gnomAD|DS_|OpenFDA|CT\.gov))")
INLINE_ACC_RE = re.compile(r"(?:PMID:\d+|PMC\d+|NCT\d{8}|NDA\d{5,6}|UMIN\d{9}|ISRCTN\d{8}|ACTRN\d{14}|jRCT[A-Za-z0-9]+|CHEMBL\d+|CID:\d+|ENS[GT]\d{11}(?:\.\d+)?|GSE\d+|PXD\d+|PRJNA\d+|syn\d+|AF-[A-Z0-9]+-F1|10\.\d{4,9}/[^\s,;)\]]+)")
PDB_TOK_RE = re.compile(r"(?:pdb_0000([0-9a-z]{4})\.cif|DS_PDB[_:]([0-9A-Za-z]{4}))", re.IGNORECASE)
VS_COUNTS_RE = re.compile(r"\b\d+\s+[A-Za-z0-9\-/+ ]{1,24}\s+vs\.?\s+\d+", re.IGNORECASE)
SAMPLE_CTX_RE = re.compile(r"\[Sample context:\s*([^\]]+)\]", re.IGNORECASE)
PAREN_VS_RE = re.compile(r"\((\d+\s+[^()]{1,40}?\s+vs\.?\s+\d+\s+[^()]{1,40}?)\)")

SUBNODE_GENE_MAP: dict[str, str] = {
    "C014-N1": "CHMP7", "C014-N2": "CHMP2B",
    "C015-N1": "SCFD1", "C015-N2": "G2E3",
    "C023-N1": "YKT6", "C023-N2": "SEC22B", "C023-N3": "STX5",
    "C023-N4": "GOSR1", "C023-N5": "NSF", "C023-N6": "GDI2",
    "C017-N1": "CHIT1", "C017-N2": "GPNMB", "C017-N3": "CHI3L1", "C017-N4": "CHI3L2",
    "C018-N1": "C1QA", "C018-N2": "C1QB", "C018-N3": "C1QC", "C018-N4": "C4B",
}

MODEL_EIDS = {
    "EV-B1-005", "EV-B1-010", "EV-B1-015", "EV-B2-002", "EV-B3-006",
    "EV-P2-T1-001", "EV-P2-T1-002", "EV-P2-T1-003", "EV-P2-T2-002", "EV-P2-T2-004",
    "EV-P3A-001", "EV-P3A-002", "EV-P3A-004", "EV-P3B-002", "EV-P3B-004",
}
LEVEL1_GENETICS_EIDS = {"EV-B2-001", "EV-B2-004", "EV-B2-006", "EV-B3-008", "EV-B6-012", "EV-B6-043"}
LEVEL1_SOC_EIDS = {"EV-P4-009", "EV-B6-050", "EV-B5-006", "EV-B5-014", "EV-B5-015", "EV-B5-024", "EV-B3-020", "EV-P3B-022", "EV-P3B-030", "EV-P3B-031", "EV-P3B-032"}


def classify_basis_and_tier(row: dict[str, str]) -> tuple[str, str, str]:
    eid = row.get("evidence_id", "").strip()
    st = row.get("source_type", "").lower()
    loc = row.get("source_id_or_locator", "").lower()
    coh = row.get("cohort_and_stratum", "").lower()
    wt = row.get("epistemic_weight", "").strip()
    n_raw = row.get("sample_size_n", "").strip()
    n_int = int(n_raw) if n_raw.isdigit() else None

    if eid == "EV-P2-T4-004":
        basis = "Human snRNA / Spatial Recompute"
    elif "mwc" in st or "ode" in st or "model" in st or "mass_action" in st or "simulation" in st:
        basis = "Biophysical / PK-PD Model"
    elif "rct" in st or "phase3" in st or "phase2_3" in st:
        basis = "Human Phase 2b/3 RCT"
    elif "phase2" in st or "clinical_trial" in st or "csf_pk_pd" in st or "landscape" in st:
        basis = "Human Clinical Trial / PK-PD"
    elif "structural" in st or "3d" in st or "cif" in st:
        basis = "3D Cryo-EM / Crystal Audit"
    elif "qtl" in st or "rare_variant" in st or "genetics" in st:
        basis = "Human Genetics / QTL"
    elif "alphagenome" in st or "bulge_subcore" in st or "multiplex_design" in st or "offtarget" in st or "triage" in st:
        basis = "GRCh38 Cis / AlphaGenome Scan"
    elif "chembl" in st or "openfda" in st or "pk" in st or "chemical" in st or "toxicity" in st or "safety" in st:
        basis = "Pharmacology / Safety Audit"
    elif "screen" in st:
        basis = "Patient iPSC-MN Drug Screen"
    elif "csf" in st or "proteom" in st or "pellet" in st or "fraction" in st:
        basis = "Human Proteomics Recompute"
    elif "snrna" in st or "single_nucleus" in st or "spatial" in st:
        basis = "Human snRNA / Spatial Recompute"
    elif "splicing" in st or "apa" in st or "riboseq" in st or "rnaseq" in st or "transcriptom" in st or "subtype" in st:
        basis = "Human RNA / Splicing Recompute"
    elif "api" in st:
        basis = "Multi-Database API Audit"
    else:
        basis = "Primary Cohort Recompute"

    # 1. Model / Heuristic Prior
    if (
        eid in MODEL_EIDS
        or any(k in st for k in ("mwc", "ode", "simulation", "mass_action", "alphagenome", "multiplex_design", "offtarget", "bulge_subcore", "triage"))
    ):
        design_tier = "Model / Heuristic Prior"
    # 2. Level 1: Reported Human ALS RCTs (n>=20, excluding unreported EV-B6-035) or Causal Human ALS Genetics / SOC
    elif eid != "EV-B6-035" and (
        eid in LEVEL1_GENETICS_EIDS
        or eid in LEVEL1_SOC_EIDS
        or (("rct" in st or "phase3" in st or "phase2_3" in st or "rct" in coh) and (n_int is None or n_int >= 20) and "open-label" not in coh and "single-group" not in coh)
    ):
        design_tier = "Level 1 · Human RCT / Genetics"
    # 3. Level 3: In Vitro / Structural Assays OR Small-N Human Studies (N < 15)
    elif (
        "ds005_bye" in loc
        or "i3neuron" in coh
        or ("ipsc" in coh and "aals" not in loc and "594" not in coh)
        or ("ds_pdb" in loc and "ds045_traut" not in loc)
        or "structural" in st
        or ("depmap" in loc and "omim" not in coh and "gnomad" not in loc and "ds045_traut" not in loc)
        or ("kinobead" in coh or eid in {"EV-B2-003", "EV-B4-019"})
        or (n_int is not None and n_int < 15 and "landscape" not in st)
    ):
        design_tier = "Level 3 · In Vitro or Small-N"
    # 4. Level 2: Human Cohorts (N >= 15), Clinical PK/Safety Labels, & Population Reference
    else:
        design_tier = "Level 2 · Human Cohort / PK-PD"

    role_map = {
        "ESTABLISHED_SOC": "SOC Benchmark",
        "DECISIVE_FALSIFYING": "Falsifying",
        "HIGH_FALSIFICATION": "Falsifying",
        "HIGH_MECHANISTIC_FALSIFICATION": "Falsifying",
        "HIGH_PK_FALSIFICATION": "PK Falsifying",
        "HIGH_SAFETY_FALSIFICATION": "Safety Falsifying",
        "MODERATE_REFUTATION": "Refutation",
        "HIGH_BENCHMARK": "Benchmark",
        "HIGH_SAFETY_BOUNDARY": "Safety Gate",
        "HIGH_SAFETY_EXCLUSION": "Safety Gate",
        "HIGH_GATE_CHECK": "Gate Check",
        "HIGH_STRUCTURAL": "3D Structure",
    }
    role = role_map.get(wt, "Unreported RCT" if eid == "EV-B6-035" else "")
    return basis, design_tier, role


def _classify_nonfile_prov(row: dict[str, str]) -> str:
    loc = row.get("source_id_or_locator", "")
    st = row.get("source_type", "").lower()
    low = loc.lower()
    if loc.startswith("RUN-") or any(k in low or k in st for k in ("mwc", "ode", "simulation", "mass_action", "multiplex_design", "offtarget", "bulge_subcore", "triage")):
        return "MODEL:Biophysical_Prior"
    if any(k in low for k in ("nct", "umin", "isrctn", "ct.gov", "clinicaltrials")):
        return "EXT_REG:ClinicalTrials.gov"
    if any(k in low for k in ("openfda", "nda", "chembl", "cid:")):
        return "EXT_REG:OpenFDA_ChEMBL"
    if any(k in low for k in ("gnomad", "alphagenome", "opentargets", "depmap", "clinvar", "gtex")):
        return "EXT_API:Genomics_Ref"
    if any(k in low for k in ("pmid:", "pmc", "europepmc", "doi:")):
        return "EXT_LIT:PubMed_PMC"
    return "EXT_API:Primary_Audit"


def _clean_v0_text(txt: str) -> str:
    txt = re.sub(r"Audit of (?:ExploreALS|baseline intake) C021 identifiers", "Chemical registry verification of Sephin1 / icerguastat", txt, flags=re.IGNORECASE)
    txt = re.sub(r"(?:ExploreALS|Baseline intake) CHEMBL3545058=", "Misattributed CHEMBL3545058=", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\b(?:baseline|prior)\s+intake\b", "baseline annotation", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\bintake\b", "baseline", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\bnon-ExploreALS\b", "de novo", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\bExploreALS\b", "baseline annotation", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\bCarbonALS\b", "ExploreALS", txt, flags=re.IGNORECASE)
    txt = txt.replace("5D Liability=100.0/100 (STX5-CDG lethal)", "STX5-CDG lethal")
    txt = re.sub(r"[;,\s]*(?:[A-Z0-9/]+\s+)?(?:5D\s+)?liability=[0-9./]+/100(?:\s*\([A-Z]+\))?", "", txt, flags=re.IGNORECASE)
    txt = re.sub(r"[;,\s]*5D=[0-9.]+/100", "", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\bDS045\b|\bD045\b", "Trautwig 2025 CSF (PMC12082929)", txt)
    txt = re.sub(r"\bD003\b", "Pineda 2024 (PMID:38521060)", txt)
    for k, v in (
        ("PASS_CLEAN_GE2MM", "Clean >=2mm"), ("CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED", "Caution (non-constrained 1mm/wobble or 25bp-SS 2mm)"),
        ("WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL", "Warn (CNS hit)"), ("FAIL_EXACT_0MM_OFFTARGET", "Fail (exact 0mm)"),
        ("TIER_3_EXPLORATORY_DISCOVERY", "Tier 3 Exploratory Discovery"), ("TIER_3_HIGH_RISK_WATCHLIST", "Tier 3 Exploratory Discovery"),
        ("Bryce-Smith 2025 ST6", "Bryce-Smith 2025"), ("Bryce-Smith ST6", "Bryce-Smith 2025"), ("Bryce-Smith ST7", "Bryce-Smith 2025"),
        ("Phase 3A v2", "GENCODE v46 6-tier"), ("Phase 3A", "GENCODE v46"),
        ("DIA_sALS_vs_Ctrl_diff=", "sALS vs Ctrl Δlog2="), ("DESeq2_inter_log2FC=", "Interaction log2FC="),
        ("NYGC_Cerv_M3_C1QB_beta=", "Cervical M3 C1QB β="), ("NYGC_Cerv_M3_beta=", "Cervical M3 β="),
        ("OLS_beta=", "OLS β="), ("adj_beta=", "adj β="), ("avg_log2FC=", "log2FC="),
        ("diff_log2CPM=", "Δlog2CPM="), ("diff_log2cpm=", "Δlog2CPM="), ("diff_log2=", "Δlog2="),
        ("gnomAD_AF=", "gnomAD AF="), ("OpenTargets_PD_L2G=", "Open Targets PD L2G="),
        ("ELK1_unique", "ELK1-unique"), ("ELK4_unique", "ELK4-unique"),
        ("max_AVI=", "max AVI="), ("wob_only=", "wobble-only="), ("sp0=", "spliced 0mm="), ("sp1=", "spliced 1mm="),
        ("pm0=", "pre-mRNA 0mm="), ("pm1_50=", "50bp-SS 1mm="), ("pm2_25=", "25bp-SS 2mm="),
        ("ese=0", "0 disrupted ESEs"), ("sub18_core_nonconstr", "18nt-subcore(non-constrained)"), ("bulge_1nt", "1nt-bulge"),
    ):
        txt = txt.replace(k, v)
    return re.sub(r"\s{2,}", " ", txt).strip()


def resolve_evidence_row(
    row: dict[str, str],
    ds_map: dict[str, dict[str, str]],
    stat_map: dict[str, dict[str, str]] | None = None,
) -> dict[str, str]:
    loc = row.get("source_id_or_locator", "")
    notes = row.get("notes", "")
    tokens = [t.strip() for t in SPLIT_RE.split(loc) if t.strip() and "exploreals" not in t.lower()]
    src_names: list[str] = []
    accs: list[str] = []
    sha12 = ""
    primary_ds = ""

    def _add_acc(a: str) -> None:
        a = a.strip().rstrip(".,;)")
        if not a or "exploreals" in a.lower():
            return
        if a.startswith("RCSB_PDB:"):
            for code in a.split(":", 1)[1].split(";"):
                if code.strip():
                    _add_acc(f"PDB {code.strip().upper()}")
            return
        if re.match(r"^10\.\d{4,9}/", a):
            a = f"DOI:{a}"
        if a not in accs:
            accs.append(a)

    for m_pdb in PDB_TOK_RE.finditer(loc):
        pcode = (m_pdb.group(1) or m_pdb.group(2) or "").upper()
        if pcode:
            _add_acc(f"PDB {pcode}")
            pdb_ds = f"DS_PDB_{pcode}"
            if not sha12 and pdb_ds in ds_map:
                sha12 = ds_map[pdb_ds]["sha256"][:12]
                primary_ds = pdb_ds
            elif not sha12 and "DS_PDB" in ds_map:
                sha12 = ds_map["DS_PDB"]["sha256"][:12]
                primary_ds = "DS_PDB"

    for tok in tokens:
        matched_sub = False
        for pref, lbl, ov_accs in SUBKEY_OVERRIDES:
            if tok.startswith(pref):
                if lbl not in src_names:
                    src_names.append(lbl)
                for oa in ov_accs:
                    _add_acc(oa)
                base_ds = pref.split(":", 1)[0]
                if not sha12 and base_ds in ds_map and not base_ds.startswith("DS_BASE"):
                    sha12 = ds_map[base_ds]["sha256"][:12]
                    primary_ds = base_ds
                matched_sub = True
                break
        if matched_sub:
            continue

        ds_key = re.split(r"[\s:(]", tok, maxsplit=1)[0]
        if ds_key in DS_LABELS:
            lbl, ds_accs = DS_LABELS[ds_key]
            if lbl not in src_names:
                src_names.append(lbl)
            for da in ds_accs:
                _add_acc(da)
            if not sha12 and ds_key in ds_map and not ds_key.startswith("DS_BASE"):
                sha12 = ds_map[ds_key]["sha256"][:12]
                primary_ds = ds_key
        elif ds_key in ds_map and not ds_key.startswith("DS_BASE") and ds_key != "DS_BA9_BUNDLE":
            drow = ds_map[ds_key]
            if not sha12:
                sha12 = drow["sha256"][:12]
                primary_ds = ds_key
            for raw_a in drow["accession_or_doi"].split(";"):
                _add_acc(raw_a)
            if ds_key.startswith("DS_PDB_"):
                pcode = ds_key.replace("DS_PDB_", "")
                lbl = f"RCSB Cryo-EM / X-Ray (PDB {pcode})"
                if lbl not in src_names:
                    src_names.append(lbl)

        for m in INLINE_ACC_RE.finditer(tok):
            _add_acc(m.group(0))
        if not src_names:
            low = tok.lower()
            if "alphagenome" in low:
                src_names.append("AlphaGenome Atlas")
            elif "gnomad" in low:
                src_names.append("gnomAD v4")
            elif "opentargets" in low or "depmap" in low:
                src_names.append("Open Targets / DepMap")
            elif "openfda" in low:
                src_names.append("FDA Drugs@FDA / FAERS")
            elif "ct.gov" in low or tok.startswith("NCT"):
                src_names.append("ClinicalTrials.gov")
            elif "chembl" in low:
                src_names.append("ChEMBL Bioactivity")
            elif "pmid:" in low or "doi:" in low or "europepmc" in low:
                src_names.append("Peer-Reviewed Literature")

    if not accs:
        for m in re.finditer(r"(?:PMID:\d+|NCT\d{8}|PMC\d+)", notes):
            _add_acc(m.group(0))
            if len(accs) >= 3:
                break

    src_title = " + ".join(src_names[:2]) if src_names else "Multi-Cohort Synthesis"
    basis, cert, role = classify_basis_and_tier(row)
    coh = _clean_v0_text(row.get("cohort_and_stratum", ""))
    con = _clean_v0_text(row.get("assay_and_contrast", ""))
    est = _clean_v0_text(row.get("effect_estimate", ""))
    if row.get("evidence_id") == "EV-P2-T1-002" and row.get("carbon_id") == "C001":
        est = f"{est} (initial AVI #1 scan; refined to Clean >=2mm Lead #2 chr19:17642537-17642554(-))"
    gene_sym = SUBNODE_GENE_MAP.get(row.get("subnode_id", "").strip(), "")

    n_val = row.get("sample_size_n", "").strip()
    n_sub = ""
    if not VS_COUNTS_RE.search(coh):
        ctx_m = SAMPLE_CTX_RE.search(notes)
        if ctx_m:
            pv = PAREN_VS_RE.search(ctx_m.group(1))
            if pv:
                n_sub = _clean_v0_text(pv.group(1))

    p_str = f"p={row['p_value']}" if row.get("p_value") else ""
    f_str = f"FDR={row['fdr_or_adjusted_p']}" if row.get("fdr_or_adjusted_p") else ""
    pf = " · ".join(x for x in (p_str, f_str) if x)
    eid = row["evidence_id"]
    srec = (stat_map or {}).get(eid, {})
    sha64 = srec.get("sha64", "")
    if sha64:
        sha12 = sha64[:12]
    if srec:
        rel_to_ds = {d["local_relpath"]: k for k, d in ds_map.items() if not k.startswith("DS_BASE")}
        primary_ds = rel_to_ds.get(srec.get("anchor_relpath", ""), "") if srec.get("anchor_type") == "STAGED_DATASET" else ""
    anchor_kind = srec.get("anchor_type", "STAGED_DATASET" if primary_ds else "CACHED_API_SNAPSHOT")
    prov_tag = f"SHA-256:{sha12}" if sha12 else _classify_nonfile_prov(row)

    return {
        "src": src_title, "accs": " · ".join(accs[:6]), "basis": basis, "cert": cert, "role": role,
        "coh": coh, "con": con, "est": est, "pf": pf, "n": n_val, "nsub": n_sub,
        "gene": gene_sym, "eid": eid, "run": row["analysis_run_id"],
        "ds": primary_ds, "anchor": anchor_kind, "sha": sha12, "sha64": sha64, "prov": prov_tag,
    }
