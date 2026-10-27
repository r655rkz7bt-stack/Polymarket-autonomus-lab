"""28/10/2026 (passage du 27/10 soir) : barres horaires Binance (miroir public data-api.binance.vision, sans clé : c'est aussi la SOURCE de règlement des
marchés « above / reach » de Polymarket) des principales cryptos, pour calculer une probabilité de modèle (volatilité réalisée) à comparer au prix du
marché. Yahoo répond 429 depuis la routine, api.binance.com refuse la zone. Écrit donnees/spot_<SYMBOLE>.json ([[debut_s, ouverture, haut, bas, clôture], ...]),
du 01/01/2024 à maintenant. Usage : python releve_spot.py"""
import json, requests, time, datetime
S = requests.Session()
DEBUT = int(datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
for sym in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE"]:
    rows, t = [], DEBUT
    while True:
        r = S.get("https://data-api.binance.vision/api/v3/klines", params={"symbol": sym + "USDT", "interval": "1h", "startTime": t, "limit": 1000}, timeout=60)
        if r.status_code != 200: print(sym, "HTTP", r.status_code); break
        b = r.json()
        if not b: break
        rows += [[k[0] // 1000, float(k[1]), float(k[2]), float(k[3]), float(k[4])] for k in b]
        t = b[-1][0] + 3600_000
        if len(b) < 1000: break
        time.sleep(0.1)
    if rows:
        json.dump(rows, open(f"experiments/crypto_pourquoi/donnees/spot_{sym}.json", "w"))
        print(sym, len(rows), datetime.datetime.utcfromtimestamp(rows[0][0]), datetime.datetime.utcfromtimestamp(rows[-1][0]))
