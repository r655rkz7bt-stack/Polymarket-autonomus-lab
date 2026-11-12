"""« Trust the process » (demande d'Etienne, 01/11/2026) : le principal coupe-t-il trop vite une stratégie qui perd ?

Rejeu heure par heure (même outil que experiments/audace/rejeu_regles.py, mêmes approximations) de la règle d'entrée en
vigueur, avec des règles de SORTIE plus patientes :
- en vigueur : on garde tant que croissance ≥ 0 et t ≥ 0 ;
- patiente : une fois entrée, gardée tant que la croissance reste ≥ −0,10 (puis −0,25, puis toujours) ;
- engagement minimal : gardée au moins 3 ou 7 jours après l'entrée, quoi qu'il arrive ;
- sans période d'essai (pleine part dès l'entrée).
Usage : bash scripts/fetch_data.sh ; .venv/bin/python experiments/confiance_processus/rejeu_patience.py
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "audace"))

import rejeu_regles as rr  # noqa: E402

ENTREE = {}  # stratégie → heure d'entrée (pour l'engagement minimal)


def regle(sortie_croissance=0.0, sortie_t=0.0, jours_min=0.0, essai=True, places=5):
    def choisir(st, tenus, now):
        ok = {}
        for nom, s in st.items():
            age = (now - s["start"]).total_seconds() / 3600 if s["start"] else 0
            entre = s["n"] >= 12 and age >= 12 and s["growth"] >= 0.02 and s["t"] >= 1.0
            garde = nom in tenus and (
                (sortie_croissance is None or s["growth"] >= sortie_croissance)
                and (sortie_t is None or s["t"] >= sortie_t)
                or (now - ENTREE.get(nom, now)) < timedelta(days=jours_min))
            if entre or garde:
                ok[nom] = s
                ENTREE.setdefault(nom, now)
        for nom in list(ENTREE):
            if nom not in ok:
                del ENTREE[nom]
        tenus_gardes = [k for k in ok if k in tenus]
        nouveaux = sorted((k for k in ok if k not in tenus), key=lambda k: -ok[k]["growth"])
        best = (tenus_gardes + nouveaux)[:places]
        total = sum(max(ok[k]["growth"], 0.0) for k in best)
        parts = {}
        for k in best:
            merite = max(ok[k]["growth"], 0.0) / total if total > 0 else 1 / len(best)
            x = 0.5 / len(best) + 0.5 * merite
            if essai and ok[k]["n"] < 30:
                x *= 0.5
            parts[k] = min(x, 0.7)
        return parts
    return choisir


def main() -> None:
    print(f"Période {rr.DEBUT:%d/%m %H:%M} → {rr.FIN:%d/%m %H:%M} UTC, moitié au {rr.MILIEU:%d/%m %H:%M}\n")
    rr.rejouer_regle(rr.en_vigueur, rr.prorata, "en vigueur (sortie : croissance < 0 ou t < 0)", par_famille=True)
    for titre, kw in (("patiente : sortie seulement sous −10 %", dict(sortie_croissance=-0.10, sortie_t=None)),
                      ("patiente : sortie seulement sous −25 %", dict(sortie_croissance=-0.25, sortie_t=None)),
                      ("jamais de sortie une fois entrée", dict(sortie_croissance=None, sortie_t=None)),
                      ("en vigueur + engagement minimal 3 jours", dict(jours_min=3)),
                      ("en vigueur + engagement minimal 7 jours", dict(jours_min=7)),
                      ("en vigueur sans période d'essai", dict(essai=False)),
                      ("patiente −25 % sans période d'essai", dict(sortie_croissance=-0.25, sortie_t=None, essai=False))):
        ENTREE.clear()
        rr.rejouer_regle(regle(**kw), rr.prorata, titre)
    print("\nMême chose à mise plate (10 € par pari)")
    for titre, kw in (("en vigueur (approchée)", dict()), ("jamais de sortie une fois entrée", dict(sortie_croissance=None, sortie_t=None))):
        ENTREE.clear()
        rr.rejouer_regle(regle(**kw), rr.plate, titre)


if __name__ == "__main__":
    main()


def voisins() -> None:
    """Le seuil de −10 % est-il un coup de chance ? Seuils voisins, avec et sans période d'essai."""
    for seuil in (-0.05, -0.075, -0.10, -0.125, -0.15, -0.20):
        for essai in (True, False):
            ENTREE.clear()
            rr.rejouer_regle(regle(sortie_croissance=seuil, sortie_t=None, essai=essai), rr.prorata,
                             f"sortie sous {seuil:+.1%}, essai {'oui' if essai else 'non'}")


