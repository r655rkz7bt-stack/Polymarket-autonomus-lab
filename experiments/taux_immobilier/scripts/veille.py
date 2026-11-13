"""Pour chaque publication Freddie Mac de 2026, prévision de la publication suivante par le 10 ans (bêta × écart des moyennes lundi-mercredi,
résidu σ) et chance de toucher chaque seuil À CETTE PUBLICATION, contre le prix horaire du marché le mercredi 23 h UTC (veille de la publication)."""
import json, csv, math, bisect
from datetime import datetime, date, timedelta, timezone
ms = json.load(open("donnees/marches.json")); prix = json.load(open("donnees/prix.json"))
ten = {date.fromisoformat(k): v for k, v in json.load(open("donnees/dix_ans.json")).items()}
pm = []
for r in csv.reader(open("donnees/pmms.csv")):
    try: pm.append((datetime.strptime(r[0], "%m/%d/%Y").date(), float(r[1])))
    except Exception: pass
pm = [x for x in pm if x[0] >= date(2025, 6, 1)]
def wk(thu):
    v = [ten[thu - timedelta(days=k)] for k in (1, 2, 3) if thu - timedelta(days=k) in ten]
    return sum(v) / len(v) if v else None
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
BETA, SIG = 0.7, 0.06
def seuil(q):
    import re
    g = re.search(r"hit (\d+\.\d+)% \((HIGH|LOW)\)", q); return float(g.group(1)), g.group(2) == "HIGH"
lignes = []
for i in range(1, len(pm)):
    (d0, p0), (d1, p1) = pm[i - 1], pm[i]
    if d1 < date(2026, 2, 5): continue
    a, b = wk(d0), wk(d1)
    if a is None or b is None: continue
    mu = p0 + BETA * (b - a)
    veille = int(datetime(d1.year, d1.month, d1.day, tzinfo=timezone.utc).timestamp()) - 3600   # mercredi 23 h UTC
    for m in ms:
        k, haut = seuil(m["q"]); h = prix.get(m["id"]) or []
        t = [x[0] for x in h]; j = bisect.bisect_right(t, veille) - 1
        if j < 0 or veille - t[j] > 6 * 3600: continue
        if m["closedTime"] and datetime.fromisoformat(m["closedTime"].replace(" ", "T").replace("+00", "+00:00")).timestamp() < veille: continue
        prior = max(x[1] for x in pm[:i]) if haut else min(x[1] for x in pm[:i])
        if (haut and prior >= k) or (not haut and prior <= k): continue
        pc = 1 - Phi((k - 0.005 - mu) / SIG) if haut else Phi((k + 0.005 - mu) / SIG)   # publié au centième
        touche = (p1 >= k) if haut else (p1 <= k)
        lignes.append((str(d1), m["q"][37:62], round(h[j][1], 3), round(pc, 3), int(touche), round(mu, 2), p1))
for l in lignes:
    if l[3] > 0.05 or l[2] > 0.05 or l[4]: print(l)
print(len(lignes), "couples (publication, seuil) ; touchés", sum(l[4] for l in lignes))
