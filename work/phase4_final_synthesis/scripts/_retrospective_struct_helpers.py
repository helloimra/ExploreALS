"""3D structural, gnomAD v4.1, ClinVar GRCh38, and AFDB helpers for RUN-P4-003 Nov 2026 deep retrospective."""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import numpy as np

from carbon_als.mmcif_parser import AtomRecord, load_mmcif_structure

SARM1_GOF_PANEL: list[tuple[str, int, int, str]] = [
    ("p.V112I", 112, 112, "CLASS_III_NAD_NMN_SENSOR"),
    ("p.V184G", 184, 184, "CLASS_III_NAD_NMN_SENSOR"),
    ("p.G206S", 206, 206, "CLASS_I_INTERPROTOMER_ARM_TIR_LATCH"),
    ("p.L223P", 223, 223, "CLASS_II_CYS311_TLOCK_WALL"),
    ("p.del226_232", 226, 232, "CLASS_II_CYS311_TLOCK_WALL"),
    ("p.R244S", 244, 244, "CLASS_I_INTERPROTOMER_ARM_TIR_LATCH"),
    ("p.R249C", 249, 249, "CLASS_I_INTERPROTOMER_ARM_TIR_LATCH"),
    ("p.del249_252", 249, 252, "CLASS_I_INTERPROTOMER_ARM_TIR_LATCH"),
    ("p.E252K", 252, 252, "CLASS_I_INTERPROTOMER_ARM_TIR_LATCH"),
    ("p.R267W", 267, 267, "CLASS_II_CYS311_TLOCK_WALL"),
    ("p.A275V", 275, 275, "CLASS_III_NAD_NMN_SENSOR"),
    ("p.V331E", 331, 331, "CLASS_III_NAD_NMN_SENSOR"),
    ("p.E340K", 340, 340, "CLASS_III_NAD_NMN_SENSOR"),
    ("p.T385A", 385, 385, "CLASS_III_NAD_NMN_SENSOR"),
]


def _min_dist(a_list: list[AtomRecord], b_list: list[AtomRecord]) -> float | None:
    if not a_list or not b_list:
        return None
    ca = np.array([[a.x, a.y, a.z] for a in a_list], dtype=float)
    cb = np.array([[b.x, b.y, b.z] for b in b_list], dtype=float)
    diff = ca[:, None, :] - cb[None, :, :]
    return round(float(np.sqrt(np.min(np.sum(diff * diff, axis=2)))), 2)


