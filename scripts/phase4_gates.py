"""Hardened Phase 4 cross-phase portfolio (52), cis-interval (26), dossier-sync, JSON, & biosecurity validators."""
from __future__ import annotations

import json
from pathlib import Path
import re

from carbon_als.accessions import accession_to_legacy, legacy_to_accession
from phase3_gates import ALLOWED_OFFTARGET_STATUS, ALLOWED_TRL, MODEL_PRIOR_RE, RAW_OLIGO_SEQ_RE, _reject_nan_const, _sha12, _sha12_variants
from phase3b_gates import ALLOWED_P3B_BASIS, ALLOWED_P3B_DEC, ALLOWED_P3B_EPI, ALLOWED_P3B_GATE, ALLOWED_P3B_TIER, FALSIFIED_P3B, GAPPED_OLIGO_RE

EXPLORE_LEAK_RE = re.compile(r"explore\s*->|\bcarbonals\b|0/4\s+explore", re.IGNORECASE)
CAPITAL_DOLLAR_LEAK_RE = re.compile(
    r"(\$\s*\d|\bUSD\b|\bcapital\w*|\bdollar\w*|do[\s_-]*not[\s_-]*fund|\bfund(?:ing|ed)\b|"
    r"\bcheap\w*|\bexpensive\w*|\bbudget\w*|\bevoi\b|cost_horizon|MODERATE_COST)",
    re.IGNORECASE,
)

EXP_ACC_COLS = (
    "accession_id,legacy_id,entity_kind,parent_accession_id,origin_phase,primary_symbol_or_inn,search_aliases"
).split(",")

EXP_PORT_COLS = (
    "unified_rank,accession_id,portfolio_id,origin_phase,origin_subcohort,track,gene_or_drug,candidate_type,primary_modality_specific,"
    "epistemic_state,decision,scientific_actionability_tier,clinical_readiness_trl,next_gate_experimental_class,"
    "primary_evidence_basis,model_prior_dependency,unsolved_hurdle_count,unsolved_hurdles_structured,"
    "lead_cis_interval_id,lead_offtarget_safety_status,key_quantitative_anchor,discriminating_next_test,"
    "source_registry_ref,analysis_run_id"
).split(",")

CIS_BIO_COLS = (
    "gc_pct,tm_phys_pops_c,dg37_kcal,cpg_dinucs,max_self_stem_bp,ese_motifs,"
    "mean_avi_phred,max_avi_phred,boundary_dist_bp,composite_score"
).split(",")

CIS_OT_COLS = (
    "spliced_0mm_genes,spliced_1mm_genes,spliced_2mm_pc_genes,spliced_wobble_only_pc_genes,"
    "premRNA_0mm_sense_genes,premRNA_1mm_sense_genes,premRNA_1mm_splice50bp_genes,premRNA_wobble_only_splice50bp_pc_genes,"
    "premRNA_2mm_splice25bp_pc_genes,bulge_1nt_steric_pc_genes,sub18_core_steric_pc_genes,"
    "flagged_constrained_neuronal_hits,offtarget_safety_status"
).split(",")

