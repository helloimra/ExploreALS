"""Head-to-head coordinate-only Torres 2024 ASO 3J benchmark (ATG4B) + CELF5 AF-Q8N6W0/PDB 3NMR RRM2 truncation, Frechet-Hoeffding phasing, & 18-nt EJC audit."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any
import urllib.request

import numpy as np

from _denovo_sso_helpers import (
    fetch_avi_positions_only,
    fetch_ensembl_dna_transient,
    fetch_gnomad_banned_positions,
    map_hits_to_premRNA,
    query_gggenome_v2_coords_only,
)
from _offtarget_helpers import load_pan_cns_7lineage_expression
from carbon_als.loaders import download_https_structure, load_brown2022_splicing, resolve_dataset_path
from carbon_als.mmcif_parser import ca_rmsd_kabsch, load_mmcif_structure
from carbon_als.offtarget_scanner import load_gencode_comprehensive_index, scan_gencode_spliced_transcriptome
from carbon_als.splice_design import _revcomp_dna, duplex_tm_moe_physiological

ROOT = Path(__file__).resolve().parents[3]
PDB_DIR = ROOT / "data" / "pharmacology_structures" / "phase3b_pdb"
SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)


def _sha256(fp: Path) -> str:
    h = hashlib.sha256()
    with fp.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stage_celf5_3nmr_and_afdb_structures() -> tuple[Path, Path]:
    PDB_DIR.mkdir(parents=True, exist_ok=True)
    specs = [
        ("DS_PDB_3NMR", "https://files.rcsb.org/download/3NMR.cif", "pdb_00003nmr.cif",
         "RCSB_PDB:3NMR;PMID:20947024;DOI:10.1016/j.str.2010.06.018", "CC0 1.0 Public Domain", "DN-04",
         "Teplova et al. 2010 crystal structure of human CELF1 (CUGBP1) tandem RRM1-RRM2 domains bound to UGUU RNA"),
        ("DS_AF_Q8N6W0", "https://alphafold.ebi.ac.uk/files/AF-Q8N6W0-F1-model_v6.cif", "AF-Q8N6W0-F1-model_v6.cif",
         "AlphaFold_DB:AF-Q8N6W0-F1;UniProt:Q8N6W0", "CC BY 4.0", "DN-04",
         "AlphaFold DB v6 full-length 3D structure prediction for human CELF5 (UniProt Q8N6W0, 485 aa)"),
    ]
    manifest_fp = ROOT / "registries" / "datasets_manifest.csv"
    with manifest_fp.open(encoding="utf-8", newline="") as fh:
        mr = csv.DictReader(fh)
        m_fields, m_rows = list(mr.fieldnames or []), list(mr)
    add_by_id: dict[str, dict[str, str]] = {}
    for ds_id, url, fn, acc, lic, cand, desc in specs:
        dest = PDB_DIR / fn
        if not dest.is_file():
            download_https_structure(url, dest)
        row = {"dataset_id": ds_id, "domain": "pharmacology_structures", "local_relpath": dest.relative_to(ROOT).as_posix(),
               "upstream_explore_relpath": "NONE_PHASE3B_PRIMARY", "accession_or_doi": acc, "license_or_access": lic,
               "size_bytes": str(dest.stat().st_size), "sha256": _sha256(dest), "relevant_candidates": cand, "description": desc}
        if "redistribution_tier" in m_fields:
            row["redistribution_tier"] = "TIER_A_OPEN_REDISTRIBUTABLE"
            row["canonical_fetch_url_or_instructions"] = url
        add_by_id[ds_id] = row
    existing = {r["dataset_id"] for r in m_rows}
    out_rows = [{**r, **add_by_id[r["dataset_id"]]} if r["dataset_id"] in add_by_id else r for r in m_rows]
    out_rows.extend(v for k, v in add_by_id.items() if k not in existing)
    with manifest_fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=m_fields)
        w.writeheader()
        w.writerows(out_rows)
    return PDB_DIR / "pdb_00003nmr.cif", PDB_DIR / "AF-Q8N6W0-F1-model_v6.cif"


def benchmark_atg4b_torres_3j_vs_carbon_intervals(cache_dir: Path, gnomad_map: dict[str, dict[str, float | None]]) -> dict[str, Any]:
    w_lo, w_hi = 241668968, 241669000
    dna_win = fetch_ensembl_dna_transient("2", w_lo, w_hi)
    gnomad_c = json.loads((cache_dir / "gnomad_banned_positions_only.json").read_text(encoding="utf-8"))
    gg_c = json.loads((cache_dir / "gggenome_denovo_coords_only.json").read_text(encoding="utf-8"))
    avi_c = json.loads((cache_dir / "alphagenome_avi_positions_only.json").read_text(encoding="utf-8"))
    banned_1b, _ = fetch_gnomad_banned_positions("2", 241668870, 241669005, gnomad_c)
    avi_pos = fetch_avi_positions_only("2", 241668870, 241669005, avi_c)

    specs = [
        ("Torres2024_ASO_3J_16bp_6LNA_benchmark", 241668980, 241668995, "Unconjugated_6LNA_PS_mixmer_16nt"),
        ("Carbon_ATG4B_Rank1_18bp_2MOE_donor", 241668981, 241668998, "Intrathecal_uniform_2MOE_18nt"),
        ("Carbon_ATG4B_Rank2_18bp_2MOE_exonic_lead", 241668970, 241668987, "Intrathecal_uniform_2MOE_18nt"),
    ]
    queries, meta = [], {}
    for label, lo, hi, chem in specs:
        iv_id = f"chr2:{lo}-{hi}(+)"
        s_dna = dna_win[lo - w_lo : hi - w_lo + 1]
        t_rna = s_dna.replace("T", "U")
        comp = _revcomp_dna(s_dna)
        tm_moe = duplex_tm_moe_physiological(t_rna)
        tm_lna_est = round(tm_moe + 6 * 3.0, 2) if "6LNA" in chem else None
        query_gggenome_v2_coords_only(iv_id, s_dna, gg_c)
        queries.append({"interval_id": iv_id, "gene_symbol": "ATG4B", "sense_dna": s_dna})
        meta[iv_id] = {
            "label": label, "interval_id": iv_id, "length_bp": hi - lo + 1, "reference_chemistry": chem,
            "gc_pct": round(100.0 * (comp.count("G") + comp.count("C")) / len(comp), 1),
            "cpg_dinucs": comp.count("CG"), "tdp43_ug_dinucs_in_target_rna": t_rna.count("UG"),
            "tm_phys_2moe_c": tm_moe, "tm_heuristic_6lna_mixmer_c": tm_lna_est,
            "est_1mm_duplex_tm_2moe_c": round(tm_moe - 6.0, 2),
            "est_1mm_duplex_tm_6lna_heuristic_c": round(tm_lna_est - 6.0, 2) if tm_lna_est else None,
            "lna_count_and_tm_note": "Torres et al. 2024 PMC11416411 Table 3 specifies 6 LNA positions (1,4,7,10,13,16) across 15 PS linkages (unconjugated); +3.0 C/LNA is an unmeasured additive heuristic." if tm_lna_est else "Uniform 2'-O-MOE model prior.",
            "gnomad_af_ge_0p001_overlap": any(p in banned_1b for p in range(lo, hi + 1)),
            "max_avi_phred": round(max((avi_pos.get(p, 0.0) for p in range(lo, hi + 1)), default=0.0), 2),
        }
    del dna_win
    gg_txt = json.dumps(gg_c, indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(gg_txt), "Biosecurity check failed on gggenome cache"
    (cache_dir / "gggenome_denovo_coords_only.json").write_text(gg_txt, encoding="utf-8")

    tx_fa = resolve_dataset_path("DS_GENCODE_V46_TX", verify_hash=True)
    gtf_idx = load_gencode_comprehensive_index(resolve_dataset_path("DS_GENCODE_V46_COMP_GTF", verify_hash=True))
    sp_hits, sp_bulge, _, _ = scan_gencode_spliced_transcriptome(tx_fa, queries, tx_mrna_map=gtf_idx["tx_mrna_map"], gene_biotype_by_id=gtf_idx["gene_biotype_by_id"], return_extended=True)
    queries.clear()

    pm_ug, pm_bg, cand_genes = {}, {}, set()
    for iv_id in meta:
        pm_ug[iv_id] = map_hits_to_premRNA(gg_c[iv_id]["ungapped_hits"], "ATG4B", gtf_idx["genes_by_cs"], gtf_idx["internal_ss_by_gene"], "premRNA_ungapped")
        pm_bg[iv_id] = map_hits_to_premRNA(gg_c[iv_id]["bulge_1nt_hits"], "ATG4B", gtf_idx["genes_by_cs"], gtf_idx["internal_ss_by_gene"], "premRNA_bulge1nt")
        for m in (sp_hits[iv_id], sp_bulge[iv_id], pm_ug[iv_id], pm_bg[iv_id]):
            for r in m.values():
                if r["biotype"] == "protein_coding" and (r.get("total_mismatches", 1) <= 1 or r.get("steric_active_region", False)):
                    cand_genes.add(r["gene_symbol"])
    cns_expr, _ = load_pan_cns_7lineage_expression(sorted(cand_genes))
    rows = []
    for iv_id, m in meta.items():
        sp, pm = sp_hits[iv_id], pm_ug[iv_id]
        sp0 = [x["gene_symbol"] for x in sp.values() if x["total_mismatches"] == 0]
        sp1 = [x["gene_symbol"] for x in sp.values() if x["total_mismatches"] == 1]
        pm0_ss = [x["gene_symbol"] for x in pm.values() if x["total_mismatches"] == 0 and x["dist_to_splice_boundary_bp"] <= 50]
        pm1_ss = [x["gene_symbol"] for x in pm.values() if x["total_mismatches"] == 1 and x["dist_to_splice_boundary_bp"] <= 50]
        bg_act = [k for k, v in {**pm_bg[iv_id], **sp_bulge[iv_id]}.items() if v["biotype"] == "protein_coding" and v["steric_active_region"]]
        flags = []
        for gsym in sorted(set(sp0 + sp1 + pm0_ss + pm1_ss + bg_act)):
            cst = gnomad_map.get(gsym, {})
            pli, loe = cst.get("pLI"), cst.get("loeuf")
            if float((cns_expr.get(gsym) or {}).get("max_cns_ctrl_log2cpm", 0.0) or 0.0) >= 1.0 and ((pli is not None and pli >= 0.9) or (loe is not None and loe <= 0.35)):
                flags.append(f"{gsym}(pLI={pli},LOEUF={loe})")
        rows.append({**m, "spliced_0mm_genes": len(sp0), "spliced_1mm_genes": len(sp1), "spliced_1mm_symbols": sorted(sp1)[:8],
                     "premRNA_0mm_splice50bp_genes": len(pm0_ss), "premRNA_1mm_splice50bp_genes": len(pm1_ss), "premRNA_1mm_splice50bp_symbols": sorted(pm1_ss)[:8],
                     "bulge_1nt_steric_pc_genes": len(bg_act), "constrained_cns_offtarget_flags": flags})
    return {
        "head_to_head_intervals": rows,
        "torres2024_pip8b2_kim1_nephrotoxicity_note": "Torres et al. 2024 (PMID:39305312, PMC11416411) evaluated two distinct constructs: (1) unconjugated 16-nt 6-LNA/15-PS mixmer ASO 3J (Table 3, chr2:241668980-241668995(+)), transfected at 5-100 nM with Lipofectamine RNAiMAX in TARDBP-KD HeLa cells (Fig. 6c), and (2) systemic IV 25-nt peptide-conjugated PMO Pip8b2-ATG4B targeting the TDP-43 binding site (10 mg/kg, Fig. 6a,b), which caused transient Day-2 mouse urinary KIM-1 elevation resolving by Day 7. Sequence off-target counts (10/18/5 vs #2 0/0/0) quantify transcriptome sequence hits rather than measured in vivo toxicity; naked intrathecal 2'-O-MOE CSF dosing avoids cationic CPP renal exposure.",
    }
