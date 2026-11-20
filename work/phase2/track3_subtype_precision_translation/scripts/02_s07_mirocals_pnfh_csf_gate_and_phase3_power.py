"""RUN-P2-T3-002: S07 MIROCALS 80th-Percentile CSF NEFH Gate Proteomic Dissection & Prospective Phase 3 Power."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from carbon_als.loaders import (  # noqa: E402
    assert_modality,
    assert_unique_donors,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase2" / "track3_subtype_precision_translation" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PANEL = [
    "NEFH", "NEFL", "NEFM", "MAPT", "UCHL1", "CHIT1", "GPNMB", "CHI3L1", "CHI3L2",
    "C1QA", "C1QB", "C3", "SERPINA3", "B2M", "CD14", "ICAM1", "VCAM1", "NPTX2", "NPTXR", "GRIA4",
]


def schoenfeld_phase3_design(
    hr: float,
    alpha_two_sided: float = 0.05,
    power: float = 0.90,
    alloc_ratio: float = 1.0,
    ctrl_21mo_event_prob: float = 0.36,
    lp_eligible_fraction: float = 0.70,
) -> dict[str, float | int]:
    """Exact Schoenfeld log-rank required deaths, randomized low-pNfH N, and total LP-screened N."""
    z_a = float(stats.norm.ppf(1.0 - alpha_two_sided / 2.0))
    z_b = float(stats.norm.ppf(power))
    p = alloc_ratio / (1.0 + alloc_ratio)
    d_events = math.ceil(((z_a + z_b) ** 2) / (p * (1.0 - p) * (math.log(hr) ** 2)))
    p_trt = 1.0 - ((1.0 - ctrl_21mo_event_prob) ** hr)
    avg_event_prob = p * p_trt + (1.0 - p) * ctrl_21mo_event_prob
    n_rand_raw = math.ceil(d_events / max(avg_event_prob, 0.05))
    n_rand = int(math.ceil(n_rand_raw / 0.92))  # 8% 21-month loss-to-followup allowance
    if n_rand % 2 == 1:
        n_rand += 1
    n_screened_lp = int(math.ceil(n_rand / lp_eligible_fraction))
    return {
        "assumed_hr": hr,
        "power": power,
        "required_deaths": int(d_events),
        "expected_21mo_event_rate_pooled": round(avg_event_prob, 4),
        "randomized_low_pnfh_n": n_rand,
        "screened_lp_patients_needed_at_70pct_pass": n_screened_lp,
    }


def analyze_cohort_nefh(mat: pd.DataFrame, status_s: pd.Series,als_labels: list[str], elapsed_s: pd.Series | None = None) -> dict:
    als_cols = status_s.loc[status_s.isin(als_labels)].index.tolist()
    if "NEFH" not in mat.index:
        return {"nefh_detected": False}
    nefh = pd.to_numeric(mat.loc["NEFH", als_cols], errors="coerce").dropna()
    if len(nefh) < 10:
        return {"nefh_detected": False, "n_non_missing": int(len(nefh))}

    q80 = float(nefh.quantile(0.80))
    low_ids = nefh.index[nefh <= q80].tolist()
    high_ids = nefh.index[nefh > q80].tolist()

    shifts: dict[str, dict] = {}
    for g in PANEL:
        if g not in mat.index:
            continue
        v_low = pd.to_numeric(mat.loc[g, low_ids], errors="coerce").dropna()
        v_high = pd.to_numeric(mat.loc[g, high_ids], errors="coerce").dropna()
        if len(v_low) >= 5 and len(v_high) >= 3:
            shifts[g] = {
                "n_low80": int(len(v_low)),
                "n_high20": int(len(v_high)),
                "diff_high20_minus_low80_log2": round(float(v_high.mean() - v_low.mean()), 4),
                "welch_p": float(stats.ttest_ind(v_high, v_low, equal_var=False).pvalue),
            }

    nefl_concordance: dict[str, float | int] = {}
    if "NEFL" in mat.index:
        both = pd.DataFrame({
            "NEFH": pd.to_numeric(mat.loc["NEFH", als_cols], errors="coerce"),
            "NEFL": pd.to_numeric(mat.loc["NEFL", als_cols], errors="coerce"),
        }).dropna()
        if len(both) >= 10:
            r_val, p_val = stats.pearsonr(both["NEFH"], both["NEFL"])
            rho_val, rho_p = stats.spearmanr(both["NEFH"], both["NEFL"])
            fh_hi = both["NEFH"] > float(both["NEFH"].quantile(0.80))
            fl_hi = both["NEFL"] > float(both["NEFL"].quantile(0.80))
            discord = int((fh_hi != fl_hi).sum())
            nefl_concordance = {
                "n_paired": int(len(both)),
                "pearson_r": round(float(r_val), 4),
                "pearson_p": float(p_val),
                "spearman_rho": round(float(rho_val), 4),
                "spearman_p": float(rho_p),
                "n_discordant_at_80th_pct": discord,
                "pct_misclassified_by_nefl_surrogate": round(100.0 * discord / len(both), 2),
                "pct_true_high_nefh_missed_by_nefl": round(100.0 * float((fh_hi & (~fl_hi)).sum()) / max(int(fh_hi.sum()), 1), 2),
            }

    dur_stats: dict[str, float | int] = {}
    if elapsed_s is not None:
        el_low = pd.to_numeric(elapsed_s.reindex(low_ids), errors="coerce").dropna()
        el_high = pd.to_numeric(elapsed_s.reindex(high_ids), errors="coerce").dropna()
        if len(el_low) >= 4 and len(el_high) >= 3:
            dur_stats = {
                "n_low80_evaluable": int(len(el_low)),
                "n_high20_evaluable": int(len(el_high)),
                "median_elapsed_yr_low80": round(float(el_low.median()), 3),
                "median_elapsed_yr_high20": round(float(el_high.median()), 3),
                "mwu_p": float(stats.mannwhitneyu(el_low, el_high, alternative="two-sided").pvalue),
            }

    return {
        "nefh_detected": True,
        "n_als_evaluated": int(len(nefh)),
        "q80_log2_cutoff": round(q80, 4),
        "n_low80_stratum": int(len(low_ids)),
        "n_high20_stratum": int(len(high_ids)),
        "nefl_surrogate_concordance": nefl_concordance,
        "elapsed_duration_by_stratum": dur_stats,
        "proteomic_shifts_high20_vs_low80": shifts,
    }


def main() -> None:
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    assert_modality("PROTEOMICS_CSF_TMT", "DS045_TRAUT")
    assert_modality("PROTEOMICS_CSF_DIA", "DS045_TRAUT")

    c1 = read_xlsx_sparse_safe(p45, "1-Cohort-SC Characteristics", 2)
    tmt = read_xlsx_sparse_safe(p45, "3-TMT-MS Raw Data", 2)
    assert_unique_donors(c1["Channel"].tolist(), "DS045_TMT_101")
    tmt["sym"] = tmt[resolve_col(tmt, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
    tmt_mat = np.log2(tmt.loc[tmt["sym"].isin(PANEL)].groupby("sym")[c1["Channel"].tolist()].first().apply(pd.to_numeric, errors="coerce").where(lambda x: x > 0))
    c1_idx = c1.set_index("Channel")
    elapsed_yr = pd.to_numeric(c1_idx["AgeAtSample"], errors="coerce") - pd.to_numeric(c1_idx["AgeOnset"], errors="coerce")

    c2 = read_xlsx_sparse_safe(p45, "2-Cohort-Exp Characteristics", 2)
    dia = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    c2["dia_col"] = c2["_unnamed_col_0"].astype(str).str.replace(r"\.2$", "", regex=True).str.replace(r"\.(\d+)$", r"-\1", regex=True)
    assert_unique_donors(c2["ID"].tolist(), "DS045_DIA_259")
    dia["sym"] = dia[resolve_col(dia, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
    dia_mat = dia.loc[dia["sym"].isin(PANEL)].groupby("sym")[c2["dia_col"].tolist()].first().apply(pd.to_numeric, errors="coerce")
    c2_idx = c2.set_index("dia_col")

    power_grid = [
        schoenfeld_phase3_design(hr=hr, power=pw)
        for hr in (0.52, 0.62, 0.64, 0.66, 0.68, 0.70)
        for pw in (0.80, 0.90)
    ]

    # Calibrate MIROCALS BioVendor log-normal from published Lancet 2025 Fig 2 counts (PMID:40354799):
    # <750 pg/mL LLOQ: n=19/220 (0 deaths); 750-3,700 pg/mL: n=154/220 (57 deaths, HR=0.52);
    # pooled <=3,700 pg/mL: n=173/220 (57/90 deaths, HR=0.57, p=0.037); >3,700 pg/mL: n=47/220 (33/90 deaths, HR=1.37, p=0.38).
    p_lloq = 19.0 / 220.0
    p_le3700 = 173.0 / 220.0
    p_gt3700 = 47.0 / 220.0
    z_750 = float(stats.norm.ppf(p_lloq))
    z_3700 = float(stats.norm.ppf(p_le3700))
    sigma_ln = (math.log(3700.0) - math.log(750.0)) / (z_3700 - z_750)
    mu_ln = math.log(3700.0) - z_3700 * sigma_ln
    # Observed 21-month mortality rate ratio from published death counts (33/47 = 70.21% vs 57/173 = 32.95% -> 2.131x)
    obs_event_rate_low = 57.0 / 173.0
    obs_event_rate_hi = 33.0 / 47.0
    rel_event_rate_hi_vs_low = obs_event_rate_hi / obs_event_rate_low

    offset_rows = []
    for k_slope, label in [
        (4.5, "unbridged_assay_4p5x_higher"),
        (1.8, "unbridged_assay_1p8x_higher"),
        (1.0, "calibrated_biovendor_or_p79_bridged"),
        (1.0 / 1.8, "unbridged_assay_1p8x_lower_eg_MSD"),
        (1.0 / 4.5, "unbridged_assay_4p5x_lower"),
    ]:
        eff_bv_cut = 3700.0 / k_slope
        elig_total = float(stats.norm.cdf((math.log(eff_bv_cut) - mu_ln) / sigma_ln))
        true_low_captured = min(elig_total, p_le3700) / p_le3700
        false_hi_admitted_frac_of_hi = max(0.0, elig_total - p_le3700) / p_gt3700
        n_low_in = min(elig_total, p_le3700)
        n_hi_in = max(0.0, elig_total - p_le3700)
        ev_share_hi = (n_hi_in * rel_event_rate_hi_vs_low) / max(n_low_in + n_hi_in * rel_event_rate_hi_vs_low, 1e-9)
        hr_dil_hi_null = math.exp((1.0 - ev_share_hi) * math.log(0.70) + ev_share_hi * math.log(1.00))
        hr_dil_hi_1p37 = math.exp((1.0 - ev_share_hi) * math.log(0.70) + ev_share_hi * math.log(1.37))
        pow_sup_hi_null = float(stats.norm.cdf(abs(math.log(hr_dil_hi_null)) * math.sqrt(247.0 * 0.25) - float(stats.norm.ppf(0.975))))
        pow_sup_hi_1p37 = float(stats.norm.cdf(abs(math.log(hr_dil_hi_1p37)) * math.sqrt(247.0 * 0.25) - float(stats.norm.ppf(0.975))))
        offset_rows.append({
            "platform_scenario": label,
            "assay_vs_biovendor_slope_k": round(k_slope, 4),
            "effective_biovendor_cutoff_pg_ml": round(eff_bv_cut, 1),
            "apparent_lp_eligible_fraction": round(elig_total, 4),
            "eligible_le3700_captured_pct": round(100.0 * true_low_captured, 2),
            "gt3700_stratum_admitted_pct": round(100.0 * false_hi_admitted_frac_of_hi, 2),
            "diluted_hr_if_true_low_0p70_and_hi_null_1p00": round(hr_dil_hi_null, 4),
            "one_sided_sup_power_247_deaths_hi_null_pct": round(100.0 * pow_sup_hi_null, 2),
            "diluted_hr_if_true_low_0p70_and_hi_1p37": round(hr_dil_hi_1p37, 4),
            "one_sided_sup_power_247_deaths_hi_1p37_pct": round(100.0 * pow_sup_hi_1p37, 2),
        })

    out = {
        "analysis_run_id": "RUN-P2-T3-002",
        "proteomic_transformation_note": "Bottom-up tryptic CSF MS total NEFH/NEFL abundance (TMT log2-transformed; Emory n=51 overlaps 4-center DIA expansion n=259 in Trautwig et al. 2025 PMC12082929).",
        "tmt_emory_symptomatic_als": analyze_cohort_nefh(tmt_mat, c1_idx["Disease"], ["Sporadic", "C9orf72", "SOD1"], elapsed_yr),
        "tmt_emory_sporadic_only": analyze_cohort_nefh(tmt_mat, c1_idx["Disease"], ["Sporadic"], elapsed_yr),
        "dia_4center_symptomatic_als": analyze_cohort_nefh(dia_mat, c2_idx["SymptomStatus"], ["sALS", "C9orf72", "SOD1"]),
        "dia_4center_sals_only": analyze_cohort_nefh(dia_mat, c2_idx["SymptomStatus"], ["sALS"]),
        "prospective_phase3_schoenfeld_grid": power_grid,
        "mirocals_primary_and_platform_bridging_sensitivity": {
            "mirocals_lancet_2025_counts": {
                "n_total": 220, "deaths_total": 90,
                "n_lloq_lt750": 19, "deaths_lloq_lt750": 0,
                "n_low_750_3700": 154, "deaths_low_750_3700": 57, "hr_low_750_3700": 0.52, "p_low_750_3700": 0.016,
                "n_pooled_le3700": 173, "deaths_pooled_le3700": 57, "hr_pooled_le3700": 0.57, "p_pooled_le3700": 0.037,
                "n_high_gt3700": 47, "deaths_high_gt3700": 33, "hr_high_gt3700": 1.37, "p_high_gt3700": 0.38,
                "obs_death_share_gt3700_pct": round(100.0 * 33.0 / 90.0, 2),
                "obs_death_rate_ratio_gt3700_vs_le3700": round(rel_event_rate_hi_vs_low, 4),
                "cox_interaction_hr_per_pgml": 1.0003, "cox_interaction_p": 0.0011,
                "alsfrsr_slope_interaction_f_1_216": 3.95, "alsfrsr_slope_interaction_p": 0.048,
            },
            "al_khleifat_2026_nested_lrt": {
                "tricals_pnfh_r": 0.357, "tricals_pnfh_r2": 0.127,
                "dchi2_add_pnfh_to_tricals": 44.39,
                "dchi2_pnfh_x_trt": 14.24,
                "dchi2_tricals_x_trt": 4.76, "lrt_p_tricals_x_trt": 0.029, "wald_p_tricals_x_trt": 0.025,
            },
            "mirocals_lognormal_fit": {"mu_ln": round(mu_ln, 4), "sigma_ln": round(sigma_ln, 4)},
            "hypothetical_unbridged_3700_platform_offset_sensitivity": offset_rows,
        },
    }
    (OUT_DIR / "run_p2_t3_002_s07_mirocals_pnfh_gate.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("SAVED run_p2_t3_002_s07_mirocals_pnfh_gate.json")


if __name__ == "__main__":
    main()
