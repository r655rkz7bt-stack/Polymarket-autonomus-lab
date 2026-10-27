"""28/10/2026 : quand le résultat d'une échelle FDV devient-il public, par rapport à `closedTime` (règlement Gamma) ? Pour chaque jeton, instant où TOUS les seuils cotent à moins de 0,05
ou plus de 0,95 pour de bon (sans retour) ; heures AVANT le règlement. Si c'est > 24 h avant, les paris « presque sûrs » de D−1 sont des paris sur un résultat déjà public.
Usage : PYTHONPATH=src python temps_reglement.py"""
import sys, statistics
sys.argv_save = sys.argv[:]
exec(open("experiments/fdv_lancement/scripts/analyse.py").read().split("print(\"| réglage")[0])
evs = collections.defaultdict(list)
for d in data: evs[d["m"]["event_id"]].append(d)
res = []
for e, v in evs.items():
    if len(v) < 4: continue
    close = max(d["close"] for d in v if d["close"])
    # instants d'échanges de l'événement
    times = sorted({t for d in v for t in d["st"]})
    def etat(t):
        out = []
        for d in v:
            i = bisect.bisect_right(d["st"], t) - 1
            out.append(d["ser"][i][1] if i >= 0 else 0.5)
        return out
    # dernier instant où au moins un seuil est entre 0,05 et 0,95 (échantillonnage sur les instants d'échange)
    last_open = None
    for t in times:
        if any(0.05 < p < 0.95 for p in etat(t)): last_open = t
    first_trade = times[0]
    res.append((e, v[0]["m"]["event_title"][:32], (close - last_open) / 3600 if last_open else None, (close - first_trade) / 86400, len(v), len(times)))
vals = [r[2] for r in res if r[2] is not None]
print(len(res), "jetons ; heures entre le dernier instant « incertain » et le règlement : médiane", round(statistics.median(vals), 1), "quartiles", [round(x, 1) for x in statistics.quantiles(vals, n=4)])
print("part des jetons dont le résultat est public ≥ 24 h avant le règlement :", round(sum(1 for x in vals if x >= 24) / len(vals), 2), "; ≥ 12 h :", round(sum(1 for x in vals if x >= 12) / len(vals), 2), "; ≥ 6 h :", round(sum(1 for x in vals if x >= 6) / len(vals), 2))
for r in sorted(res, key=lambda r: -(r[2] or 0))[:12]: print(r)
