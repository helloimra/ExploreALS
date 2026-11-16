"""G1A06 R1 primary pipeline: donor-celltype pseudobulk counts to the one-sided Holm decision over the 14 tests.

Rules implemented, and nothing else: frozen spec coordinator/G1A06_REPLICATION_SPEC_FROZEN_2026-10-23.md
(md5 5bbc2a9994dc1f642708f01a2699f9c3) section 1 ([S1] log2 CPM, OLS arm + age + sex), section 5 (batch factors as
covariates), section 6 (depth rule, its [A5] switches, the [A4] arm-blind floor), section 7 (m stays 14) and section 8
([A1] one-sided Holm at 0.025), as amended in coordinator/G1A06_DEVIATION_LOG_2026-10-23.md by DL-09 (Cramer's V is a
warning only, so it is not a stop here), DL-12 (orientation), DL-15 (classical OLS t), DL-17 (estimability), DL-18
(split-donor fractions), DL-19 (depth median), DL-20 (absence), DL-21 (no normalization factors) and DL-24 (split donors
in the DL-17(ii) count); and by the draft entry DL-27 (a working name; coordinator/DL27_NULLSIM_RULE_AMENDMENTS_DRAFT_
2026-10-25.md): batch enters the model per factor (rule 1, question A1) and DL-17(ii) is also checked on the joint batch
cells (rule 2, question A2).

Every array carries a leading run axis R, so one call analyses R simulated data sets (R = 1 for one real data set).
Batch levels arrive merged: merging (section 5 as revised by DL-09) is a metadata step before this code.
Not implemented (sensitivities outside the null simulation): HC3 (DL-15), the discovery formula and the discovery floor
(sections 1 and 6), the unadjusted model (section 4), the split-donor exclusion (DL-14), PMI/RIN, [A13].

Choices the rules do not make are marked CHOICE C-n and listed in coordinator/NULLSIM_CODE_RESULT_2026-10-25.md; those
the DL-27 draft decides are marked with its rule.
Draft code for DL-27, which Ricardo adopted as a basis on 25 Oct 2026 22:01:13Z ("Adopt all eight"): a copy of
work/g1a06_nullsim/r1pipeline.py (md5 a7cc333f7242ae01c05e5831ad3afe7a) with those changes. Written and tested on
made-up data only, 25 Oct 2026. Not in force until Ricardo freezes DL-27.
"""
import warnings
import numpy as np
from scipy import stats

ALPHA = 0.025                      # [A1]; also DL-23's per-test one-sided false-positive threshold
M_FAMILY = 14                      # section 7: a test not performed counts as not rejected and m stays 14 (holm_onesided)
FLOOR_MIN = 10.0                   # [A4]
DEPTH_CUTOFFS = {'primary': 0.1, 'one_fifth': 0.2, 'none': None}   # section 6 and [A5]
DF_MIN = 10                        # DL-17(iii)
MIX_TOL = 1e-9                     # CHOICE C-14: float tolerance on DL-17(ii)'s half (fractions such as 0.7 are inexact)

# The 14 tests in the order of work/dl23e_values/coordinator/values.tsv, with the DL-12 discovery sign.
TESTS = (('L2_L3', 'BRSK2', -1), ('Oligo', 'MYO18A', +1), ('L5', 'KIFC2', -1), ('L3_L5', 'BRSK2', -1),
         ('Oligo', 'DNAJB2', -1), ('L4_L6', 'KIFC2', -1), ('L4_L5', 'KIFC2', -1), ('L4_L5', 'BRSK2', -1),
         ('L2_L3', 'AP1G2', -1), ('L2_L3', 'ZNF783', -1), ('L3_L5', 'KIFC2', -1), ('L2_L3', 'AGAP2', -1),
         ('L2_L3', 'SNPH', -1), ('L2_L3', 'MIB2', -1))
CELL_TYPES = tuple(sorted({c for c, _, _ in TESTS}))
SIGNS = np.array([s for _, _, s in TESTS], float)
TESTS_OF = {c: np.array([i for i, (cc, _, _) in enumerate(TESTS) if cc == c]) for c in CELL_TYPES}

PERFORMED, NE_BATCH, NE_FLOOR = 0, 1, 2        # per-test state; NE = not estimable (section 8)
BIT_RANK, BIT_MIX, BIT_DF, BIT_JOINT = 1, 2, 4, 8     # which DL-17 condition failed; 8: (ii) on the joint cells (DL-27 2)


def log2cpm(count, lib):
    """[S1] log2((count + 0.5) / (library size + 1) x 10^6); library size = the pseudobulk's raw total (DL-21)."""
    return np.log2((np.asarray(count, float) + 0.5) / (np.asarray(lib, float) + 1.0) * 1e6)


