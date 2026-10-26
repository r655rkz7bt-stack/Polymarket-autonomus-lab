"""26/10/2026 : même mécanisme que correlation_manches.py, sur le handicap −1,5 d'un BO3 (la meilleure équipe gagne 2-0). Si les cartes sont corrélées,
le favori à −1,5 gagne plus souvent que q² (binomial) ; le marché le paie-t-il ? Achat de l'issue « −1,5 » quand cette équipe est la favorite, à T − 3 h
(premier échange preneur dans les 6 h suivantes, avant le match). Usage : python experiments/bo3_coherence/correlation_handicap.py"""
import gzip, json, math, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["INCLURE_50_50"] = "1"
import series  # noqa: E402
from echanges import cout_preneur  # noqa: E402
D = HERE / "donnees"
choisis = set(json.loads((D / "echantillon_esport.json").read_text()))
out = []
for nom in ("cs2", "lol", "dota2", "val"):
    for ev in json.loads(gzip.decompress((D / f"evenements_{nom}.json.gz").read_bytes())):
        if str(ev["id"]) not in choisis: continue
        ev["serie"] = nom
        c = series.match_cas(ev, "esport")
        p = D / "echanges" / f"{ev['id']}.json.gz"
        if not c or c["bo"] != 3 or not p.exists(): continue
        rows = json.loads(gzip.decompress(p.read_bytes()))
        t0 = c["start"] - 3 * 3600
        m = series.prix_vainqueur(rows, c, t0)
        if m is None or not 0.5 < max(m, 1 - m) < 0.995: continue
        for li in c["lies"]:
            if li["kind"] != "handicap" or li["won"] == -1: continue
            a_is_issue0 = li["f"](0.9) > li["f"](0.1)  # f(q) croît avec q_A si l'issue 0 est l'équipe A
            fav_is_issue0 = (m > 0.5) == a_is_issue0
            if not fav_is_issue0: continue
            q = series.q_depuis_match(max(m, 1 - m), 3)
            got = cout_preneur(rows, li["toks"][0], li["toks"][1], t0, 6 * 3600, apres=True, fin_max=c["start"])
            if not got or not 0.01 <= got[1] <= 0.99: continue
            paid = got[1] + series.it.fee(got[1], li["rate"])
            out.append({"fav": max(m, 1 - m), "binom": q * q, "marche": got[1], "reel": float(li["won"] == 0), "rend": float(li["won"] == 0) / paid - 1,
                        "serie": nom, "event": c["event"]})
def ligne(nom, v):
    if len(v) < 20: return
    n = len(v); r = sum(x["reel"] for x in v) / n; b = sum(x["binom"] for x in v) / n; mk = sum(x["marche"] for x in v) / n
    sd = math.sqrt(sum(x["marche"] * (1 - x["marche"]) for x in v)) / n
    print(f"{nom:20s} n={n:4d} réel {r:.3f} binomial {b:.3f} marché {mk:.3f} réel−binomial {r-b:+.3f} réel−marché {r-mk:+.3f} (z {(r-mk)/sd:+.2f}) rendement {sum(x['rend'] for x in v)/n*100:+.1f} %")
print(len(out), "handicaps −1,5 du favori (BO3)")
ligne("TOUS", out)
for lo, hi in [(0.5, 0.65), (0.65, 0.8), (0.8, 1.0)]: ligne(f"favori {lo:.2f}-{hi:.2f}", [x for x in out if lo <= x["fav"] < hi])
for s in ("cs2", "lol", "dota2", "val"): ligne(s, [x for x in out if x["serie"] == s])
