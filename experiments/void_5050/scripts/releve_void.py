"""Part des marchés de match réglés à 50-50, par sport (24/10/2026). Sortie : experiments/void_5050/releve.json.gz"""
import requests, json, gzip, sys, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
s = requests.get("https://gamma-api.polymarket.com/sports", headers=H, timeout=30).json()
series = [(x["sport"], x["series"]) for x in s if x.get("series")]
def une(sp_ser, pages=6):
    sp, ser = sp_ser
    out = []
    for p in range(pages):
        try:
            r = requests.get("https://gamma-api.polymarket.com/events", headers=H, timeout=40,
                params=dict(series_id=ser, closed="true", order="endDate", ascending="false", limit=100, offset=p*100))
            ev = r.json()
        except Exception:
            break
        if not isinstance(ev, list) or not ev: break
        for e in ev:
            for m in (e.get("markets") or []):
                if m.get("sportsMarketType") not in ("moneyline", "child_moneyline", "totals", "spreads"): continue
                out.append(dict(sp=sp, t=m["sportsMarketType"], q=m.get("question"), op=m.get("outcomePrices"), vol=m.get("volumeNum"), end=m.get("closedTime")))
        if len(ev) < 100: break
    return out
with cf.ThreadPoolExecutor(6) as ex:
    res = [x for r in ex.map(une, series) for x in r]
json.dump(res, gzip.open("experiments/void_5050/releve.json.gz", "wt"))
print(len(res), "marchés", len(series), "séries")
