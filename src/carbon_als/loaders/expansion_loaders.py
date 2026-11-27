"""Phase 1–4 Pack C expansion dataset loaders for CarbonALS (v1.5 staging, read-only on v1.4 core).

Hardening invariants (v1.5-prep / Checkpoint 1+):
1. SHA-256 verification parity (`verify_hash=True`) against `EXPANSION_MANIFEST_2026_11.csv`
   + sparse-XML-safe Excel parsing (`read_xlsx_sparse_safe`) for multi-header workbooks.
2. Paired contrast matching (`assert_contrast_pair`) + verified primary-method estimator metadata
   (including verbatim `Ryan 2025` eLife XML polarity for `supp1..4`).
3. Donor-level uniqueness (`assert_unique_donors`), covariate-adjusted OLS (`gc_z` + `sex`/`age`/`pmi`
   with df guards), strictly non-overlapping donor sensitivity mode (`exclude_v14_overlaps=True`),
   genotype stratification, and explicit-family BH-FDR with `p <= fdr` provenance guard.
4. Assay-physics capability registry & Epistemic Asymmetry classifier (`UNPROVEN_ASSAY_BLIND` and
   `UNPROVEN_UNDERPOWERED_OR_NULL` strictly separated from `CHALLENGED_OR_DISCORDANT`).
"""

from __future__ import annotations

import gzip
import json
import math
import re
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from scripts.phase1_batches.batch_runner_utils import _file_matches_sha256

from .guards import (
    ALLOWED_MODALITIES,
    assert_contrast_pair,
    assert_unique_donors,
    read_xlsx_sparse_safe,
    resolve_col,
)

ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "data" / "expansion_2026_11"
PB_DIR = ROOT / "work" / "phase5_pack_c_expansion" / "pseudobulks"
META_DIR = ROOT / "work" / "phase5_pack_c_expansion" / "metadata"
OUT_DIR = ROOT / "work" / "phase5_pack_c_expansion" / "outputs"

EXPANSION_ALLOWED_MODALITIES = ALLOWED_MODALITIES | {
    "INCITE_CAPILLARY_PSEUDOBULK",
    "FANS_TDP43_PSEUDOBULK",
    "PBMC_SCRNA_PSEUDOBULK",
    "CSF_RNASEQ_BULK",
    "BULK_RNASEQ_COUNTS",
    "PROTEOMICS_CSF_OLINK",
    "PROTEOMICS_PLASMA_OLINK",
    "PROTEOMICS_TISSUE_LIMMA",
    "PROTEOMICS_TISSUE_SOLUBLE_INSOLUBLE",
    "PROTEOMICS_TISSUE_TMT_FTLD",
    "PROTEOMICS_MUSCLE_DIA",
    "PHOSPHOPROTEOMICS_TMT",
    "CRISPR_SCREEN_GENOMEWIDE",
    "LONGREAD_NANOPORE_COUNTS",
    "LONGREAD_ISOSEQ_TRANSCRIPTS",
    "SPLICING_COMPENDIUM_MULTIOMIC",
    "SPLICING_LEAFCUTTER_JUNCTIONS",
    "TE_RETROTRANSPOSON_BULK",
    "PROTEIN_IDENTIFICATION_ONLY_NO_QUANT",
    "GWAS_SUMSTATS_GRCH37",
    "EQTL_SQTL_SUMSTATS",
    "EXOME_BURDEN_GENEWIDE",
}

# Verified verbatim from work/phase5_pack_c_expansion/metadata/elife-104057-v1.xml
RYAN2025_SCREEN_META: dict[str, dict[str, str]] = {
    "supp1": {
        "cell_model": "i3Neurons",
        "polarity": "KD_INCREASES_HaloTDP43",
        "estimator": "MAGeCKFlute_RRA_perm_floor_2.2e-5",
        "caption": "MAGeCKFlute robust ranked algorithm (RRA) results for genes that increased Halo-TDP-43 levels in i3Neurons.",
    },
    "supp2": {
        "cell_model": "i3Neurons",
        "polarity": "KD_DECREASES_HaloTDP43",
        "estimator": "MAGeCKFlute_RRA_perm_floor_2.2e-5",
        "caption": "MAGeCKFlute robust ranked algorithm (RRA) results for genes that decreased Halo-TDP-43 levels in i3Neurons.",
    },
    "supp3": {
        "cell_model": "iPSCs",
        "polarity": "KD_INCREASES_HaloTDP43",
        "estimator": "MAGeCKFlute_RRA_perm_floor_2.2e-5",
        "caption": "MAGeCKFlute robust ranked algorithm (RRA) results for genes that increased Halo-TDP-43 levels in induced pluripotent stem cells (iPSCs).",
    },
    "supp4": {
        "cell_model": "iPSCs",
        "polarity": "KD_DECREASES_HaloTDP43",
        "estimator": "MAGeCKFlute_RRA_perm_floor_2.2e-5",
        "caption": "MAGeCKFlute robust ranked algorithm (RRA) results for genes that decreased Halo-TDP-43 levels in induced pluripotent stem cells (iPSCs).",
    },
}

# Assay-physics & independence capability registry (AGENTS.md §2, §4)
ASSAY_PHYSICS_CAPABILITIES: dict[str, dict[str, Any]] = {
    "takeuchi2025_lsc": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "takeuchi2025_ba4": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "nygc_gse330130_lsc": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": False},
    "nygc_gse330224_lsc_visium": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": False},
    "nygc_gse330224_mtc_visium": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": False},
    "omar2025_capillary": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "ruf2026_fans_tdp43": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "zelic2025_cervical_sc": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "takeda2025_pbmc": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": True, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "DS052_DELLAR_CSF_DIA": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": True, "independent_of_v14": True},
    "DS053_MUNICH_BA6_PROT": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": True, "independent_of_v14": True},
    "DS056_NYGC_CSF_RNASEQ": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "DS065_EDIN_COGNITIVE_BULK": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": False},
    "DS_SUPP_SPITERI2025_4REG": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": True, "independent_of_v14": True},
    "DS_SUPP_FENEBERG2025_OXF": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": True, "independent_of_v14": True},
    "DS_SUPP_MIEDEMA2025_FTLD": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": True, "independent_of_v14": True},
    "DS_SUPP_PAN2026_OLINK": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "DS_SUPP_RAN2026_PREFALS": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "DS_SUPP_ROCAPEREIRA2026_CSF": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": True, "independent_of_v14": True},
    "DS_SUPP_KOZAREVA2025": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": True, "is_tryptic_ms_not_immunoassay": True, "independent_of_v14": True},
    "DS055_BOLGER_CRYPTE_ISOSEQ": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": True, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": False},
    "DS060_NYGC_TE_CORTEX_CORD": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": False},
    "DS061_EXETER_TDP43_NANOPORE": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": True, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "DS062_KEUSS_SOMA_NEURITE": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "DS063_MUSCLE_PROT_2025": {"is_rna_not_protein": False, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": True, "independent_of_v14": True},
    "DS066_RUMMENS_TDP43_AGG": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": True, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
    "DS057_ZELIC_BULK": {"is_rna_not_protein": True, "is_3prime_snrna_blind_to_internal_junctions": False, "can_detect_cryptic_splice": False, "is_tryptic_ms_not_immunoassay": False, "independent_of_v14": True},
}

_MANIFEST_CACHE: pd.DataFrame | None = None
_OVERLAP_CACHE: dict[str, set[str]] | None = None


def _get_manifest() -> pd.DataFrame:
    global _MANIFEST_CACHE
    if _MANIFEST_CACHE is None:
        _MANIFEST_CACHE = pd.read_csv(EXP_DIR / "EXPANSION_MANIFEST_2026_11.csv", dtype=str)
    return _MANIFEST_CACHE


def _norm_donor_token(x: Any) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(x).strip().upper())


def resolve_expansion_file(
    pattern: str,
    dataset_id: str | None = None,
    verify_hash: bool = False,
) -> Path:
    """Resolve a Pack C file path via EXPANSION_MANIFEST_2026_11.csv with optional SHA-256 verification."""
    m = _get_manifest()
    sub = m if dataset_id is None else m.loc[m["dataset_id"] == dataset_id]
    hits = sub.loc[sub["local_relpath"].str.contains(pattern, case=False, na=False)]
    if hits.empty:
        raise FileNotFoundError(f"Pack C manifest match failed for pattern={pattern!r}, dataset_id={dataset_id!r}")
    row = hits.iloc[0]
    p = ROOT / str(row["local_relpath"])
    if not p.exists():
        raise FileNotFoundError(f"Staged Pack C file missing on disk: {p}")
    if verify_hash:
        expected_sha = str(row["sha256"]).strip().lower()
        if not expected_sha or not _file_matches_sha256(p, expected_sha):
            raise ValueError(f"SHA-256 mismatch on Pack C file {row['local_relpath']} (expected {expected_sha})")
    return p


def assert_expansion_modality(modality: str, dataset_id: str) -> str:
    if modality not in EXPANSION_ALLOWED_MODALITIES:
        raise ValueError(f"[{dataset_id}] Invalid expansion modality {modality!r}")
    return modality


def get_v14_overlap_donors(cohort_key: str) -> set[str]:
    """Return normalized donor IDs shared between a Pack C cohort and v1.4.0 NYGC/O'Neill/Edinburgh cohorts."""
    global _OVERLAP_CACHE
    if _OVERLAP_CACHE is None:
        _OVERLAP_CACHE = {}
        # Build exact v1.4 union from primary metadata files (never truncated sample_shared_ids!)
        v14_union: set[str] = set()
        df_col = pd.read_excel(ROOT / "data/transcriptomics/nygc_d001/nygc_collab_metadata_c05a4864.xlsx")
        v14_union |= {_norm_donor_token(x) for x in df_col["ExternalSubjectId"].dropna()}
        df_st1 = pd.read_excel(ROOT / "data/transcriptomics/nygc_d001/NYGC_Flagship_ST_1_3_Metadata.xlsx", sheet_name="ST1", header=1)
        v14_union |= {_norm_donor_token(x) for x in df_st1["donor_id"].dropna()}
        df_on = pd.read_excel(ROOT / "data/transcriptomics/subtypes/oneill2025_mmc2.xlsx", sheet_name="TableS1C", header=1)
        v14_union |= {_norm_donor_token(x) for x in df_on["PatientID"].dropna()}
        ed_meta = pd.read_csv(ROOT / "data/transcriptomics/edinburgh_gse290359_pseudobulk/library_metadata.tsv", sep="\t")
        for val in ed_meta["Edinburgh ID"].dropna():
            try:
                v14_union.add(_norm_donor_token(json.loads(str(val))[0][0]))
            except Exception:
                v14_union.add(_norm_donor_token(val))
        _OVERLAP_CACHE["__v14_union__"] = v14_union

    v14_union = _OVERLAP_CACHE["__v14_union__"]
    if cohort_key in _OVERLAP_CACHE:
        return set(_OVERLAP_CACHE[cohort_key])

    if cohort_key == "DS065_EDIN_COGNITIVE_BULK":
        g314 = pd.read_csv(META_DIR / "GSE314526_sample_metadata.tsv", sep="\t", dtype=str)
        c_ids = {_norm_donor_token(x) for x in g314["char_donor_id"].dropna()}
    elif (PB_DIR / f"{cohort_key}_meta.tsv").exists():
        mdf = pd.read_csv(PB_DIR / f"{cohort_key}_meta.tsv", sep="\t", dtype=str)
        c_ids = {_norm_donor_token(x) for x in mdf["donor_id"].dropna()}
    else:
        c_ids = set()
    shared = c_ids & v14_union
    _OVERLAP_CACHE[cohort_key] = shared
    return set(shared)


def assert_contrast_columns_aligned(
    df: pd.DataFrame,
    effect_col: str,
    p_col: str,
    adj_p_col: str | None,
    required_token: str | None,
    context: str,
    allow_empirical_q: bool = False,
) -> None:
    """Verify effect/p/adj_p columns belong to the same contrast token AND satisfy p <= adj_p row-wise (unless empirical permutation q)."""
    if required_token:
        tok = required_token.lower()
        for cname in (effect_col, p_col, *( (adj_p_col,) if adj_p_col else () )):
            if tok not in str(cname).lower():
                raise AssertionError(
                    f"[{context}] CONTRAST_TOKEN_MISMATCH: column {cname!r} does not contain {required_token!r}"
                )
    if adj_p_col is not None and not allow_empirical_q:
        pv = pd.to_numeric(df[p_col], errors="coerce")
        qv = pd.to_numeric(df[adj_p_col], errors="coerce")
        mask = pv.notna() & qv.notna()
        if mask.any():
            bad = mask & (pv > qv + 1e-6)
            if bad.any():
                n_bad = int(bad.sum())
                ex_i = int(np.flatnonzero(bad.to_numpy())[0])
                raise AssertionError(
                    f"[{context}] CONTRAST_MIXING_BLOCKED: {n_bad} rows have {p_col}={pv.iloc[ex_i]} > {adj_p_col}={qv.iloc[ex_i]}"
                )


def bh_fdr_with_provenance_guard(pvals: dict[str, float], context: str = "bh_fdr") -> dict[str, dict[str, float | int]]:
    """Compute exact Benjamini-Hochberg FDR across an explicit test family with provenance_gates invariants."""
    keys = list(pvals.keys())
    raw_p = np.array([float(pvals[k]) for k in keys], dtype=np.float64)
    if len(keys) == 0:
        return {}
    if not np.all(np.isfinite(raw_p)) or np.any((raw_p < 0.0) | (raw_p > 1.0)):
        raise ValueError(f"[{context}] Non-finite or out-of-[0,1] p-value passed to bh_fdr_with_provenance_guard")
    m = len(raw_p)
    order = np.argsort(raw_p)
    ranked_p = raw_p[order]
    adj = np.empty(m, dtype=np.float64)
    running_min = 1.0
    for i in range(m - 1, -1, -1):
        val = min(1.0, ranked_p[i] * m / (i + 1))
        running_min = min(running_min, val)
        adj[i] = running_min
    out: dict[str, dict[str, float | int]] = {}
    for rank_idx, orig_idx in enumerate(order):
        p_i = float(raw_p[orig_idx])
        q_i = float(adj[rank_idx])
        if p_i > q_i + 1e-12:
            raise AssertionError(f"[{context}] PROVENANCE INVARIANT VIOLATION: p={p_i} > fdr={q_i}")
        out[keys[orig_idx]] = {"p_value": p_i, "fdr_bh": q_i, "n_family": m}
    return out