def depth_rule(lib, present, cutoff):
    """DL-20, DL-19 and the section 6 rule. lib, present: (R, n). The median is over present pseudobulks, arms pooled,
    before the rule; a pseudobulk below cutoff x median is excluded (so exactly cutoff x median is kept); cutoff None
    is [A5]'s no-exclusion run. Returns retained (R, n) and the median (R,)."""
    lib = np.asarray(lib, float)
    present = np.asarray(present, bool)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)          # a run with no present pseudobulk has no median
        med = np.nanmedian(np.where(present, lib, np.nan), axis=-1)
    if cutoff is None:
        return present.copy(), med
    with np.errstate(invalid='ignore'):
        return present & (lib >= cutoff * med[..., None]), med


def floor_test(counts, lib, retained):
    """[A4]: pooled-arm CPM x each retained donor's library size / 10^6 >= 10 for every retained donor, pooled-arm CPM
    = (sum of the gene's counts over retained donors of both arms) / (sum of their library sizes) x 10^6. It binds at
    the shallowest retained donor. counts (R, n, k), lib and retained (R, n). Returns ok (R, k) and the statistic."""
    r = retained.astype(float)
    tot = np.einsum('rnk,rn->rk', counts, r)
    libsum = (lib * r).sum(1)
    smin = np.where(retained, lib, np.inf).min(1)
    with np.errstate(invalid='ignore', divide='ignore'):
        stat = tot / libsum[:, None] * smin[:, None]
    return np.nan_to_num(stat, nan=-np.inf) >= FLOOR_MIN, stat


def _half_in_mixed(arm, retained, F, Fm):
    """DL-17(ii) with DL-24's counting on one partition of the donors (a factor's levels, or the joint cells of DL-27
    rule 2): a part contains both arms when it holds a share of a retained donor of each arm (decided on F); each arm
    passes when at least half its retained donors sit in such parts, a split donor counting only its shares there
    (counted on Fm). F, Fm (R, n, L). Returns ok (R,), the retained shares (R, n, L) and the mixed parts (R, L)."""
    pos = (F > 0) & retained[..., None]                                  # (R, n, L)
    has1 = (pos & (arm[..., None] == 1)).any(1)
    has0 = (pos & (arm[..., None] == 0)).any(1)
    mixed = has1 & has0                                                  # (R, L) parts containing both arms
    inmix = (Fm * mixed[:, None, :]).sum(2)                              # each donor's fraction in mixed parts
    ok = np.ones(arm.shape[0], bool)
    for a in (0, 1):
        sel = retained & (arm == a)
        ok &= (inmix * sel).sum(1) >= sel.sum(1) / 2.0 - MIX_TOL         # DL-17(ii) with DL-24
    return ok, pos, mixed


def _batch_masks(arm, retained, F_list, coding, F_mix=None):
    """For each factor: the levels that carry a model column, and DL-17(ii) with DL-24's counting. F_mix: the fractions
    counted for DL-17(ii) (DL-24: nuclei-weighted) when the columns carry other ones (the count-weighted S1 of DL-23b v5
    section 6); default F_list.
    DL-27 rule 1 (C-1), coding 'full' (default): every level holding a retained donor gets a fraction column, one such
    level per factor (the first in the design's level order) being the reference; each donor's fractions sum to 1
    within a factor, so the fit does not depend on which. 'mixed_only' (the per-level reading of section 5's "where they
    span both arms", kept for the record of DL-27 rule 1 only and not reachable from the command line): columns only for
    levels holding both arms, the first of them the reference, so a donor in a single-arm level is coded as if it sat
    in the reference level and that level's effect is not modelled."""
    R = arm.shape[0]
    mix_ok = np.ones(R, bool)
    cols = []
    for F, Fm in zip(F_list, F_list if F_mix is None else F_mix):
        ok, pos, mixed = _half_in_mixed(arm, retained, F, Fm)
        mix_ok &= ok
        base = pos.any(1) if coding == 'full' else mixed
        cm = base.copy()
        cm[np.arange(R), np.argmax(base, axis=1)] = False               # the reference level (no-op if none)
        cols.append(cm)
    return mix_ok, cols


def _design(arm, age, sex, retained, F_list, cols):
    """X (G, n, p): [1, arm, age centred on the retained donors, sex, batch fractions], zero rows where not retained.
    Centring age is numerical only (an intercept is present). cols: per factor, a (L,) mask shared by the G runs."""
    ret = retained.astype(float)
    nret = ret.sum(1, keepdims=True)
    agec = age - (age * ret).sum(1, keepdims=True) / np.where(nret > 0, nret, 1)
    parts = [np.ones_like(agec), arm.astype(float), agec, np.broadcast_to(sex, agec.shape).astype(float)]
    for F, cm in zip(F_list, cols):
        parts += [F[:, :, j] for j in np.flatnonzero(cm)]
    return np.stack(parts, axis=2) * ret[..., None]


