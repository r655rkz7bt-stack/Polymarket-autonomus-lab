"""Piste n° 69 : METAR (précipitation horaire p01i, rapports de routine et spéciaux) et CLI (précipitation du jour climatique)
des stations des marchés « Where will it rain », lus sur l'Iowa Environmental Mesonet (robots.txt : permis, 17/11/2026).
Une requête par station, 2 s entre deux appels. Sortie : donnees/metar_<STATION>.csv, donnees/cli_<STATION>.json."""
import time
from pathlib import Path

import requests

D = Path(__file__).parent / "donnees"
S = requests.Session()
S.headers["User-Agent"] = "curl/8"
STATIONS = ["LAX", "IAH", "DFW", "PHX", "PHL", "DCA", "ATL", "MIA", "MSY", "SFO", "NYC", "MDW", "SEA", "BOS", "DEN"]

for st in STATIONS:
    f = D / f"metar_{st}.csv"
    if not f.exists():
        r = S.get("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py", params=[
            ("station", st), ("data", "p01i"), ("year1", 2026), ("month1", 5), ("day1", 25), ("year2", 2026), ("month2", 11),
            ("day2", 18), ("tz", "Etc/UTC"), ("format", "onlycomma"), ("latlon", "no"), ("missing", "M"), ("trace", "T"),
            ("direct", "no"), ("report_type", "3"), ("report_type", "4")], timeout=120)
        r.raise_for_status()
        f.write_text(r.text)
        time.sleep(2)
    g = D / f"cli_{st}.json"
    if not g.exists():
        r = S.get("https://mesonet.agron.iastate.edu/json/cli.py", params={"station": "K" + st, "year": 2026}, timeout=60)
        r.raise_for_status()
        g.write_text(r.text)
        time.sleep(2)
    print(st, f.stat().st_size, g.stat().st_size, flush=True)