def classify_pack_c_evidence(
    cohort_key: str,
    detected: bool,
    concordant_direction: bool | None,
    p_value: float | None,
    fdr: float | None = None,
    hypothesis_requires_cryptic_splice: bool = False,
    hypothesis_requires_immunoassay_isoform: bool = False,
    is_non_overlapping_sensitivity: bool = False,
) -> dict[str, Any]:
    """Classify a Pack C stress-test result enforcing AGENTS.md §2 Epistemic Asymmetry & assay physics."""
    caps = ASSAY_PHYSICS_CAPABILITIES.get(cohort_key, {})
    assay_blind_reasons: list[str] = []
    if hypothesis_requires_cryptic_splice and not caps.get("can_detect_cryptic_splice", False):
        assay_blind_reasons.append("ASSAY_BLIND_TO_CRYPTIC_SPLICE")
    if hypothesis_requires_immunoassay_isoform and caps.get("is_tryptic_ms_not_immunoassay", False):
        assay_blind_reasons.append("TRYPTIC_MS_NOT_ISOFORM_IMMUNOASSAY")
    if not detected:
        assay_blind_reasons.append("FEATURE_UNDETECTED_IN_ASSAY")

    if assay_blind_reasons and (not detected or p_value is None or p_value >= 0.05):
        return {
            "stress_status": "UNPROVEN_ASSAY_BLIND",
            "epistemic_note": "; ".join(assay_blind_reasons),
            "falsifies_hypothesis": False,
        }
    if p_value is None or not math.isfinite(p_value) or p_value >= 0.05:
        return {
            "stress_status": "UNPROVEN_UNDERPOWERED_OR_NULL",
            "epistemic_note": "Non-significant donor-level test (p >= 0.05); does not falsify hypothesis.",
            "falsifies_hypothesis": False,
        }
    is_indep = bool(caps.get("independent_of_v14", False) or is_non_overlapping_sensitivity)
    if concordant_direction is True:
        status = "CORROBORATED_INDEPENDENT" if is_indep else "CORROBORATED_CROSS_MODAL"
        if fdr is not None and math.isfinite(fdr) and fdr < 0.05:
            note = f"Directionally concordant and family-FDR significant (p={p_value:.3g}, FDR={fdr:.3g})."
        else:
            note = f"Directionally concordant nominal support (p={p_value:.3g})."
        return {"stress_status": status, "epistemic_note": note, "falsifies_hypothesis": False}
    if concordant_direction is False:
        return {
            "stress_status": "CHALLENGED_OR_DISCORDANT",
            "epistemic_note": f"Opposite-sign shift at p={p_value:.3g}; requires polarity/compensatory review.",
            "falsifies_hypothesis": False,  # Requires multi-modal causal review before any DROP
        }
    return {
        "stress_status": "DETECTED_SIGN_UNSPECIFIED",
        "epistemic_note": f"Significant shift (p={p_value:.3g}) with unspecified directional prior.",
        "falsifies_hypothesis": False,
    }


def _welch_mwu(case_v: np.ndarray, ctrl_v: np.ndarray) -> dict[str, Any]:
    c = case_v[np.isfinite(case_v)]
    n = ctrl_v[np.isfinite(ctrl_v)]
    if len(c) < 2 or len(n) < 2:
        return {
            "n_case": int(len(c)),
            "n_ctrl": int(len(n)),
            "mean_case": float(np.mean(c)) if len(c) else float("nan"),
            "mean_ctrl": float(np.mean(n)) if len(n) else float("nan"),
            "diff": float("nan"),
            "t_welch": float("nan"),
            "p_welch": 1.0,
            "p_mwu": 1.0,
        }
    t_res = stats.ttest_ind(c, n, equal_var=False)
    u_res = stats.mannwhitneyu(c, n, alternative="two-sided")
    return {
        "n_case": int(len(c)),
        "n_ctrl": int(len(n)),
        "mean_case": round(float(np.mean(c)), 4),
        "mean_ctrl": round(float(np.mean(n)), 4),
        "diff": round(float(np.mean(c) - np.mean(n)), 4),
        "t_welch": round(float(t_res.statistic), 4) if np.isfinite(t_res.statistic) else float("nan"),
        "p_welch": float(t_res.pvalue) if np.isfinite(t_res.pvalue) else 1.0,
        "p_mwu": float(u_res.pvalue) if np.isfinite(u_res.pvalue) else 1.0,
    }


def _encode_covariate_matrix(meta_sub: pd.DataFrame) -> dict[str, np.ndarray]:
    """Extract clean numeric covariate vectors (gc_z, sex_male, age, pmi) from donor metadata."""
    covs: dict[str, np.ndarray] = {}
    if "gc_z" in meta_sub.columns:
        covs["gc_z"] = pd.to_numeric(meta_sub["gc_z"], errors="coerce").to_numpy(dtype=float)
    for sex_col in ("sex", "char_sex", "char_gender"):
        if sex_col in meta_sub.columns:
            s_low = meta_sub[sex_col].astype(str).str.strip().str.lower()
            arr = np.where(s_low.isin(["m", "male"]), 1.0, np.where(s_low.isin(["f", "female"]), 0.0, np.nan))
            covs["sex_male"] = arr
            break
    for age_col in ("age", "char_age"):
        if age_col in meta_sub.columns:
            covs["age"] = pd.to_numeric(meta_sub[age_col], errors="coerce").to_numpy(dtype=float)
            break
    for pmi_col in ("pmi", "char_pmi"):
        if pmi_col in meta_sub.columns:
            covs["pmi"] = pd.to_numeric(meta_sub[pmi_col], errors="coerce").to_numpy(dtype=float)
            break
    return covs


def _covariate_adjusted_ols(
    y: np.ndarray,
    is_case: np.ndarray,
    cov_dict: dict[str, np.ndarray] | None = None,
    min_df_resid: int = 4,
    max_case_vif: float = 5.0,
) -> dict[str, Any]:
    """Donor-level OLS: y ~ 1 + is_case + valid non-collinear covariates (priority: gc_z, sex_male, age, pmi).

    Enforces VIF < max_case_vif (default 5.0) on is_case so severe confounding collinearity (e.g. Omar NIH NBB
    PMI r=-0.906) never inflates SEs or flips signs. Never silently substitutes Welch p into adjusted p!
    """
    base_mask = np.isfinite(y) & np.isfinite(is_case)
    if base_mask.sum() < 5 or len(np.unique(is_case[base_mask])) < 2:
        return {"beta_case_adj": float("nan"), "se_case_adj": float("nan"), "covariate_adjusted_nominal_p": float("nan"), "covariates_used": [], "collinear_covariates_dropped": [], "n_complete_adj": int(base_mask.sum()), "df_resid_adj": 0}

    used_names: list[str] = []
    used_cols: list[np.ndarray] = []
    dropped_collinear: list[str] = []
    cur_mask = base_mask.copy()
    priority = ("gc_z", "sex_male", "age", "pmi")
    if cov_dict:
        for cname in priority:
            if cname not in cov_dict:
                continue
            cvec = cov_dict[cname]
            cand_mask = cur_mask & np.isfinite(cvec)
            # Only add covariate if it retains >=80% of base_mask donors, non-zero variance, both arms, enough df, and VIF < max_case_vif
            n_cand = int(cand_mask.sum())
            k_params = 2 + len(used_cols) + 1
            if (
                n_cand >= max(6, int(0.8 * base_mask.sum()))
                and (n_cand - k_params) >= min_df_resid
                and len(np.unique(is_case[cand_mask])) == 2
                and np.nanstd(cvec[cand_mask]) > 1e-8
            ):
                # Check VIF of is_case (column 0) with candidate covariate added
                mat_test = np.column_stack([is_case[cand_mask].astype(float)] + [c[cand_mask] for c in used_cols] + [cvec[cand_mask]])
                corr_m = np.corrcoef(mat_test, rowvar=False)
                try:
                    vif_case = float(np.linalg.inv(corr_m)[0, 0])
                except np.linalg.LinAlgError:
                    vif_case = float("inf")
                if not math.isfinite(vif_case) or vif_case >= max_case_vif:
                    dropped_collinear.append(f"{cname}(VIF={vif_case:.1f})")
                    continue
                cur_mask = cand_mask
                used_names.append(cname)
                used_cols.append(cvec)

    if not used_cols:
        # Strictly report NaN for covariate_adjusted_nominal_p if no covariate was fitted!
        return {"beta_case_adj": float("nan"), "se_case_adj": float("nan"), "covariate_adjusted_nominal_p": float("nan"), "covariates_used": [], "collinear_covariates_dropped": dropped_collinear, "n_complete_adj": int(cur_mask.sum()), "df_resid_adj": 0}

    yv = y[cur_mask]
    xv = is_case[cur_mask].astype(float)
    X_cols = [np.ones(len(yv)), xv] + [c[cur_mask] for c in used_cols]
    X = np.column_stack(X_cols)
    df_resid = len(yv) - X.shape[1]
    if df_resid < 2:
        return {"beta_case_adj": float("nan"), "se_case_adj": float("nan"), "covariate_adjusted_nominal_p": float("nan"), "covariates_used": used_names, "collinear_covariates_dropped": dropped_collinear, "n_complete_adj": len(yv), "df_resid_adj": df_resid}
    coef, _, _, _ = np.linalg.lstsq(X, yv, rcond=None)
    resid = yv - X @ coef
    s2 = float((resid @ resid) / df_resid)
    try:
        cov_mat = s2 * np.linalg.inv(X.T @ X)
        se = float(np.sqrt(max(cov_mat[1, 1], 1e-18)))
    except np.linalg.LinAlgError:
        return {"beta_case_adj": round(float(coef[1]), 4), "se_case_adj": float("nan"), "covariate_adjusted_nominal_p": float("nan"), "covariates_used": used_names, "collinear_covariates_dropped": dropped_collinear, "n_complete_adj": len(yv), "df_resid_adj": df_resid}
    t_val = float(coef[1] / se)
    p_val = float(2.0 * stats.t.sf(abs(t_val), df=df_resid))
    return {
        "beta_case_adj": round(float(coef[1]), 4),
        "se_case_adj": round(se, 4),
        "covariate_adjusted_nominal_p": p_val,
        "covariates_used": used_names,
        "collinear_covariates_dropped": dropped_collinear,
        "n_complete_adj": int(len(yv)),
        "df_resid_adj": int(df_resid),
    }


def _paired_tests(v_a: np.ndarray, v_b: np.ndarray) -> dict[str, Any]:
    mask = np.isfinite(v_a) & np.isfinite(v_b)
    a, b = v_a[mask], v_b[mask]
    n = int(len(a))
    if n < 3:
        return {"n_pairs": n, "mean_diff": float("nan"), "p_paired_t": 1.0, "p_wilcoxon": 1.0}
    diff = a - b
    t_res = stats.ttest_rel(a, b)
    try:
        w_res = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
        p_w = float(w_res.pvalue)
    except ValueError:
        p_w = 1.0
    return {
        "n_pairs": n,
        "mean_a": round(float(np.mean(a)), 4),
        "mean_b": round(float(np.mean(b)), 4),
        "mean_diff": round(float(np.mean(diff)), 4),
        "t_paired": round(float(t_res.statistic), 4) if np.isfinite(t_res.statistic) else float("nan"),
        "p_paired_t": float(t_res.pvalue) if np.isfinite(t_res.pvalue) else 1.0,
        "p_wilcoxon": p_w,
    }


# ---------------------------------------------------------------------------
# 1. Compiled Single-Cell & Spatial Donor Pseudobulk Loaders (All 9 Matrices)
# ---------------------------------------------------------------------------

PSEUDOBULK_MODALITY_MAP = {
    "takeuchi2025_lsc": "SNRNA_PSEUDOBULK_LOG2CPM",
    "takeuchi2025_ba4": "SNRNA_PSEUDOBULK_LOG2CPM",
    "nygc_gse330130_lsc": "SNRNA_PSEUDOBULK_LOG2CPM",
    "nygc_gse330224_lsc_visium": "SPATIAL_VISIUM_PSEUDOBULK",
    "nygc_gse330224_mtc_visium": "SPATIAL_VISIUM_PSEUDOBULK",
    "omar2025_capillary": "INCITE_CAPILLARY_PSEUDOBULK",
    "ruf2026_fans_tdp43": "FANS_TDP43_PSEUDOBULK",
    "zelic2025_cervical_sc": "SNRNA_PSEUDOBULK_LOG2CPM",
    "takeda2025_pbmc": "PBMC_SCRNA_PSEUDOBULK",
}

_PB_FULL_CACHE: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}


