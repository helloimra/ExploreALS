"""Evidence, SHA-256 statistical contrast, and Living Research Log specs (UPD-2026-11-26-02) for ExploreALS v1.4.0 EALS-053."""
from __future__ import annotations

LIVING_EVIDENCE_ROWS: list[dict[str, str]] = [
    {
        "evidence_id": "EV-LIV-001",
        "carbon_id": "L01",
        "subnode_id": "",
        "analysis_run_id": "RUN-P4-005",
        "source_type": "PRIMARY_TRANSCRIPTOMIC_RECOMPUTE",
        "source_id_or_locator": "DS001_COUNTS;DS001_ONEILL;DS_EDIN_PB;DS031_ZHANG;DS_ZENG_APA;DS_BRYCE_APA;DS045_TRAUT;PMID:36482247;PMID:40375307",
        "cohort_and_stratum": "NYGC postmortem spinal cord ALS-Glia vs Control (125 ALS-Glia vs 43 Control, n=168 within N=232 unique donors) + genotype & 7-cohort cross-check",
        "assay_and_contrast": "Donor-level GC% + neuronal/glial + RIN OLS on NYGC spinal cord CGAS (ALS-Glia vs Control) + genotype-stratified & cortical/CSF checks",
        "effect_direction": "SPINAL_ALS_GLIA_ELEVATION_WITH_C9NEG_AND_SOD1_MICROGLIOSIS_CAVEATS",
        "effect_estimate": "adj_beta=+0.4779 log2CPM (raw_diff=+0.3396; All ALS adj_beta=+0.3510, p=2.76e-5, n=232; C9-ALS +0.4438, p=0.00104, n=72; PCR-confirmed C9-neg +0.1492, adj_p=0.0909, n=163)",
        "p_value": "1.693e-06",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "168",
        "epistemic_weight": "HIGH",
        "notes": (
            "Raw Welch p=0.0001839; ALS-Glia vs ALS-Ox adj_beta=+0.2496 (adj_p=0.00347, n=189, AUC=0.7221); broad non-C9 non-SOD1 vs Control adj_beta=+0.3403 (adj_p=1.30e-4, n=199) "
            "attenuates in strict PCR-confirmed C9=='No' (n=120 vs 43: raw +0.1454, MWU p=0.0134, Welch p=0.0860, adj_p=0.0909 while IFI16 +0.4023 adj_p=4.79e-5 & PSMB8 adj_p=4.96e-6 stay elevated), "
            "and TDP-43-negative SOD1 cord (n=4 vs 43, 4/4 ALS-Glia) shows raw +0.3625 (MWU p=0.0242, adj_p=0.0898); NYGC motor cortex flat (All ALS adj_p=0.608, n=212; ALS-TE vs ALS-Ox +0.1264, adj_p=0.0451, n=153); "
            "Edinburgh cortical microglia Welch p=0.727 (n=33); Zhang 2026 Visium CGAS absent vs IFI16 MN-niche +0.8911 (p=0.00973, BH=0.0709); 0 cryptic/APA shifts (Brown/Zeng/Bryce-Smith); 0% CSF detection in Trautwig 2025 (N=259 DIA, N=101 TMT). [Sample context: 125 ALS-Glia vs 43 Control unique NYGC spinal donors]"
        ),
    },
    {
        "evidence_id": "EV-LIV-002",
        "carbon_id": "L01",
        "subnode_id": "",
        "analysis_run_id": "RUN-P4-005",
        "source_type": "STRUCTURAL_AND_GENE_LIABILITY_SYNTHESIS",
        "source_id_or_locator": "DS_PDB_CGAS_STING;DS_GNOMAD_V41_CONSTRAINT;PMID:31113940;PMID:30007416;PMID:41809005;PMID:27830700;NCT07260877",
        "cohort_and_stratum": "RCSB PDB 6MJW (2.41A human CGAS+G150) & comparator 6LRC/6NT5/4KSY/6MXE structures + gnomAD v4.1 / DepMap / ClinicalTrials.gov NCT07260877",
        "assay_and_contrast": "Heavy-atom <=4.0A ligand contact & human Q8N884 vs mouse Q8C6L5 pocket alignment + gnomAD v4.1 / GTEx v8 / DepMap safety & TDI-6570/VENT-03 PK review",
        "effect_direction": "DRUGGABLE_LOF_TOLERANT_POCKET_WITH_ORTHOLOG_AND_CNS_KPUU_GAPS",
        "effect_estimate": "PDB 6MJW G150 (IC50=10.2 nM): 13 contacts <=4.0A (10/13 conserved, 3/13 human-mouse divergent: hTyr248->mPhe234 3.09A, hSer434->mCys419 3.08A, hAsn482->mHis467 3.24A); LOEUF=1.529; Chronos=-0.1013",
        "p_value": "",
        "fdr_or_adjusted_p": "",
        "sample_size_n": "",
        "epistemic_weight": "HIGH_STRUCTURAL",
        "notes": (
            "PDB 6MJW (2.405A, K427E/K428E construct, Lama 2019 PMID:31113940) vs 68.31% human-mouse catalytic identity (aa 157-522) + K187->N172 / L195->R180 dsDNA-length spine (PMID:30007416); "
            "6LRC PF-06928215 (1.831A, TPSA=111 A^2, PMID:32459092); mouse-active micromolar TDI-6570 (CID:137943015, TPSA=45.5 A^2, Liu 2026 PMID:41809005 [PREPRINT] PMC12970331) unmeasured on human CNS Kp,uu; "
            "Ventus VENT-03 Phase 2a CLE/SLE NCT07260877 (N=24, ACTIVE_NOT_RECRUITING) has undisclosed structure, 0 CSF endpoints & excludes active NPSLE; "
            "CGAS MANE ENST00000370315 pLI=2.80e-10, LOEUF=1.529 (0 common pocket alleles vs 4 common STING1 R232H/G230A/R293Q/R71H alleles up to 41.5% EAS; PDB 6NT5/4KSY/6MXE), GTEx Heart 0.55 / Liver 0.47 / Cortex 0.50 TPM, MGI:4435548 viable with HSV-1 CNS caution (PMID:27830700)."
        ),
    },
]

