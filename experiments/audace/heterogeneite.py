"""Les écarts entre stratégies sont-ils réels ou du hasard ? (27/10/2026, experiments/audace.md)

Avantage d'une stratégie = (gagnés − Σ prix payés) / paris, frais compris. Méthode des moments (DerSimonian-Laird) :
Q compare la dispersion observée entre stratégies à celle que le seul hasard donne (Q ≈ degrés de liberté : aucun écart
réel) ; τ = écart réel entre stratégies. Puis chaque avantage est rétréci vers la moyenne (bayésien empirique).

Usage : bash scripts/fetch_data.sh ; .venv/bin/python experiments/audace/heterogeneite.py
"""

from __future__ import annotations

import math

from commun import SANS, charger


def dl(lignes):
    """(moyenne pondérée, Q, τ²) d'une liste de (avantage, variance)."""
    w = [1 / v for _, v in lignes]
    sw = sum(w)
    mu = sum(wi * e for wi, (e, _) in zip(w, lignes)) / sw
    q = sum(wi * (e - mu) ** 2 for wi, (e, _) in zip(w, lignes))
    tau2 = max(0.0, (q - (len(lignes) - 1)) / (sw - sum(wi * wi for wi in w) / sw))
    return mu, q, tau2


def main() -> None:
    lignes = []
    for nom, g in charger().items():
        t = g["trades"]
        if len(t) < 15 or nom.startswith(SANS):
            continue
        n = len(t)
        lignes.append((nom, n, sum(a["won"] - a["price"] for a in t) / n,
                       sum(a["price"] * (1 - a["price"]) for a in t) / n / n, sum(a["price"] for a in t) / n))
    mu, q, tau2 = dl([(e, v) for _, _, e, v, _ in lignes])
    print(f"{len(lignes)} stratégies : avantage moyen {mu * 100:+.2f} points par pari, Q = {q:.1f} pour "
          f"{len(lignes) - 1} degrés de liberté, τ = {math.sqrt(tau2) * 100:.2f} points")
    for titre, lo, hi in (("favoris ≥ 0,80", 0.8, 1.01), ("milieu 0,40-0,80", 0.4, 0.8), ("pas chers < 0,40", 0, 0.4)):
        sous = [(e, v) for _, _, e, v, p in lignes if lo <= p < hi]
        if len(sous) >= 3:
            m, qq, _ = dl(sous)
            print(f"  {titre:18s} (prix moyen de la stratégie) : {len(sous):3d} stratégies, avantage moyen {m * 100:+.2f} "
                  f"points, Q {qq:.1f} pour {len(sous) - 1}")
    print("\nAvantage rétréci vers la moyenne (les 12 meilleurs) :")
    post = sorted(((mu + (tau2 / (tau2 + v) if tau2 else 0.0) * (e - mu), nom, n, e, p) for nom, n, e, v, p in lignes),
                  reverse=True)
    for e_post, nom, n, e, p in post[:12]:
        print(f"  {nom[:46]:46s} {n:4d} paris, prix moyen {p:.2f}, brut {e * 100:+5.1f}, rétréci {e_post * 100:+5.2f} points")


if __name__ == "__main__":
    main()
