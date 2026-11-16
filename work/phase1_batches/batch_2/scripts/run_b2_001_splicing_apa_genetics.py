"""RUN-B2-001: Re-compute TDP-43 splicing, 3'UTR APA, Ribo-seq, 2026 consortia QTLs, and Fujita inventory for Batch 2."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase1_batches.batch_runner_utils import (  # noqa: E402
    read_xlsx_sparse_safe,
    resolve_col,
    resolve_dataset_path,
)


def read_sheet_safe(xlsx_path: Path, sheet_name: str, header_row_1based: int = 1) -> pd.DataFrame:
    try:
        return read_xlsx_sparse_safe(xlsx_path, sheet_name, header_row_1based=header_row_1based)
    except ValueError:
        wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
        try:
            rows = list(wb[sheet_name].iter_rows(values_only=True))
        finally:
            wb.close()
        raw_h = list(rows[header_row_1based - 1])
        while raw_h and (raw_h[-1] is None or str(raw_h[-1]).strip() == ""):
            raw_h.pop()
        ncols = len(raw_h)
        headers = [str(h).strip() if h is not None and str(h).strip() else f"_unnamed_{i}" for i, h in enumerate(raw_h)]
        body = [list(r[:ncols]) + [None] * max(0, ncols - len(r)) for r in rows[header_row_1based:]]
        return pd.DataFrame(body, columns=headers)

OUT_DIR = ROOT / "work" / "phase1_batches" / "batch_2" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

GENES_C015 = ["SCFD1", "G2E3", "YKT6", "SEC22B", "STX5", "GOSR1", "NSF", "GDI2"]
GENES_C016 = ["FBXL5", "IREB2", "ACO1", "TFRC", "FTH1", "FTL", "SLC40A1"]
GENES_S05 = ["FNTA", "FNTB", "PGGT1B", "PTAR1", "RABGGTB"]
ALL_GENES = set(GENES_C015 + GENES_C016 + GENES_S05)


def extract_zeng_apa() -> dict:
    p = resolve_dataset_path("DS_ZENG_APA", verify_hash=True)
    res: dict[str, list] = {}
    for sheet, g_alias in [("S1", "Gene_Name"), ("S2", "gene_name"), ("S3", "gene_name"), ("S4", "gene_name"), ("S5", "gene"), ("S6", "gene_name")]:
        df = read_xlsx_sparse_safe(p, sheet, header_row_1based=1)
        gcol = resolve_col(df, g_alias)
        sub = df[df[gcol].astype(str).str.strip().isin(ALL_GENES)].copy()
        res[sheet] = sub.to_dict(orient="records")
    return res


def extract_bryce_apa() -> dict:
    p = resolve_dataset_path("DS_BRYCE_APA", verify_hash=True)
    res: dict[str, list] = {}
    for sheet in ["Supplementary_Table_2", "Supplementary_Table_3", "Supplementary_Table_5", "Supplementary_Table_6"]:
        df = read_sheet_safe(p, sheet, header_row_1based=1)
        gcol = resolve_col(df, "gene_name")
        sub = df[df[gcol].astype(str).str.strip().isin(ALL_GENES)].copy()
        res[sheet] = sub.to_dict(orient="records")
    return res


def extract_cryptic_sources() -> dict:
    cdir = resolve_dataset_path("DS_CRYPTIC")
    out: dict[str, object] = {}

    # Brown 2022 i3Neuron splicing junctions (MOESM11), RNA-seq DE (MOESM12), Ribo-seq (MOESM13)
    for tag, fname in [("brown2022_splicing_moesm11", "Brown2022_41586_2022_4436_MOESM11_ESM.csv"),
                       ("brown2022_rnaseq_moesm12", "Brown2022_41586_2022_4436_MOESM12_ESM.csv"),
                       ("brown2022_riboseq_moesm13", "Brown2022_41586_2022_4436_MOESM13_ESM.csv")]:
        df = pd.read_csv(cdir / fname)
        gcol = resolve_col(df, "gene_name", "gene", "symbol", "geneName")
        sub = df[df[gcol].astype(str).str.strip().isin(ALL_GENES)].copy()
        out[tag] = sub.to_dict(orient="records")

    # Ma 2022 consensus cryptic splicing (MOESM5)
    wb_ma = pd.ExcelFile(cdir / "Ma2022_41586_2022_4424_MOESM5_ESM.xlsx")
    ma_hits = {}
    for s in wb_ma.sheet_names:
        df_m = pd.read_excel(wb_ma, sheet_name=s)
        mask = df_m.apply(lambda col: col.astype(str).str.strip().isin(ALL_GENES)).any(axis=1)
        if mask.any():
            ma_hits[s] = df_m[mask].to_dict(orient="records")
    out["ma2022_moesm5"] = ma_hits

    # Melamed 2019 SH-SY5Y TDP-43 KD (MOESM3) and N352S (MOESM4)
    for tag, fname in [("melamed2019_kd_moesm3", "Melamed2019_41593_2018_293_MOESM3_ESM.xlsx"),
                       ("melamed2019_n352s_moesm4", "Melamed2019_41593_2018_293_MOESM4_ESM.xlsx")]:
        xl = pd.ExcelFile(cdir / fname)
        df_mel = pd.read_excel(xl, sheet_name=xl.sheet_names[0])
        mask = df_mel.apply(lambda col: col.astype(str).str.strip().isin(ALL_GENES)).any(axis=1)
        out[tag] = df_mel[mask].to_dict(orient="records")
    return out


def extract_consortia_and_fujita() -> dict:
    cons_dir = resolve_dataset_path("DS_CONS2026")
    terms = sorted(ALL_GENES) + ["rs229143", "rs229243", "rs229190", "rs10139154", "14q12", "ferroptosis"]
    cons_hits: dict[str, dict] = {}
    for txt_file in sorted(cons_dir.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8", errors="replace")
        file_res = {}
        for t in terms:
            matches = [m.start() for m in re.finditer(rf"\b{re.escape(t)}\b", text, flags=re.IGNORECASE)]
            snippets = [text[max(0, idx - 140): min(len(text), idx + 220)].replace("\n", " ") for idx in matches[:6]]
            if matches:
                file_res[t] = {"count": len(matches), "snippets": snippets}
        cons_hits[txt_file.name] = file_res

    fuj_dir = resolve_dataset_path("DS026_FUJITA")
    inv = pd.read_csv(fuj_dir / "tested_gene_inventory.csv")
    inv_hits = inv[inv.apply(lambda col: col.astype(str).str.strip().isin(ALL_GENES)).any(axis=1)].to_dict(orient="records")

    # Scan chr14q12 (30.45-30.85 Mb GRCh38) & rsIDs in common_variants.GRCh38.tsv
    target_rs = {"rs229143", "rs229243", "rs229190", "rs10139154"}
    fuj_vars = []
    for chunk in pd.read_csv(fuj_dir / "common_variants.GRCh38.tsv", sep="\t", chunksize=200_000):
        rs_col = resolve_col(chunk, "rsid", "variant_id", "snp", "id")
        m = chunk[rs_col].astype(str).isin(target_rs)
        if m.any():
            fuj_vars.extend(chunk[m].to_dict(orient="records"))
    return {"consortia_2026": cons_hits, "fujita_inventory": inv_hits, "fujita_variants": fuj_vars}


def main() -> None:
    payload = {
        "zeng2025_apa": extract_zeng_apa(),
        "brycesmith2025_apa": extract_bryce_apa(),
        "tdp43_cryptic_sources": extract_cryptic_sources(),
        "consortia_and_fujita": extract_consortia_and_fujita(),
    }
    out_json = OUT_DIR / "b2_001_splicing_apa_genetics.json"
    out_json.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[RUN-B2-001] Wrote {out_json} ({out_json.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
