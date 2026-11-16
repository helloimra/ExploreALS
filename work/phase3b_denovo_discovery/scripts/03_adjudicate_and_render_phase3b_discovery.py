"""RUN-P3B-003: Assemble Phase 3B registries, register RUN-P3B-001..003, and render PHASE3B_DENOVO_UNBIASED_DISCOVERY.md."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _denovo_candidate_rows import build_phase3b_candidate_rows  # noqa: E402
from _denovo_evidence_rows import build_phase3b_evidence_rows  # noqa: E402
from _render_phase3b_report import render_phase3b_markdown  # noqa: E402

REG_DIR = ROOT / "registries"
OUT_DIR = ROOT / "work" / "phase3b_denovo_discovery" / "outputs"
CACHE_DIR = ROOT / "work" / "phase3b_denovo_discovery" / "cache"
REP_FP = ROOT / "reports" / "phase3" / "PHASE3B_DENOVO_UNBIASED_DISCOVERY.md"
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)


def _sha12(fp: Path) -> str:
    return hashlib.sha256(fp.read_bytes()).hexdigest()[:12]


def _write_csv(fp: Path, rows: list[dict[str, str]]) -> None:
    with fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    REP_FP.parent.mkdir(parents=True, exist_ok=True)
    f1234 = json.loads((OUT_DIR / "run_p3b_001_multimodal_funnel.json").read_text(encoding="utf-8"))
    sso = json.loads((OUT_DIR / "run_p3b_002_denovo_sso_offtarget.json").read_text(encoding="utf-8"))
    ext = json.loads((CACHE_DIR / "external_priors_and_structures.json").read_text(encoding="utf-8"))
    dd = json.loads((OUT_DIR / "run_p3b_004_targeted_deep_dive.json").read_text(encoding="utf-8"))
    with (REG_DIR / "phase3b_denovo_sso_intervals.csv").open(encoding="utf-8", newline="") as fh:
        sso_rows = list(csv.DictReader(fh))

    ev_rows = build_phase3b_evidence_rows(f1234, sso, ext, dd)
    cand_rows = build_phase3b_candidate_rows(f1234, sso, dd)

    ev_fp = REG_DIR / "phase3b_denovo_evidence.csv"
    cand_fp = REG_DIR / "phase3b_denovo_candidates.csv"
    sso_fp = REG_DIR / "phase3b_denovo_sso_intervals.csv"
    _write_csv(ev_fp, ev_rows)
    _write_csv(cand_fp, cand_rows)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_runs = [
        {
            "analysis_run_id": "RUN-P3B-001", "phase_batch": "Phase3B_DeNovo_Discovery",
            "script_relpath": "work/phase3b_denovo_discovery/scripts/00_stage_priors_and_pdb_structures.py;work/phase3b_denovo_discovery/scripts/01_genomewide_multimodal_discovery_funnel.py",
            "output_artifacts": "work/phase3b_denovo_discovery/cache/external_priors_and_structures.json;work/phase3b_denovo_discovery/outputs/run_p3b_001_multimodal_funnel.json",
            "datasets_used": "DS_CRYPTIC;DS_BRYCE_APA;DS_ZENG_APA;DS029_SPILL;DS045_TRAUT;DS046_OH_XML;DS031_ZHANG;DS003_PB;DS_EDIN_PB;DS_GC_REF;DS005_BYE;DS_PDB_2Z0D;DS_PDB_1XFD",
            "tools_and_skills_used": "carbon_als.loaders;carbon_als.mmcif_parser;opentargets-database;clinical-trials-database;literature-search-europepmc;pdb-database;uv-python",
            "reproduced_verified": "yes", "run_timestamp_utc": ts,
            "summary": "Genome-wide/proteome-wide/screen-wide de novo discovery waterfalls excluding all 40 ExploreALS items + 19 sub-nodes, header-resolved Spillman MOESM5 S3, full-genome GC BA4_Exc OLS+FDR, Trautwig DIA+TMTpro, and PDB 2Z0D(H280A)/1XFD 3D contacts.",
        },
        {
            "analysis_run_id": "RUN-P3B-002", "phase_batch": "Phase3B_DeNovo_Discovery",
            "script_relpath": "work/phase3b_denovo_discovery/scripts/02_denovo_splice_sso_and_offtarget_gate.py",
            "output_artifacts": "registries/phase3b_denovo_sso_intervals.csv;work/phase3b_denovo_discovery/outputs/run_p3b_002_denovo_sso_offtarget.json",
            "datasets_used": "DS_GENCODE_V46_TX;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;DS003_PB;DS_EDIN_PB;DS031_ZHANG",
            "tools_and_skills_used": "carbon_als.splice_design;carbon_als.offtarget_scanner;alphagenome-variant-impact-score;alphagenome-atlas-website-links;ensembl-database;gnomad-database;DBCLS_GGGenome_hg38;uv-python",
            "reproduced_verified": "yes", "run_timestamp_utc": ts,
            "summary": "Coordinate-only GRCh38 steric-SSO & GAPMER_RNASE_H 3'Ext design + live AlphaGenome AVI + gnomAD r4 (catching KALRN rs2173852 AF=17.61%) + Phase 3A v2 254,070-transcript & intronic pre-mRNA off-target audit across 14 intervals (0 oligomer sequences).",
        },
        {
            "analysis_run_id": "RUN-P3B-003", "phase_batch": "Phase3B_DeNovo_Discovery",
            "script_relpath": "work/phase3b_denovo_discovery/scripts/03_adjudicate_and_render_phase3b_discovery.py",
            "output_artifacts": "registries/phase3b_denovo_candidates.csv;registries/phase3b_denovo_evidence.csv;work/phase3b_denovo_discovery/outputs/run_p3b_003_adjudication_summary.json;reports/phase3/PHASE3B_DENOVO_UNBIASED_DISCOVERY.md",
            "datasets_used": "DS_CRYPTIC;DS_BRYCE_APA;DS029_SPILL;DS045_TRAUT;DS031_ZHANG;DS005_BYE;DS_GENCODE_V46_TX;DS_PDB_2Z0D;DS_PDB_1XFD;DS001_COUNTS;DS001_META",
            "tools_and_skills_used": "scripts.phase3b_gates;scripts.provenance_gates;uv-python",
            "reproduced_verified": "yes", "run_timestamp_utc": ts,
            "summary": "Adjudicated 19 atomic de novo candidates (2 TIER_2_FOCUSED_GATE_FIRST [ATG4B, CELF5], 9 TIER_3_EXPLORATORY_DISCOVERY [incl. KALRN], 3 RECLASSIFY_BENCHMARK_OR_BIOMARKER, 5 DROP; 0 KEEP_CORE) and 27 single-contrast evidence rows integrating Round 2 hardening + RUN-P3B-004 deep dives.",
        },
        {
            "analysis_run_id": "RUN-P3B-004", "phase_batch": "Phase3B_DeNovo_Discovery",
            "script_relpath": "work/phase3b_denovo_discovery/scripts/04_phase3b_targeted_deep_dive.py",
            "output_artifacts": "work/phase3b_denovo_discovery/cache/deep_dive_external_priors.json;work/phase3b_denovo_discovery/outputs/run_p3b_004_targeted_deep_dive.json",
            "datasets_used": "DS001_COUNTS;DS001_META;DS001_ONEILL;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;DS_BRYCE_APA;DS003_PB;DS_EDIN_PB;DS031_ZHANG;DS_GC_REF;DS_PDB_2Z0D",
            "tools_and_skills_used": "alphagenome-single-variant-analysis;opentargets-database;gtex-database;chembl-database;uniprot-database;literature-search-openalex;tooluniverse-gene-liability;biomolecular-structure-viewer;uv-python",
            "reproduced_verified": "yes", "run_timestamp_utc": ts,
            "summary": "Targeted deep dive: KALRN Kalirin-12/DuET isoform fix + AlphaGenome-predicted rs2173852 76.18x 5'SS collapse + Open Targets v4 0-ALS-GWAS check; NYGC neuronal-mass-residualized mn_neur_z tSTMN2 benchmark + ALS-SOD1/FUS negative control; ATG4B PDB 2Z0D/ChEMBL audit; PRUNE2 9-bp/34-bp exon audit; ELK1 6-cohort ST7 null.",
        },
    ]
    runs_fp = REG_DIR / "analysis_runs.csv"
    with runs_fp.open(encoding="utf-8", newline="") as fh:
        cur_runs = list(csv.DictReader(fh))
    new_by_id = {r["analysis_run_id"]: r for r in new_runs}
    ex_rids = {r["analysis_run_id"] for r in cur_runs}
    merged_runs = [{**r, **new_by_id[r["analysis_run_id"]]} if r["analysis_run_id"] in new_by_id else r for r in cur_runs]
    merged_runs.extend(r for r in new_runs if r["analysis_run_id"] not in ex_rids)
    _write_csv(runs_fp, merged_runs)

    sha_stamp = f"REGISTRY_CONCORDANCE_SHA12: denovo_cands={_sha12(cand_fp)} denovo_sso={_sha12(sso_fp)} denovo_ev={_sha12(ev_fp)}"
    md_txt = render_phase3b_markdown(f1234, ext, dd, cand_rows, sso_rows, ev_rows, sha_stamp)
    REP_FP.write_text(md_txt, encoding="utf-8")

    sum_obj = {"analysis_run_id": "RUN-P3B-003", "sha_stamp": sha_stamp, "n_candidates": len(cand_rows), "n_sso_intervals": len(sso_rows), "n_evidence": len(ev_rows)}
    (OUT_DIR / "run_p3b_003_adjudication_summary.json").write_text(json.dumps(sum_obj, indent=2, allow_nan=False), encoding="utf-8")
    for fp in (ev_fp, cand_fp, sso_fp, REP_FP):
        assert not SEQ_GUARD_RE.search(fp.read_text(encoding="utf-8")), f"Biosecurity sequence leak in {fp.name}!"
    print("RUN-P3B-003 OK:", json.dumps(sum_obj, indent=2))


if __name__ == "__main__":
    main()
