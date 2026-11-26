"""Curated faceted-bullet & paragraph splits for Candidate Dossier cards — Part B (Ranks #30–#52) + token-conservation verifier."""
from __future__ import annotations

import re

from _dossier_card_splits_a import CARD_SPLITS_A

CARD_SPLITS_B: dict[tuple[str, str], list[tuple[str, str]]] = {
    ("EALS-013", "proves"): [
        ("FDA/EMA-approved ALS survival standard of care", "- Pivotal Human ALS Survival RCTs: FDA/EMA-approved ALS survival standard of care"),
        ("p=0.002) and Rank #1/107 hit", "p=0.002).\n- Mature Patient iPSC-MN Screen Benchmark: Rank #1/107 hit"),
        ("Separately, in a TDP-43-depleted", "\n- Cortical i3Neuron SCN8A Exon 5N->5A Shift: In a TDP-43-depleted"),
        ("PMID:38771640); any mechanistic connection", "PMID:38771640).\n- Unproven Link to Riluzole Response: Any mechanistic connection"),
    ],
    ("EALS-013", "disproves"): [
        ("Established background standard-of-care reference", "- Standard-of-Care Reference Scope: Established background standard-of-care reference"),
        ("discovery candidate; at 50 mg oral BID", "discovery candidate.\n- Unbound Human CNS Exposure vs. Screen Concentration: At 50 mg oral BID"),
    ],
    ("EALS-032", "proves"): [
        ("Phase 3 JETALS RCT (", "- Phase 3 JETALS Early-Onset Efficacy: Phase 3 JETALS RCT ("),
        ("concomitant riluzole) and lowered plasma homocysteine", "concomitant riluzole).\n- Homocysteine Lowering & Japan MHLW Approval: Lowered plasma homocysteine"),
    ],
    ("EALS-032", "disproves"): [
        ("Prior broad-window (<=3 yr onset)", "- Broad-Window Trial Miss & Regional Regulatory Scope: Prior broad-window (<=3 yr onset)"),
        ("US/EU Phase 3 trials), and unshielded 2.5 uM", "US/EU Phase 3 trials).\n- Live-Imaging Photolysis Artifact in iPSC-MN Screening: Unshielded 2.5 uM"),
    ],
    ("EALS-003", "proves"): [
        ("Human ALS Phase 2 physiological RCT", "- Cortical TMS SICI Engagement in ALS RCT: Human ALS Phase 2 physiological RCT"),
        ("faster progression) and Kovalchuk 2018", "faster progression).\n- Acute Peripheral Axonal SDTC Engagement: Kovalchuk 2018"),
    ],
    ("EALS-003", "disproves"): [
        ("Specific chemical entity voluntarily discontinued", "- Commercial Withdrawal & Retinal/Pigmentation Boxed Warning: Specific chemical entity voluntarily discontinued"),
        ("tissue pigmentation), caused 30.4%", "tissue pigmentation).\n- ALS Trial Dropout & Sub-FDR Screen Readout: Caused 30.4%"),
        ("q=0.1890), and is superseded in ALS", "q=0.1890).\n- Non-Pigmenting Kv7 Follow-On Landscape: Superseded in ALS"),
    ],
    ("EALS-017", "proves"): [
        ("Individual protein associations across Trautwig", "- Multi-Center CSF & Clinical Immunoassay Associations: Individual protein associations across Trautwig"),
        ("Steinacker 2018 PMID:29142138), NYGC spinal cord", "Steinacker 2018 PMID:29142138).\n- CNS Spatial/Tissue Expression & Candidate Panel Scope: Together with NYGC spinal cord"),
    ],
    ("EALS-017", "disproves"): [
        ("Natural human CHIT1 null homozygosity", "- Human CHIT1 Null Genetics & Neuroprotective GPNMB Direction: Natural human CHIT1 null homozygosity"),
        ("lack catalytic activity, and individual case-control", "lack catalytic activity.\n- Unvalidated Fixed 4-Protein Panel Claims: Individual case-control"),
    ],
    ("EALS-043", "proves"): [
        ("Top downregulated untargeted CSF protein", "- Untargeted Emory CSF DIA Depletion: Top downregulated untargeted CSF protein"),
        ("Fig. 7a), directionally concordant in WashU", "Fig. 7a).\n- WashU Bank Caveat & Synaptosomal Concordance: Directionally concordant in WashU"),
    ],
    ("EALS-044", "proves"): [
        ("Passes single-center Emory CSF DIA FDR", "- Emory & WashU CSF DIA Depletion: Passes single-center Emory CSF DIA FDR"),
        ("32/78 bank count]), sub-FDR postmortem BA4", "32/78 bank count]).\n- Cortical Neuronal snRNA & Synaptosomal Trends: Sub-FDR postmortem BA4"),
    ],
    ("EALS-045", "proves"): [
        ("Sole upregulated untargeted CSF protein", "- Multi-Center DIA & TMTpro CSF Elevation: Sole upregulated untargeted CSF protein"),
        ("PMID:40375307); Jagaraj et al. 2026", "PMID:40375307).\n- Postmortem Spinal MN Ser3 Hyperphosphorylation: Jagaraj et al. 2026"),
    ],
    ("EALS-004", "disproves"): [
        ("Phase 3 Stage 3 RCT NCT00349622", "- Phase 3 Futility & Hepatobiliary Toxicity: Phase 3 Stage 3 RCT NCT00349622"),
        ("vs 0/173 (0%); CHEMBL161 HTS records", "vs 0/173 (0%).\n- Weak Human EAAT2 Potency & Absent Astrocyte Deficit: CHEMBL161 HTS records"),
    ],
    ("EALS-008", "verdict"): [
        ("Consistent human clinical futility across three", "- Three Negative Placebo-Controlled ALS RCTs: Consistent human clinical futility across three"),
        ("\n\nDouble-dose 40 mg/d Phase 2b TAME", "\n- Phase 2b TAME 40 mg/d & Biomarker Nulls: Double-dose 40 mg/d Phase 2b TAME"),
        ("\n\nMEDALS (", "\n- MEDALS, Exploratory Studies & Plausible CSF Exposure: MEDALS ("),
    ],
    ("EALS-008", "disproves"): [
        ("Failed three randomized placebo-controlled human ALS trials: Phase 3 MND-SMART", "- Phase 3 MND-SMART Stage 2 ALSFRS-R Futility: Failed three randomized placebo-controlled human ALS trials: Phase 3 MND-SMART"),
        ("one-sided p=0.36; descriptive follow-up deaths", "one-sided p=0.36).\n- MND-SMART Follow-Up Survival Reporting: Descriptive follow-up deaths"),
        ("prior to Stage 4, Fig. 4).", "prior to Stage 4, Fig. 4."),
        ("\n\nDouble-dose Phase 2b TAME at 40 mg/d", "\n- Phase 2b TAME 40 mg/d Clinical Nulls: Double-dose Phase 2b TAME at 40 mg/d"),
        ("duration+FVC-adjusted; Table 3 blood NfL", "duration+FVC-adjusted.\n- TAME Blood Biomarker & Registry Check: Table 3 blood NfL"),
        ("\n\nMEDALS (", "\n- MEDALS, Exploratory Studies & Corticospinal GRIN1 Loss: MEDALS ("),
    ],
    ("EALS-009", "disproves"): [
        ("Failed Phase 3 MND-SMART Stage 2 comparison", "- Phase 3 MND-SMART Stage 2 Futility: Failed Phase 3 MND-SMART Stage 2 comparison"),
        ("AEs 90% vs 77%); at 200 mg/d", "AEs 90% vs 77%).\n- Unbound CNS Exposure Deficit vs. Sedative Off-Target Potency: At 200 mg/d"),
        ("5-HT2C agonist mCPP; moreover, two tested", "5-HT2C agonist mCPP.\n- Negative Selective Brain-Penetrant eIF2B Trials (HEALEY F & G): Two tested"),
    ],
    ("EALS-012", "disproves"): [
        ("Japanese multicenter Phase 2 RCT NCT03019419", "- Phase 2 RCT Functional Worsening & High Dropout: Japanese multicenter Phase 2 RCT NCT03019419"),
        ("placebo completion; corroborated by NCT03377309", "placebo completion.\n- Terminated Companion Trials & AMPA Class Context: Corroborated by NCT03377309"),
    ],
    ("EALS-024", "verdict"): [
        ("Directly falsified in a 249-patient randomized placebo-controlled Phase 2 ALS trial: subcutaneous", "- Phase 2 MERIDIAN Futility: Subcutaneous"),
        ("ALSFRS-R p=0.6447) missed primary and all secondary endpoints alongside", "ALSFRS-R p=0.6447) missed primary and all secondary endpoints.\n- Systemic Complement Scope Boundary: Aligns with negative"),
    ],
    ("EALS-024", "disproves"): [
        ("Randomized, double-blind, placebo-controlled Phase 2 MERIDIAN", "- Phase 2 MERIDIAN Futility & Systemic C5 Failures: Randomized, double-blind, placebo-controlled Phase 2 MERIDIAN"),
        ("PMID:39960672), while antemortem CSF C3", "PMID:39960672).\n- Sub-FDR CSF C3 & Unmeasured BBB Penetration: Antemortem CSF C3"),
    ],
    ("EALS-046", "disproves"): [
        ("Selective irreversible MAOB inhibitors", "- Three Negative ALS RCTs at >85% Brain Occupancy: Selective irreversible MAOB inhibitors"),
        ("N=111); scoped strictly to MAOB", "N=111).\n- Enzymatic Scope Boundary: Scoped strictly to MAOB"),
    ],
    ("EALS-048", "disproves"): [
        ("slowed ALSFRS-R decline, and FDA SJS/TEN", "slowed ALSFRS-R decline.\n- Dermatologic & Cardiac Safety Warnings: FDA SJS/TEN"),
    ],
    ("EALS-010", "verdict"): [
        ("Conditional 14.6-556x CSF-to-assay exposure gap", "- Conditional CSF-to-Assay Exposure Gap: Conditional 14.6-556x CSF-to-assay exposure gap"),
        ("DOI:10.1111/jnc.70183], whereas Morimoto 2023", "DOI:10.1111/jnc.70183]).\n- Unestablished sALS Minimum Concentration & Spinal DRD2/3 Absence: Morimoto 2023"),
        ("mutant FUS/TDP-43 activity).\n\nIn addition, Bye 2025", "mutant FUS/TDP-43 activity.\n- iPSC-MN Harm, Null Randomized ROPALS & EXPERTS-ALS Futility: Bye 2025"),
    ],
    ("EALS-010", "proves"): [
        ("Nominated from iPSC-MN phenotypic screening", "- Phenotypic iPSC-MN Screening Precedent: Nominated from iPSC-MN phenotypic screening"),
        ("mutant FUS/TDP-43 lines) and open-label extension", "mutant FUS/TDP-43 lines).\n- ROPALS Open-Label & Isogenic TARDBP Follow-Up Assays: Open-label extension"),
    ],
    ("EALS-010", "disproves"): [
        ("At the 16 mg/d ER protocol maximum", "- Protocol Dosing & Week-24 ALS CSF Exposure: At the 16 mg/d ER protocol maximum"),
        ("engages DRD2/3 Ki 2.9-7.2 nM) sits conditionally", "engages DRD2/3 Ki 2.9-7.2 nM).\n- 1 uM Phenotypic & SREBP2 Assay Gap: Sits conditionally"),
        ("1 uM assay dose) and 146-556x below", "1 uM assay dose).\n- 10 uM Isogenic Assay Gap & Absent Spinal DRD3: Sits 146-556x below"),
        ("p=0.4320, N=223); Bye 2025 showed", "p=0.4320, N=223).\n- Sporadic iPSC-MN Survival Harm & Null Randomized ROPALS: Bye 2025 showed"),
        ("N=20), and UK Phase 2a EXPERTS-ALS", "N=20).\n- Phase 2a EXPERTS-ALS Biomarker Futility: UK Phase 2a EXPERTS-ALS"),
    ],
    ("EALS-011", "verdict"): [
        ("Excluded on modeled human unbound CNS exposure", "- Unbound CNS Exposure Deficit vs. Observational Claims: Excluded on modeled human unbound CNS exposure"),
        ("Table 1) bounded by NDA016273", "Table 1).\n- KCC2/CA Co-Inhibition & Loop-Diuretic Toxicity: Bounded by NDA016273"),
    ],
    ("EALS-011", "proves"): [
        ("Nominated from observational healthcare-claims", "- Observational Claims & PRO-ACT Signals: Nominated from observational healthcare-claims"),
        ("[Table S5]) alongside 100 uM mouse midbrain", "[Table S5]).\n- Preclinical Slice Rationale & Untested Screen Status: Paired with 100 uM mouse midbrain"),
    ],
    ("EALS-011", "disproves"): [
        ("At oral 40 mg (NDA016273 Lasix", "- Active BBB Efflux & >1,000-Fold Unbound CNS Deficit: At oral 40 mg (NDA016273 Lasix"),
        ("34-190x too low), while furosemide non-selectively inhibits", "34-190x too low).\n- Non-Selective KCC2 & Carbonic Anhydrase Co-Inhibition: Furosemide non-selectively inhibits"),
        ("Ki ~65-200 nM, reduced human soleus", "Ki ~65-200 nM.\n- Human Spinal Inhibition Loss & Loop-Diuretic Toxicity: Reduced human soleus"),
    ],
    ("EALS-017", "verdict"): [
        ("Individual sub-nodes (EALS-017.1–EALS-017.4)", "- Symptomatic CSF Associations & Validation Scope: Individual sub-nodes (EALS-017.1–EALS-017.4)"),
        ("prospective validation), while failing therapeutic target criteria:", "prospective validation).\n- Why Inhibiting This Axis Fails Target Criteria:"),
    ],
    ("EALS-043", "disproves"): [
        ("~82%-overlapping Emory Set 1", "- Null Overlapping MS2-TMTpro Omnibus ANOVA: ~82%-overlapping Emory Set 1"),
        ("p=0.0673); PDB 1XFD (", "p=0.0673).\n- Non-Catalytic 3D Scaffold, Constraint & Null GWAS: PDB 1XFD ("),
    ],
    ("EALS-044", "disproves"): [
        ("~82%-overlapping Emory Set 1", "- Null Overlapping MS2-TMTpro Omnibus ANOVA: ~82%-overlapping Emory Set 1"),
        ("p=0.0569); canonical UniProt Q8N608", "p=0.0569).\n- Non-Catalytic Sequence Substitution & Strong LoF Constraint: Canonical UniProt Q8N608"),
    ],
    ("EALS-004", "verdict"): [
        ("Falsified in a definitive 513-patient", "- Phase 3 ALSFRS-R & Survival Futility: Falsified in a definitive 513-patient"),
        ("PMID:24771634), corroborated by CHEMBL161", "PMID:24771634).\n- Weak Human EAAT2 Potency & Absent Astrocyte Deficit: Corroborated by CHEMBL161"),
    ],
    ("EALS-004", "proves"): [
        ("Stage 1/2 human ALS PK", "- Stage 1/2 Human ALS CSF Pharmacokinetics: Stage 1/2 human ALS PK"),
        ("rodent target), and Lee et al. 2008", "rodent target).\n- Cultured Fetal Astrocyte EAAT2 Assay: Lee et al. 2008"),
    ],
    ("EALS-008", "proves"): [
        ("Ranked #3/107 in Bye 2025", "- Patient iPSC-MN Phenotypic Screen (#3/107): Ranked #3/107 in Bye 2025"),
        ("PMID:41286450) and reaches pharmacologically", "PMID:41286450).\n- Plausible Human CSF Exposure (Occupancy Unmeasured): Reaches pharmacologically"),
    ],
    ("EALS-009", "verdict"): [
        ("Directly falsified as a 200 mg/d oral regimen", "- Phase 3 MND-SMART Futility: Directly falsified as a 200 mg/d oral regimen"),
        ("not prespecified in Fig. 4), reinforced by a 71-330x", "not prespecified in Fig. 4).\n- Unbound Brain Exposure Deficit & Sedative Toxicity: Reinforced by a 71-330x"),
        ("mCPP anorexia, alongside negative Phase 2/3 outcomes", "mCPP anorexia.\n- Negative Selective eIF2B Trials (ABBV-CLS-7262 & DNL343): Negative Phase 2/3 outcomes"),
    ],
    ("EALS-009", "proves"): [
        ("Ranked #4/107 in Bye 2025", "- Patient iPSC-MN Phenotypic Screen (#4/107): Ranked #4/107 in Bye 2025"),
        ("PMID:41286450) following 20-40 uM cellular ISR", "PMID:41286450).\n- Micromolar Cellular ISR & Murine Prion Precedent: Followed 20-40 uM cellular ISR"),
    ],
    ("EALS-012", "verdict"): [
        ("Randomized human ALS clinical worsening", "- Phase 2 ALSFRS-R Worsening & High Dropout: Randomized human ALS clinical worsening"),
        ("placebo completion), corroborated by NCT03377309", "placebo completion).\n- Terminated Companion Trials & AMPA Scope Boundary: Corroborated by NCT03377309"),
    ],
    ("EALS-046", "proves"): [
        ("Zhang MN Visium (+1.1839", "- Cervical Spatial & Cortical Homogenate Elevation: Zhang MN Visium (+1.1839"),
        ("PMID:42789089) are consistent with reactive astrocyte expansion alongside any per-cell glial regulation (glia-free", "PMID:42789089) are consistent with reactive astrocyte expansion alongside any per-cell glial regulation.\n- Low / Discordant Neuronal snRNA: Glia-free"),
        ("p=0.0195).", "p=0.0195."),
    ],
    ("EALS-049", "proves"): [
        ("Open-label Phase 2a LIGHTHOUSE safety/tolerability", "- Open-Label Phase 2a LIGHTHOUSE Safety: Open-label Phase 2a LIGHTHOUSE safety/tolerability"),
        ("35 completers), Bye 2025 nominal 2.5 uM", "35 completers).\n- Nominal Screen Readout & Cortical ALS-TE Biology: Bye 2025 nominal 2.5 uM"),
    ],
    ("EALS-021", "verdict"): [
        ("Excluded on low human plasma exposure", "- Low Human Plasma Exposure & Unresolved Bioavailability: Excluded on low human plasma exposure"),
        ("protein binding; modeled Cu,brain", "protein binding).\n- Modeled Brain Exposure Gap & Target Biochemistry: Modeled Cu,brain"),
        ("PMID:43036320) with flat human GDF15", "PMID:43036320.\n- Null Phase 2 Biomarkers & Cardiac/Fall Safety Signals: Flat human GDF15"),
    ],
    ("EALS-021", "disproves"): [
        ("Chemical registry verification refuted", "- Chemical Registry & Reconstituted PPP1R15A Refutation: Chemical registry verification refuted"),
        ("PMID:38359044); in Phase 2 NCT05508074", "PMID:38359044).\n- Phase 2 Oral Plasma & Modeled Brain Exposure Gap: In Phase 2 NCT05508074"),
        ("125-500x gap) with flat plasma GDF15", "125-500x gap).\n- Null Biomarkers, Fatal Cardiac TEAEs & Falls: Flat plasma GDF15"),
    ],
    ("EALS-025", "verdict"): [
        ("Despite genuine 2.5 uM iPSC-MN rescue", "- Measured Human CSF & Calculated Free-Plasma PK Gap: Despite genuine 2.5 uM iPSC-MN rescue"),
        ("companion CSF pressure PMID:9249114) and calculated FDA NDA021038", "companion CSF pressure PMID:9249114).\n- Dose-Limiting Central Alpha-2A Sedation & Hypotension: Calculated FDA NDA021038"),
    ],
    ("EALS-025", "disproves"): [
        ("Talke et al. 1997 paired human", "- Paired Human Plasma-to-Lumbar CSF PK (Talke 1997): Talke et al. 1997 paired human"),
        ("\n\nTogether with FDA NDA021038 (", "\n- FDA Precedex / Igalmi Unbound Plasma Exposure Gap: FDA NDA021038 ("),
        ("Cu,p ~0.18 nM) show tolerated human CNS exposure", "Cu,p ~0.18 nM).\n- Dose-Limiting Locus Coeruleus Sedation & Cardiovascular Toxicity: Tolerated human CNS exposure"),
    ],
    ("EALS-027", "verdict"): [
        ("Active mycophenolic acid faces", "- Unbound CNS Deficit vs. Lymphoid IMPDH2 Blockade: Active mycophenolic acid faces"),
        ("PMID:7903306), FDA Boxed Warnings", "PMID:7903306).\n- Boxed Warnings & Null 4-Drug ALS Trial: Carries FDA Boxed Warnings"),
    ],
    ("EALS-027", "disproves"): [
        ("At 1,000 mg PO BID transplant ceiling", "- Anionic BBB Efflux & Unbound CNS Deficit: At 1,000 mg PO BID transplant ceiling"),
        ("neuronal screen); carries FDA Boxed Warnings", "neuronal screen).\n- Boxed Warnings & Null Phase 2 Immunosuppression Regimen: Carries FDA Boxed Warnings"),
    ],
    ("EALS-028", "verdict"): [
        ("Combined parent + active metabolite", "- Lipid Trapping vs. Low Unbound Brain Exposure: Combined parent + active metabolite"),
        ("PMID:34326236), bounded by FDA Boxed Warnings", "PMID:34326236).\n- Thromboembolic Toxicity & Null 12-Month ALS Trials: Bounded by FDA Boxed Warnings"),
    ],
    ("EALS-028", "disproves"): [
        ("Although total brain tamoxifen is", "- Lysosomal Lipid Trapping vs. Unbound Aqueous Brain Deficit: Although total brain tamoxifen is"),
        ("PMID:34326236); carries NDA021807 Boxed Warnings", "PMID:34326236).\n- Boxed Warnings, Thromboembolic Events & Null ALS Trials: Carries NDA021807 Boxed Warnings"),
    ],
    ("EALS-029", "verdict"): [
        ("Excluded on modeled human unbound CNS exposure", "- Unbound CNS Deficit & Progeria/Oncology Toxicities: Excluded on modeled human unbound CNS exposure"),
        ("Bye 2025 screen), and predicted biochemical antagonism", "Bye 2025 screen).\n- Predicted Antagonism of Sequential YKT6 Diprenylation: Biochemical antagonism"),
    ],
    ("EALS-029", "disproves"): [
        ("Excluded on modeled CNS exposure, clinical tolerability, and predicted YKT6 prenylation antagonism (untested, not in 107-drug library, in Bye 2025 screen): (1) Predicted directional liability:", "- Sequential YKT6 Diprenylation Requirement (Untested in 107-Drug Bye 2025 Screen):"),
        ("Chronos=-1.5425), predicting that FTIs", "Chronos=-1.5425).\n- Predicted Antagonism in TDP-43-Depleted ALS Neurons: Predicts that FTIs"),
        ("unperformed); (2) Unbound CNS PK deficit:", "unperformed).\n- Unbound CNS PK Deficit:"),
        ("IC50); (3) ALS-hostile human toxicity:", "IC50).\n- Progeria & Oncology Clinical Toxicities:"),
    ],
}

