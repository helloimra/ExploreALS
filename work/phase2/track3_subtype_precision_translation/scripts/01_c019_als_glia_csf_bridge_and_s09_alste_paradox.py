"""RUN-P2-T3-001: C019 Living-CSF ALS-Glia Bridge (rs3831317-resistant) & S09 Cortex-vs-Cord ALS-TE Fate Dissection."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from carbon_als.loaders import (  # noqa: E402
    assert_modality,
    assert_unique_donors,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_DIR = ROOT / "work" / "phase2" / "track3_subtype_precision_translation" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

GENES = [
    "CHIT1", "GPNMB", "CHI3L1", "CHI3L2", "SERPINA3", "C1QA", "C1QB", "C1QC", "TIMP1", "CD14",
    "LBP", "B2M", "LGALS3BP", "CCL2", "CXCL10", "JAK1", "JAK2", "JAK3", "TYK2", "STAT1", "STAT3",
    "AAK1", "GAK", "CGAS", "STING1", "DDX58", "IFIH1", "ISG15", "MX1", "OAS1", "IL6", "MMP9", "HDGFL2", "TARDBP",
]


def roc_auc_manual(y_true: np.ndarray, scores: np.ndarray) -> float:
    pos = scores[y_true == 1]
    neg = scores[y_true == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    u_stat, _ = stats.mannwhitneyu(pos, neg, alternative="two-sided")
    return float(u_stat / (len(pos) * len(neg)))


def load_nygc_subset(symbols: list[str]) -> pd.DataFrame:
    feat = pd.read_csv(resolve_dataset_path("DS001_FEAT", verify_hash=True))
    sc, ec = resolve_col(feat, "ucsd_label"), resolve_col(feat, "nygc_exact_versioned_ids")
    sub = feat.loc[feat[sc].isin(symbols) & feat[ec].notna()]
    ens_map = {str(r[ec]): str(r[sc]) for _, r in sub.iterrows() if ";" not in str(r[ec])}
    p_cnt = resolve_dataset_path("DS001_COUNTS", verify_hash=True)
    found: dict[str, np.ndarray] = {}
    with gzip.open(p_cnt, "rt", encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        samples = hdr[1:]
        libs = np.zeros(len(samples), dtype=np.float64)
        for ln in fh:
            pts = ln.rstrip("\n").split("\t")
            arr = np.fromiter((float(x) for x in pts[2:]), dtype=np.float64, count=len(samples))
            libs += arr
            if pts[1] in ens_map:
                found[ens_map[pts[1]]] = arr
    return pd.DataFrame({s: np.log2((a / np.maximum(libs, 1.0)) * 1e6 + 1.0) for s, a in found.items()}, index=samples)


def main() -> None:
    p_on = resolve_dataset_path("DS001_ONEILL", verify_hash=True)
    tc = read_xlsx_sparse_safe(p_on, "TableS1C", 2)
    th = read_xlsx_sparse_safe(p_on, "TableS1H", 2)
    assert_unique_donors(tc["PatientID"].dropna().tolist(), "ONEILL_TableS1C_Cortex")
    assert_unique_donors(th["PatientID"].dropna().tolist(), "ONEILL_TableS1H_SpinalCord")

    # 1. Clinical & paired Cortex-to-Cord fate matrix for ALS-TE (S09) and ALS-Glia (C019) — motor ALS + ALS+FTD only (exclude_pure_ftd=True)
    als_c = tc.loc[tc["Group"].isin(["ALS", "ALS+FTD"]) & tc["PatientSubtype"].astype(str).str.startswith("ALS-")].copy()
    als_h = th.loc[th["Group"].isin(["ALS", "ALS+FTD"]) & th["PatientSubtype"].astype(str).str.startswith("ALS-")].copy()
    paired = als_c.merge(als_h[["PatientID", "PatientSubtype"]], on="PatientID", suffixes=("_cortex", "_cord"))
    assert_unique_donors(paired["PatientID"].tolist(), "ONEILL_Paired_Cortex_Cord")
    ctab = pd.crosstab(paired["PatientSubtype_cortex"], paired["PatientSubtype_cord"]).to_dict(orient="index")

    clin_by_sub: dict[str, dict] = {}
    for sub_name, grp in als_c.groupby("PatientSubtype"):
        c9_s = grp["C9 repeat expanded, >=30"].astype(str).str.upper()
        c9_pos = int((c9_s.isin(["TRUE", "YES", "1", "EXPANDED", "POS", "POSITIVE"])).sum())
        c9_eval = int((~c9_s.isin(["NAN", "NA", "NONE", "UNKNOWN", ""])).sum())
        dur = pd.to_numeric(grp["Disease Duration in Months"], errors="coerce").dropna()
        age = pd.to_numeric(grp["Age at Symptom Onset"], errors="coerce").dropna()
        bulbar = int(grp["Site of Motor Onset Detail"].astype(str).str.contains("Bulbar", case=False, na=False).sum())
        clin_by_sub[str(sub_name)] = {
            "n_donors": int(len(grp)),
            "c9_pos": c9_pos,
            "c9_evaluated": c9_eval,
            "c9_pct": round(100.0 * c9_pos / max(c9_eval, 1), 2),
            "median_duration_months": round(float(dur.median()), 2) if len(dur) else None,
            "mean_age_onset_yr": round(float(age.mean()), 2) if len(age) else None,
            "bulbar_onset_pct": round(100.0 * bulbar / len(grp), 2),
        }

    # 2. NYGC donor-level subtype transcriptomics (motor ALS + ALS+FTD vs Control; exclude_pure_ftd=True)
    expr = load_nygc_subset(GENES)
    tb = read_xlsx_sparse_safe(p_on, "TableS1B", 2)
    tb = tb.loc[tb["Sample"].astype(str).isin(expr.index) & tb["Group"].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    tb["sample_stratum"] = np.where(
        tb["Group"].astype(str).str.upper().isin(["CTL", "CONTROL"]), "Control", tb["ALS Subtype"].astype(str)
    )
    als_tb = tb.loc[tb["Group"].isin(["ALS", "ALS+FTD"]) & tb["sample_stratum"].str.startswith("ALS-")].copy()
    multi_ids = als_tb.groupby("Patient ID")["Sample"].count()
    multi_donor_set = set(multi_ids[multi_ids >= 2].index)
    n_multi_ctx_donors = len(multi_donor_set)
    n_discordant_ctx_donors = int((als_tb.loc[als_tb["Patient ID"].isin(multi_donor_set)].groupby("Patient ID")["sample_stratum"].nunique() > 1).sum())

    tc_mot = tc.loc[tc["Group"].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    tc_map = tc_mot.assign(
        patient_stratum=np.where(
            tc_mot["Group"].astype(str).str.upper().isin(["CTL", "CONTROL"]), "Control", tc_mot["PatientSubtype"].astype(str)
        )
    )[["PatientID", "patient_stratum"]].drop_duplicates(subset=["PatientID"])
    m_ctx = tb[["Sample", "Patient ID"]].merge(expr, left_on="Sample", right_index=True)
    d_ctx = m_ctx.groupby("Patient ID", as_index=False)[list(expr.columns)].mean()
    d_ctx = d_ctx.merge(tc_map, left_on="Patient ID", right_on="PatientID", how="inner").rename(
        columns={"patient_stratum": "stratum"}
    )
    assert_unique_donors(d_ctx["Patient ID"].tolist(), "NYGC_Cortex_Unique_Donors")

    nygc_markers: dict[str, dict] = {}
    for g in expr.columns:
        gl = d_ctx.loc[d_ctx["stratum"] == "ALS-Glia", g].dropna()
        ox = d_ctx.loc[d_ctx["stratum"] == "ALS-Ox", g].dropna()
        te = d_ctx.loc[d_ctx["stratum"] == "ALS-TE", g].dropna()
        ct = d_ctx.loc[d_ctx["stratum"] == "Control", g].dropna()
        nygc_markers[g] = {
            "glia_vs_ox_diff": round(float(gl.mean() - ox.mean()), 4),
            "glia_vs_ox_p": float(stats.ttest_ind(gl, ox, equal_var=False).pvalue),
            "te_vs_ox_diff": round(float(te.mean() - ox.mean()), 4),
            "glia_vs_non_glia_als_auc": round(
                roc_auc_manual(
                    (d_ctx.loc[d_ctx["stratum"].str.startswith("ALS-"), "stratum"] == "ALS-Glia").astype(int).to_numpy(),
                    d_ctx.loc[d_ctx["stratum"].str.startswith("ALS-"), g].to_numpy(),
                ),
                4,
            ),
            "te_vs_ox_p": float(stats.ttest_ind(te, ox, equal_var=False).pvalue),
            "te_vs_ctrl_diff": round(float(te.mean() - ct.mean()), 4),
            "te_vs_ctrl_p": float(stats.ttest_ind(te, ct, equal_var=False).pvalue),
        }

    # 2b. MAJ-1 Empirical Within-ALS Subtype Specificity Test (ALS-Glia vs ALS-Ox+ALS-TE in Cortex & Paired Spinal Cord)
    tg = read_xlsx_sparse_safe(p_on, "TableS1G", 2)
    tg = tg.loc[tg["Sample"].astype(str).isin(expr.index) & tg["Group"].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    th_mot = th.loc[th["Group"].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    th_map = th_mot.assign(
        patient_stratum=np.where(
            th_mot["Group"].astype(str).str.upper().isin(["CTL", "CONTROL"]), "Control", th_mot["PatientSubtype"].astype(str)
        )
    )[["PatientID", "patient_stratum"]].drop_duplicates(subset=["PatientID"])
    m_cord = tg[["Sample", "Patient ID"]].merge(expr, left_on="Sample", right_index=True)
    d_cord = m_cord.groupby("Patient ID", as_index=False)[list(expr.columns)].mean().merge(
        th_map, left_on="Patient ID", right_on="PatientID", how="inner"
    ).rename(columns={"patient_stratum": "stratum"})
    assert_unique_donors(d_cord["Patient ID"].tolist(), "NYGC_SpinalCord_Unique_Donors")

    def within_als_subtype_roc(df_reg: pd.DataFrame, target_sub: pd.Series) -> dict[str, float | int]:
        z_r = pd.DataFrame(index=df_reg.index)
        ctrl_m = df_reg["stratum"] == "Control"
        for col in ["CHIT1", "CHI3L2", "GPNMB", "CHI3L1", "SERPINA3", "CXCL10", "STAT1", "STAT3", "TYK2"]:
            if col in df_reg.columns:
                mu = float(df_reg.loc[ctrl_m, col].mean())
                sd = float(df_reg.loc[ctrl_m, col].std(ddof=1))
                z_r[col] = (df_reg[col] - mu) / max(sd, 1e-6)
        z_r["chit_resc"] = np.maximum(z_r["CHIT1"], z_r["CHI3L2"])
        z_r["bridge_4gene"] = z_r[["chit_resc", "GPNMB", "CHI3L1", "SERPINA3"]].mean(axis=1)
        z_r["jak_stat_4gene"] = z_r[["CXCL10", "STAT1", "STAT3", "TYK2"]].mean(axis=1)
        z_r["dual_bridge_plus_cxcl10"] = 0.5 * z_r["bridge_4gene"] + 0.5 * z_r["CXCL10"]
        als_idx = target_sub.index
        y_true = target_sub.loc[als_idx].astype(str).str.startswith("ALS-Glia").astype(int).to_numpy()
        return {
            "n_als_donors": int(len(y_true)),
            "n_als_glia_positive": int(y_true.sum()),
            "auc_bridge_4gene": round(roc_auc_manual(y_true, z_r.loc[als_idx, "bridge_4gene"].to_numpy()), 4),
            "auc_cxcl10_alone": round(roc_auc_manual(y_true, z_r.loc[als_idx, "CXCL10"].to_numpy()), 4),
            "auc_jak_stat_4gene": round(roc_auc_manual(y_true, z_r.loc[als_idx, "jak_stat_4gene"].to_numpy()), 4),
            "auc_dual_bridge_plus_cxcl10": round(roc_auc_manual(y_true, z_r.loc[als_idx, "dual_bridge_plus_cxcl10"].to_numpy()), 4),
            "cxcl10_glia_vs_nonglia_welch_p": float(
                stats.ttest_ind(z_r.loc[als_idx, "CXCL10"][y_true == 1], z_r.loc[als_idx, "CXCL10"][y_true == 0], equal_var=False).pvalue
            ),
        }

    ctx_als_mask = d_ctx["stratum"].str.startswith("ALS-")
    cord_als_mask = d_cord["stratum"].str.startswith("ALS-")
    d_cord_paired_to_ctx = d_cord.merge(
        d_ctx.loc[ctx_als_mask, ["Patient ID", "stratum"]].rename(columns={"stratum": "cortical_true_subtype"}),
        on="Patient ID",
        how="inner",
    )
    cord_for_ctx_eval = pd.concat([d_cord.loc[d_cord["stratum"] == "Control"], d_cord_paired_to_ctx.drop(columns=["cortical_true_subtype"])], ignore_index=True)
    paired_ctx_labels = d_cord_paired_to_ctx.set_index(
        pd.RangeIndex(start=int((d_cord["stratum"] == "Control").sum()), stop=len(cord_for_ctx_eval))
    )["cortical_true_subtype"]
    within_als_specificity = {
        "cortex_predicting_cortical_ALS_Glia": within_als_subtype_roc(d_ctx, d_ctx.loc[ctx_als_mask, "stratum"]),
        "spinal_cord_predicting_cord_ALS_Glia": within_als_subtype_roc(d_cord, d_cord.loc[cord_als_mask, "stratum"]),
        "spinal_cord_predicting_true_cortical_ALS_Glia": within_als_subtype_roc(cord_for_ctx_eval, paired_ctx_labels),
    }

    # 3. DS045_TRAUT Living-CSF ALS-Glia Bridge & rs3831317 CHIT1-Null Rescue
    assert_modality("PROTEOMICS_CSF_DIA", "DS045_TRAUT")
    p45 = resolve_dataset_path("DS045_TRAUT", verify_hash=True)
    c2 = read_xlsx_sparse_safe(p45, "2-Cohort-Exp Characteristics", 2)
    dia = read_xlsx_sparse_safe(p45, "5-DIA Raw Data", 2)
    c2["dia_col"] = c2["_unnamed_col_0"].astype(str).str.replace(r"\.2$", "", regex=True).str.replace(r"\.(\d+)$", r"-\1", regex=True)
    assert_unique_donors(c2["ID"].tolist(), "DS045_DIA_259_Donors")
    pcol = resolve_col(dia, "Protein|Uniprot")
    dia["sym"] = dia[pcol].astype(str).str.split("|").str[0].str.strip()
    dia_sub = dia.loc[dia["sym"].isin(GENES)].groupby("sym")[c2["dia_col"].tolist()].first()

    csf_detect = {g: (g in dia_sub.index and int(dia_sub.loc[g].notna().sum()) > 20) for g in GENES}
    bridge_syms = [g for g in ["CHIT1", "CHI3L2", "GPNMB", "CHI3L1", "SERPINA3"] if g in dia_sub.index]
    ctrl_cols = c2.loc[c2["SymptomStatus"] == "Control", "dia_col"].tolist()
    z_df = pd.DataFrame(index=c2["dia_col"].tolist())
    for g in bridge_syms:
        s = pd.to_numeric(dia_sub.loc[g], errors="coerce")
        mu, sd = float(s[ctrl_cols].mean()), float(s[ctrl_cols].std(ddof=1))
        z_df[g] = (s - mu) / max(sd, 1e-6)
    z_df["status"] = c2.set_index("dia_col")["SymptomStatus"]
    z_df["bank"] = c2.set_index("dia_col")["TissueBank"]

    # Null-allele-proof bridge replaces raw z_CHIT1 with max(z_CHIT1, z_CHI3L2) when CHIT1 is missing/deficient
    z_df["chit_rescued"] = np.nanmax(np.vstack([z_df["CHIT1"].fillna(-3.0), z_df["CHI3L2"].fillna(0.0)]), axis=0)
    z_df["non_chit1_glia_z"] = z_df[["GPNMB", "CHI3L1", "CHI3L2", "SERPINA3"]].mean(axis=1)
    z_df["bridge_4prot_z"] = pd.concat([z_df["chit_rescued"], z_df["GPNMB"], z_df["CHI3L1"], z_df["SERPINA3"]], axis=1).mean(axis=1)

    symp_mask = z_df["status"].isin(["sALS", "C9orf72", "SOD1"])
    symp = z_df.loc[symp_mask].copy()
    glia_cut = float(z_df.loc[z_df["status"] == "Control", "non_chit1_glia_z"].quantile(0.90))
    chit1_discordant = symp.loc[(symp["non_chit1_glia_z"] >= glia_cut) & ((symp["CHIT1"].isna()) | (symp["CHIT1"] < 0.0))]

    sals_ctrl = z_df.loc[z_df["status"].isin(["sALS", "Control"])].dropna(subset=["bridge_4prot_z"])
    y_sc = (sals_ctrl["status"] == "sALS").astype(int).to_numpy()
    auc_bridge = roc_auc_manual(y_sc, sals_ctrl["bridge_4prot_z"].to_numpy())
    auc_chit1_raw = roc_auc_manual(y_sc, sals_ctrl["CHIT1"].fillna(-2.5).to_numpy())

    asym_c9 = z_df.loc[z_df["status"] == "C9orf72-Asymptomatic", "bridge_4prot_z"]
    symp_c9 = z_df.loc[z_df["status"] == "C9orf72", "bridge_4prot_z"]
    ctrl_br = z_df.loc[z_df["status"] == "Control", "bridge_4prot_z"]
    bridge_95_ctrl = float(ctrl_br.quantile(0.95))

    out = {
        "analysis_run_id": "RUN-P2-T3-001",
        "s09_paired_cortex_to_cord_fate": {
            "n_paired_als_donors": int(len(paired)),
            "crosstab_cortex_x_cord": ctab,
            "clinical_by_cortical_subtype": clin_by_sub,
            "intra_donor_multi_region_cortex_concordance": {
                "n_als_donors_with_2plus_cortical_regions": n_multi_ctx_donors,
                "n_discordant_across_frontal_motor_cortex": n_discordant_ctx_donors,
                "concordance_pct": round(
                    100.0 * (n_multi_ctx_donors - n_discordant_ctx_donors) / max(n_multi_ctx_donors, 1), 2
                ),
            },
        },
        "nygc_subtype_transcriptomics": nygc_markers,
        "c019_within_als_subtype_specificity_maj1": within_als_specificity,
        "ds045_csf_detection_34_genes": csf_detect,
        "c019_living_csf_als_glia_bridge": {
            "n_dia_total": int(len(z_df)),
            "control_95th_pct_cutoff_z": round(bridge_95_ctrl, 4),
            "sals_exceeding_ctrl95_pct": round(100.0 * float((z_df.loc[z_df["status"] == "sALS", "bridge_4prot_z"] > bridge_95_ctrl).mean()), 2),
            "c9_symp_exceeding_ctrl95_pct": round(100.0 * float((symp_c9 > bridge_95_ctrl).mean()), 2),
            "c9_asymp_exceeding_ctrl95_pct": round(100.0 * float((asym_c9 > bridge_95_ctrl).mean()), 2),
            "roc_auc_sals_vs_ctrl_bridge_4prot": round(auc_bridge, 4),
            "roc_auc_sals_vs_ctrl_chit1_only_with_nulls": round(auc_chit1_raw, 4),
            "sals_vs_ctrl_bridge_welch_p": float(stats.ttest_ind(z_df.loc[z_df["status"] == "sALS", "bridge_4prot_z"], ctrl_br, equal_var=False).pvalue),
            "c9_asymp_vs_ctrl_bridge_welch_p": float(stats.ttest_ind(asym_c9, ctrl_br, equal_var=False).pvalue),
            "chit1_null_or_low_despite_high_non_chit1_glia_in_symp_ALS": {
                "n_discordant": int(len(chit1_discordant)),
                "n_high_non_chit1_glia": int((symp["non_chit1_glia_z"] >= glia_cut).sum()),
                "pct_rescued_from_false_negative": round(
                    100.0 * len(chit1_discordant) / max(int((symp["non_chit1_glia_z"] >= glia_cut).sum()), 1), 2
                ),
            },
        },
    }
    (OUT_DIR / "run_p2_t3_001_glia_bridge_and_alste_fate.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("SAVED run_p2_t3_001_glia_bridge_and_alste_fate.json")


if __name__ == "__main__":
    main()
