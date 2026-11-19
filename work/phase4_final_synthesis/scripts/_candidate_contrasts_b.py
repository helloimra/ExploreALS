"""Falsified candidate trap summaries (25 DROP IDs), 9-row contrast matrix, and strict invariant builder for CarbonALS."""
from __future__ import annotations

import re

from _candidate_contrasts_a import CANDIDATE_EDGES_ACTIVE, CANDIDATE_LENSES, EDGE_ROLE_LABELS, LENS_DEFS

CANDIDATE_EDGES_DROPS: dict[str, tuple[str, str]] = {
    "C004": ("FALSIFIED_TRAP", "Phase 3 futility in 513 ALS patients (p=0.24; survival HR=0.90, p=0.41) with 12.1% biliary SAEs, >10 uM human EAAT2 EC50 vs 2-6 uM CSF, and absent human astrocytic SLC1A2 mRNA loss."),
    "C008": ("FALSIFIED_TRAP", "Target-engaged clinical futility across Phase 3 MND-SMART (N=554, p=0.36) and Phase 2b TAME (40 mg/d, null ALSFRS-R/pNfH) at NMDAR-engaging CSF levels (0.25-0.6 uM) refutes the 2.5 uM iPSC culture hit."),
    "C009": ("FALSIFIED_TRAP", "Phase 3 MND-SMART futility (NCT04302870, p=0.24) plus an 8.9-54x unbound brain PK deficit vs in vitro ISR rescue and class-wide human plasma NfL elevation under eIF2B activation."),
    "C010": ("FALSIFIED_TRAP", "15-146x human CSF PK gap at GI-limited 16 mg/d MTD (68.7 nM vs 1-10 uM non-D2 rescue; 0% spinal DRD3), FDR-significant sALS iPSC-MN harm (-0.69d, FDR=0.021), BA9 GC/cross-cohort collapse, null Ph1/2a ROPALS (N=20), and Ph2a EXPERTS-ALS blood-NfL futility stop."),
    "C012": ("FALSIFIED_TRAP", "Phase 2 RCT NCT03019419 (N=66) showed ALSFRS-R worsening in the 8 mg/d arm (-8.4 pts, p=0.015; 7 completers / 67% dropout vs 18% placebo, SAE p=0.048), showing unstratified late AMPA blockade accelerates motor decline."),
    "DN-13": ("FALSIFIED_TRAP", "Postmortem MAOB Visium/bulk elevation tracks reactive astrocyte expansion rather than neuronal drive, and selective MAO-B inhibitors failed four controlled human ALS trials (two rasagiline, two selegiline)."),
    "DN-15": ("FALSIFIED_TRAP", "Sub-FDR 2.5 uM iPSC-MN survival (+0.90d, FDR=0.070) is superseded by two negative double-blind human ALS trials up to 300 mg/d with verified CSF exposure."),
    "DN-16": ("FALSIFIED_TRAP", "Phase 3 LIGHTHOUSE II (NCT05193994, N=419, Triumeq) terminated for interim survival futility in unstratified ALS alongside a 60-250x unbound CSF gap vs 2.5 uM dolutegravir."),
    "DN-17": ("FALSIFIED_TRAP", "In vitro survival (+0.95d) reflects extracellular media thiol buffering while anionic NAC has poor BBB penetration (Kp,uu<<0.05) and failed a double-blind 50 mg/kg/d SC survival RCT (N=110, p=0.31)."),
    "DN-18": ("FALSIFIED_TRAP", "Marginal 2.5 uM iPSC-MN survival (+0.74d, FDR=0.18) failed to translate in the multicenter Phase II QALS trial at 2,700 mg/d (NCT00243932, N=185, Stage 2 futility p=0.51)."),
    "DN-19": ("FALSIFIED_TRAP", "Sub-FDR 2.5 uM L-serine (+0.71d, q=0.17) shifts ~400 uM basal neuronal media serine by +0.625% (<1% noise), while SPTLC1/2-ALS GoF variants lose ORMDL feedback and overproduce canonical C18-C22 sphingolipids where L-serine is contraindicated (PMID:34059824; PMID:43025655; SPTLC1 ASO LTX-002 NCT07660614)."),
    "C011": ("FALSIFIED_TRAP", "Organic-anion BBB efflux and 91-99% albumin binding create a >500-5,000x unbound CNS gap (<1-5 nM vs ~20 uM NKCC1 IC50) while non-selectively inhibiting depleted neuronal KCC2 and Renshaw inhibition."),
    "C021": ("FALSIFIED_TRAP", "High apparent oral clearance (CL/F=580 L/h, <10% oral F) caps Cu,brain at ~13 nM (193x below 2.5 uM; null ITT ALSFRS-R p=0.92 and flat GDF15), while 25 mg BID caused 2/34 drug-related fatal TEAEs and 23.5% falls."),
    "S01": ("FALSIFIED_TRAP", "Tolerated ICU unbound CNS exposure (~0.32 nM) is 7,862-fold below the 2.5 uM iPSC-MN screen concentration and bounded by alpha-2A sedation, hypotension, and bradycardia."),
    "S03": ("FALSIFIED_TRAP", "Active mycophenolic acid faces a 125-fold unbound CNS deficit (~20 nM vs 2.5 uM) from 98% albumin binding and efflux, carries PML/infection boxed warnings, and failed Phase 2 ALS testing (0/31 responders)."),
    "S04": ("FALSIFIED_TRAP", "Unbound human brain tamoxifen (~2.59 nM, fu=0.008) is 965-fold below the 2.5 uM screen regime (canonical ALogP=6.0 cationic-amphiphilic phospholipidosis), with thromboembolic risk and three non-durable ALS trials."),
    "S05": ("FALSIFIED_TRAP", "Lonafarnib/tipifarnib combine a human Cu,brain deficit (<=2-13 nM vs 70-500 nM IC50) and cachectic GI/myelosuppressive toxicity with iatrogenic blockade of essential neuronal YKT6 Cys195 farnesylation."),
    "C024": ("FALSIFIED_TRAP", "Subcutaneous C3 inhibitor pegcetacoplan (~43.5 kDa, <0.1% intact-BBB entry) missed Week 52 primary CAFS and all secondary endpoints in Phase 2 MERIDIAN (NCT04579666, N=249), matching two negative Phase 3 C5 ALS trials (PMID:39960672)."),
}

