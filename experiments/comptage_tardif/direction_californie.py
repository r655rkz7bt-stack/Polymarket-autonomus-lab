"""Piste n° 66 (comptage tardif), 17/11/2026 : direction des bulletins comptés ENTRE deux relevés datés de californie_marges.py
(décompte officiel api.sos.ca.gov). Pour chaque district : voix ajoutées, marge (points) des bulletins ajoutés contre la marge
cumulée, et marge courante contre les bornes de tranches les plus proches, avec le carnet (acheteur / vendeur) de ces tranches."""
import gzip, json, sys
from collections import defaultdict
from pathlib import Path

R = Path(__file__).parent / "releves"
a, b = (sorted(R.glob("californie_*.jsonl.gz"))[-2:] if len(sys.argv) < 3 else [Path(x) for x in sys.argv[1:3]])


def load(p):
    out = defaultdict(list)
    for l in gzip.open(p, "rt"):
        x = json.loads(l)
        out[x["district"]].append(x)
    return out


A, B = load(a), load(b)
print(f"{a.name} -> {b.name}")
lignes = []
for n in sorted(set(A) & set(B)):
    xa, xb = A[n][0], B[n][0]
    if xa["api_heure"] == xb["api_heure"]:
        continue
    ta = {t[2]: t[0] for t in xa["top"]}
    tb = {t[2]: t[0] for t in xb["top"]}
    lead = xb["top"][0][2]
    other = xb["top"][1][2]
    add_tot = xb["total"] - xa["total"]
    add_lead = tb[lead] - ta.get(lead, 0)
    add_other = tb[other] - ta.get(other, 0)
    m_new = 100.0 * (add_lead - add_other) / add_tot if add_tot > 0 else float("nan")
    # bornes de tranches proches de la marge courante
    bornes = sorted({v for x in B[n] if x["tranche"] for v in x["tranche"][1:] if v < 999})
    proche = min(bornes, key=lambda v: abs(v - xb["marge"])) if bornes else None
    lignes.append((n, xa["total"], add_tot, xa["marge"], xb["marge"], m_new, proche))
    print(f"CA-{n:2d} {xb['parti_tete']} total {xa['total']:7d} +{add_tot:6d} ({100*add_tot/max(1,xa['total']):4.1f} %) "
          f"marge {xa['marge']:6.2f} -> {xb['marge']:6.2f} ; bulletins ajoutés {m_new:6.2f} ; borne proche {proche}")
