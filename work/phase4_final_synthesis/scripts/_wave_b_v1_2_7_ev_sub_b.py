"""Part B of modular v1.2.7 Wave B patches for evidence_ledger.csv (C023, C016, C020, C019, S02, C005) & subnode_dissection.csv."""
from __future__ import annotations


def apply_wave_b_ev_and_sub_part_b(
    ev_map: dict[str, dict[str, str]],
    sn_rows: list[dict[str, str]],
) -> None:
    # C023 (YKT6)
    ev_map["EV-B2-006"].update({
        "source_id_or_locator": "AlphaGenome_Atlas:chr7:44206388:A>G+DS_GNOMAD_V41_CONSTRAINT+OpenTargets_DepMap:ENSG00000106636+PMID:41917433+PMID:38522068",
        "cohort_and_stratum": "GRCh38 YKT6 p.Tyr64Cys (chr7:44206388:A>G, rs138273846, ENST00000223369.9:c.191A>G), gnomAD v4.1 & 1,258 DepMap lines",
        "effect_estimate": "AVI_Phred=24.53 (top 0.352%, AlphaMissense fi=0.472); ALS discovery AF=48/26,276 (0.183%, ~0.37% carriers); gnomAD v4.1 Joint AC=982/1,613,908 (AF=0.061%, 0 hom; NFE=0.071%, ASJ=0.092%); DepMap Chronos=-1.5425",
        "notes": "Corrects codon-63 44206385 offset to true codon-64 chr7:44206388:A>G (rs138273846; Hop et al. 2026 PMID:41917433 discovery case AF=48/26,276 [0.183%, ~0.37% carriers], OR=2.84, P=9.08e-8, meta P=1.50e-9): present in gnomAD v4.1 at AF=0.061% (NFE ~1:704 carriers, 0 homozygotes — moderate-effect rare risk allele, not high-penetrance dominant fALS); gnomAD v4.1 MANE ENST00000223369.9 LOEUF=0.636; biallelic human YKT6 missense LoF causes developmental disorder with hepatopathy (Ma et al. 2024 PMID:38522068).",
    })
    ev_map["EV-B2-008"].update({
        "source_id_or_locator": "DS_PDB:pdb_00003kyq.cif+pdb_00006j74.cif+DS_AFDB:AF-O15498-F1+PMID:20159557+PMID:32128853",
        "cohort_and_stratum": "Rattus norvegicus closed DPC-bound Ykt6 X-ray (PDB 3KYQ 2.44A) & human open GGTase-III:YKT6 (PDB 6J74 3.21A)",
        "notes": "PDB 3KYQ (Wen et al. 2010 PMID:20159557) resolves Rattus norvegicus Ykt6 closed fold bound to synthetic C12 dodecylphosphocholine detergent DPC (DPV201; [Ortholog/Detergent-Analog Inferred], Longin groove 14/15 identical to human AF-O15498-F1, RMSD=0.43A), whereas human YKT6 open prenylation state is resolved in GGTase-III complex PDB 6J74 (PMID:32128853).",
    })
    ev_map["EV-P2-T2-004"].update({
        "source_id_or_locator": "DS_PDB:3KYQ;DS_PDB:6J74;DS_AFDB:AF-O15498-F1;PMID:20159557;PMID:41917433;PMID:32128853",
        "cohort_and_stratum": "Rattus norvegicus closed DPC-bound Ykt6 (PDB 3KYQ 2.44A) aligned to human AF-O15498-F1 (Tyr64 pLDDT=94.81)",
        "assay_and_contrast": "ALS p.Tyr64Cys pocket-cavity expansion (-85.1 A3 side-chain loss) & vicinal Cys64-Cys66 disulfide geometry",
        "effect_estimate": "Longin RMSD=0.43A (14/15 groove identity); Y64C +85.1 A3 pocket expansion (-85.1 A3 side-chain delta) + modeled Cys64_SG-Cys66_SG=3.46A",
        "notes": "Ortholog/detergent-bound structural model (rat PDB 3KYQ + DPC PMID:20159557 vs human open PDB 6J74 PMID:32128853): explains rare ALS risk variant p.Tyr64Cys (rs138273846, ALS discovery AF=0.183% [48/26,276], gnomAD v4.1 AF=0.061%, Hop 2026 PMID:41917433 Meta P=1.50e-9) and separates rare-carrier Y64C ternary [YKT6-farnesyl+fragment] co-occupancy from non-carrier wild-type YKT6 ALS (family-history-specific sALS carrier denominator unreported) exosite/PTAR1 rescue without displacing Cys195-farnesyl.",
    })

    # C016 (FBXL5 / IRP2)
    ev_map["EV-B2-018"]["notes"] = (
        "Replicated in NYGC Frontal (n=257: 201 ALS/56 Ctrl, adj_beta=+0.1342, adj_p=3.22e-5) and Spinal Cord (n=262: 206 ALS/56 Ctrl, adj_beta=+0.1990, adj_p=8.03e-4), BUT donor-collapsed single-nucleus pseudobulks show FBXL5 mRNA is flat in sALS excitatory neurons (Pineda BA9_Exc +0.0206, p=0.6275; BA4_Exc +0.0597, p=0.2081; Edinburgh Exc +0.1266, p=0.1751, n=34) while elevated in glia (Edinburgh donor-collapsed Microglia +0.4591, p=0.00334, n=33; Pineda BA4_Astro +0.2463, p=0.0316, n=31; 216 ROSMAP Oligo cis-eQTLs), indicating compensatory glial iron-buffering."
    )
    ev_map["EV-B2-019"].update({
        "source_id_or_locator": "DS_PDB:pdb_00003v5z.cif+pdb_00006vcd.cif+DS_AFDB:AF-Q9UKA1-F1+PMID:32126207",
        "notes": "PDB 3V5Z resolves the N-terminal hemerythrin [Fe-O-Fe] di-iron degron domain (aa 1-161), while cryo-EM PDB 6VCD (Wang et al. 2020 PMID:32126207) resolves aa 199-691 LRR-bound [2Fe-2S] cluster (FES800 coordinated by Q9UKA1-1 Cys662/676/686/687 at 2.84-2.99A) recruiting IRP2 (omitting aa 1-161), showing why non-selective iron chelators destabilize holo-FBXL5.",
    })
    ev_map["EV-B2-020"].update({
        "source_id_or_locator": "DS005_BYE:Table12_Deferiprone;NCT03293069;NCT02655315;PMID:36449420",
        "effect_estimate": "Bye2025 paired (Deferiprone - DMSO) mean=+0.2430d (Rank #47/107, paired t=0.914, Wilcoxon p=0.6322; raw mean +0.115d; vs Riluzole -3.716d)",
        "p_value": "0.3751",
        "fdr_or_adjusted_p": "0.5575",
        "notes": "Matched to within-donor paired (Deferiprone - DMSO) contrast (p=0.3751, q_BH=0.5575, n=16): free brain Deferiprone (~13 uM) failed sALS iPSC-MN rescue, ALS Phase 2/3 FAIR-ALS II (NCT03293069, N=372, 30 mg/kg/d, 12-mo CAFS) completed with results unreported (hasResults=false), and unmedicated PD Phase 2 FAIRPARK-II (NCT02655315, Devos et al. 2022 NEJM PMID:36449420) worsened motor scores (+agranulocytosis boxed warning).",
    })
    ev_map["EV-B2-021"].update({
        "source_id_or_locator": "DS_GNOMAD_V41_CONSTRAINT+OpenTargets_DepMap+MGI:5295290+MGI:5796139+OMIM:618451",
        "effect_estimate": "FBXL5 gnomAD v4.1 MANE LOEUF=0.442, pLI=0.9994 (OT v2.1.1 oe_lof=0.3321; KO E8.5 lethal; DepMap Chronos=+0.0127); IREB2 LOEUF=0.389, pLI=1.000 (OT v2.1.1 oe_lof=0.3282; OMIM 618451; DepMap Chronos=-0.2148)",
        "notes": "gnomAD v4.1 MANE ENST00000341285 FBXL5 LOEUF=0.442, pLI=0.9994 (19/63.1 LoF) & ENST00000258886 IREB2 LOEUF=0.389, pLI=1.000 (16/62.4 LoF): both FBXL5 loss (fatal iron overload) and neuronal IREB2 loss (OMIM 618451 neurodegeneration) are deleterious, refuting unidirectional neuronal IRP2 degradation and requiring cell-type-resolved bidirectional FBXL5-IRP2 sensor probing.",
    })
    ev_map["EV-P2-T4-004"].update({
        "source_id_or_locator": "DS_EDIN_PB:Microglia;DS_PDB:6VCD_3V5Z;DS031_ZHANG:6d_MN;PMID:32126207",
        "effect_estimate": "Microglia FBXL5 diff=+0.4591 (TFRC +0.8641 p=0.00281, IREB2 +0.2145 p=0.0475, n=33) vs Exc FBXL5 +0.1266 (p=0.175, n=34) & TFRC -0.3144 (p_welch=0.0508, p_mwu=0.0275); 6VCD Cys662/676/686/687<=2.99A",
        "notes": "Zhang 6d_MN shows FTL +1.2719 (BH=1.04e-10) with flat FBXL5 (BH=0.862); PDB 6VCD (PMID:32126207, aa 199-691) + depleted ALS neuronal TFRC/IREB2 (Spillman Homog IREB2 -0.6213 p=0.0259) warn unidirectional neuronal IRP2 degradation risks OMIM 618451 iron starvation, motivating bidirectional sensor probes.",
    })

    # C020 (Apilimod), C019 (Baricitinib), S02 (CuATSM), C005 (Protocol)
    ev_map["EV-B4-012"].update({
        "source_id_or_locator": "DS005_BYE:Table_12:Apilimod;CHEMBL4297643;PMID:36754049",
        "notes": "Exact Wilcoxon p=0.00336; LODO max p=0.00483; Apilimod free base CHEMBL4297643 (MW 418.49 Da; AIT-101 dimesylate MW 610.70 Da, fu,p<0.01; preclinical PIKfyve ALS validation Hung et al. 2023 Cell PMID:36754049) shows 25% negative-line rate at 2.5 uM (642x above human CSF).",
    })
    ev_map["EV-B4-013"].update({
        "cohort_and_stratum": "Trautwig 2025 Set 2 4-center CSF DIA (50 sALS vs 72 Control, n=122 within N=259) & Set 1 TMT (N=101)",
        "effect_estimate": "GDI2 sALS vs Ctrl non-significant (DIA diff_log2=+0.0200, p=0.5042, n=122; TMT +0.0245, p=0.2085); C9 vs Ctrl TMT +0.0846 (p=0.00598), DIA +0.1813 (p=0.0268)",
        "p_value": "0.5042",
        "sample_size_n": "122",
        "notes": "GDI2 is quantified and statistically non-significant in sALS vs Control across both DIA (n=122 within N=259, p=0.5042) and TMT (p=0.2085), whereas CSF GPNMB rises in sALS (DIA p=6.24e-6) and C9 (p=3.05e-7).",
    })
    ev_map["EV-B4-014"].update({
        "source_id_or_locator": "NCT05163886;PMID:38606777;CHEMBL4297643",
        "effect_estimate": "Wk12 1h plasma 283.13 ng/mL (676.5 nM free-base eq, n=9/10; Wk24 OG000 315.40 ng/mL, n=5), CSF 3.89 nM (n=10, Kp,uu~0.72); Wk12 CSF poly(GP) -73% paper (-74.4% CT.gov), plasma sGPNMB >2.5x paper (2.31x vs pbo, p<0.001; CSF sGPNMB 2-sided t-test p=0.352 NS), CSF NfL -5.0%; Wk12 Plasma NfL median +39% (n=9) & Wk24 OLE CSF NfL mean +50% (n=4)",
        "notes": "AIT-101 dimesylate 125 mg BID (MW 610.70 Da; free base CHEMBL4297643 MW 418.49 Da; Babu et al. 2024 Brain PMID:38606777): published Wk12 randomized CSF poly(GP) fell 73% (-74.4% posted CT.gov) with >2.5x plasma sGPNMB rise (2.31-fold between-group, 2-sided t-test p<0.001), no notable Wk12 CSF sGPNMB group difference (posted CT.gov 2-sided t-test p=0.352), and -5.0% CSF NfL, whereas Wk12 plasma NfL (median +39% [+39.2% CT.gov], n=9) and Wk24 continuous OLE CSF NfL (mean +50% [+49.7%], n=4) rose.",
    })
    ev_map["EV-B4-015"].update({
        "source_id_or_locator": "NCT06286475;NCT06215755;PMID:41708347;PMC12916242;DS_GNOMAD_V41_CONSTRAINT",
        "cohort_and_stratum": "VRG50635 HV Ph1 studies (NL81735.056.22 PMID:41708347 & NCT06286475 N=22) + ALS Ph1b (NCT06215755, 400-800 mg QD, N=54)",
        "effect_estimate": "VRG50635 NL81735.056.22 MAD 2/6 (33%) drug-related encephalopathy/renal SAEs (NCT06286475 N=22 completed) & ALS 400-800 mg QD N=54 terminated for lack of risk-benefit data supporting Ph2 (NfL+GFAP surge, 8/54 [14.8%] drug SAEs); PIKFYVE gnomAD v4.1 MANE LOEUF=0.523",
        "notes": "Chronic daily PIKfyve blockade across separate clinical programs (continuous QD VRG50635 in NCT06215755 [terminated for lack of risk-benefit data supporting Phase 2] / PMID:41708347 vs continuous BID AIT-101 in NCT05163886 / PMID:38606777) hits an endolysosomal toxicity wall; requires a strict pulsed nanomolar (2-15 nM) zero-vacuolation/zero-NfL falsification gate.",
    })
    ev_map["EV-P2-T3-005"]["notes"] = (
        "Continuous QD/BID fails both models (0/81 pass, end_vac=0.5394); Clegg 2026 (PMID:42900584: -PI(3,5)P2->ClC-7 hyperactivation driving osmotic vacuolation + Rab/LRRK2 hyperactivation) & Kuwahara 2026 (PMID:42994990: stoichiometric +PI(3)P->direct LRRK2/Rab12/29 + ATG16L1 CASM conjugation; Drosophila C9orf72 DPR secretion in 10.64898/2026.11.09.765393 [PREPRINT]) lower [MODEL_PRIOR] q48h/q72h ODE pass rates from ~79% to ~30% at matched 10-20h repair and 0% at tau=24-48h."
    )
    ev_map["EV-B4-009"].update({
        "cohort_and_stratum": "Open-label NADALS basket trial in ALS (NCT05189106, N=9 enrolled, 5/9 completers; 2 mg QD Wk1-8 -> 4 mg QD Wk9-24; LPs Wk0/8/16 2h post-dose, n=8 PK)",
        "notes": "Descriptive posted CT.gov results (0 inferential p-values): 24-wk dosing with LPs at Wk 0/8/16 (2h post-dose total CSF 1.748 nM at Wk8 & 3.804 nM at Wk16, unbound <4 nM vs proposed 50 nM ceiling); CCL2 was flat (465.9->473.5->442.8 pg/mL), whereas CXCL10 fell -38.1% at Wk16; safety recorded 1/9 PE SAE + 1/9 DVT AE (2 AEs Possibly Related, 0 Probably/Definitely Related).",
    })
    ev_map["EV-B4-011"]["notes"] = (
        "P-gp/BCRP efflux restricts CSF exposure; gnomAD v4.1 MANE ENST00000342505 JAK1 LOEUF=0.168, pLI=1.000 & ENST00000381652 JAK2 LOEUF=0.848 (Open Targets 0.178/0.739; MGI neonatal lethal) + FDA Boxed Warnings require biomarker stratification and thromboprophylaxis."
    )
    ev_map["EV-P2-T3-002"]["notes"] = ev_map["EV-P2-T3-002"]["notes"].replace(
        "with S07 ld-IL-2", "with low-dose IL-2 (EALS-031)"
    )
    ev_map["EV-B6-034"].update({
        "source_type": "IPSC_DRUG_SCREEN",
        "effect_direction": "INCREASED_SURVIVAL",
    })
    ev_map["EV-B6-035"].update({
        "source_type": "RANDOMIZED_CLINICAL_TRIAL",
        "source_id_or_locator": "CT.gov:NCT04082832;NCT04313166;PMID:25904686",
        "cohort_and_stratum": "Phase 2/3 placebo-controlled ALS RCT NCT04082832 (72 mg/d PO, N=80 est, status UNKNOWN) & OLE NCT04313166 (N=55 actual, COMPLETED)",
        "effect_direction": "UNREPORTED_RCT_OUTCOMES",
        "effect_estimate": "Randomized efficacy unreported (NCT04082832 status UNKNOWN, hasResults=false; OLE NCT04313166 COMPLETED N=55 actual, hasResults=false)",
        "sample_size_n": "",
        "notes": "Both randomized Phase 2/3 NCT04082832 (status UNKNOWN, N=80 estimated) and completed open-label extension NCT04313166 (COMPLETED, N=55 actual) have no posted public clinical results (hasResults=false; program discontinued); [MODEL_PRIOR: 950 nM plasma x fu 0.08 x Kp,uu 0.70 = 53.2 nM] sits ~47x below 2.5 uM screen while 62Cu/64Cu-ATSM PET reflects hypoxic Cu(II)->Cu(I) reductive dissociation/transchelation rather than intact normoxic drug (PMID:25904686).",
    })
    ev_map["EV-B6-036"].update({
        "source_type": "HUMAN_POSTMORTEM_PATHOLOGY",
        "cohort_and_stratum": "Yang 2023 postmortem ALS brains (N=12: 5 vs 4 ALS-TDP + 1 vs 2 ALS-SOD1; n=11 spinal cords)",
        "effect_direction": "NULL_PATHOLOGY",
        "effect_estimate": "No significant reduction in pTDP-43 (% TDP-43+ motor-cortex neurons 0.9% vs 5.1% in 5 vs 4 ALS-TDP, Mann-Whitney p=0.1) or MN loss; higher cortical p62+ astrocytes & fewer spinal Iba1+ microglia",
        "notes": "Yang et al. 2023 (PMID:37317638, PMC10947464 Table 2) examined 6 oral CuATSM-treated vs 6 untreated ALS brains (n=11 spinal cords), mixing 5 vs 4 sporadic ALS-TDP (% TDP-43+ motor-cortex neurons 0.9% vs 5.1%, p=0.1) and 1 vs 2 ALS-SOD1 cases, reporting unchanged pTDP-43 and MN counts alongside higher motor-cortex p62+ astrocytes and fewer spinal Iba1+ microglia — an underpowered observational autopsy series, not randomized clinical futility.",
    })
    ev_map["EV-B5-011"].update({
        "source_id_or_locator": "DS045_TRAUT:Set2_DIA_N259:NPTX2;PMID:40375307",
        "cohort_and_stratum": "Trautwig 2025 Set 2 4-center CSF DIA (50 sALS vs 72 Control, n=122; All-ALS n=187; Emory n=96)",
        "assay_and_contrast": "CSF synaptic pentraxin NPTX2 ANOVA/BH-FDR, TissueBank+Age+Sex HC3 OLS & within-Emory Welch t",
        "effect_estimate": "NPTX2 sALS-Ctrl diff=-0.2021 (p=0.0398, BH-FDR=0.2843; 4C adj OLS beta=-0.1823 p=0.0739 n=122; All-ALS adj beta=-0.2015 p=0.0332 n=187; Emory sALS -0.1184 p=0.2779 n=96; TMT -0.0941 p=0.1867)",
        "p_value": "0.0398",
        "fdr_or_adjusted_p": "0.2843",
        "sample_size_n": "122",
        "notes": "Center/age/sex adjustment attenuates 4-center DIA NPTX2 (All-ALS -0.3332 p=4.60e-4 BH-FDR=0.0073 -> adj beta=-0.2015 p=0.0332; sALS adj p=0.0739; Emory p=0.278), while GRIA4 lacks a validated clinical CSF immunoassay (TMT sALS p=0.392, DIA sALS BH-FDR=0.348) and is dropped as a clinical gate; requires CLSI EP09c (N>=40) DIA-MS-to-ELISA/Simoa NPTX2 bridging.",
    })
    ev_map["EV-B5-012"]["notes"] = (
        "Weiss et al. 2016 (PMID:26911633, N=60 12-wk Phase 2 safety/muscle-cramp trial: mexiletine 300 mg/d reduced cramp frequency/severity without slowing secondary ALSFRS-R, while 900 mg/d had 32% discontinuation), Flecainide FANS (PMID:26844270), and Talampanel (PMID:19961264) show non-stage-gated Na+/AMPA blockade fails progression."
    )

    for s in sn_rows:
        sid = s["subnode_id"]
        if sid == "C015-N1":
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000458591 LOEUF=0.809, pLI=0.232 (7/16.2 LoF; Open Targets v2.1.1 LOEUF=0.472, pLI=0.996); DepMap isEssential=True (mean Chronos=-1.2619, 79.9% <-1.0, n=1,258); IMPC MGI:6383384 hom lethal"
            s["druggability_check"] = "0 human SCFD1 PDB structures: AF-Q8WVM8-F1 (mean pLDDT=84.58) + Rattus norvegicus N-term PDB 1Y9J & yeast Sly1p:Sed5p SM-fold PDB 1MQS (PMID:12426383 [Homology-Inferred]; downstream COPII SEC23A/24A/22B is PDB 3EGD); CHEMBL3752910 (Kd=171 nM) is a promiscuous EPHA3 inhibitor (0.3 nM)."
        elif sid == "C015-N2":
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000206595 LOEUF=0.600, pLI=0.888 (2/10.5 LoF; Open Targets v2.1.1 LOEUF=0.500, pLI=0.939); DepMap isEssential=False (mean Chronos=-0.0184, 0.0% <-1.0, n=1,258); mouse blastocyst KO lethal (PMID:18511420)"
            s["druggability_check"] = "0 experimental PDB structures on human G2E3 (Q7L622; AF-Q7L622-F1 mean pLDDT=85.60 only); Brooks et al. 2008 (PMID:18511420) proved PHD2/PHD3 RING-like domains carry active E3 ubiquitin ligase activity while the C-terminal HECT domain is catalytically inactive; 0 ChEMBL ligands."
            s["subnode_verdict"] = s["subnode_verdict"].replace("LOEUF=0.50", "gnomAD v4.1 MANE LOEUF=0.600 (Open Targets v2.1.1 0.500)")
        elif sid == "C014-N1":
            s["gnomad_essentiality_check"] = "HIGH_LIABILITY_FOR_COMPLETE_ABLATION: gnomAD v4.1 MANE ENST00000397677.6 LOEUF=0.496, pLI=0.984 (13/41.6 LoF; Open Targets v2.1.1 LOEUF=0.430, pLI=0.9996); DepMap isEssential=TRUE across 1,258 screens (mean Chronos=-0.6565, 66.2% <-0.5); required for neuronal SATB2-LEMD2 transcription (PMID:41744617) and telomeres (PMID:41677621)."
            s["druggability_check"] = "INTRATHECAL_ASO_PARTIAL_LOWERING_OR_NUCLEAR_IMPORT_BLOCKADE: Zero clinical trials (NCT=0). Bulk/snRNA-seq mRNA and Spillman DIA protein (p=0.081..0.949) are flat because pathology is SUN1-facilitated nuclear retention (PMID:34321318, PMID:37639327; YCharOS antibodies PMID:42975030), restricting partial <=35-50% KD to 1-based Exon-11 3'-UTR chr8:23260600-23261999(+) (inside Exon 11 chr8:23260538-23261999(+))."
        elif sid == "C014-N2":
            s["gnomad_essentiality_check"] = "PARALOG_COMPENSATED_IN_MITOSIS_BUT_NEURONAL_REPAIR_AND_AUTOPHAGY_REQUIRED: gnomAD v4.1 MANE ENST00000263780.9 LOEUF=1.503 (10/11.2 LoF; Open Targets 1.054) and DepMap Chronos=+0.0259 reflect CHMP2A mitotic compensation, whereas ALS17/FTD3 CHMP2B c.532-1G (chr3:87253711) acts via C-terminal truncation GoF and post-mitotic neurons require WT CHMP2B for autophagy and ANXA11 membrane repair (PMID:42349418 [Extrapolation: plasma membrane]), making pan-allele CHMP2B KD high liability."
            s["druggability_check"] = "SUBUNIT_SELECTIVE_EXPLORATORY_PARTIAL_ASO: Zero clinical trials (NCT=0). Keeley et al. 2024 (PMID:39709457) showed WT CHMP2B promotes nuclear CHMP7 retention in sALS iPSC-MNs alongside Spillman within-C9FTD pellet-vs-homogenate CHMP2B enrichment (+0.887, p=0.00114, n=3 C9FTD; between-genotype pellet padj=0.325 NS) and Zeng 2025 3'-UTR dPAS=+0.0709 (padj=1.88e-3); any exploratory tool ASO must stay inside 1-based Exon-6 3'-UTR chr3:87253823-87255556(+) (Exon 6 chr3:87253712-87255556(+), sparing chr3:87253711 c.532-1G 3'SS), with CHMP7 retained as sole primary target."
        elif sid in {"C018-N1", "C018-N2", "C018-N3"}:
            s["explore_bundled_claim"] = s["explore_bundled_claim"].replace("in D045", "in Trautwig 2025 CSF")
            s["key_risk_or_taste_question"] = s["key_risk_or_taste_question"].replace("in D045", "in Trautwig 2025 CSF")
            if sid == "C018-N1":
                s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000374642 LOEUF=0.997, pLI=0.060 (Open Targets v2.1.1 LOEUF=1.125, pLI=0.271); human biallelic LoF causes >90% penetrant SLE & encapsulated bacterial sepsis; Lobsiger 2013 SOD1 C1qa-/- worsened C-bouton loss"
            elif sid == "C018-N2":
                s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000509305 LOEUF=1.001, pLI=0.249 (Open Targets v2.1.1 LOEUF=1.359, pLI=0.284); human LoF causes severe early-onset SLE & encapsulated bacterial sepsis"
            elif sid == "C018-N3":
                s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000374640 LOEUF=1.643, pLI=0.018 (Open Targets v2.1.1 LOEUF=1.553, pLI=0.058); human C1QC deficiency causes severe SLE & encapsulated bacterial infections"
            s["druggability_check"] = (
                "Reject chronic IV ANX005 (~150 kDa IgG4, 0.2-0.25% CSF:serum entry saturating CSF C1q while recording 3/28 [10.7%] treatment-related AE withdrawals and 2/28 [7.1%] drug-related SAEs in HD NCT04514367, PMID:41787606; hypothesized to reflect a ~180 nM peripheral serum C1q sink [MODEL_PRIOR]), systemic IV BBB-TfR-shuttled IgG (modeled 99.99% serum C1q depletion against hypothesized 180 nM serum C1q [MODEL_PRIOR]), AND unmodified q4w IT 48 kDa Fab (~4x/day CSF bulk-flow washout); advance ONLY ECM-anchored HLE IT anti-C1q Fab/nanobody, continuous IT pump, or IT microglial C1QA/B 2'-O-MOE ASO/di-siRNA (local CNS C1q lowering sparing systemic serum C1q). PDB 1PK6 (1.85A gC1q head, 187 inter-chain pairs <=4.5A, PMID:12960167) vs AF-P02745-F1/AF-P02746-F1/AF-P02747-F1 mature cationic CLR stalk (C1QA aa 23-109, C1QB aa 28-114, C1QC aa 29-112: 27 mature Arg/Lys basic residues per heterotrimer [30 up to aa 114] required for neuronal RNP uptake, PMID:38942014) splits anti-gC1q Fab (head-only) from C1QA/B ASO (head+stalk)."
            )
        elif sid == "C018-N4":
            s["key_risk_or_taste_question"] = "Check Trautwig 2025 CSF C4B/C4A protein statistics and human RCCX C4 CNV short-read mapping artifact in ALS."
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000435363 LOEUF=0.413, pLI=0.998 (Open Targets LOEUF=0.257) — short-read mapping artifact across multi-copy RCCX C4A/C4B segmental duplications (~2-3% of healthy Europeans carry homozygous C4B*Q0 deficiency); GTEx Adrenal=60.93 TPM, Liver=48.24 TPM"
        elif sid == "C023-N1":
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000223369.9 LOEUF=0.636, pLI=0.462 (12/30.6 LoF; p.Tyr64Cys rs138273846 ALS discovery AF=48/26,276 [0.183%], gnomAD Joint AC=982/1,613,908, AF=0.061%, 0 hom); DepMap PAN-ESSENTIAL isEssential=True (mean Chronos=-1.5425, 93.8% <-1.0, n=1,258); biallelic human YKT6 LoF disorder (PMID:38522068)"
            s["druggability_check"] = "Rattus norvegicus closed DPC-bound Ykt6 PDB 3KYQ (2.44A, PMID:20159557 [Ortholog/Detergent-Analog Inferred]) shows Tyr64 (AF-O15498-F1 pLDDT=94.81) contacts acyl ligand DPV201 at 3.46A inside the cytosolic Longin groove (4.29A from Cys66; [MODEL_PRIOR] +85.1 A3 cavity expansion in Y64C) vs human open GGTase-III complex PDB 6J74 (PMID:32128853); 0 ligands, with Cys195-farnesyl steric ejection risk in non-carrier wild-type YKT6 ALS (family-history-specific sALS carrier denominator unreported)."
            s["subnode_verdict"] = "KEEP_EXPLORATORY_UNPROVEN (LEAD SUB-NODE): Convergent exome-wide p.Tyr64Cys (rs138273846, chr7:44206388:A>G, AVI Phred=24.53, top 0.352%, ALS discovery AF=0.183% [48/26,276], gnomAD v4.1 AF=0.061%) + TDP-43 3'UTR lengthening + PTAR1 GGTase-III 170-bp Exon-2 frameshift skip + GC-independent M1/BA9 neuronal downregulation; DepMap Chronos=-1.54 restricts modality strictly to allele-split Longin-groove / exosite stabilization (untested)."
        elif sid == "C023-N2":
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000578049 LOEUF=1.829, pLI=0.047 (Open Targets v2.1.1 LOEUF=0.541, pLI=0.939); DepMap isEssential=True (mean Chronos=-1.1444, 67.5% <-1.0, n=77)"
        elif sid == "C023-N3":
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000294179 LOEUF=0.549, pLI=0.868 (Open Targets v2.1.1 LOEUF=0.538, pLI=0.913); DepMap isEssential=True (mean Chronos=-1.1332, 70.5% <-1.0, n=1,258); IMPC MGI:5692753 hom lethal; human STX5-CDG lethal"
        elif sid == "C023-N4":
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000451249 LOEUF=1.753, pLI=0.244 (Open Targets v2.1.1 LOEUF=0.851, pLI=0.0002); DepMap isEssential=False (mean Chronos=-0.1430, n=1,258); human GOSR1 progressive myoclonic epilepsy (PME)"
        elif sid == "C023-N5":
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000398238 LOEUF=0.425, pLI=0.998 (Open Targets v2.1.1 LOEUF=0.435, pLI=0.9993); DepMap CATASTROPHIC PAN-ESSENTIAL isEssential=True (mean Chronos=-2.4404, min=-4.2584, 99.7% <-1.0, n=1,258); IMPC MGI:5446014 hom lethal; dominant human DEE96 epilepsy"
        elif sid == "C023-N6":
            s["explore_bundled_claim"] = s["explore_bundled_claim"].replace("in D045", "in Trautwig 2025")
            s["key_risk_or_taste_question"] = s["key_risk_or_taste_question"].replace("in D045", "in Trautwig 2025")
            s["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000380191 LOEUF=0.774, pLI=0.481 (Open Targets v2.1.1 LOEUF=0.580, pLI=0.350); DepMap isEssential=False (mean Chronos=-0.0947, n=1,258); IMPC MGI:5588293 subviable"
