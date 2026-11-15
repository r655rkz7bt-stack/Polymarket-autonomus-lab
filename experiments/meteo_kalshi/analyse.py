"""Piste n° 62 : Kalshi (maximum du jour, rapport climatologique NWS) comme prévision des tranches Polymarket (maximum des relevés
METAR horaires, ou Wunderground / weather.gov avant le 20/10), mêmes stations (KAUS, KMIA, KDEN, KLAX), depuis le 15/09/2026.
1. Loi Kalshi sur la grille des degrés entiers à l'instant T (milieu acheteur/vendeur de la dernière bougie finie, normalisé ;
   tranche 75-76 partagée moitié-moitié ; queues sur 2 degrés).
2. Écart de mesure s = valeur CLI − valeur Polymarket (≥ 0 attendu : le maximum horaire manque les pointes entre deux relevés),
   loi de s apprise par EM sur les événements réglés AVANT l'événement jugé (aucun regard vers le futur), départ uniforme 0-3.
3. Chance Kalshi d'une tranche Polymarket = somme sur v de q(v) × P(v − s dans la tranche).
4. Contre le prix Polymarket (dernier point prices-history ≤ T) : log-score, puis achats simulés si chance − (prix + écart) ≥ seuil.
Usage : analyse.py [heure UTC de décision relative au jour J, ex. -4 = J-1 20 h ; 14 = J 14 h] [seuil] [écart]"""
import json, math, re, sys, bisect, datetime as dt
from collections import defaultdict
H_DEC = float(sys.argv[1]) if len(sys.argv) > 1 else 14
SEUIL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.08
ECART = float(sys.argv[3]) if len(sys.argv) > 3 else 0.02
MOIS = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}
K = json.load(open("donnees/kalshi.json")); PE = json.load(open("donnees/poly_events.json")); PX = json.load(open("donnees/poly_prix.json"))
SER = {"Austin": "KXHIGHAUS", "Miami": "KXHIGHMIA", "Denver": "KXHIGHDEN", "Los Angeles": "KXHIGHLAX"}
MN = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}

def kdate(e):
    m = re.search(r"-(\d\d)([A-Z]{3})(\d\d)$", e); return dt.date(2000 + int(m.group(1)), MOIS[m.group(2)], int(m.group(3)))

def poly_bin(t):
    t = t.replace("°F", "").strip()
    if m := re.match(r"^(-?\d+)-(-?\d+)$", t): return int(m.group(1)), int(m.group(2))
    if m := re.match(r"^(-?\d+) or below$", t): return -999, int(m.group(1))
    if m := re.match(r"^(-?\d+) or higher$", t): return int(m.group(1)), 999
    return None

def kalshi_law(ev, T):
    """{degré entier: proba} de la valeur CLI à l'instant T, ou None."""
    law, tot = defaultdict(float), 0.0
    for m in ev["marches"]:
        cs = [c for c in ev["bougies"].get(m["ticker"], []) if c[0] <= T]
        if not cs: return None
        b, a = cs[-1][1], cs[-1][2]
        if b is None or a is None: return None
        p = (float(b) + float(a)) / 2
        if m["strike_type"] == "between": cells = [int(m["floor_strike"]), int(m["cap_strike"])]
        elif m["strike_type"] == "less": c = int(m["cap_strike"]); cells = [c - 1, c - 2]
        elif m["strike_type"] == "greater": f = int(m["floor_strike"]); cells = [f + 1, f + 2]
        else: return None
        for v in cells: law[v] += p / len(cells)
        tot += p
    if tot <= 0.5: return None
    return {v: q / tot for v, q in law.items()}

