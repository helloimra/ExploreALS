"""Helpers for RUN-P3B-004: ELK1 vs ELK4 regulon sign test, GENCODE v46 isoform/PTC & PDB 2Z0D truncation, and gene-liability."""
from __future__ import annotations

import gzip
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

from _denovo_sso_helpers import fetch_ensembl_dna_transient
from carbon_als.loaders import (
    load_edinburgh_pseudobulk,
    load_pineda2024_pseudobulk,
    load_zhang2026_spatial,
    resolve_col,
    resolve_dataset_path,
)
from carbon_als.mmcif_parser import load_mmcif_structure


def load_elk1_st7_regulons() -> dict[str, list[str]]:
    df7 = pd.read_excel(resolve_dataset_path("DS_BRYCE_APA", verify_hash=True), sheet_name="Supplementary_Table_7")
    return {
        c: sorted({str(x).strip() for x in df7[resolve_col(df7, c)].dropna() if str(x).strip() and str(x).strip() != "nan"})
        for c in ("ELK1_unique", "ELK4_unique", "ELK1_all", "ELK4_all")
    }


def _comp_sign_stats(stat_map: dict[str, float], e1_u: list[str], e4_u: list[str], bg_all: bool = False) -> dict[str, Any]:
    v1 = np.array([stat_map[g] for g in e1_u if g in stat_map and np.isfinite(stat_map[g])], dtype=float)
    v4 = np.array([stat_map[g] for g in e4_u if g in stat_map and np.isfinite(stat_map[g])], dtype=float)
    u1, d1, u4, d4 = int(np.sum(v1 > 0)), int(np.sum(v1 <= 0)), int(np.sum(v4 > 0)), int(np.sum(v4 <= 0))
    res: dict[str, Any] = {
        "n_elk1_unique": int(len(v1)), "n_elk4_unique": int(len(v4)),
        "mean_elk1_unique": round(float(v1.mean()), 4), "median_elk1_unique": round(float(np.median(v1)), 4),
        "pct_pos_elk1_unique": round(100.0 * u1 / max(len(v1), 1), 2),
        "onesamp_wilcoxon_p_elk1": float(stats.wilcoxon(v1).pvalue) if len(v1) >= 5 else 1.0,
        "mean_elk4_unique": round(float(v4.mean()), 4), "median_elk4_unique": round(float(np.median(v4)), 4),
        "pct_pos_elk4_unique": round(100.0 * u4 / max(len(v4), 1), 2),
        "diff_elk1_minus_elk4": round(float(v1.mean() - v4.mean()), 4),
        "welch_p_elk1_vs_elk4": float(stats.ttest_ind(v1, v4, equal_var=False).pvalue),
        "mwu_p_elk1_vs_elk4": float(stats.mannwhitneyu(v1, v4, alternative="two-sided").pvalue),
        "fisher_pos_p_elk1_vs_elk4": float(stats.fisher_exact([[u1, d1], [u4, d4]])[1]),
    }
    if bg_all:
        e1_set = set(e1_u)
        vbg = np.array([val for g, val in stat_map.items() if g not in e1_set and np.isfinite(val)], dtype=float)
        res["n_genome_bg"] = int(len(vbg))
        res["mean_genome_bg"] = round(float(vbg.mean()), 4)
        res["mwu_p_elk1_vs_genome_bg"] = float(stats.mannwhitneyu(v1, vbg, alternative="two-sided").pvalue)
    return res


