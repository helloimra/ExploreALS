"""Atomic 1-gene/1-drug candidate builder Part B (DN-10..DN-19) programmatically formatted from RUN-P3B-001 outputs."""
from __future__ import annotations

from typing import Any


def make_cand_row(
    did: str, fun: str, gd: str, ctype: str, mod: str, mech: str, cr: str, epi: str, dec: str,
    trl: str, gate_cls: str, basis: str, prior: str, h_str: str, sci_tier: str, just: str, nxt: str, evids: str,
) -> dict[str, str]:
    h_cnt = 0 if h_str == "NONE" else len([x for x in h_str.split(";") if x])
    return {
        "denovo_id": did, "discovery_funnel": fun, "gene_or_drug": gd, "candidate_type": ctype,
        "primary_modality_specific": mod, "mechanism_summary": mech, "causal_vs_reactive_assessment": cr,
        "epistemic_state": epi, "decision": dec, "clinical_readiness_trl": trl,
        "next_gate_experimental_class": gate_cls, "primary_evidence_basis": basis,
        "model_prior_dependency": prior, "unsolved_hurdle_count": str(h_cnt),
        "unsolved_hurdles_structured": h_str, "scientific_actionability_tier": sci_tier,
        "factual_justification": just, "discriminating_next_test": nxt,
        "supporting_denovo_evidence_ids": evids, "analysis_run_id": "RUN-P3B-003",
    }


