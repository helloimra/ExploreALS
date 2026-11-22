"""Falsified candidate trap summaries (25 DROP IDs), 9-row contrast matrix, and strict invariant builder for CarbonALS."""
from __future__ import annotations

import re

from _candidate_contrasts_a import CANDIDATE_EDGES_ACTIVE, CANDIDATE_LENSES, EDGE_ROLE_LABELS, LENS_DEFS
from _public_taxonomy import sanitize_public_prose
from carbon_als.accessions import legacy_to_accession, translate_legacy_tokens_in_prose

CANDIDATE_EDGES_DROPS: dict[str, tuple[str, str]] = {
    "C004": ("FALSIFIED_TRAP", "Phase 3 Stage 3 futility in 513 ALS patients (p=0.237; survival HR=0.90, p=0.415) with 12.1% biliary SAEs, >10 uM ChEMBL EAAT2 EC50 vs 2-6 uM CSF, and intact human astrocytic SLC1A2 mRNA."),
    "C008": ("FALSIFIED_TRAP", "Target-engaged clinical futility across Phase 3 MND-SMART (n=355 Stage 2 comparison, p=0.36) and Phase 2b TAME (40 mg/d, N=89 randomized, null ALSFRS-R/NfL) at NMDA-engaging CSF levels (~0.25-1.2 uM) refutes pan-NMDA blockade (2.5 uM rescue plausibly reflects untested media excitotoxicity)."),
    "C009": ("FALSIFIED_TRAP", "Phase 3 MND-SMART futility (n=355 Stage 2, p=0.24), a 71-330x [MODEL_PRIOR] unbound brain PK deficit vs 20-40 uM ISR rescue (5-HT2A/alpha1 sedation + mCPP anorexia), and HEALEY eIF2B class futility/NfL rise."),
    "C010": ("FALSIFIED_TRAP", "14.6-556x ALS CSF PK gap at GI-limited 16 mg/d MTD (Table S3 68.7 nM / Discussion ~18 nM vs 1-10 uM non-D2 sALS rescue; 0% spinal DRD3), FDR-significant sALS iPSC-MN harm (-0.69d, FDR=0.021), null ROPALS (p=0.76), and Ph2a EXPERTS-ALS blood-NfL stop."),
    "C012": ("FALSIFIED_TRAP", "Phase 2 RCT NCT03019419 (N=65 ITT) showed 48-wk ALSFRS-R worsening at 8 mg/d (-8.4 pts, p=0.0145; completion 33% [8 mg] & 64% [4 mg] vs 82% placebo, SAE p=0.048), showing non-selective AMPA blockade accelerates motor decline."),
    "DN-13": ("FALSIFIED_TRAP", "Postmortem MAOB Visium/homogenate elevation is consistent with reactive astrogliosis rather than neuronal drive, and PET-saturated (>85-90% in N=3 HV) selective MAO-B inhibitors failed three double-blind placebo-controlled ALS RCTs plus one open-label trial."),
    "DN-15": ("FALSIFIED_TRAP", "Sub-FDR 2.5 uM iPSC-MN survival (+0.90d, FDR=0.070) failed human ALS CSF glutamate/clinical PD at 300 mg/d (~7-15 uM total CSF, N=30 completers) alongside Eisen 1993 (N=67) and oral NaV class futility."),
    "DN-16": ("FALSIFIED_TRAP", "Phase 3 LIGHTHOUSE II (NCT05193994, N=419, Triumeq; interim futility announced 5 Apr 2025) failed survival in unstratified ALS alongside an 80-500x unbound CSF gap (~5-32 nM, PMID:24944232) and zero LINE-1 integrase."),
    "DN-18": ("FALSIFIED_TRAP", "Sub-FDR 2.5 uM survival (+0.74d, FDR=0.183) failed in Phase II QALS at 2,700 mg/d (NCT00243932, Stage 2 n=150: primary p=0.14 from 1 CoQ10 vs 5 placebo Month-9 deaths coded 0; death=16 sensitivity p=0.025 < 0.10 futile; Table 2 GI plateau)."),
    "C011": ("FALSIFIED_TRAP", "Organic-anion OAT3/MRP4 efflux and 91-99% albumin binding create a >1,000-5,800x [MODEL_PRIOR] unbound CNS gap (<1-5 nM vs 5.15-5.82 uM human hNKCC1 IC50; 0 ALS RCTs) while co-inhibiting depleted KCC2/CA1-2 and spinal D1 Ia/sural inhibition."),
    "C021": ("FALSIFIED_TRAP", "Extreme oral clearance (CL/F=580-1,388 L/h) caps total plasma Cmax at 61 nM in ALS and 35 nM in HV (41-71x below 2.5 uM; [MODEL_PRIOR] Cu,brain ~5-20 nM, flat GDF15, null ALSFRS-R p=0.92), with 2/34 possibly drug-related (5/34 total) fatal TEAEs."),
    "S01": ("FALSIFIED_TRAP", "Measured human unbound plasma (0.09-0.37 nM) and lumbar CSF (~0.20-0.35 nM, PMID:9356115; CSF pressure PMID:9249114) sit ~6,700-10,000-fold below the 2.5 uM screen concentration and are bounded by alpha-2A sedation, hypotension, and bradycardia."),
    "S03": ("FALSIFIED_TRAP", "Active mycophenolic acid faces a 45-165-fold [MODEL_PRIOR] unbound CNS deficit (~15-55 nM vs 2.5 uM; 97% bound fu=0.03), carries Boxed/PML warnings, and had 0/31 responders (p=0.20 vs lead-in; 18/31 regimen completers) in 4-drug ALS testing."),
    "S04": ("FALSIFIED_TRAP", "Combined [MODEL_PRIOR] unbound brain tamoxifen+metabolites (~3-15 nM; Lien 1991 lipid trapping) is 165-800-fold below the 2.5 uM screen (plausible cationic-amphiphilic phospholipidosis regime), with 2 PE + 3 DVT events across 38 ALS recipients (PMID:31608711) and null 12-mo trials."),
    "S05": ("FALSIFIED_TRAP", "Lonafarnib/tipifarnib combine a [MODEL_PRIOR] Cu,brain deficit (~2-13 nM vs 70-500 nM lonafarnib IC50) and pediatric progeria 37% weight-loss/GI & oncology myelosuppressive toxicity with iatrogenic blockade of mandatory YKT6 Cys195 farnesylation atop PTAR1 170-bp Exon-2 skipping."),
    "C024": ("FALSIFIED_TRAP", "Subcutaneous C3 inhibitor pegcetacoplan (~43.5 kDa, unmeasured CSF PK / limited intact-BBB entry expected) missed Week 52 primary CAFS (LS mean rank diff -3.0, p=0.72) and all secondary endpoints in Phase 2 MERIDIAN (NCT04579666, N=247 mITT), matching Ph3 ravulizumab and Ph2/3 zilucoplan futility."),
}