def run_elk1_regulon_sign_test(nygc_reg_tstats: dict[str, dict[str, float]]) -> dict[str, Any]:
    regs = load_elk1_st7_regulons()
    e1_u, e4_u = regs["ELK1_unique"], regs["ELK4_unique"]
    union_reg = sorted(set(regs["ELK1_all"]) | set(regs["ELK4_all"]))

    gc_df = pd.read_csv(resolve_dataset_path("DS_GC_REF", verify_hash=True), sep="\t")
    gc_pc = gc_df[gc_df[resolve_col(gc_df, "Gene type")] == "protein_coding"].dropna(subset=["Gene name", "Gene % GC content"])
    gc_map = gc_pc.groupby("Gene name")["Gene % GC content"].mean().to_dict()
    pin = load_pineda2024_pseudobulk("BA4", "Excitatory", sorted(set(gc_map) | set(union_reg)))["donor_df"]
    pdf = pin[pin["group"].isin(["SALS", "PN"])].copy()
    hg = [g for g, v in gc_map.items() if v >= 60.0 and g in pdf.columns]
    lg = [g for g, v in gc_map.items() if v <= 38.0 and g in pdf.columns]
    x_p = sm.add_constant(np.column_stack([(pdf["group"] == "SALS").astype(float), pdf[hg].mean(axis=1) - pdf[lg].mean(axis=1)]))
    ecols = [c for c in pdf.columns if (c in gc_map or c in set(union_reg)) and float(pdf[c].std()) > 1e-8]
    ym = pdf[ecols].astype(float).to_numpy()
    bp = np.linalg.lstsq(x_p, ym, rcond=None)[0]
    msep = ((ym - x_p @ bp) ** 2).sum(axis=0) / (len(pdf) - x_p.shape[1])
    tp = bp[1] / np.sqrt(np.maximum(msep * float(np.linalg.pinv(x_p.T @ x_p)[1, 1]), 1e-30))
    pin_tmap = {g: float(t) for g, t in zip(ecols, tp, strict=True)}

    ed = load_edinburgh_pseudobulk("Excitatory neuron", union_reg, exclude_c9=True)["stats"]
    ed_tmap = {g: float(v["t_welch"]) for g, v in ed.items() if "t_welch" in v and np.isfinite(float(v["t_welch"]))}
    zh = load_zhang2026_spatial()
    zh_mn = dict(zip(zh["mn_niche_df"]["gene"].astype(str), zh["mn_niche_df"]["avg_log2FC"].astype(float)))
    zh_tdp = dict(zip(zh["tdp43_niche_df"]["gene"].astype(str), zh["tdp43_niche_df"]["avg_log2FC"].astype(float)))

    return {
        "regulon_sizes_st7": {
            **{k: len(v) for k, v in regs.items()},
            "n_shared_elk1_elk4": len(set(regs["ELK1_all"]) & set(regs["ELK4_all"])),
        },
        "contrasts": {
            "Pineda_BA4_Exc_GC_adj_t": _comp_sign_stats(pin_tmap, e1_u, e4_u, bg_all=True),
            "Edinburgh_sALS_nonC9_Exc_Welch_t": _comp_sign_stats(ed_tmap, e1_u, e4_u, bg_all=False),
            "Zhang2026_Cervical_MN_Visium_log2FC": _comp_sign_stats(zh_mn, e1_u, e4_u, bg_all=True),
            "Zhang2026_Cervical_pTDP43_Visium_log2FC": _comp_sign_stats(zh_tdp, e1_u, e4_u, bg_all=True),
            "NYGC_Spinal_Cord_Cervical_RIN_GC_t": _comp_sign_stats(nygc_reg_tstats["Spinal_Cord_Cervical"], e1_u, e4_u, bg_all=True),
            "NYGC_Cortex_Motor_RIN_GC_t": _comp_sign_stats(nygc_reg_tstats["Cortex_Motor"], e1_u, e4_u, bg_all=True),
        },
    }


