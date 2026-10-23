import json, bisect, collections
R = json.load(open("experiments/toucher_avant_fin/donnees/appar_prix.json"))
gaps = []; per = collections.defaultdict(list)
for r in R:
    hr, ha = r["hr"], r["ha"]
    if not hr or not ha: continue
    ta = [x[0] for x in ha]
    for t, pr in hr:
        i = bisect.bisect_right(ta, t) - 1
        if i < 0 or t - ta[i] > 1200: continue
        pa = ha[i][1]
        cost = pr + (1 - pa) if r["up"] else pr + pa
        gaps.append(1 - cost)
        per[(r["asset"], r["day"], r["strike"], r["up"])].append((1 - cost, t, pr, pa))
n = len(gaps)
print("points comparés :", n, " couples :", len(per))
for th in (0.0, 0.01, 0.02, 0.03, 0.05, 0.10):
    c = sum(1 for g in gaps if g > th)
    k = sum(1 for v in per.values() if max(x[0] for x in v) > th)
    print(f"marge au milieu > {th:.2f} : {c} points ({c/n:.2%}), {k} couples")
best = sorted(((max(v)[0], k, max(v)) for k, v in per.items()), reverse=True)[:8]
for g, k, x in best: print(round(g, 3), k, "touche", x[2], "au-dessus", x[3])
print("--- calibration du prix « touche » (OUI) à 12 h UTC, jours Bitcoin/Ethereum/Solana, marchés ↑ et ↓ ---")
bins = collections.defaultdict(list)
for r in R:
    hr = r["hr"]
    if not hr: continue
    tt = [x[0] for x in hr]
    import datetime as dt
    t0 = int((dt.datetime.fromisoformat(r["day"]).replace(tzinfo=dt.timezone.utc) + dt.timedelta(hours=12)).timestamp())
    i = bisect.bisect_right(tt, t0) - 1
    if i < 0 or t0 - tt[i] > 3600: continue
    p = hr[i][1]; won = int(r["reach"]["final"] == 1.0)
    b = "0,02-0,05" if p < .05 else "0,05-0,15" if p < .15 else "0,15-0,40" if p < .4 else "0,40-0,70" if p < .7 else "≥ 0,70"
    if p >= .02: bins[b].append((p, won))
for b, v in sorted(bins.items()):
    print(f"{b} : {len(v)} marchés, prix moyen {sum(p for p,_ in v)/len(v):.3f}, touchés {sum(w for _,w in v)/len(v):.3f}")
import sys; sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
print("--- NON de « touche » (OUI 0,02-0,40) à 12 h UTC (8 h ET) : verdict ---")
for lo, hi in ((0.02, 0.15), (0.05, 0.40), (0.02, 0.40)):
    for sp in (0.01, 0.02):
        bets = []
        for r in R:
            hr = r["hr"]
            if not hr: continue
            tt = [x[0] for x in hr]
            t0 = int((dt.datetime.fromisoformat(r["day"]).replace(tzinfo=dt.timezone.utc) + dt.timedelta(hours=12)).timestamp())
            i = bisect.bisect_right(tt, t0) - 1
            if i < 0 or t0 - tt[i] > 3600: continue
            p = hr[i][1]
            if not lo <= p < hi: continue
            cost = 1 - p + sp  # les marchés « touche » ne portent pas de frais (feeSchedule absent) : à vérifier
            bets.append(dict(gain=((1 - int(r["reach"]["final"] == 1.0)) - cost) / cost, evenement=r["day"], mois=r["day"][:7], cout=cost))
        v = verdict(bets)
        print(f"OUI {lo:.2f}-{hi:.2f}, écart {sp}: {v['paris']} paris, rendement {v.get('rendement_moyen')}, t jours {v.get('confiance_evenements')}, z prix {v.get('z_prix')}, mois {v.get('mois_gagnants')}, {v['verdict']}")
