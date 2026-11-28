"""Glob-based workspace output integrity, AST dependency staleness, biosecurity, and contract verifier.

Eliminates manual filename whitelists by automatically discovering work/*/outputs/*.json, verifying:
  1. Strict RFC-8259 JSON (rejects NaN / Infinity).
  2. Coordinate-only biosecurity (0 raw >=15-nt nucleotide strings in outputs and caches).
  3. Schema-driven scientific contracts (AlphaGenome POSCTRL precedence + non-null canonical junctions;
     off-target on_target_0mm_self_hits >= 1 and 0mm pre-mRNA hard FAIL status).
  4. AST-resolved dependency staleness (flags any output JSON older than its producing script or
     imported concrete src/carbon_als/ modules; fails exit code under --strict-mtime).

Usage:
  .\\.venv\\Scripts\\python.exe scripts/check_work_outputs.py [--scope active|all] [--strict-mtime]
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys
from typing import Any

SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTUacgtu]{15,}(?![A-Za-z0-9_])")
ARCHIVED_PREFIXES = ("phase1_", "phase1c_", "phase1d_", "phase2_")
ARCHIVED_RAW_HEADER_PROBES = {
    "phase1_pack_c_schema_audit.json",
    "phase1d_remaining_cohorts_audit.json",
}
PACK_C_OFFTARGET_PREFIXES = ("v15_followup_", "ws3_")


def _scan_recursive_invariants(obj: Any, rel: str, errors: list[str], path: str = "") -> None:
    """Catch swallowed try/except {'error': '...'} payloads and rounded BH-FDR (q < p) inversions."""
    if isinstance(obj, dict):
        err_val = obj.get("error")
        if isinstance(err_val, str) and err_val.strip():
            errors.append(f"SWALLOWED_ERROR_KEY: {rel}@{path or '<root>'} ({err_val[:80]})")
        q_keys = [k for k in obj if (k.startswith("q_bh") or k == "fdr_bh") and isinstance(obj[k], (int, float))]
        if q_keys:
            p_val = next(
                (float(obj[pk]) for pk in ("p_value", "covariate_adjusted_nominal_p", "p_paired_t", "p_welch") if isinstance(obj.get(pk), (int, float))),
                None,
            )
            for qk in q_keys:
                qv = float(obj[qk])
                if qv < -1e-12 or qv > 1.0 + 1e-12 or (p_val is not None and qv < p_val - 1e-12):
                    errors.append(f"BH_FDR_LESS_THAN_P: {rel}@{path} ({qk}={qv} < p={p_val})")
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                _scan_recursive_invariants(v, rel, errors, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, (dict, list)):
                _scan_recursive_invariants(v, rel, errors, f"{path}[{i}]")


def _reject_non_rfc8259(const: str) -> Any:
    raise ValueError(f"Non-RFC8259 JSON constant: {const}")


def _resolve_carbon_als_imports(script_fp: Path, src_root: Path) -> list[Path]:
    """Parse script AST and return concrete src/carbon_als/*.py dependency files (excluding pure __init__.py)."""
    deps: set[Path] = set()
    try:
        tree = ast.parse(script_fp.read_text(encoding="utf-8"), filename=str(script_fp))
    except SyntaxError:
        return []

    def _add_mod(dotted: str) -> None:
        if not dotted.startswith("carbon_als."):
            return
        rel = Path(*dotted.split("."))
        cand_py = src_root / f"{rel}.py"
        if cand_py.is_file():
            deps.add(cand_py)
        else:
            cand_pkg = src_root / rel / "__init__.py"
            if cand_pkg.is_file():
                deps.add(cand_pkg)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                _add_mod(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            base = node.module
            if base == "carbon_als" or base.startswith("carbon_als."):
                _add_mod(base)
                for alias in node.names:
                    if alias.name != "*":
                        _add_mod(f"{base}.{alias.name}")
    return sorted(deps)


def _index_script_producers(work_root: Path, src_root: Path) -> dict[str, tuple[Path, list[Path]]]:
    """Map output JSON filename -> (producing_script_path, resolved_src_deps) by matching write targets only."""
    producers: dict[str, tuple[Path, list[Path]]] = {}
    assign_re = re.compile(
        r"^\s*(?:OUT_FP|OUT_JSON|OUT_PATH|SUMMARY_FP|out_fp|out_json|out_path)\s*(?::[^=]+)?=\s*.*?([A-Za-z0-9_.-]+\.json)",
        re.MULTILINE,
    )
    write_re = re.compile(r"([A-Za-z0-9_.-]+\.json)[^\n]*(?:write_text|json\.dump)")
    for script_fp in sorted(work_root.glob("*/scripts/*.py")):
        txt = script_fp.read_text(encoding="utf-8", errors="ignore")
        targets = assign_re.findall(txt) + write_re.findall(txt)
        if not targets:
            continue
        deps = _resolve_carbon_als_imports(script_fp, src_root)
        for name in targets:
            producers.setdefault(name, (script_fp, deps))
    return producers


def _collect_scoped_outputs(work_root: Path, scope: str) -> list[Path]:
    all_jsons = sorted(work_root.glob("*/outputs/*.json"))
    if scope == "all":
        return all_jsons
    return [
        fp for fp in all_jsons
        if not (fp.parent.parent.name == "phase5_pack_c_expansion" and fp.name.startswith(ARCHIVED_PREFIXES))
    ]


def audit_work_outputs(
    root: Path,
    *,
    scope: str = "active",
    strict_mtime: bool = False,
    mtime_tolerance_s: float = 1.0,
) -> dict[str, Any]:
    """Audit all scoped work/*/outputs/*.json and cache JSONs; returns structured report dict."""
    work_root = root / "work"
    src_root = root / "src"
    scoped = _collect_scoped_outputs(work_root, scope)
    producers = _index_script_producers(work_root, src_root)

    errors: list[str] = []
    stale: list[dict[str, Any]] = []
    legacy_notes: list[str] = []
    contracts_checked = {"alphagenome_files": 0, "offtarget_files": 0, "cache_files": 0}

    for fp in scoped:
        rel = fp.relative_to(root).as_posix()
        is_frozen_phase = fp.parent.parent.name in ("phase3a_execution_safety", "phase3b_denovo_discovery", "phase4_final_synthesis")
        txt = fp.read_text(encoding="utf-8")

        # 1. Biosecurity check
        if fp.name not in ARCHIVED_RAW_HEADER_PROBES and SEQ_GUARD_RE.search(txt):
            errors.append(f"BIOSECURITY_HIT: {rel}")

        # 2. Strict RFC-8259 JSON check
        try:
            data = json.loads(txt, parse_constant=_reject_non_rfc8259)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"INVALID_RFC8259_JSON: {rel} ({exc})")
            continue

        # 3. Schema-driven scientific contracts + recursive swallowed-error / BH-FDR invariants
        _scan_recursive_invariants(data, rel, errors)
        if isinstance(data, dict):
            meta = data.get("_meta")
            if isinstance(meta, dict) and meta.get("controls_passed") is False:
                errors.append(f"CONTROLS_FAILED: {rel} (_meta.controls_passed=False)")
            st = data.get("summary_table")
            if isinstance(st, list) and st and isinstance(st[0], dict) and "polarity_mn" in st[0] and "role" in st[0]:
                contracts_checked["alphagenome_files"] += 1
                bad_pos = [
                    r for r in st
                    if "POSCTRL" in str(r.get("role", "")) and r.get("polarity_mn") != "DISRUPTS_EXISTING_OR_CANONICAL_SPLICING"
                ]
                null_c = [r for r in st if "mn_canon_pct" in r and r.get("mn_canon_pct") is None]
                if bad_pos:
                    errors.append(f"ALPHAGENOME_POSCTRL_FAIL: {rel} ({len(bad_pos)} misclassified)")
                if null_c:
                    errors.append(f"ALPHAGENOME_NULL_CANONICAL: {rel} ({len(null_c)} null mn_canon_pct)")

            ivs = data.get("intervals")
            if isinstance(ivs, list) and ivs and isinstance(ivs[0], dict) and "offtarget_safety_status" in ivs[0]:
                contracts_checked["offtarget_files"] += 1
                require_self0 = fp.name.startswith(PACK_C_OFFTARGET_PREFIXES)
                for r in ivs:
                    pm0 = int(r.get("premRNA_0mm", r.get("premRNA_0mm_sense_genes", 0)) or 0)
                    if pm0 >= 1 and r.get("offtarget_safety_status") != "FAIL_EXACT_0MM_OFFTARGET":
                        msg = f"OFFTARGET_0MM_MASKED: {rel} interval={r.get('interval_id')}"
                        if is_frozen_phase:
                            legacy_notes.append(f"FROZEN_LEGACY_RULE: {msg}")
                        else:
                            errors.append(msg)
                    if require_self0 and int(r.get("on_target_0mm_self_hits") or 0) < 1:
                        errors.append(f"OFFTARGET_SELF0_MISSING: {rel} interval={r.get('interval_id')}")

        # 4. AST-resolved mtime staleness check (for active non-frozen outputs)
        prod = producers.get(fp.name)
        if prod is not None and not is_frozen_phase:
            script_fp, dep_fps = prod
            out_mt = fp.stat().st_mtime
            for dep in [script_fp, *dep_fps]:
                delta = dep.stat().st_mtime - out_mt
                if delta > mtime_tolerance_s:
                    stale.append({
                        "output": rel,
                        "newer_dep": dep.relative_to(root).as_posix(),
                        "delta_seconds": round(delta, 1),
                    })

    # 5. Biosecurity check across all work/*/cache/*.json
    for cfp in sorted(work_root.glob("*/cache/*.json")):
        contracts_checked["cache_files"] += 1
        if SEQ_GUARD_RE.search(cfp.read_text(encoding="utf-8", errors="ignore")):
            errors.append(f"BIOSECURITY_HIT_CACHE: {cfp.relative_to(root).as_posix()}")

    if strict_mtime:
        for s in stale:
            errors.append(f"STALE_OUTPUT: {s['output']} older than {s['newer_dep']} by {s['delta_seconds']}s")

    return {
        "scope": scope,
        "strict_mtime": strict_mtime,
        "n_outputs_checked": len(scoped),
        "contracts_checked": contracts_checked,
        "stale": stale,
        "legacy_notes": legacy_notes,
        "errors": errors,
        "passed": len(errors) == 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify work/*/outputs/*.json RFC-8259, biosecurity, contracts, and staleness.")
    parser.add_argument("--scope", choices=("active", "all"), default="active")
    parser.add_argument("--strict-mtime", action="store_true", help="Fail if any output JSON is older than its script or imported src/carbon_als module.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)

    rep = audit_work_outputs(args.root, scope=args.scope, strict_mtime=args.strict_mtime)
    if rep["legacy_notes"]:
        print(f"NOTE: {len(rep['legacy_notes'])} frozen historical release rule note(s) (queued for next release):")
        for n in rep["legacy_notes"]:
            print(f"  - {n}")
    if rep["stale"] and not args.strict_mtime:
        print(f"WARN: {len(rep['stale'])} stale output dependency link(s) (re-run or pass --strict-mtime to fail):")
        for s in rep["stale"]:
            print(f"  - {s['output']} < {s['newer_dep']} (+{s['delta_seconds']}s)")
    if rep["errors"]:
        print(f"FAIL [{rep['scope']}]: {len(rep['errors'])} error(s) across {rep['n_outputs_checked']} JSON outputs:")
        for e in rep["errors"]:
            print(f"  - {e}")
        return 1
    cc = rep["contracts_checked"]
    print(
        f"PASS [{rep['scope']}]: {rep['n_outputs_checked']}/{rep['n_outputs_checked']} work JSON outputs "
        f"(AlphaGenome={cc['alphagenome_files']}, off-target={cc['offtarget_files']}, caches={cc['cache_files']}, "
        f"stale={len(rep['stale'])}, strict_mtime={rep['strict_mtime']}, 0 errors)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
