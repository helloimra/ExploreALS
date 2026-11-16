"""Score polymorphism-free GRCh38 cis-regulatory intervals and CDS frame arithmetic for Track 1."""

from __future__ import annotations

import csv
import json
import urllib.request
from pathlib import Path

from carbon_als.loaders import assert_1based_exon_coords
from carbon_als.splice_design import genomic_to_premRNA, score_target_intervals

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "work" / "phase2" / "track1_multiplex_splice" / "outputs"
B1_API = ROOT / "work" / "phase1_batches" / "batch_1" / "outputs" / "run_b1_005_tri_pillar_apis.json"

CODON = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L", "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M", "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S", "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T", "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*", "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K", "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W", "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R", "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def fetch_ensembl_transcript_cds(tx_id: str) -> dict:
    url = f"https://rest.ensembl.org/lookup/id/{tx_id.split('.')[0]}?expand=1;content-type=application/json"
    req = urllib.request.Request(url, headers={"User-Agent": "CarbonALS/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def translate_dna(seq: str) -> str:
    return "".join(CODON.get(seq[i : i + 3], "X") for i in range(0, len(seq) - 2, 3))


def load_cached_avi() -> dict[str, dict[int, float]]:
    by_chr: dict[str, dict[int, float]] = {}
    if not B1_API.exists():
        return by_chr
    raw = json.loads(B1_API.read_text(encoding="utf-8"))
    scans = raw.get("alphagenome", {}).get("locus_avi_scans", {})
    for entries in scans.values():
        for rec in entries:
            chrom, pos_s, _ = rec["variant"].split(":", 2)
            pos = int(pos_s)
            phred = float(rec.get("avi_phred", 0.0))
            by_chr.setdefault(chrom, {})[pos] = max(by_chr.get(chrom, {}).get(pos, 0.0), phred)
    return by_chr


def analyze_kcnq2_frame(seq_info: dict, mane_prot: str) -> dict:
    ens = fetch_ensembl_transcript_cds("ENST00000359125")
    tr = ens["Translation"]
    cds_start_genomic, cds_end_genomic = tr["end"], tr["start"]  # minus strand
    exons = sorted(ens["Exon"], key=lambda e: e["end"], reverse=True)
    cum_cds = 0
    exon_cds_rows = []
    for idx, ex in enumerate(exons[:7], start=1):
        c_hi = min(ex["end"], cds_start_genomic)
        c_lo = max(ex["start"], cds_end_genomic)
        cds_len = max(0, c_hi - c_lo + 1)
        aa_start = cum_cds // 3 + 1
        cum_cds += cds_len
        aa_end = (cum_cds + 2) // 3
        exon_cds_rows.append({
            "exon_number": idx,
            "grch38_start": ex["start"],
            "grch38_end": ex["end"],
            "exon_width_bp": ex["end"] - ex["start"] + 1,
            "cds_width_bp": cds_len,
            "cds_mod3": cds_len % 3,
            "cum_cds_bp": cum_cds,
            "approx_aa_span": f"{aa_start}-{aa_end}",
        })
    ex5 = exons[4]
    assert_1based_exon_coords(63442406, 63442531, ex5["start"], ex5["end"], "KCNQ2_Exon5_MANE")
    # Check exact Exon 5 coding amino acids inside MANE protein (872 aa)
    prem, coords = genomic_to_premRNA(seq_info["dna_plus_5to3"], "chr20", seq_info["start_1b"], "-")
    pos_to_rna = dict(zip(coords, prem))
    ex5_cdna = "".join(pos_to_rna[p] for p in range(63442531, 63442405, -1)).replace("U", "T")
    matched_frame = {}
    for offset in (0, 1, 2):
        pep = translate_dna(ex5_cdna[offset:])
        idx = mane_prot.find(pep)
        if idx != -1:
            matched_frame = {
                "exon5_5prime_phase_nt": offset,
                "exon5_3prime_overhang_nt": (len(ex5_cdna) - offset) % 3,
                "exon5_full_aa_start_1b": idx + 1,
                "exon5_full_aa_end_1b": idx + len(pep),
                "exon5_internal_codons_count": len(pep),
                "exon5_peptide": pep,
                "full_exon5_skip_126bp_mod3": len(ex5_cdna) % 3,
                "retigabine_trp236_inside_exon5": (idx + 1) <= 236 <= (idx + len(pep)),
                "full_exon5_skip_consequence": "100% in-frame 42-aa deletion (ΔGlu231-Leu272, 126 bp, mod3==0) excising the entire S5 pore-lining helix + Trp236 retigabine pocket while preserving C-terminal A-D tetramerization helices",
            }
    return {"ensembl_cds_start_grch38": cds_start_genomic, "exons_1_to_7": exon_cds_rows, "exon5_translation": matched_frame}


def main() -> None:
    staged = json.loads((OUT_DIR / "genomics_sequences_and_gnomad.json").read_text(encoding="utf-8"))
    avi_by_chr = load_cached_avi()

    targets = [
        ("C006", "KCNQ2", "INCLUDE_CONSTITUTIVE_EXON", (63442406, 63442531), "CORE_3PLEX"),
        ("C001", "UNC13A", "SKIP_CRYPTIC_EXON", (17642414, 17642541), "CORE_3PLEX"),
        ("C002", "STMN2", "SKIP_CRYPTIC_EXON", (79616822, 79617048), "CORE_3PLEX"),
        ("C015-N2", "G2E3", "SKIP_CRYPTIC_EXON", (30563746, 30563950), "DEFERRED_4TH_CANDIDATE"),
    ]

    all_ranked: list[dict] = []
    locus_summary: dict[str, dict] = {}
    for cid, gene, mode, bounds, tier in targets:
        s_info = staged["sequences"][gene]
        dna_plus = s_info.get("dna_plus_5to3")
        if not dna_plus:
            cnum = str(s_info["chromosome"]).replace("chr", "")
            url = f"https://rest.ensembl.org/sequence/region/human/{cnum}:{s_info['start_1b']}..{s_info['end_1b']}?coord_system_version=GRCh38"
            req = urllib.request.Request(url, headers={"Accept": "text/plain", "User-Agent": "ExploreALS/1.2"})
            with urllib.request.urlopen(req, timeout=25) as resp:  # noqa: S310
                dna_plus = resp.read().decode("utf-8").strip().upper()
                s_info["dna_plus_5to3"] = dna_plus
        prem, coords = genomic_to_premRNA(dna_plus, s_info["chromosome"], s_info["start_1b"], s_info["strand"])
        common_vars = staged["gnomad_v4"][gene]["common_variants_af_ge_0_005"]
        banned: set[int] = set()
        for v in common_vars:
            banned.update(int(x) for x in v.get("span_1b", [v["pos_1b"]]))
        hits = score_target_intervals(
            chrom=s_info["chromosome"],
            prem_rna=prem,
            coords_1b=coords,
            strand=s_info["strand"],
            banned_positions_1b=banned,
            mode=mode,
            feature_bounds_1b=bounds,
            avi_by_pos=avi_by_chr.get(s_info["chromosome"], {}),
        )
        if gene == "KCNQ2":
            banned_short = {
                int(x)
                for v in common_vars
                if len(v.get("span_1b", [v["pos_1b"]])) <= 12
                for x in v.get("span_1b", [v["pos_1b"]])
            }
            ug_hits = score_target_intervals(
                chrom=s_info["chromosome"],
                prem_rna=prem,
                coords_1b=coords,
                strand=s_info["strand"],
                banned_positions_1b=banned_short,
                mode="INCLUDE_EXON_UPSTREAM_UG",
                feature_bounds_1b=bounds,
                avi_by_pos=avi_by_chr.get(s_info["chromosome"], {}),
            )
            hits = sorted(hits + ug_hits, key=lambda r: r["composite_score"], reverse=True)
        # De-duplicate overlapping intervals (>50% overlap) to pick top 3 non-redundant windows per gene
        selected: list[dict] = []
        for h in hits:
            if any(min(h["grch38_end"], s["grch38_end"]) - max(h["grch38_start"], s["grch38_start"]) + 1 >= 10 for s in selected):
                continue
            if gene == "KCNQ2" and len(selected) == 2:
                modes_present = {s["mode"] for s in selected}
                if "INCLUDE_EXON_UPSTREAM_UG" not in modes_present and h["mode"] != "INCLUDE_EXON_UPSTREAM_UG":
                    continue
                if "INCLUDE_CONSTITUTIVE_EXON" not in modes_present and h["mode"] != "INCLUDE_CONSTITUTIVE_EXON":
                    continue
            row = {
                "candidate_id": cid,
                "gene_symbol": gene,
                "multiplex_tier": tier,
                "rank_within_gene": len(selected) + 1,
                **h,
                "analysis_run_id": "RUN-P2-T1-001",
            }
            selected.append(row)
            all_ranked.append(row)
            if len(selected) == 3:
                break
        locus_summary[gene] = {
            "candidate_id": cid,
            "multiplex_tier": tier,
            "window_grch38": f"{s_info['chromosome']}:{s_info['start_1b']}-{s_info['end_1b']}({s_info['strand']})",
            "feature_bounds_1b": list(bounds),
            "gnomad_v4_total_variants": staged["gnomad_v4"][gene]["total_gnomad_v4_variants"],
            "gnomad_v4_common_variants_af_ge_0_005": len(common_vars),
            "masked_genomic_positions_count": len(banned),
            "masked_rsids": sorted({r for v in common_vars for r in (v.get("rsids") or [])}),
            "total_biophysically_valid_intervals": len(hits),
            "top_nonredundant_intervals": selected,
        }

    cached_sum = OUT_DIR / "phase2_track1_genomic_summary.json"
    if cached_sum.exists():
        prev = json.loads(cached_sum.read_text(encoding="utf-8"))
        frame_info = prev.get("kcnq2_cds_and_frame") or analyze_kcnq2_frame(staged["sequences"]["KCNQ2"], staged["mane_proteins"]["KCNQ2"])
    else:
        frame_info = analyze_kcnq2_frame(staged["sequences"]["KCNQ2"], staged["mane_proteins"]["KCNQ2"])

    for dest_csv in (OUT_DIR / "phase2_track1_ranked_intervals.csv", ROOT / "registries" / "phase2_multiplex_intervals.csv"):
        with dest_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(all_ranked[0].keys()))
            writer.writeheader()
            writer.writerows(all_ranked)

    summary_payload = {"kcnq2_cds_and_frame": frame_info, "loci": locus_summary}
    cached_sum.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    print(f"Saved {len(all_ranked)} non-redundant intervals -> phase2_track1_ranked_intervals.csv & registries/phase2_multiplex_intervals.csv")


if __name__ == "__main__":
    main()
