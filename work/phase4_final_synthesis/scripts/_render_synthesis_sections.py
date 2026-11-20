"""Programmatic Markdown section builders for reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from _candidate_contrasts_b import KEY_MECHANISTIC_CONTRASTS_9
from _phase4_helpers import biological_evidence_sort_key
from carbon_als.accessions import legacy_to_accession, translate_legacy_tokens_in_prose

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
        f"[phase4_unified_portfolio.csv](file:///{ROOT_POSIX}/registries/phase4_unified_portfolio.csv) (`52` hypotheses), "
        f"[phase4_unified_cis_intervals.csv](file:///{ROOT_POSIX}/registries/phase4_unified_cis_intervals.csv) (`26` `GRCh38` Coordinate-Only Cis-Regulatory Search Windows, `0` chemically modified synthesis-ready ASO sequences), and "
        f"[subnode_dissection.csv](file:///{ROOT_POSIX}/registries/subnode_dissection.csv) (`18` subunit/comparator dissections). "
        f"Synthesizes Phase 1 ([PHASE1_PORTFOLIO_ADJUDICATION_REPORT.md](file:///{ROOT_POSIX}/reports/PHASE1_PORTFOLIO_ADJUDICATION_REPORT.md)), "
        f"Phase 2 ([CARBON_ALS_PHASE2_MASTER_PORTFOLIO_SYNTHESIS.md](file:///{ROOT_POSIX}/reports/CARBON_ALS_PHASE2_MASTER_PORTFOLIO_SYNTHESIS.md)), "
        f"Phase 3A ([PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md](file:///{ROOT_POSIX}/reports/phase3/PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md)), and "
        f"Phase 3B ([PHASE3B_DENOVO_UNBIASED_DISCOVERY.md](file:///{ROOT_POSIX}/reports/phase3/PHASE3B_DENOVO_UNBIASED_DISCOVERY.md)).",
        "",
        "## 1. Executive Summary & Portfolio Partition",
        "",
        "Across four staged computational and clinical-archaeology phases (`50` reproducible runs in `registries/analysis_runs.csv` across `42` SHA-256-locked open-access resources [`40` external accessions + `2` repo-bundled reference maps]), `ExploreALS v1.2` evaluates `33` published clinical, genetic, and neuropathological ALS programs (`C001–C024`, `S01–S09`), `18` complex/panel subunits and selectivity comparators, and `19` systematic multi-omic screen nominations (`DN-01–DN-19`) (**`52` unified hypotheses total**):",
        "",
        "| Scientific Actionability & Decision Partition | Curated Clinical & Genetic (`33`) | Multi-Omic Screen (`19`) | Unified Total (`52`) | Epistemic State & Governance Rule |",
        "| :--- | :---: | :---: | :---: | :--- |",
        f"| **`TIER_1_ACTIONABLE_NOW`** (`1 KEEP_CORE` + `1 KEEP_EXPLORATORY`) | `{ox['CURATED_CLINICAL_33'].get('TIER_1_ACTIONABLE_NOW', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('TIER_1_ACTIONABLE_NOW', 0)}` | **`{ce['TIER_1_ACTIONABLE_NOW']}`** | `KEEP_CORE`-first execution (`#1 S06`) + `TRL_6` BioVendor-bridged-pNfH Ph3 (`#2 S07`) |",
        f"| **`TIER_2_FOCUSED_GATE_FIRST`** (`3 KEEP_CORE` + `3 KEEP_EXPLORATORY`) | `{ox['CURATED_CLINICAL_33'].get('TIER_2_FOCUSED_GATE_FIRST', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('TIER_2_FOCUSED_GATE_FIRST', 0)}` | **`{ce['TIER_2_FOCUSED_GATE_FIRST']}`** | Focused preclinical/PD/IND gate before clinical commitment (`#3 C001`, `#4 C006`, `#5 C002`, `#6 C007`, `#7 DN-01`, `#8 DN-04`) |",
        f"| **`TIER_3_EXPLORATORY_DISCOVERY`** (`{ce['TIER_3_EXPLORATORY_DISCOVERY']} KEEP_EXPLORATORY`) | `{ox['CURATED_CLINICAL_33'].get('TIER_3_EXPLORATORY_DISCOVERY', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('TIER_3_EXPLORATORY_DISCOVERY', 0)}` | **`{ce['TIER_3_EXPLORATORY_DISCOVERY']}`** | Retained under Epistemic Asymmetry (`UNPROVEN_UNTESTED`); **preclinical discovery triage queue only** — not therapeutic endorsement |",
        f"| **`COMPANION_PROTOCOL_ONLY`** (`1 KEEP_EXPLORATORY`) | `{ox['CURATED_CLINICAL_33'].get('COMPANION_PROTOCOL_ONLY', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('COMPANION_PROTOCOL_ONLY', 0)}` | **`{ce['COMPANION_PROTOCOL_ONLY']}`** | `C005` TMS SICI/SDTC + living-CSF `NPTX2` stage-gating protocol for `C006` (never a drug bundle) |",
        f"| **`BIOMARKER_BENCHMARK_ONLY`** (`7 RECLASSIFY`) | `{ox['CURATED_CLINICAL_33'].get('BIOMARKER_BENCHMARK_ONLY', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('BIOMARKER_BENCHMARK_ONLY', 0)}` | **`{ce['BIOMARKER_BENCHMARK_ONLY']}`** | `ESTABLISHED_BENCHMARK` (`C013`, `S08`, `C003`, `C017`, `DN-10..12`: SOC / PD / fluid staging panels) |",
        f"| **`DROPPED_FALSIFIED_EXCLUDED`** (`{ce['DROPPED_FALSIFIED_EXCLUDED']} DROP`) | `{ox['CURATED_CLINICAL_33'].get('DROPPED_FALSIFIED_EXCLUDED', 0)}` | `{ox['PHASE3B_DENOVO_19'].get('DROPPED_FALSIFIED_EXCLUDED', 0)}` | **`{ce['DROPPED_FALSIFIED_EXCLUDED']}`** | Positive counterevidence only: `{cp.get('FALSIFIED_CLINICAL', 0)}` clinical + `{cp.get('FALSIFIED_PK_SAFETY', 0)}` PK/safety + `{cp.get('ARTIFACT_CONFOUNDED', 0)}` artifact |",
        f"| **Total** | **`33`** | **`19`** | **`52`** | **`{cd['KEEP_CORE']}` `KEEP_CORE` · `{cd['KEEP_EXPLORATORY_UNPROVEN']}` `KEEP_EXPLORATORY` · `{cd['RECLASSIFY_BENCHMARK_OR_BIOMARKER']}` `BENCHMARK` · `{cd['DROP']}` `DROP`** |",
        "",
        "### 1.1 Curated Clinical & Genetic Tier Breakdown (`33` Programs)",
        "",
        "| Curated Program Group (`33` Items) | `KEEP_CORE` | `KEEP_EXPLORATORY` | `BENCHMARK` | `DROP` | Key Scientific Adjudication |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |",
    ]
    notes = {
        "Tier_1_White_Space_Core": "`C013` -> SOC benchmark; `C019` (`5`-hurdle `JAK1/JAK2` catch-22 + `657x` CSF gap), `C015` (`chr14q12` `SCFD1/G2E3`), `C023` (`YKT6` `p.Tyr64Cys`) & `C016` (glial iron) -> `TIER_3`",
        "Tier_2_Crowded_Clinical_Benchmarks_And_Combinatorial_Anchors": "`C001` (`UNC13A #2`) & `C002` (`STMN2 #2`) retained as `KEEP_CORE` (`TIER_2` Stage 2 multiplex anchors; standalone 1-plex crowded)",
        "Tier_3_Subtype_Restricted_Class_Caution_Or_Safety_Hold": "`C017` -> CSF staging biomarker (`rs3831317` KO null, `GPNMB` protective); `C018` (`C1q` IT watchlist) & `C020` (pulsed PIKfyve) -> `TIER_3`; `C021` -> `DROP`",
        "Tier_4_Exploratory_Mechanistic_Comparators": "`C006` (`KCNQ2` exon-5 SSO) -> `KEEP_CORE` (`TIER_2` #4); `C007` (`TIER_2`), `C022` (`DNAJB2` Mendelian chaperone, `TIER_3`), `C014` (`TIER_3`), `C005` (companion); `C010` (`Ropinirole`) -> `DROP`",
        "Tier_5_Parked_Negative_Or_Exposure_Benchmarks": "`C003` (`Ezogabine`) -> TMS SICI PD calibrator; `C004`, `C008`, `C009`, `C011`, `C012`, `C024` (`Pegcetacoplan` MERIDIAN) confirmed `DROP`",
        "Unadopted_Screen_Or_Blind_Survivor": "`S06` (`SARM1` non-orthosteric T-lock) -> `KEEP_CORE` (`TIER_1` #1); `S07` (`Aldesleukin` low-pNfH) -> `TIER_1` (#2); `S09` (`Censavudine`) & `S02` (`CuATSM` `NCT04082832` unreported) -> `TIER_3`; `S08` -> SOC benchmark; `4` `DROP`",
    }
    for et in (
        "Tier_1_White_Space_Core",
        "Tier_2_Crowded_Clinical_Benchmarks_And_Combinatorial_Anchors",
        "Tier_3_Subtype_Restricted_Class_Caution_Or_Safety_Hold",
        "Tier_4_Exploratory_Mechanistic_Comparators",
        "Tier_5_Parked_Negative_Or_Exposure_Benchmarks",
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
            f"| {', '.join(f'**`{legacy_to_accession(str(x))}`**' for x in row['ids'])} | **{row['domain']}** | {row['naive']} | {row['finding']} | {row['gate']} |"
            for row in KEY_MECHANISTIC_CONTRASTS_9
        ],
    ])
    return [translate_legacy_tokens_in_prose(ln) for ln in lines]


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
        "## 2. Top-8 Translational Execution Roadmaps (`TIER_1` `#1–#2` & `TIER_2` `#3–#8`)",
        "",
        "All `8` `TIER_1` + `TIER_2` programs separate **`[MEASURED]`** primary empirical evidence from **`[MODEL_PRIOR]`** order-of-magnitude structural/thermodynamic/ODE assumptions (`COARSE_PRIOR_ONLY`), order `TIER_1` by **`KEEP_CORE` causal certainty first** (`#1 S06` ahead of highest-`TRL` `KEEP_EXPLORATORY_UNPROVEN` `#2 S07`), place `C006 KCNQ2` in `TIER_2` (`#4`) alongside `#3 C001` and `#5 C002` until wet-lab Intron-5 `ISS`-vs-`ISE` microwalks prove Exon-5 inclusion, enforce `ICH M3(R2)` / `21 CFR 312.23(b)` sponsor-owned single-entity GLP intrathecal tox/PD before Stage 2 `21 CFR 300.50` genotype-stratified `2`-plex (`KCNQ2 + STMN2 #2`) vs `3`-plex (`+ UNC13A #2`) contribution testing across `rs12973192`/`rs12608932` genotypes, and enumerate atomic unsolved hurdles:",
        "",
        "| Act (`Bio`) | ID & Program | Origin | Decision (`State`) | Specific Modality & Lead `GRCh38` Interval | `TRL` & Experimental Gate | `[MODEL_PRIOR]` Dependency | Hurdles |",
        "| :---: | :--- | :---: | :--- | :--- | :--- | :--- | :---: |",
    ]
    for r in port_rows[:8]:
        brk = bio_rk_map[r["portfolio_id"]]
        acc_id = r.get("accession_id") or legacy_to_accession(r["portfolio_id"])
        lines.append(
            f"| `#{r['unified_rank']}` (`#{brk}`) | **`{acc_id}`** ({r['gene_or_drug']}) | `{r['origin_phase']}` | **`{r['decision']}`** (`{r['epistemic_state']}`) | "
            f"`{r['primary_modality_specific']}` (Lead: `{r['lead_cis_interval_id']}` `{r['lead_offtarget_safety_status']}`) | "
            f"`{r['clinical_readiness_trl']}` · `{r['next_gate_experimental_class']}` | `{r['model_prior_dependency']}` | **`{r['unsolved_hurdle_count']}`** |"
        )

    lines.extend([
        "",
        "### 2.1 Execution Highlights & Kill-Gates for `TIER_1` (`#1–#2`), `TIER_2` Splice & De Novo Leads (`#3–#8`), Top `TIER_3` (`#9 DN-05`), and Watchlist Case Study (`#24 C019`)",
        "",
        "1. **`#1 S06` `SARM1` Non-Covalent `ARM–TIR` T-Lock (`TIER_1_ACTIONABLE_NOW`, `KEEP_CORE`, `TRL_4`, `2` hurdles):** `[MEASURED]` Cryo-EM `PDB 9TZY` (`PMID:42156967`) and `122`-scaffold profiling (`PMID:42380237`) prove orthosteric `BEXi` adduct-`17` prodrugs (`LY3873862`: completed HV `NCT05492201` `N = 84`, ALS `NCT07883590` Ph1 Not Yet Recruiting; `DSRM-3716`) bridge `3` `TIR` chains (`122/122` sub-`IC50` activation across `7` series with median `8.6-fold` [`IQR 5.1–9.7`] `IC50/C_act` concentration separation; `[MODEL_PRIOR]` `~2.8x` illustrative low-reserve MWC washout scenario) at trough washout, full-length autoinhibited `PDB 7ANW` (`2.68 Å`)/`7DJT` (`2.80 Å`) octamers resolve inter-protomer `ARM(A)–TIR(H)` salt-bridge contacts (`3.07–5.47 Å` vs `37.8–65.4 Å` intra-chain; Class II `Cys311`-wall deformers `p.L223P`/`del226-232`/`p.R267W` near `Arg224`/`Glu264`; `0/12` single-gene `SARM1` `ClinVar` P/LP with `6` opposite-strand `3' SLC46A1` records), and clinical `SARM1` testing now spans three Ph1/2 programs including reversible orthosteric `NB-4746` (`NCT07369076`) and Sironax's undisclosed oral allosteric inhibitor **`SIR2501`** (`CTR20253552` China ALS Ph1b/2a, `NCT07765446` US CIPN Ph2 `n = 18`, `ANZCTR 387449` HV `N = 82` up to `600 mg`/`150 mg QD`, `ASCO 10.1200/JCO.2026.44.16_suppl.12148`, `SfN 2026 Session PSTR091` `15 Nov 2026` unreviewed congress poster; `WO2024125624A1`/`WO2024222835A1`/`WO2026086928A1`). Because undisclosed `SIR2501` could be either a chronic thiol-reactive `Cys311` electrophile (`PDB 7DJT` class, `PMID:33944777`) or a reversible `ARM`/`ARM–TIR` lock (`ASHA-624` class) — and healthy-volunteer circulating plasma `cADPR` (`ASCO #12148`) is estimated at `>90–95%` ecto-`CD38`/`BST1`-generated (`[MODEL_PRIOR]`, extrapolated from murine `Cd38`/`Sarm1` KO `PMID:32087251`; `PMID:16750163`, capping `90%` selective `SARM1` blockade at `~5–10%` cell-free fluid drop so a `-50%` plasma drop implies `~45–50%` off-target `CD38` blockade) while CIPN DRGs lie outside the BBB — this synthesis prioritizes `Cys311Ala`-verified reversible non-covalent inter-protomer (intra-octamer) `ARM–TIR` T-locks (`ASHA-624` class; spanning the **`1.0x` parallel microtubule-remodeling Bliss lower bound** [`10.64898/2026.11.07.764673` `[PREPRINT]`, `PMID:35767949`] to **`~2–7x` [`med ~3x`] `NMNAT2`-epistatic MWC upper bound** `[MODEL_PRIOR]` in `SARM1` T-lock +/- `STMN2` SSO washout curves), excludes `<0.1%` (`~0.076%` in `gnomAD v4.1`, `PMID:34796871`/`PMID:34991663`, vs benign `P332Q` `AF = 0.986%`, `97` homozygotes) constitutive `ARM`-broken GoF carriers via sequencing (`35.95%` [`~30–40%`] Binomial hetero-octamer residual NADase ceiling at `100x Kd` under `d_lock = 6.5` `[MODEL_PRIOR]`), and deploys enzymatic `CD38` counter-screening plus a `3`-layer per-target PK/TE/PD panel: unbound CSF $C_{\\text{trough},u} \\ge \\text{IC}_{80}$ ($K_{p,\\text{uu}} \\ge 0.30$), neuron-derived EV (`L1CAM`/`ATP1A3+`) `cADPR:NAD+` + `SCG10/STMN2` target-engagement rescue, and zero washout `CSF pNfH`/`NfL` spike.",
        "2. **`#2 S07` Low-Dose Aldesleukin (`TIER_1_ACTIONABLE_NOW`, `KEEP_EXPLORATORY_UNPROVEN`, `TRL_6`, `2` hurdles — Highest Clinical Proximity in Portfolio):** `[MEASURED]` MIROCALS (`NCT03039673`, `PMID:40354799`, `N = 220`, `90` deaths; unadjusted ITT `HR = 0.81, p = 0.33`) SAP pre-specified covariate-adjusted Cox (`adj HR = 0.32`, `95% CI 0.14–0.73`, `p = 0.0070`; continuous interaction `HR = 1.0003/pg/mL`, `p = 0.0011`; secondary `ALSFRS-R` slope interaction `F = 3.95, p = 0.048`; sustained Day-112 trough Treg expansion `p < 0.0001` & plasma `CCL2` `p < 0.05` vs Day-8/120 `p < 0.0001`, CSF `CCL2`/`pNfH` null) and `BioVendor ELISA` `CSF pNfH 750–3,700 pg/mL` stratum (`n = 154`, `57` deaths, `HR = 0.52`, `95% CI 0.30–0.89`, `p = 0.016`; `<750 pg/mL` LLOQ `n = 19` had `0` deaths; visually defined `<=3,700 pg/mL` baseline-distribution cutpoint [`mmc1.pdf` p. 13/23] `n = 173/220` [`78.6%` post-run-in LP; `173/304` = `56.9%` initial screen] `HR = 0.57`, `p = 0.037` vs `>3,700 pg/mL` `n = 47` [`33/90` deaths] `HR = 1.37, p = 0.38`). Inside `MIROCALS` (`N = 220`), `Al Khleifat et al. 2026` (`PMID:42836993`, `PMC13642438`, *J Neurol* `273:643`) showed clinical `TRICALS` risk shares only `r² = 12.7%` (`r = 0.357`) of variance with `CSF pNfH` and contributes less interaction fit (`Δχ² = 4.76`, LRT `p = 0.029` / Wald `p = 0.025` vs `Δχ² = 14.24` for `pNfH x trt`; adding `pNfH` to `TRICALS` `Δχ² = 44.39`; combined model reference `HR = 0.28, p = 0.002`), while commercial `pNfH` immunoassays span `~1.8x–4.5x` inter-platform `pg/mL` offsets (`PMID:31251725`, `PMID:29054919`; where hypothetical unbridged `1.8x–4.5x` lower `CSF` cutoffs admit `74–99%` of `>3,700 pg/mL` patients and reduce `247`-death two-sided superiority power from `80%` to `~43–50%` at `HR_high = 1.00` or `~14–23%` at `HR_high = 1.37` `[MODEL_PRIOR]`) and bottom-up tryptic CSF MS (`r = 0.278` across `n = 77` DIA / `n = 51` overlapping Emory TMT in `Trautwig 2025` `PMC12082929`) reflects KSP phosphorylation vs clinical immunoassays (`rho = 0.64–0.71` `PMID:38683209`; serum `NfL` > serum `pNfH` on `ALSFRS-R` slope `PMID:32385188`). Event-driven Phase 3 (`247` deaths at conservative unadjusted `HR = 0.70`, `80%` two-sided superiority power with critical `HR_crit = 0.779` vs `50%` probability of `HR_hat <= 0.70` at true `HR = 0.70`; `138` deaths at `HR = 0.62` `[MODEL_PRIOR]`; `N ~ 724` over `36–42 mo` follow-up) mandates `CLSI EP09c` (`N >= 40`) Passing-Bablok bridging to `MIROCALS`'s `~79th BioVendor percentile` (noting enrolled `N = 137` Phase 2/3 `ALSTARS NCT07161999` stratifies `3` serum `NfL` tiers on `24`-wk `ALSFRS-R` with dual `rhIL-2 + CTLA4-Ig` and no single-agent `IL-2` arm) plus longitudinal `FOXP3` TSDR Treg demethylation and `CD56bright` NK / serum `sCD25` monitoring.",
        "3. **`#4 C006` `KCNQ2` Exon-5 Steric SSO (`TIER_2_FOCUSED_GATE_FIRST`, `KEEP_CORE`, `TRL_3`, `3` hurdles — Clinically Uncrowded Splice-SSO Lead Alongside `#3 C001` & `#5 C002`):** Uncrowded (`NCT = 0` for `KCNQ2` splice SSOs) Stage 1 single-entity intrathecal `2'-O-MOE` mixed-`PO/PS` `5-MeC` dense (`>=50`-oligo `18–22 nt` `1-nt`) Intron-4/Exon-5/Intron-5 exon-inclusion microwalk anchored on off-target-clean `#3 chr20:63442302-63442319(-)` (`UG = 1`, `modeled Tm ~53 °C [MODEL_PRIOR]`, `0/18` splicing `AVI` = `Cactus/DNase` conservation; `[MODEL_PRIOR]` one-sided WT-context `AlphaGenome` `63442302:C>G` predicts `+35.2%` [`+0.1930`] Exon 4–6 skipping vs `#2` Intron-4 `UG` `-0.0522`, directly testing putative Intron-5 `ISS` relief vs wrong-sign `ISE` hazard; `CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED`) vs `#1 chr20:63442595-63442616(-)` (gated against **WT TDP-43 *cis*-eviction** from `KCNQ2` Intron-4 `(UG)8` in healthy TDP-43-intact oculomotor neurons, `PV+` cortical interneurons, and lumbar `DRGs`; `#2` deprioritized due to `PTCH1` `1-nt` bulge `WARN`), counter-screened against spontaneous human iPSC-neuron `Ca2+`-oscillation, `TLR9`, and primary `DRG` neurotox, benchmarked against `QRL-101` (`PDB 7CR2 Trp236` + `KCNQ2-DeltaE5` ER retention; completed `NCT06714396` positive `SDTC` & `NCT07421778`), and stratified by `C005` (`TMS SICI <= 5.5% RMT` [`PMID:42592079`] + preserved `CSF NPTX2`) plus `ICH M3(R2)` single-entity GLP IT tox and NHP cervical (`C3–C5`) / motor-cortex (`BA4` Betz, checking `<=3 mg` lumbar-to-BA4 rostral dilution) biodistribution before Stage 2 `21 CFR 300.50` **genotype-stratified co-delivery** — comparing `2`-plex (`KCNQ2 #3` + **`#5 C002` `STMN2 #2 chr8:79616829-79616846(+)`**) vs `3`-plex (`+` **`#3 C001` `UNC13A #2 chr19:17642537-17642554(-)`**, where `Brown 2022` `MAJIQ` Intron-31 retention `dPSI = +0.3543, FDR = 1.82e-15` sets a `[MODEL_PRIOR] 46.1–55.6%` raw PSI [`~58.3–61.6%` WT-normalized] Intron-20-only mRNA ceiling under severe TDP-43 KD that still exceeds `Keuss et al. 2026` `PMID:43015463` `>30%` human synaptic rescue orthogonally to `STMN2` & `KCNQ2`) across `rs12973192`/`rs12608932` genotypes, targeting a multiplex polyanion/DRG margin of `EC80 <= 3 mg/strand` (**`6 mg` `2`-plex to `9.0 mg` `3`-plex** `Q8W–Q12W`, calibrated to `QRL-201 ANQUR NCT05633459` `3 mg` `-46%` vs `10 mg` `~5%` Day-197 `CSF pNfH` dissociation while noting single-agent nusinersen `12–50 mg` `PMID:41634391` & tofersen `100 mg` `PMID:36129998` tolerate higher single-ASO IT masses and reclassifying unvalidated `24–48 mg` `3`-plex loads as a radiculotoxicity hazard).",
        f"4. **`#7 DN-01` `ATG4B`, `#8 DN-04` `CELF5` (`TIER_2_FOCUSED_GATE_FIRST`), & `#9 DN-05` `PRUNE2` (`#1` of `TIER_3_EXPLORATORY_DISCOVERY`):** "
        f"`ATG4B` promotes off-target-cleaner `#2 chr2:241668970-241668987(+)` (`CAUTION`, `sp1=0, pm1_50=0, pm2_25=2`, `0` constrained CNS flags, shifted `-10 bp` into the exonic `5'SS` core vs `Torres et al. 2024` `PMID:39305312` unconjugated `16-nt` `6-LNA/15-PS` mixmer `ASO 3J` `chr2:241668980-241668995(+)` [`sp1=10` (`CLN6`/`DOCK3`), `pm0_50=1`, `pm1_50=18`, `5` `pLI>=0.96` flags (`DOCK3`, `SNRNP200`, `PSMA5`, `KHDC4`, `SNU13`), unmeasured heuristic `6-LNA` `Tm ~ 80.1 °C` / `1-mm ~ 74.1 °C` `[MODEL_PRIOR]`] and `#1 chr2:241668981-241668998(+)` `sp1=2, pm1_50=1, pm2_25=18`), pairing `Torres 2024` sporadic ALS spinal cord LC3ylation + HeLa RNAiMAX `ASO 3J` mRNA rescue (bypassing separate systemic IV `25-nt` peptide-PMO `Pip8b2-ATG4B` transient Day-2 mouse urinary `KIM-1` elevation via naked IT `2'-MOE`), `Spillman` `C9-FTD` homogenate DIA protein loss (`-0.4905, nominal p = 0.0227, FDR = 0.148, PMID:42789089`, indirect `C9-FTD` proxy while synaptosomal `ATG4B` is unchanged and paralogs `ATG4A/C/D` require graded `30%/60%/90%` TDP-43-CRISPRi checks), `PDB 2Z0D` `Val319` substrate-patch (`27` `LC3B` contacts) + `Q9Y4P1` `FEIL` LIR truncation, and `NYGC` cervical loss (`beta = {pan['ATG4B']['Spinal_Cord_Cervical']['adj_beta_tdp_vs_ctrl']}, p = {pan['ATG4B']['Spinal_Cord_Cervical']['adj_p_tdp_vs_ctrl']:.4f}`, neuronal-mass-residualized `tSTMN2` tail `{pan['ATG4B']['Spinal_Cord_Cervical']['mn_adj_neuronal_tail_pct']}%`, small `n=9` `ALS-SOD1/FUS adj_p = {pan['ATG4B']['Spinal_Cord_Cervical']['adj_p_tdp_vs_sod1fus']:.4f}` underpowered for equivalence). "
        f"`CELF5` (`#1 chr19:3278299-3278318(+)`, `PASS_CLEAN_GE2MM`) replicates across `Brown` `108-bp` (`mod3=0`, PTC codon `30/36` [`18 nt` `< 50–55 nt` EJC rule `PMID:9671053` upstream of `CE–Exon 6`, so 3-exon minigenes score splice `%PSI` but evade EJC-NMD!] after Exon-5 `Pro201` inside `RRM2` [`AF-Q8N6W0-F1` / `CELF1` homolog `PDB 3NMR` `PMID:20947024`: severing `5` `beta4–beta1` H-bonds & `6/17` projected `UGUU` contacts], `98-bp` upstream micro-intron) `LeafCutter clu_25763_+` CE (`FDR = 2.83e-22`), `Bye 2025` `N=77` sALS patient iPSC-MN cluster `clu_25763_+` (`padj = 0.00904`, `PMID:41286450`, raw BAMs on controlled-access EGA; junction-level RT-PCR required), `Pineda BA4_Exc` (`-0.7684, nominal p = 0.0133, FDR = 0.136`), and `NYGC` cervical cord (`RIN+GC beta = {ny_c['adj_beta_tdp_vs_ctrl']}, p = {ny_c['adj_p_tdp_vs_ctrl']:.4f}`; `ALS-Ox beta = {ny_c['oneill_motor_subtypes']['ALS-Ox']['adj_beta_vs_ctrl']}, p = {ny_c['oneill_motor_subtypes']['ALS-Ox']['adj_p_vs_ctrl']:.4f}`, vs reactive-glia-masked bulk lumbar `{ny_l['adj_beta_tdp_vs_ctrl']:+.4f}, p = {ny_l['adj_p_tdp_vs_ctrl']:.4f}` & motor cortex `{ny_m['adj_beta_tdp_vs_ctrl']:+.4f}, p = {ny_m['adj_p_tdp_vs_ctrl']:.4f}`, and small `n=9` `ALS-SOD1/FUS` `adj_p = {ny_c['adj_p_tdp_vs_sod1fus']:.4f}` underpowered for equivalence), exhibiting the **sharpest neuronal-mass-residualized `mn_neur_z` `tSTMN2` coupling in the `9`-gene panel** (`{ny_c['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}%` cervical `p = {ny_c['within_tdp_mn_adj_log2_tSTMN2_p']:.2e}`; `{ny_l['within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal']}%` lumbar `p = {ny_l['within_tdp_mn_adj_log2_tSTMN2_p']:.2e}`), strong CNS restriction (`GTEx v8 Cerebellum = {gl['max_cns_gtex_tpm']:.2f}`, `BA9 = {gl['gtex_cns_ba9_tpm']:.2f}`, `Cervical = {gl['gtex_cns_spinal_cervical_tpm']:.2f}` vs max non-CNS `Testis = {gl['max_non_cns_gtex_tpm']:.2f} TPM`, `{gl['cns_enrichment_ratio_ba9_vs_max_non_cns']}x` `BA9` enrichment), `DepMap` non-essentiality (`Chronos = {gl['depmap_median_chronos']}`), and `gnomAD v4.1 MANE pLI = 1.00` / `LOEUF = {gl['gnomad_v41_loeuf']}` (`Open Targets / legacy gene constraint LOEUF = 0.216`) — where `Brown 2022` `MOESM11` local LSVs (`3278316-3281199` `dPSI = +0.3471, KD PSI = 0.367`; upstream `3225618-3244124` `novel_acceptor` `dPSI = +0.1218, KD PSI = 0.149`; donor vs acceptor canonical `0.546` vs `0.633`), `Ribo-seq = 38.6%` residual translation (`RNA-seq = 54.1%`), and `Zeng et al. 2025` (`PMID:40672339`, `PMC12265704`) NMD-inhibition proof (`24.8% -> 44.6%`, `FDR = 0.0235`) motivate **endogenous multi-exon Exon 1–Exon 7+ Oxford Nanopore / Iso-Seq phasing** to quantify whole-molecule rescue while verifying `<1–2% LOQ` canonical Exon-5 (`chr19:3278031-3278110(+)`) skipping AND `<=WT` baseline (`~2.8%` vs `18.2%` TDP-43 KD) **`98-bp` upstream micro-intron retention (`98 mod 3 = 2` frameshift)**. "
        f"Removing coordinate-convenience tiebreaking elevates **`#9 DN-05` `PRUNE2`** (`Zhang 2026` `55-um` multicellular Visium spot-level DE across `N=18` donors `-1.2260, BH = 0.01885` + `Spillman` synaptosome `-0.4943, p = 0.00681`) to **`#1` of `TIER_3`** (ahead of `KALRN`/`PFKP`), co-embedding `PRUNE2` Exon-flanking Nanopore RT-PCR directly into the **`ChAT + nuclear TDP-43 + duplex BaseScope` ISH gate across Stage-(ii) partially nuclear-TDP-43-depleted / pre-inclusion cervical (`C3–C8`) lamina IX alpha-MNs** (`<18–24 mo` short-duration sALS vs `SOD1/FUS`-ALS negative-TDP controls, bypassing `69.7%/70.4%` end-stage cord attrition and glial shifts on `PFKP` `+{pan['PFKP']['Spinal_Cord_Cervical']['adj_beta_tdp_vs_ctrl']}` / `DLGAP1` `+{pan['DLGAP1']['Spinal_Cord_Lumbar']['adj_beta_tdp_vs_ctrl']}`).",
        "5. **`#24 C019` Baricitinib / Selective `JAK1 JH1` (`TIER_3_EXPLORATORY_DISCOVERY`, `TRL_5`, `5` hurdles — Demoted from Upstream Core to Tier 3 Watchlist):** Deconfounded `rs3831317`-neutral `5`-protein high-chitinase CSF glial stratum achieves `Emory` single-center OOF `AUC = 0.8188` (`unadjusted Welch p = 6.40e-8`) and leave-one-MGH-control-out target-site recalibration `AUC = 0.8801` (in-sample `0.8850`, `p = 4.88e-11`, correcting `-0.5034 z` `MGH` Control drift; vs bank-only `non-MGH` indicator `AUC = 0.9444` & raw confounded `0.9405`; cross-sectional `Symptomatic-vs-Asymptomatic C9` enrichment), but is placed in `TIER_3` across `5` hurdles: `3.80 nM` CSF (`modeled ~9%` cellular pSTAT occupancy `[MODEL_PRIOR]` vs. `2,500 nM` screen; `657x` gap), `NADALS` `1/9` PE SAE + `1/9` DVT (`N = 9`), the **`JAK1`-vs-autonomous-neuronal-`JAK2` APA catch-22** (`JAK2`-sparing `JAK1` inhibitors forfeit TDP-43-induced neuronal `JAK2` 3'-UTR shortening `dPAS = -0.4391, padj = 2.96e-61` in glia-free sALS iPSC-MNs), bridged `pg/mL` immunoassay calibration across multi-case/control centers, and unproven living-CSF-to-cortical `ALS-Glia` `pSTAT3/CXCL10` interaction PD.",
        "",
        "## 3. Complete `52`-Hypothesis Unified Portfolio Ledger (`Ranks #1–#52`)",
        "",
        "| Act (`Bio`) | ID | Origin (`Subcohort`) | Track | Gene / Drug | Decision (`Epistemic State`) | Scientific Tier | `TRL` | Hurdles | Lead `GRCh38` Interval (`Safety`) |",
        "| :---: | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- |",
    ])
    for r in port_rows:
        pid = r["portfolio_id"]
        acc_id = r.get("accession_id") or legacy_to_accession(pid)
        brk = bio_rk_map[pid]
        link = (
            f"[{acc_id}](file:///{ROOT_POSIX}/reports/candidates/{pid}.md)"
            if r["origin_phase"] == "CURATED_CLINICAL_33"
            else f"[{acc_id}](file:///{ROOT_POSIX}/reports/phase3/PHASE3B_DENOVO_UNBIASED_DISCOVERY.md)"
        )
        iv_disp = f"`{r['lead_cis_interval_id']}` (`{r['lead_offtarget_safety_status']}`)" if r["lead_cis_interval_id"] != "NONE" else "`NONE`"
        lines.append(
            f"| `#{r['unified_rank']}` (`#{brk}`) | **{link}** | `{r['origin_phase']}` (`{r['origin_subcohort']}`) | `{r['track']}` | "
            f"{r['gene_or_drug']} | **`{r['decision']}`** (`{r['epistemic_state']}`) | `{r['scientific_actionability_tier']}` | "
            f"`{r['clinical_readiness_trl']}` | `{r['unsolved_hurdle_count']}` | {iv_disp} |"
        )

    lines.extend([
        "",
        "## 4. Subunit & Pathway Gene Dissection Ledger (`18` Subunits Across `EALS-014`, `EALS-015`, `EALS-023`, `EALS-017`, `EALS-018`)",
        "",
        "*Scope Note:* Multi-subunit complexes, genetic loci, and biofluid panels (`EALS-014 CHMP7/CHMP2B`, `EALS-015 chr14q12 SCFD1/G2E3`, `EALS-023 YKT6` + `5` cis-Golgi SNARE selectivity comparators, `EALS-017` `4`-protein CSF panel, and `EALS-018` `C1QA/B/C` + `C4B` RCCX comparator; systemic `C3` / pegcetacoplan is evaluated independently as `EALS-024`) are audited at the individual gene level below.",
        "",
        "| Sub-Node | Parent | Gene | Molecular Role | Human Constraint & Essentiality (`gnomAD v4` / `DepMap`) | Single-Gene Verdict |",
        "| :--- | :---: | :--- | :--- | :--- | :--- |",
    ])
    for s in sub_rows:
        v_short = s["subnode_verdict"].split(":")[0].strip()
        gn_short = s["gnomad_essentiality_check"].split(";")[0] + "; " + (s["gnomad_essentiality_check"].split(";")[1].strip() if ";" in s["gnomad_essentiality_check"] else "")
        lines.append(f"| `{legacy_to_accession(s['subnode_id'])}` | `{legacy_to_accession(s['parent_carbon_id'])}` | **`{s['gene_symbol']}`** | {s['molecular_role']} | {gn_short} | **`{v_short}`** |")

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
        sc_acc = c.get("subnode_accession_id") or legacy_to_accession(c["subnode_or_cand_id"])
        lines.append(
            f"| `{c['unified_interval_order']}` | `{sc_acc}` (`{c['gene_symbol']}` #{c['rank_within_gene']}) | {lead_tag} | "
            f"`{c['interval_id']}` | `{c['length_bp']}` | `{c['cis_mechanism_or_mode']}` | `{c['tm_phys_pops_c']}` | `{c['max_avi_phred']}` | "
            f"`{c['spliced_0mm_genes']}/{c['spliced_1mm_genes']}/{c['spliced_wobble_only_pc_genes']}` | "
            f"`{c['premRNA_0mm_sense_genes']}/{c['premRNA_1mm_splice50bp_genes']}/{c['premRNA_wobble_only_splice50bp_pc_genes']}/{c['premRNA_2mm_splice25bp_pc_genes']}/{c['bulge_1nt_steric_pc_genes']}/{c['sub18_core_steric_pc_genes']}` | "
            f"`{fl_short}` | **`{c['offtarget_safety_status']}`** | {a_link} |"
        )
    return [translate_legacy_tokens_in_prose(ln) for ln in lines]
