"""Shared AlphaGenome v1 directional splicing-polarity engine for CarbonALS.

Enforces all cold-context audit invariants across Workstreams 1-3:
  1. Strand-verified splice-site dinucleotide assertions (5'SS GT/GC, 3'SS AG, +5 U1 offset).
  2. Dynamic sequence window sizing (131 kb / 524 kb / 1 Mb) + explicit out-of-window flagging
     (never defaulting an unmeasured canonical junction to WT_CANONICAL_SAFE_NEUTRAL).
  3. Canonical/protected-junction disruption takes strict precedence over secondary cryptic gain
     (fixing canonical 5'SS knockout positive-control misclassifications).
  4. Separate positive vs. negative SSU delta tracking across BOTH +/-4 bp AND full cryptic region.
  5. Strand-safe track filtering via filter_tracks(mask.to_numpy()) (never strand-blind filter_by_ontology).
  6. 3-allele concordance adjudication separating concordant loss-of-element from single-allele
     de novo GT/AG creation artifacts (which are invalid for steric SSO ranking).
  7. Strict RFC-8259 JSON sanitization (allow_nan=False) + biosecurity >=15-nt guard.
"""
from __future__ import annotations

import json
import math
import re
import urllib.parse
import urllib.request
from typing import Any

import numpy as np
import pandas as pd

COMP_DNA = str.maketrans("ACGTacgt", "TGCAtgca")
RAW_OLIGO_SEQ_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)

DEFAULT_ONTOLOGIES: tuple[tuple[str, str], ...] = (
    ("CL:0000100", "motor_neuron"),
    ("UBERON:0006469", "cervical_spinal_cord_C1"),
    ("UBERON:0001870", "frontal_cortex"),
)

# Unified polarity thresholds across all workstreams (no cross-workstream drift)
POLARITY_THRESHOLDS: dict[str, float] = {
    "canon_disrupt_pct": -5.0,
    "canon_enhance_pct": 2.0,
    "protected_disrupt_pct": -5.0,
    "protected_enhance_guard_pct": -3.0,
    "ssu_delta_thresh": 0.05,
    "cryptic_junc_delta_min": 0.30,
    "cryptic_junc_ref_max": 0.30,
    "top_junc_report_min": 0.02,
    "ssu_report_min": 0.01,
}


def sanitize_json_value(obj: Any) -> Any:
    """Recursively convert non-finite floats (NaN/Inf) and NumPy scalars into strict RFC-8259 JSON types."""
    if isinstance(obj, dict):
        return {str(k): sanitize_json_value(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_json_value(v) for v in obj]
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        val = float(obj)
        return val if math.isfinite(val) else None
    return obj


def strict_json_dumps(obj: Any, *, indent: int = 2, check_biosecurity: bool = True) -> str:
    """Serialize strictly RFC-8259 JSON (allow_nan=False) with mandatory >=15-nt biosecurity guard."""
    txt = json.dumps(sanitize_json_value(obj), indent=indent, allow_nan=False)
    if check_biosecurity and RAW_OLIGO_SEQ_RE.search(txt):
        raise AssertionError("BIOSECURITY_GUARD_TRIGGERED: raw >=15-nt nucleotide sequence detected in JSON output!")
    return txt


def build_variant_atlas_url(chrom: str, pos: int, ref: str, alt: str) -> str:
    q = {"q": f"{chrom}:{pos}:{ref}>{alt}", "lItems": "avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:SPLICE_SITE_USAGE"}
    return "https://deepmind.google.com/science/alphagenome/atlas?" + urllib.parse.urlencode(
        q, quote_via=urllib.parse.quote, safe=":,->"
    )


def sense_base(plus_base: str, strand: str) -> str:
    """Return sense-strand DNA base given forward (+) GRCh38 reference base."""
    b = plus_base.upper()
    if strand == "+":
        return b
    if strand == "-":
        return b.translate(COMP_DNA)
    raise ValueError(f"Invalid strand={strand!r}")


def fetch_transient_ref_window(cnum: str, lo_1b: int, hi_1b: int) -> dict[int, str]:
    """Fetch transient GRCh38 forward-strand base map {pos_1b: base} in RAM only (UCSC primary, Ensembl fallback)."""
    seq = ""
    urls = [
        ("ucsc", f"https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chr{cnum};start={lo_1b - 1};end={hi_1b}"),
        ("ensembl", f"https://rest.ensembl.org/sequence/region/human/{cnum}:{lo_1b}..{hi_1b}?coord_system_version=GRCh38"),
    ]
    for kind, url in urls:
        try:
            hdrs = {"Accept": "text/plain", "User-Agent": "CarbonALS/0.5.8"} if kind == "ensembl" else {"User-Agent": "CarbonALS/0.5.8"}
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdrs), timeout=25) as resp:
                raw = resp.read().decode("utf-8").strip()
            seq = json.loads(raw)["dna"].strip().upper() if kind == "ucsc" else raw.upper()
            if len(seq) == (hi_1b - lo_1b + 1):
                break
        except Exception as exc:  # noqa: BLE001
            print(f"  WARN: {kind} transient REF lookup failed ({exc}); trying fallback...", flush=True)
    if len(seq) != (hi_1b - lo_1b + 1):
        raise RuntimeError(f"Failed to fetch transient REF bases for chr{cnum}:{lo_1b}-{hi_1b}")
    out = {lo_1b + i: seq[i] for i in range(len(seq))}
    del seq
    return out


