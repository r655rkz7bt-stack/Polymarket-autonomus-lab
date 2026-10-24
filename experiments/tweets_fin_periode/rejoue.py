"""Compteur de tweets : le modèle gagne-t-il aussi dans les dernières heures avant la fin ? (23-24/10/2026)
Le test du 20/10 (`experiments/vingt_pistes/scripts/tweets_contre_marche.py`) n'achetait qu'entre « début + 6 h » et « fin − 3 h »,
alors que `compteur_tweets` achète jusqu'à la fin (4 achats à moins de 6 h en direct, 4 perdus). Ici : même modèle, mêmes frais,
achat toutes les heures de « début + 6 h » à « fin − 10 min », résultat par horizon (heures avant la fin).
Données : donnees/xt/ (tweets_releve_marches.py, tweets_releve_messages.py). Usage : python experiments/tweets_fin_periode/rejoue.py [dispersion] [marge] [prix_min]"""
import bisect, collections, json, math, statistics as st, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "src")
from polymarket_agent import references as refs
D = "donnees/xt"
ev = json.load(open(f"{D}/marches.json"))
DISP = float(sys.argv[1]) if len(sys.argv) > 1 else 12
MARGIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.03
MINP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
R, W, STALE = 168, 0.5, 2 * 3600
import os
SPREADX = float(os.environ.get('SPREADX', 1))  # multiplie le demi-écart supposé (0,01 Elon, 0,02 les autres)
posts = {}
def P(h):
    if h not in posts:
        posts[h] = sorted(datetime.fromisoformat(t.replace("Z", "+00:00")) for t in json.load(open(f"{D}/{h}.json")))
    return posts[h]
def count(h, a, b):
    ts = P(h); return bisect.bisect_left(ts, b) - bisect.bisect_left(ts, a)
def tracking(h, start, end, t):
    hour = t.replace(minute=0, second=0, microsecond=0)
    hourly = [count(h, hour - timedelta(hours=k + 1), hour - timedelta(hours=k)) for k in range(335, -1, -1)]
    return {"debut": start.isoformat(), "fin": end.isoformat(), "total": count(h, start, t), "vu_le": t.isoformat(), "heures": hourly}
trades, nper, bad = [], 0, 0
for e in ev:
    h = e["compte"]; start = datetime.fromisoformat(e["debut"]); end = datetime.fromisoformat(e["fin"]) - timedelta(seconds=1)
    if P(h)[0] > start - timedelta(days=14):
        continue
    final = count(h, start, end + timedelta(seconds=1))
    bks = []
    for m in e["marches"]:
        b = refs.bucket_of(m["titre"] or "")
        if b and m["hist"]:
            bks.append((b, [x["t"] for x in m["hist"]], [x["p"] for x in m["hist"]], m["prix_final"], m["titre"]))
    if not bks: continue
    win = [b for b in bks if b[0][0] <= final <= b[0][1]]
    paid = [b for b in bks if json.loads(b[3] or "[0]")[0] in ("1", 1)]
    if len(win) != 1 or (paid and paid[0][0] != win[0][0]):
        bad += 1; continue  # contrôle du règlement : notre compte doit redonner la tranche réglée
    nper += 1
    t = start + timedelta(hours=6)
    t = t.replace(minute=0, second=0)
    while t < end - timedelta(minutes=10):
        ts = t.timestamp()
        prices = []
        for b, tt, pp, _, _t in bks:
            i = bisect.bisect_right(tt, ts) - 1
            prices.append(pp[i] if i >= 0 and ts - tt[i] < STALE else None)
        ANYBK = bool(os.environ.get("ANYBK"))  # 24/10 : sans exiger un prix récent pour TOUTES les tranches (Elon : 26-30 tranches, beaucoup sans échange horaire)
        have = [p for p in prices if p is not None]
        if (ANYBK and len(have) >= 3) or (all(p is not None for p in prices) and 0.5 < sum(prices) < 1.5):
            tr = tracking(h, start, end, t)
            hrs = (end - t).total_seconds() / 3600
            for (b, _tt, _pp, _pf, title), p in zip(bks, prices):
                if p is None: continue
                q = refs.tweet_bucket_probability(tr, b, t, DISP, R, 336, W)
                won = b[0] <= final <= b[1]
                spread = (0.01 if h == "elonmusk" else 0.02) * SPREADX
                for side, qq, cost in ((0, q, p + spread), (1, 1 - q, 1 - p + spread)):
                    if max(0.01, MINP) <= cost < 0.99 and qq - MARGIN > cost:
                        pay = 1.0 if (won if side == 0 else not won) else 0.0
                        trades.append(dict(title=title, ts=ts, h=h, ev=e["slug"], t=t.isoformat()[:13], hrs=hrs, side=side, cost=cost, q=qq,
                                           g_fee=(pay - cost - 0.05 * cost * (1 - cost)) / cost, g0=(pay - cost) / cost))
        t += timedelta(hours=1)
