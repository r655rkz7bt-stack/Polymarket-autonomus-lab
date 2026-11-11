"""11/11/2026 : achats du NON (vrais échanges) quand le prix payé est sous la fréquence de base − seuil, AVANT le premier séisme
qualifiant du pays dans le mois (catalogue USGS d'aujourd'hui). Usage : .venv/bin/python experiments/seismes_pays/analyse.py"""
import json, math, datetime as dt, collections, requests
rows = json.load(open("experiments/seismes_pays/echanges.json"))
rel = json.load(open("experiments/seismes_pays/releve.json"))
KEYS = {"Indonesia": ["Indonesia"], "Japan": ["Japan"], "Chile": ["Chile"], "Mexico": ["Mexico"], "Philippines": ["Philippines"],
        "Peru": ["Peru"], "United States": ["Alaska", "California", ", CA", "Hawaii", "Oregon", "Washington", "Nevada", "Idaho", "Montana",
                                          "Utah", "Wyoming", "Puerto Rico"]}
START = {"944677": dt.datetime(2026, 9, 1, 4, tzinfo=dt.timezone.utc), "1108757": dt.datetime(2026, 10, 1, 4, tzinfo=dt.timezone.utc)}
DAYS = {"944677": 30, "1108757": 31}
cat = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query", params={"format": "geojson", "minmagnitude": 5.95,
                   "starttime": "2026-09-01", "endtime": "2026-11-02"}, timeout=60).json()
q = [(f["properties"]["time"] / 1000, f["properties"]["place"] or "", f["properties"]["mag"]) for f in cat["features"]
     if round(f["properties"]["mag"] + 1e-9, 1) >= 6.0]
def first_quake(evt, pays):
    a = START[evt].timestamp(); b = a + DAYS[evt] * 86400 + 3600
    ts = [t for t, p, m in q if a <= t < b and any(k in p for k in KEYS[pays])]
    return min(ts) if ts else None
def base_no(evt, pays, d):
    j0, b0 = min((r["jour"], r["base"]) for r in rel if r["evt"] == evt and r["pays"] == pays)
    rate = -math.log(1 - b0) / (DAYS[evt] - j0)
    return math.exp(-rate * max(DAYS[evt] - d, 0))
for evt in START:
    for pays in KEYS:
        fq = first_quake(evt, pays)
        print(evt, pays, "premier séisme qualifiant :", dt.datetime.fromtimestamp(fq, dt.timezone.utc).strftime("%d/%m %H:%M") if fq else "aucun")
ok = [r for r in rows if (first_quake(r["evt"], r["pays"]) is None or START[r["evt"]].timestamp() + r["jour"] * 86400 < first_quake(r["evt"], r["pays"]))]
print(len(rows), "échanges d'achat du NON ;", len(ok), "avant le séisme qualifiant")
for seuil in (0.0, 0.05, 0.10):
    sel = [r for r in ok if r["no_px"] < base_no(r["evt"], r["pays"], r["jour"]) - seuil]
    first = {}
    for r in sorted(sel, key=lambda r: r["jour"]):
        first.setdefault((r["evt"], r["pays"]), r)
    cost = sum(r["no_px"] * r["parts"] for r in sel); pay = sum(r["issue_no"] * r["parts"] for r in sel)
    fc = sum(r["no_px"] for r in first.values()); fp = sum(r["issue_no"] for r in first.values())
    attendu = sum(base_no(r["evt"], r["pays"], r["jour"]) for r in first.values())
    print(f"seuil {seuil:.2f} : {len(sel)} échanges ({sum(r['parts'] for r in sel):.0f} parts), rendement {pay / cost - 1 if cost else 0:+.1%} ; "
          f"premier achat par marché : {len(first)} marchés, NON gagnés {fp:.0f} pour {attendu:.2f} attendus (base) et {fc:.2f} payés, "
          f"rendement {fp / fc - 1 if fc else 0:+.1%}")
    for k, v in first.items():
        print("    ", k, f"jour {v['jour']:.1f} payé {v['no_px']:.3f} base {base_no(v['evt'], v['pays'], v['jour']):.3f} parts {v['parts']:.0f} issue {v['issue_no']}")
