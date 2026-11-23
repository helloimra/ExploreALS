# ExploreALS v1.3.0 Registry & Provenance Lock Schemas

`ExploreALS v1.3.0` stores its relational data across **`18` normalized, schema-verified CSV ledgers** under `registries/` and **`2` deterministic JSON lock manifests** (`dataset_files_lock.json` and `verified_citations_lock.json`) shipped under `schemas/`, validated end-to-end by `scripts/verify_carbon_als.py`.

## 1. `registries/candidate_intake_ledger.csv`
Tracks all `33` published clinical, Mendelian/GWAS, and neuropathological ALS programs across two intake cohorts:
- `CANONICAL_24` (`C001`–`C024`: published clinical, genetic, splicing, and neuroinflammatory programs)
- `SCREEN_AND_BLIND_SURVIVORS_9` (`S01`–`S09`: unadopted `Bye 2025` FDR-significant hits, stopped FTIs, and recurrent blind-discovery mechanisms)

**Columns:**
`carbon_id,explore_id,cohort_group,track,candidate_type,name,genes_or_drug_ids,explore_tier,explore_status,explore_scores_epn,is_composite_axis,carbon_taste_critique,planned_reanalysis_assays,staged_dataset_ids,assigned_batch`

## 2. `registries/subnode_dissection.csv`
De-bundles multi-subunit complexes, GWAS loci, and biofluid panels (`C014`, `C015`, `C023`, `C017`, `C018`; `18` rows) into single-gene molecular hypotheses evaluated independently.

**Columns:**
`subnode_id,parent_carbon_id,gene_symbol,molecular_role,explore_bundled_claim,key_risk_or_taste_question,gnomad_essentiality_check,druggability_check,reanalysis_status,subnode_verdict`

## 3. `registries/candidate_decisions.csv`
Canonical Phase 1–4 adjudication table (`33` rows: `4 KEEP_CORE`, `13 KEEP_EXPLORATORY_UNPROVEN`, `4 RECLASSIFY_BENCHMARK_OR_BIOMARKER`, `12 DROP`) enforcing the **Epistemic Asymmetry Rule**.

**Columns:**
`carbon_id,name,track,phase1_batch,reanalysis_state,scientific_taste_rating,technical_accuracy_of_explore_claim,causal_vs_reactive_assessment,prior_art_crowding_level,evidence_proves_hypothesis,evidence_disproves_hypothesis,epistemic_state,decision,factual_justification,discriminating_next_test,supporting_evidence_ids,updated_at`

**Allowed Enums (enforced by `verify_carbon_als.py`):**
- `reanalysis_state`: `PENDING_PHASE1_REANALYSIS`, `IN_PROGRESS`, `ADJUDICATED_VERIFIED`
- `epistemic_state`: `PENDING`, `SUPPORTED`, `UNPROVEN_UNTESTED`, `FALSIFIED_CLINICAL`, `FALSIFIED_PK_SAFETY`, `ARTIFACT_CONFOUNDED`, `ESTABLISHED_BENCHMARK`
- `decision`: `PENDING`, `KEEP_CORE`, `KEEP_EXPLORATORY_UNPROVEN`, `RECLASSIFY_BENCHMARK_OR_BIOMARKER`, `DROP`
- **Hard Invariant:** If `decision == "DROP"`, `epistemic_state` MUST be one of `{FALSIFIED_CLINICAL, FALSIFIED_PK_SAFETY, ARTIFACT_CONFOUNDED}` and `factual_justification` + `supporting_evidence_ids` MUST be non-empty. `epistemic_state == "UNPROVEN_UNTESTED"` is strictly forbidden from mapping to `DROP`.

## 4. `registries/datasets_manifest.csv`
Tracks all `42` biomedical datasets, 3D structures, and genome reference maps (`40` external accessions + `2` repo-bundled reference maps) with 64-character SHA-256 digests, partitioned across **`28` `TIER_A_OPEN_REDISTRIBUTABLE`, `12` `TIER_B_PUBLISHER_HTTPS_FETCH`, and `2` `TIER_C_DUA_OR_BASELINE`** (registered-access Synapse entries `DS003_PB` `syn51105515` and `DS026_FUJITA` `syn52335732`), storing canonical fetch URLs and access instructions in `canonical_fetch_url_or_instructions` (paired with per-file relative paths, redistribution tiers, byte sizes, and SHA-256 hashes in `schemas/dataset_files_lock.json`).

**Columns:**
`dataset_id,domain,local_relpath,upstream_explore_relpath,accession_or_doi,license_or_access,size_bytes,sha256,relevant_candidates,description,redistribution_tier,canonical_fetch_url_or_instructions`