print(f"{nper} périodes (règlement relu), {bad} écartées ; {len(trades)} achats (dispersion {DISP}, marge {MARGIN}, billet ≥ {MINP})")
def summ(rows, label, key="g_fee"):
    if len(rows) < 3: print(f"{label:26} {len(rows)} achats"); return
    g = [r[key] for r in rows]; byp = collections.defaultdict(list)
    for r in rows: byp[r["ev"]].append(r[key])
    m = [st.mean(v) for v in byp.values()]
    tt = st.mean(m) / (st.stdev(m) / math.sqrt(len(m))) if len(m) > 2 and st.stdev(m) > 0 else 0
    print(f"{label:26} {len(g):5} achats, {st.mean(g):+7.1%} par achat | {len(m):3} périodes, {st.mean(m):+7.1%} (t {tt:+.2f})")
bins = [(0, 1), (1, 3), (3, 6), (6, 12), (12, 24), (24, 72), (72, 200)]
for key, nom in (("g_fee", "frais 0,05·p·(1−p) (ancien barème)"), ("g0", "sans frais (barème actuel)")):
    print(f"\n== {nom}")
    for lo, hi in bins:
        summ([r for r in trades if lo <= r["hrs"] < hi], f"{lo}-{hi} h avant la fin", key)
    summ(trades, "tous", key)
    summ([r for r in trades if r["side"] == 1 and r["h"] != "NYCMayor"], "NON sans NYC (toutes heures)", key)
    for lo, hi in ((0, 6), (6, 200)):
        summ([r for r in trades if r["side"] == 1 and r["h"] != "NYCMayor" and lo <= r["hrs"] < hi], f"  NON sans NYC {lo}-{hi} h", key)
print("\n== écart |estimation − prix| (tous achats, sans frais)")
for lo, hi in ((0, .1), (.1, .2), (.2, .35), (.35, 1)):
    summ([r for r in trades if lo <= abs(r["q"] - (r["cost"])) < hi], f"écart {lo}-{hi}", "g0")
print("\n== par compte, moins de 6 h avant la fin (sans frais)")
for h in sorted({r["h"] for r in trades}):
    summ([r for r in trades if r["h"] == h and r["hrs"] < 6], h, "g0")

