"""Compile publication-grade Summary-of-Findings (SoF) prose for all 59 CarbonALS candidates from frozen registries."""
from __future__ import annotations

import re

from _candidate_contrasts_b import build_edges_and_lenses
from _candidate_hypotheses import CANDIDATE_HYPOTHESES
from carbon_als.accessions import legacy_to_accession, translate_legacy_tokens_in_prose

CAUSAL_MAP: dict[str, str] = {
    "AMBIGUOUS_ISOFORM_DEPENDENT": "Opposing Isoform Functions (Secreted Decoy sST2 vs. Membrane ST2L)",
    "AMBIGUOUS_MICROGLIAL_VS_OFFTARGET_IN_VITRO": "Ambiguous Glial vs. Off-Target In Vitro Signal",
    "AMBIGUOUS_PROAPOPTOTIC_DENDRITIC_VS_TROPHIC_NUCLEAR_GAIN": "Opposing Dendritic (Pro-Apoptotic) vs. Nuclear (Trophic) Roles",
    "AMBIGUOUS_SYNAPTIC_ATP_LOSS_VS_PPP_REDOX_SHUNT": "Dual Synaptic Glycolysis vs. PPP Redox Trade-Off",
    "BIOMARKER_GATED_TREG_MODULATION_UNPROVEN_PHASE3": "Biomarker-Gated Treg Immunomodulation",
    "BIOMARKER_SOMATODENDRITIC_ATTRITION": "Reactive Somatodendritic Attrition Biomarker",
    "BIPHASIC_STAGE_DEPENDENT": "Biphasic Disease-Stage Dependent",
    "CAUSAL_AXONAL_MAINTENANCE_LOSS": "Causal Axonal Maintenance Loss",
    "CAUSAL_EXCITABILITY_MODULATOR_PARTIAL_ENGAGEMENT": "Intrinsic Motor Excitability Modulator",
    "CAUSAL_GENETIC_AND_MECHANISTIC_DRIVER": "Genetically Supported Causal Driver",
    "OPPOSITE_SIGN_MN_EQTL_GWAS_OVERLAP_VS_MICROGLIAL_COLOCALIZATION": "Opposite-Direction MN eQTL–GWAS Overlap vs. Microglial Colocalization (Treatment Direction Open)",
    "CAUSAL_RARE_CODING_SNARE_PRENYL_SWITCH_DEFECT": "Rare-Coding Longin R-SNARE Prenyl-Switch Defect",
    "AMBIGUOUS_SYNAPTIC_OPSONIN_VS_PROTECTIVE_CBOUTON_HOMEOSTASIS": "Synaptic C1q Opsonin vs. Protective C-Bouton Balance",
    "CAUSAL_LOSS_OF_FUNCTION": "Causal TDP-43 Loss-of-Function Effector",
    "CAUSAL_NEURONAL_SYNAPTIC_LOSS_WITH_PSTAT3_DUALITY": "Causal Synaptic Loss (Dual Nuclear pSTAT3 Role)",
    "CAUSAL_RNA_PROCESSING_LOSS": "Causal Neuronal Splicing-Factor Loss",
    "CAUSAL_SYNAPTIC_LOSS_CORTICAL_SELECTIVE": "Cortical-Weighted Postsynaptic Scaffold Loss",
    "CAUSAL_SYNAPTIC_LOSS_OF_FUNCTION": "Causal Synaptic Isoform Loss of Function",
    "CAUSAL_TRAFFICKING_LOSS_OF_FUNCTION": "Causal ER-to-Golgi Trafficking Loss",
    "CAUSAL_WALLERIAN_AXON_EXECUTIONER": "Causal Wallerian Axonolysis Executioner",
    "COUNTERPRODUCTIVE_TARGET_SELECTIVITY": "Counterproductive Isoform / Receptor Selectivity",
    "DELETERIOUS_SYNAPTIC_SUPPRESSION": "Deleterious Synaptic Transmission Suppression",
    "DELETERIOUS_HIGH_DOSE_PERAMPANEL_SIGNAL": "High-Dose 8 mg/d Perampanel Functional Worsening Signal",
    "DOWNSTREAM_CAUSAL_EFFECTOR_OF_AXONOPATHY": "Downstream Causal Effector of Axonopathy",
    "DOWNSTREAM_EXCITABILITY_CLINICALLY_FUTILE": "Tested Oral Lamotrigine Regimens Null in Human ALS Trials",
    "DOWNSTREAM_EXCITOTOXIC_HYPOTHESIS_REFUTED_IN_HUMANS": "Tested Oral Memantine Regimens Null in Human ALS RCTs",
    "DOWNSTREAM_REDOX_CLINICALLY_FUTILE": "Downstream Redox Buffering (Clinically Futile)",
    "DUAL_NEURONAL_TDP43_JAK2_APA_AND_SUBTYPE_GLIAL_INFLAMMATION": "Dual Neuronal JAK2 APA vs. Glial JAK1 Selectivity Trade-Off",
    "EARLY_WINDOW_HOMOCYSTEINE_METHYLATION_RESCUE": "Early-Window (<=12m Trial) Methylation SOC Benchmark (Japan MHLW)",
    "ENDOLYSOSOMAL_POLYGP_CLEARANCE_VS_CONTINUOUS_VACUOLATION_TOXICITY": "Endolysosomal Clearance vs. Continuous Vacuolation Toxicity",
    "HYPOTHESIS_REFUTED_IN_HUMANS": "Refuted in Powered Human ALS RCTs",
    "IATROGENIC_ANTAGONISM_OF_ESSENTIAL_SNARE_PRENYLATION": "Predicted Antagonism of Essential SNARE Prenylation",
    "AMBIGUOUS_EXTRACELLULAR_BUFFERING_VS_GSH_RESTORATION": "Extracellular Media Thiol Buffering vs. High-Dose CNS GSH Rescue",
    "UNPROVEN_DEOXYSPL_CLEARANCE_WITH_MONOGENIC_SPT_CONTRAINDICATION": "Unproven 1-Deoxysphingolipid Hypothesis (Monogenic SPTLC1/2 Contraindicated)",
    "UNPROVEN_SERINE_HYPOTHESIS_WITH_SPT_VARIANT_SAFEGUARD": "Unproven 1-Deoxysphingolipid Hypothesis (SPTLC1/2 Variant Safeguard Proposed)",
    "IN_VITRO_REDOX_BUFFERING_ARTIFACT": "Extracellular Media Thiol-Buffering Artifact",
    "IN_VITRO_BASAL_MEDIA_NOISE_AND_SPT_WRONG_SIGN": "In Vitro Basal Media Noise & Opposing SPTLC1/2 Gain-of-Function Genetics",
    "SPLIT_BY_SUBNODE": "Sub-Node Split (C3/C4B Excluded · CNS C1q Exploratory)",
    "METABOLIC_HYPOTHESIS_MEDIA_CONFOUNDED_UNPROVEN": "Media-Confounded Serine Metabolic Hypothesis",
    "MICROMOLAR_CAD_PHOSPHOLIPIDOSIS_ARTIFACT": "Micromolar Cationic-Amphiphilic Phospholipidosis Artifact",
    "UNTESTED_MICROMOLAR_CAD_PHOSPHOLIPIDOSIS_HYPOTHESIS": "Untested Micromolar Cationic-Amphiphilic Phospholipidosis Hypothesis",
    "NON_CAUSAL_PLEIOTROPIC_MISMATCH": "Non-Causal Pleiotropic Target Mismatch",
    "NON_CAUSAL_RODENT_PROMOTER_ARTIFACT": "Unvalidated In Vivo EAAT2 Induction & Undetected ALS SLC1A2 mRNA Deficit",
    "OFF_TARGET_HIGH_CONC_SCREEN_HIT": "High-Concentration Off-Target Screen Hit",
    "OFF_TARGET_MONOAMINERGIC_SEDATION_WITH_CLASS_ISR_FAILURE": "Off-Target 5-HT2A / α1-Adrenergic Sedation & Negative eIF2B Activator Outcomes",
    "PERIPHERAL_LYMPHOID_IMPDH_BLOCKER": "Peripheral Lymphoid IMPDH Immunosuppressant",
    "POTENTIAL_CAUSAL_PROTEOSTASIS_LOSS": "Mendelian-Supported Neuronal Chaperone Loss",
    "REACTIVE_ASTROGLIAL_COMPOSITION_SHIFT": "Reactive Astroglial Cell-Fraction Shift",
    "REACTIVE_BIOMARKER_AND_COMPENSATORY_PROTECTIVE": "Compensatory Glial Clearance & Fluid Staging Biomarker",
    "REACTIVE_DAMAGE_RELEASE_PAN_ESSENTIAL": "Pan-Essential Cytoskeletal Release Biomarker",
    "REACTIVE_MICROGLIAL_PROLIFERATION_MARKER": "Reactive Microglial Proliferation Marker",
    "REFUTED_PPP1R15A_BINDING_UM_POLYPHARMACOLOGY_UNREACHABLE_IN_HUMANS": "Refuted PPP1R15A Binding & Unreachable CNS Exposure",
    "DISPUTED_PPP1R15A_TARGET_WITH_SEVERE_PK_AND_SAFETY_LIMITATIONS": "Disputed PPP1R15A Binding & Severe Human PK / Safety Limits",
    "SOD1_COPPER_CHAPERONE_ORIGIN_UNPROVEN_IN_HUMAN_TDP43": "SOD1 Copper-Chaperone Origin (Unproven in Sporadic TDP-43 ALS)",
    "SOD1_MOUSE_PHENOCOPY_FAILED_HUMAN_TDP43": "SOD1-Mouse Phenocopy (Unproven in Human Sporadic ALS)",
    "SOMATIC_DOWNSTREAM_TDP43_MEDIATOR_OF_HYPEREXCITABILITY": "Causal TDP-43 Exon-5 Kv7.2 Hyperexcitability Driver",
    "SUBTYPE_SPECIFIC_CORTICAL_RETROTRANSPOSON_DRIVER": "Cortical ALS-TE Retrotransposon Subgroup Driver",
    "TECHNICAL_DISCORDANT_ARTIFACT": "Discordant Postmortem Technical Artifact",
    "TECHNICAL_GC_ARTIFACT": "GC-Sensitive & Cross-Cohort Non-Replicating (snRNA/Proteomics Null or Opposite)",
    "TDP43_APA_IN_VITRO_VS_LIKELY_COMPENSATORY_GLIAL_IRON_BUFFERING_IN_POSTMORTEM_TISSUE": "In Vitro APA Shift vs. Compensatory Glial Iron Homeostasis",
    "UNRESOLVED_PROXIMAL_SPHEROID_TRAPPING_VS_DOCKING": "Unresolved Axonal Mitochondrial Trapping vs. Protective Docking",
    "UNSTRATIFIED_RETROELEMENT_FUTILITY_AND_CSF_PK_GAP": "Unstratified Triumeq Clinical Futility & Dolutegravir HIV-CSF PK Gap",
    "UPSTREAM_COMPARTMENTAL_CASCADE_FOR_CHMP7_SECONDARY_SUBUNIT_FOR_CHMP2B": "Nuclear-Pore Surveillance Cascade (CHMP7 & CHMP2B Subunits)",
    "UPSTREAM_INTRINSIC_EXCITABILITY_MODULATOR": "Intrinsic Kv7.2/7.3 Excitability PD Reference",
}

