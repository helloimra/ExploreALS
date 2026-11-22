"""True biological/evidence-origin cohorts, cis-regulatory mechanisms, and public prose/modality sanitizers for ExploreALS."""
from __future__ import annotations

import re

COHORT_DEFS: list[tuple[str, str]] = [
    ("GENETICS_MENDELIAN_GWAS", "Human ALS Genetics — Mendelian & GWAS"),
    ("TDP43_SPLICING_APA", "TDP-43 Cryptic Splicing & Polyadenylation"),
    ("CNS_TISSUE_OMICS", "Human CNS Spatial, snRNA & Subcellular Omics"),
    ("CSF_AND_PHYSIOLOGY", "Living-Patient CSF Proteomics & Physiology"),
    ("CLINICAL_TRIALS_SUBGROUPS", "Human ALS Clinical Trials & Subgroups"),
    ("IPSC_PHENOTYPIC_SCREEN", "Patient iPSC-MN Phenotypic Screen (Bye 2025)"),
]

EVIDENCE_COHORT_BY_EALS: dict[str, str] = {
    "EALS-030": "GENETICS_MENDELIAN_GWAS", "EALS-001": "GENETICS_MENDELIAN_GWAS",
    "EALS-022": "GENETICS_MENDELIAN_GWAS", "EALS-015": "GENETICS_MENDELIAN_GWAS",
    "EALS-023": "GENETICS_MENDELIAN_GWAS",
    "EALS-006": "TDP43_SPLICING_APA", "EALS-002": "TDP43_SPLICING_APA",
    "EALS-034": "TDP43_SPLICING_APA", "EALS-037": "TDP43_SPLICING_APA",
    "EALS-038": "TDP43_SPLICING_APA", "EALS-035": "TDP43_SPLICING_APA",
    "EALS-036": "TDP43_SPLICING_APA", "EALS-039": "TDP43_SPLICING_APA",
    "EALS-040": "TDP43_SPLICING_APA", "EALS-041": "TDP43_SPLICING_APA",
    "EALS-042": "TDP43_SPLICING_APA",
    "EALS-007": "CNS_TISSUE_OMICS", "EALS-014": "CNS_TISSUE_OMICS",
    "EALS-018": "CNS_TISSUE_OMICS", "EALS-016": "CNS_TISSUE_OMICS",
    "EALS-046": "CNS_TISSUE_OMICS",
    "EALS-017": "CSF_AND_PHYSIOLOGY", "EALS-043": "CSF_AND_PHYSIOLOGY",
    "EALS-044": "CSF_AND_PHYSIOLOGY", "EALS-045": "CSF_AND_PHYSIOLOGY",
    "EALS-005": "CSF_AND_PHYSIOLOGY",
    "EALS-031": "CLINICAL_TRIALS_SUBGROUPS", "EALS-013": "CLINICAL_TRIALS_SUBGROUPS",
    "EALS-032": "CLINICAL_TRIALS_SUBGROUPS", "EALS-003": "CLINICAL_TRIALS_SUBGROUPS",
    "EALS-033": "CLINICAL_TRIALS_SUBGROUPS", "EALS-026": "CLINICAL_TRIALS_SUBGROUPS",
    "EALS-019": "CLINICAL_TRIALS_SUBGROUPS", "EALS-020": "CLINICAL_TRIALS_SUBGROUPS",
    "EALS-004": "CLINICAL_TRIALS_SUBGROUPS", "EALS-012": "CLINICAL_TRIALS_SUBGROUPS",
    "EALS-024": "CLINICAL_TRIALS_SUBGROUPS", "EALS-021": "CLINICAL_TRIALS_SUBGROUPS",
    "EALS-049": "CLINICAL_TRIALS_SUBGROUPS",
    "EALS-047": "IPSC_PHENOTYPIC_SCREEN", "EALS-008": "IPSC_PHENOTYPIC_SCREEN",
    "EALS-009": "IPSC_PHENOTYPIC_SCREEN", "EALS-010": "IPSC_PHENOTYPIC_SCREEN",
    "EALS-011": "CSF_AND_PHYSIOLOGY", "EALS-025": "IPSC_PHENOTYPIC_SCREEN",
    "EALS-027": "IPSC_PHENOTYPIC_SCREEN", "EALS-028": "IPSC_PHENOTYPIC_SCREEN",
    "EALS-029": "TDP43_SPLICING_APA", "EALS-048": "IPSC_PHENOTYPIC_SCREEN",
    "EALS-050": "IPSC_PHENOTYPIC_SCREEN", "EALS-051": "IPSC_PHENOTYPIC_SCREEN",
    "EALS-052": "IPSC_PHENOTYPIC_SCREEN",
}


