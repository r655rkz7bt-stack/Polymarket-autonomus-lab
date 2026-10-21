"""Cherche des familles d'événements 'classement' réglés (public-search Gamma) : python3 chercher.py "requête" ..."""
import json, sys, requests
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
for q in sys.argv[1:]:
    seen = {}
    for page in range(1, 6):
        r = S.get("https://gamma-api.polymarket.com/public-search", params={"q": q, "limit_per_type": 50, "page": page, "events_status": "closed"}, timeout=40).json()
        for e in r.get("events", []): seen[e["id"]] = e
        if not r.get("pagination", {}).get("hasMore"): break
    print("##", q, len(seen))
    for e in sorted(seen.values(), key=lambda e: e.get("endDate", ""))[:60]:
        print(" ", e["id"], e["slug"][:75], (e.get("endDate") or "")[:10], len(e.get("markets", [])))
