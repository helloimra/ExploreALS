"""Cache DN-04 CELF5 GTEx v8, Open Targets v4 safety/mouse/GWAS, GENCODE v46 exon frame, & NYGC spinal summary for Phase 4."""
from __future__ import annotations

import gzip
import json
from pathlib import Path
import re
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
P3A_SCRIPTS = ROOT / "work" / "phase3a_execution_safety" / "scripts"
for p in (SRC, P3A_SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _offtarget_helpers import load_gnomad_v41_constraint_map  # noqa: E402
from carbon_als.loaders import resolve_dataset_path  # noqa: E402

CACHE_FP = ROOT / "work" / "phase4_final_synthesis" / "cache" / "celf5_target_profile.json"
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)


def _http_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json", "User-Agent": "CarbonALS/1.0"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_gtex_v8_celf5() -> dict:
    ref = _http_json("https://gtexportal.org/api/v2/reference/gene?geneId=CELF5&gencodeVersion=v26&genomeBuild=GRCh38%2Fhg38")
    gid = ref["data"][0]["gencodeId"]
    qs = urllib.parse.urlencode({"gencodeId": gid, "datasetId": "gtex_v8", "itemsPerPage": 100})
    med = _http_json(f"https://gtexportal.org/api/v2/expression/medianGeneExpression?{qs}")
    out = {"gencode_id": gid}
    for row in med.get("data", []):
        out[row["tissueSiteDetailId"]] = round(float(row["median"]), 4)
    return out


def fetch_opentargets_celf5() -> dict:
    query = """
    query Celf5Safety($ensg: String!) {
      target(ensemblId: $ensg) {
        id approvedSymbol
        geneticConstraint { constraintType exp obs score oe oeLower oeUpper }
        safetyLiabilities { event biosamples { tissueLabel } }
        mousePhenotypes { modelPhenotypeLabel modelPhenotypeClasses { label } }
        associatedDiseases(page: {size: 50, index: 0}) {
          count
          rows { disease { id name } score datatypeScores { id score } }
        }
      }
    }
    """
    res = _http_json("https://api.platform.opentargets.org/api/v4/graphql", {"query": query, "variables": {"ensg": "ENSG00000161082"}})
    t = res["data"]["target"]
    assoc_rows = t.get("associatedDiseases", {}).get("rows", []) or []
    als_assoc = [
        r for r in assoc_rows
        if "amyotrophic" in (r.get("disease", {}).get("name") or "").lower()
        or (r.get("disease", {}).get("id") or "") in {"MONDO_0004976", "EFO_0000253"}
    ]
    als_genetic_score = 0.0
    for r in als_assoc:
        for ds in r.get("datatypeScores") or []:
            if ds.get("id") == "genetic_association":
                als_genetic_score = max(als_genetic_score, float(ds.get("score") or 0.0))
    return {
        "ensembl_id": t["id"],
        "approved_symbol": t["approvedSymbol"],
        "ot_genetic_constraint": t.get("geneticConstraint") or [],
        "n_safety_liabilities": len(t.get("safetyLiabilities") or []),
        "safety_liabilities": t.get("safetyLiabilities") or [],
        "n_mouse_phenotypes": len(t.get("mousePhenotypes") or []),
        "mouse_phenotype_labels": sorted({m["modelPhenotypeLabel"] for m in (t.get("mousePhenotypes") or []) if m.get("modelPhenotypeLabel")}),
        "total_associated_diseases": int(t.get("associatedDiseases", {}).get("count") or 0),
        "als_associated_rows": als_assoc,
        "als_ot_genetic_association_score": round(als_genetic_score, 6),
    }


