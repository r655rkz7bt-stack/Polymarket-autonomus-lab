"""Piste n° 4 (bo3_coherence) : e-sport (CS2, LoL, Dota 2, Valorant), « vainqueur du match » contre « vainqueur de la carte 1 ».
Pour chaque match réglé des derniers jours : jetons, règlement, et échanges réels (data-api) des deux marchés. -> donnees/matchs.json"""
import json, re, sys, datetime as dt, requests, concurrent.futures as cf, collections
H = {"User-Agent": "curl/8"}
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 45
cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=DAYS)).isoformat()
def get(url, params):
    for _ in range(3):
        try:
            r = requests.get(url, headers=H, params=params, timeout=60)
            if r.status_code == 200: return r.json()
        except requests.RequestException: pass
    return None
def events(series):
    out = []
    for page in range(120):
        b = get("https://gamma-api.polymarket.com/events", {"series_id": series, "closed": "true", "limit": 100, "offset": page * 100, "order": "endDate", "ascending": "false"})
        if not b: break
        for e in b:
            if (e.get("endDate") or "9") < cut[:10]: return out
            out.append(e)
    return out
def trades(eid, tokens):
    rows = []
    for page in range(11):
        b = get("https://data-api.polymarket.com/trades", {"eventId": eid, "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list) or not b: break
        rows += [[int(t["timestamp"]), t["asset"], t["side"], float(t["price"]), float(t["size"])] for t in b if t["asset"] in tokens]
        if len(b) < 1000: break
    return rows
def one(e):
    ml = [m for m in e["markets"] if m.get("sportsMarketType") == "moneyline"]
    g1 = [m for m in e["markets"] if m.get("sportsMarketType") == "child_moneyline" and re.search(r"Game 1|Map 1", m.get("question", ""))]
    if len(ml) != 1 or len(g1) != 1: return None
    ml, g1 = ml[0], g1[0]
    try:
        tm, tg = json.loads(ml["clobTokenIds"]), json.loads(g1["clobTokenIds"]); pm, pg = json.loads(ml["outcomePrices"]), json.loads(g1["outcomePrices"])
        om, og = json.loads(ml["outcomes"]), json.loads(g1["outcomes"])
    except ValueError: return None
    if sorted(pm) != ["0", "1"] or sorted(pg) != ["0", "1"] or om != og: return None
    bo = re.search(r"BO(\d)", ml.get("question", "") + e.get("title", ""))
    return dict(id=e["id"], slug=e["slug"], bo=int(bo.group(1)) if bo else None, start=ml.get("gameStartTime"), teams=om, tm=tm, tg=tg,
                win_m=int(pm[1] == "1"), win_g1=int(pg[1] == "1"), vol=float(ml.get("volume") or 0),
                fs=ml.get("feeSchedule"), fees=ml.get("feesEnabled"), trades=trades(e["id"], set(tm + tg)))
allm = {}
for sid in (10311, 10310, 10309, 10369):
    ev = events(sid); print(sid, len(ev), "événements", flush=True)
    with cf.ThreadPoolExecutor(8) as ex:
        for r in ex.map(one, ev):
            if r: allm[r["id"]] = r
    json.dump(list(allm.values()), open("experiments/bo3_coherence/donnees/matchs.json", "w"))
    print(len(allm), "matchs", flush=True)
