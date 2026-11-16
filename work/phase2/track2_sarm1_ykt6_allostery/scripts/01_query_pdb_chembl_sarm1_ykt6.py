"""Query RCSB PDB (55 human SARM1 entries) and ChEMBL REST API with strict 12s socket timeouts."""

from __future__ import annotations

import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "work" / "phase2" / "track2_sarm1_ykt6_allostery" / "outputs"
HEADERS = {"User-Agent": "CarbonALS-Phase2/1.0", "Accept": "application/json"}


def http_json(url: str, payload: dict | None = None, timeout_s: int = 12) -> dict | None:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    hdrs = {**HEADERS, **({"Content-Type": "application/json"} if data else {})}
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"WARN: {url[:85]} -> {type(exc).__name__}: {exc}")
        return None


def fetch_all_sarm1_pdb_metadata() -> list[dict]:
    entries_path = OUT / "sarm1_pdb_search.json"
    ids = [r["identifier"] for r in json.loads(entries_path.read_text(encoding="utf-8")).get("result_set", [])]
    parsed: list[dict] = []
    for i in range(0, len(ids), 30):
        chunk = ids[i : i + 30]
        gql = (
            "{ entries(entry_ids: " + json.dumps(chunk) + ") { "
            "rcsb_id struct { title } exptl { method } "
            "rcsb_entry_info { resolution_combined } "
            "rcsb_primary_citation { year pdbx_database_id_PubMed title } "
            "nonpolymer_entities { nonpolymer_comp { chem_comp { id name formula_weight } } } "
            "} }"
        )
        res = http_json("https://data.rcsb.org/graphql", payload={"query": gql}, timeout_s=15)
        if not res:
            continue
        for e in (res.get("data") or {}).get("entries") or []:
            res_list = (e.get("rcsb_entry_info") or {}).get("resolution_combined") or [None]
            ligs = []
            for np_ent in e.get("nonpolymer_entities") or []:
                cc = ((np_ent.get("nonpolymer_comp") or {}).get("chem_comp")) or {}
                if cc.get("id") and cc["id"] not in {"ZN", "MG", "NA", "CL", "CA", "SO4", "GOL", "EDO"}:
                    ligs.append({"id": cc["id"], "name": cc.get("name"), "mw": cc.get("formula_weight")})
            cit = e.get("rcsb_primary_citation") or {}
            parsed.append({
                "pdb_id": e["rcsb_id"],
                "resolution_A": res_list[0],
                "year": cit.get("year"),
                "pmid": cit.get("pdbx_database_id_PubMed"),
                "citation_title": cit.get("title"),
                "title": (e.get("struct") or {}).get("title"),
                "ligands": ligs,
            })
    parsed.sort(key=lambda r: (-(r["year"] or 0), r["resolution_A"] if r["resolution_A"] is not None else 99.0))
    (OUT / "sarm1_pdb_metadata.json").write_text(json.dumps(parsed, indent=2), encoding="utf-8")
    return parsed


def query_chembl_direct() -> dict:
    base = "https://www.ebi.ac.uk/chembl/api/data"
    s_t = http_json(f"{base}/target.json?target_components__accession=Q6SZW1&limit=5", timeout_s=12)
    y_t = http_json(f"{base}/target.json?target_components__accession=O15498&limit=5", timeout_s=12)
    s_targets = (s_t or {}).get("targets") or []
    y_targets = (y_t or {}).get("targets") or []
    if s_t is not None:
        (OUT / "sarm1_chembl_target.json").write_text(json.dumps(s_t, indent=2), encoding="utf-8")
    if y_t is not None:
        (OUT / "ykt6_chembl_target.json").write_text(json.dumps(y_t, indent=2), encoding="utf-8")

    s_acts = []
    if s_targets:
        tid = s_targets[0]["target_chembl_id"]
        act_res = http_json(f"{base}/activity.json?target_chembl_id={tid}&limit=200", timeout_s=15)
        if act_res:
            s_acts = act_res.get("activities") or []
            (OUT / "sarm1_chembl_activities.json").write_text(json.dumps(act_res, indent=2), encoding="utf-8")

    frag_q = (
        f"{base}/molecule.json?molecule_properties__mw_freebase__range=175,285"
        "&molecule_properties__psa__range=25,65&molecule_properties__alogp__range=2.0,3.5"
        "&molecule_properties__hbd__lte=2&max_phase=4&limit=50"
    )
    frag_res = http_json(frag_q, timeout_s=15)
    frags = (frag_res or {}).get("molecules") or []
    if frag_res:
        (OUT / "ykt6_cns_chaperone_candidates_chembl.json").write_text(json.dumps(frag_res, indent=2), encoding="utf-8")

    return {
        "chembl_reachable": s_t is not None,
        "sarm1_target_chembl_ids": [t["target_chembl_id"] for t in s_targets],
        "ykt6_target_chembl_ids": [t["target_chembl_id"] for t in y_targets],
        "sarm1_activity_count": len(s_acts),
        "approved_cns_fragment_scaffolds_count": len(frags),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pdb_rows = fetch_all_sarm1_pdb_metadata()
    chembl_info = query_chembl_direct()
    summary = {"sarm1_pdb_count": len(pdb_rows), "sarm1_pdb_entries": pdb_rows, "chembl": chembl_info}
    (OUT / "pdb_chembl_inventory_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"PDB human SARM1 entries={len(pdb_rows)} | ChEMBL={chembl_info}")


if __name__ == "__main__":
    main()
