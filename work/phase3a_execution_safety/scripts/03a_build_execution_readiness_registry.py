"""RUN-P3A-003 (Part A, v2): Build registries/phase3_execution_readiness.csv separating TRL from Scientific Actionability & Experimental Gate Class with atomic hurdles."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REG_DIR = ROOT / "registries"
OUT_DIR = ROOT / "work" / "phase3a_execution_safety" / "outputs"


def summarize_gene_offtargets(ot_rows: list[dict[str, str]], gene: str) -> str:
    sub = [r for r in ot_rows if r["gene_symbol"] == gene]
    return " | ".join(
        f"#{r['rank_within_gene']} {r['interval_id']}:{r['offtarget_safety_status']}"
        f"(sp0={r['spliced_0mm_genes']},sp1={r['spliced_1mm_genes']},wob0={r['spliced_wobble_only_pc_genes']},"
        f"pm1_ss={r['premRNA_1mm_splice50bp_genes']},pm_wob={r['premRNA_wobble_only_splice50bp_pc_genes']},"
        f"bulge={r['bulge_1nt_steric_pc_genes']},sub18={r['sub18_core_steric_pc_genes']},flags={r['flagged_constrained_neuronal_hits']})"
        for r in sub
    )


def main() -> None:
    with (REG_DIR / "candidate_decisions.csv").open(encoding="utf-8") as fh:
        dec_map = {r["carbon_id"]: r for r in csv.DictReader(fh)}
    with (REG_DIR / "phase3_sso_offtarget_audit.csv").open(encoding="utf-8") as fh:
        ot_rows = list(csv.DictReader(fh))
    br = json.loads((OUT_DIR / "run_p3a_002_csf_glial_bridge_validation.json").read_text(encoding="utf-8"))

    oof = br["within_emory_unconfounded_dia"]["sals_vs_ctrl_leak_free_5fold_oof"]
    dec_ext = br["deconfounded_and_stratified_external_validation"]
    ext_adj = dec_ext["ext_all_symp_als_vs_center_adj_ext_ctrl"]
    c9_adj = dec_ext["genotype_matched_ext_c9_symp_vs_c9_asym_center_adj"]
    p80 = dec_ext["matched_genotype_p80_pass_rates"]
    mgh_d = br["pooled_ds045_center_audit"]["bridge_ctrl_drift_pure_mgh_n16_minus_emory_n54_z"]
    oh = br["independent_external_study_oh2023_pmc10215566"]

    c019_gate = (
        f"rs3831317-neutral Emory leak-free sALS vs Ctrl OOF AUC={oof['oof_roc_auc']} (n={oof['n_sals']+oof['n_ctrl']}); "
        f"MGH-offset-adj external sALS/ALS vs Ctrl AUC={ext_adj['roc_auc']} (n={ext_adj['n_total']}; cross-sectional C9 Symp-vs-Asym AUC={c9_adj['roc_auc']}, n={c9_adj['n_total']}; "
        f"Oh2023 univariate {oh['n_bridge_proteins_fdr_lt_0_05']}/5 FDR<=0.044); pure MGH Ctrl drift={mgh_d:+.2f}z & sALS-p80 passes {100*p80['emory_sals_pass_at_sals_p80']:.1f}% Emory sALS"
    )

    # Columns: (cid, label, primary_mod, trl, gate_class, ev_basis, mod_dep, atomic_hurdles, ind_stage, p3_gate, b_mod, b_warn, b_pk, b_lost, tier)
    specs = [
        ("S06", "SARM1 Non-Orthosteric ARM-TIR T-Lock", "Oral_Non_Covalent_ARM_TIR_SARM1_Allosteric_TLock_ASHA624_Class",
         "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
         "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY", "COARSE_PRIOR_ONLY:8mer_MWC_order_of_magnitude_2_to_7x_threshold_sparing",
         ["HUMAN_PH1B_UNBOUND_CSF_KPUU_TROUGH_CADPR_WASHOUT_AND_ZERO_NFL_REBOUND_FOR_TLOCK",
          "PROSPECTIVE_SEQUENCING_EXCLUSION_OF_LT1PCT_CONSTITUTIVE_ARM_BROKEN_GOF_CARRIERS"],
         "SINGLE_ENTITY_ORAL_TLOCK_PH1B_GENOTYPE_GATED_BEFORE_STAGE2_STMN2_COMBINATION",
         "PDB 9TZY 3-chain BEXi filament activation (122/122 sub-IC50 spike) excluded; 48-72h oral washout (5x->0.03x IC50) & WT vs <1% p.L223P ARM-GoF sequencing gate pre-specified",
         "Intrathecal_SARM1_RNaseH_Gapmer_ASO", "Gapmer_IT_radiculitis_myelitis_and_CSF_pleocytosis_class_risk",
         "Invasive_chronic_lumbar_IT_dosing_with_5_to_10x_rostral_cortical_gradient", "Slow_axonal_SARM1_protein_clearance_delays_acute_NADase_arrest",
         "TIER_1_ACTIONABLE_NOW"),
        ("C006", "KCNQ2 Exon-5 Steric SSO", "Intrathecal_Mixed_POPS_2OMOE_Steric_SSO_Exon5_Inclusion_Walk_Lead_#3_chr20:63442302-63442319(-)_vs_#1_chr20:63442595-63442616(-)",
         "TRL_3_PRECLINICAL_SSO_COORDINATE", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_TDP43_PATHOLOGY_AND_RESCUE", "COARSE_PRIOR_ONLY:Binomial_tetramer_SantaLucia_Tm_and_unverified_lead3_Intron5_ISS_vs_ISE_polarity",
         ["DENSE_IPSC_MN_EXON5_MICRO_WALK_RESOLVING_INTRON5_ISS_VS_ISE_#3_AGAINST_BYSTANDER_UG8_#1",
          "NHP_CERVICAL_PHRENIC_AND_BA4_CORTICAL_1PLEX_VS_24_TO_48MG_MULTIPLEX_CA2_DRG_GLP_IT_TOX",
          "HUMAN_EXCITABILITY_PD_LINKED_TO_C005_TMS_SICI_SDTC_AND_CSF_NPTX2_COMPANION_CUTOFFS"],
         "STAGE_1_SPONSOR_OWNED_SINGLE_ENTITY_1PLEX_IND_BEFORE_21CFR300_50_3PLEX_COFORMULATION",
         summarize_gene_offtargets(ot_rows, "KCNQ2"),
         "Selective_Kv7_2_7_3_Small_Molecule_Opener_QRL101_BHV7000", "Dose_limiting_CNS_somnolence_dizziness_and_urinary_hesitation",
         "Requires_intact_Trp236_S5_pocket_excised_in_DeltaE5_subunits_PDB_7CR2", "ER_retention_and_DeltaE5_Trp236_loss_impose_surface_channel_density_ceiling_on_openers",
         "TIER_1_ACTIONABLE_NOW"),
        ("S07", "Low-Dose Aldesleukin (IL-2)", "Subcutaneous_Recombinant_Low_Dose_IL2_Aldesleukin",
         "TRL_6_PH2B_SUBGROUP_BIOLOGIC", "BIOMARKER_ENRICHED_PHASE3_EFFICACY_TRIAL",
         "MEASURED_HUMAN_RCT_SUBGROUP", "COARSE_PRIOR_ONLY:Operationalized_MIROCALS_3700pg_stratum_MS_NEFH_p80_caveat_and_Schoenfeld_HR070",
         ["PRE_PH3_BIOVENDOR_ELISA_TO_CLIA_PNFH_AND_PAIRED_NFL_IMMUNOASSAY_CALIBRATION",
          "PROSPECTIVE_EVENT_DRIVEN_PH3_SURVIVAL_REPLICATION_UNDER_CALIBRATED_CSF_PNFH_LE_3700_PGML"],
         "APPROVED_BIOLOGIC_BIOMARKER_ENRICHED_PH3_RCT",
         "Trautwig 2025 living CSF (n=77 DIA, n=51 overlapping Emory TMT): tryptic MS NEFL correlates weakly with NEFH (r=0.278; uncalibrated to BioVendor pNfH ELISA), motivating Stage-0 BioVendor-to-CLIA pNfH & paired NfL calibration",
         "COYA_302_ldIL2_plus_CTLA4Ig_or_IL2_mutein", "Chronic_CTLA4Ig_immunosuppression_and_serious_infection_risk",
         "Active_ALSTARS_NCT07161999_omits_baseline_CSF_pNfH_enrichment_gate", "Dual_biologic_confounds_single_agent_aldesleukin_survival_attribution",
         "TIER_1_ACTIONABLE_NOW"),
        ("C001", "UNC13A Cryptic-Exon Steric SSO", "Intrathecal_Mixed_POPS_2OMOE_Steric_SSO_Promoted_Lead_#2_chr19:17642537-17642554(-)",
         "TRL_3_PRECLINICAL_SSO_COORDINATE", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
         "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY", "COARSE_PRIOR_ONLY:SantaLucia_mixed_POPS_Tm",
         ["SPONSOR_OWNED_SINGLE_ENTITY_GLP_TOX_AND_NHP_CERVICAL_BA4_BIODISTRIBUTION_NO_21CFR300_50_REF",
          "PER_TARGET_NDEV_DPCR_AND_CSF_SYNAPTIC_SECRETOME_TE_BIOMARKER_VALIDATION",
          "CLINICAL_CROWDING_DIFFERENTIATION_AND_GENOTYPE_STRATIFIED_24_TO_48MG_MULTIPLEX_UPTAKE_CEILING"],
         "PROMOTE_PASS_CLEAN_#2_chr19:17642537-17642554(-);_STAGE_2_3PLEX_AFTER_PROPRIETARY_1PLEX_TOX_AND_PD",
         summarize_gene_offtargets(ot_rows, "UNC13A"),
         "AAV9_U7_snRNA_UNC13A_Cryptic_Exon_Splice_Vector", "Irreversible_AAV_dorsal_root_ganglion_and_hepatotoxicity_class_liability",
         "Low_adult_human_upper_and_lower_MN_intrathecal_AAV_transduction_efficiency", "Cannot_be_withdrawn_or_dose_titrated_upon_innate_immune_meningoradiculitis",
         "TIER_2_FOCUSED_GATE_FIRST"),
        ("C002", "STMN2 Cryptic-Exon-2a Steric SSO", "Intrathecal_Mixed_POPS_2OMOE_Steric_SSO_Promoted_Lead_#2_chr8:79616829-79616846(+)",
         "TRL_3_PRECLINICAL_SSO_COORDINATE", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
         "MEASURED_HUMAN_TDP43_PATHOLOGY_AND_RESCUE", "COARSE_PRIOR_ONLY:SantaLucia_Tm_and_illustrative_MWC_SARM1_sensitivity_scenario",
         ["SPONSOR_OWNED_SINGLE_ENTITY_GLP_TOX_AND_NHP_CERVICAL_BA4_BIODISTRIBUTION_NO_21CFR300_50_REF",
          "POST_QRL201_NDEV_TSTMN2_AND_SOLUBLE_SCG10_TE_BIOMARKER_BENCHMARKING",
          "STAGE_2_24_TO_48MG_MULTIPLEX_UPTAKE_CEILING_AND_PARALLEL_ORAL_SARM1_TLOCK_STAGING"],
         "PROMOTE_PASS_CLEAN_#2_chr8:79616829-79616846(+);_STAGE_2_COMBO_AFTER_PROPRIETARY_1PLEX_TOX_AND_PD",
         summarize_gene_offtargets(ot_rows, "STMN2"),
         "AAV9_U7_snRNA_STMN2_Exon2a_Splice_Vector", "Irreversible_AAV_DRG_and_hepatotoxicity_liability_while_small_molecule_DLK_stabilizers_caused_clinical_neurotoxicity",
         "Low_adult_human_upper_and_lower_MN_intrathecal_AAV_transduction_efficiency", "Cannot_be_withdrawn_or_dose_titrated_upon_adverse_neuroinflammatory_response",
         "TIER_2_FOCUSED_GATE_FIRST"),
        ("C007", "IL1RL1 / sST2 Decoy Suppression", "Intrathecal_IL1RL1_Intron8_PolyA_Steric_SSO_or_sST2_CTail_aa320_328_Sweeping_Antibody",
         "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_SPATIAL_OR_SNRNA", "COARSE_PRIOR_ONLY:Perivascular_sST2_IL33_mass_action_order_of_magnitude",
         ["N25_SALS_VS_N20_CTRL_ISOLATED_MICROVESSEL_AND_OXIMETRY_VERIFIED_CSF_SIMOA_SST2_FREE_IL33_VALIDATION",
          "CNS_RESTRICTED_INTRON8_POLYA_SSO_OR_CTAIL_AA320_328_SWEEPING_LEAD_GENERATION_SPARING_LUNG_KIDNEY"],
         "PRECLINICAL_MICROVESSEL_AND_LIVING_CSF_SIMOA_KILLGATE_BEFORE_LEAD_GENERATION",
         "Edinburgh donor-collapsed endothelial +3.11 log2CPM (p=0.00641, small n=7 Ctrl -> mandates n>=25/20 microvessels) + Zhang 55-um MN-niche Visium spots +3.76 (spot-level BH=1.85e-9 across N=14 donors); GTEx Lung/Kidney 140.1/46.5 TPM & pan-ST2 astegolimab excluded",
         "Half_Life_Extended_Fc_IL33_Treg_Selective_Mutein_Biologic", "Meningeal_mast_cell_eosinophilic_and_innate_ILC2_neuroinflammatory_flare_risk",
         "Limited_BBB_penetration_and_stoichiometric_neutralization_by_high_perivascular_sST2_sink", "Does_not_remove_endogenous_endothelial_sST2_decoy_excess",
         "TIER_2_FOCUSED_GATE_FIRST"),
        ("BA9-04", "DNAJB2a Cytosolic Isoform Augmentation", "Intrathecal_DNAJB2_Intron9_ISS_Splice_Enhancing_2OMOE_SSO_Promoting_DNAJB2a_Excision",
         "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_C9FTD_FRACTION_PROTEOMICS", "COARSE_PRIOR_ONLY:Unverified_intron9_ISS_vs_ISE_polarity_and_DNAJB2b_ERAD_precursor_pool_ceiling",
         ["SPORADIC_ALS_SPINAL_CORD_DNAJB2A_VS_DNAJB2B_PRECURSOR_POOL_PRM_REPLICATION",
          "EMPIRICAL_1151BP_INTRON9_ISS_VS_ISE_WALK_WITH_BIP_CHOP_ERAD_DNAJB2B_SPARING_COUNTERSCREEN",
          "COMPARTMENT_SELECTIVE_MN_VS_OLIGODENDROCYTE_CYTOSOLIC_DNAJB2A_STOICHIOMETRY"],
         "PRECLINICAL_SALS_CORD_PRECURSOR_POOL_KILLGATE_AND_INTRON9_ISS_WALK_VS_AAV_DNAJB2A_BEFORE_IND",
         "GENCODE v46 Intron-9 chr2:219284836-219285986(+) excised in cytosolic DNAJB2a (ENST00000392086.8, 277 aa, Exon 10 219285987-219286898(+)) vs retained in ER-CAAX DNAJB2b (ENST00000336576.10, 324 aa); gates unmapped ISS-vs-ISE polarity & BiP/CHOP ERAD preservation before SSO vs CAP-B10/mRNA choice",
         "AAV9_or_CAP_B10_Cytosolic_DNAJB2a_cDNA_Gene_Replacement", "Irreversible_AAV_dorsal_root_ganglion_and_hepatotoxicity_plus_supraphysiologic_chaperone_titration_risk",
         "Low_adult_human_corticospinal_and_spinal_MN_AAV_transduction_efficiency", "Lacks_endogenous_promoter_stoichiometry_and_cannot_be_withdrawn_once_dosed",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C014", "CHMP7 / CHMP2B Surveillance Split", "Selective_Peptidomimetic_or_Allosteric_SUN1_CHMP7_Nuclear_Import_Blocker",
         "TRL_1_TARGET_TOOL_PROBE_WATCHLIST", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_C9FTD_FRACTION_PROTEOMICS", "COARSE_PRIOR_ONLY:Uncalibrated_35_to_50pct_partial_CHMP7_knockdown_safety_window",
         ["NO_VALIDATED_SMALL_MOLECULE_OR_PEPTIDOMIMETIC_SUN1_CHMP7_IMPORT_BLOCKER",
          "EXTREME_ESSENTIALITY_SATB2_LEMD2_SYNAPTIC_AND_ANXA11_MEMBRANE_REPAIR_LIABILITY",
          "SPORADIC_ALS_HUMAN_MN_PELLET_PARTITIONING_REPLICATION_BEYOND_N6_C9FTD_IPSC"],
         "EXPLORATORY_TOOL_COMPOUND_AND_TITRATED_KD_SAFETY_SCREEN",
         "Spillman C9FTD iPSC pellet CHMP2B +0.89 (p=0.00114) vs ANXA11 -0.88 (p=0.00447, n=6); CHMP7 pLI=0.9996 penalizes deep RNase-H ablation",
         "Titrated_Partial_35_to_50pct_Intrathecal_CHMP7_Knockdown_ASO", "Narrow_margin_against_SATB2_LEMD2_chromatin_detachment_and_IT_gapmer_radiculitis",
         "Cannot_guarantee_uniform_35_to_50pct_knockdown_across_lumbar_vs_cortical_motor_neurons", "Leaves_insoluble_CHMP2B_ANXA11_membrane_repair_defect_unaddressed",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("S09", "Censavudine (TPN-101) / TYK2-JH2", "Oral_Nucleoside_LINE1_RT_Inhibitor_Censavudine_TPN101",
         "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
         "MEASURED_HUMAN_SPATIAL_OR_SNRNA", "NONE",
         ["UNPUBLISHED_PEER_REVIEWED_PRIMARY_ALS_READOUT_FROM_NCT04993755",
          "DISAGGREGATED_PAN_TDP43_HDGFL2_VS_SUBTYPE_ORF1P_L1HS_ENRICHMENT_AND_IL6_PD_VALIDATION",
          "UNPROVEN_LIVING_CGAS_STING_PSTAT2_ACTIVITY_GIVEN_FLAT_POSTMORTEM_ISGS_AND_ZERO_CORD_ALS_TE"],
         "HOLD_PENDING_NCT04993755_PEER_REVIEWED_DATA_AND_DISAGGREGATED_ORF1P_L1HS_COHORT_STUDY",
         "Motor-ALS cortical ALS-TE=13.53% (41/303; 11.52% non-C9 sALS; 0/331 cord); separates pan-TDP cryptic HDGFL2 from subtype ORF1p/L1HS cargo & longitudinal CSF IL-6 PD (IFNAR2 +0.19 adj_p=0.0376 vs flat TYK2/STAT2/ISGs)",
         "Brain_Penetrant_Allosteric_TYK2_JH2_Inhibitor_BHV8000_Class", "Type_I_IFN_viral_reactivation_herpes_zoster_and_CNS_infection_liability",
         "Requires_confirmed_living_human_CNS_Kpuu_and_active_pSTAT2_target_engagement", "Does_not_inhibit_LINE1_ORF2p_reverse_transcriptase_cDNA_synthesis_upstream_of_IFNAR",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C018", "C1q (C1QA/B/C) Intrathecal Blockade", "Intrathecal_ECM_Anchored_Half_Life_Extended_Anti_C1q_Fab_or_Nanobody",
         "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_HUMAN_SPATIAL_OR_SNRNA", "COARSE_PRIOR_ONLY:Morrison_CSF_turnover_excludes_IV_IgG_and_unmodified_q4w_IT_Fab",
         ["DE_NOVO_ECM_ANCHORED_IT_BIOLOGIC_OR_MICROGLIAL_C1QA_B_DISIRNA_ENGINEERING",
          "NULL_SURVIVAL_PRECEDENT_OF_GLOBAL_C1QA_KO_IN_SOD1_MICE",
          "RISK_OF_DISRUPTING_PROTECTIVE_CBOUTON_AND_NEURONAL_RNP_C1Q_HOMEOSTASIS"],
         "EXPLORATORY_INTRATHECAL_MODALITY_ENGINEERING_AND_SYNAPTIC_SAFETY_GATE",
         "Zhang 55-um MN-niche Visium spots C1QC +2.37 log2FC (spot-level BH=1.04e-10 across N=14 donors); IV ANX005 (10.7% HD autoimmune/SAE withdrawals) and unmodified q4w IT Fab (t1/2~12h) excluded",
         "Intrathecal_Microglial_C1QA_C1QB_2OMOE_ASO_or_LNP_di_siRNA", "Oligonucleotide_induced_innate_TLR_microglial_activation_confounding_complement_suppression",
         "Variable_human_parenchymal_microglial_uptake_efficiency_after_lumbar_IT_bolus", "Slow_clearance_of_pre_deposited_synaptic_C1q_opsonins",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C015", "YKT6 Allele-Split & 14q12 SCFD1/G2E3", "Allele_Specific_Y64C_Sub160Da_Ternary_Fragment_Stabilizer_and_14q12_CRISPRi_Probe",
         "TRL_1_TARGET_TOOL_PROBE_WATCHLIST", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY", "COARSE_PRIOR_ONLY:3KYQ_minus85A3_cavity_and_Cys64_Cys66_geometry",
         ["ZERO_KNOWN_YKT6_LIGANDS_WITH_SUB160DA_SELECTIVE_POTENCY_CEILING",
          "STERIC_EJECTION_RISK_OF_ENDOGENOUS_CYS195_FARNESYL_IN_GT99_9PCT_WT_SALS",
          "PAN_ESSENTIAL_GOLGI_SNARE_CHRONOS_MINUS1_54_TOXICITY_RISK",
          "UNRESOLVED_14Q12_SCFD1_VS_G2E3_CAUSAL_EFFECTOR"],
         "ACADEMIC_BIOPHYSICAL_FRAGMENT_AND_14Q12_CRISPRI_DISSECTION",
         f"YKT6 p.Tyr64Cys Meta P=1.50e-9 (<0.1% carriers); G2E3 excluded from 3-plex ({summarize_gene_offtargets(ot_rows, 'G2E3')})",
         "Exterior_Longin_Exosite_Stabilizer_or_PTAR1_GGTaseIII_Augmentation", "No_validated_druggable_allosteric_exosite_pocket_on_human_YKT6_PDB_3KYQ",
         "Gene_therapy_or_splice_augmentation_of_PTAR1_untested_in_adult_CNS", "May_not_prevent_intramolecular_Cys64_Cys66_disulfide_trapping_in_Y64C_carriers",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C016", "FBXL5 / IRP2 Neuronal Iron Axis", "Neuron_Selective_Non_Chelating_Cytosolic_IRP2_IREB2_Molecular_Glue_Degrader",
         "TRL_1_TARGET_TOOL_PROBE_WATCHLIST", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_HUMAN_SPATIAL_OR_SNRNA", "COARSE_PRIOR_ONLY:Hypothetical_CNS_penetrant_cytosolic_IRP2_molecular_glue_sparing_6VCD_holo_FBXL5",
         ["ZERO_HUMAN_ALS_GENETICS_WITH_FLAT_CORTICAL_AND_SPINAL_NEURONAL_FBXL5_RNA",
          "CLINICAL_FAIR_ALS_II_AND_BYE2025_FAILURE_OF_IRON_CHELATION",
          "HIGH_MW_PROTAC_BBB_EFFLUX_AND_6VCD_2FE2S_CRADLE_FRAGILITY",
          "DEPLETED_ALS_NEURONAL_IREB2_TFRC_RISKS_OMIM_618451_IRON_STARVATION"],
         "WATCHLIST_ONLY_PENDING_SELECTIVE_NON_CHELATING_IRP2_TOOL_PROBES",
         "Edinburgh microglial FBXL5 +0.46 (p=0.00334) vs flat excitatory neuronal FBXL5 (p=0.175) & depleted neuronal TFRC (-0.31, p_mwu=0.0275)",
         "Intrathecal_Partial_IREB2_IRP2_Knockdown_ASO", "Biallelic_human_IREB2_loss_causes_OMIM_618451_neurodegeneration_and_motor_axonopathy",
         "Inability_to_restrict_ASO_uptake_to_iron_overloaded_cells_while_sparing_TFRC_depleted_MNs", "Exacerbates_functional_mitochondrial_FeS_cluster_starvation_in_surviving_neurons",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("BA9-08", "SNPH Axonal Mitochondrial Docking", "Selective_SNPH_KIF5_Axonal_Docking_Release_Peptidomimetic_or_Tool_ASO",
         "TRL_1_TARGET_TOOL_PROBE_WATCHLIST", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_C9FTD_FRACTION_PROTEOMICS", "NONE",
         ["ZERO_HUMAN_ALS_GENETICS_AND_GC_CONFOUNDED_BA9_RNA_DISCOVERY_ORIGIN",
          "UNRESOLVED_PASSIVE_AXONAL_SPHEROID_CO_TRAPPING_WITH_NEFH_BSN_APP",
          "NULL_SURVIVAL_RESCUE_OF_SNPH_KO_IN_SOD1_G93A_MICE",
          "EXTREME_HUMAN_GERMLINE_LOF_INTOLERANCE_PLI_0_996_SOMA_CA2_RISK"],
         "WATCHLIST_ONLY_PENDING_TDP43_SALS_ASSEMBLOID_CAUSALITY_KILLGATE",
         "Spillman C9FTD homogenate DIA +0.46 (padj=0.0329) & pellet +0.60 co-occurs with NEFH pellet +2.13 vs BA4 sALS nuclear RNA -0.89",
         "Small_Molecule_Miro1_RHOT1_Mitochondrial_Motility_Modulator", "Disrupting_activity_dependent_synaptic_mitochondrial_arrest_impairs_local_ATP_buffering",
         "Unvalidated_human_CNS_selectivity_and_narrow_motility_vs_mitophagy_window", "Fails_to_clear_pre_existing_neurofilament_and_organelle_spheroid_jams",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C020", "Apilimod Pulsed PIKfyve Regimen", "Intermittent_Q48_to_Q72h_Oral_Apilimod_Pulsed_PIKfyve_Regimen",
         "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", "COARSE_PRIOR_ONLY:Uncalibrated_human_MN_vacuole_repair_ODE_fails_if_tau_ge_72h",
         ["EMPIRICAL_POSTMITOTIC_HUMAN_IPSC_MN_VACUOLE_AND_CASM_WASHOUT_HALF_LIFE_CALIBRATION",
          "PROOF_OF_ZERO_NFL_GFAP_SURGE_UNDER_PULSED_DOSING_AFTER_CONTINUOUS_BID_CLINICAL_FAILURES",
          "PROSPECTIVE_NON_C9_SALS_RESPONDER_BIOMARKER_BEYOND_2500NM_IN_VITRO_SCREEN"],
         "PRECLINICAL_2WK_HUMAN_IPSC_MN_WASHOUT_KILLGATE_BEFORE_ANY_PULSED_PH1B",
         "Continuous BID falsified (VRG50635 terminated, AIT-101 Wk12/24 NfL +39%/+50%); 2-week postmitotic human iPSC-MN vacuole/CASM washout assay directly tests whether reversible repair outpaces intermittent PIKfyve inhibition",
         "TRPML1_MCOLN1_Small_Molecule_Lysosomal_Efflux_Agonist", "Cytosolic_calcium_overload_and_excitotoxic_stress_in_vulnerable_motor_neurons",
         "Unproven_CNS_therapeutic_window_and_lack_of_human_ALS_target_engagement_biomarkers", "Does_not_directly_generate_signaling_lipid_PI35P2_or_replicate_polyGP_clearance",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C019", "Baricitinib / Selective JAK1 JH1", "Oral_Baricitinib_4mg_or_Brain_Penetrant_JAK2_Sparing_Selective_JAK1_JH1_Inhibitor",
         "TRL_5_HUMAN_ALS_PK_PD_PROVEN", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", "COARSE_PRIOR_ONLY:Unbound_CSF_Hill_pSTAT_8_7pct_occupancy_and_CSF_p80_to_cortical_ALS_Glia_mapping",
         ["HUMAN_4NM_CSF_VS_2500NM_SCREEN_POTENCY_GAP_8_7PCT_CELLULAR_PSTAT_OCCUPANCY",
          "NADALS_1PE_PLUS_1DVT_IN_N9_ALS_THROMBOTIC_SAFETY_LIABILITY",
          "SELECTIVE_JAK1_FORFEITS_AUTONOMOUS_NEURONAL_JAK2_APA_RESCUE_CATCH22",
          "BRIDGED_PGML_IMMUNOASSAY_CALIBRATION_ACROSS_CENTER_DRIFT_AND_RS3831317",
          "UNPROVEN_CSF_P80_TO_CORTICAL_ALS_GLIA_TREATMENT_INTERACTION_PD"],
         "PRECLINICAL_4_TO_50NM_CSF_JAK1_VS_NEURONAL_JAK2_CATCH22_KILLGATE_BEFORE_ANY_STRATIFIED_PH2",
         c019_gate,
         "Homodimeric_JAK2_Sparing_Selective_JAK1_JH1_Inhibitor", "Retains_FDA_JAK_class_VTE_MACE_and_malignancy_boxed_warning",
         "Unproven_human_unbound_CNS_Kpuu_at_clinically_tolerated_oral_doses", "Forfeits_cell_autonomous_excitatory_neuronal_JAK2_coverage",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("S02", "CuATSM Copper-ATSM Complex", "Oral_72mg_CuATSM_Hypoxia_Dissociative_Copper_Radical_Trapping_Complex",
         "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", "COARSE_PRIOR_ONLY:Hypoxic_62Cu_PET_dissociation_vs_intact_53nM_CNS_estimate",
         ["WITHHELD_COMPLETED_PH2_3_NCT04082832_EFFICACY_AND_TERMINATED_NCT04313166_OLE",
          "NULL_6VS6_TREATED_HUMAN_AUTOPSY_PTDP43_AND_MN_DENSITY_PMID_37317638",
          "FORTY_SEVEN_FOLD_NOMINAL_CNS_TO_2500NM_SCREEN_GAP_BOUNDED_BY_144MG_TRANSAMINITIS_MTD",
          "SOD1_COPPER_CHAPERONE_ORIGIN_LACKING_SPORADIC_TDP43_HUMAN_GENETICS",
          "UNVERIFIED_53NM_FERROPTOSIS_RADICAL_TRAPPING_ENGAGEMENT_IN_HUMAN_TDP43_MNS"],
         "HOLD_PENDING_NCT04082832_PUBLIC_DATA_AUDIT_AND_53NM_TDP43_MN_DECONVOLUTION",
         "Bye 2025 2.5 uM sALS iPSC-MN +1.38d (q=0.0338, n=15), but NCT04082832 randomized outcomes remain unreported (hasResults=false), Yang 2023 (n=6 vs 6) autopsies were null, and 62Cu-ATSM PET tracks hypoxic Cu(I) trapping rather than intact 2.5 uM drug",
         "Brain_Penetrant_Catalytic_Radical_Trapping_Antioxidant_Liproxstatin_Class", "Unproven_chronic_human_CNS_safety_and_off_target_CYP_inhibition_risk",
         "Requires_verified_unbound_human_CNS_Kpuu_above_neuronal_ferroptosis_IC90", "Lacks_copper_delivery_to_metal_deficient_mutant_SOD1",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C005", "Stage-Gated MN Excitability Protocol", "Paired_Cortical_TMS_SICI_Lumbar_SDTC_and_CSF_NPTX2_Companion_Protocol",
         "PROTOCOL_COMPANION_NA", "CLINICAL_PROTOCOL_STANDARDIZATION",
         "PROTOCOL_STAGE_GATING_ONLY", "NONE",
         ["STANDARDIZATION_OF_LUMBAR_SDTC_PLUS_CORTICAL_TMS_SICI_AND_CSF_NPTX2_CUTOFFS"],
         "DEPLOY_EXCLUSIVELY_AS_COMPANION_STRATIFICATION_AND_PD_PROTOCOL_FOR_C006",
         "Not an independent NCE; prevents Perampanel-like late-stage LMN hypoexcitability harm when gating C006 KCNQ2",
         "NONE", "", "", "",
         "COMPANION_PROTOCOL_ONLY"),
    ]

    rows: list[dict[str, str | int]] = []
    for rank, (cid, label, p_mod, trl, g_class, ev_basis, mod_dep, hurdles, ind_stage, p3_gate, b_mod, b_warn, b_pk, b_lost, tier) in enumerate(specs, start=1):
        d = dec_map[cid]
        rows.append({
            "priority_rank_overall": rank, "candidate_id": cid, "gene_or_drug": label,
            "primary_modality_specific": p_mod, "phase2_decision_tier": d["decision"], "epistemic_state": d["epistemic_state"],
            "clinical_readiness_trl": trl, "next_gate_experimental_class": g_class,
            "primary_evidence_basis": ev_basis, "model_prior_dependency": mod_dep,
            "unsolved_hurdle_count": len(hurdles), "unsolved_hurdles_structured": ";".join(hurdles),
            "regulatory_ind_staging": ind_stage, "phase3a_safety_or_generalization_gate": p3_gate,
            "backup_modality": b_mod, "backup_class_warning": b_warn, "backup_delivery_pk_hurdle": b_pk, "backup_lost_target": b_lost,
            "scientific_actionability_tier": tier, "analysis_run_id": "RUN-P3A-003",
        })

    out_fp = REG_DIR / "phase3_execution_readiness.csv"
    with out_fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (OUT_DIR / "run_p3a_003_execution_readiness_summary.json").write_text(
        json.dumps({"analysis_run_id": "RUN-P3A-003", "n_programs": len(rows), "rows": rows}, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(f"Wrote {len(rows)} rows to {out_fp}")


if __name__ == "__main__":
    main()
