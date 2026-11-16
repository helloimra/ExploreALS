"""G1A06 null simulation: DL-23 as set by DL-23b v5 and amended by DL-23c, DL-23d, DL-23e and the draft DL-27, with the
DL-23e values.

Governing texts (md5 at 22:10Z on 25 Oct 2026, unchanged since 5a; the DL-27 draft's md5 is in test/TEST_LOG.md):
  DL-23b v5  coordinator/DL23b_NULL_SIMULATION_DGM_DRAFT_V5_2026-10-24.md           95e5cbb5de10f0fcb82d775b2eb22922
  DL-23c v3  coordinator/DL23c_S2_NEAR_FLOOR_LEVEL_DRAFT_V3_2026-10-25.md           c7b8eb5a8c4758261c773f983f01e847
  DL-23d v3  coordinator/DL23d_S7_NEAR_FLOOR_HIGH_DISPERSION_DRAFT_V3_2026-10-25.md e0b845b6b0f04adc55bf5298056640d0
  DL-23e v3  coordinator/DL23e_DISPERSION_DEFINITION_DRAFT_V3_2026-10-25.md        8fe7a2ead7d82b6ce6bc10f01cb9fa4e
  log        coordinator/G1A06_DEVIATION_LOG_2026-10-23.md (DL-17 to DL-26, DL-23b to DL-23e, DL-23e values)
                                                                                      370e67e859848b2ce900a8ad705e3af7
  DL-27      coordinator/DL27_NULLSIM_RULE_AMENDMENTS_DRAFT_2026-10-25.md (a working name; not logged, not in force)
The analysis is r1pipeline.py (this folder), run unchanged on every simulated data set (v5 section 2.8).

Input: one design table, one row per donor x cell type x fragment, a fragment being the part of a donor-celltype
pseudobulk that sits in one combination of batch levels (an unsplit donor is one fragment). Columns: donor, cell_type,
arm (1 = sALS, 0 = control), age, sex (1 = male, 0 = female), library_size, nuclei, and one batch_<factor> column per
batch factor, levels already merged. At the run of record it is the realized eligible design, read mechanically after
DL-10 step (iii) (v5 section 4); until a cohort exists only made-up designs are used. The gene-level parameters are the
logged discovery values, read below against their md5s; no gene-level value is read from a cohort (v5 section 4 [G3]).

Choices the rules do not make are marked CHOICE C-n, here and in r1pipeline.py, and listed in
coordinator/NULLSIM_CODE_RESULT_2026-10-25.md; those the DL-27 draft decides are marked with its rule.
Draft code for DL-27, which Ricardo adopted as a basis on 25 Oct 2026 22:01:13Z ("Adopt all eight"): a copy of
work/g1a06_nullsim/nullsim.py (md5 2948c7cefd2b4747866062c77a29addd) with those changes. Written and tested on made-up
data only, 25 Oct 2026. Not in force until Ricardo freezes DL-27.

v3, 26 Oct 2026: a copy of work/g1a06_nullsim_v2/nullsim.py (md5 116f1861d6e21fe78b360a036b48fd10) with the two bounded
fixes asked for in CODEX-20261026-014 and nothing else; r1pipeline.py is v2's, unchanged. Codex F1 (its finding, not
the code check's F1): a scenario named twice in --jobs, or a (scenario, label scheme) job given twice to run_jobs, is
refused before anything is scheduled (main, run_jobs). Codex F2: a tested cell type with rows but no present
pseudobulk stops the run at a preflight, before any parameter is read or any run is drawn (preflight, _stop_report,
main, run_jobs). Tested on invented data only (test/test_v3_fixes.py). v2's test logs and its A/B outputs were made by
v2 and do not test these changes.

v4, 26 Oct 2026: a copy of work/g1a06_nullsim_v3/nullsim.py (md5 ccb0fba462fcffd5f2bdc541936d7596) with the two items
the deviation log's Entry DL-27 sets before any run, and nothing else; r1pipeline.py is v3's, unchanged. First item:
the preflight also stops a tested cell type with exactly one present pseudobulk, whose tests can never be performed
(DL-17) and whose S4 and S4b runs failed with an error in v2 and v3 (preflight, PreflightStop, _stop_report). Second
item, N-1: preflight's docstring states the condition after each donor's fragments are summed, in Codex's wording.
Tested on invented data only (test/test_v4_fixes.py).
"""
import os
for _v in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ.setdefault(_v, '1')                  # one BLAS thread per process: the work is many small fits
import argparse
import csv
import hashlib
import json
import platform
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                       # python -I leaves the script's own folder off sys.path
import numpy as np
import scipy
from scipy import stats
import r1pipeline as rp

ROOT = HERE.parents[1]                              # the sals-discovery folder

# The logged discovery values (DL-23e values entry, 25 Oct 12:14:22Z) and the discovery residual SDs (v5 section 3).
PARAM_FILES = {
    'values': ('work/dl23e_values/coordinator/values.tsv', '04088d987c8031e9eec13eb16ccd6926'),
    'values_S3': ('work/dl23e_values/coordinator/values_S3.tsv', 'a3e3cd7f15a46c195b2e10ec1dc540e2'),
    'resid_sd': ('scratchpad/g1a06_power/g1a06_power.out', 'e0733e65e9c49801f87768e87d25071c'),   # lines 49-62
}
BATCH_SD = 0.25                  # v5 2.2, DL-27 rule 7: per factor's level draws (S5, one factor, is also run at 0.50)
BETA1, BETA2 = 0.10, 0.10        # v5 2.2: log2 a(age) = BETA1 z + BETA2 z^2
SEX_LOG2 = 0.10                  # v5 2.2: log2 multiplier for the realized cohort's minority sex
S4_SHRINK, S4B_SHRINK = 0.11, 0.02   # v5 section 5, S4 and S4b
S6_GAP = 10.3                    # v5 section 5, S6: control mean age minus sALS mean age, years
BOUND_TEST, BOUND_FAMILY = 0.035, 0.030   # DL-25, DL-26
MIN_PERFORMED = 10000            # v5 6.2-6.3
CHUNK = 2500                     # CHOICE C-18: runs per random stream
CODING = 'full'                  # DL-27 rule 1: batch per factor (r1pipeline._batch_masks)
BITGEN = 'PCG64'
LABELS = {0: 'realized', 1: 'permuted'}   # v5 2.4: the realized labels are primary, free permutation secondary; both gate


