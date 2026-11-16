"""Deterministic, read-only open-access dataset staging from ExploreALS into CarbonALS."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import os

CARBON_ROOT = Path(__file__).resolve().parents[1]
EXPLORE_ROOT = Path(os.environ.get("EXPLORE_ALS_UPSTREAM_ROOT", str(CARBON_ROOT.parent / "ExploreALS")))
DATA_ROOT = CARBON_ROOT / "data"
REG_ROOT = CARBON_ROOT / "registries"

# (dataset_id, domain, upstream_relpath, local_relpath, accession_or_doi, license_info, relevant_candidates, description)
STAGING_MANIFEST = [
    ("DS_BASE_REG", "baseline", "registries/candidates.csv", "explore_als_baseline/candidates.csv", "ExploreALS_R145", "Internal Open Baseline", "ALL", "Frozen ExploreALS 21-candidate registry baseline"),
    ("DS_BASE_DS", "baseline", "registries/datasets.csv", "explore_als_baseline/datasets.csv", "ExploreALS_R145", "Internal Open Baseline", "ALL", "Frozen ExploreALS datasets registry"),
    ("DS_BASE_EV", "baseline", "registries/evidence.csv", "explore_als_baseline/evidence.csv", "ExploreALS_R145", "Internal Open Baseline", "ALL", "Frozen ExploreALS evidence claims baseline"),
    ("DS_BASE_SRC", "baseline", "registries/sources.csv", "explore_als_baseline/sources.csv", "ExploreALS_R145", "Internal Open Baseline", "ALL", "Frozen ExploreALS bibliographic sources baseline"),
    ("DS_BASE_REV", "baseline", "registries/reviews.csv", "explore_als_baseline/reviews.csv", "ExploreALS_R145", "Internal Open Baseline", "ALL", "Frozen ExploreALS adversarial reviews baseline"),
    ("DS_BASE_LNK", "baseline", "registries/cross_track_links.csv", "explore_als_baseline/cross_track_links.csv", "ExploreALS_R145", "Internal Open Baseline", "ALL", "Frozen ExploreALS cross-track links"),
    ("DS_BASE_P10A", "baseline", "work/phase10a_portfolio_triage_2026-11-06/phase10a_portfolio_triage_summary.json", "explore_als_baseline/phase10a_portfolio_triage_summary.json", "ExploreALS_R125", "Internal Open Baseline", "C001-C021", "Frozen ExploreALS Phase 10A portfolio triage JSON"),
    ("DS001_COUNTS", "transcriptomics", "work/audit32/NYGC_counts.txt.gz", "transcriptomics/nygc_d001/NYGC_counts.txt.gz", "GSE153960", "Public GEO / NYGC Open", "C001;C002;C006;C007;C010;C014-C021;BA9", "NYGC ALS Consortium postmortem CNS bulk RNA-seq raw gene counts"),
    ("DS001_FEAT", "transcriptomics", "work/audit32/provisional_unique_feature_map.csv", "transcriptomics/nygc_d001/provisional_unique_feature_map.csv", "GSE153960", "Public GEO / NYGC Open", "C001-C021;BA9", "NYGC bulk RNA-seq Ensembl-to-symbol unique feature mapping"),
    ("DS001_META", "transcriptomics", "data/nygc_collab_metadata_2026-10-31/nygc_collab_metadata_c05a4864.xlsx", "transcriptomics/nygc_d001/nygc_collab_metadata_c05a4864.xlsx", "GSE153960", "Public Consortia Metadata", "C001-C021;BA9", "NYGC donor, brain region, RIN, batch, and genotype metadata"),
    ("DS001_FLAGSHIP", "transcriptomics", "data/regional_supplements/NYGC_Flagship_ST_1_3_Metadata.xlsx", "transcriptomics/nygc_d001/NYGC_Flagship_ST_1_3_Metadata.xlsx", "PMID:35197629;GSE153960", "Published Supplement", "C001-C021;BA9", "NYGC flagship supplementary tables ST1-ST3 donor/sample metadata"),
    ("DS001_ONEILL", "transcriptomics", "data/oneill2025_supplement_2026-11-03/1-s2.0-S2211124725001731-mmc2.xlsx", "transcriptomics/subtypes/oneill2025_mmc2.xlsx", "10.1016/j.celrep.2025.115402", "CC BY / Published Supplement", "C001;C002;C005;C007;C017;C018;C019", "O'Neill et al. 2025 ALS-Ox, ALS-Glia, and ALS-TE molecular subtype labels"),
    ("DS001_TAM", "transcriptomics", "work/audit4/Tam_publisher_mmc2.xlsx", "transcriptomics/subtypes/Tam2019_mmc2.xlsx", "PMID:31665631;GSE124439", "Published Supplement", "C005;C007;C017;C018;C019", "Tam et al. 2019 postmortem cortical molecular subtype assignments"),
    ("DS_GC_REF", "transcriptomics", "work/gc_axis/sources/ensembl116_hsapiens_gene_gc.tsv", "transcriptomics/ensembl116_hsapiens_gene_gc.tsv", "Ensembl_v116", "Public Reference", "C010;C014-C018;BA9", "Human Ensembl v116 gene GC-content table for postmortem agonal/GC confounding checks"),
    ("DS003_PB", "transcriptomics", "data/d003_pseudobulk", "transcriptomics/d003_pseudobulk", "PRJNA1073234;syn51105515", "Public Open Pseudobulk", "C005;C006;C010;C014;C015;C016;BA9", "Pineda/MIT primary motor & prefrontal cortex snRNA-seq donor-celltype pseudobulk"),
    ("DS003_SUPP", "transcriptomics", "work/audit5/Pineda_mmc2.xlsx", "transcriptomics/Pineda2024_mmc2.xlsx", "PMID:38518782", "Published Supplement", "C005;C010;C014;C015;C016;BA9", "Pineda et al. 2024 M1/BA9 snRNA-seq supplementary DE tables"),
    ("DS_BA9_BUNDLE", "transcriptomics", "work/g1a06_run_bundle_2026-10-31/bundle_v5", "transcriptomics/ba9_bundle_v5", "ExploreALS_G1A06", "Open Derived Bundle", "C010;BA9", "BA9 10-named-gene design matrices and crosswalk ranks"),
    ("DS_EDIN_PB", "transcriptomics", "data/edinburgh_gse290359_pseudobulk", "transcriptomics/edinburgh_gse290359_pseudobulk", "GSE290359", "Public GEO Open", "C010;C014-C018;BA9", "Edinburgh BA44/BA46 snRNA-seq donor pseudobulk & QC metadata"),
    ("DS014_PRUD", "transcriptomics", "work/paired_region33/primary", "transcriptomics/gse67196_prudencio_primary", "GSE67196", "Public GEO Derived", "C007", "Prudencio et al. 2015 frontal/cerebellar normalized counts, metadata, and QC"),
    ("DS_CONS2026", "transcriptomics", "work/phase10b_consortia_validation_2026-11-06/fulltexts", "transcriptomics/consortia_2026_fulltexts", "PMC12919128;PMC12982666;PMC13337491", "EuropePMC Open Access", "C001;C002;C014;C015;C016;C017;C018", "Full texts of Tsitkov 2026 AALS-594 QTL, Grozdanov/Lee 2026 M1 snMultiome+FANS, and Zhang 2026 Spatial"),
    ("DS031_ZHANG", "transcriptomics", "work/il1rl1_fig6_61/41593_2026_2300_MOESM8_ESM.xlsx", "transcriptomics/Zhang2026_Spatial_MOESM8.xlsx", "PMID:42135512;GSE288365", "Published Supplement", "C007;C017;C018", "Zhang/Gate et al. 2026 cervical spinal spatial transcriptomics supplement"),
    ("DS_CRYPTIC", "genomics_splicing", "work/tdp43_overlap/sources", "genomics_splicing/tdp43_cryptic_sources", "PMID:35197628;PMID:35197629;PMID:30643298;PMID:30643292", "Published Supplements", "C001;C002;C006;C014;C015;C020", "Brown 2022, Ma 2022, Klim 2019, and Melamed 2019 TDP-43 cryptic splicing supplements"),
    ("DS_ZENG_APA", "genomics_splicing", "work/tdp43_apa_lookup/sources/zeng2025/41593_2025_2049_MOESM3_ESM.xlsx", "genomics_splicing/tdp43_apa/Zeng2025_MOESM3.xlsx", "10.1038/s41593-025-02049-3", "Published Supplement", "C014;C015;C016;C019;C021", "Zeng et al. 2025 TDP-43 alternative polyadenylation (3'UTR dPAS) supplement"),
    ("DS_BRYCE_APA", "genomics_splicing", "work/tdp43_apa_lookup/sources/brycesmith2025/41593_2025_2050_MOESM3_ESM.xlsx", "genomics_splicing/tdp43_apa/BryceSmith2025_MOESM3.xlsx", "PMID:40038262", "Published Supplement", "C001;C002;C015;C016", "Bryce-Smith et al. 2025 TDP-43 cryptic exon, ALE, Ribo-seq, and 3'Ext supplement"),
    ("DS_ELIG_BED", "genomics_splicing", "reference/eligibility_v1.0", "genomics_splicing/eligibility_v1.0", "GRCh38_MANE", "Open Reference", "ALL", "GRCh38 ALS causal-gene BED intervals and donor genetic adjudication rules v1.0"),
    ("DS026_FUJITA", "genomics_splicing", "data/fujita_oligodendrocyte", "genomics_splicing/fujita_oligodendrocyte", "syn52335732", "Open Derived Summary", "C015;BA9", "Fujita ROSMAP DLPFC cell-type eQTL variant inventory and summaries"),
    ("DS045_TRAUT", "proteomics", "work/option_d_open_access_fallback_2026-11-06/inputs/13024_2025_838_MOESM1_ESM.xlsx", "proteomics/trautwig2025_d045/13024_2025_838_MOESM1_ESM.xlsx", "PMC12082929;PMID:40375307", "CC BY 4.0", "C001;C002;C005;C007;C014;C015;C017;C018;C019", "Trautwig et al. 2025 4-Center CSF Proteomics (N=101 TMTpro + N=259 DIA-MS + WGCNA)"),
    ("DS045_XML", "proteomics", "work/option_d_open_access_fallback_2026-11-06/inputs/PMC12082929_Trautwig2025.xml", "proteomics/trautwig2025_d045/PMC12082929_Trautwig2025.xml", "PMC12082929", "CC BY 4.0", "C002;C005;C015;C017;C018", "Trautwig et al. 2025 full-text JATS XML for cohort table marginal verification"),
    ("DS046_OH_XML", "proteomics", "work/option_d_open_access_fallback_2026-11-06/inputs/PMC10215566_Oh2023.xml", "proteomics/oh2023_d046/PMC10215566_Oh2023.xml", "PMC10215566;PMID:37238921", "CC BY 4.0", "C005;C017;C018", "Oh, Jang & Na 2023 NEALS/ARTFL-UCSF CSF TMT + PRM-MS JATS XML"),
    ("DS029_SPILL", "proteomics", "work/spillman59/originals", "proteomics/spillman2026_d029_d030", "PXD083082;10.1007/s00401-026-03084-5", "Published Open Supplement", "C001;C002;C005;C014;C015;C016", "Spillman et al. 2026 frontal cortex & iPSC neuron fraction DIA proteomics"),
    ("DS005_BYE", "pharmacology_structures", "data/bye2025_supplement_2026-11-02/41593_2025_2118_MOESM3_ESM.xlsx", "pharmacology_structures/bye2025/41593_2025_2118_MOESM3_ESM.xlsx", "10.1038/s41593-025-02118-7", "Published Supplement", "C003;C004;C005;C008;C009;C010;C013;C019;C020;C021;S01-S04", "Bye et al. 2025 107-drug x 16-sALS-donor iPSC-MN survival screen & RNA-seq DEGs"),
    ("DS_ROPALS", "pharmacology_structures", "work/ropinirole_exposure22/ROPALS2023_tables.xlsx", "pharmacology_structures/ropals2023/ROPALS2023_tables.xlsx", "PMID:37264228", "Published Supplement", "C010", "Morimoto et al. 2023 ROPALS Phase 1/2a Ropinirole trial & CSF exposure tables"),
    ("DS_AFDB", "pharmacology_structures", "work/phase8_structural_druggability_2026-11-06/afdb", "pharmacology_structures/afdb", "AlphaFold_DB_v6", "CC BY 4.0", "C015;C016", "AlphaFold v6 .cif models & PAE matrices for YKT6, GDI2, SCFD1, SEC22B, GOSR1, STX5, NSF, G2E3, FBXL5, IREB2"),
    ("DS_PDB", "pharmacology_structures", "work/phase8_structural_druggability_2026-11-06/pdb", "pharmacology_structures/pdb", "RCSB_PDB:3EGD;3KYQ;3V5Z;6J74;6VCD", "CC0 1.0 Public Domain", "C015;C016", "Experimental X-ray/cryo-EM .cif structures for SEC22B, YKT6, and FBXL5-IRP2"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_and_hash(src: Path, dst: Path) -> tuple[int, str, int]:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return dst.stat().st_size, sha256_file(dst), 1
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        files = sorted(p for p in dst.rglob("*") if p.is_file())
        tree_hash = hashlib.sha256()
        total_bytes = 0
        for p in files:
            rel = p.relative_to(dst).as_posix()
            fh = sha256_file(p)
            tree_hash.update(f"{rel}:{fh}\n".encode("utf-8"))
            total_bytes += p.stat().st_size
        return total_bytes, tree_hash.hexdigest(), len(files)
    raise FileNotFoundError(f"Missing upstream path: {src}")


def main() -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    REG_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    total_files = 0
    total_bytes = 0
    for ds_id, domain, up_rel, loc_rel, acc, lic, cands, desc in STAGING_MANIFEST:
        src = EXPLORE_ROOT / Path(up_rel)
        dst = DATA_ROOT / Path(loc_rel)
        sz, digest, fcount = copy_and_hash(src, dst)
        total_files += fcount
        total_bytes += sz
        rows.append({
            "dataset_id": ds_id,
            "domain": domain,
            "local_relpath": f"data/{loc_rel}",
            "upstream_explore_relpath": up_rel,
            "accession_or_doi": acc,
            "license_or_access": lic,
            "size_bytes": sz,
            "sha256": digest,
            "relevant_candidates": cands,
            "description": desc,
        })

    manifest_csv = REG_ROOT / "datasets_manifest.csv"
    with manifest_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    receipt = {
        "staged_at_utc": datetime.now(timezone.utc).isoformat(),
        "upstream_root": str(EXPLORE_ROOT),
        "upstream_mutated": False,
        "controlled_access_dua_files_copied": 0,
        "dataset_entries": len(rows),
        "total_files_staged": total_files,
        "total_megabytes_staged": round(total_bytes / (1024 * 1024), 2),
        "datasets": rows,
    }
    (DATA_ROOT / "DATA_PROVENANCE_MANIFEST.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"Staged {len(rows)} dataset bundles ({total_files} files, {receipt['total_megabytes_staged']} MB) cleanly!")


if __name__ == "__main__":
    main()
