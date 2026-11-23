"""Shared provenance-safe data & registry utilities for CarbonALS Phase 1 batches."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REG_DIR = ROOT / "registries"


TEXT_EXTS = {".csv", ".tsv", ".json", ".bed", ".txt", ".xml", ".md", ".cif", ".gtf"}


def _sha256_path(path: Path) -> str:
    if path.is_file():
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    files = sorted((p for p in path.rglob("*") if p.is_file()), key=lambda p: p.relative_to(path).as_posix())
    agg = hashlib.sha256()
    for f in files:
        rel = f.relative_to(path).as_posix()
        agg.update(f"{rel}:{_sha256_path(f)}\n".encode("utf-8"))
    return agg.hexdigest()


def _file_matches_sha256(fp: Path, expected: str) -> bool:
    """Verify exact file content against expected SHA-256, permitting LF/CRLF equivalence on text files."""
    if not fp.is_file():
        return False
    if _sha256_path(fp) == expected:
        return True
    if fp.suffix.lower() in TEXT_EXTS:
        raw = fp.read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        if hashlib.sha256(lf).hexdigest() == expected:
            return True
        if hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest() == expected:
            return True
    return False


def _dir_matches_per_file_lock(dataset_id: str, target: Path, expected_dir_sha: str) -> bool:
    """Verify exact directory file roster, per-file content hashes (EOL-equivalent for text), and aggregate digest."""
    lock_fp = ROOT / "schemas" / "dataset_files_lock.json"
    if not target.is_dir() or not lock_fp.is_file():
        return False
    lock_raw = json.loads(lock_fp.read_text(encoding="utf-8"))
    files = ((lock_raw.get("datasets", lock_raw)).get(dataset_id) or {}).get("files") or []
    if not files:
        return False
    actual_rels = sorted(p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file())
    locked_sorted = sorted(files, key=lambda f: f["rel"])
    if actual_rels != [f["rel"] for f in locked_sorted]:
        return False
    if not all(_file_matches_sha256(target / f["rel"], f["sha256"]) for f in locked_sorted):
        return False
    agg = hashlib.sha256()
    for f in locked_sorted:
        agg.update(f"{f['rel']}:{f['sha256']}\n".encode("utf-8"))
    return agg.hexdigest() == expected_dir_sha


def resolve_dataset_path(dataset_id: str, verify_hash: bool = False) -> Path:
    """Resolve a staged dataset_id from datasets_manifest.csv to its local Path."""
    manifest = pd.read_csv(REG_DIR / "datasets_manifest.csv")
    match = manifest.loc[manifest["dataset_id"] == dataset_id]
    if match.empty:
        raise KeyError(f"Unknown dataset_id: {dataset_id!r}")
    row = match.iloc[0]
    target = ROOT / str(row["local_relpath"])
    if not target.exists():
        raise FileNotFoundError(f"Missing staged dataset path: {target}")
    if verify_hash:
        expected = str(row["sha256"])
        if target.is_file():
            if not _file_matches_sha256(target, expected):
                raise ValueError(f"SHA-256 mismatch on {dataset_id}: {_sha256_path(target)} != {expected}")
        else:
            actual = _sha256_path(target)
            if actual != expected and not _dir_matches_per_file_lock(dataset_id, target, expected):
                raise ValueError(f"SHA-256 mismatch on {dataset_id}: {actual} != {expected}")
    return target


def resolve_col(df: pd.DataFrame, *aliases: str) -> str:
    """Header-resolved column lookup; forbids positional indexing."""
    norm = {str(c).strip().lower(): str(c) for c in df.columns}
    for alias in aliases:
        key = alias.strip().lower()
        if key in norm:
            return norm[key]
    for alias in aliases:
        key = alias.strip().lower()
        hits = [orig for low, orig in norm.items() if key in low]
        if len(hits) == 1:
            return hits[0]
    raise KeyError(f"Could not resolve column aliases {aliases} in {list(df.columns)[:20]}")


def read_xlsx_sparse_safe(
    xlsx_path: Path, sheet_name: str, header_row_1based: int = 1
) -> pd.DataFrame:
    """Read Excel sheet via openpyxl column coordinates so sparse XML never shifts columns."""
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        if sheet_name not in wb.sheetnames:
            raise KeyError(f"Sheet {sheet_name!r} not in {wb.sheetnames}")
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()
    if len(rows) < header_row_1based:
        raise ValueError(f"Sheet {sheet_name!r} has fewer than {header_row_1based} rows")
    raw_headers = rows[header_row_1based - 1]
    headers = [
        str(h).strip() if h is not None and str(h).strip() else f"_unnamed_col_{idx}"
        for idx, h in enumerate(raw_headers)
    ]
    body = rows[header_row_1based:]
    return pd.DataFrame(body, columns=headers)


def assert_contrast_pair(
    diff_col: pd.Series,
    mean_a: pd.Series,
    mean_b: pd.Series,
    sign: float = 1.0,
    tol: float = 1e-3,
) -> float:
    """Verify that reported difference equals sign * (mean_a - mean_b) within tolerance."""
    d = pd.to_numeric(diff_col, errors="coerce")
    a = pd.to_numeric(mean_a, errors="coerce")
    b = pd.to_numeric(mean_b, errors="coerce")
    mask = d.notna() & a.notna() & b.notna()
    if int(mask.sum()) == 0:
        raise ValueError("No overlapping numeric rows to verify contrast pair.")
    max_err = float(np.max(np.abs(d[mask] - sign * (a[mask] - b[mask]))))
    if max_err > tol:
        raise AssertionError(
            f"Contrast pair mismatch: max |diff - ({sign})*(A - B)| = {max_err:.6g} > {tol}"
        )
    return max_err


def append_csv_row(csv_path: Path, row_dict: dict[str, object], pk_col: str) -> None:
    """Append or replace a row keyed by pk_col in a CarbonALS registry CSV."""
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames: Iterable[str] = reader.fieldnames or []
        fields = list(fieldnames)
        existing = [r for r in reader if r[pk_col] != str(row_dict[pk_col])]
    clean_row = {k: str(row_dict.get(k, "")) for k in fields}
    existing.append(clean_row)
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(existing)
