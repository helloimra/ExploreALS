# ExploreALS v1.2 — Unified ALS Therapeutic & Genetic Target Portfolio Explorer + Computational Replication Package

**Live Interactive Explorer (5 Views):** [https://helloimra.github.io/ExploreALS/](https://helloimra.github.io/ExploreALS/)
**Author:** Ricardo Agoga · [helloimra@proton.me](mailto:helloimra@proton.me) · [github.com/helloimra/ExploreALS](https://github.com/helloimra/ExploreALS)

## Overview
`ExploreALS v1.2` is an independent computational triage audit evaluating **52 ALS therapeutic and biomarker hypotheses** (33 published clinical, genetic & neuropathological programs and 19 candidates filtered from open multi-omic screens), **18 subunit & selectivity dissections** across multi-subunit complexes, GWAS loci & biofluid panels, and **26 Coordinate-Only Cis-Regulatory Search Windows** (`0` chemically modified synthesis-ready ASO sequences).

**Evidence base:** `40` open-access biomedical datasets & reference maps (`38` external accessions + `2` repo-bundled reference maps: `21` human tissue/CSF/iPSC/in-vitro cohort & assay files, `13` 3D structures, `6` genome/feature references; published tables/counts, zero new wet-lab data). The cohort data resolves into **`8` independent donor-overlap clusters** ([`cohort_overlap_map.csv`](registries/cohort_overlap_map.csv)):
- **Postmortem tissue:** NYGC ALS Consortium (`GSE153960`, incl. Tam 2019, O'Neill 2025, Ma 2022 and Bryce-Smith 2025 reanalyses) · Pineda 2024 BA4/BA9 snRNA-seq · Edinburgh `GSE290359` snRNA-seq · Prudencio 2015 paired regions + Zhang 2026 spinal-cord spatial · Spillman 2026 C9-FTD subcellular-fraction DIA
- **Living-patient biofluids:** Trautwig 2025 multi-center CSF proteomics (+ Oh 2023 external CSF cohort)
- **Patient-derived and in-vitro models:** Bye 2025 / AnswerALS sALS iPSC-MN drug screen · TDP-43 knockdown neuron series (Brown 2022, Zeng 2025, Bryce-Smith 2025)

Agreement *within* a cluster is treated as cross-platform validation, not independent replication.

## 3-Level Independent Computational Replication Quickstart

```bash
# Level 1 (<10s, 0 MB extra data): Verify all 17 CSV schemas, FKs, citation lock, Epistemic Asymmetry & 194/194 64-char SHA-256s
uv sync --frozen
uv run python scripts/verify_carbon_als.py --mode cached

# Level 2 (~5s cached / full with staged data/): Run all 8 single-command Flagship Monograph Reproducers
uv run python scripts/reproduce_all.py --flagship-only

# Stage open datasets (Tier A release bundle + Tier B direct publisher/EuropePMC HTTPS + SHA-256 verification)
uv run python scripts/fetch_open_datasets.py --list
uv run python scripts/fetch_open_datasets.py --source release

# Level 3 (~2s): Rebuild zero-CDN 5-view Explorer & 8 Monographs and run archive-aware sanitization gate
uv run python work/phase4_final_synthesis/scripts/02_render_phase4_synthesis.py --public-docs-only
uv run python scripts/audit_public_sanitization.py --target .
```

### Standalone Tier 1 & Tier 2 Translational Monographs
- **Tier 1 (`Actionable Now`):** [#1 S06 · SARM1](https://helloimra.github.io/ExploreALS/monographs/S06.html) · [#2 S07 · Aldesleukin](https://helloimra.github.io/ExploreALS/monographs/S07.html)
- **Tier 2 (`Focused Preclinical / Biofluid Gate First`):** [#3 C001 · UNC13A](https://helloimra.github.io/ExploreALS/monographs/C001.html) · [#4 C006 · KCNQ2](https://helloimra.github.io/ExploreALS/monographs/C006.html) · [#5 C002 · STMN2](https://helloimra.github.io/ExploreALS/monographs/C002.html) · [#6 C007 · IL1RL1 / sST2](https://helloimra.github.io/ExploreALS/monographs/C007.html) · [#7 DN-01 · ATG4B](https://helloimra.github.io/ExploreALS/monographs/DN-01.html) · [#8 DN-04 · CELF5](https://helloimra.github.io/ExploreALS/monographs/DN-04.html)

## Licensing, Disclaimers & Open-Data Provenance
- **Dual Software & Data License:** Python source code (`src/`, `scripts/`, `pipelines/`, `work/**/*.py`) is licensed under the **MIT License** ([LICENSE](./LICENSE)); original curated registries (`registries/*.csv`), schemas, and monographs are licensed under **CC BY 4.0** ([LICENSE-DATA.md](./LICENSE-DATA.md)). Non-`CC-BY` publisher supplements (`Tier B`) are never re-hosted and are fetched directly from canonical publisher HTTPS endpoints.
- **Preclinical Research Only — Not Medical Advice:** `ExploreALS v1.2` is an independent preclinical and translational research resource intended solely for scientific hypothesis generation. Nothing in this repository or explorer constitutes medical advice, clinical trial recruitment, or a treatment recommendation; individuals with ALS and caregivers should always consult their neurologist or ALS care team before starting, stopping, or modifying any therapy.
- **AI-Assisted Workflow Disclosure:** Curated via human-directed AI synthesis workflows paired with deterministic Python statistical pipelines across 40 open-access human ALS and preclinical resources (published tables, raw counts, and structures; zero new wet-lab data) and primary-source verification (`PubMed`, `Europe PMC`, `ClinicalTrials.gov`). Quantitative contrasts (`194/194` 64-char SHA-256 anchored) are programmatically audited and separated from modeling priors (`[MODEL_PRIOR]`), though synthesis prose may contain residual errors — always verify against linked primary sources before experimental use.
- **Data & Tool Attributions:** Google DeepMind AlphaGenome (`v1` API & Atlas `AVI`; non-commercial research use only), NIH GTEx (`v8 / v10`), Open Targets (`v4`), gnomAD (`v4.1`), Ensembl/GENCODE (`v46`), ChEMBL (`v34`), UniProt, RCSB PDB, and ClinicalTrials.gov.
