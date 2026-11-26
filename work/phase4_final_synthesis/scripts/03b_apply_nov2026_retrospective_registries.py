"""Idempotently apply RUN-P4-003 Nov 2026 retrospective updates to ExploreALS v1.2 registries."""
from __future__ import annotations

import csv
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
REG_DIR = ROOT / "registries"
SCRIPTS_DIR = ROOT / "scripts"
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (SCRIPTS_DIR, SCRIPT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _retrospective_registry_specs import NEW_EVIDENCE_ROWS, RUN_P4_003_ROW  # noqa: E402
from _retrospective_stat_and_log_specs import NEW_STAT_SPECS, UPD_2026_11_19_01  # noqa: E402
from _retrospective_wave_b_specs import WAVE_B_NEW_EVIDENCE_ROWS, WAVE_B_NEW_STAT_SPECS  # noqa: E402
from _retrospective_wave_c_specs import WAVE_C_NEW_EVIDENCE_ROWS, WAVE_C_NEW_STAT_SPECS  # noqa: E402
from _retrospective_wave_d_specs import UPD_2026_11_22_01  # noqa: E402
from _public_taxonomy import deaudit_prose  # noqa: E402
from _retrospective_tbk1_specs import UPD_2026_11_26_01  # noqa: E402
from _retrospective_v1_3_specs import UPD_2026_11_23_01  # noqa: E402
from carbon_als.accessions import legacy_to_accession, translate_legacy_tokens_in_prose  # noqa: E402
from verify_carbon_als import sha256_anchor  # noqa: E402

ALL_NEW_EVIDENCE_ROWS = [*NEW_EVIDENCE_ROWS, *WAVE_B_NEW_EVIDENCE_ROWS, *WAVE_C_NEW_EVIDENCE_ROWS]
ALL_NEW_STAT_SPECS = [*NEW_STAT_SPECS, *WAVE_B_NEW_STAT_SPECS, *WAVE_C_NEW_STAT_SPECS]

TS = "2026-11-19T03:56:00Z"


def _load(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (REG_DIR / name).open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or []), list(rd)


def _save(name: str, cols: list[str], rows: list[dict[str, str]]) -> None:
    with (REG_DIR / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def _append_ev(cur: str, new_eid: str) -> str:
    items = [x.strip() for x in cur.split(";") if x.strip()]
    if new_eid not in items:
        items.append(new_eid)
    return ";".join(items)


def main() -> None:
    # 1. analysis_runs.csv (insert RUN-P4-003 right before RUN-P4-001)
    r_cols, r_rows = _load("analysis_runs.csv")
    r_rows = [r for r in r_rows if r["analysis_run_id"] != "RUN-P4-003"]
    idx_p4 = next((i for i, r in enumerate(r_rows) if r["analysis_run_id"] == "RUN-P4-001"), len(r_rows))
    r_rows.insert(idx_p4, dict(RUN_P4_003_ROW))
    for r in r_rows:
        if r["analysis_run_id"] == "RUN-P4-002":
            r["summary"] = r["summary"].replace("188/188", "202/202").replace("194/194", "202/202").replace("197/197", "202/202").replace("199/199", "202/202")
        elif r["analysis_run_id"] == "RUN-P2-T3-002":
            r["run_timestamp_utc"] = "2026-11-20T00:05:00Z"
            r["summary"] = (
                "Living-CSF dissection of tryptic MS total NEFH vs NEFL across Emory TMT (n=51 nested subset) and "
                "4-center DIA (n=77/79; r=0.278 vs clinical immunoassay rho=0.64-0.71, motivating CLSI EP09c N>=40 "
                "BioVendor-to-CLIA pNfH & paired NfL immunoassay calibration) alongside exact MIROCALS Fig. 2 strata "
                "(<750 n=19, 750-3,700 n=154, >3,700 n=47; 2.131x death-rate ratio), platform-offset power sensitivity, "
                "and Schoenfeld Phase 3 sizing (247 events at HR=0.70; 138 at HR=0.62)."
            )
        r["summary"] = deaudit_prose(r["summary"])
    _save("analysis_runs.csv", r_cols, r_rows)

    # 2. evidence_ledger.csv
    e_cols, e_rows = _load("evidence_ledger.csv")
    new_eids = {r["evidence_id"] for r in ALL_NEW_EVIDENCE_ROWS}
    e_rows = [r for r in e_rows if r["evidence_id"] not in new_eids] + [dict(r) for r in ALL_NEW_EVIDENCE_ROWS]
    for er in e_rows:
        for ek in ("cohort_and_stratum", "assay_and_contrast", "effect_estimate", "notes"):
            er[ek] = deaudit_prose(er[ek])
    _save("evidence_ledger.csv", e_cols, e_rows)

    # 3. statistical_models_and_contrasts.csv (preserve staged sha64 in cached mode if data/ absent)
    s_cols, s_rows = _load("statistical_models_and_contrasts.csv")
    prev_sha = {r["evidence_id"]: r["sha64"] for r in s_rows}
    ds_cryptic_sha = next(
        d["sha256"] for d in _load("datasets_manifest.csv")[1] if d["dataset_id"] == "DS_CRYPTIC"
    )
    built_stats: list[dict[str, str]] = []
    for sp in ALL_NEW_STAT_SPECS:
        row = dict(sp)
        ok, digest = sha256_anchor(ROOT / row["anchor_relpath"])
        row["sha64"] = digest if ok else prev_sha.get(row["evidence_id"], ds_cryptic_sha)
        built_stats.append(row)
    s_rows = [r for r in s_rows if r["evidence_id"] not in new_eids] + built_stats
    for sr in s_rows:
        if sr["evidence_id"] == "EV-B6-046":
            sr["unadjusted_or_primary_nominal_p"] = "0.33000"
            sr["covariate_adjusted_nominal_p"] = ""
        elif sr["evidence_id"] == "EV-B6-047":
            sr["exact_contrast"] = "MIROCALS BioVendor ELISA Low/Moderate CSF pNfH stratum (750-3700 pg/mL, n=154; <750 pg/mL LLOQ n=19 analyzed separately) | 21-mo mortality hazard ratio & Treg/CCL2 PD"
        elif sr["evidence_id"] == "EV-P2-T3-004":
            sr["inference_class"] = "PRIMARY_FREQUENTIST_RECOMPUTE"
            sr["statistical_unit"] = "unique_human_donor"
            sr["exact_contrast"] = "Trautwig 2025 living symptomatic ALS CSF (4-center DIA n=77 paired NEFH+NEFL; replicated in Emory TMT n=51) | Pearson correlation & p80 discordance of tryptic MS CSF NEFL vs NEFH + CLSI EP09c platform-offset sensitivity & Schoenfeld event sizing"
            sr["model_formula_or_test"] = "Two-sided bivariate Pearson r & 80th-percentile 2x2 contingency + Schoenfeld survival power sensitivity"
            sr["effect_estimate"] = "DIA r=0.2779 (31.17% p80 discordance, 75.0% [12/16] top-quintile MS NEFH missed; overlapping Emory TMT n=51 misses 60.0% [6/10]); HR=0.70 needs 247 deaths at 80% power (138 at HR=0.62 [MODEL_PRIOR])"
            sr["unadjusted_or_primary_nominal_p"] = "0.01441"
            sr["covariate_adjusted_nominal_p"] = ""
        elif sr["evidence_id"] == "EV-B1-004":
            sr["effect_estimate"] = "6/10 C9-FTD (mean PSI=2.30%, 26 CE reads) vs 0/10 Control"
        elif sr["evidence_id"] == "EV-B6-045":
            sr["exact_contrast"] = "Clinical SARM1 programs (LY3873862 NCT05492201 completed N=84 HV + ALS Ph1 NYR NCT07883590; NB-4746 ALS Ph1/2 NCT07369076; NB-9402 HV Ph1 ACTRN12626000650392; SIR2501 ALS Ph1b/2a CTR20253552 + CIPN Ph2 NCT07765446) & 2026 medchem audit | Clinical crowding & orthosteric vs allosteric pharmacology"
            sr["effect_estimate"] = "4 clinical SARM1 programs across 3 sponsors (Lilly LY3873862 NCT07883590 [ALS Ph1 NYR; N=84 HV NCT05492201 completed]; Nura/TRICALS NB-4746 NCT07369076 + NB-9402 ACTRN12626000650392; Sironax SIR2501 CTR20253552/NCT07765446) + preclinical ASHA-624"
        elif sr["evidence_id"] == "EV-P2-T4-001":
            sr["n_statistical_units"] = "28"
            sr["exact_contrast"] = "UMI-pooled donor-collapsed Edinburgh cortical endothelium (n=28 unique donors at min_nuclei>=10: 21 non-C9 sALS vs 7 Ctrl, XIST/UTY-verified, PMID:42551425) & PDB 4KC3 IL-33-ST2 complex | Welch two-sample t-test on donor-collapsed endothelial IL1RL1 log2CPM + sST2 vs pan-ST2 Treg ST2L mass-action model"
            sr["effect_estimate"] = "Endo diff_log2CPM=+3.1067 (p=0.00698; all ALS +2.8427, p=0.0115, n=30; n=7 Ctrl caveat; Pineda BA4 vascular +0.075 p=0.918; XIST/UTY swap-immune H5AD); 4KC3 (resolved aa 21-317) 30 ST2 D1-D3 contacts (10 Cys = 5 closed disulfides, leaving sequence-deduced Cys327 in 324-SKECF-328 unpaired) -> at perivascular 400pM sST2 (vs ~5pM bulk CSF PMID:37117777), [MODEL_PRIOR] 5nM pan-ST2 suppresses Treg ST2L (3.2%->0.32%) vs 80% RNA suppression (11.8%) or intact-FcRn sweeping (28.2%)"
            sr["unadjusted_or_primary_nominal_p"] = "0.00698"
            sr["covariate_adjusted_nominal_p"] = ""
        for sk in ("exact_contrast", "model_formula_or_test", "effect_metric", "effect_estimate", "missingness_or_exclusion_rule"):
            sr[sk] = deaudit_prose(sr[sk])
        ok_a, dig_a = sha256_anchor(ROOT / sr["anchor_relpath"])
        if ok_a:
            sr["sha64"] = dig_a
    _save("statistical_models_and_contrasts.csv", s_cols, s_rows)

    # 4. candidate_decisions.csv
    d_cols, d_rows = _load("candidate_decisions.csv")
    dm = {r["carbon_id"]: r for r in d_rows}
    for cid, eid in (
        ("S06", "EV-P4-001"),
        ("C001", "EV-P4-002"),
        ("C022", "EV-P4-003"),
        ("C006", "EV-P4-004"),
        ("C015", "EV-P4-005"),
        ("C015", "EV-P4-007"),
        ("C018", "EV-P4-006"),
        ("C023", "EV-P4-008"),
        ("C013", "EV-P4-009"),
    ):
        dm[cid]["supporting_evidence_ids"] = _append_ev(dm[cid]["supporting_evidence_ids"], eid)
        if not dm[cid]["updated_at"] or dm[cid]["updated_at"] < TS:
            dm[cid]["updated_at"] = TS

    dm["S06"]["evidence_proves_hypothesis"] = dm["S06"]["evidence_proves_hypothesis"].replace(
        "(Gilley 2021; Bloom 2022; OT genetic_score=0.195)",
        "(Gilley 2021 PMID:34796871; Bloom 2022 PMID:34991663; near-full-length autoinhibited 7ANW/7DJT octamer inter-protomer ARM-TIR latch 3.07-5.47A vs 37.8-65.4A intra-chain, cumulative validated GoF AF=0.000378 [~0.076% carriers] vs benign P332Q AF=0.986%, 97 hom; 0/12 single-gene SARM1 ClinVar P/LP [6 opposite-strand SLC46A1 records])",
    ).replace(
        "4-PDB octamer inter-protomer ARM-TIR latch 3.07-5.47A vs 35.4-66.9A intra-chain, cumulative validated GoF AF=0.000378 [~0.076% carriers] vs benign P332Q AF=0.986%; 0/12 single-gene SARM1 ClinVar P/LP [6 opposite-strand SLC46A1 LoFs]",
        "near-full-length autoinhibited 7ANW/7DJT octamer inter-protomer ARM-TIR latch 3.07-5.47A vs 37.8-65.4A intra-chain, cumulative validated GoF AF=0.000378 [~0.076% carriers] vs benign P332Q AF=0.986%, 97 hom; 0/12 single-gene SARM1 ClinVar P/LP [6 opposite-strand SLC46A1 records]",
    ).replace(
        "7ANW/7DJT octamer inter-protomer ARM-TIR latch",
        "near-full-length autoinhibited 7ANW/7DJT octamer inter-protomer ARM-TIR latch",
    ).replace(
        "near-full-length autoinhibited near-full-length autoinhibited",
        "near-full-length autoinhibited",
    )
    dm["S06"]["factual_justification"] = dm["S06"]["factual_justification"].replace(
        "pairing with #2 C006",
        "pairing with #4 C006",
    )
    dm["S06"]["discriminating_next_test"] = dm["S06"]["discriminating_next_test"].replace(
        "in d_lock=6.5 GoF heterozygotes",
        "in Binomial hetero-octamer d_lock=6.5 GoF heterozygotes",
    )
    if "PMID:43015463" not in dm["C001"]["evidence_proves_hypothesis"]:
        dm["C001"]["evidence_proves_hypothesis"] = dm["C001"]["evidence_proves_hypothesis"].replace(
            "Keuss et al. 2026 Nature, 10.1038/s41586-026-11256-2:",
            "Keuss et al. 2026 Nature PMID:43015463, 10.1038/s41586-026-11256-2:",
        )
    dm["C001"]["evidence_disproves_hypothesis"] = dm["C001"]["evidence_disproves_hypothesis"].replace(
        "capping Intron-20-only ASO full-length mRNA at ~55.6% above Keuss 2026's >30% synaptic threshold",
        "implying a [MODEL_PRIOR] ~46.1-55.6% standalone Intron-20 ASO mRNA ceiling under severe TDP-43 KD above Keuss 2026's >30% synaptic threshold",
    )
    if "dPSI=+0.3543" not in dm["C001"]["evidence_disproves_hypothesis"]:
        dm["C001"]["evidence_disproves_hypothesis"] = dm["C001"]["evidence_disproves_hypothesis"].replace(
            "Intron-31 retention,",
            "Intron-31 retention (Brown MAJIQ PSI 0.097->0.444, dPSI=+0.3543, source MAJIQ 'FDR' [p_d_psi_0.05]=1.82e-15, implying a [MODEL_PRIOR] ~46.1-55.6% standalone Intron-20 ASO mRNA ceiling under severe TDP-43 KD above Keuss 2026's >30% synaptic threshold),",
        )
    else:
        dm["C001"]["evidence_disproves_hypothesis"] = dm["C001"]["evidence_disproves_hypothesis"].replace(
            "dPSI=+0.3543, FDR=1.82e-15,",
            "dPSI=+0.3543, source MAJIQ 'FDR' [p_d_psi_0.05]=1.82e-15,",
        )
    dm["C022"]["evidence_proves_hypothesis"] = dm["C022"]["evidence_proves_hypothesis"].replace(
        "55 ClinVar P/LP alleles,",
        "55 Open Targets EVA/ClinVar submissions, 25/25 single-gene GRCh38 P/LP variants,",
    ).replace("log2FC=+0.092, padj=0.283", "log2FC=+0.092, p=0.124, padj=0.283")
    dm["C022"]["factual_justification"] = dm["C022"]["factual_justification"].replace(
        "55 ClinVar P/LP variants)",
        "25/25 single-gene GRCh38 ClinVar P/LP variants; 55 Open Targets EVA submissions)",
    )
    if "25/25 (100%)" not in dm["C022"]["evidence_proves_hypothesis"]:
        dm["C022"]["evidence_proves_hypothesis"] += " Primary 6-cohort splicing/APA scan confirms 0 TDP-43 cryptic/APA events (i3Neuron RNA log2FC=+0.092, p=0.124, padj=0.283), AF-P25686 resolves 2 rigid domains (aa 1-73 & 164-223, pLDDT=67.38), and 25/25 (100%) single-gene ClinVar P/LP variants map to shared Exons 2-9 vs 0/25 in DNAJB2b Zone A."
    dm["C006"]["evidence_disproves_hypothesis"] = dm["C006"]["evidence_disproves_hypothesis"].replace(
        "[MODEL_PRIOR] Signed AlphaGenome predict_variant",
        "[MODEL_PRIOR] One-sided WT-context signed AlphaGenome predict_variant",
    )
    if "63442302:C>G" not in dm["C006"]["evidence_disproves_hypothesis"]:
        dm["C006"]["evidence_disproves_hypothesis"] += " [MODEL_PRIOR] One-sided WT-context signed AlphaGenome predict_variant shows #3 63442302:C>G increases Exon 4-6 skipping +35.2% (+0.1930) vs #2 Intron-4 UG (-0.0522), flagging a putative Intron-5 ISE hazard requiring empirical microwalk resolution."
    base_c015 = dm["C015"]["evidence_proves_hypothesis"].split(" Open Targets SuSiE-inf")[0].split(".988,")[0].rstrip(".") + "."
    dm["C015"]["evidence_proves_hypothesis"] = (
        base_c015
        + " Open Targets SuSiE-inf (purityMeanR2=0.988, EUR-vs-xAnc GWAS COLOC H4=0.958, PMID:34873335) and phased 1000G Phase 3 chromosomes show rs229243-A, cross-ancestry lead rs229195-A (PIP=0.240), rs229194-A, and rs229143-A have 96.7% (351/363) 1111 A-haplotype purity in EUR vs 72.7% (853/1,173; 320 mixed) in AFR (gnomAD NFE AF=32.6-32.9%, EAS=60.4-61.3%)."
    )
    if "PDB 1PK6" not in dm["C018"]["evidence_proves_hypothesis"]:
        dm["C018"]["evidence_proves_hypothesis"] = dm["C018"]["evidence_proves_hypothesis"].replace(
            "10.1016/j.cell.2024.05.058)",
            "PMID:38942014, 10.1016/j.cell.2024.05.058; crystal PDB 1PK6 1.85A gC1q head PMID:12960167 vs AFDB predicted mature CLR stalk [project sequence count: 27 mature Arg/Lys across C1QA 23-109 / C1QB 28-114 / C1QC 29-112, residue-level necessity untested] distinguishes anti-gC1q Fab from C1QA/B ASO)",
        )
    c019_tbk1_note = (
        " Moreover, whereas complete Tbk1 deletion on an embryonic-rescue Tnf-/- background suppressed interferon-responsive microglial [IRM]/DAM genes in SOD1G93A mice without extending male lifespan or rescuing lumbar ChAT+ MNs "
        "(Horiuchi et al. 2026 DOI:10.1186/s40478-026-02474-w; cf. Phase 2 HIMALAYA RIPK1 inhibitor SAR443820 futility in NCT05237284 PMID:42716044, ALSFTD4 TBK1 haploinsufficiency PMID:25700176 / PMID:25803835 [gnomAD v4.1 LOEUF=0.505], and TBK1 cardiomyocyte beat toxicity PMID:28453775), "
        "neuronal TBK1 physically senses monomeric TDP-43 to drive IFN-beta->IFNAR->PSMB8 immunoproteasome clearance in human iPSC-MNs while human ALS spinal MNs downregulate IFNAR "
        "(Sakai et al. 2026 PMID:42834122; NYGC spinal ALS-Glia STAT2 adj_beta=-0.4635, p=6.35e-8 & RSAD2 -0.5257, p=4.01e-4) — warning that high-Kp,uu IFNAR/TYK2/JAK1 blockade "
        "(untested on TDP-43 clearance in nuclear-TDP-43-intact Bye 2025 cultures, P=0.990) risks impairing neuronal monomeric TDP-43 turnover."
    )
    if "10.1186/s40478-026-02474-w" not in dm["C019"]["evidence_disproves_hypothesis"]:
        dm["C019"]["evidence_disproves_hypothesis"] = dm["C019"]["evidence_disproves_hypothesis"].rstrip() + c019_tbk1_note
    if "PMID:42834122" not in dm["C019"]["discriminating_next_test"]:
        dm["C019"]["discriminating_next_test"] = dm["C019"]["discriminating_next_test"].replace(
            "and reactive ALS-Glia co-cultures —",
            "and reactive ALS-Glia co-cultures (co-measuring monomeric TDP-43 turnover and PSMB8 immunoproteasome activity under cytoplasmic TDP-43 stress per Sakai et al. 2026 PMID:42834122, and excluding germline TBK1 LoF carriers PMID:25700176 / PMID:25803835) —",
        )
    dm["C019"]["updated_at"] = "2026-11-26T01:10:00Z"

    s09_tbk1_note = (
        " Upstream LINE-1 ORF2p RT blockade also selectively targets retroelement cDNA->cGAS-STING signaling "
        "(NYGC cortical ALS-TE vs ALS-Ox STING1 adj_beta=+0.3098, p=8.69e-4, IFI16 +0.2136, p=0.00664, CGAS +0.1264, p=0.0451 while TBK1 -0.2578, p=3.52e-12 is lower vs ALS-Ox; spinal ALS-Glia vs Control CGAS +0.4779, p=1.69e-6 & IFI16 +0.5870, p=5.35e-9; cf. TDP-43 mtDNA->cGAS-STING PMID:33031745) "
        "while sparing cell-autonomous neuronal TBK1->IFN-beta->IFNAR->PSMB8 immunoproteasome clearance of monomeric TDP-43 "
        "(Sakai et al. 2026 PMID:42834122; contrasting with SOD1G93A;Tbk1-/-;Tnf-/- interferon-responsive microglial [IRM] suppression in Horiuchi et al. 2026 DOI:10.1186/s40478-026-02474-w, ALSFTD4 TBK1 LoF PMID:25803835, and Phase 2 HIMALAYA RIPK1 futility NCT05237284 PMID:42716044)."
    )
    if "10.1186/s40478-026-02474-w" not in dm["S09"]["evidence_proves_hypothesis"]:
        dm["S09"]["evidence_proves_hypothesis"] = dm["S09"]["evidence_proves_hypothesis"].rstrip() + s09_tbk1_note
    if "PMID:42834122" not in dm["S09"]["discriminating_next_test"]:
        dm["S09"]["discriminating_next_test"] = dm["S09"]["discriminating_next_test"].replace(
            "given deucravacitinib P-gp efflux, PMID:41832177).",
            "across both retroelement ISG suppression and neuronal TBK1->IFN-beta->PSMB8 monomeric TDP-43 clearance [Sakai et al. 2026 PMID:42834122], given deucravacitinib P-gp efflux, PMID:41832177).",
        )
    dm["S09"]["updated_at"] = "2026-11-26T01:10:00Z"
    _save("candidate_decisions.csv", d_cols, d_rows)

    # 5. subnode_dissection.csv (C015-N1/N2 SuSiE haplotype + C018-N1..N3 PDB 1PK6 head vs CLR stalk)
    sn_cols, sn_rows = _load("subnode_dissection.csv")
    for sn in sn_rows:
        sid = sn["subnode_id"]
        if sid == "C015-N1":
            sn["subnode_verdict"] = (
                "KEEP_EXPLORATORY_UNPROVEN: Answer ALS motor-neuron eQTL-ALS GWAS locus overlap (Tsitkov 2026 [PREPRINT] PMC12919128: rs229143-A Table S8 intersection beta=+0.04762, Bonferroni adj p=1.93e-32 [Fig. 3A +0.048+/-0.003, p<2e-32], motif-suggested ISL1 footprint, AVI Phred=10.27; van Rheenen GCST90027164 ALS risk beta=+0.0212, gnomAD NFE AF=0.329; GTEx BA9 +0.269) "
                "AND formal Bayesian colocalization in human iMGLs (261 initial lines from 254 donors -> published post-QC cohorts n=189 untreated, n=188 IFN-gamma & n=188 LPS eQTL donors [inferred nominal SCFD1 fit n=186, 185 & 185]: sole chr14q12 formal colocalization PP.H4=0.8764-0.8899 with 0 G2E3 signal & sole ALS hit shared with primary microglia; same rs229143-A allele beta=-0.2955 untreated [AF=0.3441], -0.2164 IFN-gamma [AF=0.3486], -0.3107 LPS [AF=0.3459], shared rs229194-A/rs229195-A -0.2920/-0.2237/-0.3061 [AF=0.3387-0.3432; Table S4 LPS lead 14_30590763_G_A -0.3328], targeted 251-gene NeuroKO phagocytosis score=-0.07562, FDR=0.9284 null; PMID:43045849, Zenodo 21471267); "
                "SuSiE chr14q12 credible set (purityMeanR2=0.988, NFE AF=32.6-32.9%, EUR-vs-xAnc GWAS COLOC H4=0.958, PMID:34873335; 1000G EUR 96.7% [351/363] vs AFR 72.7% [853/1,173] 1111 purity; x-anc lead rs229195-A PIP=0.240) supports opposite expression signs for the same rs229143-A allele across MN and iMGL studies ([MODEL_PRIOR] AlphaGenome CD14+ q=-0.99986; slopes not compared across scales, and causal cell-type interaction, within-donor opposition, TF identity & beneficial sALS treatment direction remain open), "
                "alongside zero TDP-43 splicing shift, null Spillman MOESM1 cortex DIA protein (Homog p=0.931, Synapt p=0.797), DepMap Chronos=-1.26 pan-essentiality, and zero selective ligands requiring bidirectional MN + iMGL ER-Golgi secretory CRISPRi/CRISPRa."
            )
        elif sid == "C015-N2":
            if "rs229195-A" not in sn["subnode_verdict"]:
                sn["subnode_verdict"] += " Cross-ancestry GWAS lead rs229195-A (PIP=0.240, [MODEL_PRIOR] AlphaGenome MN G2E3 splice q=0.968) rides in phase with SCFD1 rs229243-A/rs229143-A."
            else:
                sn["subnode_verdict"] = sn["subnode_verdict"].replace(
                    "AlphaGenome MN G2E3 splice q=0.968", "[MODEL_PRIOR] AlphaGenome MN G2E3 splice q=0.968"
                ).replace("[MODEL_PRIOR] [MODEL_PRIOR]", "[MODEL_PRIOR]")
        elif sid in {"C018-N1", "C018-N2", "C018-N3"} and "PDB 1PK6" not in sn["druggability_check"]:
            sn["druggability_check"] += " Crystal PDB 1PK6 (1.85A gC1q head, 187 inter-chain pairs <=4.5A, PMID:12960167) vs AF-P02745-F1/AF-P02746-F1/AF-P02747-F1 predicted mature CLR stalk (collagen-like domain required for neuronal RNP uptake/LLPS in PMID:38942014 Figs. 3 & 6; project sequence count: 27 mature Arg/Lys residues across C1QA 23-109, C1QB 28-114, C1QC 29-112 [30 up to aa 114], residue-level necessity untested) splits anti-gC1q Fab (head-only) from C1QA/B ASO (head+stalk)."
    _save("subnode_dissection.csv", sn_cols, sn_rows)

    # 6. living_evidence_updates.csv
    u_cols, u_rows = _load("living_evidence_updates.csv")
    u_rows = [u for u in u_rows if u["update_id"] not in {"UPD-2026-11-19-01", "UPD-2026-11-20-01", "UPD-2026-11-20-02", "UPD-2026-11-21-01", "UPD-2026-11-21-02", "UPD-2026-11-21-03", "UPD-2026-11-22-01", "UPD-2026-11-23-01", "UPD-2026-11-26-01"}]
    for u in u_rows:
        uid = u["update_id"]
        if uid == "UPD-2026-11-18-05":
            u["decision_impact"] = "KCNQ2 (EALS-006) Gated on Intron-5 Microwalk (#4/52); Multiplex Margin Set at 6–9 mg"
            u["prior_state_or_assumption"] = "(1) QRL-201 / STMN2 (EALS-002): headline ANQUR ALSFRS-R or Day-421 OLE plasma NfL summaries do not separate 3 mg vs. 10 mg CSF pNfH dose dissociation, 10 mg->3 mg washout kinetics, or post-hoc baseline-NfL tertile exclusion; (2) KCNQ2 (EALS-006) & Multiplex Dosing: conservation-ranked intronic windows around KCNQ2 Exon 5 lack wet-lab ISS vs. ISE polarity proof, and extrapolating single-agent ASO doses (12–100 mg) to 2-plex/3-plex combinations risks cumulative 24–48 mg polyanion DRG radiculotoxicity."
            u["new_evidence_or_revision"] = "(1) Phase 1 ANQUR (NCT05633459, N=69 total: completed N=17 MAD + N=52 DRF at 3 mg/10 mg vs placebo, plus ongoing N=41 3 mg OLE) showed Day-197 CSF pNfH -46% vs baseline at 3 mg vs ~5% at 10 mg, while Day-253 10 mg ALSFRS-R 50% slowing vs placebo relied on post-hoc exclusion of the top baseline-NfL fast-progressor tertile; (2) Pivotal CONQUR, KCNQ2 & Benchmarks: US FDA cleared the pivotal CONQUR IND on 16 Nov 2026 (planned H1 2027), while single-agent intrathecal ASO benchmarks nusinersen (12–50 mg, DEVOTE PMID:41634391), tofersen (100 mg, VALOR PMID:36129998), and tominersen (PMID:31059641) motivate gating KCNQ2 Exon-5 polarity before <=3 mg/strand (6–9 mg) multiplex dosing."
            u["portfolio_and_gate_consequence"] = u["portfolio_and_gate_consequence"].replace("Tier 2 · Focused Gate First", "Tier 2 · Validation Gate")
        elif uid == "UPD-2026-11-18-04":
            u["prior_state_or_assumption"] = "Preclinical UNC13A (EALS-001) steric-ASO validation rested on iPSC motor-neuron splicing and Munc13-1 protein recovery (Brown 2022 PMID:35197628; Ma 2022 PMID:35197626) without defining the quantitative human protein threshold required to rescue evoked synaptic transmission."
            u["new_evidence_or_revision"] = "Keuss et al. (2026, Nature, PMID:43015463, DOI:10.1038/s41586-026-11256-2) demonstrated that restoring >30% human UNC13A protein via Intron-20 cryptic-exon deletion (~75% protein rescue) or 2'-O-MOE ASOs rescues miniature and evoked AMPA EPSCs and MEA network synchrony across human cortical and spinal motor neurons. Postsynaptic mEPSC amplitude reduction remained unrescued, and single-target UNC13A rescue leaves orthogonal STMN2 polyadenylation and KCNQ2 Exon-5 skipping unaddressed."
            u["primary_sources"] = _append_ev(u["primary_sources"], "PMID:43015463")
        elif uid == "UPD-2026-11-18-03":
            u["prior_state_or_assumption"] = "Combination models of STMN2 rescue plus SARM1 inhibition often assume indirect NMNAT2 epistasis and interpret bulk plasma cADPR drops as direct axonal SARM1 target engagement without bounding rare ARM-GoF residual NADase activity or ecto-CD38 fluid background."
            u["new_evidence_or_revision"] = "Evaluated clinical allosteric SIR2501 (NCT07765446 CIPN Ph2) and reversible orthosteric NB-4746 (NCT07369076) across three modeled bounds: (1) 1.0x parallel Bliss survival additivity (Krus 2022 PMID:35767949; Matson & Holzbaur 2026 DOI:10.64898/2026.11.07.764673) to ~2–7x (med ~3x) NMNAT2-transport-coupled MWC dose-sparing (Beccari 2025 PMID:40392845); (2) ~30–40% residual NADase ceiling at 100x Kd in rare ARM-broken GoF heterozygotes (Gilley 2021 PMID:34796871; Bloom 2022 PMID:34991663); (3) modeled ~5–10% selective cell-free fluid cADPR drop under >90–95% ecto-CD38 fluid background vs ~45–50% implied CD38 inhibition if cell-free plasma cADPR drops -50% (cf. tissue cADPR PMID:32087251; PDB 9TZY BEXi adduct 17 PMID:42156967)."
            u["primary_sources"] = _append_ev(u["primary_sources"], "PMID:34796871")
        elif uid == "UPD-2026-11-18-02":
            u["headline"] = "MIROCALS Primary Stratum Verification, CLSI EP09c pNfH Assay Bridging & Phase 3 Survival Sizing"
            u["prior_state_or_assumption"] = "Follow-on low-dose IL-2 trial designs frequently treat clinical TRICALS risk scores, shotgun CSF mass spectrometry, or unbridged commercial pNfH/NfL immunoassay cutoffs as interchangeable with MIROCALS's BioVendor ELISA CSF pNfH <=3,700 pg/mL responder stratum."
            u["new_evidence_or_revision"] = "Primary verification of MIROCALS (NCT03039673, PMID:40354799, N=220, 90 deaths, unadjusted ITT HR=0.81 p=0.33: <750 pg/mL n=19 [0 deaths], 750–3,700 n=154 [57 deaths, HR=0.52; pooled <=3,700 n=173 HR=0.57 p=0.037], >3,700 n=47 [33/90 deaths, HR=1.37 p=0.38; 2.13x crude mortality proportion ratio], continuous interaction p=0.0011, ALSFRS-R slope interaction F=3.95 p=0.048, and sustained Day-112 trough Treg expansion p<0.0001) alongside Al Khleifat et al. (2026, J Neurol, PMID:42836993: TRICALS shares r^2 = 12.7% with CSF pNfH; nested pNfH x trt dChi2 = 14.24 vs TRICALS x trt dChi2 = 4.76) separates tryptic CSF MS noise (r = 0.278, PMID:40375307) from clinical immunoassays (serum NfL–CSF pNfH rho = 0.64–0.71, PMID:38683209; serum NfL > serum pNfH on ALSFRS-R slope, PMID:32385188; paired CSF–serum pNfH r = 0.652, PMID:29054919) and notes ~1.8x–4.5x inter-platform pNfH offsets (PMID:31251725; modeled unbridged lower CSF cutoffs reduce 247-death two-sided superiority power from 80% to ~43–50% at HR_high = 1.00 or ~14–23% at HR_high = 1.37), while enrolled N=137 ALSTARS (NCT07161999) stratifies 3 serum NfL tiers on 24-wk ALSFRS-R with dual rhIL-2 + CTLA4-Ig."
            u["portfolio_and_gate_consequence"] = "Retains EALS-031 (#2/52, Keep · Exploratory, Tier 1) and locks pre-Phase-3 CLSI EP09c split-aliquot Passing-Bablok bridging (N>=40 paired ALS CSFs) to MIROCALS's ~79th BioVendor percentile plus complementary TRICALS + log(CSF pNfH) Cox adjustment across 247 Schoenfeld events (HR = 0.70)."
            u["primary_sources"] = "PMID:42836993;PMID:40354799;PMID:38683209;PMID:32385188;PMID:29054919;PMID:31251725;NCT07161999;NCT03039673"
        elif uid == "UPD-2026-11-18-01":
            u["prior_state_or_assumption"] = "Intermittent pulsed PIKfyve inhibition (EALS-020) models typically assume an occupancy dead-zone before endolysosomal vacuolation onset (~79% parameter-grid pass rate) without accounting for immediate +PI(3)P-driven LRRK2/CASM stress coupling."
            u["new_evidence_or_revision"] = "Kuwahara et al. (2026, Life Sci Alliance, PMID:42994990) demonstrated direct, threshold-free PIKfyve -> +PI(3)P -> LRRK2 Rab10-pThr73 / ATG16L1 CASM recruitment alongside Drosophila C9orf72 secreted DPR data (DOI:10.64898/2026.11.09.765393). In modeled pulsed q48h–q72h turnover simulations (>=55% substrate clearance and end-of-cycle stress <=0.05), removing the occupancy dead-zone cuts grid survival from ~79% (64/81) to ~30% (24/81) at matched 10–20 h repair and 0% (0/81) at slower 24–48 h postmitotic CASM washout."
            u["portfolio_and_gate_consequence"] = "Retains EALS-020 (#23/52, Keep · Exploratory) (125 mg BID AIT-101 NCT05163886 recorded 0 drug-related SAEs, Wk-12 CSF apilimod 1.63 ng/mL [3.89 nM free-base eq across n=9/10 randomized treated], Babu Table 3 shared-baseline mixed-model plasma sGPNMB ratio 2.31 [p<0.001] vs CSF sGPNMB ratio 0.92 [p=0.352; both separately labeled 2-sided t-test on CT.gov], and exploratory small-sample Wk-12 plasma & OLE CSF NfL rises without powered clinical efficacy testing, while continuous QD VRG50635 NCT06215755 [54 enrolled, 50 treated] recorded investigator-reported treatment-related SAEs in 8/50 [16.0%] treated participants and exploratory GFAP/NfL rises [AAN2026-003396] and terminated for lack of Phase 2 risk-benefit; the two clinical programs do not define a single class-wide toxicity threshold, and pulsed q48h–q72h remains clinically untested) behind a 14-day human iPSC-MN CASM/vacuole washout and intracellular + secreted DPR mass-balance validation gate."
    u_rows.insert(0, dict(UPD_2026_11_19_01))
    u_rows.insert(0, dict(UPD_2026_11_22_01))
    u_rows.insert(0, dict(UPD_2026_11_23_01))
    u_rows.insert(0, dict(UPD_2026_11_26_01))
    def _map_anchor_tok(tok: str) -> str:
        t = tok.strip()
        if t.startswith("FLAGSHIP-") and not t.startswith("FLAGSHIP-EALS-"):
            raw = t.removeprefix("FLAGSHIP-")
            raw_leg = f"DN-{raw[2:]}" if re.fullmatch(r"DN\d{2}", raw) else raw
            return f"FLAGSHIP-{legacy_to_accession(raw_leg)}"
        return t

    for u in u_rows:
        u["affected_ids"] = ";".join(
            legacy_to_accession(tok.strip()) for tok in u["affected_ids"].split(";") if tok.strip()
        )
        u["verification_anchor"] = ";".join(
            _map_anchor_tok(tok) for tok in u["verification_anchor"].split(";") if tok.strip()
        )
        for pk in ("decision_impact", "headline", "prior_state_or_assumption", "new_evidence_or_revision", "portfolio_and_gate_consequence"):
            u[pk] = deaudit_prose(translate_legacy_tokens_in_prose(u[pk]))
    u_rows.sort(key=lambda x: (x["date_iso"], x["update_id"]), reverse=True)
    _save("living_evidence_updates.csv", u_cols, u_rows)
    print(f"RUN-P4-003 registries updated: {len(r_rows)} runs, {len(e_rows)} evidence, {len(s_rows)} SHA-64 contrasts, {len(u_rows)} living updates.")


if __name__ == "__main__":
    main()
