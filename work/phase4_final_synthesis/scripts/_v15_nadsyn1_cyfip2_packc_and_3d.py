"""3D mmCIF structural dissection, GENCODE v46 exon-to-protein mapping, and Pack C replication summary for RUN-P4-006."""
from __future__ import annotations

import gzip
import hashlib
from pathlib import Path
import re
from typing import Any

import numpy as np
import pandas as pd

from carbon_als.loaders import download_https_structure, resolve_dataset_path
from carbon_als.mmcif_parser import ParsedMMCIF, load_mmcif_structure

PDB_V15_SPECS: tuple[tuple[str, str, str, str], ...] = (
    ("pdb_00006ofb.cif", "6OFB", "NADSYN1", "https://files.rcsb.org/download/6OFB.cif"),
    ("pdb_00003p8c.cif", "3P8C", "CYFIP1_WRC_PARALOG", "https://files.rcsb.org/download/3P8C.cif"),
    ("AF-Q6IA69-F1-model_v6.cif", "AF-Q6IA69-F1", "NADSYN1", "https://alphafold.ebi.ac.uk/files/AF-Q6IA69-F1-model_v6.cif"),
    ("AF-Q96F07-F1-model_v6.cif", "AF-Q96F07-F1", "CYFIP2", "https://alphafold.ebi.ac.uk/files/AF-Q96F07-F1-model_v6.cif"),
)


def _contig_ranges(seq_ids: list[int]) -> list[str]:
    if not seq_ids:
        return []
    s = sorted(set(seq_ids))
    spans: list[str] = []
    lo = hi = s[0]
    for v in s[1:]:
        if v == hi + 1:
            hi = v
        else:
            spans.append(f"{lo}-{hi}" if lo != hi else f"{lo}")
            lo = hi = v
    spans.append(f"{lo}-{hi}" if lo != hi else f"{lo}")
    return spans


def _ligand_contacts(st: ParsedMMCIF, lig_comp: str, cutoff_a: float = 4.0) -> list[dict[str, Any]]:
    lig_pts = np.array([a.coord for a in st.ligand_atoms if a.comp_id == lig_comp], dtype=float)
    if len(lig_pts) == 0:
        return []
    hits: list[dict[str, Any]] = []
    for (ch, seq_id, resn), atoms in sorted(st.residue_groups(include_modified=True).items()):
        pts = np.array([a.coord for a in atoms], dtype=float)
        dmin = float(np.min(np.linalg.norm(pts[:, None, :] - lig_pts[None, :, :], axis=2)))
        if dmin <= cutoff_a:
            hits.append({"chain": ch, "auth_seq_id": seq_id, "resn": resn, "min_dist_A": round(dmin, 2)})
    return hits


def map_gencode_mane_exons(genes: set[str]) -> dict[str, dict[str, Any]]:
    """Extract MANE_Select exon and CDS residue boundaries from DS_GENCODE_V46_COMP_GTF."""
    gtf_fp = resolve_dataset_path("DS_GENCODE_V46_COMP_GTF", verify_hash=True)
    tx_info: dict[str, dict[str, Any]] = {}
    with gzip.open(gtf_fp, "rt", encoding="utf-8") as fh:
        for ln in fh:
            if ln.startswith("#"):
                continue
            pts = ln.rstrip("\n").split("\t")
            if len(pts) < 9 or pts[2] not in {"transcript", "exon", "CDS"}:
                continue
            attr = pts[8]
            if 'tag "MANE_Select"' not in attr:
                continue
            mg = re.search(r'gene_name "([^"]+)"', attr)
            if not mg or mg.group(1) not in genes:
                continue
            g = mg.group(1)
            mt = re.search(r'transcript_id "([^"]+)"', attr)
            me = re.search(r'gene_id "([^"]+)"', attr)
            rec = tx_info.setdefault(g, {"gene_id": me.group(1) if me else "", "mane_tx": mt.group(1) if mt else "", "chrom": pts[0], "strand": pts[6], "exons": [], "cds": []})
            lo, hi = int(pts[3]), int(pts[4])
            if pts[2] == "exon":
                mn = re.search(r'exon_number (\d+)', attr)
                rec["exons"].append({"exon_number": int(mn.group(1)) if mn else 0, "start": lo, "end": hi, "len_bp": hi - lo + 1})
            elif pts[2] == "CDS":
                rec["cds"].append({"start": lo, "end": hi, "len_bp": hi - lo + 1})
    for g, rec in tx_info.items():
        rev = rec["strand"] == "-"
        rec["exons"].sort(key=lambda x: x["start"], reverse=rev)
        rec["cds"].sort(key=lambda x: x["start"], reverse=rev)
        cum_nt = 0
        for c in rec["cds"]:
            aa_start = cum_nt // 3 + 1
            cum_nt += c["len_bp"]
            aa_end = (cum_nt + 2) // 3
            c["aa_start"] = aa_start
            c["aa_end"] = aa_end
        rec["total_cds_nt"] = cum_nt
        rec["total_aa"] = cum_nt // 3
    return tx_info


