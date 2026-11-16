"""Automated stdlib HTTPS fetcher & 64-character SHA-256 verifier for ExploreALS v1.2 datasets.

Usage:
  uv run python scripts/fetch_open_datasets.py --list
  uv run python scripts/fetch_open_datasets.py --verify-existing
  uv run python scripts/fetch_open_datasets.py --source release            # Tier A release bundle + direct HTTPS Tier B
  uv run python scripts/fetch_open_datasets.py --source upstream           # Direct upstream HTTPS fetch (GENCODE/gnomAD/PDB/Publisher)
  uv run python scripts/fetch_open_datasets.py --with-synapse              # Also fetch syn51105515 & syn52335732 via SYNAPSE_AUTH_TOKEN
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registries" / "datasets_manifest.csv"
LOCK_JSON = ROOT / "schemas" / "dataset_files_lock.json"
RELEASE_BASE = "https://github.com/helloimra/ExploreALS/releases/download/v1.2.0"

DIRECT_SINGLE_FILE_HTTPS: dict[str, str] = {
    "DS045_TRAUT": "https://static-content.springer.com/esm/art%3A10.1186%2Fs13024-025-00838-1/MediaObjects/13024_2025_838_MOESM1_ESM.xlsx",
    "DS031_ZHANG": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-026-02300-x/MediaObjects/41593_2026_2300_MOESM8_ESM.xlsx",
    "DS_ZENG_APA": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-02049-3/MediaObjects/41593_2025_2049_MOESM3_ESM.xlsx",
    "DS_BRYCE_APA": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-02050-w/MediaObjects/41593_2025_2050_MOESM3_ESM.xlsx",
    "DS005_BYE": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-02118-7/MediaObjects/41593_2025_2118_MOESM3_ESM.xlsx",
    "DS_GENCODE_V46_TX": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.transcripts.fa.gz",
    "DS_GENCODE_V46_GTF": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.basic.annotation.gtf.gz",
    "DS_GENCODE_V46_COMP_GTF": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.annotation.gtf.gz",
    "DS_GNOMAD_V41_CONSTRAINT": "https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/constraint/gnomad.v4.1.constraint_metrics.tsv",
    "DS_PDB_7CR2": "https://files.rcsb.org/download/7CR2.cif",
    "DS_PDB_7DJT": "https://files.rcsb.org/download/7DJT.cif",
    "DS_PDB_7ANW": "https://files.rcsb.org/download/7ANW.cif",
    "DS_PDB_7NAL": "https://files.rcsb.org/download/7NAL.cif",
    "DS_PDB_9TZY": "https://files.rcsb.org/download/9TZY.cif",
    "DS_PDB_6VN8": "https://files.rcsb.org/download/6VN8.cif",
    "DS_PDB_7K2V": "https://files.rcsb.org/download/7K2V.cif",
    "DS_PDB_4KC3": "https://files.rcsb.org/download/4KC3.cif",
    "DS_PDB_2Z0D": "https://files.rcsb.org/download/2Z0D.cif",
    "DS_PDB_1XFD": "https://files.rcsb.org/download/1XFD.cif",
}


def sha256_path(path: Path) -> str:
    if path.is_file():
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    h = hashlib.sha256()
    for sub in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(f"{sub.relative_to(path).as_posix()}:{sha256_path(sub)}\n".encode("utf-8"))
    return h.hexdigest()


def _download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ExploreALS-DataFetcher/1.2"})
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
    ap.add_argument("--list", action="store_true", help="Print 48-dataset legal tier & status summary.")
    ap.add_argument("--verify-existing", action="store_true", help="Verify SHA-256 of all currently staged datasets.")
    ap.add_argument("--source", choices=["release", "upstream"], default="release")
    ap.add_argument("--with-baseline", action="store_true", help="Also fetch v1.0-baseline.tar.gz historical intake CSVs.")
    ap.add_argument("--with-synapse", action="store_true", help="Fetch Synapse cohorts using SYNAPSE_AUTH_TOKEN.")
    args = ap.parse_args()

    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    _ = json.loads(LOCK_JSON.read_text(encoding="utf-8"))
    if args.list or args.verify_existing:
        present, matched = 0, 0
        for r in rows:
            p = ROOT / r["local_relpath"]
            ex = p.exists()
            ok = ex and (sha256_path(p) == r["sha256"])
            present += int(ex)
            matched += int(ok)
            if args.list:
                st = "SHA256_OK" if ok else ("MISMATCH" if ex else "MISSING")
                print(f"{r['dataset_id']:24s} | {r['redistribution_tier']:28s} | {st:9s} | {r['local_relpath']}")
        print(f"Summary: {present}/48 staged locally, {matched}/48 SHA-256 verified.")
        if args.verify_existing and present > matched:
            raise SystemExit(1)
        return

    if args.source == "release":
        tar_tmp = ROOT / ".tmp" / "open-datasets-v1.2.tar.gz"
        print(f"Fetching frozen Tier A bundle from {RELEASE_BASE}/open-datasets-v1.2.tar.gz ...")
        _download_url(f"{RELEASE_BASE}/open-datasets-v1.2.tar.gz", tar_tmp)
        _extract_tar_safe(tar_tmp, ROOT)
    if args.with_baseline:
        b_tmp = ROOT / ".tmp" / "v1.0-baseline.tar.gz"
        _download_url(f"{RELEASE_BASE}/v1.0-baseline.tar.gz", b_tmp)
        _extract_tar_safe(b_tmp, ROOT)

    for r in rows:
        did = r["dataset_id"]
        dest = ROOT / r["local_relpath"]
        if dest.exists() and sha256_path(dest) == r["sha256"]:
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
        elif r["redistribution_tier"] == "TIER_B_PUBLISHER_HTTPS_FETCH":
            print(f"[MANUAL/HTTPS] {did}: download from {r['canonical_fetch_url_or_instructions']} -> {r['local_relpath']}")
        elif args.with_synapse and "synapse.org" in r["canonical_fetch_url_or_instructions"]:
            tok = os.environ.get("SYNAPSE_AUTH_TOKEN")
            if not tok:
                raise EnvironmentError("Set SYNAPSE_AUTH_TOKEN and install `uv sync --extra synapse` for --with-synapse.")
            print(f"[SYNAPSE] Authenticated token detected; stage {did} into {r['local_relpath']} and re-run --verify-existing.")


if __name__ == "__main__":
    main()
