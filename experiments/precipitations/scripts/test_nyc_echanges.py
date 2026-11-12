"""Même test que test_nyc.py, mais au prix des VRAIS échanges : pour chaque tranche et chaque côté où le modèle (au 11 du mois,
12 h UTC) voit un avantage, premier échange réel du jeton dans les 72 h qui suivent à un prix <= chance − 0,08 (on achète à ce
prix-là, la quantité échangée est notée). Échanges : Data API v2 par événement (data_api.lire). Frais non comptés (voir feeSchedule)."""
import json, math, re, sys, datetime as dt
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from polymarket_agent.http_client import HttpClient
from polymarket_agent import data_api

H = {"User-Agent": "curl/8"}
EVENTS = {1: 131194, 2: 193622, 3: 232661, 4: 303983, 5: 427844, 6: 531291, 7: 686198, 8: 763089, 9: 941972, 10: 1108649}
SEUIL = float(sys.argv[1]) if len(sys.argv) > 1 else 0.08
JOUR = int(sys.argv[2]) if len(sys.argv) > 2 else 11
r = requests.post("https://data.rcc-acis.org/StnData", json={"sid": "94728", "sdate": "1951-01-01", "edate": "2026-11-10",
                  "elems": [{"name": "pcpn"}]}, headers=H, timeout=120).json()
P = {d: (0.0 if v == "T" else (float(v.rstrip("A")) if v not in ("M", "S") else None)) for d, v in r["data"]}
http = HttpClient()


def bornes(nom):
    x = [float(t) for t in re.findall(r"\d+(?:\.\d+)?", nom)]
    if "<" in nom: return 0.0, x[0]
    if ">" in nom or "+" in nom: return x[0], 99.0
    return x[0], x[1]


paris = []
for mois, eid in EVENTS.items():
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=60).json()
    fin = dt.date(2026, mois + 1, 1) - dt.timedelta(days=1)
    vu = sum(P.get(f"2026-{mois:02d}-{j:02d}") or 0.0 for j in range(1, JOUR))
    restes = [sum(P.get(f"{an}-{mois:02d}-{j:02d}") or 0.0 for j in range(JOUR, fin.day + 1)) for an in range(1951, 2026)]
    tot = [vu + x for x in restes]
    T = dt.datetime(2026, mois, JOUR, 12, tzinfo=dt.timezone.utc).timestamp()
    tr = data_api.lire(http, data_api.TRADES, {"event_id": eid}, pages=20)
    for m in e["markets"]:
        if "outcomePrices" not in m: continue
        a, b = bornes(m.get("groupItemTitle") or "")
        q = max(min(sum(1 for x in tot if a <= x < b) / len(tot), 0.98), 0.02)
        y = float(json.loads(m["outcomePrices"])[0]) > 0.5
        toks = json.loads(m["clobTokenIds"])
        for cote, est, tok, gagne in (("OUI", q, toks[0], y), ("NON", 1 - q, toks[1], not y)):
            ech = sorted((float(x["timestamp"]), float(x["price"]), float(x["size"])) for x in tr
                         if str(x.get("asset")) == tok and T <= float(x["timestamp"]) <= T + 72 * 3600)
            ok = [x for x in ech if x[1] <= est - SEUIL and x[1] <= 0.95]
            if ok:
                paris.append((mois, m.get("groupItemTitle"), cote, round(est, 3), ok[0][1], round(ok[0][2], 1), gagne))
    print(mois, len(tr), "échanges", flush=True)
g = sum(1 for p in paris if p[6]); att = sum(p[4] for p in paris)
rend = sum((1 / p[4] - 1) if p[6] else -1 for p in paris) / max(len(paris), 1)
mois_res = {}
for p in paris:
    mois_res[p[0]] = mois_res.get(p[0], 0) + ((1 / p[4] - 1) if p[6] else -1)
vals = list(mois_res.values()); mu = sum(vals) / len(vals) if vals else 0
sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else float("nan")
print(f"seuil {SEUIL} jour {JOUR} : paris {len(paris)}, gagnés {g}, attendus (prix payés) {att:.1f}, rendement par mise {rend:+.3f},"
      f" mois {len(vals)}, t par mois {mu / (sd / math.sqrt(len(vals))) if len(vals) > 1 and sd > 0 else float('nan'):.2f}")
for p in paris: print("  ", p)
