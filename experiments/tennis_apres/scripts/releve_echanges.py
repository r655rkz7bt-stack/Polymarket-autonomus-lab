"""Vrais échanges (data-api) des matchs où le favori vaut 0,90-0,985 à +3, +4, +5 ou +6 h après le coup d'envoi."""
import json, os, time, requests
from concurrent.futures import ThreadPoolExecutor
rows = {r["id"]: r for r in json.load(open("donnees/matchs.json"))}
def snap(h, t):
    pts = [x for x in h if x[0] <= t]
    return pts[-1][1] if pts and t - pts[-1][0] <= 1800 else None
want = {}
for l in open("donnees/prix.jsonl"):
    p = json.loads(l)
    for lag in (3, 4, 5, 6):
        q = snap(p["h"], p["st"] + lag * 3600)
        if q is not None and 0.90 <= max(q, 1 - q) < 0.985: want[rows[p["id"]]["event"]] = p["id"]
done = set()
if os.path.exists("donnees/echanges.jsonl"): done = {json.loads(l)["event"] for l in open("donnees/echanges.jsonl")}
todo = [e for e in want if e not in done]
print("événements", len(want), "à relever", len(todo), flush=True)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def get(ev):
    out = []
    for page in range(4):
        for k in range(5):
            try:
                b = s.get("https://data-api.polymarket.com/trades", params={"eventId": ev, "limit": 1000, "offset": page * 1000}, timeout=40).json(); break
            except Exception: time.sleep(2 ** k); b = None
        if not isinstance(b, list): return None
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
        if len(b) < 1000: break
    return {"event": ev, "trades": out}
with open("donnees/echanges.jsonl", "a") as f, ThreadPoolExecutor(6) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 100 == 0: print(i, flush=True)