LIVING_STAT_SPECS: list[dict[str, str]] = [
    {
        "evidence_id": "EV-LIV-001",
        "analysis_run_id": "RUN-P4-005",
        "inference_class": "PRIMARY_FREQUENTIST_RECOMPUTE",
        "statistical_unit": "unique_human_donor",
        "n_statistical_units": "168",
        "n_unique_donors_or_participants": "168",
        "exact_contrast": "NYGC postmortem spinal cord ALS-Glia (n=125) vs Control (n=43; n=168 unique donors within N=232 motor-ALS/Control cord pool; exclude_pure_ftd=True) | Donor-collapsed CGAS log2(CPM+1) Welch t-test & GC%+neuron+glia+RIN OLS (+ genotype-stratified C9orf72/C9-neg/SOD1 sensitivity)",
        "model_formula_or_test": "Two-sided Welch t-test & donor-level OLS: CGAS_log2CPM ~ ALS_Glia_vs_Ctrl + sample_gc_index + neuron_idx + glia_idx + RIN (1 row per unique Patient ID)",
        "effect_metric": "unadjusted_diff_and_covariate_adjusted_OLS_beta_log2CPM",
        "effect_estimate": "ALS-Glia vs Ctrl raw_diff=+0.3396, OLS adj_beta=+0.4779 (All ALS +0.3510, adj_p=2.76e-5, n=232; C9orf72 +0.4438, adj_p=0.00104, n=72; PCR-confirmed C9-neg +0.1492, adj_p=0.0909, n=163; SOD1 n=4 raw +0.3625, MWU p=0.0242; Motor Cortex All ALS adj_p=0.608, n=212)",
        "se_or_ci95": "",
        "unadjusted_or_primary_nominal_p": "0.0001839",
        "covariate_adjusted_nominal_p": "1.693e-06",
        "multiplicity_adjusted_p": "",
        "multiple_testing_family": "Targeted 17-gene cytosolic DNA-sensing / IFN-I / immunoproteasome panel donor-level OLS (nominal OLS p reported)",
        "missingness_or_exclusion_rule": "Pure FTD excluded (ALS, ALS+FTD, Control retained); multi-segment cervical/lumbar/thoracic libraries averaged to 1 observation per unique Patient ID before Welch/OLS",
        "overlap_group_id": "OVL_NYGC_POSTMORTEM",
        "anchor_type": "STAGED_DATASET",
        "anchor_relpath": "data/transcriptomics/nygc_d001/NYGC_counts.txt.gz",
    },
    {
        "evidence_id": "EV-LIV-002",
        "analysis_run_id": "RUN-P4-005",
        "inference_class": "DESCRIPTIVE_PK_OR_3D_MEASUREMENT",
        "statistical_unit": "crystal_structure_entry_and_ortholog_alignment",
        "n_statistical_units": "5",
        "n_unique_donors_or_participants": "",
        "exact_contrast": "5 RCSB experimental mmCIF structures (human CGAS 6MJW [2.405A + G150 JUJ, K427E/K428E construct] & 6LRC [1.831A + PF-06928215] vs human STING1 6NT5/4KSY/6MXE) + global human Q8N884 vs mouse Q8C6L5 alignment + gnomAD v4.1 / DepMap / NCT07260877 | <=4.0A pocket conservation & CNS PK gap",
        "model_formula_or_test": "[X-ray crystal PDB 6MJW/6LRC & cryo-EM/X-ray 6NT5/4KSY/6MXE] heavy-atom <=4.0A Euclidean contact enumeration + Needleman-Wunsch Q8N884/Q8C6L5 ortholog mapping + gnomAD v4.1/DepMap/CT.gov descriptive lookup",
        "effect_metric": "pocket_contacts_le_4A_ortholog_identity_and_LOEUF",
        "effect_estimate": "PDB 6MJW G150: 13 contacts <=4.0A (10/13 conserved vs mouse Q8C6L5 [68.31% aa 157-522], 3/13 divergent: Tyr248->Phe234 3.09A, Ser434->Cys419 3.08A, Asn482->His467 3.24A); CGAS LOEUF=1.529, DepMap Chronos=-0.1013 (1,258 lines); VENT-03 NCT07260877 0 CSF endpoints",
        "se_or_ci95": "",
        "unadjusted_or_primary_nominal_p": "",
        "covariate_adjusted_nominal_p": "",
        "multiplicity_adjusted_p": "",
        "multiple_testing_family": "NOT_APPLICABLE_NON_FREQUENTIST",
        "missingness_or_exclusion_rule": "Waters/ions excluded from heavy-atom ligand contacts; PDB 6MJW engineered K427E/K428E crystallization substitutions (>15A from JUJ) explicitly annotated against canonical UniProt Q8N884",
        "overlap_group_id": "NONE_INDEPENDENT_OR_EXTERNAL",
        "anchor_type": "DETERMINISTIC_MODEL_OUTPUT",
        "anchor_relpath": "work/phase4_final_synthesis/outputs/run_p4_005_living_sting1_cgas_eval.json",
    },
]

