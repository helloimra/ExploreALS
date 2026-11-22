"""Wave D v1.2.9 patches Part B for evidence_ledger (C011, C021, S01, S03, S04, S05)."""
from __future__ import annotations


def apply_wave_d_evidence_part_b(ev_map: dict[str, dict[str, str]]) -> None:
    # C011 (Furosemide): Hampel et al. 2018 Table 1 hNKCC1A/B 5.15-5.82 uM + CA1/CA2 Ki, Klomjai 2014 D1 Ia/sural (NOT Renshaw!), S118 origin
    ev_map["EV-B5-021"].update({
        "source_id_or_locator": "OpenFDA:NDA016273;CHEMBL35;PMID:29959396;PMID:28456721;10.1038/s41746-026-03225-w",
        "cohort_and_stratum": "Human oral furosemide 40 mg PK (NDA016273, MW 330.74, 91-99% albumin bound) vs Hampel et al. 2018 Table 1 human NKCC1 IC50",
        "assay_and_contrast": "Unbound plasma & OAT3/MRP4-effluxed CNS exposure vs human hNKCC1A/B, KCC2 & CA1/CA2 potency",
        "effect_direction": "SEVERE_1000_TO_5800X_CNS_EXPOSURE_DEFICIT",
        "effect_estimate": "fup=0.01-0.09 -> Cu,plasma ~30-150 nM; [MODEL_PRIOR] OAT3/MRP4-effluxed Cu,CNS <1-5 nM vs human hNKCC1A IC50=5.15 uM & hNKCC1B=5.82 uM (>1,000-5,800x gap)",
        "notes": "Hampel et al. 2018 Sci Rep PMID:29959396 Table 1 establishes human oocyte 86Rb+ hNKCC1A IC50=5.15 uM (4.34-13.7) and hNKCC1B=5.82 uM (4.73-7.27) (~18-23 uM in native cells, Table 2), alongside non-selective KCC2 blockade (IC50 ~10-25 uM) and sulfonamide CA2/CA1 inhibition (Ki ~65-200 nM); nominated from observational claims/MR (10.1038/s41746-026-03225-w) with 0 ALS clinical trials and 0 Bye 2025 screen rows.",
    })
    ev_map["EV-B5-022"].update({
        "source_id_or_locator": "DS001_COUNTS:Spinal_Cord_Cervical:SLC12A5;PMID:24835171;PMC4221825;PMID:41286450",
        "notes": "Corroborated in Bye 2025 PMID:41286450 Table 4 sALS vs Control iPSC-MN RNA-seq (SLC12A5 log2FC=-0.391, p=0.000557, padj=0.0486); furosemide co-inhibits KCC2, and in Klomjai et al. 2014 J Physiol PMID:24835171 (PMC4221825) oral 40 mg furosemide reduced human soleus D1 Ia afferent presynaptic inhibition (p=0.037, n=19) and sural cutaneous postsynaptic inhibition (p=0.034, n=15) via fenestrated DRG/diuretic effects (preserving brain-penetrant NKCC1-sparing KCC2 enhancers as distinct).",
    })

    # C021 (Icerguastat): 41-71x total plasma gap + modeled ~5-20 nM Cu,brain, both 5/34 total & 2/34 drug-related fatal TEAEs, GDF15 pg/mL CT.gov unit note, Abgueguen 2026 & Vieira 2024
    ev_map["EV-B4-017"].update({
        "notes": "Wilcoxon signed-rank p=0.00336; LODO max p=0.00466; tested solely at 2.5 uM (41-71x above human total plasma Cmax and [MODEL_PRIOR] ~125-500x above unbound brain).",
    })
    ev_map["EV-B4-018"].update({
        "effect_estimate": "Total plasma GeoMean Cmax=12.0 ng/mL (61.0 nM; Ph1 6.92 ng/mL = 35.2 nM, 41-71x below 2.5 uM; [MODEL_PRIOR] Cu,brain ~5-20 nM = 125-500x gap); fatal TEAEs 5/34 (14.7%) vs 2/17 (11.8%) total & 2/34 (5.9% vs 0%) drug-related; falls 8/34 (23.5% vs 0%); GDF15 flat (704.3->711.3->704.9 vs 580.3->580.1); ITT ALSFRS-R -0.33 (p=0.923)",
        "notes": "Posted NCT05508074 tables record 5/34 vs 2/17 all-cause fatal TEAEs including 2/34 (5.9% vs 0%) investigator-assessed drug-related fatal TEAEs (1 cardiac arrest, 1 cardiorespiratory arrest), null Plasma NfL ratio 1.04 [0.89, 1.21] (p=0.609), and attrition-selected Per-Protocol n=40/51 slope claims (11/34 vs 3/17 non-completers); note physiological plasma GDF15 (~704 pg/mL) is posted under CT.gov's umbrella 'ng/mL' table header alongside MCP1/FGF21.",
    })
    ev_map["EV-B4-019"].update({
        "source_id_or_locator": "PMID:28447936;PMID:29618508;PMID:43036320;PMID:42790826;PMID:38359044;DS_ZENG_APA:3endseq_S4;OpenTargets:PPP1R15A_PPP1R15B",
        "effect_estimate": "Crespillo-Casado 2017/2018 refuted direct PPP1R15A-PP1 inhibition; uM GluN2B NAM (Abgueguen 2026) & PHB2 (Ding 2026) require 1-5 uM; SOD1-G93A null (Vieira 2024); Zeng 2025 PPP1R15A dPAS=+0.0558 (padj=6.42e-8); gnomAD v4.1 LOEUF PPP1R15A=1.142 vs PPP1R15B=0.776",
        "notes": "Separates Crespillo-Casado et al. 2017/2018 (PMID:28447936, PMID:29618508) holophosphatase refutation, Abgueguen et al. 2026 PMID:43036320 GluN2B NMDA negative allosteric modulation (~1-5 uM, converging on failed C008 NMDA blockade), Ding et al. 2026 PMID:42790826 PHB2 interaction, and Vieira et al. 2024 PMID:38359044 in vivo SOD1-G93A failure.",
    })

    # S01 (Dexmedetomidine): measured NDA021038 Cu,p (0.09-0.37 nM) + Talke 1997 human lumbar CSF (~0.20-0.35 nM, ~6,700-10,000x gap), Igalmi NDA215390, ProMISe PMID:33905493
    ev_map["EV-B6-032"].update({
        "source_type": "HUMAN_CSF_AND_PLASMA_PK_AUDIT",
        "source_id_or_locator": "OpenFDA:NDA021038;OpenFDA:NDA215390;PMID:9249114;PMID:9356115;ChEMBL:CHEMBL778",
        "cohort_and_stratum": "Human IV ICU sedation PK (NDA021038 Precedex 0.2-0.7 ug/kg/h) & Talke et al. 1997 paired human lumbar CSF PK",
        "assay_and_contrast": "Measured human unbound plasma & lumbar CSF concentration vs 2,500 nM screen & ADRA2A Ki",
        "effect_direction": "SEVERE_6700_TO_10000X_MEASURED_HUMAN_CNS_GAP",
        "effect_estimate": "Cu,plasma=0.09-0.37 nM (NDA021038 fu=0.06) & measured human lumbar CSF ~0.20-0.35 nM (Talke 1997) vs 2,500 nM screen (~6,700-10,000x gap)",
        "notes": "FDA NDA021038 (Precedex, MW 200.28 g/mol, 94% bound -> fu=0.06) and Talke et al. 1997 Anesth Analg (PMID:9249114, PMID:9356115: human lumbar CSF ~4% +/- 1% of total plasma = ~0.25 nM) directly establish a ~6,700-10,000x human CNS gap without relying on a modeled Kpuu guess; sublingual Igalmi (NDA215390, 120-180 ug) causes 23% somnolence & 18% orthostasis at Cu,p ~0.18 nM.",
    })
    ev_map["EV-B6-033"].update({
        "source_type": "CLINICAL_SAFETY_LABEL_AND_CLASS_AUDIT",
        "source_id_or_locator": "OpenFDA:NDA021038;OpenFDA:NDA215390;PMID:33905493",
        "effect_estimate": "0 chronic dexmedetomidine ALS trials; ICU hypotension (25-54%) & bradycardia (5-14%) ceiling; oral alpha2 agonist guanabenz >30% ALS AE dropout",
        "notes": "Continuous IV monitoring required for hypotension, sinus bradycardia/arrest, and locus coeruleus sedation (NDA021038/NDA215390); oral alpha-2 agonist guanabenz in Phase 2 ALS ProMISe (Dalla Bella et al. 2021 Brain PMID:33905493) suffered >30% autonomic/sedative intolerability dropout.",
    })

    # S03 (Mycophenolate): NDA050722 97% binding (fu=0.03 -> Cu,p,avg ~375 nM), modeled ~15-55 nM Cu,brain (45-165x gap), Fournier 2018 PMID:29308669 4-drug regimen vs pretreatment lead-in p=0.200
    ev_map["EV-B6-038"].update({
        "source_id_or_locator": "OpenFDA:NDA050722;PMID:7903306;ChEMBL:CHEMBL866",
        "cohort_and_stratum": "Human 1,000 mg PO BID MMF transplant ceiling PK (NDA050722 CellCept) & Boxed/Section 5 Warnings",
        "effect_estimate": "Cu,plasma,avg ~310-470 nM (fu=0.03, 5.3-8.1x below 2.5 uM); [MODEL_PRIOR] anionic MPA Cu,brain ~15-55 nM (45-165x below 2.5 uM screen)",
        "notes": "FDA NDA050722 (CellCept) specifies 97% human albumin binding (fu=0.03; inactive phenolic glucuronide MPAG competes in uremia), placing Cu,plasma >35x above lymphoid IMPDH2 Ki (~7-10 nM, Carr et al. 1993 PMID:7903306) while OAT3/MRP-effluxed anionic MPA (pKa 4.5) remains 45-165x below 2.5 uM in brain; carries Boxed Warnings (embryofetal toxicity, lymphoma/malignancies, serious infections) plus Section 5 PML and severe neutropenia warnings.",
    })
    ev_map["EV-B6-039"].update({
        "source_type": "CLINICAL_TRIAL_OPEN_LABEL_PHASE2",
        "source_id_or_locator": "NCT01884571;PMID:29308669",
        "cohort_and_stratum": "Human open-label Phase 2 ALS 4-drug immunosuppression trial (Fournier et al. 2018: basiliximab + tacrolimus + MMF 1,000 mg BID + prednisone, N=31)",
        "assay_and_contrast": "Primary >=6-pt ALSFRS-R responder rate, ALSFRS-R slope vs pretreatment lead-in & AE dropouts",
        "effect_estimate": "0/31 responders; ALSFRS-R slope vs pretreatment lead-in p=0.200; 13/31 (42%) AE dropouts",
        "p_value": "0.2000",
        "notes": "Fournier et al. 2018 PMID:29308669 (NCT01884571, N=31) co-administered basiliximab, tacrolimus, MMF (1,000 mg BID), and prednisone: 0/31 met the primary responder criterion, within-patient ALSFRS-R slope did not slow vs pretreatment lead-in (p=0.200), and 42% discontinued for AEs (scoped to cytostatic IMPDH pan-lymphocyte ablation, distinct from low-dose IL-2 Treg expansion in S07).",
    })

    # S04 (Tamoxifen): Lien 1991 PMID:2021551 CAD trapping + active metabolites (~3-15 nM combined free CNS) + Tummino 2021 PMID:34326236 + Babu 2020 PMID:31608711 13.2% VTEs & Chen 2020 PMID:32481440
    ev_map["EV-B6-040"].update({
        "source_id_or_locator": "DS005_BYE:Table12:HY-13757A;ChEMBL:CHEMBL83;PMID:34326236",
        "notes": "Wilcoxon signed-rank p=0.00612; lipophilic cationic amphiphile (ALogP=6.00, pKa ~8.7) tested at 2.5 uM in low-protein BrainPhys media within the canonical CAD phospholipidosis regime (Tummino et al. 2021 Science PMID:34326236).",
    })
    ev_map["EV-B6-041"].update({
        "source_id_or_locator": "OpenFDA:NDA021807;PMID:2021551;PMID:34326236;ChEMBL:CHEMBL83",
        "cohort_and_stratum": "Human 20-80 mg/d PO steady-state PK (parent + N-desmethyltamoxifen + endoxifen), Lien 1991 brain partitioning & Soltamox NDA021807 Boxed Warning",
        "effect_estimate": "[MODEL_PRIOR] Parent Cu,brain ~2.6 nM (40 mg/d) & combined parent+metabolite free CNS ~3-15 nM (40-80 mg/d) vs 2,500 nM screen (165-800x gap)",
        "notes": "Although Lien et al. 1991 PMID:2021551 measured 40-100x higher total brain-to-serum tamoxifen/N-desmethyltamoxifen, >99.98% is sequestered in membrane lipid/lysosomes (fu,brain << 0.0002; thermodynamic passive Kpuu <=1), and CYP2D6 metabolite endoxifen is P-gp effluxed and ER-selective (not active on 3-10 uM PKC/CAD targets); NDA021807 carries Boxed Warnings for uterine malignancies, stroke, and pulmonary embolism.",
    })
    ev_map["EV-B6-042"].update({
        "source_type": "CLINICAL_TRIAL_SELECTION_RCT",
        "source_id_or_locator": "NCT01257581;PMID:31608711;NCT02166944;PMID:32481440;NCT00214110",
        "cohort_and_stratum": "Babu et al. 2020 38-wk 3-arm placebo-less selection RCT (NCT01257581, N=60: creatine 30 g/d n=22, tamoxifen 40 mg/d n=21, 80 mg/d n=17) & Chen 2020 RCT (N=18)",
        "assay_and_contrast": "ALSFRS-R decline, thromboembolic VTE safety & 12-mo RCT progression",
        "effect_estimate": "Babu 2020 untreated-rate ALSFRS-R slopes (-0.80 to -0.85 pts/mo) with 5/38 (13.2%) VTEs (2 PEs, 3 DVTs) & 4/17 (23.5%) T80 deaths; Chen 2020 12-mo ALSFRS-R null",
        "notes": "Babu et al. 2020 PMID:31608711 (NCT01257581, 38-wk selection RCT without placebo): T80 ranked first statistically but all arms declined at historical untreated rates with no SVC benefit and 5/38 (13.2%) tamoxifen VTEs (2 pulmonary embolisms, 3 DVTs); Chen et al. 2020 Medicine PMID:32481440 (NCT02166944, N=18 40 mg/d) and unpublished NCT00214110 (N=100) showed no durable 12-mo functional benefit.",
    })

    # S05 (Lonafarnib / Tipifarnib FTIs): clean NDA213969/NCT00005859 locators, [MODEL_PRIOR] tag, Tipifarnib 2-75 nM sensitive-substrate IC50
    ev_map["EV-B2-015"].update({
        "source_id_or_locator": "OpenFDA:NDA213969;NCT00005859;CHEMBL298734;CHEMBL289228",
        "effect_estimate": "Lonafarnib 150 mg/m2 Cmax,u<=42.2 nM, [MODEL_PRIOR] Cu,brain ~2.1-8.4 nM vs cell IC50 70-500 nM (Tipifarnib [MODEL_PRIOR] Cu,brain ~2-13 nM vs 2-75 nM Ras/lamin IC50)",
        "notes": "Lonafarnib (NDA213969 Zokinvy, MW 638.82 Da, PPB>=99%, marginal P-gp substrate) and Tipifarnib (MW 489.40 Da, PPB>99%, NABTC glioma NCT00005859) face an 8-100x free-brain deficit for lonafarnib while tipifarnib's sensitive-substrate window hits dose-limiting myelosuppression and neuropathy.",
    })
    ev_map["EV-B2-016"].update({
        "source_id_or_locator": "OpenFDA:NDA213969;CHEMBL298734;CHEMBL289228",
        "cohort_and_stratum": "Zokinvy NDA213969 Phase 2 pooled safety (N=63), TQT study (N=64), FDA FAERS & Tipifarnib oncology trials",
        "notes": "NDA213969 Table 4 & Sec 12.2: 90% vomiting, 81% diarrhea, 37% weight loss (prognostically lethal in ALS), 35% myelosuppression/transaminases, +19 ms QTcF, and CYP3A autoinhibition (+639% midazolam AUC); Tipifarnib causes Grade 3/4 neutropenia, thrombocytopenia, and sensory neuropathy.",
    })
