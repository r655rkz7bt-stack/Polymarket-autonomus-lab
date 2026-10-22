"""Favoris de sport de toute l'arène, UN pari par jeton (le plus ancien), rendement par unité misée selon le prix payé.
Question : le biais fixe +0,05 (naive_favorite) existe-t-il, et à quel prix ?"""
import glob, json, math, sys
from collections import defaultdict
sys.path.insert(0, "src")
from polymarket_agent.reporting import closed_trades

seen = {}
for p in sorted(glob.glob("published_data/ledger/fantome/nf_sport*.jsonl") + glob.glob("published_data/ledger/fantome/nf_tennis*.jsonl")
                + glob.glob("published_data/ledger/fantome/nf_court*.jsonl") + glob.glob("published_data/ledger/fantome/naive_favorite*.jsonl")):
    if "hors_sport" in p or "football" in p:
        continue
    ents = [json.loads(l) for l in open(p)]
    first = {}
    for e in ents:
        if e["type"] == "BUY":
            d = e["data"]
            first.setdefault(d["token_id"], e)
    for t in closed_trades(ents):
        tok = t["token_id"]
        if t.get("payout") is None:
            continue
        b = first[tok]["data"]
        price = float(b["price"])
        ex = b.get("extra") or {}
        if "est_probability" not in ex or "net_edge" not in ex:
            continue
        if tok not in seen or t["opened_at"] < seen[tok]["ts"]:
            seen[tok] = dict(ts=t["opened_at"], price=price, won=float(t["payout"]) > 0.5,
                             ret=float(t["pnl"]) / float(t["cost"]), est=float(ex["est_probability"]), ev=t["event_id"])
rows = list(seen.values())
print("jetons uniques", len(rows))
bands = [(0.70,0.80),(0.80,0.85),(0.85,0.875),(0.875,0.90),(0.90,0.925),(0.925,0.95),(0.95,1.0)]
print("bande | n | gagnés | attendus(prix) | écart pts | rendement/unité | estimation moy")
for lo, hi in bands:
    v = [r for r in rows if lo <= r["price"] < hi]
    if not v: continue
    w = sum(r["won"] for r in v); e = sum(r["price"] for r in v)
    var = sum(r["price"]*(1-r["price"]) for r in v)
    print(f"{lo:.3f}-{hi:.3f} | {len(v)} | {w} | {e:.1f} | {(w-e)/len(v)*100:+.1f} (z {(w-e)/math.sqrt(var):+.2f}) | {sum(r['ret'] for r in v)/len(v)*100:+.1f}% | {sum(r['est'] for r in v)/len(v):.3f}")
v = rows
print("TOUS", len(v), sum(r["won"] for r in v), round(sum(r["price"] for r in v),1), f"rend {sum(r['ret'] for r in v)/len(v)*100:+.1f}%")
