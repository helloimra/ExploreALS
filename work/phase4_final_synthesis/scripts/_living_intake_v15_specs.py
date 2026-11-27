"""Specifications for ExploreALS v1.5.0 Living-Evidence Target Intake EALS-054 (L02, NADSYN1) & EALS-055 (L03, CYFIP2)."""
from __future__ import annotations

VERIFIED_CITATIONS_V15: dict[str, dict[str, dict[str, str]]] = {
    "pmids": {
        "21107423": {"first_author": "Chen Z", "pubdate": "2010 Nov 25", "journal": "Nature", "title": "Structure and control of the actin regulatory WAVE complex."},
        "22101682": {"first_author": "Logan CV", "pubdate": "2011 Nov 20", "journal": "Nat Genet", "title": "Mutations in MEGF10, a regulator of satellite cell myogenesis, cause early onset myopathy, areflexia, respiratory distress and dysphagia (EMARDD)."},
        "28011744": {"first_author": "Pasetto L", "pubdate": "2017 Feb 8", "journal": "J Neurosci", "title": "Targeting Extracellular Cyclophilin A Reduces Neuroinflammation and Extends Survival in a Mouse Model of Amyotrophic Lateral Sclerosis."},
        "28280971": {"first_author": "Tolcher AW", "pubdate": "2017 Apr", "journal": "Cancer Chemother Pharmacol", "title": "A phase 1 study of anti-TGFbeta receptor type-II monoclonal antibody LY3022859 in patients with advanced solid tumors."},
        "29534297": {"first_author": "Nakashima M", "pubdate": "2018 Apr", "journal": "Ann Neurol", "title": "De novo hotspot variants in CYFIP2 cause early-onset epileptic encephalopathy."},
        "31883644": {"first_author": "Szot JO", "pubdate": "2020 Jan 2", "journal": "Am J Hum Genet", "title": "Bi-allelic Mutations in NADSYN1 Cause Multiple Organ Defects and Expand the Genotypic Spectrum of Congenital NAD Deficiency Disorders."},
        "31911602": {"first_author": "Chuenchor W", "pubdate": "2020 Jan 7", "journal": "Nat Commun", "title": "Different ways to transport ammonia in human and Mycobacterium tuberculosis NAD+ synthetases."},
        "34031600": {"first_author": "Tian R", "pubdate": "2021 Jul", "journal": "Nat Neurosci", "title": "Genome-wide CRISPRi/a screens in human neurons link lysosomal failure to ferroptosis."},
        "34972208": {"first_author": "Pasetto L", "pubdate": "2021 Dec 31", "journal": "Brain", "title": "Defective cyclophilin A induces TDP-43 proteinopathy: implications for amyotrophic lateral sclerosis and frontotemporal dementia."},
        "35641224": {"first_author": "Imaizumi K", "pubdate": "2022 May-Jun", "journal": "eNeuro", "title": "Pathogenic Mutation of TDP-43 Impairs RNA Processing in a Cell Type-Specific Manner: Implications for the Pathogenesis of ALS/FTLD."},
        "35953545": {"first_author": "Dräger NM", "pubdate": "2022 Sep", "journal": "Nat Neurosci", "title": "A CRISPRi/a platform in human iPSC-derived microglia uncovers regulators of disease states."},
        "36309631": {"first_author": "Lee JH", "pubdate": "2022 Dec", "journal": "Neurochem Res", "title": "Anti-neuroinflammatory Effects and Brain Pharmacokinetic Properties of Selonsertib, a Selective ASK1 Inhibitor."},
        "38357931": {"first_author": "Szot JO", "pubdate": "2024 Feb 15", "journal": "J Clin Invest", "title": "A metabolic signature for NADSYN1-dependent congenital NAD deficiency disorder."},
        "39548852": {"first_author": "Dellar ER", "pubdate": "2025 Mar", "journal": "Ann Neurol", "title": "Elevated Cerebrospinal Fluid Ubiquitin Carboxyl-Terminal Hydrolase Isozyme L1 in Asymptomatic C9orf72 Hexanucleotide Repeat Expansion Carriers."},
        "39660913": {"first_author": "Xie S", "pubdate": "2025 Jan", "journal": "Protein Sci", "title": "Molecular basis of the CYFIP2 and NCKAP1 autism-linked variants in the WAVE regulatory complex."},
        "40087396": {"first_author": "Omar OMF", "pubdate": "2025 May", "journal": "Nat Neurosci", "title": "Endothelial TDP-43 depletion disrupts core blood-brain barrier pathways in neurodegeneration."},
        "40132594": {"first_author": "Zelic M", "pubdate": "2025 Apr 8", "journal": "Immunity", "title": "Single-cell transcriptomic and functional studies identify glial state changes and a role for inflammatory RIPK1 signaling in ALS pathogenesis."},
        "40713859": {"first_author": "Miedema SSM", "pubdate": "2025 Jul 25", "journal": "Acta Neuropathol Commun", "title": "Proteomics of the temporal cortex in semantic dementia reveals brain-region specific disruption of protein homeostasis."},
        "40737092": {"first_author": "Dargan R", "pubdate": "2025 Jul 19", "journal": "Nucleic Acids Res", "title": "Altered mRNA transport and local translation in i3Neurons with RNA-binding protein knockdown."},
        "40826370": {"first_author": "Feneberg E", "pubdate": "2025 Aug 18", "journal": "Acta Neuropathol Commun", "title": "TDP-43 pathology is associated with divergent protein profiles in ALS brain and spinal cord."},
        "41028049": {"first_author": "Spiteri AG", "pubdate": "2025 Sep 30", "journal": "Sci Rep", "title": "Proteomic analysis of brain and spinal cord tissue reveals distinct immune and mitochondrial dysfunction in amyotrophic lateral sclerosis."},
        "41803120": {"first_author": "Ruf WP", "pubdate": "2026 Mar 9", "journal": "Nat Commun", "title": "Multi-modal dissection of cell-type specific TDP-43 pathology in the motor cortex."},
        "42135847": {"first_author": "Sinha IR", "pubdate": "2026 May 14", "journal": "Mol Neurodegener", "title": "TDP-43: [GU]-ardian of the transcriptome."},
        "42509371": {"first_author": "Ran X", "pubdate": "2026 Sep", "journal": "Nat Med", "title": "Longitudinal plasma proteomics predict phenoconversion to clinically manifest ALS."},
        "42698373": {"first_author": "Pan L", "pubdate": "2026 Sep", "journal": "Eur J Neurol", "title": "Protein Biomarkers in Risk and Prognosis of Amyotrophic Lateral Sclerosis."},
    },
    "ncts": {
        "NCT04834778": {"title": "A Study of HC-5404-FU to Establish the Maximum Tolerated Dose (MTD)", "status": "COMPLETED"},
        "NCT05397665": {"title": "Pharmacodynamic EffIcacy and Clinical Benefit of AT 007 in Patients With Sorbitol Dehydrogenase (SORD) Deficiency", "status": "COMPLETED"},
        "NCT07191912": {"title": "Confirmatory Study of Govorestat in CMT-SORD", "status": "WITHDRAWN"},
        "NCT07321860": {"title": "Safety, Target Engagement, and Preliminary Efficacy of Galunisertib Combined With Nerandomilast in GREM2-positive ALS", "status": "NOT_YET_RECRUITING"},
    },
    "dois": {
        "10.1038/s41598-025-11466-0": {"title": "Proteomic analysis of brain and spinal cord tissue reveals distinct immune and mitochondrial dysfunction in amyotrophic lateral sclerosis.", "type": "journal-article"},
        "10.1038/s41467-019-13845-4": {"title": "Different ways to transport ammonia in human and Mycobacterium tuberculosis NAD+ synthetases.", "type": "journal-article"},
        "10.1038/nature09623": {"title": "Structure and control of the actin regulatory WAVE complex.", "type": "journal-article"},
        "10.1101/2025.09.29.679403": {"title": "Integrative multiomic analysis links TDP-43-driven splicing defects to cascading proteomic disruption of ALS/FTD pathways.", "type": "posted-content"},
        "10.1186/s40478-025-02077-x": {"title": "Proteomics of the temporal cortex in semantic dementia reveals brain-region specific disruption of protein homeostasis.", "type": "journal-article"},
        "10.1093/nar/gkaf709": {"title": "Altered mRNA transport and local translation in i3Neurons with RNA-binding protein knockdown.", "type": "journal-article"},
        "10.1038/s41591-026-04528-x": {"title": "Longitudinal plasma proteomics predict phenoconversion to clinically manifest ALS.", "type": "journal-article"},
        "10.1111/ene.70741": {"title": "Protein Biomarkers in Risk and Prognosis of Amyotrophic Lateral Sclerosis.", "type": "journal-article"},
        "10.1038/s41593-025-01914-5": {"title": "Endothelial TDP-43 depletion disrupts core blood-brain barrier pathways in neurodegeneration.", "type": "journal-article"},
        "10.1523/eneuro.0061-22.2022": {"title": "Pathogenic Mutation of TDP-43 Impairs RNA Processing in a Cell Type-Specific Manner.", "type": "journal-article"},
        "10.1186/s13024-026-00944-2": {"title": "TDP-43: [GU]-ardian of the transcriptome.", "type": "journal-article"},
    },
}

