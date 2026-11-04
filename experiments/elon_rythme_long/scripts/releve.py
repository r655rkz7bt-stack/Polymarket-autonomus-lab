"""Relevé des posts d'Elon Musk (XTracker, le compteur des marchés Polymarket) -> releves/posts_elon.csv (ts_utc). Lancer depuis la racine."""
import csv, requests
H = {"User-Agent": "curl/8"}
tous = {}
for a, b in (("2025-10-01", "2026-01-15"), ("2026-01-15", "2026-04-01"), ("2026-04-01", "2026-07-15"), ("2026-07-15", "2026-11-05")):
    r = requests.get("https://xtracker.polymarket.com/api/users/elonmusk/posts", params={"startDate": a + "T00:00:00Z", "endDate": b + "T00:00:00Z"}, headers=H, timeout=120).json()
    d = r.get("data") or []
    print(a, b, len(d), d[-1]["createdAt"] if d else None)
    for p in d: tous[p.get("id") or p["createdAt"]] = p["createdAt"]
ts = sorted(set(tous.values()))
with open("experiments/elon_rythme_long/releves/posts_elon.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["ts_utc"]); [w.writerow([t.replace("Z", "+00:00")]) for t in ts]
print(len(ts), ts[0], ts[-1])
