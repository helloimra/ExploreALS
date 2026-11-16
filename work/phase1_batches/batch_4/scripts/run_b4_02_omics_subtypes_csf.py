"""RUN-B4-002: Donor-level O'Neill 2025 NYGC JAK-STAT/subtype audit, Trautwig 2025 CSF, and APA/Cryptic check."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase1_batches.batch_runner_utils import (
    assert_contrast_pair,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_4" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_SYMBOLS = [
    "JAK1", "JAK2", "JAK3", "TYK2", "STAT1", "STAT3", "IRF1", "CCL2", "CXCL10",
    "AAK1", "CHIT1", "CHI3L1", "CHI3L2", "GPNMB", "CD48", "IL1R2", "GDI2",
    "PIKFYVE", "PPP1R15A", "PPP1R15B", "SIGMAR1", "GRIN2B", "HTR2A", "SCN8A",
]


def load_nygc_log2cpm_subset(symbols: list[str]) -> tuple[pd.DataFrame, dict[str, str]]:
    feat = pd.read_csv(resolve_dataset_path("DS001_FEAT", verify_hash=True))
    sym_col = resolve_col(feat, "ucsd_label")
    ens_col = resolve_col(feat, "nygc_exact_versioned_ids")
    sub = feat.loc[feat[sym_col].isin(symbols) & feat[ens_col].notna()].copy()
    ens_to_sym = {}
    for _, r in sub.iterrows():
        eids = str(r[ens_col]).split(";")
        if len(eids) == 1 and eids[0]:
            ens_to_sym[eids[0]] = str(r[sym_col])

    p_counts = resolve_dataset_path("DS001_COUNTS", verify_hash=True)
    lib_sizes = None
    target_counts: dict[str, np.ndarray] = {}
    with gzip.open(p_counts, "rt", encoding="utf-8") as fh:
        headers = fh.readline().rstrip("\n").split("\t")
        assert headers[0] == "EnsemblID"
        sample_names = headers[1:]
        lib_sizes = np.zeros(len(sample_names), dtype=np.float64)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            # R write.table format: parts[0]=row_idx, parts[1]=EnsemblID, parts[2:]=counts
            assert len(parts) == len(headers) + 1
            ens_id = parts[1]
            arr = np.fromiter((float(x) for x in parts[2:]), dtype=np.float64, count=len(sample_names))
            lib_sizes += arr
            if ens_id in ens_to_sym:
                target_counts[ens_to_sym[ens_id]] = arr

    cpm_dict = {}
    for sym, arr in target_counts.items():
        cpm = (arr / np.maximum(lib_sizes, 1.0)) * 1e6
        cpm_dict[sym] = np.log2(cpm + 1.0)
    df_log2cpm = pd.DataFrame(cpm_dict, index=sample_names)
    return df_log2cpm, ens_to_sym


def analyze_oneill_nygc(df_log2cpm: pd.DataFrame) -> dict:
    p_on = resolve_dataset_path("DS001_ONEILL", verify_hash=True)
    out = {}
    for label, sheet, glia_tag in [
        ("cortex", "TableS1B", "ALS-Glia"),
        ("spinal_cord", "TableS1G", "ALS-Glia-cord"),
    ]:
        meta = read_xlsx_sparse_safe(p_on, sheet, header_row_1based=2)
        scol = resolve_col(meta, "Sample")
        pcol = resolve_col(meta, "Patient ID")
        gcol = resolve_col(meta, "Group")
        subcol = resolve_col(meta, "ALS Subtype")

        meta = meta.loc[meta[scol].astype(str).isin(df_log2cpm.index)].copy()
        meta["sample_id"] = meta[scol].astype(str)
        meta["donor_id"] = meta[pcol].astype(str)
        meta["group_clean"] = np.where(
            meta[gcol].astype(str).str.upper().isin(["CTL", "CONTROL"]),
            "Control",
            meta[subcol].astype(str),
        )

        joined = meta[["sample_id", "donor_id", "group_clean"]].merge(
            df_log2cpm, left_on="sample_id", right_index=True, how="inner"
        )
        # Aggregate strictly to donor level (mean across regions/replicates per donor within stratum)
        donor_df = joined.groupby(["donor_id", "group_clean"], as_index=False)[list(df_log2cpm.columns)].mean()
        counts_by_stratum = donor_df["group_clean"].value_counts().to_dict()

        jak_genes = [g for g in ["JAK1", "JAK2", "STAT1", "STAT3", "IRF1", "CCL2", "CXCL10"] if g in donor_df.columns]
        z_mat = donor_df[jak_genes].apply(lambda s: (s - s.mean()) / (s.std(ddof=1) or 1.0))
        donor_df["JAK_STAT_7gene_z"] = z_mat.mean(axis=1)

        test_cols = ["JAK_STAT_7gene_z"] + [
            g for g in ["JAK1", "JAK2", "STAT1", "STAT3", "CCL2", "AAK1", "CHIT1", "GPNMB", "CHI3L1", "PIKFYVE", "PPP1R15A"]
            if g in donor_df.columns
        ]
        contrasts = [("ALS_Glia_vs_Control", glia_tag, "Control")]
        if label == "cortex":
            contrasts.append(("ALS_TE_vs_Control", "ALS-TE", "Control"))
            contrasts.append(("ALS_Glia_vs_ALS_Ox", "ALS-Glia", "ALS-Ox"))
            contrasts.append(("ALS_Glia_vs_ALS_TE", "ALS-Glia", "ALS-TE"))
        else:
            contrasts.append(("ALS_Glia_cord_vs_ALS_Ox_cord", "ALS-Glia-cord", "ALS-Ox-cord"))

        res_list = []
        for cname, g1, g2 in contrasts:
            d1 = donor_df.loc[donor_df["group_clean"] == g1]
            d2 = donor_df.loc[donor_df["group_clean"] == g2]
            if len(d1) < 3 or len(d2) < 3:
                continue
            for feat_name in test_cols:
                x1 = d1[feat_name].dropna().to_numpy()
                x2 = d2[feat_name].dropna().to_numpy()
                t_val, p_val = stats.ttest_ind(x1, x2, equal_var=False)
                u_val, p_mwu = stats.mannwhitneyu(x1, x2, alternative="two-sided")
                res_list.append({
                    "region": label,
                    "contrast": cname,
                    "feature": feat_name,
                    "n_group1": int(len(x1)),
                    "n_group2": int(len(x2)),
                    "mean_diff_log2cpm_or_z": float(np.mean(x1) - np.mean(x2)),
                    "welch_t": float(t_val),
                    "welch_p": float(p_val),
                    "mwu_p": float(p_mwu),
                })
        out[label] = {
            "n_samples_matched": int(len(joined)),
            "donor_counts_by_stratum": counts_by_stratum,
            "contrasts": res_list,
        }
    return out


def analyze_trautwig_csf() -> dict:
    p_tr = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    tmt = read_xlsx_sparse_safe(p_tr, "6-TMT-MS ANOVA", header_row_1based=2)
    dia = read_xlsx_sparse_safe(p_tr, "8-DIA ANOVA", header_row_1based=2)
    wgcna = read_xlsx_sparse_safe(p_tr, "9-WGCNA kME", header_row_1based=2)
    coh1 = read_xlsx_sparse_safe(p_tr, "1-Cohort-SC Characteristics", header_row_1based=2)
    coh2 = read_xlsx_sparse_safe(p_tr, "2-Cohort-Exp Characteristics", header_row_1based=2)

    # Assert paired contrast headers match exact same group comparison
    tmt_p_sals = resolve_col(tmt, "Sporadic-Control")
    tmt_d_sals = resolve_col(tmt, "diff Sporadic-Control")
    tmt_p_c9 = resolve_col(tmt, "Control-ALS.C9")
    tmt_d_c9 = resolve_col(tmt, "diff Control-ALS.C9_inv")
    assert "Sporadic-Control" in tmt_p_sals and "Sporadic-Control" in tmt_d_sals

    dia_p_sals = resolve_col(dia, "sALS-Control")
    dia_d_sals = resolve_col(dia, "diff sALS-Control")
    dia_p_als = resolve_col(dia, "ALS-Control")
    dia_d_als = resolve_col(dia, "diff ALS-Control")
    dia_p_c9 = resolve_col(dia, "C9orf72-Control")
    dia_d_c9 = resolve_col(dia, "diff C9orf72-Control")
    assert dia_d_sals == f"diff {dia_p_sals}" and dia_d_als == f"diff {dia_p_als}"

    pid_tmt = resolve_col(tmt, "Protein|Uniprot")
    pid_dia = resolve_col(dia, "Protein|Uniprot")
    uid_w = resolve_col(wgcna, "UniqueID")
    mod_w = resolve_col(wgcna, "net$colors")

    csf_markers = [
        "CHIT1", "CHI3L1", "CHI3L2", "GPNMB", "CD48", "IL1R2", "CCL2",
        "C1QA", "C3", "GDI2", "NEFL", "NEFH", "STMN2", "JAK1", "STAT1", "STAT3", "AAK1", "PIKFYVE",
    ]
    hits = {}
    for sym in csf_markers:
        rt = tmt.loc[tmt[pid_tmt].astype(str).str.split("|").str[0] == sym]
        rd = dia.loc[dia[pid_dia].astype(str).str.split("|").str[0] == sym]
        rw = wgcna.loc[wgcna[uid_w].astype(str).str.split("|").str[0] == sym]
        if rt.empty and rd.empty:
            continue
        hits[sym] = {
            "tmt_n101": [
                {
                    "protein_id": str(r[pid_tmt]),
                    "sals_vs_ctrl_diff_log2": float(r[tmt_d_sals]),
                    "sals_vs_ctrl_p": float(r[tmt_p_sals]),
                    "c9_vs_ctrl_diff_log2": float(r[tmt_d_c9]),
                    "c9_vs_ctrl_p": float(r[tmt_p_c9]),
                }
                for _, r in rt.iterrows()
            ],
            "dia_n259": [
                {
                    "protein_id": str(r[pid_dia]),
                    "sals_vs_ctrl_diff_log2": float(r[dia_d_sals]),
                    "sals_vs_ctrl_p": float(r[dia_p_sals]),
                    "als_vs_ctrl_diff_log2": float(r[dia_d_als]),
                    "als_vs_ctrl_p": float(r[dia_p_als]),
                    "c9_vs_ctrl_diff_log2": float(r[dia_d_c9]),
                    "c9_vs_ctrl_p": float(r[dia_p_c9]),
                }
                for _, r in rd.iterrows()
            ],
            "wgcna_module": [str(r[mod_w]) for _, r in rw.iterrows()],
        }
    dis_c1 = resolve_col(coh1, "Disease")
    sym_c2 = resolve_col(coh2, "SymptomStatus")
    return {
        "tmt_cohort_counts": coh1[dis_c1].dropna().value_counts().to_dict(),
        "dia_cohort_counts": coh2[sym_c2].dropna().value_counts().to_dict(),
        "csf_marker_results": hits,
    }


def analyze_apa_and_cryptic() -> dict:
    p_z = resolve_dataset_path("DS_ZENG_APA", verify_hash=True)
    s2 = read_xlsx_sparse_safe(p_z, "S2", header_row_1based=1)
    s4 = read_xlsx_sparse_safe(p_z, "S4", header_row_1based=1)
    g2 = resolve_col(s2, "gene_name")
    dp2 = resolve_col(s2, "delta_PUI")
    q2 = resolve_col(s2, "padj")
    dir2 = resolve_col(s2, "APA_direction")

    g4 = resolve_col(s4, "gene_name")
    dp4 = resolve_col(s4, "Delta_distal_PAS_usage")
    q4 = resolve_col(s4, "padj")
    dir4 = resolve_col(s4, "APA_direction")

    apa_hits = {}
    for sym in TARGET_SYMBOLS:
        r2 = s2.loc[s2[g2].astype(str).str.upper() == sym]
        r4 = s4.loc[s4[g4].astype(str).str.upper() == sym]
        if not r2.empty or not r4.empty:
            apa_hits[sym] = {
                "rnaseq_S2": [
                    {"delta_PUI": float(x[dp2]), "padj": float(x[q2]), "direction": str(x[dir2])}
                    for _, x in r2.iterrows()
                ],
                "3endseq_S4": [
                    {"delta_distal_PAS": float(x[dp4]), "padj": float(x[q4]), "direction": str(x[dir4])}
                    for _, x in r4.iterrows()
                ],
            }

    p_cr = resolve_dataset_path("DS_CRYPTIC", verify_hash=False)
    brown11 = pd.read_csv(p_cr / "Brown2022_41586_2022_4436_MOESM11_ESM.csv")
    gb = resolve_col(brown11, "gene_name")
    dpsib = resolve_col(brown11, "deltaPSI")
    fdrb = resolve_col(brown11, "FDR")
    crypb = resolve_col(brown11, "cryptic_junction")
    sub_b = brown11.loc[brown11[gb].astype(str).str.upper().isin(TARGET_SYMBOLS)].copy()

    ma5 = read_xlsx_sparse_safe(p_cr / "Ma2022_41586_2022_4424_MOESM5_ESM.xlsx", "Sheet1", header_row_1based=1)
    gm = resolve_col(ma5, "Genes")
    sub_m = ma5.loc[ma5[gm].astype(str).str.upper().isin(TARGET_SYMBOLS)].copy()

    return {
        "zeng2025_apa_hits": apa_hits,
        "brown2022_splicing_hits": sub_b[[gb, dpsib, fdrb, crypb]].to_dict(orient="records"),
        "ma2022_splicing_hits": sub_m.to_dict(orient="records"),
    }


def main() -> None:
    df_log2cpm, ens_map = load_nygc_log2cpm_subset(TARGET_SYMBOLS)
    oneill_res = analyze_oneill_nygc(df_log2cpm)
    csf_res = analyze_trautwig_csf()
    apa_cryptic_res = analyze_apa_and_cryptic()

    payload = {
        "nygc_feature_map": ens_map,
        "oneill2025_nygc_donor_models": oneill_res,
        "trautwig2025_csf": csf_res,
        "zeng2025_apa_and_cryptic": apa_cryptic_res,
    }
    (OUT_DIR / "batch4_omics_subtypes_csf.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    for reg in ("cortex", "spinal_cord"):
        df_c = pd.DataFrame(oneill_res[reg]["contrasts"])
        print(f"=== O'Neill NYGC {reg} ({oneill_res[reg]['donor_counts_by_stratum']}) ===")
        print(df_c.loc[df_c["feature"].isin(["JAK_STAT_7gene_z", "JAK1", "JAK2", "STAT3", "CCL2", "AAK1", "CHIT1", "GPNMB"])].to_string(index=False))
    print("CSF markers found:", list(csf_res["csf_marker_results"].keys()))
    print("Zeng APA hits:", json.dumps(apa_cryptic_res["zeng2025_apa_hits"], indent=2))
    print("Brown/Ma cryptic hits count:", len(apa_cryptic_res["brown2022_splicing_hits"]), len(apa_cryptic_res["ma2022_splicing_hits"]))


if __name__ == "__main__":
    main()
