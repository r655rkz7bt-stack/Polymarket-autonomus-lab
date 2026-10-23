"""Fatigue NHL (équipe qui a joué la veille) aux PRIX PAYÉS (23/10/2026). Reprend nhl_releve_prix.py / nhl_fatigue.py de
vingt_pistes (prix CLOB « une heure avant le match », +6,1 % par achat, t +1,2) en remplaçant le prix horaire par les vrais échanges
du marché « vainqueur du match » (data-api, filtre `market=<conditionId>`).

  prix connu   = dernier échange du jeton dans les `AVANT` heures qui précèdent T = coup d'envoi − `H` heures
  prix payé    = premier échange du jeton ADVERSE (achat de l'autre issue) dans les `APRES` heures qui suivent T (avant le coup d'envoi)
  pas d'échange = pas d'achat (compté).
Lancer depuis experiments/nhl_prix_payes/ : PYTHONPATH=../../src python test_prix_payes.py [H avant apres]"""
import bisect, collections, gzip, json, math, re, statistics as st, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
import requests

D = Path("donnees/nhl")
H = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
AVANT = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
APRES = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
S = requests.Session()
S.headers["User-Agent"] = "curl/8"
base = json.load(open(D / "base.json"))
games = [g for g in base["games"].values() if g["type"] in (2, 3) and g["state"] in ("OFF", "FINAL") and g["sa"] is not None]
played = {}
for g in games:
    for t in (g["away"], g["home"]):
        played.setdefault(t, set()).add(g["date"])
low = lambda x: (x or "").lower()
evs = [e for e in base["events"] if e["markets"] and re.match(r"nhl-[a-z]+-[a-z]+-\d{4}-\d{2}-\d{2}$", e["slug"])]
by_date = collections.defaultdict(list)
for e in evs:
    by_date[e["slug"][-10:]].append(e)
rows = []
for g in games:
    hit = None
    for e in by_date.get(g["date"], []):
        m = e["markets"][0]
        outs = [low(o) for o in json.loads(m["outcomes"])]
        same = lambda o, names: any(n and (low(n) in o or o in low(n)) for n in names)
        if len(outs) == 2 and same(outs[0], g["away_names"]) and same(outs[1], g["home_names"]):
            hit = (e, m, 0)
        elif len(outs) == 2 and same(outs[1], g["away_names"]) and same(outs[0], g["home_names"]):
            hit = (e, m, 1)
    if not hit:
        continue
    e, m, flip = hit
    prev = (datetime.fromisoformat(g["date"]) - timedelta(days=1)).date().isoformat()
    toks = json.loads(m["tok"])
    # règlement relu : le jeton « visiteur » est toks[flip]
    res = json.loads(m["res"] or "[0,0]")
    away_paid = float(res[flip]) >= 0.5
    if away_paid != (g["sa"] > g["sh"]) and float(res[flip]) in (0.0, 1.0):
        continue  # le règlement ne redonne pas le score officiel
    rows.append(dict(date=g["date"], start=g["start"], away=g["away"], home=g["home"], away_win=g["sa"] > g["sh"],
                     b2b_away=prev in played[g["away"]], b2b_home=prev in played[g["home"]], tok_away=toks[flip],
                     tok_home=toks[1 - flip], cond=m["cond"], slug=e["slug"]))
print("matchs rattachés", len(rows), "sur", len(games), flush=True)


def trades_of(r):
    path = D / "cache" / f"{r['cond']}.json.gz"
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    out = []
    for page in range(10):
        for k in range(4):
            try:
                b = S.get("https://data-api.polymarket.com/trades", params={"market": r["cond"], "limit": 1000, "offset": page * 1000}, timeout=40).json()
                break
            except Exception:
                b = None
        if not isinstance(b, list) or not b:
            break
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp")]
        if len(b) < 1000:
            break
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(out).encode()))
    return out


with ThreadPoolExecutor(8) as ex:
    allt = list(ex.map(trades_of, rows))
print("échanges", sum(len(t) for t in allt), flush=True)


