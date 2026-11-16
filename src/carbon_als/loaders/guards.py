"""Donor-uniqueness, modality, and contrast-matching guardrails for CarbonALS loaders."""

from __future__ import annotations

from collections.abc import Sequence
import hashlib
from pathlib import Path
import sys
import urllib.request

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase1_batches.batch_runner_utils import (  # noqa: E402
    assert_contrast_pair,
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)

ALLOWED_MODALITIES = {
    "RNA_SPLICING_MAJIQ",
    "RNASEQ_DESEQ2",
    "RIBOSEQ_DESEQ2",
    "PROTEOMICS_DIA",
    "PROTEOMICS_CSF_TMT",
    "PROTEOMICS_CSF_DIA",
    "IPSC_MN_SURVIVAL_DAYS",
    "SPATIAL_VISIUM_PSEUDOBULK",
    "SNRNA_PSEUDOBULK_LOG2CPM",
    "RNASEQ_BULK_SUBTYPE",
}


def assert_unique_donors(donor_ids: Sequence[str], context: str) -> list[str]:
    """Fail immediately if technical replicates or sub-fractions from the same donor are pooled."""
    cleaned = [str(d).strip() for d in donor_ids if str(d).strip()]
    if not cleaned:
        raise ValueError(f"[{context}] Empty donor ID list.")
    if len(set(cleaned)) != len(cleaned):
        dups = sorted({x for x in cleaned if cleaned.count(x) > 1})
        raise AssertionError(
            f"PSEUDOREPLICATION BLOCKED in {context}: duplicate donor IDs pooled: {dups[:10]}"
        )
    return cleaned


def assert_modality(modality: str, dataset_id: str) -> str:
    """Enforce explicit assay-modality tagging so RNA-seq is never misreported as proteomics."""
    if modality not in ALLOWED_MODALITIES:
        raise ValueError(
            f"[{dataset_id}] Invalid modality '{modality}'; expected one of {sorted(ALLOWED_MODALITIES)}"
        )
    return modality


def numeric_clean(series: pd.Series) -> np.ndarray:
    arr = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
    return arr[np.isfinite(arr)]


def assert_1based_exon_coords(
    start_1b: int,
    end_1b: int,
    ensembl_start_1b: int,
    ensembl_end_1b: int,
    context: str,
) -> int:
    """Block 0-based half-open BED coordinate offsets against 1-based closed Ensembl boundaries."""
    if start_1b == ensembl_start_1b - 1 and end_1b == ensembl_end_1b:
        raise AssertionError(
            f"ZERO_BASED_BED_OFFSET_BLOCKED in {context}: got {start_1b}-{end_1b} "
            f"(0-based start), expected 1-based closed {ensembl_start_1b}-{ensembl_end_1b}"
        )
    if start_1b != ensembl_start_1b or end_1b != ensembl_end_1b:
        raise AssertionError(
            f"EXON_COORD_MISMATCH in {context}: got {start_1b}-{end_1b}, "
            f"expected Ensembl 1-based {ensembl_start_1b}-{ensembl_end_1b}"
        )
    return end_1b - start_1b + 1


def download_https_structure(url: str, dest: Path, timeout: int = 30) -> tuple[int, str]:
    """Fetch 3D coordinate files strictly over HTTPS (never passive FTP) and return (bytes, sha256)."""
    if not url.lower().startswith("https://"):
        raise ValueError(f"FTP_OR_INSECURE_URL_BLOCKED: '{url}' must use https:// (e.g. files.rcsb.org).")
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "CarbonALS/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = resp.read()
    if len(payload) < 256:
        raise RuntimeError(f"Truncated structure download from {url}: {len(payload)} bytes")
    dest.write_bytes(payload)
    return len(payload), hashlib.sha256(payload).hexdigest()


__all__ = [
    "ALLOWED_MODALITIES",
    "assert_1based_exon_coords",
    "assert_contrast_pair",
    "assert_modality",
    "assert_unique_donors",
    "download_https_structure",
    "numeric_clean",
    "read_xlsx_sparse_safe",
    "resolve_col",
    "resolve_dataset_path",
]
