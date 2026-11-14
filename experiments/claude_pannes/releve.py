"""Relevé des cases quotidiennes de claude.ai sur status.claude.com/uptime (robots.txt : permis, relu le 14/11/2026).
Une page = 3 mois ; ?page=N remonte le temps. Écrit releves/jours.csv (date, couleur, p, m, événements)."""
import html, json, re, sys, time, csv, requests
H = {'User-Agent': 'curl/8'}
rows = {}
for page in range(1, int(sys.argv[1]) if len(sys.argv) > 1 else 13):
    s = requests.get(f'https://status.claude.com/uptime/rwppv331jlwc?page={page}', headers=H, timeout=30).text
    m = re.search(r'data-react-props="([^"]+)"', s)
    if not m:
        print('page', page, 'sans données'); break
    d = json.loads(html.unescape(m.group(1)))
    for mo in d['months']:
        for x in mo['days']:
            if 'date' in x:
                rows[x['date'][:10]] = (x['color'], x.get('p', 0), x.get('m', 0), ' | '.join(e['name'] for e in x.get('events') or []))
    print('page', page, [f"{mo['name']} {mo['year']}" for mo in d['months']])
    time.sleep(1.5)
with open(__import__('os').path.join(__import__('os').path.dirname(__file__), 'releves', 'jours.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'couleur', 'p', 'm', 'evenements'])
    for k in sorted(rows): w.writerow([k, *rows[k]])
print(len(rows), 'jours')
