"""Événements « # of Truth Social posts » réglés (Gamma public-search) -> donnees/evenements.json."""
import json, requests
H = {"User-Agent": "curl/8"}
ev = {}
for q in ["Truth Social posts", "Donald Trump of Truth Social posts"]:
    for page in range(1, 6):
        d = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=40,
                         params={"q": q, "events_status": "closed", "limit_per_type": 50, "page": page}).json()
        for e in d.get("events", []):
            if "truth-social-posts" in e["slug"] and "trump" in e["slug"]:
                ev[e["id"]] = e
        if not d.get("pagination", {}).get("hasMore"): break
json.dump(sorted(ev.values(), key=lambda e: e["endDate"]), open("experiments/truth_social/donnees/evenements.json", "w"))
print(len(ev))
