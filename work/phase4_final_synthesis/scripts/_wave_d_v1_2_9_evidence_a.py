"""Wave D v1.2.9 patches Part A for candidate_intake_ledger & evidence_ledger (C004, C008, C009, C012, C024, C010)."""
from __future__ import annotations


def apply_wave_d_evidence_part_a(
    it_rows: list[dict[str, str]],
    ev_map: dict[str, dict[str, str]],
) -> None:
    it_map = {r["carbon_id"]: r for r in it_rows}
    it_map["C004"]["staged_dataset_ids"] = "DS005_BYE;DS003_PB;DS001_COUNTS;DS045_TRAUT"
    it_map["C008"]["staged_dataset_ids"] = "DS005_BYE;DS003_PB;DS001_COUNTS"
    it_map["C012"]["staged_dataset_ids"] = "DS005_BYE;DS003_PB;DS001_COUNTS;DS045_TRAUT"
    it_map["S05"]["staged_dataset_ids"] = "DS_PDB;DS_AFDB;DS_CRYPTIC;DS_ZENG_APA"

    # C004 (Ceftriaxone): exact N=514 rand / N=513 analyzed, hepatobiliary AEs 62% vs 11% + biliary SAEs 12.1%, Lee 2008 positive in vitro vs ChEMBL161
    ev_map["EV-B5-006"].update({
        "source_id_or_locator": "NCT00349622;PMID:25297012;PMC4216315",
        "cohort_and_stratum": "Human ALS Phase 3 Stage 3 RCT (N=514 randomized [341 vs 173]; N=513 analyzed [340 ceftriaxone 4 g/d IV + ursodiol vs 173 placebo])",
        "assay_and_contrast": "Co-primary ALSFRS-R monthly slope & tracheostomy-free survival; hepatobiliary AEs/SAEs (Cudkowicz et al. 2014 Lancet Neurol Table 2/3)",
        "effect_estimate": "ALSFRS-R diff +0.09 u/mo (-1.22 vs -1.31, 95% CI -0.06 to 0.24); survival HR=0.90 (95% CI 0.71-1.15, p=0.4146); biliary SAEs 41/340 (12.1%) vs 0/173 (0%)",
        "notes": "Stopped early by DSMB for futility: Stage 3 dosed 4 g/d IV (+300 mg BID ursodiol; 2 g/d Stage 1/2 carryover or toxicity reduction), survival p=0.4146, overall hepatobiliary AEs 211/340 (62%) vs 19/173 (11%) (p<0.0001), serious biliary SAEs 41/340 (12.1%) vs 0/173 (0%).",
    })
    ev_map["EV-B5-007"].update({
        "source_type": "HUMAN_CSF_PK_POTENCY",
        "source_id_or_locator": "PMID:24771634;PMID:23613806;PMID:18326497;CHEMBL161",
        "notes": "Stage 1/2 ALS CSF reached ~2-6 uM (>1.0 uM prespecified rodent benchmark, PMID:23613806, PMID:24771634); although Lee et al. 2008 J Biol Chem PMID:18326497 reported positive NF-kappaB-mediated EAAT2 promoter activation in cultured human fetal astrocytes, independent ChEMBL161 HTS records EC50 >10 uM and human in vivo EAAT2 induction was never validated.",
    })

    # C008 (Memantine): MND-SMART Stage 2 n=355 (175 vs 180; 369 2-arm rand out of 554 Cycle 1), Bhai et al. 2025 TAME N=99 rand / N=89 analyzed
    ev_map["EV-B5-014"].update({
        "source_type": "CLINICAL_TRIAL_PHASE3_RCT",
        "source_id_or_locator": "NCT04302870;PMID:39307154",
        "cohort_and_stratum": "UK MND-SMART Phase 3 adaptive platform RCT Stage 2 comparison (n=355 analyzed: 175 memantine 20 mg/d vs 180 placebo; 369 2-arm randomized within N=554 3-arm Cycle 1)",
        "assay_and_contrast": "Monthly ALSFRS-R rate of change & overall survival (Pal et al. 2024 Lancet Neurol Table 2/3)",
        "effect_estimate": "ALSFRS-R -0.650 vs -0.655 pts/mo (adj diff -0.021 or +0.033/mo, 1-sided 90% CI lower bound -0.085); deaths 49/183 vs 48/186 (HR=0.92, p=0.71)",
        "sample_size_n": "355",
        "notes": "Isolates the 2-arm memantine vs contemporaneous placebo Stage 2 analysis set (n=355 ALSFRS-R analyzed [175 vs 180] of 369 randomized [183 vs 186]; excluding 185 trazodone-arm patients from the 554-patient 3-arm Cycle 1 total, Pal et al. 2024 PMID:39307154).",
    })
    ev_map["EV-B5-015"].update({
        "source_type": "CLINICAL_TRIAL_PHASE2_3_RCT",
        "source_id_or_locator": "NCT02118727;PMID:39511965;PMC11632565;NCT00353665;PMID:20565333;NCT00409721;NCT01020331",
        "cohort_and_stratum": "US TAME Phase 2b RCT (Bhai et al. 2025: N=99 enrolled / N=89 randomized / N=52 completing treatment, 40 mg/d x 36 wk + 4-wk washout) & MEDALS Phase 2/3 RCT (N=63, 20 mg/d x 12 mo)",
        "effect_estimate": "TAME 40 mg/d (2x AD dose) ALSFRS-R slope p=0.69 & CSF/blood NfL/pNfH/tau null; MEDALS 20 mg/d 12-mo ALSFRS/survival null",
        "notes": "Bhai et al. 2025 Muscle Nerve PMID:39511965 (PMC11632565, NCT02118727: 99 enrolled, 89 randomized 2:1, 52 completing treatment across 36-wk active 40 mg/d + 4-wk washout) and de Carvalho et al. 2010 PMID:20565333 (NCT00353665, N=63), plus NCT00409721 (N=42) & NCT01020331 (N=20), all showed no functional or biomarker benefit.",
    })
    ev_map["EV-B5-016"].update({
        "source_id_or_locator": "PMID:7478269;OpenFDA:NDA021487;CHEMBL807",
        "effect_estimate": "Human CSF/serum ratio 0.52 -> Cu,CSF ~0.25-0.60 uM (20 mg/d) to ~0.5-1.2 uM (40 mg/d) vs human NMDA Ki=0.54-1.0 uM",
    })

    # C009 (Trazodone): Halliday 2017 20/40 uM + mouse prion/tau + mCPP metabolite + MND-SMART Stage 2 n=355 + live NCT05842941 & NCT05740813
    ev_map["EV-B4-001"].update({
        "notes": "Exact Wilcoxon p=2.44e-4; LODO max p=0.00347; occurs at 2.5 uM ([MODEL_PRIOR] ~9-21x above modeled human unbound brain Cmax ~120-280 nM).",
    })
    ev_map["EV-B4-002"].update({
        "source_id_or_locator": "CHEMBL621;CHEMBL1200798;OpenFDA:Trazodone;PMID:28430857",
        "effect_estimate": "Cu,plasma ~187-430 nM; [MODEL_PRIOR] Cu,brain ~120-280 nM (fu,p=0.05-0.11, Kp,uu=0.65): 9-21x below 2.5 uM screen; 71-330x below Halliday 2017 20-40 uM ISR assays",
        "notes": "Exceeds 5-HT2A IC50 (17 nM) & alpha1A Ki (47 nM) by 6-16x (driving dose-limiting somnolence & orthostasis) and generates CNS-penetrant CYP3A4 metabolite mCPP (5-HT2C/2B agonist driving anorexia/nausea without ISR rescue); Halliday et al. 2017 Brain PMID:28430857 tested trazodone at 20 uM (CHO reporter) and 40 uM (cellular ISR rescue) alongside mouse prion/tauopathy dosing.",
    })
    ev_map["EV-B4-003"].update({
        "cohort_and_stratum": "MND-SMART Phase 3 adaptive RCT trazodone comparison (n=355 Stage 2 analyzed [175 vs 180]; N=371 2-arm randomized [185 trazodone 200 mg/d vs 186 placebo])",
        "effect_estimate": "ALSFRS-R -0.625 vs -0.655 pts/mo (adjusted diff +0.065, 95% CI -0.095 to +0.226); deaths 52/185 vs 48/186 (HR=0.95); AEs 90% vs 77%",
        "sample_size_n": "355",
        "notes": "Pal et al. 2024 Lancet Neurol PMID:39307154 Table 2/3: stopped at Stage 2 interim futility boundary (n=355 analyzed across 175 trazodone vs 180 contemporaneous placebo out of 371 randomized in the two arms).",
    })
    ev_map["EV-B4-004"].update({
        "source_type": "CLINICAL_TRIAL_BIOMARKER_AUDIT",
        "source_id_or_locator": "NCT05740813:Regimen_F;NCT05842941:Regimen_G",
        "cohort_and_stratum": "HEALEY ALS Phase 2/3 Regimen F ABBV-CLS-7262 (155 Dose 1, 78 Dose 2 vs 126 shared placebo) & Regimen G DNL343 (186 vs 139 shared placebo, N=325 ECC)",
        "assay_and_contrast": "Posted 24-wk Bayesian ALSFRS-R/mortality DRR & log-transformed NfL biomarker outcomes",
        "effect_estimate": "Regimen F Dose 1 DRR=1.06 [0.850, 1.324] & Serum NfL GMR=1.092 (p=0.0253, n=281; Dose 2 DRR=0.96 [0.753, 1.220], NfL GMR=1.073 p=0.1364); Regimen G DNL343 DRR=1.05 [0.84, 1.31] (Pr<1=0.37) & log-NfL net diff +0.081 (95% CI 0.009-0.153, p=0.03)",
        "notes": "Live ClinicalTrials.gov posted tables: Regimen G DNL343 (NCT05842941, N=325 ECC [186 vs 139]; 249 randomized within Regimen G) posted DRR=1.05 [95% CrI 0.84, 1.31], 24-wk ALSFRS-R net diff -0.41 (p=0.60), and log-transformed NfL LS mean diff +0.081 (~+8.4% GMR, p=0.03, posted under CT.gov ng/L header); Regimen F Dose 2 exploratory upper-limb HHD (+12.3%, p=0.0144) did not rescue primary DRR futility.",
    })

    # C012 (Perampanel): Aizawa 2022 N=65 ITT (66 rand), 4 mg/d completion 64% (14/22), Table 2 CIs & LOCF sensitivity
    ev_map["EV-B5-024"].update({
        "source_type": "CLINICAL_TRIAL_PHASE2_RCT",
        "source_id_or_locator": "NCT03019419;PMID:34191081;PMC8782807",
        "cohort_and_stratum": "Japanese multicenter Phase 2 RCT in sporadic ALS (N=66 randomized 1:1:1; N=65 ITT treated: 22 placebo, 22 at 4 mg/d, 21 at 8 mg/d x 48 wk)",
        "assay_and_contrast": "Primary 48-wk MMRM ALSFRS-R change, bulbar subscore, SAEs & completion (Aizawa et al. 2022 J Neurol Table 2)",
        "effect_estimate": "8 mg/d worsened ALSFRS-R vs placebo by -8.4 pts (-17.4 vs -9.0, 95% CI -15.0 to -1.8; bulbar -2.7, p=0.0206); 4 mg/d -13.4 (p=0.1476); completion 33% (7/21, 8 mg) & 64% (14/22, 4 mg) vs 82% (18/22) placebo",
        "p_value": "0.0145",
        "sample_size_n": "65",
        "notes": "Aizawa et al. 2022 PMID:34191081 (PMC8782807 Table 2; Abstract prints 95% CI -13.9 to -2.9): 1 pre-dosing withdrawal in 8 mg/d yielded N=65 ITT; SAEs higher on 8 mg/d (p=0.0483); LOCF ANCOVA sensitivity gave p=0.5519 due to 67% (14/21) 8 mg/d dropout; scopes harm to non-selective pan-AMPA blockade (distinct from ADAR2/GRIA2 Q607R editing rescue).",
    })
    ev_map["EV-B5-025"].update({
        "source_id_or_locator": "NCT03793868;NCT03377309;NCT03020797;PMID:19961264;CHEMBL1214124;OpenFDA:NDA202834",
        "notes": "US ALS trials NCT03377309 (N=6 halted due to adverse events) and NCT03020797 (N=12 terminated for low enrollment & progression dropouts) plus Phase 2 talampanel (Pascuzzi et al. 2010 PMID:19961264, N=59: nonsignificant slowing trend with poorer tolerability) reinforce class intolerability/lack of efficacy; NDA202834 carries Boxed Warning for serious psychiatric reactions.",
    })

    # C024 (Pegcetacoplan): exact arm Ns (169 vs 80 started; 168 vs 79 mITT), secondary p-values, unglue LOEUF from est, Majumder 2026 PMID:42492371
    ev_map["EV-B3-020"].update({
        "source_type": "CLINICAL_TRIAL_PHASE2_RCT",
        "source_id_or_locator": "NCT04579666;NCT04248465;NCT04436497;PMID:37695623;PMID:39960672;PMID:42492371",
        "cohort_and_stratum": "Phase 2 MERIDIAN SC pegcetacoplan RCT in ALS (N=249 started [169 vs 80]; N=247 mITT [168 pegcetacoplan 1,080 mg BIW vs 79 placebo])",
        "effect_estimate": "MERIDIAN Week 52 CAFS rank ANCOVA LS mean diff -3.0 (123.0 [SE 4.71] vs 126.0 [SE 6.89], 95% CI -19.5 to +13.5)",
        "notes": "Posted NCT04579666 results (N=249 safety [169 vs 80]; N=247 mITT [168 vs 79]): missed Week 52 CAFS (p=0.7205), ALSFRS-R (p=0.6447), %SVC (-6.6%, p=0.0949), HHD (p=0.0935), and ALSAQ-40 (+6.5 pts worse QoL, p=0.0069), alongside Phase 3 CHAMPION-ALS ravulizumab (NCT04248465, PMID:37695623) & Phase 2/3 HEALEY zilucoplan (NCT04436497, PMID:39960672) futility; ~43.5 kDa PEGylated peptide has unmeasured human CSF PK with limited intact-BBB entry expected vs hepatic C3 sink (GTEx Liver=1,575 TPM; legacy gnomAD v2.1.1 C3 LOEUF=0.552; CNS-targeted C3/C1q distinction noted in PMID:42492371).",
    })

    # C010 (Ropinirole): EV-B5-018 Table S3 vs Discussion CSF & Fig. S5 context, EV-B5-019 exact NYGC Lumbar DRD2 OLS beta=-0.0651, EV-B5-020 EXPERTS-ALS Phase 2a screen
    ev_map["EV-B5-018"].update({
        "source_id_or_locator": "DS_ROPALS:TableS3_PK_Table1_AE;UMIN000034954;PMID:37267913;PMID:30127392;PMID:40826812;GSM6383812;US12678423B2;CHEMBL589",
        "assay_and_contrast": "MW-normalized CSF/plasma molar PK (MW 260.38) vs D2/D3 Ki & assay-specific in vitro precedents",
        "effect_direction": "LOW_NM_D2_ONLY_CONDITIONAL_GAP_VS_ASSAY_SPECIFIC_PRECEDENTS",
        "effect_estimate": "Wk24 CSF Table S3 mean 17,884 pg/mL = 68.68 nM (Discussion ~18 nM) at 16 mg/d ER protocol max (0 AE dose reductions/discontinuations); conditional 14.6-55.6x vs 1 uM neurite/caspase precedent & 146-556x vs 10 uM TARDBP M337V Fig. 3F MEA (sALS Fig. 6A SREBP2 & Figs. 3A-D doses unspecified; Fig. S5 0.1-10 nM in mutant FUS/TDP-43)",
        "notes": "Morimoto et al. 2023 PMID:37267913 Table S3 reports Week-24 CSF mean 17,884 pg/mL = 68.68 nM on free-base MW 260.38 (Discussion ~18 nM) at the 16 mg/d ER protocol maximum (Supplementary Table 1 mmc2.xlsx records 0 AE-related dose reductions, interruptions, or discontinuations despite 76.9% GI AEs); conditional comparison against 1 uM documented in separate neurite/caspase assays (PMID:30127392; US12678423B2 Examples III-1/III-2, whereas Morimoto 2023 Fig. 6A / GSM6383812 sALS SREBP2 RNA-seq specifies ropinirole vs vehicle without an assay concentration) and 10 uM documented for Fig. 3F MEA electrophysiology in engineered TARDBP M337V/+ iPSC-MNs (Asano et al. 2025 PMID:40826812, DOI:10.1111/jnc.70183; Figs. 3A-D ROS/SYTOX concentrations unspecified; minimum sALS rescue concentration unestablished; Fig. S5 0.1-10 nM in mutant FUS/TDP-43).",
    })
    ev_map["EV-B5-019"].update({
        "source_id_or_locator": "DS001_COUNTS:Spinal_Cord_Lumbar:DRD2_DRD3;DS_GC_REF",
        "cohort_and_stratum": "NYGC Lumbar Spinal Cord donor-deduplicated RNA-seq (N=223, RIN+GC OLS)",
        "assay_and_contrast": "RIN+GC-adjusted HC3 OLS on Lumbar DRD2 expression & spinal DRD3 detection",
        "effect_estimate": "Lumbar DRD2 RIN+GC OLS beta=-0.0651 (median 0.70 CPM, <1 CPM in 67.8% ALS); Spinal DRD3 0.0% donors >=1 CPM",
        "notes": "Matched to ds001_nygc_spinal_motor_frontal_audit.csv (Lumbar DRD2 beta_als_adj_rin_gc=-0.0651, p=0.4320, N=223); replicated in NYGC Cervical (N=238: DRD3 0.0% >=1 CPM, DRD2 median 0.59 CPM); Pineda 2024 BA4_M1 L5 snRNA-seq also shows low/unchanged DRD2 (2.83 CPM, p=0.758) & BA9 discovery signature collapsed after GC control.",
    })
    ev_map["EV-B5-020"].update({
        "source_id_or_locator": "UMIN000034954;PMID:37267913;ISRCTN15525855",
        "assay_and_contrast": "Wk 21-24 ALSFRS-R score difference (Main Fig. 3A & Authors' Table D1) & restricted DB-period / Table S4 slope-ratio comparisons",
        "effect_estimate": "ROPALS Wk 21-24 ALSFRS-R diff +1.46 pts (95% CI -3.15 to 6.07, Main Fig. 3A / Authors' Table D1 p=0.533, FDR=0.8661; restricted DB-period 21-24w +0.38, p=0.915; Table S4 24-wk DB/run-in 4-wk change-ratio LS diff -0.212, 95% CI -1.577 to 1.153); Ph2a EXPERTS-ALS blood-NfL futility stop",
        "p_value": "0.5330",
        "fdr_or_adjusted_p": "0.8661",
        "notes": "Morimoto et al. 2023 PMID:37267913 (UMIN000034954, N=20 3:1): Main Fig. 3A and Authors' Table D1 Entire-period Wk 21-24 ALSFRS-R difference is +1.46 pts (95% CI -3.15 to 6.07, p=0.533, FDR=0.8661; restricted DB-period Wk 21-24 row +0.38 pts, 95% CI -6.97 to 7.72, p=0.915; Supplementary Table 4 mmc5.xlsx DB/run-in 4-wk change ratio 1.042 vs 1.254, LS diff -0.212, 95% CI -1.577 to 1.153); corroborated by UK multicenter Phase 2a EXPERTS-ALS biomarker platform screen (ISRCTN15525855, 16 mg/d ER protocol max, 42 dosed / 22 Wk18 analyzed; biomarker screen, distinct from a Phase 3 efficacy RCT), which closed the ropinirole arm on Oct 6, 2026 (announced Oct 12-14, 2026) for blood-NfL biomarker futility.",
    })
