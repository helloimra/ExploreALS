"""Wave C v1.2.8 decision prose updates for registries/candidate_decisions.csv (C013, S08, C003, C017)."""
from __future__ import annotations

TS_WAVE_C = "2026-11-21T23:15:00Z"


def apply_wave_c_decision_patches(dm: dict[str, dict[str, str]]) -> None:
    dm["C013"].update({
        "evidence_proves_hypothesis": (
            "FDA/EMA-approved ALS survival standard of care (Bensimon et al. 1994 NEJM PMID:8302340 N=155, 12-mo survival 74% vs 58%, p=0.014; "
            "Lacomblez et al. 1996 Lancet PMID:8676624 N=959, 100 mg/d 18-mo tracheostomy-free survival 56.8% [134/236] vs 50.4% [122/242] placebo: unadjusted RR=0.79, p=0.076; prognostic-covariate-adjusted Cox RR=0.65 [95% CI 0.50-0.85], p=0.002) and Rank #1/107 hit in Bye 2025 "
            "(+3.959d, 16/16 [100%] sALS lines > DMSO, p=1.24e-12, q=1.32e-10, PMID:41286450), reversing 10/10 overlapping sALS DEGs (Spearman r=-0.952, p=2.28e-5; KCNN1 +1.32 log2FC, padj=0.00247) "
            "and 45/45 GO sets in mature BrainPhys Stage 4 firing media, where TDP-43 loss accelerates SCN8A neonatal Exon 5N -> adult Exon 5A switching (dPSI=+0.2019, FDR=1.95e-6, 0 cryptic junctions; PMID:35197628, PMID:34425903)."
        ),
        "evidence_disproves_hypothesis": (
            "Established background standard-of-care reference rather than a novel discovery asset; at 50 mg oral BID (FDA NDA 020599 mean total plasma Cmax ~173 ng/mL = 739 nM, 96-97% protein-bound -> "
            "Cmax,u,plasma = 22.2-29.6 nM; Groeneveld et al. 2001 PMID:11677002 measured serum rather than CSF), [MODEL_PRIOR] P-gp/BCRP-limited unbound human CNS peak is ~15-30 nM (<=50 nM), "
            "which is ~85-113x below Bye 2025's 2.5 uM screen (~83-167x vs unbound CNS) and achieves fractional NaV1.6 I_NaP inhibition (IC50 ~0.3-2.0 uM) well below 10-50 uM GluR blockade."
        ),
        "factual_justification": (
            "Reclassified as an Approved Standard-of-Care (SOC) survival and iPSC-MN phenotypic/transcriptomic positive-control benchmark (Bensimon 1994 PMID:8302340; Lacomblez 1996 PMID:8676624; "
            "Rank #1/107 in Bye 2025 at supraphysiological 2.5 uM vs ~22-30 nM unbound clinical plasma Cmax / [MODEL_PRIOR] ~15-30 nM unbound human CNS)."
        ),
        "discriminating_next_test": (
            "Deploy as mandatory physiological BrainPhys positive control (paired at clinical unbound 30 nM vs 2.5 uM to separate sub-micromolar NaV1.6 I_NaP / SK channel effects from micromolar polypharmacology) "
            "and background clinical standard of care."
        ),
        "updated_at": TS_WAVE_C,
    })

    dm["S08"].update({
        "evidence_proves_hypothesis": (
            "Phase 3 JETALS RCT (NCT03548311, Oki et al. 2022 JAMA Neurol PMID:35532908, N=130 randomized / N=129 FAS [65 vs 64] / 126 Wk-16 completers, <=12m from symptom onset, 50 mg IM 2x/wk; CHEMBL4297672) "
            "slowed 16-wk MMRM ALSFRS-R decline by 43% (+1.97 pts, -2.66 vs -4.63, 95% CI 0.44-3.50, exact p=0.012; +2.11 pts [p=0.01] in n=116 concomitant riluzole) and lowered plasma homocysteine (-37.2%, p<0.001), "
            "confirming Kaji et al. 2019's <=12m stratum (PMID:30636701, n=144 HR=0.498, p<0.025) and earning Japan MHLW approval on Sept 24, 2024 (Rozebalamin 25 mg x2 vials = 50 mg IM twice weekly)."
        ),
        "evidence_disproves_hypothesis": (
            "Prior broad-window (<=3 yr onset) Phase 2/3 RCT missed overall co-primaries (Kaji et al. 2019 PMID:30636701, NCT00444613, N=373 randomized / N=370 FAS: 50 mg survival p=0.087, ALSFRS-R p=0.19), "
            "16-wk JETALS secondary FVC (p=0.39) was non-significant and Rozebalamin remains unapproved by FDA/EMA (0 active US/EU Phase 3 trials), and unshielded 2.5 uM methylcobalamin (~2.1-2.3x human 50 mg IM plasma Cmax ~1.1-1.2 uM) "
            "scored -3.60d (q=0.00246, Rank #105/107) in Bye 2025, plausibly via ~450-488 nm live-imaging Co-C bond photolysis into aquo/hydroxocobalamin + methyl/ROS radicals."
        ),
        "factual_justification": (
            "Reclassified as a regionally approved Standard-of-Care (SOC) clinical benchmark (Japan MHLW Sept 24, 2024 Rozebalamin 50 mg IM twice weekly for ALS functional slowing, anchored in JETALS <=12m onset N=129 FAS +1.97 ALSFRS-R pts, p=0.012, PMID:35532908) "
            "and iPSC-screen Co-C photolability calibration benchmark."
        ),
        "discriminating_next_test": (
            "Account for concomitant 50 mg IM mecobalamin use when stratifying Japanese ALS trial cohorts (<=12m onset; noting Rozebalamin efficacy is not yet confirmed outside Japan or in non-Japanese East-Asian cohorts), and pair dark-shielded vs ~450-488 nm blue-light-irradiated + hydroxocobalamin controls in live-imaging iPSC-MN screens."
        ),
        "updated_at": TS_WAVE_C,
    })

    dm["C003"].update({
        "prior_art_crowding_level": "HIGH_IN_KV7_CLASS_WITHDRAWN_CHEMICAL_ENTITY (POTIGA NDA022345 discontinued; QRL-101 completed 6 Ph1 studies incl. ALS NCT06714396 & MAD NCT07421778; 0 ALS trials for XEN1101/BHV-7000)",
        "evidence_proves_hypothesis": (
            "Human ALS Phase 2 physiological RCT NCT02450552 (Wainger et al. 2021 JAMA Neurol PMID:33226425, N=65 over 10-wk active treatment [4-wk titration + 6-wk maintenance]) proved 900 mg/d Weeks 6/8 cortical TMS SICI^-1 engagement "
            "(ratio 1.53 [95% CI 1.12-2.09], p=0.009; Joseph et al. 2025 Nat Neurosci PMID:41174170 linked baseline hyperexcitability to faster progression) and Kovalchuk 2018 (N=18, PMID:29672831) proved acute axonal SDTC engagement at Cu,p ~0.22-0.67 uM."
        ),
        "evidence_disproves_hypothesis": (
            "Specific chemical entity voluntarily discontinued commercially by marketing authorization holder in June 2017 with EU marketing authorization withdrawn July 19, 2018 (NDA022345 Discontinued; EMA withdrawal alongside FDA boxed warning for quinone-dimer retinal maculopathy and blue-grey tissue pigmentation), "
            "caused 30.4% (600 mg) and 26.3% (900 mg) permanent AE dropout vs 0% placebo in NCT02450552 (exploratory unpowered 10-wk ALSFRS-R/SVC/HHD non-significant), failed Bye 2025 BrainPhys FDR (+0.779d, q=0.1890), "
            "and is superseded in ALS by non-pigmenting QRL-101 (6 completed Ph1s incl. N=12 ALS NCT06714396 & N=24 HV NCT06681441 where SDTC engaged while TMS-EMG MEP missed; XEN1101 & BHV-7000 have 0 ALS trials, with Sept 2026 FDA partial hold on BHV-7000 epilepsy)."
        ),
        "factual_justification": (
            "Reclassified as a Withdrawn Human Pharmacodynamic Calibrator (NCT02450552 Weeks 6/8 TMS SICI^-1 ratio=1.53, p=0.009 over 10-wk active treatment, PMID:33226425): June 2017 commercial discontinuation and July 19, 2018 EU withdrawal (NDA022345), "
            "26.3-30.4% permanent ALS AE discontinuation, and sub-FDR BrainPhys survival (+0.779d, q=0.189) preclude chronic clinical development while anchoring Kv7.2/7.3 physiological gating for QRL-101 and EALS-006 KCNQ2 splice rescue."
        ),
        "discriminating_next_test": (
            "Use NCT02450552 SICI^-1 (ratio 1.53 at 900 mg/d) and Kovalchuk 2018 peripheral SDTC effect sizes strictly as human Kv7.2/7.3 physiological calibration benchmarks when evaluating QRL-101 ALS data (resolving HV NCT06681441 SDTC vs TMS-EMG dissociation) and EALS-006 KCNQ2 Exon-5 splice-switching ASOs."
        ),
        "updated_at": TS_WAVE_C,
    })

    dm["C017"].update({
        "causal_vs_reactive_assessment": (
            "REACTIVE_BIOMARKER_AND_COMPENSATORY_PROTECTIVE: Human germline CHIT1 knockout (Exon-10 24-bp duplication rs3831317, AF=0.2200, 40,441 gnomAD homozygotes; 9% [6/65] ALS homozygotes with undetectable CSF CHIT1 in Steinacker 2021 PMID:33576252; Pagliardini 2015 PMID:25563799) "
            "does not protect against ALS risk or slow progression; GPNMB (#1 PD 7p15 L2G=0.492, PMID:35981040) rescues SOD1/TDP-43 motor neurons (PMID:22891158, PMID:27935101) so inhibition inverts the therapeutic sign; CHI3L1/CHI3L2 are non-catalytic pseudochitinases (CHI3L2 lacks a mouse ortholog)."
        ),
        "evidence_proves_hypothesis": (
            "Individual protein associations across Trautwig 4-center DIA/TMT CSF (PMID:40375307; noting WashU 26 ALS vs 2 ordinary Ctrl shows CHI3L1/CHI3L2 p<1e-4 while small-n CHIT1 p=0.253 & GPNMB p=0.498, alongside unresolved Table 2 26/84 vs MOESM1 32/78 code 100/741/701 bank provenance), Oh 2023 CSF (PMID:37238921; plus longitudinal CSF progression modeling in Vu et al. 2023 PMID:37646115), case-control clinical immunoassays (Thompson 2019 PMID:31123140 AUC up to 0.92 vs healthy controls vs ~0.688-0.84 vs neurological mimics in Steinacker 2018 PMID:29142138), "
            "NYGC spinal cord, Edinburgh snRNA-seq, and Zhang TDP-43+ spatial niches (with GPNMB separately modulated pharmacodynamically under PIKfyve inhibition, PMID:38606777 / PMID:41708347) position the fixed four-protein panel and its proposed symptomatic staging and treatment-response uses as candidates for prospective validation."
        ),
        "evidence_disproves_hypothesis": (
            "Natural human CHIT1 null homozygosity (rs3831317: 9% [6/65] ALS cases in Steinacker 2021 PMID:33576252; Pagliardini 2015 PMID:25563799; Project MinE GWAS null PMID:34873335) confers neither ALS protection nor survival benefit (while causing ~5-10% false-negative CSF CHIT1 reads if ungenotyped), "
            "endogenous GPNMB is neuroprotective in SOD1/TDP-43 models (Tanaka 2012 PMID:22891158; Nagahara 2017 PMID:27935101 — wrong sign for inhibition), CHI3L1/CHI3L2 lack catalytic activity, and individual case-control associations do not establish a validated fixed 4-protein panel for longitudinal staging, ALS-Glia trial selection, or pharmacodynamic response."
        ),
        "factual_justification": (
            "Individual sub-nodes (C017-N1..N4) show symptomatic-ALS vs control CSF associations across MS and case-control immunoassays (flat cross-sectionally in pre-symptomatic C9orf72/SOD1 carriers, p=0.29-0.97; the fixed four-protein panel and its proposed symptomatic staging, enrichment, and treatment-response uses remain candidates for prospective validation), "
            "while failing therapeutic target criteria: human genetic CHIT1 deficiency (rs3831317, PMID:33576252) does not alter ALS risk or progression, GPNMB is compensatory/neuroprotective (PMID:22891158, PMID:27935101), and CHI3L1/CHI3L2 are catalytically inactive pseudochitinases."
        ),
        "discriminating_next_test": (
            "Prospectively calibrate rs3831317-genotyped (PMID:33576252) CSF Simoa/Ella/ELISA CHIT1 + GPNMB + CHI3L1/CHI3L2 for each intended context of use — longitudinal phenoconversion staging, ALS-Glia trial enrichment, or microglial/lysosomal pharmacodynamic readout (benchmarking mimic specificity ~0.688-0.84 alongside NfL/pNfH, PMID:29142138) — rather than pursuing chitinase or GPNMB inhibition."
        ),
        "updated_at": TS_WAVE_C,
    })
