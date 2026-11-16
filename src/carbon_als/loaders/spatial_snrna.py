"""Donor-aware single-nucleus, spatial Visium, and O'Neill subtype loaders (CarbonALS v0.4.0)."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from .guards import (
    assert_modality,
    assert_unique_donors,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

PINEDA_COMPOSITE_CELLTYPES: dict[str, list[str]] = {
    "Excitatory": ["L2_L3", "L3_L5", "L4_L5", "L4_L6", "L5", "L5_L6", "L6"],
    "Inhibitory": ["PV", "SOM", "5HT3aR", "Rosehip"],
    "Vascular": ["Endo", "Mural", "Fibro"],
}


def load_oneill2025_subtypes(exclude_pure_ftd: bool = True) -> dict[str, Any]:
    """Load O'Neill et al. 2025 (DS001_ONEILL TableS1C), guarding against pure-FTD (83.3% ALS-TE) dilution."""
    p_on = resolve_dataset_path("DS001_ONEILL", verify_hash=True)
    tc = read_xlsx_sparse_safe(p_on, "TableS1C", header_row_1based=2)
    pid_col, grp_col, sub_col = resolve_col(tc, "PatientID"), resolve_col(tc, "Group"), resolve_col(tc, "PatientSubtype")
    tc = tc.loc[tc[pid_col].notna()].copy()
    assert_unique_donors(tc[pid_col].tolist(), "DS001_ONEILL TableS1C")
    if exclude_pure_ftd:
        cases = tc.loc[tc[grp_col].isin(["ALS", "ALS+FTD"]) & ~tc[sub_col].isin(["Discordant", "NA", "Control"])].copy()
    else:
        cases = tc.loc[tc[grp_col].isin(["ALS", "ALS+FTD", "FTD"]) & ~tc[sub_col].isin(["Discordant", "NA", "Control"])].copy()
    counts = cases[sub_col].value_counts().to_dict()
    n_cases = len(cases)
    return {
        "dataset_id": "DS001_ONEILL",
        "modality": assert_modality("RNASEQ_BULK_SUBTYPE", "DS001_ONEILL"),
        "exclude_pure_ftd": exclude_pure_ftd,
        "n_non_discordant_cases": n_cases,
        "subtype_counts": {str(k): int(v) for k, v in counts.items()},
        "subtype_fractions": {str(k): round(int(v) / max(n_cases, 1), 4) for k, v in counts.items()},
        "cases_df": cases,
        "full_table_s1c": tc,
    }


def load_zhang2026_spatial(genes: list[str] | None = None) -> dict[str, Any]:
    """Load Zhang et al. 2026 cervical spinal cord spatial DE (6d MN niche & 6i pTDP-43+ niche)."""
    p_z = resolve_dataset_path("DS031_ZHANG", verify_hash=True)
    mn = read_xlsx_sparse_safe(p_z, "6d_MN_ALS_vs._HC", header_row_1based=1)
    tdp = read_xlsx_sparse_safe(p_z, "6i_TDP43_ALS_vs._HC", header_row_1based=1)
    for df in (mn, tdp):
        for c in ("avg_log2FC", "p_val", "BH"):
            df[resolve_col(df, c)] = pd.to_numeric(df[resolve_col(df, c)], errors="coerce")
    if genes is not None:
        gset = set(genes)
        mn = mn.loc[mn[resolve_col(mn, "gene")].isin(gset)].copy()
        tdp = tdp.loc[tdp[resolve_col(tdp, "gene")].isin(gset)].copy()
    return {
        "dataset_id": "DS031_ZHANG",
        "modality": assert_modality("SPATIAL_VISIUM_PSEUDOBULK", "DS031_ZHANG"),
        "mn_niche_df": mn.reset_index(drop=True),
        "tdp43_niche_df": tdp.reset_index(drop=True),
    }


