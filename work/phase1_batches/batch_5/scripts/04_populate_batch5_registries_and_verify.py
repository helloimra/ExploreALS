"""RUN-B5-004: Write Batch 5 registries and run strict Epistemic Asymmetry & FK verification."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import verify_carbon_als as verifier  # noqa: E402
from work.phase1_batches.batch_5.scripts.batch5_registry_records import (  # noqa: E402
    ANALYSIS_RUNS,
    CANDIDATE_DECISIONS,
    EVIDENCE_ROWS,
)

BATCH_DIR = ROOT / "work" / "phase1_batches" / "batch_5"
OUT_DIR = BATCH_DIR / "outputs"

RUN_FIELDS = [
    "analysis_run_id", "phase_batch", "script_relpath", "output_artifacts",
    "datasets_used", "tools_and_skills_used", "reproduced_verified", "run_timestamp_utc", "summary",
]
EVIDENCE_FIELDS = [
    "evidence_id", "carbon_id", "subnode_id", "analysis_run_id", "source_type",
    "source_id_or_locator", "cohort_and_stratum", "assay_and_contrast", "effect_direction",
    "effect_estimate", "p_value", "fdr_or_adjusted_p", "sample_size_n", "epistemic_weight", "notes",
]
DECISION_FIELDS = [
    "carbon_id", "name", "track", "phase1_batch", "reanalysis_state",
    "scientific_taste_rating", "technical_accuracy_of_explore_claim",
    "causal_vs_reactive_assessment", "prior_art_crowding_level",
    "evidence_proves_hypothesis", "evidence_disproves_hypothesis",
    "epistemic_state", "decision", "factual_justification",
    "discriminating_next_test", "supporting_evidence_ids", "updated_at",
]


def write_csv_strict(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="raise")
        w.writeheader()
        for r in rows:
            if set(r.keys()) != set(fieldnames):
                raise ValueError(f"Key mismatch in {path.name}: {set(r.keys()) ^ set(fieldnames)}")
            w.writerow(r)


def verify_batch5() -> dict[str, object]:
    errors: list[str] = []
    intake_ids = {r["carbon_id"] for r in verifier.load_csv("candidate_intake_ledger.csv")}
    batch5_expected = {"C003", "C004", "C005", "C008", "C010", "C011", "C012"}
    dec_map = {d["carbon_id"]: d for d in CANDIDATE_DECISIONS}
    if set(dec_map.keys()) != batch5_expected:
        errors.append(f"Batch 5 candidate mismatch: {set(dec_map.keys())} != {batch5_expected}")

    run_ids = {r["analysis_run_id"] for r in ANALYSIS_RUNS}
    ev_ids = {e["evidence_id"] for e in EVIDENCE_ROWS}
    if len(ev_ids) != len(EVIDENCE_ROWS):
        errors.append("Duplicate evidence_id in Batch 5 evidence_ledger.csv")

    for r in ANALYSIS_RUNS:
        sp = ROOT / r["script_relpath"]
        if not sp.exists():
            errors.append(f"Missing script for {r['analysis_run_id']}: {r['script_relpath']}")
        for art in filter(None, r["output_artifacts"].split(";")):
            if not art.endswith("batch5_verification_report.json") and not (ROOT / art).exists():
                errors.append(f"Missing output artifact: {art}")

    for e in EVIDENCE_ROWS:
        if e["carbon_id"] not in batch5_expected or e["carbon_id"] not in intake_ids:
            errors.append(f"Invalid carbon_id on {e['evidence_id']}: {e['carbon_id']}")
        if e["analysis_run_id"] not in run_ids:
            errors.append(f"Unknown analysis_run_id on {e['evidence_id']}: {e['analysis_run_id']}")

    # Merge into root decisions in memory (with dummy evidence_ledger check resolved locally)
    base_decisions = verifier.load_csv("candidate_decisions.csv")
    merged_For_Enum: list[dict[str, str]] = []
    for row in base_decisions:
        if row["carbon_id"] in dec_map:
            d = dict(dec_map[row["carbon_id"]])
            for evid in filter(None, d["supporting_evidence_ids"].split(";")):
                if evid not in ev_ids:
                    errors.append(f"{d['carbon_id']} missing batch5 evidence {evid}")
            d_copy = dict(d)
            d_copy["supporting_evidence_ids"] = "" if d["decision"] != "DROP" else d["supporting_evidence_ids"]
            merged_For_Enum.append(d)
        else:
            merged_For_Enum.append(row)

    # Filter out ONLY the expected root-evidence_ledger missing error since root registries/*.csv are untouched in Phase 1 batches
    raw_errs = verifier.verify_all(decisions_override=merged_For_Enum)
    for err in raw_errs:
        if "missing from evidence_ledger.csv" in err and any(ev in err for ev in ev_ids):
            continue
        errors.append(err)

    return {
        "n_analysis_runs": len(ANALYSIS_RUNS),
        "n_evidence_rows": len(EVIDENCE_ROWS),
        "n_candidate_decisions": len(CANDIDATE_DECISIONS),
        "decisions_summary": {d["carbon_id"]: {"epistemic_state": d["epistemic_state"], "decision": d["decision"]} for d in CANDIDATE_DECISIONS},
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }


if __name__ == "__main__":
    write_csv_strict(BATCH_DIR / "analysis_runs.csv", RUN_FIELDS, ANALYSIS_RUNS)
    write_csv_strict(BATCH_DIR / "evidence_ledger.csv", EVIDENCE_FIELDS, EVIDENCE_ROWS)
    write_csv_strict(BATCH_DIR / "candidate_decisions.csv", DECISION_FIELDS, CANDIDATE_DECISIONS)
    report = verify_batch5()
    (OUT_DIR / "batch5_verification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if report["errors"]:
        print("FAILED:", report["errors"], file=sys.stderr)
        sys.exit(1)
    print(f"PASS: Batch 5 registries written & verified ({report['n_analysis_runs']} runs, {report['n_evidence_rows']} evidence rows, 0 errors).")
