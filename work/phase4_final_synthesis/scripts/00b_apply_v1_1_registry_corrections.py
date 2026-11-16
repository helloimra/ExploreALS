"""Apply ExploreALS v1.1 primary-source, epistemic, & bioanalytical corrections to base registries."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REG_DIR = ROOT / "registries"
TS = "2026-11-16T09:15:00Z"


def _load(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (REG_DIR / name).open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or []), list(rd)


def _save(name: str, cols: list[str], rows: list[dict[str, str]]) -> None:
    with (REG_DIR / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    # 1. evidence_ledger.csv
    ev_cols, ev_rows = _load("evidence_ledger.csv")
    ev_map = {r["evidence_id"]: r for r in ev_rows}

    ev_map["EV-B1-014"].update({
        "effect_direction": "STABLE_HOMOGENATE_ER_RETAINED_CSF_ABSENT",
        "notes": "Spillman iPSC homogenate log2FC=-0.1493 (p=0.6487, n=6); undetected (0 peptides) in Trautwig 2025 CSF TMT & DIA; Joseph et al. 2025 (PMID:41174170) & Brown Ribo-seq (padj=0.983) show NMD-escaping KCNQ2-DeltaE5 accumulates in soma ER with impaired surface trafficking (cortical P2 synaptosome null reflects sparse cortical TDP-43 pathology + co-fractionated ER across non-Exon-5 peptides). [Sample context: 19 postmortem frontal cortex synaptosome preps (10 C9-FTD/ALS vs 9 Ctrl)]",
    })
    ev_map["EV-B3-004"].update({
        "cohort_and_stratum": "Zhang 2026 human cervical spinal cord 55-um multicellular MN-niche Visium spots (N=14 donors)",
        "assay_and_contrast": "Spot-level spatial differential expression ALS vs HC (6d_MN_ALS_vs._HC; gene-level IL1RL1)",
        "notes": "Strong anterior horn perineuronal/microvascular gene-level IL1RL1 upregulation across multicellular 55-um Visium spots (N=14 donors; concordant with Cooper-Knock LCM +4.735 log2FC), masked in whole-cord bulk homogenates; isoform-specific sST2 vs ST2L assays required.",
    })
    ev_map["EV-B3-006"]["sample_size_n"] = ""
    ev_map["EV-B3-007"]["notes"] = (
        ev_map["EV-B3-007"]["notes"].split("; Thompson 2019")[0]
        + "; Thompson 2019 (PMID:30737180) shows standalone CSF chitinase AUC spans 0.51-0.92 (0.688 vs neurological ALS mimics), confirming symptomatic staging/PD utility rather than standalone mimic diagnosis."
    )
    ev_map["EV-B3-022"].update({
        "cohort_and_stratum": "Zhang 2026 human cervical spinal cord 55-um multicellular TDP-43+ anterior horn Visium spots (N=14 donors)",
        "assay_and_contrast": "Spot-level spatial differential expression ALS vs HC on C1QB (with C1QA/C1QC/C3/C4B in notes)",
    })
    ev_map["EV-B6-035"].update({
        "effect_direction": "unreported_withheld_rct_outcomes",
        "effect_estimate": "Randomized efficacy unreported (CT.gov hasResults=false; completed late 2021, OLE NCT04313166 terminated)",
        "epistemic_weight": "MODERATE",
        "notes": "Collaborative Medicinal Development completed Phase 2/3 NCT04082832 in late 2021 without releasing randomized ALSFRS-R/ECAS outcomes (hasResults=false; ALS/MND International Alliance moved CuATSM to discontinued); 62Cu/64Cu-ATSM PET reflects hypoxic Cu(I) reductive trapping rather than verified intact 2.5 uM normoxic CNS exposure (PMID:22036688).",
    })
    ev_map["EV-B6-036"].update({
        "source_id_or_locator": "PMID:37317638;DOI:10.1111/nan.12919",
        "epistemic_weight": "MODERATE",
        "notes": "Postmortem neuropathology of 6 oral CuATSM-treated (72 mg/d) ALS trial decedents vs 6 untreated ALS comparators showed no significant reduction in pTDP-43 pathology or motor neuron loss (small observational autopsy series, not randomized clinical efficacy). [Sample context: 6 CuATSM-treated vs 6 untreated ALS postmortem cases]",
    })
    ev_map["EV-B6-043"]["notes"] = "Constitutively active SARM1 ARM-domain GoF variants enrich in human ALS while gnomAD v4 shows no strong population depletion of heterozygous pLoF variants (LOEUF=1.143; distinct from clinical biallelic KO phenotyping or chronic pharmacological inhibition)."
    ev_map["EV-B6-044"].update({
        "epistemic_weight": "MODERATE",
        "notes": "Elevated SARM1 protein in small-sample C9FTD iPSC-neurons (n=3 vs 3, p=0.0268); note Stmn2 depletion acts in a parallel pathway rather than linearly lowering axonal NMNAT2 or activating SARM1 in mouse motor axons (Krus et al. 2022 PMID:35767949); end-stage NYGC Frontal RNA=-0.3066 reflects projection-neuron dropout.",
    })
    ev_map["EV-B6-045"].update({
        "cohort_and_stratum": "Clinical ALS SARM1 programs (LY3873862 Ph1 Not Yet Recruiting NCT07883590; NB-4746 NCT07369076) & 2026 medchem audit",
        "effect_estimate": "2 clinical ALS programs (Lilly LY3873862 NCT07883590 [Ph1 Not Yet Recruiting]; Nura/TRICALS NB-4746 NCT07369076) + preclinical ASHA-624",
        "notes": "Moderate clinical crowding on canonical SARM1 inhibitors; PMID:42156967 (PDB 9TZY) warns orthosteric base-exchange scaffolds risk sub-inhibitory SARM1 activation, favoring non-covalent intramolecular ARM-TIR allosteric T-lock glues (ASHA-624 class; covalent Cys311 PDB 7DJT serves strictly as a structural octamer benchmark).",
    })
    ev_map["EV-P2-T2-002"]["notes"] = (
        "Krus et al. 2022 (PMID:35767949) & Lopez-Erauskin et al. 2024 (PMID:37996528) prove Sarm1-/- does NOT rescue Stmn2-/- neurofilament collapse in vivo, "
        "establishing parallel biological non-redundancy of STMN2 rescue + non-covalent ARM-TIR SARM1 T-locks (ASHA-624 class; covalent Cys311 PDB 7DJT used strictly as a structural benchmark, and ~2-7x MWC sparing framed as an illustrative sensitivity scenario)."
    )
    ev_map["EV-P2-T1-001"]["notes"] = (
        "Preserves C-terminal helices A-D while excising Trp236 and inducing soma ER retention / impaired surface trafficking of KCNQ2-DeltaE5 (Joseph et al. 2025 PMID:41174170; modeled 61.8% poisoned channels at dPSI=0.2139 [MODEL_PRIOR]), "
        "imposing a surface-channel-density ceiling on small-molecule Kv7 pore openers."
    )
    ev_map["EV-B6-047"].update({
        "cohort_and_stratum": "MIROCALS BioVendor ELISA Low/Moderate CSF pNfH stratum (750-3700 pg/mL, n=154; <750 pg/mL LLOQ n=20 analyzed separately)",
        "notes": "MIROCALS SAP pre-specified covariate-adjusted Cox + continuous log(CSF pNfH)xTreatment interaction (adj HR=0.32, 95% CI 0.14-0.73, p=0.007; unadjusted ITT HR=0.81, p=0.33), operationalized into 750-3700 pg/mL (HR=0.52, p=0.016, n=154), <750 pg/mL LLOQ (n=20, 0 deaths), and >3700 pg/mL non-significant futility (HR=1.37, 95% CI 0.68-2.75, p=0.38, n=46).",
    })
    ev_map["EV-B6-051"].update({
        "effect_direction": "photolysis_false_negative_hypothesis",
        "notes": "Mechanistic chemical photolability hypothesis: routine blue-light live imaging cleaves the photosensitive Co-C bond of methylcobalamin into phototoxic species (-3.60d in Bye 2025, which lacked a dark-shielded control well), reconciling in vitro toxicity with Phase 3 JETALS benefit (+1.97 pts, PMID:35532908).",
    })
    ev_map["EV-P2-T3-004"].update({
        "assay_and_contrast": "Pearson correlation & p80 discordance of tryptic MS CSF NEFL vs NEFH (uncalibrated to BioVendor pNfH ELISA) + Schoenfeld event sizing",
        "effect_direction": "ASSAY_SPECIFIC_MS_NEFL_VS_NEFH_DISCORDANCE",
        "effect_estimate": "DIA r=0.2779 (31.17% p80 discordance, 75.0% top-quintile MS NEFH missed; overlapping Emory TMT n=51 misses 60.0%); HR=0.70 needs 247 deaths (138 at HR=0.62)",
        "notes": "Trautwig 2025 measures tryptic MS total NEFH abundance (noting blunted DIA-MS neurofilament dynamic range and overlapping Emory donors across TMT n=51 and 4-center DIA n=77), motivating paired BioVendor/Ella/Simoa pNfH vs NfL immunoassay calibration rather than proving clinical IL-2 responder misclassification; 247 deaths requires event-driven N~650-750 over 36-42 mo (or N~850-1,050 at 24 mo). [Sample context: 77 paired DIA ALS donors; technical cross-platform check in 51 overlapping Emory TMT ALS donors]",
    })
    _save("evidence_ledger.csv", ev_cols, ev_rows)

    # 2. subnode_dissection.csv
    sn_cols, sn_rows = _load("subnode_dissection.csv")
    for s in sn_rows:
        if s["subnode_id"] == "C015-N2":
            s["druggability_check"] = (
                "PDB 4M7N (catalytically inactive human G2E3 HECT-like domain crystal structure) + AF-Q7L622-F1 (mean pLDDT=85.60); "
                "0 ChEMBL bioactivities; catalytically active PHD/RING domains lack chemical matter."
            )
            s["subnode_verdict"] = s["subnode_verdict"].replace(
                "+ favorable DepMap non-essentiality (Chronos=-0.018)",
                "(dividing cancer-line DepMap Chronos=-0.018 despite human LoF constraint LOEUF=0.50 & mouse blastocyst lethality)",
            )
        elif s["subnode_id"] == "C015-N3":
            s["druggability_check"] = (
                "PDB 3KYQ (2.44A) shows Tyr64 (pLDDT=94.81) makes direct 3.46A contact to lipid DPV201 inside the cytosolic Longin prenyl-binding groove (4.29A from Cys66) "
                "that regulates Cys195-farnesyl / Cys194-geranylgeranyl membrane-opening switches (PMID:32128853); 0 ligands, with risk of sterically ejecting Cys195-farnesyl or freezing closed cytosolic YKT6 in >99.9% WT sALS."
            )
    _save("subnode_dissection.csv", sn_cols, sn_rows)
    print("Stage 2A (evidence_ledger + subnode_dissection) OK")


if __name__ == "__main__":
    main()
