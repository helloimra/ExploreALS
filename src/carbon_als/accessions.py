"""Canonical ExploreALS accession mapping (EALS-001..EALS-052 + .k subunits) and collision-safe fuzzy resolver."""
from __future__ import annotations

import re

LEGACY_SUB_RANGE_RE = re.compile(
    r"(?<![A-Za-z0-9])(C0(?:0[1-9]|1\d|2[0-4]))-N([1-6])(?:\.\.|[-–])N?([1-6])(?![A-Za-z0-9])"
)
LEGACY_DN_RANGE_RE = re.compile(
    r"(?<![A-Za-z0-9])DN-(0[1-9]|1\d)(?:\.\.|[-–])(?:DN-)?(0[1-9]|1\d)(?![A-Za-z0-9])"
)
LEGACY_PROSE_TOKEN_RE = re.compile(
    r"(?<!FLAGSHIP-)(?<!candidates/)(?<!monographs/)(?<!reproduce_)(?<![0-9]_)(?<![A-Za-z0-9])"
    r"(C0(?:0[1-9]|1\d|2[0-4])|S0[1-9]|DN-(?:0[1-9]|1\d))(-N[1-6])?(?![A-Za-z0-9])(?![.]md\b)"
)
AMBIGUOUS_SHORT_BIO_TOKENS = frozenset({"c1", "c3", "c4", "c5", "c9", "s5", "s6"})

