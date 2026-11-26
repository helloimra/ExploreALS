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
  const curFv = ((document.getElementById('rep-filter')||{}).value||'ALL');
  const curKey = repMode + '|' + curFv;
  const nodes = [
    {x:6,  y:12, w:148, h:46, title:'1. Open Datasets (43)', sub:'677 MB · SHA-256',     act:"datasets|ALL"},
    {x:172,y:12, w:148, h:46, title:'2. Cohort Loaders',     sub:'12 Cohort Parsers',    act:"runs|COHORT"},
    {x:338,y:12, w:148, h:46, title:'3. Analysis Pipeline',  sub:'8 Lead + 51 Runs',     act:"runs|ALL"},
    {x:78, y:96, w:162, h:46, title:'4. 204 Records',        sub:'100% SHA-256 + OLS',   act:"evidence|ALL"},
    {x:260,y:96, w:164, h:46, title:'5. Verification Suite', sub:'Citations + Off-Tgt',  act:"runs|SYNTH"}
  ];
  const rects = nodes.map(n => {
    const on = n.act === curKey;
    return `
    <g data-rep-dag="${n.act}" class="cursor-pointer" role="button" tabindex="0" aria-pressed="${on?'true':'false'}" aria-label="Filter workbench: ${n.title}">
      <rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="6" fill="${on?'var(--content)':'var(--background)'}" stroke="var(--primary)" stroke-width="${on?'2.2':'1.4'}"/>
      <text x="${n.x+n.w/2}" y="${n.y+20}" text-anchor="middle" font-size="12.5" font-weight="600" fill="var(--foreground)">${n.title}</text>
      <text x="${n.x+n.w/2}" y="${n.y+37}" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">${n.sub}</text>
    </g>`;
  }).join('');
  box.innerHTML = `<svg viewBox="0 0 492 154" class="w-full h-auto" role="img" aria-label="5-stage computational provenance workflow">
    <defs><marker id="dag-arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 7 4 L 0 7 z" fill="var(--muted-foreground)"/></marker></defs>
    <line x1="154" y1="35" x2="169" y2="35" stroke="var(--muted-foreground)" stroke-width="1.5" marker-end="url(#dag-arr)"/>
    <line x1="320" y1="35" x2="335" y2="35" stroke="var(--muted-foreground)" stroke-width="1.5" marker-end="url(#dag-arr)"/>
    <path d="M 412 58 L 412 76 L 159 76 L 159 93" fill="none" stroke="var(--muted-foreground)" stroke-width="1.4" stroke-dasharray="3,3" marker-end="url(#dag-arr)"/>
    <line x1="240" y1="119" x2="257" y2="119" stroke="var(--muted-foreground)" stroke-width="1.5" marker-end="url(#dag-arr)"/>
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
      <td class="py-2 px-2"><div class="font-semibold text-[var(--foreground)]">${esc(o.name)}</div><div class="mt-0.5">${dsPills}</div></td>
      <td class="py-2 px-2 text-[var(--muted-foreground)] leading-relaxed">${esc(o.rule)}</td>
      <td class="py-2 px-2 font-mono text-xs text-[var(--foreground)] leading-relaxed">${esc(o.formula)}</td>
    </tr>`;
  }).join('');
}

