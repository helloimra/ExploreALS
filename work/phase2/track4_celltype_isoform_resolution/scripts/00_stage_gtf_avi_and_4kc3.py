"""Stage GENCODE v46 GTF isoform coordinates, dbSNP/AlphaGenome AVI scores, and PDB 4KC3 (IL-33:ST2)."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from carbon_als.loaders import download_https_structure  # noqa: E402
from carbon_als.skill_cli import run_skill_cli_to_file  # noqa: E402

import os

CACHE = ROOT / "work" / "phase2" / "track4_celltype_isoform_resolution" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)
PDB_STAGE = ROOT / "data" / "pharmacology_structures" / "phase2_pdb"
PDB_STAGE.mkdir(parents=True, exist_ok=True)
ART_STRUCT = Path(os.environ["ARTIFACT_STRUCT_DIR"]) if os.environ.get("ARTIFACT_STRUCT_DIR") else None
if ART_STRUCT:
    ART_STRUCT.mkdir(parents=True, exist_ok=True)

SKILLS = Path(os.environ.get("SCIENCE_SKILLS_DIR", ""))
AVI_CLI = SKILLS / "alphagenome_variant_impact_score" / "scripts" / "alphagenome_atlas_avi.py"
LINKS_CLI = SKILLS / "alphagenome_atlas_website_links" / "scripts" / "alphagenome_atlas_links.py"
DBSNP_CLI = SKILLS / "dbsnp_database" / "scripts" / "dbsnp_cli.py"
PDB_DL = SKILLS / "pdb_database" / "scripts" / "download_coordinate_files.py"
PDB_META = SKILLS / "pdb_database" / "scripts" / "fetch_pdb_metadata.py"


def resolve_grch38_variant(dbsnp_json: dict) -> str:
    for pl in dbsnp_json.get("placements", []):
        seq_id = str(pl.get("seq_id", ""))
        if seq_id.startswith("NC_000002."):
            chrom = "chr2"
            alleles = pl.get("alleles", [])
            if len(alleles) >= 2:
                pos_1b = int(alleles[0]["position"]) + 1
                ref = str(alleles[0]["deleted_sequence"])
                alt = str(alleles[1]["inserted_sequence"])
                return f"{chrom}:{pos_1b}:{ref}>{alt}"
    raise RuntimeError(f"Could not resolve GRCh38 chr2 placement from dbSNP payload: {list(dbsnp_json.keys())}")


def main() -> None:
    # 1. GENCODE v46 GTF protein-coding transcripts with 1-based exons, CDS, UTRs (gtf --format json writes to stdout)
    clean_env = {k: v for k, v in __import__("os").environ.items() if k != "VIRTUAL_ENV"}
    for gene in ("IL1RL1", "CHMP7", "CHMP2B", "DNAJB2", "SNPH"):
        out_p = CACHE / f"gtf_{gene}.json"
        if not (out_p.is_file() and out_p.stat().st_size > 10):
            with out_p.open("w", encoding="utf-8") as fh:
                subprocess.run(
                    ["uv", "run", str(AVI_CLI), "gtf", "--gene", gene, "--all_transcripts", "--protein_coding", "--exons", "--cds", "--utr", "--format", "json"],
                    cwd=str(AVI_CLI.parent.parent),
                    env=clean_env,
                    stdin=subprocess.DEVNULL,
                    stdout=fh,
                    stderr=subprocess.DEVNULL,
                    timeout=120,
                    check=True,
                )

    # 2. dbSNP -> GRCh38 coordinates -> AlphaGenome AVI + Atlas deep-links for IL1RL1 SNPs
    vars_resolved: dict[str, str] = {}
    for rsid in ("rs1420101", "rs953934"):
        db_out = CACHE / f"dbsnp_{rsid}.json"
        payload = run_skill_cli_to_file(DBSNP_CLI, ["get-variant", rsid], db_out, timeout_sec=45, use_cache=True)
        # Fallback inspection if schema uses spdi or alleles
        vstr = None
        for pl in payload.get("placements", []):
            if str(pl.get("seq_id", "")).startswith("NC_000002."):
                als = pl.get("alleles", [])
                if len(als) >= 2:
                    pos_0 = als[0].get("position", als[0].get("pos"))
                    ref = als[0].get("deleted_sequence", als[0].get("ref"))
                    alt = als[1].get("inserted_sequence", als[1].get("alt"))
                    if pos_0 is not None and ref and alt:
                        vstr = f"chr2:{int(pos_0) + 1}:{ref}>{alt}"
                        break
        if vstr:
            vars_resolved[rsid] = vstr

    if vars_resolved:
        avi_out = CACHE / "avi_il1rl1_snps.json"
        run_skill_cli_to_file(
            AVI_CLI,
            ["query", *vars_resolved.values(), "--include_features", "--include_track_info", "--format", "json"],
            avi_out,
            timeout_sec=60,
            use_cache=True,
        )
        links_cache = CACHE / "il1rl1_atlas_links.json"
        if not links_cache.is_file():
            links_map: dict[str, str] = {}
            for rsid, vstr in vars_resolved.items():
                if LINKS_CLI.is_file():
                    proc = subprocess.run(
                        ["uv", "run", str(LINKS_CLI), "variant", vstr, "--modalities", "RNA_SEQ,DNASE,CHIP_TF"],
                        cwd=str(LINKS_CLI.parent.parent),
                        env={k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"},
                        capture_output=True,
                        text=True,
                        timeout=30,
                        check=False,
                    )
                    links_map[rsid] = proc.stdout.strip()
                else:
                    links_map[rsid] = f"https://deepmind.google.com/science/alphagenome/atlas?q={vstr}"
            links_cache.write_text(json.dumps({"variants": vars_resolved, "links": links_map}, indent=2), encoding="utf-8")

    # 3. PDB 4KC3 (human IL-33 + ST2 ectodomain complex) metadata & coordinate staging
    pdb_meta_cache = CACHE / "pdb_track4_metadata.json"
    if not pdb_meta_cache.is_file():
        import urllib.request
        gql = {"query": '{ entries(entry_ids: ["4KC3", "6VCD", "3V5Z"]) { rcsb_id struct { title } rcsb_entry_info { resolution_combined } rcsb_primary_citation { pdbx_database_id_PubMed rcsb_journal_abbrev year } } }'}
        req = urllib.request.Request(
            "https://data.rcsb.org/graphql",
            data=json.dumps(gql).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "ExploreALS/1.2"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            pdb_meta_cache.write_text(resp.read().decode("utf-8"), encoding="utf-8")
    cif_dest = PDB_STAGE / "pdb_00004kc3.cif"
    if not cif_dest.is_file():
        download_https_structure("https://files.rcsb.org/download/4KC3.cif", cif_dest)
    if ART_STRUCT:
        shutil.copy2(cif_dest, ART_STRUCT / "pdb_00004kc3.cif")
    print("STAGED GTFs, dbSNP/AVI:", vars_resolved, "and 4KC3 bytes:", cif_dest.stat().st_size)


if __name__ == "__main__":
    main()
