"""Helpers for RUN-P3B-002: Transient RAM Ensembl/gnomAD/AlphaGenome-AVI scoring & coordinate-only GGGenome v2 off-target queries."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import time
from typing import Any
import urllib.parse
import urllib.request

import pandas as pd

from carbon_als.offtarget_scanner import min_dist_to_sorted_points
from carbon_als.skill_cli import run_skill_cli_raw_output
from carbon_als.splice_design import _revcomp_dna

import os

PRIMARY_CHROMS = {f"chr{i}" for i in range(1, 23)} | {"chrX", "chrY", "chrM"}
AVI_SCRIPT = Path(os.environ.get("ALPHAGENOME_AVI_CLI", ""))

# (dn_id, gene, cnum, win_s, win_e, strand, feat_bounds, score_mode, mech_class, n_picks, atlas_bounds)
DENOVO_CIS_SPECS: list[tuple[str, str, str, int, int, str, tuple[int, int], str, str, int, tuple[int, int]]] = [
    ("DN-01", "ATG4B", "2", 241668870, 241669005, "+", (241668875, 241668985), "SKIP_CRYPTIC_EXON", "CRYPTIC_CASSETTE_EXON_SKIP", 2, (241668875, 241668985)),
    ("DN-02", "KALRN", "3", 124701256, 124701282, "+", (124701255, 124701255), "SKIP_CRYPTIC_EXON", "CRYPTIC_CASSETTE_DOWNSTREAM_INTRONIC_ISE", 1, (124700977, 124701255)),
    ("DN-02", "KALRN", "3", 124701075, 124701115, "+", (124701093, 124701093), "SKIP_CRYPTIC_EXON", "CRYPTIC_CASSETTE_MAJOR_3SS_AND_SHARED_EXON", 1, (124700977, 124701255)),
    ("DN-03", "PTPRT", "20", 42099255, 42099281, "-", (42098553, 42099289), "SKIP_CRYPTIC_EXON", "CRYPTIC_A3SS_PROXIMAL_EXON_BLOCK", 1, (42098552, 42102124)),
    ("DN-03", "PTPRT", "20", 42099288, 42099310, "-", (42099289, 42099289), "SKIP_CRYPTIC_EXON", "CRYPTIC_A3SS_ACCEPTOR_BLOCK", 1, (42098552, 42102124)),
    ("DN-04", "CELF5", "19", 3278180, 3278345, "+", (3278209, 3278316), "SKIP_CRYPTIC_EXON", "CRYPTIC_CASSETTE_EXON_SKIP", 2, (3278209, 3278316)),
    ("DN-06", "PFKP", "10", 3099530, 3099845, "+", (3099557, 3099819), "SKIP_CRYPTIC_EXON", "CRYPTIC_CASSETTE_EXON_SKIP", 2, (3099557, 3099819)),
    ("DN-07", "TRAPPC12", "2", 3457770, 3457820, "+", (3457795, 3457795), "SKIP_CRYPTIC_EXON", "CRYPTIC_ALE_3SS_ACCEPTOR_BLOCK", 2, (3457795, 3458181)),
    ("DN-08", "ELK1", "X", 47631625, 47632050, "-", (47631625, 47632050), "GAPMER_RNASE_H", "CRYPTIC_3EXT_ISOFORM_GAPMER_WINDOW", 2, (47631618, 47635519)),
    ("DN-09", "DLGAP1", "18", 4147642, 4147692, "-", (4147667, 4147667), "SKIP_CRYPTIC_EXON", "CRYPTIC_ALE_3SS_ACCEPTOR_BLOCK", 2, (4145795, 4147667)),
]

GNOMAD_GQL = """query($chrom:String!,$start:Int!,$stop:Int!){region(chrom:$chrom,start:$start,stop:$stop,reference_genome:GRCh38){variants(dataset:gnomad_r4){variant_id exome{af} genome{af}}}}"""


def build_alphagenome_locus_url(chrom: str, s1: int, e1: int, pad_bp: int = 250) -> str:
    lo = max(1, min(s1, e1) - pad_bp)
    hi = max(s1, e1) + pad_bp
    q = {"q": f"{chrom}:{lo}-{hi}", "m": "locus", "lItems": "avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE"}
    return "https://deepmind.google.com/science/alphagenome/atlas?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote, safe=":,-")


def fetch_ensembl_dna_transient(chrom_num: str, s1: int, e1: int) -> str:
    seq = ""
    for attempt in range(2):
        try:
            url = f"https://rest.ensembl.org/sequence/region/human/{chrom_num}:{s1}..{e1}?coord_system_version=GRCh38"
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "text/plain", "User-Agent": "CarbonALS/0.5"}), timeout=20) as resp:
                seq = resp.read().decode("utf-8").strip().upper()
            break
        except Exception:  # noqa: BLE001
            if attempt == 1:
                u2 = f"https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chr{chrom_num};start={s1 - 1};end={e1}"
                with urllib.request.urlopen(urllib.request.Request(u2, headers={"User-Agent": "CarbonALS/0.5"}), timeout=25) as r2:
                    seq = json.loads(r2.read().decode("utf-8"))["dna"].strip().upper()
    assert len(seq) == (e1 - s1 + 1), f"Sequence length mismatch on chr{chrom_num}:{s1}-{e1}"
    return seq


def audit_atg4b_ce_ptc_in_ram() -> dict[str, Any]:
    seq = fetch_ensembl_dna_transient("2", 241668875, 241668985)
    codons = [seq[i : i + 3] for i in range(0, len(seq) - 2, 3)]
    ptc_1b = [idx + 1 for idx, c in enumerate(codons) if c in ("TAA", "TAG", "TGA")]
    del seq, codons
    return {"ce_coords": "chr2:241668875-241668985(+)", "ce_len_bp": 111, "upstream_exon10_end": 241668685, "upstream_phase": 0, "inframe_ptc_codon_indices_1b": ptc_1b}


def audit_ptprt_a3ss_ptc_in_ram() -> dict[str, Any]:
    seq_plus = fetch_ensembl_dna_transient("20", 42098553, 42099289)
    seq_5to3 = _revcomp_dna(seq_plus)
    codons = [seq_5to3[i : i + 3] for i in range(0, len(seq_5to3) - 2, 3)]
    ptc_1b = [idx + 1 for idx, c in enumerate(codons) if c in ("TAA", "TAG", "TGA")]
    first_ptc_dist_to_eej = (len(seq_5to3) - 3 * ptc_1b[0]) + (42098552 - 42098421 + 1)
    del seq_plus, seq_5to3, codons
    return {
        "a3ss_extension_coords": "chr20:42098553-42099289(-)",
        "cryptic_acceptor_1b": 42099289,
        "canonical_acceptor_1b": 42098552,
        "upstream_exon26_donor_1b": 42102124,
        "upstream_phase": 0,
        "extension_len_bp": 737,
        "extension_len_mod3": 737 % 3,
        "first_5_inframe_ptc_codon_indices_1b": ptc_1b[:5],
        "first_ptc_dist_to_downstream_eej_nt": first_ptc_dist_to_eej,
    }


def fetch_avi_positions_only(chrom_num: str, s1: int, e1: int, avi_cache: dict[str, Any]) -> dict[int, float]:
    key = f"chr{chrom_num}:{s1}-{e1}"
    if key in avi_cache:
        return {int(k): float(v) for k, v in avi_cache[key].items()}
    with tempfile.TemporaryDirectory() as tmpd:
        tmp_tsv = Path(tmpd) / "avi_region.tsv"
        run_skill_cli_raw_output(AVI_SCRIPT, ["region", "--region", key, "--min_phred", "0.0"], tmp_tsv, timeout_sec=90, use_cache=False)
        df = pd.read_csv(tmp_tsv, sep="\t")
        pos_max = {str(int(p)): round(float(v), 3) for p, v in df.groupby("position")["avi_phred"].max().items()}
    avi_cache[key] = pos_max
    return {int(k): float(v) for k, v in pos_max.items()}


def fetch_gnomad_banned_positions(chrom_num: str, s1: int, e1: int, cache: dict[str, Any]) -> tuple[set[int], int]:
    key = f"chr{chrom_num}:{s1}-{e1}"
    if key in cache:
        return set(cache[key]["banned_positions_af_ge_0p001"]), int(cache[key]["total_gnomad_r4_variants"])
    body = json.dumps({"query": GNOMAD_GQL, "variables": {"chrom": chrom_num, "start": s1, "stop": e1}}).encode("utf-8")
    req = urllib.request.Request("https://gnomad.broadinstitute.org/api", data=body, headers={"Content-Type": "application/json", "User-Agent": "CarbonALS/0.5"}, method="POST")
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    vlist = (((raw.get("data") or {}).get("region") or {}).get("variants")) or []
    banned: set[int] = set()
    for v in vlist:
        if max(float((v.get("exome") or {}).get("af") or 0.0), float((v.get("genome") or {}).get("af") or 0.0)) >= 0.001:
            parts = str(v["variant_id"]).split("-")
            banned.update(range(int(parts[1]), int(parts[1]) + len(parts[2])))
    cache[key] = {"total_gnomad_r4_variants": len(vlist), "banned_positions_af_ge_0p001": sorted(banned)}
    time.sleep(0.5)
    return banned, len(vlist)


def _gg_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "CarbonALS/0.5"}), timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _parse_ungapped(results: list[dict[str, Any]], sense_dna: str) -> list[dict[str, int | str]]:
    out: list[dict[str, int | str]] = []
    for h in results:
        chrom, h_st = str(h.get("name", "")), str(h.get("strand", "+"))
        if chrom not in PRIMARY_CHROMS:
            continue
        q_s = str(h["query"]).upper() if h_st == "+" else _revcomp_dna(str(h["query"]).upper())
        s_s = str(h["sbjct"]).upper() if h_st == "+" else _revcomp_dna(str(h["sbjct"]).upper())
        assert q_s == sense_dna
        nmis = sum(1 for qb, sb in zip(q_s, s_s, strict=True) if qb != sb)
        ngu = sum(1 for qb, sb in zip(q_s, s_s, strict=True) if (qb == "C" and sb == "T") or (qb == "A" and sb == "G"))
        out.append({"chrom": chrom, "grch38_start": int(h["position"]), "grch38_end": int(h["position_end"]), "strand": h_st, "total_mismatches": nmis, "gu_wobble_pairs": ngu, "destabilizing_mismatches": nmis - ngu})
    return out


def query_gggenome_v2_coords_only(iv_id: str, sense_dna: str, gg_cache: dict[str, Any]) -> dict[str, Any]:
    cur = gg_cache.get(iv_id)
    if isinstance(cur, dict) and cur.get("schema_v") == 2:
        return cur
    used_mm, raw_ug = 2, {}
    for mm in (2, 1, 0):
        raw_ug = _gg_json(f"https://gggenome.dbcls.jp/hg38/{mm}/nogap/{sense_dna}.json")
        if raw_ug.get("error") == "none":
            used_mm = mm
            break
    assert raw_ug.get("error") == "none", f"GGGenome failed on {iv_id}"
    ug = _parse_ungapped(raw_ug.get("results", []), sense_dna)
    raw_gap = _gg_json(f"https://gggenome.dbcls.jp/hg38/1/{sense_dna}.json") if used_mm == 2 else {"error": "alu_skip", "results": []}
    gap_ok = raw_gap.get("error") == "none"
    bulges = [{"chrom": str(h["name"]), "grch38_start": int(h["position"]), "grch38_end": int(h["position_end"]), "strand": str(h["strand"]), "bulge_type": "RNA_BULGE_1NT" if "-" in str(h["query"]) else "SSO_BULGE_1NT"}
              for h in (raw_gap.get("results", []) if gap_ok else []) if str(h.get("name")) in PRIMARY_CHROMS and ("-" in str(h["query"]) or "-" in str(h["sbjct"]))]
    sub18: list[dict[str, int | str]] = []
    if len(sense_dna) > 18:
        seen: set[tuple[str, int, int, str]] = set()
        for off in range(len(sense_dna) - 18 + 1):
            rs = _gg_json(f"https://gggenome.dbcls.jp/hg38/1/nogap/{sense_dna[off : off + 18]}.json")
            if rs.get("error") == "none":
                for sh in _parse_ungapped(rs.get("results", []), sense_dna[off : off + 18]):
                    lk = (str(sh["chrom"]), int(sh["grch38_start"]), int(sh["grch38_end"]), str(sh["strand"]))
                    if int(sh["destabilizing_mismatches"]) == 0 and lk not in seen:
                        seen.add(lk)
                        sub18.append({**sh, "subwindow_offset": off})
            time.sleep(0.1)
    entry = {"schema_v": 2, "max_mm_queried": used_mm, "gapped_1edit_queried": gap_ok, "ungapped_hits": ug, "bulge_1nt_hits": bulges, "sub18_core_0destab_hits": sub18}
    gg_cache[iv_id] = entry
    time.sleep(0.15)
    return entry


def map_hits_to_premRNA(hits: list[dict[str, Any]], t_gene: str, genes_by_cs: dict, ss_by_gene: dict, mode_key: str) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for h in hits:
        c, lo, hi, st = str(h["chrom"]), int(h["grch38_start"]), int(h["grch38_end"]), str(h["strand"])
        for gs, ge, gid, gn, gtype in genes_by_cs.get((c, st), []):
            if gn == t_gene or hi < gs or lo > ge:
                continue
            sdist = min_dist_to_sorted_points(lo, hi, ss_by_gene.get((gid, gn), []))
            nmis, ndest, ngu = int(h.get("total_mismatches", 1)), int(h.get("destabilizing_mismatches", 0)), int(h.get("gu_wobble_pairs", 0))
            rk = (nmis, ndest, sdist, 0 if gtype == "protein_coding" else 1)
            if gn not in best or rk < best[gn]["_rk"]:
                best[gn] = {"gene_symbol": gn, "ensembl_gene_id": gid, "biotype": gtype, "hit_coord": f"{c}:{lo}-{hi}({st})", "total_mismatches": nmis, "gu_wobble_pairs": ngu, "destabilizing_mismatches": ndest, "dist_to_splice_boundary_bp": sdist, "steric_active_region": (sdist <= 50), "mode": h.get("bulge_type", mode_key), "_rk": rk}
    for v in best.values():
        v.pop("_rk", None)
    return best
