"""Pendant la vie du marché (Bab el-Mandeb, fin octobre) : prix du OUI de chaque tranche (historique CLOB, un point par jour à 12 h UTC) contre la loi
calculée avec les seules données PortWatch publiées à cette date (dernier jour connu = jour - 5). Un seul événement : indice, pas preuve."""
import csv, datetime as dt, json, sys
import requests
from polymarket_agent import references as refs

H = {"User-Agent": "curl/8"}
rows = list(csv.DictReader(open("experiments/detroits/donnees/bab.csv")))
days = [r["jour"] for r in rows]
counts = [int(r["n_total"]) for r in rows]
ev = requests.get("https://gamma-api.polymarket.com/events/1111175", headers=H, timeout=30).json()
target = dt.date(2026, 10, 31)
print("événement créé le", ev.get("creationDate", ev.get("startDate")))
for m in ev["markets"]:
    q = m["question"]
    tr = refs.detroit_tranche(q, "Bab el-Mandeb Strait")
    tok = json.loads(m["clobTokenIds"])[0]
    h = requests.get("https://clob.polymarket.com/prices-history", params=dict(market=tok, interval="max", fidelity=60), headers=H, timeout=40).json().get("history", [])
    by_day = {}
    for p in h:
        t = dt.datetime.fromtimestamp(p["t"], dt.timezone.utc)
        if t.hour == 12:
            by_day[t.date()] = p["p"]
    out = []
    for d, price in sorted(by_day.items()):
        known = (d - dt.timedelta(days=5)).isoformat()   # PortWatch publie avec ≈ 5 jours de retard
        if known not in days:
            continue
        k = days.index(known)
        f = refs.ma7_forecast(counts[: k + 1], (target - dt.date.fromisoformat(known)).days)
        if not f:
            continue
        mu, sd = f
        p = refs._normal_cdf((tr[1] - mu) / sd) - refs._normal_cdf((tr[0] - mu) / sd)
        out.append((d, price, p))
    print(q[22:75], "| tranche", tr)
    for d, price, p in out[-12:]:
        print("   ", d, f"marché {price:.3f}  loi {p:.3f}")
