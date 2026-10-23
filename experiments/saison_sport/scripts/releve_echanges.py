"""Vrais échanges (data-api, par marché) des candidats à 0,10-0,30 aux horizons 7 et 14 jours : de quoi payer le NON
au prix réellement servi. Écrit donnees/echanges.jsonl {id, h, tok_yes, tok_no, trades:[[t, jeton, côté, prix, parts]]}."""
import json, os, time, requests
from concurrent.futures import ThreadPoolExecutor
ev = {e["id"]: e for e in json.load(open("donnees/evenements.json"))}
mk = {m["id"]: m for e in ev.values() for m in e["markets"]}
def dec(r):
    pts = [p for p in r["hist"] if p[0] <= r["t"]]
    return pts[-1][1] if pts and r["t"] - pts[-1][0] <= 43200 else None
todo = []
for l in open("donnees/prix.jsonl"):
    r = json.loads(l)
    if r["h"] in (7, 14):
        p = dec(r)
        if p is not None and 0.10 <= p < 0.30: todo.append((r["id"], r["h"], r["t"], p))
done = set()
if os.path.exists("donnees/echanges.jsonl"): done = {(x["id"], x["h"]) for x in map(json.loads, open("donnees/echanges.jsonl"))}
todo = [x for x in todo if (x[0], x[1]) not in done]
print("à relever", len(todo), flush=True)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def jget(url, params):
    for k in range(5):
        try:
            r = s.get(url, params=params, timeout=40)
            if r.status_code == 200: return r.json()
        except Exception: pass
        time.sleep(2 ** k)
def get(a):
    mid, h, t, p = a
    g = jget("https://gamma-api.polymarket.com/markets/" + mid, {})
    if not g: return None
    toks = json.loads(g["clobTokenIds"]); out = []
    for page in range(40):
        b = jget("https://data-api.polymarket.com/trades", {"market": g["conditionId"], "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list): return None
        out += [[int(x["timestamp"]), str(x["asset"]), str(x["side"]), float(x["price"]), float(x["size"])] for x in b if t - 3600 <= int(x["timestamp"]) <= t + 12 * 3600]
        if len(b) < 1000 or int(b[-1]["timestamp"]) < t - 3600: break
    return {"id": mid, "h": h, "t": t, "p": p, "tok_yes": toks[0], "tok_no": toks[1], "trades": out}
with open("donnees/echanges.jsonl", "a") as f, ThreadPoolExecutor(6) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 25 == 0: print(i, flush=True)
