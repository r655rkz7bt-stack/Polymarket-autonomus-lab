"""Piste n° 10, suite : les mêmes paris (NON des tranches dont le OUI valait 0,25-0,60 à T-72 h) aux PRIX RÉELLEMENT PAYÉS :
premier échange d'achat du NON (ou vente du OUI) dans les 2 h qui suivent T-72 h (data-api trades). Jamais un prix connu après."""
import json, sys, math, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
WIN = int(sys.argv[5]) if len(sys.argv) > 5 else 2
HRS = int(sys.argv[1]) if len(sys.argv) > 1 else 72
LO, HI = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0.25, 0.60)
FAM = (sys.argv[4] or None) if len(sys.argv) > 4 else None
def fam(e):
    t = set(e["tags"]); s = e["slug"] or ""
    if "tweets-markets" in t or "of-tweets" in s or "truth-social" in s: return "tweets"
    if "elections" in t or "primaries" in t or "global-elections" in t: return "elections"
    if "crypto" in t or "crypto-prices" in t: return "crypto"
    if "ai" in t or "ai-rankings" in t: return "ia"
    return "autres"
ev = {e["id"]: e for e in json.load(open("experiments/queues_tranches/donnees/evenements.json"))}
mk = {m["id"]: (e, m) for e in ev.values() for m in e["markets"]}
cands = []
for l in open("experiments/queues_tranches/donnees/prix.jsonl"):
    r = json.loads(l)
    if r["market"] not in mk or r["final"] not in (0.0, 1.0): continue
    e, m = mk[r["market"]]
    ts = r["end"] - HRS * 3600
    pts = [(t, p) for t, p in r["hist"] if t <= ts]
    if not pts or ts - pts[-1][0] > 6 * 3600: continue
    p = pts[-1][1]
    if LO <= p < HI and (FAM is None or fam(e) == FAM):
        cands.append((e, m, ts, p, int(r["final"] == 1.0)))
print(len(cands), "paris candidats,", len({c[0]["id"] for c in cands}), "événements")
http = HttpClient()
cache = Path("experiments/queues_tranches/donnees/echanges")
events = sorted({c[0]["id"] for c in cands})
def get(eid):
    return eid, it.fetch_event_trades(http, cache, eid)
with cf.ThreadPoolExecutor(6) as ex:
    trades = dict(ex.map(get, events))
bets, nofill = [], 0
for e, m, ts, p, yes in cands:
    cost = it.taker_cost(trades[e["id"]], m["no"], m["yes"], ts, window=WIN * 3600, after=True)
    if cost is None:
        nofill += 1; continue
    fs = m.get("fs") or {}
    rate = float(fs.get("rate") or 0) if m.get("fees") else 0.0
    c = cost + it.fee(cost, rate)
    if c >= 0.995: continue
    import datetime as dt
    bets.append(dict(gain=(0 if yes else 1) / c - 1, evenement=e["id"], cout=c,
                     mois=dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m")))
print(len(bets), "paris avec un échange réel,", nofill, "sans échange dans les 2 h")
print(json.dumps(it.verdict(bets), ensure_ascii=False, indent=1))
