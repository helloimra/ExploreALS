"""G1A06 run bundle: a made-up cohort in the bundle's input format, for the self-test (spec 10.2) and the code tests.

No real data. Donors, samples, labels and counts are invented. Gene counts of the 9 tested genes are negative
binomial at the donor level (one gamma multiplier per donor and test, Poisson per sample and label), with the logged
discovery rates and dispersions for the 14 tested pairs (values.tsv, as in the null simulation) and small generic
values elsewhere; age, sex and batch effects as in DL-23b v5 section 2.2. Ages are plainly invented: the same mean
and SD in both groups (60 and 10 years, clipped to 40-95), chosen without reference to any dataset (Researcher re-check
of version 2, V2-1). A planted effect of `fold` in the discovery
direction is applied in sALS for every one of the 14 tests (fold 1.0: no effect). Label profiles over the crosswalk
feature genes are made from the reference order with noise, so the crosswalk can be exercised: two subclusters of
L2_L3, a doublet label (marked by the holder) and a coarse mixed excitatory label (which must be excluded).
"""
import csv
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / 'work' / 'g1a06_nullsim_v4'))
import r1pipeline as rp
import crosswalk as cw

GENES9 = ('BRSK2', 'KIFC2', 'MYO18A', 'DNAJB2', 'AP1G2', 'ZNF783', 'AGAP2', 'SNPH', 'MIB2')
BASE_NUCLEI = {'5HT3aR': 500, 'Astro': 800, 'Endo': 40, 'Fibro': 5, 'L2_L3': 900, 'L3_L5': 700, 'L4_L5': 150,
               'L4_L6': 300, 'L5': 90, 'L5_L6': 180, 'L6': 80, 'Micro': 250, 'Mural': 40, 'OPC': 400, 'Oligo': 700,
               'PV': 350, 'Rosehip': 170, 'SOM': 200, 'T_Cell': 5}


