"""RUN-P4-006: Deterministic multi-cohort, 3D mmCIF, and gene-liability evaluation of NADSYN1 (L02) & CYFIP2 (L03)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (ROOT, SRC, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _v15_nadsyn1_cyfip2_packc_and_3d import (  # noqa: E402
    analyze_v15_structures,
    collect_pack_c_summary,
    map_gencode_mane_exons,
)
from carbon_als.loaders import (  # noqa: E402
    assert_modality,
    load_brown2022_splicing,
    load_edinburgh_pseudobulk,
    load_pineda2024_pseudobulk,
    load_spillman2026_fractions,
    load_zhang2026_spatial,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

S05_SCRIPT = SCRIPT_DIR / "05_living_intake_sting1_cgas_eval.py"
OUT_FP = ROOT / "work" / "phase4_final_synthesis" / "outputs" / "run_p4_006_living_nadsyn1_cyfip2_eval.json"
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)

CORE_GENES = ["NADSYN1", "CYFIP2", "CYFIP1", "NAMPT", "NMNAT2", "SARM1", "AKR1B1", "MEGF10"]
NYGC_PANEL = ["NADSYN1", "CYFIP2", "CYFIP1", "NAMPT", "NMNAT2", "AKR1B1"]


def _clean_nan(obj: object) -> object:
    if isinstance(obj, float) and (obj != obj):
        return None
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_nan(x) for x in obj]
    return obj


def _load_s05():
    spec = importlib.util.spec_from_file_location("_s05_mod", S05_SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _check_staged_apa(genes: set[str]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {"zeng2025": [], "bryce_smith2025": []}
    p_z = resolve_dataset_path("DS_ZENG_APA", verify_hash=True)
    for sh in ("Supplementary Table 3", "Table S3", "Sheet1"):
        try:
            zdf = pd.read_excel(p_z, sheet_name=sh)
            gcol = next((c for c in zdf.columns if "gene" in str(c).lower()), None)
            if gcol:
                sub = zdf.loc[zdf[gcol].astype(str).isin(genes)]
                out["zeng2025"] = sub.head(20).to_dict(orient="records")
                break
        except Exception:
            continue
    p_b = resolve_dataset_path("DS_BRYCE_APA", verify_hash=True)
    xl = pd.ExcelFile(p_b)
    for sh in xl.sheet_names:
        bdf = pd.read_excel(p_b, sheet_name=sh)
        gcol = next((c for c in bdf.columns if "gene_name" in str(c).lower() or str(c).lower() == "gene"), None)
        if gcol:
            sub = bdf.loc[bdf[gcol].astype(str).isin(genes)]
            if not sub.empty:
                for rec in sub.head(10).to_dict(orient="records"):
                    rec["_sheet"] = sh
                    out["bryce_smith2025"].append(rec)
    return out


def main() -> None:
    s05 = _load_s05()
    t3 = s05._load_t3()

    gdf = pd.read_csv(resolve_dataset_path("DS_GNOMAD_V41_CONSTRAINT", verify_hash=True), sep="\t", low_memory=False)
    gsub = gdf[
        gdf["gene"].isin(CORE_GENES)
        & (gdf["mane_select"].astype(str).str.lower() == "true")
        & gdf["transcript"].astype(str).str.startswith("ENST")
    ].sort_values("gene")
    gnomad_rows = gsub[["gene", "transcript", "lof.pLI", "lof.oe", "lof.oe_ci.upper", "lof.obs", "lof.exp", "mis.z_score"]].to_dict(orient="records")

    expr, gene_gc = s05._load_nygc_ens_gc_resolved(t3, NYGC_PANEL)
    ctx = s05._nygc_control_anchored(t3, expr, gene_gc, "TableS1B", "TableS1C", "Cortex_V15")
    cord = s05._nygc_control_anchored(t3, expr, gene_gc, "TableS1G", "TableS1H", "Spinal_V15")

    edin = {
        ct: load_edinburgh_pseudobulk(ct, NYGC_PANEL, region="donor_collapsed", min_nuclei=10)["stats"]
        for ct in ("Excitatory neuron", "Microglia", "Astrocyte", "Oligodendrocyte")
    }
    pineda = {
        reg: {ct: load_pineda2024_pseudobulk(reg, ct, NYGC_PANEL, min_nuclei=10)["stats"] for ct in ("Excitatory", "Micro", "Astro", "Oligo")}
        for reg in ("BA4", "BA9")
    }
    sp = load_spillman2026_fractions(CORE_GENES)
    zh = load_zhang2026_spatial(CORE_GENES)
    b22 = load_brown2022_splicing(["NADSYN1", "CYFIP2", "CYFIP1", "NAMPT", "NMNAT2"])
    j_cols = [
        c for c in (
            "gene_name", "lsv_id", "chr", "strand", "junc_start", "junc_end", "ir_start", "ir_end",
            "exon_start", "exon_end", "exon_length", "exon_mod_3", "junc_cat", "cryptic_junction",
            "paste_into_igv_junction", "control_e_psi", "tdp_kd_e_psi", "deltaPSI", "FDR",
        )
        if c in b22["junctions_df"].columns
    ]
    if not j_cols:
        j_cols = list(b22["junctions_df"].columns[:14])

    assert_modality("PROTEOMICS_CSF_DIA", "DS045_TRAUT")
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    dia_df = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    tmt_df = read_xlsx_sparse_safe(p45, "3-TMT-MS Raw Data", 2)
    dia_syms = set(dia_df[resolve_col(dia_df, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip())
    tmt_syms = set(tmt_df[resolve_col(tmt_df, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip())
    csf_det = {g: {"dia_n259": g in dia_syms, "tmt_n101": g in tmt_syms} for g in CORE_GENES}

    mane_exons = map_gencode_mane_exons({"NADSYN1", "CYFIP2"})
    mmcif_res = analyze_v15_structures(ROOT)
    apa_res = _check_staged_apa({"NADSYN1", "CYFIP2"})
    pack_c = collect_pack_c_summary(ROOT)

    out = _clean_nan({
        "analysis_component": "RUN-P4-006_ExploreALS_v1_5_Living_Intake_NADSYN1_L02_CYFIP2_L03_and_PackC_Benchmark",
        "gnomad_v4_1_mane_constraint": gnomad_rows,
        "gencode_v46_mane_exon_cds_map": mane_exons,
        "nygc_motor_cortex_control_anchored": {"stratum_counts": ctx["stratum_counts"], "genes": ctx["genes"]},
        "nygc_spinal_cord_control_anchored": {"stratum_counts": cord["stratum_counts"], "genes": cord["genes"]},
        "edinburgh_snrna_donor_collapsed": edin,
        "pineda2024_snrna_donor_collapsed": pineda,
        "zhang2026_cervical_visium": {"mn_niche": zh["mn_niche_df"].to_dict(orient="records"), "tdp43_niche": zh["tdp43_niche_df"].to_dict(orient="records")},
        "spillman2026_c9ftd_fractions": sp,
        "brown2022_i3neuron_tdp43_kd": {
            "junctions": b22["junctions_df"][j_cols].to_dict(orient="records"),
            "rnaseq": b22["rnaseq_df"][["gene_name", "log2FoldChange", "pvalue", "padj"]].to_dict(orient="records"),
            "riboseq": b22["riboseq_df"][["gene_name", "log2FoldChange", "pvalue", "padj"]].to_dict(orient="records"),
        },
        "staged_apa_audit": apa_res,
        "trautwig2025_csf_detection": csf_det,
        "staged_mmcif_3d_dissection": mmcif_res,
        "pack_c_multi_cohort_replication_and_crosslinks": pack_c,
    })
    txt = json.dumps(out, indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(txt), "Biosecurity sequence guard failed on RUN-P4-006 JSON!"
    OUT_FP.parent.mkdir(parents=True, exist_ok=True)
    OUT_FP.write_text(txt, encoding="utf-8")
    print(f"RUN-P4-006 OK -> {OUT_FP.relative_to(ROOT).as_posix()} ({len(txt):,} bytes)")


if __name__ == "__main__":
    main()
