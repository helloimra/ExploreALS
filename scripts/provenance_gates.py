"""Deterministic Wave-2 provenance, numeric-hygiene & external-ID validators for CarbonALS."""

from __future__ import annotations

import math
import re

BANNED_PLACEHOLDERS = {"na", "n/a", "null", "none", "nan", "0.99", "tbd", "todo", "-"}
BAD_CHEMBL_RE = re.compile(r"\bCHEMBL(?:_[A-Za-z0-9]+|[0-9]*[A-Za-z]+[0-9A-Za-z]*)\b")
BAD_NCT_RE = re.compile(r"\bNCT(?![0-9]{8}\b)[0-9]{3,12}\b")
BAD_PMID_RE = re.compile(r"\bPMID:\s*(?![0-9]{5,9}\b)[A-Za-z0-9_-]+", re.IGNORECASE)


def _parse_prob(raw: str, field: str, eid: str, errors: list[str]) -> float | None:
    val_s = raw.strip()
    if not val_s:
        return None
    if val_s.lower() in BANNED_PLACEHOLDERS:
        errors.append(f"PROVENANCE VIOLATION on {eid}: banned placeholder '{val_s}' in {field}")
        return None
    try:
        v = float(val_s)
    except ValueError:
        errors.append(f"PROVENANCE VIOLATION on {eid}: non-numeric {field}='{val_s}' (single-contrast float required)")
        return None
    if not math.isfinite(v) or v < 0.0 or v > 1.0:
        errors.append(f"PROVENANCE VIOLATION on {eid}: {field}={v} out of [0, 1] probability bounds")
        return None
    return v


def verify_provenance_gates(
    intake: list[dict[str, str]],
    evidence: list[dict[str, str]],
    runs: list[dict[str, str]],
) -> list[str]:
    errors: list[str] = []

    for r in intake:
        cid = r["carbon_id"]
        ids_col = r.get("genes_or_drug_ids", "")
        if BAD_CHEMBL_RE.search(ids_col) or BAD_NCT_RE.search(ids_col):
            errors.append(f"INTAKE ID VIOLATION on {cid}: malformed ChEMBL/NCT token in '{ids_col}'")

    for ar in runs:
        rid = ar["analysis_run_id"]
        rv = (ar.get("reproduced_verified") or "").strip()
        if rv not in {"yes", "no"}:
            errors.append(f"RUN BOOLEAN VIOLATION on {rid}: reproduced_verified='{rv}' must be 'yes' or 'no'")

    for ev in evidence:
        eid = ev["evidence_id"]
        pval = _parse_prob(ev.get("p_value", ""), "p_value", eid, errors)
        qval = _parse_prob(ev.get("fdr_or_adjusted_p", ""), "fdr_or_adjusted_p", eid, errors)
        if pval is not None and qval is not None and pval > qval + 1e-9:
            errors.append(
                f"CONTRAST MIXING VIOLATION on {eid}: p_value ({pval}) > fdr_or_adjusted_p ({qval}); "
                "cannot mix raw p from one contrast with FDR/adjusted p from another"
            )

        sn = (ev.get("sample_size_n") or "").strip()
        if sn:
            if sn.lower() in BANNED_PLACEHOLDERS:
                errors.append(f"PROVENANCE VIOLATION on {eid}: banned placeholder '{sn}' in sample_size_n")
            else:
                try:
                    n_int = int(sn)
                    if n_int < 1:
                        errors.append(f"PROVENANCE VIOLATION on {eid}: sample_size_n={n_int} must be >= 1")
                except ValueError:
                    errors.append(
                        f"PROVENANCE VIOLATION on {eid}: sample_size_n='{sn}' must be a single integer donor count"
                    )

        blob = f"{ev.get('source_id_or_locator', '')} {ev.get('source_dataset_or_id', '')} {ev.get('notes', '')}"
        if BAD_CHEMBL_RE.search(blob) or BAD_NCT_RE.search(blob) or BAD_PMID_RE.search(blob):
            errors.append(f"EXTERNAL ID VIOLATION on {eid}: malformed ChEMBL/NCT/PMID identifier in source/notes")

    return errors
