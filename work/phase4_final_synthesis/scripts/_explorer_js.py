"""Client-side interactive logic for the ExploreALS v1.1 Generative UI Explorer (pure semantic CSS vars + vector SVG)."""
from __future__ import annotations

EXPLORER_JS_BODY = """
const TRL_NUM = {TRL_6_PH2B_SUBGROUP_BIOLOGIC:6,TRL_5_HUMAN_ALS_PK_PD_PROVEN:5,TRL_4_ACTIVE_PH1_CLASS_OR_NCE:4,TRL_3_PRECLINICAL_SSO_COORDINATE:3,TRL_2_PRECLINICAL_MODALITY_DISCOVERY:2,TRL_1_TARGET_TOOL_PROBE_WATCHLIST:1,PROTOCOL_COMPANION_NA:0};
const NYGC_GENE_TO_ID = {ATG4B:'DN-01',KALRN:'DN-02',PTPRT:'DN-03',CELF5:'DN-04',PRUNE2:'DN-05',PFKP:'DN-06',TRAPPC12:'DN-07',ELK1:'DN-08',DLGAP1:'DN-09'};
let selectedId = 'S06';
let activeTab = 'portfolio';
let activeQuick = 'ALL';
let activeEpi = 'ALL';
let activeLens = 'ALL';

function esc(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function decBadge(d){
  if(d==='KEEP_CORE') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Causal human ALS genetics and/or human TDP-43 pathology + functional rescue">Keep &middot; Core</span>';
  if(d==='KEEP_EXPLORATORY_UNPROVEN') return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap" title="Untested preclinical/biofluid triage queue — prospective kill-gate required">Keep &middot; Exploratory</span>';
  if(d==='RECLASSIFY_BENCHMARK_OR_BIOMARKER') return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--primary)] border border-[var(--primary)] text-xs whitespace-nowrap" title="Approved SOC drug, PD calibrator, or fluid staging biomarker">Benchmark</span>';
  return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="Scientifically falsified by human RCT futility, CNS PK/safety wall, or confounding collapse">Drop &middot; Falsified</span>';
}
function statusBadge(st){
  if(st==='PASS_CLEAN_GE2MM') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Zero 0mm, 1mm, wobble, bulge, or 18-nt sub-core off-target hits on constrained CNS genes">Pass &middot; Clean &ge;2mm</span>';
  if(st.startsWith('CAUTION')) return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap" title="1mm, wobble, or 25bp-SS 2mm hit on non-constrained genes — empirical microwalk required">Caution &middot; 1mm/Wob</span>';
  if(st.startsWith('WARN')) return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="1mm, wobble, or 1-nt bulge hit on a LoF-intolerant (pLI >= 0.9) CNS gene">Warn &middot; CNS Hit</span>';
  if(st.startsWith('FAIL')) return '<span class="px-1.5 py-0.5 rounded font-mono font-bold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="Exact 0-mismatch off-target hybridization hit across GENCODE v46">Fail &middot; 0mm</span>';
  return '<span class="text-[var(--muted-foreground)] font-mono text-xs">None</span>';
}
function tdlBadge(tdl){
  const col = tdl==='Tclin' ? 'text-[var(--success)] border-[var(--success)]' : (tdl==='Tchem' ? 'text-[var(--primary)] border-[var(--primary)]' : 'text-[var(--muted-foreground)] border-[var(--border)]');
  return `<span class="px-1.5 py-0.5 rounded font-mono font-semibold border ${col} text-xs whitespace-nowrap" title="NIH Illuminating the Druggable Genome Target Development Level">IDG ${esc(tdl)}</span>`;
}
function tsaSubBadge(tsa){
  if(tsa==='LOW_CONSTRAINT') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Low heterozygous pLoF constraint in gnomAD v4; distinct from biallelic recessive phenotypes">&#10003; Low Het-pLoF Constraint</span>';
  if(tsa==='SELECTIVITY_GATE') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap">&#9651; Selectivity / Sign Gate</span>';
  if(tsa==='SYSTEMIC_IMMUNE') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap">&#9888; Systemic Sepsis / SLE Risk</span>';
  return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap">&#9888; Pan-Essential / Lethal</span>';
}
function shortTier(t){return t.replace('TIER_1_ACTIONABLE_NOW','T1 Actionable').replace('TIER_2_FOCUSED_GATE_FIRST','T2 Gate First').replace('TIER_3_EXPLORATORY_DISCOVERY','T3 Discovery').replace('COMPANION_PROTOCOL_ONLY','Companion').replace('BIOMARKER_BENCHMARK_ONLY','Biomarker/SOC').replace('DROPPED_FALSIFIED_EXCLUDED','Dropped');}
function shortTrl(t){return t==='PROTOCOL_COMPANION_NA'?'N/A':t.split('_').slice(0,2).join(' ');}

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

function renderContrastsTable(){
  const tb = document.getElementById('contrasts-tbody');
  const dr = document.getElementById('contrasts-drawer');
  if(dr){
    try {
      dr.open = !(typeof window !== 'undefined' && window.innerWidth && window.innerWidth < 1280);
    } catch(_e) { dr.open = true; }
  }
  if(!tb || typeof DATA_CONTRASTS === 'undefined') return;
  tb.innerHTML = DATA_CONTRASTS.map(row => {
    const ctx = row.ids[0] || 'S06';
    const idBtns = row.ids.map(cid => `<button type="button" data-open-dossier="${esc(cid)}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono font-semibold text-[var(--link)] text-xs cursor-pointer whitespace-nowrap">${esc(cid)} &rarr;</button>`).join(' ');
    return `<tr class="align-top hover:bg-[var(--content)]">
      <td class="py-2 px-2"><div class="flex flex-wrap gap-1">${idBtns}</div></td>
      <td class="py-2 px-2 font-semibold whitespace-nowrap">${esc(row.domain)}</td>
      <td class="py-2 px-2 text-[var(--muted-foreground)] leading-snug">${escLink(row.naive, ctx)}</td>
      <td class="py-2 px-2 leading-snug">${escLink(row.finding, ctx)}</td>
      <td class="py-2 px-2 text-[var(--muted-foreground)] leading-snug">${escLink(row.gate, ctx)}</td>
    </tr>`;
  }).join('');
}

function renderPortfolio(){
  renderLensBar();
  const q = document.getElementById('p-search').value.trim().toLowerCase();
  const orig = document.getElementById('p-origin').value;
  const dec = document.getElementById('p-dec').value;
  const tier = document.getElementById('p-tier').value;
  const sortBy = document.getElementById('p-sort').value;
  const lensObj = (activeLens !== 'ALL' && typeof DATA_LENSES !== 'undefined') ? DATA_LENSES.find(x => x.k === activeLens) : null;
  let rows = DATA_PORT.filter(r => {
    if(lensObj && !lensObj.ids.includes(r.id)) return false;
    if(orig!=='ALL' && r.sub!==orig) return false;
    if(dec!=='ALL' && r.dec!==dec) return false;
    if(activeEpi!=='ALL' && r.epi!==activeEpi) return false;
    if(tier==='TIER_12' && r.tier!=='TIER_1_ACTIONABLE_NOW' && r.tier!=='TIER_2_FOCUSED_GATE_FIRST') return false;
    if(tier!=='ALL' && tier!=='TIER_12' && r.tier!==tier) return false;
    const sumObj = (typeof DATA_SUM !== 'undefined' && DATA_SUM[r.id]) ? DATA_SUM[r.id] : null;
    const sumTxt = sumObj ? ((sumObj.hyp || '') + ' ' + (sumObj.edge_text || '') + ' ' + sumObj.verdict + ' ' + sumObj.sub + ' ' + sumObj.proves + ' ' + sumObj.disproves) : '';
    if(q && !(r.id+' '+r.name+' '+r.mod+' '+r.hurdles+' '+r.sub+' '+(r.crowd||'')+' '+humanizeEnum(r.basis||'')+' '+sumTxt).toLowerCase().includes(q)) return false;
    return true;
  });
  const hurdleKey = r => r.tier==='DROPPED_FALSIFIED_EXCLUDED'?99:(r.tier==='BIOMARKER_BENCHMARK_ONLY'?98:(r.tier==='COMPANION_PROTOCOL_ONLY'?97:r.hcnt));
  if(sortBy==='bio') rows.sort((a,b)=>a.brk-b.brk);
  else if(sortBy==='trl') rows.sort((a,b)=>(TRL_NUM[b.trl]-TRL_NUM[a.trl])||(a.rk-b.rk));
  else if(sortBy==='hurdles') rows.sort((a,b)=>(hurdleKey(a)-hurdleKey(b))||(a.rk-b.rk));
  else rows.sort((a,b)=>a.rk-b.rk);
  const epiNote = activeEpi !== 'ALL' ? ` \u00b7 ${humanizeEnum(activeEpi)}` : '';
  const lensNote = lensObj ? ` \u00b7 ${lensObj.lbl.split(' \u00b7 ')[0]}` : '';
  document.getElementById('p-count').textContent = `${rows.length} / ${DATA_PORT.length}${epiNote}${lensNote}`;
  if(!DATA_PORT.some(x=>x.id===selectedId)) selectedId = DATA_PORT[0].id;
  const selHidden = rows.length > 0 && !rows.some(r=>r.id===selectedId);
  document.getElementById('p-tbody').innerHTML = rows.length ? rows.map(r => {
    const active = r.id===selectedId ? 'bg-[var(--content)]' : 'hover:bg-[var(--content)]';
    const dosBtn = DATA_MONOGRAPHS[r.id]
      ? `<button type="button" data-open-dossier="${esc(r.id)}" class="px-2 py-0.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-semibold text-xs cursor-pointer">Monograph &rarr;</button>`
      : `<button type="button" data-open-dossier="${esc(r.id)}" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Summary &rarr;</button>`;
    const rkPrimary = sortBy==='bio' ? `#${r.brk}` : `#${r.rk}`;
    const rkSecondary = r.rk !== r.brk
      ? `<div class="text-xs font-semibold text-[var(--primary)]">${sortBy==='bio' ? 'Act #'+r.rk : 'Bio #'+r.brk}</div>`
      : (r.dec !== 'DROP' && r.dec !== 'RECLASSIFY_BENCHMARK_OR_BIOMARKER' ? '<div class="text-xs opacity-80">= Bio</div>' : '');
    return `<tr tabindex="0" data-select-cand="${esc(r.id)}" aria-selected="${r.id===selectedId?'true':'false'}" class="cursor-pointer focus:bg-[var(--content)] ${active}">
      <td class="py-2 px-2 font-mono tabular-nums whitespace-nowrap text-[var(--muted-foreground)]" title="Portfolio Actionability #${r.rk} · Pure Biological Evidence #${r.brk}"><div>${rkPrimary}</div>${rkSecondary}</td>
      <td class="py-2 px-1.5 font-mono font-semibold whitespace-nowrap">${esc(r.id)}</td>
      <td class="py-2 px-2"><div class="font-medium">${esc(r.name)}</div><div class="text-[var(--muted-foreground)] text-xs">${esc(humanizeEnum(r.sub))} &middot; Track ${esc(r.trk)}</div></td>
      <td class="py-2 px-1.5">${decBadge(r.dec)}</td>
      <td class="hidden xl:table-cell py-2 px-1.5 text-xs whitespace-nowrap">${esc(shortTier(r.tier))}</td>
      <td class="hidden xl:table-cell py-2 px-1.5 font-mono text-xs whitespace-nowrap">${esc(shortTrl(r.trl))}</td>
      <td class="hidden xl:table-cell py-2 px-1.5 font-mono tabular-nums text-right">${r.hcnt}</td>
      <td class="py-2 px-2 text-right whitespace-nowrap">${dosBtn}</td>
    </tr>`;
  }).join('') : `<tr><td colspan="8" class="py-6 px-4 text-center text-[var(--muted-foreground)]">No candidates match active filters. <button type="button" data-reset-filters="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></td></tr>`;
  renderDetail(selHidden);
  syncKpiHighlight();
}

function renderDetail(selHidden=false){
  const r = DATA_PORT.find(x=>x.id===selectedId) || DATA_PORT[0];
  const hiddenBanner = selHidden
    ? `<div class="p-2 rounded bg-[var(--background)] border border-dashed border-[var(--warning)] flex items-center justify-between gap-2 text-xs"><span class="text-[var(--warning)] font-mono">Pinned dossier #${r.rk} ${esc(r.id)} is outside active table filter</span><button type="button" data-reset-filters="1" class="text-[var(--link)] underline font-mono cursor-pointer shrink-0">Show all (59)</button></div>`
    : '';
  const w = DATA_MONOGRAPHS[r.id];
  const s = (typeof DATA_SUM !== 'undefined' && DATA_SUM[r.id]) ? DATA_SUM[r.id] : null;
  const isDrop = r.dec === 'DROP';
  const evRows = DATA_EV[r.id] || [];
  const accTokens = [...new Set(evRows.flatMap(e => (e.accs||'').split(' \u00b7 ').map(x=>x.trim()).filter(Boolean)))].slice(0, 6);
  const gPills = genePortalPills(r.id);
  const candCis = DATA_CIS.filter(c => c.pid===r.id || c.sc===r.id);
  const leadCis = r.iv!=='NONE' ? DATA_CIS.find(c => c.iv===r.iv) : (candCis[0] || null);
  let cisBox = '';
  if(leadCis){
    const loP = Math.max(1, Number(leadCis.lo)-250), hiP = Number(leadCis.hi)+250;
    const ensUrl = `https://www.ensembl.org/Homo_sapiens/Location/View?r=${leadCis.chr.replace('chr','')}:${leadCis.lo}-${leadCis.hi}`;
    const atlUrl = `https://deepmind.google.com/science/alphagenome/atlas?q=${leadCis.chr}:${loP}-${hiP}&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE`;
    const ucscUrl = `https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position=${leadCis.chr}:${loP}-${hiP}`;
    const lbl = r.iv !== 'NONE' ? `Promoted GRCh38 Lead (${leadCis.len}bp, Tm=${leadCis.tm}&deg;C, AVI=${leadCis.avi}):` : `GRCh38 Cis-Interval Walk (${candCis.length} ${esc(leadCis.gene)} intervals):`;
    cisBox = `<div class="p-2.5 rounded border border-[var(--border)] bg-[var(--background)] space-y-1">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <span class="text-[var(--muted-foreground)] font-semibold">${lbl}</span>
        ${statusBadge(leadCis.st)}
      </div>
      <div class="font-mono flex flex-wrap items-center justify-between gap-2">
        <span>${mkExtA(ensUrl, esc(leadCis.iv))} &middot; ${mkExtA(atlUrl, 'AlphaGenome &nearr;')} &middot; ${mkExtA(ucscUrl, 'UCSC &nearr;')}</span>
        <button type="button" data-jump-intervals="${esc(r.id)}" class="text-[var(--link)] hover:underline cursor-pointer">Tab 2 (${candCis.length}) &rarr;</button>
      </div>
    </div>`;
  }
  const candSub = DATA_SUB.filter(x => x.par === r.id);
  const subBox = candSub.length ? `<div class="p-2.5 rounded border border-[var(--border)] bg-[var(--background)] flex items-center justify-between gap-2 flex-wrap">
    <span><strong class="font-mono">Unbundled Sub-Nodes (${candSub.length} Genes):</strong> <span class="text-[var(--muted-foreground)] font-mono">${candSub.map(x=>esc(x.gene)).join(', ')}</span></span>
    <button type="button" data-jump-subnodes="${esc(r.id)}" class="font-mono text-[var(--link)] hover:underline cursor-pointer">Explore in Tab 3 &rarr;</button>
  </div>` : '';
  const priorBadge = r.prior && r.prior !== 'NONE'
    ? `<span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] font-mono">&#9671; [MODEL_PRIOR]</span> ${esc(formatPrior(r.prior))}`
    : `<span class="px-1 rounded border border-[var(--success)] text-[var(--success)] font-mono">&#9679; [MEASURED]</span> ${esc(formatPrior(r.prior))}`;
  const hurdles = r.hurdles && r.hurdles!=='NONE' ? r.hurdles.split(';').map(h=>`<li class="text-xs break-words">${esc(formatHurdle(h))}</li>`).join('') : '<li class="text-[var(--muted-foreground)] text-xs">None (Calibration standard or fluid biomarker)</li>';
  const tailBlocks = isDrop
    ? `<div class="border-t border-[var(--card-border)] pt-2"><div class="text-[var(--error)] font-mono font-semibold mb-0.5">&#10005; Decisive Falsifying Counterevidence:</div><p class="leading-relaxed break-words">${escLink(s ? s.disproves : humanizeEnum(r.epi), r.id)}</p></div>`
    : `<div><span class="text-[var(--muted-foreground)] font-semibold">Active Hurdles (${r.hcnt}):</span><ul class="list-disc pl-4 mt-1 space-y-1">${hurdles}</ul></div>
       <div class="border-t border-[var(--card-border)] pt-2"><div class="text-[var(--muted-foreground)] font-semibold mb-0.5">Discriminating Next Test:</div><div class="leading-relaxed break-words">${formatNextTest(r.nxt, r.id)}</div></div>`;
  const pubMonoLink = (typeof window !== 'undefined' && window.PUBLIC_WEB_EXPORT && w)
    ? `<a href="./monographs/${esc(r.id)}.html" class="px-2 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs shrink-0" title="Open lightweight standalone monograph page">Page &nearr;</a>`
    : '';
  const crowdChip = (r.crowd && !r.crowd.startsWith('N/A')) ? `<span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)] whitespace-nowrap">${esc(r.crowd)}</span>` : '';
  document.getElementById('p-detail').innerHTML = `${hiddenBanner}
    <div class="flex flex-wrap items-start justify-between gap-2 border-b border-[var(--card-border)] pb-2.5">
      <div>
        <div class="flex items-center gap-2 flex-wrap"><span class="font-mono font-bold text-sm" title="Portfolio Actionability Rank #${r.rk} · Pure Biological Evidence Rank #${r.brk}">#${r.rk} <span class="font-normal text-xs text-[var(--muted-foreground)]">(Bio #${r.brk})</span> &middot; ${esc(r.id)}</span> ${decBadge(r.dec)} ${crowdChip} ${gPills?`<span class="font-mono text-xs">${gPills}</span>`:''}</div>
        <div class="text-sm font-semibold mt-1">${esc(r.name)}</div>
        <div class="text-[var(--muted-foreground)] text-xs mt-0.5">${esc(humanizeEnum(r.sub))} &middot; Track ${esc(r.trk)} &middot; ${esc(humanizeEnum(r.basis))}</div>
      </div>
      <div class="flex items-center gap-1.5 shrink-0">${pubMonoLink}<button type="button" data-open-dossier="${esc(r.id)}" class="px-2.5 py-1.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-semibold text-xs shrink-0 cursor-pointer">${w?'Open Full Monograph &rarr;':`Open Summary Dossier (${evRows.length}) &rarr;`}</button></div>
    </div>
    <div class="space-y-2.5 text-xs">
      ${typeof renderEdgeRibbon === 'function' ? renderEdgeRibbon(s, r.id) : ''}
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-0.5">
          <div class="text-[var(--muted-foreground)] font-mono">Target Modality (TPP)</div>
          <div class="font-medium break-words">${escLink(formatModality(r.mod), r.id)}</div>
        </div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-0.5">
          <div class="text-[var(--muted-foreground)] font-mono">Readiness &amp; Experimental Gate</div>
          <div class="font-mono">${esc(humanizeEnum(r.trl))}</div>
          <div class="text-[var(--muted-foreground)]">${esc(humanizeEnum(r.gate))}</div>
        </div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-0.5">
          <div class="text-[var(--muted-foreground)] font-mono">Causal Sign &amp; Epistemic State</div>
          <div class="font-medium">${esc(s ? s.causal : humanizeEnum(r.epi))}</div>
          <div class="text-[var(--muted-foreground)] font-mono">${esc(humanizeEnum(r.epi))}</div>
        </div>
        <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-0.5">
          <div class="flex items-center justify-between gap-1"><span class="text-[var(--muted-foreground)] font-mono">FAIR Provenance (${evRows.length} Contrasts)</span><button type="button" data-jump-rep-cand="${esc(r.id)}" class="text-[var(--link)] hover:underline font-mono text-xs cursor-pointer">Audit SHA-256 &rarr;</button></div>
          <div class="font-mono break-words">${accTokens.length ? escLink(accTokens.join(' \u00b7 '), r.id) : '<span class="text-[var(--muted-foreground)]">Registry summary</span>'}</div>
        </div>
      </div>
      ${cisBox}
      ${subBox}
      <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] break-words">${priorBadge}</div>
      <div class="border-t border-[var(--card-border)] pt-2"><div class="text-[var(--primary)] font-semibold mb-0.5">Candidate &amp; Biological Hypothesis:</div><p class="leading-relaxed break-words">${escLink(s ? s.hyp : '', r.id)}</p></div>
      <div class="border-t border-[var(--card-border)] pt-2"><div class="text-[var(--muted-foreground)] font-semibold mb-0.5">Adjudication Rationale:</div><p class="leading-relaxed break-words">${escLink(s ? s.verdict : '', r.id)}</p></div>
      ${w?`<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--success)] space-y-1"><div class="font-mono font-bold text-[var(--success)]">&#10003; Advance Gate (Go Criteria)</div>${typeof formatGateList === 'function' ? formatGateList(w.verdict_box.pass_gate, r.id, false) : `<div class="leading-snug">${escLink(w.verdict_box.pass_gate, r.id)}</div>`}</div>`:''}
      ${tailBlocks}
    </div>`;
}
function selectCand(id, userClick=false){
  selectedId = id;
  dossierId = id;
  renderPortfolio();
  if(userClick){
    try {
      if(typeof window !== 'undefined' && window.innerWidth && window.innerWidth < 1024){
        const det = document.getElementById('p-detail');
        if(det && det.scrollIntoView) det.scrollIntoView({behavior:'smooth', block:'nearest'});
      }
    } catch(_e) {}
  }
}
function quickFilter(mode){
  activeQuick = mode;
  switchTab('portfolio'); resetPortfolioFilters(false, mode);
  if(mode==='TIER12') document.getElementById('p-tier').value='TIER_12';
  else if(mode==='CORE') document.getElementById('p-dec').value='KEEP_CORE';
  else if(mode==='EXPL') document.getElementById('p-dec').value='KEEP_EXPLORATORY_UNPROVEN';
  else if(mode==='BENCH') document.getElementById('p-dec').value='RECLASSIFY_BENCHMARK_OR_BIOMARKER';
  else if(mode==='DROP') document.getElementById('p-dec').value='DROP';
  renderPortfolio();
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
function filterByFunnel(sub, dec){
  switchTab('portfolio');
  resetPortfolioFilters(false, '');
  if(sub && sub !== 'ALL') document.getElementById('p-origin').value = sub;
  if(dec && dec !== 'ALL') document.getElementById('p-dec').value = dec;
  renderPortfolio();
}
function filterByDropGate(epi){
  switchTab('portfolio');
  resetPortfolioFilters(false, '');
  document.getElementById('p-dec').value = 'DROP';
  activeEpi = epi || 'ALL';
  renderPortfolio();
}
"""

