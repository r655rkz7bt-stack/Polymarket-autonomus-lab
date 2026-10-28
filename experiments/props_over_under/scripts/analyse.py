"""Over/Under de sport (props de joueurs, totaux, mi-temps…) : l'Over est-il trop cher ? Prix payés = premier échange réel d'un preneur qui ACHÈTE le côté
dans la fenêtre [coup d'envoi − h, coup d'envoi − h + 1 h] (avant le match seulement), taille ≥ SMIN parts, frais selon le barème du marché.
Agrégats par événement (les paris d'un même match sont liés). Usage : python analyse.py [h1,h2,...]   (heures avant le coup d'envoi)"""
import json, sys, math, collections, statistics as st, bisect
HS = [float(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "1,3,6,12").split(",")]
SMIN = 5
M = [json.loads(l) for l in open("experiments/props_over_under/donnees/ou_marches.jsonl")]
print(len(M), "marchés,", sum(1 for m in M if m["trades"]), "avec échanges")
def fee(m, p):
    f = m.get("fee") or {}
    r = f.get("rate", 0.03) if f else 0.0
    return r * p * (1 - p) if f else 0.0
def prix(m, tr, ts, T, side):
    a, b = bisect.bisect_left(ts, T), bisect.bisect_left(ts, T + 3600)
    for t in tr[a:b]:
        if t[2] == "BUY" and t[1] == m[side] and t[4] >= SMIN: return t[3], t[4]
rows = []
for m in M:
    if not m["trades"]: continue
    tr = sorted(m["trades"]); ts = [t[0] for t in tr]
    for h in HS:
        T = m["debut"] - h * 3600
        for side in ("over", "under"):
            r = prix(m, tr, ts, T, side)
            if r:
                px, sz = r; win = m["gagnant"] == side.capitalize()
                rows.append(dict(sport=m["sport"], type=m["type"], ev=m["ev"], h=h, side=side, px=px, sz=sz, win=win, g=(1.0 if win else 0.0) - px - fee(m, px), cid=m["cid"]))
print(len(rows), "achats simulés")
def aff(nom, R):
    if len(R) < 30: return
    ev = collections.defaultdict(float)
    for r in R: ev[r["ev"]] += r["g"]
    evs = list(ev.values()); sd = st.pstdev(evs) or 1
    mise = sum(r["px"] for r in R); tot = sum(r["g"] for r in R)
    print(f"{nom:46s} {len(R):6d} paris / {len(ev):5d} événements  gagnés {sum(r['win'] for r in R):6d} pour {sum(r['px'] for r in R):8.1f}  rendement {tot/mise:+7.2%}  t/événement {st.mean(evs)/(sd/math.sqrt(len(evs))):+.2f}")
for h in HS:
    print(f"\n=== {h:g} h avant le coup d'envoi")
    for side in ("over", "under"):
        aff(f"tous, {side}", [r for r in rows if r["h"] == h and r["side"] == side])
    for sport in sorted({r["sport"] for r in rows}):
        for side in ("over", "under"):
            aff(f"{sport}, {side}", [r for r in rows if r["h"] == h and r["side"] == side and r["sport"] == sport])
    for ty in sorted({r["type"] for r in rows}):
        for side in ("over", "under"):
            aff(f"type {ty}, {side}", [r for r in rows if r["h"] == h and r["side"] == side and r["type"] == ty])
