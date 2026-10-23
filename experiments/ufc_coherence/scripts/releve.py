"""Piste n° 6 (ufc_coherence) : relevé des combats UFC réglés (Gamma, série 38) et de leurs vrais échanges (data-api).
Écrit donnees/events.json (événements avec marchés) et donnees/echanges.jsonl ({event, trades:[[t, jeton, côté, prix, parts]]}).
À lancer depuis experiments/ufc_coherence/. Reprend où il s'est arrêté."""
import json, os, time, requests
from concurrent.futures import ThreadPoolExecutor
os.makedirs("donnees", exist_ok=True)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
ev = {}
if not os.path.exists("donnees/events.json"):
    for series in (38,):
        off = 0
        while True:
            for k in range(5):
                try:
                    b = s.get("https://gamma-api.polymarket.com/events", params={"series_id": series, "closed": "true", "order": "endDate",
                              "ascending": "false", "limit": 100, "offset": off}, timeout=60).json(); break
                except Exception: time.sleep(2 ** k); b = None
            if not isinstance(b, list) or not b: break
            for e in b: ev[e["id"]] = e
            off += 100
            if len(b) < 100: break
    json.dump(list(ev.values()), open("donnees/events.json", "w"))
ev = {e["id"]: e for e in json.load(open("donnees/events.json"))}
print("événements", len(ev), flush=True)
done = set()
if os.path.exists("donnees/echanges.jsonl"): done = {json.loads(l)["event"] for l in open("donnees/echanges.jsonl")}
todo = [e for e in ev if e not in done]
def get(e):
    out = []
    for page in range(10):
        b = None
        for k in range(5):
            try:
                b = s.get("https://data-api.polymarket.com/trades", params={"eventId": e, "limit": 1000, "offset": page * 1000}, timeout=40).json(); break
            except Exception: time.sleep(2 ** k)
        if not isinstance(b, list): return None
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
        if len(b) < 1000: break
    return {"event": e, "trades": out}
with open("donnees/echanges.jsonl", "a") as f, ThreadPoolExecutor(6) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 50 == 0: print(i, flush=True)
