"""RUN-P2-T4-002: C014 CHMP7/CHMP2B, C016 FBXL5 (PDB 6VCD/3V5Z), BA9-04 DNAJB2a/b & BA9-08 SNPH Compartments."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from carbon_als.allostery_pkpd import sweep_pulsed_pkpd_sensitivity  # noqa: E402
from carbon_als.loaders import (  # noqa: E402
    assert_modality,
    load_bye2025_screen,
    load_edinburgh_pseudobulk,
    load_pineda2024_pseudobulk,
    load_spillman2026_fractions,
    load_zhang2026_spatial,
    resolve_col,
    resolve_dataset_path,
)
from carbon_als.mmcif_parser import load_mmcif_structure  # noqa: E402

CACHE = ROOT / "work" / "phase2" / "track4_celltype_isoform_resolution" / "cache"
OUT_DIR = ROOT / "work" / "phase2" / "track4_celltype_isoform_resolution" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_spillman_moesm3_ipsc_pellet(genes: list[str]) -> dict[str, dict[str, Any]]:
    """Extract Spillman 2026 MOESM3 iPSC-neuron total homogenate (HOx) vs insoluble pellet (Px) DIA proteomics."""
    m3 = pd.read_excel(resolve_dataset_path("DS029_SPILL") / "401_2026_3084_MOESM3_ESM.xlsx")
    gcol = resolve_col(m3, "Gene")
    out: dict[str, dict[str, Any]] = {}
    for sym in genes:
        sub = m3.loc[m3[gcol].fillna("").astype(str).str.split(";").apply(lambda xs: sym in xs)]
        if sub.empty:
            out[sym] = {"detected_in_moesm3": False}
            continue
        r = sub.iloc[0]
        out[sym] = {
            "detected_in_moesm3": True,
            "modality": assert_modality("PROTEOMICS_DIA", "DS029_SPILL_MOESM3"),
            "ipsc_homogenate_log2fc": round(float(r[resolve_col(m3, "Log2FC_HOxC9FTD.HOxCTRL")]), 4),
            "ipsc_homogenate_p": float(r[resolve_col(m3, "pVal_HOxC9FTD.HOxCTRL")]),
            "ipsc_pellet_log2fc": round(float(r[resolve_col(m3, "Log2FC_PxC9FTD.PxCTRL")]), 4),
            "ipsc_pellet_p": float(r[resolve_col(m3, "pVal_PxC9FTD.PxCTRL")]),
            "c9ftd_pellet_over_homog_log2fc": round(float(r[resolve_col(m3, "Log2FC_PxC9FTD.HOxC9FTD")]), 4),
            "c9ftd_pellet_over_homog_p": float(r[resolve_col(m3, "pVal_PxC9FTD.HOxC9FTD")]),
        }
    return out


def analyze_fbxl5_structures() -> dict[str, Any]:
    pdb_dir = resolve_dataset_path("DS_PDB")
    s_6vcd = load_mmcif_structure(pdb_dir / "6vcd.cif" if (pdb_dir / "6vcd.cif").is_file() else next(pdb_dir.glob("*6vcd*.cif")))
    s_3v5z = load_mmcif_structure(pdb_dir / "3v5z.cif" if (pdb_dir / "3v5z.cif").is_file() else next(pdb_dir.glob("*3v5z*.cif")))

    rg6 = s_6vcd.residue_groups()
    fes_atoms = [a for a in s_6vcd.ligand_atoms if a.comp_id in {"FES", "SF4", "FE", "FE2"}]
    fes_coords = np.array([a.coord for a in fes_atoms])
    cys_coord_6vcd = []
    for (ch, seq, comp), atoms in sorted(rg6.items(), key=lambda x: (x[0][0], x[0][1])):
        pts = np.array([a.coord for a in atoms])
        d_fes = float(np.min(np.linalg.norm(pts[:, None, :] - fes_coords[None, :, :], axis=-1))) if len(fes_coords) else 99.0
        if d_fes <= 3.5:
            cys_coord_6vcd.append({"chain": ch, "auth_seq_id": seq, "comp_id": comp, "min_dist_to_FES_A": round(d_fes, 2)})

    # Inter-chain FBXL5-IRP2 contacts <=4.0A in 6VCD (chains with >200 residues)
    chain_lens = {c: len([k for k in rg6 if k[0] == c]) for c in sorted({k[0] for k in rg6})}
    top2 = sorted(chain_lens, key=lambda c: chain_lens[c], reverse=True)[:2]
    c1_atoms = np.array([a.coord for k, v in rg6.items() if k[0] == top2[0] for a in v])
    inter_contacts = []
    for (_, seq, comp), atoms in sorted(((k, v) for k, v in rg6.items() if k[0] == top2[1]), key=lambda x: x[0][1]):
        pts = np.array([a.coord for a in atoms])
        dmin = float(np.min(np.linalg.norm(pts[:, None, :] - c1_atoms[None, :, :], axis=-1)))
        if dmin <= 4.0:
            inter_contacts.append({"chain": top2[1], "auth_seq_id": seq, "comp_id": comp, "min_dist_A": round(dmin, 2)})

    rg3 = s_3v5z.residue_groups()
    fe_3v5z = np.array([a.coord for a in s_3v5z.ligand_atoms if a.comp_id.startswith("FE") or a.comp_id == "OXY"])
    diiron_ligs = []
    for (ch, seq, comp), atoms in sorted(rg3.items(), key=lambda x: (x[0][0], x[0][1])):
        if ch != sorted({k[0] for k in rg3})[0]:
            continue
        pts = np.array([a.coord for a in atoms])
        dfe = float(np.min(np.linalg.norm(pts[:, None, :] - fe_3v5z[None, :, :], axis=-1))) if len(fe_3v5z) else 99.0
        if dfe <= 3.2:
            diiron_ligs.append({"chain": ch, "auth_seq_id": seq, "comp_id": comp, "min_dist_to_diiron_A": round(dfe, 2)})

    return {
        "pdb_6vcd_chain_residue_counts": chain_lens,
        "pdb_6vcd_2fe2s_coordinating_residues_le_3p5A": cys_coord_6vcd,
        "pdb_6vcd_fbxl5_irp2_interface_residues_le_4p0A_count": len(inter_contacts),
        "pdb_6vcd_closest_interface_contacts": sorted(inter_contacts, key=lambda x: x["min_dist_A"])[:12],
        "pdb_3v5z_hemerythrin_diiron_coordinating_residues_le_3p2A": diiron_ligs,
    }


def summarize_gtf_isoforms(gene: str) -> list[dict[str, Any]]:
    raw_txt = (CACHE / f"gtf_{gene}.json").read_text(encoding="utf-8")
    raw = json.loads(raw_txt[raw_txt.index("[") :])
    txs = raw if isinstance(raw, list) else raw.get("transcripts", [raw])
    out = []
    for tx in txs:
        exs = tx.get("exons", [])
        cds = tx.get("cds", [])
        cds_bp = sum(int(c.get("width", int(c["end"]) - int(c["start"]) + 1)) for c in cds)
        out.append({
            "transcript_id": tx.get("transcript_id"),
            "is_mane_select": bool(tx.get("is_mane_select", False)),
            "strand": tx.get("strand"),
            "span_1b": f"{tx.get('chromosome')}:{tx.get('start')}-{tx.get('end')}",
            "num_exons": int(tx.get("num_exons", len(exs))),
            "cds_aa_est": int(cds_bp // 3) if cds_bp else 0,
            "terminal_exon_1b": f"{tx.get('chromosome')}:{exs[-1]['start']}-{exs[-1]['end']}" if exs else "",
        })
    return out


def main() -> None:
    panel = [
        "CHMP7", "CHMP2B", "SUN1", "XPO1", "ANXA11", "VPS4A", "VPS4B",
        "FBXL5", "IREB2", "TFRC", "FTH1", "FTL", "ACO1", "SLC40A1", "CP",
        "DNAJB2", "SNPH", "NEFH", "NEFM", "APP", "BSN", "STX1A", "SNAP25", "FOS", "ARC", "BDNF",
    ]
    sp_ctx = load_spillman2026_fractions(panel)
    sp_m3 = load_spillman_moesm3_ipsc_pellet(panel)
    ed_cells = {
        ct: load_edinburgh_pseudobulk(ct, ["CHMP7", "CHMP2B", "FBXL5", "IREB2", "TFRC", "FTH1", "FTL", "DNAJB2", "SNPH"], region="donor_collapsed")["stats"]
        for ct in ("Excitatory neuron", "Microglia", "Astrocyte", "Oligodendrocyte")
    }
    p_ba4_exc = load_pineda2024_pseudobulk("BA4", "Excitatory", ["CHMP7", "CHMP2B", "ANXA11", "FBXL5", "IREB2", "TFRC", "FTH1", "DNAJB2", "SNPH", "FOS", "ARC", "BDNF"])
    p_ba9_exc = load_pineda2024_pseudobulk("BA9", "Excitatory", ["CHMP7", "CHMP2B", "FBXL5", "DNAJB2", "SNPH"])
    p_ba4_oli = load_pineda2024_pseudobulk("BA4", "Oligo", ["DNAJB2", "FBXL5", "FTH1", "FTL"])
    p_ba9_oli = load_pineda2024_pseudobulk("BA9", "Oligo", ["DNAJB2", "FBXL5", "FTH1", "FTL"])
    p_ba4_mic = load_pineda2024_pseudobulk("BA4", "Micro", ["FBXL5", "IREB2", "TFRC", "FTH1", "FTL"])
    p_ba4_l23 = load_pineda2024_pseudobulk("BA4", "L2_L3", ["SNPH", "DNAJB2"])

    df_ba4 = p_ba4_exc["donor_df"]
    r_ch7_bdnf, p_ch7_bdnf = stats.pearsonr(df_ba4["CHMP7"], df_ba4["BDNF"])
    r_ch2b_anxa, p_ch2b_anxa = stats.pearsonr(df_ba4["CHMP2B"], df_ba4["ANXA11"])

    bye = load_bye2025_screen()
    def_row = bye.loc[bye["drug"].str.contains("Deferiprone", case=False, na=False)].to_dict(orient="records")
    zh = load_zhang2026_spatial(["CHMP7", "CHMP2B", "FBXL5", "IREB2", "TFRC", "FTH1", "FTL", "CP", "DNAJB2", "SNPH", "NEFH", "APP", "BSN"])

    out = {
        "analysis_run_id": "RUN-P2-T4-002",
        "spillman2026_4fraction_matrix": {g: {**sp_ctx.get(g, {}), "moesm3_ipsc": sp_m3.get(g, {})} for g in panel},
        "edinburgh_celltype_split": ed_cells,
        "pineda_compartment_split": {
            "BA4_Excitatory": p_ba4_exc["stats"],
            "BA9_Excitatory": p_ba9_exc["stats"],
            "BA4_Oligo": p_ba4_oli["stats"],
            "BA9_Oligo": p_ba9_oli["stats"],
            "BA4_Micro": p_ba4_mic["stats"],
            "BA4_L2_L3": p_ba4_l23["stats"],
        },
        "c014_neuronal_coexpression_ba4_n32": {
            "CHMP7_vs_BDNF": {"r": round(float(r_ch7_bdnf), 4), "p": float(p_ch7_bdnf)},
            "CHMP2B_vs_ANXA11": {"r": round(float(r_ch2b_anxa), 4), "p": float(p_ch2b_anxa)},
        },
        "c016_fbxl5_atomic_structures_6vcd_and_3v5z": analyze_fbxl5_structures(),
        "c016_bye2025_deferiprone_benchmark": def_row,
        "zhang2026_cervical_spatial": {"mn_6d": zh["mn_niche_df"].to_dict("records"), "tdp43_6i": zh["tdp43_niche_df"].to_dict("records")},
        "gencode_v46_isoform_coordinates_1based_grch38": {g: summarize_gtf_isoforms(g) for g in ("CHMP7", "CHMP2B", "DNAJB2", "SNPH")},
        "c020_v040_pulsed_pkpd_sensitivity_81grid": {
            "q48h_6p5nM": sweep_pulsed_pkpd_sensitivity([float(h) for h in range(0, 336, 48)], 336.0, 6.5, 4.5, 1.5),
            "q72h_8p0nM": sweep_pulsed_pkpd_sensitivity([0.0, 72.0, 144.0, 216.0, 288.0], 336.0, 8.0, 4.5, 1.5),
            "continuous_125mg_BID_3p89nM": sweep_pulsed_pkpd_sensitivity([float(h) for h in range(0, 336, 12)], 336.0, 3.89, 4.5, 1.5),
        },
    }
    (OUT_DIR / "run_p2_t4_002_c014_c016_ba9_compartments.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("SAVED run_p2_t4_002_c014_c016_ba9_compartments.json")


if __name__ == "__main__":
    main()
