"""RUN-B3-002: Postmortem CNS Bulk & Subtype Re-Computation (Prudencio DS014 + NYGC DS001/O'Neill/GC)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from scripts.phase1_batches.batch_runner_utils import read_xlsx_sparse_safe, resolve_col, resolve_dataset_path

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_3" / "outputs"
TARGETS = ["IL1RL1", "IL33", "CHIT1", "GPNMB", "CHI3L1", "CHI3L2", "C1QA", "C1QB", "C1QC", "C3", "C4B"]
MARKERS = {"endo": ["PECAM1", "CLDN5", "VWF"], "micro": ["TYROBP", "CSF1R", "AIF1"],
           "astro": ["AQP4", "ALDH1L1", "GFAP"], "neuro": ["SNAP25", "RBFOX3", "SYT1"]}


def run_prudencio() -> dict:
    p = resolve_dataset_path("DS014_PRUD")
    meta = pd.read_csv(p / "metadata.csv")
    nc = pd.read_csv(p / "normalized_counts.csv.gz").set_index("count_column")
    rf = pd.read_csv(p / "raw_full_gene_results.csv").set_index("gene")
    l2 = np.log2(nc + 1.0)
    l2["endo_idx"] = l2[[g for g in MARKERS["endo"] if g in l2.columns]].mean(axis=1)

    fcx = meta[meta["tissue"] == "Frontal Cortex"].set_index("donor_alias")
    cer = meta[meta["tissue"] == "Cerebellum"].set_index("donor_alias")
    common = sorted(set(fcx.index) & set(cer.index))
    res = []
    for g in TARGETS:
        rec: dict = {"gene": g, "present_in_d014": g in l2.columns}
        if g in rf.index:
            r = rf.loc[g]
            rec.update({"deseq2_inter_log2fc": float(r["log2FoldChange"]), "deseq2_inter_p": float(r["pvalue"]),
                        "deseq2_inter_padj": float(r["padj"]) if pd.notna(r["padj"]) else None})
        if g in l2.columns:
            df = pd.DataFrame({
                "is_sals": (fcx.loc[common, "genotype"] == "sALS").astype(int),
                "age": pd.to_numeric(fcx.loc[common, "age_years"], errors="coerce"),
                "sex": fcx.loc[common, "sex"].astype(str),
                "pmi": pd.to_numeric(fcx.loc[common, "pmi_hours"], errors="coerce"),
                "fcx": l2.loc[fcx.loc[common, "count_column"], g].values,
                "cer": l2.loc[cer.loc[common, "count_column"], g].values,
                "fcx_endo": l2.loc[fcx.loc[common, "count_column"], "endo_idx"].values,
            })
            df["delta"] = df["fcx"] - df["cer"]
            f_int = smf.ols("delta ~ is_sals + age + C(sex) + pmi", data=df).fit()
            f_fcx = smf.ols("fcx ~ is_sals + age + C(sex) + pmi", data=df).fit()
            f_endo = smf.ols("fcx ~ is_sals + age + C(sex) + pmi + fcx_endo", data=df).fit()
            t_w, p_w = stats.ttest_ind(df.loc[df["is_sals"] == 1, "delta"], df.loc[df["is_sals"] == 0, "delta"], equal_var=False)
            rec.update({"n_donors_sals": int(df["is_sals"].sum()), "n_donors_ctrl": int((df["is_sals"] == 0).sum()),
                        "paired_delta_welch_t": float(t_w), "paired_delta_welch_p": float(p_w),
                        "paired_delta_ols_beta": float(f_int.params["is_sals"]), "paired_delta_ols_p": float(f_int.pvalues["is_sals"]),
                        "fcx_only_ols_beta": float(f_fcx.params["is_sals"]), "fcx_only_ols_p": float(f_fcx.pvalues["is_sals"]),
                        "fcx_endo_adj_beta": float(f_endo.params["is_sals"]), "fcx_endo_adj_p": float(f_endo.pvalues["is_sals"])})
        res.append(rec)
    return {"n_paired_donors": len(common), "results": res}


def run_nygc() -> tuple[dict, list[dict]]:
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    gc_sym = gc_df.groupby(resolve_col(gc_df, "Gene name"))[resolve_col(gc_df, "Gene % GC content")].median().to_dict()
    gc_ens = gc_df.set_index(resolve_col(gc_df, "Gene stable ID"))[resolve_col(gc_df, "Gene % GC content")].to_dict()

    fmap = pd.read_csv(resolve_dataset_path("DS001_FEAT", verify_hash=True))
    want_syms = set(TARGETS) | {m for v in MARKERS.values() for m in v}
    sym2ens = fmap[fmap["ucsd_label"].isin(want_syms) & fmap["nygc_exact_versioned_ids"].notna()].set_index("ucsd_label")["nygc_exact_versioned_ids"].to_dict()

    # Stream NYGC counts: compute library sizes, GC high-vs-low index, and extract target+marker rows
    cpath = resolve_dataset_path("DS001_COUNTS", verify_hash=True)
    hdr = pd.read_csv(cpath, sep="\t", nrows=0)
    scols = list(hdr.columns[1:])
    lib_sum = np.zeros(len(scols), dtype=np.float64)
    hi_sum = np.zeros(len(scols), dtype=np.float64)
    lo_sum = np.zeros(len(scols), dtype=np.float64)
    n_hi, n_lo = 0, 0
    keep_rows = {}
    want_ens = set(sym2ens.values())

    for chunk in pd.read_csv(cpath, sep="\t", chunksize=4000):
        eids = chunk["EnsemblID"].astype(str)
        mat = chunk[scols].to_numpy(dtype=np.float64)
        lib_sum += mat.sum(axis=0)
        base_ens = eids.str.split(".").str[0]
        gcs = base_ens.map(gc_ens)
        expr_ok = (mat.mean(axis=1) >= 20.0)
        m_hi = (expr_ok & (gcs >= 58.0)).to_numpy()
        m_lo = (expr_ok & (gcs <= 40.0)).to_numpy()
        if m_hi.any():
            hi_sum += np.log2(mat[m_hi] + 1.0).sum(axis=0)
            n_hi += int(m_hi.sum())
        if m_lo.any():
            lo_sum += np.log2(mat[m_lo] + 1.0).sum(axis=0)
            n_lo += int(m_lo.sum())
        hit = eids.isin(want_ens)
        for idx in np.flatnonzero(hit.to_numpy()):
            keep_rows[eids.iloc[idx]] = mat[idx]

    lcpm = {sym: np.log2(keep_rows[ens] / (lib_sum / 1e6) + 1.0) for sym, ens in sym2ens.items() if ens in keep_rows}
    sdf = pd.DataFrame(lcpm, index=scols)
    sdf["gc_index"] = (hi_sum / max(n_hi, 1)) - (lo_sum / max(n_lo, 1))
    for k, ms in MARKERS.items():
        sdf[f"{k}_idx"] = sdf[[m for m in ms if m in sdf.columns]].mean(axis=1)

    meta = read_xlsx_sparse_safe(resolve_dataset_path("DS001_META", verify_hash=True), "GSE153960 Metadata", 1)
    meta = meta[meta["ExternalSampleId"].isin(sdf.index)].copy()
    meta["RIN_num"] = pd.to_numeric(meta["RIN"], errors="coerce")
    meta["Age_num"] = pd.to_numeric(meta["Age at Death"], errors="coerce")
    meta["reg_clean"] = meta["Sample Source"].replace({"Cortex_Motor_Medial": "Cortex_Motor", "Cortex_Motor_Lateral": "Cortex_Motor", "Cortex_Motor_Unspecified": "Cortex_Motor"})
    meta = meta.join(sdf, on="ExternalSampleId")

    # Regional donor-level OLS (ALS-TDP vs Control)
    rows = []
    for reg in ["Cortex_Frontal", "Cortex_Motor", "Spinal_Cord_Cervical", "Spinal_Cord_Lumbar"]:
        sub = meta[(meta["reg_clean"] == reg) & meta["disease_group"].isin(["ALS-TDP", "Control"])].copy()
        sub["is_als"] = (sub["disease_group"] == "ALS-TDP").astype(int)
        num_cols = [g for g in TARGETS if g in sub.columns] + ["RIN_num", "Age_num", "gc_index", "endo_idx", "micro_idx", "astro_idx", "neuro_idx", "is_als"]
        don = sub.groupby("ExternalSubjectId")[num_cols].mean()
        cat = sub.groupby("ExternalSubjectId")[["Sex", "Prep", "Platform"]].first()
        don = don.join(cat).dropna(subset=["RIN_num", "Age_num"])
        for g in TARGETS:
            if g not in don.columns:
                continue
            m1 = smf.ols(f"{g} ~ is_als + RIN_num + Age_num + C(Sex) + C(Prep)", data=don).fit()
            m2 = smf.ols(f"{g} ~ is_als + RIN_num + Age_num + C(Sex) + C(Prep) + C(Platform) + gc_index", data=don).fit()
            m3 = smf.ols(f"{g} ~ is_als + RIN_num + Age_num + C(Sex) + C(Prep) + gc_index + endo_idx + micro_idx + astro_idx + neuro_idx", data=don).fit()
            rows.append({"analysis": "NYGC_Regional_ALS_TDP_vs_Ctrl", "stratum": reg, "gene": g, "gene_gc_pct": gc_sym.get(g),
                         "n_als_donors": int((don["is_als"] == 1).sum()), "n_ctrl_donors": int((don["is_als"] == 0).sum()),
                         "m1_tech_beta": float(m1.params["is_als"]), "m1_tech_p": float(m1.pvalues["is_als"]),
                         "m2_gcbank_beta": float(m2.params["is_als"]), "m2_gcbank_p": float(m2.pvalues["is_als"]),
                         "m3_cellcomp_beta": float(m3.params["is_als"]), "m3_cellcomp_p": float(m3.pvalues["is_als"])})

    # O'Neill 2025 ALS-Glia subtype enrichment (Cortex TableS1B & Spinal Cord TableS1G)
    p_on = resolve_dataset_path("DS001_ONEILL", verify_hash=True)
    s1b = read_xlsx_sparse_safe(p_on, "TableS1B", 2)
    s1g = read_xlsx_sparse_safe(p_on, "TableS1G", 2)
    tam_wb = read_xlsx_sparse_safe(resolve_dataset_path("DS001_TAM", verify_hash=True), "Sheet1", 2)

    for label, st_df, glia_tag in [("ONeill_Cortex", s1b, "ALS-Glia"), ("ONeill_SpinalCord", s1g, "ALS-Glia-cord")]:
        m_st = st_df[st_df["Sample"].isin(sdf.index)].join(sdf, on="Sample")
        m_st["RIN_num"] = pd.to_numeric(m_st["RIN"], errors="coerce")
        als_only = m_st[m_st["Group"].isin(["ALS", "ALS+FTD"]) & m_st["ALS Subtype"].ne("Not applicable")]
        als_don_sub = als_only.groupby("Patient ID")["ALS Subtype"].agg(lambda x: x.mode().iloc[0])
        glia_frac = float((als_don_sub == glia_tag).mean())
        # Donor-level: ALS-Glia vs CTL & ALS-Glia vs other ALS subtypes
        ctl_don = m_st[m_st["Group"].isin(["CTL", "Control"])].groupby("Patient ID")[[g for g in TARGETS if g in m_st.columns] + ["RIN_num", "gc_index", "endo_idx", "micro_idx"]].mean()
        ctl_don["grp"] = "CTL"
        als_num = als_only.groupby("Patient ID")[[g for g in TARGETS if g in m_st.columns] + ["RIN_num", "gc_index", "endo_idx", "micro_idx"]].mean()
        als_num["grp"] = als_don_sub
        comb = pd.concat([ctl_don, als_num.loc[als_num.index.difference(ctl_don.index)]]).dropna(subset=["RIN_num"])
        for g in TARGETS:
            if g not in comb.columns:
                continue
            d_gc = comb[comb["grp"].isin([glia_tag, "CTL"])].copy()
            d_gc["is_glia"] = (d_gc["grp"] == glia_tag).astype(int)
            fgc = smf.ols(f"{g} ~ is_glia + RIN_num + gc_index", data=d_gc).fit()
            fgc_e = smf.ols(f"{g} ~ is_glia + RIN_num + gc_index + endo_idx + micro_idx", data=d_gc).fit()
            d_go = comb[comb["grp"] != "CTL"].copy()
            d_go["is_glia"] = (d_go["grp"] == glia_tag).astype(int)
            fgo = smf.ols(f"{g} ~ is_glia + RIN_num + gc_index", data=d_go).fit()
            rows.append({"analysis": label, "stratum": f"{glia_tag} (prev={glia_frac:.3f})", "gene": g, "gene_gc_pct": gc_sym.get(g),
                         "n_als_donors": int((d_go["is_glia"] == 1).sum()), "n_ctrl_donors": int((d_gc["is_glia"] == 0).sum()),
                         "m1_tech_beta": float(fgc.params["is_glia"]), "m1_tech_p": float(fgc.pvalues["is_glia"]),
                         "m2_gcbank_beta": float(fgo.params["is_glia"]), "m2_gcbank_p": float(fgo.pvalues["is_glia"]),
                         "m3_cellcomp_beta": float(fgc_e.params["is_glia"]), "m3_cellcomp_p": float(fgc_e.pvalues["is_glia"])})

    meta_summary = {"n_hi_gc_genes": n_hi, "n_lo_gc_genes": n_lo, "tam2019_mmc2_rows": len(tam_wb),
                    "oneill_s1b_tam_cohort_samples": int((s1b["Cohort"] == "Tam et al. 2019").sum())}
    return meta_summary, rows


def main() -> None:
    prud = run_prudencio()
    nygc_meta, nygc_rows = run_nygc()
    out = {"prudencio_d014": prud, "nygc_and_oneill_meta": nygc_meta, "nygc_and_oneill_models": nygc_rows}
    (OUT_DIR / "run_b3_002_cns_bulk_subtypes.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    pd.DataFrame(nygc_rows).to_csv(OUT_DIR / "run_b3_002_nygc_models.csv", index=False)
    pd.DataFrame(prud["results"]).to_csv(OUT_DIR / "run_b3_002_prudencio_models.csv", index=False)
    print(f"RUN-B3-002 complete: D014={len(prud['results'])} genes, NYGC/ONeill={len(nygc_rows)} model rows.")


if __name__ == "__main__":
    main()
