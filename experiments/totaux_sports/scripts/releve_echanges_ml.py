"""27/10/2026 : échantillon tiré au hasard (graine fixe) de marchés « vainqueur du match » (moneyline) du relevé complet, plus de 2 000 $ de volume, règlement net ou 50-50,
et leurs vrais échanges (data-api). Les marchés très échangés se lisent à ≈ 250 par minute : on en tire N (6 000 par défaut), répartis en 4 processus (PART=0..3 NB=4).
Écrit donnees/echanges_ml_<PART>.jsonl, reprend où il s'est arrêté. Lancer depuis la racine du dépôt."""
import json, os, random, glob, time, requests
from concurrent.futures import ThreadPoolExecutor
D = "experiments/totaux_sports/donnees"
N = int(os.environ.get("N", 6000)); PART, NB = int(os.environ.get("PART", 0)), int(os.environ.get("NB", 1))
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
cands = []
for l in open(f"{D}/totaux_complet.jsonl"):
    e = json.loads(l)
    for m in e["markets"]:
        if m["sportsMarketType"] == "moneyline" and (m.get("volumeNum") or 0) >= 2000 and m.get("umaResolutionStatus") == "resolved":
            cands.append(m["conditionId"])
cands = sorted(set(cands)); random.Random(27102026).shuffle(cands)
echantillon = cands[:N]
print(len(cands), "marchés candidats,", len(echantillon), "tirés", flush=True)
done = set()
for f in glob.glob(f"{D}/echanges_ml_*.jsonl"):
    done |= {json.loads(l)["m"] for l in open(f)}
todo = [c for k, c in enumerate(echantillon) if k % NB == PART and c not in done]
def get(c):
    out = []
    for page in range(6):
        b = jget({"market": c, "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list): return None
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
        if len(b) < 1000: break
    return {"m": c, "trades": out}
with open(f"{D}/echanges_ml_{PART}.jsonl", "a") as f, ThreadPoolExecutor(8) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 500 == 0: print(i, "/", len(todo), flush=True)