RUN_P4_006_ROW: dict[str, str] = {
    "analysis_run_id": "RUN-P4-006",
    "phase_batch": "Phase4_Final_Synthesis",
    "script_relpath": "work/phase4_final_synthesis/scripts/07_living_intake_v15_nadsyn1_cyfip2_eval.py;work/phase4_final_synthesis/scripts/08_register_living_intake_v15.py",
    "output_artifacts": "work/phase4_final_synthesis/outputs/run_p4_006_living_nadsyn1_cyfip2_eval.json;registries/living_evidence_candidates.csv;registries/living_evidence_candidate_evidence.csv",
    "datasets_used": "DS001_COUNTS;DS001_FEAT;DS_GC_REF;DS001_ONEILL;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;DS003_PB;DS_EDIN_PB;DS031_ZHANG;DS029_SPILL;DS_CRYPTIC;DS_ZENG_APA;DS_BRYCE_APA;DS045_TRAUT;DS_PDB_NADSYN1_CYFIP2",
    "tools_and_skills_used": "gnomad-database;gtex-database;pdb-database;alphafold-database-fetch-and-analyze;tooluniverse-gene-liability;carbon_als.mmcif_parser;carbon_als.loaders;uv-python",
    "reproduced_verified": "yes",
    "run_timestamp_utc": "2026-11-27T18:00:00Z",
    "summary": "Living-evidence multi-cohort omics, GENCODE v46 exon-to-protein mapping, 4-structure 3D mmCIF dissection (PDB 6OFB 2.84A human NADSYN1 octamer + NaAD/AMP/pyrophosphate, PDB 3P8C 2.29A CYFIP1 WAVE regulatory complex, AF-Q6IA69-F1, AF-Q96F07-F1), and 33-cohort external validation benchmark establishing single-gene NADSYN1 (EALS-054) and CYFIP2 (EALS-055) in Tier 3 Exploratory Discovery while confirming 0/16 target-mapped false positives across excluded regimens.",
}

