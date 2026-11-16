"""RUN-B6-003: Bye 2025 107-drug x 16-donor iPSC-MN screen & unbound CNS PK audit.

Recomputes exact paired one-sample t-tests, Wilcoxon signed-rank p-values,
107-drug BH-FDR q-values, responder fractions, RNA-seq DEGs, and human unbound
CNS exposure margins for S01-S04 (plus Riluzole calibration control).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.phase1_batches.batch_runner_utils import (
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_6" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    bye_xlsx = resolve_dataset_path("DS005_BYE")
    t12 = read_xlsx_sparse_safe(bye_xlsx, "Table 12", header_row_1based=3)
    col_drug = resolve_col(t12, "Active Ingredient")
    col_cat = resolve_col(t12, "Cat #")
    col_sup = resolve_col(t12, "Supplier")
    donor_cols = [resolve_col(t12, f"SALS {i}") for i in range(1, 17)]

    t12 = t12[t12[col_drug].notna()].copy()
    dmso_row = t12[t12[col_drug].astype(str).str.strip() == "DMSO"].iloc[0]
    dmso_vec = np.array([pd.to_numeric(dmso_row[c], errors="coerce") for c in donor_cols], dtype=float)

    screen_rows = []
    for rec in t12.to_dict(orient="records"):
        drug = str(rec[col_drug]).strip()
        if drug in {"DMSO", "Untreated"}:
            continue
        raw_vals = np.array([pd.to_numeric(rec[c], errors="coerce") for c in donor_cols], dtype=float)
        paired_diff = raw_vals - dmso_vec
        valid = paired_diff[np.isfinite(paired_diff)]
        n_val = len(valid)
        if n_val < 3:
            continue
        t_stat, p_two = stats.ttest_1samp(valid, 0.0)
        p_one = float(p_two / 2.0) if t_stat > 0 else float(1.0 - p_two / 2.0)
        nz = valid[valid != 0.0]
        w_two = float(stats.wilcoxon(nz, alternative="two-sided").pvalue) if len(nz) >= 3 else 1.0
        w_one = float(stats.wilcoxon(nz, alternative="greater").pvalue) if len(nz) >= 3 else 1.0
        screen_rows.append({
            "drug": drug,
            "cat_no": str(rec[col_cat]),
            "supplier": str(rec[col_sup]),
            "n_valid": int(n_val),
            "n_gt0": int(np.sum(valid > 0.0)),
            "n_ge1d": int(np.sum(valid >= 1.0)),
            "mean_days_vs_dmso": float(np.mean(valid)),
            "raw_mean_days": float(np.nanmean(raw_vals)),
            "sd_days": float(np.std(valid, ddof=1)),
            "median_days_vs_dmso": float(np.median(valid)),
            "iqr_days": float(np.percentile(valid, 75) - np.percentile(valid, 25)),
            "min_days": float(np.min(valid)),
            "max_days": float(np.max(valid)),
            "t_stat": float(t_stat),
            "p_t_two": float(p_two),
            "p_t_one_gt": p_one,
            "p_wilcox_two": w_two,
            "p_wilcox_one_gt": w_one,
        })

    df_scr = pd.DataFrame(screen_rows)
    df_scr["fdr_bh_t_two"] = multipletests(df_scr["p_t_two"], method="fdr_bh")[1]
    df_scr["fdr_bh_t_one"] = multipletests(df_scr["p_t_one_gt"], method="fdr_bh")[1]
    df_scr["fdr_bh_wilcox_two"] = multipletests(df_scr["p_wilcox_two"], method="fdr_bh")[1]
    df_scr = df_scr.sort_values("mean_days_vs_dmso", ascending=False).reset_index(drop=True)
    df_scr["rank_by_mean_rescue"] = np.arange(1, len(df_scr) + 1)
    df_scr.to_csv(OUT_DIR / "part_b_bye2025_full_107drug_screen.csv", index=False)

    focus_drugs = ["Riluzole", "Baricitinib", "Dexmedetomidine", "CuATSM", "Mycophenolate mofetil", "Tamoxifen", "Methylcobalamin"]
    focus_df = df_scr[df_scr["drug"].isin(focus_drugs)].copy()

    # Check Bye 2025 Table 4 (SALS vs Ctrl) & Table 9 (Riluzole vs DMSO) RNA-seq DEGs
    deg_genes = [
        "ADRA2A", "ADRA2B", "ADRA2C", "SOD1", "CCS", "IMPDH1", "IMPDH2",
        "ESR1", "ESR2", "PRKCA", "PRKCB", "SARM1", "STMN2", "DNAJB2", "SNPH",
        "AGAP2", "AP1G2", "BRSK2", "KIFC2", "MIB2", "MYO18A", "ZNF783", "CAPG",
    ]
    deg_hits = {}
    for tbl, label in [("Table 4", "sals_vs_ctrl"), ("Table 9", "riluzole_vs_dmso")]:
        dt = read_xlsx_sparse_safe(bye_xlsx, tbl, header_row_1based=3)
        cs = resolve_col(dt, "HGNC_Symbol")
        cf = resolve_col(dt, "Fold_Change_Log2")
        cp = resolve_col(dt, "P-value")
        cq = resolve_col(dt, "Adjusted P-value")
        sub = dt[dt[cs].isin(deg_genes)]
        deg_hits[label] = [
            {"gene": str(r[cs]), "log2fc": float(r[cf]), "p": float(r[cp]), "padj": float(r[cq])}
            for r in sub.to_dict(orient="records")
        ]

    # Quantitative human unbound CNS exposure vs 2.5 uM (2500 nM) screen & target Ki/IC50
    pk_models = [
        {
            "carbon_id": "S01", "drug": "Dexmedetomidine", "mw_free_base": 200.28,
            "clinical_regimen": "IV ICU infusion 0.2-0.7 ug/kg/h (Precedex label)",
            "total_plasma_nM": 6.24, "plasma_fu": 0.06, "unbound_plasma_nM": 0.374,
            "est_kpuu_cns": 0.85, "est_unbound_cns_nM": 0.318,
            "bye_screen_conc_nM": 2500.0, "screen_over_unbound_cns_ratio": round(2500.0 / 0.318, 1),
            "primary_target": "ADRA2A", "primary_ki_ic50_nM": 1.65,
            "pk_safety_verdict": "Dose-limiting ICU sedation, hypotension & bradycardia at ~0.3-0.6 nM unbound; 2500 nM iPSC screen is ~7860x above tolerated human unbound CNS exposure.",
        },
        {
            "carbon_id": "S02", "drug": "CuATSM", "mw_free_base": 321.90,
            "clinical_regimen": "72 mg/day oral suspension (Phase 2/3 NCT04082832)",
            "total_plasma_nM": 950.0, "plasma_fu": 0.08, "unbound_plasma_nM": 76.0,
            "est_kpuu_cns": 0.70, "est_unbound_cns_nM": 53.2,
            "bye_screen_conc_nM": 2500.0, "screen_over_unbound_cns_ratio": round(2500.0 / 53.2, 1),
            "primary_target": "Cu delivery / radical trapping", "primary_ki_ic50_nM": 200.0,
            "pk_safety_verdict": "CNS-penetrant PET-verified radiotracer scaffold, but failed randomized placebo-controlled Phase 2/3 ALS trial NCT04082832 across ALSFRS-R, ECAS, and survival.",
        },
        {
            "carbon_id": "S03", "drug": "Mycophenolate mofetil (active MPA)", "mw_free_base": 320.34,
            "clinical_regimen": "1000 mg PO BID CellCept (MPA Cavg ~12.5 uM total)",
            "total_plasma_nM": 12500.0, "plasma_fu": 0.02, "unbound_plasma_nM": 250.0,
            "est_kpuu_cns": 0.08, "est_unbound_cns_nM": 20.0,
            "bye_screen_conc_nM": 2500.0, "screen_over_unbound_cns_ratio": round(2500.0 / 20.0, 1),
            "primary_target": "IMPDH2 / IMPDH1", "primary_ki_ic50_nM": 20.0,
            "pk_safety_verdict": "97-99% albumin bound + active BBB organic-anion efflux yields ~125x deficit vs 2.5 uM neuronal screen, while systemic lymphoid IMPDH blockade causes Boxed Warning PML/opportunistic infections & failed clinical ALS neuroimmune regimens.",
        },
        {
            "carbon_id": "S04", "drug": "Tamoxifen", "mw_free_base": 371.51,
            "clinical_regimen": "40 mg/day PO (ALS Phase 2 dose; Css total ~540 nM)",
            "total_plasma_nM": 540.0, "plasma_fu": 0.008, "unbound_plasma_nM": 4.32,
            "est_kpuu_cns": 0.60, "est_unbound_cns_nM": 2.59,
            "bye_screen_conc_nM": 2500.0, "screen_over_unbound_cns_ratio": round(2500.0 / 2.59, 1),
            "primary_target": "ESR1 (Ki ~3 nM) vs PKC/autophagy (~2000-5000 nM)", "primary_ki_ic50_nM": 3000.0,
            "pk_safety_verdict": "fu <1% yields ~2.6 nM unbound brain vs 2500 nM screen (~965x gap); 2.5 uM hits cationic amphiphilic phospholipidosis/PKC range, and human ALS trials (NCT00214110, NCT01257581) showed no durable efficacy with Boxed Warning thromboembolism.",
        },
    ]

    out_payload = {
        "n_total_drugs_screened": int(len(df_scr)),
        "n_fdr_t_two_lt_005": int((df_scr["fdr_bh_t_two"] < 0.05).sum()),
        "focus_drugs_stats": focus_df.to_dict(orient="records"),
        "bye_rnaseq_degs": deg_hits,
        "unbound_cns_pk_models": pk_models,
    }
    (OUT_DIR / "part_b_bye2025_and_pk_summary.json").write_text(json.dumps(out_payload, indent=2), encoding="utf-8")
    print(f"Saved Bye 2025 screen ({len(df_scr)} drugs) and unbound PK audit.")


if __name__ == "__main__":
    main()
