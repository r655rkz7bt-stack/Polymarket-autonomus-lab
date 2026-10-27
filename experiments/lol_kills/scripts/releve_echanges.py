"""27/10/2026 : vrais échanges (data-api, sans clé) des marchés de kills du LoL de volume >= VOL_MIN. Usage : python releve_echanges.py [VOL_MIN=100] [inverse]
Cache : donnees/echanges/<id>.json.gz ({"complet", "echanges": [[heure, jeton, côté, prix, parts]]}). Reprise possible."""
import concurrent.futures as cf, gzip, json, os, sys, time, threading
from pathlib import Path
import requests
H = {"User-Agent": "curl/8"}; U = "https://data-api.polymarket.com/trades"
D = Path("experiments/lol_kills/donnees"); SERIE = os.environ.get("SERIE", "lol")
DIR = D / ("echanges" if SERIE == "lol" else f"echanges_{SERIE}"); DIR.mkdir(exist_ok=True)
VOL = float(sys.argv[1]) if len(sys.argv) > 1 else 100
ms = [json.loads(l) for l in open(D / ("marches.jsonl" if SERIE == "lol" else f"marches_{SERIE}.jsonl"))]
ms = [m for m in ms if m["vol"] >= VOL]
if len(sys.argv) > 2: ms.reverse()
loc = threading.local()
def get(p):
    s = getattr(loc, "s", None) or requests.Session(); loc.s = s
    for k in range(5):
        try:
            r = s.get(U, headers=H, params=p, timeout=60)
            if r.status_code == 200: return r.json()
            if r.status_code == 400: return None
        except Exception: pass
        time.sleep(2 ** k)
    raise RuntimeError("data-api muette")
def one(m):
    path = DIR / f"{m['id']}.json.gz"
    if path.exists(): return "cache"
    rows, complet = [], True
    for off in range(0, 10001, 1000):
        b = get({"market": m["cond"], "limit": 1000, "offset": off})
        if not b: break
        rows += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
        if len(b) < 1000: break
        if off == 10000: complet = False
    path.write_bytes(gzip.compress(json.dumps({"complet": complet, "echanges": rows}).encode()))
    return "ok"
n = {"ok": 0, "cache": 0, "err": 0}
with cf.ThreadPoolExecutor(8) as ex:
    for i, r in enumerate(ex.map(one, ms)):
        n[r if r in n else "err"] += 1
        if i % 500 == 0: print(i, len(ms), n, flush=True)
print("fini", n)
