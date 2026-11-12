"""PIB mensuel canadien : estimation anticipée (publiée un mois avant, communiqué du mois précédent) contre les tranches du
chiffre officiel. Loi des révisions = fréquences empiriques de (officiel − anticipé), en dixièmes, sur les communiqués relevés
(hors mois testé : pas de regard vers le futur sur sa propre issue). Test aux vrais échanges comme michigan/scripts/test.py.
Usage : test.py [SEUIL] [MIN_PARTS]"""
import collections, gzip, json, re, sys
from datetime import datetime
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "releves"
SEUIL = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 10
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
com = json.loads((R / "communiques.json").read_text())


def anticipe_de(mois_cle):
    """Estimation anticipée du mois AAAA-MM et date de sa publication (communiqué du mois d'avant)."""
    y, m = int(mois_cle[:4]), int(mois_cle[5:])
    py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
    c = com.get(f"{py}-{pm:02d}")
    if not c or c.get("anticipe_mois") != MOIS[m - 1]:
        return None, None
    return c["anticipe"], datetime.strptime(c["date"], "%y%m%d")


def revisions(sauf):
    out = collections.Counter()
    for k, c in com.items():
        if k == sauf:
            continue
        a, _ = anticipe_de(k)
        if a is not None:
            out[round((c["officiel"] - a) * 10)] += 1
    return out


def bornes(t):
    t = t.replace("%", "").replace("–", " to ").strip()
    t = re.sub(r"^(-?\d+\.\d)-(-?\d+\.\d)$", r"\1 to \2", t)
    if t.startswith("<"):
        return (-99, round(float(t[1:]) - 0.1, 1))
    if t.endswith("+"):
        return (float(t[:-1]), 99)
    a, b = t.split(" to ")
    return (float(a), float(b))


def p_tranche(a, lo, hi, rev):
    n = sum(rev.values())
    return sum(c for k, c in rev.items() if lo - 1e-9 <= round(a + k / 10, 1) <= hi + 1e-9) / n


def frais(p):
    return 0.05 * p * (1 - p)


if __name__ == "__main__":
    ms = json.load(gzip.open(R / "marches.json.gz"))
    ex = json.load(gzip.open(R / "echanges.json.gz"))
    paris = []
    for m in ms:
        mo = m["titre"].split(": ")[1].split(" (")[0]          # « September 2026 »
        cle = f"{mo.split()[1]}-{MOIS.index(mo.split()[0]) + 1:02d}"
        a, d = anticipe_de(cle)
        if a is None or not m["clos"]:
            continue
        T = d.timestamp() + 16 * 3600                              # communiqué à 8 h 30, heure de l'Est ; décision dès 16 h UTC
        rev = revisions(cle)
        lo, hi = bornes(m["tranche"])
        py = p_tranche(a, lo, hi, rev)
        issue = 1 if json.loads(m["prix"])[0] in ("1", 1) else 0
        for side, tok, est, gagne in ((0, m["tokens"][0], py, issue), (1, m["tokens"][1], 1 - py, 1 - issue)):
            tr = sorted((r for r in ex.get(m["event"], []) if r["asset"] == tok and float(r["timestamp"]) >= T and float(r["size"]) >= MIN),
                        key=lambda r: float(r["timestamp"]))
            for r in tr:
                p = float(r["price"])
                if 0.02 <= p <= 0.98 and est - p - frais(p) >= SEUIL:
                    paris.append((cle, m["tranche"], "OUI" if side == 0 else "NON", p, est, gagne))
                    break
    vus, uns = set(), []
    for x in paris:
        if (x[0], x[1]) not in vus:
            vus.add((x[0], x[1])); uns.append(x)
    for nom, L in (("tous", paris), ("un par tranche", uns)):
        c = sum(x[3] for x in L); g = sum(x[5] for x in L)
        print(f"{nom} : {len(L)} paris, {g} gagnés pour {c:.2f} attendus (prix), {sum(x[4] for x in L):.2f} (modèle), "
              f"{sum(x[5] - x[3] - frais(x[3]) for x in L) / c * 100 if c else 0:+.1f} % par mise")
    for x in uns:
        print("  ", x[0], f"{x[1]:16s}", x[2], f"prix {x[3]:.3f} chance {x[4]:.3f} issue {x[5]}")
