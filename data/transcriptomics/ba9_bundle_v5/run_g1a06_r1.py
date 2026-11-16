"""G1A06 R1 run bundle: the runner a data holder executes, unchanged, on their own machine.

It runs the frozen G1A06 replication test of 14 BA9 gene-by-cell-type results (frozen spec
coordinator/G1A06_REPLICATION_SPEC_FROZEN_2026-10-23.md, md5 5bbc2a9994dc1f642708f01a2699f9c3, as amended by the
dated deviation log, entries DL-01 to DL-27) in the locked order of DL-10, in one invocation with no human step:
  (i)   eligibility on metadata only (section 2, DL-16, DL-22);
  (ii)  the code, crosswalk and QC rules are those of this bundle, fixed by its hash (MANIFEST.sha256, checked here);
  (iii) locked preprocessing: crosswalk [A6] (crosswalk.py), one summed pseudobulk per donor and D003 type
        (DL-08, DL-14), nuclei-weighted batch fractions (DL-18, DL-24), absence (DL-20), raw library sizes (DL-21),
        the depth rule and the [A4] floor (r1pipeline.py); then realized power (section 9, DL-13) and the null
        simulation on the realized design (nullsim.py, DL-23 and successors). A null-simulation STOP ends the run:
        no fit is made;
  (iv)  the confirmatory fit (r1pipeline.analyse_celltype, unchanged) and one-sided Holm over 14, then sensitivities
        that never decide, and descriptive summaries.
Only aggregate results are written to the results folder. Per-donor intermediates stay in the private folder.

r1pipeline.py and nullsim.py are the adopted v4 files (Entry DL-27 code), byte for byte. Bundle choices the rules do
not make are marked CHOICE B-n here and listed in README.md.
"""
import os
for _v in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import argparse
import csv
import hashlib
import json
import platform
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'work' / 'g1a06_nullsim_v4'))
import numpy as np
import scipy
from scipy import stats, optimize
import r1pipeline as rp
import nullsim as ns
import crosswalk as cw

BUNDLE = 'G1A06 R1 run bundle, version 5 (1 Nov 2026)'
SEED = 20261031                       # the master seed of the null simulation, fixed by the bundle hash (DL-23b)
GENES9 = ('BRSK2', 'KIFC2', 'MYO18A', 'DNAJB2', 'AP1G2', 'ZNF783', 'AGAP2', 'SNPH', 'MIB2')
SEOI = float(np.log2(1.5))            # section 8: 1.5x on the log2 scale
SD_INFLATE = 1.25                     # section 9: discovery SDs x 1.25 for realized power
POWER_LOW = 0.5                       # section 9: below 50% realized power is "underpowered"
                                      # CHOICE B-6: read at first-step power (alpha 0.025/14), the conservative reading
ALPHA_FIRST, ALPHA_LAST = rp.ALPHA / rp.M_FAMILY, rp.ALPHA    # DL-13: first-step and last-step bounds
COV_MIN_SHARE = 0.9                   # section 4 [A11]: PMI or RIN used only if recorded for >= 90% of donors
REFERENCE = HERE / 'reference' / 'd003_ba9_crosswalk_ranks.tsv'
# CHOICE B-1: nullsim reads the 14 discovery residual SDs from lines 49-62 of a power output; the bundle ships those 14
# lines verbatim, at the same line numbers, in a file of its own, md5-checked by nullsim.load_params as before.
RESID_SD = ('params/resid_sd_lines.out', 'edafa5172b807035d4996691687ea4f3')
ns.PARAM_FILES['resid_sd'] = RESID_SD
NE_CROSSWALK = 'not estimable (crosswalk): no cohort label maps to this D003 type'
ASSAYS = ('single-nucleus rna-seq', 'snrna-seq')   # section 1: snRNA-seq of nuclei, not whole-cell scRNA-seq
PREP_FACTORS = ('prep', 'isolation_date')        # section 5: a prep batch (or nuclei-isolation date) per library
V_WARN = 0.7                                     # DL-09: Cramer's V above 0.7 is a warning only
GENOME_FILE = 'counts_all_genes.csv'             # optional; addendum A2 (genome-wide outputs for the GC comparison, D1)


class Stop(Exception):
    pass


# ----------------------------------------------------------------------------------------------------------- input
def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = [{k.strip(): (v or '').strip() for k, v in r.items()} for r in csv.DictReader(f)]
    return rows


def manifest_check():
    """The bundle must be unchanged: every file in MANIFEST.sha256 has its listed SHA-256."""
    man = HERE / 'MANIFEST.sha256'
    if not man.exists():
        raise Stop('MANIFEST.sha256 missing: the bundle cannot show it is unchanged')
    bad = []
    for line in man.read_text().splitlines():
        h, rel = line.split(None, 1)
        p = HERE / rel.strip()
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != h:
            bad.append(rel.strip())
    if bad:
        raise Stop('bundle files changed or missing: ' + ', '.join(bad))
    return hashlib.sha256(man.read_bytes()).hexdigest()


def is_mayo_jacksonville(bank):
    b = bank.lower()
    return 'mayo' in b and 'jacksonville' in b


# ------------------------------------------------------------------------------------------------ (i) eligibility
def eligibility(donors, sheet):
    """Section 2 on metadata only. Returns ({donor: dict(arm, age, sex, unknown, pmi, rin)}, attrition rows)."""
    att = []
    keep = {}
    reasons = {}
    for d in donors:
        did, dx = d['donor'], d.get('diagnosis', '').lower()
        why = None
        if is_mayo_jacksonville(d.get('brain_bank', '')):
            why = 'brain bank is Mayo Clinic Jacksonville (D003 bank; section 2.1)'
        elif dx == 'als':
            if d.get('sporadic_label', '').lower() != 'yes':
                why = 'ALS without an affirmative sporadic label (DL-16)'
            elif d.get('c9orf72', '').lower() == 'positive':
                why = 'known C9orf72 expansion carrier (section 2.2)'
            elif d.get('family_history', '').lower() == 'positive':
                why = 'known familial ALS (section 2.2)'
        elif dx == 'control':
            if d.get('neuropath_normal', '').lower() != 'yes':
                why = 'control not recorded as neuropathologically normal ([A10])'
        else:
            why = 'diagnosis neither ALS nor control (section 3)'
        if why is None:
            try:
                age = float(d['age'])
            except (KeyError, ValueError):
                why = 'age at death missing (section 2.4)'
        if why is None and d.get('sex', '').upper() not in ('M', 'F'):
            why = 'sex missing (section 2.4)'
        arm = 1 if dx == 'als' else 0
        if why is None:
            unknown = arm == 1 and not (d.get('c9orf72', '').lower() == 'negative'
                                        and d.get('family_history', '').lower() == 'negative')   # blank is never negative
            def num(k):
                try:
                    return float(d.get(k, ''))
                except ValueError:
                    return float('nan')
            keep[did] = dict(arm=arm, age=age, sex=1 if d['sex'].upper() == 'M' else 0, unknown=unknown,
                             pmi=num('pmi'), rin=num('rin'))
        else:
            reasons.setdefault((why, 'sALS' if dx == 'als' else ('control' if dx == 'control' else 'other')), 0)
            reasons[(why, 'sALS' if dx == 'als' else ('control' if dx == 'control' else 'other'))] += 1
    att.append(dict(step='donors listed', sALS=sum(d.get('diagnosis', '').lower() == 'als' for d in donors),
                    control=sum(d.get('diagnosis', '').lower() == 'control' for d in donors),
                    other=sum(d.get('diagnosis', '').lower() not in ('als', 'control') for d in donors)))
    for (why, arm), n in sorted(reasons.items()):
        att.append(dict(step='excluded: ' + why, **{arm: n}))
    att.append(dict(step='eligible (section 2)', sALS=sum(v['arm'] == 1 for v in keep.values()),
                    control=sum(v['arm'] == 0 for v in keep.values()),
                    status_unknown_sALS=sum(v['unknown'] for v in keep.values())))
    return keep, att


def bank_key(b):
    """A bank name compared ignoring case and spacing (CHOICE B-12)."""
    return ' '.join(str(b).split()).lower()


