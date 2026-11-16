"""Export zero-CDN, WCAG Light/Dark GitHub Pages bundle to reports/github_pages/ (README.md + .gitignore + docs/index.html + docs/monographs/*.html)."""
from __future__ import annotations

from pathlib import Path
import re

from _public_web_css import compile_public_css

CLASS_ATTR_RE = re.compile(r"""class(?:Name)?\s*=\s*['"]([^'"]+)['"]""")
JS_QUOTED_STR_RE = re.compile(r"""['"]([A-Za-z0-9_:\-\[\]\(\)\./%]+(?:\s+[A-Za-z0-9_:\-\[\]\(\)\./%]+)*)['"]""")
TAILWIND_LIKE_RE = re.compile(
    r"^(?:(?:sm|md|lg|xl|hover|focus|last):)?(?:"
    r"kpi-btn|tab-btn|antialiased|block|inline-block|flex|grid|table-cell|hidden|relative|absolute|sticky|"
    r"top-\d+|bottom-0|left-0|right-0|z-\d+|flex-1|flex-col|flex-wrap|flex-nowrap|shrink-0|"
    r"items-(?:start|center|baseline)|justify-between|grid-cols-[^\s]+|col-span-\d+|"
    r"(?:w|h)-(?:full|auto|px|0\.5|1|1\.5|2|2\.5|3|4)|min-[wh]-[^\s]+|max-[wh]-[^\s]+|overflow-[^\s]+|truncate|break-words|whitespace-nowrap|list-disc|"
    r"(?:p|m)(?:x|y|t|r|b|l)?-(?:0|0\.5|1|1\.5|2|2\.5|3|3\.5|4|6|auto)|gap(?:-[xy])?-(?:0\.5|1|1\.5|2|2\.5|3)|"
    r"space-y-(?:0\.5|1|1\.5|2|2\.5|3|3\.5)|rounded(?:-(?:sm|lg|full))?|border(?:-(?:2|t|r|b|b-0|l-2|l-4|dashed|collapse))?|"
    r"(?:bg|text|border|border-l|divide|accent|ring)-\[var\(--[a-z-]+\)\]|divide-y|"
    r"font-(?:mono|normal|medium|semibold|bold)|italic|text-(?:xs|sm|base|lg|left|center|right)|"
    r"leading-(?:snug|relaxed)|tabular-nums|align-(?:top|middle)|underline|decoration-(?:dotted|solid)|underline-offset-2|"
    r"opacity-\d+|shadow-sm|ring-2|outline-none|transition|rotate-45|cursor-(?:pointer|help)|select-none|pointer-events-none"
    r")$"
)

THEME_HEAD_INIT = (
    '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
    '  <meta name="color-scheme" content="light dark" />\n'
    '  <meta name="author" content="Ricardo Agoga (Independent Researcher)" />\n'
    '  <meta name="description" content="ExploreALS v1.2 — Unified 59-Candidate ALS Drug &amp; Genetic Target Portfolio, '
    '19 Single-Gene Sub-Nodes, 26 Coordinate-Only GRCh38 Search Windows (0 chemically modified synthesis-ready ASO sequences), and Computational Replication Package." />\n'
    "  <script>window.PUBLIC_WEB_EXPORT=true;(function(){try{var t=localStorage.getItem('exploreals-theme');"
    "if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(_e){}})();</script>"
)

THEME_BTN_HTML = (
    '<button id="theme-toggle-btn" type="button" data-cycle-theme="1" aria-label="Color theme: Auto" '
    'title="Switch color theme (System / Light / Dark)" '
    'class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] '
    'bg-[var(--background)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] font-mono text-xs cursor-pointer">'
    "Theme: Auto</button>"
)

THEME_BODY_JS = """
(function(){
  let memTheme = 'auto';
  try {
    const saved = localStorage.getItem('exploreals-theme');
    if(saved === 'light' || saved === 'dark') memTheme = saved;
  } catch(_e) {}
  function applyTheme(mode){
    memTheme = (mode === 'light' || mode === 'dark') ? mode : 'auto';
    if(memTheme === 'light' || memTheme === 'dark') document.documentElement.setAttribute('data-theme', memTheme);
    else document.documentElement.removeAttribute('data-theme');
    try {
      if(memTheme === 'auto') localStorage.removeItem('exploreals-theme');
      else localStorage.setItem('exploreals-theme', memTheme);
    } catch(_e) {}
    const btn = document.getElementById('theme-toggle-btn');
    if(btn){
      const lbl = memTheme === 'light' ? 'Light' : (memTheme === 'dark' ? 'Dark' : 'Auto');
      btn.textContent = 'Theme: ' + lbl;
      btn.setAttribute('aria-label', 'Color theme: ' + lbl);
    }
  }
  applyTheme(memTheme);
  document.addEventListener('click', function(ev){
    const raw = ev.target;
    const el = raw && raw.closest ? raw : (raw && raw.parentElement ? raw.parentElement : null);
    if(el && el.closest && el.closest('[data-cycle-theme]')){
      ev.preventDefault();
      applyTheme(memTheme === 'auto' ? 'light' : (memTheme === 'light' ? 'dark' : 'auto'));
    }
  });
})();
"""

