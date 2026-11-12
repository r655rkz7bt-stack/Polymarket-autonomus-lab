"""Décomposition trimestrielle (30/09 -> 31/12) : dette du public (publicDebt) et intragouvernementale.

Comparer la hausse de publicDebt au trimestre à l'estimation d'emprunt du Trésor (communiqué de début
novembre) et la hausse de la dette intragouvernementale (crédits d'intérêts du 31/12 aux fonds fiduciaires).
"""
import bisect, datetime as dt, json
from pathlib import Path
e = json.load(open(Path(__file__).parent / "donnees" / "dette.json"))["entries"]
rows = sorted((dt.datetime.strptime(x["effectiveDate"].split(" E")[0], "%B %d, %Y").date(),
               x["totalDebt"] / 1e9, x["publicDebt"] / 1e9, x["governmentHoldings"] / 1e9) for x in e)
ds = [r[0] for r in rows]
def at(d):
    return rows[bisect.bisect_right(ds, d) - 1]
for y in range(2015, 2027):
    a, b, n9 = at(dt.date(y, 9, 30)), at(dt.date(y, 12, 31)), at(dt.date(y, 11, 9))
    mx = max(r[1] for r in rows if dt.date(y, 9, 30) < r[0] <= dt.date(y, 12, 31))
    print(y, a[0], b[0], f"public {b[2]-a[2]:+.0f}", f"(au 09/11 {n9[2]-a[2]:+.0f})", f"intragouv {b[3]-a[3]:+.0f}",
          f"(au 09/11 {n9[3]-a[3]:+.0f})", f"total 31/12 - max = {b[1]-mx:+.0f}", f"intragouv 30/12->31/12 {b[3]-at(b[0]-dt.timedelta(days=1))[3]:+.0f}")
