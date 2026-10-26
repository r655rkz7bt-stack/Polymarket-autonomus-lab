"""Piste « Under des totaux de sport » (26/10/2026) : vrais échanges (data-api, `market=<conditionId>`) des marchés de totaux
dont le volume dépasse 1 000 $. Écrit donnees/echanges.jsonl (un marché par ligne), reprend où il s'est arrêté.
À lancer depuis experiments/totaux_sports/ ; REV=1 parcourt la liste à l'envers (second processus)."""
import json, os, time, requests
from concurrent.futures import ThreadPoolExecutor
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def jget(params):
    for k in range(5):
        try:
            r = s.get("https://data-api.polymarket.com/trades", params=params, timeout=60)
            if r.status_code == 200: return r.json()
            time.sleep(2 ** k)
        except Exception:
            time.sleep(2 ** k)
    return None
marches = []
for l in open("donnees/btts.jsonl"):
    e = json.loads(l)
    for m in e["markets"]:
        if (m.get("volumeNum") or 0) >= 300 and m.get("umaResolutionStatus") == "resolved":
            marches.append(m["conditionId"])
done = set()
fichier = os.environ.get("SORTIE", "donnees/echanges.jsonl")
for f in ("donnees/echanges.jsonl", "donnees/echanges_rev.jsonl"):
    if os.path.exists(f): done |= {json.loads(l)["m"] for l in open(f)}
todo = [c for c in marches if c not in done]
if os.environ.get("REV"): todo = todo[::-1]
print(len(marches), "marchés,", len(todo), "à relever", flush=True)
def get(c):
    out = []
    for page in range(6):
        b = jget({"market": c, "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list): return None
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
        if len(b) < 1000: break
    return {"m": c, "trades": out}
with open(fichier, "a") as f, ThreadPoolExecutor(6) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 1000 == 0: print(i, "/", len(todo), flush=True)