def sheet_banks(sheet):
    """The cohort sheet's brain_banks as a list: a list as given, or one string split at semicolons, as the chemistry
    field is (Researcher's check of version 4, note B12-1)."""
    banks = sheet.get('brain_banks') or []
    return [str(b) for b in (banks if isinstance(banks, list) else str(banks).split(';'))]


def banks_not_named(sheet, donor_banks):
    """CHOICE B-12 (Researcher's check of version 3, R-2): the banks that donors.csv gives the eligible donors with a
    BA9 sample but the cohort sheet's brain_banks does not name (compared ignoring case and spacing; a blank bank is
    never named). Ricardo chose this rule, "Provisional unless all named" (card tap 1 Nov 2026 06:28:42Z). Returns a
    sorted list, '(blank)' for a blank bank."""
    named = {bank_key(b) for b in sheet_banks(sheet)} - {'', 'unknown', 'not stated', 'n/a', 'na'}
    return sorted({(str(b).strip() or '(blank)') for b in donor_banks if bank_key(b) not in named})


def independence_label(sheet, donor_banks=None):
    """DL-22 and addendum A3. 'Certified' only when the cohort sheet names the brain bank(s) and gives either the
    holder's written statement of no shared donors with D003 or a trusted crosswalk of donor IDs; otherwise
    'provisionally supported' (Researcher re-check of version 2, R-1: the bank is required for both bases). With
    donor_banks (the brain_bank values in donors.csv of the eligible donors with a BA9 sample), every one of them must
    be named, since a statement naming some banks covers only their donors (CHOICE B-12; Researcher's check of
    version 3, R-2). In the bundle model the project never compares donor IDs itself."""
    basis = str(sheet.get('independence_basis', '')).strip().lower()
    if sheet.get('any_donor_from_mayo_clinic_jacksonville', '').lower() not in ('no',):
        return 'not established: the cohort sheet does not state that no donor came from Mayo Clinic Jacksonville'
    banks = sheet_banks(sheet)
    named = any(str(b).strip() and str(b).strip().lower() not in ('unknown', 'not stated', 'n/a', 'na') for b in banks)
    if basis in ('source statement', 'trusted crosswalk') and named and donor_banks is not None \
            and banks_not_named(sheet, donor_banks):
        return ('provisionally supported (the cohort sheet\'s brain_banks does not name every brain bank that donors.csv '
                'gives the eligible donors with a BA9 sample, so the statement does not cover the whole cohort; '
                'DL-22, addendum A3; CHOICE B-12)')
    if basis == 'source statement' and named:
        return 'certified (written statement of no shared donors, naming the brain bank(s); addendum A3)'
    if basis == 'trusted crosswalk' and named:
        return 'certified (trusted crosswalk of donor IDs, as declared in the cohort sheet, naming the brain bank(s))'
    return ('provisionally supported (no qualifying statement naming the bank; donor IDs not compared by the project; '
            'DL-22)')


def assay_check(sheet):
    """Section 1: the cohort must be snRNA-seq of nuclei, not whole-cell scRNA-seq, and its kit/chemistry version is
    recorded. Returns an ineligibility verdict, or None."""
    if str(sheet.get('assay', '')).strip().lower() not in ASSAYS:
        return ('INELIGIBLE: the cohort sheet does not give single-nucleus RNA-seq of nuclei as the assay (section 1: '
                'same assay class as discovery)')
    if not str(sheet.get('chemistry', '')).strip():
        return 'INELIGIBLE: the kit/chemistry version is not recorded in the cohort sheet (section 1)'
    return None


def blank_batch_levels(samples, elig, factors):
    """Section 5: every BA9 sample of an eligible donor needs a level in every recorded batch factor. Checked over all
    recorded factors before CHOICE B-11, so that a blank is never taken as a level and a factor with unknown levels is
    never treated as nested (Researcher's check of version 3, B11-1). Returns the factors with a blank, sorted."""
    ba9 = [s for s in samples if s['donor'] in elig and s.get('region', '').upper().replace(' ', '') in ('BA9',)]
    return sorted({f for f in factors for s in ba9 if not str(s.get('batch_' + f, '')).strip()})


def absorbed_factors(samples, elig, factors):
    """CHOICE B-11 (found while testing the Researcher's N-1): a batch factor whose level is fixed by the level of one
    other recorded factor, over the BA9 samples of eligible donors (each level of the other holds one level of it; for
    example a bank, kit or isolation date nested within prep batches), is already in the model through that factor:
    each donor's fractions over its levels are sums of its fractions over the other factor's levels, so its columns
    add nothing, and the joint cells (DL-27 rule 2) and DL-17 (ii) are the same with or without it. Left in, its
    columns make the design not full rank, and DL-17 (i) would then make every test not estimable. It is left out and
    the run header says so; a factor with one level is left as it is. Called only after blank_batch_levels finds no
    blank. Order (Researcher's check of version 3, B11-3): factors are taken prep factors first, then the rest by name;
    walking that order from the end, a factor is left out when every level of a factor still kept holds a single level
    of it. So in a one-to-one pair (an isolation date with the prep batch) the prep factor stays, but a prep factor that
    a finer factor fixes (several sequencing runs per prep batch, each run within one prep batch) is the one left out,
    which leaves the model the same. Returns {absorbed factor: the factor that fixed its level when it was left out};
    kept_fixer follows a chain to the factor still in the model."""
    ba9 = [s for s in samples if s['donor'] in elig and s.get('region', '').upper().replace(' ', '') in ('BA9',)]
    order = [f for f in PREP_FACTORS if f in factors] + sorted(f for f in factors if f not in PREP_FACTORS)
    kept, out = list(order), {}
    for g in reversed(order):
        if len({s.get('batch_' + g, '') for s in ba9}) < 2:
            continue
        for f in kept:
            if f == g:
                continue
            lv = {}
            for s in ba9:
                lv.setdefault(s.get('batch_' + f, ''), set()).add(s.get('batch_' + g, ''))
            if all(len(v) == 1 for v in lv.values()):
                out[g] = f
                kept.remove(g)
                break
    return out


def kept_fixer(absorbed, g):
    """The factor still in the model that fixes the level of absorbed factor g (following a chain: the level of g is
    fixed by f, and that of f by h, so h fixes g)."""
    f = absorbed[g]
    while f in absorbed:
        f = absorbed[f]
    return f


def cramers_v(D, c):
    """DL-09: Cramer's V between arm and each recorded batch factor, over the donors retained by the primary depth rule,
    nuclei-weighted split-donor fractions as counts. A warning only: V above 0.7 is reported, and V at or below 0.7
    certifies nothing."""
    t = D.ct[c]
    arm = D.arm[t.idx]
    ret = rp.depth_rule(t.lib[None], t.present[None], rp.DEPTH_CUTOFFS['primary'])[0][0]
    out = []
    for f, F in zip(D.factors, t.F_nuc):
        tab = np.array([F[ret & (arm == k)].sum(0) for k in (0, 1)])
        tab = tab[:, tab.sum(0) > 0]
        if tab.shape[1] < 2 or (tab.sum(1) == 0).any():
            out.append(dict(cell_type=c, factor=f, levels_with_donors=int(tab.shape[1]), cramers_v='',
                            warning='V not defined (one level, or one arm absent)'))
            continue
        n = tab.sum()
        e = tab.sum(1)[:, None] * tab.sum(0)[None, :] / n
        v = float(np.sqrt(((tab - e) ** 2 / e).sum() / (n * (min(tab.shape) - 1))))
        out.append(dict(cell_type=c, factor=f, levels_with_donors=int(tab.shape[1]), cramers_v=v,
                        warning='V above 0.7: warning only (DL-09)' if v > V_WARN else ''))
    return out


