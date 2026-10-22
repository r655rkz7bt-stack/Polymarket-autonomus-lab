"""Piste n° 10 (queues de tranches) : événements à tranches réglés (≥ 4 marchés binaires), Gamma.
Un marché par ligne : prix final, jetons, volume, barème de frais. -> donnees/evenements.json (ignoré par Git)."""
import json, sys, datetime as dt, requests, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
start = dt.date.fromisoformat(sys.argv[1]); end = dt.date.fromisoformat(sys.argv[2])
step = dt.timedelta(days=int(sys.argv[3]) if len(sys.argv) > 3 else 2)
wins = []
d = start
while d < end:
    wins.append((d, min(d + step, end))); d += step

def window(w):
    out = []
    for page in range(60):
        r = requests.get("https://gamma-api.polymarket.com/events", headers=H, timeout=60, params={
            "closed": "true", "limit": 100, "offset": page * 100,
            "end_date_min": f"{w[0]}T00:00:00Z", "end_date_max": f"{w[1]}T00:00:00Z"})
        b = r.json() if r.status_code == 200 else []
        if not isinstance(b, list) or not b:
            break
        for ev in b:
            ms = ev.get("markets") or []
            rows = []
            for m in ms:
                try:
                    toks = json.loads(m.get("clobTokenIds") or "[]"); pr = json.loads(m.get("outcomePrices") or "[]")
                except ValueError:
                    continue
                if len(toks) != 2 or len(pr) != 2:
                    continue
                rows.append(dict(id=m["id"], q=m.get("question", ""), item=m.get("groupItemTitle"), yes=toks[0], no=toks[1],
                                 final=float(pr[0]), uma=m.get("umaResolutionStatus"), vol=float(m.get("volume") or 0),
                                 end=m.get("endDate"), closed=m.get("closedTime"), fs=m.get("feeSchedule"), fees=m.get("feesEnabled"),
                                 neg=m.get("negRisk"), tick=m.get("orderPriceMinTickSize"), start=m.get("startDate")))
            if len(rows) >= 4:
                out.append(dict(id=ev["id"], slug=ev.get("slug"), title=ev.get("title"), end=ev.get("endDate"), neg=ev.get("negRisk"),
                                tags=[t.get("slug") for t in ev.get("tags") or []], markets=rows))
        if len(b) < 100:
            break
    return out

allev = {}
with cf.ThreadPoolExecutor(6) as ex:
    for res in ex.map(window, wins):
        for e in res:
            allev[e["id"]] = e
json.dump(list(allev.values()), open("experiments/queues_tranches/donnees/evenements.json", "w"))
print(len(allev), "événements,", sum(len(e["markets"]) for e in allev.values()), "marchés")
