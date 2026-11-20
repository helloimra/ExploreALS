"""RUN-P2-T4-001: C007 IL1RL1 (sST2 vs ST2L) Vascular/Isoform/4KC3 Model & C018 C1q Spatial/Intrathecal Fab PK."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (ROOT, SRC, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _il1rl1_pas_cterm_helper import (  # noqa: E402
    SEQ_GUARD_RE,
    audit_4kc3_disulfides_and_cys327,
    scan_gencode_v46_skecf_cterminome_and_zone1_pas,
)
from _offtarget_helpers import sanitize_for_strict_json  # noqa: E402
from carbon_als.loaders import (  # noqa: E402
    load_edinburgh_pseudobulk,
    load_pineda2024_pseudobulk,
    load_zhang2026_spatial,
)
from carbon_als.mmcif_parser import load_mmcif_structure  # noqa: E402

CACHE = ROOT / "work" / "phase2" / "track4_celltype_isoform_resolution" / "cache"
OUT_DIR = ROOT / "work" / "phase2" / "track4_celltype_isoform_resolution" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def solve_il33_st2_mass_action(
    il33_tot_pm: float,
    sst2_tot_pm: float,
    st2l_tot_pm: float,
    drug_nm: float = 0.0,
    kd_sst2_pm: float = 26.0,
    kd_st2l_pm: float = 28.0,
    kd_drug_sst2_pm: float = 50.0,
    kd_drug_st2l_pm: float | None = None,
) -> dict[str, float]:
    """Exact coupled mass-action solver for free IL-33 and Treg ST2L occupancy under pan-ST2 vs sST2-selective mAb."""
    d_pm = drug_nm * 1000.0
    eff_sst2_avail = sst2_tot_pm / (1.0 + d_pm / kd_drug_sst2_pm) if d_pm > 0 else sst2_tot_pm
    eff_st2l_avail = st2l_tot_pm / (1.0 + d_pm / kd_drug_st2l_pm) if (d_pm > 0 and kd_drug_st2l_pm is not None) else st2l_tot_pm

    def residual(free_il33: float) -> float:
        b_s = eff_sst2_avail * free_il33 / (kd_sst2_pm + free_il33)
        b_l = eff_st2l_avail * free_il33 / (kd_st2l_pm + free_il33)
        return free_il33 + b_s + b_l - il33_tot_pm

    free_l = float(optimize.brentq(residual, 0.0, il33_tot_pm))
    bound_st2l = eff_st2l_avail * free_l / (kd_st2l_pm + free_l)
    bound_sst2 = eff_sst2_avail * free_l / (kd_sst2_pm + free_l)
    return {
        "free_il33_pM": round(free_l, 4),
        "sst2_sequestered_il33_pM": round(bound_sst2, 4),
        "active_treg_st2l_il33_pM": round(bound_st2l, 4),
        "treg_st2l_fractional_signaling_pct": round(100.0 * bound_st2l / max(st2l_tot_pm, 1e-9), 2),
    }


def analyze_4kc3_interface() -> dict[str, Any]:
    cif = ROOT / "data" / "pharmacology_structures" / "phase2_pdb" / "pdb_00004kc3.cif"
    parsed = load_mmcif_structure(cif)
    rg = parsed.residue_groups()
    chains = sorted({k[0] for k in rg})
    c_sizes = {c: len([k for k in rg if k[0] == c]) for c in chains}
    st2_c = max(c_sizes, key=lambda c: c_sizes[c])
    il33_c = min(c_sizes, key=lambda c: c_sizes[c])
    st2_res = {k: np.array([a.coord for a in v]) for k, v in rg.items() if k[0] == st2_c}
    il33_atoms = np.array([a.coord for k, v in rg.items() if k[0] == il33_c for a in v])
    contacts: list[dict[str, Any]] = []
    for (_, seq, comp), coords in sorted(st2_res.items(), key=lambda x: x[0][1]):
        dmin = float(np.min(np.linalg.norm(coords[:, None, :] - il33_atoms[None, :, :], axis=-1)))
        if dmin <= 4.0:
            dom = "D1_orthosteric" if seq <= 110 else ("D2_orthosteric" if seq <= 205 else "D3_membrane_proximal")
            contacts.append({"auth_seq_id": seq, "comp_id": comp, "domain": dom, "min_dist_to_il33_A": round(dmin, 2)})
    seqs = sorted(k[1] for k in st2_res)
    return {
        "pdb_id": "4KC3",
        "st2_chain": st2_c,
        "il33_chain": il33_c,
        "st2_resolved_seq_span": [seqs[0], seqs[-1]],
        "n_st2_contact_residues_le_4A": len(contacts),
        "domain_contact_counts": {
            d: sum(1 for c in contacts if c["domain"] == d)
            for d in ("D1_orthosteric", "D2_orthosteric", "D3_membrane_proximal")
        },
        "sst2_unique_cterm_divergence_after_ectodomain_seq": seqs[-1],
        "top_closest_contacts": sorted(contacts, key=lambda x: x["min_dist_to_il33_A"])[:12],
        "cys327_and_disulfide_audit": audit_4kc3_disulfides_and_cys327(cif, st2_c),
    }


def parse_il1rl1_gtf() -> dict[str, Any]:
    raw_txt = (CACHE / "gtf_IL1RL1.json").read_text(encoding="utf-8")
    txs = json.loads(raw_txt[raw_txt.index("[") :])
    records = txs if isinstance(txs, list) else txs.get("transcripts", [txs])
    st2l_txs, sst2_txs = [], []
    for tx in records:
        exons = tx.get("exons", [])
        n_ex = int(tx.get("num_exons", len(exons)))
        # AlphaGenome gtf_IL1RL1.json stores 0-based BED start and 1-based end (width == end - start_0b);
        # convert start -> start + 1 to match official 1-based closed GENCODE v46 GTF coordinates!
        s0 = int(exons[0]["start"]) + 1 if exons and int(exons[0].get("width", 0)) == int(exons[0]["end"]) - int(exons[0]["start"]) + 1 else int(exons[0]["start"]) if exons else 0
        sn = int(exons[-1]["start"]) + 1 if exons and int(exons[-1].get("width", 0)) == int(exons[-1]["end"]) - int(exons[-1]["start"]) + 1 else int(exons[-1]["start"]) if exons else 0
        entry = {
            "transcript_id": tx.get("transcript_id"),
            "is_mane_select": bool(tx.get("is_mane_select", False)),
            "chromosome": tx.get("chromosome", "chr2"),
            "strand": tx.get("strand", "+"),
            "start_1b": s0 if exons else int(tx.get("start", 0)) + 1,
            "end_1b": int(tx.get("end", 0)),
            "num_exons": n_ex,
            "first_exon_1b": f"{tx.get('chromosome','chr2')}:{s0}-{exons[0]['end']}" if exons else "",
            "last_exon_1b": f"{tx.get('chromosome','chr2')}:{sn}-{exons[-1]['end']}" if exons else "",
        }
        (st2l_txs if n_ex >= 11 else sst2_txs).append(entry)
    return {"st2l_transmembrane_transcripts": st2l_txs, "sst2_soluble_short_transcripts": sst2_txs}


def model_c1q_cns_vs_systemic_pk() -> list[dict[str, Any]]:
    # Human serum C1q ~180 nM hexamer; CSF C1q ~0.65 nM; Kd = 0.02 nM.
    # Unmodified 48 kDa Fab in 150 mL CSF (~4x/day bulk flow, t1/2 ~12 h) washes out over 28d (56 t1/2 -> <0.001 nM)!
    c0_30mg_nm = (30e-3 / 48000.0) / 0.150 * 1e9  # ~4,167 nM bolus -> decays by 2^-56 over 672 h
    fab_q4w_trough = round(c0_30mg_nm * (0.5 ** (672.0 / 12.0)), 6)
    regimens = [
        ("Systemic_IV_ANX005_75mgkg_q2w_150kDa_IgG4", 6000.0, 9.0, 1.8),
        ("Systemic_SC_Pegcetacoplan_MERIDIAN_C3_Benchmark", 14000.0, 4.5, 0.9),
        ("BBB_TfR_Shuttled_FcSilent_AntiC1q_10mgkg_IV", 320.0, 22.0, 18.0),
        ("Unmodified_Intrathecal_AntiC1q_Fab_30mg_q4w_BulkFlowWashout", 0.001, fab_q4w_trough, fab_q4w_trough * 0.25),
        ("Intrathecal_Pump_or_ECM_Anchored_HLE_AntiC1q_Fab_SteadyState", 0.60, 35.0, 9.5),
    ]
    kd_nm, serum_c1q_nm, csf_c1q_nm, paren_c1q_nm = 0.02, 180.0, 0.65, 1.20
    out = []
    for name, c_ser, c_csf, c_par in regimens:
        # Exact tight-binding Morrison free-antigen fraction
        def free_pct(ag: float, ab: float) -> float:
            b = ag + ab + kd_nm
            comp = 0.5 * (b - np.sqrt(max(b * b - 4.0 * ag * ab, 0.0)))
            return round(100.0 * max(ag - comp, 0.0) / ag, 2)

        s_free = free_pct(serum_c1q_nm, c_ser)
        csf_free = free_pct(csf_c1q_nm, c_csf)
        par_free = free_pct(paren_c1q_nm, c_par)
        out.append({
            "regimen": name,
            "trough_serum_binder_nM": c_ser,
            "trough_csf_binder_nM": c_csf,
            "est_anterior_horn_interstitial_binder_nM": c_par,
            "free_systemic_serum_c1q_pct": s_free,
            "free_csf_c1q_pct": csf_free,
            "free_anterior_horn_c1q_pct": par_free,
            "passes_dual_gate_cns_suppression_ge90_and_serum_sparing_ge95": bool(par_free <= 10.0 and s_free >= 95.0),
        })
    return out


def main() -> None:
    ed_cts = {
        ct: load_edinburgh_pseudobulk(ct, ["IL1RL1", "IL33", "IL1RAP", "C1QA", "C1QB", "C1QC"], region="donor_collapsed")
        for ct in ("Endothelial", "Astrocyte", "Microglia", "Excitatory neuron", "Oligodendrocyte")
    }
    ed_endo_sals = load_edinburgh_pseudobulk("Endothelial", ["IL1RL1", "IL33"], region="donor_collapsed", exclude_c9=True)
    # Within-donor Astrocyte IL33 vs Endothelial IL1RL1 pairing
    m_df = ed_cts["Endothelial"]["donor_df"][["donor_id", "group", "IL1RL1"]].merge(
        ed_cts["Astrocyte"]["donor_df"][["donor_id", "IL33"]], on="donor_id"
    )
    als_m = m_df.loc[m_df["group"] == "ALS"]
    r_nv, p_nv = stats.pearsonr(als_m["IL1RL1"], als_m["IL33"])

    p_ba4_vasc = load_pineda2024_pseudobulk("BA4", "Vascular", ["IL1RL1", "IL33", "IL1RAP"], min_nuclei=5)
    p_ba4_ast = load_pineda2024_pseudobulk("BA4", "Astro", ["IL1RL1", "IL33", "IL1RAP"])
    zh = load_zhang2026_spatial([
        "IL1RL1", "IL33", "IL1RAP", "PECAM1", "CLDN5", "VWF",
        "C1QA", "C1QB", "C1QC", "C1R", "C1S", "C3", "C4B",
        "CHAT", "SLC18A3", "CHRM2", "SLC5A7", "SYP", "NPTX2",
        "LRP1", "CALR", "C1QBP", "FMR1", "G3BP1", "TIA1", "RPL10A",
    ])
    bulk_csf = solve_il33_st2_mass_action(15.0, 5.0, 10.0, drug_nm=0.0)
    healthy = solve_il33_st2_mass_action(15.0, 35.0, 10.0, drug_nm=0.0)
    als_untr = solve_il33_st2_mass_action(15.0, 400.0, 10.0, drug_nm=0.0)
    pan_st2 = solve_il33_st2_mass_action(15.0, 400.0, 10.0, drug_nm=5.0, kd_drug_sst2_pm=50.0, kd_drug_st2l_pm=50.0)
    sel_sst2 = solve_il33_st2_mass_action(15.0, 400.0, 10.0, drug_nm=5.0, kd_drug_sst2_pm=50.0, kd_drug_st2l_pm=None)
    rna_80pct = solve_il33_st2_mass_action(15.0, 80.0, 10.0, drug_nm=0.0)
    pas_cterm = scan_gencode_v46_skecf_cterminome_and_zone1_pas(CACHE)

    avi_snps = json.loads((CACHE / "avi_il1rl1_snps.json").read_text(encoding="utf-8")) if (CACHE / "avi_il1rl1_snps.json").is_file() else []
    atlas_links = json.loads((CACHE / "il1rl1_atlas_links.json").read_text(encoding="utf-8")) if (CACHE / "il1rl1_atlas_links.json").is_file() else {}

    out = {
        "analysis_run_id": "RUN-P2-T4-001",
        "c007_edinburgh_celltype_stats": {ct: res["stats"] for ct, res in ed_cts.items()},
        "c007_edinburgh_non_c9_endothelial": ed_endo_sals["stats"],
        "c007_within_donor_astro_il33_vs_endo_il1rl1_als": {"n_als_paired": int(len(als_m)), "pearson_r": round(float(r_nv), 4), "p_value": float(p_nv)},
        "c007_pineda_ba4_vascular_and_astro": {"BA4_Vascular": p_ba4_vasc["stats"], "BA4_Astro": p_ba4_ast["stats"]},
        "c007_gencode_v46_isoform_coordinates_1based_grch38": parse_il1rl1_gtf(),
        "c007_alphagenome_snps_and_atlas_links": {"avi_records": avi_snps, "atlas_links": atlas_links},
        "c007_pdb_4kc3_structural_epitope": analyze_4kc3_interface(),
        "c007_cterminome_and_zone1_pas_modality_audit": pas_cterm,
        "c007_il33_decoy_sink_mass_action": {
            "bulk_csf_baseline_5pM_sST2": bulk_csf,
            "perivascular_baseline_35pM_sST2": healthy,
            "perivascular_als_endothelial_surge_400pM_sST2": als_untr,
            "pan_st2_d1d2_blocker_astegolimab_5nM": pan_st2,
            "neurovascular_rna_80pct_sst2_suppression_to_80pM": rna_80pct,
            "isoform_selective_sst2_sweeping_mAb_5nM": sel_sst2,
            "biologic_fcrn_note": "Catalytic pH-dependent sweeping requires intact pH-6.0 FcRn salvage (never FcRn-attenuated IHH, which causes 1:1 stoichiometric lysosomal co-degradation); demoted to backup behind intrathecal neurovascular RNA suppression due to Cys327 thiol adduct heterogeneity.",
        },
        "c007_and_c018_zhang2026_cervical_spatial": {
            "mn_niche_6d": zh["mn_niche_df"].to_dict(orient="records"),
            "tdp43_niche_6i": zh["tdp43_niche_df"].to_dict(orient="records"),
        },
        "c018_cns_vs_systemic_c1q_pk_model": model_c1q_cns_vs_systemic_pk(),
    }
    txt = json.dumps(sanitize_for_strict_json(out), indent=2, allow_nan=False)
    assert not SEQ_GUARD_RE.search(txt), "Biosecurity sequence guard failed on RUN-P2-T4-001!"
    (OUT_DIR / "run_p2_t4_001_c007_il1rl1_and_c018_c1q.json").write_text(txt, encoding="utf-8")
    print("SAVED run_p2_t4_001_c007_il1rl1_and_c018_c1q.json")


if __name__ == "__main__":
    main()
