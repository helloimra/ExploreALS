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
    "MEASURED_HUMAN_PK_AND_SAFETY": 6,
    "PROTOCOL_STAGE_GATING_ONLY": 7,
}

DROP_MODEL_PRIOR_MAP: dict[str, str] = {
    "C013": "COARSE_PRIOR_ONLY:Pgp_BCRP_effluxed_Kpuu_le_1_unbound_human_CNS_peak_15_to_30nM_from_NDA020599_Cu_plasma_22.2_to_29.6nM",
    "C009": "COARSE_PRIOR_ONLY:Modeled_Kpuu_0.65_on_FDA_fup_0.05_to_0.11",
    "C011": "COARSE_PRIOR_ONLY:OAT3_MRP4_efflux_Kpuu_lt_0.05_on_NDA016273_fup",
    "C021": "COARSE_PRIOR_ONLY:Modeled_fup_and_Kpuu_beyond_measured_35.2_to_61.0nM_total_plasma_Cmax",
    "S03": "COARSE_PRIOR_ONLY:Anionic_MPA_efflux_Kpuu_on_NDA050722_fup_0.03",
    "S04": "COARSE_PRIOR_ONLY:Passive_Kpuu_le_1_and_CAD_lysosomal_partitioning_on_NDA021807_fup",
    "S05": "COARSE_PRIOR_ONLY:Pgp_attenuated_Kpuu_on_NDA213969_fup_le_0.01",
}

# Curated editorial biological-evidence priority list across non-dropped entries (human genetics/pathology > multi-omic > CSF > screen)
BIO_EVIDENCE_PRIORITY: list[str] = [
    "C001", "C002", "S06", "C006", "S07", "DN-01", "C022", "C023", "C015",
    "DN-04", "DN-05", "C014", "C007", "DN-02", "DN-03", "DN-09",
    "DN-08", "DN-07", "DN-06", "S09", "C018", "C016",
    "C019", "C020", "S02", "DN-14", "DN-17", "DN-19",
    "C005",
    "C013", "S08", "C003", "C017", "DN-10", "DN-11", "DN-12",
]

CROWDING_CLASS_MAP: dict[str, str] = {
    "S06": "3 Ph1/2 Trials (2 Orthosteric · 1 Allosteric SIR2501)",
    "C006": "0 ASO Trials (2 Kv7 Openers)",
    "S07": "Ph3 Stratum Open (pNfH-Gated)",
    "C001": "2 Clinical Assets (4 Registry Protocols)",
    "C002": "Pivotal IND + Ph1/2 Active",
    "C007": "0 CNS Trials",
    "DN-01": "0 Active ALS Trials",
    "DN-04": "0 Active ALS Trials",
    "DN-05": "0 Active ALS Trials",
    "C022": "0 Active ALS Trials",
    "C015": "0 Clinical Ligands",
    "C023": "0 Clinical Ligands",
    "C014": "0 Clinical Ligands",
    "S09": "HEALEY Ph2/3 Selected (Ph2a C9 NCT04993755)",
    "C018": "CNS IT Open (IV C3 Failed)",
    "C019": "Open-Label Ph2 PK (NCT05189106)",
    "C020": "Pulsed Hypothesis (QD/BID Failed)",
    "S02": "Discontinued (Ph2/3 Unreported)",
    "DN-14": "Ph1a/1b SC Completed (ACTRN12622000927729)",
    "DN-17": "1 Combo Ph2 (NAC+EH301 NCT07414212)",
    "DN-19": "0 Controlled sALS Trials",
    "C005": "N/A (Functional Calibrator)",
    "C013": "N/A (SOC / PD Benchmark)",
    "S08": "N/A (SOC / PD Benchmark)",
    "C003": "Withdrawn (QRL-101 6 Ph1s Active)",
    "C017": "N/A (Validated CSF Staging Panel)",
    "DN-10": "N/A (Candidate CSF Marker)",
    "DN-11": "N/A (Candidate CSF Marker)",
    "DN-12": "N/A (Candidate CSF Marker)",
}

