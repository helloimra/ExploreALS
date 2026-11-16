"""RUN-B1-004: Primary reanalysis of CSF (Trautwig 2025 DS045) & Frontal Cortex/Synaptosome (Spillman 2026 DS029) proteomics."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import fisher_exact, mannwhitneyu, spearmanr, ttest_ind

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.phase1_batches.batch_runner_utils import assert_contrast_pair, resolve_col, resolve_dataset_path

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_1" / "outputs"
TARGETS = {
    "UNC13A": "Q9UPW8", "STMN2": "Q93045", "KCNQ2": "O43526",
    "CHMP7": "Q8WUX9", "CHMP2B": "Q9UQN3", "VPS4B": "O75351", "GDI2": "P50395",
}


def match_prot(series: pd.Series, sym: str, uni: str) -> pd.Series:
    s = series.fillna("").astype(str)
    return s.str.contains(rf"(?:^|\|){sym}(?:\||$)", regex=True) | s.str.contains(uni, regex=False)


def analyze_ds045() -> dict[str, object]:
    p45 = resolve_dataset_path("DS045_TRAUT")
    tmt_anova = pd.read_excel(p45, sheet_name="6-TMT-MS ANOVA", skiprows=1)
    dia_anova = pd.read_excel(p45, sheet_name="8-DIA ANOVA", skiprows=1)
    pep_anova = pd.read_excel(p45, sheet_name="7-Peptide ANOVA", skiprows=1)
    wgcna = pd.read_excel(p45, sheet_name="9-WGCNA kME", skiprows=1)
    sc_meta = pd.read_excel(p45, sheet_name="1-Cohort-SC Characteristics", skiprows=1)
    tmt_raw = pd.read_excel(p45, sheet_name="3-TMT-MS Raw Data", skiprows=1)

    p_tmt = resolve_col(tmt_anova, "Sporadic-Control")
    d_tmt = resolve_col(tmt_anova, "diff Sporadic-Control")
    p_dia_sals = resolve_col(dia_anova, "sALS-Control")
    d_dia_sals = resolve_col(dia_anova, "diff sALS-Control")
    p_dia_als = resolve_col(dia_anova, "ALS-Control")
    d_dia_als = resolve_col(dia_anova, "diff ALS-Control")
    p_dia_c9 = resolve_col(dia_anova, "C9orf72-Control")
    d_dia_c9 = resolve_col(dia_anova, "diff C9orf72-Control")

    id_tmt = resolve_col(tmt_anova, "Protein|Uniprot")
    id_dia = resolve_col(dia_anova, "Protein|Uniprot")
    id_pep = resolve_col(pep_anova, "Protein|Uniprot|Peptide")
    id_wgcna = resolve_col(wgcna, "UniqueID")
    mod_col = resolve_col(wgcna, "net$colors")

    # Verify algebraic contrast sign/scale identities via assert_contrast_pair
    tmt_alg_err = assert_contrast_pair(
        tmt_anova[resolve_col(tmt_anova, "diff Sporadic-ALS.C9_inv")],
        tmt_anova[resolve_col(tmt_anova, "diff Control-ALS.C9_inv")],
        tmt_anova[d_tmt],
        sign=1.0, tol=1e-5,
    )
    dia_alg_err = assert_contrast_pair(
        dia_anova[resolve_col(dia_anova, "diff C9orf72-SOD1")],
        dia_anova[d_dia_c9],
        dia_anova[resolve_col(dia_anova, "diff SOD1-Control")],
        sign=1.0, tol=1e-5,
    )
    ch_col = resolve_col(sc_meta, "Channel")
    dis_col = resolve_col(sc_meta, "Disease")
    sals_ch = [c for c in sc_meta.loc[sc_meta[dis_col] == "Sporadic", ch_col].astype(str) if c in tmt_raw.columns]
    ctrl_ch = [c for c in sc_meta.loc[sc_meta[dis_col] == "Control", ch_col].astype(str) if c in tmt_raw.columns]
    raw_idx = tmt_raw.set_index(resolve_col(tmt_raw, "Protein|Uniprot"))
    anova_idx = tmt_anova.set_index(id_tmt).reindex(raw_idx.index)
    raw_diff = (
        np.log2(raw_idx[sals_ch].apply(pd.to_numeric, errors="coerce").where(lambda x: x > 0)).mean(axis=1)
        - np.log2(raw_idx[ctrl_ch].apply(pd.to_numeric, errors="coerce").where(lambda x: x > 0)).mean(axis=1)
    )
    valid_m = raw_diff.notna() & pd.to_numeric(anova_idx[d_tmt], errors="coerce").notna()
    tmt_sign_corr = float(spearmanr(raw_diff[valid_m], pd.to_numeric(anova_idx.loc[valid_m, d_tmt]))[0])
    assert tmt_sign_corr > 0.50, f"Unexpected sign inversion in TMT Sporadic-Control: rho={tmt_sign_corr}"
    chit1_tmt = float(tmt_anova.loc[match_prot(tmt_anova[id_tmt], "CHIT1", "Q13231"), d_tmt].iloc[0])
    chit1_dia = float(dia_anova.loc[match_prot(dia_anova[id_dia], "CHIT1", "Q13231"), d_dia_sals].iloc[0])
    assert chit1_tmt > 0.5 and chit1_dia > 0.5, f"Positive-control CHIT1 sign check failed: {chit1_tmt}, {chit1_dia}"

    res: dict[str, object] = {}
    for sym, uni in TARGETS.items():
        entry: dict[str, object] = {"uniprot": uni}
        rt = tmt_anova[match_prot(tmt_anova[id_tmt], sym, uni)]
        entry["tmt_set1_detected"] = len(rt) > 0
        if len(rt) > 0:
            r0 = rt.iloc[0]
            entry["tmt_set1"] = {
                "protein_id": str(r0[id_tmt]),
                "anova_F": float(r0[resolve_col(tmt_anova, "F-Value")]),
                "anova_p": float(r0[resolve_col(tmt_anova, "Pr(>F)")]),
                "sals_vs_ctrl_log2diff": float(r0[d_tmt]),
                "sals_vs_ctrl_p": float(r0[p_tmt]),
            }
        rd = dia_anova[match_prot(dia_anova[id_dia], sym, uni)]
        entry["dia_set2_detected"] = len(rd) > 0
        if len(rd) > 0:
            r0 = rd.iloc[0]
            entry["dia_set2"] = {
                "protein_id": str(r0[id_dia]),
                "sals_vs_ctrl_log2diff": float(r0[d_dia_sals]),
                "sals_vs_ctrl_p": float(r0[p_dia_sals]),
                "als_vs_ctrl_log2diff": float(r0[d_dia_als]),
                "als_vs_ctrl_p": float(r0[p_dia_als]),
                "c9_vs_ctrl_log2diff": float(r0[d_dia_c9]),
                "c9_vs_ctrl_p": float(r0[p_dia_c9]),
            }
        rp = pep_anova[match_prot(pep_anova[id_pep], sym, uni)]
        entry["tmt_peptide_count"] = int(len(rp))
        if len(rp) > 0:
            entry["tmt_peptide_median_sals_ctrl_p"] = float(rp[resolve_col(pep_anova, "Sporadic-Control")].median())
        rw = wgcna[match_prot(wgcna[id_wgcna], sym, uni)]
        if len(rw) > 0:
            w0 = rw.iloc[0]
            mcol = str(w0[mod_col])
            kcol = f"kME{mcol}"
            mod_sub = wgcna[wgcna[mod_col] == mcol].copy()
            kme_val = float(w0[kcol]) if kcol in wgcna.columns else None
            rank = int((mod_sub[kcol] > kme_val).sum() + 1) if kme_val is not None else None
            entry["wgcna"] = {"module": mcol, "kME": kme_val, "rank_in_module": rank, "module_size": int(len(mod_sub))}
        # Donor-level raw TMT OLS + elapsed duration check
        rraw = tmt_raw[match_prot(tmt_raw[resolve_col(tmt_raw, "Protein|Uniprot")], sym, uni)]
        if len(rraw) > 0:
            ch_col = resolve_col(sc_meta, "Channel")
            dis_col = resolve_col(sc_meta, "Disease")
            age_col = resolve_col(sc_meta, "AgeAtSample")
            ons_col = resolve_col(sc_meta, "AgeOnset")
            sex_col = resolve_col(sc_meta, "Sex")
            valid_ch = [c for c in sc_meta[ch_col].astype(str) if c in rraw.columns]
            vals = pd.to_numeric(rraw.iloc[0][valid_ch], errors="coerce")
            mdf = sc_meta.set_index(sc_meta[ch_col].astype(str)).loc[valid_ch].copy()
            mdf["log2_int"] = np.log2(vals.where(vals > 0))
            mdf["age"] = pd.to_numeric(mdf[age_col], errors="coerce")
            mdf["onset"] = pd.to_numeric(mdf[ons_col], errors="coerce")
            mdf["elapsed_yr"] = mdf["age"] - mdf["onset"]
            mdf["is_female"] = (mdf[sex_col].astype(str).str.upper().str.startswith("F")).astype(float)
            sc_sub = mdf[mdf[dis_col].isin(["Sporadic", "Control"])].dropna(subset=["log2_int", "age"]).copy()
            sc_sub["is_sals"] = (sc_sub[dis_col] == "Sporadic").astype(float)
            b_dummies = pd.get_dummies(sc_sub[resolve_col(sc_meta, "Batch")].astype(str), prefix="b", drop_first=True, dtype=float)
            X_ols = sm.add_constant(pd.concat([sc_sub[["is_sals", "age", "is_female"]], b_dummies], axis=1))
            ols = sm.OLS(sc_sub["log2_int"], X_ols).fit()
            sals_only = mdf[mdf[dis_col] == "Sporadic"].dropna(subset=["log2_int", "elapsed_yr"])
            rho, p_rho = spearmanr(sals_only["log2_int"], sals_only["elapsed_yr"]) if len(sals_only) >= 5 else (np.nan, np.nan)
            entry["donor_tmt_ols"] = {
                "n_sals": int((sc_sub["is_sals"] == 1).sum()), "n_ctrl": int((sc_sub["is_sals"] == 0).sum()),
                "batch_age_sex_adj_log2fc": float(ols.params["is_sals"]), "batch_age_sex_adj_p": float(ols.pvalues["is_sals"]),
                "sals_elapsed_yr_spearman_r": float(rho), "sals_elapsed_yr_p": float(p_rho), "n_sals_elapsed": int(len(sals_only)),
            }
        res[sym] = entry
    res["_contrast_verification"] = {
        "tmt_algebraic_max_err": tmt_alg_err,
        "dia_algebraic_max_err": dia_alg_err,
        "tmt_raw_vs_post_tampor_spearman_r": tmt_sign_corr,
        "chit1_pos_ctrl_tmt_log2diff": chit1_tmt,
        "chit1_pos_ctrl_dia_log2diff": chit1_dia,
    }
    return res


def analyze_ds029() -> dict[str, object]:
    p29 = resolve_dataset_path("DS029_SPILL")
    m1 = pd.read_excel(p29 / "401_2026_3084_MOESM1_ESM.xlsx")
    m2_hom = pd.read_excel(p29 / "401_2026_3084_MOESM2_ESM.xlsx", sheet_name="Homogenate", skiprows=1, index_col=0)
    m2_syn = pd.read_excel(p29 / "401_2026_3084_MOESM2_ESM.xlsx", sheet_name="Synaptosome", skiprows=1, index_col=0)
    m3 = pd.read_excel(p29 / "401_2026_3084_MOESM3_ESM.xlsx")

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

    genes_out: dict[str, object] = {}
    gcol1 = resolve_col(m1, "Gene")
    gcol3 = resolve_col(m3, "Gene")
    for sym, uni in TARGETS.items():
        if sym == "GDI2":
            continue
        rec: dict[str, object] = {}
        r1 = m1[m1[gcol1].fillna("").astype(str).str.split(";").apply(lambda x: sym in x) | m1[resolve_col(m1, "Accession")].fillna("").astype(str).str.contains(uni)]
        rec["frctx_proteomics_detected"] = len(r1) > 0
        if len(r1) > 0:
            row = r1.iloc[0]
            sc_v = pd.to_numeric(row[syn_ctl_cols], errors="coerce").dropna()
            s9_v = pd.to_numeric(row[syn_c9_cols], errors="coerce").dropna()
            hc_v = pd.to_numeric(row[hom_ctl_cols], errors="coerce").dropna()
            h9_v = pd.to_numeric(row[hom_c9_cols], errors="coerce").dropna()
            rec["frctx_synaptosome"] = {
                "n_c9ftd": int(len(s9_v)), "n_ctrl": int(len(sc_v)),
                "recomputed_log2fc": float(s9_v.mean() - sc_v.mean()),
                "recomputed_welch_p": float(ttest_ind(s9_v, sc_v, equal_var=False).pvalue),
                "table_log2fc": float(row[resolve_col(m1, "Log2Ratios_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")]),
                "table_p": float(row[resolve_col(m1, "pVal_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")]),
                "table_padj": float(row[resolve_col(m1, "pAdj_Synapt_FRCTX_C9FTD.Synapt_FRCTX_Control")]),
            }
            rec["frctx_homogenate"] = {
                "n_c9ftd": int(len(h9_v)), "n_ctrl": int(len(hc_v)),
                "recomputed_log2fc": float(h9_v.mean() - hc_v.mean()),
                "recomputed_welch_p": float(ttest_ind(h9_v, hc_v, equal_var=False).pvalue),
                "table_log2fc": float(row[resolve_col(m1, "Log2Ratios_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control")]),
                "table_p": float(row[resolve_col(m1, "pVal_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control")]),
                "table_padj": float(row[resolve_col(m1, "pAdj_Homogenate_FRCTX_C9FTD.Homogenate_FRCTX_Control")]),
            }
        for label, df2 in [("frctx_rnaseq_homogenate", m2_hom), ("frctx_rnaseq_synaptosome", m2_syn)]:
            gn_col = resolve_col(df2, "gene_name")
            r2 = df2[df2[gn_col].astype(str) == sym]
            if len(r2) > 0:
                rw2 = r2.iloc[0]
                rec[label] = {
                    "baseMean": float(rw2[resolve_col(df2, "baseMean")]),
                    "log2FC": float(rw2[resolve_col(df2, "log2FoldChange")]),
                    "p": float(rw2[resolve_col(df2, "pvalue")]),
                    "padj": float(rw2[resolve_col(df2, "padj")]),
                }
        r3 = m3[m3[gcol3].fillna("").astype(str).str.split(";").apply(lambda x: sym in x)]
        if len(r3) > 0:
            rw3 = r3.iloc[0]
            rec["ipsc_neuron_proteomics"] = {
                "homogenate_log2fc": float(rw3[resolve_col(m3, "Log2FC_HOxC9FTD.HOxCTRL")]),
                "homogenate_p": float(rw3[resolve_col(m3, "pVal_HOxC9FTD.HOxCTRL")]),
                "homogenate_padj": float(rw3[resolve_col(m3, "pAdj_HOxC9FTD.HOxCTRL")]),
                "pellet_log2fc": float(rw3[resolve_col(m3, "Log2FC_PxC9FTD.PxCTRL")]),
                "pellet_p": float(rw3[resolve_col(m3, "pVal_PxC9FTD.PxCTRL")]),
                "pellet_padj": float(rw3[resolve_col(m3, "pAdj_PxC9FTD.PxCTRL")]),
            }
        genes_out[sym] = rec

    # MOESM5 Sheet 3: CE abundance in FCx H0 (STMN2, KALRN, UNC13A junctions)
    ce_raw = pd.read_excel(p29 / "401_2026_3084_MOESM5_ESM.xlsx", sheet_name="3 - CE Abundance in FCx H0")
    top_hdr = ce_raw.iloc[0].ffill().fillna("")
    sub_hdr = ce_raw.iloc[1].fillna("")
    comp_cols = [f"{str(t).split()[0]}_{str(s).strip()}" if str(t) and "JUNCTIONS" in str(t) else str(s).strip() for t, s in zip(top_hdr, sub_hdr)]
    ce_df = ce_raw.iloc[2:].copy()
    ce_df.columns = comp_cols
    sid_col = resolve_col(ce_df, "Study ID")
    ce_df = ce_df.dropna(subset=[sid_col]).copy()
    ce_df["is_c9"] = ~ce_df[sid_col].astype(str).str.upper().str.startswith("CTRL")
    ce_summary: dict[str, object] = {}
    for g in ["STMN2", "UNC13A", "KALRN"]:
        can_c = resolve_col(ce_df, f"{g}_Canonical")
        ce_c = resolve_col(ce_df, f"{g}_CE")
        ce_df[can_c] = pd.to_numeric(ce_df[can_c], errors="coerce").fillna(0.0)
        ce_df[ce_c] = pd.to_numeric(ce_df[ce_c], errors="coerce").fillna(0.0)
        ce_df[f"{g}_psi"] = np.where((ce_df[can_c] + ce_df[ce_c]) > 0, ce_df[ce_c] / (ce_df[can_c] + ce_df[ce_c]), 0.0)
        c9_s = ce_df[ce_df["is_c9"]]
        ct_s = ce_df[~ce_df["is_c9"]]
        c9_det = int((c9_s[ce_c] > 0).sum())
        ct_det = int((ct_s[ce_c] > 0).sum())
        _, p_fish = fisher_exact([[c9_det, len(c9_s) - c9_det], [ct_det, len(ct_s) - ct_det]])
        _, p_mwu = mannwhitneyu(c9_s[f"{g}_psi"], ct_s[f"{g}_psi"], alternative="two-sided")
        ce_summary[g] = {
            "n_c9ftd": int(len(c9_s)), "n_ctrl": int(len(ct_s)),
            "c9ftd_ce_detected": c9_det, "ctrl_ce_detected": ct_det,
            "fisher_p": float(p_fish), "psi_mwu_p": float(p_mwu),
            "c9ftd_mean_psi": float(c9_s[f"{g}_psi"].mean()), "ctrl_mean_psi": float(ct_s[f"{g}_psi"].mean()),
            "c9ftd_total_ce_reads": int(c9_s[ce_c].sum()), "ctrl_total_ce_reads": int(ct_s[ce_c].sum()),
        }
    return {
        "contrast_verification": {"synaptosome_max_err": syn_err, "homogenate_max_err": hom_err},
        "genes": genes_out,
        "fcx_cryptic_exon_junctions_moesm5": ce_summary,
    }


if __name__ == "__main__":
    payload = {
        "analysis_run_id": "RUN-B1-004",
        "ds045_trautwig2025_csf_proteomics": analyze_ds045(),
        "ds029_spillman2026_frctx_synaptosome_multiomics": analyze_ds029(),
    }
    out_file = OUT_DIR / "run_b1_004_proteomics.json"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_file}")
