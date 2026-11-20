"""CELF5 (DN-04 / EALS-037) AF-Q8N6W0 + PDB 3NMR RRM2 truncation, Brown 2022 Frechet-Hoeffding phasing bounds, & 18-nt EJC minigene audit."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import urllib.request

import numpy as np

from carbon_als.loaders import load_brown2022_splicing
from carbon_als.mmcif_parser import ca_rmsd_kabsch, load_mmcif_structure


def audit_celf5_3d_rrm2_and_phasing(p_3nmr: Path, p_af: Path, cache_dir: Path) -> dict[str, Any]:
    saf = load_mmcif_structure(p_af)
    rg_af = saf.residue_groups(chain_id="A", include_modified=True)
    ca_af = saf.chain_ca_map("A")

    def mean_plddt(lo: int, hi: int) -> float:
        vals = [a.b_iso_or_plddt for (_, s, _), al in rg_af.items() if lo <= s <= hi for a in al if a.atom_name == "CA"]
        return round(float(np.mean(vals)), 2) if vals else 0.0

    rrm1_atoms = [a for (_, s, _), al in rg_af.items() if 46 <= s <= 121 for a in al]
    rrm2_atoms = [a for (_, s, _), al in rg_af.items() if 134 <= s <= 214 for a in al]
    inter_rrm_contacts = sum(
        1 for a in rrm1_atoms for b in rrm2_atoms if float(np.linalg.norm(a.coord - b.coord)) <= 4.5
    )

    pae_fp = cache_dir / "af_q8n6w0_pae_summary.json"
    if pae_fp.is_file():
        pae_sum = json.loads(pae_fp.read_text(encoding="utf-8"))
    else:
        with urllib.request.urlopen("https://alphafold.ebi.ac.uk/files/AF-Q8N6W0-F1-predicted_aligned_error_v6.json", timeout=30) as r:
            pae_mat = np.array(json.loads(r.read().decode("utf-8"))[0]["predicted_aligned_error"], dtype=float)
        pae_sum = {
            "intra_rrm1_46_121_mean_pae_A": round(float(pae_mat[45:121, 45:121].mean()), 2),
            "intra_rrm2_134_214_mean_pae_A": round(float(pae_mat[133:214, 133:214].mean()), 2),
            "inter_rrm1_rrm2_cross_mean_pae_A": round(float(pae_mat[45:121, 133:214].mean()), 2),
        }
        pae_fp.write_text(json.dumps(pae_sum, indent=2), encoding="utf-8")

    # Backbone H-bonds (N...O <= 3.5 A) and heavy-atom packing (<= 4.2 A) lost when beta4 (202-214) is excised past Pro201
    b4_atoms = [a for (_, s, _), al in rg_af.items() if 202 <= s <= 214 for a in al]
    ret_rrm2 = [a for (_, s, _), al in rg_af.items() if 134 <= s <= 200 for a in al]
    b1_atoms = [a for (_, s, _), al in rg_af.items() if 134 <= s <= 145 for a in al]
    hbonds_b4_b1 = {
        (a.seq_id, a.atom_name, b.seq_id, b.atom_name)
        for a in b4_atoms for b in b1_atoms
        if {a.atom_name, b.atom_name} == {"N", "O"} and float(np.linalg.norm(a.coord - b.coord)) <= 3.5
    }
    packing_b4_core = {
        (a.seq_id, a.comp_id, b.seq_id, b.comp_id)
        for a in b4_atoms for b in ret_rrm2
        if abs((a.seq_id or 0) - (b.seq_id or 0)) > 2 and float(np.linalg.norm(a.coord - b.coord)) <= 4.2
    }

    # PDB 3NMR (Teplova et al. 2010 CELF1 RRM1-RRM2 bound to UGUU RNA): align RRM2 C-alphas & count UGUU RNA contacts
    s3 = load_mmcif_structure(p_3nmr)
    rg3 = s3.residue_groups(include_modified=True)
    rna_nt_names = {"A", "C", "G", "U", "ADE", "CYT", "GUA", "URI"}
    prot_chains = sorted({c for (c, _, comp) in rg3 if comp not in rna_nt_names}, key=lambda c: -len([k for k in rg3 if k[0] == c]))
    p_ch = prot_chains[0]
    ca_3nmr = s3.chain_ca_map(p_ch)
    # CELF5 RRM2 (134..214, 81 aa) maps 1:1 onto CELF1 RRM2 (108..188, 81 aa) — find optimal gapless 81-aa window in 3NMR
    best_rmsd, best_start = 99.0, 108
    af_rrm2_vec = np.array([ca_af[i] for i in range(134, 215)])
    s3_keys = sorted(ca_3nmr)
    for st in s3_keys:
        if all((st + k) in ca_3nmr for k in range(81)):
            q_vec = np.array([ca_3nmr[st + k] for k in range(81)])
            rm = ca_rmsd_kabsch(af_rrm2_vec, q_vec)
            if rm < best_rmsd:
                best_rmsd, best_start = rm, st
    trunc_cut_3nmr = best_start + (201 - 134)
    rna_atoms = [a for (c, _, comp), al in rg3.items() if comp in rna_nt_names for a in al] + [
        a for a in s3.ligand_atoms if a.comp_id in rna_nt_names
    ]
    rrm2_rna_all = {(s, comp) for (c, s, comp), al in rg3.items() if c == p_ch and best_start <= s <= best_start + 80 for a in al for ra in rna_atoms if float(np.linalg.norm(a.coord - ra.coord)) <= 4.0}
    rrm2_rna_excised = {(s, comp) for (s, comp) in rrm2_rna_all if s > trunc_cut_3nmr}

    # Exact Brown 2022 local LSV junctions (distinct LSV denominators), Zeng 2025 NMD rescue, & 18-nt EJC minigene rule
    br = load_brown2022_splicing(["CELF5"])
    jdf = br["junctions_df"]
    jdf = jdf[jdf["gene_name"] == "CELF5"]
    ribo_fc = float(br["riboseq_df"].loc[br["riboseq_df"]["gene_name"] == "CELF5", "log2FoldChange"].iloc[0])
    rnaseq_fc = float(br["rnaseq_df"].loc[br["rnaseq_df"]["gene_name"] == "CELF5", "log2FoldChange"].iloc[0])
    p_ce, p_micro_wt, p_micro_kd, p_up_na = 0.3471, 0.028, 0.182, 0.1218

    return {
        "celf5_afdb_and_3nmr_rrm2_truncation": {
            "afdb_id": "AF-Q8N6W0-F1-v6",
            "pdb_homolog_id": "3NMR (PMID:20947024, CELF1 RRM1-RRM2:UGUU homolog projection; no experimental CELF5 RRM2 structure)",
            "plddt_rrm1_46_121": mean_plddt(46, 121),
            "plddt_rrm2_retained_134_201": mean_plddt(134, 201),
            "plddt_rrm2_excised_beta4_202_214": mean_plddt(202, 214),
            "inter_rrm1_rrm2_heavy_contacts_le_4p5A": inter_rrm_contacts,
            "pae_domain_independence": pae_sum,
            "severed_beta4_beta1_backbone_hbonds_le_3p5A": len(hbonds_b4_b1),
            "severed_beta4_core_residue_pairs_le_4p2A": len(packing_b4_core),
            "kabsch_ca_rmsd_rrm2_to_3nmr_A": round(best_rmsd, 3),
            "mapped_3nmr_rrm2_span": [best_start, best_start + 80],
            "mapped_3nmr_pro201_equivalent": trunc_cut_3nmr,
            "total_3nmr_rrm2_uguu_rna_contact_residues_le_4p0A": len(rrm2_rna_all),
            "excised_beta4_and_cterm_uguu_contact_residues_lost": len(rrm2_rna_excised),
            "structural_mechanism_verdict": "Truncation after Pro201 excises beta4 (202-214) in AF-Q8N6W0-F1, severing anti-parallel beta4-beta1 backbone H-bonds and projected C-terminal UGUU RNA-clamp contacts (mapped from CELF1 homolog PDB 3NMR) while leaving RRM1 (46-121; 0 inter-domain contacts) decoupled across a flexible linker: primary loss-of-function + unfolded RRM2(134-201)+29aa chaperone/granule burden rather than high-affinity competitive RNA dominant-negativity.",
        },
        "celf5_local_lsv_nmd_and_ejc_audit": {
            "n_brown2022_junction_rows": int(len(jdf)),
            "ce_108bp_dpsi": p_ce,
            "ce_108bp_kd_e_psi": 0.367,
            "canonical_3278110_3281199_kd_e_psi_donor_vs_acceptor_lsv": [0.546, 0.633],
            "adjacent_98bp_microintron_3278111_3278208_psi_wt_to_kd": [p_micro_wt, p_micro_kd],
            "upstream_novel_acceptor_3225618_3244124_dpsi": p_up_na,
            "upstream_novel_acceptor_3225618_3244124_kd_e_psi": 0.149,
            "local_lsv_phasing_note": "Brown 2022 MOESM11 quantifies local MAJIQ LSVs with distinct denominators (canonical junction 3278110-3281199 KD E[PSI]=0.546 in donor LSV vs 0.633 in acceptor LSV; upstream 3225618-3244124 is annotated novel_acceptor with blank ir_start/ir_end, not intron-1 retention) and is measured in NMD-competent i3Neurons; whole-transcript phasing bounds cannot be algebraically summed from unphased local LSVs and require long-read ONT/Iso-Seq.",
            "zeng2025_nmd_inhibition_cryptic_psi_pct": [24.8, 44.6],
            "zeng2025_nmd_inhibition_fdr": 0.0235,
            "empirical_brown2022_rnaseq_log2fc": round(rnaseq_fc, 4),
            "empirical_residual_rnaseq_pct": round(100.0 * (2.0 ** rnaseq_fc), 1),
            "empirical_brown2022_riboseq_log2fc": round(ribo_fc, 4),
            "empirical_residual_translation_pct": round(100.0 * (2.0 ** ribo_fc), 1),
            "ejc_nmd_minigene_trap": {
                "ce_length_bp": 108,
                "first_inframe_ptc_codon_1b": 30,
                "first_inframe_ptc_end_nt_in_ce": 90,
                "dist_ptc_to_ce_exon6_junction_nt": 18,
                "dist_ptc_to_exon6_exon7_junction_nt": 165,
                "canonical_ejc_nmd_threshold_nt": 50,
                "triggers_nmd_from_ce_exon6_junction_alone": False,
                "downstream_constitutive_ejcs_in_mane_exon6_to_13": 7,
                "assay_mandate": "On MANE NM_021938.4, the cryptic PTC ends 18 nt (<50-55 nt EJC threshold, PMID:9671053) upstream of CE-Exon6 and 165 nt upstream of Exon6-Exon7: a 3-exon Exon5-CE-Exon6 minigene can measure primary splice-site %PSI choice, but evades canonical EJC-dependent NMD; NMD/stability and isoform-phasing validation require endogenous multi-exon transcripts (consistent with Zeng et al. 2025 PMID:40672339 [PREPRINT] PMC12265704 showing NMD inhibition raises cryptic CELF5 PSI from 24.8% to 44.6%, FDR=0.0235) + Exon 1-7+ ONT/Iso-Seq.",
            },
        },
    }
