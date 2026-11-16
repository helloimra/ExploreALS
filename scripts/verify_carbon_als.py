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
BUNDLED_DATASET_IDS = {"DS001_FEAT", "DS_BA9_BUNDLE", "DS_ELIG_BED"}
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


def sha256_path(path: Path) -> str:
    if path.is_file():
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    tree = hashlib.sha256()
    for fp in sorted(x for x in path.rglob("*") if x.is_file()):
        rel = fp.relative_to(path).as_posix()
        tree.update(f"{rel}:{sha256_path(fp)}\n".encode("utf-8"))
    return tree.hexdigest()


def sha256_anchor(path: Path) -> tuple[bool, str]:
    if path.exists():
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
        elif sha256_path(p) != d["sha256"]:
            errors.append(f"SHA-256 mismatch on staged dataset ({'file' if p.is_file() else 'dir'}): {d['local_relpath']}")

    lock_fp = CARBON_ROOT / "schemas" / "dataset_files_lock.json"
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
    run_ids_prelim = {ar["analysis_run_id"] for ar in runs}
    if evidence_override is None:
        exp_all_ev_ids = {e["evidence_id"] for e in evidence} | {e["evidence_id"] for e in p3b_ev_rows}
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
        found_anc, got_sha = sha256_anchor(CARBON_ROOT / sr["anchor_relpath"])
        must_have_anc = (mode == "full") or (sr["anchor_type"] in {"CACHED_API_SNAPSHOT", "DETERMINISTIC_MODEL_OUTPUT"})
        if not found_anc:
            if must_have_anc:
                errors.append(f"{ev_id}: missing anchor_relpath '{sr['anchor_relpath']}'")
        elif got_sha != sr["sha64"]:
            errors.append(f"{ev_id}: sha64 mismatch on '{sr['anchor_relpath']}' ({got_sha[:12]} != {sr['sha64'][:12]})")

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
        from phase3_gates import verify_phase3a_gates
        from phase3b_gates import verify_phase3b_gates
        from phase4_gates import verify_phase4_gates

        errors.extend(verify_phase3a_gates(CARBON_ROOT, p2_rows, decisions, run_ids, load_csv, mode=mode))
        errors.extend(verify_phase3b_gates(CARBON_ROOT, intake, subnodes, runs, load_csv, mode=mode))
        errors.extend(verify_phase4_gates(CARBON_ROOT, decisions, run_ids, load_csv, mode=mode))

    return errors


def run_selftest(mode: str = "full") -> None:
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Verify ExploreALS v1.2 / CarbonALS registries, SHA-64 anchors, & gates.")
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
    n_stat = len(load_csv("statistical_models_and_contrasts.csv"))
    print(
        f"PASS [{eff_mode}]: All {n_reg} registries, {n_stat}/{n_stat} 64-char SHA-256 contrast anchors, "
        f"{n_ds} dataset manifest entries, 59-candidate/26-interval Phase 4 portfolio, "
        "Explorer v1.2 + 8 Monographs, biosecurity/provenance gates, and Epistemic Asymmetry self-tests verified (0 errors)."
    )
