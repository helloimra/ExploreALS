"""RUN-B5-003: Live Tri-Pillar API queries (CT.gov v2, OpenFDA, ChEMBL, PubChem, EuropePMC, PubMed)."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_5" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def http_get_json(url: str, timeout: int = 25) -> dict | list | None:
    req = urllib.request.Request(url, headers={"User-Agent": "CarbonALS-Phase1-Batch5/1.0", "Accept": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            if attempt == 2:
                return {"_error": str(exc), "_url": url}
            time.sleep(1.0 * (attempt + 1))
    return None


def query_clinical_trials() -> dict[str, object]:
    ncts = [
        "NCT02450552", "NCT05667779", "NCT06714396", "NCT06681441",
        "NCT00349622", "NCT04302870", "NCT02118727", "NCT00353665",
        "NCT03019419", "NCT03020797", "NCT03377309", "NCT03793868",
    ]
    studies: dict[str, object] = {}
    for nct in ncts:
        data = http_get_json(f"https://clinicaltrials.gov/api/v2/studies/{nct}")
        if not isinstance(data, dict) or "_error" in data:
            studies[nct] = data
            continue
        ps = data.get("protocolSection", {})
        ident = ps.get("identificationModule", {})
        stat = ps.get("statusModule", {})
        des = ps.get("designModule", {})
        arms = ps.get("armsInterventionsModule", {})
        outc = ps.get("outcomesModule", {})
        rs = data.get("resultsSection", {})
        posted_outcomes = []
        for om in rs.get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])[:3]:
            analyses = [
                {
                    "paramType": an.get("paramType"),
                    "paramValue": an.get("paramValue"),
                    "pValue": an.get("pValue"),
                    "ciLower": an.get("ciLowerLimit"),
                    "ciUpper": an.get("ciUpperLimit"),
                }
                for an in om.get("analyses", [])[:4]
            ]
            posted_outcomes.append({"title": om.get("title"), "type": om.get("type"), "analyses": analyses})
        studies[nct] = {
            "nctId": ident.get("nctId"),
            "briefTitle": ident.get("briefTitle"),
            "overallStatus": stat.get("overallStatus"),
            "whyStopped": stat.get("whyStopped"),
            "startDate": stat.get("startDateStruct", {}).get("date"),
            "completionDate": stat.get("completionDateStruct", {}).get("date"),
            "phases": des.get("phases", []),
            "enrollment": des.get("enrollmentInfo", {}),
            "interventions": [i.get("name") for i in arms.get("interventions", [])],
            "primaryOutcomes": [o.get("measure") for o in outc.get("primaryOutcomes", [])[:3]],
            "hasResults": bool(data.get("hasResults")),
            "postedPrimaryOutcomeAnalyses": posted_outcomes,
        }

    search_terms = [
        ("memantine_als", "memantine", "Amyotrophic Lateral Sclerosis"),
        ("ropinirole_als", "ropinirole", "Amyotrophic Lateral Sclerosis"),
        ("furosemide_als", "furosemide", "Amyotrophic Lateral Sclerosis"),
        ("perampanel_als", "perampanel", "Amyotrophic Lateral Sclerosis"),
        ("qrl101", "QRL-101", ""),
        ("bhv7000", "BHV-7000", ""),
        ("azetukalner", "XEN1101", ""),
    ]
    searches: dict[str, object] = {}
    for key, intr, cond in search_terms:
        q = f"https://clinicaltrials.gov/api/v2/studies?query.intr={urllib.parse.quote(intr)}&pageSize=15"
        if cond:
            q += f"&query.cond={urllib.parse.quote(cond)}"
        res = http_get_json(q)
        if isinstance(res, dict) and "studies" in res:
            hits = []
            for st in res["studies"]:
                ps = st.get("protocolSection", {})
                hits.append({
                    "nctId": ps.get("identificationModule", {}).get("nctId"),
                    "title": ps.get("identificationModule", {}).get("briefTitle"),
                    "status": ps.get("statusModule", {}).get("overallStatus"),
                    "phases": ps.get("designModule", {}).get("phases", []),
                    "enrollment": ps.get("designModule", {}).get("enrollmentInfo", {}).get("count"),
                })
            searches[key] = {"count": len(hits), "studies": hits}
        else:
            searches[key] = res
    return {"targeted_ncts": studies, "landscape_searches": searches}


def query_openfda() -> dict[str, object]:
    ndas = {
        "C003_ezogabine_NDA022345": "NDA022345",
        "C004_ceftriaxone_NDA050585": "NDA050585",
        "C008_memantine_NDA021487": "NDA021487",
        "C010_ropinirole_NDA022008": "NDA022008",
        "C011_furosemide_NDA016273": "NDA016273",
        "C012_perampanel_NDA202834": "NDA202834",
    }
    fda_out: dict[str, object] = {}
    for key, nda in ndas.items():
        d_res = http_get_json(f"https://api.fda.gov/drug/drugsfda.json?search=application_number:{nda}&limit=1")
        l_res = http_get_json(f"https://api.fda.gov/drug/label.json?search=openfda.application_number:{nda}&limit=1")
        entry: dict[str, object] = {"application_number": nda}
        if isinstance(d_res, dict) and "results" in d_res and d_res["results"]:
            r0 = d_res["results"][0]
            entry["sponsor"] = r0.get("sponsor_name")
            entry["products"] = [
                {"brand": p.get("brand_name"), "status": p.get("marketing_status"), "dosage_form": p.get("dosage_form")}
                for p in r0.get("products", [])[:4]
            ]
        if isinstance(l_res, dict) and "results" in l_res and l_res["results"]:
            lr = l_res["results"][0]
            entry["boxed_warning_snippet"] = (lr.get("boxed_warning", [""])[0])[:500]
            entry["pharmacokinetics_snippet"] = (lr.get("pharmacokinetics", lr.get("clinical_pharmacology", [""]))[0])[:900]
        fda_out[key] = entry
    return fda_out


def query_chembl_and_pubchem() -> dict[str, object]:
    compounds = [
        ("C003_ezogabine", 121892),
        ("C004_ceftriaxone", 5479530),
        ("C008_memantine", 4054),
        ("C010_ropinirole", 5095),
        ("C011_furosemide", 3440),
        ("C012_perampanel", 9924495),
    ]
    out: dict[str, object] = {}
    for label, cid_pubchem in compounds:
        pc = http_get_json(
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid_pubchem}/property/"
            "MolecularFormula,MolecularWeight,ExactMass,XLogP,TPSA,InChIKey/JSON"
        )
        pc_props = (
            pc.get("PropertyTable", {}).get("Properties", [{}])[0]
            if isinstance(pc, dict) and "PropertyTable" in pc
            else {}
        )
        inchikey = pc_props.get("InChIKey", "")
        mol_search = http_get_json(
            f"https://www.ebi.ac.uk/chembl/api/data/molecule.json?molecule_structures__standard_inchi_key__exact={inchikey}&limit=2"
        )
        mols = mol_search.get("molecules", []) if isinstance(mol_search, dict) else []
        mol = mols[0] if mols else {}
        cid_chembl = mol.get("molecule_chembl_id", "UNKNOWN")
        mech = http_get_json(f"https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id={cid_chembl}&limit=20")
        act = http_get_json(
            f"https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id={cid_chembl}"
            "&target_organism=Homo%20sapiens&standard_units=nM&limit=60"
        )
        props = mol.get("molecule_properties", {}) if isinstance(mol, dict) else {}
        mechs = [
            {"action": m.get("action_type"), "mechanism": m.get("mechanism_of_action"), "target": m.get("target_chembl_id")}
            for m in (mech.get("mechanisms", []) if isinstance(mech, dict) else [])
        ]
        acts_summary = []
        for a in (act.get("activities", []) if isinstance(act, dict) else []):
            if a.get("standard_value") and a.get("standard_type") in {"IC50", "Ki", "EC50", "Kd"}:
                acts_summary.append({
                    "target_pref_name": a.get("target_pref_name"),
                    "type": a.get("standard_type"),
                    "relation": a.get("standard_relation"),
                    "value_nM": float(a["standard_value"]),
                    "assay_type": a.get("assay_type"),
                })
        acts_summary.sort(key=lambda x: x["value_nM"])
        out[label] = {
            "chembl_id": cid_chembl,
            "pref_name": mol.get("pref_name") if isinstance(mol, dict) else None,
            "max_phase": mol.get("max_phase") if isinstance(mol, dict) else None,
            "withdrawn_flag": mol.get("withdrawn_flag") if isinstance(mol, dict) else None,
            "chembl_mw_freebase": props.get("mw_freebase"),
            "chembl_alogp": props.get("alogp"),
            "chembl_psa": props.get("psa"),
            "pubchem_props": pc_props,
            "mechanisms": mechs,
            "top_human_potencies_nM": acts_summary[:15],
        }
    return out


def query_europepmc_and_pubmed() -> dict[str, object]:
    pmids = [
        "33226425",  # Wainger 2021 JAMA Neurol Ezogabine ALS Phase 2
        "29672831",  # Kovalchuk 2018 acute retigabine/riluzole axonal excitability ALS
        "25297012",  # Cudkowicz 2014 Lancet Neurol Ceftriaxone Stage 3 ALS
        "24771634",  # Zhao 2014 Ceftriaxone human ALS CSF PK
        "39511965",  # Statland 2025 Muscle Nerve US Phase 2b Memantine ALS (NCT02118727)
        "39307154",  # Pal 2024 Lancet Neurol MND-SMART Memantine & Trazodone Stage 2
        "37267913",  # Morimoto 2023 Cell Stem Cell ROPALS Ropinirole Phase 1/2a
        "30127392",  # Fujimori 2018 Nat Med Ropinirole iPSC screen
        "40826812",  # 2025 J Neurochem D2R-independent Ropinirole TARDBP study
        "29959396",  # Lykke 2018 human NKCC1/KCC2 furosemide/bumetanide potency
        "34191081",  # Aizawa 2022 J Neurol Perampanel ALS Phase 2 RCT (NCT03019419)
        "26911633",  # Weiss 2016 Neurology Mexiletine ALS Phase 2 RCT
    ]
    esum = http_get_json(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(pmids)
    )
    pubmed_records: dict[str, object] = {}
    if isinstance(esum, dict) and "result" in esum:
        for p in pmids:
            r = esum["result"].get(p, {})
            pubmed_records[p] = {
                "pmid": p,
                "title": r.get("title"),
                "source": r.get("source"),
                "pubdate": r.get("pubdate"),
                "articleids": r.get("articleids", []),
            }

    epmc_queries = {
        "mnd_smart_memantine_2024": 'EXT_ID:39307154',
        "berry_2013_ceftriaxone_csf": 'DOI:"10.1371/journal.pone.0061177"',
        "de_carvalho_2010_memantine_medals": 'TITLE:"randomized, placebo-controlled trial of memantine" AND "amyotrophic lateral sclerosis"',
        "chan_memantine_als": 'AUTH:"Chan" AND TITLE:"memantine" AND TITLE:"amyotrophic lateral sclerosis"',
        "kornhuber_memantine_csf": 'AUTH:"Kornhuber" AND TITLE:"memantine" AND ("cerebrospinal" OR "serum")',
        "furosemide_renshaw_pmc4221825": 'PMCID:PMC4221825',
        "furosemide_oat3_kusuhara": 'AUTH:"Kusuhara" AND "OAT3" AND "choroid plexus"',
        "talampanel_pascuzzi_als": 'AUTH:"Pascuzzi" AND TITLE:"talampanel"',
        "flecainide_park_als": 'AUTH:"Park" AND TITLE:"flecainide" AND TITLE:"amyotrophic lateral sclerosis"',
        "guo_2025_kcnq2_tdp43": 'DOI:"10.1038/s41593-025-02096-w"',
    }
    epmc_hits: dict[str, object] = {}
    for k, q in epmc_queries.items():
        url = (
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
            + urllib.parse.quote(q)
            + "&resultType=core&pageSize=3&format=json"
        )
        res = http_get_json(url)
        items = res.get("resultList", {}).get("result", []) if isinstance(res, dict) else []
        epmc_hits[k] = [
            {
                "pmid": it.get("pmid"),
                "pmcid": it.get("pmcid"),
                "doi": it.get("doi"),
                "title": it.get("title"),
                "journal": it.get("journalTitle"),
                "pubYear": it.get("pubYear"),
                "abstract_snippet": (it.get("abstractText") or "")[:900],
            }
            for it in items
        ]
    return {"pubmed_esummary": pubmed_records, "europepmc_core": epmc_hits}


if __name__ == "__main__":
    bundle = {
        "clinical_trials_gov": query_clinical_trials(),
        "openfda": query_openfda(),
        "chembl_pubchem": query_chembl_and_pubchem(),
        "pubmed_europepmc": query_europepmc_and_pubmed(),
    }
    (OUT_DIR / "tri_pillar_clinical_pk_prior_art.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print("RUN-B5-003 complete. Saved tri_pillar_clinical_pk_prior_art.json")
