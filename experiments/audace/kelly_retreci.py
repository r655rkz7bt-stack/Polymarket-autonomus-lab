"""Rejeu : mise de Kelly sur l'avantage MESURÉ et rétréci (27/10/2026, experiments/audace.md).

À chaque heure, sur le passé seul : avantage de chaque stratégie = (gagnés − Σ prix) / paris, rétréci vers la moyenne de
sa famille de prix (favoris ≥ 0,80, milieu, pas chers < 0,40 ; « global » = une seule famille) par la méthode des moments.
Chaque pari suivant d'une stratégie à avantage rétréci positif est copié à k × e / (1 − p) du capital, plafonné par pari.

Usage : bash scripts/fetch_data.sh ; .venv/bin/python experiments/audace/kelly_retreci.py
"""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from commun import SANS, charger

G = charger()
DEBUT = min(g["start"] for g in G.values() if g["start"])
FIN = max(t["close"] for g in G.values() for t in g["trades"])
MILIEU = DEBUT + (FIN - DEBUT) / 2
BANDES = ((0.8, 1.01), (0.4, 0.8), (0.0, 0.4))


def bande(p: float) -> int:
    return next(i for i, (lo, hi) in enumerate(BANDES) if lo <= p < hi)


def dl(lignes):
    if len(lignes) < 3:
        return None
    w = [1 / v for _, v in lignes]
    sw = sum(w)
    mu = sum(wi * e for wi, (e, _) in zip(w, lignes)) / sw
    q = sum(wi * (e - mu) ** 2 for wi, (e, _) in zip(w, lignes))
    return mu, max(0.0, (q - (len(lignes) - 1)) / (sw - sum(wi * wi for wi in w) / sw))


def retrecis(now, n_min: int, global_: bool) -> dict[str, float]:
    st = {}
    for nom, g in G.items():
        if nom.startswith(SANS):
            continue
        done = [t for t in g["trades"] if t["close"] <= now]
        if len(done) < n_min:
            continue
        n = len(done)
        st[nom] = (sum(t["won"] - t["price"] for t in done) / n,
                   max(sum(t["price"] * (1 - t["price"]) for t in done) / n / n, 1e-6),
                   bande(sum(t["price"] for t in done) / n))
    tout = dl([(e, v) for e, v, _ in st.values()])
    out = {}
    for b in range(3):
        fam = [(e, v) for e, v, bb in st.values() if bb == b]
        a_priori = tout if global_ else (dl(fam) if len(fam) >= 5 else tout)
        if a_priori is None:
            continue
        mu, tau2 = a_priori
        for nom, (e, v, bb) in st.items():
            if bb == b:
                out[nom] = mu + (tau2 / (tau2 + v) if tau2 > 0 else 0.0) * (e - mu)
    return out


def rejouer(k: float, plafond: float, global_: bool, n_min: int = 10) -> None:
    now = DEBUT.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    gains, mise_totale, n, ouverts, evenements, par = [0.0, 0.0], 0.0, 0, [], [], defaultdict(float)
    while now <= FIN:
        for nom, e in retrecis(now, n_min, global_).items():
            if e <= 0:
                continue
            for t in G[nom]["trades"]:
                if now <= t["open"] < now + timedelta(hours=1):
                    s = min(plafond, k * e / max(1 - t["price"], 0.02)) * 1000
                    if s < 0.5:
                        continue
                    r = s * t["pnl"] / t["cost"]
                    mise_totale += s
                    n += 1
                    par[nom] += s
                    gains[0 if t["open"] < MILIEU else 1] += r
                    ouverts.append((t["open"], t["close"], s))
                    evenements.append((t["close"], r))
        now += timedelta(hours=1)
    cap, pic, repli = 1000.0, 1000.0, 0.0
    for _, r in sorted(evenements):
        cap += r
        pic = max(pic, cap)
        repli = max(repli, (pic - cap) / pic)
    engage = max((sum(s for o, c, s in ouverts if o <= tt < c) for tt in sorted(o for o, _, _ in ouverts)[::3]), default=0)
    total = sum(gains)
    top = ", ".join(f"{k_.rsplit('_v', 1)[0]} {v:.0f} €" for k_, v in sorted(par.items(), key=lambda kv: -kv[1])[:3])
    print(f"{'global' if global_ else 'familles'} k={k} plafond {plafond:.0%} : {n} paris, misé {mise_totale:.0f} €, "
          f"1re moitié {gains[0]:+.0f}, 2e {gains[1]:+.0f}, total {total:+.0f} €, engagé au plus {engage:.0f} €, "
          f"repli {repli:.0%} | {top}")


if __name__ == "__main__":
    for global_ in (False, True):
        for k in (0.5, 1.0):
            for plafond in (0.02, 0.05):
                rejouer(k, plafond, global_)
