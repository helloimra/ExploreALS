"""Compile publication-grade Summary-of-Findings (SoF) prose for all 59 CarbonALS candidates from frozen registries."""
from __future__ import annotations

import re

from _candidate_contrasts_b import build_edges_and_lenses
from _candidate_hypotheses import CANDIDATE_HYPOTHESES
from carbon_als.accessions import legacy_to_accession, translate_legacy_tokens_in_prose

CAUSAL_MAP: dict[str, str] = {
    "AMBIGUOUS_ISOFORM_DEPENDENT": "Isoform-Dependent Sign (Secreted Decoy sST2 vs. Membrane ST2L)",
    "AMBIGUOUS_MICROGLIAL_VS_OFFTARGET_IN_VITRO": "Ambiguous Glial vs. Off-Target In Vitro Signal",
    "AMBIGUOUS_PROAPOPTOTIC_DENDRITIC_VS_TROPHIC_NUCLEAR_GAIN": "Biphasic Dendritic vs. Nuclear Transcription Sign",
    "AMBIGUOUS_SYNAPTIC_ATP_LOSS_VS_PPP_REDOX_SHUNT": "Dual Synaptic Glycolysis vs. PPP Redox Trade-Off",
    "BIOMARKER_GATED_TREG_MODULATION_UNPROVEN_PHASE3": "Biomarker-Gated Treg Immunomodulation",
    "BIOMARKER_SOMATODENDRITIC_ATTRITION": "Reactive Somatodendritic Attrition Biomarker",
    "BIPHASIC_STAGE_DEPENDENT": "Biphasic Disease-Stage Dependent",
    "CAUSAL_AXONAL_MAINTENANCE_LOSS": "Causal Axonal Maintenance Loss",
    "CAUSAL_EXCITABILITY_MODULATOR_PARTIAL_ENGAGEMENT": "Intrinsic Motor Excitability Modulator",
    "CAUSAL_GENETIC_AND_MECHANISTIC_DRIVER": "Human-Genetics-Anchored Causal Driver",
    "OPPOSING_MN_VS_MICROGLIAL_14Q12_COLOCALIZATION": "Opposing MN vs. Microglial chr14q12 Colocalization",
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
    "DOWNSTREAM_CAUSAL_EFFECTOR_OF_AXONOPATHY": "Downstream Causal Effector of Axonopathy",
    "DOWNSTREAM_EXCITABILITY_CLINICALLY_FUTILE": "Downstream Excitability Blockade (Clinically Futile)",
    "DOWNSTREAM_EXCITOTOXIC_HYPOTHESIS_REFUTED_IN_HUMANS": "Downstream Excitotoxic Hypothesis (Refuted in Human ALS RCTs)",
    "DOWNSTREAM_REDOX_CLINICALLY_FUTILE": "Downstream Redox Buffering (Clinically Futile)",
    "DUAL_NEURONAL_TDP43_JAK2_APA_AND_SUBTYPE_GLIAL_INFLAMMATION": "Dual Neuronal JAK2 APA vs. Subtype Glial JAK1 Catch-22",
    "EARLY_WINDOW_HOMOCYSTEINE_METHYLATION_RESCUE": "Early-Window (<=12m Trial) Methylation SOC Benchmark (Japan MHLW)",
    "ENDOLYSOSOMAL_POLYGP_CLEARANCE_VS_CONTINUOUS_VACUOLATION_TOXICITY": "Endolysosomal Clearance vs. Continuous Vacuolation Toxicity",
    "HYPOTHESIS_REFUTED_IN_HUMANS": "Refuted in Powered Human ALS RCTs",
    "IATROGENIC_ANTAGONISM_OF_ESSENTIAL_SNARE_PRENYLATION": "Iatrogenic Inhibition of Essential SNARE Prenylation",
    "AMBIGUOUS_EXTRACELLULAR_BUFFERING_VS_GSH_RESTORATION": "Extracellular Media Thiol Buffering vs. High-Dose CNS GSH Rescue",
    "UNPROVEN_DEOXYSPL_CLEARANCE_WITH_MONOGENIC_SPT_CONTRAINDICATION": "Unproven 1-Deoxysphingolipid Hypothesis (Monogenic SPTLC1/2 Contraindicated)",
    "IN_VITRO_REDOX_BUFFERING_ARTIFACT": "Extracellular Media Thiol-Buffering Artifact",
    "IN_VITRO_BASAL_MEDIA_NOISE_AND_SPT_WRONG_SIGN": "In Vitro Basal Media Noise & SPTLC1/2 Wrong Sign",
    "SPLIT_BY_SUBNODE": "Sub-Node Split (C3/C4B Dropped · CNS C1q Exploratory)",
    "METABOLIC_HYPOTHESIS_MEDIA_CONFOUNDED_UNPROVEN": "Media-Confounded Serine Metabolic Hypothesis",
    "MICROMOLAR_CAD_PHOSPHOLIPIDOSIS_ARTIFACT": "Micromolar Cationic-Amphiphilic Phospholipidosis Artifact",
    "NON_CAUSAL_PLEIOTROPIC_MISMATCH": "Non-Causal Pleiotropic Target Mismatch",
    "NON_CAUSAL_RODENT_PROMOTER_ARTIFACT": "Unvalidated In Vivo EAAT2 Induction & Intact Human ALS SLC1A2 mRNA",
    "OFF_TARGET_HIGH_CONC_SCREEN_HIT": "High-Concentration Off-Target Screen Hit",
    "OFF_TARGET_MONOAMINERGIC_SEDATION_WITH_CLASS_ISR_FAILURE": "Off-Target 5-HT2A / α1-Adrenergic Sedation & Class ISR Futility",
    "PERIPHERAL_LYMPHOID_IMPDH_BLOCKER": "Peripheral Lymphoid IMPDH Immunosuppressant",
    "POTENTIAL_CAUSAL_PROTEOSTASIS_LOSS": "Mendelian-Anchored Neuronal Chaperone Loss",
    "REACTIVE_ASTROGLIAL_COMPOSITION_SHIFT": "Reactive Astroglial Cell-Fraction Shift",
    "REACTIVE_BIOMARKER_AND_COMPENSATORY_PROTECTIVE": "Compensatory Glial Clearance & Fluid Staging Biomarker",
    "REACTIVE_DAMAGE_RELEASE_PAN_ESSENTIAL": "Pan-Essential Cytoskeletal Release Biomarker",
    "REACTIVE_MICROGLIAL_PROLIFERATION_MARKER": "Reactive Microglial Proliferation Marker",
    "REFUTED_PPP1R15A_BINDING_UM_POLYPHARMACOLOGY_UNREACHABLE_IN_HUMANS": "Refuted PPP1R15A Binding & Unreachable CNS Exposure",
    "SOD1_COPPER_CHAPERONE_ORIGIN_UNPROVEN_IN_HUMAN_TDP43": "SOD1 Copper-Chaperone Origin (Unproven in Sporadic TDP-43 ALS)",
    "SOD1_MOUSE_PHENOCOPY_FAILED_HUMAN_TDP43": "SOD1-Mouse Phenocopy (Unproven in Human Sporadic ALS)",
    "SOMATIC_DOWNSTREAM_TDP43_MEDIATOR_OF_HYPEREXCITABILITY": "Causal TDP-43 Exon-5 Kv7.2 Hyperexcitability Driver",
    "SUBTYPE_SPECIFIC_CORTICAL_RETROTRANSPOSON_DRIVER": "Cortical ALS-TE Retrotransposon Subgroup Driver",
    "TECHNICAL_DISCORDANT_ARTIFACT": "Discordant Postmortem Technical Artifact",
    "TECHNICAL_GC_ARTIFACT": "GC-Sensitive & Cross-Cohort Non-Replicating (snRNA/Proteomics Null or Opposite)",
    "TDP43_APA_IN_VITRO_VS_LIKELY_COMPENSATORY_GLIAL_IRON_BUFFERING_IN_POSTMORTEM_TISSUE": "In Vitro APA Shift vs. Compensatory Glial Iron Homeostasis",
    "UNRESOLVED_PROXIMAL_SPHEROID_TRAPPING_VS_DOCKING": "Unresolved Axonal Mitochondrial Docking Polarity",
    "UNSTRATIFIED_RETROELEMENT_FUTILITY_AND_CSF_PK_GAP": "Unstratified Retroelement Futility & 80–500x Unbound CSF PK Deficit",
    "UPSTREAM_COMPARTMENTAL_CASCADE_FOR_CHMP7_SECONDARY_SUBUNIT_FOR_CHMP2B": "Nuclear-Pore Surveillance Cascade (CHMP7 & CHMP2B Subunits)",
    "UPSTREAM_INTRINSIC_EXCITABILITY_MODULATOR": "Intrinsic Kv7.2/7.3 Excitability PD Benchmark",
}

