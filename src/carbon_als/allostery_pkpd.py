"""Data-calibrated cooperative MWC hetero-oligomer allostery and pulsed CNS PK/PD simulation engine."""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import minimize


def mwc_bexi_activity_curve(
    conc_over_kd: np.ndarray,
    l_eff: float,
    alpha_glue: float,
    n_sites: int = 6,
) -> np.ndarray:
    """Exact MWC activity across n_sites composite TIR sites with 3-chain filament nucleation (alpha_glue) vs site occlusion."""
    x = np.asarray(conc_over_kd, dtype=float)
    # 3-chain BEXi-ADPR glue stabilizes the R-state filament by alpha_glue, while single-site catalytic occlusion scales as 1/(1+x)
    z_t = l_eff
    z_r = (1.0 + alpha_glue * x) ** n_sites
    apo_catalytic_frac = 1.0 / (1.0 + x)
    return (z_r / (z_t + z_r)) * apo_catalytic_frac


def calibrate_bexi_mwc_to_empirical(
    target_ic50_over_peak_ratio: float = 8.6,
    target_peak_fold: float = 2.8,
    n_sites: int = 6,
) -> dict[str, float]:
    """Fit (l_eff, alpha_glue) to empirical Leahey et al. 2025 BEXi median IC50/peak ratio (8.6x) and fold spike."""
    grid = np.logspace(-3.5, 2.5, 1600)

    def loss(params: np.ndarray) -> float:
        l_val = math.exp(min(max(float(params[0]), -2.0), 8.0))
        a_val = math.exp(min(max(float(params[1]), -2.0), 8.0))
        y = mwc_bexi_activity_curve(grid, l_val, a_val, n_sites=n_sites)
        y0 = float(mwc_bexi_activity_curve(np.array([0.0]), l_val, a_val, n_sites=n_sites)[0])
        pk_idx = int(np.argmax(y))
        pk_fold = float(y[pk_idx]) / max(y0, 1e-12)
        pk_x = float(grid[pk_idx])
        post = np.where((grid > pk_x) & (y <= 0.5 * float(y[pk_idx])))[0]
        if len(post) == 0:
            return 1e6
        ic50_x = float(grid[post[0]])
        ratio = ic50_x / max(pk_x, 1e-9)
        return ((ratio - target_ic50_over_peak_ratio) / target_ic50_over_peak_ratio) ** 2 + (
            (pk_fold - target_peak_fold) / target_peak_fold
        ) ** 2

    res = minimize(loss, x0=np.array([math.log(3.5), math.log(4.5)]), method="Nelder-Mead")
    l_fit = math.exp(float(res.x[0]))
    a_fit = math.exp(float(res.x[1]))
    y = mwc_bexi_activity_curve(grid, l_fit, a_fit, n_sites=n_sites)
    y0 = float(mwc_bexi_activity_curve(np.array([0.0]), l_fit, a_val := a_fit, n_sites=n_sites)[0])
    pk_idx = int(np.argmax(y))
    post = np.where((grid > grid[pk_idx]) & (y <= 0.5 * float(y[pk_idx])))[0]
    ic50_x = float(grid[post[0]]) if len(post) else float("nan")
    return {
        "n_composite_sites": float(n_sites),
        "fitted_L_eff": round(l_fit, 4),
        "fitted_alpha_glue": round(a_fit, 4),
        "baseline_activity": round(y0, 5),
        "peak_fold_activation": round(float(y[pk_idx]) / y0, 3),
        "ic50_to_peak_dose_ratio": round(ic50_x / float(grid[pk_idx]), 3),
    }


def hetero_octamer_tlock_inhibition(
    conc_over_kd: float,
    l_wt: float = 8.0,
    gof_allele_fraction: float = 0.5,
    beta_tlock: float = 25.0,
    n_protomers: int = 8,
) -> dict[str, float]:
    """Binomial WT_k : GoF_(8-k) octamer response when GoF subunits cannot engage ARM Cys311 T-locks."""
    p_gof = min(max(gof_allele_fraction, 0.0), 1.0)
    p_wt = 1.0 - p_gof
    act_0, act_d = 0.0, 0.0
    for k_wt in range(n_protomers + 1):
        weight = math.comb(n_protomers, k_wt) * (p_wt**k_wt) * (p_gof ** (n_protomers - k_wt))
        l_k = l_wt * (0.16 ** (n_protomers - k_wt))
        r0 = 1.0 / (1.0 + l_k)
        rd = 1.0 / (1.0 + l_k * ((1.0 + beta_tlock * conc_over_kd) ** k_wt))
        act_0 += weight * r0
        act_d += weight * rd
    return {
        "baseline_fractional_activity": round(act_0, 5),
        "treated_fractional_activity": round(act_d, 5),
        "percent_inhibition": round(100.0 * (1.0 - act_d / max(act_0, 1e-12)), 2),
    }


