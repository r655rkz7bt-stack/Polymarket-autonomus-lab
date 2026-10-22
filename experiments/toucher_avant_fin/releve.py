"""Piste n° 2 (toucher_avant_fin) : événements Bitcoin/Ethereum « touche X » et « au-dessus de X » réglés, Gamma.
-> donnees/evenements.json (ignoré par Git). Usage : releve.py 2026-04-01 2026-10-23"""
import json, sys, re, datetime as dt, requests, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
start = dt.date.fromisoformat(sys.argv[1]); end = dt.date.fromisoformat(sys.argv[2])
wins = []; d = start
while d < end:
    wins.append((d, min(d + dt.timedelta(days=3), end))); d += dt.timedelta(days=3)
PAT = re.compile(r"(bitcoin|ethereum|btc|eth)-(hit|above|multi|price)|what-price-will|hit-price|reach", re.I)
def window(w):
    out = []
    for page in range(80):
        r = None
        for _ in range(3):
            try:
                r = requests.get("https://gamma-api.polymarket.com/events", headers=H, timeout=60, params={
                    "closed": "true", "limit": 100, "offset": page * 100,
                    "end_date_min": f"{w[0]}T00:00:00Z", "end_date_max": f"{w[1]}T00:00:00Z"})
                if r.status_code == 200: break
            except requests.RequestException: pass
        b = r.json() if r is not None and r.status_code == 200 else []
        if not isinstance(b, list) or not b: break
        for ev in b:
            s = ev.get("slug", "")
            if not (re.search(r"bitcoin|ethereum|btc|eth|solana", s) and re.search(r"hit|above|multi-strikes|price|reach", s)) or "updown" in s: continue
            ms = []
            for m in ev.get("markets") or []:
                try: toks = json.loads(m.get("clobTokenIds") or "[]"); pr = json.loads(m.get("outcomePrices") or "[]")
                except ValueError: continue
                if len(toks) != 2 or len(pr) != 2: continue
                ms.append(dict(id=m["id"], q=m.get("question"), item=m.get("groupItemTitle"), yes=toks[0], no=toks[1], final=float(pr[0]),
                               vol=float(m.get("volume") or 0), end=m.get("endDate"), closed=m.get("closedTime"), start=m.get("startDate")))
            out.append(dict(id=ev["id"], slug=s, title=ev.get("title"), end=ev.get("endDate"), markets=ms))
        if len(b) < 100: break
    return out
allev = {}
with cf.ThreadPoolExecutor(6) as ex:
    for res in ex.map(window, wins):
        for e in res: allev[e["id"]] = e
json.dump(list(allev.values()), open("experiments/toucher_avant_fin/donnees/evenements.json", "w"))
import collections
c = collections.Counter(re.sub(r"\d+|january|february|march|april|may|june|july|august|september|october|november|december", "#", e["slug"]) for e in allev.values())
print(len(allev), "événements"); print(c.most_common(25))
