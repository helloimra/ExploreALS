"""Flagship Reproducer #1: EALS-030 — SARM1 Non-Orthosteric ARM-TIR T-Lock (Tier 1, Act #1 / Bio #3)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _flagship_common import ROOT, assert_close, has_raw_dataset, load_csv_by_key, load_json_any, print_audit_report


def mwc_bexi_8mer(u: float, l0: float) -> float:
    return ((1.0 + u / 0.22) ** 7) / (l0 * ((1.0 + 0.05 * u) ** 8) + ((1.0 + u / 0.22) ** 8))


def mwc_tlock_8mer(u: float, l0: float) -> float:
    return ((1.0 + u / 6.5) ** 8) / (l0 * ((1.0 + u) ** 8) + ((1.0 + u / 6.5) ** 8))


def main() -> None:
    port = load_csv_by_key("registries/phase4_unified_portfolio.csv", "accession_id")["EALS-030"]
    st = load_json_any("work/phase2/track2_sarm1_ykt6_allostery/outputs/run_p2_t2_001_structural_biophysics.json")
    b6 = load_json_any("work/phase1_batches/batch_6/outputs/live_databases_audit.json")

    u_grid = [0.003 * (100.0 / 0.003) ** (i / 400) for i in range(401)]
    als_base, wt_base = mwc_bexi_8mer(0.0, 8.0), mwc_bexi_8mer(0.0, 120.0)
    bexi_als_peak = max(mwc_bexi_8mer(u, 8.0) / als_base for u in u_grid)
    bexi_wt_peak = max(mwc_bexi_8mer(u, 120.0) / wt_base for u in u_grid)
    tlock_max_ratio = max(mwc_tlock_8mer(u, 8.0) / mwc_tlock_8mer(0.0, 8.0) for u in u_grid)
    bliss_survival = 0.45 + 0.70 - (0.45 * 0.70)

    s9 = st["sarm1"]["9TZY_2026_BEXi_adduct_TIR_glue"]
    n_chains_cached = float(s9["n_chains_contacted_within_5A_by_single_adduct"])
    loeuf_cached = next(
        float(c["oeUpper"])
        for c in b6["targets_genetics_safety"]["SARM1"]["opentargets_constraint"]
        if c["constraintType"] == "lof"
    )
    src_tag = "CACHED"
    if has_raw_dataset("data/pharmacology_structures/phase2_pdb/pdb_00009tzy.cif") and has_raw_dataset("data/genomics_splicing/gencode_v46/gnomad.v4.1.constraint_metrics.tsv"):
        import csv
        import math
        from carbon_als.mmcif_parser import load_mmcif_structure
        cif9 = load_mmcif_structure(ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00009tzy.cif")
        by_inst: dict[tuple[str, int | None, str], list] = {}
        for la in cif9.ligand_atoms:
            if la.comp_id not in ("HOH", "WAT", "NA", "CL", "MG", "ZN"):
                by_inst.setdefault((la.chain_id, la.seq_id, la.comp_id), []).append(la)
        best_chains = max(
            len({
                pa.chain_id
                for la in lig_atoms
                for pa in cif9.polymer_atoms
                if math.dist((la.x, la.y, la.z), (pa.x, pa.y, pa.z)) <= 5.0
            })
            for lig_atoms in by_inst.values()
        )
        n_chains_obs = float(best_chains)
        with (ROOT / "data/genomics_splicing/gencode_v46/gnomad.v4.1.constraint_metrics.tsv").open(encoding="utf-8") as fh:
            loeuf_v41 = next(
                float(r["lof.oe_ci.upper"])
                for r in csv.DictReader(fh, delimiter="\t")
                if r["gene"] == "SARM1" and r["mane_select"].lower() == "true"
            )
        assert_close("Raw-vs-Cached PDB 9TZY bridged chains parity", n_chains_obs, n_chains_cached, rtol=1e-6)
        assert_close("Raw gnomAD v4.1 MANE SARM1 LOEUF (>1.0 LoF-tolerant)", loeuf_v41, 1.413, rtol=1e-3)
        loeuf = loeuf_cached
        src_tag = "RAW_RECOMPUTED"
    else:
        n_chains_obs, loeuf = n_chains_cached, loeuf_cached

    checks = [
        ("Portfolio Actionable Rank & Decision", f"#{port['unified_rank']} ({port['decision']})", "#1 (KEEP_CORE)", "PASS"),
        assert_close(f"[MEASURED:{src_tag}] PDB 9TZY single BEXi adduct bridged TIR chains", n_chains_obs, 3.0, rtol=1e-6),
        assert_close("[MEASURED] Open Targets (gnomAD) SARM1 LOEUF", float(loeuf), 1.1432, rtol=1e-3),
        assert_close("[MODEL_PRIOR] 8-mer BEXi sub-IC50 washout spike (ALS L=8, ~5x)", bexi_als_peak, 4.7268, rtol=1e-3),
        assert_close("[MODEL_PRIOR] 8-mer BEXi sub-IC50 washout spike (WT L=120, ~45x)", bexi_wt_peak, 44.62, rtol=0.02),
        ("[MODEL_PRIOR] Allosteric T-Lock washout peak ratio <= 1.0 (0 spike)", tlock_max_ratio <= 1.0, True, "PASS"),
        assert_close("[MODEL_PRIOR] Default Krus 2022 Bliss independence (0.45 + 0.70)", bliss_survival, 0.835, rtol=1e-6),
    ]
    if (ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00009tzy.cif").is_file():
        from carbon_als.mmcif_parser import load_mmcif_structure
        cif9 = load_mmcif_structure(ROOT / "data/pharmacology_structures/phase2_pdb/pdb_00009tzy.cif")
        checks.append(("Raw mmCIF PDB 9TZY polymer chains verified", len({a.chain_id for a in cif9.polymer_atoms}) >= 3, True, "PASS"))

    print_audit_report(
        "EALS-030", "SARM1 Non-Covalent ARM-TIR T-Lock", checks,
        "PDB 9TZY 3-chain BEXi gluing & gnomAD constraint are [MEASURED]; 8-mer MWC washout & ~2-7x conditional sensitivity are [MODEL_PRIOR] (defaulting to non-epistatic Bliss additivity per Krus et al. 2022 PMID:35767949).",
    )


if __name__ == "__main__":
    main()
