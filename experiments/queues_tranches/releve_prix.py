"""Prix OUI heure par heure (CLOB) des 10 derniers jours avant l'échéance, pour les événements à tranches
(neg-risk, hors sport, ≥ 5 marchés, au plus un OUI réglé). Reprise possible : donnees/prix.jsonl (ignoré par Git)."""
import json, os, datetime as dt, requests, concurrent.futures as cf, threading
H = {"User-Agent": "curl/8"}
ev = json.load(open("experiments/queues_tranches/donnees/evenements.json"))
sel = [e for e in ev if e["neg"] and "sports" not in e["tags"] and "games" not in e["tags"]
       and sum(m["final"] > 0.99 for m in e["markets"]) <= 1 and len(e["markets"]) >= 5]
path = "experiments/queues_tranches/donnees/prix.jsonl"
done = set()
if os.path.exists(path):
    for l in open(path):
        done.add(json.loads(l)["market"])
jobs = []
for e in sel:
    for m in e["markets"]:
        if m["id"] in done or not m.get("end"):
            continue
        jobs.append((e, m))
print(len(jobs), "à télécharger")
lock = threading.Lock(); f = open(path, "a"); n = [0]
def one(job):
    e, m = job
    t1 = int(dt.datetime.fromisoformat(m["end"].replace("Z", "+00:00")).timestamp())
    for attempt in range(3):
        try:
            r = requests.get("https://clob.polymarket.com/prices-history", headers=H, timeout=30,
                             params={"market": m["yes"], "startTs": t1 - 10 * 86400, "endTs": t1, "fidelity": 60})
            if r.status_code == 200:
                h = [(x["t"], x["p"]) for x in r.json().get("history", [])]
                break
            if r.status_code == 429:
                import time; time.sleep(2 + attempt * 3)
        except Exception:
            h = None
    else:
        h = None
    if h is None:
        return
    with lock:
        f.write(json.dumps({"event": e["id"], "market": m["id"], "end": t1, "final": m["final"], "hist": h}) + "\n"); f.flush()
        n[0] += 1
        if n[0] % 1000 == 0: print(n[0], flush=True)
with cf.ThreadPoolExecutor(8) as ex:
    list(ex.map(one, jobs))
print("fini", n[0])
