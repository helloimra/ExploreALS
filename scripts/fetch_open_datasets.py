"""Automated stdlib HTTPS fetcher & 64-character SHA-256 verifier for ExploreALS v1.2 datasets.

Usage:
  uv run python scripts/fetch_open_datasets.py --list
  uv run python scripts/fetch_open_datasets.py --verify-existing
  uv run python scripts/fetch_open_datasets.py --source release            # Tier A release bundle + direct HTTPS Tier B
  uv run python scripts/fetch_open_datasets.py --source upstream           # Direct upstream HTTPS fetch (GENCODE/gnomAD/PDB/Publisher)
  uv run python scripts/fetch_open_datasets.py --with-synapse              # Validate SYNAPSE_AUTH_TOKEN & print Synapse CLI staging commands
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
from _fetch_recipes import DIRECT_MULTI_FILE_HTTPS, DIRECT_SINGLE_FILE_HTTPS  # noqa: E402

ROOT = SCRIPTS_DIR.parent
MANIFEST = ROOT / "registries" / "datasets_manifest.csv"
LOCK_JSON = ROOT / "schemas" / "dataset_files_lock.json"
RELEASE_BASE = "https://github.com/helloimra/ExploreALS/releases/download/v1.2.0"


def sha256_path(path: Path) -> str:
    if path.is_file():
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    h = hashlib.sha256()
    for sub in sorted((p for p in path.rglob("*") if p.is_file()), key=lambda p: p.relative_to(path).as_posix()):
        h.update(f"{sub.relative_to(path).as_posix()}:{sha256_path(sub)}\n".encode("utf-8"))
    return h.hexdigest()


def _dir_matches_lock(dest: Path, lock_entry: dict) -> bool:
    if not dest.is_dir():
        return False
    files = lock_entry.get("files") or []
    data_files = [f for f in files if Path(f["rel"]).suffix.lower() in {".csv", ".tsv", ".xlsx", ".xls", ".cif", ".bed", ".gtf", ".gz"}]
    return bool(data_files) and all((dest / f["rel"]).is_file() and sha256_path(dest / f["rel"]) == f["sha256"] for f in data_files)


def _download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ExploreALS-DataFetcher/1.2.5"})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as out:
        while chunk := resp.read(1 << 20):
            out.write(chunk)


def _extract_tar_safe(tar_path: Path, target_root: Path) -> None:
    with tarfile.open(tar_path, "r:*") as tf:
        for member in tf.getmembers():
            resolved = (target_root / member.name).resolve()
            if not str(resolved).startswith(str(target_root.resolve())):
                raise RuntimeError(f"Unsafe tar member blocked: {member.name}")
        tf.extractall(target_root)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch and SHA-256 verify ExploreALS v1.2 open datasets.")
    ap.add_argument("--list", action="store_true", help="Print 42-dataset legal tier & status summary.")
    ap.add_argument("--verify-existing", action="store_true", help="Verify SHA-256 of all currently staged datasets.")
    ap.add_argument("--source", choices=["release", "upstream"], default="release")
    ap.add_argument("--with-synapse", action="store_true", help="Validate SYNAPSE_AUTH_TOKEN and print Synapse CLI staging commands for Tier C cohorts.")
    args = ap.parse_args()

    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    lock_raw = json.loads(LOCK_JSON.read_text(encoding="utf-8"))
    lock_ds = lock_raw.get("datasets", lock_raw)
    if args.list or args.verify_existing:
        present, matched = 0, 0
        for r in rows:
            did = r["dataset_id"]
            p = ROOT / r["local_relpath"]
            ex = p.exists()
            ok = ex and (sha256_path(p) == r["sha256"] or _dir_matches_lock(p, lock_ds.get(did, {})))
            present += int(ex)
            matched += int(ok)
            if args.list:
                st = "SHA256_OK" if ok else ("MISMATCH" if ex else "MISSING")
                print(f"{did:24s} | {r['redistribution_tier']:28s} | {st:9s} | {r['local_relpath']}")
        print(f"Summary: {present}/{len(rows)} staged locally, {matched}/{len(rows)} SHA-256 verified.")
        if args.verify_existing and present > matched:
            raise SystemExit(1)
        return

    if args.source == "release":
        tar_tmp = ROOT / ".tmp" / "open-datasets-v1.2.tar.gz"
        print(f"Fetching frozen Tier A bundle from {RELEASE_BASE}/open-datasets-v1.2.tar.gz ...")
        _download_url(f"{RELEASE_BASE}/open-datasets-v1.2.tar.gz", tar_tmp)
        _extract_tar_safe(tar_tmp, ROOT)

    for r in rows:
        did = r["dataset_id"]
        dest = ROOT / r["local_relpath"]
        if dest.exists() and (sha256_path(dest) == r["sha256"] or _dir_matches_lock(dest, lock_ds.get(did, {}))):
            continue
        if did in DIRECT_SINGLE_FILE_HTTPS:
            print(f"Downloading {did} from canonical HTTPS ...")
            try:
                _download_url(DIRECT_SINGLE_FILE_HTTPS[did], dest)
                got = sha256_path(dest)
                if got != r["sha256"]:
                    print(f"[WARN] Upstream header/revision drift on {did}: got {got[:12]} vs frozen {r['sha256'][:12]}")
            except urllib.error.URLError as exc:
                print(f"[WARN] Transient HTTPS fetch error on {did} ({exc}); retry or stage manually from {DIRECT_SINGLE_FILE_HTTPS[did]}")
        elif did in DIRECT_MULTI_FILE_HTTPS:
            print(f"Downloading {did} ({len(DIRECT_MULTI_FILE_HTTPS[did])} publisher supplement files) ...")
            for rel_f, url_f in DIRECT_MULTI_FILE_HTTPS[did]:
                sub_dst = dest / rel_f
                if sub_dst.is_file():
                    continue
                try:
                    _download_url(url_f, sub_dst)
                except urllib.error.URLError as exc:
                    print(f"[WARN] Transient HTTPS fetch error on {did}/{rel_f} ({exc})")
        elif r["redistribution_tier"] == "TIER_B_PUBLISHER_HTTPS_FETCH":
            print(f"[MANUAL/HTTPS] {did}: download publisher supplement from {r['canonical_fetch_url_or_instructions']} -> {r['local_relpath']}")
        elif args.with_synapse and "synapse.org" in r["canonical_fetch_url_or_instructions"]:
            tok = os.environ.get("SYNAPSE_AUTH_TOKEN")
            if not tok:
                raise EnvironmentError("Set SYNAPSE_AUTH_TOKEN and install `uv sync --extra synapse` for --with-synapse.")
            syn_id = "syn51105515" if did == "DS003_PB" else "syn52335732"
            print(f"[SYNAPSE] Run: `uv run synapse get -r {syn_id} --downloadLocation {r['local_relpath']}` then re-run --verify-existing.")


if __name__ == "__main__":
    main()
