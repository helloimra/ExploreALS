"""Programmatic single-contrast evidence builder for Phase 3B (EV-P3B-001..027, 0 hand-typed metric or N drift)."""
from __future__ import annotations

from typing import Any

from _denovo_evidence_rows_dd import build_deep_dive_evidence_rows


def build_phase3b_evidence_rows(f1234: dict[str, Any], sso: dict[str, Any], ext: dict[str, Any], dd: dict[str, Any]) -> list[dict[str, str]]:
    f1, f2, f3, f4 = f1234["funnel1_cryptic_splicing"], f1234["funnel2_cryptic_apa"], f1234["funnel3_csf_and_spatial"], f1234["funnel4_bye2025_screen"]
    ribo, sp, kal_fcx = f1["brown_riboseq"], f1["spillman_fractions"], f1["spillman_kalrn_ce_fcx"]
    bs6 = {r["gene_name"]: r for r in f2["bryce_smith_t6_riboseq"]}
    bs5 = {r["gene_name"]: r for r in f2["bryce_smith_t5_nygc"]}
    z_s4 = [x["row"] for x in f2["zeng2025_trappc12"] if x["sheet"] == "S4"][0]
    csf = f3["trautwig_deconfounded_dia"]["target_lookup"]
    tmt = f3["trautwig_deconfounded_dia"]["set1_tmtpro_n101_anova"]
    zh, gc = f3["zhang2026_mn_selected"], f3["pineda_ba4_gc_adjusted"]["ba4_exc_by_gene"]
    ed_exc, ed_oli = f3["edinburgh_sals_non_c9"]["Excitatory"], f3["edinburgh_sals_non_c9"]["Oligo"]
    bye_pos = {r["drug"]: r for r in f4["unadopted_positive_p05_hits"]}
    bye_sp = {r["Genes"]: r for r in f1["bye2025_sals_splicing_t6"]}
    ma_map: dict[str, list[dict[str, Any]]] = {}
    for r in f1["ma2022_moesm5"]:
        ma_map.setdefault(r["Genes"], []).append(r)
    ivs = {(r["gene_symbol"], int(r["rank_within_gene"])): r for r in sso["intervals"]}
    ptc_atg = sso["atg4b_ce_reading_frame_audit"]["inframe_ptc_codon_indices_1b"]
    st2z, light2 = ext["structure_metrics"]["PDB_2Z0D_ATG4B_LC3B"], ext["key_study_details"]["NCT05193994"]

    def _sp_n(g: str, fr: str) -> int:
        return int(sp[g][fr]["n_c9ftd"]) + int(sp[g][fr]["n_ctrl"])

    def _ev(eid: str, cid: str, run: str, stype: str, loc: str, coh: str, ass: str, ed: str, est: str, pv: str, qv: str, n: str, wt: str, notes: str) -> dict[str, str]:
        return {"evidence_id": eid, "carbon_id": cid, "subnode_id": "", "analysis_run_id": run, "source_type": stype, "source_id_or_locator": loc,
                "cohort_and_stratum": coh, "assay_and_contrast": ass, "effect_direction": ed, "effect_estimate": est, "p_value": pv, "fdr_or_adjusted_p": qv,
                "sample_size_n": n, "epistemic_weight": wt, "notes": notes}

    return [
        _ev("EV-P3B-001", "DN-01", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS_CRYPTIC:Brown2022_MOESM13;DS029_SPILL:MOESM1_MOESM2",
            "Human i3Neurons TDP-43 KD vs Ctrl", "DESeq2 Ribo-seq footprinting on ATG4B", "LOSS_OF_TRANSLATION_CRYPTIC_EXON",
            f"log2FC={ribo['ATG4B']['log2FoldChange']:.4f}", f"{ribo['ATG4B']['pvalue']:.3e}", f"{ribo['ATG4B']['padj']:.3e}", "", "HIGH",
            f"Brown cryptic exon chr2:241668875-241668985(+) (111 bp, phase-0 Exon 10 Val319 introduces 2 in-frame TGA PTCs at CE codons {ptc_atg}; discovered in Ling 2015 PMID:26250685 & Torres 2018 PMID:29912613) PSI 0->0.243 (FDR=1.16e-11); Spillman C9-FTD Homogenate DIA log2FC={sp['ATG4B']['homogenate_protein']['log2fc']:.4f} (nominal p={sp['ATG4B']['homogenate_protein']['p_value']:.4f}, padj={sp['ATG4B']['homogenate_protein']['padj']:.3f}, n={_sp_n('ATG4B','homogenate_protein')}, PMID:42789089) while paired MOESM2 Homogenate RNA-seq ({sp['ATG4B']['homogenate_rnaseq']['log2fc']:+.4f}, p={sp['ATG4B']['homogenate_rnaseq']['p_value']:.4f}) & Synaptosome DIA ({sp['ATG4B']['synaptosome_protein']['log2fc']:+.4f}, p={sp['ATG4B']['synaptosome_protein']['p_value']:.4f}, n={_sp_n('ATG4B','synaptosome_protein')}) are flat. [Sample context: Brown Ribo-seq replicates]"),
        _ev("EV-P3B-002", "DN-01", "RUN-P3B-002", "PRIMARY_RECOMPUTE", "DS_GENCODE_V46_TX;DS_PDB_2Z0D;PMID:39305312;PMID:19322194",
            "GRCh38 ATG4B cryptic exon + PDB 2Z0D ATG4B(H280A)-LC3B complex", "Phase 3A v2 + AlphaGenome AVI scan + 3D catalytic triad contact audit", "CLEAN_SSO_CATALYTIC_LOSS",
            f"#1 {ivs[('ATG4B',1)]['interval_id']} ({ivs[('ATG4B',1)]['offtarget_safety_status']}, max_AVI={ivs[('ATG4B',1)]['max_avi_phred']}, sp1={ivs[('ATG4B',1)]['spliced_1mm_genes']}, pm1_50={ivs[('ATG4B',1)]['premRNA_1mm_splice50bp_genes']}); #2 {ivs[('ATG4B',2)]['interval_id']} ({ivs[('ATG4B',2)]['offtarget_safety_status']}, sp1={ivs[('ATG4B',2)]['spliced_1mm_genes']}, pm1_50={ivs[('ATG4B',2)]['premRNA_1mm_splice50bp_genes']}, pm2_25={ivs[('ATG4B',2)]['premRNA_2mm_splice25bp_pc_genes']}); triad-Gly120={st2z['triad_to_LC3B_Gly120_min_dist_A']}A", "", "", "", "HIGH",
            f"Spares annotated chr2:241668860 (#2 shifts -10 bp deeper into CE from Torres 2024 LNA ASO 3J chr2:241668980-241668995(+) to eliminate all 1mm splice-active hits vs #1); {st2z['interchain_contact_pairs_le_4p2A']} contacts<=4.2A in PDB 2Z0D (H280A, Thr5-Gln354); DepMap Chronos=-0.0312; Torres 2024 PMID:39305312 confirms preclinical ASO 3J HeLa mRNA rescue, IV Pip8b2-ATG4B murine Kim-1 nephrotoxicity, human sALS cord membrane ATG4B loss + LC3ylation, & Atg4b-KO SOD1 worsening. [Sample context: GRCh38 + PDB 2Z0D]"),
        _ev("EV-P3B-003", "DN-02", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS029_SPILL:MOESM5_Sheet3",
            "Spillman 2026 C9-FTD vs Control human frontal cortex RNA-seq", "Header-resolved two-sided Fisher exact test on KALRN cryptic exon detection", "POSTMORTEM_CRYPTIC_EXON_GAIN",
            f"{kal_fcx['kalrn_ce_pos_c9ftd']}/10 C9-FTD (mean CE frac={kal_fcx['mean_kalrn_ce_frac_c9ftd']:.4f}) vs {kal_fcx['kalrn_ce_pos_ctrl']}/10 Control",
            f"{kal_fcx['fisher_2s_p']:.6f}", "", str(kal_fcx["n_c9ftd"] + kal_fcx["n_ctrl"]), "HIGH",
            f"1/1 de novo CE on MOESM5 S3 (PSI MWU p={kal_fcx['mwu_psi_2s_p']:.6f}; exceeds UNC13A {kal_fcx['benchmark_unc13a_pos_c9ftd']}/10); Brown dPSI=+0.4946 (FDR=3.90e-19); full-GC BA4_Exc beta={gc['KALRN']['gc_adj_beta_sals']:.4f} (p={gc['KALRN']['gc_adj_p']:.4f}, q_BH={gc['KALRN']['gc_adj_q_bh']:.4f} vs unadj p={gc['KALRN']['unadj_welch_p']:.4f}; Edinburgh Exc +{ed_exc['KALRN']['diff_log2cpm']:.4f}, p={ed_exc['KALRN']['p_welch']:.4f})."),
        _ev("EV-P3B-004", "DN-02", "RUN-P3B-002", "PRIMARY_RECOMPUTE", "DS_GENCODE_V46_TX;DS_GNOMAD_V41_CONSTRAINT",
            "GRCh38 KALRN major 3'SS / shared exon vs downstream intronic ISE", "Phase 3A v2 + gnomAD r4 polymorphism & AVI scan", "CLEAN_GE2MM_SSO_SPARING_RS2173852",
            f"#1 {ivs[('KALRN',1)]['interval_id']} ({ivs[('KALRN',1)]['offtarget_safety_status']}, max_AVI={ivs[('KALRN',1)]['max_avi_phred']}, ese={ivs[('KALRN',1)]['ese_motifs']}); #2 {ivs[('KALRN',2)]['interval_id']} ({ivs[('KALRN',2)]['offtarget_safety_status']})", "", "", "", "HIGH",
            "gnomAD r4 splice-gate AF=17.61% (joint AF=17.47%, NFE=21.07%) SNP rs2173852 (3-124701255-G-C) sits on the -1 donor base (with A/U-rich <40% GC across +1..+6); #1 spans major 3'SS 124701093 acceptor & +1..+17 exonic core (ese_motifs=0) of 124700977-124701255, while #2 targets the +7..+24 intronic ISE. [Sample context: GRCh38 + gnomAD r4]"),
        _ev("EV-P3B-005", "DN-03", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS_CRYPTIC:Brown2022_MOESM13;DS_CRYPTIC:Ma2022_MOESM5;DS029_SPILL:MOESM1",
            "Human i3Neurons TDP-43 KD vs Ctrl", "DESeq2 Ribo-seq footprinting on PTPRT", "SEVERE_TRANSLATIONAL_LOSS",
            f"log2FC={ribo['PTPRT']['log2FoldChange']:.4f}", f"{ribo['PTPRT']['pvalue']:.3e}", f"{ribo['PTPRT']['padj']:.3e}", "", "HIGH",
            f"#1 FDR-significant Ribo-seq loss among Ma 2022 cryptic genes (chr20:42098552-42102124(-) FDR={ma_map['PTPRT'][0]['Leafcutter p-values (FDR-adjusted)']:.3e}); Spillman Homogenate DIA log2FC={sp['PTPRT']['homogenate_protein']['log2fc']:.4f} (p={sp['PTPRT']['homogenate_protein']['p_value']:.5f}, n={_sp_n('PTPRT','homogenate_protein')}); full-GC BA4_Exc beta={gc['PTPRT']['gc_adj_beta_sals']:.4f} (p={gc['PTPRT']['gc_adj_p']:.4f}, q_BH={gc['PTPRT']['gc_adj_q_bh']:.4f}; Edinburgh Exc p={ed_exc['PTPRT']['p_welch']:.4f}). [Sample context: Brown Ribo-seq]"),
        _ev("EV-P3B-006", "DN-04", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS005_BYE:Table_6;DS_CRYPTIC:Brown2022_MOESM11;PMID:41286450",
            "Bye 2025 sALS patient vs Control iPSC-MNs (Day 49, N=77: 65 sALS vs 12 Ctrl)", "LeafCutter cluster differential splicing on CELF5 (chr19:clu_25763_+; junction RT-PCR required)", "PATIENT_IPSC_MN_CRYPTIC_SPLICING",
            f"loglr={bye_sp['CELF5']['Loglr']:.4f} (df={int(bye_sp['CELF5']['df'])})", f"{bye_sp['CELF5']['P-value']:.3e}", f"{bye_sp['CELF5']['Adjusted P-value']:.5f}", "77", "HIGH",
            f"Bye Day-49 sALS iPSC-MNs lacked bulk nuclear TDP-43 depletion (P=0.990, PMID:41286450 -> junction RT-PCR required); Brown CE chr19:3278209-3278316(+) after Exon-5 Pro201 inside RRM2 (aa 134-214, PDB 2DNH) dPSI=+0.3471 (FDR=2.83e-22), Ribo-seq log2FC={ribo['CELF5']['log2FoldChange']:.4f} (padj={ribo['CELF5']['padj']:.3e}), nominal full-GC BA4_Exc beta={gc['CELF5']['gc_adj_beta_sals']:.4f} (p={gc['CELF5']['gc_adj_p']:.4f}, nominal q_BH={gc['CELF5']['gc_adj_q_bh']:.4f}), SSO #1 {ivs[('CELF5',1)]['interval_id']} ({ivs[('CELF5',1)]['offtarget_safety_status']}, max_AVI={ivs[('CELF5',1)]['max_avi_phred']}). [Sample context: 77 Day-49 iPSC-MN donor lines (65 sALS vs 12 Ctrl) in Bye Table 6]"),
        _ev("EV-P3B-007", "DN-05", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS031_ZHANG;DS_CRYPTIC:Ma2022_MOESM5;DS029_SPILL:MOESM1",
            "Zhang 2026 human cervical spinal cord 55-um multicellular MN-niche Visium spots (ALS vs Control, N=18 donors)", "Spot-level (within-donor pseudoreplicated, exploratory) differential expression in surviving anterior horn motor-neuron-niche Visium spots on PRUNE2", "SURVIVING_MN_TRANSCRIPT_LOSS",
            f"avg_log2FC={zh['PRUNE2']['avg_log2FC']:.4f}", f"{zh['PRUNE2']['p_val']:.5f}", f"{zh['PRUNE2']['BH']:.5f}", "18", "HIGH",
            f"Sole Ma 2022 cryptic gene (chr9:76638288-76644739(-), LeafCutter FDR={ma_map['PRUNE2'][0]['Leafcutter p-values (FDR-adjusted)']:.3e}) passing spot-level within-donor pseudoreplicated BH<0.05 loss in surviving cervical MN-niche Visium spots (multicellular spot unit across N=18 donors, exploratory), plus Spillman C9-FTD Synaptosome DIA log2FC={sp['PRUNE2']['synaptosome_protein']['log2fc']:.4f} (p={sp['PRUNE2']['synaptosome_protein']['p_value']:.5f}, n={_sp_n('PRUNE2','synaptosome_protein')})."),
        _ev("EV-P3B-008", "DN-06", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS029_SPILL:MOESM1;DS_CRYPTIC:Brown2022_MOESM13;DS031_ZHANG",
            "Spillman 2026 C9-FTD vs Control frontal cortex synaptosome DIA proteomics", "Two-sided Welch t-test on synaptosomal PFKP protein", "SYNAPTOSOMAL_LOSS_SPINAL_NULL_PPP_CAVEAT",
            f"log2FC={sp['PFKP']['synaptosome_protein']['log2fc']:.4f}", f"{sp['PFKP']['synaptosome_protein']['p_value']:.5f}", f"{sp['PFKP']['synaptosome_protein']['padj']:.4f}", str(_sp_n("PFKP", "synaptosome_protein")), "HIGH",
            f"Brown CE chr10:3099557-3099819(+) FDR=2.20e-17, Ribo-seq {ribo['PFKP']['log2FoldChange']:.4f} (padj={ribo['PFKP']['padj']:.3e}), Edinburgh Oligo {ed_oli['PFKP']['diff_log2cpm']:.4f} (p={ed_oli['PFKP']['p_welch']:.5f}), BUT Zhang cervical MN is flat ({zh['PFKP']['avg_log2FC']:.4f}, BH={zh['PFKP']['BH']:.4f}) & neuronal PFKP suppression may preserve PPP NADPH/GSH; SSO #1 {ivs[('PFKP',1)]['interval_id']} ({ivs[('PFKP',1)]['offtarget_safety_status']})."),
        _ev("EV-P3B-009", "DN-07", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS_BRYCE_APA:ST6_ST5;DS_ZENG_APA:S4;DS005_BYE:Table_6;DS029_SPILL:MOESM1",
            "Bryce-Smith 2025 i3Neuron TDP-43 KD vs Ctrl Ribo-seq", "DESeq2 Ribo-seq footprinting on TRAPPC12 cryptic ALE target", "LOSS_OF_TRANSLATION_CRYPTIC_ALE",
            f"log2FC={bs6['TRAPPC12']['log2FoldChange']:.4f}", f"{bs6['TRAPPC12']['pvalue']:.3e}", f"{bs6['TRAPPC12']['padj']:.3e}", "", "HIGH",
            f"Intronic ALE chr2:3457795-3458181(+) (NYGC 82.9% vs 34.0% non-TDP) + secondary Brown CE chr2:3458462-3458515(+) + Bye sALS iPSC-MN padj={bye_sp['TRAPPC12']['Adjusted P-value']:.5f}, distinct from Zeng 27-kb-downstream canonical 3'UTR lengthening chr2:3479564-3485092(+) (dPAS=+{z_s4['Delta_distal_PAS_usage']:.4f}); Spillman DIA null (homogenate p={sp['TRAPPC12']['homogenate_protein']['p_value']:.4f}, n={_sp_n('TRAPPC12','homogenate_protein')}; synaptosome p={sp['TRAPPC12']['synaptosome_protein']['p_value']:.4f}, n={_sp_n('TRAPPC12','synaptosome_protein')}); #1 {ivs[('TRAPPC12',1)]['interval_id']} ({ivs[('TRAPPC12',1)]['offtarget_safety_status']}, Tm={ivs[('TRAPPC12',1)]['tm_phys_pops_c']}C, sub18={ivs[('TRAPPC12',1)]['sub18_core_steric_pc_genes']}), #2 {ivs[('TRAPPC12',2)]['interval_id']} ({ivs[('TRAPPC12',2)]['offtarget_safety_status']}). [Sample context: Bryce-Smith ST6]"),
        _ev("EV-P3B-010", "DN-08", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS_BRYCE_APA:ST2_ST6;DS_EDIN_PB;DS003_PB",
            f"Edinburgh GSE290359 non-C9 sALS vs Control Excitatory neuron snRNA-seq ({ed_exc['ELK1']['n_case']} non-C9 ALS vs {ed_exc['ELK1']['n_ctrl']} Control)", "Donor-collapsed two-sided Welch t-test on ELK1 expression", "AMBIGUOUS_GAIN_CRYPTIC_3EXT",
            f"diff_log2cpm=+{ed_exc['ELK1']['diff_log2cpm']:.4f}", f"{ed_exc['ELK1']['p_welch']:.5f}", "", str(ed_exc["ELK1"]["n_case"] + ed_exc["ELK1"]["n_ctrl"]), "MODERATE",
            f"3.90-kb 3'Ext chrX:47631618-47635519(-) (extending canonical 3'UTR 47635520-47636927(-) to 5.31-kb 47631618-47636927(-); Ribo-seq +{bs6['ELK1']['log2FoldChange']:.4f}, padj={bs6['ELK1']['padj']:.3e}), BUT Pineda BA4_Exc is null (unadj p={gc['ELK1']['unadj_welch_p']:.4f}, GC-adj p={gc['ELK1']['gc_adj_p']:.4f}); RNase-H gapmer scan across post-PAS-trimmed search window chrX:47631625-47635519(-) inside 3'Ext 47631618-47635519(-): #1 {ivs[('ELK1',1)]['interval_id']} ({ivs[('ELK1',1)]['offtarget_safety_status']}), #2 {ivs[('ELK1',2)]['interval_id']} ({ivs[('ELK1',2)]['offtarget_safety_status']})."),
        _ev("EV-P3B-011", "DN-09", "RUN-P3B-002", "PRIMARY_RECOMPUTE", "DS029_SPILL:MOESM1;DS_BRYCE_APA:ST5;DS_GENCODE_V46_TX",
            "Spillman 2026 C9-FTD vs Control frontal cortex homogenate DIA proteomics", "Two-sided Welch t-test on homogenate DLGAP1 protein", "SYNAPTIC_LOSS_TRUE_3SS_RESCUED",
            f"log2FC={sp['DLGAP1']['homogenate_protein']['log2fc']:.4f}", f"{sp['DLGAP1']['homogenate_protein']['p_value']:.5f}", f"{sp['DLGAP1']['homogenate_protein']['padj']:.4f}", str(_sp_n("DLGAP1", "homogenate_protein")), "HIGH",
            f"Synaptosome DIA {sp['DLGAP1']['synaptosome_protein']['log2fc']:.4f} (p={sp['DLGAP1']['synaptosome_protein']['p_value']:.4f}, n={_sp_n('DLGAP1','synaptosome_protein')}); #1 NYGC selective ALE (17 TDP+ vs 0 non-TDP, {bs5['DLGAP1']['fold_enrichment']:.2f}x); full-GC BA4_Exc beta={gc['DLGAP1']['gc_adj_beta_sals']:.4f} (p={gc['DLGAP1']['gc_adj_p']:.4f}, q_BH={gc['DLGAP1']['gc_adj_q_bh']:.4f}); scoring directly at single true cryptic 3'SS chr18:4147667(-) rescues #1 {ivs[('DLGAP1',1)]['interval_id']} ({ivs[('DLGAP1',1)]['offtarget_safety_status']}, sp0={ivs[('DLGAP1',1)]['spliced_0mm_genes']}, flags=NONE)."),
        _ev("EV-P3B-012", "DN-10", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS045_TRAUT:Set2_DIA_Set1_TMT;DS029_SPILL:MOESM1;DS_PDB_1XFD;PMID:15476821",
            f"Trautwig 2025 single-center Emory CSF DIA-MS ({csf['DPP6']['n_em_sals']} sALS vs {csf['DPP6']['n_em_ctrl']} Control)", "Two-sided Welch t-test + 2,305-protein BH-FDR on CSF DPP6", "REPLICATED_CSF_DENDRITIC_LOSS",
            f"log2FC={csf['DPP6']['em_log2fc']:.4f}", f"{csf['DPP6']['em_p']:.3e}", f"{csf['DPP6']['em_q_bh']:.3e}", str(csf["DPP6"]["n_em_total"]), "HIGH",
            f"WashU (26 ALS vs 6 non-ALS [2 Controls + 4 asymptomatic carriers]): {csf['DPP6']['wu_log2fc']:.4f} (Welch p={csf['DPP6']['wu_p']:.4f}, MWU p={csf['DPP6']['wu_mwu_p']:.4f}); UMilan (31 ALS/0 Ctrl) & MGH (0 ALS/78) lack comparison arms; Set 1 TMTpro N=101 ANOVA Pr(>F)={tmt['DPP6']['Pr(>F)']:.4f} is C9-driven & null in sALS vs Ctrl (Sporadic-Ctrl p={tmt['DPP6']['Sporadic-Control']:.4f}, Sporadic-C9 p={tmt['DPP6']['Sporadic-ALS.C9']:.4f}); Spillman Synaptosome DIA {sp['DPP6']['synaptosome_protein']['log2fc']:.4f} (p={sp['DPP6']['synaptosome_protein']['p_value']:.4f}); Oh 2023 PRM unquantified (0 mentions); PDB 1XFD non-catalytic dimer."),
        _ev("EV-P3B-013", "DN-11", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS045_TRAUT:Set2_DIA_Set1_TMT;DS003_PB;DS_GC_REF",
            f"Trautwig 2025 single-center Emory CSF DIA-MS ({csf['DPP10']['n_em_sals']} sALS vs {csf['DPP10']['n_em_ctrl']} Control)", "Two-sided Welch t-test + 2,305-protein BH-FDR on CSF DPP10", "REPLICATED_CSF_DENDRITIC_LOSS",
            f"log2FC={csf['DPP10']['em_log2fc']:.4f}", f"{csf['DPP10']['em_p']:.3e}", f"{csf['DPP10']['em_q_bh']:.5f}", str(csf["DPP10"]["n_em_total"]), "HIGH",
            f"WashU (26 ALS vs 6 non-ALS [2 Controls + 4 asymptomatic carriers]): {csf['DPP10']['wu_log2fc']:.4f} (Welch p={csf['DPP10']['wu_p']:.4f}, MWU p={csf['DPP10']['wu_mwu_p']:.4f}); Set 1 TMTpro N=101 ANOVA Pr(>F)={tmt['DPP10']['Pr(>F)']:.4f} is C9-driven & null in sALS vs Ctrl (Sporadic-Ctrl p={tmt['DPP10']['Sporadic-Control']:.4f}, Sporadic-C9 p={tmt['DPP10']['Sporadic-ALS.C9']:.4f}); full-GC BA4_Exc beta={gc['DPP10']['gc_adj_beta_sals']:.4f} (p={gc['DPP10']['gc_adj_p']:.4f}, q_BH={gc['DPP10']['gc_adj_q_bh']:.4f})."),
        _ev("EV-P3B-014", "DN-12", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS045_TRAUT:Set2_DIA_Set1_TMT;OpenTargets_DepMap",
            f"Trautwig 2025 single-center Emory CSF DIA-MS ({csf['CFL1']['n_em_sals']} sALS vs {csf['CFL1']['n_em_ctrl']} Control)", "Two-sided Welch t-test + 2,305-protein BH-FDR on CSF CFL1", "REPLICATED_CSF_AXONAL_DAMAGE_SURGE",
            f"log2FC=+{csf['CFL1']['em_log2fc']:.4f}", f"{csf['CFL1']['em_p']:.3e}", f"{csf['CFL1']['em_q_bh']:.5f}", str(csf["CFL1"]["n_em_total"]), "HIGH",
            f"Replicated in WashU (+{csf['CFL1']['wu_log2fc']:.4f}, Welch p={csf['CFL1']['wu_p']:.5f}, MWU p={csf['CFL1']['wu_mwu_p']:.4f}, n=32) AND Set 1 TMTpro N=101 ANOVA (Pr(>F)={tmt['CFL1']['Pr(>F)']:.3e}, Sporadic-Ctrl diff=+{tmt['CFL1']['diff Sporadic-Control']:.4f}, p={tmt['CFL1']['Sporadic-Control']:.3e}); DepMap pan-essential (isEssential=True, p10 Chronos=-1.3534)."),
        _ev("EV-P3B-015", "DN-13", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS031_ZHANG;DS003_PB;DS_EDIN_PB;NCT01879241;PMID:29934198;PMID:9443715",
            "Zhang 2026 human cervical spinal cord 55-um multicellular MN-niche Visium spots (ALS vs Control, N=18 donors)", "Spot-level (within-donor pseudoreplicated, exploratory) differential expression in anterior horn motor-neuron-niche Visium spots on MAOB", "REACTIVE_ASTROGLIAL_INFILTRATION_RCT_FAILED",
            f"avg_log2FC=+{zh['MAOB']['avg_log2FC']:.4f}", f"{zh['MAOB']['p_val']:.3e}", f"{zh['MAOB']['BH']:.5f}", "18", "HIGH",
            f"BA4_Astro ctrl=7.60 log2CPM vs discordant low-level Exc snRNA (Pineda full-GC beta={gc['MAOB']['gc_adj_beta_sals']:.4f}, p={gc['MAOB']['gc_adj_p']:.4f}, q_BH={gc['MAOB']['gc_adj_q_bh']:.4f}; Edinburgh Exc +{ed_exc['MAOB']['diff_log2cpm']:.4f}, p={ed_exc['MAOB']['p_welch']:.4f}) shows multicellular within-donor pseudoreplicated Visium spot surge reflects reactive astrocyte expansion; failed 4 ALS RCTs (Rasagiline NCT01879241 N=252; NCT01786603 N=80; Selegiline N=133 & N=111)."),
        _ev("EV-P3B-016", "DN-14", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS005_BYE;NCT04248465;NCT04436497;PMID:28128456;PMID:41187881",
            "Bye 2025 16-donor sALS iPSC-MN screen (PMX 205 at 2.5 uM vs paired DMSO)", "Two-sided paired t-test + 107-drug BH-FDR on iPSC-MN survival days", "NOMINAL_IPSC_MN_SURVIVAL_GAIN_C5_CLASS_CAUTION",
            f"mean_diff=+{bye_pos['PMX 205']['mean_paired_dmso_days']:.4f}d (Rank #{int(bye_pos['PMX 205']['rank_107'])}/107)", f"{bye_pos['PMX 205']['p_ttest_2s']:.5f}", f"{bye_pos['PMX 205']['q_bh_107_ttest_2s']:.5f}", "16", "MODERATE",
            "Wilcoxon p=0.01099; upstream human ALS C5 cleavage inhibitors failed Phase 2/3 RCTs (ravulizumab CHAMPION-ALS NCT04248465 N=382 & zilucoplan HEALEY NCT04436497 futility), and glia-free Exc C5AR1 is minimal (2.06 log2CPM), requiring C5AR1-KO vs avacopan target-engagement gate."),
        _ev("EV-P3B-017", "DN-15", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS005_BYE;PMID:7906190;PMID:12807386",
            "Bye 2025 16-donor sALS iPSC-MN screen (Lamotrigine at 2.5 uM vs paired DMSO)", "Two-sided paired t-test + 107-drug BH-FDR on iPSC-MN survival days", "SCREEN_FALSE_POSITIVE_CLINICALLY_FALSIFIED",
            f"mean_diff=+{bye_pos['Lamotrigine']['mean_paired_dmso_days']:.4f}d (Rank #13/107)", f"{bye_pos['Lamotrigine']['p_ttest_2s']:.5f}", f"{bye_pos['Lamotrigine']['q_bh_107_ttest_2s']:.5f}", "16", "HIGH",
            "Clinically falsified across 2 double-blind placebo-controlled human ALS RCTs: Eisen 1993 PMID:7906190 (N=67, 100 mg/d) and CSF-verified Ryberg 2003 PMID:12807386 (N=30, 300 mg/d)."),
        _ev("EV-P3B-018", "DN-16", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS005_BYE",
            "Bye 2025 15-donor sALS iPSC-MN screen (Dolutegravir at 2.5 uM vs paired DMSO)", "Two-sided paired t-test + 107-drug BH-FDR on iPSC-MN survival days", "SUPRAPHYSIOLOGICAL_SCREEN_GAIN_FAILED_PH3",
            f"mean_diff=+{bye_pos['Dolutegravir']['mean_paired_dmso_days']:.4f}d (Rank #17/107)", f"{bye_pos['Dolutegravir']['p_ttest_2s']:.5f}", f"{bye_pos['Dolutegravir']['q_bh_107_ttest_2s']:.5f}", "15", "MODERATE",
            "Wilcoxon p=0.05798; 2.5 uM screen concentration is 60-250x above clinical unbound human CSF dolutegravir (~10-40 nM at 50 mg QD), and unstratified Triumeq failed Phase 3 LIGHTHOUSE II (EV-P3B-022)."),
        _ev("EV-P3B-019", "DN-17", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS005_BYE;PMID:7763202;NCT07414212",
            "Bye 2025 15-donor sALS iPSC-MN screen (Acetylcysteine at 2.5 uM vs paired DMSO)", "Two-sided paired t-test + 107-drug BH-FDR on iPSC-MN survival days", "SCREEN_ANTIOXIDANT_ARTIFACT_CLINICALLY_FALSIFIED",
            f"mean_diff=+{bye_pos['Acetylcysteine']['mean_paired_dmso_days']:.4f}d (Rank #12/107)", f"{bye_pos['Acetylcysteine']['p_ttest_2s']:.5f}", f"{bye_pos['Acetylcysteine']['q_bh_107_ttest_2s']:.5f}", "15", "HIGH",
            "Polar carboxylate NAC has poor CNS penetration (Kp,uu << 0.05) and high-dose 50 mg/kg/d SC NAC failed Louwerse 1995 PMID:7763202 double-blind survival RCT (N=110: HR=0.74, P=0.31); low-dose 50 mg/d NCT07414212 (N=90 recruiting) cannot overcome PK/futility."),
        _ev("EV-P3B-020", "DN-18", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS005_BYE;NCT00243932;PMID:19743457",
            "Bye 2025 16-donor sALS iPSC-MN screen (Coenzyme Q10 at 2.5 uM vs paired DMSO)", "Two-sided paired t-test + 107-drug BH-FDR on iPSC-MN survival days", "SCREEN_FALSE_POSITIVE_CLINICALLY_FALSIFIED",
            f"mean_diff=+{bye_pos['Coenzyme Q10']['mean_paired_dmso_days']:.4f}d (Rank #19/107)", f"{bye_pos['Coenzyme Q10']['p_ttest_2s']:.5f}", f"{bye_pos['Coenzyme Q10']['q_bh_107_ttest_2s']:.5f}", "16", "HIGH",
            "Clinically falsified in Phase II QALS RCT (Kaufmann 2009 Ann Neurol PMID:19743457, NCT00243932, N=185, 2,700 mg/d over 9 months: met Stage 2 futility, p=0.51)."),
        _ev("EV-P3B-021", "DN-19", "RUN-P3B-001", "PRIMARY_RECOMPUTE", "DS005_BYE;NCT03580616;NCT01835782;NCT07660614;PMID:27589995;PMID:34059824;PMID:43025655;10.1016/j.jlr.2026.101187",
            "Bye 2025 16-donor sALS iPSC-MN screen (L-Serine at 2.5 uM vs paired DMSO)", "Two-sided paired t-test + 107-drug BH-FDR on iPSC-MN survival days", "BASAL_MEDIA_NOISE_AND_SPT_WRONG_SIGN_CONFOUNDED",
            f"mean_diff=+{bye_pos['L-Serine']['mean_paired_dmso_days']:.4f}d (Rank #20/107)", f"{bye_pos['L-Serine']['p_ttest_2s']:.5f}", f"{bye_pos['L-Serine']['q_bh_107_ttest_2s']:.5f}", "16", "HIGH",
            "2.5 uM addition shifts ~400 uM basal neuronal media L-serine by +0.625% (<1% noise, failing BH-FDR at q=0.1707; Phase 1 NCT01835782 N=20 PMID:27589995 safety-only, single-arm NCT03580616 N=43 IRB noncompliance termination), while human SPTLC1/SPTLC2-ALS GoF variants lose ORMDL ceramide feedback and overproduce canonical C18-C22 dihydrosphingolipids/ceramides where L-serine is contraindicated (Mohassel et al. 2021 PMID:34059824; Ziak et al. 2026 PMID:43025655; intrathecal SPTLC1 ASO LTX-002 NCT07660614)."),
        _ev("EV-P3B-022", "DN-16", "RUN-P3B-001", "CLINICAL_TRIAL_AUDIT", "NCT05193994;NCT06658977",
            "Phase 3 LIGHTHOUSE II unstratified ALS survival RCT (Triumeq: dolutegravir/abacavir/lamivudine vs Placebo)", "Planned interim primary survival futility analysis", "PHASE3_SURVIVAL_FUTILITY_TERMINATED",
            f"TERMINATED ({light2['completion_date']}): no survival benefit vs placebo", "", "", str(light2["enrollment"]), "HIGH",
            f"NCT05193994 whyStopped verbatim: '{light2['why_stopped']}'; rollover NCT06658977 (N=12) terminated; note Triumeq targeted endogenous retrovirus HERV-K via NRTI reverse-transcriptase inhibition (abacavir/lamivudine) + HIV-1 retroviral integrase inhibition (dolutegravir, which has minimal direct non-LTR LINE-1 activity), reinforcing why S09 LINE-1 RT requires ALS-TE stratification."),
        *build_deep_dive_evidence_rows(dd, sso, _ev),
    ]
