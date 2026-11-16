"""Quote-safe mmCIF coordinate parser, Kabsch superposition, and 3D pocket steric scorer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

import numpy as np

CIF_TOKEN_RE = re.compile(r"'[^']*'|\"[^\"]*\"|\S+")
SOLVENT_AND_IONS = {
    "HOH", "WAT", "DOD", "NA", "CL", "MG", "ZN", "CA", "K", "SO4", "PO4", "GOL", "EDO", "PEG", "DMS",
}


@dataclass
class AtomRecord:
    group_pdb: str
    atom_name: str
    comp_id: str
    chain_id: str
    seq_id: int | None
    x: float
    y: float
    z: float
    b_iso_or_plddt: float

    @property
    def coord(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)


@dataclass
class ParsedMMCIF:
    polymer_atoms: list[AtomRecord] = field(default_factory=list)
    modified_polymer_atoms: list[AtomRecord] = field(default_factory=list)
    ligand_atoms: list[AtomRecord] = field(default_factory=list)

    def chain_ca_map(self, chain_id: str, include_modified: bool = True) -> dict[int, np.ndarray]:
        pool = self.polymer_atoms + (self.modified_polymer_atoms if include_modified else [])
        out: dict[int, np.ndarray] = {}
        for a in pool:
            if a.chain_id == chain_id and a.atom_name == "CA" and a.seq_id is not None and a.seq_id not in out:
                out[a.seq_id] = a.coord
        return out

    def residue_groups(
        self,
        chain_id: str | None = None,
        include_modified: bool = False,
    ) -> dict[tuple[str, int, str], list[AtomRecord]]:
        """Group polymer (and optionally modified polymer) atoms by (chain_id, auth_seq_id, comp_id)."""
        pool = self.polymer_atoms + (self.modified_polymer_atoms if include_modified else [])
        groups: dict[tuple[str, int, str], list[AtomRecord]] = {}
        for a in pool:
            if a.seq_id is None:
                continue
            if chain_id is not None and a.chain_id != chain_id:
                continue
            groups.setdefault((a.chain_id, a.seq_id, a.comp_id), []).append(a)
        return groups


def _unquote(tok: str) -> str:
    if len(tok) >= 2 and ((tok[0] == "'" and tok[-1] == "'") or (tok[0] == '"' and tok[-1] == '"')):
        return tok[1:-1]
    return tok


def load_mmcif_structure(cif_path: Path) -> ParsedMMCIF:
    """Parse mmCIF _atom_site safely, preserving quoted atom names and covalent HETATM polymer residues."""
    lines = cif_path.read_text(encoding="utf-8", errors="replace").splitlines()
    parsed = ParsedMMCIF()
    i, n = 0, len(lines)
    while i < n:
        if lines[i].strip() == "loop_":
            cols: list[str] = []
            j = i + 1
            while j < n and lines[j].strip().startswith("_"):
                cols.append(lines[j].strip())
                j += 1
            if cols and cols[0].startswith("_atom_site."):
                col_idx = {c.split(".", 1)[1]: idx for idx, c in enumerate(cols)}
                g_i = col_idx["group_PDB"]
                atom_i = col_idx.get("label_atom_id", col_idx.get("auth_atom_id", 0))
                comp_i = col_idx.get("label_comp_id", col_idx.get("auth_comp_id", 0))
                asym_i = col_idx.get("auth_asym_id", col_idx.get("label_asym_id", 0))
                lseq_i = col_idx.get("label_seq_id")
                aseq_i = col_idx.get("auth_seq_id")
                alt_i = col_idx.get("label_alt_id")
                model_i = col_idx.get("pdbx_PDB_model_num")
                x_i, y_i, z_i = col_idx["Cartn_x"], col_idx["Cartn_y"], col_idx["Cartn_z"]
                b_i = col_idx.get("B_iso_or_equiv")

                while j < n:
                    raw = lines[j].strip()
                    if not raw or raw.startswith("#") or raw == "loop_" or raw.startswith("_") or raw.startswith("data_"):
                        break
                    toks = [_unquote(t) for t in CIF_TOKEN_RE.findall(raw)]
                    j += 1
                    if len(toks) < len(cols):
                        continue
                    if model_i is not None and toks[model_i] not in {"1", ".", "?"}:
                        continue
                    if alt_i is not None and toks[alt_i] not in {".", "?", "A"}:
                        continue
                    grp = toks[g_i]
                    if grp not in {"ATOM", "HETATM"}:
                        continue
                    comp = toks[comp_i].upper()
                    lseq_raw = toks[lseq_i] if lseq_i is not None else "."
                    aseq_raw = toks[aseq_i] if aseq_i is not None else "."
                    is_polymer_seq = lseq_raw not in {".", "?"}
                    seq_val: int | None = None
                    if aseq_raw not in {".", "?"}:
                        try:
                            seq_val = int(aseq_raw)
                        except ValueError:
                            seq_val = None
                    if seq_val is None and is_polymer_seq:
                        try:
                            seq_val = int(lseq_raw)
                        except ValueError:
                            seq_val = None
                    rec = AtomRecord(
                        group_pdb=grp,
                        atom_name=toks[atom_i],
                        comp_id=comp,
                        chain_id=toks[asym_i],
                        seq_id=seq_val,
                        x=float(toks[x_i]),
                        y=float(toks[y_i]),
                        z=float(toks[z_i]),
                        b_iso_or_plddt=float(toks[b_i]) if (b_i is not None and toks[b_i] not in {".", "?"}) else 0.0,
                    )
                    if grp == "ATOM":
                        parsed.polymer_atoms.append(rec)
                    elif is_polymer_seq:
                        parsed.modified_polymer_atoms.append(rec)
                    elif comp not in SOLVENT_AND_IONS:
                        parsed.ligand_atoms.append(rec)
                i = j
                continue
        i += 1
    return parsed


def ca_rmsd_kabsch(coords_p: np.ndarray, coords_q: np.ndarray) -> float:
    """Optimal rigid-body C-alpha RMSD (in Angstroms) via Kabsch SVD."""
    if coords_p.shape != coords_q.shape or coords_p.ndim != 2 or coords_p.shape[1] != 3 or len(coords_p) < 3:
        raise ValueError(f"Invalid coordinate arrays for Kabsch RMSD: {coords_p.shape} vs {coords_q.shape}")
    p_c = coords_p - coords_p.mean(axis=0)
    q_c = coords_q - coords_q.mean(axis=0)
    cov = p_c.T @ q_c
    v, s, wt = np.linalg.svd(cov)
    d = np.sign(np.linalg.det(v @ wt))
    rot = v @ np.diag([1.0, 1.0, d]) @ wt
    diff = (p_c @ rot) - q_c
    return float(np.sqrt(np.mean(np.sum(diff * diff, axis=1))))


def score_pocket_steric_complementarity(
    pocket_coords: np.ndarray,
    mol_mw_da: float,
    target_cavity_a3: float,
    min_offtarget_ic50_nm: float | None = None,
) -> dict[str, float | bool]:
    """Score 3D cavity volume occupancy (~1.22 A3/Da) + spherical pocket clearance + off-target selectivity."""
    span = np.ptp(pocket_coords, axis=0)
    eff_radius_a = float(np.min(span) * 0.5)
    est_mol_vol_a3 = mol_mw_da * 0.92
    fill_ratio = est_mol_vol_a3 / max(abs(target_cavity_a3), 1.0)
    steric_clash = est_mol_vol_a3 > (4.0 / 3.0) * np.pi * (max(eff_radius_a, 1.5) ** 3)
    offtarget_clean = True if min_offtarget_ic50_nm is None else (min_offtarget_ic50_nm >= 1000.0)
    score = max(0.0, 100.0 - 25.0 * abs(np.log2(max(fill_ratio, 0.1)))) * (0.0 if steric_clash else 1.0)
    if not offtarget_clean:
        score *= 0.25
    return {
        "est_mol_vol_a3": round(est_mol_vol_a3, 2),
        "cavity_fill_ratio": round(fill_ratio, 3),
        "steric_clash_flag": bool(steric_clash),
        "offtarget_clean_ge_1uM": bool(offtarget_clean),
        "pocket_selectivity_score": round(float(score), 2),
    }
