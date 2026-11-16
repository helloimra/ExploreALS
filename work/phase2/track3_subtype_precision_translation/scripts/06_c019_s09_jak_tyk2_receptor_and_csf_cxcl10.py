"""RUN-P2-T3-005: C019 vs S09 JAK1/gp130-STAT3 vs IFNAR/TYK2-JH2 Receptor Mapping & Living-CSF CXCL10 Dissection."""

from __future__ import annotations

import gzip
import json
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
    load_edinburgh_pseudobulk,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase2" / "track3_subtype_precision_translation" / "outputs"

AXES = {
    "gp130_JAK1_JAK2_STAT3_axis_spared_by_TYK2_JH2": ["IL6ST", "OSMR", "OSM", "LIFR", "IL6R", "STAT3", "SOCS3", "SERPINA3", "CHI3L1", "GPNMB"],
    "IFNg_JAK1_JAK2_STAT1_axis_spared_by_TYK2_JH2": ["IFNGR1", "IFNGR2", "STAT1", "IRF1", "CXCL10", "CXCL9", "GBP1"],
    "TypeI_IFN_IL12_23_TYK2_JH2_engaged_axis": ["IFNAR1", "IFNAR2", "TYK2", "JAK1", "JAK2", "STAT2", "IRF9", "ISG15", "MX1", "OAS1", "IFIT1", "IL12RB1", "IL23R"],
    "CSF_reference_markers": ["CHIT1", "CHI3L2"],
}
CELLCOMP_GENES = ["RBFOX3", "SNAP25", "SLC17A7", "AIF1", "AQP4", "MOG"]
ALL_GENES = sorted({g for lst in AXES.values() for g in lst} | set(CELLCOMP_GENES))


