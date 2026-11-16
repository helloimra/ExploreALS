"""RUN-B6-002: NYGC bulk composition/GC refit, Spillman & Trautwig proteomics,
TDP-43 splicing/APA check, and O'Neill 2025 ALS-TE subtype prevalence audit.
"""
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

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_6" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "AGAP2", "AP1G2", "BRSK2", "DNAJB2", "KIFC2",
    "MIB2", "MYO18A", "SNPH", "ZNF783", "CAPG", "SARM1", "NEFH",
]
MARKERS = {
    "neuron": ["SNAP25", "SYT1", "RBFOX3", "SLC17A7"],
    "oligo": ["MOBP", "PLP1", "MBP", "MOG"],
    "micro": ["AIF1", "TYROBP", "CSF1R", "C1QA"],
    "astro": ["AQP4", "GFAP", "ALDH1L1"],
}


def fit_ols(y: np.ndarray, g: np.ndarray, X_cov: np.ndarray | None = None) -> dict:
    m = np.isfinite(y) & np.isfinite(g)
    if X_cov is not None:
        m &= np.all(np.isfinite(X_cov), axis=1)
    ym, gm = y[m], g[m]
    X = np.column_stack([np.ones(len(gm)), gm] + ([X_cov[m]] if X_cov is not None else []))
    res = sm.OLS(ym, X).fit()
    return {"n_case": int(np.sum(gm == 1)), "n_ctrl": int(np.sum(gm == 0)),
            "beta_log2fc": float(res.params[1]), "se": float(res.bse[1]),
            "t": float(res.tvalues[1]), "p_two": float(res.pvalues[1])}


