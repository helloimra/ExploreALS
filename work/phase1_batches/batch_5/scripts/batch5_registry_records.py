"""Structured Phase 1 Batch 5 registry records (RUN-B5-001..004, EV-B5-001..028, C003..C012)."""
from __future__ import annotations

RUN_TIMESTAMP = "2026-11-10T23:18:00Z"

ANALYSIS_RUNS: list[dict[str, str]] = [
    {
        "analysis_run_id": "RUN-B5-001",
        "phase_batch": "Batch_5_Clinical_Futility_PK_And_Excitability",
        "script_relpath": "work/phase1_batches/batch_5/scripts/01_bye2025_and_ropals_reanalysis.py",
        "output_artifacts": (
            "work/phase1_batches/batch_5/outputs/bye2025_full_107drug_reanalysis.csv;"
            "work/phase1_batches/batch_5/outputs/bye2025_batch5_and_excitability_summary.json;"
            "work/phase1_batches/batch_5/outputs/ropals_pk_ae_reanalysis.json"
        ),
        "datasets_used": "DS005_BYE;DS_ROPALS",
        "tools_and_skills_used": "uv run python;scipy.stats;openpyxl;SHA-256 verification",
        "reproduced_verified": "True",
        "run_timestamp_utc": RUN_TIMESTAMP,
        "summary": (
            "Donor-level paired t-test, exact Wilcoxon signed-rank, responder rate, and 107-drug BH-FDR "
            "re-computation on DS005_BYE (16 sALS iPSC-MN lines at 2.5 uM + DEG tables) plus exact MW-normalized "
            "molar CSF/plasma PK and adverse-event re-computation on DS_ROPALS (Morimoto 2023)."
        ),
    },
    {
        "analysis_run_id": "RUN-B5-002",
        "phase_batch": "Batch_5_Clinical_Futility_PK_And_Excitability",
        "script_relpath": "work/phase1_batches/batch_5/scripts/02_transcriptomics_proteomics_audit.py",
        "output_artifacts": (
            "work/phase1_batches/batch_5/outputs/ds003_m1_dopamine_receptors_by_celltype.csv;"
            "work/phase1_batches/batch_5/outputs/ds003_m1_excitability_donor_de.csv;"
            "work/phase1_batches/batch_5/outputs/ds001_nygc_spinal_motor_frontal_audit.csv;"
            "work/phase1_batches/batch_5/outputs/ds045_csf_synaptic_proteomics.json;"
            "work/phase1_batches/batch_5/outputs/omics_proteomics_audit_summary.json"
        ),
        "datasets_used": "DS003_PB;DS001_COUNTS;DS_GC_REF;DS045_TRAUT",
        "tools_and_skills_used": "uv run python;numpy OLS RIN+GC adjustment;scipy.stats donor-level Welch/MWU",
        "reproduced_verified": "True",
        "run_timestamp_utc": RUN_TIMESTAMP,
        "summary": (
            "Donor-level snRNA-seq pseudobulk audit in DS003_PB BA4_M1 (marker-verified cell_type_index mapping), "
            "4-region donor-deduplicated RIN+GC-adjusted OLS audit in DS001_COUNTS NYGC RNA-seq, and living-patient "
            "CSF synaptic protein audit (NPTX2, NPTXR, NPTX1, GRIA4, SLC1A2) in DS045_TRAUT Set 1 TMT and Set 2 DIA."
        ),
    },
    {
        "analysis_run_id": "RUN-B5-003",
        "phase_batch": "Batch_5_Clinical_Futility_PK_And_Excitability",
        "script_relpath": "work/phase1_batches/batch_5/scripts/03_clinical_pk_prior_art_apis.py",
        "output_artifacts": "work/phase1_batches/batch_5/outputs/tri_pillar_clinical_pk_prior_art.json",
        "datasets_used": "DS_BASE_EV;DS_BASE_SRC",
        "tools_and_skills_used": (
            "clinical-trials-database;openfda-database;chembl-database;pubchem-database;"
            "literature-search-europepmc;pubmed-database"
        ),
        "reproduced_verified": "True",
        "run_timestamp_utc": RUN_TIMESTAMP,
        "summary": (
            "Live API audit across ClinicalTrials.gov v2 (12 targeted NCTs + 7 landscape searches), OpenFDA "
            "(6 NDAs for marketing status, boxed warnings, and plasma protein binding), PubChem + ChEMBL "
            "(InChIKey-verified human target potencies), and PubMed/EuropePMC primary trial/PK literature."
        ),
    },
    {
        "analysis_run_id": "RUN-B5-004",
        "phase_batch": "Batch_5_Clinical_Futility_PK_And_Excitability",
        "script_relpath": "work/phase1_batches/batch_5/scripts/04_populate_batch5_registries_and_verify.py",
        "output_artifacts": (
            "work/phase1_batches/batch_5/analysis_runs.csv;"
            "work/phase1_batches/batch_5/evidence_ledger.csv;"
            "work/phase1_batches/batch_5/candidate_decisions.csv;"
            "work/phase1_batches/batch_5/outputs/batch5_verification_report.json"
        ),
        "datasets_used": "DS005_BYE;DS_ROPALS;DS003_PB;DS001_COUNTS;DS045_TRAUT",
        "tools_and_skills_used": "uv run python;scripts.verify_carbon_als",
        "reproduced_verified": "True",
        "run_timestamp_utc": RUN_TIMESTAMP,
        "summary": (
            "Deterministic assembly of Batch 5 analysis_runs.csv, evidence_ledger.csv, and candidate_decisions.csv "
            "followed by in-memory Epistemic Asymmetry and foreign-key validation via verify_carbon_als."
        ),
    },
]


