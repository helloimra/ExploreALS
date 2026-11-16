"""Orchestrator for ExploreALS v1.2 computational replication (Level 1 Cached, 8 Flagship, or Full 49-Run DAG)."""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_py(script_rel: str, extra_args: list[str] | None = None) -> None:
    env = os.environ.copy()
    src_p = str(ROOT / "src")
    env["PYTHONPATH"] = f"{src_p}{os.pathsep}{env['PYTHONPATH']}" if env.get("PYTHONPATH") else src_p
    cmd = [sys.executable, str(ROOT / script_rel), *(extra_args or [])]
    print(f"--> Running: {' '.join(Path(c).name if i == 1 else c for i, c in enumerate(cmd))}")
    subprocess.run(cmd, cwd=str(ROOT), env=env, check=True)


def _ordered_canonical_runs(runs: list[dict[str, str]]) -> list[dict[str, str]]:
    by_id = {r["analysis_run_id"]: r for r in runs}
    ordered: list[dict[str, str]] = []
    seen: set[str] = set()
    for r in runs:
        rid = r["analysis_run_id"]
        if rid in seen:
            continue
        if rid == "RUN-P3B-003" and "RUN-P3B-004" in by_id and "RUN-P3B-004" not in seen:
            ordered.append(by_id["RUN-P3B-004"])
            seen.add("RUN-P3B-004")
        ordered.append(r)
        seen.add(rid)
    return ordered


def main() -> None:
    ap = argparse.ArgumentParser(description="Reproduce ExploreALS v1.2 gates, 8 flagship claims, or all 49 runs.")
    ap.add_argument("--cached-gates", action="store_true", help="Level 1 (<10s): verify 16 CSVs, SHA-256s, & loaders.")
    ap.add_argument("--flagship-only", action="store_true", help="Run all 8 Tier 1+2 Flagship Monograph Reproducers.")
    ap.add_argument("--all-canonical", action="store_true", help="Execute all 48 non-bootstrap canonical runs (requires staged data/).")
    args = ap.parse_args()

    if not (args.cached_gates or args.flagship_only or args.all_canonical):
        args.cached_gates = True
        args.flagship_only = True

    is_public_export = (ROOT / "docs" / "index.html").is_file() and not (ROOT / "reports" / "candidates").is_dir()

    if args.cached_gates:
        mode = "cached" if is_public_export else ("full" if (ROOT / "data" / "transcriptomics" / "nygc_d001" / "NYGC_counts.txt.gz").is_file() else "cached")
        _run_py("scripts/verify_carbon_als.py", ["--mode", mode])
        if (ROOT / "data" / "transcriptomics" / "nygc_d001" / "NYGC_counts.txt.gz").is_file():
            _run_py("scripts/test_shared_loaders.py")

    if args.flagship_only:
        flagships = sorted((ROOT / "pipelines" / "flagship").glob("reproduce_*.py"))
        assert len(flagships) == 8, f"Expected 8 flagship scripts, found {len(flagships)}"
        for fp in flagships:
            _run_py(fp.relative_to(ROOT).as_posix())

    if args.all_canonical:
        if is_public_export:
            (ROOT / "reports" / "phase3").mkdir(parents=True, exist_ok=True)
        runs = _ordered_canonical_runs(list(csv.DictReader((ROOT / "registries" / "analysis_runs.csv").open(encoding="utf-8"))))
        for r in runs:
            rid = r["analysis_run_id"]
            if rid == "CAR-RUN-000":
                print("--> [CAR-RUN-000] Bootstrap intake verified via datasets_manifest.csv SHA-256s (skipping upstream copy).")
                continue
            if rid == "RUN-P4-001":
                for patch_s in (
                    "work/phase4_final_synthesis/scripts/00b_apply_v1_1_registry_corrections.py",
                    "work/phase4_final_synthesis/scripts/00c_apply_v1_1_decisions.py",
                ):
                    if (ROOT / patch_s).is_file():
                        _run_py(patch_s)
            for s in r["script_relpath"].split(";"):
                s = s.strip()
                if not s:
                    continue
                extra = ["--public-docs-only"] if (is_public_export and s.endswith("02_render_phase4_synthesis.py")) else None
                _run_py(s, extra)
        _run_py("scripts/verify_carbon_als.py", ["--mode", "cached" if is_public_export else "full"])

    print("PASS: ExploreALS v1.2 replication sequence completed with 0 errors.")


if __name__ == "__main__":
    main()
