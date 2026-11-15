"""Piste n° 62 : Kalshi KXHIGH{AUS,MIA,DEN,LAX} réglés depuis la bascule « historical » (15/09/2026) : marchés (bornes, résultat,
valeur CLI = expiration_value) et bougies horaires de l'événement entier (un appel par événement : /series/<s>/events/<e>/candlesticks).
API publique sans clé, débit très limité (429) : pauses. Reprend là où il s'est arrêté. Sortie : donnees/kalshi.json."""
import json, os, time, datetime as dt, requests
B = "https://api.elections.kalshi.com/trade-api/v2"; H = {"User-Agent": "curl/8"}
P = "donnees/kalshi.json"
def get(path, **params):
    for k in range(40):
        r = requests.get(B + path, params=params, headers=H, timeout=30)
        if r.status_code == 429: time.sleep(min(30, 3 + 2 * k)); continue
        r.raise_for_status(); time.sleep(1.0); return r.json()
    raise RuntimeError(path)
out = json.load(open(P)) if os.path.exists(P) else {}
for s in ("KXHIGHAUS", "KXHIGHMIA", "KXHIGHDEN", "KXHIGHLAX"):
    ms, cur = [], None
    while True:
        d = get("/markets", series_ticker=s, status="settled", limit=1000, **({"cursor": cur} if cur else {}))
        ms += d["markets"]; cur = d.get("cursor")
        if not cur or not d["markets"]: break
    evs = {}
    for m in ms:
        evs.setdefault(m["event_ticker"], []).append({k: m.get(k) for k in ("ticker", "floor_strike", "cap_strike", "strike_type", "result",
                                                                           "expiration_value", "open_time", "close_time", "yes_sub_title", "volume_fp")})
    print(s, len(ms), "marchés", len(evs), "événements", flush=True)
    for e, mk in sorted(evs.items()):
        if e in out: continue
        t0 = min(int(dt.datetime.fromisoformat(m["open_time"].replace("Z", "+00:00")).timestamp()) for m in mk)
        t1 = max(int(dt.datetime.fromisoformat(m["close_time"].replace("Z", "+00:00")).timestamp()) for m in mk)
        try:
            c = get(f"/series/{s}/events/{e}/candlesticks", start_ts=t0, end_ts=t1, period_interval=60)
        except Exception as x:
            print(e, x, flush=True); continue
        bougies = {}
        for tk, cs in zip(c.get("market_tickers") or [], c.get("market_candlesticks") or []):
            bougies[tk] = [(b["end_period_ts"], (b.get("yes_bid") or {}).get("close_dollars"), (b.get("yes_ask") or {}).get("close_dollars"),
                            (b.get("price") or {}).get("close_dollars"), b.get("volume_fp") or b.get("volume")) for b in cs]
        out[e] = {"serie": s, "marches": mk, "bougies": bougies}
        json.dump(out, open(P, "w")); print(e, len(out), flush=True)
json.dump(out, open(P, "w")); print("fini", len(out))