def inspect_celf5_mane_gtf() -> dict:
    gtf_fp = resolve_dataset_path("DS_GENCODE_V46_COMP_GTF", verify_hash=True)
    mane_tid, exons, cds = None, [], []
    with gzip.open(gtf_fp, "rt", encoding="utf-8") as fh:
        for ln in fh:
            if not ln.startswith("chr19\t") or 'gene_name "CELF5"' not in ln:
                continue
            p = ln.rstrip("\n").split("\t")
            feat, s, e, attr = p[2], int(p[3]), int(p[4]), p[8]
            if "MANE_Select" in attr:
                m = re.search(r'transcript_id "([^"]+)"', attr)
                if m:
                    mane_tid = m.group(1)
                if feat == "exon":
                    exons.append((s, e))
                elif feat == "CDS":
                    cds.append((s, e))
    exons.sort()
    cds.sort()
    up_cds_nt = sum(e - s + 1 for s, e in cds if e < 3278209)
    tot_cds_nt = sum(e - s + 1 for s, e in cds)
    ce_len = 3278316 - 3278209 + 1
    up_exons = [e for _, e in exons if e < 3278209]
    up_intron_len = 3278209 - up_exons[-1] - 1
    req = urllib.request.Request(
        "https://rest.ensembl.org/sequence/region/human/19:3278209..3278316?coord_system_version=GRCh38",
        headers={"Accept": "text/plain", "User-Agent": "CarbonALS/1.0"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        ce_seq = resp.read().decode("utf-8").strip().upper()
    ptc_1b = [idx + 1 for idx in range(ce_len // 3) if ce_seq[3 * idx : 3 * idx + 3] in {"TAA", "TAG", "TGA"}]
    del ce_seq
    return {
        "mane_transcript": mane_tid,
        "n_mane_exons": len(exons),
        "total_protein_aa": tot_cds_nt // 3,
        "upstream_cds_nt_before_ce": up_cds_nt,
        "upstream_aa_before_ce": up_cds_nt // 3,
        "upstream_exon_phase_mod3": up_cds_nt % 3,
        "cryptic_exon_coords_1b": "chr19:3278209-3278316(+)",
        "cryptic_exon_length_bp": ce_len,
        "cryptic_exon_len_mod3": ce_len % 3,
        "flanking_mane_exons_1b": [f"chr19:{s}-{e}(+)" for s, e in exons if e < 3278209][-1:] + [f"chr19:{s}-{e}(+)" for s, e in exons if s > 3278316][:1],
        "inframe_ptc_codon_indices_1b": ptc_1b,
        "upstream_intron_len_bp": up_intron_len,
    }


def main() -> None:
    CACHE_FP.parent.mkdir(parents=True, exist_ok=True)
    gnomad_map = load_gnomad_v41_constraint_map(resolve_dataset_path("DS_GNOMAD_V41_CONSTRAINT", verify_hash=True))
    ext_main = json.loads((ROOT / "work" / "phase3b_denovo_discovery" / "cache" / "external_priors_and_structures.json").read_text(encoding="utf-8"))
    d4 = json.loads((ROOT / "work" / "phase3b_denovo_discovery" / "outputs" / "run_p3b_004_targeted_deep_dive.json").read_text(encoding="utf-8"))

    gtex = fetch_gtex_v8_celf5()
    ot = fetch_opentargets_celf5()
    gtf_info = inspect_celf5_mane_gtf()
    gm = gnomad_map.get("CELF5", {})
    dm = ext_main["opentargets_depmap"]["CELF5"]
    cns_vals = {k: v for k, v in gtex.items() if k != "gencode_id" and k.startswith("Brain_")}
    non_cns = {k: v for k, v in gtex.items() if k != "gencode_id" and not k.startswith("Brain_")}
    max_nc = max(non_cns, key=non_cns.get)
    max_cns = max(cns_vals, key=cns_vals.get)

    nygc_regs = d4["nygc_multiregion_donor_analysis"]["regions"]
    f1_f2_genes = ["ATG4B", "KALRN", "PTPRT", "CELF5", "PRUNE2", "PFKP", "TRAPPC12", "ELK1", "DLGAP1"]
    panel_nygc = {
        g: {reg: nygc_regs[reg]["genes"].get(g) for reg in ("Spinal_Cord_Cervical", "Spinal_Cord_Lumbar", "Cortex_Motor")}
        for g in f1_f2_genes
    }

    out = {
        "gene_symbol": "CELF5",
        "denovo_id": "DN-04",
        "gene_liability_profile": {
            "gnomad_v41_pli": gm.get("pLI"),
            "gnomad_v41_loeuf": gm.get("loeuf"),
            "ot_genetic_constraint": ot["ot_genetic_constraint"],
            "depmap_n_lines": dm["n_depmap_lines"],
            "depmap_median_chronos": dm["median_chronos"],
            "depmap_p10_chronos": dm["p10_chronos"],
            "depmap_pct_lt_minus1": dm["pct_lines_lt_minus1"],
            "ot_is_essential": dm["ot_is_essential"],
            "n_ot_safety_liabilities": ot["n_safety_liabilities"],
            "n_mouse_ko_phenotypes": ot["n_mouse_phenotypes"],
            "mouse_ko_phenotype_labels": ot["mouse_phenotype_labels"],
            "als_ot_genetic_association_score": ot["als_ot_genetic_association_score"],
            "gtex_cns_spinal_cervical_tpm": gtex.get("Brain_Spinal_cord_cervical_c-1"),
            "gtex_cns_ba9_tpm": gtex.get("Brain_Frontal_Cortex_BA9"),
            "max_cns_gtex_tissue": max_cns,
            "max_cns_gtex_tpm": cns_vals[max_cns],
            "max_non_cns_gtex_tissue": max_nc,
            "max_non_cns_gtex_tpm": non_cns[max_nc],
            "cns_enrichment_ratio_ba9_vs_max_non_cns": round(float(gtex["Brain_Frontal_Cortex_BA9"]) / max(float(non_cns[max_nc]), 0.01), 2),
            "qualitative_safety_tier": "FAVORABLE_CNS_RESTRICTED_SPLICE_RESTORATION",
        },
        "gtex_v8_median_tpm": gtex,
        "mane_isoform_and_ce_audit": gtf_info,
        "celf5_nygc_multiregion": panel_nygc["CELF5"],
        "phase3b_f1_f2_nygc_panel_summary": {
            g: {
                reg: {
                    "adj_beta_tdp_vs_ctrl": panel_nygc[g][reg]["adj_beta_tdp_vs_ctrl"],
                    "adj_p_tdp_vs_ctrl": panel_nygc[g][reg]["adj_p_tdp_vs_ctrl"],
                    "adj_p_tdp_vs_sod1fus": panel_nygc[g][reg]["adj_p_tdp_vs_sod1fus"],
                    "mn_adj_tSTMN2_beta": panel_nygc[g][reg]["within_tdp_mn_adj_log2_tSTMN2_beta"],
                    "mn_adj_tSTMN2_p": panel_nygc[g][reg]["within_tdp_mn_adj_log2_tSTMN2_p"],
                    "mn_adj_neuronal_tail_pct": panel_nygc[g][reg]["within_tdp_mn_adj_pct_more_neg_noncryptic_neuronal"],
                }
                for reg in ("Spinal_Cord_Cervical", "Spinal_Cord_Lumbar", "Cortex_Motor")
                if panel_nygc[g][reg] is not None
            }
            for g in f1_f2_genes
        },
    }
    txt = json.dumps(out, indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(txt), "Biosecurity sequence guard triggered!"
    CACHE_FP.write_text(txt, encoding="utf-8")
    print("Cached CELF5 profile ->", CACHE_FP.relative_to(ROOT).as_posix(), f"({len(txt)} bytes)")


if __name__ == "__main__":
    main()
