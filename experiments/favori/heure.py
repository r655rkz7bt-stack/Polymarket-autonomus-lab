"""L'heure de la journée compte-t-elle ? (17/10/2026, AMELIORATION n°7)

Usage : python3 -I experiments/favori/heure.py <dossier_de_travail>
Données d'experiments/smart_money (16 680 marchés résolus, échanges ≥ 100 $). Pour chaque marché,
chaque heure UTC et chaque issue, on garde UN échange (le premier de l'heure) : prix réellement
payé p, issue gagnante ou non. Rendement d'un achat à p = issue − p − frais (barème estimé).
Question : à certaines heures (nuit américaine, week-end), les prix sont-ils plus faux ?
Regardé pour le favori (0,80-0,97) et pour l'outsider (0,03-0,20), par tranche horaire et par jour.
"""
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

SP = sys.argv[1]
sys.path.insert(0, os.path.dirname(__file__))
from analyse_commun import family, fee_rate  # noqa: E402

markets = {m["cid"]: m for m in json.load(open(f"{SP}/sm/markets.json"))}
cases = []  # (heure, jour de semaine, famille, prix, gagné, taux)
for path in glob.glob(f"{SP}/sm/trades/*.json"):
    cid = os.path.basename(path)[:-5]
    m = markets.get(cid)
    if not m:
        continue
    seen = set()
    for t in sorted(json.load(open(path)), key=lambda t: t.get("timestamp") or 0):
        try:
            p, ts, tok = float(t["price"]), int(t["timestamp"]), t["asset"]
        except (KeyError, TypeError, ValueError):
            continue
        if tok not in m["tokens"]:
            continue
        d = datetime.fromtimestamp(ts, tz=timezone.utc)
        key = (tok, d.strftime("%Y%m%d%H"))
        if key in seen:
            continue
        seen.add(key)
        cases.append((d.hour, d.weekday(), family(m), p, 1 if tok == m["winner"] else 0, fee_rate(m["tags"])))
print(len(cases), "échanges retenus (un par marché, issue et heure)")


def table(title, sel, groups):
    print(f"\n### {title}\n| groupe | paris | prix moyen | gagnés | écart | rendement après frais |\n|---|---|---|---|---|---|")
    for name, g in groups:
        v = [c for c in sel if g(c)]
        if len(v) < 200:
            continue
        cost = sum(c[3] + c[5] * c[3] * (1 - c[3]) for c in v)
        win = sum(c[4] for c in v)
        print(f"| {name} | {len(v)} | {sum(c[3] for c in v) / len(v):.3f} | {win / len(v):.3f} | "
              f"{100 * (win / len(v) - sum(c[3] for c in v) / len(v)):+.1f} pts | {100 * (win - cost) / cost:+.1f} % |")


SLOTS = [("0-4 h UTC (soir américain)", range(0, 4)), ("4-8 h UTC (nuit américaine)", range(4, 8)),
         ("8-12 h UTC (matin européen)", range(8, 12)), ("12-16 h UTC", range(12, 16)),
         ("16-20 h UTC", range(16, 20)), ("20-24 h UTC", range(20, 24))]
fav = [c for c in cases if 0.80 <= c[3] <= 0.97]
dog = [c for c in cases if 0.03 <= c[3] <= 0.20]
for name, sel in (("Favori 0,80-0,97", fav), ("Outsider 0,03-0,20", dog)):
    table(f"{name} selon l'heure UTC de l'échange", sel, [(n, lambda c, r=r: c[0] in r) for n, r in SLOTS])
    table(f"{name} : semaine contre week-end", sel, [("lundi-vendredi", lambda c: c[1] < 5), ("samedi-dimanche", lambda c: c[1] >= 5)])
    for fam in ("sport", "politique", "crypto (seuils)"):
        table(f"{name}, {fam}, selon l'heure", [c for c in sel if c[2] == fam], [(n, lambda c, r=r: c[0] in r) for n, r in SLOTS])
