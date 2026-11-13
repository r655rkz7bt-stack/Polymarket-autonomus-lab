"""Échelle « Will the 30-year Mortgage Rate hit __ in 2026? » (événement 197683) : marchés, issue, prix horaires du CLOB (tranches de
14 jours), relevé Freddie Mac (PMMS_history.csv, /pmms/docs/ permis par robots.txt) et clôtures du 10 ans (CSV du Trésor).
À lancer depuis experiments/taux_immobilier/ : écrit donnees/marches.json, donnees/prix.json, donnees/pmms.csv, donnees/dix_ans.json."""
import json, sys, time, requests
from datetime import datetime, timezone
sys.path.insert(0, "../../src")
from polymarket_agent.taux_tresor import parse_csv, CSV
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
e = S.get("https://gamma-api.polymarket.com/events/197683", timeout=30).json()
ms = []
for m in e["markets"]:
    toks = json.loads(m["clobTokenIds"]); pr = json.loads(m["outcomePrices"])
    ms.append({"id": m["id"], "q": m["question"], "tok": toks[0], "closed": bool(m.get("closed")), "won": (1 if pr[0] == "1" else 0) if m.get("closed") else None,
               "created": m.get("createdAt"), "closedTime": m.get("closedTime"), "fee": m.get("feeType")})
json.dump(ms, open("donnees/marches.json", "w"), indent=1)
now = int(time.time()); prix = {}
for m in ms:
    a = int(datetime.fromisoformat(m["created"].replace("Z", "+00:00")).timestamp())
    end = int(datetime.fromisoformat(m["closedTime"].replace(" ", "T").replace("+00", "+00:00")).timestamp()) + 3600 if m["closedTime"] else now
    h = []
    while a < end:
        b = min(a + 13 * 86400, end)
        r = S.get("https://clob.polymarket.com/prices-history", params={"market": m["tok"], "startTs": a, "endTs": b, "fidelity": 60}, timeout=40).json()
        h += [[p["t"], p["p"]] for p in r.get("history") or []]
        a = b
    prix[m["id"]] = h
    print(m["q"], m["won"], len(h), flush=True)
json.dump(prix, open("donnees/prix.json", "w"))
open("donnees/pmms.csv", "w").write(requests.get("https://www.freddiemac.com/pmms/docs/PMMS_history.csv", headers={"User-Agent": "Mozilla/5.0"}, timeout=60).text)
ten = {}
for y in (2025, 2026):
    for d, v in parse_csv(requests.get(CSV.format(y=y), headers={"User-Agent": "Mozilla/5.0"}, timeout=60).text)[10]:
        ten[d] = v
json.dump(ten, open("donnees/dix_ans.json", "w"))
