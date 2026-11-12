"""Précipitations de novembre à Central Park (NYC) : cumul observé du 1er au jour J (ACIS, sans clé) + reste du mois tiré des
années 1991-2025 (même fenêtre de dates), loi des tranches du marché « Precipitation in NYC in November? ».
Usage : nyc_novembre.py [sid] — sid ACIS (défaut 94728 = Central Park ; Seattle : SEAthr ; voir la règle du marché)."""
import json, sys, datetime as dt
import requests

SID = sys.argv[1] if len(sys.argv) > 1 else "94728"
H = {"User-Agent": "curl/8"}
TODAY = dt.date(2026, 11, 12)


def pcpn(sdate, edate):
    r = requests.post("https://data.rcc-acis.org/StnData", json={"sid": SID, "sdate": sdate, "edate": edate,
                      "elems": [{"name": "pcpn"}]}, headers=H, timeout=60).json()
    out = {}
    for d, v in r.get("data", []):
        out[d] = 0.0 if v in ("T", "0.00") else (float(v) if v not in ("M", "S") and not v.endswith("A") else (float(v[:-1]) if v.endswith("A") else None))
    return r.get("meta", {}), out


meta, obs = pcpn("2026-11-01", (TODAY - dt.timedelta(days=1)).isoformat())
print(meta.get("name"), obs)
vu = sum(v for v in obs.values() if v is not None)
manque = [d for d, v in obs.items() if v is None]
print("cumul observé", round(vu, 2), "jours manquants", manque)
debut = min([int(d[-2:]) for d, v in obs.items() if v is None] + [(TODAY - dt.date(2026, 11, 1)).days + 1])   # premier jour non observé
vu = sum(v for d, v in obs.items() if v is not None and int(d[-2:]) < debut)
restes = []
for an in range(1951, 2026):
    _, h = pcpn(f"{an}-11-{debut:02d}", f"{an}-11-30")
    vals = [v for v in h.values() if v is not None]
    if len(vals) >= len(h) - 1:
        restes.append(sum(vals))
tot = sorted(vu + r for r in restes)
print("années", len(restes), "du", debut, "au 30 ; totaux :", [round(x, 2) for x in tot])
TRANCHES = [("<2", 0, 2), ("2-3", 2, 3), ("3-3.5", 3, 3.5), ("3.5-4.25", 3.5, 4.25), ("4.25-5.75", 4.25, 5.75), (">5.75", 5.75, 99)]
for nom, a, b in TRANCHES:
    print(nom, round(sum(1 for x in tot if a <= x < b) / len(tot), 3))
json.dump({"station": meta.get("name"), "observe": obs, "cumul": vu, "restes": restes}, open(f"/tmp/claude-0/precip_{SID}.json", "w"))
