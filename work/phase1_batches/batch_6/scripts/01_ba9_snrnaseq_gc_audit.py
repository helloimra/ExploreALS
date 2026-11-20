"""RUN-B6-001: Historical BA9 10-gene + SARM1 snRNA-seq & GC confounding audit.

Recomputes Ensembl v116 gene GC%, D003 (Pineda 2024) BA9 vs BA4/M1 donor-level
pseudobulk OLS models (unadjusted vs donor GC-index adjusted), Pineda mmc2
published DE, and Edinburgh GSE290359 donor-aggregated BA44/BA46 replication.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.phase1_batches.batch_runner_utils import resolve_col, resolve_dataset_path

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_6" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_GENES = [
    "AGAP2", "AP1G2", "BRSK2", "DNAJB2", "KIFC2",
    "MIB2", "MYO18A", "SNPH", "ZNF783", "CAPG", "SARM1",
]
D003_CTI_MAP = {
    0: "5HT3aR", 1: "Astro", 2: "Endo", 3: "Fibro", 4: "L2_L3", 5: "L3_L5",
    6: "L4_L5", 7: "L4_L6", 8: "L5", 9: "L5_L6", 10: "L6", 12: "Micro",
    13: "Mural", 14: "OPC", 15: "Oligo", 16: "PV", 17: "Rosehip", 18: "SOM", 19: "T_Cell",
}


def fit_ols_contrast(y: np.ndarray, group: np.ndarray, covars: np.ndarray | None = None) -> dict:
    mask = np.isfinite(y) & np.isfinite(group)
    if covars is not None:
        mask &= np.all(np.isfinite(covars), axis=1)
    y_m, g_m = y[mask], group[mask]
    n_case, n_ctrl = int(np.sum(g_m == 1)), int(np.sum(g_m == 0))
    if n_case < 3 or n_ctrl < 3:
        return {"n_case": n_case, "n_ctrl": n_ctrl, "beta_log2fc": np.nan, "se": np.nan, "t": np.nan, "p_two": np.nan}
    X = np.column_stack([np.ones(len(g_m)), g_m] + ([covars[mask]] if covars is not None else []))
    res = sm.OLS(y_m, X).fit()
    return {
        "n_case": n_case, "n_ctrl": n_ctrl,
        "beta_log2fc": float(res.params[1]), "se": float(res.bse[1]),
        "t": float(res.tvalues[1]), "p_two": float(res.pvalues[1]),
    }


def main() -> None:
    # 1. Ensembl v116 GC content reference
    gc_path = resolve_dataset_path("DS_GC_REF")
    gc_df = pd.read_csv(gc_path, sep="\t")
    col_ens = resolve_col(gc_df, "Gene stable ID")
    col_sym = resolve_col(gc_df, "Gene name")
    col_type = resolve_col(gc_df, "Gene type")
    col_gc = resolve_col(gc_df, "Gene % GC content")
    col_chr = resolve_col(gc_df, "Chromosome/scaffold name")
    canon_chrs = {str(i) for i in range(1, 23)} | {"X", "Y", "MT"}
    pc_gc = gc_df[(gc_df[col_type] == "protein_coding") & (gc_df[col_chr].astype(str).isin(canon_chrs))].copy()
    pc_gc_vals = np.sort(pc_gc[col_gc].dropna().to_numpy())
    ens_to_gc = pc_gc.set_index(col_ens)[col_gc].to_dict()

    gc_summary = {}
    for g in TARGET_GENES:
        sub = pc_gc[pc_gc[col_sym] == g]
        if sub.empty:
            sub = gc_df[gc_df[col_sym] == g]
        val = float(sub.iloc[0][col_gc])
        pct = float(np.searchsorted(pc_gc_vals, val, side="right") / len(pc_gc_vals) * 100.0)
        gc_summary[g] = {"ensembl_id": str(sub.iloc[0][col_ens]), "gc_pct": val, "pc_gc_percentile": round(pct, 2)}

    # 2. Historical BA9 14 test pairs (embedded so RUN-B6-001 needs zero unmanifested legacy directory)
    historical_ba9_14_pairs = [
        ("L2_L3", "BRSK2"), ("Oligo", "MYO18A"), ("L5", "KIFC2"), ("L3_L5", "BRSK2"),
        ("Oligo", "DNAJB2"), ("L4_L6", "KIFC2"), ("L4_L5", "KIFC2"), ("L4_L5", "BRSK2"),
        ("L2_L3", "AP1G2"), ("L2_L3", "ZNF783"), ("L3_L5", "KIFC2"), ("L2_L3", "AGAP2"),
        ("L2_L3", "SNPH"), ("L2_L3", "MIB2"),
    ]
    opt_b5_tsv = ROOT / "data" / "transcriptomics" / "ba9_bundle_v5" / "work" / "dl23e_values" / "coordinator" / "values.tsv"
    if opt_b5_tsv.is_file():
        b5_vals = pd.read_csv(opt_b5_tsv, sep="\t")
        ct_col, gene_col = resolve_col(b5_vals, "cell_type"), resolve_col(b5_vals, "gene")
        assert list(b5_vals[[ct_col, gene_col]].itertuples(index=False, name=None)) == historical_ba9_14_pairs
    test_pairs = list(historical_ba9_14_pairs)
    test_pairs.extend([("Micro", "CAPG"), ("L2_L3", "CAPG"), ("L2_L3", "SARM1"), ("L3_L5", "SARM1"), ("Oligo", "SARM1")])

    # 3. D003 BA9 and BA4 (M1) donor-level pseudobulk + donor GC-bias index
    d3_dir = resolve_dataset_path("DS003_PB")
    rr = pd.read_csv(d3_dir / "reduce_report.csv")
    rm = pd.read_csv(d3_dir / "row_metadata.tsv", sep="\t")
    rm["gene_index"] = np.arange(1, len(rm) + 1)
    rm["gc"] = rm[resolve_col(rm, "ENSEMBL")].map(ens_to_gc)
    sym_to_gidx = rm[rm["Gene"].isin(TARGET_GENES)].set_index("Gene")["gene_index"].to_dict()
    gc_vec = rm.set_index("gene_index")["gc"].to_dict()

    d3_records = []
    for row in rr.itertuples(index=False):
        pb = pd.read_csv(d3_dir / f"{row.folder}.pseudobulk.tsv.gz", sep="\t")
        pb["ct"] = pb[resolve_col(pb, "cell_type_index")].map(D003_CTI_MAP)
        pb["gc"] = pb[resolve_col(pb, "gene_index")].map(gc_vec)
        tot = pb.groupby("ct")["sum"].sum()
        gc_valid = pb.dropna(subset=["gc"]).copy()
        gc_valid["lib"] = gc_valid["ct"].map(tot)
        gc_valid = gc_valid[gc_valid["lib"] >= 10000]
        gc_valid["l2cpm"] = np.log2(gc_valid["sum"] / gc_valid["lib"] * 1e6 + 1.0)
        hi_gc = gc_valid[gc_valid["gc"] >= 60.0].groupby("ct")["l2cpm"].mean()
        lo_gc = gc_valid[gc_valid["gc"] <= 42.0].groupby("ct")["l2cpm"].mean()
        w_gc = hi_gc - lo_gc
        sub_t = pb[pb["gene_index"].isin(sym_to_gidx.values())].pivot(index="ct", columns="gene_index", values="sum")
        for ct, lib in tot.items():
            if lib < 10000 or pd.isna(ct):
                continue
            rec = {"region": row.region, "donor": str(row.donor), "is_sals": 1.0 if row.group == "SALS" else 0.0,
                   "ct": ct, "lib_size": float(lib), "donor_gc_idx": float(w_gc.get(ct, np.nan))}
            for g, gidx in sym_to_gidx.items():
                cnt = float(sub_t.loc[ct, gidx]) if (ct in sub_t.index and gidx in sub_t.columns and pd.notna(sub_t.loc[ct, gidx])) else 0.0
                rec[f"log2cpm_{g}"] = float(np.log2(cnt / lib * 1e6 + 1.0))
            d3_records.append(rec)
    d3_df = pd.DataFrame(d3_records).groupby(["region", "donor", "is_sals", "ct"], as_index=False).mean()

    d3_results = []
    for ct, g in test_pairs:
        for reg in ["BA9", "BA4"]:
            sub = d3_df[(d3_df["region"] == reg) & (d3_df["ct"] == ct)]
            unadj = fit_ols_contrast(sub[f"log2cpm_{g}"].to_numpy(), sub["is_sals"].to_numpy())
            gc_adj = fit_ols_contrast(sub[f"log2cpm_{g}"].to_numpy(), sub["is_sals"].to_numpy(), sub[["donor_gc_idx"]].to_numpy())
            r_gc = float(np.corrcoef(sub[f"log2cpm_{g}"], sub["donor_gc_idx"])[0, 1]) if len(sub) > 3 else np.nan
            d3_results.append({"dataset": f"D003_{reg}", "cell_type": ct, "gene": g, "gc_pct": gc_summary[g]["gc_pct"],
                               "corr_with_donor_gc": round(r_gc, 4),
                               **{f"unadj_{k}": v for k, v in unadj.items()}, **{f"gc_adj_{k}": v for k, v in gc_adj.items()}})

    # 4. Edinburgh GSE290359 independent BA44/BA46 donor-level snRNA-seq replication
    ed_dir = resolve_dataset_path("DS_EDIN_PB")
    em = pd.read_csv(ed_dir / "library_metadata.tsv", sep="\t")
    eg = pd.read_csv(ed_dir / "genes.tsv", sep="\t")
    ecf = pd.read_csv(ed_dir / "celltypes_fine.tsv", sep="\t").set_index("cell_type_index")["label"].to_dict()
    eg["gc"] = eg["name"].map(ens_to_gc)
    ed_gidx = {g: int(eg.loc[eg["name"] == gc_summary[g]["ensembl_id"], "gene_index"].iloc[0])
               for g in TARGET_GENES if (eg["name"] == gc_summary[g]["ensembl_id"]).any()}
    ed_gc_map = eg.set_index("gene_index")["gc"].to_dict()

    col_lib = resolve_col(em, "library")
    col_edin_id = resolve_col(em, "Edinburgh ID")
    col_cls = resolve_col(em, "Classifcation")
    col_mut = resolve_col(em, "Mutation")
    ed_rows = []
    for r in em.to_dict(orient="records"):
        mut = json.loads(str(r[col_mut]))[0][0].strip()
        if "C9orf72" in mut:
            continue
        donor_id = json.loads(str(r[col_edin_id]))[0][0]
        cls = json.loads(str(r[col_cls]))[0][0]
        is_als = 0.0 if cls == "Control" else 1.0
        pb = pd.read_csv(ed_dir / "pseudobulk_fine" / f"{r[col_lib]}.pseudobulk.tsv.gz", sep="\t")
        pb["ct"] = pb["cell_type_index"].map(ecf)
        pb["gc"] = pb["gene_index"].map(ed_gc_map)
        for ct, grp in pb.groupby("ct"):
            lib = float(grp["sum"].sum())
            if lib < 5000 or ct in {"DBLT", "LQ"}:
                continue
            gv = grp.dropna(subset=["gc"])
            wgc = float((gv["sum"] * gv["gc"]).sum() / gv["sum"].sum())
            rec = {"donor": donor_id, "is_sals": is_als, "ct": ct, "lib_size": lib, "donor_gc_idx": wgc}
            cnt_map = grp.set_index("gene_index")["sum"].to_dict()
            for g, gi in ed_gidx.items():
                rec[f"cnt_{g}"] = float(cnt_map.get(gi, 0.0))
            ed_rows.append(rec)
    ed_agg = pd.DataFrame(ed_rows).groupby(["donor", "is_sals", "ct"], as_index=False).agg(
        {"lib_size": "sum", "donor_gc_idx": "mean", **{f"cnt_{g}": "sum" for g in ed_gidx}}
    )
    for g in ed_gidx:
        ed_agg[f"log2cpm_{g}"] = np.log2(ed_agg[f"cnt_{g}"] / ed_agg["lib_size"] * 1e6 + 1.0)

    ed_ct_map = {"L2_L3": "EN_L2_L3", "L3_L5": "EN_L3_L5", "L4_L5": "EN_L3_L5", "L4_L6": "EN_L5_L6", "L5": "EN_L5_L6", "Oligo": "OD", "Micro": "MIG"}
    ed_results = []
    for ct_orig, g in dict.fromkeys([(ed_ct_map[c], g) for c, g in test_pairs if g in ed_gidx]):
        sub = ed_agg[ed_agg["ct"] == ct_orig]
        unadj = fit_ols_contrast(sub[f"log2cpm_{g}"].to_numpy(), sub["is_sals"].to_numpy())
        gc_adj = fit_ols_contrast(sub[f"log2cpm_{g}"].to_numpy(), sub["is_sals"].to_numpy(), sub[["donor_gc_idx"]].to_numpy())
        ed_results.append({"dataset": "Edinburgh_BA44_46", "cell_type": ct_orig, "gene": g,
                           **{f"unadj_{k}": v for k, v in unadj.items()}, **{f"gc_adj_{k}": v for k, v in gc_adj.items()}})

    pd.DataFrame(d3_results).to_csv(OUT_DIR / "part_a_d003_ba9_m1_gc_audit.csv", index=False)
    pd.DataFrame(ed_results).to_csv(OUT_DIR / "part_a_edinburgh_replication.csv", index=False)
    (OUT_DIR / "part_a_gc_and_snrnaseq_summary.json").write_text(
        json.dumps({"gc_reference": gc_summary, "d003_results": d3_results, "edinburgh_results": ed_results}, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(d3_results)} D003 tests and {len(ed_results)} Edinburgh tests.")


if __name__ == "__main__":
    main()
