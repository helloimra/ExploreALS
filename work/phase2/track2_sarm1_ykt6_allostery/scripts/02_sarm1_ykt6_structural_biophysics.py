"""RUN-P2-T2-001: Atomic 3D structural & biophysical dissection of SARM1 (7DJT/7ANW/7NAL/9TZY) and YKT6 (3KYQ/AF-O15498/6J74)."""

from __future__ import annotations

import json
import math
from pathlib import Path
import re
import numpy as np

TOKEN_RE = re.compile(r"'[^']*'|\"[^\"]*\"|\S+")

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "work" / "phase2" / "track2_sarm1_ykt6_allostery" / "outputs"
P2_PDB = ROOT / "data" / "pharmacology_structures" / "phase2_pdb"
P1_PDB = ROOT / "data" / "pharmacology_structures" / "pdb"
AFDB = ROOT / "data" / "pharmacology_structures" / "afdb"

ALS_SARM1_GOF_SITES = [99, 112, 223, 226, 232, 249, 252, 267, 275, 331, 340, 385]


def parse_cif_atoms(cif_path: Path) -> list[dict]:
    lines = cif_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    cols: list[str] = []
    atoms: list[dict] = []
    in_atom = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("_atom_site."):
            in_atom = True
            cols.append(s.split(".", 1)[1].strip())
            continue
        if in_atom:
            if not s or s.startswith("#") or s.startswith("loop_") or s.startswith("_"):
                if atoms:
                    break
                in_atom = False
                cols = []
                continue
            parts = [t.strip("'\"") for t in TOKEN_RE.findall(s)]
            if len(parts) != len(cols):
                continue
            rec = dict(zip(cols, parts))
            if rec.get("pdbx_PDB_model_num", "1") not in {"1", "?"}:
                continue
            if rec.get("label_alt_id", ".") not in {".", "?", "A"}:
                continue
            try:
                seq = int(rec.get("auth_seq_id") or rec.get("label_seq_id"))
            except ValueError:
                seq = -1
            atoms.append({
                "group": rec.get("group_PDB", "ATOM"),
                "atom": rec.get("auth_atom_id") or rec.get("label_atom_id"),
                "comp": rec.get("auth_comp_id") or rec.get("label_comp_id"),
                "chain": rec.get("auth_asym_id") or rec.get("label_asym_id"),
                "seq": seq,
                "xyz": np.array([float(rec["Cartn_x"]), float(rec["Cartn_y"]), float(rec["Cartn_z"])]),
                "b": float(rec.get("B_iso_or_equiv", 0.0)),
            })
    return atoms


def kabsch_rmsd(P: np.ndarray, Q: np.ndarray) -> float:
    Pc, Qc = P - P.mean(axis=0), Q - Q.mean(axis=0)
    C = Pc.T @ Qc
    V, S, Wt = np.linalg.svd(C)
    d = 1.0 if np.linalg.det(V @ Wt) >= 0 else -1.0
    U = V @ np.diag([1.0, 1.0, d]) @ Wt
    diff = Pc @ U - Qc
    return float(np.sqrt((diff * diff).sum() / len(P)))


def min_dist(a_list: list[dict], b_list: list[dict]) -> float:
    if not a_list or not b_list:
        return float("nan")
    A = np.array([x["xyz"] for x in a_list])
    B = np.array([x["xyz"] for x in b_list])
    D = np.linalg.norm(A[:, None, :] - B[None, :, :], axis=-1)
    return float(D.min())


