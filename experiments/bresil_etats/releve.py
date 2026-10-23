"""Piste n° 16 (etats_comme_avant) : 2e tour de la présidentielle brésilienne (25/10/2026), marchés « 1st place in <État> ».
Compare le prix du 2e tour au gagnant du 1er tour dans l'État (marchés Polymarket réglés du 1er tour). Relevé en direct."""
import requests, json, sys, datetime as dt
H = {"User-Agent": "curl/8"}
def evs(prefix):
    out = {}
    for q in ("Brazil Presidential Election Second Round 1st Place", "second round 1st place Brazil presidential"):
        r = requests.get("https://gamma-api.polymarket.com/public-search", params=dict(q=q, limit_per_type=50), headers=H, timeout=40).json()
        for e in r.get("events", []):
            if e["slug"].startswith(prefix): out[e["slug"]] = e
    return out
second = evs("brazil-presidential-election-second-round-1st-place-in-")
print(len(second), "événements 2e tour")
# compléter par le motif de slug de chaque État vu au 1er tour
first = {}
for sl in second:
    st = sl.split("-in-")[-1]
    r = requests.get("https://gamma-api.polymarket.com/events", params=dict(slug="brazil-presidential-election-first-round-1st-place-in-" + st), headers=H, timeout=40).json()
    if r: first[st] = r[0]
print(len(first), "États au 1er tour")
res = []
for st, e in sorted(first.items()):
    win = [m["question"].split("Will ")[1].split(" win")[0] for m in e["markets"] if json.loads(m["outcomePrices"])[0] == "1"]
    sl = f"brazil-presidential-election-second-round-1st-place-in-{st}"
    s2 = second.get(sl) or (requests.get("https://gamma-api.polymarket.com/events", params=dict(slug=sl), headers=H, timeout=40).json() or [None])[0]
    if not s2: res.append((st, win, None)); continue
    px = {}
    for m in s2["markets"]:
        n = m["question"].split("Will ")[1].split(" win")[0]
        if n.startswith("Candidate") or n.startswith("someone"): continue
        px[n] = (float(json.loads(m["outcomePrices"])[0]), m.get("bestBid"), m.get("bestAsk"), float(m.get("volume") or 0))
    res.append((st, win, px))
for st, win, px in res: print(st, "| 1er tour:", win, "| 2e tour:", {k: round(v[0], 3) for k, v in (px or {}).items()}, "| volume", round(sum(v[3] for v in (px or {}).values())))
json.dump([(st, win, px, dt.datetime.utcnow().isoformat()) for st, win, px in res], open("experiments/bresil_etats/releve_%s.json" % dt.datetime.utcnow().strftime("%Y%m%d_%H%M"), "w"))