def _sc(sid, runs, gating=True, kind='counts', level=None, phi='own', shrink=None, cutoff='primary',
        batch_sd=BATCH_SD, s5=False, s6=False, beta2=BETA2, weights='nuclei'):
    return dict(sid=sid, runs=runs, gating=gating, kind=kind, level=level, phi=phi, shrink=shrink, cutoff=cutoff,
                batch_sd=batch_sd, s5=s5, s6=s6, beta2=beta2, weights=weights)


# sid is the scenario's fixed stream number (CHOICE C-18). Run counts: v5 section 5 and DL-26 (25,000); DL-23c rule 5
# and DL-23d (50,000 for S2, S4 and S7 at E = 10).
SCENARIOS = {
    'S1': _sc(1, 25000),
    'S1_count_weighted': _sc(2, 25000, weights='count'),                        # v5 6 [G2], [R3]: a fail stops
    'S2_E10': _sc(3, 50000, level=10.0),                                        # DL-23c rules 1-3
    'S2_E15': _sc(4, 25000, level=15.0),
    'S3': _sc(5, 25000, phi='S3'),                                              # DL-23e rule 6
    'S4_E10': _sc(6, 50000, level=10.0, shrink=S4_SHRINK),                      # v5 5 [D3]; DL-23c rule 4
    'S4_E15': _sc(7, 25000, level=15.0, shrink=S4_SHRINK),
    'S5_sd025': _sc(8, 25000, s5=True),                                         # v5 5 and 2.2 [R1]
    'S5_sd050': _sc(9, 25000, s5=True, batch_sd=0.50),
    'S6': _sc(10, 25000, s6=True),                                              # v5 5 [R4]
    'S7_E10': _sc(11, 50000, level=10.0, phi='S3'),                             # DL-23d
    'S7_E15': _sc(12, 25000, level=15.0, phi='S3'),
    # reported, not gating
    'S4b_E10': _sc(13, 25000, gating=False, level=10.0, shrink=S4B_SHRINK, cutoff='none'),   # v5 5; CHOICE C-13
    'S4b_E15': _sc(14, 25000, gating=False, level=15.0, shrink=S4B_SHRINK, cutoff='none'),
    'S1_beta2_0': _sc(15, 25000, gating=False, beta2=0.0),                      # v5 2.2 control; CHOICE C-11
    'S6_beta2_0': _sc(16, 25000, gating=False, s6=True, beta2=0.0),
    'G_S1': _sc(17, 25000, gating=False, kind='gauss'),                         # v5 section 3; CHOICE C-12
    'G_S5_sd025': _sc(18, 25000, gating=False, kind='gauss', s5=True),
    'G_S5_sd050': _sc(19, 25000, gating=False, kind='gauss', s5=True, batch_sd=0.50),
    'G_S6': _sc(20, 25000, gating=False, kind='gauss', s6=True),
}

# DL-23b v5 section 7 as amended by DL-27 rule 8, in full (F1); its five paragraphs, character for character.
SECTION7 = '\n\n'.join((
    'A pass means: every required one-sided 95% upper confidence bound satisfied its prespecified operational cap under '
    'the listed generators, scenario variants and label schemes, using the reported unconditional and performed-run '
    'denominators. This does not establish nominal 0.025 calibration or validity for the real cohort. The scheduled '
    'runs are 50,000 for each of S2, S4 and S7 at E = 10 and 25,000 for each of the other nine gating variants, under '
    'each of the two label schemes: 24 gating jobs and 750,000 gating runs.',
    'A pass does not mean the procedure is calibrated for the real data. The real cohort\'s dependence structure, '
    'mean-variance relationship, cross-cell-type correlation and any batch effect not in the recorded factors are not '
    'reproduced by these generators, and no simulation chosen by the analyst can establish that they are. The bound is '
    'an operational tolerance, not evidence that the true family error rate is at most 0.025 — the point Codex '
    'raised and Ricardo adopted on 24 Oct 15:37:27Z as item 12 of coordinator/CODEX010_FEEDBACK_DISPOSITION_2026-10-24.md. '
    'Two nulls are distinct: the generators put no arm term in the counts, but the fitted linear model, which can be '
    'misspecified, need not then have a zero arm coefficient. The check tests the procedure\'s robustness to that gap, '
    'so a failure is neither evidence of a disease effect nor proof that the procedure is miscalibrated for the real '
    'data.',
    'An upper bound above its cap is an operational stop: it can reflect uncertainty even when the observed rate is '
    'below the cap. A check with fewer than 10,000 performed runs is reported as "not checked (too few performed runs to '
    'judge)": it stops the run, but it is not evidence of excess error.',
    'The batch structures are partly constructed. S5 replaces the design\'s batch factors with one constructed factor '
    'whose membership is drawn again in every run, and S6 draws the ages again in every run, so these two scenarios '
    'assess an averaged constructed design rather than the realized one; in every scenario the batch effects are drawn '
    'afresh in each run, independently for each factor and level. No scenario generates an effect specific to a joint '
    'batch cell: DL-17(ii) as amended checks the support of the joint cells but does not model such an effect. The '
    'Gaussian diagnostic applies the depth rule but not the floor, so it differs from the count path in which tests are '
    'analysed as well as in scale, and a contrast between the two cannot by itself isolate the effect of the transform.',
    'This limitation is to be quoted wherever the check is cited. It is the reason the check gates the run rather than '
    'certifying the result.'))
LIMITATION = 'DL-23b v5 section 7 as amended by DL-27 rule 8 (draft), quoted in full as it requires:\n\n' + SECTION7
STOP_TOO_FEW = 'not checked (too few performed runs to judge)'    # v5 6.3, DL-27 rule 8b: the label, not the behaviour


