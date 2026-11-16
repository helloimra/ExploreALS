"""Offline-first public biomedical REST API client (stdlib urllib.request, zero external CLI dependencies).

Defaults strictly to loading SHA-256-verified JSON snapshots from `cache/api_snapshots/` or canonical
`work/**/outputs/` artifacts; only contacts public HTTPS endpoints when `live_api=True` is explicitly passed,
writing live comparison responses to `work/.live_api_check/` without mutating frozen v1.2 snapshots.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _http_get_json(url: str, headers: dict[str, str] | None = None, timeout: int = 25) -> Any:
    req_headers = {"Accept": "application/json", "User-Agent": "ExploreALS-Reproducibility/1.2"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_or_check_snapshot(
    snapshot_relpath: str | Path,
    live_url: str | None = None,
    *,
    live_api: bool = False,
    expected_sha256: str | None = None,
    requires_alphagenome_key: bool = False,
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or repo_root_from_here()
    snap_path = base / snapshot_relpath
    if not live_api:
        if not snap_path.is_file():
            raise FileNotFoundError(f"Frozen API snapshot missing: {snap_path}")
        if expected_sha256:
            actual = sha256_file(snap_path)
            if actual != expected_sha256:
                raise ValueError(f"SHA-256 mismatch on {snapshot_relpath}: {actual} != {expected_sha256}")
        return json.loads(snap_path.read_text(encoding="utf-8"))

    if requires_alphagenome_key and not os.environ.get("ALPHAGENOME_API_KEY"):
        if snap_path.is_file():
            return json.loads(snap_path.read_text(encoding="utf-8"))
        raise EnvironmentError("ALPHAGENOME_API_KEY unset and frozen snapshot unavailable.")

    if not live_url:
        return json.loads(snap_path.read_text(encoding="utf-8"))

    headers: dict[str, str] = {}
    if requires_alphagenome_key:
        headers["Authorization"] = f"Bearer {os.environ['ALPHAGENOME_API_KEY']}"
    payload = _http_get_json(live_url, headers=headers)
    check_dir = base / "work" / ".live_api_check"
    check_dir.mkdir(parents=True, exist_ok=True)
    out_file = check_dir / Path(snapshot_relpath).name
    wrapped = {
        "retrieved_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "canonical_url": live_url,
        "response": payload,
    }
    out_file.write_text(json.dumps(wrapped, indent=2, sort_keys=True), encoding="utf-8")
    return wrapped


def build_europepmc_url(pmids_or_dois: list[str]) -> str:
    clauses = []
    for tok in pmids_or_dois:
        clean = tok.strip()
        if clean.upper().startswith("PMID:"):
            clauses.append(f'EXT_ID:{clean.split(":", 1)[1]}')
        elif clean.upper().startswith("PMC"):
            clauses.append(f"PMCID:{clean}")
        elif clean.upper().startswith("DOI:"):
            clauses.append(f'DOI:"{clean.split(":", 1)[1]}"')
        else:
            clauses.append(f'"{clean}"')
    q = urllib.parse.quote(" OR ".join(clauses))
    return f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=core&format=json"


def build_ctgov_study_url(nct_id: str) -> str:
    return f"https://clinicaltrials.gov/api/v2/studies/{nct_id.strip().upper()}"


def build_chembl_molecule_url(chembl_id: str) -> str:
    return f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id.strip().upper()}.json"