PRIMARY_SYMBOL_AND_ALIASES: dict[str, tuple[str, list[str]]] = {
    "C001": ("UNC13A", ["unc13a", "munc13-1", "munc13", "ly4256984", "trcn-1023", "trcn1023"]),
    "C002": ("STMN2", ["stmn2", "scg10", "qrl-201", "qrl201", "anqur", "conqur", "biib147"]),
    "C003": ("Ezogabine", ["ezogabine", "retigabine"]),
    "C004": ("Ceftriaxone", ["ceftriaxone", "eaat2", "slc1a2"]),
    "C005": ("TMS-SICI / NPTX2 Protocol", ["nptx2", "sici", "sdtc", "tms-sici", "excitability-protocol"]),
    "C006": ("KCNQ2", ["kcnq2", "kv7.2", "kv72", "qrl-101", "qrl101", "xen1101"]),
    "C007": ("IL1RL1 / sST2", ["il1rl1", "sst2", "st2", "st2l", "il-33", "il33", "astegolimab"]),
    "C008": ("Memantine", ["memantine"]),
    "C009": ("Trazodone", ["trazodone"]),
    "C010": ("Ropinirole", ["ropinirole", "ropals"]),
    "C011": ("Furosemide", ["furosemide", "nkcc1", "slc12a2"]),
    "C012": ("Perampanel", ["perampanel"]),
    "C013": ("Riluzole", ["riluzole"]),
    "C014": ("CHMP7 / CHMP2B", ["chmp7", "chmp2b", "escrt-iii", "escrt3"]),
    "C015": ("SCFD1 / G2E3", ["scfd1", "g2e3", "chr14q12", "14q12"]),
    "C016": ("FBXL5 / IREB2", ["fbxl5", "ireb2", "irp2"]),
    "C017": ("CHIT1 / GPNMB", ["chit1", "gpnmb", "chi3l1", "chi3l2", "ykl-40", "ykl40"]),
    "C018": ("C1q (C1QA/B/C)", ["c1q", "c1qa", "c1qb", "c1qc", "c4b", "anx005", "anx007"]),
    "C019": ("Baricitinib / JAK1", ["baricitinib", "jak1", "jak2", "nadals"]),
    "C020": ("Apilimod / PIKfyve", ["apilimod", "pikfyve", "lam-002a", "ait-101"]),
    "C021": ("Icerguastat", ["icerguastat", "ifb-088", "ifb088", "sephin1"]),
    "C022": ("DNAJB2", ["dnajb2", "hsj1", "dnajb2a", "dnajb2b"]),
    "C023": ("YKT6", ["ykt6", "sec22b", "stx5", "gosr1", "nsf", "gdi2"]),
    "C024": ("Pegcetacoplan", ["pegcetacoplan", "meridian", "empaveli"]),
    "S01": ("Dexmedetomidine", ["dexmedetomidine", "precedex"]),
    "S02": ("CuATSM", ["cuatsm", "cu-atsm"]),
    "S03": ("Mycophenolate mofetil", ["mycophenolate", "mmf", "mpa"]),
    "S04": ("Tamoxifen", ["tamoxifen"]),
    "S05": ("Lonafarnib / Tipifarnib", ["lonafarnib", "tipifarnib", "fti", "ftis", "zokinvy"]),
    "S06": ("SARM1", ["sarm1", "asha-624", "asha624", "sir2501", "nb-4746", "nb4746", "ly3873862", "dsrm-3716"]),
    "S07": ("Aldesleukin (IL-2)", ["aldesleukin", "il-2", "il2", "mirocals", "ld-il-2", "proleukin"]),
    "S08": ("Methylcobalamin", ["methylcobalamin", "rozebalamin", "mecbl", "jetals"]),
    "S09": ("Censavudine (TPN-101)", ["censavudine", "tpn-101", "tpn101", "line-1", "tyk2"]),
    "DN-01": ("ATG4B", ["atg4b"]),
    "DN-02": ("KALRN", ["kalrn", "kalirin"]),
    "DN-03": ("PTPRT", ["ptprt"]),
    "DN-04": ("CELF5", ["celf5"]),
    "DN-05": ("PRUNE2", ["prune2"]),
    "DN-06": ("PFKP", ["pfkp"]),
    "DN-07": ("TRAPPC12", ["trappc12"]),
    "DN-08": ("ELK1", ["elk1"]),
    "DN-09": ("DLGAP1", ["dlgap1"]),
    "DN-10": ("DPP6", ["dpp6"]),
    "DN-11": ("DPP10", ["dpp10"]),
    "DN-12": ("CFL1", ["cfl1", "cofilin"]),
    "DN-13": ("MAOB", ["maob", "mao-b", "rasagiline", "selegiline"]),
    "DN-14": ("PMX 205", ["pmx205", "pmx-205", "c5ar1"]),
    "DN-15": ("Lamotrigine", ["lamotrigine"]),
    "DN-16": ("Dolutegravir", ["dolutegravir", "triumeq", "lighthouse"]),
    "DN-17": ("Acetylcysteine", ["acetylcysteine", "nac", "n-acetylcysteine"]),
    "DN-18": ("Coenzyme Q10", ["coq10", "coenzyme-q10", "ubiquinone", "qals"]),
    "DN-19": ("L-Serine", ["l-serine", "lserine", "serine"]),
}


def legacy_to_accession(legacy_id: str) -> str:
    s = legacy_id.strip()
    if s in {"NONE", "PORTFOLIO_WIDE", ""}:
        return s
    m_sub = re.fullmatch(r"(C0(?:0[1-9]|1\d|2[0-4]))-N([1-9])", s)
    if m_sub:
        return f"{legacy_to_accession(m_sub.group(1))}.{m_sub.group(2)}"
    m_c = re.fullmatch(r"C0(0[1-9]|1\d|2[0-4])", s)
    if m_c:
        return f"EALS-{int(m_c.group(1)):03d}"
    m_s = re.fullmatch(r"S0([1-9])", s)
    if m_s:
        return f"EALS-{24 + int(m_s.group(1)):03d}"
    m_d = re.fullmatch(r"DN-(0[1-9]|1[0-9])", s)
    if m_d:
        return f"EALS-{33 + int(m_d.group(1)):03d}"
    if re.fullmatch(r"EALS-0(?:0[1-9]|[1-4]\d|5[0-2])(?:\.[1-9])?", s):
        return s
    raise ValueError(f"Unknown legacy candidate/subnode ID: {legacy_id!r}")