def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def load_params(root=ROOT):
    """The 14 logged phi_g and mu_g, S3's value and the 14 discovery residual SDs, in TESTS order, each file checked
    against its md5 before it is read."""
    path = {}
    for key, (rel, md5) in PARAM_FILES.items():
        path[key] = Path(root) / rel
        got = md5_file(path[key])
        if got != md5:
            raise SystemExit(f'STOP: {rel} has md5 {got}, expected {md5}')
    with open(path['values'], newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    if [(r['cell_type'], r['gene']) for r in rows] != [(c, g) for c, g, _ in rp.TESTS]:
        raise SystemExit('STOP: values.tsv is not in the order of r1pipeline.TESTS')
    with open(path['values_S3'], newline='') as f:
        s3 = {r['quantity']: r['value'] for r in csv.DictReader(f, delimiter='\t')}
    sd = {}
    for line in path['resid_sd'].read_text().splitlines()[48:62]:
        m = re.match(r'\s*(\S+)\s+(\S+)\s+residual SD ([0-9.]+)\s', line)
        sd[(m.group(2), m.group(1))] = float(m.group(3))
    if len(sd) != 14:
        raise SystemExit('STOP: residual SDs not found at lines 49-62')
    return dict(phi=np.array([float(r['phi_g']) for r in rows]), mu=np.array([float(r['mu_g']) for r in rows]),
                phi_s3=float(s3['S3']), resid_sd=np.array([sd[(c, g)] for c, g, _ in rp.TESTS]))


class CellType:
    pass


class Design:
    """The design table, read mechanically; nothing is chosen, tuned or selected here (v5 section 4). Rows for cell
    types that carry no test are not analysed, but their donors are part of the cohort: the donor roster, from which
    the age z, the minority sex, the free permutation and S6's ages are taken (C-9, C-10, C-6), holds every donor of
    every row (F8). DL-27 rule 4 (C-4): the table holds every eligible pseudobulk before the depth rule, and the
    pipeline applies the rule, as it will on the cohort. Per cell type it also builds each donor's nuclei-weighted
    fractions over the joint batch cells, one cell per combination of levels present (DL-27 rule 2)."""

    def __init__(self, path):
        self.path, self.md5 = str(path), md5_file(path)
        with open(path, newline='') as f:
            rows = list(csv.DictReader(f, delimiter='\t'))
        need = ['donor', 'cell_type', 'arm', 'age', 'sex', 'library_size', 'nuclei']
        lack = [c for c in need if c not in rows[0]]
        if lack:
            raise ValueError(f'design lacks columns {lack}')
        self.factors = [c[len('batch_'):] for c in rows[0] if c.startswith('batch_')]
        attr, donors = {}, []
        for r in rows:
            a = (int(r['arm']), float(r['age']), int(r['sex']))
            if r['donor'] not in attr:
                attr[r['donor']] = a
                donors.append(r['donor'])
            elif attr[r['donor']] != a:
                raise ValueError(f"donor {r['donor']}: arm, age or sex differ between rows")
        self.donors, self.n = donors, len(donors)
        self.arm = np.array([attr[d][0] for d in donors])
        self.age = np.array([attr[d][1] for d in donors], float)
        self.sex = np.array([attr[d][2] for d in donors])
        if not (set(self.arm) <= {0, 1} and set(self.sex) <= {0, 1}):
            raise ValueError('arm and sex must be coded 0/1')
        self.levels = {f: sorted({r['batch_' + f] for r in rows}) for f in self.factors}   # CHOICE C-19: sorted
        where = {d: i for i, d in enumerate(donors)}
        self.ct = {}
        for c in rp.CELL_TYPES:
            rc = [r for r in rows if r['cell_type'] == c]
            if not rc:
                raise ValueError(f'design has no rows for {c}')
            ids = sorted({where[r['donor']] for r in rc})
            loc = {d: i for i, d in enumerate(ids)}
            rc.sort(key=lambda r: loc[where[r['donor']]])
            t = CellType()
            t.idx, t.n = np.array(ids), len(ids)
            t.frag_donor = np.array([loc[where[r['donor']]] for r in rc])
            t.frag_lib = np.array([float(r['library_size']) for r in rc])
            t.frag_nuc = np.array([float(r['nuclei']) for r in rc])
            if (t.frag_lib < 0).any() or (t.frag_nuc < 0).any():
                raise ValueError(f'{c}: negative library size or nuclei')
            t.frag_level = np.array([[self.levels[f].index(r['batch_' + f]) for r in rc] for f in self.factors],
                                    int).reshape(len(self.factors), len(rc))
            t.A = (t.frag_donor[None, :] == np.arange(t.n)[:, None]).astype(float)   # DL-14: one summed pseudobulk
            t.lib, t.nuc = t.A @ t.frag_lib, t.A @ t.frag_nuc
            t.present = (t.nuc > 0) & (t.lib > 0)                                    # DL-20
            t.F_nuc, t.F_cnt = [], []
            for fi, f in enumerate(self.factors):
                onehot = (t.frag_level[fi][:, None] == np.arange(len(self.levels[f]))[None, :]).astype(float)
                with np.errstate(invalid='ignore', divide='ignore'):
                    t.F_nuc.append(np.nan_to_num((t.A * t.frag_nuc) @ onehot / t.nuc[:, None]))    # DL-18
                    t.F_cnt.append(np.nan_to_num((t.A * t.frag_lib) @ onehot / t.lib[:, None]))    # DL-27 rule 8a (C-8)
            cells = sorted({tuple(t.frag_level[:, j]) for j in range(len(rc))})                   # DL-27 rule 2
            onehot = (np.array([cells.index(tuple(t.frag_level[:, j])) for j in range(len(rc))])[:, None]
                      == np.arange(len(cells))[None, :]).astype(float)
            with np.errstate(invalid='ignore', divide='ignore'):
                t.F_joint = np.nan_to_num((t.A * t.frag_nuc) @ onehot / t.nuc[:, None])
            t.sex = self.sex[t.idx]
            self.ct[c] = t


class PreflightStop(Exception):
    """Codex F2 (v3): raised by run_jobs for a design that preflight() stops; .absent is preflight()'s result, which
    from v4 also holds a tested cell type with one present pseudobulk (the attribute keeps v3's name)."""

    def __init__(self, absent):
        self.absent = absent
        super().__init__('STOP (preflight): tested cell types with rows but fewer than two present pseudobulks: '
                         + '; '.join(f'{c} ({", ".join(g)})' for c, g in absent.items()))


def preflight(D):
    """Codex F2 (v3, CODEX-20261026-014), extended in v4 by Entry DL-27's first item: the tested cell types that have
    rows in the design but fewer than two present pseudobulks, each with its tests. With none, after summing each
    donor's fragments, every donor has zero nuclei or zero library, so no pseudobulk is present (DL-20; N-1, in Codex's
    wording): Design accepts such a type, but none of its donors can be retained, and the near-floor level (DL-23c
    rule 3) has no shallowest retained donor to set it. With one, no run can retain more than that donor, so the type
    is never estimable (DL-17); and in S4 and S4b, in a run that shrinks that donor, the shrinkage's fixed point is a
    library of 0 (shrunk_size) while the donor stays retained, so the near-floor level is 0/0 and the sampler is given
    NaN means, where v2 and v3 failed with an error and no report. Either way none of the type's tests can be
    performed. They are not estimable (DL-17), m stays 14, and each would be STOP_TOO_FEW in every job, which stops
    the run (v5 section 6 item 3; DL-27 rule 8b); so the run stops here, before any parameter is read or any run is
    drawn. With two present pseudobulks or more, the shrunk library is positive and the depth rule keeps at least the
    deepest, so the near-floor level always has a positive library to set it; a type that is still never estimable
    then runs, its tests are performed in no run, and 8b stops the run after the jobs, as in v3. Returns {cell type:
    [genes]}, empty when every tested cell type has two present pseudobulks or more."""
    return {c: [rp.TESTS[i][1] for i in rp.TESTS_OF[c]] for c in rp.CELL_TYPES if D.ct[c].present.sum() < 2}


def design_summary(D, P, cutoff='primary'):
    """Per cell type under the realized labels: donors present and retained by arm, split donors, DL-17 status (bit 8:
    DL-17(ii) on the joint batch cells, DL-27 rule 2), the donor-equivalents of each arm in joint cells holding both
    arms, and a diagnostic that gates nothing: under the realized labels the age and sex multipliers of v5 2.2 are the
    same in every run, so the part the model cannot fit (0.10 z^2) shifts the arm estimate by a fixed amount, the arm
    coefficient of their least-squares projection; it is given in log2 units and per test as a shift of the oriented t
    at the discovery residual SD."""
    z = zscore(D.age[None])[0]
    off = BETA1 * z + BETA2 * z ** 2 + SEX_LOG2 * (D.sex == minority_sex(D.sex))
    out = {}
    for c, t in D.ct.items():
        arm = D.arm[t.idx]
        r = rp.analyse_celltype(t.lib, t.present, arm, D.age[t.idx], t.sex, t.F_nuc, np.ones(1),
                                Y=np.zeros((1, t.n, 1)), depth_cutoff=rp.DEPTH_CUTOFFS[cutoff], F_joint=t.F_joint)
        ret = r['retained'][0]
        split = sum(int(((F > 0).sum(1) > 1)[ret].sum()) for F in t.F_nuc)
        _, _, mixed = rp._half_in_mixed(arm[None], ret[None], t.F_joint[None], t.F_joint[None])
        inmix = (t.F_joint * mixed[0][None, :]).sum(1)
        row = dict(present_sALS=int((t.present & (arm == 1)).sum()), present_control=int((t.present & (arm == 0)).sum()),
                   retained_sALS=int((ret & (arm == 1)).sum()), retained_control=int((ret & (arm == 0)).sum()),
                   split_donor_factor_pairs=split, dl17_failed_bits=int(r['bits'][0]), residual_df=int(r['df'][0]),
                   joint_cells=int(t.F_joint.shape[1]), joint_cells_both_arms=int(mixed[0].sum()),
                   in_joint_cells_both_arms_sALS=float((inmix * (ret & (arm == 1))).sum()),
                   in_joint_cells_both_arms_control=float((inmix * (ret & (arm == 0))).sum()))
        if r['bits'][0] == 0:
            Fl = [F[None] for F in t.F_nuc]
            _, cols = rp._batch_masks(arm[None], ret[None], Fl, CODING)
            X = rp._design(arm[None], D.age[t.idx][None], t.sex, ret[None], Fl, [cc[0] for cc in cols])[0][ret]
            bias = float(np.linalg.lstsq(X, off[t.idx][ret], rcond=None)[0][1])
            v11 = float(np.linalg.inv(X.T @ X)[1, 1])
            row['fixed_offset_arm_bias_log2'] = bias
            row['fixed_offset_oriented_t_shift'] = {rp.TESTS[i][1]: float(rp.SIGNS[i] * bias / (P['resid_sd'][i] * np.sqrt(v11)))
                                                    for i in rp.TESTS_OF[c]}
        out[c] = row
    return out


def make_rng(seed, sid, labels, chunk):
    """CHOICE C-18: one master seed; a scenario's chunk draws from SeedSequence(seed, spawn_key=(scenario sid, label
    scheme, chunk index)) through PCG64, so every result is fixed by the seed whatever the number of workers."""
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed, spawn_key=(sid, labels, chunk))))