# ------------------------------------------------------------------------------------------- (iii) preprocessing
def build_pseudobulk(elig, samples, counts, mapping, factors):
    """One summed pseudobulk per donor and D003 type, kept as fragments by batch-level combination (DL-08, DL-14,
    DL-18). Returns fragments {(donor, type, levels): dict(nuclei, lib, genes(9,))}, provenance counts."""
    smp = {}
    for s in samples:
        if s['donor'] in elig and s.get('region', '').upper().replace(' ', '') in ('BA9',):
            levels = tuple(s['batch_' + f] for f in factors)
            if any(v == '' for v in levels):
                raise Stop(f'a BA9 sample of an eligible donor has a blank batch level ({", ".join(factors)}): '
                           'every sample needs every recorded batch factor (section 5)')
            smp[s['sample']] = (s['donor'], levels)
    frag = {}
    unmapped_nuclei = 0
    for r in counts:
        if r['sample'] not in smp:
            continue
        typ = mapping.get(r['label'])
        if typ is None:
            unmapped_nuclei += float(r['nuclei'])
            continue
        donor, levels = smp[r['sample']]
        f = frag.setdefault((donor, typ, levels), dict(nuclei=0.0, lib=0.0, genes=np.zeros(len(GENES9))))
        f['nuclei'] += float(r['nuclei'])
        f['lib'] += float(r['total_counts'])
        f['genes'] += np.array([float(r[g]) for g in GENES9])
    return frag, dict(ba9_samples=len(smp), nuclei_in_unmapped_labels=unmapped_nuclei,
                      donors_with_ba9_sample=len({d for d, _ in smp.values()}))


def write_design(path, elig, frag, factors, anon):
    """The nullsim design table (its module docstring): one row per donor x type x fragment; no expression value. A
    tested type with no mapped label gets one zero row per eligible donor, so that the adopted preflight reports it."""
    rows = []
    for (donor, typ, levels), f in sorted(frag.items(), key=lambda kv: (anon[kv[0][0]], kv[0][1], kv[0][2])):
        e = elig[donor]
        rows.append([anon[donor], typ, e['arm'], repr(e['age']), e['sex'], repr(f['lib']), repr(f['nuclei'])] + list(levels))
    have = {typ for (_, typ, _) in frag}
    absent = [c for c in rp.CELL_TYPES if c not in have]
    for c in absent:
        lv = sorted({k[2] for k in frag})[0] if frag else tuple('none' for _ in factors)
        for donor in sorted(elig, key=lambda d: anon[d]):
            e = elig[donor]
            rows.append([anon[donor], c, e['arm'], repr(e['age']), e['sex'], '0.0', '0.0'] + list(lv))
    with open(path, 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['donor', 'cell_type', 'arm', 'age', 'sex', 'library_size', 'nuclei'] + ['batch_' + x for x in factors])
        w.writerows(rows)
    return absent


def donor_counts(D, frag, anon, c):
    """(n_c, 9) summed gene counts for type c's donors in Design order."""
    t = D.ct[c]
    out = np.zeros((t.n, len(GENES9)))
    for (donor, typ, _), f in frag.items():
        if typ == c:
            i = np.flatnonzero(D.donors_arr[t.idx] == anon[donor])
            out[i[0]] += f['genes']
    return out


def gene_cols(c):
    """Indices into GENES9 of type c's tests, in rp.TESTS_OF order."""
    return [GENES9.index(rp.TESTS[i][1]) for i in rp.TESTS_OF[c]]


# ------------------------------------------------------------------------------------------- the variant fitter
def fit(D, c, Ycounts, *, cutoff='primary', drop=(), extra=None, hc3=False, weights=None, floor='A4',
        formula='S1', present_mask=None, coding_F='nuc'):
    """One cell type's tests under one variant, with r1pipeline's primitives. Returns dict(state, beta, se, df, p,
    n1, n0, bits) per test (k,). The primary settings reproduce r1pipeline.analyse_celltype exactly (checked in run)."""
    t = D.ct[c]
    arm, age, sex = D.arm[t.idx], D.age[t.idx], t.sex
    signs = rp.SIGNS[rp.TESTS_OF[c]]
    k = len(signs)
    present = t.present.copy() if present_mask is None else (t.present & present_mask)
    if extra is not None:
        present &= np.isfinite(extra)
    F_list = t.F_nuc if coding_F == 'nuc' else t.F_cnt
    F_mix = None if coding_F == 'nuc' else t.F_nuc
    # CHOICE B-7: a sensitivity that excludes donors recomputes the depth median and the [A4] floor within its subset
    retained = rp.depth_rule(t.lib[None], present[None], rp.DEPTH_CUTOFFS[cutoff])[0][0]
    out = dict(state=np.full(k, rp.NE_BATCH), beta=np.full(k, np.nan), se=np.full(k, np.nan), df=0,
               p=np.ones(k), n1=int((retained & (arm == 1)).sum()), n0=int((retained & (arm == 0)).sum()), bits=0)
    Fl = [F[None] for F in F_list]
    mix_ok, cols = rp._batch_masks(arm[None], retained[None], Fl, ns.CODING,
                                   None if F_mix is None else [F[None] for F in F_mix])
    joint_ok = rp._half_in_mixed(arm[None], retained[None], t.F_joint[None], t.F_joint[None])[0]
    X = rp._design(arm[None], age[None], sex, retained[None], Fl, [cc[0] for cc in cols])[0]
    keepcols = [j for j in range(X.shape[1]) if not (('age' in drop and j == 2) or ('sex' in drop and j == 3))]
    X = X[:, keepcols]
    if extra is not None:
        ex = np.where(retained, extra, 0.0)
        exc = ex - ex[retained].mean() if retained.any() else ex
        X = np.concatenate([X, (exc * retained)[:, None]], axis=1)
    nret, p_ = int(retained.sum()), X.shape[1]
    bits = 0
    if np.linalg.matrix_rank(X) < p_:
        bits |= rp.BIT_RANK
    if not mix_ok[0]:
        bits |= rp.BIT_MIX
    if nret - p_ < rp.DF_MIN:
        bits |= rp.BIT_DF
    if not joint_ok[0]:
        bits |= rp.BIT_JOINT
    out['bits'], out['df'] = bits, nret - p_
    if bits:
        return out
    cnt = Ycounts
    if floor == 'A4':
        fok = rp.floor_test(cnt[None], t.lib[None], retained[None])[0][0]
    else:                                              # discovery floor: >= 10 observed counts in every retained donor
        fok = (cnt[retained] >= rp.FLOOR_MIN).all(0)
    if formula == 'S1':
        Y = rp.log2cpm(cnt, t.lib[:, None])
    else:                                              # discovery formula, only where every retained donor has a count
        with np.errstate(divide='ignore'):
            Y = np.log2(cnt / t.lib[:, None] * 1e6)
        fok = fok & (cnt[retained] >= 1).all(0)
    Xr, Yr = X[retained], Y[retained]
    for j in range(k):
        if not fok[j]:
            out['state'][j] = rp.NE_FLOOR
            continue
        if weights is not None:
            w = np.sqrt(weights[retained, j])
            Xw, Yw = Xr * w[:, None], Yr[:, j] * w
        else:
            Xw, Yw = Xr, Yr[:, j]
        XtX_inv = np.linalg.inv(Xw.T @ Xw)
        b = XtX_inv @ Xw.T @ Yw
        e = Yw - Xw @ b
        if hc3:
            h = np.einsum('ij,jk,ik->i', Xw, XtX_inv, Xw)
            meat = (Xw.T * (e / (1 - h)) ** 2) @ Xw
            V = XtX_inv @ meat @ XtX_inv
            se = np.sqrt(V[1, 1])
        else:
            se = np.sqrt((e @ e) / (nret - p_) * XtX_inv[1, 1])
        out['state'][j], out['beta'][j], out['se'][j] = rp.PERFORMED, b[1], se
        out['p'][j] = stats.t.sf(signs[j] * b[1] / se, nret - p_)
    return out


class GenomeSkip(Exception):
    """The optional genome-wide outputs cannot be made; the reason is reported and the primary is unaffected."""


