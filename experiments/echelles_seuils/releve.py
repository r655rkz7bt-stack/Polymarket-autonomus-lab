"""Relevé du 13/11/2026 : paires incohérentes des échelles de seuils de tous les événements ouverts (Gamma, prix du carnet bestBid/bestAsk).
Coût = vendeur du OUI facile + (1 − acheteur du OUI difficile) + frais ; écart = 1 − coût."""
import json, sys, requests
sys.path.insert(0, "src"); sys.path.insert(0, "experiments/echelles_seuils")
from polymarket_agent.sources.polymarket_gamma import parse_market
from echelles import paires
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
evs, cur = [], None
for _ in range(60):
    p = {"closed": "false", "limit": 500, "order": "volume24hr", "ascending": "false"}
    if cur: p["after_cursor"] = cur
    r = S.get("https://gamma-api.polymarket.com/events/keyset", params=p, timeout=60).json()
    evs += r.get("events") or []
    cur = r.get("next_cursor")
    if not cur or not r.get("events"): break
ms = []
for e in evs:
    if len(e.get("markets") or []) < 2: continue
    for raw in e["markets"]:
        if raw.get("closed") or not raw.get("acceptingOrders", True): continue
        raw = dict(raw, events=[{"id": e["id"], "title": e["title"]}])
        try: ms.append(parse_market(raw))
        except Exception: pass
P = paires(ms)
print("événements", len(evs), "marchés", len(ms), "paires", len(P), flush=True)
rate = lambda m: float((m.fees or {}).get("rate") or 0) if isinstance(getattr(m, "fees", None), dict) else 0.0
bons = []
for f, d, mod in P:
    a, b = f.best_ask, d.best_bid
    if a is None or b is None: continue
    a, b = float(a), float(b)
    fee = 0.0
    try:
        fr = float(f.fees.rate) if hasattr(f.fees, "rate") else 0.0
    except Exception: fr = 0.0
    cost = a + (1 - b)
    edge = 1 - cost
    if edge > 0.005:
        bons.append((round(edge, 4), mod[:90], f.question[:70], a, d.question[:70], b, f.event_id))
bons.sort(reverse=True)
for x in bons[:40]: print(x)
print("paires avec écart > 0,5 point (avant frais) :", len(bons))
json.dump(bons, open("experiments/echelles_seuils/releve_13_11.json", "w"), indent=0, ensure_ascii=False)
