"""Relevé des posts de @realDonaldTrump (XTracker, sans clé) par tranches de 14 jours -> donnees/trump_posts.json (heures UTC)."""
import json, sys, requests
from datetime import datetime, timedelta, timezone
H = {"User-Agent": "curl/8"}
start = datetime(2026, 1, 1, tzinfo=timezone.utc); end = datetime.now(timezone.utc)
times = set(); t = start
while t < end:
    e = min(t + timedelta(days=14), end)
    r = requests.get("https://xtracker.polymarket.com/api/users/realDonaldTrump/posts",
                     params={"startDate": t.isoformat().replace("+00:00", "Z"), "endDate": e.isoformat().replace("+00:00", "Z")},
                     headers=H, timeout=120)
    d = r.json().get("data") or []
    times.update(p["createdAt"] for p in d)
    print(t.date(), len(d), file=sys.stderr)
    t = e
json.dump(sorted(times), open("experiments/silence_trump/donnees/trump_posts.json", "w"))
print(len(times))
