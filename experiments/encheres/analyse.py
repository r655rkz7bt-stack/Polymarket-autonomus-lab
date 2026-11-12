"""Gros lots des ventes du soir de Christie's à New York (2020-2026) : prix réalisé (frais d'acheteur compris) / estimation basse.

Rejoue les tranches des marchés Polymarket « <artiste> Sale Price » : un lot retiré ou invendu tombe dans la tranche la plus basse.
"""
import glob, json, statistics
from pathlib import Path

ICI = Path(__file__).parent


def gros_lots(seuil=10e6, exclure=("24266",)):
    out = []
    for f in sorted(glob.glob(str(ICI / "donnees" / "lots_*.json"))):
        v = json.load(open(f))
        if any(x in f for x in exclure):
            continue
        for l in v["lots"]:
            low, high = float(l.get("estimate_low") or 0), float(l.get("estimate_high") or 0)
            if low < seuil:
                continue
            pr = float(l.get("price_realised") or 0)
            out.append({"vente": v["vente"], "date": v["date"][:10], "artiste": l.get("title_primary_txt", "")[:30],
                        "low": low, "high": high, "prix": pr, "retire": bool(l.get("lot_withdrawn")),
                        "ratio": pr / low if pr else 0.0})
    return out


if __name__ == "__main__":
    L = gros_lots()
    print(len(L), "lots d'estimation basse >= 10 M$")
    for x in sorted(L, key=lambda x: x["date"]):
        etat = "RETIRÉ" if x["retire"] else ("invendu" if not x["prix"] else f"{x['ratio']:.2f}")
        print(x["date"], x["artiste"].ljust(30), f"{x['low']/1e6:6.1f}-{x['high']/1e6:6.1f}", f"{x['prix']/1e6:7.2f}", etat)
    vendus = [x["ratio"] for x in L if x["prix"]]
    print("vendus", len(vendus), "sur", len(L), "; retirés", sum(x["retire"] for x in L), "; invendus", sum((not x["prix"]) and not x["retire"] for x in L))
    q = statistics.quantiles(vendus, n=10)
    print("ratio prix/estimation basse : médiane %.2f ; déciles %s" % (statistics.median(vendus), [round(v, 2) for v in q]))
