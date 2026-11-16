"""Stage PDB 2Z0D (ATG4B-LC3B) + 1XFD (DPP6), compute 3D contacts, and query OpenTargets/DepMap, ClinicalTrials.gov v2 & EuropePMC."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import urllib.parse
import urllib.request
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from carbon_als.loaders import download_https_structure  # noqa: E402
from carbon_als.mmcif_parser import load_mmcif_structure  # noqa: E402

CACHE_OUT = ROOT / "work" / "phase3b_denovo_discovery" / "cache" / "external_priors_and_structures.json"
PDB_DIR = ROOT / "data" / "pharmacology_structures" / "phase3b_pdb"
_ART_ENV = os.environ.get("CARBON_ARTIFACT_STRUCT_DIR", "").strip()
ART_STRUCT_DIR = Path(_ART_ENV) if _ART_ENV else None
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)

TARGETS_ENSG: dict[str, str] = {
    "ATG4B": "ENSG00000168397", "KALRN": "ENSG00000160145", "PTPRT": "ENSG00000196090",
    "CELF5": "ENSG00000161082", "PRUNE2": "ENSG00000106772", "PFKP": "ENSG00000067057",
    "TRAPPC12": "ENSG00000171853", "ELK1": "ENSG00000126767", "DLGAP1": "ENSG00000170579",
    "DPP6": "ENSG00000130226", "DPP10": "ENSG00000175497", "CFL1": "ENSG00000172757",
    "MAOB": "ENSG00000069535", "C5AR1": "ENSG00000197405",
}
OT_GQL = """query($id:String!){target(ensemblId:$id){id approvedSymbol isEssential tractability{label modality value} safetyLiabilities{event biosamples{tissueLabel}} depMapEssentiality{screens{geneEffect}}}}"""


def _http_json(url: str, post_body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = json.dumps(post_body).encode("utf-8") if post_body is not None else None
    hdrs = {"User-Agent": "CarbonALS/0.5-OpenScience", "Accept": "application/json"}
    if data is not None:
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _sha256(fp: Path) -> str:
    h = hashlib.sha256()
    with fp.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _analyze_2z0d_and_1xfd(p_2z0d: Path, p_1xfd: Path) -> dict[str, Any]:
    s2 = load_mmcif_structure(p_2z0d)
    rg2 = s2.residue_groups(include_modified=True)
    chains2 = sorted({c for c, _, _ in rg2})
    a_atoms = [a for (c, _, _), al in rg2.items() if c == "A" for a in al]
    b_atoms = [a for (c, _, _), al in rg2.items() if c == "B" for a in al]
    contacts_2z0d = set()
    gly120_min_a = 99.0
    for ba in b_atoms:
        bc = ba.coord
        for aa in a_atoms:
            d = float(np.linalg.norm(bc - aa.coord))
            if d <= 4.2:
                contacts_2z0d.add((aa.seq_id, aa.comp_id, ba.seq_id, ba.comp_id))
            if ba.seq_id == 120 and aa.seq_id in {74, 278, 280} and d < gly120_min_a:
                gly120_min_a = d
    s1 = load_mmcif_structure(p_1xfd)
    rg1 = s1.residue_groups(include_modified=True)
    ch_a = [a for (c, _, _), al in rg1.items() if c == "A" for a in al if a.atom_name == "CA"]
    ch_b = [a for (c, _, _), al in rg1.items() if c == "B" for a in al if a.atom_name == "CA"]
    dimer_ca_le8 = sum(1 for a in ch_a for b in ch_b if float(np.linalg.norm(a.coord - b.coord)) <= 8.0)
    asp_nucleophile = [f"{comp}{sid}" for (c, sid, comp) in sorted(rg1) if c == "A" and sid in {712, 729, 757, 807, 835}]
    return {
        "PDB_2Z0D_ATG4B_LC3B": {
            "chains": chains2, "n_polymer_atoms": len(s2.polymer_atoms),
            "interchain_contact_pairs_le_4p2A": len(contacts_2z0d),
            "triad_to_LC3B_Gly120_min_dist_A": round(gly120_min_a, 2),
            "catalytic_cleft_contacts": [f"A:{c1}{s1}-B:{c2}{s2_id}" for s1, c1, s2_id, c2 in sorted(contacts_2z0d) if s2_id in {119, 120, 121}][:12],
        },
        "PDB_1XFD_DPP6_DIMER": {
            "chains": sorted({c for c, _, _ in rg1}), "n_polymer_atoms": len(s1.polymer_atoms),
            "homodimer_CA_pairs_le_8A": dimer_ca_le8, "hydrolase_pocket_residues_sample": asp_nucleophile,
        },
    }


def main() -> None:
    CACHE_OUT.parent.mkdir(parents=True, exist_ok=True)
    PDB_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, Any] = {"als_clinical_trials": {}, "key_study_details": {}, "opentargets_depmap": {}, "europepmc": {}, "staged_pdb": {}, "structure_metrics": {}}

    for intr in ("rasagiline", "selegiline", "lamotrigine", "acetylcysteine", "dolutegravir", "Triumeq", "Coenzyme Q10", "L-serine", "PMX205", "avacopan", "ATG4B", "KALRN", "PTPRT", "TRAPPC12", "ELK1", "DLGAP1", "DPP6"):
        q = urllib.parse.urlencode({"query.cond": "amyotrophic lateral sclerosis", "query.intr": intr, "pageSize": "10", "countTotal": "true"})
        d = _http_json(f"https://clinicaltrials.gov/api/v2/studies?{q}")
        out["als_clinical_trials"][intr] = {
            "total_count": int(d.get("totalCount", len(d.get("studies", [])))),
            "studies": [{"nct_id": s["protocolSection"]["identificationModule"]["nctId"], "status": s["protocolSection"]["statusModule"]["overallStatus"],
                         "phases": s["protocolSection"].get("designModule", {}).get("phases", []),
                         "enrollment": s["protocolSection"].get("designModule", {}).get("enrollmentInfo", {}).get("count")} for s in d.get("studies", [])],
        }
    for nct in ("NCT05193994", "NCT06658977", "NCT01879241", "NCT01786603", "NCT00243932", "NCT03580616"):
        st = _http_json(f"https://clinicaltrials.gov/api/v2/studies/{nct}")["protocolSection"]
        out["key_study_details"][nct] = {
            "title": st["identificationModule"].get("briefTitle"), "status": st["statusModule"].get("overallStatus"),
            "why_stopped": st["statusModule"].get("whyStopped", "NONE"),
            "completion_date": (st["statusModule"].get("completionDateStruct") or {}).get("date"),
            "enrollment": (st.get("designModule", {}).get("enrollmentInfo") or {}).get("count"),
        }

    for sym, ensg in TARGETS_ENSG.items():
        t = (_http_json("https://api.platform.opentargets.org/api/v4/graphql", {"query": OT_GQL, "variables": {"id": ensg}}).get("data") or {}).get("target") or {}
        effs = [float(sc["geneEffect"]) for blk in (t.get("depMapEssentiality") or []) for sc in (blk.get("screens") or []) if sc.get("geneEffect") is not None]
        arr = np.array(effs, dtype=float) if effs else np.array([], dtype=float)
        out["opentargets_depmap"][sym] = {
            "ensembl_id": ensg, "ot_is_essential": bool(t.get("isEssential", False)),
            "n_depmap_lines": int(len(arr)), "median_chronos": round(float(np.median(arr)), 4) if len(arr) else None,
            "p10_chronos": round(float(np.percentile(arr, 10)), 4) if len(arr) else None,
            "pct_lines_lt_minus1": round(100.0 * float(np.mean(arr < -1.0)), 2) if len(arr) else None,
            "tractability_pos": [f"{x['modality']}:{x['label']}" for x in (t.get("tractability") or []) if x.get("value") is True],
            "safety_events": sorted({str(s.get("event")) for s in (t.get("safetyLiabilities") or []) if s.get("event")}),
        }

    pmids = "39305312,42063624,29934198,37975796,7906190,12807386,7763202,9443715,8195821,18084291,19525032,38381392,21943606,28128456,41187881,19743457,27589995,19322194,15476821"
    esum = _http_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmids}&retmode=json").get("result", {})
    out["europepmc"]["verified_pmids"] = [
        {"pmid": pid, "year": str(esum[pid].get("pubdate", ""))[:4], "source": esum[pid].get("source"),
         "title": SEQ_GUARD_RE.sub("[REDACTED]", str(esum[pid].get("title", ""))), "europepmc_url": f"https://europepmc.org/article/MED/{pid}"}
        for pid in pmids.split(",") if pid in esum
    ]

    pdb_specs = [
        ("DS_PDB_2Z0D", "2Z0D", "pdb_00002z0d.cif", "RCSB_PDB:2Z0D;PMID:19322194;DOI:10.1038/emboj.2009.80", "DN-01", "Satoo et al. 2009 2.00A crystal structure of human ATG4B (H280A) catalytic triad bound to LC3B C-terminal tail"),
        ("DS_PDB_1XFD", "1XFD", "pdb_00001xfd.cif", "RCSB_PDB:1XFD;PMID:15476821;DOI:10.1016/j.jmb.2004.09.003", "DN-10", "Strop et al. 2004 2.65A crystal structure of human DPP6 extracellular beta-propeller and non-catalytic hydrolase homodimer"),
    ]
    manifest_fp = ROOT / "registries" / "datasets_manifest.csv"
    with manifest_fp.open(encoding="utf-8", newline="") as fh:
        mr = csv.DictReader(fh)
        m_fields, m_rows = list(mr.fieldnames or []), list(mr)
    add_by_id: dict[str, dict[str, str]] = {}
    for ds_id, code, fn, acc, cand, desc in pdb_specs:
        dest = PDB_DIR / fn
        download_https_structure(f"https://files.rcsb.org/download/{code}.cif", dest)
        if ART_STRUCT_DIR is not None and ART_STRUCT_DIR.exists():
            shutil.copy2(dest, ART_STRUCT_DIR / fn)
        sha = _sha256(dest)
        out["staged_pdb"][ds_id] = {"pdb_id": code, "relpath": dest.relative_to(ROOT).as_posix(), "size_bytes": dest.stat().st_size, "sha256": sha}
        add_by_id[ds_id] = {"dataset_id": ds_id, "domain": "pharmacology_structures", "local_relpath": dest.relative_to(ROOT).as_posix(),
                            "upstream_explore_relpath": "NONE_PHASE3B_PRIMARY", "accession_or_doi": acc, "license_or_access": "CC0 1.0 Public Domain",
                            "size_bytes": str(dest.stat().st_size), "sha256": sha, "relevant_candidates": cand, "description": desc}
    existing_ids = {r["dataset_id"] for r in m_rows}
    updated_m = [{**r, **add_by_id[r["dataset_id"]]} if r["dataset_id"] in add_by_id else r for r in m_rows]
    updated_m.extend(v for k, v in add_by_id.items() if k not in existing_ids)
    with manifest_fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=m_fields)
        w.writeheader()
        w.writerows(updated_m)

    out["structure_metrics"] = _analyze_2z0d_and_1xfd(PDB_DIR / "pdb_00002z0d.cif", PDB_DIR / "pdb_00001xfd.cif")
    txt = json.dumps(out, indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(txt), "Biosecurity sequence guard triggered!"
    CACHE_OUT.write_text(txt, encoding="utf-8")
    print("OK:", json.dumps({"n_ot": len(out["opentargets_depmap"]), "light2": out["key_study_details"]["NCT05193994"], "struct": out["structure_metrics"]}, indent=2))


if __name__ == "__main__":
    main()
