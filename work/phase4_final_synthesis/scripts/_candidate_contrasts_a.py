"""Role-calibrated mechanistic contrast strips (34 active/benchmark IDs) and non-exclusive problem lenses for CarbonALS."""
from __future__ import annotations

EDGE_ROLE_LABELS: dict[str, str] = {
    "MECHANISTIC_EDGE": "MECHANISTIC CONTRAST & KEY RISK",
    "CROWDED_MULTIPLEX": "ACTIVE CLINICAL CLASS — MULTIPLEX & TECHNICAL DELTA",
    "HIGH_HURDLE_WATCHLIST": "EXPLORATORY WATCHLIST — DOMINANT PK / BIOLOGICAL HURDLE",
    "BENCHMARK_CALIBRATOR": "CLINICAL BENCHMARK / BIOFLUID CALIBRATION BOUNDARY",
    "FALSIFIED_TRAP": "FALSIFIED MECHANISM / CONFOUNDING ARTIFACT",
}

CANDIDATE_EDGES_ACTIVE: dict[str, tuple[str, str]] = {
    "S06": ("MECHANISTIC_EDGE", "PDB 9TZY proves BEXi adduct-17 prodrugs spike WT SARM1 at washout (~2.8x empirical median, PMID:42380237), while 4-PDB octamer geometry shows inter-protomer ARM-TIR 3.07A latches, <0.08% validated GoF carriers, 3' SLC46A1 overlap, and >90% CD38-derived fluid cADPR [MODEL_PRIOR], mandating Cys311Ala-verified non-covalent T-locks and CSF trough PK."),
    "C006": ("MECHANISTIC_EDGE", "In-frame KCNQ2 Exon-5 skipping (dPSI=+0.21, FDR=4.2e-24) evades NMD with ER retention and excises Trp236 (PDB 7CR2); Tier 2 lead #3 (UG=1) avoids #1's UG8 WT TDP-43 cis-eviction hazard while [MODEL_PRIOR] AlphaGenome flags +35.2% Exon 4-6 skipping at 63442302:C>G, mandating a 50-oligo wet-lab ISE-vs-ISS microwalk."),
    "S07": ("MECHANISTIC_EDGE", "MIROCALS (PMID:40354799, N=220: <=3,700 pg/mL n=173 HR=0.57 p=0.037, int p=0.0011; ALSFRS-R int p=0.048) & Al Khleifat 2026 (PMID:42836993: TRICALS r^2=12.7%, dChi2 14.24 vs 4.76) motivate CLSI EP09c (N>=40) pNfH bridging (~1.8x-4.5x offsets; ALSTARS N=137 stratifies 3 serum NfL tiers with dual IL-2 + CTLA4-Ig)."),
    "C001": ("CROWDED_MULTIPLEX", "Keuss 2026 (Nature PMID:43015463) proved >30% UNC13A protein rescue restores human MN synaptic release orthogonally to STMN2, KCNQ2, and TDP-43 Intron-31 retention (dPSI=+0.354, capping Intron-20-only mRNA near ~58.3-61.6% of WT); shifts differentiation to clean >=2mm #2, 3-layer NDEV/secretome TE, and genotype-stratified 2-plex vs 3-plex testing."),
    "C002": ("CROWDED_MULTIPLEX", "QRL-201 ANQUR (completed N=52 DRF + ongoing N=41 3 mg OLE; pivotal CONQUR IND) dissociated 3 mg (-46%) vs 10 mg (~5%) Day-197 pNfH, anchoring a multiplex polyanion/DRG margin target (EC80<=3 mg/strand = 6-9 mg vs unvalidated 24-48 mg; BA4 rostral gradient gated) alongside parallel SARM1 T-lock protection (1.0x Bliss to ~2-7x MWC bounds)."),
    "C007": ("MECHANISTIC_EDGE", "Endothelial enrichment (+3.11 log2CPM, n=28: 21v7 Ctrl, p=0.00698; Visium spots +3.76) leaves sST2 vs ST2L & BBB-brake sign open, while PDB 4KC3 (10-Cys/5-SS) leaves Cys327 in 324-SKECF-328 unpaired (+ SLC3A2 -SKEDF 4/5 match); promotes IT CD98hc/TfR1-shuttled sST2 siRNA or Zone 1 PAS 2'-MOE SSO (#1 102346045-102346062(+))."),
    "DN-01": ("MECHANISTIC_EDGE", "TDP-43 cryptic splicing truncates ATG4B after Val319 (PDB 2Z0D: 27 LC3B contacts + FEIL LIR) with sALS cord LC3ylation (PMID:39305312); IT 2'-MOE #2 (-10 bp vs 16-nt LNA ASO 3J) cuts spliced 1-mm (10->0), 50bp-SS 1-mm (18->0), & pLI>=0.96 flags (5->0) while bypassing IV Pip8b2 Kim-1 toxicity."),
    "DN-04": ("MECHANISTIC_EDGE", "Neuron-restricted CELF5 cryptic splicing replicates in sALS iPSC-MN clu_25763_+ (N=77, padj=0.0090, PMID:41286450) & severs RRM2 beta4 H-bonds/UGUU contacts (AF-Q8N6W0/PDB 3NMR PMID:20947024); 18-nt PTC-Ex6 gap evades 3-exon minigene NMD, mandating endogenous Exon 1-7+ ONT phasing & cervical BaseScope ISH."),
    "DN-02": ("HIGH_HURDLE_WATCHLIST", "Despite 70% C9-FTD cortical penetrance and clean >=2mm SSO #1, common variant rs2173852 (AF=17.5%, 76x 5'SS drop) has zero ALS GWAS signal across 40 cohorts, pointing to low spinal expression (1.50 TPM) and alt-3'SS shunting risk."),
    "DN-06": ("HIGH_HURDLE_WATCHLIST", "Synaptosomal PFKP protein depletion (-0.51, p=0.0035, n=20 C9-FTD) and clean >=2mm SSO #1 are tempered by flat surviving cervical MN-niche Visium RNA (FDR=0.64) and risk of draining neuronal pentose-phosphate NADPH/GSH antioxidant defense."),
    "DN-07": ("HIGH_HURDLE_WATCHLIST", "Pathology-selective TRAPPC12 intronic polyadenylation (82.9% TDP+ vs 34.0% non-TDP) and sALS iPSC-MN LeafCutter splicing (padj=0.015) face null bulk C9-FTD cortical DIA proteomics (p=0.84) and co-occurring secondary cryptic-exon shunting risk."),
    "DN-08": ("HIGH_HURDLE_WATCHLIST", "TDP-43-selective ELK1 3'-extension elevates i3Neuron translation (+1.12, padj=2.3e-5) with null BA4 snRNA/regulon divergence; nuclear RNase-H1 gapmers risk Pol II readthrough cleavage of canonical ELK1 (PMID:31924448), shifting gating to steric distal-PAS SSOs or cytoplasmic 3'Ext siRNA."),
    "DN-09": ("HIGH_HURDLE_WATCHLIST", "Pathology-selective DLGAP1 cryptic polyadenylation (19.4x TDP+ enrichment) pairs with C9-FTD cortical synaptosomal protein loss (-0.74, p=0.021, n=12), but spinal motor-neuron penetrance is unproven and lumbar bulk RNA is masked by glial shifts."),
    "C022": ("MECHANISTIC_EDGE", "Mendelian dHMN5/juvenile-ALS chaperone (OMIM 614881: 25/25 single-gene ClinVar P/LP in shared Exons 2-9 vs 0/25 in Zone A; 0/6 TDP-43 cryptic shifts) with cortical oligo, cord, and synaptosomal loss; favors nuclear Intron-9 3'SS splice enhancement or DNAJB2a cDNA over Zone A CDS steric ASOs."),
    "C014": ("HIGH_HURDLE_WATCHLIST", "Post-translational SUN1-CHMP7 nuclear retention triggers NPC injury despite flat bulk RNA (iPSC pellet n=6), but extreme germline intolerance (pLI=0.9996) and sequential ANXA11-CHMP2B membrane-repair reliance penalize deep RNase-H knockdown."),
    "S09": ("HIGH_HURDLE_WATCHLIST", "Cortical ALS-TE spans 13.5% of motor ALS (0/331 bulk cord) with flat canonical ISGs; living enrichment must separate pan-TDP cryptic HDGFL2 and longitudinal CSF IL-6 PD from subtype-specific LINE-1 ORF1p/L1HS cargo and active cGAS-STING signaling."),
    "C018": ("HIGH_HURDLE_WATCHLIST", "Cervical MN-niche Visium C1QC surges (+2.37 log2FC, spot FDR=1.04e-10, N=14) despite systemic C3 futility (C024); PDB 1PK6 (1.85A gC1q head) vs AFDB cationic CLR stalk (26 Arg/Lys neuronal RNP motif, PMID:38942014) splits anti-gC1q HLE IT Fab from C1QA/B ASO alongside C-bouton safety gating."),
    "DN-03": ("HIGH_HURDLE_WATCHLIST", "Convergent Ribo-seq (-2.78, padj=1.1e-7), C9-FTD cortical DIA (-0.37, p=0.0062), and living-CSF PTPRT loss lack 1-bp cryptic-exon coordinates inside a 3.57-kb intron and carry dual synaptic-adhesion vs nuclear pSTAT3 signaling risk."),
    "DN-05": ("MECHANISTIC_EDGE", "Top Tier 3 discovery (#9/52): sole Ma cryptic-spliced gene depleted in surviving cervical MN-niche Visium spots (-1.23 log2FC, within-donor pseudoreplicated spot FDR=0.019, N=18) and C9-FTD synaptosomes (-0.49, p=0.0068), co-assayed by Nanopore RT-PCR and Stage-(ii) BaseScope ISH."),
    "C015": ("HIGH_HURDLE_WATCHLIST", "At chr14q12, G2E3 Alu Intron-1 windows fail 0mm safety, while SuSiE-inf (purityMeanR2=0.988, COLOC H4=0.958) proves rs229243-A, x-anc lead rs229195-A (PIP=0.240), rs229194-A, and rs229143-A co-segregate on one haplotype driving opposing MN (+0.048) vs iMGL (-0.22 to -0.33, PMID:43045849) SCFD1 polarity (Chronos=-1.26), barring pan-CNS knockdown."),
    "C023": ("HIGH_HURDLE_WATCHLIST", "Exome-wide YKT6 p.Tyr64Cys (<0.1% carriers, meta P=1.50e-9; PDB 3KYQ -85.1 A^3 Longin groove) pairs with TDP-43 3'UTR lengthening and PTAR1 exon skipping, but zero ligands, Cys195-farnesyl ejection risk, and pan-essential SNARE toxicity (YKT6 Chronos=-1.54, NSF -2.44) restrict intervention to positive stabilization."),
    "C016": ("HIGH_HURDLE_WATCHLIST", "Postmortem FBXL5 RNA elevation is microglial (p=0.0033) rather than excitatory neuronal (p=0.18) while ALS neuronal TFRC/IREB2 are already depleted, creating neuronal iron-starvation risk (OMIM 618451) after clinical iron-chelation failure."),
    "C020": ("HIGH_HURDLE_WATCHLIST", "Continuous BID PIKfyve blockade failed clinically via -PI(3,5)P2->ClC-7 swelling (PMID:42900584) and +PI(3)P->LRRK2/CASM activation (Life Sci Alliance PMID:42994990); pulsed q48h-q72h Apilimod drops from ~79% to ~30% at matched 10-20h repair and 0% at 24-48h CASM repair [MODEL_PRIOR], mandating a 14-day iPSC-MN washout and DPR mass-balance kill-gate."),
    "C019": ("HIGH_HURDLE_WATCHLIST", "Oral 4 mg Baricitinib reaches 3.80 nM CSF (~9% modeled pSTAT occupancy; 657x below 2.5 uM screen) with 1/9 PE + 1/9 DVT in NADALS (N=9, un-deduplicated), while JAK2-sparing JAK1 inhibitors forfeit neuronal JAK2 APA rescue (high-chitinase CSF sALS-vs-Ctrl AUC=0.82-0.89)."),
    "S02": ("HIGH_HURDLE_WATCHLIST", "Bye 2025 2.5 uM survival (+1.38d, FDR=0.034) faces 5 hurdles: withheld Phase 2/3 NCT04082832 efficacy (hasResults=false), null Yang 2023 autopsies (n=6 vs 6), ~47x CNS gap (62Cu-PET dissociation), SOD1-mouse origin, and unverified 53 nM ferroptosis engagement."),
    "DN-14": ("HIGH_HURDLE_WATCHLIST", "Sub-FDR iPSC-MN survival (+1.31d, FDR=0.070) occurred in glia-free monocultures lacking microglial/serum C5 or C5a ligand after two negative upstream C5 ALS trials, making ligand-independent cyclic-hexapeptide off-target activity the primary null."),
    "C005": ("MECHANISTIC_EDGE", "Late-stage AMPA blockade (Perampanel 8 mg/d -8.4 ALSFRS-R pts, p=0.015; 7 completers / 67% dropout, SAE p=0.048) shows excitability shifts to late synaptic failure, making paired TMS SICI/SDTC + intact CSF NPTX2 mandatory stage-gating for KCNQ2."),
    "C013": ("BENCHMARK_CALIBRATOR", "Approved SOC positive control ranking #1/107 in human sALS iPSC-MNs (+3.99d, FDR=0.0040) at ~2x human unbound brain concentration (0.23x NaV1.6 persistent INaP IC50), calibrating phenotypic screen sensitivity rather than novel NCE discovery."),
    "S08": ("BENCHMARK_CALIBRATOR", "PMDA-approved early-onset (<=12m) ALS benchmark (JETALS +1.97 ALSFRS-R pts, p=0.01) whose #105/107 live-imaging screen drop (-3.60d) is plausibly explained by blue-light Co-C photolysis (hypothesis requiring dark-shielded control verification)."),
    "C003": ("BENCHMARK_CALIBRATOR", "Clinically withdrawn Kv7.2/7.3 opener (retinal/tissue pigmentation, 26-30% ALS dropout) retained strictly as the quantitative human TMS SICI/SDTC pharmacodynamic calibration ruler (NCT02450552, p=0.009) for QRL-101 and C006."),
    "C017": ("BENCHMARK_CALIBRATOR", "Common human CHIT1 null homozygosity (rs3831317) leaves ALS risk/progression unchanged while GPNMB is neuroprotective, refuting inhibition and anchoring an rs3831317-neutral CSF staging panel (sALS-vs-Ctrl AUC=0.82-0.89; Thompson 2019 mimic AUC=0.51-0.92 [0.688 ext])."),
    "DN-10": ("BENCHMARK_CALIBRATOR", "Top downregulated living-CSF protein in Emory DIA (-0.50, FDR=8.2e-9) and C9-FTD cortical synaptosomes (-0.40, p=0.029), driven by C9orf72 somatodendritic Kv4.2 attrition on a catalytically inactive scaffold (PDB 1XFD)."),
    "DN-11": ("BENCHMARK_CALIBRATOR", "Paralogous Kv4 auxiliary subunit reduced in Emory/WashU living CSF (-0.32, FDR=0.044) and BA4 excitatory neurons (-1.34, p=0.0066), tracking C9orf72-weighted dendritic loss rather than sporadic-vs-control TMTpro shift (p=0.99)."),
    "DN-12": ("BENCHMARK_CALIBRATOR", "Sole upregulated screen-nominated living-CSF protein replicating across Emory DIA, WashU DIA, and N=101 sporadic-vs-control TMTpro (p=2.27e-5); sALS spinal MN Ser3-cofilin hyperphosphorylation triggers TDP-43 pathology (PMID:41804798), motivating CSF pSer3-CFL1:total ratios on a pan-essential gene (Chronos=-1.35)."),
}

