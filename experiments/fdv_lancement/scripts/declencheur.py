"""28/10/2026 : règle CAUSALE (sans connaître l'heure du règlement) pour jouer le côté « presque sûr » des échelles FDV : à chaque pas de 30 minutes, un jeton est « lancé » quand
l'activité de ses échanges dans les 3 dernières heures (tous seuils) dépasse N échanges ; on achète alors, sur chaque seuil, le côté coté 0,70-0,97 (un pari par marché, premier
échange réel qui l'achète dans les 12 h suivantes). Mesure les rendements et l'écart (heures) entre le déclenchement et le règlement. Usage : PYTHONPATH=src python declencheur.py"""
import sys
sys.argv_save = sys.argv[:]
exec(open("experiments/fdv_lancement/scripts/analyse.py").read().split("print(\"| réglage")[0])
evs = collections.defaultdict(list)
for d in data: evs[d["m"]["event_id"]].append(d)
def declenche(v, N, fenetre=3 * 3600, pas=1800):
    times = sorted(t for d in v for t in d["st"])
    if not times: return None
    t = times[0] + fenetre
    while t <= times[-1] + fenetre:
        i1 = bisect.bisect_right(times, t); i0 = bisect.bisect_right(times, t - fenetre)
        if i1 - i0 >= N: return t
        t += pas
    return None
def declenche_saut(v, J, fenetre=3 * 3600, pas=1800, min_ech=10):
    """Premier instant où un seuil de l'échelle a bougé d'au moins J (en prix du OUI) en 3 h, avec au moins `min_ech` échanges dans la fenêtre sur l'échelle."""
    times = sorted(t for d in v for t in d["st"])
    if not times: return None
    t = times[0] + fenetre
    while t <= times[-1] + fenetre:
        n = bisect.bisect_right(times, t) - bisect.bisect_right(times, t - fenetre)
        if n >= min_ech:
            for d in v:
                i1 = bisect.bisect_right(d["st"], t) - 1; i0 = bisect.bisect_right(d["st"], t - fenetre) - 1
                if i1 >= 0 and i0 >= 0 and i1 > i0 and abs(d["ser"][i1][1] - d["ser"][i0][1]) >= J: return t
        t += pas
    return None
MODE = "saut"
def paris_declenches(N, lo=0.70, hi=0.97, wait=12 * 3600):
    out = []; ecarts = []
    for e, v in evs.items():
        T = declenche_saut(v, N) if MODE == "saut" else declenche(v, N)
        if T is None: continue
        close = max((d["close"] for d in v if d["close"]), default=None)
        if close: ecarts.append((close - T) / 3600)
        for d in v:
            i = bisect.bisect_left(d["st"], T) - 1
            if i < 0 or T - d["st"][i] > 86400: continue
            pyes = d["ser"][i][1]
            for side in ("oui", "non"):
                pside = pyes if side == "oui" else 1 - pyes
                if not lo <= pside <= hi: continue
                arr, tt = (d["by"], d["bys"]) if side == "oui" else (d["bn"], d["bns"])
                j = bisect.bisect_left(tt, T)
                if j >= len(tt) or tt[j] > T + wait: continue
                paid = arr[j][1]
                if not lo <= paid <= hi + 0.03 or paid <= 0: continue
                won = d["won"] if side == "oui" else 1 - d["won"]
                out.append(dict(gain=(won - paid - it.fee(paid, d["rate"])) / paid, cout=paid, evenement=e, mois=dt.datetime.utcfromtimestamp(T).strftime("%Y-%m"), gagne=won, side=side))
    return out, ecarts
print("| N échanges / 3 h | jetons déclenchés (heures avant règlement : médiane, quartiles) | côté | paris | évén. | rendement | t | gagnés/attendus | mois | verdict |")
for N in ((0.15, 0.25, 0.40, 0.60) if MODE == "saut" else (20, 40, 80, 150)):
    b, ec = paris_declenches(N)
    q = statistics.quantiles(ec, n=4) if len(ec) >= 4 else ec
    print(f"N={N}: {len(ec)} jetons, écart déclenchement→règlement médiane {statistics.median(ec):.1f} h, quartiles {[round(x, 1) for x in q]}")
    show(f"N={N} tous côtés", b)
    for side in ("oui", "non"): show(f"N={N} {side.upper()}", [x for x in b if x["side"] == side])