KEY_MECHANISTIC_CONTRASTS_9: list[dict[str, object]] = [
    {"ids": ["S06"], "domain": "Axonal SARM1 Allostery", "naive": "Orthosteric SARM1 inhibitors act uniformly, SIR2501 closes allostery, and plasma/bulk cADPR measures motor-axon SARM1.", "finding": "BEXi prodrugs (LY3873862, HV NCT05492201 / ALS NYR) bridge 3 TIR chains (PDB 9TZY adduct 17; 122/122 sub-IC50 activation with median 8.6x IC50/C_act shift, PMID:42380237), undisclosed SIR2501 leaves Cys311 covalency open, and HV plasma cADPR is >90% ecto-CD38-derived [MODEL_PRIOR, murine KO PMID:32087251].", "gate": "Gate prospective Cys311Ala selectivity for non-covalent inter-protomer ARM-TIR T-locks, exclude <1% GoF carriers, and pair CD38 counter-screens + unbound CSF trough PK + NDEV cADPR:NAD+."},
    {"ids": ["C006", "C005", "C012"], "domain": "Kv7.2 Isoform & Stage Polarity", "naive": "Oral Kv7 openers fully rescue KCNQ2 loss, Intron-4 UG8 SSOs sponge trans TDP-43, and late AMPA blockade helps.", "finding": "ER-retained KCNQ2dE5 excises Trp236 (PDB 7CR2, imposing a surface-density opener ceiling; WO2023102548A1 / WO2024206195A1); UG8 SSO #1 risks cis-evicting WT TDP-43 in healthy neurons/DRGs; late 8 mg Perampanel worsened ALSFRS-R (-8.4 pts, p=0.015; 7 completers, 67% dropout).", "gate": "Run dense 1-nt microwalk (#3 ISS vs ISE check vs #1 WT cis-eviction) + companion TMS SICI/SDTC & intact CSF NPTX2 research stratification."},
    {"ids": ["C001", "C002"], "domain": "Cortical Paradox & Multiplex TE", "naive": "High bulk cortical STMN2 RNA refutes loss, Day-421 ANQUR OLE NfL proves 10 mg monotherapy, and rs12608932 A/A exempts UNC13A.", "finding": "Polyadenylated tSTMN2 inflates cortical RNA vs -28% protein (p=0.014, n=20 C9-FTD); QRL-201 ANQUR (completed DRF + ongoing OLE; CONQUR IND) dissociated 3 mg (-46%) vs 10 mg (~5%) pNfH (Day-253 10 mg ALSFRS-R excluded top NfL tertile) while 10mg->3mg OLE NfL (-36%) co-reflects washout, lag & 41/52 attrition; Keuss 2026 rescued human MN synapses (>30% UNC13A) orthogonally to STMN2 & KCNQ2.", "gate": "Pair 3-layer per-target PK + NDEV-dPCR/secretome TE + >=16-24 wk pNfH PD with multiplex polyanion/DRG margin targeting (EC80<=3 mg/strand = 6-9.0 mg; BA4 gradient checked) across rs12973192/rs12608932."},
    {"ids": ["S07"], "domain": "Biofluid Assay Calibration", "naive": "Clinical TRICALS risk, shotgun CSF MS, or uncalibrated commercial pg/mL cutoffs can substitute directly for MIROCALS BioVendor ELISA CSF pNfH <=3,700 pg/mL.", "finding": "MIROCALS (N=220, unadjusted ITT HR=0.81 p=0.33) & Al Khleifat 2026 (PMID:42836993) show TRICALS shares r^2=12.7% with CSF pNfH (nested pNfH x trt dChi2=14.24 vs TRICALS x trt 4.76), pNfH immunoassays span ~1.8x-4.5x offsets (vs tryptic MS r=0.28 & immunoassay rho=0.64-0.71, PMID:38683209), and ALSTARS (N=137) stratifies 3 serum NfL tiers with dual IL-2 + CTLA4-Ig.", "gate": "Run CLSI EP09c (N>=40) Passing-Bablok bridging to MIROCALS ~79th BioVendor percentile (n=173/220 <=3,700 pg/mL; <750 n=19 had 0 deaths) + event-driven Phase 3 (247 deaths @ HR=0.70, N~650-750)."},
    {"ids": ["C007"], "domain": "Vascular Isoform, Cys327 & RNA Shuttle", "naive": "Pan-ST2 mAbs, nuclear Intron-8 gapmers, or IHH-mutated sweeping antibodies cleanly validate and silence CNS endothelial sST2.", "finding": "Nuclear Intron-8 gapmers & Exon-8 5'SS masking cleave/deplete nascent ST2L; PDB 4KC3 (aa 21-317, 10-Cys/5-SS) leaves sequence-deduced Cys327 in 324-SKECF-328 unpaired (+ SLC3A2 -SKEDF 4/5 match), while catalytic sweeping requires intact pH-6.0 FcRn salvage and ventilatory strain spikes sST2 3-20x.", "gate": "Gate oximetry-verified FVC>=80% CSF Simoa + microvessel ddPCR + iPSC tri-culture BBB-brake sign before IT CD98hc/TfR1-shuttled cytoplasmic sST2 siRNA or Zone 1 PAS 2'-MOE SSO (#1 102346045-102346062(+))."},
    {"ids": ["DN-04", "DN-01", "DN-05", "DN-02"], "domain": "Cryptic Splicing, 3J Off-Targets & EJC Gap", "naive": "16-nt LNA ASOs and 3-exon splicing minigenes cleanly model human intrathecal cryptic-exon NMD rescue.", "finding": "In ATG4B (#7), IT 2'-MOE #2 (-10 bp vs 16-nt 6-LNA ASO 3J) cuts sequence flags from 10/18/5 to 0/0/0; in CELF5 (#8, ID-MND clu_25763_+ padj=0.0090, conditional 108-nt frame) & KALRN (#11, Intron-53, Guo 2026 PMID:42234776), PTCs sit 18 nt & ~32 nt (<50 nt EJC rule) from the downstream junction so 3-exon minigenes evade EJC-NMD (CELF5 NMD inhibition 24.8%->44.6%, PMID:40672339).", "gate": "Run Stage-(ii) cervical alpha-MN BaseScope ISH across all 4 targets + endogenous multi-exon Nanopore phasing (CELF5 Exon 1-7+ <1-2% Exon-5 skip & <=WT ~2.8% micro-intron; PRUNE2 Exon 11-12 RT-PCR; KALRN Intron-53 spinal vs cortical penetrance)."},
    {"ids": ["C022", "C015", "C023"], "domain": "Mendelian Isoform & chr14q12 Polarity", "naive": "Intron-9 3'SS blockers or gapmers boost DNAJB2a, chr14q12 SCFD1 acts unidirectionally across glia and MNs, and cis-Golgi SNAREs are co-druggable.", "finding": "DNAJB2 has 0/6 TDP-43 cryptic shifts, 25/25 ClinVar P/LP in shared Exons 2-9 vs 0/25 in Zone A, and 3'SS blockade forces DNAJB2b; SuSiE (purityMeanR2=0.988; 1000G EUR 96.7% vs AFR 72.7% 1111 purity) pairs chr14q12 risk alleles with MN +0.048 vs iMGL -0.22..-0.33 SCFD1 opposition (PMID:43045849; G2E3 Alu 0mm fail); YKT6 p.Tyr64Cys (rs138273846, ALS AF=0.183%, AVI=24.53) expands rat PDB 3KYQ's cavity +85 A^3.", "gate": "Restrict DNAJB2 SSOs to internal Intron-9 ISS/IPA competition (chr2:219284988-219285939(+)) + 3'-UTR counter-screens vs AAV-DNAJB2a, run allele-specific MN+iMGL chr14q12 editing, and restrict YKT6 to Cys195-retaining stabilizers."},
    {"ids": ["C017", "C019"], "domain": "Glial Biomarkers & JAK1/JAK2 Catch-22", "naive": "Elevated CSF CHIT1/GPNMB are drug targets or mimic-specific diagnostics, and 4 mg Baricitinib translates 2.5 uM rescue.", "finding": "Human ALS CHIT1 KO (rs3831317: 9% [6/65] homozygotes in PMID:33576252) is progression-neutral & GPNMB is protective (Emory CHIT1-adjusted CSF OOF AUC=0.82, recalibrated=0.88-0.89; healthy AUC<=0.92 PMID:31123140 vs mimic 0.688 PMID:29142138); 4 mg Baricitinib hits 3.804 nM total CSF (1/9 PE + 1/9 DVT in NADALS) while JAK1-selectives forfeit neuronal JAK2 APA.", "gate": "Deconvolve 3.8-50 nM JAK1 vs JAK1/2 in glia-free vs ALS-Glia co-cultures before any VTE-prophylaxed interaction trial."},
    {"ids": ["S01", "S02", "S05", "S08"], "domain": "Screen Physics, Unreported RCTs & Photolysis", "naive": "2.5 uM screen hits translate orally, NCT04082832 proved CuATSM RCT failure, and -3.60d refutes Methylcobalamin.", "finding": "Dexmedetomidine (~6,700-10,000x measured CSF gap, PMID:9356115) fails CNS tolerance, FTIs block YKT6 prenylation, CuATSM NCT04082832 (UNKNOWN) & completed N=55 OLE NCT04313166 outcomes remain unreported (hasResults=false; mixed 5v4 ALS-TDP + 1v2 SOD1 autopsy null), and ~450-488 nm Co-C photolysis explains B12's screen drop vs JETALS (N=129 FAS +1.97 pts, p=0.012).", "gate": "Enforce unbound human Kp,uu margins, registry-verified RCT status, and dark-vs-lit photolability controls across all screen hits."},
]


