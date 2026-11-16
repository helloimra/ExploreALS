"""Role-calibrated mechanistic contrast strips (35 active/benchmark IDs) and non-exclusive problem lenses for CarbonALS."""
from __future__ import annotations

EDGE_ROLE_LABELS: dict[str, str] = {
    "MECHANISTIC_EDGE": "MECHANISTIC CONTRAST & KEY RISK",
    "CROWDED_MULTIPLEX": "ACTIVE CLINICAL CLASS — MULTIPLEX & TECHNICAL DELTA",
    "HIGH_HURDLE_WATCHLIST": "EXPLORATORY WATCHLIST — DOMINANT PK / BIOLOGICAL HURDLE",
    "BENCHMARK_CALIBRATOR": "CLINICAL BENCHMARK / BIOFLUID CALIBRATION BOUNDARY",
    "FALSIFIED_TRAP": "FALSIFIED MECHANISM / CONFOUNDING ARTIFACT",
}

CANDIDATE_EDGES_ACTIVE: dict[str, tuple[str, str]] = {
    "S06": ("MECHANISTIC_EDGE", "PDB 9TZY proves 1-AD base-exchange prodrugs (LY3873862, Ph1 Not Yet Recruiting) bridge three TIR chains and spike WT SARM1 at washout (NB-4746 tested head-to-head), mandating non-covalent ARM-TIR T-locks, <1% GoF carrier exclusion, and NDEV/trough PK given non-neuronal CD38 cADPR background."),
    "C006": ("MECHANISTIC_EDGE", "In-frame KCNQ2 Exon-5 skipping (dPSI=+0.21, FDR=4.2e-24) evades NMD with ER retention and imposes a Trp236 surface-density ceiling on Kv7 openers (PDB 7CR2); lead #3 (UG=1, 0/18 splicing AVI) avoids #1's UG8 WT TDP-43 cis-eviction hazard pending 1-nt ISE vs ISS microwalks."),
    "S07": ("MECHANISTIC_EDGE", "Trautwig 2025 CSF (n=77 DIA / n=51 overlapping Emory TMT) shows tryptic MS NEFL correlates weakly with NEFH (r=0.28), motivating Stage-0 BioVendor ELISA-to-CLIA pNfH & NfL calibration; event-driven Phase 3 (247 deaths at HR=0.70, N~650-750 over 36-42 mo) gates pNfH <=3,700 pg/mL."),
    "C001": ("CROWDED_MULTIPLEX", "Standalone 1-plex UNC13A SSOs are crowded (LY4256984/TRCN-1023); differentiation rests on 125-bp read-length rescue (OR=3.89x), clean >=2mm anchor #2, 3-layer per-target PK/NDEV-dPCR/synaptic-secretome TE + >=16-24 wk pNfH PD, and genotype-stratified 2-plex vs 3-plex testing across rs12973192/rs12608932."),
    "C002": ("CROWDED_MULTIPLEX", "Interim QRL-201 ANQUR (NCT05633459) showed tissue STMN2 rescue with low-dose (~46%) vs 10mg (~5%) pNfH dissociation; re-analysis pairs cortical tSTMN2 RNA inflation (+0.32/+0.72) against -28% protein (p=0.014, FDR=0.11, n=20 C9-FTD) with parallel SARM1 T-lock protection (illustrative ~2-7x MWC scenario)."),
    "C007": ("MECHANISTIC_EDGE", "Endothelial enrichment (+3.11 log2CPM, n=7 Ctrl; 55-um MN-niche Visium spots +3.76, N=14) explains bulk nulls without resolving sST2 vs ST2L, while pan-ST2 mAbs block Treg ST2L 8.8x harder; gated on oximetry/capnography-verified normoxic (supine FVC>=80%) CSF Simoa and capillary ASO delivery (PMID:37188501)."),
    "DN-01": ("MECHANISTIC_EDGE", "TDP-43 cryptic splicing truncates ATG4B at Glu319 (PDB 2Z0D, 27 LC3B contacts) with C9-FTD homogenate protein loss (-0.49, p=0.023, n=20), gated on graded TDP-43-CRISPRi paralog checks and Stage-(ii) pre-inclusion cervical alpha-MN duplex BaseScope ISH."),
    "DN-04": ("MECHANISTIC_EDGE", "Neuron-restricted CELF5 cryptic splicing replicates in sALS iPSC-MN LeafCutter clu_25763_+ (padj=0.0090; nominal BA4 p=0.0133, FDR=0.136) with clean >=2mm SSO #1, gated on Exon 4-7 Nanopore RT-PCR (<1-2% LOQ Exon-5 skip / 98-bp mod3=2 retention) and Stage-(ii) cervical BaseScope ISH."),
    "DN-02": ("HIGH_HURDLE_WATCHLIST", "Despite 70% C9-FTD cortical penetrance and clean >=2mm SSO #1, common variant rs2173852 (AF=17.5%, 76x 5'SS drop) has zero ALS GWAS signal across 40 cohorts, pointing to low spinal expression (1.50 TPM) and alt-3'SS shunting risk."),
    "DN-06": ("HIGH_HURDLE_WATCHLIST", "Synaptosomal PFKP protein depletion (-0.51, p=0.0035, n=20 C9-FTD) and clean >=2mm SSO #1 are tempered by flat surviving cervical MN-niche Visium RNA (FDR=0.64) and risk of draining neuronal pentose-phosphate NADPH/GSH antioxidant defense."),
    "DN-07": ("HIGH_HURDLE_WATCHLIST", "Pathology-selective TRAPPC12 intronic polyadenylation (82.9% TDP+ vs 34.0% non-TDP) and sALS iPSC-MN LeafCutter splicing (padj=0.015) face null bulk C9-FTD cortical DIA proteomics (p=0.84) and co-occurring secondary cryptic-exon shunting risk."),
    "DN-08": ("HIGH_HURDLE_WATCHLIST", "TDP-43-selective ELK1 3'-extension elevates i3Neuron translation (+1.12, padj=2.3e-5) with null BA4 snRNA/regulon divergence; nuclear RNase-H1 gapmers risk Pol II readthrough cleavage of canonical ELK1 (PMID:31924448), shifting gating to steric distal-PAS SSOs or cytoplasmic 3'Ext siRNA."),
    "DN-09": ("HIGH_HURDLE_WATCHLIST", "Pathology-selective DLGAP1 cryptic polyadenylation (19.4x TDP+ enrichment) pairs with C9-FTD cortical synaptosomal protein loss (-0.74, p=0.021, n=12), but spinal motor-neuron penetrance is unproven and lumbar bulk RNA is masked by glial shifts."),
    "BA9-04": ("MECHANISTIC_EDGE", "Sole GC-adjusted BA9 survivor (p=3.46e-7) where cytosolic TDP-43-clearing DNAJB2a excises Intron 9 while ER-prenylated DNAJB2b retains it; splice-shifting faces unverified Intron-9 ISS vs ISE polarity and zero-sum ERAD DNAJB2b depletion risk."),
    "C014": ("HIGH_HURDLE_WATCHLIST", "Post-translational SUN1-CHMP7 nuclear retention triggers NPC injury despite flat bulk RNA (iPSC pellet n=6), but extreme germline intolerance (pLI=0.9996) and sequential ANXA11-CHMP2B membrane-repair reliance penalize deep RNase-H knockdown."),
    "S09": ("HIGH_HURDLE_WATCHLIST", "Cortical ALS-TE spans 13.5% of motor ALS (0/331 bulk cord) with flat canonical ISGs; living enrichment must separate pan-TDP cryptic HDGFL2 and longitudinal CSF IL-6 PD from subtype-specific LINE-1 ORF1p/L1HS cargo and active cGAS-STING signaling."),
    "C018": ("HIGH_HURDLE_WATCHLIST", "Cervical MN-niche Visium C1QC surges (+2.37 log2FC, spot-level FDR=1.04e-10, N=14) after C3 MERIDIAN failure, but 180 nM serum C1q sinks, ~12 h CSF Fab washout, and null SOD1 C1qa-KO survival with C-bouton loss restrict C1q to HLE IT tools."),
    "DN-03": ("HIGH_HURDLE_WATCHLIST", "Convergent Ribo-seq (-2.78, padj=1.1e-7), C9-FTD cortical DIA (-0.37, p=0.0062), and living-CSF PTPRT loss lack 1-bp cryptic-exon coordinates inside a 3.57-kb intron and carry dual synaptic-adhesion vs nuclear pSTAT3 signaling risk."),
    "DN-05": ("MECHANISTIC_EDGE", "Top Tier 3 discovery (#9/59): sole Ma cryptic-spliced gene depleted in surviving cervical MN-niche Visium spots (-1.23 log2FC, spot-level FDR=0.019, N=18) and C9-FTD synaptosomes (-0.49, p=0.0068), co-assayed by Nanopore RT-PCR and Stage-(ii) BaseScope ISH."),
    "C015": ("HIGH_HURDLE_WATCHLIST", "Unbundling drops 5/8 vesicle passengers and excludes G2E3 Alu 0mm SSOs; YKT6 p.Tyr64Cys (P=1.5e-9) converges with PTAR1 prenylation loss, but zero ligands, a -85 A3 cavity, and Cys195 farnesyl-ejection risk limit WT sALS tractability."),
    "C016": ("HIGH_HURDLE_WATCHLIST", "Postmortem FBXL5 RNA elevation is microglial (p=0.0033) rather than excitatory neuronal (p=0.18) while ALS neuronal TFRC/IREB2 are already depleted, creating neuronal iron-starvation risk (OMIM 618451) after clinical iron-chelation failure."),
    "BA9-08": ("HIGH_HURDLE_WATCHLIST", "C9-FTD cortical homogenate/pellet SNPH accumulation (+0.46/+0.60) co-occurs with NEFH (+2.13) in proximal axonal spheroids, leaving passive transport co-trapping unresolved alongside null SOD1-G93A Snph-KO survival and pLI=0.996 constraint."),
    "C020": ("HIGH_HURDLE_WATCHLIST", "Continuous BID PIKfyve inhibition failed clinically (VRG50635 stopped; AIT-101 NfL +39%/+50%); q48h-q72h pulsed Apilimod survives solely on a 2-week postmitotic iPSC-MN gate testing vacuole/CASM washout (fails if tau >=72 h), poly(GP) mass-balance, and axonal transport."),
    "C019": ("HIGH_HURDLE_WATCHLIST", "Oral 4 mg Baricitinib reaches 3.80 nM CSF (~8.7% pSTAT occupancy; 657x below 2.5 uM screen) with 1/9 PE + 1/9 DVT in NADALS (N=9, un-deduplicated), while JAK2-sparing JAK1 inhibitors forfeit neuronal JAK2 APA rescue (sALS-vs-Ctrl CSF AUC=0.82-0.89)."),
    "S02": ("HIGH_HURDLE_WATCHLIST", "Bye 2025 2.5 uM survival (+1.38d, FDR=0.034) faces 5 hurdles: withheld Phase 2/3 NCT04082832 efficacy (hasResults=false), null Yang 2023 autopsies (n=6 vs 6), ~47x CNS gap (62Cu-PET dissociation), SOD1-mouse origin, and unverified 53 nM ferroptosis engagement."),
    "DN-14": ("HIGH_HURDLE_WATCHLIST", "Sub-FDR iPSC-MN survival (+1.31d, FDR=0.070) occurred in glia-free monocultures lacking microglial/serum C5 or C5a ligand after two negative upstream C5 ALS trials, making ligand-independent cyclic-hexapeptide off-target activity the primary null."),
    "DN-19": ("HIGH_HURDLE_WATCHLIST", "Phase 2 IRB noncompliance termination left clinical efficacy untested, but 2.5 uM screen addition shifts ~400 uM basal media L-serine by +0.625% (<1% noise), barring clinical re-entry before serine-defined media deconvolution."),
    "C005": ("MECHANISTIC_EDGE", "Late-stage AMPA blockade (Perampanel 8 mg/d -8.4 ALSFRS-R pts, p=0.015; 7 completers / 67% dropout, SAE p=0.048) shows excitability shifts to late synaptic failure, making paired TMS SICI/SDTC + intact CSF NPTX2 mandatory stage-gating for KCNQ2."),
    "C013": ("BENCHMARK_CALIBRATOR", "Approved SOC positive control ranking #1/107 in human sALS iPSC-MNs (+3.99d, FDR=0.0040) at ~2x human unbound brain concentration (0.23x NaV1.6 persistent INaP IC50), calibrating phenotypic screen sensitivity rather than novel NCE discovery."),
    "S08": ("BENCHMARK_CALIBRATOR", "PMDA-approved early-onset (<=12m) ALS benchmark (JETALS +1.97 ALSFRS-R pts, p=0.01) whose #105/107 live-imaging screen drop (-3.60d) is plausibly explained by blue-light Co-C photolysis (hypothesis requiring dark-shielded control verification)."),
    "C003": ("BENCHMARK_CALIBRATOR", "Clinically withdrawn Kv7.2/7.3 opener (retinal/tissue pigmentation, 26-30% ALS dropout) retained strictly as the quantitative human TMS SICI/SDTC pharmacodynamic calibration ruler (NCT02450552, p=0.009) for QRL-101 and C006."),
    "C017": ("BENCHMARK_CALIBRATOR", "Common human CHIT1 null homozygosity (rs3831317) leaves ALS risk/progression unchanged while GPNMB is neuroprotective, refuting inhibition and anchoring an rs3831317-neutral CSF staging panel (sALS-vs-Ctrl AUC=0.82-0.89; Thompson 2019 mimic AUC=0.51-0.92 [0.688 ext])."),
    "DN-10": ("BENCHMARK_CALIBRATOR", "Top downregulated living-CSF protein in Emory DIA (-0.50, FDR=8.2e-9) and C9-FTD cortical synaptosomes (-0.40, p=0.029), driven by C9orf72 somatodendritic Kv4.2 attrition on a catalytically inactive scaffold (PDB 1XFD)."),
    "DN-11": ("BENCHMARK_CALIBRATOR", "Paralogous Kv4 auxiliary subunit reduced in Emory/WashU living CSF (-0.32, FDR=0.044) and BA4 excitatory neurons (-1.34, p=0.0066), tracking C9orf72-weighted dendritic loss rather than sporadic-vs-control TMTpro shift (p=0.99)."),
    "DN-12": ("BENCHMARK_CALIBRATOR", "Sole upregulated de novo living-CSF protein replicating across Emory DIA, WashU DIA, and N=101 sporadic-vs-control TMTpro (p=2.27e-5), indexing axonal cofilin-actin rod release on a pan-essential gene (Chronos=-1.35)."),
}

