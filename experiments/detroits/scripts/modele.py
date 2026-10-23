"""Modèle de la moyenne sur 7 jours à h jours (marche empirique) : P(tranche) d'après les écarts passés.
Usage : modele.py <csv> <dernier_jour> <jour_cible> [fenetre_jours]"""
import csv, sys, datetime as dt, math

def charge(p):
    rows = list(csv.DictReader(open(p)))
    d = {r["jour"]: int(r["n_total"]) for r in rows}
    jours = sorted(d)
    v = [d[j] for j in jours]
    ma = [None] * 6 + [sum(v[i - 6:i + 1]) / 7 for i in range(6, len(v))]
    return jours, v, ma

def ecarts(jours, ma, h, debut=None):
    out = []
    for i in range(len(jours) - h):
        if ma[i] is None or ma[i + h] is None: continue
        if debut and jours[i] < debut: continue
        out.append((jours[i], ma[i], ma[i + h]))
    return out

def tranche_probas(base, es, bornes):
    """bornes : liste de (nom, bas, haut) ; cible = base + écart observé."""
    c = {n: 0 for n, _, _ in bornes}
    for e in es:
        t = base + e
        for n, lo, hi in bornes:
            if lo <= t < hi: c[n] += 1
    return {n: k / len(es) for n, k in c.items()}

if __name__ == "__main__":
    p, last, cible = sys.argv[1:4]
    fen = int(sys.argv[4]) if len(sys.argv) > 4 else 730
    jours, v, ma = charge(p)
    h = (dt.date.fromisoformat(cible) - dt.date.fromisoformat(last)).days
    i = jours.index(last)
    base = ma[i]
    debut = (dt.date.fromisoformat(last) - dt.timedelta(days=fen)).isoformat()
    es = [b - a for _, a, b in ecarts(jours[: i + 1], ma[: i + 1], h, debut)]
    es.sort()
    print(f"dernier jour {last} (MA7 {base:.2f}), h = {h} j, {len(es)} écarts depuis {debut} ; médiane {es[len(es)//2]:+.2f}, écart-type "
          f"{(sum((e - sum(es)/len(es))**2 for e in es)/len(es))**.5:.2f}, q10 {es[len(es)//10]:+.1f}, q90 {es[9*len(es)//10]:+.1f}")
    B = [("<20", -1e9, 20), ("20-24", 20, 25), ("25-29", 25, 30), ("30-34", 30, 35), ("35+", 35, 1e9)]
    print({k: round(x, 3) for k, x in tranche_probas(base, es, B).items()})
