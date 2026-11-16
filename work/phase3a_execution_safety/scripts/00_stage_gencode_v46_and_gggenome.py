"""Stage GENCODE v46 (FASTA + basic & comprehensive GTF), gnomAD v4.1, and coordinate-only GGGenome (ungapped + 1-bulge + 18-mer core)."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from carbon_als.splice_design import _revcomp_dna, genomic_to_premRNA  # noqa: E402

GENCODE_DIR = ROOT / "data" / "genomics_splicing" / "gencode_v46"
CACHE_DIR = ROOT / "work" / "phase3a_execution_safety" / "cache"
LIC_DIR = ROOT / ".licenses"
REG_DIR = ROOT / "registries"

STAGED_REFS = {
    "DS_GENCODE_V46_TX": (
        "gencode.v46.transcripts.fa.gz",
        "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.transcripts.fa.gz",
        "GENCODE_Release_46_GRCh38.p14",
        "EMBL-EBI Open Access / CC BY 4.0",
        "GENCODE v46 human comprehensive spliced reference transcriptome FASTA (252,835 transcripts)",
    ),
    "DS_GENCODE_V46_GTF": (
        "gencode.v46.basic.annotation.gtf.gz",
        "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.basic.annotation.gtf.gz",
        "GENCODE_Release_46_GRCh38.p14",
        "EMBL-EBI Open Access / CC BY 4.0",
        "GENCODE v46 human basic gene/transcript/exon GTF annotation on GRCh38",
    ),
    "DS_GENCODE_V46_COMP_GTF": (
        "gencode.v46.annotation.gtf.gz",
        "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.annotation.gtf.gz",
        "GENCODE_Release_46_GRCh38.p14",
        "EMBL-EBI Open Access / CC BY 4.0",
        "GENCODE v46 human comprehensive gene/transcript/exon/CDS GTF annotation on GRCh38 matching DS_GENCODE_V46_TX",
    ),
    "DS_GNOMAD_V41_CONSTRAINT": (
        "gnomad.v4.1.constraint_metrics.tsv",
        "https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/constraint/gnomad.v4.1.constraint_metrics.tsv",
        "gnomAD_v4.1_GRCh38",
        "Broad Institute gnomAD Open Data (CC0 / Public Release)",
        "gnomAD v4.1 human gene/transcript loss-of-function constraint table (pLI and LOEUF across MANE Select/canonical)",
    ),
}
PRIMARY_CHROMS = {f"chr{i}" for i in range(1, 23)} | {"chrX", "chrY", "chrM"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_if_missing(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 1_000_000:
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "CarbonALS/0.5-OpenScience"})
    with urllib.request.urlopen(req, timeout=300) as resp, tmp.open("wb") as out:
        while buf := resp.read(1 << 20):
            out.write(buf)
    tmp.replace(dest)


def extract_sense_dna(staged_seq: dict, gene: str, start_1b: int, end_1b: int, strand: str) -> str:
    s_info = staged_seq["sequences"][gene]
    dna_plus = s_info.get("dna_plus_5to3")
    if not dna_plus:
        cnum = str(s_info["chromosome"]).replace("chr", "")
        url = f"https://rest.ensembl.org/sequence/region/human/{cnum}:{s_info['start_1b']}..{s_info['end_1b']}:1?content-type=application/json"
        req = urllib.request.Request(url, headers={"User-Agent": "ExploreALS/1.2"})
        with urllib.request.urlopen(req, timeout=45) as resp:  # noqa: S310
            dna_plus = json.loads(resp.read().decode("utf-8"))["seq"].upper()
            s_info["dna_plus_5to3"] = dna_plus
    prem_rna, coords = genomic_to_premRNA(dna_plus, s_info["chromosome"], s_info["start_1b"], s_info["strand"])
    pos_to_base = dict(zip(coords, prem_rna, strict=True))
    span = range(start_1b, end_1b + 1) if strand == "+" else range(end_1b, start_1b - 1, -1)
    return "".join(pos_to_base[p] for p in span).replace("U", "T")


def query_gggenome_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "CarbonALS/0.5-OpenScience"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_ungapped_hits(results: list[dict[str, Any]], sense_dna: str) -> list[dict[str, int | str]]:
    out: list[dict[str, int | str]] = []
    for h in results:
        chrom, h_strand = str(h.get("name", "")), str(h.get("strand", "+"))
        if chrom not in PRIMARY_CHROMS:
            continue
        q_raw, s_raw = str(h["query"]).upper(), str(h["sbjct"]).upper()
        q_sense = q_raw if h_strand == "+" else _revcomp_dna(q_raw)
        s_sense = s_raw if h_strand == "+" else _revcomp_dna(s_raw)
        assert q_sense == sense_dna, f"Strand mismatch: {q_sense} != {sense_dna}"
        n_mis = sum(1 for qb, sb in zip(q_sense, s_sense, strict=True) if qb != sb)
        n_gu = sum(1 for qb, sb in zip(q_sense, s_sense, strict=True) if (qb == "C" and sb == "T") or (qb == "A" and sb == "G"))
        out.append({
            "chrom": chrom, "grch38_start": int(h["position"]), "grch38_end": int(h["position_end"]),
            "strand": h_strand, "total_mismatches": n_mis, "gu_wobble_pairs": n_gu, "destabilizing_mismatches": n_mis - n_gu,
        })
    return out


def main() -> None:
    LIC_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (LIC_DIR / "gencode_gggenome_LICENSE.txt").write_text(
        f"Updated {datetime.now(timezone.utc).isoformat()}\n"
        "GENCODE v46 (EMBL-EBI Open Access / CC BY 4.0): https://www.gencodegenes.org/pages/data_access.html\n"
        "gnomAD v4.1 (Broad Institute Open Data / CC0 Public Release): https://gnomad.broadinstitute.org/data\n"
        "DBCLS GGGenome hg38 index (CC BY 4.0): https://gggenome.dbcls.jp/en/help.html\n",
        encoding="utf-8",
    )
    manifest_fp = REG_DIR / "datasets_manifest.csv"
    with manifest_fp.open(encoding="utf-8", newline="") as fh:
        r_m = csv.DictReader(fh)
        m_fields, m_rows = list(r_m.fieldnames or []), list(r_m)
    new_by_id: dict[str, dict[str, str]] = {}
    for ds_id, (fname, url, acc, lic, desc) in STAGED_REFS.items():
        fp = GENCODE_DIR / fname
        download_if_missing(url, fp)
        new_by_id[ds_id] = {
            "dataset_id": ds_id, "domain": "genomics_splicing", "local_relpath": fp.relative_to(ROOT).as_posix(),
            "upstream_explore_relpath": "NONE_PHASE3A_PRIMARY", "accession_or_doi": acc, "license_or_access": lic,
            "size_bytes": str(fp.stat().st_size), "sha256": sha256_file(fp), "relevant_candidates": "C001;C002;C006;C015", "description": desc,
        }
    ex_ids = {r["dataset_id"] for r in m_rows}
    kept_m = [{**r, **new_by_id[r["dataset_id"]]} if r["dataset_id"] in new_by_id else r for r in m_rows]
    kept_m.extend(v for k, v in new_by_id.items() if k not in ex_ids)
    with manifest_fp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=m_fields)
        w.writeheader()
        w.writerows(kept_m)

    staged = json.loads((ROOT / "work" / "phase2" / "track1_multiplex_splice" / "outputs" / "genomics_sequences_and_gnomad.json").read_text(encoding="utf-8"))
    with (REG_DIR / "phase2_multiplex_intervals.csv").open(encoding="utf-8") as fh:
        intervals = list(csv.DictReader(fh))
    coord_cache_fp = CACHE_DIR / "gggenome_hg38_coords_only.json"
    coord_cache_gz = CACHE_DIR / "gggenome_hg38_coords_only.json.gz"
    if coord_cache_fp.is_file():
        coord_payload: dict[str, Any] = json.loads(coord_cache_fp.read_text(encoding="utf-8"))
    elif coord_cache_gz.is_file():
        import gzip
        coord_payload = json.loads(gzip.decompress(coord_cache_gz.read_bytes()).decode("utf-8"))
    else:
        coord_payload = {}

    for row in intervals:
        iv_id = row["interval_id"]
        cur = coord_payload.get(iv_id)
        if isinstance(cur, dict) and cur.get("schema_v") == 2:
            continue
        sense_dna = extract_sense_dna(staged, row["gene_symbol"], int(row["grch38_start"]), int(row["grch38_end"]), row["strand"])
        used_mm, raw_ungap = 2, {}
        for mm in (2, 1, 0):
            raw_ungap = query_gggenome_json(f"https://gggenome.dbcls.jp/hg38/{mm}/nogap/{sense_dna}.json")
            if raw_ungap.get("error") == "none":
                used_mm = mm
                break
        assert raw_ungap.get("error") == "none", f"GGGenome ungapped failed on {iv_id}"
        ungapped = parse_ungapped_hits(raw_ungap.get("results", []), sense_dna)

        bulge_hits: list[dict[str, int | str]] = []
        raw_gap = query_gggenome_json(f"https://gggenome.dbcls.jp/hg38/1/{sense_dna}.json") if used_mm == 2 else {"error": "alu_skip", "results": []}
        gap_queried = raw_gap.get("error") == "none"
        for h in raw_gap.get("results", []) if gap_queried else []:
            chrom, h_strand = str(h.get("name", "")), str(h.get("strand", "+"))
            q_raw, s_raw = str(h["query"]).upper(), str(h["sbjct"]).upper()
            if chrom in PRIMARY_CHROMS and ("-" in q_raw or "-" in s_raw):
                bulge_hits.append({
                    "chrom": chrom, "grch38_start": int(h["position"]), "grch38_end": int(h["position_end"]),
                    "strand": h_strand, "bulge_type": "RNA_BULGE_1NT" if "-" in q_raw else "SSO_BULGE_1NT",
                })

        sub18_hits: list[dict[str, int | str]] = []
        if len(sense_dna) > 18:
            seen_loci: set[tuple[str, int, int, str]] = set()
            for off in range(len(sense_dna) - 18 + 1):
                sub_s = sense_dna[off : off + 18]
                r_sub = query_gggenome_json(f"https://gggenome.dbcls.jp/hg38/1/nogap/{sub_s}.json")
                if r_sub.get("error") == "none":
                    for sh in parse_ungapped_hits(r_sub.get("results", []), sub_s):
                        if int(sh["destabilizing_mismatches"]) == 0:
                            lk = (str(sh["chrom"]), int(sh["grch38_start"]), int(sh["grch38_end"]), str(sh["strand"]))
                            if lk not in seen_loci:
                                seen_loci.add(lk)
                                sub18_hits.append({**sh, "subwindow_offset": off})
                time.sleep(0.15)

        coord_payload[iv_id] = {
            "schema_v": 2, "max_mm_queried": used_mm, "gapped_1edit_queried": gap_queried,
            "ungapped_hits": ungapped, "bulge_1nt_hits": bulge_hits, "sub18_core_0destab_hits": sub18_hits,
        }
        time.sleep(0.2)

    coord_cache_fp.write_text(json.dumps(coord_payload, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Staged GENCODE v46 (FASTA + basic & comprehensive GTF), gnomAD v4.1, and v2 GGGenome cache for {len(coord_payload)} intervals.")


if __name__ == "__main__":
    main()
