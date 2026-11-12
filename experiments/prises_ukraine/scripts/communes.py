"""Limites des communes (couche « Ukrainian Settlements » de la carte ISW, celle des règles) pour chaque lieu des marchés.
Sortie : donnees/communes.json {"lat,lon": {"nom": ADM4_EN, "anneaux": [[[lon, lat], ...], ...]}}"""
import json, time
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "donnees"
U = "https://services5.arcgis.com/SaBe5HMtmnbqSWlu/arcgis/rest/services/Ukrainian_Settlements_Updated_view/FeatureServer/0/query"

ms = json.loads((D / "marches.json").read_text())
out = {}
for m in ms:
    if m["lat"] is None:
        continue
    k = f"{m['lat']:.4f},{m['lon']:.4f}"
    if k in out:
        continue
    r = requests.get(U, timeout=60, params={"where": "1=1", "geometry": f"{m['lon']},{m['lat']}", "geometryType": "esriGeometryPoint",
                                           "inSR": 4326, "outSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": "ADM4_EN",
                                           "returnGeometry": "true", "f": "json"}).json()
    fs = r.get("features") or []
    if fs:
        out[k] = {"nom": fs[0]["attributes"]["ADM4_EN"], "anneaux": fs[0]["geometry"]["rings"]}
    time.sleep(0.3)
(D / "communes.json").write_text(json.dumps(out))
print(len(out), "communes", sorted(v["nom"] for v in out.values()))
