"""Statut DeepStateMap de chaque lieu des marchés (point de la règle) dans chaque version quotidienne de la carte depuis DEBUT.
Sortie : donnees/statut_dsm.json {lieu: [[horodatage, statut], ...]} avec statut « occupe », « gris » (statut inconnu) ou « libre ».
Carte : deepstatemap.live/api/history/<id>/geojson (0,6 Mo, sans clé). Usage : statut_dsm.py [AAAA-MM-JJ]"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "donnees"
DEBUT = sys.argv[1] if len(sys.argv) > 1 else "2026-05-01"
H = {"User-Agent": "Mozilla/5.0"}


def inside(x, y, ring):
    c, n = False, len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-300) + xi:
            c = not c
        j = i
    return c


def in_poly(x, y, geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for p in polys:
        if p and inside(x, y, p[0]) and not any(inside(x, y, h) for h in p[1:]):
            return True
    return False


def statut(gj, pts):
    out = {}
    feats = []
    for f in gj.get("features", []):
        g = f.get("geometry") or {}
        if g.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        name = (f.get("properties") or {}).get("name", "")
        kind = "occupe" if "Occupied" in name or "Окуповано" in name else ("gris" if "Unknown" in name or "невідомий" in name else None)
        if kind:
            feats.append((kind, g))
    for k, (lon, lat) in pts.items():
        s = "libre"
        for kind, g in feats:
            if in_poly(lon, lat, g):
                s = kind
                if kind == "occupe":
                    break
        out[k] = s
    return out


def main():
    ms = json.loads((D / "marches.json").read_text())
    pts = {}
    for m in ms:
        if m["lat"] is not None:
            pts[f"{m['lat']:.4f},{m['lon']:.4f}"] = (m["lon"], m["lat"])
    vers = [v for v in json.loads((D / "dsm_versions.json").read_text()) if v["createdAt"] >= DEBUT]

    def one(v):
        for essai in range(3):
            try:
                gj = requests.get(f"https://deepstatemap.live/api/history/{v['id']}/geojson", headers=H, timeout=60).json()
                return v["createdAt"], statut(gj, pts)
            except Exception:
                continue
        return v["createdAt"], None

    with ThreadPoolExecutor(6) as ex:
        res = sorted(ex.map(one, vers), key=lambda r: r[0])
    out = {k: [[t, s[k]] for t, s in res if s] for k in pts}
    (D / "statut_dsm.json").write_text(json.dumps(out))
    print(len(vers), "versions", sum(1 for t, s in res if s is None), "échecs", len(pts), "lieux")


if __name__ == "__main__":
    main()
