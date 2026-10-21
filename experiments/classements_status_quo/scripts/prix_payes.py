"""Le même test, aux prix réellement payés (vrais échanges des preneurs, data-api), avec les frais du marché.
Décision à J-k avec le prix historique (leader = prix le plus haut) ; achat au premier échange 'Oui' (achat preneur)
dans les 2 h APRÈS la décision ; si aucun échange : pas de pari (compté). Frais : feeSchedule.rate * p * (1-p) par part."""
import json, math, sys, statistics
from collections import defaultdict
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
D = Path("donnees"); (D / "cache").mkdir(exist_ok=True)
ev = json.load(open(D / "events.json")); H = json.load(open(D / "hist.json"))
http = HttpClient(); 
ts = lambda s: int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
from concurrent.futures import ThreadPoolExecutor
def tr(o):
    try: return o["id"], it.fetch_event_trades(http, D / "cache", o["id"])
    except Exception as e: return o["id"], []
with ThreadPoolExecutor(5) as ex: T = dict(ex.map(tr, ev))
def at(hist, t):
    last = None
    for a, p in hist:
        if a > t: break
        last = p
    return last
bets, miss = [], defaultdict(int)
for o in ev:
    wins = [m for m in o["markets"] if m["final"] > 0.99]
    if len(wins) != 1 or not o["end"]: continue
    end = ts(o["end"]); trades = T.get(o["id"], [])
    for k in (30, 14, 7, 3, 1):
        t = end - k * 86400
        if o["start"] and ts(o["start"]) > t: continue
        px = [(at(H.get(m["tok"], []), t), m) for m in o["markets"] if H.get(m["tok"])]
        px = sorted([(p, m) for p, m in px if p is not None], key=lambda x: -x[0])
        if len(px) < 3: continue
        p, m = px[0]
        sel = sorted((x[0], x[3]) for x in trades if x[1] == m["tok"] and x[2] == "BUY" and t <= x[0] <= t + 7200)
        if not sel: miss[(o["fam"], k)] += 1; continue
        cost = sel[0][1]
        rate = float((m.get("fee") or {}).get("rate") or 0)
        c = cost + rate * cost * (1 - cost)
        gain = (1.0 if m["final"] > 0.99 else 0.0) / c - 1
        bets.append({"fam": o["fam"], "k": k, "gain": gain, "cout": cost, "evenement": o["slug"], "mois": o["end"][:7], "win": m["final"] > 0.99, "p_hist": p})
json.dump(bets, open(D / "paris_reels.json", "w"))
print("paris", len(bets), "sans échange", sum(miss.values()))
def show(sel, label):
    if len(sel) < 4: return
    v = it.verdict(sel, min_bets=10)
    n = len(sel); w = sum(b["win"] for b in sel); e = sum(b["cout"] for b in sel)
    print(f"{label:30s} n={n:3d} gagnés={w:3d} attendus(prix payés)={e:5.1f} rendement={v['rendement_moyen']:+.3f} t_ev={v['confiance_evenements']:+.2f} mois+={v['mois_gagnants']} -> {v['verdict']}")
for grp, fams in (("ia", ("ia_1", "ia_2", "ia_3")), ("grande", ("grande_1", "grande_2", "grande_3")), ("app", ("app_gratuite", "app_payante")), ("spotify", ("spotify",)), ("tout", None)):
    for k in (30, 14, 7, 3, 1):
        show([b for b in bets if b["k"] == k and (fams is None or b["fam"] in fams)], f"{grp} J-{k}")
print({f"{a}J-{b}": n for (a, b), n in sorted(miss.items())})
