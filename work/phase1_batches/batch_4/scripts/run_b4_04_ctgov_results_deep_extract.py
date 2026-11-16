"""RUN-B4-004: Deep extraction of posted ClinicalTrials.gov v2 resultsSection (PK, efficacy, biomarkers, SAEs)."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_4" / "outputs"

TRIALS_WITH_RESULTS = [
    "NCT05508074",  # IFB-088 / Icerguastat Phase 2 TRIALS Bulbar ALS
    "NCT03610334",  # IFB-088 / Icerguastat Phase 1 SAD/MAD PK
    "NCT05189106",  # NADALS Baricitinib ALS/AD
    "NCT05163886",  # AIT-101 / Apilimod Phase 2a C9orf72-ALS
    "NCT05740813",  # HEALEY Regimen F ABBV-CLS-7262 (fosigotifator)
    "NCT05842941",  # HEALEY Regimen G DNL343
]


def fetch_study(nct: str) -> dict:
    req = urllib.request.Request(
        f"https://clinicaltrials.gov/api/v2/studies/{nct}",
        headers={"Accept": "application/json", "User-Agent": "CarbonALS-Phase1-Batch4/1.0"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def summarize_results(d: dict) -> dict:
    rs = d.get("resultsSection") or {}
    pf = rs.get("participantFlowModule") or {}
    om = rs.get("outcomeMeasuresModule") or {}
    ae = rs.get("adverseEventsModule") or {}

    outcomes = []
    for o in (om.get("outcomeMeasures") or []):
        groups = {g["id"]: g.get("title") for g in (o.get("groups") or [])}
        denoms = []
        for dn in (o.get("denoms") or []):
            denoms.append({
                "units": dn.get("units"),
                "counts": {groups.get(c["groupId"], c["groupId"]): c.get("value") for c in (dn.get("counts") or [])},
            })
        classes_out = []
        for cl in (o.get("classes") or []):
            cats_out = []
            for cat in (cl.get("categories") or []):
                meas = {
                    groups.get(m["groupId"], m["groupId"]): {
                        "value": m.get("value"),
                        "spread": m.get("spread"),
                        "lowerLimit": m.get("lowerLimit"),
                        "upperLimit": m.get("upperLimit"),
                    }
                    for m in (cat.get("measurements") or [])
                }
                cats_out.append({"subTitle": cat.get("title"), "measurements": meas})
            classes_out.append({"classTitle": cl.get("title"), "categories": cats_out})

        analyses = [
            {
                "groupIds": [groups.get(gid, gid) for gid in (an.get("groupIds") or [])],
                "paramType": an.get("paramType"),
                "paramValue": an.get("paramValue"),
                "pValue": an.get("pValue"),
                "statisticalMethod": an.get("statisticalMethod"),
                "ciPctValue": an.get("ciPctValue"),
                "ciLowerLimit": an.get("ciLowerLimit"),
                "ciUpperLimit": an.get("ciUpperLimit"),
                "groupDescription": an.get("groupDescription"),
            }
            for an in (o.get("analyses") or [])
        ]
        outcomes.append({
            "type": o.get("type"),
            "title": o.get("title"),
            "timeFrame": o.get("timeFrame"),
            "unitOfMeasure": o.get("unitOfMeasure"),
            "dispersionType": o.get("dispersionType"),
            "denoms": denoms,
            "classes": classes_out,
            "analyses": analyses,
        })

    eg_map = {g["id"]: g.get("title") for g in (ae.get("eventGroups") or [])}
    sae_summary = [
        {
            "group": g.get("title"),
            "seriousNumAffected": g.get("seriousNumAffected"),
            "seriousNumAtRisk": g.get("seriousNumAtRisk"),
            "otherNumAffected": g.get("otherNumAffected"),
            "deathsNumAffected": g.get("deathsNumAffected"),
        }
        for g in (ae.get("eventGroups") or [])
    ]
    return {
        "participant_flow_periods": pf.get("periods"),
        "outcomes": outcomes,
        "adverse_event_group_summary": sae_summary,
    }


def main() -> None:
    extracted = {}
    for nct in TRIALS_WITH_RESULTS:
        d = fetch_study(nct)
        extracted[nct] = summarize_results(d)
        print(f"=== {nct} ({len(extracted[nct]['outcomes'])} outcomes) ===")
        for idx, o in enumerate(extracted[nct]["outcomes"], 1):
            print(f"  [{idx}] ({o['type']}) {o['title']} | unit={o['unitOfMeasure']} | analyses={len(o['analyses'])}")
            for an in o["analyses"][:2]:
                print(f"      -> p={an['pValue']} {an['paramType']}={an['paramValue']} [{an['ciLowerLimit']}, {an['ciUpperLimit']}] ({an['statisticalMethod']})")
        print("  SAE summary:", extracted[nct]["adverse_event_group_summary"])

    (OUT_DIR / "batch4_ctgov_posted_results.json").write_text(
        json.dumps(extracted, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
