"""Self-contained Generative UI HTML template (Tailwind + semantic CSS vars, >=12px text, side-pane optimized)."""
from __future__ import annotations

HTML_HEAD_AND_BODY = """<!DOCTYPE html>
<!-- __SHA12_STAMP__ -->
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>ExploreALS v1.2 — Unified Portfolio, Cis-Regulatory, Dossier &amp; Replication Explorer</title>
  <style>:where(.hidden){display:none}table{border-collapse:collapse;width:100%}th,td{padding:6px 8px;vertical-align:top}</style>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-4 m-0 text-xs">
  <div class="max-w-[1440px] mx-auto space-y-3.5">
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
      <div class="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="px-2 py-0.5 rounded font-mono font-semibold bg-[var(--primary)] text-[var(--primary-foreground)] text-xs">ExploreALS v1.2</span>
            <h1 class="text-base font-semibold text-[var(--foreground)]">Unified 59-Candidate Portfolio, 19-Subnode, 26-Interval &amp; Replication Explorer</h1>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs mt-1">Unified synthesis across 59 ALS drug &amp; genetic candidates &middot; 19 single-gene sub-nodes &middot; 26 Coordinate-Only Cis-Regulatory Search Windows (0 chemically modified synthesis-ready ASO sequences)</p>
          <p class="text-[var(--muted-foreground)] text-xs mt-1">Curated by <strong class="text-[var(--foreground)]">Ricardo Agoga</strong> (Independent Researcher) &middot; <a href="mailto:helloimra@proton.me" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">helloimra@proton.me</a> &middot; <a href="https://github.com/helloimra/ExploreALS" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">github.com/helloimra/ExploreALS &nearr;</a> &middot; <span class="font-mono text-[var(--warning)]">Preclinical Research Only (Not Medical Advice)</span></p>
        </div>
        <div class="flex items-center gap-2 shrink-0"><!-- THEME_TOGGLE_SLOT --></div>
      </div>
      <div class="pt-2.5 border-t border-[var(--card-border)] flex flex-wrap items-center justify-between gap-2">
        <div class="grid grid-cols-2 sm:flex sm:flex-wrap gap-1.5 w-full sm:w-auto" id="tab-bar" role="tablist" aria-label="Explorer Views">
          <button id="tab-btn-portfolio" type="button" role="tab" aria-selected="true" aria-controls="view-portfolio" data-tab="portfolio" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">1. Portfolio (59)</button>
          <button id="tab-btn-intervals" type="button" role="tab" aria-selected="false" aria-controls="view-intervals" data-tab="intervals" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">2. Cis-Intervals (26)</button>
          <button id="tab-btn-subnodes" type="button" role="tab" aria-selected="false" aria-controls="view-subnodes" data-tab="subnodes" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">3. Sub-Nodes (19)</button>
          <button id="tab-btn-analytics" type="button" role="tab" aria-selected="false" aria-controls="view-analytics" data-tab="analytics" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">4. Funnel &amp; Cohorts</button>
          <button id="tab-btn-dossiers" type="button" role="tab" aria-selected="false" aria-controls="view-dossiers" data-tab="dossiers" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">5. Dossiers (59)</button>
          <button id="tab-btn-replication" type="button" role="tab" aria-selected="false" aria-controls="view-replication" data-tab="replication" class="tab-btn px-2.5 py-1.5 rounded border border-[var(--border)] font-medium text-xs cursor-pointer">6. Replication</button>
        </div>
        <span class="hidden md:block font-mono text-xs text-[var(--muted-foreground)]">216/216 SHA-256 &middot; 48 Open Datasets &middot; 8 Flagship + 49 Runs</span>
      </div>
    </div>

    <details class="bg-[var(--card)] border border-[var(--border)] rounded-lg px-4 py-2.5 text-xs">
      <summary class="cursor-pointer font-semibold text-[var(--foreground)] select-none">Methodology &amp; Decision Guide &mdash; Track A/B Portfolio, Epistemic Asymmetry &amp; Combinatorial Strategy</summary>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2.5 mt-2 border-t border-[var(--card-border)] text-[var(--muted-foreground)] leading-relaxed">
        <div><strong class="text-[var(--foreground)]">1. Track A (Drugs) &amp; Track B (Targets):</strong> Synthesizes 59 ALS drug &amp; genetic candidates across 7 discovery modalities (de-bundling composite multi-gene axes into 19 single-gene TSA/TDL sub-nodes) using donor-level statistics (Trautwig Emory TMT n=51 is a nested subset of n=77 DIA; multi-region NYGC/Pineda donors analyzed per-region without pooling) and unbound human CNS PK (Cu,brain / Kp,uu).</div>
        <div><strong class="text-[var(--foreground)]">2. Epistemic Asymmetry Rule:</strong> Never drops an untested hypothesis due to bulk-assay blind spots. <span class="font-mono text-[var(--warning)]" title="Untested preclinical or biofluid triage queue — prospective kill-gate required">Keep &middot; Exploratory (24)</span> denotes an untested preclinical/biofluid triage queue (not therapeutic endorsement) with prospective Go/No-Go gates; <span class="font-mono text-[var(--error)]" title="Scientifically falsified by human RCT futility, CNS PK/safety wall, or confounding collapse">Drop &middot; Falsified (24)</span> requires positive human RCT futility, insurmountable PK/safety failure, or confounding collapse.</div>
        <div><strong class="text-[var(--foreground)]">3. Combinatorial Portfolio Thesis:</strong> Pairs Stage 1-gated genotype-stratified intrathecal splice rescue (evaluating 2-plex KCNQ2 C006 + STMN2 C002 vs. &le;36&ndash;48 mg 3-plex + UNC13A C001 across rs12973192/rs12608932 genotypes; unvalidated 24&ndash;48 mg scenarios) with oral non-covalent SARM1 ARM&ndash;TIR T-lock (S06, ~2&ndash;7x MWC sparing [MODEL_PRIOR]) and biomarker-gated neuroimmune precision (S07 BioVendor-bridged pNfH &le;3,700, oximetry-verified C007 sST2, Tier 3 C019 ALS-Glia bridge).</div>
      </div>
      <div class="pt-2 mt-2 border-t border-[var(--card-border)] text-[var(--muted-foreground)] font-mono text-xs">Data &amp; Provenance Standards: Open Targets / NIH IDG TDL &amp; TSA &middot; OTS 6-tier GRCh38 hybridization &middot; W3C PROV / FAIR / 4-Level Evidence Design Tiers &middot; 100% open-access recomputed data (Coordinate-Only Cis-Regulatory Search Windows, 0 chemically modified synthesis-ready ASO sequences; SantaLucia Tm/&Delta;G37 &amp; AlphaGenome AVI never rank candidates).</div>
    </details>

    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5" id="kpi-bar">
      <button type="button" data-quick-filter="ALL" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Unified Candidates</div>
        <div class="text-lg font-bold font-mono tabular-nums mt-0.5">59 <span class="text-xs font-normal text-[var(--muted-foreground)]">(7 Modalities)</span></div>
      </button>
      <button type="button" data-quick-filter="TIER12" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Tier 1 + Tier 2 Leads</div>
        <div class="text-lg font-bold font-mono tabular-nums text-[var(--success)] mt-0.5">8 <span class="text-xs font-normal text-[var(--muted-foreground)]">(3 T1 + 5 T2)</span></div>
      </button>
      <button type="button" data-quick-filter="CORE" title="Causal human ALS genetics and/or human TDP-43 pathology + functional rescue" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Keep &middot; Core Anchors</div>
        <div class="text-lg font-bold font-mono tabular-nums text-[var(--primary)] mt-0.5">4 <span class="text-xs font-normal text-[var(--muted-foreground)]">(1 Oral + 3 IT SSO)</span></div>
      </button>
      <button type="button" data-quick-filter="EXPL" title="Untested preclinical/biofluid triage queue (not therapeutic endorsement)" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Keep &middot; Exploratory</div>
        <div class="text-lg font-bold font-mono tabular-nums text-[var(--warning)] mt-0.5">24 <span class="text-xs font-normal text-[var(--muted-foreground)]">(Unproven &ne; Drop)</span></div>
      </button>
      <button type="button" data-switch-tab="intervals" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">GRCh38 Cis-Intervals</div>
        <div class="text-lg font-bold font-mono tabular-nums mt-0.5">26 <span class="text-xs font-normal text-[var(--success)]">(5 Clean &ge;2mm)</span></div>
      </button>
      <button type="button" data-quick-filter="DROP" title="Scientifically falsified by human RCT futility, CNS PK/safety wall, or confounding collapse" class="kpi-btn text-left bg-[var(--card)] border border-[var(--border)] hover:border-[var(--primary)] rounded-lg p-3 transition cursor-pointer">
        <div class="text-[var(--muted-foreground)] text-xs">Drop &middot; Falsified</div>
        <div class="text-lg font-bold font-mono tabular-nums text-[var(--error)] mt-0.5">24 <span class="text-xs font-normal text-[var(--muted-foreground)]">(9 Clin/7 PK/8 Art)</span></div>
      </button>
    </div>

    <div id="view-portfolio" role="tabpanel" aria-labelledby="tab-btn-portfolio" class="space-y-3">
      <details id="contrasts-drawer" class="bg-[var(--card)] border border-[var(--border)] border-l-4 border-l-[var(--primary)] rounded-lg px-4 py-2.5 text-xs">
        <summary class="cursor-pointer font-semibold text-[var(--foreground)] flex flex-wrap items-center justify-between gap-2 select-none">
          <span>Nine Key Mechanistic Contrasts &amp; Translational Falsifications &mdash; Field Assumptions vs. Re-Analyzed Primary Evidence</span>
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
                <th class="py-1.5 px-2 font-medium">Discriminating Gate / Rule</th>
              </tr>
            </thead>
            <tbody id="contrasts-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
          </table>
        </div>
      </details>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 flex flex-wrap items-center gap-2">
        <input id="p-search" aria-label="Search candidates" type="text" placeholder="Search ID, gene/drug, modality, hurdle, anchor..." class="bg-[var(--background)] border border-[var(--border)] rounded px-2.5 py-1.5 text-xs flex-1 min-w-[200px] text-[var(--foreground)]" />
        <select id="p-origin" aria-label="Filter by discovery modality" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
          <option value="ALL">Discovery Modality: All (59)</option>
          <option value="CANONICAL_21">Genetic, Splicing &amp; Clinical (21)</option>
          <option value="SCREEN_AND_BLIND_SURVIVORS_9">RCT Subgroup &amp; Screen Survivors (9)</option>
          <option value="HISTORICAL_BA9_NAMED_10">Postmortem Cortical BA9 RNA-seq (10)</option>
          <option value="F1_CRYPTIC_SPLICE">Unbiased &middot; TDP-43 Cryptic Exons (6)</option>
          <option value="F2_CRYPTIC_APA">Unbiased &middot; Cryptic APA / 3&apos;Ext (3)</option>
          <option value="F3_CSF_SPATIAL">Unbiased &middot; Living CSF &amp; Spatial (4)</option>
          <option value="F4_BYE2025_SCREEN">Unbiased &middot; Human iPSC-MN Screen (6)</option>
        </select>
        <select id="p-dec" aria-label="Filter by portfolio decision" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
          <option value="ALL">Decision: All (59)</option>
          <option value="KEEP_CORE">Keep &middot; Core (4)</option>
          <option value="KEEP_EXPLORATORY_UNPROVEN">Keep &middot; Exploratory (24)</option>
          <option value="RECLASSIFY_BENCHMARK_OR_BIOMARKER">Benchmark / Biomarker (7)</option>
          <option value="DROP">Drop &middot; Falsified (24)</option>
        </select>
        <select id="p-tier" aria-label="Filter by actionability tier" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
          <option value="ALL">Actionability Tier: All</option>
          <option value="TIER_12">Tier 1 + Tier 2 Leads (8)</option>
          <option value="TIER_1_ACTIONABLE_NOW">Tier 1 · Actionable Now (3)</option>
          <option value="TIER_2_FOCUSED_GATE_FIRST">Tier 2 · Focused Gate (5)</option>
          <option value="TIER_3_EXPLORATORY_DISCOVERY">Tier 3 · Exploratory Discovery (19)</option>
          <option value="COMPANION_PROTOCOL_ONLY">Companion Protocol (1)</option>
          <option value="BIOMARKER_BENCHMARK_ONLY">Biomarker / Benchmark (7)</option>
          <option value="DROPPED_FALSIFIED_EXCLUDED">Dropped · Falsified (24)</option>
        </select>
        <select id="p-sort" aria-label="Sort portfolio candidates" title="Lexicographic Portfolio Actionability tuple: (1) Actionability Tier, (2) Keep·Core before Exploratory, (3) Evidence Basis, (4) Uncrowded Whitespace vs Crowded 1-Plex, (5) Fewest Active Hurdles, (6) TRL. SantaLucia Tm/ΔG37 and AlphaGenome AVI never rank candidates." class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
          <option value="rank">Sort: Portfolio Actionability Rank</option>
          <option value="bio">Sort: Pure Biological Evidence</option>
          <option value="trl">Sort: Highest TRL</option>
          <option value="hurdles">Sort: Fewest Active Hurdles</option>
        </select>
        <button type="button" data-reset-filters="1" class="px-2.5 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xs cursor-pointer">Reset</button>
        <span id="p-count" class="font-mono tabular-nums text-[var(--muted-foreground)] text-xs ml-auto">59 / 59</span>
        <div class="w-full pt-2 mt-0.5 border-t border-[var(--card-border)] flex flex-wrap items-center gap-1.5">
          <span class="font-mono text-xs text-[var(--muted-foreground)] mr-0.5">Problem Lens:</span>
          <div id="p-lens-bar" class="flex flex-wrap gap-1.5"></div>
        </div>
        <div class="w-full pt-1.5 border-t border-[var(--card-border)] text-xs text-[var(--muted-foreground)] font-mono leading-relaxed">
          <strong class="text-[var(--foreground)]">Rank &amp; Triage Key:</strong> Act #Rk = translational actionability (tier &middot; whitespace &middot; hurdles &middot; TRL) &middot; <span class="text-[var(--primary)]">Bio #Rk</span> = pure human genetic/CNS causality &middot; <span class="text-[var(--warning)]">Keep&middot;Exploratory (24)</span> = untested triage queue (not endorsement) &middot; [MODEL_PRIOR] never ranks candidates.
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div class="lg:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg overflow-hidden lg:relative lg:min-h-[520px]">
          <div class="max-h-[420px] lg:max-h-none lg:absolute lg:inset-0 overflow-y-auto overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead class="sticky top-0 z-10 bg-[var(--card)] shadow-sm">
                <tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th class="py-2 px-2 font-medium">Rk</th>
                  <th class="py-2 px-1.5 font-medium">ID</th>
                  <th class="py-2 px-2 font-medium">Program / Gene / Drug</th>
                  <th class="py-2 px-1.5 font-medium">Decision</th>
                  <th class="hidden xl:table-cell py-2 px-1.5 font-medium">Tier</th>
                  <th class="hidden xl:table-cell py-2 px-1.5 font-medium">TRL</th>
                  <th class="hidden xl:table-cell py-2 px-1.5 font-medium text-right" title="Active Unsolved Hurdles">Hurd.</th>
                  <th class="py-2 px-2 font-medium text-right">Dossier</th>
                </tr>
              </thead>
              <tbody id="p-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
            </table>
          </div>
        </div>
        <div id="p-detail" class="lg:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-3"></div>
      </div>
    </div>
"""

