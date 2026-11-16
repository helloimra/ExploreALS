"""Coordinate-only human spliced-transcriptome and nascent pre-mRNA off-target scanner (zero oligomer sequence output)."""

from __future__ import annotations

from collections import defaultdict
import gzip
from pathlib import Path
from typing import Any

from carbon_als.gtf_splice_index import (
    load_gencode_comprehensive_index,
    load_gencode_gtf_index,
    min_dist_to_sorted_points,
)

__all__ = [
    "classify_spliced_hit_region",
    "count_mismatch_and_wobble",
    "detect_internal_1nt_bulge",
    "load_gencode_comprehensive_index",
    "load_gencode_gtf_index",
    "min_dist_to_sorted_points",
    "parse_gencode_fasta_header",
    "scan_gencode_spliced_transcriptome",
    "split_pigeonhole_3seeds",
]


def split_pigeonhole_3seeds(seq_dna: str) -> list[tuple[int, str]]:
    """Split an 18..24 bp sense slice into 3 disjoint seeds guaranteeing 100% recall at <=2 mismatches."""
    n = len(seq_dna)
    if n < 15:
        raise ValueError(f"Interval length {n} too short for 3-block <=2mm pigeonhole indexing.")
    b1, b2 = n // 3, (2 * n) // 3
    return [(0, seq_dna[:b1]), (b1, seq_dna[b1:b2]), (b2, seq_dna[b2:])]


def count_mismatch_and_wobble(query_sense_dna: str, sbjct_sense_dna: str) -> tuple[int, int, int]:
    """Return (total_mismatches, gu_wobble_pairs, destabilizing_mismatches) for antisense SSO pairing to sbjct RNA."""
    n_mis = n_gu = 0
    for qb, sb in zip(query_sense_dna, sbjct_sense_dna, strict=True):
        if qb != sb:
            n_mis += 1
            if (qb == "C" and sb == "T") or (qb == "A" and sb == "G"):
                n_gu += 1
    return n_mis, n_gu, n_mis - n_gu


def detect_internal_1nt_bulge(query_dna: str, seq: str, s0: int) -> tuple[str, int] | None:
    """Test whether seq starting at s0 matches query_dna with 0 substitutions and 1 internal 1-nt RNA or SSO bulge."""
    q_len, s_len = len(query_dna), len(seq)
    if 0 <= s0 and s0 + q_len + 1 <= s_len:
        sub_r = seq[s0 : s0 + q_len + 1]
        lcp = next((i for i in range(q_len) if query_dna[i] != sub_r[i]), q_len)
        lcs = next((i for i in range(q_len) if query_dna[q_len - 1 - i] != sub_r[q_len - i]), q_len)
        if lcp >= 1 and lcs >= 1 and lcp + lcs >= q_len:
            return ("RNA_BULGE_1NT", q_len + 1)
    if 0 <= s0 and s0 + q_len - 1 <= s_len:
        sub_s = seq[s0 : s0 + q_len - 1]
        lcp = next((i for i in range(q_len - 1) if query_dna[i] != sub_s[i]), q_len - 1)
        lcs = next((i for i in range(q_len - 1) if query_dna[q_len - 1 - i] != sub_s[q_len - 2 - i]), q_len - 1)
        if lcp >= 1 and lcs >= 1 and lcp + lcs >= q_len - 1:
            return ("SSO_BULGE_1NT", q_len - 1)
    return None


def classify_spliced_hit_region(start_0b: int, end_0b: int, tx_info: dict[str, Any] | None) -> tuple[int, str, bool]:
    """Return (dist_to_eej_nt, tx_region, steric_active_region) using comprehensive GTF mRNA offsets."""
    if not tx_info:
        return 0, "UNKNOWN_TX_MAP", True
    d_eej = min_dist_to_sorted_points(start_0b, end_0b, tx_info.get("eej_offsets") or [])
    cds_s, cds_e = tx_info.get("cds_start"), tx_info.get("cds_end")
    if d_eej <= 50:
        return d_eej, "EEJ_LE50NT", True
    if cds_s is not None and start_0b <= int(cds_s) + 25:
        return d_eej, "UTR5_OR_AUG_LE25NT", True
    if cds_s is not None and cds_e is not None and start_0b < int(cds_e) and end_0b > int(cds_s):
        return d_eej, "INTERNAL_CDS_GT50EEJ", False
    if cds_e is not None and start_0b >= int(cds_e):
        return d_eej, "UTR3_GT50EEJ", False
    return d_eej, "NONCODING_ISOFORM_GT50EEJ", False


