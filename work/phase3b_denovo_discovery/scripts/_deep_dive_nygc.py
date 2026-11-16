"""Donor-aware NYGC (GSE153960) multi-region, tSTMN2 burden, SOD1/FUS negative-control, & O'Neill subtype analysis for RUN-P3B-004."""
from __future__ import annotations

import gzip
import re
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

from carbon_als.loaders import (
    assert_unique_donors,
    load_brown2022_splicing,
    load_oneill2025_subtypes,
    resolve_col,
    resolve_dataset_path,
)

TARGET_GENES = ["ATG4B", "KALRN", "PTPRT", "CELF5", "PRUNE2", "PFKP", "TRAPPC12", "ELK1", "DLGAP1", "STMN2"]
CANDIDATE_MN_NEUR_MARKERS = ("CHAT", "ISL1", "MNX1", "NEFH", "RBFOX3", "SNAP25", "SYP", "SYN1", "ENO2", "TUBB3")
SOD1_FUS_RE = re.compile(r"positive for[^;]*\b(?:sod1|fus)\b", re.IGNORECASE)
REGIONS_MAP = {
    "Spinal_Cord_Cervical": {"Spinal_Cord_Cervical"},
    "Spinal_Cord_Lumbar": {"Spinal_Cord_Lumbar"},
    "Cortex_Motor": {"Cortex_Motor_Medial", "Cortex_Motor_Lateral"},
}


def _load_cryptic_gene_set() -> set[str]:
    jdf = load_brown2022_splicing()["junctions_df"]
    br_c = set(jdf[jdf["cryptic_junction"].astype(str).str.lower() == "true"]["gene_name"].astype(str))
    ma5 = pd.read_excel(resolve_dataset_path("DS_CRYPTIC", verify_hash=True) / "Ma2022_41586_2022_4424_MOESM5_ESM.xlsx")
    bs2 = pd.read_excel(resolve_dataset_path("DS_BRYCE_APA", verify_hash=True), sheet_name="Supplementary_Table_2")
    return br_c | set(ma5["Genes"].astype(str)) | set(bs2["gene_name"].astype(str)) | {"STMN2", "UNC13A"}


def _ols_single_x(y: np.ndarray, x_cols: np.ndarray) -> tuple[float, float, float]:
    x_mat = sm.add_constant(x_cols, has_constant="add")
    betas, *_ = np.linalg.lstsq(x_mat, y, rcond=None)
    dof = max(len(y) - x_mat.shape[1], 1)
    mse = float(np.sum((y - x_mat @ betas) ** 2) / dof)
    cov11 = float(np.linalg.pinv(x_mat.T @ x_mat)[1, 1])
    t_val = float(betas[1] / np.sqrt(max(mse * cov11, 1e-30)))
    return round(float(betas[1]), 4), round(t_val, 4), float(2.0 * stats.t.sf(abs(t_val), df=dof))


