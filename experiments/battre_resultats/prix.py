"""Piste n° 17 : historique de prix horaire du OUI sur les 10 jours avant l'échéance (le CLOB ne rend rien pour un marché clos avec interval=max)."""
import json, requests, datetime as dt, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
P = "experiments/battre_resultats/donnees/earnings.json"
R = json.load(open(P))
def ts(s):
    try: return int(dt.datetime.fromisoformat(str(s).replace("Z", "+00:00").replace(" ", "T")).timestamp())
    except Exception: return None
def one(r):
    e = ts(r["end"])
    if not e: return r
    for _ in range(3):
        try:
            x = requests.get("https://clob.polymarket.com/prices-history", headers=H, timeout=60, params={"market": r["yes"], "startTs": e - 10 * 86400, "endTs": e + 3600, "fidelity": 60})
            if x.status_code == 200:
                r["hist"] = [[p["t"], p["p"]] for p in x.json().get("history", [])]; break
        except requests.RequestException: pass
    return r
with cf.ThreadPoolExecutor(8) as ex: R = list(ex.map(one, R))
json.dump(R, open(P, "w"))
print(sum(1 for r in R if r["hist"]), "marchés avec historique sur", len(R))
