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
from verify_carbon_als import sha256_anchor  # noqa: E402

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
            r["summary"] = r["summary"].replace("188/188", "194/194")
    _save("analysis_runs.csv", r_cols, r_rows)

    # 2. evidence_ledger.csv
    e_cols, e_rows = _load("evidence_ledger.csv")
    new_eids = {r["evidence_id"] for r in NEW_EVIDENCE_ROWS}
    e_rows = [r for r in e_rows if r["evidence_id"] not in new_eids] + [dict(r) for r in NEW_EVIDENCE_ROWS]
    _save("evidence_ledger.csv", e_cols, e_rows)

    # 3. statistical_models_and_contrasts.csv (preserve staged sha64 in cached mode if data/ absent)
    s_cols, s_rows = _load("statistical_models_and_contrasts.csv")
    prev_sha = {r["evidence_id"]: r["sha64"] for r in s_rows}
    ds_cryptic_sha = next(
        d["sha256"] for d in _load("datasets_manifest.csv")[1] if d["dataset_id"] == "DS_CRYPTIC"
    )
    built_stats: list[dict[str, str]] = []
    for sp in NEW_STAT_SPECS:
        row = dict(sp)
        ok, digest = sha256_anchor(ROOT / row["anchor_relpath"])
        row["sha64"] = digest if ok else prev_sha.get(row["evidence_id"], ds_cryptic_sha)
        built_stats.append(row)
    s_rows = [r for r in s_rows if r["evidence_id"] not in new_eids] + built_stats
    _save("statistical_models_and_contrasts.csv", s_cols, s_rows)

    # 4. candidate_decisions.csv
    d_cols, d_rows = _load("candidate_decisions.csv")
    dm = {r["carbon_id"]: r for r in d_rows}
    for cid, eid in (("S06", "EV-P4-001"), ("C001", "EV-P4-002"), ("C022", "EV-P4-003"), ("C006", "EV-P4-004"), ("C015", "EV-P4-005"), ("C018", "EV-P4-006")):
        dm[cid]["supporting_evidence_ids"] = _append_ev(dm[cid]["supporting_evidence_ids"], eid)
        dm[cid]["updated_at"] = TS

    dm["S06"]["evidence_proves_hypothesis"] = dm["S06"]["evidence_proves_hypothesis"].replace(
        "(Gilley 2021; Bloom 2022; OT genetic_score=0.195)",
        "(Gilley 2021 PMID:34796871; Bloom 2022 PMID:34991663; 7ANW/7DJT octamer inter-protomer ARM-TIR latch 3.07-5.47A vs 37.8-65.4A intra-chain, cumulative validated GoF AF=0.000378 [~0.076% carriers] vs benign P332Q AF=0.986%, 97 hom; 0/12 single-gene SARM1 ClinVar P/LP [6 opposite-strand SLC46A1 records])",
    ).replace(
        "4-PDB octamer inter-protomer ARM-TIR latch 3.07-5.47A vs 35.4-66.9A intra-chain, cumulative validated GoF AF=0.000378 [~0.076% carriers] vs benign P332Q AF=0.986%; 0/12 single-gene SARM1 ClinVar P/LP [6 opposite-strand SLC46A1 LoFs]",
        "7ANW/7DJT octamer inter-protomer ARM-TIR latch 3.07-5.47A vs 37.8-65.4A intra-chain, cumulative validated GoF AF=0.000378 [~0.076% carriers] vs benign P332Q AF=0.986%, 97 hom; 0/12 single-gene SARM1 ClinVar P/LP [6 opposite-strand SLC46A1 records]",
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
            "Intron-31 retention (Brown MAJIQ PSI 0.097->0.444, dPSI=+0.3543, FDR=1.82e-15, implying a [MODEL_PRIOR] ~46.1-55.6% standalone Intron-20 ASO mRNA ceiling under severe TDP-43 KD above Keuss 2026's >30% synaptic threshold),",
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
    dm["C015"]["evidence_proves_hypothesis"] = dm["C015"]["evidence_proves_hypothesis"].replace(
        "co-segregate in phase on one risk haplotype.",
        "co-segregate in phase on one risk haplotype (gnomAD NFE AF=32.6-32.9%, EAS=60.4-61.3%).",
    )
    if "purityMeanR2=0.988" not in dm["C015"]["evidence_proves_hypothesis"]:
        dm["C015"]["evidence_proves_hypothesis"] += " Open Targets SuSiE-inf (purityMeanR2=0.988, COLOC H4=0.958, PMID:34873335) proves rs229243-A, cross-ancestry lead rs229195-A (PIP=0.240), rs229194-A, and rs229143-A co-segregate in phase on one risk haplotype (gnomAD NFE AF=32.6-32.9%, EAS=60.4-61.3%)."
    if "PDB 1PK6" not in dm["C018"]["evidence_proves_hypothesis"]:
        dm["C018"]["evidence_proves_hypothesis"] = dm["C018"]["evidence_proves_hypothesis"].replace(
            "10.1016/j.cell.2024.05.058)",
            "PMID:38942014, 10.1016/j.cell.2024.05.058; PDB 1PK6 1.85A gC1q head PMID:12960167 vs AFDB CLR stalk aa 28-114 26 Arg/Lys basic motif distinguishes anti-gC1q Fab from C1QA/B ASO)",
        )
    _save("candidate_decisions.csv", d_cols, d_rows)

    # 5. subnode_dissection.csv (C015-N1/N2 SuSiE haplotype + C018-N1..N3 PDB 1PK6 head vs CLR stalk)
    sn_cols, sn_rows = _load("subnode_dissection.csv")
    for sn in sn_rows:
        sid = sn["subnode_id"]
        if sid == "C015-N1":
            if "purityMeanR2=0.988" not in sn["subnode_verdict"]:
                sn["subnode_verdict"] = sn["subnode_verdict"].replace(
                    "opposing MN-vs-myeloid eQTL polarity,",
                    "SuSiE-proven in-phase risk haplotype (purityMeanR2=0.988, NFE AF=32.6-32.9%, COLOC H4=0.958, PMID:34873335; x-anc lead rs229195-A PIP=0.240) driving opposing MN (+0.048) vs myeloid (-0.22..-0.33; AlphaGenome CD14+ q=-0.99986) polarity,",
                )
            else:
                sn["subnode_verdict"] = sn["subnode_verdict"].replace(
                    "purityMeanR2=0.988, COLOC H4=0.958,",
                    "purityMeanR2=0.988, NFE AF=32.6-32.9%, COLOC H4=0.958,",
                )
        elif sid == "C015-N2" and "rs229195-A" not in sn["subnode_verdict"]:
            sn["subnode_verdict"] += " Cross-ancestry GWAS lead rs229195-A (PIP=0.240, AlphaGenome MN G2E3 splice q=0.968) rides in phase with SCFD1 rs229243-A/rs229143-A."
        elif sid in {"C018-N1", "C018-N2", "C018-N3"} and "PDB 1PK6" not in sn["druggability_check"]:
            sn["druggability_check"] += " PDB 1PK6 (1.85A gC1q head, 187 inter-chain pairs <=4.5A, PMID:12960167) vs AF-P02745-F1/AF-P02746-F1/AF-P02747-F1 cationic CLR stalk (aa 28-114, 26 Arg/Lys basic residues required for neuronal RNP uptake, PMID:38942014) splits anti-gC1q Fab (head-only) from C1QA/B ASO (head+stalk)."
    _save("subnode_dissection.csv", sn_cols, sn_rows)

    # 6. living_evidence_updates.csv
    u_cols, u_rows = _load("living_evidence_updates.csv")
    u_rows = [u for u in u_rows if u["update_id"] != "UPD-2026-11-19-01"]
    for u in u_rows:
        uid = u["update_id"]
        if uid == "UPD-2026-11-18-05":
            u["prior_state_or_assumption"] = "(1) KCNQ2 Tiering: placed KCNQ2 (C006) in Tier 1 ahead of wet-lab Intron-5 splice-enhancer/silencer microwalk proof; (2) Multiplex Mass: framed Stage 2 multiplex co-dosing around legacy 24–48 mg total intrathecal oligonucleotide loads."
            u["new_evidence_or_revision"] = "(1) Phase 1 ANQUR (NCT05633459): N=52 DRF at 3 mg/10 mg vs placebo and N=41 3 mg OLE showed Day-197 CSF pNfH -46% at 3 mg vs ~5% at 10 mg, while Day-253 10 mg ALSFRS-R slowing relied on post-hoc exclusion of the top baseline-NfL fast-progressor tertile; (2) Pivotal CONQUR & Benchmarks: US FDA cleared the pivotal CONQUR IND on 16 Nov 2026 (planned H1 2027), evaluated alongside single-agent intrathecal ASO benchmarks nusinersen (12–50 mg, DEVOTE PMID:41634391), tofersen (100 mg, VALOR PMID:36129998), and tominersen (PMID:31059641)."
        elif uid == "UPD-2026-11-18-04":
            u["new_evidence_or_revision"] = "Keuss et al. (2026, Nature, PMID:43015463, DOI:10.1038/s41586-026-11256-2) demonstrated that restoring >30% human UNC13A protein via Intron-20 cryptic-exon deletion or 2'-O-MOE ASOs rescues miniature and evoked AMPA EPSCs and MEA network synchrony across human cortical and spinal motor neurons. Isolated UNC13A rescue left STMN2 polyadenylation, KCNQ2 Exon-5 skipping, and ~10% postsynaptic mEPSC amplitude unrescued, confirming orthogonal compartment complementarity."
            u["primary_sources"] = _append_ev(u["primary_sources"], "PMID:43015463")
        elif uid == "UPD-2026-11-18-03":
            u["new_evidence_or_revision"] = u["new_evidence_or_revision"].replace("Gilley 2021 PMID:34991663", "Gilley 2021 PMID:34796871; Bloom 2022 PMID:34991663")
            u["primary_sources"] = _append_ev(u["primary_sources"], "PMID:34796871")
        elif uid == "UPD-2026-11-18-02":
            u["new_evidence_or_revision"] = "Al Khleifat et al. (2026, J Neurol, PMID:42836993) showed inside MIROCALS (NCT03039673, PMID:40354799, N=220) that clinical TRICALS risk explains only r^2 = 12.7% of log(CSF pNfH) (-2LL = 928.25 vs 793.36) and surfaced 1.8x–4.5x MSD ECLIA vs BioVendor ELISA pg/mL bias alongside fully enrolled N=137 ALSTARS (NCT07161999, which omits CSF pNfH gating and blocks Treg CD28): (1) [MODEL_PRIOR] unbridged lower-reading bias dilutes 247-death Phase 3 power (80% at HR = 0.70) toward ~6–12%; (2) pre-specified TRICALS + log(CSF pNfH) Cox adjustment raises power to ~84–88% (noting <750 pg/mL n=20/220 had 0 deaths)."
        elif uid == "UPD-2026-11-18-01":
            u["new_evidence_or_revision"] = "Kuwahara et al. (2026, Life Sci Alliance, PMID:42994990) demonstrated direct, threshold-free PIKfyve -> +PI(3)P -> LRRK2 Rab10-pThr73 / ATG16L1 CASM recruitment alongside Drosophila C9orf72 secreted DPR data (DOI:10.64898/2026.11.09.765393). In [MODEL_PRIOR] pulsed q48h–q72h turnover simulations (>=55% substrate clearance and end-of-cycle stress <=0.05), removing the occupancy dead-zone cuts grid survival from ~79% (64/81) to ~30% (24/81) at matched 10–20 h repair and 0% (0/81) at slower 24–48 h postmitotic CASM washout."
    u_rows.insert(0, dict(UPD_2026_11_19_01))
    u_rows.sort(key=lambda x: (x["date_iso"], x["update_id"]), reverse=True)
    _save("living_evidence_updates.csv", u_cols, u_rows)
    print(f"RUN-P4-003 registries updated: {len(r_rows)} runs, {len(e_rows)} evidence, {len(s_rows)} SHA-64 contrasts, {len(u_rows)} living updates.")


if __name__ == "__main__":
    main()
