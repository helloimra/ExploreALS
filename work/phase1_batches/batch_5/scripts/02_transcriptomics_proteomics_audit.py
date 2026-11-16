"""RUN-B5-002: Donor-aware M1/BA9 snRNA-seq (DS003_PB), NYGC bulk (DS001), & CSF proteomics (DS045) audit."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.phase1_batches.batch_runner_utils import (
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_5" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CT_INDEX_TO_NAME = dict(
    zip(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19],
        [
            "5HT3aR", "Astro", "Endo", "Fibro", "L2_L3", "L3_L5", "L4_L5", "L4_L6",
            "L5", "L5_L6", "L6", "Micro", "Mural", "OPC", "Oligo", "PV", "Rosehip", "SOM", "T_Cell",
        ],
    )
)

TARGET_GENES = [
    "DRD1", "DRD2", "DRD3", "DRD4", "DRD5",
    "KCNQ2", "KCNQ3", "SCN8A", "SCN1A", "KCNA1", "KCNA2",
    "GRIA1", "GRIA2", "ADARB1", "GRIN1", "GRIN2A", "GRIN2B",
    "SLC1A2", "SLC12A2", "SLC12A5", "NPTX2",
]


def audit_ds003_pseudobulk() -> dict[str, object]:
    pb_dir = resolve_dataset_path("DS003_PB", verify_hash=False)
    rep = pd.read_csv(pb_dir / "reduce_report.csv")
    rm = pd.read_csv(pb_dir / "row_metadata.tsv", sep="\t")
    gene_col = resolve_col(rm, "Gene")
    ens_col = resolve_col(rm, "ENSEMBL")

    # Verify marker alignment on first library before extraction
    f_check = pd.read_csv(pb_dir / f"{rep.iloc[0]['folder']}.pseudobulk.tsv.gz", sep="\t")
    mbp_gi = int(rm.index[rm[gene_col] == "MBP"][0]) + 1
    aqp4_gi = int(rm.index[rm[gene_col] == "AQP4"][0]) + 1
    top_mbp = int(f_check.loc[f_check["gene_index"] == mbp_gi].sort_values("sum", ascending=False).iloc[0]["cell_type_index"])
    top_aqp = int(f_check.loc[f_check["gene_index"] == aqp4_gi].sort_values("sum", ascending=False).iloc[0]["cell_type_index"])
    assert CT_INDEX_TO_NAME[top_mbp] == "Oligo", f"MBP marker failed: {CT_INDEX_TO_NAME.get(top_mbp)}"
    assert CT_INDEX_TO_NAME[top_aqp] == "Astro", f"AQP4 marker failed: {CT_INDEX_TO_NAME.get(top_aqp)}"

    gene_to_gi = {
        g: int(rm.index[rm[gene_col] == g][0]) + 1
        for g in TARGET_GENES
        if (rm[gene_col] == g).any()
    }
    target_gis = set(gene_to_gi.values())
    gi_to_gene = {v: k for k, v in gene_to_gi.items()}

    rows: list[dict[str, object]] = []
    for _, meta in rep.iterrows():
        folder = str(meta["folder"])
        group = str(meta["group"])
        region = str(meta["region"])
        donor = str(meta["donor"])
        pb = pd.read_csv(pb_dir / f"{folder}.pseudobulk.tsv.gz", sep="\t")
        nuc = pd.read_csv(pb_dir / f"{folder}.nuclei.tsv", sep="\t")
        nuc_map = dict(zip(nuc["cell_type"], nuc["nuclei"]))
        lib_sizes = pb.groupby("cell_type_index")["sum"].sum().to_dict()
        sub = pb[pb["gene_index"].isin(target_gis)]
        cnt_lookup = {(int(r["gene_index"]), int(r["cell_type_index"])): int(r["sum"]) for _, r in sub.iterrows()}

        for cti, ct_name in CT_INDEX_TO_NAME.items():
            tot_umi = float(lib_sizes.get(cti, 0.0))
            n_nuc = int(nuc_map.get(ct_name, 0))
            if tot_umi <= 0 or n_nuc == 0:
                continue
            for g, gi in gene_to_gi.items():
                c = cnt_lookup.get((gi, cti), 0)
                cpm = (c / tot_umi) * 1e6
                rows.append({
                    "donor": donor, "group": group, "region": region, "cell_type": ct_name,
                    "nuclei": n_nuc, "total_umi": tot_umi, "gene": g, "count": c,
                    "cpm": cpm, "log2_cpm1": float(np.log2(cpm + 1.0)),
                })

    df_all = pd.DataFrame(rows)
    # 1. Dopamine receptor expression across M1 (BA4) cell types (donors with >=10 nuclei)
    drd_genes = ["DRD1", "DRD2", "DRD3", "DRD4", "DRD5"]
    ba4 = df_all[(df_all["region"] == "BA4") & (df_all["nuclei"] >= 10) & (df_all["group"].isin(["SALS", "PN"]))]
    drd_summary: list[dict[str, object]] = []
    for (ct, g), grp in ba4[ba4["gene"].isin(drd_genes)].groupby(["cell_type", "gene"]):
        drd_summary.append({
            "region": "BA4_M1", "cell_type": ct, "gene": g,
            "n_donors": int(len(grp)),
            "n_donors_count_ge_1": int((grp["count"] >= 1).sum()),
            "n_donors_cpm_ge_1": int((grp["cpm"] >= 1.0).sum()),
            "pct_donors_cpm_ge_1": float((grp["cpm"] >= 1.0).mean() * 100.0),
            "mean_cpm": float(grp["cpm"].mean()),
            "median_cpm": float(grp["cpm"].median()),
            "max_cpm": float(grp["cpm"].max()),
        })
    pd.DataFrame(drd_summary).to_csv(OUT_DIR / "ds003_m1_dopamine_receptors_by_celltype.csv", index=False)

    # 2. Excitability / transporter SALS vs PN donor-level DE in M1 (BA4, >=20 nuclei)
    focus_cts = ["L5", "L3_L5", "L5_L6", "L2_L3", "PV", "SOM", "Astro", "Oligo"]
    de_rows: list[dict[str, object]] = []
    ba4_20 = df_all[(df_all["region"] == "BA4") & (df_all["nuclei"] >= 20) & (df_all["group"].isin(["SALS", "PN"]))]
    for (ct, g), grp in ba4_20[ba4_20["cell_type"].isin(focus_cts)].groupby(["cell_type", "gene"]):
        sals_v = grp.loc[grp["group"] == "SALS", "log2_cpm1"].to_numpy()
        pn_v = grp.loc[grp["group"] == "PN", "log2_cpm1"].to_numpy()
        if len(sals_v) < 5 or len(pn_v) < 5:
            continue
        t_res = stats.ttest_ind(sals_v, pn_v, equal_var=False)
        u_res = stats.mannwhitneyu(sals_v, pn_v, alternative="two-sided")
        de_rows.append({
            "region": "BA4_M1", "cell_type": ct, "gene": g,
            "n_sals": int(len(sals_v)), "n_pn": int(len(pn_v)),
            "mean_cpm_sals": float(grp.loc[grp["group"] == "SALS", "cpm"].mean()),
            "mean_cpm_pn": float(grp.loc[grp["group"] == "PN", "cpm"].mean()),
            "diff_log2_cpm1_sals_minus_pn": float(np.mean(sals_v) - np.mean(pn_v)),
            "welch_t": float(t_res.statistic), "p_welch_2s": float(t_res.pvalue),
            "p_mwu_2s": float(u_res.pvalue),
        })
    de_df = pd.DataFrame(de_rows)
    de_df.to_csv(OUT_DIR / "ds003_m1_excitability_donor_de.csv", index=False)
    return {"drd_ba4_rows": len(drd_summary), "m1_de_rows": len(de_df)}


def audit_nygc_d001_spinal_and_cortical() -> dict[str, object]:
    meta = read_xlsx_sparse_safe(resolve_dataset_path("DS001_META", verify_hash=True), "GSE153960 Metadata", 1)
    samp_col = resolve_col(meta, "ExternalSampleId")
    subj_col = resolve_col(meta, "ExternalSubjectId")
    grp_col = resolve_col(meta, "Subject Group")
    reg_col = resolve_col(meta, "Sample Source")
    rin_col = resolve_col(meta, "RIN")

    feat = pd.read_csv(resolve_dataset_path("DS001_FEAT", verify_hash=True))
    sym_col = resolve_col(feat, "ucsd_label")
    ver_col = resolve_col(feat, "nygc_exact_versioned_ids")
    feat_sub = feat[feat[sym_col].isin(TARGET_GENES) & feat[ver_col].notna()].copy()
    ens_to_sym = {str(r[ver_col]).strip(): str(r[sym_col]).strip() for _, r in feat_sub.iterrows()}

    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    gc_ens_col = resolve_col(gc_df, "Gene stable ID")
    gc_pct_col = resolve_col(gc_df, "Gene % GC content")
    gc_map = dict(zip(gc_df[gc_ens_col].astype(str), pd.to_numeric(gc_df[gc_pct_col], errors="coerce")))

    cnt_path = resolve_dataset_path("DS001_COUNTS", verify_hash=True)
    with gzip.open(cnt_path, "rt", encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        first_data = fh.readline().rstrip("\n").split("\t")
        # R write.table has 1 extra leading row-number column vs header
        has_row_num = len(first_data) == len(hdr) + 1 and first_data[1].startswith("ENSG")
        sample_ids = hdr[1:] if has_row_num else hdr[1:]
        n_samp = len(sample_ids)
        lib_totals = np.zeros(n_samp, dtype=np.float64)
        gc_weighted_num = np.zeros(n_samp, dtype=np.float64)
        gc_weighted_den = np.zeros(n_samp, dtype=np.float64)
        gene_counts: dict[str, np.ndarray] = {}

        def _proc_line(parts: list[str]) -> None:
            ens_ver = parts[1] if has_row_num else parts[0]
            arr = np.fromiter((float(x) for x in (parts[2:] if has_row_num else parts[1:])), dtype=np.float64, count=n_samp)
            lib_totals[:] += arr
            ens_base = ens_ver.split(".")[0]
            gc_v = gc_map.get(ens_base)
            if gc_v is not None and np.isfinite(gc_v):
                gc_weighted_num[:] += arr * gc_v
                gc_weighted_den[:] += arr
            if ens_ver in ens_to_sym:
                gene_counts[ens_to_sym[ens_ver]] = arr

        _proc_line(first_data)
        for line in fh:
            _proc_line(line.rstrip("\n").split("\t"))

    sample_gc_index = gc_weighted_num / np.maximum(gc_weighted_den, 1.0)
    idx_map = {sid: i for i, sid in enumerate(sample_ids)}

    meta = meta[meta[samp_col].astype(str).isin(idx_map)].copy()
    meta["col_idx"] = meta[samp_col].astype(str).map(idx_map)
    meta["rin_num"] = pd.to_numeric(meta[rin_col], errors="coerce")
    meta["region_clean"] = meta[reg_col].astype(str).replace({
        "Cortex_Motor_Medial": "Cortex_Motor",
        "Cortex_Motor_Lateral": "Cortex_Motor",
        "Cortex_Motor_Unspecified": "Cortex_Motor",
    })
    meta["arm"] = meta[grp_col].astype(str).map({
        "ALS Spectrum MND": "ALS",
        "ALS Spectrum MND, Other Neurological Disorders": "ALS",
        "Non-Neurological Control": "CTRL",
    })
    meta = meta[meta["arm"].isin(["ALS", "CTRL"])].sort_values("rin_num", ascending=False)
    # Strict donor deduplication within each region
    meta_dedup = meta.drop_duplicates(subset=["region_clean", subj_col], keep="first").copy()

    focus_regions = ["Spinal_Cord_Lumbar", "Spinal_Cord_Cervical", "Cortex_Motor", "Cortex_Frontal"]
    nygc_rows: list[dict[str, object]] = []
    for reg in focus_regions:
        sub_m = meta_dedup[meta_dedup["region_clean"] == reg].copy()
        cidx = sub_m["col_idx"].to_numpy(dtype=int)
        is_als = (sub_m["arm"] == "ALS").to_numpy(dtype=float)
        rin_v = sub_m["rin_num"].fillna(sub_m["rin_num"].median()).to_numpy(dtype=float)
        gc_idx = sample_gc_index[cidx]
        libs = lib_totals[cidx]

        for g, cnt_vec in sorted(gene_counts.items()):
            cpm = (cnt_vec[cidx] / np.maximum(libs, 1.0)) * 1e6
            y = np.log2(cpm + 1.0)
            als_m = is_als == 1.0
            ctrl_m = is_als == 0.0
            t_unadj = stats.ttest_ind(y[als_m], y[ctrl_m], equal_var=False)
            X_adj = sm.add_constant(np.column_stack([is_als, rin_v, gc_idx]))
            ols_adj = sm.OLS(y, X_adj).fit()
            nygc_rows.append({
                "region": reg, "gene": g,
                "n_als_donors": int(als_m.sum()), "n_ctrl_donors": int(ctrl_m.sum()),
                "median_cpm_als": float(np.median(cpm[als_m])),
                "median_cpm_ctrl": float(np.median(cpm[ctrl_m])),
                "pct_als_cpm_ge_1": float(np.mean(cpm[als_m] >= 1.0) * 100.0),
                "pct_ctrl_cpm_ge_1": float(np.mean(cpm[ctrl_m] >= 1.0) * 100.0),
                "diff_log2_cpm1_unadj": float(np.mean(y[als_m]) - np.mean(y[ctrl_m])),
                "p_welch_unadj": float(t_unadj.pvalue),
                "beta_als_adj_rin_gc": float(ols_adj.params[1]),
                "p_ols_adj_rin_gc": float(ols_adj.pvalues[1]),
            })
    nygc_df = pd.DataFrame(nygc_rows)
    nygc_df.to_csv(OUT_DIR / "ds001_nygc_spinal_motor_frontal_audit.csv", index=False)
    return {"nygc_rows": len(nygc_df), "genes_mapped": sorted(gene_counts.keys())}


def audit_ds045_csf_proteomics() -> dict[str, object]:
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    t6 = read_xlsx_sparse_safe(p45, "6-TMT-MS ANOVA", header_row_1based=2)
    t8 = read_xlsx_sparse_safe(p45, "8-DIA ANOVA", header_row_1based=2)
    t9 = read_xlsx_sparse_safe(p45, "9-WGCNA kME", header_row_1based=2)

    id6 = resolve_col(t6, "Protein|Uniprot")
    p6_sc = resolve_col(t6, "Sporadic-Control")
    d6_sc = resolve_col(t6, "diff Sporadic-Control")

    id8 = resolve_col(t8, "Protein|Uniprot")
    p8_sc = resolve_col(t8, "sALS-Control")
    d8_sc = resolve_col(t8, "diff sALS-Control")
    p8_ac = resolve_col(t8, "ALS-Control")
    d8_ac = resolve_col(t8, "diff ALS-Control")

    id9 = resolve_col(t9, "UniqueID")
    mod9 = resolve_col(t9, "net$colors")
    kme_turq = resolve_col(t9, "kMEturquoise")

    targets = ("NPTX2|", "NPTXR|", "NPTX1|", "GRIA4|", "SLC1A2|")
    csf_out: dict[str, dict[str, object]] = {}
    for pref in targets:
        sym = pref.rstrip("|")
        entry: dict[str, object] = {}
        h6 = t6[t6[id6].astype(str).str.startswith(pref)]
        if not h6.empty:
            r = h6.iloc[0]
            entry["tmt_n101_sals_vs_ctrl"] = {
                "id": str(r[id6]), "diff_log2": float(r[d6_sc]), "p_value": float(r[p6_sc]),
            }
        h8 = t8[t8[id8].astype(str).str.startswith(pref)]
        if not h8.empty:
            r = h8.iloc[0]
            entry["dia_n259_sals_vs_ctrl"] = {
                "id": str(r[id8]), "diff_log2": float(r[d8_sc]), "p_value": float(r[p8_sc]),
                "als_vs_ctrl_diff_log2": float(r[d8_ac]), "als_vs_ctrl_p_value": float(r[p8_ac]),
            }
        h9 = t9[t9[id9].astype(str).str.startswith(pref)]
        if not h9.empty:
            r = h9.iloc[0]
            entry["wgcna_tmt"] = {"module": str(r[mod9]), "kME_turquoise": float(r[kme_turq])}
        csf_out[sym] = entry
    (OUT_DIR / "ds045_csf_synaptic_proteomics.json").write_text(json.dumps(csf_out, indent=2), encoding="utf-8")
    return csf_out


if __name__ == "__main__":
    s3 = audit_ds003_pseudobulk()
    s1 = audit_nygc_d001_spinal_and_cortical()
    s45 = audit_ds045_csf_proteomics()
    summary = {"ds003_summary": s3, "ds001_summary": s1, "ds045_synaptic": s45}
    (OUT_DIR / "omics_proteomics_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("RUN-B5-002 complete:", json.dumps(summary, indent=2))
