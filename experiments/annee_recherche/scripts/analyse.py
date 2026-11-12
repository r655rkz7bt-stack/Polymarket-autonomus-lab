"""Le n° 1 « People » de Google Year in Search se lit-il dans le volume de presse (GDELT) connu mi-novembre ?

Pour chaque année Y (2018-2025) et chaque liste (monde, États-Unis) : candidats = les 10 de la liste de Y
(+ les noms de `--leurres`, célébrités toujours cotées par le marché). Mesures, toutes arrêtées au 10/11 de Y
(jour où l'on décide) : A = articles de Y ; D = A − articles de Y−1 (même fenêtre) ; R = (A + 50) / (B + 50) ;
P = pic de 7 jours de Y. On regarde le rang du vrai n° 1 selon chaque mesure.
Attention : l'univers « les 10 de la liste » regarde vers le futur (on sait qu'ils seront dans la liste) ;
le test dit seulement si la mesure ORDONNE bien les candidats plausibles, pas si elle les trouve.
"""
import json, sys
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "releves"
LEURRES = ["Donald Trump", "Taylor Swift", "Elon Musk", "Cristiano Ronaldo", "Lionel Messi", "Vladimir Putin",
           "Kim Kardashian", "Kanye West", "Joe Biden", "Benjamin Netanyahu", "Volodymyr Zelenskyy"]


def fenetre(s, y, jusqua="1110"):
    return sum(v for d, v in s.items() if d[:4] == str(y) and d[4:8] <= jusqua)


def pic7(s, y, jusqua="1110"):
    vals = [v for d, v in sorted(s.items()) if d[:4] == str(y) and d[4:8] <= jusqua]
    return max((sum(vals[i:i + 7]) for i in range(max(1, len(vals) - 6))), default=0)


def mesures(s, y):
    a, b = fenetre(s, y), fenetre(s, y - 1)
    return {"A": a, "D": a - b, "R": (a + 50) / (b + 50), "P": pic7(s, y)}


def main(leurres=False):
    listes = json.loads((R / "listes.json").read_text())
    presse = json.loads((R / "presse_gdelt.json").read_text())
    rangs = {k: [] for k in "ADRP"}
    for y in range(2018, 2026):
        for loc in ("GLOBAL", "US"):
            top = listes[str(y)][loc]["People"]
            cands = [n for n in top + (LEURRES if leurres else []) if n in presse]
            cands = list(dict.fromkeys(cands))
            if top[0] not in presse:
                print(y, loc, "n° 1 absent du relevé", top[0]); continue
            m = {n: mesures(presse[n], y) for n in cands}
            ligne = []
            for k in "ADRP":
                ordre = sorted(cands, key=lambda n: -m[n][k])
                r = ordre.index(top[0]) + 1
                rangs[k].append(r)
                ligne.append(f"{k}:{r} ({ordre[0]})")
            print(y, loc, top[0], f"[{len(cands)} candidats]", " | ".join(ligne))
    for k, v in rangs.items():
        print(k, "rang du n° 1 :", v, "premier", sum(r == 1 for r in v), "/", len(v), "dans les 3", sum(r <= 3 for r in v))


if __name__ == "__main__":
    main("--leurres" in sys.argv)