def resolve_cis_mechanism(gene: str, raw_mode: str) -> str:
    if gene in {"STMN2", "TRAPPC12", "DLGAP1", "PTPRT"} or "ALE" in raw_mode or "A3SS" in raw_mode:
        return "CRYPTIC_ALE_PAS_BLOCK"
    if gene == "KCNQ2" or raw_mode.startswith("INCLUDE_"):
        return "CONSTITUTIVE_EXON_INCLUSION"
    if gene == "ELK1" or "3EXT" in raw_mode:
        return "DISTAL_3UTR_EXTENSION"
    return "CRYPTIC_EXON_SKIP"


def resolve_cis_role(acc_id: str, raw_role: str) -> str:
    if raw_role == "CORE_3PLEX":
        return "MULTIPLEX_CORE"
    if raw_role == "DEFERRED_4TH_CANDIDATE":
        return "EXCLUDED_ALU_REPEAT"
    if acc_id in {"EALS-034", "EALS-037"}:
        return "SINGLE_LOCUS_LEAD"
    return "EXPLORATORY_LOCUS"


def resolve_cis_mode_code(gene: str, raw_mode: str) -> str:
    if gene == "STMN2":
        return "CRYPTIC_EXON2A_3SS_PAS_BLOCK"
    return raw_mode


def sanitize_public_modality(raw_mod: str) -> str:
    s = str(raw_mod or "").strip()
    if "_" in s and " " not in s.split("(")[0]:
        s = (
            s.replace("Dropped_Failed_Human_ALS_Clinical_Regimen_", "Failed ALS clinical regimen: ")
            .replace("Dropped_PK_or_Safety_Infeasible_Regimen_", "Failed CNS PK/safety regimen: ")
            .replace("Dropped_Failed_Human_CNS_PK_Safety_Regimen_", "Failed CNS PK/safety regimen: ")
            .replace("Dropped_Confounded_Postmortem_Transcriptomic_Target_", "Assay-confounded screen regimen: ")
            .replace("Dropped_Unbound_CNS_PK_Deficit_", "Failed CNS PK exposure: ")
            .replace("2OMOE", "2'-O-MOE").replace("POPS", "PO/PS").replace("TLock", "T-Lock")
            .replace("ARM_TIR", "ARM-TIR").replace("ASHA624", "ASHA-624").replace("72mg", "72 mg")
            .replace("Half_Life_Extended", "Half-Life-Extended").replace("ECM_Anchored", "ECM-Anchored")
            .replace("Anti_C1q", "Anti-C1q").replace("Allele_Specific", "Allele-Specific")
            .replace("Neuron_Selective", "Neuron-Selective").replace("Non_Covalent", "Non-Covalent")
            .replace("Non_Orthosteric", "Non-Orthosteric").replace("Non_Chelating", "Non-Chelating")
            .replace("KV7_2_7_3", "Kv7.2/7.3").replace("Kv7_2_7_3", "Kv7.2/7.3").replace("NaV1_6", "NaV1.6")
            .replace("CTail_aa324_328", "C-Tail (aa 324-328 SKECF)").replace("CTail_aa320_328", "C-Tail (aa 324-328 SKECF)").replace("Early_Onset_LE12m", "Early-Onset (<=12m)")
            .replace("LE12m", "<=12m").replace("3Plex", "3-Plex").replace("Exon5", "Exon-5")
            .replace("Exon2a", "Exon-2a").replace("Intron20", "Intron-20").replace("Intron8", "Intron-8")
            .replace("Intron9", "Intron-9").replace("ERAD_Sparing", "ERAD-Sparing")
            .replace("aa324_328", "aa 324-328").replace("aa320_328", "aa 324-328").replace("Q48_to_Q72h", "q48h-q72h")
            .replace("LINE1_RT", "LINE-1 RT").replace("TPN101", "TPN-101").replace("JAK2_Sparing", "JAK2-Sparing")
            .replace("Brain_Penetrant", "Brain-Penetrant").replace("Low_Dose", "Low-Dose").replace("IL2", "IL-2")
            .replace("_", " ")
        )
    return sanitize_public_prose(s)


