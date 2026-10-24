"""Course à la publication (24/10/2026) : PortWatch publie le mardi ≈ 11 h UTC la semaine finie le dimanche ; le marché
hebdomadaire se règle plus tard. Entre les deux, le résultat est connu de qui lit PortWatch. Aux vrais échanges, à quel prix
peut-on acheter le côté gagnant (OUI de la tranche gagnante, NON des autres) à publication + 0 / 30 min / 1 h / 2 h / 4 h ?
Usage : PYTHONPATH=src python experiments/detroits/scripts/course_publication.py [--heure-maj 11]
"""
import argparse, collections, concurrent.futures as cf, datetime as dt, json, sys
from pathlib import Path
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import commun as c
from polymarket_agent import idea_test as it
from polymarket_agent.http_client import HttpClient

ap = argparse.ArgumentParser(); ap.add_argument("--heure-maj", type=float, default=11); ap.add_argument("--debut", default="2026-06-01")
a = ap.parse_args()
CACHE = Path(c.DONNEES) / "echanges"
inv = c.charge_inventaire()
series = {n: c.serie(n) for n in ("Strait of Hormuz", "Bab el-Mandeb Strait")}
evs = []
for ev in inv:
    cb = c.cible(ev)
    if not ev["clos"] or ev["detroit"] not in series or not cb or cb[1] < dt.date.fromisoformat(a.debut):
        continue
    win = c.gagnant(ev)
    if win is not None:
        evs.append((ev, cb[0], cb[1], win))
http = HttpClient(timeout=40, min_interval=0.25)
with cf.ThreadPoolExecutor(4) as ex:
    trades = dict(ex.map(lambda e: (e[0]["id"], it.fetch_event_trades(http, CACHE, e[0]["id"])), evs))
print(len(evs), "événements, échanges", sum(len(v) for v in trades.values()))
OFFS = [0, 0.5, 1, 2, 4, 8, 24]
res = collections.defaultdict(list)   # offset -> [(event, market, prix, parts_dispo)]
keys = set()
for ev, type_, D, win in evs:
    pub = dt.datetime.combine(D + dt.timedelta(days=2), dt.time(), tzinfo=dt.timezone.utc) + dt.timedelta(hours=a.heure_maj)
    # premier mardi 11 h connaissant D
    while c.connu_jusqua(pub, a.heure_maj) < D:
        pub += dt.timedelta(days=1)
    pub_ts = int(pub.timestamp())
    fin = [c.ts(q.get("closedTime")) for q in ev["questions"] if q.get("closedTime")]
    reglement = min(fin) if fin else None
    tr = trades[ev["id"]]
    iv = c.intervalles(ev["questions"], "plancher")
    for q in ev["questions"]:
        if q["id"] not in iv:
            continue
        yes, no = json.loads(q["clobTokenIds"])
        tok, oth = (yes, no) if q["id"] == win else (no, yes)
        for off in OFFS:
            t0 = pub_ts + int(off * 3600)
            p = it.taker_cost(tr, tok, oth, t0, window=3600, after=True)
            res[off].append((ev["id"], q["id"], p, reglement and (reglement.timestamp() - pub_ts) / 3600))
print("heure de règlement après publication (h), médiane :", sorted(r[3] for r in res[0] if r[3] is not None)[len(res[0]) // 2])
for off in OFFS:
    rows = [r for r in res[off] if r[2] is not None]
    if not rows:
        continue
    gains = [1 / r[2] - 1 for r in rows]
    moy = sum(1 - r[2] for r in rows) / len(rows)
    evs_off = collections.defaultdict(list)
    for r, g in zip(rows, gains):
        evs_off[r[0]].append(g)
    print(f"+{off:>4} h : {len(rows):3d}/{len(res[off])} marchés avec un échange dans l'heure, prix moyen {sum(r[2] for r in rows)/len(rows):.3f}, "
          f"gain moyen par part {moy:+.3f}, rendement moyen par pari {sum(gains)/len(gains):+.1%}, sous 0,97 : {sum(1 for r in rows if r[2] < 0.97)} paris, "
          f"événements concernés {len(evs_off)}")
json.dump({str(k): v for k, v in res.items()}, open(f"{c.DONNEES}/course_publication.json", "w"))
