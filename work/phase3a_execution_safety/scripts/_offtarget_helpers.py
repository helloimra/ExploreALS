"""Helper functions for Phase 3A off-target CNS 7-lineage expression, gnomAD v4.1 constraints, and strict JSON sanitization."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

from carbon_als.loaders import (
    load_edinburgh_pseudobulk,
    load_pineda2024_pseudobulk,
    load_zhang2026_spatial,
    resolve_col,
)


def sanitize_for_strict_json(obj: Any) -> Any:
    """Recursively convert float NaN/Inf into None so json.dumps(..., allow_nan=False) succeeds."""
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {str(k): sanitize_for_strict_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_strict_json(v) for v in obj]
    return obj


def load_gnomad_v41_constraint_map(tsv_path: Path) -> dict[str, dict[str, float | None]]:
    best: dict[str, tuple[int, dict[str, float | None]]] = {}
    with tsv_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            g = row.get("gene", "").strip()
            tx = row.get("transcript", "").strip()
            is_mane = row.get("mane_select", "").lower() == "true"
            is_canon = row.get("canonical", "").lower() == "true"
            if not g or not (is_mane or is_canon):
                continue
            # Prioritize Ensembl ENST* MANE Select (0) and ENST* canonical (1) over duplicate RefSeq NM_* rows (2/3)
            prio = (0 if is_mane else 1) if tx.startswith("ENST") else (2 if is_mane else 3)
            pli_s, loeuf_s = row.get("lof.pLI", ""), row.get("lof.oe_ci.upper", "")
            pli = round(float(pli_s), 4) if pli_s and pli_s != "NA" else None
            loeuf = round(float(loeuf_s), 4) if loeuf_s and loeuf_s != "NA" else None
            if loeuf is None and pli is None:
                continue
            cur = best.get(g)
            if cur is None or prio < cur[0]:
                best[g] = (prio, {"pLI": pli, "loeuf": loeuf})
    return {g: val for g, (_, val) in best.items()}


def load_pan_cns_7lineage_expression(genes: list[str]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, float]]]:
    """Evaluate baseline Control expression across 7 human CNS lineages (BA4 Exc/Inh/Oligo/OPC/Astro/Micro + Edinburgh Endo)."""
    if not genes:
        return {}, {}
    pineda_specs: list[tuple[str, str | list[str]]] = [
        ("BA4_Exc", "Excitatory"),
        ("BA4_Inh", ["PV", "SOM", "5HT3aR", "Rosehip"]),
        ("BA4_Oligo", "Oligo"),
        ("BA4_OPC", "OPC"),
        ("BA4_Astro", "Astro"),
        ("BA4_Micro", "Micro"),
    ]
    lineage_maps: dict[str, dict[str, dict[str, Any]]] = {}
    for label, ct_arg in pineda_specs:
        lineage_maps[label] = load_pineda2024_pseudobulk("BA4", ct_arg, genes)["stats"]
    lineage_maps["Edin_Endo"] = load_edinburgh_pseudobulk("Endothelial", genes)["stats"]

    summary: dict[str, dict[str, Any]] = {}
    for g in genes:
        exc_st = lineage_maps["BA4_Exc"].get(g, {})
        best_lin, best_val = "NONE", 0.0
        for lin_name, st_map in lineage_maps.items():
            v = float((st_map.get(g) or {}).get("mean_ctrl_log2cpm", 0.0) or 0.0)
            if v > best_val:
                best_val, best_lin = v, lin_name
        summary[g] = {
            "ba4_exc_ctrl_log2cpm": round(float(exc_st.get("mean_ctrl_log2cpm", 0.0) or 0.0), 3),
            "ba4_exc_als_vs_ctrl_diff": exc_st.get("diff_log2cpm"),
            "ba4_exc_welch_p": exc_st.get("p_welch"),
            "max_cns_ctrl_log2cpm": round(best_val, 3),
            "max_cns_lineage": best_lin,
        }

    zh_df = load_zhang2026_spatial(genes)["mn_niche_df"]
    zh_map: dict[str, dict[str, float]] = {}
    if zh_df is not None and not zh_df.empty:
        g_col, fc_col, bh_col = resolve_col(zh_df, "gene"), resolve_col(zh_df, "avg_log2FC"), resolve_col(zh_df, "BH")
        for _, zr in zh_df.iterrows():
            zh_map[str(zr[g_col])] = {"mn_log2fc_als_vs_hc": round(float(zr[fc_col]), 4), "mn_bh": float(zr[bh_col])}
    return summary, zh_map
