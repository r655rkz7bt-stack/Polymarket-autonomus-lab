"""Argent informé (16/10/2026) : gros échanges (≥ 100 $) des marchés résolus du 15/09 au 15/10/2026.

Usage : python3 -I experiments/smart_money/collect.py <dossier_de_travail> src
Sortie : <dossier>/sm/markets.json (marchés résolus net à 1/0) et <dossier>/sm/trades/<conditionId>.json.
  Gamma  : /events?closed=true&end_date_min=..&end_date_max=..&limit=100&offset=..
  Data   : https://data-api.polymarket.com/trades?market=<conditionId>&limit=500&offset=..
           &filterType=CASH&filterAmount=100&takerOnly=false   (public, sans clé)
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

SP = sys.argv[1]
sys.path.insert(0, sys.argv[2])
from polymarket_agent.http_client import HttpClient, SourceUnavailable  # noqa: E402

http = HttpClient(min_interval=0.05)
OUT = f"{SP}/sm"
os.makedirs(f"{OUT}/trades", exist_ok=True)
START, END, MIN_VOLUME = "2026-09-15", "2026-10-15", 20000


def jl(v):
    try:
        return json.loads(v) if isinstance(v, str) else (v or [])
    except ValueError:
        return []


path = f"{OUT}/markets.json"
if os.path.exists(path):
    markets = json.load(open(path))
else:
    from datetime import date, timedelta
    markets, seen = [], set()
    days = [date.fromisoformat(START) + timedelta(days=i)
            for i in range((date.fromisoformat(END) - date.fromisoformat(START)).days + 1)]
    pages = [(d, page) for d in days for page in range(60)]  # Gamma refuse les décalages trop grands
    done_day = None
    for d, page in pages:
        if d == done_day:
            continue
        try:
            batch = http.get_json("https://gamma-api.polymarket.com/events", params={
                "closed": "true", "limit": 100, "offset": page * 100,
                "end_date_min": f"{d}T00:00:00Z", "end_date_max": f"{d}T23:59:59Z"})
        except SourceUnavailable as exc:
            print("arrêt du jour", d, "page", page, exc)
            done_day = d
            continue
        if not isinstance(batch, list) or len(batch) < 100:
            done_day = d
        for ev in batch if isinstance(batch, list) else []:
            if ev.get("id") in seen:
                continue
            seen.add(ev.get("id"))
            tags = [t.get("slug") for t in ev.get("tags") or [] if isinstance(t, dict)]
            for m in ev.get("markets") or []:
                prices, tokens = [str(p) for p in jl(m.get("outcomePrices"))], [str(t) for t in jl(m.get("clobTokenIds"))]
                if len(tokens) != 2 or sorted(prices) != ["0", "1"] or float(m.get("volumeNum") or 0) < MIN_VOLUME:
                    continue
                markets.append({"cid": m.get("conditionId"), "id": m.get("id"), "q": m.get("question"),
                                "slug": ev.get("slug"), "tags": tags, "tokens": tokens,
                                "winner": tokens[prices.index("1")], "end": m.get("endDate") or ev.get("endDate"),
                                "closed": m.get("closedTime"), "volume": float(m.get("volumeNum") or 0)})
    json.dump(markets, open(path, "w"))
print(len(markets), "marchés résolus (volume ≥ %d $)" % MIN_VOLUME)


def job(m):
    p = f"{OUT}/trades/{m['cid']}.json"
    if os.path.exists(p):
        return 0
    rows = []
    for page in range(10):
        try:
            batch = http.get_json("https://data-api.polymarket.com/trades", params={
                "market": m["cid"], "limit": 500, "offset": page * 500, "filterType": "CASH",
                "filterAmount": 100, "takerOnly": "false"})
        except SourceUnavailable:
            return 0  # réessayé au prochain lancement
        if not isinstance(batch, list):
            break
        rows += [{k: t.get(k) for k in ("proxyWallet", "side", "asset", "size", "price", "timestamp")} for t in batch]
        if len(batch) < 500:
            break
    json.dump(rows, open(p, "w"))
    return len(rows)


with ThreadPoolExecutor(6) as ex:
    n = sum(ex.map(job, markets))
print(n, "nouveaux échanges")
