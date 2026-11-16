"""Header-resolved 3D structural dissection of human Kv7.2 + retigabine cryo-EM (PDB 7CR2)."""

from __future__ import annotations

import json
import math
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CIF_PATH = ROOT / "data" / "pharmacology_structures" / "phase2_pdb" / "pdb_00007cr2.cif"
OUT_JSON = ROOT / "work" / "phase2" / "track1_multiplex_splice" / "outputs" / "phase2_track1_kv72_structure.json"

EXON5_START, EXON5_END = 231, 272
DOMAINS = {
    "S1_S3_VSD": (90, 192),
    "S4_voltage_sensor": (193, 217),
    "S4_S5_linker": (218, 230),
    "Exon5_S5_and_turret": (231, 272),
    "P_helix_selectivity_filter": (273, 291),
    "S6_inner_pore_gate": (292, 323),
    "Helix_A_B_CaM_Cterm": (324, 650),
}


def parse_atom_site(cif_path: Path) -> list[dict]:
    lines = cif_path.read_text(encoding="utf-8", errors="replace").splitlines()
    headers: list[str] = []
    atoms: list[dict] = []
    in_atom = False
    for line in lines:
        s = line.strip()
        if s == "loop_":
            in_atom = False
            headers = []
            continue
        if s.startswith("_atom_site."):
            in_atom = True
            headers.append(s.split(".", 1)[1].strip())
            continue
        if in_atom:
            if not s or s.startswith("#") or s.startswith("_"):
                if atoms:
                    break
                continue
            parts = shlex.split(s)
            if len(parts) != len(headers):
                continue
            rec = dict(zip(headers, parts))
            if rec.get("pdbx_PDB_model_num", "1") != "1":
                continue
            atoms.append(rec)
    return atoms


