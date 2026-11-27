"""Evidence, SHA-256 statistical contrast, and Living Research Log specs (UPD-2026-11-27-01/02) for ExploreALS v1.5.0."""
from __future__ import annotations

LIVING_V15_EVIDENCE_ROWS: list[dict[str, str]] = [
    {
        "evidence_id": "EV-LIV-003",
        "carbon_id": "L02",
        "subnode_id": "",
        "analysis_run_id": "RUN-P4-006",
        "source_type": "PRIMARY_SPLICING_AND_PROTEOMIC_RECOMPUTE",
        "source_id_or_locator": "DS_CRYPTIC;DS001_COUNTS;DS_BRYCE_APA;DS029_SPILL;PMID:35197628;PMID:41028049;PMID:40737092;PMID:34031600;GSE315972",
        "cohort_and_stratum": "Brown 2022 i3Neuron TDP-43 KD MAJIQ (corroborated by Spiteri 2025 4-region human sALS TMTpro & NYGC motor cortex/cord OLS, n=212/232)",
        "assay_and_contrast": "Header-resolved MAJIQ Intron-15 retention (chr11:71484448-71485541) + corroborating 4-region CNS TMTpro protein & donor-collapsed NYGC OLS",
        "effect_direction": "TDP43_INTRON15_RETENTION_AND_PAN_CNS_PROTEIN_DEPLETION",
        "effect_estimate": "Brown Intron-15 IR deltaPSI=+0.4255 (0.033->0.445, source MAJIQ 'FDR' [p_d_psi_0.05]=6.853e-20; canonical -0.5365, source MAJIQ 'FDR'=3.33e-16); corroborating Spiteri 4-region mean per-region -0.5610 (sum -2.244, adj p=0.00519; all 4 regions adj p<=0.023) & NYGC motor cortex OLS adj beta=-0.2548 (adj p=0.000381, n=212)",
        "p_value": "",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "",
        "epistemic_weight": "HIGH",
        "notes": (
            "Brown 2022 MOESM11 LSV ENSG00000172890.12:t:71485542-71485648: unannotated Intron-15 retention chr11:71484448-71485541 deltaPSI=+0.4255 (source MAJIQ 'FDR'=6.85e-20), canonical chr11:71484447-71485542 drops 0.966->0.450 (deltaPSI=-0.5365, source MAJIQ 'FDR'=3.33e-16), novel donor chr11:71485324-71485542 +0.0753 (source MAJIQ 'FDR'=1.14e-4), while acute i3Neuron total RNA (+0.481, adj p=2.00e-15) and Ribo-seq (+0.332, adj p=0.999) are not depleted. "
            "Corroborating human CNS cross-cohorts (locked in RUN-P4-006 JSON): Spiteri 2025 (PMID:41028049) depletes NADSYN1 across all 4 CNS regions (mean per-region -0.5610 [4-region sum contrast -2.244], p=5.65e-5 adj p=0.00519; cervical adj p=0.0214; lumbar adj p=0.0229; motor cortex -0.5361 adj p=0.0163; thoracic -0.5950 adj p=0.00993) while NAMPT rises (+0.711 p=0.0232; thoracic +1.045 p=0.0036); "
            "NYGC motor cortex All ALS vs Ctrl OLS adj beta=-0.2548 (adj p=0.000381, raw -0.4110 Welch p=4.37e-7, n=212; cord raw -0.3803 p=9.86e-7, OLS -0.1231 adj p=0.0821, n=232); Bolger GSE315972 BA46 Iso-Seq novel BambuTx1078 (mean 1.80 vs 0.00 CPM) & BambuTx13669 (0.74 vs 0.00 CPM); Dargan 2025 neurite -0.3841 (Welch p=0.00417, PMID:40737092); Tian 2021 CRISPRi survival -2.92 (p=0.0337, PMID:34031600); Kozareva 2025 (preprint, DOI:10.1101/2025.09.29.679403) S6 postmortem missplicing without cryptic-exon confirmation; Bryce-Smith APA non-selective (100% vs 37.2%); Spillman C9-FTD DIA null (homog p=0.500, synapt p=0.300)."
        ),
    },
    {
        "evidence_id": "EV-LIV-004",
        "carbon_id": "L02",
        "subnode_id": "",
        "analysis_run_id": "RUN-P4-006",
        "source_type": "STRUCTURAL_AND_GENE_LIABILITY_SYNTHESIS",
        "source_id_or_locator": "DS_PDB_NADSYN1_CYFIP2;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;PMID:31911602;PMID:31883644;PMID:38357931;PMID:35641224",
        "cohort_and_stratum": "RCSB PDB 6OFB (2.84A human NADSYN1 octamer + NaAD/AMP/pyrophosphate [POP]) + AF-Q6IA69-F1 + GENCODE v46 MANE + gnomAD v4.1",
        "assay_and_contrast": "Exon-16 (chr11:71485542-71485648, aa 486-521) catalytic <=4.0A ligand-contact mapping + human autosomal recessive VCRL3 & salvage-pathway review",
        "effect_direction": "DIRECT_ACTIVE_SITE_DISRUPTION_WITH_SALVAGE_REDUNDANCY_GATE",
        "effect_estimate": "PDB 6OFB (2.84A): Exon 16 (aa 486-521) directly encodes 6 catalytic <=4.0A contacts (NaAD/DND: Arg487 2.11A [2.84A crystal model], Gln498 3.48A, Leu510 3.11A, Leu511 3.56A; AMP: Arg489 3.14A, Ser515 3.83A); gnomAD v4.1 MANE LOEUF=1.010, pLI=4.63e-23",
        "p_value": "",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "",
        "epistemic_weight": "HIGH_STRUCTURAL",
        "notes": (
            "GENCODE v46 MANE_Select ENST00000319023.7 (706 aa) maps Exon 15 (chr11:71484312-71484447, aa 440-485) and Exon 16 (chr11:71485542-71485648, 107 bp, aa 486-521) directly across TDP-43-retained Intron 15. "
            "In 2.84A human NADSYN1 PDB 6OFB (Chuenchor 2020 Nat Commun PMID:31911602; AF-Q6IA69-F1 mean pLDDT=95.92, 98.0% >=70), Chain A binds 20 residues <=4.0A to DND (NaAD+), 10 to AMP, and 6 to pyrophosphate (POP), with Arg487 (2.11A in 2.84A crystal model), Arg489, Gln498, Leu510, Leu511, and Ser515 inside Exon 16. "
            "Bi-allelic human LoF causes lethal autosomal recessive congenital NAD deficiency VCRL3 (OMIM 618845; Szot 2020 PMID:31883644, Szot 2024 PMID:38357931), while heterozygous LoF is tolerated (LOEUF=1.010, 80/95.4 obs/exp, missense Z=1.18). "
            "Zero occurrences in WO2023237638A1, WO2023222858A1, or Guo 2026 (PMID:42234776); supplemental splicing mention in Imaizumi 2022 (PMID:35641224) and cataloged in Sinha 2026 [Review] (PMID:42135847). Dominant NAMPT->NMNAT2 salvage redundancy gates therapeutic priority."
        ),
    },
    {
        "evidence_id": "EV-LIV-005",
        "carbon_id": "L03",
        "subnode_id": "",
        "analysis_run_id": "RUN-P4-006",
        "source_type": "PRIMARY_MULTIOMIC_SPATIAL_AND_PROTEOMIC_RECOMPUTE",
        "source_id_or_locator": "DS_CRYPTIC;DS001_COUNTS;DS029_SPILL;PMID:35197628;PMID:41028049;PMID:40713859;PMID:40737092;GSE330224;GSE330130",
        "cohort_and_stratum": "NYGC Visium lumbar ventral horn (n=24 ALS vs 8 Ctrl; n=25 [20 vs 5] complete-covariate OLS) + NYGC bulk cord (n=232) + Brown Ribo-seq + Kozareva 2025 (preprint) S1/S6 + Spiteri motor cortex + Miedema FTLD-TDP-C + Dargan neurite",
        "assay_and_contrast": "Donor-collapsed lumbar ventral-horn Visium OLS (gc+sex+age+pmi; no neuronal-proportion term) + multi-cohort human TDP-43 protein/Ribo-seq & reciprocal CYFIP1 paralog check",
        "effect_direction": "CONCORDANT_CORTICAL_SPINAL_AND_TRANSLATION_DEPLETION_WITH_CYFIP1_COMPENSATION",
        "effect_estimate": "NYGC Visium lumbar ventral horn raw=-0.6792 (Welch p=0.00174, n=32; complete-covariate OLS n=25 [20 vs 5] adj beta=-0.8613, adj p=0.00777); NYGC cord OLS -0.1276 (adj p=0.00224, n=232); Brown Ribo-seq -1.3743 (adj p=1.68e-14); Kozareva 2025 (preprint) S1 prot -0.4678 (adj p=0.0204); Spiteri motor cortex -0.3042 (adj p=0.0476); Miedema FTLD -0.3598 (q=3.02e-8)",
        "p_value": "0.001745",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "32",
        "epistemic_weight": "HIGH",
        "notes": (
            "NYGC GSE330224 lumbar spinal cord Visium ventral horn (24 ALS vs 8 Ctrl, n=32): CYFIP2 raw diff=-0.6792 log2CPM (Welch p=0.001745, MWU p=0.002024; gc_z+sex+age+pmi complete-covariate OLS n=25 [20 ALS vs 5 Ctrl] adj beta=-0.8613, SE=0.2895, adj p=0.00777; does not adjust for neuronal proportion, so alpha-MN attrition confounding remains open); NYGC GSE330130 lumbar spinal microglia (11 vs 9) -0.7796 (Welch p=0.00510, OLS adj p=0.0290; ambient neuronal RNA caveat; Motor_Neurons at min_cells=10 has only 4v1 donors); NYGC bulk cord (n=232) OLS -0.1276 (adj p=0.00224; motor cortex adj p=0.519). "
            "Triple-concordant protein loss: Kozareva 2025 (preprint, DOI:10.1101/2025.09.29.679403) S1 iNeuron (-0.4678, p=0.00238, adj p=0.0204; RNA -0.6688 adj p=1.81e-41; S6 postmortem cryptic-exon confirmed), Spiteri motor cortex (-0.3042, p=0.00370, adj p=0.0476; spinal regions NS), Miedema FTLD-TDP-C (-0.3598, q=3.02e-8); Brown Ribo-seq (-1.3743, adj p=1.68e-14) & non-NMD-blocked canonical Exon 19-20 loss (-0.1191, source MAJIQ 'FDR'=4.03e-6) + distal 515-bp Intron-19 segment retention downstream of novel donor chr5:157330227 (+0.0784, source MAJIQ 'FDR'=9.66e-5; full Intron 19 is 2,692 bp); Dargan 2025 neurite (-0.7840, Welch p=0.000111, PMID:40737092); Spillman synaptosome (-0.282, p=0.113). "
            "Crucial caveat: paralog CYFIP1 is reciprocally upregulated in Kozareva 2025 (preprint) S1 (+0.9291, adj p=0.00362), Miedema (+0.2639, q=1.31e-7), and Spillman homogenate (+0.2735, p=0.0373)."
        ),
    },
    {
        "evidence_id": "EV-LIV-006",
        "carbon_id": "L03",
        "subnode_id": "",
        "analysis_run_id": "RUN-P4-006",
        "source_type": "STRUCTURAL_AND_GENE_LIABILITY_SYNTHESIS",
        "source_id_or_locator": "DS_PDB_NADSYN1_CYFIP2;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;PMID:21107423;PMID:29534297;PMID:39660913;PMID:35197626",
        "cohort_and_stratum": "gnomAD v4.1 MANE ENST00000620254 + AF-Q96F07-F1 + paralog CYFIP1 WAVE regulatory complex PDB 3P8C (2.29A) + IP landscape",
        "assay_and_contrast": "Human pLoF/missense constraint, GENCODE v46 Exon 19-20 (MANE aa 694-755 / Q96F07-1 aa 719-780) & DEE65 Arg87 structural context, and chemical-SSO patent check",
        "effect_direction": "EXTREME_GENETIC_CONSTRAINT_WITH_PARALOG_AND_DOSAGE_GATES",
        "effect_estimate": "gnomAD v4.1 MANE CYFIP2 pLI=1.000, LOEUF=0.274 (29/144.5 obs/exp), missense Z=6.94 (CYFIP1 LOEUF=0.440); AF-Q96F07-F1 mean pLDDT=86.81 (DEE65 Arg87=94.69, invariant across Q96F07-1/2); paralog WRC PDB 3P8C 2.29A",
        "p_value": "",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "",
        "epistemic_weight": "HIGH_STRUCTURAL",
        "notes": (
            "gnomAD v4.1 MANE Select ENST00000620254 (UniProt Q96F07-2, 1,253 aa; canonical UniProt Q96F07-1 / AF-Q96F07-F1 has 1,278 aa due to an upstream 25-aa exon ENSE00003754054) ranks among the most LoF- and missense-constrained human synaptic genes (pLI=1.000, LOEUF=0.274, o/e=0.201, missense Z=6.94). "
            "Autosomal dominant variants (hotspot Arg87, AF-Q96F07-F1 pLDDT=94.69, invariant across isoforms) destabilize WAVE regulatory complex autoinhibition causing DEE65 (OMIM 618008, Nakashima 2018 PMID:29534297; autism-linked CYFIP2/NCKAP1 WRC structural modeling in Xie 2025 PMID:39660913; paralog CYFIP1 WRC 5-subunit X-ray PDB 3P8C 2.29A Chen 2010 PMID:21107423), while Brown 2022 full Intron 19 (2,692 bp, chr5:157328050-157330741) sits between MANE Exon 19 (aa 694-719) and Exon 20 (aa 719-755; Q96F07-1 aa 719-780). "
            "Supplemental TDP-43 splicing mention in Ma 2022 (PMID:35197626) and cataloged in Sinha 2026 [Review] (PMID:42135847); genus-listed without worked examples in U7 patent WO2023237638A1 and absent from standalone chemical-SSO claims."
        ),
    },
]