def _ev(
    evid: str, cid: str, run_id: str, stype: str, loc: str, cohort: str,
    assay: str, direction: str, est: str, pval: str, fdr: str, n: str, weight: str, notes: str
) -> dict[str, str]:
    return {
        "evidence_id": evid, "carbon_id": cid, "subnode_id": "", "analysis_run_id": run_id,
        "source_type": stype, "source_id_or_locator": loc, "cohort_and_stratum": cohort,
        "assay_and_contrast": assay, "effect_direction": direction, "effect_estimate": est,
        "p_value": pval, "fdr_or_adjusted_p": fdr, "sample_size_n": n, "epistemic_weight": weight, "notes": notes,
    }


EVIDENCE_ROWS: list[dict[str, str]] = [
    _ev("EV-B5-001", "C003", "RUN-B5-001", "STAGED_COHORT_RECOMPUTE", "DS005_BYE:Table2_drug_screen:Retigabine",
        "15 human sALS donor iPSC-MN lines", "2.5 uM Retigabine vs paired DMSO survival (days)",
        "POSITIVE_SUB_FDR", "+0.779 d (9/15 positive, rank #16/107, t=+2.046)", "0.0601", "0.1890", "15",
        "MODERATE", "Exact 2-sided Wilcoxon p=0.1354 (q=0.3292); does not pass 107-drug BH-FDR."),
    _ev("EV-B5-002", "C003", "RUN-B5-003", "HUMAN_CLINICAL_TRIAL", "NCT02450552|PMID:33226425|PMC7684515",
        "Human ALS Phase 2 RCT (600 mg/d, 900 mg/d, placebo x 8 wk)", "Cortical TMS SICI inverse ratio & 8-wk ALSFRS-R/dropout",
        "PD_ENGAGED_NO_CLINICAL_RESCUE", "900 mg SICI ratio 1.53 (95% CI 1.12-2.09); permanent drug dropout 26.3-30.4% vs 0% placebo",
        "0.009", "NA", "65", "HIGH", "600 mg SICI p=0.31; 8-wk ALSFRS-R non-significant; Kovalchuk 2018 PMID:29672831 (N=18) confirmed acute axonal PD."),
    _ev("EV-B5-003", "C003", "RUN-B5-003", "PK_SAFETY_REGULATORY", "OpenFDA:NDA022345|CHEMBL41355|CID:121892",
        "Human POTIGA 300 mg TID steady-state vs human Kv7.2/7.3 EC50", "Unbound plasma PK (MW 303.34, fup~0.20) & commercial status",
        "WITHDRAWN_TOXICITY", "Cu,plasma peak/avg/trough = 0.669/0.434/0.224 uM vs Kv7.2/7.3 EC50 0.35-2.5 uM; NDA022345 Discontinued",
        "NA", "NA", "NA", "HIGH", "Withdrawn globally (2017-2018) after quinone-dimer retinal pigmentary maculopathy & blue skin discoloration."),
    _ev("EV-B5-004", "C003", "RUN-B5-003", "CLINICAL_COMPETITOR_LANDSCAPE", "NCT05667779|NCT06681441|NCT06714396|NCT06532396",
        "Next-gen non-pigmenting Kv7.2/7.3 openers (QRL-101, BHV-7000, XEN1101)", "Clinical trial registry audit in ALS & epilepsy",
        "SUPERSEDED_BY_SELECTIVE_OPENERS", "QRL-101 completed 6 Phase 1 studies incl. ALS PK/PD SDTC trial NCT06714396 (N=12); BHV-7000/XEN1101 in Ph3",
        "NA", "NA", "12", "HIGH", "Selective Kv7.2/7.3 openers without aniline/quinone-dimer liability supersede ezogabine as clinical matter."),
    _ev("EV-B5-005", "C004", "RUN-B5-001", "STAGED_COHORT_RECOMPUTE", "DS005_BYE:Table2_drug_screen:Ceftriaxone",
        "16 human sALS donor iPSC-MN lines", "2.5 uM Ceftriaxone vs paired DMSO survival (days)",
        "NULL", "+0.274 d (7/16 positive, median -0.063 d, rank #45/107, t=+1.179)", "0.2568", "0.4657", "16",
        "MODERATE", "Exact 2-sided Wilcoxon p=0.4212; null in human sALS motor neurons."),
    _ev("EV-B5-006", "C004", "RUN-B5-003", "HUMAN_CLINICAL_TRIAL", "NCT00349622|PMID:25297012|PMC4216315",
        "Human ALS Phase 3 Stage 3 RCT (2-4 g/d IV ceftriaxone vs placebo)", "Co-primary ALSFRS-R slope & tracheostomy-free survival; SAEs",
        "FUTILE_WITH_HEPATOBILIARY_SAES", "ALSFRS-R diff +0.09 u/mo (95% CI -0.06 to 0.24); survival HR=0.90 (0.71-1.15); biliary SAEs 12.1% vs 0%",
        "0.2370", "NA", "513", "DEFINITIVE", "Stopped early by DSMB for futility (survival p=0.4146; 41/340 vs 0/173 hepatobiliary/cholelithiasis SAEs)."),
    _ev("EV-B5-007", "C004", "RUN-B5-003", "HUMAN_CSF_PK_POTENCY", "PMID:24771634|PMID:23613806|CHEMBL161",
        "Stage 1/2 ALS patients on 2-4 g/d IV ceftriaxone (N=66)", "Measured human CSF ceftriaxone (MW 554.59) vs human EAAT2 EC50",
        "CNS_EXPOSED_POTENCY_MISMATCH", "Human ALS CSF maintained ~2-6 uM (>1.0 uM prespecified target), whereas ChEMBL161 human EAAT2 EC50 > 10 uM",
        "NA", "NA", "66", "HIGH", "Rules out BBB exclusion of parent target threshold while exposing weak human EAAT2 transcriptional potency."),
    _ev("EV-B5-008", "C004", "RUN-B5-002", "STAGED_COHORT_RECOMPUTE", "DS003_PB:BA4_M1:Astro;DS001_COUNTS:SLC1A2;DS045_TRAUT",
        "Human M1 Astro snRNA-seq (N=31) & NYGC Lumbar/Cervical/Motor bulk (N=223-238)", "Endogenous SLC1A2 (EAAT2) mRNA & CSF protein sALS vs Ctrl",
        "NULL_NO_MRNA_DEFICIT", "M1 Astro SLC1A2 7446 vs 7205 CPM (log2FC=+0.027); NYGC Lumbar beta=-0.055 (p=0.718); CSF TMT diff=-0.028",
        "0.9086", "NA", "31", "HIGH", "Human ALS astrocytes do not exhibit transcriptional SLC1A2 mRNA loss for ceftriaxone to rescue."),
    _ev("EV-B5-009", "C005", "RUN-B5-001", "STAGED_COHORT_RECOMPUTE", "DS005_BYE:Table2_drug_screen:Excitability_Panel",
        "15-16 human sALS donor iPSC-MN lines", "2.5 uM survival across excitability mechanisms vs paired DMSO",
        "MECHANISM_SPLIT", "Riluzole +3.959d (16/16, q=1.32e-10) vs Lamotrigine +0.899d (q=0.0695), Perampanel +0.113d, Mexiletine -0.288d, Flecainide -0.388d (p_W=0.0245)",
        "1.24e-12", "1.32e-10", "16", "HIGH", "Only persistent INaP modulator Riluzole passes FDR (aside from supratherapeutic Memantine); class Ib/Ic Na+ blockers trend negative."),
    _ev("EV-B5-010", "C005", "RUN-B5-002", "STAGED_COHORT_RECOMPUTE", "DS003_PB:BA4_M1:L5_L2_L3;DS001_COUNTS:KCNQ2_GRIN1",
        "Human M1 snRNA-seq (N=25-30) & NYGC 4 CNS regions (N=206-257)", "Donor-level KCNQ2 & GRIN1 expression in ALS vs Control",
        "SELECTIVE_KCNQ2_AND_GRIN1_LOSS", "M1 L5 KCNQ2 log2FC=-0.443 (p=0.000462), GRIN1 log2FC=-0.737 (p=0.00167); NYGC Cervical KCNQ2 beta=-0.815 (p=2.30e-5)",
        "0.000462", "NA", "25", "HIGH", "KCNQ3 & SCN8A unchanged in M1 L5 (p>0.33); Guo 2025 PMID:41174170 confirms TDP-43-driven KCNQ2 exon-5 skipping."),
    _ev("EV-B5-011", "C005", "RUN-B5-002", "STAGED_COHORT_RECOMPUTE", "DS045_TRAUT:Set2_DIA_N259:NPTX2_GRIA4",
        "Living-patient 4-center CSF DIA proteomics (N=259)", "CSF synaptic pentraxin NPTX2 & AMPA subunit GRIA4 in ALS vs Control",
        "DECREASED_SYNAPTIC_DRIVE", "NPTX2 sALS vs Ctrl diff_log2=-0.202 (p=0.0398), ALS vs Ctrl -0.333 (p=0.000460); GRIA4 ALS vs Ctrl -0.284 (p=0.000239)",
        "0.0398", "NA", "259", "HIGH", "Demonstrates living-patient excitatory synaptic loss/hypoexcitability transition in symptomatic ALS."),
    _ev("EV-B5-012", "C005", "RUN-B5-003", "HUMAN_CLINICAL_TRIAL", "PMID:26911633|PMID:26844270|PMID:19961264",
        "Human ALS Phase 2 RCTs of Mexiletine (N=60), Flecainide (FANS), & Talampanel (N=59)", "ALSFRS-R functional slope under blanket Na+ or AMPA blockade",
        "CLINICAL_NULL_ON_PROGRESSION", "Mexiletine 300-900 mg/d reduced cramps without slowing ALSFRS-R; Flecainide 200 mg/d & Talampanel 150 mg/d failed primary slopes",
        "NA", "NA", "60", "HIGH", "Blanket symptomatic Na+ and AMPA blockade repeatedly fail to modify human ALS progression."),
    _ev("EV-B5-013", "C008", "RUN-B5-001", "STAGED_COHORT_RECOMPUTE", "DS005_BYE:Table2_drug_screen:Memantine",
        "15 human sALS donor iPSC-MN lines", "2.5 uM Memantine vs paired DMSO survival (days)",
        "POSITIVE_SUPRATHERAPEUTIC_IN_VITRO", "+3.246 d (14/15 positive, median +4.00 d, rank #3/107, t=+7.570)", "2.59e-6", "5.54e-5", "15",
        "MODERATE", "Exact 2-sided Wilcoxon p=0.000122; tested at 2.5 uM (~4-10x human unbound CSF memantine)."),
    _ev("EV-B5-014", "C008", "RUN-B5-003", "HUMAN_CLINICAL_TRIAL", "NCT04302870|PMID:39307154",
        "UK MND-SMART Phase 3 adaptive platform trial Cycle 1 (N=554 total randomized)", "Memantine 20 mg/d vs contemporaneous placebo ALSFRS-R slope & survival",
        "FUTILE_PHASE3_STOP", "Stopped at Stage 2 interim futility: monthly ALSFRS-R -0.650 vs -0.655 (adj diff +0.033/mo), no survival benefit",
        "0.36", "NA", "554", "DEFINITIVE", "Well-powered multicenter randomized Phase 3 futility stop in human MND/ALS."),
]

