"""Deux camps d'un même match achetés (famille 4, 21/10/2026, soir) : tous portefeuilles, tout l'historique.

Pour chaque portefeuille et chaque marché dont les DEUX jetons ont été achetés (prix >= 0,70 aux deux achats),
chiffre le premier camp, le deuxième camp, et la paire. `python3 deux_camps_21_10.py [dossier published_data]`"""
import json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from polymarket_agent.reporting import closed_trades

root = Path(sys.argv[1] if len(sys.argv) > 1 else "published_data") / "ledger"
rd = lambda p: [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
entries = {p.stem: rd(p) for p in (root / "fantome").glob("*.jsonl")}
entries["principal"] = rd(root / "ledger.jsonl")
rows, tot = [], defaultdict(float)
for name, es in entries.items():
    first_price = {}
    for e in es:
        if e["type"] == "BUY":
            d = e["data"]
            first_price.setdefault((d["market_id"], d["token_id"]), (e["ts"], float(d["price"]), d["outcome"]))
    mk = defaultdict(list)
    for (m, t), v in first_price.items():
        mk[m].append((v[0], t, v[1], v[2]))
    pnl = {t["token_id"]: float(t["pnl"]) for t in closed_trades(es)}
    cost = {t["token_id"]: float(t["cost"]) for t in closed_trades(es)}
    for m, legs in mk.items():
        if len(legs) != 2 or min(l[2] for l in legs) < 0.70 or name.startswith("market_"):
            continue
        legs.sort()
        (a, b) = legs
        if a[1] in pnl and b[1] in pnl:
            rows.append((name, a[3], b[3], pnl[a[1]], pnl[b[1]], cost[a[1]], cost[b[1]]))
n = len(rows)
print("paires closes (hors market_*):", n)
for k, i in (("1er camp", 3), ("2e camp", 4)):
    print(k, "pnl", round(sum(r[i] for r in rows), 1), "mise", round(sum(r[i + 2] for r in rows), 1))
print("paire pnl", round(sum(r[3] + r[4] for r in rows), 1))
# paires distinctes par match (les fantômes jumeaux comptent plusieurs fois)
print("portefeuilles par paire (3 premiers):", sorted(defaultdict(int, {r[1] + '|' + r[2]: 0 for r in rows}))[:3])
print("2e camp gagnant:", sum(1 for r in rows if r[4] > 0), "/", n)
print("1er camp gagnant:", sum(1 for r in rows if r[3] > 0), "/", n)
uniq = {(r[1], r[2]) for r in rows}
print("matchs distincts:", len(uniq))
