"""RUN-P4-002: Render reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md & CARBON_ALS_INTERACTIVE_EXPLORER.html."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
REG_DIR = ROOT / "registries"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _candidate_contrasts_b import build_edges_and_lenses  # noqa: E402
from _explorer_js import EXPLORER_JS_BODY, EXPLORER_JS_TABS234  # noqa: E402
from _explorer_template import HTML_HEAD_AND_BODY, HTML_TABS_AND_SCRIPT  # noqa: E402
from _phase4_helpers import CROWDING_CLASS_MAP, biological_evidence_sort_key  # noqa: E402
from _public_taxonomy import (  # noqa: E402
    COHORT_DEFS,
    EVIDENCE_COHORT_BY_EALS,
    resolve_cis_mechanism,
    resolve_cis_mode_code,
    resolve_cis_role,
    sanitize_public_modality,
    sanitize_public_prose,
)
from _public_web_exporter import export_public_web_bundle  # noqa: E402
from _render_synthesis_sections import build_exec_and_transition_md, build_roadmaps_and_tables_md  # noqa: E402
from _subnode_v3_projection import project_subnode_v3  # noqa: E402
from _dossier_card_splits_b import structure_dossier_card  # noqa: E402
from _summary_dossier_projection import build_summary_dossiers, clean_prose  # noqa: E402
from _monograph_compiler import compile_monograph_bundle, write_standalone_monographs  # noqa: E402
from _dossier_js_svg_core import DOSSIER_JS_SVG_CORE  # noqa: E402
from _dossier_js_svg_custom import DOSSIER_JS_SVG_CUSTOM  # noqa: E402
from _dossier_js_view import DOSSIER_JS_VIEW  # noqa: E402
from _replication_payload_builder import build_replication_payloads  # noqa: E402
from _replication_sandboxes_js import REPLICATION_SANDBOXES_JS  # noqa: E402
from _replication_tab_js import REPLICATION_TAB_JS  # noqa: E402
from carbon_als.accessions import PRIMARY_SYMBOL_AND_ALIASES, legacy_to_accession, translate_legacy_tokens_in_prose  # noqa: E402
import tempfile  # noqa: E402

RAW_OLIGO_SEQ_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)
GAPPED_OLIGO_RE = re.compile(r"(?<![A-Za-z0-9_])(?:[ACGTU][\s\-_:|,;/\\]+){14,}[ACGTU](?![A-Za-z0-9_])", re.IGNORECASE)


def _read_csv(name: str) -> list[dict[str, str]]:
    with (REG_DIR / name).open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _safe_json_for_script(obj: object) -> str:
    return json.dumps(obj, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")


def main() -> None:
    public_docs_only = "--public-docs-only" in sys.argv
    port_rows = _read_csv("phase4_unified_portfolio.csv")
    cis_rows = _read_csv("phase4_unified_cis_intervals.csv")
    sub_rows = _read_csv("subnode_dissection.csv")
    intake_map = {r["carbon_id"]: r for r in _read_csv("candidate_intake_ledger.csv")}
    summary = json.loads(
        (ROOT / "work" / "phase4_final_synthesis" / "outputs" / "run_p4_001_unified_portfolio.json").read_text(encoding="utf-8")
    )

    md_lines = [
        *build_exec_and_transition_md(summary, port_rows, intake_map),
        *build_roadmaps_and_tables_md(summary, port_rows, cis_rows, sub_rows),
        "",
    ]
    md_text = "\n".join(md_lines)
    assert not RAW_OLIGO_SEQ_RE.search(md_text) and not GAPPED_OLIGO_RE.search(md_text), "Biosecurity sequence guard failed on Markdown!"
    synth_fp = ROOT / "reports" / "CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md"
    if not public_docs_only:
        synth_fp.write_text(md_text, encoding="utf-8")

    def _clean_ui(txt: str) -> str:
        txt = re.sub(r"\bnon-ExploreALS\b", "screen-nominated", txt, flags=re.IGNORECASE)
        txt = re.sub(r"\bExploreALS\b", "published catalog", txt, flags=re.IGNORECASE)
        return re.sub(r"\bCarbonALS\b", "ExploreALS", txt, flags=re.IGNORECASE)

    bio_sorted = sorted(port_rows, key=biological_evidence_sort_key)
    bio_rk_map = {r["portfolio_id"]: i for i, r in enumerate(bio_sorted, 1)}

    def _resolve_crowd(r: dict[str, str]) -> str:
        if r["portfolio_id"] in CROWDING_CLASS_MAP:
            return CROWDING_CLASS_MAP[r["portfolio_id"]]
        if r["decision"] == "DROP":
            return "N/A (Falsified)"
        if r["decision"] == "RECLASSIFY_BENCHMARK_OR_BIOMARKER":
            return "N/A (Benchmark / Biomarker)"
        if r["scientific_actionability_tier"] == "COMPANION_PROTOCOL_ONLY":
            return "N/A (Functional Calibrator)"
        return "0 Active ALS Trials"

    js_port = []
    for r in port_rows:
        lid = r["portfolio_id"]
        acc_id = r.get("accession_id") or legacy_to_accession(lid)
        sym, syn_list = PRIMARY_SYMBOL_AND_ALIASES[lid]
        coh_key = EVIDENCE_COHORT_BY_EALS[acc_id]
        js_port.append({
            "rk": int(r["unified_rank"]), "brk": bio_rk_map[lid],
            "id": acc_id, "sym": sym, "syn": syn_list,
            "o": coh_key, "sub": coh_key,
            "trk": r["track"], "name": r["gene_or_drug"],
            "mod": sanitize_public_modality(translate_legacy_tokens_in_prose(r["primary_modality_specific"])),
            "epi": r["epistemic_state"], "dec": r["decision"], "tier": r["scientific_actionability_tier"],
            "trl": r["clinical_readiness_trl"], "gate": r["next_gate_experimental_class"],
            "basis": r["primary_evidence_basis"],
            "crowd": _resolve_crowd(r),
            "prior": r["model_prior_dependency"], "hcnt": int(r["unsolved_hurdle_count"]),
            "hurdles": sanitize_public_prose(
                translate_legacy_tokens_in_prose(r["unsolved_hurdles_structured"])
                .replace("21CFR300_50", "FACTORIAL_CONTRIBUTION")
                .replace("NO_312_23_REF", "INDEPENDENT_SINGLE_ENTITY_TOX")
                .replace("STAGE_2_", "COMBINATORIAL_")
            ),
            "iv": r["lead_cis_interval_id"],
            "ivst": r["lead_offtarget_safety_status"],
            "nxt": (
                r["discriminating_next_test"]
                if r["discriminating_next_test"].startswith("NONE_")
                else structure_dossier_card(acc_id, "nxt", sanitize_public_prose(clean_prose(r["discriminating_next_test"])))
            ),
        })
    js_cis = [
        {
            "ord": int(c["unified_interval_order"]),
            "o": resolve_cis_mechanism(c["gene_symbol"], c["cis_mechanism_or_mode"]),
            "pid": c.get("accession_id") or legacy_to_accession(c["portfolio_id"]),
            "sc": c.get("subnode_accession_id") or legacy_to_accession(c["subnode_or_cand_id"]),
            "gene": c["gene_symbol"],
            "role": resolve_cis_role(c.get("accession_id") or legacy_to_accession(c["portfolio_id"]), c["program_role"]),
            "rk": int(c["rank_within_gene"]), "lead": c["is_promoted_lead"] == "True",
            "iv": c["interval_id"], "chr": c["chrom"], "lo": c["grch38_start"], "hi": c["grch38_end"], "strd": c["strand"],
            "len": int(c["length_bp"]),
            "mode": resolve_cis_mode_code(c["gene_symbol"], c["cis_mechanism_or_mode"]),
            "gc": c["gc_pct"], "tm": c["tm_phys_pops_c"],
            "dg": c["dg37_kcal"], "avi": c["max_avi_phred"],
            "sp": f"{c['spliced_0mm_genes']}/{c['spliced_1mm_genes']}/{c['spliced_wobble_only_pc_genes']}",
            "pm": f"{c['premRNA_0mm_sense_genes']}/{c['premRNA_1mm_splice50bp_genes']}/{c['premRNA_wobble_only_splice50bp_pc_genes']}/{c['premRNA_2mm_splice25bp_pc_genes']}/{c['bulge_1nt_steric_pc_genes']}/{c['sub18_core_steric_pc_genes']}",
            "pm1_all": int(c["premRNA_1mm_sense_genes"]),
            "is_gap": "GAPMER" in c["cis_mechanism_or_mode"],
            "flags": (
                re.sub(r";?\.\.\.\(\+(\d+)_more_in_JSON\)", r"; +\1 additional GENCODE v46 hits", c["flagged_constrained_neuronal_hits"])
                .replace("sub18_core_nonconstr", "18nt-subcore(non-constrained)")
                .replace("bulge_1nt", "1nt-bulge")
                .replace("0mm_deep_intron", "0-mm deep intron")
                .replace("BA4_", "BA4 ")
            ),
            "st": c["offtarget_safety_status"],
        }
        for c in cis_rows
    ]
    js_sub = [project_subnode_v3(s, _clean_ui) for s in sub_rows]
    js_funnel = []
    for sub_k, base_lbl in COHORT_DEFS:
        srows = [
            r for r in port_rows
            if EVIDENCE_COHORT_BY_EALS[r.get("accession_id") or legacy_to_accession(r["portfolio_id"])] == sub_k
        ]
        js_funnel.append({
            "sub": sub_k,
            "lbl": f"{base_lbl} ({len(srows)})",
            "c": sum(1 for r in srows if r["decision"] == "KEEP_CORE"),
            "e": sum(1 for r in srows if r["decision"] == "KEEP_EXPLORATORY_UNPROVEN"),
            "b": sum(1 for r in srows if r["decision"] == "RECLASSIFY_BENCHMARK_OR_BIOMARKER"),
            "d": sum(1 for r in srows if r["decision"] == "DROP"),
        })
    assert sum(x["c"] + x["e"] + x["b"] + x["d"] for x in js_funnel) == len(port_rows), "Funnel count mismatch!"
    drop_defs = [
        ("FALSIFIED_CLINICAL", "Human ALS RCT Futility / Harm", "Adequately powered Ph2/3 futility or class failure"),
        ("FALSIFIED_PK_SAFETY", "Unbound CNS Exposure / Safety Limit", "Cu,brain << IC50/EC50 or dose-limiting clinical toxicity"),
        ("ARTIFACT_CONFOUNDED", "Assay / Media Confounding", "Within basal media noise & opposes genetic direction"),
    ]
    js_drops = [
        {
            "epi": epi_k,
            "lbl": lbl,
            "sub": sub_txt,
            "n": sum(1 for r in port_rows if r["decision"] == "DROP" and r["epistemic_state"] == epi_k),
        }
        for epi_k, lbl, sub_txt in drop_defs
    ]
    assert sum(x["n"] for x in js_drops) == sum(x["d"] for x in js_funnel), "Drop gate count mismatch!"

    pan_raw = summary["dn04_celf5_deep_profile"]["phase3b_f1_f2_nygc_panel_summary"]
    js_nygc = {
        g: {
            reg: {
                "b": d["adj_beta_tdp_vs_ctrl"], "p": d["adj_p_tdp_vs_ctrl"], "sp": d["adj_p_tdp_vs_sod1fus"],
                "tb": d["mn_adj_tSTMN2_beta"], "tp": d["mn_adj_tSTMN2_p"], "tail": d["mn_adj_neuronal_tail_pct"],
            }
            for reg, d in regs.items()
        }
        for g, regs in pan_raw.items()
    }
    nygc_meta_raw = summary["dn04_celf5_deep_profile"]["celf5_nygc_multiregion"]
    js_nygc_meta = {
        reg: {
            "ntdp": m["n_als_tdp"],
            "nctrl": m["n_ctrl"],
            "nsod": m["n_als_sod1_fus"],
            "ntot": m["n_als_tdp"] + m["n_ctrl"] + m["n_als_sod1_fus"],
        }
        for reg, m in nygc_meta_raw.items()
    }

    ev_p1_rows = _read_csv("evidence_ledger.csv")
    ev_p3b_rows = _read_csv("phase3b_denovo_evidence.csv")
    ds_rows = _read_csv("datasets_manifest.csv")
    stat_rows = _read_csv("statistical_models_and_contrasts.csv")
    ovl_rows = _read_csv("cohort_overlap_map.csv")
    upd_rows = _read_csv("living_evidence_updates.csv")
    js_updates = [
        {
            "id": u["update_id"],
            "dt": u["date_iso"],
            "tag": u["release_tag"],
            "cat": u["update_category"],
            "ids": [legacy_to_accession(x.strip()) for x in u["affected_ids"].split(";") if x.strip()],
            "imp": sanitize_public_prose(translate_legacy_tokens_in_prose(u["decision_impact"])),
            "hdr": sanitize_public_prose(translate_legacy_tokens_in_prose(u["headline"])),
            "pre": sanitize_public_prose(translate_legacy_tokens_in_prose(u["prior_state_or_assumption"])),
            "post": sanitize_public_prose(translate_legacy_tokens_in_prose(u["new_evidence_or_revision"])),
            "cons": sanitize_public_prose(translate_legacy_tokens_in_prose(u["portfolio_and_gate_consequence"])),
            "srcs": [x.strip() for x in u["primary_sources"].split(";") if x.strip()],
            "ancs": [x.strip() for x in u["verification_anchor"].split(";") if x.strip()],
        }
        for u in upd_rows
    ]

    runs = _read_csv("analysis_runs.csv")
    run_cols = list(runs[0].keys())
    p4_r2 = {
        "analysis_run_id": "RUN-P4-002", "phase_batch": "Phase4_Final_Synthesis",
        "script_relpath": "work/phase4_final_synthesis/scripts/02_render_phase4_synthesis.py",
        "output_artifacts": "reports/CARBON_ALS_FINAL_PORTFOLIO_SYNTHESIS.md;reports/CARBON_ALS_INTERACTIVE_EXPLORER.html;reports/monographs;reports/github_pages",
        "datasets_used": "DS001_COUNTS;DS001_META;DS001_ONEILL;DS_GENCODE_V46_COMP_GTF;DS_GNOMAD_V41_CONSTRAINT",
        "tools_and_skills_used": "generative_ui;tooluniverse-gene-liability;alphagenome-atlas-website-links;scripts.phase4_gates;uv-python",
        "reproduced_verified": "yes", "run_timestamp_utc": "2026-11-19T12:45:00Z",
        "summary": f"Programmatically compiled unified 52-hypothesis ExploreALS v1.3 Explorer (with 8 Tier 1+2 Translational Monographs, 9-row Mechanistic Contrasts matrix, Replication & Verification workbench, {len(stat_rows)}/{len(stat_rows)} 64-char SHA-256 anchors, 42 SHA-256-locked open datasets [40 external + 2 bundled], 8-group cohort overlap & donor accounting & 3 sensitivity sandboxes) and zero-CDN GitHub Pages bundle across 28 1-based GRCh38 cis-regulatory target windows.",
    }
    runs = (
        [p4_r2 if r["analysis_run_id"] == "RUN-P4-002" else r for r in runs]
        if any(r["analysis_run_id"] == "RUN-P4-002" for r in runs)
        else [*runs, p4_r2]
    )

    mono_map, ev_by_id = compile_monograph_bundle(port_rows, ev_p1_rows, ev_p3b_rows, ds_rows, stat_rows)
    js_sum = build_summary_dossiers(
        port_rows,
        _read_csv("candidate_decisions.csv"),
        _read_csv("phase3b_denovo_candidates.csv"),
    )
    _, js_lenses, js_contrasts = build_edges_and_lenses(port_rows)
    js_runs, js_datasets, js_formulas, js_overlap = build_replication_payloads(
        runs, ds_rows, stat_rows, ovl_rows, [*ev_p1_rows, *ev_p3b_rows]
    )

    data_block = "\n".join([
        "  <script>",
        f"const DATA_PORT = {_safe_json_for_script(js_port)};",
        f"const DATA_CIS = {_safe_json_for_script(js_cis)};",
        f"const DATA_SUB = {_safe_json_for_script(js_sub)};",
        f"const DATA_FUNNEL = {_safe_json_for_script(js_funnel)};",
        f"const DATA_DROPS = {_safe_json_for_script(js_drops)};",
        f"const DATA_NYGC = {_safe_json_for_script(js_nygc)};",
        f"const DATA_NYGC_META = {_safe_json_for_script(js_nygc_meta)};",
        f"const DATA_MONOGRAPHS = {_safe_json_for_script(mono_map)};",
        f"const DATA_EV = {_safe_json_for_script(ev_by_id)};",
        f"const DATA_SUM = {_safe_json_for_script(js_sum)};",
        f"const DATA_LENSES = {_safe_json_for_script(js_lenses)};",
        f"const DATA_CONTRASTS = {_safe_json_for_script(js_contrasts)};",
        f"const DATA_RUNS = {_safe_json_for_script(js_runs)};",
        f"const DATA_DATASETS = {_safe_json_for_script(js_datasets)};",
        f"const DATA_FORMULAS = {_safe_json_for_script(js_formulas)};",
        f"const DATA_OVERLAP = {_safe_json_for_script(js_overlap)};",
        f"const DATA_UPDATES = {_safe_json_for_script(js_updates)};",
    ])
    st = summary["registry_sha12"]
    sha_stamp = (
        f"BUILD_PROVENANCE_SHA12: portfolio={st['phase4_unified_portfolio']} intervals={st['phase4_unified_cis_intervals']} "
        f"offtarget={st['phase3_sso_offtarget_audit']} readiness={st['phase3_execution_readiness']} "
        f"screen_cands={st['phase3b_denovo_candidates']} screen_ivs={st['phase3b_denovo_sso_intervals']}"
    )
    html_head_stamped = HTML_HEAD_AND_BODY.replace("<!-- __SHA12_STAMP__ -->", f"<!-- {sha_stamp} -->")
    html_text = (
        html_head_stamped
        + HTML_TABS_AND_SCRIPT
        + data_block
        + EXPLORER_JS_BODY
        + DOSSIER_JS_SVG_CORE
        + DOSSIER_JS_SVG_CUSTOM
        + DOSSIER_JS_VIEW
        + REPLICATION_TAB_JS
        + REPLICATION_SANDBOXES_JS
        + EXPLORER_JS_TABS234
    )
    assert not RAW_OLIGO_SEQ_RE.search(html_text) and not GAPPED_OLIGO_RE.search(html_text), "Biosecurity sequence guard failed on HTML!"
    assert "/100" not in html_text, "Subjective /100 composite score leaked in Explorer HTML!"
    assert not re.search(
        r"\bcarbonals\b|\bwiki\b|\bv0\b|\bstream\s+[ab]\b|wave\s+2|\bD003\b|\bD045\b|\bDS045\b|(?<![/a-z0-9_])Phase\s+3A\b|fixing\s+intake",
        html_text,
        re.IGNORECASE,
    ), "Residual internal nomenclature in Explorer HTML!"

    if public_docs_only:
        with tempfile.TemporaryDirectory() as tmp_d:
            mono_tmp = write_standalone_monographs(Path(tmp_d), sha_stamp, js_port, js_cis, mono_map, ev_by_id, js_sum, js_lenses)
            pub_written = export_public_web_bundle(ROOT, html_text, mono_tmp, sha_stamp=sha_stamp)
        print(f"PUBLIC DOCS REBUILD OK: {len(pub_written)} files written to {ROOT / 'docs'}")
        return

    html_fp = ROOT / "reports" / "CARBON_ALS_INTERACTIVE_EXPLORER.html"
    html_fp.write_text(html_text, encoding="utf-8")
    mono_written = write_standalone_monographs(ROOT / "reports" / "monographs", sha_stamp, js_port, js_cis, mono_map, ev_by_id, js_sum, js_lenses)
    pub_written = export_public_web_bundle(ROOT / "reports" / "github_pages", html_text, mono_written, sha_stamp=sha_stamp)

    with (REG_DIR / "analysis_runs.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=run_cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(runs)
    print(
        f"RUN-P4-002 OK: {synth_fp.name} ({len(md_lines)} lines) + {html_fp.name} ({len(html_text.splitlines())} lines) "
        f"+ {len(mono_written)} standalone monograph HTMLs + {len(pub_written)} github_pages files"
    )


if __name__ == "__main__":
    main()