def _get_pseudobulk_full(cohort_key: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and cache full raw-integer pseudobulk meta + counts table for fast DESeq2 size-factor computation."""
    if cohort_key not in _PB_FULL_CACHE:
        meta_p = PB_DIR / f"{cohort_key}_meta.tsv"
        cnt_p = PB_DIR / f"{cohort_key}_counts.tsv.gz"
        if not meta_p.exists() or not cnt_p.exists():
            raise FileNotFoundError(f"Pseudobulk not compiled yet for {cohort_key}: {meta_p}")
        meta = pd.read_csv(meta_p, sep="\t")
        cnt = pd.read_csv(cnt_p, sep="\t")
        _PB_FULL_CACHE[cohort_key] = (meta, cnt)
    return _PB_FULL_CACHE[cohort_key]


def _compute_deseq2_size_factors(
    counts_gxs: np.ndarray,
    gene_symbols: np.ndarray | list[str],
    exclude_mt_ribo: bool = True,
) -> tuple[np.ndarray, str]:
    """Compute DESeq2 median-of-ratios size factors (normalized to geometric mean 1.0), excluding MT-* & RP[SL]* composition shifts."""
    n_genes, n_samples = counts_gxs.shape
    lib = counts_gxs.sum(axis=0).astype(np.float64)
    if n_samples < 2 or n_genes < 50:
        sf = lib / np.maximum(np.exp(np.mean(np.log(np.maximum(lib, 1.0)))), 1.0)
        return sf, "raw_cpm_fallback"

    keep_gene = np.ones(n_genes, dtype=bool)
    if exclude_mt_ribo:
        gs = pd.Series(gene_symbols).astype(str).str.upper()
        keep_gene &= ~gs.str.startswith("MT-").to_numpy()
        keep_gene &= ~gs.str.match(r"^RP[SL]\d").to_numpy()
        keep_gene &= ~gs.isin(["MALAT1", "NEAT1"]).to_numpy()

    sub = counts_gxs[keep_gene]
    # Prefer genes positive across >=80% of samples (relax to >=60% if sparse)
    pos_frac = (sub > 0).mean(axis=1)
    ref_mask = pos_frac >= 0.80
    if int(ref_mask.sum()) < 200:
        ref_mask = pos_frac >= 0.60
    if int(ref_mask.sum()) < 50:
        sf = lib / np.maximum(np.exp(np.mean(np.log(np.maximum(lib, 1.0)))), 1.0)
        return sf, "raw_cpm_fallback_sparse"

    ref = np.where(sub[ref_mask] > 0, sub[ref_mask], np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        lref = np.log(ref)
        geo = np.nanmean(lref, axis=1, keepdims=True)
        ratios = lref - geo
        sf = np.exp(np.nanmedian(ratios, axis=0))
    if not np.all(np.isfinite(sf)) or np.any(sf <= 0):
        sf = lib / np.maximum(np.exp(np.mean(np.log(np.maximum(lib, 1.0)))), 1.0)
        return sf, "raw_cpm_fallback_nonfinite"
    sf = sf / float(np.exp(np.mean(np.log(sf))))
    return sf, "deseq2_mor_no_mt_ribo"


def _normalize_counts_to_log2(
    full_counts_gxs: np.ndarray,
    full_gene_symbols: np.ndarray | list[str],
    target_counts_gxs: np.ndarray,
    tot_umi: np.ndarray,
    normalization: str = "deseq2_mor",
) -> tuple[np.ndarray, str, np.ndarray]:
    """Normalize target counts using either DESeq2 median-of-ratios (default) or raw CPM, returning log2(scaled_CPM + 1)."""
    if normalization == "deseq2_mor":
        sf, norm_used = _compute_deseq2_size_factors(full_counts_gxs, full_gene_symbols, exclude_mt_ribo=True)
        mean_lib = float(np.mean(tot_umi))
        eff_denom = sf * mean_lib
        scaled = (target_counts_gxs / eff_denom[None, :]) * 1e6
        return np.log2(scaled + 1.0), norm_used, sf
    scaled = (target_counts_gxs / tot_umi[None, :]) * 1e6
    return np.log2(scaled + 1.0), "raw_cpm", tot_umi / float(np.mean(tot_umi))


_INFERRED_SEX_CACHE: dict[str, dict[str, str]] = {}


def _infer_donor_sex_from_counts(cohort_key: str) -> dict[str, str]:
    """Infer donor sex (M/F) from XIST vs RPS4Y1/DDX3Y/UTY in ALL_PBMC/ALL_CELLS pseudobulk when GEO lacks sex metadata."""
    if cohort_key in _INFERRED_SEX_CACHE:
        return _INFERRED_SEX_CACHE[cohort_key]
    meta, full_cdf = _get_pseudobulk_full(cohort_key)
    all_st = next((s for s in ("ALL_PBMC", "ALL_CELLS", "ALL_NUCLEI") if s in set(meta["stratum"])), None)
    if all_st is None:
        return {}
    sub = meta.loc[meta["stratum"] == all_st].copy()
    pids = sub["profile_id"].astype(str).tolist()
    tot = sub["total_umi"].to_numpy(dtype=np.float64)
    sx = full_cdf.loc[full_cdf["gene_symbol"].isin(["XIST", "RPS4Y1", "DDX3Y", "UTY"])]
    if sx.empty or "XIST" not in set(sx["gene_symbol"]):
        return {}
    sx_g = sx.groupby("gene_symbol")[pids].sum()
    l2 = np.log2((sx_g.to_numpy(dtype=np.float64) / np.maximum(tot[None, :], 1.0)) * 1e6 + 1.0)
    sdf = pd.DataFrame(l2.T, index=pids, columns=sx_g.index)
    y_cols = [c for c in ("RPS4Y1", "DDX3Y", "UTY") if c in sdf.columns]
    if not y_cols:
        return {}
    y_mean = sdf[y_cols].mean(axis=1).to_numpy(float)
    xist = sdf["XIST"].to_numpy(float)
    sex_arr = np.where(y_mean > xist, "M", "F")
    res = dict(zip(sub["donor_id"].astype(str), sex_arr))
    _INFERRED_SEX_CACHE[cohort_key] = res
    return res


def load_expansion_pseudobulk(
    cohort_key: str,
    stratum: str,
    genes: list[str] | None = None,
    min_cells: int = 10,
    case_groups: tuple[str, ...] = ("ALS",),
    ctrl_groups: tuple[str, ...] = ("Control",),
    exclude_v14_overlaps: bool = False,
    exclude_donors: set[str] | None = None,
    normalization: str = "deseq2_mor",
) -> dict[str, Any]:
    """Load donor-level DESeq2 median-of-ratios (or raw CPM) log2 profiles for one cohort + stratum with anti-pseudoreplication."""
    if cohort_key not in PSEUDOBULK_MODALITY_MAP:
        raise ValueError(f"Unknown pseudobulk cohort_key={cohort_key!r}; valid={sorted(PSEUDOBULK_MODALITY_MAP)}")
    meta, full_cdf = _get_pseudobulk_full(cohort_key)
    sub_meta = meta.loc[(meta["stratum"] == stratum) & (pd.to_numeric(meta["n_cells"], errors="coerce") >= min_cells)].copy()

    drop_norm: set[str] = set()
    if exclude_v14_overlaps:
        drop_norm |= get_v14_overlap_donors(cohort_key)
    if exclude_donors:
        drop_norm |= {_norm_donor_token(d) for d in exclude_donors}
    if drop_norm:
        sub_meta = sub_meta.loc[~sub_meta["donor_id"].map(_norm_donor_token).isin(drop_norm)].copy()

    if sub_meta.empty:
        avail = sorted(meta["stratum"].unique().tolist())
        raise ValueError(f"[{cohort_key}] No profiles for stratum={stratum!r} with min_cells>={min_cells}; available={avail}")

    assert_unique_donors(sub_meta["donor_id"].astype(str).tolist(), f"{cohort_key}:{stratum}")

    pids = sub_meta["profile_id"].astype(str).tolist()
    tot_umi = sub_meta.set_index("profile_id").loc[pids, "total_umi"].to_numpy(dtype=np.float64)
    if (tot_umi <= 0).any():
        raise ValueError(f"[{cohort_key}:{stratum}] Zero total_umi encountered")

    full_mat = full_cdf[pids].to_numpy(dtype=np.float64)
    full_syms = full_cdf["gene_symbol"].astype(str).to_numpy()

    if genes is not None:
        gset = {g.upper() for g in genes}
        keep = full_cdf["gene_symbol"].astype(str).str.upper().isin(gset) | full_cdf["gene_id"].astype(str).str.upper().isin(gset)
        cdf = full_cdf.loc[keep, ["gene_id", "gene_symbol"] + pids].copy()
    else:
        cdf = full_cdf[["gene_id", "gene_symbol"] + pids].copy()

    cdf["gene_key"] = cdf["gene_symbol"].astype(str)
    g_sum = cdf.groupby("gene_key", sort=False)[pids].sum()
    l2_mat, norm_used, sf = _normalize_counts_to_log2(full_mat, full_syms, g_sum.to_numpy(dtype=np.float64), tot_umi, normalization=normalization)
    log2cpm = pd.DataFrame(l2_mat, index=g_sum.index, columns=pids)

    meta_idx = sub_meta.set_index("profile_id").loc[pids].copy()
    # Auto-infer donor sex from XIST vs Y-chr transcripts when cohort lacks explicit sex metadata (e.g. Takeda 2025 PBMC)
    if not any(c in meta_idx.columns for c in ("sex", "char_sex", "char_gender")):
        sex_map = _infer_donor_sex_from_counts(cohort_key)
        if sex_map:
            meta_idx["sex"] = meta_idx["donor_id"].astype(str).map(sex_map)
            sub_meta = sub_meta.copy()
            sub_meta["sex"] = sub_meta["donor_id"].astype(str).map(sex_map)
    grp_series = meta_idx["disease_group"].astype(str)
    case_pids = [p for p in pids if grp_series.loc[p] in case_groups]
    ctrl_pids = [p for p in pids if grp_series.loc[p] in ctrl_groups]

    stats_by_gene: dict[str, dict[str, Any]] = {}
    if case_pids and ctrl_pids and genes is not None:
        sel_pids = case_pids + ctrl_pids
        is_case = np.array([1.0] * len(case_pids) + [0.0] * len(ctrl_pids))
        cov_dict = _encode_covariate_matrix(meta_idx.loc[sel_pids])
        for g in log2cpm.index:
            cv = log2cpm.loc[g, case_pids].to_numpy(dtype=float)
            nv = log2cpm.loc[g, ctrl_pids].to_numpy(dtype=float)
            st = _welch_mwu(cv, nv)
            ols = _covariate_adjusted_ols(log2cpm.loc[g, sel_pids].to_numpy(dtype=float), is_case, cov_dict)
            stats_by_gene[str(g)] = {**st, **ols}

    return {
        "cohort_key": cohort_key,
        "modality": assert_expansion_modality(PSEUDOBULK_MODALITY_MAP[cohort_key], cohort_key),
        "stratum": stratum,
        "normalization_used": norm_used,
        "size_factors": dict(zip(pids, [round(float(x), 5) for x in sf])),
        "exclude_v14_overlaps": exclude_v14_overlaps,
        "n_excluded_overlap_donors": int(len(drop_norm)),
        "meta_df": sub_meta.reset_index(drop=True),
        "log2cpm_df": log2cpm,
        "raw_counts_df": g_sum,
        "n_case": len(case_pids),
        "n_ctrl": len(ctrl_pids),
        "stats": stats_by_gene,
    }


def load_paired_strata_pseudobulk(
    cohort_key: str,
    stratum_a: str,
    stratum_b: str,
    genes: list[str] | None = None,
    min_cells: int = 5,
    disease_groups: tuple[str, ...] | None = None,
    normalization: str = "deseq2_mor",
) -> dict[str, Any]:
    """Paired within-donor two-stratum contrast using JOINT DESeq2 median-of-ratios size factors across both strata."""
    meta, full_cdf = _get_pseudobulk_full(cohort_key)
    ma = meta.loc[(meta["stratum"] == stratum_a) & (pd.to_numeric(meta["n_cells"], errors="coerce") >= min_cells)].copy()
    mb = meta.loc[(meta["stratum"] == stratum_b) & (pd.to_numeric(meta["n_cells"], errors="coerce") >= min_cells)].copy()
    if disease_groups is not None:
        ma = ma.loc[ma["disease_group"].astype(str).isin(disease_groups)].copy()
        mb = mb.loc[mb["disease_group"].astype(str).isin(disease_groups)].copy()
    amap = dict(zip(ma["donor_id"].astype(str), ma["profile_id"].astype(str)))
    bmap = dict(zip(mb["donor_id"].astype(str), mb["profile_id"].astype(str)))
    shared = sorted(set(amap) & set(bmap))
    assert_unique_donors(shared, f"{cohort_key}:paired:{stratum_a}_vs_{stratum_b}")

    a_pids = [amap[d] for d in shared]
    b_pids = [bmap[d] for d in shared]
    all_pids = a_pids + b_pids
    meta_idx = meta.set_index("profile_id").loc[all_pids]
    tot_umi = meta_idx["total_umi"].to_numpy(dtype=np.float64)

    full_mat = full_cdf[all_pids].to_numpy(dtype=np.float64)
    full_syms = full_cdf["gene_symbol"].astype(str).to_numpy()
    if genes is not None:
        gset = {g.upper() for g in genes}
        keep = full_cdf["gene_symbol"].astype(str).str.upper().isin(gset) | full_cdf["gene_id"].astype(str).str.upper().isin(gset)
        cdf = full_cdf.loc[keep, ["gene_id", "gene_symbol"] + all_pids].copy()
    else:
        cdf = full_cdf[["gene_id", "gene_symbol"] + all_pids].copy()
    cdf["gene_key"] = cdf["gene_symbol"].astype(str)
    g_sum = cdf.groupby("gene_key", sort=False)[all_pids].sum()
    l2_mat, norm_used, _ = _normalize_counts_to_log2(full_mat, full_syms, g_sum.to_numpy(dtype=np.float64), tot_umi, normalization=normalization)
    l2_df = pd.DataFrame(l2_mat, index=g_sum.index, columns=all_pids)

    stats_by_gene: dict[str, dict[str, Any]] = {}
    if genes is not None and len(shared) >= 3:
        for g in l2_df.index:
            stats_by_gene[str(g)] = _paired_tests(l2_df.loc[g, a_pids].to_numpy(float), l2_df.loc[g, b_pids].to_numpy(float))

    return {
        "cohort_key": cohort_key,
        "modality": assert_expansion_modality(PSEUDOBULK_MODALITY_MAP[cohort_key], cohort_key),
        "normalization_used": norm_used,
        "stratum_a": stratum_a,
        "stratum_b": stratum_b,
        "paired_donors": shared,
        "n_pairs": len(shared),
        "a_log2_df": l2_df[a_pids],
        "b_log2_df": l2_df[b_pids],
        "stats": stats_by_gene,
    }


def compute_lineage_ambient_flags(
    cohort_key: str,
    lineage_strata: tuple[str, ...],
    genes: list[str] | None = None,
    min_cells: int = 10,
    ratio_log2_gap: float = 2.0,
    unconditional_gap: float = 2.5,
    low_expr_cutoff: float = 1.5,
    ctrl_groups: tuple[str, ...] = ("Control", "OldCtrl", "ALS_TDP_High"),
) -> dict[tuple[str, str], dict[str, Any]]:
    """Flag droplet ambient-RNA bleed-through & low-expression noise using Control-only (or TDP-High) lineage reference dominance.

    Marks (stratum, gene) as ambient_bleed_flag=True when another major lineage (including Oligo/OPC!) in Control donors
    expresses the gene >= 2.5 log2 higher unconditionally, OR >= 2.0 log2 higher while self_mean < 5.0 (and other >= 3.0).
    Also flags low_expr_flag=True when self_mean_log2 < low_expr_cutoff (default 1.5) to block non-lineage channel noise.
    """
    means: dict[str, pd.Series] = {}
    for st in lineage_strata:
        try:
            res = load_expansion_pseudobulk(cohort_key, st, genes=genes, min_cells=min_cells, case_groups=(), ctrl_groups=())
            mdf = res["meta_df"]
            ctrl_pids = mdf.loc[mdf["disease_group"].astype(str).isin(ctrl_groups), "profile_id"].astype(str).tolist()
            use_pids = ctrl_pids if len(ctrl_pids) >= 2 else mdf["profile_id"].astype(str).tolist()
            means[st] = res["log2cpm_df"][use_pids].mean(axis=1)
        except Exception:
            continue
    if len(means) < 2:
        return {}
    df_m = pd.DataFrame(means).fillna(0.0)
    cols = list(df_m.columns)
    genes_arr = df_m.index.astype(str).to_numpy()
    mat = df_m.to_numpy(dtype=np.float64)  # (G, C)
    n_c = len(cols)
    flags: dict[tuple[str, str], dict[str, Any]] = {}
    for j, st in enumerate(cols):
        val_self = mat[:, j]
        other_idx = [k for k in range(n_c) if k != j]
        other_mat = mat[:, other_idx]
        arg_m = np.argmax(other_mat, axis=1)
        val_other = other_mat[np.arange(len(genes_arr)), arg_m]
        gap = val_other - val_self
        is_bleed = (val_other >= 3.0) & ((gap >= unconditional_gap) | ((gap >= ratio_log2_gap) & (val_self < 5.0)))
        is_low = val_self < low_expr_cutoff
        other_names = [cols[other_idx[a]] for a in arg_m]
        for i, g in enumerate(genes_arr):
            flags[(st, g)] = {
                "ambient_bleed_flag": bool(is_bleed[i]),
                "low_expr_flag": bool(is_low[i]),
                "self_mean_log2": round(float(val_self[i]), 3),
                "top_other_lineage": other_names[i],
                "other_mean_log2": round(float(val_other[i]), 3),
                "lineage_log2_gap": round(float(gap[i]), 3),
            }
    return flags


def load_ruf2026_paired_tdp43(
    cell_lineage: str = "Exc_Neurons",
    genes: list[str] | None = None,
    min_cells: int = 10,
    normalization: str = "deseq2_mor",
) -> dict[str, Any]:
    """Paired within-donor TDP-43-Low vs TDP-43-High contrast in Ruf 2026 FANS M1 nuclei (joint DESeq2 normalization)."""
    res = load_paired_strata_pseudobulk(
        "ruf2026_fans_tdp43",
        f"{cell_lineage}__TDP_Low",
        f"{cell_lineage}__TDP_High",
        genes=genes,
        min_cells=min_cells,
        normalization=normalization,
    )
    return {
        "dataset_id": "DS054_RUF_FANS_TDP43",
        "modality": assert_expansion_modality("FANS_TDP43_PSEUDOBULK", "DS054_RUF_FANS_TDP43"),
        "normalization_used": res["normalization_used"],
        "cell_lineage": cell_lineage,
        "paired_donors": res["paired_donors"],
        "n_pairs": res["n_pairs"],
        "low_log2cpm_df": res["a_log2_df"],
        "high_log2cpm_df": res["b_log2_df"],
        "stats": res["stats"],
    }


def load_omar2025_capillary(
    stratum: str = "ALL_CAPILLARY",
    case_group: str = "ALS",
    ctrl_group: str = "OldCtrl",
    genes: list[str] | None = None,
    min_cells: int = 10,
    normalization: str = "deseq2_mor",
) -> dict[str, Any]:
    """Load Omar 2025 NIH NBB brain capillary inCITE-seq donor pseudobulks (DESeq2 normalized)."""
    return load_expansion_pseudobulk(
        "omar2025_capillary",
        stratum=stratum,
        genes=genes,
        min_cells=min_cells,
        case_groups=(case_group,),
        ctrl_groups=(ctrl_group,),
        normalization=normalization,
    )


# ---------------------------------------------------------------------------
# 2. Living CSF & Biofluid Proteomics / RNA-seq Loaders
# ---------------------------------------------------------------------------

def load_dellar2025_csf_dia(
    genes: list[str] | None = None,
    case_phenotype: str = "ALS",
    ctrl_phenotype: str = "CH",
    genotype_filter: str | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Dellar 2025 UK living CSF DIA-NN proteomics (HARD FILTER: Included == 'YES', no POOL runs)."""
    key_p = resolve_expansion_file("Dellar_et_al_2024", "DS052_DELLAR_CSF_DIA", verify_hash=verify_hash)
    pg_p = resolve_expansion_file("pg_matrix.tsv", "DS052_DELLAR_CSF_DIA", verify_hash=verify_hash)

    key = pd.read_csv(key_p, sep="\t")
    inc_col = resolve_col(key, "Included in final analysis")
    lbl_col = resolve_col(key, "Sample Label")
    ph_col = resolve_col(key, "Phenotype")
    gt_col = resolve_col(key, "Genotype")

    key_yes = key.loc[key[inc_col].astype(str).str.strip().str.upper() == "YES"].copy()
    if genotype_filter is not None:
        key_yes = key_yes.loc[key_yes[gt_col].astype(str).str.strip().str.upper() == genotype_filter.upper()].copy()
    assert_unique_donors(key_yes[lbl_col].astype(str).tolist(), "DS052_DELLAR_CSF_DIA")

    pg = pd.read_csv(pg_p, sep="\t", low_memory=False)
    gene_col = resolve_col(pg, "Genes")

    raw_cols = [c for c in pg.columns if c.lower().endswith(".raw")]
    lbl_to_col: dict[str, str] = {}
    for lbl in key_yes[lbl_col].astype(str):
        pat = lbl.strip()
        matches = [c for c in raw_cols if pat.lower() in Path(c.replace("\\", "/")).stem.lower()]
        if len(matches) == 1:
            lbl_to_col[pat] = matches[0]
        elif len(matches) > 1:
            exact = [c for c in matches if Path(c.replace("\\", "/")).stem.lower().endswith("_" + pat.lower())]
            if len(exact) == 1:
                lbl_to_col[pat] = exact[0]

    key_matched = key_yes.loc[key_yes[lbl_col].astype(str).isin(lbl_to_col)].copy()
    key_matched["pg_col"] = key_matched[lbl_col].astype(str).map(lbl_to_col)
    assert_unique_donors(key_matched[lbl_col].astype(str).tolist(), "DS052_DELLAR_CSF_DIA:matched")

    pg = pg.copy()
    pg["primary_gene"] = pg[gene_col].astype(str).str.split(";").str[0].str.strip()
    if genes is not None:
        gset = {g.upper() for g in genes}
        pg = pg.loc[pg["primary_gene"].str.upper().isin(gset)].copy()

    used_cols = key_matched["pg_col"].tolist()
    val_mat = pg[used_cols].apply(pd.to_numeric, errors="coerce")
    val_log2 = np.log2(val_mat.where(val_mat > 0))
    val_log2.index = pg["primary_gene"].values
    if not val_log2.index.is_unique:
        val_log2 = val_log2.copy()
        val_log2["_nn"] = val_log2.notna().sum(axis=1)
        val_log2 = val_log2.sort_values("_nn", ascending=False).groupby(level=0, sort=False).first().drop(columns=["_nn"])

    case_cols = key_matched.loc[key_matched[ph_col] == case_phenotype, "pg_col"].tolist()
    ctrl_cols = key_matched.loc[key_matched[ph_col] == ctrl_phenotype, "pg_col"].tolist()

    stats_by_gene: dict[str, dict[str, Any]] = {}
    if genes is not None and case_cols and ctrl_cols:
        for g in val_log2.index:
            stats_by_gene[str(g)] = _welch_mwu(
                val_log2.loc[g, case_cols].to_numpy(dtype=float),
                val_log2.loc[g, ctrl_cols].to_numpy(dtype=float),
            )

    return {
        "dataset_id": "DS052_DELLAR_CSF_DIA",
        "modality": assert_expansion_modality("PROTEOMICS_CSF_DIA", "DS052_DELLAR_CSF_DIA"),
        "genotype_filter": genotype_filter or "ALL",
        "meta_df": key_matched.reset_index(drop=True),
        "log2_df": val_log2,
        "n_case": len(case_cols),
        "n_ctrl": len(ctrl_cols),
        "stats": stats_by_gene,
    }


def load_gse308462_tissue(
    tissue: str = "Cerebrospinal_Fluid",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load GSE308462 strictly filtered to ONE tissue (default living Cerebrospinal_Fluid: 18 ALS vs 10 CTL)."""
    meta = pd.read_csv(META_DIR / "GSE308462_sample_metadata.tsv", sep="\t", dtype=str)
    sub = meta.loc[meta["char_tissue"] == tissue].copy()
    if sub.empty:
        raise ValueError(f"Unknown GSE308462 tissue={tissue!r}; valid={sorted(meta['char_tissue'].unique())}")

    cnt_p = resolve_expansion_file("GSE308462_260_samples_for_geo_gex_counts.csv.gz", "DS056_NYGC_CSF_RNASEQ", verify_hash=verify_hash)
    df_all = pd.read_csv(cnt_p, index_col=0)
    avail_cols = set(df_all.columns)
    sub["mat_col"] = sub["Sample_title"].where(sub["Sample_title"].isin(avail_cols), sub["char_subject_id"])
    sub = sub.loc[sub["mat_col"].isin(avail_cols)].copy()
    assert_unique_donors(sub["char_subject_id"].tolist(), f"DS056_GSE308462:{tissue}")

    gc_df = pd.read_csv(ROOT / "data/transcriptomics/ensembl116_hsapiens_gene_gc.tsv", sep="\t")
    ens_to_sym = dict(zip(gc_df["Gene stable ID"].astype(str), gc_df["Gene name"].fillna("").astype(str)))

    mat = df_all[sub["mat_col"].tolist()].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    lib_sizes = mat.sum(axis=0).to_numpy(dtype=np.float64)
    ens_clean = pd.Index([str(x).split(".")[0] for x in mat.index])
    syms = pd.Series([ens_to_sym.get(e, e) or e for e in ens_clean], index=mat.index)

    if genes is not None:
        gset = {g.upper() for g in genes}
        keep = syms.str.upper().isin(gset) | ens_clean.str.upper().isin(gset)
        mat = mat.loc[keep].copy()
        syms = syms.loc[keep]

    mat.index = syms.values
    mat = mat.groupby(level=0, sort=False).sum()
    log2cpm = pd.DataFrame(np.log2((mat.to_numpy(dtype=np.float64) / lib_sizes[None, :]) * 1e6 + 1.0), index=mat.index, columns=mat.columns)

    case_cols = sub.loc[sub["char_genotype"] == "ALS", "mat_col"].tolist()
    ctrl_cols = sub.loc[sub["char_genotype"] == "CTL", "mat_col"].tolist()
    stats_by_gene = {
        str(g): _welch_mwu(log2cpm.loc[g, case_cols].to_numpy(float), log2cpm.loc[g, ctrl_cols].to_numpy(float))
        for g in log2cpm.index
    } if (genes is not None and case_cols and ctrl_cols) else {}

    mod = "CSF_RNASEQ_BULK" if tissue == "Cerebrospinal_Fluid" else "BULK_RNASEQ_COUNTS"
    return {
        "dataset_id": "DS056_NYGC_CSF_RNASEQ",
        "modality": assert_expansion_modality(mod, "DS056_NYGC_CSF_RNASEQ"),
        "tissue": tissue,
        "meta_df": sub.reset_index(drop=True),
        "log2cpm_df": log2cpm,
        "n_case": len(case_cols),
        "n_ctrl": len(ctrl_cols),
        "stats": stats_by_gene,
    }


def _parse_est_ci_str(val: Any) -> tuple[float, float, float]:
    """Parse '0.45 (0.21, 0.69)' or '1.42 (1.12-1.80)' into (est, ci_low, ci_high)."""
    s = str(val).strip()
    m = re.match(r"^\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*\(\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*[,;\-–]\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*\)", s)
    if not m:
        try:
            return float(s), float("nan"), float("nan")
        except ValueError:
            return float("nan"), float("nan"), float("nan")
    return float(m.group(1)), float(m.group(2)), float(m.group(3))


def load_pan2026_ukb_alsrisc(
    sheet: str = "ST6",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Pan 2026 Olink proteomics via sparse-safe header_row=2 parser with verified contrast & estimator tags."""
    sheet_meta = {
        "ST5": ("ALSrisc_Plasma_ALS_vs_Ctrl", "PROTEOMICS_PLASMA_OLINK", "GEE_Beta_RobustP_BH_FDR"),
        "ST6": ("ALSrisc_CSF_ALS_vs_Ctrl", "PROTEOMICS_CSF_OLINK", "GEE_Beta_RobustP_BH_FDR"),
        "ST7": ("UKB_PreSymptomatic_FutureALS_Plasma", "PROTEOMICS_PLASMA_OLINK", "LinearReg_Beta_P_BH_FDR"),
        "ST8": ("ALSrisc_Plasma_Survival_HR_per_1SD", "PROTEOMICS_PLASMA_OLINK", "CoxPH_HR_P_BH_FDR"),
    }
    if sheet not in sheet_meta:
        raise ValueError(f"Unknown Pan 2026 sheet={sheet!r}; expected one of {sorted(sheet_meta)}")
    contrast_lbl, mod, est_note = sheet_meta[sheet]

    zp = resolve_expansion_file("PMC13545642_supplements.zip", "DS_SUPP_TISSUE_BIOFLUID_2025_2026", verify_hash=verify_hash)
    tmp_xlsx = META_DIR / "_cache_pan2026_st.xlsx"
    if not tmp_xlsx.exists():
        with zipfile.ZipFile(zp) as zf:
            tmp_xlsx.write_bytes(zf.read("ENE-33-e70741-s003.xlsx"))
    df = read_xlsx_sparse_safe(tmp_xlsx, sheet, header_row_1based=2)
    p_prot = resolve_col(df, "Protein")
    eff_col = resolve_col(df, "Beta (95% CI)", "HR (95% CI)")
    pval_col = resolve_col(df, "Robust p-value", "P-value")
    fdr_col = resolve_col(df, "FDR")
    assert_contrast_columns_aligned(df, eff_col, pval_col, fdr_col, None, f"Pan2026:{sheet}")

    df = df.loc[df[p_prot].notna()].copy()
    parsed = df[eff_col].map(_parse_est_ci_str)
    df["protein_symbol"] = df[p_prot].astype(str).str.strip()
    df["effect_est"] = [t[0] for t in parsed]
    df["ci_low"] = [t[1] for t in parsed]
    df["ci_high"] = [t[2] for t in parsed]
    df["p_value"] = pd.to_numeric(df[pval_col], errors="coerce")
    df["fdr"] = pd.to_numeric(df[fdr_col], errors="coerce")
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df["protein_symbol"].str.upper().isin(gset)].copy()

    return {
        "dataset_id": "DS_SUPP_PAN2026_OLINK",
        "modality": assert_expansion_modality(mod, "DS_SUPP_PAN2026_OLINK"),
        "sheet": sheet,
        "contrast_label": contrast_lbl,
        "estimator_note": est_note,
        "df": df.reset_index(drop=True),
    }


def load_ran2026_prefals_olink(
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Ran 2026 Nature Medicine Pre-FALS Olink HT (Suppl Table S1: significant-only N=137 subset, sparse-safe)."""
    p = resolve_expansion_file("41591_2026_4528_MOESM3", "DS_SUPP_RAN2026_PREFALS", verify_hash=verify_hash)
    s1 = read_xlsx_sparse_safe(p, "Suppl Table S1", header_row_1based=3)
    prot_c = resolve_col(s1, "Protein")
    est_c = resolve_col(s1, "Estimate")
    p_c = resolve_col(s1, "Pr_t")
    padj_c = resolve_col(s1, "padj")

    s1 = s1.loc[s1[prot_c].notna()].copy()
    s1["protein_symbol"] = s1[prot_c].astype(str).str.strip()
    for c in (est_c, p_c, padj_c):
        s1[c] = pd.to_numeric(s1[c], errors="coerce")
    # Preserve literal author column; guard 5 author-rounded padj==0.0 rows (rows 39-43: MYOC, TRAK1, PPY, TTN, PRND)
    s1["padj_raw"] = s1[padj_c]
    s1["padj_rounded_zero_artifact"] = (s1["padj_raw"] == 0.0) & (s1[p_c] > 0.0)
    s1["padj_provenance_safe"] = np.where(s1["padj_rounded_zero_artifact"], np.nan, s1["padj_raw"])
    assert_contrast_columns_aligned(s1, est_c, p_c, "padj_provenance_safe", None, "Ran2026:S1")

    if genes is not None:
        gset = {g.upper() for g in genes}
        s1 = s1.loc[s1["protein_symbol"].str.upper().isin(gset)].copy()

    return {
        "dataset_id": "DS_SUPP_RAN2026_PREFALS",
        "modality": assert_expansion_modality("PROTEOMICS_PLASMA_OLINK", "DS_SUPP_RAN2026_PREFALS"),
        "contrast_label": "PreFALS_Discovery_OlinkHT_ALS_vs_Ctrl_log2FC",
        "table_scope": "SIGNIFICANT_SUBSET_ONLY_N137",
        "estimator_note": "MixedEffects_log2FC_t_BH_FDR (5 author-rounded padj==0.0 rows flagged in padj_rounded_zero_artifact)",
        "df": s1.reset_index(drop=True),
    }


def load_rocapereira2026_csf(
    sheet: str = "Suppl. Data S1A - ALS vs. Cntrl",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Roca-Pereira 2026 Bellvitge CSF proteomics (ALS vs Cntrl or Short vs Long Survival) with contrast assertions."""
    zp = resolve_expansion_file("PMC13429306_supplements.zip", "DS_SUPP_ROCAPEREIRA2026_CSF", verify_hash=verify_hash)
    tmp_xlsx = META_DIR / "_cache_rocapereira2026.xlsx"
    if not tmp_xlsx.exists():
        with zipfile.ZipFile(zp) as zf:
            tmp_xlsx.write_bytes(zf.read("BPA-36-e70089-s001.xlsx"))
    df = read_xlsx_sparse_safe(tmp_xlsx, sheet, header_row_1based=1)
    gcol = resolve_col(df, "Gene")
    pep_col = resolve_col(df, "Peptides")
    lfc_col = resolve_col(df, "Log2 FoldChange")
    p_col = resolve_col(df, "p-value")
    q_col = resolve_col(df, "q-value")

    df = df.loc[df[gcol].notna()].copy()
    df["primary_gene"] = df[gcol].astype(str).str.split(";").str[0].str.strip()
    for c in (pep_col, lfc_col, p_col, q_col):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["q_value_raw"] = df[q_col]
    df["q_rounded_zero_artifact"] = (df["q_value_raw"] == 0.0) & (df[p_col] > 0.0)
    df["q_provenance_safe"] = np.where(df["q_rounded_zero_artifact"], np.nan, df["q_value_raw"])
    # Flag single-peptide or extreme left-censored Perseus imputation fold-changes (e.g. PIKFYVE 1-pep +17.44 log2FC)
    df["imputation_or_single_pep_flag"] = (df[pep_col].fillna(0) < 2) | (df[lfc_col].abs() > 8.0)
    # Perseus reports empirical permutation q-values (can sit slightly below parametric t-test p)
    assert_contrast_columns_aligned(df, lfc_col, p_col, "q_provenance_safe", None, f"RocaPereira2026:{sheet}", allow_empirical_q=True)
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df["primary_gene"].str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS_SUPP_ROCAPEREIRA2026_CSF",
        "modality": assert_expansion_modality("PROTEOMICS_CSF_DIA", "DS_SUPP_ROCAPEREIRA2026_CSF"),
        "sheet": sheet,
        "contrast_label": sheet,
        "effect_col": lfc_col,
        "p_col": p_col,
        "adj_p_col": "q_provenance_safe",
        "q_method_note": "Perseus empirical permutation q-value (q==0.0 floored; single-peptide/extreme |log2FC|>8 flagged in imputation_or_single_pep_flag)",
        "n_rounded_zero_q": int(df["q_rounded_zero_artifact"].sum()),
        "n_flagged_artifacts": int(df["imputation_or_single_pep_flag"].sum()),
        "df": df.reset_index(drop=True),
    }


# ---------------------------------------------------------------------------
# 3. Independent Human Tissue Proteomics & Bulk RNA-seq Loaders
# ---------------------------------------------------------------------------

def _load_uniprot_entry_to_gene() -> dict[str, str]:
    p = META_DIR / "uniprot_human_entry_to_gene.tsv"
    if not p.exists():
        return {}
    df = pd.read_csv(p, sep="\t", dtype=str)
    id_col = resolve_col(df, "Entry Name")
    g_col = resolve_col(df, "Gene Names (primary)")
    return dict(zip(df[id_col].astype(str).str.upper(), df[g_col].fillna("").astype(str).str.strip()))


def load_munich2025_ba6_proteomics(genes: list[str] | None = None, verify_hash: bool = False) -> dict[str, Any]:
    """Load Munich BA6 human sALS proteomics (STRICTLY human-datasets, mapped via Swiss-Prot Entry Name -> HGNC)."""
    deg_z = resolve_expansion_file("proteomics_deg.zip", "DS053_MUNICH_BA6_PROT", verify_hash=verify_hash)
    cnt_z = resolve_expansion_file("proteomics_counts.zip", "DS053_MUNICH_BA6_PROT", verify_hash=verify_hash)
    sm_z = resolve_expansion_file("sample_map.zip", "DS053_MUNICH_BA6_PROT", verify_hash=verify_hash)
    with zipfile.ZipFile(deg_z) as zf:
        h_deg = [n for n in zf.namelist() if "human-datasets" in n and n.endswith(".csv")][0]
        deg_df = pd.read_csv(zf.open(h_deg))
    with zipfile.ZipFile(cnt_z) as zf:
        h_cnt = [n for n in zf.namelist() if "human-datasets" in n and n.endswith(".csv")][0]
        cnt_df = pd.read_csv(zf.open(h_cnt))
    with zipfile.ZipFile(sm_z) as zf:
        h_sm = [n for n in zf.namelist() if "human-datasets" in n and n.endswith(".tsv")][0]
        sm_df = pd.read_csv(zf.open(h_sm), sep="\t")

    up_map = _load_uniprot_entry_to_gene()
    u_col = resolve_col(deg_df, "UniProtName")
    lfc_col = resolve_col(deg_df, "log2FoldChange")
    p_col = resolve_col(deg_df, "pvalue")
    q_col = resolve_col(deg_df, "padj")
    assert_contrast_columns_aligned(deg_df, lfc_col, p_col, q_col, None, "Munich2025_BA6")

    deg_df["gene_symbol"] = [
        up_map.get(str(u).strip().upper(), str(u).split("_")[0].strip())
        for u in deg_df[u_col]
    ]
    if genes is not None:
        gset = {g.upper() for g in genes}
        deg_df = deg_df.loc[
            deg_df["gene_symbol"].astype(str).str.upper().isin(gset)
            | deg_df[u_col].astype(str).str.upper().isin(gset)
        ].copy()
    return {
        "dataset_id": "DS053_MUNICH_BA6_PROT",
        "modality": assert_expansion_modality("PROTEOMICS_TISSUE_LIMMA", "DS053_MUNICH_BA6_PROT"),
        "contrast_label": "human_BA6_ALS_vs_Ctrl_no_covariates",
        "effect_col": lfc_col,
        "p_col": p_col,
        "adj_p_col": q_col,
        "deg_df": deg_df.reset_index(drop=True),
        "intensity_df": cnt_df,
        "sample_map_df": sm_df,
    }


def load_spiteri2025_4region_proteomics(
    region: str = "all",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Spiteri 2025 4-region human ALS limma proteomics with exact paired contrast assertions."""
    reg_map = {
        "all": ("M.all_vs_C.all_diff", "M.all_vs_C.all_p.val", "M.all_vs_C.all_p.adj"),
        "cervical": ("M.cervical_vs_C.cervical_diff", "M.cervical_vs_C.cervical_p.val", "M.cervical_vs_C.cervical_p.adj"),
        "lumbar": ("M.lumbar_vs_C.lumbar_diff", "M.lumbar_vs_C.lumbar_p.val", "M.lumbar_vs_C.lumbar_p.adj"),
        "Mcx": ("M.Mcx_vs_C.Mcx_diff", "M.Mcx_vs_C.Mcx_p.val", "M.Mcx_vs_C.Mcx_p.adj"),
        "Thor": ("M.Thor_vs_C.Thor_diff", "M.Thor_vs_C.Thor_p.val", "M.Thor_vs_C.Thor_p.adj"),
    }
    if region not in reg_map:
        raise ValueError(f"Unknown Spiteri region={region!r}; valid={sorted(reg_map)}")
    eff_c, p_c, q_c = reg_map[region]

    p = resolve_expansion_file("41598_2025_11466_MOESM1", "DS_SUPP_SPITERI2025_4REG", verify_hash=verify_hash)
    df = read_xlsx_sparse_safe(p, "Human limma results", header_row_1based=1)
    sym_col = resolve_col(df, "Gene.Symbol")
    name_col = resolve_col(df, "name")
    resolve_col(df, eff_c)
    resolve_col(df, p_c)
    resolve_col(df, q_c)
    assert_contrast_columns_aligned(df, eff_c, p_c, q_c, f"M.{region}_vs_C.{region}", f"Spiteri2025:{region}")

    df["primary_gene"] = df[sym_col].fillna(df[name_col]).astype(str).str.split(";").str[0].str.strip()
    df["effect_est"] = pd.to_numeric(df[eff_c], errors="coerce")
    # Spiteri M.all_vs_C.all_diff is literally the 4-region sum (cervical+lumbar+Mcx+Thor); provide mean per region too
    df["effect_est_mean_per_region"] = df["effect_est"] / 4.0 if region == "all" else df["effect_est"]
    df["p_value"] = pd.to_numeric(df[p_c], errors="coerce")
    df["adj_p"] = pd.to_numeric(df[q_c], errors="coerce")
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df["primary_gene"].str.upper().isin(gset) | df[name_col].astype(str).str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS_SUPP_SPITERI2025_4REG",
        "modality": assert_expansion_modality("PROTEOMICS_TISSUE_LIMMA", "DS_SUPP_SPITERI2025_4REG"),
        "region": region,
        "contrast_label": f"M.{region}_vs_C.{region}",
        "effect_col": eff_c,
        "p_col": p_c,
        "adj_p_col": q_c,
        "estimator_note": "limma_moderated_t_BH_adj",
        "df": df.reset_index(drop=True),
    }


def load_feneberg2025_oxford_proteomics(
    fraction: str = "SPC insoluble",
    contrast: str = "ALS vs control",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Feneberg 2025 Oxford soluble/insoluble proteome with strict paired contrast enforcement."""
    valid_fracs = ("SPC soluble", "SPC insoluble", "CTX soluble", "CTX insoluble")
    valid_contrasts = ("ALS vs control", "ALS vs non-ALS", "ALS vs AD")
    if fraction not in valid_fracs:
        raise ValueError(f"Unknown fraction={fraction!r}; expected one of {valid_fracs}")
    if contrast not in valid_contrasts:
        raise ValueError(f"Unknown contrast={contrast!r}; expected one of {valid_contrasts}")

    p = resolve_expansion_file("40478_2025_2084_MOESM3", "DS_SUPP_FENEBERG2025_OXF", verify_hash=verify_hash)
    df = read_xlsx_sparse_safe(p, fraction, header_row_1based=1)
    gcol = resolve_col(df, "Gene symbol")
    fc_col = resolve_col(df, f"Fold change - {contrast}")
    p_col = resolve_col(df, f"p-value - {contrast}")
    q_col = resolve_col(df, f"FDR-adjusted p-value - {contrast}")
    assert_contrast_columns_aligned(df, fc_col, p_col, q_col, contrast, f"Feneberg2025:{fraction}")

    df["primary_gene"] = df[gcol].astype(str).str.split(";").str[0].str.strip()
    # Verified across all 4 sheets: 'Fold change - ...' is ALREADY log2(FC) centered at 0.0 (~50% negative values)!
    df["log2_fc"] = pd.to_numeric(df[fc_col], errors="coerce")
    df["linear_fold_change"] = np.power(2.0, df["log2_fc"])
    df["p_value"] = pd.to_numeric(df[p_col], errors="coerce")
    df["fdr"] = pd.to_numeric(df[q_col], errors="coerce")
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df["primary_gene"].str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS_SUPP_FENEBERG2025_OXF",
        "modality": assert_expansion_modality("PROTEOMICS_TISSUE_SOLUBLE_INSOLUBLE", "DS_SUPP_FENEBERG2025_OXF"),
        "fraction": fraction,
        "contrast_label": contrast,
        "effect_col": fc_col,
        "p_col": p_col,
        "adj_p_col": q_col,
        "estimator_note": "Author_log2_FoldChange_direct_plus_BH_FDR",
        "df": df.reset_index(drop=True),
    }


def load_miedema2025_ftld_tdp_c(genes: list[str] | None = None, verify_hash: bool = False, deduplicate_genes: bool = True) -> dict[str, Any]:
    """Load Miedema 2025 FTLD-TDP type C cortical proteome (+log2FC_NDCvsSD = Higher abundance in SD vs NDC; deduped to 1 row/gene)."""
    p = resolve_expansion_file("40478_2025_2077_MOESM4", "DS_SUPP_TISSUE_BIOFLUID_2025_2026", verify_hash=verify_hash)
    df = read_xlsx_sparse_safe(p, "Proteome_statistics", header_row_1based=1)
    gcol = resolve_col(df, "gene_symbols_or_id_ONLYFIRSTannotation")
    lfc_c = resolve_col(df, "log2FC_NDCvsSD")
    p_c = resolve_col(df, "pvalue_NDCvsSD")
    q_c = resolve_col(df, "qvalue_NDCvsSD")
    assert_contrast_columns_aligned(df, lfc_c, p_c, q_c, "NDCvsSD", "Miedema2025")
    for c in (lfc_c, p_c, q_c):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["primary_gene"] = df[gcol].astype(str).str.split(";").str[0].str.strip()
    if deduplicate_genes:
        df = df.sort_values(p_c, ascending=True, na_position="last").drop_duplicates(subset=["primary_gene"], keep="first").copy()
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df["primary_gene"].str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS_SUPP_MIEDEMA2025_FTLD",
        "modality": assert_expansion_modality("PROTEOMICS_TISSUE_TMT_FTLD", "DS_SUPP_MIEDEMA2025_FTLD"),
        "contrast_label": "SD_FTLD_TDP_C_vs_NDC",
        "sign_note": "Positive log2FC_NDCvsSD corresponds to FC_direction == 'Higher abundance' in SD (FTLD-TDP-C) vs NDC.",
        "df": df.reset_index(drop=True),
    }