def donor_counts(rng, mean, phi, frag_donor, n):
    """DL-27 rule 3: phi_g describes the donor total. Counts per fragment, mean `mean` (R, nf, k), sharing one gamma
    multiplier per donor and test (mean 1, variance phi, phi per test on the last axis; DL-23e: the dispersion of the
    variance mu + phi mu^2): each fragment is Poisson given its donor's multiplier, so a donor's total over its
    fragments is negative binomial with mean the sum of its fragments' means and dispersion phi, and each fragment is
    marginally negative binomial with the same phi. Poisson where phi = 0 (the multiplier is 1); a zero mean gives 0.
    frag_donor (nf,) maps the fragments to the n donors. Returns (R, nf, k)."""
    mean = np.asarray(mean, float)
    R, nf, k = mean.shape
    ph = np.broadcast_to(np.asarray(phi, float), (k,))
    g = np.ones((R, n, k))
    nb = np.flatnonzero(ph > 0)
    if nb.size:
        q = ph[nb]
        g[:, :, nb] = rng.gamma(1.0 / q, q, (R, n, nb.size))
    return rng.poisson(mean * g[:, frag_donor, :]).astype(float)


def minority_sex(sex):
    """CHOICE C-9: the realized cohort's minority sex; on a tie, male."""
    return 1 if (sex == 1).sum() <= (sex == 0).sum() else 0


def zscore(age):
    """CHOICE C-9: z over every donor of the cohort (the design's donors), SD with ddof = 1. age (R, n)."""
    sd = age.std(1, ddof=1, keepdims=True)
    if (sd == 0).any():
        raise ValueError('age has no spread')
    return (age - age.mean(1, keepdims=True)) / sd


def s6_ages(rng, D, arm):
    """v5 section 5 S6 [R4], DL-27 rule 5 (C-6). Arms, batch levels and library sizes stay as realized and age alone is
    re-assigned in every run: standard normal deviations, centred within arm and scaled, put the sALS arm exactly
    S6_GAP years below the control arm, keep the cohort's mean age, and give a pooled within-arm SD equal to the
    realized one. Under the free permutation the gap follows the permuted labels. arm (R, n) -> ages (R, n)."""
    n = D.n
    ss = sum(((D.age[D.arm == a] - D.age[D.arm == a].mean()) ** 2).sum() for a in (0, 1))
    sp = np.sqrt(ss / (n - 2))
    a1 = arm == 1
    n1 = a1.sum(1, keepdims=True)
    n0 = n - n1
    e = rng.standard_normal(arm.shape)
    e = e - np.where(a1, (e * a1).sum(1, keepdims=True) / n1, (e * ~a1).sum(1, keepdims=True) / n0)
    e = e * sp / np.sqrt((e ** 2).sum(1, keepdims=True) / (n - 2))
    m = D.age.mean()
    return np.where(a1, m - S6_GAP * n0 / n, m + S6_GAP * n1 / n) + e


