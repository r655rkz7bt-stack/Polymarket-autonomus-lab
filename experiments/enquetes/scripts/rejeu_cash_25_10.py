"""Rejeu de la trésorerie de chaque journal signé : 1000 − Σ(parts × prix + frais) + Σ(parts réglées × paiement) contre la dernière trésorerie notée par le cycle (25/10/2026)."""
import json, glob, collections, sys
from decimal import Decimal as D
def rejeu(path):
    cash = D(0); held = collections.defaultdict(D); last = None; settled = set(); dbl = 0
    for l in open(path):
        r = json.loads(l); d = r["data"]; t = r["type"]
        if t == "GENESIS": cash = D(d["initial_capital"])
        elif t == "BUY":
            cash -= D(d["shares"]) * D(d["price"]) + D(d["fee"]); held[d["token_id"]] += D(d["shares"])
        elif t == "SELL":
            cash += D(d["shares"]) * D(d["price"]) - D(d.get("fee", 0)); held[d["token_id"]] -= D(d["shares"])
        elif t == "SETTLE":
            tok = d["token_id"]
            if tok in settled: dbl += 1
            settled.add(tok); cash += held[tok] * D(d["payout_per_share"]); held[tok] = D(0)
        elif t == "HEARTBEAT": last = (D(d["cash"]), r["ts"])
    return cash, last, dbl
base = sys.argv[1] if len(sys.argv) > 1 else "published_data/ledger"
bad = []
for p in [f"{base}/ledger.jsonl"] + sorted(glob.glob(f"{base}/fantome/*.jsonl")):
    cash, last, dbl = rejeu(p)
    if last is None: continue
    if abs(cash - last[0]) > D("0.01") or dbl:
        bad.append((p.split("/")[-1], float(cash), float(last[0]), float(cash - last[0]), dbl, last[1][:16]))
print(len(bad), "journaux en désaccord")
for b in bad[:40]: print(b)