HTML_TABS_AND_SCRIPT = """    <div id="view-intervals" role="tabpanel" aria-labelledby="tab-btn-intervals" class="hidden space-y-3">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 space-y-2">
        <div class="flex flex-wrap items-center gap-2">
          <input id="iv-search" aria-label="Search GRCh38 intervals" type="text" placeholder="Filter gene, ID, coordinate..." class="bg-[var(--background)] border border-[var(--border)] rounded px-2.5 py-1.5 text-xs min-w-[180px] text-[var(--foreground)]" />
          <select id="iv-status" aria-label="Filter by off-target safety status" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
            <option value="ALL">OTS Off-Target Verdict: All (26)</option>
            <option value="PASS_CLEAN_GE2MM">Pass &middot; Clean &ge;2mm (5)</option>
            <option value="CAUTION_1MM_OR_WOBBLE_NONCONSTRAINED">Caution &middot; Non-Constrained 1mm/Wobble (14)</option>
            <option value="WARN_1MM_OR_WOBBLE_CONSTRAINED_NEURONAL">Warn &middot; Constrained CNS 1mm/Bulge (5)</option>
            <option value="FAIL_EXACT_0MM_OFFTARGET">Fail &middot; Exact 0mm Off-Target (2)</option>
          </select>
          <select id="iv-origin" aria-label="Filter by interval design panel" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
            <option value="ALL">Design Panel: All (26)</option>
            <option value="PHASE2_3A_MULTIPLEX_12">Core 3-Plex &amp; 14q12 Panel (12)</option>
            <option value="PHASE3B_DENOVO_14">Single-Entity De Novo Leads (14)</option>
          </select>
          <label class="flex items-center gap-1.5 text-xs text-[var(--foreground)] cursor-pointer">
            <input id="iv-leads" type="checkbox" class="accent-[var(--primary)]" /> Promoted Leads Only (10)
          </label>
          <button type="button" data-reset-intervals="1" class="px-2.5 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xs cursor-pointer">Reset</button>
          <span id="iv-count" class="font-mono tabular-nums text-[var(--muted-foreground)] text-xs ml-auto">26 / 26</span>
        </div>
        <div class="text-xs text-[var(--muted-foreground)] border-t border-[var(--card-border)] pt-2 leading-relaxed">
          <strong class="font-mono text-[var(--foreground)]">OTS Coordinate &amp; Hybridization Standard (1-Based Closed GRCh38 Search-Window Anchors &middot; 0 Chemically Modified Synthesis-Ready ASO Sequences):</strong>
          Sequence-clean locus anchors for empirical 1-nt microwalks + human neuron <span class="font-mono">Ca2+</span>-oscillation, <span class="font-mono">TLR9</span> &amp; primary <span class="font-mono">DRG</span> screens (GENCODE v46 reference cleanliness does not exclude phosphorothioate protein-binding toxicity) &middot;
          SantaLucia <span class="font-mono">2'-O-MOE PO/PS Tm / &Delta;G37</span> [MODEL_PRIOR] + <span class="font-mono">AlphaGenome AVI Phred</span> (DNA-variant conservation/splicing prior, not steric ASO potency certification) &middot;
          <span class="font-mono">mRNA 0/1/wob</span> = GENCODE v46 spliced mRNA (&le;200bp of splice junction) 0mm / 1mm / G:U wobble-only genes &middot;
          <span class="font-mono">Pre-mRNA 6-tier</span> = sense 0mm / 1mm (&le;50bp SS) / wobble (&le;50bp) / 2mm (&le;25bp) / 1-nt bulge / 18-nt sub-core.
        </div>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs">
          <thead>
            <tr class="border-b border-[var(--card-border)] bg-[var(--background)] text-[var(--muted-foreground)] font-mono">
              <th colspan="5" class="py-1.5 px-2.5 border-r border-[var(--card-border)]">1. Target Locus, Role &amp; OTS Mechanism</th>
              <th colspan="2" class="py-1.5 px-2 border-r border-[var(--card-border)]">2. Thermodynamics &amp; AVI</th>
              <th colspan="4" class="py-1.5 px-2 border-r border-[var(--card-border)]">3. GENCODE v46 Off-Target Hybridization Audit (254,070 tx)</th>
              <th colspan="1" class="py-1.5 px-2">4. Browsers</th>
            </tr>
            <tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
              <th class="py-2 px-2.5">#</th><th class="py-2 px-2">Gene #Rk &amp; Portals</th><th class="py-2 px-2">Role / Lead</th><th class="py-2 px-2">GRCh38 Coordinate (Ensembl)</th>
              <th class="py-2 px-2 border-r border-[var(--card-border)]">OTS Splicing Mode</th>
              <th class="py-2 px-2" title="Modeled SantaLucia nearest-neighbor melting temperature, free energy, and GC%">Tm / &Delta;G37 / GC</th>
              <th class="py-2 px-2 border-r border-[var(--card-border)]" title="Max AlphaGenome Variant Impact Phred score across interval">max AVI</th>
              <th class="py-2 px-2" title="Spliced mRNA <=200bp of splice junction: 0mm / 1mm / wobble-only genes">mRNA 0/1/wob</th>
              <th class="py-2 px-2" title="Pre-mRNA sense: 0mm / 1mm <=50bp SS / wobble <=50bp / 2mm <=25bp / 1-nt bulge / 18-nt sub-core">Pre-mRNA 6-Tier</th>
              <th class="py-2 px-2">Constrained CNS Gene Flags (gnomAD v4)</th><th class="py-2 px-2 border-r border-[var(--card-border)]">Safety Verdict</th>
              <th class="py-2 px-2">Atlas &middot; UCSC</th>
            </tr>
          </thead>
          <tbody id="iv-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
        </table>
      </div>
    </div>

    <div id="view-subnodes" role="tabpanel" aria-labelledby="tab-btn-subnodes" class="hidden space-y-3">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 space-y-2">
        <div class="flex flex-wrap items-center gap-2">
          <select id="sn-parent" aria-label="Filter sub-nodes by parent composite axis" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
            <option value="ALL">Parent Composite Axis: All (19)</option>
            <option value="C014">C014 &middot; CHMP7 / CHMP2B Nuclear Surveillance (2)</option>
            <option value="C015">C015 &middot; SNARE / Rab Vesicle Axis (8)</option>
            <option value="C017">C017 &middot; Chitinase / GPNMB Glial Axis (4)</option>
            <option value="C018">C018 &middot; Classical Complement C1q/C3/C4B (5)</option>
          </select>
          <select id="sn-verd" aria-label="Filter sub-nodes by single-gene verdict" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]">
            <option value="ALL">Single-Gene Verdict: All (19)</option>
            <option value="KEEP_">Keep &middot; Exploratory Sub-Nodes (8)</option>
            <option value="RECLASSIFY_">Reclassify &middot; Fluid Biomarkers (4)</option>
            <option value="DROP">Drop &middot; Falsified / Passenger / Toxic (7)</option>
          </select>
          <button type="button" data-reset-subnodes="1" class="px-2.5 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xs cursor-pointer">Reset</button>
          <span id="sn-count" class="font-mono tabular-nums text-[var(--muted-foreground)] text-xs ml-auto">19 / 19</span>
        </div>
        <div class="text-xs text-[var(--muted-foreground)] border-t border-[var(--card-border)] pt-2 leading-relaxed">
          <strong class="font-mono text-[var(--foreground)]">Open Targets / NIH IDG TDL &amp; Objective TSA De-Bundling Protocol:</strong>
          Multi-gene composite axes are split into 19 single-gene dossiers annotated with <strong class="text-[var(--foreground)]">NIH IDG Target Development Level</strong> (<span class="font-mono">Tclin / Tchem / Tbio</span>) and objective <strong class="text-[var(--foreground)]">Target Safety Assessment (TSA)</strong> states anchored on <span class="font-mono">gnomAD v4 LOEUF/pLI</span> (heterozygous pLoF haploinsufficiency, distinct from biallelic recessive phenotypes), <span class="font-mono">DepMap 1,258-line Chronos</span>, and <span class="font-mono">OMIM / IMPC</span> phenotypes (zero subjective composite safety scores).
        </div>
      </div>
      <div id="sn-cards" class="grid grid-cols-1 md:grid-cols-2 gap-3"></div>
    </div>

    <div id="view-analytics" role="tabpanel" aria-labelledby="tab-btn-analytics" class="hidden space-y-3">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div id="panel-funnel" class="lg:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h2 class="text-sm font-semibold">59-Candidate Discovery-Modality &amp; Falsification Funnel</h2>
            <span class="font-mono text-xs text-[var(--muted-foreground)]">59-Candidate Triage &amp; Attrition Flow &middot; Epistemic Asymmetry</span>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-relaxed">Intrinsic attrition across all 7 biological discovery modalities (<span class="font-mono text-[var(--warning)]">Unproven &ne; Drop</span>: 100% of unbiased cryptic-splicing &amp; cryptic-APA leads remain exploratory pending RT-ddPCR/SSO gates, whereas 8/10 postmortem cortical BA9 calls, 9 failed RCT regimens &amp; 7 PK/safety walls are falsified). Click any cohort bar or falsification gate to filter Portfolio.</p>
          <div id="funnel-svg-box" class="w-full"></div>
          <div class="border-t border-[var(--card-border)] pt-2.5 space-y-1.5">
            <div class="font-mono font-semibold text-xs text-[var(--muted-foreground)]">Positive Falsification Gates Across Dropped Candidates (N=24 &middot; Click to Filter):</div>
            <div id="drop-gates-box" class="grid grid-cols-1 sm:grid-cols-3 gap-2"></div>
          </div>
        </div>
        <div class="lg:col-span-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2.5">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h2 class="text-sm font-semibold">Multi-Region NYGC Spinal &amp; Cortical Panel (<a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE153960" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted hover:decoration-solid font-mono">GSE153960</a> &middot; <a href="https://pubmed.ncbi.nlm.nih.gov/36482247/" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted hover:decoration-solid font-mono">PMID:36482247</a>)</h2>
            <select id="nygc-reg" aria-label="Select NYGC anatomical region" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs text-[var(--foreground)]">
              <option value="Spinal_Cord_Cervical">Cervical Cord (N=206)</option>
              <option value="Spinal_Cord_Lumbar">Lumbar Cord (N=181)</option>
              <option value="Cortex_Motor">Motor Cortex (N=120)</option>
            </select>
          </div>
          <div id="nygc-meta" class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] flex flex-wrap items-center justify-between gap-2 text-xs font-mono"></div>
          <p class="text-[var(--muted-foreground)] text-xs leading-relaxed"><strong class="text-[var(--foreground)]">Protocol Guide:</strong> <span class="font-mono">RIN+GC &beta;</span> shows donor-level OLS shift (<span class="font-mono">&Delta;log2CPM</span>, inline Cleveland lollipop <span class="font-mono">-0.60..+0.60</span>). <span class="font-mono">SOD1/FUS p &gt; 0.25</span> indicates non-significant difference in small <span class="font-mono">n=9</span> (underpowered to prove equivalence, mandating junction <span class="font-mono">RT-ddPCR</span>). <span class="font-mono">Tail %</span> = genome-wide neuronal-mass-residualized (neuronal-mass Z-score) coupling percentile to cryptic <span class="font-mono">tSTMN2</span>.</p>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead>
                <tr class="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th class="py-1.5 px-1.5">Gene &amp; Portals</th>
                  <th class="py-1.5 px-1.5 min-w-[140px]" title="RIN + GC% adjusted OLS slope (ALS-TDP vs Control, -0.60 to +0.60 lollipop)">RIN+GC &beta; (&Delta;log2CPM)</th>
                  <th class="py-1.5 px-1.5">adj p</th>
                  <th class="py-1.5 px-1.5" title="ALS-TDP vs ALS-SOD1/FUS negative-control specificity p-value">SOD1/FUS p</th>
                  <th class="py-1.5 px-1.5" title="Neuronal-mass-residualized (neuronal-mass Z-score) tSTMN2 coupling slope and p-value">tSTMN2 &beta; (p)</th>
                  <th class="py-1.5 px-1.5 text-right" title="Empirical genome-wide neuronal lower-tail percentile">Tail %</th>
                </tr>
              </thead>
              <tbody id="nygc-tbody" class="divide-y divide-[var(--card-border)]"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div id="view-dossiers" role="tabpanel" aria-labelledby="tab-btn-dossiers" class="hidden">
      <div class="md:hidden mb-3 sticky top-2 z-20 bg-[var(--card)] border border-[var(--border)] rounded-lg p-2 flex items-center gap-1.5 shadow-sm">
        <button id="d-mobile-prev" type="button" data-open-dossier="BA9-10" class="px-2 py-1 rounded border border-[var(--border)] font-mono text-xs shrink-0 cursor-pointer">&larr;</button>
        <select id="d-mobile-select" aria-label="Select Candidate Dossier" class="flex-1 min-w-0 truncate bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs font-medium text-[var(--foreground)]"></select>
        <button id="d-mobile-next" type="button" data-open-dossier="C006" class="px-2 py-1 rounded border border-[var(--border)] font-mono text-xs shrink-0 cursor-pointer">&rarr;</button>
        <button type="button" data-toggle-d-rail="1" aria-expanded="false" aria-controls="d-aside" class="px-2 py-1 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs shrink-0 cursor-pointer">List</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-[228px_minmax(0,1fr)] gap-3 items-start">
        <aside id="d-aside" aria-label="Candidate Directory" class="hidden md:flex md:flex-col bg-[var(--card)] border border-[var(--border)] rounded-lg p-2.5 gap-2 md:sticky md:top-3 max-h-[calc(100vh-1.5rem)]">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-xs">Candidate Directory</span>
            <span id="d-nav-count" class="font-mono tabular-nums text-xs text-[var(--muted-foreground)]">59 / 59</span>
          </div>
          <input id="d-search" aria-label="Search candidate directory" type="text" placeholder="Jump: ID, gene, drug..." class="w-full bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs text-[var(--foreground)]" />
          <div id="d-slice-bar" class="flex flex-wrap gap-1"></div>
          <select id="d-lens" aria-label="Filter by Mechanistic Problem Lens" class="w-full bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1 text-xs text-[var(--foreground)]"></select>
          <div id="d-nav" class="space-y-0.5 flex-1 min-h-0 max-h-[68vh] overflow-y-auto pr-0.5"></div>
        </aside>
        <div id="d-content" class="min-w-0 space-y-3"></div>
      </div>
    </div>

    <div id="view-replication" role="tabpanel" aria-labelledby="tab-btn-replication" class="hidden space-y-3">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-mono font-semibold text-xs text-[var(--success)]">LEVEL 1 &middot; CACHED GATES (&lt;10s &middot; 0 MB)</span>
            <span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">Offline Ready</span>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-snug">Clones the &lt;18 MB repository, installs pinned Python 3.12 dependencies (<span class="font-mono">uv.lock</span>), and verifies all 16 CSV schemas, foreign keys, Epistemic Asymmetry rules, and 216/216 64-char SHA-256 digests.</p>
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] flex items-center justify-between gap-2 font-mono text-xs">
            <span class="truncate">uv sync --frozen &amp;&amp; uv run python scripts/verify_carbon_als.py --mode cached</span>
            <button type="button" data-copy-cmd="git clone https://github.com/helloimra/ExploreALS.git &amp;&amp; cd ExploreALS &amp;&amp; uv sync --frozen &amp;&amp; uv run python scripts/verify_carbon_als.py --mode cached" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] shrink-0 cursor-pointer">Copy</button>
          </div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-mono font-semibold text-xs text-[var(--primary)]">LEVEL 2 &middot; 8 FLAGSHIP &amp; RAW COHORTS</span>
            <span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">rtol = 1e-4</span>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-snug">Runs the 8 single-command Tier 1+2 monograph reproducers immediately, or fetches the 48 open datasets (<span class="font-mono">677.6 MB</span>) with 64-char SHA-256 verification to rerun donor-level OLS and 254,070-tx scans.</p>
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] flex items-center justify-between gap-2 font-mono text-xs">
            <span class="truncate">uv run python scripts/reproduce_all.py --flagship-only</span>
            <button type="button" data-copy-cmd="uv run python scripts/reproduce_all.py --flagship-only" class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] shrink-0 cursor-pointer">Copy</button>
          </div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3.5 space-y-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-mono font-semibold text-xs text-[var(--warning)]">LEVEL 3 &middot; REBUILD WEB &amp; SANITIZE</span>
            <span class="px-1.5 py-0.5 rounded border border-[var(--border)] font-mono text-xs text-[var(--muted-foreground)]">Zero-CDN</span>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-snug">Re-compiles this 6-tab Explorer and all 8 standalone monographs from the CSV registries and runs the archive-aware biosecurity &amp; host-path sanitization gate (<span class="font-mono">0</span> external CDN requests).</p>
          <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] flex items-center justify-between gap-2 font-mono text-xs">
            <span class="truncate">uv run python scripts/audit_public_sanitization.py --target .</span>
            <button type="button" data-copy-cmd="uv run python work/phase4_final_synthesis/scripts/02_render_phase4_synthesis.py --public-docs-only &amp;&amp; uv run python scripts/audit_public_sanitization.py --target ." class="px-2 py-0.5 rounded border border-[var(--border)] hover:border-[var(--primary)] text-[var(--link)] shrink-0 cursor-pointer">Copy</button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div class="lg:col-span-5 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h2 class="text-sm font-semibold">W3C PROV Computational Lineage DAG</h2>
            <span class="font-mono text-xs text-[var(--muted-foreground)]">Click Node to Filter Workbench</span>
          </div>
          <div id="rep-dag-box" class="w-full"></div>
          <p class="text-[var(--muted-foreground)] text-xs leading-snug font-mono">Environment: Python &ge;3.12 &middot; hatchling editable <span class="text-[var(--foreground)]">src/carbon_als</span> &middot; MIT (code) + CC-BY-4.0 (registries/prose) &middot; GitHub Codespaces ready.</p>
        </div>
        <div class="lg:col-span-7 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h2 class="text-sm font-semibold">Cohort Participant Overlap &amp; Donor-Level Regression Rules (8 Clusters)</h2>
            <span class="font-mono text-xs text-[var(--muted-foreground)]">Anti-Pseudoreplication Contract</span>
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

      <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-3 flex flex-wrap items-center gap-2">
        <div class="flex flex-wrap gap-1.5" role="group" aria-label="Replication Workbench Mode">
          <button type="button" data-rep-mode="runs" class="rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer">8 Flagship + 49 Runs (57)</button>
          <button type="button" data-rep-mode="datasets" class="rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer">Staged Datasets (48)</button>
          <button type="button" data-rep-mode="evidence" class="rep-mode-btn px-2.5 py-1.5 rounded border font-mono text-xs cursor-pointer">216 Evidence SHA-256 &amp; Formulas</button>
        </div>
        <input id="rep-search" aria-label="Search replication workbench" type="text" placeholder="Search Run ID, DS ID, candidate, formula, SHA-256, script..." class="bg-[var(--background)] border border-[var(--border)] rounded px-2.5 py-1.5 text-xs flex-1 min-w-[200px] text-[var(--foreground)]" />
        <select id="rep-filter" aria-label="Filter replication workbench" class="bg-[var(--background)] border border-[var(--border)] rounded px-2 py-1.5 text-xs text-[var(--foreground)]"></select>
        <button type="button" data-reset-rep="1" class="px-2.5 py-1.5 rounded border border-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] text-xs cursor-pointer">Reset</button>
        <span id="rep-count" class="font-mono tabular-nums text-[var(--muted-foreground)] text-xs ml-auto">57 / 57</span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">
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
          <p class="text-[var(--muted-foreground)] text-xs leading-snug">Generate byte-clean CSV or JSON exports directly from the verified embedded payload (works offline on <span class="font-mono">file://</span> and matches <span class="font-mono">registries/*.csv</span> in GitHub):</p>
          <div class="flex flex-wrap gap-1.5">
            <button type="button" data-dl-reg="portfolio" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; Portfolio (59 CSV)</button>
            <button type="button" data-dl-reg="intervals" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; Cis-Windows (26 CSV)</button>
            <button type="button" data-dl-reg="subnodes" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; Sub-Nodes (19 CSV)</button>
            <button type="button" data-dl-reg="formulas" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; 216 Evidence &amp; Formulas (CSV)</button>
            <button type="button" data-dl-reg="datasets" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; 48 Datasets SHA-256 (CSV)</button>
            <button type="button" data-dl-reg="runs" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; 49 Runs + 8 Flagship (CSV)</button>
            <button type="button" data-dl-reg="overlap" class="px-2.5 py-1.5 rounded border border-[var(--border)] hover:border-[var(--primary)] font-mono text-xs text-[var(--link)] cursor-pointer">&darr; 8 Cohort Overlaps (CSV)</button>
            <button type="button" data-dl-reg="json_all" class="px-2.5 py-1.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-mono font-semibold text-xs cursor-pointer">&darr; Full Provenance Bundle (JSON)</button>
          </div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-2">
          <div class="flex items-center justify-between gap-2 flex-wrap">
            <h3 class="text-sm font-semibold">Cryptographic Hash Coverage &amp; Biosecurity Audit Summary</h3>
            <span class="font-mono text-xs text-[var(--success)]">216 / 216 (100%) SHA-256</span>
          </div>
          <div class="grid grid-cols-3 gap-2 font-mono text-xs">
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)]">Staged Datasets</div><div class="font-bold text-sm text-[var(--foreground)] mt-0.5">156 <span class="text-xs font-normal text-[var(--muted-foreground)]">(48 DS)</span></div></div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)]">API Snapshots</div><div class="font-bold text-sm text-[var(--foreground)] mt-0.5">53 <span class="text-xs font-normal text-[var(--muted-foreground)]">(JSON)</span></div></div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)]"><div class="text-[var(--muted-foreground)]">Model Outputs</div><div class="font-bold text-sm text-[var(--foreground)] mt-0.5">7 <span class="text-xs font-normal text-[var(--muted-foreground)]">(ODE/MWC)</span></div></div>
          </div>
          <p class="text-[var(--muted-foreground)] text-xs leading-snug">Legal redistribution split across <span class="font-mono">677.61 MB</span> (<span class="font-mono">646.22 MiB</span>): <strong class="text-[var(--foreground)]">Tier A</strong> (<span class="font-mono">CC0/CC-BY</span> open release + git maps), <strong class="text-[var(--foreground)]">Tier B</strong> (direct publisher/EuropePMC HTTPS fetch, zero re-hosting of <span class="font-mono">CC BY-NC-ND</span> supplements), and <strong class="text-[var(--foreground)]">Tier C</strong> (<span class="font-mono">SYNAPSE_AUTH_TOKEN</span> / historical intake). <strong class="text-[var(--foreground)]">Coordinate-Only Cis-Regulatory Search Windows</strong> omit chemically modified synthesis-ready ASO constructs.</p>
        </div>
      </div>

      <details id="sandbox-drawer" class="bg-[var(--card)] border border-[var(--border)] border-l-4 border-l-[var(--warning)] rounded-lg px-4 py-3 text-xs">
        <summary class="cursor-pointer font-semibold text-[var(--foreground)] flex flex-wrap items-center justify-between gap-2 select-none">
          <span>Interactive Model-Prior Sensitivity Sandboxes &mdash; Stress-Test Channel Stoichiometry, Allostery &amp; Survival Power</span>
          <span class="px-2 py-0.5 rounded border border-[var(--warning)] text-[var(--warning)] font-mono text-xs">&#9671; [MODEL_PRIOR &middot; Zero-Install Sensitivity Check]</span>
        </summary>
        <div id="sandbox-body" class="pt-3 mt-2.5 border-t border-[var(--card-border)] grid grid-cols-1 md:grid-cols-3 gap-3"></div>
      </details>
    </div>

    <section aria-label="Attribution, AI Methodology and Research Disclaimer" class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 text-xs text-[var(--muted-foreground)] leading-relaxed">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="space-y-1">
          <div class="font-mono font-semibold text-[var(--foreground)]">Author, Correspondence &amp; Open-Science Attribution</div>
          <p>Curated by <strong class="text-[var(--foreground)]">Ricardo Agoga</strong> (Independent Researcher) &middot; Correspondence &amp; scientific inquiries: <a href="mailto:helloimra@proton.me" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">helloimra@proton.me</a> &middot; Repository: <a href="https://github.com/helloimra/ExploreALS" target="_blank" rel="noopener noreferrer" class="text-[var(--link)] underline decoration-dotted underline-offset-2 hover:decoration-solid font-mono">github.com/helloimra/ExploreALS &nearr;</a>.</p>
          <p>Primary data &amp; tool attributions: Google DeepMind AlphaGenome (v1 API &amp; Atlas AVI; non-commercial research use only), NIH GTEx (v8 / v10), Open Targets (v4), gnomAD (v4.1), Ensembl/GENCODE (v46), ChEMBL (v34), UniProt, RCSB PDB, and ClinicalTrials.gov.</p>
        </div>
        <div class="space-y-1">
          <div class="font-mono font-semibold text-[var(--warning)]">Preclinical Research Notice &amp; AI-Assisted Workflow Disclosure</div>
          <p><strong class="text-[var(--foreground)]">Not Medical Advice:</strong> ExploreALS v1.2 is an independent preclinical and translational research resource intended solely for scientific hypothesis generation. Nothing herein constitutes medical advice, clinical trial recruitment, or a treatment recommendation; individuals with ALS and caregivers should always consult their neurologist or ALS care team before starting, stopping, or modifying any therapy.</p>
          <p><strong class="text-[var(--foreground)]">AI-Assisted Methodology:</strong> Synthesized via human-directed multi-agent AI research workflows paired with deterministic Python statistical recomputation across 48 SHA-256-verified open-access staged datasets and primary-source verification (PubMed, Europe PMC, ClinicalTrials.gov). Quantitative contrasts and accessions are programmatically audited and separated from modeling priors (<span class="font-mono">[MODEL_PRIOR]</span>), though synthesis prose may contain residual errors — always verify against linked primary sources before experimental use.</p>
        </div>
      </div>
    </section>
  </div>
"""
