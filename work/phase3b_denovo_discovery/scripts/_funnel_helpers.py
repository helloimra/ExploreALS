"""Modular helpers for RUN-P3B-001: ExploreALS exclusions, full-genome GC-adjusted BA4_Exc OLS+FDR, and multi-cohort Trautwig CSF."""
from __future__ import annotations

import csv
import math
from pathlib import Path
import re
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from carbon_als.loaders import (
    assert_unique_donors,
    load_pineda2024_pseudobulk,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

ALS_SET = {"sALS", "C9orf72", "SOD1"}
NONALS_SET = {"Control", "C9orf72-Asymptomatic", "SOD1-Asymptomatic"}


def clean_json(obj: Any) -> Any:
    if isinstance(obj, (float, np.floating)):
        v = float(obj)
        return None if (math.isnan(v) or math.isinf(v)) else v
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(v) for v in obj]
    return obj


def load_explore_exclusions(root: Path) -> tuple[set[str], set[str]]:
    intake = list(csv.DictReader((root / "registries" / "candidate_intake_ledger.csv").open(encoding="utf-8")))
    subnodes = list(csv.DictReader((root / "registries" / "subnode_dissection.csv").open(encoding="utf-8")))
    excl_genes = {"TARDBP", "SOD1", "C9ORF72", "FUS", "NPTX2", "NEFL", "NEFH", "GFAP", "IREB2", "PTAR1", "NMNAT2", "ST2"}
    excl_drugs = {
        "riluzole", "baricitinib", "memantine", "trazodone", "apilimod", "icerguastat", "sephin1", "ifb-088",
        "dexmedetomidine", "cuatsm", "mycophenolate mofetil", "mycophenolate", "tamoxifen", "ezogabine", "retigabine",
        "ceftriaxone", "ropinirole", "furosemide", "perampanel", "lonafarnib", "tipifarnib", "aldesleukin",
        "methylcobalamin", "rozebalamin", "censavudine", "tpn-101",
    }
    for r in intake:
        if r["track"] == "B":
            for tok in re.findall(r"[A-Z0-9-]{2,}", r["genes_or_drug_ids"]):
                if tok not in {"GENE", "SYMBOL", "SYMBOLS", "UNIPROT", "Q9UKA1"}:
                    excl_genes.add(tok)
        elif r["track"] == "A":
            for part in re.split(r"[()/;]", r["name"].lower()):
                cleaned = re.sub(r"^(low-dose|ultrahigh-dose)\s+", "", part.strip()).strip()
                if len(cleaned) >= 3:
                    excl_drugs.add(cleaned)
    for sn in subnodes:
        excl_genes.add(sn["gene_symbol"].strip())
    return excl_genes, excl_drugs


def compute_gc_adjusted_ba4_exc(genes: list[str]) -> dict[str, Any]:
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    gc_pc = gc_df[gc_df[resolve_col(gc_df, "Gene type")] == "protein_coding"].dropna(subset=["Gene name", "Gene % GC content"])
    gc_map = gc_pc.groupby("Gene name")["Gene % GC content"].mean().to_dict()
    all_pc = sorted(set(gc_map.keys()) | set(genes))

    pin = load_pineda2024_pseudobulk("BA4", "Excitatory", all_pc)
    pdf = pin["donor_df"]
    pdf = pdf[pdf["group"].isin(["SALS", "PN"])].copy()
    assert_unique_donors(pdf["donor_id"].astype(str).tolist(), "Pineda BA4_Exc SALS+PN")
    hg_cols = [g for g, v in gc_map.items() if v >= 60.0 and g in pdf.columns]
    lg_cols = [g for g, v in gc_map.items() if v <= 38.0 and g in pdf.columns]
    pdf["gc_shift"] = pdf[hg_cols].mean(axis=1) - pdf[lg_cols].mean(axis=1)
    pdf["is_sals"] = (pdf["group"] == "SALS").astype(float)
    assert len(hg_cols) >= 500 and len(lg_cols) >= 500 and int(pdf["is_sals"].sum()) == 16 and len(pdf) == 32

    expr_cols = [c for c in pdf.columns if (c in gc_map or c in set(genes)) and float(pdf[c].std()) > 1e-8]
    y_mat = pdf[expr_cols].astype(float).to_numpy()
    x_mat = sm.add_constant(pdf[["is_sals", "gc_shift"]]).to_numpy()
    betas = np.linalg.lstsq(x_mat, y_mat, rcond=None)[0]
    dof = len(pdf) - x_mat.shape[1]
    mse = ((y_mat - x_mat @ betas) ** 2).sum(axis=0) / dof
    cov11 = float(np.linalg.inv(x_mat.T @ x_mat)[1, 1])
    t_vals = betas[1] / np.sqrt(np.maximum(mse * cov11, 1e-30))
    p_vals = 2.0 * stats.t.sf(np.abs(t_vals), df=dof)
    q_vals = multipletests(p_vals, method="fdr_bh")[1]
    ols_map = {g: (float(b), float(p), float(q)) for g, b, p, q in zip(expr_cols, betas[1], p_vals, q_vals, strict=True)}

    by_gene: dict[str, Any] = {}
    for g in genes:
        if g not in ols_map:
            continue
        b_v, p_v, q_v = ols_map[g]
        st = pin["stats"].get(g, {})
        by_gene[g] = {
            "gc_pct": round(float(gc_map[g]), 2) if g in gc_map else None, "n_sals": 16, "n_pn": 16,
            "unadj_diff_log2cpm": round(float(st.get("diff_log2cpm", 0.0)), 4), "unadj_welch_p": float(st.get("p_welch", 1.0)),
            "gc_adj_beta_sals": round(b_v, 4), "gc_adj_p": p_v, "gc_adj_q_bh": q_v,
        }
    astro = load_pineda2024_pseudobulk("BA4", "Astro", ["MAOB", "GFAP"])["stats"]
    return {"n_high_gc_ref": len(hg_cols), "n_low_gc_ref": len(lg_cols), "n_pc_genes_fdr": len(expr_cols), "ba4_exc_by_gene": by_gene, "ba4_astro_maob_gfap": astro}


