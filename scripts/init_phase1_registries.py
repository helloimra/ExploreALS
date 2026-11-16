"""Initialize all 6 canonical CarbonALS Phase 1 registries from verified ExploreALS baselines."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from phase1_extra_cohorts import BA9_NAMED_10, COMPOSITE_SUBNODES_19, SCREEN_AND_BLIND_SURVIVORS_9
from phase1_specs import CANONICAL_21_SPECS

CARBON_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = CARBON_ROOT / "data" / "explore_als_baseline"
REG_DIR = CARBON_ROOT / "registries"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with (BASE_DIR / "candidates.csv").open(encoding="utf-8") as f:
        exp_cands = list(csv.DictReader(f))
    p10a = json.loads((BASE_DIR / "phase10a_portfolio_triage_summary.json").read_text(encoding="utf-8"))
    tier_map: dict[str, str] = {}
    for item in p10a.get("candidates", p10a.get("portfolio", [])):
        cid = item.get("candidate_id")
        if cid:
            tier_map[cid] = item.get("phase10a_tier", item.get("tier", "Unknown"))

    intake_rows: list[dict[str, str]] = []
    for r in exp_cands:
        cid = r["candidate_id"]
        is_comp, critique, assays, dsets, batch = CANONICAL_21_SPECS[cid]
        epn = f"{r['evidence_score']}/{r['priority_score']}/{r['novelty_score']}"
        status_tag = r["status"].split("]")[0].lstrip("[") if "]" in r["status"] else r["status"][:60]
        intake_rows.append({
            "carbon_id": cid,
            "explore_id": cid,
            "cohort_group": "CANONICAL_21",
            "track": r["track"],
            "candidate_type": r["candidate_type"],
            "name": r["name"],
            "genes_or_drug_ids": r["normalized_id"] or r["name"],
            "explore_tier": tier_map.get(cid, status_tag),
            "explore_status": status_tag,
            "explore_scores_epn": epn,
            "is_composite_axis": is_comp,
            "carbon_taste_critique": critique,
            "planned_reanalysis_assays": assays,
            "staged_dataset_ids": dsets,
            "assigned_batch": batch,
        })

    for cid, eid, trk, ctype, name, gids, est, crit, assays, dsets, batch in BA9_NAMED_10:
        intake_rows.append({
            "carbon_id": cid,
            "explore_id": eid,
            "cohort_group": "HISTORICAL_BA9_NAMED_10",
            "track": trk,
            "candidate_type": ctype,
            "name": name,
            "genes_or_drug_ids": gids,
            "explore_tier": "BA9_Frozen_Naming_Call_Unscored",
            "explore_status": est,
            "explore_scores_epn": "unscored",
            "is_composite_axis": "False",
            "carbon_taste_critique": crit,
            "planned_reanalysis_assays": assays,
            "staged_dataset_ids": dsets,
            "assigned_batch": batch,
        })

    for cid, eid, trk, ctype, name, gids, est, crit, assays, dsets, batch in SCREEN_AND_BLIND_SURVIVORS_9:
        intake_rows.append({
            "carbon_id": cid,
            "explore_id": eid,
            "cohort_group": "SCREEN_AND_BLIND_SURVIVORS_9",
            "track": trk,
            "candidate_type": ctype,
            "name": name,
            "genes_or_drug_ids": gids,
            "explore_tier": "Unadopted_Screen_Or_Blind_Survivor",
            "explore_status": est,
            "explore_scores_epn": "unscored",
            "is_composite_axis": "False",
            "carbon_taste_critique": crit,
            "planned_reanalysis_assays": assays,
            "staged_dataset_ids": dsets,
            "assigned_batch": batch,
        })

    write_csv(REG_DIR / "candidate_intake_ledger.csv", list(intake_rows[0].keys()), intake_rows)

    sub_rows = [{
        "subnode_id": sid,
        "parent_carbon_id": pid,
        "gene_symbol": sym,
        "molecular_role": role,
        "explore_bundled_claim": claim,
        "key_risk_or_taste_question": risk,
        "gnomad_essentiality_check": "PENDING_PHASE1",
        "druggability_check": "PENDING_PHASE1",
        "reanalysis_status": "PENDING_PHASE1_REANALYSIS",
        "subnode_verdict": "PENDING",
    } for sid, pid, sym, role, claim, risk in COMPOSITE_SUBNODES_19]
    write_csv(REG_DIR / "subnode_dissection.csv", list(sub_rows[0].keys()), sub_rows)

    dec_rows = [{
        "carbon_id": r["carbon_id"],
        "name": r["name"],
        "track": r["track"],
        "phase1_batch": r["assigned_batch"],
        "reanalysis_state": "PENDING_PHASE1_REANALYSIS",
        "scientific_taste_rating": "PENDING",
        "technical_accuracy_of_explore_claim": "PENDING",
        "causal_vs_reactive_assessment": "PENDING",
        "prior_art_crowding_level": "PENDING",
        "evidence_proves_hypothesis": "PENDING",
        "evidence_disproves_hypothesis": "PENDING",
        "epistemic_state": "PENDING",
        "decision": "PENDING",
        "factual_justification": "",
        "discriminating_next_test": "",
        "supporting_evidence_ids": "",
        "updated_at": now_iso,
    } for r in intake_rows]
    write_csv(REG_DIR / "candidate_decisions.csv", list(dec_rows[0].keys()), dec_rows)

    write_csv(REG_DIR / "evidence_ledger.csv", [
        "evidence_id", "carbon_id", "subnode_id", "analysis_run_id", "source_type",
        "source_id_or_locator", "cohort_and_stratum", "assay_and_contrast", "effect_direction",
        "effect_estimate", "p_value", "fdr_or_adjusted_p", "sample_size_n", "epistemic_weight", "notes",
    ], [])

    write_csv(REG_DIR / "analysis_runs.csv", [
        "analysis_run_id", "phase_batch", "script_relpath", "output_artifacts",
        "datasets_used", "tools_and_skills_used", "reproduced_verified", "run_timestamp_utc", "summary",
    ], [{
        "analysis_run_id": "CAR-RUN-000",
        "phase_batch": "Phase1_Setup",
        "script_relpath": "scripts/stage_explore_als_data.py;scripts/init_phase1_registries.py",
        "output_artifacts": "data/DATA_PROVENANCE_MANIFEST.json;registries/*.csv",
        "datasets_used": "DS_BASE_REG;DS_BASE_P10A",
        "tools_and_skills_used": "Carbon_Setup_Harness",
        "reproduced_verified": "yes",
        "run_timestamp_utc": now_iso,
        "summary": "Staged 34 open-access ExploreALS dataset bundles (410 files, 380.76 MB) and initialized 40 candidate intake items + 19 composite sub-nodes.",
    }])
    print(f"Initialized {len(intake_rows)} candidates and {len(sub_rows)} composite sub-nodes cleanly!")


if __name__ == "__main__":
    main()
