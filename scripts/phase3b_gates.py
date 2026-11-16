"""Hardened Phase 3B validators: 0 ExploreALS overlap, schema parity, Epistemic Asymmetry, bidirectional off-target rules, & biosecurity."""
from __future__ import annotations

import json
from pathlib import Path
import re

from phase3_gates import (
    ALLOWED_ACTIONABILITY_TIERS,
    ALLOWED_EVIDENCE_BASIS,
    ALLOWED_GATE_CLASS,
    ALLOWED_OFFTARGET_STATUS,
    ALLOWED_TRL,
    MODEL_PRIOR_RE,
    RAW_OLIGO_SEQ_RE,
    _read_text_or_gz,
    _reject_nan_const,
    _sha12,
)
from provenance_gates import verify_provenance_gates

ALLOWED_P3B_TIER = ALLOWED_ACTIONABILITY_TIERS | {"BIOMARKER_BENCHMARK_ONLY", "DROPPED_FALSIFIED_EXCLUDED"}
ALLOWED_P3B_GATE = ALLOWED_GATE_CLASS | {"NOT_APPLICABLE_FALSIFIED"}
ALLOWED_P3B_BASIS = ALLOWED_EVIDENCE_BASIS | {"MEASURED_HUMAN_CSF_PROTEOMICS"}
ALLOWED_P3B_DEC = {"KEEP_CORE", "KEEP_EXPLORATORY_UNPROVEN", "RECLASSIFY_BENCHMARK_OR_BIOMARKER", "DROP"}
ALLOWED_P3B_EPI = {"SUPPORTED", "UNPROVEN_UNTESTED", "FALSIFIED_CLINICAL", "FALSIFIED_PK_SAFETY", "ARTIFACT_CONFOUNDED", "ESTABLISHED_BENCHMARK"}
FALSIFIED_P3B = {"FALSIFIED_CLINICAL", "FALSIFIED_PK_SAFETY", "ARTIFACT_CONFOUNDED"}
GAPPED_OLIGO_RE = re.compile(r"(?:[+mflr2*]?\s*[ACGTU]\s*[-*ps]+\s*){14}[+mflr2*]?\s*[ACGTU]", re.IGNORECASE)
RANKED_IV_RE = re.compile(r"#([12])(?:`|\s|\|)+\s*`?(chr[0-9XYM]+:\d+-\d+\([+-]\))")
IV_COORD_RE = re.compile(r"chr[0-9XYM]+:\d+-\d+\([+-]\)")
STATUS_TOK_RE = re.compile(
    r"\b(PASS_CLEAN_GE2MM|CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED|WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL|FAIL_EXACT_0MM_OFFTARGET)\b(?!\s*=)"
)

EXP_CAND_COLS = "denovo_id,discovery_funnel,gene_or_drug,candidate_type,primary_modality_specific,mechanism_summary,causal_vs_reactive_assessment,epistemic_state,decision,clinical_readiness_trl,next_gate_experimental_class,primary_evidence_basis,model_prior_dependency,unsolved_hurdle_count,unsolved_hurdles_structured,scientific_actionability_tier,factual_justification,discriminating_next_test,supporting_denovo_evidence_ids,analysis_run_id".split(",")
EXP_SSO_COLS = "denovo_id,gene_symbol,rank_within_gene,interval_id,chrom,grch38_start,grch38_end,strand,length_bp,cis_mechanism_class,gc_pct,tm_phys_pops_c,dg37_kcal,cpg_dinucs,max_self_stem_bp,ese_motifs,mean_avi_phred,max_avi_phred,boundary_dist_bp,composite_score,gggenome_max_mm_queried,spliced_0mm_genes,spliced_1mm_genes,spliced_2mm_pc_genes,spliced_wobble_only_pc_genes,premRNA_0mm_sense_genes,premRNA_1mm_sense_genes,premRNA_1mm_splice50bp_genes,premRNA_wobble_only_splice50bp_pc_genes,premRNA_2mm_splice25bp_pc_genes,bulge_1nt_steric_pc_genes,sub18_core_steric_pc_genes,flagged_constrained_neuronal_hits,offtarget_safety_status,alphagenome_atlas_url,analysis_run_id".split(",")
EXP_EV_COLS = "evidence_id,carbon_id,subnode_id,analysis_run_id,source_type,source_id_or_locator,cohort_and_stratum,assay_and_contrast,effect_direction,effect_estimate,p_value,fdr_or_adjusted_p,sample_size_n,epistemic_weight,notes".split(",")


