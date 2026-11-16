"""Compile publication-grade Summary-of-Findings (SoF) prose for all 59 CarbonALS candidates from frozen registries."""
from __future__ import annotations

import re

from _candidate_contrasts_b import build_edges_and_lenses
from _candidate_hypotheses import CANDIDATE_HYPOTHESES

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
    "CAUSAL_GENETIC_AND_TDP43_CONVERGENT_FOR_YKT6_SCFD1_G2E3_PASSENGER_FOR_OTHER_5": "Split Bundle (3 Active Sub-Nodes · 5 Passengers)",
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
    "EARLY_WINDOW_HOMOCYSTEINE_METHYLATION_RESCUE": "Early-Onset (<=12m) Methylation Rescue Benchmark",
    "ENDOLYSOSOMAL_POLYGP_CLEARANCE_VS_CONTINUOUS_VACUOLATION_TOXICITY": "Endolysosomal Clearance vs. Continuous Vacuolation Toxicity",
    "HYPOTHESIS_REFUTED_IN_HUMANS": "Refuted in Powered Human ALS RCTs",
    "IATROGENIC_ANTAGONISM_OF_ESSENTIAL_SNARE_PRENYLATION": "Iatrogenic Inhibition of Essential SNARE Prenylation",
    "IN_VITRO_REDOX_BUFFERING_ARTIFACT": "Extracellular Media Thiol-Buffering Artifact",
    "SPLIT_BY_SUBNODE": "Sub-Node Split (C3/C4B Dropped · CNS C1q Exploratory)",
    "METABOLIC_HYPOTHESIS_MEDIA_CONFOUNDED_UNPROVEN": "Media-Confounded Serine Metabolic Hypothesis",
    "MICROMOLAR_CAD_PHOSPHOLIPIDOSIS_ARTIFACT": "Micromolar Cationic-Amphiphilic Phospholipidosis Artifact",
    "NON_CAUSAL_PLEIOTROPIC_MISMATCH": "Non-Causal Pleiotropic Target Mismatch",
    "NON_CAUSAL_RODENT_PROMOTER_ARTIFACT": "Non-Causal Rodent Promoter Artifact",
    "OFF_TARGET_HIGH_CONC_SCREEN_HIT": "High-Concentration Off-Target Screen Hit",
    "OFF_TARGET_MONOAMINERGIC_SEDATION_WITH_CLASS_ISR_FAILURE": "Off-Target α2-Adrenergic Sedation & Class ISR Futility",
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
    "UNSTRATIFIED_RETROELEMENT_FUTILITY_AND_CSF_PK_GAP": "Unstratified Retroelement Futility & 60–250x CSF PK Deficit",
    "UPSTREAM_COMPARTMENTAL_CASCADE_FOR_CHMP7_UNBUNDLED_MODIFIER_FOR_CHMP2B": "Nuclear-Pore Surveillance Cascade (CHMP7 Unbundled from CHMP2B)",
    "UPSTREAM_INTRINSIC_EXCITABILITY_MODULATOR": "Intrinsic Kv7.2/7.3 Excitability PD Benchmark",
}

