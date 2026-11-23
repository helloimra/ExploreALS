"""Flagship Reproducer #8: EALS-037 — CELF5 Cryptic-Exon Steric SSO (Tier 2, Act #8 / Bio #9)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _flagship_common import ROOT, assert_close, assert_equal, has_raw_dataset, load_csv_by_key, load_csv_rows, load_json_any, print_audit_report


def main() -> None:
    port = load_csv_by_key("registries/phase4_unified_portfolio.csv", "accession_id")["EALS-037"]
    p4 = load_json_any("work/phase4_final_synthesis/outputs/run_p4_001_unified_portfolio.json")
    sso = {r["interval_id"]: r for r in load_csv_rows("registries/phase3b_denovo_sso_intervals.csv") if r["gene_symbol"] == "CELF5"}

    celf = p4["dn04_celf5_deep_profile"]
    ny_c = celf["celf5_nygc_multiregion"]["Spinal_Cord_Cervical"]
    ny_l = celf["celf5_nygc_multiregion"]["Spinal_Cord_Lumbar"]
    loeuf_cached = float(celf["gene_liability_profile"]["gnomad_v41_loeuf"])
    src_tag = "CACHED"
    if has_raw_dataset("data/genomics_splicing/gencode_v46/gnomad.v4.1.constraint_metrics.tsv") and has_raw_dataset("data/pharmacology_structures/bye2025/41593_2025_2118_MOESM3_ESM.xlsx"):
        import csv
        from carbon_als.loaders import read_xlsx_sparse_safe, resolve_col, resolve_dataset_path
        with (ROOT / "data/genomics_splicing/gencode_v46/gnomad.v4.1.constraint_metrics.tsv").open(encoding="utf-8") as fh:
            loeuf = next(
                float(r["lof.oe_ci.upper"])
                for r in csv.DictReader(fh, delimiter="\t")
                if r["gene"] == "CELF5" and r["mane_select"].lower() == "true"
            )
        t6 = read_xlsx_sparse_safe(resolve_dataset_path("DS005_BYE", verify_hash=True), "Table 6", header_row_1based=3)
        c_row = t6.loc[t6[resolve_col(t6, "genes")].astype(str).str.contains("CELF5", na=False)].iloc[0]
        assert_close("Raw Bye 2025 Table 6 CELF5 LeafCutter padj", float(c_row[resolve_col(t6, "Adjusted P-value")]), 0.00904, rtol=1e-2)
        assert_close("Raw-vs-Cached CELF5 gnomAD v4.1 LOEUF parity", loeuf, loeuf_cached, rtol=1e-3)
        src_tag = "RAW_RECOMPUTED"
    else:
        loeuf = loeuf_cached
    lead1 = sso["chr19:3278299-3278318(+)"]

    rrm2 = celf["celf5_afdb_and_3nmr_rrm2_truncation"]
    ph = celf["celf5_local_lsv_nmd_and_ejc_audit"]
    checks = [
        assert_equal("Portfolio Actionable Rank & Clean Lead #1", f"#{port['unified_rank']} ({port['lead_cis_interval_id']})", "#8 (chr19:3278299-3278318(+))"),
        assert_close("[MEASURED] NYGC Cervical RIN+GC OLS beta (p=0.0172)", float(ny_c["adj_beta_tdp_vs_ctrl"]), -0.4020, rtol=1e-3),
        assert_close("[MEASURED] Cervical mn_neur_z-residualized tSTMN2 neuronal tail %", float(ny_c["within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal"]), 1.90, rtol=0.02),
        assert_close("[MEASURED] Lumbar mn_neur_z-residualized tSTMN2 neuronal tail %", float(ny_l["within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal"]), 0.14, rtol=0.05),
        assert_close(f"[MEASURED:{src_tag}] gnomAD v4.1 MANE CELF5 LOEUF (pLI=1.00; Open Targets=0.216)", loeuf, 0.248, rtol=0.01),
        assert_equal("[STRUCTURALLY_INFERRED / SEQUENCE_CALCULATED] AF-Q8N6W0 / CELF1 3NMR RRM2 beta4 contacts & 108-nt transcript 18-nt EJC distance", f"{rrm2['severed_beta4_beta1_backbone_hbonds_le_3p5A']}/{ph['ejc_nmd_minigene_trap']['dist_ptc_to_ce_exon6_junction_nt']}nt", "5/18nt"),
        assert_close("[MEASURED] Brown 2022 i3Neuron Ribo-seq residual translation %", float(ph["empirical_residual_translation_pct"]), 38.6, rtol=1e-2),
        assert_close("[MEASURED] Zeng 2025 (PMID:40672339 preprint) NMD-inhibited CELF5 CE PSI % (FDR=0.0235)", float(ph["zeng2025_nmd_inhibition_cryptic_psi_pct"][1]), 44.6, rtol=1e-2),
        assert_equal("Lead #1 Clean >=2mm Off-Target Status", lead1["offtarget_safety_status"], "PASS_CLEAN_GE2MM"),
    ]
    print_audit_report(
        "EALS-037", "CELF5 Cryptic-Exon Steric SSO", checks,
        "Observed RNA/protein evidence — Brown local LSVs (CE +0.3471; upstream novel_acceptor +0.1218) / Ribo-seq (38.6% residual), Seddighi 2024 cryptic-peptide MS & Western blot (PMID:38277467), Zeng 2025 NMD rescue (24.8%->44.6%, FDR=0.0235, PMID:40672339), Bye Table 6 row 228 CELF5 cluster clu_25763_+ padj=0.00904 (PMID:41286450, N=77; coordinates unreported, overlap with this junction unresolved), & NYGC cervical RNA loss — are [MEASURED], while 5 AF-Q8N6W0/3NMR RRM2 contacts are structurally inferred and the 18-nt EJC distance is calculated for the conditional 108-nt transcript; Exon 1-7+ Nanopore phasing & spinal protein rescue are prospective gates.",
    )


if __name__ == "__main__":
    main()
