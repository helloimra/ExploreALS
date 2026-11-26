"""Specifications for ExploreALS v1.4.0 Living-Evidence Target Intake EALS-053 (L01, atomic CGAS) & UPD-2026-11-26-02."""
from __future__ import annotations

VERIFIED_CITATIONS_V14: dict[str, dict[str, dict[str, str]]] = {
    "pmids": {
        "18724357": {"first_author": "Ishikawa H", "pubdate": "2008 Oct 2", "journal": "Nature", "title": "STING is an endoplasmic reticulum adaptor that facilitates innate immune signalling."},
        "23747010": {"first_author": "Zhang X", "pubdate": "2013 Jul 25", "journal": "Mol Cell", "title": "Cyclic GMP-AMP containing mixed phosphodiester linkages is an endogenous high-affinity ligand for STING."},
        "27830700": {"first_author": "Reinert LS", "pubdate": "2016 Nov 10", "journal": "Nat Commun", "title": "Sensing of HSV-1 by the cGAS-STING pathway in microglia orchestrates antiviral defence in the CNS."},
        "29973723": {"first_author": "Haag SM", "pubdate": "2018 Jul", "journal": "Nature", "title": "Targeting STING with covalent small-molecule inhibitors."},
        "30007416": {"first_author": "Zhou W", "pubdate": "2018 Jul 12", "journal": "Cell", "title": "Structure of the Human cGAS-DNA Complex Reveals Enhanced Control of Immune Surveillance."},
        "30655953": {"first_author": "Siu T", "pubdate": "2019 Jan 10", "journal": "ACS Med Chem Lett", "title": "Discovery of a Novel cGAMP Competitive Ligand of the Inactive Form of STING."},
        "30842659": {"first_author": "Shang G", "pubdate": "2019 Mar", "journal": "Nature", "title": "Cryo-EM structures of STING reveal its mechanism of activation by cyclic GMP-AMP."},
        "31113940": {"first_author": "Lama L", "pubdate": "2019 May 21", "journal": "Nat Commun", "title": "Development of human cGAS-specific small-molecule inhibitors for repression of dsDNA-triggered interferon expression."},
        "32459092": {"first_author": "Zhao W", "pubdate": "2020 Jun 22", "journal": "J Chem Inf Model", "title": "In Silico Screening-Based Discovery of Novel Inhibitors of Human Cyclic GMP-AMP Synthase: A Cross-Validation Study of Molecular Docking and Experimental Testing."},
        "32814898": {"first_author": "McCauley ME", "pubdate": "2020 Sep", "journal": "Nature", "title": "C9orf72 in myeloid cells suppresses STING-induced inflammation."},
        "34099558": {"first_author": "Hong Z", "pubdate": "2021 Jun 15", "journal": "Proc Natl Acad Sci U S A", "title": "STING inhibitors target the cyclic dinucleotide binding pocket."},
        "38478117": {"first_author": "Marques C", "pubdate": "2024 Mar 13", "journal": "Acta Neuropathol", "title": "Neuronal STING activation in amyotrophic lateral sclerosis and frontotemporal dementia."},
        "41809005": {"first_author": "Liu Y", "pubdate": "2026 Feb 26", "journal": "bioRxiv", "title": "cGAS inhibition delays TDP-43-driven ALS Pathogenesis."},
        "42792593": {"first_author": "Zhan Y", "pubdate": "2026 Sep 18", "journal": "Biology (Basel)", "title": "Host Genetic Susceptibility and Antiviral Immunity Shape the Pathogenesis and Outcomes of Herpes Simplex Encephalitis."},
    },
    "ncts": {
        "NCT07260877": {
            "title": "A Multicenter, Randomized, Double-Blind, Placebo-Controlled, Phase 2a Study With an Open-Label Extension Evaluating the Efficacy and Safety of VENT-03 in Adult Participants With Active Cutaneous Lupus Erythematosus With or Without Systemic Lupus Erythematosus",
            "status": "ACTIVE_NOT_RECRUITING",
        },
    },
    "dois": {
        "10.1038/s41467-019-08620-4": {"title": "Development of human cGAS-specific small-molecule inhibitors for repression of dsDNA-triggered interferon expression.", "type": "journal-article"},
        "10.1016/j.cell.2018.06.026": {"title": "Structure of the Human cGAS-DNA Complex Reveals Enhanced Control of Immune Surveillance.", "type": "journal-article"},
        "10.1016/j.cell.2020.09.020": {"title": "TDP-43 Triggers Mitochondrial DNA Release via mPTP to Activate cGAS/STING in ALS.", "type": "journal-article"},
        "10.1038/s41586-020-2625-x": {"title": "C9orf72 in myeloid cells suppresses STING-induced inflammation.", "type": "journal-article"},
        "10.1007/s00401-024-02688-z": {"title": "Neuronal STING activation in amyotrophic lateral sclerosis and frontotemporal dementia.", "type": "journal-article"},
        "10.64898/2026.02.24.707791": {"title": "cGAS inhibition delays TDP-43-driven ALS Pathogenesis.", "type": "posted-content"},
    },
}

