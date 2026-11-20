"""Flagship Reproducer #5: EALS-002 — STMN2 Cryptic-Exon-2a Steric SSO (Tier 2, Act #5 / Bio #2)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _flagship_common import assert_close, assert_equal, has_raw_dataset, load_csv_by_key, load_csv_rows, load_json_any, print_audit_report


def main() -> None:
    port = load_csv_by_key("registries/phase4_unified_portfolio.csv", "accession_id")["EALS-002"]
    sp_b1 = load_json_any("work/phase1_batches/batch_1/outputs/run_b1_001_splicing_apa.json")
    pr_b1 = load_json_any("work/phase1_batches/batch_1/outputs/run_b1_004_proteomics.json")
    ot_rows = {r["interval_id"]: r for r in load_csv_rows("registries/phase3_sso_offtarget_audit.csv") if r["gene_symbol"] == "STMN2"}

    dpsi_cached = float(sp_b1["brown2022"]["i3neuron_splicing_MOESM11"]["STMN2"][0]["deltaPSI"])
    hom_cached = float(pr_b1["ds029_spillman2026_frctx_synaptosome_multiomics"]["genes"]["STMN2"]["frctx_homogenate"]["recomputed_log2fc"])
    src_tag = "CACHED"
    if has_raw_dataset("data/genomics_splicing/tdp43_cryptic_sources") and has_raw_dataset("data/proteomics/spillman2026_d029_d030"):
        from carbon_als.loaders import load_brown2022_splicing, load_spillman2026_fractions, resolve_col
        jdf = load_brown2022_splicing(["STMN2"])["junctions_df"]
        dpsi_obs = float(jdf.loc[jdf[resolve_col(jdf, "cryptic_junction")].astype(bool), resolve_col(jdf, "deltaPSI")].max())
        hom_obs = float(load_spillman2026_fractions(["STMN2"])["STMN2"]["homogenate_protein"]["log2fc"])
        assert_close("Raw-vs-Cached Brown STMN2 dPSI parity", dpsi_obs, dpsi_cached, rtol=1e-5)
        assert_close("Raw-vs-Cached Spillman STMN2 homogenate parity", hom_obs, hom_cached, rtol=1e-5)
        src_tag = "RAW_RECOMPUTED"
    else:
        dpsi_obs, hom_obs = dpsi_cached, hom_cached
    pct_loss = 100.0 * ((2.0 ** hom_obs) - 1.0)
    lead2 = ot_rows["chr8:79616829-79616846(+)"]

    checks = [
        assert_equal("Portfolio Actionable Rank & Biological Rank #2", f"Act #{port['unified_rank']} ({port['decision']})", "Act #5 (KEEP_CORE)"),
        assert_close(f"[MEASURED:{src_tag}] Brown 2022 STMN2 Exon-2a cryptic junction dPSI", dpsi_obs, 0.4820, rtol=1e-3),
        assert_close(f"[MEASURED:{src_tag}] Spillman C9-FTD homogenate STMN2 log2FC (p=0.014, padj=0.113)", hom_obs, -0.4825, rtol=1e-3),
        assert_close("[MEASURED] Derived cortical STMN2 protein change % (2^log2FC - 1)", pct_loss, -28.43, rtol=0.01),
        assert_equal("Promoted Lead #2 Clean >=2mm Off-Target Status", lead2["offtarget_safety_status"], "PASS_CLEAN_GE2MM"),
    ]
    print_audit_report(
        "EALS-002", "STMN2 Cryptic-Exon-2a Steric SSO", checks,
        "Human tSTMN2 pathology & iPSC-MN rescue are [MEASURED] (Bio #2; Spillman -28.4% sits at nominal p=0.014, FDR=0.113 in n=20 C9-FTD cortices); Stage 2 multiplex dosing & ANQUR interim pNfH dissociation are gated separately.",
    )


if __name__ == "__main__":
    main()
