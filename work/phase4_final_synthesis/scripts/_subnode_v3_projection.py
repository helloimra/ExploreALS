"""Project frozen registries/subnode_dissection.csv rows into Dossier Standard v3 (NIH IDG TDL + Objective TSA, 0 '/100' scores)."""
from __future__ import annotations

import re

SUBNODE_TDL: dict[str, str] = {
    "C3": "Tclin",
    "CHIT1": "Tchem",
    "GPNMB": "Tbio (Ph2 ADC)",
    "C1QA": "Tbio (Ph2/3 mAb)",
    "C1QB": "Tbio (Ph2/3 mAb)",
    "C1QC": "Tbio (Ph2/3 mAb)",
}

SUBNODE_TSA: dict[str, str] = {
    "NSF": "HIGH_ESSENTIALITY",
    "YKT6": "HIGH_ESSENTIALITY",
    "SCFD1": "HIGH_ESSENTIALITY",
    "STX5": "HIGH_ESSENTIALITY",
    "SEC22B": "HIGH_ESSENTIALITY",
    "C3": "SYSTEMIC_IMMUNE",
    "C1QA": "SYSTEMIC_IMMUNE",
    "C1QB": "SYSTEMIC_IMMUNE",
    "C1QC": "SYSTEMIC_IMMUNE",
    "C4B": "SYSTEMIC_IMMUNE",
    "CHMP7": "SELECTIVITY_GATE",
    "CHMP2B": "SELECTIVITY_GATE",
    "G2E3": "SELECTIVITY_GATE",
    "GOSR1": "SELECTIVITY_GATE",
    "GDI2": "SELECTIVITY_GATE",
    "GPNMB": "SELECTIVITY_GATE",
    "CHIT1": "LOW_CONSTRAINT",
    "CHI3L1": "LOW_CONSTRAINT",
    "CHI3L2": "LOW_CONSTRAINT",
}

VERDICT_LABELS: dict[str, str] = {
    "KEEP_EXPLORATORY_UNPROVEN": "Keep · Exploratory",
    "KEEP_EXPLORATORY_UNPROVEN (LEAD SUB-NODE)": "Keep · Exploratory (Lead Sub-Node)",
    "KEEP_EXPLORATORY_UNPROVEN (C9-ASYM CLAIM REFUTED)": "Keep · Exploratory (C9-Asym Refuted)",
    "KEEP_EXPLORATORY_UNPROVEN_PRIMARY_SUBNODE": "Keep · Exploratory (Primary Sub-Node)",
    "KEEP_EXPLORATORY_UNPROVEN_UNBUNDLED_SECONDARY": "Keep · Exploratory (Unbundled Secondary)",
    "RECLASSIFY_BENCHMARK_OR_BIOMARKER": "Reclassify · Fluid Biomarker",
    "RECLASSIFY_BENCHMARK_OR_BIOMARKER (WRONG SIGN FOR INHIBITION)": "Reclassify · Biomarker (Neuroprotective Sign)",
    "DROP_FROM_BUNDLE_PASSENGER_PARALOG": "Drop · Passenger Paralog",
    "DROP_FROM_BUNDLE_ESSENTIAL_HOUSEKEEPING_PASSENGER": "Drop · Essential Housekeeping Passenger",
    "DROP_FROM_BUNDLE_INFRAME_PASSENGER": "Drop · In-Frame Splicing Passenger",
    "DROP_FROM_BUNDLE_PAN_ESSENTIAL_TOXIC_TARGET": "Drop · Pan-Essential Toxic Target",
    "DROP_FROM_BUNDLE_CSF_PEPTIDE_ARTIFACT": "Drop · Passive CSF Leakage Artifact",
    "DROP (FALSIFIED_CLINICAL)": "Drop · Falsified Clinical (MERIDIAN)",
    "DROP (ARTIFACT_CONFOUNDED)": "Drop · Confounded RCCX / Null CSF",
}

COLONLESS_VERDICT_PROSE: dict[str, str] = {
    "KEEP_EXPLORATORY_UNPROVEN_PRIMARY_SUBNODE": (
        "Retained as primary unbundled C014 nuclear-envelope surveillance sub-node requiring titrated <=35–50% knockdown or selective SUN1-CHMP7 nuclear-import blockade."
    ),
    "KEEP_EXPLORATORY_UNPROVEN_UNBUNDLED_SECONDARY": (
        "Strictly unbundled from CHMP7 due to neuronal ANXA11 membrane-repair and autophagy requirements; gated on head-to-head single vs. dual partial knockdown under NE rupture challenge."
    ),
}

PREFIX_REPLACEMENTS = (
    ("HIGH_LIABILITY_FOR_COMPLETE_ABLATION:", "High liability for complete ablation —"),
    ("PARALOG_COMPENSATED_IN_MITOSIS_BUT_NEURONAL_REPAIR_AND_AUTOPHAGY_REQUIRED:", "Paralog-compensated in mitosis, neuronal repair & autophagy required —"),
    ("INTRATHECAL_ASO_PARTIAL_LOWERING_OR_NUCLEAR_IMPORT_BLOCKADE:", "Intrathecal ASO partial lowering or nuclear-import blockade —"),
    ("STRICTLY_UNBUNDLED_EXPLORATORY_PARTIAL_ASO:", "Strictly unbundled exploratory partial ASO —"),
)

SCORE_100_RE = re.compile(r";?\s*(?:5D\s+liability|gene-liability)\s*=\s*[0-9.]+/100\s*(?:\([^)]*\))?\.?", re.IGNORECASE)
INLINE_100_RE = re.compile(r"\b100/100\s+")


def project_subnode_v3(s: dict[str, str], clean_ui_fn) -> dict[str, str]:
    gene = s["gene_symbol"]
    gnomad = SCORE_100_RE.sub("", clean_ui_fn(s["gnomad_essentiality_check"])).strip()
    if gnomad and not gnomad.endswith("."):
        gnomad += "."
    drug = clean_ui_fn(s["druggability_check"]).strip()
    for raw_p, nice_p in PREFIX_REPLACEMENTS:
        gnomad = gnomad.replace(raw_p, nice_p)
        drug = drug.replace(raw_p, nice_p)

    vclean = re.sub(r";\s*mislabeled alt-3'ss in [^)]+", "", clean_ui_fn(s["subnode_verdict"])).strip()
    if ":" in vclean:
        vhead, vrest = vclean.split(":", 1)
        vcode = vhead.strip()
        vlbl = VERDICT_LABELS[vcode]
        vbody = INLINE_100_RE.sub("", vrest.strip())
    else:
        vcode = vclean
        vlbl = VERDICT_LABELS[vcode]
        vbody = COLONLESS_VERDICT_PROSE[vcode]

    out = {
        "id": s["subnode_id"],
        "par": s["parent_carbon_id"],
        "gene": gene,
        "role": s["molecular_role"],
        "tdl": SUBNODE_TDL.get(gene, "Tbio"),
        "tsa": SUBNODE_TSA[gene],
        "gnomad": gnomad,
        "drug": drug,
        "vraw": vcode,
        "vlbl": vlbl,
        "vbody": vbody,
    }
    assert "/100" not in (out["gnomad"] + out["drug"] + out["vbody"]), f"Residual /100 score in {s['subnode_id']}"
    return out
