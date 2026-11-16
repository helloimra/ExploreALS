"""G1A06 [A6] cell-type crosswalk: the frozen automated label-transfer procedure of the run bundle.

Frozen spec section 6 [A6]: every cohort label is mapped to every D003 type; map at the D003 type's level and merge all
subclusters under it; a label with no unambiguous parent is excluded; the reference is D003's own annotation with the
nine R1 genes and CAPG masked from the feature set; code and parameters are fixed before it is run; marker evidence is
recorded per mapping.

Method (bundle CHOICE B-2). The reference is, for each of the 19 human D003 types, the ORDER (average ranks, 1 = lowest)
of a frozen set of feature genes by their pooled BA9 expression in that type (reference/d003_ba9_crosswalk_ranks.tsv;
built from Pineda et al., Cell 2024, syn51105515, sporadic ALS and control BA9 libraries pooled, arms pooled). Feature
genes are protein-coding genes that vary across the 19 types; the ten masked genes, mitochondrial and ribosomal-protein
genes, XIST and chromosome Y genes are never features. A cohort label's profile is its summed counts over the feature
genes (all donors and samples pooled). Its Spearman correlation with every D003 type is computed over the feature genes
the cohort measures (the reference ranks are re-ranked on that subset). The label goes to its best type only if
  (1) the best correlation is at least R_MIN, and
  (2) the best exceeds the runner-up by at least DELTA;
otherwise it has no unambiguous parent and is excluded. Labels the holder marks as doublet or low-quality are excluded
before mapping.
No fine-tuning step is used: it forces mixtures of adjacent types onto one type (tested on D003, 31 Oct), which the
granularity rule forbids. R_MIN and DELTA were set on D003 itself (split-half and merged-type labels) before any
cohort was seen.
If fewer than MIN_FEATURE_FRACTION of the feature genes are measured, no crosswalk is made. A tested D003 type that
receives no cohort label (for that reason, or because every candidate label was refused) has no pseudobulk, and the
adopted null simulation's preflight (DL-27 rule 8b) then stops the whole run before the fit: no test is read.

The ten masked genes are never read by this module: only feature genes enter the crosswalk.
"""
import csv
import numpy as np
from scipy import stats

MASKED = ('BRSK2', 'KIFC2', 'MYO18A', 'DNAJB2', 'AP1G2', 'ZNF783', 'AGAP2', 'SNPH', 'MIB2', 'CAPG')
R_MIN = 0.70                 # set by the D003 calibration (build_reference.py calibrate), frozen with the bundle hash
DELTA = 0.02                 # likewise
MIN_FEATURE_FRACTION = 0.80


def load_reference(path):
    """Returns dict(ensembl, symbol, types, ranks (G, T))."""
    with open(path, newline='') as f:
        rd = csv.reader(f, delimiter='\t')
        head = next(rd)
        rows = list(rd)
    if head[:2] != ['ensembl', 'symbol']:
        raise ValueError('reference header must start ensembl, symbol')
    types = head[2:]
    ens = [r[0] for r in rows]
    sym = [r[1] for r in rows]
    if set(MASKED) & set(sym):
        raise ValueError('a masked gene is in the reference feature set')
    ranks = np.array([[float(x) for x in r[2:]] for r in rows])
    return dict(ensembl=ens, symbol=sym, types=types, ranks=ranks)


def match_features(ref, gene_ids):
    """Index of each reference feature in the cohort's gene columns (Ensembl ID first, version suffix ignored; else
    the symbol), or -1. Returns (idx (G,), how)."""
    def strip(g):
        return g.split('.')[0] if g.startswith('ENSG') else g
    pos = {}
    for j, g in enumerate(gene_ids):
        pos.setdefault(strip(g), j)
    idx = np.full(len(ref['ensembl']), -1)
    how = {'ensembl': 0, 'symbol': 0}
    for i, (e, s) in enumerate(zip(ref['ensembl'], ref['symbol'])):
        if e in pos:
            idx[i] = pos[e]; how['ensembl'] += 1
        elif s in pos:
            idx[i] = pos[s]; how['symbol'] += 1
    return idx, how


def correlations(ref, label_counts, idx):
    """Spearman correlation of each label (rows of label_counts, cohort gene columns) with each D003 type over the
    measured feature genes. Returns (n_labels, T)."""
    use = idx >= 0
    R = np.apply_along_axis(stats.rankdata, 0, ref['ranks'][use])            # re-rank the reference on the subset
    X = np.asarray(label_counts, float)[:, idx[use]]
    Lr = np.apply_along_axis(stats.rankdata, 1, X)
    Rc = R - R.mean(0)
    Lc = Lr - Lr.mean(1, keepdims=True)
    with np.errstate(invalid='ignore', divide='ignore'):
        return (Lc @ Rc) / np.sqrt((Lc ** 2).sum(1)[:, None] * (Rc ** 2).sum(0)[None, :])


def assign(rho, types, r_min=R_MIN, delta=DELTA):
    """For each label: (assigned type or None, best, second, margin, reason)."""
    out = []
    for row in rho:
        if not np.all(np.isfinite(row)):
            out.append((None, float('nan'), float('nan'), float('nan'), 'excluded: profile has no variation'))
            continue
        o = np.argsort(-row, kind='stable')
        b, s = float(row[o[0]]), float(row[o[1]])
        if b < r_min:
            out.append((None, b, s, b - s, f'excluded: best correlation below {r_min}'))
        elif b - s < delta:
            out.append((None, b, s, b - s, f'excluded: no unambiguous parent (margin below {delta}; best '
                        f'{types[o[0]]}, runner-up {types[o[1]]})'))
        else:
            out.append((types[o[0]], b, s, b - s, 'mapped'))
    return out


def crosswalk(ref, labels, gene_ids, label_counts, excluded_labels=(), r_min=R_MIN, delta=DELTA):
    """The full crosswalk. Returns dict(possible, n_features, matched, labels: list of per-label dicts with the
    correlation to every D003 type, mapping: {label: type}, reason)."""
    idx, how = match_features(ref, gene_ids)
    n_feat = int((idx >= 0).sum())
    res = dict(n_features_reference=len(idx), n_features_measured=n_feat, matched_by=how, labels=[], mapping={})
    if n_feat < MIN_FEATURE_FRACTION * len(idx):
        res.update(possible=False, reason=f'only {n_feat} of {len(idx)} feature genes measured (needs '
                                          f'{MIN_FEATURE_FRACTION:.0%}): no crosswalk, every test not estimable')
        return res
    keep = [i for i, l in enumerate(labels) if l not in set(excluded_labels)]
    rho = correlations(ref, np.asarray(label_counts, float)[keep], idx)
    for k, (i, (t, b, s, m, why)) in enumerate(zip(keep, assign(rho, ref['types'], r_min, delta))):
        res['labels'].append(dict(label=labels[i], assigned=t, best=b, runner_up=s, margin=m, reason=why,
                                  rho={ty: float(v) for ty, v in zip(ref['types'], rho[k])}))
        if t is not None:
            res['mapping'][labels[i]] = t
    for i, l in enumerate(labels):
        if l in set(excluded_labels):
            res['labels'].append(dict(label=l, assigned=None, best=float('nan'), runner_up=float('nan'),
                                      margin=float('nan'), reason='excluded: marked doublet or low quality by the '
                                      'holder', rho={}))
    res.update(possible=True, reason='ok')
    return res
