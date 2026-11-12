"""Dette fédérale (TreasuryDirect, totalDebt) : chance d'atteindre un seuil d'ici le 31/12.

Pour chaque année passée : gain maximal du 09/11 au 31/12 divisé par le rythme connu au 09/11
(pente des N jours précédents × 52 jours). Données : donnees/dette.json
(www.treasurydirect.gov/NP_WS/debt/search?startdate=2015-01-01&enddate=...&format=json, sans clé).
"""
import bisect
import datetime as dt
import json
import math
import sys
from pathlib import Path

ICI = Path(__file__).parent
e = json.load(open(ICI / "donnees" / "dette.json"))["entries"]
rows = sorted((dt.datetime.strptime(x["effectiveDate"].split(" E")[0], "%B %d, %Y").date(),
               x["totalDebt"] / 1e12, x["governmentHoldings"] / 1e12) for x in e)
ds = [r[0] for r in rows]


def val(d, k=1):
    i = bisect.bisect_right(ds, d) - 1
    return rows[i][k]


def ratios(jour=(11, 9), fin=(12, 31), recul=120):
    out = []
    for y in range(2015, 2026):
        d0 = dt.date(y, *jour)
        d1 = dt.date(y, *fin)
        n = (d1 - d0).days
        a = val(d0)
        pente = (a - val(d0 - dt.timedelta(days=recul))) / recul
        mx = max(v for d, v, _ in rows if d0 < d <= d1)
        out.append((y, a, pente * n, mx - a, (mx - a) / (pente * n) if pente > 0 else float("nan")))
    return out


if __name__ == "__main__":
    for recul in (60, 120, 365):
        print(f"--- pente sur {recul} jours")
        for y, a, attendu, gain, r in ratios(recul=recul):
            print(y, f"{a:.3f}", f"attendu {attendu*1000:.0f} Md", f"gain max {gain*1000:.0f} Md", f"ratio {r:.2f}")
    # dette et pente aujourd'hui
    d0 = rows[-1][0]
    for recul in (60, 120, 365):
        p = (rows[-1][1] - val(d0 - dt.timedelta(days=recul))) / recul
        n = (dt.date(2026, 12, 31) - d0).days
        print(f"aujourd'hui {d0} {rows[-1][1]:.4f} ; pente {recul} j {p*1000:.2f} Md/j ; attendu sur {n} j : {p*n*1000:.0f} Md")