EXP_CIS_COLS = [
    "unified_interval_order", "origin_phase", "accession_id", "subnode_accession_id",
    "portfolio_id", "subnode_or_cand_id", "gene_symbol", "program_role", "rank_within_gene",
    "is_promoted_lead", "interval_id", "chrom", "grch38_start", "grch38_end", "strand", "length_bp", "cis_mechanism_or_mode",
    *CIS_BIO_COLS, *CIS_OT_COLS, "source_offtarget_run_id", "analysis_run_id",
]
SITE_WORK_PATH_RE = re.compile(r"work/[A-Za-z0-9_/-]+\.(?:py|json|csv)")
SITE_LEGACY_ID_OR_ALIAS_RE = re.compile(
    r"((?<![A-Za-z0-9])(?:C0(?:0[1-9]|1\d|2[0-4])(?:-?N[1-6])?|S0[1-9]|DN-?(?:0[1-9]|1\d))(?![A-Za-z0-9])|"
    r"EALS-\d{3}(?:\.\d)?\.\.|\bLegacy\s+ID\b|\bLegacy:\s|\bAlias:\s|\baliases\b|"
    r"FLAGSHIP-(?:C0|S0|DN)|reproduce_(?:C0|S0|DN))",
    re.IGNORECASE,
)
SITE_INTERNAL_JARGON_RE = re.compile(
    r"(Single-Entity\s+De\s+Novo|De\s+Novo\s+1-Plex|De\s+Novo\s+Cryptic|De\s+Novo\s+Chemical|"
    r"\bde\s+novo\b(?!\s+(?:mutation|mutations|variant|variants|germline|chemical|biologic|sphingolipid|ceramide|guanosine|purine|pyrimidine|nucleotide|synthesis|biosynthesis|lipogenesis|methylation|assembly|design))|"
    r"\bTrack\s+[AB]\b|src/carbon_als|verify_carbon_als|CARBON_ALS_|CAR-RUN-|"
    r"Primary\s+Registry\s+Audit|Frozen\s+Baseline|Upstream\s+Baseline|baseline\s+annotation|"
    r"Round\s+2\s+hardening|21\s*CFR\s*300\.50|21\s*CFR\s*312\.23|21CFR300|"
    r"\bWhitespace\b(?!-nowrap)|white-space\s+discovery|Crowded\s+1-Plex|Screen\s+Survivors|PREVIOUSLY\s+STATED|"
    r"\[MODEL_PRIOR\]|,\s*MODEL_PRIOR\]|\[MEASURED\]|\[PRIOR\]|\[Survivor\]|T3\+Proto|"
    r"Forest\s+&amp;\s+SVG|5Rs\s+Essay|Excluded\s+4th\s+Axis|SHA-64|"
    r"REGISTRY_CONCORDANCE_SHA12|\(33\s*\+\s*19\)|0\s+chemically\s+modified\s+synthesis-ready|"
    r"Brettschneider\s+Stage\s+II|\bkill[- ]gates?\b|\bWave\s+(?:[A-D]|[1-9])\b|wave_[a-d]_|modeled\s+modeled|(?<!\[);\s*,(?!\])|"
    r"Dropped\s+PK\s+or\s+Safety\s+Infeasible\s+Regimen|GOVERNANCE\s+GUARDRAIL|scientific\s+taste)",
    re.IGNORECASE,
)


