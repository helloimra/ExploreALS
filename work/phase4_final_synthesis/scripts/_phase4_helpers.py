"""Deterministic helpers for Phase 4 unified 59-candidate portfolio & 26-interval cis-regulatory synthesis."""
from __future__ import annotations

import hashlib
from pathlib import Path

PROMOTED_LEADS: dict[str, tuple[int, str]] = {
    "C006": (3, "chr20:63442302-63442319(-)"),
    "C001": (2, "chr19:17642537-17642554(-)"),
    "C002": (2, "chr8:79616829-79616846(+)"),
    "DN-01": (2, "chr2:241668970-241668987(+)"),
    "DN-02": (1, "chr3:124701092-124701109(+)"),
    "DN-04": (1, "chr19:3278299-3278318(+)"),
    "DN-06": (1, "chr10:3099792-3099811(+)"),
    "DN-07": (1, "chr2:3457774-3457793(+)"),
    "DN-08": (1, "chrX:47631681-47631698(-)"),
    "DN-09": (1, "chr18:4147659-4147676(-)"),
}

TIER_ORDER = {
    "TIER_1_ACTIONABLE_NOW": 1,
    "TIER_2_FOCUSED_GATE_FIRST": 2,
    "TIER_3_EXPLORATORY_DISCOVERY": 3,
    "COMPANION_PROTOCOL_ONLY": 4,
    "BIOMARKER_BENCHMARK_ONLY": 5,
    "DROPPED_FALSIFIED_EXCLUDED": 6,
}

EVIDENCE_BASIS_ORDER = {
    "MEASURED_HUMAN_GENETICS_AND_PATHOLOGY": 1,
    "MEASURED_HUMAN_TDP43_PATHOLOGY_AND_RESCUE": 2,
    "MEASURED_HUMAN_RCT_SUBGROUP": 3,
    "MEASURED_C9FTD_FRACTION_PROTEOMICS": 4,
    "MEASURED_HUMAN_SPATIAL_OR_SNRNA": 4,
    "MEASURED_HUMAN_CSF_PROTEOMICS": 5,
    "MEASURED_HUMAN_PK_AND_IPSC_SCREEN": 6,
    "PROTOCOL_STAGE_GATING_ONLY": 7,
}

# Pure empirical human ALS causal biology order (zero crowding, zero TRL, zero 21 CFR 300.50, zero Tm/dG/AVI priors)
BIO_EVIDENCE_PRIORITY: list[str] = [
    "C001", "C002", "S06", "C006", "S07", "DN-01", "BA9-04", "C015",
    "DN-04", "DN-05", "C014", "C007", "DN-09", "DN-03", "DN-06",
    "DN-07", "DN-02", "DN-08", "S09", "C018", "BA9-08", "C016",
    "C019", "C020", "S02", "DN-14", "DN-19",
    "C005",
    "C013", "S08", "C003", "C017", "DN-10", "DN-11", "DN-12",
]

CROWDING_CLASS_MAP: dict[str, str] = {
    "S06": "Allosteric Open (2 Ph1 Orthosteric)",
    "C006": "Whitespace (0 ASO Trials)",
    "S07": "Biomarker-Gated Whitespace",
    "C001": "Crowded 1-Plex (4 Ph1/2 Trials)",
    "C002": "Crowded 1-Plex (2 Ph1/2 Trials)",
    "C007": "Whitespace (0 CNS Trials)",
    "DN-01": "Whitespace (0 ALS Trials)",
    "DN-04": "Whitespace (0 ALS Trials)",
    "DN-05": "Whitespace (0 ALS Trials)",
    "BA9-04": "Whitespace (0 ALS Trials)",
    "C015": "Whitespace (0 Ligands)",
    "C014": "Whitespace (0 Ligands)",
    "S09": "1 Ph2a C9 Trial (NCT04993755)",
    "C018": "CNS IT Open (IV C3 Failed)",
    "C019": "Open-Label Ph2 PK (NCT05189106)",
    "C020": "Pulsed Hypothesis (BID Failed)",
    "S02": "Discontinued (Ph2/3 Unreported)",
    "C005": "N/A (Companion Protocol)",
    "C013": "N/A (SOC / PD Benchmark)",
    "S08": "N/A (SOC / PD Benchmark)",
    "C003": "N/A (SOC / PD Benchmark)",
    "C017": "N/A (Fluid Biomarker)",
    "DN-10": "N/A (Fluid Biomarker)",
    "DN-11": "N/A (Fluid Biomarker)",
    "DN-12": "N/A (Fluid Biomarker)",
}