if os.environ.get("FOCUS"):
    foc = [r for r in trades if r["side"] == 1 and r["h"] != "NYCMayor"]
    print("\n######## FOCUS : NON sans NYC Mayor, sans frais, demi-écart x%s, marge %s" % (SPREADX, MARGIN))
    summ(foc, "toutes heures", "g0")
    print("-- par mois"); [summ([r for r in foc if r["t"][:7] == m], m, "g0") for m in sorted({r["t"][:7] for r in foc})]
    print("-- par compte"); [summ([r for r in foc if r["h"] == h], h, "g0") for h in sorted({r["h"] for r in foc})]
    print("-- par prix payé"); [summ([r for r in foc if lo <= r["cost"] < hi], f"prix {lo}-{hi}", "g0") for lo, hi in ((0.1, .3), (.3, .6), (.6, .85), (.85, 1))]
    byp = collections.defaultdict(list)
    for r in foc: byp[r["ev"]].append(r["g0"])
    per = sorted(((st.mean(v), k) for k, v in byp.items()), reverse=True)
    top3 = {k for _, k in per[:3]}
    summ([r for r in foc if r["ev"] not in top3], "sans les 3 meilleures périodes", "g0")
    evs = sorted(byp, key=lambda k: min(r["t"] for r in foc if r["ev"] == k))
    half = len(evs) // 2
    summ([r for r in foc if r["ev"] in set(evs[:half])], "1re moitié (plus anciennes)", "g0")
    summ([r for r in foc if r["ev"] in set(evs[half:])], "2e moitié (plus récentes)", "g0")
    seen, first = set(), []
    for r in sorted(foc, key=lambda r: r["t"]):
        k = (r["ev"], r["side"], round(r["q"], 2) // 1)
        first.append(r)
    one = {}
    for r in sorted(foc, key=lambda r: r["t"]):  # un seul achat par période et par tranche gagnante/perdante : le premier signal
        one.setdefault((r["ev"], round(r["cost"], 1), r["h"]), r)
    summ(list(one.values()), "premier signal (période, prix)", "g0")

if os.environ.get("PAYES"):
    # Prix réellement payés : premier échange de preneur sur NON dans l'heure qui suit la décision (taker_cost, after=True), sinon pas d'achat.
    import gzip
    from polymarket_agent import idea_test as it
    jet = json.load(open(f"{D}/jetons.json"))
    cache, rows, seen_ev = {}, [], {}
    for r in foc:
        j = jet.get(r["ev"])
        if not j or r["title"] not in j["jetons"]:
            continue
        if r["ev"] not in cache:
            path = f"{D}/cache/echanges_{j['id']}.json.gz"
            cache[r["ev"]] = json.loads(gzip.decompress(open(path, "rb").read())) if os.path.exists(path) else None
        trd = cache[r["ev"]]
        if not trd:
            continue
        yes, no = j["jetons"][r["title"]]
        paid = it.taker_cost(trd, no, yes, int(r["ts"]), window=3600, after=True)
        if paid is None or not (0.10 <= paid < 0.99):
            continue
        pay = r["g0"] * r["cost"] + r["cost"]  # 1 si NON gagne, 0 sinon
        rows.append(dict(r, paid=paid, edge_paid=r["q"] - paid, gp=(pay - paid) / paid, gpf=(pay - paid - 0.05 * paid * (1 - paid)) / paid))
    print("\n######## PRIX RÉELLEMENT PAYÉS (premier échange sur NON dans l'heure) : %d des %d achats du focus ont un échange" % (len(rows), len(foc)))
    mm = [r for r in rows if r["edge_paid"] > MARGIN]  # l'écart doit encore tenir au prix réellement payé
    for nom, rr in (("avec échange", rows), ("écart tenu au prix payé", mm)):
        summ(rr, nom + " : prix du relevé horaire", "g0"); summ(rr, nom + " : prix payé, sans frais", "gp"); summ(rr, nom + " : prix payé, frais 0,05·p·(1−p)", "gpf")
    print("prix payé moyen %.3f contre prix du relevé (+demi-écart) %.3f" % (st.mean(r["paid"] for r in mm), st.mean(r["cost"] for r in mm)))
    for lo, hi in ((0.1, .3), (.3, .6), (.6, 1)):
        summ([r for r in mm if lo <= r["paid"] < hi], f"  prix payé {lo}-{hi}", "gp")
    evs2 = sorted({r["ev"] for r in mm}, key=lambda k: min(r["t"] for r in mm if r["ev"] == k)); h2 = len(evs2) // 2
    summ([r for r in mm if r["ev"] in set(evs2[:h2])], "  1re moitié", "gp"); summ([r for r in mm if r["ev"] in set(evs2[h2:])], "  2e moitié", "gp")
    for m_ in sorted({r["t"][:7] for r in mm}): summ([r for r in mm if r["t"][:7] == m_], "  " + m_, "gp")
    for h_ in sorted({r["h"] for r in mm}): summ([r for r in mm if r["h"] == h_], "  compte " + h_, "gpf")
    for nom, key in (("prix payé, frais 0,05·p·(1−p)", "gpf"), ("prix payé, sans frais", "gp")):
        v = it.verdict([{"gain": r[key], "evenement": r["ev"], "mois": r["t"][:7], "cout": r["paid"]} for r in mm])
        print("VERDICT", nom, "|", {k: v[k] for k in ("paris", "rendement_moyen", "evenements", "confiance_evenements", "z_prix", "mois", "verdict", "raison")})
