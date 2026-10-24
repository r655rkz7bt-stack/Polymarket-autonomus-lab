"""Week-ends suivants (2e, 3e, 4e… « Nth Weekend Box Office ») : même test de la favorite, sans lier le film à son ouverture."""
import sys, re
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
import analyse, favori
from favori import *
def cases_suivants():
    out = []
    for e in analyse.EV:
        if not e["closed"] or not e.get("end") or not re.search(r"\d(st|nd|rd|th) Weekend|Second .*Weekend", e["title"]): continue
        w = analyse.winner(e)
        if not w or len(e["markets"]) < 3: continue
        tr = analyse.load(e["id"])
        if len(tr) < 20: continue
        ms = []
        for m in e["markets"]:
            if len(m["tokens"]) != 2: break
            ms.append(dict(m, series=analyse.yes_series(tr, m["tokens"][0], m["tokens"][1]), win=int(m is w)))
        else:
            out.append(dict(e=e, trades=tr, end=analyse.ts(e["end"]), ms=ms))
    return out
favori.C[:] = cases_suivants()
print(len(favori.C), "événements des week-ends suivants")
for h in (48, 36, 24, 12):
    for lo, hi in ((0.5, 1.0), (0.5, 0.8), (0.8, 1.0)):
        b = favori.run(h, lo, hi)
        if len(b) < 10: continue
        v = verdict(b)
        print(f"h={h} {lo}-{hi}: n={v['paris']} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} gagnés/attendus {sum(1 for x in b if x['gain']>0)}/{sum(x['cout'] for x in b):.1f} z_prix {v['z_prix']:+.2f}")
