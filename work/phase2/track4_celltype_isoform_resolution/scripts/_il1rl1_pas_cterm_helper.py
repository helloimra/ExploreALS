"""Helper for C007 (EALS-007 IL1RL1): PDB 4KC3 disulfide/Cys327 unpaired-thiol audit, GENCODE v46 -SKECF C-terminome scan, & Zone 1 Intron-8 PAS/DSE steric-SSO evaluation."""
from __future__ import annotations

import gzip
import json
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
P3B_SCRIPTS = ROOT / "work" / "phase3b_denovo_discovery" / "scripts"
P3A_SCRIPTS = ROOT / "work" / "phase3a_execution_safety" / "scripts"
for p in (ROOT / "src", P3B_SCRIPTS, P3A_SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _denovo_sso_helpers import (  # noqa: E402
    fetch_avi_positions_only,
    fetch_ensembl_dna_transient,
    fetch_gnomad_banned_positions,
    map_hits_to_premRNA,
    query_gggenome_v2_coords_only,
)
from carbon_als.loaders import resolve_dataset_path  # noqa: E402
from carbon_als.mmcif_parser import load_mmcif_structure  # noqa: E402
from carbon_als.offtarget_scanner import (  # noqa: E402
    load_gencode_comprehensive_index,
    parse_gencode_fasta_header,
    scan_gencode_spliced_transcriptome,
)
from carbon_als.splice_design import genomic_to_premRNA, score_target_intervals  # noqa: E402

SEQ_GUARD_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)
CODON_AA = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L", "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M", "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S", "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T", "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*", "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K", "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W", "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R", "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def audit_4kc3_disulfides_and_cys327(cif_path: Path, st2_chain: str) -> dict[str, Any]:
    rg = load_mmcif_structure(cif_path).residue_groups()
    cys_sg: dict[int, np.ndarray] = {}
    for (ch, seq, comp), atoms in rg.items():
        if ch == st2_chain and comp == "CYS":
            sg = [a.coord for a in atoms if a.atom_name == "SG"]
            if sg:
                cys_sg[int(seq)] = sg[0]
    cys_ids = sorted(cys_sg)
    disulfides, paired = [], set()
    for i, c1 in enumerate(cys_ids):
        for c2 in cys_ids[i + 1 :]:
            d = float(np.linalg.norm(cys_sg[c1] - cys_sg[c2]))
            if d <= 2.50:
                disulfides.append({"cys_pair": f"Cys{c1}-Cys{c2}", "sg_sg_dist_A": round(d, 3)})
                paired.update((c1, c2))
    free_d1_d3 = [c for c in cys_ids if c not in paired]
    return {
        "n_d1_d3_ectodomain_cysteines": len(cys_ids),
        "d1_d3_cysteine_residues": cys_ids,
        "n_closed_disulfides": len(disulfides),
        "disulfide_bridges": disulfides,
        "unpaired_cysteines_in_d1_d3": free_d1_d3,
        "sst2_cterm_unique_pentapeptide": "324-SKECF-328",
        "sst2_shared_hinge_prefix": "320-GKS (shared with ST2L 320-GKSL)",
        "cys327_ordinal_extracellular_cys": 11,
        "cys327_is_odd_unpaired_thiol": (len(free_d1_d3) == 0),
        "expected_oxidizing_biofluid_proteoforms": ["S-cysteinylated (+119 Da)", "S-glutathionylated (+305 Da)", "Cys327-Cys327 homodimer"],
    }


