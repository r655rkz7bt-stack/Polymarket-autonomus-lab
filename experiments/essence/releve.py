"""Piste « prix de l'essence AAA, au jour près » : relevé des marchés Polymarket « Gas prices on <date> ? » (tranches de 1 cent du prix moyen
américain publié par AAA ; AAA lui-même est inaccessible depuis la routine, 403) : tranche gagnante de chaque jour réglé + prix de chaque tranche
à 12 h et 24 h avant la fin. Ajoute à experiments/essence/releve.csv (une ligne par jour, versionné) : relancer à chaque passage pour allonger l'historique."""
import csv, json, re, os, bisect, datetime as dt, requests
H = {'User-Agent': 'curl/8'}
OUT = 'experiments/essence/releve.csv'
done = {r['date'] for r in csv.DictReader(open(OUT))} if os.path.exists(OUT) else set()
seen = {}
for q in ['Gas prices on October', 'Gas prices on September', 'Gas prices on November', 'Average US gas prices', 'Gas prices on']:
    for pg in (1, 2, 3):
        r = requests.get('https://gamma-api.polymarket.com/public-search', params={'q': q, 'limit_per_type': 50, 'page': pg, 'events_status': 'closed'}, headers=H, timeout=30)
        if r.status_code != 200: break
        for e in r.json().get('events', []):
            if re.match(r'^(Gas prices on|Average US gas prices on) [A-Z][a-z]+ \d+\?$', e['title']): seen[e['id']] = e
rows = []
for eid, e in sorted(seen.items(), key=lambda x: x[1].get('endDate') or ''):
    d = (e.get('endDate') or '')[:10]
    if d in done or not e.get('closed'): continue
    full = requests.get(f'https://gamma-api.polymarket.com/events/{eid}', headers=H, timeout=30).json()
    end = int(dt.datetime.fromisoformat(full['endDate'].replace('Z', '+00:00')).timestamp())
    cells = []
    for m in full['markets']:
        try: toks = json.loads(m['clobTokenIds']); yes = float(json.loads(m['outcomePrices'])[0])
        except Exception: continue
        h = requests.get('https://clob.polymarket.com/prices-history', params={'market': toks[0], 'interval': 'max', 'fidelity': 60}, headers=H, timeout=30).json().get('history', [])
        ts = [x['t'] for x in h]
        def at(hours):
            i = bisect.bisect_right(ts, end - hours * 3600) - 1
            return round(h[i]['p'], 3) if i >= 0 and end - hours * 3600 - ts[i] < 8 * 3600 else ''
        cells.append((m.get('groupItemTitle'), yes, at(24), at(12), float(m.get('volume') or 0)))
    win = [c[0] for c in cells if c[1] > .5]
    if not win: continue  # pas encore réglé
    rows.append({'date': d, 'event': eid, 'gagnante': win[0] if win else '', 'tranches': json.dumps([[c[0], c[2], c[3]] for c in cells], ensure_ascii=False), 'volume': round(sum(c[4] for c in cells))})
new = not os.path.exists(OUT)
with open(OUT, 'a', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['date', 'event', 'gagnante', 'tranches', 'volume']); 
    if new: w.writeheader()
    w.writerows(rows)
print(len(rows), 'jours ajoutés', [(r['date'], r['gagnante'], r['volume']) for r in rows])