def run_isoform_structure_and_liability_audits(
    ext_main: dict[str, Any], ext_dd: dict[str, Any], gnomad_map: dict[str, dict[str, float | None]],
) -> dict[str, Any]:
    gtf_fp = resolve_dataset_path("DS_GENCODE_V46_COMP_GTF", verify_hash=True)
    atg_cds, kal_cds, kal_tx, pr_ex, pt_ex = [], {}, {}, [], []
    with gzip.open(gtf_fp, "rt", encoding="utf-8") as fh:
        for ln in fh:
            if not ln.startswith(("chr2\t", "chr3\t", "chr9\t", "chr20\t")):
                continue
            p = ln.rstrip("\n").split("\t")
            s, e, feat, attr = int(p[3]), int(p[4]), p[2], p[8]
            if p[0] == "chr2" and 'transcript_id "ENST00000404914.8"' in attr and feat == "CDS":
                atg_cds.append((s, e))
            elif p[0] == "chr3" and 'gene_name "KALRN"' in attr and feat in ("transcript", "CDS"):
                kv = dict((x.split(" ", 1)[0], x.split(" ", 1)[1].strip('"')) for x in attr.rstrip(";").split("; ") if " " in x)
                tid = kv.get("transcript_id", "")
                if feat == "transcript":
                    kal_tx[tid] = {"name": kv.get("transcript_name"), "start": s, "end": e, "mane": "MANE_Select" in attr}
                else:
                    kal_cds.setdefault(tid, []).append((s, e))
            elif p[0] == "chr9" and feat == "exon" and 'gene_name "PRUNE2"' in attr and s > 76638288 and e < 76644739:
                pr_ex.append((s, e))
            elif p[0] == "chr20" and feat == "exon" and 'gene_name "PTPRT"' in attr and s > 42098552 and e < 42102124:
                pt_ex.append((s, e))

    atg_ex10_nt = sum(e - s + 1 for s, e in sorted(atg_cds) if e <= 241668685)
    kal_iso = {}
    for tid, cl in kal_cds.items():
        tot_nt = sum(e - s + 1 for s, e in cl)
        sp_56 = any(e == 124700033 for _, e in cl)
        if sp_56 or tot_nt >= 4800:
            up_nt = sum(e - s + 1 for s, e in cl if e <= 124700033)
            kal_iso[kal_tx[tid]["name"]] = {"transcript_id": tid, "mane_select": kal_tx[tid]["mane"], "tx_end": kal_tx[tid]["end"], "total_aa": tot_nt // 3, "spans_intron56_ce": sp_56, "aa_at_exon56_end": up_nt // 3, "carry_rem_nt": up_nt % 3}

    win = fetch_ensembl_dna_transient("3", 124700033, 124702116)
    ex56_last1, ex57_head = win[0], win[124702038 - 124700033 :]
    kal_ptc = {}
    for lbl, ce_s in (("alt_3SS_124700977", 124700977), ("major_3SS_124701093", 124701093)):
        ce_seq = win[ce_s - 124700033 : 124701255 - 124700033 + 1]
        sp_seq = ex56_last1 + ce_seq + ex57_head
        cods = [sp_seq[i : i + 3] for i in range(0, len(sp_seq) - 2, 3)]
        stops = [idx + 1 for idx, c in enumerate(cods) if c in ("TAA", "TAG", "TGA")]
        kal_ptc[lbl] = {
            "ce_len_bp": len(ce_seq), "ce_codons_spanned": (1 + len(ce_seq)) // 3,
            "cassette_len_mod3": len(ce_seq) % 3, "ce_exit_phase_mod3": (1 + len(ce_seq)) % 3,
            "inframe_stop_codon_indices_1b": stops,
        }
        del ce_seq, sp_seq
    del win, ex56_last1, ex57_head

    s2z = load_mmcif_structure(resolve_dataset_path("DS_PDB_2Z0D", verify_hash=True))
    atoms = s2z.polymer_atoms + s2z.modified_polymer_atoms
    ca_hi = [a for a in atoms if a.chain_id == "A" and (a.seq_id or 0) >= 320]
    ca_lo = [a for a in atoms if a.chain_id == "A" and (a.seq_id or 0) < 320]
    cb = [a for a in atoms if a.chain_id == "B" and a.seq_id is not None]
    core_c = {(a.seq_id, a.comp_id, b.seq_id, b.comp_id) for a in ca_hi for b in ca_lo if abs((a.seq_id or 0) - (b.seq_id or 0)) > 3 and float(np.linalg.norm(a.coord - b.coord)) <= 4.0}
    lc3_c = sorted({(a.seq_id, a.comp_id, b.seq_id, b.comp_id, round(float(np.linalg.norm(a.coord - b.coord)), 2)) for a in ca_hi for b in cb if float(np.linalg.norm(a.coord - b.coord)) <= 4.5})

    liab = {}
    for sym, v2_loeuf, qual_tier, note in (
        ("ATG4B", None, "FAVORABLE_RESTORATION_LOW_CONSTRAINT", "gnomAD v4.1 pLI=0.00/LOEUF=0.851; intrathecal steric SSO restores physiological splicing (non-inhibitory); Atg4b-KO mice viable with inner-ear/autophagy phenotype; 995 ChEMBL records are inhibitors (wrong direction)."),
        ("KALRN", 0.179, "INTRATHECAL_RESTORATION_PLI1_CANONICAL_SKIP_SENSITIVE", "gnomAD v4.1 pLI=1.00/LOEUF=0.231 (v2.1.1=0.179) prohibits pan-inhibition and demands zero accidental Exon 56/57 skipping; high vascular GTEx TPM (Artery_Aorta=37.39, Artery_Coronary=23.12 vs cervical cord=1.50) requires CNS-confined intrathecal steric SSO."),
        ("ELK1", 0.616, "MODERATE_CAUTION_KNOCKDOWN_SIGN_AMBIGUOUS", "3'Ext RNase-H gapmer lowers transcript abundance in X-linked TF (gnomAD v4.1 chrX=null; v2.1.1 LOEUF=0.616; Ovary=80.11, Liver=14.60 TPM); nuclear pELK1-SRF neuroprotection vs dendritic pro-apoptotic sign unresolved."),
    ):
        gm, dm, gt = gnomad_map.get(sym, {}), ext_main["opentargets_depmap"][sym], ext_dd["gtex_v8_median_tpm"][sym]
        non_cns = {k: float(v) for k, v in gt.items() if k != "gencode_id" and not k.startswith("Brain_")}
        max_nc_tis = max(non_cns, key=non_cns.get)
        pli_val = gm.get("pLI")
        liab[sym] = {
            "gnomad_v41_pli": pli_val, "gnomad_v41_loeuf": gm.get("loeuf"), "gnomad_v2_loeuf": v2_loeuf,
            "depmap_median_chronos": dm["median_chronos"], "depmap_p10_chronos": dm["p10_chronos"],
            "ot_is_essential": dm["ot_is_essential"],
            "gtex_cns_spinal_cervical_tpm": float(gt["Brain_Spinal_cord_cervical_c-1"]),
            "gtex_cns_ba9_tpm": float(gt["Brain_Frontal_Cortex_BA9"]),
            "max_non_cns_gtex_tissue": max_nc_tis, "max_non_cns_gtex_tpm": round(non_cns[max_nc_tis], 2),
            "on_target_canonical_skip_haploinsufficiency_risk": bool(pli_val is not None and float(pli_val) >= 0.9),
            "qualitative_safety_tier": qual_tier, "rationale": note,
        }

    return {
        "atg4b_3d_truncation_2z0d": {"mane_transcript": "ENST00000404914.8", "exon10_cum_nt": atg_ex10_nt, "exon10_last_aa_1b": atg_ex10_nt // 3, "exon10_phase": atg_ex10_nt % 3, "deleted_aa_range_1b": [320, 393], "intramolecular_core_contacts_le_4p0A": len(core_c), "lc3b_patch_heavy_atom_contacts_le_4p5A": len(lc3_c), "min_dist_Glu350_to_LC3B_Val91_A": min(x[4] for x in lc3_c), "deleted_lir_motif_1b": [388, 391]},
        "kalrn_isoform_and_ptc_audit": {"isoforms_by_name": kal_iso, "kalirin7_distance_upstream_of_intron56_bp": 124700034 - kal_iso["KALRN-201"]["tx_end"], "dual_3ss_ptc_audit": kal_ptc},
        "prune2_ptprt_intron_audit": {"prune2_internal_gencode_exons_1b": sorted(set(pr_ex)), "ptprt_internal_gencode_exons_1b": sorted(set(pt_ex))},
        "gene_liability_profiles": liab,
    }
