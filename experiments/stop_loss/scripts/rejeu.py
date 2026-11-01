"""Rejeu de stop-loss sur les positions réelles de l'arène (demande d'Etienne, 01/11/2026).

Pour chaque position réglée (releve.py) : on suit le prix du jeton (CLOB, pas de 5 min) entre l'achat et le règlement ;
une règle de sortie regarde SEULEMENT le passé à chaque instant ; si elle se déclenche, on vend au prix du moment moins
`GLISSE` (écart achat-vente + frais), sinon on garde jusqu'au règlement (paiement réel). Comparaison au « garder ».
Usage : .venv/bin/python experiments/stop_loss/scripts/rejeu.py [glisse]
"""

from __future__ import annotations

import bisect
import gzip
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DONNEES = ROOT / "experiments" / "stop_loss" / "donnees"
GLISSE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.015


def charger():
    pos = json.load(gzip.open(DONNEES / "positions.json.gz", "rt"))
    out = []
    for p in pos:
        f = DONNEES / "prix" / f"{p['jeton']}.json.gz"
        if not f.exists():
            continue
        pts = json.load(gzip.open(f, "rt"))
        if not pts:
            continue
        ts = [t for t, _ in pts]
        i, j = bisect.bisect_right(ts, p["achat"]), bisect.bisect_left(ts, p["reglement"])
        apres = pts[i:j]
        avant = [x for t, x in pts[bisect.bisect_left(ts, p["achat"] - 86400):i]]
        if p["parts"] <= 0 or p["cout"] <= 0:
            continue
        p["c"] = p["cout"] / p["parts"]
        p["chemin"] = apres
        p["sigma"] = statistics.pstdev(avant) if len(avant) >= 6 else None
        out.append(p)
    return out


def garder(p):
    return p["parts"] * p["paiement"] - p["cout"]


def rejouer(P, regle, nom, glisse=GLISSE):
    """regle(p, t, prix, etat) -> True pour vendre maintenant."""
    tot, base, n_sortie, mise, sortis_gagnants, sortis = 0.0, 0.0, 0, 0.0, 0.0, []
    moities = [0.0, 0.0]
    milieu = sorted(p["achat"] for p in P)[len(P) // 2]
    for p in P:
        etat = {"max": p["c"]}
        res = garder(p)
        for t, x in p["chemin"]:
            if regle(p, t, x, etat):
                res = p["parts"] * max(0.0, x - glisse) - p["cout"]
                n_sortie += 1
                sortis.append(p)
                break
            etat["max"] = max(etat["max"], x)
        gain = res - garder(p)
        tot += gain
        moities[0 if p["achat"] < milieu else 1] += gain
        mise += p["cout"]
    g = sum(1 for p in sortis if p["paiement"] == 1.0)
    print(f"{nom:52s} sorties {n_sortie:5d} ({n_sortie / len(P):5.1%}), dont gagnantes au règlement {g:4d} | "
          f"écart au « garder » {tot:+8.0f} € ({tot / mise:+6.2%} par euro misé), moitiés {moities[0]:+6.0f} / {moities[1]:+6.0f}")
    return tot


def calibration(P):
    """Le marché sous-réagit-il ? Pour les positions dont le prix est tombé à x (première fois), part gagnée ensuite contre x."""
    print("\nAprès une chute : chance réelle de gagner contre le prix du moment (si gagnés < prix, couper aide)")
    for d in (0.05, 0.10, 0.20, 0.30):
        n, gagne, prix = 0, 0.0, 0.0
        for p in P:
            for t, x in p["chemin"]:
                if x <= p["c"] - d:
                    n += 1
                    gagne += p["paiement"]
                    prix += x
                    break
        if n:
            se = math.sqrt(max(prix / n * (1 - prix / n), 1e-9) / n)
            print(f"  prix tombé de {d:.2f} sous le prix payé : {n:5d} positions, gagnées {gagne / n:.3f} pour un prix moyen "
                  f"{prix / n:.3f} (écart {gagne / n - prix / n:+.3f}, ±{1.96 * se:.3f})")


def main():
    P = charger()
    print(f"{len(P)} positions avec historique, glissement à la vente {GLISSE}\n")
    base = sum(garder(p) for p in P)
    print(f"Garder jusqu'au règlement : {base:+.0f} € sur {sum(p['cout'] for p in P):.0f} € misés\n")
    calibration(P)
    print()
    for d in (0.05, 0.10, 0.15, 0.20, 0.30):
        rejouer(P, lambda p, t, x, e, d=d: x <= p["c"] - d, f"stop fixe −{d:.2f}")
    for r in (0.2, 0.35, 0.5):
        rejouer(P, lambda p, t, x, e, r=r: x <= p["c"] * (1 - r), f"stop relatif −{r:.0%}")
    for m in (0.05, 0.10, 0.20):
        rejouer(P, lambda p, t, x, e, m=m: p["prob_low"] is not None and x <= p["prob_low"] - m,
                f"sous la borne basse de la stratégie −{m:.2f}")
    for k in (2, 3, 4):
        rejouer(P, lambda p, t, x, e, k=k: p["sigma"] is not None and x <= p["c"] - max(0.03, k * p["sigma"]),
                f"volatilité : −{k}×écart-type des 24 h d'avant")
    for d in (0.10, 0.20):
        rejouer(P, lambda p, t, x, e, d=d: x <= e["max"] - d, f"suiveur −{d:.2f} depuis le plus haut")
    for d in (0.10, 0.20):
        rejouer(P, lambda p, t, x, e, d=d: p["coup_envoi"] is not None and t < p["coup_envoi"] and x <= p["c"] - d,
                f"stop −{d:.2f} AVANT le coup d'envoi seulement")
        rejouer(P, lambda p, t, x, e, d=d: p["coup_envoi"] is not None and t >= p["coup_envoi"] and x <= p["c"] - d,
                f"stop −{d:.2f} PENDANT le match seulement")
    print("\nPar tranche de prix payé (stop fixe −0,10)")
    for lo, hi in ((0, 0.3), (0.3, 0.6), (0.6, 0.8), (0.8, 0.9), (0.9, 1.01)):
        sub = [p for p in P if lo <= p["c"] < hi]
        if sub:
            rejouer(sub, lambda p, t, x, e: x <= p["c"] - 0.10, f"  payé {lo:.1f}-{hi:.1f} ({len(sub)} positions)")


if __name__ == "__main__":
    main()
