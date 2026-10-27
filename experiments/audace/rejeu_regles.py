"""Rejeu heure par heure des leviers d'audace du principal (27/10/2026, experiments/audace.md).

À chaque heure, une règle choisit des stratégies d'après leurs seules opérations clôturées AVANT cette heure ; le principal
simulé copie les paris qu'elles ouvrent pendant l'heure suivante. Même approximation que experiments/regle_confiance/
rejouer.py : rendement du pari du fantôme (frais compris), sans carnet ni plafonds par famille. « prorata » = mise du
fantôme × part (plafond 5 % de son capital, règle en vigueur) ; « plate » = 10 € par pari.

Usage : bash scripts/fetch_data.sh ; .venv/bin/python experiments/audace/rejeu_regles.py
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import timedelta

from commun import charger, rejouer

from polymarket_agent.arena import family_map

G = charger()
DEBUT = min(g["start"] for g in G.values() if g["start"])
FIN = max(t["close"] for g in G.values() for t in g["trades"])
MILIEU = DEBUT + (FIN - DEBUT) / 2
FAMILLES = family_map()


def famille(nom: str) -> str:
    base = nom.rsplit("_v", 1)[0]
    return FAMILLES.get(base, base)


def stats(done: list[dict], start) -> dict:
    s = rejouer.stats(done)  # n, croissance (euros), t (rendement par mise), z (gagnés contre attendus, regroupé par jour)
    var = sum(t["price"] * (1 - t["price"]) for t in done)
    s["zp"] = (sum(t["won"] for t in done) - sum(t["price"] for t in done)) / math.sqrt(var) if var > 0 else 0.0
    s["start"] = start
    return s


def rejouer_regle(choisir, miser, titre: str, par_famille: bool = False) -> None:
    now = DEBUT.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    gains, mise_totale, n, tenus, ouverts, evenements = [0.0, 0.0], 0.0, 0, set(), [], []
    utilise, contrib = defaultdict(int), defaultdict(float)
    while now <= FIN:
        st = {}
        for nom, g in G.items():
            done = [t for t in g["trades"] if t["close"] <= now]
            if done:
                st[nom] = stats(done, g["start"])
        parts = choisir(st, tenus, now)
        tenus = set(parts)
        for nom, x in parts.items():
            for t in G[nom]["trades"]:
                if now <= t["open"] < now + timedelta(hours=1):
                    s = miser(t, x)
                    if s <= 0:
                        continue
                    r = s * t["pnl"] / t["cost"]
                    mise_totale += s
                    n += 1
                    utilise[nom] += 1
                    contrib[famille(nom)] += r
                    gains[0 if t["open"] < MILIEU else 1] += r
                    ouverts.append((t["open"], t["close"], s))
                    evenements.append((t["close"], r))
        now += timedelta(hours=1)
    engage = max((sum(s for o, c, s in ouverts if o <= tt < c) for tt in sorted(o for o, _, _ in ouverts)[::3]), default=0)
    cap, pic, repli = 1000.0, 1000.0, 0.0
    for _, r in sorted(evenements):
        cap += r
        pic = max(pic, cap)
        repli = max(repli, (pic - cap) / pic)
    total = sum(gains)
    top = ", ".join(f"{k.rsplit('_v', 1)[0]}×{v}" for k, v in sorted(utilise.items(), key=lambda kv: -kv[1])[:4])
    print(f"{titre:50s} {n:4d} paris, misé {mise_totale:6.0f} €, 1re moitié {gains[0]:+5.0f}, 2e {gains[1]:+5.0f}, "
          f"total {total:+5.0f} € ({total / mise_totale * 100 if mise_totale else 0:+5.1f} %/€), engagé au plus {engage:4.0f} €, "
          f"repli {repli:.0%} | {top}")
    if par_famille:
        for f, r in sorted(contrib.items(), key=lambda kv: kv[1]):
            print(f"      famille {f:30s} {r:+6.0f} €")


def en_vigueur(st, tenus, now):
    """Règle d'entrée en vigueur (approchée) : 12 opérations, 12 h, croissance ≥ 0,02, t ≥ 1 ; maintien croissance ≥ 0,
    t ≥ 0 ; 5 places, moitié à égalité moitié au mérite, période d'essai, 70 % au plus."""
    ok = {}
    for nom, s in st.items():
        age = (now - s["start"]).total_seconds() / 3600 if s["start"] else 0
        if (s["n"] >= 12 and age >= 12 and s["growth"] >= 0.02 and s["t"] >= 1.0) or (
                nom in tenus and s["growth"] >= 0 and s["t"] >= 0):
            ok[nom] = s
    best = sorted(ok, key=lambda k: -ok[k]["growth"])[:5]
    total = sum(ok[k]["growth"] for k in best)
    if total <= 0:
        return {}
    return {k: min((0.5 / len(best) + 0.5 * ok[k]["growth"] / total) * (0.5 if ok[k]["n"] < 30 else 1.0), 0.7) for k in best}


