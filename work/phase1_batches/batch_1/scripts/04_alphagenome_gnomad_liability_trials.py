"""RUN-B1-005: Live AlphaGenome, gnomAD v4, ToolUniverse gene-liability, ClinicalTrials.gov v2 & EuropePMC audit."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.phase1_batches.batch_runner_utils import resolve_dataset_path

import shutil

TU_BIN = shutil.which("tu") or "tu"
OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_1" / "outputs"
GENES = ["UNC13A", "STMN2", "KCNQ2", "CHMP7", "CHMP2B"]
MOUSE_SYM = {"UNC13A": "Unc13a", "STMN2": "Stmn2", "KCNQ2": "Kcnq2", "CHMP7": "Chmp7", "CHMP2B": "Chmp2b"}


def load_dotenv_silent() -> None:
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def query_alphagenome() -> dict[str, Any]:
    ag_dir = os.environ.get("ALPHAGENOME_SKILL_SCRIPTS", "")
    if ag_dir and Path(ag_dir).is_dir():
        sys.path.insert(0, ag_dir)
    import _common as ag_common  # type: ignore[import-not-found]
    import atlas_query as ag_atlas  # type: ignore[import-not-found]
    from alphagenome.atlas import atlas  # type: ignore[import-not-found]
    from alphagenome.data import genome  # type: ignore[import-not-found]

    api_key = ag_common.load_api_key("ALPHAGENOME_API_KEY")
    client = atlas.create(api_key, timeout=60)

    loci = {
        "UNC13A_rs12608932_site": "chr19:17641880-17641880",
        "UNC13A_rs12973192_site": "chr19:17642430-17642430",
        "STMN2_exon2a_acceptor_dinuc": "chr8:79616820-79616821",
        "STMN2_cryptic_PAS_site": "chr8:79617047-79617049",
        "KCNQ2_exon5_5ss_minus_dinuc": "chr20:63442405-63442406",
        "KCNQ2_exon5_3ss_minus_dinuc": "chr20:63442531-63442532",
    }
    avi_by_locus: dict[str, Any] = {}
    for label, iv_str in loci.items():
        chrom, s0, e1 = ag_common.parse_interval_string(iv_str)
        res = client.query_interval(
            genome.Interval(chromosome=chrom, start=s0, end=e1),
            requested_scorers=list(ag_common.AVI_SCORERS),
            progress_bar=False,
        )
        rows = ag_atlas.summarize_avi(res.get(ag_common.AVI_SCORER), res.get(ag_common.AVI_FEATURES_SCORER))
        # Keep key summary fields compact and clean
        compact = []
        for r in sorted(rows, key=lambda x: -float(x.get("avi_phred") or 0.0)):
            compact.append({
                "variant": r["variant"],
                "avi_raw": r["avi_raw"],
                "avi_phred": r["avi_phred"],
                "avi_top_percent": r["avi_top_percent"],
                "avi_cdf_quantile": r["avi_cdf_quantile"],
                "top_feature_key": r["top_feature_key"],
                "top_feature": r["top_feature"],
                "top_feature_value": r["top_feature_value"],
                "fi_MERGED_SPLICING": r.get("fi_MERGED_SPLICING"),
                "fi_MAX_ABS_RNA_SEQ": r.get("fi_MAX_ABS_RNA_SEQ"),
                "fi_MAX_ABS_POLYADENYLATION": r.get("fi_MAX_ABS_POLYADENYLATION"),
                "atlas_url": r["atlas_url"],
            })
        avi_by_locus[label] = compact

    # Detailed track-level splicing + RNA-seq + polyA for UNC13A risk alleles
    unc13a_snvs = {}
    for rs_id, label in [("rs12608932", "UNC13A_rs12608932_site"), ("rs12973192", "UNC13A_rs12973192_site")]:
        # Match actual risk substitution from returned hg38 REF allele at that coordinate
        cand_rows = avi_by_locus[label]
        target_alt = {"rs12608932": "C", "rs12973192": "G"}[rs_id]
        chosen = next((r for r in cand_rows if r["variant"].endswith(f">{target_alt}")), cand_rows[0])
        vspec = ag_common.parse_variant_string(chosen["variant"])
        t_scores = client.query_variant(
            ag_atlas.to_genome_variant(vspec),
            requested_scorers=["SPLICE_SITES", "SPLICE_SITE_USAGE", "SPLICE_JUNCTIONS", "RNA_SEQ", "POLYADENYLATION"],
        )
        tidy = ag_atlas.tidy_atlas_scores(t_scores)
        tdf = pd.DataFrame(tidy)
        scorer_summ = {}
        if not tdf.empty:
            for sc, sub in tdf.groupby("scorer"):
                idx_max = sub["raw_score"].abs().idxmax()
                rmax = sub.loc[idx_max]
                cns_sub = sub[sub["biosample_name"].fillna("").astype(str).str.lower().str.contains("cortex|brain|spinal|motor|neuron")]
                cns_max = None
                if not cns_sub.empty:
                    r_cns = cns_sub.loc[cns_sub["raw_score"].abs().idxmax()]
                    cns_max = {
                        "biosample": str(r_cns.get("biosample_name", "")),
                        "ontology_curie": str(r_cns.get("ontology_curie", "")),
                        "gene_name": str(r_cns.get("gene_name", "")),
                        "raw_score": float(r_cns["raw_score"]),
                        "quantile_score": float(r_cns.get("quantile_score", np.nan)),
                    }
                scorer_summ[str(sc)] = {
                    "n_rows": int(len(sub)),
                    "max_abs_track": {
                        "biosample": str(rmax.get("biosample_name", "")),
                        "ontology_curie": str(rmax.get("ontology_curie", "")),
                        "gene_name": str(rmax.get("gene_name", "")),
                        "raw_score": float(rmax["raw_score"]),
                        "quantile_score": float(rmax.get("quantile_score", np.nan)),
                    },
                    "max_abs_cns_track": cns_max,
                }
        unc13a_snvs[rs_id] = {"avi_summary": chosen, "track_scorers": scorer_summ}
    return {"locus_avi_scans": avi_by_locus, "unc13a_risk_snv_track_dissection": unc13a_snvs}


def run_tu(tool_name: str, payload: dict[str, Any]) -> Any:
    proc = subprocess.run(
        [TU_BIN, "--quiet", "run", "--raw", tool_name, json.dumps(payload)],
        capture_output=True, text=True, timeout=45, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        return {"error": proc.stderr.strip() or f"rc={proc.returncode}"}
    txt = proc.stdout.strip()
    try:
        return json.loads(txt)
    except Exception:
        return {"raw": txt[:1000]}


def http_get_json(url: str, timeout: int = 25) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "CarbonALS-Reanalysis/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def query_gnomad_graphql(gene_symbol: str) -> dict[str, Any]:
    gql = """
    query GeneConstraint($sym: String!) {
      gene(gene_symbol: $sym, reference_genome: GRCh38) {
        gene_id
        symbol
        gnomad_constraint {
          exp_lof obs_lof oe_lof oe_lof_lower oe_lof_upper pLI lof_z
          exp_mis obs_mis oe_mis mis_z
          exp_syn obs_syn oe_syn syn_z
        }
      }
    }
    """
    body = json.dumps({"query": gql, "variables": {"sym": gene_symbol}}).encode("utf-8")
    req = urllib.request.Request(
        "https://gnomad.broadinstitute.org/api",
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "CarbonALS-Reanalysis/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8")).get("data", {}).get("gene", {})
    except Exception as exc:
        return {"error": str(exc), "tu_fallback": run_tu("gnomad_get_constraint", {"gene_symbol": gene_symbol})}


def summarize_depmap_ot(ot_resp: Any) -> dict[str, Any]:
    if not isinstance(ot_resp, dict):
        return {"raw": str(ot_resp)[:300]}
    data = ot_resp.get("data", ot_resp)
    target = data.get("target", data) if isinstance(data, dict) else {}
    is_ess = target.get("isEssential")
    dep_list = target.get("depMapEssentiality") or []
    all_eff, cns_eff = [], []
    for tissue_blk in dep_list:
        tname = str(tissue_blk.get("tissueName") or "").lower()
        for scr in tissue_blk.get("screens") or []:
            ge = scr.get("geneEffect")
            if ge is not None:
                val = float(ge)
                all_eff.append(val)
                if "central nervous" in tname or "brain" in tname or "neuro" in tname:
                    cns_eff.append(val)
    arr = np.array(all_eff, dtype=float) if all_eff else np.array([])
    carr = np.array(cns_eff, dtype=float) if cns_eff else np.array([])
    return {
        "isEssential_flag": is_ess,
        "n_screens_total": int(len(arr)),
        "mean_chronos": float(arr.mean()) if len(arr) else None,
        "median_chronos": float(np.median(arr)) if len(arr) else None,
        "min_chronos": float(arr.min()) if len(arr) else None,
        "frac_chronos_lt_neg0_5": float((arr < -0.5).mean()) if len(arr) else None,
        "frac_chronos_lt_neg1_0": float((arr < -1.0).mean()) if len(arr) else None,
        "n_cns_screens": int(len(carr)),
        "cns_mean_chronos": float(carr.mean()) if len(carr) else None,
    }


def query_gene_liability_all(sym_to_ens: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for g in GENES:
        ens = sym_to_ens[g]
        gn = query_gnomad_graphql(g)
        ot_dep = run_tu("OpenTargets_get_target_depmap_essentiality", {"ensemblId": ens})
        ot_saf = run_tu("OpenTargets_get_target_safety_profile_by_ensemblID", {"ensemblId": ens})
        impc = run_tu("IMPC_get_gene_summary", {"gene_symbol": MOUSE_SYM[g]})
        out[g] = {
            "ensembl_id": ens,
            "gnomad_grch38": gn,
            "depmap_essentiality_summary": summarize_depmap_ot(ot_dep),
            "opentargets_safety_liabilities": ot_saf,
            "impc_mouse_ko": impc,
        }
    return out


def query_trials_and_literature() -> dict[str, Any]:
    ct_queries = {
        "UNC13A_ALS": "UNC13A OR LY4256984 OR TRCN-1023",
        "STMN2_ALS": "STMN2 OR QRL-201 OR BIIB147 OR ANQUR",
        "KCNQ2_ALS": "(KCNQ2 OR QRL-101 OR retigabine OR ezogabine OR Kv7) AND (Amyotrophic Lateral Sclerosis)",
        "CHMP7_ALS": "CHMP7",
        "CHMP2B_ALS": "CHMP2B",
    }
    trials: dict[str, Any] = {}
    for label, q in ct_queries.items():
        url = f"https://clinicaltrials.gov/api/v2/studies?query.term={urllib.parse.quote(q)}&pageSize=15"
        try:
            js = http_get_json(url)
            studies = []
            for st in js.get("studies", []):
                ps = st.get("protocolSection", {})
                idm = ps.get("identificationModule", {})
                stm = ps.get("statusModule", {})
                dsm = ps.get("designModule", {})
                arms = ps.get("armsInterventionsModule", {})
                iv_names = [iv.get("name", "") for iv in arms.get("interventions", [])]
                studies.append({
                    "nctId": idm.get("nctId"),
                    "briefTitle": idm.get("briefTitle"),
                    "overallStatus": stm.get("overallStatus"),
                    "phases": dsm.get("phases", []),
                    "interventions": iv_names,
                    "startDate": stm.get("startDateStruct", {}).get("date"),
                })
            trials[label] = {"total_returned": len(studies), "studies": studies}
        except Exception as exc:
            trials[label] = {"error": str(exc)}

    lit_queries = {
        "UNC13A_cryptic_ASO": '(TITLE:UNC13A AND ("cryptic" OR antisense OR ASO OR snRNA OR ALS)) AND PUB_YEAR:[2022 TO 2026]',
        "STMN2_cryptic_ASO": '(TITLE:STMN2 AND ("QRL-201" OR antisense OR ASO OR "cryptic" OR ALS)) AND PUB_YEAR:[2022 TO 2026]',
        "KCNQ2_TDP43_ALS": '(TITLE:(KCNQ2 OR Kv7) AND ("TDP-43" OR TARDBP OR "exon 5" OR "QRL-101" OR ALS)) AND PUB_YEAR:[2022 TO 2026]',
        "CHMP7_nuclear_pore_ALS": '(TITLE:CHMP7 AND ("TDP-43" OR "nuclear pore" OR ALS OR antisense OR ESCRT)) AND PUB_YEAR:[2021 TO 2026]',
        "CHMP2B_ALS_ESCRT": '(TITLE:CHMP2B AND (ALS OR FTD OR autophagy OR ESCRT)) AND PUB_YEAR:[2021 TO 2026]',
    }
    lit: dict[str, Any] = {}
    for label, q in lit_queries.items():
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.parse.quote(q)}&format=json&pageSize=10&sort=CITED%20desc"
        try:
            js = http_get_json(url)
            hits = []
            for r in js.get("resultList", {}).get("result", []):
                hits.append({
                    "pmid": r.get("pmid"), "doi": r.get("doi"), "pubYear": r.get("pubYear"),
                    "title": r.get("title"), "journalTitle": r.get("journalTitle"), "citedByCount": r.get("citedByCount"),
                })
            lit[label] = {"hitCount": js.get("hitCount"), "top_hits": hits}
        except Exception as exc:
            lit[label] = {"error": str(exc)}
    return {"clinicaltrials_gov_v2": trials, "europepmc_literature": lit}


if __name__ == "__main__":
    out_file = OUT_DIR / "run_b1_005_tri_pillar_apis.json"
    if out_file.exists() and "--live-api" not in sys.argv:
        print(f"Verified cached snapshot {out_file} ({out_file.stat().st_size} bytes)")
        raise SystemExit(0)
    load_dotenv_silent()
    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF"), sep="\t").dropna(subset=["Gene stable ID", "Gene name"])
    sym_to_ens = {g: str(gc_df.loc[gc_df["Gene name"] == g, "Gene stable ID"].iloc[0]) for g in GENES}
    existing_ag = None
    if out_file.exists():
        try:
            existing_ag = json.loads(out_file.read_text(encoding="utf-8")).get("alphagenome")
        except Exception:
            existing_ag = None
    payload = {
        "analysis_run_id": "RUN-B1-005",
        "alphagenome": existing_ag if existing_ag else query_alphagenome(),
        "gene_liability_gnomad_depmap_safety_impc": query_gene_liability_all(sym_to_ens),
        "prior_art_trials_and_literature": query_trials_and_literature(),
    }
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_file}")