def analyze_v15_structures(root: Path) -> dict[str, Any]:
    pdb_dir = root / "data" / "pharmacology_structures" / "phase5_pdb"
    out: dict[str, Any] = {}
    for fname, sid, gene, url in PDB_V15_SPECS:
        fp = pdb_dir / fname
        if not fp.is_file():
            sz, sha = download_https_structure(url, fp)
        else:
            raw = fp.read_bytes()
            sz, sha = len(raw), hashlib.sha256(raw).hexdigest()
        txt = fp.read_text(encoding="utf-8", errors="replace")
        res_m = re.findall(r"_(?:refine\.ls_d_res_high|em_3d_reconstruction\.resolution)\s+([0-9.]+)", txt)
        st = load_mmcif_structure(fp)
        chains = sorted({a.chain_id for a in st.polymer_atoms})
        chain_spans = {
            ch: {
                "n_resolved_residues": len({k[1] for k in st.residue_groups(chain_id=ch)}),
                "resolved_auth_spans": _contig_ranges([k[1] for k in st.residue_groups(chain_id=ch)]),
            }
            for ch in chains
        }
        lig_codes = sorted({a.comp_id for a in st.ligand_atoms if a.comp_id not in {"HOH", "SO4", "GOL", "EDO", "CL", "NA", "PO4", "ACT", "DMS"}})
        rec: dict[str, Any] = {
            "structure_id": sid, "target_gene": gene,
            "local_relpath": fp.relative_to(root).as_posix(), "size_bytes": sz, "sha256": sha,
            "resolution_A": float(res_m[0]) if res_m else None,
            "n_chains": len(chains), "chains": chain_spans,
            "non_solvent_ligands": lig_codes,
        }
        if sid == "6OFB":
            # Chain A contacts for clean stoichiometry summary (octamer has 8 symmetric chains A-H)
            a_contacts: dict[str, list[dict[str, Any]]] = {}
            for lc in lig_codes:
                all_c = _ligand_contacts(st, lc, 4.0)
                a_contacts[lc] = [c for c in all_c if c["chain"] == "A"]
            rec["chain_A_ligand_contacts_le_4A"] = a_contacts
            rec["total_ligand_contacts_le_4A_all_chains"] = {lc: len(_ligand_contacts(st, lc, 4.0)) for lc in lig_codes}
        elif sid.startswith("AF-"):
            ca = [a for a in st.polymer_atoms if a.atom_name == "CA"]
            plddt = np.array([a.b_iso_or_plddt for a in ca], dtype=float)
            rec["afdb_plddt"] = {
                "n_ca_residues": int(len(ca)),
                "mean_plddt": round(float(plddt.mean()), 2),
                "pct_high_conf_ge70": round(float((plddt >= 70.0).mean() * 100.0), 2),
                "pct_very_high_ge90": round(float((plddt >= 90.0).mean() * 100.0), 2),
            }
            if sid == "AF-Q96F07-F1":
                r87 = next((a.b_iso_or_plddt for a in ca if a.seq_id == 87), None)
                rec["afdb_plddt"]["Arg87_DEE65_hotspot_plddt"] = round(float(r87), 2) if r87 is not None else None
        out[sid] = rec
    return out


