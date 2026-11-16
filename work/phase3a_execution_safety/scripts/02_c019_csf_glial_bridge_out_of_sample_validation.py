"""RUN-P3A-002 (v2): Deconfounded OOF, center/genotype-stratified & rs3831317-neutral validation of the C019 4-component (5-protein) CSF Bridge."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (SRC, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _csf_bridge_helpers import BRIDGE_SYMS, eval_contrast, extract_oh2023_header_resolved, fit_bridge_params, roc_auc_mw, score_bridge  # noqa: E402
from _offtarget_helpers import sanitize_for_strict_json  # noqa: E402
from carbon_als.loaders import assert_modality, assert_unique_donors, read_xlsx_sparse_safe, resolve_col, resolve_dataset_path  # noqa: E402

OUT_DIR = ROOT / "work" / "phase3a_execution_safety" / "outputs"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert_modality("PROTEOMICS_CSF_DIA", "DS045_TRAUT")
    assert_modality("PROTEOMICS_CSF_TMT", "DS045_TRAUT")
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    c2 = read_xlsx_sparse_safe(p45, "2-Cohort-Exp Characteristics", 2)
    dia = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    c2["dia_col"] = c2["_unnamed_col_0"].astype(str).str.replace(r"\.2$", "", regex=True).str.replace(r"\.(\d+)$", r"-\1", regex=True)
    assert_unique_donors(c2["ID"].tolist(), "DS045_DIA_259")
    dia["sym"] = dia[resolve_col(dia, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
    dia_mat = dia.loc[dia["sym"].isin(BRIDGE_SYMS)].groupby("sym")[c2["dia_col"].tolist()].first().T
    dia_mat["status"] = c2.set_index("dia_col")["SymptomStatus"]
    dia_mat["bank"] = c2.set_index("dia_col")["TissueBank"]

    ctab = {f"{b}__{s}": int(n) for (b, s), n in dia_mat.groupby(["bank", "status"]).size().items()}
    em_df = dia_mat[dia_mat["bank"] == "Emory"].copy()
    ext_df = dia_mat[dia_mat["bank"] != "Emory"].copy()
    em_ctrl = em_df[em_df["status"] == "Control"]
    mgh_ctrl = ext_df[(ext_df["bank"] == "MGH") & (ext_df["status"] == "Control")]

    ctrl_drift = {}
    for g in BRIDGE_SYMS:
        e_v = pd.to_numeric(em_ctrl[g], errors="coerce").dropna()
        m_v = pd.to_numeric(mgh_ctrl[g], errors="coerce").dropna()
        ctrl_drift[g] = {
            "n_emory_ctrl": int(len(e_v)), "n_mgh_ctrl": int(len(m_v)),
            "mgh_minus_emory_log2": round(float(m_v.mean() - e_v.mean()), 4),
            "welch_p": float(stats.ttest_ind(m_v, e_v, equal_var=False).pvalue),
        }

    # Fit rs3831317-neutral calibrated Bridge (primary) + legacy uncalibrated max-z (sensitivity) on Emory Controls (n=54)
    em_fit = fit_bridge_params(em_df, em_df["status"] == "Control")
    em_sc_cal = score_bridge(em_df, em_fit, calibrated=True)
    em_sc_leg = score_bridge(em_df, em_fit, calibrated=False)
    ext_sc_cal = score_bridge(ext_df, em_fit, calibrated=True)
    ext_sc_leg = score_bridge(ext_df, em_fit, calibrated=False)
    em_z95 = float(em_fit["z_cut_95_ctrl"])

    # Exact denominator separation: pure MGH Controls (n=16) vs pooled External Controls (16 MGH + 2 WashU = 18) vs Emory (n=54)
    mgh_c_cal = ext_sc_cal[(ext_df["bank"] == "MGH") & (ext_df["status"] == "Control")]
    ext_c_cal = ext_sc_cal[ext_df["status"] == "Control"]
    em_c_cal = em_sc_cal[em_df["status"] == "Control"]
    mgh_offset_cal = float(mgh_c_cal.mean() - em_c_cal.mean())

    # Center-offset-adjusted external scores (subtracting MGH's baseline control drift from MGH samples only)
    ext_sc_center_adj = ext_sc_cal.copy()
    ext_sc_center_adj.loc[ext_df["bank"] == "MGH"] = ext_sc_center_adj.loc[ext_df["bank"] == "MGH"] - mgh_offset_cal

    # Leak-free 5-fold stratified OOF inside single-center Emory DIA (42 sALS vs 54 Control, n=96)
    em_sub = em_df[em_df["status"].isin(["sALS", "Control"])].copy()
    rng = np.random.default_rng(20261114)
    pos_idx = rng.permutation(em_sub.index[em_sub["status"] == "sALS"].to_numpy())
    neg_idx = rng.permutation(em_sub.index[em_sub["status"] == "Control"].to_numpy())
    oof_cal, oof_leg, oof_hit = pd.Series(index=em_sub.index, dtype=float), pd.Series(index=em_sub.index, dtype=float), pd.Series(index=em_sub.index, dtype=float)
    for k in range(5):
        te = np.concatenate([pos_idx[k::5], neg_idx[k::5]])
        tr_df, te_df = em_sub.drop(index=te), em_sub.loc[te]
        fk = fit_bridge_params(tr_df, tr_df["status"] == "Control")
        sk_cal = score_bridge(te_df, fk, calibrated=True)
        oof_cal.loc[te] = sk_cal
        oof_leg.loc[te] = score_bridge(te_df, fk, calibrated=False)
        oof_hit.loc[te] = (sk_cal > float(fk["z_cut_95_ctrl"])).astype(float)
    y_em = (em_sub["status"] == "sALS").astype(int).to_numpy()

    # Genotype-matched p80 cutoffs (sALS-to-sALS and all-ALS-to-all-ALS)
    em_sals_p80 = float(em_sc_cal[em_df["status"] == "sALS"].quantile(0.80))
    em_all_als_p80 = float(em_sc_cal[em_df["status"].isin(["sALS", "C9orf72", "SOD1"])].quantile(0.80))
    ext_als_mask = ext_df["status"].isin(["sALS", "C9orf72", "SOD1"])
    wu_df_mask = ext_df["bank"] == "WashU"
    mgh_df_mask = ext_df["bank"] == "MGH"

    # Technical cross-platform Emory TMTpro (N=101)
    c1 = read_xlsx_sparse_safe(p45, "1-Cohort-SC Characteristics", 2)
    tmt = read_xlsx_sparse_safe(p45, "3-TMT-MS Raw Data", 2)
    tmt["sym"] = tmt[resolve_col(tmt, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
    tmt_mat = tmt.loc[tmt["sym"].isin(BRIDGE_SYMS)].groupby("sym")[c1["Channel"].tolist()].first().T
    tmt_mat["status"] = c1.set_index("Channel")["Disease"]
    tmt_fit = fit_bridge_params(tmt_mat, tmt_mat["status"] == "Control")
    tmt_sc = score_bridge(tmt_mat, tmt_fit, calibrated=True)

    out = sanitize_for_strict_json({
        "analysis_run_id": "RUN-P3A-002",
        "evidence_basis": "MEASURED_HUMAN",
        "composite_definition": "4-component (5-protein) rs3831317-neutral calibrated Bridge: mean([z_chit_calibrated, z_GPNMB, z_CHI3L1, z_SERPINA3])",
        "pooled_ds045_center_audit": {
            "bank_by_status_counts": ctab,
            "mgh_vs_emory_healthy_control_drift": ctrl_drift,
            "bridge_ctrl_drift_pure_mgh_n16_minus_emory_n54_z": round(mgh_offset_cal, 4),
            "bridge_ctrl_drift_pure_mgh_n16_minus_emory_n54_welch_p": float(stats.ttest_ind(mgh_c_cal, em_c_cal, equal_var=False).pvalue),
            "bridge_ctrl_drift_pooled_ext_n18_minus_emory_n54_z": round(float(ext_c_cal.mean() - em_c_cal.mean()), 4),
            "bridge_ctrl_drift_pooled_ext_n18_minus_emory_n54_welch_p": float(stats.ttest_ind(ext_c_cal, em_c_cal, equal_var=False).pvalue),
            "legacy_pooled_ext_n18_minus_emory_n54_z": round(float(ext_sc_leg[ext_df["status"] == "Control"].mean() - em_sc_leg[em_df["status"] == "Control"].mean()), 4),
        },
        "within_emory_unconfounded_dia": {
            "sals_vs_ctrl_leak_free_5fold_oof": {
                "n_sals": int((y_em == 1).sum()), "n_ctrl": int((y_em == 0).sum()),
                "oof_roc_auc": round(roc_auc_mw(y_em, oof_cal.to_numpy()), 4),
                "oof_roc_auc_legacy_max_z": round(roc_auc_mw(y_em, oof_leg.to_numpy()), 4),
                "oof_welch_p": float(stats.ttest_ind(oof_cal[y_em == 1], oof_cal[y_em == 0], equal_var=False).pvalue),
                "oof_sensitivity_at_fold_z95": round(float(oof_hit[y_em == 1].mean()), 4),
                "oof_ctrl_fpr_at_fold_z95": round(float(oof_hit[y_em == 0].mean()), 4),
            },
            "all_symp_als_vs_ctrl": eval_contrast(em_sc_cal, em_df["status"].isin(["sALS", "C9orf72", "SOD1"]), em_df["status"] == "Control", em_z95),
            "c9_asymptomatic_vs_ctrl": eval_contrast(em_sc_cal, em_df["status"] == "C9orf72-Asymptomatic", em_df["status"] == "Control", em_z95),
        },
        "deconfounded_and_stratified_external_validation": {
            "confounding_disclosure": "In DS045 non-Emory samples (n=141), 57/57 symptomatic ALS come from UMilan (31, 0 Ctrl) + WashU (26, 2 Ctrl) with 86.0% (49/57) familial C9orf72/SOD1, while 16/18 Controls come from downward-shifted MGH (0 ALS). Therefore, Emory leak-free sALS OOF, within-WashU, C9 phenoconversion, and MGH-offset-adjusted AUCs are primary over raw pooled external AUC.",
            "within_washu_same_center_als_vs_non_als": eval_contrast(ext_sc_cal[wu_df_mask], ext_df.loc[wu_df_mask, "status"].isin(["sALS", "C9orf72", "SOD1"]), ~ext_df.loc[wu_df_mask, "status"].isin(["sALS", "C9orf72", "SOD1"]), em_z95),
            "within_washu_same_center_c9_symp_vs_c9_asym": eval_contrast(ext_sc_cal[wu_df_mask], ext_df.loc[wu_df_mask, "status"] == "C9orf72", ext_df.loc[wu_df_mask, "status"] == "C9orf72-Asymptomatic", em_z95),
            "within_mgh_same_center_asym_vs_ctrl_specificity": eval_contrast(ext_sc_cal[mgh_df_mask], ext_df.loc[mgh_df_mask, "status"].str.contains("Asymptomatic"), ext_df.loc[mgh_df_mask, "status"] == "Control", em_z95),
            "genotype_matched_ext_c9_symp_vs_c9_asym_center_adj": eval_contrast(ext_sc_center_adj, ext_df["status"] == "C9orf72", ext_df["status"] == "C9orf72-Asymptomatic", em_z95),
            "ext_washu_sals_vs_center_adj_ext_ctrl": eval_contrast(ext_sc_center_adj, ext_df["status"] == "sALS", ext_df["status"] == "Control", em_z95),
            "ext_all_symp_als_vs_center_adj_ext_ctrl": eval_contrast(ext_sc_center_adj, ext_als_mask, ext_df["status"] == "Control", em_z95),
            "raw_unadjusted_ext_all_symp_als_vs_ext_ctrl_confounded": eval_contrast(ext_sc_cal, ext_als_mask, ext_df["status"] == "Control", em_z95),
            "matched_genotype_p80_pass_rates": {
                "frozen_emory_z95_ctrl_cutoff": round(em_z95, 4),
                "frozen_emory_sals_p80_cutoff": round(em_sals_p80, 4),
                "emory_sals_pass_at_sals_p80": round(float((em_sc_cal[em_df["status"] == "sALS"] > em_sals_p80).mean()), 4),
                "ext_washu_sals_pass_at_sals_p80": round(float((ext_sc_cal[ext_df["status"] == "sALS"] > em_sals_p80).mean()), 4),
                "frozen_emory_all_als_p80_cutoff": round(em_all_als_p80, 4),
                "emory_all_als_pass_at_all_als_p80": round(float((em_sc_cal[em_df["status"].isin(["sALS", "C9orf72", "SOD1"])] > em_all_als_p80).mean()), 4),
                "ext_all_als_pass_at_all_als_p80_86pct_familial": round(float((ext_sc_cal[ext_als_mask] > em_all_als_p80).mean()), 4),
            },
        },
        "cross_platform_emory_tmtpro_technical_overlap": {
            "cohort_overlap_warning": "101/101 SC TMTpro samples belong to Emory inside Expanded DIA (Trautwig Par8); technical cross-platform check only.",
            "sporadic_vs_ctrl": eval_contrast(tmt_sc, tmt_mat["status"] == "Sporadic", tmt_mat["status"] == "Control", float(tmt_fit["z_cut_95_ctrl"])),
            "all_symp_als_vs_ctrl": eval_contrast(tmt_sc, tmt_mat["status"].isin(["Sporadic", "C9orf72", "SOD1"]), tmt_mat["status"] == "Control", float(tmt_fit["z_cut_95_ctrl"])),
        },
        "independent_external_study_oh2023_pmc10215566": extract_oh2023_header_resolved(resolve_dataset_path("DS046_OH_XML", verify_hash=True)),
    })
    (OUT_DIR / "run_p3a_002_csf_glial_bridge_validation.json").write_text(json.dumps(out, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"emory_oof": out["within_emory_unconfounded_dia"]["sals_vs_ctrl_leak_free_5fold_oof"], "drift": out["pooled_ds045_center_audit"]["bridge_ctrl_drift_pure_mgh_n16_minus_emory_n54_z"], "ext_adj": out["deconfounded_and_stratified_external_validation"]["ext_all_symp_als_vs_center_adj_ext_ctrl"]}, indent=2))


if __name__ == "__main__":
    main()
