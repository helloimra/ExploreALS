"""Deterministic integrity, v1.2 SHA-64 provenance, & Epistemic Asymmetry Rule validator for CarbonALS / ExploreALS."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
CARBON_ROOT = SCRIPTS_DIR.parent
REG_DIR = CARBON_ROOT / "registries"

ALLOWED_REANALYSIS = {"PENDING_PHASE1_REANALYSIS", "IN_PROGRESS", "ADJUDICATED_VERIFIED"}
ALLOWED_EPISTEMIC = {
    "PENDING", "SUPPORTED", "UNPROVEN_UNTESTED", "FALSIFIED_CLINICAL",
    "FALSIFIED_PK_SAFETY", "ARTIFACT_CONFOUNDED", "ESTABLISHED_BENCHMARK",
}
ALLOWED_DECISIONS = {
    "PENDING", "KEEP_CORE", "KEEP_EXPLORATORY_UNPROVEN",
    "RECLASSIFY_BENCHMARK_OR_BIOMARKER", "DROP",
}
FALSIFIED_STATES = {"FALSIFIED_CLINICAL", "FALSIFIED_PK_SAFETY", "ARTIFACT_CONFOUNDED"}
ALLOWED_REDIST_TIERS = {
    "TIER_A_OPEN_REDISTRIBUTABLE",
    "TIER_B_PUBLISHER_HTTPS_FETCH",
    "TIER_C_DUA_OR_BASELINE",
}
BUNDLED_DATASET_IDS = {"DS001_FEAT", "DS_ELIG_BED"}
ALLOWED_ANCHOR_TYPES = {"STAGED_DATASET", "CACHED_API_SNAPSHOT", "DETERMINISTIC_MODEL_OUTPUT"}
EXP_OVERLAP_COLS = [
    "overlap_group_id", "cluster_name", "datasets_involved",
    "overlap_mechanism", "donor_accounting_and_anti_pseudoreplication_rule", "canonical_model_formula",
]
EXP_STAT_COLS = [
    "evidence_id", "analysis_run_id", "inference_class", "statistical_unit",
    "n_statistical_units", "n_unique_donors_or_participants", "exact_contrast",
    "model_formula_or_test", "effect_metric", "effect_estimate", "se_or_ci95",
    "unadjusted_or_primary_nominal_p", "covariate_adjusted_nominal_p", "multiplicity_adjusted_p",
    "multiple_testing_family", "missingness_or_exclusion_rule", "overlap_group_id",
    "anchor_type", "anchor_relpath", "sha64",
]
EXP_UPDATES_COLS = [
    "update_id", "date_iso", "release_tag", "update_category", "affected_ids",
    "decision_impact", "headline", "prior_state_or_assumption",
    "new_evidence_or_revision", "portfolio_and_gate_consequence",
    "primary_sources", "verification_anchor",
]
EXP_LIV_CAND_COLS = [
    "living_id", "origin_subcohort", "gene_or_drug", "candidate_type", "primary_modality_specific",
    "mechanism_summary", "causal_vs_reactive_assessment", "epistemic_state", "decision",
    "clinical_readiness_trl", "next_gate_experimental_class", "primary_evidence_basis",
    "model_prior_dependency", "unsolved_hurdle_count", "unsolved_hurdles_structured",
    "scientific_actionability_tier", "factual_justification", "discriminating_next_test",
    "supporting_living_evidence_ids", "analysis_run_id",
]
EXP_LIV_EV_COLS = [
    "evidence_id", "carbon_id", "subnode_id", "analysis_run_id", "source_type", "source_id_or_locator",
    "cohort_and_stratum", "assay_and_contrast", "effect_direction", "effect_estimate",
    "p_value", "fdr_or_adjusted_p", "sample_size_n", "epistemic_weight", "notes",
]
ALLOWED_UPDATE_CATEGORIES = {
    "CLINICAL_TRIAL", "LITERATURE_INGESTION", "MODEL_REVISION",
}
FLAGSHIP_RUN_IDS = {
    "FLAGSHIP-EALS-030", "FLAGSHIP-EALS-006", "FLAGSHIP-EALS-031", "FLAGSHIP-EALS-001",
    "FLAGSHIP-EALS-002", "FLAGSHIP-EALS-007", "FLAGSHIP-EALS-034", "FLAGSHIP-EALS-037",
}


def load_csv(name: str) -> list[dict[str, str]]:
    path = REG_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required registry: {path}")
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        for idx, r in enumerate(rows, start=2):
            if None in r or any(v is None for v in r.values()):
                raise ValueError(f"{name} row {idx} has malformed column count.")
        return rows


TEXT_EXTS = {".csv", ".tsv", ".json", ".txt", ".md", ".bed", ".cif", ".gtf", ".vcf"}


def sha256_path(path: Path, eol_mode: str = "raw") -> str:
    if path.is_file():
        if eol_mode != "raw" and path.suffix.lower() in TEXT_EXTS:
            raw = path.read_bytes()
            lf = raw.replace(b"\r\n", b"\n")
            data = lf if eol_mode == "lf" else lf.replace(b"\n", b"\r\n")
            return hashlib.sha256(data).hexdigest()
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    tree = hashlib.sha256()
    for fp in sorted((x for x in path.rglob("*") if x.is_file()), key=lambda x: x.relative_to(path).as_posix()):
        rel = fp.relative_to(path).as_posix()
        tree.update(f"{rel}:{sha256_path(fp, eol_mode=eol_mode)}\n".encode("utf-8"))
    return tree.hexdigest()


def sha256_matches(path: Path, expected: str) -> tuple[bool, str]:
    raw_hex = sha256_path(path, "raw")
    if raw_hex == expected:
        return True, raw_hex
    if (path.is_file() and path.suffix.lower() in TEXT_EXTS) or path.is_dir():
        for em in ("crlf", "lf"):
            if sha256_path(path, em) == expected:
                return True, expected
    return False, raw_hex


def sha256_anchor(path: Path, expected: str = "") -> tuple[bool, str]:
    if path.exists():
        if expected:
            _, got = sha256_matches(path, expected)
            return True, got
        return True, sha256_path(path)
    gz_path = Path(str(path) + ".gz")
    if gz_path.is_file():
        h = hashlib.sha256()
        with gzip.open(gz_path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return True, h.hexdigest()
    return False, ""


def resolve_mode(mode_arg: str) -> str:
    if mode_arg in {"full", "cached"}:
        return mode_arg
    return "full" if (CARBON_ROOT / "reports" / "candidates").is_dir() else "cached"


def verify_citations_blob(txt: str, label: str, cite_lock: dict) -> list[str]:
    errs: list[str] = []
    banned = set(cite_lock.get("banned_mismatched_ids", []))
    pmids_ok = cite_lock.get("pmids", {})
    ncts_ok = cite_lock.get("ncts", {})
    dois_ok = cite_lock.get("dois", {})
    for m in sorted(set(re.findall(r"PMID:(\d{5,9})", txt))):
        tok = f"PMID:{m}"
        if tok in banned:
            errs.append(f"CITATION LOCK VIOLATION in {label}: banned/mismatched {tok}")
        elif m not in pmids_ok or not pmids_ok[m].get("title"):
            errs.append(f"CITATION LOCK VIOLATION in {label}: unverified {tok} absent from schemas/verified_citations_lock.json")
    for nct in sorted(set(re.findall(r"\b(NCT\d{8})\b", txt))):
        if nct in banned:
            errs.append(f"CITATION LOCK VIOLATION in {label}: banned/mismatched {nct}")
        elif nct not in ncts_ok or not ncts_ok[nct].get("title"):
            errs.append(f"CITATION LOCK VIOLATION in {label}: unverified {nct} absent from schemas/verified_citations_lock.json")
    for raw_doi in sorted(set(re.findall(r"(?<![A-Za-z0-9_])(10\.\d{4,9}/[A-Za-z0-9._()/:+-]+)", txt))):
        clean_d = raw_doi.rstrip(".,:)]'\"\\")
        if len(clean_d) <= 8 or clean_d.endswith("/"):
            continue
        if clean_d in banned:
            errs.append(f"CITATION LOCK VIOLATION in {label}: banned/mismatched DOI {clean_d}")
        elif clean_d not in dois_ok or not dois_ok[clean_d].get("title"):
            errs.append(f"CITATION LOCK VIOLATION in {label}: unverified DOI {clean_d} absent from schemas/verified_citations_lock.json")
    return errs


def verify_citations_lock(mode: str) -> list[str]:
    cite_fp = CARBON_ROOT / "schemas" / "verified_citations_lock.json"
    if not cite_fp.is_file():
        return ["Missing schemas/verified_citations_lock.json"]
    try:
        cite_lock = json.loads(cite_fp.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"Invalid schemas/verified_citations_lock.json: {exc}"]
    errs: list[str] = []
    targets: list[Path] = sorted(REG_DIR.glob("*.csv"))
    if mode == "full":
        targets.extend([
            CARBON_ROOT / "reports" / "CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md",
            CARBON_ROOT / "reports" / "CARBON_ALS_INTERACTIVE_EXPLORER.html",
            *sorted((CARBON_ROOT / "reports" / "monographs").glob("*.html")),
            CARBON_ROOT / "reports" / "github_pages" / "docs" / "index.html",
            *sorted((CARBON_ROOT / "reports" / "github_pages" / "docs" / "monographs").glob("*.html")),
        ])
    else:
        targets.extend([
            CARBON_ROOT / "docs" / "index.html",
            *sorted((CARBON_ROOT / "docs" / "monographs").glob("*.html")),
        ])
    for fp in targets:
        if fp.is_file():
            errs.extend(verify_citations_blob(fp.read_text(encoding="utf-8"), fp.relative_to(CARBON_ROOT).as_posix(), cite_lock))
    return errs


def verify_all(
    decisions_override: list[dict[str, str]] | None = None,
    evidence_override: list[dict[str, str]] | None = None,
    mode: str = "full",
) -> list[str]:
    from provenance_gates import verify_provenance_gates

    errors: list[str] = []
    datasets = load_csv("datasets_manifest.csv")
    intake = load_csv("candidate_intake_ledger.csv")
    subnodes = load_csv("subnode_dissection.csv")
    decisions = decisions_override if decisions_override is not None else load_csv("candidate_decisions.csv")
    evidence = evidence_override if evidence_override is not None else load_csv("evidence_ledger.csv")
    runs = load_csv("analysis_runs.csv")
    errors.extend(verify_provenance_gates(intake, evidence, runs))

    ds_ids = {d["dataset_id"] for d in datasets}
    lock_fp = CARBON_ROOT / "schemas" / "dataset_files_lock.json"
    lock_ds: dict = {}
    if not lock_fp.is_file():
        errors.append("Missing schemas/dataset_files_lock.json")
    else:
        try:
            lock_obj = json.loads(lock_fp.read_text(encoding="utf-8"))
            lock_ds = lock_obj.get("datasets", lock_obj)
            if set(lock_ds.keys()) != ds_ids:
                errors.append("schemas/dataset_files_lock.json dataset_id set does not match datasets_manifest.csv")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Invalid schemas/dataset_files_lock.json: {exc}")

    for d in datasets:
        dsid = d["dataset_id"]
        if d.get("redistribution_tier") not in ALLOWED_REDIST_TIERS:
            errors.append(f"{dsid}: invalid redistribution_tier '{d.get('redistribution_tier')}'")
        if not d.get("canonical_fetch_url_or_instructions", "").strip():
            errors.append(f"{dsid}: missing canonical_fetch_url_or_instructions")
        p = CARBON_ROOT / d["local_relpath"]
        must_exist = (mode == "full") or (dsid in BUNDLED_DATASET_IDS)
        if not p.exists():
            if must_exist:
                errors.append(f"Missing staged dataset path: {d['local_relpath']}")
        elif not sha256_matches(p, d["sha256"])[0]:
            lf_files = (lock_ds.get(dsid) or {}).get("files") or []
            actual_rels = sorted(x.relative_to(p).as_posix() for x in p.rglob("*") if x.is_file()) if p.is_dir() else []
            per_file_ok = (
                p.is_dir()
                and bool(lf_files)
                and actual_rels == sorted(f["rel"] for f in lf_files)
                and all(sha256_matches(p / f["rel"], f["sha256"])[0] for f in lf_files)
            )
            if not per_file_ok:
                errors.append(f"SHA-256 mismatch on staged dataset ({'file' if p.is_file() else 'dir'}): {d['local_relpath']}")

    ovl_rows = load_csv("cohort_overlap_map.csv")
    if ovl_rows and list(ovl_rows[0].keys()) != EXP_OVERLAP_COLS:
        errors.append(f"Schema header mismatch in cohort_overlap_map.csv: {list(ovl_rows[0].keys())}")
    if len(ovl_rows) != 8:
        errors.append(f"cohort_overlap_map.csv must define 8 overlap clusters (got {len(ovl_rows)})")
    ovl_ids = {r["overlap_group_id"] for r in ovl_rows}
    for r in ovl_rows:
        for tok in filter(None, r["datasets_involved"].split(";")):
            base_ds = tok.split(":")[0].strip()
            if base_ds not in ds_ids:
                errors.append(f"cohort_overlap_map.csv {r['overlap_group_id']} cites unknown dataset_id '{base_ds}'")

    stat_rows = load_csv("statistical_models_and_contrasts.csv")
    if stat_rows and list(stat_rows[0].keys()) != EXP_STAT_COLS:
        errors.append(f"Schema header mismatch in statistical_models_and_contrasts.csv: {list(stat_rows[0].keys())}")
    p3b_ev_rows = load_csv("phase3b_denovo_evidence.csv")
    liv_cand_rows = load_csv("living_evidence_candidates.csv")
    liv_ev_rows = load_csv("living_evidence_candidate_evidence.csv")
    if liv_cand_rows and list(liv_cand_rows[0].keys()) != EXP_LIV_CAND_COLS:
        errors.append(f"Schema header mismatch in living_evidence_candidates.csv: {list(liv_cand_rows[0].keys())}")
    if liv_ev_rows and list(liv_ev_rows[0].keys()) != EXP_LIV_EV_COLS:
        errors.append(f"Schema header mismatch in living_evidence_candidate_evidence.csv: {list(liv_ev_rows[0].keys())}")
    errors.extend(verify_provenance_gates([], liv_ev_rows, runs))
    run_ids_prelim = {ar["analysis_run_id"] for ar in runs}
    if evidence_override is None:
        exp_all_ev_ids = {e["evidence_id"] for e in evidence} | {e["evidence_id"] for e in p3b_ev_rows} | {e["evidence_id"] for e in liv_ev_rows}
        got_stat_ev_ids = [r["evidence_id"] for r in stat_rows]
        if len(got_stat_ev_ids) != len(set(got_stat_ev_ids)) or set(got_stat_ev_ids) != exp_all_ev_ids:
            errors.append(
                f"statistical_models_and_contrasts.csv evidence_id bijection failed: "
                f"{len(got_stat_ev_ids)} rows vs {len(exp_all_ev_ids)} union evidence rows"
            )
    for sr in stat_rows:
        ev_id = sr["evidence_id"]
        if sr["analysis_run_id"] not in run_ids_prelim:
            errors.append(f"{ev_id}: statistical_models_and_contrasts.csv unknown run {sr['analysis_run_id']}")
        if sr["overlap_group_id"] not in (ovl_ids | {"NONE_INDEPENDENT_OR_EXTERNAL"}):
            errors.append(f"{ev_id}: statistical_models_and_contrasts.csv unknown overlap_group_id '{sr['overlap_group_id']}'")
        if sr["anchor_type"] not in ALLOWED_ANCHOR_TYPES:
            errors.append(f"{ev_id}: invalid anchor_type '{sr['anchor_type']}'")
        if not re.fullmatch(r"[0-9a-f]{64}", sr["sha64"]):
            errors.append(f"{ev_id}: invalid 64-char sha64 '{sr['sha64']}'")
        se_val = sr["se_or_ci95"].strip()
        if se_val and (
            not re.match(r"^(?:SE|95%\s*CI|CI95)\b", se_val)
            or se_val.count("(") != se_val.count(")")
            or se_val.count("[") != se_val.count("]")
        ):
            errors.append(f"{ev_id}: malformed se_or_ci95 '{se_val}'")
        if sr["statistical_unit"] == "visium_55um_spot" and sr["n_statistical_units"] and sr["n_statistical_units"] == sr["n_unique_donors_or_participants"]:
            errors.append(f"{ev_id}: visium_55um_spot must not equate n_statistical_units with n_unique_donors_or_participants")
        if "/100" in sr["effect_estimate"] or re.search(r"liability\s*=\s*[0-9.]+\s*pct", sr["effect_estimate"], re.I):
            errors.append(f"{ev_id}: retired /100 or liability pct score leaked into statistical_models_and_contrasts.csv")
        if sr["covariate_adjusted_nominal_p"].strip():
            cov_blob = f"{sr['model_formula_or_test']} ; {sr['exact_contrast']}"
            if (
                "survival days" in sr["model_formula_or_test"].lower()
                or "z_diff" in sr["effect_metric"].lower()
                or not re.search(
                    r"\b(?:ols|cox|adjusted|adj|residualized|center|rin|gc|gc_z|age|sex|pmi|tricals|pnfh)\b", cov_blob, re.I
                )
            ):
                errors.append(f"{ev_id}: covariate_adjusted_nominal_p populated without covariate-adjusted model formula")
        if sr["multiple_testing_family"] == "NOT_APPLICABLE_NON_FREQUENTIST" and re.search(r"\bols\b", sr["model_formula_or_test"], re.I):
            errors.append(f"{ev_id}: non-frequentist row carries OLS model_formula_or_test")
        if sr["anchor_relpath"].endswith("41593_2025_2118_MOESM3_ESM.xlsx") and "survival days" in sr["model_formula_or_test"].lower():
            if sr["statistical_unit"] != "paired_ipsc_donor_line" or any(
                k in sr["exact_contrast"].lower() for k in ("deg ", "splicing", "scn8a", "pearson")
            ):
                errors.append(f"{ev_id}: copied Bye survival-screen model formula onto non-survival contrast")
        found_anc, got_sha = sha256_anchor(CARBON_ROOT / sr["anchor_relpath"], sr["sha64"])
        must_have_anc = (mode == "full") or (sr["anchor_type"] in {"CACHED_API_SNAPSHOT", "DETERMINISTIC_MODEL_OUTPUT"})
        if not found_anc:
            if must_have_anc:
                errors.append(f"{ev_id}: missing anchor_relpath '{sr['anchor_relpath']}'")
        elif got_sha != sr["sha64"]:
            errors.append(f"{ev_id}: sha64 mismatch on '{sr['anchor_relpath']}' ({got_sha[:12]} != {sr['sha64'][:12]})")
    stat_by_eid = {r["evidence_id"]: r for r in stat_rows}
    ev_by_eid = {r["evidence_id"]: r for r in evidence}
    curated_stat_guards = {
        "EV-B1-001": ("PRIMARY_BAYESIAN_SPLICING_RECOMPUTE", "in_vitro_perturbation_replicate", "p_d_psi_0_05_per_lsv_junction"),
        "EV-B1-011": ("PRIMARY_BAYESIAN_SPLICING_RECOMPUTE", "in_vitro_perturbation_replicate", "p_d_psi_0_05_per_lsv_junction"),
        "EV-B2-001": ("PUBLISHED_TRIAL_OR_GENETIC_INFERENCE", "unique_human_donor", "Tsitkov"),
        "EV-B2-004": ("PUBLISHED_TRIAL_OR_GENETIC_INFERENCE", "unique_human_donor", "Table S9"),
        "EV-B2-011": ("PRIMARY_BAYESIAN_SPLICING_RECOMPUTE", "in_vitro_perturbation_replicate", "p_d_psi_0_05_per_lsv_junction"),
        "EV-B2-014": ("PRIMARY_BAYESIAN_SPLICING_RECOMPUTE", "in_vitro_perturbation_replicate", "p_d_psi_0_05_per_lsv_junction"),
        "EV-P2-T3-004": ("PRIMARY_FREQUENTIST_RECOMPUTE", "unique_human_donor", "Pearson r"),
        "EV-B4-007": ("PRIMARY_BAYESIAN_SPLICING_RECOMPUTE", "in_vitro_perturbation_replicate", "p_d_psi_0_05_per_lsv_junction"),
        "EV-P4-001": ("STRUCTURAL_OR_MECHANISTIC_MODEL_PRIOR", "cryoem_structure_entry_and_gnomad_variant_set", "NMN-bound ARM-SAM"),
        "EV-P4-002": ("PRIMARY_BAYESIAN_SPLICING_RECOMPUTE", "in_vitro_perturbation_replicate", "p_d_psi_0_05_per_lsv_junction"),
        "EV-P4-003": ("PRIMARY_FREQUENTIST_RECOMPUTE", "in_vitro_perturbation_replicate", "ClinVar"),
        "EV-P4-004": ("STRUCTURAL_OR_MECHANISTIC_MODEL_PRIOR", "genomic_cis_variant", "AlphaGenome"),
        "EV-P4-005": ("PUBLISHED_TRIAL_OR_GENETIC_INFERENCE", "gwas_credible_set_variant", "59-variant"),
        "EV-P4-006": ("STRUCTURAL_OR_MECHANISTIC_MODEL_PRIOR", "c1q_heterotrimer_subunit_chain", "1 heterotrimer / 3 chains"),
        "EV-P4-007": ("PUBLISHED_TRIAL_OR_GENETIC_INFERENCE", "unique_human_donor", "n=189"),
        "EV-P4-008": ("PRIMARY_BAYESIAN_SPLICING_RECOMPUTE", "in_vitro_perturbation_replicate", "p_d_psi_0_05_per_lsv_junction"),
        "EV-P4-009": ("PUBLISHED_TRIAL_OR_GENETIC_INFERENCE", "human_trial_or_genetic_participant", "Unadjusted 18-mo survival relative risk"),
    }
    for g_eid, (exp_ic, exp_unit, exp_kw) in curated_stat_guards.items():
        if g_eid in stat_by_eid:
            gsr = stat_by_eid[g_eid]
            if gsr["inference_class"] != exp_ic or gsr["statistical_unit"] != exp_unit or exp_kw not in gsr["model_formula_or_test"]:
                errors.append(f"{g_eid}: curated statistical record overwritten ({gsr['inference_class']} / {gsr['statistical_unit']} / {gsr['model_formula_or_test'][:48]})")
    for qtl_eid in ("EV-B2-001", "EV-B2-004"):
        if qtl_eid in stat_by_eid and ("Bonferroni" not in stat_by_eid[qtl_eid]["multiple_testing_family"] or "BH-FDR" in stat_by_eid[qtl_eid]["multiple_testing_family"]):
            errors.append(f"{qtl_eid}: Answer ALS QTL record must use study-adjusted Bonferroni family, not BH-FDR")
    all_majiq_eids = ("EV-B1-001", "EV-B1-011", "EV-B2-011", "EV-B2-014", "EV-B4-007", "EV-P4-002", "EV-P4-008")
    for maj_eid in all_majiq_eids:
        if maj_eid in stat_by_eid:
            msr = stat_by_eid[maj_eid]
            if msr["multiplicity_adjusted_p"].strip() or "1 - P(|dPSI|" in json.dumps(msr) or "1-P(|dPSI|" in json.dumps(msr):
                errors.append(f"{maj_eid}: MAJIQ Bayesian p_d_psi_0_05 output must not use 0.10 complement formula or populate frequentist multiplicity_adjusted_p")
            if "p_d_psi_0_05_per_lsv_junction" not in msr["multiple_testing_family"] or "Transcriptome-wide BH-FDR" in msr["multiple_testing_family"] or "LeafCutter" in msr["multiple_testing_family"]:
                errors.append(f"{maj_eid}: MAJIQ Bayesian p_d_psi_0_05 output must use MAJIQ non-frequentist multiple_testing_family")
        if evidence_override is None and maj_eid in ev_by_eid and ev_by_eid[maj_eid]["fdr_or_adjusted_p"].strip():
            errors.append(f"{maj_eid}: MAJIQ Bayesian p_d_psi_0_05 output must be stored separately from frequentist fdr_or_adjusted_p")
    if evidence_override is None:
        if "EV-B1-001" in ev_by_eid and ("cryptic donor" in json.dumps(ev_by_eid["EV-B1-001"]).lower() or "novel_acceptor" not in json.dumps(ev_by_eid["EV-B1-001"])):
            errors.append("EV-B1-001: UNC13A MOESM11 line 983 must be classified as novel_acceptor, not cryptic donor")
        if "EV-B1-006" in ev_by_eid and ("LeafCutter" in ev_by_eid["EV-B1-006"]["notes"] or "line 4857" not in ev_by_eid["EV-B1-006"]["notes"]):
            errors.append("EV-B1-006: STMN2 exon-2a note must cite Brown 2022 MOESM11 line 4857 MAJIQ, not LeafCutter")
        if "EV-B1-011" in ev_by_eid and ("confirm 126-bp" in ev_by_eid["EV-B1-011"]["notes"] or "PMID:41174170" not in ev_by_eid["EV-B1-011"]["notes"]):
            errors.append("EV-B1-011: KCNQ2 note must credit Joseph et al. 2025 (PMID:41174170) for translated KCNQ2-DeltaE5 protein")
        if "EV-B4-007" in ev_by_eid:
            n407 = json.dumps(ev_by_eid["EV-B4-007"])
            if any(bad in n407 for bad in ("-0.431", "-0.692", "0.000485", "4.85e-4")) or "line 9820" not in n407 or "line 12022" not in n407 or "PMID:38771640" not in n407:
                errors.append("EV-B4-007: SCN8A note must cite MOESM12 line 9820 (-0.06007, padj=0.49335) & MOESM13 line 12022 (+0.10750, padj=0.99867) and Vanoye 2024 (PMID:38771640)")
        if "EV-B2-001" in ev_by_eid and ("N=261" in json.dumps(ev_by_eid["EV-B2-001"]) or "-0.2955" not in ev_by_eid["EV-B2-001"]["notes"] or "[PREPRINT]" not in ev_by_eid["EV-B2-001"]["cohort_and_stratum"]):
            errors.append("EV-B2-001: SCFD1 record must identify Tsitkov 2026 [PREPRINT], avoid pooled N=261, and report same-variant rs229143-A iMGL slopes")
        if "EV-P3A-002" in ev_by_eid and ("max_mm=0" in ev_by_eid["EV-P3A-002"]["notes"] or "95,283" not in ev_by_eid["EV-P3A-002"]["notes"]):
            errors.append("EV-P3A-002: G2E3 #1 note must report completed 1-mm off-target counts (max_mm=1, 95,283 loci) and NA 2-mm")
        if "EV-P4-007" in ev_by_eid and ("186" not in ev_by_eid["EV-P4-007"]["notes"] or "Zenodo:21471267" not in ev_by_eid["EV-P4-007"]["source_id_or_locator"]):
            errors.append("EV-P4-007: SCFD1 iMGL record must distinguish published 189/188/188 cohorts from inferred 186/185/185 fit counts and retain Zenodo:21471267 locator")
        if "EV-P4-001" in ev_by_eid and "NMN/1AD-activated" in json.dumps(ev_by_eid["EV-P4-001"]):
            errors.append("EV-P4-001: SARM1 7NAL must describe NMN-bound ARM-SAM ring from an NMN/1AD-incubated preparation")
    ds_desc_map = {d["dataset_id"]: d["description"] for d in datasets}
    if any(
        (dsid in ds_desc_map and req not in ds_desc_map[dsid])
        for dsid, req in (("DS_PDB_7ANW", "2.68A"), ("DS_PDB_7DJT", "H8L"), ("DS_PDB_4KC3", "3.27A"), ("DS_PDB_2Z0D", "1.90A"))
    ):
        errors.append("datasets_manifest.csv: PDB descriptions must match deposited resolutions/ligands (7ANW 2.68A, 7DJT VI3+H8L, 4KC3 3.27A, 2Z0D 1.90A)")
    if mode == "full" and all(k in stat_by_eid for k in all_majiq_eids):
        moesm11_fp = CARBON_ROOT / "data" / "genomics_splicing" / "tdp43_cryptic_sources" / "Brown2022_41586_2022_4436_MOESM11_ESM.csv"
        if moesm11_fp.is_file():
            with moesm11_fp.open(encoding="utf-8") as mf:
                m_rows = list(csv.DictReader(mf))
            for maj_eid, fline, exp_tok in (
                ("EV-B1-001", 983, "2.310e-19"),
                ("EV-B1-011", 4527, "4.153e-24"),
                ("EV-B2-011", 5690, "3.272e-06"),
                ("EV-B2-014", 4145, "3.256e-06"),
                ("EV-B4-007", 210, "1.95e-06"),
                ("EV-P4-002", 981, "1.822e-15"),
                ("EV-P4-008", 4145, "3.256e-06"),
            ):
                raw_fdr = float(m_rows[fline - 2]["FDR"])
                if abs(raw_fdr - float(exp_tok)) / max(raw_fdr, 1e-30) > 0.01 or exp_tok not in stat_by_eid[maj_eid]["effect_estimate"]:
                    errors.append(f"{maj_eid}: MOESM11 line {fline} FDR concordance check failed ({raw_fdr} vs {exp_tok})")
    schemas_md_fp = CARBON_ROOT / "schemas" / "SCHEMAS.md"
    if schemas_md_fp.is_file():
        sm_txt = schemas_md_fp.read_text(encoding="utf-8")
        if "public_release_manifest.json" in sm_txt or "reports/github_pages" in sm_txt or "TIER_C_DUA_OR_BASELINE" not in sm_txt:
            errors.append("schemas/SCHEMAS.md: must list 2 shipped JSON lock manifests, include TIER_C_DUA_OR_BASELINE, and omit public_release_manifest.json / reports/github_pages")
    if "EV-P4-006" in stat_by_eid and stat_by_eid["EV-P4-006"]["n_statistical_units"] != "3":
        errors.append(f"EV-P4-006: C1q c1q_heterotrimer_subunit_chain count must be 3 (got {stat_by_eid['EV-P4-006']['n_statistical_units']})")
    if "EV-P4-007" in stat_by_eid:
        r07 = stat_by_eid["EV-P4-007"]
        if r07["n_statistical_units"] != "189" or r07["n_unique_donors_or_participants"] != "189" or "genome-wide" in r07["multiple_testing_family"].lower() or "251-gene" not in r07["multiple_testing_family"]:
            errors.append(f"EV-P4-007: SCFD1 must record n=189 untreated eQTL donor count and targeted 251-gene NeuroKO screen")
    if "EV-P4-009" in stat_by_eid:
        r09 = stat_by_eid["EV-P4-009"]
        if r09["unadjusted_or_primary_nominal_p"] != "0.0760" or r09["covariate_adjusted_nominal_p"] != "0.00200" or r09["n_statistical_units"] != "478" or r09["n_unique_donors_or_participants"] != "478":
            errors.append(f"EV-P4-009: riluzole must record n=478 (236+242), unadjusted p=0.0760, and covariate-adjusted p=0.00200")

    intake_ids = {r["carbon_id"] for r in intake}
    if len(intake_ids) != len(intake):
        errors.append("Duplicate carbon_id in candidate_intake_ledger.csv")

    for r in intake:
        for dsid in filter(None, r["staged_dataset_ids"].split(";")):
            if dsid not in ds_ids:
                errors.append(f"{r['carbon_id']} references unknown dataset_id '{dsid}'")

    subnode_ids = {sn["subnode_id"] for sn in subnodes}
    for sn in subnodes:
        if sn["parent_carbon_id"] not in intake_ids:
            errors.append(f"Subnode {sn['subnode_id']} references unknown parent {sn['parent_carbon_id']}")

    ev_ids = {e["evidence_id"] for e in evidence}
    run_ids = {ar["analysis_run_id"] for ar in runs}
    for ar in runs:
        for dsid in filter(None, ar["datasets_used"].split(";")):
            if dsid not in ds_ids:
                errors.append(f"Analysis run {ar['analysis_run_id']} references unknown dataset_id '{dsid}'")
    for e in evidence:
        if e["carbon_id"] not in intake_ids:
            errors.append(f"Evidence {e['evidence_id']} references unknown carbon_id {e['carbon_id']}")
        if e["analysis_run_id"] and e["analysis_run_id"] not in run_ids:
            errors.append(f"Evidence {e['evidence_id']} references unknown run {e['analysis_run_id']}")

    p2_spans: set[str] = set()
    p2_rows: list[dict[str, str]] = []
    p2_path = REG_DIR / "phase2_multiplex_intervals.csv"
    if p2_path.exists():
        p2_rows = load_csv("phase2_multiplex_intervals.csv")
        if p2_rows:
            for col in p2_rows[0]:
                if any(tok in col.lower() for tok in ("sequence", "rna_5to3", "dna_5to3", "oligomer", "aso_")):
                    errors.append(f"phase2_multiplex_intervals.csv contains banned raw sequence column '{col}'")
        for row in p2_rows:
            if row["candidate_id"] not in (intake_ids | subnode_ids):
                errors.append(f"Phase2 interval {row['interval_id']} references unknown candidate_id {row['candidate_id']}")
            if row["analysis_run_id"] not in run_ids:
                errors.append(f"Phase2 interval {row['interval_id']} references unknown run {row['analysis_run_id']}")
            s_pos, e_pos, w_len = int(row["grch38_start"]), int(row["grch38_end"]), int(row["length_bp"])
            if s_pos > e_pos or (e_pos - s_pos + 1) != w_len:
                errors.append(f"Phase2 interval {row['interval_id']} has invalid GRCh38 span ({s_pos}..{e_pos} vs {w_len})")
            p2_spans.add(f"{row['chrom']}:{row['grch38_start']}-{row['grch38_end']}({row['strand']})")

    coord_re = re.compile(r"chr[0-9XYM]+:\d+-\d+\([+-]\)")
    if p2_spans:
        for e in evidence:
            if e["evidence_id"] == "EV-P2-T1-002":
                for sp in coord_re.findall(e["effect_estimate"] + " " + e["notes"]):
                    if sp not in p2_spans:
                        errors.append(f"EV-P2-T1-002 cites interval {sp} absent from phase2_multiplex_intervals.csv")

    dec_ids = {d["carbon_id"] for d in decisions}
    if dec_ids != intake_ids:
        errors.append("candidate_decisions.csv carbon_id set does not match candidate_intake_ledger.csv 1-to-1")

    for d in decisions:
        cid = d["carbon_id"]
        if d["reanalysis_state"] not in ALLOWED_REANALYSIS:
            errors.append(f"{cid}: invalid reanalysis_state '{d['reanalysis_state']}'")
        if d["epistemic_state"] not in ALLOWED_EPISTEMIC:
            errors.append(f"{cid}: invalid epistemic_state '{d['epistemic_state']}'")
        if d["decision"] not in ALLOWED_DECISIONS:
            errors.append(f"{cid}: invalid decision '{d['decision']}'")

        # HARD EPISTEMIC ASYMMETRY INVARIANT:
        if d["decision"] == "DROP":
            if d["epistemic_state"] == "UNPROVEN_UNTESTED":
                errors.append(f"EPISTEMIC VIOLATION on {cid}: Cannot DROP an UNPROVEN_UNTESTED candidate!")
            if d["epistemic_state"] not in FALSIFIED_STATES:
                errors.append(f"EPISTEMIC VIOLATION on {cid}: DROP requires epistemic_state in {sorted(FALSIFIED_STATES)}")
            if not d["factual_justification"].strip() or not d["supporting_evidence_ids"].strip():
                errors.append(f"EPISTEMIC VIOLATION on {cid}: DROP requires factual_justification and supporting_evidence_ids")

        if d["reanalysis_state"] == "ADJUDICATED_VERIFIED":
            if d["decision"] == "PENDING" or d["epistemic_state"] == "PENDING":
                errors.append(f"{cid}: ADJUDICATED_VERIFIED cannot leave decision or epistemic_state PENDING")
            for evid in filter(None, d["supporting_evidence_ids"].split(";")):
                if evid not in ev_ids:
                    errors.append(f"{cid}: supporting_evidence_id '{evid}' missing from evidence_ledger.csv")
            if d["decision"] == "KEEP_EXPLORATORY_UNPROVEN" and not d["discriminating_next_test"].strip():
                errors.append(f"{cid}: KEEP_EXPLORATORY_UNPROVEN requires discriminating_next_test")
            if p2_spans and cid in {"C001", "C002", "C006"}:
                for sp in coord_re.findall(d["discriminating_next_test"]):
                    if sp not in p2_spans:
                        errors.append(f"{cid} discriminating_next_test cites interval {sp} absent from phase2_multiplex_intervals.csv")

        if mode == "full" and decisions_override is None and evidence_override is None:
            md_fp = CARBON_ROOT / "reports" / "candidates" / f"{cid}.md"
            if not md_fp.is_file():
                errors.append(f"Missing candidate dossier: reports/candidates/{cid}.md")
            else:
                md_txt = md_fp.read_text(encoding="utf-8")
                if "<!-- CARBON_SYNC_START -->" not in md_txt:
                    errors.append(f"reports/candidates/{cid}.md missing <!-- CARBON_SYNC_START --> block")
                if f"decision = {d['decision']}" not in md_txt or f"epistemic_state = {d['epistemic_state']}" not in md_txt:
                    errors.append(f"reports/candidates/{cid}.md out of sync with candidate_decisions.csv decision/epistemic_state")
                for evid in filter(None, d["supporting_evidence_ids"].split(";")):
                    if f"`{evid}`" not in md_txt:
                        errors.append(f"reports/candidates/{cid}.md missing supporting_evidence_id {evid}")
                if re.search(r"work/phase1_batches/batch_\d+/(evidence_ledger|subnode_dissection|candidate_decisions)\.csv", md_txt):
                    errors.append(f"reports/candidates/{cid}.md contains stale batch registry link")

    if decisions_override is None and evidence_override is None:
        from phase3_gates import RAW_OLIGO_SEQ_RE, verify_phase3a_gates
        from phase3b_gates import GAPPED_OLIGO_RE, _build_explore_exclusions, verify_phase3b_gates
        from phase4_gates import CAPITAL_DOLLAR_LEAK_RE, verify_phase4_gates

        excl_g, excl_d = _build_explore_exclusions(intake, subnodes)
        p3b_gd = {r["gene_or_drug"].strip() for r in load_csv("phase3b_denovo_candidates.csv")}
        liv_ids = {r["living_id"] for r in liv_cand_rows}
        liv_ev_ids = {e["evidence_id"] for e in liv_ev_rows}
        if len(liv_ids) != len(liv_cand_rows):
            errors.append("Duplicate living_id in living_evidence_candidates.csv")
        for le in liv_ev_rows:
            if le["carbon_id"] not in liv_ids or le["analysis_run_id"] not in run_ids:
                errors.append(f"Living evidence {le['evidence_id']} has invalid carbon_id/analysis_run_id")
        for lc in liv_cand_rows:
            lid, lgd = lc["living_id"], lc["gene_or_drug"].strip()
            if not re.fullmatch(r"L0[1-9]", lid):
                errors.append(f"living_evidence_candidates.csv invalid living_id '{lid}'")
            if ";" in lgd or "/" in lgd or not lgd:
                errors.append(f"{lid}: non-atomic gene_or_drug '{lgd}'")
            if lgd in excl_g or lgd.lower() in excl_d or lgd in p3b_gd:
                errors.append(f"LIVING_OVERLAP VIOLATION on {lid}: '{lgd}' overlaps existing intake/subnodes/Phase 3B!")
            if lc["decision"] == "DROP":
                if lc["epistemic_state"] == "UNPROVEN_UNTESTED":
                    errors.append(f"EPISTEMIC VIOLATION on {lid}: Cannot DROP an UNPROVEN_UNTESTED living candidate!")
                if lc["epistemic_state"] not in FALSIFIED_STATES:
                    errors.append(f"EPISTEMIC VIOLATION on {lid}: DROP requires falsified epistemic_state")
            if lc["decision"] == "KEEP_EXPLORATORY_UNPROVEN" and not lc["discriminating_next_test"].strip():
                errors.append(f"{lid}: KEEP_EXPLORATORY_UNPROVEN requires discriminating_next_test")
            if lc["analysis_run_id"] not in run_ids:
                errors.append(f"{lid}: unknown analysis_run_id '{lc['analysis_run_id']}'")
            for levid in filter(None, lc["supporting_living_evidence_ids"].split(";")):
                if levid not in liv_ev_ids:
                    errors.append(f"{lid}: supporting_living_evidence_id '{levid}' missing from living_evidence_candidate_evidence.csv")

        upd_rows = load_csv("living_evidence_updates.csv")
        if not upd_rows:
            errors.append("living_evidence_updates.csv must contain at least 1 row")
        elif list(upd_rows[0].keys()) != EXP_UPDATES_COLS:
            errors.append(f"Schema header mismatch in living_evidence_updates.csv: {list(upd_rows[0].keys())}")
        acc_ids = {r["accession_id"] for r in load_csv("candidate_accessions.csv")}
        valid_aff = acc_ids | {"PORTFOLIO_WIDE"}
        valid_anc = ev_ids | {e["evidence_id"] for e in p3b_ev_rows} | liv_ev_ids | run_ids | FLAGSHIP_RUN_IDS
        seen_upd_ids: set[str] = set()
        sort_keys: list[tuple[str, str]] = []
        for ur in upd_rows:
            uid = ur["update_id"].strip()
            if not re.fullmatch(r"UPD-\d{4}-\d{2}-\d{2}-\d{2}", uid):
                errors.append(f"living_evidence_updates.csv invalid update_id '{uid}'")
            if uid in seen_upd_ids:
                errors.append(f"living_evidence_updates.csv duplicate update_id '{uid}'")
            seen_upd_ids.add(uid)
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ur["date_iso"].strip()) or not uid.startswith(f"UPD-{ur['date_iso'].strip()}-"):
                errors.append(f"{uid}: date_iso '{ur['date_iso']}' mismatch with update_id")
            sort_keys.append((ur["date_iso"].strip(), uid))
            if not re.fullmatch(r"v\d+\.\d+\.\d+", ur["release_tag"].strip()):
                errors.append(f"{uid}: release_tag must be bare semantic version vX.Y.Z (got '{ur['release_tag']}')")
            if ur["update_category"] not in ALLOWED_UPDATE_CATEGORIES:
                errors.append(f"{uid}: invalid update_category '{ur['update_category']}'")
            for col_k in EXP_UPDATES_COLS:
                if not ur[col_k].strip():
                    errors.append(f"{uid}: empty required column '{col_k}'")
            for aid in filter(None, ur["affected_ids"].split(";")):
                if aid.strip() not in valid_aff:
                    errors.append(f"{uid}: unknown affected_id '{aid}'")
            for anc_tok in filter(None, ur["verification_anchor"].split(";")):
                if anc_tok.strip() not in valid_anc:
                    errors.append(f"{uid}: unknown verification_anchor '{anc_tok}'")
            joined_txt = " ".join(ur.values())
            if RAW_OLIGO_SEQ_RE.search(joined_txt) or GAPPED_OLIGO_RE.search(joined_txt):
                errors.append(f"{uid}: biosecurity oligomer sequence guard failed in living_evidence_updates.csv")
            if CAPITAL_DOLLAR_LEAK_RE.search(joined_txt):
                errors.append(f"{uid}: financial/capital token leaked in living_evidence_updates.csv")
            if (
                "/100" in joined_txt
                or "CarbonALS" in joined_txt
                or "ExploreALS v1.0" in joined_txt
                or "ExploreALS v1.1" in joined_txt
                or re.search(r"\bwave\b", joined_txt, re.IGNORECASE)
            ):
                errors.append(f"{uid}: banned nomenclature leaked in living_evidence_updates.csv")
        if sort_keys != sorted(sort_keys, reverse=True):
            errors.append("living_evidence_updates.csv must be sorted reverse-chronologically by (date_iso, update_id)")

        errors.extend(verify_phase3a_gates(CARBON_ROOT, p2_rows, decisions, run_ids, load_csv, mode=mode))
        errors.extend(verify_phase3b_gates(CARBON_ROOT, intake, subnodes, runs, load_csv, mode=mode))
        errors.extend(verify_phase4_gates(CARBON_ROOT, decisions, run_ids, load_csv, mode=mode))
        errors.extend(verify_citations_lock(mode=mode))

    return errors


def run_selftest(mode: str = "full") -> None:
    cite_lock = json.loads((CARBON_ROOT / "schemas" / "verified_citations_lock.json").read_text(encoding="utf-8"))
    errs_cite1 = verify_citations_blob("Fake citation PMID:99999999 and NCT99999999", "selftest", cite_lock)
    assert len(errs_cite1) == 2 and all("unverified" in e for e in errs_cite1), "Self-test failed to block unverified PMID/NCT!"
    errs_cite2 = verify_citations_blob("Mismatched PMID:24145411", "selftest", cite_lock)
    assert any("banned/mismatched" in e for e in errs_cite2), "Self-test failed to block banned mismatched PMID!"
    base = load_csv("candidate_decisions.csv")
    bad = [dict(r) for r in base]
    bad[0]["epistemic_state"] = "UNPROVEN_UNTESTED"
    bad[0]["decision"] = "DROP"
    errs = verify_all(decisions_override=bad, mode=mode)
    assert any("Cannot DROP an UNPROVEN_UNTESTED" in e for e in errs), "Self-test failed to block UNPROVEN DROP!"

    ev_base = load_csv("evidence_ledger.csv")
    if ev_base:
        bad_ev = [dict(r) for r in ev_base]
        bad_ev[0]["p_value"] = "0.05"
        bad_ev[0]["fdr_or_adjusted_p"] = "1e-10"
        errs_ev = verify_all(evidence_override=bad_ev, mode=mode)
        assert any("CONTRAST MIXING VIOLATION" in e for e in errs_ev), "Self-test failed to block p > fdr mixing!"
        bad_ev2 = [dict(r) for r in ev_base]
        bad_ev2[0]["fdr_or_adjusted_p"] = "0.99"
        errs_ev2 = verify_all(evidence_override=bad_ev2, mode=mode)
        assert any("banned placeholder" in e for e in errs_ev2), "Self-test failed to block 0.99 placeholder!"

    from phase3b_gates import verify_phase3b_gates

    p3b_base = load_csv("phase3b_denovo_candidates.csv")
    bad_p3b_epi = [dict(r) for r in p3b_base]
    bad_p3b_epi[0]["epistemic_state"] = "UNPROVEN_UNTESTED"
    bad_p3b_epi[0]["decision"] = "DROP"
    errs_p3b_epi = verify_phase3b_gates(CARBON_ROOT, load_csv("candidate_intake_ledger.csv"), load_csv("subnode_dissection.csv"), load_csv("analysis_runs.csv"), load_csv, cand_override=bad_p3b_epi, mode=mode)
    assert any("Cannot DROP an UNPROVEN_UNTESTED" in e for e in errs_p3b_epi), "Phase 3B self-test failed to block UNPROVEN DROP!"
    bad_p3b_ov = [dict(r) for r in p3b_base]
    bad_p3b_ov[0]["gene_or_drug"] = "UNC13A"
    errs_p3b_ov = verify_phase3b_gates(CARBON_ROOT, load_csv("candidate_intake_ledger.csv"), load_csv("subnode_dissection.csv"), load_csv("analysis_runs.csv"), load_csv, cand_override=bad_p3b_ov, mode=mode)
    assert any("EXPLORE_OVERLAP VIOLATION" in e for e in errs_p3b_ov), "Phase 3B self-test failed to block ExploreALS overlap!"

    from phase4_gates import verify_phase4_gates

    p4_base = load_csv("phase4_unified_portfolio.csv")
    bad_p4_epi = [dict(r) for r in p4_base]
    bad_p4_epi[0]["epistemic_state"] = "UNPROVEN_UNTESTED"
    bad_p4_epi[0]["decision"] = "DROP"
    errs_p4_epi = verify_phase4_gates(CARBON_ROOT, base, {r["analysis_run_id"] for r in load_csv("analysis_runs.csv")}, load_csv, port_override=bad_p4_epi, mode=mode)
    assert any("Cannot DROP an UNPROVEN_UNTESTED" in e for e in errs_p4_epi), "Phase 4 self-test failed to block UNPROVEN DROP!"
    assert re.search(r"\((EALS-\d{3}(?:\.\d+)?)\s*/\s*\1\)", "bad (EALS-053 / EALS-053) token"), "Self-test duplicate EALS regex failed!"


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify ExploreALS v1.4 registries, 64-char SHA-256 anchors, & gates.")
    ap.add_argument("--mode", choices=("auto", "full", "cached"), default="auto")
    args = ap.parse_args()
    eff_mode = resolve_mode(args.mode)
    errs = verify_all(mode=eff_mode)
    if errs:
        print("VERIFICATION FAILED:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    run_selftest(mode=eff_mode)
    n_ds = len(load_csv("datasets_manifest.csv"))
    n_reg = len(list(REG_DIR.glob("*.csv")))
    stat_all = load_csv("statistical_models_and_contrasts.csv")
    n_stat = len(stat_all)
    n_uniq_anc = len({(r["anchor_relpath"], r["sha64"]) for r in stat_all})
    n_matched_local = sum(
        1 for r in stat_all if sha256_anchor(CARBON_ROOT / r["anchor_relpath"], r["sha64"]) == (True, r["sha64"])
    )
    print(
        f"PASS [{eff_mode}]: All {n_reg} registries, {n_stat}/{n_stat} recorded 64-char SHA-256 contrast digests "
        f"({n_uniq_anc} unique anchors; {n_matched_local}/{n_stat} locally byte/EOL-matched in {eff_mode} mode), "
        f"{n_ds} dataset manifest entries, 53-hypothesis/28-interval portfolio, "
        "ExploreALS v1.4 Explorer + 8 Monographs, biosecurity/provenance gates, and self-tests verified (0 errors)."
    )


if __name__ == "__main__":
    main()
