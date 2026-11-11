"""11/11/2026 : marchés « Where will a 6.0+ magnitude earthquake occur by end of <mois> ? » réglés (septembre, octobre 2026) :
prix horaire (prices-history) à J+1, J+5, J+10, J+15, J+20 du mois, issue, fréquence de base USGS (2000-2025, jours avec un M6+ dont
la description contient le pays) pour les jours restants. Usage : .venv/bin/python experiments/seismes_pays/releve.py"""
import json, math, datetime as dt, requests
UA = {"User-Agent": "curl/8"}
EVENTS = {"1108757": (2026, 10), "944677": (2026, 9)}
KEYS = {"Indonesia": ["Indonesia"], "Japan": ["Japan"], "Chile": ["Chile"], "Mexico": ["Mexico"], "Philippines": ["Philippines"],
        "Peru": ["Peru"], "United States": ["Alaska", "California", ", CA", "Hawaii", "Oregon", "Washington", "Nevada", "Idaho", "Montana",
                                          "Utah", "Wyoming", "Puerto Rico"]}
cat = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query", params={"format": "geojson", "minmagnitude": 5.95,
                   "starttime": "2000-01-01", "endtime": "2026-01-01", "limit": 20000}, timeout=120).json()
ev = [(dt.datetime.utcfromtimestamp(f["properties"]["time"] / 1000), f["properties"]["place"] or "") for f in cat["features"]
      if f["properties"]["mag"] is not None and round(f["properties"]["mag"] + 1e-9, 1) >= 6.0]
def rate_days(c):  # jours avec au moins un M6+ attribué au pays, par jour
    return len({t.date() for t, p in ev if any(k in p for k in KEYS.get(c, [c]))}) / (26 * 365.25)
out = []
for eid, (y, mo) in EVENTS.items():
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=UA, timeout=30).json()
    start = dt.datetime(y, mo, 1, 4, tzinfo=dt.timezone.utc)
    end = dt.datetime(y + (mo == 12), mo % 12 + 1, 1, 5, tzinfo=dt.timezone.utc)
    for m in e["markets"]:
        c = m.get("groupItemTitle"); tok = json.loads(m["clobTokenIds"])[0]
        res = json.loads(m.get("outcomePrices") or "[]")
        h, a = [], start
        while a < end:  # prices-history refuse les fenêtres de plus de ~14 jours
            b = min(a + dt.timedelta(days=12), end)
            h += requests.get("https://clob.polymarket.com/prices-history", params={"market": tok, "startTs": int(a.timestamp()),
                              "endTs": int(b.timestamp()), "fidelity": 60}, headers=UA, timeout=30).json().get("history", [])
            a = b
        for d in (1, 5, 10, 15, 20):
            T = start + dt.timedelta(days=d)
            before = [x["p"] for x in h if x["t"] <= T.timestamp()]
            if not before:
                continue
            left = (end - T).total_seconds() / 86400
            # le pays a-t-il déjà eu son séisme avant T ? (on ne joue que les marchés encore ouverts : prix < 0,97)
            p_base = 1 - math.exp(-rate_days(c) * left)
            out.append({"evt": eid, "pays": c, "jour": d, "prix": before[-1], "base": round(p_base, 3), "issue": float(res[0]) if res else None})
json.dump(out, open("experiments/seismes_pays/releve.json", "w"), indent=0)
for r in out:
    print(r)