def verify_phase4_gates(
    carbon_root: Path,
    decisions: list[dict[str, str]],
    run_ids: set[str],
    load_csv_fn,
    port_override: list[dict[str, str]] | None = None,
    mode: str = "full",
) -> list[str]:
    errors: list[str] = []
    reg_dir = carbon_root / "registries"
    acc_fp = reg_dir / "candidate_accessions.csv"
    port_fp = reg_dir / "phase4_unified_portfolio.csv"
    cis_fp = reg_dir / "phase4_unified_cis_intervals.csv"
    celf_fp = carbon_root / "work" / "phase4_final_synthesis" / "cache" / "celf5_target_profile.json"
    out_fp = carbon_root / "work" / "phase4_final_synthesis" / "outputs" / "run_p4_001_unified_portfolio.json"

    for fp in (acc_fp, port_fp, cis_fp, celf_fp, out_fp):
        if not fp.is_file():
            errors.append(f"Missing mandatory Phase 4 artifact: {fp.relative_to(carbon_root).as_posix()}")
    if errors:
        return errors

    acc_rows = load_csv_fn("candidate_accessions.csv")
    port_rows = port_override if port_override is not None else load_csv_fn("phase4_unified_portfolio.csv")
    cis_rows = load_csv_fn("phase4_unified_cis_intervals.csv")
    if acc_rows and list(acc_rows[0].keys()) != EXP_ACC_COLS:
        errors.append("Schema header mismatch in candidate_accessions.csv")
    if port_rows and list(port_rows[0].keys()) != EXP_PORT_COLS:
        errors.append("Schema header mismatch in phase4_unified_portfolio.csv")
    if cis_rows and list(cis_rows[0].keys()) != EXP_CIS_COLS:
        errors.append("Schema header mismatch in phase4_unified_cis_intervals.csv")

    dec_map = {r["carbon_id"]: r for r in decisions}
    rd_map = {r["candidate_id"]: r for r in load_csv_fn("phase3_execution_readiness.csv")}
    p3b_map = {r["denovo_id"]: r for r in load_csv_fn("phase3b_denovo_candidates.csv")}
    sub_map = {r["subnode_id"]: r for r in load_csv_fn("subnode_dissection.csv")}
    p2_map = {r["interval_id"]: r for r in load_csv_fn("phase2_multiplex_intervals.csv")}
    ot3a_map = {r["interval_id"]: r for r in load_csv_fn("phase3_sso_offtarget_audit.csv")}
    sso3b_map = {r["interval_id"]: r for r in load_csv_fn("phase3b_denovo_sso_intervals.csv")}

    exp_pids = set(dec_map) | set(p3b_map)
    exp_all_legs = exp_pids | set(sub_map)
    if len(acc_rows) != 70 or {r["legacy_id"] for r in acc_rows} != exp_all_legs or len({r["accession_id"] for r in acc_rows}) != 70:
        errors.append("candidate_accessions.csv must be an exact 70-row bijection over 52 candidates + 18 subunits")
    for ar in acc_rows:
        if ar["accession_id"] != legacy_to_accession(ar["legacy_id"]) or accession_to_legacy(ar["accession_id"]) != ar["legacy_id"]:
            errors.append(f"candidate_accessions.csv non-canonical mapping {ar['accession_id']} <-> {ar['legacy_id']}")
    got_pids = [r["portfolio_id"] for r in port_rows]
    if len(got_pids) != len(set(got_pids)) or set(got_pids) != exp_pids:
        errors.append(f"phase4_unified_portfolio.csv portfolio_id set ({len(got_pids)}) != disjoint union of 33 Curated + 19 Phase 3B ({len(exp_pids)})")
    if sorted(int(r["unified_rank"]) for r in port_rows) != list(range(1, len(port_rows) + 1)):
        errors.append("phase4_unified_portfolio.csv unified_rank is not contiguous 1..52")

    exp_ivs = set(ot3a_map) | set(sso3b_map)
    got_ivs = [r["interval_id"] for r in cis_rows]
    if len(got_ivs) != len(set(got_ivs)) or set(got_ivs) != exp_ivs:
        errors.append(f"phase4_unified_cis_intervals.csv interval_id set ({len(got_ivs)}) != union of 12 Phase 3A + 16 Phase 3B ({len(exp_ivs)})")
    if sorted(int(r["unified_interval_order"]) for r in cis_rows) != list(range(1, len(cis_rows) + 1)):
        errors.append("phase4_unified_cis_intervals.csv unified_interval_order is not contiguous 1..28")

    leads_from_cis: dict[str, tuple[str, str]] = {}
    for c in cis_rows:
        iv_id = c["interval_id"]
        src_ot = ot3a_map.get(iv_id) or sso3b_map.get(iv_id)
        src_bio = p2_map.get(iv_id) if c["origin_phase"] == "PHASE2_3A_MULTIPLEX_12" else sso3b_map.get(iv_id)
        if src_ot is None or src_bio is None:
            errors.append(f"{iv_id}: missing source biophysical/offtarget row")
        else:
            for k_bio in CIS_BIO_COLS:
                if c[k_bio] != src_bio[k_bio]:
                    errors.append(f"{iv_id}: Phase 4 {k_bio}='{c[k_bio]}' != source '{src_bio[k_bio]}'")
            for k_ot in CIS_OT_COLS:
                if c[k_ot] != src_ot[k_ot]:
                    errors.append(f"{iv_id}: Phase 4 {k_ot}='{c[k_ot]}' != source '{src_ot[k_ot]}'")
        if c["accession_id"] != legacy_to_accession(c["portfolio_id"]) or c["subnode_accession_id"] != legacy_to_accession(c["subnode_or_cand_id"]):
            errors.append(f"{iv_id}: accession_id/subnode_accession_id mismatch in phase4_unified_cis_intervals.csv")
        lo, hi, w = int(c["grch38_start"]), int(c["grch38_end"]), int(c["length_bp"])
        if lo > hi or (hi - lo + 1) != w or c["offtarget_safety_status"] not in ALLOWED_OFFTARGET_STATUS:
            errors.append(f"{iv_id}: invalid GRCh38 span or offtarget_safety_status")
        if c["portfolio_id"] not in exp_pids or c["analysis_run_id"] not in run_ids or c["source_offtarget_run_id"] not in run_ids:
            errors.append(f"{iv_id}: invalid portfolio_id or run_id in phase4_unified_cis_intervals.csv")
        if c["is_promoted_lead"] == "True":
            if c["portfolio_id"] in leads_from_cis:
                errors.append(f"Multiple promoted leads for {c['portfolio_id']} in phase4_unified_cis_intervals.csv")
            leads_from_cis[c["portfolio_id"]] = (iv_id, c["offtarget_safety_status"])

    for r in port_rows:
        pid = r["portfolio_id"]
        if r["accession_id"] != legacy_to_accession(pid):
            errors.append(f"{pid}: accession_id '{r['accession_id']}' != expected '{legacy_to_accession(pid)}'")
        if r["epistemic_state"] not in ALLOWED_P3B_EPI or r["decision"] not in ALLOWED_P3B_DEC:
            errors.append(f"{pid}: invalid epistemic_state/decision in phase4_unified_portfolio.csv")
        if r["decision"] == "DROP":
            if r["epistemic_state"] == "UNPROVEN_UNTESTED":
                errors.append(f"EPISTEMIC VIOLATION on {pid}: Cannot DROP an UNPROVEN_UNTESTED candidate in Phase 4!")
            if r["epistemic_state"] not in FALSIFIED_P3B or r["scientific_actionability_tier"] != "DROPPED_FALSIFIED_EXCLUDED":
                errors.append(f"EPISTEMIC VIOLATION on {pid}: DROP requires falsified epistemic_state and DROPPED_FALSIFIED_EXCLUDED")
        if r["decision"] == "KEEP_EXPLORATORY_UNPROVEN" and (not r["discriminating_next_test"].strip() or r["discriminating_next_test"].startswith("NONE")):
            errors.append(f"{pid}: KEEP_EXPLORATORY_UNPROVEN requires actionable discriminating_next_test")
        if r["scientific_actionability_tier"] not in ALLOWED_P3B_TIER or r["clinical_readiness_trl"] not in ALLOWED_TRL or r["next_gate_experimental_class"] not in ALLOWED_P3B_GATE:
            errors.append(f"{pid}: invalid scientific_actionability_tier/TRL/next_gate_experimental_class enum in phase4_unified_portfolio.csv")
        if r["primary_evidence_basis"] not in ALLOWED_P3B_BASIS or not MODEL_PRIOR_RE.match(r["model_prior_dependency"].strip()) or r["analysis_run_id"] not in run_ids:
            errors.append(f"{pid}: invalid primary_evidence_basis/model_prior_dependency/analysis_run_id")
        if len([x for x in r["unsolved_hurdles_structured"].split(";") if x and x != "NONE"]) != int(r["unsolved_hurdle_count"]):
            errors.append(f"{pid}: unsolved_hurdle_count mismatch in phase4_unified_portfolio.csv")

        if port_override is None:
            src_row = rd_map.get(pid) or p3b_map.get(pid)
            if pid in dec_map and (r["decision"] != dec_map[pid]["decision"] or r["epistemic_state"] != dec_map[pid]["epistemic_state"]):
                errors.append(f"{pid}: Phase 4 decision/epistemic_state out of sync with candidate_decisions.csv")
            if pid in p3b_map and (r["decision"] != p3b_map[pid]["decision"] or r["epistemic_state"] != p3b_map[pid]["epistemic_state"]):
                errors.append(f"{pid}: Phase 4 decision/epistemic_state out of sync with phase3b_denovo_candidates.csv")
            if src_row is not None:
                for k_chk in ("scientific_actionability_tier", "clinical_readiness_trl", "next_gate_experimental_class", "primary_evidence_basis", "model_prior_dependency", "unsolved_hurdle_count", "unsolved_hurdles_structured"):
                    if r[k_chk] != src_row[k_chk]:
                        errors.append(f"{pid}: Phase 4 {k_chk}='{r[k_chk]}' != source '{src_row[k_chk]}'")
            exp_lead = leads_from_cis.get(pid, ("NONE", "NONE"))
            if (r["lead_cis_interval_id"], r["lead_offtarget_safety_status"]) != exp_lead:
                errors.append(f"{pid}: lead_cis_interval ({r['lead_cis_interval_id']},{r['lead_offtarget_safety_status']}) != {exp_lead}")
            if mode == "full" and pid in dec_map:
                md_txt = (carbon_root / "reports" / "candidates" / f"{pid}.md").read_text(encoding="utf-8")
                if f"accession_id = {r['accession_id']}" not in md_txt or f"unified_rank = #{r['unified_rank']}/52" not in md_txt or f"scientific_actionability_tier = {r['scientific_actionability_tier']}" not in md_txt:
                    errors.append(f"reports/candidates/{pid}.md out of sync with phase4_unified_portfolio.csv")
                if pid in rd_map and f"primary_modality_specific = {rd_map[pid]['primary_modality_specific']}" not in md_txt:
                    errors.append(f"reports/candidates/{pid}.md missing Phase 3A primary_modality_specific sync")

    p4_work = carbon_root / "work" / "phase4_final_synthesis"
    json_paths = [*sorted((p4_work / "cache").glob("*.json")), *sorted((p4_work / "outputs").glob("*.json"))]
    for jfp in json_paths:
        try:
            obj = json.loads(jfp.read_text(encoding="utf-8"), parse_constant=_reject_nan_const)
            if jfp == out_fp and port_override is None:
                st = obj.get("registry_sha12", {})
                if st.get("phase4_unified_portfolio") not in _sha12_variants(port_fp) or st.get("phase4_unified_cis_intervals") not in _sha12_variants(cis_fp):
                    errors.append("run_p4_001_unified_portfolio.json SHA-12 stale vs Phase 4 registries")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"STRICT JSON VIOLATION in {jfp.relative_to(carbon_root).as_posix()}: {exc}")

    synth_md = carbon_root / "reports" / "CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md"
    explorer_html = carbon_root / "reports" / "CARBON_ALS_INTERACTIVE_EXPLORER.html"
    mono_dir = carbon_root / "reports" / "monographs"
    mono_htmls = sorted(mono_dir.glob("*.html")) if mono_dir.is_dir() else []
    gh_docs = (carbon_root / "reports" / "github_pages" / "docs") if mode == "full" else (carbon_root / "docs")
    gh_mono_dir = gh_docs / "monographs"
    gh_mono_htmls = sorted(gh_mono_dir.glob("*.html")) if gh_mono_dir.is_dir() else []
    gh_htmls = [gh_docs / "index.html", *gh_mono_htmls]
    if port_override is None:
        req_step2 = (synth_md, explorer_html, gh_docs / "index.html", gh_docs / ".nojekyll") if mode == "full" else (gh_docs / "index.html", gh_docs / ".nojekyll")
        for req_fp in req_step2:
            if not req_fp.is_file():
                errors.append(f"Missing Phase 4 Step 2 artifact: {req_fp.relative_to(carbon_root).as_posix()}")
        stamp_sets = [
            _sha12_variants(port_fp),
            _sha12_variants(cis_fp),
            _sha12_variants(reg_dir / "phase3_sso_offtarget_audit.csv"),
            _sha12_variants(reg_dir / "phase3_execution_readiness.csv"),
            _sha12_variants(reg_dir / "phase3b_denovo_candidates.csv"),
            _sha12_variants(reg_dir / "phase3b_denovo_sso_intervals.csv"),
        ]
        stamp_re = re.compile(
            r"(?:BUILD_PROVENANCE_SHA12: portfolio=([0-9a-f]{12}) intervals=([0-9a-f]{12}) "
            r"offtarget=([0-9a-f]{12}) readiness=([0-9a-f]{12}) screen_cands=([0-9a-f]{12}) screen_ivs=([0-9a-f]{12})|"
            r"REGISTRY_CONCORDANCE_SHA12: p4_port=([0-9a-f]{12}) p4_cis=([0-9a-f]{12}) "
            r"p3a_ot=([0-9a-f]{12}) p3a_rd=([0-9a-f]{12}) p3b_cand=([0-9a-f]{12}) p3b_sso=([0-9a-f]{12}))"
        )

        def _has_valid_stamp(blob: str) -> bool:
            m_st = stamp_re.search(blob)
            if not m_st:
                return False
            groups = [g for g in m_st.groups() if g is not None]
            return len(groups) == 6 and all(groups[idx] in vs for idx, vs in enumerate(stamp_sets))

        if mode == "full" and synth_md.is_file():
            stxt = synth_md.read_text(encoding="utf-8")
            if not _has_valid_stamp(stxt):
                errors.append("reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md missing or stale REGISTRY_CONCORDANCE_SHA12 stamp")
            if "PMID:40354799" not in stxt or "PMID:40349716" in stxt or re.search(r"\bDS045\b", stxt):
                errors.append("reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md has stale MIROCALS PMID or DS045 shorthand")
            if "miss 60%–75% of top-quintile" in stxt or "in `rs12608932 A/A`" in stxt or "in rs12608932 A/A" in stxt:
                errors.append("reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md has stale v1.0 MS-NEFH responder or binary rs12608932 A/A prose")
            if re.search(r"EALS-\d{3}(?:\.\d)?\.\.", stxt):
                errors.append("reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md has half-translated EALS-NNN.. range token")

        def _audit_explorer_html(html_fp: Path, is_public_export: bool) -> None:
            if not html_fp.is_file():
                return
            lbl = html_fp.relative_to(carbon_root).as_posix()
            htxt = html_fp.read_text(encoding="utf-8")
            if is_public_export:
                if "gstatic.com" in htxt or "window.PUBLIC_WEB_EXPORT=true" not in htxt:
                    errors.append(f"{lbl} fails zero-CDN or PUBLIC_WEB_EXPORT guard")
            elif "https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js" not in htxt or "<style>:where(.hidden){display:none}" not in htxt:
                errors.append(f"{lbl} missing allowlisted Tailwind or hidden fallback")
            if "const DATA_PORT =" not in htxt or "const DATA_MONOGRAPHS =" not in htxt:
                errors.append(f"{lbl} missing DATA_PORT/DATA_MONOGRAPHS payload")
            if "wiki" in htxt.lower():
                errors.append(f"{lbl} contains residual 'wiki' nomenclature")
            if not _has_valid_stamp(htxt):
                errors.append(f"{lbl} missing or stale REGISTRY_CONCORDANCE_SHA12 stamp")
            if "onclick=" in htxt.lower():
                errors.append(f"{lbl} contains inline onclick= (must use delegated data-* listeners)")
            if re.search(r'(?:fill|stroke|font-size|text-anchor)="[^"\n<>]*>', htxt):
                errors.append(f"{lbl} contains unclosed SVG attribute quote")
            if re.search(r"\bDS045\b", htxt):
                errors.append(f"{lbl} contains unexpanded DS045 shorthand")
            if "0 synthetic oligo designs" in htxt.lower() or re.search(r"liability\s*=\s*[0-9.]+\s*pct", htxt, re.I):
                errors.append(f"{lbl} contains retired '0 synthetic oligo designs' or 'liability=...pct' phrasing")
            for banned in (
                "CHEMBL1201587", "ENST00000404917", "L_eff 65 -> 8", "v4.0 TSV", "gnomAD v4.0", "FcRn-attenuated",
                "96 bp upstream of rs12973192",
                "Responsive Step Cards", "Native Wrap", "Honest Multi-Cohort", "Explore -> Carbon",
                "CarbonALS", "Candidate Wiki", "(9 v3)", "Queued for Wave 2", "WAVE 2 REGISTRY",
                "Stream A", "Stream B", "5D liability=", "gene-liability=", "/100",
                "Figure 1", "Figure 2", "Figure 3", "Figure 4", "5. Primary Evidence",
                "1. Right Target", "3. Right Modality",
                "Translational Dossier Schema 3.0", "<footer", "more_in_JSON", "Quantitative Anchor:",
                "PMID:40349716", "PMID:37264228", "PMID:35197629", "D003", "D045", "Phase 3A",
                "fixing intake", "prior intake", "IL1RL1 — Cytosolic vs. ER",
                'font-size="9', 'font-size="10', 'font-size="11',
                "sp0;", "pm1_50", "pm2_25", "sub18_core_nonconstr",
                "!important", "hidden lg:block", "hidden lg:flex", "hidden lg:inline-block",
                "PRE-REGISTERED", "Pre-Registered Next Test", ">[[", "]]<",
                "ExploreALS v1.0", "ExploreALS v1.1", "0 synthetic oligo designs",
                "MIROCALS Ella", "incorporates into synaptic membranes", "spares UNC13A",
                "within DEVOTE", "DEVOTE 50 mg precedent", "normoxic FVC>=80%", "Ct>35", "Ct > 35",
                "PRISMA 2020", "GRADE Summary", "GRADE certainty", "0 Open Targets safety flags", "C9 phenoconv",
                "miss 60%–75% of top-quintile", "miss 60%-75% of top-quintile", "in rs12608932 A/A",
                "ASHA624_or_Cys311_Class", "SARM1 T-lock epistasis", "phenoconversion axis",
                "genotype-modular genotype-stratified",
                "OTS Coordinate", "W3C PROV", "from scratch",
                "BA9-01", "BA9-02", "BA9-03", "BA9-05", "BA9-06", "BA9-07", "BA9-08", "BA9-09", "BA9-10",
                "DROP_FROM_BUNDLE", "Sole GC-adjusted BA9", "HISTORICAL_BA9", "CANONICAL_21",
                "59-Candidate", "Verify in Tab 6", "Inspect in Tab 2", "3. Pathway Genes",
                "SELF_CORRECTION", "RELEASE_MILESTONE", "Self-Corrections",
                "PDB 4M7N", "PMID:36753453", "PMID:37124168",
                "Apilimod (CHEMBL1200798)", "PMX 205 (CHEMBL5653589)", "NCT04248465 N=382 PMID:41187881",
                "26 Arg/Lys", "AVI Phred=20.02", "chr7:44206385", "NCT04313166 terminated",
                "WashU & UMilan contributed 63 ALS", "CSF ~115 nM", "PMID:31892365",
                "Lykke et al.", "Renshaw", "7,862", "7861.6", "Cu_CNS=0.318",
                "assert_contrast_pair enforced", "in HERV-K+ ALS", "slowing vs historical controls",
                "Updated Nov 2026 (v1.2.4)", "Updated Nov 2026 (v1.2.6)", "Updated Nov 2026 (v1.2.8)", "Updated Nov 2026 (v1.2.9)", "ExploreALS v1.2",
                "Audited GRCh38", "programmatically audited", "Auditing provenance from",
                "199 / 199", "199 Evidence", "Phase 3 RAS-ALS",
                "Ryberg et al. 2003 J Neurochem", "deaths 49/175", "8.94x",
                "RESTORE-ALS", "sST2 intervention has ever been tested,",
                "Sarm1-/- lowered plasma pNfH", "Sarm1-/- lowered pNfH",
            ):
                if banned in htxt:
                    errors.append(f"Dossier Schema 3.0 regression in {lbl}: found banned string '{banned}'")
            for req_str in (
                "ExploreALS v1.3", "Ricardo Agoga", "helloimra@proton.me", "github.com/helloimra/ExploreALS",
                "Not Medical Advice", "AI-Assisted Methodology",
                "Sort: Translational Priority Rank", "Sort: Genetic &amp; Pathology Evidence",
                "Human RCT / Genetics", "Human Cohort / PK-PD",
                "In Vitro / 3D or Small-N", "Model / Heuristic Prior", "BioVendor",
                "AF-Q7L622-F1", "NIH GTEx (v8 / v10)", "N/A (SOC / PD Benchmark)", "Rank &amp; Triage Key:", "Study Categories:",
                "Updated Nov 2026 (v1.3.0)", "202 / 202", "UPD-2026-11-23-01",
                "TDP-43 Cryptic Splicing &amp; Polyadenylation (12)",
                "Antemortem CSF Proteomics &amp; Physiology (6)",
                "Patient iPSC-MN Phenotypic Screen (11)",
                "CHEMBL1201438", "ENST00000311734.6", "102343270-102346100(+)", "LOEUF = 1.143",
                "LOEUF = 0.258", "LOEUF = 0.344", "LOEUF = 0.261", "107 bp upstream of rs12973192",
                "Primary Evidence &amp; Reproducibility Table", "Right Target", "Right Modality & Exposure",
                "const DATA_NYGC_META =", "const DATA_FUNNEL =", "const DATA_DROPS =", "const DATA_SUM =",
                "const DATA_LENSES =", "const DATA_CONTRASTS =",
                "const DATA_RUNS =", "const DATA_DATASETS =", "const DATA_FORMULAS =", "const DATA_OVERLAP =",
                "1. Triage Table (52)", "2. Candidate Reports (52)",
                "3. Splice Windows (28)", "4. Replication", 'id="rep-dag-box"', 'id="sandbox-drawer"',
                "Subunit &amp; Selectivity", "202 / 202 (100%) 64-char SHA-256",
                "Monograph &rarr;", "Dossier &rarr;", "Structured Triage Dossier",
                "Methodology &amp; Decision Guide", "GENCODE v46 Off-Target Alignment Screen", "Therapeutic Modality",
                "https://alphafold.ebi.ac.uk/entry/", "https://www.informatics.jax.org/marker/MGI:",
                "PMID:40354799", "PMID:37267913", "'EALS-016':'ENSG00000118564'", "FLAGSHIP-EALS-030",
                "resolveCandidateId", "matchCandidateQuery",
                "Secreted Decoy sST2 vs. Membrane ST2L", 'role="tabpanel"',
                "md:grid-cols-[268px_minmax(0,1fr)]",
                'id="d-aside"', 'id="d-slice-bar"', 'id="d-lens"', 'id="p-lens-bar"', 'id="contrasts-drawer"',
                'id="tab-btn-home"', 'id="view-home"', "const DATA_UPDATES =", "Living Research Log",
                "CONVENTIONAL / SINGLE-ASSAY VIEW", "MULTI-MODAL RE-ANALYSIS",
                "GO CRITERIA (ADVANCE THRESHOLDS)", "NO-GO CRITERIA (STOPPING THRESHOLDS)",
            ):
                if req_str not in htxt:
                    errors.append(f"Dossier Schema 3.0 missing verified anchor '{req_str}' in {lbl}")
            m_leg = SITE_LEGACY_ID_OR_ALIAS_RE.search(SITE_WORK_PATH_RE.sub("", htxt))
            if m_leg:
                errors.append(f"{lbl} contains residual legacy candidate ID or alias token '{m_leg.group(0)}'")
            clean_for_jargon = SITE_WORK_PATH_RE.sub("", htxt)
            if not is_public_export:
                clean_for_jargon = clean_for_jargon.replace("CARBON_ALS_INTERACTIVE_EXPLORER.html", "")
            m_jarg = SITE_INTERNAL_JARGON_RE.search(clean_for_jargon)
            if m_jarg:
                errors.append(f"{lbl} contains internal build/process nomenclature '{m_jarg.group(0)}'")

        if mode == "full":
            _audit_explorer_html(explorer_html, is_public_export=False)
        _audit_explorer_html(gh_docs / "index.html", is_public_export=True)

        exp_pilot_files = {
            f"{r['accession_id']}.html"
            for r in port_rows
            if r["scientific_actionability_tier"] in {"TIER_1_ACTIONABLE_NOW", "TIER_2_FOCUSED_GATE_FIRST"}
        }
        if mode == "full":
            if {p.name for p in mono_htmls} != exp_pilot_files:
                errors.append(f"reports/monographs/*.html set ({sorted(p.name for p in mono_htmls)}) != expected 8 EALS pages ({sorted(exp_pilot_files)})")
            if (carbon_root / "reports" / "wiki").exists():
                errors.append("Stale reports/wiki directory still exists (renamed to reports/monographs)")
            for wfp in mono_htmls:
                wtxt = wfp.read_text(encoding="utf-8")
                if not _has_valid_stamp(wtxt) or "https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js" not in wtxt:
                    errors.append(f"reports/monographs/{wfp.name} missing SHA-12 concordance stamp or allowlisted Tailwind")
                if "/100" in wtxt or "!important" in wtxt or "<style>:where(.hidden){display:none}" not in wtxt or "wiki" in wtxt.lower():
                    errors.append(f"reports/monographs/{wfp.name} contains /100, !important, or residual 'wiki' leak")
                if EXPLORE_LEAK_RE.search(wtxt) or SITE_LEGACY_ID_OR_ALIAS_RE.search(SITE_WORK_PATH_RE.sub("", wtxt)):
                    errors.append(f"reports/monographs/{wfp.name} contains ExploreALS or residual legacy ID/alias leak")
        if {p.name for p in gh_mono_htmls} != exp_pilot_files:
            errors.append(f"{gh_mono_dir.relative_to(carbon_root).as_posix()}/*.html set ({sorted(p.name for p in gh_mono_htmls)}) != expected 8 EALS pages")
        for gfp in gh_mono_htmls:
            gtxt = gfp.read_text(encoding="utf-8")
            if not _has_valid_stamp(gtxt) or "gstatic.com" in gtxt or "window.PUBLIC_WEB_EXPORT=true" not in gtxt:
                errors.append(f"{gfp.relative_to(carbon_root).as_posix()} missing SHA-12 stamp or fails zero-CDN guard")
            if "/100" in gtxt or "!important" in gtxt or "wiki" in gtxt.lower() or EXPLORE_LEAK_RE.search(gtxt) or SITE_LEGACY_ID_OR_ALIAS_RE.search(SITE_WORK_PATH_RE.sub("", gtxt)):
                errors.append(f"{gfp.relative_to(carbon_root).as_posix()} contains /100, !important, residual 'wiki', Explore->, or legacy ID/alias leak")
            m_gjarg = SITE_INTERNAL_JARGON_RE.search(SITE_WORK_PATH_RE.sub("", gtxt))
            if m_gjarg:
                errors.append(f"{gfp.relative_to(carbon_root).as_posix()} contains internal build/process nomenclature '{m_gjarg.group(0)}'")

        no_money_paths = [
            reg_dir / "phase3_execution_readiness.csv",
            reg_dir / "phase3b_denovo_candidates.csv",
            port_fp,
            *([synth_md] if synth_md.is_file() else []),
            *([explorer_html] if explorer_html.is_file() else []),
            *mono_htmls,
            *[p for p in gh_htmls if p.is_file()],
        ]
        for mfp in no_money_paths:
            if mfp.is_file():
                m_txt = mfp.read_text(encoding="utf-8").replace("PHASE3A_EXECUTION_SAFETY_AND_EVOI_TRIAGE.md", "")
                m_fin = CAPITAL_DOLLAR_LEAK_RE.search(m_txt)
                if m_fin:
                    errors.append(f"CAPITAL/DOLLAR FRAMING LEAK in {mfp.relative_to(carbon_root).as_posix()}: '{m_fin.group(0)}'")

    txt_paths = [
        port_fp, cis_fp,
        *([synth_md] if synth_md.is_file() else []),
        *([explorer_html] if explorer_html.is_file() else []),
        *mono_htmls,
        *[p for p in gh_htmls if p.is_file()],
        *[p for sub in ("cache", "outputs", "scripts") for p in sorted((p4_work / sub).rglob("*")) if p.is_file() and p.suffix.lower() in {".csv", ".md", ".json", ".py", ".html"}],
    ]
    for fp in txt_paths:
        txt = fp.read_text(encoding="utf-8", errors="ignore")
        m = RAW_OLIGO_SEQ_RE.search(txt) or GAPPED_OLIGO_RE.search(txt)
        if m:
            errors.append(f"BIOSECURITY SEQUENCE LEAK in {fp.relative_to(carbon_root).as_posix()}: '{m.group(0)[:20]}'")
    return errors
