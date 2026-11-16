"""Hardened Phase 4 cross-phase portfolio (59), cis-interval (26), dossier-sync, JSON, & biosecurity validators."""
from __future__ import annotations

import json
from pathlib import Path
import re

from phase3_gates import ALLOWED_OFFTARGET_STATUS, ALLOWED_TRL, MODEL_PRIOR_RE, RAW_OLIGO_SEQ_RE, _reject_nan_const, _sha12
from phase3b_gates import ALLOWED_P3B_BASIS, ALLOWED_P3B_DEC, ALLOWED_P3B_EPI, ALLOWED_P3B_GATE, ALLOWED_P3B_TIER, FALSIFIED_P3B, GAPPED_OLIGO_RE

EXPLORE_LEAK_RE = re.compile(r"explore\s*->|\bcarbonals\b|0/4\s+explore", re.IGNORECASE)
CAPITAL_DOLLAR_LEAK_RE = re.compile(
    r"(\$\s*\d|\bUSD\b|\bcapital\w*|\bdollar\w*|do[\s_-]*not[\s_-]*fund|\bfund(?:ing|ed)\b|"
    r"\bcheap\w*|\bexpensive\w*|\bbudget\w*|\bevoi\b|cost_horizon|MODERATE_COST)",
    re.IGNORECASE,
)

EXP_PORT_COLS = (
    "unified_rank,portfolio_id,origin_phase,origin_subcohort,track,gene_or_drug,candidate_type,primary_modality_specific,"
    "epistemic_state,decision,scientific_actionability_tier,clinical_readiness_trl,next_gate_experimental_class,"
    "primary_evidence_basis,model_prior_dependency,unsolved_hurdle_count,unsolved_hurdles_structured,"
    "lead_cis_interval_id,lead_offtarget_safety_status,key_quantitative_anchor,discriminating_next_test,"
    "source_registry_ref,analysis_run_id"
).split(",")

