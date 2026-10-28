"""Piste « sauts en match » (28/10/2026) : relevé des matchs réglés de tennis (ATP, WTA) et d'e-sport (CS2, LoL, Dota 2, Valorant) depuis CUT,
marché « vainqueur » (moneyline) seulement, puis leurs échanges réels (data-api, preneurs). Reprise possible. Lancer depuis la racine du dépôt.
Événements par /events/keyset (jamais offset : tests/test_releves_gamma.py)."""
import json, os, sys, time, datetime, requests, gzip
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "src")
SERIES = {"atp": 10365, "wta": 10366, "cs2": 10310, "lol": 10311, "dota2": 10309, "val": 10369}
CUT = datetime.datetime.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else "2026-08-01").replace(tzinfo=datetime.timezone.utc)
VMIN = float(sys.argv[2]) if len(sys.argv) > 2 else 2000
OUT = "experiments/sauts_en_jeu/donnees"
CHAMPS = ("id", "conditionId", "question", "outcomes", "outcomePrices", "clobTokenIds", "sportsMarketType", "feeSchedule", "feesEnabled",
          "umaResolutionStatus", "volumeNum", "closedTime", "gameStartTime")
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def jget(url, params):
    for k in range(6):
        try:
            r = s.get(url, params=params, timeout=120)
            if r.status_code == 200: return r.json()
        except Exception:
            pass
        time.sleep(2 ** k)
    return None
def start_of(e):
    for m in e.get("markets") or []:
        if m.get("gameStartTime"):
            return datetime.datetime.fromisoformat(m["gameStartTime"].replace("+00", "+00:00").replace("Z", "+00:00"))
def pull(item):
    name, sid = item
    out, cursor, vieux, vus = [], None, 0, 0
    while True:
        p = {"series_id": sid, "closed": "true", "limit": 100, "order": "endDate", "ascending": "false"}
        if cursor: p["after_cursor"] = cursor
        d = jget("https://gamma-api.polymarket.com/events/keyset", p)
        if not d or not d.get("events"): break
        for e in d["events"]:
            vus += 1
            st = start_of(e)
            if st is None: continue
            vieux = vieux + 1 if st < CUT else 0
            if st < CUT: continue
            mk = [m for m in e.get("markets") or [] if m.get("sportsMarketType") == "moneyline"]
            if len(mk) != 1 or float(mk[0].get("volumeNum") or 0) < VMIN: continue
            out.append({"sport": name, "id": e["id"], "title": e.get("title"), "start": st.isoformat(), "markets": [{k: m.get(k) for k in CHAMPS} for m in mk]})
        cursor = d.get("next_cursor")
        if not cursor or vieux > 1500: break
    print(name, vus, "lus,", len(out), "gardés", flush=True)
    return out
def trades(ev):
    path = f"{OUT}/echanges/{ev['id']}.json.gz"
    if os.path.exists(path): return True
    rows = []
    for page in range(11):
        b = jget("https://data-api.polymarket.com/trades", {"eventId": ev["id"], "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list) or not b: break
        rows += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
        if len(b) < 1000: break
    open(path, "wb").write(gzip.compress(json.dumps(rows).encode()))
    return True
if __name__ == "__main__":
    evs = []
    with ThreadPoolExecutor(6) as ex:
        for res in ex.map(pull, SERIES.items()): evs += res
    json.dump(evs, open(f"{OUT}/evenements.json", "w"))
    print("événements", len(evs), flush=True)
    with ThreadPoolExecutor(8) as ex:
        for i, _ in enumerate(ex.map(trades, evs)):
            if i % 200 == 0: print("échanges", i, len(evs), time.strftime("%H:%M:%S"), flush=True)
    print("fini")
