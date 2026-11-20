"""Apply ExploreALS v1.1 primary-source & epistemic updates to registries/candidate_decisions.csv."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REG_DIR = ROOT / "registries"
TS = "2026-11-16T09:15:00Z"


def main() -> None:
    fp = REG_DIR / "candidate_decisions.csv"
    with fp.open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = list(rd.fieldnames or [])
        rows = list(rd)
    dm = {r["carbon_id"]: r for r in rows}

    dm["S02"].update({
        "scientific_taste_rating": "LOW_SOD1_MOUSE_ORIGIN_WITHHELD_RCT_AND_NULL_AUTOPSY",
        "technical_accuracy_of_explore_claim": "VERIFIED_SCREEN_STATS_WITHHELD_RCT_AND_NULL_6VS6_AUTOPSY",
        "causal_vs_reactive_assessment": "SOD1_COPPER_CHAPERONE_ORIGIN_UNPROVEN_IN_HUMAN_TDP43",
        "prior_art_crowding_level": "DISCONTINUED_WITHHELD_PHASE2_3_OUTCOMES",
        "evidence_disproves_hypothesis": "Phase 2/3 placebo-controlled ALS trial NCT04082832 (72 mg/d oral, N=80) completed late 2021 with randomized clinical efficacy withheld/unreported (CT.gov hasResults=false; OLE NCT04313166 terminated and sponsor discontinued ALS development), postmortem neuropathology of treated trial decedents (Yang 2023 PMID:37317638, n=6 vs 6) showed no reduction in pTDP-43 burden or motor neuron loss, 62Cu/64Cu-ATSM PET (Ikawa 2015 PMID:25904686) reflects hypoxic Cu(I) dissociation rather than verified intact 2.5 uM normoxic CNS exposure (~47x nominal gap at 72 mg/d MTD bounded by 144 mg/d Phase 1 transaminitis in NCT02870634), and sporadic TDP-43 ALS lacks human genetic support for SOD1 copper-delivery rescue.",
        "epistemic_state": "UNPROVEN_UNTESTED",
        "decision": "KEEP_EXPLORATORY_UNPROVEN",
        "factual_justification": "Under Epistemic Asymmetry, withheld/unreported randomized Phase 2/3 efficacy outcomes in NCT04082832 (hasResults=false) plus a small observational autopsy series (Yang 2023 PMID:37317638, n=6 vs 6 showing unaltered pTDP-43 and MN loss) do not constitute published powered RCT clinical futility; S02 (CHEMBL4297372) is retained on the low-priority Tier 3 watchlist behind 5 unsolved clinical, neuropathological, PK (~47x screen gap), and mechanistic hurdles.",
        "discriminating_next_test": "Require public release and independent statistical audit of unblinded Phase 2/3 NCT04082832 ALSFRS-R/ECAS outcomes alongside 10-100 nM vs 2.5 uM intact unbound CuATSM concentration-response and radical-trapping ferroptosis target-engagement deconvolution in TDP-43-depleted human sALS iPSC-MNs before any renewed clinical consideration.",
        "updated_at": TS,
    })

    dm["C010"].update({
        "epistemic_state": "FALSIFIED_PK_SAFETY",
        "evidence_disproves_hypothesis": "At 16 mg/d ER MTD (76.9% GI AEs blocking dose escalation), human ALS CSF ropinirole (68.7 nM) sits 14.6-145.6x below 1-10 uM D2R-independent SREBP2/antioxidant potency (PMID:40826812) while human spinal cord lacks DRD3 (0% >=1 CPM); DS005_BYE showed FDR-significant survival harm across 15 sALS iPSC-MN lines (-0.688d, 12/15 negative, q=0.0209); cortical postmortem discovery RNA collapsed after donor GC% adjustment; blinded 24-wk Phase 1/2a ROPALS ALSFRS-R was null (+1.46, 95% CI -3.15 to 6.07, N=20); and Oct 2026 UK Phase 2a EXPERTS-ALS (ISRCTN15525855, 42 dosed / 22 Wk18 analyzed) stopped the ropinirole arm for blood-NfL biomarker futility.",
        "factual_justification": "Insurmountable 15-146x human CSF unbound exposure deficit at GI-limited 16 mg/d MTD (68.7 nM CSF vs 1-10 uM non-D2 rescue with absent spinal DRD3) plus FDR-significant survival harm across 15 human sALS iPSC-MN lines (-0.688d, q=0.0209) and postmortem GC-confounding collapse, corroborated by null blinded 24-wk Phase 1/2a ROPALS (N=20) and Oct 2026 Phase 2a EXPERTS-ALS blood-NfL biomarker futility stop (ISRCTN15525855; biomarker screen, distinct from Phase 3 efficacy).",
        "updated_at": TS,
    })

    for cid in ("C001", "C002", "C006"):
        for k in ("evidence_proves_hypothesis", "evidence_disproves_hypothesis", "factual_justification", "discriminating_next_test"):
            txt = dm[cid][k]
            txt = txt.replace("Ct>35 single-molecule Poisson limits", "late-cycle RT-qPCR (Cq>35) / Poisson-limited 20,000-partition RT-ddPCR (<3-10 copies/mL CSF)")
            txt = txt.replace("Ct>35 Poisson-limited lumbar CSF EV Exon-5/skip RT-ddPCR", "late-cycle RT-qPCR (Cq>35) / Poisson-limited RT-ddPCR on unfractionated CSF EVs")
            txt = txt.replace("Ct>35 Poisson-limited CSF EV cryptic-exon RT-ddPCR", "late-cycle RT-qPCR (Cq>35) / Poisson-limited unfractionated CSF EV RT-ddPCR")
            txt = txt.replace("Ct>35 Poisson-limited CSF EV tSTMN2 RT-ddPCR", "late-cycle RT-qPCR (Cq>35) / Poisson-limited unfractionated CSF EV RT-ddPCR")
            txt = txt.replace("within DEVOTE 50 mg tolerability precedent PMID:41634391", "unvalidated multiplex scenario requiring Ca2+/Mg2+-chelation, DRG, and TLR9 GLP IT tox beyond single-agent DEVOTE 50 mg nusinersen PMID:41634391")
            txt = txt.replace("within DEVOTE 50 mg precedent PMID:41634391", "unvalidated multiplex scenario requiring Ca2+/Mg2+-chelation, DRG, and TLR9 GLP IT tox beyond single-agent DEVOTE 50 mg nusinersen PMID:41634391")
            txt = txt.replace("(DEVOTE 50 mg precedent PMID:41634391)", "(unvalidated multiplex scenario beyond single-agent DEVOTE 50 mg nusinersen PMID:41634391)")
            txt = txt.replace("disfavoring mandatory fixed 3-in-1 co-administration in rs12608932 A/A sALS", "motivating genotype-stratified 2-plex vs 3-plex testing across rs12973192-G/rs12608932-C risk carriers and A/A homozygotes, since severe TDP-43 depletion still induces UNC13A cryptic splicing in A/A")
            txt = txt.replace("adding UNC13A #2 in rs12608932-C/rs12973192-G risk carriers on top of the KCNQ2 + STMN2 core in rs12608932 A/A sALS", "evaluating 2-plex vs 3-plex stratified by rs12973192/rs12608932 genotype rather than excluding A/A patients")
            txt = txt.replace("genotype-modular 2-plex (KCNQ2 + STMN2 in rs12608932 A/A) / 3-plex (+ UNC13A in rs12608932-C/rs12973192-G carriers) splice rescue (Guo et al. 2026) and oral non-covalent SARM1 T-lock epistasis", "genotype-stratified 2-plex vs 3-plex splice rescue across rs12973192/rs12608932 genotypes (Guo et al. 2026) and parallel non-epistatic oral SARM1 T-lock axonal protection (Krus et al. 2022 PMID:35767949)")
            txt = txt.replace("genotype-modular genotype-stratified 2-plex vs 3-plex", "genotype-stratified 2-plex vs 3-plex")
            txt = txt.replace("genotype-modular 2-plex (genotype-stratified 2-plex vs 3-plex across rs12973192/rs12608932 genotypes)", "genotype-stratified 2-plex vs 3-plex (across rs12973192/rs12608932 genotypes)")
            txt = txt.replace("genotype-modular 2-plex (genotype-stratified 2-plex vs 3-plex across rs12973192/rs12608932 genotypes;", "genotype-stratified 2-plex vs 3-plex (across rs12973192/rs12608932 genotypes;")
            txt = txt.replace("2-plex (KCNQ2 + STMN2 in rs12608932 A/A) / 3-plex (+ UNC13A in risk carriers)", "genotype-stratified 2-plex vs 3-plex across rs12973192/rs12608932 genotypes")
            txt = txt.replace("2-plex (KCNQ2 + STMN2 in rs12608932 A/A) / 3-plex (+ UNC13A in rs12608932-C/rs12973192-G carriers) splice rescue (Guo et al. 2026) and oral non-covalent SARM1 T-lock epistasis", "genotype-stratified 2-plex vs 3-plex splice rescue across rs12973192/rs12608932 genotypes (Guo et al. 2026) and parallel non-epistatic oral SARM1 T-lock axonal protection (Krus et al. 2022 PMID:35767949)")
            txt = txt.replace("(KCNQ2 + STMN2 in rs12608932 A/A sALS) vs 3-plex (+ UNC13A in rs12608932-C/rs12973192-G risk carriers;", "(genotype-stratified 2-plex vs 3-plex across rs12973192/rs12608932 genotypes;")
            txt = txt.replace("QRL-201 ANQUR Phase 1/2 (NCT05633459, N=69) human ALS CSF pNfH target-engagement proof", "sponsor-reported interim QRL-201 ANQUR Phase 1/2 (NCT05633459) tissue STMN2 restoration & low-dose DRF subgroup CSF pNfH lowering (~46% at low dose vs ~5% at 10 mg, while 10 mg slowed ALSFRS-R ~50%)")
            txt = txt.replace("QRL-201 (which reported encouraging Phase 1/2 ANQUR NCT05633459 CSF pNfH proof-of-mechanism in N=69)", "QRL-201 (sponsor-reported interim Phase 1/2 ANQUR NCT05633459 tissue STMN2 engagement & low-dose subgroup CSF pNfH reduction)")
            txt = txt.replace("anchoring Phase 1b PD on CSF pNfH/NfL reduction (QRL-201 ANQUR NCT05633459 N=69 human proof-of-mechanism benchmark;", "pairing strand-specific CSF PK -> NHP splice bridging, L1CAM+/ATP1A3+ neuron-derived EV pre-amplified dPCR/Nanopore + CSF synaptic/SCG10 secretome TE, and post-loading (>=16-24 wk) downstream CSF pNfH/NfL PD (accounting for ANQUR NCT05633459 low-vs-10mg pNfH dose dissociation;")
            txt = txt.replace("anchoring Phase 1b PD on CSF pNfH/NfL reduction (QRL-201 ANQUR NCT05633459 N=69 benchmark;", "pairing strand-specific CSF PK -> NHP splice bridging, L1CAM+/ATP1A3+ neuron-derived EV pre-amplified tSTMN2 dPCR/Nanopore + soluble SCG10 TE, and post-loading (>=16-24 wk) downstream CSF pNfH/NfL PD (accounting for sponsor-reported interim QRL-201 ANQUR NCT05633459 ~46% low-dose vs ~5% 10mg pNfH dissociation;")
            txt = txt.replace("log2FC=-0.4825, p=0.0140)", "log2FC=-0.4825, p=0.0140, FDR=0.11, n=20 C9-FTD frontal cortex)")
            txt = txt.replace("resistance to small-molecule Kv7 openers", "ER retention and surface-channel-density ceiling on small-molecule Kv7 openers")
            txt = txt.replace("non-essential mitotic profile (DepMap Chronos=+0.0409)", "dividing cancer-line DepMap Chronos=+0.0409 (whereas postmitotic neuronal Kv7.2 LoF causes DEE7 epilepsy)")
            txt = txt.replace("with CSF pNfH/NfL while treating late-cycle RT-qPCR (Cq>35)", "with L1CAM+/ATP1A3+ NDEV Exon-5/skip pre-amplified dPCR TE and >=16-24 wk post-loading CSF pNfH/NfL PD while treating late-cycle RT-qPCR (Cq>35)")
            dm[cid][k] = txt
        dm[cid]["updated_at"] = TS
    dm["C001"].update({
        "evidence_proves_hypothesis": (
            "Germline GWAS risk (van Rheenen 2021 PMID:34873335 cross-ancestry P=3.0e-25; Open Targets P=4.04e-25 across 6 catalog studies) + sQTL + 100% TDP-43-pathology cryptic exon specificity (Ma 2022 61/860 vs 0/246; Spillman 2026 PMID:42789089 6/10 C9-FTD homogenate vs 0/10 Ctrl, p=0.0108) "
            "+ GC/cell-composition-adjusted NYGC mRNA depletion across all 4 CNS regions (Motor -0.1976 p=0.0105, Frontal -0.1565 p=0.00187, Cervical -0.2912 p=0.00330, Lumbar -0.3554 p=7.38e-4; O'Neill 2025 PMID:40067829 ALS-Glia Cortical n=64 [5 ALS-Glia vs 59 Ctrl]: beta=-0.8266, p=8.62e-4) "
            "+ gnomAD v4.1 extreme LoF intolerance (pLI=1.000, LOEUF=0.344) + published human electrophysiological rescue (Keuss et al. 2026 Nature PMID:43015463, 10.1038/s41586-026-11256-2: isolated Intron-20 CE deletion [~75% protein rescue; >30% synaptic threshold] and 18/21-nt 2'-O-MOE ASOs restore presynaptic UNC13A, mEPSC frequency, evoked AMPA eEPSCs, and MEA network synchrony across human cortical/spinal MNs and hUNC13A mice) prove UNC13A loss causally drives TDP-43 presynaptic failure."
        ),
        "evidence_disproves_hypothesis": (
            "Does NOT disprove biological validity, but deprioritizes standalone me-too single-target ASO monotherapy (crowded by 2 active clinical-stage assets across 4 registry protocols — Lilly LY4256984/QRL-204 parent Ph1 NCT07100119 + substudy NCT07571174 + OLMP NCT07571200 and Trace TRCN-1023 Ph1/2 NCT07674667 + China IIT LAUNCH ALS, plus preclinical AS-241 & UCL tU7 snRNA PMID:41394711 — neither yet with completed Phase 2/3 efficacy proof), "
            "confirms single-target UNC13A CE rescue leaves orthogonal STMN2 polyadenylation, KCNQ2 Exon-5 skipping, Intron-31 retention, and postsynaptic mEPSC amplitude reduction unrescued (Keuss et al. 2026 PMID:43015463; Guo et al. 2026 PMID:42234776), "
            "notes risk alleles rs12608932-C/rs12973192-G potentiate mis-splicing magnitude while severe TDP-43 loss still mis-splices A/A homozygotes (motivating genotype-stratified 2-plex vs 3-plex testing rather than excluding A/A patients), "
            "and confirms soluble CSF UNC13A protein is undetectable (DS045=0 peptides) while unfractionated lumbar CSF EV junction RNA sits in a low-copy Poisson-limited late-Cq regime (requiring ISEV reproducibility controls PMID:38158550 and cryptic-peptide/secretome orthogonalization PMID:38278991)."
        ),
        "factual_justification": (
            "Unlike Riluzole or Methylcobalamin, UNC13A has not yet completed Phase 2/3 human clinical efficacy proof, possesses genome-wide human ALS causal GWAS/sQTL genetics directly inside its cryptic exon (rs12608932/rs12973192; EV-B1-001..EV-B1-005), "
            "and has direct human cortical and spinal motor-neuron electrophysiological rescue proof (Keuss et al. 2026 Nature PMID:43015463: >30% protein threshold restores presynaptic vesicle release and network synchrony while leaving orthogonal STMN2 and KCNQ2 pathways unaddressed). "
            "Standalone me-too single-target ASOs (LY4256984 across 3 Ph1 protocols, TRCN-1023 Ph1/2) are clinically crowded and deprioritized; UNC13A is retained in KEEP_CORE as an orthogonal presynaptic multiplex splice-rescue anchor (evaluating 2-plex vs 3-plex stratified by rs12973192/rs12608932 genotype under 21 CFR 300.50 rather than excluding A/A patients)."
        ),
        "updated_at": TS,
    })
    dm["C006"]["causal_vs_reactive_assessment"] = (
        "SOMATIC_DOWNSTREAM_TDP43_MEDIATOR_OF_HYPEREXCITABILITY: KCNQ2 lacks an ALS germline GWAS locus (somatic TDP-43 downstream effector, unlike UNC13A), "
        "but TDP-43 loss induces 42-aa in-frame deletion (KCNQ2-DeltaE5) that escapes NMD, undergoes soma ER retention / impaired surface trafficking, and co-assembles into pore-dead Kv7.2/7.3 subunits, suppressing M-current and driving intrinsic ALS motor neuron hyperexcitability (Joseph et al. 2025, Nat Neurosci, PMID:41174170)."
    )

    dm["C002"]["technical_accuracy_of_explore_claim"] = dm["C002"]["technical_accuracy_of_explore_claim"].replace(
        "(-0.4825 log2FC, p=0.0140) frontal protein loss",
        "(-0.4825 log2FC, p=0.0140, FDR=0.11, n=20 C9-FTD) frontal protein loss",
    )
    for k in ("evidence_proves_hypothesis", "factual_justification", "discriminating_next_test"):
        dm["C002"][k] = (
            dm["C002"][k]
            .replace("microtubule catastrophe restraint", "plus-end microtubule dynamicity/catastrophe")
            .replace("microtubule-catastrophe/NMJ rescue", "plus-end microtubule-dynamicity/catastrophe & NMJ rescue")
        )
    dm["C005"]["discriminating_next_test"] = dm["C005"]["discriminating_next_test"].replace(
        "(<=5.5 ms)", "(<=5.5% RMT at 1-7 ms ISI, PMID:42592079)"
    )
    dm["C005"]["updated_at"] = TS

    dm["C007"]["evidence_proves_hypothesis"] = dm["C007"]["evidence_proves_hypothesis"].replace(
        "Zhang 2026 spatial anterior horn MN-niche upregulation (+3.7606 log2FC, bh_fdr=1.85e-09)",
        "Zhang 2026 cervical 55-um multicellular MN-niche Visium spot gene-level IL1RL1 upregulation (+3.7606 log2FC, spot-level bh_fdr=1.85e-09 across N=14 donors / 18 sections)",
    )
    dm["C007"]["discriminating_next_test"] = (
        "Execute paired living-patient CSF/plasma Simoa sST2 & free IL-33 (n>=80, explicitly comparing verified normoxic [supine/upright FVC >= 80% PLUS normal overnight oximetry/capnography, PMID:41635251, non-NIV] sALS vs nocturnal-hypoxic/NIV ALS to deconfound 3-20x pulmonary/ventilatory mechanical strain, PMID:30562096, PMID:40402026) + ventilation-matched isolated CNS microvessel/pericyte (PMID:41857656) sST2/ST2L ddPCR (n>=25 sALS vs n>=20 Ctrl; GENCODE v46 1-based sST2 chr2:102343270-102346100(+) vs ST2L Exon 11 chr2:102351536-102352037(+)) + human iPSC neurovascular-microglial tri-culture + ALS CSF causal-vs-compensatory BBB-brake sign testing (PMID:37117777), before generating primary low-dose intrathecal neurovascular-shuttled (CD98hc/SLC3A2 PMID:37598178/PMID:39979268 or monovalent TfR1 PMID:39141703) cytoplasmic sST2 3'-UTR siRNA (PMID:35654979) or uniform 2'-O-MOE Zone 1 Intron-8 PAS/DSE steric SSO (chr2:102346035-102346125(+); Clean >=2mm #1 chr2:102346045-102346062(+); nuclear RNase H1 Intron-8 gapmers & Zone 2 Exon-8 5'SS chr2:102343400-102343435(+) prohibited) vs backup intact-FcRn pH-dependent sST2 aa 324-328 SKECF sweeping mAb (gated on unpaired Cys327 IP-MS thiol-adduct profiling & SLC3A2 -SKEDF counter-screening)."
    )
    dm["C007"]["updated_at"] = TS

    dm["C017"]["name"] = "CHIT1 / GPNMB / CHI3L1-CHI3L2 microglial chitinase-lysosomal staging axis"
    for k in ("evidence_proves_hypothesis", "factual_justification", "discriminating_next_test"):
        dm["C017"][k] = dm["C017"][k].replace("phenoconversion", "cross-sectional symptomatic-vs-asymptomatic staging")
    dm["C017"]["updated_at"] = TS

    for k in ("evidence_disproves_hypothesis", "factual_justification"):
        dm["C019"][k] = dm["C019"][k].replace(
            "2/9 (22.2%) VTEs (1 PE SAE + 1 DVT)",
            "1/9 PE SAE + 1/9 DVT event (1-2/9 [11.1-22.2%] ALS participants; un-deduplicated in NCT05189106 aggregate AE table)",
        ).replace(
            "2/9 (22.2%) NADALS ALS patients suffered VTEs (1 PE SAE + 1 DVT)",
            "NADALS recorded 1/9 PE SAE + 1/9 DVT event across N=9 ALS participants (un-deduplicated in aggregate registry)",
        )
    dm["C019"]["updated_at"] = TS

    dm["S06"]["evidence_proves_hypothesis"] = (
        "Rare constitutively active ARM-domain GoF variants enrich in human ALS (Gilley 2021; Bloom 2022; OT genetic_score=0.195), executing Wallerian NAD+ catastrophe; "
        "elevated protein in small-sample C9FTD iPSC neurons (+0.675, p=0.0268, n=3 vs 3); no population depletion of heterozygous pLoF variants in gnomAD v4 (obs/exp=60/65.1, LOEUF=1.143; distinct from biallelic KO phenotyping)."
    )
    dm["S06"]["evidence_disproves_hypothesis"] = dm["S06"]["evidence_disproves_hypothesis"].replace(
        "Lilly LY3873862 (NCT07883590,", "Lilly LY3873862 (NCT07883590 [Ph1 Not Yet Recruiting],"
    ).replace(
        "bulk lumbar CSF cADPR is overwhelmingly generated by astroglial/leukocyte ecto-CD38",
        "mouse Cd38-/- and axonal studies indicate bulk tissue/fluid cADPR is predominantly generated by ecto-CD38",
    )
    dm["S06"]["factual_justification"] = (
        "Core Track B target backed by human ALS rare GoF genetics, parallel axonal protection alongside STMN2 (Krus et al. 2022 PMID:35767949), "
        "elevated C9-FTD iPSC neuronal protein (+0.675, p=0.0268, n=6, PMID:42789089), and low heterozygous pLoF constraint (LOEUF=1.143); despite clinical activity across 3 programs (LY3873862 NCT07883590 [ALS Ph1 Not Yet Recruiting; HV NCT05492201 N=84 completed], NB-4746 NCT07369076, SIR2501 CTR20253552/NCT07765446), "
        "CNS-penetrant non-covalent inter-protomer ARM-TIR T-lock glues (ASHA-624 class; covalent Cys311 PDB 7DJT as structural benchmark) avoid biphasic base-exchange activation."
    )
    dm["S06"]["discriminating_next_test"] = (
        dm["S06"]["discriminating_next_test"]
        .replace("3-chain TIR-gluing BEXi prodrugs", "3-chain TIR-gluing base-exchange inhibitor (BEXi) prodrugs")
        .replace("(~2-7x modeled threshold sparing)", "(evaluating Bliss/Loewe additivity vs illustrative ~2-7x MWC sensitivity scenario)")
        .replace("(rejecting glial/immune CD38-dominated bulk CSF cADPR, PMID:32087251/PMID:16750163)", "(given mouse Cd38-/- evidence of non-neuronal CD38 background in bulk cADPR, PMID:32087251/PMID:16750163)")
        .replace("intramolecular ARM-TIR", "inter-protomer ARM-TIR")
        .replace("parallel plus-end Bliss", "parallel microtubule-remodeling Bliss")
    )
    dm["S06"]["updated_at"] = TS

    dm["S07"].update({
        "evidence_proves_hypothesis": "In MIROCALS Phase 2b (NCT03039673, PMID:40354799, Lancet May 2025, N=220, 90 deaths; CHEMBL1201438), SAP-prespecified covariate-adjusted Cox + continuous CSF pNfH x Treatment modeling was positive (adj HR=0.32, 95% CI 0.14-0.73, p=0.0070; interaction HR=1.0003/pg/mL, p=0.0011; secondary ALSFRS-R slope interaction F=3.95, p=0.048), with 48% 21-mo mortality hazard reduction in the 750-3,700 pg/mL BioVendor ELISA stratum (n=154, 57 deaths, HR=0.52, 95% CI 0.30-0.89, p=0.016; <750 pg/mL LLOQ n=19 had 0 deaths; pooled <=3,700 pg/mL n=173 HR=0.57, 95% CI 0.33-0.97, p=0.037) alongside sustained Day-112 trough FOXP3+ Treg expansion (p<0.0001) and plasma CCL2 reduction; Al Khleifat et al. 2026 (PMID:42836993, PMC13642438, J Neurol 273:643) showed inside MIROCALS (N=220) that clinical TRICALS risk shares only r^2=12.7% (r=0.357) of variance with CSF pNfH and contributes less treatment-interaction information (nested dChi2=4.76, LRT p=0.029 / Wald p=0.025 vs dChi2=14.24 for pNfH x treatment; adding pNfH to TRICALS dChi2=44.39; combined model reference HR=0.28, 95% CI 0.12-0.63, p=0.002).",
        "evidence_disproves_hypothesis": "Primary unadjusted ITT log-rank test missed significance (HR=0.81, 95% CI 0.54-1.22, p=0.33; >3,700 pg/mL n=47 [33/90 deaths] showed no demonstrated benefit HR=1.37, 95% CI 0.68-2.75, p=0.38), IL2/IL2RA has 0 human ALS genetics, EMA/MHRA/UK MND CSG declined approval pending Phase 3 proof, commercial pNfH immunoassays exhibit ~1.8x-4.5x inter-platform pg/mL calibrator offsets (PMID:31251725; PMID:29054919; cf. BioVendor ELISA in PMID:40354799 vs MSD ECLIA cited in PMID:42836993), Phase 2/3 ALSTARS (NCT07161999, N=137 enrolled, prospectively stratified across 3 baseline serum NfL tiers on 24-wk ALSFRS-R) tests dual-biologic COYA 302 (1 MIU rhIL-2 + 125 mg CTLA4-Ig q14d vs q28d; <0.5% BBB entry, CD28 blockade PMID:30683697/PMID:36920087 vs IL-2 STAT5 rescue PMID:42086904) without baseline CSF pNfH exclusion or a single-agent IL-2 arm, ALS FOXP3+ Tregs risk TSDR methylation drift + NK/eosinophil/sCD25 sinks, and zero prospective Phase 3 trials gated on calibrated CSF pNfH <=3,700 pg/mL have completed.",
        "factual_justification": "Under Epistemic Asymmetry, covariate-adjusted survival benefit (HR=0.32, p=0.0070) and <=3,700 pg/mL BioVendor ELISA benefit (750-3,700 HR=0.52, p=0.016, n=154; pooled <=3,700 HR=0.57, p=0.037, n=173) inside an unadjusted-ITT-null Phase 2b trial (MIROCALS PMID:40354799, HR=0.81, p=0.33) with zero IL2/IL2RA ALS genetics require prospective biomarker-gated Phase 3 confirmation.",
        "discriminating_next_test": "Complete pre-Phase-3 CLSI EP09c (N>=40 paired ALS CSFs spanning the measuring interval) Passing-Bablok analytical bridging from MIROCALS BioVendor ELISA CSF pNfH (~79th percentile, <=3,700 pg/mL: n=173/220) to automated CLIA immunoassays (Ella/Euroimmun/Simoa/MSD; resolving ~1.8x-4.5x inter-platform calibrator offsets, PMID:31251725, PMID:29054919; cf. Al Khleifat 2026 PMID:42836993 where TRICALS shares r^2=12.7% with CSF pNfH and nested pNfH x trt dChi2=14.24 vs TRICALS x trt dChi2=4.76), plus paired immunoassay validation before substituting blood NfL or pNfH for CSF pNfH (noting Trautwig 2025 PMC12082929 tryptic CSF MS NEFL-NEFH r=0.278 across n=77 DIA / n=51 overlapping Emory TMT vs clinical immunoassay serum NfL-CSF pNfH rho=0.64-0.71 PMID:38683209 and serum NfL outperforming serum pNfH on ALSFRS-R slope PMID:32385188; post-hoc NX210c SEALS NCT06365216 NfL<=95 pg/mL p=0.062; note enrolled N=137 ALSTARS NCT07161999 stratifies 3 serum NfL tiers on 24-wk ALSFRS-R with dual-biologic rhIL-2 + CTLA4-Ig and no single-agent IL-2 arm, so ALSTARS cannot directly falsify single-agent S07), then execute an event-driven Phase 3 RCT powered for 247 deaths at conservative unadjusted HR=0.70 (80.0% power; 138 deaths at HR=0.62 [MODEL_PRIOR]; N~650-750 over 36-42 mo variable follow-up or N~850-1,050 at 24 mo, <5% vital-status censoring, accounting for 0 deaths in <750 pg/mL n=19/220 MIROCALS LLOQ floor and pre-specifying complementary TRICALS + log[CSF pNfH] covariates — whereas hypothetical unbridged 1.8x-4.5x lower CSF cutoffs admit 74-99% of >3,700 pg/mL patients and reduce 247-death one-sided superiority power to ~43-50% if HR_high=1.00 or ~14-23% if HR_high=1.37 [MODEL_PRIOR]) enrolling calibrated ~79th-percentile CSF pNfH <=3,700 pg/mL with longitudinal Treg TSDR (PMID:17694575), CD56bright NK, and serum sCD25 (PMID:32651161; PMID:22343569) monitoring.",
        "updated_at": "2026-11-20T00:10:00Z",
    })

    dm["S08"]["evidence_disproves_hypothesis"] = (
        "Efficacy is restricted to early <=12-month onset (prior <3yr trial NCT00444613 N=373 missed ITT), and unshielded 2.5 uM methylcobalamin scored -3.60d (q=0.00246, Rank #105/107) in Bye 2025, plausibly explained by blue-light live-imaging Co-C bond photolysis (hypothesis requiring dark-shielded vs lit control verification)."
    )
    dm["S08"]["factual_justification"] = (
        "Clinically proven and PMDA-approved (Sept 2024) standard-of-care benchmark in early-onset (<=12m) ALS (+1.97 ALSFRS-R pts in Phase 3 JETALS, p=0.01); also highlights plausible Co-C photolability false-negative risk in unshielded live-imaging iPSC screens."
    )
    dm["S08"]["updated_at"] = TS

    with fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    print("Stage 2B (candidate_decisions.csv) OK")


if __name__ == "__main__":
    main()
