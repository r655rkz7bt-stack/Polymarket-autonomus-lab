"""Jours non verts du composant claude.ai sur status.claude.com/uptime (calendrier embarqué dans la page, sans clé),
arbitre du marché « Will Claude go down on __ days in <mois>? ». Pages : ?page=1 (3 derniers mois), 2, 3…
Sortie : releves/jours.json {AAAA-MM-JJ: couleur} et nombre de jours non verts par mois."""
import json, re, html, time, collections
from pathlib import Path
import requests

OUT = Path(__file__).resolve().parent / "releves"
OUT.mkdir(exist_ok=True)
jours = {}
for page in range(1, 9):
    t = requests.get(f"https://status.claude.com/uptime/rwppv331jlwc?page={page}", headers={"User-Agent": "Mozilla/5.0"}, timeout=60).text
    m = re.search(r'data-react-props="([^"]*)"\s*data-react-class="UptimeCalendar"', t) or re.search(r'data-react-class="UptimeCalendar"\s*data-react-props="([^"]*)"', t)
    if not m:
        break
    d = json.loads(html.unescape(m.group(1)))
    for mo in d["months"]:
        for x in mo["days"]:
            if x.get("date"):
                jours[x["date"][:10]] = x["color"]
    time.sleep(1)
(OUT / "jours.json").write_text(json.dumps(jours, indent=0, sort_keys=True))
par_mois = collections.defaultdict(lambda: [0, 0])
for j, c in jours.items():
    par_mois[j[:7]][0] += c.lower() != "#76ad2a"
    par_mois[j[:7]][1] += 1
for k in sorted(par_mois):
    print(k, "non verts", par_mois[k][0], "sur", par_mois[k][1])
