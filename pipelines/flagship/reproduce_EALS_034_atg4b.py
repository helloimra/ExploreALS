"""Flagship Reproducer #7: EALS-034 — ATG4B Cryptic-Exon Steric SSO (Tier 2, Act #7 / Bio #6)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _flagship_common import ROOT, assert_close, assert_equal, has_raw_dataset, load_csv_by_key, load_csv_rows, load_json_any, print_audit_report


def main() -> None:
    port = load_csv_by_key("registries/phase4_unified_portfolio.csv", "accession_id")["EALS-034"]
    f1 = load_json_any("work/phase3b_denovo_discovery/outputs/run_p3b_001_multimodal_funnel.json")
    dd = load_json_any("work/phase3b_denovo_discovery/outputs/run_p3b_004_targeted_deep_dive.json")
    sso = {r["interval_id"]: r for r in load_csv_rows("registries/phase3b_denovo_sso_intervals.csv") if r["gene_symbol"] == "ATG4B"}

    sp_cached = float(f1["funnel1_cryptic_splicing"]["spillman_fractions"]["ATG4B"]["homogenate_protein"]["log2fc"])
    ny_c = dd["nygc_multiregion_donor_analysis"]["regions"]["Spinal_Cord_Cervical"]["genes"]["ATG4B"]
    atg_3d = dd["atg4b_3d_truncation_2z0d"]
    src_tag = "CACHED"
    if has_raw_dataset("data/proteomics/spillman2026_d029_d030"):
        from carbon_als.loaders import load_spillman2026_fractions
        sp_lfc = float(load_spillman2026_fractions(["ATG4B"])["ATG4B"]["homogenate_protein"]["log2fc"])
        assert_close("Raw-vs-Cached Spillman ATG4B homogenate parity", sp_lfc, sp_cached, rtol=1e-5)
        src_tag = "RAW_RECOMPUTED"
    else:
        sp_lfc = sp_cached
    lead2 = sso["chr2:241668970-241668987(+)"]
    bench_3j = {x["interval_id"]: x for x in dd["atg4b_torres2024_3j_head_to_head_benchmark"]["head_to_head_intervals"]}
    b_3j = bench_3j["chr2:241668980-241668995(+)"]

    checks = [
        assert_equal("Portfolio Actionable Rank & Promoted Lead #2", f"#{port['unified_rank']} ({port['lead_cis_interval_id']})", "#7 (chr2:241668970-241668987(+))"),
        assert_close(f"[MEASURED:{src_tag}] Spillman C9-FTD homogenate DIA ATG4B log2FC (p=0.0227)", sp_lfc, -0.4905, rtol=1e-3),
        assert_close("[MEASURED] NYGC Cervical RIN+GC OLS beta (p=0.0010, n=197)", float(ny_c["adj_beta_tdp_vs_ctrl"]), -0.1642, rtol=1e-3),
        assert_close("[MEASURED] PDB 2Z0D deleted C-tail contacts to LC3B (<=4.5 A)", float(atg_3d["lc3b_patch_heavy_atom_contacts_le_4p5A"]), 27.0, rtol=1e-6),
        assert_equal("Promoted Lead #2 sp1=0, pm1_50=0, pm2_25=2 (CAUTION)", f"{lead2['spliced_1mm_genes']}/{lead2['premRNA_1mm_splice50bp_genes']}/{lead2['premRNA_2mm_splice25bp_pc_genes']}", "0/0/2"),
        assert_equal("Torres 2024 ASO 3J (16-nt 6-LNA/15-PS mixmer) sp1/pm1_50/pLI>=0.96 flags vs #2 (0/0/0)", f"{b_3j['spliced_1mm_genes']}/{b_3j['premRNA_1mm_splice50bp_genes']}/{len(b_3j['constrained_cns_offtarget_flags'])}", "10/18/5"),
        assert_close("[MODEL_PRIOR] Torres 2024 ASO 3J 6-LNA 1-mm heuristic Tm (C)", float(b_3j["est_1mm_duplex_tm_6lna_heuristic_c"]), 74.09, rtol=1e-3),
    ]
    if (ROOT / "data/pharmacology_structures/phase3b_pdb/pdb_00002z0d.cif").is_file():
        from carbon_als.mmcif_parser import load_mmcif_structure
        st = load_mmcif_structure(ROOT / "data/pharmacology_structures/phase3b_pdb/pdb_00002z0d.cif")
        checks.append(assert_equal("Raw mmCIF PDB 2Z0D ATG4B:LC3B complex loaded", len(st.polymer_atoms) > 1500, True))

    print_audit_report(
        "EALS-034", "ATG4B Cryptic-Exon Steric SSO", checks,
        "Brown CE/Ribo-seq, Spillman C9-FTD homogenate DIA (indirect cortical proxy), & PDB 2Z0D contacts are [MEASURED]; empirical iPSC-MN SSO rescue & single-alpha-MN BaseScope ISH are prospective kill-gates.",
    )


if __name__ == "__main__":
    main()
