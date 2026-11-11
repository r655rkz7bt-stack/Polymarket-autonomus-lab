"""11/11/2026 : vrais échanges (data-api v2) des marchés pays réglés de septembre et octobre 2026. Pour chaque marché : achats du NON
par des preneurs (côté BUY sur le jeton NON, ou SELL du OUI = NON à 1 − prix) aux jours 1 à 25, prix payé, issue, fréquence de base.
Usage : PYTHONPATH=src .venv/bin/python experiments/seismes_pays/echanges.py"""
import json, math, datetime as dt, collections, requests
from polymarket_agent.http_client import HttpClient
from polymarket_agent import data_api
http = HttpClient()
UA = {"User-Agent": "curl/8"}
rel = json.load(open("experiments/seismes_pays/releve.json"))
base = {(r["evt"], r["pays"], r["jour"]): r["base"] for r in rel}
EVENTS = {"1108757": (2026, 10), "944677": (2026, 9)}
rows = []
for eid, (y, mo) in EVENTS.items():
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=UA, timeout=30).json()
    start = dt.datetime(y, mo, 1, 4, tzinfo=dt.timezone.utc)
    tr = data_api.echanges_evenement(http, eid, pages=20)
    print(eid, "échanges", len(tr))
    cond = {m["conditionId"]: m for m in e["markets"]}
    for t in tr:
        m = cond.get(t.get("conditionId"))
        if not m:
            continue
        res = json.loads(m["outcomePrices"]); toks = json.loads(m["clobTokenIds"])
        is_no = str(t.get("asset")) == toks[1]
        side = t.get("side"); px = float(t["price"]); sz = float(t["size"])
        # prix du NON payé par un preneur qui ACHÈTE le NON ; un preneur qui VEND le OUI fournit aussi du NON à 1 − prix (même carnet)
        if is_no and side == "BUY":
            no_px = px
        elif (not is_no) and side == "SELL":
            no_px = 1 - px
        else:
            continue
        ts = dt.datetime.fromtimestamp(int(t["timestamp"]), dt.timezone.utc)
        d = (ts - start).total_seconds() / 86400
        jb = min((1, 5, 10, 15, 20), key=lambda j: abs(j - d))
        rows.append({"evt": eid, "pays": m["groupItemTitle"], "jour": round(d, 2), "no_px": no_px, "parts": sz,
                     "issue_no": float(res[1]), "base_no": round(1 - base.get((eid, m["groupItemTitle"], jb), float("nan")), 3)})
json.dump(rows, open("experiments/seismes_pays/echanges.json", "w"), indent=0)
by = collections.defaultdict(list)
for r in rows:
    by[(r["evt"], r["pays"])].append(r)
tot_c = tot_g = 0
for k, v in sorted(by.items()):
    v.sort(key=lambda r: r["jour"])
    cost = sum(r["no_px"] * r["parts"] for r in v); gain = sum(r["issue_no"] * r["parts"] for r in v) - cost
    print(k, len(v), "achats NON", f"prix moyen {cost / max(1e-9, sum(r['parts'] for r in v)):.3f}", f"parts {sum(r['parts'] for r in v):.0f}",
          f"issue NON {v[0]['issue_no']}", f"gain {gain:+.1f} $", "base NON jour~1:", v[0]["base_no"])
