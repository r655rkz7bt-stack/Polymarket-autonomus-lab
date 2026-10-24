"""Tables du modèle `seismes_marche` (à relancer chaque mois) -> src/polymarket_agent/seismes_tables.json
 jour    : pour chaque heure UTC h (0..24) et seuil x, part des jours des 3 dernières années où AUCUN séisme >= x n'a eu lieu entre h h et minuit
 semaine : Gamma-Poisson (alpha, beta) du nombre de séismes >= 5,5 et >= 6,5 par semaine, 156 dernières semaines"""
import sys, json, bisect, statistics as st
sys.path.insert(0, "experiments/seismes/scripts")
from commun import *
from jour import SEUILS, no_event_prob, DAY
today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
d0 = int(today.timestamp())
out = {"cree_le": today.date().isoformat(), "jour": {}, "semaine": {}}
for h in range(0, 25):
    out["jour"][str(h)] = {str(x): round(no_event_prob(d0, h, x) if h < 24 else 1.0, 4) for x in SEUILS}
W = 7 * DAY
for mag in (5.5, 6.5):
    cs = [count(d0 - k * W, d0 - (k - 1) * W, mag) for k in range(1, 157)]
    m = st.mean(cs); v = max(st.pvariance(cs), m * 1.05); alpha = m * m / (v - m)
    out["semaine"][str(mag)] = {"alpha": round(alpha, 4), "beta": round(alpha / m, 4), "moyenne": round(m, 3)}
json.dump(out, open("src/polymarket_agent/seismes_tables.json", "w"), indent=1)
print(json.dumps(out["semaine"]), out["jour"]["12"])