## 5. `registries/evidence_ledger.csv`
Stores `170` atomic, header-resolved quantitative, structural, and bibliographic findings (`EV-B1-*` through `EV-P4-009`).

**Columns:**
`evidence_id,carbon_id,subnode_id,analysis_run_id,source_type,source_id_or_locator,cohort_and_stratum,assay_and_contrast,effect_direction,effect_estimate,p_value,fdr_or_adjusted_p,sample_size_n,epistemic_weight,notes`

## 6. `registries/analysis_runs.csv`
Logs all `50` reproducible computational, genomic, structural, and statistical scripts executed across Phases 1–4 (`RUN-B1-*` through `RUN-P4-003`).

**Columns:**
`analysis_run_id,phase_batch,script_relpath,output_artifacts,datasets_used,tools_and_skills_used,reproduced_verified,run_timestamp_utc,summary`

## 7. `registries/phase2_multiplex_intervals.csv`
Coordinate-only (`GRCh38` 1-based closed, zero synthetic oligomer sequences) cis-regulatory splice-rescue intervals (`12` rows) ranked across `KCNQ2`, `UNC13A`, `STMN2`, and `G2E3`.

**Columns:**
`candidate_id,gene_symbol,multiplex_tier,rank_within_gene,interval_id,chrom,grch38_start,grch38_end,strand,length_bp,mode,gc_pct,tm_moe_c,tm_phys_pops_c,dg37_kcal,cpg_dinucs,max_self_stem_bp,iss_motifs,ese_motifs,tdp43_ug_dinucs,wt_bystander_sponge_flag,mean_avi_phred,max_avi_phred,boundary_dist_bp,composite_score,analysis_run_id`

## 8. `registries/phase3_sso_offtarget_audit.csv`
Exhaustive human spliced-transcriptome (`DS_GENCODE_V46_TX` x `DS_GENCODE_V46_COMP_GTF` exon-exon junction & `CDS` coordinates) and genome-wide nascent pre-mRNA (`GGGenome hg38` ungapped `0–2 mm` + `1-nt` bulge + `18-bp` sub-core x internal splice boundaries x 7-lineage CNS expression x `DS_GNOMAD_V41_CONSTRAINT`) off-target hybridization screen across all `12` Phase 2 splice intervals.

**Columns:**
`candidate_id,gene_symbol,rank_within_gene,interval_id,length_bp,tm_phys_pops_c,gggenome_max_mm_queried,spliced_0mm_genes,spliced_1mm_genes,spliced_2mm_pc_genes,spliced_wobble_only_pc_genes,premRNA_0mm_sense_genes,premRNA_1mm_sense_genes,premRNA_1mm_splice50bp_genes,premRNA_wobble_only_splice50bp_pc_genes,premRNA_2mm_splice25bp_pc_genes,bulge_1nt_steric_pc_genes,sub18_core_steric_pc_genes,flagged_constrained_neuronal_hits,offtarget_safety_status,analysis_run_id`

## 9. `registries/phase3_execution_readiness.csv`
Scientific actionability & experimental-gate staging (separating causal human genetics/pathology anchor strength from clinical `TRL` readiness), atomic 1-domain-per-token hurdle decomposition, sequential single-to-multiplex IND staging, `[MEASURED]` vs `[MODEL_PRIOR]` separation, and backup-modality symmetry across the `17` non-dropped curated survivors (`4 KEEP_CORE` + `13 KEEP_EXPLORATORY_UNPROVEN`).

**Columns:**
`priority_rank_overall,candidate_id,gene_or_drug,primary_modality_specific,phase2_decision_tier,epistemic_state,clinical_readiness_trl,next_gate_experimental_class,primary_evidence_basis,model_prior_dependency,unsolved_hurdle_count,unsolved_hurdles_structured,regulatory_ind_staging,phase3a_safety_or_generalization_gate,backup_modality,backup_class_warning,backup_delivery_pk_hurdle,backup_lost_target,scientific_actionability_tier,analysis_run_id`

## 10. `registries/phase3b_denovo_candidates.csv`
Systematic multi-omic discovery candidates (`DN-01`–`DN-19`, strictly `1` atomic HGNC gene or screened drug per row with `0` overlap against `candidate_intake_ledger.csv` + `subnode_dissection.csv`), combining Epistemic Asymmetry (`UNPROVEN_UNTESTED != FALSIFIED`) with `TRL` vs scientific actionability separation, atomic `;`-delimited hurdles, and `[MEASURED]` vs `[MODEL_PRIOR]` basis tags.

