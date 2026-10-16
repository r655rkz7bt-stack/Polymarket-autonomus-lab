"""Argent informé : un portefeuille qui a gagné continue-t-il de gagner ? (16/10/2026)

Usage : python3 -I experiments/smart_money/evaluate.py <dossier_de_travail> [date_de_coupure]
Sans regard vers le futur :
- CLASSEMENT : échanges (≥ 100 $) des marchés RÉSOLUS avant la coupure (1er/10 par défaut) ;
  gain jusqu'à la résolution : achat = parts × (issue − prix), vente = parts × (prix − issue) ;
  rendement = gain / capital engagé (achat : parts × prix ; vente : parts × (1 − prix)).
- JUGEMENT : échanges passés APRÈS la coupure, de ces mêmes portefeuilles, sur des marchés résolus.
- COPIE : on reproduit l'échange 5 minutes plus tard (un cycle), au prix du premier gros échange
  du même jeton au moins 5 minutes après (+ écart simulé), frais preneur estimés par catégorie.
"""
import glob
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

SP = sys.argv[1]
CUT = int(datetime.fromisoformat((sys.argv[2] if len(sys.argv) > 2 else "2026-10-01") + "T00:00:00+00:00").timestamp())
OUT = f"{SP}/sm"
markets = {m["cid"]: m for m in json.load(open(f"{OUT}/markets.json"))}


def ts(text):
    try:
        return int(datetime.fromisoformat(str(text).replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def fee_rate(tags):  # barème par catégorie (docs.polymarket.com/trading/fees, 16/10/2026) : estimation
    t = set(tags or [])
    if "geopolitics" in t:
        return 0.0
    if "crypto" in t:
        return 0.07
    if "sports" in t:
        return 0.05
    if t & {"politics", "finance", "tech", "mentions"}:
        return 0.04
    return 0.05


trades = []  # (wallet, cid, token, side, size, price, ts, won, end)
for path in glob.glob(f"{OUT}/trades/*.json"):
    cid = os.path.basename(path)[:-5]
    m = markets.get(cid)
    if not m:
        continue
    end = ts(m.get("closed")) or ts(m.get("end"))
    for t in json.load(open(path)):
        try:
            size, price = float(t["size"]), float(t["price"])
        except (TypeError, ValueError, KeyError):
            continue
        if not (0 < price < 1) or size <= 0 or t.get("asset") not in m["tokens"]:
            continue
        trades.append((t["proxyWallet"], cid, t["asset"], t["side"], size, price, int(t["timestamp"]),
                       1 if t["asset"] == m["winner"] else 0, end))
print(f"{len(trades)} échanges, {len({t[1] for t in trades})} marchés, {len({t[0] for t in trades})} portefeuilles")


def pnl(t):
    _, _, _, side, size, price, _, won, _ = t
    return (size * (won - price), size * price) if side == "BUY" else (size * (price - won), size * (1 - price))


# ----------------------------------------------------------------- classement (avant la coupure)
rank = defaultdict(lambda: [0.0, 0.0, 0, set()])
for t in trades:
    if t[8] is not None and t[8] < CUT:
        g, c = pnl(t)
        r = rank[t[0]]
        r[0] += g; r[1] += c; r[2] += 1; r[3].add(t[1])
eligible = {w: r[0] / r[1] for w, r in rank.items() if r[2] >= 20 and len(r[3]) >= 5 and r[1] > 0}
print(f"portefeuilles classés (≥ 20 échanges, ≥ 5 marchés avant la coupure) : {len(eligible)}")
ordered = sorted(eligible, key=eligible.get, reverse=True)
n = len(ordered)
groups = {"top 1 %": ordered[: max(1, n // 100)], "top 10 %": ordered[: max(1, n // 10)],
          "milieu 40-60 %": ordered[int(n * 0.4): int(n * 0.6)], "pires 10 %": ordered[-max(1, n // 10):]}

# ----------------------------------------------------------------- jugement (après la coupure)
after = defaultdict(lambda: [0.0, 0.0, 0])
for t in trades:
    if t[6] >= CUT:
        g, c = pnl(t)
        a = after[t[0]]
        a[0] += g; a[1] += c; a[2] += 1
print("\n| Groupe (classé avant) | rendement avant | portefeuilles actifs après | échanges après | rendement après |")
print("|---|---|---|---|---|")
for name, ws in groups.items():
    before = sum(rank[w][0] for w in ws) / sum(rank[w][1] for w in ws)
    act = [w for w in ws if after[w][2]]
    g, c, k = (sum(after[w][i] for w in act) for i in range(3))
    print(f"| {name} | {100 * before:+.1f} % | {len(act)} / {len(ws)} | {k} | {100 * g / c if c else float('nan'):+.1f} % |")
everyone = [a for a in after.values() if a[2]]
print(f"| tous les portefeuilles | | {len(everyone)} | {sum(a[2] for a in everyone)} | "
      f"{100 * sum(a[0] for a in everyone) / sum(a[1] for a in everyone):+.1f} % |")

# rang avant contre rang après (portefeuilles actifs des deux côtés, ≥ 10 échanges après)
both = [(eligible[w], after[w][0] / after[w][1]) for w in ordered if after[w][2] >= 10 and after[w][1] > 0]


def spearman(pairs):
    def ranks(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0] * len(xs)
        for k, i in enumerate(order):
            r[i] = k
        return r
    a, b = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    m = (len(pairs) - 1) / 2
    num = sum((x - m) * (y - m) for x, y in zip(a, b))
    den = math.sqrt(sum((x - m) ** 2 for x in a) * sum((y - m) ** 2 for y in b))
    return num / den if den else float("nan")


print(f"\ncorrélation des rangs avant / après (Spearman, {len(both)} portefeuilles) : {spearman(both):+.3f}")

# ----------------------------------------------------------------- copie avec 5 minutes de retard
by_token = defaultdict(list)
for t in trades:
    by_token[t[2]].append((t[6], t[5]))
for v in by_token.values():
    v.sort()
other = {m["cid"]: m for m in markets.values()}


def later_price(token, when):
    import bisect
    v = by_token[token]
    i = bisect.bisect_left(v, (when, -1.0))
    return v[i][1] if i < len(v) else None


print("\n| Copie (groupe, écart ajouté) | paris | rendement des mises | jours gagnants |")
print("|---|---|---|---|")
for name in ("top 1 %", "top 10 %", "pires 10 %"):
    ws = set(groups[name])
    for spread in (0.0, 0.01, 0.02):
        g = c = k = 0.0
        days = defaultdict(float)
        for t in trades:
            w, cid, token, side, size, price, when, won, end = t
            if w not in ws or when < CUT or end is None or when + 300 >= end:
                continue
            p = later_price(token, when + 300)
            if p is None:
                continue
            m = markets[cid]
            if side == "BUY":
                cost, win = p + spread, won
            else:  # vendre « Oui » = acheter l'autre issue à 1 − p
                cost, win = 1 - p + spread, 1 - won
            if not 0.02 <= cost <= 0.98:
                continue
            f = fee_rate(m["tags"]) * cost * (1 - cost)
            g += win - cost - f; c += cost; k += 1
            days[datetime.fromtimestamp(when, tz=timezone.utc).strftime("%m-%d")] += win - cost - f
        print(f"| {name}, +{spread} | {int(k)} | {100 * g / c if c else float('nan'):+.1f} % | "
              f"{sum(1 for v in days.values() if v > 0)} / {len(days)} |")
