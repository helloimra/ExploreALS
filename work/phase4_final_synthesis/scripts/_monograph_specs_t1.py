"""Translational Monograph Standard v3.1 (5Rs + Open Targets + FAIR/W3C PROV) — Part 1: TIER_1 (#1 S06, #2 C006, #3 S07)."""
from __future__ import annotations

MONOGRAPH_SPECS_T1: dict[str, dict] = {
    "S06": {
        "subtitle": "Non-Covalent Allosteric ARM–TIR Octamer T-Lock Inhibitor (ASHA-624 Class; Non-BEXi NADase Silencing)",
        "ident": [
            ("Gene / HGNC", "SARM1 (HGNC:17074)"), ("MANE", "ENST00000379883 (+)"), ("UniProt", "Q6SZW1 (724 aa)"),
            ("3D Cryo-EM", "PDB 7DJT (Benchmark) · 9TZY (BEXi)"), ("ALS Trials", "NCT07883590 (NYR) · NCT07369076"),
            ("IDG TDL · Modality", "Tchem · Non-Covalent Oral T-Lock"),
        ],
        "grades": [
            ("Human Genetics & Trials", "Rare ALS GoF ARM variants; LY3873862 NCT07883590 (Ph1 NYR) & NB-4746 NCT07369076"),
            ("Small-N iPSC & 3D Cryo-EM", "Spillman iPSC-N +0.675 (n=3v3, p=0.027, PXD083082); PDB 7DJT vs 9TZY"),
            ("Biophysical MWC Prior", "[MODEL_PRIOR] 8-protomer MWC BEXi washout spike vs T-lock sensitivity curve"),
        ],
        "verdict_box": {
            "pass_gate": "Monotonic NADase & axonal cADPR suppression from 0.01x–10x IC50 AND across 48–72 h simulated oral CNS washout (5x -> 0.03x IC50, modeling missed doses in bulbar dysphagia; zero >1.05x baseline spike) in microfluidic WT sALS motor axons (with isogenic SARM1 p.L223P ARM-GoF negative-control line, testing non-covalent T-lock head-to-head against Disarm-lineage BEXi LY3873862 and reversible orthosteric NB-4746) + human unbound CSF Kpuu >= 0.30 (Ctrough,u >= IC80), zero washout CSF pNfH/plasma NfL spike, and exploratory L1CAM/ATP1A3+ NDEV cADPR:NAD+ reduction (given mouse Cd38-/- evidence of non-neuronal ecto-CD38 cADPR background, PMID:32087251; PMID:16750163).",
            "kill_gate": "Any bell-shaped sub-IC50 axonal cADPR or washout CSF pNfH/plasma NfL activation spike during 48–72 h oral washout (0.05x–0.30x Kd) OR unbound human CNS Ctrough,u < IC80.",
        },
        "related": ["C002", "C006", "DN-01"],
        "causal": {
            "callout_kind": "HAZARD",
            "nodes": [
                ("Distal Axonal NMNAT2 Depletion", "Elevates axonal NMN/NAD+ ratio (co-varies with STMN2 in BA4 Exc r=+0.928, PMID:38518782; parallel to Stmn2 KO PMID:35767949)"),
                ("SARM1 ARM Autoinhibition Breaks", "W103–R376 ARM lock opens (PDB 7ANW -> 7NAL); octamer shifts T -> R state (L_eff = 8 [MODEL_PRIOR])"),
                ("2-Stranded TIR NADase Filament", "Catastrophic NAD+ depletion, cADPR surge & Wallerian motor axonolysis"),
                ("Non-Covalent ARM–TIR T-Lock (S06)", "ASHA-624-class glue locks inactive octamer (PDB 7DJT Cys311 benchmark): zero trough agonism"),
            ],
            "trap_title": "REJECTED CHEMOTYPE HAZARD — Orthosteric Base-Exchange (BEXi / 1AD)",
            "trap_desc": "Lundback et al. 2026 (PMID:42156967, PDB 9TZY) and PMID:42380237 prove 1AD bridges 3 TIR chains (33 res <=5A), nucleating active filaments & causing ~45x (WT) / ~5x (ALS) modeled NADase spikes at sub-IC50 washout troughs.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "log2fc", "tone": "disease_gain", "lbl": "Spillman C9-FTD iPSC-N DIA (n=3 vs 3, PXD083082)", "val": 0.675, "stat": "+0.675 log2FC", "p": "p=0.0268", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Frontal GC+comp end-stage dropout (n=103, GSE153960)", "val": -0.307, "stat": "-0.307 log2FC", "p": "p=1.24e-6", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Pineda BA4_Exc STMN2–NMNAT2 co-variation (n=32, PMID:38518782)", "stat": "Pearson r = +0.928", "p": "p=1.95e-14", "tag": "MEASURED"},
                {"lbl": "PDB 9TZY BEXi 3-chain TIR filament bridge (PMID:42156967)", "stat": "33 contacts <=5A", "p": "2.94A EM", "tag": "MEASURED"},
                {"lbl": "PDB 7DJT Cys311 octamer benchmark vs apo 7ANW (PMID:33944777)", "stat": "1.33A C-alpha RMSD", "p": "2.80A EM", "tag": "MEASURED"},
                {"lbl": "MWC T-Lock @ 0.30x Kd (ALS axon, L_eff=8)", "stat": "~-82% NADase (0 spike)", "p": "IC90 ~0.45x Kd", "tag": "MODEL_PRIOR"},
                {"lbl": "MWC BEXi @ 0.14x / 0.28x Kd washout trough", "stat": "~5x ALS / ~45x WT", "p": "Agonist spike!", "tag": "MODEL_PRIOR"},
            ],
        },
        "sig_fig": {
            "kind": "mwc_sarm1",
            "title": "Modeled 8-Protomer MWC Partition: BEXi Washout Spike vs Non-Covalent T-Lock Sensitivity Scenario",
            "caption": "[MODEL_PRIOR] Illustrative 8-protomer MWC scenario anchored to [MEASURED] PDB 9TZY (BEXi filament) & PDB 7DJT (inactive octamer benchmark). While Stmn2 loss acts in parallel to Sarm1 in mice (Krus et al. 2022, PMID:35767949), an illustrative L_eff shift (8 -> 65) models ~2–7x catastrophe-floor dose-sparing alongside empirical Bliss/Loewe additivity testing.",
        },
        "safety": [
            ("Het-pLoF Population Constraint", "LOW", "gnomAD v4 pLI = 2.75e-19, LOEUF = 1.143 (obs/exp 60/65.1 — no strong het-pLoF depletion; distinct from biallelic KO phenotyping)"),
            ("Dividing-Line & Mouse KO Context", "LOW", "Non-essential in dividing cancer lines (DepMap); Sarm1-/- mice viable & axon-protected (PMID:35767949; chronic human CNS tox still required)"),
            ("Non-Covalent T-Lock Selectivity", "MITIGATED", "ASHA-624-class ARM–TIR glue (Cys311 PDB 7DJT benchmark only) avoids chronic thiol reactivity & ~5–45x trough spikes"),
            ("Unbound CNS PK & CD38-Aware PD", "GATE", "Decouples LY3873862 (Ph1 Not Yet Recruiting) vs NB-4746; gates CSF Kpuu >= 0.30, Ctrough,u >= IC80, washout pNfH/NfL & NDEV cADPR"),
            ("Rare ARM-Broken GoF Alleles (<1%)", "MITIGATED", "Constitutive ARM GoF alleles (L223P/V184G) bypass ARM locks -> genotype screen or SARM1 KD ASO backup"),
        ],
        "struct_note": "Staged cryo-EM: PDB 9TZY (2.94A, PMID:42156967: 1AD BEXi bridges chains A:18, B:13, D:2) vs structural octamer benchmark PDB 7DJT (2.80A, PMID:33944777: Cys311-dHNN ARM span 40.48A, 1.33A RMSD to autoinhibited PDB 7ANW vs 2.37A to NMN-activated PDB 7NAL).",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "Wallerian motor axonolysis is triggered post-translationally when distal axonal NMNAT2 depletion elevates the NMN/NAD+ ratio and unlocks SARM1's autoinhibitory ARM ring — a distal execution step invisible to cortical soma bulk RNA-seq. Human ALS rare-variant cohorts enrich for constitutively active SARM1 ARM gain-of-function alleles, while gnomAD v4 shows no strong population depletion of heterozygous predicted loss-of-function variation (ENSG00000004139, LOEUF = 1.143; distinct from clinical biallelic knockout phenotyping)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Small-sample C9orf72-FTD/ALS iPSC neurons show elevated SARM1 protein (+0.675 log2FC, p=0.0268, n=3 vs 3; Spillman et al. 2026, PXD083082), whereas end-stage NYGC frontal bulk RNA (-0.307 log2FC, p=1.24e-6; GSE153960) reflects terminal projection-neuron dropout. Although STMN2 and NMNAT2 mRNA co-vary across BA4 excitatory neurons (r=+0.9284, p=1.95e-14; Pineda et al. 2024, PMID:38518782), Stmn2 depletion did not lower axonal NMNAT2 or activate SARM1 in mouse motor axons (Krus et al. 2022, PMID:35767949), positioning SARM1 and STMN2 primarily as parallel axonal maintenance pathways."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "Cryo-EM structure PDB 9TZY (Lundback et al. 2026, PMID:42156967) and 122-scaffold profiling (PMID:42380237) prove orthosteric base-exchange (BEXi) prodrugs bridge three TIR chains and paradoxically activate SARM1 below IC50. ExploreALS prioritizes non-covalent intramolecular ARM–TIR octamer T-locks (ASHA-624 class; positioning covalent Cys311 electrophiles in PDB 7DJT, PMID:33944777 strictly as structural benchmarks), testing them head-to-head against Disarm-lineage BEXi prodrug Lilly LY3873862 (NCT07883590, Phase 1 Not Yet Recruiting; PMID:33406435) and reversible orthosteric Nura Bio NB-4746 (NCT07369076, undisclosed structure) across 48–72 h simulated oral washout curves (5x -> 0.03x IC50).\n\nBecause mouse Cd38-/- and axonal studies indicate non-neuronal ecto-CD38 dominates bulk tissue/fluid cADPR (PMID:32087251; PMID:16750163; unquantified in human ALS lumbar CSF), Phase 1b PD anchors on unbound CSF Ctrough,u >= IC80 (Kpuu >= 0.30), zero washout CSF pNfH/plasma NfL spike, and exploratory L1CAM/ATP1A3+ neuron-derived EV cADPR:NAD+."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Because Sarm1 deletion does not rescue Stmn2-null motor neuropathy in double-mutant mice (Krus et al. 2022, PMID:35767949; Lopez-Erauskin et al. 2024, PMID:37996528), oral non-covalent SARM1 T-lock acts as a parallel distal axonal execution backstop alongside intrathecal splice rescue (C006 + C002 + genotype-stratified C001), gated on empirical Bliss/Loewe additivity testing in axotomized human sALS iPSC-MNs (with ~2–7x MWC catastrophe-floor sparing [MODEL_PRIOR] treated strictly as an unvalidated sensitivity scenario)."),
        ],
    },
    "C006": {
        "subtitle": "Intrathecal Steric-Blocking 2'-MOE SSO Restoring KCNQ2 Canonical Exon-5 Inclusion in Kv7.2 Channels",
        "ident": [
            ("Gene / HGNC", "KCNQ2 (HGNC:6295)"), ("MANE", "ENST00000359125 (-)"), ("UniProt", "O43526 (Kv7.2, 872 aa)"),
            ("3D Cryo-EM", "PDB 7CR2 (Kv7.2+Retigabine)"), ("Promoted SSO", "#3 chr20:63442302-63442319(-)"),
            ("IDG TDL · Modality", "Tclin (WT Kv7.2 Pore) · Intrathecal 2'-MOE SSO"),
        ],
        "grades": [
            ("Human Pathology & Excitability", "NYGC cord p=2.84e-4 (GSE153960); Ezogabine Ph2 NCT02450552 SICI p=0.009"),
            ("i3Neuron Splicing & 3D Cryo-EM", "Brown dPSI=+0.214 (PMID:35197628); Joseph ER trap (PMID:41174170); PDB 7CR2 Trp236"),
            ("GENCODE v46 Scan Prior", "Promoted #3 Intron-5 Conserved Anchor (sp=0/0/0, UG=1, 0/18 Splice AVI)"),
        ],
        "verdict_box": {
            "pass_gate": "Stage 1 single-entity dense (>=50-oligo 1-nt-stepped 18–22 nt) Intron-4/Exon-5/Intron-5 exon-inclusion micro-walk across BOTH graded (30%/60%/90%) TDP-43-CRISPRi human iPSC-MNs AND TDP-43-intact WT human neurons (PV+ cortical interneurons [DEE7], oculomotor MNs, and primary human DRGs) anchored on off-target-clean #3 (UG=1, modeled Tm ~53C, unverified putative ISS) vs cis-eviction-gated #1 (UG=8) suppresses Exon-5 skip >=60% without wrong-sign ISE exacerbation, WT TDP-43 cis-eviction, or Ca2+/Mg2+-formulated Ca2+-oscillation/TLR9 neurotox, establishes NHP cervical (C3–C5 phrenic) & BA4 Betz splice EC80 rescue + human C005 TMS SICI/SDTC TE, and passes unvalidated 24–48 mg Stage 2 genotype-stratified 2-plex vs 3-plex uptake/DRG/Ca2+ safety testing.",
            "kill_gate": "Zero Exon-5 inclusion gain or wrong-sign ISE exacerbation across dense Intron-4/Intron-5 micro-walk (#3 0/18 Splicing AVI acts as an ISE rather than ISS), steric cis-eviction of endogenous WT TDP-43 inducing KCNQ2-DeltaE5 in healthy TDP-43-intact neurons/PV+ interneurons/DRGs on #1, >30% 2-plex/3-plex endosomal-escape loss, OR acute PS-oligo Ca2+-oscillation suppression.",
        },
        "related": ["C005", "C001", "C002", "C003", "S06"],
        "causal": {
            "callout_kind": "RATIONALE",
            "nodes": [
                ("Nuclear TDP-43 Depletion", "Loss of intronic UG-repeat splicing control at KCNQ2 Exon 5 (PMID:35197628)"),
                ("In-Frame Exon-5 Skip (126 bp, mod3=0)", "Excises 42 aa (Glu231–Leu272: S5–pore–S6 & Trp236 pocket) without NMD"),
                ("ER Retention & Dominant-Negative Trap", "KCNQ2-DeltaE5 accumulates in ER & sequesters WT Kv7.2 (~62% homomer upper bound [MODEL_PRIOR], PMID:41174170)"),
                ("Putative Intron-5 ISS Walk (#3 Anchor)", "chr20:63442302-63442319(-) (UG=1, 0/18 Splice AVI) anchors dense exon-inclusion walk"),
            ],
            "trap_title": "MODALITY RATIONALE — Why Kv7 Openers Alone (C005 / C003) Face a Surface-Density Ceiling",
            "trap_desc": "PDB 7CR2 (Li et al. 2021, PMID:33097810) proves retigabine/ezogabine requires a 2.97A H-bond to Trp236 inside Exon 5. While residual WT Kv7.2/Kv7.3 heteromers still respond acutely (ezogabine NCT02450552 SICI p=0.009), KCNQ2-DeltaE5 ER retention (PMID:41174170) and Trp236 deletion cap opener efficacy.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "dpsi", "tone": "disease_gain", "lbl": "Brown i3Neuron Exon-5 skip (PMID:35197628)", "val": 0.214, "stat": "dPSI = +0.214", "p": "FDR=4.15e-24", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "NYGC Cervical Cord GC+cell OLS (n=87, GSE153960)", "val": -0.465, "ci": [-0.705, -0.225], "stat": "-0.465 log2FC", "p": "p=2.84e-4", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Pineda BA4_Exc GC-adj OLS (n=32, PMID:38518782)", "val": -0.302, "stat": "-0.302 log2FC", "p": "p=0.0357", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "null_or_diluted", "lbl": "Spillman C9-FTD P2 Synaptosome DIA (n=19, PXD083082)", "val": 0.247, "stat": "+0.247 log2FC", "p": "p=0.527 NS", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Idealized homomer poisoning upper bound @ dPSI=0.214", "stat": "~62% (1-(1-p)^4)", "p": "KCNQ3/ER mod.", "tag": "MODEL_PRIOR"},
                {"lbl": "PDB 7CR2 Exon-5 pore & retigabine Trp236 contacts", "stat": "26 res <=5A · 2.97A", "p": "42/42 aa", "tag": "MEASURED"},
            ],
        },
        "sig_fig": {
            "kind": "locus_sso",
            "title": "GRCh38 KCNQ2 Exon-5 Skipping Locus & Steric SSO Walk (chr20, - strand)",
            "caption": "Coordinate-only 1-based closed GRCh38 search-window map (0 chemically modified synthesis-ready ASO sequences). #2 (Intron-4 UG5) was demoted on PTCH1 (pLI=1.0); #3 (chr20:63442302-63442319(-), UG=1, 0/18 Splicing AVI = Cactus/DNase conservation) is an unverified putative ISS anchoring a >=50-oligo exon-inclusion micro-walk.",
            "strand": "-", "chrom": "chr20", "win_lo": 63439550, "win_hi": 63444900,
            "zoom_lo": 63442280, "zoom_hi": 63442640,
            "exons": [
                {"lbl": "Exon 6", "lo": 63439598, "hi": 63439708, "kind": "canon"},
                {"lbl": "Exon 5 (Skipped 126bp / Trp236)", "lo": 63442406, "hi": 63442531, "kind": "skip"},
                {"lbl": "Exon 4", "lo": 63444659, "hi": 63444834, "kind": "canon"},
            ],
            "snps": [{"lbl": "3'SS AVI=54.8", "pos": 63442531}, {"lbl": "5'SS AVI=33.7", "pos": 63442405}],
        },
        "safety": [
            ("Restoration on Constrained Gene", "MITIGATED", "gnomAD v4 pLI = 1.000, LOEUF = 0.258, mis_z = 5.61 (14/84.8 LoF; SSO restores WT Exon 5)"),
            ("Dividing-Line Context (DepMap)", "GATE", "Mean Chronos = +0.041 in dividing tumor lines (which lack M-current; human het LoF causes DEE7 epilepsy)"),
            ("CNS-Restricted Intrathecal Route", "MITIGATED", "IT 2'-MOE bypasses systemic bladder Kv7 urinary retention & peripheral liabilities (CHEMBL41355)"),
            ("GENCODE v46 Reference Hybridization", "GATE", "Lead #3 CAUTION (sp=0/0/0; deep intronic PPA2 dSS=3,142 bp); empirical PS protein-binding/DRG screens required"),
            ("WT TDP-43 Cis-Eviction Guard", "GATE", "Lead #3 (UG=1) avoids #1 (UG=8) steric cis-eviction of ~1–10 uM WT TDP-43 (PMID:21358643) in PV+ interneurons & DRGs"),
        ],
        "struct_note": "PDB 7CR2 (Kv7.2 homotetramer + retigabine, PMID:33097810): all 42 Exon-5 residues (Glu231–Leu272) resolved, forming 26 inter-subunit contacts <=5A and the essential 2.97A Trp236 H-bond to retigabine.",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "Nuclear TDP-43 loss triggers in-frame skipping of KCNQ2 Exon 5 (126 bp, mod3=0), excising 42 pore-forming residues without triggering nonsense-mediated decay. Joseph et al. 2025 (PMID:41174170) demonstrated that KCNQ2-DeltaE5 accumulates in the neuronal endoplasmic reticulum (ER), impairs plasma-membrane trafficking, and exerts dominant-negative conductance/sequestration effects on WT Kv7.2 (an idealized equal-assembly homomer model 1-(1-p)^4 yields ~62% affected channels at dPSI=0.214 [MODEL_PRIOR], modulated in vivo by ER retention and KCNQ3/Kv7.3 heterotetramerization)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Brown Ribo-seq (padj=0.983; PMID:35197628) and Joseph et al. 2025 immunoblots (PMID:41174170) confirm NMD-escaping translation with soma ER retention and ubiquitin-positive spinal cord accumulations (whereas C9-FTD cortical P2 synaptosome DIA +0.247 log2FC, p=0.527, n=19 in Spillman et al. 2026 PXD083082 reflects sparse cortical TDP-43 pathology plus co-fractionated subsynaptic ER across non-Exon-5 peptides). Junction skipping replicates across i3Neurons (dPSI=+0.214, FDR=4.15e-24; Ma et al. 2022 PMID:35197626), NYGC cervical cord (-0.465, p=2.84e-4; GSE153960), and BA4 excitatory snRNA-seq (-0.302, p=0.0357; PMID:38518782)."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "Whereas clinical trials test small-molecule Kv7 openers (ezogabine NCT02450552; QRL-101 NCT06714396) that remain active on residual WT Kv7.2/Kv7.3 channels (SICI p=0.009) but face a ceiling from KCNQ2-DeltaE5 ER retention and Trp236 deletion (PDB 7CR2), zero clinical splice-switching ASO trials target KCNQ2 (note Joseph et al.'s tool ASO validates target biology, not ExploreALS's un-synthesized windows). Promoting canonical Exon-5 inclusion requires finding a true intronic splicing silencer (ISS): GENCODE v46 scanning promoted #3 (chr20:63442302-63442319(-), UG=1, modeled Tm ~53C [MODEL_PRIOR]; DNA-variant AVI=20.75 reflects 0/18 splicing tracks and does not certify steric ASO potency).\n\nBackup #1 (Intron-4 UG=8) risks steric cis-eviction of ~1–10 uM WT TDP-43 (PMID:21358643) in healthy TDP-43-intact PV+ interneurons, oculomotor MNs, and DRGs, mandating a >=50-oligo 1-nt walk across graded TDP-43-CRISPRi iPSC-MNs and WT neurons/DRGs with Ca2+/Mg2+-formulated Ca2+-oscillation/TLR9 counter-screening."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Deploys a 3-layer per-target PK/TE/PD hierarchy: (1) strand-specific CSF PK bridged to Stage 1 NHP cervical phrenic (C3–C5) & BA4 Betz splice-rescue EC80 curves; (2) direct target-specific human neurophysiology via threshold-tracking cortical TMS SICI (<=5.5 ms, calibrated by ezogabine NCT02450552) + median-nerve axonal SDTC fallback (APB CMAP >=1.0 mV) + L1CAM+/ATP1A3+ NDEV pre-amplified dPCR (since unfractionated CSF EVs sit at late-cycle RT-qPCR Cq>35 / <3–10 copies/mL ddPCR LOQ, PMID:38158550); and (3) >=16–24 wk post-loading CSF pNfH/NfL downstream injury PD.\n\nStage 2 evaluates genotype-stratified 2-plex vs 3-plex across rs12973192/rs12608932 genotypes as unvalidated 24–48 mg development scenarios (single-agent DEVOTE 50 mg nusinersen PMID:41634391 does not establish multiplex safety across distinct sequences) under 21 CFR 300.50."),
        ],
    },
    "S07": {
        "subtitle": "Biomarker-Gated Low-Dose Subcutaneous Aldesleukin (IL-2) in Calibrated Low/Moderate CSF pNfH ALS",
        "ident": [
            ("Drug / ChEMBL", "Aldesleukin (CHEMBL1201438)"), ("Receptor", "IL2RA/B/G (ENSG00000134460)"),
            ("Phase 2b RCT", "MIROCALS NCT03039673 (N=220)"), ("Lancet 2025", "PMID:40354799 (BioVendor ELISA)"),
            ("Responder Stratum", "BioVendor pNfH 750–3,700 pg/mL (n=154)"), ("IDG TDL · Modality", "Tclin · Low-Dose SC Biologic"),
        ],
        "grades": [
            ("Human Phase 2b RCT", "MIROCALS adj Cox HR=0.32 (0.14–0.73, p=0.007); unadj ITT HR=0.81 (p=0.33); 750–3,700 HR=0.52"),
            ("Living CSF MS Discordance", "Trautwig 2025 MS NEFL vs NEFH r=0.278 (n=77 DIA / n=51 overlapping TMT; uncalibrated to ELISA)"),
            ("Event-Driven Sizing Prior", "[MODEL_PRIOR] Schoenfeld 247 deaths @ HR=0.70 (N~650–750 over 36–42 mo variable follow-up)"),
        ],
        "verdict_box": {
            "pass_gate": "Stage-0 paired analytical bridging from MIROCALS BioVendor ELISA CSF pNfH to automated CLIA immunoassays (Ella/Euroimmun/Simoa, CV <10% at 3,700 pg/mL) + paired NfL vs pNfH immunoassay calibration on banked ALS CSF, followed by an event-driven randomized Phase 3 (247 deaths @ conservative HR=0.70 [MODEL_PRIOR], requiring N~650–750 across 36–42 mo variable follow-up or N~850–1,050 at 24 mo, <5% censoring) in calibrated CSF pNfH <=3,700 pg/mL achieving OS HR <=0.70 (p<0.05) with sustained Treg TSDR stability.",
            "kill_gate": "Null overall survival in prospectively gated low/moderate CSF pNfH (<=3,700 pg/mL) Phase 3 cohort, failure of Stage-0 BioVendor-to-CLIA pNfH analytical bridging, OR collapse of ex vivo Treg suppressive durability via FOXP3 TSDR methylation / CD56bright NK cellular sink expansion.",
        },
        "related": ["C007", "C019", "C018"],
        "causal": {
            "callout_kind": "HAZARD",
            "nodes": [
                ("Calibrated Baseline CSF pNfH", "MIROCALS BioVendor ELISA: 750–3,700 pg/mL (n=154) + <750 LLOQ (n=20, 0 deaths) of N=220"),
                ("Low-Dose SC IL-2 (2 MIU x5d q4w)", "Selectively engages 10 pM trimeric CD25/CD122/CD132 on FOXP3+ Tregs"),
                ("Sustained Treg Expansion & CCL2 Drop", "Suppresses peripheral & perivascular Th1/microglial neurotoxic cascade [MEASURED]"),
                ("Adjusted & Stratum Survival Signal", "Adj Cox HR=0.32 (0.14–0.73, p=0.007); 750–3,700 stratum HR=0.52 (0.30–0.89, p=0.016)"),
            ],
            "trap_title": "BIOANALYTICAL CAUTION — BioVendor ELISA Bridging & MS NEFH vs Clinical pNfH Discordance",
            "trap_desc": "MIROCALS used BioVendor ELISA: >3,700 pg/mL (n=46) was non-significantly futile (HR=1.37, 95% CI 0.68–2.75, p=0.38). Trautwig 2025 MS NEFL vs NEFH correlates weakly (r=0.278; DIA dynamic range blunted, uncalibrated to ELISA), motivating paired immunoassay calibration before substituting NfL.",
        },
        "ev_matrix": {
            "tracks": [
                {"kind": "hr", "tone": "clinical_benefit", "lbl": "MIROCALS BioVendor pNfH 750–3,700 (n=154, NCT03039673)", "val": 0.52, "ci": [0.30, 0.89], "stat": "HR = 0.52 (-48%)", "p": "p=0.016", "tag": "MEASURED"},
                {"kind": "hr", "tone": "clinical_benefit", "lbl": "MIROCALS SAP Covariate-Adj Cox (N=220, PMID:40354799)", "val": 0.32, "ci": [0.14, 0.73], "stat": "HR = 0.32 (-68%)", "p": "p=0.007", "tag": "MEASURED"},
                {"kind": "hr", "tone": "null_or_diluted", "lbl": "MIROCALS Unadjusted ITT (N=220, NCT03039673)", "val": 0.81, "ci": [0.54, 1.22], "stat": "HR = 0.81 (null)", "p": "p=0.33 NS", "tag": "MEASURED"},
                {"kind": "hr", "tone": "null_or_diluted", "lbl": "MIROCALS High pNfH >3,700 pg/mL (n=46, wide CI)", "val": 1.37, "ci": [0.68, 2.75], "stat": "HR = 1.37 (futile)", "p": "p=0.38 NS", "tag": "MEASURED"},
                {"kind": "log2fc", "tone": "disease_loss", "lbl": "Spillman C9-FTD Synaptosome NEFH (n=20, PXD083082)", "val": -0.895, "stat": "-0.895 log2FC", "p": "p=0.0111", "tag": "MEASURED"},
            ],
            "callouts": [
                {"lbl": "Trautwig 2025 MS NEFL vs NEFH (n=77 DIA; 51 overlap TMT)", "stat": "r=0.278 (MS uncal.)", "p": "p=0.0144", "tag": "MEASURED"},
                {"lbl": "Event-driven Phase 3 Schoenfeld @ HR=0.70 (36–42 mo)", "stat": "247 deaths (N~650–750)", "p": "80% pwr (138@0.62)", "tag": "MODEL_PRIOR"},
            ],
        },
        "sig_fig": {
            "kind": "il2_strat",
            "title": "MIROCALS 21-Month Survival by BioVendor CSF pNfH Stratum & Trautwig MS NEFH/NEFL Discordance",
            "caption": "Left: Published Lancet 2025 (Bensimon et al., PMID:40354799) BioVendor ELISA results (750–3,700 pg/mL n=154 HR=0.52; <750 pg/mL LLOQ n=20 had 100% 21-mo survival; >3,700 n=46 HR=1.37 NS). Right: Trautwig 2025 tryptic MS NEFH vs NEFL (n=77 DIA; n=51 overlapping Emory TMT; uncalibrated to clinical pNfH ELISA).",
        },
        "safety": [
            ("Low-Dose vs Oncology Exposure Margin", "LOW", "2 MIU SC is >20x below oncology capillary-leak doses; tolerated over 18 mo in NCT03039673"),
            ("Treg TSDR & Cellular Sink Durability", "GATE", "Tracks ex vivo Treg suppression, FOXP3 TSDR demethylation (PMID:17694575), CD56bright NK/eosinophil sink & monomeric sCD25 (Kd ~10–30 nM vs 10 pM Treg, PMID:22343569)"),
            ("High-pNfH Non-Responder / Futility Gate", "MITIGATED", "Prospective exclusion of calibrated CSF pNfH >3,700 pg/mL avoids non-responsive HR=1.37 (0.68–2.75) stratum"),
            ("BioVendor-to-CLIA pNfH & NfL Bridging", "GATE", "Stage-0 paired BioVendor ELISA vs Ella/Euroimmun/Simoa pNfH & NfL calibration on banked ALS CSF"),
            ("JAK1 Antagonism Co-Dosing Check", "MITIGATED", "Never co-dose simultaneously with JAK1/3 inhibitors (CHEMBL2105759 blocks IL-2Rbeta/JAK1)"),
        ],
        "struct_note": "Recombinant human IL-2 biologic (CHEMBL1201438, UniProt P60568) engaging trimeric IL-2R (CD25/CD122/CD132); pairs mechanistically with C007 (preserving neurovascular IL-33 -> ST2L+ Treg homoeostasis).",
        "sections": [
            ("Right Target — Causal Disease Biology & Genetic Anchor", "Regulatory FOXP3+ T-cell dysfunction accelerates peripheral and perivascular neuroinflammation in human ALS. In randomized Phase 2b MIROCALS (N=220; Bensimon et al. 2025, PMID:40354799, NCT03039673), low-dose subcutaneous aldesleukin (CHEMBL1201438) expanded CD4+FOXP3+ Tregs and lowered plasma CCL2; the unadjusted primary log-rank analysis was non-significant (HR=0.81, 95% CI 0.54–1.22, p=0.33), whereas the SAP-prespecified covariate-adjusted Cox model including continuous log(BioVendor ELISA CSF pNfH) x treatment interaction was positive (HR=0.32, 95% CI 0.14–0.73, p=0.007), operationalized into a 48% mortality hazard reduction in the 750–3,700 pg/mL stratum (n=154, HR=0.52, p=0.016; <750 pg/mL LLOQ n=20 had 0 deaths; >3,700 pg/mL n=46 showed non-significant futility HR=1.37, 95% CI 0.68–2.75, p=0.38)."),
            ("Right Tissue — Multi-Omic Human Pathology & Assay Nuance", "Re-analyzing paired living symptomatic ALS CSF in Trautwig et al. 2025 (PMC12082929, PMID:40375307: n=77 4-center DIA; technical cross-platform check in n=51 overlapping Emory TMT donors) showed weak correlation between tryptic mass-spectrometry NEFL and NEFH peptide abundance (r=0.2779, p=0.0144, with 60–75% top-quintile MS NEFH discordance). Because tryptic MS abundance is not calibrated to phosphorylated pNfH BioVendor ELISA (and Trautwig notes blunted DIA-MS neurofilament dynamic range), Stage-0 requires paired BioVendor ELISA vs automated CLIA pNfH & NfL immunoassay calibration on banked ALS CSF before claiming clinical responder misclassification."),
            ("Right Modality & Exposure — 3-Pillar PK/PD, Selectivity & Trial Landscape", "At 2 MIU SC x5 days q4w (>20-fold below oncology vascular-leak doses), aldesleukin selectively saturates high-affinity (Kd ~10 pM) trimeric CD25/CD122/CD132 on Tregs. Because CSF pNfH <=3,700 pg/mL (~25–30% 21-mo mortality in 750–3,700 and 0% in <750 pg/mL) has lower event rates than unstratified ALS and active Phase 2/3 ALSTARS (NCT07161999) omits a CSF pNfH gate, accruing 247 Schoenfeld deaths for 80% power at conservative HR=0.70 (138 at HR=0.62 [MODEL_PRIOR]) requires event-driven variable follow-up of N~650–750 across 36–42 months (18–24 mo accrual + 18–24 mo minimum follow-up, <5% vital-status censoring; or N~850–1,050 at fixed 24 mo), paired with Treg TSDR (PMID:17694575), CD56bright NK, and sCD25 (PMID:22343569) durability monitoring."),
            ("Right Patient — Biomarker Stratification & Combinatorial Positioning", "Enrolls riluzole-treated ALS patients stratified by BioVendor-bridged CLIA baseline CSF pNfH (keeping <750 pg/mL floor and 750–3,700 pg/mL strata prespecified separately while excluding >3,700 pg/mL), complementing neurovascular sST2 decoy clearance (C007) while strictly excluding simultaneous JAK1 inhibition (C019)."),
        ],
    },
}