def _ols_arm(X, Y, nret):
    """Classical OLS t on column 1 (arm), DL-15. X (G, n, p) with zero rows outside the analysis (identical to dropping
    them), Y (G, n, k) likewise. Returns beta (G, k), se (G, k), df (G,)."""
    Q, Rm = np.linalg.qr(X)
    B = np.linalg.solve(Rm, np.matmul(np.swapaxes(Q, 1, 2), Y))
    res = Y - np.matmul(X, B)
    df = nret - X.shape[2]
    s2 = (res ** 2).sum(1) / df[:, None]
    v = (np.linalg.inv(Rm)[:, 1, :] ** 2).sum(-1)                        # [(X'X)^-1]_11 = sum_j (R^-1)_1j^2
    return B[:, 1, :], np.sqrt(s2 * v[:, None]), df


def _runs(a, R, tail):
    a = np.asarray(a)
    if a.ndim == tail:
        a = a[None]
    return np.broadcast_to(a, (R,) + a.shape[1:])


def _identical(a):
    return a.shape[0] == 1 or bool((a == a[:1]).all())


def analyse_celltype(lib, present, arm, age, sex, F_list, signs, counts=None, Y=None,
                     depth_cutoff=DEPTH_CUTOFFS['primary'], coding='full', p_mode='onesided', F_mix=None, F_joint=None):
    """One cell type over R runs and its k tests.
    counts (R, n, k): pseudobulk counts, from which [S1] values and the [A4] floor are computed; or Y (R, n, k): values
    given directly with no floor (the Gaussian diagnostic of DL-23b v5 section 3). lib (R, n) library sizes; present
    (R, n) or (n,) DL-20; arm (R, n) 1 = sALS; age (R, n); sex (n,) 1 = male; F_list: per batch factor, (R, n, L) or
    (n, L) fractions; signs (k,) DL-12. p_mode 'abs_halved' is a deliberately wrong variant for the code test only.
    F_joint (R, n, J) or (n, J): each donor's nuclei-weighted fractions over the joint batch cells, a joint cell being
    one combination of levels, one level of each factor (DL-27 rule 2). It is required with more than one batch factor;
    with one factor the joint cells are that factor's levels, and with none there is nothing to check.
    Returns p (R, k) one-sided in the discovery direction (1.0 where not performed), state (R, k), beta, se (nan where
    not performed), df (R,), bits (R,) the failed DL-17 conditions, retained (R, n), floor_stat (R, k)."""
    if F_joint is None and len(F_list) > 1:
        raise ValueError('DL-27 rule 2: the joint batch cells are needed when there is more than one batch factor')
    data = counts if counts is not None else Y
    R, n, k = np.shape(data)
    lib = _runs(np.asarray(lib, float), R, 1)
    present = _runs(np.asarray(present, bool), R, 1) & (lib > 0)      # DL-20 (zero nuclei: the caller's present)
    arm = _runs(np.asarray(arm), R, 1)
    age = _runs(np.asarray(age, float), R, 1)
    sex = np.asarray(sex, float)
    F_list = [_runs(np.asarray(F, float), R, 2) for F in F_list]
    F_mix = None if F_mix is None else [_runs(np.asarray(F, float), R, 2) for F in F_mix]
    F_joint = None if F_joint is None else _runs(np.asarray(F_joint, float), R, 2)
    signs = np.asarray(signs, float)

    retained, _ = depth_rule(lib, present, depth_cutoff)
    if counts is not None:
        floor_ok, floor_stat = floor_test(np.asarray(counts, float), lib, retained)
        Yv = log2cpm(counts, lib[..., None])
    else:
        floor_ok, floor_stat = np.ones((R, k), bool), np.full((R, k), np.nan)
        Yv = np.asarray(Y, float)
    Yv = np.where(retained[..., None], Yv, 0.0)                     # rows outside the analysis carry no value

    beta = np.full((R, k), np.nan)
    se = np.full((R, k), np.nan)
    df = np.zeros(R, int)
    bits = np.zeros(R, int)
    fixed = all(_identical(a) for a in [arm, age, retained] + list(F_list) + list(F_mix or [])
                + ([] if F_joint is None else [F_joint]))
    sel_runs = np.zeros(R, bool) if fixed else np.ones(R, bool)
    if fixed:                                           # one design for every run: decide and factor it once
        mix_ok, cols = _batch_masks(arm[:1], retained[:1], [F[:1] for F in F_list], coding,
                                    None if F_mix is None else [F[:1] for F in F_mix])
        joint_ok = (np.ones(1, bool) if F_joint is None
                    else _half_in_mixed(arm[:1], retained[:1], F_joint[:1], F_joint[:1])[0])
        X = _design(arm[:1], age[:1], sex, retained[:1], [F[:1] for F in F_list], [c[0] for c in cols])
        nret = int(retained[0].sum())
        p_ = X.shape[2]
        b = 0
        if np.linalg.matrix_rank(X[0]) < p_:
            b |= BIT_RANK
        if not mix_ok[0]:
            b |= BIT_MIX
        if nret - p_ < DF_MIN:
            b |= BIT_DF
        if not joint_ok[0]:
            b |= BIT_JOINT
        bits[:] = b
        df[:] = nret - p_
        if b == 0:
            rows = retained[0]
            X0 = X[0][rows]
            Q, Rm = np.linalg.qr(X0)
            Yr = Yv[:, rows, :].transpose(1, 0, 2).reshape(nret, R * k)
            Bm = np.linalg.solve(Rm, Q.T @ Yr)
            res = Yr - X0 @ Bm
            s2 = (res ** 2).sum(0) / (nret - p_)
            v = (np.linalg.inv(Rm)[1, :] ** 2).sum()
            beta = Bm[1].reshape(R, k)
            se = np.sqrt(s2 * v).reshape(R, k)
    else:                                               # designs differ by run: group runs by their column sets
        mix_ok, cols = _batch_masks(arm, retained, F_list, coding, F_mix)
        joint_ok = np.ones(R, bool) if F_joint is None else _half_in_mixed(arm, retained, F_joint, F_joint)[0]
        if cols:
            uniq, inv = np.unique(np.concatenate(cols, axis=1), axis=0, return_inverse=True)
            inv = np.ravel(inv)
        else:                                           # no batch factor: one column set
            uniq, inv = np.zeros((1, 0), bool), np.zeros(R, int)
        nret_all = retained.sum(1)
        for gi in range(uniq.shape[0]):
            runs = np.flatnonzero(inv == gi)
            cm = []
            off = 0
            for c in cols:
                cm.append(uniq[gi, off:off + c.shape[1]])
                off += c.shape[1]
            X = _design(arm[runs], age[runs], sex, retained[runs], [F[runs] for F in F_list], cm)
            p_ = X.shape[2]
            rank_ok = np.linalg.matrix_rank(X) == p_
            nret = nret_all[runs]
            b = (np.where(rank_ok, 0, BIT_RANK) | np.where(mix_ok[runs], 0, BIT_MIX)
                 | np.where(nret - p_ >= DF_MIN, 0, BIT_DF) | np.where(joint_ok[runs], 0, BIT_JOINT))
            bits[runs] = b
            df[runs] = nret - p_
            ok = runs[b == 0]
            if ok.size:
                Xo = X[b == 0]
                Yo = Yv[ok] * retained[ok][..., None]
                bo, so, _ = _ols_arm(Xo, Yo, nret[b == 0])
                beta[ok], se[ok] = bo, so

    est = bits == 0
    state = np.where(~est[:, None], NE_BATCH, np.where(floor_ok, PERFORMED, NE_FLOOR))
    with np.errstate(invalid='ignore', divide='ignore'):
        t = beta / se
        if p_mode == 'onesided':
            p = stats.t.sf(signs[None, :] * t, np.where(est, df, 1)[:, None])
        elif p_mode == 'abs_halved':                   # WRONG ON PURPOSE: two-sided p halved, direction ignored
            p = stats.t.sf(np.abs(t), np.where(est, df, 1)[:, None])
        else:
            raise ValueError(p_mode)
    performed = state == PERFORMED
    p = np.where(performed, p, 1.0)
    return dict(p=p, state=state, beta=np.where(performed, beta, np.nan), se=np.where(performed, se, np.nan),
                df=df, bits=bits, retained=retained, floor_stat=floor_stat)


def holm_onesided(p, alpha=ALPHA):
    """[A1] Holm step-down at alpha over the m = M_FAMILY columns of p (R, m); a test not performed carries p = 1, so m
    stays 14 (section 7). Returns rejected (R, m)."""
    R, m = p.shape
    if m != M_FAMILY:
        raise ValueError(f'the family has {M_FAMILY} tests (section 7), not {m}')
    order = np.argsort(p, axis=1, kind='stable')
    ps = np.take_along_axis(p, order, axis=1)
    keep = np.cumprod(ps <= alpha / (m - np.arange(m)), axis=1).astype(bool)
    rej = np.zeros((R, m), bool)
    np.put_along_axis(rej, order, keep, axis=1)
    return rej
