"""RUN-B3-003: Donor-Level snRNA-seq Pseudobulk (Edinburgh GSE290359) & Spatial Spinal Cord (Zhang 2026)."""
from __future__ import annotations

import json
import re
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
TARGETS = ["IL1RL1", "IL33", "CHIT1", "GPNMB", "CHI3L1", "CHI3L2", "C1QA", "C1QB", "C1QC", "C3", "C4A", "C4B"]


def unwrap(v: object) -> str:
    if isinstance(v, str) and v.startswith("[["):
        return str(json.loads(v)[0][0]).strip()
    return str(v).strip()


def run_edinburgh() -> dict:
    ep = resolve_dataset_path("DS_EDIN_PB")
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    sym2ens = gc_df.groupby(resolve_col(gc_df, "Gene name"))[resolve_col(gc_df, "Gene stable ID")].first().to_dict()
    ens2gc = gc_df.set_index(resolve_col(gc_df, "Gene stable ID"))[resolve_col(gc_df, "Gene % GC content")].to_dict()

    genes = pd.read_csv(ep / "genes.tsv", sep="\t")
    gidx2ens = genes.set_index("gene_index")["name"].to_dict()
    ens2gidx = genes.set_index("name")["gene_index"].to_dict()
    t_gidx = {g: ens2gidx[sym2ens[g]] for g in TARGETS if g in sym2ens and sym2ens[g] in ens2gidx}

    cts = pd.read_csv(ep / "celltypes.tsv", sep="\t").set_index("cell_type_index")["label"].to_dict()
    lm = pd.read_csv(ep / "library_metadata.tsv", sep="\t")
    for c in ["Sample ID", "Edinburgh ID", "Tissue", "Sex", "Age", "Classifcation", "Disease?", "Mutation"]:
        lm[c] = lm[c].apply(unwrap)
    lm["Age_num"] = pd.to_numeric(lm["Age"], errors="coerce")
    c9_donors = set(lm.loc[lm["Mutation"].str.contains("C9orf72", case=False, na=False), "Edinburgh ID"])
    lm["is_c9_donor"] = lm["Edinburgh ID"].isin(c9_donors)

    nqc = pd.read_csv(ep / "nuclei_qc.tsv", sep="\t")
    umi_map = nqc.set_index(["library", "label"])["total_umi"].to_dict()
    nuc_map = nqc.set_index(["library", "label"])["n_nuclei"].to_dict()

    # Load pseudobulk per library x celltype: compute log2CPM for targets + GC bias index
    lib_rows = []
    for _, lrow in lm.iterrows():
        lib = lrow["library"]
        pbf = ep / "pseudobulk" / f"{lib}.pseudobulk.tsv.gz"
        if not pbf.exists():
            continue
        pb = pd.read_csv(pbf, sep="\t")
        pb["ens"] = pb["gene_index"].map(gidx2ens)
        pb["gc"] = pb["ens"].map(ens2gc)
        for ct_idx, ct_name in cts.items():
            if ct_name in {"Doublet", "Low-Quality"}:
                continue
            tot_umi = float(umi_map.get((lib, ct_name), 0.0))
            n_nuc = int(nuc_map.get((lib, ct_name), 0))
            if tot_umi <= 0 or n_nuc < 5:
                continue
            sub = pb[pb["cell_type_index"] == ct_idx]
            s_map = sub.set_index("gene_index")["sum"].to_dict()
            hi_gc = np.log2(sub.loc[sub["gc"] >= 58.0, "sum"] / (tot_umi / 1e6) + 1.0).mean()
            lo_gc = np.log2(sub.loc[sub["gc"] <= 40.0, "sum"] / (tot_umi / 1e6) + 1.0).mean()
            rec = {"library": lib, "donor_id": lrow["Edinburgh ID"], "tissue": lrow["Tissue"],
                   "cell_type": ct_name, "is_als": int(lrow["Disease?"] == "Yes"),
                   "is_c9": int(lrow["is_c9_donor"]), "sex": lrow["Sex"], "age": lrow["Age_num"],
                   "n_nuclei": n_nuc, "total_umi": tot_umi, "gc_idx": float(hi_gc - lo_gc)}
            for g, gi in t_gidx.items():
                rec[g] = float(np.log2(s_map.get(gi, 0.0) / (tot_umi / 1e6) + 1.0))
            lib_rows.append(rec)

    ldf = pd.DataFrame(lib_rows)
    # Cell-type specificity atlas (donor-averaged across all donors)
    don_ct = ldf.groupby(["donor_id", "cell_type"])[[g for g in t_gidx] + ["is_als", "is_c9", "age", "gc_idx", "n_nuclei"]].mean().reset_index()
    don_sex = ldf.groupby("donor_id")["sex"].first().to_dict()
    don_ct["sex"] = don_ct["donor_id"].map(don_sex)

    ct_means = don_ct.groupby("cell_type")[[g for g in t_gidx]].mean().round(4).to_dict(orient="index")
    de_rows = []
    for ct_name in ["Microglia", "Astrocyte", "Endothelial", "Excitatory neuron", "Oligodendrocyte", "Oligodendrocyte Producing Cell"]:
        dsub = don_ct[don_ct["cell_type"] == ct_name].dropna(subset=["age"]).copy()
        if len(dsub) < 10:
            continue
        for g in t_gidx:
            if dsub[g].std() < 1e-8:
                continue
            m_all = smf.ols(f"{g} ~ is_als + age + C(sex) + gc_idx", data=dsub).fit()
            d_sals = dsub[dsub["is_c9"] == 0]
            m_sals = smf.ols(f"{g} ~ is_als + age + C(sex) + gc_idx", data=d_sals).fit()
            t_w, p_w = stats.ttest_ind(dsub.loc[dsub["is_als"] == 1, g], dsub.loc[dsub["is_als"] == 0, g], equal_var=False)
            de_rows.append({"cell_type": ct_name, "gene": g,
                            "n_als_donors": int((dsub["is_als"] == 1).sum()),
                            "n_sals_nonc9_donors": int(((d_sals["is_als"] == 1)).sum()),
                            "n_ctrl_donors": int((dsub["is_als"] == 0).sum()),
                            "mean_als_log2cpm": float(dsub.loc[dsub["is_als"] == 1, g].mean()),
                            "mean_ctrl_log2cpm": float(dsub.loc[dsub["is_als"] == 0, g].mean()),
                            "welch_p_all": float(p_w),
                            "ols_gc_als_vs_ctrl_beta": float(m_all.params["is_als"]),
                            "ols_gc_als_vs_ctrl_p": float(m_all.pvalues["is_als"]),
                            "ols_gc_sals_nonc9_beta": float(m_sals.params["is_als"]),
                            "ols_gc_sals_nonc9_p": float(m_sals.pvalues["is_als"])})
    return {"n_libraries": int(len(lm)), "n_unique_donors": int(lm["Edinburgh ID"].nunique()),
            "c9_donors_flagged": sorted(c9_donors), "celltype_mean_log2cpm": ct_means, "donor_de_models": de_rows}


