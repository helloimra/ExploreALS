"""Populate Batch 6 candidate_decisions.csv for all 18 items and verify Epistemic & Provenance hygiene."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
B6_DIR = ROOT / "work" / "phase1_batches" / "batch_6"
REG_DIR = ROOT / "registries"
TS = "2026-11-10T23:55:00Z"
BATCH = "Batch_6_BA9_Named_Genes_And_Screen_Audit"

ALLOWED_EPISTEMIC = {
    "SUPPORTED", "UNPROVEN_UNTESTED", "FALSIFIED_CLINICAL",
    "FALSIFIED_PK_SAFETY", "ARTIFACT_CONFOUNDED", "ESTABLISHED_BENCHMARK",
}
ALLOWED_DECISIONS = {
    "KEEP_CORE", "KEEP_EXPLORATORY_UNPROVEN",
    "RECLASSIFY_BENCHMARK_OR_BIOMARKER", "DROP",
}
FALSIFIED_STATES = {"FALSIFIED_CLINICAL", "FALSIFIED_PK_SAFETY", "ARTIFACT_CONFOUNDED"}


def main() -> None:
    rows = [
        ("BA9-01", "AGAP2", "B", "LOW", "CONFOUNDED_POSTMORTEM_GC", "TECHNICAL_GC_ARTIFACT", "NONE",
         "Unadjusted D003 BA9 L2_L3 log2FC=-0.805 (p=1.41e-7) and modest Bye 2025 RNA-seq log2FC=-0.231.",
         "High-GC (57.69%, r_GC=+0.810) drives BA9 signal; GC-adj p=0.00117 fails Holm (4.12e-7), M1 GC-adj p=0.054, Edinburgh EN_L2_L3 null (-0.031, p=0.891), Spillman homogenate opposite (+0.285, p=0.243), LOEUF=0.388, 0 ALS genetics.",
         "ARTIFACT_CONFOUNDED", "DROP",
         "Named BA9 excitatory call collapses under donor GC shift (p=0.00117), fails replication in Edinburgh BA44/BA46 (p=0.891) and M1 (p=0.054), trends opposite in cortical homogenate proteomics (+0.285), and lacks human ALS genetics (LOEUF=0.388).",
         "", "EV-B6-001;EV-B6-002;EV-B6-003"),
        ("BA9-02", "AP1G2", "B", "LOW", "CONFOUNDED_POSTMORTEM_GC", "TECHNICAL_GC_ARTIFACT", "NONE",
         "Unadjusted D003 BA9 L2_L3 log2FC=-1.187 (p=2.04e-9) and NYGC Frontal log2FC=-0.524.",
         "BA9 GC-adj p=8.52e-7 misses Holm (4.12e-7; r_GC=+0.547, GC=54.43%); flips sign in Edinburgh EN_L2_L3 (+0.282, p=0.376); null in NYGC Motor RIN+GC (p=0.196) & Cervical SC (p=0.279); undetected in proteomics; 0 ALS genetics.",
         "ARTIFACT_CONFOUNDED", "DROP",
         "Loses BA9 family-wise significance after donor GC control (p=8.52e-7), reverses sign in Edinburgh BA44/BA46 (+0.282, p=0.376), is null in motor/spinal bulk RNA-seq, undetected across cortical/CSF proteomics, and has zero ALS genetics.",
         "", "EV-B6-004;EV-B6-005;EV-B6-006"),
        ("BA9-03", "BRSK2", "B", "LOW", "CONFOUNDED_POSTMORTEM_GC", "TECHNICAL_GC_ARTIFACT", "NONE",
         "Unadjusted D003 BA9 L2_L3/L3_L5/L4_L5 log2FC=-0.584 to -0.714.",
         "Extreme GC (63.85%, 97.5th pct; r_GC=+0.806) drives all 3 BA9 tests out of Holm & 1.5x SEOI (GC-adj p=9.88e-6..3.87e-5); null in M1 L4_L5 (p=0.991), Edinburgh (+0.041, p=0.825), NYGC Motor RIN+GC (p=0.372), and Spillman homogenate (+0.198, p=0.434); LOEUF=0.335 autism gene, 0 ALS genetics.",
         "ARTIFACT_CONFOUNDED", "DROP",
         "Archetypal high-GC (63.85%) postmortem cortical artifact failing Holm across all 3 BA9 clusters upon GC adjustment, completely null in Edinburgh snRNA-seq (p=0.825..0.997), M1, and Spillman proteomics (+0.198, p=0.434), with severe LoF constraint (LOEUF=0.335).",
         "", "EV-B6-007;EV-B6-008;EV-B6-009"),
        ("BA9-04", "DNAJB2", "B", "MODERATE_HIGH", "PARTIALLY_VERIFIED_ISOFORM_AND_COMPARTMENT_OPEN", "POTENTIAL_CAUSAL_PROTEOSTASIS_LOSS", "LOW_WHITESPACE",
         "Sole BA9 gene surviving GC-adjusted Holm in Oligo (-0.745, p=3.46e-7), replicating in M1 Oligo (-0.618, p=2.59e-4), NYGC Cervical SC (-0.293, p=5.21e-5), Spillman synaptosomes (-0.511, p=0.0132) & iPSC neurons (-1.115, p=0.0455), backed by 55 ClinVar P/LP variants causing human DSMA5/CMT2T/juvenile ALS.",
         "Edinburgh OD is noisy/non-significant (-0.397, p=0.447), NYGC Motor bulk flips slightly (+0.087, p=0.401), CSF TMT is null (p=0.779), cellular compartment dominance (oligodendrocyte vs motor neuron) is unresolved, and rescue requires chaperone augmentation.",
         "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
         "Unlike high-GC excitatory BA9 artifacts, DNAJB2 (HSJ1) survives BA9 GC-adjusted Holm, shows concordant M1 oligo, cervical spinal, synaptosomal, and iPSC neuronal loss, and causes human recessive motor neuropathy/juvenile ALS; cell-compartment (oligodendrocyte vs motor neuron) and isoform augmentation remain untested in sALS.",
         "Compartment-resolved (motor-neuron-autonomous vs oligodendrocyte-restricted vs co-culture) and isoform-resolved (cytosolic/nuclear DNAJB2a vs ER-anchored DNAJB2b) AAV/mRNA augmentation assay in TDP-43-depleted human sALS iPSC motor-neuron + oligodendrocyte cultures measuring insoluble TDP-43 clearance and axonal survival.",
         "EV-B6-010;EV-B6-011;EV-B6-012"),
        ("BA9-05", "KIFC2", "B", "LOW", "CONFOUNDED_POSTMORTEM_GC", "TECHNICAL_GC_ARTIFACT", "NONE",
         "Unadjusted D003 BA9 L5/L4_L6/L4_L5/L3_L5 log2FC=-0.942 to -1.007.",
         "Extreme GC (63.73%, 97.4th pct; r_GC=+0.751..+0.826) knocks all 4 BA9 clusters above Holm (GC-adj p=1.80e-5..7.62e-5); flips sign in Edinburgh EN_L5_L6 (+0.433, p=0.429); null in NYGC Motor RIN+GC (p=0.332); undetected in homogenate/iPSC MS; 0 ALS genetics.",
         "ARTIFACT_CONFOUNDED", "DROP",
         "Extreme-GC (63.73%) transcript losing family-wise significance across all 4 BA9 clusters after donor GC control, flipping sign in Edinburgh EN_L5_L6 (+0.433, p=0.429), null in RIN+GC-adjusted motor bulk, and devoid of human ALS genetics.",
         "", "EV-B6-013;EV-B6-014;EV-B6-015"),
        ("BA9-06", "MIB2", "B", "LOW", "CONFOUNDED_POSTMORTEM_GC", "TECHNICAL_GC_ARTIFACT", "NONE",
         "Unadjusted D003 BA9 L2_L3 log2FC=-0.852 (p=1.67e-7).",
         "Highest GC of all 10 BA9 genes (66.41%, 99.0th pct; r_GC=+0.809); GC-adj p=0.00136 fails Holm & SEOI; null in M1 GC-adj (p=0.155), Edinburgh (+0.053, p=0.847), NYGC Motor RIN+GC (p=0.185), and Spillman homogenate (+0.052, p=0.871); 0 ALS genetics.",
         "ARTIFACT_CONFOUNDED", "DROP",
         "Highest-GC gene in the BA9 cohort (66.41%) whose BA9 signal collapses under donor GC adjustment (p=0.00136) and is completely null across M1 (p=0.155), Edinburgh snRNA-seq (+0.053, p=0.847), Spillman cortical homogenate (+0.052, p=0.871), and ALS genetics.",
         "", "EV-B6-016;EV-B6-017;EV-B6-018"),
        ("BA9-07", "MYO18A", "B", "LOW", "SIGN_REVERSED_CROSS_COHORT", "TECHNICAL_DISCORDANT_ARTIFACT", "NONE",
         "D003 BA9 Oligo unadjusted log2FC=+0.624 (p=6.38e-7).",
         "Fails Holm after GC (p=6.86e-5; r_GC=-0.597), null in M1 Oligo GC-adj (+0.105, p=0.321), reverses sign in Edinburgh OD (-0.391, p=0.452) and all 3 NYGC bulk regions (Frontal -0.239, Motor -0.385, Cervical SC -0.400, p=1.55e-5), null in Spillman MS (+0.228, p=0.352), LOEUF=0.399, 0 human ALS genetics.",
         "ARTIFACT_CONFOUNDED", "DROP",
         "BA9 oligodendrocyte elevation (+0.624) fails Holm after GC control, is null in M1 oligos (p=0.321) and Spillman proteomics (p=0.352..0.693), significantly reverses sign across NYGC Frontal, Motor, and Cervical SC (-0.400, p=1.55e-5), and is LoF-intolerant (LOEUF=0.399).",
         "", "EV-B6-019;EV-B6-020;EV-B6-021"),
        ("BA9-08", "SNPH", "B", "MODERATE", "BA9_RNA_ARTIFACT_HIGH_FRAGILITY_AXONAL_OPEN", "UNRESOLVED_PROXIMAL_SPHEROID_TRAPPING_VS_DOCKING", "LOW_WHITESPACE",
         "M1 L2_L3 shows GC-independent RNA reduction (-1.529, p=3.61e-4, r_GC=+0.020; NYGC Motor comp+GC -0.381, p=2.28e-5), Spillman DIA shows homogenate (+0.710, p=0.00536) & iPSC (+0.171, p=0.0396) accumulation, and 2025 human neuromuscular assembloids (PMID:41193975) show SNPH loss boosts mitochondrial transport & NMJ formation.",
         "High fragility: gnomAD pLI=0.996 (LOEUF=0.461), 0 ALS genetics, null SOD1-G93A mouse Snph KO (Zhu & Sheng 2011), BA9 RNA failed Holm (p=1.64e-4; Edinburgh p=0.732), and opposite-sign synaptosome (-0.260, p=0.320) vs homogenate (+0.710) may reflect passive proximal axonal spheroid trapping.",
         "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
         "Although BA9 RNA was GC-confounded and fragility is high (gnomAD pLI=0.996, LOEUF=0.461; null SOD1-G93A KO in Zhu & Sheng 2011; opposite synaptosome -0.260 vs homogenate +0.710 potentially reflecting proximal axonal spheroid trapping), GC-free M1 reduction and 2025 human assembloid NMJ rescue leave graded sALS knockdown untested.",
         "Graded (30-50%, sparing pLI=0.996 full KO) SNPH ASO knockdown vs overexpression in TDP-43-depleted sALS iPSC microfluidic motor axons with mandatory presynaptic Ca2+ buffering (GCaMP6f + STX1A/SNAP25/BSN integrity) and proximal axonal spheroid trapping (NF-H/APP/SNPH co-accumulation) safety gates alongside distal ATP/NMJ survival.",
         "EV-B6-022;EV-B6-023;EV-B6-024"),
        ("BA9-09", "ZNF783", "B", "LOW", "CONFOUNDED_POSTMORTEM_GC", "TECHNICAL_GC_ARTIFACT", "NONE",
         "Unadjusted D003 BA9 L2_L3 log2FC=-0.723 (p=1.02e-8).",
         "BA9 r_GC=+0.715 knocks GC-adj p to 5.53e-5 (fails Holm); M1 L2_L3 GC-adj collapses to -0.082 (p=0.510); Edinburgh EN_L2_L3 reverses sign (+0.292, GC-adj p=0.0471); NYGC Motor RIN+GC null (p=0.175); 0 peptides in proteomics; 0 ALS genetics or ligandability.",
         "ARTIFACT_CONFOUNDED", "DROP",
         "Uncharacterized KRAB-ZNF whose BA9 signal fails Holm after GC adjustment (p=5.53e-5), collapses in M1 (p=0.510), significantly reverses sign in Edinburgh BA44/BA46 (+0.292, p=0.047), is undetected across all proteomics, and lacks ALS genetics.",
         "", "EV-B6-025;EV-B6-026;EV-B6-027"),
        ("BA9-10", "CAPG", "B", "LOW", "COMPOSITION_CONFOUNDED_BULK_GLIOSIS", "REACTIVE_MICROGLIAL_PROLIFERATION_MARKER", "NONE",
         "NYGC Cervical SC bulk log2FC=+1.414 (p=3.45e-15), Spillman cortex homogenate +0.956 (p=2.92e-4), and Trautwig CSF DIA +0.252 (p=0.0105).",
         "Purified single-nucleus microglia trend negative across D003 BA9 (-0.849, p=0.111), D003 M1 (-0.818, p=0.090), and Edinburgh MIG (-0.484, p=0.476); NYGC Frontal trends negative (-0.216, p=0.0695); CSF TMT is null (+0.056, p=0.194); 0 ALS genetics and OpenTargets grade 3-4 neurotoxicity flag.",
         "ARTIFACT_CONFOUNDED", "DROP",
         "Bulk spinal/homogenate CAPG elevation is a pure microglial cell-fraction expansion artifact: per-cell microglial snRNA-seq expression trends negative across all 3 cortical cohorts, CSF TMT is non-significant (p=0.194), ALS genetics are absent, and OpenTargets flags grade 3-4 neurotoxicity.",
         "", "EV-B6-028;EV-B6-029;EV-B6-030"),
        ("S01", "Dexmedetomidine", "A", "LOW", "VERIFIED_SCREEN_STATS_UNVIABLE_HUMAN_PK", "OFF_TARGET_HIGH_CONC_SCREEN_HIT", "NONE_IN_ALS",
         "Verified Bye 2025 2.5 uM paired rescue +1.3992d across 16 sALS lines (12/16 >0d, t=3.250, p=0.00538, q=0.03030, Rank #7/107).",
         "IV ICU sedative (0.2-0.7 ug/kg/h) achieves <=0.318 nM unbound CNS exposure where ADRA2A agonism (Ki~1.65 nM) already causes deep sedation, hypotension, and sinus bradycardia — a 7,862x exposure deficit vs 2,500 nM screen (ADRA2A/B/C non-DE in Bye RNA-seq).",
         "FALSIFIED_PK_SAFETY", "DROP",
         "Despite genuine 2.5 uM iPSC-MN rescue (+1.399d, q=0.0303), tolerated human unbound CNS exposure (~0.32 nM IV ICU infusion) is 7,862-fold below the screen concentration and capped by dose-limiting sedation, hypotension, and bradycardia.",
         "", "EV-B6-031;EV-B6-032;EV-B6-033"),
        ("S02", "CuATSM", "A", "LOW", "VERIFIED_SCREEN_STATS_CLINICALLY_REFUTED", "SOD1_MOUSE_PHENOCOPY_FAILED_HUMAN_TDP43", "DISCONTINUED_FAILED_PHASE2_3",
         "Verified Bye 2025 2.5 uM paired rescue +1.3792d across 15 valid sALS lines (12/15 >0d, p=0.00631, q=0.03375, Rank #8/107; true ID CHEMBL4297372, fixing intake CHEMBL4297643 typo).",
         "CNS-penetrant oral CuATSM (72 mg/d) failed randomized placebo-controlled Phase 2/3 ALS trial NCT04082832 (N=80) across ALSFRS-R and ECAS, and postmortem neuropathology of treated patients (Yang 2023, n=6 vs 6) showed unaltered pTDP-43 burden and motor neuron loss.",
         "FALSIFIED_CLINICAL", "DROP",
         "Direct human clinical and neuropathological falsification: CNS-penetrant CuATSM (CHEMBL4297372) failed placebo-controlled Phase 2/3 ALS trial NCT04082832 and failed to alter spinal/cortical pTDP-43 pathology or motor neuron loss in treated patient autopsies.",
         "", "EV-B6-034;EV-B6-035;EV-B6-036"),
        ("S03", "Mycophenolate mofetil", "A", "LOW", "VERIFIED_SCREEN_STATS_PK_AND_SAFETY_FALSIFIED", "PERIPHERAL_LYMPHOID_IMPDH_BLOCKER", "FAILED_PHASE2_IMMUNOSUPPRESSION",
         "Verified Bye 2025 2.5 uM paired rescue +1.2792d across 15 valid sALS lines (12/15 >0d, p=0.00293, q=0.02090, Rank #10/107; true IDs CHEMBL1456/CHEMBL866, fixing intake CHEMBL1230607 typo).",
         "Active MPA is 98% albumin-bound (fu=0.02) and actively effluxed at BBB (Kpuu~0.08), yielding Cu_CNS ~20 nM at 1000 mg BID (125x below 2500 nM neuronal screen), carries FDA Boxed Warnings for PML/fatal infections/lymphoma, and had 0/31 responders with 42% AE dropouts in ALS Phase 2 NCT01884571.",
         "FALSIFIED_PK_SAFETY", "DROP",
         "Active MPA suffers a 125-fold human unbound CNS deficit (~20 nM vs 2,500 nM screen) due to 98% albumin binding and BBB organic-anion efflux, carries FDA Boxed Warnings for PML and fatal infections, and failed human ALS Phase 2 trial NCT01884571 (0/31 responders, 42% AE dropouts).",
         "", "EV-B6-037;EV-B6-038;EV-B6-039"),
        ("S04", "Tamoxifen", "A", "LOW", "VERIFIED_SCREEN_STATS_CAD_PK_FALSIFIED", "MICROMOLAR_CAD_PHOSPHOLIPIDOSIS_ARTIFACT", "FAILED_HISTORICAL_PHASE2",
         "Verified Bye 2025 2.5 uM paired rescue +1.2742d across 16 sALS lines (13/16 >0d, p=0.00316, q=0.02104, Rank #11/107).",
         "At 20-40 mg/d PO, fu=0.008 yields Cu_brain ~2.59 nM (965x below 2,500 nM screen & >1,000x below PKC IC50 ~3 uM); cationic amphiphile (ALogP=6.00) induces in vitro phospholipidosis at 2.5 uM, carries FDA Boxed Warnings for fatal stroke/PE/uterine sarcoma, and showed no durable 12-mo ALSFRS-R benefit across NCT01257581 (N=60), NCT00214110 (N=100), and Chen 2020.",
         "FALSIFIED_PK_SAFETY", "DROP",
         "Unbound human brain tamoxifen (~2.59 nM at 40 mg/d, fu=0.008) is 965-fold below the 2.5 uM screen concentration (a canonical ALogP=6.0 cationic amphiphilic phospholipidosis/PKC regime), carries Boxed Warnings for fatal stroke/PE, and failed to show durable efficacy across 3 human ALS trials.",
         "", "EV-B6-040;EV-B6-041;EV-B6-042"),
        ("S06", "SARM1 (Axonal NADase)", "B", "VERY_HIGH", "BLIND_SURVIVOR_GENETICALLY_AND_BIOCHEMICALLY_ANCHORED", "CAUSAL_WALLERIAN_AXON_EXECUTIONER", "MODERATE_ORTHOSTERIC_CLINICAL_CROWDING_ALLOSTERIC_OPEN",
         "Rare constitutively active ARM-domain GoF variants enrich in human ALS (Gilley 2021; Bloom 2022; OT genetic_score=0.195), directly executing Wallerian NAD+ catastrophe downstream of TDP-43/STMN2/NMNAT2 loss; elevated protein in C9FTD iPSC neurons (+0.675, p=0.0268); complete human LoF tolerance (gnomAD obs/exp=60/65.1, LOEUF=1.143, pLI=2.75e-19, 0 safety liabilities).",
         "Postmortem end-stage bulk RNA is lower (-0.307) due to projection-neuron dropout, clinical SARM1 space now has moderate crowding (Lilly LY3873862 NCT07883590; Nura/TRICALS NB-4746 NCT07369076; preclinical ASHA-624), and 2026 Commun Chem (PMID:42156967) warns first-gen orthosteric base-exchange inhibitors risk paradoxical sub-inhibitory SARM1 activation.",
         "SUPPORTED", "KEEP_CORE",
         "Core Track B target backed by human ALS rare GoF genetics, direct epistasis downstream of TDP-43/STMN2 axonal vulnerability, elevated patient iPSC neuronal protein (+0.675, p=0.0268), and human knockout safety (LOEUF=1.143); despite moderate clinical crowding (LY3873862 NCT07883590, NB-4746 NCT07369076), non-activating ARM-domain Cys311 allosteric / intramolecular-glue inhibitors retain clear differentiation over biphasic base-exchange scaffolds.",
         "Benchmark CNS-penetrant covalent/reversible ARM-domain allosteric or intramolecular-glue SARM1 inhibitors vs orthosteric base-exchange LY3873862/DSRM-3716 across full sub-IC50 concentration curves in STMN2/TDP-43-depleted human iPSC motor axons measuring cADPR, NAD+, and distal axon survival.",
         "EV-B6-043;EV-B6-044;EV-B6-045"),
        ("S07", "Low-Dose Aldesleukin (IL-2) in Low-pNfH Stratum", "A", "MODERATE_HIGH", "ITT_NULL_PHASE2B_STRATUM_HYPOTHESIS_UNCONFIRMED", "BIOMARKER_GATED_TREG_MODULATION_UNPROVEN_PHASE3", "MODERATE_UNAPPROVED_CONFIRMATORY_RCT_NEEDED",
         "In MIROCALS Phase 2b (NCT03039673, PMID:40354799, Lancet May 2025, N=220; true ID CHEMBL1201438, fixing intake Trastuzumab typo), the pre-specified Low/Mod CSF pNfH (750-3,700 pg/mL, n=154) stratum showed a 48% 21-mo mortality hazard reduction (HR=0.52, 95% CI 0.30-0.89, p=0.016) alongside FOXP3+ Treg expansion and CCL2 reduction.",
         "Primary unadjusted ITT log-rank test missed significance (HR=0.81, 95% CI 0.54-1.22, p=0.33; high-pNfH >3,700 pg/mL HR=1.37, p=0.38), IL2/IL2RA has 0 human ALS genetics, EMA/MHRA/UK MND CSG declined regulatory approval pending Phase 3 proof, and zero prospective Phase 3 trials enrolling CSF-pNfH <3,700 pg/mL patients have been completed.",
         "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
         "Under Epistemic Asymmetry, a responder stratum (HR=0.52, p=0.016 in CSF pNfH <=3,700 pg/mL) from a primary-ITT-null Phase 2b trial (MIROCALS PMID:40354799, unadjusted HR=0.81, p=0.33) with zero human IL2/IL2RA ALS genetics, regulatory non-approval (EMA/MHRA/UK MND CSG), and zero completed prospective low-pNfH Phase 3 RCTs remains an unproven biomarker-enrichment hypothesis rather than core proof.",
         "Prospective, double-blind, placebo-controlled Phase 3 RCT exclusively enrolling riluzole-treated ALS patients stratified by baseline CSF pNfH <3,700 pg/mL (or calibrated plasma pNfH/NfL equivalent) confirming 18-21 month overall survival, ALSFRS-R slowing, and longitudinal FOXP3+ Treg expansion + plasma/CSF CCL2 suppression.",
         "EV-B6-046;EV-B6-047;EV-B6-048"),
        ("S08", "Ultrahigh-Dose Methylcobalamin (Rozebalamin)", "A", "MODERATE_HIGH", "VERIFIED_PHASE3_AND_PMDA_APPROVAL", "EARLY_WINDOW_HOMOCYSTEINE_METHYLATION_RESCUE", "APPROVED_SOC_IN_JAPAN_2024",
         "Phase 3 JETALS RCT (NCT03548311, Oki et al. JAMA Neurol 2022, PMID:35532908, N=130 <=1yr onset; true ID CHEMBL4297672, fixing intake Dacomitinib typo) slowed 16-wk ALSFRS-R decline by 43% (+1.97 pts, p=0.01; +2.11 w/ riluzole) and lowered homocysteine, achieving Japan PMDA approval (Rozebalamin 50 mg IM, Sept 2024).",
         "Efficacy is restricted to early <=12-month onset (prior <3yr trial NCT00444613 N=373 missed ITT), and unshielded 2.5 uM methylcobalamin scored -3.60d (q=0.00246, Rank #105/107) in Bye 2025 due to blue-light imaging photolysis of the Co-C bond.",
         "ESTABLISHED_BENCHMARK", "RECLASSIFY_BENCHMARK_OR_BIOMARKER",
         "Clinically proven and PMDA-approved (Sept 2024) standard-of-care benchmark in early-onset (<=12m) ALS (+1.97 ALSFRS-R pts in Phase 3 JETALS, p=0.01); also serves as a critical screening calibration control exposing blue-light phototoxicity false negatives in live-imaging iPSC assays.",
         "", "EV-B6-049;EV-B6-050;EV-B6-051"),
        ("S09", "Censavudine (TPN-101) in ALS-TE Subtype", "A", "HIGH", "C9ORF72_SIGNAL_VERIFIED_SPORADIC_ALS_TE_UNTESTED", "SUBTYPE_SPECIFIC_CORTICAL_RETROTRANSPOSON_DRIVER", "LOW_IN_SPORADIC_ALS_TE",
         "Phase 2a NCT04993755 (N=42 C9orf72-ALS/FTD, 400 mg/d PO TPN-101 / CHEMBL124363) showed favorable safety, reduced CSF IL-6 & NfL, and ~50% slower 24-wk vital capacity decline (-8.4% vs -16.5% placebo in C9-ALS).",
         "Primary re-analysis of O'Neill 2025 (DS001_ONEILL) shows cortical ALS-TE dropped to 13.40% (41/306 donors; 11.52% in non-C9 sALS) and spinal cord ALS-TE is 0.00% (0/331 donors), with zero sporadic ALS-TE patients ever tested and no validated living-CSF ALS-TE diagnostic.",
         "UNPROVEN_UNTESTED", "KEEP_EXPLORATORY_UNPROVEN",
         "Oral LINE-1 RT inhibitor TPN-101 demonstrated encouraging Phase 2a biomarker (CSF IL-6/NfL) and vital-capacity signals in C9orf72-ALS, but extension to sporadic ALS-TE is untested and gated by lower cortical prevalence (13.40%), complete absence of ALS-TE in spinal cord (0/331), and lack of a living-patient biomarker.",
         "Validate a living-patient CSF extracellular-vesicle LINE-1 ORF1p / cell-free retrotransposon RNA + CSF IL-6 stratification assay paired against TDP-43-depleted iPSC-neuron LINE-1 cDNA inhibition at human unbound CSF censavudine levels prior to sporadic ALS-TE trial enrichment.",
         "EV-B6-052;EV-B6-053;EV-B6-054"),
    ]

    dec_fields = [
        "carbon_id", "name", "track", "phase1_batch", "reanalysis_state",
        "scientific_taste_rating", "technical_accuracy_of_explore_claim",
        "causal_vs_reactive_assessment", "prior_art_crowding_level",
        "evidence_proves_hypothesis", "evidence_disproves_hypothesis",
        "epistemic_state", "decision", "factual_justification",
        "discriminating_next_test", "supporting_evidence_ids", "updated_at",
    ]
    dec_path = B6_DIR / "candidate_decisions.csv"
    with dec_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(dec_fields)
        for r in rows:
            w.writerow([r[0], r[1], r[2], BATCH, "ADJUDICATED_VERIFIED", *r[3:], TS])

    intake = {r["carbon_id"]: r for r in csv.DictReader((REG_DIR / "candidate_intake_ledger.csv").open(encoding="utf-8")) if r["assigned_batch"] == BATCH}
    ds_ids = {r["dataset_id"] for r in csv.DictReader((REG_DIR / "datasets_manifest.csv").open(encoding="utf-8"))}
    b6_runs = list(csv.DictReader((B6_DIR / "analysis_runs.csv").open(encoding="utf-8")))
    b6_ev = list(csv.DictReader((B6_DIR / "evidence_ledger.csv").open(encoding="utf-8")))
    b6_dec = list(csv.DictReader(dec_path.open(encoding="utf-8")))

    errors: list[str] = []
    if {d["carbon_id"] for d in b6_dec} != set(intake.keys()):
        errors.append("Batch 6 candidate_decisions.csv IDs do not match Batch 6 intake rows 1-to-1.")
    run_ids = {r["analysis_run_id"] for r in b6_runs}
    for r in b6_runs:
        for dsid in filter(None, r["datasets_used"].split(";")):
            if dsid not in ds_ids:
                errors.append(f"Run {r['analysis_run_id']} cites unknown dataset_id {dsid}")
    ev_ids = {e["evidence_id"] for e in b6_ev}
    for e in b6_ev:
        eid = e["evidence_id"]
        if e["carbon_id"] not in intake:
            errors.append(f"{eid}: out-of-batch carbon_id {e['carbon_id']}")
        if e["analysis_run_id"] not in run_ids:
            errors.append(f"{eid}: unknown run {e['analysis_run_id']}")
        for col in ("p_value", "fdr_or_adjusted_p"):
            if e[col]:
                try:
                    v = float(e[col])
                    if not (0.0 < v <= 1.0):
                        errors.append(f"{eid}: {col}={e[col]} outside (0, 1]")
                except ValueError:
                    errors.append(f"{eid}: non-numeric {col}={e[col]!r}")
        if e["fdr_or_adjusted_p"] and not e["p_value"]:
            errors.append(f"{eid}: fdr_or_adjusted_p present without primary p_value")
        if e["sample_size_n"]:
            if not e["sample_size_n"].isdigit() or int(e["sample_size_n"]) <= 0:
                errors.append(f"{eid}: invalid sample_size_n={e['sample_size_n']!r}")
    for d in b6_dec:
        cid = d["carbon_id"]
        if d["reanalysis_state"] != "ADJUDICATED_VERIFIED":
            errors.append(f"{cid}: reanalysis_state != ADJUDICATED_VERIFIED")
        if d["epistemic_state"] not in ALLOWED_EPISTEMIC:
            errors.append(f"{cid}: invalid epistemic_state {d['epistemic_state']}")
        if d["decision"] not in ALLOWED_DECISIONS:
            errors.append(f"{cid}: invalid decision {d['decision']}")
        if d["decision"] == "DROP":
            if d["epistemic_state"] == "UNPROVEN_UNTESTED" or d["epistemic_state"] not in FALSIFIED_STATES:
                errors.append(f"EPISTEMIC VIOLATION on {cid}: invalid DROP epistemic_state {d['epistemic_state']}")
            if not d["factual_justification"].strip() or not d["supporting_evidence_ids"].strip():
                errors.append(f"EPISTEMIC VIOLATION on {cid}: DROP missing justification/evidence")
        if d["decision"] == "KEEP_EXPLORATORY_UNPROVEN" and not d["discriminating_next_test"].strip():
            errors.append(f"{cid}: KEEP_EXPLORATORY_UNPROVEN missing discriminating_next_test")
        for evid in filter(None, d["supporting_evidence_ids"].split(";")):
            if evid not in ev_ids:
                errors.append(f"{cid}: missing supporting_evidence_id {evid}")

    if errors:
        print("BATCH 6 VALIDATION FAILED:", errors, file=sys.stderr)
        sys.exit(1)
    print(f"PASS: Batch 6 verified ({len(b6_dec)} decisions, {len(b6_ev)} evidence rows, {len(b6_runs)} runs, 0 errors).")


if __name__ == "__main__":
    main()
