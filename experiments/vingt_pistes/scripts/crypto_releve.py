import json, time, requests
from datetime import datetime, timedelta, timezone
D = "donnees/cr"
s = requests.Session()
def get(url, params):
    for k in range(5):
        try:
            return s.get(url, params=params, timeout=40).json()
        except Exception:
            time.sleep(2 ** k)
    return None
ASSETS = {"bitcoin": "BTCUSDT", "ethereum": "ETHUSDT", "solana": "SOLUSDT", "xrp": "XRPUSDT"}
out = {"klines": {}, "events": []}
start = datetime(2026, 6, 20, tzinfo=timezone.utc)
for name, sym in ASSETS.items():
    rows, t = [], int(start.timestamp() * 1000)
    while True:
        r = get("https://data-api.binance.vision/api/v3/klines", {"symbol": sym, "interval": "1h", "startTime": t, "limit": 1000}) or []
        if not r: break
        rows += [[x[0], float(x[1]), float(x[4])] for x in r]
        t = r[-1][0] + 3600000
        if len(r) < 1000: break
    out["klines"][name] = rows
    print(name, len(rows), flush=True)
day = datetime(2026, 7, 1, tzinfo=timezone.utc)
while day < datetime(2026, 10, 20, tzinfo=timezone.utc):
    for name, sym in ASSETS.items():
        slug = f"{name}-up-or-down-on-{day:%B}-{day.day}-{day.year}".lower()
        ev = get("https://gamma-api.polymarket.com/events", {"slug": slug})
        if not ev: continue
        m = ev[0]["markets"][0]
        tok = json.loads(m.get("clobTokenIds") or "[]")
        end = datetime.fromisoformat(m["endDate"].replace("Z", "+00:00"))
        st = end - timedelta(days=1)
        hist = (get("https://clob.polymarket.com/prices-history", {"market": tok[0], "startTs": int(st.timestamp()) - 6 * 3600,
                                                                 "endTs": int(end.timestamp()), "fidelity": 10}) or {}).get("history") or []
        k0 = get("https://data-api.binance.vision/api/v3/klines", {"symbol": sym, "interval": "1m", "startTime": int(st.timestamp() * 1000), "limit": 1}) or []
        k1 = get("https://data-api.binance.vision/api/v3/klines", {"symbol": sym, "interval": "1m", "startTime": int(end.timestamp() * 1000), "limit": 1}) or []
        out["events"].append({"actif": name, "slug": slug, "debut": st.isoformat(), "fin": end.isoformat(),
                              "outcomes": m.get("outcomes"), "prix_final": m.get("outcomePrices"), "volume": ev[0].get("volume"),
                              "s0": float(k0[0][4]) if k0 else None, "s1": float(k1[0][4]) if k1 else None, "hist": hist})
        time.sleep(0.1)
    print(day.date(), len(out["events"]), flush=True)
    day += timedelta(days=1)
json.dump(out, open(f"{D}/data.json", "w"))
print("fini")
