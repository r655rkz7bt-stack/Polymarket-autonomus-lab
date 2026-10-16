"""Pourquoi le favori gagne-t-il ? (16/10/2026) — test sur le passé AUX PRIX RÉELLEMENT PAYÉS.

Usage : python3 -I experiments/favori/analyse.py <dossier_de_travail>
Données : celles d'experiments/smart_money (16 680 marchés résolus du 15/09 au 15/10/2026,
échanges d'au moins 100 $ : <dossier>/sm/markets.json et <dossier>/sm/trades/*.json).
Pour chaque marché et chaque instant de décision (h heures avant la clôture réelle) : prix du
dernier échange de chaque issue AVANT cet instant (jamais après) ; favori = issue la plus chère.
Rendement d'un pari de 1 part sur le favori = issue (1 ou 0) − prix − frais preneur (barème estimé
par catégorie), avec un écart ajouté de 0 / 0,01. Un seul pari par marché et par instant.
"""
import bisect
import glob
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime

SP = sys.argv[1]
# Référence du temps restant : « annoncee » = date d'échéance affichée (ce que voit le bot, sans
# regard vers le futur) ; « reelle » = clôture réelle (connue après coup : biais, à titre de comparaison).
REF = sys.argv[2] if len(sys.argv) > 2 else "annoncee"
OUT = f"{SP}/sm"
markets = {m["cid"]: m for m in json.load(open(f"{OUT}/markets.json"))}
HORIZONS = [0.5, 2, 6, 24, 72, 168]
BUCKETS = [(0.50, 0.70), (0.70, 0.80), (0.80, 0.85), (0.85, 0.90), (0.90, 0.95), (0.95, 0.98), (0.98, 0.995)]