def accession_to_legacy(accession_id: str) -> str:
    s = accession_id.strip()
    if s in {"NONE", "PORTFOLIO_WIDE", ""}:
        return s
    m = re.fullmatch(r"EALS-0(0[1-9]|[1-4]\d|5[0-2])(?:\.([1-9]))?", s)
    if not m:
        raise ValueError(f"Invalid ExploreALS accession ID: {accession_id!r}")
    num = int(m.group(1))
    sub = m.group(2)
    base = f"C{num:03d}" if num <= 24 else (f"S{num - 24:02d}" if num <= 33 else f"DN-{num - 33:02d}")
    return f"{base}-N{sub}" if sub else base


def translate_legacy_tokens_in_prose(text: str) -> str:
    s = LEGACY_SUB_RANGE_RE.sub(
        lambda m: f"{legacy_to_accession(m.group(1))}.{m.group(2)}–{legacy_to_accession(m.group(1))}.{m.group(3)}",
        text,
    )
    s = LEGACY_DN_RANGE_RE.sub(
        lambda m: f"{legacy_to_accession('DN-' + m.group(1))}–{legacy_to_accession('DN-' + m.group(2))}",
        s,
    )

    def _repl(m: re.Match[str]) -> str:
        base = legacy_to_accession(m.group(1))
        sub = m.group(2)
        return f"{base}.{sub[2:]}" if sub else base

    return LEGACY_PROSE_TOKEN_RE.sub(_repl, s)


def resolve_candidate_query(
    query: str,
    rank_to_accession: dict[int, str] | None = None,
    subnode_gene_to_accession: dict[str, tuple[str, str]] | None = None,
) -> tuple[str | None, str | None]:
    """Resolve an accession, legacy alias (c6/c006/dn013/s06), #rank, or gene/drug slug to (parent_eals, subnode_eals)."""
    q = query.strip()
    if not q:
        return None, None
    ql = q.lower()
    m_rk = re.fullmatch(r"#([1-9]|[1-4]\d|5[0-2])", ql)
    if m_rk and rank_to_accession and int(m_rk.group(1)) in rank_to_accession:
        return rank_to_accession[int(m_rk.group(1))], None
    m_ea = re.fullmatch(r"(?:eals|ea)[-_ ]?0*([1-9]|[1-4]\d|5[0-2])(?:[.-]n?([1-9]))?", ql)
    if m_ea:
        par = f"EALS-{int(m_ea.group(1)):03d}"
        return par, (f"{par}.{m_ea.group(2)}" if m_ea.group(2) else None)
    m_pad = re.fullmatch(r"0(0[1-9]|[1-4]\d|5[0-2])", ql)
    if m_pad:
        return f"EALS-{int(m_pad.group(1)):03d}", None
    m_c = re.fullmatch(r"c[-_ ]?0*([1-9]|1\d|2[0-4])(?:[-_.]n?([1-9]))?", ql)
    if m_c:
        par = f"EALS-{int(m_c.group(1)):03d}"
        return par, (f"{par}.{m_c.group(2)}" if m_c.group(2) else None)
    m_s = re.fullmatch(r"s[-_ ]?0*([1-9])", ql)
    if m_s:
        return f"EALS-{24 + int(m_s.group(1)):03d}", None
    m_dn = re.fullmatch(r"dn?[-_ ]?0*([1-9]|1[0-9])", ql)
    if m_dn and (ql.startswith("dn") or len(re.sub(r"[^0-9]", "", ql)) >= 2):
        return f"EALS-{33 + int(m_dn.group(1)):03d}", None
    slug = re.sub(r"[^a-z0-9]+", "", ql)
    if subnode_gene_to_accession and slug in subnode_gene_to_accession:
        return subnode_gene_to_accession[slug]
    for leg, (sym, aliases) in PRIMARY_SYMBOL_AND_ALIASES.items():
        all_s = {re.sub(r"[^a-z0-9]+", "", sym.lower()), *(re.sub(r"[^a-z0-9]+", "", a.lower()) for a in aliases)}
        if slug and slug in all_s:
            return legacy_to_accession(leg), None
    return None, None
