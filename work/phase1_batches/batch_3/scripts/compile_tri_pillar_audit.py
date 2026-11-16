"""RUN-B3-004: Consolidate Tri-Pillar external genomics, clinical trials, literature, and gene-liability scoring."""
import json
import os
import subprocess
import urllib.request
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "work/phase1_batches/batch_3/outputs"
API_DIR = OUT_DIR / "api_raw"
OT_DIR = Path(os.environ["OPENTARGETS_SKILL_DIR"]) if os.environ.get("OPENTARGETS_SKILL_DIR") else None

GENES = [
    ("IL1RL1", "ENSG00000115602", "C007"),
    ("CHIT1", "ENSG00000133063", "C017-N1"),
    ("GPNMB", "ENSG00000136235", "C017-N2"),
    ("CHI3L1", "ENSG00000133048", "C017-N3"),
    ("CHI3L2", "ENSG00000064886", "C017-N4"),
    ("C1QA", "ENSG00000173372", "C018-N1"),
    ("C1QB", "ENSG00000173369", "C018-N2"),
    ("C1QC", "ENSG00000159189", "C018-N3"),
    ("C3", "ENSG00000125730", "C018-N4"),
    ("C4B", "ENSG00000224389", "C018-N5"),
]

# Transparent T1/T2/T3 scoring per tooluniverse-gene-liability rubric (DepMap metadata-only => dim5 unavailable, coverage=90%)
LIABILITY_CURATION = {
    "IL1RL1": (0, 8, 12, 5, "T1/T2: Tolerant to LoF (pLI=4.9e-7, LOEUF=0.845); Il1rl1-/- mice viable with impaired Th2/Treg tissue repair; high lung/adrenal/vascular TPM; peripheral anti-ST2 astegolimab well tolerated in Ph2/3 COPD/asthma, CNS sST2 vs ST2L untested", "Isoform-selective sST2 neutralization or BBB-shuttled decoy blockade sparing Treg ST2L"),
    "CHIT1": (0, 8, 6, 0, "T1/T2: Common human 24-bp exon-10 null duplication rs3831317 (AF=0.220, 40,441 homozygotes in gnomAD) benign & does not alter ALS susceptibility or survival; Chit1-/- mice viable with altered chitin/fungal clearance; OATD-01 Ph2 tolerated", "No ALS causal rationale (human genetic LoF does not protect against ALS); genotype-adjusted CSF biomarker"),
    "GPNMB": (0, 8, 12, 12, "T1/T2: LoF tolerant in gnomAD (pLI=2.9e-29, LOEUF=1.509; human truncating alleles cause autosomal-recessive amyloidosis cutis dyschromica); PD 7p15 GWAS risk increases expression yet functional ALS/TDP-43 models show GPNMB is neuroprotective/pro-lysosomal", "DO NOT INHIBIT in ALS (wrong therapeutic sign); utilize CSF GPNMB as DAM/lysosomal PD biomarker"),
    "CHI3L1": (5, 8, 12, 5, "T2/T3: Borderline LoF tolerance (pLI=3.4e-8, LOEUF=0.999); Chil1-/- mice viable with altered lung/neuroimmune inflammation; broad liver/astrocyte/lung expression; pseudochitinase lacking catalytic pocket", "Reclassify as reactive astroglial/white-matter CSF stage biomarker rather than Track B enzyme target"),
    "CHI3L2": (0, 0, 6, 0, "T2/T3: Fully LoF tolerant (pLI=2.1e-16, LOEUF=1.266); lacks murine ortholog (human/primate pseudochitinase); low-to-moderate tissue expression; no known human LoF pathology", "Reclassify as human CSF stage/progression biomarker alongside CHIT1/CHI3L1"),
    "C1QA": (15, 18, 12, 20, "T1/T2: Intermediate LoF constraint (pLI=0.271, o/e=0.435); homozygous human C1QA deficiency causes >90% penetrant systemic lupus erythematosus (SLE) & encapsulated bacterial infections; C1qa-/- mice develop glomerulonephritis/autoimmunity", "Avoid chronic systemic ablation; requires transient or CNS-restricted C1q modulation with meningococcal/pneumococcal prophylaxis"),
    "C1QB": (15, 18, 12, 20, "T1/T2: Intermediate LoF constraint (pLI=0.284, o/e=0.432); human C1QB deficiency causes severe early-onset SLE & encapsulated bacterial sepsis; C1qb-/- mice show impaired immune-complex clearance", "Avoid chronic systemic ablation; CNS-compartmentalized biomarker-stratified dosing + vaccination mandatory"),
    "C1QC": (5, 18, 12, 20, "T1/T2: Human homozygous C1QC deficiency causes severe SLE & recurrent encapsulated bacterial infections; mouse KO impairs apoptotic body clearance", "Avoid chronic systemic ablation; requires CNS-targeted transient blockade + vaccination"),
    "C3": (15, 18, 20, 20, "T1/T2: Constrained o/e=0.467 (LOEUF=0.552); human C3 deficiency causes severe pyogenic/encapsulated bacterial infections & immune-complex renal disease; massive hepatic synthesis; pegcetacoplan requires REMS vaccination & failed ALS Ph2 MERIDIAN", "No-go for systemic C3 monotherapy in ALS (clinically falsified in MERIDIAN NCT04579666 + high infection liability)"),
    "C4B": (25, 8, 12, 12, "T1/T2: Strong gnomAD apparent constraint (pLI=1.00, LOEUF=0.257, complicated by RCCX multi-copy CNV); human C4B deficiency increases encapsulated bacterial infection & autoimmune risk", "No-go as ALS drug target; structural CNV confounds bulk/CSF interpretation"),
}


