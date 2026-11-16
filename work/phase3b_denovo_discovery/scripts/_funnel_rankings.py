"""Header-resolved Spillman MOESM5 Sheet 3 scan & genome-wide ranking waterfalls for Funnels 1 & 2 (0 hardcoded gene pre-filtering)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from carbon_als.loaders import assert_unique_donors, resolve_col, resolve_dataset_path

RUNNERUP_NOTES_F1 = {
    "BCKDHB": "Autosomal-recessive maple syrup urine disease (MSUD) mitochondrial ketoacid dehydrogenase subunit; haplo-tolerant (pLI=0) metabolic enzyme rather than neuronal axon/synapse regulator.",
    "C20orf194": "Uncharacterized open reading frame with unknown neuronal substrate or functional assay.",
    "CAMK2B": "Synaptic kinase replicated only in Ma 2022 without Bye sALS iPSC-MN splicing or Spillman fraction-proteomic loss.",
}


def scan_spillman_moesm5_sheet3(excl_genes: set[str]) -> dict[str, Any]:
    p29 = resolve_dataset_path("DS029_SPILL", verify_hash=True)
    raw = pd.read_excel(p29 / "401_2026_3084_MOESM5_ESM.xlsx", sheet_name="3 - CE Abundance in FCx H0", header=None)
    top_hdr = pd.Series([np.nan if str(x).strip() in ("", "nan") else str(x).strip() for x in raw.iloc[1].tolist()]).ffill()
    sub_hdr = [str(x).strip() for x in raw.iloc[2].tolist()]
    comp_cols = [sub if pd.isna(top) else f"{top}|{sub}" for top, sub in zip(top_hdr, sub_hdr, strict=True)]
    df = raw.iloc[3:23].copy()
    df.columns = comp_cols
    sid_c, cid_c = resolve_col(df, "Study ID"), resolve_col(df, "Case ID")
    assert_unique_donors(df[cid_c].astype(str).tolist(), "Spillman MOESM5 Sheet 3")
    grp = df[sid_c].astype(str).str.strip()
    c9_m, ctl_m = grp.str.startswith("C9-FTD"), grp.str.startswith("CTRL")
    assert int(c9_m.sum()) == 10 and int(ctl_m.sum()) == 10

    genes_on_sheet = sorted({c.split(" JUNCTIONS|")[0] for c in comp_cols if " JUNCTIONS|" in c})
    per_gene: dict[str, Any] = {}
    for g in genes_on_sheet:
        can = pd.to_numeric(df[resolve_col(df, f"{g} JUNCTIONS|Canonical")], errors="coerce")
        ce = pd.to_numeric(df[resolve_col(df, f"{g} JUNCTIONS|CE")], errors="coerce")
        c9_pos, ctl_pos = int((ce[c9_m] > 0).sum()), int((ce[ctl_m] > 0).sum())
        _, p_fish = stats.fisher_exact([[c9_pos, 10 - c9_pos], [ctl_pos, 10 - ctl_pos]], alternative="two-sided")
        psi = ce / (can + ce)
        _, p_mwu = stats.mannwhitneyu(psi[c9_m], psi[ctl_m], alternative="two-sided")
        per_gene[g] = {
            "is_explore_als": (g in excl_genes), "n_c9ftd": 10, "n_ctrl": 10,
            "ce_pos_c9ftd": c9_pos, "ce_pos_ctrl": ctl_pos, "fisher_2s_p": float(p_fish), "mwu_psi_2s_p": float(p_mwu),
            "mean_ce_frac_c9ftd": round(float(psi[c9_m].mean()), 4), "mean_ce_frac_ctrl": round(float(psi[ctl_m].mean()), 4),
        }
    non_ex = [g for g, v in per_gene.items() if not v["is_explore_als"]]
    assert non_ex == ["KALRN"], f"Expected KALRN as sole non-ExploreALS gene on MOESM5 S3, got {non_ex}"
    kal = per_gene["KALRN"]
    return {
        "all_sheet3_genes_scanned": per_gene, "non_explore_genes_on_sheet3": non_ex,
        "n_c9ftd": 10, "n_ctrl": 10, "kalrn_ce_pos_c9ftd": kal["ce_pos_c9ftd"], "kalrn_ce_pos_ctrl": kal["ce_pos_ctrl"],
        "fisher_2s_p": kal["fisher_2s_p"], "mwu_psi_2s_p": kal["mwu_psi_2s_p"],
        "mean_kalrn_ce_frac_c9ftd": kal["mean_ce_frac_c9ftd"], "mean_kalrn_ce_frac_ctrl": kal["mean_ce_frac_ctrl"],
        "benchmark_unc13a_pos_c9ftd": per_gene["UNC13A"]["ce_pos_c9ftd"], "benchmark_stmn2_pos_c9ftd": per_gene["STMN2"]["ce_pos_c9ftd"],
    }


def build_funnel1_waterfall(
    jdf: pd.DataFrame, ribo: pd.DataFrame, ma5: pd.DataFrame, bye_t6: pd.DataFrame, zh_non: pd.DataFrame, excl_genes: set[str]
) -> dict[str, Any]:
    p29 = resolve_dataset_path("DS029_SPILL", verify_hash=True)
    m1 = pd.read_excel(p29 / "401_2026_3084_MOESM1_ESM.xlsx")
    sp_dn: set[str] = set()
    h_p, h_fc = resolve_col(m1, "pVal_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control"), resolve_col(m1, "Log2Ratios_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control")
    s_p, s_fc = resolve_col(m1, "pVal_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control"), resolve_col(m1, "Log2Ratios_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")
    for _, row in m1.iterrows():
        gs = [x.strip() for x in str(row.get("Gene", "")).split(";") if x.strip()]
        if (pd.notna(row[h_p]) and float(row[h_p]) < 0.05 and float(row[h_fc]) < 0) or (pd.notna(row[s_p]) and float(row[s_p]) < 0.05 and float(row[s_fc]) < 0):
            sp_dn.update(gs)
    sp_dn -= excl_genes

    j_non = jdf[~jdf["gene_name"].astype(str).isin(excl_genes)].copy()
    all_b = set(j_non["gene_name"].astype(str))
    cj_genes = set(j_non[j_non["cryptic_junction"].astype(str).str.lower() == "true"]["gene_name"].astype(str))
    ribo_non = ribo[~ribo["gene_name"].astype(str).isin(excl_genes)].copy()
    ribo_map = ribo_non.groupby("gene_name")[["log2FoldChange", "pvalue", "padj"]].first().to_dict(orient="index")
    ribo_dn = {g for g, v in ribo_map.items() if pd.notna(v["padj"]) and float(v["padj"]) < 0.05 and float(v["log2FoldChange"]) < -0.5}
    ma_genes = set(ma5[resolve_col(ma5, "Genes")].astype(str)) - excl_genes
    bye_sig = set(bye_t6[bye_t6[resolve_col(bye_t6, "Adjusted P-value")] < 0.05][resolve_col(bye_t6, "Genes")].astype(str)) - excl_genes

    g_rep = {g for g in (cj_genes & ribo_dn) if (g in ma_genes or g in bye_sig or g in sp_dn)}
    g_i3n = (cj_genes & ribo_dn) - g_rep
    g_cj_other = cj_genes - (cj_genes & ribo_dn)
    g_iso_only = all_b - cj_genes
    assert len(g_rep) + len(g_i3n) + len(g_cj_other) + len(g_iso_only) == len(all_b), "Rule 3B-1 Funnel 1 waterfall mismatch!"

    ranked_b = sorted(
        [{"gene": g, "n_human_modalities": int(g in ma_genes) + int(g in bye_sig) + int(g in sp_dn),
          "in_ma2022": (g in ma_genes), "in_bye_sals_t6": (g in bye_sig), "in_spillman_dia_dn": (g in sp_dn),
          "riboseq_log2fc": round(float(ribo_map[g]["log2FoldChange"]), 4), "riboseq_padj": float(ribo_map[g]["padj"]),
          "runnerup_disposition": RUNNERUP_NOTES_F1.get(g, "ADOPTED_PHASE3B")} for g in g_rep],
        key=lambda x: (-x["n_human_modalities"], x["riboseq_log2fc"]),
    )
    zh_dn = set(zh_non[(zh_non[resolve_col(zh_non, "BH")] < 0.05) & (zh_non[resolve_col(zh_non, "avg_log2FC")] < 0)][resolve_col(zh_non, "gene")].astype(str))
    ma_ranked = sorted(
        [{"gene": g, "riboseq_log2fc": round(float(ribo_map[g]["log2FoldChange"]), 4) if g in ribo_map and pd.notna(ribo_map[g]["log2FoldChange"]) else None,
          "in_zhang_mn_bh05_dn": (g in zh_dn), "in_spillman_dia_dn": (g in sp_dn)}
         for g in ma_genes if (g in ribo_dn or g in zh_dn or g in sp_dn)],
        key=lambda x: (not x["in_zhang_mn_bh05_dn"], x["riboseq_log2fc"] if x["riboseq_log2fc"] is not None else 0.0),
    )
    return {
        "partition_non_explore_genes": {
            "total": len(all_b), "cryptic_junc_riboseq_dn_and_human_rep": len(g_rep),
            "cryptic_junc_riboseq_dn_i3n_only": len(g_i3n), "cryptic_junc_without_riboseq_dn": len(g_cj_other),
            "canonical_isoform_shift_only": len(g_iso_only),
        },
        "genomewide_brown_replicated_hits": ranked_b, "genomewide_ma2022_multimodal_top15": ma_ranked[:15],
    }


def build_funnel2_waterfall(bs2: pd.DataFrame, bs5: pd.DataFrame, bs6: pd.DataFrame, zeng_fp: Path, excl_genes: set[str]) -> dict[str, Any]:
    bs2_non = bs2[~bs2["gene_name"].astype(str).isin(excl_genes)].copy()
    bs6_g = resolve_col(bs6, "gene_name")
    bs6_sig = bs6[(~bs6[bs6_g].astype(str).isin(excl_genes)) & (bs6["padj"] < 0.05)].sort_values("padj")
    sig_genes = set(bs6_sig[bs6_g].astype(str))
    n_ev_ribo = int(bs2_non["gene_name"].astype(str).isin(sig_genes).sum())
    n_ev_other = int((~bs2_non["gene_name"].astype(str).isin(sig_genes)).sum())
    assert (n_ev_ribo + n_ev_other) == len(bs2_non)

    bs5_non = bs5[(~bs5["gene_name"].astype(str).isin(excl_genes)) & (bs5["selective"].astype(str).str.lower() == "true")].sort_values("fold_enrichment", ascending=False)
    z4 = pd.read_excel(zeng_fp, sheet_name="S4")
    z4_non = z4[(~z4[resolve_col(z4, "gene_name")].astype(str).isin(excl_genes)) & (z4["padj"] < 0.05)].sort_values("padj")
    return {
        "riboseq_event_partition": {"total_non_explore_events": len(bs2_non), "events_with_riboseq_padj05": n_ev_ribo, "events_without_riboseq_padj05": n_ev_other},
        "genomewide_bs6_riboseq_sig": bs6_sig[[bs6_g, "log2FoldChange", "pvalue", "padj"]].to_dict(orient="records"),
        "genomewide_bs5_nygc_selective_top15": bs5_non.head(15)[["le_id", "gene_name", "count_not_path", "count_path", "fold_enrichment"]].to_dict(orient="records"),
        "genomewide_zeng_s4_top15": z4_non.head(15)[["gene_name", "APA_direction", "PAS_ID_down", "PAS_ID_up", "Delta_distal_PAS_usage", "padj"]].to_dict(orient="records"),
        "trappc12_locus_dissection": {
            "bryce_smith_intronic_ale": "chr2:3457795-3458181(+)", "brown_secondary_cassette_ce": "chr2:3458462-3458515(+)",
            "zeng_canonical_distal_3utr_pas": "chr2:3479564-3485092(+) (27 kb downstream canonical 3'UTR lengthening, distinct from intronic ALE)",
        },
    }
