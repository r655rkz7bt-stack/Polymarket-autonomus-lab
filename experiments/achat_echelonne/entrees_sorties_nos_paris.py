"""Entrées et sorties échelonnées rejouées sur nos vrais paris « favori » (chemin de prix à la minute)."""
import json
import math
import statistics as st
import sys
from datetime import datetime

D = "donnees/ech"
rows = [r for r in json.load(open(f"{D}/paths.json")) if len(r["chemin"]) > 3]
SPREAD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
RATE = 0.04
fee = lambda p: RATE * p * (1 - p)


def ts(x):
    return datetime.fromisoformat(x).timestamp()


def buy_cost(p):
    q = min(p + SPREAD, 0.995)
    return q + fee(q)


def sell_value(p):
    q = max(p - SPREAD, 0.005)
    return q - fee(q)


def first(path, t0, cond):
    for t, p in path:
        if t > t0 and cond(p):
            return t, p
    return None


def price_at(path, when):
    last = None
    for t, p in path:
        if t > when:
            break
        last = p
    return last


def run(r, kind, a):
    """→ (gain, mise) pour 1 € (ou moins si une tranche n'a pas eu lieu)."""
    path, pay, p0, t0 = r["chemin"], r["paiement"], r["prix"], ts(r["ouvert"])
    c0 = p0 + fee(p0)  # premier achat au prix réellement payé
    end = path[-1][0]
    if kind == "base":
        return (pay - c0) / c0, 1.0
    if kind == "dca":  # 3 tranches : maintenant, +a h, +2a h
        gain, stake = (pay - c0) / c0 / 3, 1 / 3
        for k in (1, 2):
            when = t0 + k * a * 3600
            p = price_at(path, when) if when < end else None
            if p is not None and 0.02 < p < 0.98:
                c = buy_cost(p)
                gain += (pay - c) / c / 3
                stake += 1 / 3
        return gain, stake
    if kind in ("baisse", "hausse"):  # moitié maintenant, moitié si le prix bouge de a
        gain, stake = (pay - c0) / c0 / 2, 0.5
        hit = first(path, t0, (lambda p: p <= p0 - a) if kind == "baisse" else (lambda p: p >= p0 + a))
        if hit and 0.02 < hit[1] < 0.98:
            c = buy_cost(hit[1])
            gain += (pay - c) / c / 2
            stake += 0.5
        return gain, stake
    if kind == "stop":
        hit = first(path, t0, lambda p: p <= p0 - a)
        return ((sell_value(hit[1]) - c0) / c0 if hit else (pay - c0) / c0), 1.0
    if kind == "gain":  # vendre quand le prix atteint a
        hit = first(path, t0, lambda p: p >= a)
        return ((sell_value(hit[1]) - c0) / c0 if hit else (pay - c0) / c0), 1.0
    if kind == "suiveur":  # stop suiveur : a sous le plus haut atteint
        top = p0
        for t, p in path:
            if t <= t0:
                continue
            top = max(top, p)
            if p <= top - a and p < 0.97:
                return (sell_value(p) - c0) / c0, 1.0
        return (pay - c0) / c0, 1.0


VARIANTS = [("base", 0)] + [("dca", a) for a in (0.5, 2, 6)] + [("baisse", a) for a in (0.05, 0.10, 0.20)] \
    + [("hausse", a) for a in (0.03, 0.05)] + [("stop", a) for a in (0.10, 0.20, 0.30, 0.40)] \
    + [("gain", a) for a in (0.97, 0.98, 0.99)] + [("suiveur", a) for a in (0.10, 0.20)]
base = [run(r, "base", 0)[0] for r in rows]
print(f"{len(rows)} paris, écart {SPREAD}, frais {RATE}·p(1−p) ; gagnés {sum(r['paiement'] > 0 for r in rows)}")
print(f"{'variante':14} {'rendement':>9} {'t':>6} {'pire':>6} {'mise moy':>8} | écart avec la base (même pari) : moyenne, t, paris changés")
for kind, a in VARIANTS:
    res = [run(r, kind, a) for r in rows]
    per = [g / s for g, s in res]  # rendement par euro réellement misé
    m, sd = st.mean(per), st.stdev(per)
    diff = [g / s - b for (g, s), b in zip(res, base)]
    changed = sum(1 for d in diff if abs(d) > 1e-9)
    dm, dsd = st.mean(diff), st.stdev(diff)
    tdiff = dm / dsd * math.sqrt(len(diff)) if dsd > 0 else 0
    print(f"{kind + ' ' + str(a):14} {m:+9.3f} {m / sd * math.sqrt(len(per)):+6.2f} {min(per):+6.2f} {st.mean(s for _, s in res):8.2f} | "
          f"{dm:+.4f} t {tdiff:+.2f} ({changed} paris)")
# Que fait le prix après une baisse de 10 points ? (retour à la moyenne ou suite)
after = []
for r in rows:
    hit = first(r["chemin"], ts(r["ouvert"]), lambda p, p0=r["prix"]: p <= p0 - 0.10)
    if hit:
        after.append((hit[1], r["paiement"]))
if after:
    print(f"\naprès une baisse de 10 points : {len(after)} paris, prix moyen à ce moment {st.mean(p for p, _ in after):.3f}, "
          f"gagnés ensuite {st.mean(w for _, w in after):.3f}")
