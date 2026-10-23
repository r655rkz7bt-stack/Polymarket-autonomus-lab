"""Prix (CLOB prices-history, pas de 60 min) du OUI de chaque marché de gagnant de saison, dans la journée qui précède
H jours avant la fin de l'événement (H = 3, 7, 14, 30, 60). Reprend où il s'est arrêté (donnees/prix.jsonl)."""
import json, os, time, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
HOR = (3, 7, 14, 30, 60)
ev = json.load(open("donnees/evenements.json"))
def ts(x): return int(datetime.fromisoformat(x.replace(" ", "T").replace("Z", "+00:00").replace("+00", "+00:00") if not x.endswith("+00:00") else x).timestamp())
done = set()
if os.path.exists("donnees/prix.jsonl"): done = {(r["id"], r["h"]) for r in map(json.loads, open("donnees/prix.jsonl"))}
todo = []
for e in ev:
    T = ts(e["closed"])
    for m in e["markets"]:
        if float(m["vol"] or 0) < 2000: continue
        mc = ts(m["closed"]) if m["closed"] else T
        for h in HOR:
            t = T - h * 86400
            if mc > t and (m["id"], h) not in done: todo.append((m, h, t, e["id"]))
print("à relever", len(todo), flush=True)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def get(a):
    m, h, t, evid = a
    for k in range(5):
        try:
            r = s.get("https://clob.polymarket.com/prices-history", params={"market": m["tok"], "startTs": t - 86400, "endTs": t, "fidelity": 60}, timeout=40).json()
            return {"id": m["id"], "h": h, "ev": evid, "t": t, "hist": [[p["t"], p["p"]] for p in r.get("history") or []]}
        except Exception: time.sleep(2 ** k)
    return None
with open("donnees/prix.jsonl", "a") as f, ThreadPoolExecutor(8) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 500 == 0: print(i, flush=True)
