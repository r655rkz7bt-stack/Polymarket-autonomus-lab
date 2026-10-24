"""Piste « k gagnants » : achats simulés aux prix des vrais échanges (preneurs), frais du marché, événements réglés.
Décision à J-d avant la résolution, avec les derniers échanges des 24 h précédentes ; achat au premier échange preneur des 6 h suivantes.
Usage : PYTHONPATH=src python experiments/k_gagnants/scripts/test_passe.py   (racine du dépôt)"""
import bisect, datetime as dt, gzip, json, math, sys
from collections import defaultdict
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/k_gagnants/donnees")
DAY = 86400
evs = {e["id"]: e for e in json.load(open(D / "evs.json"))}
raw = {}
for l in open(D / "evenements.jsonl"):
    e = json.loads(l)
    if e["id"] in evs: raw[e["id"]] = e
hist = defaultdict(dict)
hp = {}
for l in open(D / "prix.jsonl"):
    r = json.loads(l)
    if r["h"]:
        hist[r["event"]][r["market"]] = r["h"][-1][0]
        hp[r["market"]] = r["h"]
def hist_price(mid, t):
    h = hp[mid]; i = bisect.bisect_right([x[0] for x in h], t) - 1
    return h[i][1] if i >= 0 and t - h[i][0] <= 2 * DAY else None
def rate_of(m):
    try:
        fs = m.get("feeSchedule")
        if isinstance(fs, str): fs = json.loads(fs.replace("'", '"').replace("True", "true").replace("False", "false"))
        return float(fs["rate"]) if fs and m.get("feesEnabled") in (True, "True", "true") else 0.0
    except Exception:
        return 0.0
cases = defaultdict(list)   # (event, d) -> [(market, yes_tok, no_tok, p, y, rate)]
trades = {}
cover = defaultdict(list)
for eid, e in raw.items():
    tr = json.loads(gzip.decompress((D / "cache" / f"echanges_{eid}.json.gz").read_bytes()))
    trades[eid] = tr
    ms = [m for m in e["markets"] if m["id"] in hist[eid]]
    if len(ms) < 4: continue
    ys = {m["id"]: float(json.loads(m["outcomePrices"])[0]) for m in ms}
    k = int(sum(ys.values()))
    R = max(hist[eid].values())
    for d in (3, 7, 14):
        T = R - d * DAY
        rows = []
        for m in ms:
            yt, nt = json.loads(m["clobTokenIds"])[:2]
            p = it.taker_cost(tr, yt, nt, T, window=3 * DAY)   # prix d'achat du OUI, dernier échange des 3 jours
            q = it.taker_cost(tr, nt, yt, T, window=3 * DAY)   # prix d'achat du NON
            if p is None and q is None:
                h = hist_price(m["id"], T)                     # sans échange : le prix du CLOB seulement aux extrêmes (carnet vide = 0,50 trompeur)
                if h is None or not (h <= 0.05 or h >= 0.95): continue
                pm = h
            else:
                pm = p if q is None else (1 - q if p is None else (p + 1 - q) / 2)
            rows.append((m["id"], yt, nt, pm, ys[m["id"]], rate_of(m)))
        cover[d].append((eid, len(rows), len(ms)))
        if len(rows) >= 0.9 * len(ms):
            cases[(eid, d)] = (k, rows, T, len(ms))
print("couverture (événements avec ≥ 90 % des marchés au prix connu) :", {d: sum(1 for (e, dd) in cases if dd == d) for d in (3, 7, 14)}, "sur", len(raw))
# 1) somme des prix
for d in (3, 7, 14):
    rs = sorted(sum(r[3] for r in v[1]) / v[0] for (e, dd), v in cases.items() if dd == d)
    if rs: print(f"J-{d}: Σp/k médian {rs[len(rs)//2]:.3f}, moyen {sum(rs)/len(rs):.3f}, > 1,05 : {sum(x>1.05 for x in rs)}/{len(rs)}, < 0,95 : {sum(x<0.95 for x in rs)}/{len(rs)}")
# 2) log-score
def ll(p, y):
    p = min(max(p, 0.001), 0.999); return math.log(p if y else 1 - p)
for d in (3, 7, 14):
    a = b = n = 0
    for (e, dd), (k, rows, T, nm) in cases.items():
        if dd != d: continue
        s = sum(r[3] for r in rows) * nm / len(rows)
        for r in rows:
            a += ll(r[3], r[4]); b += ll(min(r[3] * k / s, 0.999), r[4]); n += 1
    if n: print(f"J-{d} log-score prix {a/n:+.4f} renormalisé {b/n:+.4f} ({n} marchés)")
# 3) achats
def bets_for(d, gap, side, lo=0.05, hi=0.95):
    out = []
    for (e, dd), (k, rows, T, nm) in cases.items():
        if dd != d: continue
        s = sum(r[3] for r in rows) * nm / len(rows)
        for mid, yt, nt, p, y, rate in rows:
            pn = min(p * k / s, 0.999)
            want = "NON" if (p - pn >= gap and side in ("NON", "les deux")) else "OUI" if (pn - p >= gap and side in ("OUI", "les deux")) else None
            if not want: continue
            tok, oth = (nt, yt) if want == "NON" else (yt, nt)
            cost = it.taker_cost(trades[e], tok, oth, T, window=6 * 3600, after=True)
            if cost is None or not lo <= cost <= hi: continue
            f = it.fee(cost, rate)
            pay = (1 - y) if want == "NON" else y
            out.append(dict(gain=(pay - cost - f) / (cost + f), evenement=e, mois=dt.datetime.fromtimestamp(T, dt.timezone.utc).strftime("%Y-%m"), cout=cost + f, cote=want))
    return out
n_set = 0
print("\nd  écart  côté      paris  rend.moy  t_evt  z_prix  mois+   verdict")
best = []
for d in (3, 7, 14):
    for gap in (0.03, 0.06, 0.10):
        for side in ("NON", "OUI", "les deux"):
            n_set += 1
            b = bets_for(d, gap, side)
            if not b: continue
            v = it.verdict(b)
            print(f"J-{d:<2} {gap:.2f}  {side:<8} {v['paris']:>5}  {v['rendement_moyen']:+.4f}  {v['confiance_evenements']:+.2f}  {v['z_prix']:+.2f}  {v['mois_gagnants']:>5}  {v['verdict']} ({v['evenements']} événements)")
            best.append((v['confiance_evenements'], d, gap, side, v))
print(n_set, "réglages")
json.dump([(t, d, g, s, v) for t, d, g, s, v in best], open(D / "resultats.json", "w"), ensure_ascii=False, default=str)
