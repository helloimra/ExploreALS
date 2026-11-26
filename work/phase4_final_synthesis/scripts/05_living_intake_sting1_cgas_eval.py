"""Step 1 deterministic evaluation of STING1 vs CGAS/IFI16/PSMB8 across 7 human ALS cohorts, 5 mmCIFs, and gene-liability."""
from __future__ import annotations

import gzip
import importlib.util
import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (ROOT, SRC, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _cgas_checkpoint25_addendum import (  # noqa: E402
    compute_cgas_ortholog_6mjw_alignment,
    compute_nygc_genotype_stratified_cgas,
    compute_staged_apa_audit,
)
from _sting1_cgas_mmcif_and_priors import analyze_staged_mmcif_structures  # noqa: E402
from _sting1_cgas_priors import build_verified_external_priors  # noqa: E402
from carbon_als.loaders import (  # noqa: E402
    assert_modality,
    assert_unique_donors,
    load_brown2022_splicing,
    load_edinburgh_pseudobulk,
    load_pineda2024_pseudobulk,
    load_spillman2026_fractions,
    load_zhang2026_spatial,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

T3_SCRIPT = ROOT / "work" / "phase2" / "track3_subtype_precision_translation" / "scripts" / "06_c019_s09_jak_tyk2_receptor_and_csf_cxcl10.py"
CACHE_FP = ROOT / "work" / "phase4_final_synthesis" / "cache" / "living_sting1_cgas_external_priors.json"
OUT_FP = ROOT / "work" / "phase4_final_synthesis" / "outputs" / "run_p4_005_living_sting1_cgas_eval.json"
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)

NYGC_PANEL = [
    "TMEM173", "CGAS", "IFI16", "TBK1", "OPTN", "PSMB8", "PSMB9",
    "HLA-A", "HLA-B", "HLA-C", "B2M", "IFNAR1", "TYK2", "STAT1", "STAT2", "RSAD2", "ISG15",
]
SN_GENES = ["STING1", "CGAS", "IFI16", "TBK1", "OPTN", "PSMB8", "PSMB9", "HLA-A", "B2M", "IFNAR1", "TYK2", "STAT1", "ISG15"]


def _clean_nan(obj: object) -> object:
    if isinstance(obj, float) and (obj != obj):
        return None
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_nan(x) for x in obj]
    return obj


