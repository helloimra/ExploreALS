"""RUN-P3A-001 (v2): Coordinate-only spliced + pre-mRNA + 1-nt bulge + 18-mer sub-core off-target audit across 12 GRCh38 intervals."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (SRC, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _offtarget_helpers import load_gnomad_v41_constraint_map, load_pan_cns_7lineage_expression, sanitize_for_strict_json  # noqa: E402
from carbon_als.loaders import resolve_dataset_path  # noqa: E402
from carbon_als.offtarget_scanner import (  # noqa: E402
    load_gencode_comprehensive_index,
    min_dist_to_sorted_points,
    scan_gencode_spliced_transcriptome,
)
from carbon_als.splice_design import genomic_to_premRNA  # noqa: E402

CACHE_DIR = ROOT / "work" / "phase3a_execution_safety" / "cache"
OUT_DIR = ROOT / "work" / "phase3a_execution_safety" / "outputs"
REG_DIR = ROOT / "registries"


def extract_sense_dna(staged_seq: dict, gene: str, start_1b: int, end_1b: int, strand: str) -> str:
    s_info = staged_seq["sequences"][gene]
    dna_plus = s_info.get("dna_plus_5to3")
    if not dna_plus:
        import urllib.request
        cnum = str(s_info["chromosome"]).replace("chr", "")
        url = f"https://rest.ensembl.org/sequence/region/human/{cnum}:{s_info['start_1b']}..{s_info['end_1b']}:1?content-type=application/json"
        req = urllib.request.Request(url, headers={"User-Agent": "ExploreALS/1.2"})
        with urllib.request.urlopen(req, timeout=45) as resp:  # noqa: S310
            dna_plus = json.loads(resp.read().decode("utf-8"))["seq"].upper()
            s_info["dna_plus_5to3"] = dna_plus
    prem_rna, coords = genomic_to_premRNA(dna_plus, s_info["chromosome"], s_info["start_1b"], s_info["strand"])
    pos_to_base = dict(zip(coords, prem_rna, strict=True))
    span = range(start_1b, end_1b + 1) if strand == "+" else range(end_1b, start_1b - 1, -1)
    return "".join(pos_to_base[p] for p in span).replace("U", "T")


def _map_genomic_hits_to_premRNA(hits: list[dict[str, Any]], t_gene: str, genes_by_cs: dict, ss_by_gene: dict, mode_key: str) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for h in hits:
        c, lo, hi, st = str(h["chrom"]), int(h["grch38_start"]), int(h["grch38_end"]), str(h["strand"])
        if any(gname == t_gene and not (hi < gs or lo > ge) for gs, ge, _, gname, _ in genes_by_cs.get((c, st), [])):
            continue
        for gs, ge, gid, gname, gtype in genes_by_cs.get((c, st), []):
            if gname == t_gene or hi < gs or lo > ge:
                continue
            sdist = min_dist_to_sorted_points(lo, hi, ss_by_gene.get((gid, gname), []))
            nmis = int(h.get("total_mismatches", 1))
            ndest = int(h.get("destabilizing_mismatches", 0))
            ngu = int(h.get("gu_wobble_pairs", 0))
            rk = (nmis, ndest, sdist, 0 if gtype == "protein_coding" else 1)
            cur = best.get(gname)
            if cur is None or rk < cur["_rk"]:
                best[gname] = {
                    "gene_symbol": gname, "ensembl_gene_id": gid, "biotype": gtype, "hit_coord": f"{c}:{lo}-{hi}({st})",
                    "total_mismatches": nmis, "gu_wobble_pairs": ngu, "destabilizing_mismatches": ndest,
                    "dist_to_splice_boundary_bp": sdist, "steric_active_region": (sdist <= 50),
                    "mode": h.get("bulge_type", mode_key), "_rk": rk,
                }
    for v in best.values():
        v.pop("_rk", None)
    return best


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tx_fa = resolve_dataset_path("DS_GENCODE_V46_TX", verify_hash=True)
    comp_gtf = resolve_dataset_path("DS_GENCODE_V46_COMP_GTF", verify_hash=True)
    gg_fp = CACHE_DIR / "gggenome_hg38_coords_only.json"
    gg_gz = CACHE_DIR / "gggenome_hg38_coords_only.json.gz"
    if gg_fp.is_file():
        gg_cache = json.loads(gg_fp.read_text(encoding="utf-8"))
    else:
        import gzip
        gg_cache = json.loads(gzip.decompress(gg_gz.read_bytes()).decode("utf-8"))
    staged_seq = json.loads((ROOT / "work" / "phase2" / "track1_multiplex_splice" / "outputs" / "genomics_sequences_and_gnomad.json").read_text(encoding="utf-8"))
    with (REG_DIR / "phase2_multiplex_intervals.csv").open(encoding="utf-8") as fh:
        intervals = list(csv.DictReader(fh))

    print("[1/4] Loading comprehensive GENCODE v46 GTF internal splice & CDS index...", flush=True)
    gtf_idx = load_gencode_comprehensive_index(comp_gtf)
    genes_by_cs, ss_by_gene = gtf_idx["genes_by_cs"], gtf_idx["internal_ss_by_gene"]

    queries = [{"interval_id": r["interval_id"], "gene_symbol": r["gene_symbol"], "sense_dna": extract_sense_dna(staged_seq, r["gene_symbol"], int(r["grch38_start"]), int(r["grch38_end"]), r["strand"])} for r in intervals]
    print("[2/4] Scanning GENCODE v46 spliced transcriptome (<=2mm + 1-nt bulges + 18-mer sub-cores)...", flush=True)
    sp_hits, sp_bulge, sp_sub18, n_tx_scanned = scan_gencode_spliced_transcriptome(
        tx_fa, queries, tx_mrna_map=gtf_idx["tx_mrna_map"], gene_biotype_by_id=gtf_idx["gene_biotype_by_id"], return_extended=True
    )

    prem_by_iv: dict[str, dict[str, dict[str, Any]]] = {}
    pm_bulge_by_iv: dict[str, dict[str, dict[str, Any]]] = {}
    pm_sub18_by_iv: dict[str, dict[str, dict[str, Any]]] = {}
    raw_hg38: dict[str, dict[str, Any]] = {}
    prio_genes: set[str] = set()

    for r in intervals:
        iv_id, t_gene = r["interval_id"], r["gene_symbol"]
        entry = gg_cache[iv_id]
        ug_list = entry["ungapped_hits"]
        non_self_ug = [h for h in ug_list if not any(gn == t_gene and not (int(h["grch38_end"]) < gs or int(h["grch38_start"]) > ge) for gs, ge, _, gn, _ in genes_by_cs.get((str(h["chrom"]), str(h["strand"])), []))]
        max_mm = int(entry["max_mm_queried"])
        raw_hg38[iv_id] = {
            "gggenome_max_mm_queried": max_mm, "gapped_1edit_queried": bool(entry["gapped_1edit_queried"]),
            "hg38_0mm_non_self_loci": sum(1 for h in non_self_ug if int(h["total_mismatches"]) == 0),
            "hg38_1mm_non_self_loci": sum(1 for h in non_self_ug if int(h["total_mismatches"]) == 1) if max_mm >= 1 else None,
            "hg38_2mm_non_self_loci": sum(1 for h in non_self_ug if int(h["total_mismatches"]) == 2) if max_mm >= 2 else None,
        }
        prem_by_iv[iv_id] = _map_genomic_hits_to_premRNA(ug_list, t_gene, genes_by_cs, ss_by_gene, "premRNA_ungapped")
        pm_bulge_by_iv[iv_id] = _map_genomic_hits_to_premRNA(entry["bulge_1nt_hits"], t_gene, genes_by_cs, ss_by_gene, "premRNA_bulge1nt")
        pm_sub18_by_iv[iv_id] = _map_genomic_hits_to_premRNA(entry["sub18_core_0destab_hits"], t_gene, genes_by_cs, ss_by_gene, "premRNA_sub18")
        for store in (sp_hits[iv_id], sp_bulge[iv_id], sp_sub18[iv_id], prem_by_iv[iv_id], pm_bulge_by_iv[iv_id], pm_sub18_by_iv[iv_id]):
            for rec in store.values():
                if rec["biotype"] == "protein_coding" and (rec.get("total_mismatches", 1) <= 1 or rec.get("destabilizing_mismatches", 0) == 0 or rec.get("steric_active_region", False)):
                    prio_genes.add(rec["gene_symbol"])

    print(f"[3/4] Evaluating 7 human CNS lineages across {len(prio_genes)} genes + gnomAD v4.1...", flush=True)
    cns_expr, zh_map = load_pan_cns_7lineage_expression(sorted(prio_genes))
    constraint_map = load_gnomad_v41_constraint_map(resolve_dataset_path("DS_GNOMAD_V41_CONSTRAINT", verify_hash=True))

    csv_rows: list[dict[str, Any]] = []
    detail_by_iv: dict[str, Any] = {}
    for r in intervals:
        iv_id = r["interval_id"]
        sp, pm = sp_hits[iv_id], prem_by_iv[iv_id]
        sp_pc = [x for x in sp.values() if x["biotype"] == "protein_coding"]
        sp_0 = [x for x in sp.values() if x["total_mismatches"] == 0]
        sp_1 = [x for x in sp.values() if x["total_mismatches"] == 1]
        sp_2_pc = [x for x in sp_pc if x["total_mismatches"] == 2]
        sp_wobble0_pc = [x for x in sp_pc if x["gu_wobble_pairs"] > 0 and x["destabilizing_mismatches"] == 0]
        pm_0 = [x for x in pm.values() if x["total_mismatches"] == 0]
        pm_1_any = [x for x in pm.values() if x["total_mismatches"] == 1]
        pm_1_prox = [x for x in pm_1_any if x["dist_to_splice_boundary_bp"] <= 50]
        pm_wob0_prox_pc = [x for x in pm.values() if x["biotype"] == "protein_coding" and x["gu_wobble_pairs"] > 0 and x["destabilizing_mismatches"] == 0 and x["dist_to_splice_boundary_bp"] <= 50]
        pm_2_prox_pc = [x for x in pm.values() if x["total_mismatches"] == 2 and x["dist_to_splice_boundary_bp"] <= 25 and x["biotype"] == "protein_coding"]
        bulge_steric_pc = {g: rec for g, rec in {**{k: v for k, v in pm_bulge_by_iv[iv_id].items() if v["biotype"] == "protein_coding" and v["steric_active_region"]}, **{k: v for k, v in sp_bulge[iv_id].items() if v["biotype"] == "protein_coding" and v["steric_active_region"]}}.items()}
        sub18_steric_pc = {g: rec for g, rec in {**{k: v for k, v in pm_sub18_by_iv[iv_id].items() if v["biotype"] == "protein_coding" and v["steric_active_region"]}, **{k: v for k, v in sp_sub18[iv_id].items() if v["biotype"] == "protein_coding" and v["steric_active_region"]}}.items()}

        cand_pool: dict[str, tuple[tuple[int, int, int, int], str, dict[str, Any]]] = {}
        for layer, items in (("spliced", sp_0 + sp_1 + sp_wobble0_pc), ("premRNA", pm_0 + pm_1_any + pm_wob0_prox_pc + pm_2_prox_pc), ("bulge_1nt", list(bulge_steric_pc.values())), ("sub18_core", list(sub18_steric_pc.values()))):
            for x in items:
                d_val = int(x.get("dist_to_eej_nt", x.get("dist_to_splice_boundary_bp", 0)))
                act = bool(x.get("steric_active_region", d_val <= 50))
                rk = (0 if act else 1, int(x.get("total_mismatches", 1)), int(x.get("destabilizing_mismatches", 0)), d_val)
                cur = cand_pool.get(x["gene_symbol"])
                if cur is None or rk < cur[0]:
                    cand_pool[x["gene_symbol"]] = (rk, layer, x)

        flagged_active: list[tuple[int, int, str, str]] = []
        inert_notes: list[str] = []
        notable_hits: list[dict[str, Any]] = []
        for gsym, (_, layer, rec) in sorted(cand_pool.items()):
            est = cns_expr.get(gsym, {})
            max_expr = float(est.get("max_cns_ctrl_log2cpm", 0.0) or 0.0)
            cst = constraint_map.get(gsym, {})
            pli, loeuf = cst.get("pLI"), cst.get("loeuf")
            is_constr = (pli is not None and pli >= 0.9) or (loeuf is not None and loeuf <= 0.35)
            d_val = int(rec.get("dist_to_eej_nt", rec.get("dist_to_splice_boundary_bp", 0)))
            act = bool(rec.get("steric_active_region", d_val <= 50))
            nmis = int(rec.get("total_mismatches", 1))
            ndest = int(rec.get("destabilizing_mismatches", 0))
            if rec["biotype"] == "protein_coding" and max_expr >= 1.0 and is_constr and (nmis <= 1 or ndest == 0 or layer in ("bulge_1nt", "sub18_core")):
                tag = f"{gsym}({layer}:{nmis}mm,d={d_val}nt,LOEUF={loeuf},pLI={pli},{est.get('max_cns_lineage')})"
                if act:
                    flagged_active.append((nmis, d_val, gsym, tag))
                elif layer == "spliced" and nmis <= 1:
                    inert_notes.append(f"{gsym}(1mm_inert_{rec.get('tx_region')},dEEJ={d_val}nt,LOEUF={loeuf})")
            elif layer in ("bulge_1nt", "sub18_core") and act:
                inert_notes.append(f"{gsym}({layer}_nonconstr,d={d_val}bp,LOEUF={loeuf})")
            notable_hits.append({**rec, "layer": layer, **est, "gnomad_pLI": pli, "gnomad_loeuf": loeuf, **zh_map.get(gsym, {})})

        flagged_sorted = [t[3] for t in sorted(flagged_active)]
        deep_pm0 = [f"{x['gene_symbol']}(0mm_deep_intron,dSS={x['dist_to_splice_boundary_bp']}bp)" for x in sorted(pm_0, key=lambda z: z["dist_to_splice_boundary_bp"]) if x["dist_to_splice_boundary_bp"] > 50]
        if sp_0 or [x for x in pm_0 if x["dist_to_splice_boundary_bp"] <= 50] or len(pm_0) >= 5:
            status = "FAIL_EXACT_0MM_OFFTARGET"
        elif flagged_sorted:
            status = "WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL"
        elif sp_1 or pm_1_prox or sp_wobble0_pc or pm_wob0_prox_pc or pm_2_prox_pc or bulge_steric_pc or sub18_steric_pc or pm_0:
            status = "CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED"
        else:
            status = "PASS_CLEAN_GE2MM"

        max_mm_q = int(raw_hg38[iv_id]["gggenome_max_mm_queried"])
        pm2_cell: int | str = len(pm_2_prox_pc) if max_mm_q >= 2 else "NA"
        aux_notes = deep_pm0 + inert_notes
        flag_cell = (";".join(flagged_sorted[:5]) + (f";...(+{len(flagged_sorted)-5}_more_in_JSON)" if len(flagged_sorted) > 5 else "")) if flagged_sorted else (";".join(aux_notes[:3]) if aux_notes and status == "CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED" else "NONE")
        csv_rows.append({
            "candidate_id": r["candidate_id"], "gene_symbol": r["gene_symbol"], "rank_within_gene": r["rank_within_gene"], "interval_id": iv_id,
            "length_bp": r["length_bp"], "tm_phys_pops_c": r["tm_phys_pops_c"], "gggenome_max_mm_queried": max_mm_q,
            "spliced_0mm_genes": len(sp_0), "spliced_1mm_genes": len(sp_1), "spliced_2mm_pc_genes": len(sp_2_pc), "spliced_wobble_only_pc_genes": len(sp_wobble0_pc),
            "premRNA_0mm_sense_genes": len(pm_0), "premRNA_1mm_sense_genes": len(pm_1_any), "premRNA_1mm_splice50bp_genes": len(pm_1_prox),
            "premRNA_wobble_only_splice50bp_pc_genes": len(pm_wob0_prox_pc), "premRNA_2mm_splice25bp_pc_genes": pm2_cell,
            "bulge_1nt_steric_pc_genes": len(bulge_steric_pc), "sub18_core_steric_pc_genes": len(sub18_steric_pc),
            "flagged_constrained_neuronal_hits": flag_cell, "offtarget_safety_status": status, "analysis_run_id": "RUN-P3A-001",
        })
        detail_by_iv[iv_id] = {**csv_rows[-1], "flagged_constrained_cns_count": len(flagged_sorted), "flagged_constrained_cns_all": flagged_sorted, "inert_non_eej_notes": inert_notes, **raw_hg38[iv_id], "notable_offtarget_genes": notable_hits}

    with (REG_DIR / "phase3_sso_offtarget_audit.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)
    payload = sanitize_for_strict_json({"analysis_run_id": "RUN-P3A-001", "evidence_basis": "MEASURED_REFERENCE_GENOME_AND_7LINEAGE_HUMAN_CNS_SNRNA", "n_transcripts_scanned": n_tx_scanned, "intervals": detail_by_iv})
    (OUT_DIR / "run_p3a_001_sso_offtarget_audit.json").write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    for row in csv_rows:
        print(f"{row['gene_symbol']} #{row['rank_within_gene']} {row['interval_id']}: {row['offtarget_safety_status']} | sp0={row['spliced_0mm_genes']} sp1={row['spliced_1mm_genes']} wob0={row['spliced_wobble_only_pc_genes']} pm1_ss={row['premRNA_1mm_splice50bp_genes']} pm_wob={row['premRNA_wobble_only_splice50bp_pc_genes']} bulge={row['bulge_1nt_steric_pc_genes']} sub18={row['sub18_core_steric_pc_genes']} | flags={row['flagged_constrained_neuronal_hits']}")


if __name__ == "__main__":
    main()