LIVING_V15_STAT_SPECS: list[dict[str, str]] = [
    {
        "evidence_id": "EV-LIV-003",
        "analysis_run_id": "RUN-P4-006",
        "inference_class": "PRIMARY_BAYESIAN_SPLICING_RECOMPUTE",
        "statistical_unit": "in_vitro_perturbation_replicate",
        "n_statistical_units": "",
        "n_unique_donors_or_participants": "",
        "exact_contrast": "Brown 2022 human i3Neuron TDP-43 KD vs Control MAJIQ LSV ENSG00000172890.12:t:71485542-71485648 Intron-15 retention (chr11:71484448-71485541); corroborating Spiteri 2025 4-region TMTpro & NYGC motor cortex OLS (n=212) recorded in RUN-P4-006 JSON",
        "model_formula_or_test": "MAJIQ Bayesian deltaPSI & p_d_psi_0_05_per_lsv_junction on Intron-15 retention (secondary cross-cohorts in RUN-P4-006 JSON: Spiteri 4-region limma & NYGC donor OLS)",
        "effect_metric": "MAJIQ_deltaPSI_Intron15_retention",
        "effect_estimate": "Brown Intron-15 IR deltaPSI=+0.4255 (0.033->0.445, source MAJIQ 'FDR' [p_d_psi_0.05]=6.853e-20; canonical -0.5365, source MAJIQ 'FDR'=3.33e-16); corroborating Spiteri 4-region mean -0.5610 (adj p=0.00519) & NYGC motor cortex OLS -0.2548 (adj p=0.000381, n=212)",
        "se_or_ci95": "",
        "unadjusted_or_primary_nominal_p": "",
        "covariate_adjusted_nominal_p": "",
        "multiplicity_adjusted_p": "",
        "multiple_testing_family": "MAJIQ Bayesian p_d_psi_0_05_per_lsv_junction (source MOESM11 'FDR' column; non-frequentist posterior)",
        "missingness_or_exclusion_rule": "Header-resolved MOESM11 unannotated Intron-15 retention row (junc_cat=none, cryptic_junction=True); corroborating NYGC motor cortex excludes pure FTD and averages multi-region libraries per donor",
        "overlap_group_id": "OVL_IN_VITRO_TDP43_KD",
        "anchor_type": "STAGED_DATASET",
        "anchor_relpath": "data/genomics_splicing/tdp43_cryptic_sources/Brown2022_41586_2022_4436_MOESM11_ESM.csv",
    },
    {
        "evidence_id": "EV-LIV-004",
        "analysis_run_id": "RUN-P4-006",
        "inference_class": "DESCRIPTIVE_PK_OR_3D_MEASUREMENT",
        "statistical_unit": "crystal_structure_and_mane_exon_mapping",
        "n_statistical_units": "2",
        "n_unique_donors_or_participants": "",
        "exact_contrast": "Human NADSYN1 2.84A X-ray octamer PDB 6OFB (NaAD/DND, AMP, pyrophosphate/POP) & AF-Q6IA69-F1 mapped to GENCODE v46 MANE Exon 16 (chr11:71485542-71485648, aa 486-521) + gnomAD v4.1 MANE constraint",
        "model_formula_or_test": "[X-ray PDB 6OFB & AF-Q6IA69-F1] heavy-atom <=4.0A ligand contact enumeration + GENCODE v46 CDS-to-residue mapping + gnomAD v4.1 descriptive lookup",
        "effect_metric": "exon16_catalytic_contacts_le_4A_and_LOEUF",
        "effect_estimate": "PDB 6OFB Chain A: 6 catalytic <=4.0A contacts inside Exon 16 aa 486-521 (DND: Arg487 2.11A [2.84A crystal model], Gln498 3.48A, Leu510 3.11A, Leu511 3.56A; AMP: Arg489 3.14A, Ser515 3.83A); AF-Q6IA69-F1 mean pLDDT=95.92; LOEUF=1.010",
        "se_or_ci95": "",
        "unadjusted_or_primary_nominal_p": "",
        "covariate_adjusted_nominal_p": "",
        "multiplicity_adjusted_p": "",
        "multiple_testing_family": "NOT_APPLICABLE_NON_FREQUENTIST",
        "missingness_or_exclusion_rule": "Solvent/buffer ions excluded from heavy-atom ligand contacts; MANE Select ENST00000319023.7 CDS coordinates verified 1-based closed against DS_GENCODE_V46_COMP_GTF",
        "overlap_group_id": "NONE_INDEPENDENT_OR_EXTERNAL",
        "anchor_type": "DETERMINISTIC_MODEL_OUTPUT",
        "anchor_relpath": "work/phase4_final_synthesis/outputs/run_p4_006_living_nadsyn1_cyfip2_eval.json",
    },
    {
        "evidence_id": "EV-LIV-005",
        "analysis_run_id": "RUN-P4-006",
        "inference_class": "PRIMARY_FREQUENTIST_RECOMPUTE",
        "statistical_unit": "unique_human_donor",
        "n_statistical_units": "32",
        "n_unique_donors_or_participants": "32",
        "exact_contrast": "NYGC GSE330224 lumbar spinal cord Visium ventral horn CYFIP2 (24 ALS vs 8 Control, n=32 Welch; n=25 [20 ALS vs 5 Ctrl] complete-covariate OLS without neuronal-proportion adjustment) + corroborating NYGC bulk cord (n=232), Brown Ribo-seq, Kozareva 2025 (preprint), Spiteri, Miedema & CYFIP1 checks",
        "model_formula_or_test": "Two-sided Welch t-test (n=32) & complete-covariate donor-level OLS (n=25: 20 ALS vs 5 Ctrl): CYFIP2_log2CPM ~ ALS_vs_Ctrl + gc_z + sex_male + age + pmi (DESeq2 median-of-ratios donor pseudobulk; no neuronal-proportion term)",
        "effect_metric": "unadjusted_diff_and_covariate_adjusted_OLS_beta_log2CPM",
        "effect_estimate": "Visium ventral horn raw=-0.6792 (n=32; complete-covariate OLS n=25 [20 vs 5] adj beta=-0.8613, adj p=0.00777); NYGC cord OLS -0.1276 (adj p=0.00224, n=232); Brown Ribo-seq -1.3743 (adj p=1.68e-14); Kozareva 2025 (preprint) S1 -0.4678 (adj p=0.0204); Spiteri motor cortex -0.3042 (adj p=0.0476); Miedema -0.3598 (q=3.02e-8)",
        "se_or_ci95": "SE=0.2895 (OLS, n=25)",
        "unadjusted_or_primary_nominal_p": "0.001745",
        "covariate_adjusted_nominal_p": "0.007769",
        "multiplicity_adjusted_p": "",
        "multiple_testing_family": "Targeted CYFIP2 spinal spatial validation across donor-collapsed lumbar Visium ventral horn (nominal Welch n=32 & complete-covariate OLS n=25 p reported)",
        "missingness_or_exclusion_rule": "Spot counts summed per unique donor inside Vent_Horn before DESeq2 normalization; complete-covariate OLS retains n=25 donors (20 ALS vs 5 Ctrl) with recorded age and PMI and does not include a neuronal-proportion covariate",
        "overlap_group_id": "OVL_NYGC_POSTMORTEM",
        "anchor_type": "DETERMINISTIC_MODEL_OUTPUT",
        "anchor_relpath": "work/phase4_final_synthesis/outputs/run_p4_006_living_nadsyn1_cyfip2_eval.json",
    },
    {
        "evidence_id": "EV-LIV-006",
        "analysis_run_id": "RUN-P4-006",
        "inference_class": "DESCRIPTIVE_PK_OR_3D_MEASUREMENT",
        "statistical_unit": "gene_constraint_and_3d_structure_entry",
        "n_statistical_units": "2",
        "n_unique_donors_or_participants": "",
        "exact_contrast": "CYFIP2 gnomAD v4.1 MANE Select ENST00000620254 (1,253 aa Q96F07-2) constraint + AF-Q96F07-F1 (1,278 aa canonical Q96F07-1) vs paralog CYFIP1 WAVE regulatory complex PDB 3P8C (2.29A) & GENCODE v46 Exon 19-20 mapping",
        "model_formula_or_test": "[AlphaFold AF-Q96F07-F1 & X-ray PDB 3P8C] pLDDT/chain parsing + GENCODE v46 CDS-to-residue mapping + gnomAD v4.1 MANE constraint lookup",
        "effect_metric": "pLI_LOEUF_misZ_and_pLDDT",
        "effect_estimate": "CYFIP2 pLI=1.000, LOEUF=0.274 (obs 29 / exp 144.5), missense Z=6.94 (paralog CYFIP1 LOEUF=0.440); AF-Q96F07-F1 mean pLDDT=86.81 (DEE65 Arg87=94.69); PDB 3P8C 5-chain WRC 2.29A",
        "se_or_ci95": "",
        "unadjusted_or_primary_nominal_p": "",
        "covariate_adjusted_nominal_p": "",
        "multiplicity_adjusted_p": "",
        "multiple_testing_family": "NOT_APPLICABLE_NON_FREQUENTIST",
        "missingness_or_exclusion_rule": "Canonical MANE Select ENST00000620254 (1,253 aa Q96F07-2) filtered from SHA-256-locked DS_GNOMAD_V41_CONSTRAINT; AF-Q96F07-F1 models 1,278-aa Q96F07-1 (+25-aa upstream exon shift on Exons 19-20, Arg87 invariant)",
        "overlap_group_id": "NONE_INDEPENDENT_OR_EXTERNAL",
        "anchor_type": "DETERMINISTIC_MODEL_OUTPUT",
        "anchor_relpath": "work/phase4_final_synthesis/outputs/run_p4_006_living_nadsyn1_cyfip2_eval.json",
    },
]

