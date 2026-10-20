"""Relevé des événements « mentions » réglés (Gamma, tag mention-markets). Écrit donnees/mn/events.json,
lu par mentions_releve.py. À lancer depuis la racine du dépôt."""
import json
import os
import time

import requests

D = "donnees/mn"
os.makedirs(D, exist_ok=True)
s, events, offset = requests.Session(), [], 0
while offset <= 2000:  # au-delà, Gamma refuse (« offset too large ») : prendre les plus récents
    for k in range(4):
        try:
            page = s.get("https://gamma-api.polymarket.com/events", params={
                "tag_slug": "mention-markets", "closed": "true", "limit": 100, "offset": offset,
                "order": "endDate", "ascending": "false"}, timeout=40).json()
            break
        except Exception:
            time.sleep(2 ** k)
    if not isinstance(page, list) or not page:
        break
    events += page
    offset += 100
json.dump([{"slug": e["slug"], "title": e["title"], "endDate": e.get("endDate"), "startDate": e.get("startDate"),
            "volume": e.get("volume"),
            "markets": [{"t": m.get("groupItemTitle"), "q": m.get("question"), "res": m.get("outcomePrices"),
                         "tok": m.get("clobTokenIds"), "end": m.get("endDate"), "closedTime": m.get("closedTime"),
                         "vol": m.get("volume")} for m in e.get("markets") or []]} for e in events],
          open(f"{D}/events.json", "w"))
print(len(events), "événements")