EXPLORE_BENCHMARK_SPECS: dict[str, tuple[str, str, str, str, int, str]] = {
    "C013": ("BENCHMARK_DRUG", "Oral_Riluzole_50mg_BID_NaV1_6_Persistent_INaP_Positive_Benchmark", "CLINICAL_PROTOCOL_STANDARDIZATION", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", 0, "NONE"),
    "S08": ("BENCHMARK_DRUG", "Intramuscular_50mg_Methylcobalamin_Early_Onset_LE12m_SOC_Benchmark", "CLINICAL_PROTOCOL_STANDARDIZATION", "MEASURED_HUMAN_RCT_SUBGROUP", 0, "NONE"),
    "C003": ("BENCHMARK_DRUG", "Withdrawn_Ezogabine_Kv7_2_7_3_Cortical_TMS_SICI_and_SDTC_PD_Calibrator", "CLINICAL_PROTOCOL_STANDARDIZATION", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", 0, "NONE"),
    "C017": ("BIOMARKER_CSF", "Living_CSF_rs3831317_Adjusted_CHIT1_GPNMB_CHI3L1_CHI3L2_Staging_and_Glia_Panel", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE", "MEASURED_HUMAN_CSF_PROTEOMICS", 1, "PROSPECTIVE_LONGITUDINAL_PD_SLOPE_CALIBRATION_UNDER_RS3831317_GENOTYPING"),
}

PHASE3A_NEXT_TEST_OVERRIDES: dict[str, str] = {
    "C006": (
        "Stage 1 single-entity intrathecal 2'-O-MOE mixed-PO/PS 5-MeC dense (>=50-oligo 1-nt-stepped 18-22 nt) Intron-4/Exon-5/Intron-5 exon-inclusion micro-walk "
        "across BOTH graded (30%/60%/90%) TDP-43-CRISPRi human iPSC-MNs AND TDP-43-intact WT human neurons (PV+ cortical interneurons [DEE7 seizure guard], oculomotor MNs, and primary human DRGs), "
        "anchoring non-UG #3 chr20:63442302-63442319(-) (UG=1, modeled Tm~53C, 0/18 splicing AVI = Cactus/DNASE conservation only, testing putative ISS vs wrong-sign ISE; CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED) against WT-TDP-43 cis-eviction-gated #1 Intron-4 UG8 chr20:63442595-63442616(-) "
        "(CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED; deprioritizing #2 chr20:63442565-63442582(-) due to PTCH1 1-nt bulge WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL) "
        "with Ca2+/Mg2+-formulated Ca2+-oscillation/TLR9 acute neurotox counter-screening against Kv7 openers (PDB 7CR2 Trp236 surface-density ceiling), NHP cervical (C3-C5 phrenic) & BA4 Betz splice-rescue EC80 bridging, and C005 cortical TMS SICI + axonal SDTC + CSF NPTX2 target engagement before unvalidated 24-48 mg Stage 2 genotype-stratified 2-plex vs 3-plex uptake competition & 21 CFR 300.50 GLP IT tox."
    ),
    "C001": (
        "Advance promoted clean lead UNC13A #2 chr19:17642537-17642554(-) (PASS_CLEAN_GE2MM; superseding #1 chr19:17642546-17642563(-) CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED) "
        "through sponsor-owned Stage 1 single-entity GLP IT tox, NHP cervical (C3-C5 phrenic) + BA4 Betz splice-rescue EC80 bridging (>30% Munc13-1 synaptic rescue threshold per Keuss et al. 2026 Nature 10.1038/s41586-026-11256-2; no right of reference to LY4256984/TRCN-1023), and 3-layer Phase 1b PK/TE/PD "
        "(strand-specific CSF PK, L1CAM+/ATP1A3+ neuron-derived EV pre-amplified dPCR/Nanopore enrichment + CSF synaptic secretome NPTX2/VGF/SNAP25 TE, and >=16-24 wk post-loading downstream CSF pNfH/NfL PD accounting for ANQUR NCT05633459 low-vs-10mg pNfH dissociation; unfractionated CSF EVs sit at qPCR Cq>35 / <3-10 copies/mL ddPCR LOQ, PMID:38158550), "
        "followed by Stage 2 genotype-stratified 2-plex vs 3-plex randomization across rs12973192/rs12608932 genotypes (since UNC13A rescue leaves STMN2 and KCNQ2 mis-spliced; 24-48 mg unvalidated multiplex scenario gated on Ca2+/Mg2+ chelation, DRG, TLR9, and <1-2% endosomal-escape competition beyond single-agent DEVOTE 50 mg nusinersen PMID:41634391)."
    ),
    "C002": (
        "Advance promoted clean lead STMN2 #2 chr8:79616829-79616846(+) (PASS_CLEAN_GE2MM, modeled Tm_phys~64C; superseding #1 chr8:79616819-79616836(+) CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED) "
        "through sponsor-owned Stage 1 single-entity GLP IT tox, NHP cervical (C3-C5) + BA4 Betz full-length vs polyadenylated tSTMN2 EC80 bridging, and 3-layer Phase 1b PK/TE/PD "
        "(strand-specific CSF PK, L1CAM+/ATP1A3+ neuron-derived EV [NDEV] pre-amplified tSTMN2 dPCR/Nanopore + ultrasensitive soluble SCG10 assay TE, and >=16-24 wk post-loading downstream CSF pNfH/NfL PD accounting for sponsor-reported interim QRL-201 ANQUR NCT05633459 ~46% low-dose vs ~5% 10mg pNfH dissociation), "
        "then gate Stage 2 genotype-stratified 24-48 mg 2-plex vs 3-plex uptake/Ca2+/DRG safety (unvalidated scenario beyond single-agent DEVOTE PMID:41634391) and parallel oral SARM1 T-lock combination (Bliss/Loewe additivity vs illustrative ~2-7x MWC sensitivity scenario; Krus et al. 2022 PMID:35767949)."
    ),
    "S07": (
        "Complete Stage-0 paired analytical bridging from MIROCALS BioVendor ELISA CSF pNfH to automated CLIA immunoassays (Ella/Euroimmun/Simoa) plus paired NfL vs pNfH immunoassay calibration on banked ALS CSF "
        "(motivated by weak tryptic MS NEFL vs NEFH correlation r=0.278 across n=77 DIA / n=51 overlapping Emory TMT in Trautwig 2025 PMC12082929), then execute an event-driven biomarker-enriched Phase 3 ALS survival RCT "
        "powered for 247 deaths at conservative HR=0.70 (138 at HR=0.62; requiring N~650-750 over 36-42 mo variable follow-up or N~850-1,050 at 24 mo, <5% vital-status censoring) enrolling calibrated baseline CSF pNfH <=3,700 pg/mL alongside longitudinal Treg-specific demethylated region (TSDR, PMID:17694575), CD56bright NK/eosinophil sink, and monomeric sCD25 (PMID:22343569) monitoring."
    ),
    "BA9-04": (
        "Quantify cytosolic DNAJB2a vs Intron-9-retaining ER-prenylated DNAJB2b precursor ratios by targeted PRM/RT-ddPCR in sporadic ALS vs control human spinal cord "
        "(beyond n=10 C9-FTD frontal cortex; gating zero-sum ERAD DNAJB2b depletion risk), benchmark exogenous cytosolic DNAJB2a CAP-B10 AAV/mRNA replacement (ENST00000392086.8, 277 aa, Exon 10 chr2:219285987-219286898(+)) directly against a tiled 2'-O-MOE SSO micro-walk across unmapped 1,151-bp GENCODE v46 Intron 9 chr2:219284836-219285986(+) "
        "(testing putative ISS silencers vs wrong-sign ISE enhancers) with BiP/HSPA5 + CHOP/DDIT3 ER-stress counter-screens in sALS iPSC-MN/oligo co-cultures."
    ),
    "C015": (
        "Exclude G2E3 from 3-plex SSO (#1 chr14:30563747-30563764(+) & #2 chr14:30563930-30563947(+) FAIL_EXACT_0MM_OFFTARGET; "
        "#3 chr14:30563939-30563956(+) WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL ELOC); execute allele-split 19F-NMR/DSF <=160 Da ternary "
        "fragment screening for rare (<0.1%) YKT6 p.Tyr64Cys vs exterior Longin stabilizers/14q12 CRISPRi in >99.9% WT sALS."
    ),
    "C018": (
        "Engineer ECM-anchored half-life-extended intrathecal anti-C1q Fab/nanobody or intrathecal microglial C1QA/B ASO/di-siRNA "
        "(rejecting IV BBB-shuttled IgG due to 180 nM serum C1q sink and unmodified q4w IT Fab due to modeled <0.001 nM Day-28 CSF trough), "
        "and gate on preserved C-bouton/neuronal RNP homeostasis in adult spinal cord models given SOD1 C1qa-KO survival null."
    ),
    "C019": (
        "Resolve the JAK1-vs-neuronal-JAK2 catch-22 at clinically reachable unbound human CSF concentrations (3.8-50 nM; modeled ~8.7% whole-cell pSTAT occupancy at 4 mg vs 2,500 nM screen) by testing Kp,uu-verified JAK2-sparing "
        "selective JAK1 JH1 inhibitors vs Baricitinib comparator and CRISPRi JAK1/JAK2/AAK1 knockdowns across BOTH glia-free sALS iPSC-MNs & reactive ALS-Glia co-cultures, plus bridged pg/mL immunoassay calibration of the "
        "rs3831317-neutral CSF Glial Bridge (Trautwig sALS-vs-Ctrl out-of-fold cross-validated [OOF] AUC=0.8188, MGH-adj AUC=0.885; distinct from NYGC ALS-Glia subtype AUC=0.72-0.79 and Thompson 2019 PMID:30737180 mimic AUC=0.51-0.92 [0.688 ext]) before any VTE-prophylaxed Phase 2 interaction RCT."
    ),
    "C020": (
        "Execute a strict 14-day postmitotic human C9orf72 and sALS iPSC-MN vacuole and conjugation-of-ATG8-to-single-membranes (CASM) washout half-life kill-gate under intermittent q48h-q72h nanomolar Apilimod "
        "(modeled 6.5-8.0 nM unbound Cmax window fails if repair tau >=72h), pairing intracellular vs conditioned-media secreted poly(GP)/pTDP-43 mass-balance (PMID:27732842) and microfluidic fast axonal transport kymography with <5% ClC-7 vacuolation (PMID:42900584) and zero NfL/GFAP surge before any pulsed Phase 1b."
    ),
}


def sha12(fp: Path) -> str:
    return hashlib.sha256(fp.read_bytes()).hexdigest()[:12]


def classify_explore_type(cid: str, intake_row: dict[str, str], dec: str) -> str:
    if cid in EXPLORE_BENCHMARK_SPECS:
        return EXPLORE_BENCHMARK_SPECS[cid][0]
    if cid == "C005":
        return "COMPANION_PROTOCOL"
    if cid in {"C001", "C002", "C006", "BA9-04"}:
        return "GENE_CIS_SPLICE"
    if cid == "C007":
        return "GENE_CIS_APA"
    if intake_row["track"] == "A":
        return "DRUG_REPURPOSING"
    return "GENE_DRUG_AXIS"


def classify_explore_drop_basis(cid: str, intake_row: dict[str, str], epi: str) -> tuple[str, str]:
    if epi == "ARTIFACT_CONFOUNDED":
        return (f"Dropped_Confounded_Postmortem_Transcriptomic_Target_{intake_row['name']}", "MEASURED_HUMAN_SPATIAL_OR_SNRNA")
    if cid in {"C004", "C008", "C009", "C012"}:
        return (f"Dropped_Failed_Human_ALS_Clinical_Regimen_{intake_row['name'].split()[0]}", "MEASURED_HUMAN_RCT_SUBGROUP")
    return (f"Dropped_PK_or_Safety_Infeasible_Regimen_{intake_row['name'].split()[0]}", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN")


def biological_evidence_sort_key(row: dict[str, str]) -> tuple:
    pid = row["portfolio_id"]
    if pid in BIO_EVIDENCE_PRIORITY:
        return (0, BIO_EVIDENCE_PRIORITY.index(pid), int(row["unified_rank"]))
    epi_order = {"FALSIFIED_CLINICAL": 1, "FALSIFIED_PK_SAFETY": 2, "ARTIFACT_CONFOUNDED": 3}
    return (1, epi_order.get(row["epistemic_state"], 9), int(row["unified_rank"]))


def portfolio_sort_key(row: dict[str, str], p3a_rank_map: dict[str, int], dn_idx_map: dict[str, int]) -> tuple:
    t_ord = TIER_ORDER[row["scientific_actionability_tier"]]
    pid = row["portfolio_id"]
    is_non_core = 0 if row["decision"] == "KEEP_CORE" else 1
    ev_ord = EVIDENCE_BASIS_ORDER.get(row["primary_evidence_basis"], 9)
    src_ord = p3a_rank_map.get(pid, 100 + dn_idx_map.get(pid, 99))
    if t_ord == 1:
        return (t_ord, is_non_core, p3a_rank_map[pid], 0, 0, 0, 0, pid)
    if t_ord == 2:
        h_cnt = int(row["unsolved_hurdle_count"])
        return (t_ord, is_non_core, h_cnt, ev_ord, src_ord, 0, 0, pid)
    if t_ord == 3:
        h_cnt = int(row["unsolved_hurdle_count"])
        is_screen_rep = 1 if row["primary_evidence_basis"] == "MEASURED_HUMAN_PK_AND_IPSC_SCREEN" else 0
        is_sub_fdr_screen = 1 if pid in {"DN-14", "DN-19"} else 0
        is_spinal_mn_cryptic = 0 if pid == "DN-05" else 1
        is_cis_target = 0 if row["candidate_type"] in {"GENE_CIS_SPLICE", "GENE_CIS_APA"} else 1
        return (t_ord, is_screen_rep, is_sub_fdr_screen, h_cnt, is_spinal_mn_cryptic, is_cis_target, ev_ord, src_ord, pid)
    if t_ord == 4:
        return (t_ord, 0, 0, 0, 0, 0, 0, pid)
    if t_ord == 5:
        bm_order = {"C013": 1, "S08": 2, "C003": 3, "C017": 4, "DN-10": 5, "DN-11": 6, "DN-12": 7}
        return (t_ord, bm_order.get(pid, 99), 0, 0, 0, 0, 0, pid)
    epi_order = {"FALSIFIED_CLINICAL": 1, "FALSIFIED_PK_SAFETY": 2, "ARTIFACT_CONFOUNDED": 3}
    return (t_ord, epi_order.get(row["epistemic_state"], 9), 0 if row["origin_phase"] == "EXPLORE_INHERITED_40" else 1, 0, 0, 0, 0, pid)
