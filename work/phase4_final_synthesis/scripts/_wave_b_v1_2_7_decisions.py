"""Modular v1.2.7 Wave B primary-source patches for registries/candidate_decisions.csv."""
from __future__ import annotations

TS_V127 = "2026-11-21T19:30:00Z"


def apply_wave_b_decision_patches(dm: dict[str, dict[str, str]]) -> None:
    dm["C022"].update({
        "evidence_proves_hypothesis": (
            "Recessive human DNAJB2 loss-of-function variants (55 Open Targets EVA/ClinVar submissions, 25/25 (100%) single-gene GRCh38 P/LP variants in shared Exons 2-9 vs 0/25 in Zone A, OMIM 614881; Chen et al. 2016 Brain PMID:26936937; dominant stop-loss c.832T>G ER-trapping neuromyopathy PMID:37070754) cause distal hereditary motor neuropathy (dHMN5/CMT2T) and juvenile ALS, cytosolic DNAJB2a clears ubiquitylated TDP-43 aggregates, and human ALS/FTD tissue shows GC-adjusted cortical oligodendrocyte (-0.745, p=3.46e-7 in BA9; -0.618, p=2.59e-4 in BA4), NYGC cervical cord (-0.293, p=5.21e-5, n=86: 48 non-mutation sALS vs 38 Ctrl), Spillman MOESM1 C9-FTD cortical homogenate (-0.4470, p=3.05e-4, BH-FDR=0.0182, n=20) & synaptosome (-0.3818, p=0.00813, BH-FDR=0.2236, n=20; PMID:42789089), and iPSC-neuron (-1.115, p=0.0455, n=6) depletion. Primary 6-cohort splicing/APA scan confirms 0 TDP-43 cryptic/APA events (i3Neuron RNA log2FC=+0.092, p=0.124, padj=0.283), and AF-P25686-F1 resolves 2 rigid domains (aa 1-73 & 164-223, pLDDT=67.38; gnomAD v4.1 MANE ENST00000336576.10 LOEUF=0.836 vs cytosolic ENST00000392086.8 LOEUF=0.743)."
        ),
        "evidence_disproves_hypothesis": (
            "Edinburgh cortical oligodendrocyte snRNA-seq is underpowered/non-significant (-0.397, p=0.447, n=33), NYGC motor cortex bulk RNA is flat (+0.087, p=0.401), CSF TMT is null (p=0.779), motor-neuron vs oligodendrocyte compartment dominance is unresolved, internal Intron-9 sequence (chr2:219284988-219285939(+), 952 bp sparing 5'SS 219284836-219284845, Zone A CDS/stop 219284836-219284987, and BP/PPT/3'SS 219285940-219285986 whose blockade would prevent Exon-10 splicing and force DNAJB2b!) lacks mapped ISS/intronic-polyadenylation (IPA) cis-elements, and internal Intron-9 windows sit inside the mature cytoplasmic 3'-UTR of ER-prenylated (-CVVQ) DNAJB2b mRNA where steric/shift effects risk depleting ERAD-essential DNAJB2b."
        ),
        "discriminating_next_test": (
            "Quantify cytosolic DNAJB2a (ENST00000392086.8, 277 aa, excising 1,151-bp Intron 9 chr2:219284836-219285986(+)) vs Intron-9-retaining ER-prenylated DNAJB2b (ENST00000336576.10, 324 aa) precursor ratios by targeted PRM/RT-ddPCR in sporadic ALS spinal cord, and benchmark intrathecal pan-CNS/oligodendrocyte-tropic AAV-DNAJB2a cDNA replacement (cellular HSJ1a precedent PMID:26936937) against an internal Intron-9 2'-O-MOE ISS/IPA-competition microwalk restricted to chr2:219284988-219285939(+) (sparing 5'SS, Zone A CDS, and 3'SS/branchpoint chr2:219285940-219285986(+)) with mature DNAJB2b 3'-UTR stability and BiP/HSPA5 + CHOP/DDIT3 ERAD counter-screens in sALS iPSC-MN/oligodendrocyte co-cultures."
        ),
        "updated_at": TS_V127,
    })

    dm["C015"].update({
        "evidence_disproves_hypothesis": (
            "G2E3 Intron-1 cryptic ALE windows (#1 chr14:30563747-30563764(+) & #2 chr14:30563930-30563947(+)) map inside an Alu/SINE retroelement and fail 0mm transcriptome safety (375 spliced + 7,211 pre-mRNA 0mm hits on #1; 1 spliced + 37 pre-mRNA 0mm hits + constrained ELOC 1mm on #2; #3 hits constrained ELOC 1-nt bulge), NYGC bulk G2E3 cryptic detection is 0.54% (5/926 vs 0/750, selective=False) with null Ribo-seq (padj=0.890) and undetected cortical DIA protein (0 human G2E3 Q7L622 PDBs; AF-Q7L622-F1 only, with PHD2/3 RINGs catalytically active and HECT inactive per Brooks et al. 2008 PMID:18511420), SCFD1 (0 human Q8WVM8 PDBs; AF-Q8WVM8-F1 + rat 1Y9J / yeast Sly1p PDB 1MQS PMID:12426383) is pan-essential in DepMap (Chronos=-1.2619; gnomAD v4.1 MANE ENST00000458591 LOEUF=0.809 vs Open Targets v2.1.1 0.472) with opposing MN vs iMGL eQTL polarity and null cortical DIA protein (p=0.931/0.797), and CHEMBL3752910 (SCFD1 Kd=171 nM) is a promiscuous EPHA3 kinase inhibitor (IC50=0.3 nM)."
        ),
        "updated_at": TS_V127,
    })

    dm["C014"].update({
        "causal_vs_reactive_assessment": "UPSTREAM_COMPARTMENTAL_CASCADE_FOR_CHMP7_SECONDARY_SUBUNIT_FOR_CHMP2B",
        "evidence_proves_hypothesis": (
            "Human sALS/C9orf72 postmortem nuclei and iPSC-MNs exhibit nuclear CHMP7 retention preceding NUP injury and TDP-43 mis-splicing, acute CHMP7 ASO lowering reverses NPC/STMN2 defects (PMID:34321318, PMID:37639327; YCharOS validated antibodies PMID:42975030), and endogenous WT CHMP2B modulates nuclear CHMP7 accumulation in sALS iPSC-MNs (Keeley et al. 2024, PMID:39709457) alongside nominal C9-FTD cortical homogenate CHMP2B elevation (+0.337, p=0.0233, BH-FDR=0.151) and within-C9FTD iPSC pellet-vs-homogenate partitioning (+0.887, p=0.00114, padj=0.0205, n=3 C9FTD)."
        ),
        "evidence_disproves_hypothesis": (
            "Does NOT falsify partial nuclear normalization (flat bulk/snRNA-seq mRNA and null Spillman CHMP7 DIA protein across all fractions p=0.081..0.949 reflect subcellular nuclear-import localization rather than total abundance), BUT falsifies deep ESCRT ablation and flags pan-allele CHMP2B knockdown as high liability: CHMP7 is LoF-constrained (gnomAD v4.1 MANE ENST00000397677.6 LOEUF=0.496, pLI=0.984; Open Targets v2.1.1 LOEUF=0.430, pLI=0.9996), CRISPR-essential across 1,258 DepMap lines (mean Chronos=-0.6565), and required for cortical SATB2-LEMD2 activity-regulated genes (PMID:41744617) and telomeres (PMID:41677621), while WT CHMP2B is required for neuronal autophagosome maturation and sequential ANXA11->CHMP2B membrane repair (PMID:42349418 [Extrapolation: plasma-membrane laser injury])."
        ),
        "discriminating_next_test": (
            "Execute a subunit-resolved chronic (>=8-wk) head-to-head test in mature sALS/C9 iPSC-MNs comparing selective SUN1-CHMP7 nuclear-influx blockade (PMID:37639327) vs strictly titrated <=35-50% CHMP7 partial KD targeting 1-based Exon-11 3'-UTR chr8:23260600-23261999(+) (inside ENST00000397677.6 Exon 11 chr8:23260538-23261999(+); retaining CHMP7 as sole primary target while restricting any exploratory CHMP2B comparator strictly to 1-based Exon-6 3'-UTR chr3:87253823-87255556(+) inside ENST00000263780.9 Exon 6 chr3:87253712-87255556(+), sparing chr3:87253711 c.532-1G FTD3/ALS17 acceptor) under nuclear-envelope rupture challenge, co-measuring NUP/STMN2 rescue (YCharOS antibodies PMID:42975030), autophagic flux, ANXA11->CHMP2B repair (PMID:42349418 [Extrapolation: plasma membrane]), and SATB2-LEMD2 transcription (PMID:41744617)."
        ),
        "updated_at": TS_V127,
    })

    dm["S09"].update({
        "prior_art_crowding_level": "HEALEY_PH2_3_SELECTED_SPORADIC_ALS_TE_BIOMARKER_GATED",
        "evidence_proves_hypothesis": (
            "Phase 2a NCT04993755 (mixed N=42 C9orf72-ALS + FTD safety cohort, 400 mg/d PO TPN-101 / CHEMBL124363; alongside completed PSP Ph2a NCT04993768 N=42 & AGS Ph2 ISG program) reported favorable safety, reduced CSF IL-6 & NfL, ~50% slower 24-wk vital capacity decline in the C9-ALS subgroup (-8.4% vs -16.5% placebo), and May 2025 selection of TPN-101 for the Phase 2/3 HEALEY ALS Platform Trial; within motor ALS cortex, ALS-TE elevates IFNAR2 both vs ALS-Ox (+0.2793, p=6.32e-8, GC+cellcomp adj_p=3.87e-9, AUC=0.7698) and vs Control (+0.1920, p=6.62e-4, adj_p=0.0376) while retaining intact TYK2 (+0.5763 vs Ox, p=5.52e-9) and STAT2 (+0.3103 vs Ox, p=5.14e-8)."
        ),
        "evidence_disproves_hypothesis": (
            "Primary re-analysis of O'Neill 2025 (DS001_ONEILL) shows cortical ALS-TE prevalence is 13.40% (41/306 all cortical motor-ALS donors; 13.53% = 41/303 excluding 3 multi-region discordant donors; 11.52% in non-C9 sALS), spinal cord ALS-TE is 0.00% (0/331 donors, masked by ventral-horn gliosis/ox), and postmortem cortical ALS-TE TYK2 (-0.0732, p=0.465) & STAT2 (+0.0153, p=0.798) plus bulk ISGs (ISG15/IFIT1/MX1/OAS1/IRF9) are flat vs Control, while NCT04993755 remains unpublished in peer-reviewed form, no validated living-CSF ALS-TE enrichment assay exists for HEALEY Ph2/3 sporadic enrollment, nucleoside prodrug TPN-101 requires intracellular TPN-101-TP triphosphorylation (post-mitotic MN vs glial dCK/kinase efficiency unmeasured), and backup BHV-8000 is a dual TYK2/JAK1 (JH1) inhibitor rather than a JAK1-sparing TYK2-JH2 allosteric binder."
        ),
        "factual_justification": (
            "Oral LINE-1 RT inhibitor TPN-101 (TRL_5; selected May 2025 for Phase 2/3 HEALEY ALS Platform Trial following mixed N=42 C9orf72-ALS/FTD Phase 2a NCT04993755 & PSP NCT04993768) showed encouraging C9-ALS subgroup biomarker (CSF IL-6/NfL) and vital-capacity signals, and cortical ALS-TE elevates IFNAR2 above Control, yet efficacy in sporadic ALS-TE remains unproven pending peer-reviewed NCT04993755 publication, living-CSF ORF1p/L1HS enrichment for the ~13.4-13.5% cortical ALS-TE subgroup (0/331 bulk cord), and post-mitotic human MN vs glial TPN-101-TP triphosphorylation verification."
        ),
        "discriminating_next_test": (
            "Anchor Phase 2/3 HEALEY ALS Platform Trial sporadic biomarker stratification by disaggregating three biological layers alongside peer-reviewed NCT04993755 C9-ALS vs FTD publication and human iPSC-MN vs microglial TPN-101-TP LC-MS/MS phosphorylation verification: (1) cryptic HDGFL2 (PMID:38278991/PMID:42854693) solely as the upstream pan-TDP-43 pathology gate, (2) direct retroelement cargo (CSF/plasma LINE-1 ORF1p Simoa PMID:40050409 + CSF EV L1HS RNA/cDNA) as the subtype-specific ALS-TE enrichment gate calibrated to 13.40% (41/306; 13.53% = 41/303 non-discordant; 11.52% non-C9 sALS) cortical prevalence, and (3) ultrasensitive CSF IL-6 + cGAS-STING/pSTAT2/ISG activity as longitudinal PD before testing dual TYK2/JAK1 JH1 inhibition (BHV-8000, which also blocks gp130/JAK1-STAT3) vs selective allosteric TYK2-JH2 probes."
        ),
        "updated_at": TS_V127,
    })
