"""RUN-P4-003: Nov 2026 Deep Compute, AlphaGenome, gnomAD/ClinVar & 3D Retrospective (S06, C001, C022, C006, C015, C018)."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (SRC, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _retrospective_struct_helpers import analyze_dnajb2_and_c1q_structures, analyze_sarm1_octamer_and_genetics  # noqa: E402
from carbon_als.allostery_pkpd import hetero_octamer_tlock_inhibition  # noqa: E402
from carbon_als.loaders import load_brown2022_splicing, resolve_col, resolve_dataset_path  # noqa: E402

SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)
P4_CACHE = ROOT / "work" / "phase4_final_synthesis" / "cache"
RETRO_CACHE = P4_CACHE / "nov2026_retrospective"
PRIORS_FP = P4_CACHE / "nov2026_retrospective_priors.json"
OUT_FP = ROOT / "work" / "phase4_final_synthesis" / "outputs" / "run_p4_003_nov2026_retrospective.json"


def _compute_staged_splicing_and_sarm1() -> dict[str, Any]:
    br = load_brown2022_splicing(genes=["UNC13A", "DNAJB2"])
    jdf, rdf, bdf = br["junctions_df"], br["rnaseq_df"], br["riboseq_df"]
    u_j = jdf[jdf[resolve_col(jdf, "gene_name")] == "UNC13A"].copy()
    ce_row = u_j[u_j["paste_into_igv_exon"].astype(str).str.contains("17642414-17642591", na=False)].sort_values("FDR").iloc[0]
    ir_lsv = u_j[u_j["lsv_id"].astype(str).str.contains("17629240-17629323", na=False)].copy()
    ir_row = ir_lsv[(ir_lsv["junc_start"] == 17628338) & (ir_lsv["junc_end"] == 17629239)].iloc[0]
    can_31_32 = ir_lsv[(ir_lsv["junc_start"] == 17627940) & (ir_lsv["junc_end"] == 17629240)].iloc[0]

    d_rna = rdf[rdf[resolve_col(rdf, "gene_name")] == "DNAJB2"].iloc[0]
    d_ribo = bdf[bdf[resolve_col(bdf, "gene_name")] == "DNAJB2"].iloc[0]
    pdb_map = {
        k: resolve_dataset_path(f"DS_PDB_{k}", verify_hash=True)
        for k in ("7ANW", "7DJT", "7NAL", "9TZY")
    }
    return {
        "s06_sarm1_octamer_and_genetics": analyze_sarm1_octamer_and_genetics(pdb_map, RETRO_CACHE),
        "c001_unc13a_majiq_intron31_ceiling": {
            "dataset_id": "DS_CRYPTIC",
            "intron20_cryptic_exon_17642414_17642591": {
                "control_psi": round(float(ce_row["control_e_psi"]), 5),
                "tdp_kd_psi": round(float(ce_row["tdp_kd_e_psi"]), 5),
                "delta_psi": round(float(ce_row["deltaPSI"]), 5),
                "fdr": float(f"{float(ce_row['FDR']):.6e}"),
            },
            "intron31_retention_17628338_17629239": {
                "lsv_id": str(ir_row["lsv_id"]),
                "grch38_span_1b": f"chr19:{int(ir_row['junc_start'])}-{int(ir_row['junc_end'])}(-)",
                "control_psi": round(float(ir_row["control_e_psi"]), 5),
                "tdp_kd_psi": round(float(ir_row["tdp_kd_e_psi"]), 5),
                "delta_psi": round(float(ir_row["deltaPSI"]), 5),
                "fdr": float(f"{float(ir_row['FDR']):.6e}"),
                "canonical_exon31_32_control_psi": round(float(can_31_32["control_e_psi"]), 5),
                "canonical_exon31_32_tdp_kd_psi": round(float(can_31_32["tdp_kd_e_psi"]), 5),
                "canonical_exon31_32_delta_psi": round(float(can_31_32["deltaPSI"]), 5),
                "canonical_exon31_32_fdr": float(f"{float(can_31_32['FDR']):.6e}"),
                "implied_intron20_only_aso_mrna_ceiling_pct": round(100.0 * (1.0 - float(ir_row["tdp_kd_e_psi"])), 2),
            },
        },
        "c022_dnajb2_tdp43_independence": {
            "majiq_cryptic_junctions_n": int(len(jdf[jdf[resolve_col(jdf, "gene_name")] == "DNAJB2"])),
            "brown2022_i3neuron_rnaseq_log2fc": round(float(d_rna["log2FoldChange"]), 5),
            "brown2022_i3neuron_rnaseq_pvalue": round(float(d_rna["pvalue"]), 6),
            "brown2022_i3neuron_rnaseq_padj": round(float(d_rna["padj"]), 6),
            "brown2022_i3neuron_riboseq_log2fc": round(float(d_ribo["log2FoldChange"]), 5),
            "brown2022_i3neuron_riboseq_padj": round(float(d_ribo["padj"]), 6),
        },
    }


def _pick_ag_track(rows: list[dict[str, Any]], ontology_curie: str, output_type: str, gene_name: str | None = None) -> dict[str, Any]:
    for r in rows:
        if r.get("ontology_curie") == ontology_curie and r.get("output_type") == output_type:
            if gene_name is None or r.get("gene_name") == gene_name:
                return r
    raise KeyError(f"Missing AlphaGenome track: {ontology_curie} {output_type} {gene_name}")


def _summarize_alphagenome_and_scfd1() -> dict[str, Any]:
    ag = json.loads((RETRO_CACHE / "alphagenome_nov2026_retrospective.json").read_text(encoding="utf-8"))
    ot = json.loads((RETRO_CACHE / "opentargets_scfd1_crediblesets_full.json").read_text(encoding="utf-8"))["data"]
    cv_db = json.loads((RETRO_CACHE / "clinvar_sarm1_dnajb2_grch38.json").read_text(encoding="utf-8"))["ot_dbsnp_scfd1"]
    pop_afs = ot.get("gnomad_v4_population_afs", {})

    def _jmap(pred_key: str) -> dict[str, dict[str, float]]:
        return {j["junction_0b"]: j for j in ag[pred_key]["kcnq2_junctions"]}

    j3, j2 = _jmap("kcnq2_win3_predict_splicing"), _jmap("kcnq2_win2_predict_splicing")
    eur_rows = {
        (r["variant"]["rsIds"][0] if r["variant"].get("rsIds") else r["variant"]["id"]): r
        for r in ot["eur"]["locus"]["rows"]
    }
    xanc_rows = {
        (r["variant"]["rsIds"][0] if r["variant"].get("rsIds") else r["variant"]["id"]): r
        for r in ot["xanc"]["locus"]["rows"]
    }
    scfd1_snps = {}
    for rs in ("rs229243", "rs229195", "rs229194", "rs229143"):
        er, xr = eur_rows.get(rs, {}), xanc_rows.get(rs, {})
        v = er.get("variant") or xr.get("variant") or {}
        af_map = pop_afs.get(rs, {})
        scfd1_snps[rs] = {
            "grch38_variant": f"chr14:{v.get('position')}:{v.get('referenceAllele')}>{v.get('alternateAllele')}",
            "gnomad_nfe_af": af_map.get("nfe_adj"),
            "gnomad_eas_af": af_map.get("eas_adj"),
            "eur_beta_alt": round(float(er["beta"]), 6) if er.get("beta") is not None else None,
            "eur_pip": round(float(er["posteriorProbability"]), 6) if er.get("posteriorProbability") is not None else None,
            "xanc_pip": round(float(xr["posteriorProbability"]), 6) if xr.get("posteriorProbability") is not None else None,
        }
    eur_p = float(f"{float(ot['eur']['pValueMantissa'])}e{int(ot['eur']['pValueExponent'])}")
    gof_10x = hetero_octamer_tlock_inhibition(10.0, l_wt=8.0, gof_allele_fraction=0.5, d_lock=6.5)
    gof_100x = hetero_octamer_tlock_inhibition(100.0, l_wt=8.0, gof_allele_fraction=0.5, d_lock=6.5)
    return {
        "s06_hetero_octamer_gof_mwc_prior": {
            "l_wt": 8.0, "d_lock": 6.5, "gof_allele_fraction": 0.5,
            "basal_nadase_pct": round(100.0 * gof_100x["baseline_fractional_activity"], 2),
            "residual_nadase_pct_at_10x_kd": round(100.0 * gof_10x["treated_fractional_activity"], 2),
            "residual_nadase_pct_at_100x_kd": round(100.0 * gof_100x["treated_fractional_activity"], 2),
        },
        "c006_kcnq2_alphagenome_ise_hazard": {
            "win3_intron5_chr20_63442302_C_G": {
                "exon4_6_skip_63439708_63444658": j3["63439708-63444658(-)"],
                "exon5_6_incl_63439708_63442405": j3["63439708-63442405(-)"],
                "exon4_5_incl_63442531_63444658": j3["63442531-63444658(-)"],
                "exon4_6_skip_rel_pct_change": round(100.0 * j3["63439708-63444658(-)"]["delta"] / j3["63439708-63444658(-)"]["ref_score"], 2),
                "motor_neuron_atac": _pick_ag_track(ag["kcnq2_win3_peak_score"]["top_cns_neuronal"], "CL:0000100", "ATAC"),
            },
            "win2_intron4_ug_chr20_63442566_A_T": {
                "exon4_6_skip_63439708_63444658": j2["63439708-63444658(-)"],
                "exon5_6_incl_63439708_63442405": j2["63439708-63442405(-)"],
                "exon4_5_incl_63442531_63444658": j2["63442531-63444658(-)"],
                "motor_neuron_splice_quantile": _pick_ag_track(ag["kcnq2_win2_peak_score"]["top_cns_neuronal"], "CL:0000100", "SPLICE_JUNCTIONS", "KCNQ2")["quantile_score"],
            },
            "joseph2025_pmc12672377_audit": "Main-text strings at chr20:63442265-63442532 verified as RIP-qPCR and CRISPR genotyping primers; 2'-O-MOE smASOs reside in external Supplementary Table 4.",
        },
        "c015_scfd1_g2e3_susie_and_alphagenome": {
            "eur_study_locus_id": ot["eur"]["studyLocusId"],
            "eur_lead_pvalue": float(f"{eur_p:.4e}"),
            "eur_purity_mean_r2": round(float(ot["eur"]["purityMeanR2"]), 6),
            "eur_purity_min_r2": round(float(ot["eur"]["purityMinR2"]), 6),
            "eur_credible_set_n": int(ot["eur"]["locus"]["count"]),
            "coloc_h4_cross_ancestry_gcst90027163": 0.958006,
            "coloc_h4_eur_vs_cross_ancestry_gwas_gcst90027163": 0.958006,
            "coloc_h4_ftd_gcst90428108": 0.936544,
            "coloc_scope_note": "COLOC H4=0.958006 quantifies EUR ALS GWAS (GCST90027164) vs cross-ancestry ALS GWAS (GCST90027163) colocalization (not MN-vs-microglia eQTL coloc; iMGL SCFD1 PP_H4=0.88-0.89 is from Perez-Alcantara 2026 PMID:43045849).",
            "phased_1000g_phase3_4snp_haplotype_counts": {
                "snps": ["rs229243", "rs229195", "rs229194", "rs229143"],
                "eur_1111_of_any_A_chromosomes": "351/363 (96.7%)",
                "eur_mixed_of_total_chromosomes": "12/1006",
                "afr_1111_of_any_A_chromosomes": "853/1173 (72.7%)",
                "afr_mixed_of_total_chromosomes": "320/1322",
                "all_mixed_of_total_chromosomes": "382/5008",
            },
            "in_phase_als_risk_alleles": scfd1_snps,
            "dbsnp_1000g_af_audit": cv_db.get("dbsnp_scfd1", {}),
            "rs229143_cd14_monocyte_scfd1_rnaseq": _pick_ag_track(ag["scfd1_rs229143_score"]["top_myeloid_microglia"], "CL:0001054", "RNA_SEQ", "SCFD1"),
            "rs229143_motor_neuron_scfd1_splice": _pick_ag_track(ag["scfd1_rs229143_score"]["top_cns_neuronal"], "CL:0000100", "SPLICE_JUNCTIONS", "SCFD1"),
            "rs229195_motor_neuron_g2e3_splice": _pick_ag_track(ag["scfd1_rs229195_score"]["top_cns_neuronal"], "CL:0000100", "SPLICE_JUNCTIONS", "G2E3"),
        },
    }


def main() -> None:
    has_staged = (ROOT / "data" / "pharmacology_structures" / "phase2_pdb" / "pdb_00007djt.cif").is_file()
    if has_staged:
        staged_part = _compute_staged_splicing_and_sarm1()
        PRIORS_FP.write_text(json.dumps(staged_part, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    else:
        staged_part = json.loads(PRIORS_FP.read_text(encoding="utf-8"))
    mode_lbl = "staged_primary" if has_staged else "cached_priors"
    out = {
        "run_id": "RUN-P4-003",
        **staged_part,
        **analyze_dnajb2_and_c1q_structures(RETRO_CACHE),
        **_summarize_alphagenome_and_scfd1(),
    }
    blob = json.dumps(out, indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(blob), "Biosecurity sequence guard failed in RUN-P4-003!"
    OUT_FP.parent.mkdir(parents=True, exist_ok=True)
    OUT_FP.write_text(blob + "\n", encoding="utf-8")
    print(f"RUN-P4-003 OK ({mode_lbl}): {OUT_FP.relative_to(ROOT).as_posix()} ({len(blob)} bytes)")


if __name__ == "__main__":
    main()
