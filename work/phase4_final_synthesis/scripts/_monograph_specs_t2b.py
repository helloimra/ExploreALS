"""Translational Monograph Standard v3.1 (5Rs + Open Targets + FAIR/W3C PROV) — Part 3: TIER_2B (#7 DN-01, #8 DN-04)."""
from __future__ import annotations

MONOGRAPH_SPECS_T2B: dict[str, dict] = {
    "DN-01": {
        "subtitle": "Unbiased Cryptic-Splice Lead: Clean-1mm Steric SSO (#2) Restoring Autophagy Protease ATG4B & C-Terminal LIR",
        "ident": [
            ("Gene / HGNC", "ATG4B (HGNC:20790)"), ("MANE", "ENST00000404914.8 (+)"), ("UniProt", "Q9Y4P1 (393 aa)"),
            ("3D Crystal", "PDB 2Z0D (ATG4B–LC3B)"), ("IDG TDL / ChEMBL", "Tchem (Inh Only) · CHEMBL1741221"),
            ("Promoted SSO", "#2 chr2:241668970-241668987(+)"),
        ],
        "grades": [
            ("C9-FTD Brain DIA & Cord RNA", "Spillman C9-FTD DIA -0.491 (n=20, PXD083082); NYGC cord ALS-Ox p=1.14e-7"),
            ("Ribo-seq & 3D Crystal", "Ribo-seq -1.550 (PMID:35197628); PDB 2Z0D (PMID:19322194) LIR loss"),
            ("GENCODE v46 Scan Prior", "Promoted #2 spliced 1mm=0, 50bp-SS 1mm=0, 25bp-SS 2mm=2 (DNA AVI=16.16)"),
        ],
        "verdict_box": {
            "pass_gate": "SSO #2 vs #1 (plus 1-nt microwalk & Ca2+/Mg2+-formulated human neuron Ca2+-oscillation/DRG safety screen) across graded 30%/60%/90% TDP-43-CRISPRi human iPSC-MNs restores full-length ATG4B & normalizes LC3ylation (with ATG4A/C/D paralog & N-terminal ~39 kDa immunoblot checks), AND Stage-(ii) partially nuclear-TDP-43-depleted / pre-inclusion surviving cervical (C3–C8) lamina IX alpha-MN ChAT + nuclear TDP-43 + duplex BaseScope ISH across <18–24 mo sALS vs SOD1/FUS-ALS negative-TDP controls (co-assaying ATG4B, CELF5, #9 DN-05 PRUNE2, KCNQ2-DeltaE5, and tSTMN2) + FACS RT-ddPCR confirms CE penetrance.",
            "kill_gate": "Negligible cryptic exon PSI (<2%) in Stage-(ii) partially TDP-43-depleted cervical sALS vs SOD1/FUS-ALS alpha-MNs by BaseScope/LCM RT-ddPCR, acute human neuron Ca2+-oscillation/DRG neurotox, OR zero rescue of LC3 delipidation beyond paralog ATG4A/C/D buffering.",
        },
        "related": ["DN-04", "DN-05", "C001", "C015", "S06"],
        "causal": {
            "callout_kind": "RATIONALE",
            "nodes": [
                ("Nuclear TDP-43 Depletion", "Derepresses 111-bp cryptic exon chr2:241668875-241668985(+) after Exon 10 (PMID:35197628)"),
                ("2 In-Frame TGA PTCs (Codons 33, 35)", "Triggers NMD (-1.55 Ribo-seq) OR C-terminally truncated ATG4B(1–319+32aa)"),
                ("Loss of aa 320–393 LC3B Patch & LIR", "Deletes 27 LC3B contacts + LIR (PDB 2Z0D) -> CNS LC3ylation & autophagy stall"),
                ("Clean-1mm Steric SSO (#2 Lead)", "chr2:241668970-241668987(+) skips cryptic exon & restores LC3 delipidation"),
            ],
            "trap_title": "MODALITY RATIONALE — Why Small-Molecule ATG4B Ligands Act in the Wrong Direction",
            "trap_desc": "Auditing all 995 ChEMBL bioactivity records on human ATG4B (CHEMBL1741221) proved 995/995 are catalytic inhibitors designed for oncology and 0/995 are activators — locking intrathecal steric SSO as the sole mechanism-matched modality.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron CE PSI (PMID:35197628)", "val": 0.243, "stat": "dPSI = +0.243", "p": "FDR=1.16e-11", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq ATG4B (PMID:35197628)", "val": -1.550, "stat": "-1.550 log2FC", "p": "padj=5.78e-6", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Spillman C9-FTD Homogenate DIA (n=20, PXD083082)", "val": -0.491, "stat": "-0.491 log2FC", "p": "p=0.0227", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Cervical ALS-Ox OLS (n=139, GSE153960)", "val": -0.270, "stat": "-0.270 log2CPM", "p": "p=1.14e-7", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "NYGC Cervical neuronal-adj tSTMN2 slope (n=162, GSE153960)", "stat": "beta=-0.564 (6.2% tail)", "p": "p=2.16e-6", "tag": "MEASURED"},
                {"lbl": "PDB 2Z0D (PMID:19322194) aa 320–393 truncation", "stat": "-27 LC3B contacts + LIR", "p": "min 2.7A", "tag": "MODEL_PRIOR"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 ATG4B Intron 10–11 Cryptic Exon, TGA PTCs & Steric SSO Walk (chr2, +)",
            "caption": "Coordinate-only search-window anchor #2 (chr2:241668970-241668987(+), 0 chemically modified synthesis-ready ASO sequences, modeled Tm ~67C [MODEL_PRIOR], DNA AVI=16.16) shifts 11 bp into the exonic 5'SS core, eliminating spliced/50bp-SS 1mm hits while sparing chr2:241668860.",
            "strand": "+", "chrom": "chr2", "win_lo": 241668500, "win_hi": 241670820,
            "zoom_lo": 241668850, "zoom_hi": 241669015,
            "exons": [
                {"lbl": "Exon 10 (Glu319)", "lo": 241668540, "hi": 241668685, "kind": "canon"},
                {"lbl": "Cryptic Exon (111bp, PTCs 33/35)", "lo": 241668875, "hi": 241668985, "kind": "ce"},
                {"lbl": "Exon 11", "lo": 241670726, "hi": 241670782, "kind": "canon"},
            ],
            "snps": [{"lbl": "rs-annot 241668860 (Spared)", "pos": 241668860}],
        },
        "safety": [
            ("Het-pLoF Constraint & KO Context", "LOW", "gnomAD v4.1 pLI = 2.1e-6, LOEUF = 0.851 (low het-pLoF depletion; Atg4b-/- mice show otoconia defects & accelerated SOD1 pathology)"),
            ("Dividing-Line Paralog Buffering", "LOW", "DepMap median Chronos = -0.031 in dividing lines (ATG4A/C/D buffer mitosis, but do not prevent CNS LC3ylation pathology)"),
            ("CNS-Restricted Intrathecal Route", "MITIGATED", "GTEx Cervical = 30.3 / BA9 = 41.8 TPM (IT avoids systemic Kidney_Cortex 38.7 TPM)"),
            ("GENCODE v46 Reference Hybridization", "GATE", "Promoted #2 CAUTION (mRNA 0/0/0, 50bp-SS 1mm=0, 25bp-SS 2mm=2); empirical PS protein-binding & DRG screens required"),
            ("In Vivo Directionality Proof", "LOW", "Torres et al. 2024 (PMID:39305312) shows Atg4b-KO accelerates SOD1 ALS — confirming restoration sign"),
        ],
        "struct_note": "PDB 2Z0D (Satoo et al. 2009, PMID:19322194, DOI:10.1038/emboj.2009.80): catalytic Cys74/Asp278/His280 sits 2.9A from LC3B Gly120, while Exon-10 Glu319 truncation deletes 73 core contacts, 27 LC3B Val89–Val91 contacts (min 2.7A), and the C-terminal LIR (aa 388–391).",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "ATG4B (ENSG00000168397, Q9Y4P1) emerged as the #1 unbiased cryptic-splicing discovery when cryptic splicing (+0.243 dPSI, FDR=1.16e-11) and Ribo-seq loss (-1.550 log2FC, padj=5.78e-6; Brown et al. 2022, PMID:35197628) converged with human ALS/FTD CNS protein LC3ylation pathology and in vivo proof that Atg4b loss accelerates motor neurodegeneration (Torres et al. 2024, PMID:39305312)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Postmortem C9orf72-FTD/ALS frontal cortex exhibits significant homogenate ATG4B protein depletion (-0.491 log2FC, p=0.0227, n=20; Spillman et al. 2026 PXD083082 — indirect C9-FTD cortical evidence, with synaptosomal ATG4B unchanged) despite flat bulk cortical mRNA (p=0.738). In NYGC cervical spinal cord (GSE153960, n=197), ATG4B drops in ALS-TDP (-0.164, p=0.0010; ALS-Ox p=1.14e-7) and tracks neuronal-mass-adjusted tSTMN2 (p=2.16e-6, 6.2% tail) — yet because 69.7% of non-cryptic neuronal genes remain negatively correlated with tSTMN2 in end-stage cord and small-n ALS-SOD1/FUS (n=9) is non-significantly different (adj p=0.270; underpowered to prove equivalence), Stage-(ii) pre-inclusion cervical alpha-MN BaseScope ISH is mandatory."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "Although ATG4B carries IDG Tchem status via oncology protease screens, all 995 ChEMBL bioactivity records (CHEMBL1741221) inhibit catalysis rather than rescuing Exon-10 truncation (PDB 2Z0D, PMID:19322194). Coordinate-only GENCODE v46 scanning promoted 18-bp search-window anchor #2 (chr2:241668970-241668987(+), mRNA 0/0/0, 50bp-SS 1mm=0, modeled Tm ~67C [MODEL_PRIOR], DNA-variant AVI=16.16 [prioritization only, not steric ASO potency certification]) for empirical 1-nt microwalk and Ca2+/Mg2+-formulated Ca2+-oscillation/TLR9/DRG safety screening."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Graded (30%/60%/90%) TDP-43-CRISPRi human iPSC-MN LC3ylation rescue (controlling for ATG4A/C/D paralog buffering) plus ChAT + nuclear TDP-43 + duplex BaseScope splice-junction ISH in Stage-(ii) partially nuclear-TDP-43-depleted / pre-inclusion cervical (C3–C8) lamina IX alpha-MNs across <18–24 mo short-duration sALS vs SOD1/FUS-ALS negative-TDP controls (co-assaying ATG4B, CELF5, #9 DN-05 PRUNE2, KCNQ2-DeltaE5, and tSTMN2 on the same tissue block) gates progression toward single-entity GLP IT tox."),
        ],
    },
    "DN-04": {
        "subtitle": "Unbiased Cryptic-Splice Lead: Clean >=2mm 20-bp SSO (#1) Rescuing Neuron-Specific Splicing Regulator CELF5",
        "ident": [
            ("Gene / HGNC", "CELF5 (HGNC:14060)"), ("MANE", "ENST00000292672.7 (+)"), ("UniProt", "Q8N6W0 (485 aa)"),
            ("Patient iPSC-MN", "Bye 2025 clu_25763_+ padj=0.0090"), ("IDG TDL · Modality", "Tbio · Intrathecal 2'-MOE SSO"),
            ("Promoted SSO", "#1 chr19:3278299-3278318(+)"),
        ],
        "grades": [
            ("Patient iPSC-MN & Cord", "Bye sALS LeafCutter clu_25763_+ padj=0.00904; NYGC lumbar tSTMN2 p=2.54e-11"),
            ("Ribo-seq & Nominal BA4", "Ribo-seq -1.375 (PMID:35197628); BA4_Exc p=0.0133 (nominal, FDR=0.136)"),
            ("Clean >=2mm SSO Prior", "#1 Clean >=2mm reference hybridization (0 hits across all 9 steric/splice tiers)"),
        ],
        "verdict_box": {
            "pass_gate": "SSO #1 vs #2 (plus 10-oligo distal CE 5'SS microwalk & Ca2+/Mg2+-formulated Ca2+-oscillation/DRG safety screen) in Bye sALS patient iPSC-MNs confirms exact cryptic-junction suppression >=70% while full-length Exon 4–7 RT-PCR + Oxford Nanopore amplicon sequencing (>=1,000–5,000 reads) shows none detected above <1–2% LOQ for canonical Exon-5 skipping or 98-bp micro-intron retention (98 mod 3 = 2 frameshift), restores CELF5 protein, and confirms penetrance in Stage-(ii) partially TDP-43-depleted cervical (C3–C8) alpha-MNs (<18–24 mo sALS vs SOD1/FUS-ALS) via ChAT + nuclear TDP-43 + duplex BaseScope ISH.",
            "kill_gate": "Canonical Exon-5 skipping >5% OR 98-bp micro-intron retention (98 mod 3 = 2 frameshift) / latent 5'SS shunting >5% by full-length Exon 4–7 Nanopore RT-PCR, failure to confirm cryptic junction inside clu_25763_+, acute neuron Ca2+/DRG neurotox, OR absent CELF5 cryptic splicing in Stage-(ii) cervical sALS alpha-MNs.",
        },
        "related": ["DN-01", "DN-05", "C001", "C006"],
        "causal": {
            "callout_kind": "CAUTION",
            "nodes": [
                ("TDP-43 Loss in sALS Motor Neurons", "108-bp CE chr19:3278209-3278316(+) & Bye sALS iPSC-MN clu_25763_+ (padj=0.00904)"),
                ("In-Frame PTC at CE Codon 30 (mod3=0)", "108-bp CE carries internal stop -> NMD & -1.375 log2FC translation loss (PMID:35197628)"),
                ("Neuronal RNA-Binding Network Collapse", "#1 sharpest lumbar neuronal-adj tSTMN2 coupling (0.14% tail, p=2.5e-11, GSE153960)"),
                ("Clean >=2mm 20-bp SSO (#1 Lead)", "chr19:3278299-3278318(+) blocks distal CE 5'SS (189 bp downstream of Exon 5)"),
            ],
            "trap_title": "SPLICE-GEOMETRY CAUTION — 98-bp Micro-Intron Retention (mod3=2), Cluster Junction & LOQ Check",
            "trap_desc": "Canonical Exon 5 sits 98 bp upstream of the cryptic exon, and Bye 2025 reports LeafCutter cluster clu_25763_+. Full-length Exon 4–7 Nanopore RT-PCR must confirm junction identity and verify Exon-5 skipping & 98-bp micro-intron retention sit below <1–2% LOQ on a pLI=1.00 neuronal RBP.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron CE junction (PMID:35197628)", "val": 0.347, "stat": "dPSI = +0.347", "p": "FDR=2.83e-22", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq CELF5 (PMID:35197628)", "val": -1.375, "stat": "-1.375 log2FC", "p": "padj=5.65e-7", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Pineda BA4_Exc full-GC OLS (n=32, nominal)", "val": -0.768, "stat": "-0.768 log2FC", "p": "p=0.0133 · FDR=0.136", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Cervical RIN+GC OLS (n=197, GSE153960)", "val": -0.402, "stat": "-0.402 log2CPM", "p": "p=0.0172", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Bye 2025 sALS iPSC-MN LeafCutter clu_25763_+", "stat": "loglr=12.45 (cluster)", "p": "padj=0.00904", "tag": "MEASURED"},
                {"lbl": "NYGC Lumbar neuronal-adj tSTMN2 coupling (n=141, GSE153960)", "stat": "Top 0.14% tail", "p": "p=2.54e-11", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 CELF5 98-bp Micro-Intron, 108-bp Cryptic Exon & Clean 20-bp SSO #1 (chr19, +)",
            "caption": "Exon 5 ends at 3,278,110 and the 108-bp CE starts at 3,278,209 (98-bp micro-intron). Search-window anchor #1 (chr19:3278299-3278318(+), 20bp, 0 chemically modified synthesis-ready ASO sequences) has 0 hits across all 9 GENCODE v46 steric/splice-proximal tiers.",
            "strand": "+", "chrom": "chr19", "win_lo": 3277980, "win_hi": 3281400,
            "zoom_lo": 3278020, "zoom_hi": 3278345,
            "exons": [
                {"lbl": "Exon 5 (80bp)", "lo": 3278031, "hi": 3278110, "kind": "canon"},
                {"lbl": "Cryptic Exon (108bp, PTC c30)", "lo": 3278209, "hi": 3278316, "kind": "ce"},
                {"lbl": "Exon 6 (147bp)", "lo": 3281199, "hi": 3281345, "kind": "canon"},
            ],
            "snps": [],
            "spans": [{"lbl": "98bp Micro-Intron", "lo": 3278111, "hi": 3278208}],
        },
        "safety": [
            ("Restoration on pLI=1.00 Neuronal RBP", "MITIGATED", "gnomAD v4.1 pLI = 1.00, LOEUF = 0.248 (6/54.9 LoF) — mandates <1–2% LOQ Exon-5 skip"),
            ("Unliganded Tbio & Dividing-Line Context", "GATE", "Unliganded Tbio RBP (0 prior clinical drugs; dividing-line DepMap Chronos = -0.130 does not certify mature neuronal RBP safety)"),
            ("6.18x GTEx CNS Enrichment", "LOW", "BA9 = 43.1 & Cerebellum = 60.2 TPM vs max non-CNS Testis = 6.97 (Heart/Liver <0.2 TPM)"),
            ("GENCODE v46 Reference Hybridization", "GATE", "Clean >=2mm on 20-bp #1 (sp=0/0/0, pm=0/0/0/0/0/0); empirical PS protein-binding & DRG screens required"),
            ("Micro-Intron & Exon-5 LOQ Gate", "GATE", "Exon 4–7 Nanopore RT-PCR (>=1,000–5,000 reads) required to verify Exon-5 skip & 98-bp retention sit below <1–2% LOQ"),
        ],
        "struct_note": "CELF5 (Bruno-like 5, Q8N6W0, 485 aa) contains 3 RNA-recognition motifs (RRMs); Exon 5 ends at aa 201 before the linker/RRM3 domain, and CE codon 30 truncates RRM3 completely.",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "CELF5 (ENSG00000161082, Q8N6W0; gnomAD v4.1 pLI = 1.00, LOEUF = 0.248) is an intensely constrained neuron-restricted RNA-binding splicing regulator. Unlike purely engineered TDP-43-KD hits, differential splicing at the CELF5 locus replicates in unperturbed sporadic ALS patient iPSC-MNs at LeafCutter cluster clu_25763_+ (loglr=12.45, padj=0.00904; Bye et al. 2025, DOI:10.1038/s41593-025-02118-7; junction-specific RT-PCR required to confirm exact 108-bp CE usage), alongside TDP-43-KD NMD and translational loss (-1.375 log2FC, padj=5.65e-7; Brown et al. 2022, PMID:35197628)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "In human motor cortex BA4 excitatory neurons, CELF5 shows nominal downregulation after full-GC adjustment (-0.768 log2FC, p=0.0133, nominal BH-FDR=0.1357; Pineda et al. 2024, PMID:38518782), while across NYGC ALS-TDP spinal cords (GSE153960), neuronal-mass-residualized CELF5 exhibits the tightest tSTMN2 coupling in our cryptic-splicing panel (cervical p=2.02e-8, 1.90% tail; lumbar p=2.54e-11, 0.14% tail) — yet because 70.4% of non-cryptic neuronal genes remain negatively correlated with tSTMN2 in end-stage lumbar cord, Stage-(ii) partially TDP-43-depleted cervical alpha-MN BaseScope ISH is required."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "CELF5 is an unliganded IDG Tbio RBP with zero prior clinical compounds. Because canonical Exon 5 lies only 98 bp upstream of the cryptic 3'SS, our coordinate-only scan positioned 20-bp search-window anchor #1 across the distal cryptic 5'SS (chr19:3278299-3278318(+)), achieving 0 hits across all 9 GENCODE v46 reference steric/splice tiers; full-length Exon 4–7 RT-PCR + Oxford Nanopore amplicon sequencing (>=1,000–5,000x depth) across a 10-oligo microwalk must verify canonical Exon-5 skipping and 98-bp micro-intron retention (98 mod 3 = 2 frameshift NMD) remain undetected above <1–2% assay LOQ."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Because untargeted Spillman C9-FTD brain DIA (PXD083082) missed CELF5 peptides and small-n spinal ALS-SOD1/FUS (n=9, adj p=0.86) is underpowered to prove equivalence or separate pan-motor neuronal attrition from TDP-43 NMD in bulk cord, ChAT + nuclear TDP-43 + duplex BaseScope splice-junction ISH in Stage-(ii) pre-inclusion cervical (C3–C8) lamina IX alpha-MNs across <18–24 mo sALS vs SOD1/FUS-ALS controls + full-length Exon 4–7 Nanopore RT-PCR in sALS patient iPSC-MNs is the decisive preclinical validation gate."),
        ],
    },
}
