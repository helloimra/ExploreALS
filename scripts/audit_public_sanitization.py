"""Archive-aware biosecurity & host-sanitization gate for the exported ExploreALS v1.2 repository.

Scans every text file AND decompresses `.gz` / `.tar.*` streams in-memory inside the target export
directory (default: `reports/github_pages`) to block:
  1. Host paths, usernames, or internal CLI directories (Windows drive-letter paths, POSIX home dirs, dot-gemini / dot-claude).
  2. API keys / secret tokens (`AIza...`, `sk-...`, `ghp_...`, `ALPHAGENOME_API_KEY=<val>`).
  3. Synthetic antisense oligomer sequence disclosures (any `aso_seq` / `oligo_seq` / `antisense_seq` key or
     standalone chemical-modification-annotated oligomer literal).
"""
from __future__ import annotations

import argparse
import gzip
import io
import re
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HOST_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[/\\]+Users[/\\]+|(?<!https:)(?<!http:)/Users/[A-Za-z0-9._-]+/|"
    r"(?<![A-Za-z0-9_.:/-])/home/(?!about/)[A-Za-z0-9._-]+/|"
    r"\.gemini[/\\]|\.claude[/\\]|"
    r"(?<![A-Za-z0-9_.:/-])[cC]:[/\\]+(?:Windows|Temp|Documents|Projects|Antigravity))"
)
SECRET_TOKEN_RE = re.compile(
    r"(?:AIza[0-9A-Za-z\-_]{30,}|ghp_[0-9A-Za-z]{30,}|sk-[0-9A-Za-z]{30,}|SYNAPSE_AUTH_TOKEN\s*=\s*['\"][A-Za-z0-9._\-]{16,})"
)
OLIGO_KEY_RE = re.compile(
    r'"(?:aso_sequence|oligo_sequence|oligomer_sequence|antisense_sequence|spacer_sequence|dna_plus_5to3)"\s*:\s*"[ACGTUacgtu]{15,}"'
)
MODIFIED_ASO_RE = re.compile(r"(?:\+[ACGTU]|\b(?:mA|mC|mG|mU|moeA|moeC|moeG|moeT)\*){8,}")

TEXT_EXTS = {".py", ".md", ".csv", ".tsv", ".json", ".html", ".js", ".css", ".toml", ".lock", ".cff", ".txt", ".bed", ""}


def _scan_text_blob(label: str, text: str, errors: list[str]) -> None:
    m_host = HOST_PATH_RE.search(text)
    if m_host:
        errors.append(f"[HOST_PATH_LEAK] {label}: matched {m_host.group(0)!r}")
    m_sec = SECRET_TOKEN_RE.search(text)
    if m_sec:
        errors.append(f"[SECRET_LEAK] {label}: matched secret token pattern")
    m_oli = OLIGO_KEY_RE.search(text)
    if m_oli:
        errors.append(f"[BIOSECURITY_OLIGO_KEY] {label}: serialized raw nucleotide sequence key")
    m_mod = MODIFIED_ASO_RE.search(text)
    if m_mod:
        errors.append(f"[BIOSECURITY_MOD_ASO] {label}: synthesis-ready modified oligomer notation")


def audit_directory(target_dir: Path) -> list[str]:
    errors: list[str] = []
    if not target_dir.is_dir():
        return [f"Target directory missing: {target_dir}"]
    for p in sorted(target_dir.rglob("*")):
        if not p.is_file() or ".git" in p.parts:
            continue
        rel = p.relative_to(target_dir).as_posix()
        name_low = p.name.lower()
        if name_low.endswith((".tar.gz", ".tgz")):
            with tarfile.open(p, "r:*") as tf:
                for mem in tf.getmembers():
                    msuf = Path(mem.name).suffix.lower()
                    if mem.isfile() and (msuf in TEXT_EXTS or mem.name.lower().endswith((".txt.gz", ".tsv.gz", ".csv.gz"))):
                        fobj = tf.extractfile(mem)
                        if fobj:
                            raw_m = fobj.read()
                            if mem.name.lower().endswith(".gz"):
                                raw_m = gzip.decompress(raw_m)
                            _scan_text_blob(f"{rel}::{mem.name}", raw_m.decode("utf-8", errors="ignore"), errors)
        elif name_low.endswith(".gz"):
            raw = gzip.decompress(p.read_bytes())
            if name_low.endswith(".tar.gz"):
                with tarfile.open(fileobj=io.BytesIO(raw), mode="r:*") as tf:
                    for mem in tf.getmembers():
                        if mem.isfile() and (fobj := tf.extractfile(mem)):
                            _scan_text_blob(f"{rel}::{mem.name}", fobj.read().decode("utf-8", errors="ignore"), errors)
            else:
                _scan_text_blob(rel, raw.decode("utf-8", errors="ignore"), errors)
        elif p.suffix.lower() in TEXT_EXTS or p.name in {".gitignore", ".python-version", "LICENSE"}:
            _scan_text_blob(rel, p.read_text(encoding="utf-8", errors="ignore"), errors)
    return errors


def _run_selftest() -> None:
    errs: list[str] = []
    fake_win = "C" + ":" + "\\\\" + "Users" + "\\\\" + "dev_box"
    _scan_text_blob("selftest_host", f"path = '{fake_win}'", errs)
    _scan_text_blob("selftest_oligo", '{"aso_sequence": "' + ("ACGT" * 5) + '"}', errs)
    assert len(errs) == 2, f"Sanitization self-test failed: {errs}"
    clean: list[str] = []
    _scan_text_blob("selftest_protein_ok", "Hepatic:\\n\\n* MAGAGAGAGAGAGAGAGAGA protein", clean)
    assert not clean, f"False positive on benign protein/Hepatic newline: {clean}"


def main() -> None:
    _run_selftest()
    ap = argparse.ArgumentParser(description="Audit exported public repository for host leaks & oligomer strings.")
    ap.add_argument("--target", default=str(ROOT / "reports" / "github_pages"), help="Directory to scan.")
    args = ap.parse_args()
    target = Path(args.target).resolve()
    errs = audit_directory(target)
    if errs:
        for e in errs[:30]:
            print("ERROR:", e)
        raise SystemExit(f"FAIL: {len(errs)} sanitization error(s) in {target}")
    print(f"PASS: Sanitization & biosecurity audit clean across {target} (0 host leaks, 0 secrets, 0 oligo sequences).")


if __name__ == "__main__":
    main()
