"""RUN-B6-004: Live primary database queries (gnomAD v4, OpenTargets v4 + gene
liability, ClinVar, ChEMBL, ClinicalTrials.gov v2, OpenFDA, and EuropePMC).
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_6" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

GENES = {
    "AGAP2": "ENSG00000135439", "AP1G2": "ENSG00000213983", "BRSK2": "ENSG00000174672",
    "DNAJB2": "ENSG00000135924", "KIFC2": "ENSG00000167702", "MIB2": "ENSG00000197530",
    "MYO18A": "ENSG00000196535", "SNPH": "ENSG00000101298", "ZNF783": "ENSG00000204946",
    "CAPG": "ENSG00000042493", "SARM1": "ENSG00000004139",
}


def http_json(url: str, payload: dict | None = None, timeout: int = 18) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"User-Agent": "CarbonALS-Phase1/0.1", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def query_targets() -> dict:
    res = {}
    ot_q = """
    query($id: String!) {
      target(ensemblId: $id) {
        approvedSymbol
        geneticConstraint { constraintType exp obs score oe oeLower oeUpper }
        safetyLiabilities { event biosamples { tissueLabel } effects { direction } }
        tractability { label modality value }
        associatedDiseases(page: {index: 0, size: 25}) {
          rows { disease { id name } score datatypeScores { id score } }
        }
      }
    }"""
    for sym, ens in GENES.items():
        entry: dict[str, object] = {"ensembl_id": ens}
        try:
            ot = http_json("https://api.platform.opentargets.org/api/v4/graphql", {"query": ot_q, "variables": {"id": ens}})
            t = (ot.get("data") or {}).get("target") or {}
            als_rows = [
                r for r in (t.get("associatedDiseases", {}).get("rows") or [])
                if any(k in r["disease"]["name"].lower() for k in ["amyotrophic", "motor neuron", "neuropathy", "frontotemporal", "charcot"])
            ]
            entry["opentargets_constraint"] = t.get("geneticConstraint") or []
            entry["safety_liabilities"] = t.get("safetyLiabilities") or []
            entry["tractability_true"] = [x for x in (t.get("tractability") or []) if x.get("value")]
            entry["disease_associations"] = als_rows[:6]
        except Exception as exc:
            entry["opentargets_error"] = str(exc)

        try:
            term = urllib.parse.quote(f"{sym}[gene] AND (clinsig_pathogenic[prop] OR clinsig_likely_pathogenic[prop])")
            cv = http_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={term}&retmax=8&retmode=json")
            ids = (cv.get("esearchresult") or {}).get("idlist") or []
            entry["clinvar_pathogenic_count"] = int((cv.get("esearchresult") or {}).get("count", 0))
            if ids:
                sm = http_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id={','.join(ids[:5])}&retmode=json")
                res_sm = sm.get("result") or {}
                entry["clinvar_top_records"] = [
                    {"uid": i, "title": res_sm.get(i, {}).get("title"),
                     "traits": [t.get("trait_name") for t in (res_sm.get(i, {}).get("trait_set") or [])]}
                    for i in ids[:5] if i in res_sm
                ]
            time.sleep(0.35)
        except Exception as exc:
            entry["clinvar_error"] = str(exc)
        res[sym] = entry
    return res


def query_drugs_trials_lit() -> dict:
    # ChEMBL verification (including S02 CHEMBL4297643 provenance check!)
    chembl_ids = ["CHEMBL778", "CHEMBL4297643", "CHEMBL1230607", "CHEMBL1077", "CHEMBL83", "CHEMBL1201585", "CHEMBL2110732"]
    chembl_out = {}
    for cid in chembl_ids:
        try:
            m = http_json(f"https://www.ebi.ac.uk/chembl/api/data/molecule/{cid}.json")
            mech = http_json(f"https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id={cid}")
            chembl_out[cid] = {
                "pref_name": m.get("pref_name"), "max_phase": m.get("max_phase"),
                "molecule_properties": m.get("molecule_properties"),
                "mechanisms": [
                    {"action": x.get("action_type"), "mechanism": x.get("mechanism_of_action"), "target": x.get("target_chembl_id")}
                    for x in (mech.get("mechanisms") or [])
                ],
            }
        except Exception as exc:
            chembl_out[cid] = {"error": str(exc)}

    for qname in ["CuATSM", "censavudine", "DSRM-3716"]:
        try:
            sq = http_json(f"https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?q={urllib.parse.quote(qname)}&limit=3")
            chembl_out[f"search_{qname}"] = [
                {"chembl_id": x.get("molecule_chembl_id"), "pref_name": x.get("pref_name"), "max_phase": x.get("max_phase"),
                 "props": x.get("molecule_properties")}
                for x in (sq.get("molecules") or [])
            ]
        except Exception as exc:
            chembl_out[f"search_{qname}"] = {"error": str(exc)}

    # ClinicalTrials.gov API v2
    ncts = ["NCT04082832", "NCT02870634", "NCT04313166", "NCT00214110", "NCT01257581", "NCT03039673", "NCT03548311", "NCT04993755"]
    trials_out = {}
    for nct in ncts:
        try:
            d = http_json(f"https://clinicaltrials.gov/api/v2/studies/{nct}")
            ps = d.get("protocolSection") or {}
            trials_out[nct] = {
                "title": ps.get("identificationModule", {}).get("briefTitle"),
                "status": ps.get("statusModule", {}).get("overallStatus"),
                "whyStopped": ps.get("statusModule", {}).get("whyStopped"),
                "phases": ps.get("designModule", {}).get("phases"),
                "enrollment": ps.get("designModule", {}).get("enrollmentInfo"),
                "hasResults": d.get("hasResults"),
                "primaryOutcomes": [o.get("measure") for o in (ps.get("outcomesModule", {}).get("primaryOutcomes") or [])[:3]],
            }
        except Exception as exc:
            trials_out[nct] = {"error": str(exc)}

    for term in ["SARM1", "LY3873862", "dexmedetomidine amyotrophic", "mycophenolate amyotrophic"]:
        try:
            st = http_json(f"https://clinicaltrials.gov/api/v2/studies?query.term={urllib.parse.quote(term)}&pageSize=5")
            trials_out[f"search_{term}"] = [
                {"nctId": s["protocolSection"]["identificationModule"]["nctId"],
                 "title": s["protocolSection"]["identificationModule"]["briefTitle"],
                 "status": s["protocolSection"]["statusModule"]["overallStatus"],
                 "phases": s["protocolSection"].get("designModule", {}).get("phases")}
                for s in (st.get("studies") or [])
            ]
        except Exception as exc:
            trials_out[f"search_{term}"] = {"error": str(exc)}

    # OpenFDA drug labels
    fda_out = {}
    for drug in ["dexmedetomidine", "mycophenolate mofetil", "tamoxifen", "aldesleukin"]:
        try:
            fd = http_json(f'https://api.fda.gov/drug/label.json?search=openfda.generic_name:"{urllib.parse.quote(drug)}"&limit=1')
            r0 = (fd.get("results") or [{}])[0]
            fda_out[drug] = {
                "boxed_warning": (r0.get("boxed_warning") or [""])[0][:600],
                "pharmacokinetics": (r0.get("pharmacokinetics") or r0.get("clinical_pharmacology") or [""])[0][:800],
            }
        except Exception as exc:
            fda_out[drug] = {"error": str(exc)}

    # EuropePMC primary literature
    epmc_queries = {
        "MIROCALS_IL2": 'MIROCALS OR (aldesleukin AND "amyotrophic lateral sclerosis" AND pNfH)',
        "JETALS_MeCbl": 'JETALS OR (methylcobalamin AND "amyotrophic lateral sclerosis" AND Oki)',
        "CuATSM_ALS": 'CuATSM AND "amyotrophic lateral sclerosis" AND (trial OR pathology)',
        "SARM1_ALS_genetics": 'SARM1 AND "amyotrophic lateral sclerosis" AND (Gilley OR Bloom OR Fazio OR variant)',
        "SARM1_inhibitor_biphasic": 'SARM1 AND ("DSRM-3716" OR "base exchange" OR sub-inhibitory OR allosteric)',
        "TPN101_ALS_TE": '("TPN-101" OR censavudine) AND (ALS OR C9orf72 OR LINE-1)',
        "DNAJB2_ALS": 'DNAJB2 AND ("amyotrophic lateral sclerosis" OR "distal hereditary motor neuropathy" OR TDP-43)',
        "SNPH_ALS": '(SNPH OR syntaphilin) AND ("amyotrophic lateral sclerosis" OR SOD1 OR TDP-43 OR axonal)',
    }
    lit_out = {}
    for k, q in epmc_queries.items():
        try:
            ep = http_json(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.parse.quote(q)}&format=json&pageSize=5")
            lit_out[k] = [
                {"pmid": p.get("pmid"), "pmcid": p.get("pmcid"), "doi": p.get("doi"),
                 "year": p.get("pubYear"), "title": p.get("title"), "journal": p.get("journalTitle")}
                for p in (ep.get("resultList", {}).get("result") or [])
            ]
        except Exception as exc:
            lit_out[k] = {"error": str(exc)}

    return {"chembl": chembl_out, "clinical_trials": trials_out, "openfda": fda_out, "europepmc": lit_out}


if __name__ == "__main__":
    payload = {"targets_genetics_safety": query_targets(), **query_drugs_trials_lit()}
    (OUT_DIR / "live_databases_audit.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Saved live_databases_audit.json successfully.")
