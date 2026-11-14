"""Hong Kong, mars → octobre 2026 : cumul observé (Daily Extract / CSV de l'Observatoire, jours 1 à J−1, connus le jour J à 12 h UTC =
20 h à Hong Kong grâce au bulletin RYES) + reste du mois tiré des mêmes dates 1947-2025 ; premier VRAI échange du jeton dans les 72 h
à un prix <= chance − seuil, d'au moins `MIN_PARTS` parts. Usage : test_hk_echanges.py <seuil> <jour> <min_parts>."""
import csv, json, math, re, sys, collections, datetime as dt
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from polymarket_agent.http_client import HttpClient
from polymarket_agent import data_api

H = {"User-Agent": "curl/8"}
EVENTS = {3: 265697, 4: 304054, 5: 427967, 6: 531426, 7: 681514, 8: 763095, 9: 941962, 10: 1108650}
SEUIL = float(sys.argv[1]) if len(sys.argv) > 1 else 0.08
JOUR = int(sys.argv[2]) if len(sys.argv) > 2 else 11
MIN_PARTS = float(sys.argv[3]) if len(sys.argv) > 3 else 0
ICI = Path(__file__).parent
P = collections.defaultdict(dict)
for r in csv.reader(open(ICI / "donnees" / "daily_HKO_RF_ALL.csv", encoding="utf-8-sig")):
    if len(r) < 4 or not r[0].isdigit() or r[3].strip() == "***": continue
    P[(int(r[0]), int(r[1]))][int(r[2])] = 0.0 if r[3].strip() in ("Trace", "微量", "") else float(r[3])
oct26 = requests.get("https://www.weather.gov.hk/cis/dailyExtract/dailyExtract_202610.xml", headers=H, timeout=30).json()
for row in oct26["stn"]["data"][0]["dayData"]:
    if row[0].isdigit(): P[(2026, 10)][int(row[0])] = 0.0 if row[-1].strip() == "Trace" else float(row[-1])
cache = ICI / "donnees"; cache.mkdir(exist_ok=True)
http = HttpClient()


def bornes(nom):
    x = [float(t) for t in re.findall(r"\d+(?:\.\d+)?", nom)]
    if "<" in nom: return 0.0, x[0]
    if "+" in nom or "more" in nom: return x[0], 1e9
    return x[0], x[1]


paris = []
for mois, eid in EVENTS.items():
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=60).json()
    n = (dt.date(2026, mois + 1, 1) - dt.timedelta(days=1)).day
    vu = sum(P[(2026, mois)].get(j, 0.0) for j in range(1, JOUR))
    tot = [vu + sum(P[(an, mois)].get(j, 0.0) for j in range(JOUR, n + 1)) for an in range(1947, 2026) if len(P[(an, mois)]) >= n]
    T = dt.datetime(2026, mois, JOUR, 12, tzinfo=dt.timezone.utc).timestamp()
    f = cache / f"trades_{eid}.json"
    if f.exists(): tr = json.loads(f.read_text())
    else:
        tr = data_api.lire(http, data_api.TRADES, {"event_id": eid}, pages=20); f.write_text(json.dumps(tr))
    final = vu + sum(P[(2026, mois)].get(j, 0.0) for j in range(JOUR, n + 1))
    for m in e["markets"]:
        if "outcomePrices" not in m: continue
        a, b = bornes(m.get("groupItemTitle") or "")
        q = max(min(sum(1 for x in tot if a <= x < b) / len(tot), 0.98), 0.02)
        y = float(json.loads(m["outcomePrices"])[0]) > 0.5
        assert y == (a <= final < b), (mois, m.get("groupItemTitle"), final)   # contrôle du règlement
        toks = json.loads(m["clobTokenIds"])
        for cote, est, tok, gagne in (("OUI", q, toks[0], y), ("NON", 1 - q, toks[1], not y)):
            ech = sorted((float(x["timestamp"]), float(x["price"]), float(x["size"])) for x in tr
                         if str(x.get("asset")) == tok and T <= float(x["timestamp"]) <= T + 72 * 3600 and str(x.get("side")) == "BUY")
            ok = [x for x in ech if x[1] <= est - SEUIL and x[1] <= 0.95 and x[2] >= MIN_PARTS]
            if ok:
                paris.append((mois, m.get("groupItemTitle"), cote, round(est, 3), ok[0][1], round(ok[0][2], 1), gagne))
g = sum(1 for p in paris if p[6]); att = sum(p[4] for p in paris)
rend = sum((1 / p[4] - 1) if p[6] else -1 for p in paris) / max(len(paris), 1)
mois_res = collections.defaultdict(float)
for p in paris: mois_res[p[0]] += (1 / p[4] - 1) if p[6] else -1
vals = list(mois_res.values()); mu = sum(vals) / len(vals) if vals else 0
sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else float("nan")
print(f"seuil {SEUIL} jour {JOUR} parts>={MIN_PARTS} : paris {len(paris)}, gagnés {g}, attendus (prix) {att:.1f}, par le modèle "
      f"{sum(p[3] for p in paris):.1f}, rendement par mise {rend:+.3f}, mois {len(vals)}, t par mois "
      f"{mu / (sd / math.sqrt(len(vals))) if len(vals) > 1 and sd > 0 else float('nan'):.2f}")
if "-v" in sys.argv:
    for p in paris: print("  ", p)