UPD_2026_11_26_02: dict[str, str] = {
    "update_id": "UPD-2026-11-26-02",
    "date_iso": "2026-11-26",
    "release_tag": "v1.4.0",
    "update_category": "LITERATURE_INGESTION",
    "affected_ids": "EALS-053;EALS-019;EALS-033",
    "decision_impact": "Portfolio Expanded 52 -> 53 Hypotheses: Single-Gene Human CGAS (EALS-053) Added at #23/53 (Tier 3 · Keep · Exploratory) Ahead of STING1 & Excluded TBK1",
    "headline": "Living-Evidence Target Selection: Single-Gene Human CGAS (EALS-053) Added on Cytosolic DNA-Sensing Axis Following 7-Cohort Omics, Ortholog 3D Pocket & Safety Triage",
    "prior_state_or_assumption": (
        "Preclinical ALS studies linking TDP-43 mitochondrial DNA release (Yu 2020 PMID:33031745), myeloid C9orf72 loss (McCauley 2020 PMID:32814898), "
        "neuronal DNA-damage signaling (Marques 2024 PMID:38478117), and microglial cGAS inhibition (Liu 2026 PMID:41809005 [PREPRINT]) to cGAS-STING activation "
        "frequently treat STING1, cGAS, and TBK1 interchangeably and extrapolate rodent tool inhibitors (H-151, TDI-6570) or systemic lupus candidates (VENT-03) "
        "to sporadic human ALS without separating bulk spinal microgliosis from 2'3'-cGAMP catalysis, human STING1 coding haplotypes, or human-mouse cGAS active-site divergence."
    ),
    "new_evidence_or_revision": (
        "(1) Target Selection (Single-Gene Human CGAS Over STING1 & TBK1): across 5 experimental structures (PDB 6MJW, 6LRC, 6NT5, 4KSY, 6MXE), gnomAD v4.1, GTEx v8, and DepMap, "
        "upstream enzymatic CGAS (ENSG00000164430, MANE LOEUF=1.529, pLI=2.80e-10, 1,258-line median Chronos=-0.1013, Heart 0.55 / Liver 0.47 / Cortex 0.50 TPM) "
        "avoids TBK1 ALSFTD4 haploinsufficiency (LOEUF=0.505, PMID:25803835), spares cell-autonomous neuronal TBK1->IFN-beta->PSMB8 clearance of monomeric TDP-43 (Sakai 2026 PMID:42834122), "
        "and bypasses STING1's 4 common human coding polymorphisms (R232H rs1131769 12.9%, R71H rs11554776 13.8%, G230A rs78233829 up to 41.5% EAS, R293Q rs7380824 20.4%) "
        "and high vascular/pulmonary expression (Lung 139.4, Aorta 118.8 TPM); "
        "(2) Multi-Cohort & Genotype-Stratified Human ALS Re-Analysis (RUN-P4-005): NYGC spinal cord ALS-Glia elevates CGAS vs. Control (raw +0.3396, Welch p=1.84e-4; "
        "GC%+neuron+glia+RIN OLS adj_beta=+0.4779, adj_p=1.69e-6, n=168; All ALS +0.3510, adj_p=2.76e-5, n=232; C9orf72-ALS +0.4438, adj_p=0.00104, n=72), "
        "yet attenuates in strict PCR-confirmed C9-negative non-SOD1 ALS (n=120 vs. 43: raw +0.1454, MWU p=0.0134, adj_p=0.0909 while co-sensor IFI16 +0.4023 adj_p=4.79e-5 stays elevated) "
        "and rises raw in TDP-43-negative SOD1 cord (n=4: +0.3625, MWU p=0.0242), while NYGC motor cortex (All ALS adj_p=0.608, n=212), Edinburgh microglia (p=0.727), "
        "Brown/Zeng/Bryce-Smith cryptic/3'-UTR APA (0 shifts), and Trautwig CSF (0% detected) are null/absent; "
        "(3) 3D Ortholog & Clinical-PK Boundaries: in 2.41A PDB 6MJW (human CGAS+G150, PMID:31113940), 3/13 contacts <=4.0A diverge between human Q8N884 and mouse Q8C6L5 "
        "(Tyr248->Phe234 3.09A, Ser434->Cys419 3.08A, Asn482->His467 3.24A + K187/L195 DNA-spine PMID:30007416), and Phase 2a lupus VENT-03 (NCT07260877, N=24) collects 0 CSF endpoints and excludes active CNS lupus."
    ),
    "portfolio_and_gate_consequence": (
        "Expands ExploreALS v1.4.0 from 52 to 53 hypotheses by adding single-gene human CGAS (EALS-053) in dedicated living-evidence registries at Priority #23/53 "
        "(Evidence #23, Keep · Exploratory, Tier 3 · Exploratory Discovery, Preclinical Modality, 4 validation steps; Ranks #1–#22 including all 8 Flagship Monographs and #19 EALS-033 are unchanged, "
        "while prior Ranks #23–#52 shift by +1 to #24–#53, e.g., EALS-020 #24 and EALS-019 #25); gated on LC-MS/MS spinal/co-culture 2'3'-cGAMP proof beyond reactive microgliosis, "
        "PDB 6MJW human-pocket potency bridging vs. mouse TDI-6570 (CID:137943015), unbound human/NHP CNS Kp,uu>=0.30, and head-to-head CGAS vs. IFI16 vs. STING1 epistasis + HSV-1 safety (PMID:27830700)."
    ),
    "primary_sources": (
        "PMID:31113940;PMID:33031745;PMID:32814898;PMID:38478117;PMID:41809005;PMID:42834122;PMID:30007416;"
        "PMID:30842659;PMID:23747010;PMID:30655953;PMID:32459092;PMID:27830700;PMID:36482247;PMID:40375307;"
        "10.1186/s40478-026-02474-w;10.64898/2026.02.24.707791;NCT07260877"
    ),
    "verification_anchor": "EV-LIV-001;EV-LIV-002;RUN-P4-005;RUN-P4-001;RUN-P4-002",
}
