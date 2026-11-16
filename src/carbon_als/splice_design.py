"""Coordinate-resolved biophysical, cis-motif, and intrathecal-safety interval scorer on GRCh38."""

from __future__ import annotations

import math
import re
from typing import Any

COMP_DNA = str.maketrans("ACGTacgt", "TGCAtgca")
COMP_RNA = str.maketrans("ACGUacgu", "UGCAugca")

# Sugimoto et al. (1995) Biochemistry 34:11211 nearest-neighbor RNA/DNA parameters
NN_RNA_DNA: dict[str, tuple[float, float]] = {
    "AA": (-7.8, -21.9), "AU": (-8.3, -23.9), "AC": (-5.9, -12.3), "AG": (-9.1, -23.5),
    "UA": (-7.8, -23.2), "UU": (-11.5, -36.4), "UC": (-8.6, -22.9), "UG": (-10.4, -28.4),
    "CA": (-9.0, -26.1), "CU": (-7.0, -19.7), "CC": (-9.3, -23.2), "CG": (-16.3, -47.1),
    "GA": (-5.5, -13.2), "GU": (-7.8, -21.6), "GC": (-8.0, -17.1), "GG": (-12.8, -31.9),
}

ISS_MOTIFS = ("UAGGG", "UUAGG", "UAGG", "CUCUCU", "UCUCU", "UCUU")
ESE_MOTIFS = ("CACACGA", "GGAAGA", "AGAAGA", "GGAGG", "GAAGA", "UGAAG")
_ISS_SPAN_RE = re.compile("|".join(ISS_MOTIFS))
_ESE_SPAN_RE = re.compile("|".join(ESE_MOTIFS))


def _revcomp_dna(seq: str) -> str:
    return seq.upper().translate(COMP_DNA)[::-1]


def _revcomp_rna(seq: str) -> str:
    return seq.upper().translate(COMP_RNA)[::-1]


def genomic_to_premRNA(dna_plus: str, chrom: str, start_1b: int, strand: str) -> tuple[str, list[int]]:
    """Map forward-strand GRCh38 DNA window onto 5'->3' nascent pre-mRNA + 1-based genomic coords."""
    clean = re.sub(r"[^ACGTacgt]", "", dna_plus).upper()
    coords = list(range(start_1b, start_1b + len(clean)))
    if strand == "+":
        return clean.replace("T", "U"), coords
    return _revcomp_dna(clean).replace("T", "U"), coords[::-1]


def duplex_tm_moe(target_rna_5to3: str, conc_m: float = 1e-7) -> tuple[float, float]:
    """Compute (Tm_MOE_1M_C, dG37_kcal) for a 2'-O-MOE steric-blocking window at 1 M Na+ reference."""
    rna = target_rna_5to3.upper()
    dh, ds = 1.9, -3.9
    for i in range(len(rna) - 1):
        step_h, step_s = NN_RNA_DNA.get(rna[i : i + 2], (-8.0, -22.0))
        dh += step_h
        ds += step_s
    dg37 = dh - 310.15 * (ds / 1000.0)
    tm_base_c = (1000.0 * dh) / (ds + 1.987 * math.log(conc_m / 4.0)) - 273.15
    return round(tm_base_c + 1.1 * len(rna), 2), round(dg37, 2)


def duplex_tm_moe_physiological(
    target_rna_5to3: str,
    conc_m: float = 1e-7,
    na_m: float = 0.15,
    n_po_substitutions: int = 6,
) -> float:
    """Compute physiological 150 mM Na+ mixed-PO/PS 2'-O-MOE melting temperature (SantaLucia salt + PS depression)."""
    rna = target_rna_5to3.upper()
    n_steps = max(len(rna) - 1, 1)
    dh, ds = 1.9, -3.9
    for i in range(len(rna) - 1):
        step_h, step_s = NN_RNA_DNA.get(rna[i : i + 2], (-8.0, -22.0))
        dh += step_h
        ds += step_s
    ds_salt = ds + 0.368 * n_steps * math.log(max(na_m, 1e-3))
    tm_salt_c = (1000.0 * dh) / (ds_salt + 1.987 * math.log(conc_m / 4.0)) - 273.15
    n_ps = max(n_steps - n_po_substitutions, 0)
    return round(tm_salt_c + 0.85 * len(rna) - 0.45 * n_ps, 2)


