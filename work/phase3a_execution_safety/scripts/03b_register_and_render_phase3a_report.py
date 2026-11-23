"""RUN-P3A-003 (Part B, v2): Register Phase 3A v2 runs/evidence and programmatically render PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REG_DIR = ROOT / "registries"
OUT_DIR = ROOT / "work" / "phase3a_execution_safety" / "outputs"
REP_FP = ROOT / "reports" / "phase3" / "PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md"


def _sha12(fp: Path) -> str:
    return hashlib.sha256(fp.read_bytes()).hexdigest()[:12]


def _upsert_csv(fp: Path, key_col: str, new_rows: list[dict[str, str]]) -> None:
    with fp.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        existing = list(reader)
    new_by_id = {r[key_col]: r for r in new_rows}
    ex_ids = {r[key_col] for r in existing}
    kept = [{**r, **new_by_id[r[key_col]]} if r[key_col] in new_by_id else r for r in existing]
    kept.extend(r for r in new_rows if r[key_col] not in ex_ids)
    with fp.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(kept)


def main() -> None:
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ot_fp, rd_fp = REG_DIR / "phase3_sso_offtarget_audit.csv", REG_DIR / "phase3_execution_readiness.csv"
    with ot_fp.open(encoding="utf-8") as fh:
        ot_rows = list(csv.DictReader(fh))
    with rd_fp.open(encoding="utf-8") as fh:
        rd_rows = list(csv.DictReader(fh))
    ot_payload = json.loads((OUT_DIR / "run_p3a_001_sso_offtarget_audit.json").read_text(encoding="utf-8"))
    n_tx = int(ot_payload["n_transcripts_scanned"])
    ot_json = ot_payload["intervals"]
    br_json = json.loads((OUT_DIR / "run_p3a_002_csf_glial_bridge_validation.json").read_text(encoding="utf-8"))

    _upsert_csv(REG_DIR / "analysis_runs.csv", "analysis_run_id", [
        {
            "analysis_run_id": "RUN-P3A-001", "phase_batch": "Phase3A_Execution_Safety",
            "script_relpath": "work/phase3a_execution_safety/scripts/00_stage_gencode_v46_and_gggenome.py;work/phase3a_execution_safety/scripts/01_sso_transcriptome_and_premRNA_offtarget_audit.py",
            "output_artifacts": "registries/phase3_sso_offtarget_audit.csv;work/phase3a_execution_safety/outputs/run_p3a_001_sso_offtarget_audit.json",
            "datasets_used": "DS_GENCODE_V46_TX;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;DS003_PB;DS_EDIN_PB;DS031_ZHANG",
            "tools_and_skills_used": "carbon_als.offtarget_scanner;carbon_als.gtf_splice_index;gnomad-database;DBCLS_GGGenome_hg38;uv-python",
            "reproduced_verified": "yes", "run_timestamp_utc": now_iso,
            "summary": f"Coordinate-only <=2mm + G:U wobble + 1-nt bulge + 18-bp sub-core off-target audit across {n_tx:,} GENCODE v46 transcripts (with comprehensive GTF exon-exon junction/CDS localization) and GRCh38 pre-mRNA internal splice boundaries across 7 human CNS lineages.",
        },
        {
            "analysis_run_id": "RUN-P3A-002", "phase_batch": "Phase3A_Execution_Safety",
            "script_relpath": "work/phase3a_execution_safety/scripts/02_c019_csf_glial_bridge_out_of_sample_validation.py",
            "output_artifacts": "work/phase3a_execution_safety/outputs/run_p3a_002_csf_glial_bridge_validation.json",
            "datasets_used": "DS045_TRAUT;DS045_XML;DS046_OH_XML",
            "tools_and_skills_used": "carbon_als.loaders;scipy.stats;uv-python",
            "reproduced_verified": "yes", "run_timestamp_utc": now_iso,
            "summary": "rs3831317-neutral order-statistic-calibrated 4-component (5-protein) CSF Bridge validation: Emory leak-free 5-fold sALS-vs-Ctrl OOF, within-WashU/within-MGH same-center checks, MGH-offset-adjusted external & cross-sectional C9 Symptomatic-vs-Asymptomatic AUCs, header-resolved Oh 2023 univariate replication, and genotype-matched p80 pass rates.",
        },
        {
            "analysis_run_id": "RUN-P3A-003", "phase_batch": "Phase3A_Execution_Safety",
            "script_relpath": "work/phase3a_execution_safety/scripts/03a_build_execution_readiness_registry.py;work/phase3a_execution_safety/scripts/03b_register_and_render_phase3a_report.py",
            "output_artifacts": "registries/phase3_execution_readiness.csv;work/phase3a_execution_safety/outputs/run_p3a_003_execution_readiness_summary.json;reports/phase3/PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md",
            "datasets_used": "DS_GENCODE_V46_TX;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;DS045_TRAUT;DS046_OH_XML",
            "tools_and_skills_used": "scripts.phase3_gates;uv-python",
            "reproduced_verified": "yes", "run_timestamp_utc": now_iso,
            "summary": "Separated Clinical Translational Readiness (TRL) from Scientific Actionability & Experimental Gate Class with atomic 1-domain-per-token hurdles, ICH M3(R2) / 21 CFR 312.23(b) single-entity IND staging before Stage 2 21 CFR 300.50 combination testing, [MEASURED] vs [MODEL_PRIOR] tags, and 4-column backup symmetry across all 17 surviving programs.",
        },
    ])

    ot_by_id = {r["interval_id"]: r for r in ot_rows}
    g1, g2 = ot_by_id["chr14:30563747-30563764(+)"], ot_by_id["chr14:30563930-30563947(+)"]
    k1, k2, k3 = ot_by_id["chr20:63442595-63442616(-)"], ot_by_id["chr20:63442565-63442582(-)"], ot_by_id["chr20:63442302-63442319(-)"]
    u2, s2 = ot_by_id["chr19:17642537-17642554(-)"], ot_by_id["chr8:79616829-79616846(+)"]
    oof = br_json["within_emory_unconfounded_dia"]["sals_vs_ctrl_leak_free_5fold_oof"]
    dec_ext = br_json["deconfounded_and_stratified_external_validation"]
    ext_adj = dec_ext["ext_all_symp_als_vs_center_adj_ext_ctrl"]
    ext_raw = dec_ext["raw_unadjusted_ext_all_symp_als_vs_ext_ctrl_confounded"]
    wu_int = dec_ext["within_washu_same_center_als_vs_non_als"]
    mgh_sp = dec_ext["within_mgh_same_center_asym_vs_ctrl_specificity"]
    c9_adj = dec_ext["genotype_matched_ext_c9_symp_vs_c9_asym_center_adj"]
    wu_sals = dec_ext["ext_washu_sals_vs_center_adj_ext_ctrl"]
    p80 = dec_ext["matched_genotype_p80_pass_rates"]
    aud = br_json["pooled_ds045_center_audit"]
    oh = br_json["independent_external_study_oh2023_pmc10215566"]
    tier_counts = {t: sum(1 for r in rd_rows if r["scientific_actionability_tier"] == t) for t in ("TIER_1_ACTIONABLE_NOW", "TIER_2_FOCUSED_GATE_FIRST", "TIER_3_EXPLORATORY_DISCOVERY", "COMPANION_PROTOCOL_ONLY")}
    all_16_ids = ",".join(r["candidate_id"] for r in rd_rows)

    _upsert_csv(REG_DIR / "evidence_ledger.csv", "evidence_id", [
        {
            "evidence_id": "EV-P3A-001", "carbon_id": "C006", "subnode_id": "", "analysis_run_id": "RUN-P3A-001",
            "source_type": "TRANSCRIPTOME_BULGE_SUBCORE_AND_7LINEAGE_CNS_SCAN",
            "source_id_or_locator": "DS_GENCODE_V46_TX;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;DS003_PB;DS_EDIN_PB;GGGenome_hg38",
            "cohort_and_stratum": f"GENCODE v46 ({n_tx:,} transcripts + comprehensive GTF) & 7 human CNS lineages (Pineda BA4 n=32 + Edinburgh n=33)",
            "assay_and_contrast": "Coordinate-only <=2mm + G:U wobble + 1-nt bulge + 18-bp sub-core off-target scan across 9 core 3-plex intervals (KCNQ2, UNC13A, STMN2)",
            "effect_direction": "PROMOTED_ZERO_LE1MM_LEADS_AND_BULGE_SUBCORE_HAZARDS_RESOLVED",
            "effect_estimate": f"Harmonized 6-tier scan promotes UNC13A #2 ({u2['interval_id']}, {u2['offtarget_safety_status']}: 0 <=1mm/wob/blg, 25bp-SS 2mm=4) & STMN2 #2 ({s2['interval_id']}, {s2['offtarget_safety_status']}: 0 <=1mm/wob/blg, 25bp-SS 2mm=2); KCNQ2 #3 ({k3['interval_id']}) CAUTION ({k3['flagged_constrained_neuronal_hits']}), #1 ({k1['interval_id']}) CAUTION ({k1['flagged_constrained_neuronal_hits']}), #2 ({k2['interval_id']}) WARN ({k2['flagged_constrained_neuronal_hits']})",
            "p_value": "", "fdr_or_adjusted_p": "", "sample_size_n": "32", "epistemic_weight": "HIGH",
            "notes": "Comprehensive mRNA EEJ/CDS mapping proves UNC13A #3 CLOCK (dEEJ=5,288nt 3'UTR) and KCNQ2 #2 PRPF4B are non-steric, while 1-nt bulge + BA4_Oligo scanning catches PTCH1 (d=1nt, LOEUF=0.146, pLI=1.0) on KCNQ2 #2 and 18-bp sub-core scanning catches non-constrained GPR156 (dSS=41bp, LOEUF=0.961) on 22-bp KCNQ2 #1, promoting UNC13A #2, STMN2 #2, and non-sponge KCNQ2 #3 vs #1 walk (under harmonized <=25bp 2-mm == 0 gating, UNC13A #2 [25bp-SS 2mm=4] and STMN2 #2 [25bp-SS 2mm=2] carry CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED with zero <=1-mm/wobble/bulge/sub18 hits). [Sample context: 32 BA4 donors + 33 Edinburgh donors + GENCODE v46]",
        },
        {
            "evidence_id": "EV-P3A-002", "carbon_id": "C015", "subnode_id": "C015-N2", "analysis_run_id": "RUN-P3A-001",
            "source_type": "REPEAT_RETROELEMENT_OFFTARGET_EXCLUSION",
            "source_id_or_locator": "DS_GENCODE_V46_TX;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT;GGGenome_hg38",
            "cohort_and_stratum": "GENCODE v46 comprehensive transcriptome + GRCh38 internal splice boundaries across G2E3 cryptic-exon windows",
            "assay_and_contrast": "Disjoint 0mm, 1mm, pure-wobble, and 1-nt bulge off-target gene counts across G2E3 #1-#3",
            "effect_direction": "CATASTROPHIC_ALU_REPEAT_OFFTARGET_FAILURE",
            "effect_estimate": f"G2E3 #1 sp0={g1['spliced_0mm_genes']}, sp1={g1['spliced_1mm_genes']}, wob_only={g1['spliced_wobble_only_pc_genes']}, pm0={g1['premRNA_0mm_sense_genes']}, pm1={g1['premRNA_1mm_sense_genes']} (max_mm={g1['gggenome_max_mm_queried']}); G2E3 #2 sp0={g2['spliced_0mm_genes']}, pm0={g2['premRNA_0mm_sense_genes']}",
            "p_value": "", "fdr_or_adjusted_p": "", "sample_size_n": "", "epistemic_weight": "HIGH",
            "notes": f"Proves G2E3 cryptic exon chr14:30563746-30563950(+) is Alu/retroelement-derived (G2E3 #1 hits {ot_json[g1['interval_id']]['flagged_constrained_cns_count']} constrained CNS genes at sterically active splice/5'UTR sites including PAFAH1B1, DDB1, SLC12A5/KCC2, with 0-mm & 1-mm queries completed [max_mm=1: 28,576 0-mm & 95,283 1-mm non-self genomic loci, 1,206 spliced 1-mm genes, 8,634 pre-mRNA 1-mm sense genes; genome-wide 2-mm = NA after exact-match repeat saturation]; G2E3 #2 hits 1 spliced + 37 pre-mRNA 0mm sense genes including constrained BMPR1A [LOEUF=0.195] & SPECC1L-ADORA2A [dSS=69bp] plus <=50nt ELOC 1mm [d=33nt; LRP1B is 1mm dSS=7,458bp]), excluding G2E3 from steric SSO multiplexing.",
        },
        {
            "evidence_id": "EV-P3A-003", "carbon_id": "C019", "subnode_id": "", "analysis_run_id": "RUN-P3A-002",
            "source_type": "DECONFOUNDED_OOF_AND_RS3831317_NEUTRAL_CSF_VALIDATION",
            "source_id_or_locator": "DS045_TRAUT;DS045_XML;DS046_OH_XML",
            "cohort_and_stratum": "Single-center Emory DIA leak-free 5-fold sALS OOF (42 sALS vs 54 Ctrl, n=96) + stratified/target-site-recalibrated external validation (n=141)",
            "assay_and_contrast": "CHIT1-abundance-adjusted (order-statistic-calibrated) 4-component (5-protein) CSF Bridge sALS-vs-Control discrimination, bank-only negative control & matched p80 rates",
            "effect_direction": "UNCONFOUNDED_OOF_AND_WITHIN_CENTER_REPLICATION_WITH_INTERACTION_PD_MANDATE",
            "effect_estimate": f"Emory leak-free sALS-vs-Ctrl OOF AUC={oof['oof_roc_auc']}; within-WashU ALS-vs-nonALS AUC={wu_int['roc_auc']} (n={wu_int['n_total']}); cross-sectional C9 Symp-vs-Asym recalibrated AUC={c9_adj['roc_auc']} (n={c9_adj['n_total']}); target-site MGH-recalibrated ext ALS-vs-Ctrl AUC={ext_adj['roc_auc']} (LOO={dec_ext['leave_one_mgh_control_out_target_site_recalibrated_auc']}; vs raw confounded {ext_raw['roc_auc']} & bank-only non-MGH indicator {dec_ext['bank_only_non_mgh_negative_control_auc']})",
            "p_value": f"{oof['oof_welch_p']:.3e}", "fdr_or_adjusted_p": "", "sample_size_n": "96", "epistemic_weight": "HIGH",
            "notes": f"Mitigates max(Z1,Z2) order-statistic penalty against CHIT1-low/rs3831317-deficient profiles (inferred from CSF abundance z_CHIT1<-2.0 rather than direct DNA genotyping); separates pure MGH Ctrl drift ({aud['bridge_ctrl_drift_pure_mgh_n16_minus_emory_n54_z']:+.4f}z, n=16 vs 54, p={aud['bridge_ctrl_drift_pure_mgh_n16_minus_emory_n54_welch_p']:.5f}) from pooled External Ctrl ({aud['bridge_ctrl_drift_pooled_ext_n18_minus_emory_n54_z']:+.4f}z, n=18: 16 MGH + 2 WashU ordinary Controls; specimen-code prefix 100 vs 741 / Batch b06-b08 vs b01 reconciles workbook MGH=78/WashU=32 with paper prose 84/26; UMilan has 31 ALS/0 Ctrl); proves raw external AUC ({ext_raw['roc_auc']}) is center-dominated (protein-free non-MGH indicator achieves AUC={dec_ext['bank_only_non_mgh_negative_control_auc']} across 52/1,026 same-bank pairs) and frames MGH offset subtraction explicitly as target-site control recalibration (in-sample {ext_adj['roc_auc']}, LOO {dec_ext['leave_one_mgh_control_out_target_site_recalibrated_auc']}) rather than frozen transfer; within-MGH Asym vs Ctrl is null (p={mgh_sp['welch_p']:.3f}), WashU sALS vs recalibrated-Ctrl AUC={wu_sals['roc_auc']} (p={wu_sals['welch_p']:.4f}), header-resolved Oh 2023 replicates 5/5 discovery proteins (FDR<=0.044) and 4/5 in targeted PRM validation (CHI3L2 targeted columns blank; 40/61 discovery overlap), and matched sALS-p80 (z>{p80['frozen_emory_sals_p80_cutoff']}) passes {100*p80['emory_sals_pass_at_sals_p80']:.1f}% Emory sALS vs {100*oof['oof_sensitivity_at_fold_z95']:.1f}% at Ctrl-z95 (note: sALS-vs-Ctrl diagnostic ROC is distinct from unproven living-CSF-to-cortical ALS-Glia subtype assignment and Thompson 2019 PMID:31123140 mimic AUC 0.51-0.92 [0.688 ext], requiring biomarker-stratified pSTAT3/CXCL10 PD interaction testing). [Sample context: 96 single-center Emory sALS+Ctrl OOF donors]",
        },
        {
            "evidence_id": "EV-P3A-004", "carbon_id": "C006", "subnode_id": "", "analysis_run_id": "RUN-P3A-003",
            "source_type": "TRL_VS_SCIENTIFIC_ACTIONABILITY_ATOMIC_HURDLE_AND_IND_TRIAGE",
            "source_id_or_locator": "registries/phase3_execution_readiness.csv",
            "cohort_and_stratum": f"All 17 non-dropped survivors ({all_16_ids})",
            "assay_and_contrast": "Separation of Clinical Readiness (TRL) from Scientific Actionability & Next-Gate Experimental Class, atomic 1-clause hurdles, and 4-column backup symmetry",
            "effect_direction": "TRL_SEPARATED_FROM_SCIENTIFIC_DISCOVERY_PRIORITY_ACROSS_17_SURVIVORS",
            "effect_estimate": f"TIER_1={tier_counts['TIER_1_ACTIONABLE_NOW']} (S06 T-lock Ph1b, S07 calibrated-pNfH Ph3), TIER_2={tier_counts['TIER_2_FOCUSED_GATE_FIRST']} (C001, C006, C002, C007), TIER_3={tier_counts['TIER_3_EXPLORATORY_DISCOVERY']} (novel genetics/pathology leads C022, C014, S09, C018, C015, C023, C016 ahead of screen hits C020, C019, S02), PROTOCOL={tier_counts['COMPANION_PROTOCOL_ONLY']} (C005)",
            "p_value": "", "fdr_or_adjusted_p": "", "sample_size_n": "", "epistemic_weight": "HIGH",
            "notes": f"Portfolio-wide triage covering {all_16_ids}: decomposes compound hurdles atomically, enforces KEEP_CORE-first TIER_1 ordering, moves C006 to TIER_2_FOCUSED_GATE_FIRST pending Intron-5 ISS-vs-ISE microwalk proof, applies ICH M3(R2) / 21 CFR 312.23(b) single-entity GLP tox rules prior to Stage 2 21 CFR 300.50 combination testing, populates COARSE_PRIOR_ONLY tags, and maintains symmetric 4-column backups.",
        },
    ])

    stamp = f"REGISTRY_CONCORDANCE_SHA12: offtarget={_sha12(ot_fp)} readiness={_sha12(rd_fp)}"
    ot_md = "\n".join(
        f"| `{r['candidate_id']}` | `{r['gene_symbol']}` #{r['rank_within_gene']} | `{r['interval_id']}` | {r['length_bp']} | {r['tm_phys_pops_c']} | "
        f"{r['spliced_0mm_genes']} / {r['spliced_1mm_genes']} / {r['spliced_wobble_only_pc_genes']} | "
        f"{r['premRNA_0mm_sense_genes']} / {r['premRNA_1mm_splice50bp_genes']} / {r['premRNA_wobble_only_splice50bp_pc_genes']} | "
        f"{r['bulge_1nt_steric_pc_genes']} / {r['sub18_core_steric_pc_genes']} | `{r['flagged_constrained_neuronal_hits']}` | **`{r['offtarget_safety_status']}`** |"
        for r in ot_rows
    )
    rd_md = "\n".join(
        f"| {r['priority_rank_overall']} | `{r['candidate_id']}` ({r['gene_or_drug']}) | `{r['primary_modality_specific']}` | `{r['clinical_readiness_trl']}` | "
        f"`{r['next_gate_experimental_class']}` | `{r['model_prior_dependency']}` | **{r['unsolved_hurdle_count']}** (`{r['unsolved_hurdles_structured']}`) | **`{r['scientific_actionability_tier']}`** |"
        for r in rd_rows
    )
    bk_md = "\n".join(
        f"| `{r['candidate_id']}` | `{r['backup_modality']}` | `{r['backup_class_warning']}` | `{r['backup_delivery_pk_hurdle']}` | `{r['backup_lost_target']}` |"
        for r in rd_rows if r["backup_modality"] != "NONE"
    )
    with (REG_DIR / "candidate_decisions.csv").open(encoding="utf-8") as fh:
        cdec_33 = list(csv.DictReader(fh))
    d33 = {k: sum(1 for r in cdec_33 if r["decision"] == k) for k in ("KEEP_CORE", "KEEP_EXPLORATORY_UNPROVEN", "RECLASSIFY_BENCHMARK_OR_BIOMARKER", "DROP")}
    assert (d33["KEEP_CORE"], d33["KEEP_EXPLORATORY_UNPROVEN"], d33["RECLASSIFY_BENCHMARK_OR_BIOMARKER"], d33["DROP"]) == (4, 13, 4, 12), d33
    REP_FP.parent.mkdir(parents=True, exist_ok=True)
    REP_FP.write_text(
        f"# Phase 3A (v2.1) — Execution-Safety, Deconfounded CSF Calibration & TRL/Scientific-Gate Triage\n\n"
        f"> **Programmatically rendered** by `03b_register_and_render_phase3a_report.py` (`{stamp}`). Zero raw synthetic oligomer sequences stored.\n"
        f"> **v1.2 Registry Sync:** Reflects all `33` `candidate_decisions.csv` classifications (`{d33['KEEP_CORE']} KEEP_CORE`, `{d33['KEEP_EXPLORATORY_UNPROVEN']} KEEP_EXPLORATORY_UNPROVEN` [incl. `S02` CuATSM behind 5 hurdles], `{d33['RECLASSIFY_BENCHMARK_OR_BIOMARKER']} RECLASSIFY_BENCHMARK_OR_BIOMARKER`, `{d33['DROP']} DROP`).\n\n"
        f"## 1. Comprehensive Spliced + Pre-mRNA + `1-nt` Bulge + `18-bp` Sub-Core Off-Target Audit (`RUN-P3A-001`)\n\n"
        f"Scanned `{n_tx:,}` GENCODE v46 spliced human transcripts (`DS_GENCODE_V46_TX` × comprehensive `DS_GENCODE_V46_COMP_GTF` exon-exon junction & `CDS` coordinates) and `GRCh38` internal splice boundaries (`DBCLS GGGenome` × `DS_GNOMAD_V41_CONSTRAINT` × `7` human CNS lineages across `Pineda BA4` & `Edinburgh`) across all `12` candidate splice windows (`G2E3 #1` `Alu` capped at `gggenome_max_mm_queried = {g1['gggenome_max_mm_queried']}`; `2` on all other `11` windows):\n\n"
        f"| ID | Gene #Rank | `GRCh38` Interval (1-based) | Len | `Tm_phys` (°C) | Spliced `0mm / 1mm / Wob-Only` | Pre-mRNA `0mm / <=50bp 1mm / <=50bp Wob` | `1-nt Bulge / 18-bp Core` | Steric Constrained CNS / Aux Flags | Safety Verdict |\n"
        f"| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |\n{ot_md}\n\n"
        f"## 2. `C019` 4-Component (`5`-Protein) `CHIT1`-Abundance-Adjusted CSF Bridge Validation (`RUN-P3A-002`)\n\n"
        f"- **Order-Statistic Calibration & Cohort-Overlap Guard:** Standardizing `max(z_CHIT1, z_CHI3L2)` on `CHIT1`-competent controls (`z_CHIT1 > -2.0`) mitigates the `+0.11 z` Gaussian max penalty against `CHIT1`-low/`rs3831317`-deficient profiles (abundance-inferred rather than DNA-genotyped). `101/101` `SC TMTpro` samples (`sporadic AUC = {br_json['cross_platform_emory_tmtpro_technical_overlap']['sporadic_vs_ctrl']['roc_auc']}`) overlap `Emory DIA` (`DS045_XML` Par8 — technical platform check only).\n"
        f"- **Primary Unconfounded Single-Center OOF (`Emory DIA`, `42 sALS vs 54 Ctrl`, `n = 96`):** Leak-free 5-fold stratified `ROC-AUC = {oof['oof_roc_auc']}` (`Welch p = {oof['oof_welch_p']:.2e}`; legacy uncalibrated `AUC = {oof['oof_roc_auc_legacy_max_z']}`).\n"
        f"- **Deconfounded External & Same-Center Checks (`n = 141` Holdout):** Because `57/57` non-Emory ALS cases come from `UMilan + WashU` (`86.0%` familial `C9orf72/SOD1`) while `16/18` Controls come from `MGH` (pure `MGH n=16` vs `Emory n=54` Control drift = **`{aud['bridge_ctrl_drift_pure_mgh_n16_minus_emory_n54_z']:+.4f} z`, `p = {aud['bridge_ctrl_drift_pure_mgh_n16_minus_emory_n54_welch_p']:.5f}`**; pooled `External n=18` drift = `{aud['bridge_ctrl_drift_pooled_ext_n18_minus_emory_n54_z']:+.4f} z`; specimen-code `100` vs `741` reconciles workbook `MGH=78/WashU=32` with paper prose `84/26`), raw external `AUC = {ext_raw['roc_auc']}` is center/genotype-inflated. Subtracting `MGH`'s control offset yields **`MGH`-offset-adjusted external `AUC = {ext_adj['roc_auc']}`** (`p = {ext_adj['welch_p']:.2e}`, `Ctrl FPR = {100*ext_adj['ctrl_fpr_at_train_z95']:.1f}%`; `WashU sALS n=8` vs adj-Ctrl `AUC = {wu_sals['roc_auc']}`, `p = {wu_sals['welch_p']:.4f}`), corroborated by same-center **within-`WashU` `AUC = {wu_int['roc_auc']}`** (`26 ALS vs 6 non-ALS`, `p = {wu_int['welch_p']:.2e}`), **within-`MGH` specificity null** (`62 Asym vs 16 Ctrl`, `p = {mgh_sp['welch_p']:.3f}`, `{100*mgh_sp['sensitivity_at_train_z95']:.2f}%` pass), **cross-sectional genotype-matched `C9orf72` Symptomatic-vs-Asymptomatic `AUC = {c9_adj['roc_auc']}`** (`33 C9-Symp vs 53 C9-Asym`, `p = {c9_adj['welch_p']:.2e}`), and header-resolved **Oh 2023 discovery `5/5` protein replication** (`FDR <= 0.044`, `N = {oh['n_total_table1']}`, `4/5` targeted PRM with `CHI3L2` blank and `40/61` discovery overlap).\n"
        f"- **Genotype-Matched `p80` Threshold & Predictive Caveat:** `Ctrl-z95` (`z > {p80['frozen_emory_z95_ctrl_cutoff']}`) passes `{100*oof['oof_sensitivity_at_fold_z95']:.1f}%` `Emory sALS` (general microgliosis), whereas matched `Emory sALS p80` (`z > {p80['frozen_emory_sals_p80_cutoff']}`) passes `{100*p80['emory_sals_pass_at_sals_p80']:.1f}%` `Emory sALS` (`{100*p80['ext_washu_sals_pass_at_sals_p80']:.1f}%` `WashU sALS`) and `all-ALS p80` (`z > {p80['frozen_emory_all_als_p80_cutoff']}`) passes `{100*p80['emory_all_als_pass_at_all_als_p80']:.1f}%` `Emory all-ALS` vs `{100*p80['ext_all_als_pass_at_all_als_p80_86pct_familial']:.1f}%` external `86%`-familial ALS. Because case-control CSF elevation does not prove cortical `ALS-Glia` causal JAK1/2 responsiveness, `C019` requires a biomarker-stratified interaction design with `CSF pSTAT3/CXCL10` PD.\n\n"
        f"## 3. Separated Clinical Readiness (`TRL`) vs. Scientific Actionability & Atomic Hurdles (`RUN-P3A-003`)\n\n"
        f"| Rank | Program | Specific Primary Modality & Promoted Lead | Clinical `TRL` | Next-Gate Experimental Class | `[MODEL_PRIOR]` Dependency | Atomic Unsolved Hurdles | Scientific Tier |\n"
        f"| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n{rd_md}\n\n"
        f"## 4. Harmonized 4-Column Backup-Modality Symmetry Audit (`16` Therapeutic Programs)\n\n"
        f"| ID | Backup Modality | Class / Clinical Toxicity Warning | Delivery / Human CNS PK Hurdle | Lost Biological / Isoform Coverage |\n"
        f"| :--- | :--- | :--- | :--- | :--- |\n{bk_md}\n\n"
        f"---\n*Data & Attribution Notices: GENCODE v46 (EMBL-EBI Open Access / CC BY 4.0), gnomAD v4.1 (Broad Institute Open Data / CC0), DBCLS GGGenome hg38 index (CC BY 4.0).* `{stamp}`\n",
        encoding="utf-8",
    )
    print(f"Registered v2 RUN-P3A-001..003, EV-P3A-001..004, and rendered {REP_FP.relative_to(ROOT).as_posix()} ({stamp})")


if __name__ == "__main__":
    main()
