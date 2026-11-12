"""Test aux vrais échanges : après le préliminaire (publié à 10 h, heure de l'Est ; décision à partir de T = 16 h UTC le jour même),
chance de chaque tranche = P(final dans la tranche) avec final = préliminaire + révision ~ N(0, SD). Premier échange réel de chaque
jeton (OUI ou NON) entre T et la veille du final, de taille >= MIN_PARTS, à un prix <= chance − SEUIL − frais : un pari par jeton.
Usage : test.py [SD] [SEUIL] [MIN_PARTS]"""
import gzip, json, math, sys
from datetime import datetime
from pathlib import Path
from statistics import NormalDist

R = Path(__file__).resolve().parents[1] / "releves"
SD = float(sys.argv[1]) if len(sys.argv) > 1 else 1.8
SEUIL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
MIN = float(sys.argv[3]) if len(sys.argv) > 3 else 10
N = NormalDist(0, SD)
# préliminaires lus dans la presse (releves/preliminaires.json, titres relus à la main) ; finales : tbmics.csv
PRE = {"June": (48.9, "2026-06-12"), "July": (54.4, "2026-07-10"), "September": (47.8, "2026-09-11"), "October": (46.3, "2026-10-09")}
FIN = {"June": 49.5, "July": 55.2, "September": 48.1, "October": 48.0}


def bornes(t):
    t = t.replace("–", " to ").replace("≥", "").replace("+", "").strip()
    if t.startswith("<"):
        return (-1e9, float(t[1:]))
    if " to " in t:
        a, b = t.split(" to ")
        return (float(a), float(b) + 0.1)
    return (float(t), 1e9)


def frais(p):  # barème « economics » de Polymarket (≈ 0,05 · p · (1 − p) par part, ordre de grandeur, prudence)
    return 0.05 * p * (1 - p)


ms = json.load(gzip.open(R / "marches.json.gz"))
ex = json.load(gzip.open(R / "echanges.json.gz"))
paris = []
for m in ms:
    mo = m["titre"].split(" - ")[1].split()[0]
    if mo not in PRE or not m["tokens"]:
        continue
    pre, d = PRE[mo]
    T = datetime.fromisoformat(d + "T16:00:00+00:00").timestamp()
    lo, hi = bornes(m["tranche"])
    p_yes = N.cdf(hi - 0.05 - pre) - N.cdf(lo - 0.05 - pre)
    issue = 1 if json.loads(m["prix"])[0] in ("1", 1) else 0
    for side, tok, est, gagne in ((0, m["tokens"][0], p_yes, issue), (1, m["tokens"][1], 1 - p_yes, 1 - issue)):
        tr = sorted((r for r in ex.get(m["event"], []) if r["asset"] == tok and float(r["timestamp"]) >= T
                     and float(r["size"]) >= MIN), key=lambda r: float(r["timestamp"]))
        for r in tr:
            p = float(r["price"])
            if 0.02 <= p <= 0.98 and est - p - frais(p) >= SEUIL:
                paris.append((mo, m["tranche"], "OUI" if side == 0 else "NON", p, est, gagne, float(r["size"])))
                break
n = len(paris)
cout = sum(x[3] for x in paris); gain = sum(x[5] - x[3] - frais(x[3]) for x in paris)
print(f"SD {SD} seuil {SEUIL} parts >= {MIN} : {n} paris, {sum(x[5] for x in paris)} gagnés pour {cout:.2f} attendus (prix), "
      f"{sum(x[4] for x in paris):.2f} (modèle), rendement {gain / cout * 100 if cout else 0:+.1f} % par mise")
for x in paris:
    print("  ", x[0], f"{x[1]:14s}", x[2], f"prix {x[3]:.3f} chance {x[4]:.3f} issue {x[5]} parts {x[6]:.0f}")