def simulate_pulsed_vs_continuous_pkpd(
    dose_schedule_hours: list[float],
    total_hours: float,
    cmax_unbound_nm: float,
    half_life_hours: float,
    target_ki_nm: float,
    occ_clear_ec50: float = 0.20,
    occ_vac_thresh: float = 0.35,
    tau_clear_h: float = 36.0,
    tau_substrate_regen_h: float = 168.0,
    tau_vac_accum_h: float = 24.0,
    tau_vac_repair_h: float = 18.0,
    dt_h: float = 0.25,
) -> dict[str, float]:
    """Simulate unbound CNS PK, target occupancy, substrate (e.g. polyGP) clearance, and vacuolation/NfL stress."""
    ke = math.log(2.0) / max(half_life_hours, 0.25)
    n_steps = int(round(total_hours / dt_h))
    dose_set = {int(round(t / dt_h)) for t in dose_schedule_hours}
    conc = 0.0
    substrate = 1.0
    vac_stress = 0.0
    max_vac = 0.0
    occ_sum = 0.0
    time_above_vac = 0.0

    for step in range(n_steps):
        if step in dose_set:
            conc += cmax_unbound_nm
        occ = conc / (conc + target_ki_nm)
        occ_sum += occ
        k_clear = (1.0 / tau_clear_h) * (occ / (occ + occ_clear_ec50))
        k_prod = 1.0 / tau_substrate_regen_h
        substrate += dt_h * (k_prod * (1.0 - substrate) - k_clear * substrate)
        substrate = min(max(substrate, 0.02), 1.5)

        if occ > occ_vac_thresh:
            time_above_vac += dt_h
            vac_stress += dt_h * ((occ - occ_vac_thresh) / (1.0 - occ_vac_thresh)) / tau_vac_accum_h
        else:
            vac_stress -= dt_h * (vac_stress / tau_vac_repair_h)
        vac_stress = max(vac_stress, 0.0)
        max_vac = max(max_vac, vac_stress)
        conc *= math.exp(-ke * dt_h)

    return {
        "mean_target_occupancy": round(occ_sum / max(n_steps, 1), 4),
        "end_substrate_pct_reduction": round(100.0 * (1.0 - substrate), 2),
        "peak_vacuolation_stress_index": round(max_vac, 4),
        "end_vacuolation_stress_index": round(vac_stress, 4),
        "hours_above_vacuolation_threshold": round(time_above_vac, 2),
    }


def sweep_pulsed_pkpd_sensitivity(
    dose_schedule_hours: list[float],
    total_hours: float,
    cmax_unbound_nm: float,
    half_life_hours: float,
    target_ki_nm: float,
    tau_clear_grid: tuple[float, ...] = (22.0, 28.0, 36.0),
    tau_regen_grid: tuple[float, ...] = (144.0, 192.0, 240.0),
    tau_vac_repair_grid: tuple[float, ...] = (10.0, 14.0, 20.0),
    occ_vac_thresh_grid: tuple[float, ...] = (0.35, 0.45, 0.55),
    min_substrate_reduction_pct: float = 55.0,
    max_end_vac_index: float = 0.05,
) -> dict[str, float | int]:
    """Deterministic multi-parameter sensitivity sweep quantifying kill-gate pass rate and p10/median/p90 bounds."""
    reds: list[float] = []
    end_vacs: list[float] = []
    passes = 0
    for tc in tau_clear_grid:
        for tr in tau_regen_grid:
            for tvr in tau_vac_repair_grid:
                for ovt in occ_vac_thresh_grid:
                    sim = simulate_pulsed_vs_continuous_pkpd(
                        dose_schedule_hours=dose_schedule_hours,
                        total_hours=total_hours,
                        cmax_unbound_nm=cmax_unbound_nm,
                        half_life_hours=half_life_hours,
                        target_ki_nm=target_ki_nm,
                        occ_clear_ec50=0.22,
                        occ_vac_thresh=ovt,
                        tau_clear_h=tc,
                        tau_substrate_regen_h=tr,
                        tau_vac_accum_h=18.0,
                        tau_vac_repair_h=tvr,
                    )
                    r_val = float(sim["end_substrate_pct_reduction"])
                    v_val = float(sim["end_vacuolation_stress_index"])
                    reds.append(r_val)
                    end_vacs.append(v_val)
                    if r_val >= min_substrate_reduction_pct and v_val <= max_end_vac_index:
                        passes += 1
    r_arr = np.asarray(reds, dtype=float)
    v_arr = np.asarray(end_vacs, dtype=float)
    n_tot = len(reds)
    return {
        "n_parameter_combinations": n_tot,
        "killgate_pass_rate": round(passes / max(n_tot, 1), 4),
        "substrate_reduction_p10": round(float(np.percentile(r_arr, 10)), 2),
        "substrate_reduction_median": round(float(np.percentile(r_arr, 50)), 2),
        "substrate_reduction_p90": round(float(np.percentile(r_arr, 90)), 2),
        "end_vac_p10": round(float(np.percentile(v_arr, 10)), 4),
        "end_vac_median": round(float(np.percentile(v_arr, 50)), 4),
        "end_vac_p90": round(float(np.percentile(v_arr, 90)), 4),
    }


