"""Prix OUI (CLOB prices-history, pas de 12 h) de chaque marché des événements « k gagnants » à gros volume.
Sortie : donnees/prix.jsonl (un marché par ligne : événement, k, issue, historique [(t, p)])."""
import json, re
from concurrent.futures import ThreadPoolExecutor
import requests
H = {"User-Agent": "curl/8"}
VOL_MIN = 20000
ev = [json.loads(l) for l in open("experiments/k_gagnants/donnees/evenements.jsonl")]
def res(m):
    try: pr = [float(x) for x in json.loads(m["outcomePrices"])]
    except Exception: return None
    return pr[0] if sorted(pr) == [0.0, 1.0] else None
jobs = []; evs = []
for e in ev:
    r = [res(m) for m in e["markets"]]
    t = e["title"].lower()
    if any(x is None for x in r) or re.search(r"\bhit\b|\bsay\b|views|price will|titled tuesday|tweet|post", t):
        continue
    k = int(sum(r))
    if k < 2 or float(e.get("volume") or 0) < VOL_MIN:
        continue
    evs.append(dict(id=e["id"], titre=e["title"], k=k, n=len(r), volume=float(e["volume"]), fin=e["markets"][0].get("closedTime") or e.get("closedTime")))
    for m, y in zip(e["markets"], r):
        jobs.append((e["id"], m["id"], m["question"], y, json.loads(m["clobTokenIds"])[0], m.get("closedTime")))
print(len(evs), "événements,", len(jobs), "marchés")
def get(j):
    for _ in range(3):
        try:
            h = requests.get("https://clob.polymarket.com/prices-history", params=dict(market=j[4], interval="max", fidelity=720), headers=H, timeout=40).json().get("history", [])
            return j, [(x["t"], x["p"]) for x in h]
        except Exception:
            pass
    return j, None
with ThreadPoolExecutor(6) as ex, open("experiments/k_gagnants/donnees/prix.jsonl", "w") as f:
    for j, h in ex.map(get, jobs):
        if h is None: continue
        f.write(json.dumps(dict(event=j[0], market=j[1], q=j[2], y=j[3], closed=j[5], h=h)) + "\n")
json.dump(evs, open("experiments/k_gagnants/donnees/evs.json", "w"))