def _build_explore_exclusions(intake: list[dict[str, str]], subnodes: list[dict[str, str]]) -> tuple[set[str], set[str]]:
    genes = {"TARDBP", "SOD1", "C9ORF72", "FUS", "NPTX2", "NEFL", "NEFH", "GFAP", "IREB2", "PTAR1", "NMNAT2", "ST2"}
    drugs = {
        "riluzole", "baricitinib", "memantine", "trazodone", "apilimod", "icerguastat", "sephin1", "ifb-088",
        "dexmedetomidine", "cuatsm", "mycophenolate mofetil", "mycophenolate", "tamoxifen", "ezogabine", "retigabine",
        "ceftriaxone", "ropinirole", "furosemide", "perampanel", "lonafarnib", "tipifarnib", "aldesleukin",
        "methylcobalamin", "rozebalamin", "censavudine", "tpn-101",
    }
    for r in intake:
        if r["track"] == "B":
            for tok in re.findall(r"[A-Z0-9-]{2,}", r["genes_or_drug_ids"]):
                if tok not in {"GENE", "SYMBOL", "SYMBOLS", "UNIPROT", "Q9UKA1"}:
                    genes.add(tok)
        elif r["track"] == "A":
            for part in re.split(r"[()/;]", r["name"].lower()):
                cleaned = re.sub(r"^(low-dose|ultrahigh-dose)\s+", "", part.strip()).strip()
                if len(cleaned) >= 3:
                    drugs.add(cleaned)
    for sn in subnodes:
        genes.add(sn["gene_symbol"].strip())
    return genes, drugs


