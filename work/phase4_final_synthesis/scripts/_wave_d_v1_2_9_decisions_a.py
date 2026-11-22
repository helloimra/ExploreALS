"""Wave D v1.2.9 decision prose updates Part A for registries/candidate_decisions.csv (C004, C008, C009, C012, C024, C010)."""
from __future__ import annotations

TS_WAVE_D = "2026-11-22T01:20:00Z"


def apply_wave_d_decision_patches_a(dm: dict[str, dict[str, str]]) -> None:
    dm["C004"].update({
        "causal_vs_reactive_assessment": "NON_CAUSAL_RODENT_PROMOTER_ARTIFACT: Human in vivo EAAT2 transcriptional induction unvalidated (CHEMBL161 HTS EC50 >10 uM despite fetal astrocyte reporter activity in Lee et al. 2008 PMID:18326497) while endogenous human ALS astrocytic SLC1A2 mRNA is intact",
        "evidence_proves_hypothesis": (
            "Stage 1/2 human ALS PK (NCT00349622, PMID:23613806, PMID:24771634, N=66) confirmed 2-4 g/d IV ceftriaxone sustained ~2-6 uM CSF (>1.0 uM rodent target), "
            "and Lee et al. 2008 (PMID:18326497) reported NF-kappaB-mediated EAAT2 promoter activation in cultured human fetal astrocytes."
        ),
        "evidence_disproves_hypothesis": (
            "Phase 3 Stage 3 RCT NCT00349622 (Cudkowicz et al. 2014 Lancet Neurol PMID:25297012, N=514 randomized [341 vs 173] / N=513 analyzed [340 at 4 g/d IV + ursodiol vs 173 placebo]) "
            "was stopped early by DSMB for futility on co-primary ALSFRS-R slope (+0.09 u/mo, -1.22 vs -1.31, p=0.2370) and survival (HR=0.90 [0.71-1.15], p=0.4146) while causing hepatobiliary AEs in 211/340 (62%) vs 19/173 (11%) (p<0.0001) and biliary SAEs in 41/340 (12.1%) vs 0/173 (0%); "
            "CHEMBL161 HTS records human EAAT2 EC50 >10 uM, Bye 2025 survival was null (+0.274d, p=0.2568, q=0.4657), and human M1 astrocyte (p=0.9086) and NYGC spinal SLC1A2 mRNA (p=0.61-0.72) show zero transcriptional deficit."
        ),
        "factual_justification": (
            "Falsified in a definitive 513-patient Phase 3 ALS RCT (NCT00349622, PMID:25297012: ALSFRS-R p=0.2370, survival HR=0.90 p=0.4146, 12.1% vs 0% biliary SAEs) despite achieving ~2-6 uM human CSF exposure (PMID:24771634), "
            "corroborated by CHEMBL161 human EAAT2 EC50 >10 uM, null sALS iPSC-MN survival (+0.274d, p=0.2568), and intact endogenous human ALS astrocytic SLC1A2 mRNA (scoped strictly to IV ceftriaxone; distinct from direct catalytic EAAT2 transport/trafficking enhancers)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["C008"].update({
        "supporting_evidence_ids": "EV-B5-010;EV-B5-013;EV-B5-014;EV-B5-015;EV-B5-016",
        "evidence_proves_hypothesis": (
            "Ranked #3/107 in Bye 2025 at 2.5 uM (+3.246d across 15 sALS iPSC-MN lines, 14/15 positive, p=2.59e-6, q=5.54e-5, PMID:41286450) "
            "and achieves physiological human NMDA receptor engagement in human CSF (~0.25-0.60 uM at 20 mg/d to ~0.5-1.2 uM at 40 mg/d vs human NMDA Ki=0.54-1.0 uM, PMID:7478269, NDA021487)."
        ),
        "evidence_disproves_hypothesis": (
            "Failed Phase 3 MND-SMART Stage 2 comparison (NCT04302870, Pal et al. 2024 Lancet Neurol PMID:39307154: n=355 ALSFRS-R analyzed [175 memantine 20 mg/d vs 180 placebo] of 369 2-arm randomized [183 vs 186] within N=554 3-arm Cycle 1; ALSFRS-R -0.650 vs -0.655 pts/mo, p=0.36; ITT deaths 49/183 vs 48/186, HR=0.92 p=0.71), "
            "double-dose Phase 2b TAME at 40 mg/d (NCT02118727, Bhai et al. 2025 Muscle Nerve PMID:39511965, N=99 enrolled / N=89 randomized / N=52 completing treatment over 36-wk active + 4-wk washout: null ALSFRS-R p=0.69 & blood/CSF NfL/pNfH/tau), "
            "and MEDALS (NCT00353665, PMID:20565333, N=63), while human ALS M1 corticospinal & cervical neurons already downregulate GRIN1 (log2FC=-0.737, p=0.00167)."
        ),
        "factual_justification": (
            "Target-engaged human clinical futility across Phase 3 MND-SMART (NCT04302870, PMID:39307154: n=355 2-arm Stage 2 comparison, p=0.36, survival HR=0.92), "
            "double-dose 40 mg/d Phase 2b TAME (Bhai et al. 2025 PMID:39511965, N=99 enrolled / N=89 randomized / N=52 completing treatment, null ALSFRS-R & neurofilaments), and MEDALS (N=63) at NMDA-engaging human CSF levels (~0.25-1.2 uM) "
            "refutes symptomatic pan-NMDA pore blockade (whereas 2.5 uM monoculture iPSC-MN rescue plausibly reflects an untested culture-media excitotoxicity mechanism; preserving early NPTX2/TT-SICI-gated KCNQ2 splice rescue)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["C009"].update({
        "causal_vs_reactive_assessment": "OFF_TARGET_MONOAMINERGIC_SEDATION_WITH_CLASS_ISR_FAILURE: Dose-limiting 5-HT2A/alpha1A sedation, anorectic mCPP metabolite & selective eIF2B class futility/NfL rise",
        "evidence_proves_hypothesis": (
            "Ranked #4/107 in Bye 2025 at 2.5 uM (+1.8458d across 15 sALS iPSC-MN lines, 13/15 > DMSO, p=0.00150, q=0.01610, PMID:41286450) "
            "following 20-40 uM cellular ISR translational-restoration screening and murine prion/tauopathy neuroprotection in Halliday et al. 2017 (Brain PMID:28430857)."
        ),
        "evidence_disproves_hypothesis": (
            "Failed Phase 3 MND-SMART Stage 2 comparison (NCT04302870, Pal et al. 2024 PMID:39307154: n=355 analyzed [175 trazodone 200 mg/d vs 180 placebo] of N=371 2-arm randomized; adjusted ALSFRS-R diff +0.065 pts/mo [95% CI -0.095, +0.226], p=0.24; deaths 52/185 vs 48/186, HR=0.95; AEs 90% vs 77%); "
            "at 200 mg/d, Cu,plasma (~187-430 nM) and [MODEL_PRIOR] Cu,brain (~120-280 nM at Kp,uu=0.65) sit 9-21x below 2.5 uM, 71-330x below Halliday 2017's 20-40 uM ISR assays, and 23-160x below Wong et al. 2026's 10-30 uM hCMEC/D3 endothelial sST2 suppression concentrations (PMID:42446992: -35% protein / 0% mRNA at 10 uM, 0 human CSF measurements; leaving >=70% CNS sST2 depletion EALS-007 untested unless archived MND-SMART CSF shows >=50% sST2 drop) while exceeding 5-HT2A/alpha1A Ki (17-47 nM) by 6-16x and generating anorectic 5-HT2C agonist mCPP; "
            "moreover, selective brain-penetrant eIF2B activators failed Phase 2/3 HEALEY Regimen F (ABBV-CLS-7262 NCT05740813: Dose 1 DRR=1.06, Serum NfL GMR=1.092 p=0.0253; Dose 2 DRR=0.96 [0.753, 1.220]) and Regimen G (DNL343 NCT05842941, N=249 randomized [N=325 shared-placebo efficacy cohort]: DRR=1.05 [0.84, 1.31], Pr<1=0.37, log-NfL +0.081 p=0.03)."
        ),
        "factual_justification": (
            "Directly falsified in Phase 3 MND-SMART (NCT04302870, PMID:39307154: n=355 Stage 2 analyzed / N=371 randomized, p=0.24, HR=0.95), reinforced by a 71-330x [MODEL_PRIOR] unbound brain PK deficit vs 20-40 uM ISR rescue (PMID:28430857) "
            "gated by 5-HT2A/alpha1A sedation + mCPP anorexia, and class-wide Phase 2/3 ALS futility with ~8-9% NfL elevation under selective eIF2B activators ABBV-CLS-7262 (NCT05740813) and DNL343 (NCT05842941; preserving selective DNAJB2a and ATG4B proteostasis rescue)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["C012"].update({
        "evidence_proves_hypothesis": (
            "Potent CNS-penetrant non-competitive AMPA receptor (GRIA1-4) antagonist (human GRIA1 IC50=243-623 nM, CHEMBL1214124) "
            "that confirmed human ALS motor-cortex TMS motor-threshold target engagement in single-ascending-dose trial NCT03793868 (N=22)."
        ),
        "evidence_disproves_hypothesis": (
            "Japanese multicenter Phase 2 RCT NCT03019419 (Aizawa et al. 2022 J Neurol PMID:34191081, N=66 randomized 1:1:1 / N=65 ITT treated: 22 placebo, 22 at 4 mg/d, 21 at 8 mg/d) "
            "showed 8 mg/d significantly WORSENED 48-wk MMRM ALSFRS-R decline vs placebo by -8.4 pts (-17.4 vs -9.0, Table 2 95% CI -15.0 to -1.8, p=0.0145; bulbar -2.7, p=0.0206; 4 mg/d -13.4, p=0.1476; LOCF p=0.5519 under 67% [14/21] 8 mg/d dropout) "
            "with higher SAEs (p=0.0483) and 33% (8 mg/d) & 64% (4 mg/d, 14/22) vs 82% (18/22) placebo completion; corroborated by NCT03377309 (N=6 halted due to adverse events) and NCT03020797 (N=12 terminated for low enrollment & disease-progression dropouts), prior pan-AMPA talampanel Phase 2 (PMID:19961264, N=59: nonsignificant slowing trend with poorer tolerability), NDA202834 Boxed Warning, and null Bye 2025 survival (+0.113d, p=0.7610)."
        ),
        "factual_justification": (
            "Direct randomized human ALS clinical harm and CNS intolerability at TMS-confirmed motor-cortex target engagement: Phase 2 RCT NCT03019419 (Aizawa et al. 2022 PMID:34191081, N=65 ITT / 66 randomized) "
            "demonstrated significant 48-wk ALSFRS-R worsening at 8 mg/d (-8.4 pts, p=0.0145; bulbar p=0.0206), higher SAEs (p=0.0483), and 67% dropout (33% [8 mg] & 64% [4 mg] vs 82% placebo completion), corroborated by NCT03377309 AE halt & NCT03020797 low-enrollment/progression stop, talampanel Phase 2 (PMID:19961264: nonsignificant slowing trend with poorer tolerability), and null sALS iPSC-MN survival (+0.113d, q=0.857; scoped to non-selective pan-AMPA blockade, preserving upstream ADAR2/GRIA2 Q607R RNA-editing rescue)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["C024"].update({
        "evidence_proves_hypothesis": (
            "Focal C3 transcript elevation occurs within Zhang 2026 TDP-43+ cervical anterior-horn 55-um multicellular Visium spots (+1.2920, within-donor pseudoreplicated Seurat MAST spot bh_fdr=5.82e-23 across N=14 donors, PMID:42135512), "
            "motivating clinical testing of systemic C3 complement inhibition."
        ),
        "evidence_disproves_hypothesis": (
            "Randomized, double-blind, placebo-controlled Phase 2 MERIDIAN trial (NCT04579666 posted results, N=249 started [169 vs 80] / N=247 mITT [168 pegcetacoplan 1,080 mg SC BIW vs 79 placebo]) "
            "missed Week 52 primary CAFS rank (123.0 [SE 4.71] vs 126.0 [SE 6.89]; ANCOVA LS mean diff -3.0, 95% CI -19.5 to +13.5, p=0.7205) and all secondary endpoints (ALSFRS-R p=0.6447, %SVC -6.6% p=0.0949, HHD p=0.0935, ALSAQ-40 +6.5 pts worse QoL p=0.0069) and terminated for futility, "
            "echoing systemic terminal C5 failures (Phase 3 CHAMPION-ALS ravulizumab NCT04248465 PMID:37695623; Phase 2/3 HEALEY zilucoplan NCT04436497 PMID:39960672), while living-CSF C3 fails proteome-wide FDR (DIA q=0.0708; TMT p=0.6225) and ~43.5 kDa PEGylated pegcetacoplan has unmeasured human CSF PK (limited intact-BBB entry expected against hepatic C3 synthesis, GTEx Liver=1,575 TPM)."
        ),
        "factual_justification": (
            "Directly falsified in a 249-patient randomized placebo-controlled Phase 2 ALS trial: subcutaneous systemic C3 inhibitor pegcetacoplan (MERIDIAN NCT04579666, N=249 started / N=247 mITT [168 vs 79]: Week 52 CAFS LS mean diff -3.0, p=0.7205; ALSFRS-R p=0.6447) "
            "missed primary and all secondary endpoints alongside Phase 3 ravulizumab (NCT04248465, PMID:37695623) and Phase 2/3 HEALEY zilucoplan (NCT04436497, PMID:39960672; strictly scoped to systemic C3/C5 regimens with unmeasured/limited CNS entry, preserving CNS-compartmentalized intrathecal C1q blockade, PMID:42492371)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["C010"].update({
        "evidence_proves_hypothesis": (
            "Nominated from iPSC-MN phenotypic screening (Fujimori et al. 2018 Nat Med PMID:30127392) and open-label extension observations in single-center Phase 1/2a ROPALS "
            "(UMIN000034954, Morimoto et al. 2023 PMID:37267913, N=20; noting Fig. S5 reported 0.1-10 nM partial phenotype reduction in mutant FUS/TDP-43 lines alongside 1-10 uM D2R-independent SREBP2/cholesterol and phenolic antioxidant effects in sALS lines, PMID:40826812)."
        ),
        "evidence_disproves_hypothesis": (
            "At 16 mg/d ER MTD (76.9% GI AEs blocking dose escalation, Table S3), human ALS Week-24 CSF ropinirole (Table S3 mean 17,884 pg/mL = 68.68 nM on free-base MW 260.38 vs ~18 nM stated in Morimoto 2023 Discussion; engages DRD2/3 Ki 2.9-7.2 nM) "
            "sits 14.6-556x below 1-10 uM D2R-independent SREBP2/antioxidant sALS rescue (PMID:37267913, PMID:40826812; despite 0.1-10 nM mutant FUS/TDP-43 Fig. S5 activity) while human spinal cord lacks DRD3 (0% >=1 CPM; Lumbar DRD2 RIN+GC OLS beta=-0.0651, p=0.4320, N=223); "
            "Bye 2025 showed FDR-significant survival harm across 15 sALS iPSC-MN lines (-0.688d, 12/15 negative, p=0.00292, q=0.0209), cortical BA9 discovery RNA collapsed after GC adjustment, blinded 24-wk ROPALS ALSFRS-R was null (+1.46, 95% CI -3.15 to 6.07, p=0.761, N=20), "
            "and UK Phase 2a EXPERTS-ALS biomarker screen (ISRCTN15525855, 42 dosed / 22 Wk18 analyzed; distinct from a Phase 3 efficacy RCT) closed the 16 mg/d ropinirole arm on Oct 6, 2026 for blood-NfL biomarker futility."
        ),
        "factual_justification": (
            "Insurmountable 14.6-556x human ALS CSF exposure deficit at GI-limited 16 mg/d MTD (Table S3 68.68 nM / Discussion ~18 nM CSF vs 1-10 uM non-D2 sALS rescue, PMID:37267913, PMID:40826812, with absent spinal DRD3 & Lumbar DRD2 beta=-0.0651, p=0.4320, despite 0.1-10 nM mutant FUS/TDP-43 Fig. S5 activity) "
            "plus FDR-significant survival harm across 15 sALS iPSC-MN lines (-0.688d, q=0.0209) and postmortem GC collapse, corroborated by null blinded 24-wk ROPALS (p=0.761, N=20) and Oct 2026 UK Phase 2a EXPERTS-ALS blood-NfL biomarker futility stop (ISRCTN15525855)."
        ),
        "updated_at": TS_WAVE_D,
    })
