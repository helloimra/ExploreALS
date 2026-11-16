"""RUN-P2-T3-004: 3D Structural Grounding of JAK2+Baricitinib (PDB 6VN8) & Human PIKfyve Complex (PDB 7K2V)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from carbon_als.loaders import download_https_structure  # noqa: E402
from carbon_als.mmcif_parser import load_mmcif_structure  # noqa: E402

import os

PDB_DIR = ROOT / "data" / "pharmacology_structures" / "phase2_pdb"
ARTIFACT_STRUCT_DIR = Path(os.environ["ARTIFACT_STRUCT_DIR"]) if os.environ.get("ARTIFACT_STRUCT_DIR") else None
OUT_DIR = ROOT / "work" / "phase2" / "track3_subtype_precision_translation" / "outputs"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_cif_title(cif_path: Path) -> str:
    for ln in cif_path.read_text(encoding="utf-8", errors="replace").splitlines()[:150]:
        if "_struct.title" in ln:
            return ln.strip()
    return ""


def analyze_ligand_contacts(cif_path: Path, pdb_code: str, cutoff_a: float = 4.2) -> dict:
    st = load_mmcif_structure(cif_path)
    skip = {"HOH", "SO4", "PO4", "GOL", "EDO", "PEG", "DMS", "CL", "NA", "MG", "ZN", "ACT", "FMT"}
    lig_atoms = [a for a in st.ligand_atoms if a.comp_id not in skip]
    by_comp: dict[str, list] = {}
    for a in lig_atoms:
        key = f"{a.chain_id}:{a.comp_id}:{a.seq_id}"
        by_comp.setdefault(key, []).append(a)

    res_groups: dict[tuple[str, int, str], list] = {}
    for a in st.polymer_atoms:
        if a.seq_id is not None:
            res_groups.setdefault((a.chain_id, a.seq_id, a.comp_id), []).append(a)

    contacts_out: dict[str, dict] = {}
    for key, latoms in by_comp.items():
        lcoords = np.array([[a.x, a.y, a.z] for a in latoms], dtype=float)
        res_hits = []
        for (rc, rseq, rcomp), ratoms in res_groups.items():
            rcoords = np.array([[a.x, a.y, a.z] for a in ratoms], dtype=float)
            dmat = np.linalg.norm(rcoords[:, None, :] - lcoords[None, :, :], axis=2)
            min_d = float(dmat.min())
            if min_d <= cutoff_a:
                ri, li = np.unravel_index(int(np.argmin(dmat)), dmat.shape)
                res_hits.append({
                    "chain": rc,
                    "auth_seq_id": rseq,
                    "comp_id": rcomp,
                    "min_dist_A": round(min_d, 3),
                    "protein_atom": ratoms[int(ri)].atom_name,
                    "ligand_atom": latoms[int(li)].atom_name,
                })
        res_hits.sort(key=lambda x: x["min_dist_A"])
        contacts_out[key] = {
            "n_ligand_heavy_atoms": len(latoms),
            "centroid_xyz": [round(float(v), 3) for v in lcoords.mean(axis=0)],
            "n_contact_residues_le_4p2A": len(res_hits),
            "contacts": res_hits[:20],
        }

    chain_spans: dict[str, dict] = {}
    for (rc, rseq, _) in res_groups:
        if rc not in chain_spans:
            chain_spans[rc] = {"min_seq": rseq, "max_seq": rseq, "n_res": 1}
        else:
            chain_spans[rc]["min_seq"] = min(chain_spans[rc]["min_seq"], rseq)
            chain_spans[rc]["max_seq"] = max(chain_spans[rc]["max_seq"], rseq)
            chain_spans[rc]["n_res"] += 1

    return {
        "pdb_id": pdb_code,
        "title_line": extract_cif_title(cif_path),
        "n_polymer_residues": len(res_groups),
        "chain_spans": chain_spans,
        "ligand_sites": contacts_out,
    }


def main() -> None:
    PDB_DIR.mkdir(parents=True, exist_ok=True)
    if ARTIFACT_STRUCT_DIR:
        ARTIFACT_STRUCT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    staged = {}
    for pdb_code in ("6VN8", "7K2V"):
        url = f"https://files.rcsb.org/download/{pdb_code}.cif"
        dest = PDB_DIR / f"pdb_0000{pdb_code.lower()}.cif"
        if not dest.exists() or dest.stat().st_size < 10_000:
            download_https_structure(url, dest)
        if ARTIFACT_STRUCT_DIR:
            shutil.copy2(dest, ARTIFACT_STRUCT_DIR / dest.name)
        info = analyze_ligand_contacts(dest, pdb_code)
        info["local_relpath"] = str(dest.relative_to(ROOT)).replace("\\", "/")
        info["artifact_relpath"] = f"structures/{dest.name}"
        info["size_bytes"] = int(dest.stat().st_size)
        info["sha256"] = sha256_of(dest)
        staged[pdb_code] = info

    out = {
        "analysis_run_id": "RUN-P2-T3-004",
        "structures": staged,
    }
    (OUT_DIR / "run_p2_t3_004_structures_jak2_pikfyve.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("SAVED run_p2_t3_004_structures_jak2_pikfyve.json")


if __name__ == "__main__":
    main()