LENS_DEFS: list[tuple[str, str]] = [
    ("ALL", "All Lenses · 52"),
    ("ISOFORM_STRUCTURAL", "Structure & Isoform Polarity · 9"),
    ("TDP43_RNA", "TDP-43 Splicing & Polyadenylation · 12"),
    ("MULTIPLEX_STAGE", "Multiplex & Excitability Core · 5"),
    ("BIOFLUID_SUBTYPE", "Biofluids, Subtypes & Calibrators · 10"),
    ("PK_COMPARTMENT", "PK, Polypharmacology & Compartment · 8"),
    ("FALSIFIED_TRAPS", "Confounding & RCT/PK Falsifications · 18"),
]

CANDIDATE_LENSES: dict[str, list[str]] = {
    "ISOFORM_STRUCTURAL": ["S06", "C006", "C007", "C022", "DN-01", "DN-04", "DN-05", "C015", "C023"],
    "TDP43_RNA": ["C001", "C006", "C002", "DN-01", "DN-02", "DN-03", "DN-04", "DN-05", "DN-06", "DN-07", "DN-08", "DN-09"],
    "MULTIPLEX_STAGE": ["S06", "C006", "C001", "C002", "C005"],
    "BIOFLUID_SUBTYPE": ["S07", "C013", "S08", "C003", "C017", "C019", "S09", "DN-10", "DN-11", "DN-12"],
    "PK_COMPARTMENT": ["C019", "S02", "S09", "C014", "C016", "C018", "C020", "DN-14"],
}