ALL_CARD_SPLITS: dict[tuple[str, str], list[tuple[str, str]]] = {**CARD_SPLITS_A, **CARD_SPLITS_B}

_INVARIANT_TOKEN_RE = re.compile(
    r"\b(?:PMID:[0-9]+|PMC[0-9]+|NCT[0-9]{8}|CHEMBL[0-9]+|CID:[0-9]+|PDB\s+[0-9][A-Za-z0-9]{3}|NDA\s*[0-9]+|OMIM\s+[0-9]+|rs[0-9]+|ENST[0-9]+(?:\.[0-9]+)?|ENSG[0-9]+|[0-9]+\.[0-9]+|[0-9]+,[0-9]+|[0-9]{2,})\b"
)


def structure_dossier_card(acc_id: str, field: str, txt: str) -> str:
    rules = ALL_CARD_SPLITS.get((acc_id, field))
    if not rules:
        return txt
    orig_tokens = set(_INVARIANT_TOKEN_RE.findall(txt))
    out = txt
    for old_seg, new_seg in rules:
        assert old_seg in out, f"Unmatched card split anchor on ({acc_id}, {field}): {old_seg!r}"
        out = out.replace(old_seg, new_seg, 1)
    new_tokens = set(_INVARIANT_TOKEN_RE.findall(out))
    missing = orig_tokens - new_tokens
    assert not missing, f"Token loss during card structuring on ({acc_id}, {field}): {sorted(missing)}"
    assert out.count("(") == out.count(")"), f"Unbalanced () after card structuring on ({acc_id}, {field})"
    assert out.count("[") == out.count("]"), f"Unbalanced [] after card structuring on ({acc_id}, {field})"
    return out.strip()
