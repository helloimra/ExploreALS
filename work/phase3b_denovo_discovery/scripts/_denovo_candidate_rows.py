"""Atomic 1-gene candidate builder Part A (DN-01..DN-09) programmatically formatted from RUN-P3B-001, RUN-P3B-002, & RUN-P3B-004 outputs."""
from __future__ import annotations

from typing import Any

from _denovo_candidate_rows_b import build_candidates_dn10_to_dn19, make_cand_row


def build_phase3b_candidate_rows(f1234: dict[str, Any], sso: dict[str, Any], dd: dict[str, Any]) -> list[dict[str, str]]:
    ivs = {(r["gene_symbol"], int(r["rank_within_gene"])): r for r in sso["intervals"]}
    ptc_atg = sso["atg4b_ce_reading_frame_audit"]["inframe_ptc_codon_indices_1b"]
    sp = f1234["funnel1_cryptic_splicing"]["spillman_fractions"]
    gc = f1234["funnel3_csf_and_spatial"]["pineda_ba4_gc_adjusted"]["ba4_exc_by_gene"]
    ed_exc = f1234["funnel3_csf_and_spatial"]["edinburgh_sals_non_c9"]["Excitatory"]
    zh = f1234["funnel3_csf_and_spatial"]["zhang2026_mn_selected"]
    ny_c = dd["nygc_multiregion_donor_analysis"]["regions"]["Spinal_Cord_Cervical"]["genes"]
    ny_l = dd["nygc_multiregion_donor_analysis"]["regions"]["Spinal_Cord_Lumbar"]["genes"]
    ag_rs = dd["kalrn_rs2173852_alphagenome_summary"]
    kal_g = dd["kalrn_rs2173852_genetics_summary"]
    atg_3d = dd["atg4b_3d_truncation_2z0d"]
    liab = dd["gene_liability_profiles"]
    elk_ed = dd["elk1_st7_regulon_sign_test"]["contrasts"]["Edinburgh_sALS_nonC9_Exc_Welch_t"]

    part_a = [
        make_cand_row(
            "DN-01", "F1_CRYPTIC_SPLICE", "ATG4B", "GENE_CIS_SPLICE",
            f"Intrathecal steric-blocking 2'-MOE SSO (promoted clean-1mm lead #2 {ivs[('ATG4B',2)]['interval_id']} vs #1 {ivs[('ATG4B',1)]['interval_id']}) skipping cryptic exon chr2:241668875-241668985(+)",
            "Cysteine protease (Cys74/Asp278/His280) cleaving LC3B Gly120; Exon 10 (Val319) -> 111-bp cryptic exon truncates aa 320-393 (PDB 2Z0D aa 320-354 interface + Q9Y4P1 LIR aa 388-391)",
            "CAUSAL_LOSS_OF_FUNCTION", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_3_PRECLINICAL_SSO_COORDINATE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_C9FTD_FRACTION_PROTEOMICS",
            "COARSE_PRIOR_ONLY:Tm_dG37_AVI_2Z0D_contacts", "EMPIRICAL_IPSC_MN_SSO_PROTEIN_AND_LC3YLATION_RESCUE;SPINAL_MN_CE_PENETRANCE_QUANTIFICATION;SPONSOR_OWNED_GLP_IT_TOX_AND_CSF_PD_BIOMARKER",
            "TIER_2_FOCUSED_GATE_FIRST",
            f"[MEASURED] Brown CE FDR=1.16e-11 (2 in-frame TGA PTCs at CE codons {ptc_atg}; discovered in Ling 2015 PMID:26250685 & Torres 2018 PMID:29912613) & Ribo-seq -1.5501 (padj=5.78e-6), Spillman C9-FTD homogenate DIA -0.4905 (nominal p=0.0227, padj=0.148, PMID:42789089 vs flat homogenate RNA p={sp['ATG4B']['homogenate_rnaseq']['p_value']:.4f} & synaptosome DIA p={sp['ATG4B']['synaptosome_protein']['p_value']:.4f}; indirect C9-FTD cortical evidence), NYGC cervical loss (RIN+GC beta={ny_c['ATG4B']['adj_beta_tdp_vs_ctrl']:.4f}, p={ny_c['ATG4B']['adj_p_tdp_vs_ctrl']:.4f}, ALS-Ox p={ny_c['ATG4B']['oneill_motor_subtypes']['ALS-Ox']['adj_p_vs_ctrl']:.2e}, neuronal-mass-residualized mn_neur_z tSTMN2 p={ny_c['ATG4B']['within_tdp_mn_adj_log2_tSTMN2_p']:.2e} [{ny_c['ATG4B']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}% neuronal tail]), Torres 2024 PMID:39305312 (PMC11416411 Table 3) preclinical 16-nt unconjugated 6-LNA/15-PS mixmer ASO 3J (chr2:241668980-241668995(+): sequence-level transcriptome scan sp1=10 [CLN6/DOCK3], pm0_50=1, pm1_50=18, 5 pLI>=0.96 CNS flags [DOCK3/SNRNP200/PSMA5/KHDC4/SNU13], unmeasured additive heuristic 6-LNA Tm ~80.1C / 1-mm ~74.1C) HeLa RNAiMAX TARDBP-KD mRNA rescue (Fig. 6c) + sALS cord membrane ATG4B loss/LC3ylation (while separate systemic IV 25-nt peptide-PMO Pip8b2-ATG4B at 10 mg/kg caused transient Day-2 murine urinary KIM-1 elevation in Fig. 6b, avoided by naked intrathecal 2'-MOE) & Kozareva 2025 validation, Exon-10 Val319 truncation (PDB 2Z0D aa 320-354: {atg_3d['lc3b_patch_heavy_atom_contacts_le_4p5A']} LC3B Val89-Val91 heavy-atom contacts <=4.5A + Q9Y4P1 FEIL LIR aa 388-391), CHEMBL1741221 (995 inhibitors, 0 activators), promoted lead #2 {ivs[('ATG4B',2)]['interval_id']} ({ivs[('ATG4B',2)]['offtarget_safety_status']}: sp1=0, pm1_50=0, pm2_25=2, 0 pLI flags, max_AVI={ivs[('ATG4B',2)]['max_avi_phred']}) shifting -10 bp from ASO 3J/#1 to eliminate spliced/50bp-SS 1-mm & constrained CNS sequence hits, and #1 {ivs[('ATG4B',1)]['interval_id']} ({ivs[('ATG4B',1)]['offtarget_safety_status']}: sp1=2, pm1_50=1, max_AVI={ivs[('ATG4B',1)]['max_avi_phred']}), though in end-stage cord (70-90% alpha-MN loss) 69.7% (cervical) and 70.4% (lumbar) of non-cryptic neuronal genes remain negatively correlated with tSTMN2 after linear mn_neur_z residualization and cervical ALS-SOD1/FUS mRNA is non-significantly different in small n=9 (adj_p={ny_c['ATG4B']['adj_p_tdp_vs_sod1fus']:.4f}; underpowered to prove equivalence), showing bulk postmortem RNA cannot replace ChAT/SMI-32/TDP-43 LCM or FACS motor-neuron junction RT-ddPCR.",
            f"Dose-response 2'-MOE SSO walk across promoted #2 {ivs[('ATG4B',2)]['interval_id']} and #1 {ivs[('ATG4B',1)]['interval_id']} (benchmarked against Torres 2024 ASO 3J chr2:241668980-241668995(+) PMID:39305312) in TDP-43-depleted human iPSC-MNs measuring full-length ATG4B protein & LC3ylation rescue, N-terminal (aa 1-300) immunoblot (+/- proteasome/lysosome inhibition) for partial NMD-escaping ATG4B(1-319+32aa) (~39 kDa), ChAT/SMI-32/TDP-43-guided LCM + duplex BaseScope splice-junction ISH across short-duration sALS vs SOD1/FUS-ALS negative-TDP-control anterior horns (co-measuring single-alpha-MN ATG4B CE, CELF5 CE, KCNQ2 Exon-5 skip, and tSTMN2) + NeuN/TDP-43 FACS CE RT-ddPCR, and CSF PD biomarker scoping before 1-plex GLP IT tox.",
            "EV-P3B-001;EV-P3B-002;EV-P3B-024",
        ),
        make_cand_row(
            "DN-02", "F1_CRYPTIC_SPLICE", "KALRN", "GENE_CIS_SPLICE",
            f"Intrathecal steric-blocking 2'-MOE SSO (#1 {ivs[('KALRN',1)]['interval_id']}) blocking major 3'SS 124701093 acceptor & +1..+17 exonic core (ese_motifs=0) while sparing rs2173852",
            "Dual-RhoGEF Ser/Thr kinase (MANE_Select Kalirin-12 O60229-1 & DuET; Kalirin-7 ends 180.2 kb upstream & is spared); Intron 56 CE truncates C-terminal kinase (aa 2,684-2,938)",
            "CAUSAL_SYNAPTIC_LOSS_OF_FUNCTION", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_3_PRECLINICAL_SSO_COORDINATE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_C9FTD_FRACTION_PROTEOMICS",
            "COARSE_PRIOR_ONLY:Tm_dG37_AVI_composite_score", "ALTERNATIVE_3SS_124700977_SHUNTING_CHECK;ADULT_SPINAL_MN_1P5TPM_VS_CORTICAL_PENETRANCE;RS2173852_ALS_GWAS_NULL_PARADOX_RECONCILIATION",
            "TIER_3_EXPLORATORY_DISCOVERY",
            f"[MEASURED] 7/10 (70%) Spillman C9-FTD frontal cortices vs 0/10 controls (Fisher p=0.00310), Brown dPSI=+0.4946 (FDR=3.90e-19), Ma dPSI=0.831, GENCODE v46 Kalirin-12/DuET kinase truncation (sparing abundant Kalirin-7), and AlphaGenome-predicted rs2173852 (joint AF={kal_g['gnomad_af_total']:.4f}, r4 gate={kal_g['gnomad_r4_af_splice_gate']:.4f}, NFE={kal_g['gnomad_pop_af']['NFE']:.4f}) {ag_rs['donor_124701255_plus']['fold_reduction']:.2f}x 5'SS collapse with #1 {ivs[('KALRN',1)]['interval_id']} ({ivs[('KALRN',1)]['offtarget_safety_status']}, max_AVI={ivs[('KALRN',1)]['max_avi_phred']}, ese=0) & #2 {ivs[('KALRN',2)]['interval_id']} ({ivs[('KALRN',2)]['offtarget_safety_status']}), YET recalibrated to TIER_3_EXPLORATORY_DISCOVERY across 3 motor-ALS hurdles: (1) 0 ALS/FTD GWAS credible sets for rs2173852/KALRN across {kal_g['opentargets_v4_als_studies_indexed']} Open Targets v4 ALS studies (vs 6 for UNC13A rs12608932 at p=4.04e-25), (2) low GTEx v8 cervical cord expression ({liab['KALRN']['gtex_cns_spinal_cervical_tpm']:.2f} TPM vs BA9 {liab['KALRN']['gtex_cns_ba9_tpm']:.2f} & Artery_Aorta {liab['KALRN']['max_non_cns_gtex_tpm']:.2f} TPM) + 17.05% cervical neuronal tSTMN2 percentile (p={ny_c['KALRN']['within_tdp_mn_adj_log2_tSTMN2_p']:.5f}; ALS-SOD1/FUS adj_p={ny_c['KALRN']['adj_p_tdp_vs_sod1fus']:.4f}), and (3) upstream alt 3'SS 124700977 shunting risk (predicted acc={ag_rs['alt_acceptor_124700977_plus']['ref_G_prob']:.4f} vs {ag_rs['major_acceptor_124701093_plus']['ref_G_prob']:.4f}).",
            f"Test #1 {ivs[('KALRN',1)]['interval_id']} vs #2 {ivs[('KALRN',2)]['interval_id']} across rs2173852 G/G and G/C TDP-43-KD human iPSC-MNs to verify zero shunting to alt 3'SS 124700977, full-length Kalirin-12/DuET kinase rescue (using spared Kalirin-7 as internal isoform control), and adult lumbar/cervical MN vs cortical CE penetrance.",
            "EV-P3B-003;EV-P3B-004;EV-P3B-023",
        ),
        make_cand_row(
            "DN-03", "F1_CRYPTIC_SPLICE", "PTPRT", "GENE_CIS_SPLICE",
            "Coordinate-gated intrathecal steric SSO pending internal cryptic-exon junction fine-mapping inside chr20:42098552-42102124(-)",
            "Brain-restricted receptor tyrosine phosphatase regulating synaptic Neuroligin/paxillin adhesion and dephosphorylating STAT3 Tyr705",
            "CAUSAL_NEURONONAL_SYNAPTIC_LOSS_WITH_PSTAT3_DUALITY".replace("NEURONONAL", "NEURONAL"), "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_C9FTD_FRACTION_PROTEOMICS",
            "NONE", "EXACT_CRYPTIC_EXON_BOUNDARY_MAPPING;OFFTARGET_CLEAN_SSO_DESIGN;TROPHIC_MN_PSTAT3_VS_SYNAPTIC_ADHESION_DISSECTION",
            "TIER_3_EXPLORATORY_DISCOVERY",
            f"[MEASURED] #1 FDR-significant Ribo-seq loss among Ma 2022 cryptic genes (-2.7829, padj=1.06e-7; Ma intronic cluster FDR=3.54e-6), Spillman homogenate DIA -0.3662 (p=0.00624), and Trautwig CSF loss (Emory p=0.0413, WashU p=0.0272; Pineda full-GC beta={gc['PTPRT']['gc_adj_beta_sals']:.4f}, q_BH={gc['PTPRT']['gc_adj_q_bh']:.4f}; NYGC cervical adj_p={ny_c['PTPRT']['adj_p_tdp_vs_ctrl']:.4f}); GENCODE v46 (0 internal exons) & AlphaGenome (max acceptor 42099289 prob=0.1982) confirm 0 published 1-bp junctions inside 3.57-kb intron.",
            "Fine-map internal cryptic 3'SS/5'SS junctions inside chr20:42098552-42102124(-) by targeted RT-PCR/long-read sequencing in TDP-43-KD iPSC-MNs, run Phase 3A v2 off-target gate, and verify synaptic Neuroligin rescue without blunting neurotrophic nuclear MN pSTAT3 survival signaling.",
            "EV-P3B-005;EV-P3B-026",
        ),
        make_cand_row(
            "DN-04", "F1_CRYPTIC_SPLICE", "CELF5", "GENE_CIS_SPLICE",
            f"Intrathecal steric-blocking 2'-MOE SSO (#1 {ivs[('CELF5',1)]['interval_id']}) blocking cryptic exon chr19:3278209-3278316(+)",
            "Neuron-specific RNA-binding splicing regulator; 108-bp TDP-43 cryptic exon chr19:3278209-3278316(+) (98-bp upstream intron, in-frame PTC at CE codon [30]) triggers NMD & splicing loss",
            "CAUSAL_RNA_PROCESSING_LOSS", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_3_PRECLINICAL_SSO_COORDINATE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
            "COARSE_PRIOR_ONLY:Tm_dG37_AVI_composite_score", "EMPIRICAL_SSO_SPLICE_RESCUE_POTENCY;POSTMORTEM_SPINAL_PROTEIN_AND_CE_PENETRANCE_CONFIRMATION;PLI1_CANONICAL_EXON_SPARING_BELOW_LOQ_AND_GLP_IT_TOX",
            "TIER_2_FOCUSED_GATE_FIRST",
            f"[MEASURED] Replicated across Brown TDP-43 KD (108-bp CE mod3=0 after Exon-5 Pro201 inside RRM2 [aa 134-214, AF-Q8N6W0-F1 + CELF1 RRM1-RRM2 homolog projection PDB 3NMR PMID:20947024: excising beta4 202-214 severs 5 beta4-beta1 H-bonds & 6/17 projected UGUU contacts with 0 RRM1-RRM2 contacts], local donor-LSV dPSI=+0.3471 [KD PSI=0.367 vs canonical 0.546 donor-LSV / 0.633 acceptor-LSV], FDR=2.83e-22, RNA-seq log2FC=-0.8867 [54.1% residual mRNA], Ribo-seq log2FC=-1.3749 [38.6% residual translation, padj=5.65e-7], plus 2.8%->18.2% 98-bp micro-intron retention & upstream novel_acceptor 3225618-3244124 dPSI=+0.1218 [KD PSI=0.149; distinct MAJIQ LSV denominators preclude unphased algebraic isoform summing]), Zeng et al. 2025 PMID:40672339 [PREPRINT] PMC12265704 direct NMD-inhibition rescue (cryptic CELF5 junction rises from 24.8% to 44.6%, FDR=0.0235; on MANE NM_021938.4 the CE codon-30 PTC sits 18 nt [<50-55 nt EJC rule PMID:9671053] before CE-Exon6 and 165 nt before Exon6-7, so 3-exon Exon5-CE-Exon6 minigenes can score primary splice %PSI but evade EJC-NMD), Bye 2025 PMID:41286450 Table 6 sALS patient iPSC-MN LeafCutter cluster clu_25763_+ (padj=0.00904, N=77: 65 sALS vs 12 Ctrl without bulk nuclear TDP-43 depletion P=0.990; cluster-level statistics do not isolate 3278209-3278316 without junction RT-PCR; raw BAMs on controlled-access EGA), and nominal full-GC BA4_Exc ({gc['CELF5']['gc_adj_beta_sals']:.4f}, p={gc['CELF5']['gc_adj_p']:.4f}, nominal q_BH={gc['CELF5']['gc_adj_q_bh']:.4f}); SSO #1 {ivs[('CELF5',1)]['interval_id']} ({ivs[('CELF5',1)]['offtarget_safety_status']}, max_AVI={ivs[('CELF5',1)]['max_avi_phred']}; 98-bp upstream micro-intron to exon chr19:3278031-3278110(+)), though in end-stage cord (70-90% alpha-MN loss) 69.7% (cervical) and 70.4% (lumbar) of non-cryptic neuronal genes remain negatively correlated with tSTMN2 after linear mn_neur_z residualization and untargeted Spillman cortical DIA missed CELF5 peptides, mandating ChAT/SMI-32/TDP-43 LCM + FACS spinal motor-neuron junction RT-ddPCR and Exon-5-sparing verification.",
            f"Evaluate #1 {ivs[('CELF5',1)]['interval_id']} and #2 {ivs[('CELF5',2)]['interval_id']} (plus a 10-oligo micro-walk across distal CE 5'SS) in TDP-43-KD and Bye 2025 sALS patient iPSC-MN lines on endogenous multi-exon transcripts (3-exon Exon5-CE-Exon6 reporters may be used only for primary splice-site %PSI choice, never NMD/stability readouts due to the 18-nt PTC-Exon6 EJC gap PMID:9671053) via single-molecule Exon 1-7+ Nanopore/Iso-Seq phasing (>=1,000-5,000 reads) for CELF5 cryptic-exon suppression, canonical Exon-5 skipping <1-2% LOQ, <=WT 98-bp micro-intron retention (~2.8%), upstream novel_acceptor 3225618-3244124 phasing, protein restoration, and ChAT/SMI-32/TDP-43-guided LCM + duplex BaseScope splice-junction ISH across short-duration sALS vs SOD1/FUS-ALS negative-TDP-control anterior horns + NeuN/TDP-43 FACS CE RT-ddPCR before 1-plex GLP IT tox.",
            "EV-P3B-006",
        ),
        make_cand_row(
            "DN-05", "F1_CRYPTIC_SPLICE", "PRUNE2", "GENE_CIS_SPLICE",
            "Coordinate-gated intrathecal steric SSO pending RT-PCR sign/junction resolution of 9-bp/34-bp exons 76641947-76641980(-) vs cryptic 5'SS 76641905/76641790(-)",
            "Large neuronal BNIP2-homology protein suppressing RhoA-ROCK overactivation and axonal retraction in motor neurons",
            "CAUSAL_AXONAL_MAINTENANCE_LOSS", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
            "NONE", "EXACT_CRYPTIC_EXON_BOUNDARY_MAPPING;OFFTARGET_CLEAN_SSO_DESIGN;MN_AXON_OUTGROWTH_RESCUE",
            "TIER_3_EXPLORATORY_DISCOVERY",
            f"[MEASURED] Sole Ma 2022 cryptic-spliced gene (chr9:76638288-76644739(-), abs(dPSI)=0.621, FDR=2.88e-5) passing spot-level BH<0.05 loss in Zhang 2026 surviving cervical MN-niche 55-um multicellular Visium spots (-1.2260, spot-level within-donor pseudoreplicated BH=0.01885 across N=18 donors, exploratory), replicated in NYGC cervical ({ny_c['PRUNE2']['adj_beta_tdp_vs_ctrl']:.4f}, p={ny_c['PRUNE2']['adj_p_tdp_vs_ctrl']:.5f}) & lumbar cord ({ny_l['PRUNE2']['adj_beta_tdp_vs_ctrl']:.4f}, p={ny_l['PRUNE2']['adj_p_tdp_vs_ctrl']:.6f}) + Spillman C9-FTD synaptosome DIA (-0.4943, p=0.00681), though ALS-SOD1/FUS bulk mRNA is non-significantly different in small n=9 (cervical adj_p={ny_c['PRUNE2']['adj_p_tdp_vs_sod1fus']:.4f}; underpowered to prove equivalence), mn_neur_z tSTMN2 coupling attenuates (cervical {ny_c['PRUNE2']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}%, lumbar p={ny_l['PRUNE2']['within_tdp_mn_adj_log2_tSTMN2_p']:.4f}), and GENCODE v46 + AlphaGenome show annotated 9-bp (76641972-76641980(-)) & overlapping 34-bp (76641947-76641980(-)) exons vs unannotated cryptic 5'SS donors 76641905/76641790(-).",
            "Run single RT-PCR/amplicon-seq across Exon_up-chr9:76641980-76641790-Exon_dn in TDP-43-KD iPSC-MNs & ALS cervical cord to distinguish 9-bp/34-bp exon skipping from 76641905/76641790(-) cryptic 5'SS frameshift extension before Phase 3A v2 SSO selection.",
            "EV-P3B-007;EV-P3B-025",
        ),
        make_cand_row(
            "DN-06", "F1_CRYPTIC_SPLICE", "PFKP", "GENE_CIS_SPLICE",
            f"Intrathecal steric-blocking 2'-MOE SSO (#1 {ivs[('PFKP',1)]['interval_id']}) skipping cryptic exon chr10:3099557-3099819(+)",
            "Phosphofructokinase-platelet gating glycolysis vs pentose phosphate pathway (PPP) NADPH/GSH flux; cryptic exon depletes synaptosomal PFKP",
            "AMBIGUOUS_SYNAPTIC_ATP_LOSS_VS_PPP_REDOX_SHUNT", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_3_PRECLINICAL_SSO_COORDINATE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_C9FTD_FRACTION_PROTEOMICS",
            "COARSE_PRIOR_ONLY:Tm_dG37_AVI_composite_score", "NEURONAL_PPP_NADPH_GSH_REDOX_SAFETY_CHECK;SPINAL_MN_CE_PENETRANCE_QUANTIFICATION;PFKM_PFKL_ISOZYME_REDUNDANCY_CHECK",
            "TIER_3_EXPLORATORY_DISCOVERY",
            f"[MEASURED] Brown CE FDR=2.20e-17 & Ribo-seq -1.8646 (padj=3.12e-5), Spillman synaptosome DIA -0.5075 (p=0.00348), and #1 {ivs[('PFKP',1)]['interval_id']} ({ivs[('PFKP',1)]['offtarget_safety_status']}, max_AVI={ivs[('PFKP',1)]['max_avi_phred']}), YET Zhang surviving cervical MNs are flat ({zh['PFKP']['avg_log2FC']:.4f}, BH={zh['PFKP']['BH']:.4f}) and neuronal glycolysis over-activation risks draining PPP NADPH/GSH antioxidant defense (Bolanos mechanism).",
            f"Test #1 {ivs[('PFKP',1)]['interval_id']} in TDP-43-KD human iPSC-MNs under oxidative challenge quantifying BOTH synaptosomal ATP rescue AND PPP NADPH/GSH ratio + ROS survival, alongside spinal MN CE RT-ddPCR.",
            "EV-P3B-008",
        ),
        make_cand_row(
            "DN-07", "F2_CRYPTIC_APA", "TRAPPC12", "GENE_CIS_APA",
            f"Intrathecal 20-bp steric SSO (#1 {ivs[('TRAPPC12',1)]['interval_id']}) blocking cryptic ALE 3'SS chr2:3457795(+) + secondary CE chr2:3458462-3458515(+) check",
            "TRAPPIII ER-to-Golgi & autophagosome trafficking subunit (upstream of C015 YKT6/SEC22B); intronic ALE chr2:3457795-3458181(+) truncates C-terminus",
            "CAUSAL_TRAFFAKING_LOSS_OF_FUNCTION".replace("TRAFFAKING", "TRAFFICKING"), "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
            "COARSE_PRIOR_ONLY:Tm_dG37_AVI_composite_score", "SECONDARY_CE_3458462_SHUNTING_CHECK;HIGH_NON_TDP_BASELINE_34PCT;CORTICAL_PROTEIN_LOSS_CONFIRMATION",
            "TIER_3_EXPLORATORY_DISCOVERY",
            f"[MEASURED] #1 Bryce-Smith Ribo-seq loss (-1.4873, padj=3.30e-17), NYGC 82.9% TDP+ vs 34.0% non-TDP, and Bye sALS iPSC-MN LeafCutter cluster splicing (padj=0.0153; junction RT-PCR required) — distinct from Zeng's 27-kb-downstream canonical 3'UTR lengthening (chr2:3479564-3485092(+)); 20-bp polypyrimidine-shifted #1 {ivs[('TRAPPC12',1)]['interval_id']} achieves {ivs[('TRAPPC12',1)]['offtarget_safety_status']} (0 constrained hits, modeled Tm={ivs[('TRAPPC12',1)]['tm_phys_pops_c']}C, sub18={ivs[('TRAPPC12',1)]['sub18_core_steric_pc_genes']}, solving #2 {ivs[('TRAPPC12',2)]['interval_id']} SRPK2/TENM2 {ivs[('TRAPPC12',2)]['offtarget_safety_status']}), though Spillman C9-FTD DIA is null (homogenate p={sp['TRAPPC12']['homogenate_protein']['p_value']:.4f}, synaptosome p={sp['TRAPPC12']['synaptosome_protein']['p_value']:.4f}) & secondary CE chr2:3458462-3458515(+) co-occurs.",
            f"Test #1 {ivs[('TRAPPC12',1)]['interval_id']} (including LNA-wing/PMO affinity check given modeled Tm={ivs[('TRAPPC12',1)]['tm_phys_pops_c']}C) in Bye sALS iPSC-MNs to measure full-length TRAPPC12 protein rescue and check whether blocking ALE 3457795 shunts splicing into secondary CE chr2:3458462-3458515(+).",
            "EV-P3B-009",
        ),
        make_cand_row(
            "DN-08", "F2_CRYPTIC_APA", "ELK1", "GENE_CIS_APA",
            f"Watchlist isoform-selective RNase-H gapmer (#1 {ivs[('ELK1',1)]['interval_id']}) or PAS-blocking SSO across post-PAS-trimmed search window chrX:47631625-47635519(-) inside 3'Ext 47631618-47635519(-)",
            "ETS transcription factor; TDP-43 loss derepresses 3.90-kb 3'Ext (47631618-47635519(-), extending 5.31-kb terminal exon 47631618-47636927(-))",
            "AMBIGUOUS_PROAPOPTOTIC_DENDRITIC_VS_TROPHIC_NUCLEAR_GAIN", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_2_PRECLINICAL_MODALITY_DISCOVERY", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
            "COARSE_PRIOR_ONLY:Tm_dG37_AVI_composite_score", "PROAPOPTOTIC_DENDRITIC_VS_NEUROPROTECTIVE_SRF_SIGN_TEST;INTRONIC_GAPMER_QPCR_COUNTERSCREEN;PINEDA_VS_EDINBURGH_COHORT_REPLICATION",
            "TIER_3_EXPLORATORY_DISCOVERY",
            f"[MEASURED] TDP-43-selective 3.90-kb 3'Ext increases i3Neuron Ribo-seq (+1.1248, padj=2.27e-5), Edinburgh non-C9 sALS Exc RNA (+{ed_exc['ELK1']['diff_log2cpm']:.4f}, p={ed_exc['ELK1']['p_welch']:.5f}, n={ed_exc['ELK1']['n_case']+ed_exc['ELK1']['n_ctrl']}), and NYGC lumbar mRNA (+{ny_l['ELK1']['adj_beta_tdp_vs_ctrl']:.4f}, p={ny_l['ELK1']['adj_p_tdp_vs_ctrl']:.5f}), YET Pineda BA4_Exc is null (GC-adj p={gc['ELK1']['gc_adj_p']:.4f}), competitive ST7 ELK1_unique vs paralog ELK4_unique regulons show 0 divergence across all 6 contrasts (Edinburgh p={elk_ed['welch_p_elk1_vs_elk4']:.4f}, Pineda p=0.3440, Zhang MN p=0.0805; subject to ENCODE ChIP & ERK1/2 Ser383 pELK1 gating caveats), van Dijk 2026 shows sparse 3'APA non-reproducibility, and RNase-H intronic scanning caught ERBB4/KCND3/DAB1 on #2 {ivs[('ELK1',2)]['interval_id']} ({ivs[('ELK1',2)]['offtarget_safety_status']}) while #1 {ivs[('ELK1',1)]['interval_id']} passes {ivs[('ELK1',1)]['offtarget_safety_status']}.",
            f"Compare 3'Ext-selective knockdown with #1 {ivs[('ELK1',1)]['interval_id']} vs steric PAS blockade in TDP-43-KD human iPSC-MNs (with intronic pre-mRNA qPCR counter-screen and pELK1-Ser383 readout) to adjudicate dendritic pro-apoptotic vs nuclear SRF-trophic sign.",
            "EV-P3B-010;EV-P3B-027",
        ),
        make_cand_row(
            "DN-09", "F2_CRYPTIC_APA", "DLGAP1", "GENE_CIS_APA",
            f"Intrathecal steric SSO (#1 {ivs[('DLGAP1',1)]['interval_id']}) blocking cryptic ALE 3'SS chr18:4147667(-) pending spinal MN validation",
            "PSD-95-interacting postsynaptic scaffold (GKAP); TDP-43-selective cryptic ALE depletes cortical synaptosomal scaffold",
            "CAUSAL_SYNAPTIC_LOSS_CORTICAL_SELECTIVE", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_3_PRECLINICAL_SSO_COORDINATE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_C9FTD_FRACTION_PROTEOMICS",
            "COARSE_PRIOR_ONLY:Tm_dG37_AVI_composite_score", "SPINAL_MN_VS_CORTICAL_PENETRANCE;EMPIRICAL_ALE_3SS_RESCUE_POTENCY;DISTAL_INTRONIC_REPEAT_PROXIMITY",
            "TIER_3_EXPLORATORY_DISCOVERY",
            f"[MEASURED] #1 NYGC pathology-selective ALE (17 TDP+ vs 0 non-TDP, 19.36x) with Spillman homogenate (-0.8637, p=0.0121) & synaptosome (-0.7364, p=0.0212) protein loss; scoring directly at single true cryptic 3'SS chr18:4147667(-) (fixing prior 62-bp internal repeat offset) rescues #1 {ivs[('DLGAP1',1)]['interval_id']} ({ivs[('DLGAP1',1)]['offtarget_safety_status']}: sp0=0, pm0=0, pm1_sense=4, pm2_25=3, flags=NONE), though evidence remains frontal-cortex-weighted.",
            f"Test #1 {ivs[('DLGAP1',1)]['interval_id']} and #2 {ivs[('DLGAP1',2)]['interval_id']} in TDP-43-KD human i3Neurons/iPSC-MNs for synaptosomal DLGAP1 rescue and quantify lumbar spinal cord ALE penetrance.",
            "EV-P3B-011",
        ),
    ]
    return part_a + build_candidates_dn10_to_dn19(f1234)
