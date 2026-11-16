"""RUN-B1-003: Donor-level snRNA-seq pseudobulk (Pineda M1/BA9 & Edinburgh BA44/46) + 2026 Consortia."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.phase1_batches.batch_runner_utils import resolve_col, resolve_dataset_path

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_1" / "outputs"
GENES = ["UNC13A", "STMN2", "KCNQ2", "CHMP7", "CHMP2B", "VPS4B"]


def fit_models(df: pd.DataFrame, g: str) -> dict[str, object]:
    sub = df.dropna(subset=[f"log2cpm_{g}", "donor_gc_index"]).copy()
    n_als = int((sub["is_als"] == 1).sum())
    n_ctl = int((sub["is_als"] == 0).sum())
    if n_als < 3 or n_ctl < 3:
        return {"n_als": n_als, "n_ctrl": n_ctl, "status": "insufficient_donors"}
    f_un = sm.OLS(sub[f"log2cpm_{g}"], sm.add_constant(sub[["is_als"]].astype(float))).fit()
    f_gc = sm.OLS(sub[f"log2cpm_{g}"], sm.add_constant(sub[["is_als", "donor_gc_index"]].astype(float))).fit()
    return {
        "n_als": n_als,
        "n_ctrl": n_ctl,
        "unadjusted_log2fc": float(f_un.params["is_als"]),
        "unadjusted_p": float(f_un.pvalues["is_als"]),
        "gc_adj_log2fc": float(f_gc.params["is_als"]),
        "gc_adj_p": float(f_gc.pvalues["is_als"]),
    }


def analyze_d003(ens_to_gc: dict[str, float]) -> dict[str, object]:
    d3 = resolve_dataset_path("DS003_PB")
    rr = pd.read_csv(d3 / "reduce_report.csv")
    rm = pd.read_csv(d3 / "row_metadata.tsv", sep="\t")
    rm["gene_index"] = np.arange(1, len(rm) + 1)
    rm["gc"] = rm[resolve_col(rm, "ENSEMBL")].map(ens_to_gc)
    hi_idx = set(rm.loc[rm["gc"] >= 60.0, "gene_index"])
    lo_idx = set(rm.loc[rm["gc"] <= 40.0, "gene_index"])
    sym_to_gidx = {
        g: set(rm.loc[rm[resolve_col(rm, "Gene")] == g, "gene_index"]) for g in GENES
    }
    lineage_groups = {
        "All_Excitatory": {4, 5, 6, 7, 8, 9, 10},
        "Deep_L5_Excitatory": {8, 9},
        "Inhibitory": {0, 16, 17, 18},
        "Oligo": {15},
        "Astro": {1},
        "Micro": {12},
    }
    rr_sals = rr[rr["group"].isin(["SALS", "PN"])].copy()
    rows = []
    for _, meta_row in rr_sals.iterrows():
        pb_file = d3 / f"{meta_row['folder']}.pseudobulk.tsv.gz"
        if not pb_file.exists():
            continue
        pb = pd.read_csv(pb_file, sep="\t")
        for lin_name, cti_set in lineage_groups.items():
            sub = pb[pb["cell_type_index"].isin(cti_set)]
            tot = float(sub["sum"].sum())
            if tot < 1000:
                continue
            hi = float(sub.loc[sub["gene_index"].isin(hi_idx), "sum"].sum())
            lo = float(sub.loc[sub["gene_index"].isin(lo_idx), "sum"].sum())
            rec = {
                "region": str(meta_row["region"]),
                "donor": str(meta_row["donor"]),
                "is_als": 1 if meta_row["group"] == "SALS" else 0,
                "lineage": lin_name,
                "donor_gc_index": float(np.log2((hi + 1.0) / (lo + 1.0))),
            }
            for g in GENES:
                gsum = float(sub.loc[sub["gene_index"].isin(sym_to_gidx[g]), "sum"].sum())
                rec[f"log2cpm_{g}"] = float(np.log2(gsum / tot * 1e6 + 0.5))
            rows.append(rec)
    all_df = pd.DataFrame(rows)
    out: dict[str, object] = {}
    for reg in ["BA4", "BA9"]:
        out[reg] = {}
        for lin in lineage_groups:
            sub = all_df[(all_df["region"] == reg) & (all_df["lineage"] == lin)].groupby("donor", as_index=False).mean(numeric_only=True)
            sub["is_als"] = (sub["is_als"] >= 0.5).astype(int)
            out[reg][lin] = {g: fit_models(sub, g) for g in GENES}

    supp = pd.read_excel(resolve_dataset_path("DS003_SUPP"), sheet_name="Human_BA4_BA9.GENESYM")
    supp_hits = {}
    for col in supp.columns:
        vals = set(supp[col].dropna().astype(str))
        found = sorted(vals & set(GENES))
        if found:
            supp_hits[str(col)] = found
    out["pineda_mmc2_deg_membership"] = supp_hits
    return out


def analyze_edinburgh(ens_to_gc: dict[str, float], sym_to_ens: dict[str, set[str]]) -> dict[str, object]:
    ed = resolve_dataset_path("DS_EDIN_PB")
    eg = pd.read_csv(ed / "genes.tsv", sep="\t")
    name_col = resolve_col(eg, "name")
    eg["gc"] = eg[name_col].astype(str).map(ens_to_gc)
    hi_idx = set(eg.loc[eg["gc"] >= 60.0, "gene_index"])
    lo_idx = set(eg.loc[eg["gc"] <= 40.0, "gene_index"])
    sym_to_gidx = {g: set(eg.loc[eg[name_col].astype(str).isin(sym_to_ens[g]), "gene_index"]) for g in GENES}
    elm = pd.read_csv(ed / "library_metadata.tsv", sep="\t")
    ct_map = {"Excitatory": {3}, "Inhibitory": {4}, "Oligo": {7}, "Astro": {0}, "Micro": {6}}
    rows = []
    for _, mr in elm.iterrows():
        cls = json.loads(mr["Classifcation"])[0][0]
        tis = json.loads(mr["Tissue"])[0][0]
        mut = json.loads(mr["Mutation"])[0][0] if pd.notna(mr["Mutation"]) and str(mr["Mutation"]).startswith("[") else str(mr["Mutation"])
        if "C9orf72" in mut or "SOD1" in mut:
            continue
        is_als = 0 if cls == "Control" else (1 if "ALS" in cls else -1)
        if is_als < 0:
            continue
        pbf = ed / "pseudobulk" / f"{mr['library']}.pseudobulk.tsv.gz"
        if not pbf.exists():
            continue
        pb = pd.read_csv(pbf, sep="\t")
        donor_id = str(json.loads(mr["Edinburgh ID"])[0][0]) if str(mr["Edinburgh ID"]).startswith("[") else str(mr["Edinburgh ID"])
        for cname, cset in ct_map.items():
            sub = pb[pb["cell_type_index"].isin(cset)]
            tot = float(sub["sum"].sum())
            if tot < 1000:
                continue
            hi = float(sub.loc[sub["gene_index"].isin(hi_idx), "sum"].sum())
            lo = float(sub.loc[sub["gene_index"].isin(lo_idx), "sum"].sum())
            rec = {"tissue": tis, "donor": donor_id, "is_als": is_als, "lineage": cname, "donor_gc_index": float(np.log2((hi + 1.0) / (lo + 1.0)))}
            for g in GENES:
                gsum = float(sub.loc[sub["gene_index"].isin(sym_to_gidx[g]), "sum"].sum())
                rec[f"log2cpm_{g}"] = float(np.log2(gsum / tot * 1e6 + 0.5))
            rows.append(rec)
    edf = pd.DataFrame(rows)
    out: dict[str, object] = {}
    for tis in ["BA44", "BA46"]:
        out[tis] = {}
        for cname in ct_map:
            sub = edf[(edf["tissue"] == tis) & (edf["lineage"] == cname)].groupby("donor", as_index=False).mean(numeric_only=True)
            sub["is_als"] = (sub["is_als"] >= 0.5).astype(int)
            out[tis][cname] = {g: fit_models(sub, g) for g in GENES}
    return out


def scan_consortia_2026() -> dict[str, object]:
    cdir = resolve_dataset_path("DS_CONS2026")
    res: dict[str, object] = {}
    for tf in sorted(cdir.glob("*.txt")):
        txt = tf.read_text(encoding="utf-8", errors="replace")
        hits = {}
        for g in GENES:
            matches = [m.start() for m in re.finditer(rf"\b{g}\b", txt)]
            snippets = [txt[max(0, p - 100): min(len(txt), p + 180)].replace("\n", " ") for p in matches[:5]]
            hits[g] = {"mention_count": len(matches), "snippets": snippets}
        res[tf.name] = hits
    return res


if __name__ == "__main__":
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF"), sep="\t").dropna(subset=["Gene stable ID", "Gene % GC content"])
    ens_to_gc = dict(zip(gc_df["Gene stable ID"].astype(str), gc_df["Gene % GC content"].astype(float)))
    sym_to_ens = {
        g: set(gc_df.loc[gc_df["Gene name"] == g, "Gene stable ID"].astype(str)) for g in GENES
    }
    payload = {
        "analysis_run_id": "RUN-B1-003",
        "d003_pineda_pseudobulk": analyze_d003(ens_to_gc),
        "edinburgh_gse290359_pseudobulk": analyze_edinburgh(ens_to_gc, sym_to_ens),
        "consortia_2026_fulltexts": scan_consortia_2026(),
    }
    out_file = OUT_DIR / "run_b1_003_snrnaseq_consortia.json"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_file}")
