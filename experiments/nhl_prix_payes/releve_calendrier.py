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
d = date(2024, 9, 29)
while d < date(2026, 10, 23):
    r = get(f"https://api-web.nhle.com/v1/schedule/{d}") or {}
    for day in r.get("gameWeek") or []:
        for g in day.get("games") or []:
            games[g["id"]] = {"date": day["date"], "type": g.get("gameType"), "start": g.get("startTimeUTC"),
                              "away": g["awayTeam"]["abbrev"], "home": g["homeTeam"]["abbrev"],
                              "away_names": [g["awayTeam"].get("commonName", {}).get("default"), g["awayTeam"].get("placeName", {}).get("default")],
                              "home_names": [g["homeTeam"].get("commonName", {}).get("default"), g["homeTeam"].get("placeName", {}).get("default")],
                              "sa": g["awayTeam"].get("score"), "sh": g["homeTeam"].get("score"), "state": g.get("gameState")}
    d += timedelta(days=7)
    if date(2025, 6, 25) < d < date(2025, 9, 28):
        d = date(2025, 9, 28)
    if date(2026, 4, 20) < d < date(2026, 10, 1):
        d = date(2026, 10, 1)
print("matchs", len(games), flush=True)
evs, cursor = [], None
while True:
    params = {"tag_slug": "nhl", "closed": "true", "limit": 100}
    if cursor:
        params["after_cursor"] = cursor
    r = get("https://gamma-api.polymarket.com/events/keyset", params)
    if not isinstance(r, dict) or not r.get("events"):
        print("arrêt", str(r)[:200]); break
    evs += [{"id": e["id"], "slug": e["slug"], "title": e["title"], "start": e.get("startTime") or e.get("endDate"),
             "markets": [{"q": m["question"], "type": m.get("sportsMarketType"), "outcomes": m.get("outcomes"), "res": m.get("outcomePrices"),
                          "tok": m.get("clobTokenIds"), "cond": m.get("conditionId"), "start": m.get("gameStartTime")} for m in e.get("markets") or [] if m.get("sportsMarketType") == "moneyline"]}
            for e in r["events"] if e["slug"].startswith("nhl-")]
    cursor = r.get("next_cursor")
    print(len(evs), flush=True)
    if not cursor or len(evs) > 6000: break
print("événements", len(evs), flush=True)
json.dump({"games": games, "events": evs}, open(f"{D}/base.json", "w"))