LIVING_CANDIDATE_L02: dict[str, str] = {
    "living_id": "L02",
    "origin_subcohort": "TDP43_SPLICING_APA",
    "gene_or_drug": "NADSYN1",
    "candidate_type": "GENE_CIS_SPLICE",
    "primary_modality_specific": "Intrathecal_2OMOE_Steric_SSO_Intron15_Retention_Rescue_or_PreissHandler_NAD_Flux_Comparison",
    "mechanism_summary": "Glutamine-dependent NAD+ synthetase (ENSG00000172890, MANE_Select ENST00000319023, UniProt Q6IA69 706 aa, PDB 6OFB 2.84A octamer + NaAD/AMP/pyrophosphate; gnomAD v4.1 LOEUF=1.010, pLI=4.63e-23, autosomal recessive VCRL3 OMIM 618845) catalyzing the terminal de novo biosynthesis / Preiss-Handler amidation of NaAD to NAD+ upstream of SARM1 axonolysis",
    "causal_vs_reactive_assessment": "TDP43_INTRON15_RETENTION_DE_NOVO_NAD_DEPLETION_VS_SALVAGE_REDUNDANCY",
    "epistemic_state": "UNPROVEN_UNTESTED",
    "decision": "KEEP_EXPLORATORY_UNPROVEN",
    "clinical_readiness_trl": "TRL_2_PRECLINICAL_MODALITY_DISCOVERY",
    "next_gate_experimental_class": "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
    "primary_evidence_basis": "MEASURED_HUMAN_CNS_PROTEOMICS_AND_SPLICING",
    "model_prior_dependency": "NONE",
    "unsolved_hurdle_count": "4",
    "unsolved_hurdles_structured": "POSTMORTEM_INTRON15_RETENTION_PENETRANCE_AND_INEURON_PROTEIN_PROOF;NAMPT_NMNAT2_SALVAGE_PATHWAY_REDUNDANCY_VS_SARM1_NMN_NAD_GATING;INTRON_RETENTION_AND_COMPLEX_APA_SSO_TRACTABILITY_CEILING;PHYSIOLOGICAL_NICOTINAMIDE_METABOLIC_FLUX_AND_RESCUE_BENCHMARK",
    "scientific_actionability_tier": "TIER_3_EXPLORATORY_DISCOVERY",
    "factual_justification": (
        "[MEASURED] Pan-CNS human sALS protein depletion across all four anatomical regions in Spiteri et al. 2025 TMTpro proteomics (PMID:41028049, DOI:10.1038/s41598-025-11466-0: mean per-region log2FC=-0.5610 [4-region sum contrast -2.244, repeated-donor limma p=5.65e-5, adj p=0.00519]; cervical adj p=0.0214, lumbar adj p=0.0229, motor cortex -0.5361 adj p=0.0163, thoracic -0.5950 adj p=0.00993; while salvage enzyme NAMPT trends upward +0.711 all p=0.0232, thoracic +1.045 p=0.0036), "
        "converging with covariate-adjusted NYGC motor cortex bulk RNA depletion (All ALS vs Control raw -0.4110, Welch p=4.37e-7; GC%+neuron+glia+RIN OLS adj_beta=-0.2548, adj p=0.000381, n=212; spinal cord raw -0.3803, Welch p=9.86e-7, OLS adj_beta=-0.1231, adj p=0.0821, n=232), "
        "Brown et al. 2022 i3Neuron TDP-43 KD unannotated Intron-15 retention (chr11:71484448-71485541: control E[PSI]=0.033 -> KD 0.445, deltaPSI=+0.4255, source MAJIQ 'FDR'=6.85e-20; canonical Exon 15-16 junction chr11:71484447-71485542 drops 0.966 -> 0.450, deltaPSI=-0.5365, source MAJIQ 'FDR'=3.33e-16; PMID:35197628; supplemental splicing mention in Imaizumi 2022 PMID:35641224 and cataloged in Sinha 2026 [Review] PMID:42135847), "
        "GENCODE v46 + 2.84A PDB 6OFB (PMID:31911602, AF-Q6IA69-F1 mean pLDDT=95.92) mapping showing Intron 15 immediately precedes Exon 16 (chr11:71485542-71485648, 107 bp, aa 486-521) which houses six direct <=4.0A catalytic NaAD+/AMP contacts (Arg487 2.11A [2.84A crystal model], Arg489 3.14A, Gln498 3.48A, Leu510 3.11A, Leu511 3.56A, Ser515 3.83A), "
        "PacBio Iso-Seq postmortem BA46 novel isoform shifts (GSE315972 BambuTx1078 mean 1.80 vs 0.00 CPM, BambuTx13669 0.74 vs 0.00 CPM, BambuTx18010 0.00 vs 2.36 CPM; GSE310723 i3N BambuTx1053), Dargan 2025 neurite depletion (-0.3841, Welch p=0.00417, PMID:40737092, GSE299341), Tian 2021 neuronal CRISPRi survival sensitivity (antioxidant-supplemented survival phenotype=-2.92, p=0.0337, PMID:34031600), human autosomal recessive congenital NAD deficiency biology (VCRL3 OMIM 618845, PMID:31883644, PMID:38357931; gnomAD v4.1 MANE LOEUF=1.010, pLI=4.63e-23), and zero claims in major cryptic-exon ASO patent filings (WO2023237638A1, WO2023222858A1, Guo 2026 PMID:42234776), "
        "YET acute Brown 2022 i3Neuron total RNA (+0.481, adj p=2.00e-15) and Ribo-seq (+0.332, adj p=0.999) do not show bulk translation loss, Kozareva 2025 (DOI:10.1101/2025.09.29.679403 [preprint]) Table S6 records postmortem missplicing without cryptic-exon confirmation (3 cryptic-exon and 2 complex-APA annotations; iNeuron protein unmeasured) while Bryce-Smith 2025 Complex APA ENSG00000172890.13_2 is non-selective (100% pathology vs 37.2% non-pathology, PMID:41120751), Spillman 2026 C9-FTD homogenate (-0.171, p=0.500) and synaptosome (-0.227, p=0.300) DIA plus NYGC Visium lumbar ventral horn (-0.088, p=0.437) and Trautwig CSF (0% detected) are null, and neuronal NAD+ synthesis relies predominantly on the NAMPT->NMNAT2 salvage pathway (SARM1 is gated by the NMN/NAD+ ratio rather than NaAD) leaving metabolic non-redundancy and steric-SSO tractability on intron retention unproven."
    ),
    "discriminating_next_test": (
        "(1) Quantify endogenous NADSYN1 Intron-15 retention (chr11:71484448-71485541) and flanking Exon 15-16 full-length protein in sporadic ALS postmortem motor cortex and cervical spinal cord by targeted RT-ddPCR / Oxford Nanopore (ONT) long-read sequencing and targeted parallel-reaction monitoring (PRM) proteomics; "
        "(2) In human TDP-43-depleted iPSC motor neurons cultured under physiological low-nicotinamide media (1-5 uM, avoiding supraphysiological salvage masking) with defined Preiss-Handler (nicotinic acid) versus tryptophan/quinolinic acid de novo biosynthesis precursor controls (given low neuronal QPRT), measure intracellular NADSYN1 protein, NaAD, NMN, NAD+, and axonal cADPR by LC-MS/MS with and without nicotinamide riboside (NR) bypass and head-to-head steric 2'-O-MOE Intron-15 SSO versus small-molecule NAD+ precursor rescue (benchmarking against EALS-030 SARM1 inhibition)."
    ),
    "supporting_living_evidence_ids": "EV-LIV-003;EV-LIV-004",
    "analysis_run_id": "RUN-P4-006",
}

