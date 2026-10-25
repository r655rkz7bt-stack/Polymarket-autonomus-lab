"""`compteur_tweets_non` (NON seulement, sans NYC Mayor) re-jugé aux prix des vrais échanges, avec la profondeur (25/10/2026).
Mêmes règles que experiments/truth_social/scripts/contre_marche.py (formule de production : 168 h / 336 h, dispersion 12), pour un compte XTracker donné.
Usage : analyse.py [dispersion] [marge] [prix_min] [seulement_non 0|1]"""
import bisect, gzip, json, math, sys, collections, statistics as st
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, "experiments/truth_social/scripts")
from polymarket_agent import idea_test as it
from polymarket_agent.references import tweet_bucket_probability, bucket_of
D = Path("experiments/tweets_prix_payes/donnees")
R = float(sys.argv[1]) if len(sys.argv) > 1 else 12
MARGE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.04
MINP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
ONLY_NO = (sys.argv[4] if len(sys.argv) > 4 else "1") == "1"
COMPTES = ["ZelenskyyUa", "tedcruz", "WhiteHouse", "cz_binance"]
bets, regl = [], collections.Counter()
for h in COMPTES:
    ts_post = sorted(datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() for t in json.load(open(D / f"messages_{h}.json")))
    compte = lambda a, b: bisect.bisect_left(ts_post, b) - bisect.bisect_left(ts_post, a)
    first_post = ts_post[0]
    for e in json.load(open(D / f"evenements_{h}.json")):
        E = datetime.fromisoformat(e["endDate"].replace("Z", "+00:00")); S0 = E - timedelta(days=7)
        if not e.get("closed") or E > datetime.now(timezone.utc) or S0.timestamp() - 14 * 86400 < first_post: continue
        buckets, win = [], None
        for m in e["markets"]:
            b = bucket_of(m.get("groupItemTitle") or "")
            if b is None: continue
            yes, no = json.loads(m["clobTokenIds"]); p = json.loads(m["outcomePrices"])
            if float(p[0]) > 0.99: win = b
            buckets.append((m["groupItemTitle"], b, yes, no, float(p[0]) > 0.99))
        if len(buckets) < 5 or win is None: continue
        final = compte(S0.timestamp(), E.timestamp())
        ok = win[0] <= final <= win[1]; regl[(h, ok)] += 1
        if not ok: continue                       # règlement non retrouvé : période écartée (comme le test du 21/10)
        path = D / "cache" / f"echanges_{e['id']}.json.gz"
        if not path.exists(): continue
        trades = json.loads(gzip.decompress(path.read_bytes()))
        for off in (0.25, 1, 2, 3, 4, 5, 6):
            T = S0 + timedelta(days=off)
            if T >= E - timedelta(hours=3): continue
            hour = T.replace(minute=0, second=0, microsecond=0)
            hourly = [compte((hour - timedelta(hours=k + 1)).timestamp(), (hour - timedelta(hours=k)).timestamp()) for k in range(335, -1, -1)]
            tr = {"debut": S0.isoformat(), "fin": E.isoformat(), "vu_le": T.isoformat(), "total": compte(S0.timestamp(), T.timestamp()), "heures": hourly}
            ts = int(T.timestamp())
            for title, rng, yes, no, won in buckets:
                q = tweet_bucket_probability(tr, rng, T, R, 168, 336, 0.5)
                if q is None: continue
                for side, qq, mine, other in ((0, q, yes, no), (1, 1 - q, no, yes)):
                    if ONLY_NO and side == 0: continue
                    cost = it.taker_cost(trades, mine, other, ts, window=2 * 3600, after=True)
                    if cost is None or not (max(MINP, 0.03) <= cost < 0.97): continue
                    fee = 0.05 * cost * (1 - cost)
                    if qq - cost - fee > MARGE:
                        parts = sum(t[4] for t in trades if ts <= t[0] <= ts + 2 * 3600 and ((t[1] == mine and t[2] == "BUY") or (t[1] == other and t[2] == "SELL"))
                                    and (t[3] if t[1] == mine else 1 - t[3]) <= cost + 0.01)
                        gain = ((1.0 if (won if side == 0 else not won) else 0.0) - cost - fee) / cost
                        bets.append({"gain": gain, "evenement": e["slug"], "mois": E.strftime("%Y-%m"), "cout": cost, "cote": side, "off": off, "tr": title,
                                     "parts": parts, "compte": h})
print(f"R {R} marge {MARGE} prix_min {MINP} NON seul {ONLY_NO} ; règlement retrouvé :", {h: f"{regl[(h, True)]}/{regl[(h, True)] + regl[(h, False)]}" for h in COMPTES})
seen, first = set(), []
for b in sorted(bets, key=lambda b: b["off"]):
    k = (b["evenement"], b["tr"], b["cote"])
    if k not in seen: seen.add(k); first.append(b)
def resume(sel, label):
    if len(sel) < 5: print(f"  {label}: {len(sel)} achats"); return
    ev = collections.defaultdict(list)
    for x in sel: ev[x["evenement"]].append(x["gain"])
    em = [st.mean(v) for v in ev.values()]
    t = st.mean(em) / st.stdev(em) * math.sqrt(len(em)) if len(em) > 2 else 0
    print(f"  {label}: {len(sel)} achats, {len(em)} périodes, {st.mean(x['gain'] for x in sel):+.3f} par achat, t par période {t:+.2f}")
resume(first, "tous (premier signal par tranche)")
for h in COMPTES: resume([b for b in first if b["compte"] == h], h)
resume([b for b in first if b["parts"] < 20], "profondeur < 20 parts")
resume([b for b in first if 20 <= b["parts"] < 100], "profondeur 20-100 parts")
resume([b for b in first if b["parts"] >= 100], "profondeur ≥ 100 parts")
resume([b for b in first if b["cout"] < 0.30], "prix 0,10-0,30")
resume([b for b in first if 0.30 <= b["cout"] < 0.70], "prix 0,30-0,70")
resume([b for b in first if b["cout"] >= 0.70], "prix ≥ 0,70")
mo = collections.defaultdict(list)
for b in first: mo[b["mois"]].append(b)
print("  par mois :", {m: (round(st.mean(x["gain"] for x in v), 3), len(v)) for m, v in sorted(mo.items())})
print("  verdict idea_test :", json.dumps({k: v for k, v in it.verdict(first).items() if k in ("rendement_moyen", "confiance_evenements", "z_prix", "mois_gagnants", "verdict")}, ensure_ascii=False))
json.dump(first, open("/tmp/claude-0/s/bets_tweets.json", "w"))
