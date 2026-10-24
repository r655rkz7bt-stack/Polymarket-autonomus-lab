"""Famille 4 « le filtre ne filtre pas » : chaque achat des 3 derniers jours respecte-t-il la plage de prix de sa stratégie ?
Plages lues dans config/strategies.yaml : min_ask/max_ask (favori : prix du camp acheté), min_price (tweets, mots : prix payé).
Compare le prix du premier niveau consommé ET le prix moyen payé. Usage : python experiments/enquetes/scripts/filtres_prix_24_10.py"""
import sys, yaml, collections
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
from enquete import load_published
E = load_published(Path("published_data"))
cfg = yaml.safe_load(open("config/strategies.yaml"))
latest = max(e["ts"] for r in E.values() for e in r)
since = (datetime.fromisoformat(latest) - timedelta(days=3)).isoformat()
tot = collections.Counter(); bad = collections.defaultdict(list)
for name, rows in E.items():
    if name == "principal": continue
    base = name.rsplit("_v", 1)[0]
    c = cfg.get(base)
    if not c: continue
    P = {k: float(v["value"]) for k, v in (c.get("params") or {}).items() if isinstance(v, dict) and "value" in v}
    lo = P.get("min_ask", P.get("min_price", P.get("min_no_price")))
    hi = P.get("max_ask", P.get("max_price", P.get("max_no_price")))
    if lo is None and hi is None: continue
    for e in rows:
        if e["type"] != "BUY" or e["ts"] < since: continue
        d = e["data"]; price = float(d["price"])
        lv = (d.get("extra") or {}).get("levels") or []
        first = float(lv[0][0]) if lv else price
        tot[base] += 1
        tol = 0.0051  # un cran
        if (lo is not None and min(first, price) < lo - tol) or (hi is not None and max(first, price) > hi + tol):
            bad[base].append((e["ts"][:16], d["outcome"][:20], first, price, lo, hi))
print(f"achats depuis {since[:16]} : {sum(tot.values())} dans {len(tot)} stratégies à plage de prix")
for k, v in sorted(bad.items(), key=lambda kv: -len(kv[1])):
    print(f"  {k}: {len(v)}/{tot[k]} hors plage ; ex. {v[:2]}")
if not bad: print("  aucun achat hors plage")
