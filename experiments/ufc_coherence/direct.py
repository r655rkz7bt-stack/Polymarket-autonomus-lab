"""Piste n° 6, relevé EN DIRECT : carnets actuels des combats UFC à venir ; somme des meilleurs vendeurs des jambes des trios A-D
(voir coherence.py). Un trio est un arbitrage si le coût (meilleurs vendeurs + frais) est sous son paiement garanti."""
import json, requests, collections
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
ev = []
off = 0
while True:
    r = S.get("https://gamma-api.polymarket.com/events", params={"series_id": 38, "closed": "false", "limit": 100, "offset": off}, timeout=60).json()
    if not r: break
    ev += r; off += 100
print(len(ev), "événements UFC ouverts")
def book(tok):
    b = S.get("https://clob.polymarket.com/book", params={"token_id": tok}, timeout=30).json()
    asks = sorted((float(a["price"]), float(a["size"])) for a in b.get("asks", []))
    bids = sorted(((float(a["price"]), float(a["size"])) for a in b.get("bids", [])), reverse=True)
    return asks[0] if asks else None, bids[0] if bids else None
def nom(q):
    q = q.lower()
    if q.startswith("will the fight") and "won by ko or tko" in q: return "K"
    if q.startswith("will the fight") and "won by submission" in q: return "S"
    if "win by ko or tko" in q: return "KO"
    return None
rows = []
for e in ev:
    ms = e.get("markets") or []
    K = next((m for m in ms if nom(m["question"]) == "K" and m.get("sportsMarketType") == "ufc_method_of_victory"), None)
    Sm = next((m for m in ms if nom(m["question"]) == "S" and m.get("sportsMarketType") == "ufc_method_of_victory"), None)
    G = next((m for m in ms if m.get("sportsMarketType") == "ufc_go_the_distance"), None)
    ko = [m for m in ms if nom(m["question"]) == "KO"]
    if not (K and Sm and G and len(ko) == 2): continue
    legs = {}
    for key, m in (("K", K), ("S", Sm), ("G", G), ("A", ko[0]), ("B", ko[1])):
        t = json.loads(m["clobTokenIds"]); legs[key] = {"yes": book(t[0]), "no": book(t[1])}
    def ask(k, side): a = legs[k][side][0]; return a[0] if a else None
    def fee(p): return 0.05 * p * (1 - p)
    def trio(spec, payoff):
        prices = [ask(k, s) for k, s in spec]
        if any(p is None for p in prices): return None
        return payoff - sum(prices) - sum(fee(p) for p in prices), sum(prices)
    rows.append((e["title"][:70], trio([("K", "yes"), ("S", "yes"), ("G", "yes")], 1), trio([("K", "no"), ("S", "no"), ("G", "no")], 2),
                 trio([("K", "yes"), ("A", "no"), ("B", "no")], 2), trio([("K", "no"), ("A", "yes"), ("B", "yes")], 1)))
print(len(rows), "combats complets")
for r in rows: print(r[0], [None if x is None else (round(x[0], 3), round(x[1], 3)) for x in r[1:]])
