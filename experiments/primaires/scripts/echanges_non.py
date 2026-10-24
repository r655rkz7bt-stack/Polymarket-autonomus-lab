"""Vrais échanges (data-api, par marché) des candidats cotés 0,08-0,35 à J-14, J-21 ou J-30 : sert à payer le NON au prix réellement exécutable. Écrit donnees/echanges.jsonl.
À lancer depuis experiments/primaires/ après releve_prix.py."""
import json, bisect, os, time, requests
from concurrent.futures import ThreadPoolExecutor
rows = [json.loads(l) for l in open("donnees/prix.jsonl")]
cid = {}
for l in open("donnees/events.jsonl"):
    e = json.loads(l)
    for m in e["markets"] or []: cid[m["id"]] = m.get("conditionId")
want = {}
for r in rows:
    ts = [p[0] for p in r["h"]]
    for d in (7, 14, 21, 30):
        T = r["endts"] - d * 86400; i = bisect.bisect_right(ts, T) - 1
        if i >= 0 and T - ts[i] <= 12 * 3600 and 0.08 <= r["h"][i][1] <= 0.35:
            want[r["market"]] = r
done = set()
if os.path.exists("donnees/echanges.jsonl"): done = {json.loads(l)["market"] for l in open("donnees/echanges.jsonl")}
todo = [m for m in want if m not in done and cid.get(m)]
print("marchés", len(want), "à relever", len(todo), flush=True)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def get(m):
    out = []
    for page in range(15):
        for k in range(4):
            try:
                b = s.get("https://data-api.polymarket.com/trades", params={"market": cid[m], "limit": 1000, "offset": page * 1000}, timeout=60).json(); break
            except Exception: time.sleep(2 ** k); b = None
        if not isinstance(b, list): return None
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp")]
        if len(b) < 1000: break
    return {"market": m, "trades": out, "complete": len(b) < 1000}
with open("donnees/echanges.jsonl", "a") as f, ThreadPoolExecutor(6) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 50 == 0: print(i, len(todo), flush=True)
