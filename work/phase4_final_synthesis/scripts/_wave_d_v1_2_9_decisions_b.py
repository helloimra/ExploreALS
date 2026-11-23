"""Wave D v1.2.9 decision prose updates Part B for registries/candidate_decisions.csv (C011, C021, S01, S03, S04, S05)."""
from __future__ import annotations

TS_WAVE_D = "2026-11-22T01:20:00Z"


def apply_wave_d_decision_patches_b(dm: dict[str, dict[str, str]]) -> None:
    dm["C011"].update({
        "evidence_proves_hypothesis": (
            "Nominated from observational healthcare-claims & PRO-ACT analyses in Saez-Atienzar et al. 2026 (DOI:10.1038/s41746-026-03225-w: observational PRO-ACT comparison of 18 vs 90 matched patients reported slower ALSFRS-R slope decline p=0.02 [Fig. S2] and improved survival p=0.024 [Fig. S3]; separate observational Medicare case-control ALS incidence OR=0.75, p=4.99e-10 [Table S5]) alongside 100 uM mouse midbrain slice experiments "
            "proposing NKCC1 (SLC12A2) inhibition to lower neuronal intracellular [Cl-]; untested (not in 107-drug library) in Bye 2025 iPSC-MN screen and 0 ALS RCTs conducted."
        ),
        "evidence_disproves_hypothesis": (
            "At oral 40 mg (NDA016273 Lasix: MW 330.74, 91-99% albumin bound -> Cu,plasma ~30-150 nM), active BBB/choroid-plexus OAT3/MRP4 efflux restricts [MODEL_PRIOR] Cu,CNS to <1-5 nM — "
            ">1,000-5,800x below Hampel et al. 2018 (PMID:29959396 Table 1) human oocyte hNKCC1A IC50=5.15 uM & hNKCC1B=5.82 uM (~18-23 uM in native cells, Table 2; even Cu,plasma is 34-190x too low) — "
            "while furosemide non-selectively inhibits protective neuronal Cl- extruder KCC2 (SLC12A5, already depleted in sALS iPSC-MNs padj=0.0486 & NYGC cervical cord beta=-0.595, p=0.0342), "
            "inhibits CA2/CA1 at Ki ~65-200 nM, reduced human soleus D1 Ia presynaptic (p=0.037) and sural cutaneous inhibition (p=0.034) in Klomjai et al. 2014 (PMID:24835171, PMC4221825), and carries Boxed Warning diuretic/electrolyte dehydration toxicity."
        ),
        "factual_justification": (
            "Excluded on modeled human unbound CNS exposure and KCC2/CA non-selectivity (clinical ALS efficacy untested across 0 ALS RCTs, alongside observational PRO-ACT 18 vs 90 ALSFRS-R slope p=0.02 [Fig. S2] & survival p=0.024 [Fig. S3] and separate Medicare ALS incidence OR=0.75 [Table S5] signals in DOI:10.1038/s41746-026-03225-w): >1,000-5,800x [MODEL_PRIOR] human unbound CNS exposure deficit (<1-5 nM OAT3/MRP4-effluxed CNS & 30-150 nM Cu,plasma vs human hNKCC1A/B IC50=5.15-5.82 uM in Hampel et al. 2018 PMID:29959396 Table 1) "
            "bounded by NDA016273 loop-diuretic dehydration/hypokalemia, compounded by counterproductive KCC2/CA1-2 co-inhibition and reduced human spinal D1 Ia presynaptic & sural cutaneous inhibition (Klomjai et al. 2014 PMID:24835171; scoped strictly to systemic furosemide, preserving brain-penetrant NKCC1-sparing KCC2 enhancers)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["C021"].update({
        "causal_vs_reactive_assessment": "DISPUTED_PPP1R15A_TARGET_WITH_SEVERE_PK_AND_SAFETY_LIMITATIONS: Negative reconstituted PPP1R15A-PP1c tests & disputed target interpretation, 41-71x group plasma Cmax gap under studied 25 mg BID / HV regimens, and Phase 2 fatal TEAE/fall imbalance",
        "evidence_disproves_hypothesis": (
            "Chemical registry audit refuted misattributed IDs (verified Sephin1=CHEMBL2365743 / CID:9561611, free-base MW 196.64, acetate MW 256.69); "
            "reconstituted biochemical assays reported negative direct PPP1R15A-PP1c holophosphatase inhibition with disputed primary target interpretation (Crespillo-Casado et al. 2017/2018 PMID:28447936, PMID:29618508; while early rat motor-neuron mutant SOD1 cultures reported 10-50 nM rescue, characterized human cellular effects include 1-5 uM GluN2B NAM [Abgueguen et al. 2026 PMID:43036320] & PHB2 [Ding et al. 2026 PMID:42790826], failing SOD1-G93A mice in Vieira et al. 2024 PMID:38359044); "
            "in Phase 2 NCT05508074 (N=51 bulbar-onset ALS [88.2% sporadic], 25 mg BID + riluzole; CL/F=580 L/h in ALS, 736-1,388 L/h in HV Ph1; absolute oral bioavailability and CNS exposure ceiling unresolved), total plasma peak under the studied oral regimens was a geometric mean Cmax of 12.0 ng/mL (61.0 nM) in ALS (NCT05508074) and an arithmetic mean Cmax of 6.92 ng/mL (35.2 nM) in healthy volunteers (NCT03610334, 50 mg MAD group at Dose 2, n=6; 41-71x below 2.5 uM in total plasma; [MODEL_PRIOR] Cu,brain ~5-20 nM = 125-500x gap) "
            "with flat plasma GDF15 (~704 pg/mL posted under CT.gov ng/mL header), null ITT ALSFRS-R (-0.33, p=0.923; N=51 size limits clinical efficacy precision) & NfL ratio 1.04 (p=0.609), and 5/34 (14.7%) vs 2/17 (11.8%) total fatal TEAEs including 2/34 (5.9% vs 0%) investigator-assessed possibly drug-related sudden/cardiac fatal TEAEs and 8/34 (23.5% vs 0%) falls."
        ),
        "factual_justification": (
            "Excluded on low human plasma exposure under studied oral regimens, disputed primary target biochemistry, and Phase 2 safety signals: under the studied oral regimens (25 mg BID ALS CL/F=580 L/h; HV Ph1 CL/F=736-1,388 L/h; absolute oral bioavailability and a CNS exposure ceiling remain unresolved), total plasma peak was a geometric mean Cmax of 12.0 ng/mL (61.0 nM) in ALS (NCT05508074) and an arithmetic mean Cmax of 6.92 ng/mL (35.2 nM) in healthy volunteers (NCT03610334, 50 mg MAD group at Dose 2, n=6; 41-71x below nominal 2.5 uM even before protein binding; [MODEL_PRIOR] Cu,brain ~5-20 nM = 125-500x below 2.5 uM & 1-5 uM GluN2B/PHB2 activity, PMID:28447936, PMID:43036320) "
            "with flat human GDF15 and null ITT ALSFRS-R (p=0.923) / NfL (p=0.609) in bulbar-onset Phase 2 NCT05508074 (N=51, 88.2% sporadic; trial size limits standalone efficacy precision), while 25 mg BID recorded 2/34 (5.9% vs 0%) possibly drug-related sudden/cardiac fatal TEAEs (5/34 vs 2/17 all-cause) and 23.5% falls."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["S01"].update({
        "evidence_disproves_hypothesis": (
            "Talke et al. 1997 paired human total plasma and lumbar CSF PK (PMID:9356115: measured ~0.20-0.35 nM total lumbar CSF = ~4% of measured total plasma; ~7,143-12,500x below the nominal 2,500 nM screen; companion CSF pressure study PMID:9249114) "
            "and FDA NDA021038 (Precedex IV ICU infusion 0.2-0.7 ug/kg/h, MW 200.28: estimated unbound plasma 0.09-0.37 nM, assuming 94% binding [fu~0.06, MODEL_PRIOR], ~6,757-27,778x below 2,500 nM; sublingual Igalmi NDA215390 23% somnolence / 18% orthostasis at estimated Cu,p ~0.18 nM) show tolerated human CNS exposure sits >7,000x below the nominal 2.5 uM screen dose (minimum effective iPSC-MN concentration unmeasured) "
            "and is gated by ADRA2A locus coeruleus unconsciousness, hypotension (25-54%), and sinus bradycardia/arrest (Ki ~1-2 nM; ADRA2A/B/C non-DE in Bye RNA-seq; oral alpha-2 agonist guanabenz had >30% ALS AE dropout in Phase 2 ProMISe, PMID:33905493)."
        ),
        "factual_justification": (
            "Despite genuine 2.5 uM iPSC-MN rescue (+1.399d, q=0.0303; minimum effective screen concentration unmeasured), directly measured human lumbar CSF (~0.20-0.35 nM, ~4% of measured total plasma, ~7,143-12,500x below nominal 2.5 uM, Talke et al. 1997 PMID:9356115; companion CSF pressure PMID:9249114) and estimated unbound plasma 0.09-0.37 nM, assuming 94% binding [MODEL_PRIOR] (~6,757-27,778x below 2.5 uM, NDA021038), "
            "are capped by dose-limiting central alpha-2A sedation, hypotension, and bradycardia (corroborated by >30% oral alpha-2 intolerability in ALS ProMISe, PMID:33905493)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["S03"].update({
        "evidence_disproves_hypothesis": (
            "At 1,000 mg PO BID transplant ceiling (NDA050722 CellCept: active MPA MW 320.34 is 97% albumin-bound, fu=0.03), human Cu,plasma,avg (~310-470 nM) sits 5.3-8.1x below 2.5 uM while >35x above lymphoid IMPDH2 Ki (~7-10 nM, PMID:7903306), "
            "and OAT3/MRP-effluxed anionic MPA (pKa 4.5) yields [MODEL_PRIOR] Cu,brain ~15-55 nM (45-165x below 2.5 uM neuronal screen); carries FDA Boxed Warnings (embryofetal toxicity, lymphoma/malignancies, serious infections) plus Section 5 PML/neutropenia warnings, "
            "and open-label Phase 2 ALS 4-drug immunosuppression trial NCT01884571 (Fournier et al. 2018 PMID:29308669: basiliximab + tacrolimus + MMF + prednisone, N=31) had 0/31 responders, no ALSFRS-R slowing vs pretreatment lead-in (p=0.200), and only 18/31 (58%) completing the treatment regimen (23/31 [74%] completing the study; 1 AE withdrawal, 2 deaths, 2 patient withdrawals, 3 disease-progression stops)."
        ),
        "factual_justification": (
            "Active mycophenolic acid faces a 45-165-fold [MODEL_PRIOR] human unbound CNS deficit (~15-55 nM vs 2,500 nM screen; 97% albumin binding fu=0.03, NDA050722, Cu,plasma ~310-470 nM) bounded by peripheral IMPDH2 cytostasis (Ki ~7-10 nM, PMID:7903306), "
            "FDA Boxed Warnings (serious infections, lymphoma, teratogenicity) + Section 5 PML risk, and 0/31 responders (p=0.200 vs pretreatment lead-in; 18/31 regimen completers, 23/31 study completers) in 4-drug ALS trial NCT01884571 (PMID:29308669; scoped to pan-lymphocyte IMPDH ablation, preserving low-dose IL-2 Treg expansion)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["S04"].update({
        "causal_vs_reactive_assessment": "UNTESTED_MICROMOLAR_CAD_PHOSPHOLIPIDOSIS_HYPOTHESIS: Plausible untested cationic-amphiphilic phospholipidosis/PKC regime at 2.5 uM vs ~3-15 nM [MODEL_PRIOR] unbound CNS PK",
        "evidence_disproves_hypothesis": (
            "Although total brain tamoxifen is 40-100x serum due to membrane/lysosomal lipid trapping (Lien et al. 1991 PMID:2021551, fu,brain <<0.0002; cLogP ~6.0-6.3, >99% bound), "
            "[MODEL_PRIOR] unbound aqueous brain exposure at 40-80 mg/d (~2.6 nM parent; ~3-15 nM combined with N-desmethyltamoxifen & P-gp-effluxed endoxifen) sits 165-800x below the 2.5 uM screen (where cationic-amphiphilic phospholipidosis/PKC modulation in low-protein media is a plausible untested hypothesis, Tummino et al. 2021 Science PMID:34326236); "
            "carries NDA021807 Boxed Warnings (stroke, pulmonary embolism, uterine malignancies), recorded 2 pulmonary embolisms and 3 DVTs (event-level counts across 38 tamoxifen-treated participants) plus 4/17 (23.5%) T80 deaths with untreated-rate ALSFRS-R decline in 38-wk placebo-less selection RCT NCT01257581 (Babu et al. 2020 PMID:31608711, N=60), "
            "and showed transient 3- and 6-mo differences attenuating to null at 12 mo in Chen et al. 2020 (PMID:32481440, NCT02166944, N=18) alongside conference-reported dose-comparison study NCT00214110 (N=100, unpublished in peer-reviewed full text)."
        ),
        "factual_justification": (
            "Combined parent + active metabolite [MODEL_PRIOR] unbound human brain exposure (~3-15 nM at 40-80 mg/d; Lien et al. 1991 PMID:2021551 lipid trapping) is 165-800-fold below the 2.5 uM screen concentration (plausibly an untested cationic-amphiphilic phospholipidosis/PKC regime, Tummino et al. 2021 PMID:34326236), "
            "bounded by FDA Boxed Warnings (stroke, PE, uterine malignancy), thromboembolic events (2 PE and 3 DVT events across 38 tamoxifen recipients) in ALS selection RCT NCT01257581 (Babu et al. 2020 PMID:31608711, N=60), null 12-mo endpoint in Chen et al. 2020 (PMID:32481440, N=18), and unpublished NCT00214110 (N=100)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["S05"].update({
        "evidence_disproves_hypothesis": (
            "Excluded on modeled CNS exposure, clinical tolerability, and predicted YKT6 prenylation antagonism (untested — not in 107-drug library — in Bye 2025 screen): (1) Predicted directional liability: although sub-stoichiometric FTIs improved synucleinopathy/tauopathy models via Rhes/closed-YKT6 modulation (Cuddy et al. 2019 PMID:31648898; Hernandez et al. 2019 PMID:30918111), human GGTase-III (PTAR1/RABGGTB, PDB 6J74 PMID:32128853; Sakata et al. 2021 PMID:33035318) biochemically requires prior FTase Cys195 farnesylation to geranylgeranylate YKT6 Cys194 for Golgi/lysosomal trafficking (pan-essential DepMap Chronos=-1.5425), "
            "predicting that FTIs would impair YKT6 diprenylation in TDP-43-depleted ALS neurons already carrying YKT6 APA (padj=4.57e-40) + PTAR1 170-bp Exon-2 frameshift skipping (chr9:69750781-69750950(-), mod_3=2, MOESM11 line 4145 group E(PSI) 0.156->0.369 [MAJIQ shrunk dPSI=+0.1563], source MAJIQ 'FDR' [p_d_psi_0.05]=3.256e-6; direct FTI testing in ALS neurons remains unperformed); "
            "(2) Unbound CNS PK deficit: Lonafarnib (NDA213969, MW 638.82, PPB>=99%) achieves Cmax,u<=42.2 nM at 150 mg/m2 BID and [MODEL_PRIOR] Cu,brain ~2.1-8.4 nM vs 70-500 nM cellular IC50 (Tipifarnib [MODEL_PRIOR] Cu,brain ~2-13 nM vs 2-75 nM sensitive-substrate IC50); "
            "(3) ALS-hostile human toxicity: Zokinvy Table 4 (N=63 pediatric Hutchinson-Gilford progeria patients at 150 mg/m2 BID) records 90% vomiting, 81% diarrhea, 37% weight loss (prognostically deleterious in ALS), 35% myelosuppression, +19 ms QTcF, and strong CYP3A autoinhibition, while Tipifarnib oncology regimens cause dose-limiting Grade 3/4 myelosuppression and neuropathy (Crul et al. 2002 PMID:12039935)."
        ),
        "factual_justification": (
            "Excluded on [MODEL_PRIOR] human unbound CNS exposure limits (Lonafarnib Cu,brain ~2-8 nM vs 70-500 nM cellular IC50; Tipifarnib ~2-13 nM, NDA213969), "
            "ALS-hostile clinical toxicities (pediatric progeria Zokinvy label: 37% weight loss, 81-90% GI toxicity, 35% myelosuppression, +19 ms QTcF; oncology Tipifarnib myelosuppression/neuropathy DLT PMID:12039935; untested in Bye 2025 screen), "
            "and predicted biochemical antagonism of sequential FTase Cys195 -> GGTase-III Cys194 dual prenylation on YKT6 (PDB 6J74 PMID:32128853; untested directly in ALS neurons) atop TDP-43 PTAR1 170-bp Exon-2 skipping (despite mouse tauopathy FTI rescue PMID:30918111; preserving pro-prenylation YKT6/PTAR1 rescue in C023)."
        ),
        "updated_at": TS_WAVE_D,
    })