EXP_CIS_COLS = (
    "unified_interval_order,origin_phase,portfolio_id,subnode_or_cand_id,gene_symbol,program_role,rank_within_gene,"
    "is_promoted_lead,interval_id,chrom,grch38_start,grch38_end,strand,length_bp,cis_mechanism_or_mode,gc_pct,"
    "tm_phys_pops_c,dg37_kcal,cpg_dinucs,max_self_stem_bp,ese_motifs,mean_avi_phred,max_avi_phred,boundary_dist_bp,"
    "composite_score,spliced_0mm_genes,spliced_1mm_genes,spliced_2mm_pc_genes,spliced_wobble_only_pc_genes,"
    "premRNA_0mm_sense_genes,premRNA_1mm_sense_genes,premRNA_1mm_splice50bp_genes,premRNA_wobble_only_splice50bp_pc_genes,"
    "premRNA_2mm_splice25bp_pc_genes,bulge_1nt_steric_pc_genes,sub18_core_steric_pc_genes,"
    "flagged_constrained_neuronal_hits,offtarget_safety_status,source_offtarget_run_id,analysis_run_id"
).split(",")


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
    port_fp = reg_dir / "phase4_unified_portfolio.csv"
    cis_fp = reg_dir / "phase4_unified_cis_intervals.csv"
    celf_fp = carbon_root / "work" / "phase4_final_synthesis" / "cache" / "celf5_target_profile.json"
    out_fp = carbon_root / "work" / "phase4_final_synthesis" / "outputs" / "run_p4_001_unified_portfolio.json"

    for fp in (port_fp, cis_fp, celf_fp, out_fp):
        if not fp.is_file():
            errors.append(f"Missing mandatory Phase 4 artifact: {fp.relative_to(carbon_root).as_posix()}")
    if errors:
        return errors

    port_rows = port_override if port_override is not None else load_csv_fn("phase4_unified_portfolio.csv")
    cis_rows = load_csv_fn("phase4_unified_cis_intervals.csv")
    if port_rows and list(port_rows[0].keys()) != EXP_PORT_COLS:
        errors.append("Schema header mismatch in phase4_unified_portfolio.csv")
    if cis_rows and list(cis_rows[0].keys()) != EXP_CIS_COLS:
        errors.append("Schema header mismatch in phase4_unified_cis_intervals.csv")

    dec_map = {r["carbon_id"]: r for r in decisions}
    rd_map = {r["candidate_id"]: r for r in load_csv_fn("phase3_execution_readiness.csv")}
    p3b_map = {r["denovo_id"]: r for r in load_csv_fn("phase3b_denovo_candidates.csv")}
    p2_map = {r["interval_id"]: r for r in load_csv_fn("phase2_multiplex_intervals.csv")}
    ot3a_map = {r["interval_id"]: r for r in load_csv_fn("phase3_sso_offtarget_audit.csv")}
    sso3b_map = {r["interval_id"]: r for r in load_csv_fn("phase3b_denovo_sso_intervals.csv")}

    exp_pids = set(dec_map) | set(p3b_map)
    got_pids = [r["portfolio_id"] for r in port_rows]
    if len(got_pids) != len(set(got_pids)) or set(got_pids) != exp_pids:
        errors.append(f"phase4_unified_portfolio.csv portfolio_id set ({len(got_pids)}) != disjoint union of 40 ExploreALS + 19 Phase 3B ({len(exp_pids)})")
    if sorted(int(r["unified_rank"]) for r in port_rows) != list(range(1, len(port_rows) + 1)):
        errors.append("phase4_unified_portfolio.csv unified_rank is not contiguous 1..59")

    exp_ivs = set(ot3a_map) | set(sso3b_map)
    got_ivs = [r["interval_id"] for r in cis_rows]
    if len(got_ivs) != len(set(got_ivs)) or set(got_ivs) != exp_ivs:
        errors.append(f"phase4_unified_cis_intervals.csv interval_id set ({len(got_ivs)}) != union of 12 Phase 3A + 14 Phase 3B ({len(exp_ivs)})")
    if sorted(int(r["unified_interval_order"]) for r in cis_rows) != list(range(1, len(cis_rows) + 1)):
        errors.append("phase4_unified_cis_intervals.csv unified_interval_order is not contiguous 1..26")

    leads_from_cis: dict[str, tuple[str, str]] = {}
    for c in cis_rows:
        iv_id = c["interval_id"]
        src_ot = ot3a_map.get(iv_id) or sso3b_map.get(iv_id)
        src_bio = p2_map.get(iv_id) if c["origin_phase"] == "PHASE2_3A_MULTIPLEX_12" else sso3b_map.get(iv_id)
        if src_ot is None or src_bio is None:
            errors.append(f"{iv_id}: missing source biophysical/offtarget row")
        else:
            for k_bio in EXP_CIS_COLS[15:25]:
                if c[k_bio] != src_bio[k_bio]:
                    errors.append(f"{iv_id}: Phase 4 {k_bio}='{c[k_bio]}' != source '{src_bio[k_bio]}'")
            for k_ot in EXP_CIS_COLS[25:38]:
                if c[k_ot] != src_ot[k_ot]:
                    errors.append(f"{iv_id}: Phase 4 {k_ot}='{c[k_ot]}' != source '{src_ot[k_ot]}'")
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
                if f"unified_rank = #{r['unified_rank']}/59" not in md_txt or f"scientific_actionability_tier = {r['scientific_actionability_tier']}" not in md_txt:
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
                if st.get("phase4_unified_portfolio") != _sha12(port_fp) or st.get("phase4_unified_cis_intervals") != _sha12(cis_fp):
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
        exp_stamp = (
            f"REGISTRY_CONCORDANCE_SHA12: p4_port={_sha12(port_fp)} p4_cis={_sha12(cis_fp)} "
            f"p3a_ot={_sha12(reg_dir / 'phase3_sso_offtarget_audit.csv')} p3a_rd={_sha12(reg_dir / 'phase3_execution_readiness.csv')} "
            f"p3b_cand={_sha12(reg_dir / 'phase3b_denovo_candidates.csv')} p3b_sso={_sha12(reg_dir / 'phase3b_denovo_sso_intervals.csv')}"
        )
        if mode == "full" and synth_md.is_file():
            stxt = synth_md.read_text(encoding="utf-8")
            if exp_stamp not in stxt:
                errors.append("reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md missing or stale REGISTRY_CONCORDANCE_SHA12 stamp")
            if "PMID:40354799" not in stxt or "PMID:40349716" in stxt or re.search(r"\bDS045\b", stxt):
                errors.append("reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md has stale MIROCALS PMID or DS045 shorthand")
            if "miss 60%–75% of top-quintile" in stxt or "in `rs12608932 A/A`" in stxt or "in rs12608932 A/A" in stxt:
                errors.append("reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md has stale v1.0 MS-NEFH responder or binary rs12608932 A/A prose")

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
            if exp_stamp not in htxt:
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
                "CHEMBL1201587", "ENST00000404917", "L_eff 65 -> 8", "LOEUF = 1.413", "LOEUF=0.295",
                "LOEUF=0.389", "LOEUF=0.250", "96 bp upstream of rs12973192",
                "Responsive Step Cards", "Native Wrap", "Honest Multi-Cohort", "Explore -> Carbon",
                "CarbonALS", "Candidate Wiki", "(9 v3)", "Queued for Wave 2", "WAVE 2 REGISTRY",
                "Stream A", "Stream B", "5D liability=", "gene-liability=", "/100",
                "Figure 1", "Figure 2", "Figure 3", "Figure 4", "5. Primary Evidence",
                "1. Right Target", "3. Right Modality",
                "Translational Dossier Schema 3.0", "<footer", "more_in_JSON", "Quantitative Anchor:",
                "PMID:40349716", "PMID:37264228", "PMID:35197629", "D003", "D045", "Phase 3A",
                "fixing intake", "prior intake", "Cytosolic vs. ER",
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
            ):
                if banned in htxt:
                    errors.append(f"Dossier Schema 3.0 regression in {lbl}: found banned string '{banned}'")
            for req_str in (
                "ExploreALS v1.2", "Ricardo Agoga", "helloimra@proton.me", "github.com/helloimra/ExploreALS",
                "Not Medical Advice", "AI-Assisted Methodology",
                "Sort: Portfolio Actionability Rank", "Sort: Pure Biological Evidence",
                "Human RCT / Genetics", "Human Cohort / PK-PD",
                "In Vitro or Small-N", "Model / Heuristic Prior", "BioVendor",
                "0 chemically modified synthesis-ready ASO sequences",
                "PDB 4M7N", "NIH GTEx (v8 / v10)", "N/A (SOC / PD Benchmark)", "Rank &amp; Triage Key:", "Design Tiers:",
                "CHEMBL1201438", "ENST00000311734.6", "102343269-102346100(+)", "LOEUF = 1.143",
                "LOEUF = 0.258", "LOEUF = 0.344", "LOEUF = 0.261", "107 bp upstream of rs12973192",
                "Primary Evidence &amp; FAIR Provenance Ledger", "Right Target", "Right Modality & Exposure",
                "const DATA_NYGC_META =", "const DATA_FUNNEL =", "const DATA_DROPS =", "const DATA_SUM =",
                "const DATA_LENSES =", "const DATA_CONTRASTS =",
                "const DATA_RUNS =", "const DATA_DATASETS =", "const DATA_FORMULAS =", "const DATA_OVERLAP =",
                "4. Funnel &amp; Cohorts", "5. Dossiers (59)", "6. Replication", 'id="rep-dag-box"', 'id="sandbox-drawer"',
                "Monograph &rarr;", "Summary &rarr;", "Summary-of-Findings Dossier",
                "Methodology &amp; Decision Guide", "OTS Coordinate &amp; Hybridization Standard", "Target Modality (TPP)",
                "https://alphafold.ebi.ac.uk/entry/", "https://www.informatics.jax.org/marker/MGI:",
                "PMID:40354799", "PMID:37267913", "C016:'ENSG00000118564'",
                "Secreted Decoy sST2 vs. Membrane ST2L", 'role="tabpanel"',
                "md:grid-cols-[228px_minmax(0,1fr)]",
                'id="d-aside"', 'id="d-slice-bar"', 'id="d-lens"', 'id="p-lens-bar"', 'id="contrasts-drawer"',
                "ADVANCE GATE (GO CRITERIA)", "FALSIFICATION GATE (KILL / NO-GO CRITERIA)",
            ):
                if req_str not in htxt:
                    errors.append(f"Dossier Schema 3.0 missing verified anchor '{req_str}' in {lbl}")

        if mode == "full":
            _audit_explorer_html(explorer_html, is_public_export=False)
        _audit_explorer_html(gh_docs / "index.html", is_public_export=True)

        exp_pilot_files = {
            f"{r['portfolio_id']}.html"
            for r in port_rows
            if r["scientific_actionability_tier"] in {"TIER_1_ACTIONABLE_NOW", "TIER_2_FOCUSED_GATE_FIRST"}
        }
        if mode == "full":
            if {p.name for p in mono_htmls} != exp_pilot_files:
                errors.append(f"reports/monographs/*.html set ({sorted(p.name for p in mono_htmls)}) != expected {len(exp_pilot_files)} Tier 1+2 pilot pages ({sorted(exp_pilot_files)})")
            if (carbon_root / "reports" / "wiki").exists():
                errors.append("Stale reports/wiki directory still exists (renamed to reports/monographs)")
            for wfp in mono_htmls:
                wtxt = wfp.read_text(encoding="utf-8")
                if exp_stamp not in wtxt or "https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js" not in wtxt:
                    errors.append(f"reports/monographs/{wfp.name} missing SHA-12 concordance stamp or allowlisted Tailwind")
                if "/100" in wtxt or "!important" in wtxt or "<style>:where(.hidden){display:none}" not in wtxt or "wiki" in wtxt.lower():
                    errors.append(f"reports/monographs/{wfp.name} contains /100, !important, or residual 'wiki' leak")
                if EXPLORE_LEAK_RE.search(wtxt):
                    errors.append(f"reports/monographs/{wfp.name} contains ExploreALS / Explore-> leak outside Tab 4 audit panel")
        if {p.name for p in gh_mono_htmls} != exp_pilot_files:
            errors.append(f"{gh_mono_dir.relative_to(carbon_root).as_posix()}/*.html set ({sorted(p.name for p in gh_mono_htmls)}) != expected {len(exp_pilot_files)} Tier 1+2 pilot pages")
        for gfp in gh_mono_htmls:
            gtxt = gfp.read_text(encoding="utf-8")
            if exp_stamp not in gtxt or "gstatic.com" in gtxt or "window.PUBLIC_WEB_EXPORT=true" not in gtxt:
                errors.append(f"{gfp.relative_to(carbon_root).as_posix()} missing SHA-12 stamp or fails zero-CDN guard")
            if "/100" in gtxt or "!important" in gtxt or "wiki" in gtxt.lower() or EXPLORE_LEAK_RE.search(gtxt):
                errors.append(f"{gfp.relative_to(carbon_root).as_posix()} contains /100, !important, residual 'wiki', or Explore-> leak")

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