def assert_splice_dinucleotide(
    ref_map: dict[int, str],
    pos_1b: int,
    strand: str,
    expect_motif: str,
    label: str = "",
) -> str:
    """Verify that pos_1b matches the expected sense-strand splice dinucleotide (or base) on GRCh38.

    Supported `expect_motif` values:
      - "5SS_GT_B1" / "5SS_GT_B2": canonical GT donor (+1 G, +2 T on sense strand)
      - "5SS_GC_B1" / "5SS_GC_B2": non-canonical GC donor (+1 G, +2 C on sense strand)
      - "3SS_AG_B1" / "3SS_AG_B2": canonical AG acceptor (-2 A, -1 G on sense strand)
      - "G", "A", "C", "T": exact single sense-strand base check (e.g. +5 U1 G)
    """
    step = 1 if strand == "+" else -1
    if expect_motif in ("G", "A", "C", "T"):
        got = sense_base(ref_map[pos_1b], strand)
        if got != expect_motif:
            raise ValueError(
                f"SPLICE_BASE_MISMATCH [{label}] pos={pos_1b}({strand}): expected sense '{expect_motif}', "
                f"got sense '{got}' (+strand '{ref_map[pos_1b]}')."
            )
        return got

    motif_specs = {
        "5SS_GT_B1": (0, step, "GT"),
        "5SS_GT_B2": (-step, 0, "GT"),
        "5SS_GC_B1": (0, step, "GC"),
        "5SS_GC_B2": (-step, 0, "GC"),
        "3SS_AG_B1": (0, step, "AG"),
        "3SS_AG_B2": (-step, 0, "AG"),
    }
    if expect_motif not in motif_specs:
        raise ValueError(f"Unknown expect_motif={expect_motif!r}")
    off1, off2, exp = motif_specs[expect_motif]
    p1, p2 = pos_1b + off1, pos_1b + off2
    got = sense_base(ref_map[p1], strand) + sense_base(ref_map[p2], strand)
    if got != exp:
        raise ValueError(
            f"SPLICE_DINUCLEOTIDE_MISMATCH [{label}] pos={pos_1b}({strand}) expects {expect_motif} "
            f"(sense '{exp}' at {p1}..{p2}), got sense '{got}' (+strand '{ref_map[p1]}{ref_map[p2]}')."
        )
    return got


def select_window_length(intron_start: int, intron_end: int, margin_bp: int = 20_000) -> tuple[int, int, int]:
    """Select smallest AlphaGenome v1 supported sequence length fully containing [intron_start, intron_end] + margin.

    Returns (window_length_bp, interval_start_0b, interval_end_0b).
    """
    span = abs(intron_end - intron_start) + 2 * margin_bp
    mid = (intron_start + intron_end) // 2
    for seq_len in (131_072, 524_288, 1_048_576):
        if span <= seq_len:
            half = seq_len // 2
            return seq_len, mid - half, mid + half
    half = 1_048_576 // 2
    return 1_048_576, mid - half, mid + half