**Columns:**
`denovo_id,discovery_funnel,gene_or_drug,candidate_type,primary_modality_specific,mechanism_summary,causal_vs_reactive_assessment,epistemic_state,decision,clinical_readiness_trl,next_gate_experimental_class,primary_evidence_basis,model_prior_dependency,unsolved_hurdle_count,unsolved_hurdles_structured,scientific_actionability_tier,factual_justification,discriminating_next_test,supporting_denovo_evidence_ids,analysis_run_id`

## 11. `registries/phase3b_denovo_sso_intervals.csv`
Coordinate-only (`GRCh38` 1-based closed, zero raw oligomer nucleotide sequences) de novo steric-SSO / `3'Ext` search windows (`16` rows) paired upfront with the `254,070`-transcript `GENCODE v46` and `GGGenome hg38` nascent pre-mRNA off-target safety screen and AlphaGenome Atlas locus links.

**Columns:**
`denovo_id,gene_symbol,rank_within_gene,interval_id,chrom,grch38_start,grch38_end,strand,length_bp,cis_mechanism_class,gc_pct,tm_phys_pops_c,dg37_kcal,cpg_dinucs,max_self_stem_bp,ese_motifs,mean_avi_phred,max_avi_phred,boundary_dist_bp,composite_score,gggenome_max_mm_queried,spliced_0mm_genes,spliced_1mm_genes,spliced_2mm_pc_genes,spliced_wobble_only_pc_genes,premRNA_0mm_sense_genes,premRNA_1mm_sense_genes,premRNA_1mm_splice50bp_genes,premRNA_wobble_only_splice50bp_pc_genes,premRNA_2mm_splice25bp_pc_genes,bulge_1nt_steric_pc_genes,sub18_core_steric_pc_genes,flagged_constrained_neuronal_hits,offtarget_safety_status,alphagenome_atlas_url,analysis_run_id`

## 12. `registries/phase3b_denovo_evidence.csv`
Atomic, single-contrast primary quantitative and clinical/structural evidence rows (`32` `EV-P3B-*` rows) backing `phase3b_denovo_candidates.csv`, validated under the identical `provenance_gates.py` rules (`p_value <= fdr_or_adjusted_p`, no `"NA"`/`"0.99"` placeholders, donor-level `sample_size_n`) as `evidence_ledger.csv`.

**Columns:**
`evidence_id,carbon_id,subnode_id,analysis_run_id,source_type,source_id_or_locator,cohort_and_stratum,assay_and_contrast,effect_direction,effect_estimate,p_value,fdr_or_adjusted_p,sample_size_n,epistemic_weight,notes`

## 13. `registries/phase4_unified_portfolio.csv`
Canonical cross-phase master portfolio (`52` rows = disjoint union of `33` curated clinical/genetic programs + `19` multi-omic screen nominations: `4 KEEP_CORE`, `25 KEEP_EXPLORATORY_UNPROVEN`, `7 RECLASSIFY_BENCHMARK_OR_BIOMARKER`, `16 DROP`), paired 1-to-1 with immutable `EALS-001`–`EALS-052` accessions and ranked `1..52` under scientific actionability, human causal/pathology evidence basis, Epistemic Asymmetry, atomic `;`-delimited hurdles, and promoted `GRCh38` cis-interval off-target statuses (`scripts/phase4_gates.py`).

**Columns:**
`unified_rank,accession_id,portfolio_id,origin_phase,origin_subcohort,track,gene_or_drug,candidate_type,primary_modality_specific,epistemic_state,decision,scientific_actionability_tier,clinical_readiness_trl,next_gate_experimental_class,primary_evidence_basis,model_prior_dependency,unsolved_hurdle_count,unsolved_hurdles_structured,lead_cis_interval_id,lead_offtarget_safety_status,key_quantitative_anchor,discriminating_next_test,source_registry_ref,analysis_run_id`

## 14. `registries/phase4_unified_cis_intervals.csv`
Unified coordinate-only (`GRCh38` 1-based closed, zero raw oligomer nucleotide sequences) cis-regulatory search-window registry (`28` rows = `12` Phase 2/3A intervals + `16` Phase 3B intervals) paired 1-to-1 with `EALS-NNN` / `EALS-NNN.k` accessions, human spliced-transcriptome (`254,070` `GENCODE v46` transcripts), and `GGGenome hg38` nascent pre-mRNA off-target safety classifications.

