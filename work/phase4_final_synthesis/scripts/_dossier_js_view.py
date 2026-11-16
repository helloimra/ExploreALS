"""Client-side Candidate Dossier & Monograph Standard v3.1 view (5Rs + Open Targets + FAIR / 4-Level Evidence Design Standard)."""
from __future__ import annotations

DOSSIER_JS_VIEW = """
const MONOGRAPH_ORDER = ['S06','C006','S07','C001','C002','C007','DN-01','DN-04'];
let dossierId = 'S06';
let dossierSlice = 'ALL';
let dossierLens = 'ALL';

const ENUM_LABELS = {
  TIER_1_ACTIONABLE_NOW: 'Tier 1 · Actionable Now',
  TIER_2_FOCUSED_GATE_FIRST: 'Tier 2 · Focused Gate First',
  TIER_3_EXPLORATORY_DISCOVERY: 'Tier 3 · Exploratory Discovery',
  COMPANION_PROTOCOL_ONLY: 'Companion PD Protocol',
  BIOMARKER_BENCHMARK_ONLY: 'Biomarker / SOC Benchmark',
  DROPPED_FALSIFIED_EXCLUDED: 'Dropped · Falsified',
  TRL_6_PH2B_SUBGROUP_BIOLOGIC: 'TRL 6 · Ph2b Subgroup Biologic',
  TRL_5_HUMAN_ALS_PK_PD_PROVEN: 'TRL 5 · Human ALS PK/PD Proven',
  TRL_4_ACTIVE_PH1_CLASS_OR_NCE: 'TRL 4 · Registered Ph1 / NCE Class',
  TRL_3_PRECLINICAL_SSO_COORDINATE: 'TRL 3 · Preclinical GRCh38 SSO',
  TRL_2_PRECLINICAL_MODALITY_DISCOVERY: 'TRL 2 · Preclinical Modality',
  TRL_1_TARGET_TOOL_PROBE_WATCHLIST: 'TRL 1 · Tool/Probe Watchlist',
  PROTOCOL_COMPANION_NA: 'Protocol / Benchmark (N/A)',
  MEASURED_HUMAN_GENETICS_AND_PATHOLOGY: 'Human Genetics + CNS Pathology',
  MEASURED_HUMAN_TDP43_PATHOLOGY_AND_RESCUE: 'Human TDP-43 Pathology + Rescue',
  MEASURED_HUMAN_RCT_SUBGROUP: 'Human ALS RCT Subgroup',
  MEASURED_C9FTD_FRACTION_PROTEOMICS: 'Human C9-FTD Fraction Proteomics',
  MEASURED_HUMAN_SPATIAL_OR_SNRNA: 'Human Spatial / snRNA-seq',
  MEASURED_HUMAN_CSF_PROTEOMICS: 'Living Human CSF Proteomics',
  MEASURED_HUMAN_PK_AND_IPSC_SCREEN: 'Human PK / Patient iPSC-MN Screen',
  PROTOCOL_STAGE_GATING_ONLY: 'Clinical Stage-Gating Protocol',
  TARGETED_PRECLINICAL_VALIDATION_GATE: 'Preclinical Cellular / Tissue Validation Gate',
  TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE: 'Human Biofluid / Phase 1b PK-PD Gate',
  DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE: 'De Novo Chemical / Biologic Modality Discovery',
  BIOMARKER_ENRICHED_PHASE3_EFFICACY_TRIAL: 'Biomarker-Enriched Phase 3 Survival RCT',
  CLINICAL_PROTOCOL_STANDARDIZATION: 'Clinical Protocol / Calibration Standard',
  NOT_APPLICABLE_FALSIFIED: 'N/A — Scientifically Falsified',
  EXPLORE_INHERITED_40: 'Seeded Literature, Clinical & QTL Set (40)',
  PHASE3B_DENOVO_19: 'Unbiased Multi-Omic Discovery Set (19)',
  CANONICAL_21: 'Genetic, Splicing & Clinical Targets',
  HISTORICAL_BA9_NAMED_10: 'Postmortem Cortical BA9 RNA-seq',
  SCREEN_AND_BLIND_SURVIVORS_9: 'RCT Subgroup & Screen Survivors',
  F1_CRYPTIC_SPLICE: 'Unbiased · TDP-43 Cryptic Exons',
  F2_CRYPTIC_APA: "Unbiased · Cryptic APA / 3'Ext",
  F3_CSF_SPATIAL: 'Unbiased · Living CSF & Spatial',
  F4_BYE2025_SCREEN: 'Unbiased · Human iPSC-MN Screen',
  PHASE2_3A_MULTIPLEX_12: 'Core 3-Plex & 14q12 Panel (12)',
  PHASE3B_DENOVO_14: 'Single-Entity De Novo Leads (14)',
  SUPPORTED: 'Supported (Human Genetics + Pathology)',
  UNPROVEN_UNTESTED: 'Unproven / Untested (Gate Required)',
  ESTABLISHED_BENCHMARK: 'Established SOC / PD Benchmark',
  FALSIFIED_CLINICAL: 'Falsified · Human ALS RCT Futility',
  FALSIFIED_PK_SAFETY: 'Falsified · CNS PK / Safety Wall',
  ARTIFACT_CONFOUNDED: 'Falsified · Postmortem Confounding',
  KEEP_CORE: 'Keep · Core',
  KEEP_EXPLORATORY_UNPROVEN: 'Keep · Exploratory',
  RECLASSIFY_BENCHMARK_OR_BIOMARKER: 'Benchmark / Biomarker',
  DROP: 'Drop · Falsified',
  SKIP_CRYPTIC_EXON: "Steric 2'-MOE SSO · Cryptic Exon Skip",
  CRYPTIC_CASSETTE_EXON_SKIP: "Steric 2'-MOE SSO · Cryptic Cassette Skip",
  CRYPTIC_CASSETTE_MAJOR_3SS_AND_SHARED_EXON: "Steric 2'-MOE SSO · Major 3'SS + Exonic",
  CRYPTIC_CASSETTE_DOWNSTREAM_INTRONIC_ISE: "Steric 2'-MOE SSO · Downstream Intronic ISE",
  INCLUDE_CONSTITUTIVE_EXON: "Steric 2'-MOE SSO · Exon-5 Inclusion (ISS)",
  INCLUDE_EXON_UPSTREAM_UG: "Steric 2'-MOE SSO · Exon-5 Inclusion (UG)",
  CRYPTIC_ALE_3SS_ACCEPTOR_BLOCK: "Steric 2'-MOE SSO · Cryptic ALE 3'SS Block",
  CRYPTIC_3EXT_ISOFORM_GAPMER_WINDOW: "Historical 3'Ext Window (Nuclear Gapmer Retired -> Steric PAS SSO)",
  CORE_3PLEX: 'Core 3-Plex',
  DEFERRED_4TH_CANDIDATE: 'Excluded 4th Axis',
  DENOVO_SINGLE_ENTITY: 'De Novo 1-Plex',
  NONE_FALSIFIED_CLINICAL: 'None — Falsified in human ALS clinical trials.',
  NONE_FALSIFIED_PK_SAFETY: 'None — Falsified by insurmountable human CNS PK deficit or clinical toxicity.',
  NONE_ARTIFACT_CONFOUNDED: 'None — Postmortem discovery signal collapsed under GC / cell-type confounding adjustment.',
};
const HURDLE_TOK = {
  SSO:'SSO', ASO:'ASO', IT:'IT', IV:'IV', SC:'SC', GLP:'GLP', CSF:'CSF', CNS:'CNS', BBB:'BBB', PD:'PD', PK:'PK',
  MN:'MN', CE:'CE', ALS:'ALS', FTD:'FTD', RCT:'RCT', MWC:'MWC', PAS:'PAS', ALE:'ALE', CLIA:'CLIA', RT:'RT',
  NCE:'NCE', TPM:'TPM', GWAS:'GWAS', OMIM:'OMIM', LOEUF:'LOEUF', STMN2:'STMN2', UNC13A:'UNC13A', KCNQ2:'KCNQ2',
  SARM1:'SARM1', BA4:'BA4', BA9:'BA9', C5:'C5', STAT2:'STAT2', STAT3:'STAT3', NADPH:'NADPH', GSH:'GSH', PPP:'PPP',
  ATP:'ATP', ROS:'ROS', DIA:'DIA', MS:'MS', TMT:'TMT', DNAJB2:'DNAJB2', DNAJB2A:'DNAJB2a', DNAJB2B:'DNAJB2b',
  IREB2:'IREB2', TFRC:'TFRC', HDGFL2:'HDGFL2', CASM:'CASM', ECM:'ECM', C1Q:'C1q', C1QA:'C1QA', '3KYQ':'3KYQ',
  '6VCD':'6VCD', FBXL5:'FBXL5', IRP2:'IRP2', '2Z0D':'2Z0D', TMS:'TMS', SICI:'SICI', SDTC:'SDTC', NPTX2:'NPTX2',
  CXCL10:'CXCL10', PE:'PE', DVT:'DVT', NADALS:'NADALS', FAIR:'FAIR-ALS', II:'II', PROTAC:'PROTAC', SATB2:'SATB2',
  LEMD2:'LEMD2', ANXA11:'ANXA11', SUN1:'SUN1', CHMP7:'CHMP7', SNPH:'SNPH', NEFH:'NEFH', BSN:'BSN', APP:'APP',
  SOD1:'SOD1', G93A:'G93A', KO:'KO', WT:'WT', SCFD1:'SCFD1', G2E3:'G2E3', YKT6:'YKT6', CYS195:'Cys195',
  PFKM:'PFKM', PFKL:'PFKL', SRF:'SRF', IFN:'IFN', ISGS:'ISGs', UG8:'UG8', CADPR:'cADPR', NFL:'NfL', PNFH:'pNfH',
  KPUU:'Kp,uu', IPSC:'iPSC', TLOCK:'T-Lock', GOF:'GoF', LOF:'LoF', TDP43:'TDP-43', TSTMN2:'tSTMN2', SST2:'sST2',
  PSTAT:'pSTAT', PSTAT2:'pSTAT2', PSTAT3:'pSTAT3', DISIRNA:'di-siRNA', QPCR:'qPCR', DDPCR:'ddPCR', PH1B:'Ph1b',
  PH3:'Ph3', CA2:'Ca2+', '2FE2S':'[2Fe-2S]', QRL201:'QRL-201', TPN101:'TPN-101', ORF1P:'ORF1p', '3SS':"3'SS",
  '5SS':"5'SS", C5AR1:'C5aR1', CTAIL:'C-tail', SUB160DA:'<=160 Da', LT1PCT:'<1%', '34PCT':'34%', '36PCT':'36%',
  '1P5TPM':'1.5 TPM', '2P5UM':'2.5 uM', '400UM':'400 uM', '4NM':'4 nM', '2500NM':'2,500 nM', PGML:'pg/mL',
  '1PLEX':'1-plex', '2PLEX':'2-plex', '3PLEX':'3-plex', PLI1:'pLI=1.0', '14Q12':'14q12', N6:'n=6', N7:'n=7', P80:'p80',
  ELLA:'Ella', EUROIMMUN:'Euroimmun', GFAP:'GFAP', ER:'ER', EV:'EV', NHP:'NHP', EC50:'EC50', MRNA:'mRNA',
  SNRNA:'snRNA', C9:'C9', SALS:'sALS', C9FTD:'C9-FTD', BYE2025:'Bye 2025', JAK1:'JAK1', JAK2:'JAK2',
  APA:'APA', CATCH22:'catch-22', ISE:'ISE', ISS:'ISS', BIP:'BiP', CHOP:'CHOP', ERAD:'ERAD', PRM:'PRM',
  CGAS:'cGAS', STING:'STING', L1HS:'L1HS', IL6:'IL-6', '1151BP':'1,151-bp', N25:'n>=25', N20:'n>=20',
  '48MG':'48 mg', VTE:'VTE', AAK1:'AAK1', AA:'A/A', ANQUR:'ANQUR', FVC:'FVC', GE80:'>=80%', SIMOA:'Simoa',
  '2OMOE':"2'-MOE", POLII:'Pol II', ELK1:'ELK1', FDR:'FDR', MW:'MW', WASHU:'WashU', MWU:'MWU',
  BIOVENDOR:'BioVendor', ELISA:'ELISA', NDEV:'NDEV', DPCR:'dPCR', LOQ:'LOQ', SCG10:'SCG10', N9:'N=9',
  '1PE':'1 PE', '1DVT':'1 DVT', NCT04082832:'NCT04082832', NCT04313166:'NCT04313166', OLE:'OLE',
  PTDP43:'pTDP-43', '144MG':'144 mg', '53NM':'53 nM', MNS:'MNs', MTD:'MTD', PET:'PET', CUATSM:'CuATSM',
};
function humanizeEnum(s){
  if(!s || s === 'NONE') return 'None';
  if(ENUM_LABELS[s]) return ENUM_LABELS[s];
  return String(s).replace(/_/g, ' ');
}
function formatHurdle(code){
  if(!code || code === 'NONE') return 'None';
  const pre = String(code)
    .replace(/21CFR300_50/g, '21CFR300.50')
    .replace(/24_TO_48MG/g, '24–48 mg')
    .replace(/PH2_3/g, 'Ph2/3')
    .replace(/6VS6/g, '6 vs 6')
    .replace(/PMID_37317638/g, 'PMID:37317638')
    .replace(/KP_UU/g, 'Kp,uu')
    .replace(/GT99_9PCT/g, '>99.9%')
    .replace(/8_7PCT/g, '8.7%')
    .replace(/LE_3700/g, '<=3,700')
    .replace(/PLI_0_996/g, 'pLI=0.996')
    .replace(/CHRONOS_MINUS1_54/g, 'Chronos=-1.54')
    .replace(/NON_ORTHOSTERIC/g, 'non-orthosteric')
    .replace(/NON_C9/g, 'non-C9')
    .replace(/PRE_PH3/g, 'Pre-Ph3')
    .replace(/POST_QRL201/g, 'Post-QRL-201')
    .replace(/ALS_GLIA/g, 'ALS-Glia')
    .replace(/AA320_328/g, 'aa 320-328')
    .replace(/Q48_TO_Q72H/g, 'q48h-q72h');
  const words = pre.split('_').filter(Boolean).map(w => {
    if(HURDLE_TOK[w]) return HURDLE_TOK[w];
    if(/^(#|<=|>=|<|>|[0-9]|pLI=|Chronos=|21CFR|Pre-|Post-|ALS-|non-|aa )/.test(w)) return w;
    if(/^RS[0-9]+$/.test(w)) return w.toLowerCase();
    return w.toLowerCase();
  });
  const out = words.join(' ');
  return out ? (out[0].toUpperCase() + out.slice(1)) : code;
}
function formatPrior(code){
  if(!code || code === 'NONE') return 'None — Direct empirical data only';
  return String(code)
    .replace(/^COARSE_PRIOR_ONLY:/, '')
    .replace(/8mer_MWC_order_of_magnitude_2_to_7x/g, '8-mer MWC order-of-magnitude (2–7x)')
    .replace(/Tm_dG37_AVI_2Z0D_contacts/g, 'SantaLucia Tm, ΔG37, AlphaGenome AVI & PDB 2Z0D contacts')
    .replace(/Tm_dG37_AVI_composite_score/g, 'SantaLucia Tm, ΔG37 & AlphaGenome AVI composite score')
    .replace(/Post_hoc/g, 'Post-hoc')
    .replace(/8_7pct/g, '8.7%')
    .replace(/35_to_50pct/g, '35–50%')
    .replace(/2_to_7x/g, '2–7x')
    .replace(/minus85A3/g, '-85 Å³')
    .replace(/tau_ge_72h/g, 'τ ≥ 72h')
    .replace(/3700pg/g, '3,700 pg/mL')
    .replace(/HR062/g, 'HR = 0.62')
    .replace(/HR070/g, 'HR = 0.70')
    .replace(/53nM/g, '53 nM')
    .replace(/ALS_Glia/g, 'ALS-Glia')
    .replace(/_/g, ' ');
}
function formatModality(s){
  if(!s) return '';
  const raw = String(s);
  if(!raw.includes('_')) return raw;
  return raw
    .replace(/^Dropped_Failed_Human_ALS_Clinical_Regimen_/, 'Dropped (Failed Human ALS RCT): ')
    .replace(/^Dropped_PK_or_Safety_Infeasible_Regimen_/, 'Dropped (Infeasible Human CNS PK / Safety): ')
    .replace(/^Dropped_Confounded_Postmortem_Transcriptomic_Target_/, 'Dropped (Confounded Postmortem Call): ')
    .replace(/2OMOE/g, "2'-O-MOE").replace(/POPS/g, 'PO/PS').replace(/TLock/g, 'T-Lock').replace(/72mg/g, '72 mg')
    .replace(/ARM_TIR/g, 'ARM-TIR').replace(/ASHA624/g, 'ASHA-624').replace(/NaV1_6/g, 'NaV1.6')
    .replace(/Kv7_2_7_3/g, 'Kv7.2/7.3').replace(/Half_Life_Extended/g, 'Half-Life-Extended')
    .replace(/ECM_Anchored/g, 'ECM-Anchored').replace(/Anti_C1q/g, 'Anti-C1q')
    .replace(/Allele_Specific/g, 'Allele-Specific').replace(/Neuron_Selective/g, 'Neuron-Selective')
    .replace(/Non_Covalent/g, 'Non-Covalent').replace(/Non_Orthosteric/g, 'Non-Orthosteric').replace(/Non_Chelating/g, 'Non-Chelating')
    .replace(/CTail_aa320_328/g, 'C-Tail (aa 320–328)').replace(/Intron8/g, 'Intron-8').replace(/Intron9/g, 'Intron-9')
    .replace(/ERAD_Sparing/g, 'ERAD-Sparing')
    .replace(/Early_Onset_LE12m/g, 'Early-Onset (<=12m)').replace(/Q48_to_Q72h/g, 'q48h–q72h')
    .replace(/LINE1_RT/g, 'LINE-1 RT').replace(/TPN101/g, 'TPN-101').replace(/JAK2_Sparing/g, 'JAK2-Sparing')
    .replace(/Brain_Penetrant/g, 'Brain-Penetrant').replace(/Low_Dose/g, 'Low-Dose').replace(/Sub160Da/g, '<=160 Da')
    .replace(/_/g, ' ');
}
function splitTopClauses(raw, sepRe){
  const s = String(raw || '').trim();
  if(!s) return [];
  const flags = sepRe.flags.includes('g') ? sepRe.flags : (sepRe.flags + 'g');
  const re = new RegExp(sepRe.source, flags);
  const depths = new Array(s.length).fill(0);
  let d = 0;
  for(let i = 0; i < s.length; i++){
    const ch = s[i];
    if(ch === '(' || ch === '[') d++;
    depths[i] = d;
    if((ch === ')' || ch === ']') && d > 0) d--;
  }
  const parts = [];
  let last = 0, m;
  while((m = re.exec(s)) !== null){
    if(depths[m.index] === 0 && m[0].length > 0){
      const chunk = s.slice(last, m.index).trim();
      if(chunk) parts.push(chunk);
      last = m.index + m[0].length;
    }
    if(m[0].length === 0) re.lastIndex++;
  }
  const tail = s.slice(last).trim();
  if(tail) parts.push(tail);
  return parts.length ? parts : [s];
}
function capClause(c){
  if(!c) return '';
  return (/^[a-z]/.test(c) && !/^(?:pLI|q48|rs\\d|tSTMN2|sST2|sALS|iPSC|cADPR|mRNA|snRNA)/.test(c)) ? (c[0].toUpperCase() + c.slice(1)) : c;
}
function formatGateList(rawStr, ctx, isKill){
  const sep = isKill
    ? /,?\\s+OR\\s+|,\\s+(?=inadequate\\s+cervical|acute\\s+human|acute\\s+neuron|flat\\s+ventilation|failure\\s+to\\s+engage|collapse\\s+of\\s+ex\\s+vivo|steric\\s+cis-eviction|>[0-9]+%\\s+2-plex)/
    : /\\s+\\+\\s+|,?\\s+AND\\s+(?!(?:TDP-43-intact|0%\\s+98-bp|across\\s+48))|,\\s+(?=establishes\\s+NHP)|,\\s+and\\s+(?=Stage\\s+2|passes\\s+genotype|confirms\\s+penetrance)/;
  const clauses = splitTopClauses(rawStr, sep);
  if(clauses.length <= 1) return `<p class="leading-relaxed text-[var(--foreground)]">${escLink(rawStr, ctx)}</p>`;
  return `<ul class="space-y-1.5">${clauses.map((c, idx) => {
    const linked = escLink(capClause(c), ctx).replace(/^(Stage\\s+[12]\\b[^(:<]{0,28})/, m => '<strong>' + m + '</strong>');
    const mark = isKill
      ? '<span class="font-mono font-bold text-[var(--error)] shrink-0">&bull;</span>'
      : `<span class="font-mono font-bold text-[var(--success)] shrink-0">${idx+1}.</span>`;
    return `<li class="flex items-baseline gap-1.5 leading-snug text-[var(--foreground)]">${mark}<span class="min-w-0 break-words">${linked}</span></li>`;
  }).join('')}</ul>`;
}
function formatNextTest(s, ctx){
  if(!s) return '';
  if(ENUM_LABELS[s]) return `<span class="text-[var(--muted-foreground)] italic">${esc(ENUM_LABELS[s])}</span>`;
  const clauses = splitTopClauses(s, /;\\s+|,\\s+(?:then|followed by)\\s+|\\s+(?=\\([123]\\)\\s)/);
  if(clauses.length <= 1) return escLink(s, ctx);
  return `<ul class="list-disc pl-4 space-y-1 mt-1 leading-snug">${clauses.map(c => `<li class="break-words">${escLink(capClause(c), ctx)}</li>`).join('')}</ul>`;
}
function riskStateBadge(st){
  if(st==='LOW') return '<span class="px-2 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs shrink-0">&#10003; LOW / DE-RISKED</span>';
  if(st==='MITIGATED') return '<span class="px-2 py-0.5 rounded font-mono font-semibold text-[var(--primary)] border border-[var(--primary)] text-xs shrink-0">&#9670; MITIGATED BY ROUTE / SELECTIVITY</span>';
  if(st==='GATE') return '<span class="px-2 py-0.5 rounded font-mono font-semibold text-[var(--warning)] border border-[var(--warning)] text-xs shrink-0">&#9651; PRECLINICAL GATE REQUIRED</span>';
  return '<span class="px-2 py-0.5 rounded font-mono font-bold text-[var(--error)] border border-[var(--error)] text-xs shrink-0">&#9888; CLINICAL / PK LIMITATION</span>';
}
function certBadge(cert){
  const c = String(cert || 'Level 2 · Human Cohort / PK-PD');
  const col = c.startsWith('Level 1') ? 'text-[var(--success)] border-[var(--success)]'
    : (c.startsWith('Level 2') ? 'text-[var(--primary)] border-[var(--primary)]'
    : (c.startsWith('Model') ? 'text-[var(--muted-foreground)] border-dashed border-[var(--border)]' : 'text-[var(--warning)] border-[var(--warning)]'));
  return `<span class="inline-block px-1.5 py-0.5 rounded border font-mono text-xs whitespace-nowrap ${col}">${esc(c)}</span>`;
}

function setDossierSlice(sl){
  dossierSlice = sl || 'ALL';
  if(dossierSlice === 'ALL') dossierLens = 'ALL';
  renderDossierSidebar();
}
function setDossierLens(lk){
  dossierLens = lk || 'ALL';
  renderDossierSidebar();
}
function renderEdgeRibbon(s, cid){
  if(!s || !s.edge_text) return '';
  const k = s.edge_kind || 'HIGH_HURDLE_WATCHLIST';
  const pillCls = k === 'FALSIFIED_TRAP'
    ? 'text-[var(--error)] border-[var(--error)]'
    : (k === 'HIGH_HURDLE_WATCHLIST'
      ? 'text-[var(--warning)] border-[var(--warning)]'
      : 'text-[var(--primary)] border-[var(--primary)]');
  return `<div class="p-2.5 rounded-lg bg-[var(--content)] border border-[var(--card-border)] flex flex-wrap sm:flex-nowrap items-baseline gap-2 text-xs">
    <span class="px-1.5 py-0.5 rounded border font-mono font-semibold shrink-0 whitespace-nowrap ${pillCls}">${esc(s.edge_label)}</span>
    <span class="leading-relaxed text-[var(--foreground)] min-w-0">${escLink(s.edge_text, cid)}</span>
  </div>`;
}
function toggleDossierRail(){
  const a = document.getElementById('d-aside');
  if(!a) return;
  const wasHidden = a.classList.contains ? a.classList.contains('hidden') : false;
  a.classList.toggle('hidden');
  if(wasHidden) a.classList.add('flex','flex-col');
  try {
    document.querySelectorAll('[data-toggle-d-rail]').forEach(b => b.setAttribute('aria-expanded', wasHidden ? 'true' : 'false'));
  } catch(_e) {}
}
function openDossier(id){
  if(!id) return;
  id = String(id).replace(/-N[0-9]+$/, '');
  if(!DATA_PORT.some(x=>x.id===id)) return;
  dossierId = id;
  selectedId = id;
  try {
    if(typeof window !== 'undefined' && window.innerWidth && window.innerWidth < 768){
      const a = document.getElementById('d-aside');
      if(a && a.classList) a.classList.add('hidden');
    }
  } catch(_e) {}
  try {
    if((location.protocol==='http:' || location.protocol==='https:') && location.hash !== '#dossier/'+id){
      history.replaceState(null, '', '#dossier/'+id);
    }
  } catch(_e) {}
  if(activeTab === 'dossiers') renderDossierMain();
  else switchTab('dossiers');
  try { if(typeof window !== 'undefined' && window.scrollTo) window.scrollTo(0, 0); } catch(_e) {}
}

function renderSummaryDomainPanels(r){
  const isFull = (typeof DATA_SUB !== 'undefined');
  let out = '';
  const cisRows = (typeof DATA_CIS !== 'undefined') ? DATA_CIS.filter(c => c.pid === r.id || c.sc === r.id) : [];
  if(cisRows.length){
    const jumpBtn = isFull
      ? `<button type="button" data-jump-intervals="${esc(r.id)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Inspect in Tab 2 (GRCh38 Cis-Intervals) &rarr;</button>`
      : (location.protocol !== 'about:' ? `<a href="../CARBON_ALS_INTERACTIVE_EXPLORER.html#dossier/${esc(r.id)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs">Open in Full Explorer &rarr;</a>` : '');
    out += `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <h3 class="text-sm font-semibold">Audited GRCh38 Cis-Regulatory Intervals (${cisRows.length} Coordinate Walk${cisRows.length>1?'s':''})</h3>
        ${jumpBtn}
      </div>
      <div class="overflow-x-auto"><table class="w-full text-left border-collapse text-xs">
        <thead><tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
          <th class="py-1.5 px-2">Candidate Walk</th><th class="py-1.5 px-2">GRCh38 Coordinate</th><th class="py-1.5 px-2">OTS Splicing Mode</th>
          <th class="py-1.5 px-2" title="Modeled 2'-O-MOE PO/PS Tm, free energy, and max AlphaGenome AVI Phred">Tm / &Delta;G37 / AVI</th><th class="py-1.5 px-2" title="mRNA = spliced 0mm/1mm/wobble genes; pre = pre-mRNA 0mm/1mm(<=50bp)/wobble/2mm(<=25bp)/1nt-bulge/18nt-subcore">mRNA &amp; Pre-mRNA Hits</th><th class="py-1.5 px-2">Safety Verdict &amp; Browsers</th>
        </tr></thead>
        <tbody class="divide-y divide-[var(--card-border)]">${cisRows.map(c => {
          const loP = Math.max(1, Number(c.lo)-250), hiP = Number(c.hi)+250;
          const ensUrl = `https://www.ensembl.org/Homo_sapiens/Location/View?r=${c.chr.replace('chr','')}:${c.lo}-${c.hi}`;
          const atlUrl = `https://deepmind.google.com/science/alphagenome/atlas?q=${c.chr}:${loP}-${hiP}&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE`;
          const ucscUrl = `https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position=${c.chr}:${loP}-${hiP}`;
          const stB = (typeof statusBadge === 'function') ? statusBadge(c.st) : `<span class="font-mono">${esc(humanizeEnum(c.st))}</span>`;
          return `<tr class="align-top">
            <td class="py-2 px-2 font-mono">${c.lead?'<span class="text-[var(--success)] font-bold">&#9733; Lead</span>':'<span class="text-[var(--muted-foreground)]">Alt</span>'} &middot; <strong>${esc(c.gene)} #${c.rk}</strong></td>
            <td class="py-2 px-2 font-mono">${mkExtA(ensUrl, esc(c.iv))} <span class="text-[var(--muted-foreground)]">(${c.len}bp)</span></td>
            <td class="py-2 px-2">${esc(humanizeEnum(c.mode))}</td>
            <td class="py-2 px-2 font-mono tabular-nums">${c.tm}&deg;C &middot; ${c.dg} &middot; AVI=${c.avi}</td>
            <td class="py-2 px-2 font-mono tabular-nums" title="mRNA 0mm/1mm/wobble · pre-mRNA 0mm/1mm(<=50bp)/wobble/2mm(<=25bp)/1nt-bulge/18nt-subcore">mRNA ${c.sp} &middot; pre ${c.pm}</td>
            <td class="py-2 px-2 font-mono whitespace-nowrap">${stB} &middot; ${mkExtA(atlUrl, 'Atlas &nearr;')} &middot; ${mkExtA(ucscUrl, 'UCSC &nearr;')}</td>
          </tr>`;
        }).join('')}</tbody>
      </table></div>
      <div class="text-[var(--muted-foreground)] font-mono text-xs pt-1 border-t border-[var(--card-border)]">Key: mRNA = spliced 0mm/1mm/wobble genes &middot; pre = pre-mRNA 0mm / 1mm(&le;50bp SS) / wobble / 2mm(&le;25bp) / 1-nt bulge / 18-nt sub-core (Coordinate-Only Search Windows, 0 chemically modified synthesis-ready ASO sequences).</div></div>`;
  }
  if(!isFull && location.protocol !== 'about:' && (['C014','C015','C017','C018'].includes(r.id) || /^DN-0[1-9]$/.test(r.id))){
    out += `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 flex items-center justify-between gap-2 flex-wrap text-xs">
      <span class="text-[var(--muted-foreground)]">Interactive single-gene sub-node cards &amp; 3-region NYGC RNA-seq profiles are available in the full 6-tab Explorer.</span>
      <a href="../CARBON_ALS_INTERACTIVE_EXPLORER.html#dossier/${esc(r.id)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono cursor-pointer">Open in Full Explorer &rarr;</a>
    </div>`;
  }
  const subRows = isFull ? DATA_SUB.filter(x => x.par === r.id) : [];
  if(subRows.length){
    out += `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <h3 class="text-sm font-semibold">Unbundled Single-Gene Sub-Nodes (${subRows.length} Genes &middot; NIH IDG TDL &amp; TSA)</h3>
        <button type="button" data-jump-subnodes="${esc(r.id)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Explore Full Cards in Tab 3 &rarr;</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">${subRows.map(sn => {
        const vcol = sn.vraw.startsWith('KEEP')?'text-[var(--warning)] border-[var(--warning)]':(sn.vraw.startsWith('RECLASSIFY')?'text-[var(--primary)] border-[var(--primary)]':'text-[var(--error)] border-[var(--error)]');
        return `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1">
          <div class="flex items-center justify-between gap-1.5 flex-wrap">
            <span class="font-mono font-bold">${esc(sn.id)} &middot; ${esc(sn.gene)}</span>
            <div class="flex items-center gap-1 flex-wrap">${tdlBadge(sn.tdl)}${tsaSubBadge(sn.tsa)}<span class="px-1.5 py-0.5 rounded border font-mono font-semibold ${vcol}">${esc(sn.vlbl)}</span></div>
          </div>
          <div class="text-[var(--muted-foreground)]">${esc(sn.role)}</div>
          <div class="leading-snug">${escLink(sn.gnomad, sn.gene)}</div>
        </div>`;
      }).join('')}</div></div>`;
  }
  if(typeof DATA_NYGC !== 'undefined' && typeof NYGC_GENE_TO_ID !== 'undefined'){
    const gKey = Object.keys(NYGC_GENE_TO_ID).find(g => NYGC_GENE_TO_ID[g] === r.id);
    if(gKey && DATA_NYGC[gKey]){
      const regDefs = [['Spinal_Cord_Cervical','Cervical Cord'],['Spinal_Cord_Lumbar','Lumbar Cord'],['Cortex_Motor','Motor Cortex']];
      out += `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
        <div class="flex items-center justify-between gap-2 flex-wrap">
          <h3 class="text-sm font-semibold">3-Region NYGC Postmortem RNA-Seq Profile &mdash; ${esc(gKey)} (${mkExtA('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE153960','GSE153960')})</h3>
          <button type="button" data-switch-tab="analytics" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Compare 9-Gene Panel in Tab 4 &rarr;</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs">${regDefs.map(([rk, rlbl]) => {
          const d = DATA_NYGC[gKey][rk], m = DATA_NYGC_META[rk];
          const sigNeg = d.b < 0 && d.p < 0.05, sigPos = d.b > 0 && d.p < 0.05;
          const dotCol = sigNeg ? 'var(--primary)' : (sigPos ? 'var(--warning)' : 'var(--muted-foreground)');
          const ptPct = Math.max(4, Math.min(96, ((Math.max(-0.6, Math.min(0.6, d.b)) + 0.6) / 1.2) * 100));
          const sL = Math.min(50, ptPct), sW = Math.max(1, Math.abs(ptPct - 50));
          return `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1 font-mono tabular-nums">
            <div class="flex items-center justify-between"><strong>${rlbl}</strong><span class="text-[var(--muted-foreground)]">N=${m.ntot}</span></div>
            <div>RIN+GC &beta; = <strong>${d.b>=0?'+':''}${d.b.toFixed(3)}</strong> (p=${d.p<0.001?d.p.toExponential(1):d.p.toFixed(3)})</div>
            <div class="relative w-full h-3 rounded bg-[var(--card)] border border-[var(--card-border)] overflow-hidden">
              <div class="absolute top-0 bottom-0 w-px bg-[var(--foreground)] opacity-40" style="left:50%"></div>
              <div class="absolute" style="left:${sL.toFixed(1)}%;width:${sW.toFixed(1)}%;top:5px;height:2px;background:${dotCol}"></div>
              <div class="absolute rounded-full" style="left:${ptPct.toFixed(1)}%;top:2.5px;width:7px;height:7px;margin-left:-3.5px;background:${dotCol}"></div>
            </div>
            <div class="text-[var(--muted-foreground)]">tSTMN2 &beta;=${d.tb>=0?'+':''}${d.tb.toFixed(2)} (p=${d.tp<0.001?d.tp.toExponential(1):d.tp.toFixed(3)}) &middot; Tail ${d.tail.toFixed(2)}%</div>
          </div>`;
        }).join('')}</div></div>`;
    }
  }
  return out;
}

function renderDossierSidebar(){
  const qEl = document.getElementById('d-search');
  const q = qEl ? qEl.value.trim().toLowerCase() : '';
  const sliceDefs = [
    ['ALL', 'All'],
    ['T12', 'T1/2 (8)'],
    ['WATCH', 'T3+Proto (20)'],
    ['BIO', 'Bio (7)'],
    ['DROP', 'Drop (24)'],
  ];
  const sBar = document.getElementById('d-slice-bar');
  if(sBar){
    sBar.innerHTML = sliceDefs.map(([k, lbl]) => {
      const on = dossierSlice === k;
      const cls = on ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)] font-semibold' : 'bg-[var(--background)] text-[var(--muted-foreground)] border-[var(--border)] hover:text-[var(--foreground)]';
      return `<button type="button" data-dossier-slice="${k}" class="px-1.5 py-0.5 rounded border font-mono text-xs cursor-pointer ${cls}">${lbl}</button>`;
    }).join('');
  }
  const dLensSel = document.getElementById('d-lens');
  if(dLensSel && typeof DATA_LENSES !== 'undefined'){
    if(!dLensSel.options.length){
      dLensSel.innerHTML = DATA_LENSES.map(l => `<option value="${esc(l.k)}">${esc(l.lbl)}</option>`).join('');
    }
    dLensSel.value = dossierLens;
  }
  const activeLensObj = (dossierLens !== 'ALL' && typeof DATA_LENSES !== 'undefined') ? DATA_LENSES.find(l => l.k === dossierLens) : null;
  const inSlice = r => {
    if(activeLensObj && !activeLensObj.ids.includes(r.id)) return false;
    if(dossierSlice === 'T12') return r.tier === 'TIER_1_ACTIONABLE_NOW' || r.tier === 'TIER_2_FOCUSED_GATE_FIRST';
    if(dossierSlice === 'WATCH') return r.tier === 'TIER_3_EXPLORATORY_DISCOVERY' || r.tier === 'COMPANION_PROTOCOL_ONLY';
    if(dossierSlice === 'BIO') return r.tier === 'BIOMARKER_BENCHMARK_ONLY';
    if(dossierSlice === 'DROP') return r.tier === 'DROPPED_FALSIFIED_EXCLUDED';
    return true;
  };
  const mkBtn = r => {
    const isPilot = Boolean(DATA_MONOGRAPHS[r.id]);
    const on = r.id === dossierId;
    const dotCol = r.tier==='TIER_1_ACTIONABLE_NOW' ? 'var(--success)'
      : ((r.tier==='TIER_2_FOCUSED_GATE_FIRST' || r.tier==='BIOMARKER_BENCHMARK_ONLY') ? 'var(--primary)'
      : (r.tier==='DROPPED_FALSIFIED_EXCLUDED' ? 'var(--error)' : 'var(--warning)'));
    const cls = on ? 'bg-[var(--content)] border-[var(--primary)] border-l-2 font-semibold text-[var(--foreground)]' : 'bg-[var(--background)] border-[var(--card-border)] hover:bg-[var(--content)]';
    const shortLbl = r.name.split('(')[0].trim();
    const tip = `#${r.rk} ${r.id} — ${r.name} [${isPilot ? 'Full Monograph' : 'Summary Dossier'}]`;
    return `<button type="button" data-open-dossier="${esc(r.id)}" ${on?'aria-current="true"':''} title="${esc(tip)}" class="w-full text-left px-2 py-1 rounded border ${cls} flex items-center justify-between gap-1.5 text-xs cursor-pointer">
      <span class="min-w-0 flex items-center gap-1.5 pointer-events-none">
        <span class="w-1.5 h-1.5 rounded-full shrink-0" style="background:${dotCol}"></span>
        <span class="font-mono text-[var(--muted-foreground)] shrink-0">#${r.rk}</span>
        <span class="font-mono font-semibold shrink-0">${esc(r.id)}</span>
        <span class="truncate text-[var(--muted-foreground)]">${esc(shortLbl)}</span>
      </span>
      ${isPilot?'<span class="px-1 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono text-xs shrink-0 pointer-events-none" title="Full Translational Monograph">M</span>':''}
    </button>`;
  };
  const match = r => {
    const sObj = (typeof DATA_SUM !== 'undefined' && DATA_SUM[r.id]) ? DATA_SUM[r.id] : null;
    const hTxt = sObj ? ((sObj.hyp || '') + ' ' + (sObj.verdict || '') + ' ' + (sObj.edge_text || '')) : '';
    return inSlice(r) && (!q || (r.id+' '+r.name+' '+r.mod+' '+r.tier+' '+r.sub+' '+hTxt).toLowerCase().includes(q));
  };
  const t1 = DATA_PORT.filter(r => r.tier==='TIER_1_ACTIONABLE_NOW' && match(r));
  const t2 = DATA_PORT.filter(r => r.tier==='TIER_2_FOCUSED_GATE_FIRST' && match(r));
  const t3 = DATA_PORT.filter(r => (r.tier==='TIER_3_EXPLORATORY_DISCOVERY' || r.tier==='COMPANION_PROTOCOL_ONLY') && match(r));
  const bm = DATA_PORT.filter(r => r.tier==='BIOMARKER_BENCHMARK_ONLY' && match(r));
  const dr = DATA_PORT.filter(r => r.tier==='DROPPED_FALSIFIED_EXCLUDED' && match(r));
  const totMatched = t1.length + t2.length + t3.length + bm.length + dr.length;
  const cntEl = document.getElementById('d-nav-count');
  if(cntEl) cntEl.textContent = `${totMatched} / ${DATA_PORT.length}`;
  let html = '';
  if(t1.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--success)] font-mono font-semibold text-xs py-0.5">T1 &middot; Actionable (${t1.length})</div>` + t1.map(mkBtn).join('');
  if(t2.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--primary)] font-mono font-semibold text-xs pt-1.5 pb-0.5">T2 &middot; Kill-Gate (${t2.length})</div>` + t2.map(mkBtn).join('');
  if(t3.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--warning)] font-mono font-semibold text-xs pt-1.5 pb-0.5">T3 &middot; Discovery (${t3.length})</div>` + t3.map(mkBtn).join('');
  if(bm.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--primary)] font-mono font-semibold text-xs pt-1.5 pb-0.5">Biomarkers (${bm.length})</div>` + bm.map(mkBtn).join('');
  if(dr.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--error)] font-mono font-semibold text-xs pt-1.5 pb-0.5">Falsified (${dr.length})</div>` + dr.map(mkBtn).join('');
  const nav = document.getElementById('d-nav');
  if(nav) nav.innerHTML = html || '<div class="text-[var(--muted-foreground)] text-xs py-2">No matching dossiers. <button type="button" data-dossier-slice="ALL" class="text-[var(--link)] underline font-mono cursor-pointer">Show all</button></div>';
  const mobSel = document.getElementById('d-mobile-select');
  if(mobSel){
    if(!mobSel.options.length){
      const g1 = DATA_PORT.filter(r => r.tier==='TIER_1_ACTIONABLE_NOW');
      const g2 = DATA_PORT.filter(r => r.tier==='TIER_2_FOCUSED_GATE_FIRST');
      const g3 = DATA_PORT.filter(r => r.tier==='TIER_3_EXPLORATORY_DISCOVERY' || r.tier==='COMPANION_PROTOCOL_ONLY');
      const gB = DATA_PORT.filter(r => r.tier==='BIOMARKER_BENCHMARK_ONLY');
      const gD = DATA_PORT.filter(r => r.tier==='DROPPED_FALSIFIED_EXCLUDED');
      const mkOpt = r => `<option value="${esc(r.id)}">#${r.rk} ${esc(r.id)} — ${esc(r.name.split('(')[0].trim())} ${DATA_MONOGRAPHS[r.id]?'[Monograph]':'[Summary]'}</option>`;
      mobSel.innerHTML = `<optgroup label="Tier 1 · Actionable Leads (${g1.length})">${g1.map(mkOpt).join('')}</optgroup><optgroup label="Tier 2 · Focused Gate (${g2.length})">${g2.map(mkOpt).join('')}</optgroup><optgroup label="Tier 3 & Companion (${g3.length})">${g3.map(mkOpt).join('')}</optgroup><optgroup label="Benchmarks & Fluid Biomarkers (${gB.length})">${gB.map(mkOpt).join('')}</optgroup><optgroup label="Dropped · Scientifically Falsified (${gD.length})">${gD.map(mkOpt).join('')}</optgroup>`;
    }
    mobSel.value = dossierId;
  }
}

function renderDossierMain(){
  renderDossierSidebar();
  try {
    const nav = document.getElementById('d-nav');
    const actBtn = nav && nav.querySelector ? nav.querySelector('[data-open-dossier="'+dossierId+'"]') : null;
    if(actBtn && actBtn.scrollIntoView) actBtn.scrollIntoView({block:'nearest'});
  } catch(_e) {}
  const box = document.getElementById('d-content');
  if(!box) return;
  const r = DATA_PORT.find(x=>x.id===dossierId) || DATA_PORT[0];
  const allIdx = DATA_PORT.findIndex(x=>x.id===r.id);
  const isFullExplorer = (typeof DATA_SUB !== 'undefined');
  const pIdx = MONOGRAPH_ORDER.indexOf(r.id);
  const prevId = (!isFullExplorer && pIdx >= 0) ? MONOGRAPH_ORDER[(pIdx - 1 + MONOGRAPH_ORDER.length) % MONOGRAPH_ORDER.length] : DATA_PORT[(allIdx - 1 + DATA_PORT.length) % DATA_PORT.length].id;
  const nextId = (!isFullExplorer && pIdx >= 0) ? MONOGRAPH_ORDER[(pIdx + 1) % MONOGRAPH_ORDER.length] : DATA_PORT[(allIdx + 1) % DATA_PORT.length].id;
  const prevObj = DATA_PORT.find(x=>x.id===prevId) || r;
  const nextObj = DATA_PORT.find(x=>x.id===nextId) || r;
  const prevLbl = `#${prevObj.rk} ${prevObj.id}`;
  const nextLbl = `#${nextObj.rk} ${nextObj.id}`;
  const mp = document.getElementById('d-mobile-prev'), mn = document.getElementById('d-mobile-next');
  if(mp){ mp.setAttribute('data-open-dossier', prevId); mp.textContent = '\u2190 ' + prevLbl; }
  if(mn){ mn.setAttribute('data-open-dossier', nextId); mn.textContent = nextLbl + ' \u2192'; }

  const w = DATA_MONOGRAPHS[r.id];
  const s = (typeof DATA_SUM !== 'undefined' && DATA_SUM[r.id]) ? DATA_SUM[r.id] : null;
  const evRows = DATA_EV[r.id] || [];
  const evTable = evRows.length ? `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
    <div class="flex items-center justify-between gap-2 flex-wrap">
      <h3 class="text-sm font-semibold">Primary Evidence &amp; FAIR Provenance Ledger (${evRows.length} Atomic Contrasts)</h3>
      <span class="font-mono text-xs text-[var(--muted-foreground)]">W3C PROV &middot; 4-Level Evidence Design &amp; Source Locator Ledger</span>
    </div>
    <div class="text-xs text-[var(--muted-foreground)] font-mono leading-relaxed pb-1 border-b border-[var(--card-border)]">
      <strong class="text-[var(--foreground)]">Design Tiers:</strong> <span class="text-[var(--success)]">Level 1</span> = Human ALS Genetics / Powered RCT &middot; <span class="text-[var(--primary)]">Level 2</span> = Human Cohort (N&ge;15) / PK-PD &middot; <span class="text-[var(--warning)]">Level 3</span> = In Vitro / 3D / Small-N (&lt;15) &middot; <span>Model / Heuristic Prior</span> = Biophysical / Cis-Scan Simulation.
    </div>
    <div class="overflow-x-auto"><table class="w-full text-left border-collapse text-xs">
      <thead><tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
        <th class="py-1.5 px-2">Primary Source &amp; Accessions</th><th class="py-1.5 px-2">Basis &amp; Evidence Design Tier</th>
        <th class="py-1.5 px-2">Cohort &amp; Case/Control N</th><th class="py-1.5 px-2">Assay &amp; Adjusted Contrast</th>
        <th class="py-1.5 px-2">Effect Estimate</th><th class="py-1.5 px-2">p / Adjusted FDR</th>
      </tr></thead>
      <tbody class="divide-y divide-[var(--card-border)]">${evRows.map(e=>{
        const gCtx = e.gene || r.id;
        const gPill = e.gene ? `<span class="inline-block px-1.5 py-0.5 rounded bg-[var(--background)] border border-[var(--primary)] text-[var(--primary)] font-mono font-bold mr-1.5">${esc(e.gene)}</span>` : '';
        const rolePill = e.role ? `<span class="px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] font-mono text-xs whitespace-nowrap">${esc(e.role)}</span>` : '';
        const nLine = e.n ? `<div class="font-mono font-semibold text-[var(--foreground)] mt-0.5">n=${esc(e.n)}${e.nsub?` <span class="font-normal text-[var(--muted-foreground)]">(${esc(e.nsub)})</span>`:''}</div>`
          : (e.nsub ? `<div class="font-mono text-[var(--muted-foreground)] mt-0.5">${esc(e.nsub)}</div>` : '');
        const provTip = `W3C PROV: ${esc(e.eid)} · ${esc(e.run)}${e.sha64 ? ' · sha256:' + esc(e.sha64) : (e.sha ? ' · sha256:' + esc(e.sha) : '')}`;
        const repHref = '../CARBON_ALS_INTERACTIVE_EXPLORER.html#replication' + (e.run ? '/' + encodeURIComponent(e.run) : '');
        const runChip = e.run
          ? (isFullExplorer
            ? `<button type="button" data-open-rep-run="${esc(e.run)}" class="text-[var(--link)] hover:underline font-mono text-xs cursor-pointer" title="${provTip}">Verify in Tab 6 &rarr;</button>`
            : (location.protocol !== 'about:' ? `<a href="${repHref}" class="text-[var(--link)] hover:underline font-mono text-xs" title="${provTip}">Verify in Tab 6 &rarr;</a>` : ''))
          : '';
        const shaChip = (isFullExplorer && e.sha64) ? ` &middot; <button type="button" data-copy-sha="${esc(e.sha64)}" class="text-[var(--muted-foreground)] hover:text-[var(--foreground)] font-mono text-xs cursor-pointer" title="Click to copy 64-char SHA-256: ${esc(e.sha64)}">Copy SHA</button>` : '';
        return `<tr class="align-top" title="${provTip}">
          <td class="py-2 px-2"><div class="font-semibold text-[var(--foreground)]">${esc(e.src)}</div>${e.accs?`<div class="font-mono text-xs mt-0.5">${escLink(e.accs, gCtx)}</div>`:''}</td>
          <td class="py-2 px-2"><div class="text-[var(--foreground)] mb-1">${esc(e.basis)}</div><div class="flex items-center gap-1 flex-wrap">${certBadge(e.cert)}${rolePill}</div>${runChip?`<div class="font-mono text-xs text-[var(--muted-foreground)] mt-0.5">${runChip}${shaChip}</div>`:''}</td>
          <td class="py-2 px-2"><div>${escLink(e.coh, gCtx)}</div>${nLine}</td>
          <td class="py-2 px-2 text-[var(--muted-foreground)]">${gPill}${escLink(e.con, gCtx)}</td>
          <td class="py-2 px-2 font-mono">${escLink(e.est, gCtx)}</td>
          <td class="py-2 px-2 font-mono whitespace-nowrap">${esc(e.pf || '—')}</td>
        </tr>`;
      }).join('')}</tbody>
    </table></div></div>` : '';

  if(!w){
    const isDrop = r.dec === 'DROP';
    const isBench = r.dec === 'RECLASSIFY_BENCHMARK_OR_BIOMARKER';
    const vCol = isDrop ? 'border-l-[var(--error)]' : (isBench ? 'border-l-[var(--primary)]' : 'border-l-[var(--warning)]');
    const vTxt = isDrop ? `text-[var(--error)]` : (isBench ? `text-[var(--primary)]` : `text-[var(--warning)]`);
    const vHdr = isDrop ? `ADJUDICATION RATIONALE &mdash; DROP &middot; ${esc(humanizeEnum(r.epi)).toUpperCase()}`
      : (isBench ? 'ADJUDICATION RATIONALE &mdash; CLINICAL BENCHMARK / FLUID STAGING BIOMARKER' : 'ADJUDICATION RATIONALE &mdash; KEEP &middot; EXPLORATORY (UNPROVEN &ne; DROP)');
    const hCell = isDrop
      ? `<div class="text-[var(--muted-foreground)] font-mono">Positive Falsification Gate</div><div class="font-semibold text-[var(--error)] mt-0.5">${esc(humanizeEnum(r.epi))}</div><div class="text-[var(--muted-foreground)] mt-0.5">Excluded by positive counterevidence under Epistemic Asymmetry.</div>`
      : `<div class="text-[var(--muted-foreground)] font-mono">Active Hurdles (${r.hcnt})</div><div class="flex flex-wrap gap-1 mt-1">${r.hurdles && r.hurdles !== 'NONE' ? r.hurdles.split(';').map(h=>`<span class="px-1.5 py-0.5 rounded border border-[var(--border)] text-xs">${esc(formatHurdle(h))}</span>`).join('') : '<span class="text-[var(--muted-foreground)]">None (Calibration / Biomarker)</span>'}</div>`;
    const crowdPill = (r.crowd && !r.crowd.startsWith('N/A')) ? `<span class="px-2 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">${esc(r.crowd)}</span>` : '';
    const sumPriorLine = (r.prior && r.prior !== 'NONE')
      ? `<div class="mt-0.5"><span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] font-mono">&#9671; [MODEL_PRIOR]</span> <span class="text-[var(--muted-foreground)]">${esc(formatPrior(r.prior))}</span></div>`
      : `<div class="mt-0.5"><span class="px-1 rounded border border-[var(--success)] text-[var(--success)] font-mono">&#9679; [MEASURED]</span> <span class="text-[var(--muted-foreground)]">${esc(formatPrior(r.prior))}</span></div>`;
    const gPills = genePortalPills(r.id);
    const rightCol = isDrop
      ? `<div class="p-3.5 rounded-lg border border-[var(--card-border)] bg-[var(--background)] border-l-4 border-l-[var(--error)] space-y-1.5 text-xs">
          <div class="font-mono font-bold text-[var(--error)]">&#10005; DECISIVE FALSIFYING COUNTEREVIDENCE</div>
          <p class="leading-relaxed text-[var(--foreground)]">${escLink(s ? s.disproves : humanizeEnum(r.epi), r.id)}</p>
        </div>`
      : `<div class="p-3.5 rounded-lg border border-[var(--card-border)] bg-[var(--background)] border-l-4 border-l-[var(--warning)] space-y-1.5 text-xs">
          <div class="font-mono font-bold text-[var(--warning)]">&#9651; TRANSLATIONAL CAVEATS &amp; NEXT DISCRIMINATING GATE</div>
          <p class="leading-relaxed text-[var(--foreground)]">${escLink(s ? s.disproves : '', r.id)}</p>
          <div class="pt-1.5 mt-1 border-t border-[var(--card-border)] leading-relaxed"><strong class="font-mono text-[var(--foreground)]">Discriminating Next Test:</strong> ${formatNextTest(r.nxt, r.id)}</div>
        </div>`;
    box.innerHTML = `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
      <div class="flex items-start justify-between gap-2 flex-wrap border-b border-[var(--card-border)] pb-3">
        <div>
          <div class="flex items-center gap-2 flex-wrap"><span class="px-2 py-0.5 rounded bg-[var(--background)] border border-[var(--border)] font-mono font-bold text-xs" title="Portfolio Actionability Rank #${r.rk}/59 · Pure Biological Evidence Rank #${r.brk}/59">Rank #${r.rk}/59 (Bio #${r.brk}) &middot; ${esc(r.id)}</span> ${decBadge(r.dec)} <span class="px-2 py-0.5 rounded border border-[var(--border)] font-medium text-xs">${esc(humanizeEnum(r.tier))}</span> ${crowdPill}</div>
          <h2 class="text-base font-bold mt-1.5">${esc(r.name)} &mdash; <span class="font-normal text-[var(--muted-foreground)]">${escLink(s ? s.sub : humanizeEnum(r.sub), r.id)}</span></h2>
          <div class="text-xs font-mono text-[var(--muted-foreground)] mt-0.5">${!isDrop && r.trl !== 'PROTOCOL_COMPANION_NA' ? esc(humanizeEnum(r.trl)) + ' &middot; ' : ''}${esc(humanizeEnum(r.basis))}${gPills?' &middot; '+gPills:''}</div>
        </div>
        <div class="flex items-center gap-1.5 flex-wrap shrink-0">
          <span class="px-2 py-1 rounded border border-[var(--border)] bg-[var(--background)] text-[var(--muted-foreground)] font-mono text-xs">Summary-of-Findings Dossier</span>
          <button type="button" data-open-dossier="${prevId}" class="inline-block px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs cursor-pointer" title="Previous candidate ([ key)">&larr; ${esc(prevLbl)}</button>
          <button type="button" data-open-dossier="${nextId}" class="inline-block px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs cursor-pointer" title="Next candidate (] key)">${esc(nextLbl)} &rarr;</button>
        </div>
      </div>
      ${renderEdgeRibbon(s, r.id)}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
        <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--primary)] space-y-1">
          <div class="font-mono font-bold text-[var(--primary)]">CANDIDATE &amp; BIOLOGICAL HYPOTHESIS</div>
          <p class="leading-relaxed text-[var(--foreground)]">${escLink(s ? s.hyp : '', r.id)}</p>
        </div>
        <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 ${vCol} space-y-1">
          <div class="font-mono font-bold ${vTxt}">${vHdr}</div>
          <p class="leading-relaxed text-[var(--foreground)]">${escLink(s ? s.verdict : '', r.id)}</p>
        </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-2.5 text-xs">
        <div class="p-2.5 rounded border border-[var(--card-border)] bg-[var(--background)] space-y-0.5"><div class="text-[var(--muted-foreground)] font-mono">Target Modality (TPP)</div><div class="font-medium leading-snug">${escLink(formatModality(r.mod), r.id)}</div></div>
        <div class="p-2.5 rounded border border-[var(--card-border)] bg-[var(--background)] space-y-0.5"><div class="text-[var(--muted-foreground)] font-mono">Causal vs. Reactive Sign</div><div class="font-medium">${esc(s ? s.causal : humanizeEnum(r.epi))}</div><div class="text-[var(--muted-foreground)]">${esc(humanizeEnum(r.sub))} &middot; Track ${esc(r.trk)}</div></div>
        <div class="p-2.5 rounded border border-[var(--card-border)] bg-[var(--background)] space-y-0.5"><div class="text-[var(--muted-foreground)] font-mono">Experimental Gate &amp; Prior Basis</div><div class="font-mono">${esc(humanizeEnum(r.gate))}</div>${sumPriorLine}</div>
        <div class="p-2.5 rounded border border-[var(--card-border)] bg-[var(--background)]">${hCell}</div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="p-3.5 rounded-lg border border-[var(--card-border)] bg-[var(--background)] border-l-4 ${isDrop?'border-l-[var(--muted-foreground)]':'border-l-[var(--success)]'} space-y-1.5 text-xs">
          <div class="font-mono font-bold ${isDrop?'text-[var(--muted-foreground)]':'text-[var(--success)]'}">${isDrop?'ORIGINATING DISCOVERY / PRECLINICAL SIGNAL':'&#10003; SUPPORTING HUMAN &amp; PRECLINICAL EVIDENCE'}</div>
          <p class="leading-relaxed text-[var(--foreground)]">${escLink(s ? s.proves : '', r.id)}</p>
        </div>
        ${rightCol}
      </div>
    </div>${renderSummaryDomainPanels(r)}${evTable}`;
    return;
  }

  const cisForAtlas = DATA_CIS.filter(c => c.sc===r.id || (r.id==='DN-01'&&c.gene==='ATG4B') || (r.id==='DN-04'&&c.gene==='CELF5'));
  const atlasBtns = cisForAtlas.map(c => {
    const url = `https://deepmind.google.com/science/alphagenome/atlas?q=${c.chr}:${Math.max(1,Number(c.lo)-250)}-${Number(c.hi)+250}&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE`;
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs">${c.lead?'★ ':''}${esc(c.gene)} #${c.rk} Atlas &nearr;</a>`;
  }).join('') + (isFullExplorer && cisForAtlas.length ? `<button type="button" data-jump-intervals="${esc(r.id)}" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Inspect in Tab 2 &rarr;</button>` : (cisForAtlas.length && location.protocol !== 'about:' ? `<a href="../CARBON_ALS_INTERACTIVE_EXPLORER.html#dossier/${esc(r.id)}" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs">Inspect in Full Explorer &rarr;</a>` : ''));
  const hurdleHtml = r.hurdles && r.hurdles !== 'NONE'
    ? r.hurdles.split(';').map(h=>`<div class="leading-snug">&bull; ${esc(formatHurdle(h))}</div>`).join('')
    : '<div class="text-[var(--muted-foreground)]">None</div>';
  const mCol = r.dec === 'KEEP_CORE' ? 'border-l-[var(--success)]' : 'border-l-[var(--warning)]';
  const mTxt = r.dec === 'KEEP_CORE' ? 'text-[var(--success)]' : 'text-[var(--warning)]';
  const mHdr = r.dec === 'KEEP_CORE'
    ? 'ADJUDICATION RATIONALE &mdash; KEEP &middot; CORE'
    : 'ADJUDICATION RATIONALE &mdash; KEEP &middot; EXPLORATORY (UNPROVEN &ne; DROP)';

  box.innerHTML = `
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
      <div class="flex flex-wrap items-start justify-between gap-2 border-b border-[var(--card-border)] pb-3">
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="px-2 py-0.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-bold text-xs" title="Portfolio Actionability Rank #${r.rk}/59 · Pure Biological Evidence Rank #${r.brk}/59">Rank #${r.rk}/59 (Bio #${r.brk}) &middot; ${esc(r.id)}</span>
            ${decBadge(r.dec)}
            <span class="px-2 py-0.5 rounded border border-[var(--border)] font-medium text-xs">${esc(humanizeEnum(r.tier))}</span>
            ${(r.crowd && !r.crowd.startsWith('N/A')) ? `<span class="px-2 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">${esc(r.crowd)}</span>` : ''}
          </div>
          <h2 class="text-base font-bold mt-1.5">${esc(r.name)} &mdash; <span class="font-normal text-[var(--muted-foreground)]">${esc(w.subtitle)}</span></h2>
          <div class="text-xs font-mono text-[var(--muted-foreground)] mt-0.5">${esc(humanizeEnum(r.trl))} &middot; ${esc(humanizeEnum(r.gate))} &middot; ${esc(humanizeEnum(r.basis))}</div>
        </div>
        <div class="flex items-center gap-1.5 flex-wrap shrink-0">
          ${(typeof window !== 'undefined' && window.PUBLIC_WEB_EXPORT && isFullExplorer) ? `<a href="./monographs/${esc(r.id)}.html" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs" title="Open lightweight standalone monograph page">Standalone Page &nearr;</a>` : ''}
          <button type="button" data-open-dossier="${prevId}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs cursor-pointer" title="Previous candidate ([ key)">&larr; ${esc(prevLbl)}</button>
          <button type="button" data-open-dossier="${nextId}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs cursor-pointer" title="Next candidate (] key)">${esc(nextLbl)} &rarr;</button>
        </div>
      </div>
      ${renderEdgeRibbon(s, r.id)}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
        <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--primary)] space-y-1">
          <div class="font-mono font-bold text-[var(--primary)]">CANDIDATE &amp; BIOLOGICAL HYPOTHESIS</div>
          <p class="leading-relaxed text-[var(--foreground)]">${escLink(s && s.hyp ? s.hyp : w.subtitle, r.id)}</p>
        </div>
        <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 ${mCol} space-y-1">
          <div class="font-mono font-bold ${mTxt}">${mHdr}</div>
          <p class="leading-relaxed text-[var(--foreground)]">${escLink(s ? s.verdict : '', r.id)}</p>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
        <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--success)] space-y-1.5 text-xs">
          <div class="font-mono font-bold text-[var(--success)]">&#10003; ADVANCE GATE (GO CRITERIA)</div>
          ${formatGateList(w.verdict_box.pass_gate, r.id, false)}
        </div>
        <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--error)] space-y-1.5 text-xs">
          <div class="font-mono font-bold text-[var(--error)]">&#10005; FALSIFICATION GATE (KILL / NO-GO CRITERIA)</div>
          ${formatGateList(w.verdict_box.kill_gate, r.id, true)}
        </div>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-2">
        ${w.ident.map(([k,v])=>`<div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] text-xs">${esc(k)}</div><div class="font-mono font-semibold text-xs mt-0.5 break-words">${escLink(v, r.id)}</div></div>`).join('')}
      </div>
      <div class="flex flex-wrap items-center justify-between gap-2 pt-1">
        <div class="flex flex-wrap gap-1.5">${w.grades.map(([g,d])=>`<span class="px-2 py-1 rounded bg-[var(--background)] border border-[var(--border)] text-xs"><strong class="text-[var(--primary)]">${esc(g)}:</strong> ${escLink(d, r.id)}</span>`).join('')}</div>
        <div class="flex flex-wrap items-center gap-1.5 text-xs"><span class="text-[var(--muted-foreground)]">Related:</span>${w.related.map(x=>{const rp=DATA_PORT.find(q=>q.id===x); const rShort=x==='C005'?'Excitability PD':(rp?rp.name.replace(/^(?:Low-Dose|Ultrahigh-Dose|Stage-Gated)\\s+/i,'').split(/[\\s(/]/)[0]:''); const rTip=rp?`#${rp.rk} ${rp.id} — ${rp.name}`:x; return `<button type="button" data-open-dossier="${esc(x)}" title="${esc(rTip)}" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-[var(--link)] cursor-pointer">${esc(x)}${rShort?' &middot; '+esc(rShort):''} &rarr;</button>`;}).join('')}</div>
      </div>
    </div>

    <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
      <div class="flex items-center justify-between gap-2 flex-wrap"><h3 class="text-sm font-semibold">Pathogenic Mechanism &amp; Modality Rationale</h3><span class="font-mono text-xs text-[var(--muted-foreground)]">Steps 1&ndash;3: Pathogenic Cascade &rarr; Step 4: Intervention</span></div>
      ${renderCausalGrid(w.causal, r.id)}
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-12 gap-3">
      <div class="xl:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
        <div class="flex items-center justify-between gap-2 flex-wrap"><h3 class="text-sm font-semibold">Multi-Cohort Quantitative Evidence</h3><span class="font-mono text-xs text-[var(--muted-foreground)]">Scale-Separated Tracks &middot; [MEASURED] vs. [MODEL_PRIOR]</span></div>
        ${renderEvidenceMatrix(w.ev_matrix, r.id)}
      </div>
      <div class="xl:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
        <h3 class="text-sm font-semibold">${esc(w.sig_fig.title)}</h3>
        ${renderSignatureSvg(r.id, w.sig_fig)}
        <p class="text-[var(--muted-foreground)] text-xs leading-relaxed">${escLink(w.sig_fig.caption, r.id)}</p>
        ${atlasBtns?`<div class="flex flex-wrap gap-1.5 pt-1">${atlasBtns}</div>`:''}
      </div>
    </div>

    <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
      <h3 class="text-sm font-semibold">5-Axis Target Safety Assessment (TSA) &amp; 3D Structural Profile</h3>
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 items-start">
        <div class="lg:col-span-8 space-y-2">
          ${w.safety.map(([lbl,st,note])=>`<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1 text-xs">
            <div class="flex flex-wrap items-center justify-between gap-2"><span class="font-semibold text-[var(--foreground)]">${esc(lbl)}</span>${riskStateBadge(st)}</div>
            <div class="text-[var(--muted-foreground)] leading-relaxed">${escLink(note, r.id)}</div>
          </div>`).join('')}
        </div>
        <div class="lg:col-span-4 p-3 rounded-lg bg-[var(--background)] border border-[var(--border)] space-y-2 text-xs">
          <div class="font-mono font-bold text-[var(--primary)]">3D Structural &amp; Biophysical Anchor</div>
          <p class="leading-relaxed">${escLink(w.struct_note, r.id)}</p>
          <div class="border-t border-[var(--card-border)] pt-2"><span class="font-semibold text-[var(--muted-foreground)]">Active Hurdles (${r.hcnt}):</span>
          <div class="text-xs mt-1 space-y-1">${hurdleHtml}</div></div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      ${w.sections.map(([st,body])=>{
        const sp = String(st).split(' — ');
        const hdrHtml = sp.length === 2 ? `<span class="font-mono text-xs text-[var(--primary)]">${esc(sp[0])} &mdash;</span> ${esc(sp[1])}` : esc(st);
        const paras = String(body).split(/\\n\\n+/).map(p => `<p class="text-xs leading-relaxed text-[var(--foreground)]">${escLink(p, r.id)}</p>`).join('');
        return `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
          <h3 class="text-sm font-semibold">${hdrHtml}</h3>
          <div class="space-y-2">${paras}</div>
        </div>`;
      }).join('')}
    </div>
    ${evTable}`;
}
"""