def analyze_sarm1() -> dict:
    a7djt = parse_cif_atoms(P2_PDB / "pdb_00007djt.cif")
    a7anw = parse_cif_atoms(P2_PDB / "pdb_00007anw.cif")
    a7nal = parse_cif_atoms(P2_PDB / "pdb_00007nal.cif")
    a9tzy = parse_cif_atoms(P2_PDB / "pdb_00009tzy.cif")

    # 1. 7DJT Cys311 (covalently modified VI3 at seq=311 + H8L at seq=1001) on Chain A
    pchain = "A"
    prot_a = [x for x in a7djt if x["chain"] == pchain and (x["group"] == "ATOM" or x["seq"] == 311)]
    c311_atoms = [x for x in a7djt if x["chain"] == pchain and x["seq"] == 311]
    c311_sg = [x for x in c311_atoms if x["atom"] == "SG"]
    h8l_chain_a = [x for x in a7djt if x["chain"] == pchain and x["comp"] == "H8L"]
    lig_site = h8l_chain_a + [x for x in c311_atoms if x["atom"] not in {"N", "CA", "C", "O", "CB", "SG"}]
    c311_h8l_d = min_dist(c311_sg, h8l_chain_a)

    pocket_res = sorted({
        (x["seq"], x["comp"]) for x in prot_a
        if x["seq"] != 311 and min_dist([x], lig_site or c311_sg) <= 5.0
    })
    als_dists = {}
    nad_sensor = [x for x in prot_a if x["seq"] in {103, 110, 157, 193} and x["atom"] == "CA"]
    c311_ca = [x for x in c311_atoms if x["atom"] == "CA"]
    for r in ALS_SARM1_GOF_SITES:
        rca = [x for x in prot_a if x["seq"] == r and x["atom"] == "CA"]
        if rca:
            als_dists[f"res_{r}_{rca[0]['comp']}"] = {
                "dist_to_Cys311_CA_A": round(min_dist(rca, c311_ca), 2),
                "min_dist_to_NAD_NMN_sensor_CA_A": round(min_dist(rca, nad_sensor), 2),
            }

    # 2. ARM closure across 7DJT (Cys311-locked T), 7ANW (NAD+ T), 7NAL (NMN R)
    confs = {}
    ca_maps = {}
    for label, atoms in [("7DJT_Cys311_dHNN", a7djt), ("7ANW_NAD_autoinhib", a7anw), ("7NAL_NMN_activated", a7nal)]:
        ch0 = "A"
        cmap = {x["seq"]: x["xyz"] for x in atoms if x["chain"] == ch0 and x["atom"] == "CA" and (x["group"] == "ATOM" or x["seq"] == 311)}
        ca_maps[label] = cmap
        confs[label] = {
            "chain": ch0,
            "W103_to_R376_ARM_span_A": round(float(np.linalg.norm(cmap[103] - cmap[376])), 2) if 103 in cmap and 376 in cmap else None,
            "W103_to_K193_sensor_cleft_A": round(float(np.linalg.norm(cmap[103] - cmap[193])), 2) if 103 in cmap and 193 in cmap else None,
            "A100_to_C311_hinge_A": round(float(np.linalg.norm(cmap[100] - cmap[311])), 2) if 100 in cmap and 311 in cmap else None,
            "has_resolved_TIR_561_700": any(s >= 565 for s in cmap),
        }
    common_arm = sorted(set(ca_maps["7DJT_Cys311_dHNN"]) & set(ca_maps["7ANW_NAD_autoinhib"]) & set(ca_maps["7NAL_NMN_activated"]) & set(range(70, 400)))
    rmsd_djt_anw = round(kabsch_rmsd(np.array([ca_maps["7DJT_Cys311_dHNN"][s] for s in common_arm]), np.array([ca_maps["7ANW_NAD_autoinhib"][s] for s in common_arm])), 2)
    rmsd_anw_nal = round(kabsch_rmsd(np.array([ca_maps["7ANW_NAD_autoinhib"][s] for s in common_arm]), np.array([ca_maps["7NAL_NMN_activated"][s] for s in common_arm])), 2)
    rmsd_djt_nal = round(kabsch_rmsd(np.array([ca_maps["7DJT_Cys311_dHNN"][s] for s in common_arm]), np.array([ca_maps["7NAL_NMN_activated"][s] for s in common_arm])), 2)

    # 3. 9TZY (2026 BEXi adduct A1JZ0): check cross-chain TIR-TIR dimer bridging!
    adducts = [x for x in a9tzy if x["comp"] == "A1JZ0"]
    ad_chains = sorted({x["chain"] for x in adducts})
    ad0 = [x for x in adducts if x["chain"] == ad_chains[0]] if ad_chains else []
    tir_contacts_by_chain: dict[str, list[str]] = {}
    for x in a9tzy:
        if x["group"] == "ATOM" and ad0 and min_dist([x], ad0) <= 5.0:
            tir_contacts_by_chain.setdefault(x["chain"], [])
            tag = f"{x['comp']}{x['seq']}"
            if tag not in tir_contacts_by_chain[x["chain"]]:
                tir_contacts_by_chain[x["chain"]].append(tag)

    return {
        "7DJT_Cys311_allosteric_site": {
            "chain": pchain,
            "cys311_SG_to_H8L_min_dist_A": round(c311_h8l_d, 2),
            "pocket_residues_5A": [f"{c}{s}" for s, c in pocket_res],
            "als_gof_distances_A": als_dists,
        },
        "arm_conformational_comparison": {
            "states": confs,
            "n_common_arm_CA": len(common_arm),
            "ARM_CA_RMSD_7DJT_vs_7ANW_T_state_A": rmsd_djt_anw,
            "ARM_CA_RMSD_7ANW_vs_7NAL_NMN_R_state_A": rmsd_anw_nal,
            "ARM_CA_RMSD_7DJT_vs_7NAL_NMN_R_state_A": rmsd_djt_nal,
        },
        "9TZY_2026_BEXi_adduct_TIR_glue": {
            "ligand_id": "A1JZ0",
            "n_chains_contacted_within_5A_by_single_adduct": len(tir_contacts_by_chain),
            "contacts_by_chain_5A": tir_contacts_by_chain,
        },
    }


