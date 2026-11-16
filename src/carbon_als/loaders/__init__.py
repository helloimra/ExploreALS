"""Shared verified dataset loaders and anti-pseudoreplication guardrails."""

from .cohorts import (
    load_brown2022_splicing,
    load_bye2025_screen,
    load_spillman2026_fractions,
)
from .guards import (
    ALLOWED_MODALITIES,
    assert_1based_exon_coords,
    assert_contrast_pair,
    assert_modality,
    assert_unique_donors,
    download_https_structure,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)
from .spatial_snrna import (
    PINEDA_COMPOSITE_CELLTYPES,
    load_edinburgh_pseudobulk,
    load_oneill2025_subtypes,
    load_pineda2024_pseudobulk,
    load_zhang2026_spatial,
)

__all__ = [
    "ALLOWED_MODALITIES",
    "PINEDA_COMPOSITE_CELLTYPES",
    "assert_1based_exon_coords",
    "assert_contrast_pair",
    "assert_modality",
    "assert_unique_donors",
    "download_https_structure",
    "load_brown2022_splicing",
    "load_bye2025_screen",
    "load_edinburgh_pseudobulk",
    "load_oneill2025_subtypes",
    "load_pineda2024_pseudobulk",
    "load_spillman2026_fractions",
    "load_zhang2026_spatial",
    "read_xlsx_sparse_safe",
    "resolve_col",
    "resolve_dataset_path",
]
