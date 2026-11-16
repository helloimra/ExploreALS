# ExploreALS v1.2 — Unified ALS Therapeutic & Genetic Target Portfolio Explorer + Computational Replication Package

**Live Interactive Explorer (6 Tabs):** [https://helloimra.github.io/ExploreALS/](https://helloimra.github.io/ExploreALS/)
**Author:** Ricardo Agoga (Independent Researcher) · [helloimra@proton.me](mailto:helloimra@proton.me) · [github.com/helloimra/ExploreALS](https://github.com/helloimra/ExploreALS)

## Overview
`ExploreALS v1.2` synthesizes **59 ALS drug and genetic target candidates**, **19 single-gene sub-nodes** de-bundled from multi-gene composite axes, and **26 Coordinate-Only Cis-Regulatory Search Windows** (`0` chemically modified synthesis-ready ASO sequences) across `48` SHA-256-verified open-access human ALS cohorts (`NYGC GSE153960`, `Pineda 2024`, `Edinburgh GSE290359`, `Zhang 2026` spatial, `Spillman 2026` fraction DIA, `Trautwig 2025` & `Oh 2023` living CSF proteomics, `Brown/Ma 2022` & `Bryce-Smith/Zeng 2025` TDP-43 splicing/APA, and `Bye 2025` sALS patient iPSC-MN drug screening).

## 3-Level Independent Computational Replication Quickstart

```bash
# Level 1 (<10s, 0 MB extra data): Verify all 16 CSV schemas, FKs, Epistemic Asymmetry & 216/216 64-char SHA-256s
uv sync --frozen
uv run python scripts/verify_carbon_als.py --mode cached

# Level 2 (~5s cached / full with staged data/): Run all 8 single-command Flagship Monograph Reproducers
uv run python scripts/reproduce_all.py --flagship-only

# Stage open datasets (Tier A release bundle + Tier B direct publisher/EuropePMC HTTPS + SHA-256 verification)
uv run python scripts/fetch_open_datasets.py --list
uv run python scripts/fetch_open_datasets.py --source release

# Level 3 (~2s): Rebuild zero-CDN 6-tab Explorer & 8 Monographs and run archive-aware sanitization gate
uv run python work/phase4_final_synthesis/scripts/02_render_phase4_synthesis.py --public-docs-only
uv run python scripts/audit_public_sanitization.py --target .
```

### Standalone Tier 1 & Tier 2 Translational Monographs
- **Tier 1 (`Actionable Now`):** [#1 S06 · SARM1](https://helloimra.github.io/ExploreALS/monographs/S06.html) · [#2 C006 · KCNQ2](https://helloimra.github.io/ExploreALS/monographs/C006.html) · [#3 S07 · Aldesleukin](https://helloimra.github.io/ExploreALS/monographs/S07.html)
- **Tier 2 (`Focused Preclinical / Biofluid Gate First`):** [#4 C001 · UNC13A](https://helloimra.github.io/ExploreALS/monographs/C001.html) · [#5 C002 · STMN2](https://helloimra.github.io/ExploreALS/monographs/C002.html) · [#6 C007 · IL1RL1 / sST2](https://helloimra.github.io/ExploreALS/monographs/C007.html) · [#7 DN-01 · ATG4B](https://helloimra.github.io/ExploreALS/monographs/DN-01.html) · [#8 DN-04 · CELF5](https://helloimra.github.io/ExploreALS/monographs/DN-04.html)

## Licensing, Disclaimers & Open-Data Provenance
- **Dual Software & Data License:** Python source code (`src/`, `scripts/`, `pipelines/`, `work/**/*.py`) is licensed under the **MIT License** ([LICENSE](./LICENSE)); original curated registries (`registries/*.csv`), schemas, and monographs are licensed under **CC BY 4.0** ([LICENSE-DATA.md](./LICENSE-DATA.md)). Non-`CC-BY` publisher supplements (`Tier B`) are never re-hosted and are fetched directly from canonical publisher HTTPS endpoints.
- **Preclinical Research Only — Not Medical Advice:** `ExploreALS v1.2` is an independent preclinical and translational research resource intended solely for scientific hypothesis generation. Nothing in this repository or explorer constitutes medical advice, clinical trial recruitment, or a treatment recommendation; individuals with ALS and caregivers should always consult their neurologist or ALS care team before starting, stopping, or modifying any therapy.
- **AI-Assisted Workflow Disclosure:** Developed via human-directed multi-agent AI research workflows paired with deterministic Python statistical recomputation across open-access human ALS datasets and primary-source verification (`PubMed`, `Europe PMC`, `ClinicalTrials.gov`). Quantitative contrasts (`216/216` 64-char SHA-256 anchored) are programmatically audited and separated from modeling priors (`[MODEL_PRIOR]`), though synthesis prose may contain residual errors — always verify against linked primary sources before experimental use.
- **Data & Tool Attributions:** Google DeepMind AlphaGenome (`v1` API & Atlas `AVI`; non-commercial research use only), NIH GTEx (`v8 / v10`), Open Targets (`v4`), gnomAD (`v4.1`), Ensembl/GENCODE (`v46`), ChEMBL (`v34`), UniProt, RCSB PDB, and ClinicalTrials.gov.