def analyze_ykt6() -> dict:
    a3kyq = parse_cif_atoms(P1_PDB / "pdb_00003kyq.cif")
    aaf = parse_cif_atoms(AFDB / "AF-O15498-F1-model_v6.cif")
    a6j74 = parse_cif_atoms(P1_PDB / "pdb_00006j74.cif")

    dpv = [x for x in a3kyq if x["comp"] == "DPV" and x["seq"] == 201]
    prot3 = [x for x in a3kyq if x["group"] == "ATOM" and x["chain"] == "A"]
    groove3 = sorted({(x["seq"], x["comp"]) for x in prot3 if min_dist([x], dpv) <= 5.0})
    af_seq_comp = {x["seq"]: x["comp"] for x in aaf if x["group"] == "ATOM" and x["atom"] == "CA"}
    conserved = sum(1 for s, c in groove3 if af_seq_comp.get(s) == c)

    ca3 = {x["seq"]: x["xyz"] for x in prot3 if x["atom"] == "CA"}
    caaf = {x["seq"]: x["xyz"] for x in aaf if x["group"] == "ATOM" and x["atom"] == "CA"}
    ca6 = {x["seq"]: x["xyz"] for x in a6j74 if x["group"] == "ATOM" and x["chain"] == "C" and x["atom"] == "CA"}
    longin_idx = sorted(set(ca3) & set(caaf) & set(ca6) & set(range(4, 134)))
    rmsd_3kyq_af = round(kabsch_rmsd(np.array([ca3[s] for s in longin_idx]), np.array([caaf[s] for s in longin_idx])), 2)
    rmsd_3kyq_6j74 = round(kabsch_rmsd(np.array([ca3[s] for s in longin_idx]), np.array([ca6[s] for s in longin_idx])), 2)

    # Tyr64 vs Cys66 geometry & modeled Cys64 S-gamma position along C-alpha -> C-beta vector (1.81 A Cbeta-Sgamma)
    y64_3 = {x["atom"]: x["xyz"] for x in prot3 if x["seq"] == 64}
    c66_3 = {x["atom"]: x["xyz"] for x in prot3 if x["seq"] == 66}
    u_cacb = (y64_3["CB"] - y64_3["CA"]) / np.linalg.norm(y64_3["CB"] - y64_3["CA"])
    # Check min S-gamma(Cys64)--S-gamma(Cys66) across standard chi1 rotamers (-60, +60, 180 deg)
    ca_vec = y64_3["CA"] - y64_3["CB"]
    n_vec = y64_3["N"] - y64_3["CA"]
    perp1 = np.cross(u_cacb, n_vec)
    perp1 /= np.linalg.norm(perp1)
    perp2 = np.cross(u_cacb, perp1)
    sg_dists = []
    for deg in (-60.0, 60.0, 180.0):
        rad = math.radians(deg)
        dir_sg = math.cos(math.radians(66.0)) * u_cacb + math.sin(math.radians(66.0)) * (math.cos(rad) * perp1 + math.sin(rad) * perp2)
        sg64 = y64_3["CB"] + 1.81 * dir_sg
        sg_dists.append(round(float(np.linalg.norm(sg64 - c66_3["SG"])), 2))

    # Score ChEMBL Phase-4 CNS chaperone scaffolds for p.Tyr64Cys cavity complementarity
    frags = json.loads((OUT / "ykt6_cns_chaperone_candidates_chembl.json").read_text(encoding="utf-8"))
    scored = []
    for f in frags:
        ar = f.get("aromatic_rings") or 0
        mw, psa, alogp, hbd = f.get("mw") or 0, f.get("psa") or 99, f.get("alogp") or 0, f.get("hbd") or 0
        if ar < 1 or ar > 2:
            continue
        # Ideal cavity-filling CNS MPO score for -85.1 A^3 Tyr64Cys + DPV201 groove subpocket
        s_vol = max(0.0, 1.0 - abs(mw - 225.0) / 75.0)
        s_lip = max(0.0, 1.0 - abs(alogp - 2.75) / 1.2)
        s_bbb = 1.0 if 25.0 <= psa <= 52.0 and hbd <= 1 else 0.65
        tot = round(100.0 * (0.4 * s_vol + 0.35 * s_lip + 0.25 * s_bbb), 1)
        scored.append({**f, "ykt6_groove_chaperone_score": tot})
    scored.sort(key=lambda r: -r["ykt6_groove_chaperone_score"])

    return {
        "longin_groove_conservation": {
            "n_dpv201_5A_residues": len(groove3),
            "human_rat_identical_in_groove": f"{conserved}/{len(groove3)}",
            "dpv201_5A_residues": [f"{c}{s}" for s, c in groove3],
            "longin_CA_RMSD_3KYQ_vs_human_AF_A": rmsd_3kyq_af,
            "longin_CA_RMSD_3KYQ_closed_vs_6J74_open_A": rmsd_3kyq_6j74,
        },
        "tyr64cys_dual_biophysical_defect": {
            "tyr64_to_DPV201_min_dist_A": round(min_dist([x for x in prot3 if x["seq"] == 64], dpv), 2),
            "tyr64_to_PHE28_ring_min_dist_A": round(min_dist([x for x in prot3 if x["seq"] == 64], [x for x in prot3 if x["seq"] == 28]), 2),
            "sidechain_volume_loss_A3": -85.1,  # Chothia residue volume Cys (108.5 A^3) - Tyr (193.6 A^3)
            "CA64_to_CA66_dist_A": round(float(np.linalg.norm(y64_3["CA"] - c66_3["CA"])), 2),
            "CB64_to_SG66_dist_A": round(float(np.linalg.norm(y64_3["CB"] - c66_3["SG"])), 2),
            "modeled_Cys64_SG_to_Cys66_SG_rotamer_dists_A": sg_dists,
        },
        "top_cns_chaperone_scaffolds_chembl_phase4": scored[:10],
    }


if __name__ == "__main__":
    res = {"analysis_run_id": "RUN-P2-T2-001", "sarm1": analyze_sarm1(), "ykt6": analyze_ykt6()}
    (OUT / "run_p2_t2_001_structural_biophysics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(json.dumps(res["sarm1"]["arm_conformational_comparison"], indent=2))
    print("9TZY BEXi contacted chains:", res["sarm1"]["9TZY_2026_BEXi_adduct_TIR_glue"]["n_chains_contacted_within_5A_by_single_adduct"])
    print("YKT6 groove conservation:", res["ykt6"]["longin_groove_conservation"]["human_rat_identical_in_groove"], "| Cys64-Cys66 SG rotamers:", res["ykt6"]["tyr64cys_dual_biophysical_defect"]["modeled_Cys64_SG_to_Cys66_SG_rotamer_dists_A"])
