"""Translational Monograph Standard v3.1 (5Rs + Open Targets + Script/Checksum Provenance) — Part 3: #6 DN-01 (Tier 2) & #7 DN-04 (Tier 3 Deep-Dive)."""
from __future__ import annotations

MONOGRAPH_SPECS_T2B: dict[str, dict] = {
    "DN-01": {
        "subtitle": "Transcriptome-Wide Cryptic-Splice Lead: Steric SSO (#2, 0 <=1-mm Off-Targets) Restoring Autophagy Protease ATG4B & C-Terminal LIR",
        "ident": [
            ("Gene / HGNC", "ATG4B (HGNC:20790)"), ("MANE", "ENST00000404914.8 (+)"), ("UniProt", "Q9Y4P1 (393 aa)"),
            ("3D Crystal", "PDB 2Z0D (ATG4B–LC3B)"), ("IDG TDL / ChEMBL", "Tchem (Inh Only) · CHEMBL1741221"),
            ("Promoted SSO", "#2 chr2:241668970-241668987(+)"),
        ],
        "grades": [
            ("C9-FTD Brain DIA & sALS Cord", "Spillman C9-FTD DIA -0.491 (p=0.023, FDR=0.148, PMID:42789089); Torres 2024 sALS cord LC3ylation (PMID:39305312)"),
            ("Ribo-seq, ASO 3J & 3D Crystal", "Ribo-seq -1.550 (PMID:35197628); Torres ASO 3J mRNA rescue; PDB 2Z0D + Q9Y4P1 FEIL LIR"),
            ("Head-to-Head vs ASO 3J Scan", "Promoted #2 (-10 bp vs ASO 3J): spliced 1mm 10->0, 50bp-SS 1mm 18->0, pLI>=0.96 flags 5->0 (DNA AVI=16.16)"),
        ],
        "verdict_box": {
            "pass_gate": (
                "- Graded Human iPSC-MN Rescue & Safety Microwalk: SSO #2 vs #1 and Torres 2024 16-nt LNA ASO 3J benchmark (plus 1-nt microwalk and Ca2+/Mg2+-formulated human neuron Ca2+-oscillation, PS-protein-binding, and DRG safety screens, PMID:39305312, PMID:31036929, PMID:35166597, PMID:39460376) across graded 30%/60%/90% TDP-43-CRISPRi human iPSC-MNs restores full-length ATG4B protein and normalizes membrane LC3ylation (with ATG4A/C/D paralog, CLN6/DOCK3/SNRNP200 off-target splicing, and N-terminal ~39 kDa immunoblot checks).\n"
                "- Single-Neuron Cervical Alpha-MN Penetrance: Stage-(ii) partially nuclear-TDP-43-depleted / pre-inclusion surviving cervical (C3–C8) lamina IX alpha-MN ChAT + nuclear TDP-43 + duplex BaseScope ISH across <18–24 mo sALS vs SOD1/FUS-ALS negative-TDP controls (co-assaying ATG4B, CELF5, #8 DN-05 PRUNE2, KCNQ2-DeltaE5, and tSTMN2) plus FACS RT-ddPCR confirms single-MN cryptic-exon penetrance."
            ),
            "kill_gate": (
                "- Negligible Alpha-MN Cryptic Splicing: Cryptic exon PSI <2% in Stage-(ii) partially TDP-43-depleted cervical sALS vs SOD1/FUS-ALS alpha-MNs by BaseScope/LCM RT-ddPCR.\n"
                "- Neuronal Toxicity or Redundant Paralog Buffering: Acute human neuron Ca2+-oscillation/DRG neurotoxicity, or zero rescue of human iPSC-MN ATG4B protein and LC3 delipidation beyond paralog ATG4A/C/D buffering."
            ),
        },
        "related": ["DN-04", "DN-05", "C001", "C023", "S06"],
        "causal": {
            "callout_kind": "RATIONALE",
            "nodes": [
                ("Nuclear TDP-43 Depletion", "Derepresses 111-bp cryptic exon chr2:241668875-241668985(+) after Exon 10 Val319 (PMID:26250685; PMID:29912613; PMID:35197628; DOI:10.1186/s44477-025-00013-w)"),
                ("2 In-Frame TGA PTCs (Codons 33, 35)", "Triggers NMD (-1.55 Ribo-seq) OR C-terminally truncated ATG4B(1–319+32aa)"),
                ("Loss of aa 320–393 LC3B Patch & LIR", "Deletes 27 LC3B contacts (PDB 2Z0D) + FEIL LIR (aa 388–391, PMID:28287329) -> sALS cord LC3ylation (PMID:39305312)"),
                ("IT Steric SSO (#2 Lead, 0 <=1-mm)", "chr2:241668970-241668987(+) (-10 bp vs Torres ASO 3J: spliced 1mm 10->0, 50bp-SS 1mm 18->0; proposed IT route vs IV Pip8b2)"),
            ],
            "trap_title": "MODALITY & BENCHMARK RATIONALE: Why IT 2'-MOE #2 Beats ChEMBL Ligands & Benchmark ASO 3J / IV Pip8b2-PMO",
            "trap_desc": "All 995 ChEMBL ATG4B records (CHEMBL1741221) are inhibitors (0/995 activators). In Torres et al. 2024 (PMID:39305312, PMC11416411 Table 3), unconjugated 16-nt 6-LNA/15-PS ASO 3J (chr2:241668980-241668995(+); heuristic 6-LNA Tm ~80.1C / 1-mm ~74.1C) carries 10 spliced 1-mm (CLN6, DOCK3), 18 50bp-SS 1-mm, & 5 pLI>=0.96 CNS sequence hits (while separate IV 25-nt Pip8b2-ATG4B peptide-PMO caused transient Day-2 mouse urinary KIM-1 elevation, motivating empirical safety testing of naked IT 2'-MOE #2).",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron CE PSI (PMID:35197628)", "val": 0.243, "stat": "dPSI = +0.243", "p": "FDR=1.16e-11", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq ATG4B (PMID:35197628)", "val": -1.550, "stat": "-1.550 log2FC", "p": "padj=5.78e-6", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Spillman C9-FTD Homogenate DIA (n=20, PMID:42789089)", "val": -0.491, "stat": "-0.491 log2FC", "p": "p=0.0227 · FDR=0.148", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Cervical ALS-Ox OLS (n=139, GSE153960)", "val": -0.270, "stat": "-0.270 log2CPM", "p": "p=1.14e-7", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Head-to-head #2 (18bp 2'-MOE) vs Torres ASO 3J (16bp LNA)", "stat": "0/0/0 vs 10/18/5 flags", "p": "1mm/50bp-SS/pLI", "tag": "MEASURED"},
                {"lbl": "NYGC Cervical neuronal-adj tSTMN2 slope (n=162, GSE153960)", "stat": "beta=-0.564 (6.2% tail)", "p": "p=2.16e-6", "tag": "MEASURED"},
                {"lbl": "PDB 2Z0D (aa 320–354) + Q9Y4P1 FEIL LIR (aa 388–391)", "stat": "-27 LC3B contacts + LIR", "p": "min 2.7A", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 ATG4B Intron 10–11 Cryptic Exon: #2 vs #1 & Torres 2024 ASO 3J Benchmark (chr2, +)",
            "caption": "Coordinate-only target window #2 (chr2:241668970-241668987(+), 0 chemically modified synthesis-ready ASO sequences, modeled 2'-MOE Tm ~67.2C, DNA AVI=16.16) shifts 10 bp upstream of Torres et al. 2024 16-nt LNA ASO 3J (chr2:241668980-241668995(+), PMID:39305312) into the exonic 5'SS core, cutting spliced 1-mm (10->0), 50bp-SS 1-mm (18->0), and pLI>=0.96 CNS flags (5->0) while sparing chr2:241668860.",
            "strand": "+", "chrom": "chr2", "win_lo": 241668500, "win_hi": 241670820,
            "zoom_lo": 241668850, "zoom_hi": 241669015,
            "exons": [
                {"lbl": "Exon 10 (Val319)", "lo": 241668540, "hi": 241668685, "kind": "canon"},
                {"lbl": "Cryptic Exon (111bp, PTCs 33/35)", "lo": 241668875, "hi": 241668985, "kind": "ce"},
                {"lbl": "Exon 11", "lo": 241670726, "hi": 241670782, "kind": "canon"},
            ],
            "snps": [{"lbl": "rs-annot 241668860 (Spared)", "pos": 241668860}],
            "zoom_spans": [
                {"lbl": "Torres 2024 ASO 3J: 241668980-241668995(+) (16bp LNA)", "sub": "mRNA 1mm=10 · 50bp-SS 1mm=18 · 5 pLI>=0.96 flags", "lo": 241668980, "hi": 241668995, "tone": "hazard"},
            ],
        },
        "safety": [
            ("Het-pLoF Constraint & KO Context", "LOW", "gnomAD v4.1 MANE pLI = 2.08e-6, LOEUF = 0.851 (29/46.5 LoF; Open Targets / gnomAD v4.1.1 pLI = 3.35e-4, LOEUF = 0.699; Atg4b-/- mice otoconia defects PMID:20577052 & accelerated SOD1 ALS PMID:39305312)"),
            ("Dividing-Line Paralog Buffering", "LOW", "DepMap median Chronos = -0.031 in dividing lines (ATG4A/C/D buffer mitosis, but do not prevent CNS LC3ylation pathology)"),
            ("Proposed IT 2'-MOE vs IV Pip8b2-PMO", "GATE", "GTEx Cervical = 30.3 / BA9 = 41.8 TPM; naked IT 2'-MOE is proposed to mitigate systemic IV cationic Pip8b2-ATG4B 25-nt peptide-PMO transient Day-2 murine urinary KIM-1 exposure (PMID:39305312), requiring empirical IT safety testing"),
            ("Head-to-Head vs ASO 3J Sequence Scan", "GATE", "Promoted #2 CAUTION (sequence scan: mRNA 1mm=0, 50bp-SS 1mm=0, 25bp-SS 2mm=2, 0 pLI flags vs 16-nt 6-LNA ASO 3J mRNA 1mm=10 [CLN6/DOCK3], 50bp-SS 0mm=1, 50bp-SS 1mm=18, 5 pLI flags); empirical PS protein-binding/DRG screens required (PMID:31036929; PMID:39460376)"),
            ("In Vivo & ASO 3J Directionality Proof", "LOW", "Torres et al. 2024 (PMID:39305312) proved Atg4b-KO accelerates SOD1 ALS and RNAiMAX-transfected 16-nt 6-LNA ASO 3J rescues canonical mRNA in TARDBP-KD HeLa cells"),
        ],
        "struct_note": "PDB 2Z0D (Satoo et al. 2009, PMID:19322194, Thr5–Gln354 H280A): catalytic Cys74/Asp278/His280A sits 2.9A from LC3B Gly120, while Exon-10 Val319 truncation deletes 73 intra-chain residue-pair contacts (<=4.0A) & 27 heavy-atom contacts (<=4.5A, min 2.7A) to LC3B Val89–Val91 inside 2Z0D, plus the downstream disordered C-terminal FEIL LIR (UniProt Q9Y4P1 aa 388–391, PMID:28287329).",
        "sections": [
            ("Right Target: Causal Biology & Human Genetics", (
                "- Cryptic Exon-10a & Translational Loss: ATG4B (ENSG00000168397, Q9Y4P1; gnomAD v4.1 MANE LOEUF = 0.851; Open Targets / gnomAD v4.1.1 LOEUF = 0.699) emerged as the #1 transcriptome-wide cryptic-splicing lead via cryptic Exon-10a inclusion (+0.243 dPSI, FDR=1.16e-11; Ling et al. 2015 PMID:26250685; Torres et al. 2018 PMID:29912613; Newton et al. 2026 DOI:10.1186/s44477-025-00013-w) and Ribo-seq loss (-1.550 log2FC, padj=5.78e-6; Brown et al. 2022, PMID:35197628).\n"
                "- Human sALS Cord Pathology & In Vivo Proof: Converges with sporadic ALS spinal-cord ATG4B depletion and insoluble membrane protein LC3ylation (Fig. 1c, 1e) plus in vivo proof that Atg4b loss accelerates motor neurodegeneration in mice (Torres et al. 2024, PMID:39305312; otoconia baseline phenotype Mariño et al. 2010 PMID:20577052)."
            )),
            ("Right Tissue: Human CNS Pathology & Assay Considerations", (
                "- i3Neuron & Postmortem Proteomics: WTC11 NGN2 cortical i3Neuron TARDBP-KD proteomics confirmed ATG4B depletion (-1.183 log2FC, p=1.10e-7, padj=1.32e-5, Table S1; Kozareva et al. 2025 PMID:41256508 [PREPRINT]) alongside GABARAP (-0.972, padj=1.01e-5) and GABARAPL2 (-0.475, padj=2.94e-4; Table S15 reanalysis of Guise et al. 2024 PMID:38183652 staged single-LCM spinal MNs [3 ALS / 75 cells, mean age 74.7 yr vs 2 CTL / 25 cells, mean age 48.0 yr; cell-level] GABARAPL2 mod -1.571, padj=6.14e-6) and C9-FTLD frontal cortex ATG4B depletion (-1.273 log2FC, p=3.68e-4, FDR=0.00600, Table S15).\n"
                "- Cortical DIA, Compartment Decay & Spinal Transcriptomics: Spillman et al. 2026 C9-FTD frontal homogenate DIA showed nominal reduction (-0.491 log2FC, p=0.0227, BH-FDR=0.148, n=20; PMID:42789089, PXD083082; no statistically significant synaptosomal difference detected; Miedema et al. 2025 FTLD-TDP-C temporal cortex DIA bulk ATG4B unchanged log2FC=0.000, p=1.00, q=1.00) alongside direct sporadic ALS spinal cord ATG4B loss and LC3ylation (Torres et al. 2024 PMID:39305312), despite flat bulk cortical mRNA (p=0.738). Depth-filtered TDP-43-KD i3Neuron compartment RNA-seq (Dargan et al. 2025 GSE299341 PMID:40737092) confirms cytoplasmic and axonal depletion (Soma -0.522 p=8.26e-4; Neurite -0.617 p=7.78e-5) following nuclear sparing/non-depletion (NS) in sorted TDP-43-low excitatory nuclei (+0.310, p=0.108, n=8 QC-passing paired donors of 10 FANS-seq M1 samples; Ruf et al. 2026 PMID:41803120).\n"
                "- End-Stage Cord Attrition Caveat: In NYGC cervical cord (GSE153960, n=197), ATG4B drops in ALS-TDP (-0.164, p=0.0010; ALS-Ox p=1.14e-7) and tracks neuronal-mass-adjusted tSTMN2 (p=2.16e-6, 6.2% tail); yet because 69.7% of non-cryptic neuronal genes remain negatively correlated with tSTMN2 in end-stage cord and small-n ALS-SOD1/FUS (n=9, adj p=0.270) is underpowered to prove equivalence, single-neuron Stage-(ii) pre-inclusion cervical alpha-MN BaseScope ISH remains decisive."
            )),
            ("Right Modality & Exposure: CNS PK/PD, Selectivity & Clinical Landscape", (
                "- Why Small Molecules Fail: Although ATG4B carries IDG Tchem status via oncology screens, all 995 ChEMBL records (CHEMBL1741221) inhibit catalysis rather than rescuing Exon-10 Val319 truncation (PDB 2Z0D, PMID:19322194; Q9Y4P1 FEIL LIR, PMID:28287329; Kozareva et al. 2025 PMID:41256508 [PREPRINT]).\n"
                "- Published Rescue Constructs (Torres 2024): Torres et al. 2024 (PMID:39305312, PMC11416411 Fig. 6 & Table 3; 0 specific ATG4B ASO patent families or clinical trials) tested (1) unconjugated 16-nt 6-LNA/15-PS mixmer ASO 3J across the cryptic 5'SS (chr2:241668980-241668995(+)), rescuing canonical ATG4B mRNA in Lipofectamine RNAiMAX-transfected (5–100 nM) TARDBP-KD HeLa cells (Fig. 6c), and (2) systemic IV 25-nt peptide-PMO Pip8b2-ATG4B (10 mg/kg, Fig. 6a,b), reaching mouse brain while causing transient Day-2 urinary KIM-1 elevation (normalized by Day 7).\n"
                "- Head-to-Head Window #2 Off-Target & WT AlphaGenome v1 Polarity Check: GENCODE v46 + GGGenome scanning shows 16-nt ASO 3J matches 10 spliced 1-mm genes (CLN6, DOCK3), 1 exact 0-mm <=50bp splice site, 18 1-mm <=50bp splice sites, 7 1-nt bulges, and 5 pLI>=0.96 constrained CNS genes (DOCK3, SNRNP200, PSMA5, KHDC4, SNU13; heuristic 6-LNA Tm ~80.1C / 1-mm ~74.1C [MODEL_PRIOR]), whereas candidate 18-bp intrathecal 2'-MOE window #2 (chr2:241668970-241668987(+), shifted 10 bp upstream with an 8-bp cryptic 5'SS overlap chr2:241668980-241668987(+), UG=4, modeled 2'-MOE Tm ~67.2C) cuts those hits to 0/0/0/0 while proposing naked intrathecal CSF dosing for lower renal exposure. Evaluated strictly as an in silico WT TDP-43-intact 1-nt DNA-substitution proxy (valid as a WT canonical-safety guard; unable to simulate 20-nt steric footprints or TDP-43-KD derepression; canonical Exon-10 5'SS knockout positive control chr2:241668686 disrupts canonical splicing across 3/3 alternate alleles), WT AlphaGenome v1 directional polarity across motor neurons, C1 spinal cord, and frontal cortex shows 3/3 concordant canonical-enhancing shifts at the shared cryptic 5'SS bases (tested chr2:241668986, 241668987, 241668990, serving both LeafCutter cryptic acceptors at 241668782 and 241668875) while window #2 exonic interior (241668979) stays WT-neutral."
            )),
            ("Right Patient: Stratification & Combination Positioning", (
                "- Graded Human iPSC-MN Rescue: Extending Torres et al. 2024's HeLa mRNA rescue, graded (30%/60%/90%) TDP-43-CRISPRi human iPSC-MN microwalk testing (#2 vs #1 and ASO 3J benchmark, plus WT neuron UG=4 cis-eviction and Ca2+-oscillation/DRG checks, PMID:35166597, PMID:39460376) must confirm full-length ATG4B protein recovery and normalization of endogenous LC3ylation after controlling for ATG4A/C/D paralog buffering.\n"
                "- Pre-Inclusion Cervical Alpha-MN Gate: ChAT + nuclear TDP-43 + duplex BaseScope splice-junction ISH in Stage-(ii) partially nuclear-TDP-43-depleted / pre-inclusion cervical (C3–C8) lamina IX alpha-MNs across <18–24 mo short-duration sALS vs SOD1/FUS-ALS negative-TDP controls (co-assaying ATG4B, CELF5, #8 DN-05 PRUNE2, KCNQ2-DeltaE5, and tSTMN2 on the same tissue block) gates progression toward single-entity GLP IT tox."
            )),
        ],
    },
    "DN-04": {
        "subtitle": "Transcriptome-Wide Cryptic-Splice Lead: 20-bp Steric SSO (#1, >=2-mm Off-Target Margin) Rescuing Neuron-Specific Splicing Regulator CELF5",
        "ident": [
            ("Gene / HGNC", "CELF5 (HGNC:14058)"), ("MANE", "ENST00000292672.7 (+)"), ("UniProt / 3D", "Q8N6W0 · AF-Q8N6W0-F1 / CELF1 3NMR"),
            ("Patient Cluster", "Bye clu_25763_+ padj=0.0090 (Junction RT-PCR Req.)"), ("IDG TDL · Modality", "Tbio · Intrathecal 2'-MOE SSO"),
            ("Promoted SSO", "#1 chr19:3278299-3278318(+)"),
        ],
        "grades": [
            ("Patient Cluster & Cord", "ID-MND Bye sALS N=77 clu_25763_+ padj=0.00904 (PMID:41286450, junction RT-PCR req.); Newton 2026 cord/BA4 qPCR"),
            ("Ribo-seq, MS & 3D RRM2", "Ribo-seq -1.375 (PMID:35197628); Seddighi 2024 MS/WB (PMID:38277467) & Kozareva 2025 MS; AF-Q8N6W0 / 3NMR"),
            ("Off-Target Screen & 18-nt EJC", "#1 Pass (>=2 mismatches across GENCODE v46 / GGGenome, 25bp-SS 2mm=0); conditional 108-nt PTC c30 sits 18 nt (<50 nt) from CE-Ex6"),
        ],
        "verdict_box": {
            "pass_gate": (
                "- Patient iPSC-MN Cluster Resolution & Endogenous Rescue: SSO #1 vs #2 (plus 10-oligo distal CE 5'SS microwalk and Ca2+/Mg2+-formulated Ca2+-oscillation/DRG safety screens) in Australian ID-MND Bye sALS patient iPSC-MNs (PMID:41286450) tests whether this cryptic junction accounts for unlocalized LeafCutter cluster clu_25763_+ (Table 6 row 228 lacks coordinates; testing the conditional 108-bp chr19:3278209-3278316(+) model alongside Brown MOESM11 107-nt exit row 3278316-3281199 & Faura 2025 267-aa upstream acceptor model) and achieves >=70% suppression on endogenous multi-exon transcripts (for the specified conditional 108-nt transcript, 3-exon Exon5–CE–Exon6 minigenes score primary splice %PSI choice, but evade canonical EJC-NMD because calculated PTC codon 30 sits 18 nt [<50–55 nt, PMID:9671053] upstream of CE–Exon 6).\n"
                "- Long-Read Multi-Exon Phasing & Protein Recovery: Single-molecule Exon 1–7+ Oxford Nanopore / Iso-Seq sequencing (>=1,000–5,000 reads, resolving unphased upstream novel 3'-acceptor junction 3225618-3244124 dPSI=+0.1218 vs CE dPSI=+0.3471) shows canonical Exon-5 skipping <1–2% LOQ, 98-bp micro-intron retention (98 mod 3 = 2 frameshift: ~2.8% WT -> 18.2% TDP-43 KD) restored to <=WT baseline, and CELF5 protein recovery.\n"
                "- Single-Neuron Cervical Alpha-MN Penetrance: ChAT + nuclear TDP-43 + duplex BaseScope ISH confirms penetrance in Stage-(ii) partially TDP-43-depleted cervical (C3–C8) alpha-MNs (<18–24 mo sALS vs SOD1/FUS-ALS)."
            ),
            "kill_gate": (
                "- Exon-5 Skipping, Micro-Intron Retention, or Upstream Acceptor Block: Canonical Exon-5 skipping >5%, post-SSO 98-bp micro-intron retention (98 mod 3 = 2 frameshift) exceeding WT vehicle baseline by >5% / latent 5'SS shunting >5%, or unrescued upstream novel 3'-acceptor junction 3225618-3244124 splicing blocking >50% functional protein recovery on Exon 1–7+ Nanopore sequencing.\n"
                "- Absent Patient Cluster Overlap, Neurotoxicity, or Null Cord ISH: Absence of cryptic junction splicing in sALS patient iPSC-MNs (unresolved from unlocalized clu_25763_+), acute neuron Ca2+/DRG neurotoxicity, or absent CELF5 cryptic splicing in Stage-(ii) cervical sALS alpha-MNs."
            ),
        },
        "related": ["DN-01", "DN-05", "C001", "C006"],
        "causal": {
            "callout_kind": "CAUTION",
            "nodes": [
                ("TDP-43 Loss in sALS Motor Neurons", "Conditional 108-bp CE chr19:3278209-3278316(+), ID-MND Bye N=77 clu_25763_+ (padj=0.00904), & Newton 2026 cord qPCR"),
                ("PTC c30 (18-nt Gap) & RRM2 beta4 Loss", "Endogenous NMD (24.8%->44.6% on NMD block, PMID:40672339; 38.6% Ribo-seq); conditional Pro201 cut severs 5 beta4–beta1 H-bonds"),
                ("Neuronal RNA-Binding Network Collapse", "#1 sharpest lumbar neuronal-adj tSTMN2 coupling (0.14% tail, p=2.5e-11, GSE153960)"),
                ("20-bp Distal CE 5'SS SSO (#1 Lead)", "chr19:3278299-3278318(+) (inside WO2023237638 SEQ ID 463); Exon 1–7+ ONT resolves multi-LSV phasing"),
            ],
            "trap_title": "CONDITIONAL 5'-ACCEPTOR PHASING & 18-NT EJC RULE: Multi-LSV Denominators & Minigene Caveat",
            "trap_desc": "Under the conditional 108-nt Ex5->CE->Ex6 frame, codon-30 PTC sits 18 nt (<50–55 nt, PMID:9671053) upstream of CE–Exon 6, so 3-exon minigenes score splice %PSI but evade EJC-NMD (endogenous NMD block lifts CE 24.8%->44.6%, PMID:40672339); Brown MOESM11 (107-nt exit 3278316-3281199 +0.3471, upstream novel 3'-acceptor junction 3225618-3244124 +0.1218; cf. Faura 2025 267-aa model) requires long-read phasing.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron CE donor LSV (KD PSI=0.367, PMID:35197628)", "val": 0.347, "stat": "dPSI = +0.347", "p": "FDR=2.83e-22", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq CELF5 (38.6% residual, PMID:35197628)", "val": -1.375, "stat": "-1.375 log2FC", "p": "padj=5.65e-7", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Pineda BA4_Exc full-GC OLS (n=32, nominal)", "val": -0.768, "stat": "-0.768 log2FC", "p": "p=0.0133 · FDR=0.136", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Cervical RIN+GC OLS (n=197, GSE153960)", "val": -0.402, "stat": "-0.402 log2CPM", "p": "p=0.0172", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "ID-MND Bye 2025 sALS clu_25763_+ (Table 6 r228, overlap unres.)", "stat": "loglr=12.45 (65v12)", "p": "padj=0.00904", "tag": "MEASURED"},
                {"lbl": "Zeng 2025 NMD-inhibition cryptic PSI rescue (PMID:40672339)", "stat": "24.8% -> 44.6% PSI", "p": "FDR=0.0235", "tag": "MEASURED"},
                {"lbl": "Structurally inferred AF-Q8N6W0 / CELF1 3NMR Pro201 cut", "stat": "-5 H-bonds · -6/17 UGUU", "p": "108-nt calc. 18nt EJC", "tag": "MODEL_PRIOR"},
                {"lbl": "NYGC Lumbar neuronal-adj tSTMN2 coupling (n=141, GSE153960)", "stat": "Top 0.14% tail", "p": "p=2.54e-11", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 CELF5 98-bp Micro-Intron, Conditional 108-bp CE (18-nt EJC Gap) & 20-bp SSO #1 (chr19, +)",
            "caption": "Exon 5 (Pro201 inside RRM2) ends at 3,278,110 and the conditional 108-bp CE starts at 3,278,209 (98-bp micro-intron: ~2.8% WT -> 18.2% TDP-43 KD; conditional CE PTC c30 sits 18 nt upstream of CE–Exon 6, requiring endogenous Exon 1–7+ transcripts for NMD & upstream-acceptor phasing). Target window #1 (chr19:3278299-3278318(+), 20bp, inside WO2023237638A1 SEQ ID NO: 463) passes with >=2 mismatches across GENCODE v46 / GGGenome mRNA and pre-mRNA checks (0 bp from splice boundary, 25bp-SS 2mm=0).",
            "strand": "+", "chrom": "chr19", "win_lo": 3277980, "win_hi": 3281400,
            "zoom_lo": 3278020, "zoom_hi": 3278345,
            "iv_notes": {
                "1": "Exon 1-7+ ONT req. for NMD & multi-LSV phasing",
            },
            "exons": [
                {"lbl": "Exon 5 (80bp, Pro201/RRM2)", "lo": 3278031, "hi": 3278110, "kind": "canon"},
                {"lbl": "Cryptic Exon (108bp cond., PTC c30)", "lo": 3278209, "hi": 3278316, "kind": "ce"},
                {"lbl": "Exon 6 (147bp)", "lo": 3281199, "hi": 3281345, "kind": "canon"},
            ],
            "snps": [{"lbl": "PTC c30 (18nt to 5'SS)", "pos": 3278298}],
            "spans": [{"lbl": "98bp Micro-Intron (~2.8% WT)", "lo": 3278111, "hi": 3278208}],
        },
        "safety": [
            ("Restoration on pLI=1.00 Neuronal RBP", "MITIGATED", "gnomAD v4.1 MANE pLI = 1.00, LOEUF = 0.248 (6/47.7 LoF; Open Targets / gnomAD v4.1.1 LOEUF = 0.216, 6/54.9); mandates <1–2% Exon-5 skip"),
            ("Unliganded Tbio & Dividing-Line Context", "GATE", "Unliganded Tbio RBP (0 prior clinical drugs; dividing-line DepMap Chronos = -0.130 does not certify mature neuronal RBP safety)"),
            ("6.18x GTEx CNS Enrichment", "LOW", "BA9 = 43.1 & Cerebellum = 60.2 TPM vs max non-CNS Testis = 6.97 (Heart/Liver <0.2 TPM)"),
            ("GENCODE v46 Reference Hybridization", "GATE", "20-bp #1 passes with >=2 mismatches across GENCODE v46 / GGGenome mRNA and pre-mRNA checks (0 bp from splice boundary, 25bp-SS 2mm=0); empirical PS protein-binding & DRG screens required (PMID:31036929; PMID:39460376)"),
            ("Long-Read Phasing & Endogenous EJC Gate", "GATE", "Exon 1–7+ Nanopore (>=1,000–5,000x; 3-exon minigenes score %PSI only, not EJC-NMD) verifies <1–2% Exon-5 skip, <=WT 98-bp retention (~2.8%), & upstream 3225618-3244124 phasing"),
        ],
        "struct_note": "AF-Q8N6W0-F1-v6 & paralogous CELF1 crystal homolog PDB 3NMR (Teplova et al. 2010, PMID:20947024, CELF1 RRM1–RRM2:UGUU; no experimental CELF5 RRM2 structure): RRM1 (aa 46–121, pLDDT=91.8) and RRM2 (aa 134–214, pLDDT=90.9) make 0 inter-domain contacts <=4.5A (cross-PAE 21.3A); under the conditional 108-nt Exon5->CE->Exon6 frame, Exon-5 Pro201 truncation (230 aa; vs 267-aa prediction under alternative upstream 5' acceptor usage in Faura et al. 2025 DOI:10.1007/s00401-025-02901-7) excises RRM2 beta-4 (aa 202–214) + RRM3, severing 5 anti-parallel beta4–beta1 backbone H-bonds (<=3.5A), 44 core packing pairs, and 6/17 projected UGUU-contacting RRM2 residues mapped onto CELF1 3NMR, pointing to primary LoF + unfolded RRM2(134–201)+29aa chaperone burden rather than competitive RNA dominant-negativity.",
        "sections": [
            ("Right Target: Causal Biology & Human Genetics", (
                "- Constrained Neuronal Splicing Regulator: CELF5 (ENSG00000161082, HGNC:14058, Q8N6W0; gnomAD v4.1 MANE pLI = 1.00, LOEUF = 0.248 [6/47.7 LoF; Open Targets / gnomAD v4.1.1 LOEUF = 0.216, 6/54.9]) was first identified as a murine Tdp-43 cryptic-splicing target by Fratta et al. 2018 (PMID:29764981) and validated in human TDP-43-depleted i3Neurons via cryptic-peptide MS and Western blot by Seddighi et al. 2024 (PMID:38277467).\n"
                "- Patient iPSC-MN Cluster Signal (Unresolved Coordinates): Differential splicing at CELF5 is detected in unperturbed Australian ID-MND sporadic ALS patient iPSC-MNs (distinct from US Answer ALS) at LeafCutter cluster clu_25763_+ (loglr=12.45, padj=0.00904 across N=77 [65 sALS vs 12 Ctrl at Day 49, without bulk nuclear TDP-43 IF depletion P=0.990]; Bye et al. 2025 PMID:41286450, DOI:10.1038/s41593-025-02118-7; Table 6 row 228 omits genomic coordinates and raw BAMs sit on controlled-access EGA, requiring RT-PCR/Nanopore junction confirmation).\n"
                "- Human Postmortem & NMD Replication: Supported by ALS lumbar cord & motor cortex cryptic junction RT-qPCR (Newton et al. 2026 DOI:10.1186/s44477-025-00013-w), FTLD-TDP cortex RNA-seq (dPSI=0.0305, Faura et al. 2025 DOI:10.1007/s00401-025-02901-7), ALS cortex/cord Western blot (Liu et al. Mar 2026 UMich RNA Symp Poster 28), i3Neuron RNA-seq (-0.887 log2FC = 54.1% residual) & Ribo-seq loss (-1.375 log2FC = 38.6% residual, padj=5.65e-7; Brown et al. 2022 PMID:35197628; Humphrey et al. 2023 PMID:36482247), and NMD-inhibition rescue (24.8% -> 44.6%, FDR=0.0235; Zeng et al. 2025 PMID:40672339 [PREPRINT], PMC12265704 Fig. 2b / Table S8)."
            )),
            ("Right Tissue: Human CNS Pathology & Assay Considerations", (
                "- i3Neuron Compartment Decay vs Bulk Cortical Proteomics: Kozareva et al. 2025 (PMID:41256508 [PREPRINT], Table S1) quantified WTC11 NGN2 cortical i3Neuron TARDBP-KD CELF5 protein depletion (-1.716 log2FC [-69.6%], p=7.27e-4, padj=0.00874), mirrored by depth-filtered TDP-43-KD i3Neuron Soma (-0.979, p=1.53e-7) and Neurite (-0.588, p=1.85e-4; Dargan et al. 2025 GSE299341 PMID:40737092; sorted excitatory nuclei show nuclear sparing/non-depletion [NS] +0.040, p=0.648, n=8 QC-passing paired donors of 10 FANS-seq M1 samples in Ruf et al. 2026 PMID:41803120), whereas in Spillman et al. 2026 C9-FTD frontal cortex DIA proteomics (PMID:42789089, PXD083082, MOESM1 row 6733), CELF5 protein group Q8N6W0;Q8N6W0-2 showed no statistically significant difference (synaptosome log2FC=-0.083, p=0.616, padj=0.834; homogenate log2FC=-0.055, p=0.720, padj=0.870, n=20; undetected in Miedema et al. 2025 FTLD-TDP-C temporal cortex DIA).\n"
                "- Cortical snRNA & Spinal tSTMN2 Coupling: Motor cortex BA4 excitatory neurons show nominal downregulation (-0.768 log2FC, p=0.0133, BH-FDR=0.1357; Pineda et al. 2024 PMID:38521060), while across NYGC ALS-TDP spinal cords (GSE153960), neuronal-mass-residualized CELF5 exhibits the tightest tSTMN2 coupling in the 9-gene cryptic-splicing panel (cervical p=2.02e-8, 1.90% tail; lumbar p=2.54e-11, 0.14% tail), though 70.4% of non-cryptic neuronal genes remain negatively correlated with tSTMN2 in end-stage lumbar cord, motivating Stage-(ii) cervical alpha-MN BaseScope ISH.\n"
                "- Structural RRM2 Consequence: Under the conditional 108-nt Exon5->CE->Exon6 frame (AF-Q8N6W0-F1 + CELF1 homolog PDB 3NMR, PMID:20947024), truncation after Pro201 (230 aa) severs 5 beta4–beta1 backbone H-bonds and 6/17 projected RRM2 UGUU contacts while leaving RRM1 (0 inter-domain contacts, cross-PAE 21.3A) uncoupled, indicating primary loss-of-function rather than competitive RNA dominant-negativity."
            )),
            ("Right Modality & Exposure: CNS PK/PD, Selectivity & Clinical Landscape", (
                "- Patent Coordinates & Synthetic SSO Positioning: CELF5 is an unliganded IDG Tbio RBP with zero clinical compounds and zero published wet-lab splice-switching rescue examples; UCL/King's modified U7 snRNA patent WO2023237638A1 / US20250354145A1 claims the CELF5 cryptic exon (SEQ ID NO: 451) and a 40-nt donor splice-site region (SEQ ID NO: 463, chr19:3278299-3278338(+), without CELF5 wet-lab data) overlapping 20/20 bases of #1 and 18/18 bases of #2 (while UCSD's dual U7smOPT preprint PMID:41573891 [PREPRINT] tested STMN2+UNC13A only; cf. Roche US20220033818A1), positioning reversible intrathecal 20-bp 2'-O-MOE steric SSO #1 (chr19:3278299-3278318(+), >=2-mismatch margin across GENCODE v46 / GGGenome mRNA and pre-mRNA checks, 0 bp from splice boundary, 25bp-SS 2mm=0) as a modality-differentiated preclinical candidate without AAV DRG liabilities.\n"
                "- Multi-LSV Phasing, 18-nt EJC Rule & WT AlphaGenome v1 Polarity: In Brown et al. 2022 MAJIQ local splicing variations (MOESM11), the CE donor junction (3278316-3281199: 107-nt exit row, dPSI=+0.3471, KD E[PSI]=0.367 vs canonical 3278110-3281199 KD E[PSI]=0.546 in the donor LSV vs 0.633 in the acceptor LSV), the adjacent 98-bp micro-intron (3278111-3278208: ~2.8% WT -> 18.2% KD), and an upstream novel 3'-acceptor junction (3225618-3244124: dPSI=+0.1218, KD E[PSI]=0.149, blank ir_start/ir_end, FDR=3.67e-7; cf. Faura 2025 267-aa model) belong to distinct local LSV denominators, requiring endogenous Exon 1–7+ Oxford Nanopore / Iso-Seq (>=1,000–5,000x depth) + UPF1/CHX NMD controls because the conditional 108-bp codon-30 PTC sits 18 nt (<50–55 nt canonical EJC rule, PMID:9671053) upstream of CE–Exon 6. Evaluated strictly as an in silico WT TDP-43-intact 1-nt DNA-substitution proxy (valid as a WT canonical-safety guard; unable to simulate 20-nt steric footprints or TDP-43-KD derepression; canonical Exon-5 5'SS knockout positive control chr19:3278111 disrupts canonical splicing across 3/3 alternate alleles), WT AlphaGenome v1 directional polarity shows 3/3 concordant canonical-enhancing shifts at the cryptic 5'SS bases (tested chr19:3278317, 3278318, 3278321, overlapping +1/+2 [3278317-3278318] of promoted window #1) while resolving Brown 2022 cryptic 3'SS AG acceptors into WT-neutral chr19:3278211-3278212 versus single-allele newly created splice-site artifact chr19:3278229-3278230."
            )),
            ("Right Patient: Stratification & Combination Positioning", (
                "- Why Bulk Frontal & Small-N Cord Are Insufficient: Spillman C9-FTD cortical homogenate and synaptosome DIA (PMID:42789089, MOESM1 row 6733 Q8N6W0;Q8N6W0-2: padj=0.870 & 0.834) showed no statistically significant bulk frontal difference, and small-n spinal ALS-SOD1/FUS (n=9, adj p=0.86) is underpowered to separate pan-motor neuronal attrition from TDP-43 NMD in bulk cord.\n"
                "- Decisive Validation Gate: ChAT + nuclear TDP-43 + duplex BaseScope splice-junction ISH in Stage-(ii) pre-inclusion cervical (C3–C8) lamina IX alpha-MNs across <18–24 mo sALS vs SOD1/FUS-ALS controls paired with endogenous Exon 1–7+ Nanopore phasing in ID-MND sALS patient iPSC-MNs."
            )),
        ],
    },
}
