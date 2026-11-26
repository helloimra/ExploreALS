"""Self-contained Generative UI HTML template (Tailwind + semantic CSS vars, >=12px text, side-pane optimized)."""
from __future__ import annotations

HTML_HEAD_AND_BODY = """<!DOCTYPE html>
<!-- __SHA12_STAMP__ -->
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>ExploreALS v1.4: ALS Target Triage, Splice Windows &amp; Replication Explorer</title>
  <style>:where(.hidden){display:none}.text-xs:not(.leading-snug):not(.leading-relaxed){line-height:1.5}table{border-collapse:collapse;width:100%}th,td{padding:6px 8px;vertical-align:top}.gate-clamp[data-clamped="true"]{position:relative;max-height:7.25rem;overflow:hidden}.gate-clamp[data-clamped="true"]::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1.75rem;background:linear-gradient(to bottom,transparent,var(--background));pointer-events:none}@media(min-width:1024px){.p-workbench{height:clamp(310px,calc(100vh - 13.25rem),760px);height:clamp(310px,calc(100dvh - 13.25rem),760px)}}@media(min-width:1280px){.p-workbench{height:clamp(340px,calc(100vh - 11.75rem),780px);height:clamp(340px,calc(100dvh - 11.75rem),780px)}}.iv-table-cap{max-height:420px}@media(min-width:1024px){.iv-table-cap,.iv-detail-cap{max-height:clamp(310px,calc(100vh - 5.75rem),820px);max-height:clamp(310px,calc(100dvh - 5.75rem),820px)}}</style>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-4 m-0 text-xs">
  <div class="max-w-[1440px] mx-auto space-y-3.5">
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2">
      <div class="flex flex-wrap items-start justify-between gap-2">
        <div class="flex-1 min-w-[200px]">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="px-2 py-0.5 rounded font-mono font-semibold bg-[var(--primary)] text-[var(--primary-foreground)] text-xs">ExploreALS v1.4</span>
            <h1 class="text-base font-semibold text-[var(--foreground)]">ALS Therapeutic &amp; Genetic Target Triage, Candidate Reports &amp; Replication Explorer</h1>
          </div>
          <div id="hdr-sub">
            <p class="text-[var(--muted-foreground)] text-xs mt-1">Independent computational triage of 53 ALS therapeutic &amp; biomarker hypotheses across 43 open human &amp; preclinical datasets (Mendelian/GWAS genetics, TDP-43 cryptic splicing &amp; polyadenylation, spatial/snRNA/subcellular omics, CSF proteomics, clinical trial subgroups &amp; patient iPSC-MN screens) &middot; 18 complex/panel subunits &middot; 28 1-based GRCh38 cis-regulatory target windows</p>
            <p class="text-[var(--muted-foreground)] text-xs mt-1">Curated by <strong class="text-[var(--foreground)]">Ricardo Agoga</strong> &middot; <a href="mailto:helloimra@proton.me" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">helloimra@proton.me</a> &middot; <a href="https://github.com/helloimra/ExploreALS" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">github.com/helloimra/ExploreALS &nearr;</a> &middot; <span class="font-mono text-[var(--warning)]">Preclinical Research Only (Not Medical Advice)</span></p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0"><!-- THEME_TOGGLE_SLOT --></div>
      </div>
      <div class="pt-2 border-t border-[var(--card-border)]">
        <div class="grid grid-cols-2 sm:flex sm:flex-wrap gap-1.5 w-full sm:w-auto" id="tab-bar" role="tablist" aria-label="Explorer Views">
          <button id="tab-btn-home" type="button" role="tab" aria-selected="true" aria-controls="view-home" data-tab="home" class="tab-btn col-span-2 flex items-center gap-1.5 px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="shrink-0"><path d="M3 10.5L12 3l9 7.5"/><path d="M5 9.5V20a1 1 0 0 0 1 1h4.5v-6h3v6H18a1 1 0 0 0 1-1V9.5"/></svg><span>Home &middot; Updates</span></button>
          <button id="tab-btn-portfolio" type="button" role="tab" aria-selected="false" aria-controls="view-portfolio" data-tab="portfolio" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">1. Triage Table (53)</button>
          <button id="tab-btn-dossiers" type="button" role="tab" aria-selected="false" aria-controls="view-dossiers" data-tab="dossiers" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">2. Candidate Reports (53)</button>
          <button id="tab-btn-intervals" type="button" role="tab" aria-selected="false" aria-controls="view-intervals" data-tab="intervals" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">3. Splice Windows (28)</button>
          <button id="tab-btn-replication" type="button" role="tab" aria-selected="false" aria-controls="view-replication" data-tab="replication" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">4. Replication</button>
        </div>
      </div>
    </div>

    <div class="hidden sm:grid sm:grid-cols-3 lg:grid-cols-6 gap-2.5" id="kpi-bar">
      <button type="button" data-quick-filter="ALL" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Evaluated Hypotheses</div>
        <div class="text-lg font-bold font-mono tabular-nums mt-0.5">53 <span class="text-xs font-normal text-[var(--muted-foreground)]">(6 Cohorts)</span></div>
      </button>
      <button type="button" data-quick-filter="TIER12" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Tier 1 + Tier 2 Leads</div>
        <div class="text-lg font-bold font-mono tabular-nums text-[var(--success)] mt-0.5">8 <span class="text-xs font-normal text-[var(--muted-foreground)]">(2 T1 + 6 T2)</span></div>
      </button>
      <button type="button" data-quick-filter="CORE" title="Causal human ALS genetics and/or human TDP-43 pathology + functional rescue" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Keep &middot; Core Leads</div>
        <div class="text-lg font-bold font-mono tabular-nums text-[var(--primary)] mt-0.5">4 <span class="text-xs font-normal text-[var(--muted-foreground)]">(1 Oral + 3 IT SSO)</span></div>
      </button>
      <button type="button" data-quick-filter="EXPL" title="Untested preclinical/biofluid triage queue (not therapeutic endorsement)" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Keep &middot; Exploratory</div>
        <div class="text-lg font-bold font-mono tabular-nums text-[var(--warning)] mt-0.5">26 <span class="text-xs font-normal text-[var(--muted-foreground)]">(Untested &ne; Falsified)</span></div>
      </button>
      <button type="button" data-switch-tab="intervals" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">GRCh38 Splice Windows</div>
        <div class="text-lg font-bold font-mono tabular-nums mt-0.5">28 <span class="text-xs font-normal text-[var(--success)]">(4 Clean, &ge;2 Mismatches)</span></div>
      </button>
      <button type="button" data-quick-filter="DROP" title="Deprioritized based on human RCT futility, CNS exposure/safety limits, or assay confounding" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Drop &middot; Falsified</div>
        <div class="text-lg font-bold font-mono tabular-nums text-[var(--error)] mt-0.5">16 <span class="text-xs font-normal text-[var(--muted-foreground)]">(9 Trial &middot; 7 PK/Tox &middot; 0 Confounded)</span></div>
      </button>
    </div>

    <div id="view-home" role="tabpanel" aria-labelledby="tab-btn-home" class="space-y-3">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 items-start">
        <div class="lg:col-span-5 space-y-2.5">
          <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2.5">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span class="px-2 py-0.5 rounded bg-[var(--background)] border border-[var(--primary)] text-[var(--primary)] font-mono font-semibold text-xs">START HERE &middot; OVERVIEW &amp; SCOPE</span>
              <span class="font-mono text-xs text-[var(--muted-foreground)]">Updated Nov 2026 (v1.4.0)</span>
            </div>
            <h2 class="text-sm font-semibold text-[var(--foreground)]">How 53 ALS Hypotheses Map Across Evidence, Validation Steps &amp; Trial Readouts</h2>
            <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">Synthesizes donor-level statistics (<span class="font-mono">8</span> participant-overlap and donor-accounting groups, <span class="font-mono">204</span> SHA-256-verified statistical records across <span class="font-mono">47</span> unique source files; zero new wet-lab data), unbound human brain PK, and GENCODE v46 off-target scans across four triage verdicts:</p>
            <div class="p-3 rounded bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--warning)] space-y-1.5">
              <div class="font-mono font-semibold text-xs text-[var(--foreground)]">Four Evidence &amp; Triage Verdicts (<span class="font-mono">Untested &ne; Falsified</span>)</div>
              <ul class="space-y-1.5 text-xs leading-relaxed">
                <li><span class="font-mono font-semibold text-[var(--success)]">Keep &middot; Core (4):</span> Supported by human ALS genetics and/or TDP-43 rescue with a CNS-viable modality.</li>
                <li><span class="font-mono font-semibold text-[var(--warning)]">Keep &middot; Exploratory (26):</span> Unresolved due to bulk-assay, dosing, or cohort blind spots, paired with 1 Go/No-Go test.</li>
                <li><span class="font-mono font-semibold text-[var(--primary)]">Benchmark / Biomarker (7):</span> Approved SOC comparator (2), clinical PD reference (1), CSF staging panel (1), or candidate CSF marker (3).</li>
                <li><span class="font-mono font-semibold text-[var(--error)]">Drop &middot; Falsified (16):</span> Deprioritized at the tested regimen/exposure based on human ALS RCT futility (<span class="font-mono">9</span>), unbound CNS exposure or safety limits (<span class="font-mono">7</span>), or assay confounding (<span class="font-mono">0</span>).</li>
              </ul>
            </div>
            <div class="p-2.5 rounded bg-[var(--background)] border border-[var(--card-border)] border-l-4 border-l-[var(--success)] space-y-1.5">
              <div class="font-mono font-semibold text-xs text-[var(--foreground)]">Flagship Tier 1 (2) + Tier 2 (6) Leads: Open Monograph</div>
              <div class="flex flex-wrap gap-1">
                <button type="button" data-open-dossier="EALS-030" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">#1 SARM1 &middot; EALS-030</button>
                <button type="button" data-open-dossier="EALS-031" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">#2 IL-2 &middot; EALS-031</button>
                <button type="button" data-open-dossier="EALS-001" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">#3 UNC13A &middot; EALS-001</button>
                <button type="button" data-open-dossier="EALS-006" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">#4 KCNQ2 &middot; EALS-006</button>
                <button type="button" data-open-dossier="EALS-002" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">#5 STMN2 &middot; EALS-002</button>
                <button type="button" data-open-dossier="EALS-007" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">#6 sST2 &middot; EALS-007</button>
                <button type="button" data-open-dossier="EALS-034" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">#7 ATG4B &middot; EALS-034</button>
                <button type="button" data-open-dossier="EALS-037" class="px-1.5 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">#8 CELF5 &middot; EALS-037</button>
              </div>
            </div>
            <div class="pt-1.5 border-t border-[var(--card-border)] space-y-1.5">
              <div class="font-mono font-semibold text-xs text-[var(--muted-foreground)]">WHERE TO GO NEXT</div>
              <button type="button" data-switch-tab="portfolio" class="w-full text-left px-2.5 py-2 rounded bg-[var(--background)] border border-[var(--border)] hover:border-[var(--primary)] flex items-center justify-between gap-2 cursor-pointer transition">
                <div><div class="font-mono font-semibold text-xs text-[var(--foreground)]">1. Compare All 53 Hypotheses (Triage Table)</div><div class="text-xs text-[var(--muted-foreground)] mt-0.5 leading-normal">Filter &amp; rank by verdict, subunit, pathway/mechanism, or biological evidence</div></div>
                <span class="font-mono text-[var(--link)] shrink-0">&rarr;</span>
              </button>
              <button type="button" data-switch-tab="dossiers" class="w-full text-left px-2.5 py-2 rounded bg-[var(--background)] border border-[var(--border)] hover:border-[var(--primary)] flex items-center justify-between gap-2 cursor-pointer transition">
                <div><div class="font-mono font-semibold text-xs text-[var(--foreground)]">2. Read the 53 Candidate Reports</div><div class="text-xs text-[var(--muted-foreground)] mt-0.5 leading-normal">8 full translational monographs + 45 structured triage dossiers</div></div>
                <span class="font-mono text-[var(--link)] shrink-0">&rarr;</span>
              </button>
              <button type="button" data-switch-tab="intervals" class="w-full text-left px-2.5 py-2 rounded bg-[var(--background)] border border-[var(--border)] hover:border-[var(--primary)] flex items-center justify-between gap-2 cursor-pointer transition">
                <div><div class="font-mono font-semibold text-xs text-[var(--foreground)]">3. Inspect the 28 GRCh38 Splice Windows</div><div class="text-xs text-[var(--muted-foreground)] mt-0.5 leading-normal">Target coordinates, SantaLucia Tm &amp; 254,070-transcript off-target scan</div></div>
                <span class="font-mono text-[var(--link)] shrink-0">&rarr;</span>
              </button>
              <button type="button" data-switch-tab="replication" class="w-full text-left px-2.5 py-2 rounded bg-[var(--background)] border border-[var(--border)] hover:border-[var(--primary)] flex items-center justify-between gap-2 cursor-pointer transition">
                <div><div class="font-mono font-semibold text-xs text-[var(--foreground)]">4. Reproduce Any Analysis &amp; Explore PK-PD Models</div><div class="text-xs text-[var(--muted-foreground)] mt-0.5 leading-normal">43 open datasets, 59 Python pipelines &amp; 3 biophysical/trial-power models</div></div>
                <span class="font-mono text-[var(--link)] shrink-0">&rarr;</span>
              </button>
              <button type="button" data-home-contrasts="1" class="w-full text-left px-2.5 py-2 rounded border border-dashed border-[var(--border)] hover:border-[var(--primary)] flex items-center justify-between gap-2 text-xs cursor-pointer transition">
                <span class="text-[var(--muted-foreground)] leading-normal"><strong class="font-mono text-[var(--foreground)]">Field Contrasts:</strong> Nine standard assumptions vs. re-analyzed data</span>
                <span class="font-mono text-[var(--link)] shrink-0">&rarr;</span>
              </button>
            </div>
          </div>
        </div>

        <div id="upd-card" class="lg:col-span-7 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
          <div class="flex flex-wrap items-start justify-between gap-2 border-b border-[var(--card-border)] pb-2.5">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h2 class="text-sm font-semibold text-[var(--foreground)]">Living Research Log &middot; Trial &amp; Literature Updates</h2>
                <span id="upd-count" class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono tabular-nums text-xs text-[var(--muted-foreground)]">10 / 10</span>
              </div>
              <p class="text-xs text-[var(--muted-foreground)] mt-0.5 leading-relaxed">Chronological record of post-release clinical trial readouts, newly published studies, and quantitative PK-PD/survival model revisions.</p>
            </div>
            <button type="button" data-dl-reg="updates" class="px-2.5 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] shrink-0 cursor-pointer">&darr; Updates (CSV)</button>
          </div>
          <div class="flex flex-wrap items-center gap-1.5">
            <button type="button" data-upd-cat="ALL" class="px-2 py-1 rounded border font-mono text-xs cursor-pointer">All</button>
            <button type="button" data-upd-cat="CLINICAL_TRIAL" class="px-2 py-1 rounded border font-mono text-xs cursor-pointer">&bull; Clinical / Trial</button>
            <button type="button" data-upd-cat="LITERATURE_INGESTION" class="px-2 py-1 rounded border font-mono text-xs cursor-pointer">&#9670; New Literature</button>
            <button type="button" data-upd-cat="MODEL_REVISION" class="px-2 py-1 rounded border font-mono text-xs cursor-pointer">&#9671; Model / Re-Analysis</button>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <input id="upd-search" aria-label="Search living research updates" type="text" placeholder="Filter by ID (e.g. EALS-030, EALS-001), gene, trial NCT, PMID..." class="bg-[var(--background)] border border-[var(--border)] rounded px-2.5 py-1.5 text-xs flex-1 min-w-[180px] text-[var(--foreground)]" />
            <button type="button" data-reset-updates="1" class="px-2.5 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xs cursor-pointer">Reset</button>
          </div>
          <div id="upd-feed" class="space-y-2.5 max-h-[74vh] overflow-y-auto pr-1"></div>
        </div>
      </div>
    </div>

    <div id="view-portfolio" role="tabpanel" aria-labelledby="tab-btn-portfolio" class="hidden space-y-3">
      <details id="methodology-drawer" class="bg-[var(--card)] border border-[var(--border)] rounded-lg px-4 py-2.5 text-xs">
        <summary class="cursor-pointer font-semibold text-[var(--foreground)] select-none">Methodology &amp; Decision Guide: Clinical Regimens, Molecular Targets &amp; Evidence Triage</summary>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2.5 mt-2 border-t border-[var(--card-border)] text-[var(--muted-foreground)] leading-relaxed">
          <div><strong class="text-[var(--foreground)]">1. Clinical Regimens &amp; Molecular Targets:</strong> Evaluates 53 ALS therapeutic &amp; biomarker hypotheses across 6 biological evidence sources (including 18 complex/panel subunits and selectivity comparators) using donor-level statistics (Trautwig Emory TMT n=51 is a nested subset of n=77 DIA; multi-region NYGC/Pineda donors analyzed per-region without pooling) and unbound human CNS PK (Cu,brain / Kp,uu).</div>
          <div><strong class="text-[var(--foreground)]">2. Untested &ne; Falsified Triage Rule:</strong> Never discards an untested hypothesis due to bulk-assay, fixed-library-concentration, or unstratified-cohort blind spots. <span class="font-mono text-[var(--warning)]" title="Untested preclinical or biofluid triage queue; prospective Go/No-Go test required">Keep &middot; Exploratory (26)</span> denotes an untested preclinical/biofluid triage queue (not therapeutic endorsement) paired with prospective Go/No-Go criteria; <span class="font-mono text-[var(--error)]" title="Deprioritized based on human RCT futility, CNS exposure/safety limits, or assay confounding">Drop &middot; Falsified (16)</span> evaluates specific clinical drug regimens/exposures separately from molecular target pathways and requires positive human RCT futility, insurmountable CNS exposure/safety limits, or confounding collapse.</div>
          <div><strong class="text-[var(--foreground)]">3. Combinatorial Portfolio Thesis:</strong> Pairs single-agent-qualified genotype-stratified intrathecal splice rescue (evaluating 2-plex KCNQ2 EALS-006 + STMN2 EALS-002 vs. 3-plex + UNC13A EALS-001 across rs12973192/rs12608932 genotypes at a 6&ndash;9 mg [&le;3 mg/strand] total intrathecal ASO dose target vs. 12&ndash;50 mg nusinersen &amp; 100 mg tofersen; &ge;24&ndash;48 mg flagged as DRG/radiculotoxicity hazard) with oral non-covalent SARM1 ARM&ndash;TIR octamer stabilization (EALS-030, 1.0x parallel Bliss floor to ~2&ndash;7x modeled NMNAT2-coupled MWC bounds) and biomarker-gated neuroimmune modulation (EALS-031 BioVendor-bridged pNfH &le;3,700, oximetry-verified EALS-007 sST2, Tier 3 EALS-019 high-chitinase CSF glial stratum).</div>
        </div>
        <div class="pt-2 mt-2 border-t border-[var(--card-border)] text-[var(--muted-foreground)] font-mono text-xs leading-relaxed space-y-1">
          <div><strong class="text-[var(--foreground)]">Rank &amp; Triage Key:</strong> Priority #Rk = translational priority (tier &middot; trial landscape &middot; validation steps &middot; stage) &middot; <span class="text-[var(--primary)]">Evidence #Rk</span> = curated human genetic &amp; CNS pathology ordering (37 prioritized programs; editorial order, not win probability) &middot; <span class="text-[var(--warning)]">Keep&middot;Exploratory (26)</span> = untested triage queue (not endorsement) &middot; Modeled estimates never rank candidates.</div>
          <div>Data &amp; Provenance Standards: Open Targets / NIH IDG TDL &amp; TSA &middot; GENCODE v46 Off-Target Alignment Screen &middot; Linked Scripts, SHA-256 Checksums &amp; Study-Type Evidence Categories &middot; 100% open-access published tables/counts (1-based GRCh38 target windows; SantaLucia Tm/&Delta;G37 &amp; AlphaGenome AVI never rank candidates).</div>
        </div>
      </details>
      <details id="contrasts-drawer" class="bg-[var(--card)] border border-[var(--border)] border-l-4 border-l-[var(--primary)] rounded-lg px-4 py-2.5 text-xs">
        <summary class="cursor-pointer font-semibold text-[var(--foreground)] flex flex-wrap items-center justify-between gap-2 select-none">
          <span>Nine Key Mechanistic Contrasts &amp; Translational Lessons: Field Assumptions vs. Re-Analyzed Primary Evidence</span>
          <span class="font-mono font-normal text-[var(--muted-foreground)]">9 Cross-Portfolio Insights &middot; Click ID for Dossier</span>
        </summary>
        <div class="mt-2 pt-2 border-t border-[var(--card-border)] max-h-[290px] overflow-y-auto overflow-x-auto">
          <table class="w-full text-left border-collapse text-xs">
            <thead class="sticky top-0 z-10 bg-[var(--card)]">
              <tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                <th class="py-1.5 px-2 font-medium">Dossier(s)</th>
                <th class="py-1.5 px-2 font-medium">Domain</th>
                <th class="py-1.5 px-2 font-medium">Standard Field Assumption</th>
                <th class="py-1.5 px-2 font-medium">Verified Re-Analysis Finding</th>
                <th class="py-1.5 px-2 font-medium">Prospective Validation Rule</th>
              </tr>
            </thead>
            <tbody id="contrasts-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
          </table>
        </div>
      </details>
      <div id="p-filter-bar" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 flex flex-wrap items-center gap-2">
        <input id="p-search" aria-label="Search candidates" type="text" placeholder="Search ID (e.g. EALS-006, #4), gene/drug, subunit (G2E3, C1QA)..." class="bg-[var(--background)] border border-[var(--border)] rounded px-2.5 py-1.5 text-xs flex-1 min-w-[200px] text-[var(--foreground)]" />
        <select id="p-origin" aria-label="Filter by biological evidence source" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
          <option value="ALL">Evidence Source: All (53)</option>
          <option value="GENETICS_MENDELIAN_GWAS">Human ALS Genetics: Mendelian &amp; GWAS (5)</option>
          <option value="TDP43_SPLICING_APA">TDP-43 Cryptic Splicing &amp; Polyadenylation (12)</option>
          <option value="CNS_TISSUE_OMICS">Human CNS Spatial, snRNA &amp; Subcellular Omics (6)</option>
          <option value="CSF_AND_PHYSIOLOGY">Antemortem CSF Proteomics &amp; Physiology (6)</option>
          <option value="CLINICAL_TRIALS_SUBGROUPS">Human ALS Clinical Trials &amp; Subgroups (13)</option>
          <option value="IPSC_PHENOTYPIC_SCREEN">Patient iPSC-MN Phenotypic Screen (11)</option>
        </select>
        <select id="p-dec" aria-label="Filter by triage verdict" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
          <option value="ALL">Triage Verdict: All (53)</option>
          <option value="KEEP_CORE">Keep &middot; Core (4)</option>
          <option value="KEEP_EXPLORATORY_UNPROVEN">Keep &middot; Exploratory (26)</option>
          <option value="RECLASSIFY_BENCHMARK_OR_BIOMARKER">Benchmark / Biomarker (7)</option>
          <option value="DROP">Drop &middot; All Excluded (16)</option>
          <option value="DROP_CLIN">&nbsp;&nbsp;&larrhk; Drop: Human RCT Futility (9)</option>
          <option value="DROP_PK">&nbsp;&nbsp;&larrhk; Drop: CNS Exposure / Safety Limit (7)</option>
          <option value="DROP_ART">&nbsp;&nbsp;&larrhk; Drop: Assay Confounding (0)</option>
        </select>
        <select id="p-tier" aria-label="Filter by translational priority tier" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
          <option value="ALL">Priority Tier: All (53)</option>
          <option value="TIER_12">Tier 1 + Tier 2 Leads (8)</option>
          <option value="TIER_1_ACTIONABLE_NOW">Tier 1 &middot; Translational Lead (2)</option>
          <option value="TIER_2_FOCUSED_GATE_FIRST">Tier 2 &middot; Validation Gate (6)</option>
          <option value="TIER_3_EXPLORATORY_DISCOVERY">Tier 3 &middot; Exploratory Discovery (21)</option>
          <option value="BIO_AND_CAL">Biomarkers &amp; Benchmarks (8)</option>
          <option value="DROPPED_FALSIFIED_EXCLUDED">Drop &middot; Excluded Regimens (16)</option>
        </select>
        <select id="p-sort" aria-label="Sort portfolio candidates" title="Lexicographic Translational Priority tuple: (1) Priority Tier, (2) Keep·Core before Exploratory, (3) Within-tier sub-rules (Tier 3 genetic/spatial programs ahead of screen-only candidates; benchmark sub-roles; human RCT futility ahead of PK/safety exclusions), (4) Active ALS Trial Landscape &amp; Open Validation Steps, (5) Clinical Development Stage. Genetic &amp; Pathology Evidence uses a 37-program curated biological evidence ordering. SantaLucia Tm/ΔG37 and AlphaGenome AVI never rank candidates." class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
          <option value="rank">Sort: Translational Priority Rank</option>
          <option value="bio">Sort: Genetic &amp; Pathology Evidence</option>
          <option value="trl">Sort: Development Stage</option>
          <option value="hurdles">Sort: Fewest Validation Steps</option>
        </select>
        <button type="button" data-reset-filters="1" class="px-2.5 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xs cursor-pointer">Reset</button>
        <button type="button" data-open-method="1" class="px-2 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] font-mono text-xs cursor-pointer" title="Open Methodology &amp; Rank Key">Rank Key</button>
        <span id="p-count" class="font-mono tabular-nums text-[var(--muted-foreground)] text-xs ml-auto">53 / 53</span>
        <div class="w-full pt-2 mt-0.5 border-t border-[var(--card-border)] flex flex-wrap items-center gap-1.5">
          <span class="font-mono text-xs text-[var(--muted-foreground)] mr-0.5">Pathway / Mechanism:</span>
          <div id="p-lens-bar" class="flex flex-wrap gap-1.5"></div>
        </div>
      </div>
      <div id="p-split-pane" class="p-workbench grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div class="lg:col-span-8 bg-[var(--card)] border border-[var(--border)] rounded-lg lg:flex lg:flex-col lg:min-h-0 overflow-hidden">
          <div class="max-h-[420px] lg:max-h-none lg:flex-1 lg:min-h-0 overflow-y-auto overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead class="sticky top-0 z-10 bg-[var(--card)] shadow-sm">
                <tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th class="py-2 px-2 font-medium">Rk</th>
                  <th class="py-2 px-1.5 font-medium">ID</th>
                  <th class="py-2 px-2 font-medium">Program / Gene / Drug</th>
                  <th class="hidden xl:table-cell py-2 px-2 font-medium">Therapeutic Modality</th>
                  <th class="py-2 px-1.5 font-medium">Verdict</th>
                  <th class="hidden lg:table-cell py-2 px-1.5 font-medium">Tier</th>
                  <th class="hidden sm:table-cell py-2 px-1.5 font-medium">Stage</th>
                  <th class="hidden sm:table-cell py-2 px-1.5 font-medium text-right" title="Open Validation Steps">Steps</th>
                  <th class="py-2 px-2 font-medium text-right">Report</th>
                </tr>
              </thead>
              <tbody id="p-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
            </table>
          </div>
        </div>
        <div id="p-detail" class="lg:col-span-4 bg-[var(--card)] border border-[var(--border)] rounded-lg lg:flex lg:flex-col lg:min-h-0 lg:overflow-hidden"></div>
      </div>
    </div>
"""