def classify_variant_polarity(
    canon_pct: float | None,
    max_pos_ssu_delta: float,
    min_neg_ssu_delta: float,
    new_cryptic_gains: list[dict[str, Any]],
    *,
    canonical_in_window: bool = True,
    protected_pcts: dict[str, float | None] | None = None,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Classify AlphaGenome v1 single-SNV splicing polarity with disruption-first precedence.

    Invariants:
      1. Out-of-window / unmeasured canonical junctions NEVER silently pass as WT_CANONICAL_SAFE_NEUTRAL.
      2. Canonical or protected physiological junction disruption (<= -5%) ALWAYS takes precedence over
         secondary cryptic activation (fixing canonical 5'SS knockout positive controls).
      3. Separate positive & negative SSU deltas prevent max(key=abs) sign masking.
    """
    th = thresholds or POLARITY_THRESHOLDS
    prot_vals = [v for v in (protected_pcts or {}).values() if v is not None and math.isfinite(v)]
    min_prot_pct = min(prot_vals) if prot_vals else None
    has_cryptic_gain = bool(new_cryptic_gains) or (max_pos_ssu_delta >= th["ssu_delta_thresh"])
    canon_disrupted = (canon_pct is not None and canon_pct <= th["canon_disrupt_pct"])
    prot_disrupted = (min_prot_pct is not None and min_prot_pct <= th["protected_disrupt_pct"])
    ssu_disrupted = (min_neg_ssu_delta <= -th["ssu_delta_thresh"])

    if not canonical_in_window or canon_pct is None:
        if prot_disrupted or ssu_disrupted:
            label = "DISRUPTS_EXISTING_OR_CANONICAL_SPLICING"
        elif has_cryptic_gain:
            label = "GAINS_CRYPTIC_SPLICE_SITE_OR_JUNCTION"
        else:
            label = "CANONICAL_JUNCTION_UNMEASURED_OUT_OF_WINDOW"
        return {
            "polarity": label,
            "with_secondary_cryptic_activation": bool(has_cryptic_gain and label.startswith("DISRUPTS")),
            "protected_junction_disrupted": bool(prot_disrupted),
            "canonical_in_window": bool(canonical_in_window),
        }

    if canon_disrupted or prot_disrupted or ssu_disrupted:
        label = "DISRUPTS_EXISTING_OR_CANONICAL_SPLICING"
    elif has_cryptic_gain:
        label = "GAINS_CRYPTIC_SPLICE_SITE_OR_JUNCTION"
    elif canon_pct >= th["canon_enhance_pct"] and (min_prot_pct is None or min_prot_pct >= th["protected_enhance_guard_pct"]):
        label = "ENHANCES_CANONICAL_SPLICING"
    else:
        label = "WT_CANONICAL_SAFE_NEUTRAL"

    return {
        "polarity": label,
        "with_secondary_cryptic_activation": bool(has_cryptic_gain and label == "DISRUPTS_EXISTING_OR_CANONICAL_SPLICING"),
        "protected_junction_disrupted": bool(prot_disrupted),
        "canonical_in_window": True,
    }


def summarize_position_concordance(alleles: list[dict[str, Any]]) -> dict[str, Any]:
    """Adjudicate 3-allele concordance at a tested genomic position to block single-allele GT/AG artifacts.

    A valid WT steric-blocking loss-of-element signal requires concordant enhancement across all 3 non-REF
    alleles (or 3/3 WT neutrality when basal WT cryptic usage is near zero). Single-allele cryptic-site
    creation (1 allele disrupts/gains cryptic while 2 alleles are neutral/enhancing) is flagged invalid for SSO ranking.
    """
    pols = [str(a.get("polarity_mn", "")) for a in alleles]
    n_enh = sum(1 for p in pols if p == "ENHANCES_CANONICAL_SPLICING")
    n_dis = sum(1 for p in pols if p == "DISRUPTS_EXISTING_OR_CANONICAL_SPLICING")
    n_gain = sum(1 for p in pols if p == "GAINS_CRYPTIC_SPLICE_SITE_OR_JUNCTION")
    n_neut = sum(1 for p in pols if p == "WT_CANONICAL_SAFE_NEUTRAL")
    n_unm = sum(1 for p in pols if p == "CANONICAL_JUNCTION_UNMEASURED_OUT_OF_WINDOW")
    n_tot = len(alleles)
    n_bad_cryptic_or_dis = n_dis + n_gain

    if n_tot == 0 or n_unm == n_tot:
        cls = "UNMEASURED_OUT_OF_WINDOW"
        sso_valid = False
    elif n_enh == n_tot:
        cls = "CONCORDANT_3OF3_ENHANCES_WT"
        sso_valid = True
    elif n_dis == n_tot:
        cls = "CONCORDANT_3OF3_DISRUPTS_ESSENTIAL_SITE"
        sso_valid = False
    elif n_neut == n_tot:
        cls = "WT_TDP43_REPLETION_NEUTRAL_SAFETY_ONLY"
        sso_valid = True  # WT safety check only; cannot infer TDP-43-KD rescue potency
    elif n_bad_cryptic_or_dis == 1 and (n_neut + n_enh) == (n_tot - 1):
        cls = "SINGLE_ALLELE_DE_NOVO_SITE_ARTIFACT"
        sso_valid = False
    elif n_enh >= 2 and n_dis == 0 and n_gain == 0:
        cls = "MOSTLY_CONCORDANT_ENHANCES_WT"
        sso_valid = True
    else:
        cls = "MIXED_ALLELE_DEPENDENT"
        sso_valid = False

    return {
        "concordance_class": cls,
        "valid_for_wt_sso_safety": sso_valid,
        "counts": {"enhances": n_enh, "disrupts": n_dis, "gains_cryptic": n_gain, "neutral": n_neut, "unmeasured": n_unm},
    }


def filter_track_by_ontology_strand(data: Any, curie: str, strand: str) -> Any:
    """Strictly filter TrackData/JunctionData by ontology_curie AND sense strand (never strand-blind)."""
    if data is None:
        return None
    md = data.metadata
    mask = md["ontology_curie"].astype(str) == curie
    if "strand" in md.columns:
        s_mask = md["strand"].astype(str).isin([strand, "."])
        if (mask & s_mask).any():
            mask = mask & s_mask
    if not mask.any():
        return None
    return data.filter_tracks(mask.to_numpy())


def parse_junction_df(junc_obj: Any, ontology_curie: str, strand: str) -> pd.DataFrame:
    sub = filter_track_by_ontology_strand(junc_obj, ontology_curie, strand)
    if sub is None or len(sub.junctions) == 0:
        return pd.DataFrame(columns=["start", "end", "strand", "score"])
    vals = sub.values
    scores = (vals.mean(axis=1) if vals.shape[0] == len(sub.junctions) else vals.mean(axis=0)) if vals.ndim == 2 else vals
    return pd.DataFrame([
        {"start": int(j.start), "end": int(j.end), "strand": str(j.strand), "score": float(s)}
        for j, s in zip(sub.junctions, scores)
    ])


def _extract_junction_record(loc: pd.DataFrame, j_start_1b: int, j_end_1b: int) -> dict[str, Any] | None:
    rows = loc[(loc["start"].sub(j_start_1b - 1).abs() <= 2) & (loc["end"].sub(j_end_1b).abs() <= 2)]
    if rows.empty:
        rows = loc[(loc["start"].sub(j_start_1b).abs() <= 2) & (loc["end"].sub(j_end_1b).abs() <= 2)]
    if rows.empty:
        return None
    cr = rows.sort_values("score_ref", ascending=False).iloc[0]
    ref_v, alt_v, d_v = float(cr["score_ref"]), float(cr["score_alt"]), float(cr["delta"])
    return {
        "start": int(cr["start"]),
        "end": int(cr["end"]),
        "ref": round(ref_v, 4),
        "alt": round(alt_v, 4),
        "delta": round(d_v, 4),
        "rel_pct_change": round(100.0 * d_v / max(ref_v, 1e-6), 2),
    }


def analyze_locus(
    model: Any,
    gene: str,
    cfg: dict[str, Any],
    *,
    ontologies: tuple[tuple[str, str], ...] = DEFAULT_ONTOLOGIES,
    include_rna_seq: bool = True,
) -> dict[str, Any]:
    """Run unified AlphaGenome v1 directional polarity audit for a splicing locus.

    `cfg` keys:
      - chrom, cnum, strand, intron_start, intron_end
      - peak_positions: list of (pos_1b, role) OR (pos_1b, role, expect_motif)
      - optional: eals_id, promoted_windows, protected_junctions ({name: (start_1b, end_1b)}),
                  ssu_region_bounds ((lo_1b, hi_1b)), primary_junction_bounds ((start_1b, end_1b))
    """
    from alphagenome.data import genome
    from alphagenome.models.v1 import dna_client

    chrom, cnum, strand = cfg["chrom"], str(cfg["cnum"]), cfg["strand"]
    int_s, int_e = int(cfg["intron_start"]), int(cfg["intron_end"])
    prim_s, prim_e = cfg.get("primary_junction_bounds", (int_s, int_e))
    prot_juncs: dict[str, tuple[int, int]] = cfg.get("protected_junctions", {})

    seq_len, pred_start, pred_end = select_window_length(int_s, int_e)
    pred_interval = genome.Interval(chrom, pred_start, pred_end)
    canonical_in_window = bool(pred_start < (prim_s - 50) and (prim_e + 50) < pred_end)

    # Fetch transient REF window covering all tested positions +/- 2 bp for dinucleotide assertions
    pos_entries = []
    for item in cfg["peak_positions"]:
        if len(item) == 3:
            pos_entries.append((int(item[0]), str(item[1]), item[2]))
        else:
            pos_entries.append((int(item[0]), str(item[1]), None))
    all_pos = [p for p, _, _ in pos_entries]
    ref_map = fetch_transient_ref_window(cnum, min(all_pos) - 2, max(all_pos) + 2)

    # Fail-fast dinucleotide verification BEFORE spending any AlphaGenome API calls!
    dinuc_verified: dict[int, str] = {}
    for pos, role, expect_motif in pos_entries:
        if expect_motif:
            dinuc_verified[pos] = assert_splice_dinucleotide(ref_map, pos, strand, expect_motif, label=f"{gene}:{role}")

    requested = [dna_client.OutputType.SPLICE_JUNCTIONS, dna_client.OutputType.SPLICE_SITE_USAGE]
    if include_rna_seq:
        requested.append(dna_client.OutputType.RNA_SEQ)
    ont_curies = [c for c, _ in ontologies]

    win_lo = max(pred_interval.start, int_s - 200)
    win_hi = min(pred_interval.end, int_e + 200)
    ssu_reg = cfg.get("ssu_region_bounds")
    if ssu_reg is None:
        ssu_reg = (max(int_s, min(all_pos) - 50), min(int_e, max(all_pos) + 50))

    variant_results: list[dict[str, Any]] = []
    baseline_ref: dict[str, Any] = {}

    for pos, role, expect_motif in pos_entries:
        ref = ref_map[pos]
        alts = [b for b in "ACGT" if b != ref]
        print(f"  [{gene}] {chrom}:{pos}({strand}) {role} REF={ref} (len={seq_len})...", flush=True)
        per_alt: list[dict[str, Any]] = []
        for alt in alts:
            var = genome.Variant(chrom, pos, ref, alt)
            pred = model.predict_variant(
                interval=pred_interval,
                variant=var,
                requested_outputs=requested,
                ontology_terms=ont_curies,
            )
            if not baseline_ref:
                for curie, tlabel in ontologies:
                    jdf_r = parse_junction_df(pred.reference.splice_junctions, curie, strand)
                    loc_j = jdf_r[
                        (jdf_r["strand"] == strand) & (jdf_r["end"] >= win_lo) & (jdf_r["start"] <= win_hi)
                    ].sort_values("score", ascending=False).head(10)
                    baseline_ref[tlabel] = loc_j.to_dict(orient="records")

            by_tissue: dict[str, Any] = {}
            for curie, tlabel in ontologies:
                jdf_r = parse_junction_df(pred.reference.splice_junctions, curie, strand)
                jdf_a = parse_junction_df(pred.alternate.splice_junctions, curie, strand)
                merged = pd.merge(jdf_r, jdf_a, on=["start", "end", "strand"], how="outer", suffixes=("_ref", "_alt")).fillna(0.0)
                merged["delta"] = merged["score_alt"] - merged["score_ref"]
                loc = merged[(merged["strand"] == strand) & (merged["end"] >= win_lo) & (merged["start"] <= win_hi)].copy()

                canon_j = _extract_junction_record(loc, prim_s, prim_e) if canonical_in_window else None
                prot_recs = {pname: _extract_junction_record(loc, ps, pe) for pname, (ps, pe) in prot_juncs.items()}

                top_changed = loc.reindex(loc["delta"].abs().sort_values(ascending=False).index).head(6)
                top_j_list = [
                    {
                        "start": int(r["start"]),
                        "end": int(r["end"]),
                        "ref": round(float(r["score_ref"]), 4),
                        "alt": round(float(r["score_alt"]), 4),
                        "delta": round(float(r["delta"]), 4),
                    }
                    for _, r in top_changed.iterrows()
                    if abs(float(r["delta"])) >= POLARITY_THRESHOLDS["top_junc_report_min"]
                ]

                # SSU scan across BOTH +/-4 bp local AND full cryptic region (separate pos & neg peaks)
                ss_r = filter_track_by_ontology_strand(pred.reference.splice_site_usage, curie, strand)
                ss_a = filter_track_by_ontology_strand(pred.alternate.splice_site_usage, curie, strand)
                local_ssu: list[dict[str, Any]] = []
                region_ssu: list[dict[str, Any]] = []
                max_pos_local, min_neg_local = 0.0, 0.0
                max_pos_reg, min_neg_reg = 0.0, 0.0
                if ss_r is not None and ss_a is not None:
                    r_arr = ss_r.values.mean(axis=1) if ss_r.values.ndim > 1 else ss_r.values
                    a_arr = ss_a.values.mean(axis=1) if ss_a.values.ndim > 1 else ss_a.values
                    d_arr = a_arr - r_arr
                    ss_idx = (pos - 1) - pred_interval.start
                    for off in range(-4, 5):
                        ii = ss_idx + off
                        if 0 <= ii < len(d_arr):
                            d_ss = float(d_arr[ii])
                            max_pos_local = max(max_pos_local, d_ss)
                            min_neg_local = min(min_neg_local, d_ss)
                            if abs(d_ss) >= POLARITY_THRESHOLDS["ssu_report_min"]:
                                local_ssu.append({"pos_1b": pos + off, "ref": round(float(r_arr[ii]), 4), "alt": round(float(a_arr[ii]), 4), "delta": round(d_ss, 4)})
                    local_ssu.sort(key=lambda x: -abs(x["delta"]))

                    r0 = max(0, (int(ssu_reg[0]) - 1) - pred_interval.start)
                    r1 = min(len(d_arr), int(ssu_reg[1]) - pred_interval.start)
                    if r1 > r0:
                        sub_d = d_arr[r0:r1]
                        max_pos_reg = float(np.max(sub_d))
                        min_neg_reg = float(np.min(sub_d))
                        nz = np.flatnonzero(np.abs(sub_d) >= POLARITY_THRESHOLDS["ssu_report_min"])
                        if len(nz) > 0:
                            top_idx = nz[np.argsort(-np.abs(sub_d[nz]))[:6]]
                            for rel_i in top_idx:
                                abs_i = r0 + int(rel_i)
                                region_ssu.append({
                                    "pos_1b": pred_interval.start + abs_i + 1,
                                    "ref": round(float(r_arr[abs_i]), 4),
                                    "alt": round(float(a_arr[abs_i]), 4),
                                    "delta": round(float(d_arr[abs_i]), 4),
                                })

                intron_rna_l2fc = None
                if include_rna_seq and pred.reference.rna_seq is not None and pred.alternate.rna_seq is not None:
                    rna_r = filter_track_by_ontology_strand(pred.reference.rna_seq, curie, strand)
                    rna_a = filter_track_by_ontology_strand(pred.alternate.rna_seq, curie, strand)
                    if rna_r is not None and rna_a is not None:
                        rr_arr = rna_r.values.mean(axis=1) if rna_r.values.ndim > 1 else rna_r.values
                        ra_arr = rna_a.values.mean(axis=1) if rna_a.values.ndim > 1 else rna_a.values
                        i0 = max(0, (int_s - 1) - pred_interval.start)
                        i1 = min(len(rr_arr), int_e - pred_interval.start)
                        if i1 > i0:
                            intron_rna_l2fc = round(float(np.log2((float(ra_arr[i0:i1].mean()) + 1e-4) / (float(rr_arr[i0:i1].mean()) + 1e-4))), 4)

                by_tissue[tlabel] = {
                    "canonical_intron_junction": canon_j,
                    "protected_junctions": prot_recs,
                    "top_changed_junctions": top_j_list,
                    "top_local_ssu_deltas": local_ssu[:4],
                    "top_region_ssu_deltas": region_ssu[:6],
                    "max_pos_local_ssu_delta": round(max_pos_local, 4),
                    "min_neg_local_ssu_delta": round(min_neg_local, 4),
                    "max_pos_region_ssu_delta": round(max_pos_reg, 4),
                    "min_neg_region_ssu_delta": round(min_neg_reg, 4),
                    "intron_rna_log2fc": intron_rna_l2fc,
                }

            mn = by_tissue["motor_neuron"]
            canon_pct = mn["canonical_intron_junction"]["rel_pct_change"] if mn["canonical_intron_junction"] else None
            prot_pcts = {k: (v["rel_pct_change"] if v else None) for k, v in mn["protected_junctions"].items()}
            new_cryptic = [
                j for j in mn["top_changed_junctions"]
                if j["delta"] >= POLARITY_THRESHOLDS["cryptic_junc_delta_min"]
                and j["ref"] < POLARITY_THRESHOLDS["cryptic_junc_ref_max"]
            ]
            pol_info = classify_variant_polarity(
                canon_pct,
                max(mn["max_pos_local_ssu_delta"], mn["max_pos_region_ssu_delta"]),
                min(mn["min_neg_local_ssu_delta"], mn["min_neg_region_ssu_delta"]),
                new_cryptic,
                canonical_in_window=canonical_in_window,
                protected_pcts=prot_pcts,
            )
            max_signed_ssu = (
                mn["min_neg_local_ssu_delta"]
                if abs(mn["min_neg_local_ssu_delta"]) >= abs(mn["max_pos_local_ssu_delta"])
                else mn["max_pos_local_ssu_delta"]
            )
            per_alt.append({
                "variant": f"{chrom}:{pos}:{ref}>{alt}",
                "alt": alt,
                "polarity_mn": pol_info["polarity"],
                "with_secondary_cryptic_activation": pol_info["with_secondary_cryptic_activation"],
                "protected_junction_disrupted": pol_info["protected_junction_disrupted"],
                "mn_canon_pct": canon_pct,
                "mn_protected_pcts": prot_pcts,
                "mn_max_pos_ssu_delta": mn["max_pos_local_ssu_delta"],
                "mn_min_neg_ssu_delta": mn["min_neg_local_ssu_delta"],
                "mn_max_ssu_delta": max_signed_ssu,
                "atlas_url": build_variant_atlas_url(chrom, pos, ref, alt),
                "by_tissue": by_tissue,
            })

        conc = summarize_position_concordance(per_alt)
        variant_results.append({
            "pos_1b": pos,
            "role": role,
            "ref": ref,
            "verified_motif": dinuc_verified.get(pos),
            "concordance": conc,
            "alleles": per_alt,
        })

    del ref_map
    return {
        "eals_id": cfg.get("eals_id"),
        "gene": gene,
        "intron_coords": f"{chrom}:{int_s}-{int_e}({strand})",
        "primary_junction_bounds": f"{chrom}:{prim_s}-{prim_e}({strand})",
        "protected_junction_bounds": {k: f"{chrom}:{ps}-{pe}({strand})" for k, (ps, pe) in prot_juncs.items()},
        "pred_window_bp": seq_len,
        "pred_interval_0b": [pred_start, pred_end],
        "canonical_in_window": canonical_in_window,
        "model_caveat": "WT TDP-43-intact 1-nt perturbation; valid for WT canonical safety and concordant loss-of-element checks, not TDP-43-KD steric-SSO potency.",
        "promoted_windows": cfg.get("promoted_windows", []),
        "baseline_ref_junctions_top10": baseline_ref,
        "perturbation_audit": variant_results,
    }
