"""Flagship Reproducer #8: EALS-007 — IL1RL1 / sST2 Decoy Suppression (Tier 3 Deep-Dive, Act #22 / Bio #13)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _flagship_common import ROOT, assert_close, assert_equal, has_raw_dataset, load_csv_by_key, load_json_any, print_audit_report


def main() -> None:
    port = load_csv_by_key("registries/phase4_unified_portfolio.csv", "accession_id")["EALS-007"]
    t4 = load_json_any("work/phase2/track4_celltype_isoform_resolution/outputs/run_p2_t4_001_c007_il1rl1_and_c018_c1q.json")
    b3_sp = load_json_any("work/phase1_batches/batch_3/outputs/run_b3_003_singlecell_spatial.json")

    endo_cached = t4["c007_edinburgh_non_c9_endothelial"]["IL1RL1"]
    iso = t4["c007_gencode_v46_isoform_coordinates_1based_grch38"]
    sst2_exon = iso["sst2_soluble_short_transcripts"][0]["last_exon_1b"] + "(+)"
    zh_cached = next(
        float(x["avg_log2FC"])
        for x in b3_sp["zhang2026_spatial_d031"]["sheets"]["6d_MN_ALS_vs._HC"]
        if x["gene"] == "IL1RL1"
    )
    src_tag = "CACHED"
    if has_raw_dataset("data/transcriptomics/edinburgh_gse290359_pseudobulk") and has_raw_dataset("data/transcriptomics/d003_pseudobulk") and has_raw_dataset("data/transcriptomics/Zhang2026_Spatial_MOESM8.xlsx"):
        from carbon_als.loaders import load_edinburgh_pseudobulk, load_zhang2026_spatial, resolve_col
        ed_raw = load_edinburgh_pseudobulk("Endothelial", ["IL1RL1"], exclude_c9=True)["stats"]["IL1RL1"]
        zdf = load_zhang2026_spatial(["IL1RL1"])["mn_niche_df"]
        zh_spot = float(zdf[resolve_col(zdf, "avg_log2FC")].iloc[0])
        ed_diff, ed_p = float(ed_raw["diff_log2cpm"]), float(ed_raw["p_welch"])
        assert_close("Raw UMI-pooled vs library-mean Edinburgh IL1RL1 dlog2CPM", ed_diff, float(endo_cached["diff_log2cpm"]), rtol=1e-3)
        assert_close("Raw-vs-Cached Zhang Visium IL1RL1 log2FC parity", zh_spot, zh_cached, rtol=1e-5)
        src_tag = "RAW_RECOMPUTED"
    else:
        ed_diff, ed_p, zh_spot = float(endo_cached["diff_log2cpm"]), float(endo_cached["p_welch"]), zh_cached

    cys_aud = t4["c007_pdb_4kc3_structural_epitope"]["cys327_and_disulfide_audit"]
    pas_aud = t4["c007_cterminome_and_zone1_pas_modality_audit"]
    z1_lead = pas_aud["isoform_selective_rna_modality_zones_1based_grch38"]["zone_1_top_steric_moe_intervals"][0]
    checks = [
        assert_equal("Portfolio Actionable Rank & Decision", f"#{port['unified_rank']} ({port['decision']})", "#22 (KEEP_EXPLORATORY_UNPROVEN)"),
        assert_close(f"[MEASURED:{src_tag}] Edinburgh donor-collapsed non-C9 endothelial IL1RL1 dlog2CPM (n=7 Ctrl)", ed_diff, 3.1067, rtol=0.01),
        assert_close(f"[MEASURED:{src_tag}] Edinburgh endothelial Welch two-sided p (n=28: 21 non-C9 vs 7 Ctrl)", ed_p, 0.00698, rtol=0.02),
        assert_close(f"[MEASURED:{src_tag}] Zhang 2026 55-um Visium MN-niche spot log2FC (n=14/18 sections)", zh_spot, 3.76, rtol=0.02),
        assert_equal("[MEASURED] GENCODE v46 1-based soluble sST2 intron-8 polyA exon span", sst2_exon, "chr2:102343270-102346100(+)"),
        assert_equal("[MEASURED] PDB 4KC3 D1-D3 (aa 21-317) 5 closed disulfides; sequence-deduced 11th Cys327", f"{cys_aud['n_closed_disulfides']}/{cys_aud['cys327_is_odd_unpaired_thiol']}", "5/True"),
        assert_equal("[MEASURED] Zone 1 Intron-8 PAS #1 steric window (mRNA/50bp-SS 0/0; 25bp-SS 2mm=1)", f"{z1_lead['interval_id']}:{z1_lead['offtarget_status']}", "chr2:102346045-102346062(+):PASS_CLEAN_GE2MM"),
    ]
    if (ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00004kc3.cif").is_file():
        from carbon_als.mmcif_parser import load_mmcif_structure
        st = load_mmcif_structure(ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00004kc3.cif")
        checks.append(assert_equal("Raw mmCIF PDB 4KC3 IL-33:ST2 complex loaded", len(st.polymer_atoms) > 1000, True))

    print_audit_report(
        "EALS-007", "IL1RL1 / sST2 Decoy Suppression", checks,
        "Gene-level endothelial snRNA & 55-um Visium spot elevation are [MEASURED] (small n=7 Ctrl & spot-level BH=1.85e-9); soluble sST2 vs membrane ST2L attribution and oximetry-verified normoxic CSF stratification are prospective kill-gates.",
    )


if __name__ == "__main__":
    main()
