"""26/10/2026 : pourquoi l'« Under 2,5 » des BO3 d'e-sport gagne-t-il ? Les cartes d'un match sont-elles CORRÉLÉES (un balayage 2-0 plus fréquent
que ne le dit la loi binomiale à partir du prix du vainqueur) et le marché de totaux le sait-il ?
Pour chaque BO3 avec un total « 2,5 » : prix du vainqueur à T0 = coup d'envoi − 3 h (5 derniers échanges de l'heure avant), q binomial tel que
q²(3 − 2q) = prix, chance binomiale du balayage = 1 − 2q(1 − q) ; prix payé de l'Under (premier échange preneur dans les 6 h après T0, avant le match) ;
résultat réel. Par tranche de force du favori : réel contre binomial contre prix du marché. Usage : python experiments/bo3_coherence/correlation_manches.py"""
import gzip, json, math, os, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["INCLURE_50_50"] = "1"
import series  # noqa: E402
from echanges import cout_preneur  # noqa: E402

D = HERE / "donnees"
BO = int(os.environ.get("BO", "3"))  # BO=5 : Under 3,5 (balayage 3-0 en cinq manches)
choisis = set(json.loads((D / "echantillon_esport.json").read_text()))
rows_out = []
for nom in ("cs2", "lol", "dota2", "val"):
    for ev in json.loads(gzip.decompress((D / f"evenements_{nom}.json.gz").read_bytes())):
        if str(ev["id"]) not in choisis:
            continue
        ev["serie"] = nom
        c = series.match_cas(ev, "esport")
        p = D / "echanges" / f"{ev['id']}.json.gz"
        if not c or c["bo"] != BO or not p.exists():
            continue
        rows = json.loads(gzip.decompress(p.read_bytes()))
        t0 = c["start"] - 3 * 3600
        m = series.prix_vainqueur(rows, c, t0)
        if m is None or not 0.5 <= max(m, 1 - m) < 0.995:
            continue
        for li in c["lies"]:
            if li["kind"] != "total" or li["won"] == -1:
                continue
            if BO == 5 and round(min(li["f"](0.5), 1 - li["f"](0.5)), 3) != 0.25:
                continue  # BO5 : seule la ligne 3,5 (la 4,5 a une autre loi)
            over_idx = 0 if li["f"](0.9) < 0.5 else 1  # f(0.9) = chance de l'issue 0 : 0,18 si Over, 0,82 si Under
            u = 1 - over_idx
            got = cout_preneur(rows, li["toks"][u], li["toks"][over_idx], t0, 6 * 3600, apres=True, fin_max=c["start"])
            if not got or not 0.01 <= got[1] <= 0.99:
                continue
            q = series.q_depuis_match(max(m, 1 - m), BO)
            rows_out.append({"fav": max(m, 1 - m), "binom": (1 - 2 * q * (1 - q)) if BO == 3 else (q ** 3 + (1 - q) ** 3), "marche": got[1], "reel": float(li["won"] == u), "serie": nom,
                             "event": c["event"], "mois": series.jour(c["start"])[:7]})
print(len(rows_out), f"matchs BO{BO} avec total {2.5 if BO == 3 else 3.5}, prix du vainqueur et prix de l'Under")

def ligne(nom, v):
    if len(v) < 20: return
    n = len(v); r = sum(x["reel"] for x in v) / n; b = sum(x["binom"] for x in v) / n; mk = sum(x["marche"] for x in v) / n
    sd = math.sqrt(sum(x["marche"] * (1 - x["marche"]) for x in v)) / n
    print(f"{nom:24s} n={n:4d}  réel {r:.3f}  binomial {b:.3f}  marché {mk:.3f}  réel−binomial {r-b:+.3f}  réel−marché {r-mk:+.3f} (z {(r-mk)/sd:+.2f})")

ligne("TOUS", rows_out)
for lo, hi in [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]:
    ligne(f"favori {lo:.1f}-{hi:.1f}", [x for x in rows_out if lo <= x["fav"] < hi])
for s in ("cs2", "lol", "dota2", "val"):
    ligne(f"série {s}", [x for x in rows_out if x["serie"] == s])
for lo, hi in [("2026-01", "2026-06"), ("2026-06", "2026-11")]:
    ligne(f"mois {lo}..{hi}", [x for x in rows_out if lo <= x["mois"] < hi])
print("-- par prix payé de l'Under (la stratégie mère n'achète qu'entre 0,30 et 0,70)")
for lo, hi in [(0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]:
    ligne(f"Under {lo:.1f}-{hi:.1f}", [x for x in rows_out if lo <= x["marche"] < hi])
