"""Curated faceted-bullet & paragraph splits for Candidate Dossier cards — Part A (Ranks #1–#29)."""
from __future__ import annotations

CARD_SPLITS_A: dict[tuple[str, str], list[tuple[str, str]]] = {
    ("EALS-030", "verdict"): [
        ("Core molecular target backed by", "- Human Genetics & Mouse Axon Models: Core molecular target backed by"),
        ("alongside blood NfL), parallel axonal protection", "alongside blood NfL).\n- Parallel STMN2 Biology & Low Constraint: Parallel axonal protection"),
        ("MANE LOEUF=1.413); across 4 clinical-stage", "MANE LOEUF=1.413).\n- Clinical Landscape & ARM-TIR T-Lock Rationale: Across 4 clinical-stage"),
    ],
    ("EALS-001", "verdict"): [
        ("Unlike Riluzole or Methylcobalamin,", "- Causal Human ALS Genetics: Unlike Riluzole or Methylcobalamin,"),
        ("Brown Fig. 1c), and has direct human cortical", "Brown Fig. 1c).\n- Human Neuronal Synaptic Rescue: Direct human cortical"),
        ("Standalone me-too single-target ASOs", "\n- Multiplex Positioning: Standalone me-too single-target ASOs"),
    ],
    ("EALS-007", "verdict"): [
        ("Bulk transcriptomic nulls reflect", "- Vascular Dilution & Biofluid Divergence: Bulk transcriptomic nulls reflect"),
        ("Because donor-level Edinburgh", "\n- Endothelial & Spatial Induction: Donor-level Edinburgh"),
        ("tested in ALS (whereas in Alzheimer's disease", "tested in ALS.\n- AD & Preclinical Prior-Art Context: In Alzheimer's disease"),
        ("Korhonen et al. 2019 PMID:30705990), the Untested != Falsified triage rule mandates", "Korhonen et al. 2019 PMID:30705990.\n- Normoxic & Isoform Validation Gate: The Untested != Falsified triage rule mandates"),
    ],
    ("EALS-038", "verdict"): [
        ("Elevated to #1 of Tier 3 Exploratory Discovery (Rank #9/52): surviving", "- Spatial & Single-MN Proteomics (Rank #9/52, #1 Tier 3): Surviving"),
        ("vs 2 CTL donors / 25 cells), and C9-FTD synaptosomal loss", "vs 2 CTL donors / 25 cells).\n- Synaptosomal Depletion & Validation Gate: C9-FTD synaptosomal loss"),
    ],
    ("EALS-038", "proves"): [
        ("Sole Ma 2022 cryptic-spliced gene", "- Cervical Spatial & Cryptic Splicing: Sole Ma 2022 cryptic-spliced gene"),
        ("PMID:42135512) and depleted in Kozareva et al. 2025", "PMID:42135512).\n- Staged Single-LCM Spinal MN Proteomics: Depleted in Kozareva et al. 2025"),
        ("temporal precedence), replicated in NYGC cervical", "temporal precedence).\n- Spinal & Cortical Replication: Replicated in NYGC cervical"),
    ],
    ("EALS-038", "disproves"): [
        ("Cervical ALS-SOD1/FUS bulk mRNA", "- Underpowered Subtype & i3Neuron Ribo-seq: Cervical ALS-SOD1/FUS bulk mRNA"),
        ("PMID:35197628), gnomAD v4.1 population constraint", "PMID:35197628).\n- Population Constraint & Upstream ROCK Nulls: gnomAD v4.1 population constraint"),
        ("PMID:39424560), neuronal-mass-residualized tSTMN2", "PMID:39424560).\n- tSTMN2 Residualization & Unannotated 5'SS Donors: Neuronal-mass-residualized tSTMN2"),
    ],
    ("EALS-022", "proves"): [
        ("Recessive human DNAJB2 loss-of-function variants", "- Mendelian Motor Neuropathy & In Vivo Rescue: Recessive human DNAJB2 loss-of-function variants"),
        ("PMID:24023695), and human ALS/FTD tissue shows", "PMID:24023695).\n- Human ALS/FTD Multi-Omic Depletion: Human ALS/FTD tissue shows"),
        ("Primary 6-cohort splicing/APA scan", "\n- Splicing Independence & Structural Domains: Primary 6-cohort splicing/APA scan"),
    ],
    ("EALS-022", "disproves"): [
        ("Edinburgh cortical oligodendrocyte snRNA-seq", "- Null Cortical/CSF Subsets & Isoform Ambiguity: Edinburgh cortical oligodendrocyte snRNA-seq"),
        ("dominance is unresolved, internal Intron-9 sequence", "dominance is unresolved.\n- Unmapped Intron-9 Cis-Elements: Internal Intron-9 sequence"),
        ("cis-elements, and internal Intron-9 windows sit", "cis-elements.\n- ER-Prenylated DNAJB2b 3'-UTR Safety Hazard: Internal Intron-9 windows sit"),
    ],
    ("EALS-035", "proves"): [
        ("Guo et al. 2026 (", "- Cortical iNeuron ASO Rescue & BaseScope: Guo et al. 2026 ("),
        ("Layer-2 BaseScope ISH, corroborated by Newton et al. 2026", "Layer-2 BaseScope ISH.\n- Postmortem qPCR & Cortical Proteomics: Corroborated by Newton et al. 2026"),
        ("\n\nSplicing, genetic constraint, and target-window profile: Brown", "\n- Splicing Magnitude & Intron-53 Constraint: Brown"),
        ("kinase truncation, AlphaGenome-predicted rs2173852", "kinase truncation.\n- rs2173852 Variant & Target Windows: AlphaGenome-predicted rs2173852"),
    ],
    ("EALS-035", "nxt"): [
        ("before CE-Exon54) to verify zero shunting", "before CE-Exon54); verify zero shunting"),
    ],
    ("EALS-036", "proves"): [
        ("#1 FDR-significant Ribo-seq loss", "- Ribo-seq Loss & Intron-26 Alternative 3'SS: #1 FDR-significant Ribo-seq loss"),
        ("event-specific decay) and postmortem tissue detection", "event-specific decay).\n- Postmortem Tissue & Cortical Proteomics: Postmortem tissue detection"),
        ("\n\nProteomic and off-target profile: Kozareva et al. 2025", ", paired with Kozareva et al. 2025"),
        ("PMID:42789089), and GENCODE v46 6-tier off-target design", "PMID:42789089).\n- GENCODE v46 Off-Target Window Selection: GENCODE v46 off-target design"),
    ],
    ("EALS-036", "disproves"): [
        ("Spillman synaptosome DIA is null", "- Null Synaptosome & Unreplicated CSF Signals: Spillman synaptosome DIA is null"),
        ("\n\nCortical/spinal bulk RNA is attenuated", "\n- Attenuated Bulk RNA & Sparse Lumbar Detection: Cortical/spinal bulk RNA is attenuated"),
        ("identity unresolved), and treatment direction remains open", "identity unresolved).\n- Open pSTAT3 vs. Synaptic Directionality: Treatment direction remains open"),
    ],
    ("EALS-036", "nxt"): [
        ("DOI:10.1186/s44477-025-00013-w), and evaluate under", "DOI:10.1186/s44477-025-00013-w); evaluate under"),
    ],
    ("EALS-042", "proves"): [
        ("#1 Bryce-Smith 2025 ST5 pathology-selective", "- Pathology-Selective NYGC Cryptic ALE: #1 Bryce-Smith 2025 ST5 pathology-selective"),
        ("\n\nIndependent splicing & proteomic cohorts: Brown MOESM11", "\n- i3Neuron Splicing & Ribo-seq Loss: Brown MOESM11"),
        ("row padj=0.958), Spillman 2026 C9-FTD MOESM1", "row padj=0.958).\n- Cortical Proteomics & Window #1 Profile: Spillman 2026 C9-FTD MOESM1"),
    ],
    ("EALS-041", "proves"): [
        ("TDP-43-selective 3.90-kb 3'Ext increases", "- Neuronal 3'-Extension & Protein Elevation: TDP-43-selective 3.90-kb 3'Ext increases"),
        ("PMID:36482247), while intronic RNase-H pre-mRNA scanning", "PMID:36482247).\n- Intronic Pre-mRNA Off-Target Screen: Intronic RNase-H pre-mRNA scanning"),
    ],
    ("EALS-041", "disproves"): [
        ("Pineda BA4 excitatory neurons is null", "- Null BA4 snRNA & ChIP-Atlas Target Sets: Pineda BA4 excitatory neurons is null"),
        ("gating caveats), 10x 3'-snRNA-seq technical sparsity", "gating caveats).\n- 3'-snRNA-seq Capture Sparsity: 10x 3'-snRNA-seq technical sparsity"),
        ("10.64898/2026.08.07.743523), and nuclear RNase-H cleavage", "10.64898/2026.08.07.743523).\n- Hemizygous Xp11.23 Transcription-Termination Risk: Nuclear RNase-H cleavage"),
    ],
    ("EALS-041", "nxt"): [
        ("human iPSC-MNs, mandating canonical Exon 1-6", "human iPSC-MNs; enforce canonical Exon 1-6"),
    ],
    ("EALS-040", "proves"): [
        ("#1 Bryce-Smith 2025 gene-level Ribo-seq loss", "- Ribo-seq, Postmortem qPCR & Cortical Trend: #1 Bryce-Smith 2025 gene-level Ribo-seq loss"),
        ("PMID:41256508 (preprint)), and Bye 2025 ID-MND", "PMID:41256508 (preprint)).\n- Patient iPSC-MN Cluster (Unresolved Coordinates): Bye 2025 ID-MND"),
        ("PMID:41120750); 20-nt polypyrimidine-shifted #1", "PMID:41120750).\n- Polypyrimidine-Shifted Window #1: 20-nt polypyrimidine-shifted #1"),
    ],
    ("EALS-040", "disproves"): [
        ("Bryce-Smith ST5 classifies", "- Non-Selective Baseline CNS Expression: Bryce-Smith ST5 classifies"),
        ("within-donor correlation), no gnomAD v4.1 pLoF depletion", "within-donor correlation).\n- Recessive Constraint & Null Cortical DIA: No gnomAD v4.1 pLoF depletion"),
        ("PMID:42789089), and secondary CE chr2:3458462-3458515(+)", "PMID:42789089).\n- Secondary Cryptic Exon & 13-nt EJC Rule: Secondary CE chr2:3458462-3458515(+)"),
    ],
    ("EALS-039", "proves"): [
        ("Brown CE FDR=2.20e-17", "- Cryptic Exon, Ribo-seq & Postmortem qPCR: Brown CE FDR=2.20e-17"),
        ("8/8 CTL motor cortex), Kozareva 2025 WTC11", "8/8 CTL motor cortex).\n- Proteomic Depletion & Window #1: Kozareva 2025 WTC11"),
    ],
    ("EALS-015", "verdict"): [
        ("Human chr14q12 ALS GWAS/eQTL/sQTL signals", "- Opposing MN vs. Microglial Genetic Associations: Human chr14q12 ALS GWAS/eQTL/sQTL signals"),
        ("fit n=186/185/185]) studies while leaving causal", "fit n=186/185/185]) studies.\n- Open Cell-Type Directionality & Safety Limits: Leaves causal"),
    ],
    ("EALS-015", "proves"): [
        ("At chr14q12, SCFD1 (EALS-015.1) shows", "- Motor-Neuron eQTL–GWAS Overlap (SCFD1): At chr14q12, SCFD1 (EALS-015.1) shows"),
        ("GTEx BA9 +0.269) AND formal Bayesian colocalization", "GTEx BA9 +0.269).\n- Microglial Colocalization (SCFD1): Formal Bayesian colocalization"),
        ("Zenodo 21471267), where SCFD1 is the sole", "Zenodo 21471267), where SCFD1 is the sole"),
        ("primary microglia) and the very same rs229143-A allele", "primary microglia).\n- Opposite Microglial Slope & Phagocytosis Screen: The very same rs229143-A allele"),
        ("\n\nAdjacent G2E3 (EALS-015.2) combines", "\n- Adjacent G2E3 Splicing & Cryptic ALE: Adjacent G2E3 (EALS-015.2) combines"),
        ("MAJIQ 'FDR'=2.90e-21). Open Targets SuSiE-inf", "MAJIQ 'FDR'=2.90e-21).\n- Cross-Ancestry Fine-Mapping & Haplotype Purity: Open Targets SuSiE-inf"),
    ],
    ("EALS-015", "disproves"): [
        ("G2E3 Intron-1 cryptic ALE windows", "- Alu/SINE Off-Target Failure (G2E3): G2E3 Intron-1 cryptic ALE windows"),
        ("\n\nPostmortem detection and essentiality limits: NYGC bulk G2E3", "\n- Low Bulk G2E3 Detection & Domain Architecture: NYGC bulk G2E3"),
        ("PMID:18511420), SCFD1 (0 human Q8WVM8 PDBs", "PMID:18511420).\n- SCFD1 Pan-Essentiality, TWAS Divergence & Ligand Promiscuity: SCFD1 (0 human Q8WVM8 PDBs"),
    ],
    ("EALS-015", "nxt"): [
        ("trafficking (given SuSiE mean LD R2=0.988", "trafficking; (3) Stratify by 1000G EUR/AFR haplotype purity (SuSiE mean LD R2=0.988"),
        ("rs229143-A, paired with opposite SCFD1", "rs229143-A); (4) Reconcile opposite SCFD1"),
        ("barring pan-CNS knockdown).", "barring pan-CNS knockdown."),
    ],
    ("EALS-014", "proves"): [
        ("Human sALS/C9orf72 postmortem nuclei", "- Nuclear CHMP7 Retention & ASO Rescue: Human sALS/C9orf72 postmortem nuclei"),
        ("PMID:42975030), and Keeley et al. 2024", "PMID:42975030).\n- CHMP2B Knockdown Rescue & Subcellular Partitioning: Keeley et al. 2024"),
    ],
    ("EALS-014", "disproves"): [
        ("Does NOT falsify partial nuclear normalization", "- Subcellular Localization vs. Total Abundance: Does NOT falsify partial nuclear normalization"),
        ("total abundance), BUT falsifies deep ESCRT ablation", "total abundance).\n- CHMP7 Essentiality & CHMP2B Autophagy/Repair Liability: Rules out deep ESCRT ablation"),
    ],
    ("EALS-033", "proves"): [
        ("Phase 2a NCT04993755 (", "- Phase 2a C9-ALS/FTD Signals & HEALEY Selection: Phase 2a NCT04993755 ("),
        ("Master Protocol NCT04297683); within motor ALS cortex", "Master Protocol NCT04297683).\n- Cortical ALS-TE IFNAR2/TYK2/STAT2 Enrichment: Within motor ALS cortex"),
        ("p=5.14e-8). Upstream LINE-1 ORF2p RT blockade", "p=5.14e-8).\n- Upstream cGAS-STING Selectivity & Neuronal TBK1/PSMB8 Sparing: Upstream LINE-1 ORF2p RT blockade"),
    ],
    ("EALS-033", "disproves"): [
        ("Primary re-analysis of O'Neill 2025", "- Cortical ALS-TE Prevalence & Unresolved Spinal Split: Primary re-analysis of O'Neill 2025"),
        ("Glia-cord or Ox-cord, and postmortem cortical ALS-TE TYK2", "Glia-cord or Ox-cord.\n- Flat Cortical ISGs vs. Control & Unpublished Trial Data: Postmortem cortical ALS-TE TYK2"),
        ("ALS CSF), nucleoside prodrug TPN-101 inhibits", "ALS CSF).\n- ORF2p RT vs. dsRNA Mechanism & Comparator PK: Nucleoside prodrug TPN-101 inhibits"),
    ],
    ("EALS-018", "proves"): [
        ("Zhang 2026 TDP-43+ ALS vs. Control", "- Cervical Anterior-Horn Spatial C1QA/B/C Upregulation: Zhang 2026 TDP-43+ ALS vs. Control"),
        ("C1QA +1.49 [2.76e-4]), and Scott-Hewitt et al.", "C1QA +1.49 [2.76e-4]).\n- C3-Independent Neuronal Endocytosis & RNP Phase Separation: Scott-Hewitt et al."),
    ],
    ("EALS-018", "disproves"): [
        ("Bulk spinal RNA and antemortem CSF", "- Glial Proportion & RCCX CNV Confounding: Bulk spinal RNA and antemortem CSF"),
        ("LOEUF=0.257/0.413); systemic C1q ablation carries", "LOEUF=0.257/0.413).\n- Systemic Anti-C1q Autoimmune Toxicity (HD Phase 2): Systemic C1q ablation carries"),
        ("(modeled estimate); whereas in completed open-label ALS Phase 2a", "(modeled estimate)).\n- Open-Label ALS Phase 2a Registry & Form 10-K: In completed open-label ALS Phase 2a"),
        ("without peer-reviewed publication; note Annexon also advanced", "without peer-reviewed publication.\n- Intravitreal Fab & C1s Modality Precedents: Annexon also advanced"),
        ("CLR-stalk RNP uptake); IV BBB-TfR-shuttled IgG", "CLR-stalk RNP uptake.\n- Systemic Sink Depletion, Rapid Fab Clearance & Mouse KO: IV BBB-TfR-shuttled IgG"),
    ],
    ("EALS-018", "nxt"): [
        ("up to aa 114]; rejecting IV ANX005", "up to aa 114]); (2) Exclude IV ANX005"),
        ("CSF trough (modeled estimate)); (2) Gate head-to-head", "CSF trough (modeled estimate); (3) Gate head-to-head"),
    ],
    ("EALS-023", "proves"): [
        ("YKT6 (EALS-023.1) converges across exome-wide", "- Exome-Wide Rare Coding Variant (p.Tyr64Cys): YKT6 (EALS-023.1) converges across exome-wide"),
        ("top 0.352%), direct 3.46A heavy-atom contact", "top 0.352%).\n- Acyl-Pocket Contact & Dual Prenylation Requirement: Direct 3.46A heavy-atom contact"),
        ("\n\nConvergent TDP-43 & human cortical pathology: TDP-43", "\n- Convergent TDP-43 Splicing/APA & Cortical Depletion: TDP-43"),
    ],
    ("EALS-023", "disproves"): [
        ("YKT6 is pan-essential across 1,258 DepMap lines", "- Pan-Essentiality & Carrier Frequency: YKT6 is pan-essential across 1,258 DepMap lines"),
        ("risk allele]) while the rat PDB 3KYQ", "risk allele]).\n- Pocket Expansion & Autoinhibited Closed-State Hazard: Rat PDB 3KYQ"),
        ("wild-type YKT6 ALS — alongside null C9-FTD", "wild-type YKT6 ALS.\n- Null Synaptosomal DIA & Essential Cis-Golgi SNAREs: Null C9-FTD"),
    ],
    ("EALS-016", "disproves"): [
        ("Two major findings rule out unidirectional neuronal IRP2 degradation while retaining bidirectional sensor probing: (1) Cell-type & directionality split:", "- Cell-Type & Directionality Split:"),
        ("functional iron starvation — directly corroborated in vivo", "functional iron starvation.\n- In Vivo Irp2-Null Neurodegeneration: Directly corroborated in vivo"),
        ("PMID:22003390); (2) Bulk iron chelation", "PMID:22003390).\n- Negative Iron-Chelation Screen & Clinical Trials: Bulk iron chelation"),
    ],
    ("EALS-016", "nxt"): [
        ("negative control), measuring labile Fe2+", "negative control); measure labile Fe2+"),
    ],
    ("EALS-020", "verdict"): [
        ("12-wk randomized C9orf72-ALS target engagement", "- Phase 2a Target Engagement & Sporadic ALS Gap: 12-wk randomized C9orf72-ALS target engagement"),
        ("pulsed dosing open, while preclinical neuronal ClC-7", "pulsed dosing open.\n- Preclinical Vacuolation & Exploratory NfL Shifts: Preclinical neuronal ClC-7"),
        ("mean +50% [n=4]), and distinct inhibitor VRG50635", "mean +50% [n=4]).\n- Comparator VRG50635 Safety Signals & Washout Gate: Distinct inhibitor VRG50635"),
    ],
    ("EALS-020", "proves"): [
        ("Apilimod (free base CHEMBL4297643", "- Patient iPSC-MN Rescue: Apilimod (free base CHEMBL4297643"),
        ("q=0.0173); AIT-101 dimesylate 125 mg BID", "q=0.0173).\n- Phase 2a C9orf72-ALS CSF PK & Poly(GP) Reduction: AIT-101 dimesylate 125 mg BID"),
    ],
    ("EALS-020", "disproves"): [
        ("Trautwig 2025 CSF GDI2 is quantified", "- Non-Significant sALS CSF GDI2 & Heterogeneous Screen Response: Trautwig 2025 CSF GDI2 is quantified"),
        ("worsened at 2.5 uM; preclinical PIKfyve blockade", "worsened at 2.5 uM.\n- ClC-7 Osmotic Vacuolation & LRRK2/CASM Stress: Preclinical PIKfyve blockade"),
        ("PMID:42994990); in AIT-101 NCT05163886", "PMID:42994990).\n- AIT-101 CSF sGPNMB & Exploratory NfL Shifts: In AIT-101 NCT05163886"),
        ("mean +50% (+49.7%, n=4); and in distinct inhibitor VRG50635", "mean +50% (+49.7%, n=4).\n- Comparator VRG50635 Clinical SAEs & Trial Termination: In distinct inhibitor VRG50635"),
    ],
    ("EALS-020", "nxt"): [
        ("Apilimod (CHEMBL4297643; resolving the modeled ODE sensitivity", "Apilimod (CHEMBL4297643); (2) Resolve the modeled ODE sensitivity"),
        ("10.26508/lsa.202603939); (2) Pair intracellular", "10.26508/lsa.202603939; (3) Pair intracellular"),
    ],
    ("EALS-019", "verdict"): [
        ("Descriptive open-label ALS CSF CXCL10", "- Open-Label CXCL10 & Neuronal/Glial Rationale: Descriptive open-label ALS CSF CXCL10"),
        ("However, EALS-019 is recalibrated to the Tier 3 exploratory watchlist because", "\n- CNS Exposure Deficit, VTE Risk & JAK1/JAK2 Trade-Off: EALS-019 is recalibrated to the Tier 3 exploratory watchlist because"),
    ],
    ("EALS-019", "proves"): [
        ("Rank #2/107 in Bye 2025", "- Patient iPSC-MN Screen & Neuronal JAK2 APA: Rank #2/107 in Bye 2025"),
        ("p=0.0457, n=34); NYGC ALS-Glia enriches", "p=0.0457, n=34).\n- ALS-Glia gp130/JAK-STAT Enrichment: NYGC ALS-Glia enriches"),
        ("TYK2 is flat p=0.843); originating C9orf72 dsRNA", "TYK2 is flat p=0.843).\n- Open-Label NADALS CSF PK & CXCL10 Readout: Originating C9orf72 dsRNA"),
        ("JAK occupancy), while subsequent cortical TDP-43", "JAK occupancy).\n- Cortical dsRNA->TYK2 Potency Gap: Subsequent cortical TDP-43"),
    ],
    ("EALS-019", "disproves"): [
        ("P-gp/BCRP efflux limits", "- P-gp/BCRP Efflux & 657-Fold CNS Exposure Gap: P-gp/BCRP efflux limits"),
        ("2.5 uM screen); NADALS ALS had", "2.5 uM screen).\n- Open-Label NADALS Thromboembolic Events: NADALS ALS had"),
        ("4/9 non-completers); structural/mechanistic", "4/9 non-completers).\n- Neuronal JAK2 vs. Glial JAK1/TYK2 Trade-Off: Structural/mechanistic"),
        ("and neuronal JAK2; shotgun MS CSF CXCL10", "and neuronal JAK2.\n- Left-Censored CSF CXCL10 & Null Center Comparison: Shotgun MS CSF CXCL10"),
        ("CSF glial panel; gnomAD v4.1 MANE JAK1", "CSF glial panel.\n- JAK1 Constraint & FDA Boxed Warnings: gnomAD v4.1 MANE JAK1"),
        ("chronic dosing. Moreover, whereas complete Tbk1 deletion", "chronic dosing.\n- Neuronal TBK1–IFN-beta–PSMB8 Clearance Trade-Off & RIPK1/TBK1 Context: Whereas complete Tbk1 deletion"),
    ],
    ("EALS-026", "verdict"): [
        ("Unreported randomized Phase 2/3 outcomes", "- Unreported Clinical Trials & Underpowered Autopsy Series: Unreported randomized Phase 2/3 outcomes"),
        ("powered RCT futility; EALS-026 (", "powered RCT futility.\n- Low-Priority Tier 3 Watchlist Scope: EALS-026 ("),
    ],
    ("EALS-026", "disproves"): [
        ("Randomized Phase 2/3 ALS trial NCT04082832", "- Unreported Phase 2/3 & Discontinued Clinical Program: Randomized Phase 2/3 ALS trial NCT04082832"),
        ("\n\nObservational postmortem neuropathology", "\n- Null Treated-Decedent Postmortem Neuropathology: Observational postmortem neuropathology"),
        ("\n\nUnbound human CNS exposure", "\n- Unbound CNS Exposure Gap & Hypoxic PET Dissociation: Unbound human CNS exposure"),
    ],
    ("EALS-047", "proves"): [
        ("Sub-FDR Bye 2025 screen survival delta", "- Sub-FDR iPSC-MN Screen & Murine Origin: Sub-FDR Bye 2025 screen survival delta"),
        ("PMID:28128456; Alsonex completed N=8 ALS", "PMID:28128456).\n- Phase 1b Safety/Ex Vivo PD & Missing Efficacy RCTs: Alsonex completed N=8 ALS"),
        ("efficacy RCTs).", "efficacy RCTs."),
    ],
    ("EALS-047", "disproves"): [
        ("Upstream human ALS C5 cleavage inhibitors", "- Upstream C5 Clinical Failures & Flat Neuronal C5AR1: Upstream human ALS C5 cleavage inhibitors"),
        ("vs 4.54, n=33), and Bye 2025 monocultures lack", "vs 4.54, n=33).\n- Glia-Free Monoculture Off-Target Alternative: Bye 2025 monocultures lack"),
    ],
    ("EALS-047", "nxt"): [
        ("C5b-9/C5L2), alongside peer-reviewed unbound", "C5b-9/C5L2); quantify peer-reviewed unbound"),
    ],
    ("EALS-050", "verdict"): [
        ("Retained in Tier 3 Exploratory Discovery (Rank #27/52): sub-FDR", "- Screen Thiol Buffering & Low-Dose Oral Trial (Rank #27/52): Sub-FDR"),
        ("1,800 mg/d EH301, yet Louwerse 1995", "1,800 mg/d EH301.\n- Underpowered Subcutaneous Trial & High-Dose CSF Penetration: Louwerse 1995"),
    ],
    ("EALS-050", "proves"): [
        ("Bye 2025 iPSC-MN screen Rank #12/107", "- iPSC-MN Screen & Underpowered Subcutaneous Trial: Bye 2025 iPSC-MN screen Rank #12/107"),
        ("p=0.06), and high-dose oral NAC human CSF", "p=0.06).\n- High-Dose Oral Human CSF Penetration: High-dose oral NAC human CSF"),
    ],
    ("EALS-052", "proves"): [
        ("Bye 2025 iPSC-MN screen Rank #20/107", "- Sub-FDR Patient iPSC-MN Screen Shift: Bye 2025 iPSC-MN screen Rank #20/107"),
        ("p=0.04190) and randomized double-blind", "p=0.04190).\n- Phase 1 Historical-Control Tolerability: Randomized double-blind"),
    ],
    ("EALS-005", "verdict"): [
        ("Unstratified symptomatic AMPA/NMDA/class-I-Na+ regimens", "- Stage-Gated Excitability Rationale: Unstratified symptomatic AMPA/NMDA/class-I-Na+ regimens"),
        ("disease-modification RCT. EALS-005 serves strictly", "disease-modification RCT.\n- Companion Stratification Protocol Scope: EALS-005 serves strictly"),
    ],
    ("EALS-005", "proves"): [
        ("Riluzole (INaP modulator) is #1/107", "- Phenotypic Screen & Human KCNQ2 Splicing Loss: Riluzole (INaP modulator) is #1/107"),
        ("PMID:41174170); human constant-stimulus", "PMID:41174170).\n- Human Cortical SICI & Axonal SDTC Engagement: Human constant-stimulus"),
        ("FIH PK NCT05667779), distinct from RMT-normalized", "FIH PK NCT05667779).\n- Threshold-Tracking TT-SICI Paradigm Distinction: Distinct from RMT-normalized"),
    ],
    ("EALS-005", "disproves"): [
        ("Symptomatic postsynaptic glutamate receptor regimens", "- Unstratified Postsynaptic & Na+ Blocker Failures: Symptomatic postsynaptic glutamate receptor regimens"),
        ("unstratified symptomatic trials alongside cross-sectional reductions", "unstratified symptomatic trials.\n- Cross-Sectional GRIN1/NPTX2 Loss & Unproven Staging Transition: Cross-sectional reductions"),
    ],
    ("EALS-005", "nxt"): [
        ("prospectively validated — in an early-onset ALS", "prospectively validated; evaluate in an early-onset ALS"),
    ],
    ("EALS-022", "verdict"): [
        ("Anchored by human Mendelian", "- Mendelian Genetics & Multi-Omic Depletion: Anchored by human Mendelian"),
        ("isoform-blind P25686); retained in Tier 3", "isoform-blind P25686).\n- Tier 3 Isoform & Safety Validation Gate: Retained in Tier 3"),
    ],
    ("EALS-042", "disproves"): [
        ("7/9 GENCODE protein-coding DLGAP1beta isoforms", "- Downstream Internal Promoter Escape (7/9 Isoforms): 7/9 GENCODE protein-coding DLGAP1beta isoforms"),
        ("5'UTR Intron-2, and spinal motor-neuron penetrance", "5'UTR Intron-2.\n- Unproven Spinal Motor-Neuron Penetrance: Spinal motor-neuron penetrance"),
    ],
    ("EALS-014", "verdict"): [
        ("Per the Untested != Falsified triage rule,", "- Subcellular Localization vs. Bulk Nulls: Per the Untested != Falsified triage rule,"),
        ("do not falsify EALS-014. EALS-014 is retained", "do not falsify EALS-014.\n- Sub-Node Dissection (CHMP7 vs. CHMP2B): EALS-014 is retained"),
    ],
    ("EALS-033", "verdict"): [
        ("Oral LINE-1 RT inhibitor TPN-101", "- Phase 2a C9-ALS Signals & HEALEY Selection: Oral LINE-1 RT inhibitor TPN-101"),
        ("IFNAR2 above Control, yet efficacy in sporadic ALS-TE", "IFNAR2 above Control.\n- Unproven Sporadic ALS-TE Enrichment & Mechanism: Efficacy in sporadic ALS-TE"),
    ],
    ("EALS-018", "verdict"): [
        ("Per the Untested != Falsified triage rule,", "- Parenchymal C1q vs. Systemic C3 Scope: Per the Untested != Falsified triage rule,"),
        ("confounded/null. Completed open-label ALS Phase 2a", "confounded/null.\n- Open-Label ALS Phase 2a vs. HD Systemic Autoimmunity: Completed open-label ALS Phase 2a"),
        ("99.99% (modeled estimate)) and unmodified q4w IT Fab", "99.99% (modeled estimate)).\n- Intrathecal Half-Life & C-Bouton Gate: Because unmodified q4w IT Fab"),
    ],
    ("EALS-016", "verdict"): [
        ("Parkinson's FAIRPARK-II motor worsening", "- Negative Bulk Iron-Chelation Precedents: Parkinson's FAIRPARK-II motor worsening"),
        ("microglia untested; pivoted from unidirectional", "microglia untested.\n- Bidirectional Sensor Watchlist Scope: Pivoted from unidirectional"),
    ],
    ("EALS-016", "proves"): [
        ("TDP-43 depletion induces coordinated", "- Coordinated TDP-43 Iron-Axis 3'-UTR Lengthening: TDP-43 depletion induces coordinated"),
        ("mRNA upregulation; postmortem tissues show", "mRNA upregulation.\n- Postmortem RNA, Cortical DIA & CSF Remodeling: Postmortem tissues show"),
        ("DIA p=0.0273). PDB 3V5Z", "DIA p=0.0273).\n- Dual Iron-Cofactor Structural Requirement: PDB 3V5Z"),
    ],
}
