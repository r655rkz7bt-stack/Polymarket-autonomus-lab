import json, time, requests
from datetime import datetime, timedelta, timezone
D = "donnees/xt"
PREFIX = {"elonmusk": "elon-musk-of-tweets", "WhiteHouse": "white-house-of-tweets", "tedcruz": "ted-cruz-of-tweets",
          "ZelenskyyUa": "zelenskyy-of-tweets", "realDonaldTrump": "donald-trump-of-truth-social-posts",
          "NYCMayor": "nyc-mayor-of-tweets", "cz_binance": "cz-binance-of-tweets"}
s = requests.Session()
def get(url, params):
    for k in range(5):
        try:
            return s.get(url, params=params, timeout=40).json()
        except Exception as e:
            time.sleep(2 ** k)
    return {}
out = []
day = datetime(2026, 7, 1, 16, tzinfo=timezone.utc)
while day < datetime(2026, 10, 14, tzinfo=timezone.utc):
    if day.weekday() in (1, 4):
        end = day + timedelta(days=7)
        tag = f"{day:%B}-{day.day}-{end:%B}-{end.day}-{end.year}".lower()
        for h, p in PREFIX.items():
            ev = get("https://gamma-api.polymarket.com/events", {"slug": f"{p}-{tag}"})
            if not ev:
                continue
            ev = ev[0]
            mk = []
            for m in ev.get("markets") or []:
                tok = json.loads(m.get("clobTokenIds") or "[]")
                if not tok:
                    continue
                hist = get("https://clob.polymarket.com/prices-history",
                           {"market": tok[0], "startTs": int(day.timestamp()), "endTs": int(end.timestamp()),
                            "fidelity": 60}).get("history") or []
                mk.append({"titre": m.get("groupItemTitle"), "prix_final": m.get("outcomePrices"), "hist": hist})
                time.sleep(0.12)
            out.append({"compte": h, "debut": day.isoformat(), "fin": end.isoformat(), "slug": ev["slug"],
                        "volume": ev.get("volume"), "marches": mk})
            print(h, tag, len(mk), "marchés", "volume", round(float(ev.get("volume") or 0)), flush=True)
    day += timedelta(days=1)
json.dump(out, open(f"{D}/marches.json", "w"))