def _load_t3():
    spec = importlib.util.spec_from_file_location("_t3_mod", T3_SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_nygc_ens_gc_resolved(t3, symbols: list[str]) -> tuple[pd.DataFrame, dict[str, float]]:
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    gc_by_ens = dict(zip(gc_df[resolve_col(gc_df, "Gene stable ID")].astype(str), pd.to_numeric(gc_df[resolve_col(gc_df, "Gene % GC content")], errors="coerce")))
    feat = pd.read_csv(resolve_dataset_path("DS001_FEAT", verify_hash=True))
    sc, ec = resolve_col(feat, "ucsd_label"), resolve_col(feat, "nygc_exact_versioned_ids")
    sub = feat.loc[feat[sc].isin(set(symbols) | set(t3.CELLCOMP_GENES)) & feat[ec].notna()]
    ens_to_out: dict[str, str] = {}
    gene_gc: dict[str, float] = {}
    for _, r in sub.iterrows():
        ver_id = str(r[ec])
        if ";" in ver_id:
            continue
        out_sym = "STING1" if str(r[sc]) == "TMEM173" else str(r[sc])
        ens_to_out[ver_id] = out_sym
        base_ens = ver_id.split(".")[0]
        if base_ens in gc_by_ens and pd.notna(gc_by_ens[base_ens]):
            gene_gc[out_sym] = round(float(gc_by_ens[base_ens]), 2)
    found: dict[str, np.ndarray] = {}
    with gzip.open(resolve_dataset_path("DS001_COUNTS", verify_hash=True), "rt", encoding="utf-8") as fh:
        samples = fh.readline().rstrip("\n").split("\t")[1:]
        libs = np.zeros(len(samples), dtype=np.float64)
        hi_gc = np.zeros(len(samples), dtype=np.float64)
        lo_gc = np.zeros(len(samples), dtype=np.float64)
        for ln in fh:
            pts = ln.rstrip("\n").split("\t")
            arr = np.fromiter((float(x) for x in pts[2:]), dtype=np.float64, count=len(samples))
            libs += arr
            g_gc = gc_by_ens.get(pts[1].split(".")[0])
            if g_gc is not None and not np.isnan(g_gc):
                if g_gc >= 60.0:
                    hi_gc += arr
                elif g_gc <= 42.0:
                    lo_gc += arr
            if pts[1] in ens_to_out:
                found[ens_to_out[pts[1]]] = arr
    df = pd.DataFrame({s: np.log2((a / np.maximum(libs, 1.0)) * 1e6 + 1.0) for s, a in found.items()}, index=samples)
    df["_sample_gc_index"] = np.log2((hi_gc + 1.0) / (lo_gc + 1.0))
    return df, gene_gc


def _nygc_control_anchored(t3, expr: pd.DataFrame, gene_gc: dict[str, float], s_sheet: str, d_sheet: str, label: str) -> dict:
    p_on = resolve_dataset_path("DS001_ONEILL", verify_hash=True)
    base = t3.summarize_nygc_region(expr, gene_gc, read_xlsx_sparse_safe(p_on, s_sheet, 2), read_xlsx_sparse_safe(p_on, d_sheet, 2), label)
    samp_df, donor_df = read_xlsx_sparse_safe(p_on, s_sheet, 2), read_xlsx_sparse_safe(p_on, d_sheet, 2)
    s_mot = samp_df.loc[samp_df["Sample"].astype(str).isin(expr.index) & samp_df["Group"].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    rin_cols = [c for c in s_mot.columns if c.strip().upper() == "RIN"]
    if rin_cols:
        s_mot[rin_cols[0]] = pd.to_numeric(s_mot[rin_cols[0]], errors="coerce")
    d_mot = donor_df.loc[donor_df["Group"].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    d_map = d_mot.assign(stratum=np.where(d_mot["Group"].astype(str).str.upper().isin(["CTL", "CONTROL"]), "Control", d_mot["PatientSubtype"].astype(str)))[["PatientID", "stratum"]].drop_duplicates(subset=["PatientID"])
    don = s_mot[["Sample", "Patient ID", *rin_cols[:1]]].merge(expr, left_on="Sample", right_index=True).groupby("Patient ID", as_index=False)[[*expr.columns, *rin_cols[:1]]].mean().merge(d_map, left_on="Patient ID", right_on="PatientID", how="inner")
    assert_unique_donors(don["Patient ID"].tolist(), f"NYGC_CTRL_{label}")
    don["_neuron_idx"] = don[["RBFOX3", "SNAP25", "SLC17A7"]].mean(axis=1)
    don["_glia_idx"] = don[["AIF1", "AQP4", "MOG"]].mean(axis=1)
    covs = ["_sample_gc_index", "_neuron_idx", "_glia_idx"] + (rin_cols[:1] if rin_cols and don[rin_cols[0]].notna().sum() >= 30 else [])
    als_ct = don.loc[don["stratum"].str.startswith("ALS-") | (don["stratum"] == "Control")].copy()
    is_als = als_ct["stratum"].str.startswith("ALS-")
    for g, rec in base["genes"].items():
        rec["mean_ctrl_log2cpm"] = round(float(als_ct.loc[~is_als, g].mean()), 4)
        rec["all_als_vs_ctrl_diff"] = round(float(als_ct.loc[is_als, g].mean() - als_ct.loc[~is_als, g].mean()), 4)
        rec["all_als_vs_ctrl_welch_p"] = float(stats.ttest_ind(als_ct.loc[is_als, g], als_ct.loc[~is_als, g], equal_var=False).pvalue)
        rec["all_als_vs_ctrl_gc_cellcomp_ols"] = t3._ols_adj(als_ct, g, is_als, covs)
    return base


def main() -> None:
    t3 = _load_t3()
    priors = build_verified_external_priors()
    CACHE_FP.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FP.write_text(json.dumps(priors, indent=2, allow_nan=False), encoding="utf-8")

    gdf = pd.read_csv(resolve_dataset_path("DS_GNOMAD_V41_CONSTRAINT", verify_hash=True), sep="\t", low_memory=False)
    gsub = gdf[gdf["gene"].isin(["STING1", "CGAS", "IFI16", "TBK1", "OPTN", "PSMB8", "PSMB9", "B2M", "IFNAR1", "TYK2"]) & (gdf["mane_select"].astype(str).str.lower() == "true") & gdf["transcript"].astype(str).str.startswith("ENST")].sort_values("gene")
    gnomad_rows = gsub[["gene", "transcript", "lof.pLI", "lof.oe", "lof.oe_ci.upper", "lof.obs", "lof.exp", "mis.z_score"]].to_dict(orient="records")

    expr, gene_gc = _load_nygc_ens_gc_resolved(t3, NYGC_PANEL)
    assert gene_gc.get("STING1") == 53.56, f"Expected STING1 GC%=53.56, got {gene_gc.get('STING1')}"
    ctx = _nygc_control_anchored(t3, expr, gene_gc, "TableS1B", "TableS1C", "Cortex_STING1")
    cord = _nygc_control_anchored(t3, expr, gene_gc, "TableS1G", "TableS1H", "Spinal_STING1")

    edin = {ct: load_edinburgh_pseudobulk(ct, SN_GENES, region="donor_collapsed", min_nuclei=10)["stats"] for ct in ("Microglia", "Endothelial", "Astrocyte", "Oligodendrocyte", "Excitatory neuron")}
    pineda = {
        reg: {ct: load_pineda2024_pseudobulk(reg, ct, SN_GENES, min_nuclei=10)["stats"] for ct in ("Micro", "Endo", "Vascular", "Astro", "Oligo", "Excitatory")}
        for reg in ("BA4", "BA9")
    }
    sp = load_spillman2026_fractions(["STING1", "TMEM173", "CGAS", "IFI16", "TBK1", "OPTN", "PSMB8", "PSMB9", "HLA-A", "B2M"])
    zh = load_zhang2026_spatial(["STING1", "TMEM173", "CGAS", "IFI16", "TBK1", "OPTN", "PSMB8", "PSMB9", "HLA-A", "B2M", "APOE", "GPNMB"])
    b22 = load_brown2022_splicing(["STING1", "TMEM173", "CGAS", "IFI16", "TBK1", "PSMB8", "B2M"])

    assert_modality("PROTEOMICS_CSF_DIA", "DS045_TRAUT")
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    dia_df = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    tmt_df = read_xlsx_sparse_safe(p45, "3-TMT-MS Raw Data", 2)
    dia_syms = set(dia_df[resolve_col(dia_df, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip())
    tmt_syms = set(tmt_df[resolve_col(tmt_df, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip())
    csf_det = {g: {"dia_n259": (g in dia_syms) or (g == "STING1" and "TMEM173" in dia_syms), "tmt_n101": (g in tmt_syms) or (g == "STING1" and "TMEM173" in tmt_syms)} for g in ["STING1", "CGAS", "IFI16", "TBK1", "PSMB8", "HLA-A", "B2M"]}

    mmcif_res = analyze_staged_mmcif_structures(ROOT)
    geno_res = compute_nygc_genotype_stratified_cgas(t3, expr)
    ortholog_res = compute_cgas_ortholog_6mjw_alignment(ROOT, mmcif_res["6MJW"])
    apa_res = compute_staged_apa_audit()
    out = _clean_nan({
        "analysis_component": "Step1_and_Checkpoint2_5_Living_Intake_CGAS_vs_STING1_IFI16_PSMB8_Evaluation",
        "gnomad_v4_1_mane_constraint": gnomad_rows,
        "nygc_motor_cortex_control_anchored": {"stratum_counts": ctx["stratum_counts"], "genes": ctx["genes"]},
        "nygc_spinal_cord_control_anchored": {"stratum_counts": cord["stratum_counts"], "genes": cord["genes"]},
        "nygc_genotype_stratified_cgas_addendum": geno_res,
        "edinburgh_snrna_donor_collapsed_5lineages": edin,
        "pineda2024_snrna_donor_collapsed_ba4_ba9": pineda,
        "zhang2026_cervical_visium": {"mn_niche": zh["mn_niche_df"].to_dict(orient="records"), "tdp43_niche": zh["tdp43_niche_df"].to_dict(orient="records")},
        "spillman2026_c9ftd_fractions": sp,
        "brown2022_i3neuron_tdp43_kd": {
            "n_cryptic_junctions": int(len(b22["junctions_df"])),
            "rnaseq": b22["rnaseq_df"][["gene_name", "log2FoldChange", "pvalue", "padj"]].to_dict(orient="records"),
            "riboseq": b22["riboseq_df"][["gene_name", "log2FoldChange", "pvalue", "padj"]].to_dict(orient="records"),
        },
        "staged_3utr_apa_audit": apa_res,
        "trautwig2025_csf_detection": csf_det,
        "staged_mmcif_3d_dissection": mmcif_res,
        "cgas_6mjw_human_vs_mouse_ortholog_alignment": ortholog_res,
        "verified_external_priors_and_gene_liability": priors,
    })
    txt = json.dumps(out, indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(txt), "Biosecurity sequence guard failed!"
    OUT_FP.parent.mkdir(parents=True, exist_ok=True)
    OUT_FP.write_text(txt, encoding="utf-8")
    print(f"STEP 1 OK -> {OUT_FP.relative_to(ROOT).as_posix()} ({len(txt)} bytes)")


if __name__ == "__main__":
    main()
