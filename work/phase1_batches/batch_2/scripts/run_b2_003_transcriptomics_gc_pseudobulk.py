"""RUN-B2-003: Donor-level postmortem bulk RNA-seq (NYGC + GC/composition refit) and snRNA-seq pseudobulks (Pineda D003, Edinburgh GSE290359)."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase1_batches.batch_runner_utils import resolve_col, resolve_dataset_path  # noqa: E402

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_2" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_GENES = [
    "SCFD1", "G2E3", "YKT6", "SEC22B", "STX5", "GOSR1", "NSF", "GDI2",
    "FBXL5", "IREB2", "ACO1", "TFRC", "FTH1", "FTL", "FNTA", "PTAR1",
]
MARKERS_NEURON = ["RBFOX3", "SNAP25", "SYT1"]
MARKERS_GLIA = ["GFAP", "AQP4", "MOG", "C1QA"]


def load_gc_map() -> dict[str, dict]:
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    id_col = resolve_col(gc_df, "Gene stable ID")
    nm_col = resolve_col(gc_df, "Gene name")
    gc_col = resolve_col(gc_df, "Gene % GC content")
    by_ens = {str(r[id_col]).strip(): float(r[gc_col]) for _, r in gc_df.iterrows() if pd.notna(r[gc_col])}
    by_sym = {str(r[nm_col]).strip(): float(r[gc_col]) for _, r in gc_df.iterrows() if pd.notna(r[nm_col]) and pd.notna(r[gc_col])}
    return {"by_ens": by_ens, "by_sym": by_sym}


def analyze_nygc(gc_maps: dict) -> dict:
    feat = pd.read_csv(resolve_dataset_path("DS001_FEAT", verify_hash=True))
    sym_col = resolve_col(feat, "ucsd_label")
    ens_col = resolve_col(feat, "nygc_exact_versioned_ids")
    wanted_syms = set(TARGET_GENES + MARKERS_NEURON + MARKERS_GLIA)
    sym_to_ens = {
        str(r[sym_col]).strip(): str(r[ens_col]).strip()
        for _, r in feat.iterrows()
        if str(r[sym_col]).strip() in wanted_syms and pd.notna(r[ens_col]) and ";" not in str(r[ens_col])
    }
    ens_to_sym = {v: k for k, v in sym_to_ens.items()}

    # Stream NYGC_counts.txt.gz once to compute library sizes, sample GC index, and extract wanted genes
    counts_path = resolve_dataset_path("DS001_COUNTS", verify_hash=True)
    with gzip.open(counts_path, "rt", encoding="utf-8") as fh:
        header = fh.readline().strip().split("\t")
        sample_ids = header[1:]
        n_samp = len(sample_ids)
        lib_sizes = np.zeros(n_samp, dtype=np.float64)
        hi_gc_sum = np.zeros(n_samp, dtype=np.float64)
        lo_gc_sum = np.zeros(n_samp, dtype=np.float64)
        extracted: dict[str, np.ndarray] = {}
        for line_idx, line in enumerate(fh):
            parts = line.rstrip("\n").split("\t")
            ens_ver = parts[1] if len(parts) == n_samp + 2 else parts[0]
            vals = np.fromiter((float(x) for x in (parts[2:] if len(parts) == n_samp + 2 else parts[1:])), dtype=np.float64, count=n_samp)
            lib_sizes += vals
            ens_base = ens_ver.split(".")[0]
            gc_val = gc_maps["by_ens"].get(ens_base)
            if gc_val is not None and line_idx % 5 == 0:
                if gc_val >= 55.0:
                    hi_gc_sum += vals
                elif gc_val <= 42.0:
                    lo_gc_sum += vals
            if ens_ver in ens_to_sym:
                extracted[ens_to_sym[ens_ver]] = vals

    cpm_log = {g: np.log2(v / np.maximum(lib_sizes, 1.0) * 1e6 + 1.0) for g, v in extracted.items()}
    gc_index = np.log2((hi_gc_sum + 1.0) / (lo_gc_sum + 1.0))
    neur_idx = np.mean([cpm_log[m] for m in MARKERS_NEURON if m in cpm_log], axis=0)
    glia_idx = np.mean([cpm_log[m] for m in MARKERS_GLIA if m in cpm_log], axis=0)

    sample_df = pd.DataFrame({"sample_col": sample_ids, "base_id": [s.split("-2")[0] if s.endswith("-2") else s for s in sample_ids],
                              "gc_index": gc_index, "neur_idx": neur_idx, "glia_idx": glia_idx})
    for g in TARGET_GENES:
        if g in cpm_log:
            sample_df[g] = cpm_log[g]

    meta = pd.read_excel(resolve_dataset_path("DS001_META", verify_hash=True))
    ext_col = resolve_col(meta, "ExternalSampleId")
    subj_col = resolve_col(meta, "ExternalSubjectId")
    grp_col = resolve_col(meta, "Subject Group")
    reg_col = resolve_col(meta, "Sample Source")
    rin_col = resolve_col(meta, "RIN")
    sex_col = resolve_col(meta, "Sex")
    merged = sample_df.merge(meta[[ext_col, subj_col, grp_col, reg_col, rin_col, sex_col]], left_on="sample_col", right_on=ext_col, how="left")
    unmatched = merged[ext_col].isna()
    if unmatched.any():
        m2 = sample_df.loc[unmatched].merge(meta[[ext_col, subj_col, grp_col, reg_col, rin_col, sex_col]], left_on="base_id", right_on=ext_col, how="left")
        merged.loc[unmatched, [ext_col, subj_col, grp_col, reg_col, rin_col, sex_col]] = m2[[ext_col, subj_col, grp_col, reg_col, rin_col, sex_col]].values

    merged["is_als"] = np.where(merged[grp_col].astype(str).str.startswith("ALS Spectrum MND"), 1.0,
                       np.where(merged[grp_col].astype(str) == "Non-Neurological Control", 0.0, np.nan))
    merged["region_group"] = np.where(merged[reg_col].astype(str).str.startswith("Cortex_Motor"), "Motor_Cortex",
                             np.where(merged[reg_col].astype(str) == "Cortex_Frontal", "Frontal_Cortex",
                             np.where(merged[reg_col].astype(str).str.startswith("Spinal_Cord"), "Spinal_Cord", "Other")))

    results: dict[str, dict] = {}
    for reg in ["Motor_Cortex", "Frontal_Cortex", "Spinal_Cord"]:
        sub = merged[(merged["region_group"] == reg) & merged["is_als"].notna()].drop_duplicates(subset=[subj_col]).copy()
        sub["rin_num"] = pd.to_numeric(sub[rin_col], errors="coerce")
        sub["sex_m"] = (sub[sex_col].astype(str) == "Male").astype(float)
        reg_out = {}
        for g in TARGET_GENES:
            if g not in sub.columns:
                continue
            d1 = sub[["is_als", g]].dropna()
            m_unadj = sm.OLS(d1[g], sm.add_constant(d1[["is_als"]])).fit(cov_type="HC3")
            d2 = sub[["is_als", "rin_num", "sex_m", "gc_index", "neur_idx", "glia_idx", g]].dropna()
            m_adj = sm.OLS(d2[g], sm.add_constant(d2[["is_als", "rin_num", "sex_m", "gc_index", "neur_idx", "glia_idx"]])).fit(cov_type="HC3")
            reg_out[g] = {
                "n_als": int((d2["is_als"] == 1).sum()), "n_ctrl": int((d2["is_als"] == 0).sum()),
                "unadj_beta": float(m_unadj.params["is_als"]), "unadj_p": float(m_unadj.pvalues["is_als"]),
                "adj_beta": float(m_adj.params["is_als"]), "adj_p": float(m_adj.pvalues["is_als"]),
                "gc_beta": float(m_adj.params["gc_index"]), "gc_p": float(m_adj.pvalues["gc_index"]),
            }
        results[reg] = reg_out
    return results


def analyze_d003_pseudobulk() -> dict:
    d_dir = resolve_dataset_path("DS003_PB")
    rep = pd.read_csv(d_dir / "reduce_report.csv")
    row_meta = pd.read_csv(d_dir / "row_metadata.tsv", sep="\t")
    row_meta["gene_index"] = np.arange(1, len(row_meta) + 1)
    g_map = {
        int(r["gene_index"]): str(r["Gene"]).strip()
        for _, r in row_meta.iterrows()
        if str(r["Gene"]).strip() in set(TARGET_GENES)
    }

    records = []
    for _, r in rep.iterrows():
        stem = str(r["folder"]).strip()
        pb_f = d_dir / f"{stem}.pseudobulk.tsv.gz"
        nuc_f = d_dir / f"{stem}.nuclei.tsv"
        if not pb_f.exists() or not nuc_f.exists():
            continue
        nuc_df = pd.read_csv(nuc_f, sep="\t")
        ct_map = {i: str(ct).strip() for i, ct in enumerate(nuc_df["cell_type"])}
        pb = pd.read_csv(pb_f, sep="\t")
        pb["ct"] = pb["cell_type_index"].map(ct_map)
        pb["broad_ct"] = np.where(pb["ct"].isin({"L2_L3", "L3_L5", "L4_L5", "L4_L6", "L5", "L5_L6", "L6"}), "Excitatory",
                         np.where(pb["ct"] == "Oligo", "Oligo",
                         np.where(pb["ct"] == "Micro", "Micro",
                         np.where(pb["ct"] == "Astro", "Astro", "Other"))))
        totals = pb.groupby("broad_ct")["sum"].sum().to_dict()
        sub = pb[pb["gene_index"].isin(g_map)].copy()
        sub["gene"] = sub["gene_index"].map(g_map)
        agg = sub.groupby(["broad_ct", "gene"])["sum"].sum().reset_index()
        for bct in ["Excitatory", "Oligo", "Micro", "Astro"]:
            tot = totals.get(bct, 0.0)
            if tot < 10_000:
                continue
            g_sums = dict(zip(agg.loc[agg["broad_ct"] == bct, "gene"], agg.loc[agg["broad_ct"] == bct, "sum"]))
            for g in TARGET_GENES:
                records.append({
                    "donor": str(r["donor"]), "region": str(r["region"]), "group": str(r["group"]),
                    "broad_ct": bct, "gene": g, "log2_cpm1": float(np.log2(g_sums.get(g, 0.0) / tot * 1e6 + 1.0)),
                })

    df_all = pd.DataFrame(records).groupby(["region", "broad_ct", "donor", "group", "gene"], as_index=False)["log2_cpm1"].mean()
    out: dict[str, dict] = {}
    for (reg, bct), grp_df in df_all.groupby(["region", "broad_ct"]):
        key = f"{reg}_{bct}"
        out[key] = {}
        for g, gdf in grp_df.groupby("gene"):
            vs = gdf.loc[gdf["group"] == "SALS", "log2_cpm1"].values
            vc = gdf.loc[gdf["group"] == "PN", "log2_cpm1"].values
            if len(vs) > 1 and len(vc) > 1:
                out[key][g] = {
                    "n_sals": int(len(vs)), "n_pn": int(len(vc)),
                    "log2FC_sals_vs_pn": float(np.mean(vs) - np.mean(vc)),
                    "welch_p": float(stats.ttest_ind(vs, vc, equal_var=False).pvalue),
                    "mwu_p": float(stats.mannwhitneyu(vs, vc).pvalue),
                }
    return out


def analyze_edinburgh_pseudobulk() -> dict:
    e_dir = resolve_dataset_path("DS_EDIN_PB")
    genes_df = pd.read_csv(e_dir / "genes.tsv", sep="\t")
    feat = pd.read_csv(resolve_dataset_path("DS001_FEAT"))
    ens_to_sym = {
        str(r["gencode_v30_gene_ids"]).split(".")[0]: str(r["ucsd_label"]).strip()
        for _, r in feat.iterrows()
        if str(r["ucsd_label"]).strip() in set(TARGET_GENES) and ";" not in str(r["gencode_v30_gene_ids"])
    }
    g_map = {int(r["gene_index"]): ens_to_sym[str(r["name"]).split(".")[0]] for _, r in genes_df.iterrows() if str(r["name"]).split(".")[0] in ens_to_sym}
    ct_df = pd.read_csv(e_dir / "celltypes.tsv", sep="\t")
    ct_map = dict(zip(ct_df["cell_type_index"], ct_df["label"]))
    lm = pd.read_csv(e_dir / "library_metadata.tsv", sep="\t")

    records = []
    for _, r in lm.iterrows():
        lib = str(r["library"]).strip()
        pb_f = e_dir / "pseudobulk" / f"{lib}.pseudobulk.tsv.gz"
        if not pb_f.exists():
            continue
        is_als = 1 if '"Yes"' in str(r["Disease?"]) else 0
        donor = str(r["Edinburgh ID"]).strip()
        pb = pd.read_csv(pb_f, sep="\t")
        pb["ct"] = pb["cell_type_index"].map(ct_map)
        totals = pb.groupby("ct")["sum"].sum().to_dict()
        sub = pb[pb["gene_index"].isin(g_map)].copy()
        sub["gene"] = sub["gene_index"].map(g_map)
        agg = sub.groupby(["ct", "gene"])["sum"].sum().reset_index()
        for ct_name in ["Excitatory neuron", "Oligodendrocyte", "Astrocyte", "Microglia"]:
            tot = totals.get(ct_name, 0.0)
            if tot < 10_000:
                continue
            g_sums = dict(zip(agg.loc[agg["ct"] == ct_name, "gene"], agg.loc[agg["ct"] == ct_name, "sum"]))
            for g in TARGET_GENES:
                records.append({"donor": donor, "is_als": is_als, "ct": ct_name, "gene": g,
                                "log2_cpm1": float(np.log2(g_sums.get(g, 0.0) / tot * 1e6 + 1.0))})

    df_all = pd.DataFrame(records).groupby(["ct", "donor", "is_als", "gene"], as_index=False)["log2_cpm1"].mean()
    out: dict[str, dict] = {}
    for ct_name, cdf in df_all.groupby("ct"):
        out[ct_name] = {}
        for g, gdf in cdf.groupby("gene"):
            vs = gdf.loc[gdf["is_als"] == 1, "log2_cpm1"].values
            vc = gdf.loc[gdf["is_als"] == 0, "log2_cpm1"].values
            if len(vs) > 1 and len(vc) > 1:
                out[ct_name][g] = {
                    "n_als_donors": int(len(vs)), "n_ctrl_donors": int(len(vc)),
                    "log2FC_als_vs_ctrl": float(np.mean(vs) - np.mean(vc)),
                    "welch_p": float(stats.ttest_ind(vs, vc, equal_var=False).pvalue),
                }
    return out


if __name__ == "__main__":
    gc_maps = load_gc_map()
    payload = {
        "gene_gc_pct": {g: gc_maps["by_sym"].get(g) for g in TARGET_GENES},
        "nygc_bulk_d001": analyze_nygc(gc_maps),
        "pineda_snrna_d003": analyze_d003_pseudobulk(),
        "edinburgh_snrna_gse290359": analyze_edinburgh_pseudobulk(),
    }
    out_p = OUT_DIR / "b2_003_transcriptomics_gc_pseudobulk.json"
    out_p.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[RUN-B2-003] Wrote {out_p} ({out_p.stat().st_size:,} bytes)")
