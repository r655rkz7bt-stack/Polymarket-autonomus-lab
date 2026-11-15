"""Piste n° 62 : prix horaires du CLOB (prices-history, fidelity 60) du jeton OUI de chaque tranche Polymarket, événements dont
la fin est après le 14/09/2026 (période couverte par l'API « live » de Kalshi). Sortie : donnees/poly_prix.json {jeton: [[t, p]]}."""
import json, os, datetime as dt, requests
from concurrent.futures import ThreadPoolExecutor
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
ev = [e for e in json.load(open("donnees/poly_events.json")) if (e["fin"] or "") >= "2026-09-14"]
P = "donnees/poly_prix.json"
out = json.load(open(P)) if os.path.exists(P) else {}
todo = []
for e in ev:
    fin = int(dt.datetime.fromisoformat(e["fin"].replace("Z", "+00:00")).timestamp())
    for m in e["marches"]:
        if m["jetons"] and m["jetons"][0] not in out: todo.append((m["jetons"][0], fin))
def one(a):
    tok, fin = a; pts = []
    for k in range(3):  # fenêtres de 4 jours avant la fin (≤ 14 j par appel)
        try:
            r = S.get("https://clob.polymarket.com/prices-history", params={"market": tok, "startTs": fin - 4 * 86400 * (k + 1), "endTs": fin - 4 * 86400 * k, "fidelity": 60}, timeout=30)
            pts += [(h["t"], h["p"]) for h in (r.json() or {}).get("history") or []]
        except Exception: pass
    return tok, sorted(set(pts))
with ThreadPoolExecutor(8) as ex:
    for i, (tok, pts) in enumerate(ex.map(one, todo)):
        out[tok] = pts
        if i % 300 == 0: print(i, len(todo), flush=True)
json.dump(out, open(P, "w")); print("fini", len(out), sum(1 for v in out.values() if v))
