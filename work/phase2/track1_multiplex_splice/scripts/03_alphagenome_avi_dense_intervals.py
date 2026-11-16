"""RUN-P2-T1-003: Dense AlphaGenome AVI saturation scans + full-locus re-ranking across Track 1 GRCh38 intervals."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from carbon_als.loaders import resolve_col  # noqa: E402
from carbon_als.skill_cli import run_skill_cli_raw_output, run_skill_cli_stdout_text  # noqa: E402
from carbon_als.splice_design import genomic_to_premRNA, score_target_intervals  # noqa: E402

import os
import urllib.request

AVI_CLI = Path(os.environ.get("ALPHAGENOME_AVI_CLI", ""))
LINKS_CLI = Path(os.environ.get("ALPHAGENOME_LINKS_CLI", ""))
OUT_DIR = ROOT / "work" / "phase2" / "track1_multiplex_splice" / "outputs"


def _ensure_dna_plus(s_info: dict) -> str:
    if s_info.get("dna_plus_5to3"):
        return str(s_info["dna_plus_5to3"])
    chrom_num = str(s_info["chromosome"]).replace("chr", "")
    url = f"https://rest.ensembl.org/sequence/region/human/{chrom_num}:{s_info['start_1b']}..{s_info['end_1b']}?coord_system_version=GRCh38"
    req = urllib.request.Request(url, headers={"Accept": "text/plain", "User-Agent": "ExploreALS/1.2"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8").strip().upper()

LOCUS_WINDOWS = {
    "KCNQ2": "chr20:63442050-63442900",
    "UNC13A": "chr19:17642375-17642580",
    "STMN2": "chr8:79616785-79617085",
    "G2E3": "chr14:30563710-30563986",
}

TARGETS = [
    ("C006", "KCNQ2", "INCLUDE_CONSTITUTIVE_EXON", (63442406, 63442531), "CORE_3PLEX"),
    ("C001", "UNC13A", "SKIP_CRYPTIC_EXON", (17642414, 17642541), "CORE_3PLEX"),
    ("C002", "STMN2", "SKIP_CRYPTIC_EXON", (79616822, 79617048), "CORE_3PLEX"),
    ("C015-N2", "G2E3", "SKIP_CRYPTIC_EXON", (30563746, 30563950), "DEFERRED_4TH_CANDIDATE"),
]


def load_or_scan_dense_avi(gene: str, region_1b: str) -> pd.DataFrame:
    tsv_out = OUT_DIR / f"avi_dense_{gene.lower()}.tsv"
    _, span = region_1b.split(":")
    req_s, req_e = [int(x) for x in span.split("-")]
    need_rescan = True
    if tsv_out.is_file() and tsv_out.stat().st_size > 500:
        df_try = pd.read_csv(tsv_out, sep="\t")
        p_col = resolve_col(df_try, "position")
        p_num = pd.to_numeric(df_try[p_col], errors="coerce").dropna()
        if not p_num.empty and int(p_num.min()) <= req_s and int(p_num.max()) >= req_e:
            need_rescan = False
            return df_try
    run_skill_cli_raw_output(
        AVI_CLI, ["region", "--region", region_1b, "--min_phred", "0.0", "--top_k", "10"],
        tsv_out, timeout_sec=180, use_cache=not need_rescan,
    )
    return pd.read_csv(tsv_out, sep="\t")


def cached_atlas_url(mode_arg: str, target: str) -> str:
    key = hashlib.sha1(f"{mode_arg}:{target}".encode("utf-8")).hexdigest()[:12]
    cache_fp = OUT_DIR / "atlas_links_cache" / f"{mode_arg}_{key}.txt"
    if cache_fp.is_file():
        txt = cache_fp.read_text(encoding="utf-8")
    elif LINKS_CLI.is_file():
        txt = run_skill_cli_stdout_text(LINKS_CLI, [mode_arg, target, "--modalities", "RNA_SEQ,DNASE"], cache_fp, use_cache=True)
    else:
        txt = ""
    for ln in txt.splitlines():
        if "https://deepmind.google.com/science/alphagenome/atlas" in ln:
            return ln[ln.index("https://deepmind.google.com/science/alphagenome/atlas") :].strip().rstrip(")")
    return f"https://deepmind.google.com/science/alphagenome/atlas?q={target}"


def main() -> None:
    staged = json.loads((OUT_DIR / "genomics_sequences_and_gnomad.json").read_text(encoding="utf-8"))
    tables: dict[str, pd.DataFrame] = {g: load_or_scan_dense_avi(g, r) for g, r in LOCUS_WINDOWS.items()}
    avi_pos_max_by_gene: dict[str, dict[int, float]] = {}
    for g, df in tables.items():
        pc, ac = resolve_col(df, "position"), resolve_col(df, "avi_phred")
        avi_pos_max_by_gene[g] = df.assign(_p=pd.to_numeric(df[pc]), _a=pd.to_numeric(df[ac])).groupby("_p")["_a"].max().to_dict()

    all_ranked: list[dict] = []
    for cid, gene, mode, bounds, tier in TARGETS:
        s_info = staged["sequences"][gene]
        prem, coords = genomic_to_premRNA(_ensure_dna_plus(s_info), s_info["chromosome"], s_info["start_1b"], s_info["strand"])
        common_vars = staged["gnomad_v4"][gene]["common_variants_af_ge_0_005"]
        banned = {int(x) for v in common_vars for x in v.get("span_1b", [v["pos_1b"]])}
        hits = score_target_intervals(
            s_info["chromosome"], prem, coords, s_info["strand"],
            banned_positions_1b=banned, mode=mode, feature_bounds_1b=bounds, avi_by_pos=avi_pos_max_by_gene[gene],
        )
        if gene == "KCNQ2":
            banned_short = {int(x) for v in common_vars if len(v.get("span_1b", [v["pos_1b"]])) <= 12 for x in v.get("span_1b", [v["pos_1b"]])}
            ug_hits = score_target_intervals(
                s_info["chromosome"], prem, coords, s_info["strand"],
                banned_positions_1b=banned_short, mode="INCLUDE_EXON_UPSTREAM_UG", feature_bounds_1b=bounds, avi_by_pos=avi_pos_max_by_gene[gene],
            )
            hits = sorted(hits + ug_hits, key=lambda r: r["composite_score"], reverse=True)
        selected: list[dict] = []
        for h in hits:
            if any(min(h["grch38_end"], s["grch38_end"]) - max(h["grch38_start"], s["grch38_start"]) + 1 >= 10 for s in selected):
                continue
            if gene == "KCNQ2" and len(selected) == 2:
                modes_p = {s["mode"] for s in selected}
                if ("INCLUDE_EXON_UPSTREAM_UG" not in modes_p and h["mode"] != "INCLUDE_EXON_UPSTREAM_UG") or (
                    "INCLUDE_CONSTITUTIVE_EXON" not in modes_p and h["mode"] != "INCLUDE_CONSTITUTIVE_EXON"
                ):
                    continue
            row = {"candidate_id": cid, "gene_symbol": gene, "multiplex_tier": tier, "rank_within_gene": len(selected) + 1, **h, "analysis_run_id": "RUN-P2-T1-003"}
            selected.append(row)
            all_ranked.append(row)
            if len(selected) == 3:
                break

    interval_reports, uniq_pos = [], set()
    for row in all_ranked:
        df = tables[row["gene_symbol"]]
        pc, vc, ac, mc = resolve_col(df, "position"), resolve_col(df, "variant"), resolve_col(df, "avi_phred"), resolve_col(df, "top_modality")
        s_1b, e_1b = int(row["grch38_start"]), int(row["grch38_end"])
        sub = df.loc[(pd.to_numeric(df[pc]) >= s_1b) & (pd.to_numeric(df[pc]) <= e_1b)].copy()
        sub[ac] = pd.to_numeric(sub[ac])
        assert int(sub[pc].nunique()) == e_1b - s_1b + 1
        uniq_pos.update((row["chrom"], int(p)) for p in range(s_1b, e_1b + 1))
        pos_max = sub.groupby(pc)[ac].max()
        pk = sub.sort_values(ac, ascending=False).iloc[0]
        mod_counts = sub.loc[sub.groupby(pc)[ac].idxmax(), mc].value_counts().to_dict()
        interval_reports.append({
            "candidate_id": row["candidate_id"], "gene_symbol": row["gene_symbol"], "rank_within_gene": row["rank_within_gene"],
            "interval_id": row["interval_id"], "mode": row["mode"], "length_bp": e_1b - s_1b + 1,
            "iss_motifs": row["iss_motifs"], "ese_motifs": row["ese_motifs"], "composite_score": row["composite_score"],
            "n_positions_scored": int(sub[pc].nunique()), "n_snvs_scored": int(len(sub)),
            "mean_pos_max_avi_phred": row["mean_avi_phred"], "mean_all_3snv_avi_phred": round(float(sub[ac].mean()), 2),
            "p90_pos_max_avi_phred": round(float(np.percentile(pos_max.to_numpy(), 90)), 2), "max_avi_phred": row["max_avi_phred"],
            "peak_variant": str(pk[vc]), "peak_top_modality": str(pk[mc]),
            "per_base_dominant_modalities": {str(k): int(v) for k, v in mod_counts.items()},
            "atlas_locus_url": cached_atlas_url("locus", f"{row['chrom']}:{s_1b}-{e_1b}"),
            "atlas_peak_variant_url": cached_atlas_url("variant", str(pk[vc])),
        })

    for dest in (OUT_DIR / "phase2_track1_ranked_intervals.csv", ROOT / "registries" / "phase2_multiplex_intervals.csv"):
        with dest.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(all_ranked[0].keys()))
            w.writeheader()
            w.writerows(all_ranked)

    payload = {
        "analysis_run_id": "RUN-P2-T1-003", "locus_windows_scanned_1based": LOCUS_WINDOWS,
        "total_locus_positions_scanned": int(sum(df[resolve_col(df, "position")].nunique() for df in tables.values())),
        "total_locus_snvs_scanned": int(sum(len(df) for df in tables.values())),
        "summed_12_interval_positions": int(sum(r["length_bp"] for r in interval_reports)),
        "summed_12_interval_snvs": int(sum(r["n_snvs_scored"] for r in interval_reports)),
        "unique_deduplicated_interval_positions": len(uniq_pos),
        "unique_deduplicated_interval_snvs": 3 * len(uniq_pos),
        "mean_avi_column_definition": "mean_pos_max_avi_phred (per-position maximum across 3 alt SNVs, averaged across the interval)",
        "intervals_dense_avi": interval_reports,
    }
    (OUT_DIR / "run_p2_t1_003_alphagenome_dense_avi.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("SAVED run_p2_t1_003_alphagenome_dense_avi.json & synchronized composite_score + RUN-P2-T1-003 across 12/12 intervals.")


if __name__ == "__main__":
    main()
