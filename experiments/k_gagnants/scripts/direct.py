"""Relevé en direct : événements OUVERTS « Top N » (k connu par le titre) : somme des meilleurs prix d'achat et de vente OUI contre k.
Σ meilleurs achats (bid) > k : vendre tous les OUI (= acheter tous les NON) rapporte la différence ; Σ meilleurs ventes (ask) < k : acheter tous les OUI."""
import json, re, sys
import requests
H = {"User-Agent": "curl/8"}
evs = {}
for q in ["Finish Top 8", "Top 4 finishers", "Top 4", "Top 24", "Top 10", "Top 5", "Top 3", "Top 20", "Top 6"]:
    for page in (1, 2):
        r = requests.get("https://gamma-api.polymarket.com/public-search", params=dict(q=q, limit_per_type=30, page=page, events_status="active"), headers=H, timeout=40).json()
        for e in r.get("events", []):
            evs[e["id"]] = e
out = []
for e in evs.values():
    t = e["title"]
    m = re.search(r"Top (\d+)", t)
    ms = [x for x in e.get("markets", []) if not x.get("closed") and x.get("clobTokenIds")]
    if not m or len(ms) < 6 or re.search(r"Titled Tuesday|Tweet|tweet|Netflix|views", t):
        continue
    k = int(m.group(1))
    toks = [json.loads(x["clobTokenIds"])[0] for x in ms]
    bid = ask = 0.0; n = 0
    for i in range(0, len(toks), 40):
        books = requests.post("https://clob.polymarket.com/books", json=[{"token_id": t_} for t_ in toks[i:i + 40]], headers=H, timeout=40).json()
        for b in books:
            bb = max((float(x["price"]) for x in b.get("bids", [])), default=0.0)
            aa = min((float(x["price"]) for x in b.get("asks", [])), default=1.0)
            bid += bb; ask += aa; n += 1
    out.append((t[:70], k, len(ms), round(float(e.get("volume") or 0)), round(bid, 3), round(ask, 3)))
for o in sorted(out, key=lambda o: -o[3]):
    print(f"{o[0]:<72} k={o[1]:<3} n={o[2]:<3} vol={o[3]:>9}  Σbid={o[4]:<7} Σask={o[5]:<7}  {'Σbid>k !' if o[4] > o[1] else ''}{'Σask<k !' if o[5] < o[1] else ''}")