def genome_pseudobulk(path, elig, samples, counts, mapping, D, anon, frag):
    """CHOICE B-9 (addendum A2). Per tested type, the donor x gene summed counts of the optional genome-wide file, in
    Design order, built exactly as the primary pseudobulk: BA9 samples of eligible donors, labels mapped by the
    crosswalk, summed per donor and type. The file must hold every (sample, label) row of counts.csv that enters a
    tested type's pseudobulk, once, and agree with counts.csv on any of the 9 tested genes it carries. Returns
    (genes, {type: (n_c, G) array})."""
    smp = {s['sample']: s['donor'] for s in samples
           if s['donor'] in elig and s.get('region', '').upper().replace(' ', '') in ('BA9',)}
    used = {(r['sample'], r['label']) for r in counts if r['sample'] in smp and mapping.get(r['label']) in rp.CELL_TYPES}
    pos = {c: {a: i for i, a in enumerate(D.donors_arr[D.ct[c].idx])} for c in rp.CELL_TYPES}
    with open(path, newline='', encoding='utf-8-sig') as f:
        rd = csv.reader(f)
        head = [h.strip() for h in next(rd)]
        if head[:2] != ['sample', 'label']:
            raise GenomeSkip('the first two columns of ' + GENOME_FILE + ' must be sample and label')
        genes = head[2:]
        if not genes or len(set(genes)) != len(genes) or any(not g for g in genes):
            raise GenomeSkip('gene columns are missing, blank or repeated in ' + GENOME_FILE)
        out = {c: np.zeros((D.ct[c].n, len(genes))) for c in rp.CELL_TYPES}
        seen = set()
        for row in rd:
            if not row:
                continue
            key = (row[0].strip(), row[1].strip())
            if key not in used:
                continue
            if key in seen:
                raise GenomeSkip('a sample and label pair appears twice in ' + GENOME_FILE)
            seen.add(key)
            if len(row) != len(head):
                raise GenomeSkip('a row of ' + GENOME_FILE + ' has the wrong number of fields')
            try:
                vals = np.array([float(v) for v in row[2:]])
            except ValueError:
                raise GenomeSkip('a count in ' + GENOME_FILE + ' is not a number')
            if not np.isfinite(vals).all() or (vals < 0).any():
                raise GenomeSkip('a count in ' + GENOME_FILE + ' is negative or not finite')
            c = mapping[key[1]]
            out[c][pos[c][anon[smp[key[0]]]]] += vals
    if used - seen:
        raise GenomeSkip(f'{len(used - seen)} sample and label pair(s) of counts.csv are missing from ' + GENOME_FILE)
    for c in rp.CELL_TYPES:
        dc = donor_counts(D, frag, anon, c)
        for gi, g in enumerate(GENES9):
            if g in genes and not np.array_equal(out[c][:, genes.index(g)], dc[:, gi]):
                raise GenomeSkip(GENOME_FILE + ' disagrees with counts.csv on a tested gene')
    return genes, out


def genome_fit(D, c, G):
    """The primary model (S1, primary depth rule, nuclei-weighted batch fractions, DL-17 design checks, [A4] floor per
    gene) for every gene of the genome-wide file in type c, as fit() does for the 9 tested genes. Returns None if the
    design is not estimable, else dict(df, n1, n0, floor_ok (G,), mean (G,), beta (G,), se (G,), t (G,)). mean is the
    gene's mean log2 CPM over the retained donors, arms pooled (for the expression deciles of addendum D1)."""
    t = D.ct[c]
    arm, age, sex = D.arm[t.idx], D.age[t.idx], t.sex
    retained = rp.depth_rule(t.lib[None], t.present[None], rp.DEPTH_CUTOFFS['primary'])[0][0]
    Fl = [F[None] for F in t.F_nuc]
    mix_ok, cols = rp._batch_masks(arm[None], retained[None], Fl, ns.CODING, None)
    joint_ok = rp._half_in_mixed(arm[None], retained[None], t.F_joint[None], t.F_joint[None])[0]
    X = rp._design(arm[None], age[None], sex, retained[None], Fl, [cc[0] for cc in cols])[0]
    nret, p_ = int(retained.sum()), X.shape[1]
    if np.linalg.matrix_rank(X) < p_ or not mix_ok[0] or nret - p_ < rp.DF_MIN or not joint_ok[0]:
        return None
    fok = rp.floor_test(G[None], t.lib[None], retained[None])[0][0]
    Y = rp.log2cpm(G, t.lib[:, None])
    Xr, Yr = X[retained], Y[retained]
    XtX_inv = np.linalg.inv(Xr.T @ Xr)
    b = XtX_inv @ Xr.T @ Yr
    e = Yr - Xr @ b
    se = np.sqrt((e * e).sum(0) / (nret - p_) * XtX_inv[1, 1])
    return dict(df=nret - p_, n1=int((retained & (arm == 1)).sum()), n0=int((retained & (arm == 0)).sum()),
                floor_ok=fok, mean=Yr.mean(0), beta=b[1], se=se, t=b[1] / se)


def genome_outputs(results, inp, elig, samples, counts, mapping, D, anon, frag, per_type, absent):
    """Addendum A2/D1: writes genomewide_summary.tsv and one genomewide_<type>.tsv per tested type. Never deciding:
    the GC percentile and the pattern readout are computed by the study team from these files after return."""
    path = inp / GENOME_FILE
    if not path.exists():
        write_tsv(results / 'genomewide_summary.tsv', [dict(note='not run: ' + GENOME_FILE + ' not supplied')])
        return 'not supplied'
    try:
        genes, G = genome_pseudobulk(path, elig, samples, counts, mapping, D, anon, frag)
    except GenomeSkip as e:
        write_tsv(results / 'genomewide_summary.tsv', [dict(note='not run: ' + str(e))])
        return 'not run: ' + str(e)
    rows = []
    for c in rp.CELL_TYPES:
        if c in absent:
            rows.append(dict(cell_type=c, state=NE_CROSSWALK))
            continue
        g = genome_fit(D, c, G[c])
        if g is None:
            rows.append(dict(cell_type=c, state='design not estimable (DL-17)'))
            continue
        for k, i in enumerate(rp.TESTS_OF[c]):          # internal check: the tested genes match the primary fit
            gene = rp.TESTS[i][1]
            if gene in genes and per_type[c]['state'][k] == rp.PERFORMED:
                j = genes.index(gene)
                if not (np.isclose(g['beta'][j], per_type[c]['beta'][k], rtol=1e-9, atol=1e-12)
                        and np.isclose(g['se'][j], per_type[c]['se'][k], rtol=1e-9, atol=1e-12)):
                    raise Stop(f'internal check failed: the genome-wide fit does not reproduce the primary in {c}')
        out = [dict(gene=gn, state='performed' if g['floor_ok'][j] else 'not estimable (floor: [A4])',
                    mean_log2cpm=g['mean'][j], estimate=g['beta'][j] if g['floor_ok'][j] else '',
                    se=g['se'][j] if g['floor_ok'][j] else '', t=g['t'][j] if g['floor_ok'][j] else '')
               for j, gn in enumerate(genes)]
        write_tsv(results / f'genomewide_{c}.tsv', out, ['gene', 'state', 'mean_log2cpm', 'estimate', 'se', 't'])
        rows.append(dict(cell_type=c, state='performed', genes_in_file=len(genes),
                         genes_above_floor=int(g['floor_ok'].sum()), df=g['df'], n_sALS=g['n1'], n_control=g['n0']))
    write_tsv(results / 'genomewide_summary.tsv', rows)
    return f'performed for {sum(r["state"] == "performed" for r in rows)} of {len(rp.CELL_TYPES)} tested types'


def assemble(per_type, absent):
    """14-test arrays from per-type fits, absent types not estimable (crosswalk)."""
    T = len(rp.TESTS)
    A = dict(state=np.full(T, -1), beta=np.full(T, np.nan), se=np.full(T, np.nan), df=np.zeros(T, int),
             p=np.ones(T), n1=np.zeros(T, int), n0=np.zeros(T, int), bits=np.zeros(T, int))
    for c, r in per_type.items():
        ti = rp.TESTS_OF[c]
        for key in ('state', 'beta', 'se', 'p'):
            A[key][ti] = r[key]
        for key in ('df', 'n1', 'n0', 'bits'):
            A[key][ti] = r[key]
    A['rejected'] = rp.holm_onesided(A['p'][None])[0]
    return A


STATE_WORDS = {rp.PERFORMED: 'performed', rp.NE_BATCH: 'not estimable (batch: DL-17)', rp.NE_FLOOR:
               'not estimable (floor: [A4])', -1: NE_CROSSWALK}


def bits_words(b):
    w = []
    if b & rp.BIT_RANK:
        w.append('design not full rank')
    if b & rp.BIT_MIX:
        w.append('fewer than half of an arm in batch levels holding both arms')
    if b & rp.BIT_DF:
        w.append('residual df below 10')
    if b & rp.BIT_JOINT:
        w.append('fewer than half of an arm in joint batch cells holding both arms')
    return '; '.join(w)


