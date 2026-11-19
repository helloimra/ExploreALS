"""Client-side Tab 4 (4. Replication) Script & Checksum Provenance DAG, Cohort Overlap Matrix, Master-Detail Workbench & CSV/JSON Exporter."""
from __future__ import annotations

REPLICATION_TAB_JS = r"""
let repMode = 'runs';
let selectedRepKey = 'FLAGSHIP-EALS-030';
let repReturnDossier = '';
let repReturnTab = 'dossiers';

function renderRepDag(){
  const box = document.getElementById('rep-dag-box');
  if(!box) return;
  const nodes = [
    {x:6,  y:12, w:132, h:46, title:'1. Open Datasets (40)', sub:'673.4 MB · SHA-256', act:"datasets|ALL"},
    {x:164,y:12, w:132, h:46, title:'2. Cohort Loaders',     sub:'src/carbon_als (12)', act:"runs|FLAGSHIP"},
    {x:322,y:12, w:132, h:46, title:'3. Python DAG (50)',    sub:'60 Portable Scripts', act:"runs|ALL"},
    {x:84, y:96, w:140, h:46, title:'4. 194 Contrasts',      sub:'100% SHA-64 + OLS',   act:"evidence|ALL"},
    {x:254,y:96, w:146, h:46, title:'5. 5-Gate Verifier',    sub:'Citations + Off-Tgt', act:"runs|FLAGSHIP"}
  ];
  const rects = nodes.map(n => `
    <g data-rep-dag="${n.act}" class="cursor-pointer" role="button" tabindex="0" aria-label="Filter workbench: ${n.title}">
      <rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="6" fill="var(--background)" stroke="var(--primary)" stroke-width="1.4"/>
      <text x="${n.x+n.w/2}" y="${n.y+20}" text-anchor="middle" font-size="12.5" font-weight="600" fill="var(--foreground)">${n.title}</text>
      <text x="${n.x+n.w/2}" y="${n.y+37}" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">${n.sub}</text>
    </g>`).join('');
  box.innerHTML = `<svg viewBox="0 0 460 154" class="w-full h-auto" role="img" aria-label="5-stage script and checksum computational provenance DAG">
    <defs><marker id="dag-arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 7 4 L 0 7 z" fill="var(--muted-foreground)"/></marker></defs>
    <line x1="138" y1="35" x2="161" y2="35" stroke="var(--muted-foreground)" stroke-width="1.5" marker-end="url(#dag-arr)"/>
    <line x1="296" y1="35" x2="319" y2="35" stroke="var(--muted-foreground)" stroke-width="1.5" marker-end="url(#dag-arr)"/>
    <path d="M 388 58 L 388 76 L 154 76 L 154 93" fill="none" stroke="var(--muted-foreground)" stroke-width="1.4" stroke-dasharray="3,3" marker-end="url(#dag-arr)"/>
    <line x1="224" y1="119" x2="251" y2="119" stroke="var(--muted-foreground)" stroke-width="1.5" marker-end="url(#dag-arr)"/>
    ${rects}
  </svg>`;
}

function renderRepOverlap(){
  const tb = document.getElementById('rep-overlap-tbody');
  if(!tb || typeof DATA_OVERLAP === 'undefined') return;
  tb.innerHTML = DATA_OVERLAP.map(o => {
    const dsPills = o.ds.split(';').map(d => {
      const base = d.split(':')[0];
      return `<button type="button" data-open-rep-ds="${esc(base)}" class="text-[var(--link)] hover:underline font-mono text-xs cursor-pointer mr-1">${esc(d)}</button>`;
    }).join('');
    return `<tr class="align-top">
      <td class="py-1.5 px-2"><div class="font-semibold text-[var(--foreground)]">${esc(o.name)}</div><div class="mt-0.5">${dsPills}</div></td>
      <td class="py-1.5 px-2 text-[var(--muted-foreground)] leading-snug">${esc(o.rule)}</td>
      <td class="py-1.5 px-2 font-mono text-xs text-[var(--foreground)] leading-snug">${esc(o.formula)}</td>
    </tr>`;
  }).join('');
}

function populateRepFilterOptions(){
  const sel = document.getElementById('rep-filter');
  if(!sel) return;
  if(repMode === 'runs'){
    sel.innerHTML = '<option value="ALL">Stage: All (58)</option><option value="FLAGSHIP">8 Flagship Monograph Reproducers</option><option value="PHASE1">Phase 1 · Cohort Batches 1–6</option><option value="PHASE2">Phase 2 · Cis/Structural/PK-PD</option><option value="PHASE34">Phase 3 &amp; 4 · De Novo, Off-Target &amp; Synthesis</option>';
  } else if(repMode === 'datasets'){
    sel.innerHTML = '<option value="ALL">Legal Tier: All (40)</option><option value="TIER_A_OPEN_REDISTRIBUTABLE">Tier A · Open Redistributable (CC0 / CC-BY)</option><option value="TIER_B_PUBLISHER_HTTPS_FETCH">Tier B · Direct Publisher/EuropePMC HTTPS</option><option value="TIER_C_DUA_OR_BASELINE">Tier C · Registered Synapse Access</option>';
  } else {
    sel.innerHTML = '<option value="ALL">Anchor Type: All (194)</option><option value="STAGED_DATASET">Staged Open Dataset (130)</option><option value="CACHED_API_SNAPSHOT">Cached API Snapshot (56)</option><option value="DETERMINISTIC_MODEL_OUTPUT">Deterministic Model Output (8)</option>';
  }
}

function setRepMode(mode, keepFilter=false){
  repMode = mode;
  document.querySelectorAll('.rep-mode-btn').forEach(b => {
    const on = b.getAttribute('data-rep-mode') === mode;
    b.className = 'rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer ' + (on ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)]' : 'bg-[var(--background)] text-[var(--foreground)] border-[var(--border)]');
  });
  if(!keepFilter) populateRepFilterOptions();
  renderReplicationWorkbench();
}

function renderReplicationWorkbench(){
  if(typeof DATA_RUNS === 'undefined') return;
  const q = ((document.getElementById('rep-search')||{}).value||'').trim();
  const fv = ((document.getElementById('rep-filter')||{}).value||'ALL');
  const th = document.getElementById('rep-thead');
  const tb = document.getElementById('rep-tbody');
  if(!th || !tb) return;

  let items = [];
  if(repMode === 'runs'){
    items = DATA_RUNS.filter(r => {
      if(fv === 'FLAGSHIP' && !r.flag) return false;
      if(fv === 'PHASE1' && !r.grp.startsWith('Batch') && !r.grp.startsWith('Stage 1')) return false;
      if(fv === 'PHASE2' && !r.grp.startsWith('Stage 2')) return false;
      if(fv === 'PHASE34' && !r.grp.startsWith('Stage 3') && !r.grp.startsWith('Stage 4')) return false;
      if(!q) return true;
      const rIds = r.cands ? r.cands.split(';').filter(Boolean) : [];
      return queryMatchesIdOrText(rIds, q, r.id+' '+r.grp+' '+r.script+' '+r.ds+' '+r.cands+' '+r.sum);
    });
    if(!items.some(x=>x.id===selectedRepKey) && items.length) selectedRepKey = items[0].id;
    document.getElementById('rep-count').textContent = `${items.length} / ${DATA_RUNS.length}`;
    th.innerHTML = '<tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]"><th class="py-2 px-2.5 font-medium">Run ID</th><th class="py-2 px-2 font-medium">Stage / Monograph</th><th class="py-2 px-2 font-medium">Canonical Script</th><th class="py-2 px-2 font-medium">Inputs</th></tr>';
    tb.innerHTML = items.map(r => {
      const sel = r.id === selectedRepKey;
      const badge = r.flag ? '<span class="px-1 rounded border border-[var(--success)] text-[var(--success)] font-mono text-xs mr-1">Flagship</span>' : '';
      return `<tr data-rep-select="${esc(r.id)}" tabindex="0" aria-selected="${sel?'true':'false'}" class="cursor-pointer hover:bg-[var(--background)] ${sel?'bg-[var(--content)] border-l-4 border-l-[var(--primary)]':''}">
        <td class="py-1.5 px-2.5 font-mono font-semibold whitespace-nowrap">${esc(r.id)}</td>
        <td class="py-1.5 px-2">${badge}<span class="text-[var(--muted-foreground)]">${esc(r.grp)}</span></td>
        <td class="py-1.5 px-2 font-mono text-xs break-words">${esc(r.script.split(';')[0].split('/').slice(-1)[0])}</td>
        <td class="py-1.5 px-2 font-mono text-xs text-[var(--muted-foreground)] whitespace-nowrap">${r.ds ? r.ds.split(';').length + ' DS' : 'Snapshot'}</td>
      </tr>`;
    }).join('');
  } else if(repMode === 'datasets'){
    items = DATA_DATASETS.filter(d => {
      if(fv !== 'ALL' && d.tier !== fv) return false;
      if(!q) return true;
      const dIds = d.cands ? d.cands.split(';').filter(Boolean) : [];
      return queryMatchesIdOrText(dIds, q, d.id+' '+d.dom+' '+d.acc+' '+d.lic+' '+d.sha+' '+d.cands+' '+d.desc);
    });
    if(!items.some(x=>x.id===selectedRepKey) && items.length) selectedRepKey = items[0].id;
    document.getElementById('rep-count').textContent = `${items.length} / ${DATA_DATASETS.length}`;
    th.innerHTML = '<tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]"><th class="py-2 px-2.5 font-medium">Dataset ID</th><th class="py-2 px-2 font-medium">Domain &amp; Size</th><th class="py-2 px-2 font-medium">Legal Tier</th><th class="py-2 px-2 font-medium">SHA-256</th></tr>';
    tb.innerHTML = items.map(d => {
      const sel = d.id === selectedRepKey;
      const tShort = d.tier.startsWith('TIER_A') ? '<span class="text-[var(--success)]">Tier A · Open</span>' : (d.tier.startsWith('TIER_B') ? '<span class="text-[var(--primary)]">Tier B · HTTPS</span>' : '<span class="text-[var(--warning)]">Tier C · Synapse</span>');
      return `<tr data-rep-select="${esc(d.id)}" tabindex="0" aria-selected="${sel?'true':'false'}" class="cursor-pointer hover:bg-[var(--background)] ${sel?'bg-[var(--content)] border-l-4 border-l-[var(--primary)]':''}">
        <td class="py-1.5 px-2.5 font-mono font-semibold whitespace-nowrap">${esc(d.id)}</td>
        <td class="py-1.5 px-2 text-[var(--muted-foreground)]">${esc(d.dom)} &middot; <span class="font-mono">${esc(d.mb)}</span></td>
        <td class="py-1.5 px-2 font-mono text-xs whitespace-nowrap">${tShort}</td>
        <td class="py-1.5 px-2 font-mono text-xs text-[var(--muted-foreground)]">${esc(d.sha.slice(0,10))}&hellip;</td>
      </tr>`;
    }).join('');
  } else {
    items = DATA_FORMULAS.filter(f => {
      if(fv !== 'ALL' && f.anc !== fv) return false;
      if(!q) return true;
      return queryMatchesIdOrText([f.cid], q, f.eid+' '+f.cid+' '+f.run+' '+f.unit+' '+f.con+' '+f.mod+' '+f.sha);
    });
    if(!items.some(x=>x.eid===selectedRepKey) && items.length) selectedRepKey = items[0].eid;
    document.getElementById('rep-count').textContent = `${items.length} / ${DATA_FORMULAS.length}`;
    th.innerHTML = '<tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]"><th class="py-2 px-2.5 font-medium">Evidence</th><th class="py-2 px-2 font-medium">Cand &middot; Run</th><th class="py-2 px-2 font-medium">Unit (Donor N)</th><th class="py-2 px-2 font-medium">p / Multiplicity</th></tr>';
    tb.innerHTML = items.map(f => {
      const sel = f.eid === selectedRepKey;
      const pDisp = [f.up?`p=${f.up}`:'', f.cp?`adj_p=${f.cp}`:'', f.mp?`FDR=${f.mp}`:''].filter(Boolean).join(' · ') || 'Ref/3D';
      return `<tr data-rep-select="${esc(f.eid)}" tabindex="0" aria-selected="${sel?'true':'false'}" class="cursor-pointer hover:bg-[var(--background)] ${sel?'bg-[var(--content)] border-l-4 border-l-[var(--primary)]':''}">
        <td class="py-1.5 px-2.5 font-mono font-semibold whitespace-nowrap">${esc(f.eid)}</td>
        <td class="py-1.5 px-2 font-mono text-xs whitespace-nowrap"><span class="text-[var(--primary)]">${esc(f.cid)}</span> &middot; ${esc(f.run)}</td>
        <td class="py-1.5 px-2 font-mono text-xs text-[var(--muted-foreground)]">${esc(f.unit)} (${esc(f.ndon||'—')})</td>
        <td class="py-1.5 px-2 font-mono text-xs whitespace-nowrap">${esc(pDisp)}</td>
      </tr>`;
    }).join('');
  }
  renderRepInspector();
}
"""
