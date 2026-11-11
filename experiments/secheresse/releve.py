"""Piste n° 24 (11/11/2026) : sécheresse exceptionnelle (D4) par État, US Drought Monitor contre prix Polymarket.

1. USDM : statistiques catégorielles hebdomadaires de chaque État (part de la surface en D0..D4), 2000 → aujourd'hui,
   `usdmdataservices.unl.edu` (sans clé, code FIPS).
2. Gamma : événements « Exceptional drought (D4) by state — week of … » réglés (public-search), marchés, issues.
3. Data API v2 : tous les échanges de chaque événement (`event_id`).
Sorties dans `donnees/` (ignoré par Git) ; le résumé des marchés est versionné (`marches.json`)."""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

H = {"User-Agent": "curl/8", "Accept": "application/json"}
D = Path(__file__).parent / "donnees"
D.mkdir(exist_ok=True)
FIPS = {"Alabama": "01", "Arizona": "04", "Arkansas": "05", "California": "06", "Colorado": "08", "Connecticut": "09",
        "Delaware": "10", "Florida": "12", "Georgia": "13", "Idaho": "16", "Illinois": "17", "Indiana": "18", "Iowa": "19",
        "Kansas": "20", "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24", "Massachusetts": "25",
        "Michigan": "26", "Minnesota": "27", "Mississippi": "28", "Missouri": "29", "Montana": "30", "Nebraska": "31",
        "Nevada": "32", "New Hampshire": "33", "New Jersey": "34", "New Mexico": "35", "New York": "36",
        "North Carolina": "37", "North Dakota": "38", "Ohio": "39", "Oklahoma": "40", "Oregon": "41", "Pennsylvania": "42",
        "Rhode Island": "44", "South Carolina": "45", "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49",
        "Vermont": "50", "Virginia": "51", "Washington": "53", "West Virginia": "54", "Wisconsin": "55", "Wyoming": "56"}


def get(url, params=None, tries=4):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=H, timeout=60)
            if r.status_code == 200:
                return r.json()
        except (requests.RequestException, ValueError):
            pass
        time.sleep(2 ** i)
    raise RuntimeError(url)


def usdm():
    def one(item):
        name, code = item
        rows = []
        for a, b in ((2000, 2009), (2010, 2019), (2020, 2026)):
            rows += get("https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent",
                        {"aoi": code, "startdate": f"1/1/{a}", "enddate": f"12/31/{b}", "statisticsType": 2})
        return name, sorted(({"date": r["mapDate"][:10], **{k: float(r[k]) for k in ("none", "d0", "d1", "d2", "d3", "d4")}}
                             for r in rows), key=lambda r: r["date"])
    with ThreadPoolExecutor(6) as ex:
        out = dict(ex.map(one, FIPS.items()))
    json.dump(out, open(D / "usdm.json", "w"))
    print("usdm", sum(len(v) for v in out.values()), "lignes")


def gamma():
    evs = {}
    for status in ("closed", "active"):
        for page in range(1, 6):
            res = get("https://gamma-api.polymarket.com/public-search",
                      {"q": "Exceptional drought (D4) by state", "events_status": status, "limit_per_type": 50, "page": page})
            lot = res.get("events") or []
            for e in lot:
                if e.get("title", "").startswith("Exceptional drought (D4) by state"):
                    evs[e["id"]] = e["id"]
            if len(lot) < 50:
                break
    marches = []
    for eid in evs:
        e = get(f"https://gamma-api.polymarket.com/events/{eid}")
        for m in e.get("markets") or []:
            prices = json.loads(m.get("outcomePrices") or "[]")
            toks = json.loads(m.get("clobTokenIds") or "[]")
            marches.append({"event": eid, "titre": e["title"], "fin": e.get("endDate"), "id": m["id"], "etat": m.get("groupItemTitle"),
                            "condition": m.get("conditionId"), "yes": toks[0] if toks else None, "no": toks[1] if len(toks) > 1 else None,
                            "clos": m.get("closed"), "prix": prices, "volume": float(m.get("volume") or 0),
                            "cree": m.get("createdAt"), "ferme": m.get("closedTime"), "frais": m.get("feeType")})
    json.dump(marches, open(Path(__file__).parent / "marches.json", "w"), indent=0)
    print("gamma", len(evs), "événements", len(marches), "marchés")


def echanges():
    marches = json.load(open(Path(__file__).parent / "marches.json"))
    out = []
    for eid in sorted({m["event"] for m in marches}):
        cur = None
        for _ in range(50):
            p = {"event_id": eid, "limit": 1000}
            if cur:
                p["cursor"] = cur
            res = get("https://data-api.polymarket.com/v2/trades", p)
            lot = res.get("data") or []
            out += lot
            pag = res.get("pagination") or {}
            cur = pag.get("next_cursor") if pag.get("has_more") else None
            if not cur:
                break
    json.dump(out, open(D / "echanges.json", "w"))
    print("échanges", len(out))


if __name__ == "__main__":
    for step in sys.argv[1:] or ["usdm", "gamma", "echanges"]:
        globals()[step]()
