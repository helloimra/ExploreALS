"""Client-side Tab 6 Inspector, Deep-Link Router, CSV/JSON Blob Downloader & 3 Specialist-Verified [MODEL_PRIOR] Sensitivity Sandboxes."""
from __future__ import annotations

REPLICATION_SANDBOXES_JS = r"""
function renderRepInspector(){
  const box = document.getElementById('rep-detail');
  if(!box) return;
  const retBtn = repReturnDossier
    ? (repReturnTab === 'portfolio'
      ? `<button type="button" data-switch-tab="portfolio" class="text-[var(--link)] underline font-semibold cursor-pointer">&larr; Return to ${esc(repReturnDossier)} in Triage Table</button>`
      : `<button type="button" data-open-dossier="${esc(repReturnDossier)}" class="text-[var(--link)] underline font-semibold cursor-pointer">&larr; Return to ${esc(repReturnDossier)} Report</button>`)
    : '';
  const retBar = repReturnDossier ? `<div class="p-2 rounded bg-[var(--background)] border border-[var(--primary)] flex items-center justify-between gap-2 text-xs font-mono"><span>Auditing provenance from <strong>${esc(repReturnDossier)}</strong></span>${retBtn}</div>` : '';

  if(repMode === 'runs'){
    const r = DATA_RUNS.find(x => x.id === selectedRepKey) || DATA_RUNS[0];
    if(!r){ box.innerHTML = retBar + '<div class="text-[var(--muted-foreground)]">No matching run.</div>'; return; }
    const sLinks = r.script.split(';').filter(Boolean).map(sp => `<a href="https://github.com/helloimra/ExploreALS/blob/main/${esc(sp)}" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted hover:decoration-solid font-mono break-all">${esc(sp)} &nearr;</a>`).join('<br/>');
    const dsChips = r.ds ? r.ds.split(';').filter(Boolean).map(d => `<button type="button" data-open-rep-ds="${esc(d)}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">${esc(d)} &rarr;</button>`).join(' ') : '<span class="text-[var(--muted-foreground)] font-mono">Cached API / Portfolio Synthesis</span>';
    const cChips = r.cands ? r.cands.split(';').filter(Boolean).slice(0,18).map(c => `<button type="button" data-open-dossier="${esc(c)}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--primary)] cursor-pointer">${esc(c)}</button>`).join(' ') : '';
    const cmd = `uv run python ${r.script.split(';')[0]}`;
    box.innerHTML = `${retBar}
      <div class="flex flex-wrap items-start justify-between gap-2 border-b border-[var(--card-border)] pb-2.5">
        <div><div class="font-mono font-bold text-sm">${esc(r.id)} <span class="font-normal text-xs text-[var(--success)]">&#10003; Verified</span></div><div class="text-[var(--muted-foreground)] text-xs mt-0.5">${esc(r.grp)}</div></div>
        <button type="button" data-copy-cmd="${esc(cmd)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">Copy Run Cmd</button>
      </div>
      <div class="space-y-2.5 text-xs">
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono mb-0.5">Repository Script Path(s)</div>${sLinks}</div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono mb-1">Staged Input Datasets (Click to Inspect SHA-256)</div><div class="flex flex-wrap gap-1">${dsChips}</div></div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono mb-0.5">Verified Output Artifact(s)</div><div class="font-mono break-words">${esc(r.out)}</div></div>
        <div><div class="font-semibold text-[var(--foreground)] mb-0.5">Computational Scope &amp; Statistical Method:</div><p class="text-[var(--muted-foreground)] leading-relaxed">${esc(r.sum)}</p></div>
        ${cChips ? `<div class="border-t border-[var(--card-border)] pt-2"><div class="text-[var(--muted-foreground)] font-mono mb-1">Backed Candidate Dossiers:</div><div class="flex flex-wrap gap-1">${cChips}</div></div>` : ''}
      </div>`;
  } else if(repMode === 'datasets'){
    const d = DATA_DATASETS.find(x => x.id === selectedRepKey) || DATA_DATASETS[0];
    if(!d){ box.innerHTML = retBar + '<div class="text-[var(--muted-foreground)]">No matching dataset.</div>'; return; }
    const consRuns = DATA_RUNS.filter(r => r.ds.split(';').includes(d.id)).map(r => `<button type="button" data-open-rep-run="${esc(r.id)}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">${esc(r.id)} &rarr;</button>`).join(' ');
    box.innerHTML = `${retBar}
      <div class="flex flex-wrap items-start justify-between gap-2 border-b border-[var(--card-border)] pb-2.5">
        <div><div class="font-mono font-bold text-sm">${esc(d.id)} &middot; <span class="font-normal text-xs text-[var(--muted-foreground)]">${esc(d.mb)}</span></div><div class="text-[var(--muted-foreground)] text-xs mt-0.5">${esc(d.lic)} &middot; ${esc(d.tier.replace(/_/g,' '))}</div></div>
        <button type="button" data-copy-sha="${esc(d.sha)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">Copy 64-Char SHA-256</button>
      </div>
      <div class="space-y-2.5 text-xs">
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono mb-0.5">Full 64-Character SHA-256 Digest</div><div class="font-mono break-words text-[var(--foreground)]">${esc(d.sha)}</div></div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono">Local Staging Path</div><div class="font-mono break-words mt-0.5">${esc(d.rel)}</div></div>
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono">Primary Accession / DOI</div><div class="font-mono break-words mt-0.5">${escLink(d.acc, '')}</div></div>
        </div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono mb-0.5">Canonical Retrieval URL / Fetcher Rule</div><div class="font-mono break-words text-[var(--muted-foreground)]">${esc(d.url)}</div></div>
        <div><div class="font-semibold mb-0.5">Cohort Description:</div><p class="text-[var(--muted-foreground)] leading-relaxed">${esc(d.desc)}</p></div>
        ${consRuns ? `<div class="border-t border-[var(--card-border)] pt-2"><div class="text-[var(--muted-foreground)] font-mono mb-1">Consuming Analysis Runs:</div><div class="flex flex-wrap gap-1">${consRuns}</div></div>` : ''}
      </div>`;
  } else {
    const f = DATA_FORMULAS.find(x => x.eid === selectedRepKey) || DATA_FORMULAS[0];
    if(!f){ box.innerHTML = retBar + '<div class="text-[var(--muted-foreground)]">No matching evidence record.</div>'; return; }
    box.innerHTML = `${retBar}
      <div class="flex flex-wrap items-start justify-between gap-2 border-b border-[var(--card-border)] pb-2.5">
        <div><div class="font-mono font-bold text-sm">${esc(f.eid)} &middot; <button type="button" data-open-dossier="${esc(f.cid)}" class="text-[var(--primary)] hover:underline cursor-pointer">${esc(f.cid)} Dossier &rarr;</button></div><div class="text-[var(--muted-foreground)] text-xs mt-0.5 font-mono">${esc(f.cls.replace(/_/g,' '))} &middot; ${esc(f.anc)}</div></div>
        <button type="button" data-copy-sha="${esc(f.sha)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">Copy 64-Char SHA-256</button>
      </div>
      <div class="space-y-2 text-xs">
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono mb-0.5">Exact Cohort &amp; Adjusted Contrast</div><div class="leading-snug">${esc(f.con)}</div></div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono">Statistical Unit &amp; True Donor N</div><div class="font-mono mt-0.5">${esc(f.unit)} (units=${esc(f.nu||'—')} &middot; donors=${esc(f.ndon||'—')})</div></div>
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono">Effect &amp; Precision</div><div class="font-mono mt-0.5 break-words">${esc(f.est)}${f.ci?` (${esc(f.ci)})`:''}</div></div>
        </div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] font-mono mb-0.5">Model Equation / Statistical Test &amp; Exclusion Rule</div><div class="font-mono text-[var(--foreground)] break-words">${esc(f.mod)}</div><div class="text-[var(--muted-foreground)] mt-0.5">Rule: ${esc(f.excl)} &middot; Overlap: <span class="font-mono">${esc(f.ovl)}</span></div></div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] font-mono"><span class="text-[var(--muted-foreground)]">Covariate vs Multiplicity Split:</span> unadj_p=${esc(f.up||'—')} &middot; cov_adj_p=${esc(f.cp||'—')} &middot; mult_adj_p=${esc(f.mp||'—')} (${esc(f.mfam)})</div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] font-mono break-words"><span class="text-[var(--muted-foreground)]">Anchor (<button type="button" data-open-rep-run="${esc(f.run)}" class="text-[var(--link)] hover:underline cursor-pointer">${esc(f.run)}</button>):</span> ${esc(f.arel)}<div class="text-[var(--muted-foreground)] mt-0.5">${esc(f.sha)}</div></div>
      </div>`;
  }
}

function openReplicationTarget(kind, key, fromDossier='', fromTab='dossiers', historyMode='push'){
  if(fromDossier){ repReturnDossier = fromDossier; repReturnTab = fromTab || 'dossiers'; }
  const newH = kind === 'cand' ? '#replication/cand/' + encodeURIComponent(key) : '#replication/' + encodeURIComponent(key);
  switchTab('replication', 'none');
  document.getElementById('rep-search').value = '';
  if(kind === 'run'){ setRepMode('runs'); selectedRepKey = key; }
  else if(kind === 'ds'){ setRepMode('datasets'); selectedRepKey = key; }
  else if(kind === 'ev'){ setRepMode('evidence'); selectedRepKey = key; }
  else if(kind === 'cand'){ setRepMode('evidence'); document.getElementById('rep-search').value = key; }
  renderReplicationWorkbench();
  if(typeof commitHistory === 'function') commitHistory(historyMode, newH);
}

function downloadBlob(filename, mime, content){
  const blob = new Blob([content], {type: mime});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; document.body.appendChild(a); a.click();
  setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 200);
}
function rowsToCsv(rows){
  if(!rows || !rows.length) return '';
  const ks = Object.keys(rows[0]);
  const escCsv = v => { const s = String(v ?? ''); return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g,'""') + '"' : s; };
  return [ks.join(','), ...rows.map(r => ks.map(k => escCsv(r[k])).join(','))].join('\r\n');
}
function exportRegistryBlob(which){
  const builders = {
    updates: ['living_evidence_updates.csv', () => (typeof DATA_UPDATES !== 'undefined' ? DATA_UPDATES : []).map(u => ({
      update_id:u.id, date_iso:u.dt, release_tag:u.tag, update_category:u.cat,
      affected_ids:u.ids.join(';'), decision_impact:u.imp, headline:u.hdr,
      prior_state_or_assumption:u.pre, new_evidence_or_revision:u.post,
      portfolio_and_gate_consequence:u.cons, primary_sources:u.srcs.join(';'),
      verification_anchor:u.ancs.join(';')
    }))],
    portfolio: ['phase4_unified_portfolio.csv', () => DATA_PORT.map(r => ({
      unified_rank:r.rk, biological_rank:r.brk, accession_id:r.id, primary_symbol:r.sym,
      synonyms:(r.syn||[]).join(';'), origin_phase:r.o, origin_subcohort:r.sub, track:r.trk,
      gene_or_drug:r.name, primary_modality:r.mod, epistemic_state:r.epi, decision:r.dec,
      scientific_actionability_tier:r.tier, clinical_readiness_trl:r.trl,
      next_gate_experimental_class:r.gate, primary_evidence_basis:r.basis,
      clinical_crowding:r.crowd, model_prior_dependency:r.prior,
      unsolved_hurdle_count:r.hcnt, unsolved_hurdles:r.hurdles,
      lead_cis_interval_id:r.iv, lead_offtarget_safety_status:r.ivst,
      discriminating_next_test:r.nxt
    }))],
    intervals: ['phase4_unified_cis_intervals.csv', () => DATA_CIS.map(c => ({
      unified_interval_order:c.ord, origin_phase:c.o, accession_id:c.pid, target_accession_id:c.sc,
      gene_symbol:c.gene, program_role:c.role, rank_within_gene:c.rk, is_promoted_lead:c.lead,
      interval_id:c.iv, chrom:c.chr, grch38_start:c.lo, grch38_end:c.hi, strand:c.strd,
      length_bp:c.len, cis_mechanism_or_mode:c.mode, gc_pct:c.gc, tm_phys_pops_c:c.tm,
      dg37_kcal:c.dg, max_avi_phred:c.avi, spliced_0_1_wobble:c.sp, premRNA_6tier:c.pm,
      premRNA_1mm_sense_genes:c.pm1_all, flagged_constrained_neuronal_hits:c.flags,
      offtarget_safety_status:c.st
    }))],
    subnodes: ['subnode_dissection.csv', () => DATA_SUB.map(s => ({
      subunit_accession_id:s.id, parent_accession_id:s.par, gene_symbol:s.gene,
      molecular_role:s.role, idg_tdl:s.tdl, target_safety_class:s.tsa,
      gnomad_essentiality_check:s.gnomad, druggability_check:s.drug,
      verdict_code:s.vraw, verdict_label:s.vlbl, verdict_rationale:s.vbody
    }))],
    formulas: ['statistical_models_and_contrasts.csv', () => DATA_FORMULAS.map(f => ({
      evidence_id:f.eid, accession_id:f.cid, analysis_run_id:f.run, inference_class:f.cls,
      statistical_unit:f.unit, n_statistical_units:f.nu, n_unique_donors_or_participants:f.ndon,
      exact_contrast:f.con, model_formula_or_test:f.mod, effect_estimate:f.est, se_or_ci95:f.ci,
      unadjusted_or_primary_nominal_p:f.up, covariate_adjusted_nominal_p:f.cp,
      multiplicity_adjusted_p:f.mp, multiple_testing_family:f.mfam,
      missingness_or_exclusion_rule:f.excl, overlap_group_id:f.ovl,
      anchor_type:f.anc, anchor_relpath:f.arel, sha64:f.sha
    }))],
    datasets: ['datasets_manifest.csv', () => DATA_DATASETS.map(d => ({
      dataset_id:d.id, domain:d.dom, local_relpath:d.rel, accession_or_doi:d.acc,
      license_or_access:d.lic, size_display:d.mb, sha256:d.sha, relevant_candidates:d.cands,
      description:d.desc, redistribution_tier:d.tier, canonical_fetch_url:d.url
    }))],
    runs: ['analysis_runs_and_flagship.csv', () => DATA_RUNS.map(r => ({
      analysis_run_id:r.id, stage_group:r.grp, script_relpath:r.script, output_artifacts:r.out,
      datasets_used:r.ds, relevant_candidates:r.cands, summary:r.sum, is_flagship:r.flag
    }))],
    overlap: ['cohort_overlap_map.csv', () => DATA_OVERLAP.map(o => ({
      overlap_group_id:o.id, cluster_name:o.name, datasets_involved:o.ds,
      donor_accounting_rule:o.rule, canonical_model_formula:o.formula
    }))]
  };
  if(which === 'json_all'){
    const outObj = {version:'1.2.3'};
    Object.keys(builders).forEach(k => { outObj[k] = builders[k][1](); });
    downloadBlob('exploreals_v1_2_provenance_bundle.json', 'application/json', JSON.stringify(outObj, null, 2));
    return;
  }
  const hit = builders[which];
  if(hit) downloadBlob(hit[0], 'text/csv;charset=utf-8', rowsToCsv(hit[1]()));
}

function initSandboxes(){
  const sb = document.getElementById('sandbox-body');
  if(!sb) return;
  sb.innerHTML = `
    <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-2">
      <div class="font-mono font-semibold text-[var(--foreground)]">1. KCNQ2 ER Co-Trapping &amp; 2:2 Heteromers (#4 EALS-006)</div>
      <label class="block"><span>RNA Exon-5 Skip (&Delta;PSI): <strong id="sb-k-p-val" class="font-mono">0.214</strong></span><input id="sb-k-p" aria-label="KCNQ2 RNA Exon-5 Skip fraction" type="range" min="0.05" max="0.50" step="0.005" value="0.214" class="w-full mt-0.5"/></label>
      <label class="block"><span>2:2 Kv7.2:Kv7.3 Heteromer Share (&theta;): <strong id="sb-k-h-val" class="font-mono">0.00 (4:0 Homomer)</strong></span><input id="sb-k-h" aria-label="Kv7.2 to Kv7.3 heteromer share" type="range" min="0" max="1" step="0.05" value="0" class="w-full mt-0.5"/></label>
      <label class="block"><span>Mutant Surface Escape (&alpha;_esc): <strong id="sb-k-a-val" class="font-mono">0.15</strong></span><input id="sb-k-a" aria-label="Mutant subunit surface escape" type="range" min="0" max="1" step="0.05" value="0.15" class="w-full mt-0.5"/></label>
      <div id="sb-k-out" class="p-2 rounded bg-[var(--card)] border border-[var(--border)] font-mono space-y-0.5"></div>
    </div>
    <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-2">
      <div class="font-mono font-semibold text-[var(--foreground)]">2. SARM1 Washout: Orthosteric BEXi vs T-Lock (#1 EALS-030)</div>
      <select id="sb-s-mode" aria-label="STMN2-SARM1 interaction model" class="w-full bg-[var(--card)] border border-[var(--border)] rounded px-2 py-1 text-xs font-mono">
        <option value="bliss">Mode 1 (Default): Parallel Bliss Independence (Krus 2022)</option>
        <option value="mwc">Mode 2: Hypothetical Indirect L_eff Shift (Unproven in Mice)</option>
      </select>
      <label class="block"><span>Oral Washout Ratio ([I]/Kd): <strong id="sb-s-u-val" class="font-mono">0.20x</strong></span><input id="sb-s-u" aria-label="Inhibitor over Kd washout ratio" aria-valuetext="0.20x Kd" type="range" min="-2.0" max="1.3" step="0.05" value="-0.70" class="w-full mt-0.5"/></label>
      <label class="block"><span>Allosteric L_eff: <strong id="sb-s-l-val" class="font-mono">2.5 (Leahey Cal.)</strong></span><input id="sb-s-l" aria-label="Baseline SARM1 allosteric L_eff" type="range" min="2.0" max="65.0" step="0.5" value="2.5" class="w-full mt-0.5"/></label>
      <div id="sb-s-out" class="p-2 rounded bg-[var(--card)] border border-[var(--border)] font-mono space-y-0.5"></div>
    </div>
    <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-2">
      <div class="font-mono font-semibold text-[var(--foreground)]">3. MIROCALS Ph3 Survival &amp; Assay Sizing (#2 EALS-031)</div>
      <select id="sb-m-pre" aria-label="MIROCALS follow-up horizon preset" class="w-full bg-[var(--card)] border border-[var(--border)] rounded px-2 py-1 text-xs font-mono">
        <option value="0.41">Preset A: 36–42 mo Event-Driven Follow-Up (P0=0.41)</option>
        <option value="0.37">Preset B: &lt;750 pg/mL Zero-Death Stratum Dilution (P0=0.37)</option>
        <option value="0.29">Preset C: Fixed 24-mo Slow-Progressor Rate (P0=0.29)</option>
      </select>
      <label class="block"><span>Target Hazard Ratio (HR): <strong id="sb-m-hr-val" class="font-mono">0.70</strong></span><input id="sb-m-hr" aria-label="Target hazard ratio" type="range" min="0.52" max="0.80" step="0.01" value="0.70" class="w-full mt-0.5"/></label>
      <label class="block"><span>Control Event Prob P0(T) / Censoring 5% / LP Pass 79%: <strong id="sb-m-p0-val" class="font-mono">0.41</strong></span><input id="sb-m-p0" aria-label="Control cumulative mortality P0" type="range" min="0.22" max="0.50" step="0.01" value="0.41" class="w-full mt-0.5"/></label>
      <div id="sb-m-out" class="p-2 rounded bg-[var(--card)] border border-[var(--border)] font-mono space-y-0.5"></div>
    </div>`;
  updateSandboxes();
}

function updateSandboxes(){
  const kp = document.getElementById('sb-k-p');
  if(!kp) return;
  const p = parseFloat(kp.value), th = parseFloat(document.getElementById('sb-k-h').value), al = parseFloat(document.getElementById('sb-k-a').value);
  document.getElementById('sb-k-p-val').textContent = p.toFixed(3);
  document.getElementById('sb-k-h-val').textContent = th===0 ? '0.00 (4:0 Homomer)' : (th===1 ? '1.00 (2:2 Heteromer)' : th.toFixed(2) + ' Mixed');
  document.getElementById('sb-k-a-val').textContent = al.toFixed(2);
  const im = (1-th)*Math.pow(1-p,4) + th*Math.pow(1-p,2);
  const ns = (1-th)*Math.pow(1-p+al*p,4) + th*Math.pow(1-p+al*p,2);
  const erTrap = Math.max(0, 1 - ns), surfDead = Math.max(0, ns - im);
  const poisPct = ns > 0 ? (100 * surfDead / ns).toFixed(0) : '0';
  document.getElementById('sb-k-out').innerHTML = `<div>WT Functional M-Current: <strong class="text-[var(--warning)]">${(100*im).toFixed(1)}%</strong> (${(100*(1-im)).toFixed(1)}% loss)</div><div>ER-Trapped: <strong>${(100*erTrap).toFixed(1)}%</strong> &middot; Surface Pore-Dead: <strong>${(100*surfDead).toFixed(1)}%</strong></div><div class="text-[var(--muted-foreground)]">Surface Kv7: ${(100*ns).toFixed(1)}% (${poisPct}% poisoned; I_M invariant to &alpha;_esc)</div>`;

  const sm = document.getElementById('sb-s-mode').value;
  const suEl = document.getElementById('sb-s-u');
  const u = Math.pow(10, parseFloat(suEl.value));
  const l0 = parseFloat(document.getElementById('sb-s-l').value);
  suEl.setAttribute('aria-valuetext', u.toFixed(2) + 'x Kd');
  document.getElementById('sb-s-u-val').textContent = u.toFixed(2) + 'x';
  document.getElementById('sb-s-l-val').textContent = l0.toFixed(1) + (Math.abs(l0-2.5)<0.3?' (Leahey Cal.)':(l0<=10?' (ALS Prior)':''));
  const base = 1 / (1 + l0);
  const zR = Math.pow(1 + 5.154 * u, 6);
  const aBexi = (zR / (l0 + zR)) / (1 + u);
  const aTlock = Math.pow(1 + u/6.5, 8) / (l0*Math.pow(1+u, 8) + Math.pow(1+u/6.5, 8));
  const rB = aBexi / base, rT = aTlock / base;
  const fRatio = ((1 + l0) / (1 + 8)).toFixed(1);
  const combLine = sm === 'bliss' ? 'STMN2+SARM1: 1.0x IC90 shift (Bliss E=83.5% at 45%+70%)' : `Hypothetical L_eff 8&rarr;${l0.toFixed(1)}: IC90 1.0x; floor-dose ~${fRatio}x [Unproven]`;
  document.getElementById('sb-s-out').innerHTML = `<div>BEXi (Base-Exchange) vs Base: <strong class="${rB>1.05?'text-[var(--error)]':'text-[var(--success)]'}">${rB.toFixed(2)}x</strong> ${rB>1.05?'(Washout Spike!)':''}</div><div>T-Lock (ARM&ndash;TIR) vs Base: <strong class="text-[var(--success)]">${rT.toFixed(2)}x</strong> (Monotonic &le;1.0x)</div><div class="text-[var(--muted-foreground)]">${combLine}</div>`;

  const hr = parseFloat(document.getElementById('sb-m-hr').value), p0 = parseFloat(document.getElementById('sb-m-p0').value);
  document.getElementById('sb-m-hr-val').textContent = hr.toFixed(2);
  document.getElementById('sb-m-p0-val').textContent = p0.toFixed(2);
  const dReq = Math.ceil(Math.pow(1.959964+0.841621, 2) / (0.25 * Math.pow(Math.log(hr), 2)));
  const p1 = 1 - Math.pow(1 - p0, hr), pbar = 0.5*(p0 + p1);
  const nRand = 2 * Math.ceil(dReq / (2 * pbar * 0.95));
  const nScr = Math.ceil(nRand / 0.79);
  document.getElementById('sb-m-out').innerHTML = `<div>Required Deaths (80% pwr, 2s &alpha;=0.05): <strong class="text-[var(--primary)]">${dReq}</strong></div><div>Pooled Event Rate: <strong>${(100*pbar).toFixed(1)}%</strong> &rarr; N_rand = <strong>${nRand}</strong></div><div class="text-[var(--muted-foreground)]">LP Screen (~79% &le;3,700 pg/mL; &lt;750 n=20 had 0 deaths): N_screen &approx; <strong>${nScr}</strong></div>`;
}
"""
