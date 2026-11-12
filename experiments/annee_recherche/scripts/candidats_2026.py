"""Mesures de presse (GDELT) des candidats 2026 contre les prix des marchés « Year in Search 2026 »."""
import json, sys
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).parent))
from analyse import mesures

R = Path(__file__).resolve().parents[1] / "releves"
EVENTS = {715392: "monde n° 1", 779081: "US n° 1", 996200: "monde top 5", 996201: "US top 5"}
presse = json.loads((R / "presse_gdelt.json").read_text())
prix = {}
for eid, lab in EVENTS.items():
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers={"User-Agent": "curl/8"}, timeout=30).json()
    for m in e["markets"]:
        if float(m.get("volume") or 0) > 0 and not m.get("closed"):
            prix.setdefault(m["groupItemTitle"], {})[lab] = float(json.loads(m["outcomePrices"])[0])
noms = [n for n in prix if n in presse]
ms = {n: mesures(presse[n], 2026) for n in noms}
print(f"{'nom':22s} {'A 2026':>8s} {'D':>8s} {'R':>6s} {'pic7':>6s}  prix")
for n in sorted(noms, key=lambda n: -ms[n]["D"]):
    m = ms[n]
    print(f"{n:22s} {m['A']:8d} {m['D']:8d} {m['R']:6.1f} {m['P']:6d}  {prix[n]}")
print("absents du relevé :", [n for n in prix if n not in presse][:30])