# appariement Polymarket ↔ Kalshi
cas = []
for e in PE:
    mt = re.match(r"Highest temperature in (.+?) on (\w+) (\d+)\??$", e["titre"])
    if not mt or mt.group(1) not in SER: continue
    fin = dt.datetime.fromisoformat(e["fin"].replace("Z", "+00:00"))
    d = dt.date(fin.year, MN[mt.group(2)], int(mt.group(3)))
    if d > fin.date() + dt.timedelta(days=2): d = d.replace(year=d.year - 1)
    ke = f"{SER[mt.group(1)]}-{d.strftime('%y')}{list(MOIS)[d.month-1]}{d.day:02d}"
    if ke not in K: continue
    bins, win = [], None
    for m in e["marches"]:
        b = poly_bin(m["tranche"] or "")
        if b is None or not m["jetons"]: continue
        pr = [float(x) for x in m["prix"]] if m["prix"] else []
        bins.append((b, m["jetons"][0]))
        if pr and pr[0] > 0.99: win = b
    cli = next((float(m["expiration_value"]) for m in K[ke]["marches"] if re.fullmatch(r"-?\d+(\.\d+)?", str(m.get("expiration_value") or ""))), None)
    if win is None or cli is None: continue
    regle = "metar" if "hourly temperature remark" in e["desc"] else ("wunderground" if "wunderground" in e["desc"].lower() else "weather.gov")
    T = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() + H_DEC * 3600)
    cas.append({"ev": e["id"], "ville": mt.group(1), "date": d, "bins": bins, "win": win, "cli": int(round(cli)), "regle": regle, "T": T, "k": K[ke]})
cas.sort(key=lambda c: c["date"])
print(f"{len(cas)} événements appariés ({min(c['date'] for c in cas)} → {max(c['date'] for c in cas)}) ; décision à J {H_DEC:+.0f} h UTC")
# écart de mesure observé : la valeur CLI tombe-t-elle dans la tranche gagnante ? sinon de combien au-dessus ?
from collections import Counter
obs = Counter()
for c in cas:
    lo, hi = c["win"]; v = c["cli"]
    obs[(c["regle"], 0 if lo <= v <= hi else (v - hi if v > hi else v - lo))] += 1
print("CLI − tranche gagnante Polymarket (0 = dedans) :", sorted(obs.items()))

def em(train, iters=30):
    pi = [0.25] * 4
    for _ in range(iters):
        acc = [1e-3] * 4
        for c in train:
            lo, hi = c["win"]; w = [pi[s] * (lo <= c["cli"] - s <= hi) for s in range(4)]; z = sum(w)
            if z > 0:
                for s in range(4): acc[s] += w[s] / z
        t = sum(acc); pi = [a / t for a in acc]
    return pi

rows = []
for i, c in enumerate(cas):
    train = [x for x in cas[:i] if x["date"] < c["date"] and x["regle"] == c["regle"]]
    if len(train) < 15: continue
    pi = em(train)
    law = kalshi_law(c["k"], c["T"])
    if law is None: continue
    for (lo, hi), tok in c["bins"]:
        q = sum(p * pi[s] for v, p in law.items() for s in range(4) if lo <= v - s <= hi)
        pts = PX.get(tok) or []
        j = bisect.bisect_right([t for t, _ in pts], c["T"]) - 1
        if j < 0 or c["T"] - pts[j][0] > 3 * 3600: continue
        p = pts[j][1]; y = (lo, hi) == c["win"]
        rows.append((c, (lo, hi), min(max(q, .005), .995), p, y))
print(f"{len(rows)} tranches avec prix Polymarket et loi Kalshi ({len({r[0]['ev'] for r in rows})} événements)")
lk = sum(-math.log(q if y else 1 - q) for _, _, q, p, y in rows) / len(rows)
lp = sum(-math.log(min(max(p, .005), .995) if y else 1 - min(max(p, .005), .995)) for _, _, q, p, y in rows) / len(rows)
print(f"log-perte : Kalshi corrigé {lk:.4f}  Polymarket {lp:.4f}")
for regle in ("metar", "weather.gov", "wunderground"):
    R = [r for r in rows if r[0]["regle"] == regle]
    if R:
        a = sum(-math.log(q if y else 1 - q) for _, _, q, p, y in R) / len(R); b = sum(-math.log(min(max(p, .005), .995) if y else 1 - min(max(p, .005), .995)) for _, _, q, p, y in R) / len(R)
        print(f"  {regle:12s} {len(R)} tranches : Kalshi {a:.4f}  Polymarket {b:.4f}")
# achats simulés : OUI si q − (p + écart) ≥ seuil ; NON si (1−q) − (1−p + écart) ≥ seuil ; prix payé 0,02-0,98
bets = []
for c, b, q, p, y in rows:
    for side, qq, pp, win in ((1, q, p + ECART, y), (0, 1 - q, 1 - p + ECART, not y)):
        if 0.02 <= pp <= 0.98 and qq - pp >= SEUIL:
            bets.append((c["ev"], c["date"].strftime("%Y-%m"), side, pp, qq, win, c["regle"]))
