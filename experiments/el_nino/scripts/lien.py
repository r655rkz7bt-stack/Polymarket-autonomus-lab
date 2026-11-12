"""Lien entre la RONI publiée (CPC, saisons de 3 mois) et la moyenne des relevés hebdomadaires OISST du Niño 3.4 (même saison)."""
import collections, pathlib, statistics, sys
from datetime import datetime
R = pathlib.Path(__file__).resolve().parent.parent / "releves"
SAIS = "DJF JFM FMA MAM AMJ MJJ JJA JAS ASO SON OND NDJ".split()

def roni():
    out = {}
    for l in (R / "RONI.ascii.txt").read_text().splitlines()[1:]:
        p = l.split()
        if len(p) == 3:
            out[(int(p[1]), SAIS.index(p[0]))] = float(p[2])   # saison centrée sur le mois index+1 (DJF -> janvier)
    return out

def hebdo():
    m = collections.defaultdict(list)
    for l in (R / "wksst9120.for").read_text().splitlines():
        p = l.split()
        if len(p) == 9 and p[0][-4:].isdigit():
            d = datetime.strptime(p[0].title(), "%d%b%Y")
            m[(d.year, d.month)].append(float(p[6]))
    return {k: statistics.mean(v) for k, v in m.items()}

def saison_oisst(H, y, c):
    """Moyenne des mois c-1, c, c+1 (c = mois central 1..12, année y du mois central)."""
    ks = []
    for dm in (-1, 0, 1):
        mm, yy = c + dm, y
        if mm == 0: mm, yy = 12, y - 1
        if mm == 13: mm, yy = 1, y + 1
        ks.append((yy, mm))
    return statistics.mean(H[k] for k in ks) if all(k in H for k in ks) else None

if __name__ == "__main__":
    Ro, H = roni(), hebdo()
    pts = []
    for (y, i), v in sorted(Ro.items()):
        c = i + 1
        o = saison_oisst(H, y, c)
        if o is not None:
            pts.append((y, c, v, o))
    for debut in (1991, 2010, 2016, 2020):
        xs = [(o, v) for y, c, v, o in pts if y >= debut]
        mx, my = statistics.mean(x for x, _ in xs), statistics.mean(y for _, y in xs)
        b = sum((x - mx) * (y - my) for x, y in xs) / sum((x - mx) ** 2 for x, _ in xs)
        a = my - b * mx
        res = [y - (a + b * x) for x, y in xs]
        print(f"depuis {debut}: RONI = {a:+.3f} + {b:.3f} × OISST, résidu σ {statistics.pstdev(res):.3f} (n={len(xs)})")
    for y, c, v, o in pts[-10:]:
        print(y, c, "RONI", v, "OISST", round(o, 3), "écart", round(v - o, 2))
    print({k: round(v, 2) for k, v in H.items() if k[0] == 2026})
