"""Client-side Dossier Standard v3 core: deterministic CURIE linkifier, 3-tier Causal Grid, Cleveland Lollipop/CI Matrix, & GRCh38 Locus SVG."""
from __future__ import annotations

DOSSIER_JS_SVG_CORE = """
const GENE_ENSG = {
  S06:'ENSG00000004139', C006:'ENSG00000075043', S07:'ENSG00000134460', C001:'ENSG00000130477',
  C002:'ENSG00000104435', C007:'ENSG00000115602', 'DN-01':'ENSG00000168397', 'DN-02':'ENSG00000160145',
  'DN-03':'ENSG00000196090', 'DN-04':'ENSG00000161082', 'DN-05':'ENSG00000106772', 'DN-06':'ENSG00000067057',
  'DN-07':'ENSG00000171853', 'DN-08':'ENSG00000126767', 'DN-09':'ENSG00000170579', 'DN-10':'ENSG00000130226',
  'DN-11':'ENSG00000175497', 'DN-12':'ENSG00000172757', 'DN-13':'ENSG00000069535', 'DN-14':'ENSG00000197405',
  C016:'ENSG00000118564', C019:'ENSG00000162434', C020:'ENSG00000115020', 'BA9-01':'ENSG00000135439', 'BA9-02':'ENSG00000213983',
  'BA9-03':'ENSG00000174672', 'BA9-04':'ENSG00000135924', 'BA9-05':'ENSG00000167702', 'BA9-06':'ENSG00000197530',
  'BA9-07':'ENSG00000196535', 'BA9-08':'ENSG00000101298', 'BA9-09':'ENSG00000204946', 'BA9-10':'ENSG00000042493',
  AGAP2:'ENSG00000135439', AP1G2:'ENSG00000213983', ARHGEF11:'ENSG00000132694', ATG4B:'ENSG00000168397',
  BRSK2:'ENSG00000174672', C1QA:'ENSG00000173372', C1QB:'ENSG00000173369', C1QC:'ENSG00000159189',
  C3:'ENSG00000125730', C4B:'ENSG00000224389', C5AR1:'ENSG00000197405', CAPG:'ENSG00000042493',
  CELF5:'ENSG00000161082', CFL1:'ENSG00000172757', CHI3L1:'ENSG00000133048', CHI3L2:'ENSG00000064886',
  CHIT1:'ENSG00000133063', CHMP2B:'ENSG00000083937', CHMP7:'ENSG00000147457', CLK3:'ENSG00000179335',
  CLOCK:'ENSG00000134852', DAB1:'ENSG00000173406', DDB1:'ENSG00000167986', DDX1:'ENSG00000079785',
  DENR:'ENSG00000139726', DLGAP1:'ENSG00000170579', DNAJB2:'ENSG00000135924', DPP10:'ENSG00000175497',
  DPP6:'ENSG00000130226', ELK1:'ENSG00000126767', ELOC:'ENSG00000154582', ERBB4:'ENSG00000178568',
  ETV3:'ENSG00000117036', FBXL5:'ENSG00000118564', G2E3:'ENSG00000092140', GDI2:'ENSG00000057608',
  GOSR1:'ENSG00000108587', GPNMB:'ENSG00000136235', GPR156:'ENSG00000175697', IL1RL1:'ENSG00000115602',
  IL2RA:'ENSG00000134460', IQGAP1:'ENSG00000140575', IREB2:'ENSG00000136381', JAK1:'ENSG00000162434',
  JAK2:'ENSG00000096968', KALRN:'ENSG00000160145', KCND3:'ENSG00000171385', KCNQ2:'ENSG00000075043',
  KCNQ3:'ENSG00000184156', KIFC2:'ENSG00000167702', MAOB:'ENSG00000069535', MIB2:'ENSG00000197530',
  MYO18A:'ENSG00000196535', MYOCD:'ENSG00000141052', NSF:'ENSG00000073969', PAFAH1B1:'ENSG00000007168',
  PFKP:'ENSG00000067057', PIKFYVE:'ENSG00000115020', PPA2:'ENSG00000138777', PRUNE2:'ENSG00000106772',
  PTCH1:'ENSG00000185920', PTPRT:'ENSG00000196090', SARM1:'ENSG00000004139', SCFD1:'ENSG00000092108',
  SEC22B:'ENSG00000265808', SLC12A5:'ENSG00000124140', SNPH:'ENSG00000101298', SRPK2:'ENSG00000135250',
  STMN2:'ENSG00000104435', STX5:'ENSG00000162236', TENM2:'ENSG00000145934', TRAPPC12:'ENSG00000171853',
  UNC13A:'ENSG00000130477', YKT6:'ENSG00000106636', ZNF783:'ENSG00000204946'
};
const CHEMBL_COMPOUNDS = new Set([
  'CHEMBL1200798','CHEMBL1201438','CHEMBL1214124','CHEMBL124363','CHEMBL1456','CHEMBL161',
  'CHEMBL2105759','CHEMBL2365743','CHEMBL289228','CHEMBL298734','CHEMBL35','CHEMBL3545058',
  'CHEMBL3752910','CHEMBL41355','CHEMBL4297372','CHEMBL4297672','CHEMBL5653589','CHEMBL589',
  'CHEMBL621','CHEMBL744','CHEMBL778','CHEMBL807','CHEMBL83','CHEMBL866'
]);
const ACC_TOKEN_RE = /(?<![A-Za-z0-9])(?:PMID:(\\d{5,9})|(PMC\\d{6,9})|(?:DOI:\\s*)?(10\\.\\d{4,9}\\/[^\\s,;\\]\\u00b7&<>"]+)|(NCT\\d{8})|ISRCTN(\\d{8})|PDB\\s+([0-9][A-Za-z0-9]{3})|(7DJT|9TZY|7ANW|7NAL|7CR2|4KC3|2Z0D|6VN8|1XFD|7K2V|3KYQ|6J74|3EGD|3V5Z|6VCD|4M7N)|(CHEMBL\\d+)|CID:(\\d+)|(ENS[GT]\\d{11})(?:\\.\\d+)?|HGNC:(\\d+)|MGI:(\\d+)|OMIM\\s+(\\d{6})|AF-([A-Z0-9]{6,10})-F\\d+|(O15498|O43526|O60229|O60674|O75396|O95249|P23458|P42779|P46459|P50395|P60568|Q01638|Q13190|Q6SZW1|Q7L622|Q8N6W0|Q8WVM8|Q93045|Q9UKA1|Q9UPW8|Q9Y4P1)|(gnomAD\\s+(?:v4(?:\\.1)?|r4))|(GSE\\d{4,8})|(PXD\\d{5,8})|(PRJNA\\d{5,9})|(syn\\d{6,10})|(rs\\d{3,12}))(?![A-Za-z0-9])/g;

function mkExtA(url, lbl){
  return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid">${lbl}</a>`;
}
function linkifyAcc(escapedStr, geneCtx){
  if(!escapedStr) return '';
  return String(escapedStr).replace(ACC_TOKEN_RE, (full, pmid, pmc, doi, nct, isrctn, pdbPref, pdbBare, chembl, cid, ens, hgnc, mgi, omim, af, uniprot, gnomad, gse, pxd, prjna, syn, rsid) => {
    if(pmid) return mkExtA('https://pubmed.ncbi.nlm.nih.gov/' + pmid + '/', full);
    if(pmc) return mkExtA('https://pmc.ncbi.nlm.nih.gov/articles/' + pmc + '/', full);
    if(doi){
      let clean = doi, trail = '';
      while(clean.length > 4){
        const ch = clean[clean.length - 1];
        const openN = (clean.match(/\\(/g)||[]).length, closeN = (clean.match(/\\)/g)||[]).length;
        if(ch === '.' || ch === ':' || (ch === ')' && closeN > openN)){
          trail = ch + trail;
          clean = clean.slice(0, -1);
        } else break;
      }
      const vis = full.slice(0, full.length - trail.length);
      return mkExtA('https://doi.org/' + clean, vis) + trail;
    }
    if(nct) return mkExtA('https://clinicaltrials.gov/study/' + nct, full);
    if(isrctn) return mkExtA('https://www.isrctn.com/ISRCTN' + isrctn, full);
    if(pdbPref || pdbBare) return mkExtA('https://www.rcsb.org/structure/' + (pdbPref || pdbBare), full);
    if(chembl){
      if(chembl === 'CHEMBL1741221') return mkExtA('https://www.ebi.ac.uk/chembl/explore/target/' + chembl, full);
      if(CHEMBL_COMPOUNDS.has(chembl)) return mkExtA('https://www.ebi.ac.uk/chembl/explore/compound/' + chembl, full);
      return mkExtA('https://www.ebi.ac.uk/chembl/g/#search_results/all/query=' + chembl, full);
    }
    if(cid) return mkExtA('https://pubchem.ncbi.nlm.nih.gov/compound/' + cid, full);
    if(ens){
      const kind = ens.startsWith('ENST') ? 'Transcript/Summary?t=' : 'Gene/Summary?g=';
      return mkExtA('https://www.ensembl.org/Homo_sapiens/' + kind + ens, full);
    }
    if(hgnc) return mkExtA('https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:' + hgnc, full);
    if(mgi) return mkExtA('https://www.informatics.jax.org/marker/MGI:' + mgi, full);
    if(omim) return mkExtA('https://www.omim.org/entry/' + omim, full);
    if(af) return mkExtA('https://alphafold.ebi.ac.uk/entry/' + af, full);
    if(uniprot) return mkExtA('https://www.uniprot.org/uniprotkb/' + uniprot + '/entry', full);
    if(gnomad){
      const gid = GENE_ENSG[geneCtx] || '';
      const gUrl = gid ? ('https://gnomad.broadinstitute.org/gene/' + gid + '?dataset=gnomad_r4') : 'https://gnomad.broadinstitute.org/';
      return mkExtA(gUrl, full);
    }
    if(gse) return mkExtA('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + gse, full);
    if(pxd) return mkExtA('https://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=' + pxd, full);
    if(prjna) return mkExtA('https://www.ncbi.nlm.nih.gov/bioproject/' + prjna, full);
    if(syn) return mkExtA('https://www.synapse.org/Synapse:' + syn, full);
    if(rsid) return mkExtA('https://www.ncbi.nlm.nih.gov/snp/' + rsid, full);
    return full;
  });
}
function escLink(rawStr, geneCtx){ return linkifyAcc(esc(rawStr), geneCtx); }
function linkifyCisFlags(rawFlags){
  if(!rawFlags || rawFlags === 'NONE') return '<span class="text-[var(--muted-foreground)]">None</span>';
  return esc(rawFlags).replace(/\\b([A-Z0-9]{2,10})\\(/g, (m, g) => {
    const gid = GENE_ENSG[g];
    return gid ? (mkExtA('https://gnomad.broadinstitute.org/gene/' + gid + '?dataset=gnomad_r4', g) + '(') : m;
  });
}
function genePortalPills(symOrId){
  const gid = GENE_ENSG[symOrId];
  if(!gid) return '';
  return `${mkExtA('https://www.ensembl.org/Homo_sapiens/Gene/Summary?g='+gid, 'Ensembl')} &middot; ${mkExtA('https://gnomad.broadinstitute.org/gene/'+gid+'?dataset=gnomad_r4', 'gnomAD v4')}`;
}

function renderCausalGrid(c, geneCtx){
  const cards = c.nodes.map((nd, i) => {
    const isLast = i === 3;
    const bdr = isLast ? 'border-[var(--success)] border-2' : 'border-[var(--border)]';
    const badge = isLast ? 'bg-[var(--success)] text-[var(--primary-foreground)]' : 'bg-[var(--content)] text-[var(--foreground)] border border-[var(--border)]';
    const stepTag = isLast ? '4 &middot; INTERVENTION' : `STEP ${i+1} &rarr;`;
    return `<div class="p-3 rounded-lg bg-[var(--background)] border ${bdr} flex flex-col justify-between space-y-1.5 text-xs">
      <div class="space-y-1">
        <div class="flex items-center justify-between gap-1.5">
          <span class="px-1.5 py-0.5 rounded font-mono font-bold text-xs ${badge}">${stepTag}</span>
        </div>
        <div class="font-semibold text-[var(--foreground)] leading-snug break-words">${esc(nd[0])}</div>
      </div>
      <div class="text-[var(--muted-foreground)] leading-relaxed break-words">${escLink(nd[1], geneCtx)}</div>
    </div>`;
  }).join('');
  const kind = c.callout_kind || 'CAUTION';
  const boxCls = kind === 'HAZARD' ? 'border-dashed border-[var(--error)]' : (kind === 'RATIONALE' ? 'border-[var(--primary)]' : 'border-dashed border-[var(--warning)]');
  const hdrCls = kind === 'HAZARD' ? 'text-[var(--error)]' : (kind === 'RATIONALE' ? 'text-[var(--primary)]' : 'text-[var(--warning)]');
  const icon = kind === 'HAZARD' ? '&#9888;' : (kind === 'RATIONALE' ? '&#9670;' : '&#9651;');
  return `<div class="space-y-2.5">
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-2.5">${cards}</div>
    <div class="p-3 rounded-lg bg-[var(--background)] border ${boxCls} space-y-1 text-xs">
      <div class="font-mono font-bold ${hdrCls}">${icon} ${esc(c.trap_title)}</div>
      <p class="text-[var(--foreground)] leading-relaxed break-words">${escLink(c.trap_desc, geneCtx)}</p>
    </div>
  </div>`;
}

function renderEvidenceMatrix(ev, geneCtx){
  const meta = {
    log2fc: {hdr:'Effect Size: log2FC / \u0394log2CPM (-3.0 to +4.0, null = 0.0)', ticks:'<span>-3.0</span><span>0.0</span><span>+4.0</span>'},
    dpsi:   {hdr:'Cryptic / Isoform Junction Shift (\u0394PSI: 0.00 to 1.00)', ticks:'<span>0.00</span><span>0.50</span><span>1.00</span>'},
    hr:     {hdr:'Survival Hazard Ratio (Log Scale: 0.25 to 2.00, null HR = 1.00)', ticks:'<span>0.25 (Benefit)</span><span>HR=1.0</span><span>2.00</span>'},
    auc:    {hdr:'Biomarker / Pathway Discrimination (ROC-AUC: 0.50 null to 1.00)', ticks:'<span>0.50 (Null)</span><span>0.75</span><span>1.00</span>'},
  };
  const mapVal = (k, v) => {
    const num = Number(v);
    if(k === 'log2fc') return Math.max(1, Math.min(99, ((Math.max(-3.0, Math.min(4.0, num)) + 3.0) / 7.0) * 100));
    if(k === 'dpsi') return Math.max(1, Math.min(99, Math.max(0.0, Math.min(1.0, num)) * 100));
    if(k === 'hr'){
      const cHr = Math.max(0.25, Math.min(2.0, num));
      return Math.max(1, Math.min(99, ((Math.log(cHr) - Math.log(0.25)) / (Math.log(2.0) - Math.log(0.25))) * 100));
    }
    return Math.max(1, Math.min(99, ((Math.max(0.5, Math.min(1.0, num)) - 0.5) / 0.5) * 100));
  };
  const toneVar = t => {
    if(t === 'clinical_benefit') return 'var(--success)';
    if(t === 'clinical_harm') return 'var(--error)';
    if(t === 'disease_gain') return 'var(--warning)';
    if(t === 'null_or_diluted') return 'var(--muted-foreground)';
    return 'var(--primary)';
  };
  const order = ['log2fc','dpsi','hr','auc'];
  let groupsHtml = '';
  order.forEach(k => {
    const sub = (ev.tracks || []).filter(r => r.kind === k);
    if(!sub.length) return;
    const zeroPct = k === 'log2fc' ? (3.0 / 7.0) * 100 : (k === 'hr' ? mapVal('hr', 1.0) : 0.0);
    const rowsHtml = sub.map(r => {
      const isPrior = r.tag === 'MODEL_PRIOR';
      const col = toneVar(r.tone || 'disease_loss');
      const ptPct = mapVal(k, r.val);
      const hasCi = Array.isArray(r.ci) && r.ci.length === 2;
      let spanHtml = '';
      if(hasCi){
        const ciL = mapVal(k, r.ci[0]), ciR = mapVal(k, r.ci[1]);
        const lo = Math.min(ciL, ciR), w = Math.max(0.8, Math.abs(ciR - ciL));
        spanHtml = `<div class="absolute" style="left:${lo.toFixed(1)}%;width:${w.toFixed(1)}%;top:7px;height:2px;background:${col}"></div>
          <div class="absolute" style="left:${ciL.toFixed(1)}%;top:4px;height:8px;width:1.5px;background:${col}"></div>
          <div class="absolute" style="left:${ciR.toFixed(1)}%;top:4px;height:8px;width:1.5px;background:${col}"></div>`;
      } else {
        const sL = Math.min(zeroPct, ptPct), sW = Math.max(0.8, Math.abs(ptPct - zeroPct));
        spanHtml = `<div class="absolute" style="left:${sL.toFixed(1)}%;width:${sW.toFixed(1)}%;top:7px;height:2px;background:${col};opacity:0.75"></div>`;
      }
      const glyph = isPrior
        ? `<div class="absolute rotate-45 bg-[var(--background)]" style="left:${ptPct.toFixed(1)}%;top:3.5px;width:9px;height:9px;margin-left:-4.5px;border:2px solid ${col}"></div>`
        : `<div class="absolute rounded-full" style="left:${ptPct.toFixed(1)}%;top:3.5px;width:9px;height:9px;margin-left:-4.5px;background:${col}"></div>`;
      const survTag = r.tone === 'compensatory_or_survivor' ? '<span class="px-1 rounded border border-[var(--primary)] text-[var(--primary)] font-mono text-xs">[Survivor]</span> ' : '';
      const pTag = isPrior ? '<span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] font-mono text-xs">[MODEL_PRIOR]</span> ' : '';
      return `<div class="py-1.5 border-b border-[var(--card-border)] last:border-b-0 space-y-1 text-xs">
        <div class="flex items-baseline justify-between gap-2">
          <span class="font-medium text-[var(--foreground)] break-words">${escLink(r.lbl, geneCtx)}</span>
          <span class="font-mono whitespace-nowrap shrink-0">${survTag}${pTag}<strong>${esc(r.stat)}</strong> <span class="text-[var(--muted-foreground)]">(${esc(r.p)})</span></span>
        </div>
        <div class="relative w-full h-4 rounded bg-[var(--background)] border border-[var(--card-border)] overflow-hidden">
          <div class="absolute left-0 right-0 bg-[var(--card-border)]" style="top:7.5px;height:1px"></div>
          ${zeroPct>0.5?`<div class="absolute top-0 bottom-0 w-px bg-[var(--foreground)] opacity-45" style="left:${zeroPct.toFixed(1)}%"></div>`:''}
          ${spanHtml}${glyph}
        </div>
      </div>`;
    }).join('');
    groupsHtml += `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1">
      <div class="font-mono text-xs font-semibold text-[var(--muted-foreground)]">${meta[k].hdr}</div>
      <div class="flex justify-between font-mono text-xs text-[var(--muted-foreground)] opacity-80">${meta[k].ticks}</div>
      <div>${rowsHtml}</div>
    </div>`;
  });
  const callouts = (ev.callouts || []).map(c => {
    const isP = c.tag === 'MODEL_PRIOR';
    const bdr = isP ? 'border-dashed border-[var(--warning)]' : 'border-[var(--card-border)]';
    return `<div class="p-2 rounded bg-[var(--background)] border ${bdr} flex flex-col justify-between gap-0.5 text-xs">
      <div class="text-[var(--muted-foreground)] leading-snug break-words">${escLink(c.lbl, geneCtx)}</div>
      <div class="flex items-center justify-between gap-1.5 font-mono pt-0.5">
        <span class="font-bold text-[var(--foreground)]">${esc(c.stat)}</span>
        <span class="${isP?'text-[var(--warning)]':'text-[var(--muted-foreground)]'}">${isP?'[PRIOR] ':''}${esc(c.p)}</span>
      </div>
    </div>`;
  }).join('');
  const leg = `<div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs font-mono text-[var(--muted-foreground)] pb-0.5">
    <span>&#9679; [MEASURED]</span><span>&#9671; [MODEL_PRIOR]</span><span>&#9500;&#9472;&#9679;&#9472;&#9508; 95% CI (staged)</span><span>&#9472;&#9472;&#9679; Point stem (p/FDR)</span>
  </div>`;
  return `<div class="space-y-2.5">${leg}${groupsHtml}${callouts?`<div class="space-y-1"><div class="font-mono text-xs font-semibold text-[var(--muted-foreground)]">Structural, Correlation &amp; Power Anchors</div><div class="grid grid-cols-1 sm:grid-cols-2 gap-2">${callouts}</div></div>`:''}</div>`;
}

function renderLocusSsoSvg(candId, sig){
  const cis = DATA_CIS.filter(c => c.sc === candId || (candId==='DN-01'&&c.gene==='ATG4B') || (candId==='DN-04'&&c.gene==='CELF5') || (candId==='C006'&&c.gene==='KCNQ2') || (candId==='C001'&&c.gene==='UNC13A') || (candId==='C002'&&c.gene==='STMN2')).sort((a,b)=>(b.lead-a.lead)||(a.rk-b.rk));
  const L = 14, R = 446, W = R - L;
  const mapTop = p => L + ((p - sig.win_lo) / Math.max(1, sig.win_hi - sig.win_lo)) * W;
  const mapBot = p => L + ((p - sig.zoom_lo) / Math.max(1, sig.zoom_hi - sig.zoom_lo)) * W;
  const dirTxt = sig.strand === '+' ? "5' -> 3' (+ strand)" : "3' <- 5' (- strand)";
  let exSvg = '', snpSvg = '', zoomExSvg = '', ssoSvg = '';
  sig.exons.forEach((ex, idx) => {
    const x1 = Math.max(L, mapTop(ex.lo)), x2 = Math.min(R, mapTop(ex.hi)), xm = (x1 + x2) / 2;
    const col = ex.kind==='ce' ? 'var(--error)' : (ex.kind==='skip' ? 'var(--warning)' : 'var(--primary)');
    const dash = ex.kind==='ce' ? 'stroke-dasharray="3,2"' : '';
    const ly = idx === 1 ? 33 : 49;
    const anchor = xm < 120 ? 'start' : (xm > 320 ? 'end' : 'middle');
    const tx = anchor==='start' ? Math.max(L, x1) : (anchor==='end' ? Math.min(R, x2) : xm);
    exSvg += `<rect x="${x1.toFixed(1)}" y="55" width="${Math.max(7, x2-x1).toFixed(1)}" height="16" rx="3" fill="${col}" stroke="var(--foreground)" stroke-opacity="0.25" ${dash}/>
      ${idx===1?`<line x1="${xm.toFixed(1)}" y1="36" x2="${xm.toFixed(1)}" y2="55" stroke="${col}" stroke-width="1.1" stroke-dasharray="2,2"/>`:''}
      <text x="${tx.toFixed(1)}" y="${ly}" text-anchor="${anchor}" font-size="12.6" font-weight="600" fill="${idx===1?col:'var(--foreground)'}">${esc(ex.lbl)}</text>`;
    if(ex.hi >= sig.zoom_lo && ex.lo <= sig.zoom_hi){
      const zx1 = Math.max(L, mapBot(Math.max(ex.lo, sig.zoom_lo))), zx2 = Math.min(R, mapBot(Math.min(ex.hi, sig.zoom_hi)));
      zoomExSvg += `<rect x="${zx1.toFixed(1)}" y="136" width="${Math.max(5, zx2-zx1).toFixed(1)}" height="12" rx="2" fill="${col}" fill-opacity="0.35" stroke="${col}" stroke-width="1.1"/>`;
    }
  });
  const snpItems = (sig.snps||[]).map(sn => ({...sn, sx: Math.max(L+14, Math.min(R-14, mapTop(sn.pos)))})).sort((a,b)=>a.sx-b.sx);
  const closePair = snpItems.length === 2 && Math.abs(snpItems[1].sx - snpItems[0].sx) < 95;
  snpItems.forEach((sn, idx) => {
    const sx = sn.sx;
    const sAnchor = closePair ? (idx === 0 ? 'end' : 'start') : (sx < 115 ? 'start' : (sx > 345 ? 'end' : 'middle'));
    const tx = closePair ? (idx === 0 ? sx - 5 : sx + 5) : sx;
    const ty = closePair ? 100 : (99 + (idx%2)*14);
    snpSvg += `<line x1="${sx.toFixed(1)}" y1="71" x2="${sx.toFixed(1)}" y2="83" stroke="var(--warning)" stroke-width="1.5"/>
      <circle cx="${sx.toFixed(1)}" cy="85" r="3.2" fill="var(--warning)"/>
      <text x="${tx.toFixed(1)}" y="${ty}" text-anchor="${sAnchor}" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">${esc(sn.lbl)}</text>`;
  });
  (sig.spans||[]).forEach(sp => {
    const sx1 = Math.max(L+6, mapTop(sp.lo)), sx2 = Math.min(R-6, mapTop(sp.hi)), sm = (sx1 + sx2)/2;
    const sAnchor = sm < 115 ? 'start' : (sm > 345 ? 'end' : 'middle');
    snpSvg += `<line x1="${sx1.toFixed(1)}" y1="81" x2="${sx2.toFixed(1)}" y2="81" stroke="var(--warning)" stroke-width="2"/>
      <line x1="${sx1.toFixed(1)}" y1="76" x2="${sx1.toFixed(1)}" y2="86" stroke="var(--warning)" stroke-width="1.5"/>
      <line x1="${sx2.toFixed(1)}" y1="76" x2="${sx2.toFixed(1)}" y2="86" stroke="var(--warning)" stroke-width="1.5"/>
      <text x="${sm.toFixed(1)}" y="100" text-anchor="${sAnchor}" font-size="12.5" font-family="monospace" font-weight="600" fill="var(--warning)">${esc(sp.lbl)}</text>`;
  });
  const zt1 = Math.max(L, mapTop(sig.zoom_lo)), zt2 = Math.min(R, mapTop(sig.zoom_hi));
  if(cis.length === 0){
    const emptyNote = sig.empty_cis_note || ('Isoform locus: ' + sig.chrom + ':' + sig.zoom_lo + '-' + sig.zoom_hi);
    ssoSvg = `<rect x="${L+10}" y="158" width="${W-20}" height="30" rx="4" fill="var(--background)" stroke="var(--warning)" stroke-width="1.4" stroke-dasharray="4,3"/>
      <text x="230" y="178" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--foreground)">${esc(emptyNote)}</text>`;
  } else {
    cis.forEach((c, idx) => {
      const y = 156 + idx * 44;
      const bx1 = Math.max(L, mapBot(Number(c.lo))), bx2 = Math.min(R, mapBot(Number(c.hi)));
      const bCol = c.st==='PASS_CLEAN_GE2MM' ? 'var(--success)' : (c.st.startsWith('WARN') ? 'var(--error)' : 'var(--warning)');
      const stShort = c.st==='PASS_CLEAN_GE2MM' ? 'Clean >=2mm' : (c.st.startsWith('WARN') ? 'Warn CNS Hit' : (c.st.startsWith('FAIL') ? 'Fail 0mm' : 'Caution 1mm/Wob'));
      ssoSvg += `<g>
        <rect x="${bx1.toFixed(1)}" y="${y}" width="${Math.max(12, bx2-bx1).toFixed(1)}" height="10" rx="3" fill="${bCol}" ${c.st.startsWith('WARN')?'stroke="var(--foreground)" stroke-dasharray="2,2"':''}/>
        <text x="${L}" y="${y+23}" font-size="12.6" font-family="monospace" font-weight="${c.lead?'700':'500'}" fill="var(--foreground)">${c.lead?'★ ':''}#${c.rk} ${esc(c.iv)}</text>
        <text x="${R}" y="${y+23}" text-anchor="end" font-size="12.5" font-family="monospace" font-weight="600" fill="${bCol}">${esc(stShort)}</text>
        <text x="${L}" y="${y+37}" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">${c.len}bp · Tm=${c.tm}°C · max AVI=${c.avi}</text>
      </g>`;
    });
  }
  const h = cis.length === 0 ? 198 : (160 + cis.length * 44);
  return `<svg viewBox="0 0 460 ${h}" class="w-full h-auto block select-none" role="img" aria-label="GRCh38 locus and steric SSO coordinate map">
    <text x="${L}" y="16" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">${esc(sig.chrom)}:${sig.win_lo.toLocaleString()}-${sig.win_hi.toLocaleString()} · ${esc(dirTxt)}</text>
    <line x1="${L}" y1="63" x2="${R}" y2="63" stroke="var(--border)" stroke-width="2.2"/>
    ${exSvg}${snpSvg}
    <polygon points="${zt1.toFixed(1)},71 ${zt2.toFixed(1)},71 ${R},132 ${L},132" fill="var(--primary)" fill-opacity="0.06" stroke="var(--border)" stroke-dasharray="3,3"/>
    <text x="${L}" y="127" font-size="12.5" font-family="monospace" fill="var(--primary)">Zoom: ${esc(sig.chrom)}:${sig.zoom_lo.toLocaleString()}-${sig.zoom_hi.toLocaleString()} (1-based GRCh38)</text>
    <line x1="${L}" y1="142" x2="${R}" y2="142" stroke="var(--foreground)" stroke-opacity="0.35" stroke-width="1.5"/>
    ${zoomExSvg}${ssoSvg}
  </svg>`;
}
"""
