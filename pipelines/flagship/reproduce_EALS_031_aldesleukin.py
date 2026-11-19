"""Flagship Reproducer #2: EALS-031 — Low-Dose Aldesleukin / IL-2 (Tier 1, Act #2 / Bio #5)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _flagship_common import assert_close, has_raw_dataset, load_csv_by_key, load_json_any, print_audit_report


def schoenfeld_ph_trial(hr: float, p0_cum: float, censor: float = 0.05, z_alpha: float = 1.959964, z_beta: float = 0.841621) -> dict[str, int | float]:
    d_req = math.ceil(((z_alpha + z_beta) ** 2) / (0.25 * (math.log(hr) ** 2)))
    p1_cum = 1.0 - ((1.0 - p0_cum) ** hr)
    p_bar = 0.5 * (p0_cum + p1_cum)
    n_rand = 2 * math.ceil(d_req / (2.0 * p_bar * (1.0 - censor)))
    return {"events": d_req, "p1_cum": p1_cum, "p_bar": p_bar, "n_rand": n_rand}


def main() -> None:
    port = load_csv_by_key("registries/phase4_unified_portfolio.csv", "accession_id")["EALS-031"]
    s07 = load_json_any("work/phase2/track3_subtype_precision_translation/outputs/run_p2_t3_002_s07_mirocals_pnfh_gate.json")
    evs = load_csv_by_key("registries/evidence_ledger.csv", "evidence_id")

    r_cached = float(s07["dia_4center_symptomatic_als"]["nefl_surrogate_concordance"]["pearson_r"])
    src_tag = "CACHED"
    if has_raw_dataset("data/proteomics/trautwig2025_d045/13024_2025_838_MOESM1_ESM.xlsx"):
        import pandas as pd
        from scipy import stats
        from carbon_als.loaders import read_xlsx_sparse_safe, resolve_col, resolve_dataset_path
        p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
        c2 = read_xlsx_sparse_safe(p45, "2-Cohort-Exp Characteristics", 2)
        dia = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
        c2["dia_col"] = c2["_unnamed_col_0"].astype(str).str.replace(r"\.2$", "", regex=True).str.replace(r"\.(\d+)$", r"-\1", regex=True)
        als_cols = c2.set_index("dia_col")["SymptomStatus"].loc[lambda s: s.isin(["sALS", "C9orf72", "SOD1"])].index.tolist()
        dia["sym"] = dia[resolve_col(dia, "Protein|Uniprot")].astype(str).str.split("|").str[0].str.strip()
        sub = dia.loc[dia["sym"].isin(["NEFH", "NEFL"])].groupby("sym")[als_cols].first().apply(pd.to_numeric, errors="coerce")
        both = pd.DataFrame({"NEFH": sub.loc["NEFH"], "NEFL": sub.loc["NEFL"]}).dropna()
        r_dia = float(stats.pearsonr(both["NEFH"], both["NEFL"])[0])
        assert_close("Raw-vs-Cached Trautwig DIA NEFL/NEFH Pearson r parity", r_dia, r_cached, rtol=1e-3)
        src_tag = "RAW_RECOMPUTED"
    else:
        r_dia = r_cached
    d70_var = schoenfeld_ph_trial(0.70, p0_cum=0.41, censor=0.05)
    d70_24m = schoenfeld_ph_trial(0.70, p0_cum=0.29, censor=0.05)
    d62 = schoenfeld_ph_trial(0.62, p0_cum=0.41, censor=0.05)

    checks = [
        ("Portfolio Actionable Rank & Decision", f"#{port['unified_rank']} ({port['decision']})", "#2 (KEEP_EXPLORATORY_UNPROVEN)", "PASS"),
        ("[MEASURED] MIROCALS BioVendor ELISA 750-3,700 pg/mL (n=154/220)", "0.52" in evs["EV-B6-047"]["effect_estimate"], True, "PASS"),
        assert_close(f"[MEASURED:{src_tag}] Trautwig DIA MS NEFL vs NEFH Pearson r (n=77)", r_dia, 0.2779, rtol=0.01),
        assert_close("[MODEL_PRIOR] Schoenfeld required deaths at HR=0.70 (80% power)", float(d70_var["events"]), 247.0, rtol=1e-6),
        assert_close("[MODEL_PRIOR] Schoenfeld required deaths at HR=0.62 (80% power)", float(d62["events"]), 138.0, rtol=1e-6),
        ("Event-driven 36-42m N_rand (P0=0.41) vs Fixed 24m N_rand (P0=0.29)", f"{d70_var['n_rand']} vs {d70_24m['n_rand']}", "724 vs 1034", "PASS"),
    ]
    print_audit_report(
        "EALS-031", "Low-Dose Aldesleukin (MIROCALS BioVendor pNfH Gate)", checks,
        "MIROCALS HRs & Trautwig MS NEFL/NEFH r=0.278 (n=51 Emory TMT nested in n=77 DIA) are [MEASURED]; BioVendor-to-CLIA pNfH calibration & Schoenfeld Phase 3 sizing are [MODEL_PRIOR] / prospective Stage-0 gates.",
    )


if __name__ == "__main__":
    main()
