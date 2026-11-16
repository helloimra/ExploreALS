"""RUN-B2-002: Re-compute human CSF (Trautwig 2025 D045) and cortical/synaptosome (Spillman 2026 D029) proteomics."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase1_batches.batch_runner_utils import (  # noqa: E402
    assert_contrast_pair,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_2" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_GENES = [
    "SCFD1", "G2E3", "YKT6", "SEC22B", "STX5", "GOSR1", "NSF", "GDI2",
    "PTAR1", "FBXL5", "IREB2", "ACO1", "TFRC", "FTH1", "FTL", "TF", "CP",
]


def read_sheet_safe(xlsx_path: Path, sheet_name: str, header_row_1based: int = 1) -> pd.DataFrame:
    try:
        return read_xlsx_sparse_safe(xlsx_path, sheet_name, header_row_1based=header_row_1based)
    except ValueError:
        wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
        try:
            rows = list(wb[sheet_name].iter_rows(values_only=True))
        finally:
            wb.close()
        raw_h = list(rows[header_row_1based - 1])
        while raw_h and (raw_h[-1] is None or str(raw_h[-1]).strip() == ""):
            raw_h.pop()
        ncols = len(raw_h)
        headers = [str(h).strip() if h is not None and str(h).strip() else f"_unnamed_{i}" for i, h in enumerate(raw_h)]
        body = [list(r[:ncols]) + [None] * max(0, ncols - len(r)) for r in rows[header_row_1based:]]
        return pd.DataFrame(body, columns=headers)


def analyze_trautwig() -> dict:
    p = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    meta1 = read_sheet_safe(p, "1-Cohort-SC Characteristics", 2)
    meta2 = read_sheet_safe(p, "2-Cohort-Exp Characteristics", 2)
    tmt_raw = read_sheet_safe(p, "3-TMT-MS Raw Data", 2)
    dia_raw = read_sheet_safe(p, "5-DIA Raw Data", 2)
    tmt_anova = read_sheet_safe(p, "6-TMT-MS ANOVA", 2)
    pep_anova = read_sheet_safe(p, "7-Peptide ANOVA", 2)
    dia_anova = read_sheet_safe(p, "8-DIA ANOVA", 2)
    wgcna = read_sheet_safe(p, "9-WGCNA kME", 2)

    # Map Set 1 and Set 2 sample IDs cleanly (normalizing '.' vs '-' in Set 2 sample headers)
    ch_col = resolve_col(meta1, "Channel")
    dis_col = resolve_col(meta1, "Disease")
    sals_ch = [c for c in meta1.loc[meta1[dis_col].astype(str).str.strip() == "Sporadic", ch_col].astype(str) if c in tmt_raw.columns]
    ctrl_ch = [c for c in meta1.loc[meta1[dis_col].astype(str).str.strip() == "Control", ch_col].astype(str) if c in tmt_raw.columns]

    norm_dia_cols = {c.replace("-", "."): c for c in dia_raw.columns}
    raw_id_col2 = resolve_col(meta2, "_unnamed_col_0", "_unnamed_0")
    meta2 = meta2.copy()
    meta2["_dia_col"] = meta2[raw_id_col2].astype(str).str.replace("-", ".").map(norm_dia_cols)
    sym_col2 = resolve_col(meta2, "SymptomStatus")
    bank_col2 = resolve_col(meta2, "TissueBank")

    sals_dia = meta2.loc[meta2[sym_col2].astype(str).str.strip() == "sALS", "_dia_col"].dropna().tolist()
    als_dia = meta2.loc[meta2[sym_col2].astype(str).str.strip().isin({"sALS", "C9orf72", "SOD1"}), "_dia_col"].dropna().tolist()
    ctrl_dia = meta2.loc[meta2[sym_col2].astype(str).str.strip() == "Control", "_dia_col"].dropna().tolist()
    em_s = meta2.loc[(meta2[sym_col2] == "sALS") & (meta2[bank_col2] == "Emory"), "_dia_col"].dropna().tolist()
    em_c = meta2.loc[(meta2[sym_col2] == "Control") & (meta2[bank_col2] == "Emory"), "_dia_col"].dropna().tolist()

    p_col_dia = resolve_col(dia_raw, "Protein|Uniprot")
    p_col_tmt = resolve_col(tmt_raw, "Protein|Uniprot")

    # Programmatic contrast-pair & sign verification via assert_contrast_pair on exact regressed ANOVA contrasts
    tmt_err_c9 = assert_contrast_pair(
        tmt_anova[resolve_col(tmt_anova, "diff Sporadic-Control")],
        tmt_anova[resolve_col(tmt_anova, "diff Control-ALS.C9_inv")],
        tmt_anova[resolve_col(tmt_anova, "diff Sporadic-ALS.C9_inv")],
        sign=1.0, tol=1e-5,
    )
    dia_err_c9 = assert_contrast_pair(
        dia_anova[resolve_col(dia_anova, "diff C9orf72-C9orf72.Asymptomatic")],
        dia_anova[resolve_col(dia_anova, "diff C9orf72-Control")],
        dia_anova[resolve_col(dia_anova, "diff C9orf72.Asymptomatic-Control")],
        sign=1.0, tol=1e-5,
    )
    # Also quantify unregressed raw vs covariate-regressed ANOVA shift in DIA Set 2
    dia_means = pd.DataFrame({
        "prot": dia_raw[p_col_dia].astype(str),
        "mean_sals": dia_raw[sals_dia].apply(pd.to_numeric, errors="coerce").mean(axis=1),
        "mean_als": dia_raw[als_dia].apply(pd.to_numeric, errors="coerce").mean(axis=1),
        "mean_ctrl": dia_raw[ctrl_dia].apply(pd.to_numeric, errors="coerce").mean(axis=1),
    })
    merged_dia = dia_anova.merge(dia_means, left_on=resolve_col(dia_anova, "Protein|Uniprot"), right_on="prot")
    dia_unreg_vs_reg_r = float(
        pd.to_numeric(merged_dia[resolve_col(merged_dia, "diff sALS-Control")], errors="coerce")
        .corr(merged_dia["mean_sals"] - merged_dia["mean_ctrl"])
    )

    def match_gene(series: pd.Series) -> pd.Series:
        return series.astype(str).str.split("|").str[0].str.strip()

    gene_res: dict[str, dict] = {}
    for g in TARGET_GENES:
        t_rows = tmt_anova[match_gene(tmt_anova[resolve_col(tmt_anova, "Protein|Uniprot")]) == g]
        d_rows = dia_anova[match_gene(dia_anova[resolve_col(dia_anova, "Protein|Uniprot")]) == g]
        p_rows = pep_anova[match_gene(pep_anova[resolve_col(pep_anova, "Protein|Uniprot|Peptide")]) == g]
        w_rows = wgcna[wgcna[resolve_col(wgcna, "UniqueID")].astype(str).str.split("|").str[0].str.strip() == g]

        donor_tests = []
        for _, tr in tmt_raw[match_gene(tmt_raw[p_col_tmt]) == g].iterrows():
            vs = np.log2(pd.to_numeric(tr[sals_ch], errors="coerce").replace(0, np.nan)).dropna().values
            vc = np.log2(pd.to_numeric(tr[ctrl_ch], errors="coerce").replace(0, np.nan)).dropna().values
            donor_tests.append({
                "assay": "TMT_Set1_unregressed_log2", "protein_id": tr[p_col_tmt],
                "n_sals": int(len(vs)), "n_ctrl": int(len(vc)),
                "diff_log2": float(np.mean(vs) - np.mean(vc)) if len(vs) and len(vc) else None,
                "welch_p": float(stats.ttest_ind(vs, vc, equal_var=False).pvalue) if len(vs) > 1 and len(vc) > 1 else None,
            })
        for _, dr in dia_raw[match_gene(dia_raw[p_col_dia]) == g].iterrows():
            vs = pd.to_numeric(dr[sals_dia], errors="coerce").dropna().values
            vc = pd.to_numeric(dr[ctrl_dia], errors="coerce").dropna().values
            ves = pd.to_numeric(dr[em_s], errors="coerce").dropna().values
            vec = pd.to_numeric(dr[em_c], errors="coerce").dropna().values
            donor_tests.append({
                "assay": "DIA_Set2_donor_log2", "protein_id": dr[p_col_dia],
                "all_n_sals": int(len(vs)), "all_n_ctrl": int(len(vc)),
                "all_diff_log2": float(np.mean(vs) - np.mean(vc)) if len(vs) and len(vc) else None,
                "all_welch_p": float(stats.ttest_ind(vs, vc, equal_var=False).pvalue) if len(vs) > 1 and len(vc) > 1 else None,
                "all_mwu_p": float(stats.mannwhitneyu(vs, vc).pvalue) if len(vs) > 1 and len(vc) > 1 else None,
                "emory_n_sals": int(len(ves)), "emory_n_ctrl": int(len(vec)),
                "emory_diff_log2": float(np.mean(ves) - np.mean(vec)) if len(ves) and len(vec) else None,
                "emory_welch_p": float(stats.ttest_ind(ves, vec, equal_var=False).pvalue) if len(ves) > 1 and len(vec) > 1 else None,
            })
        gene_res[g] = {
            "tmt_anova": t_rows.to_dict(orient="records"),
            "dia_anova": d_rows.to_dict(orient="records"),
            "peptide_anova": p_rows.to_dict(orient="records"),
            "wgcna_kme": w_rows.to_dict(orient="records"),
            "donor_recompute": donor_tests,
        }

    return {
        "cohort_set1_counts": meta1[dis_col].value_counts(dropna=False).to_dict(),
        "cohort_set2_mapped": int(meta2["_dia_col"].notna().sum()),
        "cohort_set2_by_bank_status": meta2.groupby([bank_col2, sym_col2], dropna=False).size().reset_index(name="n").to_dict(orient="records"),
        "contrast_pair_max_err": {
            "tmt_c9_triangle": tmt_err_c9,
            "dia_c9_triangle": dia_err_c9,
            "dia_unregressed_vs_regressed_pearson_r": dia_unreg_vs_reg_r,
        },
        "genes": gene_res,
    }


def analyze_spillman() -> dict:
    sdir = resolve_dataset_path("DS029_SPILL")
    m1 = read_sheet_safe(sdir / "401_2026_3084_MOESM1_ESM.xlsx", "Sheet1", 1)
    m2_hom = read_sheet_safe(sdir / "401_2026_3084_MOESM2_ESM.xlsx", "Homogenate", 2)
    m2_syn = read_sheet_safe(sdir / "401_2026_3084_MOESM2_ESM.xlsx", "Synaptosome", 2)
    m3 = read_sheet_safe(sdir / "401_2026_3084_MOESM3_ESM.xlsx", "Sheet1", 1)

    # MOESM1: Frontal cortex DIA proteomics — strictly separate Synapt_FRCTX (Norm_S*, n=10 vs 10) from Homogenate_FRCTX (Norm_H*, n=10 vs 10)
    syn_ctl_cols = [c for c in m1.columns if c.startswith("Norm_S") and "Synapt_FRCTX_Control" in c]
    syn_c9_cols = [c for c in m1.columns if c.startswith("Norm_S") and "Synapt_FRCTX_C9FTD" in c]
    hom_ctl_cols = [c for c in m1.columns if c.startswith("Norm_H") and "Homogenate_FRCTX_Control" in c]
    hom_c9_cols = [c for c in m1.columns if c.startswith("Norm_H") and "Homogenate_FRCTX_C9FTD" in c]

    syn_err = assert_contrast_pair(
        m1[resolve_col(m1, "Log2Ratios_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")],
        m1[syn_c9_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1),
        m1[syn_ctl_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1),
        sign=1.0, tol=1e-2,
    )
    hom_err = assert_contrast_pair(
        m1[resolve_col(m1, "Log2Ratios_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control")],
        m1[hom_c9_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1),
        m1[hom_ctl_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1),
        sign=1.0, tol=1e-2,
    )

    # MOESM3: iPSC neuron DIA proteomics — strictly separate Homogenate_iPSC (HOx*, n=3 vs 3) from Pellet_iPSC (Px*, n=3 vs 3)
    hox_ctl_cols = [c for c in m3.columns if "HOxCTRL" in c and c.startswith("Norm_")]
    hox_c9_cols = [c for c in m3.columns if "HOxC9FTD" in c and c.startswith("Norm_")]
    px_ctl_cols = [c for c in m3.columns if "PxCTRL" in c and c.startswith("Norm_")]
    px_c9_cols = [c for c in m3.columns if "PxC9FTD" in c and c.startswith("Norm_")]

    gcol1 = resolve_col(m1, "Gene")
    acc1 = resolve_col(m1, "Accession")
    gcol3 = resolve_col(m3, "Gene")
    acc3 = resolve_col(m3, "Accession")

    genes_out: dict[str, dict] = {}
    for sym in TARGET_GENES:
        rec: dict[str, object] = {"gene": sym}

        # 1. MOESM1 Frontal Cortex DIA Proteomics (Synaptosome vs Homogenate separated)
        r1 = m1[m1[gcol1].fillna("").astype(str).str.split(";").apply(lambda xs: sym in [x.strip() for x in xs])]
        rec["moesm1_frctx_proteomics_detected"] = bool(len(r1) > 0)
        if len(r1) > 0:
            row = r1.iloc[0]
            sc_v = pd.to_numeric(row[syn_ctl_cols], errors="coerce").dropna().values
            s9_v = pd.to_numeric(row[syn_c9_cols], errors="coerce").dropna().values
            hc_v = pd.to_numeric(row[hom_ctl_cols], errors="coerce").dropna().values
            h9_v = pd.to_numeric(row[hom_c9_cols], errors="coerce").dropna().values
            rec["moesm1_accession"] = str(row[acc1])
            rec["moesm1_synapt_frctx_proteomics"] = {
                "assay_modality": "DIA_proteomics_Synapt_FRCTX",
                "n_c9ftd": int(len(s9_v)),
                "n_ctrl": int(len(sc_v)),
                "recomputed_log2fc": float(np.mean(s9_v) - np.mean(sc_v)) if len(s9_v) and len(sc_v) else None,
                "recomputed_welch_p": float(stats.ttest_ind(s9_v, sc_v, equal_var=False).pvalue) if len(s9_v) > 1 and len(sc_v) > 1 else None,
                "table_log2fc": float(row[resolve_col(m1, "Log2Ratios_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")]),
                "table_p": float(row[resolve_col(m1, "pVal_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")]),
                "table_padj": float(row[resolve_col(m1, "pAdj_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")]),
            }
            rec["moesm1_homogenate_frctx_proteomics"] = {
                "assay_modality": "DIA_proteomics_Homogenate_FRCTX",
                "n_c9ftd": int(len(h9_v)),
                "n_ctrl": int(len(hc_v)),
                "recomputed_log2fc": float(np.mean(h9_v) - np.mean(hc_v)) if len(h9_v) and len(hc_v) else None,
                "recomputed_welch_p": float(stats.ttest_ind(h9_v, hc_v, equal_var=False).pvalue) if len(h9_v) > 1 and len(hc_v) > 1 else None,
                "table_log2fc": float(row[resolve_col(m1, "Log2Ratios_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control")]),
                "table_p": float(row[resolve_col(m1, "pVal_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control")]),
                "table_padj": float(row[resolve_col(m1, "pAdj_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control")]),
            }
        else:
            rec["moesm1_synapt_frctx_proteomics"] = None
            rec["moesm1_homogenate_frctx_proteomics"] = None

        # 2. MOESM3 iPSC-Neuron DIA Proteomics (Homogenate HOx vs Pellet Px separated)
        r3 = m3[m3[gcol3].fillna("").astype(str).str.split(";").apply(lambda xs: sym in [x.strip() for x in xs])]
        rec["moesm3_ipsc_proteomics_detected"] = bool(len(r3) > 0)
        if len(r3) > 0:
            rw3 = r3.iloc[0]
            hox_ctl = pd.to_numeric(rw3[hox_ctl_cols], errors="coerce").dropna().values if hox_ctl_cols else np.array([])
            hox_c9 = pd.to_numeric(rw3[hox_c9_cols], errors="coerce").dropna().values if hox_c9_cols else np.array([])
            px_ctl = pd.to_numeric(rw3[px_ctl_cols], errors="coerce").dropna().values if px_ctl_cols else np.array([])
            px_c9 = pd.to_numeric(rw3[px_c9_cols], errors="coerce").dropna().values if px_c9_cols else np.array([])
            rec["moesm3_accession"] = str(rw3[acc3])
            rec["moesm3_homogenate_ipsc_proteomics"] = {
                "assay_modality": "DIA_proteomics_Homogenate_iPSC",
                "n_c9ftd": int(len(hox_c9)),
                "n_ctrl": int(len(hox_ctl)),
                "recomputed_log2fc": float(np.mean(hox_c9) - np.mean(hox_ctl)) if len(hox_c9) and len(hox_ctl) else None,
                "recomputed_welch_p": float(stats.ttest_ind(hox_c9, hox_ctl, equal_var=False).pvalue) if len(hox_c9) > 1 and len(hox_ctl) > 1 else None,
                "table_log2fc": float(rw3[resolve_col(m3, "Log2FC_HOxC9FTD.HOxCTRL")]),
                "table_p": float(rw3[resolve_col(m3, "pVal_HOxC9FTD.HOxCTRL")]),
                "table_padj": float(rw3[resolve_col(m3, "pAdj_HOxC9FTD.HOxCTRL")]),
            }
            rec["moesm3_pellet_ipsc_proteomics"] = {
                "assay_modality": "DIA_proteomics_Pellet_iPSC",
                "n_c9ftd": int(len(px_c9)),
                "n_ctrl": int(len(px_ctl)),
                "recomputed_log2fc": float(np.mean(px_c9) - np.mean(px_ctl)) if len(px_c9) and len(px_ctl) else None,
                "recomputed_welch_p": float(stats.ttest_ind(px_c9, px_ctl, equal_var=False).pvalue) if len(px_c9) > 1 and len(px_ctl) > 1 else None,
                "table_log2fc": float(rw3[resolve_col(m3, "Log2FC_PxC9FTD.PxCTRL")]),
                "table_p": float(rw3[resolve_col(m3, "pVal_PxC9FTD.PxCTRL")]),
                "table_padj": float(rw3[resolve_col(m3, "pAdj_PxC9FTD.PxCTRL")]),
            }
        else:
            rec["moesm3_homogenate_ipsc_proteomics"] = None
            rec["moesm3_pellet_ipsc_proteomics"] = None

        # 3. MOESM2 Frontal Cortex DESeq2 RNA-seq (explicitly labeled RNAseq, NOT proteomics)
        for key_label, df2, frac_name in [
            ("Spillman_MOESM2_RNAseq_homogenate", m2_hom, "Homogenate_FRCTX_DESeq2_RNAseq"),
            ("Spillman_MOESM2_RNAseq_synaptosome", m2_syn, "Synaptosome_FRCTX_DESeq2_RNAseq"),
        ]:
            gn_col = resolve_col(df2, "gene_name")
            r2 = df2[df2[gn_col].astype(str).str.strip() == sym]
            if len(r2) > 0:
                rw2 = r2.iloc[0]
                rec[key_label] = {
                    "assay_modality": frac_name,
                    "ensembl_id": str(rw2.iloc[0]),
                    "baseMean": float(rw2[resolve_col(df2, "baseMean")]),
                    "log2FoldChange": float(rw2[resolve_col(df2, "log2FoldChange")]),
                    "pvalue": float(rw2[resolve_col(df2, "pvalue")]),
                    "padj": float(rw2[resolve_col(df2, "padj")]) if pd.notna(rw2[resolve_col(df2, "padj")]) else None,
                }
            else:
                rec[key_label] = None

        genes_out[sym] = rec

    return {
        "contrast_pair_max_err": {
            "moesm1_synapt_frctx_c9_vs_ctrl": syn_err,
            "moesm1_homogenate_frctx_c9_vs_ctrl": hom_err,
        },
        "sample_counts": {
            "moesm1_synapt_frctx_proteomics": {"n_c9ftd": len(syn_c9_cols), "n_ctrl": len(syn_ctl_cols)},
            "moesm1_homogenate_frctx_proteomics": {"n_c9ftd": len(hom_c9_cols), "n_ctrl": len(hom_ctl_cols)},
            "moesm3_homogenate_ipsc_proteomics": {"n_c9ftd": len(hox_c9_cols), "n_ctrl": len(hox_ctl_cols)},
            "moesm3_pellet_ipsc_proteomics": {"n_c9ftd": len(px_c9_cols), "n_ctrl": len(px_ctl_cols)},
        },
        "genes": genes_out,
    }


if __name__ == "__main__":
    payload = {"trautwig2025_d045": analyze_trautwig(), "spillman2026_d029": analyze_spillman()}
    out_path = OUT_DIR / "b2_002_proteomics_csf_tissue.json"
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[RUN-B2-002] Wrote {out_path} ({out_path.stat().st_size:,} bytes)")
