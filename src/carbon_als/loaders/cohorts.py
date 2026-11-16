"""Battle-tested, donor-aware dataset loaders for CarbonALS Phase 2+."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from .guards import (
    assert_contrast_pair,
    assert_modality,
    assert_unique_donors,
    numeric_clean,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)


def load_brown2022_splicing(genes: list[str] | None = None) -> dict[str, Any]:
    """Load Brown et al. 2022 (DS_CRYPTIC) MAJIQ splice junctions, RNA-seq, and Ribo-seq."""
    cdir = resolve_dataset_path("DS_CRYPTIC", verify_hash=True)
    junc = pd.read_csv(cdir / "Brown2022_41586_2022_4436_MOESM11_ESM.csv")
    rna = pd.read_csv(cdir / "Brown2022_41586_2022_4436_MOESM12_ESM.csv")
    ribo = pd.read_csv(cdir / "Brown2022_41586_2022_4436_MOESM13_ESM.csv")
    if genes is not None:
        gset = set(genes)
        junc = junc[junc[resolve_col(junc, "gene_name")].isin(gset)].copy()
        rna = rna[rna[resolve_col(rna, "gene_name")].isin(gset)].copy()
        ribo = ribo[ribo[resolve_col(ribo, "gene_name")].isin(gset)].copy()
    return {
        "dataset_id": "DS_CRYPTIC",
        "splicing_modality": assert_modality("RNA_SPLICING_MAJIQ", "DS_CRYPTIC"),
        "rnaseq_modality": assert_modality("RNASEQ_DESEQ2", "DS_CRYPTIC"),
        "riboseq_modality": assert_modality("RIBOSEQ_DESEQ2", "DS_CRYPTIC"),
        "junctions_df": junc,
        "rnaseq_df": rna,
        "riboseq_df": ribo,
    }


def load_bye2025_screen() -> pd.DataFrame:
    """Recompute Bye et al. 2025 (DS005_BYE) 107-drug x 16-sALS-donor paired screen statistics."""
    bye_path = resolve_dataset_path("DS005_BYE", verify_hash=True)
    t12 = read_xlsx_sparse_safe(bye_path, "Table 12", header_row_1based=3)
    drug_col = resolve_col(t12, "Active Ingredient")
    donor_cols = [resolve_col(t12, f"SALS {i}") for i in range(1, 17)]
    assert_unique_donors(donor_cols, "DS005_BYE Table 12")
    t12 = t12[t12[drug_col].notna()].copy()
    t12[drug_col] = t12[drug_col].astype(str).str.strip()
    for dc in donor_cols:
        t12[dc] = pd.to_numeric(t12[dc], errors="coerce")
    dmso = t12.loc[t12[drug_col] == "DMSO", donor_cols].iloc[0].to_numpy(dtype=float)
    active = t12.loc[~t12[drug_col].isin(["DMSO", "Untreated"])].copy()
    assert len(active) == 107, f"Expected 107 active drugs, got {len(active)}"
    rows: list[dict[str, Any]] = []
    for _, r in active.iterrows():
        vals = r[donor_cols].to_numpy(dtype=float)
        m = np.isfinite(vals) & np.isfinite(dmso)
        diff = vals[m] - dmso[m]
        t_res = stats.ttest_1samp(diff, popmean=0.0)
        w_res = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided", method="exact")
        rows.append({
            "drug": str(r[drug_col]),
            "modality": assert_modality("IPSC_MN_SURVIVAL_DAYS", "DS005_BYE"),
            "n_donors": int(m.sum()),
            "mean_paired_dmso_days": float(np.mean(diff)),
            "t_stat_paired": float(t_res.statistic),
            "p_ttest_2s": float(t_res.pvalue),
            "p_wilcoxon_exact_2s": float(w_res.pvalue),
        })
    df = pd.DataFrame(rows).sort_values("mean_paired_dmso_days", ascending=False).reset_index(drop=True)
    df["rank_107"] = np.arange(1, len(df) + 1)
    df["q_bh_107_ttest_2s"] = multipletests(df["p_ttest_2s"], method="fdr_bh")[1]
    return df


def load_spillman2026_fractions(genes: list[str]) -> dict[str, dict[str, Any]]:
    """Load Spillman 2026 (DS029_SPILL) strictly separating MOESM1 DIA protein fractions from MOESM2 RNA-seq."""
    p29 = resolve_dataset_path("DS029_SPILL", verify_hash=True)
    m1 = pd.read_excel(p29 / "401_2026_3084_MOESM1_ESM.xlsx")
    m2_hom = pd.read_excel(p29 / "401_2026_3084_MOESM2_ESM.xlsx", sheet_name="Homogenate", skiprows=1, index_col=0)
    m2_syn = pd.read_excel(p29 / "401_2026_3084_MOESM2_ESM.xlsx", sheet_name="Synaptosome", skiprows=1, index_col=0)
    syn_ctl = [c for c in m1.columns if c.startswith("Norm_S") and "Synapt_FRCTX_Control" in c]
    syn_c9 = [c for c in m1.columns if c.startswith("Norm_S") and "Synapt_FRCTX_C9FTD" in c]
    hom_ctl = [c for c in m1.columns if c.startswith("Norm_H") and "Homogenate_FRCTX_Control" in c]
    hom_c9 = [c for c in m1.columns if c.startswith("Norm_H") and "Homogenate_FRCTX_C9FTD" in c]
    assert_unique_donors([re.sub(r"^Norm_S", "S_", c) for c in syn_ctl + syn_c9], "DS029_SPILL Synaptosome")
    assert_unique_donors([re.sub(r"^Norm_H", "H_", c) for c in hom_ctl + hom_c9], "DS029_SPILL Homogenate")
    assert_contrast_pair(
        m1[resolve_col(m1, "Log2Ratios_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")],
        m1[syn_c9].apply(pd.to_numeric, errors="coerce").mean(axis=1),
        m1[syn_ctl].apply(pd.to_numeric, errors="coerce").mean(axis=1),
        tol=1e-2,
    )
    gcol1 = resolve_col(m1, "Gene")
    out: dict[str, dict[str, Any]] = {}
    for sym in genes:
        rec: dict[str, Any] = {}
        r1 = m1[m1[gcol1].fillna("").astype(str).str.split(";").apply(lambda x: sym in x)]
        if not r1.empty:
            row = r1.iloc[0]
            for key, c_cols, d_cols, l_col, p_col, q_col in [
                ("synaptosome_protein", syn_ctl, syn_c9, "Log2Ratios_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control", "pVal_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control", "pAdj_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control"),
                ("homogenate_protein", hom_ctl, hom_c9, "Log2Ratios_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control", "pVal_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control", "pAdj_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control"),
            ]:
                cv, dv = numeric_clean(row[c_cols]), numeric_clean(row[d_cols])
                rec[key] = {
                    "modality": assert_modality("PROTEOMICS_DIA", "DS029_SPILL"),
                    "n_c9ftd": int(len(dv)),
                    "n_ctrl": int(len(cv)),
                    "log2fc": float(row[resolve_col(m1, l_col)]),
                    "p_value": float(row[resolve_col(m1, p_col)]),
                    "padj": float(row[resolve_col(m1, q_col)]),
                }
        for rkey, df2 in [("homogenate_rnaseq", m2_hom), ("synaptosome_rnaseq", m2_syn)]:
            r2 = df2[df2[resolve_col(df2, "gene_name")].astype(str) == sym]
            if not r2.empty:
                rw2 = r2.iloc[0]
                rec[rkey] = {
                    "modality": assert_modality("RNASEQ_DESEQ2", "DS029_SPILL_MOESM2"),
                    "log2fc": float(rw2[resolve_col(df2, "log2FoldChange")]),
                    "p_value": float(rw2[resolve_col(df2, "pvalue")]),
                    "padj": float(rw2[resolve_col(df2, "padj")]),
                }
        out[sym] = rec
    return out