INLINE_SWAPS = (
    ("(PASS_CLEAN_GE2MM)", "(Pass: >=2 mismatches)"),
    ("(CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED)", "(Caution: non-constrained 1-mm/wobble or <=25-bp 2-mm)"),
    ("PASS_CLEAN_GE2MM", "Pass (>=2 mismatches)"),
    ("CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED", "Caution: non-constrained 1-mm/wobble or <=25-bp 2-mm"),
    ("WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL", "Warn: constrained CNS gene hit"),
    ("FAIL_EXACT_0MM_OFFTARGET", "Fail: exact 0-mm off-target"),
    ("TIER_3_EXPLORATORY_DISCOVERY", "Tier 3 Exploratory Discovery"),
    ("KEEP_EXPLORATORY_UNPROVEN_SECONDARY_SUBUNIT", "Keep · Exploratory (secondary subunit)"),
    ("KEEP_EXPLORATORY_UNPROVEN", "Keep · Exploratory"),
    ("KEEP_CORE", "Keep · Core"),
    ("FALSIFIED_CLINICAL", "Excluded (Clinical)"),
    ("ARTIFACT_CONFOUNDED", "Confounded Artifact"),
    ("UNPROVEN_UNTESTED", "Unproven / Untested"),
    ("LOW_TO_MODERATE_COMPENSATORY_GLIAL_RISK", "low-to-moderate compensatory glial risk"),
    ("MANE_Select", "MANE Select"),
    ("O'Neill 2025 (DS001_ONEILL)", "O'Neill 2025 (DOI:10.1016/j.celrep.2025.115402)"),
    ("DS001_ONEILL", "O'Neill 2025"),
    ("DS005_BYE iPSC-MN", "Bye 2025 iPSC-MN"),
    ("DS005_BYE", "Bye 2025 iPSC-MN screen"),
    ("6i_TDP43_ALS_vs._HC", "TDP-43+ ALS vs. Control"),
    ("neuronal-mass-residualized mn_neur_z", "neuronal-mass-residualized"),
    ("mn_neur_z", "neuronal-mass-residualized"),
    ("competitive ST7 ELK1_unique", "Bryce-Smith 2025 ELK1-unique"),
    ("RUN-P2-T1-003 ", ""),
    (" (fixing prior 62-bp internal repeat offset)", ""),
    ("Phase 3A v2", "GENCODE v46 off-target screen"),
    ("Phase 3A promoted clean lead", "GENCODE v46 promoted clean lead"),
    ("Phase 3A #1", "GENCODE v46 #1"),
    ("Phase 3A", "GENCODE v46"),
    ("sp0=0, pm0=0", "0 exact mRNA/pre-mRNA hits"),
    ("pm1_sense=", "1mm sense pre-mRNA="),
    ("sp1=", "spliced 1mm="),
    ("pm1_50=", "50bp-SS 1mm="),
    ("pm2_25=", "25bp-SS 2mm="),
    ("sub18=", "18-nt sub-core="),
    ("ese=0", "0 disrupted ESE motifs"),
    ("max_AVI=", "max AVI="),
    ("adj_p=", "adj p="),
    ("adj_beta=", "adj β="),
    ("q_BH=", "FDR="),
    ("bh_fdr=", "FDR="),
    ("diff_log2=", "Δlog2="),
    ("z_diff=", "Δz="),
    ("Cu_brain", "Cu,brain"),
    ("ELK1_unique", "ELK1-unique"),
    ("ELK4_unique", "ELK4-unique"),
    ("EN_L2_L3", "L2/3 Exc"),
    ("EN_L5_L6", "L5/6 Exc"),
)


