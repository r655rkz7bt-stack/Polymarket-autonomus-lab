"""Événements « Billboard 200 #1 Album Week of <date> » réglés (Gamma public-search), avec gagnant et jetons.
Sortie : experiments/billboard_hdd/releves/evenements.json"""
import json, time
from pathlib import Path
import requests
OUT = Path(__file__).resolve().parents[1] / "releves" / "evenements.json"
OUT.parent.mkdir(exist_ok=True)
H = {"User-Agent": "curl/8"}
seen, res = set(), []
for page in range(1, 12):
    d = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=60, params={
        "q": "Billboard 200 #1 Album", "events_status": "closed", "limit_per_type": 50, "page": page}).json()
    evs = d.get("events") or []
    for e in evs:
        if e["id"] in seen or "Billboard 200 #1" not in e["title"]:
            continue
        seen.add(e["id"])
        full = requests.get(f"https://gamma-api.polymarket.com/events/{e['id']}", headers=H, timeout=60).json()
        ms = []
        for m in full["markets"]:
            if "outcomePrices" not in m or float(m.get("volume") or 0) <= 0:
                continue
            ms.append({"id": m["id"], "nom": m.get("groupItemTitle"), "issue": float(json.loads(m["outcomePrices"])[0]),
                       "jeton": json.loads(m["clobTokenIds"])[0], "volume": float(m["volume"])})
        res.append({"id": e["id"], "titre": e["title"], "fin": full.get("endDate"), "ferme": full.get("closedTime"),
                    "debut": full.get("startDate"), "marches": ms})
        time.sleep(0.2)
    if not d.get("pagination", {}).get("hasMore", len(evs) == 50):
        break
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=0))
print(len(res), sorted(r["titre"][-25:] for r in res)[:5])
