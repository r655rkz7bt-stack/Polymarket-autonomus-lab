"""Piste n° 1 (score_exact_poisson) : relevé des événements « exact-score » de football réglés (Gamma, tag soccer),
par fenêtres de 12 h sur la date de fin (Gamma coupe la pagination vers 2 000 lignes).
Sortie : donnees/exact_events.jsonl (un événement par ligne, avec ses marchés)."""
import json, sys, requests, datetime as dt, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
G = "https://gamma-api.polymarket.com/events"
D0 = dt.datetime.fromisoformat(sys.argv[1]); D1 = dt.datetime.fromisoformat(sys.argv[2])
def fenetre(a):
    b = a + dt.timedelta(hours=12); got = []
    for off in range(0, 2000, 100):
        for _ in range(3):
            try:
                r = requests.get(G, params=dict(closed="true", limit=100, offset=off, tag_slug="soccer",
                    end_date_min=a.strftime("%Y-%m-%dT%H:%M:%SZ"), end_date_max=b.strftime("%Y-%m-%dT%H:%M:%SZ")), headers=H, timeout=40)
                if r.status_code == 200: break
            except Exception: r = None
        if r is None or r.status_code != 200: break
        evs = r.json(); got += evs
        if len(evs) < 100: break
    return a, got
fen = []; a = D0
while a < D1: fen.append(a); a += dt.timedelta(hours=12)
out = {}
with cf.ThreadPoolExecutor(6) as ex:
    for a, evs in ex.map(fenetre, fen):
        n = 0
        for e in evs:
            s = e.get("slug") or ""
            if s.endswith("-exact-score") and "half" not in s: out[e["id"]] = e; n += 1
        print(a.isoformat(), len(evs), n, len(out), flush=True)
with open("experiments/score_exact/donnees/exact_events.jsonl", "w") as f:
    for e in out.values(): f.write(json.dumps(e) + "\n")
print("total", len(out))
