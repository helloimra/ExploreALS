"""RUN-B5-001: Primary donor-aware reanalysis of DS005_BYE (Bye 2025) & DS_ROPALS (Morimoto 2023)."""
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

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_5" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_bye2025_reanalysis() -> dict[str, object]:
    bye_path = resolve_dataset_path("DS005_BYE", verify_hash=True)
    t12 = read_xlsx_sparse_safe(bye_path, "Table 12", header_row_1based=3)
    drug_col = resolve_col(t12, "Active Ingredient")
    cat_col = resolve_col(t12, "Cat #")
    sup_col = resolve_col(t12, "Supplier")
    donor_cols = [resolve_col(t12, f"SALS {i}") for i in range(1, 17)]

    t12 = t12[t12[drug_col].notna()].copy()
    t12[drug_col] = t12[drug_col].astype(str).str.strip()
    for dc in donor_cols:
        t12[dc] = pd.to_numeric(t12[dc], errors="coerce")

    dmso_row = t12.loc[t12[drug_col] == "DMSO", donor_cols].iloc[0].to_numpy(dtype=float)
    active_df = t12.loc[~t12[drug_col].isin(["DMSO", "Untreated"])].copy()
    assert len(active_df) == 107, f"Expected 107 active drugs, got {len(active_df)}"

    records: list[dict[str, object]] = []
    for _, row in active_df.iterrows():
        vals = row[donor_cols].to_numpy(dtype=float)
        mask = np.isfinite(vals) & np.isfinite(dmso_row)
        raw_v = vals[mask]
        diff = raw_v - dmso_row[mask]
        n = int(mask.sum())
        mean_diff = float(np.mean(diff))
        sd_diff = float(np.std(diff, ddof=1))
        t_res = stats.ttest_1samp(diff, popmean=0.0)
        t_stat = float(t_res.statistic)
        p_2s = float(t_res.pvalue)
        p_1s_rescue = float(stats.t.sf(t_stat, df=n - 1))
        w_res = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided", method="exact")
        records.append({
            "drug": str(row[drug_col]),
            "catalog": str(row[cat_col]),
            "supplier": str(row[sup_col]),
            "n_donors": n,
            "n_pos_paired_dmso": int(np.sum(diff > 0)),
            "responder_rate_paired": float(np.mean(diff > 0)),
            "n_pos_raw": int(np.sum(raw_v > 0)),
            "mean_raw_days": float(np.mean(raw_v)),
            "mean_paired_dmso_days": mean_diff,
            "sd_paired_dmso_days": sd_diff,
            "median_paired_dmso_days": float(np.median(diff)),
            "t_stat_paired": t_stat,
            "p_ttest_2s": p_2s,
            "p_ttest_1s_rescue": p_1s_rescue,
            "wilcoxon_stat": float(w_res.statistic),
            "p_wilcoxon_exact_2s": float(w_res.pvalue),
        })

    res_df = pd.DataFrame(records).sort_values("mean_paired_dmso_days", ascending=False).reset_index(drop=True)
    res_df["rank_107_by_paired_mean"] = np.arange(1, len(res_df) + 1)
    res_df["q_bh_107_ttest_2s"] = multipletests(res_df["p_ttest_2s"], method="fdr_bh")[1]
    res_df["q_bh_107_ttest_1s_rescue"] = multipletests(res_df["p_ttest_1s_rescue"], method="fdr_bh")[1]
    res_df["q_bh_107_wilcoxon_2s"] = multipletests(res_df["p_wilcoxon_exact_2s"], method="fdr_bh")[1]
    res_df.to_csv(OUT_DIR / "bye2025_full_107drug_reanalysis.csv", index=False)

    focus_drugs = [
        "Retigabine", "Ceftriaxone", "Memantine", "Ropinirole", "Furosemide", "Perampanel",
        "Riluzole", "Lamotrigine", "Gabapentin", "Primidone", "Valproic acid", "Nimodipine",
        "Ranolazine", "Dalfampridine", "Mexiletine", "Benzocaine", "Flecainide",
    ]
    focus_out: dict[str, object] = {}
    for fd in focus_drugs:
        hit = res_df.loc[res_df["drug"].str.lower() == fd.lower()]
        focus_out[fd] = hit.iloc[0].to_dict() if not hit.empty else {"present_in_bye2025_107": False}

    target_genes = [
        "KCNQ2", "KCNQ3", "SCN8A", "SCN1A", "GRIA1", "GRIA2", "GRIN1", "GRIN2A",
        "GRIN2B", "SLC1A2", "DRD2", "DRD3", "SLC12A2", "SLC12A5",
    ]
    deg_tables: dict[str, dict[str, object]] = {}
    for sheet_label, key in [("Table 4", "sals_vs_ctrl_ipsc_mn"), ("Table 9", "riluzole_vs_dmso_ipsc_mn")]:
        dt = read_xlsx_sparse_safe(bye_path, sheet_label, header_row_1based=3)
        sym_col = resolve_col(dt, "HGNC_Symbol")
        lfc_col = resolve_col(dt, "Fold_Change_Log2")
        p_col = resolve_col(dt, "P-value")
        q_col = resolve_col(dt, "Adjusted P-value")
        sub = dt[dt[sym_col].astype(str).str.strip().isin(target_genes)]
        deg_tables[key] = {
            str(r[sym_col]).strip(): {
                "log2FC": float(r[lfc_col]),
                "p_value": float(r[p_col]),
                "adj_p_value": float(r[q_col]),
            }
            for _, r in sub.iterrows()
        }
    return {
        "n_active_drugs": int(len(res_df)),
        "n_fdr05_two_sided": int((res_df["q_bh_107_ttest_2s"] < 0.05).sum()),
        "dmso_donor_mean_days": float(np.mean(dmso_row)),
        "focus_compounds": focus_out,
        "bye2025_deg_lookup": deg_tables,
    }


