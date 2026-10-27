"""27/10/2026, piste 0c : vrais échanges (data-api, sans clé) des marchés crypto relevés par releve_marches.py avec volume >= VOL_MIN.
Usage : python releve_echanges.py [VOL_MIN=5000] [inverse]. Cache : donnees/echanges/<id>.json.gz ([heure, jeton, côté, prix, parts]). Reprise possible."""
import concurrent.futures as cf, gzip, json, sys, time, threading
from pathlib import Path
import requests
H = {"User-Agent": "curl/8"}; U = "https://data-api.polymarket.com/trades"
D = Path("experiments/contrer_crypto_passe/donnees"); DIR = D / "echanges"; DIR.mkdir(exist_ok=True)
VOL = float(sys.argv[1]) if len(sys.argv) > 1 else 5000
import os
ms = [json.loads(l) for l in open(D / os.environ.get("MARCHES", "marches.jsonl"))]
ms = [m for m in ms if (m["vol"] or 0) >= VOL and "up or down" not in m["question"].lower()]
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
    for i, r in enumerate(ex.map(lambda m: (lambda: one(m))() if True else None, ms)):
        n[r if r in n else "err"] += 1
        if i % 200 == 0: print(i, len(ms), n, flush=True)
print("fini", n)
