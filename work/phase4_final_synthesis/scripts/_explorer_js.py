"""Client-side interactive logic for the ExploreALS v1.1 Generative UI Explorer (pure semantic CSS vars + vector SVG)."""
from __future__ import annotations

EXPLORER_JS_BODY = """
const TRL_NUM = {TRL_6_PH2B_SUBGROUP_BIOLOGIC:6,TRL_5_HUMAN_ALS_PK_PD_PROVEN:5,TRL_4_ACTIVE_PH1_CLASS_OR_NCE:4,TRL_3_PRECLINICAL_SSO_COORDINATE:3,TRL_2_PRECLINICAL_MODALITY_DISCOVERY:2,TRL_1_TARGET_TOOL_PROBE_WATCHLIST:1,PROTOCOL_COMPANION_NA:0};
const NYGC_GENE_TO_ID = {ATG4B:'EALS-034',KALRN:'EALS-035',PTPRT:'EALS-036',CELF5:'EALS-037',PRUNE2:'EALS-038',PFKP:'EALS-039',TRAPPC12:'EALS-040',ELK1:'EALS-041',DLGAP1:'EALS-042'};
let selectedId = 'EALS-030';
let selectedIvOrd = 5;
let activeTab = 'home';
let activeQuick = 'ALL';
let activeEpi = 'ALL';
let activeLens = 'ALL';
let activeUpdCat = 'ALL';
let dossierFromPortfolio = false;
let pendingDossierSec = '';
let isRestoringHistory = false;
let historyInitialized = false;
let lastSelHidden = false;
const expandedDetailGates = {};

function valOf(id, fb=''){ const el = document.getElementById(id); return el ? String(el.value || '') : fb; }
function setValOf(id, v){ const el = document.getElementById(id); if(el && v !== undefined && v !== null) el.value = v; }

function defaultHashForCurrentState(){
  if(activeTab === 'home'){
    const uq = valOf('upd-search').trim();
    if(uq) return '#updates/' + encodeURIComponent(uq);
    if(activeUpdCat !== 'ALL') return '#updates';
    return '#home';
  }
  if(activeTab === 'portfolio') return '#portfolio';
  if(activeTab === 'dossiers') return '#dossier/' + encodeURIComponent((typeof dossierId !== 'undefined' && dossierId) ? dossierId : (selectedId || 'EALS-030'));
  if(activeTab === 'intervals'){
    const iq = valOf('iv-search').trim();
    return iq ? '#intervals/' + encodeURIComponent(iq) : '#intervals';
  }
  if(activeTab === 'replication'){
    const rq = valOf('rep-search').trim();
    if(typeof repMode !== 'undefined' && repMode === 'evidence' && rq) return '#replication/cand/' + encodeURIComponent(rq);
    if(typeof selectedRepKey !== 'undefined' && selectedRepKey && selectedRepKey !== 'FLAGSHIP-EALS-030') return '#replication/' + encodeURIComponent(selectedRepKey);
    return '#replication';
  }
  return '#home';
}

function buildHistorySnapshot(targetHash){
  const dr = document.getElementById('contrasts-drawer');
  const ivL = document.getElementById('iv-leads');
  return {
    tab: activeTab, selectedId: selectedId,
    dossierId: (typeof dossierId !== 'undefined' ? dossierId : selectedId),
    dossierFromPortfolio: dossierFromPortfolio,
    dossierSlice: (typeof dossierSlice !== 'undefined' ? dossierSlice : 'ALL'),
    dossierLens: (typeof dossierLens !== 'undefined' ? dossierLens : 'ALL'),
    activeQuick: activeQuick, activeEpi: activeEpi, activeLens: activeLens,
    pSearch: valOf('p-search'), pOrigin: valOf('p-origin','ALL'), pDec: valOf('p-dec','ALL'), pTier: valOf('p-tier','ALL'), pSort: valOf('p-sort','rank'),
    contrastsOpen: Boolean(dr && dr.open),
    activeUpdCat: activeUpdCat, updSearch: valOf('upd-search'),
    ivSearch: valOf('iv-search'), ivStatus: valOf('iv-status','ALL'), ivOrigin: valOf('iv-origin','ALL'), ivLeads: Boolean(ivL && ivL.checked), selectedIvOrd: selectedIvOrd,
    repMode: (typeof repMode !== 'undefined' ? repMode : 'runs'),
    selectedRepKey: (typeof selectedRepKey !== 'undefined' ? selectedRepKey : 'FLAGSHIP-EALS-030'),
    repSearch: valOf('rep-search'), repFilter: valOf('rep-filter','ALL'),
    repReturnDossier: (typeof repReturnDossier !== 'undefined' ? repReturnDossier : ''),
    repReturnTab: (typeof repReturnTab !== 'undefined' ? repReturnTab : 'dossiers'),
    hash: targetHash
  };
}

function commitHistory(mode='push', explicitHash=''){
  if(isRestoringHistory || mode === 'none') return;
  try {
    if(location.protocol !== 'http:' && location.protocol !== 'https:') return;
    const nextHash = explicitHash || defaultHashForCurrentState();
    const curHash = (!location.hash || location.hash === '#') ? '#home' : location.hash;
    const url = (nextHash === '#home' && (!location.hash || location.hash === '#'))
      ? (location.pathname + location.search)
      : nextHash;
    const snap = buildHistorySnapshot(nextHash);
    if(!historyInitialized || mode === 'replace' || curHash === nextHash){
      history.replaceState(snap, '', url);
      historyInitialized = true;
    } else {
      history.pushState(snap, '', url);
      historyInitialized = true;
    }
  } catch(_e) {}
}

function updCatBadge(cat){
  if(cat==='CLINICAL_TRIAL') return '<span class="px-1.5 py-0.5 rounded border border-[var(--success)] text-[var(--success)] font-mono font-semibold text-xs whitespace-nowrap">&bull; Clinical / Trial</span>';
  if(cat==='LITERATURE_INGESTION') return '<span class="px-1.5 py-0.5 rounded border border-[var(--primary)] text-[var(--primary)] font-mono font-semibold text-xs whitespace-nowrap">&#9670; New Literature</span>';
  return '<span class="px-1.5 py-0.5 rounded border border-[var(--warning)] text-[var(--warning)] font-mono font-semibold text-xs whitespace-nowrap">&#9671; Model / Re-Analysis</span>';
}
function updBorderCls(cat){
  if(cat==='CLINICAL_TRIAL') return 'border-l-[var(--success)]';
  if(cat==='LITERATURE_INGESTION') return 'border-l-[var(--primary)]';
  return 'border-l-[var(--warning)]';
}
function renderUpdatesLog(){
  const feed = document.getElementById('upd-feed');
  if(!feed || typeof DATA_UPDATES === 'undefined') return;
  document.querySelectorAll('[data-upd-cat]').forEach(b => {
    const on = b.getAttribute('data-upd-cat') === activeUpdCat;
    b.className = 'px-2 py-1 rounded border font-mono text-xs cursor-pointer ' + (on ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)] font-semibold' : 'bg-[var(--background)] text-[var(--muted-foreground)] border-[var(--border)] hover:text-[var(--foreground)] hover:border-[var(--primary)]');
  });
  const qEl = document.getElementById('upd-search');
  const q = (qEl ? qEl.value : '').trim();
  const rows = DATA_UPDATES.filter(u => {
    if(activeUpdCat !== 'ALL' && u.cat !== activeUpdCat) return false;
    if(!q) return true;
    const cNames = u.ids.map(aid => {
      const cp = DATA_PORT.find(x => x.id === aid);
      const sn = DATA_SUB.find(x => x.id === aid);
      return (cp ? cp.name + ' ' + (cp.sym || '') : '') + ' ' + (sn ? sn.gene : '');
    }).join(' ');
    const hay = [u.id || '', u.tag || '', u.dt, u.cat, u.ids.join(' '), cNames, u.imp, u.hdr, u.pre, u.post, u.cons, u.srcs.join(' '), u.ancs.join(' ')].join(' ');
    return queryMatchesIdOrText(u.ids, q, hay);
  });
  const cntEl = document.getElementById('upd-count');
  if(cntEl) cntEl.textContent = `${rows.length} / ${DATA_UPDATES.length}`;
  feed.innerHTML = rows.length ? rows.map(u => {
    const gCtx = u.ids.find(x => x !== 'PORTFOLIO_WIDE' && !x.includes('.')) || 'EALS-030';
    const makeIdPill = aid => {
      if(aid === 'PORTFOLIO_WIDE') return '<span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">All 52 Hypotheses</span>';
      if(aid.includes('.')){
        const sn = DATA_SUB.find(x => x.id === aid);
        return `<button type="button" data-open-dossier="${esc(aid)}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono font-semibold text-xs text-[var(--link)] cursor-pointer">${sn ? esc(sn.gene) + ' &middot; ' : ''}${esc(aid)} &rarr;</button>`;
      }
      const cp = DATA_PORT.find(x => x.id === aid);
      const shortNm = cp ? (cp.sym || cp.name.replace(/^(?:Low-Dose|Ultrahigh-Dose|Stage-Gated)\\s+/i,'').split(/[\\s(/]/)[0]) : '';
      return `<button type="button" data-open-dossier="${esc(aid)}" title="${cp ? esc('#' + cp.rk + ' ' + cp.name + ' (' + cp.id + ')') : esc(aid)}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono font-semibold text-xs text-[var(--link)] cursor-pointer">${cp ? '#' + cp.rk + ' ' : ''}${shortNm ? esc(shortNm) + ' &middot; ' : ''}${esc(aid)} &rarr;</button>`;
    };
    const orderedIds = q ? [...u.ids].sort((a, b) => {
      const ca = DATA_PORT.find(x => x.id === a), cb = DATA_PORT.find(x => x.id === b);
      const ma = queryMatchesIdOrText([a], q, a + ' ' + (ca ? ca.name + ' ' + (ca.sym || '') : '')) ? 0 : 1;
      const mb = queryMatchesIdOrText([b], q, b + ' ' + (cb ? cb.name + ' ' + (cb.sym || '') : '')) ? 0 : 1;
      return ma - mb;
    }) : u.ids;
    const idPills = orderedIds.length > 12
      ? orderedIds.slice(0, 10).map(makeIdPill).join(' ') + `<details class="w-full mt-0.5"><summary class="cursor-pointer font-mono text-xs text-[var(--link)] select-none">Show all ${orderedIds.length} affected programs (+${orderedIds.length - 10} more)</summary><div class="flex flex-wrap items-center gap-1 mt-1.5">${orderedIds.slice(10).map(makeIdPill).join(' ')}</div></details>`
      : orderedIds.map(makeIdPill).join(' ');
    const ancPills = u.ancs.map(anc => {
      const attr = anc.startsWith('EV-') ? `data-open-rep-ev="${esc(anc)}"` : `data-open-rep-run="${esc(anc)}"`;
      return `<button type="button" ${attr} class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer" title="Inspect statistical model &amp; code in Tab 4">${esc(anc)} &rarr;</button>`;
    }).join(' ');
    const openDet = q ? ' open' : '';
    return `<div class="p-3.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 ${updBorderCls(u.cat)} space-y-2 text-xs">
      <div class="flex flex-wrap items-center justify-between gap-1.5">
        <div class="flex flex-wrap items-center gap-1.5">
          ${updCatBadge(u.cat)}
          <span class="font-mono text-xs text-[var(--muted-foreground)]">${esc(u.dt)}${u.tag ? ' &middot; ' + esc(u.tag) : ''}${u.id ? ' &middot; ' + esc(u.id) : ''}</span>
        </div>
        <span class="font-mono text-xs text-[var(--muted-foreground)]">${esc(u.imp)}</span>
      </div>
      <div class="font-semibold text-sm text-[var(--foreground)] leading-snug">${esc(u.hdr)}</div>
      <div class="flex flex-wrap items-center gap-1">${idPills}</div>
      <div class="p-2.5 rounded bg-[var(--card)] border border-[var(--card-border)] space-y-1">
        <div class="font-mono font-semibold text-xs text-[var(--foreground)]">NET PORTFOLIO &amp; VALIDATION IMPACT</div>
        ${formatProseParas(u.cons, gCtx, 'space-y-1.5', 'text-[var(--muted-foreground)]')}
      </div>
      <details${openDet} class="rounded bg-[var(--card)] border border-[var(--card-border)] px-3 py-2.5">
        <summary class="cursor-pointer font-mono text-xs text-[var(--link)] flex flex-wrap items-center justify-between gap-2 select-none"><span>Compare Conventional / Single-Assay View vs. Multi-Modal Re-Analysis &amp; Primary Sources</span><span class="text-[var(--muted-foreground)]">${u.srcs.length} Source${u.srcs.length===1?'':'s'} &middot; ${u.ancs.length} Record${u.ancs.length===1?'':'s'}</span></summary>
        <div class="pt-2.5 mt-2 border-t border-[var(--card-border)] space-y-2.5">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1.5">
              <div class="font-mono font-semibold text-xs text-[var(--muted-foreground)] border-b border-[var(--card-border)] pb-1">CONVENTIONAL / SINGLE-ASSAY VIEW</div>
              ${formatProseParas(u.pre, gCtx, 'space-y-2', 'text-[var(--muted-foreground)]')}
            </div>
            <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1.5">
              <div class="font-mono font-semibold text-xs text-[var(--foreground)] border-b border-[var(--card-border)] pb-1">&rarr; MULTI-MODAL RE-ANALYSIS</div>
              ${formatProseParas(u.post, gCtx, 'space-y-2', 'text-[var(--foreground)]')}
            </div>
          </div>
          <div class="flex flex-wrap items-center justify-between gap-2 font-mono text-xs leading-relaxed">
            <div class="break-words"><span class="text-[var(--muted-foreground)]">Primary Sources:</span> ${escLink(u.srcs.join(' \u00b7 '), gCtx)}</div>
            <div class="flex flex-wrap items-center gap-1"><span class="text-[var(--muted-foreground)]">Verify:</span> ${ancPills}</div>
          </div>
        </div>
      </details>
    </div>`;
  }).join('') : `<div class="p-6 rounded bg-[var(--background)] border border-[var(--card-border)] text-center text-[var(--muted-foreground)] text-xs">No research updates match active filter. <button type="button" data-reset-updates="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></div>`;
}
function jumpToUpdates(query, updateHash=true){
  activeUpdCat = 'ALL';
  const qEl = document.getElementById('upd-search');
  if(qEl) qEl.value = query || '';
  const targetH = query ? ('#updates/' + encodeURIComponent(query)) : '#updates';
  switchTab('home', updateHash ? 'push' : 'none', targetH);
}

function esc(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function decBadge(d, id=''){
  if(d==='KEEP_CORE') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Causal human ALS genetics and/or human TDP-43 pathology + functional rescue">Keep &middot; Core</span>';
  if(d==='KEEP_EXPLORATORY_UNPROVEN') return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap" title="Untested preclinical/biofluid triage queue — prospective Go/No-Go test required">Keep &middot; Exploratory</span>';
  if(d==='RECLASSIFY_BENCHMARK_OR_BIOMARKER'){
    if(id==='EALS-013'||id==='EALS-032') return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--primary)] border border-[var(--primary)] text-xs whitespace-nowrap" title="Approved clinical ALS standard-of-care & in vitro screen calibration benchmark">SOC Benchmark</span>';
    if(id==='EALS-003') return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--primary)] border border-[var(--primary)] text-xs whitespace-nowrap" title="Commercially withdrawn drug retained strictly as a human physiological Kv7.2/7.3 pharmacodynamic reference">Clinical PD Reference</span>';
    if(id==='EALS-017') return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--primary)] border border-[var(--primary)] text-xs whitespace-nowrap" title="Individually associated symptomatic-ALS CSF proteins; fixed 4-protein panel & proposed staging/PD uses are candidates for validation (rs3831317-genotyped)">Candidate CSF Panel</span>';
    if(id==='EALS-043'||id==='EALS-044'||id==='EALS-045') return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--primary)] border border-[var(--primary)] text-xs whitespace-nowrap" title="Pre-validation untargeted CSF proteomic candidate marker requiring targeted PRM / immunoassay bridging">Candidate CSF Marker</span>';
    return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--primary)] border border-[var(--primary)] text-xs whitespace-nowrap" title="Approved SOC drug, clinical PD reference, or fluid staging biomarker">Benchmark</span>';
  }
  return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="Deprioritized based on human RCT futility, CNS exposure/safety limits, or assay confounding">Drop &middot; Falsified</span>';
}
function statusBadge(st, c=null){
  if(st==='PASS_CLEAN_GE2MM') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Zero 0-mm, 1-mm, wobble, bulge, or 18-nt sub-core off-target hits on constrained CNS genes">Pass &middot; Clean (&ge;2mm)</span>';
  if(st.startsWith('CAUTION')){
    const cs = cautionSummary(c);
    return `<span class="px-1.5 py-0.5 rounded font-mono text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap" title="${cs.tip}">${cs.badge}</span>`;
  }
  if(st.startsWith('WARN')) return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="1-mm, wobble, or 1-nt bulge hit on a LoF-intolerant (pLI >= 0.9) CNS gene">Warn &middot; CNS Hit</span>';
  if(st.startsWith('FAIL')) return '<span class="px-1.5 py-0.5 rounded font-mono font-bold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="Exact 0-mismatch off-target hybridization hit across GENCODE v46">Fail &middot; 0-mm</span>';
  return '<span class="text-[var(--muted-foreground)] font-mono text-xs">None</span>';
}
function tdlBadge(tdl){
  const col = tdl==='Tclin' ? 'text-[var(--success)] border-[var(--success)]' : (tdl==='Tchem' ? 'text-[var(--primary)] border-[var(--primary)]' : 'text-[var(--muted-foreground)] border-[var(--border)]');
  return `<span class="px-1.5 py-0.5 rounded font-mono font-semibold border ${col} text-xs whitespace-nowrap" title="NIH Illuminating the Druggable Genome Target Development Level">IDG ${esc(tdl)}</span>`;
}
function tsaSubBadge(tsa){
  if(tsa==='LOW_CONSTRAINT') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Low heterozygous pLoF constraint in gnomAD v4; distinct from biallelic recessive phenotypes">&#10003; Low Het-pLoF Constraint</span>';
  if(tsa==='SELECTIVITY_GATE') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap">&#9651; Selectivity / Directionality</span>';
  if(tsa==='SYSTEMIC_IMMUNE') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap">&#9888; Systemic Sepsis / SLE Risk</span>';
  return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap">&#9888; Pan-Essential / Lethal</span>';
}
function shortTier(t){return t.replace('TIER_1_ACTIONABLE_NOW','T1 Lead').replace('TIER_2_FOCUSED_GATE_FIRST','T2 Validation').replace('TIER_3_EXPLORATORY_DISCOVERY','T3 Discovery').replace('COMPANION_PROTOCOL_ONLY','PD Protocol').replace('BIOMARKER_BENCHMARK_ONLY','Biomarker/SOC').replace('DROPPED_FALSIFIED_EXCLUDED','Excluded');}
const SHORT_STAGE_MAP = {TRL_6_PH2B_SUBGROUP_BIOLOGIC:'Ph2b Subgrp',TRL_5_HUMAN_ALS_PK_PD_PROVEN:'ALS PK/PD',TRL_4_ACTIVE_PH1_CLASS_OR_NCE:'Ph1 / NCE',TRL_3_PRECLINICAL_SSO_COORDINATE:'Preclin SSO',TRL_2_PRECLINICAL_MODALITY_DISCOVERY:'Preclin Mod',TRL_1_TARGET_TOOL_PROBE_WATCHLIST:'Probe/Watch',PROTOCOL_COMPANION_NA:'N/A'};
function shortTrl(t){return SHORT_STAGE_MAP[t] || 'N/A';}

function syncKpiHighlight(){
  document.querySelectorAll('.kpi-btn').forEach(btn => {
    const qf = btn.getAttribute('data-quick-filter');
    const st = btn.getAttribute('data-switch-tab');
    const on = (activeTab==='portfolio' && qf && qf===activeQuick) || (st && activeTab===st);
    btn.classList.toggle('ring-2', Boolean(on));
    btn.classList.toggle('ring-[var(--primary)]', Boolean(on));
    btn.classList.toggle('bg-[var(--content)]', Boolean(on));
  });
}

function renderLensBar(){
  const box = document.getElementById('p-lens-bar');
  if(!box || typeof DATA_LENSES === 'undefined') return;
  box.innerHTML = DATA_LENSES.map(l => {
    const on = activeLens === l.k;
    const cls = on
      ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)] font-semibold'
      : 'bg-[var(--background)] text-[var(--muted-foreground)] border-[var(--border)] hover:text-[var(--foreground)] hover:border-[var(--primary)]';
    return `<button type="button" data-p-lens="${esc(l.k)}" class="px-2 py-0.5 rounded border font-mono text-xs cursor-pointer ${cls}">${esc(l.lbl)}</button>`;
  }).join('');
}

function shortMod(s){
  const raw = String(s || '');
  const leadM = /(#\\d+)/.exec(raw);
  const tag = leadM ? (' (' + leadM[1] + ')') : '';
  let fm = formatModality(raw)
    .replace(/^Dropped \\([^)]+\\):\\s*/, 'Dropped: ')
    .replace(/^Reference Benchmark:\\s*/, '')
    .replace(/\\bchr[0-9XY]+:[0-9.\\-+()_A-Za-z]+/g, '')
    .replace(/\\([^)]*\\)/g, '');
  fm = fm.split(/\\s+(?:Promoted|Exon-5\\s+Inclusion|Promoting|skipping|blocking|pending|across|inside|in\\s+unstratified|with|at|gating|evaluating|&\\s+dendritic-loss|vs\\b)/i)[0];
  fm = fm.replace(/\\s{2,}/g, ' ').replace(/^[,;:\\s-]+|[,;:\\s-]+$/g, '');
  if(tag && !fm.includes(leadM[1])) fm += tag;
  return fm;
}

function renderContrastsTable(){
  const tb = document.getElementById('contrasts-tbody');
  const dr = document.getElementById('contrasts-drawer');
  if(dr) dr.open = false;
  if(!tb || typeof DATA_CONTRASTS === 'undefined') return;
  tb.innerHTML = DATA_CONTRASTS.map(row => {
    const ctx = row.ids[0] || 'EALS-030';
    const idBtns = row.ids.map(cid => {
      const cp = DATA_PORT.find(x => x.id === cid);
      const sLbl = cp ? (cp.sym || cp.name).split(/[\\s(/]/)[0] : '';
      return `<button type="button" data-open-dossier="${esc(cid)}" title="${cp ? esc('#' + cp.rk + ' ' + cp.name + ' (' + cid + ')') : esc(cid)}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono font-semibold text-[var(--link)] text-xs cursor-pointer whitespace-nowrap">${sLbl ? esc(sLbl) + ' &middot; ' : ''}${esc(cid)} &rarr;</button>`;
    }).join(' ');
    return `<tr class="align-top hover:bg-[var(--content)]">
      <td class="py-2 px-2"><div class="flex flex-wrap gap-1">${idBtns}</div></td>
      <td class="py-2 px-2 font-semibold whitespace-nowrap">${esc(row.domain)}</td>
      <td class="py-2 px-2 text-[var(--muted-foreground)] leading-relaxed">${escLink(row.naive, ctx)}</td>
      <td class="py-2 px-2 leading-relaxed">${escLink(row.finding, ctx)}</td>
      <td class="py-2 px-2 text-[var(--muted-foreground)] leading-relaxed">${escLink(row.gate, ctx)}</td>
    </tr>`;
  }).join('');
}

function renderPortfolio(){
  renderLensBar();
  const qRaw = document.getElementById('p-search').value.trim();
  const q = qRaw.toLowerCase();
  const orig = document.getElementById('p-origin').value;
  const dec = document.getElementById('p-dec').value;
  const tier = document.getElementById('p-tier').value;
  const sortBy = document.getElementById('p-sort').value;
  const lensObj = (activeLens !== 'ALL' && typeof DATA_LENSES !== 'undefined') ? DATA_LENSES.find(x => x.k === activeLens) : null;
  const matchMeta = {};
  let rows = DATA_PORT.filter(r => {
    if(lensObj && !lensObj.ids.includes(r.id)) return false;
    if(orig!=='ALL' && r.sub!==orig) return false;
    if(dec==='DROP_CLIN' && (r.dec!=='DROP' || r.epi!=='FALSIFIED_CLINICAL')) return false;
    else if(dec==='DROP_PK' && (r.dec!=='DROP' || r.epi!=='FALSIFIED_PK_SAFETY')) return false;
    else if(dec==='DROP_ART' && (r.dec!=='DROP' || r.epi!=='ARTIFACT_CONFOUNDED')) return false;
    else if(dec!=='ALL' && !dec.startsWith('DROP_') && r.dec!==dec) return false;
    if(activeEpi!=='ALL' && r.epi!==activeEpi) return false;
    if(tier==='TIER_12' && r.tier!=='TIER_1_ACTIONABLE_NOW' && r.tier!=='TIER_2_FOCUSED_GATE_FIRST') return false;
    if(tier==='BIO_AND_CAL' && r.tier!=='BIOMARKER_BENCHMARK_ONLY' && r.tier!=='COMPANION_PROTOCOL_ONLY') return false;
    if(tier!=='ALL' && tier!=='TIER_12' && tier!=='BIO_AND_CAL' && r.tier!==tier) return false;
    if(!qRaw){ matchMeta[r.id] = {tier: 9}; return true; }
    const sumObj = (typeof DATA_SUM !== 'undefined' && DATA_SUM[r.id]) ? DATA_SUM[r.id] : null;
    const sumTxt = sumObj ? ((sumObj.hyp || '') + ' ' + (sumObj.edge_text || '') + ' ' + sumObj.verdict + ' ' + sumObj.sub + ' ' + sumObj.proves + ' ' + sumObj.disproves) : '';
    const subTxt = DATA_SUB.filter(sn => sn.par === r.id).map(sn => sn.id + ' ' + sn.gene + ' ' + sn.role + ' ' + sn.vlbl + ' ' + sn.vbody).join(' ');
    const m = matchCandidateQuery(r, qRaw, humanizeEnum(r.basis||'') + ' ' + sumTxt + ' ' + subTxt);
    if(!m.ok) return false;
    matchMeta[r.id] = m;
    return true;
  });
  const hurdleKey = r => r.tier==='DROPPED_FALSIFIED_EXCLUDED'?99:(r.tier==='BIOMARKER_BENCHMARK_ONLY'?98:(r.tier==='COMPANION_PROTOCOL_ONLY'?97:r.hcnt));
  const baseCmp = (a, b) => {
    if(sortBy==='bio') return a.brk - b.brk;
    if(sortBy==='trl') return (TRL_NUM[b.trl]-TRL_NUM[a.trl])||(a.rk-b.rk);
    if(sortBy==='hurdles') return (hurdleKey(a)-hurdleKey(b))||(a.rk-b.rk);
    return a.rk - b.rk;
  };
  rows.sort((a, b) => qRaw ? (((matchMeta[a.id]||{}).tier||9) - ((matchMeta[b.id]||{}).tier||9)) || baseCmp(a, b) : baseCmp(a, b));
  const epiNote = activeEpi !== 'ALL' ? ` \u00b7 ${humanizeEnum(activeEpi)}` : '';
  const lensNote = lensObj ? ` \u00b7 ${lensObj.lbl.split(' \u00b7 ')[0]}` : '';
  document.getElementById('p-count').textContent = `${rows.length} / ${DATA_PORT.length}${epiNote}${lensNote}`;
  if(!DATA_PORT.some(x=>x.id===selectedId)) selectedId = DATA_PORT[0].id;
  const selHidden = rows.length > 0 && !rows.some(r=>r.id===selectedId);
  document.getElementById('p-tbody').innerHTML = rows.length ? rows.map(r => {
    const active = r.id===selectedId ? 'bg-[var(--content)]' : 'hover:bg-[var(--content)]';
    const dosBtn = DATA_MONOGRAPHS[r.id]
      ? `<button type="button" data-open-dossier="${esc(r.id)}" class="px-2 py-0.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-semibold text-xs cursor-pointer">Monograph &rarr;</button>`
      : `<button type="button" data-open-dossier="${esc(r.id)}" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Dossier &rarr;</button>`;
    const rkPrimary = sortBy==='bio' ? `#${r.brk}` : `#${r.rk}`;
    const rkSecondary = (r.rk !== r.brk || (r.dec !== 'DROP' && r.dec !== 'RECLASSIFY_BENCHMARK_OR_BIOMARKER'))
      ? `<div class="text-xs font-semibold text-[var(--primary)]">${sortBy==='bio' ? 'Prio #'+r.rk : 'Evid #'+r.brk}</div>`
      : '';
    const mSub = (matchMeta[r.id] && matchMeta[r.id].sub) ? matchMeta[r.id].sub : '';
    const matchedSub = q ? DATA_SUB.filter(sn => sn.par === r.id && !r.name.toLowerCase().includes(sn.gene.toLowerCase()) && (sn.id === mSub || (sn.gene+' '+sn.id+' '+sn.role).toLowerCase().includes(q))).map(sn => sn.gene) : [];
    const subCnt = DATA_SUB.filter(sn => sn.par === r.id).length;
    const hasNygc = Object.values(NYGC_GENE_TO_ID).includes(r.id);
    const metaChips = [
      matchedSub.length ? `<span class="px-1.5 py-0.5 rounded border border-[var(--primary)] text-[var(--primary)] font-mono text-xs">Includes: ${esc(matchedSub.join(', '))}</span>` : (subCnt ? `<span class="px-1 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] font-mono text-xs">${subCnt} Subunits</span>` : ''),
      hasNygc ? '<span class="px-1 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] font-mono text-xs">NYGC 3-Region</span>' : ''
    ].filter(Boolean).join(' ');
    return `<tr tabindex="0" data-select-cand="${esc(r.id)}" aria-selected="${r.id===selectedId?'true':'false'}" class="cursor-pointer focus:bg-[var(--content)] ${active}">
      <td class="py-2 px-2 font-mono tabular-nums whitespace-nowrap text-[var(--muted-foreground)]" title="Translational Priority #${r.rk} · Genetic & Pathology Evidence #${r.brk}"><div>${rkPrimary}</div>${rkSecondary}</td>
      <td class="py-2 px-1.5 font-mono text-xs text-[var(--muted-foreground)] whitespace-nowrap" title="ExploreALS Accession ${esc(r.id)}">${esc(r.id)}</td>
      <td class="py-2 px-2"><div class="flex flex-wrap items-center gap-1"><strong class="font-bold text-[var(--foreground)]">${esc(r.name)}</strong>${metaChips}</div><div class="text-[var(--muted-foreground)] text-xs">${esc(humanizeEnum(r.sub))} &middot; ${trackLabel(r.trk)}</div></td>
      <td class="hidden xl:table-cell py-2 px-2 text-xs text-[var(--muted-foreground)] max-w-[220px] break-words" title="${esc(formatModality(r.mod))}">${esc(shortMod(r.mod))}</td>
      <td class="py-2 px-1.5">${decBadge(r.dec, r.id)}</td>
      <td class="hidden lg:table-cell py-2 px-1.5 text-xs whitespace-nowrap">${esc(shortTier(r.tier))}</td>
      <td class="hidden sm:table-cell py-2 px-1.5 font-mono text-xs whitespace-nowrap">${esc(shortTrl(r.trl))}</td>
      <td class="hidden sm:table-cell py-2 px-1.5 font-mono tabular-nums text-right">${r.hcnt}</td>
      <td class="py-2 px-2 text-right whitespace-nowrap">${dosBtn}</td>
    </tr>`;
  }).join('') : `<tr><td colspan="9" class="py-6 px-4 text-center text-[var(--muted-foreground)]">No candidates match active filters. <button type="button" data-reset-filters="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></td></tr>`;
  renderDetail(selHidden);
  syncKpiHighlight();
}

function renderExpandableGate(candId, mode, titleHtml, borderCls, rawStr){
  if(!rawStr) return '';
  if(ENUM_LABELS[rawStr]) return `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] ${borderCls} leading-relaxed break-words">${titleHtml} ${esc(ENUM_LABELS[rawStr])}</div>`;
  const fullHtml = (mode === 'go' || mode === 'kill')
    ? formatGateList(rawStr, candId, mode === 'kill')
    : formatProseParas(rawStr, candId, 'space-y-1.5');
  const shouldClamp = String(rawStr).trim().length >= 420;
  if(!shouldClamp){
    return `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] ${borderCls} space-y-1.5 leading-relaxed break-words"><div>${titleHtml}</div>${fullHtml}</div>`;
  }
  const key = candId + ':' + mode;
  const domId = 'gate-body-' + candId + '-' + mode;
  const isOpen = Boolean(expandedDetailGates[key]);
  const itemCnt = (fullHtml.match(/<li\\b/g) || []).length;
  const moreLbl = itemCnt >= 2 ? `Read all ${itemCnt} items &darr;` : 'Read full details &darr;';
  return `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] ${borderCls} space-y-1.5 leading-relaxed break-words">` +
    `<div>${titleHtml}</div>` +
    `<div id="${esc(domId)}" class="gate-clamp" data-clamped="${isOpen ? 'false' : 'true'}">${fullHtml}</div>` +
    `<button type="button" data-toggle-detail-gate="${esc(key)}" data-more-lbl="${moreLbl}" aria-expanded="${isOpen ? 'true' : 'false'}" aria-controls="${esc(domId)}" class="text-[var(--link)] hover:underline font-mono text-xs cursor-pointer">${isOpen ? 'Collapse &uarr;' : moreLbl}</button>` +
    `</div>`;
}

function syncDetailClamps(){
  const det = document.getElementById('p-detail');
  if(!det) return;
  det.querySelectorAll('[data-toggle-detail-gate]').forEach(btn => {
    const gk = btn.getAttribute('data-toggle-detail-gate') || '';
    const bodyEl = document.getElementById(btn.getAttribute('aria-controls') || '');
    if(!bodyEl) return;
    if(expandedDetailGates[gk]){
      bodyEl.setAttribute('data-clamped', 'false');
      btn.classList.remove('hidden');
      return;
    }
    bodyEl.setAttribute('data-clamped', 'false');
    const naturalH = bodyEl.scrollHeight;
    if(naturalH > 0 && naturalH <= 142){
      btn.classList.add('hidden');
    } else {
      bodyEl.setAttribute('data-clamped', 'true');
      btn.classList.remove('hidden');
    }
  });
}

function renderDetail(selHidden=false){
  lastSelHidden = selHidden;
  const r = DATA_PORT.find(x=>x.id===selectedId) || DATA_PORT[0];
  const hiddenBanner = selHidden
    ? `<div class="p-2 rounded bg-[var(--background)] border border-dashed border-[var(--warning)] flex items-center justify-between gap-2 text-xs"><span class="text-[var(--warning)] font-mono">Pinned #${r.rk} ${esc(r.id)} is outside active filter</span><button type="button" data-reset-filters="1" class="text-[var(--link)] underline font-mono cursor-pointer shrink-0">Show all (52)</button></div>`
    : '';
  const w = DATA_MONOGRAPHS[r.id];
  const s = (typeof DATA_SUM !== 'undefined' && DATA_SUM[r.id]) ? DATA_SUM[r.id] : null;
  const isDrop = r.dec === 'DROP';
  const evRows = DATA_EV[r.id] || [];
  const gPills = genePortalPills(r.id);
  const candCis = DATA_CIS.filter(c => c.pid===r.id || c.sc===r.id);
  const leadCis = r.iv!=='NONE' ? DATA_CIS.find(c => c.iv===r.iv) : (candCis[0] || null);
  const candSub = DATA_SUB.filter(x => x.par === r.id);
  const hasNygc = Object.values(NYGC_GENE_TO_ID).includes(r.id);
  let cisBox = '';
  if(leadCis){
    const loP = Math.max(1, Number(leadCis.lo)-250), hiP = Number(leadCis.hi)+250;
    const ensUrl = `https://www.ensembl.org/Homo_sapiens/Location/View?r=${leadCis.chr.replace('chr','')}:${leadCis.lo}-${leadCis.hi}`;
    const atlUrl = `https://deepmind.google.com/science/alphagenome/atlas?q=${leadCis.chr}:${loP}-${hiP}&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE`;
    const ucscUrl = `https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position=${leadCis.chr}:${loP}-${hiP}`;
    cisBox = `<div class="p-2 rounded border border-[var(--border)] bg-[var(--background)] space-y-1">
      <div class="flex items-center justify-between gap-1.5 flex-wrap">
        <span class="font-mono font-semibold text-[var(--foreground)]">${r.iv!=='NONE'?'Lead Window':'Target Window'} (${leadCis.len}bp &middot; ${leadCis.tm}&deg;C)</span>
        ${statusBadge(leadCis.st, leadCis)}
      </div>
      <div class="font-mono flex flex-wrap items-center justify-between gap-1.5">
        <span>${mkExtA(ensUrl, esc(leadCis.iv))} &middot; ${mkExtA(atlUrl, 'Atlas &nearr;')} &middot; ${mkExtA(ucscUrl, 'UCSC &nearr;')}</span>
        <button type="button" data-jump-intervals="${esc(r.id)}" class="text-[var(--link)] hover:underline cursor-pointer">Tab 3 (${candCis.length}) &rarr;</button>
      </div>
    </div>`;
  }
  const priorTag = r.prior && r.prior !== 'NONE'
    ? '<span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] font-mono">&#9671; Modeled Estimate</span>'
    : '<span class="px-1 rounded border border-[var(--success)] text-[var(--success)] font-mono">&#9679; Empirical Data</span>';
  const hurdles = r.hurdles && r.hurdles!=='NONE'
    ? `<div class="flex flex-wrap gap-1 mt-0.5">${r.hurdles.split(';').map(h=>`<span class="px-1.5 py-0.5 rounded border border-[var(--border)] bg-[var(--background)] text-xs leading-snug">${esc(formatHurdle(h))}</span>`).join('')}</div>`
    : '<span class="text-[var(--muted-foreground)] text-xs ml-1">None (Calibration / Biomarker)</span>';
  let gateSnap = '';
  if(isDrop){
    gateSnap = renderExpandableGate(r.id, 'drop', `<strong class="font-mono text-[var(--error)]">&#10005; ${esc(humanizeEnum(r.epi))}:</strong>`, 'border-l-4 border-l-[var(--error)]', s ? s.disproves : humanizeEnum(r.epi));
  } else if(w){
    gateSnap = `<div class="space-y-2">
      <div><span class="text-[var(--muted-foreground)] font-semibold">Open Validation Steps (${r.hcnt}):</span>${hurdles}</div>
      ${renderExpandableGate(r.id, 'go', '<strong class="font-mono text-[var(--success)]">&#10003; Go Criteria:</strong>', 'border-l-4 border-l-[var(--success)]', w.verdict_box.pass_gate)}
      ${renderExpandableGate(r.id, 'kill', '<strong class="font-mono text-[var(--error)]">&#10005; No-Go Criteria:</strong>', 'border-l-4 border-l-[var(--error)]', w.verdict_box.kill_gate)}
    </div>`;
  } else {
    gateSnap = `<div class="space-y-2">
      <div><span class="text-[var(--muted-foreground)] font-semibold">Open Validation Steps (${r.hcnt}):</span>${hurdles}</div>
      ${r.nxt && r.nxt !== 'NONE' && !r.nxt.startsWith('NONE_') ? renderExpandableGate(r.id, 'next', '<strong class="font-mono text-[var(--warning)]">&#9651; Next Test:</strong>', 'border-l-4 border-l-[var(--warning)]', r.nxt) : ''}
    </div>`;
  }
  const secLinks = [];
  if(w){
    secLinks.push(['sec-cascade', 'Pathogenic Mechanism'], ['sec-evidence-viz', 'Effect Sizes & Diagrams'], ['sec-safety', 'Safety & 3D Structure'], ['sec-5rs', 'Translational Deep Dive']);
  } else {
    secLinks.push(['sec-overview', 'Hypothesis & Verdict'], ['sec-procon', isDrop ? 'Originating Signal vs. Negative Evidence' : 'Evidence Pro / Con']);
  }
  if(candSub.length) secLinks.push(['sec-subunits', `Subunit & Selectivity (${candSub.length})`]);
  if(hasNygc) secLinks.push(['sec-nygc', 'NYGC 3-Region RNA']);
  if(candCis.length) secLinks.push(['sec-cis', `Splice Windows (${candCis.length})`]);
  if(evRows.length) secLinks.push(['sec-ledger', `Primary Evidence (${evRows.length})`]);
  const secBar = secLinks.map(([sid, lbl]) => `<button type="button" data-open-dossier-sec="${esc(r.id)}|${sid}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">${esc(lbl)} &rarr;</button>`).join(' ');
  const pubMonoLink = (typeof window !== 'undefined' && window.PUBLIC_WEB_EXPORT && w)
    ? `<a href="./monographs/${esc(r.id)}.html" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs shrink-0" title="Open lightweight standalone monograph page">Page &nearr;</a>`
    : '';
  const candUpds = (typeof DATA_UPDATES !== 'undefined') ? DATA_UPDATES.filter(u => u.ids.includes(r.id) || u.ids.some(x => x.startsWith(r.id + '.'))) : [];
  const updDetailBtn = candUpds.length
    ? `<button type="button" data-jump-updates="${esc(r.id)}" class="px-2 py-1 rounded border border-[var(--primary)] text-[var(--primary)] font-mono text-xs shrink-0 cursor-pointer" title="View living research updates for ${esc(r.id)}">&#8634; ${candUpds.length}</button>`
    : '';
  const crowdChip = (r.crowd && !r.crowd.startsWith('N/A')) ? `<span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)] whitespace-nowrap">${esc(r.crowd)}</span>` : '';
  document.getElementById('p-detail').innerHTML = `${hiddenBanner}
    <div class="space-y-1.5 border-b border-[var(--card-border)] pb-2">
      <div class="flex items-center justify-between gap-1.5 flex-wrap">
        <div class="flex items-center gap-1.5 flex-wrap"><span class="font-mono font-bold text-sm" title="Translational Priority Rank #${r.rk} · Genetic & Pathology Evidence Rank #${r.brk}">#${r.rk} <span class="font-normal text-xs text-[var(--muted-foreground)]">(Evid #${r.brk})</span> &middot; <span class="text-[var(--muted-foreground)] font-normal">${esc(r.id)}</span></span> ${decBadge(r.dec, r.id)} ${crowdChip}</div>
        <div class="flex items-center gap-1 shrink-0">${updDetailBtn}${pubMonoLink}</div>
      </div>
      <div class="text-sm font-semibold leading-snug">${esc(r.name)}</div>
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <span class="font-mono text-xs text-[var(--muted-foreground)]">${gPills || esc(trackLabel(r.trk))}</span>
        <button type="button" data-open-dossier="${esc(r.id)}" class="px-2.5 py-1 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-semibold text-xs cursor-pointer">${w?'Open Full Monograph &rarr;':`Open Full Dossier (${evRows.length}) &rarr;`}</button>
      </div>
    </div>
    <div class="space-y-2 text-xs">
      ${typeof renderEdgeRibbon === 'function' ? renderEdgeRibbon(s, r.id, true) : ''}
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-2">
        <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1 xl:col-span-2">
          <div class="text-[var(--muted-foreground)] font-mono">Therapeutic Modality</div>
          <div class="font-medium leading-relaxed break-words">${escLink(formatModality(r.mod), r.id)}</div>
        </div>
        <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1">
          <div class="text-[var(--muted-foreground)] font-mono">Development Stage &amp; Next Step</div>
          <div class="font-mono font-semibold">${esc(humanizeEnum(r.trl))}</div>
          <div class="text-[var(--muted-foreground)] leading-relaxed">${esc(humanizeEnum(r.gate))}</div>
        </div>
        <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1">
          <div class="text-[var(--muted-foreground)] font-mono">Causal Role &amp; Directionality</div>
          <div class="font-medium leading-relaxed">${esc(s ? s.causal : humanizeEnum(r.epi))}</div>
        </div>
        <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1 xl:col-span-2">
          <div class="text-[var(--muted-foreground)] font-mono">Evidence Basis &amp; Modeling</div>
          <div class="leading-relaxed">${esc(humanizeEnum(r.basis))}</div>
          <div class="pt-0.5">${priorTag}</div>
        </div>
      </div>
      ${cisBox}
      ${gateSnap}
      <div class="pt-2 border-t border-[var(--card-border)] space-y-1.5">
        <div class="flex items-center justify-between gap-1 font-mono text-[var(--muted-foreground)]">
          <span>Inside Candidate Report (Tab 2):</span>
          <button type="button" data-jump-rep-cand="${esc(r.id)}" class="text-[var(--link)] hover:underline cursor-pointer">Verify in Tab 4 &rarr;</button>
        </div>
        <div class="flex flex-wrap gap-1">${secBar}</div>
      </div>
    </div>`;
  syncDetailClamps();
}
function selectCand(id, userClick=false){
  selectedId = id;
  dossierId = id;
  renderPortfolio();
  if(userClick){
    commitHistory('replace');
    try {
      if(typeof window !== 'undefined' && window.innerWidth && window.innerWidth < 1024){
        const det = document.getElementById('p-detail');
        if(det && det.scrollIntoView) det.scrollIntoView({behavior:'smooth', block:'nearest'});
      }
    } catch(_e) {}
  }
}
function quickFilter(mode){
  const wasPortfolio = (activeTab === 'portfolio');
  activeQuick = mode;
  resetPortfolioFilters(false, mode);
  if(mode==='TIER12') document.getElementById('p-tier').value='TIER_12';
  else if(mode==='CORE') document.getElementById('p-dec').value='KEEP_CORE';
  else if(mode==='EXPL') document.getElementById('p-dec').value='KEEP_EXPLORATORY_UNPROVEN';
  else if(mode==='BENCH') document.getElementById('p-dec').value='RECLASSIFY_BENCHMARK_OR_BIOMARKER';
  else if(mode==='DROP') document.getElementById('p-dec').value='DROP';
  if(!wasPortfolio) switchTab('portfolio', 'push');
  else { renderPortfolio(); commitHistory('replace'); }
}
function resetPortfolioFilters(redraw=true, keepQuick='ALL'){
  activeQuick = keepQuick;
  activeEpi = 'ALL';
  activeLens = 'ALL';
  document.getElementById('p-search').value='';
  document.getElementById('p-origin').value='ALL';
  document.getElementById('p-dec').value='ALL';
  document.getElementById('p-tier').value='ALL';
  document.getElementById('p-sort').value='rank';
  if(redraw) renderPortfolio();
}
"""