EXPLORER_JS_TABS234 = """
function renderIntervals(){
  const qEl = document.getElementById('iv-search');
  const q = qEl ? qEl.value.trim().toLowerCase() : '';
  const st = document.getElementById('iv-status').value;
  const orig = document.getElementById('iv-origin').value;
  const leadsOnly = document.getElementById('iv-leads').checked;
  const rows = DATA_CIS.filter(c => {
    if(st!=='ALL' && c.st!==st) return false;
    if(orig!=='ALL' && c.o!==orig) return false;
    if(leadsOnly && !c.lead) return false;
    if(q && !(c.pid+' '+c.sc+' '+c.gene+' '+c.iv+' '+c.flags+' '+c.mode).toLowerCase().includes(q)) return false;
    return true;
  });
  document.getElementById('iv-count').textContent = `${rows.length} / ${DATA_CIS.length}`;
  document.getElementById('iv-tbody').innerHTML = rows.length ? rows.map(c => {
    const loPad = Math.max(1, Number(c.lo) - 250), hiPad = Number(c.hi) + 250;
    const atlUrl = `https://deepmind.google.com/science/alphagenome/atlas?q=${c.chr}:${loPad}-${hiPad}&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE`;
    const ucscUrl = `https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position=${c.chr}:${loPad}-${hiPad}`;
    const ensUrl = `https://www.ensembl.org/Homo_sapiens/Location/View?r=${c.chr.replace('chr','')}:${c.lo}-${c.hi}`;
    const gid = GENE_ENSG[c.gene] || '';
    const gnomUrl = gid ? `https://gnomad.broadinstitute.org/gene/${gid}?dataset=gnomad_r4` : '';
    const linkId = (c.pid && c.pid !== 'NONE') ? c.pid : String(c.sc).replace(/-N[0-9]+$/, '');
    return `<tr class="hover:bg-[var(--content)] align-top">
      <td class="py-2 px-2.5 font-mono tabular-nums text-[var(--muted-foreground)]">${c.ord}</td>
      <td class="py-2 px-2 font-mono"><div class="font-semibold"><button type="button" data-open-dossier="${esc(linkId)}" class="text-[var(--link)] hover:underline font-mono font-semibold cursor-pointer">${esc(c.gene)} #${c.rk}</button> <span class="text-[var(--muted-foreground)] font-normal">(${esc(c.sc)})</span></div>${gnomUrl?`<div class="text-xs mt-0.5">${mkExtA(gnomUrl, 'gnomAD v4')}</div>`:''}</td>
      <td class="py-2 px-2 font-mono"><div>${c.lead?'<span class="text-[var(--success)] font-bold">&#9733; Lead</span>':'<span class="text-[var(--muted-foreground)]">Alt</span>'}</div><div class="text-[var(--muted-foreground)] text-xs" title="${esc(c.role)}">${esc(humanizeEnum(c.role))}</div></td>
      <td class="py-2 px-2 font-mono"><div>${mkExtA(ensUrl, esc(c.iv))}</div><div class="text-[var(--muted-foreground)] text-xs">${c.len}bp &middot; GRCh38</div></td>
      <td class="py-2 px-2 text-xs border-r border-[var(--card-border)]" title="${esc(c.mode)}">${esc(humanizeEnum(c.mode))}</td>
      <td class="py-2 px-2 font-mono tabular-nums"><div>${c.tm}&deg;C</div><div class="text-[var(--muted-foreground)] text-xs">&Delta;G=${c.dg} &middot; GC=${c.gc}%</div></td>
      <td class="py-2 px-2 font-mono tabular-nums border-r border-[var(--card-border)]">${c.avi}</td>
      <td class="py-2 px-2 font-mono tabular-nums">${c.sp}</td>
      <td class="py-2 px-2 font-mono tabular-nums">${c.pm}</td>
      <td class="py-2 px-2 font-mono text-xs max-w-[260px] break-words">${linkifyCisFlags(c.flags)}</td>
      <td class="py-2 px-2 border-r border-[var(--card-border)]">${statusBadge(c.st)}</td>
      <td class="py-2 px-2 font-mono whitespace-nowrap"><div>${mkExtA(atlUrl, 'Atlas &nearr;')}</div><div class="mt-0.5">${mkExtA(ucscUrl, 'UCSC &nearr;')}</div></td>
    </tr>`;
  }).join('') : `<tr><td colspan="12" class="py-6 px-4 text-center text-[var(--muted-foreground)]">No GRCh38 intervals match active filters. <button type="button" data-reset-intervals="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></td></tr>`;
}

function resetSubnodeFilters(redraw=true){
  document.getElementById('sn-parent').value = 'ALL';
  document.getElementById('sn-verd').value = 'ALL';
  if(redraw) renderSubnodes();
}

function renderSubnodes(){
  const par = document.getElementById('sn-parent').value;
  const vd = document.getElementById('sn-verd').value;
  const rows = DATA_SUB.filter(s => (par==='ALL'||s.par===par) && (vd==='ALL'||s.vraw.startsWith(vd)));
  document.getElementById('sn-count').textContent = `${rows.length} / ${DATA_SUB.length}`;
  document.getElementById('sn-cards').innerHTML = rows.length ? rows.map(s => {
    const vcol = s.vraw.startsWith('KEEP')?'text-[var(--warning)] border-[var(--warning)]':(s.vraw.startsWith('RECLASSIFY')?'text-[var(--primary)] border-[var(--primary)]':'text-[var(--error)] border-[var(--error)]');
    const gPills = genePortalPills(s.gene);
    return `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2 text-xs">
      <div class="flex items-start justify-between gap-2 flex-wrap border-b border-[var(--card-border)] pb-2">
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-mono font-bold text-sm">${esc(s.id)} &middot; ${esc(s.gene)}</span>
            <button type="button" data-open-dossier="${esc(s.par)}" class="text-[var(--link)] hover:underline font-mono cursor-pointer">(Parent ${esc(s.par)} &rarr;)</button>
            ${gPills?`<span class="font-mono">${gPills}</span>`:''}
          </div>
          <div class="text-[var(--muted-foreground)] mt-0.5">${esc(s.role)}</div>
        </div>
        <div class="flex flex-wrap items-center gap-1.5">${tdlBadge(s.tdl)}${tsaSubBadge(s.tsa)}</div>
      </div>
      <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1">
        <div class="font-mono font-semibold text-[var(--muted-foreground)]">1. Human Genetic Constraint &amp; Essentiality (TSA)</div>
        <div class="leading-relaxed break-words">${escLink(s.gnomad, s.gene)}</div>
      </div>
      <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1">
        <div class="font-mono font-semibold text-[var(--muted-foreground)]">2. 3D Structural Pocket &amp; Tractability</div>
        <div class="leading-relaxed break-words">${escLink(s.drug, s.gene)}</div>
      </div>
      <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1">
        <div class="flex items-center justify-between gap-2 flex-wrap">
          <span class="font-mono font-semibold text-[var(--muted-foreground)]">3. Single-Gene Adjudication Rationale</span>
          <span class="px-1.5 py-0.5 rounded border font-mono font-semibold ${vcol}" title="${esc(s.vraw)}">${esc(s.vlbl)}</span>
        </div>
        <div class="leading-relaxed break-words">${escLink(s.vbody, s.gene)}</div>
      </div>
    </div>`;
  }).join('') : `<div class="md:col-span-2 p-6 rounded-lg bg-[var(--card)] border border-[var(--border)] text-center text-[var(--muted-foreground)]">No single-gene sub-nodes match active filters. <button type="button" data-reset-subnodes="1" class="text-[var(--link)] underline font-mono ml-1 cursor-pointer">Reset filters</button></div>`;
}

function renderNygc(){
  const reg = document.getElementById('nygc-reg').value;
  const m = DATA_NYGC_META[reg];
  const metaBox = document.getElementById('nygc-meta');
  if(metaBox && m){
    metaBox.innerHTML = `<span><strong>N=${m.ntot}</strong> donors &middot; <span class="text-[var(--primary)]">${m.ntdp} ALS-TDP</span> vs. ${m.nctrl} Control &middot; ${m.nsod} ALS-SOD1/FUS (specificity control)</span><span class="text-[var(--muted-foreground)]">&#9679; [MEASURED] RIN+GC OLS</span>`;
  }
  const genes = Object.keys(DATA_NYGC);
  document.getElementById('nygc-tbody').innerHTML = genes.map(g => {
    const d = DATA_NYGC[g][reg];
    const sigNeg = d.b < 0 && d.p < 0.05, sigPos = d.b > 0 && d.p < 0.05;
    const bCol = sigNeg ? 'text-[var(--primary)] font-semibold' : (sigPos ? 'text-[var(--warning)] font-semibold' : 'text-[var(--muted-foreground)]');
    const dotCol = sigNeg ? 'var(--primary)' : (sigPos ? 'var(--warning)' : 'var(--muted-foreground)');
    const ptPct = Math.max(4, Math.min(96, ((Math.max(-0.6, Math.min(0.6, d.b)) + 0.6) / 1.2) * 100));
    const sL = Math.min(50, ptPct), sW = Math.max(1, Math.abs(ptPct - 50));
    const pid = NYGC_GENE_TO_ID[g];
    const gid = GENE_ENSG[g] || '';
    const gPills = gid ? `<div class="text-xs font-normal mt-0.5">${mkExtA('https://gnomad.broadinstitute.org/gene/'+gid+'?dataset=gnomad_r4', 'gnomAD v4')}</div>` : '';
    const gHtml = pid ? `<button type="button" data-open-dossier="${pid}" class="text-[var(--link)] hover:underline font-mono font-semibold cursor-pointer">${esc(g)} (${pid})</button>${gPills}` : `${esc(g)}${gPills}`;
    const ddpcrPill = (d.p < 0.05 && d.sp > 0.25) ? ' <span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] text-xs" title="Non-significant in small n=9 ALS-SOD1/FUS (underpowered for equivalence); junction RT-ddPCR required">ddPCR</span>' : '';
    const tailHtml = d.tail <= 5.0 ? `<span class="px-1.5 py-0.5 rounded border border-[var(--success)] text-[var(--success)] font-bold">${d.tail.toFixed(2)}%</span>` : `${d.tail.toFixed(2)}%`;
    return `<tr class="align-middle">
      <td class="py-1.5 px-1.5 font-mono font-semibold">${gHtml}</td>
      <td class="py-1.5 px-1.5 font-mono tabular-nums">
        <div class="${bCol}">${d.b>=0?'+':''}${d.b.toFixed(3)}</div>
        <div class="relative w-full h-3 rounded bg-[var(--background)] border border-[var(--card-border)] mt-0.5 overflow-hidden">
          <div class="absolute top-0 bottom-0 w-px bg-[var(--foreground)] opacity-40" style="left:50%"></div>
          <div class="absolute" style="left:${sL.toFixed(1)}%;width:${sW.toFixed(1)}%;top:5px;height:2px;background:${dotCol}"></div>
          <div class="absolute rounded-full" style="left:${ptPct.toFixed(1)}%;top:2.5px;width:7px;height:7px;margin-left:-3.5px;background:${dotCol}"></div>
        </div>
      </td>
      <td class="py-1.5 px-1.5 font-mono tabular-nums">${d.p<0.001?d.p.toExponential(1):d.p.toFixed(3)}</td>
      <td class="py-1.5 px-1.5 font-mono tabular-nums whitespace-nowrap">${d.sp.toFixed(2)}${ddpcrPill}</td>
      <td class="py-1.5 px-1.5 font-mono tabular-nums whitespace-nowrap">${d.tb>=0?'+':''}${d.tb.toFixed(2)} <span class="text-[var(--muted-foreground)]">(${d.tp<0.001?d.tp.toExponential(1):d.tp.toFixed(3)})</span></td>
      <td class="py-1.5 px-1.5 font-mono tabular-nums text-right">${tailHtml}</td>
    </tr>`;
  }).join('');
}

function renderDiscoveryFunnelSvg(){
  const box = document.getElementById('funnel-svg-box');
  if(!box) return;
  const maxTot = Math.max(...DATA_FUNNEL.map(d=>d.c+d.e+d.b+d.d));
  const padL = 232, barW = 196, rowH = 30, topY = 6, h = topY + DATA_FUNNEL.length * rowH + 6;
  const segDefs = [
    {k:'c', col:'var(--success)', qf:'CORE', dec:'KEEP_CORE', lbl:'Keep \u00b7 Core (4)'},
    {k:'e', col:'var(--warning)', qf:'EXPL', dec:'KEEP_EXPLORATORY_UNPROVEN', lbl:'Keep \u00b7 Exploratory (24)'},
    {k:'b', col:'var(--primary)', qf:'BENCH', dec:'RECLASSIFY_BENCHMARK_OR_BIOMARKER', lbl:'Benchmark (7)'},
    {k:'d', col:'var(--error)', qf:'DROP', dec:'DROP', lbl:'Drop \u00b7 Falsified (24)'},
  ];
  const legHtml = `<div class="flex flex-wrap gap-2 pb-1.5 text-xs">${segDefs.map(s=>`<button type="button" data-quick-filter="${s.qf}" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] flex items-center gap-1.5 font-mono cursor-pointer"><span class="inline-block w-2.5 h-2.5 rounded-sm" style="background:${s.col}"></span>${esc(s.lbl)}</button>`).join('')}</div>`;
  const rowsSvg = DATA_FUNNEL.map((row, i) => {
    const y = topY + i * rowH, tot = row.c + row.e + row.b + row.d;
    let x = padL, bars = '';
    segDefs.forEach(s => {
      const val = row[s.k];
      if(val > 0){
        const sw = (val / maxTot) * barW;
        const rw = Math.max(sw-1.2, 4.0);
        const ariaLbl = `${esc(row.lbl)}: ${val} ${esc(s.lbl.split(' (')[0])} — Filter Portfolio`;
        bars += `<rect tabindex="0" role="button" aria-label="${ariaLbl}" data-funnel-sub="${esc(row.sub)}" data-funnel-dec="${s.dec}" x="${x.toFixed(1)}" y="${y+4}" width="${rw.toFixed(1)}" height="18" rx="2" fill="${s.col}" class="cursor-pointer"><title>${esc(row.lbl)} \u2192 ${val} ${esc(s.lbl.split(' (')[0])} (click to filter)</title></rect>`;
        if(sw >= 22){
          bars += `<text x="${(x + rw/2).toFixed(1)}" y="${y+17}" text-anchor="middle" font-size="12.5" font-family="monospace" font-weight="700" fill="var(--primary-foreground)" pointer-events="none">${val}</text>`;
        }
        x += sw;
      }
    });
    return `<text tabindex="0" role="button" aria-label="Filter ${esc(row.lbl)}" data-funnel-sub="${esc(row.sub)}" data-funnel-dec="ALL" x="${padL-8}" y="${y+18}" text-anchor="end" font-size="12.6" fill="var(--foreground)" class="cursor-pointer hover:underline">${esc(row.lbl)}</text>${bars}<text x="${(x+6).toFixed(1)}" y="${y+18}" font-size="12.6" font-family="monospace" fill="var(--muted-foreground)">${tot}</text>`;
  }).join('');
  box.innerHTML = `${legHtml}<svg viewBox="0 0 460 ${h}" class="w-full h-auto block select-none" role="img" aria-label="59-candidate discovery-modality and epistemic falsification funnel">${rowsSvg}</svg>`;
  const dropBox = document.getElementById('drop-gates-box');
  if(dropBox){
    dropBox.innerHTML = DATA_DROPS.map(g => `<button type="button" data-drop-epi="${esc(g.epi)}" class="text-left p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] hover:border-[var(--error)] transition space-y-0.5 cursor-pointer">
      <div class="flex items-center justify-between gap-1 font-mono"><span class="font-bold text-sm text-[var(--error)]">${g.n} / 24</span><span class="text-xs text-[var(--link)]">Filter &rarr;</span></div>
      <div class="font-semibold text-xs text-[var(--foreground)]">${esc(g.lbl)}</div>
      <div class="text-xs text-[var(--muted-foreground)] leading-snug">${esc(g.sub)}</div>
    </button>`).join('');
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
  switchTab('intervals');
  resetIntervalFilters(false);
  const qEl = document.getElementById('iv-search');
  if(qEl && pid) qEl.value = pid;
  renderIntervals();
}
function jumpToSubnodes(parId){
  switchTab('subnodes');
  document.getElementById('sn-parent').value = parId || 'ALL';
  document.getElementById('sn-verd').value = 'ALL';
  renderSubnodes();
}

function switchTab(tab){
  activeTab = tab;
  ['portfolio','intervals','subnodes','analytics','dossiers','replication'].forEach(t => {
    const el = document.getElementById('view-'+t);
    if(el) el.classList.toggle('hidden', t!==tab);
  });
  document.querySelectorAll('.tab-btn').forEach(btn => {
    const on = btn.dataset.tab === tab;
    btn.setAttribute('aria-selected', on ? 'true' : 'false');
    btn.className = 'tab-btn px-2.5 py-1.5 rounded border font-medium text-xs cursor-pointer ' + (on ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)]' : 'bg-[var(--background)] text-[var(--foreground)] border-[var(--border)]');
  });
  if(tab !== 'dossiers' && tab !== 'replication'){
    try {
      if((location.protocol==='http:' || location.protocol==='https:') && /^#(?:dossier|monograph|replication)/.test(location.hash||'')){
        history.replaceState(null, '', location.pathname + location.search);
      }
    } catch(_e) {}
  }
  if(tab==='portfolio'){
    renderPortfolio();
    try {
      const tb = document.getElementById('p-tbody');
      const actRow = tb && tb.querySelector ? tb.querySelector('[data-select-cand="'+selectedId+'"]') : null;
      if(actRow && actRow.scrollIntoView) actRow.scrollIntoView({block:'nearest'});
    } catch(_e) {}
  }
  if(tab==='dossiers') renderDossierMain();
  if(tab==='replication' && typeof renderReplicationWorkbench === 'function') renderReplicationWorkbench();
  syncKpiHighlight();
  try { if(typeof window !== 'undefined' && window.scrollTo) window.scrollTo(0, 0); } catch(_e) {}
}

function syncFromHash(){
  const h = location.hash || '';
  const m = /^#(?:dossier|monograph)[/]([A-Za-z0-9-]+)$/.exec(h);
  const cid = m ? m[1].replace(/-N[0-9]+$/, '') : '';
  if(cid && DATA_PORT.some(x=>x.id===cid)){ dossierId = cid; selectedId = cid; switchTab('dossiers'); return true; }
  const mr = /^#replication(?:[/](?:cand[/]([A-Za-z0-9-]+)|([A-Za-z0-9_-]+)))?$/.exec(h);
  if(mr && typeof openReplicationTarget === 'function'){
    if(mr[1]){ openReplicationTarget('cand', mr[1], mr[1]); }
    else if(mr[2]){ openReplicationTarget(mr[2].startsWith('DS') ? 'ds' : 'run', mr[2], ''); }
    else { switchTab('replication'); }
    return true;
  }
  return false;
}

document.querySelectorAll('.tab-btn').forEach(b => b.addEventListener('click', () => switchTab(b.dataset.tab)));
document.addEventListener('click', e => {
  const raw = e.target;
  const tgt = raw && raw.closest ? raw : (raw && raw.parentElement && raw.parentElement.closest ? raw.parentElement : null);
  if(!tgt) return;
  const ccBtn = tgt.closest('[data-copy-cmd]');
  if(ccBtn){ e.preventDefault(); const v = ccBtn.getAttribute('data-copy-cmd')||''; if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(v); } const orig = (ccBtn.dataset&&(ccBtn.dataset.orig||(ccBtn.dataset.orig=ccBtn.textContent)))||ccBtn.textContent; ccBtn.textContent='Copied \u2713'; setTimeout(()=>{ ccBtn.textContent = orig; }, 1400); return; }
  const csBtn = tgt.closest('[data-copy-sha]');
  if(csBtn){ e.preventDefault(); const v = csBtn.getAttribute('data-copy-sha')||''; if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(v); } const orig = (csBtn.dataset&&(csBtn.dataset.orig||(csBtn.dataset.orig=csBtn.textContent)))||csBtn.textContent; csBtn.textContent='Copied \u2713'; setTimeout(()=>{ csBtn.textContent = orig; }, 1400); return; }
  const rrBtn = tgt.closest('[data-open-rep-run]');
  if(rrBtn){ e.preventDefault(); e.stopPropagation(); openReplicationTarget('run', rrBtn.getAttribute('data-open-rep-run'), activeTab==='dossiers'?dossierId:''); return; }
  const rdBtn = tgt.closest('[data-open-rep-ds]');
  if(rdBtn){ e.preventDefault(); e.stopPropagation(); openReplicationTarget('ds', rdBtn.getAttribute('data-open-rep-ds'), activeTab==='dossiers'?dossierId:''); return; }
  const rcBtn = tgt.closest('[data-jump-rep-cand]');
  if(rcBtn){ e.preventDefault(); e.stopPropagation(); openReplicationTarget('cand', rcBtn.getAttribute('data-jump-rep-cand'), rcBtn.getAttribute('data-jump-rep-cand')); return; }
  const rmBtn = tgt.closest('[data-rep-mode]');
  if(rmBtn){ e.preventDefault(); setRepMode(rmBtn.getAttribute('data-rep-mode')); return; }
  const rsRow = tgt.closest('[data-rep-select]');
  if(rsRow){ selectedRepKey = rsRow.getAttribute('data-rep-select'); renderReplicationWorkbench(); return; }
  const dgBtn = tgt.closest('[data-rep-dag]');
  if(dgBtn){ e.preventDefault(); const [m,f] = dgBtn.getAttribute('data-rep-dag').split('|'); setRepMode(m); document.getElementById('rep-filter').value = f; renderReplicationWorkbench(); return; }
  const rrpBtn = tgt.closest('[data-reset-rep]');
  if(rrpBtn){ e.preventDefault(); repReturnDossier=''; document.getElementById('rep-search').value=''; setRepMode('runs'); return; }
  const dlBtn = tgt.closest('[data-dl-reg]');
  if(dlBtn){ e.preventDefault(); exportRegistryBlob(dlBtn.getAttribute('data-dl-reg')); return; }
  const wBtn = tgt.closest('[data-open-dossier]');
  if(wBtn){ e.preventDefault(); e.stopPropagation(); openDossier(wBtn.getAttribute('data-open-dossier')); return; }
  const wsBtn = tgt.closest('[data-dossier-slice]');
  if(wsBtn){ e.preventDefault(); setDossierSlice(wsBtn.getAttribute('data-dossier-slice')); return; }
  const plBtn = tgt.closest('[data-p-lens]');
  if(plBtn){ e.preventDefault(); activeQuick = ''; activeLens = plBtn.getAttribute('data-p-lens') || 'ALL'; renderPortfolio(); return; }
  const trBtn = tgt.closest('[data-toggle-d-rail]');
  if(trBtn){ e.preventDefault(); toggleDossierRail(); return; }
  const jiBtn = tgt.closest('[data-jump-intervals]');
  if(jiBtn){ e.preventDefault(); e.stopPropagation(); jumpToIntervals(jiBtn.getAttribute('data-jump-intervals')); return; }
  const jsBtn = tgt.closest('[data-jump-subnodes]');
  if(jsBtn){ e.preventDefault(); e.stopPropagation(); jumpToSubnodes(jsBtn.getAttribute('data-jump-subnodes')); return; }
  const riBtn = tgt.closest('[data-reset-intervals]');
  if(riBtn){ e.preventDefault(); resetIntervalFilters(true); return; }
  const rsBtn = tgt.closest('[data-reset-subnodes]');
  if(rsBtn){ e.preventDefault(); resetSubnodeFilters(true); return; }
  const fBtn = tgt.closest('[data-funnel-sub]');
  if(fBtn){ e.preventDefault(); filterByFunnel(fBtn.getAttribute('data-funnel-sub'), fBtn.getAttribute('data-funnel-dec')); return; }
  const dBtn = tgt.closest('[data-drop-epi]');
  if(dBtn){ e.preventDefault(); filterByDropGate(dBtn.getAttribute('data-drop-epi')); return; }
  const tBtn = tgt.closest('[data-switch-tab]');
  if(tBtn){ e.preventDefault(); switchTab(tBtn.getAttribute('data-switch-tab')); return; }
  const qBtn = tgt.closest('[data-quick-filter]');
  if(qBtn){ e.preventDefault(); quickFilter(qBtn.getAttribute('data-quick-filter')); return; }
  const rBtn = tgt.closest('[data-reset-filters]');
  if(rBtn){ e.preventDefault(); resetPortfolioFilters(true, 'ALL'); return; }
  const cRow = tgt.closest('[data-select-cand]');
  if(cRow){ selectCand(cRow.getAttribute('data-select-cand'), true); }
});
document.addEventListener('keydown', e => {
  const act = document.activeElement;
  const tag = act && act.tagName ? String(act.tagName).toUpperCase() : '';
  if(act && act.dataset && act.dataset.tab && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')){
    const tabs = ['portfolio','intervals','subnodes','analytics','dossiers','replication'];
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
    const idx = DATA_PORT.findIndex(x => x.id === dossierId);
    if(idx >= 0){
      e.preventDefault();
      const step = e.key === '[' ? -1 : 1;
      openDossier(DATA_PORT[(idx + step + DATA_PORT.length) % DATA_PORT.length].id);
      return;
    }
  }
  if(e.key !== 'Enter' && e.key !== ' ') return;
  const raw = e.target;
  const dgBtn = raw && raw.closest ? raw.closest('[data-rep-dag]') : null;
  if(dgBtn && raw === dgBtn){ e.preventDefault(); const [m,f] = dgBtn.getAttribute('data-rep-dag').split('|'); setRepMode(m); document.getElementById('rep-filter').value = f; renderReplicationWorkbench(); return; }
  const rsRow = raw && raw.closest ? raw.closest('tr[data-rep-select]') : null;
  if(rsRow && raw === rsRow){ e.preventDefault(); selectedRepKey = rsRow.getAttribute('data-rep-select'); renderReplicationWorkbench(); return; }
  const fBtn = raw && raw.closest ? raw.closest('[data-funnel-sub]') : null;
  if(fBtn && raw === fBtn){ e.preventDefault(); filterByFunnel(fBtn.getAttribute('data-funnel-sub'), fBtn.getAttribute('data-funnel-dec')); return; }
  const cRow = raw && raw.closest ? raw.closest('tr[data-select-cand]') : null;
  if(cRow && raw === cRow){ e.preventDefault(); selectCand(cRow.getAttribute('data-select-cand'), true); }
});
['p-search','p-origin','p-dec','p-tier','p-sort'].forEach(id => {
  const el = document.getElementById(id);
  const fn = () => { activeQuick = ''; if(id!=='p-sort' && id!=='p-search') activeEpi = 'ALL'; renderPortfolio(); };
  el.addEventListener('input', fn);
  el.addEventListener('change', fn);
});
['iv-status','iv-origin','iv-leads'].forEach(id => document.getElementById(id).addEventListener('change', renderIntervals));
document.getElementById('iv-search').addEventListener('input', renderIntervals);
['sn-parent','sn-verd'].forEach(id => document.getElementById(id).addEventListener('change', renderSubnodes));
document.getElementById('nygc-reg').addEventListener('change', renderNygc);
document.getElementById('d-search').addEventListener('input', renderDossierSidebar);
const dLensEl = document.getElementById('d-lens');
if(dLensEl) dLensEl.addEventListener('change', e => setDossierLens(e.target.value));
document.getElementById('d-mobile-select').addEventListener('change', e => openDossier(e.target.value));
const repS = document.getElementById('rep-search');
if(repS) repS.addEventListener('input', renderReplicationWorkbench);
const repF = document.getElementById('rep-filter');
if(repF) repF.addEventListener('change', renderReplicationWorkbench);
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
window.addEventListener('hashchange', syncFromHash);
renderContrastsTable(); renderPortfolio(); renderIntervals(); renderSubnodes(); renderNygc(); renderDiscoveryFunnelSvg();
if(typeof renderRepDag === 'function'){ renderRepDag(); renderRepOverlap(); setRepMode('runs'); initSandboxes(); }
if(!syncFromHash()) switchTab('portfolio');
</script>
</body>
</html>
"""
