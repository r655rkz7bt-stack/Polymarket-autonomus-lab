"""Tous les événements clos et ouverts des étiquettes `cpi` (101701) et `inflation` (702), par /events/keyset -> donnees/evenements_tags.json."""
import json, pathlib, requests
H = {"User-Agent": "curl/8"}
D = pathlib.Path(__file__).resolve().parent.parent / "donnees"
seen = {}
for tag in (101701, 702):
    for closed in ("true", "false"):
        cur = None
        for _ in range(60):
            p = {"tag_id": tag, "closed": closed, "limit": 100, "order": "endDate", "ascending": "false"}
            if cur: p["after_cursor"] = cur
            r = requests.get("https://gamma-api.polymarket.com/events/keyset", headers=H, params=p, timeout=30).json()
            evs = r.get("events") or r.get("data") or []
            for e in evs:
                seen[e["id"]] = e
            cur = r.get("next_cursor")
            if not cur or not evs:
                break
(D / "evenements_tags.json").write_text(json.dumps(list(seen.values())))
print(len(seen))
