"""RUN-B2-004: Consolidate gnomAD v4, AlphaGenome GTF/AVI, and 5D Gene Liability scores."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_2" / "outputs"
CACHE_DIR = OUT_DIR / "api_cache_b2_004"

# Curated mammalian KO & Mendelian T1/T2 annotations cross-referenced with MGI IDs retrieved by OpenTargets
MAMMALIAN_AND_MENDELIAN = {
    "SCFD1": (25, "T2", "IMPC MGI:6383384 (Scfd1<em1(IMPC)Tcp> het early only; pre-weaning homozygous lethality; zebrafish scfd1 KO lethal neuromuscular defect)", 5, "T3", "No single-gene Mendelian LoF syndrome in ClinVar (23 records are 14q12 contiguous-gene CNVs); common ALS risk eQTL rs229143 increases expression"),
    "G2E3": (25, "T2", "Brooks et al. PNAS 2008 gene-trap KO embryonic lethal via massive blastocyst apoptosis; IMPC MGI:6156577 early phenotypes", 5, "T3", "No single-gene Mendelian syndrome in ClinVar (22 records are 14q12 multi-gene CNVs); 14q12 sQTL rs229190 modulates exon-2 skipping"),
    "YKT6": (25, "T2", "Pan-eukaryotic essential R-SNARE; biallelic hypomorphic variants cause severe congenital neurodevelopmental/hepatocerebral disorder", 20, "T1", "Human causal genetics: Hop 2026 ALS rare missense p.Tyr64Cys (OR=2.84, P=9.08e-8) + biallelic human developmental encephalopathy/liver disease"),
    "SEC22B": (18, "T2", "Essential ER-Golgi R-SNARE in hematopoiesis/dendritic cross-presentation; conditional mouse KO impairs ER-phagy/secretory trafficking", 5, "T3", "0 single-gene pathogenic ClinVar variants; paralogous compensation with SEC22A/SEC22C uncertain in neurons"),
    "STX5": (25, "T2", "IMPC MGI:5692753 (Stx5a<tm1b(EUCOMM)Hmgu> het early only; homozygous embryonic lethality); essential cis-Golgi Qa-SNARE", 20, "T1", "Human congenital disorder of glycosylation (STX5-CDG): biallelic hypomorphic/splicing loss causes lethal multisystem hepatocerebral failure"),
    "GOSR1": (18, "T2", "Essential cis-Golgi Qb-SNARE; hypomorphic loss causes severe progressive neurological/Golgi trafficking phenotypes", 20, "T1", "Human GOSR1 progressive myoclonic epilepsy (PME / GOSR1-related encephalopathy, homozygous p.Gly144Trp)"),
    "NSF": (25, "T2", "IMPC MGI:5446014 (Nsf<tm1b(KOMP)Mbp> het early only; homozygous embryonic lethality) + MGI:7531415 (PMID:34745222)", 20, "T1", "Human dominant Developmental and Epileptic Encephalopathy 96 (DEE96, OMIM 619340): heterozygous de novo missense causes infantile intractable epilepsy/early death"),
    "GDI2": (18, "T2", "IMPC MGI:5588293 (Gdi2<tm1b(EUCOMM)Hmgu> het early; pre-weaning subviability/lethality); paralog GDI1 partially overlaps in brain", 5, "T3", "0 single-gene Mendelian pathogenic variants in ClinVar; ubiquitous Rab GDP-dissociation inhibitor"),
    "FBXL5": (25, "T2", "MGI:5295290 (Fbxl5<tm1Kei>/Fbxl5<tm1Kei>, Moroishi Cell Metab 2011 PMID:21907140): embryonic lethal ~E8.5 from fatal iron overload, rescued by Ireb2 deletion", 5, "T3", "0 single-gene Mendelian LoF diseases in ClinVar; CarbonALS hypothesis is FBXL5 stabilization/activation (not inhibition)"),
    "IREB2": (18, "T2", "MGI:5796139 / MGI:3584280 (Ireb2-/-, LaVaute Nat Genet 2001 PMID:11175792): viable with microcytic anemia + adult-onset progressive neurodegeneration/motor axonopathy", 20, "T1", "ClinVar IDs 633461 (p.Gly357Ter) & 633460 (p.Arg419Ter): biallelic LoF causes human early-onset neurodegeneration with choreoathetosis & microcytic anemia (OMIM 618451)"),
}


def score_constraint(gc: dict | None) -> tuple[int, str]:
    if not gc:
        return 5, "Constraint unavailable"
    pli = float(gc.get("pli") or 0.0)
    oe_lof = float(gc.get("oe_lof") or 1.0)
    oe_up = float(gc.get("oe_lof_upper") or 1.0)
    oe_mis = float(gc.get("oe_mis") or 1.0)
    if pli >= 0.90 and (oe_up <= 0.35 or oe_lof <= 0.35):
        pts = 25
    elif pli >= 0.90 or oe_lof <= 0.42 or oe_mis <= 0.70:
        pts = 15
    elif oe_lof <= 0.65:
        pts = 5
    else:
        pts = 0
    return pts, f"gnomAD v4 pLI={pli:.4f}, oe_lof={oe_lof:.4f} (LOEUF={oe_up:.4f}), oe_mis={oe_mis:.4f}"


def score_expression(gt: dict) -> tuple[int, str]:
    if not gt.get("available"):
        return 12, "GTEx unavailable"
    crit = gt.get("critical_organs_tpm", {})
    n_high = sum(1 for v in crit.values() if v >= 15.0)
    med = float(gt.get("median_across_tissues_tpm", 0.0))
    if n_high >= 3 or med >= 20.0:
        pts = 20
    elif n_high >= 1 or med >= 5.0:
        pts = 12
    else:
        pts = 6
    return pts, f"GTEx v8 median_TPM={med:.2f}, max_TPM={gt['max_tpm']:.2f}, critical_organs_ge15TPM={n_high}"


def score_depmap(dep_sum: dict | None) -> tuple[int | None, str]:
    if not dep_sum or not dep_sum.get("available"):
        return None, "DepMap Chronos unavailable"
    mean_c = float(dep_sum["mean_chronos"])
    med_c = float(dep_sum["median_chronos"])
    min_c = float(dep_sum["min_chronos"])
    n_tot = int(dep_sum["n_screens_total"])
    f_lt1 = float(dep_sum["frac_chronos_lt_neg1_0"])
    is_ess = bool(dep_sum.get("isEssential_flag"))
    if is_ess or mean_c <= -1.0 or f_lt1 >= 0.50:
        pts = 10
    elif mean_c <= -0.5 or float(dep_sum["frac_chronos_lt_neg0_5"]) >= 0.25:
        pts = 6
    elif mean_c <= -0.20:
        pts = 3
    else:
        pts = 0
    cns_val = dep_sum.get("cns_mean_chronos")
    neu_val = dep_sum.get("neural_all_mean_chronos")
    cns_part = f", CNS_mean={cns_val:.3f} (n={dep_sum.get('n_cns_screens')})" if cns_val is not None else (
        f", Neural_mean={neu_val:.3f} (n={dep_sum.get('n_neural_all_screens')})" if neu_val is not None else ""
    )
    return (
        pts,
        f"OpenTargets DepMap CRISPR Chronos (n={n_tot} lines): isEssential={is_ess}, "
        f"mean={mean_c:.4f}, median={med_c:.4f}, min={min_c:.4f}, frac<-1.0={f_lt1:.3f}{cns_part}",
    )


def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p1 = json.loads((CACHE_DIR / "part1_gnomad_alphagenome.json").read_text(encoding="utf-8"))
    p2 = json.loads((CACHE_DIR / "part2_tooluniverse_raw.json").read_text(encoding="utf-8"))
    p3_path = CACHE_DIR / "part3_opentargets_depmap.json"
    p3 = json.loads(p3_path.read_text(encoding="utf-8")) if p3_path.exists() else {}

    liability_profiles = {}
    for sym, tu_rec in p2.items():
        gc = (p1["gnomad_v4_constraints"].get(sym) or {}).get("gnomad_constraint")
        c_pts, c_ev = score_constraint(gc)
        e_pts, e_ev = score_expression(tu_rec["gtex_summary"])
        m_pts, m_tier, m_ev, o_pts, o_tier, o_ev = MAMMALIAN_AND_MENDELIAN[sym]
        dep_sum = (p3.get(sym) or {}).get("summary")
        d_pts, d_ev = score_depmap(dep_sum)
        if d_pts is not None:
            avail_weight = 100
            earned = c_pts + m_pts + e_pts + o_pts + d_pts
            cov_pct = 100.0
            dep_dim = {"points": d_pts, "max": 10, "tier": "T2", "evidence": d_ev, "summary": dep_sum}
        else:
            avail_weight = 90
            earned = c_pts + m_pts + e_pts + o_pts
            cov_pct = 90.0
            dep_dim = {"points": None, "max": 10, "status": "UNAVAILABLE"}
        score_100 = round(100.0 * earned / avail_weight, 2)
        band = "very_high" if score_100 >= 75 else ("high" if score_100 >= 50 else ("moderate" if score_100 >= 25 else "low"))
        conf = "High" if o_tier == "T1" else "Moderate"
        cv_vars = tu_rec["clinvar_pathogenic"].get("data", {}).get("variants", [])
        single_cv = [v for v in cv_vars if isinstance(v, dict) and v.get("genes") == [sym]]
        liability_profiles[sym] = {
            "symbol": sym,
            "ensembl_id": tu_rec["ensembl_id"],
            "intervention_assumption": "Complete systemic loss of function / pan-cellular inhibition (baseline safety screen)",
            "liability_score_0_100": score_100,
            "liability_band": band,
            "evidence_coverage_pct": cov_pct,
            "confidence": conf,
            "dimensions": {
                "human_genetic_constraint_w25": {"points": c_pts, "max": 25, "tier": "T2", "evidence": c_ev},
                "mammalian_knockout_w25": {"points": m_pts, "max": 25, "tier": m_tier, "evidence": m_ev},
                "critical_organ_expression_w20": {"points": e_pts, "max": 20, "tier": "T3", "evidence": e_ev},
                "observed_ontarget_effects_w20": {"points": o_pts, "max": 20, "tier": o_tier, "evidence": o_ev, "single_gene_clinvar_records": len(single_cv)},
                "cellular_essentiality_w10": dep_dim,
            },
            "disclaimer": "This is a research risk assessment, not a clinical safety determination.",
        }

    out_payload = {
        "analysis_run_id": "RUN-B2-004",
        "gnomad_v4_constraints": p1["gnomad_v4_constraints"],
        "gnomad_v4_variants": p1["gnomad_v4_variants"],
        "alphagenome_gencode_v46_gtf_summary": {
            g: {
                "gene_id": recs[0]["gene_id"], "transcript_id": recs[0]["transcript_id"],
                "strand": recs[0]["strand"], "num_exons": recs[0]["num_exons"],
                "span": f"{recs[0]['chromosome']}:{recs[0]['start']}-{recs[0]['end']}",
            }
            for g, recs in p1["alphagenome_gencode_v46_gtf"].items() if isinstance(recs, list) and recs
        },
        "alphagenome_avi_variant_scores": p1["alphagenome_avi_scores"],
        "gene_liability_5d_profiles": liability_profiles,
    }
    out_file = OUT_DIR / "b2_004_genetics_alphagenome_liability.json"
    out_file.write_text(json.dumps(out_payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_file} ({out_file.stat().st_size} bytes)")
    for sym, prof in liability_profiles.items():
        print(f"  {sym:7s}: liability={prof['liability_score_0_100']:5.1f} ({prof['liability_band']}), conf={prof['confidence']}, constraint={prof['dimensions']['human_genetic_constraint_w25']['evidence']}")


if __name__ == "__main__":
    main()