def collect_pack_c_summary(root: Path) -> dict[str, Any]:
    """Read verified Pack C primary loaders and Phase 2/3 outputs when staged on disk."""
    p5_out = root / "work" / "phase5_pack_c_expansion" / "outputs"
    if not (root / "data" / "expansion_2026_11").is_dir():
        return {"staged_locally": False}
    from carbon_als.loaders import expansion_loaders as el  # noqa: PLC0415

    genes_focus = ["NADSYN1", "CYFIP2", "CYFIP1", "NAMPT", "NMNAT2", "AKR1B1", "MEGF10", "CGAS", "IL1RL1"]
    spit_by_reg: dict[str, list[dict[str, Any]]] = {}
    for reg in ("all", "Cervical", "Lumbar", "Mcx", "Thor", "Cerv", "Lumb"):
        try:
            spit_by_reg[reg] = el.load_spiteri2025_4region_proteomics(region=reg, genes=genes_focus)["df"].to_dict(orient="records")
        except ValueError:
            continue
    koz_s1 = el.load_kozareva2025_compendium("S1", genes=["NADSYN1", "CYFIP2", "CYFIP1", "AKR1B1"])["df"]
    koz_s6 = el.load_kozareva2025_compendium("S6", genes=["NADSYN1", "CYFIP2", "CYFIP1"])["df"]
    mied = el.load_miedema2025_ftld_tdp_c(genes=["NADSYN1", "CYFIP2", "CYFIP1", "AKR1B1"])["df"]
    keuss_n = el.load_keuss2025_soma_neurite(fraction="Neurite", genes=["NADSYN1", "CYFIP2"])["stats"]
    keuss_s = el.load_keuss2025_soma_neurite(fraction="Soma", genes=["NADSYN1", "CYFIP2"])["stats"]
    tian_p = el.load_crisprbrain_screens("tian2021_survival_plusao", genes=["NADSYN1", "CYFIP2", "CYFIP1"])["df"]
    tian_n = el.load_crisprbrain_screens("tian2021_survival_noao", genes=["NADSYN1", "CYFIP2", "CYFIP1"])["df"]
    drager = el.load_drager2022_microglia_crispr(genes=["AKR1B1", "NADSYN1", "CYFIP2"])["df"]
    fene_na = el.load_feneberg2025_oxford_proteomics("SPC insoluble", "ALS vs non-ALS", genes=["AKR1B1", "NADSYN1", "CYFIP2"])["df"]
    fene_hc = el.load_feneberg2025_oxford_proteomics("SPC insoluble", "ALS vs control", genes=["AKR1B1", "NADSYN1", "CYFIP2"])["df"]

    bolger_res: dict[str, list[dict[str, Any]]] = {}
    for split in ("nygc_transcript", "i3n_transcript"):
        bdf = el.load_bolger2026_isoseq(split, ensembl_ids=["ENSG00000172890", "ENSG00000055163"])["df"]
        if not bdf.empty:
            bolger_res[split] = bdf.head(20).to_dict(orient="records")

    pb_checks: dict[str, dict[str, Any]] = {}
    for key, cohort, ct in (
        ("nygc_lsc_visium_vent_horn", "nygc_gse330224_lsc_visium", "Vent_Horn"),
        ("nygc_lsc_snrna_motor_neurons", "nygc_gse330130_lsc", "Motor_Neurons"),
        ("nygc_lsc_snrna_microglia", "nygc_gse330130_lsc", "Microglia"),
        ("zelic_cervical_neuron", "zelic2025_cervical_sc", "Neuron"),
        ("zelic_cervical_microglia", "zelic2025_cervical_sc", "Microglia"),
    ):
        r = el.load_expansion_pseudobulk(cohort, ct, genes=["NADSYN1", "CYFIP2", "AKR1B1", "CGAS"])
        pb_checks[key] = {"n_als": r.get("n_als"), "n_ctrl": r.get("n_ctrl"), "stats": r.get("stats", {})}

    cal_df = pd.read_csv(p5_out / "phase3" / "phase3_calibration_53_benchmark.csv")
    n_drop_total = int((cal_df["v14_decision"] == "DROP").sum())
    n_drop_pass = int(((cal_df["v14_decision"] == "DROP") & (cal_df["qualifies_gate"] == True)).sum())  # noqa: E712
    t24 = pd.read_csv(p5_out / "phase2_track24_biofluid_proteomics.csv")
    t25 = pd.read_csv(p5_out / "phase2_track25_hop2026_exome.csv")
    t26 = pd.read_csv(p5_out / "phase2_track26_takeda_pbmc.csv")
    t21 = pd.read_csv(p5_out / "phase2_track21_22_cns_vascular.csv")
    f3 = pd.read_csv(p5_out / "phase3" / "phase3_f3_proteomics.csv")
    return {
        "staged_locally": True,
        "spiteri2025_4region_tmtpro": spit_by_reg,
        "kozareva2025_s1_ineuron": koz_s1.to_dict(orient="records"),
        "kozareva2025_s6_splicing": koz_s6.to_dict(orient="records"),
        "miedema2025_ftld_tdp_c": mied.to_dict(orient="records"),
        "dargan_keuss2025_neurite": keuss_n,
        "dargan_keuss2025_soma": keuss_s,
        "bolger2026_isoseq": bolger_res,
        "spinal_spatial_snrna_pseudobulk": pb_checks,
        "tian2021_neuron_crispri_plusao": tian_p.to_dict(orient="records"),
        "tian2021_neuron_crispri_noao": tian_n.to_dict(orient="records"),
        "drager2022_microglia_crispr": drager.to_dict(orient="records"),
        "feneberg2025_spinal_insoluble_vs_nonals": fene_na.to_dict(orient="records"),
        "feneberg2025_spinal_insoluble_vs_ctrl": fene_hc.to_dict(orient="records"),
        "phase3_v2_calibration_lock": {
            "n_drop_evaluated": n_drop_total,
            "n_drop_qualifying_novel_gate": n_drop_pass,
            "core_passing": cal_df.loc[(cal_df["v14_decision"] == "KEEP_CORE") & (cal_df["qualifies_gate"] == True), "gene_or_drug"].tolist(),  # noqa: E712
        },
        "crosslink_eals007_il1rl1_biofluid": t24.loc[t24["gene"] == "IL1RL1"].to_dict(orient="records"),
        "crosslink_eals007_il1rl1_omar": t21.loc[(t21["gene"] == "IL1RL1") & t21["cohort_key"].str.contains("omar", case=False, na=False)].to_dict(orient="records"),
        "crosslink_eals031_il2ra_biofluid": t24.loc[t24["gene"].isin(["IL2RA", "FOXP3"])].to_dict(orient="records"),
        "crosslink_eals031_053_takeda_pbmc": t26.loc[t26["gene"].isin(["CGAS", "FOXP3", "IL2RA", "STING1"])].to_dict(orient="records"),
        "crosslink_megf10_prefals": f3.loc[f3["gene"] == "MEGF10"].to_dict(orient="records"),
        "crosslink_hop2026_exome_ref": t25.loc[t25["gene"].isin(["SCFD1", "G2E3", "UNC13C", "TTC3", "YKT6", "NADSYN1", "CYFIP2"])].to_dict(orient="records"),
    }
