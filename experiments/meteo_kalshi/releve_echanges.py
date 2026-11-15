"""Piste n° 62 : vrais échanges (data-api v2, filtre `condition`) des tranches Polymarket depuis le 14/09/2026.
-> donnees/echanges.json {condition: [[ts, côté, issue, prix, parts], ...]}."""
import json, time, requests, concurrent.futures as cf
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
conds = sorted({m["cond"] for e in json.load(open("donnees/poly_events.json")) if (e["fin"] or "") >= "2026-09-14" for m in e["marches"] if m.get("cond")})
print(len(conds), "marchés", flush=True)
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
    res = dict(ex.map(one, conds))
json.dump(res, open("donnees/echanges.json", "w"))
print(sum(len(v) for v in res.values()), "échanges ;", sum(1 for v in res.values() if v), "marchés avec échanges")
