"""RUN-P3B-002: Coordinate-only GRCh38 steric-SSO & 3'Ext gapmer design + AlphaGenome AVI + Phase 3A v2 off-target audit."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
P3A_SCRIPTS = ROOT / "work" / "phase3a_execution_safety" / "scripts"
for p in (SRC, SCRIPT_DIR, P3A_SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _denovo_sso_helpers import (  # noqa: E402
    DENOVO_CIS_SPECS,
    audit_atg4b_ce_ptc_in_ram,
    build_alphagenome_locus_url,
    fetch_avi_positions_only,
    fetch_ensembl_dna_transient,
    fetch_gnomad_banned_positions,
    map_hits_to_premRNA,
    query_gggenome_v2_coords_only,
)
from _offtarget_helpers import load_gnomad_v41_constraint_map, load_pan_cns_7lineage_expression, sanitize_for_strict_json  # noqa: E402
from carbon_als.loaders import resolve_dataset_path  # noqa: E402
from carbon_als.offtarget_scanner import load_gencode_comprehensive_index, scan_gencode_spliced_transcriptome  # noqa: E402
from carbon_als.splice_design import genomic_to_premRNA, score_target_intervals  # noqa: E402

CACHE_DIR = ROOT / "work" / "phase3b_denovo_discovery" / "cache"
OUT_FP = ROOT / "work" / "phase3b_denovo_discovery" / "outputs" / "run_p3b_002_denovo_sso_offtarget.json"
CSV_FP = ROOT / "registries" / "phase3b_denovo_sso_intervals.csv"
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)


def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FP.parent.mkdir(parents=True, exist_ok=True)
    gnomad_fp, gg_fp, avi_fp = CACHE_DIR / "gnomad_banned_positions_only.json", CACHE_DIR / "gggenome_denovo_coords_only.json", CACHE_DIR / "alphagenome_avi_positions_only.json"
    gg_gz = CACHE_DIR / "gggenome_denovo_coords_only.json.gz"
    gnomad_cache = json.loads(gnomad_fp.read_text(encoding="utf-8")) if gnomad_fp.is_file() else {}
    if gg_fp.is_file():
        gg_cache = json.loads(gg_fp.read_text(encoding="utf-8"))
    elif gg_gz.is_file():
        import gzip
        gg_cache = json.loads(gzip.decompress(gg_gz.read_bytes()).decode("utf-8"))
    else:
        gg_cache = {}
    avi_cache = json.loads(avi_fp.read_text(encoding="utf-8")) if avi_fp.is_file() else {}

    atg4b_ptc = audit_atg4b_ce_ptc_in_ram()
    selected_ivs, transient_queries, rank_counter = [], [], {}
    for dn_id, gene, cnum, w_s, w_e, strand, fbounds, smode, mech, n_picks, atlas_b in DENOVO_CIS_SPECS:
        chrom = f"chr{cnum}"
        dna_plus = fetch_ensembl_dna_transient(cnum, w_s, w_e)
        banned_1b, _ = fetch_gnomad_banned_positions(cnum, w_s, w_e, gnomad_cache)
        avi_by_pos = fetch_avi_positions_only(cnum, w_s, w_e, avi_cache)
        prem_rna, coords = genomic_to_premRNA(dna_plus, chrom, w_s, strand)
        pos_to_base = dict(zip(coords, prem_rna, strict=True))
        del dna_plus
        ranked = score_target_intervals(chrom, prem_rna, coords, strand, lengths=(18, 20), avi_by_pos=avi_by_pos, banned_positions_1b=banned_1b, mode=smode, feature_bounds_1b=fbounds)
        assert len(ranked) >= n_picks, f"Fewer than {n_picks} intervals scored for {gene} ({mech})"
        picks = [ranked[0]]
        if n_picks == 2:
            for cand in ranked[1:]:
                if abs(int(cand["grch38_start"]) - int(picks[0]["grch38_start"])) >= 5:
                    picks.append(cand)
                    break
            if len(picks) < 2:
                picks.append(ranked[1])
        for iv in picks:
            rank_counter[dn_id] = rank_counter.get(dn_id, 0) + 1
            lo, hi = int(iv["grch38_start"]), int(iv["grch38_end"])
            sense_dna = "".join(pos_to_base[p] for p in (range(lo, hi + 1) if strand == "+" else range(hi, lo - 1, -1))).replace("U", "T")
            query_gggenome_v2_coords_only(iv["interval_id"], sense_dna, gg_cache)
            selected_ivs.append({**iv, "denovo_id": dn_id, "gene_symbol": gene, "rank_within_gene": rank_counter[dn_id], "score_mode": smode, "cis_mechanism_class": mech, "alphagenome_atlas_url": build_alphagenome_locus_url(chrom, min(atlas_b[0], lo), max(atlas_b[1], hi))})
            transient_queries.append({"interval_id": iv["interval_id"], "gene_symbol": gene, "sense_dna": sense_dna})
        del prem_rna, pos_to_base

    for fp, obj in ((gnomad_fp, gnomad_cache), (gg_fp, gg_cache), (avi_fp, avi_cache)):
        txt = json.dumps(obj, indent=2, allow_nan=False)
        assert not SEQ_GUARD_RE.search(txt), f"Biosecurity check failed on {fp.name}"
        fp.write_text(txt, encoding="utf-8")

    tx_fa = resolve_dataset_path("DS_GENCODE_V46_TX", verify_hash=True)
    gtf_idx = load_gencode_comprehensive_index(resolve_dataset_path("DS_GENCODE_V46_COMP_GTF", verify_hash=True))
    sp_hits, sp_bulge, sp_sub18, n_tx = scan_gencode_spliced_transcriptome(tx_fa, transient_queries, tx_mrna_map=gtf_idx["tx_mrna_map"], gene_biotype_by_id=gtf_idx["gene_biotype_by_id"], return_extended=True)
    transient_queries.clear()

    pm_ug, pm_bg, pm_s18, prio_genes = {}, {}, {}, set()
    for r in selected_ivs:
        iv_id, tg, is_gap = r["interval_id"], r["gene_symbol"], (r["score_mode"] == "GAPMER_RNASE_H")
        ent = gg_cache[iv_id]
        pm_ug[iv_id] = map_hits_to_premRNA(ent["ungapped_hits"], tg, gtf_idx["genes_by_cs"], gtf_idx["internal_ss_by_gene"], "premRNA_ungapped")
        pm_bg[iv_id] = map_hits_to_premRNA(ent["bulge_1nt_hits"], tg, gtf_idx["genes_by_cs"], gtf_idx["internal_ss_by_gene"], "premRNA_bulge1nt")
        pm_s18[iv_id] = map_hits_to_premRNA(ent["sub18_core_0destab_hits"], tg, gtf_idx["genes_by_cs"], gtf_idx["internal_ss_by_gene"], "premRNA_sub18")
        for st_map in (sp_hits[iv_id], sp_bulge[iv_id], sp_sub18[iv_id], pm_ug[iv_id], pm_bg[iv_id], pm_s18[iv_id]):
            for rec in st_map.values():
                if rec["biotype"] == "protein_coding" and (is_gap or rec.get("total_mismatches", 1) <= 1 or rec.get("destabilizing_mismatches", 0) == 0 or rec.get("steric_active_region", False)):
                    prio_genes.add(rec["gene_symbol"])

    cns_expr, _ = load_pan_cns_7lineage_expression(sorted(prio_genes))
    c_map = load_gnomad_v41_constraint_map(resolve_dataset_path("DS_GNOMAD_V41_CONSTRAINT", verify_hash=True))

    csv_rows: list[dict[str, Any]] = []
    for r in selected_ivs:
        iv_id, is_gap = r["interval_id"], (r["score_mode"] == "GAPMER_RNASE_H")
        sp, pm = sp_hits[iv_id], pm_ug[iv_id]
        sp_pc = [x for x in sp.values() if x["biotype"] == "protein_coding"]
        sp_0, sp_1, sp_2_pc = [x for x in sp.values() if x["total_mismatches"] == 0], [x for x in sp.values() if x["total_mismatches"] == 1], [x for x in sp_pc if x["total_mismatches"] == 2]
        sp_wob0 = [x for x in sp_pc if x["gu_wobble_pairs"] > 0 and x["destabilizing_mismatches"] == 0]
        pm_0, pm_1 = [x for x in pm.values() if x["total_mismatches"] == 0], [x for x in pm.values() if x["total_mismatches"] == 1]
        pm_1_ss = [x for x in pm_1 if x["dist_to_splice_boundary_bp"] <= 50]
        pm_wob0_all = [x for x in pm.values() if x["biotype"] == "protein_coding" and x["gu_wobble_pairs"] > 0 and x["destabilizing_mismatches"] == 0]
        pm_wob0 = [x for x in pm_wob0_all if x["dist_to_splice_boundary_bp"] <= 50]
        pm_2_ss = [x for x in pm.values() if x["total_mismatches"] == 2 and x["dist_to_splice_boundary_bp"] <= 25 and x["biotype"] == "protein_coding"]
        bg_pc = {k: v for k, v in {**pm_bg[iv_id], **sp_bulge[iv_id]}.items() if v["biotype"] == "protein_coding" and (is_gap or v["steric_active_region"])}
        s18_pc = {k: v for k, v in {**pm_s18[iv_id], **sp_sub18[iv_id]}.items() if v["biotype"] == "protein_coding" and (is_gap or v["steric_active_region"])}

        flagged: list[str] = []
        pm_eval = (pm_0 + pm_1 + pm_wob0_all) if is_gap else (pm_0 + pm_1 + pm_wob0 + pm_2_ss)
        for layer, items in (("spliced", sp_0 + sp_1 + sp_wob0), ("premRNA", pm_eval), ("bulge_1nt", list(bg_pc.values())), ("sub18_core", list(s18_pc.values()))):
            for x in items:
                gsym = x["gene_symbol"]
                d_v = int(x.get("dist_to_eej_nt", x.get("dist_to_splice_boundary_bp", 0)))
                act = True if is_gap else bool(x.get("steric_active_region", d_v <= 50))
                est, cst = cns_expr.get(gsym, {}), c_map.get(gsym, {})
                pli, loeuf = cst.get("pLI"), cst.get("loeuf")
                is_c = (pli is not None and pli >= 0.9) or (loeuf is not None and loeuf <= 0.35)
                if act and x["biotype"] == "protein_coding" and float(est.get("max_cns_ctrl_log2cpm", 0.0) or 0.0) >= 1.0 and is_c and (int(x.get("total_mismatches", 1)) <= 1 or int(x.get("destabilizing_mismatches", 0)) == 0 or layer in ("bulge_1nt", "sub18_core")):
                    pli_s, loe_s = (f"{pli:.2f}" if pli is not None else "none"), (f"{loeuf:.3f}" if loeuf is not None else "none")
                    flagged.append(f"{gsym}({layer}:{x.get('total_mismatches',1)}mm,d={d_v}nt,pLI={pli_s},LOEUF={loe_s})")
        flagged = sorted(set(flagged))
        if sp_0 or (is_gap and pm_0) or [x for x in pm_0 if x["dist_to_splice_boundary_bp"] <= 50] or len(pm_0) >= 5:
            status = "FAIL_EXACT_0MM_OFFTARGET"
        elif flagged:
            status = "WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL"
        elif sp_1 or pm_1_ss or sp_wob0 or pm_wob0 or pm_2_ss or bg_pc or s18_pc or pm_0 or (is_gap and (pm_1 or pm_wob0_all)):
            status = "CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED"
        else:
            status = "PASS_CLEAN_GE2MM"
        csv_rows.append({
            "denovo_id": r["denovo_id"], "gene_symbol": r["gene_symbol"], "rank_within_gene": r["rank_within_gene"],
            "interval_id": iv_id, "chrom": r["chrom"], "grch38_start": r["grch38_start"], "grch38_end": r["grch38_end"],
            "strand": r["strand"], "length_bp": r["length_bp"], "cis_mechanism_class": r["cis_mechanism_class"],
            "gc_pct": r["gc_pct"], "tm_phys_pops_c": r["tm_phys_pops_c"], "dg37_kcal": r["dg37_kcal"],
            "cpg_dinucs": r["cpg_dinucs"], "max_self_stem_bp": r["max_self_stem_bp"], "ese_motifs": r["ese_motifs"],
            "mean_avi_phred": r["mean_avi_phred"], "max_avi_phred": r["max_avi_phred"],
            "boundary_dist_bp": r["boundary_dist_bp"], "composite_score": r["composite_score"],
            "gggenome_max_mm_queried": gg_cache[iv_id]["max_mm_queried"],
            "spliced_0mm_genes": len(sp_0), "spliced_1mm_genes": len(sp_1), "spliced_2mm_pc_genes": len(sp_2_pc),
            "spliced_wobble_only_pc_genes": len(sp_wob0), "premRNA_0mm_sense_genes": len(pm_0), "premRNA_1mm_sense_genes": len(pm_1),
            "premRNA_1mm_splice50bp_genes": len(pm_1_ss), "premRNA_wobble_only_splice50bp_pc_genes": len(pm_wob0),
            "premRNA_2mm_splice25bp_pc_genes": len(pm_2_ss), "bulge_1nt_steric_pc_genes": len(bg_pc), "sub18_core_steric_pc_genes": len(s18_pc),
            "flagged_constrained_neuronal_hits": ";".join(flagged[:6]) if flagged else "NONE",
            "offtarget_safety_status": status, "alphagenome_atlas_url": r["alphagenome_atlas_url"], "analysis_run_id": "RUN-P3B-002",
        })

    safety_ord = {"PASS_CLEAN_GE2MM": 0, "CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED": 1, "WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL": 2, "FAIL_EXACT_0MM_OFFTARGET": 3}
    dn_ord = {r["denovo_id"]: idx for idx, r in enumerate(csv_rows)}
    csv_rows.sort(key=lambda x: (dn_ord[x["denovo_id"]], safety_ord[x["offtarget_safety_status"]], -float(x["composite_score"])))
    seen_dn: dict[str, int] = {}
    for row in csv_rows:
        seen_dn[row["denovo_id"]] = seen_dn.get(row["denovo_id"], 0) + 1
        row["rank_within_gene"] = seen_dn[row["denovo_id"]]

    with CSV_FP.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)
    out_txt = json.dumps(sanitize_for_strict_json({"analysis_run_id": "RUN-P3B-002", "n_transcripts_scanned": n_tx, "atg4b_ce_reading_frame_audit": atg4b_ptc, "intervals": csv_rows}), indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(out_txt) and not SEQ_GUARD_RE.search(CSV_FP.read_text(encoding="utf-8")), "Biosecurity sequence leak!"
    OUT_FP.write_text(out_txt, encoding="utf-8")
    for row in csv_rows:
        print(f"{row['denovo_id']} {row['gene_symbol']} #{row['rank_within_gene']} {row['interval_id']}: {row['offtarget_safety_status']} | avi={row['max_avi_phred']} | sp0={row['spliced_0mm_genes']} sp1={row['spliced_1mm_genes']} pm0={row['premRNA_0mm_sense_genes']} pm1={row['premRNA_1mm_sense_genes']} bg={row['bulge_1nt_steric_pc_genes']} | flags={row['flagged_constrained_neuronal_hits']}")


if __name__ == "__main__":
    main()
