"""Historique de prix (CLOB prices-history, pas de 10 min) du premier camp de chaque match, de J-1 à +4 h
autour du coup d'envoi. Reprend où il s'est arrêté (donnees/sport_prix.jsonl). Usage depuis experiments/tennis."""
import json, os, time, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
rows = json.load(open("donnees/sport_matchs.json"))
done = set()
if os.path.exists("donnees/sport_prix.jsonl"):
    done = {json.loads(l)["id"] for l in open("donnees/sport_prix.jsonl")}
todo = [r for r in rows if r["id"] not in done and r["start"]]
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def ts(x): return int(datetime.fromisoformat(x.replace(" ", "T").replace("+00", "+00:00")).timestamp())
def get(r):
    st = ts(r["start"])
    for k in range(5):
        try:
            h = s.get("https://clob.polymarket.com/prices-history", params={"market": r["toks"][0], "startTs": st - 24 * 3600, "endTs": st + 4 * 3600,
                      "fidelity": 10}, timeout=40).json()
            return {"id": r["id"], "st": st, "h": [[p["t"], p["p"]] for p in h.get("history") or []]}
        except Exception: time.sleep(2 ** k)
    return None
with open("donnees/sport_prix.jsonl", "a") as f, ThreadPoolExecutor(6) as ex:
    for i, out in enumerate(ex.map(get, todo)):
        if out: f.write(json.dumps(out) + "\n"); f.flush()
        if i % 200 == 0: print(i, len(todo), flush=True)
