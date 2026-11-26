"""Checkpoint 2.5 addendum: NYGC genotype-stratified CGAS, 6MJW ortholog pocket alignment, and staged 3'-UTR APA audit."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from Bio.Align import PairwiseAligner
import numpy as np
import pandas as pd
from scipy import stats

from carbon_als.loaders import assert_unique_donors, read_xlsx_sparse_safe, resolve_col, resolve_dataset_path
from carbon_als.mmcif_parser import load_mmcif_structure

HC_Q8N884 = (
    "MQPWHGKAMQRASEAGATAPKASARNARGAPMDPTESPAAPEAALPKAGKFGPARKSGSRQKKSAPDTQERPPVRATGARAKKAPQRAQDTQPSDATSAP"
    "GAEGLEPPAAREPALSRAGSCRQRGARCSTKPRPPPGPWDVPSPGLPVSAPILVRRDAAPGASKLRAVLEKLKLSRDDISTAAGMVKGVVDHLLLRLKC"
    "DSAFRGVGLLNTGSYYEHVKISAPNEFDVMFKLEVPRIQLEEYSNTRAYYFVKFKRNPKENPLSQFLEGEILSASKMLSKFRKIIKEEINDIKDTDVIMK"
    "RKRGGSPAVTLLISEKISVDITLALESKSSWPASTQEGLRIQNWLSAKVRKQLRLKPFYLVPKHAKEGNGFQEETWRLSFSHIEKEILNNHGKSKTCCEN"
    "KEEKCCRKDCLKLMKYLLEQLKERFKDKKHLDKFSSYHVKTAFFHVCTQNPQDSQWDRKDLGLCFDNCVTYFLQCLRTEKLENYFIPEFNLFSSNLIDKR"
    "SKEFLTKQIEYERNNEFPVFDEF"
)
MC_Q8C6L5 = (
    "MEDPRRRTTAPRAKKPSAKRAPTQPSRTRAHAESCGPQRGARSRRAERDGDTTEKPRAPGPRVHPARATELTKDAQPSAMDAAGATARPAVRVPQQQAIL"
    "DPELPAVREPQPPADPEARKVVRGPSHRRGARSTGQPRAPRGSRKEPDKLKKVLDKLRLKRKDISEAAETVNKVVERLLRRMQKRESEFKGVEQLNTGSY"
    "YEHVKISAPNEFDVMFKLEVPRIELQEYYETGAFYLVKFKRIPRGNPLSHFLEGEVLSATKMLSKFRKIIKEEVKEIKDIDVSVEKEKPGSPAVTLLIRN"
    "PEEISVDIILALESKGSWPISTKEGLPIQGWLGTKVRTNLRREPFYLVPKNAKDGNSFQGETWRLSFSHTEKYILNNHGIEKTCCESSGAKCCRKECLKL"
    "MKYLLEQLKKEFQELDAFCSYHVKTAIFHMWTQDPQDSQWDPRNLSSCFDKLLAFFLECLRTEKLDHYFIPKFNLFSQELIDRKSKEFLSKKIEYERNNG"
    "FPIFDKL"
)
AA3_TO_1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}
GENO_PANEL = ["CGAS", "IFI16", "STING1", "PSMB8", "HLA-A", "B2M", "TBK1", "OPTN", "STAT1", "STAT2", "ISG15"]
APA_SYMS = {"CGAS", "MB21D1", "STING1", "TMEM173", "IFI16", "PSMB8", "TBK1", "OPTN"}
APA_ENS = {"ENSG00000164430", "ENSG00000184584", "ENSG00000163565", "ENSG00000204264", "ENSG00000183735", "ENSG00000123240"}


def _contrast_pair(t3, df: pd.DataFrame, g: str, case_mask: pd.Series, ctrl_mask: pd.Series, covs: list[str]) -> dict[str, Any]:
    sub = df.loc[case_mask | ctrl_mask].copy()
    is_case = case_mask.loc[sub.index]
    x, y = sub.loc[is_case, g], sub.loc[~is_case, g]
    ols = t3._ols_adj(sub, g, is_case, covs) if (len(x) >= 3 and len(y) >= 3) else {}
    return {
        "n_case": int(len(x)), "n_ref": int(len(y)),
        "mean_case_log2cpm": round(float(x.mean()), 4), "mean_ref_log2cpm": round(float(y.mean()), 4),
        "raw_diff_log2cpm": round(float(x.mean() - y.mean()), 4),
        "welch_p": float(stats.ttest_ind(x, y, equal_var=False).pvalue) if (len(x) >= 2 and len(y) >= 2) else None,
        "mwu_p": float(stats.mannwhitneyu(x, y, alternative="two-sided").pvalue) if (len(x) >= 2 and len(y) >= 2) else None,
        "gc_cellcomp_rin_ols": ols,
    }


def _nygc_region_genotype(t3, expr: pd.DataFrame, s_sheet: str, d_sheet: str, label: str) -> dict[str, Any]:
    p_on = resolve_dataset_path("DS001_ONEILL", verify_hash=True)
    samp_df, donor_df = read_xlsx_sparse_safe(p_on, s_sheet, 2), read_xlsx_sparse_safe(p_on, d_sheet, 2)
    s_mot = samp_df.loc[samp_df[resolve_col(samp_df, "Sample")].astype(str).isin(expr.index) & samp_df[resolve_col(samp_df, "Group")].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    rin_c = resolve_col(s_mot, "RIN")
    s_mot[rin_c] = pd.to_numeric(s_mot[rin_c], errors="coerce")
    d_mot = donor_df.loc[donor_df[resolve_col(donor_df, "Group")].isin(["ALS", "ALS+FTD", "CTL", "CONTROL"])].copy()
    c9_c, mut_c, sub_c, pid_c = resolve_col(d_mot, "C9 repeat expanded, >=30"), resolve_col(d_mot, "PatientMutation"), resolve_col(d_mot, "PatientSubtype"), resolve_col(d_mot, "PatientID")
    d_map = d_mot.assign(
        stratum=np.where(d_mot[resolve_col(d_mot, "Group")].astype(str).str.upper().isin(["CTL", "CONTROL"]), "Control", d_mot[sub_c].astype(str)),
        c9_status=d_mot[c9_c].astype(str).str.strip(),
        mutation=d_mot[mut_c].astype(str).str.strip(),
    )[[pid_c, "stratum", "c9_status", "mutation"]].drop_duplicates(subset=[pid_c])
    don = s_mot[["Sample", "Patient ID", rin_c]].merge(expr, left_on="Sample", right_index=True).groupby("Patient ID", as_index=False)[[*expr.columns, rin_c]].mean().merge(d_map, left_on="Patient ID", right_on=pid_c, how="inner")
    assert_unique_donors(don["Patient ID"].tolist(), f"NYGC_GENO_{label}")
    don = don.loc[don["stratum"].str.startswith("ALS-") | (don["stratum"] == "Control")].copy()
    don["_neuron_idx"] = don[["RBFOX3", "SNAP25", "SLC17A7"]].mean(axis=1)
    don["_glia_idx"] = don[["AIF1", "AQP4", "MOG"]].mean(axis=1)
    covs = ["_sample_gc_index", "_neuron_idx", "_glia_idx", rin_c]
    is_ctrl = don["stratum"] == "Control"
    is_als = don["stratum"].str.startswith("ALS-")
    is_c9 = is_als & ((don["c9_status"] == "Yes") | (don["mutation"].str.upper() == "C9ORF72"))
    is_sod1_fus = is_als & don["mutation"].str.upper().isin({"SOD1", "FUS"})
    is_non_c9 = is_als & (~is_c9) & (~is_sod1_fus)
    is_strict_c9neg = is_non_c9 & (don["c9_status"] == "No")
    geno_lbl = np.select([is_ctrl, is_c9, is_sod1_fus, is_strict_c9neg, is_non_c9], ["Control", "C9orf72_ALS", "SOD1_FUS_ALS", "Confirmed_C9neg_nonSOD1_ALS", "Unscreened_NA_nonSOD1_ALS"], default="Other")
    don["geno_group"] = geno_lbl
    xtab = don.groupby(["geno_group", "stratum"]).size().unstack(fill_value=0).to_dict(orient="index")
    genes_out = {
        g: {
            "non_c9_non_sod1_als_vs_ctrl": _contrast_pair(t3, don, g, is_non_c9, is_ctrl, covs),
            "confirmed_c9neg_non_sod1_als_vs_ctrl": _contrast_pair(t3, don, g, is_strict_c9neg, is_ctrl, covs),
            "c9orf72_als_vs_ctrl": _contrast_pair(t3, don, g, is_c9, is_ctrl, covs),
            "c9orf72_als_vs_non_c9_non_sod1_als": _contrast_pair(t3, don, g, is_c9, is_non_c9, covs),
            "sod1_tdp43neg_als_vs_ctrl": _contrast_pair(t3, don, g, is_sod1_fus, is_ctrl, covs),
            "sod1_tdp43neg_als_vs_non_c9_als": _contrast_pair(t3, don, g, is_sod1_fus, is_non_c9, covs),
        }
        for g in GENO_PANEL if g in don.columns
    }
    return {
        "n_total_donors": int(len(don)),
        "genotype_counts": {k: int(v) for k, v in pd.Series(geno_lbl).value_counts().items()},
        "mutation_breakdown_in_sod1_fus_stratum": {k: int(v) for k, v in don.loc[is_sod1_fus, "mutation"].value_counts().items()},
        "genotype_by_subtype_crosstab": xtab,
        "genes": genes_out,
    }


def compute_nygc_genotype_stratified_cgas(t3, expr: pd.DataFrame) -> dict[str, Any]:
    return {
        "spinal_cord": _nygc_region_genotype(t3, expr, "TableS1G", "TableS1H", "Spinal"),
        "motor_cortex": _nygc_region_genotype(t3, expr, "TableS1B", "TableS1C", "Cortex"),
    }


def compute_cgas_ortholog_6mjw_alignment(root: Path, mmcif_6mjw: dict[str, Any]) -> dict[str, Any]:
    st = load_mmcif_structure(root / "data" / "pharmacology_structures" / "phase4_pdb" / "pdb_00006mjw.cif")
    construct_muts = [
        {"auth_seq_id": sid, "pdb_resn": resn, "uniprot_q8n884_aa": HC_Q8N884[sid - 1]}
        for (_, sid, resn) in sorted(st.residue_groups("A"))
        if 1 <= sid <= len(HC_Q8N884) and HC_Q8N884[sid - 1] != AA3_TO_1.get(resn, "?")
    ]
    aligner = PairwiseAligner(mode="global", match_score=2.0, mismatch_score=-1.0, open_gap_score=-10.0, extend_gap_score=-0.5)
    aln = aligner.align(HC_Q8N884, MC_Q8C6L5)[0]
    h_to_m: dict[int, tuple[int | None, str]] = {}
    hi = mi = 0
    for hc, mc in zip(aln[0], aln[1]):
        if hc != "-":
            hi += 1
        if mc != "-":
            mi += 1
        if hc != "-":
            h_to_m[hi] = (mi, mc) if mc != "-" else (None, "-")
    cat_ident = sum(1 for p in range(157, 523) if h_to_m[p][1] == HC_Q8N884[p - 1])
    contacts = mmcif_6mjw["contacts_le_4A"]["JUJ"]
    pocket_map = [
        {
            "human_pos": c["auth_seq_id"], "human_aa": HC_Q8N884[c["auth_seq_id"] - 1], "pdb_resn": c["resn"],
            "min_dist_to_JUJ_A": c["min_dist_A"], "mouse_pos": h_to_m[c["auth_seq_id"]][0],
            "mouse_aa": h_to_m[c["auth_seq_id"]][1], "conserved": HC_Q8N884[c["auth_seq_id"] - 1] == h_to_m[c["auth_seq_id"]][1],
        }
        for c in contacts
    ]
    dna_spine = [
        {"human_pos": p, "human_aa": HC_Q8N884[p - 1], "mouse_pos": h_to_m[p][0], "mouse_aa": h_to_m[p][1], "conserved": HC_Q8N884[p - 1] == h_to_m[p][1]}
        for p in (187, 195)
    ]
    return {
        "human_uniprot": {"accession": "Q8N884", "length_aa": len(HC_Q8N884)},
        "mouse_uniprot": {"accession": "Q8C6L5", "length_aa": len(MC_Q8C6L5)},
        "catalytic_domain_157_522_identity_pct": round(100.0 * cat_ident / (522 - 157 + 1), 2),
        "pdb_6mjw_crystallization_construct_mutations_vs_Q8N884": construct_muts,
        "g150_juj_pocket_le_4A_ortholog_conservation": {
            "n_contacts_le_4A": len(pocket_map),
            "n_conserved_human_vs_mouse": sum(1 for r in pocket_map if r["conserved"]),
            "n_divergent_human_vs_mouse": sum(1 for r in pocket_map if not r["conserved"]),
            "divergent_pocket_residues": [f"h{r['human_aa']}{r['human_pos']}->m{r['mouse_aa']}{r['mouse_pos']} ({r['min_dist_to_JUJ_A']} A)" for r in pocket_map if not r["conserved"]],
            "residues": pocket_map,
        },
        "dna_length_specificity_spine_pmid_30007416": dna_spine,
    }


def compute_staged_apa_audit() -> dict[str, Any]:
    out: dict[str, Any] = {"zeng2025_ds_zeng_apa": {}, "bryce_smith2025_ds_bryce_apa": {}}
    pz = resolve_dataset_path("DS_ZENG_APA", verify_hash=True)
    for sh, cols in [("S1", ["Gene_Name"]), ("S2", ["gene_name"]), ("S3", ["gene_id", "gene_name"]), ("S4", ["gene_id", "gene_name"]), ("S5", ["gene"]), ("S6", ["gene_name"])]:
        df = read_xlsx_sparse_safe(pz, sh, 1)
        m = pd.Series(False, index=df.index)
        for c in cols:
            rc = resolve_col(df, c)
            s = df[rc].astype(str).str.strip()
            m = m | s.str.upper().isin(APA_SYMS) | s.str.split(".").str[0].isin(APA_ENS)
        out["zeng2025_ds_zeng_apa"][sh] = {"n_rows_scanned": int(len(df)), "matches": df.loc[m].to_dict(orient="records")}
    pb = resolve_dataset_path("DS_BRYCE_APA", verify_hash=True)
    for sh, cols in [("Supplementary_Table_2", ["le_id", "gene_name"]), ("Supplementary_Table_3", ["le_id", "gene_name"]), ("Supplementary_Table_5", ["le_id", "gene_name"]), ("Supplementary_Table_6", ["gene_id", "gene_name"])]:
        df = pd.read_excel(pb, sheet_name=sh, header=0)
        m = pd.Series(False, index=df.index)
        for c in cols:
            rc = resolve_col(df, c)
            s = df[rc].astype(str).str.strip()
            m = m | s.str.upper().isin(APA_SYMS) | s.str.split(".").str[0].str.split("_").str[0].isin(APA_ENS)
        keep_cols = [resolve_col(df, c) for c in cols] + [c for c in df.columns if c in {"event_type", "experiment_name", "pvalue", "padj", "delta_PPAU_treatment_control", "log2FoldChange"}]
        out["bryce_smith2025_ds_bryce_apa"][sh] = {"n_rows_scanned": int(len(df)), "matches": df.loc[m, list(dict.fromkeys(keep_cols))].to_dict(orient="records")}
    return out
