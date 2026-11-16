"""Piste n° 66, test sur le passé : marchés « margin of victory » d'élections DÉJÀ VOTÉES, réglés.
Pour chaque marché à tranches : prix (prices-history, fidelity 60) à J+1, J+3, J+7 après la fin du vote (endDate de
l'événement), si avant `closedTime`. Question : après le vote, le prix est-il calibré (gagnés contre attendus par tranche
de prix), et le favori de l'événement gagne-t-il plus souvent que son prix ?  Données : donnees/ (ignoré par Git)."""
import json, math, sys, datetime as dt, collections, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).parent / "donnees"; OUT.mkdir(exist_ok=True)


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def events():
    seen = {}
    for q in ("margin of victory", "vote share margin", "popular vote margin"):
        for page in range(1, 15):
            r = requests.get("https://gamma-api.polymarket.com/public-search", params={
                "q": q, "events_status": "closed", "limit_per_type": 50, "page": page}, headers=H, timeout=30).json()
            ev = r.get("events") or []
            if not ev:
                break
            for e in ev:
                seen[e["id"]] = e
    return [e for e in seen.values() if e.get("closedTime") and (e.get("endDate") or "") >= "2024-01-01"]


def detail(eid):
    return requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()


def history(token, start, end):
    r = requests.get("https://clob.polymarket.com/prices-history", params={
        "market": token, "startTs": int(start), "endTs": int(end), "fidelity": 60}, timeout=30).json()
    return [(p["t"], p["p"]) for p in r.get("history") or []]


def cas(e):
    e = detail(e["id"])
    vote = ts(e["endDate"])
    rows = []
    for m in e.get("markets") or []:
        if not m.get("closed") or not m.get("closedTime"):
            continue
        try:
            pay = json.loads(m["outcomePrices"]); tok = json.loads(m["clobTokenIds"])
        except (KeyError, ValueError, TypeError):
            continue
        if pay[0] not in ("0", "1"):
            continue
        fin = ts(m["closedTime"].replace(" ", "T").replace("+00", "+00:00") if "T" not in m["closedTime"] else m["closedTime"])
        h = history(tok[0], vote - 86400, min(fin, vote + 14 * 86400))
        if not h:
            continue
        pts = {}
        for jours in (1, 3, 7):
            t = vote + jours * 86400
            if t >= fin - 3600:
                continue
            avant = [p for tt, p in h if tt <= t]
            if avant:
                pts[jours] = avant[-1]
        rows.append({"event": e["id"], "title": e["title"], "market": m["id"], "item": m.get("groupItemTitle"),
                     "gagne": int(pay[0] == "1"), "prix": pts, "vote": e["endDate"], "fin": m["closedTime"]})
    return rows


if __name__ == "__main__":
    evs = events()
    print(len(evs), "événements réglés", file=sys.stderr)
    with ThreadPoolExecutor(6) as ex:
        res = [r for rows in ex.map(cas, evs) for r in rows]
    (OUT / "cas.json").write_text(json.dumps(res))
    for jours in (1, 3, 7):
        sel = [r for r in res if str(jours) in r["prix"] or jours in r["prix"]]
        get = lambda r: r["prix"].get(jours, r["prix"].get(str(jours)))
        nev = len({r["event"] for r in sel})
        print(f"J+{jours} : {len(sel)} tranches, {nev} événements")
        for lo, hi in ((0.02, 0.15), (0.15, 0.5), (0.5, 0.85), (0.85, 0.98)):
            s = [r for r in sel if lo <= get(r) < hi]
            if s:
                print(f"   prix {lo}-{hi}: n {len(s)} gagnés {sum(r['gagne'] for r in s)} attendus {sum(get(r) for r in s):.1f}")
