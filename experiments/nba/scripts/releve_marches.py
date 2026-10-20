"""Marchés « vainqueur » NBA réglés (Gamma, series_id 10345) → donnees/marches.json."""
import json, time, re, requests
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
evs, off = [], 0
while True:
    for k in range(5):
        try:
            r = s.get("https://gamma-api.polymarket.com/events", params={"series_id": 10345, "closed": "true", "limit": 100, "offset": off,
                      "order": "startDate", "ascending": "false"}, timeout=40).json(); break
        except Exception:
            time.sleep(2 ** k); r = None
    if not isinstance(r, list) or not r:
        print("arrêt", off, str(r)[:150]); break
    for e in r:
        ms = [m for m in e.get("markets") or [] if m.get("sportsMarketType") == "moneyline"]
        if ms and re.match(r"nba-[a-z]+-[a-z]+-\d{4}-\d{2}-\d{2}$", e["slug"]):
            m = ms[0]
            evs.append({"slug": e["slug"], "title": e["title"], "outcomes": m["outcomes"], "res": m["outcomePrices"], "tok": m["clobTokenIds"],
                        "start": m.get("gameStartTime"), "volume": m.get("volumeNum"), "fee": m.get("feeSchedule") or m.get("feeType")})
    off += 100
    print(off, len(evs), flush=True)
    if off > 6000: break
json.dump(evs, open("donnees/marches.json", "w"))