if bets:
    n = len(bets); g = sum(b[5] for b in bets); att = sum(b[3] for b in bets); mise = sum(b[3] for b in bets)
    rend = (g - att) / mise
    print(f"\nachats (seuil {SEUIL}, écart {ECART}) : {n} paris, {g} gagnés pour {att:.1f} attendus par les prix ({sum(b[4] for b in bets):.1f} par Kalshi), rendement {rend:+.1%}")
    byev = defaultdict(list)
    for b in bets: byev[b[0]].append((b[5] - b[3]) / b[3])
    xs = [sum(v) / len(v) for v in byev.values()]; m = sum(xs) / len(xs); sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** .5 if len(xs) > 1 else 0
    print(f"  par événement : {len(xs)} événements, moyenne {m:+.1%}, t {m / (sd / len(xs) ** .5) if sd else 0:+.2f}")
    for k in sorted({b[1] for b in bets}):
        B = [b for b in bets if b[1] == k]; print(f"  {k} : {len(B)} paris, {sum(b[5] for b in B)} pour {sum(b[3] for b in B):.1f}, {(sum(b[5] for b in B) - sum(b[3] for b in B)) / sum(b[3] for b in B):+.1%}")
    for s in (1, 0):
        B = [b for b in bets if b[2] == s]
        if B: print(f"  {'OUI' if s else 'NON'} : {len(B)} paris, {(sum(b[5] for b in B) - sum(b[3] for b in B)) / sum(b[3] for b in B):+.1%}")
    for lo, hi in ((0, .1), (.1, .45), (.45, .8), (.8, 1)):
        B = [b for b in bets if lo <= b[3] < hi]
        if B: print(f"  prix {lo}-{hi} : {len(B)} paris, {(sum(b[5] for b in B) - sum(b[3] for b in B)) / sum(b[3] for b in B):+.1%}")

# ---- aux vrais échanges : premier achat PRENEUR de la même issue dans les FEN heures après T, à un prix ≤ q − seuil,
# sur au moins MIN_PARTS parts (cumulées au même prix ou moins) ; frais : 1 point avant le 20/10 (météo payante), 0 après.
import os
if os.path.exists("donnees/echanges.json"):
    TR = json.load(open("donnees/echanges.json"))
    cond_of = {m["jetons"][0]: m["cond"] for e in PE for m in e["marches"] if m["jetons"]}
    FEN = 2
    for MIN_PARTS in (0, 20, 100):
        reel = []
        for c, (lo, hi), q, p, y in rows:
            tok = next(t for b, t in c["bins"] if b == (lo, hi))
            tr = sorted(TR.get(cond_of.get(tok), []))
            for side, qq, win in ((1, q, y), (0, 1 - q, not y)):
                lim = qq - SEUIL; issue = "Yes" if side else "No"; cum = 0.0
                for ts, sd, oc, pr, sz in tr:
                    if ts < c["T"] or ts > c["T"] + FEN * 3600 or sd != "BUY" or oc != issue or float(pr) > lim: continue
                    cum += float(sz)
                    if cum >= max(MIN_PARTS, 1e-9) and 0.02 <= float(pr) <= 0.98:
                        frais = 0.01 if c["date"] < dt.date(2026, 10, 20) else 0.0
                        reel.append((c["ev"], c["date"].strftime("%Y-%m"), side, float(pr) + frais, qq, win)); break
        if not reel: print(f"\nvrais échanges (≥ {MIN_PARTS} parts) : aucun"); continue
        n = len(reel); g = sum(b[5] for b in reel); mise = sum(b[3] for b in reel)
        byev = defaultdict(list)
        for b in reel: byev[b[0]].append((b[5] - b[3]) / b[3])
        xs = [sum(v) / len(v) for v in byev.values()]; m = sum(xs) / len(xs); sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** .5 if len(xs) > 1 else 0
        mois = defaultdict(lambda: [0, 0.0])
        for b in reel: mois[b[1]][0] += b[5]; mois[b[1]][1] += b[3]
        print(f"\nvrais échanges (≥ {MIN_PARTS} parts, {FEN} h) : {n} paris, {g} gagnés pour {mise:.1f} payés, rendement {(g - mise) / mise:+.1%} ; "
              f"{len(xs)} événements, t par événement {m / (sd / len(xs) ** .5) if sd else 0:+.2f} ; par mois "
              + ", ".join(f"{k} {(v[0] - v[1]) / v[1]:+.0%}" for k, v in sorted(mois.items())))
