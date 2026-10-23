"""Sonde : quels types de marchés (Gamma `sportsMarketType`) existent dans les événements de tennis réglés ?
Usage (depuis la racine du dépôt) : python experiments/tennis_sets_coherence/sonde_types.py [pages]"""
import collections
import json
import sys

import requests

S = requests.Session()
S.headers["User-Agent"] = "polymarket-autonomous-lab"
SERIES = {"atp": 10365, "wta": 10366, "itf": 11634}
PAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 1
for nom, sid in SERIES.items():
    compte, exemple, n_ev, dernier = collections.Counter(), {}, 0, None
    for page in range(PAGES):
        d = S.get("https://gamma-api.polymarket.com/events", params={"closed": "true", "limit": 100, "offset": 100 * page,
                  "series_id": sid, "order": "endDate", "ascending": "false"}, timeout=60).json()
        if not isinstance(d, list) or not d:
            break
        n_ev += len(d)
        dernier = d[-1].get("endDate")
        for e in d:
            for m in e.get("markets") or []:
                t = m.get("sportsMarketType")
                compte[t] += 1
                exemple.setdefault(t, (e["slug"], m.get("question"), m.get("outcomes"), round(m.get("volumeNum") or 0)))
    print(nom, "événements", n_ev, "jusqu'au", dernier, json.dumps(dict(compte)))
    for k, v in exemple.items():
        print("   ", k, v)
