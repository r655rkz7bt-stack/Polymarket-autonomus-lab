"""Comme presse_gdelt.py, mais pour quelques noms, une requête toutes les 30 s (l'adresse de sortie de la routine
est partagée : GDELT répond souvent 429 même à une requête par 5 s). Usage : presse_lent.py nom1 nom2 …"""
import json, sys, time
from pathlib import Path
import requests

OUT = Path(__file__).resolve().parents[1] / "releves" / "presse_gdelt.json"
for n in sys.argv[1:]:
    for essai in range(4):
        time.sleep(30)
        data = json.loads(OUT.read_text())
        if n in data:
            break
        try:
            r = requests.get("https://api.gdeltproject.org/api/v2/doc/doc", timeout=120, params={
                "query": f'"{n}"', "mode": "timelinevolraw", "format": "json",
                "startdatetime": "20170101000000", "enddatetime": time.strftime("%Y%m%d000000")})
        except requests.RequestException as exc:
            print("erreur", n, type(exc).__name__, flush=True); continue
        if r.text.startswith("{"):
            tl = r.json().get("timeline") or []
            data[n] = {x["date"][:8]: x["value"] for x in (tl[0]["data"] if tl else [])}
            OUT.write_text(json.dumps(data)); print("ok", n, sum(data[n].values()), flush=True); break
        print("refus", n, r.status_code, flush=True)