def build_candidates_dn10_to_dn19(f1234: dict[str, Any]) -> list[dict[str, str]]:
    csf = f1234["funnel3_csf_and_spatial"]["trautwig_deconfounded_dia"]["target_lookup"]
    tmt = f1234["funnel3_csf_and_spatial"]["trautwig_deconfounded_dia"]["set1_tmtpro_n101_anova"]
    gc = f1234["funnel3_csf_and_spatial"]["pineda_ba4_gc_adjusted"]["ba4_exc_by_gene"]
    ed_exc = f1234["funnel3_csf_and_spatial"]["edinburgh_sals_non_c9"]["Excitatory"]

    return [
        make_cand_row(
            "DN-10", "F3_CSF_SPATIAL", "DPP6", "BIOMARKER_CSF",
            "Living-CSF somatodendritic Kv4.2 channel-complex & dendritic-loss pharmacodynamic biomarker panel",
            "Catalytically inactive S9B dipeptidyl-peptidase homolog (PDB 1XFD) assembling with somatodendritic Kv4.2 A-type K+ channels",
            "BIOMARKER_SOMATODENDRITIC_ATTRITION", "ESTABLISHED_BENCHMARK", "RECLASSIFY_BENCHMARK_OR_BIOMARKER",
            "PROTOCOL_COMPANION_NA", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE", "MEASURED_HUMAN_CSF_PROTEOMICS",
            "NONE", "LONGITUDINAL_WITHIN_PATIENT_SLOPE_VALIDATION;SPORADIC_VS_C9_SUBGROUP_EFFECT_SIZE_CALIBRATION",
            "BIOMARKER_BENCHMARK_ONLY",
            f"[MEASURED] #1 downregulated non-ExploreALS CSF protein in Emory DIA ({csf['DPP6']['em_log2fc']:.4f}, q_BH={csf['DPP6']['em_q_bh']:.2e}, n={csf['DPP6']['n_em_total']}), directionally replicated in WashU ({csf['DPP6']['wu_log2fc']:.4f}, Welch p={csf['DPP6']['wu_p']:.4f}, MWU p={csf['DPP6']['wu_mwu_p']:.4f}, 26 ALS vs 6 non-ALS [2 Controls + 4 asymptomatic carriers]) & Spillman synaptosome DIA (-0.4023, p=0.0287), whereas Set 1 TMTpro (N=101) is null for Sporadic vs Control (ANOVA Pr(>F)={tmt['DPP6']['Pr(>F)']:.4f}, Sporadic-Ctrl p={tmt['DPP6']['Sporadic-Control']:.4f}; C9-driven Sporadic-C9 p={tmt['DPP6']['Sporadic-ALS.C9']:.4f}); PDB 1XFD lacks catalytic Ser nucleophile.",
            "Validate longitudinal within-patient CSF DPP6/DPP10 trajectories stratified by C9orf72 vs sALS alongside pNfH and NPTX2.",
            "EV-P3B-012",
        ),
        make_cand_row(
            "DN-11", "F3_CSF_SPATIAL", "DPP10", "BIOMARKER_CSF",
            "Companion living-CSF somatodendritic Kv4 auxiliary subunit pharmacodynamic biomarker",
            "Neuronal Kv4 K+ channel auxiliary subunit paralogous to DPP6; tracks somatodendritic membrane loss in living ALS CSF",
            "BIOMARKER_SOMATODENDRITIC_ATTRITION", "ESTABLISHED_BENCHMARK", "RECLASSIFY_BENCHMARK_OR_BIOMARKER",
            "PROTOCOL_COMPANION_NA", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE", "MEASURED_HUMAN_CSF_PROTEOMICS",
            "NONE", "LONGITUDINAL_WITHIN_PATIENT_SLOPE_VALIDATION;WASHU_SMALL_CONTROL_MWU_SENSITIVITY",
            "BIOMARKER_BENCHMARK_ONLY",
            f"[MEASURED] Passes single-center Emory CSF DIA FDR ({csf['DPP10']['em_log2fc']:.4f}, q_BH={csf['DPP10']['em_q_bh']:.4f}, n={csf['DPP10']['n_em_total']}), WashU Welch t-test ({csf['DPP10']['wu_log2fc']:.4f}, p={csf['DPP10']['wu_p']:.4f}; MWU p={csf['DPP10']['wu_mwu_p']:.4f}, 26 ALS vs 6 non-ALS [2 Controls + 4 asymptomatic carriers]), and nominal full-GC BA4_Exc loss ({gc['DPP10']['gc_adj_beta_sals']:.4f}, p={gc['DPP10']['gc_adj_p']:.4f}, q_BH={gc['DPP10']['gc_adj_q_bh']:.4f}), whereas Set 1 TMTpro (N=101) is null for Sporadic vs Control (ANOVA Pr(>F)={tmt['DPP10']['Pr(>F)']:.4f}, Sporadic-Ctrl p={tmt['DPP10']['Sporadic-Control']:.4f}; C9-driven Sporadic-C9 p={tmt['DPP10']['Sporadic-ALS.C9']:.4f}).",
            "Co-quantify CSF DPP10 with DPP6 by targeted PRM/immunoassay in larger balanced sALS vs healthy control cohorts.",
            "EV-P3B-013",
        ),
        make_cand_row(
            "DN-12", "F3_CSF_SPATIAL", "CFL1", "BIOMARKER_CSF",
            "Living-CSF actin-cofilin rod / cytoskeletal axonal damage biomarker (pan-essentiality blocks therapeutic inhibition)",
            "Cofilin-1 actin-severing protein forming ATP-depleted cofilin-actin rods during motor axon degeneration; released into ALS CSF",
            "REACTIVE_DAMAGE_RELEASE_PAN_ESSENTIAL", "ESTABLISHED_BENCHMARK", "RECLASSIFY_BENCHMARK_OR_BIOMARKER",
            "PROTOCOL_COMPANION_NA", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE", "MEASURED_HUMAN_CSF_PROTEOMICS",
            "NONE", "CSF_CELLULAR_CONTAMINATION_AND_NFL_INCREMENTAL_VALUE",
            "BIOMARKER_BENCHMARK_ONLY",
            f"[MEASURED] Sole upregulated non-ExploreALS CSF protein replicating across Emory DIA (+0.3582, q_BH=0.00764, n={csf['CFL1']['n_em_total']}), WashU DIA (+0.2600, Welch p=0.00235, MWU p={csf['CFL1']['wu_mwu_p']:.4f}), AND Set 1 TMTpro N=101 ANOVA (Pr(>F)={tmt['CFL1']['Pr(>F)']:.3e}, Sporadic-Ctrl p={tmt['CFL1']['Sporadic-Control']:.3e}); DepMap pan-essentiality (p10 Chronos=-1.3534) rules out systemic inhibition.",
            "Evaluate CSF CFL1 incremental prognostic variance orthogonal to pNfH/NfL in longitudinal ALS cohorts while excluding pre-analytical platelet/PBMC lysis.",
            "EV-P3B-014",
        ),
        make_cand_row(
            "DN-13", "F3_CSF_SPATIAL", "MAOB", "GENE_DRUG_AXIS",
            "Selective MAO-B enzymatic inhibition (rasagiline / selegiline class)",
            "Outer-mitochondrial monoamine oxidase B enriched in reactive astrocytes (BA4_Astro ctrl=7.60 log2CPM); Visium surge reflects astrogliosis",
            "REACTIVE_ASTROGLIAL_COMPOSITION_SHIFT", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            f"[MEASURED] Zhang MN Visium (+1.1839, BH=0.00243) & Spillman homogenate (+1.1633, padj=0.0277) reflect reactive astrocyte expansion (glia-free Exc snRNA is low/discordant: Pineda full-GC {gc['MAOB']['gc_adj_beta_sals']:.4f}, q_BH={gc['MAOB']['gc_adj_q_bh']:.4f} vs Edinburgh +{ed_exc['MAOB']['diff_log2cpm']:.4f}, p={ed_exc['MAOB']['p_welch']:.4f}), AND selective MAOB inhibitors failed 4 ALS RCTs across rasagiline (NCT01879241 N=252; NCT01786603 N=80) & selegiline (PMID:9443715 N=133; PMID:8195821 N=111).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-015",
        ),
        make_cand_row(
            "DN-14", "F4_BYE2025_SCREEN", "PMX 205", "DRUG_REPURPOSING",
            "Subcutaneous cyclic hexapeptide C5aR1 complement receptor antagonist (PMX 205)",
            "Allosteric C5aR1 antagonist; nominal Rank #9/107 gain in glia-depleted sALS iPSC-MNs despite upstream human ALS C5 RCT failures",
            "AMBIGUOUS_MICROGLIAL_VS_OFFTARGET_IN_VITRO", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "UPSTREAM_C5_RCT_FUTILITY_MECHANISTIC_DIFFERENTIATION;NEURONAL_C5AR1_KO_TARGET_ENGAGEMENT_CHECK;UNBOUND_HUMAN_CSF_KP_UU_QUANTIFICATION",
            "TIER_3_EXPLORATORY_DISCOVERY",
            "[MEASURED] Top unadopted Bye 2025 hit (#9/107: +1.3055d, p=0.0141, Wilcoxon p=0.0110, q_BH=0.0695) with zero completed C5aR1 ALS efficacy RCTs, BUT upstream human ALS C5 cleavage inhibitors failed Phase 2/3 trials (ravulizumab CHAMPION-ALS NCT04248465 N=382 & zilucoplan HEALEY NCT04436497), glia-free cortical Exc C5AR1 is minimal (2.06 log2CPM), and Bye 2025 glia-free monocultures lack exogenous or microglial complement C5/C5a ligand, making ligand-independent 2.5 uM cyclic-hexapeptide off-target activity the primary null hypothesis pending C5AR1-KO + avacopan target deconvolution.",
            "Execute in vitro target-deconvolution testing of PMX 205 vs orthosteric avacopan in wild-type vs C5AR1-KO human iPSC-MNs (+/- exogenous C5a & microglia, testing the primary null that 2.5 uM rescue in C5/C5a-free monocultures is a ligand-independent cyclic-hexapeptide off-target artifact rather than on-target C5aR1 blockade sparing C5b-9/C5L2), plus unbound human CSF Kp,uu quantification.",
            "EV-P3B-016",
        ),
        make_cand_row(
            "DN-15", "F4_BYE2025_SCREEN", "Lamotrigine", "DRUG_REPURPOSING",
            "Oral voltage-gated Na+ channel blocker / anti-glutamatergic (lamotrigine)",
            "Presynaptic Na+ channel & glutamate-release inhibitor; rescues hyperexcitable iPSC-MNs at 2.5 uM in vitro but failed human ALS RCTs",
            "DOWNSTREAM_EXCITABILITY_CLINICALLY_FUTILE", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            "[MEASURED] Despite Bye 2025 Rank #13/107 (+0.8992d, p=0.0143, q_BH=0.0695), lamotrigine failed two randomized double-blind placebo-controlled ALS trials including high-dose 300 mg/d with verified CSF target exposure (Eisen 1993 PMID:7906190 N=67; Ryberg 2003 PMID:12807386 N=30).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-017",
        ),
        make_cand_row(
            "DN-16", "F4_BYE2025_SCREEN", "Dolutegravir", "DRUG_REPURPOSING",
            "Oral HIV integrase inhibitor / Triumeq fixed-dose antiretroviral regimen in unstratified ALS",
            "HIV-1 retroviral integrase inhibitor (minimal non-LTR LINE-1 activity); 2.5 uM screen exceeds unbound human CSF by 60-250x & Triumeq failed Ph3 LIGHTHOUSE II",
            "UNSTRATIFIED_RETROELEMENT_FUTILITY_AND_CSF_PK_GAP", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_RCT_SUBGROUP",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            "[MEASURED] Phase 3 LIGHTHOUSE II (NCT05193994, N=419, Triumeq: dolutegravir HIV-1 integrase inhibitor [minimal direct non-LTR LINE-1 activity] + abacavir/lamivudine NRTIs vs placebo) was TERMINATED on 2025-06-30 for interim survival futility, while Bye 2025's 2.5 uM dolutegravir concentration (+0.7458d, p=0.0431) is 60-250x above clinical unbound human CSF (~10-40 nM).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-018;EV-P3B-022",
        ),
        make_cand_row(
            "DN-17", "F4_BYE2025_SCREEN", "Acetylcysteine", "DRUG_REPURPOSING",
            "Systemic thiol antioxidant (N-acetylcysteine)",
            "Glutathione precursor & direct thiol ROS scavenger with poor CNS Kp,uu (<<0.05); buffers media ROS at 2.5 uM without modifying ALS survival",
            "IN_VITRO_REDOX_BUFFERING_ARTIFACT", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            "[MEASURED] Bye 2025 Rank #12/107 (+0.9458d, p=0.0201, q_BH=0.0936) reflects extracellular thiol media buffering; polar anionic NAC has poor BBB penetration (Kp,uu<<0.05) and high-dose 50 mg/kg/d SC NAC (~3,500 mg/d) failed Louwerse 1995 PMID:7763202 double-blind survival RCT (N=110: HR=0.74, P=0.31; active 50 mg/d NCT07414212 N=90 is 70x lower dose).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-019",
        ),
        make_cand_row(
            "DN-18", "F4_BYE2025_SCREEN", "Coenzyme Q10", "DRUG_REPURPOSING",
            "High-dose oral mitochondrial ubiquinone antioxidant (Coenzyme Q10)",
            "Mitochondrial electron-transport carrier & lipid antioxidant; marginal Bye 2025 Rank #19/107 gain falsified in Phase II QALS RCT",
            "DOWNSTREAM_REDOX_CLINICALLY_FUTILE", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            "[MEASURED] Bye 2025 Rank #19/107 (+0.7430d, p=0.0495, q_BH=0.1827) failed to translate in the multicenter randomized double-blind placebo-controlled Phase II QALS trial at 2,700 mg/d over 9 months (NCT00243932, Kaufmann 2009 PMID:19743457, N=185: met pre-specified Stage 2 futility, p=0.51).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-020",
        ),
        make_cand_row(
            "DN-19", "F4_BYE2025_SCREEN", "L-Serine", "DRUG_REPURPOSING",
            "High-dose oral L-serine amino-acid supplementation",
            "De novo sphingolipid substrate suppressing non-canonical 1-deoxysphingolipids in HSAN1, whereas SPTLC1/SPTLC2-ALS variants lose ceramide feedback and overproduce canonical C18-C22 sphingolipids (PMID:43025655)",
            "METABOLIC_HYPOTHESIS_MEDIA_CONFOUNDED_UNPROVEN", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "BASAL_MEDIA_400UM_SERINE_CONFOUND_AT_2P5UM;SPTLC1_SPTLC2_ALS_IMPAIRED_CERAMIDE_FEEDBACK_OVERPRODUCTION_HAZARD;NO_PLACEBO_CONTROLLED_ALS_RCT;NON_FDR_SCREEN_BORDERLINE",
            "TIER_3_EXPLORATORY_DISCOVERY",
            "[MEASURED] Oral L-serine (up to 15 g BID) crosses the human ALS BBB and elevates CSF L-serine in Phase 1 (Levine 2017 NCT01835782, PMID:28181924, N=20), while open-label Phase 2 NCT03580616 (N=43) was terminated by the IRB for protocol noncompliance rather than efficacy futility (preserving UNPROVEN_UNTESTED in non-SPT sporadic ALS under Epistemic Asymmetry); however, Bye 2025 Rank #20/107 (+0.7117d, p=0.0419, q_BH=0.1707 at 2.5 uM) shifts ~400 uM basal media L-serine by only +0.625% (<1%, funnel-entry noise), and Ziak et al. 2026 (PMID:43025655, 10.1016/j.jlr.2026.101187) prove SPTLC1/SPTLC2-ALS variants impair ceramide homeostatic feedback to overproduce canonical C18-C22 dihydrosphingolipids/sphingolipids (making L-serine counterproductive in SPT-ALS unlike HSAN1), barring clinical progression prior to genetic exclusion and lipidomic deconvolution.",
            "Mandate prospective SPTLC1/SPTLC2 sequencing exclusion and execute L-serine dose-response deconvolution (0-1,000 uM) in serine-defined non-SPT human sALS iPSC-MN media quantifying paired 1-deoxysphinganine suppression vs canonical C18-C22 dihydrosphingolipid/ceramide accumulation (PMID:43025655) and isotonic osmolyte controls before any clinical re-entry.",
            "EV-P3B-021",
        ),
    ]
