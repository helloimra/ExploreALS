"""Apply ExploreALS v1.1 primary-source, epistemic, & bioanalytical corrections to base registries."""
from __future__ import annotations

import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _wave_b_v1_2_7_ev_sub import apply_wave_b_ev_and_sub_patches  # noqa: E402
from _wave_b_v1_2_7_ev_sub_b import apply_wave_b_ev_and_sub_part_b  # noqa: E402
from _wave_c_v1_2_8_evidence_subnodes import apply_wave_c_ev_and_sub_patches  # noqa: E402
from _wave_d_v1_2_9_evidence_a import apply_wave_d_evidence_part_a  # noqa: E402
from _wave_d_v1_2_9_evidence_b import apply_wave_d_evidence_part_b  # noqa: E402
REG_DIR = ROOT / "registries"
TS = "2026-11-16T09:15:00Z"


def _load(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (REG_DIR / name).open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or []), list(rd)


def _save(name: str, cols: list[str], rows: list[dict[str, str]]) -> None:
    with (REG_DIR / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    # 1. evidence_ledger.csv
    ev_cols, ev_rows = _load("evidence_ledger.csv")
    ev_map = {r["evidence_id"]: r for r in ev_rows}

    ev_map["EV-B1-001"].update({
        "source_type": "MAJIQ_UNC13A_CRYPTIC_SPLICING_RECOMPUTE",
        "source_id_or_locator": "DS_CRYPTIC:Brown2022_MOESM11;PMID:35197628;DOI:10.1038/s41586-022-04436-3",
        "cohort_and_stratum": "Brown et al. 2022 human i3Neuron TDP-43 CRISPRi KD vs Control MAJIQ splicing (LSV ENSG00000130477.15:s:17642845-17642960)",
        "assay_and_contrast": "MAJIQ novel_acceptor cryptic junction (chr19:17642541-17642845, MOESM11 line 983)",
        "effect_estimate": "deltaPSI=+0.4632 (0.001 -> 0.476; source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=2.310e-19, p_d_psi_0_10=1.000, junc_cat=novel_acceptor, MOESM11 line 983)",
        "fdr_or_adjusted_p": "",
        "notes": "Brown 2022 MOESM11 line 983 classifies chr19:17642541-17642845 as junc_cat=novel_acceptor (source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=2.31000e-19, p_d_psi_0_10=1.000, stored separately from frequentist adjusted p-values; paired canonical dPSI=-0.5868, source MAJIQ 'FDR'=1.50e-13); separate MOESM12/13 DESeq2 gene RNA log2FC=-0.2508 (BH-FDR padj=1.14e-5) and Ribo-seq log2FC=-0.7811 (BH-FDR padj=0.0296); replicated separately in Ma 2022 MAJIQ dPSI=0.779; in cellular & humanized mouse assays, Keuss et al. 2026 (Nature, PMID:43015463, 10.1038/s41586-026-11256-2; preceded by Chi et al. 2024 Les Turner 14th Annual ALS Research Symposium Poster 24 and patent filings CA3213590A1 [ASO-121/132] & US20240301415A1 [1616106]) show isolated Intron-20 CE deletion (~75% protein rescue; >30% cellular synaptic threshold) and 18/21-nt 2'-O-MOE ASOs (~35.8% full-length splicing / ~62.2% protein in patient iPSC-MNs, Fig. 3c,f) restore presynaptic UNC13A, mEPSC frequency, evoked AMPA eEPSCs, and MEA network synchrony (noting Fig. 4c-e p=0.052 on one motor-neuron electrophysiology sub-panel, while postsynaptic mEPSC amplitude reduction and orthogonal STMN2/KCNQ2 pathways remain unrescued). [Sample context: i3Neuron TDP-43 KD vs Ctrl replicates (Brown 2022 MOESM11)]",
    })
    ev_map["EV-B1-006"]["notes"] = (
        "Paired Brown 2022 MOESM11 line 4857 MAJIQ novel_acceptor exon-2a dPSI=+0.4820 (0.000 -> 0.495, source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=3.02e-18, p_d_psi_0_10=1.000; distinct from this row's primary MOESM13 DESeq2 Ribo-seq BH-FDR=1.57e-173); "
        "Zeng 2025 intronic PAS chr8:79617048:+ dPAS=+0.4564 (padj=0); Bryce-Smith 2025 NYGC 100% specificity: 383/926 (41.36%) TDP-path vs 0/750 non-path across 1,676 libraries (10/10 KD cohorts sig). [Sample context: i3Neuron TDP-43 KD vs Ctrl Ribo-seq replicates (Brown 2022 MOESM13)]"
    )
    ev_map["EV-B1-004"].update({
        "cohort_and_stratum": "Spillman 2026 C9-FTD vs Control frontal cortex homogenate RNA-seq (10 C9-FTD vs 10 Ctrl)",
        "effect_estimate": "6/10 C9-FTD (mean PSI=2.30%, 26 CE reads) vs 0/10 Control",
        "notes": "Homogenate RNA-seq PSI Mann-Whitney p=0.00597 (synaptosome RNA-seq CE p>0.9999 in PMID:42789089); paired Spillman synaptosome DIA protein log2FC=-0.2496 (Welch p=0.0502, padj=0.3442, n=20); undetected (0 peptides) in Trautwig 2025 CSF TMT & DIA.",
    })
    ev_map["EV-B1-009"].update({
        "cohort_and_stratum": "Spillman 2026 C9-FTD vs Control frontal cortex homogenate DIA proteomics (10 C9-FTD vs 10 Ctrl)",
        "notes": "Paired Spillman MOESM5 CE junctions detected in 10/10 C9-FTD (mean PSI=7.71%, 77 reads) vs 0/10 Ctrl (Fisher p=1.08e-5, PMID:42789089); homogenate DIA nominal p=0.0140, padj=0.113; Trautwig 2025 DIA CSF undetected.",
    })
    ev_map["EV-B1-011"].update({
        "source_type": "MAJIQ_KCNQ2_EXON5_SKIP_SPLICING_RECOMPUTE",
        "source_id_or_locator": "DS_CRYPTIC:Brown2022_MOESM11;PMID:35197628;DOI:10.1038/s41586-022-04436-3",
        "cohort_and_stratum": "Brown et al. 2022 human i3Neuron TDP-43 CRISPRi KD vs Control MAJIQ splicing (LSV ENSG00000075043.18:s:63444659-63444834)",
        "assay_and_contrast": "MAJIQ novel_exon_skip in-frame Exon-5 skipping junction (chr20:63439708-63444659, MOESM11 line 4527)",
        "effect_estimate": "deltaPSI=+0.2139 (0.000 -> 0.236; source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=4.153e-24, p_d_psi_0_10=0.999994, junc_cat=novel_exon_skip, MOESM11 line 4527)",
        "fdr_or_adjusted_p": "",
        "notes": "Brown 2022 MOESM11 line 4527 MAJIQ novel_exon_skip output (source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=4.15270e-24, p_d_psi_0_10=0.999994, stored separately from frequentist adjusted p-values; paired canonical dPSI=-0.2230, source MAJIQ 'FDR'=0); separately replicated in Ma et al. 2022 MOESM5 (MAJIQ dPSI=0.451, LeafCutter dPSI=0.243, LeafCutter cluster BH-FDR=1.45e-5, PMID:35197626); separate Brown MOESM12/13 DESeq2 whole-gene RNA log2FC=+0.0779 (BH-FDR padj=0.2286) and Ribo-seq +0.2350 (BH-FDR padj=0.9828) show no statistically significant whole-gene reduction (which alone cannot establish isoform-specific NMD escape), whereas dedicated characterization in Joseph et al. 2025 (Nat Neurosci PMID:41174170, DOI:10.1038/s41593-025-02096-w) directly demonstrates translated, ER-retained KCNQ2-DeltaE5 protein. [Sample context: i3Neuron TDP-43 KD vs Ctrl replicates (Brown 2022 MOESM11)]",
    })
    ev_map["EV-B1-014"].update({
        "cohort_and_stratum": "Spillman 2026 C9-FTD vs Control frontal cortex synaptosome DIA proteomics (10 C9-FTD vs 9 Ctrl)",
        "effect_direction": "STABLE_HOMOGENATE_ER_RETAINED_CSF_ABSENT",
        "notes": "Spillman iPSC homogenate log2FC=-0.1493 (p=0.6487, n=6); undetected (0 peptides) in Trautwig 2025 CSF TMT & DIA; Joseph et al. 2025 (PMID:41174170, DOI:10.1038/s41593-025-02096-w; Exon-5 splice-rescue ASO series claimed in QurAlis WO2023102548A1 [SEQ IDs 758/759, 465, 460] & Northwestern/UMass WO2024206195A1 [smKCNQ2]) directly demonstrates translated KCNQ2-DeltaE5 protein accumulating in soma ER with impaired surface trafficking (alongside non-significant whole-gene Brown Ribo-seq padj=0.983; cortical P2 synaptosome null reflects sparse cortical TDP-43 pathology + co-fractionated ER across non-Exon-5 peptides). [Sample context: 19 postmortem frontal cortex synaptosome preps (10 C9-FTD vs 9 Ctrl)]",
    })
    ev_map["EV-B3-001"].update({
        "cohort_and_stratum": "Prudencio 2015 QC-passing paired sALS (n=8) vs Healthy (n=7) Frontal & Cerebellum (of 18 deposited paired donors)",
    })
    ev_map["EV-B3-003"].update({
        "cohort_and_stratum": "Edinburgh cortical Endothelial pseudobulk (n=25 ALS [23 non-C9 sALS] vs n=7 Ctrl donors, min_nuclei>=5, XIST/UTY-verified PMID:42551425)",
    })
    ev_map["EV-B3-004"].update({
        "cohort_and_stratum": "Zhang 2026 human cervical spinal cord 55-um multicellular MN-niche Visium spots (n=14 of 18 cervical sections retaining MN-enriched spots)",
        "assay_and_contrast": "Spot-level Seurat MAST spatial differential expression ALS vs HC (6d_MN_ALS_vs._HC; gene-level IL1RL1)",
        "notes": "Strong anterior horn perineuronal/microvascular gene-level IL1RL1 upregulation across multicellular 55-um Visium CytAssist spots (n=14/18 sections, Seurat MAST with cellular detection rate covariate; concordant with Cooper-Knock LCM +4.735 log2FC, whereas Pineda BA4 pooled vascular snRNA is null at +0.075 log2CPM, p=0.918, n=31; may include mural pericytes per Jansson 2026 PMID:41857656), masked in whole-cord bulk homogenates; isoform-specific sST2 vs ST2L assays required.",
    })
    ev_map["EV-B5-010"]["notes"] = ev_map["EV-B5-010"]["notes"].replace("Guo 2025 PMID:41174170", "Joseph et al. 2025 PMID:41174170")
    ev_map["EV-P2-T2-003"]["source_id_or_locator"] = "DS003_PB:BA4_Excitatory;PMID:38521060"
    ev_map["EV-P2-T4-001"].update({
        "source_id_or_locator": "DS_EDIN_PB;DS_PDB_4KC3;GENCODE_v46;PMID:42551425;PMID:23980170;PMID:41765683",
        "cohort_and_stratum": "UMI-pooled donor-collapsed Edinburgh cortical endothelium (n=28 unique donors at min_nuclei>=10: 21 non-C9 sALS vs 7 Ctrl, XIST/UTY-verified, PMID:42551425) & PDB 4KC3 IL-33-ST2 complex",
        "effect_estimate": "Endo diff_log2CPM=+3.1067 (p=0.00698; all ALS +2.8427, p=0.0115, n=30; n=7 Ctrl caveat; Pineda BA4 vascular +0.075 p=0.918; XIST/UTY swap-immune H5AD); 4KC3 (resolved aa 21-317) 30 ST2 D1-D3 contacts (10 Cys = 5 closed disulfides, leaving sequence-deduced Cys327 in 324-SKECF-328 unpaired) -> at perivascular 400pM sST2 (vs ~5pM bulk CSF PMID:37117777), [MODEL_PRIOR] 5nM pan-ST2 suppresses Treg ST2L (3.2%->0.32%) vs 80% RNA suppression (11.8%) or intact-FcRn sweeping (28.2%)",
        "p_value": "0.00698",
        "sample_size_n": "28",
        "notes": "GENCODE v46 1-based GTF maps soluble sST2 (ENST00000311734.6) to intron-8 polyA exon chr2:102343270-102346100(+) (AATAAA 102346074-102346079(+); Zone 1 PAS #1 chr2:102346045-102346062(+) mRNA/50bp-SS 0/0 [boundary_dist_bp=40, Caution on 25bp-SS 2mm=1]; Zone 2 Exon-8 5'SS 102343400-102343435(+) & nuclear Intron-8 gapmers prohibited; cf. sST2 decoy patents US20080003199A1 & WO2024246589A1, null sALS serum/CSF sST2 in Italiani 2014 PMID:24884937, & compartment-divergent Pan 2026 PMID:42698373 [plasma IL1RL1/ST2 case-status elevation ST5 beta=0.41, q=0.00464 with null survival ST8/9 & null corrected plasma functional slope ST10, vs CSF IL1RL1 association with respiratory functional decline ST11/14]; PDB 4KC3 resolves aa 21-317 [construct aa 321] with 10/10 D1-D3 Cys paired, so Cys327 in 324-SKECF-328 is sequence-deduced as an odd 11th unpaired thiol [ALS CSF redox state unmeasured] alongside sole 4/5 C-terminome homolog SLC3A2 -SKEDF across 89,484 transcripts, whereas pan-ST2 astegolimab missed Phase 3 ARNASA p=0.068 PMID:42150581). [Sample context: 28 unique donors at min_nuclei>=10 (21 non-C9 sALS vs 7 Ctrl)]",
    })
    ev_map["EV-B3-006"]["sample_size_n"] = ""
    ev_map["EV-B3-007"]["notes"] = (
        ev_map["EV-B3-007"]["notes"].split("; Thompson 2019")[0]
        + "; Thompson 2019 (PMID:31123140) shows standalone CSF chitinase AUC spans 0.51-0.92 (0.688 vs neurological ALS mimics), confirming symptomatic staging/PD utility rather than standalone mimic diagnosis."
    )
    ev_map["EV-B3-017"]["notes"] = ev_map["EV-B3-017"]["notes"].replace(
        "WashU & UMilan contributed 63 ALS, 0 Controls",
        "UMilan contributed 31 ALS / 0 Controls and WashU contributed 26 ALS code 100 + 6 comparators code 741 (2 Controls + 4 asymptomatic carriers; unresolved Table 2 26/84 vs MOESM1 32/78 bank count)",
    )
    ev_map["EV-B2-011"].update({
        "source_type": "MAJIQ_GOSR1_SPLICING_RECOMPUTE",
        "source_id_or_locator": "DS_CRYPTIC:Brown2022_MOESM11;PMID:35197628;DOI:10.1038/s41586-022-04436-3",
        "cohort_and_stratum": "Brown et al. 2022 human i3Neuron TDP-43 CRISPRi KD vs Control MAJIQ splicing (LSV ENSG00000108587.15:s:30480856-30481342)",
        "assay_and_contrast": "MAJIQ splicing of annotated 6-bp in-frame GOSR1 a5ss junction (chr17:30481263-30484214, MOESM11 line 5690)",
        "effect_estimate": "GOSR1 a5ss PSI 0.410->0.537 (dPSI=+0.1142, source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=3.272e-06, p_d_psi_0_10=0.5825, mod_3=0, junc_cat=annotated, cryptic_junction=False, MOESM11 line 5690)",
        "fdr_or_adjusted_p": "",
        "notes": "Mislabeled alt-3'ss in baseline intake; Brown 2022 MOESM11 line 5690 MAJIQ output (3.27157e-06 is MAJIQ's per-junction p_d_psi_0_05_per_lsv_junction output renamed 'FDR' in parsing_voila_delta.R alongside p_d_psi_0_10=0.5825, stored separately from frequentist adjusted p-values) shows an annotated 2-codon donor shift with null separate Brown MOESM12 DESeq2 KD RNA-seq (log2FC=+0.0187, p=0.7301, BH-FDR padj=0.8538) & MOESM13 Ribo-seq (p=0.1383, BH-FDR padj=0.8796), null Trautwig Set 2 DIA CSF sALS vs Ctrl (diff=-0.1852, p=0.3550, n=122), and null Spillman MOESM1 cortex DIA protein (Homog log2FC=-0.4811, p=0.1055, padj=0.3394, n=7 vs 9; Synapt -0.1794, p=0.3022, n=9 vs 10); DepMap Chronos=-0.1430. [Sample context: i3Neuron TDP-43 KD vs Ctrl replicates (Brown 2022 MOESM11)]",
    })
    ev_map["EV-B2-014"].update({
        "source_type": "MAJIQ_PTAR1_EXON2_SKIP_SPLICING_RECOMPUTE",
        "source_id_or_locator": "DS_CRYPTIC:Brown2022_MOESM11;DS_GENCODE_V46_COMP_GTF:ENST00000340434.5;PMID:35197628",
        "cohort_and_stratum": "Brown et al. 2022 human i3Neuron TDP-43 CRISPRi KD vs Control MAJIQ splicing (LSV ENSG00000188647.13:t:69741516-69741858)",
        "assay_and_contrast": "MAJIQ novel_exon_skip (chr9:69741858-69759853(-)) skipping 170-bp Exon 2 (chr9:69750781-69750950(-), mod_3=2) of GGTase-III subunit PTAR1 (MOESM11 line 4145)",
        "effect_estimate": "PTAR1 Exon-2 skip group E(PSI) 0.156->0.369 (raw diff +0.213; MAJIQ shrunk dPSI=+0.1563, source MAJIQ 'FDR' [p_d_psi_0_05_per_lsv_junction]=3.256e-06, p_d_psi_0_10=0.6995, MOESM11 line 4145; 170 bp mod_3=2 frameshift; canonical dPSI=-0.1563)",
        "fdr_or_adjusted_p": "",
        "notes": "Same Brown 2022 MOESM11 line 4145 MAJIQ junction evaluated on EALS-023 (EV-P4-008), where 3.25568e-06 is MAJIQ's per-junction p_d_psi_0_05_per_lsv_junction output renamed 'FDR' via setnames in parsing_voila_delta.R alongside p_d_psi_0_10=0.699459 (stored separately from frequentist MOESM12/13 DESeq2 gene BH-FDR padj=0.1436/0.9987): GGTase-III (PTAR1/RABGGTB, PDB 6J74 PMID:32128853) requires prior FTase Cys195 farnesylation to geranylgeranylate YKT6 Cys194, so FTIs are predicted to impair YKT6 diprenylation atop TDP-43 YKT6 APA + PTAR1 Exon-2 skipping. [Sample context: i3Neuron TDP-43 KD vs Ctrl replicates (Brown 2022 MOESM11)]",
    })
    ev_map["EV-B3-020"].update({
        "effect_estimate": "MERIDIAN Week 52 CAFS rank LS mean diff -3.0 (123.0 vs 126.0, 95% CI -19.5 to +13.5); C3 LOEUF=0.552",
        "notes": "N=249 enrolled / N=247 mITT analyzed: SC pegcetacoplan (1,080 mg BIW, ~43.5 kDa PEGylated peptide, unmeasured human CSF PK with limited intact-BBB entry expected against a 1,575.28 TPM hepatic C3 sink) missed Week 52 primary CAFS rank score (123.0 [SE 4.71] vs 126.0 [SE 6.89], ANCOVA LS mean diff -3.0, p=0.7205) and all secondary endpoints alongside Phase 3 CHAMPION-ALS ravulizumab (NCT04248465, PMID:37695623) & Phase 2/3 HEALEY zilucoplan (NCT04436497, PMID:39960672) futility.",
    })
    ev_map["EV-B3-022"].update({
        "cohort_and_stratum": "Zhang 2026 human cervical spinal cord 55-um multicellular TDP-43+ anterior horn Visium spots (N=14 donors)",
        "assay_and_contrast": "Spot-level Seurat MAST spatial differential expression ALS vs HC on C1QB (with C1QA/C1QC/C3/C4B in notes)",
    })
    ev_map["EV-B6-035"].update({
        "effect_direction": "unreported_rct_outcomes",
        "effect_estimate": "Randomized efficacy unreported (CT.gov hasResults=false; completed late 2021, OLE NCT04313166 terminated)",
        "epistemic_weight": "MODERATE",
        "notes": "Collaborative Medicinal Development completed Phase 2/3 NCT04082832 in late 2021 with no posted randomized ALSFRS-R/ECAS outcomes (hasResults=false; OLE NCT04313166 terminated and ALS/MND International Alliance moved CuATSM to discontinued); 62Cu/64Cu-ATSM PET reflects hypoxic Cu(I) reductive trapping rather than verified intact 2.5 uM normoxic CNS exposure (PMID:25904686).",
    })
    ev_map["EV-B6-036"].update({
        "source_id_or_locator": "PMID:37317638;DOI:10.1111/nan.12919",
        "epistemic_weight": "MODERATE",
        "notes": "Postmortem neuropathology of 6 oral CuATSM-treated (72 mg/d) ALS trial decedents vs 6 untreated ALS comparators showed no significant reduction in pTDP-43 pathology or motor neuron loss alongside higher motor-cortex p62+ astrocyte density and lower spinal Iba1+ microglial density (small observational autopsy series, not randomized clinical efficacy). [Sample context: 6 CuATSM-treated vs 6 untreated ALS postmortem cases]",
    })
    ev_map["EV-B6-043"].update({
        "cohort_and_stratum": "Human ALS rare-variant cohorts, Open Targets & gnomAD v4.1",
        "effect_estimate": "OT genetic_score=0.195; Open Targets LoF=60/65.1 (LOEUF=1.143, pLI=2.75e-19; gnomAD v4.1 MANE LOEUF=1.413, 60/52.6)",
        "notes": "Constitutively active SARM1 ARM-domain GoF variants enrich in human ALS while Open Targets / legacy constraint (LOEUF=1.143, 60/65.1) and gnomAD v4.1 MANE (LOEUF=1.413, 60/52.6) show no population depletion of heterozygous pLoF variants (distinct from clinical biallelic KO phenotyping or chronic pharmacological inhibition).",
    })
    ev_map["EV-B6-044"].update({
        "epistemic_weight": "MODERATE",
        "notes": "Elevated SARM1 protein in small-sample C9FTD iPSC-neurons (n=3 vs 3, p=0.0268); note Stmn2 depletion acts in a parallel pathway rather than linearly lowering axonal NMNAT2 or activating SARM1 in mouse motor axons (Krus et al. 2022 PMID:35767949); end-stage NYGC Frontal RNA=-0.3066 reflects projection-neuron dropout.",
    })
    ev_map["EV-B6-045"].update({
        "cohort_and_stratum": "Clinical SARM1 programs (LY3873862 NCT05492201 completed N=84 HV + ALS Ph1 NYR NCT07883590; NB-4746 ALS Ph1/2 NCT07369076; NB-9402 HV Ph1 ACTRN12626000650392; SIR2501 ALS Ph1b/2a CTR20253552 + CIPN Ph2 NCT07765446) & 2026 medchem audit",
        "effect_estimate": "4 clinical SARM1 programs across 3 sponsors (Lilly LY3873862 NCT07883590 [ALS Ph1 NYR; N=84 HV NCT05492201 completed]; Nura/TRICALS NB-4746 NCT07369076 + NB-9402 ACTRN12626000650392; Sironax SIR2501 CTR20253552/NCT07765446) + preclinical ASHA-624",
        "notes": "Moderate clinical crowding across clinical SARM1 programs (originating small-molecule isoquinoline base-exchange scaffolds in Bosanac et al. 2021 PMID:33964142); PMID:42156967 (PDB 9TZY BEXi adduct 17) and PMID:42380237 (122/122 BEIs across 7 series activate SARM1 below IC50 with median 8.6-fold [IQR 5.1-9.7] IC50/C_act separation) warn orthosteric base-exchange scaffolds risk sub-inhibitory SARM1 activation, favoring non-covalent inter-protomer ARM-TIR allosteric T-lock glues (PDB 7DJT Glu252-Gln585 3.2-3.3A polar interface proximity; ASHA-624 class; covalent Cys311 PDB 7DJT serves strictly as a structural octamer benchmark, with Cys311Ala selectivity gated prospectively).",
    })
    ev_map["EV-P2-T2-002"].update({
        "source_id_or_locator": "RUN-P2-T2-002:mwc_8mer_epistasis;PMID:42380237;PMID:35767949;NCT07883590;NCT07369076",
        "effect_estimate": "[MODEL_PRIOR] Illustrative low-reserve BEXi washout spike ~2.8x (L0=2.5; 8-mer ceiling ~45x WT / ~5x ALS; cf. Leahey 2025 PMID:42380237 empirical 8.6x [IQR 5.1-9.7] IC50/C_act concentration shift across 122 BEIs); T-lock=0 spike by model construction (~82% inhib at 0.3x Kd; IC90 ~0.45x Kd); STMN2+SARM1 spans 1.0x parallel plus-end Bliss lower bound to ~2-7x (med ~3x) NMNAT2-epistatic upper bound",
        "notes": (
            "Krus et al. 2022 (PMID:35767949) & Lopez-Erauskin et al. 2024 (PMID:37996528) prove Sarm1-/- does NOT rescue Stmn2-/- neurofilament collapse in vivo (and White et al. 2019 PMID:31661035 showed Sarm1-/- preserved TDP-43Q331K MN axons/NMJs without improving rotarod latency), "
            "establishing parallel biological non-redundancy of STMN2 rescue + non-covalent ARM-TIR SARM1 T-locks (ASHA-624 class; covalent Cys311 PDB 7DJT used strictly as a structural benchmark, and zero T-lock spike / ~2.8x low-reserve BEXi spike / ~2-7x MWC sparing framed strictly as model-by-construction illustrative sensitivity scenarios)."
        ),
    })
    ev_map["EV-P2-T1-001"]["notes"] = (
        "Preserves C-terminal helices A-D while excising Trp236 (3.00A NE1-O3 H-bond / 2.97A closest CZ2-O3 contact to retigabine in PDB 7CR2) and inducing soma ER retention / impaired surface trafficking of KCNQ2-DeltaE5 (Joseph et al. 2025 PMID:41174170 Fig. 3h: 117.3 vs 208.6 pA/pF at +40 mV = 56.2% residual current / 43.8% loss at 1:1 in CHO-KCNQ3; smKCNQ2 naming & Exon-5 splice-rescue ASO series claimed in WO2023102548A1 [SEQ IDs 758/759, 465, 460] & WO2024206195A1; modeled 38.2% [2:2 Kv7.2:Kv7.3] to 61.8% [4:0 Kv7.2] poisoned channels at dPSI=0.2139 [MODEL_PRIOR]), "
        "imposing a surface-channel-density ceiling on small-molecule Kv7 pore openers."
    )
    ev_map["EV-B6-046"]["notes"] = (
        "Primary unadjusted ITT log-rank test missed significance (HR=0.81, 95% CI 0.54-1.22, p=0.33; SAP-prespecified covariate-adjusted Cox conditional HR=0.32 at reference pNfH=0, p=0.0070 with continuous CSF pNfH interaction HR=1.0003/pg/mL, p=0.0011; secondary ALSFRS-R slope interaction F=3.95, p=0.048); EMA/MHRA declined approval; fixes intake CHEMBL1201585 (Trastuzumab) typo -> CHEMBL1201438."
    )
    ev_map["EV-B6-047"].update({
        "cohort_and_stratum": "MIROCALS BioVendor ELISA Low/Moderate CSF pNfH stratum (750-3700 pg/mL, n=154; <750 pg/mL LLOQ n=19 analyzed separately)",
        "notes": "Primary unadjusted ITT HR=0.81 (p=0.33); MIROCALS SAP pre-specified covariate-adjusted Cox + continuous CSF pNfH x Treatment interaction (conditional adj HR=0.32 at reference pNfH=0, 95% CI 0.14-0.73, p=0.0070; interaction HR=1.0003/pg/mL, p=0.0011), partitioned via baseline CSF pNfH visual distribution assessment in mmc1.pdf pp. 13, 23 alongside survival cutoff comparisons across pNfH thresholds in WO2024121173A1 (cf. WO2021176044A1; temporal order/independence unresolved) into 750-3700 pg/mL (HR=0.52, p=0.016, n=154, 57 deaths), <750 pg/mL LLOQ (n=19, 0 deaths; pooled <=3700 pg/mL n=173/220 [56.9% of all 304 screened who were both randomized and <=3700 pg/mL] HR=0.57, p=0.037), and >3700 pg/mL no demonstrated benefit (HR=1.37, 95% CI 0.68-2.75, p=0.38, n=47, 33/90 [36.7%] deaths; ALSFRS-R slope interaction F=3.95, p=0.048; Day-112 trough Tregs p<0.0001 and plasma CCL2 p<0.05 [p<0.0001 at Days 8 & 120; CSF CCL2/pNfH NS at Day 112]).",
    })
    ev_map["EV-B6-051"].update({
        "effect_direction": "photolysis_false_negative_hypothesis",
        "notes": "Mechanistic chemical photolability hypothesis: routine blue-light live imaging cleaves the photosensitive Co-C bond of methylcobalamin into phototoxic species (-3.60d in Bye 2025, which lacked a dark-shielded control well), reconciling in vitro toxicity with Japanese Phase 3 JETALS early-stage (<=1 yr from onset) benefit (+1.97 pts, PMID:35532908).",
    })
    ev_map["EV-P2-T3-004"].update({
        "source_id_or_locator": "DS045_TRAUT:TMT_ALS51_DIA_ALS79;PMID:40354799;PMID:42836993;PMID:38683209;PMID:32385188;PMID:29054919;NCT07161999",
        "assay_and_contrast": "Pearson correlation & p80 discordance of tryptic MS CSF NEFL vs NEFH + CLSI EP09c platform-offset sensitivity & Schoenfeld event sizing",
        "effect_direction": "ASSAY_SPECIFIC_MS_NEFL_VS_NEFH_DISCORDANCE",
        "effect_estimate": "DIA r=0.2779 (31.17% p80 discordance, 75.0% [12/16] top-quintile MS NEFH missed; overlapping Emory TMT n=51 misses 60.0% [6/10]); HR=0.70 needs 247 deaths at 80% power (138 at HR=0.62 [MODEL_PRIOR])",
        "notes": "Trautwig 2025 measures tryptic CSF MS total NEFH/NEFL abundance (where KSP phosphorylation attenuates tryptic correlation vs clinical immunoassay serum NfL-CSF pNfH rho=0.64-0.71 PMID:38683209, paired CSF-serum pNfH r=0.652 PMID:29054919, and serum NfL outperforming serum pNfH on ALSFRS-R slope PMID:32385188); commercial pNfH platforms span ~1.8x-4.5x calibrator offsets (PMID:31251725; cf. BioVendor ELISA in PMID:40354799 vs MSD ECLIA in PMID:42836993), where hypothetical unbridged 1.8x-4.5x higher CSF cutoffs over-exclude 36.5-86.3% of <=3,700 pg/mL eligibles while lower cutoffs admit 73.7-98.9% of >3,700 pg/mL patients (2.13x crude mortality proportion ratio: 33/47 vs 57/173), reducing 247-death one-sided superiority power from 80.0% to ~43.0-50.2% if HR_high=1.00 or ~14.0-23.1% if HR_high=1.37 [MODEL_PRIOR] and motivating CLSI EP09c (N>=40) split-aliquot Passing-Bablok bridging. [Sample context: 77 paired DIA ALS donors; technical cross-platform check in 51 overlapping Emory TMT ALS donors]",
    })
    # 2. subnode_dissection.csv + Wave B v1.2.7 patches
    it_cols, it_rows = _load("candidate_intake_ledger.csv")
    sn_cols, sn_rows = _load("subnode_dissection.csv")
    for s in sn_rows:
        if s["subnode_id"] == "C015-N2":
            s["subnode_verdict"] = s["subnode_verdict"].replace(
                "+ favorable DepMap non-essentiality (Chronos=-0.018)",
                "(dividing cancer-line DepMap Chronos=-0.018 despite human LoF constraint LOEUF=0.50 & mouse blastocyst lethality)",
            )
    apply_wave_b_ev_and_sub_patches(it_rows, ev_map, sn_rows)
    apply_wave_b_ev_and_sub_part_b(ev_map, sn_rows)
    apply_wave_c_ev_and_sub_patches(it_rows, ev_map, sn_rows)
    apply_wave_d_evidence_part_a(it_rows, ev_map)
    apply_wave_d_evidence_part_b(ev_map)
    _save("candidate_intake_ledger.csv", it_cols, it_rows)
    _save("evidence_ledger.csv", ev_cols, ev_rows)
    _save("subnode_dissection.csv", sn_cols, sn_rows)
    print("Stage 2A (candidate_intake_ledger + evidence_ledger + subnode_dissection) OK")


if __name__ == "__main__":
    main()