GITHUB_README_MD = """# ExploreALS v1.2 — Unified ALS Therapeutic & Genetic Target Portfolio Explorer + Computational Replication Package

**Live Interactive Explorer (6 Tabs):** [https://helloimra.github.io/ExploreALS/](https://helloimra.github.io/ExploreALS/)
**Author:** Ricardo Agoga (Independent Researcher) · [helloimra@proton.me](mailto:helloimra@proton.me) · [github.com/helloimra/ExploreALS](https://github.com/helloimra/ExploreALS)

## Overview
`ExploreALS v1.2` synthesizes **59 ALS drug and genetic target candidates**, **19 single-gene sub-nodes** de-bundled from multi-gene composite axes, and **26 Coordinate-Only Cis-Regulatory Search Windows** (`0` chemically modified synthesis-ready ASO sequences) across `48` SHA-256-verified open-access human ALS cohorts (`NYGC GSE153960`, `Pineda 2024`, `Edinburgh GSE290359`, `Zhang 2026` spatial, `Spillman 2026` fraction DIA, `Trautwig 2025` & `Oh 2023` living CSF proteomics, `Brown/Ma 2022` & `Bryce-Smith/Zeng 2025` TDP-43 splicing/APA, and `Bye 2025` sALS patient iPSC-MN drug screening).

## 3-Level Independent Computational Replication Quickstart

```bash
# Level 1 (<10s, 0 MB extra data): Verify all 16 CSV schemas, FKs, Epistemic Asymmetry & 216/216 64-char SHA-256s
uv sync --frozen
uv run python scripts/verify_carbon_als.py --mode cached

# Level 2 (~5s cached / full with staged data/): Run all 8 single-command Flagship Monograph Reproducers
uv run python scripts/reproduce_all.py --flagship-only

# Stage open datasets (Tier A release bundle + Tier B direct publisher/EuropePMC HTTPS + SHA-256 verification)
uv run python scripts/fetch_open_datasets.py --list
uv run python scripts/fetch_open_datasets.py --source release

# Level 3 (~2s): Rebuild zero-CDN 6-tab Explorer & 8 Monographs and run archive-aware sanitization gate
uv run python work/phase4_final_synthesis/scripts/02_render_phase4_synthesis.py --public-docs-only
uv run python scripts/audit_public_sanitization.py --target .
```

### Standalone Tier 1 & Tier 2 Translational Monographs
- **Tier 1 (`Actionable Now`):** [#1 S06 · SARM1](https://helloimra.github.io/ExploreALS/monographs/S06.html) · [#2 C006 · KCNQ2](https://helloimra.github.io/ExploreALS/monographs/C006.html) · [#3 S07 · Aldesleukin](https://helloimra.github.io/ExploreALS/monographs/S07.html)
- **Tier 2 (`Focused Preclinical / Biofluid Gate First`):** [#4 C001 · UNC13A](https://helloimra.github.io/ExploreALS/monographs/C001.html) · [#5 C002 · STMN2](https://helloimra.github.io/ExploreALS/monographs/C002.html) · [#6 C007 · IL1RL1 / sST2](https://helloimra.github.io/ExploreALS/monographs/C007.html) · [#7 DN-01 · ATG4B](https://helloimra.github.io/ExploreALS/monographs/DN-01.html) · [#8 DN-04 · CELF5](https://helloimra.github.io/ExploreALS/monographs/DN-04.html)

## Licensing, Disclaimers & Open-Data Provenance
- **Dual Software & Data License:** Python source code (`src/`, `scripts/`, `pipelines/`, `work/**/*.py`) is licensed under the **MIT License** ([LICENSE](./LICENSE)); original curated registries (`registries/*.csv`), schemas, and monographs are licensed under **CC BY 4.0** ([LICENSE-DATA.md](./LICENSE-DATA.md)). Non-`CC-BY` publisher supplements (`Tier B`) are never re-hosted and are fetched directly from canonical publisher HTTPS endpoints.
- **Preclinical Research Only — Not Medical Advice:** `ExploreALS v1.2` is an independent preclinical and translational research resource intended solely for scientific hypothesis generation. Nothing in this repository or explorer constitutes medical advice, clinical trial recruitment, or a treatment recommendation; individuals with ALS and caregivers should always consult their neurologist or ALS care team before starting, stopping, or modifying any therapy.
- **AI-Assisted Workflow Disclosure:** Developed via human-directed multi-agent AI research workflows paired with deterministic Python statistical recomputation across open-access human ALS datasets and primary-source verification (`PubMed`, `Europe PMC`, `ClinicalTrials.gov`). Quantitative contrasts (`216/216` 64-char SHA-256 anchored) are programmatically audited and separated from modeling priors (`[MODEL_PRIOR]`), though synthesis prose may contain residual errors — always verify against linked primary sources before experimental use.
- **Data & Tool Attributions:** Google DeepMind AlphaGenome (`v1` API & Atlas `AVI`; non-commercial research use only), NIH GTEx (`v8 / v10`), Open Targets (`v4`), gnomAD (`v4.1`), Ensembl/GENCODE (`v46`), ChEMBL (`v34`), UniProt, RCSB PDB, and ClinicalTrials.gov.
"""