HTML_TABS_AND_SCRIPT = """    <div id="view-intervals" role="tabpanel" aria-labelledby="tab-btn-intervals" class="hidden space-y-3">
      <details id="iv-method-drawer" class="bg-[var(--card)] border border-[var(--border)] rounded-lg px-4 py-2.5 text-xs">
        <summary class="cursor-pointer font-semibold text-[var(--foreground)] select-none">GENCODE v46 Off-Target Alignment Screen: 1-Based Closed GRCh38 Target Windows, Safety Rules &amp; Biophysical Notes</summary>
        <div class="text-xs text-[var(--muted-foreground)] border-t border-[var(--card-border)] pt-2.5 mt-2 space-y-1.5 leading-relaxed">
          <div><strong class="font-mono text-[var(--foreground)]">GENCODE v46 Off-Target Alignment Screen (1-Based Closed GRCh38 Target Windows):</strong> Candidate target windows for empirical 1-nt microwalks plus human neuron <span class="font-mono">Ca2+</span>-oscillation, <span class="font-mono">TLR9</span> &amp; primary <span class="font-mono">DRG</span> safety screens (reference transcriptome alignment does not exclude phosphorothioate protein-binding toxicity) &middot; modeled SantaLucia <span class="font-mono">2'-O-MOE PO/PS Tm / &Delta;G37</span> + <span class="font-mono">AlphaGenome AVI Phred</span> (DNA-variant conservation/splicing score, not steric ASO potency).</div>
          <div>Select any window below to inspect its labeled <span class="font-mono text-[var(--foreground)]">Spliced mRNA (&le;200bp of splice junction)</span> and <span class="font-mono text-[var(--foreground)]">Nascent Pre-mRNA (sense strand)</span> hybridization counts across <span class="font-mono">254,070</span> GENCODE v46 transcripts, <span class="font-mono">gnomAD v4</span> constrained CNS gene flags, sibling windows on the same locus, and genome browser tracks (<span class="font-mono text-[var(--success)]">Pass &middot; Clean</span> requires zero hits across all spliced mRNA, &le;50bp-SS, &le;25bp 2-mm, 1-nt bulge &amp; 18-nt sub-core filters).</div>
        </div>
      </details>
      <div id="iv-filter-bar" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3">
        <div class="flex flex-wrap items-center gap-2">
          <input id="iv-search" aria-label="Search GRCh38 intervals" type="text" placeholder="Filter gene, ID, coordinate..." class="bg-[var(--background)] border border-[var(--border)] rounded px-2.5 py-1.5 text-xs min-w-[180px] text-[var(--foreground)]" />
          <select id="iv-status" aria-label="Filter by off-target safety status" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
            <option value="ALL">Off-Target Verdict: All (28)</option>
            <option value="PASS_CLEAN_GE2MM">Pass &middot; Clean (&ge;2 Mismatches) (4)</option>
            <option value="CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED">Caution &middot; Non-Constrained 1-mm / Wobble / 2-mm (17)</option>
            <option value="WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL">Warn &middot; Constrained CNS 1-mm / Bulge (5)</option>
            <option value="FAIL_EXACT_0MM_OFFTARGET">Fail &middot; Exact 0-mm Off-Target (2)</option>
          </select>
          <select id="iv-origin" aria-label="Filter by cis-regulatory mechanism" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
            <option value="ALL">Cis-Mechanism: All (28)</option>
            <option value="CRYPTIC_EXON_SKIP">Cryptic Cassette Exon Skipping (14)</option>
            <option value="CRYPTIC_ALE_PAS_BLOCK">Cryptic 3&apos;SS / Premature PolyA Blockade (9)</option>
            <option value="CONSTITUTIVE_EXON_INCLUSION">Constitutive Exon Inclusion Rescue (3)</option>
            <option value="DISTAL_3UTR_EXTENSION">Distal 3&apos;-UTR Extension Suppression (2)</option>
          </select>
          <label class="flex items-center gap-1.5 text-xs text-[var(--foreground)] cursor-pointer">
            <input id="iv-leads" type="checkbox" class="accent-[var(--primary)]" /> Promoted Leads Only (11)
          </label>
          <button type="button" data-reset-intervals="1" class="px-2.5 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xs cursor-pointer">Reset</button>
          <button type="button" data-open-iv-method="1" class="px-2 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] font-mono text-xs cursor-pointer" title="Open Off-Target Screen Methodology &amp; Safety Rules">Screen Guide</button>
          <span id="iv-count" class="font-mono tabular-nums text-[var(--muted-foreground)] text-xs ml-auto">28 / 28</span>
        </div>
      </div>
      <div id="iv-split-pane" class="grid grid-cols-1 lg:grid-cols-12 gap-3 lg:items-start">
        <div class="iv-table-cap lg:col-span-7 bg-[var(--card)] border border-[var(--border)] rounded-lg flex flex-col overflow-hidden">
          <div class="min-h-0 overflow-y-auto overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead class="sticky top-0 z-10 bg-[var(--card)] shadow-sm">
                <tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th class="py-2 px-1.5 font-medium">#</th>
                  <th class="py-2 px-2 font-medium">Gene &amp; Window</th>
                  <th class="py-2 px-2 font-medium" title="1-based closed GRCh38 span · length · modeled Tm · max AlphaGenome AVI Phred">GRCh38 Coordinate</th>
                  <th class="hidden xl:table-cell py-2 px-2 font-medium">Cis-Mechanism</th>
                  <th class="py-2 px-2 font-medium text-right">Off-Target Verdict</th>
                </tr>
              </thead>
              <tbody id="iv-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
            </table>
          </div>
        </div>
        <div id="iv-detail" class="iv-detail-cap lg:col-span-5 bg-[var(--card)] border border-[var(--border)] rounded-lg lg:flex lg:flex-col lg:overflow-hidden"></div>
      </div>
    </div>

    <div id="view-dossiers" role="tabpanel" aria-labelledby="tab-btn-dossiers" class="hidden">
      <div class="md:hidden mb-3 sticky top-2 z-20 bg-[var(--card)] border border-[var(--border)] rounded-lg p-2 flex items-center gap-1.5 shadow-sm">
        <button id="d-mobile-prev" type="button" data-open-dossier="EALS-052" class="px-2 py-1 rounded border border-[var(--border)] font-mono text-xs shrink-0 cursor-pointer">&larr;</button>
        <select id="d-mobile-select" aria-label="Select Candidate Dossier" class="flex-1 min-w-0 truncate bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs font-medium text-[var(--foreground)]"></select>
        <button id="d-mobile-next" type="button" data-open-dossier="EALS-031" class="px-2 py-1 rounded border border-[var(--border)] font-mono text-xs shrink-0 cursor-pointer">&rarr;</button>
        <button type="button" data-toggle-d-rail="1" aria-expanded="false" aria-controls="d-aside" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs shrink-0 cursor-pointer">List</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-[268px_minmax(0,1fr)] gap-3 items-start">
        <aside id="d-aside" aria-label="Candidate Directory" class="hidden md:flex md:flex-col bg-[var(--card)] border border-[var(--border)] rounded-lg p-2.5 gap-2 md:sticky md:top-3 max-h-[calc(100vh-1.5rem)]">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-xs">Candidate Directory</span>
            <span id="d-nav-count" class="font-mono tabular-nums text-xs text-[var(--muted-foreground)]">53 / 53</span>
          </div>
          <div class="text-xs text-[var(--muted-foreground)] leading-normal"><span class="font-mono font-semibold text-[var(--primary)]">M</span> Full Monograph (8) &middot; Triage Dossier (45)</div>
          <input id="d-search" aria-label="Search candidate directory" type="text" placeholder="Jump: EALS-006, KCNQ2, #4..." class="w-full bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs text-[var(--foreground)]" />
          <div id="d-slice-bar" class="flex flex-wrap gap-1"></div>
          <select id="d-lens" aria-label="Filter by biological pathway or mechanism" class="w-full bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs text-[var(--foreground)]"></select>
          <div id="d-nav" class="space-y-0.5 flex-1 min-h-0 max-h-[68vh] overflow-y-auto pr-0.5"></div>
        </aside>
        <div id="d-content" class="min-w-0 space-y-3"></div>
      </div>
    </div>

    <div id="view-replication" role="tabpanel" aria-labelledby="tab-btn-replication" class="hidden space-y-3">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-mono font-semibold text-xs text-[var(--success)]">LEVEL 1 &middot; SCHEMA &amp; CHECKSUM CHECKS (&lt;10s &middot; 0 MB)</span>
            <span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">Offline Ready</span>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-relaxed">Clones the &lt;18 MB repository, installs pinned Python 3.12 dependencies (<span class="font-mono">uv.lock</span>), and verifies all 20 CSV schemas, foreign keys, primary citations, decision rules, and 204 recorded 64-char SHA-256 digests (<span class="font-mono">47</span> unique source files; <span class="font-mono">66/204</span> bundled in clean checkout, <span class="font-mono">204/204</span> with staged data).</p>
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] flex items-center justify-between gap-2 font-mono text-xs">
            <span class="truncate">uv sync --frozen &amp;&amp; uv run python scripts/verify_explore_als.py --mode cached</span>
            <button type="button" data-copy-cmd="git clone https://github.com/helloimra/ExploreALS.git &amp;&amp; cd ExploreALS &amp;&amp; uv sync --frozen &amp;&amp; uv run python scripts/verify_explore_als.py --mode cached" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] shrink-0 cursor-pointer">Copy</button>
          </div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-mono font-semibold text-xs text-[var(--primary)]">LEVEL 2 &middot; 8 FLAGSHIP &amp; RAW COHORTS</span>
            <span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">rtol = 1e-4</span>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-relaxed">Runs the 8 single-command Tier 1+2 monograph reproducers immediately, or fetches the 41 external open datasets (<span class="font-mono">677.0 MB</span> across 43 SHA-256-locked resources) to rerun donor-level OLS and 254,070-tx scans.</p>
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] flex items-center justify-between gap-2 font-mono text-xs">
            <span class="truncate">uv run python scripts/reproduce_all.py --flagship-only</span>
            <button type="button" data-copy-cmd="uv run python scripts/reproduce_all.py --flagship-only" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] shrink-0 cursor-pointer">Copy</button>
          </div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-mono font-semibold text-xs text-[var(--warning)]">LEVEL 3 &middot; REBUILD EXPLORER &amp; MONOGRAPHS</span>
            <span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">Zero-CDN</span>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-relaxed">Re-compiles this 5-view Explorer and all 8 standalone monographs directly from the CSV registries into self-contained HTML (<span class="font-mono">0</span> external CDN requests).</p>
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] flex items-center justify-between gap-2 font-mono text-xs">
            <span class="truncate">uv run python scripts/build_explorer.py --public-docs-only</span>
            <button type="button" data-copy-cmd="uv run python scripts/build_explorer.py --public-docs-only" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] shrink-0 cursor-pointer">Copy</button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div class="lg:col-span-5 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h2 class="text-sm font-semibold">Computational Provenance Workflow</h2>
            <span class="font-mono text-xs text-[var(--muted-foreground)]">Click Step to Filter Workbench</span>
          </div>
          <div id="rep-dag-box" class="w-full"></div>
          <p class="text-[var(--muted-foreground)] text-xs leading-relaxed font-mono">Environment: Python &ge;3.12 &middot; pinned <span class="text-[var(--foreground)]">uv.lock</span> &middot; MIT (code) + CC BY 4.0 (registries/prose) &middot; GitHub Codespaces ready.</p>
        </div>
        <div class="lg:col-span-7 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h2 class="text-sm font-semibold">Cohort Participant Overlap &amp; Donor-Accounting Rules (8 Groups)</h2>
            <span class="font-mono text-xs text-[var(--muted-foreground)]">Donor-Level Independence Rules</span>
          </div>
          <div class="max-h-[290px] overflow-y-auto overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead class="sticky top-0 z-10 bg-[var(--card)]">
                <tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th class="py-1.5 px-2 font-medium">Cluster &amp; Datasets</th>
                  <th class="py-1.5 px-2 font-medium">Participant Overlap &amp; Unit Rule</th>
                  <th class="py-1.5 px-2 font-medium">Canonical Statistical Model</th>
                </tr>
              </thead>
              <tbody id="rep-overlap-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
            </table>
          </div>
        </div>
      </div>

      <div id="rep-workbench-bar" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 flex flex-wrap items-center gap-2">
        <div class="flex flex-wrap items-center gap-1.5" role="group" aria-label="Replication Workbench Registry">
          <span class="font-mono text-xs text-[var(--muted-foreground)] mr-0.5">Registry:</span>
          <button type="button" data-rep-mode="runs" class="rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer">8 Flagship + 51 Runs (59)</button>
          <button type="button" data-rep-mode="datasets" class="rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer">Open Datasets (43)</button>
          <button type="button" data-rep-mode="evidence" class="rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer">204 Evidence SHA-256 &amp; Formulas</button>
        </div>
        <input id="rep-search" aria-label="Search replication workbench" type="text" placeholder="Search Run ID, DS ID, candidate, formula, SHA-256, script..." class="bg-[var(--background)] border border-[var(--border)] rounded px-2.5 py-1.5 text-xs flex-1 min-w-[200px] text-[var(--foreground)]" />
        <select id="rep-filter" aria-label="Filter replication workbench" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]"></select>
        <button type="button" data-reset-rep="1" class="px-2.5 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xs cursor-pointer">Reset</button>
        <span id="rep-count" class="font-mono tabular-nums text-[var(--muted-foreground)] text-xs ml-auto">59 / 59</span>
        <div class="w-full pt-2 mt-0.5 border-t border-[var(--card-border)] flex flex-wrap items-center gap-1.5">
          <span id="rep-subfilter-lbl" class="font-mono text-xs text-[var(--muted-foreground)] mr-0.5">Workflow:</span>
          <div id="rep-subfilter-bar" class="flex flex-wrap gap-1.5"></div>
        </div>
      </div>

      <div id="rep-split-pane" class="grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div class="lg:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg overflow-hidden lg:relative lg:min-h-[520px]">
          <div class="max-h-[420px] lg:max-h-none lg:absolute lg:inset-0 overflow-y-auto overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead id="rep-thead" class="sticky top-0 z-10 bg-[var(--card)] shadow-sm"></thead>
              <tbody id="rep-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
            </table>
          </div>
        </div>
        <div id="rep-detail" class="lg:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-3 lg:min-h-[520px]"></div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h3 class="text-sm font-semibold">Machine-Readable Registry &amp; Schema Exports (Offline-Safe)</h3>
            <span class="font-mono text-xs text-[var(--muted-foreground)]">Client-Side CSV / JSON</span>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-relaxed">Generate byte-clean CSV or JSON exports directly from the verified embedded payload (works offline on <span class="font-mono">file://</span> and matches curated tables in GitHub):</p>
          <div class="flex flex-wrap gap-1.5">
            <button type="button" data-dl-reg="portfolio" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; Portfolio (53 CSV)</button>
            <button type="button" data-dl-reg="intervals" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; Splice Windows (28 CSV)</button>
            <button type="button" data-dl-reg="subnodes" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; Subunit Cards (18 CSV)</button>
            <button type="button" data-dl-reg="formulas" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; 204 Evidence &amp; Formulas (CSV)</button>
            <button type="button" data-dl-reg="datasets" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; 43 Datasets SHA-256 (CSV)</button>
            <button type="button" data-dl-reg="runs" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; 51 Runs + 8 Flagship (CSV)</button>
            <button type="button" data-dl-reg="overlap" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; 8 Cohort Overlaps (CSV)</button>
            <button type="button" data-dl-reg="updates" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; Updates (CSV)</button>
            <button type="button" data-dl-reg="json_all" class="px-2.5 py-1.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-semibold text-xs cursor-pointer">&darr; Full Provenance Bundle (JSON)</button>
          </div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h3 class="text-sm font-semibold">Cryptographic Hash Coverage &amp; Open-Access Redistribution</h3>
            <span class="font-mono text-xs text-[var(--success)]">204 / 204 (100%) 64-char SHA-256</span>
          </div>
          <div class="grid grid-cols-3 gap-2 font-mono text-xs">
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)]">Dataset Anchors</div><div class="font-bold text-sm text-[var(--foreground)] mt-0.5">138 <span class="text-xs font-normal text-[var(--muted-foreground)]">(43 DS)</span></div></div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)]">API Snapshots</div><div class="font-bold text-sm text-[var(--foreground)] mt-0.5">57 <span class="text-xs font-normal text-[var(--muted-foreground)]">(JSON)</span></div></div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)]">Model Outputs</div><div class="font-bold text-sm text-[var(--foreground)] mt-0.5">9 <span class="text-xs font-normal text-[var(--muted-foreground)]">(ODE/MWC)</span></div></div>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-relaxed">All <span class="font-mono">204</span> records carry 64-char SHA-256 digests across <span class="font-mono">47</span> unique source files (<span class="font-mono">66/204</span> bundled in clean git checkout; <span class="font-mono">204/204</span> locally matched when all <span class="font-mono">43</span> resources are staged across <span class="font-mono">676.99 MB</span> / <span class="font-mono">645.63 MiB</span>):</p>
          <ul class="space-y-1 text-[var(--muted-foreground)] text-xs leading-relaxed">
            <li><strong class="text-[var(--foreground)]">Tier A:</strong> <span class="font-mono">CC0/CC-BY</span> open release + repo-bundled reference maps.</li>
            <li><strong class="text-[var(--foreground)]">Tier B:</strong> Direct publisher/EuropePMC HTTPS fetch (zero re-hosting of <span class="font-mono">CC BY-NC-ND</span> supplements).</li>
            <li><strong class="text-[var(--foreground)]">Tier C:</strong> <span class="font-mono">SYNAPSE_AUTH_TOKEN</span> registered consortium access (cis-regulatory windows report 1-based GRCh38 coordinates only).</li>
          </ul>
        </div>
      </div>

      <details id="sandbox-drawer" class="bg-[var(--card)] border border-[var(--border)] border-l-4 border-l-[var(--warning)] rounded-lg px-4 py-3 text-xs">
        <summary class="cursor-pointer font-semibold text-[var(--foreground)] flex flex-wrap items-center justify-between gap-2 select-none">
          <span>Interactive Biophysical &amp; Trial-Power Models: Explore Channel Stoichiometry, Allostery &amp; Survival Power</span>
          <span class="px-2 py-0.5 rounded border border-[var(--warning)] text-[var(--warning)] font-mono text-xs">&#9671; Modeled Sensitivity Check &middot; Zero-Install</span>
        </summary>
        <div id="sandbox-body" class="pt-3 mt-2.5 border-t border-[var(--card-border)] grid grid-cols-1 md:grid-cols-3 gap-3"></div>
      </details>
    </div>

    <section aria-label="Attribution, AI Methodology and Research Disclaimer" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 text-xs text-[var(--muted-foreground)] leading-relaxed">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="space-y-1">
          <div class="font-mono font-semibold text-[var(--foreground)]">Author, Correspondence &amp; Open-Science Attribution</div>
          <p>Curated by <strong class="text-[var(--foreground)]">Ricardo Agoga</strong> &middot; Correspondence, inquiries &amp; error reporting: <a href="mailto:helloimra@proton.me" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">helloimra@proton.me</a> &middot; Repository: <a href="https://github.com/helloimra/ExploreALS" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">github.com/helloimra/ExploreALS &nearr;</a>.</p>
          <p>Primary data &amp; tool attributions: Google DeepMind AlphaGenome (v1 API &amp; Atlas AVI; non-commercial research use only), NIH GTEx (v8 / v10), Open Targets (v4), gnomAD (v4.1 / v4.1.1), Ensembl/GENCODE (v46), ChEMBL (v34), UniProt, RCSB PDB, and ClinicalTrials.gov.</p>
        </div>
        <div class="space-y-1">
          <div class="font-mono font-semibold text-[var(--warning)]">Preclinical Research Notice &amp; AI-Assisted Workflow Disclosure</div>
          <p><strong class="text-[var(--foreground)]">Not Medical Advice:</strong> ExploreALS v1.4 is an independent preclinical and translational research resource intended solely for scientific hypothesis generation. Nothing herein constitutes medical advice, clinical trial recruitment, or a treatment recommendation; individuals with ALS and caregivers should always consult their neurologist or ALS care team before starting, stopping, or modifying any therapy.</p>
          <p><strong class="text-[var(--foreground)]">AI-Assisted Methodology:</strong> Curated via human-directed AI synthesis workflows paired with deterministic Python statistical pipelines across 43 open-access human ALS and preclinical resources (published tables, raw counts, and structures; zero new wet-lab data) and primary-source verification (PubMed, Europe PMC, ClinicalTrials.gov). Quantitative contrasts and accessions are programmatically verified and separated from modeled biophysical and PK-PD estimates, though synthesis prose may contain residual errors; always verify against linked primary sources before experimental use.</p>
        </div>
      </div>
    </section>
  </div>
  <button id="back-to-top-btn" type="button" data-back-to-top="1" aria-label="Back to top of page" title="Scroll back to top of page" class="hidden fixed bottom-4 right-4 z-20 px-3 py-1.5 rounded-full bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-semibold text-xs shadow-md cursor-pointer">&uarr; Top</button>
"""
