"""27/10/2026 : balayage des cases (sport × tranche de prix × délai) des favoris avant le match (paris_favoris.json) : une case n'est retenue que si elle est positive ET
significative (t par événement ≥ 1,5, au moins 25 paris) dans CHACUNE des deux fenêtres (février-août, août-octobre). Contre-épreuve du bruit : le même balayage avec le signe
des gains mélangé au hasard (500 tirages) dit combien de cases « doubles » le hasard produit."""
import json, random, math, collections, statistics as st
D = "experiments/totaux_sports/donnees"
rows = json.load(open(f"{D}/paris_favoris.json"))
COUPE = 1786752000    # 15/08/2026 00:00 UTC
BANDES = [(0.55, 0.70), (0.70, 0.80), (0.80, 0.90), (0.90, 0.97)]
def t_event(bets):
    ev = collections.defaultdict(list)
    for b in bets: ev[b["evenement"]].append(b["gain"])
    xs = [sum(v) / len(v) for v in ev.values()]
    if len(xs) < 5: return 0.0
    sd = st.pstdev(xs) * math.sqrt(len(xs) / (len(xs) - 1))
    return st.mean(xs) / (sd / math.sqrt(len(xs))) if sd > 0 else 0.0
def cases(rows):
    out = {}
    for sport in sorted({r["sport"] for r in rows}):
        for d in (1, 3, 6, 12):
            for lo, hi in BANDES:
                a = [r for r in rows if r["sport"] == sport and r["d"] == d and lo <= r["cout"] < hi and r["start"] < COUPE]
                b = [r for r in rows if r["sport"] == sport and r["d"] == d and lo <= r["cout"] < hi and r["start"] >= COUPE]
                out[(sport, d, lo, hi)] = (a, b)
    return out
def doubles(c):
    res = []
    for k, (a, b) in c.items():
        if len(a) >= 25 and len(b) >= 25 and t_event(a) >= 1.5 and t_event(b) >= 1.5 and st.mean(x["gain"] for x in a) > 0 and st.mean(x["gain"] for x in b) > 0:
            res.append((k, len(a), len(b), st.mean(x["gain"] for x in a), st.mean(x["gain"] for x in b)))
    return res
c = cases(rows)
vrai = doubles(c)
print(len(c), "cases ;", sum(1 for a, b in c.values() if len(a) >= 25 and len(b) >= 25), "avec au moins 25 paris dans chaque fenêtre")
print("cases positives et significatives dans les deux fenêtres :", len(vrai))
for k, na, nb, ma, mb in vrai: print("  ", k, f"février-août {na} paris {ma*100:+.1f} %  août-octobre {nb} paris {mb*100:+.1f} %")
random.seed(27)
comptes = []
for _ in range(100):
    for r in rows:
        r["gain"] = r["gain"]            # mélange : on permute les gains entre paris d'une même case de prix (même sport, même délai)
    perm = list(rows)
    by = collections.defaultdict(list)
    for r in perm: by[(r["sport"], r["d"], 0 if r["cout"] < 0.7 else 1 if r["cout"] < 0.8 else 2 if r["cout"] < 0.9 else 3)].append(r)
    for lst in by.values():
        g = [x["gain"] for x in lst]; random.shuffle(g)
        for x, y in zip(lst, g): x["gain_m"] = y
    fake = [dict(r, gain=r["gain_m"]) for r in perm]
    comptes.append(len(doubles(cases(fake))))
print("cases « doubles » produites par le hasard (gains mélangés dans chaque case, 100 tirages) : moyenne", st.mean(comptes), "maximum", max(comptes))
