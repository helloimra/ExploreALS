"""RUN-P4-001: Build registries/phase4_unified_portfolio.csv (59), phase4_unified_cis_intervals.csv (26), & summary JSON."""
from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
REG_DIR = ROOT / "registries"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _phase4_helpers import (  # noqa: E402
    EXPLORE_BENCHMARK_SPECS,
    PHASE3A_NEXT_TEST_OVERRIDES,
    PROMOTED_LEADS,
    classify_explore_drop_basis,
    classify_explore_type,
    portfolio_sort_key,
    sha12,
)

SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)
PORTFOLIO_COLS = [
    "unified_rank", "portfolio_id", "origin_phase", "origin_subcohort", "track", "gene_or_drug",
    "candidate_type", "primary_modality_specific", "epistemic_state", "decision", "scientific_actionability_tier",
    "clinical_readiness_trl", "next_gate_experimental_class", "primary_evidence_basis", "model_prior_dependency",
    "unsolved_hurdle_count", "unsolved_hurdles_structured", "lead_cis_interval_id", "lead_offtarget_safety_status",
    "key_quantitative_anchor", "discriminating_next_test", "source_registry_ref", "analysis_run_id",
]
CIS_COLS = [
    "unified_interval_order", "origin_phase", "portfolio_id", "subnode_or_cand_id", "gene_symbol", "program_role",
    "rank_within_gene", "is_promoted_lead", "interval_id", "chrom", "grch38_start", "grch38_end", "strand", "length_bp",
    "cis_mechanism_or_mode", "gc_pct", "tm_phys_pops_c", "dg37_kcal", "cpg_dinucs", "max_self_stem_bp", "ese_motifs",
    "mean_avi_phred", "max_avi_phred", "boundary_dist_bp", "composite_score", "spliced_0mm_genes", "spliced_1mm_genes",
    "spliced_2mm_pc_genes", "spliced_wobble_only_pc_genes", "premRNA_0mm_sense_genes", "premRNA_1mm_sense_genes",
    "premRNA_1mm_splice50bp_genes", "premRNA_wobble_only_splice50bp_pc_genes", "premRNA_2mm_splice25bp_pc_genes",
    "bulge_1nt_steric_pc_genes", "sub18_core_steric_pc_genes", "flagged_constrained_neuronal_hits",
    "offtarget_safety_status", "source_offtarget_run_id", "analysis_run_id",
]


def _read_csv(name: str) -> list[dict[str, str]]:
    with (REG_DIR / name).open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _write_csv(fp: Path, cols: list[str], rows: list[dict[str, str]]) -> None:
    with fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def build_cis_intervals() -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    p2_rows = _read_csv("phase2_multiplex_intervals.csv")
    ot_by_iv = {r["interval_id"]: r for r in _read_csv("phase3_sso_offtarget_audit.csv")}
    p3b_sso = _read_csv("phase3b_denovo_sso_intervals.csv")
    cis_rows: list[dict[str, str]] = []
    lead_by_pid: dict[str, dict[str, str]] = {}

    for p2 in p2_rows:
        iv_id = p2["interval_id"]
        ot = ot_by_iv[iv_id]
        sc_id = p2["candidate_id"]
        pid = sc_id.split("-")[0] if "-" in sc_id else sc_id
        rk = int(p2["rank_within_gene"])
        is_lead = PROMOTED_LEADS.get(pid) == (rk, iv_id)
        row = {
            "unified_interval_order": str(len(cis_rows) + 1), "origin_phase": "PHASE2_3A_MULTIPLEX_12",
            "portfolio_id": pid, "subnode_or_cand_id": sc_id, "gene_symbol": p2["gene_symbol"],
            "program_role": p2["multiplex_tier"], "rank_within_gene": str(rk), "is_promoted_lead": str(is_lead),
            "interval_id": iv_id, "chrom": p2["chrom"], "grch38_start": p2["grch38_start"], "grch38_end": p2["grch38_end"],
            "strand": p2["strand"], "length_bp": p2["length_bp"], "cis_mechanism_or_mode": p2["mode"],
            "gc_pct": p2["gc_pct"], "tm_phys_pops_c": p2["tm_phys_pops_c"], "dg37_kcal": p2["dg37_kcal"],
            "cpg_dinucs": p2["cpg_dinucs"], "max_self_stem_bp": p2["max_self_stem_bp"], "ese_motifs": p2["ese_motifs"],
            "mean_avi_phred": p2["mean_avi_phred"], "max_avi_phred": p2["max_avi_phred"], "boundary_dist_bp": p2["boundary_dist_bp"],
            "composite_score": p2["composite_score"],
            **{k: ot[k] for k in CIS_COLS[25:38]},
            "source_offtarget_run_id": ot["analysis_run_id"], "analysis_run_id": "RUN-P4-001",
        }
        cis_rows.append(row)
        if is_lead:
            lead_by_pid[pid] = row

    for s in p3b_sso:
        pid, iv_id, rk = s["denovo_id"], s["interval_id"], int(s["rank_within_gene"])
        is_lead = PROMOTED_LEADS.get(pid) == (rk, iv_id)
        row = {
            "unified_interval_order": str(len(cis_rows) + 1), "origin_phase": "PHASE3B_DENOVO_14",
            "portfolio_id": pid, "subnode_or_cand_id": pid, "gene_symbol": s["gene_symbol"],
            "program_role": "DENOVO_SINGLE_ENTITY", "rank_within_gene": str(rk), "is_promoted_lead": str(is_lead),
            "interval_id": iv_id, "chrom": s["chrom"], "grch38_start": s["grch38_start"], "grch38_end": s["grch38_end"],
            "strand": s["strand"], "length_bp": s["length_bp"], "cis_mechanism_or_mode": s["cis_mechanism_class"],
            **{k: s[k] for k in CIS_COLS[15:38]},
            "source_offtarget_run_id": s["analysis_run_id"], "analysis_run_id": "RUN-P4-001",
        }
        cis_rows.append(row)
        if is_lead:
            lead_by_pid[pid] = row
    return cis_rows, lead_by_pid