RUN_P4_005_ROW: dict[str, str] = {
    "analysis_run_id": "RUN-P4-005",
    "phase_batch": "Phase4_Final_Synthesis",
    "script_relpath": "work/phase4_final_synthesis/scripts/05_living_intake_sting1_cgas_eval.py;work/phase4_final_synthesis/scripts/06_register_living_intake_eals053.py",
    "output_artifacts": "work/phase4_final_synthesis/cache/living_sting1_cgas_external_priors.json;work/phase4_final_synthesis/outputs/run_p4_005_living_sting1_cgas_eval.json;registries/living_evidence_candidates.csv;registries/living_evidence_candidate_evidence.csv",
    "datasets_used": "DS001_COUNTS;DS001_FEAT;DS_GC_REF;DS001_ONEILL;DS_GNOMAD_V41_CONSTRAINT;DS003_PB;DS_EDIN_PB;DS031_ZHANG;DS029_SPILL;DS_CRYPTIC;DS_ZENG_APA;DS_BRYCE_APA;DS045_TRAUT;DS_PDB_CGAS_STING",
    "tools_and_skills_used": "gnomad-database;gtex-database;chembl-database;pubchem-database;clinical-trials-database;pdb-database;tooluniverse-gene-liability;carbon_als.mmcif_parser;uv-python",
    "reproduced_verified": "yes",
    "run_timestamp_utc": "2026-11-26T09:14:30Z",
    "summary": "Living-evidence 7-cohort human ALS omics (incl. NYGC genotype-stratified spinal/cortical contrasts & staged 3'-UTR APA check), 5-structure RCSB mmCIF (PDB 6MJW 2.41A human CGAS+G150 vs mouse Q8C6L5 pocket conservation, 6LRC, 6NT5, 4KSY, 6MXE), and gene-inhibition safety evaluation establishing single-gene human CGAS (EALS-053) in Tier 3 ahead of STING1 and excluded TBK1.",
}

