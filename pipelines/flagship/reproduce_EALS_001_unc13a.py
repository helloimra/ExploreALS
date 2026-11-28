"""Flagship Reproducer #1: EALS-001 — UNC13A Cryptic-Exon Steric SSO (Tier 2, Act #1 / Bio #1)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _flagship_common import assert_close, assert_equal, has_raw_dataset, load_csv_by_key, load_csv_rows, load_json_any, print_audit_report


def main() -> None:
    port = load_csv_by_key("registries/phase4_unified_portfolio.csv", "accession_id")["EALS-001"]
    sp_b1 = load_json_any("work/phase1_batches/batch_1/outputs/run_b1_001_splicing_apa.json")
    pr_b1 = load_json_any("work/phase1_batches/batch_1/outputs/run_b1_004_proteomics.json")
    ot_rows = {r["interval_id"]: r for r in load_csv_rows("registries/phase3_sso_offtarget_audit.csv") if r["gene_symbol"] == "UNC13A"}

    ce_cached = max(float(x["deltaPSI"]) for x in sp_b1["brown2022"]["i3neuron_splicing_MOESM11"]["UNC13A"] if x.get("cryptic_junction"))
    syn_cached = float(pr_b1["ds029_spillman2026_frctx_synaptosome_multiomics"]["genes"]["UNC13A"]["frctx_synaptosome"]["recomputed_log2fc"])
    src_tag = "CACHED"
    if has_raw_dataset("data/genomics_splicing/tdp43_cryptic_sources") and has_raw_dataset("data/proteomics/spillman2026_d029_d030"):
        from carbon_als.loaders import load_brown2022_splicing, load_spillman2026_fractions, resolve_col
        jdf = load_brown2022_splicing(["UNC13A"])["junctions_df"]
        ce_inc = float(jdf.loc[jdf[resolve_col(jdf, "cryptic_junction")].astype(bool), resolve_col(jdf, "deltaPSI")].max())
        syn_lfc = float(load_spillman2026_fractions(["UNC13A"])["UNC13A"]["synaptosome_protein"]["log2fc"])
        assert_close("Raw-vs-Cached Brown UNC13A dPSI parity", ce_inc, ce_cached, rtol=1e-5)
        assert_close("Raw-vs-Cached Spillman UNC13A synaptosome parity", syn_lfc, syn_cached, rtol=1e-5)
        src_tag = "RAW_RECOMPUTED"
    else:
        ce_inc, syn_lfc = ce_cached, syn_cached
    lead2 = ot_rows["chr19:17642537-17642554(-)"]

    checks = [
        assert_equal("Portfolio Actionable Rank & Biological Rank #1", f"Act #{port['unified_rank']} ({port['decision']})", "Act #1 (KEEP_CORE)"),
        assert_close(f"[MEASURED:{src_tag}] Brown 2022 UNC13A cryptic junction dPSI", ce_inc, 0.4632, rtol=1e-3),
        assert_close(f"[MEASURED:{src_tag}] Spillman 2026 C9-FTD synaptosome UNC13A log2FC", syn_lfc, -0.2496, rtol=1e-3),
        assert_equal("Promoted Lead #2 Harmonized Off-Target Status (pm2_25=4 -> CAUTION)", f"{lead2['offtarget_safety_status']}:{lead2['premRNA_2mm_splice25bp_pc_genes']}", "CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED:4"),
        assert_close("Promoted Lead #2 sp0+sp1+pm1_50+bulge+sub18 hits", float(int(lead2["spliced_0mm_genes"]) + int(lead2["spliced_1mm_genes"]) + int(lead2["premRNA_1mm_splice50bp_genes"]) + int(lead2["bulge_1nt_steric_pc_genes"]) + int(lead2["sub18_core_steric_pc_genes"])), 0.0, rtol=1e-6),
    ]
    print_audit_report(
        "EALS-001", "UNC13A Cryptic-Exon Steric SSO", checks,
        "Human rs12973192/rs12608932 genetics, TDP-43 CE pathology, and human cortical/spinal MN synaptic rescue (>30% protein threshold; Keuss 2026 Nature 10.1038/s41586-026-11256-2) are [MEASURED] (Bio #1; ~43% NFE A/A modulates magnitude without conferring exemption); SantaLucia Tm & Stage 2 6-9 mg multiplex dosing are [MODEL_PRIOR].",
    )


if __name__ == "__main__":
    main()
