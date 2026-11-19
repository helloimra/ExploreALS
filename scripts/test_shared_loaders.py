"""Unit and integration self-tests for src/carbon_als/ (loaders, mmcif_parser, skill_cli, allostery_pkpd)."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from carbon_als.allostery_pkpd import (  # noqa: E402
    calibrate_bexi_mwc_to_empirical,
    compute_cd38_cadpr_dilution_and_audit_bound,
    hetero_octamer_tlock_inhibition,
    simulate_coupled_pikfyve_casm_pkpd,
    simulate_pulsed_vs_continuous_pkpd,
    sweep_coupled_pikfyve_casm_sensitivity,
    sweep_pulsed_pkpd_sensitivity,
    sweep_sarm1_mwc_threshold_synergy,
)
from carbon_als.splice_design import (  # noqa: E402
    duplex_tm_moe,
    duplex_tm_moe_physiological,
    score_target_intervals,
)
from carbon_als.loaders import (  # noqa: E402
    assert_1based_exon_coords,
    assert_modality,
    assert_unique_donors,
    download_https_structure,
    load_brown2022_splicing,
    load_bye2025_screen,
    load_edinburgh_pseudobulk,
    load_oneill2025_subtypes,
    load_pineda2024_pseudobulk,
    load_spillman2026_fractions,
    load_zhang2026_spatial,
    resolve_dataset_path,
)
from carbon_als.mmcif_parser import (  # noqa: E402
    ca_rmsd_kabsch,
    load_mmcif_structure,
    score_pocket_steric_complementarity,
)
from carbon_als.skill_cli import (  # noqa: E402
    filter_offtarget_liabilities,
    parse_json_ignoring_banner,
    run_skill_cli_to_file,
    sanitize_chembl_filters,
)


def main() -> None:
    # 1. Anti-pseudoreplication guard blocks duplicate donors
    try:
        assert_unique_donors(["Donor1", "Donor2", "Donor1"], "unit_test")
        raise AssertionError("Expected assert_unique_donors to fail on duplicate donor!")
    except AssertionError as exc:
        assert "PSEUDOREPLICATION BLOCKED" in str(exc)

    # 2. Modality guard blocks bogus modality tags
    try:
        assert_modality("FAKE_ASSAY", "unit_test")
        raise AssertionError("Expected assert_modality to fail on invalid modality!")
    except ValueError:
        pass

    # 3. Brown 2022 loader verifies multiplex splice targets
    b22 = load_brown2022_splicing(["KCNQ2", "UNC13A", "STMN2", "G2E3"])
    assert b22["splicing_modality"] == "RNA_SPLICING_MAJIQ" and len(b22["junctions_df"]) >= 4

    # 4. Bye 2025 loader verifies bit-exact Riluzole #1 (+3.959 d)
    bye = load_bye2025_screen()
    assert len(bye) == 107 and bye.iloc[0]["drug"] == "Riluzole"
    assert abs(float(bye.iloc[0]["mean_paired_dmso_days"]) - 3.959) < 0.002

    # 5. Spillman 2026 loader separates Synaptosome vs Homogenate DIA protein from MOESM2 RNA-seq
    sp = load_spillman2026_fractions(["TFRC", "G2E3", "CHMP2B"])
    assert sp["TFRC"]["synaptosome_protein"]["modality"] == "PROTEOMICS_DIA"
    assert sp["G2E3"].get("synaptosome_protein") is None
    assert sp["G2E3"]["homogenate_rnaseq"]["modality"] == "RNASEQ_DESEQ2"

    # 6. 1-based closed exon coordinate guard blocks 0-based BED start offset
    assert assert_1based_exon_coords(63442406, 63442531, 63442406, 63442531, "KCNQ2_Ex5") == 126
    try:
        assert_1based_exon_coords(63442405, 63442531, 63442406, 63442531, "KCNQ2_Ex5")
        raise AssertionError("Expected 0-based BED start 63442405 to be blocked!")
    except AssertionError as exc:
        assert "ZERO_BASED_BED_OFFSET_BLOCKED" in str(exc)

    # 7. HTTPS-only structural downloader blocks passive FTP URLs
    try:
        download_https_structure("ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/mmCIF/7cr2.cif.gz", ROOT / "tmp.cif")
        raise AssertionError("Expected ftp:// URL to be blocked!")
    except ValueError as exc:
        assert "FTP_OR_INSECURE_URL_BLOCKED" in str(exc)

    # 8. Quote-safe mmCIF parser captures polymeric covalent HETATM VI3 at SARM1 seq=311 in 7DJT + quoted O4' in 9TZY
    s_7djt = load_mmcif_structure(ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00007djt.cif")
    mod_311 = [a for a in s_7djt.modified_polymer_atoms if a.chain_id == "A" and a.seq_id == 311]
    assert mod_311 and mod_311[0].comp_id == "VI3", "Failed to capture covalent Cys311 HETATM VI3 in 7DJT!"
    s_9tzy = load_mmcif_structure(ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00009tzy.cif")
    assert any(a.comp_id == "A1JZ0" for a in s_9tzy.ligand_atoms), "Failed to capture BEXi adduct A1JZ0 in 9TZY!"
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".cif", delete=False, encoding="utf-8") as tf:
        tf.write(
            "data_test\nloop_\n_atom_site.group_PDB\n_atom_site.label_atom_id\n_atom_site.label_comp_id\n"
            "_atom_site.auth_asym_id\n_atom_site.label_seq_id\n_atom_site.auth_seq_id\n"
            "_atom_site.Cartn_x\n_atom_site.Cartn_y\n_atom_site.Cartn_z\n"
            "HETATM \"O4'\" 1AD A . 901 1.0 2.0 3.0\n"
        )
        tf_path = Path(tf.name)
    try:
        s_q = load_mmcif_structure(tf_path)
        assert len(s_q.ligand_atoms) == 1 and s_q.ligand_atoms[0].atom_name == "O4'"
    finally:
        tf_path.unlink(missing_ok=True)

    # 9. Kabsch RMSD + 3D pocket steric/off-target scorer
    pts = np.array([[0.0, 0.0, 0.0], [8.5, 0.0, 0.0], [0.0, 8.5, 0.0], [0.0, 0.0, 8.5]])
    tiny_pts = np.array([[0.0, 0.0, 0.0], [4.5, 0.0, 0.0], [0.0, 4.5, 0.0], [0.0, 0.0, 4.5]])
    assert ca_rmsd_kabsch(pts, pts + 2.5) < 1e-9
    clean_sc = score_pocket_steric_complementarity(pts, 230.0, -85.1, min_offtarget_ic50_nm=5000.0)
    promisc_sc = score_pocket_steric_complementarity(pts, 230.0, -85.1, min_offtarget_ic50_nm=15.0)
    clash_sc = score_pocket_steric_complementarity(tiny_pts, 230.0, -85.1, min_offtarget_ic50_nm=5000.0)
    assert clean_sc["offtarget_clean_ge_1uM"] is True and clean_sc["pocket_selectivity_score"] > promisc_sc["pocket_selectivity_score"] > 0.0
    assert clash_sc["steric_clash_flag"] is True and clash_sc["pocket_selectivity_score"] == 0.0

    # 10. ChEMBL __range sanitizer & off-target liability stripper
    sanitized = sanitize_chembl_filters(["molecule_properties__mw_freebase__range=175,285", "max_phase=4"])
    assert sanitized == ["molecule_properties__mw_freebase__gte=175", "molecule_properties__mw_freebase__lte=285", "max_phase=4"]
    kept = filter_offtarget_liabilities(
        [{"molecule_chembl_id": "CHEMBL_A"}, {"molecule_chembl_id": "CHEMBL_B"}],
        {"CHEMBL_A": 12.0, "CHEMBL_B": 4500.0},
    )
    assert len(kept) == 1 and kept[0]["molecule_chembl_id"] == "CHEMBL_B"

    # 11. Empirical 6-site MWC calibration (Leahey 2025 8.6x ratio) & heterozygous WT:GoF SARM1 octamer
    cal = calibrate_bexi_mwc_to_empirical(target_ic50_over_peak_ratio=8.6, target_peak_fold=2.8, n_sites=6)
    assert abs(cal["ic50_to_peak_dose_ratio"] - 8.6) < 0.4 and cal["peak_fold_activation"] > 2.4
    wt_hom = hetero_octamer_tlock_inhibition(1.0, gof_allele_fraction=0.0)
    het_gof = hetero_octamer_tlock_inhibition(1.0, gof_allele_fraction=0.5)
    hom_gof = hetero_octamer_tlock_inhibition(1.0, gof_allele_fraction=1.0)
    assert wt_hom["percent_inhibition"] > het_gof["percent_inhibition"] > hom_gof["percent_inhibition"] == 0.0

    # 12. Pulsed vs continuous PK/PD simulation verifies reduced vacuolation stress on 48h-on/120h-off schedule
    cont = simulate_pulsed_vs_continuous_pkpd([float(h) for h in range(0, 336, 12)], 336.0, 4.0, 5.0, 4.5)
    pulsed = simulate_pulsed_vs_continuous_pkpd([0.0, 12.0, 24.0, 36.0, 168.0, 180.0, 192.0, 204.0], 336.0, 4.0, 5.0, 4.5)
    assert pulsed["end_vacuolation_stress_index"] < cont["end_vacuolation_stress_index"]

    # 13. ParsedMMCIF.residue_groups() groups chain/residue atoms (including modified covalent Cys311 VI3 when requested)
    rg_std = s_7djt.residue_groups(chain_id="A", include_modified=False)
    rg_mod = s_7djt.residue_groups(chain_id="A", include_modified=True)
    assert ("A", 311, "VI3") not in rg_std and ("A", 311, "VI3") in rg_mod

    # 14. run_skill_cli_to_file(use_cache=True) serves valid cached JSON without spawning a child uv process
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as cf:
        cf.write('{"cached_ok": true, "n": 42}')
        cf_path = Path(cf.name)
    try:
        cached_res = run_skill_cli_to_file(ROOT / "nonexistent_script.py", ["noop"], cf_path, use_cache=True)
        assert cached_res == {"cached_ok": True, "n": 42}
    finally:
        cf_path.unlink(missing_ok=True)

    # 15. sweep_pulsed_pkpd_sensitivity() quantifies 81-point kill-gate pass rate (79.0% on q48h vs 0.0% continuous BID)
    sw_q48 = sweep_pulsed_pkpd_sensitivity([float(h) for h in range(0, 336, 48)], 336.0, 6.5, 4.5, 1.5)
    sw_bid = sweep_pulsed_pkpd_sensitivity([float(h) for h in range(0, 336, 12)], 336.0, 3.89, 4.5, 1.5)
    assert sw_q48["n_parameter_combinations"] == 81 and sw_q48["killgate_pass_rate"] > 0.75 and sw_q48["end_vac_median"] < 0.05
    assert sw_bid["killgate_pass_rate"] == 0.0 and sw_bid["end_vac_median"] > 0.40

    # 16. v0.4.0 O'Neill pure-FTD guard, Zhang 2026 spatial loader, Edinburgh & Pineda donor-aware snRNA loaders
    on_motor = load_oneill2025_subtypes(exclude_pure_ftd=True)
    on_pooled = load_oneill2025_subtypes(exclude_pure_ftd=False)
    assert on_motor["n_non_discordant_cases"] == 303 and on_motor["subtype_counts"]["ALS-TE"] == 41
    assert on_pooled["subtype_counts"]["ALS-TE"] == 66  # 41 motor ALS/ALS+FTD + 25 pure FTD
    zh = load_zhang2026_spatial(["IL1RL1", "C1QA", "C1QB", "C1QC"])
    assert zh["modality"] == "SPATIAL_VISIUM_PSEUDOBULK" and not zh["tdp43_niche_df"].empty
    ed = load_edinburgh_pseudobulk("Endothelial", ["IL1RL1", "IL33"], region="donor_collapsed")
    assert ed["modality"] == "SNRNA_PSEUDOBULK_LOG2CPM" and len(ed["donor_df"]) >= 25
    ed_nc9 = load_edinburgh_pseudobulk("Excitatory neuron", ["ELK1"], region="donor_collapsed", exclude_c9=True)
    assert len(ed_nc9["donor_df"]) == 32 and "SD006/17" not in set(ed_nc9["donor_df"]["donor_id"]), "Donor-level C9 exclusion failed on SD006/17!"
    pi = load_pineda2024_pseudobulk("BA4", "Excitatory", ["CHMP7", "CHMP2B", "FBXL5"])
    assert pi["modality"] == "SNRNA_PSEUDOBULK_LOG2CPM" and len(pi["donor_df"]) == 32

    # 17. v0.4.1 Directory SHA-256 tree verification passes on multi-file staged directories (DS_CRYPTIC, DS029_SPILL, DS_PDB)
    p_cryp = resolve_dataset_path("DS_CRYPTIC", verify_hash=True)
    p_sp29 = resolve_dataset_path("DS029_SPILL", verify_hash=True)
    p_pdb1 = resolve_dataset_path("DS_PDB", verify_hash=True)
    assert p_cryp.is_dir() and p_sp29.is_dir() and p_pdb1.is_dir()

    # 18. v0.4.1 parse_json_ignoring_banner() strips non-JSON license/notice headers from stdout payloads
    raw_banner = "[NOTICE] AlphaGenome research-only terms apply.\nWarning: cached schema\n  {\"avi_phred\": 5.67, \"ok\": [1, 2]}\n"
    parsed_b = parse_json_ignoring_banner(raw_banner)
    assert parsed_b == {"avi_phred": 5.67, "ok": [1, 2]}

    # 19. Physiological 150 mM Na+ mixed-PO/PS Tm & WT bystander (UG)8 sponge penalty prioritize ISS Window B over UG8
    tm_1m, _ = duplex_tm_moe("UAGGGCUUCUCUGGAUCA")
    tm_ph = duplex_tm_moe_physiological("UAGGGCUUCUCUGGAUCA")
    assert 48.0 <= tm_ph <= 72.0 and tm_ph < tm_1m - 10.0
    iss_hit = score_target_intervals("chr20", "A" * 15 + "UAGGGCUUCUCUGGAUCA" + "A" * 15, list(range(100, 148)), "+", (18,), mode="INCLUDE_CONSTITUTIVE_EXON", feature_bounds_1b=(70, 80))
    ug8_hit = score_target_intervals("chr20", "C" * 15 + "UGUGUGUGUGUGUGUGCCAA" + "C" * 15, list(range(10, 60)), "+", (20,), mode="INCLUDE_EXON_UPSTREAM_UG", feature_bounds_1b=(75, 95))
    assert iss_hit and ug8_hit and ug8_hit[0]["wt_bystander_sponge_flag"] is True
    assert iss_hit[0]["composite_score"] > ug8_hit[0]["composite_score"]

    # 20. 2D SARM1+STMN2 MWC threshold synergy sweep verifies 1.0x relative IC90 vs multi-fold absolute threshold sparing
    mwc_sw = sweep_sarm1_mwc_threshold_synergy()
    assert mwc_sw["intrinsic_relative_ic90_fold_shift"] == 1.0 and mwc_sw["n_active_threshold_combinations"] >= 10
    assert 2.0 <= float(mwc_sw["threshold_sparing_median_fold"]) <= 12.0

    # 21. Phase 3A pigeonhole 3-seed off-target scanner & antisense G:U wobble polarity verification
    from carbon_als.offtarget_scanner import (
        classify_spliced_hit_region,
        count_mismatch_and_wobble,
        detect_internal_1nt_bulge,
        min_dist_to_sorted_points,
        split_pigeonhole_3seeds,
    )
    seeds18 = split_pigeonhole_3seeds("ACGT" * 4 + "AC")
    assert [len(s) for _, s in seeds18] == [6, 6, 6]
    nm, ngu, nd = count_mismatch_and_wobble("CAG", "TGG")
    assert (nm, ngu, nd) == (2, 2, 0)
    nm2, ngu2, nd2 = count_mismatch_and_wobble("CAG", "CAA")
    assert (nm2, ngu2, nd2) == (1, 0, 1)
    assert min_dist_to_sorted_points(105, 122, [100, 200]) == 5
    assert min_dist_to_sorted_points(95, 110, [100, 200]) == 0

    # 22. Phase 3A v2 1-nt RNA/SSO bulge detector & spliced mRNA EEJ/UTR5/UTR3 steric classifier
    q_b = "AACCGGTT" * 2 + "AA"
    assert detect_internal_1nt_bulge(q_b, q_b[:9] + "G" + q_b[9:], 0) == ("RNA_BULGE_1NT", 19)
    assert detect_internal_1nt_bulge(q_b, q_b[:8] + q_b[9:], 0) == ("SSO_BULGE_1NT", 17)
    assert detect_internal_1nt_bulge(q_b, "G" + q_b, 0) is None
    assert classify_spliced_hit_region(90, 108, {"eej_offsets": [100], "cds_start": 30, "cds_end": 500}) == (0, "EEJ_LE50NT", True)
    assert classify_spliced_hit_region(12, 30, {"eej_offsets": [200], "cds_start": 25, "cds_end": 500}) == (170, "UTR5_OR_AUG_LE25NT", True)
    assert classify_spliced_hit_region(600, 618, {"eej_offsets": [200], "cds_start": 25, "cds_end": 500}) == (400, "UTR3_GT50EEJ", False)

    # 23. Phase 3A biosecurity >=15-nt case-insensitive oligomer sequence leak regex
    from phase3_gates import RAW_OLIGO_SEQ_RE
    assert RAW_OLIGO_SEQ_RE.search("chr8:79616819-79616836(+) ENST00000392086.8") is None
    assert RAW_OLIGO_SEQ_RE.search("raw oligo " + ("acgt" * 4 + "ac") + " leak") is not None

    # 24. Phase 3B zero-overlap, atomic single-entity, and Epistemic Asymmetry gate
    from phase3b_gates import verify_phase3b_gates
    from verify_carbon_als import load_csv
    p3b_ok = verify_phase3b_gates(ROOT, load_csv("candidate_intake_ledger.csv"), load_csv("subnode_dissection.csv"), load_csv("analysis_runs.csv"), load_csv)
    assert p3b_ok == [], f"Unexpected Phase 3B gate errors: {p3b_ok}"
    bad_bundle = [dict(r) for r in load_csv("phase3b_denovo_candidates.csv")]
    bad_bundle[0]["gene_or_drug"] = "DPP6;DPP10"
    errs_b = verify_phase3b_gates(ROOT, load_csv("candidate_intake_ledger.csv"), load_csv("subnode_dissection.csv"), load_csv("analysis_runs.csv"), load_csv, cand_override=bad_bundle)
    assert any("non-atomic gene_or_drug" in e for e in errs_b)

    # Test 25: Phase 4 52-hypothesis & 26-interval cross-phase portfolio gate
    from phase4_gates import verify_phase4_gates
    errs_p4 = verify_phase4_gates(ROOT, load_csv("candidate_decisions.csv"), {r["analysis_run_id"] for r in load_csv("analysis_runs.csv")}, load_csv)
    assert not errs_p4, f"Unexpected Phase 4 gate errors: {errs_p4}"
    p4_rows = load_csv("phase4_unified_portfolio.csv")
    cis4_rows = load_csv("phase4_unified_cis_intervals.csv")
    assert len(p4_rows) == 52 and len(cis4_rows) == 26, f"Expected 52 portfolio & 26 cis rows, got {len(p4_rows)} & {len(cis4_rows)}"

    # Test 26: Coupled zero-dead-zone +PI(3)P->LRRK2/CASM turnover ODE, finite-d_lock hetero-octamer & CD38 cADPR bound
    casm_q48 = sweep_coupled_pikfyve_casm_sensitivity([float(h) for h in range(0, 336, 48)], 336.0, 6.5, 4.5, 1.5)
    casm_q72 = sweep_coupled_pikfyve_casm_sensitivity([0.0, 72.0, 144.0, 216.0, 288.0], 336.0, 8.0, 4.5, 1.5)
    assert casm_q48["n_parameter_combinations"] == 81 and casm_q48["killgate_pass_rate"] == 0.0 and casm_q48["end_casm_min"] > 0.05
    assert casm_q72["n_parameter_combinations"] == 81 and casm_q72["killgate_pass_rate"] == 0.0 and casm_q72["end_casm_min"] > 0.05
    casm_decay = simulate_coupled_pikfyve_casm_pkpd([0.0], 168.0, 8.0, 4.5, 1.5, ec50_casm=0.22, tau_casm_repair_h=24.0)
    assert casm_decay["end_casm_stress_index"] < 0.02 * casm_decay["peak_casm_stress_index"]  # continuous repair never freezes
    het_rev = hetero_octamer_tlock_inhibition(100.0, gof_allele_fraction=0.5, d_lock=6.5)
    assert 0.30 <= het_rev["treated_fractional_activity"] <= 0.40  # ~34.8% residual NADase ceiling in ARM-broken GoF heterozygote
    cd38_b = compute_cd38_cadpr_dilution_and_audit_bound(0.10, 0.90, 0.50)
    assert cd38_b["selective_sarm1_fluid_cadpr_drop_pct"] == 9.0 and abs(cd38_b["min_offtarget_cd38_inhibition_pct_if_cell_free_plasma"] - 44.44) < 0.02

    print("PASS: All 26 v0.5.4 shared-loader, directory-SHA256, mmCIF, skill-CLI, splice-Tm/bystander, MWC/PKPD/CASM/CD38, off-target/bulge/EEJ, Phase 3B, Phase 4 portfolio, and biosecurity tests verified (0 errors).")


if __name__ == "__main__":
    main()
