"""Vrais échanges (data-api v2, preneurs) des marchés réglés, puis rejeu des achats simulés aux prix réellement payés :
après l'instant de décision (02 h UTC du jour), premier échange PRENEUR sur le côté voulu à ≤ prix visé (prix horaire + 0,02),
dans la fenêtre FEN (3 h par défaut : une fenêtre de 24 h compte des achats faits après un mouvement en séance, regard vers le futur) ; parts cumulées à ce prix ou moins dans la fenêtre (profondeur). Sortie : donnees/echanges/<id>.json"""
import json, os, sys, collections
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
import requests
from polymarket_agent import data_api
D = os.path.join(os.path.dirname(__file__), "..", "donnees")
FEN = int(os.environ.get("FEN", "10800"))  # fenêtre d'exécution après 02 h UTC (3 h : marché américain fermé)
os.makedirs(os.path.join(D, "echanges"), exist_ok=True)
H = {"User-Agent": "curl/8"}

class Http:
    def get_json(self, url, params=None):
        r = requests.get(url, params=params, headers=H, timeout=60); r.raise_for_status(); return r.json()

rows = json.load(open(os.path.join(D, "marches.json")))
def fetch(r):
    out = os.path.join(D, "echanges", r["id"] + ".json")
    if os.path.exists(out):
        return
    m = requests.get(f"https://gamma-api.polymarket.com/markets/{r['id']}", headers=H, timeout=60).json()
    tr = data_api.lire(Http(), data_api.TRADES, {"condition": m["conditionId"]}, pages=10)
    json.dump({"tokens": json.loads(m["clobTokenIds"]), "trades": [{k: t.get(k) for k in ("asset", "side", "price", "size", "timestamp")} for t in tr]}, open(out, "w"))
if "--fetch" in sys.argv:
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(fetch, rows))
by_id = {r["id"]: r for r in rows}
for K in [a for a in sys.argv[1:] if not a.startswith("--")]:
    o = json.load(open(os.path.join(D, f"obs_K{K}.json")))
    for seuil in (0.05, 0.10, 0.15):
        for qmin in (10, 50):
            done, bets, absent = set(), [], 0
            for x in sorted(o, key=lambda x: x["jour"]):
                if x["id"] in done:
                    continue
                for side, est, pr in ((1, x["p"], x["prix"] + 0.02), (0, 1 - x["p"], 1 - x["prix"] + 0.02)):
                    if 0.05 <= pr <= 0.95 and est - pr >= seuil:
                        done.add(x["id"])
                        f = os.path.join(D, "echanges", x["id"] + ".json")
                        if not os.path.exists(f):
                            absent += 1; break
                        e = json.load(open(f)); tok = e["tokens"][0 if side == 1 else 1]
                        t0 = datetime.fromisoformat(x["jour"]).replace(hour=2, tzinfo=timezone.utc).timestamp()
                        ok = sorted((t for t in e["trades"] if t["asset"] == tok and t["side"] == "BUY" and t0 <= int(t["timestamp"]) < t0 + FEN
                                     and float(t["price"]) <= pr + 1e-9), key=lambda t: int(t["timestamp"]))
                        if sum(float(t["size"]) for t in ok) >= qmin:
                            paid = ok[0]["price"] if qmin <= float(ok[0]["size"]) else sum(float(t["price"]) * float(t["size"]) for t in ok) / sum(float(t["size"]) for t in ok)
                            win = x["y"] if side == 1 else 1 - x["y"]
                            bets.append((x["mois"], float(paid), win))
                        break
            g = collections.defaultdict(list)
            for b in bets: g[b[0]].append(b)
            tot = sum(b[2] / b[1] - 1 for b in bets) / max(len(bets), 1)
            print(f"K={K} seuil {seuil} ≥{qmin} parts : {len(bets)} paris exécutables, gagnés {sum(b[2] for b in bets)} pour {sum(b[1] for b in bets):.1f} attendus, {tot:+.1%} ;",
                  " ; ".join(f"{m} {len(v)} {sum(b[2]/b[1]-1 for b in v)/len(v):+.0%}" for m, v in sorted(g.items())))
