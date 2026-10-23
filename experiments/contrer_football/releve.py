"""Piste n° 13 (contrer_football_en_jeu) : télécharge, pour chaque match de football (événement « exact-score » de volume >= VMIN),
l'événement 1X2 du match et ses échanges réels (data-api). Reprise possible (cache gzip). Utilise le relevé de score_exact/releve_evenements.py."""
import json, sys, gzip, requests, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
H = {"User-Agent": "curl/8"}
VMIN = float(sys.argv[1]) if len(sys.argv) > 1 else 5000
SRC = Path("experiments/score_exact/donnees"); D = Path("experiments/contrer_football/donnees")
(D / "echanges").mkdir(parents=True, exist_ok=True); (D / "match").mkdir(exist_ok=True)
ev = [json.loads(l) for l in open(SRC / "exact_events.jsonl")]
ev = sorted([e for e in ev if float(e.get("volume") or 0) >= VMIN], key=lambda e: -float(e.get("volume") or 0))
http = HttpClient(min_interval=0.03)
def sib(slug):
    p = D / "match" / (slug + ".json.gz")
    if p.exists(): return json.loads(gzip.decompress(p.read_bytes()))
    for _ in range(3):
        try:
            r = requests.get("https://gamma-api.polymarket.com/events", params=dict(slug=slug), headers=H, timeout=40)
            if r.status_code == 200:
                j = r.json(); out = j[0] if j else None
                p.write_bytes(gzip.compress(json.dumps(out).encode())); return out
        except Exception: pass
    return None
def un(e):
    m = sib(e["slug"][:-len("-exact-score")])
    if m: it.fetch_event_trades(http, D / "echanges", str(m["id"]))
    return e["id"], bool(m)
ok = 0
with cf.ThreadPoolExecutor(20) as ex:
    for i, r in enumerate(ex.map(un, ev)):
        ok += r[1]
        if i % 100 == 0: print(i, len(ev), r, flush=True)
print("fini", ok, len(ev))