EXPLORER_JS_TABS234 = """
const SHORT_CIS_ROLE = {
  MULTIPLEX_CORE: 'Multiplex Core',
  SINGLE_LOCUS_LEAD: 'Single Lead',
  EXPLORATORY_LOCUS: 'Exploratory',
  EXCLUDED_ALU_REPEAT: 'Alu Excluded'
};
const SHORT_CIS_MODE = {
  INCLUDE_EXON_UPSTREAM_UG: 'Exon-5 Inclusion (UG)',
  INCLUDE_CONSTITUTIVE_EXON: 'Intron-5 (ISS/ISE)',
  SKIP_CRYPTIC_EXON: 'Cryptic Exon Skip',
  CRYPTIC_EXON2A_3SS_PAS_BLOCK: "Exon-2a 3'SS & PAS",
  CRYPTIC_CASSETTE_EXON_SKIP: 'Cryptic Cassette Skip',
  CRYPTIC_CASSETTE_MAJOR_3SS_AND_SHARED_EXON: "Major 3'SS + Exonic",
  CRYPTIC_CASSETTE_DOWNSTREAM_INTRONIC_ISE: 'Intronic ISE Block',
  CRYPTIC_A3SS_PROXIMAL_EXON_BLOCK: 'Cryptic A3SS (+8..27)',
  CRYPTIC_A3SS_ACCEPTOR_BLOCK: 'Cryptic A3SS Block',
  CRYPTIC_ALE_3SS_ACCEPTOR_BLOCK: "Cryptic ALE 3'SS",
  CRYPTIC_3EXT_ISOFORM_GAPMER_WINDOW: "3'-Ext Gapmer ASO",
  DISTAL_3UTR_EXT_PAS_WINDOW: "Distal 3'-UTR PAS"
};
function shortIvBadge(c){
  const st = String(c.st || '');
  if(st === 'PASS_CLEAN_GE2MM') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Zero 0-mm, 1-mm, wobble, 2-mm (<=25bp), bulge, or 18-nt sub-core off-target hits">Pass &middot; Clean</span>';
  if(st.startsWith('CAUTION')) return `<span class="px-1.5 py-0.5 rounded font-mono text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap" title="${cautionSummary(c).tip}">Caution</span>`;
  if(st.startsWith('WARN')) return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="1-mm, wobble, or 1-nt bulge hit on a LoF-intolerant (pLI >= 0.9) CNS gene">Warn &middot; CNS</span>';
  if(st.startsWith('FAIL')) return '<span class="px-1.5 py-0.5 rounded font-mono font-bold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="Exact 0-mismatch off-target hybridization hit across GENCODE v46">Fail &middot; 0-mm</span>';
  return '<span class="text-[var(--muted-foreground)] font-mono text-xs">None</span>';
}
const CIS_HIT_LBL = {
  'spliced:0mm':'Spliced mRNA 0-mm', 'spliced:1mm':'Spliced mRNA 1-mm', 'spliced:2mm':'Spliced mRNA 2-mm',
  'premRNA:0mm':'Pre-mRNA 0-mm', 'premRNA:1mm':'Pre-mRNA 1-mm', 'premRNA:2mm':'Pre-mRNA 2-mm',
  '1nt-bulge:1mm':'1-nt bulge (1-mm)', '18nt-subcore(non-constrained)':'18-nt sub-core (non-constrained)',
  '0-mm deep intron':'Deep-intron 0-mm (steric-inert)', '1mm_inert_UTR3_GT50EEJ':"3'-UTR 1-mm (>50nt past EEJ, NMD-inert)"
};
const CIS_CELL_LBL = {
  Edin_Endo:'Edinburgh Endothelium', 'BA4 Oligo':'BA4 Oligodendrocytes',
  'BA4 Inh':'BA4 Inhibitory Neurons', 'BA4 Exc':'BA4 Excitatory Neurons', 'BA4 Astro':'BA4 Astrocytes'
};
function parseCisFlags(rawFlags){
  if(!rawFlags || rawFlags === 'NONE') return {items: [], extraNote: ''};
  const byGene = new Map();
  let extraNote = '';
  String(rawFlags).split(';').map(s => s.trim()).filter(Boolean).forEach(chunk => {
    if(chunk.startsWith('+')){ extraNote = chunk; return; }
    const pIdx = chunk.indexOf('(');
    if(pIdx < 0) return;
    const gene = chunk.slice(0, pIdx).trim();
    const inner = chunk.endsWith(')') ? chunk.slice(pIdx + 1, -1) : chunk.slice(pIdx + 1);
    const parts = inner.split(',').map(x => x.trim()).filter(Boolean);
    const hitLbl = CIS_HIT_LBL[parts[0]] || parts[0];
    const meta = parts.slice(1).map(p => {
      if(CIS_CELL_LBL[p]) return CIS_CELL_LBL[p];
      if(p.startsWith('dSS=')) return 'splice dist ' + p.slice(4);
      if(p.startsWith('dEEJ=')) return 'EEJ dist ' + p.slice(5);
      if(p.startsWith('d=')) return 'splice dist ' + p.slice(2);
      return p;
    });
    if(!byGene.has(gene)) byGene.set(gene, {gene: gene, hits: [], meta: []});
    const rec = byGene.get(gene);
    if(hitLbl && !rec.hits.includes(hitLbl)) rec.hits.push(hitLbl);
    meta.forEach(m => { if(!rec.meta.includes(m)) rec.meta.push(m); });
  });
  return {items: Array.from(byGene.values()), extraNote: extraNote};
}
function findBestIvOrd(raw){
  if(!raw) return 0;
  const q = String(raw).trim();
  if(/^([1-9]|1[0-9]|2[0-8])$/.test(q)) return Number(q);
  const ql = q.toLowerCase();
  const matches = DATA_CIS.filter(c => c.pid.toLowerCase() === ql || c.sc.toLowerCase() === ql || c.gene.toLowerCase() === ql);
  if(!matches.length) return 0;
  return (matches.find(c => c.lead) || matches[0]).ord;
}
function ivCellBox(lbl, val, isExact){
  const n = Number(val);
  const tone = (isExact && n > 0) ? 'text-[var(--error)]' : ((val !== '0' && val !== 'NA') ? 'text-[var(--warning)]' : 'text-[var(--muted-foreground)]');
  return `<div class="p-1.5 rounded bg-[var(--card)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] leading-snug">${lbl}</div><div class="font-mono font-semibold text-sm tabular-nums mt-0.5 ${tone}">${esc(val)}</div></div>`;
}
function renderIntervalDetail(rows){
  const det = document.getElementById('iv-detail');
  if(!det) return;
  const c = DATA_CIS.find(x => x.ord === selectedIvOrd) || DATA_CIS[0];
  const loPad = Math.max(1, Number(c.lo) - 250), hiPad = Number(c.hi) + 250;
  const atlUrl = `https://deepmind.google.com/science/alphagenome/atlas?q=${c.chr}:${loPad}-${hiPad}&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE`;
  const ucscUrl = `https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position=${c.chr}:${loPad}-${hiPad}`;
  const ensUrl = `https://www.ensembl.org/Homo_sapiens/Location/View?r=${c.chr.replace('chr','')}:${c.lo}-${c.hi}`;
  const gid = GENE_ENSG[c.gene] || '';
  const gnomUrl = gid ? `https://gnomad.broadinstitute.org/gene/${gid}?dataset=gnomad_r4` : '';
  const linkId = (c.pid && c.pid !== 'NONE') ? c.pid : String(c.sc).replace(/\\.[0-9]+$/, '');
  const siblings = DATA_CIS.filter(x => x.gene === c.gene);
  const sibBar = siblings.map(s => {
    const on = s.ord === c.ord;
    const cls = on ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)] font-semibold' : 'bg-[var(--background)] text-[var(--foreground)] border-[var(--border)] hover:border-[var(--primary)]';
    return `<button type="button" data-select-iv="${s.ord}" class="px-2 py-0.5 rounded border font-mono text-xs cursor-pointer ${cls}">#${s.rk}${s.lead ? ' &#9733;' : ''} &middot; ${s.len}bp</button>`;
  }).join(' ');
  const [mExact, mOne, mWob] = String(c.sp).split('/');
  const [pExact, pOne, pWob, pTwo, pBulge, pCore] = String(c.pm).split('/');
  const pf = parseCisFlags(c.flags);
  const isWarnOrFail = String(c.st).startsWith('WARN') || String(c.st).startsWith('FAIL');
  const flagsHtml = !pf.items.length
    ? `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--success)]"><span class="font-mono font-semibold text-[var(--success)]">&#10003; Zero flagged LoF-intolerant CNS gene hits</span> <span class="text-[var(--muted-foreground)]">(gnomAD v4 pLI / LOEUF screen)</span></div>`
    : `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] border-l-4 ${isWarnOrFail ? 'border-l-[var(--error)]' : 'border-l-[var(--warning)]'} space-y-1.5">
        <div class="font-mono font-semibold ${isWarnOrFail ? 'text-[var(--error)]' : 'text-[var(--warning)]'}">${isWarnOrFail ? `Flagged LoF-Intolerant CNS Genes (${pf.items.length})` : `Off-Target Gene Note (${pf.items.length} Non-Constrained / Steric-Inert)`}</div>
        <div class="space-y-1">${pf.items.map(it => {
          const fgid = GENE_ENSG[it.gene] || '';
          const gLink = fgid ? mkExtA('https://gnomad.broadinstitute.org/gene/' + fgid + '?dataset=gnomad_r4', `<strong class="font-semibold">${esc(it.gene)}</strong>`) : `<strong class="font-semibold">${esc(it.gene)}</strong>`;
          return `<div class="p-2 rounded bg-[var(--card)] border border-[var(--card-border)] space-y-0.5"><div class="flex flex-wrap items-center justify-between gap-1 font-mono"><span>${gLink}</span><span class="text-[var(--foreground)]">${esc(it.hits.join(' + '))}</span></div>${it.meta.length ? `<div class="font-mono text-[var(--muted-foreground)]">${esc(it.meta.join(' \u00b7 '))}</div>` : ''}</div>`;
        }).join('')}</div>
        ${pf.extraNote ? `<div class="font-mono text-[var(--error)] pt-0.5">${esc(pf.extraNote)} (Alu repeat family)</div>` : ''}
      </div>`;
  const pmFoot = c.is_gap
    ? `RNase-H1 gapmer window: total intronic sense 1-mm genes across full pre-mRNA = ${c.pm1_all} (nuclear RNase H1 cleaves deep-intronic hybrids regardless of splice-site distance).`
    : (pTwo === 'NA'
      ? `Total sense 1-mm pre-mRNA genes = ${c.pm1_all}; Alu-repeat window saturates GGGenome max_mm=1 (2-mm scan = NA).`
      : `Full pre-mRNA sense 1-mm genes (including deep introns >50 bp from splice sites) = ${c.pm1_all}.`);
  det.innerHTML = `<div class="space-y-1.5 border-b border-[var(--card-border)] pb-2">
      <div class="flex items-center justify-between gap-1.5 flex-wrap">
        <div class="flex items-center gap-1.5 flex-wrap"><span class="font-mono font-bold text-sm">#${c.ord} &middot; ${esc(c.gene)} &middot; Window #${c.rk}</span> ${c.lead ? '<span class="px-1.5 py-0.5 rounded border border-[var(--success)] text-[var(--success)] font-mono font-semibold text-xs whitespace-nowrap">&#9733; Promoted Lead</span>' : '<span class="px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] font-mono text-xs whitespace-nowrap">Alternative</span>'}</div>
        ${statusBadge(c.st, c)}
      </div>
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <span class="font-mono text-xs text-[var(--muted-foreground)]">${esc(c.sc !== linkId ? c.sc + ' (' + linkId + ')' : linkId)} &middot; ${esc(humanizeEnum(c.role))}</span>
        <button type="button" data-open-dossier="${esc(linkId)}" class="px-2.5 py-1 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-semibold text-xs cursor-pointer">Candidate Report &rarr;</button>
      </div>
      ${siblings.length > 1 ? `<div class="flex flex-wrap items-center gap-1 pt-0.5"><span class="font-mono text-xs text-[var(--muted-foreground)] mr-0.5">${esc(c.gene)} windows:</span>${sibBar}</div>` : ''}
    </div>
    <div class="space-y-2 text-xs">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1 sm:col-span-2">
          <div class="flex items-center justify-between gap-2"><span class="text-[var(--muted-foreground)] font-mono">1-Based Closed GRCh38 Target Window</span><button type="button" data-copy-cmd="${esc(c.iv)}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">Copy</button></div>
          <div class="font-mono font-semibold text-sm break-all">${esc(c.iv)} <span class="text-xs font-normal text-[var(--muted-foreground)]">(${c.len} bp &middot; ${c.strd === '+' ? 'Plus (+)' : 'Minus (&minus;)'} strand)</span></div>
          <div class="leading-relaxed"><span class="text-[var(--muted-foreground)]">Mechanism:</span> <strong class="font-medium text-[var(--foreground)]">${esc(humanizeEnum(c.mode))}</strong></div>
        </div>
        <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-0.5">
          <div class="text-[var(--muted-foreground)] font-mono">Modeled 2&apos;-O-MOE PO/PS</div>
          <div class="font-mono font-semibold tabular-nums">Tm ${c.tm}&deg;C &middot; &Delta;G37 ${c.dg} kcal/mol</div>
          <div class="text-[var(--muted-foreground)] font-mono tabular-nums">GC content: ${c.gc}%</div>
        </div>
        <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-0.5">
          <div class="text-[var(--muted-foreground)] font-mono">AlphaGenome Variant Impact</div>
          <div class="font-mono font-semibold tabular-nums">max AVI = ${c.avi} Phred</div>
          <div class="text-[var(--muted-foreground)] leading-snug">DNA conservation/splicing score</div>
        </div>
      </div>
      <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-2">
        <div class="flex items-center justify-between gap-2 flex-wrap"><span class="font-mono font-semibold text-[var(--foreground)]">GENCODE v46 Off-Target Hybridization (254,070 tx)</span></div>
        <div class="space-y-1">
          <div class="font-mono text-[var(--muted-foreground)]">Spliced mRNA (&le;200 bp of splice junction)</div>
          <div class="grid grid-cols-3 gap-1.5">${ivCellBox('Exact 0-mm', mExact, true)}${ivCellBox('1-Mismatch', mOne, false)}${ivCellBox('G:U Wobble', mWob, false)}</div>
        </div>
        <div class="space-y-1">
          <div class="font-mono text-[var(--muted-foreground)]">Nascent Pre-mRNA (Sense Strand)</div>
          <div class="grid grid-cols-3 gap-1.5">${ivCellBox('Sense 0-mm', pExact, true)}${ivCellBox('1-mm (&le;50bp SS)', pOne, false)}${ivCellBox('Wobble (&le;50bp)', pWob, false)}${ivCellBox('2-mm (&le;25bp SS)', pTwo, false)}${ivCellBox('1-nt Bulge', pBulge, false)}${ivCellBox('18-nt Sub-Core', pCore, false)}</div>
          <div class="text-[var(--muted-foreground)] leading-snug pt-0.5">${esc(pmFoot)}</div>
        </div>
      </div>
      ${flagsHtml}
      <div class="pt-2 border-t border-[var(--card-border)] space-y-1.5">
        <div class="flex flex-wrap gap-1.5 font-mono">
          <span class="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--background)]">${mkExtA(ensUrl, 'Ensembl GRCh38 &nearr;')}</span>
          <span class="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--background)]">${mkExtA(atlUrl, 'AlphaGenome Atlas &nearr;')}</span>
          <span class="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--background)]">${mkExtA(ucscUrl, 'UCSC hg38 &nearr;')}</span>
          ${gnomUrl ? `<span class="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--background)]">${mkExtA(gnomUrl, 'gnomAD v4 (' + esc(c.gene) + ') &nearr;')}</span>` : ''}
        </div>
        <div class="flex items-center justify-between gap-2 font-mono text-[var(--muted-foreground)]">
          <span>${rows.length} / ${DATA_CIS.length} windows shown</span>
          <button type="button" data-jump-rep-cand="${esc(linkId)}" class="text-[var(--link)] hover:underline cursor-pointer">Verify Provenance in Tab 4 &rarr;</button>
        </div>
      </div>
    </div>`;
}
function renderIntervals(){
  const qEl = document.getElementById('iv-search');
  const q = qEl ? qEl.value.trim() : '';
  const st = document.getElementById('iv-status').value;
  const orig = document.getElementById('iv-origin').value;
  const leadsOnly = document.getElementById('iv-leads').checked;
  const rows = DATA_CIS.filter(c => {
    if(st!=='ALL' && c.st!==st) return false;
    if(orig!=='ALL' && c.o!==orig) return false;
    if(leadsOnly && !c.lead) return false;
    if(q && !queryMatchesIdOrText([c.sc], q, (c.sc===c.pid ? c.pid+' ' : '')+c.sc+' '+c.gene+' '+c.iv+' '+c.flags+' '+c.mode)) return false;
    return true;
  });
  if(!DATA_CIS.some(x => x.ord === selectedIvOrd)) selectedIvOrd = 5;
  if(rows.length > 0 && !rows.some(x => x.ord === selectedIvOrd)){
    selectedIvOrd = (rows.find(x => x.lead) || rows[0]).ord;
  }
  document.getElementById('iv-count').textContent = `${rows.length} / ${DATA_CIS.length}`;
  document.getElementById('iv-tbody').innerHTML = rows.length ? rows.map(c => {
    const isSel = c.ord === selectedIvOrd;
    const activeCls = isSel ? 'bg-[var(--content)] border-l-4 border-l-[var(--primary)]' : 'hover:bg-[var(--content)]';
    const pf = parseCisFlags(c.flags);
    const isWF = String(c.st).startsWith('WARN') || String(c.st).startsWith('FAIL');
    const cShort = String(c.st).startsWith('CAUTION') ? cautionSummary(c).short.replace(/^Caution\\s*\\((.*)\\)$/, (_m, g) => g) : '';
    const flagLine = c.st === 'PASS_CLEAN_GE2MM'
      ? '0 off-target hits'
      : (isWF
        ? (pf.items.length === 1 ? `1 CNS (${pf.items[0].gene})` : `${pf.items.length} CNS${pf.extraNote ? ' (+62)' : ' genes'}`)
        : (pf.items.length ? `Note: ${pf.items[0].gene}` : (cShort || 'Non-CNS only')));
    const shortMode = SHORT_CIS_MODE[c.mode] || humanizeEnum(c.mode);
    const chemSub = c.is_gap ? 'RNase-H Gapmer ASO' : "Steric 2'-MOE SSO";
    return `<tr tabindex="0" data-select-iv="${c.ord}" aria-selected="${isSel?'true':'false'}" class="cursor-pointer focus:bg-[var(--content)] align-top ${activeCls}">
      <td class="py-1.5 px-1.5 font-mono tabular-nums text-[var(--muted-foreground)]">${c.ord}</td>
      <td class="py-1.5 px-2 whitespace-nowrap"><div class="font-mono"><strong class="font-bold text-[var(--foreground)]">${esc(c.gene)} &middot; #${c.rk}</strong> ${c.lead ? '<span class="text-[var(--success)] font-bold text-xs" title="Promoted Lead Window">&#9733; Lead</span>' : '<span class="text-[var(--muted-foreground)] text-xs">Alt</span>'}</div><div class="font-mono text-xs text-[var(--muted-foreground)]">${esc(c.sc)} &middot; ${esc(SHORT_CIS_ROLE[c.role] || humanizeEnum(c.role))}</div></td>
      <td class="py-1.5 px-2 font-mono whitespace-nowrap"><div class="text-[var(--foreground)]">${esc(c.iv)}</div><div class="text-[var(--muted-foreground)] text-xs tabular-nums">${c.len}bp &middot; ${c.tm}&deg;C &middot; AVI ${c.avi}</div></td>
      <td class="hidden xl:table-cell py-1.5 px-2 whitespace-nowrap" title="${esc(humanizeEnum(c.mode))}"><div class="font-medium text-[var(--foreground)]">${esc(shortMode)}</div><div class="font-mono text-xs text-[var(--muted-foreground)]">${esc(chemSub)}</div></td>
      <td class="py-1.5 px-2 text-right whitespace-nowrap"><div>${shortIvBadge(c)}</div><div class="font-mono text-xs text-[var(--muted-foreground)] mt-0.5">${esc(flagLine)}</div></td>
    </tr>`;
  }).join('') : `<tr><td colspan="5" class="py-6 px-4 text-center text-[var(--muted-foreground)]">No GRCh38 intervals match active filters. <button type="button" data-reset-intervals="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></td></tr>`;
  renderIntervalDetail(rows);
}
function selectInterval(ord, userClick=false){
  const n = Number(ord);
  if(!n || !DATA_CIS.some(x => x.ord === n)) return;
  selectedIvOrd = n;
  renderIntervals();
  if(userClick){
    commitHistory('replace');
    try {
      if(typeof window !== 'undefined' && window.innerWidth && window.innerWidth < 1024){
        const det = document.getElementById('iv-detail');
        if(det && det.scrollIntoView) det.scrollIntoView({behavior:'smooth', block:'nearest'});
      }
    } catch(_e) {}
  }
}

function resetIntervalFilters(redraw=true){
  const qEl = document.getElementById('iv-search');
  if(qEl) qEl.value = '';
  document.getElementById('iv-status').value = 'ALL';
  document.getElementById('iv-origin').value = 'ALL';
  document.getElementById('iv-leads').checked = false;
  if(redraw) renderIntervals();
}
function jumpToIntervals(pid){
  resetIntervalFilters(false);
  const qEl = document.getElementById('iv-search');
  if(qEl && pid) qEl.value = pid;
  const hitOrd = findBestIvOrd(pid);
  if(hitOrd) selectedIvOrd = hitOrd;
  switchTab('intervals', 'push', pid ? '#intervals/' + encodeURIComponent(pid) : '#intervals');
}

function switchTab(tab, historyMode='push', explicitHash=''){
  activeTab = tab;
  ['home','portfolio','dossiers','intervals','replication'].forEach(t => {
    const el = document.getElementById('view-'+t);
    if(el) el.classList.toggle('hidden', t!==tab);
  });
  document.querySelectorAll('.tab-btn').forEach(btn => {
    const on = btn.dataset.tab === tab;
    const isHome = btn.dataset.tab === 'home';
    const layoutCls = isHome ? 'col-span-2 flex items-center gap-1.5 ' : '';
    btn.setAttribute('aria-selected', on ? 'true' : 'false');
    btn.setAttribute('tabindex', on ? '0' : '-1');
    btn.className = 'tab-btn ' + layoutCls + 'px-2.5 py-1.5 rounded border font-medium text-xs cursor-pointer ' + (on ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)]' : 'bg-[var(--background)] text-[var(--foreground)] border-[var(--border)]');
  });
  const hdrSub = document.getElementById('hdr-sub');
  if(hdrSub) hdrSub.classList.toggle('hidden', tab !== 'home');
  const mdEl = document.getElementById('methodology-drawer');
  if(mdEl) mdEl.classList.toggle('hidden', tab !== 'portfolio');
  const kpiEl = document.getElementById('kpi-bar');
  if(kpiEl){
    kpiEl.className = tab === 'portfolio'
      ? 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5'
      : (tab === 'home' ? 'hidden sm:grid sm:grid-cols-3 lg:grid-cols-6 gap-2.5' : 'hidden');
  }
  if(tab==='home' && typeof renderUpdatesLog === 'function') renderUpdatesLog();
  if(tab==='portfolio'){
    renderPortfolio();
    try {
      const tb = document.getElementById('p-tbody');
      const actRow = tb && tb.querySelector ? tb.querySelector('[data-select-cand="'+selectedId+'"]') : null;
      if(actRow && actRow.scrollIntoView) actRow.scrollIntoView({block:'nearest'});
    } catch(_e) {}
  }
  if(tab==='dossiers') renderDossierMain();
  if(tab==='intervals'){
    renderIntervals();
    try {
      const itb = document.getElementById('iv-tbody');
      const actIv = itb && itb.querySelector ? itb.querySelector('tr[data-select-iv="'+selectedIvOrd+'"]') : null;
      if(actIv && actIv.scrollIntoView) actIv.scrollIntoView({block:'nearest'});
    } catch(_e) {}
  }
  if(tab==='replication' && typeof renderReplicationWorkbench === 'function') renderReplicationWorkbench();
  syncKpiHighlight();
  commitHistory(historyMode, explicitHash);
  if(tab === 'dossiers' && pendingDossierSec){
    const secId = pendingDossierSec;
    pendingDossierSec = '';
    setTimeout(() => {
      const secEl = document.getElementById(secId);
      if(secEl && secEl.scrollIntoView) secEl.scrollIntoView({behavior:'smooth', block:'start'});
    }, 30);
    return;
  }
  try { if(typeof window !== 'undefined' && window.scrollTo) window.scrollTo(0, 0); } catch(_e) {}
}

function restoreHistorySnapshot(snap){
  if(!snap || !snap.tab) return false;
  selectedId = snap.selectedId || 'EALS-030';
  if(typeof dossierId !== 'undefined') dossierId = snap.dossierId || selectedId;
  dossierFromPortfolio = Boolean(snap.dossierFromPortfolio);
  if(typeof dossierSlice !== 'undefined' && snap.dossierSlice) dossierSlice = snap.dossierSlice;
  if(typeof dossierLens !== 'undefined' && snap.dossierLens) dossierLens = snap.dossierLens;
  activeQuick = snap.activeQuick || 'ALL';
  activeEpi = snap.activeEpi || 'ALL';
  activeLens = snap.activeLens || 'ALL';
  setValOf('p-search', snap.pSearch ?? '');
  setValOf('p-origin', snap.pOrigin || 'ALL');
  setValOf('p-dec', snap.pDec || 'ALL');
  setValOf('p-tier', snap.pTier || 'ALL');
  setValOf('p-sort', snap.pSort || 'rank');
  const dr = document.getElementById('contrasts-drawer');
  if(dr) dr.open = Boolean(snap.contrastsOpen);
  activeUpdCat = snap.activeUpdCat || 'ALL';
  setValOf('upd-search', snap.updSearch ?? '');
  setValOf('iv-search', snap.ivSearch ?? '');
  setValOf('iv-status', snap.ivStatus || 'ALL');
  setValOf('iv-origin', snap.ivOrigin || 'ALL');
  const ivL = document.getElementById('iv-leads');
  if(ivL) ivL.checked = Boolean(snap.ivLeads);
  if(snap.selectedIvOrd) selectedIvOrd = Number(snap.selectedIvOrd) || 5;
  if(typeof setRepMode === 'function' && snap.repMode){
    repMode = snap.repMode;
    populateRepFilterOptions();
    document.querySelectorAll('.rep-mode-btn').forEach(b => {
      const on = b.getAttribute('data-rep-mode') === repMode;
      b.className = 'rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer ' + (on ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)]' : 'bg-[var(--background)] text-[var(--foreground)] border-[var(--border)]');
    });
  }
  if(typeof selectedRepKey !== 'undefined' && snap.selectedRepKey) selectedRepKey = snap.selectedRepKey;
  setValOf('rep-search', snap.repSearch ?? '');
  setValOf('rep-filter', snap.repFilter || 'ALL');
  if(typeof repReturnDossier !== 'undefined') repReturnDossier = snap.repReturnDossier || '';
  if(typeof repReturnTab !== 'undefined') repReturnTab = snap.repReturnTab || 'dossiers';
  switchTab(snap.tab, 'none');
  return true;
}

function syncFromHash(fromPop=false){
  const h = location.hash || '';
  if(fromPop && (h === '' || h === '#')){ activeUpdCat = 'ALL'; setValOf('upd-search', ''); switchTab('home', 'none'); return true; }
  if(h === '#home' || h === '#updates'){ if(h === '#home'){ activeUpdCat = 'ALL'; setValOf('upd-search', ''); } switchTab('home', 'none'); return true; }
  const mu = /^#updates[/](.+)$/.exec(h);
  if(mu){ jumpToUpdates(decodeURIComponent(mu[1]), false); return true; }
  if(h === '#subnodes' || h === '#analytics' || h === '#portfolio'){ switchTab('portfolio', 'none'); return true; }
  const mi = /^#intervals(?:[/](.+))?$/.exec(h);
  if(mi){
    resetIntervalFilters(false);
    if(mi[1]){
      const rawIv = decodeURIComponent(mi[1]);
      if(/^([1-9]|1[0-9]|2[0-8])$/.test(rawIv)) selectedIvOrd = Number(rawIv);
      else { setValOf('iv-search', rawIv); const ho = findBestIvOrd(rawIv); if(ho) selectedIvOrd = ho; }
    }
    switchTab('intervals', 'none');
    return true;
  }
  const m = /^#(?:dossier|monograph)[/](.+)$/.exec(h);
  if(m){
    const res = resolveCandidateId(decodeURIComponent(m[1]));
    if(res && DATA_PORT.some(x=>x.id===res.id)){
      if(res.sub) pendingDossierSec = 'sec-subunits';
      dossierId = res.id; selectedId = res.id;
      switchTab('dossiers', 'none');
      return true;
    }
  }
  const mr = /^#replication(?:[/](?:cand[/]([^/]+)|([A-Za-z0-9_.-]+)))?$/.exec(h);
  if(mr && typeof openReplicationTarget === 'function'){
    if(mr[1]){
      const rc = resolveCandidateId(decodeURIComponent(mr[1]));
      const cKey = rc ? rc.id : decodeURIComponent(mr[1]);
      openReplicationTarget('cand', cKey, cKey, 'dossiers', 'none');
    }
    else if(mr[2]){ openReplicationTarget(mr[2].startsWith('DS') ? 'ds' : (mr[2].startsWith('EV-') ? 'ev' : 'run'), mr[2], '', 'dossiers', 'none'); }
    else { switchTab('replication', 'none'); }
    return true;
  }
  return false;
}

document.querySelectorAll('.tab-btn').forEach(b => b.addEventListener('click', () => { if(b.dataset.tab === 'dossiers') dossierFromPortfolio = false; switchTab(b.dataset.tab); }));
document.addEventListener('click', e => {
  const raw = e.target;
  const tgt = raw && raw.closest ? raw : (raw && raw.parentElement && raw.parentElement.closest ? raw.parentElement : null);
  if(!tgt) return;
  const ccBtn = tgt.closest('[data-copy-cmd]');
  if(ccBtn){ e.preventDefault(); const v = ccBtn.getAttribute('data-copy-cmd')||''; if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(v); } const orig = (ccBtn.dataset&&(ccBtn.dataset.orig||(ccBtn.dataset.orig=ccBtn.textContent)))||ccBtn.textContent; ccBtn.textContent='Copied \u2713'; setTimeout(()=>{ ccBtn.textContent = orig; }, 1400); return; }
  const tgBtn = tgt.closest('[data-toggle-detail-gate]');
  if(tgBtn){
    e.preventDefault(); e.stopPropagation();
    const gk = tgBtn.getAttribute('data-toggle-detail-gate')||'';
    const open = !expandedDetailGates[gk];
    expandedDetailGates[gk] = open;
    const bodyEl = document.getElementById(tgBtn.getAttribute('aria-controls')||'');
    if(bodyEl) bodyEl.setAttribute('data-clamped', open ? 'false' : 'true');
    tgBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    tgBtn.innerHTML = open ? 'Collapse &uarr;' : (tgBtn.getAttribute('data-more-lbl') || 'Read full details &darr;');
    return;
  }
  const csBtn = tgt.closest('[data-copy-sha]');
  if(csBtn){ e.preventDefault(); const v = csBtn.getAttribute('data-copy-sha')||''; if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(v); } const orig = (csBtn.dataset&&(csBtn.dataset.orig||(csBtn.dataset.orig=csBtn.textContent)))||csBtn.textContent; csBtn.textContent='Copied \u2713'; setTimeout(()=>{ csBtn.textContent = orig; }, 1400); return; }
  const ucBtn = tgt.closest('[data-upd-cat]');
  if(ucBtn){ e.preventDefault(); activeUpdCat = ucBtn.getAttribute('data-upd-cat') || 'ALL'; renderUpdatesLog(); commitHistory('replace'); return; }
  const ruBtn = tgt.closest('[data-reset-updates]');
  if(ruBtn){ e.preventDefault(); activeUpdCat = 'ALL'; const uq = document.getElementById('upd-search'); if(uq) uq.value = ''; renderUpdatesLog(); commitHistory('replace', '#home'); return; }
  const juBtn = tgt.closest('[data-jump-updates]');
  if(juBtn){ e.preventDefault(); e.stopPropagation(); jumpToUpdates(juBtn.getAttribute('data-jump-updates')); return; }
  const hfBtn = tgt.closest('[data-home-flagships]');
  if(hfBtn){ e.preventDefault(); dossierSlice = 'T12'; dossierLens = 'ALL'; openDossier('EALS-030'); return; }
  const hcBtn = tgt.closest('[data-home-contrasts]');
  if(hcBtn){ e.preventDefault(); const dr = document.getElementById('contrasts-drawer'); if(dr) dr.open = true; switchTab('portfolio', 'push'); if(dr && dr.scrollIntoView){ try{ dr.scrollIntoView({behavior:'smooth', block:'start'}); }catch(_e){} } return; }
  const reBtn = tgt.closest('[data-open-rep-ev]');
  if(reBtn){ e.preventDefault(); e.stopPropagation(); openReplicationTarget('ev', reBtn.getAttribute('data-open-rep-ev'), activeTab==='dossiers'?dossierId:(activeTab==='portfolio'?selectedId:''), activeTab); return; }
  const rrBtn = tgt.closest('[data-open-rep-run]');
  if(rrBtn){ e.preventDefault(); e.stopPropagation(); openReplicationTarget('run', rrBtn.getAttribute('data-open-rep-run'), activeTab==='dossiers'?dossierId:(activeTab==='portfolio'?selectedId:''), activeTab); return; }
  const rdBtn = tgt.closest('[data-open-rep-ds]');
  if(rdBtn){ e.preventDefault(); e.stopPropagation(); openReplicationTarget('ds', rdBtn.getAttribute('data-open-rep-ds'), activeTab==='dossiers'?dossierId:(activeTab==='portfolio'?selectedId:''), activeTab); return; }
  const rcBtn = tgt.closest('[data-jump-rep-cand]');
  if(rcBtn){ e.preventDefault(); e.stopPropagation(); openReplicationTarget('cand', rcBtn.getAttribute('data-jump-rep-cand'), rcBtn.getAttribute('data-jump-rep-cand'), activeTab); return; }
  const rmBtn = tgt.closest('[data-rep-mode]');
  if(rmBtn){ e.preventDefault(); setRepMode(rmBtn.getAttribute('data-rep-mode')); commitHistory('replace'); return; }
  const rsRow = tgt.closest('[data-rep-select]');
  if(rsRow){ selectedRepKey = rsRow.getAttribute('data-rep-select'); renderReplicationWorkbench(); commitHistory('replace'); return; }
  const dgBtn = tgt.closest('[data-rep-dag]');
  if(dgBtn){ e.preventDefault(); const [m,f] = dgBtn.getAttribute('data-rep-dag').split('|'); setRepMode(m); document.getElementById('rep-filter').value = f; renderReplicationWorkbench(); commitHistory('replace'); return; }
  const rrpBtn = tgt.closest('[data-reset-rep]');
  if(rrpBtn){ e.preventDefault(); repReturnDossier=''; repReturnTab='dossiers'; document.getElementById('rep-search').value=''; setRepMode('runs'); commitHistory('replace', '#replication'); return; }
  const dlBtn = tgt.closest('[data-dl-reg]');
  if(dlBtn){ e.preventDefault(); exportRegistryBlob(dlBtn.getAttribute('data-dl-reg')); return; }
  const dsBtn = tgt.closest('[data-open-dossier-sec]');
  if(dsBtn){ e.preventDefault(); e.stopPropagation(); const [did, sid] = (dsBtn.getAttribute('data-open-dossier-sec')||'').split('|'); dossierFromPortfolio = (activeTab === 'portfolio'); pendingDossierSec = sid || ''; openDossier(did); return; }
  const scBtn = tgt.closest('[data-scroll-sec]');
  if(scBtn){ e.preventDefault(); const el = document.getElementById(scBtn.getAttribute('data-scroll-sec')||''); if(el && el.scrollIntoView) el.scrollIntoView({behavior:'smooth', block:'start'}); return; }
  const wBtn = tgt.closest('[data-open-dossier]');
  if(wBtn){ e.preventDefault(); e.stopPropagation(); dossierFromPortfolio = (activeTab === 'portfolio' || (activeTab === 'dossiers' && dossierFromPortfolio)); pendingDossierSec = ''; openDossier(wBtn.getAttribute('data-open-dossier')); return; }
  const wsBtn = tgt.closest('[data-dossier-slice]');
  if(wsBtn){ e.preventDefault(); setDossierSlice(wsBtn.getAttribute('data-dossier-slice')); commitHistory('replace'); return; }
  const rdnBtn = tgt.closest('[data-reset-d-nav]');
  if(rdnBtn){ e.preventDefault(); resetDossierNav(); commitHistory('replace'); return; }
  const plBtn = tgt.closest('[data-p-lens]');
  if(plBtn){ e.preventDefault(); activeQuick = ''; activeLens = plBtn.getAttribute('data-p-lens') || 'ALL'; renderPortfolio(); commitHistory('replace'); return; }
  const trBtn = tgt.closest('[data-toggle-d-rail]');
  if(trBtn){ e.preventDefault(); toggleDossierRail(); return; }
  const jiBtn = tgt.closest('[data-jump-intervals]');
  if(jiBtn){ e.preventDefault(); e.stopPropagation(); jumpToIntervals(jiBtn.getAttribute('data-jump-intervals')); return; }
  const riBtn = tgt.closest('[data-reset-intervals]');
  if(riBtn){ e.preventDefault(); resetIntervalFilters(true); commitHistory('replace', '#intervals'); return; }
  const tBtn = tgt.closest('[data-switch-tab]');
  if(tBtn){ e.preventDefault(); switchTab(tBtn.getAttribute('data-switch-tab')); return; }
  const qBtn = tgt.closest('[data-quick-filter]');
  if(qBtn){ e.preventDefault(); quickFilter(qBtn.getAttribute('data-quick-filter')); return; }
  const rBtn = tgt.closest('[data-reset-filters]');
  if(rBtn){ e.preventDefault(); resetPortfolioFilters(true, 'ALL'); commitHistory('replace', '#portfolio'); return; }
  const cRow = tgt.closest('[data-select-cand]');
  if(cRow){ selectCand(cRow.getAttribute('data-select-cand'), true); return; }
  const ivRow = tgt.closest('[data-select-iv]');
  if(ivRow){ selectInterval(ivRow.getAttribute('data-select-iv'), true); }
});
document.addEventListener('keydown', e => {
  const act = document.activeElement;
  const tag = act && act.tagName ? String(act.tagName).toUpperCase() : '';
  if(act && act.dataset && act.dataset.tab && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')){
    const tabs = ['home','portfolio','dossiers','intervals','replication'];
    const ti = tabs.indexOf(act.dataset.tab);
    if(ti >= 0){
      e.preventDefault();
      const nextTab = tabs[(ti + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
      switchTab(nextTab);
      const nb = document.getElementById('tab-btn-' + nextTab);
      if(nb && nb.focus) nb.focus();
      return;
    }
  }
  if(activeTab === 'dossiers' && !e.ctrlKey && !e.metaKey && !e.altKey && tag !== 'INPUT' && tag !== 'SELECT' && tag !== 'TEXTAREA' && (e.key === '[' || e.key === ']')){
    const fl = (typeof getFilteredDossierList === 'function') ? getFilteredDossierList() : [];
    const pool = (fl.length >= 2 && fl.some(x => x.id === dossierId)) ? fl : DATA_PORT;
    const idx = pool.findIndex(x => x.id === dossierId);
    if(idx >= 0){
      e.preventDefault();
      const step = e.key === '[' ? -1 : 1;
      openDossier(pool[(idx + step + pool.length) % pool.length].id);
      return;
    }
  }
  if(e.key !== 'Enter' && e.key !== ' ') return;
  const raw = e.target;
  const dgBtn = raw && raw.closest ? raw.closest('[data-rep-dag]') : null;
  if(dgBtn && raw === dgBtn){ e.preventDefault(); const [m,f] = dgBtn.getAttribute('data-rep-dag').split('|'); setRepMode(m); document.getElementById('rep-filter').value = f; renderReplicationWorkbench(); return; }
  const rsRow = raw && raw.closest ? raw.closest('tr[data-rep-select]') : null;
  if(rsRow && raw === rsRow){ e.preventDefault(); selectedRepKey = rsRow.getAttribute('data-rep-select'); renderReplicationWorkbench(); return; }
  const cRow = raw && raw.closest ? raw.closest('tr[data-select-cand]') : null;
  if(cRow && raw === cRow){ e.preventDefault(); selectCand(cRow.getAttribute('data-select-cand'), true); return; }
  const ivRow = raw && raw.closest ? raw.closest('tr[data-select-iv]') : null;
  if(ivRow && raw === ivRow){ e.preventDefault(); selectInterval(ivRow.getAttribute('data-select-iv'), true); }
});
['p-search','p-origin','p-dec','p-tier','p-sort'].forEach(id => {
  const el = document.getElementById(id);
  const fn = () => { activeQuick = ''; if(id!=='p-sort' && id!=='p-search') activeEpi = 'ALL'; renderPortfolio(); commitHistory('replace'); };
  el.addEventListener('input', fn);
  el.addEventListener('change', fn);
});
['iv-status','iv-origin','iv-leads'].forEach(id => document.getElementById(id).addEventListener('change', () => { renderIntervals(); commitHistory('replace'); }));
document.getElementById('iv-search').addEventListener('input', () => { renderIntervals(); commitHistory('replace'); });
document.getElementById('d-search').addEventListener('input', () => { renderDossierSidebar(); commitHistory('replace'); });
const dLensEl = document.getElementById('d-lens');
if(dLensEl) dLensEl.addEventListener('change', e => { setDossierLens(e.target.value); commitHistory('replace'); });
document.getElementById('d-mobile-select').addEventListener('change', e => openDossier(e.target.value));
const repS = document.getElementById('rep-search');
if(repS) repS.addEventListener('input', () => { renderReplicationWorkbench(); commitHistory('replace'); });
const repF = document.getElementById('rep-filter');
if(repF) repF.addEventListener('change', () => { renderReplicationWorkbench(); commitHistory('replace'); });
const updS = document.getElementById('upd-search');
if(updS) updS.addEventListener('input', () => { renderUpdatesLog(); commitHistory('replace'); });
const sbBody = document.getElementById('sandbox-body');
if(sbBody){
  sbBody.addEventListener('input', e => {
    if(e.target && e.target.id === 'sb-m-pre') document.getElementById('sb-m-p0').value = e.target.value;
    updateSandboxes();
  });
  sbBody.addEventListener('change', e => {
    if(e.target && e.target.id === 'sb-m-pre') document.getElementById('sb-m-p0').value = e.target.value;
    updateSandboxes();
  });
}
window.addEventListener('popstate', e => {
  isRestoringHistory = true;
  try {
    if(!(e.state && restoreHistorySnapshot(e.state))){
      if(!syncFromHash(true)) switchTab('home', 'none');
    }
  } finally {
    isRestoringHistory = false;
  }
  commitHistory('replace');
});
window.addEventListener('hashchange', () => {
  if(isRestoringHistory) return;
  const curH = (!location.hash || location.hash === '#') ? '#home' : location.hash;
  if(history.state && history.state.hash === curH) return;
  isRestoringHistory = true;
  try {
    if(!syncFromHash(true)) switchTab('home', 'none');
  } finally {
    isRestoringHistory = false;
  }
  commitHistory('replace');
});
document.addEventListener('focusin', e => {
  const cl = e.target && e.target.closest ? e.target.closest('.gate-clamp[data-clamped="true"]') : null;
  if(!cl || (e.target.offsetTop + e.target.offsetHeight <= cl.clientHeight)) return;
  const btn = cl.parentElement ? cl.parentElement.querySelector('[data-toggle-detail-gate]') : null;
  if(btn) btn.click();
});
window.addEventListener('resize', () => { if(typeof syncDetailClamps === 'function') syncDetailClamps(); });
renderUpdatesLog(); renderContrastsTable(); renderPortfolio(); renderIntervals();
if(typeof renderRepDag === 'function'){ renderRepDag(); renderRepOverlap(); setRepMode('runs'); initSandboxes(); }
if(!syncFromHash(false)) switchTab('home', 'none');
commitHistory('replace');
</script>
</body>
</html>
"""
