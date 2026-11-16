"""RUN-B1-001: Primary reanalysis of TDP-43 cryptic splicing, Ribo-seq & APA for Batch 1."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.phase1_batches.batch_runner_utils import (
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_1" / "outputs"
GENES = ["UNC13A", "STMN2", "KCNQ2", "CHMP7", "CHMP2B", "VPS4B"]


def analyze_brown2022(cdir: Path) -> dict[str, object]:
    res: dict[str, object] = {}
    junc = pd.read_csv(cdir / "Brown2022_41586_2022_4436_MOESM11_ESM.csv")
    gcol = resolve_col(junc, "gene_name")
    dpsi_col = resolve_col(junc, "deltaPSI")
    fdr_col = resolve_col(junc, "FDR")
    igv_col = resolve_col(junc, "paste_into_igv_junction")
    cry_col = resolve_col(junc, "cryptic_junction")
    cpsi_col = resolve_col(junc, "control_e_psi")
    kpsi_col = resolve_col(junc, "tdp_kd_e_psi")

    by_gene = {}
    for g in GENES:
        sub = junc[junc[gcol] == g].copy()
        if not sub.empty:
            sub["abs_dpsi"] = sub[dpsi_col].abs()
            sub = sub.sort_values("abs_dpsi", ascending=False)
            by_gene[g] = sub[[gcol, igv_col, cpsi_col, kpsi_col, dpsi_col, fdr_col, cry_col]].to_dict("records")
        else:
            by_gene[g] = []
    res["i3neuron_splicing_MOESM11"] = by_gene

    rna = pd.read_csv(cdir / "Brown2022_41586_2022_4436_MOESM12_ESM.csv")
    rg, rlfc, rpadj, rbm = (
        resolve_col(rna, "gene_name"),
        resolve_col(rna, "log2FoldChange"),
        resolve_col(rna, "padj"),
        resolve_col(rna, "baseMean"),
    )
    res["i3neuron_rnaseq_MOESM12"] = (
        rna[rna[rg].isin(GENES)][[rg, rbm, rlfc, rpadj]].to_dict("records")
    )

    ribo = pd.read_csv(cdir / "Brown2022_41586_2022_4436_MOESM13_ESM.csv")
    bg, blfc, bpadj, bbm = (
        resolve_col(ribo, "gene_name"),
        resolve_col(ribo, "log2FoldChange"),
        resolve_col(ribo, "padj"),
        resolve_col(ribo, "baseMean"),
    )
    res["i3neuron_riboseq_MOESM13"] = (
        ribo[ribo[bg].isin(GENES)][[bg, bbm, blfc, bpadj]].to_dict("records")
    )

    rl_df = pd.read_excel(cdir / "Brown2022_41586_2022_4436_MOESM6_ESM.xls")
    res["read_length_raw_MOESM6"] = rl_df.to_dict("records")
    d_col = resolve_col(rl_df, "Disease group")
    t_col = resolve_col(rl_df, "tissue")
    h_un = resolve_col(rl_df, "Undetected HiSeq")
    h_det = resolve_col(rl_df, "N  Detected")
    n_det = resolve_col(rl_df, "Detected NovaSeq")
    other_cols = [c for c in rl_df.columns if c not in {d_col, t_col, h_un, h_det, n_det} and "fisher" not in c.lower()]
    n_un = other_cols[0]
    rl_clean = rl_df.copy()
    rl_clean[d_col] = rl_clean[d_col].ffill()
    recomputed_rl = []
    for _, row in rl_clean.dropna(subset=[t_col, h_det, h_un, n_det, n_un]).iterrows():
        hd, hu = int(row[h_det]), int(row[h_un])
        nd, nu = int(row[n_det]), int(row[n_un])
        odds, p_two = fisher_exact([[hd, hu], [nd, nu]], alternative="two-sided")
        recomputed_rl.append({
            "disease_group": str(row[d_col]),
            "tissue": str(row[t_col]),
            "hiseq_125bp_detected": hd,
            "hiseq_125bp_total": hd + hu,
            "hiseq_125bp_pct": round(100.0 * hd / (hd + hu), 2) if (hd + hu) else None,
            "novaseq_100bp_detected": nd,
            "novaseq_100bp_total": nd + nu,
            "novaseq_100bp_pct": round(100.0 * nd / (nd + nu), 2) if (nd + nu) else None,
            "fisher_odds_ratio": float(odds),
            "fisher_p_recomputed": float(p_two),
        })
    res["read_length_fisher_recomputed"] = recomputed_rl

    snp_df = pd.read_excel(cdir / "Brown2022_41586_2022_4436_MOESM7_ESM.xls")
    res["unc13a_patient_snp_psi_MOESM7"] = snp_df.to_dict("records")
    return res


def read_sheet_safe(xlsx_path: Path, sheet_name: str, header_row_1based: int = 1) -> pd.DataFrame:
    try:
        return read_xlsx_sparse_safe(xlsx_path, sheet_name, header_row_1based)
    except ValueError:
        return pd.read_excel(xlsx_path, sheet_name=sheet_name, header=header_row_1based - 1, engine="openpyxl")


def analyze_ma_melamed_bryce_zeng(cdir: Path) -> dict[str, object]:
    out: dict[str, object] = {}
    ma5 = read_sheet_safe(cdir / "Ma2022_41586_2022_4424_MOESM5_ESM.xlsx", "Sheet1", 1)
    mg = resolve_col(ma5, "Genes")
    out["ma2022_spliced_MOESM5"] = ma5[ma5[mg].isin(GENES)].to_dict("records")

    ma6 = read_sheet_safe(cdir / "Ma2022_41586_2022_4424_MOESM6_ESM.xlsx", "Sheet1", 1)
    out["ma2022_nygc_detection_MOESM6"] = ma6.dropna(how="all").to_dict("records")

    klim = read_sheet_safe(cdir / "Klim2019_41593_2018_300_MOESM3_ESM.xlsx", "STMN2 KO HUES3 Hb9GFP", 1)
    kdist = resolve_col(klim, "distance from soma")
    kwtr = resolve_col(klim, "aver. WT ROCK")
    kkor = resolve_col(klim, "aver. KO ROCK")
    kpval = resolve_col(klim, "p-values WT vs. KO with ROCK")
    out["klim2019_stmn2_ko_sholl_summary"] = {
        "n_radii_tested": int(klim[kpval].notna().sum()),
        "min_p_wt_vs_ko_rock": float(pd.to_numeric(klim[kpval], errors="coerce").min()),
        "peak_wt_intersections": float(pd.to_numeric(klim[kwtr], errors="coerce").max()),
        "peak_ko_intersections": float(pd.to_numeric(klim[kkor], errors="coerce").max()),
        "sample_rows": klim[[kdist, kwtr, kkor, kpval]].dropna().head(6).to_dict("records"),
    }

    mel3 = read_sheet_safe(cdir / "Melamed2019_41593_2018_293_MOESM3_ESM.xlsx", "diff.ShySy.DESeq2(1)", 3)
    melg = resolve_col(mel3, "GENE")
    out["melamed2019_siTDP43_MOESM3"] = mel3[mel3[melg].astype(str).str.contains("|".join(GENES), na=False)].to_dict("records")

    mel4 = read_sheet_safe(cdir / "Melamed2019_41593_2018_293_MOESM4_ESM.xlsx", "Supplementary Table1_Gene expre", 3)
    mel4g = resolve_col(mel4, "GENE")
    out["melamed2019_N352S_MOESM4"] = mel4[mel4[mel4g].astype(str).str.contains("|".join(GENES), na=False)].to_dict("records")

    bpath = resolve_dataset_path("DS_BRYCE_APA")
    for st in ["Supplementary_Table_2", "Supplementary_Table_3", "Supplementary_Table_5", "Supplementary_Table_6"]:
        bdf = read_sheet_safe(bpath, st, 1)
        bg = resolve_col(bdf, "gene_name")
        out[f"brycesmith2025_{st}"] = bdf[bdf[bg].isin(GENES)].to_dict("records")

    zpath = resolve_dataset_path("DS_ZENG_APA")
    for st, g_alias in [("S1", "Gene_Name"), ("S2", "gene_name"), ("S3", "gene_name"), ("S4", "gene_name"), ("S5", "gene"), ("S6", "gene_name")]:
        zdf = read_sheet_safe(zpath, st, 1)
        zg = resolve_col(zdf, g_alias)
        out[f"zeng2025_{st}"] = zdf[zdf[zg].isin(GENES)].to_dict("records")
    return out


if __name__ == "__main__":
    cdir = resolve_dataset_path("DS_CRYPTIC")
    payload = {
        "analysis_run_id": "RUN-B1-001",
        "brown2022": analyze_brown2022(cdir),
        "other_splicing_apa": analyze_ma_melamed_bryce_zeng(cdir),
    }
    out_file = OUT_DIR / "run_b1_001_splicing_apa.json"
    out_file.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_file}")
