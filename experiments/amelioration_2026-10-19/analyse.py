"""Bilan de toutes les opérations clôturées des fantômes (AMELIORATION du 19/10/2026).

Usage : python experiments/amelioration_2026-10-19/analyse.py <dossier>
<dossier> contient les journaux *.jsonl (branche data, ledger/ et ledger/fantome/) et ess.sqlite
(backup/essentiel.sqlite.gz décompressé, pour les libellés des marchés). Écrit rows.json dans le
dossier et affiche les tableaux du rapport (familles, prix, horizon, issue, heure, ventes).
"""
import json,glob,os,sqlite3,math,re,sys
from collections import defaultdict
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "src"))
from polymarket_agent.reporting import closed_trades
S=sys.argv[1]
c=sqlite3.connect(f"{S}/ess.sqlite")
Q={m:q for m,q in c.execute("select market_id,question from market_rules")}
def fam(q):
    q=(q or "").lower()
    if "temperature" in q or "°" in q: return "météo"
    if re.search(r"bitcoin|ethereum|solana|xrp|btc|eth |crypto|up or down", q): return "crypto"
    if re.search(r" vs\.? | vs |o/u|spread|map \d|bo\d|win on 20|grand prix|open,|match", q): return "sport"
    if re.search(r"elect|president|senate|house|minister|parliament|trump|vote|governor|nominee|nomination|party|war|ceasefire|strike|resign", q): return "politique"
    return "autre" if q else "inconnu"
bets={}  # token -> record (dedupe)
rows=[]
for f in glob.glob(f"{S}/*.jsonl"):
    n=os.path.basename(f)[:-6]
    if n=="ledger": continue
    E=[json.loads(l) for l in open(f)]
    hz={}
    for e in E:
        if e["type"]=="BUY":
            x=e["data"].get("extra") or {}
            hz.setdefault(e["data"]["token_id"],(x.get("horizon_hours"),e["ts"],x.get("fill_status")))
    for t in closed_trades(E):
        if float(t["cost"])<=0: continue
        h,ts,fs=hz.get(t["token_id"],(None,None,None))
        price=float(t["cost"]-t["fees"])/float(t["shares_bought"]) if float(t["shares_bought"])>0 else None
        r=dict(strat=n,fam=fam(Q.get(t["market_id"])),ret=float(t["pnl"])/float(t["cost"]),pnl=float(t["pnl"]),
               price=price,win=(float(t["payout"])>0.5) if t.get("payout") is not None else None,
               sold=t.get("resolution")=="vendu",h=float(h) if h not in (None,"None") else None,
               hour=int(ts[11:13]) if ts else None,outcome=t["outcome"],token=t["token_id"],patient="patiente" in n)
        rows.append(r)
json.dump(rows,open(f"{S}/rows.json","w"))
def summ(R,label):
    if not R: return
    n=len(R); m=sum(r["ret"] for r in R)/n
    sd=math.sqrt(sum((r["ret"]-m)**2 for r in R)/(n-1)) if n>1 else 0
    S_=[r for r in R if r["win"] is not None and r["price"]]
    W=sum(r["win"] for r in S_); P=sum(r["price"] for r in S_); V=sum(r["price"]*(1-r["price"]) for r in S_)
    z=(W-P)/math.sqrt(V) if V>0 else 0
    print(f"{label:34} n={n:4} rendement moy {m*100:+6.1f}% t={m/(sd/math.sqrt(n)) if sd>0 else 0:+5.2f} | gagnés {W}/{P:.1f} z={z:+.2f} | pnl {sum(r['pnl'] for r in R):+8.1f}")
print("=== par famille (tous fantômes, toutes opérations)")
for f_ in sorted({r["fam"] for r in rows}): summ([r for r in rows if r["fam"]==f_],f_)
print("=== favoris (prix ≥ 0,7) par famille, patients ou non")
for f_ in sorted({r["fam"] for r in rows}):
    for p in (False,True): summ([r for r in rows if r["fam"]==f_ and r["price"] and r["price"]>=0.7 and r["patient"]==p],f"{f_} {'patient' if p else 'immédiat'}")
print("=== par horizon à l'achat (h)")
for lo,hi in [(0,3),(3,6),(6,12),(12,24),(24,72),(72,1e9)]:
    summ([r for r in rows if r["h"] is not None and lo<=r["h"]<hi],f"{lo}-{hi} h")
print("=== par tranche de prix")
for lo,hi in [(0,0.2),(0.2,0.5),(0.5,0.7),(0.7,0.85),(0.85,0.95),(0.95,1)]:
    summ([r for r in rows if r["price"] and lo<=r["price"]<hi],f"prix {lo}-{hi}")
print("=== issue Oui/Non (favoris)")
for o in ("Yes","No"): summ([r for r in rows if r["outcome"]==o and r["price"] and r["price"]>=0.7],o)
print("=== heure UTC d'achat (favoris sport)")
for lo,hi in [(0,6),(6,12),(12,18),(18,24)]:
    summ([r for r in rows if r["hour"] is not None and lo<=r["hour"]<hi and r["fam"]=="sport" and r["price"] and r["price"]>=0.7],f"{lo}-{hi} h UTC")
print("=== vendus avant la fin vs gardés")
summ([r for r in rows if r["sold"]],"vendus"); summ([r for r in rows if not r["sold"]],"gardés jusqu'au règlement")