def load_edinburgh_gse314526_bulk(
    region: str = "BA44",
    genes: list[str] | None = None,
    exclude_v14_overlaps: bool = False,
    verify_hash: bool = False,
    normalization: str = "deseq2_mor",
) -> dict[str, Any]:
    """Load GSE314526 Edinburgh paired bulk RNA-seq (transposed CGND_ID x ENSG), 1 row/donor, DESeq2 norm + covariate OLS."""
    meta = pd.read_csv(META_DIR / "GSE314526_sample_metadata.tsv", sep="\t", dtype=str)
    if region not in ("BA44", "BA46"):
        raise ValueError(f"Specify single region 'BA44' or 'BA46' (got {region!r}) to avoid donor pooling")
    sub = meta.loc[meta["char_tissue"] == region].copy()
    if exclude_v14_overlaps:
        ov = get_v14_overlap_donors("DS065_EDIN_COGNITIVE_BULK")
        sub = sub.loc[~sub["char_donor_id"].map(_norm_donor_token).isin(ov)].copy()
    assert_unique_donors(sub["char_donor_id"].tolist(), f"DS065_GSE314526:{region}")

    cnt_p = resolve_expansion_file("GSE314526_BA44_BA46_COUNT_DATA.tsv.gz", "DS065_EDIN_COGNITIVE_BULK", verify_hash=verify_hash)
    df_raw = pd.read_csv(cnt_p, sep="\t", index_col=0)
    sub["cgnd_id"] = sub["Sample_description"].astype(str).str.extract(r"(CGND-[A-Za-z0-9\-]+)", expand=False)
    if sub["cgnd_id"].isna().all():
        for c in sub.columns:
            ext = sub[c].astype(str).str.extract(r"(CGND-[A-Za-z0-9\-]+)", expand=False)
            if ext.notna().sum() >= 10:
                sub["cgnd_id"] = ext
                break
    sub = sub.loc[sub["cgnd_id"].isin(df_raw.index)].copy()
    assert_unique_donors(sub["char_donor_id"].tolist(), f"DS065_GSE314526:{region}:matched")

    mat_sxg = df_raw.loc[sub["cgnd_id"].tolist()].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    lib_sizes = mat_sxg.sum(axis=1).to_numpy(dtype=np.float64)
    mat_gxs = mat_sxg.T

    gc_df = pd.read_csv(ROOT / "data/transcriptomics/ensembl116_hsapiens_gene_gc.tsv", sep="\t")
    ens_to_sym = dict(zip(gc_df["Gene stable ID"].astype(str), gc_df["Gene name"].fillna("").astype(str)))
    ens_to_gc = dict(zip(gc_df["Gene stable ID"].astype(str), pd.to_numeric(gc_df["Gene % GC content"], errors="coerce")))
    ens_clean_all = [str(x).split(".")[0] for x in mat_gxs.index]
    gc_all = np.array([ens_to_gc.get(e, np.nan) for e in ens_clean_all], dtype=float)
    vgc = np.isfinite(gc_all)
    w_all = mat_gxs.to_numpy(dtype=float)[vgc, :]
    gc_mean = (gc_all[vgc] @ w_all) / np.maximum(w_all.sum(axis=0), 1.0)
    sub = sub.copy()
    sub["gc_z"] = (gc_mean - np.mean(gc_mean)) / np.std(gc_mean, ddof=1) if len(gc_mean) >= 3 else np.nan

    ens_clean = pd.Index(ens_clean_all)
    syms = pd.Series([ens_to_sym.get(e, e) or e for e in ens_clean], index=mat_gxs.index)
    full_mat_arr = mat_gxs.to_numpy(dtype=np.float64)
    full_syms_arr = syms.to_numpy()
    if genes is not None:
        gset = {g.upper() for g in genes}
        keep = syms.str.upper().isin(gset) | ens_clean.str.upper().isin(gset)
        mat_gxs = mat_gxs.loc[keep].copy()
        syms = syms.loc[keep]

    mat_gxs.index = syms.values
    mat_gxs = mat_gxs.groupby(level=0, sort=False).sum()
    l2_arr, norm_used, _ = _normalize_counts_to_log2(full_mat_arr, full_syms_arr, mat_gxs.to_numpy(dtype=np.float64), lib_sizes, normalization=normalization)
    log2cpm = pd.DataFrame(l2_arr, index=mat_gxs.index, columns=sub["char_donor_id"].tolist())

    sub_idx = sub.set_index("char_donor_id")
    case_d = sub.loc[sub["char_als_phenotype"].isin(["ALS", "ALSci"]), "char_donor_id"].tolist()
    ctrl_d = sub.loc[sub["char_als_phenotype"] == "Control", "char_donor_id"].tolist()
    stats_by_gene: dict[str, dict[str, Any]] = {}
    if genes is not None and case_d and ctrl_d:
        sel_d = case_d + ctrl_d
        is_case = np.array([1.0] * len(case_d) + [0.0] * len(ctrl_d))
        cov_dict = _encode_covariate_matrix(sub_idx.loc[sel_d])
        for g in log2cpm.index:
            st = _welch_mwu(log2cpm.loc[g, case_d].to_numpy(float), log2cpm.loc[g, ctrl_d].to_numpy(float))
            ols = _covariate_adjusted_ols(log2cpm.loc[g, sel_d].to_numpy(float), is_case, cov_dict)
            stats_by_gene[str(g)] = {**st, **ols}

    return {
        "dataset_id": "DS065_EDIN_COGNITIVE_BULK",
        "modality": assert_expansion_modality("BULK_RNASEQ_COUNTS", "DS065_EDIN_COGNITIVE_BULK"),
        "region": region,
        "normalization_used": norm_used,
        "exclude_v14_overlaps": exclude_v14_overlaps,
        "meta_df": sub.reset_index(drop=True),
        "log2cpm_df": log2cpm,
        "n_case": len(case_d),
        "n_ctrl": len(ctrl_d),
        "stats": stats_by_gene,
    }


