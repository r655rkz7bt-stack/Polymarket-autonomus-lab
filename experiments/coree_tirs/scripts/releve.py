"""Piste n° 64 (15/11/2026) : « Number of North Korea Missile Tests in <mois> 2026 » — tranche réglée et prix de chaque
tranche au 8, au 15 et au 22 du mois (prices-history du CLOB, fidelity 60, dernière barre FINIE avant l'instant)."""
import json, sys, datetime as dt, requests
H = {"User-Agent": "curl/8"}
G = "https://gamma-api.polymarket.com"
ids = set()
for page in range(1, 4):
    r = requests.get(f"{G}/public-search", params={"q": "Number of North Korea Missile Tests", "events_status": "closed",
                     "limit_per_type": 50, "page": page}, headers=H, timeout=30).json()
    for e in r.get("events") or []:
        if e["title"].startswith("Number of North Korea"):
            ids.add(e["id"])
    if len(r.get("events") or []) < 50:
        break
out = []
for eid in sorted(ids):
    e = requests.get(f"{G}/events/{eid}", headers=H, timeout=30).json()
    end = dt.datetime.fromisoformat(e["endDate"].replace("Z", "+00:00"))
    month0 = (end - dt.timedelta(days=2)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    rows = []
    for m in e["markets"]:
        prices = json.loads(m.get("outcomePrices") or "[]")
        tok = json.loads(m["clobTokenIds"])[0]
        snap = {}
        for day in (8, 15, 22):
            T = month0.replace(day=day)
            h = requests.get("https://clob.polymarket.com/prices-history", params={"market": tok, "startTs": int((T - dt.timedelta(days=3)).timestamp()),
                             "endTs": int(T.timestamp()), "fidelity": 60}, timeout=30).json().get("history") or []
            h = [x for x in h if x["t"] <= T.timestamp() - 3600]
            snap[day] = h[-1]["p"] if h else None
        rows.append({"tranche": m.get("groupItemTitle"), "paye": float(prices[0]) if prices else None, "prix": snap,
                     "volume": float(m.get("volumeNum") or 0)})
    out.append({"id": eid, "titre": e["title"], "fin": e["endDate"], "tranches": rows})
    print(e["title"], [(r["tranche"], r["paye"], r["prix"]) for r in rows])
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "releve.json", "w"), indent=1)
