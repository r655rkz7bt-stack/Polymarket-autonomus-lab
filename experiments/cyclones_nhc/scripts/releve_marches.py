"""Piste n° 63 : relève les événements Polymarket réglés sur l'intensité d'un cyclone du NHC (Atlantique, Pacifique Est et Central).

« Will Tropical Storm X strengthen to a hurricane? », « How strong will X be? » (catégorie de pointe), « X becomes a major hurricane? »…
Sortie : donnees/evenements.json (événement, marchés, jetons, description). Recherche Gamma `public-search` (pages numérotées de 50, recherche plein texte : pas de liste `/events` à parcourir).
"""
import json, re, sys, requests
from pathlib import Path

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).resolve().parents[1] / "donnees" / "evenements.json"
REQUETES = ["strengthen to a hurricane", "strengthens to a hurricane", "How strong will", "become a hurricane", "become a major hurricane",
            "Hurricane Category", "peak intensity hurricane", "reach Category", "hurricane strength", "Tropical Storm", "Hurricane"]

def main():
    vus = {}
    for q in REQUETES:
        for page in range(1, 12):
            r = requests.get("https://gamma-api.polymarket.com/public-search", params=dict(q=q, events_status="closed", limit_per_type=50, page=page), headers=H, timeout=30).json()
            ev = r.get("events") or []
            for e in ev:
                vus[e["id"]] = e["title"]
            if len(ev) < 50:
                break
    garde = []
    for i, titre in vus.items():
        if not re.search(r"strength|how strong|categor|major hurricane|become a hurricane|hurricane\?", titre, re.I):
            continue
        e = requests.get(f"https://gamma-api.polymarket.com/events/{i}", headers=H, timeout=30).json()
        d = e.get("description") or ""
        if "National Hurricane Center" not in d and "NHC" not in d and "nhc.noaa" not in (e.get("resolutionSource") or ""):
            continue
        garde.append(dict(id=e["id"], titre=e["title"], debut=e.get("startDate"), fin=e.get("endDate"), description=d,
                          marches=[dict(id=m["id"], titre=m.get("groupItemTitle") or m["question"], condition=m.get("conditionId"),
                                        jetons=json.loads(m.get("clobTokenIds") or "[]"), issues=json.loads(m.get("outcomes") or "[]"),
                                        prix=json.loads(m.get("outcomePrices") or "[]"), volume=float(m.get("volume") or 0),
                                        frais=m.get("feeType"), ferme=m.get("closedTime"))
                                   for m in e.get("markets", [])]))
    OUT.write_text(json.dumps(garde, indent=1))
    for g in sorted(garde, key=lambda g: g["debut"] or ""):
        print(g["id"], (g["debut"] or "")[:10], g["titre"][:70], len(g["marches"]), round(sum(m["volume"] for m in g["marches"])))
    print(len(garde), "événements")

if __name__ == "__main__":
    main()