EVIDENCE_ROWS.extend([
    _ev("EV-B5-015", "C008", "RUN-B5-003", "HUMAN_CLINICAL_TRIAL", "NCT02118727|PMID:39511965|NCT00353665|PMID:20565333",
        "US TAME Phase 2b (N=89, 40 mg/d x 36 wk) & MEDALS Phase 2/3 (N=63, 20 mg/d x 12 mo)", "ALSFRS-R linear mixed slope, blood pNfH/NfL, & behavioral endpoints",
        "FUTILE_UP_TO_40MG", "No significant difference vs placebo in ALSFRS-R decline, blood neurofilaments, or survival across both RCTs",
        "NS", "NA", "89", "HIGH", "Additional trials NCT00409721 (N=42) & NCT01020331 (N=20) also yielded no controlled functional benefit."),
    _ev("EV-B5-016", "C008", "RUN-B5-003", "HUMAN_CSF_PK_POTENCY", "PMID:7478269|OpenFDA:NDA021487|CHEMBL807",
        "Human memantine CSF/serum PK (5-30 mg/d) & NDA021487 (fup=0.55)", "Unbound human CSF concentration vs human NMDA receptor Ki/IC50",
        "TARGET_ENGAGED_IN_CNS", "Human CSF/serum ratio 0.52 -> ~0.25-0.6 uM CSF at 20-40 mg/d vs human NMDA Ki=0.54-1.0 uM (GRIN1/2A IC50=0.91 uM)",
        "NA", "NA", "NA", "HIGH", "Confirms physiological NMDA target engagement in human ALS CNS while showing Bye 2025 2.5 uM is 4-10x higher."),
    _ev("EV-B5-017", "C010", "RUN-B5-001", "STAGED_COHORT_RECOMPUTE", "DS005_BYE:Table2_drug_screen:Ropinirole",
        "15 human sALS donor iPSC-MN lines", "2.5 uM Ropinirole vs paired DMSO survival (days)",
        "FDR_SIGNIFICANT_SURVIVAL_REDUCTION",
        "-0.688 d (12/15 negative, 1/15 tied at 0.0 d, 2/15 positive [80.0% worsened, 86.7% non-positive], rank #94/107, t=-3.597)",
        "0.00292", "0.0209", "15",
        "HIGH", "Exact 2-sided Wilcoxon p=0.00525 (q=0.0312, 14 non-zero pairs); significant net motor-neuron survival harm across sALS donors."),
    _ev("EV-B5-018", "C010", "RUN-B5-001", "STAGED_COHORT_RECOMPUTE", "DS_ROPALS:TableS3_PK_Table1_AE|PMID:37267913|CHEMBL589",
        "ROPALS Phase 1/2a ALS patients on 16 mg/d ropinirole ER (N=13 CSF, N=18 plasma)", "MW-normalized CSF/plasma molar PK (MW 260.38) vs D2/D3 Ki & non-D2 potency",
        "LOW_NM_D2_ONLY_15_TO_146X_BELOW_NOND2", "Wk24 CSF 17,884 pg/mL = 68.68 nM (95% CI 54.48-86.59 nM); engages DRD2/3 (Ki 2.9-7.2 nM), 14.6-145.6x below 1-10 uM non-D2 rescue",
        "NA", "NA", "13", "HIGH", "Corrects Morimoto Discussion unit typo ('~18 nmol/L' for 17.88 ng/mL); GI AEs in 76.9% vs 14.3% placebo cap dose."),
    _ev("EV-B5-019", "C010", "RUN-B5-002", "STAGED_COHORT_RECOMPUTE", "DS001_COUNTS:DRD2_DRD3;DS003_PB:BA4_M1;DS_BASE_EV:E1749",
        "NYGC Lumbar Spinal Cord donor-deduplicated RNA-seq (N=223)", "Human spinal DRD2/DRD3 expression & BA9 GC-adjusted signature",
        "SPINAL_DRD3_ABSENT_DRD2_TRACE_BA9_COLLAPSED", "Spinal DRD3 0.0% donors >=1 CPM; Lumbar DRD2 median 0.70 CPM (<1 CPM in 67.8% ALS)",
        "0.4320", "", "223", "HIGH", "Replicated in NYGC Cervical (N=238: DRD3 0.0% >=1 CPM, DRD2 median 0.59 CPM); M1 L5 DRD2 median 2.83 CPM; BA9 signature collapsed after GC control."),
    _ev("EV-B5-020", "C010", "RUN-B5-003", "HUMAN_CLINICAL_TRIAL", "UMIN000034954|PMID:37267913|ISRCTN15525855",
        "ROPALS Ph1/2a double-blind RCT (N=20: 13 ropinirole vs 7 placebo)", "24-wk blinded ALSFRS-R primary outcome",
        "BLINDED_NULL_AND_NFL_FUTILITY_STOP", "ROPALS 24-wk DB ALSFRS-R diff +1.46 (95% CI -3.15 to 6.07, null)",
        "NS", "", "20", "DEFINITIVE", "Corroborated by UK multicenter EXPERTS-ALS platform trial (ISRCTN15525855, 16 mg/d ER), which stopped the ropinirole arm Oct 2026 for futility (no blood NfL reduction)."),
    _ev("EV-B5-021", "C011", "RUN-B5-003", "PK_SAFETY_REGULATORY", "OpenFDA:NDA016273|CHEMBL35|PMID:29959396|PMID:28456721",
        "Human oral furosemide 40 mg PK (MW 330.74, 91-99% albumin bound) vs hNKCC1A/B IC50", "Unbound plasma & OAT3/MRP4-effluxed CNS exposure vs human NKCC1 potency",
        "SEVERE_500_TO_5000X_CNS_EXPOSURE_DEFICIT", "fup=0.01-0.02 -> Cu,plasma ~0.05-0.14 uM; BBB/choroid efflux yields Cu,CNS <1-5 nM vs hNKCC1 IC50 ~18-23 uM",
        "NA", "NA", "NA", "DEFINITIVE", "Systemic loop diuresis/hypokalemia/dehydration ceiling prevents CNS target engagement; 0 ALS trials on CT.gov."),
    _ev("EV-B5-022", "C011", "RUN-B5-002", "STAGED_COHORT_RECOMPUTE", "DS001_COUNTS:Spinal_Cord_Cervical:SLC12A5",
        "NYGC Cervical Spinal Cord donor-deduplicated RNA-seq (N=238: 197 ALS vs 41 Ctrl)", "RIN+GC-adjusted OLS expression of neuronal chloride extruder SLC12A5 (KCC2)",
        "KCC2_DOWNREGULATED_MECHANISM_HAZARD", "NYGC Cervical SLC12A5 beta=-0.595 (unadj diff_log2=-0.658)",
        "0.0342", "", "238", "HIGH", "Corroborated in DS005_BYE Table 4 sALS vs Control iPSC-MNs (log2FC=-0.391, p=0.000557, padj=0.0486); furosemide co-inhibits KCC2 and oral 40 mg reduces human spinal Renshaw inhibition (PMC4221825)."),
    _ev("EV-B5-023", "C012", "RUN-B5-001", "STAGED_COHORT_RECOMPUTE", "DS005_BYE:Table2_drug_screen:Perampanel",
        "15 human sALS donor iPSC-MN lines", "2.5 uM Perampanel vs paired DMSO survival (days)",
        "NULL", "+0.113 d (8/15 positive, median +0.063 d, rank #59/107, t=+0.310)", "0.7610", "0.8572", "15",
        "MODERATE", "Exact 2-sided Wilcoxon p=0.7354; complete lack of survival rescue in sALS iPSC-MNs."),
    _ev("EV-B5-024", "C012", "RUN-B5-003", "HUMAN_CLINICAL_TRIAL", "NCT03019419|PMID:34191081|PMC8782807",
        "Japanese multicenter Phase 2 RCT in sporadic ALS (placebo, 4 mg/d, 8 mg/d x 48 wk)", "Primary 48-wk ALSFRS-R change, bulbar subscore, SAEs, & completion",
        "CLINICAL_WORSENING_AND_INTOLERABILITY", "8 mg/d worsened ALSFRS-R decline vs placebo by -8.4 pts (bulbar-driven); SAEs higher (p=0.0483); completion 33% vs 82%",
        "0.015", "NA", "66", "DEFINITIVE", "4 mg/d also showed no benefit; demonstrates dose-dependent functional and bulbar harm under chronic AMPA blockade."),
    _ev("EV-B5-025", "C012", "RUN-B5-003", "HUMAN_CLINICAL_TRIAL", "NCT03793868|CHEMBL1214124|OpenFDA:NDA202834",
        "Human ALS Single-Ascending-Dose TMS biomarker study NCT03793868 (N=22)", "Motor-cortex TMS motor threshold target engagement & human GRIA1 IC50",
        "TERMINATED_ADVERSE_EVENTS_AT_TARGET_ENGAGEMENT", "Confirmed human ALS motor-cortex TMS threshold engagement (N=22) at human GRIA1 IC50=243-623 nM",
        "NA", "", "22", "HIGH", "Additional US ALS trials NCT03377309 (N=6 halted due to adverse events) and NCT03020797 (N=12 terminated for low enrollment & early progression dropouts) failed tolerability; NDA202834 carries Boxed Warning for serious psychiatric reactions."),
])