def clean_prose(txt: str) -> str:
    s = re.sub(r"^\[(?:MEASURED|MODEL_PRIOR)\]\s*", "", (txt or "").strip())
    s = re.sub(r"\b(?:ExploreALS|baseline intake)\s+cited\s+corrupt\s+IDs", "Chemical registry verification refuted misattributed IDs", s, flags=re.IGNORECASE)
    s = re.sub(r";\s*true IDs?\s+([A-Za-z0-9/]+),\s*fixing (?:intake|baseline) [^)]*typo", r"; \1", s, flags=re.IGNORECASE)
    s = re.sub(r",?\s*fixing (?:prior |baseline )?intake [^);]*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\b(?:prior|baseline)\s+intake\b", "prior literature catalog", s, flags=re.IGNORECASE)
    s = re.sub(r"\bintake\b", "catalog", s, flags=re.IGNORECASE)
    s = re.sub(r"\bnon-ExploreALS\b", "screen-nominated", s, flags=re.IGNORECASE)
    s = re.sub(r"\bExploreALS\s+composite\s+Tier\s+1A\s*\([^)]*\)\s*", "composite ", s, flags=re.IGNORECASE)
    s = re.sub(r"\bExploreALS\b", "prior literature catalog", s, flags=re.IGNORECASE)
    s = re.sub(r"\bCarbonALS\b", "ExploreALS", s, flags=re.IGNORECASE)
    s = re.sub(r"\bDS045\b|\bD045\b", "Trautwig 2025 CSF (PMC12082929)", s)
    s = re.sub(r"\bD003\b", "Pineda 2024 (PMID:38521060)", s)
    s = re.sub(r"\(\s*[0-9.]+(?:-[0-9.]+)?/100\s*\)", "", s)
    s = re.sub(r",?\s*(?:5D=)?[0-9.]+(?:-[0-9.]+)?/100\s*(?:liability)?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+in\s+EV-[A-Z0-9.\-/]+", "", s)
    s = re.sub(r"\(\s*EV-[A-Z0-9.\-/]+(?:\.\.EV-[A-Z0-9.\-/]+)?\s*\)", "", s)
    s = re.sub(r";?\s*EV-[A-Z0-9.\-/]+(?:\.\.EV-[A-Z0-9.\-/]+)?", "", s)
    for k, v in INLINE_SWAPS:
        s = s.replace(k, v)
    s = re.sub(r"\(\s*;\s*", "(", s)
    for old_seg, new_seg in (
        ("human clinical efficacy proof yet, and STMN2 exon-2a steric", "human clinical efficacy proof yet. STMN2 exon-2a steric"),
        ("ceiling on small-molecule Kv7 openers, serving both as", "ceiling on small-molecule Kv7 openers. It serves both as"),
        ("relative to ALS-Ox, but extension to sporadic ALS-TE", "relative to ALS-Ox. However, extension to sporadic ALS-TE"),
        ("prenylation pathology, while extreme pan-essentiality", "prenylation pathology. Extreme pan-essentiality"),
        ("forbid DROP under Epistemic Asymmetry, but C019 is recalibrated", "forbid exclusion without testing. However, C019 is recalibrated"),
        ("SICI p=0.009), not a viable chronic drug candidate", "SICI p=0.009). It is not a viable chronic drug candidate"),
        ("C9/SOD1 carriers), but fail Track B drug-target criteria:", "C9/SOD1 carriers). However, they fail therapeutic target criteria:"),
        ("GC-confounding collapse, corroborated by null blinded", "GC-confounding collapse. This is corroborated by null blinded"),
        ("human NKCC1 IC50), compounded by non-selective inhibition", "human NKCC1 IC50). This deficit is compounded by non-selective inhibition"),
        ("prior to Stage 4, Fig. 4), double-dose Phase 2b TAME at 40 mg/d", "prior to Stage 4, Fig. 4).\n\nDouble-dose Phase 2b TAME at 40 mg/d"),
        ("not prespecified in Fig. 4), double-dose 40 mg/d Phase 2b TAME", "not prespecified in Fig. 4).\n\nDouble-dose 40 mg/d Phase 2b TAME"),
        ("no CSF or tau results), and MEDALS (", "no CSF or tau results).\n\nMEDALS ("),
        ("no CSF or tau results reported), and MEDALS (", "no CSF or tau results reported).\n\nMEDALS ("),
        ("synaptosome p=0.095]), Brown dPSI=+0.4946", "synaptosome p=0.095]).\n\nSplicing, genetic constraint, and target-window profile: Brown dPSI=+0.4946"),
        ("companion CSF pressure study PMID:9249114) and FDA NDA021038 (", "companion CSF pressure study PMID:9249114).\n\nTogether with FDA NDA021038 ("),
        ("1-nt bulge), NYGC bulk G2E3 cryptic detection", "1-nt bulge).\n\nPostmortem detection and essentiality limits: NYGC bulk G2E3 cryptic detection"),
        ("cortical DIA protein (p=0.931/0.797), and CHEMBL3752910", "cortical DIA protein (p=0.931/0.797); CHEMBL3752910"),
        ("FDR=0.9284 null), while adjacent G2E3", "FDR=0.9284 null).\n\nAdjacent G2E3"),
        ("lumbar cord 1/10 ALS & 1/10 CTL), Kozareva et al. 2025", "lumbar cord 1/10 ALS & 1/10 CTL).\n\nProteomic and off-target profile: Kozareva et al. 2025"),
        ("shedding, PMID:40375307), cortical/spinal bulk RNA", "shedding, PMID:40375307).\n\nCortical/spinal bulk RNA"),
        ("mutant FUS/TDP-43 activity) plus FDR-significant survival harm", "mutant FUS/TDP-43 activity).\n\nIn addition, Bye 2025 showed FDR-significant survival harm"),
        ("discontinued ALS development), observational postmortem neuropathology", "discontinued ALS development).\n\nObservational postmortem neuropathology"),
        ("fewer spinal Iba1+ microglia, [MODEL_PRIOR:", "fewer spinal Iba1+ microglia.\n\nUnbound human CNS exposure [MODEL_PRIOR:"),
        ("Sakata et al. 2021 PMID:33035318), TDP-43 3'UTR lengthening", "Sakata et al. 2021 PMID:33035318).\n\nConvergent TDP-43 & human cortical pathology: TDP-43 3'UTR lengthening"),
        ("PMID:41120751), Brown MOESM11 splicing", "PMID:41120751).\n\nIndependent splicing & proteomic cohorts: Brown MOESM11 splicing"),
    ):
        s = s.replace(old_seg, new_seg)
    s = re.sub(r"\bUnder Epistemic Asymmetry,\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[ \t]+([.,;:\)])", r"\1", s)
    from _public_taxonomy import sanitize_public_prose
    s = sanitize_public_prose(translate_legacy_tokens_in_prose(re.sub(r"[ \t]{2,}", " ", s).strip()))
    return (s[0].upper() + s[1:]) if s and s[0].islower() else s


