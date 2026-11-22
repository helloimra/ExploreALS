"""Canonical direct HTTPS single-file and multi-file publisher recipes for ExploreALS v1.2."""
from __future__ import annotations

SPRINGER_BROWN = "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-022-04436-3/MediaObjects"
SPRINGER_MA = "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-022-04424-7/MediaObjects"
SPRINGER_KLIM = "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41593-018-0300-4/MediaObjects"
SPRINGER_MELAMED = "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41593-018-0293-z/MediaObjects"

DIRECT_SINGLE_FILE_HTTPS: dict[str, str] = {
    "DS045_TRAUT": "https://static-content.springer.com/esm/art%3A10.1186%2Fs13024-025-00838-9/MediaObjects/13024_2025_838_MOESM1_ESM.xlsx",
    "DS031_ZHANG": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-026-02300-5/MediaObjects/41593_2026_2300_MOESM8_ESM.xlsx",
    "DS_ZENG_APA": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-02049-3/MediaObjects/41593_2025_2049_MOESM3_ESM.xlsx",
    "DS_BRYCE_APA": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-02050-w/MediaObjects/41593_2025_2050_MOESM3_ESM.xlsx",
    "DS005_BYE": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41593-025-02118-7/MediaObjects/41593_2025_2118_MOESM3_ESM.xlsx",
    "DS045_XML": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12082929/fullTextXML",
    "DS046_OH_XML": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10215566/fullTextXML",
    "DS_GENCODE_V46_TX": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.transcripts.fa.gz",
    "DS_GENCODE_V46_GTF": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.basic.annotation.gtf.gz",
    "DS_GENCODE_V46_COMP_GTF": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.annotation.gtf.gz",
    "DS_GNOMAD_V41_CONSTRAINT": "https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/constraint/gnomad.v4.1.constraint_metrics.tsv",
    "DS_PDB_7CR2": "https://files.rcsb.org/download/7CR2.cif",
    "DS_PDB_7DJT": "https://files.rcsb.org/download/7DJT.cif",
    "DS_PDB_7ANW": "https://files.rcsb.org/download/7ANW.cif",
    "DS_PDB_7NAL": "https://files.rcsb.org/download/7NAL.cif",
    "DS_PDB_9TZY": "https://files.rcsb.org/download/9TZY.cif",
    "DS_PDB_6VN8": "https://files.rcsb.org/download/6VN8.cif",
    "DS_PDB_7K2V": "https://files.rcsb.org/download/7K2V.cif",
    "DS_PDB_4KC3": "https://files.rcsb.org/download/4KC3.cif",
    "DS_PDB_2Z0D": "https://files.rcsb.org/download/2Z0D.cif",
    "DS_PDB_1XFD": "https://files.rcsb.org/download/1XFD.cif",
    "DS_PDB_3NMR": "https://files.rcsb.org/download/3NMR.cif",
    "DS_AF_Q8N6W0": "https://alphafold.ebi.ac.uk/files/AF-Q8N6W0-F1-model_v6.cif",
}

DIRECT_MULTI_FILE_HTTPS: dict[str, list[tuple[str, str]]] = {
    "DS_CRYPTIC": [
        *[(f"Brown2022_41586_2022_4436_MOESM{i}_ESM.xls", f"{SPRINGER_BROWN}/41586_2022_4436_MOESM{i}_ESM.xls") for i in range(4, 11)],
        *[(f"Brown2022_41586_2022_4436_MOESM{i}_ESM.csv", f"{SPRINGER_BROWN}/41586_2022_4436_MOESM{i}_ESM.csv") for i in (11, 12, 13)],
        ("Brown2022_41586_2022_4436_MOESM14_ESM.xlsx", f"{SPRINGER_BROWN}/41586_2022_4436_MOESM14_ESM.xlsx"),
        *[(f"source_data/Brown2022_41586_2022_4436_MOESM{i}_ESM.xlsx", f"{SPRINGER_BROWN}/41586_2022_4436_MOESM{i}_ESM.xlsx") for i in range(15, 19)],
        ("Klim2019_41593_2018_300_MOESM3_ESM.xlsx", f"{SPRINGER_KLIM}/41593_2018_300_MOESM3_ESM.xlsx"),
        ("Ma2022_41586_2022_4424_MOESM1_ESM.pdf", f"{SPRINGER_MA}/41586_2022_4424_MOESM1_ESM.pdf"),
        *[(f"Ma2022_41586_2022_4424_MOESM{i}_ESM.xlsx", f"{SPRINGER_MA}/41586_2022_4424_MOESM{i}_ESM.xlsx") for i in (5, 6, 7)],
        *[(f"source_data/Ma2022_41586_2022_4424_MOESM{i}_ESM.xlsx", f"{SPRINGER_MA}/41586_2022_4424_MOESM{i}_ESM.xlsx") for i in range(8, 19)],
        *[(f"Melamed2019_41593_2018_293_MOESM{i}_ESM.xlsx", f"{SPRINGER_MELAMED}/41593_2018_293_MOESM{i}_ESM.xlsx") for i in range(3, 8)],
    ],
}
