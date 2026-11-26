"""Headless mmCIF 3D structural dissection and verified external priors for Step 1 STING1/CGAS evaluation."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
from typing import Any

import numpy as np

from carbon_als.loaders import download_https_structure
from carbon_als.mmcif_parser import ParsedMMCIF, load_mmcif_structure

PDB_SPECS: tuple[tuple[str, str, str], ...] = (
    ("6NT5", "STING1", "Full-length human STING1 apo homodimer cryo-EM (Shang et al. 2019 Nature PMID:30842659)"),
    ("4KSY", "STING1", "Human STING1 R232 LBD closed-lid 2'3'-cGAMP (1SY) X-ray (Zhang et al. 2013 Mol Cell PMID:23747010)"),
    ("6MXE", "STING1", "Human STING1 G230A/H232R/R293Q open-inactive Compound 18 (K5S) antagonist X-ray (Siu et al. 2019 PMID:30655953)"),
    ("6MJW", "CGAS", "Human cGAS catalytic domain + human-selective inhibitor G150 (JUJ) X-ray (Lama et al. 2019 PMID:31113940)"),
    ("6LRC", "CGAS", "Human cGAS catalytic domain + active-site inhibitor PF-06928215 (KHM) X-ray (PMID:32459092)"),
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


def _atom_dist(st: ParsedMMCIF, ch1: str, seq1: int, at1: str, ch2: str, seq2: int, at2: str) -> float | None:
    p1 = next((a.coord for a in st.polymer_atoms if a.chain_id == ch1 and a.seq_id == seq1 and a.atom_name == at1), None)
    p2 = next((a.coord for a in st.polymer_atoms if a.chain_id == ch2 and a.seq_id == seq2 and a.atom_name == at2), None)
    return round(float(np.linalg.norm(p1 - p2)), 2) if (p1 is not None and p2 is not None) else None


def analyze_staged_mmcif_structures(root: Path) -> dict[str, Any]:
    pdb_dir = root / "data" / "pharmacology_structures" / "phase4_pdb"
    out: dict[str, Any] = {}
    for pid, gene, desc in PDB_SPECS:
        fp = pdb_dir / f"pdb_0000{pid.lower()}.cif"
        if not fp.is_file():
            sz, sha = download_https_structure(f"https://files.rcsb.org/download/{pid}.cif", fp)
        else:
            raw = fp.read_bytes()
            sz, sha = len(raw), hashlib.sha256(raw).hexdigest()
        txt = fp.read_text(encoding="utf-8", errors="replace")
        res_m = re.findall(r"_(?:refine\.ls_d_res_high|em_3d_reconstruction\.resolution)\s+([0-9.]+)", txt)
        pm_m = re.findall(r"_citation\.pdbx_database_id_PubMed\s+(\d+)", txt)
        st = load_mmcif_structure(fp)
        chains = sorted({a.chain_id for a in st.polymer_atoms})
        chain_spans = {
            ch: {
                "n_resolved_residues": len({k[1] for k in st.residue_groups(chain_id=ch)}),
                "resolved_auth_spans": _contig_ranges([k[1] for k in st.residue_groups(chain_id=ch)]),
            }
            for ch in chains
        }
        lig_codes = sorted({a.comp_id for a in st.ligand_atoms})
        rec: dict[str, Any] = {
            "pdb_id": pid, "target_gene": gene, "description": desc,
            "local_relpath": fp.relative_to(root).as_posix(), "size_bytes": sz, "sha256": sha,
            "resolution_A": float(res_m[0]) if res_m else None, "primary_pmid": pm_m[0] if pm_m else None,
            "chains": chain_spans, "non_solvent_ligands": lig_codes,
            "contacts_le_4A": {lc: _ligand_contacts(st, lc, 4.0) for lc in lig_codes},
        }
        if pid == "6NT5":
            rec["palmitoylation_and_cleft_geometry_A"] = {
                "Cys88_CA_A_to_B": _atom_dist(st, "A", 88, "CA", "B", 88, "CA"),
                "Cys91_CA_A_to_B": _atom_dist(st, "A", 91, "CA", "B", 91, "CA"),
                "Cys91_SG_A_to_B": _atom_dist(st, "A", 91, "SG", "B", 91, "SG"),
                "Cys88_to_Cys91_CA_intraA": _atom_dist(st, "A", 88, "CA", "A", 91, "CA"),
                "apo_cleft_Tyr167_CA_A_to_B": _atom_dist(st, "A", 167, "CA", "B", 167, "CA"),
                "apo_cleft_Ser241_CA_A_to_B": _atom_dist(st, "A", 241, "CA", "B", 241, "CA"),
                "Arg71_resolved_in_chain_A": ("A", 71) in {(k[0], k[1]) for k in st.residue_groups("A")},
            }
        elif pid in {"4KSY", "6MXE"}:
            res_set = {(k[0], k[1]): k[2] for k in st.residue_groups()}
            rec["lid_and_polymorphic_residues"] = {
                "pos230_observed": {ch: res_set.get((ch, 230), "UNRESOLVED_OPEN_LID") for ch in chains},
                "pos232_observed": {ch: res_set.get((ch, 232), "UNRESOLVED_OPEN_LID") for ch in chains},
                "pos238_observed": {ch: res_set.get((ch, 238), "UNRESOLVED_OPEN_LID") for ch in chains},
                "pos293_observed": {ch: res_set.get((ch, 293), "UNRESOLVED") for ch in chains},
                "Ser241_CA_A_to_B": _atom_dist(st, "A", 241, "CA", "B", 241, "CA") if len(chains) >= 2 else None,
            }
        out[pid] = rec
    return out