def scan_trautwig_deconfounded(excl_genes: set[str], target_genes: list[str]) -> dict[str, Any]:
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    c2 = read_xlsx_sparse_safe(p45, "2-Cohort-Exp Characteristics", 2)
    c2["dia_col"] = c2["_unnamed_col_0"].astype(str).str.replace(r"\.2$", "", regex=True).str.replace(r"\.(\d+)$", r"-\1", regex=True)
    dia = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    dia["sym"] = dia[resolve_col(dia, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
    mat = dia.groupby("sym")[c2["dia_col"].tolist()].first().T
    mat["status"] = c2.set_index("dia_col")["SymptomStatus"].astype(str)
    mat["bank"] = c2.set_index("dia_col")["TissueBank"].astype(str)
    assert set(mat["status"].unique()) <= (ALS_SET | NONALS_SET), f"Unexpected Trautwig status: {set(mat['status'].unique())}"
    ctab = pd.crosstab(mat["bank"], mat["status"]).to_dict(orient="index")

    em_pos, em_neg = mat[(mat["bank"] == "Emory") & (mat["status"] == "sALS")], mat[(mat["bank"] == "Emory") & (mat["status"] == "Control")]
    wu_pos, wu_neg = mat[(mat["bank"] == "WashU") & (mat["status"].isin(ALS_SET))], mat[(mat["bank"] == "WashU") & (mat["status"].isin(NONALS_SET))]
    assert_unique_donors(em_pos.index.tolist() + em_neg.index.tolist(), "Trautwig Emory DIA")
    assert_unique_donors(wu_pos.index.tolist() + wu_neg.index.tolist(), "Trautwig WashU DIA")

    rows: list[dict[str, Any]] = []
    for g in [c for c in mat.columns if c not in ("status", "bank") and c not in excl_genes and ";" not in c]:
        ep, en = pd.to_numeric(em_pos[g], errors="coerce").dropna(), pd.to_numeric(em_neg[g], errors="coerce").dropna()
        if len(ep) < 20 or len(en) < 20:
            continue
        wp, wn = pd.to_numeric(wu_pos[g], errors="coerce").dropna(), pd.to_numeric(wu_neg[g], errors="coerce").dropna()
        wu_ok = len(wp) >= 5 and len(wn) >= 5
        rows.append({
            "gene": g, "n_em_sals": int(len(ep)), "n_em_ctrl": int(len(en)), "n_em_total": int(len(ep) + len(en)),
            "em_log2fc": round(float(ep.mean() - en.mean()), 4), "em_p": float(stats.ttest_ind(ep, en, equal_var=False).pvalue),
            "n_wu_als": int(len(wp)), "n_wu_nonals": int(len(wn)), "n_wu_ctrl_only": int((wu_neg.loc[wn.index, "status"] == "Control").sum()),
            "wu_log2fc": round(float(wp.mean() - wn.mean()), 4) if wu_ok else None,
            "wu_p": float(stats.ttest_ind(wp, wn, equal_var=False).pvalue) if wu_ok else None,
            "wu_mwu_p": float(stats.mannwhitneyu(wp, wn, alternative="two-sided").pvalue) if wu_ok else None,
        })
    rdf = pd.DataFrame(rows)
    rdf["em_q_bh"] = multipletests(rdf["em_p"], method="fdr_bh")[1]
    rep_m = (rdf["em_q_bh"] < 0.05) & rdf["wu_p"].notna() & (rdf["wu_p"] < 0.05) & ((rdf["em_log2fc"] * rdf["wu_log2fc"]) > 0)
    fdr_nr, nonfdr = (rdf["em_q_bh"] < 0.05) & (~rep_m), rdf["em_q_bh"] >= 0.05
    assert int(rep_m.sum() + fdr_nr.sum() + nonfdr.sum()) == len(rdf), "Rule 3B-1 CSF partition mismatch!"

    tmt = read_xlsx_sparse_safe(p45, "6-TMT-MS ANOVA", 2)
    tmt["sym"] = tmt[resolve_col(tmt, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
    tmt_sub = tmt[tmt["sym"].isin(["DPP6", "DPP10", "CFL1"])].set_index("sym")[["F-Value", "Pr(>F)", "Sporadic-Control", "Control-ALS.C9", "Sporadic-ALS.C9", "diff Sporadic-Control", "diff Control-ALS.C9_inv", "diff Sporadic-ALS.C9_inv"]].to_dict(orient="index")
    oh_txt = resolve_dataset_path("DS046_OH_XML", verify_hash=True).read_text(encoding="utf-8")
    return {
        "n_non_explore_proteins_tested": int(len(rdf)), "bank_status_crosstab": ctab,
        "partition_counts": {"emory_fdr05_and_washu_concordant_p05": int(rep_m.sum()), "emory_fdr05_washu_unreplicated": int(fdr_nr.sum()), "emory_q_ge_0p05": int(nonfdr.sum())},
        "replicated_hits": rdf[rep_m].sort_values("em_p").to_dict(orient="records"),
        "set1_tmtpro_n101_anova": tmt_sub,
        "oh2023_prm_xml_mentions": {s: oh_txt.count(s) for s in ("DPP6", "DPP10", "CFL1", "CHIT1", "CHI3L1")},
        "target_lookup": {r["gene"]: r for r in rdf[rdf["gene"].isin(set(target_genes))].to_dict(orient="records")},
    }
