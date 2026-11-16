"""RUN-B4-003: Live ChEMBL, PubChem, CT.gov v2, OpenFDA/FAERS, gnomAD/OpenTargets, EuropePMC & Unbound CNS PK."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_4" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def http_json(url: str, payload: dict | None = None, timeout: int = 20) -> dict | list | None:
    headers = {"Accept": "application/json", "User-Agent": "CarbonALS-Phase1-Batch4/1.0"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"_error": str(exc), "_url": url}


def fetch_chembl_and_pubchem() -> dict:
    chembl_ids = [
        ("C009", "CHEMBL621"),              # Trazodone free base
        ("C009_HCl", "CHEMBL1200798"),      # Trazodone HCl
        ("C013", "CHEMBL744"),              # Riluzole
        ("C019", "CHEMBL2105759"),          # Baricitinib
        ("C020", "CHEMBL4297643"),          # Apilimod free base
        ("C021_true", "CHEMBL2365743"),     # True Sephin1 / Icerguastat (MW 196.64)
        ("C021_explore_corrupt", "CHEMBL3545058"),  # ExploreALS corrupt ID (Dextrothyroxine sodium!)
    ]
    chem_out = {}
    for label, cid in chembl_ids:
        mol = http_json(f"https://www.ebi.ac.uk/chembl/api/data/molecule/{cid}.json")
        mech = http_json(f"https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id={cid}")
        props = (mol or {}).get("molecule_properties") or {}
        chem_out[label] = {
            "chembl_id": cid,
            "pref_name": (mol or {}).get("pref_name"),
            "mw_freebase": props.get("mw_freebase"),
            "full_mwt": props.get("full_mwt"),
            "alogp": props.get("alogp"),
            "psa": props.get("psa"),
            "max_phase": (mol or {}).get("max_phase"),
            "molecule_hierarchy": (mol or {}).get("molecule_hierarchy"),
            "mechanisms": [
                {
                    "action_type": m.get("action_type"),
                    "mechanism_of_action": m.get("mechanism_of_action"),
                    "target_chembl_id": m.get("target_chembl_id"),
                }
                for m in ((mech or {}).get("mechanisms") or [])
            ],
        }

    # Fetch top ChEMBL quantitative IC50/Ki/Kd activities for parent molecules
    for label, cid in [
        ("C009", "CHEMBL621"),
        ("C013", "CHEMBL744"),
        ("C019", "CHEMBL2105759"),
        ("C020", "CHEMBL4297643"),
        ("C021_true", "CHEMBL2365743"),
    ]:
        act = http_json(
            f"https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id={cid}&standard_units=nM&limit=40"
        )
        rows = []
        for a in ((act or {}).get("activities") or []):
            if a.get("standard_type") in {"IC50", "Ki", "Kd", "EC50"} and a.get("standard_value"):
                rows.append({
                    "target_pref_name": a.get("target_pref_name"),
                    "target_organism": a.get("target_organism"),
                    "standard_type": a.get("standard_type"),
                    "standard_relation": a.get("standard_relation"),
                    "standard_value_nM": float(a["standard_value"]),
                    "assay_type": a.get("assay_type"),
                })
        rows.sort(key=lambda r: r["standard_value_nM"])
        chem_out[label]["top_nanomolar_activities"] = rows[:15]

    pubchem_cids = {
        "C009": 5533,
        "C009_HCl": 62935,
        "C013": 5070,
        "C019": 44205240,
        "C020": 10173277,
        "C020_dimesylate": 11527330,
        "C021_true": 9561611,
        "C021_explore_corrupt": 5702546,
    }
    pc_out = {}
    for k, pcid in pubchem_cids.items():
        d = http_json(
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{pcid}/property/MolecularFormula,MolecularWeight,XLogP,TPSA,InChIKey/JSON"
        )
        plist = (((d or {}).get("PropertyTable") or {}).get("Properties") or [{}])[0]
        pc_out[k] = plist
    return {"chembl": chem_out, "pubchem": pc_out}


def fetch_clinical_trials() -> dict:
    nct_ids = [
        "NCT04302870",  # MND-SMART (Trazodone, Memantine)
        "NCT05740813",  # HEALEY Regimen F (ABBV-CLS-7262 / fosigotifator)
        "NCT05842941",  # HEALEY Regimen G (DNL343)
        "NCT05189106",  # NADALS (Baricitinib in ALS/AD)
        "NCT03921554",  # Baricitinib in Aicardi-Goutieres
        "NCT05163886",  # AIT-101 (Apilimod) in C9orf72 ALS
        "NCT06286475",  # VRG50635 healthy-volunteer Phase 1 trial (halted for encephalopathy/renal SAE)
        "NCT06215755",  # VRG50635 (PIKfyve inhibitor) in ALS
        "NCT05508074",  # IFB-088 (Icerguastat) Phase 2 TRIALS bulbar ALS
        "NCT03610334",  # IFB-088 Phase 1 PK
    ]
    studies = {}
    for nct in nct_ids:
        d = http_json(f"https://clinicaltrials.gov/api/v2/studies/{nct}")
        if not d or "_error" in d:
            studies[nct] = d
            continue
        ps = d.get("protocolSection", {})
        idm = ps.get("identificationModule", {})
        stm = ps.get("statusModule", {})
        des = ps.get("designModule", {})
        arm = ps.get("armsInterventionsModule", {})
        outm = ps.get("outcomesModule", {})
        has_res = bool(d.get("hasResults"))
        res_summary = None
        if has_res and d.get("resultsSection"):
            rs = d["resultsSection"]
            pf = rs.get("participantFlowModule", {})
            om = rs.get("outcomeMeasuresModule", {})
            res_summary = {
                "flow_groups": pf.get("groups"),
                "outcome_measures": [
                    {
                        "title": o.get("title"),
                        "type": o.get("type"),
                        "unitOfMeasure": o.get("unitOfMeasure"),
                        "classes": o.get("classes"),
                    }
                    for o in (om.get("outcomeMeasures") or [])[:10]
                ],
            }
        studies[nct] = {
            "briefTitle": idm.get("briefTitle"),
            "overallStatus": stm.get("overallStatus"),
            "whyStopped": stm.get("whyStopped"),
            "startDate": (stm.get("startDateStruct") or {}).get("date"),
            "completionDate": (stm.get("completionDateStruct") or {}).get("date"),
            "phases": des.get("phases"),
            "enrollmentInfo": des.get("enrollmentInfo"),
            "armGroups": arm.get("armGroups"),
            "primaryOutcomes": outm.get("primaryOutcomes"),
            "hasResults": has_res,
            "resultsSummary": res_summary,
        }
    return studies


def fetch_openfda_and_faers() -> dict:
    drug_queries = [
        ("trazodone", 'openfda.generic_name:"trazodone"'),
        ("riluzole", 'openfda.brand_name:"RILUTEK"'),
        ("baricitinib", 'openfda.brand_name:"OLUMIANT"'),
    ]
    labels = {}
    for dname, qstr in drug_queries:
        url = f"https://api.fda.gov/drug/label.json?search={urllib.parse.quote(qstr)}&limit=1"
        res = http_json(url)
        rec = ((res or {}).get("results") or [{}])[0]
        labels[dname] = {
            "brand_name": (rec.get("openfda") or {}).get("brand_name"),
            "application_number": (rec.get("openfda") or {}).get("application_number"),
            "boxed_warning": [s[:1200] for s in (rec.get("boxed_warning") or [])],
            "pharmacokinetics": [s[:2000] for s in (rec.get("pharmacokinetics") or rec.get("clinical_pharmacology") or [])],
            "warnings_excerpt": [s[:1000] for s in (rec.get("warnings_and_cautions") or rec.get("warnings") or [])[:1]],
        }

    faers = {}
    for dname in ["TRAZODONE", "RILUZOLE", "BARICITINIB", "APILIMOD"]:
        q_ser = f"https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:%22{dname}%22+AND+serious:1&count=patient.reaction.reactionmeddrapt.exact&limit=10"
        q_tot = f"https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:%22{dname}%22&limit=1"
        r_ser = http_json(q_ser)
        r_tot = http_json(q_tot)
        tot_n = (((r_tot or {}).get("meta") or {}).get("results") or {}).get("total", 0)
        faers[dname] = {
            "total_reports": tot_n,
            "top_serious_meddra_pts": (r_ser or {}).get("results", []),
        }
    return {"fda_labels": labels, "faers": faers}


def fetch_gene_liability() -> dict:
    genes = [
        ("PIKFYVE", "ENSG00000115020"),
        ("JAK1", "ENSG00000162434"),
        ("JAK2", "ENSG00000096968"),
        ("AAK1", "ENSG00000115977"),
        ("PPP1R15A", "ENSG00000087074"),
        ("PPP1R15B", "ENSG00000158615"),
        ("SIGMAR1", "ENSG00000147955"),
        ("GRIN2B", "ENSG00000273079"),
        ("HTR2A", "ENSG00000102468"),
        ("SCN8A", "ENSG00000196876"),
    ]
    out = {}
    ot_query = """
    query GeneLiability($ensgId: String!) {
      target(ensemblId: $ensgId) {
        approvedSymbol
        isEssential
        geneticConstraint { constraintType exp obs score oe oeLower oeUpper }
        safetyLiabilities { event eventId biosamples { tissueLabel } effects { direction dosing } }
        mousePhenotypes { modelPhenotypeLabel modelPhenotypeClasses { label } }
        depMapEssentiality { screens { cellLineName diseaseFromSource geneEffect } }
      }
    }
    """
    for sym, ensg in genes:
        res = http_json(
            "https://api.platform.opentargets.org/api/v4/graphql",
            payload={"query": ot_query, "variables": {"ensgId": ensg}},
        )
        t = (((res or {}).get("data") or {}).get("target")) or {}
        screens = []
        for blk in (t.get("depMapEssentiality") or []):
            screens.extend(blk.get("screens") or [])
        effs = [float(s["geneEffect"]) for s in screens if s.get("geneEffect") is not None]
        mp_labels = [m.get("modelPhenotypeLabel") for m in (t.get("mousePhenotypes") or []) if m.get("modelPhenotypeLabel")]
        lethal_mp = [m for m in mp_labels if any(k in m.lower() for k in ("lethal", "death", "vacuol", "neuro", "motor", "axon"))]
        out[sym] = {
            "ensembl_id": ensg,
            "is_essential_ot": t.get("isEssential"),
            "genetic_constraint": t.get("geneticConstraint"),
            "depmap_n_screens": len(effs),
            "depmap_mean_chronos": round(sum(effs) / len(effs), 4) if effs else None,
            "depmap_pct_below_neg0_5": round(100.0 * sum(1 for e in effs if e < -0.5) / len(effs), 2) if effs else None,
            "safety_liabilities": (t.get("safetyLiabilities") or [])[:8],
            "mouse_phenotypes_total_n": len(mp_labels),
            "mouse_lethal_vacuol_neuro_phenotypes": lethal_mp[:15],
        }
    return out


def fetch_europepmc_literature() -> dict:
    queries = {
        "C009_mnd_smart": 'TITLE_ABS:("MND-SMART" AND trazodone)',
        "C009_halliday_isr": 'TITLE_ABS:(trazodone AND ("integrated stress response" OR eIF2B OR ATF4))',
        "C013_riluzole_als": 'TITLE_ABS:(riluzole AND "persistent sodium" AND motor)',
        "C019_baricitinib_pstat": 'TITLE_ABS:(baricitinib AND pSTAT AND IC50)',
        "C019_baricitinib_csf": 'TITLE_ABS:(baricitinib AND ("cerebrospinal fluid" OR CSF))',
        "C020_apilimod_als": 'TITLE_ABS:((apilimod OR "AIT-101" OR "VRG50635") AND ("amyotrophic lateral sclerosis" OR C9orf72 OR PIKFYVE))',
        "C021_sephin1_controversy": 'TITLE_ABS:((Sephin1 OR icerguastat OR "IFB-088") AND (PPP1R15A OR GADD34 OR NR2B OR GluN2B OR "amyotrophic lateral sclerosis"))',
    }
    lit = {}
    for key, q in queries.items():
        enc = urllib.parse.quote(q)
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={enc}&format=json&pageSize=8&resultType=core"
        res = http_json(url)
        items = (((res or {}).get("resultList") or {}).get("result")) or []
        lit[key] = [
            {
                "pmid": it.get("pmid"),
                "pmcid": it.get("pmcid"),
                "doi": it.get("doi"),
                "pubYear": it.get("pubYear"),
                "journal": (it.get("journalInfo") or {}).get("journal", {}).get("title"),
                "title": it.get("title"),
                "abstract_snippet": (it.get("abstractText") or "")[:500],
            }
            for it in items
        ]
    return lit


def compute_unbound_cns_pk_models() -> list[dict]:
    """
    Rigorous free-base normalized unbound plasma, CSF, and brain PK vs primary & screen EC50/IC50.
    All salt-vs-free-base molecular weights explicitly separated.
    """
    rows = []

    # C009: Trazodone (administered as Trazodone HCl MW 408.32 g/mol; free base MW 371.87 g/mol, ratio=0.9107)
    # Clinical dose: 150-200 mg/day (MND-SMART tested 200 mg QD; max outpatient 300-400 mg/day)
    # FDA Desyrel label: 150 mg single/steady-state Cmax_total ~ 1.5-2.1 ug/mL (~2.0 ug/mL at 200 mg QD); fu,p = 0.08 (89-95% bound -> mean ~92% bound, fu,p=0.08)
    # Human/rodent brain Kp,uu ~ 0.65; Halliday 2017 ISR translational restoration tested at 20 uM (EC50 ~ 10-20 uM in CHO/HeLa; no direct eIF2B binding); 5-HT2A Ki = 20 nM, alpha1A Ki = 12-40 nM, H1 Ki = 220 nM
    mw_traz = 371.87
    cmax_tot_traz_nM = (2000.0 / mw_traz) * 1000.0  # 2.0 ug/mL = 2000 ng/mL -> 5378.2 nM total plasma
    fup_traz = 0.08
    cmax_u_traz_nM = cmax_tot_traz_nM * fup_traz    # 430.3 nM unbound plasma
    kpuu_traz = 0.65
    cu_brain_traz_nM = cmax_u_traz_nM * kpuu_traz   # ~279.7 nM (~0.28 uM) unbound brain
    rows.append({
        "carbon_id": "C009",
        "drug_name": "Trazodone",
        "clinical_formulation": "Trazodone HCl (MW 408.32 g/mol; free base MW 371.87 g/mol)",
        "clinical_regimen": "200 mg/day PO (MND-SMART RCT; max outpatient 300-400 mg/day)",
        "cmax_total_plasma_nM": round(cmax_tot_traz_nM, 1),
        "fu_plasma": fup_traz,
        "cmax_unbound_plasma_nM": round(cmax_u_traz_nM, 1),
        "csf_total_measured_nM": None,
        "kpuu_cns_estimate": kpuu_traz,
        "cu_cns_estimated_nM": round(cu_brain_traz_nM, 1),
        "primary_on_target_potency_nM": 15000.0,  # Halliday 2017 ISR cellular rescue 10-20 uM (midpoint 15,000 nM)
        "dose_limiting_off_target_nM": 20.0,      # 5-HT2A Ki ~20 nM / alpha1A Ki ~25 nM (sedation/orthostasis)
        "cu_cns_over_target_ic50": round(cu_brain_traz_nM / 15000.0, 4),
        "bye2025_2500nM_over_cu_cns_gap": round(2500.0 / cu_brain_traz_nM, 2),
        "pk_verdict": "Unbound brain (~280 nM at 200 mg/d; ~560 nM at 400 mg/d) is 14x above sedating 5-HT2A/alpha1 Ki (~20 nM) yet 9-36x BELOW Bye 2025 (2,500 nM) and Halliday 2017 ISR assay (10,000-20,000 nM).",
    })

    # C013: Riluzole (free base MW 234.20 g/mol; 50 mg BID PO)
    # FDA Rilutek label: Cmax_total ~ 173-209 ng/mL (~190 ng/mL = 811.3 nM); fu,p = 0.04 (96% bound); lipophilic neutral benzothiazole Kp,uu ~ 1.0-1.3 (CSF/unbound plasma ~1.0; brain tissue total much higher, unbound ~35-50 nM at Cmax, up to ~100-300 nM in hyperexcitable persistent NaV1.6 state-dependent block IC50 ~ 0.3-2.0 uM)
    mw_ril = 234.20
    cmax_tot_ril_nM = (190.0 / mw_ril) * 1000.0  # 811.3 nM total plasma
    fup_ril = 0.04
    cmax_u_ril_nM = cmax_tot_ril_nM * fup_ril    # 32.5 nM unbound plasma (up to ~65-100 nM in high-exposure CYP1A2 slow metabolizers)
    kpuu_ril = 1.10
    cu_brain_ril_nM = cmax_u_ril_nM * kpuu_ril   # ~35.7 nM mean unbound brain (human ALS CSF measured ~50-210 nM total/free)
    rows.append({
        "carbon_id": "C013",
        "drug_name": "Riluzole",
        "clinical_formulation": "Riluzole free base (MW 234.20 g/mol)",
        "clinical_regimen": "50 mg BID PO (FDA standard of care)",
        "cmax_total_plasma_nM": round(cmax_tot_ril_nM, 1),
        "fu_plasma": fup_ril,
        "cmax_unbound_plasma_nM": round(cmax_u_ril_nM, 1),
        "csf_total_measured_nM": 115.0,  # Published ALS patient CSF ~27 ng/mL (~115 nM)
        "kpuu_cns_estimate": kpuu_ril,
        "cu_cns_estimated_nM": 115.0,    # Protein-poor CSF ~100-120 nM; persistent I_NaP IC50 ~ 300-2000 nM
        "primary_on_target_potency_nM": 500.0,   # Persistent Na+ current (I_NaP, NaV1.6) IC50 ~ 300-1000 nM
        "dose_limiting_off_target_nM": 2000.0,   # Asthenia / ALT elevation / NaV peak block >10 uM
        "cu_cns_over_target_ic50": round(115.0 / 500.0, 3),
        "bye2025_2500nM_over_cu_cns_gap": round(2500.0 / 115.0, 2),
        "pk_verdict": "Benchmark partial I_NaP engagement (~0.1-0.25x IC50 in human CSF ~115 nM; 21.7x below 2.5 uM screen) yields modest 2-3 month Phase 3 survival benefit.",
    })

    # C019: Baricitinib (free base MW 371.42 g/mol; 4 mg QD max approved RA dose; 2 -> 4 mg QD in NADALS NCT05189106)
    # FDA NDA 207924 ClinPharmR: RA 4 mg QD PopPK Cmax,ss = 53.4 ng/mL = 143.77 nM total plasma; fu,p = 0.50 -> Cmax,u = 71.89 nM
    # NADALS NCT05189106 ALS CSF: 1.748 nM at 2 mg QD (Wk 8), 3.804 nM at 4 mg QD (Wk 16) -> Kp,uu,CSF vs steady-state plasma (~50-72 nM unbound) ~ 0.053-0.15 (P-gp/BCRP efflux); AGS pediatric higher weight-adjusted doses give CSF/total plasma ~0.10-0.14 (Kp,uu ~0.20-0.28)
    # Cellular JAK1/2 pSTAT1/3 IC50 in human leukocytes = 17-60 nM (McInnes 2019: IFN-gamma pSTAT1 ~23-44 nM, IL-6 pSTAT3 ~40-61 nM); cell-free JAK1/2 IC50 = 5.9/5.7 nM; AAK1 Kd = 17 nM
    mw_bari = 371.42
    cmax_tot_bari_nM = (53.4 / mw_bari) * 1000.0  # 143.8 nM
    fup_bari = 0.50
    cmax_u_bari_nM = cmax_tot_bari_nM * fup_bari  # 71.9 nM
    csf_bari_nM = 3.804                           # NADALS Week 16 at 4 mg/day (essentially 100% unbound in low-protein CSF)
    kpuu_bari = round(csf_bari_nM / 36.0, 3)      # vs mid-interval unbound plasma ~36 nM (or 3.804/71.9 = 0.053 vs Cmax,u)
    rows.append({
        "carbon_id": "C019",
        "drug_name": "Baricitinib",
        "clinical_formulation": "Baricitinib free base (MW 371.42 g/mol)",
        "clinical_regimen": "4 mg QD PO (max RA approved dose; NADALS Week 16)",
        "cmax_total_plasma_nM": round(cmax_tot_bari_nM, 2),
        "fu_plasma": fup_bari,
        "cmax_unbound_plasma_nM": round(cmax_u_bari_nM, 2),
        "csf_total_measured_nM": csf_bari_nM,
        "kpuu_cns_estimate": kpuu_bari,
        "cu_cns_estimated_nM": csf_bari_nM,
        "primary_on_target_potency_nM": 40.0,     # Whole-cell human JAK1/2 pSTAT1/3 IC50 ~23-60 nM (McInnes 2019); enzymatic 5.7-5.9 nM; AAK1 Kd ~17 nM
        "dose_limiting_off_target_nM": 72.0,      # Systemic JAK1/2/3 immunosuppression / thrombosis / MACE Boxed Warning above 4 mg QD
        "cu_cns_over_target_ic50": round(csf_bari_nM / 40.0, 3),
        "bye2025_2500nM_over_cu_cns_gap": round(2500.0 / csf_bari_nM, 1),
        "pk_verdict": "Human ALS CSF at 4 mg QD is 3.80 nM (Kp,uu,CSF ~0.05-0.11 due to P-gp/BCRP efflux): ~0.65x cell-free JAK1/2 IC50 (5.8 nM), ONLY ~0.095x whole-cell pSTAT IC50 (~40 nM), ~0.22x AAK1 Kd (17 nM), and 657x below the 2,500 nM Bye 2025 screen (34.8x below plasma Cmax,u 71.9 nM).",
    })

    # C020: Apilimod (administered as Apilimod dimesylate AIT-101 MW 610.72 g/mol; free base MW 418.50 g/mol, ratio=0.6853)
    # Babu et al. 2024 (Brain, NCT05163886, 125 mg BID AIT-101): Week 12 1h post-dose total plasma = 283 ng/mL (676.2 nM free base), total CSF = 1.63 ng/mL (3.895 nM)
    # Apilimod plasma protein binding >99% (fu,p ~ 0.005 to 0.01; using fu,p=0.008 -> Cmax,u = 5.41 nM; total CSF 3.90 nM in low-albumin CSF -> Kp,uu,CSF ~ 0.65-0.72!)
    # PIKFYVE biochemical IC50 = 14 nM (Cai 2013 / Gayle 2017), cellular PI(3,5)P2 / sGPNMB / poly(GP) target engagement EC50 ~ 5-25 nM -> PROVEN 73% CSF poly(GP) reduction in C9orf72-ALS!
    mw_apil = 418.50
    cmax_tot_apil_nM = (283.13 / mw_apil) * 1000.0  # 676.5 nM (Week 12 LAM-002A arm, n=10)
    fup_apil = 0.008                                # >99% bound in human plasma
    cmax_u_apil_nM = cmax_tot_apil_nM * fup_apil    # 5.41 nM unbound plasma
    csf_apil_nM = (1.63 / mw_apil) * 1000.0         # 3.895 nM CSF
    kpuu_apil = round(csf_apil_nM / cmax_u_apil_nM, 2)
    rows.append({
        "carbon_id": "C020",
        "drug_name": "Apilimod",
        "clinical_formulation": "Apilimod dimesylate / AIT-101 (salt MW 610.72 g/mol; free base MW 418.50 g/mol)",
        "clinical_regimen": "125 mg BID PO (NCT05163886 C9orf72-ALS Phase 2a, Week 12 LAM-002A arm n=10)",
        "cmax_total_plasma_nM": round(cmax_tot_apil_nM, 1),
        "fu_plasma": fup_apil,
        "cmax_unbound_plasma_nM": round(cmax_u_apil_nM, 2),
        "csf_total_measured_nM": round(csf_apil_nM, 2),
        "kpuu_cns_estimate": kpuu_apil,
        "cu_cns_estimated_nM": round(csf_apil_nM, 2),
        "primary_on_target_potency_nM": 14.0,     # PIKFYVE IC50 = 14 nM (cellular EC50 5-20 nM)
        "dose_limiting_off_target_nM": 50.0,      # Continuous PIKFYVE blockade -> cytoplasmic vacuolation, encephalopathy/renal toxicity (VRG50635 NCT06286475) & NfL/GFAP rise (NCT06215755)
        "cu_cns_over_target_ic50": round(csf_apil_nM / 14.0, 3),
        "bye2025_2500nM_over_cu_cns_gap": round(2500.0 / csf_apil_nM, 1),
        "pk_verdict": "Week 12 plasma Cmax 283.13 ng/mL (676.5 nM; fu,p ~0.008 -> 5.41 nM) and CSF 1.63 ng/mL (3.89 nM; Kp,uu,CSF ~0.72, 0.28x PIKFYVE IC50 14 nM) achieved -74.4% CSF poly(GP) in C9orf72-ALS (CSF sGPNMB p=0.352), while continuous dosing risks class vacuolation/NfL/GFAP toxicity (VRG50635 NCT06286475/NCT06215755).",
    })

    # C021: Icerguastat / IFB-088 / Sephin1 (administered as Icerguastat acetate MW 256.69 g/mol; Sephin1 free base C8H9ClN4 MW 196.64 g/mol, CHEMBL2365743, CID:9561611)
    # Posted Phase 2 NCT05508074 results (n=34 IFB-088 50 mg/day [25 mg BID] + riluzole): geometric mean total plasma Cmax = 12 ng/mL (GeoCV 66.4%; AUC = 63 ng*h/mL; CL/F = 580 L/h in ALS; Ph1 CL/F = 736-1,388 L/h = 6.4-15.4x hepatic blood flow)!
    # 12 ng/mL / 196.64 g/mol = 61.03 nM total plasma! With fu,p ~ 0.25 -> Cmax,u = 15.26 nM; preclinical Kp,uu ~ 0.85 -> Cu,brain ~ 13.0 nM (human CSF never directly measured).
    # Target controversy: PPP1R15A direct holophosphatase inhibition refuted in vitro (Crespillo-Casado 2017); cellular rescue/PHB2/GluN2B-NR2B reported at 1-10 uM (Bye 2025 at 2.5 uM); ASIC3 pH7 EC50 = 28,930 nM; G-actin EC50 ~28.9-150 uM
    mw_icer = 196.64
    cmax_tot_icer_nM = (12.0 / mw_icer) * 1000.0   # 61.03 nM measured human ALS total plasma geometric mean Cmax in NCT05508074!
    fup_icer = 0.25
    cmax_u_icer_nM = cmax_tot_icer_nM * fup_icer   # 15.26 nM unbound plasma
    kpuu_icer = 0.85
    cu_brain_icer_nM = cmax_u_icer_nM * kpuu_icer  # ~12.97 nM (~0.013 uM) estimated unbound brain (human CSF unmeasured)
    rows.append({
        "carbon_id": "C021",
        "drug_name": "Icerguastat (IFB-088 / Sephin1)",
        "clinical_formulation": "Icerguastat acetate (salt MW 256.69 g/mol; Sephin1 free base MW 196.64 g/mol; ExploreALS misreported MW 215.64 & wrong IDs)",
        "clinical_regimen": "25 mg BID (50 mg/day) PO + riluzole (Phase 2 NCT05508074 TRIALS, n=34 PK)",
        "cmax_total_plasma_nM": round(cmax_tot_icer_nM, 2),
        "fu_plasma": fup_icer,
        "cmax_unbound_plasma_nM": round(cmax_u_icer_nM, 2),
        "csf_total_measured_nM": None,
        "kpuu_cns_estimate": kpuu_icer,
        "cu_cns_estimated_nM": round(cu_brain_icer_nM, 2),
        "primary_on_target_potency_nM": 2500.0,    # Cellular proteostasis / GluN2B-NR2B / PHB2 ~1-5 uM (direct PPP1R15A biochemical IC50 refuted by Crespillo-Casado 2017)
        "dose_limiting_off_target_nM": 28930.0,   # Rat ASIC3 pH7 EC50 28.9 uM; HeLa G-actin disruption EC50 28.9 uM
        "cu_cns_over_target_ic50": round(cu_brain_icer_nM / 2500.0, 4),
        "bye2025_2500nM_over_cu_cns_gap": round(2500.0 / cu_brain_icer_nM, 1),
        "pk_verdict": "FALSIFIED_PK_SAFETY: Extreme oral clearance (CL/F=580 L/h in ALS; 736-1,388 L/h in Ph1 = 6.4-15.4x hepatic blood flow) caps plasma GeoMean Cmax at 12 ng/mL (GeoCV 66.4%; 61.0 nM; Cu,brain ~13.0 nM = 193x below 2.5 uM screen) with flat ISR GDF15, null ITT ALSFRS-R (p=0.923), AND 2/34 (5.9% vs 0% pbo) drug-related fatal TEAEs + 8/34 (23.5% vs 0%) falls, barring 80-200x dose escalation.",
    })
    return rows


def main() -> None:
    chem = fetch_chembl_and_pubchem()
    trials = fetch_clinical_trials()
    fda = fetch_openfda_and_faers()
    gene_liab = fetch_gene_liability()
    lit = fetch_europepmc_literature()
    pk_rows = compute_unbound_cns_pk_models()

    import pandas as pd
    pd.DataFrame(pk_rows).to_csv(OUT_DIR / "batch4_unbound_cns_pk_models.csv", index=False)

    payload = {
        "chembl_and_pubchem": chem,
        "clinical_trials_ctgov_v2": trials,
        "openfda_and_faers": fda,
        "gene_liability_opentargets": gene_liab,
        "europepmc_literature": lit,
        "unbound_cns_pk_models": pk_rows,
    }
    (OUT_DIR / "batch4_tri_pillar_pharmacology_safety.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    print("Saved batch4_tri_pillar_pharmacology_safety.json and batch4_unbound_cns_pk_models.csv")
    for nct, st in trials.items():
        print(f"  {nct}: {st.get('overallStatus')} | hasResults={st.get('hasResults')} | enroll={st.get('enrollmentInfo')} | why={st.get('whyStopped')}")
    for g, gl in gene_liab.items():
        print(f"  Gene {g}: essential={gl.get('is_essential_ot')} chronos={gl.get('depmap_mean_chronos')} pct<-0.5={gl.get('depmap_pct_below_neg0_5')} constraint={gl.get('genetic_constraint')}")


if __name__ == "__main__":
    main()
