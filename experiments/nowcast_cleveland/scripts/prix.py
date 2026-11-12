"""Prix horaires du OUI de chaque tranche des événements d'inflation réglés, 9 jours avant le règlement -> donnees/prix.json."""
import json, sys, pathlib, requests
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from commun import D, classify, bounds, ts

ev = [e for e in json.loads((D / "evenements_tags.json").read_text()) if classify(e["title"]) and e.get("closed")]
jobs = []
for e in ev:
    for m in e["markets"]:
        if not m.get("closedTime") or not m.get("clobTokenIds"):
            continue
        t1 = int(ts(m["closedTime"]).timestamp())
        jobs.append((m["id"], json.loads(m["clobTokenIds"])[0], t1 - 9 * 86400, t1))

def get(j):
    mid, tok, a, b = j
    for _ in range(3):
        try:
            r = requests.get("https://clob.polymarket.com/prices-history", timeout=30,
                             params={"market": tok, "startTs": a, "endTs": b, "fidelity": 60})
            return mid, r.json().get("history", [])
        except Exception:
            pass
    return mid, []

with ThreadPoolExecutor(6) as ex:
    out = dict(ex.map(get, jobs))
(D / "prix.json").write_text(json.dumps(out))
print(len(ev), len(jobs), sum(1 for v in out.values() if v))