EXPLORE_BENCHMARK_SPECS: dict[str, tuple[str, str, str, str, int, str]] = {
    "C013": ("BENCHMARK_DRUG", "Oral_Riluzole_50mg_BID_NaV1_6_Persistent_INaP_Positive_Benchmark", "CLINICAL_PROTOCOL_STANDARDIZATION", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", 0, "NONE"),
    "S08": ("BENCHMARK_DRUG", "Intramuscular_50mg_Methylcobalamin_Rozebalamin_Japan_MHLW_SOC_Benchmark", "CLINICAL_PROTOCOL_STANDARDIZATION", "MEASURED_HUMAN_RCT_SUBGROUP", 0, "NONE"),
    "C003": ("BENCHMARK_DRUG", "Withdrawn_Ezogabine_Kv7_2_7_3_Cortical_TMS_SICI_and_SDTC_PD_Calibrator", "CLINICAL_PROTOCOL_STANDARDIZATION", "MEASURED_HUMAN_PK_AND_IPSC_SCREEN", 0, "NONE"),
    "C017": ("BIOMARKER_CSF", "Living_CSF_rs3831317_Adjusted_CHIT1_GPNMB_CHI3L1_CHI3L2_Staging_and_Glia_Panel", "TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE", "MEASURED_HUMAN_CSF_PROTEOMICS", 1, "PROSPECTIVE_LONGITUDINAL_PD_SLOPE_CALIBRATION_UNDER_RS3831317_GENOTYPING"),
}

PHASE3A_NEXT_TEST_OVERRIDES: dict[str, str] = {
    "C006": (
        "(1) Execute a dense (>=50-oligo 1-nt-stepped 18-22 nt) Stage 1 Intron-4/Exon-5/Intron-5 2'-O-MOE mixed-PO/PS exon-inclusion microwalk across graded (30%/60%/90%) TDP-43-CRISPRi human iPSC-MNs and TDP-43-intact WT neurons (PV+ cortical interneurons [DEE7 guard], oculomotor MNs, primary human DRGs), testing non-UG #3 chr20:63442302-63442319(-) (UG=1, modeled Tm~53C, 0/18 splicing AVI = Cactus/DNASE conservation; [MODEL_PRIOR] signed AlphaGenome 63442302:C>G increases Exon 4-6 skipping +35.2% [+0.1930] vs #2 Intron-4 UG -0.0522, directly testing putative ISS vs wrong-sign ISE hazard; CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED) against #1 Intron-4 UG8 chr20:63442595-63442616(-) (CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED; WT TDP-43 cis-eviction guard; #2 chr20:63442565-63442582(-) deprioritized due to PTCH1 1-nt bulge WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL); "
        "(2) Pair Ca2+/Mg2+-formulated Ca2+-oscillation/TLR9/DRG acute neurotox counter-screens against Kv7 openers (PDB 7CR2 Trp236 surface-density ceiling) with NHP cervical (C3-C5 phrenic) and motor-cortex (BA4 Betz) biodistribution/EC80 bridging (explicitly testing whether <=3 mg lumbar IT reaches BA4 Layer V against caudorostral dilution) and ICH M3(R2) single-entity GLP IT tox; "
        "(3) Gate Stage 2 21 CFR 300.50 genotype-stratified 2-plex vs 3-plex testing on C005 cortical TMS SICI (<=5.5% RMT, PMID:42592079) + axonal SDTC + CSF NPTX2 target engagement and a multiplex polyanion/DRG margin target of EC80<=3 mg/strand (6 mg 2-plex to 9.0 mg 3-plex Q8W-Q12W, calibrated to ANQUR 3 mg vs 10 mg pNfH dissociation while noting single-agent nusinersen 12-50 mg PMID:41634391 & tofersen 100 mg PMID:36129998 tolerate higher single-ASO IT masses and reclassifying unvalidated 24-48 mg 3-plex loads as a radiculotoxicity hazard)."
    ),
    "C001": (
        "(1) Advance promoted clean lead UNC13A #2 chr19:17642537-17642554(-) (PASS_CLEAN_GE2MM; superseding #1 chr19:17642546-17642563(-) CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED, verifying zero cryptic shunting to the 50-bp upstream 178-bp 3'SS chr19:17642591 PMID:35197626) through sponsor-owned ICH M3(R2) single-entity GLP IT tox and NHP cervical (C3-C5 phrenic) + BA4 Betz splice-rescue EC80 bridging (>30% Munc13-1 synaptic threshold per Keuss et al. 2026 Nature PMID:43015463, 10.1038/s41586-026-11256-2, accounting for persistent TDP-43 Intron-31 retention dPSI=+0.3543 [FDR=1.82e-15] yielding ~58.3-61.6% Control-normalized WT mRNA ceiling [46.1-55.6% raw KD PSI]; testing <=3 mg lumbar-to-BA4 rostral delivery; zero 21 CFR 312.23(b) right of reference to LY4256984/TRCN-1023); "
        "(2) Validate 3-layer Phase 1b PK/TE/PD: strand-specific CSF PK, L1CAM+/ATP1A3+ neuron-derived EV pre-amplified dPCR/Nanopore (adhering to ISEV CSF EV reproducibility controls PMID:38158550, since unfractionated CSF EVs sit in a low-copy Poisson-limited late-Cq regime) + CSF synaptic secretome (NPTX2/VGF/SNAP25) TE, and >=16-24 wk post-loading CSF pNfH/NfL PD (accounting for ANQUR NCT05633459 completed DRF 3 mg -46% vs baseline & 10 mg ~5% CSF pNfH dissociation plus ongoing OLE Day-421 10 mg->3 mg -36% plasma NfL washout/lag ahead of pivotal CONQUR); "
        "(3) Execute Stage 2 21 CFR 300.50 genotype-stratified 2-plex vs 3-plex testing across rs12973192/rs12608932 genotypes (targeting a multiplex polyanion/DRG margin of EC80<=3 mg/strand = 6-9.0 mg total Q8W-Q12W vs unvalidated 24-48 mg polyanion hazard, while noting single-agent nusinersen 12-50 mg PMID:41634391 & tofersen 100 mg PMID:36129998 precedents and <1-2% endosomal-escape competition)."
    ),
    "C002": (
        "(1) Advance promoted clean lead STMN2 #2 chr8:79616829-79616846(+) (PASS_CLEAN_GE2MM, +8..+25 bp epistatically suppressing cryptic 3'SS & premature polyadenylation per Baughn et al. 2023 PMID:36927019, modeled Tm_phys~64C; superseding #1 chr8:79616819-79616836(+) CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED) through sponsor-owned ICH M3(R2) single-entity GLP IT tox and NHP cervical (C3-C5) + BA4 Betz full-length vs polyadenylated tSTMN2 EC80 bridging (evaluating <=3 mg lumbar-to-BA4 rostral delivery; zero 21 CFR 312.23(b) right of reference to QRL-201/BIIB147); "
        "(2) Validate 3-layer Phase 1b PK/TE/PD: strand-specific CSF PK, L1CAM+/ATP1A3+ NDEV pre-amplified tSTMN2 dPCR/Nanopore + ultrasensitive soluble SCG10 TE, and >=16-24 wk post-loading CSF pNfH/NfL PD (accounting for QRL-201 ANQUR NCT05633459 completed N=52 DRF 3 mg Day-197 -46% vs baseline & 10 mg ~5% CSF pNfH dissociation plus ongoing N=41 OLE Day-421 10 mg->3 mg -36% vs baseline plasma NfL down-dosing washout, remodeling lag & 41/52 attrition confounders ahead of pivotal CONQUR IND); "
        "(3) Gate Stage 2 21 CFR 300.50 genotype-stratified 2-plex vs 3-plex uptake/Ca2+/DRG safety (multiplex polyanion/DRG margin target EC80<=3 mg/strand = 6-9.0 mg total vs unvalidated 24-48 mg hazard, noting single-agent Spinraza 12-50 mg PMID:41634391 & Tofersen 100 mg PMID:36129998 precedents) and parallel oral SARM1 T-lock combination (bracketing 1.0x parallel Bliss survival additivity per Krus 2022 PMID:35767949 & Matson & Holzbaur 2026 10.64898/2026.11.07.764673 [PREPRINT] to ~2-7x [med ~3x] NMNAT2-transport-coupled MWC bounds per Beccari 2025 PMID:40392845 [MODEL_PRIOR])."
    ),
    "S07": (
        "(1) Complete pre-Phase-3 CLSI EP09c (N>=40 paired ALS CSFs spanning the measuring interval) Passing-Bablok analytical bridging from MIROCALS BioVendor ELISA CSF pNfH (~79th percentile, <=3,700 pg/mL visually defined from baseline distribution blinded to survival: n=173/220 [78.6% LP / 173/304 = 56.9% screened; n=19 <750 LLOQ with 0 deaths + n=154 750-3,700 HR=0.52 p=0.016], pooled HR=0.57 p=0.037 vs >3,700 n=47 [33/90 deaths] HR=1.37 p=0.38; unadjusted ITT HR=0.81 p=0.33, continuous interaction p=0.0011, ALSFRS-R slope interaction F=3.95 p=0.048, PMID:40354799) to automated CLIA immunoassays (Ella/Euroimmun/Simoa/MSD; resolving ~1.8x-4.5x inter-platform calibrator offsets, PMID:31251725, PMID:29054919; cf. MSD ECLIA cited in Al Khleifat et al. 2026 J Neurol PMID:42836993 where TRICALS shares r^2=12.7% with CSF pNfH and nested pNfH x trt dChi2=14.24 vs TRICALS x trt dChi2=4.76), plus paired immunoassay validation before substituting blood NfL or pNfH for CSF pNfH (noting Trautwig 2025 PMC12082929 tryptic CSF MS NEFL-NEFH r=0.278 across n=77 DIA / n=51 overlapping Emory TMT vs clinical immunoassay serum NfL-CSF pNfH rho=0.64-0.71 PMID:38683209 and serum NfL outperforming serum pNfH on ALSFRS-R slope PMID:32385188; post-hoc NX210c SEALS NCT06365216 NfL<=95 pg/mL p=0.062); "
        "(2) Treat Phase 2/3 ALSTARS (NCT07161999, N=137 enrolled, prospectively stratified across 3 baseline serum NfL tiers on 24-wk ALSFRS-R) as mechanistically distinct because COYA 302 pairs 1 MIU rhIL-2 with 125 mg CTLA4-Ig (q14d synchronous Regimen 2 PMID:38915796 vs q28d staggered Regimen 1; <0.5% BBB entry, CD28 blockade PMID:30683697/PMID:36920087 vs IL-2 STAT5 rescue PMID:42086904; note MIROCALS sustained Day-112 trough Tregs p<0.0001 and plasma CCL2 p<0.05 [p<0.0001 at Days 8 & 120] across a 23-d IL-2-free cycle) without baseline CSF pNfH exclusion or a single-agent IL-2 comparator arm; "
        "(3) Execute an event-driven biomarker-enriched Phase 3 ALS survival RCT powered for 247 deaths at assumed true HR=0.70 (80% two-sided alpha=0.05 superiority power, critical boundary HR_crit=0.779 [50% probability of observed HR<=0.70 at true HR=0.70]; 138 deaths at HR=0.62 [MODEL_PRIOR]; N~650-750 over 36-42 mo variable follow-up or N~850-1,050 at 24 mo, <5% vital-status censoring, accounting for 0 deaths in <750 pg/mL n=19/220 MIROCALS LLOQ floor and pre-specifying complementary TRICALS + log[CSF pNfH] covariates — whereas hypothetical unbridged 1.8x-4.5x lower-reading CSF cutoffs admit 74-99% of >3,700 pg/mL patients and reduce 247-death one-sided superiority power to ~43-50% if HR_high=1.00 or ~14-23% if HR_high=1.37 [MODEL_PRIOR]) with longitudinal Treg TSDR (PMID:17694575), CD56bright NK, and serum sCD25 (PMID:32651161; PMID:22343569) monitoring."
    ),
    "C022": (
        "(1) Quantify cytosolic DNAJB2a vs Intron-9-retaining ER-prenylated DNAJB2b precursor ratios by targeted PRM/RT-ddPCR in sporadic ALS vs control human spinal cord (beyond n=10 C9-FTD frontal cortex; 0/6 TDP-43 cryptic/APA events and 25/25 shared-exon ClinVar P/LP vs 0/25 in Zone A; gating zero-sum ERAD DNAJB2b depletion risk); "
        "(2) Benchmark intrathecal pan-CNS/oligodendrocyte-tropic AAV-DNAJB2a cDNA replacement (ENST00000392086.8, 277 aa, cellular HSJ1a precedent PMID:26936937; rodent Ly6a CAP-B10 caveat) directly against an internal Intron-9 2'-O-MOE ISS/IPA-competition microwalk restricted to chr2:219284988-219285939(+) (sparing 5'SS, Zone A CDS, and BP/PPT/3'SS chr2:219285940-219285986(+) whose blockade would force DNAJB2b) with mature DNAJB2b 3'-UTR stability and BiP/HSPA5 + CHOP/DDIT3 ER-stress counter-screens in sALS iPSC-MN/oligo co-cultures."
    ),
    "C015": (
        "(1) Exclude Alu-derived G2E3 Intron-1 windows from 3-plex SSO (#1 chr14:30563747-30563764(+) & #2 chr14:30563930-30563947(+) FAIL_EXACT_0MM_OFFTARGET; #3 chr14:30563939-30563956(+) WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL ELOC); "
        "(2) Run bidirectional CRISPRi/CRISPRa and allele-specific prime-editing dissection of chr14q12 SCFD1 vs G2E3 across paired isogenic human iPSC-MNs and LPS-stimulated human iMGL measuring ER-Golgi secretory and lysosomal-enzyme trafficking (given SuSiE purityMeanR2=0.988 & EUR-vs-xAnc GWAS COLOC H4=0.958 alongside 1000G Phase 3 EUR 96.7% [351/363] vs AFR 72.7% [853/1,173; 320 mixed] 1111 A-haplotype purity across rs229243-A, x-anc lead rs229195-A [PIP=0.240], rs229194-A, and MN ISL1-peak rs229143-A, paired with MN +0.048 vs iMGL -0.22 to -0.33 [PP_H4=0.88-0.89] SCFD1 opposition in Perez-Alcantara 2026 Nat Genet PMID:43045849, with SCFD1 Chronos=-1.26 barring pan-CNS knockdown)."
    ),
    "C023": (
        "(1) Execute allele-split 19F-NMR/DSF ternary pocket-stabilizer screening in rare (<0.1% ALS; gnomAD NFE AF=0.071%) YKT6 p.Tyr64Cys (rs138273846, chr7:44206388:A>G, AVI=24.53) knock-in human iPSC-MNs (rat DPC-bound PDB 3KYQ +85.1 A^3 cavity expansion + 3.46A Cys64-Cys66 disulfide trap PMID:20159557 vs human open PDB 6J74 PMID:32128853), verifying ternary [YKT6-Cys195-farnesyl + fragment] co-occupancy without ejecting endogenous Cys195-farnesyl or blocking PTAR1; "
        "(2) In >99.9% WT YKT6 sALS, test exterior Longin exosite stabilizers or PTAR1 170-bp Exon-2 skipping rescue (chr9:69750781-69750950(-)) while counter-screening cis-Golgi SNARE assembly (STX5/GOSR1/SEC22B/NSF)."
    ),
    "C018": (
        "(1) Engineer ECM-anchored half-life-extended intrathecal anti-gC1q Fab/nanobody (PDB 1PK6 1.85A globular head PMID:12960167) vs intrathecal microglial C1QA/B ASO/di-siRNA (depleting both gC1q opsonin head and AFDB mature cationic CLR stalk [C1QA 23-109, C1QB 28-114, C1QC 29-112: 27 mature Arg/Lys residues; 30 up to aa 114]; rejecting IV ANX005 & IV BBB-shuttled IgG due to peripheral 180 nM serum C1q sink ablation [10.7% autoimmune SAEs in HD NCT04514367 PMID:41787606] and unmodified q4w IT Fab due to modeled <0.001 nM Day-28 CSF trough [MODEL_PRIOR]); "
        "(2) Gate head-to-head on classical C3d/iC3b synaptic opsonization, preserved cholinergic C-bouton (SLC18A3/SLC5A7; Lobsiger 2013 PMID:24170856), and CLR-dependent neuronal RNP/polysome translation profiling (Scott-Hewitt 2024 PMID:38942014)."
    ),
    "C019": (
        "(1) Resolve the JAK1-vs-neuronal-JAK2 catch-22 at clinically reachable unbound human CSF concentrations (3.8-50 nM; modeled ~9% whole-cell pSTAT occupancy at 4 mg [MODEL_PRIOR] vs 2,500 nM screen) by testing Kp,uu-verified JAK2-sparing selective JAK1 JH1 inhibitors vs Baricitinib comparator and CRISPRi JAK1/JAK2/AAK1 knockdowns across BOTH glia-free sALS iPSC-MNs & reactive ALS-Glia co-cultures; "
        "(2) Complete bridged pg/mL immunoassay calibration of the rs3831317-neutral high-chitinase CSF glial stratum (Trautwig Emory leak-free sALS-vs-Ctrl OOF AUC=0.8188; target-site MGH-recalibrated AUC=0.885 [LOO=0.8801; bank-only non-MGH indicator=0.9444]; noting living-CSF-to-postmortem cortical ALS-Glia subtype concordance is unproven and distinct from healthy-control AUC<=0.92 in Thompson 2019 PMID:31123140 vs neurological-mimic AUC=0.688 in Steinacker 2018 PMID:29142138) before any VTE-prophylaxed Phase 2 interaction RCT."
    ),
    "C020": (
        "(1) Execute a strict 14-day postmitotic human C9orf72 and sALS iPSC-MN ClC-7 vacuole, ATG16L1-catalyzed LC3B CASM, and LRRK2 pRab10-Thr73 washout half-life falsification gate under intermittent q48h-q72h nanomolar Apilimod (CHEMBL4297643; resolving the [MODEL_PRIOR] ODE sensitivity where 6.5-8.0 nM unbound Cmax passes ~79% [64/81] in decoupled dead-zone Model 1 vs ~30% [24/81] at matched 10-20h repair and 0% [0/81] at 24-48h postmitotic repair in zero-dead-zone coupled +PI(3)P->LRRK2/CASM Model 2; PMID:42900584; Kuwahara 2026 Life Sci Alliance PMID:42994990, 10.26508/lsa.202603939); "
        "(2) Pair intracellular vs conditioned-media secreted poly(GP)/pTDP-43 mass-balance (PMID:27732842; Drosophila C9orf72 model 10.64898/2026.11.09.765393 [PREPRINT]), nanomolar-to-2.5 uM potency bridging, and microfluidic fast axonal transport kymography with <5% ClC-7 vacuolation, baseline CASM + pRab10-Thr73 washout (tau <24 h), and zero NfL/GFAP surge before any pulsed Phase 1b."
    ),
}


def sha12(fp: Path) -> str:
    return hashlib.sha256(fp.read_bytes()).hexdigest()[:12]


def classify_explore_type(cid: str, intake_row: dict[str, str], dec: str) -> str:
    if cid in EXPLORE_BENCHMARK_SPECS:
        return EXPLORE_BENCHMARK_SPECS[cid][0]
    if cid == "C005":
        return "COMPANION_PROTOCOL"
    if cid in {"C001", "C002", "C006", "C022"}:
        return "GENE_CIS_SPLICE"
    if cid == "C007":
        return "GENE_CIS_APA"
    if intake_row["track"] == "A":
        return "DRUG_REPURPOSING"
    return "GENE_DRUG_AXIS"


def classify_explore_drop_basis(cid: str, intake_row: dict[str, str], epi: str) -> tuple[str, str]:
    if epi == "ARTIFACT_CONFOUNDED":
        return (f"Dropped_Confounded_Postmortem_Transcriptomic_Target_{intake_row['name']}", "MEASURED_HUMAN_SPATIAL_OR_SNRNA")
    if cid in {"C004", "C008", "C009", "C012", "C024"}:
        return (f"Dropped_Failed_Human_ALS_Clinical_Regimen_{intake_row['name'].split()[0]}", "MEASURED_HUMAN_RCT_SUBGROUP")
    if cid in {"C011", "S05"}:
        return (f"Dropped_PK_or_Safety_Infeasible_Regimen_{intake_row['name'].split()[0]}", "MEASURED_HUMAN_PK_AND_SAFETY")
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
        is_sub_fdr_screen = 1 if pid in {"DN-14", "DN-17", "DN-19"} else 0
        is_cis_target = 0 if row["candidate_type"] in {"GENE_CIS_SPLICE", "GENE_CIS_APA"} else 1
        if is_screen_rep == 0 and is_cis_target == 0:
            is_spinal_mn_cryptic = 0 if pid == "DN-05" else 1
            is_mendelian_cis = 0 if pid == "C022" else 1
            cis_watchlist_order = {"DN-02": 1, "DN-03": 2, "DN-09": 3, "DN-08": 4, "DN-07": 5, "DN-06": 6}.get(pid, 9)
            return (t_ord, 0, 0, 0, is_spinal_mn_cryptic, is_mendelian_cis, h_cnt, cis_watchlist_order, pid)
        if is_sub_fdr_screen:
            sub_fdr_order = {"DN-14": 1, "DN-17": 2, "DN-19": 3}[pid]
            return (t_ord, is_screen_rep, is_sub_fdr_screen, 1, sub_fdr_order, h_cnt, ev_ord, src_ord, pid)
        return (t_ord, is_screen_rep, is_sub_fdr_screen, 1, h_cnt, ev_ord, src_ord, 0, pid)
    if t_ord == 4:
        return (t_ord, 0, 0, 0, 0, 0, 0, pid)
    if t_ord == 5:
        bm_order = {"C013": 1, "S08": 2, "C003": 3, "C017": 4, "DN-10": 5, "DN-11": 6, "DN-12": 7}
        return (t_ord, bm_order.get(pid, 99), 0, 0, 0, 0, 0, pid)
    epi_order = {"FALSIFIED_CLINICAL": 1, "FALSIFIED_PK_SAFETY": 2, "ARTIFACT_CONFOUNDED": 3}
    return (t_ord, epi_order.get(row["epistemic_state"], 9), 0 if row["origin_phase"] == "CURATED_CLINICAL_33" else 1, 0, 0, 0, 0, pid)
