"""Piste 1 de PISTES.md (25/10/2026, nuit) : champions de saison, Polymarket contre Pinnacle (cotes de champion de The Odds API, source `odds_outrights`).
Photo du jour : marchés « Will the X win the 2027 NBA Finals / Stanley Cup / Super Bowl ? » rattachés à la cote de l'équipe (references.attach_outrights),
écart prix - cote, par tranche de cote. Pas d'historique de cotes gratuit : la piste ne peut se juger que par un fantôme (futurs_bookmakers)."""
import sys, json, gzip, datetime as dt, requests
sys.path.insert(0, 'src')
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent import references
from polymarket_agent.persistence import Database
H = {'User-Agent': 'curl/8'}
db = Database(sys.argv[1])           # copie de la sauvegarde publiée (published_data/backup/essentiel.sqlite.gz décompressée)
seen = {}
for q in ['2027 NBA Finals', 'Stanley Cup', 'Super Bowl', 'NBA Champion 2027', 'NHL champion 2027', 'Super Bowl LXI']:
    r = requests.get('https://gamma-api.polymarket.com/public-search', params=dict(q=q, events_status='active', limit_per_type=20), headers=H, timeout=30).json()
    for e in r.get('events', []):
        for m in e.get('markets', []):
            if m.get('closed') or not m.get('active'):
                continue
            seen[m['id']] = parse_market(dict(m, events=[{'id': e['id'], 'slug': e['slug'], 'title': e['title']}]))
ms = list(seen.values())
print(len(ms), 'marchés lus ;', references.attach_outrights(ms, db), 'rattachés à une cote')
rows = []
for m in ms:
    o = (m.references or {}).get('outright')
    if o and m.outcome_prices:
        rows.append((m.question, float(o['p']), float(m.outcome_prices[0]), m.end_date))
bandes = [(0, .02), (.02, .05), (.05, .10), (.10, .25), (.25, 1)]
print('tranche de cote Pinnacle : n, prix moyen, cote moyenne, écart moyen (prix - cote), plus gros écart')
for lo, hi in bandes:
    L = [r for r in rows if lo <= r[1] < hi]
    if L:
        print(f'{lo:.2f}-{hi:.2f} : {len(L):3d}  {sum(r[2] for r in L)/len(L):.4f}  {sum(r[1] for r in L)/len(L):.4f}  {sum(r[2]-r[1] for r in L)/len(L):+.4f}  {max(abs(r[2]-r[1]) for r in L):.3f}')
big = sorted(rows, key=lambda r: -abs(r[2] - r[1]))[:5]
for q, p, y, e in big:
    print(f'{q[:58]:58s} cote {p:.3f} prix {y:.3f} fin {e.date() if e else None}')
fin = [r[3] for r in rows if r[3]]
print('échéance médiane des marchés rattachés :', sorted(fin)[len(fin)//2].date() if fin else None)
