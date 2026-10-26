"""27/10/2026 : vrais échanges (data-api, `market=<conditionId>`) des marchés du relevé complet (releve_complet.py).
Marchés de totaux, de handicaps de sets et de vainqueur avec plus de 1 000 $ de volume (50 $ pour « Total Sets O/U 2.5 » du tennis, marché mince),
règlement `resolved`. Écrit donnees/echanges_complet_<PART>.jsonl (un marché par ligne), reprend où il s'est arrêté ; (PART=0..3 NB=4 : quatre processus en parallèle, un fichier chacun ). Lancer depuis la racine du dépôt."""
import json, os, time, requests
from concurrent.futures import ThreadPoolExecutor
D = "experiments/totaux_sports/donnees"
PREFIXE = "echanges_complet"
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def jget(params):
    for k in range(5):
        try:
            r = s.get("https://data-api.polymarket.com/trades", params=params, timeout=60)
            if r.status_code == 200: return r.json()
        except Exception:
            pass
        time.sleep(2 ** k)
    return None
marches = []
for l in open(f"{D}/totaux_complet.jsonl"):
    e = json.loads(l)
    for m in e["markets"]:
        if m.get("sportsMarketType") in ("moneyline", "spreads", "tennis_set_handicap"): continue   # seuls les marchés de totaux (les vainqueurs : ≈ 250 marchés par minute, 4 heures pour 64 000)
        seuil = 50 if m.get("sportsMarketType") == "tennis_set_totals" else 1000
        if (m.get("volumeNum") or 0) >= seuil and m.get("umaResolutionStatus") == "resolved":
            marches.append(m["conditionId"])
done = set()
import glob
PART, NB = int(os.environ.get("PART", 0)), int(os.environ.get("NB", 1))      # PART=i NB=4 : le i-ème quart de la liste (4 processus)
fichier = f"{D}/{PREFIXE}_{PART}.jsonl"
for f in glob.glob(f"{D}/{PREFIXE}_*.jsonl"):
    done |= {json.loads(l)["m"] for l in open(f)}
todo = [c for k, c in enumerate(dict.fromkeys(marches)) if k % NB == PART and c not in done]
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
