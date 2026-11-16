"""Client-side Tab 6 Inspector, Deep-Link Router, CSV/JSON Blob Downloader & 3 Specialist-Verified [MODEL_PRIOR] Sensitivity Sandboxes."""
from __future__ import annotations

REPLICATION_SANDBOXES_JS = r"""
function renderRepInspector(){
  const box = document.getElementById('rep-detail');
  if(!box) return;
  const retBar = repReturnDossier ? `<div class="p-2 rounded bg-[var(--background)] border border-[var(--primary)] flex items-center justify-between gap-2 text-xs font-mono"><span>Auditing provenance from <strong>${esc(repReturnDossier)}</strong></span><button type="button" data-open-dossier="${esc(repReturnDossier)}" class="text-[var(--link)] underline font-semibold cursor-pointer">&larr; Return to ${esc(repReturnDossier)} Dossier</button></div>` : '';

  if(repMode === 'runs'){
    const r = DATA_RUNS.find(x => x.id === selectedRepKey) || DATA_RUNS[0];
    if(!r){ box.innerHTML = retBar + '<div class="text-[var(--muted-foreground)]">No matching run.</div>'; return; }
    const sLinks = r.script.split(';').filter(Boolean).map(sp => `<a href="https://github.com/helloimra/ExploreALS/blob/main/${esc(sp)}" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted hover:decoration-solid font-mono break-words">${esc(sp)} &nearr;</a>`).join('<br/>');
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

function openReplicationTarget(kind, key, fromDossier=''){
  if(fromDossier) repReturnDossier = fromDossier;
  switchTab('replication');
  document.getElementById('rep-search').value = '';
  if(kind === 'run'){ setRepMode('runs'); selectedRepKey = key; }
  else if(kind === 'ds'){ setRepMode('datasets'); selectedRepKey = key; }
  else if(kind === 'cand'){ setRepMode('evidence'); document.getElementById('rep-search').value = key; }
  renderReplicationWorkbench();
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
  const map = {portfolio:[DATA_PORT,'phase4_unified_portfolio.csv'], intervals:[DATA_CIS,'phase4_unified_cis_intervals.csv'], subnodes:[DATA_SUB,'subnode_dissection.csv'], formulas:[DATA_FORMULAS,'statistical_models_and_contrasts.csv'], datasets:[DATA_DATASETS,'datasets_manifest.csv'], runs:[DATA_RUNS,'analysis_runs_and_flagship.csv'], overlap:[DATA_OVERLAP,'cohort_overlap_map.csv']};
  if(which === 'json_all'){
    downloadBlob('exploreals_v1_2_provenance_bundle.json', 'application/json', JSON.stringify({version:'1.2.0', portfolio:DATA_PORT, cis_intervals:DATA_CIS, subnodes:DATA_SUB, statistical_models:DATA_FORMULAS, datasets:DATA_DATASETS, runs:DATA_RUNS, cohort_overlap:DATA_OVERLAP}, null, 2));
    return;
  }
  const hit = map[which];
  if(hit) downloadBlob(hit[1], 'text/csv;charset=utf-8', rowsToCsv(hit[0]));
}

function initSandboxes(){
  const sb = document.getElementById('sandbox-body');
  if(!sb) return;
  sb.innerHTML = `
    <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-2">
      <div class="font-mono font-semibold text-[var(--foreground)]">1. KCNQ2 ER Co-Trapping &amp; 2:2 Heteromers (#2 C006)</div>
      <label class="block"><span>RNA Exon-5 Skip (&Delta;PSI): <strong id="sb-k-p-val" class="font-mono">0.214</strong></span><input id="sb-k-p" aria-label="KCNQ2 RNA Exon-5 Skip fraction" type="range" min="0.05" max="0.50" step="0.005" value="0.214" class="w-full mt-0.5"/></label>
      <label class="block"><span>2:2 Kv7.2:Kv7.3 Heteromer Share (&theta;): <strong id="sb-k-h-val" class="font-mono">0.00 (4:0 Nodal)</strong></span><input id="sb-k-h" aria-label="Kv7.2 to Kv7.3 heteromer share" type="range" min="0" max="1" step="0.05" value="0" class="w-full mt-0.5"/></label>
      <label class="block"><span>Mutant Surface Escape (&alpha;_esc): <strong id="sb-k-a-val" class="font-mono">0.15</strong></span><input id="sb-k-a" aria-label="Mutant subunit surface escape" type="range" min="0" max="1" step="0.05" value="0.15" class="w-full mt-0.5"/></label>
      <div id="sb-k-out" class="p-2 rounded bg-[var(--card)] border border-[var(--border)] font-mono space-y-0.5"></div>
    </div>
    <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-2">
      <div class="font-mono font-semibold text-[var(--foreground)]">2. SARM1 Washout &amp; Parallel Bliss vs MWC (#1 S06)</div>
      <select id="sb-s-mode" aria-label="STMN2-SARM1 interaction model" class="w-full bg-[var(--card)] border border-[var(--border)] rounded px-2 py-1 text-xs font-mono">
        <option value="bliss">Mode 1 (Default): Parallel Bliss Independence (Krus 2022)</option>
        <option value="mwc">Mode 2: Hypothetical Indirect L_eff Shift (Unproven in Mice)</option>
      </select>
      <label class="block"><span>Oral Washout Ratio ([I]/Kd): <strong id="sb-s-u-val" class="font-mono">0.35x</strong></span><input id="sb-s-u" aria-label="Inhibitor over Kd washout ratio" type="range" min="-2.0" max="1.3" step="0.05" value="-0.456" class="w-full mt-0.5"/></label>
      <label class="block"><span>Axonal Allosteric L0: <strong id="sb-s-l-val" class="font-mono">8 (ALS)</strong></span><input id="sb-s-l" aria-label="Baseline SARM1 allosteric L0" type="range" min="4" max="120" step="2" value="8" class="w-full mt-0.5"/></label>
      <div id="sb-s-out" class="p-2 rounded bg-[var(--card)] border border-[var(--border)] font-mono space-y-0.5"></div>
    </div>
    <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-2">
      <div class="font-mono font-semibold text-[var(--foreground)]">3. MIROCALS Ph3 Survival &amp; LP Sizing (#3 S07)</div>
      <select id="sb-m-pre" aria-label="MIROCALS follow-up horizon preset" class="w-full bg-[var(--card)] border border-[var(--border)] rounded px-2 py-1 text-xs font-mono">
        <option value="0.41">Preset A: 36–42 mo Event-Driven Follow-Up (P0=0.41)</option>
        <option value="0.29">Preset B: Fixed 24-mo Slow-Progressor Rate (P0=0.29)</option>
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
  document.getElementById('sb-k-out').innerHTML = `<div>WT Functional M-Current: <strong class="text-[var(--warning)]">${(100*im).toFixed(1)}%</strong> (${(100*(1-im)).toFixed(1)}% loss)</div><div>Surface Kv7 Density: <strong>${(100*ns).toFixed(1)}%</strong> &middot; ER-Trapped: <strong>${(100*(1-ns)).toFixed(1)}%</strong></div><div class="text-[var(--muted-foreground)]">Lowering &alpha;_esc co-traps WT in ER (I_M stays ${(100*im).toFixed(1)}%).</div>`;

  const sm = document.getElementById('sb-s-mode').value;
  const u = Math.pow(10, parseFloat(document.getElementById('sb-s-u').value));
  const l0 = parseFloat(document.getElementById('sb-s-l').value);
  document.getElementById('sb-s-u-val').textContent = u.toFixed(2) + 'x';
  document.getElementById('sb-s-l-val').textContent = l0 + (l0<=12?' (ALS)':'');
  const base = 1 / (1 + l0);
  const aBexi = Math.pow(1 + u/0.22, 7) / (l0*Math.pow(1+0.05*u, 8) + Math.pow(1+u/0.22, 8));
  const aTlock = Math.pow(1 + u/6.5, 8) / (l0*Math.pow(1+u, 8) + Math.pow(1+u/6.5, 8));
  const rB = aBexi / base, rT = aTlock / base;
  const fRatio = ((1 + l0) / (1 + 8)).toFixed(2);
  const combLine = sm === 'bliss' ? 'STMN2+SARM1: 1.00x IC90 shift (Bliss E=83.5% at 45%+70%)' : `Hypothetical L_eff 8&rarr;${l0}: IC90 1.00x; floor-dose ~${fRatio}x [Unproven]`;
  document.getElementById('sb-s-out').innerHTML = `<div>BEXi NADase vs Base: <strong class="${rB>1.05?'text-[var(--error)]':'text-[var(--success)]'}">${rB.toFixed(2)}x</strong> ${rB>1.05?'(Washout Spike!)':''}</div><div>T-Lock NADase vs Base: <strong class="text-[var(--success)]">${rT.toFixed(2)}x</strong> (Monotonic &le;1.0x)</div><div class="text-[var(--muted-foreground)]">${combLine}</div>`;

  const hr = parseFloat(document.getElementById('sb-m-hr').value), p0 = parseFloat(document.getElementById('sb-m-p0').value);
  document.getElementById('sb-m-hr-val').textContent = hr.toFixed(2);
  document.getElementById('sb-m-p0-val').textContent = p0.toFixed(2);
  const dReq = Math.ceil(Math.pow(1.959964+0.841621, 2) / (0.25 * Math.pow(Math.log(hr), 2)));
  const p1 = 1 - Math.pow(1 - p0, hr), pbar = 0.5*(p0 + p1);
  const nRand = 2 * Math.ceil(dReq / (2 * pbar * 0.95));
  const nScr = Math.ceil(nRand / 0.7909);
  document.getElementById('sb-m-out').innerHTML = `<div>Required Deaths (80% pwr, 2s &alpha;=0.05): <strong class="text-[var(--primary)]">${dReq}</strong></div><div>Pooled Event Rate: <strong>${(100*pbar).toFixed(1)}%</strong> &rarr; N_rand = <strong>${nRand}</strong></div><div class="text-[var(--muted-foreground)]">LP Screen (~79% &le;3,700 pg/mL): N_screen &approx; <strong>${nScr}</strong> (gated on Stage-0 BioVendor&rarr;CLIA pNfH bridge)</div>`;
}
"""
