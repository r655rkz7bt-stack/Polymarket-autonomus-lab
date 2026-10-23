"""Piste n° 17 (battre_resultats) : « Will <société> beat quarterly earnings? » réglés : issue, prix de la veille (CLOB), vrais échanges.
Recherche par public-search (pages) puis lecture de chaque événement. -> donnees/earnings.json (ignoré par Git)."""
import json, re, requests, datetime as dt, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
def get(url, params):
    for _ in range(3):
        try:
            r = requests.get(url, headers=H, params=params, timeout=60)
            if r.status_code == 200: return r.json()
        except requests.RequestException: pass
slugs = {}
for q in ("beat quarterly earnings", "quarterly earnings gaap eps", "quarterly earnings nongaap eps", "earnings beat", "Will beat quarterly earnings 2026", "beat quarterly earnings 2025"):
    for pg in range(1, 40):
        r = get("https://gamma-api.polymarket.com/public-search", {"q": q, "limit_per_type": 50, "page": pg})
        evs = (r or {}).get("events", [])
        if not evs: break
        for e in evs:
            if "quarterly-earnings" in e["slug"]: slugs[e["id"]] = e["slug"]
print(len(slugs), "événements trouvés")
def one(item):
    eid, slug = item
    e = get("https://gamma-api.polymarket.com/events", {"slug": slug})
    if not e: return None
    e = e[0]; m = e["markets"][0]
    try: toks = json.loads(m["clobTokenIds"]); pr = json.loads(m["outcomePrices"])
    except Exception: return None
    if not e.get("closed") or sorted(pr) != ["0", "1"] or m.get("umaResolutionStatus") not in (None, "", "resolved"): return None
    end = m.get("closedTime") or m.get("endDate")
    h = get("https://clob.polymarket.com/prices-history", {"market": toks[0], "interval": "max", "fidelity": 60}) or {}
    return dict(id=eid, slug=slug, title=e["title"], yes=toks[0], won=int(pr[0] == "1"), end=m.get("endDate"), closed=m.get("closedTime"), vol=float(m.get("volume") or 0),
                fs=m.get("feeSchedule"), fees=m.get("feesEnabled"), hist=[[p["t"], p["p"]] for p in h.get("history", [])], desc=(m.get("description") or "")[:400])
with cf.ThreadPoolExecutor(8) as ex:
    res = [r for r in ex.map(one, slugs.items()) if r]
json.dump(res, open("experiments/battre_resultats/donnees/earnings.json", "w"))
print(len(res), "réglés ;", sum(r["won"] for r in res), "OUI")
