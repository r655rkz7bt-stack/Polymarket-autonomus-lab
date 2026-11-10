"""Cases de l'agenda (voyage, heure du dernier rendez-vous) contre « lid avant 18 h 30 », par moitié de période (10/11/2026).
Entrée : donnees/cal.json = https://media-cdn.factba.se/rss/json/trump/calendar-full.json (lien public donné par rollcall.com/factbase/trump/calendar/)."""
import json, collections
rows = json.load(open('donnees/cal.json'))
days = collections.defaultdict(list)
for r in rows:
    days[r['date']].append(r)

def first_lid(d):
    ls = sorted(r['time'] for r in days.get(d, []) if 'travel/photo lid called' in (r['details'] or '').lower() and r['time']
                and r['time'] >= '06:00:00' and 'local' not in (r['details'] or '').lower())
    return ls[0] if ls else None

T = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for d in sorted(days):
    if d < '2025-03-01' or d >= '2026-11-10':
        continue
    sch = [r for r in days[d] if r['type'] == 'President Schedule']
    if not sch:
        continue
    f = first_lid(d); y = f is not None and f <= '18:30:00'
    txt = ' '.join((r['details'] or '').lower() for r in sch)
    last = max([r['time'] for r in sch if r['time']] or ['00:00:00'])
    v = 'voyage' if ('departs' in txt or 'arrives' in txt) else 'sans voyage'
    l = '>=17h' if last >= '17:00:00' else '<17h'
    per = 'A 2025' if d < '2026-01-01' else 'B 2026'
    for p in [per, 'tout']:
        T[(v, l)][p][0] += y; T[(v, l)][p][1] += 1
for k, v in sorted(T.items()):
    print(k, {p: f'{a}/{b}={a/b:.2f}' for p, (a, b) in sorted(v.items())})