def prorata(t, x):
    return x * min(t["cost"], 50.0)


def plate(t, x):
    return 10.0


def par_seuil(cle, seuil, n_min, garder=None):
    def choisir(st, tenus, now):
        ok = {k: s for k, s in st.items() if s["n"] >= n_min and s[cle] >= seuil}
        if garder is not None:
            ok.update({k: st[k] for k in tenus if k in st and st[k][cle] >= garder})
        return {k: 1.0 for k in ok}
    return choisir


def sans(choisir, prefixes):
    def c(st, tenus, now):
        return {k: v for k, v in choisir(st, tenus, now).items() if not k.startswith(prefixes)}
    return c


def familles_perdantes_ecartees(choisir, min_paris=100):
    """Écarte les stratégies dont la FAMILLE (mère et filles, toutes versions) perd contre ses prix sur le passé."""
    def c(st, tenus, now):
        agg = defaultdict(lambda: [0, 0.0])
        for nom, g in G.items():
            done = [t for t in g["trades"] if t["close"] <= now]
            a = agg[famille(nom)]
            a[0] += len(done)
            a[1] += sum(t["won"] - t["price"] for t in done)
        mauvaises = {f for f, (n, ex) in agg.items() if n >= min_paris and ex / n < 0}
        return choisir({k: v for k, v in st.items() if famille(k) not in mauvaises}, tenus, now)
    return c


def main() -> None:
    print(f"Période {DEBUT:%d/%m %H:%M} → {FIN:%d/%m %H:%M} UTC, moitié au {MILIEU:%d/%m %H:%M}\n")
    rejouer_regle(en_vigueur, prorata, "règle en vigueur (prorata, plafond 5 %)", par_famille=True)
    rejouer_regle(en_vigueur, plate, "règle en vigueur, mise plate")
    rejouer_regle(lambda st, h, n: {k: 1.0 for k, s in st.items() if s["n"] >= 15}, plate, "tout copier (≥ 15 op.), mise plate")
    for cle in ("t", "zp", "z"):
        for seuil in (1.0, 1.5, 2.0):
            for n_min in (15, 30):
                rejouer_regle(par_seuil(cle, seuil, n_min), plate, f"{cle} ≥ {seuil}, ≥ {n_min} op., mise plate")
    print("\nLe CHOIX ou la MISE ?")
    rejouer_regle(par_seuil("zp", 1.0, 30), lambda t, x: 0.2 * min(t["cost"], 50.0), "zp ≥ 1, ≥ 30 op., prorata ×0,2")
    rejouer_regle(par_seuil("z", 1.0, 30), lambda t, x: 0.2 * min(t["cost"], 50.0), "z ≥ 1, ≥ 30 op., prorata ×0,2")
    print("\nSans les deux fantômes « contrer » de la crypto")
    rejouer_regle(sans(par_seuil("zp", 1.0, 30), ("contrer_crypto",)), plate, "zp ≥ 1, ≥ 30 op., plate, sans contrer_crypto*")
    rejouer_regle(sans(par_seuil("z", 1.0, 30), ("contrer_crypto",)), plate, "z ≥ 1, ≥ 30 op., plate, sans contrer_crypto*")
    print("\nVariantes")
    rejouer_regle(par_seuil("zp", 1.0, 30, garder=0.0), plate, "zp ≥ 1 (garder tant que ≥ 0), ≥ 30 op., plate")
    rejouer_regle(par_seuil("zp", 1.0, 20), plate, "zp ≥ 1, ≥ 20 op., plate")
    rejouer_regle(par_seuil("zp", 0.5, 30), plate, "zp ≥ 0,5, ≥ 30 op., plate")
    print("\nFamilles qui perdent contre leurs prix écartées (sur le passé seulement)")
    rejouer_regle(familles_perdantes_ecartees(en_vigueur), prorata, "en vigueur, familles perdantes écartées", par_famille=True)
    rejouer_regle(familles_perdantes_ecartees(en_vigueur), plate, "idem, mise plate")


if __name__ == "__main__":
    main()