def _welch_and_mwu(case_vals: np.ndarray, ctrl_vals: np.ndarray) -> dict[str, float | int]:
    c_clean, n_clean = case_vals[np.isfinite(case_vals)], ctrl_vals[np.isfinite(ctrl_vals)]
    if len(c_clean) < 2 or len(n_clean) < 2:
        return {"n_case": len(c_clean), "n_ctrl": len(n_clean), "diff_log2cpm": float("nan"), "p_welch": 1.0, "p_mwu": 1.0}
    t_res = stats.ttest_ind(c_clean, n_clean, equal_var=False)
    u_res = stats.mannwhitneyu(c_clean, n_clean, alternative="two-sided")
    return {
        "n_case": int(len(c_clean)),
        "n_ctrl": int(len(n_clean)),
        "mean_case_log2cpm": round(float(np.mean(c_clean)), 4),
        "mean_ctrl_log2cpm": round(float(np.mean(n_clean)), 4),
        "diff_log2cpm": round(float(np.mean(c_clean) - np.mean(n_clean)), 4),
        "t_welch": round(float(t_res.statistic), 4),
        "p_welch": float(t_res.pvalue),
        "p_mwu": float(u_res.pvalue),
    }


def load_edinburgh_pseudobulk(
    cell_type: str,
    genes: list[str],
    region: str = "donor_collapsed",
    exclude_c9: bool = False,
    min_nuclei: int = 10,
) -> dict[str, Any]:
    """Donor-aware Edinburgh GSE290359 loader collapsing BA44+BA46 per Edinburgh ID before testing."""
    edir = resolve_dataset_path("DS_EDIN_PB")
    d3_rm = pd.read_csv(resolve_dataset_path("DS003_PB") / "row_metadata.tsv", sep="\t")
    sym_to_ens = dict(zip(d3_rm[resolve_col(d3_rm, "Gene")], d3_rm[resolve_col(d3_rm, "ENSEMBL")]))
    eg = pd.read_csv(edir / "genes.tsv", sep="\t")
    ens_to_gidx = dict(zip(eg[resolve_col(eg, "name")], eg[resolve_col(eg, "gene_index")]))
    gidx_to_sym = {int(ens_to_gidx[sym_to_ens[g]]): g for g in genes if g in sym_to_ens and sym_to_ens[g] in ens_to_gidx}
    cts = pd.read_csv(edir / "celltypes.tsv", sep="\t")
    ct_row = cts.loc[cts[resolve_col(cts, "label")] == cell_type]
    if ct_row.empty:
        raise ValueError(f"Unknown Edinburgh cell_type '{cell_type}'; options={cts['label'].tolist()}")
    ct_idx = int(ct_row.iloc[0][resolve_col(cts, "cell_type_index")])
    meta = pd.read_csv(edir / "library_metadata.tsv", sep="\t")
    nqc = pd.read_csv(edir / "nuclei_qc.tsv", sep="\t")
    nqc_ct = nqc.loc[nqc[resolve_col(nqc, "label")] == cell_type].set_index(resolve_col(nqc, "library"))

    c9_donors = {
        str(json.loads(str(r_m["Edinburgh ID"]))[0][0]).strip()
        for _, r_m in meta.iterrows()
        if "c9orf72" in str(json.loads(str(r_m["Mutation"]))[0][0]).lower()
    } if exclude_c9 else set()
    donor_acc: dict[str, dict[str, Any]] = {}
    for _, mr in meta.iterrows():
        lib = str(mr[resolve_col(meta, "library")])
        tis = str(json.loads(str(mr["Tissue"]))[0][0])
        if region in {"BA44", "BA46"} and tis != region:
            continue
        did = str(json.loads(str(mr["Edinburgh ID"]))[0][0]).strip()
        if did in c9_donors:
            continue
        is_als = str(json.loads(str(mr["Disease?"]))[0][0]).strip() == "Yes"
        nuc = int(nqc_ct.loc[lib, "n_nuclei"]) if lib in nqc_ct.index else 0
        t_umi = float(nqc_ct.loc[lib, "total_umi"]) if lib in nqc_ct.index else 0.0
        pb = pd.read_csv(edir / "pseudobulk" / f"{lib}.pseudobulk.tsv.gz", sep="\t")
        pb_ct = pb.loc[(pb["cell_type_index"] == ct_idx) & (pb["gene_index"].isin(gidx_to_sym))]
        rec = donor_acc.setdefault(did, {"donor_id": did, "is_als": is_als, "n_nuclei": 0, "total_umi": 0.0, "counts": {g: 0.0 for g in genes}})
        rec["n_nuclei"] += nuc
        rec["total_umi"] += t_umi
        for _, pr in pb_ct.iterrows():
            rec["counts"][gidx_to_sym[int(pr["gene_index"])]] += float(pr["sum"])

    kept = [v for v in donor_acc.values() if v["n_nuclei"] >= min_nuclei and v["total_umi"] > 0]
    assert_unique_donors([v["donor_id"] for v in kept], f"DS_EDIN_PB:{cell_type}:{region}")
    rows = [{"donor_id": v["donor_id"], "group": "ALS" if v["is_als"] else "Control", "n_nuclei": v["n_nuclei"], **{g: float(np.log2((v["counts"][g] / v["total_umi"]) * 1e6 + 1.0)) for g in genes}} for v in kept]
    df = pd.DataFrame(rows)
    stats_by_gene = {g: _welch_and_mwu(df.loc[df["group"] == "ALS", g].to_numpy(float), df.loc[df["group"] == "Control", g].to_numpy(float)) for g in genes if g in df.columns}
    return {"dataset_id": "DS_EDIN_PB", "modality": assert_modality("SNRNA_PSEUDOBULK_LOG2CPM", "DS_EDIN_PB"), "cell_type": cell_type, "region": region, "donor_df": df, "stats": stats_by_gene}


