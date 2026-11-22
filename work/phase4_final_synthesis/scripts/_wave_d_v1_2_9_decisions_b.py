"""Wave D v1.2.9 decision prose updates Part B for registries/candidate_decisions.csv (C011, C021, S01, S03, S04, S05)."""
from __future__ import annotations

TS_WAVE_D = "2026-11-22T01:20:00Z"


def apply_wave_d_decision_patches_b(dm: dict[str, dict[str, str]]) -> None:
    dm["C011"].update({
        "evidence_proves_hypothesis": (
            "Nominated from observational healthcare-claims/MR screening (DOI:10.1038/s41746-026-03225-w) and 100 uM rodent spinal slice experiments "
            "proposing NKCC1 (SLC12A2) inhibition to lower neuronal intracellular [Cl-]; absent (0/107) from Bye 2025 iPSC-MN drug screen."
        ),
        "evidence_disproves_hypothesis": (
            "At oral 40 mg (NDA016273 Lasix: MW 330.74, 91-99% albumin bound -> Cu,plasma ~30-150 nM), active BBB/choroid-plexus OAT3/MRP4 efflux restricts [MODEL_PRIOR] Cu,CNS to <1-5 nM — "
            ">1,000-5,800x below Hampel et al. 2018 (PMID:29959396 Table 1) human oocyte hNKCC1A IC50=5.15 uM & hNKCC1B=5.82 uM (~18-23 uM in native cells, Table 2; even Cu,plasma is 34-190x too low) — "
            "while furosemide non-selectively inhibits protective neuronal Cl- extruder KCC2 (SLC12A5, already depleted in sALS iPSC-MNs padj=0.0486 & NYGC cervical cord beta=-0.595, p=0.0342), "
            "inhibits CA2/CA1 at Ki ~65-200 nM, reduced human soleus D1 Ia presynaptic (p=0.037) and sural cutaneous inhibition (p=0.034) in Klomjai et al. 2014 (PMID:24835171, PMC4221825), and carries Boxed Warning diuretic/electrolyte dehydration toxicity."
        ),
        "factual_justification": (
            "Falsified by a >1,000-5,800x [MODEL_PRIOR] human unbound CNS exposure deficit (<1-5 nM OAT3/MRP4-effluxed CNS & 30-150 nM Cu,plasma vs human hNKCC1A/B IC50=5.15-5.82 uM in Hampel et al. 2018 PMID:29959396 Table 1) "
            "bounded by NDA016273 loop-diuretic dehydration/hypokalemia, compounded by counterproductive KCC2/CA1-2 co-inhibition and reduced human spinal D1 Ia presynaptic & sural cutaneous inhibition (Klomjai et al. 2014 PMID:24835171; scoped strictly to systemic furosemide, preserving brain-penetrant NKCC1-sparing KCC2 enhancers)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["C021"].update({
        "evidence_disproves_hypothesis": (
            "Chemical registry audit refuted misattributed IDs (verified Sephin1=CHEMBL2365743 / CID:9561611, free-base MW 196.64, acetate MW 256.69); "
            "direct PPP1R15A-PP1c holophosphatase inhibition was biochemically refuted (Crespillo-Casado et al. 2017/2018 PMID:28447936, PMID:29618508; cellular activity reflects 1-5 uM GluN2B NAM [Abgueguen et al. 2026 PMID:43036320] & PHB2 [Ding et al. 2026 PMID:42790826], failing SOD1-G93A mice in Vieira et al. 2024 PMID:38359044); "
            "in Phase 2 NCT05508074 (N=51 bulbar ALS, 25 mg BID + riluzole), extreme apparent oral clearance (CL/F=580 L/h; Ph1 736-1,388 L/h) capped measured total plasma GeoMean Cmax at 12.0 ng/mL = 61.0 nM (Ph1 35.2 nM — already 41-71x below 2.5 uM in total plasma; [MODEL_PRIOR] Cu,brain ~5-20 nM = 125-500x gap) "
            "with flat plasma GDF15 (~704 pg/mL posted under CT.gov ng/mL header), null ITT ALSFRS-R (-0.33, p=0.923) & NfL ratio 1.04 (p=0.609), and 5/34 (14.7%) vs 2/17 (11.8%) total fatal TEAEs including 2/34 (5.9% vs 0%) drug-related fatal TEAEs and 8/34 (23.5% vs 0%) falls."
        ),
        "factual_justification": (
            "Falsified by a non-closable human PK/safety wall and refuted primary target: extreme oral clearance (CL/F=580-1,388 L/h) caps measured human total plasma Cmax at 35.2-61.0 nM (41-71x below 2.5 uM even before protein binding; [MODEL_PRIOR] Cu,brain ~5-20 nM = 125-500x below 2.5 uM & 1-5 uM GluN2B/PHB2 activity, PMID:28447936, PMID:43036320) "
            "with flat human GDF15 and null ITT ALSFRS-R (p=0.923) / NfL (p=0.609) in Phase 2 NCT05508074 (N=51), while 25 mg BID already recorded 2/34 (5.9% vs 0%) drug-related fatal TEAEs (5/34 vs 2/17 all-cause) and 23.5% falls."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["S01"].update({
        "evidence_disproves_hypothesis": (
            "FDA NDA021038 (Precedex IV ICU infusion 0.2-0.7 ug/kg/h, MW 200.28, 94% bound -> Cu,plasma=0.09-0.37 nM; sublingual Igalmi NDA215390 23% somnolence / 18% orthostasis at Cu,p ~0.18 nM) "
            "and Talke et al. 1997 paired human lumbar CSF PK (PMID:9249114, PMID:9356115: ~0.20-0.35 nM CSF) prove tolerated human CNS exposure sits ~6,700-10,000x below the 2,500 nM screen "
            "and is gated by ADRA2A locus coeruleus unconsciousness, hypotension (25-54%), and sinus bradycardia/arrest (Ki ~1-2 nM; ADRA2A/B/C non-DE in Bye RNA-seq; oral alpha-2 agonist guanabenz had >30% ALS AE dropout in Phase 2 ProMISe, PMID:33905493)."
        ),
        "factual_justification": (
            "Despite genuine 2.5 uM iPSC-MN rescue (+1.399d, q=0.0303), directly measured human unbound plasma (0.09-0.37 nM, NDA021038) and human lumbar CSF (~0.20-0.35 nM, Talke et al. 1997 PMID:9249114) "
            "sit ~6,700-10,000-fold below the 2.5 uM screen concentration and are capped by dose-limiting central alpha-2A sedation, hypotension, and bradycardia (corroborated by >30% oral alpha-2 intolerability in ALS ProMISe, PMID:33905493)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["S03"].update({
        "evidence_disproves_hypothesis": (
            "At 1,000 mg PO BID transplant ceiling (NDA050722 CellCept: active MPA MW 320.34 is 97% albumin-bound, fu=0.03), human Cu,plasma,avg (~310-470 nM) sits 5.3-8.1x below 2.5 uM while >35x above lymphoid IMPDH2 Ki (~7-10 nM, PMID:7903306), "
            "and OAT3/MRP-effluxed anionic MPA (pKa 4.5) yields [MODEL_PRIOR] Cu,brain ~15-55 nM (45-165x below 2.5 uM neuronal screen); carries FDA Boxed Warnings (embryofetal toxicity, lymphoma/malignancies, serious infections) plus Section 5 PML/neutropenia warnings, "
            "and open-label Phase 2 ALS 4-drug immunosuppression trial NCT01884571 (Fournier et al. 2018 PMID:29308669: basiliximab + tacrolimus + MMF + prednisone, N=31) had 0/31 responders, no ALSFRS-R slowing vs pretreatment lead-in (p=0.200), and 42% AE dropouts."
        ),
        "factual_justification": (
            "Active mycophenolic acid faces a 45-165-fold [MODEL_PRIOR] human unbound CNS deficit (~15-55 nM vs 2,500 nM screen; 97% albumin binding fu=0.03, NDA050722, Cu,plasma ~310-470 nM) bounded by peripheral IMPDH2 cytostasis (Ki ~7-10 nM, PMID:7903306), "
            "FDA Boxed Warnings (serious infections, lymphoma, teratogenicity) + Section 5 PML risk, and 0/31 responders (p=0.200 vs pretreatment lead-in, 42% AE dropouts) in 4-drug ALS trial NCT01884571 (PMID:29308669; scoped to pan-lymphocyte IMPDH ablation, preserving low-dose IL-2 Treg expansion)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["S04"].update({
        "evidence_disproves_hypothesis": (
            "Although total brain tamoxifen is 40-100x serum due to membrane/lysosomal lipid trapping (Lien et al. 1991 PMID:2021551, fu,brain <<0.0002; cLogP ~6.0-6.3, >99% bound), "
            "[MODEL_PRIOR] unbound aqueous brain exposure at 40-80 mg/d (~2.6 nM parent; ~3-15 nM combined with N-desmethyltamoxifen & P-gp-effluxed endoxifen) sits 165-800x below the 2.5 uM screen (a canonical cationic-amphiphilic phospholipidosis/PKC regime in low-protein media, Tummino et al. 2021 Science PMID:34326236); "
            "carries NDA021807 Boxed Warnings (stroke, pulmonary embolism, uterine malignancies), caused 5/38 (13.2%) VTEs (2 PEs, 3 DVTs) & 4/17 (23.5%) T80 deaths with untreated-rate ALSFRS-R decline in 38-wk placebo-less selection RCT NCT01257581 (Babu et al. 2020 PMID:31608711, N=60), "
            "and showed no durable 12-mo benefit in Chen et al. 2020 (PMID:32481440, NCT02166944, N=18) or NCT00214110 (N=100)."
        ),
        "factual_justification": (
            "Combined parent + active metabolite [MODEL_PRIOR] unbound human brain exposure (~3-15 nM at 40-80 mg/d; Lien et al. 1991 PMID:2021551 lipid trapping) is 165-800-fold below the 2.5 uM in vitro cationic-amphiphilic phospholipidosis/PKC regime (Tummino et al. 2021 PMID:34326236), "
            "bounded by FDA Boxed Warnings (stroke, PE, uterine malignancy), 13.2% (5/38: 2 PE, 3 DVT) thromboembolism in ALS selection RCT NCT01257581 (Babu et al. 2020 PMID:31608711, N=60), and negative 12-mo ALS trials (PMID:32481440, NCT00214110)."
        ),
        "updated_at": TS_WAVE_D,
    })

    dm["S05"].update({
        "evidence_disproves_hypothesis": (
            "Falsified on three independent axes (0/107 in Bye 2025 screen): (1) Directional paradox: although sub-stoichiometric FTI (LNK-754) relieved alpha-synuclein-trapped closed YKT6 in PD models (Cuddy et al. 2019 PMID:31648898), human GGTase-III (PTAR1/RABGGTB, PDB 6J74 PMID:32128853; Sakata et al. 2021 PMID:33035318) strictly requires prior FTase Cys195 farnesylation to geranylgeranylate YKT6 Cys194 for Golgi/lysosomal trafficking (pan-essential DepMap Chronos=-1.5425), "
            "so in TDP-43-depleted ALS neurons already suffering YKT6 APA (padj=4.57e-40) + PTAR1 170-bp Exon-2 frameshift skipping (chr9:69750781-69750950(-), mod_3=2, dPSI=+0.1563, FDR=3.26e-6), FTIs worsen YKT6 diprenylation failure; "
            "(2) Unbound CNS PK deficit: Lonafarnib (NDA213969, MW 638.82, PPB>=99%) achieves Cmax,u<=42.2 nM at 150 mg/m2 BID and [MODEL_PRIOR] Cu,brain ~2.1-8.4 nM vs 70-500 nM cellular IC50 (Tipifarnib [MODEL_PRIOR] Cu,brain ~2-13 nM vs 2-75 nM sensitive-substrate IC50); "
            "(3) ALS-hostile human toxicity: Zokinvy Table 4 (N=63) records 90% vomiting, 81% diarrhea, 37% weight loss (prognostically lethal in ALS), 35% myelosuppression, +19 ms QTcF, and strong CYP3A autoinhibition, while Tipifarnib causes Grade 3/4 myelosuppression and neuropathy."
        ),
        "factual_justification": (
            "Dropped due to [MODEL_PRIOR] human unbound CNS exposure deficit (Lonafarnib Cu,brain ~2-8 nM vs 70-500 nM cellular IC50; Tipifarnib ~2-13 nM, NDA213969), "
            "ALS-hostile clinical toxicities (37% weight loss, 81-90% GI toxicity, 35% myelosuppression, +19 ms QTcF, neuropathic DLT; 0 Bye 2025 screen rows), "
            "and direct mechanistic antagonism of mandatory FTase Cys195 -> GGTase-III Cys194 dual prenylation on YKT6 (PDB 6J74 PMID:32128853) atop TDP-43 PTAR1 170-bp Exon-2 skipping (preserving pro-prenylation YKT6/PTAR1 rescue in C023)."
        ),
        "updated_at": TS_WAVE_D,
    })
