"""Modular v1.2.7 Wave B primary-source patches for candidate_intake_ledger.csv, evidence_ledger.csv, and subnode_dissection.csv."""
from __future__ import annotations


def apply_wave_b_ev_and_sub_patches(
    intake_rows: list[dict[str, str]],
    ev_map: dict[str, dict[str, str]],
    sn_rows: list[dict[str, str]],
) -> None:
    for it in intake_rows:
        if it["carbon_id"] == "C015":
            it["staged_dataset_ids"] = "DS_BRYCE_APA;DS_CONS2026;DS_AFDB;DS029_SPILL;DS_GENCODE_V46_TX;DS_GNOMAD_V41_CONSTRAINT"

    # C022 (DNAJB2)
    ev_map["EV-B6-011"].update({
        "source_id_or_locator": "DS029_SPILL:MOESM1_Synapt_FRCTX:DNAJB2;PMID:42789089",
        "effect_estimate": "-0.3818",
        "p_value": "0.00813",
        "fdr_or_adjusted_p": "0.2236",
        "notes": "Official Spillman 2026 MOESM1 Synapt_FRCTX DIA matrix (10 C9-FTD vs 10 Ctrl, PMID:42789089; nominal p=0.00813, inconclusive after multiplicity at BH-FDR=0.2236; P25686 group does not separate DNAJB2a from DNAJB2b; paired Homogenate DIA -0.4470, p=3.05e-4, BH-FDR=0.0182 in EV-P2-T4-005); concordant loss in Spillman iPSC neurons (log2FC=-1.1153, p=0.0455, n=6) & NYGC Cervical SC RNA (beta=-0.2933, p=5.21e-5, n=86: 48 non-mutation sALS vs 38 Ctrl); Trautwig CSF TMT null (p=0.779, N=101).",
    })
    ev_map["EV-B6-012"].update({
        "source_type": "HUMAN_GENETICS",
        "source_id_or_locator": "ClinVar:DNAJB2;OpenTargets:ENSG00000135924;DS_GNOMAD_V41_CONSTRAINT;PMID:26936937;PMID:37070754",
        "cohort_and_stratum": "ClinVar Mendelian DSMA5/CMT2T/Juvenile ALS & gnomAD v4.1",
        "effect_direction": "LOSS_OF_FUNCTION_PATHOGENIC",
        "effect_estimate": "OT_genetic_score=0.598 (55 OT EVA P/LP submissions; 25 unique single-gene ClinVar P/LP)",
        "notes": "Recessive DNAJB2 (HSJ1) LoF causes human distal HMN (dHMN5/DSMA5), axonal CMT2T, and juvenile ALS (OMIM 614881; PMID:26936937); gnomAD v4.1 MANE Select ENST00000336576.10 (DNAJB2b, 324 aa) LOEUF=0.836 (21/36.2 LoF) vs cytosolic ENST00000392086.8 (DNAJB2a, 277 aa) LOEUF=0.743 (18/35.9 LoF); dominant stop-loss c.832T>G ER-trapping causes neuromyopathy (PMID:37070754).",
    })

    # C015 (SCFD1 / G2E3)
    ev_map["EV-B2-001"].update({
        "source_id_or_locator": "DS_CONS2026:Tsitkov2026_AALS594_eQTL_rs229143;OpenTargets_v4:GCST90027164;PMID:43045849",
        "assay_and_contrast": "SCFD1 cis-eQTL & motif-suggested ISL1 chromatin footprint at rs229143 (chr14:30622552:T>A)",
        "effect_estimate": "rs229143-A MN beta=+0.04762 (+0.048+/-0.003 in Fig. 3A, Table S8 adj p=1.93e-32; vs iMGL rs229143-A beta=-0.2955 untreated, -0.2164 IFN-gamma, -0.3107 LPS)",
        "fdr_or_adjusted_p": "1.93e-32",
        "notes": "Answer ALS N=594 human iPSC-derived motor-neuron cis-eQTL (Tsitkov et al. PMC12919128 [PREPRINT], Fig. 3A & Table S8): normalized SCFD1 expression increases from TT to TA to AA at rs229143-A (chr14:30622552:T>A; Table S8 slope +0.04762, adj p=1.93e-32; Fig. 3A +0.048 +/- 0.003, adj p<2e-32; GTEx BA9 nes=+0.269), overlapping an ATAC chromatin footprint whose motif suggests ISL1 (TF identity unproven; Table S8 lists the ALS GWAS p-value without a signed GWAS allele, whereas allele-coded van Rheenen 2021 GCST90027164 assigns ALS risk beta=+0.0212 to rs229143-A, gnomAD NFE AF=0.329). In Perez-Alcantara et al. 2026 nonproliferating human iMGLs (PMID:43045849, Zenodo 21471267; 261 initial lines from 254 donors -> 194 cell-count QC -> n=189 untreated, n=188 IFN-gamma & n=188 LPS donors, separated in EV-P4-007), the very same rs229143-A allele is associated with lower normalized SCFD1 expression across all three conditions (untreated beta=-0.2955, p=1.40e-23, AF=0.3441; IFN-gamma beta=-0.2164, p=1.72e-12, AF=0.3486; LPS beta=-0.3107, p=3.19e-12, AF=0.3459), supporting opposite expression associations for the same allele across the two studies (slopes not directly compared across different expression scales; causal cell-type interaction, opposing effects within individual donors, TF identity, and beneficial sporadic-ALS treatment direction remain open).",
    })
    ev_map["EV-B2-002"]["notes"] = (
        "rs229143 maps to CL:0000100 motor neuron SCFD1 RNA-seq/splicing (fi=0.0394); gnomAD v4.1 MANE ENST00000458591 LOEUF=0.809, pLI=0.232 (7/16.2 LoF; Open Targets legacy v2.1.1 LOEUF=0.472, pLI=0.996); Spillman MOESM1 cortex DIA protein null (Homog log2FC=-0.0156, p=0.9313; Synapt +0.0265, p=0.7966, n=10 vs 10). [Sample context: 1,258 DepMap CRISPR screens; GRCh38 AlphaGenome locus scan]"
    )
    ev_map["EV-B2-004"]["notes"] = (
        "Colocalizes at chr14q12 ALS GWAS (including adult prefrontal cortex G2E3 eQTL/sQTL PP4=0.99 alongside SCFD1 colocalizations in Brain Catalog, Pan et al. 2023 Nucleic Acids Res PMID:36243988, DOI:10.1093/nar/gkac895) and converges with Brown 2022 TDP-43 KD Intron-1 cryptic ALE (chr14:30559272-30563746, dPSI=+0.4044, FDR=2.90e-21, replicated across 5/5 KD studies in Bryce-Smith Table 2); AlphaGenome rs229190 AVI_Phred=7.61; DepMap isEssential=False (mean Chronos=-0.0184, 0.0% <-1.0 across 1,258 lines); gnomAD v4.1 MANE ENST00000206595 LOEUF=0.600, pLI=0.888 (2/10.5 LoF; Open Targets legacy LOEUF=0.500)."
    )

    # C014 (CHMP7 / CHMP2B)
    ev_map["EV-B1-018"]["notes"] = (
        "Spillman MOESM3 between-genotype iPSC insoluble pellet PxC9FTD.PxCTRL CHMP2B log2FC=+0.5664 (p=0.0213, padj=0.3248 NS, n=6 lines: 3 C9FTD vs 3 Ctrl; within-C9FTD pellet-vs-homogenate +0.8865, p=0.00114, padj=0.0205 in EV-P2-T4-003) while CHMP7 is null across all fractions (FCx Homog -0.3005 p=0.1263, Synapt p=0.174, MOESM3 p=0.081..0.949); CHMP7/CHMP2B/VPS4B are 0-peptide undetected in Trautwig 2025 CSF; YCharOS validated antibody toolbox available for CHMP7/CHMP2B (Ayoubi et al. 2026 PMID:42975030, 10.7554/eLife.111349). [Sample context: 20 postmortem frontal cortex brains (10 C9-FTD/ALS vs 10 Ctrl)]"
    )
    ev_map["EV-B1-019"].update({
        "source_id_or_locator": "DS_GNOMAD_V41_CONSTRAINT;DepMap;IMPC;ClinicalTrials_v2;PMID:34321318;PMID:37639327;PMID:41744617;PMID:41677621",
        "cohort_and_stratum": "CHMP7 (ENSG00000147457) across 1,258 DepMap CRISPR screens & gnomAD v4.1",
        "effect_estimate": "DepMap mean Chronos=-0.6565 (66.2% lines <-0.5, isEssential=True); gnomAD v4.1 MANE ENST00000397677.6 LOEUF=0.496, pLI=0.984 (Open Targets v2.1.1 LOEUF=0.430, pLI=0.9996)",
        "notes": "gnomAD v4.1 MANE ENST00000397677.6 (13 obs / 41.6 exp LoF, lof_z=3.76; Open Targets v2.1.1 15/53.7, lof_z=4.48), 0 clinical trials; Coyne et al. 2021 (PMID:34321318) & Baskerville et al. 2024 (epub 2023, PMID:37639327) show partial CHMP7 lowering rescues NPCs/TDP-43, balanced against 2026 requirement in cortical activity-regulated genes (PMID:41744617) and telomere integrity (PMID:41677621). [Sample context: 1,258 DepMap CRISPR screens; gnomAD v4.1 GRCh38]",
    })
    ev_map["EV-B1-021"].update({
        "source_id_or_locator": "DS_GNOMAD_V41_CONSTRAINT;DepMap;PMID:39709457;PMID:42349418;PMID:42975030",
        "cohort_and_stratum": "CHMP2B (ENSG00000083937) across 1,258 DepMap CRISPR screens, gnomAD v4.1 & 2024-2026 literature",
        "effect_estimate": "DepMap mean Chronos=+0.0259 (isEssential=False); gnomAD v4.1 MANE ENST00000263780.9 LOEUF=1.503 (10/11.2 LoF; Open Targets v2.1.1 LOEUF=1.054)",
        "notes": "Keeley et al. 2024 (PMID:39709457) shows endogenous WT CHMP2B promotes nuclear CHMP7 accumulation in sALS iPSC-MNs and partial CHMP2B knockdown rescues nuclear CHMP7 accumulation, POM121 nucleoporin reduction, and downstream TDP-43 mis-splicing in human sALS iPSC-MNs (separate published intervention alongside CHMP7 ASO), balanced against sequential ANXA11->CHMP2B membrane repair (Heffner et al. 2026 PMID:42349418 [Extrapolation: plasma-membrane laser injury to nuclear envelope]) and neuronal autophagic maturation, flagging pan-allele CHMP2B KD as high liability. [Sample context: 1,258 DepMap CRISPR screens; gnomAD v4.1 GRCh38]",
    })
    ev_map["EV-P2-T4-003"].update({
        "cohort_and_stratum": "Spillman 2026 within-C9FTD iPSC-neuron pellet vs homogenate DIA (n=3 C9FTD lines; Ctrl n=3 & Pineda BA4 n=32 comparators)",
        "assay_and_contrast": "Within-C9FTD pellet-over-homogenate (PxC9FTD.HOxC9FTD) log2FC shift for CHMP2B vs ANXA11",
        "effect_estimate": "PxC9FTD.HOxC9FTD CHMP2B log2FC=+0.8865 (padj=0.0205; vs PxCTRL.HOxCTRL +0.3391 p=0.3634 & PxC9FTD.PxCTRL +0.5664 padj=0.3248) vs ANXA11 -0.8806 (p=0.00447, padj=0.0325); BA4 CHMP2B-ANXA11 r=+0.5280 (p=0.00190, n=32)",
        "fdr_or_adjusted_p": "0.0205",
        "sample_size_n": "3",
        "notes": "CHMP7 total/pellet/synaptosome protein is null across all fractions (MOESM1 p=0.126..0.174; MOESM3 p=0.081..0.949, purely nuclear-import driven); Heffner 2026 (PMID:42349418 [Extrapolation: plasma-membrane repair]) sequential ANXA11->CHMP2B recruitment and Chietera 2026 (PMID:41744617) SATB2-LEMD2-CHMP7 synaptic transcription penalize deep ESCRT ablation vs SUN1-CHMP7 import blockade (PMID:37639327).",
    })

    # S09 (Censavudine / TPN-101)
    ev_map["EV-B6-052"].update({
        "source_id_or_locator": "CT.gov:NCT04993755;NCT04993768;ChEMBL:CHEMBL124363",
        "cohort_and_stratum": "Phase 2a mixed C9orf72-ALS + FTD RCT (N=42 safety; C9-ALS VC subgroup, TPN-101 400 mg/d PO) & HEALEY Ph2/3 selection",
        "effect_estimate": "Mixed N=42 ALS+FTD favorable safety; C9-ALS subgroup 24w VC -8.4% vs -16.5% pbo (randomized ALSFRS-R -7.2 vs -6.7) & lower CSF IL-6/NfL; selected May 2025 for HEALEY Ph2/3",
        "notes": "Oral nucleoside LINE-1 RT inhibitor (MW 248.24; also completed PSP Ph2a NCT04993768 N=42 & studied in AGS) selected May 2025 for the Phase 2/3 HEALEY ALS Platform Trial; NCT04993755 remains unpublished in peer-reviewed form, pooled ALS+FTD in N=42 (24-wk randomized ALSFRS-R -7.2 vs -6.7), enrolled 0 sporadic ALS-TE patients, and requires intracellular TPN-101-TP triphosphorylation (post-mitotic MN vs proliferating glial kinase efficiency unmeasured).",
    })
    ev_map["EV-B6-053"]["notes"] = (
        "Dropped from 19.74% (15/76 Tam 2019) to 11.30% (26/230 expansion) = 13.40% (41/306 all cortical motor-ALS donors; 13.53% = 41/303 excluding 3 multi-region discordant donors; 11.52% [22/191] in C9-neg ALS+ALS/FTD and 11.60% [21/181] in C9-neg ALS; 11.24% across 587 libraries in TableS1B; spinal cord ALS-TE prevalence not estimable because O'Neill's separate 2-class spinal classifier [N=331] assigned only Glia-cord or Ox-cord)."
    )
    if "EV-B6-054" in ev_map:
        ev_map["EV-B6-054"].update({
            "effect_estimate": "Spinal ALS-TE prevalence not estimable (O'Neill 2-class spinal classifier N=331 assigns only Glia-cord or Ox-cord)",
            "notes": "O'Neill et al. 2025 (DS001_ONEILL) applied a two-class spinal cord classifier (Glia-cord vs Ox-cord across N=331 spinal donors) that includes no retrotransposon ALS-TE category, so spinal ALS-TE prevalence is not estimable from that model rather than observed at 0%.",
        })

    # C018 (C1q)
    for eid_c18 in ("EV-B3-014", "EV-B3-015", "EV-B3-016", "EV-B3-018"):
        ev_map[eid_c18]["notes"] = ev_map[eid_c18]["notes"].replace(
            "WashU & UMilan contributed 63 ALS, 0 Controls",
            "UMilan contributed 31 ALS / 0 Controls and WashU contributed 26 ALS code 100 + 6 comparators code 741 (2 ordinary Controls + 4 asymptomatic carriers; unresolved Table 2 26/84 vs MOESM1 32/78 bank count)",
        ).replace(
            "(reconciled via MGH/WashU specimen codes 100 vs 741)",
            "(code 100 vs 741; unresolved Table 2 26/84 vs MOESM1 32/78 bank count)",
        )
    ev_map["EV-B3-021"].update({
        "source_id_or_locator": "NCT04569435;NCT04514367;PMID:41787606;PMID:38942014;10.1016/j.cell.2024.05.058;PMID:24170856;PMID:23946404",
        "notes": "In HD Phase 2 NCT04514367 (N=28, PMC13307253, PMID:41787606), IV ANX005 (75-100 mg/kg) achieved 0.2-0.25% CSF:serum penetration that saturated baseline CSF C1q with downstream CSF complement reduction, yet recorded 3/28 (10.7%) treatment-related AE withdrawals and 2/28 (7.1%) drug-related SAEs (abstract: lupus + idiopathic autoimmune hemolytic anemia; Results/Table 2: SLE + non-infectious pneumonitis; hypothesized to reflect peripheral ~180 nM serum C1q sink depletion [MODEL_PRIOR]; in completed open-label ALS Phase 2a NCT04569435 [17 actual participants in CT.gov registry], Annexon's 2024 Form 10-K reports 13 treated for 12 weeks, 7 of whom continued to 24 weeks, with C1q target engagement and downstream complement reduction in blood plus an exploratory sponsor-reported subgroup observation of less ALSFRS-R decline and blood NfL stabilization without peer-reviewed publication); systemic IV IgG, IV BBB shuttles, and unmodified q4w IT Fab (~12h CSF t1/2) are rejected in favor of ECM-anchored HLE IT anti-gC1q Fab/nanobody or microglial C1QA/B ASO/di-siRNA gated on Scott-Hewitt 2024 RNP, Stephan 2013 aging C1q (PMID:23946404), and Lobsiger 2013 C-bouton safety.",
    })
    ev_map["EV-P2-T4-002"].update({
        "source_id_or_locator": "DS031_ZHANG:6d_MN_ALS_vs._HC;NCT04514367;PMID:41787606;PMID:24170856",
        "cohort_and_stratum": "Zhang 2026 human cervical anterior-horn surviving MN Visium spots (N=14 donors, Seurat MAST) & 2-compartment human CSF turnover PK",
        "effect_estimate": "6d_MN C1QC avg_log2FC=+2.3735 (C1S +1.7520, C1QB +1.6245 [BH=3.49e-6], C1QA +1.4870 [BH=2.76e-4]; VAChT intact); IV TfR-IgG is modeled to deplete 99.99% of hypothesized 180nM serum C1q [MODEL_PRIOR] & unmodified q4w IT 48kDa Fab washes out (t1/2~12h -> <0.001nM) vs IT pump/ECM-anchored HLE Fab [MODEL_PRIOR]",
        "notes": "PMC13307253 (PMID:41787606, HD NCT04514367 N=28) proved IV ANX005 saturates low-abundance CSF C1q at 0.2-0.25% CSF:serum penetration while recording 3/28 treatment-related AE withdrawals and 2/28 drug-related SAEs (hypothesized to reflect peripheral ~180 nM serum C1q sink depletion [MODEL_PRIOR]), and ~4x/day human CSF bulk flow clears unmodified q4w 48 kDa IT Fab (intravitreal glaucoma ANX007 is non-CNS), motivating ECM-anchored HLE IT Fab/nanobody or IT microglial C1QA/B ASO/di-siRNA.",
    })
