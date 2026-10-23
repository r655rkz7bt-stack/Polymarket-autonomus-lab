"""Sonde : limites de pagination de Gamma (décalage maximal sur /markets et /events) et tri des échanges data-api.
Usage : python experiments/score_exact_poisson/sonde_limites.py"""
import requests

S = requests.Session()
S.headers["User-Agent"] = "polymarket-autonomous-lab"
G = "https://gamma-api.polymarket.com"
for off in (1990, 2000, 2001, 2500):
    r = S.get(f"{G}/markets", params={"sports_market_types": "soccer_exact_score", "closed": "true", "limit": 5, "offset": off}, timeout=60)
    print("/markets offset", off, r.status_code, (len(r.json()) if r.status_code == 200 and isinstance(r.json(), list) else r.text[:120]))
for off in (1900, 2000, 5000, 9000):
    r = S.get(f"{G}/events", params={"series_id": 10310, "closed": "true", "limit": 5, "offset": off}, timeout=60)
    print("/events offset", off, r.status_code, (len(r.json()) if r.status_code == 200 and isinstance(r.json(), list) else r.text[:120]))
# Fenêtre de dates : combien de marchés « score exact » réglés par mois ?
import calendar
for y, m in [(2025, 6), (2025, 10), (2026, 1), (2026, 3), (2026, 5), (2026, 8), (2026, 9), (2026, 10)]:
    last = calendar.monthrange(y, m)[1]
    n, off = 0, 0
    while True:
        d = S.get(f"{G}/markets", params={"sports_market_types": "soccer_exact_score", "closed": "true", "limit": 500, "offset": off,
                  "end_date_min": f"{y}-{m:02d}-01T00:00:00Z", "end_date_max": f"{y}-{m:02d}-{last}T23:59:59Z"}, timeout=90).json()
        if not isinstance(d, list):
            print("erreur", str(d)[:100]); break
        n += len(d); off += 500
        if len(d) < 500 or off >= 2000:
            break
    print(f"score exact {y}-{m:02d} : {n} marchés{' (au moins)' if off >= 2000 and n >= 2000 else ''}")
r = S.get("https://data-api.polymarket.com/trades", params={"eventId": 1159904, "limit": 5}, timeout=60).json()
print("data-api échanges (premiers renvoyés) :", [(t.get("timestamp"), t.get("side"), t.get("price"), t.get("size")) for t in r][:5])
