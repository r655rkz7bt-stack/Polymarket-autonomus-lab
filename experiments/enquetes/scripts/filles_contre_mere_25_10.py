"""Famille 5 (25/10) : les filles battent-elles le RESTE de leur mère sur la même période, en moyenne ?
Fille = paris réglés d'une stratégie à `mere` ; reste = paris réglés de la mère achetés depuis le 1er achat de la fille, sur des jetons que la fille n'a pas joués.
Rendement = gain / mise, pondéré par les mises ; différence fille − reste ; moyenne et écart-type de ces différences sur toutes les filles (n ≥ 10 paris)."""
import glob, math, os, statistics, sys
import yaml
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger

cfg = yaml.safe_load(open('config/strategies.yaml'))
res = []
for nom, c in cfg.items():
    if not isinstance(c, dict) or not c.get('mere'):
        continue
    fm = glob.glob(f"published_data/ledger/fantome/{nom}_v*.jsonl")
    mm = glob.glob(f"published_data/ledger/fantome/{c['mere']}_v*.jsonl")
    if not fm or not mm:
        continue
    f, m = charger(fm[0]), charger(mm[0])
    if len(f) < 10:
        continue
    t0 = min(p['ts'] for p in f)
    tokf = {p['token'] for p in f}
    reste = [p for p in m if p['ts'] >= t0 and p['token'] not in tokf]
    if len(reste) < 10:
        continue
    rf = float(sum(p['gain'] for p in f) / sum(p['mise'] for p in f))
    rr = float(sum(p['gain'] for p in reste) / sum(p['mise'] for p in reste))
    res.append((rf - rr, nom, len(f), len(reste), rf, rr, c.get('created_at')))
res.sort(reverse=True)
for d, nom, nf, nr, rf, rr, ca in res:
    print(f"{nom[:44]:44} fille {nf:3d} paris {100*rf:+6.1f} %   reste de la mère {nr:3d} paris {100*rr:+6.1f} %   écart {100*d:+6.1f}")
ds = [r[0] for r in res]
moy = statistics.mean(ds); sd = statistics.stdev(ds)
print(f"\n{len(ds)} filles ; écart moyen {100*moy:+.2f} points ; écart-type {100*sd:.1f} ; t = {moy/(sd/math.sqrt(len(ds))):.2f} ; filles meilleures que le reste : {sum(1 for d in ds if d>0)}")
