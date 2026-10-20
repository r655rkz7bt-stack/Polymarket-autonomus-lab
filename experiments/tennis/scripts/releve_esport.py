"""Piste e-sport : relève des matchs de tennis réglés (Gamma, séries ATP/WTA/ITF), moneyline seulement.
Usage (depuis experiments/tennis) : python3 scripts/releve_marches.py   -> donnees/esport_matchs.json"""
import json, time, requests
from concurrent.futures import ThreadPoolExecutor
SERIES = {"cs2": 10310, "lol": 10311, "dota2": 10309, "val": 10369}
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def page(args):
    sid, off = args
    for k in range(5):
        try:
            r = s.get("https://gamma-api.polymarket.com/events", params={"closed": "true", "limit": 100, "offset": off, "series_id": sid,
                      "order": "endDate", "ascending": "false"}, timeout=60); return r.json()
        except Exception: time.sleep(2 ** k)
    return []
rows = []
for circuit, sid in SERIES.items():
    off, n = 0, 0
    with ThreadPoolExecutor(4) as ex:
        while True:
            batches = list(ex.map(page, [(sid, off + 100 * i) for i in range(4)])); off += 400
            done = False
            for b in batches:
                if not isinstance(b, list): done = True; continue
                for ev in b:
                    for m in ev.get("markets") or []:
                        if m.get("sportsMarketType") not in ("moneyline", "child_moneyline"): continue
                        try: outs = json.loads(m["outcomes"]); prs = json.loads(m["outcomePrices"]); toks = json.loads(m["clobTokenIds"])
                        except Exception: continue
                        if len(outs) != 2 or sorted(prs) != ["0", "1"]: continue
                        fs = m.get("feeSchedule") or {}
                        rows.append({"id": m["id"], "event": ev["id"], "slug": ev["slug"], "circuit": circuit, "type": m.get("sportsMarketType"), "q": m["question"], "outs": outs,
                                     "won": prs.index("1"), "toks": toks, "start": m.get("gameStartTime"), "closed": m.get("closedTime"),
                                     "vol": m.get("volumeNum"), "fee": fs.get("rate") if m.get("feesEnabled") else 0, "title": ev.get("title")})
                        n += 1
                if len(b) < 100: done = True
            print(circuit, off, n, flush=True)
            if done or off > 40000: break
json.dump(rows, open("donnees/esport_matchs.json", "w"))
print("total", len(rows))