INLINE_SWAPS = (
    ("PASS_CLEAN_GE2MM", "Clean >=2mm off-target status"),
    ("CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED", "Caution (non-constrained 1mm/wobble)"),
    ("WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL", "Warn (constrained CNS gene hit)"),
    ("FAIL_EXACT_0MM_OFFTARGET", "Fail (exact 0mm off-target)"),
    ("TIER_3_EXPLORATORY_DISCOVERY", "Tier 3 Exploratory Discovery"),
    ("KEEP_EXPLORATORY_UNPROVEN_SECONDARY_SUBUNIT", "Keep · Exploratory (secondary subunit)"),
    ("KEEP_EXPLORATORY_UNPROVEN", "Keep · Exploratory"),
    ("KEEP_CORE", "Keep · Core"),
    ("FALSIFIED_CLINICAL", "Falsified (Clinical)"),
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
    ("Phase 3A v2", "GENCODE v46 6-tier"),
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
    ):
        s = s.replace(old_seg, new_seg)
    s = re.sub(r"\bUnder Epistemic Asymmetry,\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+([.,;:\)])", r"\1", s)
    from _public_taxonomy import sanitize_public_prose
    s = sanitize_public_prose(translate_legacy_tokens_in_prose(re.sub(r"\s{2,}", " ", s).strip()))
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
    "DN-02": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): published cortical iNeuron 2'-MOE/PS ASO rescue & FTD-MND Layer-2 BaseScope (Guo et al. 2026, PMID:42234776; Stanford docket S25-325 / Trace Neuroscience co-authors, ASO sequences withheld), 70% C9-FTD cortical Intron-53 splicing, and clean (>=2 mismatches) SSO #1 are tempered by zero ALS GWAS loci on rs2173852, low cervical cord expression (1.50 TPM), and alt-3'SS shunting risk.",
    "DN-03": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): severe Ribo-seq and C9-FTD cortical homogenate PTPRT loss (paired with null synaptosome DIA and FDR-non-significant CSF ectodomain trends, PMID:40375307) require 1-bp Intron-26 junction mapping and neurotrophic pSTAT3-Tyr705 vs. Neuroligin sign resolution.",
    "DN-04": "Promoted as Tier 2 neuron-specific splicing-factor lead (Rank #{rk}/52): LeafCutter cluster splicing in sporadic ALS patient iPSC-MNs (clu_25763_+ padj=0.0090, cluster-level pending junction RT-PCR; nominal BA4 p=0.0133, FDR=0.136), Kozareva 2025 i3Neuron CELF5 protein loss (-1.72 log2FC, padj=0.0087, PMID:41256508), Zeng 2025 NMD-inhibition rescue (24.8%->44.6%, FDR=0.0235), and clean (>=2 mismatches) synthetic 2'-O-MOE SSO #1 (0 wet-lab CELF5 constructs in literature or prophetic U7 patent WO2023237638A1) merit endogenous Exon 1–7+ Nanopore phasing (<1-2% LOQ Exon-5 skip / <=WT ~2.8% micro-intron retention) plus early pre-inclusion cervical alpha-MN BaseScope ISH.",
    "DN-05": "Elevated to #1 of Tier 3 Exploratory Discovery (Rank #{rk}/52): surviving cervical MN-niche 55-um Visium RNA (-1.23 log2FC, pseudoreplicated spot FDR=0.019, N=18), pre-inclusion single-LCM ALS spinal MN PRUNE2 protein loss (Guise 2024 PMID:38183652: non -2.37, mod -3.65, padj=1.8e-6, N=14 donors), and C9-FTD synaptosomal loss (-0.49, p=0.0068, FDR=0.212; LOEUF=0.689) warrant Exon 11–12 Nanopore RT-PCR and cervical alpha-MN BaseScope ISH.",
    "DN-06": "Stepped down within Tier 3 Exploratory Discovery (Rank #{rk}/52): chr10:3099557-3099819(+) is endogenous GENCODE NMD poison exon ENSE00004576209 with >10% false-positive inclusion in control human motor cortex and spinal cord (PMID:41332610), complete LoF tolerance (LOEUF=1.286), opposite-sign NYGC mRNA (+0.42, p=1.45e-6), and neuronal PPP NADPH/GSH redox risk (PMID:19448625).",
    "DN-07": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): Ribo-seq loss and sALS iPSC-MN cluster clu_29117_+ splicing (padj=0.015) target an annotated non-selective intronic ALE (selective=False: 82.9% TDP+ vs. 34.0% non-TDP, PMID:41120751) on a recessive gene (LOEUF=1.192, OMIM 617669) with null cortical DIA.",
    "DN-08": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): TDP-43-selective Xp11.23 ELK1 3'-extension elevates FACS cortical neuronal nuclei (+76%), Ribo-seq (+1.12), and Western blot protein (PMID:41120751) despite null BA4_Exc & HeLa ChIP-Atlas regulon divergence, motivating head-to-head comparison of Caution-tier (0 constrained CNS hits) 3'-Ext gapmer #1 vs. steric distal-PAS SSO and 3'-Ext siRNA with Exon 1–6 counter-screens.",
    "DN-09": "Elevated within Tier 3 Exploratory Discovery (Rank #{rk}/52): pathology-selective 5'-UTR Intron-2 ALE (17/926 [1.84%] TDP+ vs. 0/750 non-TDP NYGC libraries, Fisher p=6.25e-5, PMID:41120751), i3Neuron Ribo-seq loss (-1.02, padj=0.0064), and C9-FTD homogenate/synaptosomal DLGAP1 loss require spinal MN penetrance and downstream DLGAP1beta promoter-escape profiling.",
    "DN-10": "Reclassified as a Candidate CSF Somatodendritic Attrition Marker (Pre-Validation · Rank #{rk}/52): Emory DIA CSF (-0.50, FDR=8.2e-9) and C9-FTD synaptosomal DPP6 depletion track Kv4.2 membrane loss on a non-catalytic scaffold (PDB 1XFD 3.00A Asp712), gated on PRM bridging for MS2-TMTpro omnibus discordance.",
    "DN-11": "Reclassified as a Candidate CSF Somatodendritic Attrition Marker (Pre-Validation · Rank #{rk}/52): Emory DIA CSF (-0.32, FDR=0.044) and BA4 excitatory DPP10 reduction parallel paralogous DPP6 loss on a non-catalytic Kv4 subunit (Q8N608 Gly651), gated on PRM bridging for MS2-TMTpro and WashU MWU sensitivity.",
    "DN-12": "Reclassified as a Candidate CSF Cytoskeletal Injury Marker (Pre-Validation · Rank #{rk}/52, 3 gates): cross-platform ALS CSF pan-Cofilin-1 elevation survives erythrocyte/platelet lysis OLS controls while LIMK1-driven Ser3 hyperphosphorylation (inactivation) drives SALS TDP-43 pathology (PMID:41804798) on a pan-essential gene.",
    "DN-13": "Falsified in randomized human ALS clinical trials (Rank #{rk}/52 · Drop): postmortem MAOB elevation reflects reactive astrogliosis, and PET-saturated (>85–90%) selective MAOB inhibition failed three double-blind placebo-controlled ALS RCTs plus one open-label trial.",
    "DN-14": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52, 4 hurdles): cyclic hexapeptide PMX 205 (ALS-205, PubChem CID:6918845; Woodruff/UQ SOD1G93A rescue PMID:28128456; completed subcutaneous Phase 1a/1b ACTRN12622000927729; intrahelical Site-2 analog PMX-53 in PDB 6C1R PMID:29867214) has zero completed ALS efficacy trials despite upstream C5/C3 failures (HEALEY zilucoplan DRR=1.08 PMID:39960672), though C5/C5a-free monocultures make ligand-independent 2.5 uM off-target activity the primary null pending C5AR1-KO deconvolution.",
    "DN-15": "Falsified in human ALS clinical & CSF-PD testing (Rank #{rk}/52 · Drop): sub-FDR 2.5 uM survival (+0.90d, FDR=0.070) failed human CSF glutamate/clinical PD at 300 mg/d (~7–15 uM CSF, Ryberg 2003 N=30) alongside Eisen 1993 (N=67) and oral NaV class futility.",
    "DN-16": "Falsified in Phase 3 human ALS clinical testing (Rank #{rk}/52 · Drop): LIGHTHOUSE II interim survival futility (N=419; announced 5 Apr 2025, completion 30 Jun 2025), an 80–500x unbound human CSF PK gap (~5–32 nM, PMID:24944232), and zero LINE-1 integrase refute dolutegravir/Triumeq while preserving EALS-033 Censavudine in ALS-TE.",
    "DN-17": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): sub-FDR 2.5 uM survival (+0.95d, FDR=0.094) may reflect extracellular thiol buffering and NCT07414212 co-doses low-dose 600 mg/d oral NAC with 1,800 mg/d EH301, yet Louwerse 1995 (50 mg/kg/d SC, N=110: HR=0.74 [0.41–1.33]) was underpowered and 70 mg/kg oral BID NAC reaches 9.26 uM human CSF (PMID:25765302), gating high-dose CNS GSH target engagement.",
    "DN-18": "Falsified in randomized human ALS clinical testing (Rank #{rk}/52 · Drop): sub-FDR in vitro survival (+0.74d, FDR=0.183) failed in Phase II QALS at 2,700 mg/day (NCT00243932, N=185 / Stage 2 n=150: primary p=0.14 driven by 5 vs 1 Month-9 deaths coded 0; prespecified death=16 sensitivity p=0.025 < 0.10 futile; Table 2 GI absorption plateau).",
    "DN-19": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/52): adding 2.5 uM L-serine shifts ~400 uM basal BrainPhys/DMEM-F12 media serine concentration by only +0.625% (survival +0.71d, p=0.0419, FDR=0.1707), zero controlled sporadic ALS RCTs have completed (NCT01835782; NCT03580616), and <0.5% monogenic SPTLC1/SPTLC2 GoF ALS requires mandatory genetic exclusion (PMID:34059824; PMID:43025655).",
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
                    "Cellularly pan-essential across dividing human lines (DepMap p10 Chronos = -1.3534; gnomAD v4.1 MANE ENST00000308162 LOEUF = 0.408, pLI = 0.990, mis_z = 3.38) "
                    "while sporadic ALS spinal motor neurons exhibit LIMK1-mediated Ser3-cofilin hyperphosphorylation/inactivation (Jagaraj et al. 2026 Brain PMID:41804798 — opposite in phospho-polarity to dephospho-cofilin rods) "
                    "and upstream ROCK1/2 blockade (Fasudil, which de-represses CFL1) showed no clinical separation in Phase 2a ROCK-ALS (NCT03792490, N = 120, PMID:39424560) or Bye 2025 (p = 0.209); "
                    "bottom-up tryptic MS measures unmodified pan-CFL1, requiring atraumatic-LP hemolysis/platelet QC (PMID:31566909), phosphatase-stabilized pSer3-CFL1:total CFL1 assays, and orthogonal variance proof beyond NfL and pNfH."
                )
            elif pid == "DN-15":
                proves = "Bye 2025 iPSC-MN screen Rank #13/107 at 2.5 uM (+0.8992d across 16 sALS lines, nominal p=0.0143, sub-FDR q_BH=0.0695) and presynaptic Na+ channel hyperexcitability rationale."
                disproves = "Although Eisen et al. 1993 (PMID:7906190, 100 mg/d, N=67, D=12 deaths) was individually underpowered for survival, high-dose Ryberg et al. 2003 (PMID:12807386, 300 mg/d paired double-blind crossover, N=30 with serial LPs achieving ~7-15 uM unbound CSF = 3-6x screen) directly falsified living-ALS CSF glutamate/aspartate/BCAA reduction and clinical benefit (0/4 scales), reinforced by oral NaV pore-blocker ALS progression futility (mexiletine PMID:26911633 N=60; flecainide FANS PMID:26844270 N=54) and FDA SJS/TEN + cardiac NaV1.5 warnings."
            elif pid == "DN-16":
                proves = "Open-label Phase 2a LIGHTHOUSE safety/tolerability in unstratified sporadic ALS (NCT02868580, Gold et al. 2019 PMID:31284774, N=40 treated / 35 completers), Bye 2025 nominal 2.5 uM readout (+0.7458d, p=0.0431), and O'Neill 2025 retrotransposon-active cortical ALS-TE subtype biology."
                disproves = "Phase 3 LIGHTHOUSE II (NCT05193994, N=419, 2:1 Triumeq vs placebo in unstratified ALS) stopped early at planned interim analysis for survival futility (announced 2025-04-05; registry completion 2025-06-30), Week-16 human unbound CSF dolutegravir (~5-32 nM; total 9.5-42.9 nM, Letendre et al. 2014 PMID:24944232) sits ~80-500x below 2.5 uM, and autonomous human LINE-1 encodes zero integrase (preserving nanomolar LINE-1 ORF2p RT inhibition in EALS-033 Censavudine)."
            elif pid == "DN-17":
                proves = "Bye 2025 iPSC-MN screen Rank #12/107 at 2.5 uM (+0.9458d across 15 sALS lines, nominal p=0.02013, Wilcoxon p=0.00671), underpowered subcutaneous NAC survival signals in Louwerse et al. 1995 (PMID:7763202, 50 mg/kg/d SC, N=110: overall HR=0.74 [95% CI 0.41-1.33], p=0.31; limb-onset HR=0.50 [0.24-1.04], p=0.06), and high-dose oral NAC human CSF penetration (70 mg/kg BID -> 9.26 +/- 1.62 uM CSF NAC, p<0.001, Katz et al. 2015 PMID:25765302)."
                disproves = "Misses 107-drug screen FDR (q_BH=0.09364) where 2.5 uM reactive thiol can buffer extracellular media cystine/ROS, while low-dose oral NAC (600 mg/d effervescent NAC co-administered with 1,800 mg/d EH301 [1,500 mg NR + 300 mg PTER] + riluzole in Phase 2 NCT07414212, N=90; 5.83x lower mass than 3,500 mg/d SC at 70 kg; ALSUntangled #82 PMID:41777232) undergoes ~90-94% first-pass gut/hepatic deacetylation vs neutral BBB-permeable N-acetylcysteine amide (NACA/AD4)."
            elif pid == "DN-18":
                proves = "Bye 2025 iPSC-MN screen Rank #19/107 at 2.5 uM (+0.7430d across 16 sALS lines, nominal p=0.04951) and mitochondrial Complex I-III electron-transport rationale."
                disproves = "Missed 107-drug screen FDR (q_BH=0.1827; cLogP ~19.4 colloid dispersion in lipoprotein-free media) and failed in randomized Phase II QALS (NCT00243932, Kaufmann et al. 2009 PMID:19743457, PMC2854625 Table 3, N=185 total / Stage 2 n=150 at 2,700 mg/d vs placebo): primary p=0.14 (8.80 [SD 7.34] vs 9.44 [SD 8.82]) reflected 5 Month-9 CoQ10 deaths vs 1 placebo death coded as 0 decline, prespecified death=16 sensitivity crossed formal futility (8.52 vs 8.37, p=0.025 < 0.10; 13/17 death scores futile; linear slope p=0.097), secondary endpoints were null, and oral GI absorption saturated between 1,800 and 2,700 mg/d (Table 2; PMID:16344537)."
            elif pid == "DN-19":
                proves = "Bye 2025 iPSC-MN screen Rank #20/107 at 2.5 uM (+0.7117d survival shift across 16 sALS lines, unadjusted paired p=0.04190) and uncontrolled 6-month Phase 1 safety-only tolerability up to 15 g BID (30 g/d) oral dosing (NCT01835782 N=20, Cox/Dunlop BMAA-displacement rationale PMID:27589995)."
                disproves = "Fixed 2.5 uM library addition increases L-serine molar concentration by only +0.625% atop ~400 uM basal BrainPhys/DMEM-F12 L-serine and misses 107-drug FDR (q_BH=0.17067), zero controlled sporadic ALS efficacy RCTs have completed (single-arm NCT03580616 N=43 terminated for IRB noncompliance; historical BMAA rationale remains unconfirmed in sporadic ALS), and rare (<0.5% monogenic) SPTLC1/SPTLC2 GoF variants overproduce canonical C18-C22 sphingolipids where exogenous L-serine is contraindicated (PMID:34059824; PMID:43025655; intrathecal SPTLC1 ASO LTX-002 NCT07660614)."
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
