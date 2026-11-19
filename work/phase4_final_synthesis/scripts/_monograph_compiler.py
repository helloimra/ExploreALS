"""Compile verified Dossier Standard v3 Monograph payloads (8 Tier-1/2 leads + 59-candidate FAIR evidence map) & emit standalone reports/monographs/*.html."""
from __future__ import annotations

import json
from pathlib import Path
import re

from _dossier_js_svg_core import DOSSIER_JS_SVG_CORE
from _dossier_js_svg_custom import DOSSIER_JS_SVG_CUSTOM
from _dossier_js_view import DOSSIER_JS_VIEW
from _monograph_specs_t1 import MONOGRAPH_SPECS_T1
from _monograph_specs_t2a import MONOGRAPH_SPECS_T2A
from _monograph_specs_t2b import MONOGRAPH_SPECS_T2B
from _dossier_provenance_resolver import resolve_evidence_row
from _public_taxonomy import sanitize_public_tree
from carbon_als.accessions import legacy_to_accession, translate_legacy_tokens_in_prose

RAW_OLIGO_SEQ_RE = re.compile(r"(?<![A-Za-z0-9_])[ACGTU]{15,}(?![A-Za-z0-9_])", re.IGNORECASE)
GAPPED_OLIGO_RE = re.compile(r"(?<![A-Za-z0-9_])(?:[ACGTU][\s\-_:|,;/\\]+){14,}[ACGTU](?![A-Za-z0-9_])", re.IGNORECASE)
EXPLORE_LEAK_RE = re.compile(r"explore\s*->|\bcarbonals\b|0/4\s+explore", re.IGNORECASE)