def run_ropals_reanalysis() -> dict[str, object]:
    rop_path = resolve_dataset_path("DS_ROPALS", verify_hash=True)
    ae_df = read_xlsx_sparse_safe(rop_path, "Sheet1", header_row_1based=5)
    var_col = resolve_col(ae_df, "Variable")
    db_rop_col = resolve_col(ae_df, "(n = 13)")
    db_pbo_col = resolve_col(ae_df, "(n = 7)")
    ole_rop_col = resolve_col(ae_df, "(n = 12)")
    ole_pbo_col = resolve_col(ae_df, "(n = 5)")
    ae_rows = {
        str(r[var_col]).strip(): {
            "db_ropinirole_n13": str(r[db_rop_col]),
            "db_placebo_n7": str(r[db_pbo_col]),
            "ole_ropinirole_n12": str(r[ole_rop_col]),
            "ole_explacebo_n5": str(r[ole_pbo_col]),
        }
        for _, r in ae_df.iterrows()
        if pd.notna(r[var_col]) and pd.notna(r[db_rop_col])
    }

    mw_free_base = 260.38  # CHEMBL566 / CID:5095 C16H24N2O
    mw_hcl_salt = 296.84   # CHEMBL1200580 / CID:68727 C16H25ClN2O
    fup_requip_label = 0.60  # ~40% plasma protein binding (FDA Requip XL NDA 022008 label Sec 12.3)
    csf_pg_ml = {"geomean": 17884.0, "ci95_low": 14186.0, "ci95_high": 22547.0, "n": 13, "dose_mg_day": 16}
    plasma_pg_ml_visits = [
        {"visit_row": "16mg_row1_n18", "geomean_pg_ml": 22593.0, "n": 18},
        {"visit_row": "16mg_row2_n17", "geomean_pg_ml": 20058.0, "n": 17},
        {"visit_row": "16mg_row3_n14", "geomean_pg_ml": 22510.0, "n": 14},
    ]
    csf_nm_freebase = csf_pg_ml["geomean"] / mw_free_base / 1000.0 * 1000.0  # pg/mL / (g/mol) = pM -> /1000 = nM
    # Exact dimensional check: 17884 pg/mL = 17.884 ug/L; (17.884 ug/L) / (260.38 g/mol) = 0.0686842 uM = 68.6842 nM
    csf_nm_fb = (csf_pg_ml["geomean"] * 1e-3) / mw_free_base * 1e3
    csf_ci_nm_fb = [
        (csf_pg_ml["ci95_low"] * 1e-3) / mw_free_base * 1e3,
        (csf_pg_ml["ci95_high"] * 1e-3) / mw_free_base * 1e3,
    ]
    csf_nm_hcl = (csf_pg_ml["geomean"] * 1e-3) / mw_hcl_salt * 1e3
    plasma_conv = []
    for pv in plasma_pg_ml_visits:
        tot_nm = (pv["geomean_pg_ml"] * 1e-3) / mw_free_base * 1e3
        plasma_conv.append({**pv, "total_plasma_nM": tot_nm, "est_unbound_plasma_nM_fup060": tot_nm * fup_requip_label})

    return {
        "mw_free_base_g_mol": mw_free_base,
        "mw_hcl_salt_g_mol": mw_hcl_salt,
        "csf_16mg_wk24_n13": {
            "reported_pg_ml": csf_pg_ml["geomean"],
            "reported_ng_ml": csf_pg_ml["geomean"] / 1000.0,
            "author_discussion_unit_typo_note": "Morimoto 2023 Discussion wrote '~18 nmol/L', mis-stating 17.884 ng/mL (17,884 pg/mL in Table S3) as nmol/L.",
            "molar_total_csf_nM_freebase": csf_nm_fb,
            "molar_total_csf_ci95_nM_freebase": csf_ci_nm_fb,
            "molar_total_csf_nM_if_hcl_calibrated": csf_nm_hcl,
            "ratio_bye2025_2500nM_to_csf_nM": 2500.0 / csf_nm_fb,
            "ratio_nonD2_1000nM_to_csf_nM": 1000.0 / csf_nm_fb,
            "ratio_nonD2_10000nM_to_csf_nM": 10000.0 / csf_nm_fb,
        },
        "plasma_16mg_predose_rows": plasma_conv,
        "adverse_events_summary": ae_rows,
    }