def ts(text):
    try:
        return int(datetime.fromisoformat(str(text).replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def fee_rate(tags):  # docs.polymarket.com/trading/fees (16/10/2026), estimé par catégorie
    t = set(tags or [])
    if "geopolitics" in t:
        return 0.0
    if "crypto" in t:
        return 0.07
    if "sports" in t or "esports" in t:
        return 0.05
    if t & {"politics", "finance", "tech", "mentions"}:
        return 0.04
    return 0.05


def family(m):
    t, slug = set(m["tags"] or []), m["slug"] or ""
    if "updown" in slug or "up-or-down" in slug:
        return "crypto hausse/baisse"
    if "crypto" in t:
        return "crypto (seuils)"
    if "esports" in t:
        return "e-sport"
    if "sports" in t:
        return "sport"
    if "weather" in t or "temperature" in slug:
        return "météo"
    if "politics" in t or "elections" in t:
        return "politique"
    if "geopolitics" in t:
        return "géopolitique"
    if t & {"economy", "finance", "fed", "business"}:
        return "économie / finance"
    if t & {"culture", "pop-culture", "movies", "music", "tech", "mentions"}:
        return "culture / tech / mentions"
    return "autres"


cases = []  # (famille, h, prix, gagné, frais, cid, volume, âge du prix en h, neg)
for path in glob.glob(f"{OUT}/trades/*.json"):
    cid = os.path.basename(path)[:-5]
    m = markets.get(cid)
    if not m:
        continue
    closed_at = ts(m.get("closed")) or ts(m.get("end"))
    close = ts(m.get("end")) if REF == "annoncee" else closed_at
    if close is None or closed_at is None:
        continue
    series = defaultdict(list)
    for t in json.load(open(path)):
        try:
            if t["asset"] in m["tokens"]:
                series[t["asset"]].append((int(t["timestamp"]), float(t["price"])))
        except (KeyError, TypeError, ValueError):
            continue
    if len(series) == 0:
        continue
    for v in series.values():
        v.sort()
    fam, rate = family(m), fee_rate(m["tags"])
    for h in HORIZONS:
        when = close - h * 3600
        if when >= closed_at:
            continue  # déjà clos à l'instant de décision (échéance annoncée dépassée)
        last = {}
        for tok, v in series.items():
            i = bisect.bisect_right(v, (when, 2.0)) - 1
            if i >= 0 and when - v[i][0] <= 6 * 3600:  # prix d'au plus 6 h avant la décision
                last[tok] = v[i]
        if not last:
            continue
        # favori : prix le plus haut ; un seul jeton connu → son prix ou 1 − prix de l'autre
        best = max(last.items(), key=lambda kv: kv[1][1])
        tok, (t0, p) = best
        if p < 0.5:
            other = [x for x in m["tokens"] if x != tok][0]
            tok, p = other, 1 - p
        cases.append((fam, h, p, 1 if tok == m["winner"] else 0, rate, cid, m["volume"], (when - t0) / 3600,
                      m["tokens"].index(tok)))
print(f"Référence du temps restant : {REF}")
print(f"{len(cases)} cas ({len({c[5] for c in cases})} marchés)")


def stats(sel, slip=0.0):
    n = len(sel)
    if n == 0:
        return None
    win = sum(c[3] for c in sel) / n
    price = sum(c[2] for c in sel) / n
    cost = sum(c[2] + slip + c[4] * (c[2] + slip) * (1 - c[2] - slip) for c in sel)
    gain = sum(c[3] for c in sel) - cost
    se = math.sqrt(max(win * (1 - win), 1e-9) / n)
    return n, price, win, se, 100 * gain / cost


def table(title, groups, slip=0.0, min_n=30):
    print(f"\n### {title}\n| groupe | paris | prix moyen | gagnés | écart (gagnés − prix) | rendement après frais |")
    print("|---|---|---|---|---|---|")
    for name, sel in groups:
        s = stats(sel, slip)
        if s and s[0] >= min_n:
            n, price, win, se, ret = s
            print(f"| {name} | {n} | {price:.3f} | {win:.3f} ± {se:.3f} | {100 * (win - price):+.1f} pts | {ret:+.2f} % |")


fav = [c for c in cases if c[2] >= 0.80]
table("Calibration : tous les prix du favori (tous instants)", [(f"{a:.2f}-{b:.3f}", [c for c in cases if a <= c[2] < b]) for a, b in BUCKETS])
table("Favori 0,80-0,995 selon le temps restant", [(f"{h} h avant", [c for c in fav if c[1] == h]) for h in HORIZONS])
table("Favori 0,80-0,95 (la plage de naive_favorite) selon le temps restant", [(f"{h} h avant", [c for c in fav if c[1] == h and c[2] < 0.95]) for h in HORIZONS])
fams = sorted({c[0] for c in cases})
table("Favori 0,80-0,995 selon la famille de marchés", [(f, [c for c in fav if c[0] == f]) for f in fams])
table("Favori 0,80-0,95 selon la famille (plage naive_favorite)", [(f, [c for c in fav if c[0] == f and c[2] < 0.95]) for f in fams])
table("Favori 0,95-0,995 selon la famille (« presque certain »)", [(f, [c for c in fav if c[0] == f and c[2] >= 0.95]) for f in fams])
table("Favori 0,80-0,995 selon le volume du marché", [
    ("< 50 k$", [c for c in fav if c[6] < 5e4]), ("50-200 k$", [c for c in fav if 5e4 <= c[6] < 2e5]),
    ("200 k$-1 M$", [c for c in fav if 2e5 <= c[6] < 1e6]), ("> 1 M$", [c for c in fav if c[6] >= 1e6])])
table("Favori 0,80-0,995 selon l'âge du dernier prix", [
    ("< 10 min", [c for c in fav if c[7] < 1 / 6]), ("10 min-1 h", [c for c in fav if 1 / 6 <= c[7] < 1]),
    ("1-6 h", [c for c in fav if c[7] >= 1])])
table("Écart ajouté de 0,01 (prix vendeur plus cher) : favori 0,80-0,995 selon le temps restant",
      [(f"{h} h avant", [c for c in fav if c[1] == h]) for h in HORIZONS], slip=0.01)
# « Il ne se passe rien » : favori = NON dans une question « Will … ? » (le NON est l'issue n°1).
import re
yesno = lambda c: (markets[c[5]]["q"] or "").startswith("Will ")  # noqa: E731
deadline = re.compile(r"\b(by|before)\b .*(\d{4}|January|February|March|April|May|June|July|August|September|October|November|December)", re.I)
table("Questions « Will … ? » : favori NON (« il ne se passe rien ») contre favori OUI, 0,80-0,995", [
    ("favori NON", [c for c in fav if yesno(c) and c[8] == 1]), ("favori OUI", [c for c in fav if yesno(c) and c[8] == 0])])
table("Favori NON d'une question à échéance (« … by / before <date> ? »), 0,80-0,995", [
    ("à échéance, favori NON", [c for c in fav if yesno(c) and c[8] == 1 and deadline.search(markets[c[5]]["q"] or "")]),
    ("à échéance, favori OUI", [c for c in fav if yesno(c) and c[8] == 0 and deadline.search(markets[c[5]]["q"] or "")]),
    ("sans échéance, favori NON", [c for c in fav if yesno(c) and c[8] == 1 and not deadline.search(markets[c[5]]["q"] or "")])])
table("Favori NON (« Will … ? ») par famille, 0,80-0,995", [(f, [c for c in fav if c[0] == f and yesno(c) and c[8] == 1]) for f in fams])
table("Politique et géopolitique, favori 0,80-0,995 selon le temps restant", [
    (f"{h} h avant", [c for c in fav if c[0] in ("politique", "géopolitique") and c[1] == h]) for h in HORIZONS])
table("Politique, favori selon le prix", [(f"{a:.2f}-{b:.3f}", [c for c in cases if c[0] == "politique" and a <= c[2] < b]) for a, b in BUCKETS[2:]])
pol_days = defaultdict(list)
for c in fav:
    if c[0] in ("politique", "géopolitique") and c[2] < 0.95:
        pol_days[(markets[c[5]].get("closed") or "?")[:10]].append(c)
ok = [d for d, sel in pol_days.items() if stats(sel)[4] > 0]
print(f"\nPolitique + géopolitique, favori 0,80-0,95 : {len(ok)} jours gagnants sur {len(pol_days)} ; "
      f"{len({c[5] for sel in pol_days.values() for c in sel})} marchés, "
      f"{len({markets[c[5]]['slug'] for sel in pol_days.values() for c in sel})} événements")
# Par jour (stabilité) pour la meilleure tranche
days = defaultdict(list)
for c in fav:
    days[markets[c[5]]["closed"][:10] if markets[c[5]].get("closed") else "?"].append(c)
pos = sum(1 for d, sel in days.items() if stats(sel) and stats(sel)[4] > 0)
print(f"\nJours (de clôture) gagnants pour « favori 0,80-0,995, tous instants » : {pos} / {len(days)}")
json.dump([list(c) for c in cases], open(f"{SP}/fav_cases_{REF}.json", "w"))
