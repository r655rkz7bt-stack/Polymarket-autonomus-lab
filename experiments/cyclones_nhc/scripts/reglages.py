"""Piste n° 63 : log-score modèle contre prix, puis plusieurs réglages (seuil, parts minimales)."""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse

# log-score : tous les couples (avis, jeton OUI) avec un échange, sans seuil
paris, _, _ = analyse.main(seuil=-1.0)
oui = [p for p in paris if p["k"] == 0]
def ll(q, y): q = min(max(q, 0.01), 0.99); return math.log(q if y else 1 - q)
print(f"log-score sur {len(oui)} couples (avis, jeton OUI) : modèle {sum(ll(p['p'], p['gagne']) for p in oui)/len(oui):.3f}"
      f" contre prix {sum(ll(p['cout'], p['gagne']) for p in oui)/len(oui):.3f}")
for w in (0.0, 0.5):
    m = sum(ll(w * p['p'] + (1 - w) * p['cout'] if w else p['cout'], p['gagne']) for p in oui) / len(oui)
mix = sum(ll(0.5 * p['p'] + 0.5 * p['cout'], p['gagne']) for p in oui) / len(oui)
print(f"mélange 50/50 modèle-prix : {mix:.3f}")
n = 0
for seuil in (0.05, 0.10, 0.20, 0.30):
    for pmin in (0, 20, 100):
        ps, _, _ = analyse.main(seuil, pmin); n += 1
        if ps:
            g = sum(p['gagne'] for p in ps); c = sum(p['cout'] for p in ps)
            print(f"seuil {seuil:.2f} parts≥{pmin:>3} : {len(ps):>3} paris, {len(set(p['evenement'] for p in ps)):>2} cyclones, gagnés {g:>3} pour {c:5.1f} payés, rendement {sum(p['gain'] for p in ps)/len(ps):+.1%}")
print(n, "réglages")
