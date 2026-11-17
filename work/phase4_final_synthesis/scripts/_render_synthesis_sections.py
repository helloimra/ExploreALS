"""Programmatic Markdown section builders for reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from _candidate_contrasts_b import KEY_MECHANISTIC_CONTRASTS_9
from _phase4_helpers import biological_evidence_sort_key

ROOT_POSIX = Path(__file__).resolve().parents[3].as_posix()


def atlas_url(chrom: str, start: str, end: str, pad_bp: int = 250) -> str:
    lo = max(1, int(start) - pad_bp)
    hi = int(end) + pad_bp
    return (
        f"https://deepmind.google.com/science/alphagenome/atlas?q={chrom}:{lo}-{hi}"
        "&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE"
    )


def build_exec_and_transition_md(
    summary: dict[str, Any],
    port_rows: list[dict[str, str]],
    intake_map: dict[str, dict[str, str]],
) -> list[str]:
    sha = summary["registry_sha12"]
    cd = summary["counts_by_decision"]
    ce = summary["counts_by_scientific_tier"]
    cp = summary["counts_by_epistemic_state"]
    ox = summary["origin_x_tier_matrix"]
    et_map = summary["explore_tier_to_carbon_decision"]

    lines = [
        "# CarbonALS v1.2 (ExploreALS v1.2) — Final Cross-Phase Portfolio & Translational Execution Synthesis",
        "",
        f"<!-- REGISTRY_CONCORDANCE_SHA12: p4_port={sha['phase4_unified_portfolio']} p4_cis={sha['phase4_unified_cis_intervals']} "
        f"p3a_ot={sha['phase3_sso_offtarget_audit']} p3a_rd={sha['phase3_execution_readiness']} "
        f"p3b_cand={sha['phase3b_denovo_candidates']} p3b_sso={sha['phase3b_denovo_sso_intervals']} -->",
        "",
        "> **Programmatically rendered** by `02_render_phase4_synthesis.py` (`RUN-P4-002`) from verified registries "
        f"[phase4_unified_portfolio.csv](file:///{ROOT_POSIX}/registries/phase4_unified_portfolio.csv) (`59` candidates), "
        f"[phase4_unified_cis_intervals.csv](file:///{ROOT_POSIX}/registries/phase4_unified_cis_intervals.csv) (`26` `GRCh38` Coordinate-Only Cis-Regulatory Search Windows, `0` chemically modified synthesis-ready ASO sequences), and "
        f"[subnode_dissection.csv](file:///{ROOT_POSIX}/registries/subnode_dissection.csv) (`19` unbundled sub-nodes). "
        f"Synthesizes Phase 1 ([PHASE1_PORTFOLIO_ADJUDICATION_REPORT.md](file:///{ROOT_POSIX}/reports/PHASE1_PORTFOLIO_ADJUDICATION_REPORT.md)), "
        f"Phase 2 ([CARBON_ALS_PHASE2_MASTER_PORTFOLIO_SYNTHESIS.md](file:///{ROOT_POSIX}/reports/CARBON_ALS_PHASE2_MASTER_PORTFOLIO_SYNTHESIS.md)), "
        f"Phase 3A ([PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md](file:///{ROOT_POSIX}/reports/phase3/PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md)), and "
        f"Phase 3B ([PHASE3B_DENOVO_UNBIASED_DISCOVERY.md](file:///{ROOT_POSIX}/reports/phase3/PHASE3B_DENOVO_UNBIASED_DISCOVERY.md)).",
        "",
        "## 1. Executive Summary & `ExploreALS` -> `CarbonALS` Paradigm Shift",
        "",
        "Across four staged computational and clinical-archaeology phases (`49` reproducible runs in `registries/analysis_runs.csv` across `48` SHA-256-locked open-access staged datasets), `CarbonALS` re-adjudicated all `40` `ExploreALS`-inherited candidates, decomposed `4` multi-gene composite bundles into `19` single-gene sub-nodes, and executed an unbiased genome-wide / proteome-wide / phenotypic-screen *de novo* expansion yielding `19` non-overlapping Phase 3B candidates (**`59` unified candidates total**):",
        "",
        "| Scientific Actionability & Decision Partition | `ExploreALS`-Inherited (`40`) | Phase 3B *De Novo* (`19`) | Unified Total (`59`) | Epistemic State & Governance Rule |",
        "| :--- | :---: | :---: | :---: | :--- |",
        f"| **`TIER_1_ACTIONABLE_NOW`** (`2 KEEP_CORE` + `1 KEEP_EXPLORATORY`) | `{ox['EXPLORE_INHERITED_40'].get('TIER_1_ACTIONABLE_NOW', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('TIER_1_ACTIONABLE_NOW', 0)}` | **`{ce['TIER_1_ACTIONABLE_NOW']}`** | `KEEP_CORE`-first execution (`#1 S06`, `#2 C006`) + `TRL_6` BioVendor-bridged-pNfH Ph3 (`#3 S07`) |",
        f"| **`TIER_2_FOCUSED_GATE_FIRST`** (`2 KEEP_CORE` + `3 KEEP_EXPLORATORY`) | `{ox['EXPLORE_INHERITED_40'].get('TIER_2_FOCUSED_GATE_FIRST', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('TIER_2_FOCUSED_GATE_FIRST', 0)}` | **`{ce['TIER_2_FOCUSED_GATE_FIRST']}`** | Focused preclinical/PD/IND gate before clinical commitment (`C001`, `C002`, `C007`, `DN-01`, `DN-04`) |",
        f"| **`TIER_3_EXPLORATORY_DISCOVERY`** (`{ce['TIER_3_EXPLORATORY_DISCOVERY']} KEEP_EXPLORATORY`) | `{ox['EXPLORE_INHERITED_40'].get('TIER_3_EXPLORATORY_DISCOVERY', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('TIER_3_EXPLORATORY_DISCOVERY', 0)}` | **`{ce['TIER_3_EXPLORATORY_DISCOVERY']}`** | Retained under Epistemic Asymmetry (`UNPROVEN_UNTESTED`); **preclinical discovery triage queue only** — not therapeutic endorsement |",
        f"| **`COMPANION_PROTOCOL_ONLY`** (`1 KEEP_EXPLORATORY`) | `{ox['EXPLORE_INHERITED_40'].get('COMPANION_PROTOCOL_ONLY', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('COMPANION_PROTOCOL_ONLY', 0)}` | **`{ce['COMPANION_PROTOCOL_ONLY']}`** | `C005` TMS SICI/SDTC + living-CSF `NPTX2` stage-gating protocol for `C006` (never a drug bundle) |",
        f"| **`BIOMARKER_BENCHMARK_ONLY`** (`7 RECLASSIFY`) | `{ox['EXPLORE_INHERITED_40'].get('BIOMARKER_BENCHMARK_ONLY', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('BIOMARKER_BENCHMARK_ONLY', 0)}` | **`{ce['BIOMARKER_BENCHMARK_ONLY']}`** | `ESTABLISHED_BENCHMARK` (`C013`, `S08`, `C003`, `C017`, `DN-10..12`: SOC / PD / fluid staging panels) |",
        f"| **`DROPPED_FALSIFIED_EXCLUDED`** (`{ce['DROPPED_FALSIFIED_EXCLUDED']} DROP`) | `{ox['EXPLORE_INHERITED_40'].get('DROPPED_FALSIFIED_EXCLUDED', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('DROPPED_FALSIFIED_EXCLUDED', 0)}` | **`{ce['DROPPED_FALSIFIED_EXCLUDED']}`** | Positive counterevidence only: `{cp['FALSIFIED_CLINICAL']}` clinical + `{cp['FALSIFIED_PK_SAFETY']}` PK/safety + `{cp['ARTIFACT_CONFOUNDED']}` artifact |",
        f"| **Total** | **`40`** | **`19`** | **`59`** | **`{cd['KEEP_CORE']}` `KEEP_CORE` · `{cd['KEEP_EXPLORATORY_UNPROVEN']}` `KEEP_EXPLORATORY` · `{cd['RECLASSIFY_BENCHMARK_OR_BIOMARKER']}` `BENCHMARK` · `{cd['DROP']}` `DROP`** |",
        "",
        "### 1.1 `ExploreALS` Original Tier -> `CarbonALS` Re-Adjudication Matrix (`0/4` Core Overlap)",
        "",
        "**Complete Core Inversion:** Zero (`0/4`) of `ExploreALS`'s `Tier_1_White_Space_Core` picks (`C013 Riluzole`, `C015 8-gene SNARE/Rab bundle`, `C016 FBXL5`, `C019 Baricitinib`) survived as `KEEP_CORE` in `CarbonALS`. `C013` is an approved SOC positive control (`ESTABLISHED_BENCHMARK`); `C015` inflated `5/8` passenger/pan-essential sub-nodes (`NSF Chronos = -2.44`, `STX5 = -1.13`, `GDI2` CSF DIA `p = 0.5042`) and saw `G2E3` `#1/#2` fail `0mm` off-target safety (`#1`: `375` Alu-SINE spliced + `7,211` pre-mRNA `0mm` genes; `#2`: `1` spliced `LRP1B` + `37` pre-mRNA `0mm`); `C016` postmortem RNA elevation proved microglial (`Edinburgh Microglia p = 0.00334`) rather than excitatory neuronal (`Edinburgh Exc p = 0.175`, `Pineda BA4_Exc p = 0.208`); and `C019` (`3.80 nM` CSF at `4 mg/d` = modeled `~8.7%` whole-cell pSTAT occupancy, `1/9` PE SAE + `1/9` DVT in `NADALS` `N = 9`, and a `JAK1`-vs-autonomous-neuronal-`JAK2` APA catch-22) is demoted to `TIER_3_EXPLORATORY_DISCOVERY` (`5` hurdles, `#24/59`). Conversely, `CarbonALS`'s `4 KEEP_CORE` anchors (`S06 SARM1`, `C006 KCNQ2`, `C001 UNC13A`, `C002 STMN2`) originated in `ExploreALS` `Tier_2` (`2`), `Tier_4` (`1`), and unadopted blind survivors (`1`):",
        "",
        "| `ExploreALS` Upstream Tier (`40` Items) | `KEEP_CORE` | `KEEP_EXPLORATORY` | `BENCHMARK` | `DROP` | Key Re-Calibration Mechanism |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |",
    ]
    notes = {
        "Tier_1_White_Space_Core": "`C013` -> SOC benchmark; `C019` (`5`-hurdle `JAK1/JAK2` catch-22 + `657x` CSF gap), `C015` (`5/8` dropped, `G2E3` 0mm fail) & `C016` (glial iron) -> `TIER_3`",
        "Tier_2_Crowded_Clinical_Benchmarks_And_Combinatorial_Anchors": "`C001` (`UNC13A #2`) & `C002` (`STMN2 #2`) retained as `KEEP_CORE` (`TIER_2` Stage 2 multiplex anchors; standalone 1-plex crowded)",
        "Tier_3_Subtype_Restricted_Class_Caution_Or_Safety_Hold": "`C017` -> CSF staging biomarker (`rs3831317` KO null, `GPNMB` protective); `C018` (`C3` MERIDIAN drop, `C1q` IT watchlist) & `C020` (pulsed PIKfyve) -> `TIER_3`; `C021` -> `DROP`",
        "Tier_4_Exploratory_Mechanistic_Comparators": "`C006` (`KCNQ2` exon-5 SSO) promoted to `KEEP_CORE` & `TIER_1` (#2 overall); `C007` (`TIER_2`), `C014` (`TIER_3`), `C005` (companion protocol); `C010` (`Ropinirole` PK/safety deficit + EXPERTS-ALS blood-NfL futility) -> `DROP` (`FALSIFIED_PK_SAFETY`)",
        "Tier_5_Parked_Negative_Or_Exposure_Benchmarks": "`C003` (`Ezogabine`) -> TMS SICI PD calibrator; `C004`, `C008`, `C009`, `C011`, `C012` confirmed `DROP` (`FALSIFIED_CLINICAL` / `FALSIFIED_PK_SAFETY`)",
        "BA9_Frozen_Naming_Call_Unscored": "`8/10` collapsed after `NYGC`/snRNA GC-content adjustment (`ARTIFACT_CONFOUNDED`); `BA9-04` (`DNAJB2a`) & `BA9-08` (`SNPH`) rescued under Epistemic Asymmetry (`TIER_3`)",
        "Unadopted_Screen_Or_Blind_Survivor": "`S06` (`SARM1` non-orthosteric T-lock) -> `KEEP_CORE` (`TIER_1` #1); `S07` (`Aldesleukin` low-pNfH) -> `TIER_1` (#3); `S09` (`Censavudine`) & `S02` (`CuATSM` `NCT04082832` unreported) -> `TIER_3`; `S08` -> SOC benchmark; `4` `DROP`",
    }
    for et in (
        "Tier_1_White_Space_Core",
        "Tier_2_Crowded_Clinical_Benchmarks_And_Combinatorial_Anchors",
        "Tier_3_Subtype_Restricted_Class_Caution_Or_Safety_Hold",
        "Tier_4_Exploratory_Mechanistic_Comparators",
        "Tier_5_Parked_Negative_Or_Exposure_Benchmarks",
        "BA9_Frozen_Naming_Call_Unscored",
        "Unadopted_Screen_Or_Blind_Survivor",
    ):
        d = et_map.get(et, {})
        lines.append(
            f"| `{et}` | `{d.get('KEEP_CORE', 0)}` | `{d.get('KEEP_EXPLORATORY_UNPROVEN', 0)}` | "
            f"`{d.get('RECLASSIFY_BENCHMARK_OR_BIOMARKER', 0)}` | `{d.get('DROP', 0)}` | {notes[et]} |"
        )
    lines.extend([
        "",
        "### 1.2 Nine Key Mechanistic Contrasts & Translational Falsifications",
        "",
        "| Program(s) | Mechanistic Domain | Naive Field Assumption | Verified Re-Analysis Finding | Pre-Specified Falsification / Gate |",
        "| :--- | :--- | :--- | :--- | :--- |",
        *[
            f"| {', '.join(f'**`{x}`**' for x in row['ids'])} | **{row['domain']}** | {row['naive']} | {row['finding']} | {row['gate']} |"
            for row in KEY_MECHANISTIC_CONTRASTS_9
        ],
    ])
    return lines


def build_roadmaps_and_tables_md(
    summary: dict[str, Any],
    port_rows: list[dict[str, str]],
    cis_rows: list[dict[str, str]],
    sub_rows: list[dict[str, str]],
) -> list[str]:
    celf = summary["dn04_celf5_deep_profile"]
    gl = celf["gene_liability_profile"]
    ny_c = celf["celf5_nygc_multiregion"]["Spinal_Cord_Cervical"]
    ny_l = celf["celf5_nygc_multiregion"]["Spinal_Cord_Lumbar"]
    ny_m = celf["celf5_nygc_multiregion"]["Cortex_Motor"]
    pan = celf["phase3b_f1_f2_nygc_panel_summary"]

    bio_rk_map = {r["portfolio_id"]: i for i, r in enumerate(sorted(port_rows, key=biological_evidence_sort_key), 1)}
    lines = [
        "",
        "## 2. Top-8 Translational Execution Roadmaps (`TIER_1` `#1–#3` & `TIER_2` `#4–#8`)",
        "",
        "All `8` `TIER_1` + `TIER_2` programs separate **`[MEASURED]`** primary empirical evidence from **`[MODEL_PRIOR]`** order-of-magnitude structural/thermodynamic/ODE assumptions (`COARSE_PRIOR_ONLY`), order `TIER_1` by **`KEEP_CORE` causal certainty first** (`#1 S06`, `#2 C006` ahead of highest-`TRL` `KEEP_EXPLORATORY_UNPROVEN` `#3 S07`), enforce FDA `21 CFR 300.50` fixed-combination IND staging (sponsor-owned single-entity Stage 1 GLP intrathecal tox/PD and cervical/cortical parenchymal splice-rescue proof on uncrowded `C006 KCNQ2` before Stage 2 genotype-stratified `2`-plex [`KCNQ2 + STMN2 #2`] vs `3`-plex [`+ UNC13A #2`] randomization across `rs12973192`/`rs12608932` genotypes, with zero right of reference to competitor 1-plex trials), and enumerate atomic unsolved hurdles:",
        "",
        "| Act (`Bio`) | ID & Program | Origin | Decision (`State`) | Specific Modality & Lead `GRCh38` Interval | `TRL` & Experimental Gate | `[MODEL_PRIOR]` Dependency | Hurdles |",
        "| :---: | :--- | :---: | :--- | :--- | :--- | :--- | :---: |",
    ]
    for r in port_rows[:8]:
        brk = bio_rk_map[r["portfolio_id"]]
        lines.append(
            f"| `#{r['unified_rank']}` (`#{brk}`) | **`{r['portfolio_id']}`** ({r['gene_or_drug']}) | `{r['origin_phase']}` | **`{r['decision']}`** (`{r['epistemic_state']}`) | "
            f"`{r['primary_modality_specific']}` (Lead: `{r['lead_cis_interval_id']}` `{r['lead_offtarget_safety_status']}`) | "
            f"`{r['clinical_readiness_trl']}` · `{r['next_gate_experimental_class']}` | `{r['model_prior_dependency']}` | **`{r['unsolved_hurdle_count']}`** |"
        )

    lines.extend([
        "",
        "### 2.1 Execution Highlights & Kill-Gates for `TIER_1` (`#1–#3`), `TIER_2` Co-Leads (`#7 DN-01`, `#8 DN-04`), Top `TIER_3` (`#9 DN-05`), and Watchlist Case Study (`#24 C019`)",
        "",
        "1. **`#1 S06` `SARM1` Non-Covalent `ARM–TIR` T-Lock (`TIER_1_ACTIONABLE_NOW`, `KEEP_CORE`, `TRL_4`, `2` hurdles):** `[MEASURED]` Cryo-EM `PDB 9TZY` (`PMID:42156967`) proves orthosteric `1-AD` `BEXi` prodrugs (`LY3873862 NCT07883590` [Ph1 Not Yet Recruiting], `DSRM-3716`) bridge `3` `TIR` chains (`122/122` sub-`IC50` activation contacts) and spike WT `SARM1` at trough washout, whereas reversible orthosteric `NB-4746` (`NCT07369076`, undisclosed clinical structure) requires empirical head-to-head washout testing and `Cys311` isothiazoles (`PDB 7DJT`, `PMID:33944777`) serve as structural octamer benchmarks rather than chronic oral clinical leads. `CarbonALS` prioritizes non-covalent intramolecular `ARM–TIR` T-locks (`ASHA-624` class; `~2–7x` MWC sparing `[MODEL_PRIOR]`, testable in parallel human iPSC-MN `SARM1` T-lock +/- `STMN2` SSO washout curves), excludes `<1%` constitutive `ARM`-broken GoF carriers via sequencing, and deploys a `3`-layer per-target PK/TE/PD panel: unbound CSF $C_{\\text{trough},u} \\ge \\text{IC}_{80}$ ($K_{p,\\text{uu}} \\ge 0.30$), neuron-derived EV (`L1CAM`/`ATP1A3+`) `cADPR:NAD+` + `SCG10/STMN2` target-engagement rescue (given mouse `Cd38-/-`-inferred non-neuronal `CD38` background in bulk lumbar `CSF cADPR`, `PMID:32087251`; `PMID:16750163`), and zero washout `CSF pNfH`/`NfL` spike.",
        "2. **`#2 C006` `KCNQ2` Exon-5 Steric SSO (`TIER_1_ACTIONABLE_NOW`, `KEEP_CORE`, `TRL_3`, `3` hurdles):** Uncrowded (`NCT = 0` for `KCNQ2` splice SSOs) Stage 1 single-entity intrathecal `2'-O-MOE` mixed-`PO/PS` `5-MeC` dense (`>=50`-oligo `18–22 nt` `1-nt`) Intron-4/Exon-5/Intron-5 exon-inclusion microwalk anchored on off-target-clean `#3 chr20:63442302-63442319(-)` (`UG = 1`, `modeled Tm ~53 °C [MODEL_PRIOR]`, `0/18` splicing `AVI` = `Cactus/DNase` conservation, unverified putative Intron-5 ISS; `CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED`) vs `#1 chr20:63442595-63442616(-)` (gated against **WT TDP-43 *cis*-eviction** from `KCNQ2` Intron-4 `(UG)8` in healthy TDP-43-intact oculomotor neurons, `PV+` cortical interneurons, and lumbar `DRGs`; `#2` deprioritized due to `PTCH1` `1-nt` bulge `WARN`), counter-screened against spontaneous human iPSC-neuron `Ca2+`-oscillation, `TLR9`, and primary `DRG` neurotox, benchmarked against `QRL-101` (`PDB 7CR2 Trp236` + `KCNQ2-DeltaE5` ER retention), and stratified by `C005` (`TMS SICI <= 5.5 ms` with `APB CMAP >= 1.0 mV` peripheral axonal `SDTC` fallback + preserved `CSF NPTX2`) before Stage 2 `21 CFR 300.50` **genotype-stratified co-delivery** — comparing `2`-plex (`KCNQ2 #3` + **`#5 C002` `STMN2 #2 chr8:79616829-79616846(+)`**, unvalidated `24–32 mg` total-PS scenario) vs unvalidated `<=36–48 mg` `3`-plex (`+` **`#4 C001` `UNC13A #2 chr19:17642537-17642554(-)`**) stratified across `rs12973192`/`rs12608932` genotypes (`~43%` NFE / `~35–38%` ALS `A/A`, testing rather than excluding `A/A` homozygotes and requiring multi-oligo GLP IT DRG/hydrocephalus tox beyond single-ASO nusinersen `50 mg` `PMID:41634391`), paired with a `3`-layer per-target PK/TE/PD readout (strand-specific CSF PK, `L1CAM+`/`ATP1A3+` NDEV pre-amplified dPCR + CSF synaptic/`SCG10` secretome + `C005` `TMS SICI` TE, and `>=16–24 wk` post-loading `CSF pNfH`/`NfL` PD accounting for sponsor-reported interim `QRL-201 ANQUR NCT05633459` `~46%` low-dose vs `~5%` `10 mg` `pNfH` dissociation; unfractionated CSF EVs sit near `Cq > 35` / `<3–10 copies/mL` LOQ, `PMID:38158550`; `PMID:38278991`).",
        "3. **`#3 S07` Low-Dose Aldesleukin (`TIER_1_ACTIONABLE_NOW`, `KEEP_EXPLORATORY_UNPROVEN`, `TRL_6`, `2` hurdles — Highest Clinical Proximity in Portfolio):** `[MEASURED]` MIROCALS (`NCT03039673`, `PMID:40354799`) SAP pre-specified covariate-adjusted Cox (`adj HR = 0.32`, `95% CI 0.14–0.73`, `p = 0.007`) and `BioVendor ELISA` `CSF pNfH 750–3,700 pg/mL` stratum (`n = 154`, `HR = 0.52`, `95% CI 0.30–0.89`, `p = 0.016`; `<750 pg/mL` LLOQ `n = 20` had `0` deaths; `~79%` of `N = 220 <= 3,700 pg/mL` vs null unadjusted ITT `HR = 0.81, p = 0.33`). Trautwig 2025 living CSF (`PMC12082929`, `n = 77` DIA, `n = 51` nested Emory TMT subset) shows tryptic MS total `NEFL` correlates weakly with total `NEFH` (`r = 0.278`; `75%` DIA / `60%` TMT `p80` discordance, uncalibrated to `BioVendor` `pNfH` ELISA), motivating Stage-0 paired `BioVendor`-to-CLIA `pNfH` & `NfL` immunoassay calibration; event-driven Phase 3 (`247` deaths at conservative `HR = 0.70` requiring `N ~ 650–750` over `36–42 mo` follow-up due to slow-progressor event rates; sensitivity `138` events at `HR = 0.62` `[MODEL_PRIOR]`) mandates analytical `BioVendor`-to-`Ella`/`Euroimmun`/`Simoa` CLIA bridging for lumbar `CSF pNfH <= 3,700 pg/mL` enrichment (active `ALSTARS NCT07161999` omits this gate) plus longitudinal `FOXP3` TSDR Treg demethylation and `CD56bright` NK / serum `sCD25` cellular-sink monitoring.",
        f"4. **`#7 DN-01` `ATG4B`, `#8 DN-04` `CELF5` (`TIER_2_FOCUSED_GATE_FIRST`), & `#9 DN-05` `PRUNE2` (`#1` of `TIER_3_EXPLORATORY_DISCOVERY`):** "
        f"`ATG4B` promotes off-target-cleaner `#2 chr2:241668970-241668987(+)` (`CAUTION`, `sp1=0, pm1_50=0, pm2_25=2` vs `#1 chr2:241668981-241668998(+)` `sp1=2, pm1_50=1, pm2_25=18`), pairing `Spillman` `C9-FTD` homogenate DIA protein loss (`-0.4905, p = 0.0227`, indirect `C9-FTD` proxy while synaptosomal `ATG4B` is unchanged and paralogs `ATG4A/C/D` require graded `30%/60%/90%` TDP-43-CRISPRi checks), `PDB 2Z0D` `Glu319` catalytic/LIR truncation (`27` `LC3B` contacts), and `NYGC` cervical loss (`beta = {pan['ATG4B']['Spinal_Cord_Cervical']['adj_beta_tdp_vs_ctrl']}, p = {pan['ATG4B']['Spinal_Cord_Cervical']['adj_p_tdp_vs_ctrl']:.4f}`, neuronal-mass-residualized `tSTMN2` tail `{pan['ATG4B']['Spinal_Cord_Cervical']['mn_adj_neuronal_tail_pct']}%`, small `n=9` `ALS-SOD1/FUS adj_p = {pan['ATG4B']['Spinal_Cord_Cervical']['adj_p_tdp_vs_sod1fus']:.4f}` underpowered for equivalence). "
        f"`CELF5` (`#1 chr19:3278299-3278318(+)`, `PASS_CLEAN_GE2MM`) replicates across `Brown` `108-bp` (`mod3=0`, PTC codon `30/36`, `98-bp` upstream micro-intron) `LeafCutter clu_25763_+` CE (`FDR = 2.83e-22`), `Bye 2025` sALS patient iPSC-MNs (`padj = 0.00904`), `Pineda BA4_Exc` (`-0.7684, nominal p = 0.0133, FDR = 0.136`), and `NYGC` cervical cord (`RIN+GC beta = {ny_c['adj_beta_tdp_vs_ctrl']}, p = {ny_c['adj_p_tdp_vs_ctrl']:.4f}`; `ALS-Ox beta = {ny_c['oneill_motor_subtypes']['ALS-Ox']['adj_beta_vs_ctrl']}, p = {ny_c['oneill_motor_subtypes']['ALS-Ox']['adj_p_vs_ctrl']:.4f}`, vs reactive-glia-masked bulk lumbar `{ny_l['adj_beta_tdp_vs_ctrl']:+.4f}, p = {ny_l['adj_p_tdp_vs_ctrl']:.4f}` & motor cortex `{ny_m['adj_beta_tdp_vs_ctrl']:+.4f}, p = {ny_m['adj_p_tdp_vs_ctrl']:.4f}`, and small `n=9` `ALS-SOD1/FUS` `adj_p = {ny_c['adj_p_tdp_vs_sod1fus']:.4f}` underpowered for equivalence), exhibiting the **sharpest neuronal-mass-residualized `mn_neur_z` `tSTMN2` coupling in the `9`-gene panel** (`{ny_c['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}%` cervical `p = {ny_c['within_tdp_mn_adj_log2_tSTMN2_p']:.2e}`; `{ny_l['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}%` lumbar `p = {ny_l['within_tdp_mn_adj_log2_tSTMN2_p']:.2e}`), strong CNS restriction (`GTEx v8 Cerebellum = {gl['max_cns_gtex_tpm']:.2f}`, `BA9 = {gl['gtex_cns_ba9_tpm']:.2f}`, `Cervical = {gl['gtex_cns_spinal_cervical_tpm']:.2f}` vs max non-CNS `Testis = {gl['max_non_cns_gtex_tpm']:.2f} TPM`, `{gl['cns_enrichment_ratio_ba9_vs_max_non_cns']}x` `BA9` enrichment), `DepMap` non-essentiality (`Chronos = {gl['depmap_median_chronos']}`), and `gnomAD v4.1 pLI = {gl['gnomad_v41_pli']:.2f}` / `LOEUF = {gl['gnomad_v41_loeuf']}` — mandating **full-length Exon 4–Exon 7 RT-PCR + Oxford Nanopore amplicon sequencing** to verify `<1–2% LOQ` canonical Exon-5 (`chr19:3278031-3278110(+)`) skipping AND `<1–2% LOQ` **`98-bp` upstream micro-intron retention (`98 mod 3 = 2` frameshift)** or latent `5'SS` shunting. "
        f"Removing coordinate-convenience tiebreaking elevates **`#9 DN-05` `PRUNE2`** (`Zhang 2026` `55-um` multicellular Visium spot-level DE across `N=18` donors `-1.2260, BH = 0.01885` + `Spillman` synaptosome `-0.4943, p = 0.00681`) to **`#1` of `TIER_3`** (ahead of `KALRN`/`PFKP`), co-embedding `PRUNE2` Exon-flanking Nanopore RT-PCR directly into the **`ChAT + nuclear TDP-43 + duplex BaseScope` ISH gate across Stage-(ii) partially nuclear-TDP-43-depleted / pre-inclusion cervical (`C3–C8`) lamina IX alpha-MNs** (`<18–24 mo` short-duration sALS vs `SOD1/FUS`-ALS negative-TDP controls, bypassing `69.7%/70.4%` end-stage cord attrition and glial shifts on `PFKP` `+{pan['PFKP']['Spinal_Cord_Cervical']['adj_beta_tdp_vs_ctrl']}` / `DLGAP1` `+{pan['DLGAP1']['Spinal_Cord_Lumbar']['adj_beta_tdp_vs_ctrl']}`).",
        "5. **`#24 C019` Baricitinib / Selective `JAK1 JH1` (`TIER_3_EXPLORATORY_DISCOVERY`, `TRL_5`, `5` hurdles — Demoted from Upstream Core to Tier 3 Watchlist):** Deconfounded `rs3831317`-neutral `5`-protein CSF Glial Bridge achieves `Emory` single-center OOF `AUC = 0.8188` (`p = 6.40e-8`) and `MGH`-offset-adjusted external `AUC = 0.885` (`p = 4.88e-11`, correcting `-0.5034 z` `MGH` Control drift; cross-sectional `Symptomatic-vs-Asymptomatic C9` enrichment), but is placed in `TIER_3` across `5` hurdles: `3.80 nM` CSF (`modeled ~8.7%` cellular pSTAT occupancy vs. `2,500 nM` screen; `657x` gap), `NADALS` `1/9` PE SAE + `1/9` DVT (`N = 9`), the **`JAK1`-vs-autonomous-neuronal-`JAK2` APA catch-22** (`JAK2`-sparing `JAK1` inhibitors forfeit TDP-43-induced neuronal `JAK2` 3'-UTR shortening `dPAS = -0.4391, padj = 2.96e-61` in glia-free sALS iPSC-MNs), bridged `pg/mL` immunoassay calibration, and unproven `CSF pSTAT3/CXCL10` interaction PD.",
        "",
        "## 3. Complete `59`-Candidate Unified Portfolio Ledger (`Ranks #1–#59`)",
        "",
        "| Act (`Bio`) | ID | Origin (`Subcohort`) | Track | Gene / Drug | Decision (`Epistemic State`) | Scientific Tier | `TRL` | Hurdles | Lead `GRCh38` Interval (`Safety`) |",
        "| :---: | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- |",
    ])
    for r in port_rows:
        pid = r["portfolio_id"]
        brk = bio_rk_map[pid]
        link = (
            f"[{pid}](file:///{ROOT_POSIX}/reports/candidates/{pid}.md)"
            if r["origin_phase"] == "EXPLORE_INHERITED_40"
            else f"[{pid}](file:///{ROOT_POSIX}/reports/phase3/PHASE3B_DENOVO_UNBIASED_DISCOVERY.md)"
        )
        iv_disp = f"`{r['lead_cis_interval_id']}` (`{r['lead_offtarget_safety_status']}`)" if r["lead_cis_interval_id"] != "NONE" else "`NONE`"
        lines.append(
            f"| `#{r['unified_rank']}` (`#{brk}`) | **{link}** | `{r['origin_phase']}` (`{r['origin_subcohort']}`) | `{r['track']}` | "
            f"{r['gene_or_drug']} | **`{r['decision']}`** (`{r['epistemic_state']}`) | `{r['scientific_actionability_tier']}` | "
            f"`{r['clinical_readiness_trl']}` | `{r['unsolved_hurdle_count']}` | {iv_disp} |"
        )

    lines.extend([
        "",
        "## 4. Multi-Gene Composite Unbundling Ledger (`19` Sub-Nodes Across `C014`, `C015`, `C017`, `C018`)",
        "",
        "*Governance Container Note:* Parent ID `C015` is retained in Phase 3A/4 portfolio ledgers as a legacy foreign-key container whose active exploratory hypothesis is narrowed to lead sub-node **`C015-N3` (`YKT6` Longin-groove prenyl stabilization)** alongside `14q12` locus probes `C015-N1` (`SCFD1`) and `C015-N2` (`G2E3`, excluded from 3-plex SSO), while `5/8` composite members (`C015-N4 SEC22B`, `C015-N5 STX5`, `C015-N6 GOSR1`, `C015-N7 NSF`, `C015-N8 GDI2`) are dropped.",
        "",
        "| Sub-Node | Parent | Gene | Molecular Role | Human Constraint & Essentiality (`gnomAD v4` / `DepMap`) | Unbundled `CarbonALS` Verdict |",
        "| :--- | :---: | :--- | :--- | :--- | :--- |",
    ])
    for s in sub_rows:
        v_short = s["subnode_verdict"].split(":")[0].strip()
        gn_short = s["gnomad_essentiality_check"].split(";")[0] + "; " + (s["gnomad_essentiality_check"].split(";")[1].strip() if ";" in s["gnomad_essentiality_check"] else "")
        lines.append(f"| `{s['subnode_id']}` | `{s['parent_carbon_id']}` | **`{s['gene_symbol']}`** | {s['molecular_role']} | {gn_short} | **`{v_short}`** |")

    lines.extend([
        "",
        "## 5. Unified Coordinate-Only `GRCh38` Cis-Regulatory Ledger (`26` Search Windows, `0` Chemically Modified Synthesis-Ready ASO Sequences)",
        "",
        "*Off-Target Column & Search-Window Anchor Key:* All `26` `GRCh38` coordinates define sequence-clean **Coordinate-Only Cis-Regulatory Search Windows** (`0` chemically modified synthesis-ready ASO sequences; biosecurity guardrail) requiring empirical `1-nt` cellular microwalks and human iPSC-neuron spontaneous `Ca2+`-oscillation, `TLR9`, and primary `DRG` counter-screens (`GENCODE v46` reference alignment cleanliness does not exclude sequence-specific phosphorothioate protein-binding toxicity, and `AlphaGenome AVI` scores DNA-variant conservation/splicing impact rather than steric `2'-MOE` potency; nuclear `RNase-H1` gapmer deployment is retired on `DN-08 ELK1` `#1/#2` in favor of steric distal-PAS blockade due to nascent Pol II readthrough cleavage risk, `PMID:31924448`, though the upstream Phase 3B column preserves historical label `CRYPTIC_3EXT_ISOFORM_GAPMER_WINDOW` for SHA-12 provenance). `sp0/sp1/wob` = spliced exonic `0-mm` / `1-mm` / `G:U`-wobble-only protein-coding genes (`GENCODE v46`). `pm0/1_50/wob/2_25/blg/s18` = nascent pre-mRNA `0-mm` sense / `1-mm <=50 bp` splice / wobble-only `<=50 bp` splice / `2-mm <=25 bp` splice / `1-nt` bulge steric / `18-bp` sub-core steric protein-coding genes (`GGGenome hg38`). `PASS_CLEAN_GE2MM` requires `0` hits across `sp0`, `sp1`, `wob`, `pm0`, `pm1_50`, `wob_50`, `blg`, and `s18` plus `0` constrained neuronal (`pLI >= 0.9`) flags (Phase 3B single-entity scans additionally gated `pm2_25 == 0`, conservatively labeling `DN-01 #2` `pm2_25=2` and `DN-09 #1` `pm2_25=3` as `CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED`); any `1-mm` or wobble hit on non-constrained genes triggers `CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED`.",
        "",
        "| `#` | ID (`Gene #Rk`) | Lead? | `1`-Based `GRCh38` Interval | Len | Mode | `Tm_phys` (°C) | `max_AVI` | `sp0/sp1/wob` | `pm0/1_50/wob/2_25/blg/s18` | Constrained CNS Flags | Off-Target Safety Status | Atlas |",
        "| :---: | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- | :---: |",
    ])
    for c in cis_rows:
        lead_tag = "**YES**" if c["is_promoted_lead"] == "True" else "No"
        fl = c["flagged_constrained_neuronal_hits"]
        fl_short = fl if len(fl) <= 68 else fl[:65] + "..."
        a_link = f"[Atlas]({atlas_url(c['chrom'], c['grch38_start'], c['grch38_end'])})"
        lines.append(
            f"| `{c['unified_interval_order']}` | `{c['subnode_or_cand_id']}` (`{c['gene_symbol']}` #{c['rank_within_gene']}) | {lead_tag} | "
            f"`{c['interval_id']}` | `{c['length_bp']}` | `{c['cis_mechanism_or_mode']}` | `{c['tm_phys_pops_c']}` | `{c['max_avi_phred']}` | "
            f"`{c['spliced_0mm_genes']}/{c['spliced_1mm_genes']}/{c['spliced_wobble_only_pc_genes']}` | "
            f"`{c['premRNA_0mm_sense_genes']}/{c['premRNA_1mm_splice50bp_genes']}/{c['premRNA_wobble_only_splice50bp_pc_genes']}/{c['premRNA_2mm_splice25bp_pc_genes']}/{c['bulge_1nt_steric_pc_genes']}/{c['sub18_core_steric_pc_genes']}` | "
            f"`{fl_short}` | **`{c['offtarget_safety_status']}`** | {a_link} |"
        )
    return lines