function getRepFilterDefs(mode){
  if(mode === 'runs'){
    const runs = (typeof DATA_RUNS !== 'undefined') ? DATA_RUNS : [];
    const flagCnt = runs.filter(r => r.flag).length;
    const cohortCnt = runs.filter(r => r.grp.startsWith('Cohort Re-Analysis') || r.grp.startsWith('Data Staging')).length;
    const biophysCnt = runs.filter(r => r.grp.startsWith('3D & PK-PD')).length;
    const synthCnt = runs.filter(r => r.grp.startsWith('Multi-Omic') || r.grp.startsWith('Hybridization') || r.grp.startsWith('Portfolio')).length;
    return {
      lbl: 'Workflow:',
      opts: [
        {v:'ALL', opt:`Workflow: All (${runs.length})`, pill:`Workflow: All (${runs.length})`},
        {v:'FLAGSHIP', opt:`Flagship Monograph Reproducers (${flagCnt})`, pill:`Flagship (${flagCnt})`},
        {v:'COHORT', opt:`Cohort Re-Analysis · Splicing, snRNA & Proteomics (${cohortCnt})`, pill:`Cohort Re-Analysis (${cohortCnt})`},
        {v:'BIOPHYS', opt:`3D Biophysics, Isoforms & PK-PD (${biophysCnt})`, pill:`3D Biophysics & PK-PD (${biophysCnt})`},
        {v:'SYNTH', opt:`Multi-Omic Triage, Alignment & Synthesis (${synthCnt})`, pill:`Triage & Synthesis (${synthCnt})`}
      ]
    };
  }
  if(mode === 'datasets'){
    const ds = (typeof DATA_DATASETS !== 'undefined') ? DATA_DATASETS : [];
    const aCnt = ds.filter(d => d.tier === 'TIER_A_OPEN_REDISTRIBUTABLE').length;
    const bCnt = ds.filter(d => d.tier === 'TIER_B_PUBLISHER_HTTPS_FETCH').length;
    const cCnt = ds.filter(d => d.tier === 'TIER_C_DUA_OR_BASELINE').length;
    return {
      lbl: 'Legal Tier:',
      opts: [
        {v:'ALL', opt:`Legal Tier: All (${ds.length})`, pill:`Legal Tier: All (${ds.length})`},
        {v:'TIER_A_OPEN_REDISTRIBUTABLE', opt:`Tier A · Open Redistributable (${aCnt})`, pill:`Tier A · Open (${aCnt})`},
        {v:'TIER_B_PUBLISHER_HTTPS_FETCH', opt:`Tier B · Direct Publisher/EuropePMC HTTPS (${bCnt})`, pill:`Tier B · HTTPS (${bCnt})`},
        {v:'TIER_C_DUA_OR_BASELINE', opt:`Tier C · Registered Synapse Access (${cCnt})`, pill:`Tier C · Synapse (${cCnt})`}
      ]
    };
  }
  const ev = (typeof DATA_FORMULAS !== 'undefined') ? DATA_FORMULAS : [];
  const dsCnt = ev.filter(f => f.anc === 'STAGED_DATASET').length;
  const apiCnt = ev.filter(f => f.anc === 'CACHED_API_SNAPSHOT').length;
  const modCnt = ev.filter(f => f.anc === 'DETERMINISTIC_MODEL_OUTPUT').length;
  return {
    lbl: 'Anchor Type:',
    opts: [
      {v:'ALL', opt:`Anchor Type: All (${ev.length})`, pill:`Anchor Type: All (${ev.length})`},
      {v:'STAGED_DATASET', opt:`Dataset File Anchor (${dsCnt})`, pill:`Dataset File Anchor (${dsCnt})`},
      {v:'CACHED_API_SNAPSHOT', opt:`API Snapshot Anchor (${apiCnt})`, pill:`API Snapshot Anchor (${apiCnt})`},
      {v:'DETERMINISTIC_MODEL_OUTPUT', opt:`Model Output Anchor (${modCnt})`, pill:`Model Output Anchor (${modCnt})`}
    ]
  };
}

function populateRepFilterOptions(){
  const sel = document.getElementById('rep-filter');
  if(!sel) return;
  const defs = getRepFilterDefs(repMode);
  sel.innerHTML = defs.opts.map(o => `<option value="${esc(o.v)}">${esc(o.opt)}</option>`).join('');
}

function renderRepSubfilterBar(){
  const bar = document.getElementById('rep-subfilter-bar');
  const lbl = document.getElementById('rep-subfilter-lbl');
  if(!bar) return;
  const defs = getRepFilterDefs(repMode);
  if(lbl) lbl.textContent = defs.lbl;
  const fv = ((document.getElementById('rep-filter')||{}).value||'ALL');
  bar.innerHTML = defs.opts.map(o => {
    const on = o.v === fv;
    const cls = on
      ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)] font-semibold'
      : 'bg-[var(--background)] text-[var(--muted-foreground)] border-[var(--border)] hover:text-[var(--foreground)] hover:border-[var(--primary)]';
    return `<button type="button" data-rep-subfilter="${esc(o.v)}" aria-pressed="${on?'true':'false'}" class="px-2 py-0.5 rounded border font-mono text-xs cursor-pointer ${cls}">${esc(o.pill)}</button>`;
  }).join('');
}

function setRepMode(mode, keepFilter=false, skipRender=false){
  repMode = mode;
  document.querySelectorAll('.rep-mode-btn').forEach(b => {
    const on = b.getAttribute('data-rep-mode') === mode;
    b.className = 'rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer ' + (on ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)]' : 'bg-[var(--background)] text-[var(--foreground)] border-[var(--border)]');
  });
  if(!keepFilter) populateRepFilterOptions();
  if(!skipRender) renderReplicationWorkbench();
}

function formatRepMult(f){
  if(!f.mp) return '';
  const mf = String(f.mfam || '');
  if(/bonferroni/i.test(mf)) return `Bonf_p=${f.mp}`;
  if(/fdr/i.test(mf)) return `FDR=${f.mp}`;
  return `mult_p=${f.mp}`;
}