LENS_DEFS: list[tuple[str, str]] = [
    ("ALL", "All Lenses · 59"),
    ("ISOFORM_STRUCTURAL", "Structure & Isoform Polarity · 8"),
    ("DENOVO_RNA", "De Novo Cryptic Splicing & APA · 9"),
    ("MULTIPLEX_STAGE", "Multiplex & Stage-Gated Core · 5"),
    ("BIOFLUID_SUBTYPE", "Biofluids, Subtypes & Calibrators · 10"),
    ("PK_COMPARTMENT", "PK, Polypharmacology & Compartment · 10"),
    ("FALSIFIED_TRAPS", "Confounding & RCT/PK Falsifications · 24"),
]

CANDIDATE_LENSES: dict[str, list[str]] = {
    "ISOFORM_STRUCTURAL": ["S06", "C006", "C007", "BA9-04", "DN-01", "DN-04", "DN-05", "C015"],
    "DENOVO_RNA": ["DN-01", "DN-02", "DN-03", "DN-04", "DN-05", "DN-06", "DN-07", "DN-08", "DN-09"],
    "MULTIPLEX_STAGE": ["S06", "C006", "C001", "C002", "C005"],
    "BIOFLUID_SUBTYPE": ["S07", "C013", "S08", "C003", "C017", "C019", "S09", "DN-10", "DN-11", "DN-12"],
    "PK_COMPARTMENT": ["C019", "S02", "S09", "C014", "C016", "C018", "C020", "BA9-08", "DN-14", "DN-19"],
}