def main() -> None:
    # 1. NYGC bulk RNA-seq streaming + GC & cell-composition adjustment
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF"), sep="\t")
    ens_gc = gc_df.set_index(resolve_col(gc_df, "Gene stable ID"))[resolve_col(gc_df, "Gene % GC content")].to_dict()
    feat = pd.read_csv(resolve_dataset_path("DS001_FEAT"))
    c_sym, c_vid = resolve_col(feat, "ucsd_label"), resolve_col(feat, "nygc_exact_versioned_ids")
    want_syms = set(TARGETS) | {g for lst in MARKERS.values() for g in lst}
    vid_to_sym = feat[feat[c_sym].isin(want_syms)].dropna(subset=[c_vid]).set_index(c_vid)[c_sym].to_dict()

    cnt_path = resolve_dataset_path("DS001_COUNTS")
    with gzip.open(cnt_path, "rt", encoding="utf-8") as fh:
        hdr = fh.readline().strip().split("\t")
        samples = hdr[1:] if hdr[0] == "EnsemblID" else hdr
        n_s = len(samples)
        lib_sum = np.zeros(n_s, dtype=np.float64)
        hi_gc_sum = np.zeros(n_s, dtype=np.float64)
        lo_gc_sum = np.zeros(n_s, dtype=np.float64)
        gene_mat: dict[str, np.ndarray] = {}
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            vid = parts[1] if len(parts) == n_s + 2 else parts[0]
            arr = np.fromiter((float(x) for x in (parts[2:] if len(parts) == n_s + 2 else parts[1:])), dtype=np.float64, count=n_s)
            lib_sum += arr
            gcv = ens_gc.get(vid.split(".")[0])
            if gcv is not None:
                if gcv >= 60.0:
                    hi_gc_sum += arr
                elif gcv <= 42.0:
                    lo_gc_sum += arr
            if vid in vid_to_sym:
                gene_mat[vid_to_sym[vid]] = arr

    meta = pd.read_excel(resolve_dataset_path("DS001_META"))
    cs_id = resolve_col(meta, "ExternalSampleId")
    cd_id = resolve_col(meta, "ExternalSubjectId")
    c_reg = resolve_col(meta, "Sample Source")
    c_rin = resolve_col(meta, "RIN")
    c_grp = resolve_col(meta, "disease_group")
    c_mut = resolve_col(meta, "Reported Genomic Mutations")
    s_idx = {s: i for i, s in enumerate(samples)}
    meta = meta[meta[cs_id].isin(s_idx)].copy()
    meta["s_i"] = meta[cs_id].map(s_idx)
    mut_str = meta[c_mut].fillna("None").astype(str)
    meta = meta[(meta[c_grp].isin(["ALS-TDP", "Control"])) & (~mut_str.str.contains("C9orf72|SOD1|FUS|TARDBP", case=False, regex=True))].copy()
    meta["is_sals"] = (meta[c_grp] == "ALS-TDP").astype(float)
    meta["gc_ratio_log2"] = np.log2((hi_gc_sum[meta["s_i"]] + 1.0) / (lo_gc_sum[meta["s_i"]] + 1.0))
    for g, arr in gene_mat.items():
        meta[f"l2cpm_{g}"] = np.log2(arr[meta["s_i"]] / lib_sum[meta["s_i"]] * 1e6 + 1.0)

    nygc_results = []
    reg_groups = {
        "NYGC_Frontal": ["Cortex_Frontal"],
        "NYGC_Motor": ["Cortex_Motor_Medial", "Cortex_Motor_Lateral"],
        "NYGC_Cervical_SC": ["Spinal_Cord_Cervical"],
    }
    for rlabel, rlist in reg_groups.items():
        sub = meta[meta[c_reg].isin(rlist)].drop_duplicates(subset=[cd_id]).copy()
        for mname, mgenes in MARKERS.items():
            zs = [stats.zscore(sub[f"l2cpm_{mg}"], nan_policy="omit") for mg in mgenes if f"l2cpm_{mg}" in sub]
            sub[f"idx_{mname}"] = np.nanmean(np.vstack(zs), axis=0)
        cov_rg = sub[[c_rin, "gc_ratio_log2"]].to_numpy(dtype=float)
        cov_full = sub[[c_rin, "gc_ratio_log2", "idx_neuron", "idx_oligo", "idx_micro", "idx_astro"]].to_numpy(dtype=float)
        for g in TARGETS:
            if f"l2cpm_{g}" not in sub:
                continue
            yv, gv = sub[f"l2cpm_{g}"].to_numpy(), sub["is_sals"].to_numpy()
            nygc_results.append({
                "region": rlabel, "gene": g,
                "unadj": fit_ols(yv, gv),
                "rin_gc_adj": fit_ols(yv, gv, cov_rg),
                "full_comp_gc_adj": fit_ols(yv, gv, cov_full),
            })

    # 2. Spillman 2026 Cortex & iPSC DIA Proteomics + RNA-seq
    sp_dir = resolve_dataset_path("DS029_SPILL")
    sp_piv = pd.read_csv(sp_dir / "172_0005_02A_FRCTXonly_Report_IMSSR_ProteinQuant_Pivot.tsv", sep="\t")
    cg = resolve_col(sp_piv, "PG.Genes")
    q_cols = [c for c in sp_piv.columns if c.endswith(".PG.Quantity")]
    l2_mat = np.log2(sp_piv[q_cols].apply(pd.to_numeric, errors="coerce").replace(0, np.nan))
    l2_mat = l2_mat.subtract(l2_mat.median(axis=0), axis=1)
    spillman_res = []
    sp_genes_list = sp_piv[cg].fillna("").astype(str).str.split(";")
    for g in TARGETS:
        m = sp_genes_list.apply(lambda xs: g in [x.strip() for x in xs])
        if not m.any():
            continue
        r0 = l2_mat.loc[m].iloc[0]
        for frac in ["Homogenate_FRCTX", "Synapt_FRCTX"]:
            ctrl = r0[[c for c in q_cols if frac in c and "Control" in c]].dropna().to_numpy()
            case = r0[[c for c in q_cols if frac in c and "C9FTD" in c]].dropna().to_numpy()
            if len(ctrl) >= 3 and len(case) >= 3:
                t_s, p_s = stats.ttest_ind(case, ctrl, equal_var=False)
                spillman_res.append({"assay": f"Spillman_{frac}_DIA", "gene": g, "n_case": len(case), "n_ctrl": len(ctrl),
                                     "log2fc_c9ftd_vs_ctrl": float(np.mean(case) - np.mean(ctrl)), "t": float(t_s), "p_two": float(p_s)})

    sp_ipsc = read_xlsx_sparse_safe(sp_dir / "401_2026_3084_MOESM3_ESM.xlsx", "Sheet1", 1)
    cig = resolve_col(sp_ipsc, "Gene")
    for g in TARGETS:
        sub = sp_ipsc[sp_ipsc[cig].fillna("").astype(str).str.strip() == g]
        if sub.empty:
            continue
        r0 = sub.iloc[0]
        for tag, lbl in [("xHOx", "Spillman_iPSC_Homogenate_DIA"), ("xP2x", "Spillman_iPSC_Synaptosome_DIA")]:
            ctrl = pd.to_numeric(pd.Series([r0[c] for c in sp_ipsc.columns if tag in c and "CTRL" in c]), errors="coerce").dropna().to_numpy()
            case = pd.to_numeric(pd.Series([r0[c] for c in sp_ipsc.columns if tag in c and "C9FTD" in c]), errors="coerce").dropna().to_numpy()
            if len(ctrl) >= 2 and len(case) >= 2:
                t_s, p_s = stats.ttest_ind(case, ctrl, equal_var=False)
                spillman_res.append({"assay": lbl, "gene": g, "n_case": len(case), "n_ctrl": len(ctrl),
                                     "log2fc_c9ftd_vs_ctrl": float(np.mean(case) - np.mean(ctrl)), "t": float(t_s), "p_two": float(p_s)})

    # 3. Trautwig 2025 CSF TMT (N=101) & DIA (N=259)
    tr_xlsx = resolve_dataset_path("DS045_TRAUT")
    tr_res = []
    for sh, pcol, dcol in [("6-TMT-MS ANOVA", "Sporadic-Control", "diff Sporadic-Control"), ("8-DIA ANOVA", "sALS-Control", "diff sALS-Control")]:
        dt = read_xlsx_sparse_safe(tr_xlsx, sh, 2)
        cp = resolve_col(dt, "Protein|Uniprot")
        p_c = resolve_col(dt, pcol)
        d_c = resolve_col(dt, dcol) if any(dcol.lower() in str(c).lower() for c in dt.columns) else resolve_col(dt, "diff ALS-Control")
        for g in TARGETS:
            hit = dt[dt[cp].fillna("").astype(str).str.startswith(f"{g}|")]
            for r in hit.to_dict(orient="records"):
                tr_res.append({"sheet": sh, "protein": str(r[cp]), "gene": g, "diff_col": d_c,
                               "log2fc": float(pd.to_numeric(r[d_c], errors="coerce")),
                               "p_sals_vs_ctrl": float(pd.to_numeric(r[p_c], errors="coerce"))})

    # 4. TDP-43 Cryptic Splicing (Bryce-Smith 2025) & APA (Zeng 2025)
    zeng = pd.read_excel(resolve_dataset_path("DS_ZENG_APA"), sheet_name="S2")
    bs = pd.read_excel(resolve_dataset_path("DS_BRYCE_APA"), sheet_name="Supplementary_Table_2")
    apa_hits = zeng[zeng[resolve_col(zeng, "gene_name")].isin(TARGETS)].to_dict(orient="records")
    ce_hits = bs[bs[resolve_col(bs, "gene_name")].isin(TARGETS)].to_dict(orient="records")

    # 5. O'Neill 2025 ALS-TE subtype prevalence (S09)
    on_xlsx = resolve_dataset_path("DS001_ONEILL")
    oneill_summary = {}
    for sh, gcol, scol in [("TableS1C", "Group", "PatientSubtype"), ("TableS1B", "Group", "ALS Subtype"),
                           ("TableS1H", "Group", "PatientSubtype"), ("TableS1G", "Group", "ALS Subtype")]:
        df_o = read_xlsx_sparse_safe(on_xlsx, sh, 2)
        cg_o, cs_o = resolve_col(df_o, gcol), resolve_col(df_o, scol)
        als_o = df_o[df_o[cg_o].astype(str).str.contains("ALS", na=False)].copy()
        vc = als_o[cs_o].value_counts().to_dict()
        tot_n = int(sum(vc.values()))
        te_n = int(vc.get("ALS-TE", 0))
        oneill_summary[sh] = {"total_als": tot_n, "counts": {str(k): int(v) for k, v in vc.items()},
                              "als_te_pct": round(te_n / tot_n * 100.0, 2) if tot_n else 0.0}

    out = {"nygc_bulk_models": nygc_results, "spillman_proteomics": spillman_res,
           "trautwig_csf_proteomics": tr_res, "zeng_apa_hits": apa_hits,
           "brycesmith_cryptic_hits": ce_hits, "oneill_2025_subtypes": oneill_summary}
    (OUT_DIR / "part_a_b_nygc_proteomics_oneill.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"Saved NYGC ({len(nygc_results)}), Spillman ({len(spillman_res)}), Trautwig ({len(tr_res)}), O'Neill ({len(oneill_summary)}).")


if __name__ == "__main__":
    main()
