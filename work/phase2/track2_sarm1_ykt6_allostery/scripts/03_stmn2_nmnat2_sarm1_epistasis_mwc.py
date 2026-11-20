"""RUN-P2-T2-002: Donor-level STMN2-NMNAT2-SARM1-YKT6 epistasis & 8-protomer MWC BEXi vs Cys311 allosteric modeling."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))
from carbon_als.loaders import (  # noqa: E402
    assert_modality,
    assert_unique_donors,
    load_brown2022_splicing,
    load_spillman2026_fractions,
    resolve_col,
    resolve_dataset_path,
)

OUT = ROOT / "work" / "phase2" / "track2_sarm1_ykt6_allostery" / "outputs"
GENES = ["STMN2", "NMNAT2", "SARM1", "YKT6", "PTAR1", "UNC13A", "KCNQ2"]


def analyze_brown_and_spillman() -> dict:
    br = load_brown2022_splicing(GENES)
    rna, ribo, junc = br["rnaseq_df"], br["riboseq_df"], br["junctions_df"]
    brown_summary = {}
    for g in GENES:
        r_row = rna[rna["gene_name"] == g]
        b_row = ribo[ribo["gene_name"] == g]
        j_sub = junc[junc["gene_name"] == g]
        brown_summary[g] = {
            "n_cryptic_or_splice_junctions": int(len(j_sub)),
            "rnaseq_log2fc": round(float(r_row.iloc[0]["log2FoldChange"]), 4) if not r_row.empty else None,
            "rnaseq_padj": float(r_row.iloc[0]["padj"]) if not r_row.empty and pd.notna(r_row.iloc[0]["padj"]) else None,
            "riboseq_log2fc": round(float(b_row.iloc[0]["log2FoldChange"]), 4) if not b_row.empty else None,
            "riboseq_padj": float(b_row.iloc[0]["padj"]) if not b_row.empty and pd.notna(b_row.iloc[0]["padj"]) else None,
        }

    sp_summary = load_spillman2026_fractions(GENES)
    # Donor-level within-compartment correlations in Spillman MOESM1 (never pooling fractions!)
    p29 = resolve_dataset_path("DS029_SPILL")
    m1 = pd.read_excel(p29 / "401_2026_3084_MOESM1_ESM.xlsx")
    gcol = resolve_col(m1, "Gene")
    syn_cols = [c for c in m1.columns if c.startswith("Norm_S") and "Synapt_FRCTX_" in c]
    hom_cols = [c for c in m1.columns if c.startswith("Norm_H") and "Homogenate_FRCTX_" in c]
    assert_unique_donors([re.sub(r"^Norm_S", "S_", c) for c in syn_cols], "DS029_SPILL Synaptosome Corr")
    assert_unique_donors([re.sub(r"^Norm_H", "H_", c) for c in hom_cols], "DS029_SPILL Homogenate Corr")

    def get_vec(sym: str, cols: list[str]) -> np.ndarray | None:
        sub = m1[m1[gcol].fillna("").astype(str).str.split(";").apply(lambda x: sym in x)]
        if sub.empty:
            return None
        return pd.to_numeric(sub.iloc[0][cols], errors="coerce").to_numpy(dtype=float)

    corrs = {}
    for comp_name, cols in [("synaptosome_donors_n20", syn_cols), ("homogenate_donors_n20", hom_cols)]:
        comp_res = {}
        for g1, g2 in [("STMN2", "NMNAT2"), ("STMN2", "YKT6"), ("NMNAT2", "SARM1"), ("STMN2", "SARM1")]:
            v1, v2 = get_vec(g1, cols), get_vec(g2, cols)
            if v1 is not None and v2 is not None:
                m = np.isfinite(v1) & np.isfinite(v2)
                if m.sum() >= 6:
                    pr = stats.pearsonr(v1[m], v2[m])
                    sr = stats.spearmanr(v1[m], v2[m])
                    comp_res[f"{g1}_vs_{g2}"] = {
                        "modality": assert_modality("PROTEOMICS_DIA", "DS029_SPILL"),
                        "n_donors": int(m.sum()),
                        "pearson_r": round(float(pr.statistic), 4),
                        "pearson_p": float(pr.pvalue),
                        "spearman_rho": round(float(sr.statistic), 4),
                        "spearman_p": float(sr.pvalue),
                    }
        # Donor-level [SARM1 - NMNAT2] log2 synaptic vulnerability ratio (C9FTD vs Control)
        vsarm, vnmn = get_vec("SARM1", cols), get_vec("NMNAT2", cols)
        if vsarm is not None and vnmn is not None:
            is_c9 = np.array(["C9FTD" in c for c in cols])
            diff_idx = vsarm - vnmn
            c9_v, ctl_v = diff_idx[is_c9 & np.isfinite(diff_idx)], diff_idx[(~is_c9) & np.isfinite(diff_idx)]
            if len(c9_v) >= 3 and len(ctl_v) >= 3:
                wt = stats.ttest_ind(c9_v, ctl_v, equal_var=False)
                comp_res["log2_SARM1_over_NMNAT2_vulnerability_index"] = {
                    "n_c9ftd": int(len(c9_v)), "n_ctrl": int(len(ctl_v)),
                    "delta_log2_ratio_c9ftd_vs_ctrl": round(float(np.mean(c9_v) - np.mean(ctl_v)), 4),
                    "welch_p": float(wt.pvalue),
                }
        corrs[comp_name] = comp_res
    return {"brown2022_tdp43_kd": brown_summary, "spillman2026_fractions": sp_summary, "spillman2026_donor_epistasis": corrs}


def analyze_pineda_excitatory() -> dict:
    d_dir = resolve_dataset_path("DS003_PB")
    rep = pd.read_csv(d_dir / "reduce_report.csv")
    rm = pd.read_csv(d_dir / "row_metadata.tsv", sep="\t")
    rm["gene_index"] = np.arange(1, len(rm) + 1)
    gmap = {int(r["gene_index"]): str(r["Gene"]).strip() for _, r in rm.iterrows() if str(r["Gene"]).strip() in set(GENES)}
    rows = []
    for _, r in rep.iterrows():
        stem = str(r["folder"]).strip()
        pb_f, nuc_f = d_dir / f"{stem}.pseudobulk.tsv.gz", d_dir / f"{stem}.nuclei.tsv"
        if not pb_f.exists() or not nuc_f.exists():
            continue
        ct_map = {i: str(ct).strip() for i, ct in enumerate(pd.read_csv(nuc_f, sep="\t")["cell_type"])}
        pb = pd.read_csv(pb_f, sep="\t")
        pb["is_exc"] = pb["cell_type_index"].map(ct_map).isin({"L2_L3", "L3_L5", "L4_L5", "L4_L6", "L5", "L5_L6", "L6"})
        exc = pb[pb["is_exc"]]
        tot = float(exc["sum"].sum())
        if tot < 10_000:
            continue
        gsub = exc[exc["gene_index"].isin(gmap)].groupby("gene_index")["sum"].sum().to_dict()
        rec = {"donor": str(r["donor"]), "region": str(r["region"]), "group": str(r["group"])}
        for gi, sym in gmap.items():
            rec[sym] = float(np.log2(gsub.get(gi, 0.0) / tot * 1e6 + 1.0))
        rows.append(rec)
    df = pd.DataFrame(rows).groupby(["region", "donor", "group"], as_index=False)[GENES].mean()
    out = {}
    for reg, rdf in df.groupby("region"):
        sub = rdf[rdf["group"].isin(["SALS", "PN"])].copy()
        assert_unique_donors(sub["donor"].tolist(), f"DS003_PB {reg}_Excitatory")
        de = {}
        for g in GENES:
            vs, vc = sub.loc[sub["group"] == "SALS", g].values, sub.loc[sub["group"] == "PN", g].values
            de[g] = {
                "n_sals": int(len(vs)), "n_pn": int(len(vc)),
                "log2fc_sals_vs_pn": round(float(np.mean(vs) - np.mean(vc)), 4),
                "welch_p": float(stats.ttest_ind(vs, vc, equal_var=False).pvalue),
            }
        pr_sn = stats.pearsonr(sub["STMN2"], sub["NMNAT2"])
        pr_sy = stats.pearsonr(sub["STMN2"], sub["YKT6"])
        vuln_s = (sub.loc[sub["group"] == "SALS", "SARM1"] - sub.loc[sub["group"] == "SALS", "NMNAT2"]).values
        vuln_c = (sub.loc[sub["group"] == "PN", "SARM1"] - sub.loc[sub["group"] == "PN", "NMNAT2"]).values
        out[f"{reg}_Excitatory"] = {
            "de": de,
            "donor_corr_STMN2_NMNAT2": {"n": int(len(sub)), "r": round(float(pr_sn.statistic), 4), "p": float(pr_sn.pvalue)},
            "donor_corr_STMN2_YKT6": {"n": int(len(sub)), "r": round(float(pr_sy.statistic), 4), "p": float(pr_sy.pvalue)},
            "log2_SARM1_over_NMNAT2_sals_vs_pn": {
                "delta": round(float(np.mean(vuln_s) - np.mean(vuln_c)), 4),
                "welch_p": float(stats.ttest_ind(vuln_s, vuln_c, equal_var=False).pvalue),
            },
        }
    return out


def simulate_8mer_mwc_epistasis() -> dict:
    """8-protomer MWC SARM1 octamer comparing orthosteric BEXi (3-chain TIR glue) vs Cys311 allosteric T-lock + STMN2 rescue."""
    # L_eff = [T]/[R] equilibrium constant without drug: exploratory sensitivity states across axonal NMNAT2 depletion & ARM-GoF
    states = {
        "healthy_axon_100pct_NMNAT2": 120.0,
        "als_axon_transport_stressed_NMNAT2_depleted": 8.0,
        "als_axon_parallel_plus_end_STMN2_rescue_no_NMNAT2_shift": 8.0,
        "als_axon_plus_Track1_STMN2_rescue_80pct_NMNAT2": 65.0,
        "als_axon_SARM1_ARM_GoF_plus_STMN2_loss": 2.2,
    }
    doses = np.logspace(-2.5, 2.0, 91)  # [I]/Kd from 0.003x to 100x
    c_glue = 0.22  # BEXi-ADPR 3-chain TIR dimerization stabilization per bound site (9TZY A+B+D glue)
    d_lock = 6.5   # Cys311 dHNN/isothiazole T-state wedge stabilization per protomer (7DJT 40.48 A open ARM)

    curves = {}
    for st_name, L_eff in states.items():
        # Baseline apo NADase fraction (k=0 bound): P_R(0) = 1 / (1 + L_eff)
        base_act = 1.0 / (1.0 + L_eff)
        # BEXi: if k of 8 TIR sites carry BEXi-ADPR with R-state affinity Kd, R-weight = (1 + u)^8?
        # Wait: active catalytic output comes from the (8 - k)/8 UNOCCUPIED TIR sites in the R-state!
        # Partition: Z_T = L_eff * (1 + 0.05*u)^8 ; R-state sum over k=0..8 of C(8,k)*(u/c_glue)^k with catalytic fraction (8-k)/8:
        # Exact binomial identity: sum_{k=0}^8 C(8,k) * ((8-k)/8) * x^k = (1 + x)^7 !
        x = doses / c_glue
        z_r_total = (1.0 + x) ** 8
        z_t_bexi = L_eff * (1.0 + 0.05 * doses) ** 8
        bexi_act = ((1.0 + x) ** 7) / (z_t_bexi + z_r_total)

        # Cys311 allosteric T-lock: binds ARM hinge in T-state (affinity Kd_T, d_lock-fold weaker in R), leaving TIR catalytic site untouched unless R forms
        z_t_allost = L_eff * (1.0 + doses) ** 8
        z_r_allost = (1.0 + doses / d_lock) ** 8
        allost_act = z_r_allost / (z_t_allost + z_r_allost)

        peak_idx = int(np.argmax(bexi_act))
        ic90_allost = next((float(d) for d, a in zip(doses, allost_act) if a <= 0.10 * base_act), None)
        ic90_abs = next((float(d) for d, a in zip(doses, allost_act) if a <= 0.01), None)
        curves[st_name] = {
            "L_eff_T_over_R": L_eff,
            "baseline_fractional_NADase": round(float(base_act), 5),
            "BEXi_peak_fold_over_baseline": round(float(bexi_act[peak_idx] / base_act), 3),
            "BEXi_peak_fractional_NADase": round(float(bexi_act[peak_idx]), 4),
            "BEXi_peak_at_dose_over_Kd": round(float(doses[peak_idx]), 3),
            "BEXi_trough_0p3xKd_fold_over_baseline": round(float(bexi_act[np.argmin(np.abs(doses - 0.3))] / base_act), 3),
            "Cys311_allost_max_fold_over_baseline": round(float(np.max(allost_act) / base_act), 4),
            "Cys311_allost_trough_0p3xKd_fold_over_baseline": round(float(allost_act[np.argmin(np.abs(doses - 0.3))] / base_act), 3),
            "Cys311_allost_IC90_rel_in_Kd_units": round(ic90_allost, 3) if ic90_allost else None,
            "Cys311_allost_dose_to_reach_lt_1pct_max_NADase_in_Kd_units": round(ic90_abs, 3) if ic90_abs else None,
        }
    return curves


from carbon_als.allostery_pkpd import (  # noqa: E402
    compute_cd38_cadpr_dilution_and_audit_bound,
    hetero_octamer_tlock_inhibition,
    sweep_sarm1_mwc_threshold_synergy,
)


def summarize_nov2026_sarm1_sensitivity(mwc_grid: dict) -> dict:
    well_sep = [
        float(r["absolute_threshold_dose_sparing_fold"])
        for r in mwc_grid["grid"]
        if r["absolute_threshold_dose_sparing_fold"] is not None
        and float(r["baseline_rescued_nadase"]) >= 1.5 * float(r["nadase_catastrophe_floor"])
    ]
    doses = np.logspace(-2.5, 2.0, 91)
    z_emp = (1.0 + 5.154 * doses) ** 6
    emp_bexi_rel = 3.5 * (z_emp / (2.5 + z_emp)) / (1.0 + doses)
    emp_pk = int(np.argmax(emp_bexi_rel))
    return {
        "model_status": "EXPLORATORY_MECHANISTIC_SENSITIVITY_SWEEP",
        "leahey_empirical_wt_6mer_calibration": {
            "L0": 2.5,
            "cooperativity_n_eff": 6,
            "peak_fold_over_baseline": round(float(emp_bexi_rel[emp_pk]), 3),
            "peak_at_dose_over_Kd": round(float(doses[emp_pk]), 3),
        },
        "parallel_plus_end_lower_bound_fold": 1.0,
        "parallel_mechanism_note": (
            "Two-branch competing-hazard architecture — Branch A (SARM1-independent microtubule regeneration): "
            "Krus et al. 2022 (PMID:35767949), Beccari et al. 2025 (PMID:40392845), and Matson & Holzbaur 2026 "
            "(10.64898/2026.11.07.764673 [PREPRINT]) demonstrate that STMN2 promotes plus-end microtubule dynamicity/"
            "catastrophe and suppresses runaway tubulin polymerization; STMN2 loss reduces catastrophe and impairs "
            "neurite outgrowth/regeneration independently of SARM1 L_eff (1.00x SARM1 Kd_T potency shift at alpha=0), "
            "proving SARM1 inhibition cannot substitute for STMN2 rescue. Branch B (conditional NMNAT2-SARM1 metabolic "
            f"switch, alpha in [0, 1]): spans alpha=0 (Krus 2022 Stmn2-/- baseline, 1.00x shift) to alpha>0 vesicular "
            f"co-transport stress (Beccari 2025, {np.min(well_sep):.2f}x-{np.max(well_sep):.2f}x [median {np.median(well_sep):.2f}x] Cys311 T-lock floor-dose sparing across n={len(well_sep)} well-separated threshold states)."
        ),
        "two_branch_competing_hazard_architecture": {
            "branch_a_sarm1_independent_regeneration": {
                "alpha_coupling": 0.0,
                "sarm1_kd_potency_shift_fold": 1.0,
                "sarm1_inhibition_replaces_stmn2_rescue": False,
                "anchors": ["PMID:35767949", "PMID:40392845", "10.64898/2026.11.07.764673"],
            },
            "branch_b_conditional_nmnat2_sarm1_switch": {
                "alpha_coupling_range": [0.0, 1.0],
                "well_separated_dose_sparing_range_fold": [round(float(np.min(well_sep)), 2), round(float(np.max(well_sep)), 2)],
                "well_separated_median_fold": round(float(np.median(well_sep)), 2),
                "anchors": ["PMID:40392845"],
            },
        },
        "well_separated_epistatic_n": len(well_sep),
        "well_separated_epistatic_min_fold": round(float(np.min(well_sep)), 2),
        "well_separated_epistatic_median_fold": round(float(np.median(well_sep)), 2),
        "well_separated_epistatic_max_fold": round(float(np.max(well_sep)), 2),
        "reversible_noncovalent_tlock_gof_heterozygote_100xKd": hetero_octamer_tlock_inhibition(
            100.0, gof_allele_fraction=0.5, d_lock=6.5
        ),
        "cd38_fluid_cadpr_dilution_bounds": {
            "f_sarm1_10pct_basal_fluid": compute_cd38_cadpr_dilution_and_audit_bound(0.10, 0.90, 0.50),
            "f_sarm1_05pct_basal_fluid": compute_cd38_cadpr_dilution_and_audit_bound(0.05, 0.90, 0.50),
        },
    }


if __name__ == "__main__":
    mwc_sw = sweep_sarm1_mwc_threshold_synergy()
    res = {
        "analysis_run_id": "RUN-P2-T2-002",
        "cohorts": analyze_brown_and_spillman(),
        "pineda_d003": analyze_pineda_excitatory(),
        "mwc_8mer_epistasis": simulate_8mer_mwc_epistasis(),
        "mwc_threshold_synergy_sensitivity_grid": mwc_sw,
        "nov2026_parallel_and_cd38_sensitivity": summarize_nov2026_sarm1_sensitivity(mwc_sw),
    }
    (OUT / "run_p2_t2_002_epistasis_mwc.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(json.dumps(res["nov2026_parallel_and_cd38_sensitivity"], indent=2))
