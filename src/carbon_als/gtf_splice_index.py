"""Comprehensive GENCODE v46 GTF index for internal pre-mRNA splice boundaries and spliced mRNA EEJ/CDS coordinates."""

from __future__ import annotations

import bisect
from collections import defaultdict
import gzip
from pathlib import Path
from typing import Any


def min_dist_to_sorted_points(lo: int, hi: int, pts: list[int]) -> int:
    """Minimum distance in bp/nt from closed interval [lo, hi] to sorted coordinate list pts."""
    if not pts:
        return 999_999
    i = bisect.bisect_left(pts, lo)
    if i < len(pts) and pts[i] <= hi:
        return 0
    cand: list[int] = []
    if i < len(pts):
        cand.append(abs(pts[i] - hi))
    if i > 0:
        cand.append(abs(lo - pts[i - 1]))
    return min(cand) if cand else 999_999


def _parse_gtf_attrs(attrs: str) -> tuple[str, str, str, str]:
    gid = gname = gtype = tid = ""
    for tok in attrs.split(";"):
        tok = tok.strip()
        if tok.startswith("gene_id "):
            gid = tok.split('"')[1].split(".")[0]
        elif tok.startswith("gene_name "):
            gname = tok.split('"')[1]
        elif tok.startswith("gene_type "):
            gtype = tok.split('"')[1]
        elif tok.startswith("transcript_id "):
            tid = tok.split('"')[1].split(".")[0]
    return gid, gname, gtype, tid


def load_gencode_comprehensive_index(gtf_gz_path: Path) -> dict[str, Any]:
    """Parse GENCODE GTF into gene spans, gene biotypes, internal splice junctions (excluding TSS/TES), and per-ENST mRNA EEJ/CDS maps."""
    genes_by_cs: dict[tuple[str, str], list[tuple[int, int, str, str, str]]] = defaultdict(list)
    gene_biotype_by_id: dict[str, str] = {}
    tx_exons: dict[str, tuple[str, str, str, list[tuple[int, int]]]] = {}
    tx_cds: dict[str, list[tuple[int, int]]] = defaultdict(list)

    with gzip.open(gtf_gz_path, "rt", encoding="utf-8") as fh:
        for line in fh:
            if not line or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 9:
                continue
            feat = cols[2]
            if feat not in ("gene", "exon", "CDS"):
                continue
            chrom, start_1b, end_1b, strand = cols[0], int(cols[3]), int(cols[4]), cols[6]
            gid, gname, gtype, tid = _parse_gtf_attrs(cols[8])
            if feat == "gene" and gid and gname:
                genes_by_cs[(chrom, strand)].append((start_1b, end_1b, gid, gname, gtype))
                gene_biotype_by_id[gid] = gtype
            elif feat == "exon" and tid and gid and gname:
                if tid not in tx_exons:
                    tx_exons[tid] = (gid, gname, strand, [(start_1b, end_1b)])
                else:
                    tx_exons[tid][3].append((start_1b, end_1b))
            elif feat == "CDS" and tid:
                tx_cds[tid].append((start_1b, end_1b))

    internal_ss_sets: dict[tuple[str, str], set[int]] = defaultdict(set)
    tx_mrna_map: dict[str, dict[str, Any]] = {}

    for tid, (gid, gname, strand, ex_list) in tx_exons.items():
        # Order exons 5' -> 3' along mRNA
        ex_sorted = sorted(ex_list, key=lambda x: x[0], reverse=(strand == "-"))
        if len(ex_sorted) >= 2:
            for idx_e, (es, ee) in enumerate(ex_sorted):
                if strand == "+":
                    if idx_e > 0:
                        internal_ss_sets[(gid, gname)].add(es)
                    if idx_e < len(ex_sorted) - 1:
                        internal_ss_sets[(gid, gname)].add(ee)
                else:
                    if idx_e > 0:
                        internal_ss_sets[(gid, gname)].add(ee)
                    if idx_e < len(ex_sorted) - 1:
                        internal_ss_sets[(gid, gname)].add(es)

        eej_offsets: list[int] = []
        cum = 0
        cds_intervals = tx_cds.get(tid, [])
        cds_mrna_min: int | None = None
        cds_mrna_max: int | None = None
        for idx_e, (es, ee) in enumerate(ex_sorted):
            elen = ee - es + 1
            for cs, ce in cds_intervals:
                ov_s, ov_e = max(es, cs), min(ee, ce)
                if ov_s <= ov_e:
                    m_s = cum + (ov_s - es) if strand == "+" else cum + (ee - ov_e)
                    m_e = cum + (ov_e - es + 1) if strand == "+" else cum + (ee - ov_s + 1)
                    cds_mrna_min = m_s if cds_mrna_min is None else min(cds_mrna_min, m_s)
                    cds_mrna_max = m_e if cds_mrna_max is None else max(cds_mrna_max, m_e)
            cum += elen
            if idx_e < len(ex_sorted) - 1:
                eej_offsets.append(cum)

        tx_mrna_map[tid] = {"eej_offsets": eej_offsets, "cds_start": cds_mrna_min, "cds_end": cds_mrna_max}

    internal_ss_by_gene = {k: sorted(v) for k, v in internal_ss_sets.items()}
    return {
        "genes_by_cs": genes_by_cs,
        "gene_biotype_by_id": gene_biotype_by_id,
        "internal_ss_by_gene": internal_ss_by_gene,
        "tx_mrna_map": tx_mrna_map,
    }


def load_gencode_gtf_index(gtf_gz_path: Path) -> tuple[dict[tuple[str, str], list[tuple[int, int, str, str, str]]], dict[str, list[int]]]:
    """Backward-compatible wrapper returning (genes_by_cs, internal_ss_by_symbol)."""
    comp = load_gencode_comprehensive_index(gtf_gz_path)
    by_sym: dict[str, set[int]] = defaultdict(set)
    for (_, gname), pts in comp["internal_ss_by_gene"].items():
        by_sym[gname].update(pts)
    return comp["genes_by_cs"], {g: sorted(v) for g, v in by_sym.items()}
