"""Piste n° 61 : vrais échanges (data-api v2, filtre `condition`) des marchés « beat » à OUI 0,25-0,92 à T-7, T-3 ou T-1 j.
-> donnees/echanges.json {condition: [[ts, côté, issue, prix, parts], ...]}."""
import json, sys, time, requests, concurrent.futures as cf
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
conds = set()
for D in (1, 3, 7):
    for c in json.load(open(f"experiments/battre_historique/donnees/cas_T{D}.json")):
        if 0.25 <= c["p"] <= 0.92: conds.add(c["cond"])
print(len(conds), "marchés")
def one(cond):
    out, cur = [], None
    for _ in range(30):
        p = {"condition": cond, "limit": 1000}
        if cur: p["cursor"] = cur
        for i in range(4):
            try:
                r = S.get("https://data-api.polymarket.com/v2/trades", params=p, timeout=60)
                if r.status_code == 200: break
            except requests.RequestException: pass
            time.sleep(1 + 2 * i)
        else: break
        j = r.json(); rows = j.get("data") or []
        out += [[x["timestamp"], x["side"], x["outcome"], x["price"], x["size"]] for x in rows if x.get("condition_id") == cond]
        cur = (j.get("pagination") or {}).get("next_cursor")
        if not rows or not (j.get("pagination") or {}).get("has_more") or not cur: break
    return cond, out
with cf.ThreadPoolExecutor(8) as ex:
    res = dict(ex.map(one, sorted(conds)))
json.dump(res, open("experiments/battre_historique/donnees/echanges.json", "w"))
print(sum(len(v) for v in res.values()), "échanges ;", sum(1 for v in res.values() if v), "marchés avec échanges")
