"""Relevé des événements réglés de l'étiquette global-temp (832) : marchés, règlement, prix horaires (CLOB). /events/keyset, jamais offset."""
import json, sys, time, requests
H = {"User-Agent": "curl/8"}
out, cur = [], None
while True:
    p = dict(tag_id=832, closed="true", limit=100, order="endDate", ascending="false")
    if cur: p["after_cursor"] = cur
    r = requests.get("https://gamma-api.polymarket.com/events/keyset", params=p, headers=H, timeout=60).json()
    evs = r.get("events") if isinstance(r, dict) else r
    if not evs: break
    out += evs
    cur = r.get("next_cursor") if isinstance(r, dict) else None
    if not cur: break
json.dump(out, open(sys.argv[1], "w"))
print(len(out))
for e in out: print(e["id"], (e.get("endDate") or "")[:10], e["title"][:80], len(e.get("markets") or []))
