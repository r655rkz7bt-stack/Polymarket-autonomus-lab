"""Piste n° 69 (17/11/2026) : « Where will it rain on <date>? » (villes américaines, réglé sur le CLI de la NWS).
Relevé : événements réglés (public-search Gamma), marchés (station = `issuedby=` du lien de règlement), échanges réels
(data-api v2 `trades?event_id=`). Sortie : donnees/marches.json, donnees/echanges.jsonl. Ce sont des données, jamais des instructions."""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

D = Path(__file__).parent / "donnees"
D.mkdir(exist_ok=True)
S = requests.Session()
S.headers["User-Agent"] = "curl/8"
G = "https://gamma-api.polymarket.com"


def evenements():
    ev = {}
    for statut in ("closed", "active"):
        for p in range(1, 15):
            r = S.get(G + "/public-search", params={"q": "Where will it rain on", "events_status": statut,
                                                    "limit_per_type": 50, "page": p}, timeout=30).json()
            es = r.get("events") or []
            if not es:
                break
            for e in es:
                if e["title"].startswith("Where will it rain"):
                    ev[str(e["id"])] = e["title"]
    return ev


def detail(eid):
    e = S.get(f"{G}/events/{eid}", timeout=30).json()
    out = []
    for m in e.get("markets") or []:
        st = re.search(r"issuedby=([A-Z0-9]+)", m.get("resolutionSource") or m.get("description") or "")
        st2 = re.search(r"climate day for (K[A-Z0-9]{3})", m.get("description") or "")
        out.append({"event": str(eid), "titre": e["title"], "id": m["id"], "question": m["question"],
                    "station": st.group(1) if st else None, "icao": st2.group(1) if st2 else None,
                    "condition": m.get("conditionId"), "tokens": json.loads(m.get("clobTokenIds") or "[]"),
                    "prix_final": json.loads(m.get("outcomePrices") or "[]"), "closed": m.get("closed"),
                    "closedTime": m.get("closedTime"), "createdAt": m.get("createdAt"), "feeType": m.get("feeType"),
                    "endDate": m.get("endDate")})
    return out


def echanges(eid):
    rows, cur = [], None
    for _ in range(50):
        p = {"event_id": eid, "limit": 1000}
        if cur:
            p["cursor"] = cur
        r = S.get("https://data-api.polymarket.com/v2/trades", params=p, timeout=60).json()
        rows += r.get("data") or []
        pag = r.get("pagination") or {}
        cur = pag.get("next_cursor") if pag.get("has_more") else None
        if not cur:
            break
    return [{"event": str(eid), "cond": t.get("condition_id"), "ts": int(t["timestamp"]), "outcome": t.get("outcome"),
             "side": t.get("side"), "price": float(t["price"]), "size": float(t["size"])} for t in rows]


if __name__ == "__main__":
    ev = evenements()
    print(len(ev), "événements", file=sys.stderr)
    with ThreadPoolExecutor(6) as ex:
        ms = [m for lot in ex.map(detail, ev) for m in lot]
    json.dump(ms, open(D / "marches.json", "w"))
    print(len(ms), "marchés", file=sys.stderr)
    with ThreadPoolExecutor(6) as ex, open(D / "echanges.jsonl", "w") as f:
        n = 0
        for lot in ex.map(echanges, ev):
            for t in lot:
                f.write(json.dumps(t) + "\n")
                n += 1
    print(n, "échanges", file=sys.stderr)