def parse_gencode_fasta_header(header: str) -> tuple[str, str, str, str, bool]:
    parts = header.lstrip(">").strip().split("|")
    enst = parts[0].split(".")[0] if len(parts) > 0 else ""
    ensg = parts[1].split(".")[0] if len(parts) > 1 else ""
    sym = parts[5] if len(parts) > 5 else ensg
    tx_biotype = parts[7] if len(parts) > 7 else "unknown"
    return enst, ensg, sym, tx_biotype, ("MANE_Select" in header)


def scan_gencode_spliced_transcriptome(
    fasta_gz_path: Path,
    queries: list[dict[str, Any]],
    tx_mrna_map: dict[str, dict[str, Any]] | None = None,
    gene_biotype_by_id: dict[str, str] | None = None,
    return_extended: bool = False,
) -> Any:
    """Scan GENCODE v46 spliced transcripts for <=2mm, 1-nt bulges, and 18-bp sub-cores (for length > 18)."""
    seed3_map: dict[str, list[tuple[str, str, int, str, int]]] = defaultdict(list)
    bulge2_map: dict[str, list[tuple[str, str, bool, int, str, int]]] = defaultdict(list)
    sub18_map: dict[str, list[tuple[str, str, int, str]]] = defaultdict(list)

    for q in queries:
        iv_id, t_gene, s_dna = str(q["interval_id"]), str(q["gene_symbol"]), str(q["sense_dna"]).upper()
        q_len, half = len(s_dna), len(s_dna) // 2
        for off, seed in split_pigeonhole_3seeds(s_dna):
            seed3_map[seed].append((iv_id, t_gene, off, s_dna, q_len))
        bulge2_map[s_dna[:half]].append((iv_id, t_gene, True, half, s_dna, q_len))
        bulge2_map[s_dna[half:]].append((iv_id, t_gene, False, half, s_dna, q_len))
        if q_len > 18:
            for w_off in range(q_len - 18 + 1):
                sub18 = s_dna[w_off : w_off + 18]
                for off, seed in split_pigeonhole_3seeds(sub18):
                    sub18_map[seed].append((iv_id, t_gene, off, sub18))

    best_by_iv: dict[str, dict[str, dict[str, Any]]] = {str(q["interval_id"]): {} for q in queries}
    bulge_by_iv: dict[str, dict[str, dict[str, Any]]] = {str(q["interval_id"]): {} for q in queries}
    sub18_by_iv: dict[str, dict[str, dict[str, Any]]] = {str(q["interval_id"]): {} for q in queries}
    n_tx = 0

    def process_record(hdr: str, chunks: list[str]) -> None:
        nonlocal n_tx
        if not hdr:
            return
        n_tx += 1
        enst, ensg, sym, tx_bt, is_mane = parse_gencode_fasta_header(hdr)
        gene_bt = (gene_biotype_by_id or {}).get(ensg, "protein_coding" if tx_bt == "protein_coding" else tx_bt)
        tx_info = (tx_mrna_map or {}).get(enst) if tx_mrna_map is not None else None
        seq = "".join(chunks).upper()
        s_len = len(seq)

        chk3: set[tuple[str, int]] = set()
        for seed, entries in seed3_map.items():
            idx = seq.find(seed)
            while idx != -1:
                for iv_id, t_gene, off, q_dna, q_len in entries:
                    st = idx - off
                    if sym != t_gene and 0 <= st and st + q_len <= s_len and (iv_id, st) not in chk3:
                        chk3.add((iv_id, st))
                        nm, ngu, nd = count_mismatch_and_wobble(q_dna, seq[st : st + q_len])
                        if nm <= 2:
                            d_eej, reg, active = classify_spliced_hit_region(st, st + q_len, tx_info)
                            rk = (nm, nd, 0 if active else 1, d_eej, 0 if gene_bt == "protein_coding" else 1, 0 if is_mane else 1)
                            cur = best_by_iv[iv_id].get(sym)
                            if cur is None or rk < cur["_rk"]:
                                best_by_iv[iv_id][sym] = {
                                    "gene_symbol": sym, "ensembl_gene_id": ensg, "biotype": gene_bt, "tx_biotype": tx_bt,
                                    "in_mane_select": is_mane, "total_mismatches": nm, "gu_wobble_pairs": ngu,
                                    "destabilizing_mismatches": nd, "dist_to_eej_nt": d_eej, "tx_region": reg,
                                    "steric_active_region": active, "_rk": rk,
                                }
                idx = seq.find(seed, idx + 1)

        if not return_extended:
            return
        chkb: set[tuple[str, int]] = set()
        for bseed, bentries in bulge2_map.items():
            idx = seq.find(bseed)
            while idx != -1:
                for iv_id, t_gene, is_pref, half, q_dna, q_len in bentries:
                    if sym == t_gene:
                        continue
                    for s0 in ([idx] if is_pref else [idx - half - 1, idx - half + 1]):
                        if (iv_id, s0) not in chkb:
                            chkb.add((iv_id, s0))
                            bres = detect_internal_1nt_bulge(q_dna, seq, s0)
                            if bres is not None:
                                btype, mlen = bres
                                d_eej, reg, active = classify_spliced_hit_region(s0, s0 + mlen, tx_info)
                                rk = (0 if active else 1, d_eej, 0 if gene_bt == "protein_coding" else 1)
                                cur = bulge_by_iv[iv_id].get(sym)
                                if cur is None or rk < cur["_rk"]:
                                    bulge_by_iv[iv_id][sym] = {
                                        "gene_symbol": sym, "ensembl_gene_id": ensg, "biotype": gene_bt, "bulge_type": btype,
                                        "dist_to_eej_nt": d_eej, "tx_region": reg, "steric_active_region": active, "_rk": rk,
                                    }
                idx = seq.find(bseed, idx + 1)

        chks: set[tuple[str, int, str]] = set()
        for sseed, sentries in sub18_map.items():
            idx = seq.find(sseed)
            while idx != -1:
                for iv_id, t_gene, off, sub18 in sentries:
                    st = idx - off
                    if sym != t_gene and 0 <= st and st + 18 <= s_len and (iv_id, st, sub18) not in chks:
                        chks.add((iv_id, st, sub18))
                        nm, ngu, nd = count_mismatch_and_wobble(sub18, seq[st : st + 18])
                        if nd == 0:
                            d_eej, reg, active = classify_spliced_hit_region(st, st + 18, tx_info)
                            rk = (nm, 0 if active else 1, d_eej)
                            cur = sub18_by_iv[iv_id].get(sym)
                            if cur is None or rk < cur["_rk"]:
                                sub18_by_iv[iv_id][sym] = {
                                    "gene_symbol": sym, "ensembl_gene_id": ensg, "biotype": gene_bt,
                                    "sub18_mismatches": nm, "sub18_wobbles": ngu, "dist_to_eej_nt": d_eej,
                                    "tx_region": reg, "steric_active_region": active, "_rk": rk,
                                }
                idx = seq.find(sseed, idx + 1)

    with gzip.open(fasta_gz_path, "rt", encoding="utf-8") as fh:
        cur_hdr, chunks = "", []
        for line in fh:
            if line.startswith(">"):
                process_record(cur_hdr, chunks)
                cur_hdr, chunks = line, []
            else:
                chunks.append(line.strip())
        process_record(cur_hdr, chunks)

    for store in (best_by_iv, bulge_by_iv, sub18_by_iv):
        for iv_hits in store.values():
            for rec in iv_hits.values():
                rec.pop("_rk", None)
    return (best_by_iv, bulge_by_iv, sub18_by_iv, n_tx) if return_extended else best_by_iv
