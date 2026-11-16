"""RUN-B3-001: Primary CSF Proteomics Re-Computation (Trautwig 2025 DS045 + Oh 2023 DS046)."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from scripts.phase1_batches.batch_runner_utils import (
    assert_contrast_pair, read_xlsx_sparse_safe, resolve_col, resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_3" / "outputs"
TARGETS = ["IL1RL1", "IL33", "CHIT1", "GPNMB", "CHI3L1", "CHI3L2", "C1QA", "C1QB", "C1QC", "C3", "C4A", "C4B", "NEFL"]
UNIPROTS = {"Q01638": "IL1RL1", "O95760": "IL33", "Q13231": "CHIT1", "Q14956": "GPNMB", "P36222": "CHI3L1",
            "Q15782": "CHI3L2", "P02745": "C1QA", "P02746": "C1QB", "P02747": "C1QC", "P01024": "C3",
            "P0C0L4": "C4A", "P0C0L5": "C4B", "P07196": "NEFL"}


def bh_series(s: pd.Series) -> pd.Series:
    p = pd.to_numeric(s, errors="coerce")
    out = pd.Series(np.nan, index=s.index)
    m = p.notna()
    if m.sum() > 0:
        out.loc[m] = multipletests(p.loc[m], method="fdr_bh")[1]
    return out


def parse_xml_tables(ds_id: str) -> list[dict]:
    root = ET.fromstring(resolve_dataset_path(ds_id).read_text(encoding="utf-8", errors="replace"))
    out = []
    for tw in root.findall(".//table-wrap"):
        rows = [["".join(c.itertext()).strip() for c in tr.findall("./*")] for tr in tw.findall(".//tr")]
        out.append({"id": tw.attrib.get("id", ""), "rows": rows})
    return out


def match_gene(pid: str) -> str | None:
    parts = str(pid).split("|")
    sym = parts[0].strip()
    uni = parts[1].strip().split("-")[0] if len(parts) > 1 else ""
    if sym in TARGETS:
        return sym
    return UNIPROTS.get(uni)


def main() -> None:
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    c1 = read_xlsx_sparse_safe(p45, "1-Cohort-SC Characteristics", 2)
    c2 = read_xlsx_sparse_safe(p45, "2-Cohort-Exp Characteristics", 2)
    tmt_raw = read_xlsx_sparse_safe(p45, "3-TMT-MS Raw Data", 2)
    pep_raw = read_xlsx_sparse_safe(p45, "4-Peptide Raw Data", 2)
    dia_raw = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    tmt_aov = read_xlsx_sparse_safe(p45, "6-TMT-MS ANOVA", 2)
    dia_aov = read_xlsx_sparse_safe(p45, "8-DIA ANOVA", 2)
    wgcna = read_xlsx_sparse_safe(p45, "9-WGCNA kME", 2)

    # 1. Cohort marginals & XML verification
    xml45 = parse_xml_tables("DS045_XML")
    c1_ch, c1_dis = resolve_col(c1, "Channel"), resolve_col(c1, "Disease")
    c2_ch, c2_id, c2_st = "_unnamed_col_0", resolve_col(c2, "ID"), resolve_col(c2, "SymptomStatus")
    c2["dia_col"] = c2[c2_ch].astype(str).str.replace(r"\.2$", "", regex=True).str.replace(r"\.(\d+)$", r"-\1", regex=True)
    assert c2["dia_col"].isin(dia_raw.columns).all(), "Failed to map all 259 DIA channels"
    assert c2[c2_id].nunique() == len(c2) == 259, "Expected 259 unique donors (0 longitudinal pairs)"

    # 2. Contrast pair assertions (algebraic sign & contrast alignment + raw vs TAMPOR check)
    tmt_pcol, dia_pcol = resolve_col(tmt_raw, "Protein|Uniprot"), resolve_col(dia_raw, "Protein|Uniprot")
    tmt_mat = tmt_raw.set_index(tmt_pcol)[c1[c1_ch].tolist()].apply(pd.to_numeric, errors="coerce")
    tmt_log2 = np.log2(tmt_mat.where(tmt_mat > 0))
    tmt_aov_idx = tmt_aov.set_index(resolve_col(tmt_aov, "Protein|Uniprot"))
    err_tmt = assert_contrast_pair(
        tmt_aov_idx[resolve_col(tmt_aov_idx, "diff Sporadic-ALS.C9_inv")],
        tmt_aov_idx[resolve_col(tmt_aov_idx, "diff Control-ALS.C9_inv")],
        tmt_aov_idx[resolve_col(tmt_aov_idx, "diff Sporadic-Control")], sign=1.0, tol=1e-5,
    )
    err_tmt_asym = assert_contrast_pair(
        tmt_aov_idx[resolve_col(tmt_aov_idx, "diff ALS.C9.Asymptomatic-ALS.C9_inv")],
        tmt_aov_idx[resolve_col(tmt_aov_idx, "diff Control-ALS.C9_inv")],
        tmt_aov_idx[resolve_col(tmt_aov_idx, "diff Control-ALS.C9.Asymptomatic_inv")], sign=1.0, tol=1e-3,
    )

    dia_mat = dia_raw.set_index(dia_pcol)[c2["dia_col"].tolist()].apply(pd.to_numeric, errors="coerce")
    dia_aov_idx = dia_aov.set_index(resolve_col(dia_aov, "Protein|Uniprot"))
    err_dia_c9 = assert_contrast_pair(
        dia_aov_idx[resolve_col(dia_aov_idx, "diff C9orf72-C9orf72.Asymptomatic")],
        dia_aov_idx[resolve_col(dia_aov_idx, "diff C9orf72-Control")],
        dia_aov_idx[resolve_col(dia_aov_idx, "diff C9orf72.Asymptomatic-Control")], sign=1.0, tol=1e-5,
    )
    err_dia_sod1 = assert_contrast_pair(
        dia_aov_idx[resolve_col(dia_aov_idx, "diff SOD1-SOD1.Asymptomatic")],
        dia_aov_idx[resolve_col(dia_aov_idx, "diff SOD1-Control")],
        dia_aov_idx[resolve_col(dia_aov_idx, "diff SOD1.Asymptomatic-Control")], sign=1.0, tol=1e-5,
    )
    err_dia_cs = assert_contrast_pair(
        dia_aov_idx[resolve_col(dia_aov_idx, "diff C9orf72-SOD1")],
        dia_aov_idx[resolve_col(dia_aov_idx, "diff C9orf72-Control")],
        dia_aov_idx[resolve_col(dia_aov_idx, "diff SOD1-Control")], sign=1.0, tol=1e-5,
    )

    # 3. Proteome-wide BH adjustment + Donor covariate OLS + Emory duration correlations
    for col in ["Pr(>F)", "Sporadic-Control", "Control-ALS.C9", "Control-ALS.C9.Asymptomatic", "ALS.C9.Asymptomatic-ALS.C9"]:
        tmt_aov_idx[f"bh_{col}"] = bh_series(tmt_aov_idx[resolve_col(tmt_aov_idx, col)])
    for col in ["Pr(>F)", "ALS-Control", "Symptomatic-Asymptomatic", "sALS-Control", "C9orf72.Asymptomatic-Control", "SOD1.Asymptomatic-Control"]:
        dia_aov_idx[f"bh_{col}"] = bh_series(dia_aov_idx[resolve_col(dia_aov_idx, col)])

    w_map = wgcna.set_index(resolve_col(wgcna, "UniqueID"))[resolve_col(wgcna, "net$colors")].to_dict()
    c1["dur_yr"] = pd.to_numeric(c1[resolve_col(c1, "AgeAtSample")], errors="coerce") - pd.to_numeric(c1[resolve_col(c1, "AgeOnset")], errors="coerce")
    sals_dur = c1.loc[(c1[c1_dis] == "Sporadic") & c1["dur_yr"].notna(), [c1_ch, "dur_yr"]]

    rows = []
    for g in TARGETS:
        tmt_hits = [k for k in tmt_aov_idx.index if match_gene(k) == g]
        dia_hits = [k for k in dia_aov_idx.index if match_gene(k) == g]
        pep_n = int(pep_raw[resolve_col(pep_raw, "Protein|Uniprot|Peptide")].astype(str).apply(match_gene).eq(g).sum())
        rec: dict = {"gene": g, "tmt_detected": bool(tmt_hits), "tmt_peptides_n": pep_n, "dia_detected": bool(dia_hits)}
        if tmt_hits:
            tk = tmt_hits[0]
            tr = tmt_aov_idx.loc[tk]
            y_s = tmt_log2.loc[tk, sals_dur[c1_ch]].dropna()
            d_s = sals_dur.set_index(c1_ch).loc[y_s.index, "dur_yr"]
            r_p, p_p = stats.pearsonr(y_s, d_s) if len(y_s) >= 5 else (np.nan, np.nan)
            r_s, p_s = stats.spearmanr(y_s, d_s) if len(y_s) >= 5 else (np.nan, np.nan)
            rec.update({"tmt_id": tk, "wgcna_module": w_map.get(tk, "none"),
                        "tmt_diff_sals_ctrl": float(tr["diff Sporadic-Control"]), "tmt_p_sals_ctrl": float(tr["Sporadic-Control"]),
                        "tmt_bh_sals_ctrl": float(tr["bh_Sporadic-Control"]), "tmt_p_omnibus": float(tr["Pr(>F)"]),
                        "tmt_bh_omnibus": float(tr["bh_Pr(>F)"]), "emory_sals_dur_n": int(len(y_s)),
                        "emory_sals_dur_pearson_r": float(r_p), "emory_sals_dur_pearson_p": float(p_p),
                        "emory_sals_dur_spearman_rho": float(r_s), "emory_sals_dur_spearman_p": float(p_s)})
        for dk in (dia_hits or [None]):
            r_copy = dict(rec)
            if dk:
                dr = dia_aov_idx.loc[dk]
                df_m = c2.copy()
                df_m["y"] = dia_mat.loc[dk, df_m["dia_col"]].values
                df_m["Age_num"] = pd.to_numeric(df_m[resolve_col(df_m, "Age")], errors="coerce")
                sub = df_m[df_m[c2_st].isin(["sALS", "Control"]) & df_m["y"].notna()].copy()
                sub["is_sals"] = (sub[c2_st] == "sALS").astype(int)
                fit = smf.ols("y ~ is_sals + Age_num + C(Sex) + C(TissueBank)", data=sub).fit()
                fit_b = smf.ols("y ~ is_sals + Age_num + C(Sex) + C(TissueBank) + C(Batch)", data=sub).fit()
                r_copy.update({"dia_id": dk, "dia_n_nonmissing": int(df_m["y"].notna().sum()),
                               "dia_diff_sals_ctrl": float(dr["diff sALS-Control"]), "dia_p_sals_ctrl": float(dr["sALS-Control"]),
                               "dia_bh_sals_ctrl": float(dr["bh_sALS-Control"]), "dia_diff_als_ctrl": float(dr["diff ALS-Control"]),
                               "dia_p_als_ctrl": float(dr["ALS-Control"]), "dia_bh_als_ctrl": float(dr["bh_ALS-Control"]),
                               "dia_diff_sym_asym": float(dr["diff Symptomatic-Asymptomatic"]), "dia_p_sym_asym": float(dr["Symptomatic-Asymptomatic"]),
                               "dia_bh_sym_asym": float(dr["bh_Symptomatic-Asymptomatic"]),
                               "dia_diff_c9asym_ctrl": float(dr["diff C9orf72.Asymptomatic-Control"]),
                               "dia_p_c9asym_ctrl": float(dr["C9orf72.Asymptomatic-Control"]), "dia_bh_c9asym_ctrl": float(dr["bh_C9orf72.Asymptomatic-Control"]),
                               "dia_p_sod1asym_ctrl": float(dr["SOD1.Asymptomatic-Control"]),
                               "dia_covadj_sals_ctrl_beta": float(fit.params["is_sals"]), "dia_covadj_sals_ctrl_p": float(fit.pvalues["is_sals"]),
                               "dia_batch_covadj_beta": float(fit_b.params["is_sals"]), "dia_batch_covadj_p": float(fit_b.pvalues["is_sals"]),
                               "dia_covadj_n": int(fit.nobs)})
            rows.append(r_copy)

    # 4. Oh 2023 (DS046_OH_XML) Table 2 & PRM extraction
    xml46 = parse_xml_tables("DS046_OH_XML")
    raw46 = resolve_dataset_path("DS046_OH_XML", verify_hash=True).read_text(encoding="utf-8", errors="replace")
    oh_t2 = [r for r in xml46[1]["rows"] if any(t in " ".join(r) for t in TARGETS)]
    prm_sec = re.findall(r"3\.5\.\s*Validation.*?(?=4\.\s*Discussion)", re.sub(r"<[^>]+>", " ", raw46), flags=re.S)

    out_json = {
        "cohort_verification": {"tmt_n": int(len(c1)), "tmt_groups": c1[c1_dis].value_counts().to_dict(),
                                "dia_n": int(len(c2)), "dia_unique_donors": int(c2[c2_id].nunique()),
                                "dia_groups": c2[c2_st].value_counts().to_dict(), "dia_centers": c2[resolve_col(c2, "TissueBank")].value_counts().to_dict(),
                                "xml_tab1_rows": xml45[0]["rows"], "xml_tab2_rows": xml45[1]["rows"]},
        "contrast_assertions_max_abs_err": {"tmt_c9_sals_ctrl_triangle": err_tmt, "tmt_c9_asym_ctrl_triangle": err_tmt_asym,
                                            "dia_c9_asym_ctrl_triangle": err_dia_c9, "dia_sod1_asym_ctrl_triangle": err_dia_sod1,
                                            "dia_c9_sod1_ctrl_triangle": err_dia_cs},
        "target_results": rows,
        "oh2023_d046": {"table1_demographics": xml46[0]["rows"], "table2_target_rows": oh_t2, "prm_section_text": prm_sec[0][:3500] if prm_sec else ""},
    }
    (OUT_DIR / "run_b3_001_proteomics.json").write_text(json.dumps(out_json, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(OUT_DIR / "run_b3_001_proteomics_summary.csv", index=False)
    print(f"RUN-B3-001 complete: {len(rows)} target rows, max contrast err={max(err_tmt, err_tmt_asym, err_dia_c9, err_dia_sod1, err_dia_cs):.2e}")


if __name__ == "__main__":
    main()