class Jeton:
    def __init__(self, tok, other, trades):
        pts = sorted((t[0], t[3] if t[1] == tok else 1 - t[3]) for t in trades
                     if (t[1] == tok and t[2] == "BUY") or (t[1] == other and t[2] == "SELL"))
        self.t, self.p = [a for a, _ in pts], [b for _, b in pts]

    def avant(self, ts, w):
        i = bisect.bisect_right(self.t, ts) - 1
        return self.p[i] if i >= 0 and ts - self.t[i] <= w else None

    def apres(self, ts, w):
        i = bisect.bisect_left(self.t, ts)
        return self.p[i] if i < len(self.t) and self.t[i] - ts <= w else None


cases = collections.defaultdict(list)
sans = collections.Counter()
for r, tr in zip(rows, allt):
    start = int(datetime.fromisoformat(r["start"].replace("Z", "+00:00")).timestamp())
    T = start - int(H * 3600)
    away, home = Jeton(r["tok_away"], r["tok_home"], tr), Jeton(r["tok_home"], r["tok_away"], tr)
    p_away = away.avant(T, AVANT * 3600)  # prix connu du visiteur
    if p_away is None or not 0.05 < p_away < 0.95:
        sans["prix connu"] += 1
        continue
    if r["b2b_away"] and not r["b2b_home"]:
        kind, tired, rested, tired_wins = "fatigué dehors, adversaire reposé", away, home, r["away_win"]
    elif r["b2b_home"] and not r["b2b_away"]:
        kind, tired, rested, tired_wins = "fatigué à domicile, adversaire reposé", home, away, not r["away_win"]
    elif r["b2b_home"] and r["b2b_away"]:
        kind = "les deux"; tired, rested, tired_wins = away, home, r["away_win"]
    else:
        kind = "aucun"; tired, rested, tired_wins = away, home, r["away_win"]
    p_tired = tired.avant(T, AVANT * 3600)
    paid = rested.apres(T, APRES * 3600)  # prix payé pour acheter l'adversaire
    if paid is None:
        sans[kind] += 1
        cases[kind + " (sans échange)"].append(1)
        continue
    if not 0.02 <= paid <= 0.98:
        continue
    win = not tired_wins
    fee = 0.05 * paid * (1 - paid)  # même taux que le test d'origine (prudent pour le sport)
    cases[kind].append(dict(slug=r["slug"], date=r["date"], paid=paid, win=win, gain=((1.0 if win else 0.0) - paid - fee) / paid,
                            p_tired=p_tired, tired_wins=tired_wins))

print(f"T = coup d'envoi − {H} h, prix connu : dernier échange dans les {AVANT} h avant ; prix payé : premier échange dans les {APRES} h après")
print("sans prix connu :", sans["prix connu"])
for kind in ("fatigué dehors, adversaire reposé", "fatigué à domicile, adversaire reposé", "les deux", "aucun"):
    v = cases.get(kind, [])
    nos = len(cases.get(kind + " (sans échange)", []))
    if len(v) < 5:
        print(f"  {kind:42} {len(v)} achats ({nos} sans échange)")
        continue
    g = [x["gain"] for x in v]
    t = st.mean(g) / st.stdev(g) * math.sqrt(len(g))
    won = sum(x["win"] for x in v)
    exp = sum(x["paid"] for x in v)
    # écart de l'équipe fatiguée (prix connu contre résultat)
    pf = [x for x in v if x["p_tired"] is not None]
    ecart = (sum(x["tired_wins"] for x in pf) - sum(x["p_tired"] for x in pf)) / len(pf)
    mois = collections.defaultdict(list)
    for x in v:
        mois[x["date"][:7]].append(x["gain"])
    saisons = collections.defaultdict(list)
    for x in v:
        saisons["24-25" if x["date"] < "2025-08" else ("25-26" if x["date"] < "2026-08" else "26-27")].append(x["gain"])
    print(f"  {kind:42} {len(v):4} achats ({nos} sans échange) | par achat {st.mean(g):+.3f} (t {t:+.2f}) | adversaire gagne {won}/{exp:.1f} attendus | "
          f"équipe fatiguée : écart prix connu {ecart:+.3f} | " + " ".join(f"{k}:{st.mean(x):+.2f}(n{len(x)})" for k, x in sorted(saisons.items())))
