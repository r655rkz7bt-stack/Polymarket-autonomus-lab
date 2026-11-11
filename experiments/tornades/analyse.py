"""11/11/2026 : piste n° 21. Relit test_passe.json, refait la loi avec le compte SPC réduit (rapports tardifs : regard vers le futur),
log-score contre le marché et achats aux vrais prix (premier achat preneur dans les 6 h, un pari par tranche au premier signal).
Usage : .venv/bin/python experiments/tornades/analyse.py"""
import csv, json, math, datetime as dt, collections, statistics
R = json.load(open("experiments/tornades/test_passe.json"))
spc = json.load(open("experiments/tornades/spc_jours.json"))
seen, daily = set(), collections.Counter()
for r in csv.DictReader(open("experiments/tornades/donnees/actual.csv")):
    if r["sg"] == "2" or (r["yr"], r["om"]) in seen:
        continue
    seen.add((r["yr"], r["om"])); daily[(int(r["yr"]), int(r["mo"]), int(r["dy"]))] += 1
import re
def bracket(label):
    s = label.replace("–", "-").replace(" ", "").lower()
    if m := re.match(r"(?:<|under)(\d+)$", s): return (0, int(m.group(1)) - 1)
    if m := re.match(r"(\d+)(?:\+|ormore)$", s): return (int(m.group(1)), 10**6)
    if m := re.match(r"(\d+)-(\d+)$", s): return (int(m.group(1)), int(m.group(2)))
def ndays(y, mo): return ((dt.date(y + (mo == 12), mo % 12 + 1, 1)) - dt.date(y, mo, 1)).days
nb = collections.Counter(r["mois"] for r in R if r["jour"] == 5)
def p_of(r, scale):
    y, mo = map(int, r["mois"].split("-")); d = r["jour"]; br = bracket(r["tranche"])
    so = scale * sum(spc.get(dt.date(y, mo, k).isoformat(), 0) for k in range(1, d - 1))
    tot = [so + sum(daily[(yy, mo, k)] for k in range(d - 1, ndays(y, mo) + 1)) for yy in range(1995, 2025)]
    k = sum(br[0] <= round(t) <= br[1] for t in tot)
    return (k + 0.5) / (len(tot) + 0.5 * nb[r["mois"]])
FEE = 0.05  # weather_fees (prudence : appliqué même aux marchés anciens sans frais)
import os
JOUR_MIN = int(os.environ.get("JOUR_MIN", "1"))  # 11/11 : paris seulement à partir de ce jour du mois
for scale in (1.0, 0.93, 0.85):
    ll = collections.defaultdict(lambda: [0, 0, 0])
    for r in R:
        if r["prix"] is None: continue
        p = min(max(p_of(r, scale), 0.01), 0.99); q = min(max(r["prix"], 0.01), 0.99); y = r["gagne"]
        a = ll[r["jour"]]; a[0] += -(y * math.log(p) + (1 - y) * math.log(1 - p)); a[1] += -(y * math.log(q) + (1 - y) * math.log(1 - q)); a[2] += 1
    print(f"échelle {scale} : log-loss modèle/marché par jour", {d: (round(v[0] / v[2], 3), round(v[1] / v[2], 3)) for d, v in sorted(ll.items())})
    for seuil in (0.03, 0.05, 0.10):
        bets = {}
        for r in sorted((r for r in R if r["jour"] >= JOUR_MIN), key=lambda r: r["jour"]):
            key = (r["mois"], r["tranche"])
            if key in bets: continue
            p = p_of(r, scale)
            for side, prob, tr in (("OUI", p, r["achat_oui"]), ("NON", 1 - p, r["achat_non"])):
                if tr is None: continue
                px = tr[0]; cost = px + FEE * px * (1 - px)
                if 0.03 <= px <= 0.97 and prob - cost > seuil:
                    pay = r["gagne"] if side == "OUI" else 1 - r["gagne"]
                    bets[key] = (side, px, cost, prob, pay, r["jour"], r["mois"], tr[1]); break
        if not bets: continue
        rets = [b[4] / b[2] - 1 for b in bets.values()]
        months = collections.defaultdict(list)
        for k, b in bets.items(): months[b[6]].append(b[4] / b[2] - 1)
        mm = [statistics.mean(v) for v in months.values()]
        t = statistics.mean(mm) / (statistics.stdev(mm) / math.sqrt(len(mm))) if len(mm) > 2 and statistics.stdev(mm) > 0 else float("nan")
        won = sum(b[4] for b in bets.values()); exp_ = sum(b[3] for b in bets.values()); paid = sum(b[1] for b in bets.values())
        print(f"   seuil {seuil:.2f} : {len(bets)} paris, gagnés {won:.0f} pour {exp_:.2f} attendus (modèle) et {paid:.2f} payés, rendement moyen {statistics.mean(rets):+.1%}, "
              f"mois gagnants {sum(x > 0 for x in mm)}/{len(mm)}, t par mois {t:.2f}, parts médianes {statistics.median(b[7] for b in bets.values()):.0f}")
    if scale == 0.93:
        for k, b in sorted(bets.items()): print("      ", k, b[:7])
