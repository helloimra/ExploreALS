"""Client-side Candidate Dossier & Monograph Standard v3.1 view (5Rs + Open Targets + FAIR / 4-Level Evidence Design Standard)."""
from __future__ import annotations

DOSSIER_JS_VIEW = """
const MONOGRAPH_ORDER = ['EALS-030','EALS-031','EALS-001','EALS-006','EALS-002','EALS-007','EALS-034','EALS-037'];
let dossierId = 'EALS-030';
let dossierSlice = 'ALL';
let dossierLens = 'ALL';

function trackLabel(t){
  if(t === 'A') return 'Clinical Drug / Regimen';
  if(t === 'B') return 'Molecular / Genetic Target';
  if(t === 'BIOMARKER') return 'Fluid Staging Biomarker';
  return 'Candidate Modality';
}

const ENUM_LABELS = {
  TIER_1_ACTIONABLE_NOW: 'Tier 1 · Actionable Now',
  TIER_2_FOCUSED_GATE_FIRST: 'Tier 2 · Validation Gate',
  TIER_3_EXPLORATORY_DISCOVERY: 'Tier 3 · Exploratory Discovery',
  COMPANION_PROTOCOL_ONLY: 'Functional PD Calibrator',
  BIOMARKER_BENCHMARK_ONLY: 'Biomarker / SOC Benchmark',
  DROPPED_FALSIFIED_EXCLUDED: 'Dropped · Falsified',
  PASS_CLEAN_GE2MM: 'Pass · Clean (>=2 Mismatches)',
  CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED: 'Caution · Non-Constrained 1-mm / Wobble / 25bp 2-mm',
  WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL: 'Warn · Constrained CNS 1-mm / Bulge',
  FAIL_EXACT_0MM_OFFTARGET: 'Fail · Exact 0-mm Off-Target',
  TRL_6_PH2B_SUBGROUP_BIOLOGIC: 'Phase 2b Subgroup Biologic',
  TRL_5_HUMAN_ALS_PK_PD_PROVEN: 'Human ALS PK/PD Proven',
  TRL_4_ACTIVE_PH1_CLASS_OR_NCE: 'Active Phase 1 / NCE Class',
  TRL_3_PRECLINICAL_SSO_COORDINATE: 'Preclinical GRCh38 SSO',
  TRL_2_PRECLINICAL_MODALITY_DISCOVERY: 'Preclinical Modality',
  TRL_1_TARGET_TOOL_PROBE_WATCHLIST: 'Target Watchlist / Tool Probe',
  PROTOCOL_COMPANION_NA: 'Biomarker / Calibrator (N/A)',
  MEASURED_HUMAN_GENETICS_AND_PATHOLOGY: 'Human Genetics + CNS Pathology',
  MEASURED_HUMAN_TDP43_PATHOLOGY_AND_RESCUE: 'Human TDP-43 Pathology + Rescue',
  MEASURED_HUMAN_RCT_SUBGROUP: 'Human ALS RCT Subgroup',
  MEASURED_C9FTD_FRACTION_PROTEOMICS: 'Human C9-FTD Fraction Proteomics',
  MEASURED_HUMAN_SPATIAL_OR_SNRNA: 'Human Spatial / snRNA-seq',
  MEASURED_HUMAN_CSF_PROTEOMICS: 'Living Human CSF Proteomics',
  MEASURED_HUMAN_PK_AND_IPSC_SCREEN: 'Human PK / Patient iPSC-MN Screen',
  MEASURED_HUMAN_PK_AND_SAFETY: 'Human PK / Regulatory Safety',
  PROTOCOL_STAGE_GATING_ONLY: 'Clinical Stage-Gating Protocol',
  TARGETED_PRECLINICAL_VALIDATION_GATE: 'Preclinical Cellular / Tissue Validation',
  TRANSLATIONAL_BIOMARKER_OR_PH1B_PKPD_GATE: 'Human Biofluid / Phase 1b PK-PD Study',
  DE_NOVO_CHEMICAL_OR_BIOLOGIC_DISCOVERY_GATE: 'Chemical / Biologic Modality Discovery',
  BIOMARKER_ENRICHED_PHASE3_EFFICACY_TRIAL: 'Biomarker-Enriched Phase 3 Survival RCT',
  CLINICAL_PROTOCOL_STANDARDIZATION: 'Clinical Protocol / Calibration Standard',
  NOT_APPLICABLE_FALSIFIED: 'N/A — Scientifically Falsified',
  GENETICS_MENDELIAN_GWAS: 'Human ALS Genetics — Mendelian & GWAS',
  TDP43_SPLICING_APA: 'TDP-43 Cryptic Splicing & Polyadenylation',
  CNS_TISSUE_OMICS: 'Human CNS Spatial, snRNA & Subcellular Omics',
  CSF_AND_PHYSIOLOGY: 'Living-Patient CSF Proteomics & Physiology',
  CLINICAL_TRIALS_SUBGROUPS: 'Human ALS Clinical Trials & Subgroups',
  IPSC_PHENOTYPIC_SCREEN: 'Patient iPSC-MN Phenotypic Screen',
  CRYPTIC_EXON_SKIP: 'Cryptic Cassette Exon Skipping',
  CRYPTIC_ALE_PAS_BLOCK: "Cryptic 3'SS / Premature PolyA Blockade",
  CONSTITUTIVE_EXON_INCLUSION: 'Constitutive Exon Inclusion Rescue',
  DISTAL_3UTR_EXTENSION: "Distal 3'-UTR Extension Suppression",
  SUPPORTED: 'Supported (Human Genetics + Pathology)',
  UNPROVEN_UNTESTED: 'Untested / Unresolved (Validation Required)',
  ESTABLISHED_BENCHMARK: 'Established SOC / PD Benchmark',
  FALSIFIED_CLINICAL: 'Falsified · Human ALS RCT Futility',
  FALSIFIED_PK_SAFETY: 'Falsified · CNS PK / Safety Wall',
  ARTIFACT_CONFOUNDED: 'Falsified · Assay Confounding',
  KEEP_CORE: 'Keep · Core',
  KEEP_EXPLORATORY_UNPROVEN: 'Keep · Exploratory',
  RECLASSIFY_BENCHMARK_OR_BIOMARKER: 'Benchmark / Biomarker',
  DROP: 'Drop · Falsified',
  SKIP_CRYPTIC_EXON: "Steric 2'-MOE SSO · Cryptic Exon Skip",
  CRYPTIC_EXON2A_3SS_PAS_BLOCK: "Steric 2'-MOE SSO · Proximal Exon-2a (+8..+25) Epistatic 3'SS / PAS Suppression",
  CRYPTIC_CASSETTE_EXON_SKIP: "Steric 2'-MOE SSO · Cryptic Cassette Skip",
  CRYPTIC_CASSETTE_MAJOR_3SS_AND_SHARED_EXON: "Steric 2'-MOE SSO · Major 3'SS + Exonic",
  CRYPTIC_CASSETTE_DOWNSTREAM_INTRONIC_ISE: "Steric 2'-MOE SSO · Downstream Intronic ISE",
  INCLUDE_CONSTITUTIVE_EXON: "Steric 2'-MOE SSO · Putative Intron-5 Site (ISS vs ISE Gate)",
  INCLUDE_EXON_UPSTREAM_UG: "Steric 2'-MOE SSO · Exon-5 Inclusion (UG)",
  CRYPTIC_ALE_3SS_ACCEPTOR_BLOCK: "Steric 2'-MOE SSO · Cryptic ALE 3'SS Block",
  CRYPTIC_A3SS_PROXIMAL_EXON_BLOCK: "Steric 2'-MOE SSO · Cryptic A3SS Exonic Block (+8..+27)",
  CRYPTIC_A3SS_ACCEPTOR_BLOCK: "Steric 2'-MOE SSO · Cryptic A3SS Acceptor Block",
  DISTAL_3UTR_EXT_PAS_WINDOW: "Distal 3'-UTR Extension Window (Steric Distal-PAS SSO or 3'-Ext siRNA)",
  CRYPTIC_3EXT_ISOFORM_GAPMER_WINDOW: "Exploratory 3'-Ext RNase-H Gapmer ASO Window (vs. Steric PAS / 3'-Ext siRNA Gate)",
  MULTIPLEX_CORE: 'Multiplex Core',
  SINGLE_LOCUS_LEAD: 'Single-Locus Lead',
  EXPLORATORY_LOCUS: 'Exploratory Locus',
  EXCLUDED_ALU_REPEAT: 'Excluded (Alu Repeat)',
  NONE_FALSIFIED_CLINICAL: 'None — Falsified in human ALS clinical trials.',
  NONE_FALSIFIED_PK_SAFETY: 'None — Falsified by insurmountable human CNS PK deficit or clinical toxicity.',
  NONE_ARTIFACT_CONFOUNDED: 'None — Assay perturbation sits within basal media noise and contradicts human genetic polarity.',
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
  LEMD2:'LEMD2', ANXA11:'ANXA11', SUN1:'SUN1', CHMP7:'CHMP7', NEFH:'NEFH', BSN:'BSN', APP:'APP',
  SOD1:'SOD1', G93A:'G93A', KO:'KO', WT:'WT', SCFD1:'SCFD1', G2E3:'G2E3', YKT6:'YKT6', CYS195:'Cys195', Y64C:'Y64C',
  ALU:'Alu', EQTL:'eQTL', INTRON1:'Intron-1', '0MM':'0mm', CRISPRI:'CRISPRi', CRISPRA:'CRISPRa',
  PFKM:'PFKM', PFKL:'PFKL', SRF:'SRF', IFN:'IFN', ISGS:'ISGs', UG8:'UG8', CADPR:'cADPR', NFL:'NfL', PNFH:'pNfH',
  KPUU:'Kp,uu', IPSC:'iPSC', TLOCK:'T-Lock', GOF:'GoF', LOF:'LoF', TDP43:'TDP-43', TSTMN2:'tSTMN2', SST2:'sST2',
  PSTAT:'pSTAT', PSTAT2:'pSTAT2', PSTAT3:'pSTAT3', DISIRNA:'di-siRNA', QPCR:'qPCR', DDPCR:'ddPCR', PH1B:'Ph1b',
  PH3:'Ph3', CA2:'Ca2+', '2FE2S':'[2Fe-2S]', QRL201:'QRL-201', TPN101:'TPN-101', ORF1P:'ORF1p', '3SS':"3'SS",
  '5SS':"5'SS", C5AR1:'C5aR1', CTAIL:'C-tail', LT1PCT:'<1%', '34PCT':'34%', '36PCT':'36%',
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
  ICH:'ICH', M3R2:'M3(R2)', FCRN:'FcRn', CD38:'CD38', IMGL:'iMGL', CONQUR:'CONQUR',
  IL33:'IL-33', CTRL:'control', EXON5:'Exon-5', INTRON5:'Intron-5', POPS:'PO/PS',
  EXON2A:'Exon-2a', INTRON8:'Intron-8', INTRON4:'Intron-4',
  IPA:'IPA', '3UTR':"3'-UTR", '952BP':'952-bp', N3:'n=3', HEALEY:'HEALEY', N42:'N=42', N55:'N=55',
  QD:'QD', BID:'BID', DPR:'DPR', ALSTDP:'ALS-TDP', RMT:'RMT', EP09C:'EP09c', CLSI:'CLSI', TT:'TT',
  '3V5Z':'3V5Z', '6C1R':'6C1R', SITE2:'Site-2', NCT03293069:'NCT03293069', NCT04993755:'NCT04993755',
  ACTRN12622000927729:'ACTRN12622000927729', PMX205:'PMX 205', RS138273846:'rs138273846',
  MS2:'MS2', TMTPRO:'TMTpro', PSER3:'pSer3', CFL1:'CFL1', DPP6:'DPP6', DPP10:'DPP10',
  RBC:'RBC', WBC:'WBC', LP:'LP', QC:'QC', RS3831317:'rs3831317', AD:'AD',
  SPHINGOLIPID:'sphingolipid', SCREENING:'screening', SAFEGUARD:'safeguard', SPTLC1:'SPTLC1', SPTLC2:'SPTLC2',
};
function humanizeEnum(s){
  if(!s || s === 'NONE') return 'None';
  if(ENUM_LABELS[s]) return ENUM_LABELS[s];
  return String(s).replace(/_/g, ' ');
}
function formatHurdle(code){
  if(!code || code === 'NONE') return 'None';
  const pre = String(code)
    .replace(/FACTORIAL_CONTRIBUTION/g, 'factorial contribution')
    .replace(/ICH_M3R2/g, 'ICH M3(R2)')
    .replace(/INDEPENDENT_SINGLE_ENTITY_TOX/g, 'independent single-entity tox qualification')
    .replace(/6_TO_9MG/g, '6–9 mg')
    .replace(/LE_3MG/g, '<=3 mg')
    .replace(/LE_5_5PCT/g, '<=5.5%')
    .replace(/24_TO_48MG/g, '24–48 mg')
    .replace(/PH2_3/g, 'Ph2/3')
    .replace(/PH1A_1B/g, 'Ph1a/1b')
    .replace(/6VS6/g, '6 vs 6')
    .replace(/5VS4/g, '5 vs 4')
    .replace(/1VS2/g, '1 vs 2')
    .replace(/FE_O_FE/g, '[Fe-O-Fe]')
    .replace(/TPN101_TP/g, 'TPN-101-TP')
    .replace(/FAIRPARK_II/g, 'FAIRPARK-II')
    .replace(/PMID_37317638/g, 'PMID:37317638')
    .replace(/KP_UU/g, 'Kp,uu')
    .replace(/GT99_9PCT/g, '>99.9%')
    .replace(/LT0_1PCT/g, '<0.1%')
    .replace(/PLUS0048/g, '+0.048')
    .replace(/MINUS022_TO_033/g, '-0.22 to -0.33')
    .replace(/8_7PCT/g, '8.7%')
    .replace(/LE_3700/g, '<=3,700')
    .replace(/PLI_0_996/g, 'pLI=0.996')
    .replace(/CHRONOS_MINUS1_54/g, 'Chronos=-1.54')
    .replace(/CHRONOS_MINUS1_26/g, 'Chronos=-1.26')
    .replace(/NON_ORTHOSTERIC/g, 'non-orthosteric')
    .replace(/NON_C9/g, 'non-C9')
    .replace(/PRE_PH3/g, 'Pre-Ph3')
    .replace(/POST_QRL201/g, 'Post-QRL-201')
    .replace(/ALS_GLIA/g, 'ALS-Glia')
    .replace(/AA324_328/g, 'aa 324-328 SKECF')
    .replace(/Q48_TO_Q72H/g, 'q48h-q72h');
  const words = pre.split('_').filter(Boolean).map(w => {
    if(HURDLE_TOK[w]) return HURDLE_TOK[w];
    if(/^(#|<=|>=|<|>|-0\\.|[0-9]|EALS-|pLI=|Chronos=|factorial|ICH|independent|Pre-|Post-|ALS-|non-|aa |\\[Fe)/.test(w)) return w;
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
    .replace(/Pgp_BCRP_effluxed_Kpuu_le_1_unbound_human_CNS_peak_15_to_30nM_from_NDA020599_Cu_plasma_22\\.2_to_29\\.6nM/g, 'P-gp/BCRP-effluxed Kp,uu <= 1.0 unbound human CNS peak (~15–30 nM, <=50 nM) from NDA 020599 Cu,plasma (22.2–29.6 nM)')
    .replace(/Modeled_Kpuu_0\\.65_on_FDA_fup_0\\.05_to_0\\.11/g, 'Modeled Kp,uu ~ 0.65 on FDA fu,p = 0.05–0.11 (~120–280 nM Cu,brain vs 20–40 uM ISR)')
    .replace(/OAT3_MRP4_efflux_Kpuu_lt_0\\.05_on_NDA016273_fup/g, 'OAT3/MRP4 anionic BBB efflux (Kp,uu < 0.05) on NDA 016273 fu,p (~1–5 nM Cu,CNS)')
    .replace(/Modeled_fup_and_Kpuu_beyond_measured_35\\.2_to_61\\.0nM_total_plasma_Cmax/g, 'Modeled fu,p & Kp,uu (~5–20 nM Cu,brain) beyond measured 35.2–61.0 nM total plasma Cmax')
    .replace(/Anionic_MPA_efflux_Kpuu_on_NDA050722_fup_0\\.03/g, 'OAT3/MRP anionic MPA efflux Kp,uu on NDA 050722 fu,p = 0.03 (~15–55 nM Cu,brain)')
    .replace(/Passive_Kpuu_le_1_and_CAD_lysosomal_partitioning_on_NDA021807_fup/g, 'Passive Kp,uu <= 1.0 & CAD lipid partitioning on NDA 021807 fu,p (~3–15 nM combined free CNS)')
    .replace(/Pgp_attenuated_Kpuu_on_NDA213969_fup_le_0\\.01/g, 'P-gp-attenuated Kp,uu on NDA 213969 fu,p <= 0.01 (~2–13 nM Cu,brain)')
    .replace(/8mer_MWC_1x_parallel_Bliss_to_2_to_7x_epistatic_bounds/g, '8-mer MWC (1.0x parallel Bliss to ~2–7x epistatic bounds)')
    .replace(/1x_parallel_Bliss_to_2_to_7x_MWC_SARM1_bounds/g, '1.0x parallel Bliss to ~2–7x MWC SARM1 bounds')
    .replace(/Bifurcated_PKPD_ODE_79_to_30_to_0pct_coupled_PI3P_LRRK2_CASM/g, 'Bifurcated PK/PD ODE (~79% dead-zone -> ~30% matched -> 0% slow coupled +PI(3)P->LRRK2/CASM)')
    .replace(/Bifurcated_PKPD_ODE_79pct_osmotic_deadzone_vs_0pct_coupled_PI3P_LRRK2_CASM/g, 'Bifurcated PK/PD ODE (~79% osmotic dead-zone vs ~30%/0% coupled +PI(3)P->LRRK2/CASM)')
    .replace(/8mer_MWC_order_of_magnitude_2_to_7x/g, '8-mer MWC order-of-magnitude (~2–7x)')
    .replace(/Tm_dG37_AVI_2Z0D_contacts/g, 'SantaLucia Tm, ΔG37, AlphaGenome AVI & PDB 2Z0D contacts')
    .replace(/Tm_dG37_AVI_composite_score/g, 'SantaLucia Tm, ΔG37 & AlphaGenome AVI composite score')
    .replace(/79_to_30_to_0pct/g, '~79% -> ~30% -> 0%')
    .replace(/Operationalized_MIROCALS_p79_bridging_Schoenfeld_HR070_and_platform_offset_sensitivity/g, 'Operationalized MIROCALS ~79th-pct CLSI EP09c bridging, Schoenfeld HR = 0.70 & platform-offset sensitivity')
    .replace(/30_to_40pct/g, '~30–40%')
    .replace(/45_to_50pct/g, '~45–50%')
    .replace(/Post_hoc/g, 'Post-hoc')
    .replace(/8_7pct/g, '8.7%')
    .replace(/35_to_50pct/g, '35–50%')
    .replace(/2_to_7x/g, '~2–7x')
    .replace(/minus85A3/g, '-85 Å³')
    .replace(/plus85A3/g, '+85 Å³')
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
    .replace(/^Dropped_Confounded_Postmortem_Transcriptomic_Target_/, 'Dropped (Assay-Confounded Screen Hit): ')
    .replace(/2OMOE/g, "2'-O-MOE").replace(/POPS/g, 'PO/PS').replace(/TLock/g, 'T-Lock').replace(/72mg/g, '72 mg')
    .replace(/ARM_TIR/g, 'ARM-TIR').replace(/ASHA624/g, 'ASHA-624').replace(/NaV1_6/g, 'NaV1.6')
    .replace(/Kv7_2_7_3/g, 'Kv7.2/7.3').replace(/Half_Life_Extended/g, 'Half-Life-Extended')
    .replace(/ECM_Anchored/g, 'ECM-Anchored').replace(/Anti_C1q/g, 'Anti-C1q')
    .replace(/Allele_Specific/g, 'Allele-Specific').replace(/Neuron_Selective/g, 'Neuron-Selective')
    .replace(/Non_Covalent/g, 'Non-Covalent').replace(/Non_Orthosteric/g, 'Non-Orthosteric').replace(/Non_Chelating/g, 'Non-Chelating')
    .replace(/CTail_aa324_328/g, 'C-Tail (aa 324–328 SKECF)').replace(/Intron8/g, 'Intron-8').replace(/Intron9/g, 'Intron-9')
    .replace(/ERAD_Sparing/g, 'ERAD-Sparing')
    .replace(/Early_Onset_LE12m/g, 'Early-Onset (<=12m)').replace(/Q48_to_Q72h/g, 'q48h–q72h')
    .replace(/LINE1_RT/g, 'LINE-1 RT').replace(/TPN101/g, 'TPN-101').replace(/JAK2_Sparing/g, 'JAK2-Sparing')
    .replace(/ldIL2/g, 'ld-IL-2').replace(/CTLA4Ig/g, 'CTLA4-Ig').replace(/IL2/g, 'IL-2').replace(/ALSFRSR/g, 'ALSFRS-R').replace(/N137/g, 'N=137').replace(/24wk/g, '24-wk')
    .replace(/Brain_Penetrant/g, 'Brain-Penetrant').replace(/Low_Dose/g, 'Low-Dose')
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
function ensurePeriod(c){
  const t = String(c || '').trim();
  return (!t || /[.!?:]$/.test(t)) ? t : (t + '.');
}
function topDepths(s){
  const dp = new Array(s.length).fill(0);
  let d = 0;
  for(let i = 0; i < s.length; i++){
    const ch = s[i];
    if(ch === '(' || ch === '[') d++;
    dp[i] = d;
    if((ch === ')' || ch === ']') && d > 0) d--;
  }
  return dp;
}
function formatBulletBody(rawBody, ctx){
  const body = ensurePeriod(capClause(rawBody));
  const linked = escLink(body, ctx);
  const cm = /^([^:<()]{2,34}:)\\s+([\\s\\S]+)$/.exec(linked);
  return cm ? `<strong class="font-semibold text-[var(--foreground)]">${cm[1]}</strong> ${cm[2]}` : linked;
}
function formatProseParas(raw, ctx, gapCls='space-y-2', toneCls='text-[var(--foreground)]'){
  const txt = String(raw || '').trim();
  if(!txt) return '';
  const htmlBlocks = [];
  for(const blk of txt.split(/\\n\\n+/)){
    const b = blk.trim();
    if(!b) continue;
    if(/^\\(1\\)\\s/.test(b) && b.includes('(2) ')){
      const items = splitTopClauses(b, /[;,]\\s+(?:and\\s+)?(?=\\([2-9]\\)\\s)/);
      htmlBlocks.push(`<ul class="space-y-1.5 pl-0.5">${items.map(it => {
        const m = /^\\(([0-9]+)\\)\\s*(.+)$/.exec(it.trim());
        const num = m ? m[1] : '&bull;';
        const rawBody = m ? m[2] : it;
        return `<li class="flex items-baseline gap-1.5"><span class="font-mono font-semibold text-[var(--primary)] shrink-0">(${num})</span><span class="min-w-0 break-words">${formatBulletBody(rawBody, ctx)}</span></li>`;
      }).join('')}</ul>`);
      continue;
    }
    const dp0 = topDepths(b);
    let enumColon = -1;
    for(let i = 15; i < b.length - 20; i++){
      if(b[i] === ':' && dp0[i] === 0 && /^:\\s+\\(1\\)\\s/.test(b.slice(i)) && b.slice(i).includes('(2) ')){
        enumColon = i; break;
      }
    }
    if(enumColon > 0){
      const intro = b.slice(0, enumColon + 1).trim();
      const rest = b.slice(enumColon + 1).trim();
      const items = splitTopClauses(rest, /[;,]\\s+(?:and\\s+)?(?=\\([2-9]\\)\\s)/);
      let postNote = '';
      if(items.length >= 2){
        const lastIt = items[items.length - 1];
        const dpL = topDepths(lastIt);
        for(let i = 30; i < lastIt.length - 55; i++){
          if(lastIt[i] === '.' && dpL[i] === 0 && /^\\s+[A-Z]/.test(lastIt.slice(i + 1)) && !/\\b(?:et\\s+al|vs|v|e\\.g|i\\.e|incl|cf|Fig|Figs|[A-Z])$/.test(lastIt.slice(0, i))){
            postNote = lastIt.slice(i + 1).trim();
            items[items.length - 1] = lastIt.slice(0, i + 1).trim();
            break;
          }
        }
      }
      htmlBlocks.push(`<p class="break-words">${escLink(intro, ctx)}</p>`);
      htmlBlocks.push(`<ul class="space-y-1.5 pl-1">${items.map(it => {
        const m = /^\\(([0-9]+)\\)\\s*(.+)$/.exec(it.trim());
        const num = m ? m[1] : '&bull;';
        const rawBody = m ? m[2] : it;
        return `<li class="flex items-baseline gap-1.5"><span class="font-mono font-semibold text-[var(--primary)] shrink-0">(${num})</span><span class="min-w-0 break-words">${formatBulletBody(rawBody, ctx)}</span></li>`;
      }).join('')}</ul>`);
      if(postNote) htmlBlocks.push(`<p class="break-words">${escLink(postNote, ctx)}</p>`);
      continue;
    }
    const sents = [];
    let last = 0;
    for(let i = 0; i < b.length; i++){
      if(b[i] === '.' && dp0[i] === 0){
        const rem = b.slice(i + 1);
        const m = /^(\\s+)(?=[A-Z0-9#])/.exec(rem);
        if(m && !/\\b(?:et\\s+al|vs|v|e\\.g|i\\.e|incl|cf|esp|Fig|Figs|Suppl|Ext|Ref|Refs|Eq|Tab|No|ca|approx|Dr|St|Prof|[A-Z])$/.test(b.slice(0, i))){
          const seg = b.slice(last, i + 1).trim();
          if(seg.length >= 65 && rem.trim().length >= 65){
            sents.push(seg);
            last = i + 1 + m[1].length;
          }
        }
      }
    }
    if(b.slice(last).trim()) sents.push(b.slice(last).trim());
    for(const st of sents){
      const semis = st.length >= 220 ? splitTopClauses(st, /;\\s+/) : [st];
      const merged = [];
      for(let idx = 0; idx < semis.length; idx++){
        const sm = semis[idx].trim();
        if(merged.length && (merged[merged.length - 1].length < 80 || sm.length < 80)){
          merged[merged.length - 1] = merged[merged.length - 1].replace(/\\.+$/, '') + '; ' + sm;
        } else {
          merged.push(idx > 0 ? capClause(sm) : sm);
        }
      }
      for(let idx = 0; idx < merged.length; idx++){
        const p = idx < merged.length - 1 ? ensurePeriod(merged[idx]) : merged[idx];
        if(p.length >= 240){
          const dpP = topDepths(p);
          let cIdx = -1;
          for(let k = 24; k <= Math.min(310, p.length - 80); k++){
            if(p[k] === ':' && dpP[k] === 0 && p[k + 1] === ' ' && !/\\b(?:DOI|PMID|CID|OMIM|HGNC|MGI|HR|OR)$/i.test(p.slice(0, k))){ cIdx = k; break; }
          }
          if(cIdx > 0){
            const lead = p.slice(0, cIdx + 1).trim();
            const tail = p.slice(cIdx + 1).trim();
            htmlBlocks.push(`<p class="font-medium break-words">${escLink(lead, ctx)}</p>`);
            htmlBlocks.push(`<p class="break-words">${escLink(capClause(tail), ctx)}</p>`);
            continue;
          }
        }
        htmlBlocks.push(`<p class="break-words">${escLink(p, ctx)}</p>`);
      }
    }
  }
  return `<div class="${gapCls} leading-relaxed text-xs ${toneCls}">${htmlBlocks.join('')}</div>`;
}
function statusBadge(st, c=null){
  if(st==='PASS_CLEAN_GE2MM') return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--success)] border border-[var(--success)] text-xs whitespace-nowrap" title="Zero 0-mm, 1-mm, wobble, bulge, or 18-nt sub-core off-target hits on constrained CNS genes">Pass &middot; Clean (&ge;2mm)</span>';
  if(String(st||'').startsWith('CAUTION')){
    const pts = c && c.sp === '0/0/0' ? String(c.pm || '').split('/') : [];
    const m25 = (pts.length === 6 && pts[0]==='0' && pts[1]==='0' && pts[2]==='0' && /^[1-9][0-9]*$/.test(pts[3]) && pts[4]==='0' && pts[5]==='0') ? [null, pts[3]] : null;
    if(m25) return `<span class="px-1.5 py-0.5 rounded font-mono text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap" title="Zero 0-mm, spliced 1-mm/wobble, <=50bp splice-site 1-mm/wobble, 1-nt bulge, or 18-nt sub-core hits (${c&&c.pm1_all!=null?c.pm1_all:'?'} sense pre-mRNA 1-mm gene(s)); ${m25[1]} non-constrained 25bp-SS 2-mm hit(s) — empirical microwalk required">Caution &middot; 25bp 2-mm (${m25[1]})</span>`;
    return '<span class="px-1.5 py-0.5 rounded font-mono text-[var(--warning)] border border-[var(--warning)] text-xs whitespace-nowrap" title="Non-constrained spliced or <=50bp splice-site 1-mm, wobble, or 25bp-SS 2-mm hit (zero constrained CNS pLI >= 0.9 hits) — empirical microwalk required">Caution &middot; 1-mm/Wob/2-mm</span>';
  }
  if(String(st||'').startsWith('WARN')) return '<span class="px-1.5 py-0.5 rounded font-mono font-semibold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="1-mm, wobble, or 1-nt bulge hit on a LoF-intolerant (pLI >= 0.9) CNS gene">Warn &middot; CNS Hit</span>';
  if(String(st||'').startsWith('FAIL')) return '<span class="px-1.5 py-0.5 rounded font-mono font-bold text-[var(--error)] border border-[var(--error)] text-xs whitespace-nowrap" title="Exact 0-mismatch off-target hybridization hit across GENCODE v46">Fail &middot; 0-mm</span>';
  return '<span class="text-[var(--muted-foreground)] font-mono text-xs">None</span>';
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
function resetDossierNav(){
  const sEl = document.getElementById('d-search');
  if(sEl) sEl.value = '';
  dossierLens = 'ALL';
  setDossierSlice('ALL');
}
function setDossierLens(lk){
  dossierLens = lk || 'ALL';
  renderDossierSidebar();
}
function renderEdgeRibbon(s, cid, compact=false){
  if(!s || !s.edge_text) return '';
  const k = s.edge_kind || 'HIGH_HURDLE_WATCHLIST';
  const pillCls = k === 'FALSIFIED_TRAP'
    ? 'text-[var(--error)] border-[var(--error)]'
    : (k === 'HIGH_HURDLE_WATCHLIST'
      ? 'text-[var(--warning)] border-[var(--warning)]'
      : 'text-[var(--primary)] border-[var(--primary)]');
  const rawTxt = (compact && typeof firstGateSummary === 'function') ? firstGateSummary(s.edge_text, 175) : s.edge_text;
  return `<div class="${compact?'p-2':'p-2.5'} rounded-lg bg-[var(--content)] border border-[var(--card-border)] space-y-1 text-xs">
    <div><span class="inline-block px-1.5 py-0.5 rounded border font-mono font-semibold ${pillCls}">${esc(s.edge_label)}</span></div>
    <div class="leading-snug text-[var(--foreground)]">${escLink(rawTxt, cid)}</div>
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
function openDossier(rawId){
  if(!rawId) return;
  const res = (typeof resolveCandidateId === 'function') ? resolveCandidateId(rawId) : null;
  const id = res ? res.id : String(rawId).replace(/\\.[0-9]+$/, '');
  if(res && res.sub && typeof pendingDossierSec !== 'undefined' && !pendingDossierSec) pendingDossierSec = 'sec-subunits';
  if(!DATA_PORT.some(x=>x.id===id)) return;
  dossierId = id;
  selectedId = id;
  try {
    if(typeof window !== 'undefined' && window.innerWidth && window.innerWidth < 768){
      const a = document.getElementById('d-aside');
      if(a && a.classList) a.classList.add('hidden');
    }
  } catch(_e) {}
  const hasPendSec = (typeof pendingDossierSec !== 'undefined' && Boolean(pendingDossierSec));
  if(activeTab === 'dossiers'){
    renderDossierMain();
    if(typeof commitHistory === 'function') commitHistory('push', '#dossier/' + id);
    if(hasPendSec){
      const secId = pendingDossierSec;
      pendingDossierSec = '';
      setTimeout(() => {
        const secEl = document.getElementById(secId);
        if(secEl && secEl.scrollIntoView) secEl.scrollIntoView({behavior:'smooth', block:'start'});
      }, 30);
      return;
    }
  } else {
    switchTab('dossiers', 'push', '#dossier/' + id);
    if(hasPendSec) return;
  }
  try { if(typeof window !== 'undefined' && window.scrollTo) window.scrollTo(0, 0); } catch(_e) {}
}

function renderSummaryDomainPanels(r){
  const isFull = (typeof DATA_SUB !== 'undefined');
  let out = '';
  const cisRows = (typeof DATA_CIS !== 'undefined') ? DATA_CIS.filter(c => c.pid === r.id || c.sc === r.id) : [];
  if(cisRows.length){
    const jumpBtn = isFull
      ? `<button type="button" data-jump-intervals="${esc(r.id)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Inspect in Tab 3 (Splice Windows) &rarr;</button>`
      : (location.protocol !== 'about:' ? `<a href="../CARBON_ALS_INTERACTIVE_EXPLORER.html#intervals/${esc(r.id)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs">Inspect in Tab 3 (Splice Windows) &rarr;</a>` : '');
    out += `<div id="sec-cis" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <h3 class="text-sm font-semibold">Audited GRCh38 Splice-Target Windows (${cisRows.length} Target Window${cisRows.length>1?'s':''})</h3>
        ${jumpBtn}
      </div>
      <div class="overflow-x-auto"><table class="w-full text-left border-collapse text-xs">
        <thead><tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
          <th class="py-1.5 px-2">Target Window</th><th class="py-1.5 px-2">GRCh38 Coordinate</th><th class="py-1.5 px-2">Cis-Mechanism</th>
          <th class="py-1.5 px-2" title="Modeled 2'-O-MOE PO/PS Tm, free energy, and max AlphaGenome AVI Phred">Tm / &Delta;G37 / AVI</th><th class="py-1.5 px-2" title="mRNA = spliced 0-mm·1-mm·wobble genes; pre = pre-mRNA 0-mm·1-mm(<=50bp)·wobble·2-mm(<=25bp)·1nt-bulge·18nt-subcore">mRNA &amp; Pre-mRNA Hits</th><th class="py-1.5 px-2">Safety Verdict &amp; Browsers</th>
        </tr></thead>
        <tbody class="divide-y divide-[var(--card-border)]">${cisRows.map(c => {
          const loP = Math.max(1, Number(c.lo)-250), hiP = Number(c.hi)+250;
          const ensUrl = `https://www.ensembl.org/Homo_sapiens/Location/View?r=${c.chr.replace('chr','')}:${c.lo}-${c.hi}`;
          const atlUrl = `https://deepmind.google.com/science/alphagenome/atlas?q=${c.chr}:${loP}-${hiP}&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE`;
          const ucscUrl = `https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position=${c.chr}:${loP}-${hiP}`;
          const stB = (typeof statusBadge === 'function') ? statusBadge(c.st, c) : `<span class="font-mono">${esc(humanizeEnum(c.st))}</span>`;
          return `<tr class="align-top">
            <td class="py-2 px-2 font-mono">${c.lead?'<span class="text-[var(--success)] font-bold">&#9733; Lead</span>':'<span class="text-[var(--muted-foreground)]">Alt</span>'} &middot; <strong>${esc(c.gene)} &middot; Window #${c.rk}</strong></td>
            <td class="py-2 px-2 font-mono">${mkExtA(ensUrl, esc(c.iv))} <span class="text-[var(--muted-foreground)]">(${c.len}bp)</span></td>
            <td class="py-2 px-2">${esc(humanizeEnum(c.mode))}</td>
            <td class="py-2 px-2 font-mono tabular-nums">${c.tm}&deg;C &middot; ${c.dg} &middot; AVI=${c.avi}</td>
            <td class="py-2 px-2 font-mono tabular-nums" title="mRNA 0-mm·1-mm·wobble · pre-mRNA 0-mm·1-mm(<=50bp)·wobble·2-mm(<=25bp)·1nt-bulge·18nt-subcore">mRNA ${esc(c.sp).replaceAll('/',' \u00b7 ')} &middot; pre ${esc(c.pm).replaceAll('/',' \u00b7 ')}</td>
            <td class="py-2 px-2 font-mono whitespace-nowrap">${stB} &middot; ${mkExtA(atlUrl, 'Atlas &nearr;')} &middot; ${mkExtA(ucscUrl, 'UCSC &nearr;')}</td>
          </tr>`;
        }).join('')}</tbody>
      </table></div>
      <div class="text-[var(--muted-foreground)] font-mono text-xs pt-1 border-t border-[var(--card-border)]">Key: mRNA = spliced 0-mm&middot;1-mm&middot;wobble genes &middot; pre = pre-mRNA 0-mm / 1-mm(&le;50bp SS) / wobble / 2-mm(&le;25bp) / 1-nt bulge / 18-nt sub-core (1-based GRCh38 target windows).</div></div>`;
  }
  if(!isFull && location.protocol !== 'about:' && (['EALS-014','EALS-015','EALS-023','EALS-017','EALS-018'].includes(r.id) || /^EALS-0(?:3[4-9]|4[0-2])$/.test(r.id))){
    out += `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 flex items-center justify-between gap-2 flex-wrap text-xs">
      <span class="text-[var(--muted-foreground)]">Interactive single-gene subunit cards &amp; 3-region NYGC RNA-seq profiles are available in the full 5-view Explorer.</span>
      <a href="../CARBON_ALS_INTERACTIVE_EXPLORER.html#dossier/${esc(r.id)}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono cursor-pointer">Open in Full Explorer &rarr;</a>
    </div>`;
  }
  const subRows = isFull ? DATA_SUB.filter(x => x.par === r.id) : [];
  if(subRows.length){
    out += `<div id="sec-subunits" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <h3 class="text-sm font-semibold">Subunit &amp; Selectivity Gene Dissection (${subRows.length} Genes &middot; NIH IDG TDL &amp; TSA)</h3>
        <span class="font-mono text-xs text-[var(--muted-foreground)]">gnomAD v4 LOEUF/pLI &middot; DepMap Chronos &middot; 3D Pocket &amp; Single-Gene Rationale</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">${subRows.map(sn => {
        const vcol = sn.vraw.startsWith('KEEP')?'text-[var(--warning)] border-[var(--warning)]':(sn.vraw.startsWith('RECLASSIFY')?'text-[var(--primary)] border-[var(--primary)]':'text-[var(--error)] border-[var(--error)]');
        const gPills = genePortalPills(sn.gene);
        return `<div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] space-y-2">
          <div class="flex items-start justify-between gap-2 flex-wrap border-b border-[var(--card-border)] pb-1.5">
            <div>
              <div class="flex items-center gap-1.5 flex-wrap" title="ExploreALS Subunit ${esc(sn.id)}">
                <span class="font-mono font-bold text-sm">${esc(sn.gene)}</span>
                <span class="font-mono text-xs text-[var(--muted-foreground)]">${esc(sn.id)}</span>
                ${gPills?`<span class="font-mono">${gPills}</span>`:''}
              </div>
              <div class="text-[var(--muted-foreground)] mt-0.5">${esc(sn.role)}</div>
            </div>
            <div class="flex flex-wrap items-center gap-1">${tdlBadge(sn.tdl)}${tsaSubBadge(sn.tsa)}</div>
          </div>
          <div class="space-y-0.5">
            <div class="font-mono font-semibold text-[var(--muted-foreground)]">1. Human Genetic Constraint &amp; Essentiality (TSA)</div>
            <div class="leading-relaxed break-words">${escLink(sn.gnomad, sn.gene)}</div>
          </div>
          <div class="space-y-0.5 pt-1 border-t border-[var(--card-border)]">
            <div class="font-mono font-semibold text-[var(--muted-foreground)]">2. 3D Structural Pocket &amp; Tractability</div>
            <div class="leading-relaxed break-words">${escLink(sn.drug, sn.gene)}</div>
          </div>
          <div class="space-y-0.5 pt-1 border-t border-[var(--card-border)]">
            <div class="flex items-center justify-between gap-1.5 flex-wrap">
              <span class="font-mono font-semibold text-[var(--muted-foreground)]">3. Single-Gene Adjudication Rationale</span>
              <span class="px-1.5 py-0.5 rounded border font-mono font-semibold ${vcol}">${esc(sn.vlbl)}</span>
            </div>
            <div class="leading-relaxed break-words">${escLink(sn.vbody, sn.gene)}</div>
          </div>
        </div>`;
      }).join('')}</div></div>`;
  }
  if(typeof DATA_NYGC !== 'undefined' && typeof NYGC_GENE_TO_ID !== 'undefined'){
    const gKey = Object.keys(NYGC_GENE_TO_ID).find(g => NYGC_GENE_TO_ID[g] === r.id);
    if(gKey && DATA_NYGC[gKey]){
      const regDefs = [['Spinal_Cord_Cervical','Cervical Cord'],['Spinal_Cord_Lumbar','Lumbar Cord'],['Cortex_Motor','Motor Cortex']];
      const allGenes = Object.keys(DATA_NYGC);
      const cmpRows = allGenes.map(g => {
        const pid = NYGC_GENE_TO_ID[g];
        const dc = DATA_NYGC[g]['Spinal_Cord_Cervical'], dl = DATA_NYGC[g]['Spinal_Cord_Lumbar'], dm = DATA_NYGC[g]['Cortex_Motor'];
        const hi = g === gKey ? 'bg-[var(--content)] font-semibold' : '';
        const dd = (dc.p < 0.05 && dc.sp > 0.25) ? ' <span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] font-mono text-xs" title="Non-significant in small n=9 ALS-SOD1/FUS; junction RT-ddPCR required">ddPCR</span>' : '';
        return `<tr class="align-middle ${hi}">
          <td class="py-1 px-2 font-mono"><button type="button" data-open-dossier="${esc(pid)}" class="text-[var(--link)] hover:underline font-semibold cursor-pointer">${esc(g)} (${esc(pid)})</button></td>
          <td class="py-1 px-2 font-mono tabular-nums">${dc.b>=0?'+':''}${dc.b.toFixed(3)} <span class="text-[var(--muted-foreground)]">(p=${dc.p<0.001?dc.p.toExponential(1):dc.p.toFixed(3)})</span></td>
          <td class="py-1 px-2 font-mono tabular-nums whitespace-nowrap">${dc.sp.toFixed(2)}${dd}</td>
          <td class="py-1 px-2 font-mono tabular-nums">${dc.tail.toFixed(2)}%</td>
          <td class="py-1 px-2 font-mono tabular-nums">${dl.b>=0?'+':''}${dl.b.toFixed(3)} <span class="text-[var(--muted-foreground)]">(p=${dl.p<0.001?dl.p.toExponential(1):dl.p.toFixed(3)})</span></td>
          <td class="py-1 px-2 font-mono tabular-nums">${dm.b>=0?'+':''}${dm.b.toFixed(3)} <span class="text-[var(--muted-foreground)]">(p=${dm.p<0.001?dm.p.toExponential(1):dm.p.toFixed(3)})</span></td>
        </tr>`;
      }).join('');
      out += `<div id="sec-nygc" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
        <div class="flex items-center justify-between gap-2 flex-wrap">
          <h3 class="text-sm font-semibold">NYGC 3-Region Postmortem RNA-Seq Profile &mdash; ${esc(gKey)} (${mkExtA('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE153960','GSE153960')} &middot; ${mkExtA('https://pubmed.ncbi.nlm.nih.gov/36482247/','PMID:36482247')})</h3>
          <span class="font-mono text-xs text-[var(--muted-foreground)]">&#9679; Empirical Donor-Level RIN+GC OLS</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs">${regDefs.map(([rk, rlbl]) => {
          const d = DATA_NYGC[gKey][rk], m = DATA_NYGC_META[rk];
          const sigNeg = d.b < 0 && d.p < 0.05, sigPos = d.b > 0 && d.p < 0.05;
          const dotCol = sigNeg ? 'var(--primary)' : (sigPos ? 'var(--warning)' : 'var(--muted-foreground)');
          const ptPct = Math.max(4, Math.min(96, ((Math.max(-0.6, Math.min(0.6, d.b)) + 0.6) / 1.2) * 100));
          const sL = Math.min(50, ptPct), sW = Math.max(1, Math.abs(ptPct - 50));
          const ddpcrTag = (d.p < 0.05 && d.sp > 0.25) ? ' <span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] text-xs" title="Non-significant in small n=9 ALS-SOD1/FUS (underpowered for equivalence); junction RT-ddPCR required">ddPCR</span>' : '';
          return `<div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] space-y-1 font-mono tabular-nums">
            <div class="flex items-center justify-between"><strong>${rlbl}</strong><span class="text-[var(--muted-foreground)]">N=${m.ntot} (${m.ntdp} TDP/${m.nctrl} Ctrl/${m.nsod} SOD1)</span></div>
            <div>RIN+GC &beta; = <strong>${d.b>=0?'+':''}${d.b.toFixed(3)}</strong> (p=${d.p<0.001?d.p.toExponential(1):d.p.toFixed(3)}) &middot; SOD1/FUS p=${d.sp.toFixed(2)}${ddpcrTag}</div>
            <div class="relative w-full h-3 rounded bg-[var(--card)] border border-[var(--card-border)] overflow-hidden">
              <div class="absolute top-0 bottom-0 w-px bg-[var(--foreground)] opacity-40" style="left:50%"></div>
              <div class="absolute" style="left:${sL.toFixed(1)}%;width:${sW.toFixed(1)}%;top:5px;height:2px;background:${dotCol}"></div>
              <div class="absolute rounded-full" style="left:${ptPct.toFixed(1)}%;top:2.5px;width:7px;height:7px;margin-left:-3.5px;background:${dotCol}"></div>
            </div>
            <div class="text-[var(--muted-foreground)]">tSTMN2 &beta;=${d.tb>=0?'+':''}${d.tb.toFixed(2)} (p=${d.tp<0.001?d.tp.toExponential(1):d.tp.toFixed(3)}) &middot; Tail ${d.tail.toFixed(2)}%</div>
          </div>`;
        }).join('')}</div>
        <details class="rounded bg-[var(--background)] border border-[var(--card-border)] px-3 py-2 text-xs">
          <summary class="cursor-pointer font-mono text-xs text-[var(--link)] flex flex-wrap items-center justify-between gap-2 select-none"><span>Compare All 9 Cryptic-Splicing &amp; APA Candidates Across NYGC Cervical (N=206), Lumbar (N=181) &amp; Motor Cortex (N=120)</span><span class="text-[var(--muted-foreground)]">EALS-034 &ndash; EALS-042 Cross-Region Table</span></summary>
          <div class="pt-2 mt-2 border-t border-[var(--card-border)] overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead><tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                <th class="py-1 px-2">Gene (ID)</th><th class="py-1 px-2">Cervical &beta; (adj p)</th><th class="py-1 px-2">Cervical SOD1/FUS p</th>
                <th class="py-1 px-2">Cervical Tail %</th><th class="py-1 px-2">Lumbar &beta; (adj p)</th><th class="py-1 px-2">Motor Cortex &beta; (adj p)</th>
              </tr></thead>
              <tbody class="divide-y divide-[var(--card-border)]">${cmpRows}</tbody>
            </table>
          </div>
        </details></div>`;
    }
  }
  return out;
}

function getFilteredDossierList(){
  const qEl = document.getElementById('d-search');
  const q = qEl ? qEl.value.trim() : '';
  const activeLensObj = (dossierLens !== 'ALL' && typeof DATA_LENSES !== 'undefined') ? DATA_LENSES.find(l => l.k === dossierLens) : null;
  const scored = [];
  for(let i = 0; i < DATA_PORT.length; i++){
    const r = DATA_PORT[i];
    if(activeLensObj && !activeLensObj.ids.includes(r.id)) continue;
    if(dossierSlice === 'T12' && r.tier !== 'TIER_1_ACTIONABLE_NOW' && r.tier !== 'TIER_2_FOCUSED_GATE_FIRST') continue;
    if(dossierSlice === 'WATCH' && r.tier !== 'TIER_3_EXPLORATORY_DISCOVERY') continue;
    if(dossierSlice === 'BIO' && r.tier !== 'BIOMARKER_BENCHMARK_ONLY' && r.tier !== 'COMPANION_PROTOCOL_ONLY') continue;
    if(dossierSlice === 'DROP' && r.tier !== 'DROPPED_FALSIFIED_EXCLUDED') continue;
    if(!q){ scored.push({r: r, tier: 9}); continue; }
    const sObj = (typeof DATA_SUM !== 'undefined' && DATA_SUM[r.id]) ? DATA_SUM[r.id] : null;
    const hTxt = sObj ? ((sObj.hyp || '') + ' ' + (sObj.verdict || '') + ' ' + (sObj.edge_text || '')) : '';
    const snTxt = (typeof DATA_SUB !== 'undefined') ? DATA_SUB.filter(sn => sn.par === r.id).map(sn => sn.id + ' ' + sn.gene + ' ' + sn.role).join(' ') : '';
    const m = matchCandidateQuery(r, q, r.tier + ' ' + hTxt + ' ' + snTxt);
    if(m.ok) scored.push({r: r, tier: m.tier});
  }
  if(q) scored.sort((a, b) => (a.tier - b.tier) || (a.r.rk - b.r.rk));
  return scored.map(x => x.r);
}

function renderDossierSidebar(){
  const sliceDefs = [
    ['ALL', 'All'],
    ['T12', 'T1/2 (8)'],
    ['WATCH', 'T3 (20)'],
    ['BIO', 'Bio & Calib (8)'],
    ['DROP', 'Falsified (16)'],
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
  const dSearchQ = ((document.getElementById('d-search') || {}).value || '').trim();
  const dSearchLow = dSearchQ.toLowerCase();
  const SHORT_NAV_NAME = {'EALS-030':'SARM1','EALS-031':'Aldesleukin','EALS-001':'UNC13A','EALS-006':'KCNQ2','EALS-002':'STMN2','EALS-007':'IL1RL1 / sST2','EALS-015':'SCFD1 / G2E3','EALS-014':'CHMP7 / CHMP2B','EALS-018':'C1q (C1QA/B/C)','EALS-016':'FBXL5 / IRP2','EALS-020':'Apilimod','EALS-019':'Baricitinib','EALS-026':'CuATSM','EALS-005':'TMS / SDTC PD','EALS-032':'Methylcobalamin','EALS-017':'CHIT1 / GPNMB','EALS-027':'Mycophenolate','EALS-029':'Lonafarnib'};
  const mkBtn = r => {
    const isPilot = Boolean(DATA_MONOGRAPHS[r.id]);
    const on = r.id === dossierId;
    const dotCol = r.tier==='TIER_1_ACTIONABLE_NOW' ? 'var(--success)'
      : ((r.tier==='TIER_2_FOCUSED_GATE_FIRST' || r.tier==='BIOMARKER_BENCHMARK_ONLY' || r.tier==='COMPANION_PROTOCOL_ONLY') ? 'var(--primary)'
      : (r.tier==='DROPPED_FALSIFIED_EXCLUDED' ? 'var(--error)' : 'var(--warning)'));
    const cls = on ? 'bg-[var(--content)] border-[var(--primary)] border-l-2 font-semibold text-[var(--foreground)]' : 'bg-[var(--background)] border-[var(--card-border)] hover:bg-[var(--content)]';
    const mq = dSearchQ ? matchCandidateQuery(r, dSearchQ, '') : {sub: ''};
    const subM = (dSearchLow && typeof DATA_SUB !== 'undefined') ? DATA_SUB.filter(sn => sn.par === r.id && !r.name.toLowerCase().includes(sn.gene.toLowerCase()) && (sn.id === mq.sub || (sn.gene+' '+sn.id+' '+sn.role).toLowerCase().includes(dSearchLow))).map(sn => sn.gene) : [];
    const baseShort = SHORT_NAV_NAME[r.id] || r.name.split('(')[0].trim();
    const shortLbl = baseShort + (subM.length ? ' (+' + subM.join(',') + ')' : '');
    const tip = `#${r.rk} ${r.name} (${r.id}) [${isPilot ? 'Full Monograph' : 'Triage Dossier'}]`;
    return `<button type="button" data-open-dossier="${esc(r.id)}" ${on?'aria-current="true"':''} title="${esc(tip)}" class="w-full text-left px-2 py-1 rounded border ${cls} flex items-center justify-between gap-1.5 text-xs cursor-pointer">
      <span class="min-w-0 flex items-center gap-1.5 pointer-events-none">
        <span class="w-1.5 h-1.5 rounded-full shrink-0" style="background:${dotCol}"></span>
        <span class="font-mono text-[var(--muted-foreground)] shrink-0">#${r.rk}</span>
        <span class="font-medium truncate text-[var(--foreground)]">${esc(shortLbl)}</span>
      </span>
      <span class="shrink-0 flex items-center gap-1 pointer-events-none">
        <span class="font-mono text-xs text-[var(--muted-foreground)]">${esc(r.id)}</span>
        ${isPilot?'<span class="px-1 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono text-xs" title="Full Translational Monograph">M</span>':''}
      </span>
    </button>`;
  };
  const matched = getFilteredDossierList();
  const t1 = matched.filter(r => r.tier==='TIER_1_ACTIONABLE_NOW');
  const t2 = matched.filter(r => r.tier==='TIER_2_FOCUSED_GATE_FIRST');
  const t3 = matched.filter(r => r.tier==='TIER_3_EXPLORATORY_DISCOVERY');
  const bm = matched.filter(r => r.tier==='BIOMARKER_BENCHMARK_ONLY' || r.tier==='COMPANION_PROTOCOL_ONLY');
  const dr = matched.filter(r => r.tier==='DROPPED_FALSIFIED_EXCLUDED');
  const totMatched = matched.length;
  const cntEl = document.getElementById('d-nav-count');
  if(cntEl) cntEl.textContent = `${totMatched} / ${DATA_PORT.length}`;
  let html = '';
  if(t1.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--success)] font-mono font-semibold text-xs py-0.5">T1 &middot; Actionable (${t1.length})</div>` + t1.map(mkBtn).join('');
  if(t2.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--primary)] font-mono font-semibold text-xs pt-1.5 pb-0.5">T2 &middot; Validation Gate (${t2.length})</div>` + t2.map(mkBtn).join('');
  if(t3.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--warning)] font-mono font-semibold text-xs pt-1.5 pb-0.5">T3 &middot; Discovery (${t3.length})</div>` + t3.map(mkBtn).join('');
  if(bm.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--primary)] font-mono font-semibold text-xs pt-1.5 pb-0.5">Biomarkers &amp; Calibrators (${bm.length})</div>` + bm.map(mkBtn).join('');
  if(dr.length) html += `<div class="sticky top-0 z-10 bg-[var(--card)] text-[var(--error)] font-mono font-semibold text-xs pt-1.5 pb-0.5">Falsified (${dr.length})</div>` + dr.map(mkBtn).join('');
  const nav = document.getElementById('d-nav');
  if(nav) nav.innerHTML = html || '<div class="text-[var(--muted-foreground)] text-xs py-2">No matching dossiers. <button type="button" data-reset-d-nav="1" class="text-[var(--link)] underline font-mono cursor-pointer">Show all</button></div>';
  const mobSel = document.getElementById('d-mobile-select');
  if(mobSel){
    if(!mobSel.options.length){
      const g1 = DATA_PORT.filter(r => r.tier==='TIER_1_ACTIONABLE_NOW');
      const g2 = DATA_PORT.filter(r => r.tier==='TIER_2_FOCUSED_GATE_FIRST');
      const g3 = DATA_PORT.filter(r => r.tier==='TIER_3_EXPLORATORY_DISCOVERY');
      const gB = DATA_PORT.filter(r => r.tier==='BIOMARKER_BENCHMARK_ONLY' || r.tier==='COMPANION_PROTOCOL_ONLY');
      const gD = DATA_PORT.filter(r => r.tier==='DROPPED_FALSIFIED_EXCLUDED');
      const mkOpt = r => `<option value="${esc(r.id)}">#${r.rk} ${esc(r.name.split('(')[0].trim())} (${esc(r.id)}) ${DATA_MONOGRAPHS[r.id]?'[Monograph]':'[Dossier]'}</option>`;
      mobSel.innerHTML = `<optgroup label="Tier 1 · Actionable Leads (${g1.length})">${g1.map(mkOpt).join('')}</optgroup><optgroup label="Tier 2 · Validation Gate (${g2.length})">${g2.map(mkOpt).join('')}</optgroup><optgroup label="Tier 3 · Exploratory Discovery (${g3.length})">${g3.map(mkOpt).join('')}</optgroup><optgroup label="Biomarkers & Functional Calibrators (${gB.length})">${gB.map(mkOpt).join('')}</optgroup><optgroup label="Dropped · Scientifically Falsified (${gD.length})">${gD.map(mkOpt).join('')}</optgroup>`;
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
  const isFullExplorer = (typeof DATA_SUB !== 'undefined');
  const filtList = isFullExplorer ? getFilteredDossierList() : [];
  const navPool = (isFullExplorer && filtList.length >= 2 && filtList.some(x=>x.id===r.id)) ? filtList : DATA_PORT;
  const poolIdx = navPool.findIndex(x=>x.id===r.id);
  const pIdx = MONOGRAPH_ORDER.indexOf(r.id);
  const prevId = (!isFullExplorer && pIdx >= 0) ? MONOGRAPH_ORDER[(pIdx - 1 + MONOGRAPH_ORDER.length) % MONOGRAPH_ORDER.length] : navPool[(poolIdx - 1 + navPool.length) % navPool.length].id;
  const nextId = (!isFullExplorer && pIdx >= 0) ? MONOGRAPH_ORDER[(pIdx + 1) % MONOGRAPH_ORDER.length] : navPool[(poolIdx + 1) % navPool.length].id;
  const prevObj = DATA_PORT.find(x=>x.id===prevId) || r;
  const nextObj = DATA_PORT.find(x=>x.id===nextId) || r;
  const prevLbl = `#${prevObj.rk} ${prevObj.sym || prevObj.id}`;
  const nextLbl = `#${nextObj.rk} ${nextObj.sym || nextObj.id}`;
  const mp = document.getElementById('d-mobile-prev'), mn = document.getElementById('d-mobile-next');
  if(mp){ mp.setAttribute('data-open-dossier', prevId); mp.textContent = '\u2190 #' + prevObj.rk; }
  if(mn){ mn.setAttribute('data-open-dossier', nextId); mn.textContent = '#' + nextObj.rk + ' \u2192'; }

  const w = DATA_MONOGRAPHS[r.id];
  const s = (typeof DATA_SUM !== 'undefined' && DATA_SUM[r.id]) ? DATA_SUM[r.id] : null;
  const candUpds = (isFullExplorer && typeof DATA_UPDATES !== 'undefined') ? DATA_UPDATES.filter(u => u.ids.includes(r.id) || u.ids.some(x => x.startsWith(r.id + '.'))) : [];
  const updPill = candUpds.length
    ? `<button type="button" data-jump-updates="${esc(r.id)}" class="px-2.5 py-1 rounded border border-[var(--primary)] text-[var(--primary)] font-mono text-xs cursor-pointer" title="View living research updates and revisions for ${esc(r.id)}">&#8634; ${candUpds.length} Update${candUpds.length>1?'s':''} &rarr;</button>`
    : '';
  const evRows = DATA_EV[r.id] || [];
  const evFilterBtn = isFullExplorer
    ? `<button type="button" data-jump-rep-cand="${esc(r.id)}" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Filter All ${evRows.length} in Tab 4 &rarr;</button>`
    : '';
  const evTable = evRows.length ? `<div id="sec-ledger" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
    <div class="flex items-center justify-between gap-2 flex-wrap">
      <h3 class="text-sm font-semibold">Primary Evidence &amp; FAIR Provenance Ledger (${evRows.length} Atomic Contrasts)</h3>
      <div class="flex items-center gap-2 flex-wrap"><span class="font-mono text-xs text-[var(--muted-foreground)]">Script &amp; Checksum Provenance &middot; 4-Level Evidence Design</span>${evFilterBtn}</div>
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
        const provTip = `Provenance: ${esc(e.eid)} · ${esc(e.run)}${e.sha64 ? ' · sha256:' + esc(e.sha64) : (e.sha ? ' · sha256:' + esc(e.sha) : '')}`;
        const repHref = '../CARBON_ALS_INTERACTIVE_EXPLORER.html#replication' + (e.run ? '/' + encodeURIComponent(e.run) : '');
        const runChip = e.run
          ? (isFullExplorer
            ? `<button type="button" data-open-rep-run="${esc(e.run)}" class="text-[var(--link)] hover:underline font-mono text-xs cursor-pointer" title="${provTip}">Verify in Tab 4 &rarr;</button>`
            : (location.protocol !== 'about:' ? `<a href="${repHref}" class="text-[var(--link)] hover:underline font-mono text-xs" title="${provTip}">Verify in Tab 4 &rarr;</a>` : ''))
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

  const hasSubPanel = isFullExplorer && DATA_SUB.some(x => x.par === r.id);
  const hasNygcPanel = (typeof DATA_NYGC !== 'undefined' && typeof NYGC_GENE_TO_ID !== 'undefined' && Object.values(NYGC_GENE_TO_ID).includes(r.id));
  const hasCisPanel = (typeof DATA_CIS !== 'undefined' && DATA_CIS.some(c => c.pid === r.id || c.sc === r.id));
  const jumpSecs = w
    ? [['sec-overview', 'Overview & Gates'], ['sec-cascade', 'Pathogenic Mechanism'], ['sec-evidence-viz', 'Effect Sizes & Diagrams'], ['sec-safety', 'Safety & 3D Structure'], ['sec-5rs', 'Translational Deep Dive']]
    : [['sec-overview', 'Hypothesis & Verdict'], ['sec-procon', r.dec === 'DROP' ? 'Discovery vs. Falsifier' : 'Evidence Pro / Con']];
  if(hasSubPanel) jumpSecs.push(['sec-subunits', 'Subunit & Selectivity']);
  if(hasNygcPanel) jumpSecs.push(['sec-nygc', 'NYGC 3-Region RNA']);
  if(hasCisPanel) jumpSecs.push(['sec-cis', 'Splice Windows']);
  if(evRows.length) jumpSecs.push(['sec-ledger', `Primary Evidence (${evRows.length})`]);
  const fromPortBtn = (isFullExplorer && typeof dossierFromPortfolio !== 'undefined' && dossierFromPortfolio)
    ? `<button type="button" data-switch-tab="portfolio" class="px-2 py-0.5 rounded border border-[var(--primary)] text-[var(--primary)] font-mono font-semibold text-xs cursor-pointer">&larr; Triage Table</button>`
    : '';
  const secJumpBar = `<div class="flex flex-wrap items-center justify-between gap-1.5 pb-1 border-b border-[var(--card-border)] text-xs font-mono">
    <div class="flex flex-wrap items-center gap-1">${fromPortBtn}<span class="text-[var(--muted-foreground)] mr-0.5">Sections:</span>${jumpSecs.map(([sid, slbl]) => `<button type="button" data-scroll-sec="${sid}" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] cursor-pointer">${esc(slbl)}</button>`).join('')}</div>
    ${isFullExplorer ? `<button type="button" data-jump-rep-cand="${esc(r.id)}" class="text-[var(--link)] hover:underline cursor-pointer">Verify in Tab 4 &rarr;</button>` : ''}
  </div>`;

  if(!w){
    const isDrop = r.dec === 'DROP';
    const isBench = r.dec === 'RECLASSIFY_BENCHMARK_OR_BIOMARKER';
    const vCol = isDrop ? 'border-l-[var(--error)]' : (isBench ? 'border-l-[var(--primary)]' : 'border-l-[var(--warning)]');
    const vTxt = isDrop ? `text-[var(--error)]` : (isBench ? `text-[var(--primary)]` : `text-[var(--warning)]`);
    const benchHdr = (r.id==='EALS-013'||r.id==='EALS-032') ? 'ADJUDICATION RATIONALE &mdash; APPROVED SOC &amp; ASSAY BENCHMARK'
      : (r.id==='EALS-003' ? 'ADJUDICATION RATIONALE &mdash; WITHDRAWN HUMAN PD CALIBRATOR'
      : (r.id==='EALS-017' ? 'ADJUDICATION RATIONALE &mdash; REPLICATED LIVING-CSF STAGING &amp; PD PANEL'
      : 'ADJUDICATION RATIONALE &mdash; CANDIDATE CSF MARKER (PRE-VALIDATION)'));
    const vHdr = isDrop ? `ADJUDICATION RATIONALE &mdash; DROP &middot; ${esc(humanizeEnum(r.epi)).toUpperCase()}`
      : (isBench ? benchHdr : 'ADJUDICATION RATIONALE &mdash; KEEP &middot; EXPLORATORY (UNTESTED &ne; FALSIFIED)');
    const hCell = isDrop
      ? `<div class="text-[var(--muted-foreground)] font-mono">Positive Falsification Gate</div><div class="font-semibold text-[var(--error)] mt-0.5">${esc(humanizeEnum(r.epi))}</div><div class="text-[var(--muted-foreground)] mt-0.5">Excluded by positive clinical, PK/safety, or confounding counterevidence.</div>`
      : `<div class="text-[var(--muted-foreground)] font-mono">Open Validation Steps (${r.hcnt})</div><div class="flex flex-wrap gap-1 mt-1">${r.hurdles && r.hurdles !== 'NONE' ? r.hurdles.split(';').map(h=>`<span class="px-1.5 py-0.5 rounded border border-[var(--border)] text-xs">${esc(formatHurdle(h))}</span>`).join('') : '<span class="text-[var(--muted-foreground)]">None (Calibration / Biomarker)</span>'}</div>`;
    const crowdPill = (r.crowd && !r.crowd.startsWith('N/A')) ? `<span class="px-2 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">${esc(r.crowd)}</span>` : '';
    const sumPriorLine = (r.prior && r.prior !== 'NONE')
      ? `<div class="mt-0.5"><span class="px-1 rounded border border-[var(--warning)] text-[var(--warning)] font-mono">&#9671; Modeled Estimate</span> <span class="text-[var(--muted-foreground)]">${esc(formatPrior(r.prior))}</span></div>`
      : `<div class="mt-0.5"><span class="px-1 rounded border border-[var(--success)] text-[var(--success)] font-mono">&#9679; Empirical Data</span> <span class="text-[var(--muted-foreground)]">${esc(formatPrior(r.prior))}</span></div>`;
    const gPills = genePortalPills(r.id);
    const rightCol = isDrop
      ? `<div class="p-3.5 rounded-lg border border-[var(--card-border)] bg-[var(--background)] border-l-4 border-l-[var(--error)] space-y-2 text-xs">
          <div class="font-mono font-bold text-[var(--error)]">&#10005; DECISIVE FALSIFYING COUNTEREVIDENCE</div>
          ${formatProseParas(s ? s.disproves : humanizeEnum(r.epi), r.id, 'space-y-2')}
        </div>`
      : `<div class="p-3.5 rounded-lg border border-[var(--card-border)] bg-[var(--background)] border-l-4 border-l-[var(--warning)] space-y-2 text-xs">
          <div class="font-mono font-bold text-[var(--warning)]">&#9651; TRANSLATIONAL CAVEATS &amp; NEXT DISCRIMINATING TEST</div>
          ${formatProseParas(s ? s.disproves : '', r.id, 'space-y-2')}
          <div class="pt-1.5 mt-1 border-t border-[var(--card-border)] leading-relaxed"><strong class="font-mono text-[var(--foreground)]">Discriminating Next Test:</strong> ${formatNextTest(r.nxt, r.id)}</div>
        </div>`;
    box.innerHTML = `<div id="sec-overview" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
      <div class="flex items-start justify-between gap-2 flex-wrap border-b border-[var(--card-border)] pb-2.5">
        <div class="min-w-0">
          <div class="flex items-center gap-2 flex-wrap"><span class="px-2 py-0.5 rounded bg-[var(--background)] border border-[var(--border)] font-mono font-bold text-xs" title="Translational Priority Rank #${r.rk}/52 · Genetic & Pathology Evidence Rank #${r.brk}/52">Priority #${r.rk}/52 (Evidence #${r.brk}) &middot; ${esc(r.id)}</span> ${decBadge(r.dec, r.id)} <span class="px-2 py-0.5 rounded border border-[var(--border)] font-medium text-xs">${esc(humanizeEnum(r.tier))}</span> ${crowdPill}</div>
          <h2 class="text-base font-bold mt-1.5 break-words">${esc(r.name)} &mdash; <span class="font-normal text-[var(--muted-foreground)]">${escLink(s ? s.sub : humanizeEnum(r.sub), r.id)}</span></h2>
          <div class="text-xs font-mono text-[var(--muted-foreground)] mt-0.5">${!isDrop && r.trl !== 'PROTOCOL_COMPANION_NA' ? esc(humanizeEnum(r.trl)) + ' &middot; ' : ''}${esc(humanizeEnum(r.basis))}${gPills?' &middot; '+gPills:''}</div>
        </div>
        <div class="flex items-center gap-1.5 flex-wrap min-w-0">
          ${updPill}
          <span class="px-2 py-1 rounded border border-[var(--border)] bg-[var(--background)] text-[var(--muted-foreground)] font-mono text-xs">Structured Triage Dossier</span>
          <button type="button" data-open-dossier="${prevId}" class="inline-block px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs cursor-pointer" title="Previous candidate ([ key)">&larr; ${esc(prevLbl)}</button>
          <button type="button" data-open-dossier="${nextId}" class="inline-block px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs cursor-pointer" title="Next candidate (] key)">${esc(nextLbl)} &rarr;</button>
        </div>
      </div>
      ${secJumpBar}
      ${renderEdgeRibbon(s, r.id)}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
        <div class="p-3.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--primary)] space-y-2">
          <div class="font-mono font-bold text-[var(--primary)]">CANDIDATE &amp; BIOLOGICAL HYPOTHESIS</div>
          ${formatProseParas(s ? s.hyp : '', r.id, 'space-y-2')}
        </div>
        <div class="p-3.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 ${vCol} space-y-2">
          <div class="font-mono font-bold ${vTxt}">${vHdr}</div>
          ${formatProseParas(s ? s.verdict : '', r.id, 'space-y-2')}
        </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-2.5 text-xs">
        <div class="p-2.5 rounded border border-[var(--card-border)] bg-[var(--background)] space-y-0.5"><div class="text-[var(--muted-foreground)] font-mono">Therapeutic Modality</div><div class="font-medium leading-snug">${escLink(formatModality(r.mod), r.id)}</div></div>
        <div class="p-2.5 rounded border border-[var(--card-border)] bg-[var(--background)] space-y-0.5"><div class="text-[var(--muted-foreground)] font-mono">Causal vs. Reactive Sign</div><div class="font-medium">${esc(s ? s.causal : humanizeEnum(r.epi))}</div><div class="text-[var(--muted-foreground)]">${esc(humanizeEnum(r.sub))} &middot; ${trackLabel(r.trk)}</div></div>
        <div class="p-2.5 rounded border border-[var(--card-border)] bg-[var(--background)] space-y-0.5"><div class="text-[var(--muted-foreground)] font-mono">Next Validation &amp; Basis</div><div class="font-mono">${esc(humanizeEnum(r.gate))}</div>${sumPriorLine}</div>
        <div class="p-2.5 rounded border border-[var(--card-border)] bg-[var(--background)]">${hCell}</div>
      </div>
      <div id="sec-procon" class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="p-3.5 rounded-lg border border-[var(--card-border)] bg-[var(--background)] border-l-4 ${isDrop?'border-l-[var(--muted-foreground)]':'border-l-[var(--success)]'} space-y-2 text-xs">
          <div class="font-mono font-bold ${isDrop?'text-[var(--muted-foreground)]':'text-[var(--success)]'}">${isDrop?'ORIGINATING DISCOVERY / PRECLINICAL SIGNAL':'&#10003; SUPPORTING HUMAN &amp; PRECLINICAL EVIDENCE'}</div>
          ${formatProseParas(s ? s.proves : '', r.id, 'space-y-2')}
        </div>
        ${rightCol}
      </div>
    </div>${renderSummaryDomainPanels(r)}${evTable}`;
    return;
  }

  const cisForAtlas = DATA_CIS.filter(c => c.pid===r.id || c.sc===r.id);
  const atlasBtns = cisForAtlas.map(c => {
    const url = `https://deepmind.google.com/science/alphagenome/atlas?q=${c.chr}:${Math.max(1,Number(c.lo)-250)}-${Number(c.hi)+250}&m=locus&lItems=avi,section:RNA_SEQ,section:SPLICE_JUNCTIONS,section:DNASE`;
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs">${c.lead?'★ ':''}${esc(c.gene)} &middot; Window #${c.rk} Atlas &nearr;</a>`;
  }).join('') + (isFullExplorer && cisForAtlas.length ? `<button type="button" data-jump-intervals="${esc(r.id)}" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs cursor-pointer">Inspect in Tab 3 &rarr;</button>` : (cisForAtlas.length && location.protocol !== 'about:' ? `<a href="../CARBON_ALS_INTERACTIVE_EXPLORER.html#intervals/${esc(r.id)}" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs">Inspect in Tab 3 &rarr;</a>` : ''));
  const hurdleHtml = r.hurdles && r.hurdles !== 'NONE'
    ? r.hurdles.split(';').map(h=>`<div class="leading-snug">&bull; ${esc(formatHurdle(h))}</div>`).join('')
    : '<div class="text-[var(--muted-foreground)]">None</div>';
  const mCol = r.dec === 'KEEP_CORE' ? 'border-l-[var(--success)]' : 'border-l-[var(--warning)]';
  const mTxt = r.dec === 'KEEP_CORE' ? 'text-[var(--success)]' : 'text-[var(--warning)]';
  const mHdr = r.dec === 'KEEP_CORE'
    ? 'ADJUDICATION RATIONALE &mdash; KEEP &middot; CORE'
    : 'ADJUDICATION RATIONALE &mdash; KEEP &middot; EXPLORATORY (UNTESTED &ne; FALSIFIED)';
  const mGPills = genePortalPills(r.id);

  box.innerHTML = `
    <div id="sec-overview" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2.5">
      <div class="flex flex-wrap items-start justify-between gap-2 border-b border-[var(--card-border)] pb-2.5">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <span class="px-2 py-0.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-bold text-xs" title="Translational Priority Rank #${r.rk}/52 · Genetic & Pathology Evidence Rank #${r.brk}/52">Priority #${r.rk}/52 (Evidence #${r.brk}) &middot; ${esc(r.id)}</span>
            ${decBadge(r.dec, r.id)}
            <span class="px-2 py-0.5 rounded border border-[var(--border)] font-medium text-xs">${esc(humanizeEnum(r.tier))}</span>
            ${(r.crowd && !r.crowd.startsWith('N/A')) ? `<span class="px-2 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">${esc(r.crowd)}</span>` : ''}
          </div>
          <h2 class="text-base font-bold mt-1 break-words">${esc(r.name)} &mdash; <span class="font-normal text-[var(--muted-foreground)]">${esc(w.subtitle)}</span></h2>
          <div class="text-xs font-mono text-[var(--muted-foreground)] mt-0.5">${esc(humanizeEnum(r.trl))} &middot; ${esc(humanizeEnum(r.gate))} &middot; ${esc(humanizeEnum(r.basis))}${mGPills ? ' &middot; ' + mGPills : ''}</div>
        </div>
        <div class="flex items-center gap-1.5 flex-wrap min-w-0">
          ${updPill}
          ${(typeof window !== 'undefined' && window.PUBLIC_WEB_EXPORT && isFullExplorer) ? `<a href="./monographs/${esc(r.id)}.html" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] font-mono text-xs" title="Open lightweight standalone monograph page">Standalone Page &nearr;</a>` : ''}
          <button type="button" data-open-dossier="${prevId}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs cursor-pointer" title="Previous candidate ([ key)">&larr; ${esc(prevLbl)}</button>
          <button type="button" data-open-dossier="${nextId}" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs cursor-pointer" title="Next candidate (] key)">${esc(nextLbl)} &rarr;</button>
        </div>
      </div>
      ${secJumpBar}
      ${renderEdgeRibbon(s, r.id)}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
        <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--primary)] space-y-2">
          <div class="font-mono font-bold text-[var(--primary)]">CANDIDATE &amp; BIOLOGICAL HYPOTHESIS</div>
          ${formatProseParas(s && s.hyp ? s.hyp : w.subtitle, r.id, 'space-y-2')}
        </div>
        <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 ${mCol} space-y-2">
          <div class="font-mono font-bold ${mTxt}">${mHdr}</div>
          ${formatProseParas(s ? s.verdict : '', r.id, 'space-y-2')}
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
        <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--success)] space-y-1 text-xs">
          <div class="font-mono font-bold text-[var(--success)]">&#10003; GO CRITERIA (ADVANCE THRESHOLDS)</div>
          ${formatGateList(w.verdict_box.pass_gate, r.id, false)}
        </div>
        <div class="p-2.5 rounded-lg bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--error)] space-y-1 text-xs">
          <div class="font-mono font-bold text-[var(--error)]">&#10005; NO-GO CRITERIA (FALSIFICATION THRESHOLDS)</div>
          ${formatGateList(w.verdict_box.kill_gate, r.id, true)}
        </div>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-1.5">
        ${w.ident.map(([k,v])=>`<div class="p-1.5 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)] text-xs">${esc(k)}</div><div class="font-mono font-semibold text-xs mt-0.5 break-words">${escLink(v, r.id)}</div></div>`).join('')}
      </div>
      <div class="flex flex-wrap items-center justify-between gap-2 pt-0.5">
        <div class="flex flex-wrap gap-1.5">${w.grades.map(([g,d])=>`<span class="px-2 py-0.5 rounded bg-[var(--background)] border border-[var(--border)] text-xs"><strong class="text-[var(--primary)]">${esc(g)}:</strong> ${escLink(d, r.id)}</span>`).join('')}</div>
        <div class="flex flex-wrap items-center gap-1.5 text-xs"><span class="text-[var(--muted-foreground)]">Related:</span>${w.related.map(x=>{const rp=DATA_PORT.find(q=>q.id===x); const rShort=x==='EALS-005'?'Excitability PD':(rp?(rp.sym || rp.name.split(/[\\s(/]/)[0]):''); const rTip=rp?`#${rp.rk} ${rp.name} (${rp.id})`:x; return `<button type="button" data-open-dossier="${esc(x)}" title="${esc(rTip)}" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-[var(--link)] cursor-pointer">${rp?'#'+rp.rk+' ':''}${esc(rShort || x)} &middot; ${esc(x)} &rarr;</button>`;}).join('')}</div>
      </div>
    </div>

    <div id="sec-cascade" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
      <div class="flex items-center justify-between gap-2 flex-wrap"><h3 class="text-sm font-semibold">Pathogenic Mechanism &amp; Modality Rationale</h3><span class="font-mono text-xs text-[var(--muted-foreground)]">Steps 1&ndash;3: Pathogenic Cascade &rarr; Step 4: Intervention</span></div>
      ${renderCausalGrid(w.causal, r.id)}
    </div>

    <div id="sec-evidence-viz" class="grid grid-cols-1 xl:grid-cols-12 gap-3">
      <div class="xl:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
        <div class="flex items-center justify-between gap-2 flex-wrap"><h3 class="text-sm font-semibold">Multi-Cohort Quantitative Evidence</h3><span class="font-mono text-xs text-[var(--muted-foreground)]">Scale-Separated Tracks &middot; Empirical Data vs. Modeled Estimates</span></div>
        ${renderEvidenceMatrix(w.ev_matrix, r.id)}
      </div>
      <div class="xl:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
        <h3 class="text-sm font-semibold">${esc(w.sig_fig.title)}</h3>
        ${renderSignatureSvg(r.id, w.sig_fig)}
        <p class="text-[var(--muted-foreground)] text-xs leading-relaxed">${escLink(w.sig_fig.caption, r.id)}</p>
        ${atlasBtns?`<div class="flex flex-wrap gap-1.5 pt-1">${atlasBtns}</div>`:''}
      </div>
    </div>

    <div id="sec-safety" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
      <h3 class="text-sm font-semibold">Target Safety Assessment (TSA) &amp; 3D Structural Profile</h3>
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
          <div class="border-t border-[var(--card-border)] pt-2"><span class="font-semibold text-[var(--muted-foreground)]">Open Validation Steps (${r.hcnt}):</span>
          <div class="text-xs mt-1 space-y-1">${hurdleHtml}</div></div>
        </div>
      </div>
    </div>

    <div id="sec-5rs" class="grid grid-cols-1 md:grid-cols-2 gap-3">
      ${w.sections.map(([st,body])=>{
        const sp = String(st).split(' — ');
        const hdrHtml = sp.length === 2 ? `<span class="font-mono text-xs text-[var(--primary)]">${esc(sp[0])} &mdash;</span> ${esc(sp[1])}` : esc(st);
        return `<div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
          <h3 class="text-sm font-semibold border-b border-[var(--card-border)] pb-1.5">${hdrHtml}</h3>
          ${formatProseParas(body, r.id, 'space-y-2.5')}
        </div>`;
      }).join('')}
    </div>
    ${renderSummaryDomainPanels(r)}${evTable}`;
}
"""
