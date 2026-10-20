import json, time, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
D = "donnees/nhl"
s = requests.Session()
def get(url, params=None):
    for k in range(5):
        try: return s.get(url, params=params, timeout=40).json()
        except Exception: time.sleep(2 ** k)
    return None
rows = json.load(open(f"{D}/rows.json"))
slugs = {r["slug"]: r for r in rows}
tot = []
for slug, r in slugs.items():
    pass
def ev(slug):
    e = get("https://gamma-api.polymarket.com/events", {"slug": slug})
    if not e: return []
    out = []
    for m in e[0].get("markets") or []:
        if m.get("sportsMarketType") == "totals" and m.get("line") is not None:
            out.append({"slug": slug, "line": float(m["line"]), "outcomes": m.get("outcomes"), "res": m.get("outcomePrices"),
                        "tok": json.loads(m.get("clobTokenIds") or "[]"), "start": slugs[slug]["start"]})
    return out
with ThreadPoolExecutor(4) as ex:
    for o in ex.map(ev, list(slugs)): tot += o
print("marchés de total", len(tot), flush=True)
def hist(t):
    st = int(datetime.fromisoformat(t["start"].replace("Z", "+00:00")).timestamp())
    h = get("https://clob.polymarket.com/prices-history", {"market": t["tok"][0], "startTs": st - 12 * 3600, "endTs": st, "fidelity": 10}) or {}
    t["hist"] = h.get("history") or []
with ThreadPoolExecutor(4) as ex: list(ex.map(hist, tot))
json.dump(tot, open(f"{D}/totals.json", "w"))
print("fini", sum(1 for t in tot if t["hist"]), flush=True)