if __name__ == "__main__":
    bye_summary = run_bye2025_reanalysis()
    rop_summary = run_ropals_reanalysis()
    (OUT_DIR / "bye2025_batch5_and_excitability_summary.json").write_text(
        json.dumps(bye_summary, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "ropals_pk_ae_reanalysis.json").write_text(
        json.dumps(rop_summary, indent=2), encoding="utf-8"
    )
    print("RUN-B5-001 complete. Active drugs:", bye_summary["n_active_drugs"], "FDR<0.05 (2s):", bye_summary["n_fdr05_two_sided"])
    for k, v in bye_summary["focus_compounds"].items():
        if "mean_paired_dmso_days" in v:
            print(f"  {k:16s} rank={v['rank_107_by_paired_mean']:3d} n={v['n_donors']} resp={v['n_pos_paired_dmso']}/{v['n_donors']} "
                  f"mean={v['mean_paired_dmso_days']:+.3f}d p2s={v['p_ttest_2s']:.4g} q2s={v['q_bh_107_ttest_2s']:.4g} pW={v['p_wilcoxon_exact_2s']:.4g}")
        else:
            print(f"  {k:16s} NOT IN BYE 2025 107-DRUG LIBRARY")
    print("ROPALS CSF nM (free base):", round(rop_summary["csf_16mg_wk24_n13"]["molar_total_csf_nM_freebase"], 3))