# ---------------------------------------------------------------------------
# 4. Splicing, TDP-43, Functional CRISPR Screens, Genetics & QTL Loaders
# ---------------------------------------------------------------------------

def load_kozareva2025_compendium(
    table: str = "S6",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Kozareva 2025 TDP-43 multi-omic compendium (S1=iNeuron DE, S6=splicing, S15=postmortem DE)."""
    pat_map = {
        "S1": "table_S1_de_ds_ineurons.tsv",
        "S6": "table_S6_splicing_compendium.tsv",
        "S7": "table_S7_inferred_tf_activity.tsv",
        "S11": "table_S11_network_nodes.tsv",
        "S15": "table_S15_postmortem_de.tsv",
    }
    if table not in pat_map:
        raise ValueError(f"Unknown Kozareva table={table!r}; valid={sorted(pat_map)}")
    p = resolve_expansion_file(pat_map[table], "DS_SUPP_KOZAREVA2025", verify_hash=verify_hash)
    df = pd.read_csv(p, sep="\t", low_memory=False)
    if genes is not None:
        gset = {g.upper() for g in genes}
        gcol = next((c for c in ("gene_name", "external_gene_name", "TF") if c in df.columns), df.columns[0])
        df = df.loc[df[gcol].astype(str).str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS_SUPP_KOZAREVA2025",
        "modality": assert_expansion_modality("SPLICING_COMPENDIUM_MULTIOMIC", "DS_SUPP_KOZAREVA2025"),
        "table": table,
        "df": df.reset_index(drop=True),
    }


def load_ryan2025_tdp43_crispri(genes: list[str] | None = None, verify_hash: bool = False) -> dict[str, Any]:
    """Load all 4 Ryan 2025 eLife genome-wide TDP-43 CRISPRi screens with verbatim XML polarity metadata (explicit RRA score sort)."""
    dfs = []
    for k in (1, 2, 3, 4):
        sk = f"supp{k}"
        p = resolve_expansion_file(f"elife-104057-{sk}-v1.txt", "DS_SUPP_RYAN2025_CRISPRI", verify_hash=verify_hash)
        df = pd.read_csv(p, sep="\t")
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
        df["p-value"] = pd.to_numeric(df["p-value"], errors="coerce")
        df = df.sort_values(["score", "p-value"], ascending=[True, True], na_position="last").reset_index(drop=True)
        df["rank_in_screen"] = np.arange(1, len(df) + 1)
        df["screen_supp"] = sk
        df["cell_model"] = RYAN2025_SCREEN_META[sk]["cell_model"]
        df["polarity"] = RYAN2025_SCREEN_META[sk]["polarity"]
        df["estimator"] = RYAN2025_SCREEN_META[sk]["estimator"]
        if genes is not None:
            gset = {g.upper() for g in genes}
            df = df.loc[df[resolve_col(df, "target")].astype(str).str.upper().isin(gset)].copy()
        dfs.append(df)
    combined = pd.concat(dfs, ignore_index=True)
    return {
        "dataset_id": "DS_SUPP_RYAN2025_CRISPRI",
        "modality": assert_expansion_modality("CRISPR_SCREEN_GENOMEWIDE", "DS_SUPP_RYAN2025_CRISPRI"),
        "screen_metadata": RYAN2025_SCREEN_META,
        "df": combined,
    }


def load_crisprbrain_screens(
    screen: str = "tian2021_survival_noao",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load CRISPRbrain genome-wide iPSC neuron/astrocyte screens (deduplicating Leng 2022 H1+TFs overlap)."""
    if screen.startswith("tian2021_"):
        sheet_map = {
            "tian2021_survival_noao": "Survival_noAO_CRISPRi",
            "tian2021_survival_plusao": "Survival_plusAO_CRISPRi",
            "tian2021_liperfluo": "Liperfluo_CRISPRi",
            "tian2021_lysotracker": "Lysotracker_CRISPRi",
            "tian2021_ferhonox": "FeRhoNox-1_CRISPRi",
        }
        p = resolve_expansion_file("41593_2021_862_MOESM3", "DS_SUPP_CRISPRBRAIN_GLIA_NEURON", verify_hash=verify_hash)
        df = read_xlsx_sparse_safe(p, sheet_map[screen], header_row_1based=1)
        gcol = resolve_col(df, "Gene")
    elif screen == "leng2022_astrocyte":
        p = resolve_expansion_file("41593_2022_1180_MOESM4", "DS_SUPP_CRISPRBRAIN_GLIA_NEURON", verify_hash=verify_hash)
        h1 = read_xlsx_sparse_safe(p, "H1_combined", header_row_1based=1)
        h1["library"] = "H1_druggable"
        tfs = read_xlsx_sparse_safe(p, "TFs_combined", header_row_1based=1)
        tfs["library"] = "TFs"
        df = pd.concat([h1, tfs], ignore_index=True)
        gcol = resolve_col(df, "gene")
        # Deduplicate overlapping H1 + TFs genes, retaining the row with strongest min p-value across phago/VCAM1
        p_cols = [c for c in ("pvalue.phago.ITC", "pvalue.VCAM1.ITC") if c in df.columns]
        if p_cols:
            df["_min_p"] = df[p_cols].apply(pd.to_numeric, errors="coerce").min(axis=1).fillna(1.0)
            df = df.sort_values("_min_p", ascending=True).drop_duplicates(subset=[gcol], keep="first").drop(columns=["_min_p"]).copy()
    else:
        raise ValueError(f"Unknown CRISPRbrain screen={screen!r}")
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df[gcol].astype(str).str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS_SUPP_CRISPRBRAIN_GLIA_NEURON",
        "modality": assert_expansion_modality("CRISPR_SCREEN_GENOMEWIDE", "DS_SUPP_CRISPRBRAIN_GLIA_NEURON"),
        "screen": screen,
        "df": df.reset_index(drop=True),
    }