**Columns:**
`unified_interval_order,origin_phase,accession_id,subnode_accession_id,portfolio_id,subnode_or_cand_id,gene_symbol,program_role,rank_within_gene,is_promoted_lead,interval_id,chrom,grch38_start,grch38_end,strand,length_bp,cis_mechanism_or_mode,gc_pct,tm_phys_pops_c,dg37_kcal,cpg_dinucs,max_self_stem_bp,ese_motifs,mean_avi_phred,max_avi_phred,boundary_dist_bp,composite_score,spliced_0mm_genes,spliced_1mm_genes,spliced_2mm_pc_genes,spliced_wobble_only_pc_genes,premRNA_0mm_sense_genes,premRNA_1mm_sense_genes,premRNA_1mm_splice50bp_genes,premRNA_wobble_only_splice50bp_pc_genes,premRNA_2mm_splice25bp_pc_genes,bulge_1nt_steric_pc_genes,sub18_core_steric_pc_genes,flagged_constrained_neuronal_hits,offtarget_safety_status,source_offtarget_run_id,analysis_run_id`

## 15. `registries/statistical_models_and_contrasts.csv`
Exact 1-to-1 statistical model, sample-unit, covariate-vs-multiplicity $p$-value, cohort-overlap, and 64-character SHA-256 provenance ledger across all `202` primary evidence rows (`170` `evidence_ledger.csv` + `32` `phase3b_denovo_evidence.csv`).

**Columns:**
`evidence_id,analysis_run_id,inference_class,statistical_unit,n_statistical_units,n_unique_donors_or_participants,exact_contrast,model_formula_or_test,effect_metric,effect_estimate,se_or_ci95,unadjusted_or_primary_nominal_p,covariate_adjusted_nominal_p,multiplicity_adjusted_p,multiple_testing_family,missingness_or_exclusion_rule,overlap_group_id,anchor_type,anchor_relpath,sha64`

## 16. `registries/cohort_overlap_map.csv`
Explicit participant-sharing and nested-sampling matrix across all `8` empirical shared-donor / shared-lineage cohort clusters (`OVL_NYGC_POSTMORTEM`, `OVL_MIT_PINEDA_CORTEX`, `OVL_EDINBURGH_SNRNA`, `OVL_TRAUTWIG_CSF`, `OVL_SPILLMAN_FRACTIONS`, `OVL_IN_VITRO_TDP43_KD`, `OVL_ANSWERALS_IPSC`, `OVL_PAIRED_AND_NESTED_TISSUE`).

**Columns:**
`overlap_group_id,cluster_name,datasets_involved,overlap_mechanism,donor_accounting_and_anti_pseudoreplication_rule,canonical_model_formula`

## 17. `registries/living_evidence_updates.csv`
Chronological living-evidence, clinical-trial readout, and structural/genomic model-revision ledger (`8` rows: `UPD-2026-11-18-01` through `UPD-2026-11-23-01`), tracking explicit before/after revisions (`prior_state_or_assumption` vs `new_evidence_or_revision`), portfolio & gate consequences, verified primary identifiers, and reproducible verification anchors.

**Columns:**
`update_id,date_iso,release_tag,update_category,affected_ids,decision_impact,headline,prior_state_or_assumption,new_evidence_or_revision,portfolio_and_gate_consequence,primary_sources,verification_anchor`

## 18. `registries/candidate_accessions.csv`
Canonical immutable ExploreALS accession & fuzzy-alias master ledger (`70` rows = `52` `CANDIDATE` rows `EALS-001`–`EALS-052` in deterministic ledger-ingestion order + `18` `SUBUNIT` rows `EALS-014.1`–`EALS-023.6`), bridging `EALS-NNN` accessions to Phase 1–3 `legacy_id` foreign keys (`C001`–`C024`, `S01`–`S09`, `DN-01`–`DN-19`, `C014-N1`–`C023-N6`) and curated HGNC/INN search aliases.

**Columns:**
`accession_id,legacy_id,entity_kind,parent_accession_id,origin_phase,primary_symbol_or_inn,search_aliases`

## 19. JSON Lock Manifests (`schemas/*.json`)
- **`schemas/dataset_files_lock.json`**: Per-file byte sizes and 64-character SHA-256 checksums across all `42` `datasets_manifest.csv` entries (supporting cross-platform `LF`/`CRLF` text normalization on directory-level reference bundles).
- **`schemas/verified_citations_lock.json`**: Live-verified metadata lock across `PMID`, `NCT`, `DOI`, and international trial identifiers (`CTR`, `ANZCTR`), preventing unverified bibliographic or clinical-registry citations across registries and rendered HTML/Markdown reports.
