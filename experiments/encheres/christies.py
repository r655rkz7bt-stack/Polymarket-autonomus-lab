"""Lots d'une vente Christie's (page de vente, JSON embarqué « lots »), robots.txt relu le 12/11/2026 (pages de vente autorisées).

Usage : python christies.py <numéro de vente>... → donnees/lots_<n>.json (estimations basse/haute, prix réalisé, garantie).
"""
import json, re, sys, time
from pathlib import Path
import requests

ICI = Path(__file__).parent
H = {"User-Agent": "Mozilla/5.0"}


def lots_de_la_page(html: str) -> list[dict]:
    i = html.find('"lots":[')
    if i < 0:
        return []
    dec = json.JSONDecoder()
    arr, _ = dec.raw_decode(html[i + len('"lots":'):])
    return arr


def vente(n: str) -> dict:
    html = requests.get(f"https://www.christies.com/en/auction/auction-{n}-nyr/browse-lots", headers=H, timeout=30).text
    titre = re.search(r"<title>([^<]{0,120})", html)
    date = re.search(r'"(?:sale_start_date|start_date|date_start)[a-z_]*"\s*:\s*"([^"]+)"', html)
    return {"vente": n, "titre": titre.group(1) if titre else "", "date": date.group(1) if date else "",
            "lots": lots_de_la_page(html)}


if __name__ == "__main__":
    out = ICI / "donnees"
    out.mkdir(exist_ok=True)
    for n in sys.argv[1:]:
        v = vente(n)
        (out / f"lots_{n}.json").write_text(json.dumps(v), encoding="utf-8")
        vendus = [l for l in v["lots"] if float(l.get("price_realised") or 0) > 0]
        print(n, v["titre"][:40], v["date"][:10], len(v["lots"]), "lots,", len(vendus), "vendus")
        time.sleep(1)
