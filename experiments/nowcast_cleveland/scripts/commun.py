"""Lecture des prévisions de la Fed de Cleveland (nowcast_month/year.json) et des événements d'inflation de Gamma."""
import json, math, pathlib, re
from datetime import date, datetime, timezone

D = pathlib.Path(__file__).resolve().parent.parent / "donnees"
SERIES = {"CPI Inflation": "cpi", "Core CPI Inflation": "core_cpi", "PCE Inflation": "pce", "Core PCE Inflation": "core_pce"}
MOIS = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}


def _ym_label(target: tuple[int, int], label: str) -> date:
    y, m = target
    mm, dd = (int(x) for x in label.split("/"))
    yy = y + 1 if mm < m else y
    return date(yy, mm, dd)


def nowcasts(freq: str = "month"):
    """{(serie, (a, m)): {"nc": [(jour, valeur)], "actual": (jour, valeur) | None}}."""
    out = {}
    for c in json.loads((D / f"nowcast_{freq}.json").read_text()):
        y, m = (int(x) for x in c["chart"]["subcaption"].split("-"))
        for s in c["dataset"]:
            name = s["seriesname"]
            actual = name.startswith("Actual ")
            key = SERIES[name.replace("Actual ", "").replace("Core CPI Inflation", "Core CPI Inflation")]
            rec = out.setdefault((key, (y, m)), {"nc": [], "actual": None})
            for x in s["data"]:
                if not x.get("value"):
                    continue
                d = _ym_label((y, m), x["tooltext"].split("{br}")[1])
                if actual:
                    rec["actual"] = (d, float(x["value"]))
                else:
                    rec["nc"].append((d, float(x["value"])))
    for rec in out.values():
        rec["nc"].sort()
    return out


def nc_before(rec, day: date):
    """Dernière prévision publiée strictement avant `day` (prudent : la valeur du jour sort vers 10 h ET)."""
    v = [x for x in rec["nc"] if x[0] < day]
    return v[-1] if v else None


def classify(title: str):
    """(serie, freq, mois cible) ou None."""
    t = title.strip()
    if re.search(r"Japan|China|UK|U\.K\.|Argentin|Canada|Euro|Brazil|Mexico|Korea|Africa|Turkey|BLS|from", t):
        return None
    m = re.match(r"Core (CPI|PCE)(?: \(ex food and energy\))? (MoM|YoY) - (\w+) (\d{4})$", t)
    if m:
        return ("core_" + m.group(1).lower(), "month" if m.group(2) == "MoM" else "year", (int(m.group(4)), MOIS[m.group(3)]))
    m = re.match(r"(\w+) Inflation(?: US)? - (Monthly|Annual)", t)
    if m and m.group(1) in MOIS:
        return ("cpi", "month" if m.group(2) == "Monthly" else "year", (None, MOIS[m.group(1)]))
    return None


def bounds(label: str):
    s = label.replace("%", "").replace(" ", "").replace("−", "-")
    m = re.match(r"^(≤|<=|<)(-?\d+\.\d)$", s)
    if m:
        return (-math.inf, float(m.group(2)) + 0.05)
    m = re.match(r"^(≥|>=|>)(-?\d+\.\d)$", s) or re.match(r"^(-?\d+\.\d)\+$", s)
    if m:
        v = float(m.group(m.lastindex))
        return (v - 0.05, math.inf)
    m = re.match(r"^(-?\d+\.\d)$", s)
    if m:
        v = float(m.group(1))
        return (v - 0.05, v + 0.05)
    return None


def ts(s: str) -> datetime:
    s = s.replace(" ", "T").replace("Z", "+00:00")
    if s.endswith("+00"):
        s += ":00"
    return datetime.fromisoformat(s)
