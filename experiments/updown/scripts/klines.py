"""Barres d'une minute du BTC/USDT (miroir public Binance, sans clé) -> donnees/klines_btc.json : [[ouverture_s, open, high, low, close], ...]"""
import requests, json, os, sys, time, datetime as dt
ICI = os.path.dirname(os.path.abspath(__file__))
d0 = sys.argv[1]
t = int(dt.datetime.fromisoformat(d0).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
now = int(time.time() * 1000); out = []
while t < now:
    r = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol="BTCUSDT", interval="1m", startTime=t, limit=1000), timeout=30)
    j = r.json()
    if not j:
        break
    out += [[x[0] // 1000, float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in j]
    t = j[-1][0] + 60000
json.dump(out, open(os.path.join(ICI, "..", "donnees", "klines_btc.json"), "w"))
print(len(out), out[0][0], out[-1][0])
