"""Living Research Log v2.0.0 specification (UPD-2026-11-28-04): Portfolio Governance & Tiering Revision.
Implements six owner-authorized tiering, hurdle-accounting, and priority-ordering revisions while
preserving Epistemic Asymmetry (0 new DROPs) and all 8 standalone Monograph URLs.
"""
from __future__ import annotations

UPD_2026_11_28_04: dict[str, str] = {
    "update_id": "UPD-2026-11-28-04",
    "date_iso": "2026-11-28",
    "release_tag": "v2.0.0",
    "update_category": "MODEL_REVISION",
    "affected_ids": "EALS-001;EALS-002;EALS-006;EALS-030;EALS-031;EALS-034;EALS-037;EALS-007;EALS-020;EALS-019;EALS-026;EALS-047;EALS-050;EALS-052;EALS-033",
    "decision_impact": "v2.0.0 Portfolio Governance Revision: 0 Tier 1, 6 Tier 2 (#1 UNC13A > #2 STMN2 > #3 KCNQ2 > #4 SARM1 > #5 Aldesleukin > #6 ATG4B), CELF5 (#7) & IL1RL1 (#22) in Tier 3, 6 Stalled Drugs Parked in Tier 4 Watchlist (0 New Drops)",
    "headline": "ExploreALS v2.0.0 Portfolio Governance & Tiering Calibration: Zero Tier 1 Programs, Core Splice-Rescue Ordering, and Tier 4 Parked Watchlist",
    "prior_state_or_assumption": (
        "ExploreALS v1.6.0 placed SARM1 (EALS-030) and low-dose Aldesleukin (EALS-031) in Tier 1 (Actionable Now), ranked KCNQ2 (EALS-006) ahead of STMN2 (EALS-002) among core splice-rescue programs, retained IL1RL1/sST2 (EALS-007) and CELF5 (EALS-037) in Tier 2 (Validation Gate), and grouped stalled iPSC-MN drug-repurposing leads together with active mechanistic discovery programs in Tier 3."
    ),
    "new_evidence_or_revision": (
        "(1) Zero Tier 1 Actionable Programs (EALS-030 SARM1 #4 & EALS-031 Aldesleukin #5 -> Tier 2): SARM1 non-covalent ARM-TIR T-lock programs still require prospective Cys311Ala dependence and intact-protein MS non-covalency verification (4th hurdle, alongside sub-IC50 orthosteric activation PMID:42380237, plasma cADPR ecto-CD38 masking, and soma-axon decoupling PMID:35863521, PMID:31661035), while low-dose Aldesleukin missed its unadjusted ITT survival primary endpoint in MIROCALS (HR=0.81, p=0.33, PMID:40354799) and requires CLSI EP09c BioVendor-to-CLIA CSF pNfH bridging (PMID:42836993) plus longitudinal Treg TSDR vs. CD56bright NK and sCD25 durability (3rd hurdle). Neither program clears the bar for immediate execution without prior gating; "
        "(2) Core Tier 2 Ordering (EALS-001 #1 > EALS-002 #2 > EALS-006 #3 > EALS-030 #4, followed by Exploratory Tier 2 EALS-031 #5 & EALS-034 ATG4B #6): STMN2 (EALS-002) advances ahead of KCNQ2 (EALS-006) because STMN2 has validated human cryptic-exon-2a ASO mechanics and completed Phase 1 ANQUR CSF pNfH dose-response readouts (PMID:36927019), whereas KCNQ2 lead #3 still requires an empirical Intron-5 ISS vs. ISE microwalk (PMID:41174170); "
        "(3) Tier 3 Discovery Recalibration (EALS-037 CELF5 -> #7 Top Tier 3; EALS-007 IL1RL1/sST2 -> #22 Tier 3): CELF5 (EALS-037) awaits empirical ASO splice rescue and postmortem spinal protein confirmation (Spillman 2026 cortical DIA inconclusive, PMID:42789089) while ATG4B (EALS-034, #6) retains Tier 2 on published human ASO mRNA rescue and cross-cohort protein depletion; IL1RL1/sST2 (EALS-007) moves to Tier 3 with a 3rd hurdle requiring iPSC neurovascular-microglial tri-culture pathogenic-decoy vs. BBB-brake directionality (resolving Edinburgh endothelial elevation PMID:42551425 vs. null Pineda BA4 vascular RNA PMID:38521060 and antemortem CSF immunoassay limits); "
        "(4) New Tier 4 Parked Watchlist (#26-#31): parks six stalled repurposing leads facing multi-fold unbound CNS exposure gaps, negative/unreported clinical readouts, or unconfirmed monoculture signals (EALS-020 Apilimod #26, EALS-019 Baricitinib #27, EALS-026 CuATSM #28, EALS-047 PMX 205 #29, EALS-050 Acetylcysteine #30, EALS-052 L-Serine #31; Bye 2025 PMID:41286450) while strictly preserving Keep · Exploratory and Untested / Unresolved status (zero new Drops) and keeping Censavudine (EALS-033, #20) in active Tier 3 pending HEALEY Phase 2/3 readouts."
    ),
    "portfolio_and_gate_consequence": (
        "Establishes v2.0.0 portfolio tier distribution across 55 candidates: 0 Tier 1, 6 Tier 2 (4 Core + 2 Exploratory), 19 active Tier 3 Discovery, 6 Tier 4 Parked Watchlist, 1 Companion Protocol (#32), 7 Biomarkers/Benchmarks (#33-#39), and 16 Excluded (#40-#55). All 8 standalone Monograph pages remain live at unchanged URLs (6 Tier 2 Leads plus 2 Tier 3 Deep-Dive Monographs for EALS-037 and EALS-007). Promotion criteria: Tier 1 requires cleared Phase 1b target-engagement PK/PD or analytical assay bridging plus confirmed mechanism; un-parking from Tier 4 to Tier 3 requires primary human CNS exposure/PD proof or public release of unreported clinical efficacy data."
    ),
    "primary_sources": "PMID:42380237;PMID:35863521;PMID:31661035;PMID:40354799;PMID:42836993;PMID:36927019;PMID:41174170;PMID:42551425;PMID:38521060;PMID:42789089;PMID:41286450",
    "verification_anchor": "RUN-P3A-003;RUN-P3B-003;RUN-P4-001;RUN-P4-002;EV-P3A-004;FLAGSHIP-EALS-001;FLAGSHIP-EALS-002;FLAGSHIP-EALS-006;FLAGSHIP-EALS-030;FLAGSHIP-EALS-031;FLAGSHIP-EALS-034;FLAGSHIP-EALS-037;FLAGSHIP-EALS-007",
}