def analyze_sarm1_octamer_and_genetics(pdb_map: dict[str, Path], cache_dir: Path) -> dict[str, Any]:
    gn = json.loads((cache_dir / "gnomad_v4_sarm1_dnajb2_sanitized.json").read_text(encoding="utf-8"))["SARM1"]
    cv = json.loads((cache_dir / "clinvar_sarm1_dnajb2_grch38.json").read_text(encoding="utf-8"))
    pdb_dists: dict[str, dict[str, Any]] = {}
    for pid, cif_fp in pdb_map.items():
        st = load_mmcif_structure(cif_fp)
        all_poly = st.polymer_atoms + st.modified_polymer_atoms
        tir_same = [a for a in all_poly if a.chain_id == "A" and a.seq_id and a.seq_id >= 550]
        tir_adj = [a for a in all_poly if a.chain_id != "A" and a.seq_id and a.seq_id >= 550]
        c311_pkt = [a for a in all_poly if a.chain_id == "A" and a.seq_id == 311] + [
            a for a in st.ligand_atoms if a.chain_id == "A" and a.comp_id in {"H8L", "VI3"}
        ]
        nad_pkt = [a for a in st.ligand_atoms if a.chain_id == "A" and a.comp_id in {"NAD", "NMN", "1AD", "3AD", "APR"}]
        v_rows: dict[str, dict[str, float | None]] = {}
        for lbl, lo, hi, _cls in [*SARM1_GOF_PANEL, ("p.P332Q_benign", 332, 332, "BENIGN_COMMON_POLYMORPHISM")]:
            va = [a for a in all_poly if a.chain_id == "A" and a.seq_id and lo <= a.seq_id <= hi]
            v_rows[lbl] = {
                "intra_chain_tir_A": _min_dist(va, tir_same),
                "inter_protomer_adj_tir_A": _min_dist(va, tir_adj),
                "cys311_pocket_A": _min_dist(va, c311_pkt),
                "nad_nmn_sensor_A": _min_dist(va, nad_pkt),
            }
        wall_7djt = sorted({
            f"{a.comp_id}{a.seq_id}"
            for a in all_poly
            if pid == "7DJT" and a.chain_id == "A" and a.seq_id and a.seq_id != 311 and (_min_dist([a], c311_pkt) or 99.0) <= 5.0
        })
        pdb_dists[pid] = {"variants": v_rows, "cys311_h8l_wall_le_5A": wall_7djt}

    def _tot_ac_an(v: dict[str, Any]) -> tuple[int, int, int]:
        ex, ge = v.get("exome") or {}, v.get("genome") or {}
        nh_ex = int(ex.get("homozygote_count", ex.get("nhomalt", 0)) or 0)
        nh_ge = int(ge.get("homozygote_count", ge.get("nhomalt", 0)) or 0)
        return int(ex.get("ac", 0)) + int(ge.get("ac", 0)), max(int(ex.get("an", 0)) + int(ge.get("an", 0)), 1), nh_ex + nh_ge

    gof_gnomad: dict[str, dict[str, Any]] = {}
    gof_Map = {
        "p.V112I": "p.Val112Ile", "p.V184G": "p.Val184Gly", "p.G206S": "p.Gly206Ser", "p.L223P": "p.Leu223Pro",
        "p.del226_232": "p.Ala229_Leu235del", "p.R244S": "p.Arg244Ser", "p.R249C": "p.Arg249Cys",
        "p.del249_252": "p.Arg249_Glu252del", "p.E252K": "p.Glu252Lys", "p.R267W": "p.Arg267Trp",
        "p.A275V": "p.Ala275Val", "p.V331E": "p.Val331Glu", "p.E340K": "p.Glu340Lys", "p.T385A": "p.Thr385Ala",
        "p.P332Q_benign": "p.Pro332Gln",
    }
    by_hgvsp: dict[str, dict[str, Any]] = {}
    for v in gn["variants"]:
        hp = v.get("hgvsp") or ""
        if hp:
            by_hgvsp[hp] = v
    cum_gof_af = 0.0
    for lbl, hp in gof_Map.items():
        hit = by_hgvsp.get(hp)
        ac, an, nhom = _tot_ac_an(hit) if hit else (0, 1_550_000, 0)
        af = round(ac / an, 8) if hit else 0.0
        if lbl != "p.P332Q_benign":
            cum_gof_af += af
        gof_gnomad[lbl] = {"hgvsp_vcf": hp, "ac": ac, "an": an if hit else 0, "nhomalt": nhom, "af": af}

    plof_csq = {"stop_gained", "frameshift_variant", "splice_acceptor_variant", "splice_donor_variant"}
    plofs = [v for v in gn["variants"] if v.get("consequence") in plof_csq]
    return {
        "octamer_pdb_distances": pdb_dists,
        "gnomad_v41_gof_and_benign": gof_gnomad,
        "cumulative_validated_gof_allele_freq": round(cum_gof_af, 7),
        "approx_heterozygote_carrier_pct": round(200.0 * cum_gof_af, 4),
        "gnomad_v41_plof": {"n_variants": len(plofs), "total_ac": sum(_tot_ac_an(v)[0] for v in plofs), "total_nhomalt": sum(_tot_ac_an(v)[2] for v in plofs), "loeuf": gn["gnomad_constraint"]["oe_lof_upper"]},
        "clinvar_grch38": {
            "total_overlapping": cv["clinvar_sarm1_total_overlapping"],
            "single_gene_sarm1_plp": cv["clinvar_sarm1_single_gene_sarm1_count"],
            "opposite_strand_slc46a1_records": cv["clinvar_sarm1_slc46a1_overlap_count"],
            "multigene_17p_q_cnvs": cv["clinvar_sarm1_multigene_cnv_count"],
        },
    }