def mise_mesuree(part_min, part_max=1.0, fictifs=30, suppose=0.035):
    """La mise du principal multipliée par avantage mesuré / avantage supposé (arena.measured_stake), bornée [part_min, part_max] ;
    l'avantage mesuré = Σ(gagné − prix) / (opérations + paris fictifs), sur les paris clôturés AVANT l'ouverture du pari."""
    def miser(t, x):
        done = [u for u in rr.G[t["_nom"]]["trades"] if u["close"] <= t["open"]]
        exces = sum(u["won"] - u["price"] for u in done)
        ratio = (exces / (len(done) + fictifs)) / suppose
        return x * min(t["cost"], 50.0) * min(part_max, max(part_min, ratio))
    return miser


def planchers() -> None:
    """Mise à proportion de l'avantage mesuré (règle en vigueur, plancher 0) contre des planchers plus hauts."""
    for nom, g in rr.G.items():
        for t in g["trades"]:
            t["_nom"] = nom
    for titre, kw in (("sortie en vigueur", dict()), ("sortie sous −10 %", dict(sortie_croissance=-0.10, sortie_t=None))):
        for pm in (0.0, 0.25, 0.5, 1.0):
            ENTREE.clear()
            rr.rejouer_regle(regle(**kw), mise_mesuree(pm), f"{titre}, mise mesurée, plancher {pm}")


def regle_v2(entree="croissance", n_min=12, z_min=1.0, garder="croissance", essai=True, places=5):
    """Entrée au capital principal : « croissance » (règle en vigueur : 12 opérations, +2 %, t ≥ 1) ou « bat ses prix »
    (zp, gagnés contre attendus, ≥ z_min après n_min opérations). Maintien : croissance ≥ −10 % (en vigueur) ou zp ≥ 0."""
    def choisir(st, tenus, now):
        ok = {}
        for nom, s in st.items():
            age = (now - s["start"]).total_seconds() / 3600 if s["start"] else 0
            if entree == "croissance":
                entre = s["n"] >= n_min and age >= 12 and s["growth"] >= 0.02 and s["t"] >= 1.0
            else:
                entre = s["n"] >= n_min and s["zp"] >= z_min
            garde = nom in tenus and (s["growth"] >= -0.10 if garder == "croissance" else s["zp"] >= 0.0)
            if entre or garde:
                ok[nom] = s
        cle = (lambda k: -ok[k]["growth"]) if entree == "croissance" else (lambda k: -ok[k]["zp"])
        tenus_gardes = [k for k in ok if k in tenus]
        best = (tenus_gardes + sorted((k for k in ok if k not in tenus), key=cle))[:places]
        poids = {k: max(ok[k]["growth"] if entree == "croissance" else ok[k]["zp"], 0.0) for k in best}
        total = sum(poids.values())
        parts = {}
        for k in best:
            x = 0.5 / len(best) + 0.5 * (poids[k] / total if total > 0 else 1 / len(best))
            if essai and ok[k]["n"] < 30:
                x *= 0.5
            parts[k] = min(x, 0.7)
        return parts
    return choisir


def v2() -> None:
    """Les deux changements demandés par Etienne le 12/11/2026 : juger sur « bat ses prix » ; alléger les freins."""
    for nom, g in rr.G.items():
        for t in g["trades"]:
            t["_nom"] = nom
    print(f"Période {rr.DEBUT:%d/%m %H:%M} → {rr.FIN:%d/%m %H:%M} UTC, moitié au {rr.MILIEU:%d/%m %H:%M}\n")
    essais = (("en vigueur (croissance, maintien −10 %, essai)", dict()),
              ("allégée : 8 opérations, sans essai", dict(n_min=8, essai=False)),
              ("bat ses prix : zp ≥ 1, 12 op., maintien −10 %", dict(entree="zp")),
              ("bat ses prix : zp ≥ 1, 20 op., maintien −10 %", dict(entree="zp", n_min=20)),
              ("bat ses prix : zp ≥ 1,5, 20 op., maintien −10 %", dict(entree="zp", n_min=20, z_min=1.5)),
              ("bat ses prix : zp ≥ 1, 12 op., maintien zp ≥ 0", dict(entree="zp", garder="zp")),
              ("bat ses prix + allégée : zp ≥ 1, 8 op., sans essai", dict(entree="zp", n_min=8, essai=False)),
              ("bat ses prix + allégée : zp ≥ 1, 20 op., sans essai", dict(entree="zp", n_min=20, essai=False)))
    for titre, kw in essais:
        for pm in (0.25, 1.0):
            rr.rejouer_regle(regle_v2(**kw), mise_mesuree(pm), f"{titre}, plancher {pm}")
