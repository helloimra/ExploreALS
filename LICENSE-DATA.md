# ExploreALS Data, Documentation & Third-Party Attribution License

## 1. Original Registries, Monographs & Documentation (`CC-BY-4.0`)
Original curated CSV registries (`registries/*.csv`), schemas (`schemas/*`), interactive web documentation (`docs/*`), and prose analyses authored for `ExploreALS` are licensed under the **Creative Commons Attribution 4.0 International License (`CC BY 4.0`)** (`https://creativecommons.org/licenses/by/4.0/`), while Python source code (`src/`, `scripts/`, `pipelines/`, `work/**/*.py`) is licensed under the **MIT License** (`LICENSE`).

## 2. Third-Party Open Datasets & Publisher Supplements (`48` Staged Datasets)
`ExploreALS` analyzes 48 publicly accessible biomedical datasets documented in `registries/datasets_manifest.csv` with exact 64-character SHA-256 digests and legal redistribution tiers:
- **`TIER_A_OPEN_REDISTRIBUTABLE`:** Datasets released under `CC0 1.0` (RCSB PDB experimental structures, Broad Institute gnomAD v4.1) or `CC BY 4.0` (Trautwig et al. 2025 PMC12082929, Oh et al. 2023 PMC10215566, AlphaFold Protein Structure Database v6, EMBL-EBI GENCODE v46, NCBI GEO public series, Ensembl reference tables) and project-authored reference maps.
- **`TIER_B_PUBLISHER_HTTPS_FETCH`:** Openly downloadable supplemental `.xlsx` tables and `CC BY-NC-ND 4.0` open-access supplements (e.g., *Nature*, *Nature Neuroscience*, *Cell*, *Cell Reports*, *Acta Neuropathologica*). These files are **never re-hosted** in this repository or its release archives; `scripts/fetch_open_datasets.py` retrieves them directly from canonical publisher/EuropePMC HTTPS endpoints to the user's local `data/` directory and verifies their SHA-256 checksums.
- **`TIER_C_DUA_OR_BASELINE`:** Cohorts hosted on Synapse (`syn51105515` Pineda et al. 2024; `syn52335732` Fujita et al. ROSMAP) require individual registration and acceptance of upstream data-use terms via `SYNAPSE_AUTH_TOKEN`.

## 3. Google DeepMind AlphaGenome Non-Commercial Notice
Cached AlphaGenome Variant Impact (`AVI`) and track-level splicing predictions in `cache/api_snapshots/` and `work/` outputs were generated via the Google DeepMind AlphaGenome API (`v1`) and AlphaGenome Atlas under **Google DeepMind AlphaGenome Non-Commercial Terms of Use** for non-commercial academic/preclinical research only. Any commercial user must omit AlphaGenome-derived columns or obtain separate commercial authorization from Google DeepMind.
