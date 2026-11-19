"""RUN-P2-T3-003: C019 JAK/AAK1 Unbound CNS Occupancy, Bye 2025 Donor Co-Response & C020 Pulsed PIKfyve Kill-Gate."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import urllib.request

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from carbon_als.allostery_pkpd import (  # noqa: E402
    simulate_pulsed_vs_continuous_pkpd,
    sweep_coupled_pikfyve_casm_sensitivity,
    sweep_pulsed_pkpd_sensitivity,
)
from carbon_als.loaders import (  # noqa: E402
    assert_modality,
    assert_unique_donors,
    load_bye2025_screen,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)
from carbon_als.skill_cli import run_skill_cli_to_file  # noqa: E402

import os

OUT_DIR = ROOT / "work" / "phase2" / "track3_subtype_precision_translation" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CHEMBL_CLI = Path(os.environ.get("CHEMBL_SKILL_CLI", ""))


def query_chembl_target_potencies() -> dict:
    scratch = OUT_DIR / "chembl_scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    summary: dict[str, list[dict]] = {}
    old_apil = scratch / "apilimod_mesylate_CHEMBL4297643.json"
    new_apil = scratch / "apilimod_freebase_CHEMBL4297643.json"
    if old_apil.is_file() and not new_apil.is_file():
        new_apil.write_text(old_apil.read_text(encoding="utf-8"), encoding="utf-8")
    for label, cid in [
        ("baricitinib_CHEMBL2105759", "CHEMBL2105759"),
        ("apilimod_freebase_CHEMBL4297643", "CHEMBL4297643"),
        ("censavudine_CHEMBL124363", "CHEMBL124363"),
    ]:
        cache_f = scratch / f"{label}.json"
        if cache_f.is_file():
            data = json.loads(cache_f.read_text(encoding="utf-8"))
        else:
            try:
                data = run_skill_cli_to_file(
                    CHEMBL_CLI,
                    [
                        "activity",
                        "--filter",
                        f"molecule_chembl_id={cid}",
                        "--filter",
                        "pchembl_value__isnull=false",
                        "--normalize",
                        "--limit",
                        "40",
                    ],
                    cache_f,
                    timeout_sec=25,
                )
            except TimeoutError:
                url = (
                    f"https://www.ebi.ac.uk/chembl/api/data/activity.json?"
                    f"molecule_chembl_id={cid}&pchembl_value__isnull=false&limit=40"
                )
                req = urllib.request.Request(url, headers={"User-Agent": "CarbonALS-Scientific-Verification/0.3"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                cache_f.write_text(json.dumps(data, indent=2), encoding="utf-8")
        acts = data.get("activities", []) if isinstance(data, dict) else []
        rows = []
        for a in acts:
            nv = a.get("normalized_value_nM")
            if nv is None and a.get("standard_units") == "nM" and a.get("standard_value") is not None:
                nv = float(a["standard_value"])
            st = a.get("standard_type")
            if nv is not None and st in {"IC50", "Ki", "Kd", "EC50"}:
                rows.append({
                    "target_pref_name": a.get("target_pref_name"),
                    "target_organism": a.get("target_organism"),
                    "standard_type": st,
                    "standard_relation": a.get("standard_relation"),
                    "normalized_value_nM": round(float(nv), 3),
                    "pchembl_value": a.get("pchembl_value"),
                })
        rows.sort(key=lambda r: r["normalized_value_nM"])
        summary[label] = rows[:25]
    return summary


def analyze_bye2025_donor_heterogeneity() -> dict:
    assert_modality("IPSC_MN_SURVIVAL_DAYS", "DS005_BYE")
    bye_summary = load_bye2025_screen()
    p_bye = resolve_dataset_path("DS005_BYE", verify_hash=True)
    t12 = read_xlsx_sparse_safe(p_bye, "Table 12", header_row_1based=3)
    drug_col = resolve_col(t12, "Active Ingredient")
    donor_cols = [resolve_col(t12, f"SALS {i}") for i in range(1, 17)]
    assert_unique_donors(donor_cols, "DS005_BYE_16_Donor_Lines")
    t12 = t12[t12[drug_col].notna()].copy()
    t12[drug_col] = t12[drug_col].astype(str).str.strip()
    for dc in donor_cols:
        t12[dc] = pd.to_numeric(t12[dc], errors="coerce")
    dmso = t12.loc[t12[drug_col] == "DMSO", donor_cols].iloc[0]

    sub_drugs = {}
    for target_name in ["Riluzole", "Baricitinib", "Apilimod", "Fedratinib", "Ruxolitinib"]:
        m = t12[t12[drug_col].astype(str).str.contains(target_name, case=False, na=False)]
        if len(m) >= 1:
            sub_drugs[target_name] = pd.to_numeric(m.iloc[0][donor_cols], errors="coerce") - dmso

    df_d = pd.DataFrame(sub_drugs)
    apil_neg = df_d.loc[df_d["Apilimod"] < 0.0]
    apil_pos = df_d.loc[df_d["Apilimod"] > 0.0]
    r_bar_apil, p_bar_apil = stats.pearsonr(df_d["Baricitinib"].dropna(), df_d["Apilimod"].dropna())
    r_ril_bar, p_ril_bar = stats.pearsonr(df_d["Riluzole"].dropna(), df_d["Baricitinib"].dropna())

    return {
        "n_unique_sals_donor_lines": int(len(donor_cols)),
        "donor_line_ids": donor_cols,
        "summary_table_metrics": bye_summary.loc[
            bye_summary["drug"].str.contains("Riluzole|Baricitinib|Apilimod|Fedratinib|Ruxolitinib", case=False, na=False)
        ].to_dict(orient="records"),
        "per_donor_paired_dmso_days": {
            k: {d: round(float(v), 4) for d, v in df_d[k].items()} for k in df_d.columns
        },
        "apilimod_harmed_donors_n": int(len(apil_neg)),
        "apilimod_harmed_donor_ids": apil_neg.index.tolist(),
        "apilimod_harmed_donors_mean_apilimod_days": round(float(apil_neg["Apilimod"].mean()), 4),
        "apilimod_harmed_donors_mean_baricitinib_days": round(float(apil_neg["Baricitinib"].mean()), 4),
        "apilimod_harmed_donors_mean_riluzole_days": round(float(apil_neg["Riluzole"].mean()), 4),
        "apilimod_helped_donors_mean_baricitinib_days": round(float(apil_pos["Baricitinib"].mean()), 4),
        "baricitinib_positive_in_n_of_16_donors": int((df_d["Baricitinib"] > 0.0).sum()),
        "apilimod_positive_in_n_of_16_donors": int((df_d["Apilimod"] > 0.0).sum()),
        "donor_corr_baricitinib_vs_apilimod": {"r": round(float(r_bar_apil), 4), "p": float(p_bar_apil)},
        "donor_corr_riluzole_vs_baricitinib": {"r": round(float(r_ril_bar), 4), "p": float(p_ril_bar)},
    }


def model_baricitinib_cns_occupancy() -> list[dict]:
    # Enzymatic & cellular IC50/Kd values (ChEMBL2105759 + NADALS NCT05189106 human CSF PK)
    targets = {
        "JAK1_enzymatic_IC50_5p9nM": 5.9,
        "JAK2_enzymatic_IC50_5p7nM": 5.7,
        "WholeCell_IFNg_IL6_pSTAT_IC50_40nM": 40.0,
        "AAK1_Kd_17nM": 17.0,
        "TYK2_enzymatic_IC50_53nM": 53.0,
        "JAK3_enzymatic_IC50_560nM": 560.0,
        "Bye2025_Screen_Conc_2500nM": 2500.0,
    }
    regimens = [
        ("2mg_QD_oral_ALS_CSF", 1.75),
        ("4mg_QD_oral_NADALS_measured_CSF", 3.80),
        ("8mg_QD_supratherapeutic_boxed_warning", 7.60),
        ("20nM_in_vitro_bridge_dose", 20.0),
        ("2500nM_Bye2025_screen_dose", 2500.0),
    ]
    out = []
    for label, cu_nm in regimens:
        row: dict[str, str | float] = {"regimen": label, "cu_cns_nM": cu_nm}
        for tname, ic50 in targets.items():
            if "Bye2025" in tname:
                row["fold_vs_2500nM_screen"] = round(cu_nm / 2500.0, 5)
            else:
                row[f"occ_pct_{tname}"] = round(100.0 * cu_nm / (cu_nm + ic50), 2)
        out.append(row)
    return out


def model_apilimod_pulsed_killgate() -> list[dict]:
    # 14-day (336h) regimen sweep calibrated to AIT-101 125 mg BID (Cu,CSF = 3.89 nM, t1/2 ~ 4.5 h, cellular PIKfyve Ki ~ 1.5 nM)
    schedules = [
        ("AIT101_125mg_BID_Continuous_12h", [float(h) for h in range(0, 336, 12)], 3.89),
        ("Continuous_LowDose_QD_24h", [float(h) for h in range(0, 336, 24)], 3.89),
        ("Pulsed_48h_ON_BID_120h_OFF_3p89nM", [float(w * 168 + h) for w in range(2) for h in (0, 12, 24, 36)], 3.89),
        ("Pulsed_48h_ON_BID_120h_OFF_6p5nM", [float(w * 168 + h) for w in range(2) for h in (0, 12, 24, 36)], 6.50),
        ("Pulsed_24h_ON_BID_144h_OFF_8p0nM", [float(w * 168 + h) for w in range(2) for h in (0, 12)], 8.00),
        ("TwiceWeekly_SinglePulse_MonThu_8p0nM", [0.0, 84.0, 168.0, 252.0], 8.00),
        ("Every3Days_q72h_SinglePulse_6p5nM", [0.0, 72.0, 144.0, 216.0, 288.0], 6.50),
        ("Every3Days_q72h_SinglePulse_8p0nM", [0.0, 72.0, 144.0, 216.0, 288.0], 8.00),
        ("Every48h_q48h_SinglePulse_6p5nM", [float(h) for h in range(0, 336, 48)], 6.50),
    ]
    rows = []
    for name, hrs, cmax_u in schedules:
        sim = simulate_pulsed_vs_continuous_pkpd(
            dose_schedule_hours=hrs,
            total_hours=336.0,
            cmax_unbound_nm=cmax_u,
            half_life_hours=4.5,
            target_ki_nm=1.5,
            occ_clear_ec50=0.22,
            occ_vac_thresh=0.45,
            tau_clear_h=28.0,
            tau_substrate_regen_h=192.0,
            tau_vac_accum_h=18.0,
            tau_vac_repair_h=14.0,
        )
        sim_row: dict[str, str | float | bool] = {"regimen": name, "cmax_unbound_csf_nM": cmax_u, **sim}
        sim_row["passes_killgate_polyGP_ge_55pct_and_end_vac_le_0p05"] = bool(
            sim["end_substrate_pct_reduction"] >= 55.0 and sim["end_vacuolation_stress_index"] <= 0.05
        )
        rows.append(sim_row)
    return rows


def model_coupled_vs_decoupled_pikfyve_sweeps() -> dict:
    key_schedules = [
        ("AIT101_125mg_BID_Continuous_12h", [float(h) for h in range(0, 336, 12)], 3.89, 336.0),
        ("Every48h_q48h_SinglePulse_6p5nM", [float(h) for h in range(0, 336, 48)], 6.50, 336.0),
        ("Every3Days_q72h_SinglePulse_6p5nM", [0.0, 72.0, 144.0, 216.0, 288.0], 6.50, 336.0),
        ("Every3Days_q72h_SinglePulse_8p0nM_336h", [0.0, 72.0, 144.0, 216.0, 288.0], 8.00, 336.0),
        ("Every3Days_q72h_SinglePulse_8p0nM_360h_Full5CycleTrough", [0.0, 72.0, 144.0, 216.0, 288.0], 8.00, 360.0),
    ]
    rows = []
    for name, hrs, cmax_u, tot_h in key_schedules:
        m1 = sweep_pulsed_pkpd_sensitivity(hrs, tot_h, cmax_u, 4.5, 1.5)
        m2 = sweep_coupled_pikfyve_casm_sensitivity(hrs, tot_h, cmax_u, 4.5, 1.5)
        rows.append({
            "regimen": name,
            "cmax_unbound_csf_nM": cmax_u,
            "total_hours": tot_h,
            "model1_decoupled_osmotic_deadzone_81pt": m1,
            "model2_coupled_zero_deadzone_pi3p_lrrk2_casm_81pt": m2,
        })
    return {"regimen_sweeps": rows}


def main() -> None:
    chembl_pot = query_chembl_target_potencies()
    bye_het = analyze_bye2025_donor_heterogeneity()
    bari_occ = model_baricitinib_cns_occupancy()
    apil_grid = model_apilimod_pulsed_killgate()
    apil_sweeps = model_coupled_vs_decoupled_pikfyve_sweeps()
    out = {
        "analysis_run_id": "RUN-P2-T3-003",
        "chembl_normalized_potencies": chembl_pot,
        "c019_baricitinib_cns_occupancy": bari_occ,
        "bye2025_16donor_heterogeneity": bye_het,
        "c020_apilimod_pulsed_vs_continuous_pkpd": apil_grid,
        "c020_nov2026_decoupled_vs_coupled_casm_sweeps": apil_sweeps,
    }
    (OUT_DIR / "run_p2_t3_003_pk_selectivity_and_pulsed_killgate.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("SAVED run_p2_t3_003_pk_selectivity_and_pulsed_killgate.json")


if __name__ == "__main__":
    main()
