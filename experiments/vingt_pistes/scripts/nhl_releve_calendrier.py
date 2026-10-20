import json, time, requests
from datetime import date, timedelta
D = "donnees/nhl"
s = requests.Session()
def get(url, params=None):
    for k in range(5):
        try:
            return s.get(url, params=params, timeout=40).json()
        except Exception:
            time.sleep(2 ** k)
    return None
games = {}
d = date(2025, 9, 28)
while d < date(2026, 10, 20):
    r = get(f"https://api-web.nhle.com/v1/schedule/{d}") or {}
    for day in r.get("gameWeek") or []:
        for g in day.get("games") or []:
            games[g["id"]] = {"date": day["date"], "type": g.get("gameType"), "start": g.get("startTimeUTC"),
                              "away": g["awayTeam"]["abbrev"], "home": g["homeTeam"]["abbrev"],
                              "away_names": [g["awayTeam"].get("commonName", {}).get("default"), g["awayTeam"].get("placeName", {}).get("default")],
                              "home_names": [g["homeTeam"].get("commonName", {}).get("default"), g["homeTeam"].get("placeName", {}).get("default")],
                              "sa": g["awayTeam"].get("score"), "sh": g["homeTeam"].get("score"), "state": g.get("gameState")}
    d += timedelta(days=7)
    if d > date(2026, 4, 20) and d < date(2026, 10, 1):
        d = date(2026, 10, 1)
print("matchs", len(games), flush=True)
evs, off = [], 0
while True:
    r = get("https://gamma-api.polymarket.com/events", {"tag_slug": "nhl", "closed": "true", "limit": 100, "offset": off})
    if not isinstance(r, list) or not r:
        print("arrêt", off, str(r)[:200]); break
    evs += [{"slug": e["slug"], "title": e["title"], "start": e.get("startTime") or e.get("endDate"),
             "markets": [{"q": m["question"], "type": m.get("sportsMarketType"), "outcomes": m.get("outcomes"), "res": m.get("outcomePrices"),
                          "tok": m.get("clobTokenIds"), "start": m.get("gameStartTime")} for m in e.get("markets") or [] if m.get("sportsMarketType") == "moneyline"]}
            for e in r if e["slug"].startswith("nhl-")]
    off += 100
    if off > 8000: break
print("événements", len(evs), flush=True)
json.dump({"games": games, "events": evs}, open(f"{D}/base.json", "w"))
