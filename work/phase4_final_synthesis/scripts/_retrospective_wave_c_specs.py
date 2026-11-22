"""Wave C v1.2.8 retrospective evidence, statistical contrast, and Living Research Log specs (EV-P4-009, UPD-2026-11-21-03)."""
from __future__ import annotations

WAVE_C_NEW_EVIDENCE_ROWS: list[dict[str, str]] = [
    {
        "evidence_id": "EV-P4-009",
        "carbon_id": "C013",
        "subnode_id": "",
        "analysis_run_id": "RUN-P4-003",
        "source_type": "PIVOTAL_SURVIVAL_RCTS_AND_HUMAN_PK_BENCHMARK",
        "source_id_or_locator": "PMID:8302340;PMID:8676624;PMID:11677002;PMID:17898704;OpenFDA:NDA020599;CHEMBL744;CID:5070",
        "cohort_and_stratum": "Pivotal ALS survival RCTs (Bensimon 1994 N=155; Lacomblez 1996 N=959, Table 2/3) & FDA NDA 020599 / Groeneveld 2001 human PK",
        "assay_and_contrast": "18-mo tracheostomy-free survival RR at 100 mg/d PO + human unbound plasma/CNS PK vs 2.5 uM screen & NaV1.6 IC50",
        "effect_direction": "APPROVED_SOC_SURVIVAL_GAIN_WITH_FRACTIONAL_CNS_ENGAGEMENT",
        "effect_estimate": "Lacomblez 1996 100 mg/d 18-mo Cox RR=0.65 (95% CI 0.50-0.85; Bensimon 1994 N=155 12-mo 74% vs 58%, p=0.014); Cmax,u,plasma=22.2-29.6 nM (85-113x below 2.5 uM screen; [MODEL_PRIOR] Cu,brain ~15-30 nM, ~83-167x below)",
        "p_value": "0.00200",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "959",
        "epistemic_weight": "HIGH_BENCHMARK",
        "notes": "Separates clinical survival efficacy & human PK from Brown 2022 SCN8A splicing (EV-B4-007): Lacomblez et al. 1996 Lancet PMID:8676624 (N=959 across placebo, 50, 100, 200 mg/d; Table 3 100 mg/d 18-mo adjusted Cox RR=0.65, p=0.002; overall dose-response p=0.003) and Bensimon et al. 1994 NEJM PMID:8302340 (N=155, Day-365 survival 74% vs 58%, stratified log-rank p=0.014) established oral riluzole (50 mg BID) as global ALS SOC (+2-3 mo median survival); FDA NDA 020599 establishes mean total plasma Cmax ~173 +/- 72 ng/mL (739 nM, MW 234.20 g/mol) with 96-97% protein binding (fu,p=0.03-0.04 -> Cmax,u,plasma=22.2-29.6 nM; Groeneveld et al. 2001 PMID:11677002 & 2008 PMID:17898704 quantified human ALS serum rather than CSF), yielding [MODEL_PRIOR] P-gp/BCRP-effluxed unbound human CNS peaks of ~15-30 nM (<=50 nM) — ~85-113x below Bye 2025's 2.5 uM screen (~0.01-0.1x NaV1.6 I_NaP IC50 ~0.3-2.0 uM).",
    },
]

WAVE_C_NEW_STAT_SPECS: list[dict[str, str]] = [
    {
        "evidence_id": "EV-P4-009",
        "analysis_run_id": "RUN-P4-003",
        "inference_class": "PUBLISHED_TRIAL_OR_GENETIC_INFERENCE",
        "statistical_unit": "human_trial_or_genetic_participant",
        "n_statistical_units": "959",
        "n_unique_donors_or_participants": "959",
        "exact_contrast": "Lacomblez et al. 1996 international dose-ranging Phase 3 ALS RCT (N=959, Lancet PMID:8676624 Table 3; plus Bensimon 1994 NEJM PMID:8302340 N=155) & FDA NDA 020599 PK | 18-mo tracheostomy-free survival Cox RR (100 mg/d vs placebo) & unbound human PK margin",
        "model_formula_or_test": "Prognostic-covariate-adjusted Cox proportional hazards model at 18 months (100 mg/d PO riluzole vs placebo; plus NDA 020599 unbound plasma/CNS PK)",
        "effect_metric": "adjusted_Cox_RR_and_unbound_PK_nM",
        "effect_estimate": "Lacomblez 1996 100 mg/d 18-mo Cox RR=0.65 (Bensimon 1994 N=155 12-mo 74% vs 58%, p=0.014); Cmax,u,plasma=22.2-29.6 nM (85-113x below 2.5 uM screen; [MODEL_PRIOR] Cu,brain ~15-30 nM, ~83-167x below)",
        "se_or_ci95": "95% CI 0.50-0.85",
        "unadjusted_or_primary_nominal_p": "",
        "covariate_adjusted_nominal_p": "0.00200",
        "multiplicity_adjusted_p": "",
        "multiple_testing_family": "Prespecified dose-ranging Phase 3 Cox comparison (overall dose-trend p=0.003)",
        "missingness_or_exclusion_rule": "Separated from Brown 2022 i3Neuron SCN8A splicing (EV-B4-007) to preserve single-study denominator provenance; Groeneveld 2001 PMID:11677002 serum TDM distinguished from modeled unbound CNS PK",
        "overlap_group_id": "NONE_INDEPENDENT_OR_EXTERNAL",
        "anchor_type": "CACHED_API_SNAPSHOT",
        "anchor_relpath": "work/phase4_final_synthesis/cache/nov2026_retrospective/riluzole_soc_pk_rct_snapshot.json",
    },
]