def verify_phase3b_gates(
    carbon_root: Path, intake: list[dict[str, str]], subnodes: list[dict[str, str]], runs: list[dict[str, str]], load_csv_fn, cand_override: list[dict[str, str]] | None = None, mode: str = "full",
) -> list[str]:
    errors: list[str] = []
    reg_dir = carbon_root / "registries"
    cand_fp, sso_fp, ev_fp = reg_dir / "phase3b_denovo_candidates.csv", reg_dir / "phase3b_denovo_sso_intervals.csv", reg_dir / "phase3b_denovo_evidence.csv"
    rep_fp = carbon_root / "reports" / "phase3" / "PHASE3B_DENOVO_UNBIASED_DISCOVERY.md"
    req_fps = (cand_fp, sso_fp, ev_fp, rep_fp) if mode == "full" else (cand_fp, sso_fp, ev_fp)
    for fp in req_fps:
        if not fp.is_file():
            errors.append(f"Missing mandatory Phase 3B artifact: {fp.relative_to(carbon_root).as_posix()}")
    if errors:
        return errors

    run_ids = {r["analysis_run_id"] for r in runs}
    excl_genes, excl_drugs = _build_explore_exclusions(intake, subnodes)
    cands = cand_override if cand_override is not None else load_csv_fn("phase3b_denovo_candidates.csv")
    sso_rows, ev_rows = load_csv_fn("phase3b_denovo_sso_intervals.csv"), load_csv_fn("phase3b_denovo_evidence.csv")
    for name, rows, exp in (("phase3b_denovo_candidates.csv", cands, EXP_CAND_COLS), ("phase3b_denovo_sso_intervals.csv", sso_rows, EXP_SSO_COLS), ("phase3b_denovo_evidence.csv", ev_rows, EXP_EV_COLS)):
        if rows and list(rows[0].keys()) != exp:
            errors.append(f"Schema header mismatch in {name}: got {list(rows[0].keys())} != {exp}")

    errors.extend(verify_provenance_gates([], ev_rows, runs))
    cand_by_id = {c["denovo_id"]: c for c in cands}
    if len(cand_by_id) != len(cands):
        errors.append("Duplicate denovo_id in phase3b_denovo_candidates.csv")
    ev_ids = {e["evidence_id"] for e in ev_rows}
    sso_by_dn_rk = {(s["denovo_id"], int(s["rank_within_gene"])): s["interval_id"] for s in sso_rows}
    sso_by_iv = {s["interval_id"]: s for s in sso_rows}

    def _check_iv_status_segments(label: str, text: str) -> None:
        for ln in text.splitlines():
            ms = [m for m in IV_COORD_RE.finditer(ln) if m.group(0) in sso_by_iv]
            for idx, m_iv in enumerate(ms):
                iv_id = m_iv.group(0)
                seg_end = ms[idx + 1].start() if (idx + 1) < len(ms) else len(ln)
                for st_tok in STATUS_TOK_RE.findall(ln[m_iv.end() : seg_end]):
                    exp_st = sso_by_iv[iv_id]["offtarget_safety_status"]
                    if st_tok != exp_st:
                        errors.append(f"{label}: {iv_id} paired with '{st_tok}' != SSO registry '{exp_st}'")

    for e in ev_rows:
        if e["carbon_id"] not in cand_by_id or e["analysis_run_id"] not in run_ids:
            errors.append(f"Phase 3B evidence {e['evidence_id']} has invalid carbon_id/analysis_run_id")
        if cand_override is None:
            for rk_s, iv_c in RANKED_IV_RE.findall(e["effect_estimate"] + " " + e["notes"]):
                if sso_by_dn_rk.get((e["carbon_id"], int(rk_s))) != iv_c:
                    errors.append(f"{e['evidence_id']} cites #{rk_s} {iv_c} != SSO registry {sso_by_dn_rk.get((e['carbon_id'], int(rk_s)))}")

    for c in cands:
        did, gd = c["denovo_id"], c["gene_or_drug"].strip()
        if ";" in gd or "/" in gd or not gd:
            errors.append(f"{did}: non-atomic gene_or_drug '{gd}'")
        if gd in excl_genes or gd.lower() in excl_drugs:
            errors.append(f"EXPLORE_OVERLAP VIOLATION on {did}: '{gd}' overlaps ExploreALS intake/subnodes!")
        if c["epistemic_state"] not in ALLOWED_P3B_EPI or c["decision"] not in ALLOWED_P3B_DEC:
            errors.append(f"{did}: invalid epistemic_state/decision ({c['epistemic_state']}/{c['decision']})")
        if c["decision"] == "DROP":
            if c["epistemic_state"] == "UNPROVEN_UNTESTED":
                errors.append(f"EPISTEMIC VIOLATION on {did}: Cannot DROP an UNPROVEN_UNTESTED candidate!")
            if c["epistemic_state"] not in FALSIFIED_P3B or c["scientific_actionability_tier"] != "DROPPED_FALSIFIED_EXCLUDED":
                errors.append(f"EPISTEMIC VIOLATION on {did}: DROP requires falsified epistemic_state and DROPPED_FALSIFIED_EXCLUDED")
        if c["decision"] == "KEEP_EXPLORATORY_UNPROVEN" and (not c["discriminating_next_test"].strip() or c["discriminating_next_test"].startswith("NONE")):
            errors.append(f"{did}: KEEP_EXPLORATORY_UNPROVEN requires actionable discriminating_next_test")
        if c["clinical_readiness_trl"] not in ALLOWED_TRL or c["next_gate_experimental_class"] not in ALLOWED_P3B_GATE:
            errors.append(f"{did}: invalid TRL or next_gate_experimental_class")
        if c["primary_evidence_basis"] not in ALLOWED_P3B_BASIS or not MODEL_PRIOR_RE.match(c["model_prior_dependency"].strip()):
            errors.append(f"{did}: invalid primary_evidence_basis '{c['primary_evidence_basis']}' or model_prior_dependency")
        if c["scientific_actionability_tier"] not in ALLOWED_P3B_TIER or c["analysis_run_id"] not in run_ids:
            errors.append(f"{did}: invalid scientific_actionability_tier or analysis_run_id")
        if len([x for x in c["unsolved_hurdles_structured"].split(";") if x and x != "NONE"]) != int(c["unsolved_hurdle_count"]):
            errors.append(f"{did}: unsolved_hurdle_count mismatch")
        for eid in filter(None, c["supporting_denovo_evidence_ids"].split(";")):
            if eid not in ev_ids:
                errors.append(f"{did}: missing supporting_denovo_evidence_id '{eid}'")
        if cand_override is None:
            for rk_s, iv_c in RANKED_IV_RE.findall(c["primary_modality_specific"] + " " + c["factual_justification"] + " " + c["discriminating_next_test"]):
                if sso_by_dn_rk.get((did, int(rk_s))) != iv_c:
                    errors.append(f"{did} cites #{rk_s} {iv_c} != SSO registry {sso_by_dn_rk.get((did, int(rk_s)))}")

    zcols = ("spliced_0mm_genes", "spliced_1mm_genes", "spliced_wobble_only_pc_genes", "premRNA_0mm_sense_genes", "premRNA_1mm_splice50bp_genes", "premRNA_wobble_only_splice50bp_pc_genes", "premRNA_2mm_splice25bp_pc_genes", "bulge_1nt_steric_pc_genes", "sub18_core_steric_pc_genes")
    for s in sso_rows:
        st, iv_id, did = s["offtarget_safety_status"], s["interval_id"], s["denovo_id"]
        exp_iv = f"{s['chrom']}:{s['grch38_start']}-{s['grch38_end']}({s['strand']})"
        if iv_id != exp_iv or did not in cand_by_id or (cand_override is None and s["gene_symbol"] != cand_by_id[did]["gene_or_drug"]) or s["gene_symbol"] in excl_genes or s["analysis_run_id"] not in run_ids:
            errors.append(f"{iv_id}: invalid interval_id/denovo_id/gene_symbol/run_id")
        lo, hi, w = int(s["grch38_start"]), int(s["grch38_end"]), int(s["length_bp"])
        if lo > hi or (hi - lo + 1) != w or st not in ALLOWED_OFFTARGET_STATUS:
            errors.append(f"{iv_id}: invalid GRCh38 span or offtarget_safety_status '{st}'")
        if (int(s["spliced_0mm_genes"]) > 0 and st != "FAIL_EXACT_0MM_OFFTARGET") or (st == "FAIL_EXACT_0MM_OFFTARGET" and int(s["spliced_0mm_genes"]) == 0 and int(s["premRNA_0mm_sense_genes"]) == 0):
            errors.append(f"Bidirectional FAIL_0MM violation on {iv_id}")
        if (s["flagged_constrained_neuronal_hits"] != "NONE" and st not in {"WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL", "FAIL_EXACT_0MM_OFFTARGET"}) or (st == "WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL" and s["flagged_constrained_neuronal_hits"] == "NONE"):
            errors.append(f"Bidirectional WARN/flagged violation on {iv_id}: st={st} flags={s['flagged_constrained_neuronal_hits']}")
        is_gap = "GAPMER" in s["cis_mechanism_class"]
        any_risk = any(int(s[zc]) != 0 for zc in zcols) or (is_gap and int(s["premRNA_1mm_sense_genes"]) != 0)
        if (st == "PASS_CLEAN_GE2MM" and any_risk) or (st != "PASS_CLEAN_GE2MM" and not any_risk and s["flagged_constrained_neuronal_hits"] == "NONE"):
            errors.append(f"Bidirectional PASS_CLEAN_GE2MM violation on {iv_id}: st={st}")
        if not s["alphagenome_atlas_url"].startswith("https://deepmind.google.com/science/alphagenome/atlas?"):
            errors.append(f"{iv_id}: invalid alphagenome_atlas_url")

    p3b_work = carbon_root / "work" / "phase3b_denovo_discovery"
    json_paths = [
        *sorted((p3b_work / "cache").glob("*.json")),
        *sorted((p3b_work / "cache").glob("*.json.gz")),
        *sorted((p3b_work / "outputs").glob("*.json")),
        *sorted((p3b_work / "outputs").glob("*.json.gz")),
    ]
    for jfp in json_paths:
        try:
            json.loads(_read_text_or_gz(jfp), parse_constant=_reject_nan_const)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"STRICT JSON VIOLATION in {jfp.relative_to(carbon_root).as_posix()}: {exc}")

    txt_paths = [
        cand_fp, sso_fp, ev_fp,
        *([rep_fp] if rep_fp.is_file() else []),
        *json_paths,
        *[p for sub in ("cache", "outputs", "scripts") if (p3b_work / sub).is_dir() for p in sorted((p3b_work / sub).rglob("*")) if p.is_file() and p.suffix.lower() in {".csv", ".md", ".py", ".tsv", ".txt", ".yaml", ".yml"}],
    ]
    for fp in txt_paths:
        txt = _read_text_or_gz(fp) if fp.suffix == ".gz" else fp.read_text(encoding="utf-8", errors="ignore")
        m = RAW_OLIGO_SEQ_RE.search(txt) or GAPPED_OLIGO_RE.search(txt)
        if m:
            errors.append(f"BIOSECURITY SEQUENCE LEAK in {fp.relative_to(carbon_root).as_posix()}: '{m.group(0)[:20]}'")

    if cand_override is None:
        for e in ev_rows:
            _check_iv_status_segments(e["evidence_id"], e["effect_estimate"] + " " + e["notes"])
        for c in cands:
            _check_iv_status_segments(c["denovo_id"], c["primary_modality_specific"] + " " + c["factual_justification"] + " " + c["discriminating_next_test"])
        if mode == "full" and rep_fp.is_file():
            rep_txt = rep_fp.read_text(encoding="utf-8")
            for rk_s, iv_c in RANKED_IV_RE.findall(rep_txt):
                if iv_c not in sso_by_iv or int(sso_by_iv[iv_c]["rank_within_gene"]) != int(rk_s):
                    errors.append(f"PHASE3B report cites #{rk_s} {iv_c} inconsistent with phase3b_denovo_sso_intervals.csv")
            _check_iv_status_segments("PHASE3B_DENOVO_UNBIASED_DISCOVERY.md", rep_txt)
            if f"REGISTRY_CONCORDANCE_SHA12: denovo_cands={_sha12(cand_fp)} denovo_sso={_sha12(sso_fp)} denovo_ev={_sha12(ev_fp)}" not in rep_txt:
                errors.append("PHASE3B report stale vs registries")
    return errors
