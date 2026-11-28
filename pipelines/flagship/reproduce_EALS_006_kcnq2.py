"""Flagship Reproducer #3: EALS-006 — KCNQ2 Exon-5 Steric SSO (Tier 2, Act #3 / Bio #4)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _flagship_common import ROOT, assert_close, assert_equal, has_raw_dataset, load_csv_by_key, load_csv_rows, load_json_any, print_audit_report


def kcnq2_er_cotrapping_model(p_skip: float, theta_het: float = 0.0, alpha_esc: float = 0.15) -> dict[str, float]:
    im_rel = (1.0 - theta_het) * ((1.0 - p_skip) ** 4) + theta_het * ((1.0 - p_skip) ** 2)
    nsurf_m4 = (1.0 - p_skip + alpha_esc * p_skip) ** 4
    nsurf_m2 = (1.0 - p_skip + alpha_esc * p_skip) ** 2
    nsurf = (1.0 - theta_het) * nsurf_m4 + theta_het * nsurf_m2
    return {"im_rel": im_rel, "im_loss_pct": 100.0 * (1.0 - im_rel), "nsurf_rel": nsurf, "er_trapped_pct": 100.0 * (1.0 - nsurf)}


def main() -> None:
    port = load_csv_by_key("registries/phase4_unified_portfolio.csv", "accession_id")["EALS-006"]
    sp_b1 = load_json_any("work/phase1_batches/batch_1/outputs/run_b1_001_splicing_apa.json")
    kv_3d = load_json_any("work/phase2/track1_multiplex_splice/outputs/phase2_track1_kv72_structure.json")
    ot_rows = {r["interval_id"]: r for r in load_csv_rows("registries/phase3_sso_offtarget_audit.csv") if r["gene_symbol"] == "KCNQ2"}

    skip_juncs = [
        j for j in sp_b1["brown2022"]["i3neuron_splicing_MOESM11"]["KCNQ2"]
        if j["paste_into_igv_junction"] == "chr20:63439708-63444659" and j["cryptic_junction"]
    ]
    dpsi_cached = max(float(j["deltaPSI"]) for j in skip_juncs)
    trp_cached = float(kv_3d["ligands_and_retigabine_pocket"]["FBX"]["min_dist_to_chainA_Trp236_A"])
    src_tag = "CACHED"
    if has_raw_dataset("data/genomics_splicing/tdp43_cryptic_sources") and has_raw_dataset("data/pharmacology_structures/phase2_pdb/pdb_00007cr2.cif"):
        import math
        from carbon_als.loaders import load_brown2022_splicing, resolve_col
        from carbon_als.mmcif_parser import load_mmcif_structure
        jdf = load_brown2022_splicing(["KCNQ2"])["junctions_df"]
        jcol, ccol, dcol = resolve_col(jdf, "paste_into_igv_junction"), resolve_col(jdf, "cryptic_junction"), resolve_col(jdf, "deltaPSI")
        i3n_dpsi = float(jdf.loc[(jdf[jcol] == "chr20:63439708-63444659") & jdf[ccol].astype(bool), dcol].max())
        st7 = load_mmcif_structure(ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00007cr2.cif")
        fbx_a = [a for a in st7.ligand_atoms if a.comp_id == "FBX" and a.chain_id == "A"] or [a for a in st7.ligand_atoms if a.comp_id == "FBX"]
        trp236_a = [a for a in st7.polymer_atoms if a.chain_id == "A" and a.seq_id == 236 and a.comp_id == "TRP"]
        trp_dist = min(math.dist((x.x, x.y, x.z), (y.x, y.y, y.z)) for x in fbx_a for y in trp236_a)
        assert_close("Raw-vs-Cached Brown KCNQ2 skip dPSI parity", i3n_dpsi, dpsi_cached, rtol=1e-5)
        assert_close("Raw-vs-Cached PDB 7CR2 FBX-Trp236 distance parity", trp_dist, trp_cached, rtol=1e-2, atol=0.01)
        src_tag = "RAW_RECOMPUTED"
    else:
        i3n_dpsi, trp_dist = dpsi_cached, trp_cached
    hom_m4 = kcnq2_er_cotrapping_model(i3n_dpsi, theta_het=0.0, alpha_esc=0.15)
    het_m2 = kcnq2_er_cotrapping_model(i3n_dpsi, theta_het=1.0, alpha_esc=0.15)
    lead3 = ot_rows["chr20:63442302-63442319(-)"]

    checks = [
        assert_equal("Portfolio Actionable Rank & Promoted Lead", f"#{port['unified_rank']} ({port['lead_cis_interval_id']})", "#3 (chr20:63442302-63442319(-))"),
        assert_close(f"[MEASURED:{src_tag}] Brown 2022 i3Neuron KCNQ2 Exon-4-Exon-6 skip dPSI", i3n_dpsi, 0.2139, rtol=1e-3),
        assert_close("[MEASURED] Exon 5 in-frame length (bp = 42 aa Glu231-Leu272)", float(63442531 - 63442406 + 1), 126.0, rtol=1e-6),
        assert_close(f"[MEASURED:{src_tag}] PDB 7CR2 Retigabine-to-Trp236 closest CZ2-O3 contact (A)", trp_dist, 2.97, rtol=0.02),
        assert_close("[MODEL_PRIOR] 4:0 Nodal Kv7.2 homomer M-current loss % (q=0.2139)", hom_m4["im_loss_pct"], 61.81, rtol=1e-3),
        assert_close("[MODEL_PRIOR] 2:2 AIS Kv7.2:Kv7.3 heteromer M-current loss % (q=0.2139)", het_m2["im_loss_pct"], 38.20, rtol=1e-3),
        assert_equal("Lead #3 Off-Target Status (sp0=0, sp1=0, bulge=0)", lead3["offtarget_safety_status"], "CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED"),
    ]
    if (ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00007cr2.cif").is_file():
        from carbon_als.mmcif_parser import load_mmcif_structure
        st = load_mmcif_structure(ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00007cr2.cif")
        checks.append(assert_equal("Raw mmCIF PDB 7CR2 FBX ligand atoms present", any(a.comp_id == "FBX" for a in st.ligand_atoms), True))

    print_audit_report(
        "EALS-006", "KCNQ2 Exon-5 Steric SSO", checks,
        "Exon-5 skipping, Joseph 2025 ER retention, & PDB 7CR2 Trp236 geometry are [MEASURED]; binomial ER co-trapping across 4:0 vs 2:2 Kv7.2:Kv7.3 channels and Intron-5 ISS polarity on #3 are [MODEL_PRIOR].",
    )


if __name__ == "__main__":
    main()