UPD_2026_11_27_01: dict[str, str] = {
    "update_id": "UPD-2026-11-27-01",
    "date_iso": "2026-11-27",
    "release_tag": "v1.5.0",
    "update_category": "MODEL_REVISION",
    "affected_ids": "PORTFOLIO_WIDE;EALS-007;EALS-053;EALS-031;EALS-015",
    "decision_impact": "33-Cohort Benchmark & 0/16 Excluded-Regimen Calibration: All 53 Prior Verdicts Preserved",
    "headline": "Multi-Cohort Validation Benchmark Across 33 External 2025-2026 ALS/FTD Cohorts: 0/16 Target-Mapped False Positives & Cross-Checks on EALS-007, EALS-053, EALS-031 & EALS-015",
    "prior_state_or_assumption": (
        "Prior portfolio triage rested on 43 core replication resources across 8 donor-overlap groups without an independent large-scale benchmark across newly released 2025-2026 ALS multi-region proteomics, brain-capillary snRNA-seq, living PBMC scRNA-seq, longitudinal Olink plasma/CSF proteomics, and 17,919-case exome sequencing."
    ),
    "new_evidence_or_revision": (
        "(1) Calibration & Specificity Benchmark (RUN-P4-006): a five-modality validation screen across 33 external open-access 2025-2026 ALS/FTD cohorts evaluated alongside the 44-resource core replication manifest (summary metrics locked in RUN-P4-006: Spiteri 2025 PMID:41028049, Feneberg 2025 PMID:40826370, Miedema 2025 PMID:40713859, Dellar 2025 PMID:39548852, Pan 2026 PMID:42698373, Ran 2026 PMID:42509371, Omar 2025 PMID:40087396, Ruf 2026 PMID:41803120, Hop 2026 PMID:41917433, Dargan 2025 PMID:40737092, Tian 2021 PMID:34031600, Drager 2022 PMID:35953545, Kozareva 2025 DOI:10.1101/2025.09.29.679403 [preprint], plus GSE244263, GSE287257, GSE310723/GSE315972, GSE330130/GSE330224); recovers positive core controls UNC13A and STMN2 while yielding 0/16 target-mapped false-positive nominations across all 16 clinically or exposure-excluded regimens; "
        "(2) EALS-007 (IL1RL1 / sST2): Pan 2026 Olink elevates symptomatic ALS plasma IL1RL1 (+0.41, p=4.63e-4, adj p=0.00464) but is null in case-control ALS CSF (-0.05, p=0.856) and pre-symptomatic UK Biobank plasma (-0.07, p=0.169); Omar 2025 brain capillaries show stronger elevation in Alzheimer disease (+3.73, p=1.36e-4) than ALS (+2.37, p=0.029) and pure-endothelial ALS OLS collapses under GC/sex/age/PMI adjustment (p=0.570), reinforcing the existing Tier 2 pre-hypoxic CSF Simoa and vascular-specificity validation gate; "
        "(3) EALS-031 (Aldesleukin / IL-2) & EALS-053 (CGAS): Pan 2026 plasma IL2RA (+0.40, p=0.00229, adj p=0.0156) measures shed soluble sCD25 rather than intact Treg competence, whereas living ALS PBMC scRNA-seq (GSE244263, n=30 ALS vs 10 Ctrl) shows nominal Treg FOXP3 downregulation (OLS beta=-0.382, p=0.0267); systemic pan-PBMC CGAS is elevated (beta=+0.552, p=1.18e-4, FDR=0.00258; CD14 monocytes beta=+0.469, p=3.38e-4) contrasted with null spinal snRNA CGAS (GSE330130 microglia p=0.819; GSE287257 p=0.137), preserving MIROCALS (NCT03039673 PMID:40354799) and EALS-053's 2'3'-cGAMP catalytic validation gate; "
        "(4) EALS-015 (SCFD1 / G2E3): Hop 2026 rare-variant exome burden (PMID:41917433) highlights nominal G2E3 PHD zinc-finger domain signal (p=9.38e-4, gene p=0.0127) alongside null SCFD1 rare-variant burden (gene p=0.422), keeping the chr14q12 subunit split active."
    ),
    "portfolio_and_gate_consequence": (
        "Preserves 100% of verdicts, tiers, and validation gates across all 53 prior hypotheses (zero changes to Ranks #1-#16 or any Flagship Monograph) while documenting biofluid, endothelial, PBMC, and rare-variant boundary conditions that sharpen prospective experimental assays on EALS-007, EALS-031, EALS-053, and EALS-015."
    ),
    "primary_sources": (
        "PMID:41028049;PMID:40826370;PMID:40713859;PMID:39548852;PMID:42698373;PMID:42509371;PMID:40087396;"
        "PMID:41803120;PMID:41917433;PMID:40737092;PMID:34031600;PMID:35953545;PMID:40354799;"
        "10.1101/2025.09.29.679403;NCT03039673;NCT07260877"
    ),
    "verification_anchor": "RUN-P4-006;EV-LIV-001;EV-LIV-003;EV-LIV-005;RUN-P4-001;RUN-P4-002",
}