LIVING_CANDIDATE_L01: dict[str, str] = {
    "living_id": "L01",
    "origin_subcohort": "CNS_TISSUE_OMICS",
    "gene_or_drug": "CGAS",
    "candidate_type": "GENE_DRUG_AXIS",
    "primary_modality_specific": "Oral_Brain_Penetrant_Human_Active_Site_CGAS_Small_Molecule_Inhibitor",
    "mechanism_summary": "Cytosolic dsDNA/mtDNA nucleotidyltransferase (ENSG00000164430, MANE_Select ENST00000370315, UniProt Q8N884 522 aa, PDB 6MJW 2.41A active-site G150; gnomAD v4.1 LOEUF=1.529, pLI=2.80e-10) synthesizing 2'3'-cGAMP upstream of STING1 while sparing cell-autonomous neuronal TBK1->IFN-beta->PSMB8 monomeric TDP-43 clearance (PMID:42834122)",
    "causal_vs_reactive_assessment": "UPSTREAM_CYTOSOLIC_DNA_SENSOR_VS_REACTIVE_CORD_MICROGLIOSIS",
    "epistemic_state": "UNPROVEN_UNTESTED",
    "decision": "KEEP_EXPLORATORY_UNPROVEN",
    "clinical_readiness_trl": "TRL_2_PRECLINICAL_MODALITY_DISCOVERY",
    "next_gate_experimental_class": "DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE",
    "primary_evidence_basis": "MEASURED_HUMAN_SPATIAL_OR_SNRNA",
    "model_prior_dependency": "NONE",
    "unsolved_hurdle_count": "4",
    "unsolved_hurdles_structured": "CORD_MICROGLIOSIS_CONFOUNDING_AND_C9NEG_SALS_23CGAMP_PROOF;HUMAN_VS_MOUSE_6MJW_SER434_TYR248_ASN482_POCKET_DIVERGENCE;UNMEASURED_HUMAN_CNS_KP_UU_AND_CSF_PD_BIOMARKER_GAP;CGAS_VS_IFI16_VS_STING1_SELECTIVITY_AND_CNS_HSV1_SAFETY",
    "scientific_actionability_tier": "TIER_3_EXPLORATORY_DISCOVERY",
    "factual_justification": (
        "[MEASURED] Covariate-adjusted NYGC spinal cord ALS-Glia vs Control CGAS upregulation (raw +0.3396 log2CPM, Welch p=0.0001839; GC%+neuron+glia+RIN OLS adj_beta=+0.4779, adj_p=1.693e-6, n=168 [125 ALS-Glia vs 43 Ctrl]; All ALS vs Control adj_beta=+0.3510, adj_p=2.755e-5, n=232; ALS-Glia vs ALS-Ox adj_beta=+0.2496, adj_p=0.00347, AUC=0.7221; C9orf72-ALS vs Control adj_beta=+0.4438, adj_p=0.00104, n=72, PMID:36482247), convergent preclinical ALS & microglial rescue benchmarks (TDP-43 mtDNA->cGAS-STING1 PMID:33031745; myeloid C9orf72 STING1 PMID:32814898; neuronal STING1 PMID:38478117; and mouse-active micromolar brain-penetrant cGAS tool TDI-6570 CID:137943015 rescuing TDP-43 Q331K mouse splicing & iPSC microglia-MN co-cultures in Liu et al. 2026 PMID:41809005 [PREPRINT], PMC12970331), 2.41A human CGAS+G150 active-site crystallography (PDB 6MJW PMID:31113940, CHEMBL4448176 IC50=10.2 nM) & human LoF tolerance (gnomAD v4.1 LOEUF=1.529, 26/23.6 obs/exp LoF, 0 common active-site polymorphisms vs 4 common STING1 R232H/G230A/R293Q/R71H alleles up to 41.5% EAS; DepMap 1,258 lines median Chronos=-0.1013; low parenchymal GTEx v8 Heart 0.55 / Liver 0.47 / Cortex 0.50 / Cervical cord 2.23 TPM vs STING1 Lung 139.4 / Aorta 118.8 TPM; sparing neuronal TBK1->IFN-beta->PSMB8 monomeric TDP-43 turnover PMID:42834122), "
        "YET genotype-stratified NYGC spinal cord attenuates in PCR-confirmed C9orf72-negative non-SOD1 ALS vs Control (n=163 [120 vs 43]: raw +0.1454, MWU p=0.0134, Welch p=0.0860, adj_beta=+0.1492, adj_p=0.0909 while IFI16 +0.4023 adj_p=4.79e-5 & PSMB8 adj_p=4.96e-6 stay elevated) and rises raw in TDP-43-negative SOD1-ALS cord (n=4 vs 43, 4/4 ALS-Glia-cord: +0.3625, MWU p=0.0242, adj_p=0.0898, showing bulk CGAS mRNA tracks microgliosis without proving 2'3'-cGAMP catalysis), flat NYGC motor cortex (All ALS vs Control adj_p=0.608, n=212; Edinburgh cortical microglia Welch p=0.727, n=33; Zhang 2026 cervical Visium CGAS non-significant vs IFI16 MN-niche +0.8911, p=0.00973, BH=0.0709; 0 cryptic/3'-UTR APA shifts across Brown 2022, Zeng 2025 & Bryce-Smith 2025; 0% CSF CGAS/STING1/IFI16 detection in Trautwig 2025 N=259 DIA & N=101 TMTpro, PMID:40375307), 3/13 human-vs-mouse G150 <=4.0A pocket contacts diverge in PDB 6MJW (hTyr248->mPhe234 3.09A, hSer434->mCys419 3.08A, hAsn482->mHis467 3.24A at 68.3% catalytic identity + K187/L195 dsDNA-length spine PMID:30007416, blocking unbridged mouse TDI-6570 extrapolation), and clinical cGAS inhibitor VENT-03 (Phase 2a lupus NCT07260877, N=24) has undisclosed structure, 0 CSF endpoints, active NPSLE exclusion, and CNS HSV-1 antiviral caution (MGI:4435548, PMID:27830700)."
    ),
    "discriminating_next_test": (
        "(1) Quantify endogenous 2'3'-cGAMP by LC-MS/MS alongside pSTING1-Ser366 across C9orf72, PCR-verified C9-negative sporadic ALS, and SOD1-ALS postmortem spinal cord and patient iPSC microglia-motor neuron co-cultures under cytoplasmic TDP-43/mtDNA stress (separating catalytic cGAS activation from reactive microgliosis); "
        "(2) Execute head-to-head CRISPRi and chemical epistasis comparing human-active cGAS inhibition (bridging PDB 6MJW Ser434/Tyr248/Asn482 human pocket potency vs mouse-active TDI-6570 CID:137943015 PMID:41809005 [PREPRINT] and polar PF-06928215 PDB 6LRC TPSA=111 A^2) against co-sensor IFI16 knockdown and haplotype-panel STING1 antagonists (R232/R232, H232, HAQ; PDB 6NT5/4KSY/6MXE), co-measuring preserved neuronal TBK1->IFN-beta->PSMB8 monomeric TDP-43 clearance (PMID:42834122), unbound human/NHP CNS Kp,uu>=0.30, and microglial HSV-1 DNA-virus defense (PMID:27830700)."
    ),
    "supporting_living_evidence_ids": "EV-LIV-001;EV-LIV-002",
    "analysis_run_id": "RUN-P4-005",
}
