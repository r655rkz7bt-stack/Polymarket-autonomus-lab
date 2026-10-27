"""27/10/2026 : découpages du « Under » (et du « Over ») des totaux de kills du LoL, avec profondeur (parts achetables à <= prix + 0,02 dans la fenêtre).
Usage : python analyse2.py [H=1] [VOL_MIN=0] [COTE=Under]"""
import json, sys, math, collections, re
sys.path.insert(0, "experiments/lol_kills/scripts")
import analyse as A
H = float(sys.argv[1]) if len(sys.argv) > 1 else 1
COTE = sys.argv[3] if len(sys.argv) > 3 else "Under"
ms = [json.loads(l) for l in open(A.MARCHES)]
bets = []
for m in ms:
    if m["vol"] < A.VOLMIN or not m["debut"]: continue
    rows = A.charge(m)
    if not rows: continue
    s = A.ts(m["debut"]); t0 = s - int(H * 3600); fin = min(t0 + 3600, s)
    b = A.pari(m, rows, COTE, t0, fin)
    if not b: continue
    j, a = (m["over"], m["under"]) if COTE == "Over" else (m["under"], m["over"])
    b["parts"] = sum(sz for t, as_, sd, p, sz in rows if t0 <= t <= fin and ((as_ == j and sd == "BUY" and p <= b["cout"] + 0.02) or (as_ == a and sd == "SELL" and 1 - p <= b["cout"] + 0.02)))
    lg = re.search(r" - (.*)$", m["titre"]); b["ligue"] = (lg.group(1) if lg else "?")
    b["ligue"] = re.sub(r"\b(Group|Stage|Playoffs?|Regular|Season|Week|Round|Day|Split)\b.*", "", b["ligue"]).strip()[:24]
    bets.append(b)
print(f"{COTE} h={H} vol>={A.VOLMIN}: {len(bets)} paris")
# Un pari par partie (la ligne dont le prix payé est le plus proche de 0,5) : les lignes d'une même partie se gagnent ou se perdent ensemble.
par_partie = {}
for b in bets:
    k = (b["evenement"], b["jeu"])
    if k not in par_partie or abs(b["cout"] - 0.5) < abs(par_partie[k]["cout"] - 0.5):
        par_partie[k] = b
A.rapport(list(par_partie.values()), "UN PAR PARTIE (ligne la plus proche de 0,5)")
A.rapport(bets, "TOUS")
for k in (0, 20, 100, 400):
    A.rapport([b for b in bets if b["parts"] >= k], f"  parts achetables >= {k}")
for g in (1, 2, 3):
    A.rapport([b for b in bets if b["jeu"] == g], f"  partie {g}")
for lo, hi in ((0, 22), (22, 26), (26, 30), (30, 34), (34, 60)):
    A.rapport([b for b in bets if lo <= b["ligne"] < hi], f"  ligne {lo}-{hi}")
for mo in sorted({b["mois"] for b in bets}):
    A.rapport([b for b in bets if b["mois"] == mo], f"  mois {mo}")
c = collections.Counter(b["ligue"] for b in bets)
for lg, n in c.most_common(8):
    A.rapport([b for b in bets if b["ligue"] == lg], f"  ligue {lg}")
