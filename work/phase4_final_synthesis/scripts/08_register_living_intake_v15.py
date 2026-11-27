"""Idempotently register ExploreALS v1.5.0 EALS-054 (L02, NADSYN1) & EALS-055 (L03, CYFIP2) datasets, citations, and living-intake CSVs."""
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

from _living_intake_v15_evidence_specs import LIVING_V15_EVIDENCE_ROWS  # noqa: E402
from _living_intake_v15_specs import LIVING_CANDIDATE_L02, LIVING_CANDIDATE_L03, VERIFIED_CITATIONS_V15  # noqa: E402
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


def _read_csv(fp: Path) -> tuple[list[str], list[dict[str, str]]]:
    with fp.open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or []), list(rd)


def _write_csv(fp: Path, cols: list[str], rows: list[dict[str, str]]) -> None:
    with fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    # 1. Update schemas/verified_citations_lock.json
    cite_fp = SCHEMA_DIR / "verified_citations_lock.json"
    cite_obj = json.loads(cite_fp.read_text(encoding="utf-8"))
    cite_obj["schema_version"] = "1.5.0"
    for bucket, entries in VERIFIED_CITATIONS_V15.items():
        cite_obj.setdefault(bucket, {}).update(entries)
    cite_fp.write_text(json.dumps(cite_obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 2. Register DS_PDB_NADSYN1_CYFIP2 in datasets_manifest.csv & schemas/dataset_files_lock.json
    ds_fp = REG_DIR / "datasets_manifest.csv"
    ds_cols, ds_rows = _read_csv(ds_fp)
    ds_rows = [r for r in ds_rows if r["dataset_id"] != "DS_PDB_NADSYN1_CYFIP2"]
    lock_fp = SCHEMA_DIR / "dataset_files_lock.json"
    lock_obj = json.loads(lock_fp.read_text(encoding="utf-8"))
    pdb_dir = ROOT / "data" / "pharmacology_structures" / "phase5_pdb"
    if pdb_dir.is_dir() and any(pdb_dir.glob("*.cif")):
        files_meta = [
            {"rel": fp.name, "size_bytes": fp.stat().st_size, "sha256": sha256_path(fp)}
            for fp in sorted(pdb_dir.glob("*.cif"))
        ]
        tot_sz = sum(x["size_bytes"] for x in files_meta)
        dir_sha = sha256_path(pdb_dir)
        lock_obj["DS_PDB_NADSYN1_CYFIP2"] = {
            "local_relpath": "data/pharmacology_structures/phase5_pdb",
            "is_dir": True,
            "tier": "TIER_A_OPEN_REDISTRIBUTABLE",
            "sha256": dir_sha,
            "files": files_meta,
        }
    else:
        ex_lock = lock_obj["DS_PDB_NADSYN1_CYFIP2"]
        dir_sha = ex_lock["sha256"]
        tot_sz = sum(int(x["size_bytes"]) for x in ex_lock["files"])
    ds_rows.append({
        "dataset_id": "DS_PDB_NADSYN1_CYFIP2",
        "domain": "pharmacology_structures",
        "local_relpath": "data/pharmacology_structures/phase5_pdb",
        "upstream_explore_relpath": "NONE_PHASE4_LIVING_PRIMARY",
        "accession_or_doi": "RCSB_PDB:6OFB;3P8C;AlphaFold_DB:AF-Q6IA69-F1;AF-Q96F07-F1;PMID:31911602;PMID:21107423",
        "license_or_access": "CC0 1.0 / CC BY 4.0",
        "size_bytes": str(tot_sz),
        "sha256": dir_sha,
        "relevant_candidates": "L02;L03",
        "description": "Experimental X-ray and AlphaFold v6 .cif structures for human NADSYN1 octamer + NaAD/AMP/POP (PDB 6OFB, 2.84A; AF-Q6IA69-F1, 706 aa) and human CYFIP2 (AF-Q96F07-F1, 1,278 aa) vs paralog CYFIP1 WAVE regulatory complex (PDB 3P8C, 2.29A)",
        "redistribution_tier": "TIER_A_OPEN_REDISTRIBUTABLE",
        "canonical_fetch_url_or_instructions": "https://files.rcsb.org/download/{6OFB,3P8C}.cif ; https://alphafold.ebi.ac.uk/files/{AF-Q6IA69-F1,AF-Q96F07-F1}-model_v6.cif",
    })
    _write_csv(ds_fp, ds_cols, ds_rows)
    lock_fp.write_text(json.dumps(lock_obj, indent=2) + "\n", encoding="utf-8")

    # 3. Idempotently upsert L02 & L03 into living_evidence_candidates.csv (preserving L01)
    _, cur_cands = _read_csv(REG_DIR / "living_evidence_candidates.csv")
    kept_cands = [r for r in cur_cands if r["living_id"] not in {"L02", "L03"}]
    new_cands = [{k: deaudit_prose(v) for k, v in row.items()} for row in (LIVING_CANDIDATE_L02, LIVING_CANDIDATE_L03)]
    _write_csv(REG_DIR / "living_evidence_candidates.csv", LIVING_CAND_COLS, [*kept_cands, *new_cands])

    # 4. Idempotently upsert EV-LIV-003..006 into living_evidence_candidate_evidence.csv (preserving EV-LIV-001..002)
    _, cur_evs = _read_csv(REG_DIR / "living_evidence_candidate_evidence.csv")
    new_eids = {r["evidence_id"] for r in LIVING_V15_EVIDENCE_ROWS}
    kept_evs = [r for r in cur_evs if r["evidence_id"] not in new_eids]
    new_evs = [{k: deaudit_prose(v) for k, v in r.items()} for r in LIVING_V15_EVIDENCE_ROWS]
    _write_csv(REG_DIR / "living_evidence_candidate_evidence.csv", LIVING_EV_COLS, [*kept_evs, *new_evs])
    print(f"RUN-P4-006 v1.5 living intake registered: {len(ds_rows)} datasets, {len(kept_cands) + len(new_cands)} living candidates, {len(kept_evs) + len(new_evs)} living evidence rows.")


if __name__ == "__main__":
    main()
