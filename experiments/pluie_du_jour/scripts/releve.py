"""Relevé de la famille « Where will it rain on <date>? » (13/11/2026, piste n° 55).

1. événements (liste `donnees/rain_events.json` trouvée par `public-search`) → marchés par ville (Gamma `/events/<id>`) ;
2. vrais échanges de chaque événement (Data API v2, `trades?event_id=`, curseur) ;
3. observations horaires METAR (IEM, `asos.py`, colonne `p01i`) de chaque station citée par le règlement (`issuedby=XXX`).
Sorties dans `donnees/` (ignoré par Git). Usage : python releve.py
"""
import json, os, re, sys, time, csv, io
from concurrent.futures import ThreadPoolExecutor
import requests

H = {"User-Agent": "curl/8"}
D = os.path.join(os.path.dirname(__file__), "..", "donnees")


def get(url, params=None, tries=4):
    for k in range(tries):
        try:
            r = requests.get(url, params=params, headers=H, timeout=60)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        time.sleep(2 * (k + 1))
    return None


def marches(eid):
    r = get(f"https://gamma-api.polymarket.com/events/{eid}")
    if r is None:
        return eid, None
    e = r.json()
    out = []
    for m in e.get("markets", []):
        src = m.get("resolutionSource") or ""
        st = re.search(r"issuedby=([A-Z0-9]+)", src)
        out.append({"market_id": m["id"], "ville": m.get("groupItemTitle"), "station": st.group(1) if st else None,
                    "condition": m.get("conditionId"), "tokens": json.loads(m.get("clobTokenIds") or "[]"),
                    "outcomes": json.loads(m.get("outcomes") or "[]"), "final": json.loads(m.get("outcomePrices") or "[]"),
                    "fee": m.get("feeType"), "closed": m.get("closed"), "umaStatus": m.get("umaResolutionStatus")})
    return eid, {"id": eid, "title": e.get("title"), "endDate": e.get("endDate"), "createdAt": e.get("createdAt"), "markets": out}


def echanges(eid):
    rows, cur = [], None
    for _ in range(50):
        p = {"event_id": eid, "limit": 1000}
        if cur:
            p["cursor"] = cur
        r = get("https://data-api.polymarket.com/v2/trades", p)
        if r is None:
            break
        j = r.json()
        rows += j.get("data") or []
        pag = j.get("pagination") or {}
        cur = pag.get("next_cursor") if pag.get("has_more") else None
        if not cur:
            break
    return eid, rows


def metar(st):
    r = get("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py",
            {"station": st, "data": "p01i", "year1": 2026, "month1": 6, "day1": 1, "year2": 2026, "month2": 11, "day2": 14,
             "tz": "Etc/UTC", "format": "onlycomma", "latlon": "no", "missing": "M", "trace": "T", "report_type": [3, 4]})
    return st, (r.text if r is not None else None)


if __name__ == "__main__":
    evs = [e for e in json.load(open(os.path.join(D, "rain_events.json")))]
    with ThreadPoolExecutor(6) as ex:
        ev = dict(ex.map(marches, [e["id"] for e in evs]))
    json.dump(ev, open(os.path.join(D, "marches.json"), "w"))
    print("événements", len(ev), "marchés", sum(len(v["markets"]) for v in ev.values() if v))
    with ThreadPoolExecutor(6) as ex:
        tr = dict(ex.map(echanges, list(ev)))
    json.dump(tr, open(os.path.join(D, "echanges.json"), "w"))
    print("échanges", sum(len(v) for v in tr.values()))
    sts = sorted({m["station"] for v in ev.values() if v for m in v["markets"] if m["station"]})
    print("stations", sts)
    with ThreadPoolExecutor(4) as ex:
        mt = dict(ex.map(metar, sts))
    json.dump(mt, open(os.path.join(D, "metar.json"), "w"))
    print("metar", {k: (len(v.splitlines()) if v else None) for k, v in mt.items()})
