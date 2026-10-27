"""27/10/2026 famille 4 : `heures_min/heures_max` = heures AVANT le coup d'envoi (Gamma gameStartTime). Le journal garde
`depuis_coup_d_envoi_h` (négatif = avant) depuis le 20/10 : un achat à h heures du coup d'envoi a depuis = -h.
Vérifie, achat par achat (ordres posés : tolérance de leur durée), que le filtre est respecté."""
import glob, os, json, collections, yaml
cfg = yaml.safe_load(open('config/strategies.yaml'))
tot, mal, sans = collections.Counter(), collections.defaultdict(list), collections.Counter()
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    nom = os.path.basename(f)[:-6].rsplit('_v', 1)[0]
    flt = (cfg.get(nom) or {}).get('filtres') or {}
    lo, hi = flt.get('heures_min'), flt.get('heures_max')
    if lo is None and hi is None: continue
    vus = set()
    for l in open(f):
        x = json.loads(l)
        if x['type'] != 'BUY' or x['data']['token_id'] in vus: continue
        vus.add(x['data']['token_id']); d = x['data']; e = d.get('extra') or {}
        if 'depuis_coup_d_envoi_h' not in e: sans[nom] += 1; continue
        h = -float(e['depuis_coup_d_envoi_h']); tot[nom] += 1
        poseeserv = e.get('order_type') == 'limite' or e.get('resting_order')
        tol = 6.0 if poseeserv else 0.5
        bad = None
        if lo is not None and h < lo - tol: bad = f'{h:.1f} h avant < min {lo}'
        if hi is not None and h > hi + tol: bad = f'{h:.1f} h avant > max {hi}'
        if bad: mal[nom].append((x['ts'][:16], d['market_id'], bad, 'posé' if poseeserv else 'immédiat'))
print(sum(tot.values()), 'premiers achats contrôlés,', len(tot), 'stratégies ; sans coup d\'envoi journalisé :', sum(sans.values()))
for n, v in sorted(mal.items(), key=lambda kv: -len(kv[1])):
    print(n, f'{len(v)}/{tot[n]}', v[:3])
