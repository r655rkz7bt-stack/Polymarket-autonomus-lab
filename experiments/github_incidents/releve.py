"""Incidents de githubstatus.com par mois (page /history.json, autorisée par robots.txt ; /api/ est interdit aux robots : jamais
utilisé par script). Usage : releve.py <pages> → donnees/history.json (liste brute des mois)."""
import json, sys, time, requests
from pathlib import Path
out = []
for page in range(1, int(sys.argv[1]) + 1):
    r = requests.get("https://www.githubstatus.com/history.json", params={"page": page}, headers={"User-Agent": "curl/8"}, timeout=30)
    if r.status_code != 200: print(page, r.status_code); break
    d = r.json()
    months = d.get("months") or []
    if not months: break
    out += months
    print(page, [m.get("name") for m in months][:3], sum(len(m.get("incidents") or []) for m in months), flush=True)
    time.sleep(1.0)
Path("donnees").mkdir(exist_ok=True)
json.dump(out, open("donnees/history.json", "w"))
