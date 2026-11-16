# G1A06 R1 run bundle (version 5, 1 Nov 2026)

A self-contained, pre-registered test of 14 gene-by-cell-type differences between sporadic ALS and control donors
in dorsolateral prefrontal cortex (Brodmann area 9), found in a public single-nucleus dataset (Pineda et al., Cell
2024, PMID 38521060, Synapse syn51105515). It runs on your machine and returns **summary numbers only**.

## What it returns, and what it never returns
- Returns (folder `results/`): eligibility and attrition counts by group; the cell-type crosswalk table; realized
  power; a batch-balance check (Cramer's V, a warning only); the null-simulation verdict; for each of the 14 tests the estimate, standard error, one-sided p, the Holm
  decision, intervals and donor counts per group; sensitivity analyses; age quartiles and sex counts by group; and,
  if you supply the optional genome-wide counts file, per-gene statistics for every gene in each tested cell type
  (group difference, standard error, t, and mean expression; no per-donor value).
- Never returns: donor or sample identifiers, per-donor values, expression matrices. Per-donor working files are
  written to a separate private folder, which stays with you. A final check refuses to write results that contain any
  donor or sample identifier from your input.

## Requirements
Python 3.13 with numpy 2.5 and scipy 1.18 (tested with Python 3.13.16, numpy 2.5.3, scipy 1.18.1; `environment.txt`).
Nothing else. Run Python with `-I -B` from outside the bundle folder.

## Steps
1. **Check the bundle on made-up data first.** Two parts, both on invented data: (a) the pre-registered positive
   control (a planted 1.5-fold effect in all 14 tests must be recovered in at least 80% of 5,000 simulated runs at 35
   donors per group); (b) a made-up cohort of 35 donors per group, with the same ages in both groups and a planted
   1.5-fold effect, run end to end, including the full null simulation and the optional genome-wide step on 2,000
   made-up genes (about ten minutes with 4 workers):
   `python3 -I -B path/to/bundle/run_g1a06_r1.py selftest --dir selftest_out --workers 4`
2. **Write the crosswalk gene list:** `python3 -I -B path/to/bundle/run_g1a06_r1.py features --out features.tsv`
   (1,900 genes; none of the 10 genes under test is among them).
3. **Prepare the inputs** (below) in one folder.
4. **Run once:** `python3 -I -B path/to/bundle/run_g1a06_r1.py run --input in --results results --private private --workers 4`
5. **Return the `results/` folder only.**

The bundle checks its own files against `MANIFEST.sha256` and refuses to run if any file was changed.

## Inputs (CSV, UTF-8, one header row)
- `cohort_sheet.json`: `cohort_name`; `region` (BA9); `assay` ("single-nucleus RNA-seq" is required: whole-cell
  single-cell RNA-seq is ineligible); `chemistry` (the kit and chemistry version, for example the 10x kit and version;
  required; if more than one was used, name each, separated by semicolons, and add a `batch_chemistry` column to
  `samples.csv`, or the run stops as ineligible); `brain_banks` (the bank or banks the donors came from, by name:
  name every bank that appears in `donors.csv` `brain_bank`, spelled the same way, as a list or separated by
  semicolons; case and spacing are ignored);
  `sporadic_definition`; `c9orf72_testing`; `doublet_handling`; `any_donor_from_mayo_clinic_jacksonville` ("no" is
  required); `independence_basis` ("source statement" if you or your source state in writing that no donor overlaps
  the Pineda et al. cohort, "trusted crosswalk" if donor IDs were compared through a trusted crosswalk, otherwise a
  short description; either of the first two counts only with every bank named in `brain_banks`);
  `interleaving_statement` and `interleaving_judgement` (both used only if no prep batch is recorded, below);
  `labels_doublet_or_low_quality` (a list of your cell labels that are doublets or low quality).
- `donors.csv`: `donor`, `brain_bank`, `diagnosis` (ALS, control or other), `sporadic_label` (yes if your source labels
  the donor sporadic ALS), `c9orf72` (negative, positive or not_tested), `family_history` (negative, positive,
  uncertain or blank), `neuropath_normal` (yes for neuropathologically normal controls), `age` (at death), `sex` (M or
  F), `pmi` and `rin` (optional; blank if not recorded).
- `samples.csv`: `sample`, `donor`, `region` (BA9 samples are used; others are ignored), and one `batch_<name>` column
  per recorded batch factor (for example `batch_prep`, `batch_sequencing_run`). Every BA9 sample needs a level in
  every factor: a blank in any batch column of a BA9 sample of an eligible donor stops the run as ineligible.
  If the eligible donors come from two or more brain banks and there is no `batch_bank` column, the runner adds one
  from `donors.csv` `brain_bank`, since bank or site counts as a batch factor; a blank `brain_bank` then stops the run
  as ineligible. A factor whose level is fixed by another recorded factor (for example a bank, kit or isolation date
  nested within prep batches) is already in the model through that factor and is left out of the design; the run
  header names it and the factor that fixes it, and `batch_check.tsv` gives it a row. A nuclei-preparation batch
  (`batch_prep`) or nuclei-isolation date (`batch_isolation_date`) is required. Without either, whatever other batch
  factors are recorded, the cohort is eligible only if `interleaving_statement` documents that cases and controls
  were processed interleaved, and whether that statement
  qualifies is the study team's judgement, made before any expression is read: the first run then stops before
  reading `counts.csv`; send back the results folder, and run again only once the study team's judgement has been
  entered as `interleaving_judgement` (it starts with "qualifies").
- `counts.csv`: one row per sample and cell label: `sample`, `label`, `nuclei`, `total_counts` (all genes, summed
  over the nuclei of that label in that sample), then the summed counts of `BRSK2`, `KIFC2`, `MYO18A`, `DNAJB2`,
  `AP1G2`, `ZNF783`, `AGAP2`, `SNPH`, `MIB2`. Use your doublet-filtered nuclei.
- `label_profiles.csv`: one row per cell label: `label`, then one column per gene of `features.tsv` (Ensembl ID, or
  symbol), holding that label's counts summed over all samples.
- Optional: `counts_ambient_corrected.csv` and `counts_no_doublet_removal.csv`, in the format of `counts.csv`, for two
  sensitivity analyses.
- Optional, and much requested: `counts_all_genes.csv`: one row per sample and cell label, as in `counts.csv`:
  `sample`, `label`, then one column per gene (every gene you measured, by Ensembl ID or symbol), holding that label's
  counts summed over its nuclei in that sample. It must have a row for every sample and label of `counts.csv` and the
  same counts for any of the nine tested genes it includes. It lets the study team check whether each tested gene
  stands out from genes of similar GC content and expression; without it, that check cannot be made.

## How it decides (fixed in advance; summary)
- Eligibility on metadata only: single-nucleus RNA-seq with the chemistry recorded (and a `batch_chemistry` column
  if it varies); a prep batch recorded (or the interleaving route above); sporadic ALS by your source's own label,
  known C9orf72 carriers and familial cases excluded, neuropathologically normal controls, age and sex recorded, no
  donor from the Mayo Clinic Jacksonville bank.
- No shared donors with the original study: the bundle never compares donor IDs. The run header says "certified" only
  when the cohort sheet names every brain bank that `donors.csv` gives the eligible donors and there is either a
  written statement of no shared donors or a trusted crosswalk; otherwise it says "provisionally supported" (and lists
  any bank not named), and the study team decides how that result is read.
- Cell types: each of your labels is matched to the reference cell types of the original study by correlation over
  the 1,900 genes; a label that does not match one type clearly is left out; labels matching one type are pooled.
- Per donor and cell type, counts are summed; the analysis is log2 counts per million ~ group + age + sex + batch
  (every recorded batch factor, bank and chemistry included), one-sided Holm at 0.025 across the 14 tests. Before the
  fit, a null simulation on your design (no real expression) must show the error rates are within bounds; if not, the
  run stops with no fit.
- The expression floor ([A4]) is checked per test inside the fit, on the donors the depth rule keeps, from counts only
  and without group labels. Realized power is printed before that check, so a test can show power and then be
  reported not estimable (floor).
- With `counts_all_genes.csv`, every gene in each tested cell type is fitted with the same model, depth rule and
  expression floor as the tested genes, after the primary fit (`genomewide_<type>.tsv`, `genomewide_summary.tsv`).
  These results decide nothing in this run; if the file is missing or inconsistent, the summary says why and the
  rest of the run is unaffected.
- `batch_check.tsv` gives Cramer's V between group and each batch factor per tested cell type. Above 0.7 it is flagged,
  as a warning only: it never stops a run, and a low value certifies nothing.

## If the run stops before the fit
The run can stop before any expression value is analysed. The results folder then holds the reason and no estimates.
Return it as it is; what happens next is decided by the study team, not by you. Known causes:
- No prep batch is recorded and the study team has not yet judged the interleaving statement (above).
- The crosswalk: if any of the six tested cell types receives none of your labels (every candidate label refused,
  or fewer than 80% of the 1,900 crosswalk genes measured), the null simulation's preflight stops the whole run.
- The null simulation itself. It includes a small age effect that the analysis model does not fit (a squared age
  term). With your actual group labels it shifts the group estimate by a fixed amount whenever the two groups' ages
  differ in spread or shape, and the pre-registered tolerance is tight, so a stop can happen even with well-matched
  cohorts. The report's design summary shows the size of that shift for each test. If the null-simulation check named
  S4b does not pass, the "no depth exclusion" rows of `sensitivities.tsv` are marked as not readable as calibrated.
- Batch: a BA9 sample of an eligible donor has a blank level in a batch column; brain_bank is blank for an eligible
  donor in a cohort that pools banks; or the cohort sheet names more than one chemistry version and `samples.csv` has
  no `batch_chemistry` column (above).

## Privacy, and what is not collected
- The final check refuses results containing any donor or sample identifier of four characters or more; shorter
  identifiers are not checked, so please use identifiers of at least four characters. Small groups (age quartiles,
  sex strata, nuclei sums) are not screened for disclosure of a single donor: look at `results/` before returning it.
- The null-simulation report's header records the path of the private design file relative to the folder you ran
  from; with the command in step 4 it is `private/design.tsv`. Run from the folder that holds `private/` so that no
  other folder name appears.
- Not collected: Braak stage, Thal phase, co-pathology, onset site, disease duration and cause of death. The study team
  may ask for them separately, as group summaries.

## Bundle choices the pre-registered rules leave open
- B-1: the 14 discovery residual SDs ship as their own small file (`params/resid_sd_lines.out`).
- B-2: the crosswalk method (`crosswalk.py`): correlation over 1,900 marker genes, thresholds 0.70 and 0.02.
- B-3: the precision-weighted sensitivity uses weights 1 / (1/expected count + 1/nuclei).
- B-4: the unadjusted sensitivity drops age and sex and keeps batch.
- B-5: with no prep batch, the run stops before reading expression until the study team's judgement of the
  interleaving statement is entered in the cohort sheet, whether or not other batch factors are recorded.
- B-6: "underpowered" (below 50% realized power) is read at the first Holm step (alpha 0.025/14).
- B-7: sensitivities that leave donors out recompute the depth median and the expression floor within that subset.
- B-8: PMI and RIN are each added alone as a covariate, not together.
- B-9: the genome-wide outputs use the primary model, the primary depth rule and the expression floor per gene; each
  gene's mean expression is its mean log2 CPM over the retained donors, both groups pooled.
- B-10: with two or more brain banks among the eligible donors and no `batch_bank` column, bank is derived from
  `donors.csv`; with two or more chemistry versions named, a `batch_chemistry` column is required.
- B-11: a batch factor whose level is fixed by the level of another recorded factor is left out of the design, since
  its columns add nothing to that factor's and would make the design not full rank. Factors are taken prep factors
  first: in a one-to-one pair the prep factor stays, but a prep factor that a finer factor fixes (for example several
  sequencing runs per prep batch, each run within one prep batch) is the one left out. The header names, for each
  factor left out, the factor still in the model that fixes it; `batch_check.tsv` gives it a row (its Cramer's V
  cannot exceed that factor's). A blank level stops the run before this step, whether or not the factor would be left
  out.
- B-12: "certified" needs every brain bank that `donors.csv` gives the eligible donors with a BA9 sample to be named
  in the cohort sheet's `brain_banks` (a list, or one line separated by semicolons; compared ignoring case and
  spacing); a statement naming some banks covers only their donors. Chosen by the study team.

## Files
`run_g1a06_r1.py` (runner), `crosswalk.py`, `simulate.py` (made-up cohorts), `reference/` (crosswalk reference: gene
order per cell type, derived from Pineda et al. 2024), `designs/` (the invented 35-per-group design of the positive
control), `params/`, `work/g1a06_nullsim_v4/` (the analysis and null
simulation code), `work/dl23e_values/` (simulation parameters), `environment.txt`, `MANIFEST.sha256`.