KEY_MECHANISTIC_CONTRASTS_9: list[dict[str, object]] = [
    {"ids": ["S06"], "domain": "Axonal SARM1 Allostery", "naive": "Orthosteric SARM1 inhibitors act uniformly, SIR2501 closes allostery, and plasma/bulk cADPR measures motor-axon SARM1.", "finding": "1-AD BEXi prodrugs (LY3873862, NYR) bridge 3 TIR chains (PDB 9TZY, 122/122 washout spike), undisclosed SIR2501 (CTR20253552/NCT07765446) leaves Cys311 covalency open, and HV plasma/bulk cADPR is >90% ecto-CD38-derived (PMID:32087251).", "gate": "Advance Cys311Ala-verified non-covalent ARM-TIR T-locks, exclude <1% GoF carriers, and pair CD38 counter-screens + unbound CSF trough PK + NDEV cADPR:NAD+."},
    {"ids": ["C006", "C005", "C012"], "domain": "Kv7.2 Isoform & Stage Polarity", "naive": "Oral Kv7 openers fully rescue KCNQ2 loss, Intron-4 UG8 SSOs sponge trans TDP-43, and late AMPA blockade helps.", "finding": "ER-retained KCNQ2dE5 excises Trp236 (PDB 7CR2, imposing a surface-density opener ceiling); UG8 SSO #1 risks cis-evicting WT TDP-43 in healthy neurons/DRGs; late 8 mg Perampanel worsened ALSFRS-R (-8.4 pts, p=0.015; 7 completers, 67% dropout).", "gate": "Run dense 1-nt microwalk (#3 ISS vs ISE check vs #1 WT cis-eviction) + early TMS SICI/SDTC & intact CSF NPTX2 gating."},
    {"ids": ["C001", "C002"], "domain": "Cortical Paradox & Multiplex TE", "naive": "High bulk cortical STMN2 RNA refutes loss, Day-421 ANQUR OLE NfL proves 10 mg monotherapy, and rs12608932 A/A exempts UNC13A.", "finding": "Polyadenylated tSTMN2 inflates cortical RNA vs -28% protein (p=0.014, n=20 C9-FTD); QRL-201 ANQUR (CONQUR IND) dissociated 3 mg (-46%) vs 10 mg (~5%) pNfH while 10mg->3mg OLE NfL (-36%) co-reflects bolus-shedding washout, lag & 41/52 attrition; Keuss 2026 rescued human MN synapses (>30% UNC13A) while STMN2 & KCNQ2 stayed mis-spliced.", "gate": "Pair 3-layer per-target PK + NDEV-dPCR/secretome TE + >=16-24 wk pNfH PD with multiplex polyanion/DRG margin targeting (EC80<=3 mg/strand = 6-9.0 mg; BA4 gradient checked) across rs12973192/rs12608932."},
    {"ids": ["S07"], "domain": "Biofluid Assay Calibration", "naive": "Clinical TRICALS risk or uncalibrated MSD/NfL pg/mL cutoffs can substitute for MIROCALS BioVendor ELISA CSF pNfH <=3,700 pg/mL.", "finding": "Al Khleifat 2026 (J Neurol, PMID:42836993, MIROCALS N=220) shows TRICALS explains r^2=12.7% (-2LL=928.25 vs 793.36; combined HR=0.28, p=0.002) and exposes 1.8x-4.5x MSD vs BioVendor pg/mL bias alongside weak Trautwig MS NEFL-NEFH r=0.28, while ALSTARS (N=137) omits pNfH and blocks Treg CD28.", "gate": "Run Passing-Bablok bridging to MIROCALS ~79th-80th BioVendor percentile + paired NfL calibration + event-driven Phase 3 (247 deaths @ HR=0.70, N~650-750; <750 pg/mL n=20 0-death floor noted)."},
    {"ids": ["C007"], "domain": "Vascular Isoform, Hypoxia & ASO Gap", "naive": "Pan-ST2 mAbs (astegolimab), FVC>=80% alone, or naked lumbar 2'-MOE ASOs cleanly validate and silence CNS endothelial sST2.", "finding": "Within-donor pseudoreplicated Visium spots (55-um, N=14) do not separate sST2 vs ST2L, pan-ST2 mAbs suppress protective Treg ST2L (~0.3% vs ~28% under sST2-selective neutralization, PDB 4KC3), nocturnal hypoxia spikes endothelial sST2 3-20x, and brain capillaries resist naked IT 2'-MOE ASOs (PMID:37188501).", "gate": "Gate oximetry/capnography-verified (PMID:41635251) FVC>=80% CSF Simoa + microvessel sST2/ST2L ddPCR (n>=25/20) before IT HLE sST2-neutralizing biologic (reduced BBB FcRn efflux) or conjugated PAS SSO."},
    {"ids": ["DN-04", "DN-01", "DN-05", "DN-02"], "domain": "De Novo Cryptic Splicing & Cord Stage", "naive": "Small-n SOD1/FUS p>0.25 proves equivalence, and distal CE 5'SS SSOs guarantee 0% upstream exon perturbation.", "finding": "CELF5 (#8, iPSC-MN clu_25763_+ padj=0.0090; nominal BA4 p=0.0133/FDR=0.136), ATG4B (#7), and PRUNE2 (#9) replicate, while n=9 SOD1/FUS is underpowered and CELF5's 98-bp micro-intron risks mod3=2 retention.", "gate": "Run Stage-(ii) pre-inclusion cervical alpha-MN BaseScope ISH + Exon 4-7 Nanopore RT-PCR (<1-2% LOQ Exon-5 skip / micro-intron retention)."},
    {"ids": ["C022", "C015", "C023"], "domain": "Mendelian Isoform & chr14q12 Polarity", "naive": "Intron-9 gapmers boost DNAJB2, chr14q12 SCFD1 acts unidirectionally across glia and MNs, and cis-Golgi SNAREs are co-druggable.", "finding": "DNAJB2 has 0/6 TDP-43 cryptic shifts and 25/25 ClinVar P/LP in shared Exons 2-9 vs 0/25 in Zone A; SuSiE (purityMeanR2=0.988) proves one chr14q12 risk haplotype drives MN +0.048 vs iMGL -0.22..-0.33 SCFD1 opposition (PMID:43045849; G2E3 Alu 0mm fail); YKT6 p.Tyr64Cys sits in a -85 A^3 groove.", "gate": "Favor nuclear Intron-9 3'SS or DNAJB2a cDNA over Zone A CDS ASOs, run allele-specific MN+iMGL chr14q12 editing, and restrict YKT6 to Cys195-retaining ternary stabilizers."},
    {"ids": ["C017", "C019"], "domain": "Glial Biomarkers & JAK1/JAK2 Catch-22", "naive": "Elevated CSF CHIT1/GPNMB are drug targets or mimic-specific diagnostics, and 4 mg Baricitinib translates 2.5 uM rescue.", "finding": "Human CHIT1 KO (rs3831317) is ALS-neutral (Trautwig sALS-vs-Ctrl CSF AUC=0.82-0.89; Thompson 2019 mimic AUC=0.51-0.92 [0.688 ext]); 4 mg Baricitinib hits 3.80 nM CSF (1/9 PE + 1/9 DVT in N=9 NADALS) while JAK1-selectives forfeit neuronal JAK2 APA.", "gate": "Deconvolve 3.8-50 nM JAK1 vs JAK1/2 in glia-free vs ALS-Glia co-cultures before any VTE-prophylaxed interaction trial."},
    {"ids": ["S01", "S02", "S05", "S08"], "domain": "Screen Physics, Withheld RCTs & Photolysis", "naive": "2.5 uM screen hits translate orally, NCT04082832 proved CuATSM RCT failure, and -3.60d refutes Methylcobalamin.", "finding": "Dexmedetomidine (7,862x) fails Cu,brain, FTIs block YKT6 prenylation, CuATSM NCT04082832 outcomes remain unreported (hasResults=false; n=6v6 autopsy null), and Co-C photolysis plausibly explains B12's screen drop vs JETALS (+1.97 pts).", "gate": "Enforce unbound human Kp,uu margins, registry-verified RCT status, and dark-vs-lit photolability controls across all screen hits."},
]