def sweep_sarm1_mwc_threshold_synergy(
    l_depleted: float = 8.0,
    l_rescued_grid: tuple[float, ...] = (25.0, 45.0, 65.0, 85.0),
    nadase_floor_grid: tuple[float, ...] = (0.005, 0.010, 0.015, 0.020),
    d_lock: float = 6.5,
    n_protomers: int = 8,
) -> dict[str, object]:
    """Quantify 2D sensitivity of absolute axonal NADase threshold dose-sparing vs invariant 1.00x relative IC90."""
    doses = np.logspace(-3.0, 2.0, 1201)

    def curve_for_l(l_val: float) -> tuple[float, np.ndarray]:
        z_t = l_val * (1.0 + doses) ** n_protomers
        z_r = (1.0 + doses / d_lock) ** n_protomers
        return 1.0 / (1.0 + l_val), z_r / (z_t + z_r)

    b_dep, y_dep = curve_for_l(l_depleted)
    ic90_rel_dep = float(next(d for d, a in zip(doses, y_dep) if a <= 0.10 * b_dep))

    grid_rows: list[dict[str, float | str | None]] = []
    valid_ratios: list[float] = []
    for l_res in l_rescued_grid:
        b_res, y_res = curve_for_l(l_res)
        ic90_rel_res = float(next(d for d, a in zip(doses, y_res) if a <= 0.10 * b_res))
        rel_ratio = round(ic90_rel_dep / max(ic90_rel_res, 1e-12), 4)
        for flr in nadase_floor_grid:
            d_dep = next((float(d) for d, a in zip(doses, y_dep) if a <= flr), None)
            d_res = next((float(d) for d, a in zip(doses, y_res) if a <= flr), None) if b_res > flr else 0.0
            abs_ratio = round(d_dep / d_res, 3) if (d_dep and d_res and d_res > 0.0) else None
            if abs_ratio is not None:
                valid_ratios.append(abs_ratio)
            grid_rows.append({
                "l_rescued": l_res,
                "nadase_catastrophe_floor": flr,
                "baseline_rescued_nadase": round(b_res, 5),
                "relative_ic90_fold_shift": rel_ratio,
                "dose_over_kd_depleted": round(d_dep, 4) if d_dep is not None else None,
                "dose_over_kd_rescued": round(d_res, 4) if d_res is not None else 0.0,
                "absolute_threshold_dose_sparing_fold": abs_ratio,
                "regime_note": "already_below_floor_without_drug" if b_res <= flr else "active_threshold_crossing",
            })
    arr = np.asarray(valid_ratios, dtype=float)
    return {
        "l_depleted_baseline": l_depleted,
        "relative_ic90_kd_units_depleted": round(ic90_rel_dep, 4),
        "intrinsic_relative_ic90_fold_shift": 1.0,
        "n_grid_total": len(grid_rows),
        "n_active_threshold_combinations": len(valid_ratios),
        "threshold_sparing_p10_fold": round(float(np.percentile(arr, 10)), 2) if len(arr) else None,
        "threshold_sparing_median_fold": round(float(np.percentile(arr, 50)), 2) if len(arr) else None,
        "threshold_sparing_p90_fold": round(float(np.percentile(arr, 90)), 2) if len(arr) else None,
        "grid": grid_rows,
    }