GITIGNORE_TXT = """.venv/
__pycache__/
*.pyc
*.egg-info/
.env
.licenses/
.tmp/
releases/
work/.live_api_check/
/data/*
!/data/genomics_splicing/
/data/genomics_splicing/*
!/data/genomics_splicing/eligibility_v1.0/
!/data/genomics_splicing/eligibility_v1.0/**
!/data/transcriptomics/
/data/transcriptomics/*
!/data/transcriptomics/nygc_d001/
/data/transcriptomics/nygc_d001/*
!/data/transcriptomics/nygc_d001/provisional_unique_feature_map.csv
!/data/transcriptomics/ba9_bundle_v5/
!/data/transcriptomics/ba9_bundle_v5/**
"""


def collect_all_utility_tokens(blobs: list[str]) -> set[str]:
    tokens: set[str] = {"ring-2", "ring-[var(--primary)]", "border-2", "border-l-2", "flex", "flex-col", "hidden"}
    for blob in blobs:
        for m in CLASS_ATTR_RE.finditer(blob):
            for tok in m.group(1).split():
                if "${" not in tok and "'" not in tok and '"' not in tok:
                    tokens.add(tok)
        for m in JS_QUOTED_STR_RE.finditer(blob):
            for tok in m.group(1).split():
                if TAILWIND_LIKE_RE.match(tok):
                    tokens.add(tok)
    return tokens


def export_public_web_bundle(repo_dir: Path, agy_explorer_html: str, agy_mono_files: list[Path]) -> list[Path]:
    docs_dir = repo_dir / "docs"
    mono_out = docs_dir / "monographs"
    mono_out.mkdir(parents=True, exist_ok=True)
    for stale in mono_out.glob("*.html"):
        if stale.stem not in {p.stem for p in agy_mono_files}:
            stale.unlink()

    raw_monos = {p.stem: p.read_text(encoding="utf-8") for p in agy_mono_files}
    tokens = collect_all_utility_tokens([agy_explorer_html, THEME_BTN_HTML, *raw_monos.values()])
    head_bundle = f"{THEME_HEAD_INIT}\n  <style>\n{compile_public_css(tokens)}\n  </style>"
    agy_head_re = re.compile(
        r"<style>:where\(\.hidden\)\{display:none\}[^<]*</style>\s*"
        r'<script src="https://www\.gstatic\.com/antigravity/web/dev/tailwindcss\.min\.js"></script>'
    )
    assert agy_head_re.search(agy_explorer_html), "Expected AGY head style+script block in Explorer HTML"

    assert "<!-- THEME_TOGGLE_SLOT -->" in agy_explorer_html, "Expected <!-- THEME_TOGGLE_SLOT --> in Explorer HTML"
    pub_index = agy_head_re.sub(lambda _: head_bundle, agy_explorer_html, count=1)
    pub_index = pub_index.replace("<!-- THEME_TOGGLE_SLOT -->", THEME_BTN_HTML, 1)
    pub_index = pub_index.replace("</script>\n</body>", THEME_BODY_JS + "</script>\n</body>", 1)
    assert "gstatic.com" not in pub_index and "onclick=" not in pub_index.lower() and "wiki" not in pub_index.lower()
    idx_fp = docs_dir / "index.html"
    idx_fp.write_text(pub_index, encoding="utf-8")
    nojekyll_fp = docs_dir / ".nojekyll"
    nojekyll_fp.write_text("", encoding="utf-8")
    readme_fp = repo_dir / "README.md"
    readme_fp.write_text(GITHUB_README_MD, encoding="utf-8")
    gi_fp = repo_dir / ".gitignore"
    gi_fp.write_text(GITIGNORE_TXT, encoding="utf-8")
    written = [idx_fp, nojekyll_fp, readme_fp, gi_fp]

    for stem, mraw in sorted(raw_monos.items()):
        assert agy_head_re.search(mraw), f"Expected AGY head block in {stem}.html"
        mpub = agy_head_re.sub(lambda _: head_bundle, mraw, count=1)
        mpub = mpub.replace("../CARBON_ALS_INTERACTIVE_EXPLORER.html", "../index.html")
        mpub = re.sub(
            r'(<a id="explorer-back-link"[^>]+>&larr; Open in Full 59-Candidate Explorer</a>)',
            r'<div class="flex flex-wrap items-center gap-2">\1 ' + THEME_BTN_HTML.replace("py-1.5", "py-1") + "</div>",
            mpub,
            count=1,
        )
        mpub = mpub.replace("  </script></body></html>", THEME_BODY_JS + "  </script></body></html>", 1)
        assert "gstatic.com" not in mpub and "CARBON_ALS_INTERACTIVE_EXPLORER" not in mpub and "onclick=" not in mpub.lower() and "wiki" not in mpub.lower()
        mfp = mono_out / f"{stem}.html"
        mfp.write_text(mpub, encoding="utf-8")
        written.append(mfp)
    return written