UPD_2026_11_27_02: dict[str, str] = {
    "update_id": "UPD-2026-11-27-02",
    "date_iso": "2026-11-27",
    "release_tag": "v1.5.0",
    "update_category": "LITERATURE_INGESTION",
    "affected_ids": "EALS-054;EALS-055;EALS-030",
    "decision_impact": "Portfolio Expanded 53 -> 55: NADSYN1 (EALS-054, #17) & CYFIP2 (EALS-055, #18) Added in Tier 3",
    "headline": "Living-Evidence Target Addition: Single-Gene NADSYN1 (EALS-054) & CYFIP2 (EALS-055) Added From Multi-Cohort TDP-43 Splicing & Proteomics With Non-Promoted Lead Log",
    "prior_state_or_assumption": (
        "Prior TDP-43 cryptic-splicing triage evaluated 12 splice/APA loci without testing whether pan-CNS human ALS proteomics (Spiteri 2025, Miedema 2025), PacBio Iso-Seq long reads, and lumbar spinal spatial/snRNA cohorts nominate additional non-overlapping TDP-43 loss-of-function targets with open chemical-SSO IP landscapes or clarify polarity-ambiguous metabolic/biomarker screen hits."
    ),
    "new_evidence_or_revision": (
        "(1) EALS-054 (NADSYN1, #17/55, Tier 3 · Keep · Exploratory): depleted across all four human ALS CNS regions in Spiteri 2025 TMTpro (mean per-region -0.561 [4-region sum contrast -2.244], adj p=0.00519; cervical/lumbar/motor cortex/thoracic all adj p<=0.023, PMID:41028049) and NYGC motor cortex OLS (-0.255, adj p=3.81e-4, n=212), converging with Brown 2022 TDP-43 Intron-15 retention (chr11:71484448-71485541, deltaPSI=+0.4255, source MAJIQ 'FDR'=6.85e-20, PMID:35197628); Intron 15 directly precedes Exon 16 (aa 486-521), encoding six <=4.0A NaAD+/AMP catalytic contacts in 2.84A PDB 6OFB (Arg487 [2.11A crystal model]/Arg489/Gln498/Leu510/Leu511/Ser515, PMID:31911602), paired with autosomal recessive VCRL3 human biology (OMIM 618845, PMID:31883644, PMID:38357931), Tian 2021 neuronal survival sensitivity (-2.92, PMID:34031600), and zero claims in WO2023237638A1/WO2023222858A1, gated on NAMPT->NMNAT2 salvage redundancy upstream of EALS-030 (SARM1) and postmortem Intron-15 proof; "
        "(2) EALS-055 (CYFIP2, #18/55, Tier 3 · Keep · Exploratory): extreme human constraint (gnomAD v4.1 pLI=1.000, LOEUF=0.274, missense Z=6.94; autosomal dominant DEE65 OMIM 618008 Nakashima 2018 PMID:29534297; autism-linked actin regulatory complex [WRC] structural modeling Xie 2025 PMID:39660913; paralog WRC PDB 3P8C 2.29A PMID:21107423) paired with Brown Ribo-seq (-1.374, adj p=1.68e-14) and triple-concordant protein depletion (Kozareva 2025 [preprint] S1 -0.468 adj p=0.0204 & S6 postmortem cryptic-exon confirmed; Spiteri motor cortex -0.304 adj p=0.0476; Miedema FTLD-TDP-C -0.360 q=3.02e-8); corroborated by Dargan neurite loss (-0.784 p=1.11e-4, PMID:40737092), NYGC lumbar Visium ventral horn (-0.679 Welch p=0.00174, n=32; n=25 [20 ALS vs 5 Ctrl] complete-covariate OLS adj p=0.00777 without neuronal-proportion adjustment), and bulk cord OLS (-0.128 adj p=0.00224), gated on reciprocal CYFIP1 upregulation (+0.929 Kozareva S1; +0.264 Miedema) and NMD-blocked long-read mapping across full 2,692-bp Intron 19; "
        "(3) Explicitly Not Promoted as Therapeutic Targets: AKR1B1 (elevated in Spiteri mean +0.781 adj p=0.0289, Feneberg spinal insoluble +0.820 FDR=0.0176 PMID:40826370, and Zelic 2025 cervical microglia +0.662 p=0.0268 PMID:40132594) is withheld due to unresolved reactive-vs-causal microglial redox/phagocytic polarity (Drager 2022 CRISPRa phagocytosis +0.55 PMID:35953545, zero ALS genetic or TDP-43 link, withdrawn Charcot-Marie-Tooth SORD neuropathy Ph3 NCT07191912 N=0 & INSPIRE NCT05397665); MEGF10 is logged as a validated pre-symptomatic phenoconversion biomarker (Ran 2026 Pre-fALS +1.24 q=3e-18 PMID:42509371; Pan 2026 UK Biobank +0.29 q=9.6e-4 PMID:42698373) with autosomal recessive EMARDD myopathy LoF contraindication (PMID:22101682); five further multi-cohort hits are documented without promotion: EIF2AK3 (downstream ALS integrated-stress-response eIF2B-activator futility in HEALEY NCT05842941 & NCT05740813; direct PERK inhibitor HC-5404-FU tested only in solid-tumor Phase 1 MTD NCT04834778 with zero ALS efficacy trials), TGFBR2 (anti-TGFBR2 mAb LY3022859 solid-tumor cytokine-release-syndrome halt PMID:28280971; distinct from planned NOT_YET_RECRUITING Phase 2/3 TGFBR1/ALK5 small-molecule galunisertib + nerandomilast trial NCT07321860 in GREM2-positive ALS), UNC13C/TTC3 (reversed Hop 2026 replication PMID:41917433), intracellular PPIA (Ppia-/- induces TDP-43 pathology PMID:34972208 vs extracellular MM218 PMID:28011744), and AKT3 (Guo 2026 Fig. 1 cryptic-exon panel PMID:42234776)."
    ),
    "portfolio_and_gate_consequence": (
        "Expands ExploreALS v1.5.0 from 53 to 55 hypotheses by adding single-gene NADSYN1 (EALS-054, #17/55) and CYFIP2 (EALS-055, #18/55) in dedicated living-evidence registries (Tier 3 · Keep · Exploratory, Preclinical Modality, 4 validation steps each; zero edits to existing historical registries; Ranks #1-#16 including all 8 Flagship Monographs are unchanged while prior Ranks #17-#53 shift by +2 to #19-#55, e.g., EALS-053 CGAS #23 -> #25)."
    ),
    "primary_sources": (
        "PMID:41028049;PMID:35197628;PMID:31911602;PMID:31883644;PMID:38357931;PMID:34031600;PMID:35641224;"
        "PMID:42135847;PMID:29534297;PMID:39660913;PMID:21107423;PMID:40713859;PMID:40737092;PMID:35197626;"
        "PMID:40826370;PMID:40132594;PMID:35953545;PMID:42509371;PMID:42698373;PMID:22101682;PMID:28280971;PMID:41917433;"
        "PMID:34972208;PMID:28011744;PMID:42234776;10.1101/2025.09.29.679403;"
        "NCT05842941;NCT05740813;NCT04834778;NCT05397665;NCT07191912;NCT07321860"
    ),
    "verification_anchor": "EV-LIV-003;EV-LIV-004;EV-LIV-005;EV-LIV-006;RUN-P4-006;RUN-P4-001;RUN-P4-002",
}