def shrunk_size(lib, present, j, shrink):
    """v5 section 5 S4 [D3], CHOICE C-3: the library size that puts pseudobulk j at `shrink` x its cell type's median
    (DL-19: over present pseudobulks, arms pooled), the median being taken with j at its new size (a fixed point)."""
    lb = np.asarray(lib, float).copy()
    lb[j] = 0.0
    val = shrink * np.median(lb[present])
    for _ in range(100):
        lb[j] = val
        new = shrink * np.median(lb[present])
        if new == val:
            return val
        val = new
    raise RuntimeError('S4 fixed point not reached')


def s4_table(D, sc):
    """CHOICE C-2: one donor per run, drawn uniformly among the cohort's donors that the realized design retains (under
    the scenario's depth cutoff) in at least one tested cell type, and shrunk in every tested cell type that retains
    it; its fragments are scaled in proportion and its nuclei are unchanged (CHOICE C-3)."""
    cutoff = rp.DEPTH_CUTOFFS[sc['cutoff']]
    tab, elig = {}, np.zeros(D.n, bool)
    for c, t in D.ct.items():
        ret = rp.depth_rule(t.lib[None], t.present[None], cutoff)[0][0]
        shr = np.full(t.n, np.nan)
        for j in np.flatnonzero(ret):
            shr[j] = shrunk_size(t.lib, t.present, j, sc['shrink'])
        pos = np.full(D.n, -1)
        pos[t.idx] = np.arange(t.n)
        tab[c] = (ret, shr, pos)
        elig[t.idx[ret]] = True
    return np.flatnonzero(elig), tab


def s5_weights(rng, arm, retained):
    """v5 section 5 S5, CHOICE C-5. Per cell type and per run, after the labels: one batch factor replaces the
    design's, with levels M (both arms), A1 (sALS only) and A0 (controls only), at DL-17(ii)'s minimum. In each arm
    with n_a retained donors, floor((n_a - s_a) / 2) donors sit wholly in M, s_a donors (1 if n_a is odd, 2 if even)
    are split with half their nuclei and half their library in M and half in their arm's own level, and the rest sit
    wholly in their arm's own level, so exactly n_a / 2 donor-equivalents are in M. Which donors take which role is
    drawn uniformly within each arm in every run. Returns each donor's share in M (R, n); 1 for donors not retained."""
    w = np.ones(arm.shape)
    u = rng.random(arm.shape)
    for a in (0, 1):
        sel = retained & (arm == a)
        na = sel.sum(1, keepdims=True)
        sa = np.where(na % 2 == 1, 1, 2) * (na > 0)
        kf = (na - sa) // 2
        rank = np.argsort(np.argsort(np.where(sel, u, np.inf), axis=1), axis=1)
        w = np.where(sel, np.where(rank < kf, 1.0, np.where(rank < kf + sa, 0.5, 0.0)), w)
    return w


def s4_libs(t, c, s4, R):
    """One cell type's library sizes in each run, with the run's S4 donor at its shrunk size where the realized
    design retains it, and the factor that scales that donor's fragments. Returns lib (R, n_c) and scale or None."""
    lib = np.broadcast_to(t.lib, (R, t.n))
    if s4 is None:
        return lib, None
    pick, tab = s4
    ret0, shr, pos = tab[c]
    j = pos[pick]
    hit = j >= 0
    hit[hit] = ret0[j[hit]]
    rows = np.flatnonzero(hit)
    lib = lib.copy()
    lib[rows, j[rows]] = shr[j[rows]]
    scale = np.ones((R, t.n))
    scale[rows, j[rows]] = shr[j[rows]] / t.lib[j[rows]]
    return lib, scale


def _celltype(rng, D, P, c, sc, arm, age, l2ax, s4, phi, coding, p_mode, planted):
    """Generate one cell type's tests over R runs and analyse them. Returns the pipeline's output and zero flags."""
    t, ti = D.ct[c], rp.TESTS_OF[c]
    R, k = arm.shape[0], len(ti)
    sign = rp.SIGNS[ti]
    arm_c, age_c, l2ax_c = arm[:, t.idx], age[:, t.idx], l2ax[:, t.idx]
    cutoff = rp.DEPTH_CUTOFFS[sc['cutoff']]
    lib, scale = s4_libs(t, c, s4, R)
    present = np.broadcast_to(t.present, (R, t.n))
    retained = rp.depth_rule(lib, present, cutoff)[0]

    if sc['s5']:                                       # slot 0 sits in M, slot 1 in the donor's own arm level
        w = s5_weights(rng, arm_c, retained)
        fd = np.concatenate([np.arange(t.n), np.arange(t.n)])
        flib = lib[:, fd] * np.concatenate([w, 1.0 - w], axis=1)
        lvl = np.concatenate([np.zeros((R, t.n), int), np.where(arm_c == 1, 1, 2)], axis=1)
        lb = rng.normal(0.0, sc['batch_sd'], (R, k, 3))
        fl2b = np.take_along_axis(lb, np.broadcast_to(lvl[:, None, :], (R, k, 2 * t.n)), axis=2)
        F_list = [np.stack([w, (1.0 - w) * (arm_c == 1), (1.0 - w) * (arm_c == 0)], axis=2)]
        F_mix = F_joint = None                          # one factor: its levels are the joint cells (DL-27 rule 2)
        agg = np.concatenate([np.eye(t.n), np.eye(t.n)], axis=1)
    else:
        fd = t.frag_donor
        flib = np.broadcast_to(t.frag_lib, (R, len(fd))) if scale is None else t.frag_lib * scale[:, fd]
        fl2b = np.zeros((R, k, len(fd)))
        for fi, f in enumerate(D.factors):             # DL-27 rule 7 (C-7): per run, per test, per level of each factor
            lb = rng.normal(0.0, sc['batch_sd'], (R, k, len(D.levels[f])))
            fl2b = fl2b + lb[:, :, t.frag_level[fi]]
        F_list = t.F_cnt if sc['weights'] == 'count' else t.F_nuc
        F_mix = t.F_nuc if sc['weights'] == 'count' else None    # DL-27 rule 8a (C-8): DL-17(ii) stays nuclei-weighted
        F_joint = t.F_joint
        agg = t.A
    # expected count per unit rate, per fragment (R, nf, k): library x batch x age x sex (v5 2.1, 2.7)
    mult = flib[:, :, None] * np.exp2(np.swapaxes(fl2b, 1, 2) + l2ax_c[:, fd][:, :, None])
    if sc['level'] is None:
        mu = P['mu'][ti][None, :]
    else:                                              # DL-23c rule 3: mu = E / (s_min x m_bar), per run, per test
        rf = retained[:, fd]
        mbar = np.einsum('rf,rfk->rk', rf, mult) / (rf * flib).sum(1)[:, None]
        smin = np.where(retained, lib, np.inf).min(1)
        mu = sc['level'] / (smin[:, None] * mbar)
    eff = np.ones((R, len(fd), k)) if planted is None else np.exp2(planted * sign * arm_c[:, fd][:, :, None])

    if sc['kind'] == 'counts':
        counts = np.einsum('df,rfk->rdk', agg, donor_counts(rng, mu[:, None, :] * mult * eff, phi[ti], fd, t.n))
        out = rp.analyse_celltype(lib, present, arm_c, age_c, t.sex, F_list, sign, counts=counts, depth_cutoff=cutoff,
                                  coding=coding, p_mode=p_mode, F_mix=F_mix, F_joint=F_joint)
        zero = ((counts == 0) & out['retained'][..., None]).any(1)
    else:                                              # v5 section 3: Gaussian on the log2 CPM scale, no transform or floor
        bmix = np.einsum('df,rfk->rdk', agg, flib[:, :, None] * np.exp2(np.swapaxes(fl2b, 1, 2)))
        with np.errstate(invalid='ignore', divide='ignore'):
            bmix = np.where(lib[:, :, None] > 0, bmix / lib[:, :, None], 1.0)
        Y = (np.log2(mu * 1e6)[:, None, :] + np.log2(bmix) + l2ax_c[:, :, None]
             + rng.standard_normal((R, t.n, k)) * P['resid_sd'][ti])
        if planted is not None:
            Y = Y + planted * sign * arm_c[:, :, None]
        out = rp.analyse_celltype(lib, present, arm_c, age_c, t.sex, F_list, sign, Y=Y, depth_cutoff=cutoff,
                                  coding=coding, p_mode=p_mode, F_mix=F_mix, F_joint=F_joint)
        zero = np.zeros((R, k), bool)
    return out, zero


