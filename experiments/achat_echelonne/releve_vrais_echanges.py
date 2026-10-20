"""Vérification aux VRAIS échanges : outsiders de tennis achetés 1 h avant le match."""
import json, time, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import requests
D = "donnees/ech"
rows = [r for r in json.load(open(f"{D}/univers.json")) if len(r["chemin"]) > 30 and r["sport"] in ("itf", "atp", "wta", "cs2", "lol", "dota2")]
s = requests.Session()
def get(url, params):
    for k in range(5):
        try: return s.get(url, params=params, timeout=40).json()
        except Exception: time.sleep(2 ** k)
    return None
def one(r):
    m = get("https://gamma-api.polymarket.com/markets", {"slug": r["slug"], "closed": "true"})
    if not m: return
    m = m[0]
    r["toks"] = json.loads(m.get("clobTokenIds") or "[]")
    r["condition"] = m.get("conditionId")
    start = int(datetime.fromisoformat(r["debut"]).timestamp())
    out = []
    for page in range(4):
        b = get("https://data-api.polymarket.com/trades", {"market": r["condition"], "limit": 1000, "offset": page * 1000, "takerOnly": "true"})
        if not isinstance(b, list) or not b: break
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b
                if t.get("timestamp") and start - 4 * 3600 <= int(t["timestamp"]) <= start + 600]
        if len(b) < 1000 or int(b[-1]["timestamp"]) < start - 4 * 3600: break
    r["echanges"] = out
with ThreadPoolExecutor(4) as ex: list(ex.map(one, rows))
json.dump([{k: v for k, v in r.items() if k != "chemin"} | {"p1h": None} for r in rows], open(f"{D}/trades.json", "w"))
print("fini", len(rows), sum(1 for r in rows if r.get("echanges")), flush=True)
