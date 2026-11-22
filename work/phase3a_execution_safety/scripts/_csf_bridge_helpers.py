"""Helpers for C019 CSF Glial Bridge scoring, JATS XML header-resolved table extraction, and strict ROC/Welch evaluation."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from scipy import stats

BRIDGE_SYMS = ["CHIT1", "CHI3L2", "GPNMB", "CHI3L1", "SERPINA3"]


def roc_auc_mw(y_true: np.ndarray, scores: np.ndarray) -> float:
    pos, neg = scores[y_true == 1], scores[y_true == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.0
    u_stat = float(stats.mannwhitneyu(pos, neg, alternative="two-sided").statistic)
    return u_stat / float(len(pos) * len(neg))


def fit_bridge_params(df_raw: pd.DataFrame, ctrl_mask: pd.Series) -> dict[str, Any]:
    stats_map: dict[str, dict[str, float]] = {}
    z_ctrl = pd.DataFrame(index=df_raw.loc[ctrl_mask].index)
    for g in BRIDGE_SYMS:
        vals = pd.to_numeric(df_raw.loc[ctrl_mask, g], errors="coerce")
        clean = vals.dropna()
        mu, sd = float(clean.mean()), max(float(clean.std(ddof=1)), 1e-6)
        stats_map[g] = {"mean": mu, "sd": sd}
        z_ctrl[g] = (vals - mu) / sd
    comp_mask = z_ctrl["CHIT1"].notna() & (z_ctrl["CHIT1"] > -2.0)
    raw_max = np.maximum(z_ctrl.loc[comp_mask, "CHIT1"], z_ctrl.loc[comp_mask, "CHI3L2"].fillna(-3.0))
    c_mu = float(raw_max.mean()) if len(raw_max) >= 2 else 0.0
    c_sd = max(float(raw_max.std(ddof=1)), 1e-6) if len(raw_max) >= 2 else 1.0
    params: dict[str, Any] = {"protein_norm": stats_map, "chit_max_mean": c_mu, "chit_max_sd": c_sd}
    params["z_cut_95_ctrl"] = float(score_bridge(df_raw.loc[ctrl_mask], params, calibrated=True).quantile(0.95))
    params["z_cut_95_ctrl_legacy"] = float(score_bridge(df_raw.loc[ctrl_mask], params, calibrated=False).quantile(0.95))
    return params


def score_bridge(df_raw: pd.DataFrame, params: dict[str, Any], calibrated: bool = True) -> pd.Series:
    norm_map = params["protein_norm"]
    z = pd.DataFrame(index=df_raw.index)
    for g in BRIDGE_SYMS:
        z[g] = (pd.to_numeric(df_raw[g], errors="coerce") - norm_map[g]["mean"]) / norm_map[g]["sd"]
    if calibrated:
        is_comp = z["CHIT1"].notna() & (z["CHIT1"] > -2.0)
        both_max = (np.maximum(z["CHIT1"].fillna(-3.0), z["CHI3L2"].fillna(-3.0)) - float(params["chit_max_mean"])) / float(params["chit_max_sd"])
        chit_axis = np.where(is_comp, both_max, z["CHI3L2"].fillna(-3.0).to_numpy())
    else:
        chit_axis = np.nanmax(np.vstack([z["CHIT1"].fillna(-3.0), z["CHI3L2"].fillna(0.0)]), axis=0)
    comp = pd.concat([pd.Series(chit_axis, index=df_raw.index), z["GPNMB"], z["CHI3L1"], z["SERPINA3"]], axis=1)
    return comp.mean(axis=1)


def eval_contrast(scores: pd.Series, pos_mask: pd.Series, neg_mask: pd.Series, z_cut: float) -> dict[str, float | int | None]:
    pos, neg = scores.loc[pos_mask].dropna().to_numpy(), scores.loc[neg_mask].dropna().to_numpy()
    y = np.concatenate([np.ones(len(pos), dtype=int), np.zeros(len(neg), dtype=int)])
    sc = np.concatenate([pos, neg])
    w_p = float(stats.ttest_ind(pos, neg, equal_var=False).pvalue) if len(pos) >= 2 and len(neg) >= 2 else None
    mwu_p = float(stats.mannwhitneyu(pos, neg, alternative="two-sided").pvalue) if len(pos) >= 1 and len(neg) >= 1 else None
    return {
        "n_cases": int(len(pos)), "n_controls": int(len(neg)), "n_total": int(len(pos) + len(neg)),
        "mean_diff_vs_ctrl_z": round(float(pos.mean() - neg.mean()), 4),
        "case_mean_z": round(float(pos.mean()), 4), "ctrl_mean_z": round(float(neg.mean()), 4),
        "roc_auc": round(roc_auc_mw(y, sc), 4), "welch_p": w_p, "mwu_p": mwu_p,
        "sensitivity_at_train_z95": round(float((pos > z_cut).mean()), 4),
        "ctrl_fpr_at_train_z95": round(float((neg > z_cut).mean()), 4),
    }


def extract_oh2023_header_resolved(xml_path: Path) -> dict[str, Any]:
    def expand_rows(trs: list[ET.Element]) -> list[list[str]]:
        grid: dict[tuple[int, int], str] = {}
        max_c = 0
        for r_i, tr in enumerate(trs):
            c_i = 0
            for cell in list(tr):
                while (r_i, c_i) in grid:
                    c_i += 1
                txt = re.sub(r"\s+", " ", "".join(cell.itertext())).strip()
                rs, cs = int(cell.attrib.get("rowspan", "1") or "1"), int(cell.attrib.get("colspan", "1") or "1")
                for dr in range(rs):
                    for dc in range(cs):
                        grid[(r_i + dr, c_i + dc)] = txt
                c_i += cs
                max_c = max(max_c, c_i)
        return [[grid.get((r, c), "") for c in range(max_c)] for r in range(len(trs))]

    root = ET.parse(xml_path).getroot()
    tws = root.findall(".//table-wrap")
    t1_h, t1_b = expand_rows(tws[0].findall(".//thead//tr"))[-1], expand_rows(tws[0].findall(".//tbody//tr"))
    sid_idx = t1_h.index("Subject ID")
    app_idx = next(i for i, h in enumerate(t1_h) if "Application" in h)
    als_tot = sum(1 for r in t1_b if r[sid_idx].upper().startswith("ALS"))
    hc_tot = sum(1 for r in t1_b if r[sid_idx].upper().startswith("HC"))
    als_disc = sum(1 for r in t1_b if r[sid_idx].upper().startswith("ALS") and "DISCOVERY" in r[app_idx].upper())
    hc_disc = sum(1 for r in t1_b if r[sid_idx].upper().startswith("HC") and "DISCOVERY" in r[app_idx].upper())

    t2_h, t2_b = expand_rows(tws[1].findall(".//thead//tr"))[-1], expand_rows(tws[1].findall(".//tbody//tr"))
    g_idx, p_idx, fc_idx = t2_h.index("Gene Symbol"), t2_h.index("p Value"), t2_h.index("Log2(ALS/HC)")
    det_idx = t2_h.index("Detectability by PRM")
    disc_q_idx = next(i for i, h in enumerate(t2_h) if h == "q-Value" and i < fc_idx)
    prm_q_idx = next(i for i, h in enumerate(t2_h) if h == "q-Value" and i > det_idx)
    rep: dict[str, dict[str, str | float]] = {}
    for row in t2_b:
        if len(row) > prm_q_idx and row[g_idx] in BRIDGE_SYMS:
            det_txt = row[det_idx].strip()
            prm_ok = det_txt.lower().startswith("detect")
            rep[row[g_idx]] = {
                "log2_als_vs_hc": float(row[fc_idx].replace("−", "-")),
                "discovery_p_raw_text": row[p_idx], "discovery_q": float(row[disc_q_idx]),
                "prm_detectability": det_txt if prm_ok else "UNREPORTED_BLANK_IN_TABLE2",
                "prm_validation_q": row[prm_q_idx].strip() if prm_ok else "",
            }
    assert len(rep) == 5, f"Expected 5/5 bridge proteins in Oh 2023 Table 2, got {len(rep)}"
    n_disc_sig = sum(1 for v in rep.values() if float(v["discovery_q"]) <= 0.05)
    n_prm_sig = sum(1 for v in rep.values() if bool(v["prm_validation_q"]))
    return {
        "scope": "UNIVARIATE_5_OF_5_DISCOVERY_MS_AND_4_OF_5_PRM_VALIDATION_40_OF_61_OVERLAP",
        "n_als_discovery": als_disc, "n_hc_discovery": hc_disc, "n_total_discovery": als_disc + hc_disc,
        "n_als_total_table1": als_tot, "n_hc_total_table1": hc_tot, "n_total_table1": als_tot + hc_tot,
        "n_bridge_proteins_fdr_lt_0_05": n_disc_sig,
        "n_bridge_proteins_prm_validated": n_prm_sig,
        "proteins": rep,
    }