def build_edges_and_lenses(port_rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], list[dict[str, object]], list[dict[str, object]]]:
    all_edges = {**CANDIDATE_EDGES_ACTIVE, **CANDIDATE_EDGES_DROPS}
    port_ids = {r["portfolio_id"] for r in port_rows}
    drop_ids = [r["portfolio_id"] for r in port_rows if r["decision"] == "DROP"]
    assert set(CANDIDATE_EDGES_ACTIVE).isdisjoint(CANDIDATE_EDGES_DROPS) and set(all_edges) == port_ids, "Edge IDs != 52 portfolio IDs"
    assert set(CANDIDATE_EDGES_DROPS) == set(drop_ids) and len(drop_ids) == 18, f"Drop edge partition != 18 DROP rows: {len(drop_ids)}"
    role_counts = {k: sum(1 for rk, _ in all_edges.values() if rk == k) for k in EDGE_ROLE_LABELS}
    assert role_counts == {"MECHANISTIC_EDGE": 9, "CROWDED_MULTIPLEX": 2, "HIGH_HURDLE_WATCHLIST": 16, "BENCHMARK_CALIBRATOR": 7, "FALSIFIED_TRAP": 18}, role_counts

    lens_map = {**CANDIDATE_LENSES, "FALSIFIED_TRAPS": drop_ids}
    union_non_all = set().union(*lens_map.values())
    assert union_non_all == port_ids, f"Lens union missing IDs: {port_ids - union_non_all}"
    lenses_out: list[dict[str, object]] = []
    for lk, llbl in LENS_DEFS:
        ids = [r["portfolio_id"] for r in port_rows] if lk == "ALL" else lens_map[lk]
        assert int(llbl.rsplit("·", 1)[1].strip()) == len(ids), f"Lens count label mismatch on {lk}: {llbl} vs {len(ids)}"
        lenses_out.append({"k": lk, "lbl": llbl, "ids": ids})

    edges_out: dict[str, dict[str, str]] = {}
    for pid, (rk, txt) in all_edges.items():
        wcnt = len(txt.split())
        assert 14 <= wcnt <= 62, f"{pid}: edge_text word count {wcnt} out of bounds: {txt}"
        edges_out[pid] = {"edge_kind": rk, "edge_label": EDGE_ROLE_LABELS[rk], "edge_text": txt}

    blob = " ".join([*(v["edge_text"] for v in edges_out.values()), *(str(r) for r in KEY_MECHANISTIC_CONTRASTS_9)])
    assert not re.search(r"exploreals|\bD003\b|\bD045\b|\bDS045\b|Phase\s*3A|/100|Cytosolic\s+vs\.\s+ER", blob, re.I), "Banned token in contrasts!"
    assert not re.search(r"\$\s*\d|\b(?:USD|capital|dollar|dollars|cheap|expensive|budget|fund|funds|funding|funded|cost|costs|evoi)\b", blob, re.I), "Financial token in contrasts!"
    return edges_out, lenses_out, KEY_MECHANISTIC_CONTRASTS_9
