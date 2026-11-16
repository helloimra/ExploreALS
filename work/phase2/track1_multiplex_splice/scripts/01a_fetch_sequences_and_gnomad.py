"""Phase 2 Track 1 (01a): Fetch GRCh38 target sequences, MANE protein/CDS, and gnomAD v4 variants."""
from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
TRACK_DIR = ROOT / "work" / "phase2" / "track1_multiplex_splice"
DATA_DIR = TRACK_DIR / "data"
OUT_DIR = TRACK_DIR / "outputs"

SEQ_WINDOWS: dict[str, tuple[str, int, int, str]] = {
    "KCNQ2": ("20", 63442050, 63442900, "-"),
    "UNC13A": ("19", 17641850, 17642900, "-"),
    "STMN2": ("8", 79616650, 79617250, "+"),
    "G2E3": ("14", 30563600, 30564250, "+"),
}

GNOMAD_QUERY = """
query($chrom: String!, $start: Int!, $stop: Int!, $dataset: DatasetId!, $referenceGenome: ReferenceGenomeId!) {
  region(chrom: $chrom, start: $start, stop: $stop, reference_genome: $referenceGenome) {
    variants(dataset: $dataset) {
      variant_id
      rsids
      consequence
      exome {
        ac
        an
        af
        homozygote_count
      }
      genome {
        ac
        an
        af
        homozygote_count
      }
    }
  }
}
"""


def fetch_ensembl_text(endpoint: str) -> str:
    url = f"https://rest.ensembl.org{endpoint}"
    req = urllib.request.Request(url, headers={"Accept": "text/plain", "User-Agent": "CarbonALS/0.2"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8").strip()


def fetch_gnomad_region(chrom: str, start: int, stop: int) -> dict[str, Any]:
    payload = json.dumps({
        "query": GNOMAD_QUERY,
        "variables": {
            "chrom": chrom,
            "start": start,
            "stop": stop,
            "dataset": "gnomad_r4",
            "referenceGenome": "GRCh38",
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://gnomad.broadinstitute.org/api",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "CarbonALS/0.2"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sequences: dict[str, dict[str, Any]] = {}
    for gene, (chrom, s1, e1, strand) in SEQ_WINDOWS.items():
        staged_txt = DATA_DIR / f"seq_{gene.lower()}_win.txt"
        source_used = "Ensembl_REST_GRCh38"
        seq_str = ""
        if staged_txt.exists() and staged_txt.stat().st_size >= (e1 - s1 + 1):
            raw = staged_txt.read_text(encoding="utf-8").strip()
            if len(raw) == (e1 - s1 + 1):
                seq_str = raw.upper()
                source_used = str(staged_txt.relative_to(ROOT))
        if not seq_str:
            seq_str = fetch_ensembl_text(f"/sequence/region/human/{chrom}:{s1}..{e1}?coord_system_version=GRCh38")
            time.sleep(0.25)
        assert len(seq_str) == (e1 - s1 + 1), f"{gene}: expected {e1 - s1 + 1} bp, got {len(seq_str)}"
        sequences[gene] = {
            "chromosome": f"chr{chrom}",
            "start_1b": s1,
            "end_1b": e1,
            "length_bp": len(seq_str),
            "strand": strand,
            "source": source_used,
            "dna_plus_5to3": seq_str.upper(),
        }
        print(f"[SEQ] {gene} chr{chrom}:{s1}-{e1} ({len(seq_str)} bp) OK")

    # Fetch MANE Select protein sequences to confirm exact AA spans
    mane_proteins: dict[str, str] = {}
    for gene, enst in [
        ("KCNQ2", "ENST00000359125"),
        ("UNC13A", "ENST00000519716"),
        ("STMN2", "ENST00000220876"),
        ("G2E3", "ENST00000206595"),
    ]:
        mane_proteins[gene] = fetch_ensembl_text(f"/sequence/id/{enst}?type=protein")
        time.sleep(0.25)
        print(f"[PROT] {gene} ({enst}): {len(mane_proteins[gene])} aa")

    # Query gnomAD v4 across all 4 intervals
    gnomad_summary: dict[str, Any] = {}
    for gene, (chrom, s1, e1, _) in SEQ_WINDOWS.items():
        raw_g = fetch_gnomad_region(chrom, s1, e1)
        out_g = OUT_DIR / f"genomics_gnomad_{gene.lower()}.json"
        out_g.write_text(json.dumps(raw_g, indent=2), encoding="utf-8")
        vlist = raw_g.get("data", {}).get("region", {}).get("variants", []) or []
        common = []
        for v in vlist:
            ex_af = float((v.get("exome") or {}).get("af") or 0.0)
            ge_af = float((v.get("genome") or {}).get("af") or 0.0)
            max_af = max(ex_af, ge_af)
            if max_af >= 0.005:
                parts = str(v["variant_id"]).split("-")
                pos_1b = int(parts[1])
                ref_b, alt_b = parts[2], parts[3]
                span_positions = list(range(pos_1b, pos_1b + len(ref_b)))
                common.append({
                    "variant_id": v["variant_id"],
                    "rsids": v.get("rsids") or [],
                    "pos_1b": pos_1b,
                    "ref": ref_b,
                    "alt": alt_b,
                    "span_1b": span_positions,
                    "consequence": v.get("consequence"),
                    "exome_af": ex_af if v.get("exome") else None,
                    "genome_af": ge_af if v.get("genome") else None,
                    "max_af": round(max_af, 6),
                })
        gnomad_summary[gene] = {
            "interval_queried": f"chr{chrom}:{s1}-{e1}",
            "total_gnomad_v4_variants": len(vlist),
            "common_variants_af_ge_0_005": common,
        }
        print(f"[GNOMAD] {gene}: {len(vlist)} total variants, {len(common)} with AF >= 0.005")
        time.sleep(1.5)

    bundle_path = OUT_DIR / "genomics_sequences_and_gnomad.json"
    bundle_path.write_text(
        json.dumps({"sequences": sequences, "mane_proteins": mane_proteins, "gnomad_v4": gnomad_summary}, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {bundle_path}")


if __name__ == "__main__":
    main()
