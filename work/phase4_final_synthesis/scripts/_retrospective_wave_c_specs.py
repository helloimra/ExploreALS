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
        "assay_and_contrast": "18-mo tracheostomy-free survival unadjusted & covariate-adjusted Cox RR at 100 mg/d PO + human unbound plasma/CNS PK vs 2.5 uM screen",
        "effect_direction": "APPROVED_SOC_SURVIVAL_GAIN_WITH_FRACTIONAL_CNS_ENGAGEMENT",
        "effect_estimate": "Lacomblez 1996 100 mg/d 18-mo survival (134/236 [56.8%] vs 122/242 [50.4%] placebo): unadjusted RR=0.79 (p=0.076) & prognostic-covariate-adjusted Cox RR=0.65 (95% CI 0.50-0.85, p=0.002; Bensimon 1994 N=155 12-mo 74% vs 58%, p=0.014); Cmax,u,plasma=22.2-29.6 nM (85-113x below 2.5 uM screen; [MODEL_PRIOR] Cu,brain ~15-30 nM, ~83-167x below)",
        "p_value": "0.0760",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "959",
        "epistemic_weight": "HIGH_BENCHMARK",
        "notes": "Separates clinical survival efficacy & human PK from Brown 2022 SCN8A splicing (EV-B4-007): Lacomblez et al. 1996 Lancet PMID:8676624 (N=959 across placebo, 50, 100, 200 mg/d; 18-mo survival without tracheostomy 134/236 [56.8%] at 100 mg/d vs 122/242 [50.4%] placebo: unadjusted RR=0.79, p=0.076; prognostic-covariate-adjusted Table 3 Cox RR=0.65 [95% CI 0.50-0.85], p=0.002; overall dose-response p=0.003) and Bensimon et al. 1994 NEJM PMID:8302340 (N=155, Day-365 survival 74% vs 58%, stratified log-rank p=0.014) established oral riluzole (50 mg BID) as global ALS SOC (+2-3 mo median survival); FDA NDA 020599 establishes mean total plasma Cmax ~173 +/- 72 ng/mL (739 nM, MW 234.20 g/mol) with 96-97% protein binding (fu,p=0.03-0.04 -> Cmax,u,plasma=22.2-29.6 nM; Groeneveld et al. 2001 PMID:11677002 & 2008 PMID:17898704 quantified human ALS serum rather than CSF), yielding [MODEL_PRIOR] P-gp/BCRP-effluxed unbound human CNS peaks of ~15-30 nM (<=50 nM) — ~85-113x below Bye 2025's 2.5 uM screen (~0.01-0.1x NaV1.6 I_NaP IC50 ~0.3-2.0 uM).",
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
        "exact_contrast": "Lacomblez et al. 1996 international dose-ranging Phase 3 ALS RCT (N=959, Lancet PMID:8676624 Table 2/3; plus Bensimon 1994 NEJM PMID:8302340 N=155) & FDA NDA 020599 PK | 18-mo tracheostomy-free survival unadjusted RR & prognostic-covariate-adjusted Cox RR (100 mg/d vs placebo) + unbound human PK margin",
        "model_formula_or_test": "Unadjusted 18-mo survival relative risk (RR=0.79, p=0.076) & prognostic-covariate-adjusted Cox proportional hazards model (RR=0.65, 95% CI 0.50-0.85, p=0.002) at 100 mg/d PO vs placebo (plus NDA 020599 unbound PK)",
        "effect_metric": "unadjusted_RR_and_adjusted_Cox_RR_plus_unbound_PK_nM",
        "effect_estimate": "Lacomblez 1996 100 mg/d 18-mo survival (134/236 [56.8%] vs 122/242 [50.4%] placebo): unadjusted RR=0.79 (p=0.076) & adjusted Cox RR=0.65 (95% CI 0.50-0.85, p=0.002; Bensimon 1994 N=155 12-mo 74% vs 58%, p=0.014); Cmax,u,plasma=22.2-29.6 nM (85-113x below 2.5 uM screen; [MODEL_PRIOR] Cu,brain ~15-30 nM, ~83-167x below)",
        "se_or_ci95": "95% CI 0.50-0.85 (adjusted Cox RR)",
        "unadjusted_or_primary_nominal_p": "0.0760",
        "covariate_adjusted_nominal_p": "0.00200",
        "multiplicity_adjusted_p": "",
        "multiple_testing_family": "Prespecified dose-ranging Phase 3 100 mg/d comparison (overall dose-trend p=0.003)",
        "missingness_or_exclusion_rule": "Both published 100 mg/d vs placebo survival analyses recorded (unadjusted RR=0.79, p=0.076 & covariate-adjusted Cox RR=0.65, p=0.002); separated from Brown 2022 i3Neuron SCN8A splicing (EV-B4-007); Groeneveld 2001 PMID:11677002 serum TDM distinguished from modeled unbound CNS PK",
        "overlap_group_id": "NONE_INDEPENDENT_OR_EXTERNAL",
        "anchor_type": "CACHED_API_SNAPSHOT",
        "anchor_relpath": "work/phase4_final_synthesis/cache/nov2026_retrospective/riluzole_soc_pk_rct_snapshot.json",
    },
]
