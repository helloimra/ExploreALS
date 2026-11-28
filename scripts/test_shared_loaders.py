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


def _has_ds(dataset_id: str) -> bool:
    try:
        return resolve_dataset_path(dataset_id, verify_hash=False).exists()
    except (FileNotFoundError, KeyError):
        return False


def main() -> None:
    is_pub = (ROOT / "docs" / "index.html").is_file() and not (ROOT / "reports" / "candidates").is_dir()
    eff_mode = "cached" if is_pub else "full"

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

    # 3. Brown 2022 loader verifies multiplex splice targets (when DS_CRYPTIC staged)
    if _has_ds("DS_CRYPTIC"):
        b22 = load_brown2022_splicing(["KCNQ2", "UNC13A", "STMN2", "G2E3"])
        assert b22["splicing_modality"] == "RNA_SPLICING_MAJIQ" and len(b22["junctions_df"]) >= 4

    # 4. Bye 2025 loader verifies bit-exact Riluzole #1 (+3.959 d) (when DS005_BYE staged)
    if _has_ds("DS005_BYE"):
        bye = load_bye2025_screen()
        assert len(bye) == 107 and bye.iloc[0]["drug"] == "Riluzole"
        assert abs(float(bye.iloc[0]["mean_paired_dmso_days"]) - 3.959) < 0.002

    # 5. Spillman 2026 loader separates Synaptosome vs Homogenate DIA protein from MOESM2 RNA-seq
    if _has_ds("DS029_SPILL"):
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
    s_7djt = None
    if _has_ds("DS_PDB_7DJT") and _has_ds("DS_PDB_9TZY"):
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
    if s_7djt is not None:
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
    if _has_ds("DS001_ONEILL"):
        on_motor = load_oneill2025_subtypes(exclude_pure_ftd=True)
        on_pooled = load_oneill2025_subtypes(exclude_pure_ftd=False)
        assert on_motor["n_non_discordant_cases"] == 303 and on_motor["subtype_counts"]["ALS-TE"] == 41
        assert on_pooled["subtype_counts"]["ALS-TE"] == 66  # 41 motor ALS/ALS+FTD + 25 pure FTD
    if _has_ds("DS031_ZHANG"):
        zh = load_zhang2026_spatial(["IL1RL1", "C1QA", "C1QB", "C1QC"])
        assert zh["modality"] == "SPATIAL_VISIUM_PSEUDOBULK" and not zh["tdp43_niche_df"].empty
    if _has_ds("DS_EDIN_PB"):
        ed = load_edinburgh_pseudobulk("Endothelial", ["IL1RL1", "IL33"], region="donor_collapsed")
        assert ed["modality"] == "SNRNA_PSEUDOBULK_LOG2CPM" and len(ed["donor_df"]) >= 25
        ed_nc9 = load_edinburgh_pseudobulk("Excitatory neuron", ["ELK1"], region="donor_collapsed", exclude_c9=True)
        assert len(ed_nc9["donor_df"]) == 32 and "SD006/17" not in set(ed_nc9["donor_df"]["donor_id"]), "Donor-level C9 exclusion failed on SD006/17!"
    if _has_ds("DS003_PB"):
        pi = load_pineda2024_pseudobulk("BA4", "Excitatory", ["CHMP7", "CHMP2B", "FBXL5"])
        assert pi["modality"] == "SNRNA_PSEUDOBULK_LOG2CPM" and len(pi["donor_df"]) == 32

    # 17. v0.4.1 Directory SHA-256 tree verification passes on multi-file staged directories (including LF-checked-out DS_ELIG_BED) & rejects content edits
    for dsid_dir in ("DS_CRYPTIC", "DS029_SPILL", "DS_PDB", "DS_ELIG_BED"):
        if _has_ds(dsid_dir):
            assert resolve_dataset_path(dsid_dir, verify_hash=True).is_dir()
    if _has_ds("DS_ELIG_BED"):
        from scripts.phase1_batches.batch_runner_utils import _dir_matches_per_file_lock
        import shutil as _shutil
        elig_src = resolve_dataset_path("DS_ELIG_BED", verify_hash=False)
        exp_elig_sha = "79f79fd2e783104681064fc3a1350ccb2eb6e41da0435f165b0aec26a875f21a"
        with tempfile.TemporaryDirectory() as td_elig:
            lf_copy = Path(td_elig) / "elig_lf"
            _shutil.copytree(elig_src, lf_copy)
            for fp_e in lf_copy.rglob("*"):
                if fp_e.is_file():
                    fp_e.write_bytes(fp_e.read_bytes().replace(b"\r\n", b"\n"))
            assert _dir_matches_per_file_lock("DS_ELIG_BED", lf_copy, exp_elig_sha), "LF-normalized DS_ELIG_BED checkout failed per-file lock!"
            tampered = lf_copy / "package.json"
            tampered.write_bytes(tampered.read_bytes() + b" ")
            assert not _dir_matches_per_file_lock("DS_ELIG_BED", lf_copy, exp_elig_sha), "Tampered DS_ELIG_BED content was not rejected!"

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
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    from phase3b_gates import verify_phase3b_gates
    from verify_carbon_als import load_csv
    p3b_ok = verify_phase3b_gates(ROOT, load_csv("candidate_intake_ledger.csv"), load_csv("subnode_dissection.csv"), load_csv("analysis_runs.csv"), load_csv, mode=eff_mode)
    assert p3b_ok == [], f"Unexpected Phase 3B gate errors: {p3b_ok}"
    bad_bundle = [dict(r) for r in load_csv("phase3b_denovo_candidates.csv")]
    bad_bundle[0]["gene_or_drug"] = "DPP6;DPP10"
    errs_b = verify_phase3b_gates(ROOT, load_csv("candidate_intake_ledger.csv"), load_csv("subnode_dissection.csv"), load_csv("analysis_runs.csv"), load_csv, cand_override=bad_bundle, mode=eff_mode)
    assert any("non-atomic gene_or_drug" in e for e in errs_b)

    # Test 25: Phase 4 55-hypothesis & 28-interval cross-phase portfolio gate
    from phase4_gates import verify_phase4_gates
    errs_p4 = verify_phase4_gates(ROOT, load_csv("candidate_decisions.csv"), {r["analysis_run_id"] for r in load_csv("analysis_runs.csv")}, load_csv, mode=eff_mode)
    assert not errs_p4, f"Unexpected Phase 4 gate errors: {errs_p4}"
    p4_rows = load_csv("phase4_unified_portfolio.csv")
    cis4_rows = load_csv("phase4_unified_cis_intervals.csv")
    assert len(p4_rows) == 55 and len(cis4_rows) == 28, f"Expected 55 portfolio & 28 cis rows, got {len(p4_rows)} & {len(cis4_rows)}"

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

    # Test 27: ExploreALS EALS-001..EALS-055 accession bijection & collision-safe fuzzy resolver
    from carbon_als.accessions import (
        AMBIGUOUS_SHORT_BIO_TOKENS,
        accession_to_legacy,
        legacy_to_accession,
        resolve_candidate_query,
        translate_legacy_tokens_in_prose,
    )
    rk_map = {int(r["unified_rank"]): r["accession_id"] for r in p4_rows}
    sub_slug = {r["gene_symbol"].lower(): (legacy_to_accession(r["parent_carbon_id"]), legacy_to_accession(r["subnode_id"])) for r in load_csv("subnode_dissection.csv")}
    assert legacy_to_accession("C006") == "EALS-006" and accession_to_legacy("EALS-006") == "C006"
    assert legacy_to_accession("S06") == "EALS-030" and accession_to_legacy("EALS-030") == "S06"
    assert legacy_to_accession("DN-13") == "EALS-046" and accession_to_legacy("EALS-046") == "DN-13"
    assert legacy_to_accession("L01") == "EALS-053" and accession_to_legacy("EALS-053") == "L01"
    assert legacy_to_accession("L02") == "EALS-054" and accession_to_legacy("EALS-054") == "L02"
    assert legacy_to_accession("L03") == "EALS-055" and accession_to_legacy("EALS-055") == "L03"
    assert legacy_to_accession("C015-N1") == "EALS-015.1" and accession_to_legacy("EALS-015.1") == "C015-N1"
    for q_in, exp_pair in (
        ("c006", ("EALS-006", None)), ("c6", ("EALS-006", None)), ("eals6", ("EALS-006", None)), ("006", ("EALS-006", None)),
        ("#3", ("EALS-006", None)), ("#4", ("EALS-030", None)), ("kcnq2", ("EALS-006", None)), ("dn013", ("EALS-046", None)), ("dn-13", ("EALS-046", None)),
        ("d013", ("EALS-046", None)), ("maob", ("EALS-046", None)), ("s06", ("EALS-030", None)), ("sarm1", ("EALS-030", None)),
        ("l01", ("EALS-053", None)), ("cgas", ("EALS-053", None)), ("#25", ("EALS-053", None)),
        ("l02", ("EALS-054", None)), ("nadsyn1", ("EALS-054", None)), ("#16", ("EALS-054", None)),
        ("l03", ("EALS-055", None)), ("cyfip2", ("EALS-055", None)), ("#17", ("EALS-055", None)),
        ("scfd1", ("EALS-015", "EALS-015.1")), ("c015-n2", ("EALS-015", "EALS-015.2")), ("eals-015.2", ("EALS-015", "EALS-015.2")),
    ):
        assert resolve_candidate_query(q_in, rk_map, sub_slug) == exp_pair, f"Failed query {q_in}: {resolve_candidate_query(q_in, rk_map, sub_slug)}"
    assert resolve_candidate_query("sod1", rk_map, sub_slug) == (None, None)  # never hijacks S01
    assert "c3" in AMBIGUOUS_SHORT_BIO_TOKENS and "c9" in AMBIGUOUS_SHORT_BIO_TOKENS
    assert translate_legacy_tokens_in_prose("Pair S06 with C006, L01, L02, L03, and C015-N1 (FLAGSHIP-S06, candidates/C006.md, C3-C5 cord, ALS17)") == (
        "Pair EALS-030 with EALS-006, EALS-053, EALS-054, EALS-055, and EALS-015.1 (FLAGSHIP-S06, candidates/C006.md, C3-C5 cord, ALS17)"
    )
    assert translate_legacy_tokens_in_prose("LINKED_TO_C005_TMS; DN-10..12; C017-N1..N4; 01_c019_als_glia.py") == (
        "LINKED_TO_EALS-005_TMS; EALS-043–EALS-045; EALS-017.1–EALS-017.4; 01_c019_als_glia.py"
    )

    # Test 28: Flagship VerifiedCheck blocks mismatched assert_equal / assert_close and bans raw un-asserted tuples
    if str(ROOT / "pipelines" / "flagship") not in sys.path:
        sys.path.insert(0, str(ROOT / "pipelines" / "flagship"))
    from _flagship_common import assert_close, assert_equal, print_audit_report
    ok_chk = assert_equal("unit_eq", "PASS_CLEAN_GE2MM", "PASS_CLEAN_GE2MM")
    assert ok_chk.status == "PASS"
    for bad_fn in (
        lambda: assert_equal("corrupt_eq", "WARN", "PASS_CLEAN_GE2MM"),
        lambda: assert_close("corrupt_num", 0.51, 0.14, rtol=1e-4),
        lambda: print_audit_report("TEST", "raw_tuple", [("unasserted", "A", "B", "PASS")], "note"),  # type: ignore[list-item]
    ):
        try:
            bad_fn()
            raise AssertionError("Expected flagship guard to fail on corrupted or un-asserted check!")
        except AssertionError as exc:
            assert "[FAIL]" in str(exc)

    # Test 29: Unconditional synthetic minus-strand 5'->3' extraction & on-target 0-mm GGGenome self-hit guard
    from carbon_als.splice_design import assert_on_target_0mm_hit, extract_interval_sense_dna, genomic_to_premRNA
    _plus_seq = "AACGTTGGCCAATTGACC"  # 18 bp asymmetric sequence
    _prem_m, _coords_m = genomic_to_premRNA(_plus_seq, "chr9", 1001, "-")
    _p2b_m = dict(zip(_coords_m, _prem_m, strict=True))
    _sense_m = extract_interval_sense_dna(_p2b_m, 1001, 1018, "-")
    assert _sense_m == "GGTCAATTGGCCAACGTT", f"Minus-strand 5'->3' sense extraction wrong: got {_sense_m}"
    _prem_p, _coords_p = genomic_to_premRNA(_plus_seq, "chr2", 2001, "+")
    _p2b_p = dict(zip(_coords_p, _prem_p, strict=True))
    assert extract_interval_sense_dna(_p2b_p, 2001, 2018, "+") == _plus_seq
    _gg_ok = {"ungapped_hits": [{"chrom": "chr9", "grch38_start": 1001, "grch38_end": 1018, "strand": "-", "total_mismatches": 0}]}
    assert assert_on_target_0mm_hit(_gg_ok, "chr9", 1001, 1018, "-", "chr9:1001-1018(-)") == 1
    _gg_bad = {"ungapped_hits": [{"chrom": "chr2", "grch38_start": 5000, "grch38_end": 5017, "strand": "+", "total_mismatches": 2}]}
    try:
        assert_on_target_0mm_hit(_gg_bad, "chr9", 1001, 1018, "-", "chr9:1001-1018(-)")
        raise AssertionError("Expected ON_TARGET_SELF_HIT_MISSING when 0 on-target 0mm hits exist!")
    except AssertionError as exc:
        assert "ON_TARGET_SELF_HIT_MISSING" in str(exc)

    # Test 30: Unconditional AlphaGenome polarity module (dinucleotides, window sizing, disruption-first precedence, 3-allele concordance, strict JSON)
    from carbon_als.alphagenome_polarity import (
        assert_splice_dinucleotide,
        classify_variant_polarity,
        select_window_length,
        strict_json_dumps,
        summarize_position_concordance,
    )
    # Plus-strand GT/AG & minus-strand GT (+strand CA) / AG (+strand TC) checks
    _ref_m = {100: "T", 101: "G", 102: "A", 103: "C", 104: "T"}  # on '-' strand: 103..102 = GT, 104..103 = AG, 101..100 = CA (NOT GT!)
    assert assert_splice_dinucleotide(_ref_m, 103, "-", "5SS_GT_B1", "valid_minus_gt") == "GT"
    assert assert_splice_dinucleotide(_ref_m, 104, "-", "3SS_AG_B1", "valid_minus_ag") == "AG"
    for bad_call in (
        lambda: assert_splice_dinucleotide(_ref_m, 101, "-", "5SS_GT_B1", "prune2_ac_bug"),
        lambda: assert_splice_dinucleotide({207: "C", 208: "G"}, 207, "+", "3SS_AG_B1", "celf5_cg_bug"),
    ):
        try:
            bad_call()
            raise AssertionError("Expected SPLICE_DINUCLEOTIDE_MISMATCH on non-donor/non-acceptor coordinates!")
        except ValueError as exc:
            assert "SPLICE_DINUCLEOTIDE_MISMATCH" in str(exc)
    # Dynamic window sizing upgrades DLGAP1 146-kb intron to 524,288 bp
    _wlen, _ws, _we = select_window_length(4005202, 4151179)
    assert _wlen == 524_288 and _ws < 4005202 and _we > 4151179
    # Out-of-window canonical junction NEVER silently defaults to WT_CANONICAL_SAFE_NEUTRAL
    _p_oow = classify_variant_polarity(None, 0.0, 0.0, [], canonical_in_window=False)
    assert _p_oow["polarity"] == "CANONICAL_JUNCTION_UNMEASURED_OUT_OF_WINDOW"
    # Disruption-first precedence: canonical 5'SS knockout (-95%) + cryptic gain MUST be DISRUPTS (never GAINS_CRYPTIC!)
    _p_posctrl = classify_variant_polarity(-95.0, 0.45, -0.92, [{"delta": 0.65, "ref": 0.01}])
    assert _p_posctrl["polarity"] == "DISRUPTS_EXISTING_OR_CANONICAL_SPLICING" and _p_posctrl["with_secondary_cryptic_activation"] is True
    # Protected physiological microexon disruption blocks false ENHANCES_CANONICAL_SPLICING
    _p_micro = classify_variant_polarity(+250.0, 0.01, -0.01, [], protected_pcts={"microexon_9bp": -32.0})
    assert _p_micro["polarity"] == "DISRUPTS_EXISTING_OR_CANONICAL_SPLICING" and _p_micro["protected_junction_disrupted"] is True
    # 3-allele concordance flags 1-of-3 de novo GT/AG creation as SINGLE_ALLELE_DE_NOVO_SITE_ARTIFACT
    _c_art = summarize_position_concordance([
        {"polarity_mn": "WT_CANONICAL_SAFE_NEUTRAL"},
        {"polarity_mn": "WT_CANONICAL_SAFE_NEUTRAL"},
        {"polarity_mn": "GAINS_CRYPTIC_SPLICE_SITE_OR_JUNCTION"},
    ])
    assert _c_art["concordance_class"] == "SINGLE_ALLELE_DE_NOVO_SITE_ARTIFACT" and _c_art["valid_for_wt_sso_safety"] is False
    _c_ok = summarize_position_concordance([{"polarity_mn": "ENHANCES_CANONICAL_SPLICING"}] * 3)
    assert _c_ok["concordance_class"] == "CONCORDANT_3OF3_ENHANCES_WT" and _c_ok["valid_for_wt_sso_safety"] is True
    # Strict RFC-8259 JSON converts NaN->null and blocks >=15-nt raw sequences
    _j_clean = strict_json_dumps({"x": float("nan"), "y": 1.5})
    assert "null" in _j_clean and "NaN" not in _j_clean
    try:
        strict_json_dumps({"leak": "ACGTACGTACGTACGT"})
        raise AssertionError("Expected strict_json_dumps to block 16-nt raw sequence!")
    except AssertionError as exc:
        assert "BIOSECURITY_GUARD_TRIGGERED" in str(exc)

    # Test 31: Unconditional Pack C statistical guards (VIF blocking, missing-sex->NaN, 1-UMI cliff + specificity, BH-FDR p<=q, FDR-gated classify, Zhu SMR)
    import numpy as _np
    import pandas as _pd
    from carbon_als.loaders import expansion_loaders as _el
    _meta_sex = _pd.DataFrame({"sex": ["M", "Female", "Unknown", "", None, "Missing"]})
    _s_enc = _el._encode_covariate_matrix(_meta_sex)["sex_male"]
    assert _s_enc[0] == 1.0 and _s_enc[1] == 0.0 and bool(_np.all(_np.isnan(_s_enc[2:]))), f"Missing sex coerced incorrectly: {_s_enc}"
    # Collinear covariate (r=-0.995 -> VIF>50) MUST be dropped with NaN adjusted p (no Welch fallback!)
    _case_syn = _np.array([1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0], dtype=float)
    _col_cov = -_case_syn + _np.linspace(0.0, 0.05, 12)
    _ols_col = _el._covariate_adjusted_ols(_np.linspace(1.0, 4.0, 12), _case_syn, {"gc_z": _col_cov}, max_case_vif=5.0)
    assert len(_ols_col["collinear_covariates_dropped"]) == 1 and _np.isnan(_ols_col["covariate_adjusted_nominal_p"])
    # Small-N 1-UMI Poisson cliff caught (positive) AND clean separation passes (negative specificity!)
    _lev_1umi = _el.compute_small_n_dropout_leverage_flag(
        _np.array([4.9, 0.0, 0.0, 0.0]), _np.array([5.5, 5.6, 5.3, 4.7]), 0.0004, 0.043, 0.0545,
        raw_case_counts=_np.array([1, 0, 0, 0]), raw_ctrl_counts=_np.array([1, 4, 1, 1]),
    )
    assert _lev_1umi["sparse_1umi_cliff_flag"] is True and _lev_1umi["small_n_dropout_leverage_flag"] is True
    _lev_clean = _el.compute_small_n_dropout_leverage_flag(
        _np.array([8.1, 8.3, 7.9, 8.2]), _np.array([4.1, 4.0, 4.2, 3.9]), 0.0002, 0.0003, 0.0286,
        raw_case_counts=_np.array([120, 140, 110, 130]), raw_ctrl_counts=_np.array([15, 14, 16, 13]),
    )
    assert _lev_clean["small_n_dropout_leverage_flag"] is False
    # Exact BH-FDR provenance guard (no rounding q<p, rejects out-of-range p)
    _bh = _el.bh_fdr_with_provenance_guard({"a": 1e-12, "b": 0.04, "c": 0.995105044}, context="unit_bh")
    assert all(_bh[k]["fdr_bh"] >= _bh[k]["p_value"] for k in _bh) and _bh["a"]["fdr_bh"] > 0.0
    try:
        _el.bh_fdr_with_provenance_guard({"bad": 1.2}, context="unit_bh_bad")
        raise AssertionError("Expected ValueError on p > 1.0")
    except ValueError:
        pass
    # classify_pack_c_evidence MUST gate CORROBORATED_INDEPENDENT on FDR < 0.05
    _cl_nom = _el.classify_pack_c_evidence("takeuchi2025_lsc", True, True, 0.02, fdr=0.25)
    assert _cl_nom["stress_status"] == "NOMINAL_CONCORDANT_UNCORRECTED"
    _cl_fdr = _el.classify_pack_c_evidence("takeuchi2025_lsc", True, True, 0.001, fdr=0.01)
    assert _cl_fdr["stress_status"] == "CORROBORATED_INDEPENDENT"
    # Exact Zhu et al. (2016) T_SMR check
    _smr = _el.compute_smr_stats(gwas_beta=0.08, gwas_se=0.02, qtl_beta=0.30, qtl_se=0.05)  # z_g=4, z_q=6 -> T=(16*36)/(16+36)=11.0769
    assert abs(_smr["t_smr"] - (16.0 * 36.0 / 52.0)) < 1e-3

    # Test 32: Hardened Pack C staged-data integration checks (Keuss 4v5 + TDP43.20 drop, Takeuchi MNs 1-UMI cliff + Somatomotor leverage, Miedema non-p-peeking dedup, fail-fast lineage guard)
    pack_c_manifest = ROOT / "data" / "expansion_2026_11" / "EXPANSION_MANIFEST_2026_11.csv"
    if pack_c_manifest.is_file():
        keu_s = _el.load_keuss2025_soma_neurite("Soma", "TDP43-knockdown", "nontargeting-sgRNA", genes=["SYP", "STMN2", "UNC13A"])
        assert keu_s["n_case"] == 4 and keu_s["n_ctrl"] == 5, f"Expected 4v5 matched Soma after dropping TDP43.20, got {keu_s['n_case']}v{keu_s['n_ctrl']}"
        assert "TDP43.20" in keu_s["dropped_low_depth_libs"] and keu_s["dropped_low_depth_libs"]["TDP43.20"] < 1000
        assert keu_s["normalization_used"].startswith("deseq2_mor") and abs(keu_s["stats"]["SYP"]["diff"]) < 0.25
        keu_n = _el.load_keuss2025_soma_neurite("Neurite", "TDP43-knockdown", "nontargeting-sgRNA", genes=["SYP", "UNC13A"])
        assert keu_n["n_case"] == 5 and keu_n["n_ctrl"] == 5 and keu_n["stats"]["UNC13A"]["diff"] < -0.5
        tak_sm = _el.load_expansion_pseudobulk("takeuchi2025_lsc", "Somatomotor_Neuron", genes=["KCNQ2", "UNC13A"], min_cells=5)
        assert tak_sm["stats"]["KCNQ2"]["small_n_dropout_leverage_flag"] is True
        assert tak_sm["stats"]["UNC13A"]["small_n_dropout_leverage_flag"] is True
        tak_mn = _el.load_expansion_pseudobulk("takeuchi2025_lsc", "MNs", genes=["NPTX2", "STMN2"], min_cells=5)
        assert tak_mn["stats"]["NPTX2"]["sparse_1umi_cliff_flag"] is True and tak_mn["stats"]["NPTX2"]["small_n_dropout_leverage_flag"] is True
        mied_r = _el.load_miedema2025_ftld_tdp_c(genes=["STMN2"])
        assert mied_r["dedup_method"] == "max_completeness_stable_no_p_peeking"
        try:
            _el.compute_lineage_ambient_flags("zelic2025_cervical_sc", ("Astrocyte", "INVALID_STRATUM_XYZ"), genes=["STMN2"])
            raise AssertionError("Expected fail-fast ValueError on invalid lineage stratum!")
        except ValueError:
            pass

    # Test 33: PEP 562 lazy carbon_als.__init__ + check_work_outputs.py positive & negative unit tests
    import json as _json
    import os as _os
    import subprocess as _sp
    import tempfile as _tf
    from pathlib import Path as _P
    _lazy_proc = _sp.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'src'); from carbon_als.alphagenome_polarity import strict_json_dumps; assert 'carbon_als.loaders' not in sys.modules and 'statsmodels' not in sys.modules"],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    assert _lazy_proc.returncode == 0, f"PEP 562 lazy import leaked loaders/statsmodels: {_lazy_proc.stderr}"

    sys.path.insert(0, str(ROOT / "scripts"))
    import check_work_outputs as _cwo  # noqa: E402

    with _tf.TemporaryDirectory() as _td:
        _tr = _P(_td)
        (_tr / "src" / "carbon_als").mkdir(parents=True)
        (_tr / "work" / "phase5_pack_c_expansion" / "scripts").mkdir(parents=True)
        (_tr / "work" / "phase5_pack_c_expansion" / "outputs").mkdir(parents=True)
        (_tr / "work" / "phase5_pack_c_expansion" / "cache").mkdir(parents=True)
        _dep_py = _tr / "src" / "carbon_als" / "dummy_mod.py"
        _dep_py.write_text("X = 1\n", encoding="utf-8")
        _scr_py = _tr / "work" / "phase5_pack_c_expansion" / "scripts" / "99_demo.py"
        _scr_py.write_text(
            "from carbon_als.dummy_mod import X\nOUT_FP = 'v15_followup_demo.json'\n",
            encoding="utf-8",
        )
        _out_fp = _tr / "work" / "phase5_pack_c_expansion" / "outputs" / "v15_followup_demo.json"
        _out_fp.write_text(_json.dumps({
            "summary_table": [{"role": "CANON_5SS_POSCTRL", "polarity_mn": "DISRUPTS_EXISTING_OR_CANONICAL_SPLICING", "mn_canon_pct": -95.0}],
            "intervals": [{"interval_id": "chr1:1-20(+)", "on_target_0mm_self_hits": 1, "premRNA_0mm": 0, "offtarget_safety_status": "PASS_CLEAN_GE2MM"}],
        }), encoding="utf-8")
        _os.utime(_dep_py, (1000, 1000))
        _os.utime(_scr_py, (1000, 1000))
        _os.utime(_out_fp, (2000, 2000))
        _ok_rep = _cwo.audit_work_outputs(_tr, scope="active", strict_mtime=True)
        assert _ok_rep["passed"] and _ok_rep["n_outputs_checked"] == 1 and not _ok_rep["stale"], f"Clean synthetic check failed: {_ok_rep}"
        # Negative 1: Stale dependency under --strict-mtime
        _os.utime(_dep_py, (3000, 3000))
        _st_rep = _cwo.audit_work_outputs(_tr, scope="active", strict_mtime=True)
        assert not _st_rep["passed"] and any("STALE_OUTPUT" in e for e in _st_rep["errors"]), f"Failed to catch stale dep: {_st_rep}"
        _os.utime(_dep_py, (1000, 1000))
        # Negative 2: Non-RFC8259 NaN
        _out_fp.write_text('{"x": NaN}', encoding="utf-8")
        _nan_rep = _cwo.audit_work_outputs(_tr, scope="active", strict_mtime=False)
        assert not _nan_rep["passed"] and any("INVALID_RFC8259_JSON" in e for e in _nan_rep["errors"])
        # Negative 3: Biosecurity sequence leak
        _out_fp.write_text('{"leak": "ACGTACGTACGTACGT"}', encoding="utf-8")
        _bio_rep = _cwo.audit_work_outputs(_tr, scope="active", strict_mtime=False)
        assert not _bio_rep["passed"] and any("BIOSECURITY_HIT" in e for e in _bio_rep["errors"])
        # Negative 4: Misclassified POSCTRL & self0=0 & masked 0mm off-target
        _out_fp.write_text(_json.dumps({
            "summary_table": [{"role": "CANON_5SS_POSCTRL", "polarity_mn": "GAINS_CRYPTIC_SPLICE_SITE_OR_JUNCTION", "mn_canon_pct": None}],
            "intervals": [{"interval_id": "chr1:1-20(-)", "on_target_0mm_self_hits": 0, "premRNA_0mm": 1, "offtarget_safety_status": "CAUTION"}],
        }), encoding="utf-8")
        _bad_rep = _cwo.audit_work_outputs(_tr, scope="active", strict_mtime=False)
        assert not _bad_rep["passed"] and len(_bad_rep["errors"]) >= 4, f"Expected 4 contract errors, got: {_bad_rep}"
        # Negative 5: Swallowed {"error": "..."} payload & rounded BH-FDR (q < p) inversion
        _out_fp.write_text(_json.dumps({
            "stratum_a": {"error": "Stratum MotorNeurons not found"},
            "stats": {"GENE1": {"covariate_adjusted_nominal_p": 0.051, "q_bh_ws3": 0.049}},
        }), encoding="utf-8")
        _rec_rep = _cwo.audit_work_outputs(_tr, scope="active", strict_mtime=False)
        assert not _rec_rep["passed"] and any("SWALLOWED_ERROR_KEY" in e for e in _rec_rep["errors"]) and any("BH_FDR_LESS_THAN_P" in e for e in _rec_rep["errors"]), f"Failed recursive error/BH check: {_rec_rep}"
        # Positive + Negative test of carbon_als.io_guards (require_hit + write_work_json)
        from carbon_als.io_guards import require_hit as _req_hit, write_work_json as _wwj
        assert _req_hit({"ok": 1}, "nonempty")["ok"] == 1
        for _empty in (None, {}, [], ""):
            try:
                _req_hit(_empty, "empty_case")
                raise AssertionError(f"Expected LookupError for {_empty!r}")
            except LookupError:
                pass
        _wwj(_out_fp, {"val": float("nan"), "ok": 42}, script="99_demo.py", controls_passed=True, controls_summary={"pos": "STMN2_down"})
        _loaded = _json.loads(_out_fp.read_text(encoding="utf-8"))
        assert _loaded["_meta"]["script"] == "99_demo.py" and _loaded["_meta"]["strict_rfc8259"] is True and _loaded["_meta"]["controls_summary"]["pos"] == "STMN2_down" and _loaded["val"] is None
        try:
            _wwj(_out_fp, {"ok": 1}, script="99_demo.py")  # type: ignore[call-arg]
            raise AssertionError("Expected TypeError when controls_passed is omitted!")
        except TypeError:
            pass
        _wwj(_out_fp, {"ok": 1}, script="99_demo.py", controls_passed=False)
        _ctrl_rep = _cwo.audit_work_outputs(_tr, scope="active", strict_mtime=False)
        assert not _ctrl_rep["passed"] and any("CONTROLS_FAILED" in e for e in _ctrl_rep["errors"]), f"Failed to catch controls_passed=False: {_ctrl_rep}"
        try:
            _wwj(_out_fp, {"leak": "ACGTACGTACGTACGT"}, script="99_demo.py", controls_passed=True)
            raise AssertionError("Expected biosecurity block in write_work_json!")
        except AssertionError as _exc:
            assert "BIOSECURITY_GUARD_TRIGGERED" in str(_exc)

    print("PASS: All 33 v0.5.9 shared-loader, PEP 562 lazy-import, check_work_outputs, unconditional Pack C/AlphaGenome/minus-strand/VIF/1-UMI/BH-FDR/SMR, Keuss/Takeuchi integration, flagship-VerifiedCheck, EALS accession, directory-SHA256, mmCIF, splice-Tm/bystander, MWC/PKPD/CASM/CD38, Phase 3B/4, and biosecurity tests verified (0 errors).")


if __name__ == "__main__":
    main()
