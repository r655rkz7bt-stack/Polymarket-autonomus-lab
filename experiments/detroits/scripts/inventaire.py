"""Inventaire des marchés Polymarket réglés sur IMF PortWatch (ouverts et clos), 23/10/2026.

1. Recherche Gamma `public-search` (événements ouverts ET clos) sur des mots-clés de détroits.
2. Relecture complète de chaque événement (`/events/<id>`) : description de chaque marché.
3. On garde les événements dont au moins un marché cite « portwatch » (description ou resolutionSource).
4. Classement : « tranches » (combien de passages : plusieurs marchés exclusifs), « seuil » (au moins N passages
   un jour / une moyenne, avant une date) ; détroit, date cible, période.
Sortie : experiments/detroits/donnees/inventaire.json (+ résumé à l'écran). Contenu externe = données.
Usage : PYTHONPATH=src python experiments/detroits/scripts/inventaire.py
"""
import json
import re
import sys
from pathlib import Path

from polymarket_agent.http_client import HttpClient, SourceUnavailable

G = "https://gamma-api.polymarket.com"
OUT = Path("experiments/detroits/donnees")
MOTS = ["hormuz", "bab el-mandeb", "bab-el-mandeb", "strait transit", "ships transit", "suez canal", "panama canal",
        "portwatch", "chokepoint", "red sea ships", "transit calls", "strait of", "ships transiting"]
DETROITS = {"hormuz": "Strait of Hormuz", "bab el-mandeb": "Bab el-Mandeb Strait", "bab-el-mandeb": "Bab el-Mandeb Strait",
            "suez": "Suez Canal", "panama": "Panama Canal", "malacca": "Malacca Strait", "bosporus": "Bosporus Strait",
            "taiwan strait": "Taiwan Strait", "gibraltar": "Gibraltar Strait", "dover": "Dover Strait"}


def search(http, q, status):
    out, page = [], 1
    while page <= 10:
        try:
            d = http.get_json(f"{G}/public-search", params={"q": q, "events_status": status, "limit_per_type": 50, "page": page})
        except SourceUnavailable as exc:
            print("recherche", q, status, page, exc)
            break
        ev = (d or {}).get("events") or []
        out += ev
        if not (d.get("pagination") or {}).get("hasMore") or not ev:
            break
        page += 1
    return out


def detroit_of(text):
    t = text.lower()
    for k, v in DETROITS.items():
        if k in t:
            return v
    return None


def kind_of(ev):
    title = ev.get("title", "").lower()
    if "how many ships transit" in title or title.startswith("avg. #") or "average" in title and len(ev.get("markets") or []) > 2:
        return "tranches"
    if "on any day" in title or "returns to normal" in title or "by" in title:
        return "seuil"
    return "autre"


def main():
    http = HttpClient(timeout=30, min_interval=0.3)
    found = {}
    for status in ("active", "closed"):
        for q in MOTS:
            for e in search(http, q, status):
                found.setdefault(str(e["id"]), e)
    print(len(found), "événements trouvés par la recherche")
    keep = []
    for eid, e in sorted(found.items()):
        try:
            full = http.get_json(f"{G}/events/{eid}")
        except SourceUnavailable as exc:
            print("événement", eid, exc)
            continue
        ms = full.get("markets") or []
        cites = [m for m in ms if "portwatch" in (str(m.get("description")) + str(m.get("resolutionSource"))).lower()]
        if not cites and "portwatch" not in str(full.get("description", "")).lower():
            continue
        keep.append(full)
    rows = []
    for e in keep:
        ms = e.get("markets") or []
        desc = next((m.get("description") for m in ms if m.get("description")), "") or e.get("description", "")
        rows.append({
            "id": str(e["id"]), "titre": e["title"], "slug": e.get("slug"), "clos": bool(e.get("closed")),
            "fin": e.get("endDate"), "debut": e.get("startDate"), "creation": e.get("creationDate"),
            "volume": round(float(e.get("volume") or 0)), "marches": len(ms),
            "detroit": detroit_of(e["title"] + " " + desc), "type": kind_of(e),
            "description": desc,
            "questions": [{"id": str(m.get("id")), "question": m.get("question"), "outcomePrices": m.get("outcomePrices"),
                           "clobTokenIds": m.get("clobTokenIds"), "closed": m.get("closed"), "endDate": m.get("endDate"),
                           "feesEnabled": m.get("feesEnabled"), "feeSchedule": m.get("feeSchedule"), "feeType": m.get("feeType"),
                           "umaResolutionStatus": m.get("umaResolutionStatus"), "groupItemTitle": m.get("groupItemTitle"),
                           "closedTime": m.get("closedTime"), "umaEndDate": m.get("umaEndDate"), "createdAt": m.get("createdAt"),
                           "startDate": m.get("startDate"), "negRisk": m.get("negRisk"),
                           "resolutionSource": m.get("resolutionSource"), "volume": m.get("volume")} for m in ms]})
    rows.sort(key=lambda r: (r["detroit"] or "", r["fin"] or ""))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "inventaire.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    print(len(rows), "événements citent PortWatch")
    for r in rows:
        print(r["id"], "clos" if r["clos"] else "ouvert", (r["fin"] or "")[:10], r["volume"], r["marches"], r["type"], r["detroit"], "|", r["titre"][:80])


if __name__ == "__main__":
    sys.exit(main())