CANDIDATE_DECISIONS: list[dict[str, str]] = [
    {
        "carbon_id": "C003", "name": "Ezogabine (retigabine)", "track": "A",
        "phase1_batch": "Batch_5_Clinical_Futility_PK_And_Excitability", "reanalysis_state": "ADJUDICATED_VERIFIED",
        "scientific_taste_rating": "MODERATE_BENCHMARK_SUPERSEDED",
        "technical_accuracy_of_explore_claim": "VERIFIED_ACCURATE (ExploreALS correctly parked C003; fresh DS005_BYE re-compute confirms +0.779d, 9/15, p_2s=0.0601, q=0.1890)",
        "causal_vs_reactive_assessment": "UPSTREAM_INTRINSIC_EXCITABILITY_MODULATOR (compensates TDP-43-driven KCNQ2 loss-of-conductance)",
        "prior_art_crowding_level": "HIGH_IN_KV7_CLASS_WITHDRAWN_CHEMICAL_ENTITY (POTIGA NDA022345 discontinued; QRL-101 completed 6 Ph1 studies incl. ALS NCT06714396)",
        "evidence_proves_hypothesis": "Human ALS Phase 2 RCT NCT02450552 (N=65, PMID:33226425) proved 900 mg/d cortical SICI increase (ratio 1.53, p=0.009) and Kovalchuk 2018 (N=18, PMID:29672831) proved acute axonal excitability engagement at Cu,p ~0.22-0.67 uM.",
        "evidence_disproves_hypothesis": "Specific molecule globally withdrawn for quinone-dimer retinal/skin pigmentation (NDA022345 Discontinued), caused 26.3-30.4% permanent ALS dropout vs 0% placebo, failed 8-wk ALSFRS-R and Bye 2025 FDR (q=0.1890), and is superseded by non-pigmenting QRL-101.",
        "epistemic_state": "ESTABLISHED_BENCHMARK", "decision": "RECLASSIFY_BENCHMARK_OR_BIOMARKER",
        "factual_justification": "Ezogabine is an established human ALS Kv7.2/7.3 pharmacodynamic proof-of-mechanism benchmark (NCT02450552 SICI p=0.009), not a viable chronic drug candidate due to global withdrawal (NDA022345 pigmentary maculopathy), 26-30% ALS intolerability, sub-FDR iPSC-MN survival (+0.779d, q=0.189), and clinical replacement by selective non-pigmenting Kv7.2/7.3 opener QRL-101 (NCT06714396) and C006 KCNQ2 splice rescue.",
        "discriminating_next_test": "Use NCT02450552 SICI/SDTC effect sizes exclusively as quantitative PD calibration benchmarks when evaluating QRL-101 Phase 2 ALS data and C006 KCNQ2 exon-5 splice-switching ASOs.",
        "supporting_evidence_ids": "EV-B5-001;EV-B5-002;EV-B5-003;EV-B5-004", "updated_at": RUN_TIMESTAMP,
    },
    {
        "carbon_id": "C004", "name": "Ceftriaxone", "track": "A",
        "phase1_batch": "Batch_5_Clinical_Futility_PK_And_Excitability", "reanalysis_state": "ADJUDICATED_VERIFIED",
        "scientific_taste_rating": "LOW_RODENT_ARTIFACT_FALSIFIED",
        "technical_accuracy_of_explore_claim": "VERIFIED_ACCURATE (DS005_BYE 16-donor null +0.274d, p_2s=0.2568, q=0.4657 and Stage 3 futility confirmed)",
        "causal_vs_reactive_assessment": "NON_CAUSAL_RODENT_PROMOTER_ARTIFACT (human ALS M1 astrocytes and NYGC spinal cord show intact endogenous SLC1A2 mRNA, p=0.72-0.91)",
        "prior_art_crowding_level": "EXHAUSTED_FAILED_PHASE3 (NCT00349622 N=513)",
        "evidence_proves_hypothesis": "Stage 1/2 human ALS PK (PMID:24771634; PMID:23613806, N=66) proved 2-4 g/d IV ceftriaxone entered human CSF (~2-6 uM) above the prespecified 1.0 uM target.",
        "evidence_disproves_hypothesis": "Phase 3 NCT00349622 (N=513, PMID:25297012) stopped for futility on ALSFRS-R (+0.09 u/mo, p=0.237) and survival (HR=0.90, p=0.415) with 12.1% vs 0% hepatobiliary SAEs; ChEMBL161 human EAAT2 EC50 >10 uM; Bye 2025 sALS iPSC-MN null (+0.274d, p=0.257); human M1 astrocyte SLC1A2 mRNA unchanged (p=0.909).",
        "epistemic_state": "FALSIFIED_CLINICAL", "decision": "DROP",
        "factual_justification": "Target-threshold-exposed Phase 3 clinical futility in 513 ALS patients (NCT00349622: ALSFRS-R p=0.2370, survival HR=0.90 p=0.4146) accompanied by severe biliary toxicity (12.1% vs 0% SAEs), weak human EAAT2 potency (EC50 >10 uM vs 2-6 uM CSF), null human sALS iPSC-MN survival (+0.274d, q=0.466), and absence of endogenous human astrocytic SLC1A2 mRNA loss.",
        "discriminating_next_test": "", "supporting_evidence_ids": "EV-B5-005;EV-B5-006;EV-B5-007;EV-B5-008", "updated_at": RUN_TIMESTAMP,
    },
    {
        "carbon_id": "C005", "name": "Context-specific reduction of motor-neuron hyperexcitability", "track": "B",
        "phase1_batch": "Batch_5_Clinical_Futility_PK_And_Excitability", "reanalysis_state": "ADJUDICATED_VERIFIED",
        "scientific_taste_rating": "MODERATE_WHEN_STAGE_AND_KV7_SHARPENED",
        "technical_accuracy_of_explore_claim": "PARTIALLY_CONFLATED_NOW_UNBUNDLED (ExploreALS bundled persistent INaP, Kv7 opening, and failed AMPA/NMDA blockade; unbundled via DS005, DS003, DS001, DS045)",
        "causal_vs_reactive_assessment": "BIPHASIC_STAGE_DEPENDENT (early intrinsic hyperexcitability from TDP-43 KCNQ2 mis-splicing vs symptomatic synaptic loss marked by GRIN1 & CSF NPTX2 drop)",
        "prior_art_crowding_level": "MODERATE_TO_HIGH (blanket Na+/AMPA/NMDA trials crowded & negative; early SICI-stratified Kv7 disease modification untested in Ph2/3)",
        "evidence_proves_hypothesis": "Riluzole (INaP modulator) is #1/107 in DS005_BYE (+3.959d, 16/16, q=1.32e-10); human M1 L5 shows selective KCNQ2 mRNA loss (p=0.000462) replicated across 4 NYGC regions (Cervical p=2.30e-5) plus TDP-43 KCNQ2 exon-5 skipping (PMID:41174170); human TMS SICI responds to Kv7 opening (NCT02450552).",
        "evidence_disproves_hypothesis": "Blanket symptomatic postsynaptic glutamate blockade (Perampanel C012 worsened ALSFRS-R p=0.015; Talampanel PMID:19961264 null; Memantine C008 MND-SMART futile) and class Ib/Ic Na+ blockade (Mexiletine PMID:26911633, Flecainide PMID:26844270; DS005_BYE -0.288 to -0.388d) fail as circuits lose GRIN1 (M1 L5 p=0.00167) and living-CSF NPTX2 (DS045 DIA p=0.0398).",
        "epistemic_state": "UNPROVEN_UNTESTED", "decision": "KEEP_EXPLORATORY_UNPROVEN",
        "factual_justification": "Under Epistemic Asymmetry, blanket late-stage AMPA/NMDA/class-I-Na+ suppression is clinically falsified, whereas early-stage selective Kv7.2 (KCNQ2) restoration prior to synaptic collapse has human genetic/splicing/PD support and remains untested in a stratified disease-modification RCT. GOVERNANCE GUARDRAIL: C005 serves strictly as the stage-gating and biomarker stratification protocol (TMS SICI / axonal SDTC + living-CSF NPTX2/GRIA4) for single-node C006 (KCNQ2), NEVER as a composite multi-channel drug bundle.",
        "discriminating_next_test": "Apply C005 strictly as the stage-gating & biomarker stratification protocol for single-node C006 (KCNQ2) — never as a multi-channel drug bundle — in a Phase 2 trial (or QRL-101/KCNQ2-ASO stratum analysis) enrolling early-onset ALS/presymptomatic carriers with baseline reduced TMS SICI (<=5.5 ms) or elevated axonal SDTC AND preserved living-CSF NPTX2/GRIA4, testing 24-48 wk plasma/CSF NfL reduction.",
        "supporting_evidence_ids": "EV-B5-002;EV-B5-009;EV-B5-010;EV-B5-011;EV-B5-012", "updated_at": RUN_TIMESTAMP,
    },
    {
        "carbon_id": "C008", "name": "Memantine", "track": "A",
        "phase1_batch": "Batch_5_Clinical_Futility_PK_And_Excitability", "reanalysis_state": "ADJUDICATED_VERIFIED",
        "scientific_taste_rating": "LOW_SUPRATHERAPEUTIC_SCREEN_FALSE_POSITIVE",
        "technical_accuracy_of_explore_claim": "VERIFIED_ACCURATE (DS005_BYE +3.246d at 2.5 uM confirmed alongside 4 negative human ALS trials including MND-SMART & 40 mg/d TAME)",
        "causal_vs_reactive_assessment": "DOWNSTREAM_EXCITOTOXIC_ HYPOTHESIS_REFUTED_IN_HUMANS (symptomatic human M1 L2-L6 neurons already downregulate GRIN1, p=1.2e-5 to 0.0017)",
        "prior_art_crowding_level": "EXHAUSTED_FIVE_REGISTERED_ALS_TRIALS (NCT04302870, NCT02118727, NCT00353665, NCT00409721, NCT01020331)",
        "evidence_proves_hypothesis": "Rescued 14/15 sALS iPSC-MN lines at 2.5 uM in DS005_BYE (+3.246d, q=5.54e-5) and reaches ~0.25-0.6 uM unbound human CSF (CSF/serum=0.52, PMID:7478269; fup=0.55, NDA021487) matching human NMDA Ki (0.54-1.0 uM, CHEMBL807).",
        "evidence_disproves_hypothesis": "Target-engaged futility in UK Phase 3 MND-SMART Cycle 1 (NCT04302870, PMID:39307154, N=554: ALSFRS-R -0.650 vs -0.655/mo, one-sided p=0.36), US Phase 2b TAME at double dose 40 mg/d (NCT02118727, PMID:39511965, N=89: null ALSFRS-R & blood pNfH), and MEDALS (NCT00353665, PMID:20565333, N=63).",
        "epistemic_state": "FALSIFIED_CLINICAL", "decision": "DROP",
        "factual_justification": "Target-engaged human clinical futility across Phase 3 MND-SMART (20 mg/d, N=554, p=0.36) and Phase 2b TAME (40 mg/d, N=89, null on ALSFRS-R and pNfH) at CNS concentrations (~0.25-0.6 uM CSF) engaging human NMDA receptors (Ki=0.54-1.0 uM), proving the 2.5 uM Bye 2025 iPSC hit (4-10x human CSF) is a supratherapeutic culture artifact.",
        "discriminating_next_test": "", "supporting_evidence_ids": "EV-B5-010;EV-B5-013;EV-B5-014;EV-B5-015;EV-B5-016", "updated_at": RUN_TIMESTAMP,
    },
    {
        "carbon_id": "C010", "name": "Ropinirole", "track": "A",
        "phase1_batch": "Batch_5_Clinical_Futility_PK_And_Excitability", "reanalysis_state": "ADJUDICATED_VERIFIED",
        "scientific_taste_rating": "LOW_PK_MECHANISM_DISCONNECT_AND_IPSC_HARM",
        "technical_accuracy_of_explore_claim": "VERIFIED_AND_STRENGTHENED (BA9 GC collapse & Bye 2025 -0.688d q=0.0209 harm verified, plus Oct 2026 EXPERTS-ALS NfL futility stop & ROPALS unit error uncovered)",
        "causal_vs_reactive_assessment": "NON_CAUSAL_PLEIOTROPIC_MISMATCH (human spinal cord lacks DRD3 and has trace DRD2, while non-D2 SREBP2/ROS rescue requires 15-146x higher concentration than human CSF)",
        "prior_art_crowding_level": "MODERATE (UMIN000034954 Ph1/2a completed; K Pharma/Alfresa Japan Ph3 plans; UK EXPERTS-ALS ISRCTN15525855 arm stopped for futility)",
        "evidence_proves_hypothesis": "Penetrates human ALS CSF at 16 mg/d (ROPALS Wk24 17,884 pg/mL = 68.68 nM on MW 260.38, engaging DRD2/3 Ki 2.9-7.2 nM) with exploratory unblinded OLE signal in Morimoto 2023 (PMID:37267913).",
        "evidence_disproves_hypothesis": "ROPALS primary 24-wk blinded ALSFRS-R was null (+1.46, 95% CI -3.15 to 6.07); UK EXPERTS-ALS (ISRCTN15525855, 16 mg/d ER) stopped ropinirole arm Oct 2026 for futility (no blood NfL reduction); DS005_BYE showed FDR-significant survival loss across 15 sALS iPSC-MN lines (-0.688d, 12/15 negative, 1/15 tied at 0.0 d, 2/15 positive [80.0% worsened, 86.7% non-positive], q=0.0209); 68.7 nM CSF is 14.6-145.6x below 1-10 uM D2R-independent potency (PMID:40826812) while 76.9% GI AEs block dose escalation and spinal DRD3 is 0% >=1 CPM.",
        "epistemic_state": "FALSIFIED_CLINICAL", "decision": "DROP",
        "factual_justification": "Blinded 24-week ROPALS ALSFRS-R null (+1.46, 95% CI -3.15 to 6.07) plus Oct 2026 independent DMC futility stop of the 16 mg/d ropinirole arm in UK EXPERTS-ALS (ISRCTN15525855) for failure to lower blood NfL, reinforced by FDR-significant survival harm in 15 human sALS iPSC-MN lines (-0.688d, q=0.0209), absence of spinal DRD3, a 15-146x human CSF exposure deficit (68.7 nM) vs D2R-independent potency (1-10 uM), and BA9 GC-artifact collapse.",
        "discriminating_next_test": "", "supporting_evidence_ids": "EV-B5-017;EV-B5-018;EV-B5-019;EV-B5-020", "updated_at": RUN_TIMESTAMP,
    },
    {
        "carbon_id": "C011", "name": "Furosemide", "track": "A",
        "phase1_batch": "Batch_5_Clinical_Futility_PK_And_Excitability", "reanalysis_state": "ADJUDICATED_VERIFIED",
        "scientific_taste_rating": "VERY_LOW_PK_IMPOSSIBLE_LOOP_DIURETIC",
        "technical_accuracy_of_explore_claim": "VERIFIED_AND_SHARPENED (91-99% albumin binding + OAT3/MRP4 efflux yields >500-5000x CNS deficit vs hNKCC1 IC50, worse than ExploreALS's conservative 25-50x estimate)",
        "causal_vs_reactive_assessment": "COUNTERPRODUCTIVE_TARGET_SELECTIVITY (co-inhibits neuronal chloride extruder KCC2/SLC12A5, which is already downregulated in sALS iPSC-MNs adj p=0.0486 and cervical cord p=0.034)",
        "prior_art_crowding_level": "NONE_IN_ALS_CLINIC (0 ALS trials on CT.gov; absent from Bye 2025 107-drug library)",
        "evidence_proves_hypothesis": "Weakly inhibits human NKCC1/KCC2 in vitro at ~18-25 uM (PMID:29959396) and altered rodent slice rhythms at 100 uM.",
        "evidence_disproves_hypothesis": "OpenFDA NDA016273 confirms 91-99% albumin binding (fup=0.01-0.02 -> Cu,p ~0.05-0.14 uM at 40 mg) and active BBB/choroid OAT3/MRP4 efflux (PMID:28456721) yields Cu,CNS <1-5 nM (>500-5000x below hNKCC1 IC50 ~18-23 uM); oral 40 mg reduces human spinal Renshaw inhibition (PMC4221825); systemic loop diuresis risks hypokalemia/dehydration in ALS.",
        "epistemic_state": "FALSIFIED_PK_SAFETY", "decision": "DROP",
        "factual_justification": "Insurmountable >500-5,000x unbound human CNS exposure deficit (91-99% plasma protein binding in NDA016273 plus active BBB/choroid-plexus organic anion efflux yielding <1-5 nM unbound CNS vs ~18-23 uM human NKCC1 IC50), compounded by non-selective inhibition of already-depleted neuronal KCC2 (SLC12A5 adj p=0.0486), reduced human spinal Renshaw inhibition at 40 mg (PMC4221825), and dose-limiting diuresis/electrolyte depletion.",
        "discriminating_next_test": "", "supporting_evidence_ids": "EV-B5-021;EV-B5-022", "updated_at": RUN_TIMESTAMP,
    },
    {
        "carbon_id": "C012", "name": "Perampanel", "track": "A",
        "phase1_batch": "Batch_5_Clinical_Futility_PK_And_Excitability", "reanalysis_state": "ADJUDICATED_VERIFIED",
        "scientific_taste_rating": "LOW_ON_TARGET_CLINICAL_HARM",
        "technical_accuracy_of_explore_claim": "VERIFIED_ACCURATE (Phase 2 RCT worsening, US trial terminations, FDA psychiatric boxed warning, and DS005_BYE null +0.113d p=0.761 all verified)",
        "causal_vs_reactive_assessment": "DELETERIOUS_SYNAPTIC_SUPPRESSION (blocking residual postsynaptic AMPA transmission accelerates bulbar/motor decline in symptomatic ALS)",
        "prior_art_crowding_level": "EXHAUSTED_FOUR_ALS_TRIALS (NCT03019419 completed negative/harmful; NCT03377309 & NCT03020797 terminated; NCT03793868 TMS PD)",
        "evidence_proves_hypothesis": "Potent CNS-penetrant human AMPA GluA1 antagonist (IC50=243-623 nM, CHEMBL1214124) that confirmed human ALS motor-cortex TMS threshold engagement (NCT03793868, N=22).",
        "evidence_disproves_hypothesis": "Japanese Phase 2 RCT NCT03019419 (N=66, PMID:34191081) showed 8 mg/d significantly WORSENED 48-wk ALSFRS-R decline vs placebo by -8.4 pts (p=0.015, bulbar-driven) with increased SAEs (p=0.0483) and 33% vs 82% completion; NCT03377309 (N=6) halted for adverse events; NCT03020797 (N=12) terminated; DS005_BYE iPSC-MN survival null (+0.113d, p=0.761).",
        "epistemic_state": "FALSIFIED_CLINICAL", "decision": "DROP",
        "factual_justification": "Direct randomized human ALS clinical harm and CNS intolerability at confirmed motor-cortex target engagement: Phase 2 RCT NCT03019419 (N=66, PMID:34191081) demonstrated statistically significant ALSFRS-R worsening at 8 mg/d (-8.4 pts vs placebo, p=0.015), higher SAEs (p=0.0483), and 67% dropout, corroborated by adverse-event termination of NCT03377309, termination of NCT03020797, FDA Boxed Warning (NDA202834), and null sALS iPSC-MN survival (+0.113d, q=0.857).",
        "discriminating_next_test": "", "supporting_evidence_ids": "EV-B5-023;EV-B5-024;EV-B5-025", "updated_at": RUN_TIMESTAMP,
    },
]
