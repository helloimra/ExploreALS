"""Windows-safe Google Science skill CLI runner (zero grandchild pipe hangs) and ChEMBL filter helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from typing import Any


def sanitize_chembl_filters(filters: list[str]) -> list[str]:
    """Convert error-prone ChEMBL '__range=low,high' tokens into validated '__gte=low' + '__lte=high'."""
    out: list[str] = []
    for flt in filters:
        if "__range=" in flt:
            lhs, rhs = flt.split("__range=", 1)
            parts = [p.strip() for p in rhs.split(",")]
            if len(parts) != 2:
                raise ValueError(f"Malformed ChEMBL __range filter '{flt}'; expected low,high")
            out.append(f"{lhs}__gte={parts[0]}")
            out.append(f"{lhs}__lte={parts[1]}")
        else:
            out.append(flt)
    return out


def run_skill_cli_to_file(
    script_path: Path,
    subcommand_and_args: list[str],
    output_path: Path,
    timeout_sec: int = 45,
    use_cache: bool = True,
) -> Any:
    """Execute a Google Science skill script via 'uv run' without pipe-capture deadlocks on Windows."""
    if use_cache and output_path.is_file() and output_path.stat().st_size > 2:
        try:
            return json.loads(output_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            output_path.unlink(missing_ok=True)
    if not script_path.is_file():
        raise FileNotFoundError(f"Skill CLI script not found: {script_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    cmd = ["uv", "run", str(script_path), *subcommand_and_args, "--output", str(output_path)]
    child_env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    skill_root = script_path.parent.parent if script_path.parent.name == "scripts" else script_path.parent
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0
    proc = subprocess.Popen(
        cmd,
        cwd=str(skill_root),
        env=child_env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    try:
        rc = proc.wait(timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            proc.kill()
        raise TimeoutError(f"Skill CLI timed out after {timeout_sec}s: {' '.join(cmd)}") from exc

    if rc != 0 or not output_path.is_file():
        raise RuntimeError(f"Skill CLI exited with code {rc} (output exists={output_path.is_file()}): {' '.join(cmd)}")
    return json.loads(output_path.read_text(encoding="utf-8"))


def parse_json_ignoring_banner(raw_text: str) -> Any:
    """Extract and parse JSON payload even when a CLI tool prints '[NOTICE]' or status banners before JSON."""
    for idx, ch in enumerate(raw_text):
        if ch in "{[":
            try:
                return json.loads(raw_text[idx:])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"No valid JSON payload found in CLI output: {raw_text[:160]!r}")


def run_skill_cli_stdout_json(
    script_path: Path,
    subcommand_and_args: list[str],
    cache_path: Path,
    timeout_sec: int = 45,
    use_cache: bool = True,
) -> Any:
    """Run a CLI tool that emits JSON to stdout (no --output flag) via file handle to avoid Windows pipe hangs."""
    if use_cache and cache_path.is_file() and cache_path.stat().st_size > 2:
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cache_path.unlink(missing_ok=True)
    if not script_path.is_file():
        raise FileNotFoundError(f"Skill CLI script not found: {script_path}")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    raw_log = cache_path.with_suffix(".stdout.tmp")
    cmd = ["uv", "run", str(script_path), *subcommand_and_args]
    child_env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    skill_root = script_path.parent.parent if script_path.parent.name == "scripts" else script_path.parent
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0
    with raw_log.open("w", encoding="utf-8") as stdout_fh:
        proc = subprocess.Popen(
            cmd,
            cwd=str(skill_root),
            env=child_env,
            stdin=subprocess.DEVNULL,
            stdout=stdout_fh,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        rc = proc.wait(timeout=timeout_sec)
    try:
        if rc != 0:
            raise RuntimeError(f"Skill CLI exited with code {rc}: {' '.join(cmd)}")
        parsed = parse_json_ignoring_banner(raw_log.read_text(encoding="utf-8"))
    finally:
        raw_log.unlink(missing_ok=True)
    cache_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
    return parsed


def run_skill_cli_raw_output(
    script_path: Path,
    subcommand_and_args: list[str],
    output_path: Path,
    timeout_sec: int = 180,
    use_cache: bool = True,
    min_bytes: int = 64,
) -> Path:
    """Execute a Google Science skill CLI writing non-JSON (--output TSV/CSV) safely without Windows pipe hangs."""
    if use_cache and output_path.is_file() and output_path.stat().st_size >= min_bytes:
        return output_path
    if not script_path.is_file():
        raise FileNotFoundError(f"Skill CLI script not found: {script_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)
    cmd = ["uv", "run", str(script_path), *subcommand_and_args, "--output", str(output_path)]
    child_env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    skill_root = script_path.parent.parent if script_path.parent.name == "scripts" else script_path.parent
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0
    proc = subprocess.Popen(
        cmd, cwd=str(skill_root), env=child_env,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    rc = proc.wait(timeout=timeout_sec)
    if rc != 0 or not output_path.is_file():
        raise RuntimeError(f"Skill CLI exited with code {rc}: {' '.join(cmd)}")
    return output_path


def run_skill_cli_stdout_text(
    script_path: Path,
    subcommand_and_args: list[str],
    cache_path: Path,
    timeout_sec: int = 45,
    use_cache: bool = True,
) -> str:
    """Execute a plain-text stdout Google Science skill CLI safely via cached file redirect."""
    if use_cache and cache_path.is_file() and cache_path.stat().st_size > 4:
        return cache_path.read_text(encoding="utf-8").strip()
    if not script_path.is_file():
        raise FileNotFoundError(f"Skill CLI script not found: {script_path}")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["uv", "run", str(script_path), *subcommand_and_args]
    child_env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    skill_root = script_path.parent.parent if script_path.parent.name == "scripts" else script_path.parent
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0
    with cache_path.open("w", encoding="utf-8") as out_fh:
        proc = subprocess.Popen(
            cmd, cwd=str(skill_root), env=child_env,
            stdin=subprocess.DEVNULL, stdout=out_fh, stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        rc = proc.wait(timeout=timeout_sec)
    if rc != 0:
        cache_path.unlink(missing_ok=True)
        raise RuntimeError(f"Skill CLI exited with code {rc}: {' '.join(cmd)}")
    return cache_path.read_text(encoding="utf-8").strip()


def filter_offtarget_liabilities(
    candidates: list[dict[str, Any]],
    offtarget_min_ic50_nm_by_chembl: dict[str, float],
    min_allowed_ic50_nm: float = 1000.0,
) -> list[dict[str, Any]]:
    """Annotate and filter out promiscuous drugs/probes with sub-micromolar human off-target bioactivities."""
    clean: list[dict[str, Any]] = []
    for mol in candidates:
        cid = str(mol.get("molecule_chembl_id", ""))
        min_ic50 = offtarget_min_ic50_nm_by_chembl.get(cid)
        if min_ic50 is not None and min_ic50 < min_allowed_ic50_nm:
            continue
        enriched = dict(mol)
        enriched["min_known_offtarget_ic50_nM"] = min_ic50
        clean.append(enriched)
    return clean