INLINE_SWAPS = (
    ("PASS_CLEAN_GE2MM", "Clean >=2mm off-target status"),
    ("CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED", "Caution (non-constrained 1mm/wobble)"),
    ("WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL", "Warn (constrained CNS gene hit)"),
    ("FAIL_EXACT_0MM_OFFTARGET", "Fail (exact 0mm off-target)"),
    ("TIER_3_EXPLORATORY_DISCOVERY", "Tier 3 Exploratory Discovery"),
    ("KEEP_EXPLORATORY_UNPROVEN_UNBUNDLED_SECONDARY", "Keep · Exploratory (unbundled secondary)"),
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
    s = re.sub(r"\bExploreALS\s+cited\s+corrupt\s+IDs", "Chemical registry verification refuted misattributed IDs", s, flags=re.IGNORECASE)
    s = re.sub(r";\s*true IDs?\s+([A-Za-z0-9/]+),\s*fixing intake [^)]*typo", r"; \1", s, flags=re.IGNORECASE)
    s = re.sub(r",?\s*fixing (?:prior )?intake [^);]*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\bprior intake\b", "baseline annotation", s, flags=re.IGNORECASE)
    s = re.sub(r"\bnon-ExploreALS\b", "de novo", s, flags=re.IGNORECASE)
    s = re.sub(r"\bExploreALS\s+composite\s+Tier\s+1A\s*\([^)]*\)\s*", "composite ", s, flags=re.IGNORECASE)
    s = re.sub(r"\bExploreALS\b", "baseline annotation", s, flags=re.IGNORECASE)
    s = re.sub(r"\bCarbonALS\b", "ExploreALS", s, flags=re.IGNORECASE)
    s = re.sub(r"\bDS045\b|\bD045\b", "Trautwig 2025 CSF (PMC12082929)", s)
    s = re.sub(r"\bD003\b", "Pineda 2024 (PMID:38518782)", s)
    s = re.sub(r"\(\s*[0-9.]+(?:-[0-9.]+)?/100\s*\)", "", s)
    s = re.sub(r",?\s*(?:5D=)?[0-9.]+(?:-[0-9.]+)?/100\s*(?:liability)?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+in\s+EV-[A-Z0-9.\-/]+", "", s)
    s = re.sub(r"\(\s*EV-[A-Z0-9.\-/]+(?:\.\.EV-[A-Z0-9.\-/]+)?\s*\)", "", s)
    s = re.sub(r";?\s*EV-[A-Z0-9.\-/]+(?:\.\.EV-[A-Z0-9.\-/]+)?", "", s)
    for k, v in INLINE_SWAPS:
        s = s.replace(k, v)
    s = re.sub(r"\s+([.,;:\)])", r"\1", s)
    s = re.sub(r"\s{2,}", " ", s).strip()
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
    "DN-01": "Promoted as #1 unbiased TDP-43 cryptic-splicing discovery (Rank #{rk}/59 · Tier 2): convergent human Ribo-seq, C9-FTD homogenate protein loss, and in vivo Atg4b-KO acceleration justify preclinical SSO #2 rescue alongside Stage-(ii) pre-inclusion cervical alpha-MN duplex BaseScope ISH.",
    "DN-02": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry: robust C9-FTD cortical Kalirin-12/DuET cryptic splicing and clean >=2mm SSO #1 are tempered by zero ALS GWAS loci, low cervical cord expression, and alt-3'SS shunting risk.",
    "DN-03": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry: multi-cohort Ribo-seq, brain DIA, and living-CSF PTPRT depletion require 1-bp cryptic-junction mapping before steric SSO design.",
    "DN-04": "Promoted as Tier 2 neuron-specific splicing-factor lead (Rank #{rk}/59): LeafCutter cluster replication in sporadic ALS patient iPSC-MNs (padj=0.0090; nominal BA4 p=0.0133, FDR=0.136) and clean >=2mm 20-bp SSO #1 merit Exon 4–7 Nanopore RT-PCR (<1-2% LOQ Exon-5 skip / 98-bp micro-intron retention) plus Stage-(ii) cervical BaseScope ISH.",
    "DN-05": "Elevated to #1 of Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry: surviving cervical MN-niche 55-um Visium RNA (-1.23 log2FC, spot-level FDR=0.019, N=18) and C9-FTD synaptosomal PRUNE2 loss (-0.49, p=0.0068) warrant Nanopore RT-PCR and Stage-(ii) cervical BaseScope ISH to resolve microexon vs. cryptic 5'SS polarity.",
    "DN-06": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry: synaptosomal PFKP depletion and clean >=2mm SSO #1 require metabolic flux gating to rule out pentose-phosphate NADPH/GSH depletion.",
    "DN-07": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry: pathology-selective TRAPPC12 intronic polyadenylation and sALS iPSC-MN splicing merit isoform-resolved testing despite null bulk cortical DIA.",
    "DN-08": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry while retiring nuclear RNase-H1 gapmers (which risk Pol II readthrough cleavage of canonical ELK1, PMID:31924448) in favor of steric distal-PAS SSO or cytoplasmic 3'-extension siRNA gating.",
    "DN-09": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry: pathology-selective DLGAP1 cryptic polyadenylation and cortical synaptosomal scaffold loss require spinal motor-neuron penetrance verification.",
    "DN-10": "Reclassified as a non-therapeutic Somatodendritic Attrition Biomarker (Rank #{rk}/59): living-CSF and synaptosomal DPP6 depletion tracks Kv4.2 membrane loss rather than a catalytically druggable driver.",
    "DN-11": "Reclassified as a non-therapeutic Somatodendritic Attrition Biomarker (Rank #{rk}/59): living-CSF and motor-cortex DPP10 reduction parallels paralogous DPP6 loss without sporadic-vs-control TMTpro specificity.",
    "DN-12": "Reclassified as a non-therapeutic Axonal Release Biomarker (Rank #{rk}/59): cross-platform ALS CSF Cofilin-1 elevation reflects degenerating motor-axon rod release on a pan-essential cytoskeletal gene.",
    "DN-13": "Falsified in randomized human ALS clinical trials (Rank #{rk}/59 · Drop): postmortem MAOB elevation reflects reactive astrogliosis, and selective MAOB inhibition failed four controlled human ALS trials.",
    "DN-14": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry: selective C5aR1 antagonism has zero completed ALS efficacy trials despite upstream C5 failures, but C5/C5a-free monocultures make ligand-independent 2.5 uM cyclic-hexapeptide off-target activity the primary null pending C5AR1-KO deconvolution.",
    "DN-15": "Falsified in randomized human ALS clinical trials (Rank #{rk}/59 · Drop): modest in vitro iPSC-MN survival rescue is superseded by two negative placebo-controlled human ALS trials at target-engaging CSF exposure.",
    "DN-16": "Falsified in Phase 3 human ALS clinical testing (Rank #{rk}/59 · Drop): LIGHTHOUSE II interim survival futility and a 60–250x unbound human CSF exposure gap refute repurposing dolutegravir/Triumeq.",
    "DN-17": "Falsified by human ALS clinical futility and poor CNS penetration (Rank #{rk}/59 · Drop): in vitro rescue reflects media thiol buffering while high-dose subcutaneous N-acetylcysteine failed human ALS survival testing.",
    "DN-18": "Falsified in randomized human ALS clinical testing (Rank #{rk}/59 · Drop): marginal in vitro antioxidant survival gain failed to translate in the multicenter Phase II QALS trial at 2,700 mg/day.",
    "DN-19": "Retained in Tier 3 Exploratory Discovery (Rank #{rk}/59) under Epistemic Asymmetry: Phase 2 IRB termination did not test clinical efficacy in non-SPT sporadic ALS, but +0.625% basal-media noise and SPTLC1/2-ALS ceramide-feedback loss (PMID:43025655) mandate SPT exclusion and lipidomic deconvolution.",
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
            if pid == "DN-15":
                m15 = re.match(r"^Despite (.+?\)),\s*(.+)$", just)
                proves = (m15.group(1) + ".") if m15 else just
                disproves = (m15.group(2)[0].upper() + m15.group(2)[1:]) if m15 else just
            elif pid == "DN-16":
                p1, p2 = just.split(", while ", 1)
                proves = p2[0].upper() + p2[1:]
                disproves = p1 + "."
            elif pid == "DN-18":
                p1, p2 = just.split(" failed to translate ", 1)
                proves = p1 + " in sALS patient iPSC-MNs."
                disproves = "Failed to translate " + p2
            else:
                proves, disproves = _split_top_level_dn(just)
            verdict = DN_VERDICT_HEADLINES[pid].format(rk=r["unified_rank"])

        item = {
            "hyp": hyp,
            "sub": sub,
            "causal": causal_lbl,
            "verdict": verdict,
            "proves": proves,
            "disproves": disproves,
            **edges_map[pid],
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
        out[pid] = item
    return out
