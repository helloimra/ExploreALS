"""Client-side Dossier Standard v3 core: deterministic CURIE linkifier, 3-tier Causal Grid, Cleveland Lollipop/CI Matrix, & GRCh38 Locus SVG."""
from __future__ import annotations

DOSSIER_JS_SVG_CORE = """
const GENE_ENSG = {
  'EALS-030':'ENSG00000004139', 'EALS-006':'ENSG00000075043', 'EALS-031':'ENSG00000134460', 'EALS-001':'ENSG00000130477',
  'EALS-002':'ENSG00000104435', 'EALS-007':'ENSG00000115602', 'EALS-034':'ENSG00000168397', 'EALS-035':'ENSG00000160145',
  'EALS-036':'ENSG00000196090', 'EALS-037':'ENSG00000161082', 'EALS-038':'ENSG00000106772', 'EALS-039':'ENSG00000067057',
  'EALS-040':'ENSG00000171853', 'EALS-041':'ENSG00000126767', 'EALS-042':'ENSG00000170579', 'EALS-043':'ENSG00000130226',
  'EALS-044':'ENSG00000175497', 'EALS-045':'ENSG00000172757', 'EALS-046':'ENSG00000069535', 'EALS-047':'ENSG00000197405',
  'EALS-016':'ENSG00000118564', 'EALS-019':'ENSG00000162434', 'EALS-020':'ENSG00000115020',
  'EALS-022':'ENSG00000135924', 'EALS-023':'ENSG00000106636', 'EALS-024':'ENSG00000125730', 'EALS-053':'ENSG00000164430',
  'EALS-054':'ENSG00000172890', 'EALS-055':'ENSG00000055163',
  AGAP2:'ENSG00000135439', AKR1B1:'ENSG00000085662', AP1G2:'ENSG00000213983', ARHGEF11:'ENSG00000132694', ATG4B:'ENSG00000168397',
  BMPR1A:'ENSG00000107779', BRSK2:'ENSG00000174672', C1QA:'ENSG00000173372', C1QB:'ENSG00000173369', C1QC:'ENSG00000159189',
  C3:'ENSG00000125730', C4B:'ENSG00000224389', C5AR1:'ENSG00000197405', CAPG:'ENSG00000042493',
  CELF5:'ENSG00000161082', CFL1:'ENSG00000172757', CGAS:'ENSG00000164430', CHI3L1:'ENSG00000133048', CHI3L2:'ENSG00000064886',
  CHIT1:'ENSG00000133063', CHMP2B:'ENSG00000083937', CHMP7:'ENSG00000147457', CLK3:'ENSG00000179335',
  CLOCK:'ENSG00000134852', CYFIP1:'ENSG00000273749', CYFIP2:'ENSG00000055163', DAB1:'ENSG00000173406', DDB1:'ENSG00000167986', DDX1:'ENSG00000079785',
  DENR:'ENSG00000139726', DLGAP1:'ENSG00000170579', DNAJB2:'ENSG00000135924', DPP10:'ENSG00000175497',
  DPP6:'ENSG00000130226', ELK1:'ENSG00000126767', ELOC:'ENSG00000154582', ERBB4:'ENSG00000178568',
  ETV3:'ENSG00000117036', FBXL5:'ENSG00000118564', G2E3:'ENSG00000092140', GDI2:'ENSG00000057608',
  GOSR1:'ENSG00000108587', GPNMB:'ENSG00000136235', GPR156:'ENSG00000175697', IFI16:'ENSG00000163565', IFNAR1:'ENSG00000142166', IL1RL1:'ENSG00000115602',
  IL2RA:'ENSG00000134460', IKBKE:'ENSG00000263528', IQGAP1:'ENSG00000140575', IREB2:'ENSG00000136381', JAK1:'ENSG00000162434',
  JAK2:'ENSG00000096968', KALRN:'ENSG00000160145', KCND3:'ENSG00000171385', KCNQ2:'ENSG00000075043',
  KCNQ3:'ENSG00000184156', KIFC2:'ENSG00000167702', MAOB:'ENSG00000069535', MEGF10:'ENSG00000145794', MIB2:'ENSG00000197530',
  MYO18A:'ENSG00000196535', MYOCD:'ENSG00000141052', NADSYN1:'ENSG00000172890', NAMPT:'ENSG00000105835', NMNAT2:'ENSG00000157064', NSF:'ENSG00000073969', OPTN:'ENSG00000123240', PAFAH1B1:'ENSG00000007168',
  PFKP:'ENSG00000067057', PIKFYVE:'ENSG00000115020', PPA2:'ENSG00000138777', PRUNE2:'ENSG00000106772', PSMB8:'ENSG00000204264',
  PTAR1:'ENSG00000188647', PTCH1:'ENSG00000185920', PTPRT:'ENSG00000196090', RIPK1:'ENSG00000137275', SARM1:'ENSG00000004139', SCFD1:'ENSG00000092108',
  SEC22B:'ENSG00000265808', SLC12A5:'ENSG00000124140', SNPH:'ENSG00000101298', SRPK2:'ENSG00000135250',
  STING1:'ENSG00000184584', STMN2:'ENSG00000104435', STX5:'ENSG00000162236', TBK1:'ENSG00000183735', TENM2:'ENSG00000145934', TFRC:'ENSG00000072274', TRAPPC12:'ENSG00000171853',
  TYK2:'ENSG00000105397', UNC13A:'ENSG00000130477', VAPB:'ENSG00000124164', YKT6:'ENSG00000106636', ZNF783:'ENSG00000204946'
};
const CHEMBL_COMPOUNDS = new Set([
  'CHEMBL1200798','CHEMBL1201438','CHEMBL1214124','CHEMBL124363','CHEMBL1456','CHEMBL161',
  'CHEMBL2105759','CHEMBL2365743','CHEMBL289228','CHEMBL298734','CHEMBL35','CHEMBL3545058',
  'CHEMBL3752910','CHEMBL3989871','CHEMBL41355','CHEMBL4297372','CHEMBL4297643','CHEMBL4297672','CHEMBL4448176','CHEMBL5189857','CHEMBL5653589','CHEMBL589',
  'CHEMBL621','CHEMBL744','CHEMBL778','CHEMBL807','CHEMBL83','CHEMBL866'
]);
const ACC_TOKEN_RE = /(?<![A-Za-z0-9])(?:PMID:(\\d{5,9})|(PMC\\d{6,9})|(?:DOI:\\s*)?(10\\.\\d{4,9}\\/[^\\s,;\\]\\u00b7&<>"]+)|(NCT\\d{8})|(AAN2026-\\d{6})|(ACTRN\\d{14})|ISRCTN(\\d{8})|((?:WO20\\d{8}|US\\d{7,11}|CA\\d{7})(?:[A-Z]\\d?)?)|PDB\\s+([0-9][A-Za-z0-9]{3})|(7DJT|9TZY|7ANW|7NAL|7CR2|4KC3|2Z0D|3NMR|2DNH|6VN8|1XFD|7K2V|3KYQ|6J74|3EGD|3V5Z|6VCD|6C1R|1MQS|1Y9J|1PK6|5O33|2OOQ|5YPO|6TNQ|1DUX|4XYJ|6MJW|6LRC|6NT5|4KSY|6MXE|6OFB|3P8C)|(CHEMBL\\d+)|CID:(\\d+)|(ENS[GT]\\d{11})(?:\\.\\d+)?|HGNC:(\\d+)|MGI:(\\d+)|OMIM\\s+(\\d{6})|AF-([A-Z0-9]{6,10})-F\\d+|((?:O14490|O14522|O15498|O43526|O60229|O60674|O75396|O95249|P02745|P02746|P02747|P19419|P23458|P23528|P25686|P27338|P28062|P42658|P42779|P46459|P50395|P60568|Q01638|Q01813|Q13190|Q16666|Q6IA69|Q6SZW1|Q7L622|Q86WV6|Q8C6L5|Q8N608|Q8N6W0|Q8N884|Q8WUY3|Q8WVM8|Q8WVT3|Q93045|Q96F07|Q9UKA1|Q9UPW8|Q9Y4P1)(?:-\\d+)?)|(gnomAD\\s+(?:v4(?:\\.1)?|r4|v2\\.1\\.1))|(GSE\\d{4,8}|GSM\\d{6,8})|(PXD\\d{5,8})|(PRJNA\\d{5,9})|(syn\\d{6,10})|(rs\\d{3,12})|(mmc[245]\\.xlsx))(?![A-Za-z0-9])/g;

function mkExtA(url, lbl){
  return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid">${lbl}</a>`;
}
function linkifyAcc(escapedStr, geneCtx){
  if(!escapedStr) return '';
  return String(escapedStr).replace(ACC_TOKEN_RE, (full, pmid, pmc, doi, nct, aan, actrn, isrctn, pat, pdbPref, pdbBare, chembl, cid, ens, hgnc, mgi, omim, af, uniprot, gnomad, gse, pxd, prjna, syn, rsid, mmc, offset, wholeStr) => {
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
    if(aan) return mkExtA('https://index.mirasmart.com/AAN2026/PDFfiles/' + aan + '.html', full);
    if(actrn) return mkExtA('https://www.anzctr.org.au/TrialSearch.aspx?searchTxt=' + actrn, full);
    if(isrctn) return mkExtA('https://www.isrctn.com/ISRCTN' + isrctn, full);
    if(pat) return mkExtA('https://patents.google.com/patent/' + pat, full);
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
    if(uniprot) return mkExtA('https://www.uniprot.org/uniprotkb/' + uniprot.split('-')[0] + '/entry', full);
    if(gnomad){
      let gid = GENE_ENSG[geneCtx] || '';
      const srcStr = String(wholeStr || ''), pos = Number(offset || 0);
      const aft = srcStr.slice(pos + full.length, pos + full.length + 34);
      const mAft = /^\\s+(?:MANE(?:\\s+Select)?\\s+)?([A-Z][A-Z0-9]{2,9})\\b/.exec(aft);
      if(mAft && GENE_ENSG[mAft[1]]) gid = GENE_ENSG[mAft[1]];
      else {
        const preWin = srcStr.slice(Math.max(0, pos - 120), pos);
        const sentPre = preWin.slice(Math.max(preWin.lastIndexOf('. '), preWin.lastIndexOf('\\n')) + 1);
        const mEnsg = /\\b(ENSG\\d{11})\\b(?![\\s\\S]*\\bENSG\\d{11}\\b)/.exec(sentPre);
        if(mEnsg) gid = mEnsg[1];
        else {
          const gSyms = sentPre.match(/\\b[A-Z][A-Z0-9]{2,9}\\b/g) || [];
          for(let gi = gSyms.length - 1; gi >= 0; gi--){
            if(GENE_ENSG[gSyms[gi]]){ gid = GENE_ENSG[gSyms[gi]]; break; }
          }
        }
      }
      const gUrl = gid ? ('https://gnomad.broadinstitute.org/gene/' + gid + '?dataset=gnomad_r4') : 'https://gnomad.broadinstitute.org/';
      return mkExtA(gUrl, full);
    }
    if(gse) return mkExtA('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + gse, full);
    if(pxd) return mkExtA('https://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=' + pxd, full);
    if(prjna) return mkExtA('https://www.ncbi.nlm.nih.gov/bioproject/' + prjna, full);
    if(syn) return mkExtA('https://www.synapse.org/Synapse:' + syn, full);
    if(rsid) return mkExtA('https://www.ncbi.nlm.nih.gov/snp/' + rsid, full);
    if(mmc) return mkExtA('https://ars.els-cdn.com/content/image/1-s2.0-S1934590923001352-' + mmc, full);
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

const VALID_SUB_IDS = new Set([
  'EALS-014.1','EALS-014.2','EALS-015.1','EALS-015.2',
  'EALS-017.1','EALS-017.2','EALS-017.3','EALS-017.4',
  'EALS-018.1','EALS-018.2','EALS-018.3','EALS-018.4',
  'EALS-023.1','EALS-023.2','EALS-023.3','EALS-023.4','EALS-023.5','EALS-023.6'
]);
function padEals(n){ return 'EALS-' + String(Number(n)).padStart(3, '0'); }
function normSlugJs(s){ return String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, ''); }
function normQueryJs(qRaw){ return String(qRaw || '').trim().toLowerCase().replace(/\\b(eals|ea)\\s+(0*\\d)/g, (_, a, b) => a + '-' + b); }

function parseIdTokenJs(rawTok){
  const tk = String(rawTok || '').trim().toLowerCase();
  if(!tk) return null;
  const mRk = /^#([1-9]|[1-4][0-9]|5[0-5])$/.exec(tk);
  if(mRk && typeof DATA_PORT !== 'undefined'){
    const hit = DATA_PORT.find(x => x.rk === Number(mRk[1]));
    if(hit) return {id: hit.id, sub: '', kind: 'rank'};
  }
  const mEa = /^(?:eals|ea)[-_ ]?0*([1-9]|[1-4][0-9]|5[0-5])(?:[.-]([1-9]))?$/.exec(tk);
  if(mEa){
    const par = padEals(mEa[1]);
    const sub = mEa[2] ? (par + '.' + mEa[2]) : '';
    if(sub && !VALID_SUB_IDS.has(sub)) return null;
    return {id: par, sub: sub, kind: 'eals'};
  }
  const mPad = /^0(0[1-9]|[1-4][0-9]|5[0-5])(?:[.]([1-9]))?$/.exec(tk);
  if(mPad){
    const par = padEals(mPad[1]);
    const sub = mPad[2] ? (par + '.' + mPad[2]) : '';
    if(sub && !VALID_SUB_IDS.has(sub)) return null;
    return {id: par, sub: sub, kind: 'eals'};
  }
  return null;
}

function resolveCandidateId(raw){
  if(!raw) return null;
  const tok = normQueryJs(raw);
  const parsed = parseIdTokenJs(tok);
  if(parsed && (typeof DATA_PORT === 'undefined' || DATA_PORT.some(x => x.id === parsed.id))) return parsed;
  const slug = normSlugJs(tok);
  if(!slug) return null;
  if(typeof DATA_SUB !== 'undefined'){
    const snHit = DATA_SUB.find(sn => normSlugJs(sn.gene) === slug);
    if(snHit) return {id: snHit.par, sub: snHit.id, kind: 'subunit'};
  }
  if(typeof DATA_PORT !== 'undefined'){
    const pHit = DATA_PORT.find(r => normSlugJs(r.sym) === slug || normSlugJs(r.name.split('(')[0]) === slug || (r.syn || []).some(a => normSlugJs(a) === slug));
    if(pHit) return {id: pHit.id, sub: '', kind: 'slug'};
  }
  return null;
}

function matchCandidateQuery(r, qRaw, extraHay=''){
  const q = normQueryJs(qRaw);
  if(!q) return {ok: true, tier: 9, sub: ''};
  const hay = (r.id + ' ' + r.name + ' ' + (r.sym || '') + ' ' + (r.syn || []).join(' ') + ' ' + r.mod + ' ' + r.hurdles + ' ' + r.sub + ' ' + (r.crowd || '') + ' ' + extraHay).toLowerCase();
  const subList = (typeof DATA_SUB !== 'undefined') ? DATA_SUB.filter(sn => sn.par === r.id) : [];
  const toks = q.split(/\\s+/).filter(Boolean);
  let bestTier = 9;
  let subHit = '';
  for(let i = 0; i < toks.length; i++){
    const tk = toks[i];
    const pTok = parseIdTokenJs(tk);
    if(pTok && pTok.id === r.id){
      bestTier = Math.min(bestTier, 1);
      if(pTok.sub) subHit = subHit || pTok.sub;
      continue;
    }
    const slug = normSlugJs(tk);
    const snMatch = slug ? subList.find(sn => normSlugJs(sn.gene) === slug) : null;
    if(snMatch) subHit = subHit || snMatch.id;
    const exactBio = (slug && (normSlugJs(r.sym) === slug || (r.syn || []).some(a => normSlugJs(a) === slug) || Boolean(snMatch))) ||
      (tk === 'c3' && r.id === 'EALS-024') || (tk === 'c4' && r.id === 'EALS-018') || (tk === 'c5' && r.id === 'EALS-047') ||
      (tk === 'c1' && r.id === 'EALS-018') || (tk === 'c9' && (hay.includes('c9orf72') || hay.includes('c9-als') || hay.includes('c9-ftd')));
    if(exactBio){ bestTier = Math.min(bestTier, 2); continue; }
    if(hay.includes(tk)){ bestTier = Math.min(bestTier, 4); continue; }
    return {ok: false, tier: 99, sub: ''};
  }
  return {ok: true, tier: bestTier, sub: subHit};
}

function queryMatchesIdOrText(idsList, qRaw, hayRaw){
  const q = normQueryJs(qRaw);
  if(!q) return true;
  const hay = String(hayRaw || '').toLowerCase();
  const toks = q.split(/\\s+/).filter(Boolean);
  return toks.every(tk => {
    if(hay.includes(tk)) return true;
    const res = resolveCandidateId(tk);
    if(!res) return false;
    if(res.sub) return idsList.some(id => id === res.sub || id === res.id);
    return idsList.some(id => id === res.id || String(id).startsWith(res.id + '.'));
  });
}

function renderCausalGrid(c, geneCtx){
  const cards = c.nodes.map((nd, i) => {
    const isLast = i === 3;
    const bdr = isLast ? 'border-[var(--success)] border-2' : 'border-[var(--border)]';
    const badge = isLast ? 'bg-[var(--success)] text-[var(--primary-foreground)]' : 'bg-[var(--content)] text-[var(--foreground)] border border-[var(--border)]';
    const stepTag = isLast ? '4 &middot; INTERVENTION' : `STEP ${i+1} &rarr;`;
    return `<div class="p-3.5 rounded-lg bg-[var(--background)] border ${bdr} flex flex-col space-y-1.5 text-xs">
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
    <div class="p-3.5 rounded-lg bg-[var(--background)] border ${boxCls} space-y-1.5 text-xs">
      <div class="font-mono font-bold leading-snug ${hdrCls}">${icon} ${esc(c.trap_title)}</div>
      <p class="text-[var(--foreground)] leading-relaxed break-words">${escLink(c.trap_desc, geneCtx)}</p>
    </div>
  </div>`;
}

function renderEvidenceMatrix(ev, geneCtx){
  const meta = {
    log2fc: {hdr:'Effect Size: log2FC / \u0394log2CPM (-3.0 to +4.0, null = 0.0)', tL:'-3.0', tM:'0.0', tR:'+4.0', midPct:(3.0 / 7.0) * 100},
    dpsi:   {hdr:'Cryptic / Isoform Junction Shift (\u0394PSI: 0.00 to 1.00)', tL:'0.00', tM:'0.50', tR:'1.00', midPct:50.0},
    hr:     {hdr:'Survival Hazard Ratio (Log Scale: 0.12 to 3.00, null HR = 1.00)', tL:'0.12 (Benefit)', tM:'HR=1.0', tR:'3.00', midPct:((Math.log(1.0) - Math.log(0.12)) / (Math.log(3.0) - Math.log(0.12))) * 100},
    auc:    {hdr:'Biomarker / Pathway Discrimination (ROC-AUC: 0.50 null to 1.00)', tL:'0.50 (Null)', tM:'0.75', tR:'1.00', midPct:50.0},
  };
  const mapVal = (k, v) => {
    const num = Number(v);
    if(k === 'log2fc') return Math.max(1, Math.min(99, ((Math.max(-3.0, Math.min(4.0, num)) + 3.0) / 7.0) * 100));
    if(k === 'dpsi') return Math.max(1, Math.min(99, Math.max(0.0, Math.min(1.0, num)) * 100));
    if(k === 'hr'){
      const cHr = Math.max(0.12, Math.min(3.0, num));
      return Math.max(1, Math.min(99, ((Math.log(cHr) - Math.log(0.12)) / (Math.log(3.0) - Math.log(0.12))) * 100));
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
      const survTag = r.tone === 'compensatory_or_survivor' ? '<span class="px-1 rounded border border-[var(--primary)] text-[var(--primary)] font-mono text-xs" title="Enriched in surviving residual neurons rather than causal pathogenic gain">Residual-Neuron Bias</span> ' : '';
      const pTag = isPrior ? '<span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] font-mono text-xs">Modeled</span> ' : '';
      return `<div class="py-1.5 border-b border-[var(--card-border)] last:border-b-0 space-y-1 text-xs">
        <div class="flex flex-wrap items-baseline justify-between gap-x-2 gap-y-0.5">
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
      <div class="relative h-4 font-mono text-xs text-[var(--muted-foreground)] opacity-80">
        <span class="absolute left-0 top-0">${meta[k].tL}</span>
        <span class="absolute top-0" style="left:${meta[k].midPct.toFixed(1)}%;transform:translateX(-50%)">${meta[k].tM}</span>
        <span class="absolute right-0 top-0">${meta[k].tR}</span>
      </div>
      <div>${rowsHtml}</div>
    </div>`;
  });
  const callouts = (ev.callouts || []).map(c => {
    const isP = c.tag === 'MODEL_PRIOR';
    const bdr = isP ? 'border-dashed border-[var(--warning)]' : 'border-[var(--card-border)]';
    return `<div class="p-2.5 rounded bg-[var(--background)] border ${bdr} flex flex-col justify-between gap-1 text-xs">
      <div class="text-[var(--muted-foreground)] leading-relaxed break-words">${escLink(c.lbl, geneCtx)}</div>
      <div class="flex items-center justify-between gap-1.5 font-mono pt-0.5">
        <span class="font-bold text-[var(--foreground)]">${esc(c.stat)}</span>
        <span class="${isP?'text-[var(--warning)]':'text-[var(--muted-foreground)]'}">${isP?'Modeled &middot; ':''}${esc(c.p)}</span>
      </div>
    </div>`;
  }).join('');
  const leg = `<div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs font-mono text-[var(--muted-foreground)] pb-0.5">
    <span>&#9679; Empirical Data</span><span>&#9671; Modeled Estimate</span><span>&#9500;&#9472;&#9679;&#9472;&#9508; 95% CI (staged)</span><span>&#9472;&#9472;&#9679; Point stem (p/FDR)</span>
  </div>`;
  return `<div class="space-y-2.5">${leg}${groupsHtml}${callouts?`<div class="space-y-1.5"><div class="font-mono text-xs font-semibold text-[var(--muted-foreground)]">Biophysical, Correlation &amp; Power Metrics</div><div class="grid grid-cols-1 sm:grid-cols-2 gap-2">${callouts}</div></div>`:''}</div>`;
}

function cautionSummary(c){
  if(!c) return {short: 'Caution (non-CNS hit)', badge: 'Caution &middot; Non-CNS Hit', tip: 'Non-constrained reference hybridization match (zero constrained CNS pLI >= 0.9 hits); empirical microwalk required'};
  const sp = String(c.sp || '').split('/').map(x => parseInt(x, 10) || 0);
  const pm = String(c.pm || '').split('/').map(x => parseInt(x, 10) || 0);
  const s1 = sp[1] || 0, sWob = sp[2] || 0;
  const p0 = pm[0] || 0, p1s50 = pm[1] || 0, pWob50 = pm[2] || 0, p2s25 = pm[3] || 0, pBulge = pm[4] || 0, pSub18 = pm[5] || 0;
  const flg = (c.flags && c.flags !== 'NONE') ? (' (' + esc(c.flags) + ')') : '';
  const pmAll = (c.pm1_all != null) ? (c.pm1_all + ' unrestricted sense pre-mRNA 1-mm gene(s)') : '';
  const svgToks = [], bdgToks = [], tipParts = [];
  if(p0 > 0){ svgToks.push('intron 0-mm'); bdgToks.push('Intron 0-mm (' + p0 + ')'); tipParts.push(p0 + ' deep-intronic sense pre-mRNA 0-mm match(es)' + flg); }
  if(s1 > 0 || p1s50 > 0){ svgToks.push('1-mm'); bdgToks.push('1-mm'); tipParts.push((s1 ? (s1 + ' spliced 1-mm') : '') + (s1 && p1s50 ? ' + ' : '') + (p1s50 ? (p1s50 + ' <=50bp-SS 1-mm') : '') + (p0 === 0 ? flg : '')); }
  if(sWob > 0 || pWob50 > 0){ svgToks.push('wobble'); bdgToks.push('Wobble'); tipParts.push((sWob ? (sWob + ' spliced G:U wobble') : '') + (sWob && pWob50 ? ' + ' : '') + (pWob50 ? (pWob50 + ' <=50bp-SS wobble') : '')); }
  if(p2s25 > 0){ svgToks.push(svgToks.length ? '2-mm' : '25bp 2-mm'); bdgToks.push('25bp 2-mm (' + p2s25 + ')'); tipParts.push(p2s25 + ' non-constrained <=25bp-SS 2-mm hit(s)'); }
  if(pBulge > 0){ svgToks.push('bulge'); bdgToks.push('1-nt Bulge (' + pBulge + ')'); tipParts.push(pBulge + ' non-constrained 1-nt bulge hit(s)'); }
  if(pSub18 > 0){ svgToks.push(svgToks.length ? 'sub-core' : '18-nt sub-core'); bdgToks.push('18-nt Sub-Core (' + pSub18 + ')'); tipParts.push(pSub18 + ' non-constrained 18-nt sub-core match(es)' + (p0 === 0 && s1 === 0 && p1s50 === 0 ? flg : '')); }
  let shortBody = svgToks.join(' + ');
  if(shortBody.length > 15) shortBody = svgToks.map(t => t.replace('intron 0-mm','intron 0mm').replace('wobble','wob').replace('sub-core','sub18').replace('2-mm','2mm').replace('1-mm','1mm')).join('+');
  const short = shortBody ? ('Caution (' + shortBody + ')') : 'Caution (non-CNS hit)';
  const badge = bdgToks.length ? ('Caution &middot; ' + bdgToks.slice(0, 2).join(' + ')) : 'Caution &middot; Non-CNS Hit';
  const tip = (tipParts.length ? tipParts.join('; ') : 'Non-constrained reference match') + ' (zero constrained CNS pLI >= 0.9 hits' + (pmAll ? '; ' + pmAll : '') + '); empirical microwalk required';
  return {short, badge, tip};
}

function renderLocusSsoSvg(candId, sig){
  const cis = DATA_CIS.filter(c => c.sc === candId || c.pid === candId).sort((a,b)=>(b.lead-a.lead)||(a.rk-b.rk));
  const L = 14, R = 446, W = R - L;
  const mapTop = p => L + ((p - sig.win_lo) / Math.max(1, sig.win_hi - sig.win_lo)) * W;
  const mapBot = p => L + ((p - sig.zoom_lo) / Math.max(1, sig.zoom_hi - sig.zoom_lo)) * W;
  const dirTxt = sig.strand === '+' ? "5' -> 3' (+ strand)" : "3' <- 5' (- strand)";
  let exSvg = '', snpSvg = '', zoomExSvg = '', ssoSvg = '';
  sig.exons.forEach((ex, idx) => {
    const x1 = Math.max(L, mapTop(ex.lo)), x2 = Math.min(R, mapTop(ex.hi)), xm = (x1 + x2) / 2;
    const col = ex.kind==='ce' ? 'var(--error)' : (ex.kind==='skip' ? 'var(--warning)' : 'var(--primary)');
    const dash = ex.kind==='ce' ? 'stroke-dasharray="3,2"' : '';
    const ly = idx === 1 ? 54 : 34;
    const anchor = idx === 0 ? 'start' : (idx === 2 ? 'end' : (xm < 130 ? 'start' : (xm > 330 ? 'end' : 'middle')));
    const tx = anchor==='start' ? Math.max(L, idx===0 ? L : x1) : (anchor==='end' ? Math.min(R, idx===2 ? R : x2) : xm);
    exSvg += `<rect x="${x1.toFixed(1)}" y="61" width="${Math.max(7, x2-x1).toFixed(1)}" height="16" rx="3" fill="${col}" stroke="var(--foreground)" stroke-opacity="0.25" ${dash}/>
      <text x="${tx.toFixed(1)}" y="${ly}" text-anchor="${anchor}" font-size="12.4" font-weight="600" fill="${idx===1?col:'var(--foreground)'}">${esc(ex.lbl)}</text>`;
  });
  const snpItems = (sig.snps||[]).map(sn => ({...sn, sx: Math.max(L+14, Math.min(R-14, mapTop(sn.pos)))})).sort((a,b)=>a.sx-b.sx);
  const spanItems = sig.spans || [];
  const bothTop = snpItems.length > 0 && spanItems.length > 0;
  const spanOff = bothTop ? 22 : 0;
  spanItems.forEach(sp => {
    const sx1 = Math.max(L+6, mapTop(sp.lo)), sx2 = Math.min(R-6, mapTop(sp.hi)), sm = (sx1 + sx2)/2;
    const sAnchor = sm < 130 ? 'start' : (sm > 330 ? 'end' : 'middle');
    const spY = 86;
    const spTxtY = 103;
    snpSvg += `<line x1="${sx1.toFixed(1)}" y1="${spY}" x2="${sx2.toFixed(1)}" y2="${spY}" stroke="var(--warning)" stroke-width="2"/>
      <line x1="${sx1.toFixed(1)}" y1="${spY-5}" x2="${sx1.toFixed(1)}" y2="${spY+5}" stroke="var(--warning)" stroke-width="1.5"/>
      <line x1="${sx2.toFixed(1)}" y1="${spY-5}" x2="${sx2.toFixed(1)}" y2="${spY+5}" stroke="var(--warning)" stroke-width="1.5"/>
      <text x="${sm.toFixed(1)}" y="${spTxtY}" text-anchor="${sAnchor}" font-size="12.3" font-family="monospace" font-weight="600" fill="var(--warning)">${esc(sp.lbl)}</text>`;
  });
  let maxSnpY = bothTop ? 103 : (spanItems.length > 0 ? 103 : 86);
  const rowRightBySlot = [-999, -999, -999];
  snpItems.forEach((sn) => {
    const sx = sn.sx;
    const estW = Math.max(84, sn.lbl.length * 7.6);
    const sAnchor = sx < 155 ? 'start' : (sx > 305 ? 'end' : 'middle');
    const tx = sAnchor === 'start' ? Math.max(L, sx - 6) : (sAnchor === 'end' ? Math.min(R, sx + 6) : sx);
    const estL = sAnchor === 'start' ? tx : (sAnchor === 'end' ? tx - estW : tx - estW / 2);
    const estR = estL + estW;
    let slot = 0;
    while(slot < 2 && estL < rowRightBySlot[slot] + 10) slot++;
    rowRightBySlot[slot] = Math.max(rowRightBySlot[slot], estR);
    const tickEnd = 89 + spanOff;
    const dotY = 91 + spanOff;
    const ty = 106 + spanOff + slot * 17;
    if(ty > maxSnpY) maxSnpY = ty;
    snpSvg += `<line x1="${sx.toFixed(1)}" y1="77" x2="${sx.toFixed(1)}" y2="${tickEnd}" stroke="var(--warning)" stroke-width="1.5"/>
      <circle cx="${sx.toFixed(1)}" cy="${dotY}" r="3.2" fill="var(--warning)"/>
      <text x="${tx.toFixed(1)}" y="${ty}" text-anchor="${sAnchor}" font-size="12.2" font-family="monospace" fill="var(--muted-foreground)">${esc(sn.lbl)}</text>`;
  });
  const zoomLblY = Math.max(134, maxSnpY + 20);
  const zoomPolyY = zoomLblY + 6;
  const zoomAxisY = zoomPolyY + 10;
  sig.exons.forEach((ex) => {
    const col = ex.kind==='ce' ? 'var(--error)' : (ex.kind==='skip' ? 'var(--warning)' : 'var(--primary)');
    if(ex.hi >= sig.zoom_lo && ex.lo <= sig.zoom_hi){
      const zx1 = Math.max(L, mapBot(Math.max(ex.lo, sig.zoom_lo))), zx2 = Math.min(R, mapBot(Math.min(ex.hi, sig.zoom_hi)));
      zoomExSvg += `<rect x="${zx1.toFixed(1)}" y="${zoomAxisY-6}" width="${Math.max(5, zx2-zx1).toFixed(1)}" height="12" rx="2" fill="${col}" fill-opacity="0.35" stroke="${col}" stroke-width="1.1"/>`;
    }
  });
  const zt1 = Math.max(L, mapTop(sig.zoom_lo)), zt2 = Math.min(R, mapTop(sig.zoom_hi));
  const hasNotes = Boolean(sig.iv_notes);
  const rowH = hasNotes ? 68 : 48;
  const zSpans = sig.zoom_spans || [];
  const startRowY = zoomAxisY + 14;
  let baseRowY = startRowY;
  if(cis.length === 0 && zSpans.length === 0){
    const emptyNote = sig.empty_cis_note || ('Isoform locus: ' + sig.chrom + ':' + sig.zoom_lo + '-' + sig.zoom_hi);
    ssoSvg = `<rect x="${L+10}" y="${startRowY+2}" width="${W-20}" height="30" rx="4" fill="var(--background)" stroke="var(--warning)" stroke-width="1.4" stroke-dasharray="4,3"/>
      <text x="230" y="${startRowY+22}" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--foreground)">${esc(emptyNote)}</text>`;
    baseRowY = startRowY + 42;
  } else {
    cis.forEach((c, idx) => {
      const y = startRowY + idx * rowH;
      const bx1 = Math.max(L, mapBot(Number(c.lo))), bx2 = Math.min(R, mapBot(Number(c.hi)));
      const bCol = c.st==='PASS_CLEAN_GE2MM' ? 'var(--success)' : (c.st.startsWith('WARN') ? 'var(--error)' : 'var(--warning)');
      const cs = c.st.startsWith('CAUTION') ? cautionSummary(c) : null;
      const stShort = c.st==='PASS_CLEAN_GE2MM' ? 'Clean (>=2mm)' : (c.st.startsWith('WARN') ? 'Warn CNS Hit' : (c.st.startsWith('FAIL') ? 'Fail 0-mm' : cs.short));
      const ivNote = (sig.iv_notes && sig.iv_notes[String(c.rk)]) ? sig.iv_notes[String(c.rk)] : '';
      ssoSvg += `<g>${cs?`<title>${cs.tip}</title>`:''}
        <rect x="${bx1.toFixed(1)}" y="${y}" width="${Math.max(12, bx2-bx1).toFixed(1)}" height="10" rx="3" fill="${bCol}" ${c.st.startsWith('WARN')?'stroke="var(--foreground)" stroke-dasharray="2,2"':''}/>
        <text x="${L}" y="${y+23}" font-size="12.5" font-family="monospace" font-weight="${c.lead?'700':'500'}" fill="var(--foreground)">${c.lead?'★ ':''}#${c.rk} ${esc(c.iv)}</text>
        <text x="${R}" y="${y+23}" text-anchor="end" font-size="12.4" font-family="monospace" font-weight="600" fill="${bCol}">${esc(stShort)}</text>
        <text x="${L}" y="${y+39}" font-size="12.3" font-family="monospace" fill="var(--muted-foreground)">${c.len}bp · Tm=${c.tm}°C · max AVI=${c.avi}</text>
        ${ivNote?`<text x="${L}" y="${y+56}" font-size="12.2" fill="var(--warning)">&#9656; ${esc(ivNote)}</text>`:''}
      </g>`;
    });
    baseRowY = startRowY + cis.length * rowH;
    zSpans.forEach((zs, zIdx) => {
      const zy = baseRowY + zIdx * 54;
      const zx1 = Math.max(L, mapBot(Number(zs.lo))), zx2 = Math.min(R, mapBot(Number(zs.hi)));
      const zCol = zs.tone==='clean' ? 'var(--success)' : (zs.tone==='hazard' ? 'var(--error)' : 'var(--warning)');
      ssoSvg += `<g>
        <rect x="${zx1.toFixed(1)}" y="${zy}" width="${Math.max(12, zx2-zx1).toFixed(1)}" height="9" rx="2.5" fill="${zCol}" fill-opacity="0.78" stroke="${zCol}" stroke-dasharray="3,2"/>
        <text x="${L}" y="${zy+23}" font-size="12.4" font-weight="600" fill="${zCol}">${esc(zs.lbl)}</text>
        <text x="${L}" y="${zy+40}" font-size="12.2" font-family="monospace" fill="var(--muted-foreground)">${esc(zs.sub || '')}</text>
      </g>`;
    });
    baseRowY += zSpans.length * 54;
  }
  const h = baseRowY + 8;
  return `<svg viewBox="0 0 460 ${h}" class="w-full h-auto block select-none" role="img" aria-label="GRCh38 locus and steric SSO coordinate map">
    <text x="${L}" y="15" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">${esc(sig.chrom)}:${sig.win_lo.toLocaleString()}-${sig.win_hi.toLocaleString()} · ${esc(dirTxt)}</text>
    <line x1="${L}" y1="69" x2="${R}" y2="69" stroke="var(--border)" stroke-width="2.2"/>
    ${exSvg}${snpSvg}
    <polygon points="${zt1.toFixed(1)},77 ${zt2.toFixed(1)},77 ${R},${zoomPolyY} ${L},${zoomPolyY}" fill="var(--primary)" fill-opacity="0.06" stroke="var(--border)" stroke-dasharray="3,3"/>
    <text x="${L}" y="${zoomLblY}" font-size="12.4" font-family="monospace" fill="var(--primary)">Zoom: ${esc(sig.chrom)}:${sig.zoom_lo.toLocaleString()}-${sig.zoom_hi.toLocaleString()} (1-based GRCh38)</text>
    <line x1="${L}" y1="${zoomAxisY}" x2="${R}" y2="${zoomAxisY}" stroke="var(--foreground)" stroke-opacity="0.35" stroke-width="1.5"/>
    ${zoomExSvg}${ssoSvg}
  </svg>`;
}
"""