def analyze_nygc_multiregion(regulon_genes: set[str]) -> tuple[dict[str, Any], dict[str, dict[str, float]]]:
    cryptic_genes = _load_cryptic_gene_set()
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    ens_col, sym_col = resolve_col(gc_df, "Gene stable ID"), resolve_col(gc_df, "Gene name")
    gc_col, typ_col = resolve_col(gc_df, "Gene % GC content"), resolve_col(gc_df, "Gene type")
    gc_sub = gc_df.dropna(subset=[ens_col, sym_col, gc_col])
    ens_to_sym = dict(zip(gc_sub[ens_col].astype(str), gc_sub[sym_col].astype(str)))
    pc_gc = gc_sub[gc_sub[typ_col] == "protein_coding"].groupby(sym_col)[gc_col].mean().to_dict()
    hg_set = {g for g, v in pc_gc.items() if v >= 60.0}
    lg_set = {g for g, v in pc_gc.items() if v <= 38.0}
    tracked = set(pc_gc) | set(TARGET_GENES) | set(CANDIDATE_MN_NEUR_MARKERS) | regulon_genes

    cnt_fp = resolve_dataset_path("DS001_COUNTS", verify_hash=True)
    with gzip.open(cnt_fp, "rt", encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        assert hdr[0].strip('"') in {"EnsemblID", "gene_id", "Geneid"} and hdr[1].strip('"').startswith("CGND-"), f"Bad NYGC header: {hdr[:3]}"
        sample_ids = [s.strip('"') for s in hdr[1:]]
        n_samp = len(sample_ids)
        lib_size = np.zeros(n_samp, dtype=np.float64)
        sym_cnt: dict[str, np.ndarray] = {}
        for ln in fh:
            t1 = ln.find("\t")
            t2 = ln.find("\t", t1 + 1)
            ens_b = ln[t1 + 1 : t2].strip('"').split(".")[0]
            vals = np.fromstring(ln[t2 + 1 :], dtype=np.float64, sep="\t")
            if len(vals) != n_samp:
                continue
            lib_size += vals
            sym = ens_to_sym.get(ens_b)
            if sym in tracked:
                if sym not in sym_cnt:
                    sym_cnt[sym] = vals.astype(np.float32)
                else:
                    sym_cnt[sym] += vals.astype(np.float32)

    denom = np.maximum(lib_size, 1.0)
    log2cpm = {g: np.log2((arr.astype(np.float64) / denom) * 1e6 + 1.0) for g, arr in sym_cnt.items()}
    hg_avail = [log2cpm[g] for g in hg_set if g in log2cpm]
    lg_avail = [log2cpm[g] for g in lg_set if g in log2cpm]
    gc_score = np.mean(hg_avail, axis=0) - np.mean(lg_avail, axis=0)

    meta = pd.read_excel(resolve_dataset_path("DS001_META", verify_hash=True), sheet_name=0)
    mut_col = [c for c in meta.columns if "Reported Genomic Mutations" in str(c)][0]
    meta["ExternalSampleId"] = meta[resolve_col(meta, "ExternalSampleId")].astype(str)
    meta = meta[meta["ExternalSampleId"].isin(set(sample_ids))].copy()
    sid_to_idx = {s: i for i, s in enumerate(sample_ids)}
    m_idx = meta["ExternalSampleId"].map(sid_to_idx).to_numpy(int)
    meta["calc_lib_size"] = lib_size[m_idx]
    meta["gc_score"] = gc_score[m_idx]
    meta["RIN_num"] = pd.to_numeric(meta[resolve_col(meta, "RIN")], errors="coerce")
    meta["STMN2_TPM_num"] = pd.to_numeric(meta[resolve_col(meta, "STMN2_TPM")], errors="coerce").fillna(0.0)
    meta["tSTMN2_TPM_num"] = pd.to_numeric(meta[resolve_col(meta, "tSTMN2_TPM")], errors="coerce").fillna(0.0)
    meta = meta[(meta["RIN_num"] >= 5.0) & (meta["calc_lib_size"] >= 1e6)].copy()
    m_idx2 = meta["ExternalSampleId"].map(sid_to_idx).to_numpy(int)

    oneill = load_oneill2025_subtypes(exclude_pure_ftd=True)["cases_df"]
    pid_to_sub = dict(zip(oneill["PatientID"].astype(str), oneill["PatientSubtype"].astype(str)))
    meta["oneill_motor_subtype"] = meta[resolve_col(meta, "ExternalSubjectId")].astype(str).map(pid_to_sub).fillna("")

    def _classify_strata(r: pd.Series) -> str:
        dg, sg, mut = str(r["disease_group"]), str(r["Subject Group"]), str(r[mut_col])
        has_sf = bool(SOD1_FUS_RE.search(mut)) or dg == "ALS-SOD1" or "FUS" in dg
        if dg == "Control" and sg == "Non-Neurological Control":
            return "Control"
        if dg in {"ALS-TDP", "ALS/FTLD"} and not has_sf:
            return "ALS_TDP"
        if dg == "ALS-SOD1" or ("ALS" in sg and has_sf):
            return "ALS_SOD1_FUS"
        return "OTHER"

    meta["stratum"] = meta.apply(_classify_strata, axis=1)
    mn_markers = [m for m in CANDIDATE_MN_NEUR_MARKERS if m in log2cpm and m not in cryptic_genes]
    assert len(mn_markers) >= 5, f"Too few TDP-43-spared MN/neuronal markers: {mn_markers}"
    all_eval_genes = sorted((set(pc_gc) | set(TARGET_GENES) | set(mn_markers) | regulon_genes) & set(log2cpm))
    expr_df = pd.DataFrame({g: log2cpm[g][m_idx2] for g in all_eval_genes}, index=meta.index)
    full_df = pd.concat([meta[["ExternalSubjectId", "Sample Source", "stratum", "oneill_motor_subtype", "RIN_num", "gc_score", "STMN2_TPM_num", "tSTMN2_TPM_num"]], expr_df], axis=1)

    reg_out: dict[str, Any] = {"n_high_gc_ref": len(hg_avail), "n_low_gc_ref": len(lg_avail), "tdp43_spared_mn_neur_markers": mn_markers, "regions": {}}
    reg_tstats: dict[str, dict[str, float]] = {}
    for reg_name, src_set in REGIONS_MAP.items():
        sub = full_df[full_df["Sample Source"].isin(src_set) & full_df["stratum"].isin({"Control", "ALS_TDP", "ALS_SOD1_FUS"})].copy()
        num_cols = ["RIN_num", "gc_score", "STMN2_TPM_num", "tSTMN2_TPM_num", *all_eval_genes]
        gb = sub.groupby("ExternalSubjectId")
        ddf = pd.concat([gb[["stratum", "oneill_motor_subtype"]].first(), gb[num_cols].mean()], axis=1).reset_index()
        assert_unique_donors(ddf["ExternalSubjectId"].astype(str).tolist(), f"NYGC:{reg_name}")
        mk_mat = ddf[mn_markers].to_numpy(float)
        ddf["mn_neur_z"] = ((mk_mat - mk_mat.mean(axis=0)) / np.maximum(mk_mat.std(axis=0), 1e-8)).mean(axis=1)
        tdp_df, ctrl_df, sf_df = ddf[ddf["stratum"] == "ALS_TDP"], ddf[ddf["stratum"] == "Control"], ddf[ddf["stratum"] == "ALS_SOD1_FUS"]
        tc_df = ddf[ddf["stratum"].isin({"ALS_TDP", "Control"})]
        ts_df = ddf[ddf["stratum"].isin({"ALS_TDP", "ALS_SOD1_FUS"})]

        if reg_name in {"Spinal_Cord_Cervical", "Cortex_Motor"}:
            eval_nz = [g for g in all_eval_genes if float(tc_df[g].std()) > 1e-8]
            x_tc = sm.add_constant(np.column_stack([(tc_df["stratum"] == "ALS_TDP").astype(float), tc_df["RIN_num"], tc_df["gc_score"]]))
            ym = tc_df[eval_nz].to_numpy(float)
            bt = np.linalg.lstsq(x_tc, ym, rcond=None)[0]
            mse_v = ((ym - x_tc @ bt) ** 2).sum(axis=0) / max(len(tc_df) - x_tc.shape[1], 1)
            tv = bt[1] / np.sqrt(np.maximum(mse_v * float(np.linalg.pinv(x_tc.T @ x_tc)[1, 1]), 1e-30))
            reg_tstats[reg_name] = {g: float(t) for g, t in zip(eval_nz, tv, strict=True)}

        ctrl_mn = ctrl_df["mn_neur_z"].to_numpy(float)
        ctrl_mn_c = ctrl_mn - ctrl_mn.mean()
        ctrl_mn_ss = max(float(np.sum(ctrl_mn_c**2)), 1e-12)
        cand_nc = [g for g in all_eval_genes if g in pc_gc and g not in cryptic_genes and g not in set(mn_markers) and float(ctrl_df[g].mean()) >= 2.0 and float(ctrl_df[g].std()) > 1e-6 and float(tdp_df[g].std()) > 1e-6]
        cm = ctrl_df[cand_nc].to_numpy(float)
        cm_c = cm - cm.mean(axis=0)
        r_ctrl = (ctrl_mn_c @ cm_c) / np.sqrt(ctrl_mn_ss * np.maximum((cm_c**2).sum(axis=0), 1e-12))
        nc_neur_cols = [g for g, r_v in zip(cand_nc, r_ctrl, strict=True) if float(r_v) >= 0.30]

        x_mn = sm.add_constant(np.column_stack([np.log2(tdp_df["tSTMN2_TPM_num"] + 1.0), tdp_df["RIN_num"], tdp_df["gc_score"], tdp_df["mn_neur_z"]]))
        ym_nc = tdp_df[nc_neur_cols].to_numpy(float)
        b_nc = np.linalg.lstsq(x_mn, ym_nc, rcond=None)[0]
        mse_nc = ((ym_nc - x_mn @ b_nc) ** 2).sum(axis=0) / max(len(tdp_df) - x_mn.shape[1], 1)
        ref_t_nc = b_nc[1] / np.sqrt(np.maximum(mse_nc * float(np.linalg.pinv(x_mn.T @ x_mn)[1, 1]), 1e-30))

        gene_res: dict[str, Any] = {}
        for g in TARGET_GENES:
            if g not in ddf.columns:
                continue
            vt, vc, vs = tdp_df[g].to_numpy(float), ctrl_df[g].to_numpy(float), sf_df[g].to_numpy(float)
            b_tc, t_tc, p_tc = _ols_single_x(tc_df[g].to_numpy(float), np.column_stack([(tc_df["stratum"] == "ALS_TDP").astype(float), tc_df["RIN_num"], tc_df["gc_score"]]))
            b_ts, _, p_ts = _ols_single_x(ts_df[g].to_numpy(float), np.column_stack([(ts_df["stratum"] == "ALS_TDP").astype(float), ts_df["RIN_num"], ts_df["gc_score"]])) if len(sf_df) >= 3 else (0.0, 0.0, 1.0)
            sp_r, sp_p = stats.spearmanr(vt, tdp_df["tSTMN2_TPM_num"].to_numpy(float))
            b_mn, t_mn, p_mn = _ols_single_x(vt, np.column_stack([np.log2(tdp_df["tSTMN2_TPM_num"] + 1.0), tdp_df["RIN_num"], tdp_df["gc_score"], tdp_df["mn_neur_z"]]))
            pct_more_neg = round(100.0 * float(np.mean(ref_t_nc < t_mn)), 2) if len(ref_t_nc) else None
            sub_dict: dict[str, Any] = {}
            sub_arrays = []
            for s_lbl in ("ALS-Ox", "ALS-Glia", "ALS-TE"):
                s_rows = tdp_df[tdp_df["oneill_motor_subtype"] == s_lbl]
                if len(s_rows) >= 3:
                    sub_arrays.append(s_rows[g].to_numpy(float))
                    sc = pd.concat([s_rows, ctrl_df], axis=0)
                    bs, _, ps = _ols_single_x(sc[g].to_numpy(float), np.column_stack([(sc["stratum"] == "ALS_TDP").astype(float), sc["RIN_num"], sc["gc_score"]]))
                    sub_dict[s_lbl] = {"n": int(len(s_rows)), "mean_log2cpm": round(float(s_rows[g].mean()), 4), "adj_beta_vs_ctrl": bs, "adj_p_vs_ctrl": ps}
            kw_p = float(stats.kruskal(*sub_arrays).pvalue) if len(sub_arrays) == 3 else None
            gene_res[g] = {
                "n_als_tdp": int(len(vt)), "n_ctrl": int(len(vc)), "n_als_sod1_fus": int(len(vs)),
                "mean_als_tdp": round(float(vt.mean()), 4), "mean_ctrl": round(float(vc.mean()), 4),
                "mean_als_sod1_fus": round(float(vs.mean()), 4) if len(vs) else None,
                "unadj_diff_tdp_vs_ctrl": round(float(vt.mean() - vc.mean()), 4),
                "welch_p_tdp_vs_ctrl": float(stats.ttest_ind(vt, vc, equal_var=False).pvalue),
                "mwu_p_tdp_vs_ctrl": float(stats.mannwhitneyu(vt, vc, alternative="two-sided").pvalue),
                "adj_beta_tdp_vs_ctrl": b_tc, "adj_t_tdp_vs_ctrl": t_tc, "adj_p_tdp_vs_ctrl": p_tc,
                "unadj_diff_tdp_vs_sod1fus": round(float(vt.mean() - vs.mean()), 4) if len(vs) >= 3 else None,
                "welch_p_tdp_vs_sod1fus": float(stats.ttest_ind(vt, vs, equal_var=False).pvalue) if len(vs) >= 3 else None,
                "adj_beta_tdp_vs_sod1fus": b_ts if len(vs) >= 3 else None, "adj_p_tdp_vs_sod1fus": p_ts if len(vs) >= 3 else None,
                "within_tdp_spearman_tSTMN2_rho": round(float(sp_r), 4), "within_tdp_spearman_tSTMN2_p": float(sp_p),
                "within_tdp_mn_adj_log2_tSTMN2_beta": b_mn, "within_tdp_mn_adj_log2_tSTMN2_t": t_mn,
                "within_tdp_mn_adj_log2_tSTMN2_p": p_mn,
                "within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal": pct_more_neg,
                "oneill_motor_subtypes": sub_dict, "oneill_kruskal_3subtype_p": kw_p,
            }
        reg_out["regions"][reg_name] = {
            "n_donors_total": int(len(ddf)), "n_als_tdp": int(len(tdp_df)), "n_ctrl": int(len(ctrl_df)), "n_als_sod1_fus": int(len(sf_df)),
            "n_noncryptic_neuronal_ref": int(len(nc_neur_cols)),
            "noncryptic_neuronal_ref_median_t": round(float(np.median(ref_t_nc)), 4) if len(ref_t_nc) else None,
            "noncryptic_neuronal_ref_pct_neg": round(100.0 * float(np.mean(ref_t_nc < 0)), 2) if len(ref_t_nc) else None,
            "genes": gene_res,
        }
    return reg_out, reg_tstats