UPD_2026_11_21_03: dict[str, str] = {
    "update_id": "UPD-2026-11-21-03",
    "date_iso": "2026-11-21",
    "release_tag": "v1.2.8",
    "update_category": "MODEL_REVISION",
    "affected_ids": "EALS-013;EALS-032;EALS-003;EALS-017;EALS-043;EALS-044;EALS-045",
    "decision_impact": "All 7 Wave C Benchmark & Biomarker Verdicts (#30–#36) Confirmed; Rendered Sub-Roles Partitioned Into 4 Calibration & Staging Classes",
    "headline": "Primary-Source Clinical, Pharmacokinetic, Splicing & CSF Proteomic Audit Across Seven Wave C Benchmarks & Biomarkers",
    "prior_state_or_assumption": "(1) Standard-of-Care & Physiological Drug Benchmarks (EALS-013 Riluzole, EALS-032 Methylcobalamin, EALS-003 Ezogabine): Riluzole summaries bundled human CSF PK estimates (~115 nM) into Brown 2022 SCN8A splicing without primary pivotal survival RCT rows or serum-vs-CSF separation, JETALS summaries used randomized N=130 rather than modified-ITT FAS N=129 (p=0.012) and treated JETALS's <=12m inclusion window as a formal Japanese label restriction, and Ezogabine summaries described NCT02450552 as an 8-week trial while grouping non-ALS epilepsy/mood Kv7 trials (XEN1101, BHV-7000) with ALS-active QRL-101; (2) Validated vs Pre-Validation CSF Biomarker Entries (EALS-017 CHIT1/GPNMB/CHI3L1-2, EALS-043 DPP6, EALS-044 DPP10, EALS-045 CFL1): all 7 Wave C entries shared a single generic Benchmark/Biomarker pill, EALS-017 paired rs3831317 with a non-ALS citation and omitted primary GPNMB motor-neuron rescue papers, DPP6/DPP10 cited diffraction (2.8A) rather than refined 3.00A PDB 1XFD resolution and framed Set 1 MS2 TMTpro (omnibus Pr(>F)=0.231 & 0.367) as C9-significant, and CFL1 lacked traumatic-LP hemolysis/platelet OLS controls and SALS LIMK1->pSer3-CFL1 inactivation polarity.",
    "new_evidence_or_revision": "(1) Clinical & PK-Splicing disambiguation: Riluzole (EALS-013) adds standalone pivotal survival & PK record EV-P4-009 (Bensimon 1994 PMID:8302340 N=155 p=0.014; Lacomblez 1996 PMID:8676624 N=959 100 mg/d 18-mo Cox RR=0.65, p=0.002; FDA NDA 020599 mean total plasma Cmax ~173 ng/mL = 739 nM, fu,p=0.03–0.04 -> Cmax,u,plasma = 22.2–29.6 nM [~85–113x below Bye 2025's 2.5 uM screen], Groeneveld 2001 PMID:11677002 serum TDM, and modeled P-gp/BCRP-limited unbound human CNS peak ~15–30 nM [<=50 nM, ~83–167x below 2.5 uM]) and isolates Brown 2022 SCN8A annotated mutually exclusive neonatal Exon 5N -> adult Exon 5A switching (dPSI=+0.2019, FDR=1.95e-6, 0 cryptic junctions; PMID:34425903) in EV-B4-007; Methylcobalamin/Rozebalamin (EALS-032) locks JETALS FAS N=129 (65 vs 64, 126 Wk-16 completers, MMRM +1.97 pts, exact p=0.012, PMID:35532908), Kaji 2019 broad <=3yr Phase 2/3 N=373 randomized / N=370 FAS (50 mg survival p=0.087; <=12m n=144 HR=0.498 p<0.025, PMID:30636701), and Sept 24, 2024 Japan MHLW broad ALS label (50 mg IM 2x/wk, peak plasma ~1.1–1.2 uM vs 2.5 uM [~2.1–2.3x Cmax] ~450–488 nm blue-light photolysis in vitro); Ezogabine (EALS-003) records NCT02450552's 10-wk active regimen (Weeks 6/8 SICI^-1 ratio=1.53 p=0.009, 26.3–30.4% permanent AE dropout, PMID:33226425; Joseph et al. 2025 Nat Neurosci PMID:41174170) and separates QRL-101's 6 completed Phase 1 studies (incl. N=12 ALS NCT06714396 & N=24 HV NCT06681441 where SDTC engaged while TMS-EMG MEP missed) from non-ALS XEN1101 (NCT05614063) and BHV-7000 (failed mood Ph2/3 NCT06419582/NCT06419608; Sept 2026 FDA partial hold on epilepsy NCT06309966/NCT06132893); (2) Validated vs Pre-Validation CSF Markers: EALS-017 anchors human ALS CHIT1 rs3831317 homozygosity (9% [6/65] ALS cases with undetectable CSF CHIT1 yet typical progression in Steinacker 2021 PMID:33576252; Pagliardini 2015 PMID:25563799), primary GPNMB motor-neuron protection (Tanaka 2012 PMID:22891158; Nagahara 2017 PMID:27935101; Diaz-Ortiz 2022 PMID:35981040), Oh 2023 CSF PRM (PMID:37238921), exact gnomAD v4.1 MANE Select metrics, and healthy-control (<=0.92, PMID:31123140) vs mimic (~0.688–0.84, PMID:29142138) AUCs; DPP6 (EALS-043) & DPP10 (EALS-044) lock PDB 1XFD 3.00A homodimer Ser->Asp712 (GKDYGG) / Q8N608 Ser->Gly651 (GKGYGG), Emory DIA Age+Sex OLS (DPP6 p=3.55e-10; DPP10 p=0.00617), and ~82%-overlapping Set 1 18-plex HCD MS2 TMTpro omnibus nulls (Pr(>F)=0.2307 & 0.3671); and CFL1 (EALS-045) adds EV-P3B-029 proving Emory CSF pan-CFL1 elevation survives Age+Sex+HBB+CA1+PRDX2 erythrocyte-hemolysis OLS (beta=+0.3392, p=2.47e-4, n=91, PMID:31566909) and PFN1+TLN1+ACTB platelet OLS (beta=+0.2946, p=2.54e-4, n=92) alongside SALS spinal MN LIMK1->pSer3-CFL1 inactivation (Jagaraj et al. 2026 Brain PMID:41804798; ROCK-ALS Fasudil PMID:39424560).",
    "portfolio_and_gate_consequence": "Preserves all 7 Reclassify · Benchmark/Biomarker verdicts and exact unified portfolio ranks (#30–#36; 0 rank shifts), partitions Explorer badges into Approved SOC Benchmark (#30–#31), Withdrawn PD Calibrator (#32), Validated CSF Staging Panel (#33), and Candidate CSF Marker (#34–#36), steps EALS-045 to 3 open pre-validation gates, and expands SHA-256-anchored statistical contrasts to 199/199.",
    "primary_sources": "PMID:8302340;PMID:8676624;PMID:11677002;PMID:34425903;PMID:35532908;PMID:30636701;PMID:33226425;PMID:41174170;PMID:33576252;PMID:29142138;PMID:22891158;PMID:27935101;PMID:35981040;PMID:37238921;PMID:40375307;PMID:15476821;PMID:41804798;PMID:39424560;PMID:31566909;NCT03548311;NCT00444613;NCT02450552;NCT06714396;NCT06681441",
    "verification_anchor": "EV-P4-009;EV-B4-007;EV-B6-049;EV-B6-050;EV-B5-002;EV-B5-004;EV-B3-008;EV-B3-011;EV-P3B-012;EV-P3B-013;EV-P3B-014;EV-P3B-029;RUN-P4-003",
}
