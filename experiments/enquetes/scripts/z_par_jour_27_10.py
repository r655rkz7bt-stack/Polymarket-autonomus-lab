"""27/10/2026 (soir) famille 2 : pour chaque stratégie, z des gagnés contre attendus pari par pari, par événement, par jour de règlement (un jour = un tirage).
Repère les « avantages » qui ne sont qu'un facteur commun (le cours du Bitcoin, un soir de matchs). Usage : python experiments/enquetes/scripts/z_par_jour_27_10.py"""
import sys, math
from pathlib import Path
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
from enquete import load_published
from polymarket_agent import enquete as E
from polymarket_agent.reporting import closed_trades
ent = load_published(Path("published_data"))
rows = []
for name, r in ent.items():
    if name == "principal": continue
    t = closed_trades(r)
    if len(t) < 30: continue
    won, exp = E._won_vs_expected(t)
    var = sum((float(x["cost"]) / float(x["shares_bought"])) * (1 - float(x["cost"]) / float(x["shares_bought"])) for x in t if float(x["shares_bought"]) > 0)
    if var <= 0: continue
    zp = (won - exp) / math.sqrt(var)
    days = len({x["closed_at"][:10] for x in t})
    rows.append((name, len(t), days, zp, E._z_by_event(t), E._z_by_day(t)))
rows.sort(key=lambda x: -x[3])
print("| stratégie | paris | jours | z pari | z événement | z jour |")
for n, k, d, a, b, c in rows[:15]: print(f"| {n} | {k} | {d} | {a:+.2f} | {b:+.2f} | {c:+.2f} |")
print("... écart z pari − z jour le plus grand :")
for n, k, d, a, b, c in sorted(rows, key=lambda x: -(x[3] - (x[5] if x[5] != float('inf') else x[3])))[:8]: print(f"| {n} | {k} | {d} | {a:+.2f} | {b:+.2f} | {c:+.2f} |")