def build_edges_and_lenses(port_rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], list[dict[str, object]], list[dict[str, object]]]:
    all_edges = {**CANDIDATE_EDGES_ACTIVE, **CANDIDATE_EDGES_DROPS}
    port_ids = {r["portfolio_id"] for r in port_rows}
    drop_ids = [r["portfolio_id"] for r in port_rows if r["decision"] == "DROP"]
    assert set(CANDIDATE_EDGES_ACTIVE).isdisjoint(CANDIDATE_EDGES_DROPS) and set(all_edges) == port_ids, "Edge IDs != 52 portfolio IDs"
    assert set(CANDIDATE_EDGES_DROPS) == set(drop_ids) and len(drop_ids) == 16, f"Drop edge partition != 16 DROP rows: {len(drop_ids)}"
    role_counts = {k: sum(1 for rk, _ in all_edges.values() if rk == k) for k in EDGE_ROLE_LABELS}
    assert role_counts == {"MECHANISTIC_EDGE": 9, "CROWDED_MULTIPLEX": 2, "HIGH_HURDLE_WATCHLIST": 18, "BENCHMARK_CALIBRATOR": 7, "FALSIFIED_TRAP": 16}, role_counts

    lens_map = {**CANDIDATE_LENSES, "FALSIFIED_TRAPS": drop_ids}
    union_non_all = set().union(*lens_map.values())
    assert union_non_all == port_ids, f"Lens union missing IDs: {port_ids - union_non_all}"
    lenses_out: list[dict[str, object]] = []
    for lk, llbl in LENS_DEFS:
        ids = [r["portfolio_id"] for r in port_rows] if lk == "ALL" else lens_map[lk]
        assert int(llbl.rsplit("·", 1)[1].strip()) == len(ids), f"Lens count label mismatch on {lk}: {llbl} vs {len(ids)}"
        lenses_out.append({"k": lk, "lbl": llbl, "ids": [legacy_to_accession(x) for x in ids]})

    bench_sub_labels = {
        "C013": "APPROVED STANDARD-OF-CARE & ASSAY BENCHMARK",
        "S08": "APPROVED STANDARD-OF-CARE & ASSAY BENCHMARK",
        "C003": "WITHDRAWN DRUG — HUMAN KV7 PD CALIBRATION RULER",
        "C017": "VALIDATED LIVING-CSF STAGING & GLIAL PD PANEL",
        "DN-10": "CANDIDATE CSF PROTEOMIC MARKER (PRE-VALIDATION)",
        "DN-11": "CANDIDATE CSF PROTEOMIC MARKER (PRE-VALIDATION)",
        "DN-12": "CANDIDATE CSF PROTEOMIC MARKER (PRE-VALIDATION)",
    }
    edges_out: dict[str, dict[str, str]] = {}
    for pid, (rk, txt) in all_edges.items():
        clean_txt = sanitize_public_prose(translate_legacy_tokens_in_prose(txt))
        wcnt = len(clean_txt.split())
        assert 14 <= wcnt <= 68, f"{pid}: edge_text word count {wcnt} out of bounds: {clean_txt}"
        elbl = bench_sub_labels.get(pid, EDGE_ROLE_LABELS[rk])
        edges_out[legacy_to_accession(pid)] = {"edge_kind": rk, "edge_label": elbl, "edge_text": clean_txt}

    contrasts_out: list[dict[str, object]] = [
        {
            "ids": [legacy_to_accession(str(x)) for x in row["ids"]],  # type: ignore[union-attr]
            "domain": sanitize_public_prose(translate_legacy_tokens_in_prose(str(row["domain"]))),
            "naive": sanitize_public_prose(translate_legacy_tokens_in_prose(str(row["naive"]))),
            "finding": sanitize_public_prose(translate_legacy_tokens_in_prose(str(row["finding"]))),
            "gate": sanitize_public_prose(translate_legacy_tokens_in_prose(str(row["gate"]))),
        }
        for row in KEY_MECHANISTIC_CONTRASTS_9
    ]

    blob = " ".join([*(v["edge_text"] for v in edges_out.values()), *(str(r) for r in contrasts_out)])
    assert not re.search(r"exploreals|\bD003\b|\bD045\b|\bDS045\b|Phase\s*3A|/100|Cytosolic\s+vs\.\s+ER", blob, re.I), "Banned token in contrasts!"
    assert not re.search(r"\$\s*\d|\b(?:USD|capital|dollar|dollars|cheap|expensive|budget|fund|funds|funding|funded|cost|costs|evoi)\b", blob, re.I), "Financial token in contrasts!"
    return edges_out, lenses_out, contrasts_out