LIVING_CANDIDATE_L03: dict[str, str] = {
    "living_id": "L03",
    "origin_subcohort": "TDP43_SPLICING_APA",
    "gene_or_drug": "CYFIP2",
    "candidate_type": "GENE_CIS_SPLICE",
    "primary_modality_specific": "Intrathecal_2OMOE_Steric_SSO_TDP43_Missplicing_and_Synaptic_WAVE_Complex_Rescue",
    "mechanism_summary": "WAVE regulatory complex (WRC) subunit (ENSG00000055163, MANE_Select ENST00000620254 / UniProt Q96F07-2 1,253 aa vs canonical Q96F07-1 / AF-Q96F07-F1 1,278 aa with +25-aa upstream exon shift, mean pLDDT=86.81, paralog CYFIP1 WRC PDB 3P8C 2.29A; gnomAD v4.1 pLI=1.000, LOEUF=0.274, missense Z=6.94, autosomal dominant DEE65 OMIM 618008) governing Rac1-dependent dendritic/axonal actin remodeling",
    "causal_vs_reactive_assessment": "TDP43_CONSTRAINED_SYNAPTIC_WRC_DEPLETION_VS_CYFIP1_PARALOG_BUFFERING",
    "epistemic_state": "UNPROVEN_UNTESTED",
    "decision": "KEEP_EXPLORATORY_UNPROVEN",
    "clinical_readiness_trl": "TRL_2_PRECLINICAL_MODALITY_DISCOVERY",
    "next_gate_experimental_class": "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
    "primary_evidence_basis": "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
    "model_prior_dependency": "NONE",
    "unsolved_hurdle_count": "4",
    "unsolved_hurdles_structured": "NMD_BLOCKED_LONGREAD_CRYPTIC_COORDINATE_AND_SPINAL_PENETRANCE_PROOF;CYFIP1_COMPENSATORY_PARALOG_BUFFERING_AND_EXPRESSION_RESCUE_EPISTASIS;SPINAL_CORD_BULK_PROTEOME_NULL_AND_DENDRITIC_ATTRITION_CONFOUNDING;UNVALIDATED_2OMOE_STERIC_SSO_WINDOW_AND_DEE65_DOSAGE_CEILING",
    "scientific_actionability_tier": "TIER_3_EXPLORATORY_DISCOVERY",
    "factual_justification": (
        "[MEASURED] Extreme human genetic constraint (gnomAD v4.1 MANE ENST00000620254: pLI=1.000, LOEUF=0.274, 29/144.5 obs/exp LoF, missense Z=6.94; autosomal dominant developmental and epileptic encephalopathy DEE65 OMIM 618008 discovered in Nakashima 2018 PMID:29534297; autism-linked CYFIP2/NCKAP1 WAVE regulatory complex structural modeling in Xie 2025 PMID:39660913; AF-Q96F07-F1 Arg87 hotspot pLDDT=94.69 [invariant across 1,253-aa Q96F07-2 and 1,278-aa Q96F07-1] vs paralog CYFIP1 WRC PDB 3P8C 2.29A PMID:21107423) paired with multi-cohort TDP-43 translation and protein depletion: "
        "Brown et al. 2022 i3Neuron TDP-43 KD Ribo-seq (-1.3743 log2FC, p=5.71e-18, adj p=1.68e-14) and RNA-seq (-0.6688, adj p=1.81e-41, PMID:35197628), Kozareva et al. 2025 (DOI:10.1101/2025.09.29.679403 [preprint]) Table S1 iNeuron protein (-0.4678, p=0.00238, adj p=0.0204) and Table S6 postmortem cryptic-exon confirmation (3 cryptic-exon annotations across ALS-FTD MAJIQ, Sinha NMD-inhibited, and Newton meta-analyses; supplemental splicing mention in Ma 2022 PMID:35197626 and cataloged in Sinha 2026 [Review] PMID:42135847), "
        "Spiteri et al. 2025 human sALS motor cortex TMTpro protein (-0.3042, p=0.00370, adj p=0.0476, PMID:41028049), Miedema et al. 2025 FTLD-TDP Type C temporal cortex DIA protein (-0.3598, q=3.02e-8, PMID:40713859), Dargan et al. 2025 TDP-43 KD neurite depletion (-0.7840, Welch p=0.000111, PMID:40737092, GSE299341), "
        "and human spinal cord RNA depletion in NYGC Visium lumbar ventral horn (GSE330224 n=24 ALS vs 8 Ctrl: raw -0.6792, Welch p=0.00174, MWU p=0.00202; complete-covariate gc+sex+age+pmi OLS n=25 [20 ALS vs 5 Ctrl] adj_beta=-0.8613, adj p=0.00777 without neuronal-proportion adjustment), NYGC bulk spinal cord (All ALS vs Ctrl OLS adj_beta=-0.1276, adj p=0.00224, n=232), and NYGC lumbar spinal microglia (GSE330130 n=11 vs 9: -0.7796, Welch p=0.00510, OLS adj p=0.0290; ambient neuronal RNA caveat), with zero standalone chemical-SSO patents (genus-listed without worked examples in U7 filing WO2023237638A1), "
        "YET non-NMD-blocked Brown 2022 MAJIQ shows modest steady-state Exon 19-20 canonical loss (chr5:157328049-157330742, MANE aa 694-755 / canonical Q96F07-1 aa 719-780: 1.000 -> 0.854, deltaPSI=-0.1191, source MAJIQ 'FDR'=4.03e-6) and retention of the distal 515-bp segment of 2,692-bp Intron 19 downstream of a novel donor at chr5:157330227 (chr5:157330227-157330741 within full Intron 19 chr5:157328050-157330741: 0.000 -> 0.106, deltaPSI=+0.0784, source MAJIQ 'FDR'=9.66e-5), Spiteri 2025 spinal cord bulk TMTpro regions (cervical adj p=0.974, lumbar adj p=0.976, thoracic adj p=0.702), Spillman 2026 C9-FTD synaptosomes (-0.282, p=0.113) and homogenate (+0.042, p=0.764), NYGC motor cortex bulk (adj p=0.519), and Trautwig CSF (0% detected) are null, while paralog CYFIP1 (LOEUF=0.440) is reciprocally upregulated across Kozareva 2025 (preprint) S1 iNeurons (+0.9291, adj p=0.00362), Miedema FTLD-TDP-C (+0.2639, q=1.31e-7), and Spillman C9-FTD homogenates (+0.2735, p=0.0373), leaving functional non-redundancy, exact NMD-sensitive cryptic coordinates, and neuronal/synaptic attrition confounding (including unadjusted Visium composition and microglial ambient RNA) unproven."
    ),
    "discriminating_next_test": (
        "(1) Map exact NMD-sensitive CYFIP2 cryptic-exon and Intron-19 coordinates (spanning full Intron 19 chr5:157328050-157330741 and the distal 515-bp boundary at chr5:157330227) plus full-length PSI by SMG1-inhibitor / cycloheximide-treated Oxford Nanopore (ONT) long-read sequencing in TDP-43-depleted human iPSC motor neurons and validate junction penetrance in human ALS motor cortex and lumbar ventral horn (with neuronal-proportion residualization); "
        "(2) Perform isoform-matched CYFIP2 cDNA / steric-SSO rescue in TDP-43-depleted human iPSC motor neurons (holding STMN2 and UNC13A constant) while measuring whether reciprocal endogenous CYFIP1 upregulation (+0.93 log2FC) buffers WAVE regulatory complex actin/synaptic morphology and verifying physiological dosage bounds against DEE65 gain-of-function/destabilization toxicity."
    ),
    "supporting_living_evidence_ids": "EV-LIV-005;EV-LIV-006",
    "analysis_run_id": "RUN-P4-006",
}
