"""Relève les événements 'classement' réglés (Gamma public-search) et le prix horaire de chaque 'Oui' (CLOB).
python3 releve.py  -> donnees/events.json, donnees/hist.json (jeton -> [[ts, prix], ...])"""
import json, re, time, sys
import requests
from concurrent.futures import ThreadPoolExecutor
D = "donnees"
FAMILLES = {
    "ia_1": r"^which-company-has-(the-)?best-ai-model-(end-of|on)-",
    "ia_2": r"^which-company-has-(the-)?second-best-ai-model",
    "ia_3": r"^which-company-has-(the-)?third-best-ai-model",
    "grande_1": r"^largest-company-end-of-",
    "grande_2": r"^2nd-largest-company-end-of-",
    "grande_3": r"^3rd-largest-company-end-of-",
    "app_gratuite": r"^1-free-app-in-the-us-apple-app-store-on-",
    "app_payante": r"^1-paid-app-in-the-us-apple-app-store-on-",
    "spotify": r"^top-spotify-artist-(in-|this-month)",
}
QUERIES = ["best AI model end of", "second best AI model", "third best AI model", "largest company end of", "2nd largest company end of",
           "3rd largest company end of", "1 free app in the US Apple App Store", "1 paid app in the US Apple App Store", "top spotify artist"]
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
def get(url, **p):
    for k in range(4):
        try:
            r = S.get(url, params=p, timeout=40)
            if r.status_code == 200: return r.json()
        except Exception: pass
        time.sleep(1 + k)
    return None
import os
found = {}
for q in ([] if os.path.exists(f"{D}/events.json") else QUERIES):
    for page in range(1, 9):
        r = get("https://gamma-api.polymarket.com/public-search", q=q, limit_per_type=50, page=page, events_status="closed")
        if not r: break
        for e in r.get("events", []): found[e["id"]] = e
        if not r.get("pagination", {}).get("hasMore"): break
print("événements trouvés", len(found), flush=True)
keep = {}
for e in found.values():
    for fam, rx in FAMILLES.items():
        if re.match(rx, e["slug"]) and e.get("closed"):
            keep[e["id"]] = (fam, e["id"])
def full(item):
    fam, eid = item
    e = get(f"https://gamma-api.polymarket.com/events/{eid}")
    return fam, e
with ThreadPoolExecutor(6) as ex: evs = list(ex.map(full, keep.values()))
out = []
for fam, e in evs:
    if not e: continue
    ms = []
    for m in e["markets"]:
        try:
            outs = json.loads(m["outcomes"]); pr = [float(x) for x in json.loads(m["outcomePrices"])]; tok = json.loads(m["clobTokenIds"])
        except Exception: continue
        if outs[0] != "Yes": continue
        ms.append({"id": m["id"], "name": m.get("groupItemTitle") or m["question"], "tok": tok[0], "final": pr[0], "vol": m.get("volumeNum") or 0,
                   "fee": m.get("feeSchedule"), "closedTime": m.get("closedTime"), "uma": m.get("umaResolutionStatus")})
    out.append({"fam": fam, "id": e["id"], "slug": e["slug"], "start": e.get("startDate"), "end": e.get("endDate"), "markets": ms})
if os.path.exists(f"{D}/events.json"): out = json.load(open(f"{D}/events.json"))
else: json.dump(out, open(f"{D}/events.json", "w"))
print("gardés", len(out), {f: sum(1 for o in out if o["fam"] == f) for f in FAMILLES}, flush=True)
toks = [(o["end"], m["tok"], o["start"]) for o in out for m in o["markets"] if m["vol"] > 500]
def hist(t):
    end, tok, start = t
    for fid in (60, 240, 720):  # les marchés clos refusent les pas fins : on prend le plus fin qui répond
        h = get("https://clob.polymarket.com/prices-history", market=tok, interval="max", fidelity=fid)
        if (h or {}).get("history"): return tok, h["history"]
    return tok, []
with ThreadPoolExecutor(6) as ex: res = list(ex.map(hist, toks))
json.dump({t: [[p["t"], p["p"]] for p in h] for t, h in res}, open(f"{D}/hist.json", "w"))
print("historiques", len(res), "vides", sum(1 for _, h in res if not h))