def prepare(rng, D, sc, labels, R):
    """The draws made once per run before the cell types: labels, S6 ages, the age and sex multipliers (v5 2.2) and
    the S4 donor. Returns arm, age, log2 of the age x sex multiplier (each (R, n)), the S4 table and the S4 donor's arm."""
    n = D.n
    arm = np.broadcast_to(D.arm, (R, n))
    if labels == 1:                                    # CHOICE C-10: free permutation of the cohort's donors
        arm = rng.permuted(arm, axis=1)
    age = s6_ages(rng, D, arm) if sc['s6'] else np.broadcast_to(D.age, (R, n))
    z = zscore(age)
    l2ax = BETA1 * z + sc['beta2'] * z ** 2 + SEX_LOG2 * (D.sex == minority_sex(D.sex))[None, :]
    s4 = s4_arm = None
    if sc['shrink'] is not None:
        elig, tab = s4_table(D, sc)
        pick = elig[rng.integers(0, len(elig), R)]
        s4, s4_arm = (pick, tab), arm[np.arange(R), pick]
    return arm, age, l2ax, s4, s4_arm


def run_chunk(D, P, name, labels, chunk, nruns, seed, coding=CODING, p_mode='onesided', planted=None):
    """nruns runs of one scenario under one label scheme, from the chunk's own stream. Order of draws: labels, ages
    (S6), the S4 donor, then per cell type in sorted order the S5 assignment, the batch normals, and the donors' gamma
    multipliers followed by the fragments' Poisson counts (DL-27 rule 3), or the Gaussian noise. `planted` (a log2 arm
    effect in the discovery direction), `coding` other than CODING and `p_mode` other than 'onesided' exist for the code
    tests only and are not reachable from the command line. The per-test event is the raw one-sided test at 0.025 in
    a run where the test was performed; the family event is at least one Holm rejection over the 14 (DL-27 rule 8a)."""
    sc = SCENARIOS[name]
    rng = make_rng(seed, sc['sid'], labels, chunk)
    R = nruns
    arm, age, l2ax, s4, s4_arm = prepare(rng, D, sc, labels, R)
    phi = np.full(len(rp.TESTS), P['phi_s3']) if sc['phi'] == 'S3' else P['phi']
    p = np.ones((R, len(rp.TESTS)))
    state = np.zeros((R, len(rp.TESTS)), int)
    zero = np.zeros((R, len(rp.TESTS)), bool)
    tor = np.full((R, len(rp.TESTS)), np.nan)          # oriented t (DL-12), for the report
    for c in rp.CELL_TYPES:
        ti = rp.TESTS_OF[c]
        out, zc = _celltype(rng, D, P, c, sc, arm, age, l2ax, s4, phi, coding, p_mode, planted)
        p[:, ti], state[:, ti], zero[:, ti] = out['p'], out['state'], zc
        with np.errstate(invalid='ignore', divide='ignore'):
            tor[:, ti] = out['beta'] / out['se'] * rp.SIGNS[ti]
    rej = rp.holm_onesided(p)
    perf = state == rp.PERFORMED
    fp = perf & (p <= rp.ALPHA)
    res = dict(n=R, performed=perf.sum(0), ne_batch=(state == rp.NE_BATCH).sum(0),
               ne_floor=(state == rp.NE_FLOOR).sum(0), fp=fp.sum(0), zero=zero.sum(0), holm=rej.sum(0),
               family=int(rej.any(1).sum()), all14=int(rej.all(1).sum()),
               t_sum=np.nansum(tor, 0), t_ss=np.nansum(tor ** 2, 0))
    if s4 is not None:
        for a in (0, 1):
            m = s4_arm == a
            res[f's4_arm{a}_n'], res[f's4_arm{a}_performed'], res[f's4_arm{a}_fp'] = int(m.sum()), perf[m].sum(0), fp[m].sum(0)
    return res


