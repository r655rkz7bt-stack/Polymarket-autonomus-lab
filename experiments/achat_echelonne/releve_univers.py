"""Tous les matchs « vainqueur » à deux issues réglés du 22/09 au 19/10/2026, chemin de prix (1 min)
de 3 h avant le début jusqu'au règlement, pour tester l'achat après une baisse sur un univers large."""
import json, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import requests
D = "donnees/ech"
s = requests.Session()
def get(url, params):
    for k in range(5):
        try: return s.get(url, params=params, timeout=40).json()
        except Exception: time.sleep(2 ** k)
    return None
rows = []
day = datetime(2026, 9, 22, tzinfo=timezone.utc)
while day < datetime(2026, 10, 20, tzinfo=timezone.utc):
    off = 0
    while off < 1500:
        page = get("https://gamma-api.polymarket.com/markets", {"sports_market_types": "moneyline", "closed": "true",
                   "end_date_min": day.isoformat(), "end_date_max": (day + timedelta(days=1)).isoformat(), "limit": 100, "offset": off})
        if not isinstance(page, list) or not page: break
        for m in page:
            try:
                outs, res, toks = json.loads(m["outcomes"]), json.loads(m["outcomePrices"]), json.loads(m["clobTokenIds"])
            except Exception: continue
            if len(outs) != 2 or {o.lower() for o in outs} == {"yes", "no"} or res not in (["1", "0"], ["0", "1"]): continue
            if float(m.get("volume") or 0) < 5000 or not m.get("gameStartTime") or not m.get("closedTime"): continue
            rows.append({"slug": m["slug"], "sport": m["slug"].split("-")[0], "debut": m["gameStartTime"].replace(" ", "T").replace("+00", "+00:00"),
                         "ferme": m["closedTime"].replace(" ", "T").replace("+00", "+00:00"), "tok0": toks[0], "gagne0": res == ["1", "0"],
                         "taux": (m.get("feeSchedule") or {}).get("rate", 0.04), "volume": float(m["volume"])})
        off += 100
    print(day.date(), len(rows), flush=True)
    day += timedelta(days=1)
def hist(r):
    st = int(datetime.fromisoformat(r["debut"]).timestamp()) - 3 * 3600
    en = min(int(datetime.fromisoformat(r["ferme"]).timestamp()), st + 3 * 3600 + 8 * 3600)
    h = get("https://clob.polymarket.com/prices-history", {"market": r["tok0"], "startTs": st, "endTs": en, "fidelity": 1}) or {}
    r["chemin"] = [(x["t"], x["p"]) for x in h.get("history") or []]
with ThreadPoolExecutor(4) as ex: list(ex.map(hist, rows))
json.dump(rows, open(f"{D}/univers.json", "w"))
print("fini", len(rows), sum(1 for r in rows if len(r["chemin"]) > 30), flush=True)
