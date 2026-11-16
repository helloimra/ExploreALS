"""Download Phase 2 human SARM1 PDB structures via HTTPS guardrail and parse ChEMBL SARM1 + CNS-MPO scaffolds."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))
from carbon_als.loaders import download_https_structure  # noqa: E402

OUT = ROOT / "work" / "phase2" / "track2_sarm1_ykt6_allostery" / "outputs"
PDB_DIR = ROOT / "data" / "pharmacology_structures" / "phase2_pdb"
HEADERS = {"User-Agent": "CarbonALS-Phase2/1.0", "Accept": "application/json"}


def http_json(url: str, timeout_s: int = 15) -> dict | None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"WARN: {url[:90]} -> {type(exc).__name__}: {exc}")
        return None


def stage_sarm1_pdbs() -> dict[str, str]:
    PDB_DIR.mkdir(parents=True, exist_ok=True)
    pdb_ids = ["7DJT", "7ANW", "7NAL", "9TZY"]
    staged = {}
    for pid in pdb_ids:
        dest = PDB_DIR / f"pdb_0000{pid.lower()}.cif"
        if not dest.exists() or dest.stat().st_size < 10_000:
            download_https_structure(f"https://files.rcsb.org/download/{pid}.cif", dest)
        staged[pid] = str(dest)
    return staged


def fetch_chembl_quantitative_and_cns() -> dict:
    base = "https://www.ebi.ac.uk/chembl/api/data"
    # Fetch quantitative IC50/EC50/Ki records for human SARM1 (CHEMBL4523350)
    q_url = f"{base}/activity.json?target_chembl_id=CHEMBL4523350&pchembl_value__isnull=false&limit=200"
    q_res = http_json(q_url, timeout_s=15) or {}
    q_acts = q_res.get("activities") or []

    mol_ids = sorted({a["molecule_chembl_id"] for a in q_acts if a.get("molecule_chembl_id")})
    mol_props: dict[str, dict] = {}
    if mol_ids:
        m_url = f"{base}/molecule.json?molecule_chembl_id__in={','.join(mol_ids[:60])}&limit=100"
        m_res = http_json(m_url, timeout_s=15) or {}
        for m in m_res.get("molecules") or []:
            mol_props[m["molecule_chembl_id"]] = {
                "pref_name": m.get("pref_name"),
                "max_phase": m.get("max_phase"),
                "properties": m.get("molecule_properties") or {},
                "smiles": (m.get("molecule_structures") or {}).get("canonical_smiles"),
            }

    enriched = []
    for a in q_acts:
        mid = a.get("molecule_chembl_id")
        mp = mol_props.get(mid, {})
        props = mp.get("properties") or {}
        enriched.append({
            "molecule_chembl_id": mid,
            "pref_name": mp.get("pref_name") or a.get("molecule_pref_name"),
            "standard_type": a.get("standard_type"),
            "standard_value_nM": float(a["standard_value"]) if a.get("standard_value") else None,
            "pchembl_value": float(a["pchembl_value"]) if a.get("pchembl_value") else None,
            "assay_description": a.get("assay_description"),
            "document_year": a.get("document_year"),
            "mw": float(props["mw_freebase"]) if props.get("mw_freebase") else None,
            "psa": float(props["psa"]) if props.get("psa") else None,
            "alogp": float(props["alogp"]) if props.get("alogp") else None,
            "hbd": props.get("hbd"),
            "smiles": a.get("canonical_smiles") or mp.get("smiles"),
        })
    enriched.sort(key=lambda r: (r["standard_value_nM"] if r["standard_value_nM"] is not None else 1e9))
    (OUT / "sarm1_chembl_quantitative.json").write_text(json.dumps(enriched, indent=2), encoding="utf-8")

    # Approved CNS-penetrant hydrophobic-groove chaperone scaffolds for YKT6 p.Tyr64Cys cavity
    frag_url = (
        f"{base}/molecule.json?molecule_properties__mw_freebase__gte=175"
        "&molecule_properties__mw_freebase__lte=285&molecule_properties__psa__gte=25"
        "&molecule_properties__psa__lte=65&molecule_properties__alogp__gte=2.0"
        "&molecule_properties__alogp__lte=3.5&molecule_properties__hbd__lte=2&max_phase=4&limit=60"
    )
    frag_res = http_json(frag_url, timeout_s=15) or {}
    frags = []
    for m in frag_res.get("molecules") or []:
        pr = m.get("molecule_properties") or {}
        frags.append({
            "molecule_chembl_id": m.get("molecule_chembl_id"),
            "pref_name": m.get("pref_name"),
            "mw": float(pr["mw_freebase"]) if pr.get("mw_freebase") else None,
            "psa": float(pr["psa"]) if pr.get("psa") else None,
            "alogp": float(pr["alogp"]) if pr.get("alogp") else None,
            "hbd": pr.get("hbd"),
            "aromatic_rings": pr.get("aromatic_rings"),
            "heavy_atoms": pr.get("heavy_atoms"),
            "smiles": (m.get("molecule_structures") or {}).get("canonical_smiles"),
        })
    (OUT / "ykt6_cns_chaperone_candidates_chembl.json").write_text(json.dumps(frags, indent=2), encoding="utf-8")

    # Fetch 2025-2026 BEXi paradoxical activation abstracts from Europe PMC
    epmc = {}
    for pmid in ["42156967", "40529094", "41948869", "33944777"]:
        r = http_json(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{pmid}&resultType=core&format=json")
        hit = (((r or {}).get("resultList") or {}).get("result") or [{}])[0]
        epmc[pmid] = {"title": hit.get("title"), "year": hit.get("pubYear"), "journal": (hit.get("journalInfo") or {}).get("journal", {}).get("title"), "abstract": hit.get("abstractText")}
    (OUT / "sarm1_bexi_abstracts.json").write_text(json.dumps(epmc, indent=2), encoding="utf-8")
    return {"quantitative_sarm1_count": len(enriched), "unique_sarm1_mols": len(mol_ids), "ykt6_cns_scaffolds": len(frags)}


if __name__ == "__main__":
    staged_files = stage_sarm1_pdbs()
    stats = fetch_chembl_quantitative_and_cns()
    print(json.dumps({"staged": staged_files, "stats": stats}, indent=2))