# ----------------------------------------------------------------------------------------------- realized power
def realized_power(D, c, sd):
    """Per test of type c: first-step and last-step power at 1.5x and the first-step MDE at 80%, from the realized
    retained design (primary depth rule) and discovery residual SDs x 1.25 (section 9; DL-13)."""
    t = D.ct[c]
    arm, age, sex = D.arm[t.idx], D.age[t.idx], t.sex
    retained = rp.depth_rule(t.lib[None], t.present[None], rp.DEPTH_CUTOFFS['primary'])[0][0]
    Fl = [F[None] for F in t.F_nuc]
    _, cols = rp._batch_masks(arm[None], retained[None], Fl, 'full')
    X = rp._design(arm[None], age[None], sex, retained[None], Fl, [cc[0] for cc in cols])[0][retained]
    df = X.shape[0] - X.shape[1]
    if df < 1 or np.linalg.matrix_rank(X) < X.shape[1]:
        return None
    v11 = float(np.linalg.inv(X.T @ X)[1, 1])
    out = []
    for i in rp.TESTS_OF[c]:
        s = SD_INFLATE * sd[i] * np.sqrt(v11)
        pw = {}
        for nm, a in (('first', ALPHA_FIRST), ('last', ALPHA_LAST)):
            tc = stats.t.isf(a, df)
            pw[nm] = float(stats.nct.sf(tc, df, SEOI / s))
        tc = stats.t.isf(ALPHA_FIRST, df)
        mde = optimize.brentq(lambda d: stats.nct.sf(tc, df, d / s) - 0.8, 1e-6, 50 * s + 10)
        out.append(dict(test=i, df=df, power_first_step=pw['first'], power_last_step=pw['last'],
                        mde80_first_step_log2=mde, mde80_first_step_fold=float(2 ** mde)))
    return out


# --------------------------------------------------------------------------------------------------------- run
def write_tsv(path, rows, cols=None):
    cols = cols or list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(cols)
        for r in rows:
            w.writerow([fmt(r.get(k, '')) for k in cols])


def fmt(v):
    if isinstance(v, (float, np.floating)):
        return 'NA' if not np.isfinite(v) else f'{float(v):.6g}'
    if isinstance(v, (np.integer,)):
        return str(int(v))
    if isinstance(v, (np.bool_,)):
        return str(bool(v))
    return str(v)


