"""Lightweight stdlib-only fail-loud lookup and strict RFC-8259 work-JSON provenance helpers.

Zero third-party imports so any Python or external plugin `uv` environment can import cleanly via:
  from carbon_als.io_guards import require_hit, write_work_json
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
from typing import Any, TypeVar

T = TypeVar("T")
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTUacgtu]{15,}(?![A-Za-z0-9_])")


def require_hit(value: T | None, label: str) -> T:
    """Fail loud on missing/empty targeted biological or library lookups instead of silently writing {} or None."""
    if value is None:
        raise LookupError(f"REQUIRED_LOOKUP_EMPTY: {label} (got None)")
    if isinstance(value, (str, bytes, list, tuple, dict, set)) and len(value) == 0:
        raise LookupError(f"REQUIRED_LOOKUP_EMPTY: {label} (got empty {type(value).__name__})")
    if hasattr(value, "empty") and bool(getattr(value, "empty")):
        raise LookupError(f"REQUIRED_LOOKUP_EMPTY: {label} (got empty DataFrame/Series)")
    return value


def _sanitize_strict(obj: Any) -> Any:
    if isinstance(obj, bool) or obj is None or isinstance(obj, (str, int)):
        return obj
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {str(k): _sanitize_strict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_strict(v) for v in obj]
    if hasattr(obj, "item"):
        return _sanitize_strict(obj.item())
    if isinstance(obj, Path):
        return obj.as_posix()
    return str(obj)


def write_work_json(
    path: str | Path,
    payload: dict[str, Any],
    *,
    script: str | Path,
    controls_passed: bool,
    controls_summary: dict[str, Any] | None = None,
    extra_meta: dict[str, Any] | None = None,
    indent: int = 2,
) -> Path:
    """Stamp compact `_meta` (requiring explicit controls_passed), enforce strict RFC-8259 & biosecurity, and write UTF-8."""
    out_fp = Path(path)
    meta: dict[str, Any] = {
        "script": Path(script).name,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "controls_passed": bool(controls_passed),
        "strict_rfc8259": True,
    }
    if controls_summary is not None:
        meta["controls_summary"] = controls_summary
    if extra_meta:
        meta.update(extra_meta)
    wrapped = {"_meta": meta, **{k: v for k, v in payload.items() if k != "_meta"}}
    txt = json.dumps(_sanitize_strict(wrapped), indent=indent, allow_nan=False)
    if SEQ_GUARD_RE.search(txt):
        raise AssertionError(f"BIOSECURITY_GUARD_TRIGGERED: raw >=15-nt sequence detected before writing {out_fp.name}!")
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(txt, encoding="utf-8")
    return out_fp