def _max_self_stem(seq_dna: str) -> int:
    rc = _revcomp_dna(seq_dna)
    n = len(seq_dna)
    for k in range(min(10, n // 2), 2, -1):
        for i in range(n - k + 1):
            sub = seq_dna[i : i + k]
            if sub in rc[n - i:] or sub in rc[: max(0, n - i - k)]:
                return k
    return 0


def score_target_intervals(
    chrom: str,
    prem_rna: str,
    coords_1b: list[int],
    strand: str,
    lengths: tuple[int, ...] = (18, 20, 22),
    banned_positions_1b: set[int] | None = None,
    mode: str = "SKIP_CRYPTIC_EXON",
    feature_bounds_1b: tuple[int, int] | None = None,
    avi_by_pos: dict[int, float] | None = None,
) -> list[dict[str, Any]]:
    """Rank polymorphism-free GRCh38 cis-regulatory target intervals by biophysics, motifs & AVI."""
    banned = banned_positions_1b or set()
    avi_map = avi_by_pos or {}
    hits: list[dict[str, Any]] = []
    for k in lengths:
        for i in range(len(prem_rna) - k + 1):
            t_rna = prem_rna[i : i + k]
            t_coords = coords_1b[i : i + k]
            if any(pos in banned for pos in t_coords):
                continue
            comp = _revcomp_rna(t_rna).replace("U", "T")
            if "GGGG" in comp or "CCCC" in comp or "AAAAA" in comp or "TTTTT" in comp:
                continue
            gc_pct = 100.0 * (comp.count("G") + comp.count("C")) / k
            min_gc = 33.0 if mode == "INCLUDE_EXON_UPSTREAM_UG" else 40.0
            if not (min_gc <= gc_pct <= 65.0):
                continue
            stem = _max_self_stem(comp)
            if stem >= 6:
                continue
            tm_c, dg37 = duplex_tm_moe(t_rna)
            tm_phys_c = duplex_tm_moe_physiological(t_rna)
            cpg = comp.count("CG")
            ug_tracts = t_rna.count("UG")
            iss_n = len(_ISS_SPAN_RE.findall(t_rna))
            ese_n = len(_ESE_SPAN_RE.findall(t_rna))
            mean_avi = sum(avi_map.get(p, 0.0) for p in t_coords) / k if avi_map else 0.0
            max_avi = max((avi_map.get(p, 0.0) for p in t_coords), default=0.0)

            g_min, g_max = min(t_coords), max(t_coords)
            in_exonic, boundary_dist = False, 999
            if feature_bounds_1b is not None:
                f_lo, f_hi = min(feature_bounds_1b), max(feature_bounds_1b)
                in_exonic = not (g_max < f_lo or g_min > f_hi)
                boundary_dist = min(abs(g_min - f_lo), abs(g_max - f_lo), abs(g_min - f_hi), abs(g_max - f_hi))

            wt_sponge_flag = bool(mode == "INCLUDE_EXON_UPSTREAM_UG" and ug_tracts >= 6)
            if mode == "INCLUDE_CONSTITUTIVE_EXON":
                if in_exonic or boundary_dist < 12:
                    continue  # Spare canonical 5'SS/3'SS splice boundaries while allowing conserved deep intronic ISS motifs
                safety_bonus = 12.0 if (iss_n >= 2 and ug_tracts <= 1) else (8.0 if (iss_n == 1 and ug_tracts <= 1) else 0.0)
                score = 12.0 * iss_n + safety_bonus - 6.0 * ug_tracts - 1.5 * stem - 0.15 * abs(tm_c - 68.0) - 0.06 * boundary_dist
            elif mode == "INCLUDE_EXON_UPSTREAM_UG":
                if feature_bounds_1b is None or in_exonic or boundary_dist < 14 or ug_tracts < 4:
                    continue
                f_lo, f_hi = min(feature_bounds_1b), max(feature_bounds_1b)
                is_upstream = (g_min > f_hi) if strand == "-" else (g_max < f_lo)
                if not is_upstream:
                    continue
                # Penalize dense (UG)>=6 windows for WT bystander TDP-43 displacement risk while ranking within upstream UG class
                bystander_pen = 22.0 if wt_sponge_flag else 12.0
                score = 5.0 * ug_tracts - bystander_pen + 4.0 * iss_n - 1.5 * stem - 0.12 * abs(tm_c - 65.0) - 0.04 * boundary_dist
            elif mode == "GAPMER_RNASE_H":
                if feature_bounds_1b is not None:
                    f_lo, f_hi = min(feature_bounds_1b), max(feature_bounds_1b)
                    if g_min < f_lo or g_max > f_hi:
                        continue  # Strictly inside retained exonic/3'Ext RNA span (never post-cleavage)
                    boundary_dist = min(abs(g_min - f_lo), abs(g_max - f_hi))
                score = 8.0 - 2.0 * cpg - 1.5 * stem - 0.15 * abs(tm_phys_c - 62.0) - 0.08 * abs(gc_pct - 50.0) + 0.2 * max_avi
            else:
                if not in_exonic and boundary_dist > 15:
                    continue
                score = 10.0 * ese_n + 0.4 * max_avi + (8.0 if boundary_dist <= 8 else 0.0) - 1.5 * stem - 0.15 * abs(tm_c - 68.0)

            hits.append({
                "interval_id": f"{chrom}:{g_min}-{g_max}({strand})",
                "chrom": chrom,
                "grch38_start": g_min,
                "grch38_end": g_max,
                "strand": strand,
                "length_bp": k,
                "mode": mode,
                "gc_pct": round(gc_pct, 1),
                "tm_moe_c": tm_c,
                "tm_phys_pops_c": tm_phys_c,
                "dg37_kcal": dg37,
                "cpg_dinucs": cpg,
                "max_self_stem_bp": stem,
                "iss_motifs": iss_n,
                "ese_motifs": ese_n,
                "tdp43_ug_dinucs": ug_tracts,
                "wt_bystander_sponge_flag": wt_sponge_flag,
                "mean_avi_phred": round(mean_avi, 2),
                "max_avi_phred": round(max_avi, 2),
                "boundary_dist_bp": boundary_dist,
                "composite_score": round(score, 2),
            })
    hits.sort(key=lambda r: r["composite_score"], reverse=True)
    return hits
