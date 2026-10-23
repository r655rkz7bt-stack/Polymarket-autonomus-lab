"""Sonde : la data-api accepte-t-elle un filtre par marché (conditionId, liste) et par montant ? Ordre des échanges ?
Usage : python experiments/tennis_sets_coherence/sonde_echanges.py <slug d'événement>"""
import sys
from datetime import datetime, timezone

import requests

S = requests.Session()
S.headers["User-Agent"] = "polymarket-autonomous-lab"
slug = sys.argv[1] if len(sys.argv) > 1 else "atp-atmane-bellucc-2026-10-22"
ev = S.get("https://gamma-api.polymarket.com/events", params={"slug": slug}, timeout=60).json()[0]
print(ev["id"], ev["slug"])
ml = [m for m in ev["markets"] if m.get("sportsMarketType") == "moneyline"][0]
autres = [m for m in ev["markets"] if m.get("sportsMarketType") != "moneyline" and (m.get("volumeNum") or 0) > 0]
print("vainqueur", ml["conditionId"][:12], "volume", ml.get("volumeNum"), "début", ml.get("gameStartTime"))
fmt = lambda ts: datetime.fromtimestamp(ts, timezone.utc).strftime("%m-%d %H:%M")
for label, params in [
    ("événement", {"eventId": ev["id"]}),
    ("vainqueur seul", {"market": ml["conditionId"]}),
    ("vainqueur >= 100 $", {"market": ml["conditionId"], "filterType": "CASH", "filterAmount": 100}),
    ("marchés annexes (liste)", {"market": ",".join(m["conditionId"] for m in autres)}),
]:
    n, oldest, newest = 0, None, None
    for page in range(11):
        try:
            b = S.get("https://data-api.polymarket.com/trades", params=dict(params, limit=1000, offset=1000 * page), timeout=60)
        except requests.RequestException as exc:
            print("   erreur", exc); break
        if b.status_code != 200:
            print("   HTTP", b.status_code, b.text[:100]); break
        b = b.json()
        if not b:
            break
        n += len(b)
        ts = [t["timestamp"] for t in b]
        oldest = min(ts + ([oldest] if oldest else []))
        newest = max(ts + ([newest] if newest else []))
        if len(b) < 1000:
            break
    print(f"{label:28s} échanges {n:6d}  du {fmt(oldest) if oldest else '-'} au {fmt(newest) if newest else '-'}")