def load_hop2026_exome_burden(
    level: str = "gene",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Hop 2026 Nature Genetics N=25,069 ALS exome rare-variant burden across genome-wide tables.

    `level`:
      - 'gene': MOESM6 genome-wide gene-level burden (17,324 genes: gene_id, gene_name, P)
      - 'gene_bins': MOESM7 per-gene variant-bin burden (48,461 rows: OR, ORCIlower, ORCIupper, P)
      - 'domain': MOESM8 protein-domain burden (65,071 rows: domain_name, P)
      - 'pathway': MOESM10 gene-set burden (11,777 pathways: geneSet, P_exclsiggenes, P)
      - 'variants_main' / 'variants_all': MOESM5 curated variant-level Excel sheets
    """
    if level == "gene":
        p = resolve_expansion_file("41588_2026_2535_MOESM6_ESM.csv", "DS_SUPP_HOP2026_EXOME", verify_hash=verify_hash)
        df = pd.read_csv(p)
        gcol = resolve_col(df, "gene_name")
        df["P"] = pd.to_numeric(df[resolve_col(df, "P")], errors="coerce")
        scope = "GENOMEWIDE_N17324_GENES"
    elif level == "gene_bins":
        p = resolve_expansion_file("41588_2026_2535_MOESM7_ESM.csv", "DS_SUPP_HOP2026_EXOME", verify_hash=verify_hash)
        df = pd.read_csv(p)
        gcol = resolve_col(df, "gene_name")
        for c in ("OR", "ORCIlower", "ORCIupper", "P"):
            df[c] = pd.to_numeric(df[resolve_col(df, c)], errors="coerce")
        scope = "GENOMEWIDE_GENE_VARIANT_BINS"
    elif level == "domain":
        p = resolve_expansion_file("41588_2026_2535_MOESM8_ESM.csv", "DS_SUPP_HOP2026_EXOME", verify_hash=verify_hash)
        df = pd.read_csv(p)
        gcol = resolve_col(df, "gene_name")
        df["P"] = pd.to_numeric(df[resolve_col(df, "P")], errors="coerce")
        scope = "GENOMEWIDE_PROTEIN_DOMAINS"
    elif level == "pathway":
        p = resolve_expansion_file("41588_2026_2535_MOESM10_ESM.csv", "DS_SUPP_HOP2026_EXOME", verify_hash=verify_hash)
        df = pd.read_csv(p)
        gcol = resolve_col(df, "geneSet")
        scope = "GENOMEWIDE_GENESETS"
    elif level in ("variants_main", "variants_all", "main_analysis", "all"):
        sh = "all" if level in ("variants_all", "all") else "main_analysis"
        p = resolve_expansion_file("41588_2026_2535_MOESM5", "DS_SUPP_HOP2026_EXOME", verify_hash=verify_hash)
        df = read_xlsx_sparse_safe(p, sh, header_row_1based=1)
        gcol = resolve_col(df, "gene_name")
        scope = f"CURATED_VARIANTS_{sh.upper()}"
    else:
        raise ValueError(f"Unknown Hop 2026 level={level!r}")

    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df[gcol].astype(str).str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS_SUPP_HOP2026_EXOME",
        "modality": assert_expansion_modality("EXOME_BURDEN_GENEWIDE", "DS_SUPP_HOP2026_EXOME"),
        "level": level,
        "table_scope": scope,
        "df": df.reset_index(drop=True),
    }


def load_drager2022_microglia_crispr(genes: list[str] | None = None, verify_hash: bool = False) -> dict[str, Any]:
    """Load Drager 2022 Nature Neuroscience human iTF-Microglia CRISPRi/a screens (ST3, disambiguating merged 2-row headers)."""
    import openpyxl

    p = resolve_expansion_file("41593_2022_1131_MOESM4", "DS_SUPP_CRISPRBRAIN_GLIA_NEURON", verify_hash=verify_hash)
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    try:
        rows = list(wb["Supplementary Table 3"].iter_rows(values_only=True))
    finally:
        wb.close()
    # Disambiguate duplicate 'pvalue.phago' / 'product.phago' between CRISPRi Phagocytosis and CRISPRa Phagocytosis
    r1, r2 = rows[0], rows[1]
    group_prefix = ""
    headers: list[str] = []
    for h1, h2 in zip(r1, r2):
        if h1 is not None and str(h1).strip():
            group_prefix = str(h1).strip()
        sub = str(h2).strip() if h2 is not None and str(h2).strip() else ""
        if not sub:
            headers.append(group_prefix)
        elif "CRISPRa" in group_prefix:
            headers.append(f"crispra_{sub}")
        else:
            headers.append(sub)
    df = pd.DataFrame(rows[2:], columns=headers)
    gcol = resolve_col(df, "gene")
    for c in headers[2:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df[gcol].astype(str).str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS_SUPP_CRISPRBRAIN_GLIA_NEURON",
        "modality": assert_expansion_modality("CRISPR_SCREEN_GENOMEWIDE", "DS_SUPP_CRISPRBRAIN_GLIA_NEURON"),
        "screen": "drager2022_microglia_st3",
        "df": df.reset_index(drop=True),
    }


def load_bolger2026_isoseq(
    cohort: str = "i3n_transcript",
    ensembl_ids: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Bolger 2026 IsoSeq long-read Bambu transcript CPM or gene counts (i3N TDP-43 KD & postmortem NYGC)."""
    cmap = {
        "i3n_transcript": ("GSE310723_i3N_isoseq_CPM_transcript.txt.gz", "LONGREAD_ISOSEQ_TRANSCRIPTS"),
        "i3n_gene": ("GSE310723_i3N_isoseq_counts_gene.txt.gz", "LONGREAD_ISOSEQ_TRANSCRIPTS"),
        "nygc_transcript": ("GSE315972_NYGC_isoseq_CPM_transcript.txt.gz", "LONGREAD_ISOSEQ_TRANSCRIPTS"),
        "nygc_gene": ("GSE315972_NYGC_isoseq_counts_gene.txt.gz", "LONGREAD_ISOSEQ_TRANSCRIPTS"),
    }
    if cohort not in cmap:
        raise ValueError(f"Unknown Bolger cohort={cohort!r}; valid={sorted(cmap)}")
    fname, mod = cmap[cohort]
    p = resolve_expansion_file(fname, "DS055_BOLGER_CRYPTE_ISOSEQ", verify_hash=verify_hash)
    df = pd.read_csv(p, sep="\t")
    gcol = resolve_col(df, "GENEID")
    df["ensg_clean"] = df[gcol].astype(str).str.split(".").str[0]
    if "TXNAME" in df.columns:
        df["is_novel_bambu_tx"] = df["TXNAME"].astype(str).str.startswith("BambuTx")
    if ensembl_ids is not None:
        eset = {e.split(".")[0].upper() for e in ensembl_ids}
        df = df.loc[df["ensg_clean"].str.upper().isin(eset)].copy()
    return {
        "dataset_id": "DS055_BOLGER_CRYPTE_ISOSEQ",
        "modality": assert_expansion_modality(mod, "DS055_BOLGER_CRYPTE_ISOSEQ"),
        "cohort": cohort,
        "df": df.reset_index(drop=True),
    }


def load_exeter2025_nanopore(
    ensembl_ids: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Exeter 2025 GSE290441 Nanopore long-read counts (E5 & E8 lines: NES cytoplasmic TDP-43 vs Ctrl nanobody)."""
    p = resolve_expansion_file("GSE290441_tdp43_all_chr.counts.tsv.gz", "DS061_EXETER_TDP43_NANOPORE", verify_hash=verify_hash)
    df = pd.read_csv(p, sep="\t")
    id_col = resolve_col(df, "ID")
    df["ensg_clean"] = df[id_col].astype(str).str.extract(r"(ENSG\d+)", expand=False).fillna("")
    if ensembl_ids is not None:
        eset = {e.split(".")[0].upper() for e in ensembl_ids}
        df = df.loc[df["ensg_clean"].str.upper().isin(eset)].copy()
    ctrl_cols = [c for c in df.columns if "_ctrl_" in c.lower()]
    nes_cols = [c for c in df.columns if "_nes_" in c.lower()]
    return {
        "dataset_id": "DS061_EXETER_TDP43_NANOPORE",
        "modality": assert_expansion_modality("LONGREAD_NANOPORE_COUNTS", "DS061_EXETER_TDP43_NANOPORE"),
        "ctrl_cols": ctrl_cols,
        "nes_cols": nes_cols,
        "df": df.reset_index(drop=True),
    }


def load_keuss2025_soma_neurite(
    fraction: str = "Neurite",
    treatment: str = "TDP43-knockdown",
    control: str = "nontargeting-sgRNA",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Keuss 2025 GSE299341 soma vs neurite TDP-43 / hnRNPA1 knockdown RNA-seq (log2CPM)."""
    meta = pd.read_csv(META_DIR / "GSE299341_sample_metadata.tsv", sep="\t", dtype=str)
    meta["lib_col"] = meta["Sample_description"].astype(str).str.replace(r"^Library name:\s*", "", regex=True).str.strip()
    sub = meta.loc[(meta["char_fraction"] == fraction) & (meta["char_treatment"].isin([treatment, control]))].copy()
    if sub.empty:
        raise ValueError(f"No Keuss samples for fraction={fraction!r}, treatment={treatment!r}, control={control!r}")

    p = resolve_expansion_file("GSE299341_feature_counts.csv.gz", "DS062_KEUSS_SOMA_NEURITE", verify_hash=verify_hash)
    df_all = pd.read_csv(p, index_col=0)
    sub = sub.loc[sub["lib_col"].isin(df_all.columns)].copy()
    assert_unique_donors(sub["lib_col"].tolist(), f"DS062_KEUSS:{fraction}:{treatment}")

    gc_df = pd.read_csv(ROOT / "data/transcriptomics/ensembl116_hsapiens_gene_gc.tsv", sep="\t")
    ens_to_sym = dict(zip(gc_df["Gene stable ID"].astype(str), gc_df["Gene name"].fillna("").astype(str)))

    mat = df_all[sub["lib_col"].tolist()].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    lib_sizes = mat.sum(axis=0).to_numpy(dtype=np.float64)
    ens_clean = pd.Index([str(x).split(".")[0] for x in mat.index])
    syms = pd.Series([ens_to_sym.get(e, e) or e for e in ens_clean], index=mat.index)
    if genes is not None:
        gset = {g.upper() for g in genes}
        keep = syms.str.upper().isin(gset) | ens_clean.str.upper().isin(gset)
        mat = mat.loc[keep].copy()
        syms = syms.loc[keep]
    mat.index = syms.values
    mat = mat.groupby(level=0, sort=False).sum()
    log2cpm = pd.DataFrame(np.log2((mat.to_numpy(dtype=np.float64) / lib_sizes[None, :]) * 1e6 + 1.0), index=mat.index, columns=mat.columns)

    case_cols = sub.loc[sub["char_treatment"] == treatment, "lib_col"].tolist()
    ctrl_cols = sub.loc[sub["char_treatment"] == control, "lib_col"].tolist()
    stats_by_gene = {
        str(g): _welch_mwu(log2cpm.loc[g, case_cols].to_numpy(float), log2cpm.loc[g, ctrl_cols].to_numpy(float))
        for g in log2cpm.index
    } if (genes is not None and case_cols and ctrl_cols) else {}

    return {
        "dataset_id": "DS062_KEUSS_SOMA_NEURITE",
        "modality": assert_expansion_modality("BULK_RNASEQ_COUNTS", "DS062_KEUSS_SOMA_NEURITE"),
        "fraction": fraction,
        "treatment": treatment,
        "control": control,
        "n_case": len(case_cols),
        "n_ctrl": len(ctrl_cols),
        "log2cpm_df": log2cpm,
        "stats": stats_by_gene,
    }


def load_rummens2025_tdp43_agg(
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Rummens 2025 GSE284828 TDP-43 aggregate-sorted vs non-aggregate-sorted U2OS counts (3 vs 3)."""
    p = resolve_expansion_file("GSE284828_All_Samples_Counts.csv.gz", "DS066_RUMMENS_TDP43_AGG", verify_hash=verify_hash)
    df = pd.read_csv(p)
    gcol = resolve_col(df, "Gene Name")
    agg_cols = [c for c in df.columns if c.startswith("Aggregates_Sorted_")]
    no_cols = [c for c in df.columns if c.startswith("NoAggregates_Sorted_")]
    assert len(agg_cols) == 3 and len(no_cols) == 3
    all_cols = agg_cols + no_cols
    mat = df[all_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    lib_sizes = mat.sum(axis=0).to_numpy(dtype=np.float64)
    if genes is not None:
        gset = {g.upper() for g in genes}
        keep = df[gcol].astype(str).str.upper().isin(gset)
        mat = mat.loc[keep].copy()
        idx_names = df.loc[keep, gcol].astype(str).values
    else:
        idx_names = df[gcol].astype(str).values
    mat.index = idx_names
    mat = mat.groupby(level=0, sort=False).sum()
    log2cpm = pd.DataFrame(np.log2((mat.to_numpy(dtype=np.float64) / lib_sizes[None, :]) * 1e6 + 1.0), index=mat.index, columns=all_cols)
    stats_by_gene = {
        str(g): _welch_mwu(log2cpm.loc[g, agg_cols].to_numpy(float), log2cpm.loc[g, no_cols].to_numpy(float))
        for g in log2cpm.index
    } if genes is not None else {}
    return {
        "dataset_id": "DS066_RUMMENS_TDP43_AGG",
        "modality": assert_expansion_modality("BULK_RNASEQ_COUNTS", "DS066_RUMMENS_TDP43_AGG"),
        "n_case": len(agg_cols),
        "n_ctrl": len(no_cols),
        "log2cpm_df": log2cpm,
        "stats": stats_by_gene,
    }


def query_bryois2022_celltype_eqtl(
    cell_type: str,
    chroms: list[str] | None = None,
    ensembl_ids: set[str] | None = None,
    gene_symbols: set[str] | None = None,
    p_threshold: float = 1e-4,
) -> dict[str, Any]:
    """Stream Bryois 2022 8-cell-type brain sc-eQTL shards (space-delimited: GENE_ENSG rsid dist pval beta)."""
    valid_cts = ("Astrocytes", "Endothelial", "Excitatory", "Inhibitory", "Microglia", "OPCs", "Oligodendrocytes", "Pericytes")
    if cell_type not in valid_cts:
        raise ValueError(f"Unknown Bryois cell_type={cell_type!r}; valid={valid_cts}")
    m = _get_manifest()
    sub = m.loc[(m["dataset_id"] == "DS_QTL_BRYOIS_8LINEAGE") & (m["filename"].str.startswith(f"{cell_type}."))]
    if chroms is not None:
        cset = {str(c).replace("chr", "") for c in chroms}
        sub = sub.loc[sub["filename"].map(lambda fn: fn.split(".")[1] in cset)]
    e_up = {e.split(".")[0].upper() for e in ensembl_ids} if ensembl_ids else None
    g_up = {g.upper() for g in gene_symbols} if gene_symbols else None

    rows: list[tuple[str, str, str, int, float, float]] = []
    for rel in sub["local_relpath"]:
        p = ROOT / rel
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) < 5:
                    continue
                pval = float(parts[3])
                if pval > p_threshold:
                    continue
                feat = parts[0]
                if "_" in feat:
                    gsym, ensg = feat.rsplit("_", 1)
                else:
                    gsym, ensg = feat, ""
                if e_up is not None and ensg.upper() not in e_up and (g_up is None or gsym.upper() not in g_up):
                    continue
                if e_up is None and g_up is not None and gsym.upper() not in g_up:
                    continue
                rows.append((gsym, ensg, parts[1], int(parts[2]), pval, float(parts[4])))
    df = pd.DataFrame(rows, columns=["gene_symbol", "ensembl_id", "rsid", "tss_distance", "p_value", "beta"])
    return {
        "dataset_id": "DS_QTL_BRYOIS_8LINEAGE",
        "modality": assert_expansion_modality("EQTL_SQTL_SUMSTATS", "DS_QTL_BRYOIS_8LINEAGE"),
        "cell_type": cell_type,
        "df": df,
    }


def load_nygc_te_subfamilies(
    region_group: str = "cortex",
    tissue_filter: str | None = None,
    te_prefixes: list[str] | None = None,
) -> dict[str, Any]:
    """Load compiled NYGC RepeatMasker TE subfamily log2CPM (collapsing repeated samples to 1 row/donor)."""
    if region_group not in ("cortex", "cord"):
        raise ValueError(f"region_group must be 'cortex' or 'cord', got {region_group!r}")
    meta = pd.read_csv(PB_DIR / f"nygc_te_{region_group}_meta.tsv", sep="\t")
    if tissue_filter is not None:
        meta = meta.loc[meta["tissue"].astype(str).str.lower() == tissue_filter.lower()].copy()
    cnt = pd.read_csv(PB_DIR / f"nygc_te_{region_group}_counts.tsv.gz", sep="\t", index_col=0)
    if te_prefixes is not None:
        pref_up = tuple(p.upper() for p in te_prefixes)
        cnt = cnt.loc[cnt.index.astype(str).str.upper().str.startswith(pref_up)].copy()

    # Collapse multi-region libraries per donor_id by summing raw TE counts & total_library_counts (zero donor pseudoreplication!)
    donor_groups = meta.groupby("donor_id", sort=True)
    d_cols: dict[str, np.ndarray] = {}
    d_meta_rows: list[dict[str, Any]] = []
    for did, gdf in donor_groups:
        gsms = gdf["sample_gsm"].tolist()
        tot_lib = float(pd.to_numeric(gdf["total_library_counts"], errors="coerce").sum())
        if tot_lib <= 0:
            continue
        te_sum = cnt[gsms].sum(axis=1).to_numpy(dtype=np.float64)
        d_cols[str(did)] = np.log2((te_sum / tot_lib) * 1e6 + 1.0)
        d_meta_rows.append({
            "donor_id": str(did),
            "disease_group": str(gdf["disease_group"].iloc[0]),
            "n_libraries_collapsed": int(len(gsms)),
            "tissues": ";".join(sorted(gdf["tissue"].astype(str).unique())),
            "total_library_counts": int(tot_lib),
        })
    d_meta = pd.DataFrame(d_meta_rows)
    assert_unique_donors(d_meta["donor_id"].tolist(), f"DS060_NYGC_TE:{region_group}")
    log2cpm = pd.DataFrame(d_cols, index=cnt.index)

    case_d = d_meta.loc[d_meta["disease_group"].isin(["ALS", "ALS+FTD"]), "donor_id"].tolist()
    ctrl_d = d_meta.loc[d_meta["disease_group"] == "CTL", "donor_id"].tolist()
    stats_by_te = {
        str(te): _welch_mwu(log2cpm.loc[te, case_d].to_numpy(float), log2cpm.loc[te, ctrl_d].to_numpy(float))
        for te in log2cpm.index
    } if (te_prefixes is not None and case_d and ctrl_d) else {}

    return {
        "dataset_id": "DS060_NYGC_TE_CORTEX_CORD",
        "modality": assert_expansion_modality("TE_RETROTRANSPOSON_BULK", "DS060_NYGC_TE_CORTEX_CORD"),
        "region_group": region_group,
        "overlap_warning": "100% donor overlap with v1.4 NYGC Flagship/O'Neill; cross-modal TE assay layer, NOT independent cohort.",
        "meta_df": d_meta,
        "log2cpm_df": log2cpm,
        "n_case": len(case_d),
        "n_ctrl": len(ctrl_d),
        "stats": stats_by_te,
    }


def load_zelic2025_cervical_bulk(genes: list[str] | None = None, verify_hash: bool = False) -> dict[str, Any]:
    """Load Zelic 2025 GSE287256 cervical spinal cord normalized bulk RNA-seq (8 ALS vs 4 Control, NIH NBB)."""
    meta = pd.read_csv(META_DIR / "GSE287256_sample_metadata.tsv", sep="\t", dtype=str)
    meta["lib_col"] = meta["Sample_description"].astype(str).str.replace(r"^Library name:\s*", "", regex=True).str.strip()
    meta["donor_id"] = meta["Sample_title"].astype(str).str.extract(r"Donor ID\s*(\d+)", expand=False)
    meta["disease_group"] = np.where(meta["Sample_title"].astype(str).str.contains("_ALS"), "ALS", "Control")
    assert_unique_donors(meta["donor_id"].tolist(), "DS057_ZELIC_BULK")

    p = resolve_expansion_file("GSE287256_ALS_bulkRNAseq", "DS057_ZELIC_CERVICAL_SNRNA", verify_hash=verify_hash)
    df = pd.read_csv(p)
    gcol = resolve_col(df, "gene_name")
    cols = meta["lib_col"].tolist()
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df[gcol].astype(str).str.upper().isin(gset)].copy()
    mat = df[cols].apply(pd.to_numeric, errors="coerce")
    mat.index = df[gcol].astype(str).values
    mat = mat.groupby(level=0, sort=False).sum()
    log2_df = np.log2(mat.clip(lower=0.0) + 1.0)
    case_c = meta.loc[meta["disease_group"] == "ALS", "lib_col"].tolist()
    ctrl_c = meta.loc[meta["disease_group"] == "Control", "lib_col"].tolist()
    stats_by_gene = {
        str(g): _welch_mwu(log2_df.loc[g, case_c].to_numpy(float), log2_df.loc[g, ctrl_c].to_numpy(float))
        for g in log2_df.index
    } if genes is not None else {}
    return {
        "dataset_id": "DS057_ZELIC_BULK",
        "modality": assert_expansion_modality("BULK_RNASEQ_COUNTS", "DS057_ZELIC_BULK"),
        "meta_df": meta[["donor_id", "lib_col", "disease_group"]].reset_index(drop=True),
        "log2_df": log2_df,
        "n_case": len(case_c),
        "n_ctrl": len(ctrl_c),
        "stats": stats_by_gene,
    }


def load_muscle2025_proteome(genes: list[str] | None = None, verify_hash: bool = False) -> dict[str, Any]:
    """Load PXD060425 human skeletal muscle MaxQuant LFQ proteome (5 ALS vs 5 CON, filtering Reverse/Contaminant)."""
    mp = resolve_expansion_file("file_mapping.txt", "DS063_MUSCLE_PROT_2025", verify_hash=verify_hash)
    zp = resolve_expansion_file("SEARCH_prot.zip", "DS063_MUSCLE_PROT_2025", verify_hash=False)
    mmap = pd.read_csv(mp, sep="\t")
    mmap["run_num"] = mmap["RAW file background proteome"].astype(str).str.extract(r"_(\d+)\.raw$", expand=False)
    mmap["lfq_col"] = "LFQ intensity " + mmap["run_num"]
    assert_unique_donors(mmap["run_num"].tolist(), "DS063_MUSCLE_PROT_2025")

    with zipfile.ZipFile(zp) as zf:
        pg = pd.read_csv(zf.open("SEARCH/proteinGroups.txt"), sep="\t", low_memory=False)
    # Standard MaxQuant QC filter: remove Reverse, Potential contaminant, Only identified by site
    for qc_col in ("Reverse", "Potential contaminant", "Only identified by site"):
        if qc_col in pg.columns:
            pg = pg.loc[pg[qc_col].astype(str).str.strip() != "+"].copy()
    gcol = resolve_col(pg, "Gene names")
    pg["primary_gene"] = pg[gcol].fillna("").astype(str).str.split(";").str[0].str.strip()
    pg = pg.loc[pg["primary_gene"] != ""].copy()
    if genes is not None:
        gset = {g.upper() for g in genes}
        pg = pg.loc[pg["primary_gene"].str.upper().isin(gset)].copy()

    lfq_cols = mmap["lfq_col"].tolist()
    vals = pg[lfq_cols].apply(pd.to_numeric, errors="coerce")
    log2_df = np.log2(vals.where(vals > 0))
    log2_df.index = pg["primary_gene"].values
    if not log2_df.index.is_unique:
        log2_df = log2_df.copy()
        log2_df["_nn"] = log2_df.notna().sum(axis=1)
        log2_df = log2_df.sort_values("_nn", ascending=False).groupby(level=0, sort=False).first().drop(columns=["_nn"])

    case_c = mmap.loc[mmap["Group"] == "ALS", "lfq_col"].tolist()
    ctrl_c = mmap.loc[mmap["Group"] == "CON", "lfq_col"].tolist()
    stats_by_gene = {
        str(g): _welch_mwu(log2_df.loc[g, case_c].to_numpy(float), log2_df.loc[g, ctrl_c].to_numpy(float))
        for g in log2_df.index
    } if genes is not None else {}
    return {
        "dataset_id": "DS063_MUSCLE_PROT_2025",
        "modality": assert_expansion_modality("PROTEOMICS_MUSCLE_DIA", "DS063_MUSCLE_PROT_2025"),
        "meta_df": mmap[["Sample", "run_num", "lfq_col", "Group"]].reset_index(drop=True),
        "log2_df": log2_df,
        "n_case": len(case_c),
        "n_ctrl": len(ctrl_c),
        "stats": stats_by_gene,
    }


def load_smeyers2025_tbk1_detection(
    dataset_part: str = "TiO2_fractions_neurons",
    genes: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Smeyers 2025 PXD068150 Protein Prospector 1%-FDR identification list (QUALITATIVE DETECTION ONLY — no TMT channel quantification in staged files)."""
    p = resolve_expansion_file(dataset_part, "DS059_SMEYERS_TBK1_PHOSPHO", verify_hash=verify_hash)
    df = read_xlsx_sparse_safe(p, "Sheet1", header_row_1based=8)
    gcol = resolve_col(df, "Gene")
    df = df.loc[df[gcol].notna()].copy()
    df["gene_symbol"] = df[gcol].astype(str).str.strip()
    if genes is not None:
        gset = {g.upper() for g in genes}
        df = df.loc[df["gene_symbol"].str.upper().isin(gset)].copy()
    return {
        "dataset_id": "DS059_SMEYERS_TBK1_PHOSPHO",
        "modality": assert_expansion_modality("PROTEIN_IDENTIFICATION_ONLY_NO_QUANT", "DS059_SMEYERS_TBK1_PHOSPHO"),
        "dataset_part": dataset_part,
        "quant_warning": "Staged PRIDE files are 1%-FDR Protein Prospector identification lists only (no WT vs TBK1-KO TMT reporter fold-changes).",
        "df": df.reset_index(drop=True),
    }


def load_miga_microglia_eqtl(
    region: str = "MFG",
    ensembl_ids: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load MiGA human microglia top cis-eQTL summary statistics (MFG/STG/SVZ/THA)."""
    p = resolve_expansion_file(f"{region}_eur_expression_.*\\.cis_qtl\\.txt\\.gz$", "DS_QTL_MIGA_MICROGLIA", verify_hash=verify_hash)
    df = pd.read_csv(p, sep="\t")
    df["ensg_clean"] = df[resolve_col(df, "phenotype_id")].astype(str).str.split(".").str[0]
    if ensembl_ids is not None:
        eset = {e.split(".")[0].upper() for e in ensembl_ids}
        df = df.loc[df["ensg_clean"].str.upper().isin(eset)].copy()
    return {
        "dataset_id": "DS_QTL_MIGA_MICROGLIA",
        "modality": assert_expansion_modality("EQTL_SQTL_SUMSTATS", "DS_QTL_MIGA_MICROGLIA"),
        "region": region,
        "df": df.reset_index(drop=True),
    }


def load_humphrey_spinal_cord_qtl(
    region: str = "Cervical",
    qtl_type: str = "expression",
    ensembl_ids: list[str] | None = None,
    verify_hash: bool = False,
) -> dict[str, Any]:
    """Load Humphrey 2023 spinal cord eQTL or sQTL top summary statistics (Cervical/Lumbar/Thoracic)."""
    pat = f"{region}SpinalCord_{qtl_type}_.*\\.cis_qtl\\.txt\\.gz$"
    p = resolve_expansion_file(pat, "DS_QTL_HUMPHREY_SC", verify_hash=verify_hash)
    df = pd.read_csv(p, sep="\t")
    pid_col = resolve_col(df, "phenotype_id")
    df["ensg_clean"] = df[pid_col].astype(str).str.extract(r"(ENSG\d+)", expand=False).fillna(df[pid_col].astype(str))
    if ensembl_ids is not None:
        eset = {e.split(".")[0].upper() for e in ensembl_ids}
        df = df.loc[df["ensg_clean"].str.upper().isin(eset)].copy()
    return {
        "dataset_id": "DS_QTL_HUMPHREY_SC",
        "modality": assert_expansion_modality("EQTL_SQTL_SUMSTATS", "DS_QTL_HUMPHREY_SC"),
        "region": region,
        "qtl_type": qtl_type,
        "df": df.reset_index(drop=True),
    }


def compute_smr_stats(
    gwas_beta: float,
    gwas_se: float,
    qtl_beta: float,
    qtl_se: float,
) -> dict[str, float]:
    """Compute exact Zhu et al. (2016) SMR statistic propagating BOTH GWAS and cis-QTL first-stage uncertainty.

    T_SMR = (z_g^2 * z_q^2) / (z_g^2 + z_q^2) ~ chi2(df=1), preventing naive Wald-ratio qtl_beta cancellation.
    """
    if not all(math.isfinite(x) for x in (gwas_beta, gwas_se, qtl_beta, qtl_se)) or gwas_se <= 0 or qtl_se <= 0 or abs(qtl_beta) < 1e-12:
        return {"z_gwas": float("nan"), "z_qtl": float("nan"), "qtl_f_stat": float("nan"), "t_smr": float("nan"), "p_smr": float("nan")}
    z_g = float(gwas_beta / gwas_se)
    z_q = float(qtl_beta / qtl_se)
    zg2 = z_g * z_g
    zq2 = z_q * z_q
    denom = zg2 + zq2
    if denom <= 0:
        return {"z_gwas": z_g, "z_qtl": z_q, "qtl_f_stat": zq2, "t_smr": 0.0, "p_smr": 1.0}
    t_smr = float((zg2 * zq2) / denom)
    p_smr = float(stats.chi2.sf(t_smr, df=1))
    return {
        "z_gwas": round(z_g, 4),
        "z_qtl": round(z_q, 4),
        "qtl_f_stat": round(zq2, 2),
        "t_smr": round(t_smr, 4),
        "p_smr": p_smr,
    }


def query_vanrheenen2021_gwas(
    rsids: set[str] | None = None,
    ancestry: str = "EUR",
    verify_hash: bool = False,
    drop_multiallelic: bool = True,
) -> dict[str, Any]:
    """Stream van Rheenen 2021 ALS GWAS summary statistics (GRCh37) filtered to a target rsid set, dropping multiallelic rsIDs cleanly."""
    fname = "GCST90027164_buildGRCh37.tsv.gz" if ancestry.upper() == "EUR" else "GCST90027163_buildGRCh37.tsv.gz"
    p = resolve_expansion_file(fname, "DS_GWAS_VANRHEENEN2021", verify_hash=verify_hash)
    rows: list[list[str]] = []
    header: list[str] = []
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        header = fh.readline().rstrip("\r\n").split("\t")
        rs_i = header.index("rsid")
        for line in fh:
            parts = line.rstrip("\r\n").split("\t")
            if rsids is None or parts[rs_i] in rsids:
                rows.append(parts)
    df = pd.DataFrame(rows, columns=header)
    n_multiallelic_dropped = 0
    if drop_multiallelic and not df.empty:
        dup_mask = df["rsid"].duplicated(keep=False)
        n_multiallelic_dropped = int(dup_mask.sum())
        df = df.loc[~dup_mask].reset_index(drop=True)
    for c in ("base_pair_location", "effect_allele_frequency", "beta", "standard_error", "p_value", "N_effective"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return {
        "dataset_id": "DS_GWAS_VANRHEENEN2021",
        "modality": assert_expansion_modality("GWAS_SUMSTATS_GRCH37", "DS_GWAS_VANRHEENEN2021"),
        "ancestry": ancestry.upper(),
        "n_multiallelic_dropped": n_multiallelic_dropped,
        "df": df,
    }


__all__ = [
    "ASSAY_PHYSICS_CAPABILITIES",
    "EXPANSION_ALLOWED_MODALITIES",
    "PSEUDOBULK_MODALITY_MAP",
    "RYAN2025_SCREEN_META",
    "assert_contrast_columns_aligned",
    "assert_contrast_pair",
    "assert_expansion_modality",
    "bh_fdr_with_provenance_guard",
    "classify_pack_c_evidence",
    "compute_lineage_ambient_flags",
    "compute_smr_stats",
    "get_v14_overlap_donors",
    "load_bolger2026_isoseq",
    "load_crisprbrain_screens",
    "load_dellar2025_csf_dia",
    "load_drager2022_microglia_crispr",
    "load_edinburgh_gse314526_bulk",
    "load_exeter2025_nanopore",
    "load_expansion_pseudobulk",
    "load_feneberg2025_oxford_proteomics",
    "load_gse308462_tissue",
    "load_hop2026_exome_burden",
    "load_humphrey_spinal_cord_qtl",
    "load_keuss2025_soma_neurite",
    "load_kozareva2025_compendium",
    "load_miedema2025_ftld_tdp_c",
    "load_miga_microglia_eqtl",
    "load_munich2025_ba6_proteomics",
    "load_muscle2025_proteome",
    "load_nygc_te_subfamilies",
    "load_omar2025_capillary",
    "load_paired_strata_pseudobulk",
    "load_pan2026_ukb_alsrisc",
    "load_ran2026_prefals_olink",
    "load_rocapereira2026_csf",
    "load_ruf2026_paired_tdp43",
    "load_rummens2025_tdp43_agg",
    "load_ryan2025_tdp43_crispri",
    "load_smeyers2025_tbk1_detection",
    "load_spiteri2025_4region_proteomics",
    "load_zelic2025_cervical_bulk",
    "query_bryois2022_celltype_eqtl",
    "query_vanrheenen2021_gwas",
    "resolve_expansion_file",
]
