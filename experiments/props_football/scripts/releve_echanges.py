"""28/10/2026 : vrais échanges (data-api, `market=<conditionId>`) des marchés de football réglés à plus de 300 $ de volume :
premier à marquer, buteur à tout moment, corners d'équipe, totaux d'équipe de la 1re mi-temps. Écrit donnees/echanges_props.jsonl. Racine du dépôt."""
import json, os, time, requests
from concurrent.futures import ThreadPoolExecutor
D = "experiments/props_football/donnees"
TYPES = {"soccer_first_to_score", "soccer_anytime_goalscorer", "soccer_team_total_corners", "soccer_first_half_team_totals"}
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def jget(params):
    for k in range(5):
        try:
            r = s.get("https://data-api.polymarket.com/trades", params=params, timeout=60)
            if r.status_code == 200: return r.json()
        except Exception:
            pass
        time.sleep(2 ** k)
marches = []
for l in open(f"{D}/props_evenements.jsonl"):
    e = json.loads(l)
    for m in e["markets"]:
        if m["sportsMarketType"] in TYPES and (m.get("volumeNum") or 0) >= 300 and m.get("umaResolutionStatus") == "resolved":
            marches.append(m["conditionId"])
marches = list(dict.fromkeys(marches))
fichier = f"{D}/echanges_props.jsonl"
done = {json.loads(l)["m"] for l in open(fichier)} if os.path.exists(fichier) else set()
todo = [c for c in marches if c not in done]
print(len(marches), "marchés,", len(todo), "à relever", flush=True)
def get(c):
    out = []
    for page in range(6):
        b = jget({"market": c, "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list): return None
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
        if len(b) < 1000: break
    return {"m": c, "trades": out}
with open(fichier, "a") as f, ThreadPoolExecutor(8) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 500 == 0: print(i, "/", len(todo), flush=True)