def chunk_sizes(nruns):
    return [CHUNK] * (nruns // CHUNK) + ([nruns % CHUNK] if nruns % CHUNK else [])


_G = {}


def _init(D, P):
    _G['D'], _G['P'] = D, P


def _task(args):
    name, labels, chunk, size, seed, kw = args
    t0 = time.process_time()
    res = run_chunk(_G['D'], _G['P'], name, labels, chunk, size, seed, **kw)
    res['cpu'] = time.process_time() - t0
    return name, labels, res


def _add(acc, res):
    if not acc:
        return {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in res.items()}
    for k, v in res.items():
        acc[k] = acc[k] + v
    return acc


def run_jobs(D, P, jobs, seed, workers=1, nruns=None, **kw):
    """jobs: list of (scenario name, label scheme). Returns {(name, labels): accumulated counts}. nruns overrides the
    scenarios' run counts (code tests only). Codex F1 (v3): a job given twice is refused before anything is
    scheduled, since its chunks would draw the same streams again (make_rng) and add them to the same counts as if
    they were new runs. Codex F2 (v3): so is a design that preflight() stops (PreflightStop)."""
    rep = sorted({job for job in jobs if jobs.count(job) > 1})
    if rep:
        raise ValueError(f'repeated jobs {rep}: each (scenario, label scheme) is run once')
    absent = preflight(D)
    if absent:
        raise PreflightStop(absent)
    tasks = [(name, lab, ci, size, seed, kw) for name, lab in jobs
             for ci, size in enumerate(chunk_sizes(SCENARIOS[name]['runs'] if nruns is None else nruns))]
    acc = {job: {} for job in jobs}
    if workers <= 1:
        _init(D, P)
        for tk in tasks:
            name, lab, res = _task(tk)
            acc[(name, lab)] = _add(acc[(name, lab)], res)
    else:
        with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=(D, P)) as ex:
            for name, lab, res in ex.map(_task, tasks, chunksize=1):
                acc[(name, lab)] = _add(acc[(name, lab)], res)
    return acc


def cp_upper(x, n):
    """Exact one-sided Clopper-Pearson 95% upper limit for x positives in n runs (DL-25)."""
    if n <= 0:
        return float('nan')
    return 1.0 if x >= n else float(stats.beta.ppf(0.95, x + 1, n - x))


def cutoff(n, bound):
    """DL-27 rule 8c: the largest number of positives in n runs whose exact one-sided 95% upper limit is within
    `bound` (826 per test and 705 for the family at 25,000 runs; 1,682 and 1,437 at 50,000; 319 at 10,000). None if
    not even 0 positives would pass. A count passes its bound exactly when it is at most this cutoff."""
    if n <= 0 or cp_upper(0, n) > bound:
        return None
    lo, hi = 0, n                                      # cp_upper(lo, n) <= bound < cp_upper(hi, n) = 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if cp_upper(mid, n) <= bound:
            lo = mid
        else:
            hi = mid
    return lo


def evaluate(acc, gating):
    """v5 section 6 [D4]: per test, the unconditional and conditional rates against BOUND_TEST, the conditional one
    only on at least MIN_PERFORMED performed runs (STOP_TOO_FEW otherwise, which stops the run like a fail, v5 6.3 and
    DL-27 rule 8b); the Holm family rate against BOUND_FAMILY; the removal rate, not-estimable and floor counts, and
    zero-count runs (DL-23c rule 6). Each result carries its own cutoff (DL-27 rule 8c): runs is N, performed M and
    positives K."""
    n = acc['n']
    tests, ok, over, few = [], True, False, False
    cut_u = cutoff(n, BOUND_TEST)
    for i, (c, g, s) in enumerate(rp.TESTS):
        perf, fp = int(acc['performed'][i]), int(acc['fp'][i])
        bu = cp_upper(fp, n)
        if perf >= MIN_PERFORMED:
            bc, cut_c = cp_upper(fp, perf), cutoff(perf, BOUND_TEST)
            cond = 'pass' if bc <= BOUND_TEST else 'fail'
        else:
            bc, cut_c, cond = (cp_upper(fp, perf) if perf else float('nan')), None, STOP_TOO_FEW
        row = dict(cell_type=c, gene=g, sign=s, runs=n, performed=perf, removal_rate=1 - perf / n,
                   not_estimable_batch=int(acc['ne_batch'][i]), floor_removed=int(acc['ne_floor'][i]),
                   positives=fp, rate_unconditional=fp / n, bound_unconditional=bu, cutoff_unconditional=cut_u,
                   unconditional='pass' if bu <= BOUND_TEST else 'fail',
                   rate_conditional=(fp / perf if perf else float('nan')), bound_conditional=bc,
                   cutoff_conditional=cut_c, conditional=cond,
                   zero_count_runs=int(acc['zero'][i]), holm_rejections=int(acc['holm'][i]),
                   mean_oriented_t=(acc['t_sum'][i] / perf if perf else float('nan')),
                   sd_oriented_t=(float(np.sqrt(max(acc['t_ss'][i] / perf - (acc['t_sum'][i] / perf) ** 2, 0.0)))
                                  if perf else float('nan')))
        for a in (0, 1):
            if f's4_arm{a}_n' in acc:
                row[f's4_donor_{"sALS" if a else "control"}'] = dict(
                    runs=acc[f's4_arm{a}_n'], performed=int(acc[f's4_arm{a}_performed'][i]),
                    positives=int(acc[f's4_arm{a}_fp'][i]))
        ok &= row['unconditional'] == 'pass' and cond == 'pass'
        over |= row['unconditional'] == 'fail' or cond == 'fail'
        few |= cond == STOP_TOO_FEW
        tests.append(row)
    bf = cp_upper(acc['family'], n)
    fam = dict(positives=acc['family'], rate=acc['family'] / n, bound=bf, cutoff=cutoff(n, BOUND_FAMILY),
               result='pass' if bf <= BOUND_FAMILY else 'fail', all14_rejected=acc['all14'])
    ok &= fam['result'] == 'pass'
    over |= fam['result'] == 'fail'
    return dict(runs=n, gating=gating, tests=tests, family=fam, passed=bool(ok), bound_above_cap=bool(over),
                too_few_performed=bool(few), cpu_seconds=acc.get('cpu'))


