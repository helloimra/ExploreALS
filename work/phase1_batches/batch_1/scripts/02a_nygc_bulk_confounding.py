"""RUN-B1-002: Donor-level NYGC bulk RNA-seq confounding & subtype reanalysis for Batch 1."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.phase1_batches.batch_runner_utils import resolve_col, resolve_dataset_path

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_1" / "outputs"
TARGET_GENES = ["UNC13A", "STMN2", "KCNQ2", "CHMP7", "CHMP2B", "VPS4B"]
NEURO_GENES = ["SNAP25", "SYT1", "RBFOX3"]
GLIA_GENES = ["TYROBP", "AIF1", "GFAP", "ALDH1L1"]


def build_gene_lookup() -> tuple[dict[str, str], dict[str, float]]:
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF"), sep="\t")
    ens_col = resolve_col(gc_df, "Gene stable ID")
    sym_col = resolve_col(gc_df, "Gene name")
    pct_col = resolve_col(gc_df, "Gene % GC content")
    gc_df = gc_df.dropna(subset=[ens_col, pct_col]).drop_duplicates(subset=[ens_col])
    ens_to_gc = dict(zip(gc_df[ens_col].astype(str), gc_df[pct_col].astype(float)))
    sym_sub = gc_df[gc_df[sym_col].isin(TARGET_GENES + NEURO_GENES + GLIA_GENES)]
    ens_to_sym = dict(zip(sym_sub[ens_col].astype(str), sym_sub[sym_col].astype(str)))
    return ens_to_sym, ens_to_gc


def stream_nygc_counts(ens_to_sym: dict[str, str], ens_to_gc: dict[str, float]) -> pd.DataFrame:
    cpath = resolve_dataset_path("DS001_COUNTS")
    with gzip.open(cpath, "rt", encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        samples = header[1:]
        n_samp = len(samples)
        lib_size = np.zeros(n_samp, dtype=np.float64)
        hi_gc_sum = np.zeros(n_samp, dtype=np.float64)
        lo_gc_sum = np.zeros(n_samp, dtype=np.float64)
        gene_counts: dict[str, np.ndarray] = {}

        for line in fh:
            parts = line.rstrip("\n").split("\t")
            ens_raw = parts[1]
            ens_base = ens_raw.split(".")[0]
            arr = np.fromiter((float(x) for x in parts[2:]), dtype=np.float64, count=n_samp)
            lib_size += arr
            gc_val = ens_to_gc.get(ens_base)
            if gc_val is not None:
                if gc_val >= 60.0:
                    hi_gc_sum += arr
                elif gc_val <= 40.0:
                    lo_gc_sum += arr
            sym = ens_to_sym.get(ens_base)
            if sym is not None:
                gene_counts[sym] = gene_counts.get(sym, np.zeros(n_samp, dtype=np.float64)) + arr

    df = pd.DataFrame({"ExternalSampleId": samples, "lib_size_calc": lib_size})
    df["donor_gc_index"] = np.log2((hi_gc_sum + 1.0) / (lo_gc_sum + 1.0))
    for g, vec in gene_counts.items():
        df[f"log2cpm_{g}"] = np.log2(vec / np.maximum(lib_size, 1.0) * 1e6 + 0.5)
    df["neuro_score"] = df[[f"log2cpm_{g}" for g in NEURO_GENES if f"log2cpm_{g}" in df]].mean(axis=1)
    df["glia_score"] = df[[f"log2cpm_{g}" for g in GLIA_GENES if f"log2cpm_{g}" in df]].mean(axis=1)
    return df


def fit_ols_term(y: pd.Series, X: pd.DataFrame, term: str) -> dict[str, float]:
    Xc = sm.add_constant(X.astype(float), has_constant="add")
    fit = sm.OLS(y.astype(float), Xc).fit()
    return {
        "beta_log2fc": float(fit.params[term]),
        "se": float(fit.bse[term]),
        "t": float(fit.tvalues[term]),
        "p_value": float(fit.pvalues[term]),
        "n_donors": int(len(y)),
    }


def main() -> None:
    ens_to_sym, ens_to_gc = build_gene_lookup()
    gene_gc_pct = {}
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF"), sep="\t")
    for g in TARGET_GENES:
        vals = gc_df.loc[gc_df[resolve_col(gc_df, "Gene name")] == g, resolve_col(gc_df, "Gene % GC content")]
        gene_gc_pct[g] = float(vals.median()) if not vals.empty else None

    cnt_df = stream_nygc_counts(ens_to_sym, ens_to_gc)
    meta = pd.read_excel(resolve_dataset_path("DS001_META"))
    sid_col = resolve_col(meta, "ExternalSampleId")
    subj_col = resolve_col(meta, "ExternalSubjectId")
    dg_col = resolve_col(meta, "disease_group")
    src_col = resolve_col(meta, "Sample Source")
    rin_col = resolve_col(meta, "RIN")
    age_col = resolve_col(meta, "Age at Death")
    sex_col = resolve_col(meta, "Sex")
    plat_col = resolve_col(meta, "Platform")
    mut_col = resolve_col(meta, "Reported Genomic Mutations")
    tstmn2_col = resolve_col(meta, "tSTMN2_TPM")

    oneill_path = resolve_dataset_path("DS001_ONEILL")
    s1b = pd.read_excel(oneill_path, sheet_name="TableS1B", header=1)
    s1g = pd.read_excel(oneill_path, sheet_name="TableS1G", header=1)
    sub_map = pd.concat([
        s1b[[resolve_col(s1b, "Sample"), resolve_col(s1b, "ALS Subtype")]].rename(columns={resolve_col(s1b, "Sample"): "ExternalSampleId", resolve_col(s1b, "ALS Subtype"): "oneill_subtype"}),
        s1g[[resolve_col(s1g, "Sample"), resolve_col(s1g, "ALS Subtype")]].rename(columns={resolve_col(s1g, "Sample"): "ExternalSampleId", resolve_col(s1g, "ALS Subtype"): "oneill_subtype"}),
    ], ignore_index=True).drop_duplicates(subset=["ExternalSampleId"])

    m = cnt_df.merge(meta, left_on="ExternalSampleId", right_on=sid_col).merge(sub_map, on="ExternalSampleId", how="left")
    m["region_group"] = m[src_col].replace({
        "Cortex_Motor_Medial": "Motor_Cortex",
        "Cortex_Motor_Lateral": "Motor_Cortex",
        "Cortex_Motor_Unspecified": "Motor_Cortex",
        "Cortex_Frontal": "Frontal_Cortex",
        "Spinal_Cord_Cervical": "Cervical_Spinal_Cord",
        "Spinal_Cord_Lumbar": "Lumbar_Spinal_Cord",
        "Cerebellum": "Cerebellum",
    })
    mut_str = m[mut_col].fillna("None").astype(str)
    is_sals = (m[dg_col] == "ALS-TDP") & (~mut_str.str.contains("C9orf72|SOD1|FUS|TARDBP", case=False, regex=True))
    is_ctrl = m[dg_col] == "Control"
    m_sub = m[is_sals | is_ctrl].copy()
    m_sub["is_als"] = is_sals.loc[m_sub.index].astype(int)
    m_sub["rin_num"] = pd.to_numeric(m_sub[rin_col], errors="coerce")
    m_sub["age_num"] = pd.to_numeric(m_sub[age_col], errors="coerce")
    m_sub["is_male"] = (m_sub[sex_col].astype(str).str.lower() == "male").astype(int)
    m_sub["is_novaseq"] = m_sub[plat_col].astype(str).str.contains("NovaSeq", case=False, na=False).astype(int)
    m_sub["tSTMN2_num"] = pd.to_numeric(m_sub[tstmn2_col], errors="coerce").fillna(0.0)

    results: dict[str, object] = {"gene_gc_percent": gene_gc_pct, "regions": {}, "oneill_subtypes": {}, "tSTMN2_cryptic_summary": {}}
    num_cols = [f"log2cpm_{g}" for g in TARGET_GENES] + ["donor_gc_index", "neuro_score", "glia_score", "rin_num", "age_num", "is_male", "is_novaseq", "is_als", "tSTMN2_num"]

    for reg in ["Motor_Cortex", "Frontal_Cortex", "Cervical_Spinal_Cord", "Lumbar_Spinal_Cord", "Cerebellum"]:
        rdf = m_sub[m_sub["region_group"] == reg].groupby(subj_col, as_index=False)[num_cols].mean()
        rdf["is_als"] = (rdf["is_als"] >= 0.5).astype(int)
        rdf_complete = rdf.dropna(subset=["rin_num", "age_num"]).copy()
        n_als = int((rdf_complete["is_als"] == 1).sum())
        n_ctl = int((rdf_complete["is_als"] == 0).sum())
        reg_res = {"n_sals_donors": n_als, "n_ctrl_donors": n_ctl, "genes": {}}
        for g in TARGET_GENES:
            y = rdf_complete[f"log2cpm_{g}"]
            reg_res["genes"][g] = {
                "unadjusted": fit_ols_term(y, rdf_complete[["is_als"]], "is_als"),
                "tech_demo_adj": fit_ols_term(y, rdf_complete[["is_als", "rin_num", "age_num", "is_male", "is_novaseq"]], "is_als"),
                "gc_adj": fit_ols_term(y, rdf_complete[["is_als", "rin_num", "age_num", "is_male", "is_novaseq", "donor_gc_index"]], "is_als"),
                "gc_plus_cellcomp_adj": fit_ols_term(y, rdf_complete[["is_als", "rin_num", "age_num", "is_male", "is_novaseq", "donor_gc_index", "neuro_score", "glia_score"]], "is_als"),
            }
        als_t = rdf.loc[rdf["is_als"] == 1, "tSTMN2_num"]
        ctl_t = rdf.loc[rdf["is_als"] == 0, "tSTMN2_num"]
        results["tSTMN2_cryptic_summary"][reg] = {
            "sals_pos_donors": int((als_t > 0).sum()), "sals_total_donors": int(len(als_t)),
            "sals_mean_tSTMN2_TPM": float(als_t.mean()),
            "ctrl_pos_donors": int((ctl_t > 0).sum()), "ctrl_total_donors": int(len(ctl_t)),
            "ctrl_mean_tSTMN2_TPM": float(ctl_t.mean()),
        }
        results["regions"][reg] = reg_res

    ctx = m_sub[m_sub["region_group"].isin(["Motor_Cortex", "Frontal_Cortex"])].copy()
    for st_label in ["ALS-Glia", "ALS-Ox", "ALS-TE"]:
        st_df = ctx[(ctx["is_als"] == 0) | (ctx["oneill_subtype"] == st_label)].groupby(subj_col, as_index=False)[num_cols].mean()
        st_df["is_als"] = (st_df["is_als"] >= 0.5).astype(int)
        st_df = st_df.dropna(subset=["rin_num", "age_num"])
        results["oneill_subtypes"][st_label] = {
            "n_subtype_donors": int((st_df["is_als"] == 1).sum()),
            "n_ctrl_donors": int((st_df["is_als"] == 0).sum()),
            "genes_gc_adj": {
                g: fit_ols_term(st_df[f"log2cpm_{g}"], st_df[["is_als", "rin_num", "age_num", "is_male", "is_novaseq", "donor_gc_index"]], "is_als")
                for g in TARGET_GENES
            },
        }

    out_path = OUT_DIR / "run_b1_002_nygc_bulk_confounding.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
