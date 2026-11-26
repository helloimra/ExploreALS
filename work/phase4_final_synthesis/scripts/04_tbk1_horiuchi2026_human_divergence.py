"""Reproducible human ALS multi-cohort re-analysis of TBK1, cGAS-STING, Type I IFN, and MAM markers (Horiuchi et al. 2026 context)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from carbon_als.loaders import (  # noqa: E402
    assert_modality,
    load_brown2022_splicing,
    load_edinburgh_pseudobulk,
    load_spillman2026_fractions,
    load_zhang2026_spatial,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

T3_SCRIPT = ROOT / "work" / "phase2" / "track3_subtype_precision_translation" / "scripts" / "06_c019_s09_jak_tyk2_receptor_and_csf_cxcl10.py"
OUT_FP = ROOT / "work" / "phase4_final_synthesis" / "outputs" / "run_p4_004_tbk1_human_divergence.json"

PANEL_GENES = [
    "TBK1", "IKBKE", "TNF", "TNFRSF1A", "RIPK1",
    "OPTN", "SQSTM1", "TAX1BP1", "ATG4B", "VAPB", "ITPR3",
    "CGAS", "STING1", "TMEM173", "IFI16", "IRF3", "IFIH1",
    "IFNAR1", "IFNAR2", "TYK2", "JAK1", "JAK2", "STAT1", "STAT2",
    "ISG15", "IFIT1", "IFIT3", "MX1", "OAS1", "RSAD2", "CXCL10",
]


def _clean_nan(obj: object) -> object:
    if isinstance(obj, float) and (obj != obj):
        return None
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_nan(x) for x in obj]
    return obj


def _load_t3_module():
    spec = importlib.util.spec_from_file_location("_t3_jak_tyk2", T3_SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    t3 = _load_t3_module()

    # 1. Staged gnomAD v4.1 MANE Select constraint
    gdf = pd.read_csv(resolve_dataset_path("DS_GNOMAD_V41_CONSTRAINT", verify_hash=True), sep="\t", low_memory=False)
    gsub = gdf[gdf["gene"].isin(["TBK1", "IKBKE", "RIPK1", "OPTN", "VAPB", "CGAS", "STING1", "IFI16", "IFNAR1", "TYK2", "JAK1"])].copy()
    gsub = gsub[gsub["mane_select"].astype(str).str.lower() == "true"]
    gsub = gsub[gsub["transcript"].astype(str).str.startswith("ENST")].sort_values("gene")
    gnomad_cols = ["gene", "transcript", "lof.pLI", "lof.oe", "lof.oe_ci.upper", "lof.obs", "lof.exp", "mis.z_score"]
    gnomad_records = gsub[gnomad_cols].to_dict(orient="records")

    # 2. NYGC Motor Cortex & Spinal Cord donor-level GC% + neuronal/glial + RIN OLS (exclude_pure_ftd via Group filter)
    nygc_syms = sorted(set(PANEL_GENES) | set(t3.CELLCOMP_GENES))
    expr, gene_gc = t3.load_nygc_panel(nygc_syms)
    p_on = resolve_dataset_path("DS001_ONEILL", verify_hash=True)
    ctx_res = t3.summarize_nygc_region(expr, gene_gc, read_xlsx_sparse_safe(p_on, "TableS1B", 2), read_xlsx_sparse_safe(p_on, "TableS1C", 2), "Cortex_TBK1")
    cord_res = t3.summarize_nygc_region(expr, gene_gc, read_xlsx_sparse_safe(p_on, "TableS1G", 2), read_xlsx_sparse_safe(p_on, "TableS1H", 2), "Spinal_TBK1")

    # 3. Spillman 2026 C9-FTD frontal cortex homogenate & P2 synaptosome DIA proteomics + RNA-seq
    sp_res = load_spillman2026_fractions(
        ["TBK1", "IKBKE", "RIPK1", "OPTN", "SQSTM1", "TAX1BP1", "VAPB", "ITPR3", "CGAS", "STING1", "IFI16", "TYK2", "JAK1", "STAT1", "ISG15", "RSAD2"]
    )

    # 4. Zhang 2026 human cervical spinal cord 55-um Visium spatial niches
    zh = load_zhang2026_spatial(["TBK1", "RIPK1", "OPTN", "VAPB", "ITPR3", "CGAS", "STING1", "IFI16", "RSAD2", "ISG15", "APOE", "GPNMB", "CHIT1"])

    # 5. Edinburgh donor-collapsed snRNA-seq Microglia & Excitatory neuron checks
    edin_out: dict[str, object] = {}
    for ct in ("Microglia", "Astrocyte", "Excitatory neuron", "Endothelial"):
        er = load_edinburgh_pseudobulk(ct, ["TBK1", "OPTN", "VAPB", "CGAS", "STING1", "IFI16", "IFNAR1", "TYK2", "JAK1", "STAT1", "ISG15", "RSAD2", "CXCL10"], region="donor_collapsed", min_nuclei=10)
        edin_out[ct] = er["stats"]

    # 6. Brown 2022 i3Neuron TDP-43 KD splicing & RNA/Ribo-seq
    b22 = load_brown2022_splicing(["TBK1", "OPTN", "TAX1BP1", "VAPB", "CGAS", "STING1", "IFI16", "IFNAR1", "TYK2", "JAK1"])

    # 7. Trautwig 2025 antemortem CSF DIA & TMT detection status
    assert_modality("PROTEOMICS_CSF_DIA", "DS045_TRAUT")
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    dia = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    tmt = read_xlsx_sparse_safe(p45, "3-TMT-MS Raw Data", 2)
    dia_syms = set(dia[resolve_col(dia, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip())
    tmt_syms = set(tmt[resolve_col(tmt, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip())
    csf_det = {
        g: {
            "dia_n259_detected": (g in dia_syms) or (g == "STING1" and "TMEM173" in dia_syms),
            "tmt_n101_detected": (g in tmt_syms) or (g == "STING1" and "TMEM173" in tmt_syms),
        }
        for g in ["TBK1", "IKBKE", "CGAS", "STING1", "IFI16", "RSAD2", "ISG15", "CXCL10", "STAT1"]
    }

    payload = _clean_nan({
        "analysis_component": "TBK1_cGAS_STING_IFNI_Human_ALS_Divergence_Horiuchi2026_Context",
        "linked_run_id": "RUN-P4-003",
        "gnomad_v4_1_mane_constraint": gnomad_records,
        "nygc_motor_cortex": {"stratum_counts": ctx_res["stratum_counts"], "axis_composites": ctx_res["axis_composites"], "genes": ctx_res["genes"]},
        "nygc_spinal_cord": {"stratum_counts": cord_res["stratum_counts"], "axis_composites": cord_res["axis_composites"], "genes": cord_res["genes"]},
        "spillman2026_c9ftd_fractions": sp_res,
        "zhang2026_cervical_visium": {"mn_niche": zh["mn_niche_df"].to_dict(orient="records"), "tdp43_niche": zh["tdp43_niche_df"].to_dict(orient="records")},
        "edinburgh_snrna_donor_collapsed": edin_out,
        "brown2022_i3neuron_tdp43_kd": {
            "n_cryptic_junction_rows": int(len(b22["junctions_df"])),
            "rnaseq": b22["rnaseq_df"][["gene_name", "log2FoldChange", "pvalue", "padj"]].to_dict(orient="records"),
            "riboseq": b22["riboseq_df"][["gene_name", "log2FoldChange", "pvalue", "padj"]].to_dict(orient="records"),
        },
        "trautwig2025_antemortem_csf_detection": csf_det,
    })
    OUT_FP.parent.mkdir(parents=True, exist_ok=True)
    OUT_FP.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    print(f"SAVED {OUT_FP.relative_to(ROOT).as_posix()} ({OUT_FP.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