def main() -> None:
    intake = {r["carbon_id"]: r for r in _read_csv("candidate_intake_ledger.csv")}
    decisions = _read_csv("candidate_decisions.csv")
    subnodes = _read_csv("subnode_dissection.csv")
    rd_map = {r["candidate_id"]: r for r in _read_csv("phase3_execution_readiness.csv")}
    p3b_cands = _read_csv("phase3b_denovo_candidates.csv")
    celf5_prof = json.loads((ROOT / "work" / "phase4_final_synthesis" / "cache" / "celf5_target_profile.json").read_text(encoding="utf-8"))

    cis_rows, lead_by_pid = build_cis_intervals()
    p3a_rank_map = {cid: int(r["priority_rank_overall"]) for cid, r in rd_map.items()}
    dn_idx_map = {r["denovo_id"]: idx for idx, r in enumerate(p3b_cands, start=1)}
    rows: list[dict[str, str]] = []

    for d in decisions:
        cid = d["carbon_id"]
        it = intake[cid]
        dec, epi = d["decision"], d["epistemic_state"]
        lead = lead_by_pid.get(cid)
        lead_iv = lead["interval_id"] if lead else "NONE"
        lead_st = lead["offtarget_safety_status"] if lead else "NONE"
        if cid in rd_map:
            rd = rd_map[cid]
            rows.append({
                "unified_rank": "0", "portfolio_id": cid, "origin_phase": "EXPLORE_INHERITED_40",
                "origin_subcohort": it["cohort_group"], "track": d["track"], "gene_or_drug": rd["gene_or_drug"],
                "candidate_type": classify_explore_type(cid, it, dec), "primary_modality_specific": rd["primary_modality_specific"],
                "epistemic_state": epi, "decision": dec, "scientific_actionability_tier": rd["scientific_actionability_tier"],
                "clinical_readiness_trl": rd["clinical_readiness_trl"], "next_gate_experimental_class": rd["next_gate_experimental_class"],
                "primary_evidence_basis": rd["primary_evidence_basis"], "model_prior_dependency": rd["model_prior_dependency"],
                "unsolved_hurdle_count": rd["unsolved_hurdle_count"], "unsolved_hurdles_structured": rd["unsolved_hurdles_structured"],
                "lead_cis_interval_id": lead_iv, "lead_offtarget_safety_status": lead_st,
                "key_quantitative_anchor": f"[MEASURED] {rd['phase3a_safety_or_generalization_gate']}",
                "discriminating_next_test": PHASE3A_NEXT_TEST_OVERRIDES.get(cid, d["discriminating_next_test"]),
                "source_registry_ref": "candidate_decisions.csv;phase3_execution_readiness.csv", "analysis_run_id": "RUN-P4-001",
            })
        elif dec == "RECLASSIFY_BENCHMARK_OR_BIOMARKER":
            ctype, pmod, gclass, ebasis, hcnt, hstr = EXPLORE_BENCHMARK_SPECS[cid]
            nxt = d["discriminating_next_test"].strip() or f"Reference calibration benchmark ({d['name']}); not an active NCE discovery program."
            rows.append({
                "unified_rank": "0", "portfolio_id": cid, "origin_phase": "EXPLORE_INHERITED_40",
                "origin_subcohort": it["cohort_group"], "track": "BIOMARKER" if ctype == "BIOMARKER_CSF" else d["track"],
                "gene_or_drug": d["name"], "candidate_type": ctype, "primary_modality_specific": pmod,
                "epistemic_state": epi, "decision": dec, "scientific_actionability_tier": "BIOMARKER_BENCHMARK_ONLY",
                "clinical_readiness_trl": "PROTOCOL_COMPANION_NA", "next_gate_experimental_class": gclass,
                "primary_evidence_basis": ebasis, "model_prior_dependency": "NONE",
                "unsolved_hurdle_count": str(hcnt), "unsolved_hurdles_structured": hstr,
                "lead_cis_interval_id": "NONE", "lead_offtarget_safety_status": "NONE",
                "key_quantitative_anchor": f"[MEASURED] {d['factual_justification']}", "discriminating_next_test": nxt,
                "source_registry_ref": "candidate_decisions.csv", "analysis_run_id": "RUN-P4-001",
            })
        else:
            pmod, ebasis = classify_explore_drop_basis(cid, it, epi)
            rows.append({
                "unified_rank": "0", "portfolio_id": cid, "origin_phase": "EXPLORE_INHERITED_40",
                "origin_subcohort": it["cohort_group"], "track": d["track"], "gene_or_drug": d["name"],
                "candidate_type": classify_explore_type(cid, it, dec), "primary_modality_specific": pmod,
                "epistemic_state": epi, "decision": dec, "scientific_actionability_tier": "DROPPED_FALSIFIED_EXCLUDED",
                "clinical_readiness_trl": "PROTOCOL_COMPANION_NA", "next_gate_experimental_class": "NOT_APPLICABLE_FALSIFIED",
                "primary_evidence_basis": ebasis, "model_prior_dependency": "NONE",
                "unsolved_hurdle_count": "0", "unsolved_hurdles_structured": "NONE",
                "lead_cis_interval_id": "NONE", "lead_offtarget_safety_status": "NONE",
                "key_quantitative_anchor": f"[MEASURED] {d['factual_justification']}",
                "discriminating_next_test": f"NONE_{epi}", "source_registry_ref": "candidate_decisions.csv",
                "analysis_run_id": "RUN-P4-001",
            })

    for c in p3b_cands:
        did = c["denovo_id"]
        lead = lead_by_pid.get(did)
        trk = "A" if c["candidate_type"] == "DRUG_REPURPOSING" else ("BIOMARKER" if c["candidate_type"] == "BIOMARKER_CSF" else "B")
        anchor, nxt = c["factual_justification"], c["discriminating_next_test"]
        if did == "DN-04":
            ny_c = celf5_prof["celf5_nygc_multiregion"]["Spinal_Cord_Cervical"]
            ny_l = celf5_prof["celf5_nygc_multiregion"]["Spinal_Cord_Lumbar"]
            ny_m = celf5_prof["celf5_nygc_multiregion"]["Cortex_Motor"]
            ce_m = celf5_prof["mane_isoform_and_ce_audit"]
            anchor = (
                f"{c['factual_justification']} Phase 4 NYGC 3-region & safety synthesis (RUN-P4-001/RUN-P3B-004): NYGC cervical RIN+GC "
                f"beta={ny_c['adj_beta_tdp_vs_ctrl']:.4f} (p={ny_c['adj_p_tdp_vs_ctrl']:.4f}; ALS-Ox beta=-0.4186, p=0.0321) vs glial-composition-masked "
                f"lumbar beta=+{ny_l['adj_beta_tdp_vs_ctrl']:.4f} (p={ny_l['adj_p_tdp_vs_ctrl']:.4f}) & motor cortex beta=+{ny_m['adj_beta_tdp_vs_ctrl']:.4f} "
                f"(p={ny_m['adj_p_tdp_vs_ctrl']:.4f}), with non-significant difference vs. small-n TDP-43-negative ALS-SOD1/FUS (n=9, mean={ny_c['mean_als_sod1_fus']:.4f} vs ALS-TDP "
                f"{ny_c['mean_als_tdp']:.4f}, adj_p={ny_c['adj_p_tdp_vs_sod1fus']:.4f}; underpowered to prove equivalence, consistent with end-stage neuronal attrition masking bulk mRNA); "
                "sharpest neuronal-mass-residualized mn_neur_z tSTMN2 neuronal tail in panel (cervical beta=-1.3932, "
                "p=2.02e-8 [1.90% tail]; lumbar beta=-1.1940, p=2.54e-11 [0.14% tail]); CNS-restricted GTEx v8 (BA9=43.06, Cerebellum=60.18, Cervical=1.91 vs "
                "max non-CNS Testis=6.97 TPM), dividing-line DepMap Chronos=-0.1304 (0% <-1.0; unliganded Tbio target with 0 prior clinical drugs), and gnomAD v4.1 pLI=1.00/LOEUF=0.248 "
                f"across {ce_m['upstream_intron_len_bp']}-bp upstream micro-intron (108-bp CE mod3=0 carries in-frame PTC at codon {ce_m['inframe_ptc_codon_indices_1b']})."
            )
            nxt = (
                f"{c['discriminating_next_test']} "
                "(MANE_Select ENST00000292672.7 flanking exons chr19:3278031-3278110(+) / chr19:3281199-3281345(+), pLI=1.00)."
            )
        rows.append({
            "unified_rank": "0", "portfolio_id": did, "origin_phase": "PHASE3B_DENOVO_19",
            "origin_subcohort": c["discovery_funnel"], "track": trk, "gene_or_drug": c["gene_or_drug"],
            "candidate_type": c["candidate_type"], "primary_modality_specific": c["primary_modality_specific"],
            "epistemic_state": c["epistemic_state"], "decision": c["decision"], "scientific_actionability_tier": c["scientific_actionability_tier"],
            "clinical_readiness_trl": c["clinical_readiness_trl"], "next_gate_experimental_class": c["next_gate_experimental_class"],
            "primary_evidence_basis": c["primary_evidence_basis"], "model_prior_dependency": c["model_prior_dependency"],
            "unsolved_hurdle_count": c["unsolved_hurdle_count"], "unsolved_hurdles_structured": c["unsolved_hurdles_structured"],
            "lead_cis_interval_id": lead["interval_id"] if lead else "NONE",
            "lead_offtarget_safety_status": lead["offtarget_safety_status"] if lead else "NONE",
            "key_quantitative_anchor": anchor, "discriminating_next_test": nxt,
            "source_registry_ref": "phase3b_denovo_candidates.csv", "analysis_run_id": "RUN-P4-001",
        })

    rows.sort(key=lambda r: portfolio_sort_key(r, p3a_rank_map, dn_idx_map))
    for rk_i, r in enumerate(rows, start=1):
        r["unified_rank"] = str(rk_i)

    port_fp = REG_DIR / "phase4_unified_portfolio.csv"
    cis_fp = REG_DIR / "phase4_unified_cis_intervals.csv"
    _write_csv(port_fp, PORTFOLIO_COLS, rows)
    _write_csv(cis_fp, CIS_COLS, cis_rows)

    runs_fp = REG_DIR / "analysis_runs.csv"
    runs = _read_csv("analysis_runs.csv")
    run_cols = list(runs[0].keys())
    p4_run = {
        "analysis_run_id": "RUN-P4-001", "phase_batch": "Phase4_Final_Synthesis",
        "script_relpath": "work/phase4_final_synthesis/scripts/00_cache_celf5_profile.py;work/phase4_final_synthesis/scripts/01_build_phase4_unified_portfolio.py",
        "output_artifacts": "registries/phase4_unified_portfolio.csv;registries/phase4_unified_cis_intervals.csv;work/phase4_final_synthesis/outputs/run_p4_001_unified_portfolio.json",
        "datasets_used": "DS001_COUNTS;DS001_META;DS001_ONEILL;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT",
        "tools_and_skills_used": "gtex-database;opentargets-database;gnomad-database;tooluniverse-gene-liability;scripts.phase4_gates;uv-python",
        "reproduced_verified": "yes", "run_timestamp_utc": "2026-11-15T01:05:00Z",
        "summary": "Unified all 59 CarbonALS candidates (40 ExploreALS + 19 Phase 3B de novo), 19 sub-nodes, and 26 coordinate-only GRCh38 cis-regulatory intervals under pure scientific actionability & causal evidence basis with CELF5 NYGC/GTEx/liability profile and Phase 3A dossier sync.",
    }
    runs = (
        [p4_run if r["analysis_run_id"] == "RUN-P4-001" else r for r in runs]
        if any(r["analysis_run_id"] == "RUN-P4-001" for r in runs)
        else [*runs, p4_run]
    )
    _write_csv(runs_fp, run_cols, runs)

    summary = {
        "analysis_run_id": "RUN-P4-001",
        "total_unified_candidates": len(rows),
        "counts_by_origin_phase": dict(Counter(r["origin_phase"] for r in rows)),
        "counts_by_decision": dict(Counter(r["decision"] for r in rows)),
        "counts_by_scientific_tier": dict(Counter(r["scientific_actionability_tier"] for r in rows)),
        "counts_by_epistemic_state": dict(Counter(r["epistemic_state"] for r in rows)),
        "origin_x_tier_matrix": {
            orig: dict(Counter(r["scientific_actionability_tier"] for r in rows if r["origin_phase"] == orig))
            for orig in ("EXPLORE_INHERITED_40", "PHASE3B_DENOVO_19")
        },
        "explore_tier_to_carbon_decision": {
            et: dict(Counter(r["decision"] for r in rows if r["origin_phase"] == "EXPLORE_INHERITED_40" and intake[r["portfolio_id"]]["explore_tier"] == et))
            for et in sorted({v["explore_tier"] for v in intake.values()})
        },
        "subnode_unbundling_summary": {
            "total_subnodes": len(subnodes),
            "by_parent": {
                par: {
                    "total": sum(1 for s in subnodes if s["parent_carbon_id"] == par),
                    "retained_exploratory": [s["gene_symbol"] for s in subnodes if s["parent_carbon_id"] == par and s["subnode_verdict"].startswith("KEEP_")],
                    "reclassified_biomarker": [s["gene_symbol"] for s in subnodes if s["parent_carbon_id"] == par and s["subnode_verdict"].startswith("RECLASSIFY_")],
                    "dropped_from_bundle": [s["gene_symbol"] for s in subnodes if s["parent_carbon_id"] == par and s["subnode_verdict"].startswith("DROP")],
                }
                for par in ("C014", "C015", "C017", "C018")
            },
        },
        "unified_cis_intervals_summary": {
            "total_intervals": len(cis_rows),
            "by_origin": dict(Counter(r["origin_phase"] for r in cis_rows)),
            "by_offtarget_safety_status": dict(Counter(r["offtarget_safety_status"] for r in cis_rows)),
            "promoted_leads_10": {pid: {"interval_id": v["interval_id"], "gene_symbol": v["gene_symbol"], "status": v["offtarget_safety_status"]} for pid, v in lead_by_pid.items()},
        },
        "dn04_celf5_deep_profile": celf5_prof,
        "registry_sha12": {
            "phase4_unified_portfolio": sha12(port_fp),
            "phase4_unified_cis_intervals": sha12(cis_fp),
            "phase3_sso_offtarget_audit": sha12(REG_DIR / "phase3_sso_offtarget_audit.csv"),
            "phase3_execution_readiness": sha12(REG_DIR / "phase3_execution_readiness.csv"),
            "phase3b_denovo_candidates": sha12(REG_DIR / "phase3b_denovo_candidates.csv"),
            "phase3b_denovo_sso_intervals": sha12(REG_DIR / "phase3b_denovo_sso_intervals.csv"),
        },
    }
    out_fp = ROOT / "work" / "phase4_final_synthesis" / "outputs" / "run_p4_001_unified_portfolio.json"
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    jtxt = json.dumps(summary, indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(jtxt), "Biosecurity sequence guard triggered!"
    out_fp.write_text(jtxt, encoding="utf-8")
    print(f"RUN-P4-001 OK: {len(rows)} unified candidates, {len(cis_rows)} cis intervals -> {out_fp.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
