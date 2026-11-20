"""Shared verification & dual-mode (cached + raw-data) audit utilities for the 8 ExploreALS v1.2 Flagship Monograph Reproducers."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, NamedTuple


class VerifiedCheck(NamedTuple):
    label: str
    observed: Any
    expected: Any
    status: str

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


def has_raw_dataset(relpath: str) -> bool:
    return (ROOT / relpath).exists()


def load_json_any(relpath: str) -> Any:
    p = ROOT / relpath
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    pgz = ROOT / f"{relpath}.gz"
    if pgz.is_file():
        with gzip.open(pgz, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    raise FileNotFoundError(f"Missing artifact: {relpath}")


def load_csv_by_key(relpath: str, key_col: str) -> dict[str, dict[str, str]]:
    with (ROOT / relpath).open(encoding="utf-8") as fh:
        return {r[key_col]: r for r in csv.DictReader(fh)}


def load_csv_rows(relpath: str) -> list[dict[str, str]]:
    with (ROOT / relpath).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def sha256_short(relpath: str) -> str:
    p = ROOT / relpath
    if not p.is_file() and (ROOT / f"{relpath}.gz").is_file():
        p = ROOT / f"{relpath}.gz"
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def assert_close(label: str, observed: float, expected: float, rtol: float = 1e-4, atol: float = 1e-4) -> VerifiedCheck:
    ok = math.isclose(observed, expected, rel_tol=rtol, abs_tol=atol)
    if not ok:
        raise AssertionError(f"[FAIL] {label}: observed={observed} != expected={expected}")
    return VerifiedCheck(label, observed, expected, "PASS")


def assert_equal(label: str, observed: Any, expected: Any) -> VerifiedCheck:
    if observed != expected or type(observed) is not type(expected):
        raise AssertionError(f"[FAIL] {label}: observed={observed!r} != expected={expected!r}")
    return VerifiedCheck(label, observed, expected, "PASS")


def print_audit_report(cand_id: str, title: str, checks: list[VerifiedCheck], priors_note: str) -> None:
    print(f"=== ExploreALS v1.2 Flagship Monograph Audit: {cand_id} ({title}) ===")
    for chk in checks:
        if not isinstance(chk, VerifiedCheck) or chk.status != "PASS":
            raise AssertionError(f"[FAIL] Unverified flagship check tuple in {cand_id}: {chk!r}")
        label, obs, exp, status = chk
        o_s = f"{obs:.6g}" if isinstance(obs, float) else str(obs)
        e_s = f"{exp:.6g}" if isinstance(exp, float) else str(exp)
        print(f"  [{status}] {label}: observed={o_s} | expected={e_s}")
    print(f"  [EPISTEMIC BOUNDARY] {priors_note}")
    print(f"=== ALL {len(checks)}/{len(checks)} CHECKS PASSED FOR {cand_id} ===\n")