def run(inp, results, private, workers=1, skip_manifest=False, nullsim_runs=None, sensitivities=True):
    t0 = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    inp, results, private = Path(inp), Path(results), Path(private)
    results.mkdir(parents=True, exist_ok=False)
    private.mkdir(parents=True, exist_ok=False)
    header = dict(bundle=BUNDLE, start_utc=t0, seed=SEED, python=platform.python_version(), numpy=np.__version__,
                  scipy=scipy.__version__, workers=workers)
    header['manifest_sha256'] = 'NOT CHECKED (code test only)' if skip_manifest else manifest_check()
    sheet = json.loads((inp / 'cohort_sheet.json').read_text())
    donors, samples = (read_csv(inp / n) for n in ('donors.csv', 'samples.csv'))   # no expression read before the checks
    status = dict(stage='started')

    def finish(stage, verdict):
        status.update(stage=stage, verdict=verdict)
        header['end_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        header.update(status)
        (results / 'run_header.json').write_text(json.dumps(header, indent=1, default=fmt))
        privacy_check(results, donors, samples)
        return status

    # (i) eligibility
    elig, att = eligibility(donors, sheet)
    bank_of = {d['donor']: str(d.get('brain_bank', '')).strip() for d in donors}
    ba9_donors = {s['donor'] for s in samples
                  if s['donor'] in elig and s.get('region', '').upper().replace(' ', '') in ('BA9',)}
    banks_used = sorted({bank_of.get(d, '') for d in ba9_donors})
    header['independence'] = independence_label(sheet, banks_used)        # CHOICE B-12
    unnamed = banks_not_named(sheet, banks_used)
    if unnamed:
        header['brain_banks_not_named_in_sheet'] = unnamed
    header['cohort_sheet'] = {k: sheet.get(k) for k in ('cohort_name', 'region', 'brain_banks', 'sporadic_definition',
                              'c9orf72_testing', 'doublet_handling', 'independence_basis',
                              'any_donor_from_mayo_clinic_jacksonville', 'interleaving_statement',
                              'interleaving_judgement', 'assay', 'chemistry')}
    bad_assay = assay_check(sheet)
    if bad_assay:
        write_tsv(results / 'eligibility_attrition.tsv', att)
        return finish('eligibility', bad_assay)
    # section 5 [A7]: brain bank or site is a batch factor when a cohort pools sources, and so is the kit or chemistry
    # version when it varies (Researcher re-check of version 2, N-1). CHOICE B-10: with two or more banks among the
    # eligible donors that have a BA9 sample and no batch_bank column, the runner derives batch_bank from donors.csv;
    # with two or more chemistry versions named in the cohort sheet, a batch_chemistry column is required.
    if len(banks_used) > 1 and not any('batch_bank' in s for s in samples):
        if '' in banks_used:
            write_tsv(results / 'eligibility_attrition.tsv', att)
            return finish('eligibility', 'INELIGIBLE: brain_bank is blank for an eligible donor with a BA9 sample, so '
                          'whether the cohort pools banks cannot be assessed (section 5: bank or site is a batch factor)')
        for s in samples:
            s['batch_bank'] = bank_of.get(s['donor'], '')
        header['bank_factor'] = (f'batch_bank derived from donors.csv brain_bank: {len(banks_used)} banks among the '
                                 'eligible donors with a BA9 sample (section 5; CHOICE B-10)')
    chem = sheet.get('chemistry', '')
    chem = [str(x).strip() for x in (chem if isinstance(chem, list) else str(chem).split(';')) if str(x).strip()]
    if len(chem) > 1 and not any('batch_chemistry' in s for s in samples):
        write_tsv(results / 'eligibility_attrition.tsv', att)
        return finish('eligibility', 'INELIGIBLE: the cohort sheet names more than one kit/chemistry version and '
                      'samples.csv has no batch_chemistry column (section 5: kit or chemistry version is a batch factor)')
    factors = sorted({k[len('batch_'):] for s in samples for k in s if k.startswith('batch_')})
    if not any(f in PREP_FACTORS for f in factors):
        # section 5: a prep batch (or isolation date) per library; without one, only documented interleaved processing,
        # and whether a statement qualifies is the study team's judgement, recorded before any expression is read
        # (CHOICE B-5: the run stops here until that judgement is entered in the cohort sheet). This applies whether or
        # not other batch factors (sequencing run, bank, chemistry) are recorded (Researcher re-check, D-2a). The study
        # team logs the judgement it gives, dated, and compares the returned interleaving_judgement_used with it (D-2b).
        statement = str(sheet.get('interleaving_statement', '')).strip()
        judged = str(sheet.get('interleaving_judgement', '')).strip()
        if not statement:
            write_tsv(results / 'eligibility_attrition.tsv', att)
            return finish('eligibility', 'INELIGIBLE: no prep batch or nuclei-isolation date is recorded and the cohort '
                          'sheet gives no statement that cases and controls were processed interleaved (section 5)')
        if not judged.lower().startswith('qualifies'):
            write_tsv(results / 'eligibility_attrition.tsv', att)
            return finish('eligibility', 'STOPPED BEFORE ANY EXPRESSION WAS READ: no prep batch or nuclei-isolation date '
                          'is recorded; whether the interleaving statement qualifies is the study team\'s judgement '
                          '(section 5). Return this folder; rerun only after the study team gives its judgement, entered '
                          'as interleaving_judgement')
        header['interleaving_judgement_used'] = judged
    if header['independence'].startswith('not established'):
        write_tsv(results / 'eligibility_attrition.tsv', att)
        return finish('eligibility', 'INELIGIBLE: donor-level independence from D003 is not established (section 2.1)')
    blank = blank_batch_levels(samples, elig, factors)             # section 5; B11-1: before CHOICE B-11
    if blank:
        write_tsv(results / 'eligibility_attrition.tsv', att)
        return finish('eligibility', f'INELIGIBLE: a BA9 sample of an eligible donor has a blank level in a recorded '
                      f'batch factor ({", ".join(blank)}): every sample needs every recorded batch factor (section 5)')
    absorbed = absorbed_factors(samples, elig, factors)            # CHOICE B-11
    if absorbed:
        kept = {g: kept_fixer(absorbed, g) for g in absorbed}
        header['batch_factors_absorbed'] = {
            g: (f'level fixed by batch_{kept[g]}'
                + (f' (through batch_{f}, itself left out)' if f != kept[g] else '')
                + f': in the model through batch_{kept[g]} (CHOICE B-11)') for g, f in sorted(absorbed.items())}
        factors = [f for f in factors if f not in absorbed]

    # (iii) crosswalk
    ref = cw.load_reference(REFERENCE)
    with open(inp / 'label_profiles.csv', newline='', encoding='utf-8-sig') as f:
        rd = csv.reader(f)
        head = next(rd)
        prow = list(rd)
    labels = [r[0].strip() for r in prow]
    L = np.array([[float(x or 0) for x in r[1:]] for r in prow])
    xw = cw.crosswalk(ref, labels, [h.strip() for h in head[1:]], L,
                      excluded_labels=tuple(sheet.get('labels_doublet_or_low_quality', [])))
    write_tsv(results / 'crosswalk.tsv',
              [dict(label=x['label'], assigned=x['assigned'] or '', best=x['best'], runner_up=x['runner_up'],
                    margin=x['margin'], reason=x['reason'], **{'rho_' + k: v for k, v in x['rho'].items()})
               for x in xw['labels']])
    header['crosswalk'] = {k: xw[k] for k in ('possible', 'reason', 'n_features_reference', 'n_features_measured',
                                              'matched_by')}
    header['crosswalk']['r_min'], header['crosswalk']['delta'] = cw.R_MIN, cw.DELTA
    mapping = xw['mapping'] if xw['possible'] else {}

    counts = read_csv(inp / 'counts.csv')
    frag, prov = build_pseudobulk(elig, samples, counts, mapping, factors)
    ba9 = {s['donor'] for s in samples if s['donor'] in elig and s.get('region', '').upper().replace(' ', '') == 'BA9'}
    att.append(dict(step='eligible donors with a BA9 sample', sALS=sum(elig[d]['arm'] == 1 for d in ba9),
                    control=sum(elig[d]['arm'] == 0 for d in ba9)))
    withfrag = {k[0] for k in frag}
    att.append(dict(step='of these, with nuclei in a mapped label', sALS=sum(elig[d]['arm'] == 1 for d in withfrag),
                    control=sum(elig[d]['arm'] == 0 for d in withfrag)))
    header['provenance'] = prov
    write_tsv(results / 'eligibility_attrition.tsv', att)
    anon = {d: f'D{i + 1:04d}' for i, d in enumerate(sorted(elig))}
    design = private / 'design.tsv'
    absent_types = write_design(design, elig, frag, factors, anon)
    D = ns.Design(design)
    D.donors_arr = np.array(D.donors)
    P = ns.load_params(HERE)
    sd = P['resid_sd']

    # attrition by cell type, depth rule
    rows = []
    for c in rp.CELL_TYPES:
        t = D.ct[c]
        arm = D.arm[t.idx]
        ret = rp.depth_rule(t.lib[None], t.present[None], rp.DEPTH_CUTOFFS['primary'])[0][0]
        rows.append(dict(cell_type=c, mapped_labels=';'.join(sorted(l for l, ty in mapping.items() if ty == c)),
                         present_sALS=int((t.present & (arm == 1)).sum()), present_control=int((t.present & (arm == 0)).sum()),
                         retained_after_depth_sALS=int((ret & (arm == 1)).sum()),
                         retained_after_depth_control=int((ret & (arm == 0)).sum()),
                         nuclei_retained_sALS=float(t.nuc[ret & (arm == 1)].sum()),
                         nuclei_retained_control=float(t.nuc[ret & (arm == 0)].sum()),
                         split_donors=int(sum(((F > 0).sum(1) > 1)[ret].sum() for F in t.F_nuc)) if t.F_nuc else 0))
    write_tsv(results / 'attrition_by_celltype.tsv', rows)
    vrows = []                                                       # DL-09 warning, never deciding
    for c in rp.CELL_TYPES:
        vrows += cramers_v(D, c)
        for g in sorted(absorbed):                                   # B11-2: DL-09 assesses the original factors
            vrows.append(dict(cell_type=c, factor=g, levels_with_donors='', cramers_v='',
                              warning=f'absorbed (CHOICE B-11): its level is fixed by {kept_fixer(absorbed, g)}, so its '
                                      f'V is not above the V of {kept_fixer(absorbed, g)} in this cell type (merging '
                                      'levels cannot raise chi-square)'))
    write_tsv(results / 'batch_check.tsv', vrows if vrows else [dict(note='no batch factor recorded')])
    header['cramers_v_warnings'] = sum(bool(r.get('warning', '').startswith('V above')) for r in vrows)

    # realized power (before the fit, DL-10)
    pw_rows = []
    for c in rp.CELL_TYPES:
        if c in absent_types:
            for i in rp.TESTS_OF[c]:
                pw_rows.append(dict(cell_type=c, gene=rp.TESTS[i][1], note=NE_CROSSWALK))
            continue
        r = realized_power(D, c, sd)
        for i in rp.TESTS_OF[c]:
            if r is None:
                pw_rows.append(dict(cell_type=c, gene=rp.TESTS[i][1], note='design not estimable'))
                continue
            x = [q for q in r if q['test'] == i][0]
            pw_rows.append(dict(cell_type=c, gene=rp.TESTS[i][1], df=x['df'], power_first_step=x['power_first_step'],
                                power_last_step=x['power_last_step'],
                                underpowered=x['power_first_step'] < POWER_LOW,
                                mde80_first_step_fold=x['mde80_first_step_fold']))
    write_tsv(results / 'realized_power.tsv', pw_rows)

    # null simulation on the realized design (DL-23 ...), the adopted code; a STOP ends the run
    nsout = results / 'null_simulation'
    if nullsim_runs is None:
        # Researcher re-check S-7: the adopted code records the design path it is given in report.json; a path relative
        # to the folder the run started from keeps most of the holder's folder names out of the returned report
        try:
            dpath = os.path.relpath(design)
        except ValueError:                             # Windows: a different drive has no relative path
            dpath = str(design)
        code = ns.main(['--design', dpath, '--seed', str(SEED), '--out', str(nsout), '--workers', str(workers)])
    elif nullsim_runs == 0:                            # code tests only: the simulation is not run at all
        nsout.mkdir()
        (nsout / 'verdict.txt').write_text('SKIPPED (code test only, no verdict)\n')
        code = 0 if not ns.preflight(D) else 1
    else:                                              # code tests only: fewer runs cannot give a verdict
        code = nullsim_reduced(design, nsout, nullsim_runs, workers)
    verdict = (nsout / 'verdict.txt').read_text().splitlines()[0]
    header['null_simulation_verdict'] = verdict
    if code != 0:
        return finish('null simulation', 'STOPPED BEFORE THE FIT: ' + verdict)

    # (iv) the confirmatory fit: r1pipeline.analyse_celltype, unchanged
    per_type, cnts = {}, {}
    for c in rp.CELL_TYPES:
        if c in absent_types:
            continue
        t = D.ct[c]
        cnts[c] = donor_counts(D, frag, anon, c)[:, gene_cols(c)]
        r = rp.analyse_celltype(t.lib, t.present, D.arm[t.idx], D.age[t.idx], t.sex, t.F_nuc, rp.SIGNS[rp.TESTS_OF[c]],
                                counts=cnts[c][None], depth_cutoff=rp.DEPTH_CUTOFFS['primary'], F_joint=t.F_joint)
        mine = fit(D, c, cnts[c])
        same = (np.array_equal(r['state'][0], mine['state']) and np.allclose(r['beta'][0], mine['beta'], equal_nan=True,
                rtol=1e-9, atol=1e-12) and np.allclose(r['se'][0], mine['se'], equal_nan=True, rtol=1e-9, atol=1e-12))
        if not same:
            raise Stop(f'internal check failed: the variant fitter does not reproduce r1pipeline in {c}')
        per_type[c] = dict(state=r['state'][0], beta=r['beta'][0], se=r['se'][0], p=r['p'][0], df=int(r['df'][0]),
                           bits=int(r['bits'][0]), n1=mine['n1'], n0=mine['n0'])
    A = assemble(per_type, absent_types)
    write_tsv(results / 'primary.tsv', primary_rows(A, pw_rows))
    # addendum A2/D1 (CHOICE B-9): optional genome-wide outputs under the primary model, after the primary fit
    header['genomewide'] = genome_outputs(results, inp, elig, samples, counts, mapping, D, anon, frag, per_type,
                                          absent_types)

    if not sensitivities:                              # code tests only
        n_rep = int(A['rejected'].sum())
        return finish('complete (code test: no sensitivities)', f'COMPLETE: {n_rep} of 14 tests replicated')
    # sensitivities (never deciding)
    unk = np.array([elig_by_anon(elig, anon, d)['unknown'] for d in D.donors])
    variants = [('unadjusted (age and sex dropped; CHOICE B-4: batch kept)', dict(drop=('age', 'sex'))),
                ('depth cutoff one fifth [A5]', dict(cutoff='one_fifth')),
                ('no depth exclusion [A5]', dict(cutoff='none')),
                ('discovery floor (>=10 counts in every retained donor)', dict(floor='discovery')),
                ('discovery formula (log2 CPM without prior; every retained donor >= 1 count)', dict(formula='discovery')),
                ('HC3 standard errors (DL-15)', dict(hc3=True)),
                ('count-weighted split-donor fractions (DL-23b)', dict(coding_F='cnt'))]
    sens = []
    s4b_failed = 'S4b did not pass' in (nsout / 'verdict.txt').read_text()        # nullsim writes its notes there
    for name, kw in variants:
        vr = variant_rows(name, {c: fit(D, c, cnts[c], **kw) for c in cnts}, absent_types)
        if s4b_failed and kw.get('cutoff') == 'none':
            for r in vr:
                r['note'] = 'S4b did not pass: this no-exclusion sensitivity cannot be read as calibrated (v5 section 5)'
        sens += vr
    split_mask = {c: ~np.any([((F > 0).sum(1) > 1) for F in D.ct[c].F_nuc], axis=0) if D.ct[c].F_nuc
                  else np.ones(D.ct[c].n, bool) for c in cnts}
    sens += variant_rows('split donors excluded (DL-14)', {c: fit(D, c, cnts[c], present_mask=split_mask[c]) for c in cnts},
                         absent_types)
    sens += variant_rows('status-unknown sALS excluded ([A11] sensitivity)',
                         {c: fit(D, c, cnts[c], present_mask=~unk[D.ct[c].idx]) for c in cnts}, absent_types)
    for cov in ('pmi', 'rin'):                         # CHOICE B-8: PMI and RIN are each added alone, not together
        vals = np.array([elig_by_anon(elig, anon, d)[cov] for d in D.donors])
        share = float(np.isfinite(vals).mean()) if len(vals) else 0.0
        if share >= COV_MIN_SHARE:
            sens += variant_rows(f'{cov.upper()} added as a covariate ({share:.0%} recorded)',
                                 {c: fit(D, c, cnts[c], extra=vals[D.ct[c].idx]) for c in cnts}, absent_types)
        else:
            sens.append(dict(variant=f'{cov.upper()} added as a covariate', note=f'not run: recorded for {share:.0%} of '
                             'donors (needs 90%)'))
    wts = {}
    for c in cnts:                                     # CHOICE B-3, [A13]: w = 1 / (1/mu + 1/nuclei), mu arm-blind
        t = D.ct[c]
        ret = rp.depth_rule(t.lib[None], t.present[None], rp.DEPTH_CUTOFFS['primary'])[0][0]
        cpm = cnts[c][ret].sum(0) / max(t.lib[ret].sum(), 1.0)
        mu = np.maximum(t.lib[:, None] * cpm[None, :], 1e-9)
        wts[c] = 1.0 / (1.0 / mu + 1.0 / np.maximum(t.nuc[:, None], 1.0))
    sens += variant_rows('precision-weighted fit ([A13]; CHOICE B-3)', {c: fit(D, c, cnts[c], weights=wts[c]) for c in cnts},
                         absent_types)
    for nm, fn in (('ambient-RNA-corrected counts ([A13])', 'counts_ambient_corrected.csv'),
                   ('no doublet removal (DL-05)', 'counts_no_doublet_removal.csv')):
        if (inp / fn).exists():
            frag2, _ = build_pseudobulk(elig, samples, read_csv(inp / fn), mapping, factors)
            d2 = private / ('design_' + fn.replace('.csv', '.tsv'))
            write_design(d2, elig, frag2, factors, anon)
            D2 = ns.Design(d2)
            D2.donors_arr = np.array(D2.donors)
            fits = {c: fit(D2, c, donor_counts(D2, frag2, anon, c)[:, gene_cols(c)]) for c in cnts if c in D2.ct}
            sens += variant_rows(nm, fits, absent_types)
        else:
            sens.append(dict(variant=nm, note='not run: input not supplied'))
    write_tsv(results / 'sensitivities.tsv', sens)

    # descriptive
    desc = descriptive(D, elig, anon, cnts, absent_types)
    (results / 'descriptive.json').write_text(json.dumps(desc, indent=1, default=fmt))
    header['dl07_age_flag'] = desc.get('age_flag', '')
    n_rep = int(A['rejected'].sum())
    return finish('complete', f'COMPLETE: {n_rep} of 14 tests replicated under rule (a) (Holm-rejected, discovery '
                  f'sign); null simulation: {verdict.split(":")[0]}')


def elig_by_anon(elig, anon, a):
    for d, x in anon.items():
        if x == a:
            return elig[d]
    raise KeyError(a)


def intervals(A, i):
    b, se, df = A['beta'][i], A['se'][i], A['df'][i]
    s = rp.SIGNS[i]
    est = s * b
    q95 = stats.t.isf(0.025, df)
    qf = stats.t.isf(0.05 / rp.M_FAMILY / 2, df)                   # [A2]: 1 - 0.05/14, two-sided
    lo, hi = est - qf * se, est + qf * se
    pos = 'above' if lo > SEOI else ('below' if hi < SEOI else 'undetermined')
    return est, est - q95 * se, est + q95 * se, lo, hi, pos


def primary_rows(A, pw_rows):
    rows = []
    for i, (c, g, s) in enumerate(rp.TESTS):
        st = int(A['state'][i])
        r = dict(cell_type=c, gene=g, discovery_sign=s, state=STATE_WORDS[st])
        if st == rp.NE_BATCH:
            r['reason'] = bits_words(int(A['bits'][i]))
        r.update(n_sALS=A['n1'][i], n_control=A['n0'][i], df=A['df'][i])
        if st == rp.PERFORMED:
            est, l95, h95, lf, hf, pos = intervals(A, i)
            r.update(estimate_oriented_log2=est, fold_oriented=2 ** est, se=A['se'][i], t_oriented=est / A['se'][i],
                     p_one_sided=A['p'][i], holm_rejected=bool(A['rejected'][i]),
                     outcome=('replicated' if A['rejected'][i] else
                              ('tested, not replicated (discordant: opposite sign)' if est < 0 else 'tested, not replicated')),
                     ci95_low=l95, ci95_high=h95, ci_family_low=lf, ci_family_high=hf, seoi_position=pos)
        else:
            r['outcome'] = 'not estimable'
        pw = [q for q in pw_rows if q['cell_type'] == c and q['gene'] == g][0]
        r.update(power_first_step=pw.get('power_first_step', ''), power_last_step=pw.get('power_last_step', ''),
                 underpowered=pw.get('underpowered', ''), mde80_first_step_fold=pw.get('mde80_first_step_fold', ''))
        rows.append(r)
    return rows


def variant_rows(name, per_type, absent):
    A = assemble(per_type, absent)
    rows = []
    for i, (c, g, s) in enumerate(rp.TESTS):
        st = int(A['state'][i])
        r = dict(variant=name, cell_type=c, gene=g, state=STATE_WORDS[st], n_sALS=A['n1'][i], n_control=A['n0'][i],
                 df=A['df'][i])
        if st == rp.PERFORMED:
            r.update(estimate_oriented_log2=s * A['beta'][i], se=A['se'][i], p_one_sided=A['p'][i],
                     holm_rejected_in_variant=bool(A['rejected'][i]))
        rows.append(r)
    return rows


def descriptive(D, elig, anon, cnts, absent):
    ages = {a: np.array([e['age'] for e in elig.values() if e['arm'] == a]) for a in (0, 1)}
    q = {('sALS' if a else 'control'): [float(np.percentile(v, x)) for x in (25, 50, 75)] if len(v) else []
         for a, v in ages.items()}
    overlap = bool(q['sALS'] and q['control'] and not (q['sALS'][2] < q['control'][0] or q['control'][2] < q['sALS'][0]))
    out = dict(age_quartiles_by_arm=q, middle_50pct_age_ranges_overlap=overlap,
               age_flag='' if overlap else 'limited overlap (DL-07)',
               sex_by_arm={('sALS' if a else 'control'): dict(male=sum(e['sex'] == 1 for e in elig.values() if e['arm'] == a),
                                                               female=sum(e['sex'] == 0 for e in elig.values() if e['arm'] == a))
                           for a in (0, 1)})
    strat = []
    for sx, nm in ((1, 'male'), (0, 'female')):
        per = {}
        for c in cnts:
            t = D.ct[c]
            per[c] = fit(D, c, cnts[c], drop=('sex',), present_mask=(t.sex == sx))
        for r in variant_rows(f'{nm} donors only (descriptive)', per, absent):
            strat.append({k: r.get(k) for k in ('variant', 'cell_type', 'gene', 'state', 'n_sALS', 'n_control',
                                                'estimate_oriented_log2', 'se')})
    out['sex_stratified'] = strat
    return out


def positive_control(out, workers=1, nruns=5000):
    """Frozen section 10.2 as defined by DL-27 rule 6: S1's generator, the realized labels and a planted arm effect of
    log2 1.5 on every test in its discovery direction, on the made-up design of 35 donors per arm with no batch factor
    (designs/design_P35.tsv: invented, from the project's null-simulation code tests, md5 e7f8578a70a7a4c59bd13de7395d1051),
    over 5,000 runs. Recovered means each of the 14 tests, and all 14 together, rejected by one-sided Holm at 0.025 in
    at least 80% of runs. Uses the adopted null-simulation code unchanged."""
    path = HERE / 'designs' / 'design_P35.tsv'
    if hashlib.md5(path.read_bytes()).hexdigest() != 'e7f8578a70a7a4c59bd13de7395d1051':
        raise Stop('designs/design_P35.tsv changed')
    D = ns.Design(path)
    P = ns.load_params()
    acc = ns.run_jobs(D, P, [('S1', 0)], SEED, workers=workers, nruns=nruns, planted=float(np.log2(1.5)))[('S1', 0)]
    per = np.asarray(acc['holm']) / acc['n']
    all14 = acc['all14'] / acc['n']
    ok = bool(per.min() >= 0.8 and all14 >= 0.8)
    rep = dict(rule='DL-27 rule 6 (frozen section 10.2): S1 generator, realized labels, planted log2 1.5 in the discovery '
                    'direction, design_P35 (35 per arm, no batch factor), 5,000 runs; each test and all 14 together '
                    'rejected by one-sided Holm at 0.025 in at least 80% of runs',
               runs=int(acc['n']), seed=SEED,
               per_test=[dict(cell_type=c, gene=g, holm_rejection_rate=round(float(r), 4))
                         for (c, g, s), r in zip(rp.TESTS, per)],
               all_14=round(float(all14), 4), passed=ok)
    Path(out).mkdir(parents=True, exist_ok=True)
    (Path(out) / 'positive_control_rule6.json').write_text(json.dumps(rep, indent=1))
    return rep


def privacy_check(results, donors, samples):
    """No donor or sample identifier (four characters or longer) may appear in any results file."""
    ids = {d['donor'] for d in donors if len(d['donor']) >= 4} | {s['sample'] for s in samples if len(s['sample']) >= 4}
    for p in results.rglob('*'):
        if p.is_file():
            txt = p.read_text(errors='ignore')
            hit = [x for x in ids if x in txt]
            if hit:
                bad = results.parent / (results.name + '_WITHHELD_privacy_check_failed')
                results.rename(bad)
                raise Stop(f'privacy check failed: {len(hit)} identifier(s) found in {p.name}; results moved to {bad}')


def nullsim_reduced(design, out, nruns, workers):
    """Code tests only: the adopted null simulation with every scenario at nruns runs. It cannot give a verdict
    (DL-26 fixes the run counts), so its PASS/STOP is labelled REDUCED."""
    out.mkdir(parents=True)
    D = ns.Design(design)
    absent = ns.preflight(D)
    if absent:
        (out / 'verdict.txt').write_text('STOP (preflight, reduced code-test run): ' + '; '.join(absent) + '\n')
        return 1
    P = ns.load_params(HERE)
    jobs = [(nm, lab) for nm in ns.SCENARIOS for lab in (0, 1)]
    acc = ns.run_jobs(D, P, jobs, SEED, workers=workers, nruns=nruns)
    res = {f'{nm}|{ns.LABELS[lab]}': ns.evaluate(acc[(nm, lab)], ns.SCENARIOS[nm]['gating']) for nm, lab in jobs}
    fam = max(v['family']['rate'] for v in res.values() if v['gating'])
    (out / 'verdict.txt').write_text(f'REDUCED ({nruns} runs per scenario, code test only, no verdict): highest '
                                     f'gating family rate {fam:.4f}\n')
    (out / 'report.json').write_text(json.dumps(res, indent=1, default=ns._json))
    return 0


def features(out):
    ref = cw.load_reference(REFERENCE)
    with open(out, 'w') as f:
        f.write('ensembl\tsymbol\n')
        for e, s in zip(ref['ensembl'], ref['symbol']):
            f.write(f'{e}\t{s}\n')
    print(f'{len(ref["ensembl"])} feature genes written to {out}')


def main(argv=None):
    ap = argparse.ArgumentParser(description=BUNDLE)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a1 = sub.add_parser('features', help='write the crosswalk feature genes to export label profiles for')
    a1.add_argument('--out', required=True)
    a2 = sub.add_parser('run', help='run the frozen test on a cohort')
    a2.add_argument('--input', required=True)
    a2.add_argument('--results', required=True)
    a2.add_argument('--private', required=True, help='folder for per-donor intermediates; never returned')
    a2.add_argument('--workers', type=int, default=1)
    a3 = sub.add_parser('selftest', help='the positive control (frozen section 10.2 as defined by DL-27 rule 6), then an '
                        'end-to-end run on a made-up cohort (35 donors per arm, the same ages in both arms, a planted 1.5x '
                        'effect in all 14 tests) with the full null simulation')
    a3.add_argument('--dir', required=True, help='a new folder for the made-up input, results and private files')
    a3.add_argument('--workers', type=int, default=1)
    a = ap.parse_args(argv)
    if a.cmd == 'features':
        features(a.out)
        return 0
    try:
        if a.cmd == 'selftest':
            import simulate
            d = Path(a.dir)
            manifest_check()
            pc = positive_control(d / 'positive_control', workers=a.workers)
            print('POSITIVE CONTROL (DL-27 rule 6):', 'RECOVERED' if pc['passed'] else 'NOT RECOVERED',
                  f"(lowest per-test rate {min(x['holm_rejection_rate'] for x in pc['per_test']):.3f}; all 14 {pc['all_14']:.3f})")
            simulate.make(d / 'input', n_per_arm=35, fold=1.5, seed=SEED, age_matched=True, n_extra_genes=2000)
            st = run(d / 'input', d / 'results', d / 'private', workers=a.workers)
            print('END-TO-END RUN ON A MADE-UP COHORT:', st['verdict'])
            return 0
        st = run(a.input, a.results, a.private, workers=a.workers)
    except Stop as e:
        print('STOP:', e)
        return 2
    print(st['verdict'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
