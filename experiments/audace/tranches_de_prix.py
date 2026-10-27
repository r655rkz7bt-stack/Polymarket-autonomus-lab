"""Où se trouve l'avantage selon le prix payé ? (27/10/2026, experiments/audace.md)

1. Toute l'arène (sans tenue de marché ni market_structure), par tranche de prix, sur toute la période et par moitié.
   Les fantômes font souvent les mêmes paris : les z sont trop forts (doublons), le signe et l'ordre de grandeur comptent.
2. Les tranches basses, stratégie par stratégie, et sans les deux fantômes « contrer » de la crypto.
3. Les quatre stratégies qui battent leurs prix, par tranche et par jour.

Usage : bash scripts/fetch_data.sh ; .venv/bin/python experiments/audace/tranches_de_prix.py
"""

from __future__ import annotations

from collections import defaultdict

from commun import SANS, bilan, charger

TRANCHES = ((0, 0.10), (0.10, 0.20), (0.20, 0.30), (0.30, 0.45), (0.45, 0.60), (0.60, 0.80), (0.80, 0.90), (0.90, 0.95),
            (0.95, 1.01))


def ligne(titre: str, paris: list[dict]) -> str:
    b = bilan(paris)
    return (f"  {titre:38s} {b['n']:5d} paris, gagnés {b['gagnes']:5d} / attendus {b['attendus']:7.1f}, "
            f"z {b['z']:+6.2f}, mise plate {b['plat'] * 100:+6.1f} %, euros {b['euros']:+6.0f}")


def main() -> None:
    g = charger()
    tous = [dict(a, s=nom) for nom, x in g.items() if not nom.startswith(SANS) for a in x["trades"]]
    debut = min(a["open"] for a in tous)
    fin = max(a["close"] for a in tous)
    milieu = debut + (fin - debut) / 2
    for titre, sous in (("Tous les paris", tous), ("1re moitié", [a for a in tous if a["open"] < milieu]),
                        ("2e moitié", [a for a in tous if a["open"] >= milieu])):
        print(titre)
        for lo, hi in TRANCHES:
            print(ligne(f"{lo:.2f}-{hi:.2f}", [a for a in sous if lo <= a["price"] < hi]))
    for lo, hi in TRANCHES[:4]:
        par = defaultdict(list)
        for a in tous:
            if lo <= a["price"] < hi:
                par[a["s"].rsplit("_v", 1)[0]].append(a)
        print(f"\nprix {lo:.2f}-{hi:.2f}, par stratégie")
        for nom, paris in sorted(par.items(), key=lambda kv: -len(kv[1]))[:8]:
            print(ligne(nom, paris))
        print(ligne(">> sans contrer_crypto*", [a for k, v in par.items() if not k.startswith("contrer_crypto") for a in v]))
    for nom in ("contrer_crypto_patiente_v1.0.0", "contrer_crypto_v1.0.0", "compteur_tweets_v1.0.0", "moins_de_cartes_v1.0.0"):
        paris = g[nom]["trades"]
        print(f"\n{nom}")
        for lo, hi in ((0, 0.10), (0.10, 0.20), (0.20, 0.30), (0.30, 0.45), (0.45, 0.60), (0.60, 1.01)):
            sous = [a for a in paris if lo <= a["price"] < hi]
            if sous:
                print(ligne(f"{lo:.2f}-{hi:.2f}", sous))
        jours = defaultdict(list)
        for a in paris:
            jours[a["close"].date()].append(a)
        print("  par jour (gagnés/attendus, euros) : " + "  ".join(
            f"{d:%d/%m} {sum(x['won'] for x in v)}/{sum(x['price'] for x in v):.1f} {sum(x['pnl'] for x in v):+.0f}"
            for d, v in sorted(jours.items())))


if __name__ == "__main__":
    main()