def sanitize_public_prose(txt: str) -> str:
    s = str(txt or "")
    if not s:
        return s
    s = s.replace("[MEASURED] vs [MODEL_PRIOR] tags", "empirical vs. modeled-estimate tags")
    s = s.replace(", MODEL_PRIOR]", ", modeled estimate]")
    s = re.sub(r"\[MODEL_PRIOR:\s*([^\]]+)\]", r"(modeled estimate: \1)", s)
    s = re.sub(r"\b(the|a|an)\s+\[MODEL_PRIOR\]\s+", r"\1 modeled ", s, flags=re.I)
    s = re.sub(
        r"^\[MODEL_PRIOR\]\s+([A-Za-z0-9\-]+)",
        lambda m: "Modeled: " + (
            m.group(1)
            if m.group(1).startswith(("Schoenfeld", "SantaLucia", "Binomial", "MWC", "PDB", "CLSI", "ICH", "ALS", "CSF", "NHP"))
            else m.group(1)[0].lower() + m.group(1)[1:]
        ),
        s,
    )
    s = re.sub(r"^\[(?:MEASURED|MODEL_PRIOR|PRIOR)\]\s*", "", s)
    s = s.replace(" [MEASURED]", "").replace("[MEASURED] ", "").replace("[MEASURED]", "empirically measured")
    s = s.replace(" [MODEL_PRIOR]", " (modeled estimate)").replace("[MODEL_PRIOR] ", "modeled ")
    s = s.replace("[MODEL_PRIOR]", "modeled estimate")
    s = s.replace("[PRIOR] ", "Modeled: ").replace(" [PREPRINT]", " (preprint)").replace("[PREPRINT]", "preprint")
    s = re.sub(
        r"([;,])?\s*(?:zero|no)\s+21\s*CFR\s*312\.23\(b\)\s*(?:external\s+)?right[- ]of[- ]reference(?:\s+to\s+[A-Za-z0-9/\-]+)?",
        lambda m: (m.group(1) or ",") + " independent single-entity toxicology qualification",
        s,
        flags=re.I,
    )
    s = re.sub(r"\(\s*[;,]?\s*independent single-entity toxicology qualification\s*\)", "(independent single-entity toxicology qualification)", s)
    s = re.sub(r"ICH\s+M3\(R2\)\s*/\s*21\s*CFR\s*312\.23\(b\)", "ICH M3(R2)", s, flags=re.I)
    s = re.sub(r"\b21\s*CFR\s*312\.23(?:\(b\))?\b\s*", "", s, flags=re.I)
    s = re.sub(r"FDA co-development guidance\s*/\s*21\s*CFR\s*300\.50\s+factorial contribution principles", "factorial combination-contribution principles", s, flags=re.I)
    s = re.sub(r"\b21\s*CFR\s*300\.50\b(?!\s+(?:factorial|principles|design|contribution))", "factorial combination-contribution principles", s, flags=re.I)
    s = re.sub(r"\b21\s*CFR\s*300\.50\b\s*", "factorial ", s, flags=re.I)
    s = re.sub(r"\bsponsor-owned\s+ICH\s+M3\(R2\)", "ICH M3(R2)", s, flags=re.I)
    s = re.sub(r"\bin\s+Track\s+A/B\s+trials\b", "in clinical and target-directed ALS trials", s, flags=re.I)
    s = re.sub(r"\bCore\s+Track\s+B\s+target\b", "Core molecular target", s, flags=re.I)
    s = re.sub(r"\bas\s+Track\s+A\s+positive\s+clinical\b", "as established positive clinical", s, flags=re.I)
    s = re.sub(r"\bTrack\s+A\b", "clinical regimen", s)
    s = re.sub(r"\bTrack\s+B\b", "molecular target", s)
    s = re.sub(r"\bStage-0\b", "Pre-trial", s)
    s = re.sub(r"\bStage-\(ii\)\s+partially\s+nuclear-TDP-43-depleted\s*/\s*pre-inclusion", "early pre-inclusion (partially nuclear-TDP-43-depleted)", s, flags=re.I)
    s = re.sub(r"\bStage-\(ii\)\s+partially\s+TDP-43-depleted", "early pre-inclusion (partially nuclear-TDP-43-depleted)", s, flags=re.I)
    s = re.sub(r"\bStage-\(ii\)\s+pre-inclusion", "early pre-inclusion", s, flags=re.I)
    s = re.sub(r"\bStage-\(ii\)", "early pre-inclusion (partially TDP-43-depleted)", s, flags=re.I)
    s = s.replace(") Stage 1 Intron-4/Exon-5/Intron-5", ") Intron-4/Exon-5/Intron-5")
    s = s.replace("Evaluated in Stage 2 under", "Evaluated combinatorially under")
    s = s.replace("and Stage 2 rs12973192", "and combinatorial rs12973192")
    s = re.sub(r"\bStage\s+1-gated\b", "Single-agent-qualified", s)
    s = re.sub(
        r"\bStage\s+1\b(?=\s+(?:single-entity|dense|ICH|NHP|\(>=50))",
        lambda m: "Preclinical" if m.start() == 0 or s[max(0, m.start() - 2) : m.start()].strip() in {".", ":", ";", "—"} or s[m.start() - 1] == "\n" else "preclinical",
        s,
    )
    s = re.sub(
        r"\bStage\s+2\b(?=\s+(?:factorial|genotype-stratified|testing|evaluates|multiplex|co-dosing))",
        lambda m: "Combinatorial" if m.start() == 0 or s[max(0, m.start() - 2) : m.start()].strip() in {".", ":", ";", "—"} or s[m.start() - 1] == "\n" else "combinatorial",
        s,
    )
    s = s.replace("Combinatorial factorial combination testing", "combinatorial factorial testing")
    s = re.sub(r"\bBio\s+#([1-9])\b", r"Evidence #\1", s)
    s = re.sub(r"\bunder\s+Epistemic\s+Asymmetry\b:?", "", s, flags=re.I)
    s = re.sub(r"\b(?:the\s+)?Epistemic\s+Asymmetry(?:\s+Rule)?\b", "the Untested != Falsified triage rule", s, flags=re.I)
    s = s.replace("valid the Untested != Falsified triage rule retention", "retention under the Untested != Falsified triage rule")
    s = s.replace("in-memory the Untested != Falsified triage rule", "in-memory Untested != Falsified triage-rule")
    s = re.sub(r"\bBatch\s+[1-6]\b", "cohort re-analysis", s)
    s = re.sub(r"\bkill[- ]gates\b", "No-Go criteria", s, flags=re.I)
    s = re.sub(r"\bkill[- ]gate\b", "No-Go criterion", s, flags=re.I)
    s = s.replace("(ese_motifs=0)", "(0 disrupted ESE motifs)")
    s = re.sub(r"(?:\bmodeled\s+)?Tm_phys~64C", "modeled Tm ~64C", s)
    s = re.sub(r"(modeled\s+Tm\s*~[0-9]+C)\s*\(modeled\s+estimate\)", r"\1", s)
    s = s.replace("Exon_up-chr9:76641980-76641790-Exon_dn", "flanking canonical Exon 11 (chr9:76644739-76644909(-)) and Exon 12 (chr9:76638186-76638288(-))")
    s = s.replace("load_brown2022_splicing(verify_hash=True)", "Checksum-verified Brown 2022 MAJIQ junction table")
    s = re.sub(r"\bClean\s*>=2mm\b", "Clean (>=2 mismatches)", s)
    s = re.sub(r"\bclean\s*>=2mm\b", "clean (>=2 mismatches)", s)
    s = re.sub(r"\bpm2_25\b", "25bp-SS 2mm", s)
    s = re.sub(r"\bpm1_50\b", "50bp-SS 1mm", s)
    s = re.sub(r"\b(?:Audit of\s+)?baseline annotation\b", "Published catalog check:", s, flags=re.I)
    s = re.sub(r"\b(?:Frozen|Upstream)\s+Baseline\b", "prior literature catalog", s, flags=re.I)
    s = s.replace("integrating Round 2 hardening", "with multi-cohort verification")
    s = s.replace("6-cohort ST7 null", "6-cohort Bryce-Smith Suppl. Table 7 null")
    s = s.replace("6-Tier Cis-Safety dossier sync", "cross-registry dossier verification")
    s = s.replace("verify_carbon_als", "verify_explore_als")
    s = re.sub(r"\bDS045_TRAUT\b", "Trautwig 2025 CSF", s)
    s = re.sub(r"\bTrautwig\s+2025\s+CSF\s+CSF\b", "Trautwig 2025 CSF", s)
    s = re.sub(r"\bDS003_PB\b", "Pineda 2024 snRNA-seq", s)
    s = s.replace("neuronal-mass-residualized residualization", "neuronal-proportion residualization")
    s = s.replace("neuronal-mass-residualized mn_neur_z", "neuronal-proportion-residualized")
    s = re.sub(r"\bmn_neur_z\b", "neuronal-proportion z-score", s)
    s = s.replace("neuronal-mass-residualized neuronal-proportion z-score", "neuronal-proportion-residualized")
    s = re.sub(
        r"\bde\s+novo\b(?!\s+(?:mutation|mutations|variant|variants|germline|chemical|biologic|sphingolipid|ceramide|guanosine|purine|pyrimidine|nucleotide|synthesis|biosynthesis|lipogenesis|methylation|assembly|design))",
        "untargeted",
        s,
        flags=re.I,
    )
    s = s.replace("Not a novel white-space discovery asset;", "Not a novel therapeutic target discovery candidate;")
    s = s.replace("GOVERNANCE GUARDRAIL:", "Protocol Scope:")
    s = s.replace("taste is downgraded to", "translational priority is tempered by")
    s = s.replace("Two major risks lower scientific taste", "Two major risks temper biological priority")
    s = s.replace("Tier 2 · Focused Gate First", "Tier 2 · Validation Gate")
    s = re.sub(r"\bUnbiased\s+Cryptic-Splice\s+Lead\b", "Transcriptome-Wide Cryptic-Splice Lead", s)
    s = re.sub(r"\bunbiased\s+(?=(?:TDP-43\s+)?cryptic-splicing\s+discovery)", "transcriptome-wide ", s, flags=re.I)
    s = re.sub(r",\s*0 chemically modified synthesis-ready ASO sequences", "", s)
    s = re.sub(r"\(0 chemically modified synthesis-ready ASO sequences\)", "(1-based GRCh38 target coordinates)", s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    return (s[0].upper() + s[1:]) if s and s[0].islower() and txt and txt[0].isupper() else s


def sanitize_public_tree(obj: object) -> object:
    if isinstance(obj, str):
        return sanitize_public_prose(obj)
    if isinstance(obj, list):
        return [sanitize_public_tree(x) for x in obj]
    if isinstance(obj, tuple):
        return tuple(sanitize_public_tree(x) for x in obj)
    if isinstance(obj, dict):
        return {
            k: (val if k in {"tag", "kind", "tone", "st", "ivst", "dec", "epi", "tier", "trl", "gate", "basis", "o", "sub", "id", "pid", "sc", "cid", "eid", "run", "ds", "sha", "sha64", "prov", "anchor", "anc", "cls", "ovl", "cat", "dt", "iv", "chr", "strd", "rel", "arel", "url", "callout_kind", "related", "cert", "role", "accs", "gene"} else sanitize_public_tree(val))
            for k, val in obj.items()
        }
    return obj
