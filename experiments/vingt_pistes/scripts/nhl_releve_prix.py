import json, time, requests, re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
D = "donnees/nhl"
b = json.load(open(f"{D}/base.json"))
games = [g for g in b["games"].values() if g["type"] in (2, 3) and g["state"] in ("OFF", "FINAL") and g["sa"] is not None]
played = {}
for g in games:
    for t in (g["away"], g["home"]):
        played.setdefault(t, set()).add(g["date"])
def low(x): return (x or "").lower()
evs = [e for e in b["events"] if e["markets"] and re.match(r"nhl-[a-z]+-[a-z]+-\d{4}-\d{2}-\d{2}$", e["slug"])]
by_date = {}
for e in evs:
    by_date.setdefault(e["slug"][-10:], []).append(e)
rows = []
for g in games:
    cands = by_date.get(g["date"], [])
    hit = None
    for e in cands:
        m = e["markets"][0]
        outs = [low(o) for o in json.loads(m["outcomes"])]
        def same(o, names): return any(n and (low(n) in o or o in low(n)) for n in names)
        if len(outs) == 2 and same(outs[0], g["away_names"]) and same(outs[1], g["home_names"]):
            hit = (e, m, 0)
        elif len(outs) == 2 and same(outs[1], g["away_names"]) and same(outs[0], g["home_names"]):
            hit = (e, m, 1)
    if not hit: continue
    e, m, flip = hit
    prev = (datetime.fromisoformat(g["date"]) - timedelta(days=1)).date().isoformat()
    rows.append({"date": g["date"], "start": g["start"], "away": g["away"], "home": g["home"],
                 "away_win": g["sa"] > g["sh"], "b2b_away": prev in played[g["away"]], "b2b_home": prev in played[g["home"]],
                 "tok": json.loads(m["tok"])[flip], "slug": e["slug"], "res": m["res"], "flip": flip})
print("matchs rattachés", len(rows), "sur", len(games), flush=True)
s = requests.Session()
def hist(r):
    st = int(datetime.fromisoformat(r["start"].replace("Z", "+00:00")).timestamp())
    for k in range(4):
        try:
            h = s.get("https://clob.polymarket.com/prices-history", params={"market": r["tok"], "startTs": st - 12 * 3600, "endTs": st, "fidelity": 10}, timeout=40).json()
            r["hist"] = h.get("history") or []; return
        except Exception: time.sleep(2 ** k)
    r["hist"] = []
with ThreadPoolExecutor(4) as ex: list(ex.map(hist, rows))
json.dump(rows, open(f"{D}/rows.json", "w"))
print("fini", sum(1 for r in rows if r["hist"]), flush=True)
