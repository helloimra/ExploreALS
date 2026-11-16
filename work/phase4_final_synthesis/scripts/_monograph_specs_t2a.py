"""Translational Monograph Standard v3.1 (5Rs + Open Targets + FAIR/W3C PROV) — Part 2: TIER_2A (#4 C001, #5 C002, #6 C007)."""
from __future__ import annotations

MONOGRAPH_SPECS_T2A: dict[str, dict] = {
    "C001": {
        "subtitle": "Clean >=2mm Intrathecal Steric SSO (#2) Blocking UNC13A Intron 20–21 Cryptic Exon Inclusion",
        "ident": [
            ("Gene / HGNC", "UNC13A (HGNC:23150)"), ("MANE", "ENST00000519716 (-)"), ("UniProt", "Q9UPW8 (1,703 aa)"),
            ("ALS GWAS", "rs12608932 · rs12973192"), ("Promoted SSO", "#2 chr19:17642537-17642554(-)"),
            ("IDG TDL · Modality", "Tchem (Non-Sel C1) / Pre-mRNA SSO · IT 2'-MOE"),
        ],
        "grades": [
            ("Human GWAS & Postmortem", "6 ALS GWAS credible sets (p=4.04e-25); Spillman C9-FTD 6/10 (PXD083082)"),
            ("Splicing & Synaptic Rescue", "Brown CE dPSI=+0.463; Keuss 2026 Nature human MN eEPSC/MEA rescue (10.1038/s41586-026-11256-2)"),
            ("GENCODE v46 Scan Prior", "Promoted #2 Clean >=2mm (mRNA 0/0/0, 50bp-SS 1mm=0, DNA AVI=23.1)"),
        ],
        "verdict_box": {
            "pass_gate": "Stage 1 single-entity UNC13A #2 establishes NHP cervical (C3–C5 phrenic) & BA4 Betz parenchymal splice-rescue EC80 curves + 3-layer Phase 1b PK/TE/PD (strand-specific CSF PK, L1CAM+/ATP1A3+ NDEV pre-amplified dPCR/Nanopore + CSF synaptic secretome NPTX2/VGF/SNAP25 TE, and >=16–24 wk post-loading CSF pNfH/NfL PD accounting for ANQUR dose dissociation), and Stage 2 genotype-stratified randomization (testing 2-plex vs 3-plex across rs12973192/rs12608932 genotypes as unvalidated 24–48 mg scenarios beyond single-agent DEVOTE PMID:41634391) rescues all junctions >=65% without saturating <1–2% endosomal escape or triggering Ca2+/Mg2+-chelation, TLR9, or DRG tox.",
            "kill_gate": "Competitive scavenger-receptor uptake or productive late-endosomal escape loss >30% vs 1-plex, inadequate cervical/BA4 parenchymal splice rescue, acute human neuron Ca2+-oscillation/DRG neurotox, OR failure to restore Munc13-1 synaptic vesicle priming.",
        },
        "related": ["C006", "C002", "DN-01", "DN-04"],
        "causal": {
            "callout_kind": "CAUTION",
            "nodes": [
                ("TDP-43 Loss + Risk Alleles C/G", "CE-internal rs12973192-G & rs12608932-C potentiate susceptibility (severe TDP-43 loss still mis-splices A/A, PMID:35197628)"),
                ("Intron 20–21 Cryptic Exon (128/178 bp)", "chr19:17642414-17642541(-) introduces frameshift PTC & NMD decay"),
                ("Presynaptic Vesicle Priming Failure", "Munc13-1 loss collapses glutamatergic neuromuscular synaptic transmission"),
                ("Clean >=2mm Steric SSO (#2 Lead)", "chr19:17642537-17642554(-) masks cryptic 3'SS; genotype-stratified multiplex"),
            ],
            "trap_title": "ASSAY & GENOTYPE CAUTION — Read-Length Bias, Bulk Masking & Non-Binary A/A Susceptibility",
            "trap_desc": "In NYGC GSE153960, 100bp NovaSeq misses UNC13A CE 3.89x vs 125bp HiSeq (p=3.38e-4), and lumbar depletion emerges after GC+cell adjustment (p=7.38e-4). Because severe TDP-43 depletion induces UNC13A CE even in A/A (~43% NFE / ~35–38% ALS), genotype informs stratification rather than binary exclusion.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron CE junction (PMID:35197628)", "val": 0.463, "stat": "dPSI = +0.463", "p": "FDR=2.31e-19", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq UNC13A (PMID:35197628)", "val": -0.781, "stat": "-0.781 log2FC", "p": "padj=0.0296", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Lumbar Cord GC+cell OLS (n=92, GSE153960)", "val": -0.355, "ci": [-0.554, -0.157], "stat": "-0.355 log2FC", "p": "p=7.38e-4", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Spillman C9-FTD Synaptosome DIA (n=20, PXD083082)", "val": -0.250, "stat": "-0.250 log2FC", "p": "p=0.0502", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Spillman C9-FTD CE junction detection (n=20, PXD083082)", "stat": "6/10 vs 0/10 Ctrl", "p": "p=0.0108", "tag": "MEASURED"},
                {"lbl": "NYGC 125bp HiSeq vs 100bp NovaSeq CE bias (n=201, GSE153960)", "stat": "OR = 3.89x (30.9% vs 10.3%)", "p": "p=3.38e-4", "tag": "MEASURED"},
                {"lbl": "AlphaGenome rs12973192 DLPFC DNA-variant splice quantile", "stat": "q = 0.989 (AVI=8.90)", "p": "GWAS sQTL", "tag": "MODEL_PRIOR"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 UNC13A Intron 20–21 Cryptic Exon, GWAS Risk SNPs & SSO Walk (chr19, -)",
            "caption": "Coordinate-only search-window anchor #2 (chr19:17642537-17642554(-), 0 chemically modified synthesis-ready ASO sequences) achieves Clean >=2mm reference hybridization across 254,070 GENCODE v46 transcripts while starting 107 bp upstream of polymorphic rs12973192 (chr19:17642430:C>G).",
            "strand": "-", "chrom": "chr19", "win_lo": 17641350, "win_hi": 17643000,
            "zoom_lo": 17642400, "zoom_hi": 17642580,
            "exons": [
                {"lbl": "Exon 21", "lo": 17641393, "hi": 17641556, "kind": "canon"},
                {"lbl": "Cryptic Exon (128bp PTC)", "lo": 17642414, "hi": 17642541, "kind": "ce"},
                {"lbl": "Exon 20", "lo": 17642845, "hi": 17642960, "kind": "canon"},
            ],
            "snps": [{"lbl": "rs12608932 (GWAS)", "pos": 17641880}, {"lbl": "rs12973192 (CE)", "pos": 17642430}],
        },
        "safety": [
            ("Restoration on Constrained Gene", "MITIGATED", "gnomAD v4 pLI = 1.000, LOEUF = 0.344 (biallelic LoF causes fatal synaptic encephalopathy PMID:27545677; SSO restores WT)"),
            ("Dividing-Line Context (DepMap)", "GATE", "Mean Chronos = -0.043 in dividing cancer lines (which lack synapses; canonical splicing preservation mandatory)"),
            ("CNS Specificity & IT Delivery", "LOW", "Strictly neuronal presynaptic expression; IT 2'-MOE restricts exposure to CNS"),
            ("GENCODE v46 Reference Hybridization", "GATE", "Clean >=2mm on #2 (mRNA 0/0/0, 50bp-SS 1mm=0); empirical PS protein-binding, TLR9 & DRG tox still required"),
            ("Polymorphism Masking (gnomAD v4)", "LOW", "#2 starts 107 bp upstream of rs12973192 (106 intervening bases), ensuring genotype-agnostic binding"),
        ],
        "struct_note": "Munc13-1 (Q9UPW8) MUN domain catalyzes SNARE syntaxin-1 opening; pairs with C006 (excitability) and C002 (axonal outgrowth) via genotype-stratified multiplex testing across rs12973192/rs12608932 genotypes.",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "UNC13A (ENSG00000130477, gnomAD v4 LOEUF = 0.344) is the strongest human-genetics-anchored TDP-43 cryptic-splicing target in ALS: GWAS risk alleles rs12608932-C (p=4.04e-25) and cryptic-exon-internal rs12973192-G directly weaken TDP-43 repression and potentiate Intron 20–21 cryptic exon inclusion and NMD loss of presynaptic Munc13-1, though severe nuclear TDP-43 depletion still triggers cryptic splicing in A/A homozygotes (~43% in gnomAD v4 non-Finnish Europeans vs ~35–38% in European ALS cohorts; Brown et al. 2022 PMID:35197628; Ma et al. 2022 PMID:35197626).\n\nKeuss et al. 2026 (Nature, DOI:10.1038/s41586-026-11256-2) directly closed the human functional-rescue proof: in HaloTDP human cortical iNeurons and human iPSC spinal motor neurons, isolated CRISPR deletion of the Intron-20 cryptic exon (~75% protein recovery; >30% physiological threshold) or 18/21-nt 2'-O-MOE steric ASOs restored presynaptic UNC13A, mEPSC frequency (~80% recovery), evoked AMPA eEPSCs, and MEA network synchrony across both reference and risk alleles — while STMN2 polyadenylation, KCNQ2 Exon-5 skipping, Intron-31 retention, and ~10% postsynaptic mEPSC amplitude remained unrescued, confirming orthogonal compartment complementarity with C006 and C002."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Re-computing NYGC postmortem RNA-seq (GSE153960) proved 100bp NovaSeq under-detects UNC13A cryptic junctions 3.89-fold vs 125bp HiSeq (p=3.38e-4), and lumbar cord mRNA depletion (-0.355 log2FC, 95% CI -0.554 to -0.157, p=7.38e-4) emerges after GC and cell-composition adjustment, alongside indirect C9-FTD cortical synaptosome Munc13-1 loss (-0.250 log2FC, p=0.0502, n=20; PXD083082). Because unfractionated lumbar CSF EVs sit in the late-cycle RT-qPCR (Cq>35) / Poisson-limited (<3–10 copies/mL) ddPCR regime (PMID:38158550) and CSF pNfH is a target-agnostic injury PD marker that showed inverse dose dissociation in sponsor-reported interim QRL-201 ANQUR data (~46% drop at low dose vs ~5% at 10 mg), Phase 1b pairs strand-specific CSF PK -> NHP splice bridging with L1CAM+/ATP1A3+ NDEV pre-amplified dPCR/Nanopore + CSF synaptic secretome (NPTX2/VGF/SNAP25) TE and >=16–24 wk post-loading pNfH/NfL PD."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "Specific rescue requires intrathecal 2'-MOE steric splicing modulation (note published Keuss et al. 2026 2'-MOE ASOs in humanized hUNC13A mice and clinical candidates LY4256984/TRCN-1023 across NCT07100119, NCT07571174, NCT07571200, NCT07674667 validate target biology rather than ExploreALS's un-synthesized windows, while Keuss 2026's >30% Munc13-1 synaptic rescue threshold informs rostral C3–C5/BA4 parenchymal target-engagement margins). GENCODE v46 scanning promoted Clean >=2mm 3'SS search-window anchor #2 (chr19:17642537-17642554(-), modeled Tm ~64C [MODEL_PRIOR], DNA-variant AVI=23.1 [prioritization only, not steric ASO potency proof], 107 bp upstream of rs12973192) for empirical 1-nt microwalk and Ca2+/Mg2+-formulated Ca2+-oscillation/TLR9/DRG safety gating."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Evaluated in Stage 2 under 21 CFR 300.50 via prospective genotype-stratified randomization testing 2-plex (KCNQ2 C006 + STMN2 C002) vs 3-plex (+UNC13A C001) across both rs12973192-G/rs12608932-C risk carriers and A/A homozygotes (treating 24–48 mg mixed-PO/PS regimens strictly as unvalidated development scenarios — single-agent DEVOTE 50 mg nusinersen PMID:41634391 does not establish multiplex safety across distinct sequences), gated on Stage 1 single-entity GLP NHP IT tox, C3–C5/BA4 splice rescue, and <1–2% endosomal-escape competition curves."),
        ],
    },
    "C002": {
        "subtitle": "Clean >=2mm Intrathecal Steric SSO (#2) Blocking STMN2 Exon-2a Cryptic 3'SS & Premature PAS",
        "ident": [
            ("Gene / HGNC", "STMN2 (HGNC:10577)"), ("MANE", "ENST00000220876 (+)"), ("UniProt", "Q93045 (SCG10, 179 aa)"),
            ("Clinical Benchmark", "QRL-201 NCT05633459 · BIIB147 NCT07855211"), ("Promoted SSO", "#2 chr8:79616829-79616846(+)"),
            ("IDG TDL · Modality", "Tbio (Ph1/2 ASO) · Intrathecal 2'-MOE SSO"),
        ],
        "grades": [
            ("Human Pathology & Ph1/2", "NYGC lumbar -0.771; interim QRL-201 ANQUR tissue STMN2 TE & low-dose subgroup pNfH PD"),
            ("Ribo-seq & Parallel Axons", "Ribo-seq -2.924 (PMID:35197628); parallel to Sarm1 KO in mice (Krus 2022 PMID:35767949)"),
            ("GENCODE v46 Scan Prior", "Promoted #2 Clean >=2mm (mRNA 0/0/0, 50bp-SS 1mm=0, DNA AVI=20.86)"),
        ],
        "verdict_box": {
            "pass_gate": "Bliss/Loewe additivity or synergy on axon outgrowth & NAD+ preservation when combining STMN2 #2 SSO with sub-IC80 allosteric SARM1 T-lock (S06; evaluating parallel protection vs illustrative ~2–7x MWC scenario [MODEL_PRIOR]) in axotomized TDP-43-KD human iPSC-MNs + Stage 1 NHP cervical (C3–C5) & BA4 splice EC80 bridging + 3-layer PK/TE/PD (strand-specific CSF PK, L1CAM+/ATP1A3+ NDEV tSTMN2 dPCR/Nanopore + ultrasensitive soluble SCG10 TE, and >=16–24 wk post-loading CSF pNfH/NfL PD) + unvalidated 24–48 mg 2-plex/3-plex Ca2+/DRG/uptake safety.",
            "kill_gate": "Redundant functional ceiling with allosteric SARM1 T-lock alone OR >30% competitive uptake / endosomal-escape loss, human neuron Ca2+-oscillation/DRG/autonomic neurotox, or cervical/BA4 sub-efficacy in 2-plex/3-plex co-delivery.",
        },
        "related": ["S06", "C006", "C001"],
        "causal": {
            "callout_kind": "RATIONALE",
            "nodes": [
                ("Nuclear TDP-43 Depletion", "Derepresses Intron-1 cryptic 3'SS (chr8:79616822) & premature PAS (PMID:30643298; PMID:30643292)"),
                ("Truncated Exon-2a mRNA (227 bp)", "Terminates transcription after Exon 1; ablates full-length SCG10 protein (Q93045)"),
                ("Parallel NMJ & Microtubule Collapse", "Drives distal NMJ denervation parallel to SARM1 (PMID:35767949; BA4 NMNAT2 co-variation r=+0.928)"),
                ("Clean >=2mm SSO (#2) + SARM1 T-Lock", "chr8:79616829-79616846(+) restores SCG10 alongside orthogonal SARM1 T-lock protection"),
            ],
            "trap_title": "COMBINATORIAL & PD CAUTION — Parallel Stmn2/Sarm1 Genetics & ANQUR pNfH Dose Dissociation",
            "trap_desc": "Krus et al. 2022 (PMID:35767949) showed Stmn2 loss acts in parallel to Sarm1 in mice (making C002 + S06 orthogonal protection; ~2–7x MWC sparing is an illustrative scenario). In interim QRL-201 ANQUR data, CSF pNfH fell ~46% at low dose vs ~5% at 10 mg while ALSFRS-R favored 10 mg, requiring direct per-target TE.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq STMN2 (PMID:35197628)", "val": -2.924, "stat": "-2.924 log2FC", "p": "FDR=1.6e-173", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Lumbar Cord GC+cell OLS (n=92, GSE153960)", "val": -0.771, "ci": [-1.110, -0.433], "stat": "-0.771 log2FC", "p": "p=2.47e-5", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Spillman C9-FTD Homogenate DIA (n=20, PXD083082)", "val": -0.483, "stat": "-0.483 (-28%)", "p": "p=0.014, FDR=0.11", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "compensatory_or_survivor", "lbl": "Pineda Surviving BA4 L5_Exc snRNA (n=32, PMID:38518782)", "val": 0.497, "stat": "+0.497 log2FC", "p": "p=2.23e-4", "tag": "MEASURED"},
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron Exon-2a cryptic ALE (PMID:35197628)", "val": 0.482, "stat": "dPSI = +0.482", "p": "FDR=3.02e-18", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Pineda BA4_Exc STMN2–NMNAT2 co-variation (n=32, PMID:38518782)", "stat": "Pearson r = +0.928", "p": "p=1.95e-14", "tag": "MEASURED"},
                {"lbl": "Bryce-Smith NYGC postmortem tSTMN2 specificity (PMID:40038262)", "stat": "383/926 vs 0/750", "p": "100% TDP+", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 STMN2 Intron-1 Cryptic Exon-2a / Premature PAS & SSO Walk (chr8, +)",
            "caption": "Coordinate-only search-window anchor #2 (chr8:79616829-79616846(+), 0 chemically modified synthesis-ready ASO sequences, modeled Tm ~64C [MODEL_PRIOR], DNA AVI=20.86) masks +8..+25 bp inside Exon-2a with Clean >=2mm GENCODE v46 reference hybridization.",
            "strand": "+", "chrom": "chr8", "win_lo": 79611000, "win_hi": 79637000,
            "zoom_lo": 79616800, "zoom_hi": 79617060,
            "exons": [
                {"lbl": "Exon 1", "lo": 79611117, "hi": 79611214, "kind": "canon"},
                {"lbl": "Cryptic Exon 2a + PAS (227bp)", "lo": 79616822, "hi": 79617048, "kind": "ce"},
                {"lbl": "Exon 2", "lo": 79636802, "hi": 79636897, "kind": "canon"},
            ],
            "snps": [{"lbl": "Cryptic 3'SS AVI=23.6", "pos": 79616821}],
        },
        "safety": [
            ("Restoration on Constrained Gene", "MITIGATED", "gnomAD v4 pLI = 0.9999, LOEUF = 0.261 (2/24.1 LoF) — restores endogenous SCG10"),
            ("Peripheral / DRG Expression Check", "GATE", "Dividing-line Chronos = -0.047, but STMN2 is expressed in peripheral sympathetic/autonomic & DRG neurons -> IT DRG/autonomic monitoring"),
            ("Sponsor Interim Ph1/2 Precedent", "GATE", "Interim QRL-201 ANQUR (NCT05633459, Feb–Sept 2026) reported tissue STMN2 TE & low-dose subgroup pNfH drop (validates target, not #2 oligo)"),
            ("GENCODE v46 Reference Hybridization", "GATE", "Clean >=2mm on #2 (mRNA 0/0/0, 50bp-SS 1mm=0); empirical PS protein-binding & TLR9 screens required"),
            ("Biophysical Melting Window", "LOW", "#2 modeled Tm ~64C [MODEL_PRIOR] avoids #1's hyper-stable ~74C self-dimerization risk"),
        ],
        "struct_note": "SCG10 (Q93045, 179 aa) N-terminal palmitoylated Golgi membrane anchor + tubulin-binding stathmin repeats; supports distal NMJ integrity parallel to SARM1 (PMID:35767949; Beccari et al. 2025 PMID:40392845).",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "STMN2 (ENSG00000104435, gnomAD v4 LOEUF = 0.261) is the most abundant and penetrant TDP-43 cryptic-polyadenylation loss in human motor neurons (Klim et al. 2019 PMID:30643298; Melamed et al. 2019 PMID:30643292; Bryce-Smith et al. 2025 PMID:40038262: 383/926 ALS-TDP vs 0/750 controls). Loss of SCG10 collapses neuromuscular microtubule outgrowth and fast-fatigable NMJ maintenance."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Translational loss in TDP-43-depleted human i3Neurons (-2.924 log2FC Ribo-seq, FDR=1.6e-173; PMID:35197628) replicates in NYGC lumbar cord (-0.771 log2FC, 95% CI -1.110 to -0.433, p=2.47e-5; GSE153960), with nominal -28% homogenate protein reduction in C9-FTD frontal cortex (-0.4825 log2FC, p=0.0140, FDR=0.11, n=20; PXD083082 — indirect cortical evidence for sporadic spinal MNs). Paradoxically, whole-gene cortical STMN2 RNA rises in NYGC Frontal (+0.318, p=6.29e-6) and surviving BA4 L5_Exc snRNA (+0.497, p=2.23e-4; PMID:38518782) because exon-2a premature polyadenylation accumulates stable non-NMD tSTMN2 RNA without translating full-length SCG10."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "Sponsor-reported interim Phase 1/2 ANQUR disclosures for QRL-201 (NCT05633459, Feb–Sept 2026; alongside BIIB147 NCT07855211) distinguished tissue STMN2 splice restoration from downstream CSF pNfH changes — where significant CSF pNfH lowering (~46%) occurred in the low-dose DRF subgroup vs ~5% at 10 mg while 10 mg drove ~50% ALSFRS-R slowing (consistent with high-bolus PS-ASO radicular/DRG shedding masking early pNfH drops). Accordingly, C002 pairs strand-specific CSF PK -> NHP splice bridging with L1CAM+/ATP1A3+ NDEV pre-amplified tSTMN2 dPCR/Nanopore + ultrasensitive soluble SCG10 TE and >=16–24 wk post-loading pNfH/NfL PD on Clean >=2mm anchor #2 (chr8:79616829-79616846(+))."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Rather than duplicating standalone STMN2 ASOs, ExploreALS gates STMN2 #2 on Stage 1 single-entity GLP NHP IT tox, C3–C5/BA4 full-length vs tSTMN2 rescue, and Stage 2 genotype-stratified 2-plex vs 3-plex testing across rs12973192/rs12608932 genotypes (unvalidated 24–48 mg scenarios gated on Ca2+/Mg2+-chelation, DRG/autonomic, and <1–2% endosomal-escape competition beyond single-agent DEVOTE PMID:41634391) under 21 CFR 300.50 alongside parallel oral SARM1 T-lock protection (#1 S06)."),
        ],
    },
    "C007": {
        "subtitle": "Intrathecal HLE/ECM sST2 C-Tail (aa 320–328) Sweeping Biologic or Endothelial-Targeted Intron-8 PAS SSO Sparing Treg ST2L",
        "ident": [
            ("Gene / HGNC", "IL1RL1 (HGNC:5998)"), ("ST2L MANE", "ENST00000233954.6 (+) (556 aa)"), ("sST2 Isoform", "ENST00000311734.6 (+) (328 aa)"),
            ("3D Crystal", "PDB 4KC3 (IL-33–ST2 D1-D3)"), ("sQTL / eQTL", "rs1420101 · rs953934"),
            ("IDG TDL · Modality", "Tbio (Ph3 mAb Class) · IT Sweep mAb / Conj SSO"),
        ],
        "grades": [
            ("Multicellular Spatial & snRNA", "Zhang 55-um MN-niche Visium spots +3.76 (N=14); Edin Endo +3.11 (n=7 Ctrl)"),
            ("3D Interface & ASO Atlas", "PDB 4KC3 (PMID:23963640) D1-D3 shared; Mortberg 2023 (PMID:37188501) endo ASO gap"),
            ("Isoform & Oximetry Gate", "Gene-level RNA unresolved -> oximetry/capnography FVC>=80% CSF Simoa + microvessel ddPCR"),
        ],
        "verdict_box": {
            "pass_gate": "Living-patient CSF/plasma Simoa sST2 & free IL-33 (n>=80, explicitly stratified into verified normoxic [supine/upright FVC >= 80% PLUS normal overnight oximetry/capnography, PMID:41635251] non-NIV sALS vs nocturnal-hypoxic/NIV ALS to deconfound 3–20x hypoxic endothelial sST2 induction PMID:30562096, PMID:40402026) + ventilation-matched n>=25 sALS vs n>=20 Control isolated microvessel sST2/ST2L ddPCR confirms pre-hypoxic sST2 decoy excess (resolving Secreted Decoy sST2 vs. Membrane ST2L), AND intrathecal HLE aa 320–328 sweeping biologic or IT endothelial-conjugated Intron-8 PAS SSO clears CNS sST2 >=70% while sparing Treg ST2L and GTEx Lung (140.08 TPM).",
            "kill_gate": "Living-CSF sST2 elevation restricted to nocturnal-hypoxic/NIV ALS (flat in oximetry-verified normoxic sALS), microvessel ddPCR showing protective ST2L rather than sST2 induction, failure to engage capillary endothelium (PMID:37188501), OR concomitant Treg ST2L suppression.",
        },
        "related": ["S07", "C018", "C019"],
        "causal": {
            "callout_kind": "HAZARD",
            "nodes": [
                ("Gene-Level Neurovascular Surge", "Cortical endothelial IL1RL1 +3.11 (n=7 Ctrl, GSE290359) & 55-um Visium spots +3.76 (N=14)"),
                ("Unresolved Isoform Hypothesis", "Tests Intron-8 PAS sST2 decoy (ENST00000311734.6) vs compensatory membrane ST2L"),
                ("Proposed Perivascular IL-33 Sink", "If sST2 predominates (~400 pM Virchow-Robin [MODEL_PRIOR]), sequesters IL-33 from ST2L+ Tregs"),
                ("IT Sweep mAb / Conjugated PAS SSO", "IT HLE aa 320–328 sweep mAb or IT endothelial-targeted PAS SSO spares Treg ST2L"),
            ],
            "trap_title": "ISOFORM, NOCTURNAL HYPOXIA & DELIVERY HAZARD — Gene-Level Blind Spots & Naked IT ASO Gap",
            "trap_desc": "3' snRNA-seq and 55-um multicellular Visium spots do not separate sST2 from ST2L; FVC >= 80% alone misses mild-ALS nocturnal hypoxia (PMID:41635251) that spikes vascular sST2 3–20x; pan-ST2 mAbs block Treg ST2L (PDB 4KC3); and brain capillaries resist naked IT 2'-MOE ASOs (PMID:37188501).",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "log2fc", "tone": "disease_gain", "lbl": "Zhang 55-um MN-Niche Visium Spots (N=14, spot-level)", "val": 3.761, "stat": "+3.761 log2FC", "p": "spot FDR=1.85e-9", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_gain", "lbl": "Edinburgh Cortical Endo (n=29; n=7 Ctrl, GSE290359)", "val": 3.106, "stat": "+3.106 log2CPM", "p": "p=0.00641", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "null_or_diluted", "lbl": "NYGC Bulk Cortex ALS-Glia (N=67, GSE153960)", "val": 0.216, "stat": "+0.216 log2CPM", "p": "p=0.651 NS", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "null_or_diluted", "lbl": "Prudencio Bulk Frontal-Cereb (N=15, GSE67196)", "val": -0.322, "stat": "-0.322 log2FC", "p": "p=0.660 NS", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "sST2 clearance vs 5 nM pan-ST2 mAb on Treg ST2L", "stat": "28.2% vs 0.32%", "p": "8.8x Treg!", "tag": "MODEL_PRIOR"},
                {"lbl": "Trautwig 2025 CSF DIA (N=259, PMC12082929) LoQ check", "stat": "0 peptides", "p": "Needs Simoa", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 IL1RL1 Isoform Bifurcation: Soluble sST2 (ENST00000311734.6) vs Treg ST2L",
            "caption": "Exons 1–8 encode shared D1–D3 (PDB 4KC3). GENCODE v46 sST2 (ENST00000311734.6) uses terminal Exon 8 + intron-8 polyA chr2:102343269-102346100(+), whereas ST2L (ENST00000233954.6) splices to Exons 9–11 (102351535-102352037(+)). Isoform ratio in ALS CNS remains to be measured.",
            "strand": "+", "chrom": "chr2", "win_lo": 102340000, "win_hi": 102352200,
            "zoom_lo": 102343200, "zoom_hi": 102348200,
            "empty_cis_note": "Pre-SSO Simoa/ddPCR isoform gate · sST2 PAS chr2:102343269-102346100(+)",
            "exons": [
                {"lbl": "Exon 8 (D3)", "lo": 102343269, "hi": 102343415, "kind": "canon"},
                {"lbl": "Intron-8 sST2 Readthrough + PAS (Decoy)", "lo": 102343416, "hi": 102346100, "kind": "ce"},
                {"lbl": "Exon 9–11 (ST2L TM+TIR)", "lo": 102347945, "hi": 102352037, "kind": "skip"},
            ],
            "snps": [{"lbl": "rs1420101 sQTL (q=0.997)", "pos": 102341256}],
        },
        "safety": [
            ("Het-pLoF Population Constraint", "LOW", "gnomAD v4 pLI = 8.6e-6, LOEUF = 1.063 — no het-pLoF depletion (does not certify Treg ST2L blockade)"),
            ("Isoform Selectivity (ST2L Sparing)", "GATE", "Must resolve Secreted Decoy sST2 vs. Membrane ST2L first, targeting only sST2 aa 320–328 or Intron-8 PAS"),
            ("CNS Route & Capillary Delivery", "GATE", "Mortberg 2023 (PMID:37188501) shows naked IT 2'-MOE poorly silences capillary endothelium; IT HLE sweep mAb or IT endothelial-conjugated SSO avoids GTEx Lung = 140.08 TPM IV sink"),
            ("Opposing Enhancer Genetics", "GATE", "rs953934 shows opposing endothelial (-0.996) vs CD4+ T (+0.991) AlphaGenome quantiles"),
            ("Oximetry-Verified Normoxic Gate", "GATE", "FVC >= 80% alone misses nocturnal hypoxia (PMID:41635251); requires overnight oximetry/capnography + non-NIV CSF Simoa"),
        ],
        "struct_note": "PDB 4KC3 (PMID:23963640, IL-33 bound to ST2 ectodomain D1–D3): all 30 heavy-atom interface contacts are 100% shared between sST2 (328 aa) and ST2L (556 aa) — only sST2's C-terminal tail (aa 320–328) or Intron-8 PAS RNA is isoform-unique.",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "IL1RL1 (ENSG00000115602, Q01638) bifurcates via Intron-8 alternative polyadenylation into neuroprotective transmembrane ST2L (ENST00000233954.6) on meningeal/CNS FOXP3+ Tregs versus secreted decoy sST2 (ENST00000311734.6). Because current ALS datasets measure gene-level IL1RL1 rather than isoform-resolved protein, C007 tests the pathway hypothesis that perivascular endothelial sST2 decoy excess — rather than compensatory ST2L induction — sequesters astrocytic IL-33 in ALS motor niches."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Because neurovascular endothelial cells comprise <2% of cortical nuclei, bulk cortical RNA-seq is flat (NYGC p=0.651; Prudencio p=0.660), whereas 55-um multicellular cervical anterior-horn MN-niche Visium spots (+3.761 log2FC, spot-level FDR=1.85e-9 across N=14 donors; Zhang et al. 2026 PMID:42135512) and donor-collapsed cortical endothelial nuclei (+3.106 log2CPM, p=0.00641, small n=7 control group; GSE290359) show strong gene-level IL1RL1 induction. Because hypoxia and mechanical ventilation spike endothelial sST2 3–20x (PMID:30562096; PMID:40402026) and FVC >= 80% does not exclude nocturnal hypoventilation in mild ALS (PMID:41635251), validation requires overnight-oximetry/capnography-verified normoxic CSF Simoa plus ventilation-matched microvessel sST2/ST2L ddPCR (n>=25/20)."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "PDB 4KC3 (PMID:23963640) proves systemic pan-ST2 antibodies (astegolimab) ablate Treg ST2L signaling, while NHP/mouse ASO atlases (Mortberg et al. 2023, PMID:37188501) show brain capillary endothelial cells resist unconjugated intrathecal 2'-MOE ASOs — and IV conjugates face a 140.08 TPM GTEx Lung sink. Contingent on confirming pathogenic sST2 excess, ExploreALS gates an intrathecal HLE sST2 C-tail (aa 320–328) sweeping biologic or IT endothelial-targeted Intron-8 PAS SSO (chr2:102343269-102346100(+))."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Gated first on paired living-patient CSF Simoa soluble sST2 & free IL-33 explicitly comparing oximetry/capnography-verified normoxic (supine/upright FVC >= 80%, non-NIV) sporadic ALS vs nocturnal-hypoxic/NIV ALS alongside BioVendor-bridged CSF pNfH and the C019 CSF panel before any therapeutic lead generation."),
        ],
    },
}
