"""RUN-B4-001: Primary Bye 2025 107-drug x 16-donor iPSC-MN screen & RNA-seq reanalysis."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase1_batches.batch_runner_utils import (
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_4" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BATCH4_DRUGS = {
    "Trazodone": "C009",
    "Riluzole": "C013",
    "Baricitinib": "C019",
    "Apilimod": "C020",
    "Icerguastat": "C021",
}


def analyze_table12(xlsx_path: Path) -> tuple[pd.DataFrame, dict]:
    df12 = read_xlsx_sparse_safe(xlsx_path, "Table 12", header_row_1based=3)
    drug_col = resolve_col(df12, "Active Ingredient")
    cat_col = resolve_col(df12, "Cat #")
    sup_col = resolve_col(df12, "Supplier")
    donor_cols = [resolve_col(df12, f"SALS {i}") for i in range(1, 17)]

    df12 = df12.loc[df12[drug_col].notna()].copy()
    for c in donor_cols:
        df12[c] = pd.to_numeric(df12[c], errors="coerce")

    dmso_row = df12.loc[df12[drug_col].astype(str).str.strip() == "DMSO"]
    untreated_row = df12.loc[df12[drug_col].astype(str).str.strip() == "Untreated"]
    assert len(dmso_row) == 1, "Expected exactly 1 DMSO control row in Table 12"
    dmso_vec = dmso_row.iloc[0][donor_cols].to_numpy(dtype=float)
    untr_vec = untreated_row.iloc[0][donor_cols].to_numpy(dtype=float)

    active_df = df12.loc[~df12[drug_col].astype(str).str.strip().isin(["DMSO", "Untreated"])].copy()
    assert len(active_df) == 107, f"Expected 107 active compounds, got {len(active_df)}"

    records = []
    donor_profiles = {}
    for _, row in active_df.iterrows():
        name = str(row[drug_col]).strip()
        vec = row[donor_cols].to_numpy(dtype=float)
        mask = ~np.isnan(vec) & ~np.isnan(dmso_vec)
        n_donors = int(mask.sum())
        v_sub = vec[mask]
        d_sub = dmso_vec[mask]
        diff = v_sub - d_sub

        t_paired, p_paired_2s = stats.ttest_rel(v_sub, d_sub)
        p_paired_1s = float(p_paired_2s / 2.0) if t_paired > 0 else float(1.0 - p_paired_2s / 2.0)
        w_stat, p_wilcox_2s = stats.wilcoxon(diff, alternative="two-sided", method="exact")
        _, p_wilcox_gt = stats.wilcoxon(diff, alternative="greater", method="exact")
        t_raw, p_raw_2s = stats.ttest_1samp(v_sub, 0.0)

        lodo_means = [float(np.mean(np.delete(diff, i))) for i in range(n_donors)]
        lodo_p2s = [
            float(stats.ttest_rel(np.delete(v_sub, i), np.delete(d_sub, i))[1])
            for i in range(n_donors)
        ]

        records.append({
            "drug_name": name,
            "carbon_id": BATCH4_DRUGS.get(name, ""),
            "catalog_no": str(row[cat_col]),
            "supplier": str(row[sup_col]),
            "n_donors": n_donors,
            "mean_paired_vs_dmso_days": float(np.mean(diff)),
            "sd_paired_vs_dmso_days": float(np.std(diff, ddof=1)),
            "median_paired_vs_dmso_days": float(np.median(diff)),
            "iqr_paired_vs_dmso_days": float(np.percentile(diff, 75) - np.percentile(diff, 25)),
            "mean_raw_table12_days": float(np.mean(v_sub)),
            "responders_gt_dmso_n": int(np.sum(diff > 0)),
            "responders_gt_dmso_pct": float(100.0 * np.mean(diff > 0)),
            "responders_gt_1day_vs_dmso_n": int(np.sum(diff >= 1.0)),
            "negative_lines_vs_dmso_n": int(np.sum(diff < 0)),
            "paired_t_stat": float(t_paired),
            "paired_p_2s": float(p_paired_2s),
            "paired_p_1s_greater": p_paired_1s,
            "wilcoxon_stat": float(w_stat),
            "wilcoxon_exact_p_2s": float(p_wilcox_2s),
            "wilcoxon_exact_p_1s_greater": float(p_wilcox_gt),
            "raw_1samp_t_stat": float(t_raw),
            "raw_1samp_p_2s": float(p_raw_2s),
            "lodo_min_mean_diff_days": float(np.min(lodo_means)),
            "lodo_max_mean_diff_days": float(np.max(lodo_means)),
            "lodo_max_p_2s": float(np.max(lodo_p2s)),
        })
        if name in BATCH4_DRUGS:
            donor_profiles[name] = {
                donor_cols[i]: {
                    "raw_days": None if np.isnan(vec[i]) else round(float(vec[i]), 6),
                    "dmso_days": round(float(dmso_vec[i]), 6),
                    "paired_diff_days": None if np.isnan(vec[i]) else round(float(vec[i] - dmso_vec[i]), 6),
                }
                for i in range(16)
            }

    res_df = pd.DataFrame(records)
    res_df["bh_fdr_q_2s"] = multipletests(res_df["paired_p_2s"], method="fdr_bh")[1]
    res_df["bh_fdr_q_1s_greater"] = multipletests(res_df["paired_p_1s_greater"], method="fdr_bh")[1]
    res_df["wilcoxon_bh_fdr_q_2s"] = multipletests(res_df["wilcoxon_exact_p_2s"], method="fdr_bh")[1]
    res_df = res_df.sort_values("mean_paired_vs_dmso_days", ascending=False).reset_index(drop=True)
    res_df["rank_by_paired_mean"] = np.arange(1, len(res_df) + 1)
    res_df["rank_by_paired_p2s"] = res_df["paired_p_2s"].rank(method="min").astype(int)

    ctrl_meta = {
        "dmso_mean_days": float(np.mean(dmso_vec)),
        "dmso_sd_days": float(np.std(dmso_vec, ddof=1)),
        "untreated_mean_days": float(np.mean(untr_vec)),
        "untreated_vs_dmso_paired_p2s": float(stats.ttest_rel(untr_vec, dmso_vec)[1]),
        "donor_profiles_batch4": donor_profiles,
    }
    return res_df, ctrl_meta


def analyze_rnaseq_reversal(xlsx_path: Path) -> dict:
    df4 = read_xlsx_sparse_safe(xlsx_path, "Table 4", header_row_1based=3)
    df9 = read_xlsx_sparse_safe(xlsx_path, "Table 9", header_row_1based=3)
    df11 = read_xlsx_sparse_safe(xlsx_path, "Table 11", header_row_1based=5)
    df7 = read_xlsx_sparse_safe(xlsx_path, "Table 7", header_row_1based=3)

    for df in (df4, df9):
        ens_c = resolve_col(df, "Ensemb_Gene_ID")
        sym_c = resolve_col(df, "HGNC_Symbol")
        fc_c = resolve_col(df, "Fold_Change_Log2")
        p_c = resolve_col(df, "P-value")
        q_c = resolve_col(df, "Adjusted P-value")
        df[fc_c] = pd.to_numeric(df[fc_c], errors="coerce")
        df[p_c] = pd.to_numeric(df[p_c], errors="coerce")
        df[q_c] = pd.to_numeric(df[q_c], errors="coerce")
        df.dropna(subset=[ens_c, fc_c], inplace=True)

    ens4 = resolve_col(df4, "Ensemb_Gene_ID")
    sym4 = resolve_col(df4, "HGNC_Symbol")
    fc4 = resolve_col(df4, "Fold_Change_Log2")
    q4 = resolve_col(df4, "Adjusted P-value")

    ens9 = resolve_col(df9, "Ensemb_Gene_ID")
    sym9 = resolve_col(df9, "HGNC_Symbol")
    fc9 = resolve_col(df9, "Fold_Change_Log2")
    q9 = resolve_col(df9, "Adjusted P-value")

    merged = pd.merge(
        df4[[ens4, sym4, fc4, q4]].rename(columns={ens4: "ensg", sym4: "symbol", fc4: "log2fc_sals", q4: "fdr_sals"}),
        df9[[ens9, fc9, q9]].rename(columns={ens9: "ensg", fc9: "log2fc_rilu", q9: "fdr_rilu"}),
        on="ensg",
        how="inner",
    )

    sig_both = merged.loc[(merged["fdr_sals"] < 0.05) & (merged["fdr_rilu"] < 0.05)].copy()
    opp_all = int(np.sum(np.sign(merged["log2fc_sals"]) == -np.sign(merged["log2fc_rilu"])))
    opp_sig = int(np.sum(np.sign(sig_both["log2fc_sals"]) == -np.sign(sig_both["log2fc_rilu"])))

    rho_all, p_rho_all = stats.spearmanr(merged["log2fc_sals"], merged["log2fc_rilu"])
    binom_all_p = float(stats.binomtest(opp_all, len(merged), 0.5, alternative="greater").pvalue) if len(merged) else 1.0
    binom_sig_p = float(stats.binomtest(opp_sig, len(sig_both), 0.5, alternative="greater").pvalue) if len(sig_both) else 1.0

    # GO reversal table 11
    nes_sals_c = resolve_col(df11, "SALS vs Control")
    nes_rilu_c = resolve_col(df11, "Riluzole Treated vs DMSO")
    id_c = resolve_col(df11, "ID")
    desc_c = resolve_col(df11, "Description")
    df11_clean = df11.loc[df11[id_c].astype(str).str.startswith("GO:")].copy()
    df11_clean[nes_sals_c] = pd.to_numeric(df11_clean[nes_sals_c], errors="coerce")
    df11_clean[nes_rilu_c] = pd.to_numeric(df11_clean[nes_rilu_c], errors="coerce")
    df11_clean = df11_clean.dropna(subset=[nes_sals_c, nes_rilu_c])
    go_reversed_n = int(np.sum(np.sign(df11_clean[nes_sals_c]) == -np.sign(df11_clean[nes_rilu_c])))

    target_genes = [
        "KCNN1", "NEFH", "PKM", "SCN8A", "SCN1A", "UNC13A", "STMN2",
        "JAK1", "JAK2", "STAT1", "STAT3", "AAK1", "PIKFYVE",
        "PPP1R15A", "PPP1R15B", "SIGMAR1", "GRIN2B", "HTR2A", "ATF4", "DDIT3",
    ]
    gene_hits = {}
    for g in target_genes:
        r4 = df4.loc[df4[sym4].astype(str).str.upper() == g]
        r9 = df9.loc[df9[sym9].astype(str).str.upper() == g]
        if not r4.empty or not r9.empty:
            gene_hits[g] = {
                "sals_vs_ctrl": None if r4.empty else {
                    "log2fc": float(r4.iloc[0][fc4]),
                    "fdr": float(r4.iloc[0][q4]),
                },
                "riluzole_vs_dmso": None if r9.empty else {
                    "log2fc": float(r9.iloc[0][fc9]),
                    "fdr": float(r9.iloc[0][q9]),
                },
            }

    g7_col = resolve_col(df7, "Genes")
    q7_col = resolve_col(df7, "Adjusted P-value")
    df7[q7_col] = pd.to_numeric(df7[q7_col], errors="coerce")
    cryptic_splicing = df7.dropna(subset=[g7_col, q7_col])[[g7_col, q7_col]].to_dict(orient="records")

    return {
        "n_sals_vs_ctrl_rows_table4": int(len(df4)),
        "n_sals_vs_ctrl_fdr05": int((df4[q4] < 0.05).sum()),
        "n_riluzole_vs_dmso_rows_table9": int(len(df9)),
        "n_riluzole_vs_dmso_fdr05": int((df9[q9] < 0.05).sum()),
        "n_overlapping_genes_t4_t9": int(len(merged)),
        "n_opposite_sign_overlap_all": opp_all,
        "opposite_sign_pct_all": float(100.0 * opp_all / max(len(merged), 1)),
        "binom_reversal_p_all": binom_all_p,
        "spearman_r_sals_vs_riluzole": None if np.isnan(rho_all) else float(rho_all),
        "spearman_p_sals_vs_riluzole": None if np.isnan(p_rho_all) else float(p_rho_all),
        "n_both_fdr05": int(len(sig_both)),
        "n_both_fdr05_opposite_sign": opp_sig,
        "binom_reversal_p_both_fdr05": binom_sig_p,
        "table11_go_sets_total": int(len(df11_clean)),
        "table11_go_sets_reversed_n": go_reversed_n,
        "top5_riluzole_degs": df9.nsmallest(5, q9)[[sym9, fc9, q9]].to_dict(orient="records"),
        "target_gene_hits": gene_hits,
        "table7_unc13a_stmn2_splicing": cryptic_splicing,
    }


def main() -> None:
    xlsx_path = resolve_dataset_path("DS005_BYE", verify_hash=True)
    res_df, ctrl_meta = analyze_table12(xlsx_path)
    rnaseq_summary = analyze_rnaseq_reversal(xlsx_path)

    res_df.to_csv(OUT_DIR / "bye2025_107drugs_reanalysis.csv", index=False)
    b4_df = res_df.loc[res_df["carbon_id"] != ""].copy()
    b4_df.to_csv(OUT_DIR / "bye2025_batch4_summary.csv", index=False)

    payload = {
        "dataset_id": "DS005_BYE",
        "sha256_verified": True,
        "screen_concentration_uM": 2.5,
        "n_active_drugs": int(len(res_df)),
        "n_fdr05_2s_hits": int((res_df["bh_fdr_q_2s"] < 0.05).sum()),
        "n_fdr05_1s_greater_hits": int((res_df["bh_fdr_q_1s_greater"] < 0.05).sum()),
        "controls": {k: v for k, v in ctrl_meta.items() if k != "donor_profiles_batch4"},
        "batch4_candidates": b4_df.to_dict(orient="records"),
        "donor_profiles_batch4": ctrl_meta["donor_profiles_batch4"],
        "rnaseq_and_splicing": rnaseq_summary,
    }
    (OUT_DIR / "bye2025_batch4_reanalysis.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(b4_df[[
        "carbon_id", "drug_name", "rank_by_paired_mean", "n_donors",
        "mean_paired_vs_dmso_days", "responders_gt_dmso_n",
        "paired_p_2s", "bh_fdr_q_2s", "wilcoxon_exact_p_2s", "lodo_max_p_2s"
    ]].to_string(index=False))
    print("RNA-seq summary:", json.dumps({k: v for k, v in rnaseq_summary.items() if not isinstance(v, (list, dict))}, indent=2))


if __name__ == "__main__":
    main()
