"""ExploreALS v1.3.0 Living Research Log specification (UPD-2026-11-23-01) for primary-source retrospective & consequent remediation."""
from __future__ import annotations

UPD_2026_11_23_01: dict[str, str] = {
    "update_id": "UPD-2026-11-23-01",
    "date_iso": "2026-11-23",
    "release_tag": "v1.3.0",
    "update_category": "MODEL_REVISION",
    "affected_ids": (
        "EALS-030;EALS-031;EALS-001;EALS-006;EALS-002;EALS-007;EALS-034;EALS-037;"
        "EALS-036;EALS-015;EALS-018;EALS-020;EALS-013;EALS-044;EALS-004;EALS-008;"
        "EALS-009;EALS-010;EALS-021;EALS-025;EALS-048"
    ),
    "decision_impact": (
        "All 52 Triage Verdicts, Ranks & 28 Cis-Regulatory Classifications Confirmed; "
        "Primary-Source Splicing, Structural, Trial-Denominator & 202-Contrast Provenance Remediated"
    ),
    "headline": (
        "Cross-Portfolio Primary-Source Retrospective & Consequent Quantitative, "
        "Structural, Clinical-Denominator & Workbench Remediation"
    ),
    "prior_state_or_assumption": (
        "(1) Cryptic Splicing, Modality Separation & Population Constraint (EALS-006, EALS-001, EALS-034, EALS-037, EALS-036): "
        "prior KCNQ2 (EALS-006) annotations grouped stem-cell neuron TDP-43 knockdowns with postmortem C9orf72 ALS/FTD nuclear-fraction RNA-seq "
        "without noting their shared GSE126543 origin, sample-level NYGC library proportions vs. Mayo IHC case-control and within-FTLD-TDP biochemical pTDP-43 counts, PDB 7CR2 atom-pair contact distances, or gnomAD v4.1 vs. v4.1.1 MANE pLI/LOEUF constraint "
        "across flagship monographs (EALS-030, EALS-001, EALS-006, EALS-002, EALS-007, EALS-034, EALS-037), while MAJIQ exports (Brown 2022 MOESM11) rename Bayesian "
        "p_d_psi_0.05 posterior tails as 'FDR', PTPRT (EALS-036) lacked Intron-26 737-bp A3SS coordinate windows, and non-significant Spillman 2026 synaptosome DIA shifts "
        "were phrased as unchanged rather than non-significant in assayed peptides; "
        "(2) Multi-Cell-Type Colocalization & 3D Structural Assemblies (EALS-015, EALS-030, EALS-018, EALS-007, EALS-044): "
        "chr14q12 (EALS-015) SCFD1/G2E3 annotations needed initial iPSC line counts separated from post-QC nonproliferating iMGL eQTL donor denominators and targeted "
        "NeuroKO screen statistics alongside signed rs229143-A / rs229194-A / rs229195-A slopes, SARM1 (EALS-030) PDB 7NAL / 7ANW / 7DJT entries needed explicit resolved-chain "
        "and preparation-ligand bounds, C1q (EALS-018) PDB 1PK6 needed mature signal-cleaved CLR cationic counts, IL1RL1 (EALS-007) needed compartment-divergent fluid context, "
        "and DPP10 (EALS-044) needed canonical Q8N608 vs. Q8N608-3 residue indexing; "
        "(3) Standard-of-Care vs. Phenotypic-Screen Mechanism Separation (EALS-013): "
        "Riluzole (EALS-013) clinical survival efficacy and unbound plasma Cmax exposure needed explicit separation from the Bye 2025 iPSC-MN SCN8A Exon 5N->5A splicing readout "
        "and Brown 2022 TDP-43-KD SCN8A RNA/Ribo depletion; "
        "(4) Clinical-Trial Denominators, Biofluid Modalities & Safety Provenance (EALS-008, EALS-009, EALS-020, EALS-010, EALS-021, EALS-048, EALS-018): "
        "Memantine (EALS-008) TAME records previously blended de Carvalho 2010 PEG-placement p-values and Levine 2010 open-label NCT01020331 CSF tau with randomized TAME "
        "and carried unverified interim survival HRs on MND-SMART (EALS-008, EALS-009), while Apilimod (EALS-020), Ropinirole (EALS-010), Icerguastat (EALS-021), Lamotrigine (EALS-048), and ANX005 (EALS-018) "
        "needed primary-table plasma vs. CSF ratios, investigator-attributed SAE denominators, and crossover-completer counts; "
        "(5) Statistical Contrast Classification & Workbench Display (EALS-004, EALS-025, 202 Contrasts): "
        "compact Replication Workbench labels required strict separation of frequentist p/BH-FDR tests, GWAS-intersection Bonferroni thresholds, Bayesian MAJIQ posteriors, "
        "human CSF PK participant units and calculated free-concentration estimates, and positive-coordinate 3D structural entries."
    ),
    "new_evidence_or_revision": (
        "(1) Splicing, Modality & Constraint Remediation: separates Brown 2022 i3Neuron (PMID:35197628, MOESM11 line 4527: dPSI=+0.2139, p_d_psi_0.05=4.15e-24, "
        "posterior P(|dPSI|>=0.10)=0.999994) and Joseph 2025 stem-cell neuron knockdowns (PMID:41174170 Fig. 1a,c-i) from postmortem GSE126543 (Liu 2019 PMID:31042469) "
        "FACS-sorted neuronal-nuclear fractions analyzed across N=7 C9orf72 ALS/FTD cortices in Ma 2022 (PMID:35197626 MOESM5 row 29: LeafCutter BH-FDR=1.45e-5, dPSI=0.243; "
        "MAJIQ dPSI=0.451) and reused across 6/7 coverage-passing GSE126543 datasets in Joseph 2025 Fig. 2j-k (6/6 people's pooled TDP-43-low nuclear fractions, vs Fig. 1b gene-list intersection; alongside PDB 7CR2 Trp236 2.97A CZ2-O3 closest contact vs 3.00A NE1-O3 H-bond and 2:2 vs 4:0 "
        "Kv7.2/Kv7.3 stoichiometry 38.2% vs 61.8% in EV-P2-T1-001), distinguishes sample-level NYGC motor-cortex (29.5%) and lumbar-cord (17.3%) proportions across 1,124 libraries "
        "(252 donors) from Mayo IHC-confirmed frontal-cortex case-control RT-qPCR (Fig. 2f: 89 FTLD-TDP vs 27 controls, n=116, adj beta=4.994, P<0.0001) and within-FTLD-TDP biochemical pTDP-43 immunoassay regression (Fig. 2h: n=89 cases, adj beta=0.835, P<0.0001), pairs release-specific gnomAD v4.1 vs v4.1.1 MANE pLI/LOEUF across flagship monographs "
        "(KCNQ2 LOEUF 0.295 vs 0.258 / mis_z 5.61, SARM1 pLI 2.28e-23 / LOEUF 1.413 vs 2.75e-19 / 1.143, UNC13A 0.389 vs 0.344, STMN2 0.261, IL1RL1 pLI 8.59e-6 / LOEUF 1.063 vs 4.86e-7 / 0.845, ATG4B pLI 2.08e-6 / LOEUF 0.851 vs 3.35e-4 / 0.699, CELF5 0.216), reports Spillman 2026 cortical P2 synaptosome DIA (PMID:42789089) "
        "as non-significant in assayed peptides, and expands GRCh38 cis-regulatory coverage to 28 windows including PTPRT Intron-26 chr20:42099262-42099281(-); "
        "(2) Haplotype & 3D Structural Remediation: resolves chr14q12 (EALS-015, PMID:43045849) 261 initial iPSC lines (254 donors) into post-QC nonproliferating iMGL eQTL "
        "donors (n=189 untreated, n=188 IFN-gamma, n=188 LPS; nominal SCFD1 fit n=186/185/185) and targeted 251-gene NeuroKO FDR=0.9284 in EV-P4-007 with exported "
        "UNRESOLVED_CELL_TYPE_OPPOSING_EQTL_POLARITY status, specifies SARM1 (EALS-030) near-full-length octamers 7ANW (aa 26-724) & 7DJT (aa 27-724) vs 7NAL NMN-bound ARM-SAM ring "
        "(from an NMN/1AD-incubated preparation; companion 7NAK), locks C1q (EALS-018) PDB 1PK6 (PMID:12960167) 1 heterotrimer / 3 chains and 27 mature CLR Arg/Lys residues "
        "(C1QA 23-109, C1QB 28-114, C1QC 29-112; PMID:38942014), adds Pan 2026 compartment-divergent IL1RL1 context (PMID:42698373), and indexes DPP10 (EALS-044) canonical Q8N608 "
        "Gly651 vs Q8N608-3 Gly655; "
        "(3) Benchmark & Clinical-Trial Remediation: decouples Riluzole (EALS-013) pivotal survival & unbound plasma Cmax,u (22.2-29.6 nM, PMID:8302340; PMID:8676624) in EV-P4-009 "
        "from Bye 2025 SCN8A Exon 5N->5A splicing (EV-B4-007, dPSI=+0.2019; Brown MOESM12/13 whole-gene RNA log2FC=-0.0601, Ribo +0.1075 NS), anchors Bhai 2024 randomized TAME (PMID:39511965, "
        "NCT02118727: N=89 randomized, n=83 LME evaluable [54 vs 29], N=52 completing assigned 36-wk treatment [32 memantine, 20 placebo, Fig. 1]) Table 2 weekly ALSFRS-R slope differences (-0.005 [SD 0.067], p=0.94 unadjusted; "
        "-0.007 [0.067], p=0.92 duration-adjusted; -0.021 [0.074], p=0.77 duration+FVC-adjusted) and Table 3 (SE) blood biomarkers (NfL p=0.28, pNF-H p=0.99, TNF-alpha p=0.22, Chit-1 p=0.79; NCT02118727 blood tau prespecified NOT_POSTED, no CSF or tau results reported "
        "vs placebo-controlled MEDALS PMID:20565333 and non-placebo Levine 2010 PMID:20839903 NCT01020331 & Chan 2011 NCT00409721 DOI:10.3109/17482968.2011.615513) alongside MND-SMART Stage 2 n=355 (EV-B5-014, EV-B4-003, PMID:39307154: 49 memantine & 52 trazodone vs 48 placebo follow-up deaths in Appendix Table S3, with formal interim survival HR not prespecified in Fig. 4), and locks primary-table "
        "precision on Apilimod (EALS-020: Babu Table 3 plasma sGPNMB 2.31 p<0.001 vs CSF 0.92 p=0.352, PMID:38606777; VRG50635 NCT06215755 AAN2026-003396 8/50 [16.0%] investigator-reported "
        "treatment-related SAEs, PMID:41708347), Ropinirole (EALS-010: Table S3 68.68 nM vs Discussion ~18 nM CSF, PMID:37267913), Icerguastat (EALS-021, NCT05508074), Lamotrigine "
        "(EALS-048: Ryberg 2003 N=30 crossover completers, PMID:12807386), and ANX005 (EALS-018, NCT04569435); "
        "(4) Provenance & Workbench Remediation: reclassifies Spillman NEFH Welch t-test (EV-B6-048) to donor-level frequentist recompute and Dexmedetomidine (EV-B6-032: N=8 postoperative women in Talke 1997 PMID:9356115, measured lumbar CSF = 4% +/- 1% of plasma + calculated molar CSF & calculated NDA021038 unbound plasma) & Ceftriaxone "
        "(EV-B5-007, PMID:24771634) CSF PK to PK/binding measurements, anchors 3D labels strictly to positive structural coordinates, and maps multi-component contrast rows to explicit detail views."
    ),
    "portfolio_and_gate_consequence": (
        "Advances ExploreALS to v1.3.0 with all 52 candidate ranks, biological evidence ranks, triage verdicts (4 Keep · Core, 25 Keep · Exploratory, "
        "7 Benchmark/Biomarker, 16 Drop · Falsified), actionability tiers, hurdle counts, and 28 GRCh38 cis-regulatory safety classifications preserved intact "
        "while synchronizing primary-source denominators, assay modalities, structural chain bounds, and 202/202 checksum-anchored statistical contrast "
        "classifications across all 18 registries, 8 flagship monographs, and the Replication Workbench."
    ),
    "primary_sources": (
        "PMID:35197628;PMID:35197626;PMID:31042469;PMID:41174170;PMID:42789089;PMID:43045849;"
        "PMID:12960167;PMID:38942014;PMID:42698373;PMID:8302340;PMID:8676624;PMID:39511965;"
        "PMID:39307154;PMID:20565333;PMID:20839903;PMID:9356115;PMID:38606777;PMID:41708347;PMID:37267913;"
        "PMID:12807386;PMID:24771634;10.3109/17482968.2011.615513;NCT02118727;NCT01020331;NCT00409721;NCT05163886;NCT06215755;"
        "NCT05508074;NCT04569435"
    ),
    "verification_anchor": (
        "FLAGSHIP-EALS-030;FLAGSHIP-EALS-031;FLAGSHIP-EALS-001;FLAGSHIP-EALS-006;FLAGSHIP-EALS-002;"
        "FLAGSHIP-EALS-007;FLAGSHIP-EALS-034;FLAGSHIP-EALS-037;EV-B1-011;EV-B1-014;EV-B1-015;"
        "EV-P2-T1-001;EV-B4-003;EV-B4-007;EV-P4-007;EV-P4-009;EV-B5-007;EV-B5-014;EV-B5-015;EV-B6-032;"
        "EV-B6-036;EV-B6-043;EV-B6-048;EV-P3B-031;RUN-P4-001;RUN-P4-002;RUN-P4-003"
    ),
}