def _humanize_causal(raw: str) -> tuple[str, str]:
    txt = re.sub(r"([A-Z0-9])_\s+([A-Z0-9])", r"\1_\2", (raw or "").strip())
    m = re.match(r"^([A-Z0-9_]+)\s*(?::\s*(.+)|\((.+)\))?$", txt)
    if m:
        code = m.group(1)
        detail = clean_prose(m.group(2) or m.group(3) or "")
        lbl = CAUSAL_MAP.get(code, code.replace("_", " ").title())
        return lbl, detail
    return clean_prose(txt), ""


DN_VERDICT_HEADLINES: dict[str, str] = {
    "DN-01": "Promoted as #1 transcriptome-wide TDP-43 cryptic-splicing lead (Rank #{rk}/52 · Tier 2): convergent human Ribo-seq, C9-FTD homogenate protein loss, and in vivo Atg4b-KO acceleration justify preclinical SSO #2 rescue alongside early pre-inclusion (partially nuclear-TDP-43-depleted) cervical alpha-MN duplex BaseScope ISH.",
    "DN-02": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): published cortical iNeuron 2'-MOE/PS ASO rescue & FTD-MND Layer-2 BaseScope (Guo et al. 2026, PMID:42234776; Stanford docket S25-325 / Trace Neuroscience co-authors, ASO sequences withheld), 70% C9-FTD cortical Intron-53 splicing, and Pass (>=2 mismatches) SSO #1 support cortical biology.\n\n- Key Caveats: Zero ALS GWAS loci map to rs2173852, adult cervical spinal cord expression is low (1.50 TPM), and downstream alt-3'SS shunting risk remains open.",
    "DN-03": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52 · TRL 3): Ribo-seq and C9-FTD cortical homogenate PTPRT loss (paired with null synaptosome DIA and FDR-non-significant CSF ectodomain trends, PMID:40375307) plus Newton et al. 2026's published 737-base Intron-26 5'-extended exon (chr20:42098553-42099289(-), A3SS chr20:42099289-42102124(-), DOI:10.1186/s44477-025-00013-w, predicted codon-10 TAA NMD candidate) motivate Pass (>=2 mismatches) window #1 chr20:42099262-42099281(-).\n\n- Validation Requirements: Cellular origin, adult spinal motor-neuron penetrance, and net functional balance (pSTAT3-Tyr705 dephosphorylation vs. Neuroligin synaptic adhesion).",
    "DN-04": "Promoted as Tier 2 neuron-specific splicing-factor lead (Rank #{rk}/52):\n\n- Human Splicing & Protein Loss: LeafCutter cluster splicing in Australian ID-MND sporadic ALS patient iPSC-MNs (clu_25763_+ Table 6 row 228, padj=0.0090, coordinates unreported pending RT-PCR; Newton 2026 cord/BA4 qPCR; nominal BA4 p=0.0133, FDR=0.136) pairs with i3Neuron CELF5 protein loss (-1.72 log2FC, padj=0.0087, PMID:38277467 / PMID:41256508 [PREPRINT]; Spillman MOESM1 row 6733 cortical DIA null) and Zeng 2025 NMD-inhibition rescue (24.8%->44.6%, FDR=0.0235).\n- Next Validation Step: Synthetic 2'-O-MOE window #1 (inside UCL/KCL U7 patent WO2023237638A1 SEQ ID NOs: 451 & 463, 0 wet-lab CELF5 rescue data) merits endogenous Exon 1–7+ Nanopore phasing of the conditional 108-nt frame plus early pre-inclusion cervical alpha-MN BaseScope ISH.",
    "DN-05": "Elevated to #1 of Tier 3 Exploratory Discovery (Rank #{rk}/52): surviving cervical MN-niche 55-um Visium RNA (-1.23 log2FC, Seurat MAST spot FDR=0.019, N=18), Kozareva Table S15 reanalysis of Guise 2024 staged single-LCM ALS spinal MN PRUNE2 protein loss (PMID:38183652: non -2.37, mod -3.65, cell-level padj=1.8e-6 across 3 ALS donors / 75 cells vs 2 CTL donors / 25 cells), and C9-FTD synaptosomal loss (-0.49, p=0.0068, FDR=0.212; LOEUF=0.689) warrant Exon 11–12 Nanopore RT-PCR and cervical alpha-MN BaseScope ISH.",
    "DN-06": "Stepped down within Tier 3 Exploratory Discovery (Rank #{rk}/52): chr10:3099557-3099819(+) is endogenous GENCODE NMD poison exon ENSE00004576209 with >10% baseline inclusion in control human motor cortex and spinal cord (PMID:41332610 [PREPRINT]), low heterozygous LoF constraint (LOEUF=1.286), opposite-direction NYGC mRNA (+0.42, p=1.45e-6), and neuronal PPP NADPH/GSH redox risk (PMID:19448625).",
    "DN-07": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): gene-level Ribo-seq loss and unlocalized sALS iPSC-MN cluster clu_29117_+ splicing (Table 6 row 280, padj=0.015; coordinates unreported) accompany an annotated non-selective intronic ALE (82.9% TDP+ vs. 34.0% non-TDP, PMID:41120751; exact-event link and isoform-resolved full-length protein loss unverified) on a recessive gene (LOEUF=1.192, OMIM 617669) with null cortical DIA.",
    "DN-08": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): TDP-43-selective Xp11.23 ELK1 3'-extension elevates FACS cortical neuronal nuclei (+76%), Ribo-seq (+1.12), and Western blot protein (PMID:41120751) despite null BA4 excitatory snRNA & HeLa ChIP-Atlas regulon divergence, motivating head-to-head comparison of Caution-tier (0 constrained CNS hits) 3'-Ext gapmer #1 vs. steric distal-PAS SSO and 3'-Ext siRNA with Exon 1–6 counter-screens.",
    "DN-09": "Elevated within Tier 3 Exploratory Discovery (Rank #{rk}/52): pathology-selective 5'-UTR Intron-2 ALE (17/926 [1.84%] TDP+ vs. 0/750 non-TDP NYGC libraries, Fisher p=6.25e-5, PMID:41120751), i3Neuron Ribo-seq loss (-1.02, padj=0.0064), C9-FTLD bulk reduction (-0.59, FDR=0.036), and inconclusive C9-FTD O14490-6 homogenate/synaptosomal DIA trends require spinal MN penetrance and downstream DLGAP1beta promoter-escape profiling.",
    "DN-10": "Reclassified as a Candidate CSF Somatodendritic Attrition Marker (Pre-Validation · Rank #{rk}/52): Emory DIA CSF (-0.50, FDR=8.2e-9) and C9-FTD synaptosomal DPP6 depletion track Kv4.2 membrane loss on a non-catalytic scaffold (PDB 1XFD 3.00A Asp712), pending PRM bridging for MS2-TMTpro omnibus discordance.",
    "DN-11": "Reclassified as a Candidate CSF Somatodendritic Attrition Marker (Pre-Validation · Rank #{rk}/52): Emory DIA CSF (-0.32, FDR=0.044) and BA4 excitatory DPP10 reduction parallel paralogous DPP6 loss on a non-catalytic Kv4 subunit (canonical Q8N608 Gly651; isoform Q8N608-3 Gly655), pending PRM bridging for MS2-TMTpro and WashU MWU sensitivity.",
    "DN-12": "Reclassified as a Candidate CSF Cytoskeletal Injury Marker (Pre-Validation · Rank #{rk}/52, 3 validation checks): ALS CSF pan-Cofilin-1 elevation across Emory/WashU DIA (corroborated in overlapping Emory TMTpro and surviving erythrocyte/platelet lysis OLS controls) pairs with postmortem sALS spinal MN Ser3 hyperphosphorylation and model TDP-43 aggregation (PMID:41804798) on a pan-essential gene.",
    "DN-13": "Deprioritized following randomized human ALS clinical trials (Rank #{rk}/52 · Drop): postmortem MAOB elevation is consistent with reactive astrogliosis, and PET-saturated (>85–90% in N=3 HV) selective MAOB inhibition failed three double-blind placebo-controlled ALS RCTs plus one open-label trial.",
    "DN-14": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52, 4 hurdles): cyclic hexapeptide PMX 205 (ALS-205, PubChem CID:6918845; Woodruff/UQ hSOD1-G93A rescue PMID:28128456; completed subcutaneous Phase 1a/1b ACTRN12622000927729 incl. N=8 ALS single-dose Ph1b; Fung et al. 2025 DOI:10.1016/j.imbio.2025.153003; intrahelical Site-2 analog PMX-53 in PDB 6C1R PMID:29867214) has zero completed ALS efficacy trials despite upstream C5/C3 failures (HEALEY zilucoplan DRR=1.08 PMID:39960672).\n\n- Key Caveat: Monocultures lacking exogenous C5/C5a make ligand-independent 2.5 uM off-target activity a primary alternative hypothesis pending C5AR1-knockout target validation.",
    "DN-15": "Deprioritized in tested oral human ALS trials (Rank #{rk}/52 · Drop): sub-FDR 2.5 uM survival (+0.90d, FDR=0.070) failed human ALS CSF glutamate/aspartate/BCAA and 4-scale clinical testing at 300 mg/d (Ryberg 2003 PMID:12807386, N=30 crossover completers) alongside 100 mg/d Eisen 1993 (PMID:7906190, N=67).\n\n- Comparator Na+ Channel Trials: Neither mexiletine (PMID:26911633, N=60; reduced muscle cramps without slowing ALSFRS-R/SVC) nor flecainide (FANS PMID:26844270, N=54; less secondary neurophysiological-index decline p=0.02 without slowing primary ALSFRS-R slope p=0.50) slowed ALSFRS-R decline.",
    "DN-16": "Deprioritized as fixed-dose Triumeq in Phase 3 human ALS testing (Rank #{rk}/52 · Drop): LIGHTHOUSE II Triumeq interim survival futility (NCT05193994, N=419; fixed-dose 3-drug regimen does not isolate dolutegravir alone).\n\n- Single-Agent PK & Mechanism: Dolutegravir alone faces a 58–263x measured total HIV CSF PK gap (9.5–42.9 nM, PMID:24944232) and autonomous human LINE-1 encodes zero integrase (preserving EALS-033 Censavudine in ALS-TE).",
    "DN-17": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): sub-FDR 2.5 uM survival (+0.95d, FDR=0.094) may reflect extracellular thiol buffering and NCT07414212 co-doses low-dose 600 mg/d oral NAC with 1,800 mg/d EH301, yet Louwerse 1995 (50 mg/kg/d SC, N=110: HR=0.74 [0.41–1.33]; limb 0.50 vs bulbar 1.66) was underpowered and 70 mg/kg oral BID NAC reaches 9.26 uM human CSF (PMID:25765302), motivating high-dose CNS GSH target-engagement testing.",
    "DN-18": "Deprioritized following randomized human ALS clinical testing (Rank #{rk}/52 · Drop): sub-FDR in vitro survival (+0.74d, FDR=0.183) failed in Phase II QALS at 2,700 mg/day (NCT00243932, N=185 / Stage 2 n=150: primary p=0.14 driven by 1 CoQ10 vs 5 placebo Month-9 deaths coded as ALSFRS-R=0; prespecified death=16 sensitivity p=0.025 < 0.10 futile; Table 2 GI absorption plateau).",
    "DN-19": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): adding 2.5 uM L-serine shifts ~400 uM basal BrainPhys/DMEM-F12 media serine concentration by only +0.625% (survival +0.71d, p=0.0419, FDR=0.1707), and zero placebo-controlled sporadic ALS RCTs have completed (randomized blinded 4-dose Ph1 NCT01835782 used historical controls; open-label NCT03580616).\n\n- Genetic Safeguard: Variant-specific SPTLC1/SPTLC2 GoF ceramide overproduction motivates a proposed prospective genetic and sphingolipid screening safeguard (PMID:34059824; PMID:43025655).",
}

