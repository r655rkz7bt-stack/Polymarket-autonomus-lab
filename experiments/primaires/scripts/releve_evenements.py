"""Primaires américaines réglées (2026) : événements Gamma avec leurs marchés. Écrit donnees/events.jsonl. À lancer depuis experiments/primaires/."""
import requests, json, re
H = {"User-Agent": "curl/8"}
seen = {}
for slug in ("primaries", "primary", "midterms", "elections", "politics", "us-politics", "senate", "governor", "house"):
    for off in range(0, 3000, 100):
        r = requests.get("https://gamma-api.polymarket.com/events", headers=H, timeout=60,
                         params=dict(tag_slug=slug, closed="true", limit=100, offset=off, order="endDate", ascending="false"))
        try: b = r.json()
        except Exception: break
        if not isinstance(b, list) or not b: break
        for e in b:
            t = e.get("title") or ""
            if re.search(r"Primary|Runoff|primary", t) and "Winner" in t or re.search(r"Primary Winner|Runoff Winner", t):
                seen[e["id"]] = e
        if len(b) < 100: break
    print(slug, len(seen), flush=True)
with open("donnees/events.jsonl", "w") as f:
    for e in seen.values():
        f.write(json.dumps({k: e.get(k) for k in ("id", "title", "endDate", "closedTime", "volume", "markets", "startDate")}) + "\n")
print(len(seen))
