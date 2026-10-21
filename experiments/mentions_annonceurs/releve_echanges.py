"""Relève les vrais échanges (data-api) des événements « announcers » / « anyone » : identifiants
Gamma par slug, puis échanges des preneurs (idea_test.fetch_event_trades, cache gzip).
Écrit donnees/mn/echanges/*.json.gz et donnees/mn/ids.json."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient  # noqa: E402
from polymarket_agent.idea_test import fetch_event_trades  # noqa: E402

D = Path("donnees/mn")
slugs = sorted({r["ev"] for r in json.load(open(D / "annonceurs.json"))})
s = requests.Session()
s.headers["User-Agent"] = "curl/8"


def get_id(slug):
    for _ in range(3):
        try:
            j = s.get("https://gamma-api.polymarket.com/events", params={"slug": slug, "closed": "true"}, timeout=30).json()
            return slug, (j[0]["id"] if j else None)
        except Exception:
            pass
    return slug, None


ids = dict(ThreadPoolExecutor(6).map(get_id, slugs))
json.dump(ids, open(D / "ids.json", "w"))
print("ids", sum(1 for v in ids.values() if v), "/", len(ids), flush=True)
http = HttpClient(timeout=40)


def trades(item):
    slug, eid = item
    if not eid:
        return slug, -1
    return slug, len(fetch_event_trades(http, D / "echanges", eid))


done = list(ThreadPoolExecutor(4).map(trades, ids.items()))
print("échanges par événement : médiane", sorted(n for _, n in done)[len(done) // 2], "max", max(n for _, n in done),
      "vides", sum(1 for _, n in done if n <= 0), flush=True)
