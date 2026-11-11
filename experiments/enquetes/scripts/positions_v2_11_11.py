"""Famille 6 (11/11/2026, 11 h) : positions ouvertes des fantômes v2 relues sur Gamma (marché clos ? réglé ? échéance ?)."""
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import requests

folder = Path(sys.argv[1] if len(sys.argv) > 1 else "published_data/ledger/fantome_v2")
H = {"User-Agent": "curl/8"}
for f in sorted(folder.glob("*.jsonl")):
    opened, shares, cost = {}, defaultdict(Decimal), defaultdict(Decimal)
    for line in f.read_text().splitlines():
        e = json.loads(line)
        d = e.get("data") if isinstance(e.get("data"), dict) else {}
        tok = d.get("token_id")
        if e["type"] == "BUY":
            opened.setdefault(tok, e)
            shares[tok] += Decimal(str(d["shares"]))
            cost[tok] += Decimal(str(d.get("cost") or d.get("amount") or 0))
        elif e["type"] in ("SELL", "SETTLE") and tok in opened:
            if e["type"] == "SETTLE":
                opened.pop(tok)
            else:
                shares[tok] -= Decimal(str(d["shares"]))
                if shares[tok] <= 0:
                    opened.pop(tok)
    for tok, e in opened.items():
        d = e["data"]
        try:
            m = requests.get(f"https://gamma-api.polymarket.com/markets/{d['market_id']}", headers=H, timeout=20).json()
        except Exception as exc:  # noqa: BLE001
            m = {"question": f"erreur {exc}"}
        print(f"{f.stem[:34]:34} {e['ts'][:16]} {d['market_id']} {d['outcome']:4} {float(shares[tok]):7.1f} parts "
              f"fin {str(m.get('endDate'))[:16]} clos={m.get('closed')} uma={m.get('umaResolutionStatus')} "
              f"prix={m.get('outcomePrices')} | {str(m.get('question'))[:60]}")