def roc_auc_u(y_true: np.ndarray, scores: np.ndarray) -> float:
    pos, neg = scores[y_true == 1], scores[y_true == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    u_stat, _ = stats.mannwhitneyu(pos, neg, alternative="two-sided")
    return float(u_stat / (len(pos) * len(neg)))


def load_nygc_panel(symbols: list[str]) -> tuple[pd.DataFrame, dict[str, float]]:
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    gc_by_ens = dict(zip(gc_df[resolve_col(gc_df, "Gene stable ID")].astype(str), pd.to_numeric(gc_df[resolve_col(gc_df, "Gene % GC content")], errors="coerce")))
    gc_by_sym = gc_df.groupby(resolve_col(gc_df, "Gene name"))[resolve_col(gc_df, "Gene % GC content")].mean().to_dict()
    feat = pd.read_csv(resolve_dataset_path("DS001_FEAT", verify_hash=True))
    sc, ec = resolve_col(feat, "ucsd_label"), resolve_col(feat, "nygc_exact_versioned_ids")
    sub = feat.loc[feat[sc].isin(symbols) & feat[ec].notna()]
    ens_map = {str(r[ec]): str(r[sc]) for _, r in sub.iterrows() if ";" not in str(r[ec])}
    found: dict[str, np.ndarray] = {}
    with gzip.open(resolve_dataset_path("DS001_COUNTS", verify_hash=True), "rt", encoding="utf-8") as fh:
        samples = fh.readline().rstrip("\n").split("\t")[1:]
        libs = np.zeros(len(samples), dtype=np.float64)
        hi_gc = np.zeros(len(samples), dtype=np.float64)
        lo_gc = np.zeros(len(samples), dtype=np.float64)
        for ln in fh:
            pts = ln.rstrip("\n").split("\t")
            arr = np.fromiter((float(x) for x in pts[2:]), dtype=np.float64, count=len(samples))
            libs += arr
            g_gc = gc_by_ens.get(pts[1].split(".")[0])
            if g_gc is not None and not np.isnan(g_gc):
                if g_gc >= 60.0:
                    hi_gc += arr
                elif g_gc <= 42.0:
                    lo_gc += arr
            if pts[1] in ens_map:
                found[ens_map[pts[1]]] = arr
    df = pd.DataFrame({s: np.log2((a / np.maximum(libs, 1.0)) * 1e6 + 1.0) for s, a in found.items()}, index=samples)
    df["_sample_gc_index"] = np.log2((hi_gc + 1.0) / (lo_gc + 1.0))
    gene_gc = {s: round(float(gc_by_sym[s]), 2) for s in symbols if s in gc_by_sym and pd.notna(gc_by_sym[s])}
    return df, gene_gc


def _ols_adj(df_sub: pd.DataFrame, target_g: str, case_mask: pd.Series, cov_cols: list[str]) -> dict[str, float | int]:
    sub = df_sub[[target_g, *cov_cols]].assign(_case=case_mask.astype(float)).dropna()
    X = np.column_stack([np.ones(len(sub)), sub["_case"].to_numpy(), *[sub[c].to_numpy() for c in cov_cols]])
    y = sub[target_g].to_numpy(dtype=float)
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = max(len(y) - X.shape[1], 1)
    se = float(np.sqrt(max(float((resid @ resid) / dof) * float(np.linalg.pinv(X.T @ X)[1, 1]), 1e-12)))
    return {"n": int(len(sub)), "adj_beta": round(float(beta[1]), 4), "adj_p": float(2.0 * stats.t.sf(abs(beta[1]) / se, df=dof))}


def summarize_nygc_region(expr: pd.DataFrame, gene_gc: dict[str, float], samp_df: pd.DataFrame, donor_df: pd.DataFrame, label: str) -> dict:
    s_mot = samp_df.loc[samp_df["Sample"].astype(str).isin(expr.index) & samp_df["Group"].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    rin_cols = [c for c in s_mot.columns if c.strip().upper() == "RIN"]
    keep_s = ["Sample", "Patient ID"] + (rin_cols[:1] if rin_cols else [])
    if rin_cols:
        s_mot[rin_cols[0]] = pd.to_numeric(s_mot[rin_cols[0]], errors="coerce")
    d_mot = donor_df.loc[donor_df["Group"].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    d_map = d_mot.assign(
        stratum=np.where(d_mot["Group"].astype(str).str.upper().isin(["CTL", "CONTROL"]), "Control", d_mot["PatientSubtype"].astype(str))
    )[["PatientID", "stratum"]].drop_duplicates(subset=["PatientID"])
    merged = s_mot[keep_s].merge(expr, left_on="Sample", right_index=True)
    num_cols = list(expr.columns) + (rin_cols[:1] if rin_cols else [])
    don = merged.groupby("Patient ID", as_index=False)[num_cols].mean().merge(d_map, left_on="Patient ID", right_on="PatientID", how="inner")
    assert_unique_donors(don["Patient ID"].tolist(), f"NYGC_{label}")
    don["_neuron_idx"] = don[[c for c in ["RBFOX3", "SNAP25", "SLC17A7"] if c in don.columns]].mean(axis=1)
    don["_glia_idx"] = don[[c for c in ["AIF1", "AQP4", "MOG"] if c in don.columns]].mean(axis=1)
    covs = ["_sample_gc_index", "_neuron_idx", "_glia_idx"] + (rin_cols[:1] if rin_cols and don[rin_cols[0]].notna().sum() >= 30 else [])

    ctrl = don.loc[don["stratum"] == "Control"]
    als = don.loc[don["stratum"].str.startswith("ALS-")].copy()
    gl = als.loc[als["stratum"].str.startswith("ALS-Glia")]
    ox = als.loc[als["stratum"].str.startswith("ALS-Ox")]
    te = als.loc[als["stratum"].str.startswith("ALS-TE")]

    gene_stats: dict[str, dict] = {}
    panel_only = sorted(g for g in expr.columns if not g.startswith("_") and g not in CELLCOMP_GENES)
    for g in panel_only:
        y_gl = als["stratum"].str.startswith("ALS-Glia").astype(int).to_numpy()
        gl_ox = pd.concat([gl, ox], axis=0)
        gl_ct = pd.concat([gl, ctrl], axis=0)
        rec: dict[str, object] = {
            "gene_gc_pct": gene_gc.get(g),
            "glia_vs_ox_diff": round(float(gl[g].mean() - ox[g].mean()), 4),
            "glia_vs_ox_welch_p": float(stats.ttest_ind(gl[g], ox[g], equal_var=False).pvalue),
            "glia_vs_ox_gc_cellcomp_ols": _ols_adj(gl_ox, g, gl_ox["stratum"].str.startswith("ALS-Glia"), covs),
            "glia_vs_ctrl_diff": round(float(gl[g].mean() - ctrl[g].mean()), 4),
            "glia_vs_ctrl_welch_p": float(stats.ttest_ind(gl[g], ctrl[g], equal_var=False).pvalue),
            "glia_vs_ctrl_gc_cellcomp_ols": _ols_adj(gl_ct, g, gl_ct["stratum"].str.startswith("ALS-Glia"), covs),
            "within_als_glia_auc": round(roc_auc_u(y_gl, als[g].to_numpy()), 4),
        }
        if len(te) >= 5:
            y_te = als["stratum"].str.startswith("ALS-TE").astype(int).to_numpy()
            te_ox = pd.concat([te, ox], axis=0)
            te_ct = pd.concat([te, ctrl], axis=0)
            rec.update({
                "te_vs_ox_diff": round(float(te[g].mean() - ox[g].mean()), 4),
                "te_vs_ox_welch_p": float(stats.ttest_ind(te[g], ox[g], equal_var=False).pvalue),
                "te_vs_ox_gc_cellcomp_ols": _ols_adj(te_ox, g, te_ox["stratum"].str.startswith("ALS-TE"), covs),
                "te_vs_ctrl_diff": round(float(te[g].mean() - ctrl[g].mean()), 4),
                "te_vs_ctrl_welch_p": float(stats.ttest_ind(te[g], ctrl[g], equal_var=False).pvalue),
                "te_vs_ctrl_gc_cellcomp_ols": _ols_adj(te_ct, g, te_ct["stratum"].str.startswith("ALS-TE"), covs),
                "ox_vs_ctrl_diff": round(float(ox[g].mean() - ctrl[g].mean()), 4),
                "ox_vs_ctrl_welch_p": float(stats.ttest_ind(ox[g], ctrl[g], equal_var=False).pvalue),
                "within_als_te_auc": round(roc_auc_u(y_te, als[g].to_numpy()), 4),
            })
        gene_stats[g] = rec

    axis_scores: dict[str, dict] = {}
    for ax_name, g_list in AXES.items():
        if ax_name == "CSF_reference_markers":
            continue
        present = [g for g in g_list if g in don.columns]
        z_mat = pd.DataFrame({g: (don[g] - float(ctrl[g].mean())) / max(float(ctrl[g].std(ddof=1)), 1e-6) for g in present}, index=don.index)
        comp = z_mat.mean(axis=1)
        y_gl = als["stratum"].str.startswith("ALS-Glia").astype(int).to_numpy()
        ax_rec: dict[str, object] = {
            "genes_present": present,
            "glia_vs_ox_z_diff": round(float(comp.loc[gl.index].mean() - comp.loc[ox.index].mean()), 4),
            "glia_vs_ox_welch_p": float(stats.ttest_ind(comp.loc[gl.index], comp.loc[ox.index], equal_var=False).pvalue),
            "within_als_glia_auc": round(roc_auc_u(y_gl, comp.loc[als.index].to_numpy()), 4),
        }
        if len(te) >= 5:
            y_te = als["stratum"].str.startswith("ALS-TE").astype(int).to_numpy()
            ax_rec["te_vs_ox_z_diff"] = round(float(comp.loc[te.index].mean() - comp.loc[ox.index].mean()), 4)
            ax_rec["te_vs_ox_welch_p"] = float(stats.ttest_ind(comp.loc[te.index], comp.loc[ox.index], equal_var=False).pvalue)
            ax_rec["within_als_te_auc"] = round(roc_auc_u(y_te, comp.loc[als.index].to_numpy()), 4)
        axis_scores[ax_name] = ax_rec
    return {"stratum_counts": don["stratum"].value_counts().to_dict(), "axis_composites": axis_scores, "genes": gene_stats}


def analyze_ds045_living_csf() -> dict:
    assert_modality("PROTEOMICS_CSF_DIA", "DS045_TRAUT")
    assert_modality("PROTEOMICS_CSF_TMT", "DS045_TRAUT")
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    targets = ["CXCL10", "STAT1", "STAT3", "ISG15", "CHIT1", "CHI3L2", "GPNMB", "CHI3L1", "SERPINA3"]

    c2 = read_xlsx_sparse_safe(p45, "2-Cohort-Exp Characteristics", 2)
    dia = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    c2["dia_col"] = c2["_unnamed_col_0"].astype(str).str.replace(r"\.2$", "", regex=True).str.replace(r"\.(\d+)$", r"-\1", regex=True)
    assert_unique_donors(c2["ID"].tolist(), "DS045_DIA_259")
    dia["sym"] = dia[resolve_col(dia, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
    d_sub = dia.loc[dia["sym"].isin(targets)].groupby("sym")[c2["dia_col"].tolist()].first().apply(pd.to_numeric, errors="coerce")
    st_dia = c2.set_index("dia_col")["SymptomStatus"]
    bank_dia = c2.set_index("dia_col")[resolve_col(c2, "TissueBank")]

    ctrl_cols = st_dia.index[st_dia == "Control"].tolist()
    z_b = pd.DataFrame(index=c2["dia_col"].tolist())
    for g in ["CHIT1", "CHI3L2", "GPNMB", "CHI3L1", "SERPINA3"]:
        mu, sd = float(d_sub.loc[g, ctrl_cols].mean()), float(d_sub.loc[g, ctrl_cols].std(ddof=1))
        z_b[g] = (d_sub.loc[g] - mu) / max(sd, 1e-6)
    z_b["bridge_4prot"] = pd.concat([np.maximum(z_b["CHIT1"].fillna(-3.0), z_b["CHI3L2"].fillna(0.0)), z_b["GPNMB"], z_b["CHI3L1"], z_b["SERPINA3"]], axis=1).mean(axis=1)

    def center_adj_ols(val_s: pd.Series, grp_s: pd.Series, pos_vals: list[str]) -> dict:
        df_m = pd.DataFrame({"y": val_s, "grp": grp_s, "bank": bank_dia}).loc[lambda d: d["grp"].isin(pos_vals + ["Control"])].dropna()
        valid_banks = {
            b for b, gdf in df_m.groupby("bank")
            if int((gdf["grp"] == "Control").sum()) >= 2 and int((gdf["grp"] != "Control").sum()) >= 2
        }
        df_m = df_m.loc[df_m["bank"].isin(valid_banks)].copy()
        if int((df_m["grp"] != "Control").sum()) < 5 or int((df_m["grp"] == "Control").sum()) < 5:
            return {"n_matched_centers": int(len(df_m)), "banks_included": sorted(valid_banks), "beta": None, "p": None}
        x_case = (df_m["grp"] != "Control").astype(float).to_numpy()
        dummies = pd.get_dummies(df_m["bank"], drop_first=True, dtype=float).to_numpy()
        X = np.column_stack([np.ones(len(df_m)), x_case, dummies]) if dummies.shape[1] > 0 else np.column_stack([np.ones(len(df_m)), x_case])
        y = df_m["y"].to_numpy(dtype=float)
        beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        dof = max(len(y) - X.shape[1], 1)
        cov = (float(resid @ resid) / dof) * np.linalg.pinv(X.T @ X)
        se = float(np.sqrt(max(cov[1, 1], 1e-12)))
        p_val = float(2.0 * stats.t.sf(abs(beta[1]) / se, df=dof))
        return {"n_matched_centers": int(len(df_m)), "banks_included": sorted(valid_banks), "beta": round(float(beta[1]), 4), "p": p_val}

    dia_proteins: dict[str, dict] = {}
    for g in targets:
        if g not in d_sub.index:
            dia_proteins[g] = {"detected": False}
            continue
        s = d_sub.loc[g]
        by_grp = {str(k): int(s.loc[st_dia == k].notna().sum()) for k in st_dia.unique()}
        v_ctrl = s.loc[st_dia == "Control"].dropna()
        v_sals = s.loc[st_dia == "sALS"].dropna()
        v_c9 = s.loc[st_dia == "C9orf72"].dropna()
        v_c9a = s.loc[st_dia == "C9orf72-Asymptomatic"].dropna()
        v_sod1 = s.loc[st_dia == "SOD1"].dropna()
        v_sym = s.loc[st_dia.isin(["sALS", "C9orf72", "SOD1"])].dropna()
        q90 = float(v_ctrl.quantile(0.90)) if len(v_ctrl) >= 10 else float("nan")
        pair = pd.DataFrame({"prot": s, "bridge": z_b["bridge_4prot"], "status": st_dia}).loc[st_dia.isin(["sALS", "C9orf72", "SOD1"])].dropna()
        dia_proteins[g] = {
            "detected": True,
            "n_non_missing_total": int(s.notna().sum()),
            "missing_pct_total": round(100.0 * float(s.isna().mean()), 2),
            "non_missing_by_group": by_grp,
            "sals_vs_ctrl_log2_diff": round(float(v_sals.mean() - v_ctrl.mean()), 4) if len(v_sals) >= 5 and len(v_ctrl) >= 5 else None,
            "sals_vs_ctrl_welch_p": float(stats.ttest_ind(v_sals, v_ctrl, equal_var=False).pvalue) if len(v_sals) >= 5 and len(v_ctrl) >= 5 else None,
            "sals_vs_ctrl_matched_center_ols": center_adj_ols(s, st_dia, ["sALS"]),
            "c9_vs_ctrl_log2_diff": round(float(v_c9.mean() - v_ctrl.mean()), 4) if len(v_c9) >= 5 and len(v_ctrl) >= 5 else None,
            "c9_vs_ctrl_welch_p": float(stats.ttest_ind(v_c9, v_ctrl, equal_var=False).pvalue) if len(v_c9) >= 5 and len(v_ctrl) >= 5 else None,
            "c9_vs_ctrl_matched_center_ols": center_adj_ols(s, st_dia, ["C9orf72"]),
            "c9_asym_vs_ctrl_log2_diff": round(float(v_c9a.mean() - v_ctrl.mean()), 4) if len(v_c9a) >= 5 and len(v_ctrl) >= 5 else None,
            "c9_asym_vs_ctrl_welch_p": float(stats.ttest_ind(v_c9a, v_ctrl, equal_var=False).pvalue) if len(v_c9a) >= 5 and len(v_ctrl) >= 5 else None,
            "sod1_vs_ctrl_log2_diff": round(float(v_sod1.mean() - v_ctrl.mean()), 4) if len(v_sod1) >= 5 and len(v_ctrl) >= 5 else None,
            "sod1_vs_ctrl_welch_p": float(stats.ttest_ind(v_sod1, v_ctrl, equal_var=False).pvalue) if len(v_sod1) >= 5 and len(v_ctrl) >= 5 else None,
            "symp_als_vs_ctrl_log2_diff": round(float(v_sym.mean() - v_ctrl.mean()), 4) if len(v_sym) >= 5 and len(v_ctrl) >= 5 else None,
            "symp_als_vs_ctrl_welch_p": float(stats.ttest_ind(v_sym, v_ctrl, equal_var=False).pvalue) if len(v_sym) >= 5 and len(v_ctrl) >= 5 else None,
            "symp_als_vs_ctrl_matched_center_ols": center_adj_ols(s, st_dia, ["sALS", "C9orf72", "SOD1"]),
            "pct_above_ctrl_p90": {
                "sALS": round(100.0 * float((v_sals > q90).mean()), 2) if len(v_sals) >= 5 and not np.isnan(q90) else None,
                "C9orf72": round(100.0 * float((v_c9 > q90).mean()), 2) if len(v_c9) >= 5 and not np.isnan(q90) else None,
            },
            "corr_with_bridge4_in_symp_als": {
                "n_paired": int(len(pair)),
                "pearson_r": round(float(stats.pearsonr(pair["prot"], pair["bridge"]).statistic), 4) if len(pair) >= 8 else None,
                "pearson_p": float(stats.pearsonr(pair["prot"], pair["bridge"]).pvalue) if len(pair) >= 8 else None,
                "spearman_rho": round(float(stats.spearmanr(pair["prot"], pair["bridge"]).statistic), 4) if len(pair) >= 8 else None,
            },
        }

    c1 = read_xlsx_sparse_safe(p45, "1-Cohort-SC Characteristics", 2)
    tmt = read_xlsx_sparse_safe(p45, "3-TMT-MS Raw Data", 2)
    tmt["sym"] = tmt[resolve_col(tmt, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
    t_sub = np.log2(tmt.loc[tmt["sym"].isin(targets)].groupby("sym")[c1["Channel"].tolist()].first().apply(pd.to_numeric, errors="coerce").where(lambda x: x > 0))
    st_tmt = c1.set_index("Channel")[resolve_col(c1, "Disease")]
    ctrl_tmt = st_tmt.index[st_tmt == "Control"].tolist()
    z_tb = pd.DataFrame(index=c1["Channel"].tolist())
    for g in ["CHIT1", "CHI3L2", "GPNMB", "CHI3L1", "SERPINA3"]:
        if g in t_sub.index:
            mu_t, sd_t = float(t_sub.loc[g, ctrl_tmt].mean()), float(t_sub.loc[g, ctrl_tmt].std(ddof=1))
            z_tb[g] = (t_sub.loc[g] - mu_t) / max(sd_t, 1e-6)
    z_tb["bridge_4prot"] = pd.concat(
        [np.maximum(z_tb["CHIT1"].fillna(-3.0), z_tb["CHI3L2"].fillna(0.0)), z_tb["GPNMB"], z_tb["CHI3L1"], z_tb["SERPINA3"]], axis=1
    ).mean(axis=1)
    tmt_summary: dict[str, dict] = {}
    for g in targets:
        if g not in t_sub.index:
            tmt_summary[g] = {"detected": False}
            continue
        s = t_sub.loc[g]
        va = s.loc[st_tmt.isin(["Sporadic", "C9orf72", "SOD1"])].dropna()
        vs = s.loc[st_tmt == "Sporadic"].dropna()
        vc = s.loc[st_tmt == "Control"].dropna()
        pair_t = pd.DataFrame({"prot": s, "bridge": z_tb["bridge_4prot"]}).loc[st_tmt.isin(["Sporadic", "C9orf72", "SOD1"])].dropna()
        tmt_summary[g] = {
            "detected": True,
            "n_symp_als": int(len(va)),
            "n_sals": int(len(vs)),
            "n_ctrl": int(len(vc)),
            "symp_als_vs_ctrl_log2_diff": round(float(va.mean() - vc.mean()), 4) if len(va) >= 5 and len(vc) >= 5 else None,
            "symp_als_vs_ctrl_welch_p": float(stats.ttest_ind(va, vc, equal_var=False).pvalue) if len(va) >= 5 and len(vc) >= 5 else None,
            "sals_vs_ctrl_log2_diff": round(float(vs.mean() - vc.mean()), 4) if len(vs) >= 5 and len(vc) >= 5 else None,
            "sals_vs_ctrl_welch_p": float(stats.ttest_ind(vs, vc, equal_var=False).pvalue) if len(vs) >= 5 and len(vc) >= 5 else None,
            "corr_with_bridge4_in_symp_als": {
                "n_paired": int(len(pair_t)),
                "pearson_r": round(float(stats.pearsonr(pair_t["prot"], pair_t["bridge"]).statistic), 4) if len(pair_t) >= 8 else None,
                "pearson_p": float(stats.pearsonr(pair_t["prot"], pair_t["bridge"]).pvalue) if len(pair_t) >= 8 else None,
            },
        }
    return {"dia_4center_N259": dia_proteins, "tmt_emory_N101": tmt_summary}


def analyze_edinburgh_celltypes() -> dict:
    cell_genes = ["IL6ST", "OSMR", "STAT3", "SERPINA3", "IFNGR1", "STAT1", "CXCL10", "IFNAR1", "TYK2", "JAK1", "JAK2", "ISG15"]
    out: dict[str, dict] = {}
    for ct in ("Astrocyte", "Microglia", "Endothelial", "Excitatory neuron", "Oligodendrocyte"):
        res = load_edinburgh_pseudobulk(ct, cell_genes, region="donor_collapsed")
        df = res["donor_df"]
        g_col = resolve_col(df, "group")
        als_m = df[g_col].astype(str).str.upper() == "ALS"
        ct_stats: dict[str, dict] = {}
        for g in cell_genes:
            if g not in df.columns:
                continue
            va, vc = df.loc[als_m, g].dropna(), df.loc[~als_m, g].dropna()
            if len(va) >= 5 and len(vc) >= 4:
                ct_stats[g] = {
                    "n_als": int(len(va)),
                    "n_ctrl": int(len(vc)),
                    "mean_als_log2cpm": round(float(va.mean()), 3),
                    "als_vs_ctrl_diff": round(float(va.mean() - vc.mean()), 4),
                    "welch_p": float(stats.ttest_ind(va, vc, equal_var=False).pvalue),
                }
        out[ct] = ct_stats
    return out


def main() -> None:
    p_on = resolve_dataset_path("DS001_ONEILL", verify_hash=True)
    expr, gene_gc = load_nygc_panel(ALL_GENES)
    ctx = summarize_nygc_region(expr, gene_gc, read_xlsx_sparse_safe(p_on, "TableS1B", 2), read_xlsx_sparse_safe(p_on, "TableS1C", 2), "Cortex")
    cord = summarize_nygc_region(expr, gene_gc, read_xlsx_sparse_safe(p_on, "TableS1G", 2), read_xlsx_sparse_safe(p_on, "TableS1H", 2), "SpinalCord")
    payload = {
        "analysis_run_id": "RUN-P2-T3-005",
        "nygc_motor_cortex": ctx,
        "nygc_spinal_cord": cord,
        "edinburgh_snrna_celltypes": analyze_edinburgh_celltypes(),
        "ds045_living_csf_proteomics": analyze_ds045_living_csf(),
    }
    (OUT_DIR / "run_p2_t3_005_jak_tyk2_receptor_and_csf_cxcl10.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("SAVED run_p2_t3_005_jak_tyk2_receptor_and_csf_cxcl10.json")


if __name__ == "__main__":
    main()
