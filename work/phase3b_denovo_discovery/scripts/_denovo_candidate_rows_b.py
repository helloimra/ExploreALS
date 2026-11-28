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
            "Living-CSF somatodendritic Kv4.2 auxiliary subunit attrition candidate marker (pre-validation)",
            "Catalytically inactive S9B dipeptidyl-peptidase homolog (PDB 1XFD 3.00A homodimer: Ser->Asp712 in GKDYGG) assembling with somatodendritic Kv4.2 K+ channels",
            "BIOMARKER_SOMATODENDRITIC_ATTRITION", "ESTABLISHED_BENCHMARK", "RECLASSIFY_BENCHMARK_OR_BIOMARKER",
            "PROTOCOL_COMPANION_NA", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE", "MEASURED_HUMAN_CSF_PROTEOMICS",
            "NONE", "EMORY_MS2_TMTPRO_VS_DIA_PLATFORM_COMPRESSION_PRM_IMMUNOASSAY_GATE;LONGITUDINAL_WITHIN_PATIENT_SLOPE_AND_TRANS_DIAGNOSTIC_FTD_AD_CALIBRATION",
            "BIOMARKER_BENCHMARK_ONLY",
            f"[MEASURED] Top downregulated untargeted CSF protein in Emory DIA ({csf['DPP6']['em_log2fc']:.4f}, q_BH={csf['DPP6']['em_q_bh']:.2e}, n={csf['DPP6']['n_em_total']}; Age+Sex OLS beta=-0.4911, p=3.55e-10; highlighted in Trautwig et al. 2025 PMID:40375307 Fig. 7a), directionally concordant in WashU ({csf['DPP6']['wu_log2fc']:.4f}, Welch p={csf['DPP6']['wu_p']:.4f}, MWU p={csf['DPP6']['wu_mwu_p']:.4f}, 26 ALS vs 6 non-ALS [2 ordinary Controls + 4 asymptomatic carriers; vs 2 ordinary Controls alone -0.150, Welch p=0.637; tissue-bank totals differ unresolvedly between paper Table 2 WashU=26/0 & MGH=0/84 and MOESM1 Sheet 2 WashU=32 (26 ALS code 100 vs 6 comparators code 741) & MGH=78 (all code 701), confounding WashU case/comparator status with code 100 vs 741]) & postmortem C9-FTD frontal cortex synaptosome DIA (-0.4023, p=0.0287, BH-FDR=0.2984, n=20 vs homogenate -0.1099, p=0.4200, PMID:42789089), whereas ~82%-overlapping Emory Set 1 18-plex HCD MS2 TMTpro (N=101, no SPS-MS3) has a null 5-group omnibus ANOVA (Pr(>F)={tmt['DPP6']['Pr(>F)']:.4f}, Sporadic-Ctrl p={tmt['DPP6']['Sporadic-Control']:.4f}; unprotected pairwise Sporadic-C9 p={tmt['DPP6']['Sporadic-ALS.C9']:.4f}, C9-Ctrl diff_inv={tmt['DPP6']['diff Control-ALS.C9_inv']:.4f} p={tmt['DPP6']['Control-ALS.C9']:.4f}); PDB 1XFD (3.00A homodimer, auth_seq_id 127-849, PMID:15476821) substitutes Ser->Asp712 in G710-K711-D712-Y713-G714-G715, gnomAD v4.1 MANE ENST00000377770 LOEUF=0.751 (cardiac Purkinje IVF liability), and candidate-era rs10260404 (PMID:18084291) did not replicate in Project MinE GWAS (PMID:34873335).",
            "Resolve the ~82%-overlapping Emory MS2-TMTpro vs DIA-MS discordance via targeted heavy-isotope PRM-MS on non-glycosylated ectodomain peptides (6 N-glycans/monomer in PDB 1XFD) and validate longitudinal within-patient CSF DPP6/DPP10 slopes alongside Simoa/Ella immunoassay pNfH and NPTX2 (noting trans-diagnostic AD/FTD synaptic depletion, PMID:33087358, PMID:37468915).",
            "EV-P3B-012",
        ),
        make_cand_row(
            "DN-11", "F3_CSF_SPATIAL", "DPP10", "BIOMARKER_CSF",
            "Companion living-CSF somatodendritic Kv4 auxiliary subunit attrition candidate marker (pre-validation)",
            "Catalytically inactive neuronal Kv4 K+ channel auxiliary subunit (canonical UniProt Q8N608 [796 aa]: Ser->Gly651 in GKGYGG, Ala657; isoform Q8N608-3 [800 aa]: Ser->Gly655, Ile651; LOEUF=0.378) tracking somatodendritic loss",
            "BIOMARKER_SOMATODENDRITIC_ATTRITION", "ESTABLISHED_BENCHMARK", "RECLASSIFY_BENCHMARK_OR_BIOMARKER",
            "PROTOCOL_COMPANION_NA", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE", "MEASURED_HUMAN_CSF_PROTEOMICS",
            "NONE", "EMORY_MS2_TMTPRO_VS_DIA_PLATFORM_COMPRESSION_AND_WASHU_MWU_SENSITIVITY;LONGITUDINAL_WITHIN_PATIENT_SLOPE_AND_TRANS_DIAGNOSTIC_FTD_AD_CALIBRATION",
            "BIOMARKER_BENCHMARK_ONLY",
            f"[MEASURED] Passes single-center Emory CSF DIA FDR ({csf['DPP10']['em_log2fc']:.4f}, q_BH={csf['DPP10']['em_q_bh']:.4f}, n={csf['DPP10']['n_em_total']}; Age+Sex OLS beta=-0.2470, p=0.00617, PMID:40375307), with nominal WashU Welch separation ({csf['DPP10']['wu_log2fc']:.4f}, p={csf['DPP10']['wu_p']:.4f}, but non-parametric MWU p={csf['DPP10']['wu_mwu_p']:.4f} NS across 26 ALS code 100 vs 6 non-ALS code 741 [2 ordinary Controls + 4 asymptomatic carriers; vs 2 ordinary Controls alone -0.428, Welch p=0.118; unresolved Table 2 26/84 vs MOESM1 32/78 bank count]), sub-FDR postmortem BA4_Exc snRNA-seq mRNA reduction ({gc['DPP10']['gc_adj_beta_sals']:.4f}, p={gc['DPP10']['gc_adj_p']:.4f}, q_BH={gc['DPP10']['gc_adj_q_bh']:.4f}, PMID:38521060), and C9-FTD Spillman MOESM1 isoform Q8N608-3 (row 1684) synaptosome DIA trend (-0.3305, p=0.0699, BH-FDR=0.3791 vs Q8N608-2 row 3579 BH-FDR=0.560 & canonical Q8N608 row 4979 BH-FDR=0.680, PMID:42789089), whereas ~82%-overlapping Emory Set 1 MS2 TMTpro (N=101) has a null 5-group omnibus ANOVA (Pr(>F)={tmt['DPP10']['Pr(>F)']:.4f}, Sporadic-Ctrl p={tmt['DPP10']['Sporadic-Control']:.4f}; unprotected pairwise Sporadic-C9 p={tmt['DPP10']['Sporadic-ALS.C9']:.4f}, C9-Ctrl diff_inv={tmt['DPP10']['diff Control-ALS.C9_inv']:.4f} p={tmt['DPP10']['Control-ALS.C9']:.4f}); canonical UniProt Q8N608 (796 aa) substitutes Ser->Gly651 in GKGYGG (Ala657; 800-aa isoform Q8N608-3 places Gly655 in GKGYGG, Ile651) with strong LoF intolerance (ENST00000410059 LOEUF=0.378, pLI=1.000).",
            "Co-quantify CSF DPP10 with DPP6 by targeted heavy-isotope PRM-MS in balanced longitudinal sALS and C9orf72-ALS vs healthy/FTD/mimic cohorts alongside Simoa/Ella immunoassay pNfH.",
            "EV-P3B-013",
        ),
        make_cand_row(
            "DN-12", "F3_CSF_SPATIAL", "CFL1", "BIOMARKER_CSF",
            "Living-CSF pan-Cofilin-1 cytoskeletal injury candidate marker (pan-essentiality & SALS p-Ser3-CFL1 inactivation block inhibition)",
            "Actin-severing Cofilin-1 (UniProt P23528); bottom-up tryptic CSF MS quantifies unmodified pan-CFL1 release while postmortem sALS spinal MNs exhibit Ser3 hyperphosphorylation/inactivation and experimental models link LIMK1-driven pSer3-CFL1 to TDP-43 aggregation (PMID:41804798, opposing dephospho-cofilin rods)",
            "REACTIVE_DAMAGE_RELEASE_PAN_ESSENTIAL", "ESTABLISHED_BENCHMARK", "RECLASSIFY_BENCHMARK_OR_BIOMARKER",
            "PROTOCOL_COMPANION_NA", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE", "MEASURED_HUMAN_CSF_PROTEOMICS",
            "NONE", "PREANALYTICAL_RBC_PLATELET_WBC_LYSIS_QC_GATE;PSER3_VS_DEPHOSPHO_CFL1_ISOFORM_SELECTIVE_ASSAY_GATE;INCREMENTAL_PROGNOSTIC_VARIANCE_BEYOND_IMMUNOASSAY_NFL_PNFH",
            "BIOMARKER_BENCHMARK_ONLY",
            f"[MEASURED] Sole upregulated untargeted CSF protein replicating across Emory DIA (+0.3582, q_BH=0.00764, n={csf['CFL1']['n_em_total']}; surviving Age+Sex+HBB+CA1+PRDX2 hemolysis OLS beta=+0.3392, p=2.47e-4, n=91 & PFN1+TLN1+ACTB platelet OLS beta=+0.2946, p=2.54e-4, n=92) and WashU DIA (+0.2600, Welch p=0.00235, MWU p={csf['CFL1']['wu_mwu_p']:.4f}, 26 ALS code 100 vs 6 comparators code 741 [2 ordinary Ctrl + 4 asym; vs 2 ordinary Controls alone +0.188, Welch p=0.0096, MWU p=0.429]; 4-center DIA ANOVA sALS-Ctrl diff=+0.2503, p=0.00242), with cross-platform analytical corroboration in ~82%-overlapping Emory Set 1 TMTpro N=101 ANOVA (Pr(>F)={tmt['CFL1']['Pr(>F)']:.3e}, Sporadic-Ctrl diff=+{tmt['CFL1']['diff Sporadic-Control']:.4f}, p={tmt['CFL1']['Sporadic-Control']:.3e}, PMID:40375307); Jagaraj et al. 2026 (Brain 149(11):3999-4017, PMID:41804798; cf. C9orf72 PMID:27723745 — opposite phospho-sign to dephospho-cofilin rods) observed elevated pSer3-CFL1 in postmortem human sALS spinal MNs and demonstrated in experimental cellular/model perturbations that LIMK1-driven Ser3 hyperphosphorylation (inactivation) promotes TDP-43 aggregation, whereas direct CFL1 inhibition is barred by pan-essentiality (DepMap p10 Chronos=-1.3534; gnomAD v4.1 MANE ENST00000308162 LOEUF=0.408, pLI=0.990, mis_z=3.38) and upstream ROCK1/2 blockade (Fasudil, which de-represses CFL1) showed no clinical separation in 20-d Phase 2a ROCK-ALS (NCT03792490, N=120, PMID:39424560) or Bye 2025 (p=0.209).",
            "Enforce atraumatic-LP erythrocyte/platelet contamination QC (HBB/CA1/PRDX2/PF4, PMID:31566909), develop phosphatase-stabilized isoform-selective pSer3-CFL1 vs total CFL1 targeted PRM/Simoa assays (resolving muscle CFL2/DSTN; PMID:41804798), and test incremental longitudinal variance orthogonal to immunoassay NfL and pNfH.",
            "EV-P3B-014;EV-P3B-029",
        ),
        make_cand_row(
            "DN-13", "F3_CSF_SPATIAL", "MAOB", "GENE_DRUG_AXIS",
            "Selective MAO-B enzymatic inhibition (rasagiline / selegiline class)",
            "Outer-mitochondrial monoamine oxidase B enriched in reactive astrocytes (BA4_Astro ctrl=7.60 log2CPM); Visium/homogenate surge is consistent with astrogliosis & irreversible MAO-B blockade failed 3 DB-RCTs + 1 open-label trial",
            "REACTIVE_ASTROGLIAL_COMPOSITION_SHIFT", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            f"[MEASURED] Zhang MN Visium (+1.1839, spot-level MAST BH=0.00243 across N=18 donors, PMID:42135512) & Spillman C9-FTD frontal cortex homogenate DIA (+1.1633, padj=0.0277, n=19, PMID:42789089) are consistent with reactive astrocyte expansion alongside any per-cell glial regulation (glia-free Exc snRNA is low/discordant: Pineda full-GC {gc['MAOB']['gc_adj_beta_sals']:.4f}, q_BH={gc['MAOB']['gc_adj_q_bh']:.4f} vs Edinburgh +{ed_exc['MAOB']['diff_log2cpm']:.4f}, p={ed_exc['MAOB']['p_welch']:.4f}), AND selective irreversible MAOB inhibitors at [11C]-L-deprenyl PET-measured >85-90% human brain saturation in N=3 healthy volunteers (PMID:16204711) failed 3 double-blind placebo-controlled ALS RCTs — RAS-ALS rasagiline 1 mg/d (NCT01879241, PMID:29934198, N=252 rand / N=251 ITT [126 vs 125]: 18-mo survival HR=0.91, p=0.31; null longitudinal NfL PMID:37975796 & null MAOB SNP interaction PMID:38240416), Statland 2019 rasagiline 2 mg/d (NCT01786603, PMID:30192007, N=80 3:1), and Lange 1998 selegiline 10 mg/d (PMID:9443715, N=133) — plus 1 open-label unblinded selegiline trial (Mazzini 1994 PMID:8195821, N=111); scoped strictly to MAOB enzymatic inhibition (distinct from homeostatic astrocyte-Treg signaling).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-015;EV-P3B-030",
        ),
        make_cand_row(
            "DN-14", "F4_BYE2025_SCREEN", "PMX 205", "DRUG_REPURPOSING",
            "Subcutaneous cyclic hexapeptide intrahelical orthosteric Site-2 C5aR1 complement receptor antagonist (PMX 205 / ALS-205, CID:6918845)",
            "Intrahelical orthosteric Site-2 C5aR1 cyclic hexapeptide antagonist ([Ligand-Analog Inferred from PMX-53 in PDB 6C1R, PMID:29867214], free-base MW 839.04 Da); sub-FDR Rank #9/107 gain in monocultured sALS iPSC-MNs without exogenous C5/C5a despite upstream C5 RCT futility",
            "AMBIGUOUS_MICROGLIAL_VS_OFFTARGET_IN_VITRO", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "SUB_FDR_COMPLEMENT_FREE_MONOCULTURE_OFFTARGET_NULL_CHECK;UPSTREAM_C5_RCT_FUTILITY_MECHANISTIC_DIFFERENTIATION;NEURONAL_C5AR1_KO_TARGET_ENGAGEMENT_CHECK;UNBOUND_HUMAN_CSF_KP_UU_QUANTIFICATION",
            "TIER_4_PARKED_INSUFFICIENT_EVIDENCE",
            "[MEASURED] Sub-FDR Bye 2025 screen survival delta (#9/107: +1.3055d, paired t p=0.0141, Wilcoxon p=0.0110, q_BH=0.0695, n=16) for cyclic hexapeptide PMX 205 (ALS-205, CID:6918845, free-base MW 839.04 Da; originated in hSOD1-G93A mice by Lee, Woodruff et al. at Univ. of Queensland PMID:28128456; Alsonex completed N=8 ALS open-label single-dose Phase 1b subcutaneous safety/PK ACTRN12622000927729, with preliminary paired n=8 ALS blood ex vivo C5a-challenge inhibition reported by Fung, Lee & Woodruff 2025 DOI:10.1016/j.imbio.2025.153003, unbound human CSF Kp,uu unpublished, and zero completed randomized ALS efficacy RCTs), BUT upstream human ALS C5 cleavage inhibitors failed Phase 2/3 efficacy trials (ravulizumab CHAMPION-ALS NCT04248465 N=382 PMID:37695623 & zilucoplan HEALEY NCT04436497 N=162 DRR=1.08 PMID:39960672), glia-free cortical Exc C5AR1 RNA is low and flat (Edinburgh Exc 2.10 ALS vs 2.06 Ctrl log2CPM, p=0.893, n=34 vs Microglia 4.35 vs 4.54, n=33), and Bye 2025 monocultures lack exogenous C5/C5a or microglia (endogenous/media C5/C5a unmeasured), making ligand-independent 2.5 uM cyclic-hexapeptide off-target activity a primary alternative pending C5AR1-KO + extrahelical allosteric avacopan (CHEMBL3989871) vs intrahelical orthosteric Site-2 PMX 205 ([Ligand-Analog Inferred from PMX-53 in PDB 6C1R, PMID:29867214]) deconvolution.",
            "Execute in vitro target-deconvolution testing of intrahelical orthosteric Site-2 PMX 205 (CID:6918845; [Ligand-Analog Inferred from PMX-53 in PDB 6C1R, PMID:29867214]) vs extrahelical allosteric TM3-5 antagonist avacopan (CHEMBL3989871) in wild-type vs C5AR1-KO human iPSC-MNs (+/- exogenous C5a & microglia, measuring basal media C5/C5a to test whether sub-FDR 2.5 uM monoculture rescue is ligand-independent off-target activity vs on-target C5aR1 blockade sparing C5b-9/C5L2), alongside peer-reviewed unbound human ALS CSF Kp,uu quantification beyond single-dose ACTRN12622000927729 / ex vivo blood PD (DOI:10.1016/j.imbio.2025.153003).",
            "EV-P3B-016;EV-P3B-028",
        ),
        make_cand_row(
            "DN-15", "F4_BYE2025_SCREEN", "Lamotrigine", "DRUG_REPURPOSING",
            "Oral voltage-gated Na+ channel blocker / anti-glutamatergic (lamotrigine 100-300 mg/d)",
            "Presynaptic Na+ pore blocker; sub-FDR 2.5 uM iPSC-MN gain superseded by null human ALS CSF amino-acid & clinical testing at 300 mg/d (Ryberg 2003 N=30) + 100 mg/d Eisen 1993 (N=67), while mexiletine (cramps reduced) & flecainide (secondary NI p=0.02) did not slow ALSFRS-R decline",
            "DOWNSTREAM_EXCITABILITY_CLINICALLY_FUTILE", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            "[MEASURED] Bye 2025 Rank #13/107 (+0.8992d, p=0.0143, q_BH=0.0695, n=16) missed BH-FDR, and although Eisen et al. 1993 PMID:7906190 (100 mg/d, N=67, D=12 deaths) was individually underpowered for survival, high-dose Ryberg et al. 2003 PMID:12807386 (300 mg/d paired double-blind crossover across 30 completers with serial LPs measuring CSF lamotrigine, glutamate, aspartate, and BCAAs; exact randomized N and numerical CSF concentration table require paywalled full text) found no significant human CNS glutamate/aspartate/BCAA reduction or clinical benefit across 4 scales, alongside comparator ALS trials in which neither mexiletine (Weiss et al. 2016 PMID:26911633, N=60 12-wk trial: reduced muscle cramp frequency p=0.047/0.002 and intensity p=0.005 without slowing ALSFRS-R or SVC decline) nor flecainide (FANS Park et al. 2015 PMID:26844270 / PMC4703720, N=54 32-wk trial: did not slow primary ALSFRS-R slope [p=0.50] despite less decline in a secondary neurophysiological index [p=0.02]) demonstrated statistically significant slowing of ALSFRS-R decline, plus FDA SJS/TEN Boxed Warning + cardiac NaV1.5 arrhythmia warnings (scoped strictly to the named drugs, doses, and endpoints rather than asserting class-wide oral Na+ channel inhibition futility; distinct from KCNQ2 splice rescue, selective NaV1.6 modulation, or background riluzole).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-017;EV-P3B-031",
        ),
        make_cand_row(
            "DN-16", "F4_BYE2025_SCREEN", "Dolutegravir", "DRUG_REPURPOSING",
            "Oral HIV-1 integrase inhibitor / Triumeq fixed-dose antiretroviral regimen in unstratified ALS",
            "Fixed-dose 3-drug Triumeq failed survival in Phase 3 LIGHTHOUSE II (does not isolate dolutegravir alone); single-agent dolutegravir faces a 58-263x HIV total CSF PK gap vs 2.5 uM & zero LINE-1 integrase",
            "UNSTRATIFIED_RETROELEMENT_FUTILITY_AND_CSF_PK_GAP", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_RCT_SUBGROUP",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            "[MEASURED] Phase 3 LIGHTHOUSE II (NCT05193994, N=419, 2:1 fixed-dose three-drug Triumeq: dolutegravir 50 mg + abacavir 600 mg + lamivudine 300 mg vs placebo in unstratified ALS; following open-label Phase 2a LIGHTHOUSE NCT02868580 N=40 PMID:31284774) stopped early for interim survival futility (sponsor announcement 2025-04-05; registry completion 2025-06-30; clinical conclusion applies to the fixed-dose Triumeq regimen and does not isolate dolutegravir's individual clinical effect), while single-agent dolutegravir is deprioritized pharmacologically because Bye 2025's sub-FDR 2.5 uM readout (+0.7458d, p=0.0431, q_BH=0.1707) exceeds HIV-cohort Week-16 total human CSF at 50 mg QD (4-18 ng/mL = 9.5-42.9 nM, median 13 ng/mL = 31.0 nM total CSF compared against unbound plasma; Letendre et al. 2014 PMID:24944232) by 58-263x and autonomous human LINE-1 encodes zero integrase (uses ORF2p TPRT; preserving nanomolar LINE-1 RT inhibition in ~13.4% cortical ALS-TE under EALS-033 Censavudine).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-018;EV-P3B-022",
        ),
        make_cand_row(
            "DN-17", "F4_BYE2025_SCREEN", "Acetylcysteine", "DRUG_REPURPOSING",
            "High-dose CNS-penetrant N-acetylcysteine regimen (>=50-70 mg/kg/d parenteral or high-dose oral; distinct from low-dose <=600 mg/d oral NAC)",
            "Glutathione precursor & thiol redox modulator; underpowered Louwerse 1995 SC RCT (HR=0.74 [0.41-1.33]) & short-term PD CSF PK (~9.26 uM at 70 mg/kg BID, PMID:25765302) leave chronic ALS CNS GSH target engagement unproven",
            "AMBIGUOUS_EXTRACELLULAR_BUFFERING_VS_GSH_RESTORATION", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "SUB_FDR_SCREEN_EXTRACELLULAR_MEDIA_REDOX_CONFIRMATORY_CHECK;HIGH_DOSE_HUMAN_ALS_CSF_GSH_TARGET_ENGAGEMENT;LOW_DOSE_600MG_ORAL_FIRST_PASS_DEACETYLATION_GAP",
            "TIER_4_PARKED_INSUFFICIENT_EVIDENCE",
            "[MEASURED] Bye 2025 Rank #12/107 (+0.9458d, p=0.0201, q_BH=0.0936, n=15) did not survive BH-FDR and may reflect extracellular thiol media buffering, YET neither clinical futility nor insurmountable CNS PK deficit is established: Louwerse et al. 1995 PMID:7763202 (50 mg/kg/d SC NAC [~3,500 mg/d at 70 kg], N=110) was an underpowered trial whose survival CI includes substantial benefit alongside opposing onset strata (overall HR=0.74 [95% CI 0.41-1.33], p=0.31; limb-onset n=81 HR=0.50 [0.24-1.04], p=0.06 vs bulbar-onset n=29 HR=1.66 [0.56-4.99]), and Katz et al. 2015 PMID:25765302 demonstrated in N=12 Parkinson participants over 2 days (LP 90 min post-dose) that 70 mg/kg oral NAC BID achieves 9.26 +/- 1.62 uM human CSF NAC (p<0.001) without acute DLT, whereas recruiting NCT07414212 (N=90) administers 600 mg/d oral effervescent NAC (5.83x lower nominal daily mass than 3,500 mg/d SC across ~6-10% oral bioavailability; cf. lipophilic NACA/AD4 prodrugs and ALSUntangled #82 review PMID:41777232) co-formulated with 1,800 mg/d EH301 (1,500 mg nicotinamide riboside + 300 mg pterostilbene) + 100 mg riluzole, precluding single-agent NAC attribution.",
            "Separate extracellular thiol media-oxidation buffering (using Catalase/GSH-ethyl-ester/GCLC-inhibition controls) from intracellular neuronal glutathione rescue in human sALS iPSC-MNs, and require paired human ALS CSF free-NAC and 7T/3T MRS cortical/cervical GSH target-engagement proof at high-dose (>=50-70 mg/kg) dosing before efficacy testing.",
            "EV-P3B-019",
        ),
        make_cand_row(
            "DN-18", "F4_BYE2025_SCREEN", "Coenzyme Q10", "DRUG_REPURPOSING",
            "High-dose oral mitochondrial ubiquinone antioxidant (Coenzyme Q10 1,800-2,700 mg/d)",
            "Mitochondrial electron-transport carrier & lipid antioxidant; sub-FDR Bye 2025 Rank #19/107 colloid noise with Phase II QALS futility & oral GI absorption ceiling",
            "DOWNSTREAM_REDOX_CLINICALLY_FUTILE", "FALSIFIED_CLINICAL", "DROP",
            "PROTOCOL_COMPANION_NA", "NOT_APPLICABLE_FALSIFIED", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "NONE",
            "DROPPED_FALSIFIED_EXCLUDED",
            "[MEASURED] Bye 2025 Rank #19/107 (+0.7430d, p=0.0495, q_BH=0.1827, n=16; cLogP ~19.4 colloid dispersion in lipoprotein-free media) failed BH-FDR, and in the multicenter randomized double-blind placebo-controlled Phase II QALS trial at 2,700 mg/d over 9 months (NCT00243932, Kaufmann et al. 2009 Ann Neurol PMID:19743457, PMC2854625 Table 3, N=185 total [Stage 2 n=75 at 2,700 mg/d vs n=75 placebo]), Stage 2 primary bias-adjusted one-sided futility testing (alpha=0.10) gave p=0.14 (mean decline 8.80 [SD 7.34] vs 9.44 [SD 8.82], 1-sided 90% CI <0.22) only because 1 Month-9 CoQ10 death vs 5 placebo deaths were imputed as total Month-9 ALSFRS-R=0 (large decline), whereas prespecified death-score=16 sensitivity crossed formal futility (8.52 vs 8.37, p=0.025 < 0.10; 13/17 death scores 4-16 futile; linear slope p=0.097), secondary endpoints (FVC, QoL, fatigue) were null, and oral GI absorption saturated at ~7-9 uM between 1,800 and 2,700 mg/d (Table 2; Ferrante et al. 2005 PMID:16344537; scoped to oral ubiquinone/unstratified ROS scavenging, distinct from SARM1 NAD+ preservation or high-dose CNS-GSH NAC).",
            "NONE_FALSIFIED_CLINICAL",
            "EV-P3B-020;EV-P3B-032",
        ),
        make_cand_row(
            "DN-19", "F4_BYE2025_SCREEN", "L-Serine", "DRUG_REPURPOSING",
            "High-dose oral L-serine amino-acid supplementation (15 g BID = 30 g/d) with proposed prospective SPTLC1/SPTLC2 genetic & sphingolipid screening",
            "Serine palmitoyltransferase substrate; fixed 2.5 uM library addition shifts ~400 uM basal media serine by +0.625% (survival +0.7117d, p=0.0419, q_BH=0.1707), leaving 30 g/d dosing untested in low-serine media while variant-specific SPTLC1/2-ALS ceramide risk motivates screening",
            "UNPROVEN_SERINE_HYPOTHESIS_WITH_SPT_VARIANT_SAFEGUARD", "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
            "TRL_4_ACTIVE_PH1_CLASS_OR_NCE", "TARGETED_PRECLINICAL_VALIDATION_GATE", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN",
            "NONE", "SERINE_DEPLETED_DOSE_RESPONSE_AND_1DEOXYSPL_QUANTIFICATION;ZERO_COMPLETED_RANDOMIZED_PLACEBO_CONTROLLED_SALS_TRIALS;PROSPECTIVE_SPTLC1_SPTLC2_GENETIC_AND_SPHINGOLIPID_SCREENING",
            "TIER_4_PARKED_INSUFFICIENT_EVIDENCE",
            "[MEASURED] Bye 2025 2.5 uM survival delta (+0.7117d, Rank #20/107, nominal p=0.04190, q_BH=0.17067 across 16 sALS lines) reflects a fixed-library-concentration endpoint mismatch where adding 2.5 uM increases ~400 uM basal BrainPhys/DMEM-F12 media L-serine concentration by only +0.625% (leaving clinical 15 g BID = 30 g/d systemic exposure untested in physiological low-serine media without proving clinical underdosing); zero concurrent-placebo-controlled sALS efficacy trials have completed (Phase 1 NCT01835782 N=20 Levine et al. 2017 PMID:27589995 — motivated historically by Cox/Dunlop cyanobacterial BMAA seryl-tRNA misincorporation alongside HSAN1 SPT 1-deoxysphingolipid suppression — was randomized and double-blind across 4 dose levels [0.5, 2.5, 7.5, 15 g BID] compared against matched historical placebo controls with no concurrent placebo arm; single-arm Phase 2 NCT03580616 N=43 terminated for IRB noncompliance), while human ALS genetics motivates a proposed genetic/lipid safeguard: rare ALS-linked SPTLC1/SPTLC2 GoF variants (sporadic prevalence rare and cohort-dependent) disrupt ORMDL ceramide feedback and overproduce canonical C18-C22 dihydrosphingolipids/ceramides (variant-specific biochemical risk distinct from HSAN1 1-deoxysphingolipid variants; Mohassel et al. 2021 PMID:34059824; Ziak et al. 2026 PMID:43025655, 10.1016/j.jlr.2026.101187; targeted by intrathecal SPTLC1 ASO LTX-002 NCT07660614).",
            "Quantify 1-deoxysphingolipid vs canonical C18-C22 ceramide flux and dose-response survival across physiological CSF-like low-serine (~25-40 uM) human sALS iPSC-MN media (0-1,000 uM L-serine), and incorporate prospective SPTLC1/SPTLC2 sequencing + plasma sphingolipid profiling as a safety safeguard before any concurrent-placebo-controlled sporadic ALS trial.",
            "EV-P3B-021",
        ),
    ]
