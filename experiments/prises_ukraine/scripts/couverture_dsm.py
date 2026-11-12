"""Pour chaque version quotidienne de DeepStateMap depuis DEBUT et chaque commune des marchés : part de la commune (grille de
points intérieurs) sous une zone « occupée », et sous « occupée ou grise » ; « touche » = au moins un point de grille OU un sommet
d'une zone dans la commune. Cartes mises en cache dans donnees/dsm/<id>.json (0,6 Mo). Sortie : donnees/couverture_dsm.json
{"lat,lon": [[createdAt, part_occ, part_occ_gris, touche_occ, touche_gris], ...]}"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from statut_dsm import inside

D = Path(__file__).resolve().parents[1] / "donnees"
C = D / "dsm"
C.mkdir(exist_ok=True)
DEBUT = sys.argv[1] if len(sys.argv) > 1 else "2026-05-01"
H = {"User-Agent": "Mozilla/5.0"}


def carte(v):
    f = C / f"{v['id']}.json"
    if f.exists():
        return json.loads(f.read_text())
    for _ in range(3):
        try:
            t = requests.get(f"https://deepstatemap.live/api/history/{v['id']}/geojson", headers=H, timeout=60).text
            json.loads(t)
            f.write_text(t)
            return json.loads(t)
        except Exception:
            continue
    return None


def polys(gj):
    out = []
    for f in gj.get("features", []):
        g = f.get("geometry") or {}
        if g.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        n = (f.get("properties") or {}).get("name", "")
        kind = "occ" if ("Occupied" in n or "Окуповано" in n or "ОРДЛО" in n or "Crimea" in n) else ("gris" if ("Unknown" in n or "невідомий" in n) else None)
        if not kind:
            continue
        for p in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            if p:
                xs = [q[0] for q in p[0]]; ys = [q[1] for q in p[0]]
                out.append((kind, p, (min(xs), min(ys), max(xs), max(ys))))
    return out


def in_rings(x, y, rings):
    return inside(x, y, rings[0]) and not any(inside(x, y, h) for h in rings[1:])


def grille(rings, n=24):
    xs = [q[0] for q in rings[0]]; ys = [q[1] for q in rings[0]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pts = [(x0 + (x1 - x0) * (i + .5) / n, y0 + (y1 - y0) * (j + .5) / n) for i in range(n) for j in range(n)]
    return [p for p in pts if in_rings(p[0], p[1], rings)], (x0, y0, x1, y1)


def mesure(ps, com):
    res = {}
    for k, (rings, pts, bb) in com.items():
        near = [(kd, p) for kd, p, b in ps if not (b[2] < bb[0] or b[0] > bb[2] or b[3] < bb[1] or b[1] > bb[3])]
        occ = grey = 0
        for x, y in pts:
            s = None
            for kd, p in near:
                if in_rings(x, y, p):
                    s = kd
                    if kd == "occ":
                        break
            occ += s == "occ"; grey += s is not None
        t_occ = occ > 0 or any(in_rings(q[0], q[1], rings) for kd, p in near if kd == "occ" for q in p[0][::3])
        t_gr = grey > 0 or t_occ or any(in_rings(q[0], q[1], rings) for kd, p in near for q in p[0][::3])
        n = max(len(pts), 1)
        res[k] = [round(occ / n, 3), round(grey / n, 3), t_occ, t_gr]
    return res


def main():
    cm = json.loads((D / "communes.json").read_text())
    com = {}
    for k, v in cm.items():
        rings = v["anneaux"]
        pts, bb = grille(rings)
        com[k] = (rings, pts, bb)
    vers = [v for v in json.loads((D / "dsm_versions.json").read_text()) if v["createdAt"] >= DEBUT]

    def one(v):
        gj = carte(v)
        return (v["createdAt"], mesure(polys(gj), com)) if gj else (v["createdAt"], None)

    with ThreadPoolExecutor(6) as ex:
        res = sorted(ex.map(one, vers), key=lambda r: r[0])
    out = {k: [[t] + m[k] for t, m in res if m] for k in com}
    (D / "couverture_dsm.json").write_text(json.dumps(out))
    print(len(vers), "versions,", sum(m is None for _, m in res), "échecs,", len(com), "communes")


if __name__ == "__main__":
    main()
