"""Piste n° 9, contrôle aux ÉCHANGES RÉELS : les « pics isolés » (prix CLOB milieu) sont-ils de vrais prix ?
Pour chaque pic à T-72 h : dernier échange réel du OUI dans les 24 h AVANT T0, et premier échange d'achat du NON dans les 24 h APRÈS."""
import json, math, re, sys, datetime as dt
from pathlib import Path
import concurrent.futures as cf
sys.argv = [sys.argv[0], "72"]
exec(open("experiments/queues_tranches/lissage.py").read().split("dips, spikes, n_ev")[0])
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
cases = []
for e in ev.values():
    ms = [(num(m), m) for m in e["markets"] if m["id"] in px and px[m["id"]]["final"] in (0.0, 1.0)]
    if len(ms) < 6 or any(n is None for n, _ in ms) or len(ms) != len(e["markets"]): continue
    ms.sort(key=lambda x: x[0])
    ps = [price(px[m["id"]]) for _, m in ms]
    if any(p is None for p in ps) or sum(px[m["id"]]["final"] for _, m in ms) != 1: continue
    top = max(range(len(ps)), key=lambda i: ps[i])
    for i in range(1, len(ps) - 1):
        p, a, b = ps[i], ps[i - 1], ps[i + 1]
        if 0.05 <= p <= 0.70 and p > 1.6 * max(a, b) and i != top and not (0.44 <= p <= 0.56):
            m = ms[i][1]
            cases.append(dict(e=e, m=m, p=p, yes=int(px[m["id"]]["final"] == 1.0), t0=px[m["id"]]["end"] - HRS * 3600))
print(len(cases), "pics,", len({c["e"]["id"] for c in cases}), "événements")
http = HttpClient(); cache = Path("experiments/queues_tranches/donnees/echanges")
def get(eid): return eid, it.fetch_event_trades(http, cache, eid)
with cf.ThreadPoolExecutor(6) as ex:
    trades = dict(ex.map(get, sorted({c["e"]["id"] for c in cases})))
rows = []
for c in cases:
    tr = trades[c["e"]["id"]]; tok, oth = c["m"]["yes"], c["m"]["no"]
    before = it.taker_cost(tr, tok, oth, c["t0"], window=24 * 3600)            # dernier prix payé pour le OUI avant T0
    after_no = it.taker_cost(tr, oth, tok, c["t0"], window=24 * 3600, after=True)  # prix payable pour le NON après T0
    rows.append((c, before, after_no))
have = [r for r in rows if r[1] is not None]
print(f"{len(have)} pics avec un échange réel du OUI dans les 24 h avant T0 ; {sum(1 for r in rows if r[2] is not None)} avec un achat de NON possible dans les 24 h après")
if have:
    print("prix affiché → dernier échange réel du OUI :", [(round(r[0]['p'], 2), round(r[1], 2)) for r in have][:25])
    ratio = sum(1 for r in have if r[1] < 0.6 * r[0]["p"]) / len(have)
    print(f"échange réel < 0,6 × prix affiché : {ratio:.0%} des pics")
    w = sum(r[0]["yes"] for r in have); ex_ = sum(r[1] for r in have); var = sum(r[1] * (1 - r[1]) for r in have)
    print(f"OUI gagnés {w} pour {ex_:.1f} attendus par le dernier prix réel (z {(w-ex_)/math.sqrt(var):+.2f})")
bets = []
for c, before, no in rows:
    if no is None or no >= 0.995: continue
    fs = c["m"].get("fs") or {}; rate = float(fs.get("rate") or 0) if c["m"].get("fees") else 0.0
    cost = no + it.fee(no, rate)
    bets.append(dict(gain=(0 if c["yes"] else 1) / cost - 1, evenement=c["e"]["id"], cout=cost,
                     mois=dt.datetime.fromtimestamp(c["t0"], dt.timezone.utc).strftime("%Y-%m")))
print(json.dumps(it.verdict(bets, min_bets=20), ensure_ascii=False))