def params():
    with open(HERE / 'work/dl23e_values/coordinator/values.tsv', newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    return {(r['cell_type'], r['gene']): (float(r['mu_g']), float(r['phi_g'])) for r in rows}


def make(out, n_per_arm=35, fold=1.5, seed=1, split_share=0.1, unknown_share=0.2, factors=('prep', 'seqrun'),
         levels=(6, 3), extra_ineligible=True, drop_types=(), confound=False, pmi_missing=0.05, label_noise=0.15,
         mu_scale=None, n_features_kept=None, age_matched=False, n_extra_genes=0, extra_effect_share=0.0):
    """age_matched=True gives the controls the same ages as the sALS donors (same draws, so every other draw is
    unchanged). The self-test uses it: under the realized labels, the null simulation's unmodelled age term (0.10 z^2,
    DL-23b v5 section 2.2) shifts the arm estimate by a fixed amount whenever the two arms' age distributions differ
    in shape, and the adopted code then stops before the fit. Identical ages in both arms remove that shift, so the
    positive control can show the whole run, null simulation included.
    n_extra_genes > 0 also writes the optional counts_all_genes.csv: the 9 tested genes exactly as in counts.csv, plus
    that many made-up genes (MADEUP00001, ...) drawn from a separate generator, so every other draw is unchanged; a share
    extra_effect_share of them carries a made-up arm effect of +/- 0.5 log2."""
    rng = np.random.default_rng(seed)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    par = params()
    ref = cw.load_reference(HERE / 'reference/d003_ba9_crosswalk_ranks.tsv')
    types = ref['types']
    # donors
    donors = []
    for a, nm in ((1, 'ALS'), (0, 'control')):
        for i in range(n_per_arm):
            unk = a == 1 and rng.random() < unknown_share
            donors.append(dict(donor=f'SIMDONOR{len(donors) + 1:03d}', brain_bank='Made-up Bank', diagnosis=nm,
                               sporadic_label='yes' if a else '', c9orf72=('not_tested' if unk else 'negative') if a else '',
                               family_history='negative' if a else '', neuropath_normal='' if a else 'yes',
                               age=f'{float(np.clip(rng.normal(60, 10), 40, 95)):.0f}',      # invented (V2-1)
                               sex='M' if rng.random() < 0.55 else 'F',
                               pmi='' if rng.random() < pmi_missing else f'{max(rng.normal(12, 6), 2):.1f}',
                               rin=f'{float(np.clip(rng.normal(6.5, 1.5), 2, 10)):.1f}'))
    if age_matched:
        als_ages = [d['age'] for d in donors[:n_per_arm]]
        for d, a in zip(donors[n_per_arm:2 * n_per_arm], als_ages):
            d['age'] = a
    if extra_ineligible:
        for kw in (dict(diagnosis='ALS', sporadic_label='yes', c9orf72='positive', family_history='negative'),
                   dict(diagnosis='ALS', sporadic_label='yes', c9orf72='negative', family_history='positive'),
                   dict(diagnosis='ALS', sporadic_label='', c9orf72='negative', family_history=''),
                   dict(diagnosis='control', neuropath_normal='no'),
                   dict(diagnosis='control', neuropath_normal='yes', brain_bank='Mayo Clinic Jacksonville'),
                   dict(diagnosis='FTD'), dict(diagnosis='ALS', sporadic_label='yes', c9orf72='negative',
                                               family_history='negative', age='')):
            d = dict(donor=f'SIMDONOR{len(donors) + 1:03d}', brain_bank='Made-up Bank', diagnosis='', sporadic_label='',
                     c9orf72='', family_history='', neuropath_normal='', age='70', sex='F', pmi='10', rin='7')
            d.update(kw)
            donors.append(d)
    # samples
    samples = []
    lev = {f: [f'{f.upper()}{j + 1}' for j in range(L)] for f, L in zip(factors, levels)}
    for d in donors:
        k = 2 if rng.random() < split_share else 1
        for s in range(k):
            row = dict(sample=f'{d["donor"]}_S{s + 1}', donor=d['donor'], region='BA9')
            for f in factors:
                if confound and f == factors[0]:
                    row['batch_' + f] = lev[f][0] if d['diagnosis'] == 'ALS' else lev[f][1]
                else:
                    row['batch_' + f] = lev[f][rng.integers(len(lev[f]))]
            samples.append(row)
        if rng.random() < 0.2:
            samples.append(dict(sample=f'{d["donor"]}_M1', donor=d['donor'], region='BA4',
                                **{'batch_' + f: lev[f][0] for f in factors}))
    # labels: one per D003 type (L2_L3 as two subclusters), a doublet and a coarse mixed label
    lab_types = {}
    for t in types:
        if t in drop_types:
            continue
        if t == 'L2_L3':
            lab_types['cohort_L2_L3_a'] = [('L2_L3', 0.5)]
            lab_types['cohort_L2_L3_b'] = [('L2_L3', 0.5)]
        else:
            lab_types['cohort_' + t] = [(t, 1.0)]
    lab_types['cohort_doublet'] = [('Oligo', 0.02), ('L2_L3', 0.02)]
    lab_types['cohort_EN_mixed'] = [('L2_L3', 0.03), ('L3_L5', 0.03), ('L4_L6', 0.03)]
    # label profiles over the feature genes, from the reference order with noise
    z = (ref['ranks'] - ref['ranks'].mean(0)) / ref['ranks'].std(0)
    prof_t = {t: np.exp(1.2 * z[:, j] + rng.normal(0, label_noise, z.shape[0])) for j, t in enumerate(types)}
    labels = list(lab_types)
    prof = []
    for l in labels:
        v = sum(w / max(sum(ww for _, ww in lab_types[l]), 1e-9) * prof_t[t] * (1 + 0.1 * rng.normal(0, 1, z.shape[0]) ** 2)
                for t, w in lab_types[l])
        prof.append(rng.poisson(v / v.sum() * 2e6))
    keep = np.arange(len(ref['ensembl'])) if n_features_kept is None else np.arange(n_features_kept)
    with open(out / 'label_profiles.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['label'] + [ref['ensembl'][i] for i in keep])
        for l, p in zip(labels, prof):
            w.writerow([l] + [int(p[i]) for i in keep])
    # counts per sample x label
    blev = {f: dict(zip(lev[f], rng.normal(0, 0.25, len(lev[f])))) for f in factors}
    dmap = {d['donor']: d for d in donors}
    ages = np.array([float(d['age']) for d in donors if d['age']])
    mz, sz = ages.mean(), ages.std()
    gam = {}
    rows = []
    rowinfo = []                                      # for the optional genome-wide file (no draw from rng)
    for s in samples:
        d = dmap[s['donor']]
        als = d['diagnosis'] == 'ALS'
        age = float(d['age']) if d['age'] else mz
        zz = (age - mz) / sz
        l2 = 0.10 * zz + 0.10 * zz ** 2 + (0.10 if d['sex'] == 'F' else 0.0) + sum(blev[f][s['batch_' + f]] for f in factors)
        upn = np.exp(rng.normal(np.log(4500), 0.3))
        for l in labels:
            nuc = 0
            mean_g = np.zeros(len(GENES9))
            libs = 0.0
            libs_t = []
            for t, wgt in lab_types[l]:
                nt = rng.poisson(BASE_NUCLEI[t] * wgt * (0.8 if t in drop_types else 1.0))
                nuc += nt
                lib_t = nt * upn
                libs += lib_t
                libs_t.append(lib_t)
                for gi, g in enumerate(GENES9):
                    mu, phi = par.get((t, g), (2e-5, 0.1))
                    mu *= (mu_scale or {}).get((t, g), 1.0)
                    eff = 0.0
                    for ti, (tc, tg, sg) in enumerate(rp.TESTS):
                        if tc == t and tg == g and als:
                            eff = sg * np.log2(fold)
                    key = (s['donor'], t, g)
                    if key not in gam:
                        gam[key] = rng.gamma(1 / phi, phi) if phi > 0 else 1.0
                    mean_g[gi] += mu * lib_t * 2 ** (l2 + eff) * gam[key]
            cnt = rng.poisson(mean_g)
            rowinfo.append((s['donor'], als, l2, [(t, nt_lib) for t, nt_lib in zip([t for t, _ in lab_types[l]], libs_t)]))
            rows.append([s['sample'], l, nuc, int(round(libs))] + [int(x) for x in cnt])
    with open(out / 'counts.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['sample', 'label', 'nuclei', 'total_counts'] + list(GENES9))
        w.writerows(rows)
    if n_extra_genes:
        r2 = np.random.default_rng([seed, 7])
        G = n_extra_genes
        mu2 = {t: np.exp(r2.normal(np.log(5e-5), 1.5, G)) for t in types}
        eff2 = np.where(r2.random(G) < extra_effect_share, r2.choice([-0.5, 0.5], G), 0.0)
        gam2 = {}
        with open(out / 'counts_all_genes.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['sample', 'label'] + list(GENES9) + [f'MADEUP{i + 1:05d}' for i in range(G)])
            for row, (donor, als, l2, parts) in zip(rows, rowinfo):
                m = np.zeros(G)
                for t, lib_t in parts:
                    if (donor, t) not in gam2:
                        gam2[(donor, t)] = r2.gamma(10.0, 0.1, G)
                    m += mu2[t] * lib_t * 2 ** (l2 + (eff2 if als else 0.0)) * gam2[(donor, t)]
                w.writerow(row[:2] + row[4:] + [int(x) for x in r2.poisson(m)])
    for name, rr in (('donors.csv', donors), ('samples.csv', samples)):
        cols = list(dict.fromkeys(k for r in rr for k in r))
        with open(out / name, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rr)
    sheet = dict(cohort_name='made-up cohort (self-test)', region='BA9', brain_banks=['Made-up Bank'],
                 sporadic_definition='made up', c9orf72_testing='made up', doublet_handling='source doublet-filtered',
                 independence_basis='different bank, IDs not matched', any_donor_from_mayo_clinic_jacksonville='no',
                 interleaving_statement='', labels_doublet_or_low_quality=['cohort_doublet'],
                 assay='single-nucleus RNA-seq', chemistry='made-up kit, version 1')
    (out / 'cohort_sheet.json').write_text(json.dumps(sheet, indent=1))
    return out
