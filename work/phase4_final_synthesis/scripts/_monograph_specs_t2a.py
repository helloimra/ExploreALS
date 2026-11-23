"""Translational Monograph Standard v3.1 (5Rs + Open Targets + Script/Checksum Provenance) — Part 2: #3 C001, #5 C002, #6 C007."""
from __future__ import annotations

MONOGRAPH_SPECS_T2A: dict[str, dict] = {
    "C001": {
        "subtitle": "Promoted Intrathecal Steric SSO (#2) Blocking UNC13A Intron 20–21 Cryptic Exon Inclusion",
        "ident": [
            ("Gene / HGNC", "UNC13A (HGNC:23150)"), ("MANE", "ENST00000519716 (-)"), ("UniProt", "Q9UPW8 (1,703 aa)"),
            ("ALS GWAS", "rs12608932 · rs12973192"), ("Promoted SSO", "#2 chr19:17642537-17642554(-)"),
            ("IDG TDL · Modality", "Tchem (Non-Sel C1) / Pre-mRNA SSO · IT 2'-MOE"),
        ],
        "grades": [
            ("Human GWAS & Postmortem", "van Rheenen GWAS P=3.0e-25 (PMID:34873335; OT 6-study p=4.04e-25); Spillman C9-FTD 6/10 (PMID:42789089)"),
            ("Splicing & Synaptic Rescue", "Brown CE dPSI=+0.463 & Intron-31 IR +0.354; Keuss 2026 Nature PMID:43015463"),
            ("GENCODE v46 Scan Prior", "Promoted #2 Caution (mRNA 0/0/0, 50bp-SS 1mm=0, bulge=0; 25bp-SS 2mm=4, DNA AVI=23.1)"),
        ],
        "verdict_box": {
            "pass_gate": "Stage 1 single-entity UNC13A #2 completes sponsor-owned ICH M3(R2) GLP IT tox (zero 21 CFR 312.23(b) right of reference to LY4256984/TRCN-1023) and establishes NHP cervical (C3–C5 phrenic) & BA4 Betz parenchymal splice-rescue EC80 curves (verifying <=3 mg lumbar-to-BA4 rostral delivery and absence of 178-bp upstream cryptic 3'SS shunting at chr19:17642591, PMID:35197626) + 3-layer Phase 1b PK/TE/PD (strand-specific CSF PK, L1CAM+/ATP1A3+ NDEV pre-amplified dPCR/Nanopore with ISEV EV controls PMID:38158550 + CSF synaptic secretome NPTX2/VGF/SNAP25 TE, and >=16–24 wk post-loading CSF pNfH/NfL PD accounting for ANQUR 3 mg vs 10 mg dissociation ahead of pivotal CONQUR), and Stage 2 21 CFR 300.50 genotype-stratified randomization (2-plex vs 3-plex across rs12973192/rs12608932 genotypes, targeting a 6–9 mg [<=3 mg/strand] multiplex polyanion/DRG margin while reclassifying unvalidated 24–48 mg 3-plex loads as a hazard) rescues all junctions >=65% without saturating <1–2% endosomal escape or triggering Ca2+/Mg2+-chelation, TLR9, or DRG tox.",
            "kill_gate": "Competitive scavenger-receptor uptake or productive late-endosomal escape loss >30% vs 1-plex, shunting to the upstream 178-bp cryptic 3'SS (chr19:17642591), inadequate cervical/BA4 parenchymal splice rescue, acute human neuron Ca2+-oscillation/DRG neurotox, OR failure to restore Munc13-1 synaptic vesicle priming.",
        },
        "related": ["C006", "C002", "DN-01", "DN-04"],
        "causal": {
            "callout_kind": "CAUTION",
            "nodes": [
                ("TDP-43 Loss + Risk Alleles C/G", "CE-internal rs12973192-G & intronic (+534 bp) rs12608932-C potentiate susceptibility (severe TDP-43 loss still mis-splices A/A, PMID:35197628)"),
                ("Intron 20–21 Cryptic Exon (128/178 bp)", "chr19:17642414-17642541(-) (plus 178-bp upstream 3'SS at 17642591, PMID:35197626) triggers frameshift NMD"),
                ("Presynaptic Vesicle Priming Failure", "Munc13-1 loss collapses glutamatergic neuromuscular synaptic transmission"),
                ("Promoted Steric SSO (#2 Lead)", "chr19:17642537-17642554(-) masks 128-bp cryptic 3'SS; genotype-stratified multiplex"),
            ],
            "trap_title": "ASSAY, INTRON-31 CEILING & GENOTYPE CAUTION — Read-Length Bias, ~58–62% WT Cap & A/A Susceptibility",
            "trap_desc": "In NYGC GSE153960, 100bp NovaSeq misses UNC13A CE 3.89x vs 125bp HiSeq (p=3.38e-4). Under severe TDP-43 KD & LSV independence [MODEL_PRIOR], downstream Intron-31 retention (dPSI=+0.354, source MAJIQ 'FDR' [p_d_psi_0.05]=1.82e-15; Exon 31–32 PSI 0.791->0.461) caps Intron-20-only ASO mRNA near 46.1–55.6% raw PSI (~58.3–61.6% of WT baseline — above Keuss 2026's >30% in vitro cellular rescue boundary, PMID:43015463; cf. ~25% STMN2 boundary in Baughn 2023 PMID:36927019, both preclinical model-specific benchmarks rather than validated human clinical thresholds), while A/A (~43% NFE) informs stratification rather than exclusion.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron Intron-20 CE junction (PMID:35197628)", "val": 0.463, "stat": "dPSI = +0.463", "p": "FDR=2.31e-19", "tag": "MEASURED"},
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron Intron-31 retention (PSI 0.097 -> 0.444, PMID:35197628)", "val": 0.354, "stat": "dPSI = +0.354", "p": "MAJIQ 'FDR'=1.82e-15", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq UNC13A (PMID:35197628)", "val": -0.781, "stat": "-0.781 log2FC", "p": "padj=0.0296", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Lumbar Cord GC+cell OLS (n=92, GSE153960)", "val": -0.355, "ci": [-0.554, -0.157], "stat": "-0.355 log2FC", "p": "p=7.38e-4", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Spillman C9-FTD Synaptosome DIA (n=20, PMID:42789089)", "val": -0.250, "stat": "-0.250 log2FC", "p": "p=0.0502", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Keuss 2026 in vitro MN eEPSC/MEA boundary (PMID:43015463)", "stat": ">30% Munc13-1 (model-spec.)", "p": "cf. ~25% STMN2", "tag": "MEASURED"},
                {"lbl": "Intron-20-only ASO ceiling (severe KD: raw vs WT-normalized)", "stat": "46.1–55.6% (~58–62% WT)", "p": "Exon 31–32 0.461", "tag": "MODEL_PRIOR"},
                {"lbl": "Spillman C9-FTD CE junction detection (n=20, PMID:42789089)", "stat": "6/10 vs 0/10 Ctrl", "p": "p=0.0108", "tag": "MEASURED"},
                {"lbl": "NYGC 125bp HiSeq vs 100bp NovaSeq CE bias (n=201, GSE153960)", "stat": "OR = 3.89x (30.9% vs 10.3%)", "p": "p=3.38e-4", "tag": "MEASURED"},
                {"lbl": "AlphaGenome rs12973192 DLPFC DNA-variant splice quantile", "stat": "q = 0.989 (AVI=8.90)", "p": "GWAS sQTL", "tag": "MODEL_PRIOR"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 UNC13A Intron 20–21 Cryptic Exon, GWAS Risk SNPs & SSO Walk (chr19, -)",
            "caption": "Coordinate-only search-window anchor #2 (chr19:17642537-17642554(-), 0 chemically modified synthesis-ready ASO sequences) achieves zero <=1-mm/wobble/bulge reference hybridization (CAUTION on 25bp-SS 2mm=4) 107 bp upstream of rs12973192; 14 kb downstream (chr19:17628338-17629239), TDP-43 Intron-31 retention (dPSI=+0.354) implies a [MODEL_PRIOR] 46.1–55.6% raw (~58.3–61.6% WT-normalized) Intron-20-only mRNA ceiling under severe TDP-43 KD (above Keuss 2026's >30% in vitro cellular boundary; human clinical threshold unproven).",
            "strand": "-", "chrom": "chr19", "win_lo": 17641350, "win_hi": 17643000,
            "zoom_lo": 17642400, "zoom_hi": 17642610,
            "exons": [
                {"lbl": "Exon 21", "lo": 17641393, "hi": 17641556, "kind": "canon"},
                {"lbl": "Cryptic Exon (128bp PTC)", "lo": 17642414, "hi": 17642541, "kind": "ce"},
                {"lbl": "Exon 20", "lo": 17642845, "hi": 17642960, "kind": "canon"},
            ],
            "snps": [
                {"lbl": "rs12608932 (GWAS)", "pos": 17641880},
                {"lbl": "rs12973192 (CE)", "pos": 17642430},
                {"lbl": "178bp Alt 3'SS", "pos": 17642591},
            ],
        },
        "safety": [
            ("Restoration on Constrained Gene", "MITIGATED", "gnomAD v4.1 MANE pLI = 1.000, LOEUF = 0.389 (61/194.0 LoF; Open Targets / legacy gene constraint LOEUF = 0.344; biallelic LoF causes fatal synaptic encephalopathy PMID:27648472; SSO restores WT)"),
            ("Dividing-Line Context (DepMap)", "GATE", "Mean Chronos = -0.043 in dividing cancer lines (which lack synapses; canonical splicing preservation mandatory)"),
            ("CNS Specificity & IT Delivery", "LOW", "Strictly neuronal presynaptic expression; IT 2'-MOE restricts exposure to CNS"),
            ("GENCODE v46 Reference Hybridization", "GATE", "CAUTION on #2 under harmonized <=25bp 2-mm == 0 rule (mRNA 0/0/0, 50bp-SS 1mm=0, bulge=0, sub18=0; 25bp-SS 2mm=4); empirical PS protein-binding, TLR9, DRG & 178-bp upstream 3'SS checks required"),
            ("Polymorphism Masking (gnomAD v4)", "LOW", "#2 starts 107 bp upstream of rs12973192 (106 intervening bases), ensuring genotype-agnostic binding"),
        ],
        "struct_note": "Munc13-1 (Q9UPW8) MUN domain catalyzes SNARE syntaxin-1 opening; pairs with C006 (excitability) and C002 (axonal outgrowth) via genotype-stratified multiplex testing across rs12973192/rs12608932 genotypes.",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "UNC13A (ENSG00000130477, gnomAD v4.1 MANE LOEUF = 0.389; Open Targets / legacy gene constraint LOEUF = 0.344) is the strongest human-genetics-anchored TDP-43 cryptic-splicing target in ALS: GWAS risk alleles rs12608932-C (van Rheenen et al. 2021 PMID:34873335, P=3.0e-25; Open Targets p=4.04e-25 across 6 catalog studies) and cryptic-exon-internal rs12973192-G directly weaken TDP-43 repression and potentiate Intron 20–21 cryptic exon inclusion and NMD loss of presynaptic Munc13-1, though severe nuclear TDP-43 depletion still triggers cryptic splicing in A/A homozygotes (~43% in gnomAD v4 non-Finnish Europeans vs ~35–38% in European ALS cohorts; Brown et al. 2022 PMID:35197628; Ma et al. 2022 PMID:35197626).\n\nIn cellular and humanized mouse models, Keuss et al. 2026 (Nature, PMID:43015463, DOI:10.1038/s41586-026-11256-2) directly tested human functional rescue: in HaloTDP human cortical iNeurons (rs12608932 A/A, rs12973192 C/C) and human iPSC spinal motor neurons (rs12608932 A/C & C/C), isolated CRISPR deletion of the Intron-20 cryptic exon (~75% protein recovery; >30% in vitro cellular synaptic boundary — comparable to Baughn et al. 2023 PMID:36927019's ~25% STMN2 regeneration boundary in human iPSC-MNs, both representing model-specific preclinical benchmarks rather than validated human clinical efficacy thresholds) or 18/21-nt 2'-O-MOE steric ASOs (~35.8% full-length splicing / ~62.2% protein in patient iPSC-MNs, Fig. 3c,f) restored presynaptic UNC13A, mEPSC frequency, evoked AMPA eEPSCs, and MEA network synchrony (noting Fig. 4c–e p=0.052 on one pooled motor-neuron electrophysiology sub-panel, while postsynaptic mEPSC amplitude reduction remained unrescued). Mechanistically, Intron-20 UNC13A rescue acts orthogonally to STMN2 polyadenylation (C002), KCNQ2 Exon-5 skipping (C006), and downstream UNC13A Intron-31 retention (Brown MAJIQ PSI 0.097->0.444, dPSI=+0.3543, FDR=1.82e-15, cutting Exon 31–32 canonical splicing 0.791->0.461 and implying a [MODEL_PRIOR] 46.1–55.6% raw PSI [~58.3–61.6% of WT baseline] Intron-20-only ASO mRNA ceiling under severe CRISPRi TDP-43 KD and LSV independence vs partial HaloTDP depletion/protein half-life)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Re-computing NYGC postmortem RNA-seq (GSE153960) proved 100bp NovaSeq under-detects UNC13A cryptic junctions 3.89-fold vs 125bp HiSeq (p=3.38e-4), and lumbar cord mRNA depletion (-0.355 log2FC, 95% CI -0.554 to -0.157, p=7.38e-4) emerges after GC and cell-composition adjustment, alongside indirect C9-FTD (1/10 FTD-MND) cortical synaptosome Munc13-1 loss (-0.250 log2FC, p=0.0502, n=20; Spillman et al. 2026 PMID:42789089, PXD083082). Because unfractionated lumbar CSF EVs sit in the late-cycle RT-qPCR (Cq>35) / Poisson-limited (<3–10 copies/mL) ddPCR regime and CSF pNfH is a target-agnostic injury PD marker that showed inverse dose dissociation in QRL-201 ANQUR data (3 mg Day-197 -46% drop vs ~5% at 10 mg, with Day-421 10 mg->3 mg OLE -36% plasma NfL co-driven by down-dosing washout, remodeling lag & 41/52 attrition ahead of pivotal CONQUR), Phase 1b pairs strand-specific CSF PK -> NHP splice bridging with L1CAM+/ATP1A3+ NDEV pre-amplified dPCR/Nanopore (with ISEV EV controls, PMID:38158550) + CSF synaptic secretome (NPTX2/VGF/SNAP25) TE and >=16–24 wk post-loading pNfH/NfL PD."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "Specific rescue requires intrathecal 2'-MOE steric splicing modulation: published Keuss et al. 2026 2'-MOE ASOs in humanized hUNC13A mice (UCL WO2022122872A1; Stanford WO2022216759A1 / CA3213590A1 Table 7B ASO-121 & ASO-132, which contain #2 and #1 with experimental qPCR rescue; Ionis US20240301415A1 Compound 1616106 [SEQ ID NO: 86], an exact 18-mer match to #2 tested in SH-SY5Y cryptic-RNA [38% of control] and canonical-RNA [84%] assays; Roche (CA)n WO2022018187A1 / US12084657B2; Takeda WO2025186619A1 / US20250283083A1), preclinical AS-241, upstream SYF2 spliceosome ASO (PMID:36736291) & VectorY AAV anti-TDP-43 VTx-002, single-vector dual STMN2+UNC13A U7 snRNA platforms (UCL/KCL WO2023237638A1; Mehta et al. 2025 PMID:41394711; UCSD SURF-sg1/sg2 Gomberg et al. 2025 PMID:41573891 [PREPRINT], which avoid multi-oligo dosing via nuclear Sm-ring RNP engagement at the expense of irreversible adult intrathecal AAV transduction & DRG immunogenicity limits), and 2 clinical ASO assets across 4 registry protocols — Lilly/QurAlis LY4256984/QRL-204 (EXCEED parent basket NCT07100119, substudy NCT07571174, OLMP NCT07571200) and Trace Neuroscience TRCN-1023 (Phase 1/2 FUNCtion ALS NCT07674667 plus China investigator-initiated LAUNCH ALS) — validate target biology, while promoted 3'SS anchor #2 (chr19:17642537-17642554(-), modeled Tm ~64C [MODEL_PRIOR], DNA-variant AVI=23.1, 107 bp upstream of polymorphic rs12973192) represents in silico GENCODE v46 reference-hybridization selection within this patented and experimentally tested canonical 3'SS hotspot (chr19:17642541) rather than claiming potency superiority or freedom-to-operate, gated on empirical 1-nt microwalk suppression of both the 128-bp CE 3'SS and the 178-bp upstream cryptic 3'SS (chr19:17642591, PMID:35197626) plus Ca2+/Mg2+-formulated Ca2+-oscillation/TLR9/DRG safety."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Evaluated in Stage 2 under FDA co-development guidance / 21 CFR 300.50 factorial contribution principles via prospective genotype-stratified randomization testing 2-plex (KCNQ2 C006 + STMN2 C002) vs 3-plex (+UNC13A C001; noting Chi et al. 2024 Les Turner ALS Symposium Poster 24 previously proposed co-targeting UNC13A, STMN2, and KCNQ2 via spherical nucleic acids) across both rs12973192-G/rs12608932-C risk carriers and A/A homozygotes (targeting a multiplex polyanion/DRG margin of EC80<=3 mg/strand = 6 mg 2-plex to 9.0 mg equimolar 18-bp 3-plex Q8W–Q12W calibrated to ANQUR 3 mg vs 10 mg pNfH dissociation, while noting single-agent nusinersen 12–50 mg PMID:41634391 & tofersen 100 mg PMID:36129998 tolerate higher single-ASO IT masses and reclassifying unvalidated 24–48 mg 3-plex loads as a radiculotoxicity hazard).\n\nAdvancement is gated on Stage 1 ICH M3(R2) single-entity GLP NHP IT tox (zero 21 CFR 312.23(b) external right of reference), C3–C5/BA4 splice rescue (checking <=3 mg lumbar-to-BA4 rostral dilution), and <1–2% endosomal-escape competition curves."),
        ],
    },
    "C002": {
        "subtitle": "Promoted Intrathecal Steric SSO (#2) Masking Proximal STMN2 Exon-2a (+8..+25) to Suppress Cryptic 3'SS & Premature Polyadenylation",
        "ident": [
            ("Gene / HGNC", "STMN2 (HGNC:10577)"), ("MANE", "ENST00000220876 (+)"), ("UniProt", "Q93045 (SCG10, 179 aa)"),
            ("Clinical Benchmark", "QRL-201 CONQUR IND / NCT05633459 · BIIB147"), ("Promoted SSO", "#2 chr8:79616829-79616846(+)"),
            ("IDG TDL · Modality", "Tbio (Pivotal IND ASO) · Intrathecal 2'-MOE SSO"),
        ],
        "grades": [
            ("Human Pathology & CONQUR IND", "NYGC lumbar -0.771; QRL-201 ANQUR DRF (N=52 done) / OLE (N=41 ongoing) + 16 Nov 2026 CONQUR IND"),
            ("Ribo-seq, NMJ & Parallel Axons", "Ribo-seq -2.924; Matson 2026 TIRF/NMJ [PREPRINT]; Baughn 2023 PMID:36927019; Beccari 2025 PMID:40392845"),
            ("GENCODE v46 Scan Prior", "Promoted #2 Caution (mRNA 0/0/0, 50bp-SS 1mm=0, bulge=0; 25bp-SS 2mm=2, DNA AVI=20.86)"),
        ],
        "verdict_box": {
            "pass_gate": "Bliss/Loewe additivity or synergy on axon outgrowth & NAD+ preservation when combining STMN2 #2 SSO with sub-IC80 allosteric SARM1 T-lock (S06; evaluating 1.0x parallel Bliss protection vs illustrative ~2–7x MWC scenario [MODEL_PRIOR]) in axotomized TDP-43-KD human iPSC-MNs + Stage 1 ICH M3(R2) single-entity GLP IT tox & NHP cervical (C3–C5) / BA4 Betz splice EC80 bridging (checking <=3 mg lumbar-to-BA4 rostral delivery) + 3-layer PK/TE/PD (strand-specific CSF PK, L1CAM+/ATP1A3+ NDEV tSTMN2 dPCR/Nanopore + ultrasensitive soluble SCG10 TE, and >=16–24 wk post-loading CSF pNfH/NfL PD) + Stage 2 21 CFR 300.50 6–9 mg (<=3 mg/strand) multiplex polyanion/DRG/Ca2+/uptake safety (reclassifying unvalidated 24–48 mg loads as a radiculotoxicity hazard).",
            "kill_gate": "Redundant functional ceiling with allosteric SARM1 T-lock alone OR >30% competitive uptake / endosomal-escape loss, human neuron Ca2+-oscillation/DRG/autonomic neurotox, or cervical/BA4 sub-efficacy in 2-plex/3-plex co-delivery.",
        },
        "related": ["S06", "C006", "C001"],
        "causal": {
            "callout_kind": "RATIONALE",
            "nodes": [
                ("Nuclear TDP-43 Depletion", "Derepresses Intron-1 cryptic 3'SS (chr8:79616822) & premature PAS (Klim 2019 PMID:30643292; Melamed 2019 PMID:30643298; Baughn 2023 PMID:36927019)"),
                ("Truncated Exon-2a mRNA (227 bp)", "Terminates transcription after Exon 1; ablates full-length SCG10 protein (Q93045)"),
                ("Microtubule Dynamicity & NMJ Loss", "STMN2 loss reduces plus-end dynamicity/catastrophe & impairs post-stress regeneration/NMJ resilience (10.64898/2026.11.07.764673 [PREPRINT]; PMID:40392845; PMID:35767949)"),
                ("Promoted SSO (#2) + SARM1 T-Lock", "chr8:79616829-79616846(+) (+8..+25 Exon-2a) restores SCG10 alongside non-redundant SARM1 T-lock"),
            ],
            "trap_title": "COMBINATORIAL & PD CAUTION — Parallel Stmn2/Sarm1 Genetics & Ongoing ANQUR 10mg->3mg OLE",
            "trap_desc": "Krus et al. 2022 (PMID:35767949) showed Stmn2 acts in parallel to Sarm1 in mice (with Beccari 2025 PMID:40392845 adding NMNAT2 transport & tubulin-independent roles). In QRL-201 ANQUR (N=69: completed N=52 DRF + ongoing N=41 3 mg OLE; CONQUR IND 16 Nov 2026), Day-197 CSF pNfH fell -46% vs baseline at 3 mg vs ~5% at 10 mg, while Day-421 10mg->3mg OLE -36% NfL vs baseline co-reflects washout, lag & 41/52 attrition.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Brown i3Neuron Ribo-seq STMN2 (PMID:35197628)", "val": -2.924, "stat": "-2.924 log2FC", "p": "FDR=1.6e-173", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Lumbar Cord GC+cell OLS (n=92, GSE153960)", "val": -0.771, "ci": [-1.110, -0.433], "stat": "-0.771 log2FC", "p": "p=2.47e-5", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Spillman C9-FTD Homogenate DIA (n=20, PMID:42789089)", "val": -0.483, "stat": "-0.483 (-28%)", "p": "p=0.014, FDR=0.11", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "compensatory_or_survivor", "lbl": "Pineda Surviving BA4 L5_Exc snRNA (n=32, PMID:38521060)", "val": 0.497, "stat": "+0.497 log2FC", "p": "p=2.23e-4", "tag": "MEASURED"},
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron Exon-2a cryptic ALE (PMID:35197628)", "val": 0.482, "stat": "dPSI = +0.482", "p": "FDR=3.02e-18", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Pineda BA4_Exc STMN2–NMNAT2 co-variation (n=32, PMID:38521060)", "stat": "Pearson r = +0.928", "p": "p=1.95e-14", "tag": "MEASURED"},
                {"lbl": "Bryce-Smith NYGC postmortem tSTMN2 specificity (PMID:41120751)", "stat": "383/926 vs 0/750", "p": "100% TDP+", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 STMN2 Intron-1 Cryptic Exon-2a / Premature PAS & SSO Walk (chr8, +)",
            "caption": "Coordinate-only search-window anchor #2 (chr8:79616829-79616846(+), 0 chemically modified synthesis-ready ASO sequences, modeled Tm ~64C [MODEL_PRIOR], DNA AVI=20.86) masks +8..+25 bp inside Exon-2a (suppressing cryptic 3'SS recognition & downstream PAS usage, cf. Baughn et al. 2023 PMID:36927019) with zero <=1-mm/wobble/bulge GENCODE v46 reference hits (CAUTION on 25bp-SS 2mm=2).",
            "strand": "+", "chrom": "chr8", "win_lo": 79611000, "win_hi": 79637000,
            "zoom_lo": 79616800, "zoom_hi": 79617060,
            "exons": [
                {"lbl": "Exon 1", "lo": 79611117, "hi": 79611214, "kind": "canon"},
                {"lbl": "Cryptic Exon 2a + PAS (227bp)", "lo": 79616822, "hi": 79617048, "kind": "ce"},
                {"lbl": "Exon 2", "lo": 79636802, "hi": 79636897, "kind": "canon"},
            ],
            "snps": [{"lbl": "Cryptic 3'SS AVI=23.6", "pos": 79616821}, {"lbl": "Premature PAS (ATTAAA)", "pos": 79617025}],
        },
        "safety": [
            ("Restoration on Constrained Gene", "MITIGATED", "gnomAD v4.1 MANE pLI = 1.000, LOEUF = 0.250 (2/25.1 LoF; Open Targets / legacy gene constraint LOEUF = 0.261) — restores endogenous SCG10"),
            ("Peripheral / DRG Expression Check", "GATE", "Dividing-line Chronos = -0.047, but STMN2 is expressed in peripheral sympathetic/autonomic & DRG neurons -> IT DRG/autonomic monitoring"),
            ("ANQUR Ph1 & Pivotal CONQUR IND", "GATE", "QRL-201 ANQUR (N=69: completed N=52 DRF with 0 DRF SAEs; ongoing N=41 3 mg OLE) + 16 Nov 2026 CONQUR IND (validates target, not #2 oligo)"),
            ("GENCODE v46 Reference Hybridization", "GATE", "CAUTION on #2 under harmonized <=25bp 2-mm == 0 rule (mRNA 0/0/0, 50bp-SS 1mm=0, bulge=0, sub18=0; 25bp-SS 2mm=2); empirical PS protein-binding & TLR9 screens required"),
            ("Biophysical Melting Window", "LOW", "#2 modeled Tm ~64C [MODEL_PRIOR] avoids #1's hyper-stable ~74C self-dimerization risk"),
        ],
        "struct_note": "SCG10 (Q93045, 179 aa) N-terminal palmitoylated Golgi/vesicle membrane anchor + tubulin-binding stathmin repeats; promotes plus-end microtubule dynamicity/catastrophe while suppressing runaway tubulin polymerization to sustain post-stress axonal regeneration/NMJ resilience (10.64898/2026.11.07.764673 [PREPRINT]) plus tubulin-dimer-independent axonal regeneration & NMNAT2 vesicular co-transport (Beccari et al. 2025, PMID:40392845) alongside parallel SARM1 signaling (PMID:35767949).",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "STMN2 (ENSG00000104435, gnomAD v4.1 MANE LOEUF = 0.250; Open Targets / legacy gene constraint LOEUF = 0.261) is the most abundant and penetrant TDP-43 cryptic-polyadenylation loss in human motor neurons (Klim et al. 2019 PMID:30643292; Melamed et al. 2019 PMID:30643298; Baughn et al. 2023 PMID:36927019: ~25% in vitro STMN2 rescue restores neurite regeneration & lysosomal trafficking in TDP-43-deficient human motor neurons, a model-specific preclinical benchmark rather than an established human clinical threshold; Bryce-Smith et al. 2025 PMID:41120751: 383/926 ALS-TDP vs 0/750 controls). Because SCG10 normally promotes plus-end microtubule dynamicity/catastrophe and suppresses runaway tubulin polymerization, STMN2 loss reduces catastrophe and impairs post-stress neurite outgrowth, remodeling, and human iPSC-MN–myocyte neuromuscular junction resilience via a SARM1-independent pathway (Matson & Holzbaur 2026 [PREPRINT], 10.64898/2026.11.07.764673; Krus et al. 2022 PMID:35767949) alongside tubulin-dimer-independent axonal regeneration and vesicular NMNAT2 co-transport deficits (Beccari et al. 2025, PMID:40392845)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Translational loss in TDP-43-depleted human i3Neurons (-2.924 log2FC Ribo-seq, FDR=1.6e-173; PMID:35197628) replicates in NYGC lumbar cord (-0.771 log2FC, 95% CI -1.110 to -0.433, p=2.47e-5; GSE153960), with nominal -28% homogenate protein reduction in C9-FTD (1/10 FTD-MND) frontal cortex (-0.4825 log2FC, p=0.0140, FDR=0.11, n=20; Spillman et al. 2026 PMID:42789089, PXD083082 — indirect cortical evidence for sporadic spinal MNs). Paradoxically, whole-gene cortical STMN2 RNA rises in NYGC Frontal (+0.318, p=6.29e-6) and surviving BA4 L5_Exc snRNA (+0.497, p=2.23e-4; PMID:38521060) because exon-2a premature polyadenylation accumulates stable non-NMD tSTMN2 RNA without translating full-length SCG10."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "Phase 1 ANQUR disclosures for QRL-201 (NCT05633459, N=69 total: completed N=52 placebo-controlled DRF at 3 mg/10 mg with 0 DRF SAEs, ongoing N=41 3 mg OLE, and 16 Nov 2026 US FDA IND clearance for pivotal CONQUR in H1 2027; QurAlis WO2020247419A2, Harvard & UMass original-applicant WO2021195446A2, and QurAlis WO2023102242A2; alongside recruiting BIIB147 NCT07855211, Ionis/Ludwig granted Exon-2a patent US11833168 / WO2019241648A1, dual STMN2+UNC13A U7 snRNA platforms [UCL/KCL WO2023237638A1; UCSD SURF-sg1/sg2 Gomberg et al. 2025 PMID:41573891 [PREPRINT]], upstream SYF2 ASO PMID:36736291, and VectorY AAV anti-TDP-43 VTx-002) distinguished tissue STMN2 restoration from complex neurofilament kinetics: Day-197 CSF pNfH fell -46% vs baseline at 3 mg (p<0.01) vs ~5% at 10 mg; unreviewed Day-253 10 mg -50% ALSFRS-R slowing vs placebo relied on NEALS (5 Nov 2026) post-hoc exclusion of the top baseline-NfL fast-progressor tertile (while Day-337 3 mg plasma NfL was -31% vs placebo, p=0.07); and Day-421 10 mg->3 mg OLE plasma NfL -36% vs baseline (p=0.01 in 41/52 entrants) co-reflects 10 mg->3 mg down-dosing washout of high-bolus PS-ASO radicular/DRG shedding (tominersen/WVE-004 precedent), post-loading STMN2 remodeling lag, and 21.2% OLE attrition without a Day-421 placebo arm. Guided by Baughn et al. 2023 (PMID:36927019, rASO5 steric Exon-2a rescue principles), proximal Exon-2a (+8..+25) anchor #2 (chr8:79616829-79616846(+), representing in silico GENCODE v46 reference-hybridization hygiene within the patented Exon-2a hotspot rather than claiming clinical potency superiority or standalone unclaimed IP, and contrasting reversible 6–9 mg KCNQ2+STMN2±UNC13A ASO dosing against irreversible AAV-U7 WO2023237638A1) pairs strand-specific CSF PK -> NHP splice bridging with L1CAM+/ATP1A3+ NDEV pre-amplified tSTMN2 dPCR/Nanopore + ultrasensitive soluble SCG10 TE and >=16–24 wk post-loading pNfH/NfL PD."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Rather than duplicating standalone STMN2 ASOs, this synthesis gates STMN2 #2 on Stage 1 ICH M3(R2) single-entity GLP NHP IT tox (zero 21 CFR 312.23(b) right of reference to QRL-201/BIIB147) and C3–C5/BA4 full-length vs tSTMN2 rescue (evaluating <=3 mg lumbar-to-BA4 rostral dilution).\n\nStage 2 testing evaluates 21 CFR 300.50 genotype-stratified 2-plex vs 3-plex testing across rs12973192/rs12608932 genotypes (targeting a multiplex polyanion/DRG margin of EC80<=3 mg/strand = 6 mg 2-plex to 9.0 mg equimolar 18-bp 3-plex Q8W–Q12W calibrated to ANQUR 3 mg vs 10 mg pNfH dissociation, while noting single-agent nusinersen 12–50 mg PMID:41634391 & tofersen 100 mg PMID:36129998 tolerate higher single-ASO IT masses and reclassifying unvalidated 24–48 mg 3-plex loads as a hazard) alongside parallel oral SARM1 T-lock protection (#1 S06: 1.0x parallel Bliss lower bound to ~2–7x [med ~3x] MWC upper bound [MODEL_PRIOR])."),
        ],
    },
    "C007": {
        "subtitle": "Low-Dose Intrathecal Neurovascular-Shuttled sST2 3'-UTR siRNA / Zone 1 Intron-8 PAS Steric SSO (Primary) or Intact-FcRn sST2 C-Tail Sweeping Biologic (Backup) Sparing Treg ST2L",
        "ident": [
            ("Gene / HGNC", "IL1RL1 (HGNC:5998)"), ("ST2L MANE", "ENST00000233954.6 (+) (556 aa)"), ("sST2 Isoform", "ENST00000311734.6 (+) (328 aa)"),
            ("3D Crystal", "PDB 4KC3 (5 D1-D3 Disulfides)"), ("sQTL / eQTL", "rs1420101 · rs953934"),
            ("IDG TDL · Modality", "Tbio (Astegolimab ARNASA Ph3 p=0.068) · IT Shuttled RNA / Sweeping Biologic"),
        ],
        "grades": [
            ("Multicellular Spatial & snRNA", "Zhang 55-um Visium spots +3.76 (N=14 donors / 18 sections); Edin Endo +3.11 (n=28: 21v7, p=0.00698, PMID:42551425)"),
            ("3D Cys327 & ASO Atlas", "PDB 4KC3 (PMID:23980170) 10-Cys/5-SS leaves Cys327 unpaired; Mortberg 2023 (PMID:37188501) naked ASO gap"),
            ("Isoform, Oximetry & BBB Sign", "Oximetry FVC>=80% CSF Simoa + microvessel ddPCR + iPSC neurovascular-microglial tri-culture sign gate"),
        ],
        "verdict_box": {
            "pass_gate": "Living-patient CSF/plasma Simoa sST2 & free IL-33 (n>=80, explicitly stratified into verified normoxic [supine/upright FVC >= 80% PLUS normal overnight oximetry/capnography, PMID:41635251] non-NIV sALS vs nocturnal-hypoxic/NIV ALS to deconfound 3–20x pulmonary vascular/alveolar mechanical-strain & ventilator-associated sST2 induction, PMID:30562096, PMID:40402026) + ventilation-matched n>=25 sALS vs n>=20 Control isolated CNS microvessel/pericyte (PMID:41857656) sST2/ST2L ddPCR confirms pre-hypoxic sST2 decoy excess (resolving Secreted Decoy sST2 vs. Membrane ST2L) AND human iPSC neurovascular-microglial tri-culture + ALS CSF confirms pathogenic IL-33 sink vs compensatory BBB-tight-junction brake polarity (PMID:37117777), followed by primary low-dose intrathecal neurovascular-shuttled (CD98hc/SLC3A2 PMID:37598178/PMID:39979268 or monovalent TfR1 PMID:39141703) cytoplasmic sST2 3'-UTR siRNA (PMID:35654979) or uniform 2'-O-MOE Zone 1 Intron-8 PAS/DSE steric SSO (chr2:102346035-102346125(+); 0 <=1-mm/wobble #1 chr2:102346045-102346062(+) [Caution on 25bp-SS 2mm=1]; nuclear RNase H1 Intron-8 gapmers prohibited, Zone 2 Exon-8 5'SS chr2:102343400-102343435(+) excluded) — or backup intact-FcRn pH-dependent sST2 aa 324–328 SKECF sweeping biologic gated on Cys327 IP-MS thiol-adduct profiling & SLC3A2(-SKEDF) counter-screening — clearing CNS sST2 >=70% while sparing Treg ST2L and GTEx Lung (140.08 TPM).",
            "kill_gate": "Living-CSF sST2 elevation restricted to nocturnal-hypoxic/NIV ALS (flat in oximetry-verified normoxic sALS), microvessel/pericyte ddPCR showing protective ST2L rather than sST2 induction, human iPSC neurovascular-microglial tri-culture showing sST2 knockdown worsens IL-33-driven BBB tight-junction breakdown (compensatory brake inversion), Exon-8 5'SS / nascent pre-mRNA ST2L depletion, OR failure to engage capillary endothelium/pericytes (PMID:37188501).",
        },
        "related": ["S07", "C018", "C019"],
        "causal": {
            "callout_kind": "HAZARD",
            "nodes": [
                ("Gene-Level Neurovascular Surge", "Cortical endothelial IL1RL1 +3.11 (n=28: 21v7, p=0.00698, PMID:42551425) & 55-um Visium spots +3.76 (N=14/18 sections)"),
                ("Unresolved Isoform & BBB Sign", "Tests endothelial/pericyte (PMID:41857656) Intron-8 PAS sST2 decoy (ENST00000311734.6) vs ST2L & BBB brake sign"),
                ("Proposed Perivascular IL-33 Sink", "If pathogenic sST2 predominates (~400 pM Virchow-Robin [MODEL_PRIOR]; cf. AD PMID:37117777), sequesters IL-33 from ST2L+ Tregs"),
                ("IT Shuttled sST2 siRNA / Zone 1 PAS SSO", "IT CD98hc/TfR1-shuttled cytoplasmic sST2 siRNA or Zone 1 PAS 2'-MOE SSO (102346045-102346062(+)) spares Treg ST2L"),
            ],
            "trap_title": "NUCLEAR GAPMER, EXON-8 5'SS & CYS327 HAZARD — Co-Transcriptional ST2L Loss & Unpaired Thiol",
            "trap_desc": "Nuclear RNase H1 Intron-8 gapmers cleave nascent ST2L pre-mRNA before Exon 8->9 splicing, and Zone 2 Exon-8 5'SS masking (102343400-102343435(+)) depletes ST2L; in PDB 4KC3 all 10 D1-D3 cysteines form 5 disulfides, leaving Cys327 in 324-SKECF-328 as an odd unpaired thiol (plus 4/5 C-term match SLC3A2 -SKEDF), while sweeping requires intact pH-6.0 FcRn salvage.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "log2fc", "tone": "disease_gain", "lbl": "Zhang 55-um Visium Spots (N=14 donors / 18 sections, spot MAST)", "val": 3.761, "stat": "+3.761 log2FC", "p": "MAST FDR=1.85e-9", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_gain", "lbl": "Edinburgh Cortical Endo (n=28: 21v7 Ctrl, PMID:42551425)", "val": 3.107, "stat": "+3.107 log2CPM", "p": "p=0.00698", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "null_or_diluted", "lbl": "Pineda BA4 Vascular snRNA (n=31, PMID:38521060)", "val": 0.075, "stat": "+0.075 log2CPM", "p": "p=0.918 NS", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "null_or_diluted", "lbl": "NYGC Bulk Cortex ALS-Glia (N=67, GSE153960)", "val": 0.216, "stat": "+0.216 log2CPM", "p": "p=0.651 NS", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "null_or_diluted", "lbl": "Prudencio Bulk Frontal-Cereb (N=15 of 18, GSE67196)", "val": -0.322, "stat": "-0.322 log2FC", "p": "p=0.660 NS", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "80% RNA suppression / sweeping vs 5 nM pan-ST2 on Treg ST2L", "stat": "11.8–28.2% vs 0.32% ST2L", "p": "Pan-ST2 blocks ST2L", "tag": "MODEL_PRIOR"},
                {"lbl": "PDB 4KC3 (aa 21–317) disulfides & GENCODE v46 -SKECF scan", "stat": "4KC3 5 SS; Cys327 seq-deduced", "p": "1/89,484 (-SKECF)", "tag": "MEASURED"},
                {"lbl": "Trautwig 2025 CSF DIA (N=259, PMC12082929) LoQ check", "stat": "0 proteins detected", "p": "Needs Simoa", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 IL1RL1 Isoform Bifurcation: Zone 1 PAS Steric Window vs Zone 2 Exon-8 5'SS Exclusion",
            "caption": "Exons 1–8 encode shared D1–D3 (PDB 4KC3). 1-based GENCODE v46 sST2 (ENST00000311734.6) uses terminal Exon 8 + intron-8 polyA chr2:102343270-102346100(+) (canonical AATAAA at 102346074-102346079(+)), whereas ST2L (ENST00000233954.6) splices to Exons 9–11 (102351536-102352037(+)). Zone 1 (102346035-102346125(+); #1 102346045-102346062(+) has 0 mRNA/50bp-SS hits, boundary_dist_bp=40, Caution on 25bp-SS 2mm=1) spares Exon-8 5'SS (Zone 2 DO-NOT-MASK 102343400-102343435(+)); nuclear RNase H1 Intron-8 gapmers are prohibited.",
            "strand": "+", "chrom": "chr2", "win_lo": 102340000, "win_hi": 102352200,
            "zoom_lo": 102343200, "zoom_hi": 102346300,
            "exons": [
                {"lbl": "Exon 8 (D3)", "lo": 102343270, "hi": 102343415, "kind": "canon"},
                {"lbl": "Intron-8 sST2 Readthrough + PAS (Decoy)", "lo": 102343416, "hi": 102346100, "kind": "ce"},
                {"lbl": "Exon 9–11 (ST2L TM+TIR)", "lo": 102347945, "hi": 102352037, "kind": "skip"},
            ],
            "snps": [{"lbl": "rs1420101 sQTL (q=0.997)", "pos": 102341256}, {"lbl": "sST2 PAS (AATAAA)", "pos": 102346074}],
            "zoom_spans": [
                {"lbl": "Zone 1 PAS Steric #1 chr2:102346045-102346062(+)", "sub": "mRNA 0/0, 50bp-SS 0/0 (Caution: 25bp-SS 2mm=1)", "lo": 102346045, "hi": 102346062, "tone": "caution"},
                {"lbl": "Zone 2 DO-NOT-MASK Exon-8 5'SS (102343400-102343435(+))", "sub": "Blocks Ex8->9 (depletes ST2L!)", "lo": 102343400, "hi": 102343435, "tone": "hazard"},
            ],
        },
        "safety": [
            ("Het-pLoF Population Constraint", "LOW", "gnomAD v4.1 MANE pLI = 4.86e-7, LOEUF = 1.063 (20/27.4 LoF; Open Targets / legacy gene constraint LOEUF = 0.845, 32/50.9 — does not certify Treg ST2L blockade)"),
            ("Nuclear Gapmer Ban & Zone 2 Guard", "GATE", "Must resolve Secreted Decoy sST2 vs. Membrane ST2L first; nuclear RNase H1 Intron-8 gapmers & Zone 2 Exon-8 5'SS masking (102343400-102343435(+)) are banned to protect nascent ST2L"),
            ("Capillary Shuttle & Lung Sink", "GATE", "Mortberg 2023 (PMID:37188501) shows naked IT 2'-MOE misses brain capillaries; low-dose IT CD98hc/TfR1-shuttled cytoplasmic sST2 siRNA or Zone 1 PAS 2'-MOE SSO bypasses the 140.08 TPM GTEx Lung IV sink (PMID:37598178; PMID:39141703)"),
            ("Cys327 Thiol & SLC3A2 Counter-Screen", "GATE", "Backup intact-FcRn sweeping mAb on 324-SKECF-328 faces unpaired Cys327 thiol adducts (+119/+305 Da, dimers) & sole 4/5 human C-terminome match SLC3A2 (-SKEDF)"),
            ("Oximetry & BBB-Brake Sign Gate", "GATE", "Overnight oximetry/capnography FVC >= 80% CSF Simoa (PMID:41635251) + iPSC neurovascular-microglial tri-culture test pathogenic decoy vs compensatory BBB-brake sign"),
        ],
        "struct_note": "PDB 4KC3 (PMID:23980170, IL-33 bound to ST2 D1–D3, construct aa 19–321 / resolved coordinates aa 21–317): all 30 ST2 interface residues (224 heavy-atom contacts <4.0A; last IL-33 contact Arg313) are 100% shared between sST2 (328 aa) and ST2L (556 aa), and all 10 D1–D3 cysteines form 5 closed disulfides (SG–SG 2.03–2.05A), establishing by sequence deduction past resolved Glu317 that Cys327 inside sST2's unique 5-aa C-tail (324-SKECF-328; 320-GKS shared with ST2L 320-GKSL) is an odd 11th unpaired extracellular thiol (redox/adduct state in human ALS CSF unmeasured).",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "IL1RL1 (ENSG00000115602, Q01638) bifurcates via Intron-8 alternative polyadenylation into neuroprotective transmembrane ST2L (ENST00000233954.6) on meningeal/CNS FOXP3+ Tregs versus secreted decoy sST2 (ENST00000311734.6; contextualized by Alzheimer's disease CNS sST2 genetic/CRISPR/ASO-siRNA precedents in Jiang et al. 2022 PMID:37117777, HKUST patent US20240376452A1 claiming sST2 3'-UTR/rs1921622 RNA modulation in AD, selective-sST2 decoy prior art US20080003199A1 & WO2024246589A1, and Wong et al. 2026 PMID:42446992 [observing AD plasma sST2 beta=-1.716, P=0.008 in n=29 vs 430 with 0 CSF measurements, while requiring 10–30 uM trazodone for -35% protein / -15% mRNA in hCMEC/D3 cells — 23–160x above human Cu,plasma ~187–430 nM at the MND-SMART EALS-009 200 mg/d dose PMID:39307154], alongside mixed peripheral/fluid ALS cytokine reports: lower serum IL-33 / higher serum sST2 in Lin et al. 2012 PMID:22633272, null sALS serum and CSF sST2/IL-33 in Italiani et al. 2014 PMID:24884937, compartment-divergent findings in Pan et al. 2026 PMID:42698373 [plasma IL1RL1/ST2 case-status elevation ST5 q=0.00464 with null survival ST8/9 & null corrected plasma functional progression ST10, vs CSF IL1RL1 association with respiratory functional decline ST11/14], and female-restricted IL-33 delay / male null in SOD1-G93A ALS mice in Korhonen et al. 2019 PMID:30705990). Because zero CNS/isoform-selective sST2 interventions have been tested in ALS, current ALS CNS transcriptomic datasets measure gene-level IL1RL1 rather than isoform-resolved protein, and endothelial sST2 induction could represent either a pathogenic IL-33 sink or a compensatory neurovascular brake limiting excess perivascular IL-33 BBB permeability, C007 explicitly gates isoform identity, sex-stratified (female vs male) CSF/preclinical effects, archived MND-SMART CSF sST2 (<30% vs >=50%), and causal-vs-compensatory sign in human iPSC neurovascular-microglial tri-cultures exposed to ALS CSF."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Because neurovascular endothelial cells and pericytes (Jansson et al. 2026, PMID:41857656) comprise <2% of cortical nuclei, bulk cortical RNA-seq is flat (NYGC N=67 p=0.651; Prudencio N=15 of 18 paired frontal-cerebellar donors p=0.660) and Pineda BA4 pooled vascular snRNA-seq is flat (+0.075 log2CPM, p=0.918 across n=31 donors; PMID:38521060), whereas 55-um multicellular cervical anterior-horn MN-niche Visium spots (+3.761 log2FC, within-donor pseudoreplicated Seurat MAST spot FDR=1.85e-9 across N=14 donors / 18 sections, exploratory; Zhang et al. 2026 PMID:42135512) and UMI-pooled BA39/BA44/BA46 cortical endothelial nuclei (+3.107 log2CPM, Welch p=0.00698 across n=28 donors [21 non-C9 sALS vs 7 Ctrl] at >=10 nuclei; Petrescu et al. 2026 PMID:42551425, GSE290359 — verified via XIST/UTY counts on CGND-HRA-03640/03662 to be immune to the Nov-12-2026 GEO GSM title swap) show strong gene-level IL1RL1 induction, while untargeted CSF DIA missed IL1RL1 below LOQ (0 proteins detected across N=259, PMC12082929). Because pulmonary vascular/alveolar mechanical strain and invasive ventilation spike circulating sST2 3–20x (PMID:30562096; PMID:40402026) and FVC >= 80% does not exclude nocturnal hypoventilation in mild ALS (contextualized by ALS sleep-study precedent PMID:41635251), validation requires overnight-oximetry/capnography-verified normoxic CSF Simoa plus ventilation-matched microvessel/pericyte sST2/ST2L ddPCR (n>=25/20)."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "PDB 4KC3 (resolved aa 21–317, PMID:23980170) proves systemic pan-ST2 antibodies (e.g., astegolimab, IDG Tbio target; Phase 2b NCT05037929 & Phase 3 ARNASA NCT05595642 missed p=0.068 in COPD, Papi et al. 2026 PMID:42150581; cf. sST2-selective decoy prior art US20080003199A1 & WO2024246589A1 and HKUST AD sST2 3'-UTR RNA patent US20240376452A1) ablate Treg ST2L signaling, while NHP/mouse ASO atlases (Mortberg et al. 2023, PMID:37188501) show brain capillary endothelial cells resist unconjugated intrathecal 2'-MOE ASOs — and systemic IV conjugates face a 140.08 TPM GTEx Lung sink. Structural cysteine auditing of PDB 4KC3 further reveals that all 10 D1–D3 ectodomain cysteines form 5 closed disulfide bridges (2.03–2.05A), establishing by sequence deduction beyond resolved Glu317 that Cys327 inside sST2's 5-aa neo-epitope (324-SKECF-328) is an odd 11th unpaired thiol susceptible to CSF/plasma S-cysteinylation (+119 Da), S-glutathionylation (+305 Da), and homodimerization (empirical thiol state in ALS CSF unmeasured), while GENCODE v46 C-terminome scanning (89,484 protein-coding transcripts) identifies endothelial CD98hc/SLC3A2 (-SKEDF) as the sole 4/5 human C-terminal homolog.\n\nAccordingly, contingent on confirming pathogenic sST2 excess, C007 promotes neurovascular RNA suppression over the 5-aa biologic: low-dose intrathecal neurovascular-shuttled (contextual BBB-shuttle precedents: CD98hc/SLC3A2 PMID:37598178/PMID:39979268 or monovalent TfR1 PMID:39141703) cytoplasmic Ago2/RISC siRNA (contextual CNS C16-siRNA precedent PMID:35654979; untested on endothelial sST2) targeting exported mature sST2 3'-UTR RNA (chr2:102343416-102346100(+)) OR uniform 2'-O-MOE steric PAS/DSE blockade inside Zone 1 (chr2:102346035-102346125(+); 0 <=1-mm/wobble #1 chr2:102346045-102346062(+), boundary_dist_bp=40, Caution on 25bp-SS 2mm=1 upstream of AATAAA 102346074-102346079(+)), strictly prohibiting nuclear RNase H1 Intron-8 gapmers (co-transcriptional nascent ST2L pre-mRNA cleavage) and Zone 2 Exon-8 5'SS masking (chr2:102343400-102343435(+)), while retaining an intact-FcRn pH-dependent 324-SKECF-328 sweeping mAb (catalytic sweeping requires intact pH-6.0 FcRn salvage) strictly as a secondary backup gated on Cys327 IP-MS adduct profiling and SLC3A2 counter-screening."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Gated first on paired living-patient CSF Simoa soluble sST2 & free IL-33 comparing oximetry/capnography-verified normoxic (supine/upright FVC >= 80%, non-NIV) sporadic ALS vs nocturnal-hypoxic/NIV ALS, isolated microvessel sST2/ST2L ddPCR, and human iPSC neurovascular-microglial tri-culture BBB-brake sign testing alongside BioVendor-bridged CSF pNfH (#2 S07) before lead generation."),
        ],
    },
}
