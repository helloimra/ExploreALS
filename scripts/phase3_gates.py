"""Hardened deterministic Phase 3A validators: unconditional existence, bidirectional off-target rules, TRL/scientific-gate separation, strict RFC-8259 JSON & case-insensitive zero-sequence biosecurity."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import re

ALLOWED_OFFTARGET_STATUS = {
    "PASS_CLEAN_GE2MM",
    "CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED",
    "WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL",
    "FAIL_EXACT_0MM_OFFTARGET",
}
ALLOWED_ACTIONABILITY_TIERS = {
    "TIER_1_ACTIONABLE_NOW",
    "TIER_2_FOCUSED_GATE_FIRST",
    "TIER_3_EXPLORATORY_DISCOVERY",
    "COMPANION_PROTOCOL_ONLY",
}
ALLOWED_TRL = {
    "TRL_6_PH2B_SUBGROUP_BIOLOGIC",
    "TRL_5_HUMAN_ALS_PK_PD_PROVEN",
    "TRL_4_ACTIVE_PH1_CLASS_OR_NCE",
    "TRL_3_PRECLINICAL_SSO_COORDINATE",
    "TRL_2_PRECLINICAL_MODALITY_DISCOVERY",
    "TRL_1_TARGET_TOOL_PROBE_WATCHLIST",
    "PROTOCOL_COMPANION_NA",
}
ALLOWED_GATE_CLASS = {
    "TARGETED_PRECLINICAL_VALIDATION_GATE",
    "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
    "BIOMARKER_ENRICHED_PHASE3_EFFICACY_TRIAL",
    "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
    "CLINICAL_PROTOCOL_STANDARDIZATION",
}
ALLOWED_EVIDENCE_BASIS = {
    "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY",
    "MEASURED_HUMAN_TDP43_PATHOLOGY_AND_RESCUE",
    "MEASURED_HUMAN_RCT_SUBGROUP",
    "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
    "MEASURED_HUMAN_PK_AND_SAFETY",
    "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
    "MEASURED_C9FTD_FRACTION_PROTEOMICS",
    "PROTOCOL_STAGE_GATING_ONLY",
}
MODEL_PRIOR_RE = re.compile(r"^(NONE|COARSE_PRIOR_ONLY:[A-Za-z0-9_.,+-]+)$")
RAW_OLIGO_SEQ_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)


def _sha12(fp: Path) -> str:
    return hashlib.sha256(fp.read_bytes()).hexdigest()[:12]


def _sha12_variants(fp: Path) -> set[str]:
    raw = fp.read_bytes()
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    return {hashlib.sha256(b).hexdigest()[:12] for b in (raw, lf, crlf)}


def _reject_nan_const(val: str) -> None:
    raise ValueError(f"Non-RFC-8259 constant '{val}' detected")


def _read_text_or_gz(fp: Path) -> str:
    if fp.suffix == ".gz":
        return gzip.decompress(fp.read_bytes()).decode("utf-8")
    return fp.read_text(encoding="utf-8")


def verify_phase3a_gates(
    carbon_root: Path,
    p2_rows: list[dict[str, str]],
    decisions: list[dict[str, str]],
    run_ids: set[str],
    load_csv_fn,
    mode: str = "full",
) -> list[str]:
    errors: list[str] = []
    reg_dir = carbon_root / "registries"
    ot_fp = reg_dir / "phase3_sso_offtarget_audit.csv"
    rd_fp = reg_dir / "phase3_execution_readiness.csv"
    rep_fp = carbon_root / "reports" / "phase3" / "PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md"

    req_fps = (ot_fp, rd_fp, rep_fp) if mode == "full" else (ot_fp, rd_fp)
    for req_fp in req_fps:
        if not req_fp.is_file():
            errors.append(f"Missing mandatory Phase 3A artifact: {req_fp.relative_to(carbon_root).as_posix()}")
    if errors:
        return errors

    ot_rows = load_csv_fn("phase3_sso_offtarget_audit.csv")
    if {r["interval_id"] for r in ot_rows} != {r["interval_id"] for r in p2_rows} or len(ot_rows) != len(p2_rows):
        errors.append("phase3_sso_offtarget_audit.csv interval_id set does not match phase2_multiplex_intervals.csv 1-to-1")
    for r in ot_rows:
        st = r["offtarget_safety_status"]
        if st not in ALLOWED_OFFTARGET_STATUS:
            errors.append(f"Invalid offtarget_safety_status '{st}' on {r['interval_id']}")
        if int(r["spliced_0mm_genes"]) > 0 and st != "FAIL_EXACT_0MM_OFFTARGET":
            errors.append(f"Bidirectional status violation on {r['interval_id']}: spliced_0mm_genes={r['spliced_0mm_genes']} requires FAIL_EXACT_0MM_OFFTARGET")
        if int(r["gggenome_max_mm_queried"]) < 2 and r["premRNA_2mm_splice25bp_pc_genes"] != "NA":
            errors.append(f"{r['interval_id']}: gggenome_max_mm_queried={r['gggenome_max_mm_queried']} < 2 must record premRNA_2mm_splice25bp_pc_genes='NA' (got '{r['premRNA_2mm_splice25bp_pc_genes']}')")
        if int(r["gggenome_max_mm_queried"]) >= 2 and r["premRNA_2mm_splice25bp_pc_genes"] == "NA":
            errors.append(f"{r['interval_id']}: gggenome_max_mm_queried>=2 cannot leave premRNA_2mm_splice25bp_pc_genes='NA'")
        if st == "PASS_CLEAN_GE2MM":
            for zcol in (
                "spliced_0mm_genes", "spliced_1mm_genes", "spliced_wobble_only_pc_genes",
                "premRNA_0mm_sense_genes", "premRNA_1mm_splice50bp_genes",
                "premRNA_wobble_only_splice50bp_pc_genes", "premRNA_2mm_splice25bp_pc_genes",
                "bulge_1nt_steric_pc_genes", "sub18_core_steric_pc_genes",
            ):
                if r[zcol] == "NA" or int(r[zcol]) != 0:
                    errors.append(f"PASS_CLEAN_GE2MM violation on {r['interval_id']}: {zcol}={r[zcol]} != 0")
        if r["analysis_run_id"] not in run_ids:
            errors.append(f"Off-target row {r['interval_id']} references unknown run {r['analysis_run_id']}")

    rd_rows = load_csv_fn("phase3_execution_readiness.csv")
    surviving_ids = {d["carbon_id"] for d in decisions if d["decision"] in {"KEEP_CORE", "KEEP_EXPLORATORY_UNPROVEN"}}
    if {r["candidate_id"] for r in rd_rows} != surviving_ids or len(rd_rows) != len(surviving_ids):
        errors.append("phase3_execution_readiness.csv candidate_id set does not match surviving KEEP_CORE + KEEP_EXPLORATORY_UNPROVEN 1-to-1")
    dec_map = {d["carbon_id"]: d for d in decisions}
    if sorted(int(r["priority_rank_overall"]) for r in rd_rows) != list(range(1, len(rd_rows) + 1)):
        errors.append(f"phase3_execution_readiness.csv priority_rank_overall must be contiguous 1..{len(rd_rows)}")
    for r in rd_rows:
        cid = r["candidate_id"]
        if cid in dec_map and (r["phase2_decision_tier"] != dec_map[cid]["decision"] or r["epistemic_state"] != dec_map[cid]["epistemic_state"]):
            errors.append(f"{cid}: phase3_execution_readiness.csv out of sync with candidate_decisions.csv")
        if not r["primary_modality_specific"].strip():
            errors.append(f"{cid}: missing primary_modality_specific")
        if r["clinical_readiness_trl"] not in ALLOWED_TRL:
            errors.append(f"{cid}: invalid clinical_readiness_trl '{r['clinical_readiness_trl']}'")
        if r["next_gate_experimental_class"] not in ALLOWED_GATE_CLASS:
            errors.append(f"{cid}: invalid next_gate_experimental_class '{r['next_gate_experimental_class']}'")
        if r["primary_evidence_basis"] not in ALLOWED_EVIDENCE_BASIS:
            errors.append(f"{cid}: invalid primary_evidence_basis '{r['primary_evidence_basis']}'")
        if not MODEL_PRIOR_RE.match(r["model_prior_dependency"].strip()):
            errors.append(f"{cid}: invalid model_prior_dependency '{r['model_prior_dependency']}'")
        if r["scientific_actionability_tier"] not in ALLOWED_ACTIONABILITY_TIERS:
            errors.append(f"{cid}: invalid scientific_actionability_tier '{r['scientific_actionability_tier']}'")
        if r["analysis_run_id"] not in run_ids:
            errors.append(f"{cid}: phase3_execution_readiness.csv references unknown run {r['analysis_run_id']}")
        h_items = [x for x in r["unsolved_hurdles_structured"].split(";") if x and x != "NONE"]
        if len(h_items) != int(r["unsolved_hurdle_count"]):
            errors.append(f"{cid}: unsolved_hurdle_count={r['unsolved_hurdle_count']} != {len(h_items)} items")
        if r["backup_modality"].strip() != "NONE":
            for sym_col in ("backup_class_warning", "backup_delivery_pk_hurdle", "backup_lost_target"):
                if not r[sym_col].strip():
                    errors.append(f"BACKUP SYMMETRY VIOLATION on {cid}: missing {sym_col}")

    p3a_cache = carbon_root / "work" / "phase3a_execution_safety" / "cache"
    p3a_out = carbon_root / "work" / "phase3a_execution_safety" / "outputs"
    json_paths = [
        *(sorted([*p3a_cache.glob("*.json"), *p3a_cache.glob("*.json.gz")]) if p3a_cache.is_dir() else []),
        *(sorted([*p3a_out.glob("*.json"), *p3a_out.glob("*.json.gz")]) if p3a_out.is_dir() else []),
    ]
    for jfp in json_paths:
        if jfp.is_file():
            try:
                json.loads(_read_text_or_gz(jfp), parse_constant=_reject_nan_const)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"STRICT JSON VIOLATION in {jfp.relative_to(carbon_root).as_posix()}: {exc}")

    p3_rep_dir = carbon_root / "reports" / "phase3"
    scan_paths = [
        ot_fp, rd_fp, reg_dir / "evidence_ledger.csv", reg_dir / "analysis_runs.csv",
        *json_paths,
        *sorted((carbon_root / "work" / "phase3a_execution_safety" / "scripts").glob("*.py")),
        *(sorted(p3_rep_dir.glob("*.md")) if p3_rep_dir.is_dir() else []),
    ]
    for fp in scan_paths:
        if fp.is_file():
            m = RAW_OLIGO_SEQ_RE.search(_read_text_or_gz(fp))
            if m:
                errors.append(f"BIOSECURITY SEQUENCE LEAK in {fp.relative_to(carbon_root).as_posix()}: '{m.group(0)[:20]}'")

    if mode == "full" and rep_fp.is_file():
        expected_stamp = f"REGISTRY_CONCORDANCE_SHA12: offtarget={_sha12(ot_fp)} readiness={_sha12(rd_fp)}"
        if expected_stamp not in rep_fp.read_text(encoding="utf-8"):
            errors.append(f"PHASE3A report stale vs registries (missing {expected_stamp})")

    return errors