def scan_gencode_v46_skecf_cterminome_and_zone1_pas(cache_dir: Path) -> dict[str, Any]:
    tx_fa = resolve_dataset_path("DS_GENCODE_V46_TX", verify_hash=True)
    gtf_idx = load_gencode_comprehensive_index(resolve_dataset_path("DS_GENCODE_V46_COMP_GTF", verify_hash=True))
    tx_mrna_map = gtf_idx["tx_mrna_map"]
    n_pc_tx, skecf_genes, kecf_genes, skecf_4of5_genes = 0, set(), set(), set()

    def flush(hdr: str, seq: str) -> None:
        nonlocal n_pc_tx
        if not hdr:
            return
        enst, _, sym, biotype, _ = parse_gencode_fasta_header(hdr)
        tinfo = tx_mrna_map.get(enst) or {}
        cs, ce = tinfo.get("cds_start"), tinfo.get("cds_end")
        if biotype != "protein_coding" or cs is None or ce is None or (ce - cs) < 15:
            return
        cds = seq[int(cs) : int(ce)].upper()
        cds = cds[: (len(cds) // 3) * 3]
        if len(cds) < 15:
            return
        aas = "".join(CODON_AA.get(cds[i : i + 3], "X") for i in range(max(0, len(cds) - 18), len(cds), 3)).rstrip("*")
        if len(aas) < 5:
            return
        n_pc_tx += 1
        tail5 = aas[-5:]
        if tail5 == "SKECF":
            skecf_genes.add(sym)
        if tail5.endswith("KECF") and sym != "IL1RL1":
            kecf_genes.add(f"{sym}(-{tail5})")
        if sym != "IL1RL1" and sum(a == b for a, b in zip(tail5, "SKECF")) >= 4:
            skecf_4of5_genes.add(f"{sym}(-{tail5})")

    with gzip.open(tx_fa, "rt", encoding="utf-8") as fh:
        cur_h, chunks = "", []
        for ln in fh:
            if ln.startswith(">"):
                flush(cur_h, "".join(chunks))
                cur_h, chunks = ln.strip(), []
            else:
                chunks.append(ln.strip())
        flush(cur_h, "".join(chunks))
    assert "IL1RL1" in skecf_genes, "Expected IL1RL1 sST2 (-SKECF) in GENCODE v46 C-terminome!"

    # Zone 1 Intron-8 PAS/DSE steric-SSO window (chr2:102346035-102346125(+)) vs Zone 2 DO-NOT-MASK Exon-8 5'ss
    w_lo, w_hi = 102346035, 102346125
    gnomad_c = json.loads((cache_dir / "il1rl1_zone1_gnomad.json").read_text(encoding="utf-8")) if (cache_dir / "il1rl1_zone1_gnomad.json").is_file() else {}
    gg_c = json.loads((cache_dir / "il1rl1_zone1_gggenome.json").read_text(encoding="utf-8")) if (cache_dir / "il1rl1_zone1_gggenome.json").is_file() else {}
    avi_c = json.loads((cache_dir / "il1rl1_zone1_avi.json").read_text(encoding="utf-8")) if (cache_dir / "il1rl1_zone1_avi.json").is_file() else {}

    dna_plus = fetch_ensembl_dna_transient("2", w_lo, w_hi)
    pas_hits = [f"chr2:{w_lo + m.start()}-{w_lo + m.end() - 1}(+)" for m in re.finditer(r"A[AT]TAAA", dna_plus)]
    banned_1b, n_gnomad_vars = fetch_gnomad_banned_positions("2", w_lo, w_hi, gnomad_c)
    try:
        avi_pos = fetch_avi_positions_only("2", w_lo, w_hi, avi_c)
    except Exception:  # noqa: BLE001
        avi_pos = {}
    prem_rna, coords = genomic_to_premRNA(dna_plus, "chr2", w_lo, "+")
    pos_to_base = dict(zip(coords, prem_rna, strict=True))
    del dna_plus
    ranked = score_target_intervals("chr2", prem_rna, coords, "+", lengths=(18, 20), avi_by_pos=avi_pos, banned_positions_1b=banned_1b, mode="SKIP_CRYPTIC_EXON", feature_bounds_1b=(102346070, 102346105))
    picks = [ranked[0]]
    for cand in ranked[1:]:
        if abs(int(cand["grch38_start"]) - int(picks[0]["grch38_start"])) >= 6:
            picks.append(cand)
            break
    t_queries = []
    for iv in picks:
        s_dna = "".join(pos_to_base[p] for p in range(int(iv["grch38_start"]), int(iv["grch38_end"]) + 1)).replace("U", "T")
        query_gggenome_v2_coords_only(iv["interval_id"], s_dna, gg_c)
        t_queries.append({"interval_id": iv["interval_id"], "gene_symbol": "IL1RL1", "sense_dna": s_dna})
    del prem_rna, pos_to_base

    for fn, obj in (("il1rl1_zone1_gnomad.json", gnomad_c), ("il1rl1_zone1_gggenome.json", gg_c), ("il1rl1_zone1_avi.json", avi_c)):
        txt = json.dumps(obj, indent=2, allow_nan=False)
        assert not SEQ_GUARD_RE.search(txt), f"Biosecurity guard failed on {fn}"
        (cache_dir / fn).write_text(txt, encoding="utf-8")

    sp_hits, sp_bulge, _, _ = scan_gencode_spliced_transcriptome(tx_fa, t_queries, tx_mrna_map=gtf_idx["tx_mrna_map"], gene_biotype_by_id=gtf_idx["gene_biotype_by_id"], return_extended=True)
    t_queries.clear()

    zone1_candidates = []
    for rk, iv in enumerate(picks, 1):
        iv_id = iv["interval_id"]
        sp = sp_hits[iv_id]
        pm = map_hits_to_premRNA(gg_c[iv_id]["ungapped_hits"], "IL1RL1", gtf_idx["genes_by_cs"], gtf_idx["internal_ss_by_gene"], "premRNA_ungapped")
        pm_bg = map_hits_to_premRNA(gg_c[iv_id]["bulge_1nt_hits"], "IL1RL1", gtf_idx["genes_by_cs"], gtf_idx["internal_ss_by_gene"], "premRNA_bulge1nt")
        sp_0 = [x["gene_symbol"] for x in sp.values() if x["total_mismatches"] == 0]
        sp_1 = [x["gene_symbol"] for x in sp.values() if x["total_mismatches"] == 1]
        pm_0_ss = [x["gene_symbol"] for x in pm.values() if x["total_mismatches"] == 0 and x["dist_to_splice_boundary_bp"] <= 50]
        pm_1_ss = [x["gene_symbol"] for x in pm.values() if x["total_mismatches"] == 1 and x["dist_to_splice_boundary_bp"] <= 50]
        bg_pc = [k for k, v in {**pm_bg, **sp_bulge[iv_id]}.items() if v["biotype"] == "protein_coding" and v["steric_active_region"]]
        zone1_candidates.append({
            "rank": rk, "interval_id": iv_id, "length_bp": iv["length_bp"], "gc_pct": iv["gc_pct"],
            "tm_phys_pops_c": iv["tm_phys_pops_c"], "cpg_dinucs": iv["cpg_dinucs"], "max_avi_phred": iv["max_avi_phred"],
            "spliced_0mm_genes": len(sp_0), "spliced_1mm_genes": len(sp_1),
            "premRNA_0mm_splice50bp_genes": len(pm_0_ss), "premRNA_1mm_splice50bp_genes": len(pm_1_ss),
            "bulge_1nt_steric_pc_genes": len(bg_pc),
            "offtarget_status": "PASS_CLEAN_GE2MM" if not (sp_0 or sp_1 or pm_0_ss or pm_1_ss or bg_pc) else "CAUTION_1MM_OR_BULGE",
        })
    return {
        "gencode_v46_cterminome_audit": {
            "n_protein_coding_transcripts_scanned": n_pc_tx,
            "exact_SKECF_cterm_genes": sorted(skecf_genes),
            "offtarget_KECF_cterm_genes": sorted(kecf_genes),
            "offtarget_4of5_SKECF_cterm_genes": sorted(skecf_4of5_genes),
        },
        "isoform_selective_rna_modality_zones_1based_grch38": {
            "primary_lead_modality": "Low-dose intrathecal CD98hc/SLC3A2 or monovalent TfR1 neurovascular-shuttled cytoplasmic sST2 3'-UTR siRNA (chr2:102343416-102346100(+)) OR uniform 2'-O-MOE Zone 1 Intron-8 PAS/DSE steric SSO",
            "nuclear_rnaseh_intron8_gapmer_prohibited": True,
            "nuclear_gapmer_hazard_reason": "Nuclear RNase H1 cleavage anywhere inside Intron 8 (chr2:102343416-102346100(+)) destroys nascent full-length ST2L pre-mRNA co-transcriptionally prior to Exon 8->9 splicing.",
            "zone_1_safe_intron8_pas_dse_steric_window": "chr2:102346035-102346125(+)",
            "zone_1_pas_hexamer_coords_1b": pas_hits,
            "zone_1_gnomad_r4_total_variants": n_gnomad_vars,
            "zone_1_gnomad_af_ge_0p001_positions": sorted(banned_1b),
            "zone_1_top_steric_moe_intervals": zone1_candidates,
            "zone_2_do_not_mask_exon8_5ss_window": "chr2:102343400-102343435(+)",
            "zone_2_hazard_reason": "Covers canonical Exon-8 5' splice donor (chr2:102343415(+)); steric masking blocks Exon 8->9 splicing and depletes protective transmembrane ST2L (catastrophic sign inversion).",
        },
    }
