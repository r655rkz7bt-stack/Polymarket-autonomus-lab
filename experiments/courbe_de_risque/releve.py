"""Piste n° 8 (courbe_de_risque) : relevé des « échelles de dates » réglées (événements à >= 4 marchés « by <date> ») depuis le 01/03/2026
(Gamma, par fenêtres de 10 jours sur la date de fin) et de leurs échanges réels (data-api). Sortie : donnees/echelles.jsonl + donnees/echanges/."""
import json, sys, re, requests, datetime as dt, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
H = {"User-Agent": "curl/8"}
G = "https://gamma-api.polymarket.com/events"
D = Path("experiments/courbe_de_risque/donnees"); (D / "echanges").mkdir(parents=True, exist_ok=True)
D0 = dt.datetime.fromisoformat(sys.argv[1]); D1 = dt.datetime.fromisoformat(sys.argv[2])
PAT = re.compile(r"\b(by|through|before)\b", re.I)
def fenetre(a):
    b = a + dt.timedelta(days=3); got = []
    for off in range(0, 2000, 100):
        r = None
        for _ in range(3):
            try:
                r = requests.get(G, params=dict(closed="true", limit=100, offset=off, end_date_min=a.strftime("%Y-%m-%dT%H:%M:%SZ"), end_date_max=b.strftime("%Y-%m-%dT%H:%M:%SZ")), headers=H, timeout=40)
                if r.status_code == 200: break
            except Exception: r = None
        if r is None or r.status_code != 200: break
        evs = r.json(); got += evs
        if len(evs) < 100: break
    return got
fen = []; a = D0
while a < D1: fen.append(a); a += dt.timedelta(days=3)
out = {}
with cf.ThreadPoolExecutor(6) as ex:
    for evs in ex.map(fenetre, fen):
        for e in evs:
            ms = e.get("markets") or []
            if len(ms) >= 4 and sum(1 for m in ms if PAT.search(m.get("question") or "")) >= 4 and float(e.get("volume") or 0) >= 5000: out[e["id"]] = e
    print("événements", len(out), flush=True)
with open(D / (sys.argv[3] if len(sys.argv) > 3 else "echelles.jsonl"), "w") as f:
    for e in out.values(): f.write(json.dumps(e) + "\n")
http = HttpClient(min_interval=0.03)
def un(e): it.fetch_event_trades(http, D / "echanges", str(e["id"])); return 1
with cf.ThreadPoolExecutor(16) as ex: n = sum(ex.map(un, out.values()))
print("échanges", n)
