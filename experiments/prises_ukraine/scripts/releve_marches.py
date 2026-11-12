"""Marchés « Will Russia capture / enter <lieu> by …? » réglés et ouverts (Gamma public-search), avec coordonnées lues dans la
règle, source de règlement (ISW ou DeepStateMap), dates et issue. Sortie : donnees/marches.json"""
import json, re, sys, time
from pathlib import Path
import requests

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).resolve().parents[1] / "donnees" / "marches.json"
COORD = re.compile(r"\(\s*(-?\d+\.\d+)°?\s*N?\s*,\s*(-?\d+\.\d+)°?\s*E?\s*\)")


def search(q, status):
    evs, page = {}, 1
    while page < 40:
        r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=60,
                         params={"q": q, "events_status": status, "limit_per_type": 50, "page": page}).json()
        es = r.get("events") or []
        for e in es:
            evs[e["id"]] = e
        if not r.get("pagination", {}).get("hasMore"):
            break
        page += 1
        time.sleep(0.3)
    return evs


def main():
    evs = {}
    for q in ("Will Russia capture", "Will Russia enter", "Which cities will Russia enter", "Will Ukraine recapture", "Will Ukraine re-enter"):
        for st in ("closed", "active"):
            evs.update(search(q, st))
    rows = []
    for i, eid in enumerate(evs):
        ev = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=60).json()
        for m in ev.get("markets") or []:
            desc = m.get("description") or ""
            c = COORD.search(desc)
            src = "isw" if "ISW" in desc or "storymaps" in desc else ("deepstate" if "DeepState" in desc or "deepstatemap" in desc else "autre")
            try:
                prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
            except ValueError:
                prices = []
            rows.append({"event": eid, "titre": ev.get("title"), "id": m["id"], "question": m.get("question"),
                         "groupe": m.get("groupItemTitle"), "lat": float(c.group(1)) if c else None, "lon": float(c.group(2)) if c else None,
                         "source": src, "creation": m.get("createdAt"), "fin": m.get("endDate"), "ferme": m.get("closedTime"),
                         "clos": bool(m.get("closed")), "prix": prices, "tokens": json.loads(m.get("clobTokenIds") or "[]"),
                         "volume": float(m.get("volume") or 0)})
        time.sleep(0.2)
    OUT.write_text(json.dumps(rows))
    print(len(evs), "événements", len(rows), "marchés")


if __name__ == "__main__":
    main()
