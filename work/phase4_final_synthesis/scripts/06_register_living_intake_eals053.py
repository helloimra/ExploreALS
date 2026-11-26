"""Idempotently register ExploreALS v1.4.0 EALS-053 (L01, atomic CGAS) datasets, citation lock, and living-intake CSVs."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
REG_DIR = ROOT / "registries"
SCHEMA_DIR = ROOT / "schemas"
SCRIPTS_DIR = ROOT / "scripts"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (SCRIPTS_DIR, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _living_intake_eals053_evidence_specs import LIVING_EVIDENCE_ROWS  # noqa: E402
from _living_intake_eals053_specs import LIVING_CANDIDATE_L01, VERIFIED_CITATIONS_V14  # noqa: E402
from _public_taxonomy import deaudit_prose  # noqa: E402
from verify_carbon_als import sha256_path  # noqa: E402

LIVING_CAND_COLS = [
    "living_id", "origin_subcohort", "gene_or_drug", "candidate_type", "primary_modality_specific",
    "mechanism_summary", "causal_vs_reactive_assessment", "epistemic_state", "decision",
    "clinical_readiness_trl", "next_gate_experimental_class", "primary_evidence_basis",
    "model_prior_dependency", "unsolved_hurdle_count", "unsolved_hurdles_structured",
    "scientific_actionability_tier", "factual_justification", "discriminating_next_test",
    "supporting_living_evidence_ids", "analysis_run_id",
]
LIVING_EV_COLS = [
    "evidence_id", "carbon_id", "subnode_id", "analysis_run_id", "source_type", "source_id_or_locator",
    "cohort_and_stratum", "assay_and_contrast", "effect_direction", "effect_estimate",
    "p_value", "fdr_or_adjusted_p", "sample_size_n", "epistemic_weight", "notes",
]


def _write_csv(fp: Path, cols: list[str], rows: list[dict[str, str]]) -> None:
    with fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    # 1. Update schemas/verified_citations_lock.json
    cite_fp = SCHEMA_DIR / "verified_citations_lock.json"
    cite_obj = json.loads(cite_fp.read_text(encoding="utf-8"))
    cite_obj["schema_version"] = "1.4.0"
    for bucket, entries in VERIFIED_CITATIONS_V14.items():
        cite_obj.setdefault(bucket, {}).update(entries)
    cite_fp.write_text(json.dumps(cite_obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 2. Register DS_PDB_CGAS_STING in datasets_manifest.csv & schemas/dataset_files_lock.json
    ds_fp = REG_DIR / "datasets_manifest.csv"
    with ds_fp.open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        ds_cols = list(rd.fieldnames or [])
        ds_rows = [r for r in rd if r["dataset_id"] != "DS_PDB_CGAS_STING"]
    lock_fp = SCHEMA_DIR / "dataset_files_lock.json"
    lock_obj = json.loads(lock_fp.read_text(encoding="utf-8"))
    pdb_dir = ROOT / "data" / "pharmacology_structures" / "phase4_pdb"
    if pdb_dir.is_dir() and any(pdb_dir.glob("*.cif")):
        files_meta = [
            {"rel": fp.name, "size_bytes": fp.stat().st_size, "sha256": sha256_path(fp)}
            for fp in sorted(pdb_dir.glob("*.cif"))
        ]
        tot_sz = sum(x["size_bytes"] for x in files_meta)
        dir_sha = sha256_path(pdb_dir)
        lock_obj["DS_PDB_CGAS_STING"] = {
            "local_relpath": "data/pharmacology_structures/phase4_pdb",
            "is_dir": True,
            "tier": "TIER_A_OPEN_REDISTRIBUTABLE",
            "sha256": dir_sha,
            "files": files_meta,
        }
    else:
        ex_lock = lock_obj["DS_PDB_CGAS_STING"]
        dir_sha = ex_lock["sha256"]
        tot_sz = sum(int(x["size_bytes"]) for x in ex_lock["files"])
    ds_rows.append({
        "dataset_id": "DS_PDB_CGAS_STING",
        "domain": "pharmacology_structures",
        "local_relpath": "data/pharmacology_structures/phase4_pdb",
        "upstream_explore_relpath": "NONE_PHASE4_LIVING_PRIMARY",
        "accession_or_doi": "RCSB_PDB:6MJW;6LRC;6NT5;4KSY;6MXE;PMID:31113940;PMID:32459092;PMID:30842659;PMID:23747010;PMID:30655953",
        "license_or_access": "CC0 1.0 Public Domain",
        "size_bytes": str(tot_sz),
        "sha256": dir_sha,
        "relevant_candidates": "L01",
        "description": "Experimental X-ray/cryo-EM .cif structures for human CGAS catalytic domain + G150 (6MJW, 2.405A, K427E/K428E construct) and PF-06928215 (6LRC, 1.831A), and comparator human STING1 apo dimer (6NT5, 4.10A), 2'3'-cGAMP-bound LBD (4KSY, 1.881A), and Compound 18 open-cleft antagonist (6MXE, 2.470A)",
        "redistribution_tier": "TIER_A_OPEN_REDISTRIBUTABLE",
        "canonical_fetch_url_or_instructions": "https://files.rcsb.org/download/{6MJW,6LRC,6NT5,4KSY,6MXE}.cif",
    })
    _write_csv(ds_fp, ds_cols, ds_rows)
    lock_fp.write_text(json.dumps(lock_obj, indent=2) + "\n", encoding="utf-8")

    # 3. Write registries/living_evidence_candidates.csv & living_evidence_candidate_evidence.csv
    cand_row = {k: deaudit_prose(v) for k, v in LIVING_CANDIDATE_L01.items()}
    ev_rows = [{k: deaudit_prose(v) for k, v in r.items()} for r in LIVING_EVIDENCE_ROWS]
    _write_csv(REG_DIR / "living_evidence_candidates.csv", LIVING_CAND_COLS, [cand_row])
    _write_csv(REG_DIR / "living_evidence_candidate_evidence.csv", LIVING_EV_COLS, ev_rows)
    print(f"RUN-P4-005 living intake registered: {len(ds_rows)} datasets, 1 living candidate (L01), {len(ev_rows)} evidence rows.")


if __name__ == "__main__":
    main()
