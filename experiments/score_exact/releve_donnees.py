"""Piste n° 1 : pour chaque match de football (exact-score, volume >= VMIN), télécharge l'événement du match (1X2),
l'événement « more-markets » (totaux) et les échanges réels (data-api) des trois. Reprise possible (cache gzip)."""
import json, sys, gzip, requests, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
H = {"User-Agent": "curl/8"}
VMIN = float(sys.argv[1]) if len(sys.argv) > 1 else 2000
D = Path("experiments/score_exact/donnees"); (D / "echanges").mkdir(exist_ok=True); (D / "siblings").mkdir(exist_ok=True)
ev = [json.loads(l) for l in open(D / "exact_events.jsonl")]
ev = sorted([e for e in ev if float(e.get("volume") or 0) >= VMIN], key=lambda e: -float(e.get("volume") or 0))
http = HttpClient(min_interval=0.03)
def sib(slug):
    p = D / "siblings" / (slug + ".json.gz")
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
    base = e["slug"][:-len("-exact-score")]
    m = sib(base); mm = sib(base + "-more-markets")
    for x in (e, m, mm):
        if x: it.fetch_event_trades(http, D / "echanges", str(x["id"]))
    return e["id"], bool(m), bool(mm)
ok = 0
with cf.ThreadPoolExecutor(20) as ex:
    for i, r in enumerate(ex.map(un, ev)):
        ok += 1
        if i % 100 == 0: print(i, len(ev), r, flush=True)
print("fini", ok)
