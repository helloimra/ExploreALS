"""RUN-P3B-004: Targeted Phase 3B deep dive on DN-02 KALRN (rs2173852 + Kalirin-12), DN-01 ATG4B, DN-03/05 PTPRT/PRUNE2, & DN-08 ELK1."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
P3A_SCRIPTS = ROOT / "work" / "phase3a_execution_safety" / "scripts"
for p in (SRC, SCRIPT_DIR, P3A_SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _deep_dive_helpers import load_elk1_st7_regulons, run_elk1_regulon_sign_test, run_isoform_structure_and_liability_audits  # noqa: E402
from _deep_dive_nygc import analyze_nygc_multiregion  # noqa: E402
from _funnel_helpers import clean_json  # noqa: E402
from _offtarget_helpers import load_gnomad_v41_constraint_map  # noqa: E402
from carbon_als.loaders import resolve_dataset_path  # noqa: E402

CACHE_DIR = ROOT / "work" / "phase3b_denovo_discovery" / "cache"
OUT_FP = ROOT / "work" / "phase3b_denovo_discovery" / "outputs" / "run_p3b_004_targeted_deep_dive.json"
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)


def _summarize_alphagenome_rs2173852(ag_kal: dict) -> dict:
    ss_by = {(r["pos_1b"], r["track_name"], r["strand"]): r for r in ag_kal["splice_sites_base_probs"]}
    d5 = ss_by[(124701255, "donor", "+")]
    a_maj = ss_by[(124701093, "acceptor", "+")]
    a_alt = ss_by[(124700977, "acceptor", "+")]
    fcx_u = [r for r in ag_kal["splice_usage_base_probs"] if r["pos_1b"] == 124701255 and r["biosample"] == "frontal cortex"]
    sc_u = [r for r in ag_kal["splice_usage_base_probs"] if r["pos_1b"] == 124701255 and r["biosample"] == "spinal cord"]
    top_by_bio = {}
    for r in ag_kal["top_global_scores"]:
        if r["output_type"] == "SPLICE_JUNCTIONS" and r["biosample_name"] not in top_by_bio:
            top_by_bio[r["biosample_name"]] = {"raw_score": round(float(r["raw_score"]), 4), "quantile_score": round(float(r["quantile_score"]), 6)}
    return {
        "variant": ag_kal["variant"], "rsid": ag_kal["rsid"], "n_scored_rows": ag_kal["n_scored_rows"],
        "donor_124701255_plus": {
            "ref_G_prob": d5["ref_G_prob"], "alt_C_prob": d5["alt_C_prob"],
            "delta_alt_minus_ref": d5["delta_alt_minus_ref"],
            "fold_reduction": round(float(d5["ref_G_prob"]) / float(d5["alt_C_prob"]), 2),
        },
        "major_acceptor_124701093_plus": {
            "ref_G_prob": a_maj["ref_G_prob"], "alt_C_prob": a_maj["alt_C_prob"],
            "fold_reduction": round(float(a_maj["ref_G_prob"]) / float(a_maj["alt_C_prob"]), 2),
        },
        "alt_acceptor_124700977_plus": {
            "ref_G_prob": a_alt["ref_G_prob"], "alt_C_prob": a_alt["alt_C_prob"],
            "fold_reduction": round(float(a_alt["ref_G_prob"]) / float(a_alt["alt_C_prob"]), 2),
        },
        "max_frontal_cortex_usage_fold_drop": round(max(float(r["ref_G_usage"]) / float(r["alt_C_usage"]) for r in fcx_u), 2),
        "max_spinal_cord_usage_fold_drop": round(max(float(r["ref_G_usage"]) / float(r["alt_C_usage"]) for r in sc_u), 2),
        "top_cns_splice_junction_scores": {k: top_by_bio[k] for k in ("dorsolateral prefrontal cortex", "spinal cord", "frontal cortex", "motor neuron") if k in top_by_bio},
    }


def main() -> None:
    OUT_FP.parent.mkdir(parents=True, exist_ok=True)
    ext_main = json.loads((CACHE_DIR / "external_priors_and_structures.json").read_text(encoding="utf-8"))
    ext_dd = json.loads((CACHE_DIR / "deep_dive_external_priors.json").read_text(encoding="utf-8"))
    gnomad_map = load_gnomad_v41_constraint_map(resolve_dataset_path("DS_GNOMAD_V41_CONSTRAINT", verify_hash=True))

    regs = load_elk1_st7_regulons()
    union_reg = set(regs["ELK1_all"]) | set(regs["ELK4_all"])
    nygc_res, nygc_tstats = analyze_nygc_multiregion(union_reg)
    elk1_res = run_elk1_regulon_sign_test(nygc_tstats)
    iso_struct_liab = run_isoform_structure_and_liability_audits(ext_main, ext_dd, gnomad_map)
    ag_rs = _summarize_alphagenome_rs2173852(ext_dd["alphagenome"]["kalrn_rs2173852"])

    out = clean_json({
        "analysis_run_id": "RUN-P3B-004",
        "kalrn_rs2173852_alphagenome_summary": ag_rs,
        "kalrn_rs2173852_genetics_summary": ext_dd["kalrn_rs2173852_human_genetics"],
        "gtex_v8_median_tpm": ext_dd["gtex_v8_median_tpm"],
        "chembl_atg4b_summary": ext_dd["chembl_atg4b_modality_audit"],
        "recent_literature_2025_2026": ext_dd["recent_literature_2025_2026"],
        "prune2_intron_alphagenome_peaks": ext_dd["alphagenome"]["prune2_intron"]["top_internal_splice_peaks"][:5],
        "ptprt_intron_alphagenome_peaks": ext_dd["alphagenome"]["ptprt_intron"]["top_internal_splice_peaks"][:5],
        **iso_struct_liab,
        "nygc_multiregion_donor_analysis": nygc_res,
        "elk1_st7_regulon_sign_test": elk1_res,
    })
    txt = json.dumps(out, indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(txt), "Biosecurity sequence guard failed in run_p3b_004_targeted_deep_dive.json!"
    OUT_FP.write_text(txt, encoding="utf-8")
    print("RUN-P3B-004 OK ->", OUT_FP.relative_to(ROOT).as_posix(), f"({len(txt)} bytes)")


if __name__ == "__main__":
    main()
