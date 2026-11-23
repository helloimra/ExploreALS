"""Wave C v1.2.8 patches for candidate_intake_ledger, evidence_ledger & subnode_dissection (C013, S08, C003, C017)."""
from __future__ import annotations


def apply_wave_c_ev_and_sub_patches(
    it_rows: list[dict[str, str]],
    ev_map: dict[str, dict[str, str]],
    sn_rows: list[dict[str, str]],
) -> None:
    it_map = {r["carbon_id"]: r for r in it_rows}
    it_map["C013"]["staged_dataset_ids"] = "DS005_BYE;DS_CRYPTIC"
    it_map["C017"].update({
        "name": "CHIT1 / GPNMB / CHI3L1-CHI3L2 microglial chitinase-lysosomal staging axis",
        "staged_dataset_ids": "DS045_TRAUT;DS045_XML;DS046_OH_XML;DS001_COUNTS;DS001_META;DS001_ONEILL;DS_EDIN_PB;DS031_ZHANG;DS_GNOMAD_V41_CONSTRAINT",
    })

    # C013 (Riluzole): split pure Brown 2022 SCN8A Exon 5N -> 5A mutually exclusive switch on EV-B4-007 from PK/RCT EV-P4-009
    ev_map["EV-B4-006"].update({
        "fdr_or_adjusted_p": "",
        "notes": "Single-test Spearman r=-0.952 across 10/10 overlapping FDR<0.05 sALS-vs-Control DEGs (p=2.28e-5; binomial sign-reversal p=9.77e-4; 45/45 GO sets reversed); DESeq2 transcriptome-wide BH-FDR confirms SK1 channel KCNN1 (+1.319 log2FC, padj=0.00247) and neurofilament heavy NEFH (+0.499, padj=0.00875) upregulation (Bye 2025 PMID:41286450 Table 4/9/11).",
    })
    ev_map["EV-B4-007"].update({
        "source_type": "MAJIQ_SCN8A_SPLICING_RECOMPUTE",
        "source_id_or_locator": "DS_CRYPTIC:Brown2022_MOESM11;PMID:35197628;PMID:34425903",
        "cohort_and_stratum": "Brown et al. 2022 human i3Neuron TDP-43 CRISPRi KD vs Control MAJIQ splicing",
        "assay_and_contrast": "MAJIQ differential splicing of annotated mutually exclusive SCN8A (NaV1.6) Domain I S3-S4 Exon 5N (MOESM11 line 210) vs Exon 5A (MOESM11 line 211)",
        "effect_direction": "NEONATAL_5N_TO_ADULT_5A_HYPERPOLARIZING_SWITCH",
        "effect_estimate": "SCN8A Exon 5N (chr12:51688758-51688849, MOESM11 line 210) PSI 0.578->0.330 (dPSI=-0.2019, source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=1.95e-06, p_d_psi_0_10=0.8435) vs Exon 5A (chr12:51689005-51689096, MOESM11 line 211) PSI 0.422->0.670 (dPSI=+0.2019, source MAJIQ 'FDR'=1.95e-06, p_d_psi_0_10=0.8435; 0 cryptic junctions)",
        "p_value": "",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "",
        "notes": "Brown 2022 MOESM11 contains 0 cryptic junctions in SCN8A; instead, TDP-43 depletion accelerates switching from neonatal Exon 5N (MOESM11 line 210: PSI 0.578->0.330, dPSI=-0.2019, source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=1.94673e-06, p_d_psi_0_10=0.84348) to adult Exon 5A (MOESM11 line 211: PSI 0.422->0.670, dPSI=+0.2019, source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=1.94664e-06, p_d_psi_0_10=0.84348; stored separately from frequentist MOESM12/13 DESeq2 total RNA-seq log2FC=-0.431, BH-FDR=4.85e-4 & Ribo-seq log2FC=-0.692, BH-FDR=0.0155), shifting human NaV1.6 voltage-dependent activation hyperpolarizing and enhancing persistent/resurgent Na+ current (Liang et al. 2021 PMID:34425903).",
    })

    # S08 (Methylcobalamin / Rozebalamin): exact JETALS FAS=129 (126 completers, p=0.012), Kaji 2019 PMID:30636701 FAS=370, MHLW label
    ev_map["EV-B6-049"].update({
        "source_id_or_locator": "NCT03548311;PMID:35532908;CHEMBL4297672",
        "cohort_and_stratum": "JETALS Phase 3 RCT early-stage <=12m ALS (N=130 randomized [65 vs 65]; N=129 FAS [65 vs 64]; 126 Wk-16 completers, 50 mg IM 2x/wk)",
        "assay_and_contrast": "16-wk MMRM ALSFRS-R LS mean change (Oki et al. 2022 JAMA Neurol Table 2 / Fig. 2) & plasma homocysteine",
        "effect_estimate": "ALSFRS-R LS mean diff=+1.97 pts (-2.66 vs -4.63; 95% CI 0.44-3.50; 43% slowing; +2.11 pts [95% CI 0.46-3.76, p=0.01] in n=116 concomitant riluzole)",
        "p_value": "0.01200",
        "sample_size_n": "129",
        "notes": "Oki et al. 2022 JAMA Neurol PMID:35532908 (PMC9086935 Table 2, Fig. 1-2): 130 randomized, 129 modified ITT Full Analysis Set (65 mecobalamin vs 64 placebo; 126 completed Week 16, 124 entered OLE), exact MMRM p=0.012 (printed .01 per journal style), plasma homocysteine -37.2% (p<0.001); secondary FVC (p=0.39) and Norris/ALSAQ-40 were non-significant over 16 weeks; peak human plasma Cmax ~1.1-1.2 uM at 50 mg IM (2x25 mg Rozebalamin vials).",
    })
    ev_map["EV-B6-050"].update({
        "source_id_or_locator": "NCT00444613;PMID:30636701;PMID:35532908;PMDA_MHLW_Japan_2024_09_24:Rozebalamin",
        "cohort_and_stratum": "Prior broad-window (<=3yr onset) Phase 2/3 ALS RCT (N=373 randomized; N=370 FAS, Kaji et al. 2019 Table 2) & Japan MHLW approval",
        "assay_and_contrast": "Primary <=3yr FAS survival/ALSFRS-R co-primary (25 mg & 50 mg IM 2x/wk vs placebo) & post-hoc <=12m stratum",
        "effect_estimate": "Broad <=3yr FAS missed primary survival/ALSFRS-R (50 mg survival p=0.087, ALSFRS-R p=0.19, N=370); <=12m subgroup n=144 HR=0.498 (p<0.025) -> Sept 24, 2024 Japan MHLW Rozebalamin approval",
        "p_value": "0.08700",
        "sample_size_n": "370",
        "notes": "Kaji et al. 2019 JNNP PMID:30636701 (NCT00444613, Table 2 / Fig. 2, N=373 randomized / N=370 FAS across placebo, 25 mg, 50 mg IM twice weekly over 3.5 yr) missed overall co-primaries but identified <=12m symptom-onset benefit (50 mg event-free survival HR=0.498, p<0.025; ALSFRS-R +3.42, p=0.003 across n=144) prospectively confirmed in JETALS; Japan MHLW approved Rozebalamin 25 mg x2 vials (50 mg IM twice weekly) on Sept 24, 2024 for slowing progression of functional impairment in ALS broadly (<=12m was the JETALS trial entry gate, not a formal Japanese label restriction).",
    })
    ev_map["EV-B6-051"].update({
        "notes": "Mechanistic chemical photolability hypothesis: routine ~450-488 nm blue-light live-cell fluorescence imaging cleaves the photosensitive Co-C bond of dissolved 2.5 uM methylcobalamin (~2.1-2.3x human 50 mg IM plasma Cmax ~1.1-1.2 uM) into aquocobalamin/hydroxocobalamin + methyl/superoxide radicals (-3.60d in Bye 2025 PMID:41286450, which lacked dark-shielded control wells), reconciling in vitro toxicity with Phase 3 JETALS clinical benefit (+1.97 pts, PMID:35532908).",
    })

    # C003 (Ezogabine): 10-wk active treatment, Joseph et al. 2025 Nat Neurosci PMID:41174170, QRL-101 6 Ph1s vs XEN1101/BHV-7000 non-ALS status
    ev_map["EV-B5-001"].update({
        "notes": "Exact 2-sided Wilcoxon p=0.1354 (q=0.3292) across 15 sALS lines at 2.5 uM in mature BrainPhys Stage 4 firing media (Bye 2025 PMID:41286450; fails 107-drug BH-FDR despite earlier Wainger 2014 SOD1-A4V iPSC-MN rescue).",
    })
    ev_map["EV-B5-002"].update({
        "source_id_or_locator": "NCT02450552;PMID:33226425;PMID:29672831;PMID:41174170",
        "cohort_and_stratum": "Human ALS Phase 2 physiological RCT (600 mg/d, 900 mg/d, placebo over 10-wk active treatment [4-wk titration + 6-wk maintenance], N=65)",
        "assay_and_contrast": "Primary Weeks 6/8 cortical TMS SICI^-1 ratio & exploratory 10-wk ALSFRS-R/tolerability (Wainger et al. 2021 JAMA Neurol Table 2)",
        "effect_estimate": "900 mg SICI^-1 ratio=1.53 (95% CI 1.12-2.09; +53% inhibition); permanent AE discontinuation 30.4% (600 mg) & 26.3% (900 mg) vs 0% placebo",
        "notes": "Wainger et al. 2021 JAMA Neurol PMID:33226425 (PMC7684515 Table 2 / Fig. 2, N=65: 23 placebo, 23 at 600 mg/d, 19 at 900 mg/d over 10-wk active treatment + 2-wk taper): 600 mg SICI^-1 p=0.31, exploratory unpowered ALSFRS-R slope (-1.01/mo) and SVC/HHD non-significant; Kovalchuk et al. 2018 PMID:29672831 (N=18) proved acute peripheral axonal SDTC/superexcitability engagement, and Joseph et al. 2025 Nat Neurosci PMID:41174170 linked NCT02450552 baseline hyperexcitability/depolarization to faster ALS progression.",
    })
    ev_map["EV-B5-003"].update({
        "source_id_or_locator": "OpenFDA:NDA022345;CHEMBL41355;CID:121892",
        "assay_and_contrast": "Unbound plasma PK (MW 303.34, fup~0.20) & regulatory marketing status",
        "notes": "Voluntarily discontinued commercially by marketing authorization holder in June 2017 with EU marketing authorization withdrawn July 19, 2018 (FDA NDA022345 Discontinued; EMA holder withdrawal alongside 2013 FDA boxed warning / EMA pigmentary restrictions for quinone-dimer retinal maculopathy and mucocutaneous blue-grey discoloration).",
    })
    ev_map["EV-B5-004"].update({
        "source_id_or_locator": "NCT05667779;NCT06532396;NCT06681441;NCT06714396;NCT06877624;NCT07421778;NCT05614063;NCT05716100;NCT05667142;NCT06419582;NCT06419608;NCT06309966;NCT06132893",
        "cohort_and_stratum": "Next-generation non-pigmenting Kv7 openers across ALS (QRL-101) vs non-ALS epilepsy/psychiatry (XEN1101, BHV-7000)",
        "assay_and_contrast": "ClinicalTrials.gov & 2025-2026 sponsor clinical audit across selective Kv7.2/7.3 channel openers",
        "effect_estimate": "QRL-101 completed 6 Phase 1 studies incl. ALS PK/SDTC NCT06714396 (N=12) & HV TMS/NET NCT06681441 (N=24: SDTC positive, TMS-EMG MEP null); 0 ALS trials for XEN1101 or BHV-7000",
        "notes": "All 6 ALS-program Phase 1 trials (NCT05667779, NCT06532396, NCT06681441, NCT06714396, NCT06877624, NCT07421778) belong to QurAlis QRL-101 (where ~50% > ezogabine cross-study SDTC decrease came from N=24 healthy-volunteer NCT06681441, whose cortical TMS-EMG MEP co-primary missed); Xenon azetukalner/XEN1101 (positive Ph3 X-TOLE2 NCT05614063; active Ph3 NCT05716100/NCT05667142) and Biohaven BHV-7000 (failed 2025 Ph2/3 mania NCT06419582 & MDD NCT06419608; Sept 2026 FDA partial clinical hold on focal epilepsy NCT06309966/NCT06132893) have 0 ALS trials.",
    })

    # C017 (CHIT1 / GPNMB / CHI3L1-2): purge WashU+UMilan=63 error, fix PMID:31892365 -> Steinacker 2021 PMID:33576252, add GPNMB primary papers & WashU 2-ordinary-Ctrl results
    bank_note = "4-center DIA total N=259 (Emory 118 [42 sALS + 14 C9 + 8 SOD1 + 54 Ctrl], MGH 78 all code 701 [16 Ctrl + 62 asym], WashU 32 [26 ALS code 100 + 6 comparators code 741: 2 ordinary Ctrl + 4 asym], UMilan 31 [31 ALS, 0 non-ALS]; unresolved Table 2 [WashU=26/0, MGH=0/84] vs MOESM1 Sheet 2 [32/78] bank discrepancy confounds WashU case/comparator status with code 100 vs 741)"
    ev_map["EV-B3-007"]["notes"] = (
        f"{bank_note}; WashU 26 ALS vs 2 ordinary Ctrl +1.972 (Welch p=0.2534, n=25v2; vs 6 comp +1.615, p=0.0300); Emory TMT (N=101: 35 Sporadic vs 44 Ctrl) diff=+0.8716 (p=6.89e-05, q=0.00806); Center+Age+Sex OLS (n=114) beta=+1.9954 (p=3.29e-12); "
        "Center+Batch+Age+Sex OLS (n=114) beta=+1.7955 (p=2.51e-08); Emory DIA Age+Sex OLS (n=89) beta=+2.0111 (p=4.33e-11); C9-Asym (n=59 vs 72) diff=+0.1827 (p=0.2937, q=0.6605); "
        "Sym vs Asym (n=115 vs 72) diff=+2.0657 (p=1.15e-14); SOD1-Asym p=0.8819; Oh 2023 (DS046_OH_XML, PMID:37238921: 5/5 core markers replicated in discovery MS & 4/5 in targeted PRM [CHI3L2 blank, 40/61 cohort overlap]) log2FC=+3.9943 (p=1.88e-5, q<1e-6; longitudinal CSF progression modeling in Vu et al. 2023 PMID:37646115); "
        "CSF chitinases achieve AUC up to 0.92 vs healthy controls (Thompson 2019 PMID:31123140) vs ~0.688-0.84 against neurological ALS mimics (Steinacker 2018 PMID:29142138), supporting symptomatic staging/PD biomarker utility while requiring prospective intended-use calibration before deploying a fixed 4-protein composite decision rule."
    )
    ev_map["EV-B3-008"].update({
        "source_id_or_locator": "DS_GNOMAD_V41_CONSTRAINT:ENST00000367229;PMID:33576252;PMID:25563799;PMID:34873335;NCT06205121",
        "cohort_and_stratum": "Human CHIT1 Exon-10 24-bp null duplication rs3831317 (chr1:203217822) across gnomAD v4 exomes & ALS cohorts (Steinacker 2021 Table 1 / Pagliardini 2015)",
        "notes": "Provenance verified: rs3831317 (chr1:203217822) is the canonical CHIT1 Exon-10 24-bp null duplication (not chr8 rs10955890); Steinacker et al. 2021 PMID:33576252 demonstrated 9% (6/65) homozygous null carriage in ALS patients with undetectable CSF CHIT1 yet typical ALS onset and progression (consistent with Pagliardini 2015 PMID:25563799 & Project MinE GWAS null PMID:34873335; OATD-01 NCT06205121 is in pulmonary sarcoidosis only), refuting CHIT1 inhibition as a causal ALS therapy while mandating rs3831317 genotyping for CSF CHIT1 assay interpretation.",
    })
    ev_map["EV-B3-009"]["notes"] = (
        f"{bank_note}; WashU 26 ALS vs 2 ordinary Ctrl +0.126 (Welch p=0.4982, n=26v2; vs 6 comp +0.161, p=0.4944); Emory TMT (N=101: 35 Sporadic vs 44 Ctrl) diff=+0.1814 (p=0.0142, q=0.3438); Center+Age+Sex OLS (n=120) beta=+0.3550 (p=3.14e-04); "
        "Center+Batch+Age+Sex OLS (n=120) beta=+0.3328 (p=0.00480); Emory DIA Age+Sex OLS (n=95) beta=+0.3483 (p=6.23e-04); C9-Asym (n=59 vs 72) diff=-0.0357 (p=0.6087, q=0.8678); "
        "Sym vs Asym diff=+0.4841 (p=1.70e-07); SOD1-Asym p=0.3127; Oh 2023 (PMID:37238921) log2FC=+1.0694 (p=8.06e-5, q=0.0244); also elevated in AD CSF (PMID:36384809)."
    )
    ev_map["EV-B3-011"].update({
        "source_id_or_locator": "OpenTargets:GCST009325(rs199347);PMID:22891158;PMID:27935101;PMID:26988030;PMID:35981040;PMID:41708347",
        "notes": "Tanaka et al. 2012 PMID:22891158 and Nagahara et al. 2017 PMID:27935101 (plus Ono 2016 PMID:26988030) demonstrated that GPNMB rescues motor neurons from mutant SOD1-G93A and TDP-43 toxicity via ERK1/2 and PI3K/Akt signaling while anti-GPNMB neutralization worsens death; Diaz-Ortiz et al. 2022 Science PMID:35981040 linked chr7p15 PD risk rs199347 (#1 L2G=0.492) to GPNMB, and VRG50635 ALS Phase 1b PMID:41708347 uses CSF GPNMB as a clinical PIKfyve target-engagement biomarker — confirming GPNMB inhibition inverts the protective sign.",
    })
    ev_map["EV-B3-012"]["notes"] = (
        f"{bank_note}; WashU 26 ALS vs 2 ordinary Ctrl +1.709 (Welch p<1e-4, n=26v2; vs 6 comp +1.372, p=7.2e-4); Emory TMT (N=101: 35 Sporadic vs 44 Ctrl) diff=+0.3579 (p=5.15e-05, q=0.00687); Center+Age+Sex OLS (n=122) beta=+0.6473 (p=1.09e-05); "
        "Center+Batch+Age+Sex OLS (n=122) beta=+0.6754 (p=2.27e-05); Emory DIA Age+Sex OLS (n=96) beta=+0.5660 (p=3.08e-04); C9-Asym (n=59 vs 72) diff=-0.0037 (p=0.9676, q=0.9945); "
        "Oh 2023 (PMID:37238921) log2FC=+1.1379 (q=0.044); Edinburgh Astrocyte (N=34) OLS_beta=+2.4065 (p=0.0180); NYGC Cervical M2 beta=+1.5285 (p=3.19e-07) collapses in M3 (n=198) to beta=+0.0876 (p=0.7517)."
    )
    ev_map["EV-B3-013"]["notes"] = (
        f"{bank_note}; WashU 26 ALS vs 2 ordinary Ctrl +0.918 (Welch p<1e-4, n=26v2; vs 6 comp +0.934, p=5.3e-4); Emory TMT (N=101: 35 Sporadic vs 44 Ctrl) diff=+0.4328 (p=1.09e-05, q=0.00281); Center+Age+Sex OLS (n=122) beta=+0.8007 (p=1.96e-09); "
        "Center+Batch+Age+Sex OLS (n=122) beta=+0.6666 (p=6.99e-06); Emory DIA Age+Sex OLS (n=96) beta=+0.7606 (p=5.43e-08); C9-Asym (n=59 vs 72) diff=+0.0491 (p=0.5189, q=0.8217); "
        "Oh 2023 (PMID:37238921) log2FC=+2.5277 (p=2.01e-8, q<1e-6); NYGC Cervical M2 beta=+1.7171 (p=3.13e-10) attenuates in M3 (n=198) to beta=+0.3345 (p=0.1769); pseudochitinase lacking murine ortholog."
    )

    # C017-N1..N4 subnode_dissection.csv exact gnomAD v4.1 MANE Select + primary citations
    sn_map = {s["subnode_id"]: s for s in sn_rows}
    sn_map["C017-N1"].update({
        "gnomad_essentiality_check": "gnomAD v4.1 MANE ENST00000367229 o/e=0.900 (47/52.2 LoF), LOEUF=1.147, pLI=5.54e-15; Exon-10 24-bp null duplication rs3831317 AF=0.2200 (40,441 homozygotes; 9% [6/65] ALS homozygotes with undetectable CSF CHIT1 in Steinacker 2021 PMID:33576252)",
        "subnode_verdict": "RECLASSIFY_BENCHMARK_OR_BIOMARKER: Verified symptomatic CSF staging marker (DIA n=50 vs 72 diff=+2.0060, q=3.24e-09; Center+Batch OLS beta=+1.7955, p=2.51e-08; C9-Asym p=0.2937), but lifelong human CHIT1 knockout (rs3831317 homozygosity: 6/65 [9%] ALS cases in PMID:33576252; Pagliardini 2015 PMID:25563799; Project MinE PMID:34873335) does not prevent ALS or slow progression, while requiring mandatory rs3831317 genotyping to avoid ~5-10% false-negative CSF CHIT1 reads.",
    })
    sn_map["C017-N2"].update({
        "gnomad_essentiality_check": "gnomAD v4.1 MANE ENST00000258733 o/e=1.187 (52/43.8 LoF), LOEUF=1.496, pLI=6.06e-21; biallelic LoF causes amyloidosis cutis dyschromica; PD 7p15 rs199347 #1 L2G=0.492 (PMID:35981040)",
        "druggability_check": "Oncology ectodomain ADC glembatumumab vedotin (not suitable for CNS); validated clinical PIKfyve target-engagement CSF biomarker (VRG50635 PMID:41708347); recombinant GPNMB is neuroprotective in SOD1/TDP-43 models (PMID:22891158, PMID:27935101), with 0 CNS agonists.",
        "subnode_verdict": "RECLASSIFY_BENCHMARK_OR_BIOMARKER (WRONG SIGN FOR INHIBITION): Confirmed DAM/TDP-43+ niche induction (NYGC M3 beta=+2.2014, p=1.90e-18; Zhang 6i_TDP43 +2.5987, bh_fdr=7.15e-19) and symptomatic CSF rise (DIA +0.4020, q=0.00162; BatchOLS +0.3328, p=0.00480), while cortical astrocyte GPNMB falls (-1.6523, p=0.00539) and endogenous GPNMB rescues SOD1/TDP-43 motor neurons (PMID:22891158, PMID:27935101).",
    })
    sn_map["C017-N3"]["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000255409 o/e=0.737 (30/40.7 LoF), LOEUF=1.000, pLI=3.22e-08; Chil1-/- mice viable"
    sn_map["C017-N4"]["gnomad_essentiality_check"] = "gnomAD v4.1 MANE ENST00000369748 o/e=0.954 (38/39.8 LoF), LOEUF=1.250, pLI=5.57e-13; lacks murine ortholog"
