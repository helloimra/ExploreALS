"""RUN-P3B-001: Genome-wide, proteome-wide & screen-wide unbiased discovery funnel across staged CarbonALS cohorts (0 ExploreALS overlap)."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (SRC, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _funnel_helpers import clean_json, compute_gc_adjusted_ba4_exc, load_explore_exclusions, scan_trautwig_deconfounded  # noqa: E402
from _funnel_rankings import build_funnel1_waterfall, build_funnel2_waterfall, scan_spillman_moesm5_sheet3  # noqa: E402
from carbon_als.loaders import (  # noqa: E402
    load_brown2022_splicing,
    load_bye2025_screen,
    load_edinburgh_pseudobulk,
    load_spillman2026_fractions,
    load_zhang2026_spatial,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

OUT_FP = ROOT / "work" / "phase3b_denovo_discovery" / "outputs" / "run_p3b_001_multimodal_funnel.json"
ADOPTED_GENES = ["ATG4B", "KALRN", "PTPRT", "CELF5", "PRUNE2", "PFKP", "TRAPPC12", "ELK1", "DLGAP1", "DPP6", "DPP10", "CFL1", "MAOB", "C5AR1"]
ADOPTED_DRUGS = ["PMX 205", "Lamotrigine", "Dolutegravir", "Acetylcysteine", "Coenzyme Q10", "L-Serine"]


def main() -> None:
    OUT_FP.parent.mkdir(parents=True, exist_ok=True)
    excl_genes, excl_drugs = load_explore_exclusions(ROOT)
    assert not (set(ADOPTED_GENES) & excl_genes), f"Gene overlap with ExploreALS: {set(ADOPTED_GENES) & excl_genes}"
    assert not ({d.lower() for d in ADOPTED_DRUGS} & excl_drugs), f"Drug overlap with ExploreALS: {{d.lower() for d in ADOPTED_DRUGS}} & excl_drugs"

    # Load genome-wide Zhang spatial MN first for cross-modal Funnel 1 + Funnel 3 waterfalls
    zh_all = load_zhang2026_spatial(None)["mn_niche_df"]
    zh_non = zh_all[~zh_all[resolve_col(zh_all, "gene")].astype(str).isin(excl_genes)].copy()
    fc_c, bh_c, p_c, g_c = resolve_col(zh_non, "avg_log2FC"), resolve_col(zh_non, "BH"), resolve_col(zh_non, "p_val"), resolve_col(zh_non, "gene")
    zh_up = int(((zh_non[bh_c] < 0.05) & (zh_non[fc_c] > 0)).sum())
    zh_dn = int(((zh_non[bh_c] < 0.05) & (zh_non[fc_c] < 0)).sum())
    zh_ns = int((~(zh_non[bh_c] < 0.05)).sum())
    assert (zh_up + zh_dn + zh_ns) == len(zh_non), "Rule 3B-1 Zhang MN partition mismatch!"

    # Funnel 1: Genome-wide Brown 2022 + Ma 2022 + header-resolved Spillman MOESM5 S3 + Bye sALS splicing
    br = load_brown2022_splicing()
    jdf, ribo = br["junctions_df"], br["riboseq_df"]
    ma5 = pd.read_excel(resolve_dataset_path("DS_CRYPTIC", verify_hash=True) / "Ma2022_41586_2022_4424_MOESM5_ESM.xlsx")
    bye_t6 = read_xlsx_sparse_safe(resolve_dataset_path("DS005_BYE", verify_hash=True), "Table 6", header_row_1based=3)
    f1_wf = build_funnel1_waterfall(jdf, ribo, ma5, bye_t6, zh_non, excl_genes)
    kalrn_fcx = scan_spillman_moesm5_sheet3(excl_genes)
    ribo_sub = ribo[ribo["gene_name"].isin(ADOPTED_GENES)].set_index("gene_name")[["log2FoldChange", "pvalue", "padj"]].to_dict(orient="index")
    ma_sub = ma5[ma5["Genes"].isin(ADOPTED_GENES)].to_dict(orient="records")
    bye_sals_sp = bye_t6[bye_t6[resolve_col(bye_t6, "Genes")].astype(str).isin(ADOPTED_GENES)].to_dict(orient="records")
    spill_dia = load_spillman2026_fractions(ADOPTED_GENES)

    # Funnel 2: Genome-wide Bryce-Smith 2025 APA + NYGC pathology + Zeng 2025 dPAS
    bs_fp = resolve_dataset_path("DS_BRYCE_APA", verify_hash=True)
    bs2 = pd.read_excel(bs_fp, sheet_name="Supplementary_Table_2")
    bs2_non = bs2[~bs2["gene_name"].astype(str).isin(excl_genes)].copy()
    ev_counts = bs2_non["event_type"].astype(str).value_counts().to_dict()
    assert sum(ev_counts.values()) == len(bs2_non), "Rule 3B-1 Funnel 2 APA partition mismatch!"
    bs5 = pd.read_excel(bs_fp, sheet_name="Supplementary_Table_5")
    bs6 = pd.read_excel(bs_fp, sheet_name="Supplementary_Table_6")
    bs6_gcol = resolve_col(bs6, "gene_name")
    zeng_fp = resolve_dataset_path("DS_ZENG_APA", verify_hash=True)
    f2_wf = build_funnel2_waterfall(bs2, bs5, bs6, zeng_fp, excl_genes)
    z_trappc12 = []
    for sh, gname in (("S1", "Gene_Name"), ("S2", "gene_name"), ("S3", "gene_name"), ("S4", "gene_name"), ("S5", "gene"), ("S6", "gene_name")):
        zdf = pd.read_excel(zeng_fp, sheet_name=sh)
        gc = resolve_col(zdf, gname)
        for _, r_z in zdf[zdf[gc].astype(str) == "TRAPPC12"].iterrows():
            z_trappc12.append({"sheet": sh, "row": r_z.to_dict()})

    # Funnel 3: Deconfounded Trautwig CSF + Set 1 TMTpro + Zhang MN + Full-Genome GC-adjusted BA4_Exc + Edinburgh
    csf_scan = scan_trautwig_deconfounded(excl_genes, ADOPTED_GENES)
    zh_lookup = zh_non[zh_non[g_c].isin(ADOPTED_GENES)][[g_c, fc_c, p_c, bh_c]].set_index(g_c).to_dict(orient="index")
    zh_top_dn = zh_non[(zh_non[bh_c] < 0.05) & (zh_non[fc_c] < 0)].sort_values(bh_c).head(15)[[g_c, fc_c, p_c, bh_c]].to_dict(orient="records")
    zh_top_up = zh_non[(zh_non[bh_c] < 0.05) & (zh_non[fc_c] > 0)].sort_values(bh_c).head(15)[[g_c, fc_c, p_c, bh_c]].to_dict(orient="records")
    gc_ba4 = compute_gc_adjusted_ba4_exc(ADOPTED_GENES)
    edin_exc = load_edinburgh_pseudobulk("Excitatory neuron", ADOPTED_GENES, exclude_c9=True)["stats"]
    edin_oli = load_edinburgh_pseudobulk("Oligodendrocyte", ADOPTED_GENES, exclude_c9=True)["stats"]

    # Funnel 4: Complete 107-drug Bye 2025 Screen Partition (all 6/6 unadopted positive p<0.05 hits adopted!)
    bye_df = load_bye2025_screen()
    is_ex_d = bye_df["drug"].str.lower().isin(excl_drugs)
    un_pos = (~is_ex_d) & (bye_df["p_ttest_2s"] < 0.05) & (bye_df["mean_paired_dmso_days"] > 0)
    un_neg = (~is_ex_d) & (bye_df["p_ttest_2s"] < 0.05) & (bye_df["mean_paired_dmso_days"] < 0)
    un_null = (~is_ex_d) & (bye_df["p_ttest_2s"] >= 0.05)
    assert int(is_ex_d.sum() + un_pos.sum() + un_neg.sum() + un_null.sum()) == 107
    assert set(bye_df[un_pos]["drug"].tolist()) == set(ADOPTED_DRUGS), "All 6/6 unadopted positive hits must match ADOPTED_DRUGS!"

    payload = clean_json({
        "analysis_run_id": "RUN-P3B-001",
        "excluded_explore_counts": {"n_genes": len(excl_genes), "n_drug_aliases": len(excl_drugs)},
        "funnel1_cryptic_splicing": {
            **f1_wf,
            "brown_junctions_selected": jdf[jdf["gene_name"].isin(ADOPTED_GENES)][["gene_name", "lsv_id", "deltaPSI", "FDR", "control_e_psi", "tdp_kd_e_psi", "chr", "strand", "paste_into_igv_junction", "paste_into_igv_exon", "junc_cat", "cryptic_junction"]].to_dict(orient="records"),
            "brown_riboseq": ribo_sub, "ma2022_moesm5": ma_sub, "spillman_kalrn_ce_fcx": kalrn_fcx,
            "bye2025_sals_splicing_t6": bye_sals_sp, "spillman_fractions": spill_dia,
        },
        "funnel2_cryptic_apa": {
            "partition_non_explore_events": ev_counts, **f2_wf,
            "bryce_smith_t2": bs2[bs2["gene_name"].isin(ADOPTED_GENES)][["le_id", "gene_name", "event_type", "n_exper_cryptic", "annot_status", "chromosome", "strand", "start_rep", "end_rep", "binding_start", "binding_end"]].to_dict(orient="records"),
            "bryce_smith_t5_nygc": bs5[bs5["gene_name"].isin(ADOPTED_GENES)].to_dict(orient="records"),
            "bryce_smith_t6_riboseq": bs6[bs6[bs6_gcol].isin(ADOPTED_GENES)].to_dict(orient="records"),
            "zeng2025_trappc12": z_trappc12,
        },
        "funnel3_csf_and_spatial": {
            "trautwig_deconfounded_dia": csf_scan,
            "zhang2026_mn_partition": {"total_non_explore": int(len(zh_non)), "bh05_up": zh_up, "bh05_down": zh_dn, "bh_ge_0p05": zh_ns},
            "zhang2026_mn_top15_down": zh_top_dn, "zhang2026_mn_top15_up": zh_top_up,
            "zhang2026_mn_selected": zh_lookup, "pineda_ba4_gc_adjusted": gc_ba4,
            "edinburgh_sals_non_c9": {"Excitatory": edin_exc, "Oligo": edin_oli},
        },
        "funnel4_bye2025_screen": {
            "partition_107_drugs": {"explore_adopted": int(is_ex_d.sum()), "unadopted_pos_p05": int(un_pos.sum()), "unadopted_neg_p05": int(un_neg.sum()), "unadopted_null": int(un_null.sum())},
            "unadopted_positive_p05_hits": bye_df[un_pos].to_dict(orient="records"),
        },
    })
    OUT_FP.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    print("RUN-P3B-001 OK:", json.dumps({"f1": f1_wf["partition_non_explore_genes"], "f2": f2_wf["riboseq_event_partition"], "f3_csf": csf_scan["partition_counts"], "f4": payload["funnel4_bye2025_screen"]["partition_107_drugs"]}, indent=2))


if __name__ == "__main__":
    main()
