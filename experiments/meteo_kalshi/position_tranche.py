"""Piste n° 62, suite : la foule Polymarket retire-t-elle l'écart METAR (maximum horaire ≤ maximum CLI) ?
Pour chaque vrai achat preneur du OUI (≥ MIN parts) d'une tranche Polymarket entre J−1 12 h et J 20 h UTC, position de la tranche
par rapport à la médiane de la loi Kalshi NON décalée à l'heure de l'échange (k = 0 : la tranche contient la médiane CLI ; −1 :
celle du dessous). Gagnés contre payés (frais weather_fees 0,05 × p × (1 − p) compris) par k et par règle (un pari = premier échange qualifiant par jeton).
Si la foule ignore l'écart : k = 0 trop cher, k = −1 trop bon marché."""
import json, re, sys, datetime as dt
from collections import defaultdict
MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 20
MOIS = list("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())
MN = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}
SER = {"Austin": "KXHIGHAUS", "Miami": "KXHIGHMIA", "Denver": "KXHIGHDEN", "Los Angeles": "KXHIGHLAX"}
K = json.load(open("donnees/kalshi.json")); PE = json.load(open("donnees/poly_events.json")); TR = json.load(open("donnees/echanges.json"))
def poly_bin(t):
    t = (t or "").replace("°F", "").strip()
    if m := re.match(r"^(-?\d+)-(-?\d+)$", t): return int(m.group(1)), int(m.group(2))
    if m := re.match(r"^(-?\d+) or below$", t): return -999, int(m.group(1))
    if m := re.match(r"^(-?\d+) or higher$", t): return int(m.group(1)), 999
QUEUE_MAX = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
def law(ev, T):
    out, tot, queue = defaultdict(float), 0.0, 0.0
    for m in ev["marches"]:
        cs = [c for c in ev["bougies"].get(m["ticker"], []) if c[0] <= T]
        if not cs or cs[-1][1] is None or cs[-1][2] is None: return None
        p = (float(cs[-1][1]) + float(cs[-1][2])) / 2
        st = m["strike_type"]
        cells = ([int(m["floor_strike"]), int(m["cap_strike"])] if st == "between" else
                 [int(m["cap_strike"]) - 1, int(m["cap_strike"]) - 2] if st == "less" else [int(m["floor_strike"]) + 1, int(m["floor_strike"]) + 2])
        for v in cells: out[v] += p / 2
        tot += p
        if st != "between": queue = max(queue, p)
    # 15/11 : une queue (« < 61 ») qui porte une grosse part de la loi n'a pas de forme connue : pas de médiane fiable
    return None if tot < .5 or queue / tot > QUEUE_MAX else {v: q / tot for v, q in out.items()}
def median(l):
    acc = 0
    for v in sorted(l):
        acc += l[v]
        if acc >= .5: return v
res = defaultdict(lambda: [0, 0.0, 0])
for e in PE:
    mt = re.match(r"Highest temperature in (.+?) on (\w+) (\d+)\??$", e["titre"])
    if not mt or mt.group(1) not in SER: continue
    fin = dt.datetime.fromisoformat(e["fin"].replace("Z", "+00:00"))
    d = dt.date(fin.year, MN[mt.group(2)], int(mt.group(3)))
    ke = f"{SER[mt.group(1)]}-{d.strftime('%y')}{MOIS[d.month-1]}{d.day:02d}"
    if ke not in K: continue
    regle = "metar" if "hourly temperature remark" in e["desc"] else "weather.gov"
    t0 = dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp(); a, b = t0 - 12 * 3600, t0 + 20 * 3600
    bins = [(poly_bin(m["tranche"]), m) for m in e["marches"]]
    win = next((bb for bb, m in bins if bb and m["prix"] and float(json.loads(json.dumps(m["prix"]))[0]) > .99), None)
    if win is None: continue
    for bb, m in bins:
        if not bb or bb[0] == -999 or bb[1] == 999: continue
        for ts, sd, oc, pr, sz in sorted(TR.get(m["cond"], [])):
            if not (a <= ts <= b) or sd != "BUY" or oc != "Yes" or float(sz) < MIN or not (.03 <= float(pr) <= .97): continue
            L = law(K[ke], ts)
            if L is None: continue
            med = median(L)
            # position : tranche Polymarket contenant med → 0 ; celle du dessous → −1 ; etc. (tranches de 2 °F)
            k = (bb[0] - (med - ((med - bb[0]) % 2))) // 2 if False else ((bb[0] + 1) // 2 * 2 - (med if med % 2 == 0 else med - 1)) // 2
            pp = float(pr); r = res[(regle, k)]; r[0] += (bb == win); r[1] += pp + 0.05 * pp * (1 - pp); r[2] += 1  # frais weather_fees
            break
for (regle, k), (g, p, n) in sorted(res.items()):
    if n >= 10: print(f"{regle:12s} k={k:+d} : {n:4d} paris, {g:4d} gagnés pour {p:6.1f} payés, rendement {(g - p) / p:+.1%}")