def fetch_ot_safety_mouse():
    out_p = API_DIR / "ot_safety_mouse_all10.json"
    if out_p.exists():
        return json.loads(out_p.read_text(encoding="utf-8"))
    q = (
        "query($ids: [String!]!) { targets(ensemblIds: $ids) { id approvedSymbol "
        "safetyLiabilities { event effects { direction } biosamples { tissueLabel } } "
        "mousePhenotypes { modelPhenotypeLabel modelPhenotypeClasses { label } } } }"
    )
    if OT_DIR and OT_DIR.is_dir():
        vars_str = json.dumps({"ids": [g[1] for g in GENES]})
        subprocess.run(
            ["uv", "run", "--project", str(OT_DIR), str(OT_DIR / "scripts" / "query_opentargets.py"),
             "--limit", "40", "--output", str(out_p), "custom-query", q, "--variables", vars_str],
            check=True, capture_output=True, text=True, timeout=60,
        )
        return json.loads(out_p.read_text(encoding="utf-8"))
    req = urllib.request.Request(
        "https://api.platform.opentargets.org/api/v4/graphql",
        data=json.dumps({"query": q, "variables": {"ids": [g[1] for g in GENES]}}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8")).get("data", {})
    out_p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def summarize_gtex(sym: str) -> dict:
    p = API_DIR / f"gtex_{sym.lower()}_expr.json"
    if not p.exists():
        return {}
    rows = json.loads(p.read_text(encoding="utf-8"))
    by_t = {r["tissueSiteDetailId"]: float(r["median"]) for r in rows if "tissueSiteDetailId" in r}
    top5 = sorted(by_t.items(), key=lambda x: x[1], reverse=True)[:5]
    return {
        "top5_tissues_tpm": [{ "tissue": k, "tpm": round(v, 3)} for k, v in top5],
        "Brain_Frontal_Cortex_BA9_tpm": round(by_t.get("Brain_Frontal_Cortex_BA9", 0.0), 4),
        "Brain_Spinal_cord_cervical_c-1_tpm": round(by_t.get("Brain_Spinal_cord_cervical_c-1", 0.0), 4),
        "Brain_Cerebellum_tpm": round(by_t.get("Brain_Cerebellum", 0.0), 4),
        "Lung_tpm": round(by_t.get("Lung", 0.0), 4),
        "Liver_tpm": round(by_t.get("Liver", 0.0), 4),
        "Whole_Blood_tpm": round(by_t.get("Whole_Blood", 0.0), 4),
    }


def main():
    ot_sm = fetch_ot_safety_mouse()
    ot_map = {t["id"]: t for t in ot_sm.get("targets", [])}
    tu_raw = json.loads((API_DIR / "tu_gene_liability_raw.json").read_text(encoding="utf-8"))

    liab_rows = []
    gene_profiles = {}
    for sym, ensg, node in GENES:
        gn = json.loads((API_DIR / f"gnomad_{sym}.json").read_text(encoding="utf-8"))["data"]["gene"]["gnomad_constraint"]
        ot_d = json.loads((API_DIR / f"ot_drug_{sym}.json").read_text(encoding="utf-8")).get("target", {})
        ot_dis = json.loads((API_DIR / f"ot_dis_{sym}.json").read_text(encoding="utf-8")).get("target", {}).get("associatedDiseases", {})
        tract_true = [f"{t['modality']}:{t['label']}" for t in ot_d.get("tractability", []) if t.get("value")]
        drugs = tu_raw.get(sym, {}).get("associated_drugs", {}).get("data", {}).get("target", {}).get("drugAndClinicalCandidates", {}).get("rows", [])
        drug_names = [f"{d['drug']['name']} ({d.get('maxClinicalStage')})" for d in drugs]
        mp_labels = [m["modelPhenotypeLabel"] for m in ot_map.get(ensg, {}).get("mousePhenotypes", [])[:8]]
        saf_events = [s["event"] for s in ot_map.get(ensg, {}).get("safetyLiabilities", []) if s.get("event")]

        p_const, p_mouse, p_expr, p_ontarget, rationale, strategy = LIABILITY_CURATION[sym]
        avail_wt = 90  # DepMap returned metadata-only without CRISPR effect scores => dim5 marked unavailable per skill rule
        pts = p_const + p_mouse + p_expr + p_ontarget
        score = round(100.0 * pts / avail_wt, 1)
        band = "low" if score < 25 else ("moderate" if score < 50 else ("high" if score < 75 else "very high"))

        gtex_s = summarize_gtex(sym)
        liab_rows.append({
            "node_id": node, "gene_symbol": sym, "ensembl_id": ensg,
            "pli": round(float(gn["pli"]), 6), "oe_lof": round(float(gn["oe_lof"]), 4), "loeuf": round(float(gn["oe_lof_upper"]), 4),
            "dim1_constraint_25": p_const, "dim2_mouse_ko_25": p_mouse, "dim3_organ_expr_20": p_expr,
            "dim4_ontarget_20": p_ontarget, "dim5_depmap_10": "UNAVAILABLE_METADATA_ONLY",
            "points_earned": pts, "available_weight": avail_wt, "coverage_pct": 90,
            "liability_score_0_100": score, "liability_band": band, "confidence": "High",
            "known_drugs": "; ".join(drug_names) if drug_names else "None in OpenTargets clinical pipeline",
            "tractability_flags": "; ".join(tract_true[:6]),
            "rationale": rationale, "modulation_strategy": strategy,
        })
        gene_profiles[sym] = {
            "node_id": node, "ensembl_id": ensg, "gnomad_constraint": gn, "gtex_v10": gtex_s,
            "opentargets_tractability_positive": tract_true, "opentargets_drugs": drug_names,
            "opentargets_top_diseases": [r["disease"]["name"] for r in ot_dis.get("rows", [])[:8]],
            "opentargets_mouse_phenotypes": mp_labels, "opentargets_safety_events": saf_events,
            "gene_liability": liab_rows[-1],
        }

    # Summarize L2G GWAS hits for rs199347 (GPNMB) and rs1420101 (IL1RL1)
    l2g_summary = {}
    for rs, fn in [("rs199347_GPNMB_7p15", "ot_l2g_rs199347.json"), ("rs1420101_IL1RL1_2q12", "ot_l2g_rs1420101.json")]:
        cs = json.loads((API_DIR / fn).read_text(encoding="utf-8")).get("credibleSets", {})
        gwas_rows = []
        for r in cs.get("rows", []):
            st = r.get("study", {})
            if st.get("studyType") == "gwas":
                preds = r.get("l2GPredictions", {}).get("rows", [])
                top_p = preds[0] if preds else {}
                gwas_rows.append({
                    "study_id": st.get("id"), "trait": st.get("traitFromSource"),
                    "top_gene": top_p.get("target", {}).get("approvedSymbol"), "l2g_score": top_p.get("score"),
                })
        l2g_summary[rs] = {"total_credible_sets": cs.get("count"), "returned_rows": len(cs.get("rows", [])), "gwas_l2g_hits": gwas_rows[:15]}

    # Summarize EuropePMC Open-Access Paper URLs
    epmc_urls = []
    for p in sorted(API_DIR.glob("epmc_*.json")):
        res = json.loads(p.read_text(encoding="utf-8")).get("results", [])
        for r in res[:6]:
            pmid = r.get("pmid")
            pmcid = r.get("pmcid")
            url = f"https://europepmc.org/article/MED/{pmid}" if pmid else (f"https://europepmc.org/articles/{pmcid}" if pmcid else "")
            if url:
                epmc_urls.append({"query_file": p.name, "pmid": pmid, "pmcid": pmcid, "year": r.get("pubYear"), "title": r.get("title"), "url": url})

    pd.DataFrame(liab_rows).to_csv(OUT_DIR / "run_b3_004_gene_liability.csv", index=False)
    (OUT_DIR / "run_b3_004_tri_pillar_summary.json").write_text(
        json.dumps({"gene_profiles": gene_profiles, "l2g_summary": l2g_summary, "europepmc_sources": epmc_urls}, indent=2),
        encoding="utf-8",
    )
    print("Saved run_b3_004_gene_liability.csv and run_b3_004_tri_pillar_summary.json")


if __name__ == "__main__":
    main()