function hasPositiveRep3D(f){
  const arel = String(f.arel || '');
  if(/\.(?:cif|pdb)(?:\.gz)?$/i.test(arel) || /(?:^|\/)(?:pdb|afdb|phase2_pdb|phase3b_pdb|phase4_pdb)(?:\/|$)/i.test(arel)) return true;
  const meta = String(f.con || '') + ' ' + String(f.mod || '') + ' ' + String(f.est || '');
  return /\bPDB[:\s_]+[0-9][A-Za-z0-9]{3}\b/.test(meta) || /\bAF-[A-Z0-9]{6,10}-F\d+\b/.test(meta) || /\b(?:cryo-em|x-ray\s+crystal|alphafold)\b/i.test(meta);
}

function formatRepPDisp(f){
  const parts = [f.up ? `p=${f.up}` : '', f.cp ? `cov_adj_p=${f.cp}` : '', formatRepMult(f)].filter(Boolean);
  if(parts.length) return parts.join(' · ');
  const mf = String(f.mfam || '');
  if(f.cls === 'PRIMARY_BAYESIAN_SPLICING_RECOMPUTE' || /majiq\s+bayesian/i.test(mf)) return 'N/A (Bayesian MAJIQ)';
  if(f.cls === 'STRUCTURAL_OR_MECHANISTIC_MODEL_PRIOR'){
    return hasPositiveRep3D(f) ? 'N/A (3D / Model)' : 'N/A (Model Prior)';
  }
  if(f.cls === 'DETERMINISTIC_MODEL_PRIOR') return 'N/A (Model / Scan)';
  if(f.cls === 'POPULATION_REFERENCE_METRIC') return 'N/A (Ref Metric)';
  if(f.cls === 'DESCRIPTIVE_PK_OR_3D_MEASUREMENT'){
    const dBlob = String(f.con || '') + ' ' + String(f.mod || '') + ' ' + String(f.est || '');
    if(hasPositiveRep3D(f)){
      if(/\b(?:unbound\s+csf|cu,csf|cmax|occupancy)\b/i.test(dBlob)) return 'N/A (3D / PK)';
      if(/\b(?:binomial|heterotetramer|poisoned)\b/i.test(dBlob)) return 'N/A (3D / Model)';
      return 'N/A (3D Structure)';
    }
    if(/\b(?:unbound|cu,plasma|cu,csf|cu,brain|cu,cns|fup\b|plasma\s+pk|csf\s+ceftriaxone|csf\/serum|csf.*ec50|csf\s+concentration|chembl\d+\s+binding|kinobead|nanobret|talke\s+1997|lumbar\s+csf)\b/i.test(dBlob)) return 'N/A (PK / Binding)';
    if(/\b(?:alphagenome|avi_phred|lof\s+constraint|loeuf|depmap)\b/i.test(dBlob)) return 'N/A (Ref Metric)';
    return 'See contrast details';
  }
  return 'See contrast details';
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
      if(fv === 'COHORT' && !r.grp.startsWith('Cohort Re-Analysis') && !r.grp.startsWith('Data Staging')) return false;
      if(fv === 'BIOPHYS' && !r.grp.startsWith('3D & PK-PD')) return false;
      if(fv === 'SYNTH' && !r.grp.startsWith('Multi-Omic') && !r.grp.startsWith('Hybridization') && !r.grp.startsWith('Portfolio')) return false;
      if(!q) return true;
      const rIds = r.cands ? r.cands.split(';').filter(Boolean) : [];
      return queryMatchesIdOrText(rIds, q, r.id+' '+r.grp+' '+r.script+' '+r.ds+' '+r.cands+' '+r.sum);
    });
    if(!items.some(x=>x.id===selectedRepKey) && items.length) selectedRepKey = items[0].id;
    document.getElementById('rep-count').textContent = `${items.length} / ${DATA_RUNS.length}`;
    th.innerHTML = '<tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]"><th class="py-2 px-2.5 font-medium">Run ID</th><th class="py-2 px-2 font-medium">Workflow / Monograph</th><th class="py-2 px-2 font-medium">Canonical Script</th><th class="py-2 px-2 font-medium">Inputs</th></tr>';
    const emptyRow = '<tr><td colspan="4" class="py-6 px-4 text-center text-[var(--muted-foreground)]">No matching items. <button type="button" data-reset-rep="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></td></tr>';
    tb.innerHTML = items.length ? items.map(r => {
      const sel = r.id === selectedRepKey;
      const badge = r.flag ? '<span class="px-1 rounded border border-[var(--success)] text-[var(--success)] font-mono text-xs mr-1">Flagship</span>' : '';
      return `<tr data-rep-select="${esc(r.id)}" tabindex="0" aria-selected="${sel?'true':'false'}" class="cursor-pointer hover:bg-[var(--background)] ${sel?'bg-[var(--content)] border-l-4 border-l-[var(--primary)]':''}">
        <td class="py-1.5 px-2.5 font-mono font-semibold whitespace-nowrap">${esc(r.id)}</td>
        <td class="py-1.5 px-2">${badge}<span class="text-[var(--muted-foreground)]">${esc(r.grp)}</span></td>
        <td class="py-1.5 px-2 font-mono text-xs break-words">${esc(r.script.split(';')[0].split('/').slice(-1)[0])}${r.script.includes(';') ? ' (+' + (r.script.split(';').filter(Boolean).length - 1) + ')' : ''}</td>
        <td class="py-1.5 px-2 font-mono text-xs text-[var(--muted-foreground)] whitespace-nowrap">${r.ds ? r.ds.split(';').length + ' DS' : 'Snapshot'}</td>
      </tr>`;
    }).join('') : emptyRow;
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
    const emptyDsRow = '<tr><td colspan="4" class="py-6 px-4 text-center text-[var(--muted-foreground)]">No matching datasets. <button type="button" data-reset-rep="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></td></tr>';
    tb.innerHTML = items.length ? items.map(d => {
      const sel = d.id === selectedRepKey;
      const tShort = d.tier.startsWith('TIER_A') ? '<span class="text-[var(--success)]">Tier A · Open</span>' : (d.tier.startsWith('TIER_B') ? '<span class="text-[var(--primary)]">Tier B · HTTPS</span>' : '<span class="text-[var(--warning)]">Tier C · Synapse</span>');
      return `<tr data-rep-select="${esc(d.id)}" tabindex="0" aria-selected="${sel?'true':'false'}" class="cursor-pointer hover:bg-[var(--background)] ${sel?'bg-[var(--content)] border-l-4 border-l-[var(--primary)]':''}">
        <td class="py-1.5 px-2.5 font-mono font-semibold whitespace-nowrap">${esc(d.id)}</td>
        <td class="py-1.5 px-2 text-[var(--muted-foreground)]">${esc(d.dom)} &middot; <span class="font-mono">${esc(d.mb)}</span></td>
        <td class="py-1.5 px-2 font-mono text-xs whitespace-nowrap">${tShort}</td>
        <td class="py-1.5 px-2 font-mono text-xs text-[var(--muted-foreground)]">${esc(d.sha.slice(0,10))}&hellip;</td>
      </tr>`;
    }).join('') : emptyDsRow;
  } else {
    items = DATA_FORMULAS.filter(f => {
      if(fv !== 'ALL' && f.anc !== fv) return false;
      if(!q) return true;
      return queryMatchesIdOrText([f.cid], q, f.eid+' '+f.cid+' '+f.run+' '+f.unit+' '+f.con+' '+f.mod+' '+f.sha);
    });
    if(!items.some(x=>x.eid===selectedRepKey) && items.length) selectedRepKey = items[0].eid;
    document.getElementById('rep-count').textContent = `${items.length} / ${DATA_FORMULAS.length}`;
    th.innerHTML = '<tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]"><th class="py-2 px-2.5 font-medium">Evidence</th><th class="py-2 px-2 font-medium">Cand &middot; Run</th><th class="py-2 px-2 font-medium">Unit (Donor N)</th><th class="py-2 px-2 font-medium">p / Multiplicity</th></tr>';
    const emptyEvRow = '<tr><td colspan="4" class="py-6 px-4 text-center text-[var(--muted-foreground)]">No matching evidence contrasts. <button type="button" data-reset-rep="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></td></tr>';
    tb.innerHTML = items.length ? items.map(f => {
      const sel = f.eid === selectedRepKey;
      const pDisp = formatRepPDisp(f);
      return `<tr data-rep-select="${esc(f.eid)}" tabindex="0" aria-selected="${sel?'true':'false'}" class="cursor-pointer hover:bg-[var(--background)] ${sel?'bg-[var(--content)] border-l-4 border-l-[var(--primary)]':''}">
        <td class="py-1.5 px-2.5 font-mono font-semibold whitespace-nowrap">${esc(f.eid)}</td>
        <td class="py-1.5 px-2 font-mono text-xs whitespace-nowrap"><span class="text-[var(--primary)]">${esc(f.cid || 'Portfolio')}</span> &middot; ${esc(f.run)}</td>
        <td class="py-1.5 px-2 font-mono text-xs text-[var(--muted-foreground)]">${esc(f.unit)} (${esc(f.ndon||'N/A')})</td>
        <td class="py-1.5 px-2 font-mono text-xs whitespace-nowrap">${esc(pDisp)}</td>
      </tr>`;
    }).join('') : emptyEvRow;
  }
  renderRepSubfilterBar();
  renderRepDag();
  renderRepInspector(items.length === 0);
  if(typeof scrollRowInPane === 'function') scrollRowInPane('rep-tbody', 'tr[data-rep-select="'+selectedRepKey+'"]');
}
"""