DN_TOP_SPLIT_RE = re.compile(
    r",\s*(?:YET|BUT|though|whereas)\s+|;\s*(?=DepMap|polar anionic|however,|GENCODE v46 \(0)|,\s*AND\s+(?=selective)"
)


def _split_top_level_dn(just: str) -> tuple[str, str]:
    depth = 0
    for idx, ch in enumerate(just):
        if ch in "([":
            depth += 1
        elif ch in ")]" and depth > 0:
            depth -= 1
        elif depth == 0:
            m = DN_TOP_SPLIT_RE.match(just, idx)
            if m:
                left = just[:idx].rstrip(".") + "."
                right = re.sub(r"^however,\s+", "", just[m.end():].strip(), flags=re.IGNORECASE)
                return left, (right[0].upper() + right[1:] if right else right)
    return (
        just.rstrip(".") + ".",
        "Non-significant difference vs. small-n spinal ALS-SOD1/FUS requires cryptic-junction RT-ddPCR and isoform-resolved SSO rescue validation.",
    )


def build_summary_dossiers(
    port_rows: list[dict[str, str]],
    cdec_rows: list[dict[str, str]],
    p3b_rows: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    cdec_map = {r["carbon_id"]: r for r in cdec_rows}
    p3b_map = {r["denovo_id"]: r for r in p3b_rows}
    port_ids = {r["portfolio_id"] for r in port_rows}
    assert set(CANDIDATE_HYPOTHESES) == port_ids, (
        f"CANDIDATE_HYPOTHESES mismatch: missing={port_ids - set(CANDIDATE_HYPOTHESES)}, extra={set(CANDIDATE_HYPOTHESES) - port_ids}"
    )
    edges_map, _, _ = build_edges_and_lenses(port_rows)
    out: dict[str, dict[str, str]] = {}

    for r in port_rows:
        pid = r["portfolio_id"]
        hyp = clean_prose(CANDIDATE_HYPOTHESES[pid])
        if pid in cdec_map:
            cd = cdec_map[pid]
            causal_lbl, causal_det = _humanize_causal(cd["causal_vs_reactive_assessment"])
            verdict = clean_prose(cd["factual_justification"])
            proves = clean_prose(cd["evidence_proves_hypothesis"])
            disproves = clean_prose(cd["evidence_disproves_hypothesis"])
            sub = causal_det if causal_det else causal_lbl
        else:
            pb = p3b_map[pid]
            causal_lbl, _ = _humanize_causal(pb["causal_vs_reactive_assessment"])
            sub = clean_prose(pb["mechanism_summary"])
            just = clean_prose(pb["factual_justification"])
            if pid == "DN-12":
                proves, _ = _split_top_level_dn(just)
                disproves = (
                    "- Essentiality & Phospho-Inactivation: Cellularly pan-essential across dividing human lines (DepMap p10 Chronos = -1.3534; gnomAD v4.1 MANE ENST00000308162 LOEUF = 0.408, pLI = 0.990, mis_z = 3.38), while postmortem sporadic ALS spinal motor neurons show LIMK1-associated Ser3-cofilin hyperphosphorylation/inactivation and experimental models link CFL1 loss/inactivation to TDP-43 aggregation (Jagaraj et al. 2026 Brain PMID:41804798 — opposite in phosphorylation state to dephosphorylated cofilin rods).\n"
                    "- Clinical ROCK1/2 Comparator & Assay Requirements: Upstream ROCK1/2 blockade (Fasudil, which de-represses CFL1) showed no clinical separation in Phase 2a ROCK-ALS (NCT03792490, N = 120, PMID:39424560) or Bye 2025 (p = 0.209). Bottom-up tryptic MS measures unmodified pan-CFL1, requiring atraumatic-LP hemolysis/platelet QC (PMID:31566909), phosphatase-stabilized pSer3-CFL1:total CFL1 assays, and incremental prognostic value beyond NfL and pNfH."
                )
            elif pid == "DN-15":
                proves = "Bye 2025 iPSC-MN screen Rank #13/107 at 2.5 uM (+0.8992d across 16 sALS lines, nominal p=0.0143, sub-FDR q_BH=0.0695) and presynaptic Na+ channel hyperexcitability rationale."
                disproves = (
                    "- Direct Human ALS Lamotrigine Trials: Although Eisen et al. 1993 (PMID:7906190, 100 mg/d, N=67, D=12 deaths) was individually underpowered for survival, high-dose Ryberg et al. 2003 (PMID:12807386, 300 mg/d paired double-blind crossover across N=30 completers with serial LPs measuring CSF lamotrigine, glutamate, aspartate, and BCAAs; exact randomized N and numerical CSF concentration table require paywalled full text) found no significant human CSF amino-acid reduction or clinical benefit across 4 scales.\n"
                    "- Comparator Na+ Channel Trials & Safety: Neither mexiletine (Weiss et al. 2016 PMID:26911633, N=60 12-wk trial: reduced muscle cramp frequency p=0.047/0.002 and intensity p=0.005 without slowing ALSFRS-R or SVC decline) nor flecainide (FANS Park et al. 2015 PMID:26844270 / PMC4703720, N=54 32-wk trial: primary ALSFRS-R slope p=0.50 despite less secondary neurophysiological-index decline [p=0.02]) slowed ALSFRS-R decline, and FDA SJS/TEN plus cardiac NaV1.5 warnings weigh against these tested oral regimens (without establishing class-wide futility across all Na+ channel modulators)."
                )
            elif pid == "DN-16":
                proves = "Open-label Phase 2a LIGHTHOUSE safety/tolerability in unstratified sporadic ALS (NCT02868580, Gold et al. 2019 PMID:31284774, N=40 treated / 35 completers), Bye 2025 nominal 2.5 uM readout (+0.7458d, p=0.0431), and O'Neill 2025 retrotransposon-active cortical ALS-TE subtype biology."
                disproves = (
                    "- Phase 3 LIGHTHOUSE II Futility: NCT05193994 (N=419, 2:1 fixed-dose three-drug Triumeq [dolutegravir 50 mg + abacavir 600 mg + lamivudine 300 mg] vs placebo in unstratified ALS) stopped early at planned interim analysis for survival futility (announced 2025-04-05; registry completion 2025-06-30; applies to fixed-dose Triumeq and does not isolate dolutegravir alone).\n"
                    "- Single-Agent CSF Exposure & Mechanism: Week-16 measured total human HIV CSF dolutegravir (9.5-42.9 nM, median 31.0 nM; Letendre et al. 2014 PMID:24944232) sits 58-263x below nominal 2.5 uM (modeled free fraction lower still), and autonomous human LINE-1 encodes zero integrase (preserving nanomolar LINE-1 ORF2p RT inhibition in EALS-033 Censavudine)."
                )
            elif pid == "DN-17":
                proves = "Bye 2025 iPSC-MN screen Rank #12/107 at 2.5 uM (+0.9458d across 15 sALS lines, nominal p=0.02013, Wilcoxon p=0.00671), underpowered subcutaneous NAC survival signals in Louwerse et al. 1995 (PMID:7763202, 50 mg/kg/d SC, N=110: overall HR=0.74 [95% CI 0.41-1.33], p=0.31; limb-onset HR=0.50 [0.24-1.04], p=0.06), and high-dose oral NAC human CSF penetration (70 mg/kg BID -> 9.26 +/- 1.62 uM CSF NAC, p<0.001, Katz et al. 2015 PMID:25765302)."
                disproves = (
                    "- Media Buffering Caveat: Misses 107-drug screen FDR (q_BH=0.09364), where 2.5 uM reactive thiol can buffer extracellular media cystine/ROS independently of neuronal glutathione synthesis.\n"
                    "- Low-Dose Oral Bioavailability Gap: Phase 2 NCT07414212 (N=90) co-administers 600 mg/d effervescent NAC with 1,800 mg/d EH301 (1,500 mg NR + 300 mg PTER) + riluzole (5.83x lower mass than 3,500 mg/d SC at 70 kg; ALSUntangled #82 PMID:41777232), and oral NAC undergoes ~90-94% first-pass gut/hepatic deacetylation vs neutral BBB-permeable N-acetylcysteine amide (NACA/AD4)."
                )
            elif pid == "DN-18":
                proves = "Bye 2025 iPSC-MN screen Rank #19/107 at 2.5 uM (+0.7430d across 16 sALS lines, nominal p=0.04951) and mitochondrial Complex I-III electron-transport rationale."
                disproves = (
                    "- Screen & Absorption Limits: Missed 107-drug screen FDR (q_BH=0.1827; cLogP ~19.4 colloid dispersion in lipoprotein-free media), and oral GI absorption saturated between 1,800 and 2,700 mg/d in Phase II QALS (Table 2; PMID:16344537).\n"
                    "- Randomized Phase II QALS Futility: In NCT00243932 (Kaufmann et al. 2009 PMID:19743457, PMC2854625 Table 3, N=185 total / Stage 2 n=150 at 2,700 mg/d vs placebo), primary p=0.14 (8.80 [SD 7.34] vs 9.44 [SD 8.82]) reflected 1 Month-9 CoQ10 death vs 5 placebo deaths imputed as total ALSFRS-R=0, prespecified death=16 sensitivity crossed formal futility (8.52 vs 8.37, p=0.025 < 0.10; 13/17 death scores futile; linear slope p=0.097), and secondary endpoints were null."
                )
            elif pid == "DN-19":
                proves = "Bye 2025 iPSC-MN screen Rank #20/107 at 2.5 uM (+0.7117d survival shift across 16 sALS lines, unadjusted paired p=0.04190) and randomized double-blind 4-dose Phase 1 tolerability up to 15 g BID (30 g/d) oral dosing vs historical controls (NCT01835782 N=20, Levine et al. 2017 PMID:27589995; motivated historically by Cox/Dunlop BMAA-displacement rationale)."
                disproves = (
                    "- Basal Media Dilution & Uncontrolled Trial History: Fixed 2.5 uM library addition increases L-serine molar concentration by only +0.625% atop ~400 uM basal BrainPhys/DMEM-F12 L-serine and misses 107-drug FDR (q_BH=0.17067). Zero placebo-controlled sporadic ALS efficacy RCTs have completed (randomized blinded 4-dose Ph1 NCT01835782 used historical controls; open-label NCT03580616 N=43 terminated for IRB noncompliance; historical BMAA rationale remains unconfirmed in sporadic ALS).\n"
                    "- Monogenic SPTLC1/SPTLC2 Safeguard: Specific rare SPTLC1/SPTLC2 GoF ALS variants overproduce canonical C18-C22 sphingolipids under ORMDL feedback loss, motivating a proposed prospective genetic/sphingolipid screening safeguard (PMID:34059824; PMID:43025655; intrathecal SPTLC1 ASO LTX-002 NCT07660614)."
                )
            else:
                proves, disproves = _split_top_level_dn(just)
            verdict = DN_VERDICT_HEADLINES[pid].format(rk=r["unified_rank"])

        acc_id = r.get("accession_id") or legacy_to_accession(pid)
        item = {
            "hyp": hyp,
            "sub": sub,
            "causal": causal_lbl,
            "verdict": verdict,
            "proves": proves,
            "disproves": disproves,
            **edges_map[acc_id],
        }
        assert len(hyp) >= 60 and hyp not in {verdict, proves, disproves}, f"{pid}: invalid or duplicated hypothesis summary"
        blob = " ".join(item.values())
        assert "/100" not in blob, f"{pid}: /100 score leaked in summary projection: {blob}"
        assert blob.count("(") == blob.count(")"), f"{pid}: unbalanced parentheses in summary projection: {blob}"
        assert item["verdict"] != item["proves"] and item["verdict"] != item["disproves"], f"{pid}: duplicated verdict in summary projection"
        assert not re.search(
            r"\bcarbonals\b|\bv0\b|\bD003\b|\bD045\b|\bDS045\b|Phase\s*3A|intake|typo|PASS_CLEAN_GE2MM|CAUTION_1MM|WARN_1MM|TIER_3_EXPLORATORY|more_in_JSON",
            blob,
            re.I,
        ), f"{pid}: uncleaned token in summary projection: {blob}"
        assert not re.search(
            r"\$\s*\d|\b(?:capital|dollar|dollars|cheap|cheaper|cheapest|budget|budgets|expensive|inexpensive|fund|funds|funding|funded|cost|costs|costing|evoi)\b",
            blob,
            re.I,
        ), f"{pid}: financial/capital leak in summary projection: {blob}"
        out[acc_id] = item
    return out