def load_pineda2024_pseudobulk(region: str, cell_type: str | list[str], genes: list[str], min_nuclei: int = 10) -> dict[str, Any]:
    """Donor-aware Pineda et al. 2024 (DS003_PB) loader resolving per-library .nuclei.tsv cell-type indices."""
    d3 = resolve_dataset_path("DS003_PB")
    rm = pd.read_csv(d3 / "row_metadata.tsv", sep="\t")
    rm["gene_index"] = np.arange(1, len(rm) + 1)
    g_sub = rm.loc[rm[resolve_col(rm, "Gene")].isin(genes)]
    gidx_to_sym = dict(zip(g_sub["gene_index"].astype(int), g_sub[resolve_col(rm, "Gene")].astype(str)))
    target_cts = set(PINEDA_COMPOSITE_CELLTYPES.get(cell_type, [cell_type]) if isinstance(cell_type, str) else cell_type)
    rep = pd.read_csv(d3 / "reduce_report.csv")
    rep = rep.loc[rep[resolve_col(rep, "region")] == region].copy()

    rows: list[dict[str, Any]] = []
    for _, rr in rep.iterrows():
        fld = str(rr[resolve_col(rep, "folder")])
        ndf = pd.read_csv(d3 / f"{fld}.nuclei.tsv", sep="\t")
        ndf["ct_idx"] = np.arange(len(ndf))
        matched = ndf.loc[ndf[resolve_col(ndf, "cell_type")].isin(target_cts)]
        n_nuc = int(matched[resolve_col(ndf, "nuclei")].sum())
        if n_nuc < min_nuclei:
            continue
        pb = pd.read_csv(d3 / f"{fld}.pseudobulk.tsv.gz", sep="\t")
        pb_ct = pb.loc[pb["cell_type_index"].isin(set(matched["ct_idx"].astype(int)))]
        tot_umi = float(pb_ct["sum"].sum())
        if tot_umi <= 0:
            continue
        g_sums = pb_ct.loc[pb_ct["gene_index"].isin(gidx_to_sym)].groupby("gene_index")["sum"].sum().to_dict()
        rows.append({"donor_id": f"D{int(rr['donor'])}", "group": str(rr["group"]), "n_nuclei": n_nuc, **{g: float(np.log2((float(g_sums.get(gi, 0.0)) / tot_umi) * 1e6 + 1.0)) for gi, g in gidx_to_sym.items()}})

    df = pd.DataFrame(rows)
    assert_unique_donors(df["donor_id"].tolist(), f"DS003_PB:{region}:{cell_type}")
    stats_by_gene = {g: _welch_and_mwu(df.loc[df["group"] == "SALS", g].to_numpy(float), df.loc[df["group"] == "PN", g].to_numpy(float)) for g in genes if g in df.columns}
    return {"dataset_id": "DS003_PB", "modality": assert_modality("SNRNA_PSEUDOBULK_LOG2CPM", "DS003_PB"), "region": region, "cell_type": cell_type, "donor_df": df, "stats": stats_by_gene}
