"""ExploreALS v1.3.1 Living Research Log & cross-link specification (UPD-2026-11-26-01) for 2026 TBK1/IFN-I/RIPK1 synthesis."""
from __future__ import annotations

UPD_2026_11_26_01: dict[str, str] = {
    "update_id": "UPD-2026-11-26-01",
    "date_iso": "2026-11-26",
    "release_tag": "v1.3.1",
    "update_category": "LITERATURE_INGESTION",
    "affected_ids": "EALS-019;EALS-033;EALS-017;EALS-034",
    "decision_impact": (
        "Direct TBK1 & Unstratified RIPK1 Inhibition Excluded; EALS-019 (#24) & EALS-033 (#19) "
        "Cross-Linked on Microglial IFN-I vs. Neuronal Monomeric TDP-43 Clearance"
    ),
    "headline": (
        "2026 Nagoya TBK1–IFN-I Studies (Horiuchi SOD1G93A Tbk1/Tnf DKO & Sakai Monomeric TDP-43 Clearance), "
        "Phase 2 HIMALAYA RIPK1 Futility & Multi-Cohort Human ALS Re-Analysis"
    ),
    "prior_state_or_assumption": (
        "Translational extrapolations from SOD1G93A mouse Tbk1-deletion studies (Brenner 2019 PMID:30635357; "
        "Gerbino 2020 PMID:32220666; Horiuchi 2026 DOI:10.1186/s40478-026-02474-w) or murine Tnf/Ripk1 rescue "
        "models frequently treat TBK1, RIPK1, or pan-CNS Type I interferon (IFNAR/TYK2/JAK1) blockade as broadly "
        "neuroprotective in human ALS without separating SOD1 misfolding (~2% of ALS) from sporadic TDP-43 "
        "proteinopathy (~97%), accounting for constitutive Tnf-/- embryonic-lethality rescue backgrounds, or testing "
        "whether receptor-level IFNAR/TYK2/JAK1 inhibition impairs cell-autonomous neuronal TDP-43 turnover "
        "(unedited Bye 2025 sALS iPSC-MN screen cultures lacked bulk nuclear TDP-43 depletion, P=0.990, PMID:41286450)."
    ),
    "new_evidence_or_revision": (
        "(1) Biphasic Mouse SOD1 vs. Protective Neuronal TDP-43 TBK1 Biology: in unblinded, non-randomized mixed "
        "C57BL/6 x 129/Sv SOD1G93A;Tbk1-/-;Tnf-/- (G-DKO, n=19: 8M/11F) vs. SOD1G93A;Tbk1+/+;Tnf-/- (G-TKO, n=27: "
        "16M/11F) mice (requiring Tnf-/- because Tbk1-/-;Tnf+/+ and Tbk1-/-;Tnf+/- had 0 live births, Fig. S2), "
        "Horiuchi et al. (2026, Acta Neuropathol Commun, DOI:10.1186/s40478-026-02474-w) reported accelerated onset "
        "and worse 3-month clasping/rotarod (Fig. 1B-E), downregulated 5-month CD11b+ microglial DAM, "
        "interferon-responsive microglial [IRM] (10/53 IRM markers including Rsad2/Ifi204), and autophagy "
        "(Sqstm1/Atg7/Nrbf2) across 587 DEGs (362 up, 225 down, n=3 vs. 4), +18.6 d post-onset duration extension "
        "without extending male lifespan (Fig. 1F-H) or rescuing day-111/end-stage lumbar ChAT+ motor neurons "
        "(Fig. S6, n=4), reduced spinal MAM proteins IP3R3 and VAPB (Fig. S5, n=3), and Tnf-/--driven sciatic-axotomy "
        "microglial suppression (Fig. 5); conversely, Tbk1+/- worsened NMJ denervation in TDP-43(G298S) mice "
        "(PMID:33038415); and Sakai et al. (2026, EMBO Rep, PMID:42834122) showed aggregation-prone monomeric TDP-43 "
        "physically activates neuronal TBK1 -> IFN-beta -> IFNAR -> immunoproteasome (PSMB8) degradation independently "
        "of macroautophagy (EALS-034 ATG4B), with IFNAR downregulated in postmortem human ALS spinal motor neurons; "
        "(2) Human Genetic, Safety & Phase 2 HIMALAYA RIPK1 Counterevidence: human TBK1 haploinsufficiency causes "
        "ALSFTD4 (PMID:25700176; PMID:25803835; gnomAD v4.1 MANE ENST00000331710 pLI=0.972, LOEUF=0.505, obs/exp="
        "19/55.2 vs. LoF-tolerant CGAS LOEUF=1.529 & STING1 LOEUF=0.846); TBK1 inhibition/knockdown alters human "
        "iPSC-cardiomyocyte beating (PMID:28453775); and in Phase 2 HIMALAYA (NCT05237284, Cudkowicz et al. 2026 "
        "Lancet Neurol PMID:42716044, N=305 randomized 2:1 [203 oral CNS-penetrant RIPK1 inhibitor SAR443820 20 mg "
        "BID, 102 placebo; n=299 primary set]), SAR443820 missed Week-24 ALSFRS-R (MMRM LS mean -6.73 [n=169] vs. "
        "-6.32 [n=87], diff -0.41 [-0.414 on CT.gov, 95% CI -1.71 to +0.88, p=0.5289]) and Part B Week-52 CAFS "
        "(145.24 [n=196] vs. 154.89 [n=100], ANCOVA p=0.1830) with higher AE discontinuations (28/202 [14%] vs. 5/102 "
        "[5%]) and 'Hepatic enzyme increased' SAEs (5/202 [2.48%] Part A + 3/79 [3.80%] Part B crossover vs. 0/102 "
        "placebo), terminating ALS development (0 human ALS/FTD trials test TBK1, cGAS, or STING1 inhibitors through "
        "Nov 2026); "
        "(3) Multi-Cohort Human ALS Divergence: in NYGC spinal cord (GC% + neuronal/glial + RIN OLS), ALS-Glia "
        "elevates CGAS (vs. Control adj_beta=+0.4779, p=1.69e-6, n=168; vs. ALS-Ox +0.2496, p=0.00347, n=189), IFI16 "
        "(vs. Control +0.5870, p=5.35e-9; Zhang 2026 cervical MN-niche +0.8911, p=0.00973, BH=0.0709), STING1 (vs. "
        "ALS-Ox +0.2917, p=0.0102), and JAK1 (vs. Control +0.2501, p=4.92e-11; gp130/JAK1-STAT3 vs. ALS-Ox Welch "
        "z_diff=+0.4169, p=1.91e-6), whereas STAT2 (-0.4635, p=6.35e-8), RSAD2 (-0.5257, p=4.01e-4), IFIT1 (-0.3507, "
        "p=6.09e-4), and VAPB (-0.2906, p=1.74e-6) are lower than Control (spinal Type I IFN composite vs. ALS-Ox "
        "Welch p=0.843); in NYGC motor cortex (ALS-TE vs. ALS-Ox, n=153), TYK2 (+0.5824, p=1.27e-18), RIPK1 (+0.3971, "
        "p=2.90e-11), IKBKE (+0.3246, p=1.54e-5), STING1 (+0.3098, p=8.69e-4), IFI16 (+0.2136, p=0.00664), and CGAS "
        "(+0.1264, p=0.0451; cf. mtDNA->cGAS-STING PMID:33031745) rise while TBK1 (-0.2578, p=3.52e-12), TAX1BP1 "
        "(-0.2153, p=1.47e-9), and VAPB (-0.2109, p=2.45e-9) are lower vs. ALS-Ox; in Spillman 2026 C9-FTD cortex "
        "(PMID:42789089), homogenate OPTN (-0.6869, padj=0.0266) and synaptosome TBK1 (-0.4002, p=0.0070, padj=0.212) "
        "/ TAX1BP1 (-0.6558, p=0.00148, padj=0.140) decline vs. homogenate JAK1 (+0.6088, padj=0.0392); and Edinburgh "
        "cortical snRNA-seq microglial ISG15 falls (-1.1603, p=0.0460), Brown 2022 i3Neuron TDP-43 KD shows 0 cryptic "
        "splicing junctions across the panel, and Trautwig 2025 antemortem CSF (PMID:40375307) detects 0% TBK1, CGAS, "
        "STING1, IFI16, and RSAD2."
    ),
    "portfolio_and_gate_consequence": (
        "Excludes pharmacological TBK1 and unstratified RIPK1 inhibition while preserving all 52 candidate ranks "
        "and verdicts (EALS-019 #24 and EALS-033 #19 remain Keep · Exploratory, Tier 3; EALS-017 #33 remains "
        "Benchmark / Biomarker; EALS-034 #7 remains Tier 2): "
        "(1) updates EALS-019 (Baricitinib / JAK1 / BHV-8000) to require monomeric TDP-43 / PSMB8 immunoproteasome "
        "counter-screening and germline TBK1 LoF carrier exclusion on high-Kp,uu IFNAR/TYK2/JAK1 blockers; "
        "(2) notes EALS-033 (TPN-101 LINE-1 RT) spares cell-autonomous neuronal TBK1->IFN-beta->PSMB8 clearance "
        "upstream of cGAS-STING; and "
        "(3) records motor-neuron-restricted PSMB8/PA28 activation (+/- EALS-034 ATG4B splice rescue, gated against "
        "neuronal HLA-ABC/B2M MHC-I CD8+ T-cell killing) as a bounded preclinical hypothesis."
    ),
    "primary_sources": (
        "10.1186/s40478-026-02474-w;PMID:42834122;PMID:42716044;PMID:25700176;PMID:25803835;PMID:28453775;"
        "PMID:30635357;PMID:32220666;PMID:33038415;PMID:33031745;PMID:41832177;PMID:42789089;PMID:40375307;"
        "NCT05237284;NCT04993755;NCT04297683;NCT05189106;NCT06976268"
    ),
    "verification_anchor": (
        "RUN-P2-T3-005;EV-P2-T3-001;EV-P2-T3-002;EV-P2-T3-003;EV-P2-T3-006;EV-B3-007;FLAGSHIP-EALS-034;RUN-P4-003"
    ),
}
