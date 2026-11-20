"""Programmatic single-contrast evidence builder for RUN-P3B-004 targeted deep-dive rows (EV-P3B-023..027)."""
from __future__ import annotations

from typing import Any, Callable


def build_deep_dive_evidence_rows(dd: dict[str, Any], sso: dict[str, Any], ev_fn: Callable[..., dict[str, str]]) -> list[dict[str, str]]:
    ivs = {(r["gene_symbol"], int(r["rank_within_gene"])): r for r in sso["intervals"]}
    reg_c = dd["nygc_multiregion_donor_analysis"]["regions"]["Spinal_Cord_Cervical"]
    reg_l = dd["nygc_multiregion_donor_analysis"]["regions"]["Spinal_Cord_Lumbar"]
    ny_c, ny_l = reg_c["genes"], reg_l["genes"]
    ny_m = dd["nygc_multiregion_donor_analysis"]["regions"]["Cortex_Motor"]["genes"]
    ag_rs = dd["kalrn_rs2173852_alphagenome_summary"]
    kal_g = dd["kalrn_rs2173852_genetics_summary"]
    kal_i = dd["kalrn_isoform_and_ptc_audit"]
    atg_3d = dd["atg4b_3d_truncation_2z0d"]
    ch_atg = dd["chembl_atg4b_summary"]
    st7_sz = dd["elk1_st7_regulon_sign_test"]["regulon_sizes_st7"]
    elk_c = dd["elk1_st7_regulon_sign_test"]["contrasts"]
    ed_e = elk_c["Edinburgh_sALS_nonC9_Exc_Welch_t"]
    liab = dd["gene_liability_profiles"]
    pr_pk = {int(r["pos_1b"]): float(r["prob"]) for r in dd["prune2_intron_alphagenome_peaks"]}
    pt_pk = dd["ptprt_intron_alphagenome_peaks"][0]
    unc_bm = kal_g["opentargets_v4_unc13a_rs12608932_als_credible_sets_benchmark"]

    return [
        ev_fn(
            "EV-P3B-023", "DN-02", "RUN-P3B-004", "PRIMARY_RECOMPUTE",
            "DS001_COUNTS;DS001_META;DS_GENCODE_V46_COMP_GTF;AlphaGenome_v1;GTEx_v8;OpenTargets_v4",
            "NYGC GSE153960 cervical spinal cord ALS-TDP donors (RIN>=5, RIN+GC+mn_neur_z adjusted)",
            "Neuronal-mass-residualized within-ALS-TDP OLS slope of KALRN log2CPM on log2(tSTMN2_TPM+1) + AlphaGenome rs2173852, GTEx v8, & Open Targets v4 audit",
            "KALIRIN12_TRUNCATION_RS2173852_NULL_GWAS_PARADOX",
            f"beta_log2_tSTMN2={ny_c['KALRN']['within_tdp_mn_adj_log2_tSTMN2_beta']:.4f} ({ny_c['KALRN']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}% non-cryptic neuronal tail); predicted rs2173852 5'SS {ag_rs['donor_124701255_plus']['ref_G_prob']:.4f}->{ag_rs['donor_124701255_plus']['alt_C_prob']:.4f} ({ag_rs['donor_124701255_plus']['fold_reduction']:.2f}x drop)",
            f"{ny_c['KALRN']['within_tdp_mn_adj_log2_tSTMN2_p']:.5f}", "", str(ny_c["KALRN"]["n_als_tdp"]), "MODERATE",
            f"GENCODE v46 + UniProt O60229 prove Kalirin-7 (KALRN-201, 1,663 aa) ends {kal_i['kalirin7_distance_upstream_of_intron56_bp']} bp upstream of Intron 56 & is spared (bulk ALS-TDP vs Ctrl adj_p={ny_c['KALRN']['adj_p_tdp_vs_ctrl']:.4f}, ALS-SOD1/FUS n={ny_c['KALRN']['n_als_sod1_fus']} adj_p={ny_c['KALRN']['adj_p_tdp_vs_sod1fus']:.4f}), whereas CE truncates MANE_Select Kalirin-12 (KALRN-226, 2,986 aa) & DuET (aa 2,684-2,938 kinase; PTCs 124700977:{kal_i['dual_3ss_ptc_audit']['alt_3SS_124700977']['inframe_stop_codon_indices_1b']}, 124701093:{kal_i['dual_3ss_ptc_audit']['major_3SS_124701093']['inframe_stop_codon_indices_1b']}). However, cervical mn_neur_z-adjusted tSTMN2 coupling sits at {ny_c['KALRN']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}% among {reg_c['n_noncryptic_neuronal_ref']} non-cryptic neuronal genes ({reg_c['noncryptic_neuronal_ref_pct_neg']}% negative; Spearman rho={ny_c['KALRN']['within_tdp_spearman_tSTMN2_rho']:.4f}; lumbar {ny_l['KALRN']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}%), GTEx v8 cervical cord is {liab['KALRN']['gtex_cns_spinal_cervical_tpm']:.2f} TPM (vs BA9 {liab['KALRN']['gtex_cns_ba9_tpm']:.2f} & {liab['KALRN']['max_non_cns_gtex_tissue']}={liab['KALRN']['max_non_cns_gtex_tpm']:.2f} TPM), alt 3'SS 124700977 (predicted acc={ag_rs['alt_acceptor_124700977_plus']['ref_G_prob']:.4f} vs 124701093={ag_rs['major_acceptor_124701093_plus']['ref_G_prob']:.4f}) requires shunting checks, and rs2173852 (joint AF={kal_g['gnomad_af_total']:.4f}, r4 gate={kal_g['gnomad_r4_af_splice_gate']:.4f}, NFE={kal_g['gnomad_pop_af']['NFE']:.4f}, DLPFC q={ag_rs['top_cns_splice_junction_scores']['dorsolateral prefrontal cortex']['quantile_score']:.6f}) has {kal_g['opentargets_v4_als_ftd_gwas_credible_sets_count']} ALS/FTD GWAS credible sets across {kal_g['opentargets_v4_als_studies_indexed']} Open Targets v4 ALS studies (vs {unc_bm['als_credible_sets_count']} for UNC13A rs12608932 peaking at p={unc_bm['lead_p_value']:.2e}); safety={liab['KALRN']['qualitative_safety_tier']}.",
        ),
        ev_fn(
            "EV-P3B-024", "DN-01", "RUN-P3B-004", "PRIMARY_RECOMPUTE",
            "DS001_COUNTS;DS001_META;DS001_ONEILL;DS_PDB_2Z0D;CHEMBL1741221;PMID:28287329",
            f"NYGC GSE153960 cervical spinal cord donors ({ny_c['ATG4B']['n_als_tdp']} ALS-TDP vs {ny_c['ATG4B']['n_ctrl']} Control, RIN+GC adjusted)",
            "Donor-level OLS on ATG4B log2CPM + neuronal-mass-residualized mn_neur_z tSTMN2 benchmark + SOD1/FUS negative control + PDB 2Z0D & ChEMBL audit",
            "SPINAL_ALSOX_LOSS_3D_LIR_ABLATION_SSO_LOCK",
            f"adj_beta={ny_c['ATG4B']['adj_beta_tdp_vs_ctrl']:.4f} (ALS-Ox n={ny_c['ATG4B']['oneill_motor_subtypes']['ALS-Ox']['n']} beta={ny_c['ATG4B']['oneill_motor_subtypes']['ALS-Ox']['adj_beta_vs_ctrl']:.4f}, p={ny_c['ATG4B']['oneill_motor_subtypes']['ALS-Ox']['adj_p_vs_ctrl']:.2e})",
            f"{ny_c['ATG4B']['adj_p_tdp_vs_ctrl']:.6f}", "", str(ny_c["ATG4B"]["n_als_tdp"] + ny_c["ATG4B"]["n_ctrl"]), "HIGH",
            f"Neuronal-mass-residualized mn_neur_z-adjusted log2(tSTMN2_TPM+1) slope beta={ny_c['ATG4B']['within_tdp_mn_adj_log2_tSTMN2_beta']:.4f} (p={ny_c['ATG4B']['within_tdp_mn_adj_log2_tSTMN2_p']:.2e}, {ny_c['ATG4B']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}% tail of {reg_c['n_noncryptic_neuronal_ref']} cervical neuronal genes; lumbar beta={ny_l['ATG4B']['within_tdp_mn_adj_log2_tSTMN2_beta']:.4f}, p={ny_l['ATG4B']['within_tdp_mn_adj_log2_tSTMN2_p']:.2e}, {ny_l['ATG4B']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}% tail of {reg_l['n_noncryptic_neuronal_ref']}); 3-subtype Kruskal p={ny_c['ATG4B']['oneill_kruskal_3subtype_p']:.2e} cervical & p={ny_l['ATG4B']['oneill_kruskal_3subtype_p']:.2e} lumbar, YET TDP-43-negative ALS-SOD1/FUS (n={ny_c['ATG4B']['n_als_sod1_fus']} cervical mean={ny_c['ATG4B']['mean_als_sod1_fus']:.4f} vs ALS-TDP {ny_c['ATG4B']['mean_als_tdp']:.4f}, adj_p={ny_c['ATG4B']['adj_p_tdp_vs_sod1fus']:.4f}; lumbar ALS-TDP vs Ctrl adj_p={ny_l['ATG4B']['adj_p_tdp_vs_ctrl']:.4f}) shows bulk mRNA reflects ALS-Ox/cellular state rather than replacing CE RT-ddPCR. Exon 10 Val319 truncation deletes aa 320-393 (PDB 2Z0D Thr5-Gln354: {atg_3d['intramolecular_core_contacts_le_4p0A']} intra-chain residue pairs<=4.0A, {atg_3d['lc3b_patch_heavy_atom_contacts_le_4p5A']} LC3B Val89-Val91 heavy-atom contacts<=4.5A min {atg_3d['min_dist_Glu350_to_LC3B_Val91_A']}A, + Q9Y4P1 FEIL LIR aa 388-391 PMID:28287329). CHEMBL1741221 ({ch_atg['total_bioactivity_records']} inhibitors, 0 activators) locks promoted #2 {ivs[('ATG4B',2)]['interval_id']} ({ivs[('ATG4B',2)]['offtarget_safety_status']}) & #1 {ivs[('ATG4B',1)]['interval_id']} ({ivs[('ATG4B',1)]['offtarget_safety_status']}); Kozareva 2025 (10.1101/2025.09.29.679403); safety={liab['ATG4B']['qualitative_safety_tier']} ({liab['ATG4B']['max_non_cns_gtex_tissue']}={liab['ATG4B']['max_non_cns_gtex_tpm']:.2f} TPM).",
        ),
        ev_fn(
            "EV-P3B-025", "DN-05", "RUN-P3B-004", "PRIMARY_RECOMPUTE",
            "DS001_COUNTS;DS001_META;DS_GENCODE_V46_COMP_GTF;AlphaGenome_v1",
            f"NYGC GSE153960 lumbar spinal cord donors ({ny_l['PRUNE2']['n_als_tdp']} ALS-TDP vs {ny_l['PRUNE2']['n_ctrl']} Control, RIN+GC adjusted)",
            "Donor-level OLS on PRUNE2 log2CPM + SOD1/FUS negative control + GENCODE v46 & AlphaGenome intronic splice-site audit",
            "REPLICATED_SPINAL_LOSS_MICROEXON_VS_CRYPTIC_5SS_GATE",
            f"adj_beta={ny_l['PRUNE2']['adj_beta_tdp_vs_ctrl']:.4f} (cervical n=197 adj_beta={ny_c['PRUNE2']['adj_beta_tdp_vs_ctrl']:.4f}, p={ny_c['PRUNE2']['adj_p_tdp_vs_ctrl']:.5f})",
            f"{ny_l['PRUNE2']['adj_p_tdp_vs_ctrl']:.6f}", "", str(ny_l["PRUNE2"]["n_als_tdp"] + ny_l["PRUNE2"]["n_ctrl"]), "MODERATE",
            f"ALS-Ox cervical beta={ny_c['PRUNE2']['oneill_motor_subtypes']['ALS-Ox']['adj_beta_vs_ctrl']:.4f} (p={ny_c['PRUNE2']['oneill_motor_subtypes']['ALS-Ox']['adj_p_vs_ctrl']:.2e}), YET ALS-SOD1/FUS is equally low (cervical mean={ny_c['PRUNE2']['mean_als_sod1_fus']:.4f} vs {ny_c['PRUNE2']['mean_als_tdp']:.4f}, adj_p={ny_c['PRUNE2']['adj_p_tdp_vs_sod1fus']:.4f}; lumbar adj_p={ny_l['PRUNE2']['adj_p_tdp_vs_sod1fus']:.4f}), mn_neur_z tSTMN2 coupling attenuates ({ny_c['PRUNE2']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}% cervical p={ny_c['PRUNE2']['within_tdp_mn_adj_log2_tSTMN2_p']:.4f}; lumbar p={ny_l['PRUNE2']['within_tdp_mn_adj_log2_tSTMN2_p']:.4f}, {ny_l['PRUNE2']['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}%), and cortical Oligo expression exceeds Exc. Inside Ma 2022 chr9:76638288-76644739(-), GENCODE v46 + AlphaGenome show annotated 9-bp microexon 76641972-76641980(-) (acc={pr_pk[76641980]:.4f}, don={pr_pk[76641972]:.4f}) & overlapping 34-bp exon 76641947-76641980(-) vs unannotated cryptic 5'SS donors 76641905(-) (prob={pr_pk[76641905]:.4f}) & 76641790(-) (prob={pr_pk[76641790]:.4f}); 0 SSO intervals emitted pending RT-PCR.",
        ),
        ev_fn(
            "EV-P3B-026", "DN-03", "RUN-P3B-004", "PRIMARY_RECOMPUTE",
            "DS001_COUNTS;DS001_META;DS_GENCODE_V46_COMP_GTF;AlphaGenome_v1",
            f"NYGC GSE153960 cervical spinal cord donors ({ny_c['PTPRT']['n_als_tdp']} ALS-TDP vs {ny_c['PTPRT']['n_ctrl']} Control, RIN+GC adjusted)",
            "Donor-level OLS on PTPRT log2CPM + GENCODE v46 & AlphaGenome intronic splice-site audit",
            "BULK_ATTENUATED_UNMAPPED_INTRON_GATE",
            f"adj_beta={ny_c['PTPRT']['adj_beta_tdp_vs_ctrl']:.4f} (unadj diff={ny_c['PTPRT']['unadj_diff_tdp_vs_ctrl']:.4f}, Welch p={ny_c['PTPRT']['welch_p_tdp_vs_ctrl']:.4f})",
            f"{ny_c['PTPRT']['adj_p_tdp_vs_ctrl']:.5f}", "", str(ny_c["PTPRT"]["n_als_tdp"] + ny_c["PTPRT"]["n_ctrl"]), "MODERATE",
            f"Lumbar cord is null (adj_p={ny_l['PTPRT']['adj_p_tdp_vs_ctrl']:.4f}, n=173) while motor cortex shifts +{ny_m['PTPRT']['adj_beta_tdp_vs_ctrl']:.4f} (adj_p={ny_m['PTPRT']['adj_p_tdp_vs_ctrl']:.4f}, n=114). Inside Ma 2022 chr20:42098552-42102124(-), GENCODE v46 has 0 internal exons and AlphaGenome shows only weak internal peaks (max {pt_pk['track']} {pt_pk['pos_1b']} prob={pt_pk['prob']:.4f}) with 0 published 2022-2026 1-bp junctions; 0 SSO intervals emitted pending RT-PCR.",
        ),
        ev_fn(
            "EV-P3B-027", "DN-08", "RUN-P3B-004", "PRIMARY_RECOMPUTE",
            "DS_BRYCE_APA:ST7;DS_EDIN_PB;DS003_PB;DS031_ZHANG;DS001_COUNTS",
            "Edinburgh GSE290359 non-C9 sALS vs Control Excitatory neuron snRNA-seq (Bryce-Smith ST7 ELK1_unique vs ELK4_unique)",
            f"Two-sided Welch t-test comparing ELK1_unique ({ed_e['n_elk1_unique']}/{st7_sz['ELK1_unique']} genes) vs non-cryptic paralog ELK4_unique ({ed_e['n_elk4_unique']}/{st7_sz['ELK4_unique']} genes) target t-statistics",
            "NULL_ELK1_VS_ELK4_REGULON_DIVERGENCE",
            f"diff_mean_t=+{ed_e['diff_elk1_minus_elk4']:.4f} (ELK1_unique={ed_e['mean_elk1_unique']:.4f} vs ELK4_unique={ed_e['mean_elk4_unique']:.4f})",
            f"{ed_e['welch_p_elk1_vs_elk4']:.5f}", "", "", "MODERATE",
            f"Null ELK1_unique vs ELK4_unique divergence across all 6 contrasts (quantifying 39-{ed_e['n_elk1_unique']} of {st7_sz['ELK1_unique']} ELK1_unique & 53-{ed_e['n_elk4_unique']} of {st7_sz['ELK4_unique']} ELK4_unique genes; {st7_sz['n_shared_elk1_elk4']}/{st7_sz['ELK1_all']} ENCODE non-neuronal ChIP targets shared): Pineda BA4_Exc ({elk_c['Pineda_BA4_Exc_GC_adj_t']['diff_elk1_minus_elk4']:.4f}, p={elk_c['Pineda_BA4_Exc_GC_adj_t']['welch_p_elk1_vs_elk4']:.4f}), NYGC motor cortex (p={elk_c['NYGC_Cortex_Motor_RIN_GC_t']['welch_p_elk1_vs_elk4']:.4f}), NYGC cervical cord (p={elk_c['NYGC_Spinal_Cord_Cervical_RIN_GC_t']['welch_p_elk1_vs_elk4']:.4f}), Zhang cervical MN (n={elk_c['Zhang2026_Cervical_MN_Visium_log2FC']['n_elk1_unique']}/{elk_c['Zhang2026_Cervical_MN_Visium_log2FC']['n_elk4_unique']}, p={elk_c['Zhang2026_Cervical_MN_Visium_log2FC']['welch_p_elk1_vs_elk4']:.4f}), & pTDP-43+ (n={elk_c['Zhang2026_Cervical_pTDP43_Visium_log2FC']['n_elk1_unique']}/{elk_c['Zhang2026_Cervical_pTDP43_Visium_log2FC']['n_elk4_unique']}, p={elk_c['Zhang2026_Cervical_pTDP43_Visium_log2FC']['welch_p_elk1_vs_elk4']:.4f}); NYGC lumbar bulk ELK1 mRNA rises +{ny_l['ELK1']['adj_beta_tdp_vs_ctrl']:.4f} (p={ny_l['ELK1']['adj_p_tdp_vs_ctrl']:.5f}), while ERK1/2 Ser383 pELK1 gating & dendritic local-translation effects require direct iPSC-MN perturbation; van Dijk 2026 (10.64898/2026.08.07.743523); safety={liab['ELK1']['qualitative_safety_tier']} ({liab['ELK1']['max_non_cns_gtex_tissue']}={liab['ELK1']['max_non_cns_gtex_tpm']:.2f} TPM). [Sample context: 371 ELK1_unique vs 437 ELK4_unique genes across 32 non-C9 Edinburgh donors]",
        ),
    ]