def min_dist(a_list: list[tuple[float, float, float]], b_list: list[tuple[float, float, float]]) -> float:
    best = 999.0
    for ax, ay, az in a_list:
        for bx, by, bz in b_list:
            d2 = (ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2
            if d2 < best:
                best = d2
    return math.sqrt(best)


def main() -> None:
    atoms = parse_atom_site(CIF_PATH)
    if not atoms:
        raise RuntimeError(f"No _atom_site records parsed from {CIF_PATH}")

    chain_res: dict[str, set[int]] = {}
    het_by_comp: dict[str, list[dict]] = {}
    chain_a_res_coords: dict[int, tuple[str, list[tuple[float, float, float]]]] = {}
    other_kv_coords: dict[tuple[str, int], tuple[str, list[tuple[float, float, float]]]] = {}

    for r in atoms:
        if r.get("type_symbol") == "H":
            continue
        grp = r["group_PDB"]
        ch = r["auth_asym_id"]
        comp = r["auth_comp_id"]
        seq_s = r["auth_seq_id"]
        xyz = (float(r["Cartn_x"]), float(r["Cartn_y"]), float(r["Cartn_z"]))
        if grp == "ATOM" and seq_s.lstrip("-").isdigit():
            seq = int(seq_s)
            chain_res.setdefault(ch, set()).add(seq)
            if ch == "A":
                chain_a_res_coords.setdefault(seq, (comp, []))[1].append(xyz)
            elif ch in {"B", "C", "D"}:
                other_kv_coords.setdefault((ch, seq), (comp, []))[1].append(xyz)
        elif grp == "HETATM" and comp != "HOH":
            het_by_comp.setdefault(comp, []).append({"chain": ch, "seq": seq_s, "atom": r["label_atom_id"], "xyz": xyz})

    ex5_resolved = sorted(s for s in chain_a_res_coords if EXON5_START <= s <= EXON5_END)
    ex5_xyz = [pt for s in ex5_resolved for pt in chain_a_res_coords[s][1]]

    # Contacts (<5.0 A) from Chain A Exon 5 (231-272) to intra-subunit domains & adjacent Kv7.2 chains
    intra_contacts: dict[str, list[str]] = {k: [] for k in DOMAINS if k != "Exon5_S5_and_turret"}
    for seq, (comp, pts) in sorted(chain_a_res_coords.items()):
        if EXON5_START <= seq <= EXON5_END:
            continue
        d = min_dist(ex5_xyz, pts)
        if d <= 5.0:
            for dname, (lo, hi) in DOMAINS.items():
                if dname != "Exon5_S5_and_turret" and lo <= seq <= hi:
                    intra_contacts[dname].append(f"{comp}{seq}({d:.2f}A)")

    inter_subunit_contacts: list[str] = []
    for (ch, seq), (comp, pts) in sorted(other_kv_coords.items()):
        d = min_dist(ex5_xyz, pts)
        if d <= 5.0:
            inter_subunit_contacts.append(f"{ch}:{comp}{seq}({d:.2f}A)")

    # Retigabine / ligand pocket contacts & Trp236 distance
    ligand_summary = {}
    w236_pts = chain_a_res_coords.get(236, ("TRP", []))[1]
    for comp, recs in het_by_comp.items():
        by_inst: dict[tuple[str, str], list[tuple[float, float, float]]] = {}
        for item in recs:
            by_inst.setdefault((item["chain"], item["seq"]), []).append(item["xyz"])
        closest_inst, best_d_ex5, best_d_w236 = None, 999.0, 999.0
        for inst, pts in by_inst.items():
            d_ex5 = min_dist(ex5_xyz, pts)
            d_w = min_dist(w236_pts, pts) if w236_pts else 999.0
            if d_ex5 < best_d_ex5:
                best_d_ex5, best_d_w236, closest_inst = d_ex5, d_w, f"{inst[0]}:{inst[1]}"
        # Pocket residues on Chain A + neighbors within 4.5 A of closest ligand instance
        pocket_res = []
        if closest_inst and best_d_ex5 <= 12.0:
            c_ch, c_seq = closest_inst.split(":")
            l_pts = by_inst[(c_ch, c_seq)]
            for s, (rc, rpts) in sorted(chain_a_res_coords.items()):
                dd = min_dist(l_pts, rpts)
                if dd <= 4.5:
                    pocket_res.append({"chain": "A", "auth_seq_id": s, "comp": rc, "dist_A": round(dd, 2), "in_exon5": EXON5_START <= s <= EXON5_END})
            for (och, os), (orc, orpts) in sorted(other_kv_coords.items()):
                dd = min_dist(l_pts, orpts)
                if dd <= 4.5:
                    pocket_res.append({"chain": och, "auth_seq_id": os, "comp": orc, "dist_A": round(dd, 2), "in_exon5": EXON5_START <= os <= EXON5_END})
        ligand_summary[comp] = {
            "instances": len(by_inst),
            "closest_instance_to_chainA_exon5": closest_inst,
            "min_dist_to_chainA_exon5_A": round(best_d_ex5, 2),
            "min_dist_to_chainA_Trp236_A": round(best_d_w236, 2),
            "pocket_residues_within_4_5A": pocket_res,
        }

    chain_spans = {ch: {"count": len(s), "min_seq": min(s), "max_seq": max(s)} for ch, s in sorted(chain_res.items())}
    out = {
        "pdb_id": "7CR2",
        "cif_path": str(CIF_PATH.relative_to(ROOT)),
        "resolved_chains": chain_spans,
        "chain_A_exon5_residues": {
            "expected_range": [EXON5_START, EXON5_END],
            "resolved_count": len(ex5_resolved),
            "resolved_min": min(ex5_resolved),
            "resolved_max": max(ex5_resolved),
            "trp236_resolved": 236 in chain_a_res_coords,
            "trp236_comp": chain_a_res_coords.get(236, ("MISSING", []))[0],
        },
        "intra_subunit_chainA_contacts_le_5A": {k: {"count": len(v), "residues": v[:20]} for k, v in intra_contacts.items()},
        "inter_subunit_tetramer_contacts_le_5A": {"count": len(inter_subunit_contacts), "residues": inter_subunit_contacts[:30]},
        "ligands_and_retigabine_pocket": ligand_summary,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved 7CR2 structural dissection -> {OUT_JSON.name}")


if __name__ == "__main__":
    main()
