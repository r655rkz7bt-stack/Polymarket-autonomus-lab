"""Famille 4 (25/10 soir) : les achats respectent-ils les fenêtres de temps du filtre (echeance_min/max en heures, heure_utc) ?
Compare `horizon_hours` (journal) aux filtres de config/strategies.yaml, achat par achat (premier achat de chaque jeton)."""
import glob, os, sys, json, collections
import yaml
sys.path.insert(0, os.path.dirname(__file__))
cfg = yaml.safe_load(open('config/strategies.yaml'))
tot = collections.Counter(); mal = collections.defaultdict(list)
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    nom = os.path.basename(f)[:-6].rsplit('_v', 1)[0]
    flt = (cfg.get(nom) or {}).get('filtres') or {}
    lo, hi = flt.get('echeance_min'), flt.get('echeance_max')
    hr = flt.get('heure_utc')
    if lo is None and hi is None and not hr: continue
    vus = set()
    for l in open(f):
        x = json.loads(l)
        if x['type'] != 'BUY': continue
        d = x['data']
        if d['token_id'] in vus: continue
        vus.add(d['token_id'])
        h = float(d['extra'].get('horizon_hours', 'nan'))
        tot[nom] += 1
        # l'achat peut venir plusieurs minutes après le signal : tolérance 0,5 h
        if lo is not None and h < lo / 60 - 0.5 if False else False: pass
        bad = []
        if lo is not None and h < lo - 0.5: bad.append(f'h {h:.1f} < min {lo}')
        if hi is not None and h > hi + 0.5: bad.append(f'h {h:.1f} > max {hi}')
        if hr:
            hh = int(x['ts'][11:13])
            if not (hr[0] <= hh < hr[1] or hr[0] <= hh <= hr[1]): bad.append(f'heure {hh} hors {hr}')
        if bad: mal[nom].append((x['ts'][:16], d['market_id'], bad[0]))
print(sum(tot.values()), 'premiers achats contrôlés,', len(tot), 'stratégies avec fenêtre')
for n, v in sorted(mal.items(), key=lambda kv: -len(kv[1])):
    print(n, f'{len(v)}/{tot[n]}', v[:2])