def _safe_json(obj: object) -> str:
    return json.dumps(obj, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")


def _translate_spec_obj(obj: object) -> object:
    if isinstance(obj, str):
        return translate_legacy_tokens_in_prose(obj)
    if isinstance(obj, list):
        return [_translate_spec_obj(x) for x in obj]
    if isinstance(obj, tuple):
        return tuple(_translate_spec_obj(x) for x in obj)
    if isinstance(obj, dict):
        return {
            k: ([legacy_to_accession(str(v)) for v in val] if k == "related" and isinstance(val, list) else _translate_spec_obj(val))
            for k, val in obj.items()
        }
    return obj


def compile_monograph_bundle(
    port_rows: list[dict[str, str]],
    ev_p1_rows: list[dict[str, str]],
    ev_p3b_rows: list[dict[str, str]],
    ds_rows: list[dict[str, str]],
    stat_rows: list[dict[str, str]] | None = None,
) -> tuple[dict[str, dict], dict[str, list[dict[str, str]]]]:
    raw_mono = {**MONOGRAPH_SPECS_T1, **MONOGRAPH_SPECS_T2A, **MONOGRAPH_SPECS_T2B}
    mono_map: dict[str, dict] = {
        legacy_to_accession(k): sanitize_public_tree(_translate_spec_obj(v))  # type: ignore[misc]
        for k, v in raw_mono.items()
    }
    valid_ids = {r.get("accession_id") or legacy_to_accession(r["portfolio_id"]) for r in port_rows}
    exp_pilot = {
        r.get("accession_id") or legacy_to_accession(r["portfolio_id"])
        for r in port_rows
        if r["scientific_actionability_tier"] in {"TIER_1_ACTIONABLE_NOW", "TIER_2_FOCUSED_GATE_FIRST"}
    }
    assert set(mono_map) == exp_pilot, f"Monograph IDs {set(mono_map)} != Tier 1+2 {exp_pilot}"
    for cid, spec in mono_map.items():
        for rel in spec["related"]:
            assert rel in valid_ids, f"{cid}: unknown related ID {rel}"
        spec_blob = json.dumps(spec)
        assert not EXPLORE_LEAK_RE.search(spec_blob), f"{cid}: ExploreALS leak in pilot spec!"
        assert not re.search(r"\bD003\b|\bD045\b|\bDS045\b|Phase\s*3A|RUN-P2-", spec_blob, re.I), f"{cid}: internal code in pilot spec!"

    ds_map = {d["dataset_id"]: d for d in ds_rows}
    stat_map = {s["evidence_id"]: s for s in (stat_rows or [])}
    ev_by_id: dict[str, list[dict[str, str]]] = {
        (r.get("accession_id") or legacy_to_accession(r["portfolio_id"])): []
        for r in port_rows
    }
    for row in [*ev_p1_rows, *ev_p3b_rows]:
        if row["evidence_id"] == "EV-P3A-004":
            continue
        cid = legacy_to_accession(row["carbon_id"])
        if cid not in ev_by_id:
            continue
        resolved = sanitize_public_tree({
            rk: (translate_legacy_tokens_in_prose(rv) if isinstance(rv, str) else rv)
            for rk, rv in resolve_evidence_row(row, ds_map, stat_map).items()
        })  # type: ignore[assignment]
        res_blob = json.dumps(resolved)
        assert not EXPLORE_LEAK_RE.search(res_blob), f"{cid} {row['evidence_id']}: ExploreALS leak in resolved row!"
        assert "/100" not in res_blob, f"{cid} {row['evidence_id']}: /100 score leaked in resolved row: {res_blob}"
        assert not re.search(r"\bD003\b|\bD045\b|\bDS045\b|Phase\s*3A|intake|typo", res_blob, re.I), (
            f"{cid} {row['evidence_id']}: internal code leaked in resolved row: {res_blob}"
        )
        ev_by_id[cid].append(resolved)
    return mono_map, ev_by_id


def write_standalone_monographs(
    mono_dir: Path,
    sha_stamp: str,
    js_port: list[dict],
    js_cis: list[dict],
    mono_map: dict[str, dict],
    ev_by_id: dict[str, list[dict[str, str]]],
    js_sum: dict[str, dict[str, str]],
    js_lenses: list[dict],
) -> list[Path]:
    mono_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    port_by_id = {r["id"]: r for r in js_port}
    pilot_ids = ["EALS-030", "EALS-031", "EALS-001", "EALS-006", "EALS-002", "EALS-007", "EALS-034", "EALS-037"]
    keep_stems = set(pilot_ids)
    for stale_fp in mono_dir.glob("*.html"):
        if stale_fp.stem not in keep_stems:
            stale_fp.unlink()
    standalone_ev_ids = sorted(set(pilot_ids) | {rel for k in pilot_ids for rel in mono_map[k]["related"]})

    for idx, cid in enumerate(pilot_ids):
        r = port_by_id[cid]
        prev_cid = pilot_ids[(idx - 1) % len(pilot_ids)]
        next_cid = pilot_ids[(idx + 1) % len(pilot_ids)]
        page = "\n".join([
            "<!DOCTYPE html>",
            f"<!-- {sha_stamp} -->",
            '<html lang="en"><head><meta charset="UTF-8" />',
            f"<title>ExploreALS Monograph — #{r['rk']} {r['name']} ({cid})</title>",
            "<style>:where(.hidden){display:none}table{border-collapse:collapse;width:100%}th,td{padding:6px 8px;vertical-align:top}</style>",
            '<script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script></head>',
            '<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-4 m-0 text-xs">',
            '  <div class="max-w-[1440px] mx-auto pb-4">',
            '    <div class="mb-3 flex flex-wrap items-center justify-between gap-2 bg-[var(--card)] border border-[var(--border)] rounded-lg px-4 py-2.5">',
            '      <div class="font-mono text-xs"><span class="font-semibold">ExploreALS v1.2 &middot; Target &amp; Modality Monograph</span> <span class="text-[var(--muted-foreground)]">&middot; Ricardo Agoga</span></div>',
            '      <div class="flex flex-wrap items-center gap-3"><a href="../CARBON_ALS_INTERACTIVE_EXPLORER.html#replication/cand/' + cid + '" class="text-[var(--link)] underline decoration-dotted hover:decoration-solid font-mono text-xs">Verify Data &amp; Code &rarr;</a><a id="explorer-back-link" href="../CARBON_ALS_INTERACTIVE_EXPLORER.html#dossier/' + cid + '" class="text-[var(--link)] underline font-mono text-xs">&larr; Open in Full 52-Hypothesis Explorer</a></div>',
            "    </div>",
            '    <div class="md:hidden mb-3 sticky top-2 z-20 bg-[var(--card)] border border-[var(--border)] rounded-lg p-2 flex items-center gap-1.5 shadow-sm">',
            f'      <button id="d-mobile-prev" type="button" data-open-dossier="{prev_cid}" class="px-2 py-1 rounded border border-[var(--border)] font-mono text-xs shrink-0 cursor-pointer">&larr;</button>',
            '      <select id="d-mobile-select" aria-label="Select Candidate Dossier" class="flex-1 min-w-0 truncate bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs font-medium text-[var(--foreground)]"></select>',
            f'      <button id="d-mobile-next" type="button" data-open-dossier="{next_cid}" class="px-2 py-1 rounded border border-[var(--border)] font-mono text-xs shrink-0 cursor-pointer">&rarr;</button>',
            '      <button type="button" data-toggle-d-rail="1" aria-expanded="false" aria-controls="d-aside" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs shrink-0 cursor-pointer">List</button>',
            "    </div>",
            '    <div class="grid grid-cols-1 md:grid-cols-[268px_minmax(0,1fr)] gap-3 items-start">',
            '      <aside id="d-aside" aria-label="Candidate Directory" class="hidden md:flex md:flex-col bg-[var(--card)] border border-[var(--border)] rounded-lg p-2.5 gap-2 md:sticky md:top-3 max-h-[calc(100vh-1.5rem)]">',
            '        <div class="flex items-center justify-between"><span class="font-semibold text-xs">Candidate Directory</span><span id="d-nav-count" class="font-mono tabular-nums text-xs text-[var(--muted-foreground)]">52 / 52</span></div>',
            '        <div class="text-xs text-[var(--muted-foreground)] leading-snug"><span class="font-mono font-semibold text-[var(--primary)]">M</span> Full Monograph (8) &middot; Triage Dossier (44)</div>',
            '        <input id="d-search" aria-label="Search candidate directory" type="text" placeholder="Jump: EALS-006, KCNQ2, #4..." class="w-full bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs text-[var(--foreground)]" />',
            '        <div id="d-slice-bar" class="flex flex-wrap gap-1"></div>',
            '        <select id="d-lens" aria-label="Filter by Mechanistic Problem Lens" class="w-full bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs text-[var(--foreground)]"></select>',
            '        <div id="d-nav" class="space-y-0.5 flex-1 min-h-0 max-h-[68vh] overflow-y-auto pr-0.5"></div>',
            "      </aside>",
            '      <div id="d-content" class="min-w-0 space-y-3"></div>',
            "    </div>",
            '    <section aria-label="Attribution, AI Methodology and Research Disclaimer" class="mt-3 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 text-xs text-[var(--muted-foreground)] leading-relaxed">',
            '      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">',
            '        <div class="space-y-1">',
            '          <div class="font-mono font-semibold text-[var(--foreground)]">Author, Correspondence &amp; Open-Science Attribution</div>',
            '          <p>Curated by <strong class="text-[var(--foreground)]">Ricardo Agoga</strong> &middot; Correspondence, inquiries &amp; error reporting: <a href="mailto:helloimra@proton.me" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">helloimra@proton.me</a> &middot; Repository: <a href="https://github.com/helloimra/ExploreALS" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">github.com/helloimra/ExploreALS &nearr;</a>.</p>',
            '          <p>Primary data &amp; tool attributions: Google DeepMind AlphaGenome (v1 API &amp; Atlas AVI; non-commercial research use only), NIH GTEx (v8 / v10), Open Targets (v4), gnomAD (v4.1), Ensembl/GENCODE (v46), ChEMBL (v34), UniProt, RCSB PDB, and ClinicalTrials.gov.</p>',
            "        </div>",
            '        <div class="space-y-1">',
            '          <div class="font-mono font-semibold text-[var(--warning)]">Preclinical Research Notice &amp; AI-Assisted Workflow Disclosure</div>',
            '          <p><strong class="text-[var(--foreground)]">Not Medical Advice:</strong> ExploreALS v1.2 is an independent preclinical and translational research resource intended solely for scientific hypothesis generation. Nothing herein constitutes medical advice, clinical trial recruitment, or a treatment recommendation; individuals with ALS and caregivers should always consult their neurologist or ALS care team before starting, stopping, or modifying any therapy.</p>',
            '          <p><strong class="text-[var(--foreground)]">AI-Assisted Methodology:</strong> Curated via human-directed AI synthesis workflows paired with deterministic Python statistical pipelines across 40 open-access human ALS and preclinical resources (published tables, raw counts, and structures; zero new wet-lab data) and primary-source verification (PubMed, Europe PMC, ClinicalTrials.gov). Quantitative contrasts and accessions are programmatically audited and separated from modeled biophysical and PK-PD estimates, though synthesis prose may contain residual errors — always verify against linked primary sources before experimental use.</p>',
            "        </div>",
            "      </div>",
            "    </section>",
            "  </div>",
            "  <script>",
            f"const DATA_PORT = {_safe_json(js_port)};",
            f"const DATA_CIS = {_safe_json(js_cis)};",
            f"const DATA_MONOGRAPHS = {_safe_json({k: mono_map[k] for k in pilot_ids})};",
            f"const DATA_EV = {_safe_json({k: ev_by_id[k] for k in standalone_ev_ids})};",
            f"const DATA_SUM = {_safe_json(js_sum)};",
            f"const DATA_LENSES = {_safe_json(js_lenses)};",
            'function esc(s){return String(s??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}',
            'function decBadge(d){if(d==="KEEP_CORE")return \'<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Causal human ALS genetics and/or human TDP-43 pathology + functional rescue">Keep &middot; Core</span>\';if(d==="KEEP_EXPLORATORY_UNPROVEN")return \'<span class="px-1.5 py-0.5 rounded font-mono text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap" title="Untested preclinical/biofluid triage queue — prospective Go/No-Go gate required">Keep &middot; Exploratory</span>\';if(d==="RECLASSIFY_BENCHMARK_OR_BIOMARKER")return \'<span class="px-1.5 py-0.5 rounded font-mono text-[var(--primary)] border border-[var(--primary)] text-xs whitespace-nowrap" title="Approved SOC drug, PD calibrator, or fluid staging biomarker">Benchmark</span>\';return \'<span class="px-1.5 py-0.5 rounded font-mono text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="Scientifically falsified by human RCT futility, CNS PK/safety wall, or assay confounding">Drop &middot; Falsified</span>\';}',
            DOSSIER_JS_SVG_CORE,
            DOSSIER_JS_SVG_CUSTOM,
            DOSSIER_JS_VIEW,
            f"let activeTab = 'dossiers'; let selectedId = '{cid}'; dossierId = '{cid}';",
            "if(location.protocol==='about:'){ const bl = document.getElementById('explorer-back-link'); if(bl){ bl.removeAttribute('href'); bl.className='text-[var(--muted-foreground)] font-mono text-xs'; bl.textContent='Standalone Preview (Use ExploreALS Explorer Artifact for all 5 views)'; } }",
            "function openDossier(rawId){ if(!rawId) return; const res = resolveCandidateId(rawId); const id = res ? res.id : String(rawId).replace(/\\.[0-9]+$/, ''); const pObj = DATA_PORT.find(x=>x.id===id); if(!pObj) return; if(location.protocol==='about:'){ dossierId=id; selectedId=id; try { document.title = 'ExploreALS Dossier — #' + pObj.rk + ' ' + pObj.name + ' (' + pObj.id + ')'; } catch(_e) {} renderDossierMain(); return; } const hashId = (res && res.sub) ? res.sub : id; location.href = DATA_MONOGRAPHS[id] ? './' + id + '.html' : '../CARBON_ALS_INTERACTIVE_EXPLORER.html#dossier/' + hashId; }",
            "document.addEventListener('click', e => { const raw = e.target; const el = raw && raw.closest ? raw : (raw && raw.parentElement ? raw.parentElement : null); if(!el || !el.closest) return; const sc = el.closest('[data-scroll-sec]'); if(sc){ e.preventDefault(); const tEl = document.getElementById(sc.getAttribute('data-scroll-sec')||''); if(tEl && tEl.scrollIntoView) tEl.scrollIntoView({behavior:'smooth', block:'start'}); return; } const b = el.closest('[data-open-dossier]'); if(b){ e.preventDefault(); openDossier(b.getAttribute('data-open-dossier')); return; } const ws = el.closest('[data-dossier-slice]'); if(ws){ e.preventDefault(); setDossierSlice(ws.getAttribute('data-dossier-slice')); return; } const rdn = el.closest('[data-reset-d-nav]'); if(rdn){ e.preventDefault(); resetDossierNav(); return; } const tr = el.closest('[data-toggle-d-rail]'); if(tr){ e.preventDefault(); toggleDossierRail(); return; } const rc = el.closest('[data-jump-rep-cand]'); if(rc && location.protocol!=='about:'){ e.preventDefault(); location.href = '../CARBON_ALS_INTERACTIVE_EXPLORER.html#replication/cand/' + rc.getAttribute('data-jump-rep-cand'); return; } const rr = el.closest('[data-open-rep-run]'); if(rr && location.protocol!=='about:'){ e.preventDefault(); location.href = '../CARBON_ALS_INTERACTIVE_EXPLORER.html#replication/' + rr.getAttribute('data-open-rep-run'); return; } const rd = el.closest('[data-open-rep-ds]'); if(rd && location.protocol!=='about:'){ e.preventDefault(); location.href = '../CARBON_ALS_INTERACTIVE_EXPLORER.html#replication/' + rd.getAttribute('data-open-rep-ds'); return; } const cs = el.closest('[data-copy-sha]'); if(cs){ e.preventDefault(); const v = cs.getAttribute('data-copy-sha')||''; if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(v); } cs.textContent='Copied \\u2713'; setTimeout(()=>{ cs.textContent='SHA-256:' + v.slice(0,8); }, 1400); return; } const ji = el.closest('[data-jump-intervals]'); if(ji && location.protocol!=='about:'){ e.preventDefault(); location.href = '../CARBON_ALS_INTERACTIVE_EXPLORER.html#intervals/' + (ji.getAttribute('data-jump-intervals')||dossierId); return; } const j = el.closest('[data-jump-subnodes],[data-switch-tab]'); if(j && location.protocol!=='about:'){ e.preventDefault(); location.href = '../CARBON_ALS_INTERACTIVE_EXPLORER.html#dossier/' + dossierId; } });",
            "document.addEventListener('keydown', e => { const tag = e.target && e.target.tagName ? e.target.tagName : ''; if(!e.ctrlKey && !e.metaKey && !e.altKey && tag !== 'INPUT' && !e.target.closest('select') && tag !== 'TEXTAREA' && (e.key === '[' || e.key === ']')){ const pIdx = MONOGRAPH_ORDER.indexOf(dossierId); if(pIdx >= 0){ e.preventDefault(); openDossier(MONOGRAPH_ORDER[(pIdx + (e.key === '[' ? -1 : 1) + MONOGRAPH_ORDER.length) % MONOGRAPH_ORDER.length]); } } });",
            "const dsIn = document.getElementById('d-search'); if(dsIn) dsIn.addEventListener('input', renderDossierSidebar);",
            "const dlSel = document.getElementById('d-lens'); if(dlSel) dlSel.addEventListener('change', e => setDossierLens(e.target.value));",
            "const dmSel = document.getElementById('d-mobile-select'); if(dmSel) dmSel.addEventListener('change', e => openDossier(e.target.value));",
            "renderDossierMain();",
            "  </script></body></html>",
        ])
        assert not RAW_OLIGO_SEQ_RE.search(page) and not GAPPED_OLIGO_RE.search(page), f"Biosecurity leak in {cid}.html"
        assert "/100" not in page, f"/100 score leaked in standalone {cid}.html"
        assert not EXPLORE_LEAK_RE.search(page), f"ExploreALS leak in standalone {cid}.html"
        assert not re.search(r"\bwiki\b|\bv0\b|\bstream\s+[ab]\b|wave\s+2|\bD003\b|\bD045\b|\bDS045\b|Phase\s*3A", page, re.IGNORECASE), f"Jargon leak in standalone {cid}.html"
        fp = mono_dir / f"{cid}.html"
        fp.write_text(page, encoding="utf-8")
        written.append(fp)

    return written