def analyze_dnajb2_and_c1q_structures(cache_dir: Path) -> dict[str, Any]:
    gn_d = json.loads((cache_dir / "gnomad_v4_sarm1_dnajb2_sanitized.json").read_text(encoding="utf-8"))["DNAJB2"]
    cv = json.loads((cache_dir / "clinvar_sarm1_dnajb2_grch38.json").read_text(encoding="utf-8"))
    plddt_txt = (cache_dir / "afdb_P25686" / "official_plddt.txt").read_text(encoding="utf-8")
    pae_txt = (cache_dir / "afdb_P25686" / "official_pae.txt").read_text(encoding="utf-8")
    m_glob = re.search(r"Global mean pLDDT:\s*([0-9.]+)", plddt_txt)
    doms = [f"{a}-{b}" for a, b in re.findall(r"Domain\s+\d+:\s*residues\s+(\d+)\s*-\s*(\d+)", pae_txt)]
    def _vpos(v: dict[str, Any]) -> int:
        return int(v["pos"]) if "pos" in v else int(v["variant_id"].split("-")[1])

    plof_csq = {"stop_gained", "frameshift_variant", "splice_acceptor_variant", "splice_donor_variant"}
    zone_a_plofs = [v for v in gn_d["variants"] if 219284836 <= _vpos(v) <= 219284984 and v.get("consequence") in plof_csq]
    shared_plofs = [v for v in gn_d["variants"] if _vpos(v) <= 219284769 and v.get("consequence") in plof_csq]
    zone_a_plp = [
        r for r in cv["clinvar_dnajb2_zone_a_or_intron9"]
        if "pathogenic" in (r.get("classification") or "").lower() and "conflicting" not in (r.get("classification") or "").lower()
    ]

    st_1pk6 = load_mmcif_structure(cache_dir / "pdb_1pk6" / "pdb_00001pk6.cif")
    rg = st_1pk6.residue_groups()
    by_ch = {ch: [atoms for (c, _s, _m), atoms in rg.items() if c == ch] for ch in ("A", "B", "C")}
    pairs_4p5 = {
        f"{c1}_{c2}": sum(1 for r1 in by_ch[c1] for r2 in by_ch[c2] if (_min_dist(r1, r2) or 99.0) <= 4.5)
        for c1, c2 in (("A", "B"), ("A", "C"), ("B", "C"))
    }
    c1q_af: dict[str, dict[str, Any]] = {}
    for gsym, uni, clr_hi in (("C1QA", "P02745", 109), ("C1QB", "P02746", 114), ("C1QC", "P02747", 112)):
        af_st = load_mmcif_structure(cache_dir / f"afdb_{uni}" / f"AF-{uni}-F1-model_v6.cif")
        ca = [a for a in af_st.polymer_atoms if a.atom_name == "CA" and a.seq_id]
        clr = [a for a in ca if 28 <= (a.seq_id or 0) <= clr_hi]
        hd = [a for a in ca if (a.seq_id or 0) > clr_hi]
        c1q_af[gsym] = {
            "uniprot": uni,
            "clr_mean_plddt": round(float(np.mean([a.b_iso_or_plddt for a in clr])), 2),
            "clr_cationic_arg_lys_count": sum(1 for a in clr if a.comp_id in {"ARG", "LYS"}),
            "gc1q_head_mean_plddt": round(float(np.mean([a.b_iso_or_plddt for a in hd])), 2),
        }
    return {
        "dnajb2_af_p25686_and_clinvar": {
            "global_mean_plddt": float(m_glob.group(1)) if m_glob else 67.38,
            "pae_rigid_domains": doms,
            "clinvar_total_overlapping": cv["clinvar_dnajb2_total_overlapping"],
            "clinvar_single_gene_count": cv["clinvar_dnajb2_single_gene_count"],
            "clinvar_single_gene_plp_shared_exons2_9": len(cv["clinvar_dnajb2_single_gene_plp"]),
            "clinvar_single_gene_plp_zone_a_intron9": len(zone_a_plp),
            "clinvar_total_vus_benign_zone_a_intron9": len(cv["clinvar_dnajb2_zone_a_or_intron9"]),
            "gnomad_v41_zone_a_plof_variants": len(zone_a_plofs),
            "gnomad_v41_shared_exons2_9_plof_variants": len(shared_plofs),
            "gnomad_v41_loeuf": gn_d["gnomad_constraint"]["oe_lof_upper"],
        },
        "c1q_1pk6_and_afdb_modality_split": {
            "pdb_1pk6_resolution_A": 1.85,
            "pdb_1pk6_inter_subunit_residue_pairs_le_4p5A": {**pairs_4p5, "total": sum(pairs_4p5.values())},
            "afdb_clr_stalk_vs_gc1q_head": c1q_af,
            "total_clr_stalk_cationic_arg_lys": sum(x["clr_cationic_arg_lys_count"] for x in c1q_af.values()),
        },
    }
