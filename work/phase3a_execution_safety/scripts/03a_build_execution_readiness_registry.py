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
        f"bulge={r['bulge_1nt_steric_pc_genes']},sub18={r['sub18_core_steric_pc_genes']},flags={r['flagged_constrained_neuronal_hits'].replace('...(+62_more_in_JSON)', '...(+62_more)')})"
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
        f"CHIT1-abundance-adjusted (order-statistic-calibrated) Emory leak-free sALS vs Ctrl OOF AUC={oof['oof_roc_auc']} (n={oof['n_sals']+oof['n_ctrl']}); "
        f"target-site MGH-recalibrated external ALS vs Ctrl AUC={ext_adj['roc_auc']} (LOO={dec_ext['leave_one_mgh_control_out_target_site_recalibrated_auc']}, n={ext_adj['n_total']}; bank-only non-MGH indicator AUC={dec_ext['bank_only_non_mgh_negative_control_auc']}; cross-sectional C9 Symp-vs-Asym AUC={c9_adj['roc_auc']}, n={c9_adj['n_total']}; "
        f"Oh2023 discovery {oh['n_bridge_proteins_fdr_lt_0_05']}/5 FDR<=0.044 [4/5 targeted PRM, CHI3L2 targeted blank; 40/61 discovery overlap]); pure MGH Ctrl drift={mgh_d:+.2f}z & sALS-p80 passes {100*p80['emory_sals_pass_at_sals_p80']:.1f}% Emory sALS; NADALS measured 2h total CSF 1.748 nM (2mg) & 3.804 nM (4mg) vs 50 nM proposed test ceiling"
    )

    # Columns: (cid, label, primary_mod, trl, gate_class, ev_basis, mod_dep, atomic_hurdles, ind_stage, p3_gate, b_mod, b_warn, b_pk, b_lost, tier)
    specs = [
        ("S06", "SARM1 Non-Orthosteric ARM-TIR T-Lock", "Oral_Non_Covalent_Inter_Protomer_ARM_TIR_SARM1_Allosteric_TLock",
         "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
         "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY", "COARSE_PRIOR_ONLY:8mer_MWC_1x_parallel_Bliss_to_2_to_7x_epistatic_bounds",
         ["HUMAN_PH1B_UNBOUND_CSF_KPUU_TROUGH_CADPR_WASHOUT_AND_ZERO_NFL_REBOUND_FOR_TLOCK",
          "PROSPECTIVE_SEQUENCING_EXCLUSION_OF_LT1PCT_CONSTITUTIVE_ARM_BROKEN_GOF_CARRIERS",
          "SOMA_SYNAPSE_DECOUPLING_CEILING_REQUIRING_MUNE_CMAP_AND_NPTX2_BEYOND_NFL_FRAGMENTATION_PD"],
         "SINGLE_ENTITY_ORAL_TLOCK_PH1B_GENOTYPE_GATED_BEFORE_STAGE2_STMN2_COMBINATION",
         "PDB 9TZY 3-chain BEXi adduct 17 filament activation (122/122 sub-IC50 activation with median 8.6x [IQR 5.1-9.7] IC50/C_act shift, PMID:42380237; vs CIPN protection Bosanac et al. 2021 PMID:33964142) excluded; requires prospective gating of clinical allosteric SIR2501 (CTR20253552/NCT07765446/WO2026086928A1), Nura Phase 1 HV covalent allosteric NB-9402 (ACTRN12626000650392/WO2025090514A1), & preclinical intramolecular ASHA-624 via Cys311Ala Cys311-dependence + intact-protein MS covalency checks (vs EV-99 PMID:35994671 / WO2023235719A1) + CD38 plasma cADPR ([MODEL_PRIOR] >90-95% ecto-CD38 fluid share caps 90% selective SARM1 drop at ~5-10%) + 48-72h oral washout + soma-axon decoupling PD (in Collins 2022 PMID:35863521, Sarm1KO lowered Simoa serum NfL & GFAP without rescuing uninjured mSOD1G93A MN somata or survival; in White 2019 PMID:31661035, TDP-43Q331K showed anatomical axon/NMJ protection without rotarod behavioral rescue; TBI-SOD1G93A PMID:39791335 — motivating our project's prospective trial-design choices of non-SOD1 enrollment & MScanFit MUNE/CMAP + CSF NPTX2 monitoring alongside blood NfL) & <1% ARM-GoF (~30-40% residual NADase ceiling at 100x Kd [MODEL_PRIOR]) sequencing gate",
         "Intrathecal_SARM1_RNaseH_Gapmer_ASO", "Gapmer_IT_radiculitis_myelitis_and_CSF_pleocytosis_class_risk",
         "Invasive_chronic_lumbar_IT_dosing_with_5_to_10x_rostral_cortical_gradient", "Slow_axonal_SARM1_protein_clearance_delays_acute_NADase_arrest",
         "TIER_1_ACTIONABLE_NOW"),
        ("S07", "Low-Dose Aldesleukin (IL-2)", "Subcutaneous_Recombinant_Low_Dose_IL2_Aldesleukin",
         "TRL_6_PH2B_SUBGROUP_BIOLOGIC", "BIOMARKER_ENRICHED_PHASE3_EFFICACY_TRIAL",
         "MEASURED_HUMAN_RCT_SUBGROUP", "COARSE_PRIOR_ONLY:Operationalized_MIROCALS_p79_bridging_Schoenfeld_HR070_and_platform_offset_sensitivity",
         ["PRE_PH3_BIOVENDOR_ELISA_TO_CLIA_PNFH_AND_PAIRED_NFL_IMMUNOASSAY_CALIBRATION",
          "PROSPECTIVE_EVENT_DRIVEN_PH3_SURVIVAL_REPLICATION_UNDER_CALIBRATED_CSF_PNFH_LE_3700_PGML"],
         "APPROVED_BIOLOGIC_BIOMARKER_ENRICHED_PH3_RCT",
         "Trautwig 2025 living CSF (n=77 DIA, n=51 overlapping Emory TMT): tryptic MS NEFL vs NEFH r=0.278 (vs clinical immunoassay rho=0.64-0.71 PMID:38683209; serum NfL > serum pNfH on ALSFRS-R slope PMID:32385188; paired CSF-serum pNfH r=0.652 PMID:29054919); MIROCALS (PMID:40354799, N=220, 90 deaths) missed primary unadjusted ITT survival (HR=0.81, p=0.33; reference-point-conditional interaction model adj HR=0.32, p=0.0009; cutoffs described via mmc1.pdf distribution split and 2024 patent WO2024121173A1 iterative survival exploration): <750 pg/mL n=19 (0 deaths), 750-3,700 n=154 (57 deaths, HR=0.52 p=0.016; pooled <=3,700 n=173/220 randomized [78.6% LP; 173/304 = 56.9% of all 304 screened] HR=0.57 p=0.037), >3,700 n=47 (33/90 [36.7%] deaths, HR=1.37 p=0.38; 2.13x 21-mo mortality proportion ratio), interaction p=0.0011 & ALSFRS-R slope interaction F=3.95 p=0.048; Al Khleifat 2026 (PMID:42836993, J Neurol) shows TRICALS shares r^2=12.7% with CSF pNfH (nested pNfH add dChi2=44.39, pNfH x trt dChi2=14.24 vs TRICALS x trt dChi2=4.76) while commercial pNfH platforms span ~1.8x-4.5x scale offsets ([MODEL_PRIOR] hypothetical unbridged 1.8x-4.5x lower CSF cutoff reduces 247-death two-sided alpha=0.05 [one-sided alpha=0.025] directional superiority power from 80% to ~43-50% if HR_high=1.00 or ~14-23% if HR_high=1.37; higher platforms over-exclude 36-86%)",
         "COYA_302_ldIL2_plus_CTLA4Ig_or_IL2_mutein", "Chronic_CTLA4Ig_CD28_blockade_impairs_homeostatic_Treg_survival_and_raises_infection_risk",
         "Enrolled_N137_ALSTARS_NCT07161999_stratifies_3_serum_NfL_tiers_on_24wk_ALSFRSR_without_CSF_pNfH_gate_or_single_agent_IL2_arm", "Dual_biologic_confounds_single_agent_aldesleukin_survival_attribution",
         "TIER_1_ACTIONABLE_NOW"),
        ("C001", "UNC13A Cryptic-Exon Steric SSO", "Intrathecal_Mixed_POPS_2OMOE_Steric_SSO_Promoted_Lead_#2_chr19:17642537-17642554(-)",
         "TRL_3_PRECLINICAL_SSO_COORDINATE", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
         "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY", "COARSE_PRIOR_ONLY:SantaLucia_mixed_POPS_Tm",
         ["SPONSOR_OWNED_ICH_M3R2_SINGLE_ENTITY_GLP_TOX_AND_NHP_CERVICAL_BA4_BIODISTRIBUTION_NO_312_23_REF",
          "PER_TARGET_NDEV_DPCR_AND_CSF_SYNAPTIC_SECRETOME_TE_BIOMARKER_VALIDATION",
          "CLINICAL_CROWDING_DIFFERENTIATION_AND_GENOTYPE_STRATIFIED_6_TO_9MG_POTENCY_GATED_MULTIPLEX_UPTAKE"],
         "PROMOTE_#2_chr19:17642537-17642554(-)_ZERO_LE1MM_CAUTION_PM2_25_EQ_4;_STAGE_2_3PLEX_AFTER_PROPRIETARY_1PLEX_TOX_AND_PD",
         f"{summarize_gene_offtargets(ot_rows, 'UNC13A')} (harmonized pm2_25==0 rule: #2 has 0 spliced/<=50bp-SS 1-mm/wobble/bulge/sub18 hits, 2 unrestricted sense pre-mRNA 1-mm genes, and <=25bp 2-mm pre-mRNA count=4 triggering Caution)",
         "AAV9_U7_snRNA_UNC13A_Cryptic_Exon_Splice_Vector", "Irreversible_AAV_dorsal_root_ganglion_and_hepatotoxicity_class_liability",
         "Low_adult_human_upper_and_lower_MN_intrathecal_AAV_transduction_efficiency", "Cannot_be_withdrawn_or_dose_titrated_upon_innate_immune_meningoradiculitis",
         "TIER_2_FOCUSED_GATE_FIRST"),
        ("C006", "KCNQ2 Exon-5 Steric SSO", "Intrathecal_Mixed_POPS_2OMOE_Steric_SSO_Exon5_Inclusion_Walk_Lead_#3_chr20:63442302-63442319(-)_vs_#1_chr20:63442595-63442616(-)",
         "TRL_3_PRECLINICAL_SSO_COORDINATE", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_TDP43_PATHOLOGY_AND_RESCUE", "COARSE_PRIOR_ONLY:Binomial_tetramer_SantaLucia_Tm_and_unverified_lead3_Intron5_ISS_vs_ISE_polarity",
         ["DENSE_IPSC_MN_EXON5_MICRO_WALK_RESOLVING_INTRON5_ISS_VS_ISE_#3_AGAINST_BYSTANDER_UG8_#1",
          "NHP_CERVICAL_PHRENIC_AND_BA4_CORTICAL_EC80_LE_3MG_STRAND_6_TO_9MG_MULTIPLEX_CA2_DRG_GLP_IT_TOX",
          "HUMAN_EXCITABILITY_PD_LINKED_TO_C005_TMS_SICI_SDTC_AND_CSF_NPTX2_COMPANION_CUTOFFS"],
         "STAGE_1_SPONSOR_OWNED_ICH_M3R2_SINGLE_ENTITY_1PLEX_IND_BEFORE_STAGE2_MULTIPLEX_COFORMULATION",
         f"{summarize_gene_offtargets(ot_rows, 'KCNQ2')} (prior art: QurAlis WO2023102548A1 SEQ IDs 758/759 [#3], 465 [#1], 460 [17/22 #1, Tables 7-9] & Northwestern/UMass WO2024206195A1; Joseph 2025 PMID:41174170 functional rescue used smKCNQ2/ASO2)",
         "Selective_Kv7_2_7_3_Small_Molecule_Opener_QRL101_BHV7000", "Dose_limiting_CNS_somnolence_dizziness_and_urinary_hesitation",
         "Requires_intact_Trp236_S5_pocket_excised_in_DeltaE5_subunits_PDB_7CR2", "ER_retention_and_DeltaE5_Trp236_loss_impose_surface_channel_density_ceiling_on_openers",
         "TIER_2_FOCUSED_GATE_FIRST"),
        ("C002", "STMN2 Cryptic-Exon-2a Steric SSO", "Intrathecal_Mixed_POPS_2OMOE_Steric_SSO_Promoted_Lead_#2_chr8:79616829-79616846(+)",
         "TRL_3_PRECLINICAL_SSO_COORDINATE", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
         "MEASURED_HUMAN_TDP43_PATHOLOGY_AND_RESCUE", "COARSE_PRIOR_ONLY:SantaLucia_Tm_and_1x_parallel_Bliss_to_2_to_7x_MWC_SARM1_bounds",
         ["SPONSOR_OWNED_ICH_M3R2_SINGLE_ENTITY_GLP_TOX_AND_NHP_CERVICAL_BA4_BIODISTRIBUTION_NO_312_23_REF",
          "POST_QRL201_NDEV_TSTMN2_AND_SOLUBLE_SCG10_TE_BIOMARKER_BENCHMARKING",
          "STAGE_2_6_TO_9MG_POTENCY_GATED_MULTIPLEX_UPTAKE_AND_PARALLEL_ORAL_SARM1_TLOCK_STAGING"],
         "PROMOTE_#2_chr8:79616829-79616846(+)_ZERO_LE1MM_CAUTION_PM2_25_EQ_2;_STAGE_2_COMBO_AFTER_PROPRIETARY_1PLEX_TOX_AND_PD",
         f"{summarize_gene_offtargets(ot_rows, 'STMN2')} (harmonized pm2_25==0 rule: #2 has 0 spliced/<=50bp-SS/unrestricted sense pre-mRNA 1-mm/wobble/bulge/sub18 hits and <=25bp 2-mm pre-mRNA count=2 triggering Caution; WO2020247419A2, Harvard/UMass WO2021195446A2, WO2023102242A2)",
         "AAV9_U7_snRNA_STMN2_Exon2a_Splice_Vector", "Irreversible_AAV_DRG_and_hepatotoxicity_liability_while_small_molecule_DLK_stabilizers_caused_clinical_neurotoxicity",
         "Low_adult_human_upper_and_lower_MN_intrathecal_AAV_transduction_efficiency", "Cannot_be_withdrawn_or_dose_titrated_upon_adverse_neuroinflammatory_response",
         "TIER_2_FOCUSED_GATE_FIRST"),
        ("C007", "IL1RL1 / sST2 Decoy Suppression", "Intrathecal_Neurovascular_Shuttled_sST2_3UTR_siRNA_or_Zone1_Intron8_PAS_2OMOE_Steric_SSO",
         "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_SPATIAL_OR_SNRNA", "COARSE_PRIOR_ONLY:Perivascular_sST2_IL33_mass_action_order_of_magnitude",
         ["N25_SALS_VS_N20_CTRL_ISOLATED_MICROVESSEL_AND_OXIMETRY_VERIFIED_CSF_SIMOA_SST2_FREE_IL33_VALIDATION",
          "CNS_RESTRICTED_INTRON8_POLYA_SSO_OR_CTAIL_AA324_328_BIOLOGIC_LEAD_GENERATION_SPARING_LUNG_KIDNEY"],
         "PRECLINICAL_MICROVESSEL_BBB_SIGN_AND_LIVING_CSF_SIMOA_FALSIFICATION_GATE_BEFORE_LEAD_GENERATION",
         "Edinburgh donor-collapsed non-C9 endothelial +3.11 log2CPM (p=0.00698, n=28: 21 non-C9 vs 7 Ctrl, XIST/UTY-verified PMID:42551425; vs null Pineda BA4 vascular +0.075 log2CPM, p=0.918, n=31 PMID:38521060 -> mandates n>=25/20 microvessels + iPSC neurovascular-microglial tri-culture BBB-brake sign gate) + Zhang 55-um MN-niche Visium spots +3.76 (spot-level MAST BH=1.85e-9 across n=14/18 sections, exploratory); Zone 1 PAS #1 chr2:102346045-102346062(+) (mRNA/50bp-SS 0/0; Caution on 25bp-SS 2mm=1) spares Zone 2 Exon-8 5'SS (102343400-102343435(+); nuclear RNase H1 Intron-8 gapmers prohibited); PDB 4KC3 10-Cys/5-SS leaves Cys327 in 324-SKECF-328 unpaired (+ SLC3A2 -SKEDF 4/5 match; selective-sST2 prior art US20080003199A1 & WO2024246589A1), demoting intact-FcRn sweeping mAb to backup; GTEx Lung 140.1 TPM & pan-ST2 astegolimab (ARNASA p=0.068 PMID:42150581) excluded",
         "Intact_FcRn_sST2_CTail_aa324_328_SKECF_Sweeping_Biologic", "Unpaired_Cys327_thiol_adducts_and_SLC3A2_SKEDF_4of5_cterminome_cross_reactivity_risk",
         "Requires_intact_pH6_FcRn_salvage_and_IP_MS_verification_of_unmodified_Cys327_in_living_ALS_CSF", "Monovalent_5aa_tail_binding_14_residues_past_Arg313_lacks_direct_orthosteric_IL33_displacement",
         "TIER_2_FOCUSED_GATE_FIRST"),
        ("C022", "DNAJB2 (HSJ1) Cytosolic Isoform Axis", "Intrathecal_DNAJB2_Internal_Intron9_ISS_IPA_2OMOE_SSO_Promoting_DNAJB2a_Excision",
         "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_C9FTD_FRACTION_PROTEOMICS", "COARSE_PRIOR_ONLY:Unverified_internal_intron9_ISS_IPA_polarity_and_DNAJB2b_3UTR_ERAD_ceiling",
         ["SPORADIC_ALS_SPINAL_CORD_DNAJB2A_VS_DNAJB2B_PRECURSOR_POOL_PRM_REPLICATION",
          "EMPIRICAL_952BP_INTERNAL_INTRON9_ISS_IPA_WALK_WITH_3UTR_AND_BIP_CHOP_ERAD_DNAJB2B_COUNTERSCREEN",
          "COMPARTMENT_SELECTIVE_MN_VS_OLIGODENDROCYTE_CYTOSOLIC_DNAJB2A_STOICHIOMETRY"],
         "PRECLINICAL_SALS_CORD_PRECURSOR_POOL_GATE_AND_INTERNAL_INTRON9_WALK_VS_AAV_DNAJB2A_BEFORE_IND",
         "GENCODE v46 Intron-9 chr2:219284836-219285986(+) excised in cytosolic DNAJB2a (ENST00000392086.8, 277 aa, Exon 10 219285987-219286898(+)) vs retained in ER-CAAX DNAJB2b (ENST00000336576.10, 324 aa); restricts SSO walk to internal Intron-9 chr2:219284988-219285939(+) (sparing 5'SS, Zone A CDS & 3'SS/branchpoint 219285940-219285986) with mature DNAJB2b 3'-UTR & BiP/CHOP ERAD counter-screens vs pan-CNS/oligo AAV-DNAJB2a cDNA (PMID:26936937; rodent Ly6a CAP-B10 caveat)",
         "Pan_CNS_or_Oligodendrocyte_Tropic_AAV_Cytosolic_DNAJB2a_cDNA_Replacement", "Irreversible_AAV_dorsal_root_ganglion_and_hepatotoxicity_plus_supraphysiologic_chaperone_titration_risk",
         "Low_adult_human_corticospinal_and_spinal_MN_AAV_transduction_efficiency", "Lacks_endogenous_promoter_stoichiometry_and_cannot_be_withdrawn_once_dosed",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C014", "ESCRT-III Nuclear-Pore Surveillance (CHMP7 / CHMP2B)", "Selective_Peptidomimetic_or_Allosteric_SUN1_CHMP7_Nuclear_Import_Blocker",
         "TRL_1_TARGET_TOOL_PROBE_WATCHLIST", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_C9FTD_FRACTION_PROTEOMICS", "COARSE_PRIOR_ONLY:Uncalibrated_35_to_50pct_partial_CHMP7_knockdown_safety_window",
         ["NO_VALIDATED_SMALL_MOLECULE_OR_PEPTIDOMIMETIC_SUN1_CHMP7_IMPORT_BLOCKER",
          "EXTREME_ESSENTIALITY_SATB2_LEMD2_SYNAPTIC_AND_ANXA11_MEMBRANE_REPAIR_LIABILITY",
          "SPORADIC_ALS_HUMAN_MN_PELLET_PARTITIONING_REPLICATION_BEYOND_N3_C9FTD_IPSC"],
         "EXPLORATORY_TOOL_COMPOUND_AND_TITRATED_KD_SAFETY_SCREEN",
         "Spillman within-C9FTD iPSC pellet-vs-homogenate CHMP2B +0.89 (p=0.00114, padj=0.0205, n=3 C9FTD; between-genotype pellet +0.57 padj=0.325 NS) vs ANXA11 -0.88 (padj=0.0325) & null CHMP7 across all fractions; gnomAD v4.1 MANE CHMP7 LOEUF=0.496 (pLI=0.984) restricts partial KD to 1-based Exon-11 3'-UTR chr8:23260600-23261999(+)",
         "Titrated_Partial_35_to_50pct_Intrathecal_CHMP7_Knockdown_ASO", "Narrow_margin_against_SATB2_LEMD2_chromatin_detachment_and_IT_gapmer_radiculitis",
         "Cannot_guarantee_uniform_35_to_50pct_knockdown_across_lumbar_vs_cortical_motor_neurons", "Leaves_insoluble_CHMP2B_ANXA11_membrane_repair_defect_unaddressed",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("S09", "Censavudine (TPN-101) / LINE-1 RT", "Oral_Nucleoside_LINE1_RT_Inhibitor_Censavudine_TPN101",
         "TRL_5_HUMAN_ALS_PK_PD_PROVEN", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE",
         "MEASURED_HUMAN_SPATIAL_OR_SNRNA", "NONE",
         ["UNPUBLISHED_PEER_REVIEWED_MIXED_N42_ALS_FTD_NCT04993755_AND_HEALEY_PH2_3_SPORADIC_EFFICACY",
          "DISAGGREGATED_PAN_TDP43_HDGFL2_VS_SUBTYPE_ORF1P_L1HS_ENRICHMENT_AND_IL6_PD_VALIDATION",
          "POSTMITOTIC_MN_VS_GLIAL_TPN101_TP_TRIPHOSPHORYLATION_AND_LIVING_CGAS_STING_PSTAT2_ACTIVITY"],
         "HEALEY_PH2_3_SPORADIC_ALS_TE_BIOMARKER_GATING_AND_NCT04993755_PEER_REVIEWED_AUDIT",
         "Selected May 2025 for Phase 2/3 HEALEY ALS Platform Trial following mixed N=42 C9orf72 ALS/FTD NCT04993755 (randomized 24-wk ALSFRS-R -7.2 vs -6.7 NS alongside slower SVC decline & CSF IL-6/NfL signals) & PSP NCT04993768; cortical ALS-TE=13.40% (41/306 all motor-ALS; 13.53%=41/303 non-discordant; 11.52%=22/191 C9-neg ALS+ALS/FTD [11.60%=21/181 C9-neg ALS]; spinal ALS-TE prevalence not estimable under O'Neill 2-class Glia-cord/Ox-cord spinal classifier, N=331); gates MN vs glial TPN-101-TP phosphorylation & ALS-validated ORF1p/L1HS enrichment (noting PMID:40050409 validated blood ORF1p in ovarian carcinoma)",
         "Dual_TYK2_JAK1_JH1_Inhibitor_BHV8000_Class_or_Selective_TYK2_JH2_Probe", "Type_I_IFN_viral_reactivation_plus_BHV8000_JAK1_inhibition_of_neurotrophic_gp130_STAT3",
         "Requires_confirmed_living_human_CNS_Kpuu_and_active_pSTAT2_target_engagement", "Does_not_inhibit_LINE1_ORF2p_reverse_transcriptase_cDNA_synthesis_upstream_of_IFNAR",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C018", "Classical Complement C1q (C1QA/B/C)", "Intrathecal_ECM_Anchored_Half_Life_Extended_Anti_C1q_Fab_or_Nanobody",
         "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_HUMAN_SPATIAL_OR_SNRNA", "COARSE_PRIOR_ONLY:Two_compartment_CSF_turnover_excludes_IV_IgG_and_unmodified_q4w_IT_Fab",
         ["DE_NOVO_ECM_ANCHORED_IT_BIOLOGIC_OR_MICROGLIAL_C1QA_B_DISIRNA_ENGINEERING",
          "NULL_SURVIVAL_PRECEDENT_OF_GLOBAL_C1QA_KO_IN_SOD1_MICE",
          "RISK_OF_DISRUPTING_PROTECTIVE_CBOUTON_AND_NEURONAL_RNP_C1Q_HOMEOSTASIS"],
         "EXPLORATORY_INTRATHECAL_MODALITY_ENGINEERING_AND_SYNAPTIC_SAFETY_GATE",
         "Zhang 55-um MN-niche Visium spots C1QC +2.37 log2FC (spot-level MAST BH=1.04e-10 across N=14 donors, exploratory); HD NCT04514367 (PMID:41787606, N=28) proved ~0.2-0.25% IV ANX005 CSF:serum entry saturates CSF C1q while recording 3 treatment-related AE withdrawals and 2 treatment-related SAEs (abstract lists lupus + AIHA; Results/Table 2/SEC filing list SLE + drug-induced pneumonitis; peripheral ~180 nM C1q sink hypothesized [MODEL_PRIOR]), completed open-label ALS NCT04569435 (17 actual participants in CT.gov registry; sponsor 2024 10-K reports 13 treated for 12 wks, 7 continuing to 24 wks, with C1q target engagement and downstream complement reduction in blood and an exploratory sponsor-reported subgroup observation of less ALSFRS-R decline & blood NfL stabilization without a control arm), Lobsiger 2013 PMID:24170856 showed C1qa-/- failed to extend SOD1 survival with compensatory synapse loss, and unmodified q4w IT Fab clears via CSF turnover (t1/2~12h)",
         "Intrathecal_Microglial_C1QA_C1QB_2OMOE_ASO_or_LNP_di_siRNA", "Oligonucleotide_induced_innate_TLR_microglial_activation_confounding_complement_suppression",
         "Variable_human_parenchymal_microglial_uptake_efficiency_after_lumbar_IT_bolus", "Slow_clearance_of_pre_deposited_synaptic_C1q_opsonins",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C015", "chr14q12 GWAS Locus (SCFD1 / G2E3)", "Bidirectional_CRISPRi_CRISPRa_chr14q12_SCFD1_vs_G2E3_Effector_Dissection",
         "TRL_1_TARGET_TOOL_PROBE_WATCHLIST", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY", "NONE",
         ["CATASTROPHIC_ALU_0MM_OFFTARGETS_ON_G2E3_INTRON1_WINDOWS",
          "PROVISIONAL_POSSIBLE_OPPOSITE_SIGN_MN_VS_IMGL_SCFD1_EQTL_ASSOCIATIONS",
          "PAN_ESSENTIAL_SCFD1_CHRONOS_MINUS1_26_AND_ZERO_SELECTIVE_LIGANDS"],
         "ACADEMIC_14Q12_CELLTYPE_CRISPRI_CRISPRA_AND_SECRETORY_DISSECTION",
         f"Human iMGLs (261 initial lines from 254 donors -> n=189 untreated, n=188 IFN-gamma & n=188 LPS eQTL donors) show sole chr14q12 SCFD1 colocalization PP.H4=0.8764-0.8899 (same rs229143-A allele beta=-0.2955 untreated, -0.2164 IFN-gamma, -0.3107 LPS vs Answer ALS MN +0.0476 [Table S8 adj p=1.93e-32, motif-suggested ISL1 footprint]; shared rs229194-A/rs229195-A -0.2920/-0.2237/-0.3061; targeted 251-gene NeuroKO FDR=0.9284 null, PMID:43045849, EV-P4-007; within-donor causality & sALS treatment direction open); G2E3 (AF-Q7L622-F1 only; active PHD2/3 RINGs PMID:18511420) excluded from 3-plex ({summarize_gene_offtargets(ot_rows, 'G2E3')})",
         "Selective_SM_Chaperone_or_G2E3_PHD_RING_Chemical_Probe", "Promiscuous_kinome_off_target_liability_CHEMBL3752910_EPHA3_0_3nM",
         "Unproven_CNS_cell_type_selectivity_between_motor_neurons_and_microglia", "Cannot_resolve_provisional_MN_vs_myeloid_chr14q12_allelic_sign_without_genetic_perturbation",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C023", "YKT6 (p.Tyr64Cys Longin R-SNARE)", "Allele_Specific_Y64C_Ternary_Pocket_Stabilizer_or_WT_Longin_Exosite_Chaperone",
         "TRL_1_TARGET_TOOL_PROBE_WATCHLIST", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY", "COARSE_PRIOR_ONLY:Rat_3KYQ_plus85A3_cavity_expansion_and_Cys64_Cys66_geometry",
         ["ZERO_KNOWN_YKT6_LIGANDS_WITH_RESTRICTED_CAVITY_POTENCY_CEILING",
          "STERIC_EJECTION_RISK_OF_ENDOGENOUS_CYS195_FARNESYL_IN_NON_CARRIER_WT_SALS",
          "PAN_ESSENTIAL_GOLGI_SNARE_CHRONOS_MINUS1_54_TOXICITY_RISK",
          "LOW_PREVALENCE_Y64C_RS138273846_CARRIER_FREQUENCY_IN_SPORADIC_ALS"],
         "ACADEMIC_BIOPHYSICAL_19FNMR_TERNARY_FRAGMENT_SCREEN",
         "YKT6 p.Tyr64Cys (rs138273846, chr7:44206388:A>G, AVI=24.53, gnomAD v4.1 AF=0.061%; Hop 2026 PMID:41917433 discovery case allele frequency 48/26,276=0.183%) Meta P=1.50e-9 (rat DPC-bound PDB 3KYQ, [MODEL_PRIOR] +85.1 A^3 cavity expansion PMID:20159557 vs human open PDB 6J74 PMID:32128853) + TDP-43 3'UTR lengthening (padj=4.57e-40) & PTAR1 170-bp Exon-2 skip (MOESM11 line 4145, dPSI=+0.1563, source MAJIQ 'FDR' [p_d_psi_0.05]=3.256e-6); cis-Golgi SNARE partners (NSF/STX5) pan-essential",
         "Exterior_Longin_Exosite_Stabilizer_or_PTAR1_GGTaseIII_Augmentation", "No_validated_druggable_allosteric_exosite_pocket_on_YKT6_rat_3KYQ_or_human_6J74",
         "Gene_therapy_or_splice_augmentation_of_PTAR1_untested_in_adult_CNS", "May_not_prevent_intramolecular_Cys64_Cys66_disulfide_trapping_in_Y64C_carriers",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C016", "FBXL5 / IRP2 Cell-Type Iron-Sensor Axis", "Cell_Type_Resolved_Bidirectional_FBXL5_IRP2_Iron_Sensor_Probe",
         "TRL_1_TARGET_TOOL_PROBE_WATCHLIST", "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
         "MEASURED_HUMAN_SPATIAL_OR_SNRNA", "COARSE_PRIOR_ONLY:Bidirectional_MN_starvation_vs_microglial_overload_sensor_polarity_PDB_3V5Z_6VCD",
         ["ZERO_HUMAN_ALS_GENETICS_WITH_FLAT_NEURONAL_VS_ELEVATED_GLIAL_FBXL5_RNA",
          "UNREPORTED_FAIR_ALS_II_NCT03293069_PD_FAIRPARK_II_WORSENING_AND_BYE2025_CHELATION_FAILURE",
          "DEPLETED_ALS_NEURONAL_IREB2_TFRC_RISKS_OMIM_618451_IRON_STARVATION_UNDER_IRP2_DEGRADATION",
          "DUAL_COFACTOR_3V5Z_FE_O_FE_AND_6VCD_2FE2S_CRADLE_FRAGILITY_LACKING_SELECTIVE_PROBES"],
         "WATCHLIST_ONLY_PENDING_BIDIRECTIONAL_MN_VS_IMGL_IRON_SENSOR_SIGN_DISSECTION",
         "Edinburgh donor-collapsed microglial FBXL5 +0.46 (p=0.00334, n=33) vs flat excitatory neuronal FBXL5 (p=0.175, n=34) & depleted neuronal TFRC (-0.31, p_mwu=0.0275) + cortical IREB2 (-0.62, p=0.0259); PDB 6VCD (PMID:32126207) + paired Deferiprone +0.243d (p=0.3751) & PD FAIRPARK-II worsening (PMID:36449420) pivot C016 to bidirectional sensor probing",
         "Lineage_Restricted_CRISPRi_CRISPRa_FBXL5_IREB2_Sign_Dissection", "Biallelic_IREB2_loss_causes_OMIM_618451_neurodegeneration_while_FBXL5_loss_causes_iron_overload",
         "Genetic_perturbation_tool_only_lacking_clinical_CNS_cell_type_selective_delivery", "Cannot_separate_acute_post_translational_iron_sensing_from_chronic_transcriptional_compensation",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C020", "Apilimod Pulsed PIKfyve Regimen", "Intermittent_Q48_to_Q72h_Oral_Apilimod_Pulsed_PIKfyve_Regimen",
         "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", "COARSE_PRIOR_ONLY:Bifurcated_PKPD_ODE_79pct_osmotic_deadzone_vs_30_to_0pct_coupled_PI3P_LRRK2_CASM",
         ["EMPIRICAL_POSTMITOTIC_HUMAN_IPSC_MN_VACUOLE_AND_CASM_WASHOUT_HALF_LIFE_CALIBRATION",
          "PROOF_OF_ZERO_NFL_GFAP_SURGE_UNDER_PULSED_DOSING_AFTER_CONTINUOUS_BID_NFL_AND_VRG50635_SIGNALS",
          "INTRACELLULAR_VS_SECRETED_DPR_MASS_BALANCE_AND_NANOMOLAR_TO_2500NM_SALS_POTENCY_GAP",
          "PROSPECTIVE_NON_C9_SALS_RESPONDER_BIOMARKER_BEYOND_2500NM_IN_VITRO_SCREEN"],
         "PRECLINICAL_2WK_HUMAN_IPSC_MN_WASHOUT_FALSIFICATION_GATE_BEFORE_ANY_PULSED_PH1B",
         "Separates C9-ALS biomarker Ph2a NCT05163886 (Babu et al. 2024 Brain PMID:38606777, N=15: met safety/PK with 0 drug-related SAEs, Wk12 CSF 1.63 ng/mL [3.89 nM free-base eq, n=9/10 randomized treated], -73% [-74.4% CT.gov] CSF poly(GP), and Babu Table 3 shared-baseline repeated-measures mixed-model plasma sGPNMB ratio 2.31 [95% CI 1.56-3.41, p<0.001] vs CSF sGPNMB ratio 0.92 [90% CI 0.80-1.07, p=0.352 NS; both separately labeled 2-sided t-test on CT.gov], alongside exploratory active-arm Wk12 plasma NfL median +39% [102->142, n=9] and Wk24 OLE CSF NfL mean +50% [6,707->10,041, n=4; Wk12 CSF mean 6,373] without randomized clinical futility) from distinct inhibitor VRG50635 (NCT06215755, 54 enrolled / 50 treated, terminated for lack of risk-benefit data with investigator-reported treatment-related SAEs in 8/50 [16.0%] treated participants & exploratory GFAP/NfL rises in AAN2026-003396 + HV MAD NL81735.056.22 2/6 drug SAEs PMID:41708347) and months-long intrathecal PIKFYVE ASO AS-202 (PMID:29400714; PMID:36754049); [MODEL_PRIOR] q48h/q72h passes ~79% (64/81) in decoupled osmotic Model 1 vs ~30% (24/81) at matched 10-20h repair and 0% (0/81) at 24-48h postmitotic repair in zero-dead-zone coupled +PI(3)P->LRRK2/CASM Model 2 (PMID:42900584; PMID:42994990), mandating 14-day human iPSC-MN washout + secreted DPR mass-balance gate",
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
         "PRECLINICAL_4_TO_50NM_CSF_JAK1_VS_NEURONAL_JAK2_CATCH22_FALSIFICATION_GATE_BEFORE_ANY_STRATIFIED_PH2",
         c019_gate,
         "Homodimeric_JAK2_Sparing_Selective_JAK1_JH1_Inhibitor", "Retains_FDA_JAK_class_VTE_MACE_and_malignancy_boxed_warning",
         "Unproven_human_unbound_CNS_Kpuu_at_clinically_tolerated_oral_doses", "Forfeits_cell_autonomous_excitatory_neuronal_JAK2_coverage",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("S02", "CuATSM Copper-ATSM Complex", "Oral_72mg_CuATSM_Hypoxia_Dissociative_Copper_Radical_Trapping_Complex",
         "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE",
         "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", "COARSE_PRIOR_ONLY:Hypoxic_62Cu_PET_dissociation_vs_modeled_53nM_intact_CNS_prior",
         ["UNREPORTED_PH2_3_NCT04082832_UNKNOWN_AND_COMPLETED_N55_NCT04313166_OLE_OUTCOMES",
          "NULL_5VS4_ALSTDP_PLUS_1VS2_SOD1_TREATED_HUMAN_AUTOPSY_PMID_37317638",
          "FORTY_SEVEN_FOLD_MODELED_53NM_CNS_TO_2500NM_SCREEN_GAP_BOUNDED_BY_144MG_TRANSAMINITIS_MTD",
          "SOD1_COPPER_CHAPERONE_ORIGIN_LACKING_SPORADIC_TDP43_HUMAN_GENETICS",
          "UNVERIFIED_53NM_FERROPTOSIS_RADICAL_TRAPPING_ENGAGEMENT_IN_HUMAN_TDP43_MNS"],
         "HOLD_PENDING_NCT04082832_PUBLIC_DATA_AUDIT_AND_53NM_TDP43_MN_DECONVOLUTION",
         "Bye 2025 2.5 uM sALS iPSC-MN +1.38d (q=0.0338, n=15), while NCT04082832 (status UNKNOWN) and completed OLE NCT04313166 (N=55 actual) have no posted results (hasResults=false), Yang 2023 mixed autopsy series (5 vs 4 ALS-TDP p=0.1 + 1 vs 2 SOD1; PMID:37317638) showed unaltered neuronal pTDP-43/MN counts alongside more cortical p62+ astrocytes & fewer spinal Iba1+ microglia, and 62Cu-ATSM PET tracks hypoxic Cu(I) transchelation rather than [MODEL_PRIOR] 53.2 nM intact drug",
         "Brain_Penetrant_Catalytic_Radical_Trapping_Antioxidant_Liproxstatin_Class", "Unproven_chronic_human_CNS_safety_and_off_target_CYP_inhibition_risk",
         "Requires_verified_unbound_human_CNS_Kpuu_above_neuronal_ferroptosis_IC90", "Lacks_copper_delivery_to_metal_deficient_mutant_SOD1",
         "TIER_3_EXPLORATORY_DISCOVERY"),
        ("C005", "Stage-Gated MN Excitability Protocol", "Paired_Cortical_TMS_SICI_Lumbar_SDTC_and_CSF_NPTX2_Companion_Protocol",
         "PROTOCOL_COMPANION_NA", "CLINICAL_PROTOCOL_STANDARDIZATION",
         "PROTOCOL_STAGE_GATING_ONLY", "NONE",
         ["PARADIGM_LOCKED_TT_SICI_LE_5_5PCT_RMT_LUMBAR_SDTC_AND_CLSI_EP09C_CSF_NPTX2_CALIBRATION"],
         "DEPLOY_AS_COMPANION_STRATIFICATION_AND_PD_RESEARCH_PROTOCOL_FOR_C006",
         "Companion research protocol rather than an independent NCE: pairs threshold-tracking TT-SICI <=5.5% RMT (PMID:42592079; non-interchangeable with amplitude-ratio SICI^-1 PMID:33226425), lumbar SDTC, and CLSI EP09c-bridged CSF NPTX2 (dropping unvalidated CSF GRIA4) to test excitability-biomarker prevalence and treatment interaction in C006 KCNQ2 without prematurely excluding marker-negative participants",
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
