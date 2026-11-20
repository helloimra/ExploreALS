"""Translational Monograph Standard v3.1 (5Rs + Open Targets + Script/Checksum Provenance) — Part 3: TIER_2B (#7 DN-01, #8 DN-04)."""
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
            ("C9-FTD Brain DIA & sALS Cord", "Spillman C9-FTD DIA -0.491 (p=0.023, FDR=0.148, PMID:42789089); Torres 2024 sALS cord LC3ylation (PMID:39305312)"),
            ("Ribo-seq, ASO 3J & 3D Crystal", "Ribo-seq -1.550 (PMID:35197628); Torres ASO 3J mRNA rescue; PDB 2Z0D + Q9Y4P1 FEIL LIR"),
            ("Head-to-Head vs ASO 3J Scan", "Promoted #2 (-10 bp vs ASO 3J): spliced 1mm 10->0, 50bp-SS 1mm 18->0, pLI>=0.96 flags 5->0 (DNA AVI=16.16)"),
        ],
        "verdict_box": {
            "pass_gate": "SSO #2 vs #1 and Torres 2024 16-nt LNA ASO 3J benchmark (plus 1-nt microwalk & Ca2+/Mg2+-formulated human neuron Ca2+-oscillation/PS-protein-binding/DRG safety screen, PMID:39305312, PMID:31036929, PMID:35166597, PMID:39460376) across graded 30%/60%/90% TDP-43-CRISPRi human iPSC-MNs restores full-length ATG4B protein & normalizes membrane LC3ylation (with ATG4A/C/D paralog, CLN6/DOCK3/SNRNP200 off-target splicing, & N-terminal ~39 kDa immunoblot checks), AND Stage-(ii) partially nuclear-TDP-43-depleted / pre-inclusion surviving cervical (C3–C8) lamina IX alpha-MN ChAT + nuclear TDP-43 + duplex BaseScope ISH across <18–24 mo sALS vs SOD1/FUS-ALS negative-TDP controls (co-assaying ATG4B, CELF5, #9 DN-05 PRUNE2, KCNQ2-DeltaE5, and tSTMN2) + FACS RT-ddPCR confirms single-MN CE penetrance.",
            "kill_gate": "Negligible cryptic exon PSI (<2%) in Stage-(ii) partially TDP-43-depleted cervical sALS vs SOD1/FUS-ALS alpha-MNs by BaseScope/LCM RT-ddPCR, acute human neuron Ca2+-oscillation/DRG neurotox, OR zero rescue of human iPSC-MN ATG4B protein & LC3 delipidation beyond paralog ATG4A/C/D buffering.",
        },
        "related": ["DN-04", "DN-05", "C001", "C023", "S06"],
        "causal": {
            "callout_kind": "RATIONALE",
            "nodes": [
                ("Nuclear TDP-43 Depletion", "Derepresses 111-bp cryptic exon chr2:241668875-241668985(+) after Exon 10 Val319 (PMID:26250685; PMID:29912613; PMID:35197628)"),
                ("2 In-Frame TGA PTCs (Codons 33, 35)", "Triggers NMD (-1.55 Ribo-seq) OR C-terminally truncated ATG4B(1–319+32aa)"),
                ("Loss of aa 320–393 LC3B Patch & LIR", "Deletes 27 LC3B contacts (PDB 2Z0D) + FEIL LIR (aa 388–391, PMID:28287329) -> sALS cord LC3ylation (PMID:39305312)"),
                ("Clean-1mm IT Steric SSO (#2 Lead)", "chr2:241668970-241668987(+) (-10 bp vs Torres ASO 3J: spliced 1mm 10->0, 50bp-SS 1mm 18->0; IT avoids IV Pip8b2 Kim-1)"),
            ],
            "trap_title": "MODALITY & BENCHMARK RATIONALE — Why IT 2'-MOE #2 Beats ChEMBL Ligands & IV Pip8b2-LNA ASO 3J",
            "trap_desc": "All 995 ChEMBL ATG4B records (CHEMBL1741221) are inhibitors (0/995 activators), while Torres 2024's 16-nt LNA ASO 3J (chr2:241668980-241668995(+), PMID:39305312; est. 1-mm LNA Tm ~80C) carries 10 spliced 1-mm (CLN6, DOCK3), 18 50bp-SS 1-mm, & 5 pLI>=0.96 CNS flags (DOCK3, SNRNP200, PSMA5, KHDC4, SNU13) plus systemic IV Pip8b2 peptide proximal-tubule Kim-1 nephrotoxicity — all eliminated by IT 2'-MOE #2.",
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
            "caption": "Coordinate-only search-window anchor #2 (chr2:241668970-241668987(+), 0 chemically modified synthesis-ready ASO sequences, modeled 2'-MOE Tm ~67.2C [MODEL_PRIOR], DNA AVI=16.16) shifts 10 bp upstream of Torres et al. 2024 16-nt LNA ASO 3J (chr2:241668980-241668995(+), PMID:39305312) into the exonic 5'SS core, cutting spliced 1-mm (10->0), 50bp-SS 1-mm (18->0), and pLI>=0.96 CNS flags (5->0) while sparing chr2:241668860.",
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
            ("Het-pLoF Constraint & KO Context", "LOW", "gnomAD v4.1 MANE pLI = 3.35e-4, LOEUF = 0.851 (29/46.5 LoF; Open Targets / legacy gene constraint LOEUF = 0.699; Atg4b-/- mice otoconia defects PMID:20577052 & accelerated SOD1 ALS PMID:39305312)"),
            ("Dividing-Line Paralog Buffering", "LOW", "DepMap median Chronos = -0.031 in dividing lines (ATG4A/C/D buffer mitosis, but do not prevent CNS LC3ylation pathology)"),
            ("Naked IT 2'-MOE vs IV Pip8b2-LNA", "MITIGATED", "GTEx Cervical = 30.3 / BA9 = 41.8 TPM; naked IT 2'-MOE bypasses systemic IV cationic Pip8b2-peptide + LNA proximal-tubule Kim-1 nephrotoxicity (PMID:39305312)"),
            ("Head-to-Head vs ASO 3J Hybridization", "GATE", "Promoted #2 CAUTION (mRNA 1mm=0, 50bp-SS 1mm=0, 25bp-SS 2mm=2, 0 pLI flags vs ASO 3J mRNA 1mm=10 [CLN6/DOCK3], 50bp-SS 0mm=1, 50bp-SS 1mm=18, 5 pLI flags); empirical PS protein-binding/DRG screens required (PMID:31036929; PMID:39460376)"),
            ("In Vivo & ASO 3J Directionality Proof", "LOW", "Torres et al. 2024 (PMID:39305312) proved Atg4b-KO accelerates SOD1 ALS and LNA ASO 3J rescues canonical mRNA in TARDBP-KD HeLa cells"),
        ],
        "struct_note": "PDB 2Z0D (Satoo et al. 2009, PMID:19322194, Thr5–Gln354 H280A): catalytic Cys74/Asp278/His280A sits 2.9A from LC3B Gly120, while Exon-10 Val319 truncation deletes 73 intra-chain residue-pair contacts (<=4.0A) & 27 heavy-atom contacts (<=4.5A, min 2.7A) to LC3B Val89–Val91 inside 2Z0D, plus the downstream disordered C-terminal FEIL LIR (UniProt Q9Y4P1 aa 388–391, PMID:28287329).",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "ATG4B (ENSG00000168397, Q9Y4P1; gnomAD v4.1 MANE LOEUF = 0.851; Open Targets / legacy gene constraint LOEUF = 0.699) emerged as the #1 unbiased cryptic-splicing discovery when cryptic Exon-10a inclusion (+0.243 dPSI, FDR=1.16e-11; first mapped by Ling et al. 2015 PMID:26250685 and quantified in ALS brain by Torres et al. 2018 PMID:29912613) and Ribo-seq loss (-1.550 log2FC, padj=5.78e-6; Brown et al. 2022, PMID:35197628) converged with human sporadic ALS spinal-cord ATG4B depletion and insoluble membrane protein LC3ylation (Fig. 1c, 1e) plus in vivo proof that Atg4b loss accelerates motor neurodegeneration (Torres et al. 2024, PMID:39305312; otoconia baseline phenotype Mariño et al. 2010 PMID:20577052)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Postmortem C9orf72-FTD (1/10 FTD-MND) frontal cortex exhibits nominal homogenate ATG4B protein depletion (-0.491 log2FC, nominal p=0.0227, BH-FDR=0.148, n=20; Spillman et al. 2026 PMID:42789089, PXD083082 — indirect C9-FTD cortical evidence, with synaptosomal ATG4B unchanged) alongside direct sporadic ALS spinal cord ATG4B loss and LC3ylation in Torres et al. 2024 (PMID:39305312), despite flat bulk cortical mRNA (p=0.738). In NYGC cervical spinal cord (GSE153960, n=197), ATG4B drops in ALS-TDP (-0.164, p=0.0010; ALS-Ox p=1.14e-7) and tracks neuronal-mass-adjusted tSTMN2 (p=2.16e-6, 6.2% tail) — yet because 69.7% of non-cryptic neuronal genes remain negatively correlated with tSTMN2 in end-stage cord and small-n ALS-SOD1/FUS (n=9) is non-significantly different (adj p=0.270; underpowered to prove equivalence), single-neuron Stage-(ii) pre-inclusion cervical alpha-MN BaseScope ISH remains decisive."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "Although ATG4B carries IDG Tchem status via oncology protease screens, all 995 ChEMBL bioactivity records (CHEMBL1741221) inhibit catalysis rather than rescuing Exon-10 Val319 truncation (PDB 2Z0D, PMID:19322194; Q9Y4P1 FEIL LIR, PMID:28287329). Crucially, Torres et al. 2024 (PMID:39305312, Fig. 6 & Table 3) proved in human TARDBP-KD HeLa cells that 16-nt LNA steric-blocking ASO 3J across the cryptic 5'SS (chr2:241668980-241668995(+)) suppresses cryptic exon inclusion and restores canonical ATG4B mRNA, whereas systemic IV administration of cationic cell-penetrating peptide Pip8b2 conjugated to the LNA mixmer caused murine kidney Kim-1 tubular toxicity via megalin/cubilin proximal-tubule accumulation. Head-to-head coordinate-only scanning across GENCODE v46 + GGGenome shows 16-nt ASO 3J hits 10 spliced 1-mm genes (including CLN6 and DOCK3), 1 exact 0-mm <=50bp splice site, 18 1-mm <=50bp splice sites, 7 1-nt bulges, and 5 pLI>=0.96 constrained CNS genes (DOCK3, SNRNP200, PSMA5, KHDC4, SNU13; est. 8-LNA 1-mm duplex Tm ~80.1C [MODEL_PRIOR]), whereas our 18-bp intrathecal 2'-MOE anchor #2 (chr2:241668970-241668987(+), shifted 10 bp into the exonic 5'SS core, UG=4, modeled 2'-MOE Tm ~67.2C [MODEL_PRIOR]) reduces spliced 1-mm, <=50bp splice 0/1-mm, 1-nt bulge, and constrained CNS flags to 0/0/0/0 while naked intrathecal CSF dosing bypasses systemic Pip8b2 renal exposure."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Extending Torres et al. 2024's HeLa mRNA rescue, graded (30%/60%/90%) TDP-43-CRISPRi human iPSC-MN microwalk testing (#2 vs #1 and ASO 3J benchmark, plus WT neuron UG=4 cis-eviction & Ca2+-oscillation/DRG checks, PMID:35166597, PMID:39460376) must confirm full-length ATG4B protein recovery and normalization of endogenous LC3ylation after controlling for ATG4A/C/D paralog buffering.\n\nIn parallel, ChAT + nuclear TDP-43 + duplex BaseScope splice-junction ISH in Stage-(ii) partially nuclear-TDP-43-depleted / pre-inclusion cervical (C3–C8) lamina IX alpha-MNs across <18–24 mo short-duration sALS vs SOD1/FUS-ALS negative-TDP controls (co-assaying ATG4B, CELF5, #9 DN-05 PRUNE2, KCNQ2-DeltaE5, and tSTMN2 on the same tissue block) gates progression toward single-entity GLP IT tox."),
        ],
    },
    "DN-04": {
        "subtitle": "Unbiased Cryptic-Splice Lead: Clean >=2mm 20-bp SSO (#1) Rescuing Neuron-Specific Splicing Regulator CELF5",
        "ident": [
            ("Gene / HGNC", "CELF5 (HGNC:14058)"), ("MANE", "ENST00000292672.7 (+)"), ("UniProt / 3D", "Q8N6W0 · AF-Q8N6W0-F1 / PDB 3NMR"),
            ("Patient iPSC-MN", "Bye 2025 clu_25763_+ padj=0.0090 (PMID:41286450)"), ("IDG TDL · Modality", "Tbio · Intrathecal 2'-MOE SSO"),
            ("Promoted SSO", "#1 chr19:3278299-3278318(+)"),
        ],
        "grades": [
            ("Patient iPSC-MN & Cord", "Bye sALS N=77 clu_25763_+ padj=0.00904 (PMID:41286450; raw BAMs EGA); NYGC lumbar tSTMN2 p=2.54e-11"),
            ("Ribo-seq, 3D RRM2 & BA4", "Ribo-seq -1.375 (38.6% residual, PMID:35197628); AF-Q8N6W0/3NMR beta4 loss; BA4_Exc p=0.0133"),
            ("Clean >=2mm & 18-nt EJC", "#1 Clean >=2mm (0/9 tiers); PTC c30 sits 18 nt (<50 nt) from CE-Ex6 -> multi-exon ONT required"),
        ],
        "verdict_box": {
            "pass_gate": "SSO #1 vs #2 (plus 10-oligo distal CE 5'SS microwalk & Ca2+/Mg2+-formulated Ca2+-oscillation/DRG safety screen) in Bye sALS patient iPSC-MNs (PMID:41286450) confirms exact 108-bp cryptic-junction suppression >=70% inside endogenous multi-exon transcripts (never a 3-exon Exon5–CE–Exon6 minigene, which places PTC codon 30 only 18 nt [<50–55 nt] upstream of CE–Exon 6 and artificially evades EJC-NMD!), while single-molecule Exon 1–7+ Oxford Nanopore / Iso-Seq long-read sequencing (>=1,000–5,000 reads, resolving Intron-1 dPSI=+0.122 vs CE dPSI=+0.347 phasing bounds) shows canonical Exon-5 skipping <1–2% LOQ and 98-bp micro-intron retention (98 mod 3 = 2 frameshift: ~2.8% WT -> 18.2% TDP-43 KD) restored to <=WT baseline, restores CELF5 protein, and confirms penetrance in Stage-(ii) partially TDP-43-depleted cervical (C3–C8) alpha-MNs (<18–24 mo sALS vs SOD1/FUS-ALS) via ChAT + nuclear TDP-43 + duplex BaseScope ISH.",
            "kill_gate": "Canonical Exon-5 skipping >5% OR post-SSO 98-bp micro-intron retention (98 mod 3 = 2 frameshift) exceeding WT vehicle baseline by >5% / latent 5'SS shunting >5% or unrescued cis-independent Intron-1 retention blocking >50% functional protein recovery on Exon 1–7+ Nanopore sequencing, failure to confirm 108-bp CE inside clu_25763_+, acute neuron Ca2+/DRG neurotox, OR absent CELF5 cryptic splicing in Stage-(ii) cervical sALS alpha-MNs.",
        },
        "related": ["DN-01", "DN-05", "C001", "C006"],
        "causal": {
            "callout_kind": "CAUTION",
            "nodes": [
                ("TDP-43 Loss in sALS Motor Neurons", "108-bp CE chr19:3278209-3278316(+) & Bye sALS iPSC-MN clu_25763_+ (N=77, padj=0.00904, PMID:41286450)"),
                ("PTC c30 (18-nt Gap) & RRM2 beta4 Loss", "Endogenous Ex6–13 EJCs drive NMD (-1.375 Ribo-seq); Pro201 cut severs 5 beta4–beta1 H-bonds & 6/17 3NMR RNA contacts"),
                ("Neuronal RNA-Binding Network Collapse", "#1 sharpest lumbar neuronal-adj tSTMN2 coupling (0.14% tail, p=2.5e-11, GSE153960)"),
                ("Clean >=2mm 20-bp SSO (#1 Lead)", "chr19:3278299-3278318(+) blocks distal CE 5'SS (87.8–100% single-locus canonical ceiling)"),
            ],
            "trap_title": "PHASING & 18-NT EJC MINIGENE TRAP — 98-bp Micro-Intron, Intron-1 Bounds & False Minigene NMD Escape",
            "trap_desc": "CE codon-30 PTC sits only 18 nt (<50–55 nt) upstream of CE–Exon 6, so 3-exon Exon5–CE–Exon6 minigenes artificially evade EJC-NMD (requiring endogenous Exon 4–7+ / Exon 1–7+ ONT assays); Frechet–Hoeffding phasing of CE (+0.347) + Intron-1 (+0.122) bounds baseline canonical mRNA at 53.1–65.3% (vs 38.6% empirical Ribo-seq) and single-SSO ceiling at 87.8–100%.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron CE junction (PMID:35197628)", "val": 0.347, "stat": "dPSI = +0.347", "p": "FDR=2.83e-22", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq CELF5 (38.6% residual, PMID:35197628)", "val": -1.375, "stat": "-1.375 log2FC", "p": "padj=5.65e-7", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Pineda BA4_Exc full-GC OLS (n=32, nominal)", "val": -0.768, "stat": "-0.768 log2FC", "p": "p=0.0133 · FDR=0.136", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Cervical RIN+GC OLS (n=197, GSE153960)", "val": -0.402, "stat": "-0.402 log2CPM", "p": "p=0.0172", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Bye 2025 sALS iPSC-MN clu_25763_+ (N=77, PMID:41286450)", "stat": "loglr=12.45 (65v12)", "p": "padj=0.00904", "tag": "MEASURED"},
                {"lbl": "AF-Q8N6W0 / PDB 3NMR Pro201 RRM2 beta4 excision (PMID:20947024)", "stat": "-5 H-bonds · -6/17 UGUU", "p": "0 RRM1–2 contacts", "tag": "MEASURED"},
                {"lbl": "Frechet–Hoeffding CE (+0.347) + Intron-1 (+0.122) mRNA bounds", "stat": "53.1–65.3% -> 87.8–100%", "p": "18-nt EJC gap", "tag": "MODEL_PRIOR"},
                {"lbl": "NYGC Lumbar neuronal-adj tSTMN2 coupling (n=141, GSE153960)", "stat": "Top 0.14% tail", "p": "p=2.54e-11", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 CELF5 98-bp Micro-Intron, 108-bp CE (18-nt EJC Gap) & Clean 20-bp SSO #1 (chr19, +)",
            "caption": "Exon 5 (Pro201 inside RRM2) ends at 3,278,110 and the 108-bp CE starts at 3,278,209 (98-bp micro-intron: ~2.8% WT -> 18.2% TDP-43 KD; CE PTC c30 sits 18 nt upstream of CE–Exon 6, requiring endogenous Exon 4–7+ NMD assays). Search-window anchor #1 (chr19:3278299-3278318(+), 20bp, 0 chemically modified synthesis-ready ASO sequences) has 0 hits across all 9 GENCODE v46 steric/splice-proximal tiers.",
            "strand": "+", "chrom": "chr19", "win_lo": 3277980, "win_hi": 3281400,
            "zoom_lo": 3278020, "zoom_hi": 3278345,
            "iv_notes": {
                "1": "Exon 1-7+ ONT req. (18-nt PTC gap evades 3-exon NMD)",
            },
            "exons": [
                {"lbl": "Exon 5 (80bp, Pro201/RRM2)", "lo": 3278031, "hi": 3278110, "kind": "canon"},
                {"lbl": "Cryptic Exon (108bp, PTC c30)", "lo": 3278209, "hi": 3278316, "kind": "ce"},
                {"lbl": "Exon 6 (147bp)", "lo": 3281199, "hi": 3281345, "kind": "canon"},
            ],
            "snps": [{"lbl": "PTC c30 (18nt to 5'SS)", "pos": 3278298}],
            "spans": [{"lbl": "98bp Micro-Intron (~2.8% WT)", "lo": 3278111, "hi": 3278208}],
        },
        "safety": [
            ("Restoration on pLI=1.00 Neuronal RBP", "MITIGATED", "gnomAD v4.1 MANE pLI = 1.00, LOEUF = 0.248 (6/47.7 LoF; Open Targets / legacy gene constraint LOEUF = 0.216, 6/54.9) — mandates <1–2% Exon-5 skip"),
            ("Unliganded Tbio & Dividing-Line Context", "GATE", "Unliganded Tbio RBP (0 prior clinical drugs; dividing-line DepMap Chronos = -0.130 does not certify mature neuronal RBP safety)"),
            ("6.18x GTEx CNS Enrichment", "LOW", "BA9 = 43.1 & Cerebellum = 60.2 TPM vs max non-CNS Testis = 6.97 (Heart/Liver <0.2 TPM)"),
            ("GENCODE v46 Reference Hybridization", "GATE", "Clean >=2mm on 20-bp #1 (sp=0/0/0, pm=0/0/0/0/0/0); empirical PS protein-binding & DRG screens required (PMID:31036929; PMID:39460376)"),
            ("Long-Read Phasing & Endogenous EJC Gate", "GATE", "Exon 1–7+ Nanopore (>=1,000–5,000x; never 3-exon minigene due to 18-nt PTC gap) verifies <1–2% Exon-5 skip, <=WT 98-bp retention (~2.8%), & Intron-1 phasing"),
        ],
        "struct_note": "AF-Q8N6W0-F1-v6 & crystal homolog PDB 3NMR (Teplova et al. 2010, PMID:20947024, CELF1 RRM1–RRM2:UGUU): RRM1 (aa 46–121, pLDDT=91.8) and RRM2 (aa 134–214, pLDDT=90.9) make 0 inter-domain contacts <=4.5A (cross-PAE 21.3A); Exon-5 Pro201 truncation excises RRM2 beta-4 (aa 202–214) + RRM3, severing 5 anti-parallel beta4–beta1 backbone H-bonds (<=3.5A), 44 core packing pairs, and 6/17 UGUU-contacting RRM2 residues in 3NMR — establishing primary LoF + unfolded RRM2(134–201)+29aa chaperone burden rather than competitive RNA dominant-negativity.",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "CELF5 (ENSG00000161082, HGNC:14058, Q8N6W0; gnomAD v4.1 MANE pLI = 1.00, LOEUF = 0.248 [6/47.7 LoF; Open Targets / legacy gene constraint LOEUF = 0.216, 6/54.9]) is an intensely constrained neuron-restricted RNA-binding splicing regulator. Unlike purely engineered TDP-43-KD hits, differential splicing at the CELF5 locus replicates in unperturbed sporadic ALS patient iPSC-MNs at LeafCutter cluster clu_25763_+ (loglr=12.45, padj=0.00904 across N=77 [65 sALS vs 12 Ctrl at Day 49, despite intact bulk nuclear TDP-43 IF P=0.990]; Bye et al. 2025, PMID:41286450, DOI:10.1038/s41593-025-02118-7 — MOESM publishes cluster-level stats while raw patient BAMs reside under controlled access on EGA, requiring junction-specific RT-PCR/Nanopore to confirm exact 108-bp CE usage), alongside TDP-43-KD cryptic splicing and translational loss (-1.375 log2FC = 38.6% residual translation, padj=5.65e-7; Brown et al. 2022 PMID:35197628; Humphrey et al. 2023 PMID:36482247)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "In human motor cortex BA4 excitatory neurons, CELF5 shows nominal downregulation after full-GC adjustment (-0.768 log2FC, p=0.0133, nominal BH-FDR=0.1357; Pineda et al. 2024, PMID:38521060), while across NYGC ALS-TDP spinal cords (GSE153960), neuronal-mass-residualized CELF5 exhibits the tightest tSTMN2 coupling in the 9-gene cryptic-splicing panel (cervical p=2.02e-8, 1.90% tail; lumbar p=2.54e-11, 0.14% tail) — yet because 70.4% of non-cryptic neuronal genes remain negatively correlated with tSTMN2 in end-stage lumbar cord, Stage-(ii) partially TDP-43-depleted cervical alpha-MN BaseScope ISH is required. Structurally (AF-Q8N6W0-F1 + PDB 3NMR, PMID:20947024), truncation after Pro201 severs 5 beta4–beta1 backbone H-bonds and 6/17 RRM2 UGUU contacts while leaving RRM1 (0 inter-domain contacts, cross-PAE 21.3A) uncoupled, pointing to primary loss-of-function (plus candidate 29-aa cryptic neo-peptide biomarker if any molecules evade NMD) rather than high-affinity competitive RNA dominant-negativity."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "CELF5 is an unliganded IDG Tbio RBP with zero prior clinical compounds. In Brown et al. 2022 short-read splicing, the 98-bp micro-intron (3278111-3278208: ~2.8% WT -> 18.2% KD) physically adjoins the 108-bp CE (dPSI=+0.347), while upstream Intron-1 retention (dPSI=+0.122, FDR=1.63e-5) is unphased: exact Frechet–Hoeffding bounds place total aberrant transcripts at 34.7% (cis-coupled) to 46.9% (mutually exclusive), corresponding to 53.1%–65.3% baseline canonical mRNA (vs 38.6% empirical Ribo-seq translation) and an 87.8%–100.0% canonical rescue ceiling for a single-locus CE steric SSO. Crucially, because the first in-frame PTC (codon 30, nt 90 of 108) sits only 18 nt (<50–55 nt canonical EJC rule) upstream of the CE–Exon 6 junction, endogenous NMD depends on the 7 downstream constitutive junctions (Exons 6–13) — meaning a 3-exon Exon5–CE–Exon6 splicing minigene artificially evades NMD! Promoted 20-bp anchor #1 (chr19:3278299-3278318(+), 0 hits across all 9 GENCODE v46 steric/splice tiers) must therefore be validated on endogenous multi-exon transcripts via single-molecule Exon 1–7+ Oxford Nanopore / Iso-Seq sequencing (>=1,000–5,000x depth) + UPF1/CHX NMD rescue to verify <1–2% Exon-5 skip, <=WT 98-bp retention (~2.8%), and Intron-1 phasing."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Untargeted Spillman C9-FTD brain DIA (PMID:42789089, PXD083082) missed CELF5 peptides, and small-n spinal ALS-SOD1/FUS (n=9, adj p=0.86) is underpowered to prove equivalence or separate pan-motor neuronal attrition from TDP-43 NMD in bulk cord.\n\nAccordingly, ChAT + nuclear TDP-43 + duplex BaseScope splice-junction ISH in Stage-(ii) pre-inclusion cervical (C3–C8) lamina IX alpha-MNs across <18–24 mo sALS vs SOD1/FUS-ALS controls + endogenous Exon 1–7+ Nanopore phasing in sALS patient iPSC-MNs serves as the decisive preclinical validation gate."),
        ],
    },
}