def _json(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def _stop_report(a, D, absent, out, t_start, w0):
    """Codex F2 (v3; v4 adds the one-present case): the structured stop main writes when preflight() finds a tested
    cell type with fewer than two present pseudobulks. No parameter file is read, no run is drawn and no rate is
    computed, so the report holds no result: each of the 14 tests is listed as unavailable (its cell type has no
    present pseudobulk, or only one) or as not run, and no summary.tsv is written. For a type with none, the words are
    v3's."""
    one = {c for c in absent if D.ct[c].present.sum() == 1}
    verdict = ('STOP (preflight): ' + '; '.join(
        (f'{c} has rows in the design but only one present pseudobulk (DL-20), and a single donor can never give an '
         'estimable test (DL-17), ' if c in one else
         f'{c} has rows in the design but no present pseudobulk (zero nuclei or zero library in every row, DL-20), ')
        + f'so its tests ({", ".join(g)}) cannot be performed' for c, g in absent.items())
        + '. They are not estimable, which means no test, not negative biology (DL-17), and they stay in the family of '
        '14 with p = 1 (DL-27 rule 8a); in every job each would be "' + STOP_TOO_FEW + '", which stops the run (v5 '
        'section 6 item 3; DL-27 rule 8b). No parameter file was read and no run was drawn. The run stops until '
        'Ricardo decides (DL-25; v5 section 6 item 3).')
    tests = [dict(cell_type=c, gene=g, sign=s, status=('unavailable: one present pseudobulk' if c in one else
                                                        'unavailable: no present pseudobulk') if c in absent
                  else 'not run: the run stopped at the preflight') for c, g, s in rp.TESTS]
    header = dict(
        script='nullsim.py', script_md5=md5_file(__file__), pipeline_md5=md5_file(rp.__file__),
        design=a.design, design_md5=D.md5, params='not read: the run stopped at the preflight', seed=a.seed,
        jobs_requested=a.jobs, workers=a.workers, python=platform.python_version(), numpy=np.__version__,
        scipy=scipy.__version__, start_utc=t_start, end_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        wall_seconds=time.perf_counter() - w0)
    with open(out / 'report.json', 'w') as f:
        json.dump(dict(header=header, verdict=verdict,
                       preflight=dict(family_size=rp.M_FAMILY, unavailable=absent, tests=tests),
                       limitation=LIMITATION, jobs={}), f, indent=1, default=_json)
    with open(out / 'verdict.txt', 'w') as f:
        f.write(verdict + '\n\n' + LIMITATION + '\n')
    print(verdict)
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='G1A06 null simulation (DL-23, DL-23b v5, DL-23c, DL-23d, DL-23e, '
                                             'draft DL-27).')
    ap.add_argument('--design', required=True, help='design table (TSV), see the module docstring')
    ap.add_argument('--seed', required=True, type=int, help='the master seed recorded in the pre-run log')
    ap.add_argument('--out', required=True, help='output folder (must not exist yet)')
    ap.add_argument('--jobs', default='all', help='comma-separated scenario names; a subset cannot give a verdict')
    ap.add_argument('--workers', type=int, default=1)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    names = list(SCENARIOS) if a.jobs == 'all' else a.jobs.split(',')
    for nm in names:
        if nm not in SCENARIOS:
            raise SystemExit(f'unknown scenario {nm}')
    rep = sorted({nm for nm in names if names.count(nm) > 1})
    if rep:                                            # Codex F1 (v3): a repeat would count the same draws twice
        raise SystemExit(f'repeated scenario {", ".join(rep)}: each scenario may be named once')
    t_start = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    w0 = time.perf_counter()
    D = Design(a.design)
    absent = preflight(D)
    if absent:                                         # Codex F2 (v3): no parameter is read and no run is drawn
        return _stop_report(a, D, absent, out, t_start, w0)
    P = load_params()
    jobs = [(nm, lab) for nm in names for lab in (0, 1)]
    acc = run_jobs(D, P, jobs, a.seed, workers=a.workers)
    res = {f'{nm}|{LABELS[lab]}': evaluate(acc[(nm, lab)], SCENARIOS[nm]['gating']) for nm, lab in jobs}
    complete = set(names) >= {nm for nm, sc in SCENARIOS.items() if sc['gating']}
    failed = [k for k, v in res.items() if v['gating'] and not v['passed']]
    if not complete:
        verdict = 'INCOMPLETE: not every gating scenario was run, so no verdict is given'
    elif failed:
        why = {(True, False): 'an upper bound above its cap', (False, True): STOP_TOO_FEW,
               (True, True): 'an upper bound above its cap; ' + STOP_TOO_FEW}
        verdict = ('STOP: ' + '; '.join(f"{k} ({why[(res[k]['bound_above_cap'], res[k]['too_few_performed'])]})"
                                        for k in failed)
                   + '. The run stops until Ricardo decides (DL-25; v5 section 6 item 3).')
    else:
        verdict = ('PASS: every required one-sided 95% upper bound was within its cap under the generators, scenario '
                   'variants and label schemes of DL-23b v5 as amended by DL-23c, DL-23d, DL-23e and DL-27 (draft)')
    notes = []
    s4b = [k for k, v in res.items() if k.startswith('S4b') and not v['passed']]
    if s4b:
        notes.append('S4b did not pass (' + ', '.join(s4b) + '): not a stop, but the [A5] no-exclusion sensitivity '
                     'cannot be read as calibrated (v5 section 5).')
    header = dict(
        script='nullsim.py', script_md5=md5_file(__file__), pipeline_md5=md5_file(rp.__file__),
        design=a.design, design_md5=D.md5, params={k: v for k, v in PARAM_FILES.items()},
        seed=a.seed, bit_generator=BITGEN, seed_rule='SeedSequence(seed, spawn_key=(sid, label scheme, chunk))',
        chunk=CHUNK, coding=CODING, workers=a.workers, cpu_count=os.cpu_count(), python=platform.python_version(),
        numpy=np.__version__, scipy=scipy.__version__, start_utc=t_start,
        end_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), wall_seconds=time.perf_counter() - w0,
        design_summary=design_summary(D, P))
    with open(out / 'report.json', 'w') as f:
        json.dump(dict(header=header, verdict=verdict, notes=notes, limitation=LIMITATION, jobs=res), f, indent=1,
                  default=_json)
    with open(out / 'summary.tsv', 'w') as f:
        cols = ['performed', 'removal_rate', 'not_estimable_batch', 'floor_removed', 'positives', 'rate_unconditional',
                'bound_unconditional', 'cutoff_unconditional', 'unconditional', 'rate_conditional', 'bound_conditional',
                'cutoff_conditional', 'conditional', 'zero_count_runs', 'holm_rejections', 'mean_oriented_t',
                'sd_oriented_t']
        f.write('\t'.join(['scenario', 'labels', 'gating', 'runs', 'cell_type', 'gene'] + cols) + '\n')
        for key, v in res.items():
            nm, lab = key.split('|')
            for r in v['tests']:
                f.write('\t'.join([nm, lab, str(v['gating']), str(v['runs']), r['cell_type'], r['gene']]
                                  + [f'{r[c]:.6g}' if isinstance(r[c], float) else str(r[c]) for c in cols]) + '\n')
            fam = v['family']
            f.write('\t'.join([nm, lab, str(v['gating']), str(v['runs']), 'FAMILY', 'Holm', '', '', '', '',
                               str(fam['positives']), f"{fam['rate']:.6g}", f"{fam['bound']:.6g}", str(fam['cutoff']),
                               fam['result']] + [''] * 8) + '\n')
    with open(out / 'verdict.txt', 'w') as f:
        f.write(verdict + '\n')
        for nt in notes:
            f.write(nt + '\n')
        f.write('\n' + LIMITATION + '\n')
    print(verdict)
    return 0 if (complete and not failed) else 1


if __name__ == '__main__':
    sys.exit(main())