def run_zhang_spatial() -> dict:
    zp = resolve_dataset_path("DS031_ZHANG", verify_hash=True)
    out_sheets = {}
    for s in ["6d_MN_ALS_vs._HC", "6i_TDP43_ALS_vs._HC"]:
        df = read_xlsx_sparse_safe(zp, s, 1)
        gcol = resolve_col(df, "gene")
        pcol = resolve_col(df, "p_val")
        bhcol = resolve_col(df, "BH")
        fccol = resolve_col(df, "avg_log2FC")
        decol = resolve_col(df, "DE")
        sub = df[df[gcol].isin(TARGETS)].copy()
        out_sheets[s] = [
            {"gene": str(r[gcol]), "avg_log2FC": float(r[fccol]), "p_val": float(r[pcol]),
             "bh_fdr": float(r[bhcol]), "de_call": str(r[decol])}
            for _, r in sub.iterrows()
        ]
        present = {x["gene"] for x in out_sheets[s]}
        for g in TARGETS:
            if g not in present:
                out_sheets[s].append({"gene": g, "avg_log2FC": None, "p_val": None, "bh_fdr": None, "de_call": "NOT_IN_TABLE"})

    # Extract exact cervical duration linear regressions reported in Zhang 2026 full text
    ztxt = (resolve_dataset_path("DS_CONS2026") / "PMC13337491_Zhang_2026_Spatial.txt").read_text(encoding="utf-8", errors="replace")
    dur_matches = re.findall(r"(CHIT1|APOC1|C1QA|C1QB|C1QC|LSP1)\s*\(P\s*=\s*([^,]+),\s*r\s*=\s*([^,]+),\s*FDR\s*=\s*([^)]+)\)", ztxt)
    return {"sheets": out_sheets, "cervical_duration_regressions_fulltext": [
        {"gene": g, "p_str": p.strip(), "r_str": r.strip(), "fdr_str": f.strip()} for g, p, r, f in dur_matches
    ]}


def main() -> None:
    edin = run_edinburgh()
    zhang = run_zhang_spatial()
    out = {"edinburgh_gse290359": edin, "zhang2026_spatial_d031": zhang}
    (OUT_DIR / "run_b3_003_singlecell_spatial.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    pd.DataFrame(edin["donor_de_models"]).to_csv(OUT_DIR / "run_b3_003_edinburgh_de.csv", index=False)
    z_flat = [{"sheet": k, **r} for k, v in zhang["sheets"].items() for r in v]
    pd.DataFrame(z_flat).to_csv(OUT_DIR / "run_b3_003_zhang_spatial.csv", index=False)
    print(f"RUN-B3-003 complete: Edin DE={len(edin['donor_de_models'])}, Zhang rows={len(z_flat)}")


if __name__ == "__main__":
    main()
