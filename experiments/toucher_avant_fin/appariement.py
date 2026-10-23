"""Piste n° 2 : « touche X pendant la journée » ≥ « au-dessus de X à midi (ET) » (principe de réflexion).
Appariement des événements Bitcoin/Ethereum/Solana « what-price-will-<x>-hit-on-<jour> » (barres ↑ et ↓) et « <x>-above-on-<jour> ».
Pour chaque force X commune : achat « touche OUI » + « au-dessus NON » (↑) ou « touche OUI » + « au-dessus OUI » (↓) paie au moins 1.
Historique CLOB à 10 min -> donnees/appar_prix.json ; ensuite analyse_appar.py."""
import json, re, datetime as dt, requests, concurrent.futures as cf, os
H = {"User-Agent": "curl/8"}
E = json.load(open("experiments/toucher_avant_fin/donnees/evenements.json"))
def day(slug, pref):
    m = re.match(rf"{pref}-(\w+)-(\d+)(?:-(\d{{4}}))?$", slug)
    if not m: return None
    mon, d, y = m.groups()
    try: return dt.datetime.strptime(f"{mon} {d} {y or 2026}", "%B %d %Y").date()
    except ValueError: return None
pairs = []
for asset in ("bitcoin", "ethereum", "solana"):
    hits = {day(e["slug"], f"what-price-will-{asset}-hit-on"): e for e in E if e["slug"].startswith(f"what-price-will-{asset}-hit-on")}
    abv = {day(e["slug"], f"{asset}-above-on"): e for e in E if e["slug"].startswith(f"{asset}-above-on")}
    for d, h in hits.items():
        if d and d in abv: pairs.append((asset, d, h, abv[d]))
print(len(pairs), "jours appariés")
def strike(m):
    s = re.sub(r"[^\d.]", "", (m["item"] or "").split(" ")[-1].replace(",", ""))
    return float(s) if s else None
tasks = []
for asset, d, h, a in pairs:
    aby = {strike(m): m for m in a["markets"]}
    for m in h["markets"]:
        k = strike(m)
        if k in aby:
            up = (m["item"] or "").startswith("↑")
            tasks.append(dict(asset=asset, day=str(d), strike=k, up=up, reach=m, above=aby[k]))
print(len(tasks), "couples touche/au-dessus")
def hist(tok, a, b):
    out = []
    for _ in range(3):
        try:
            r = requests.get("https://clob.polymarket.com/prices-history", headers=H, timeout=60, params={"market": tok, "startTs": a, "endTs": b, "fidelity": 10})
            if r.status_code == 200: return [[p["t"], p["p"]] for p in r.json().get("history", [])]
        except requests.RequestException: pass
    return None
def one(t):
    d = dt.datetime.fromisoformat(t["day"]).replace(tzinfo=dt.timezone.utc)
    a = int((d + dt.timedelta(hours=4)).timestamp()); b = int((d + dt.timedelta(hours=16, minutes=5)).timestamp())  # 04:00 UTC -> 12:05 ET
    return dict(t, hr=hist(t["reach"]["yes"], a, b), ha=hist(t["above"]["yes"], a, b))
with cf.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(one, tasks))
json.dump(res, open("experiments/toucher_avant_fin/donnees/appar_prix.json", "w"))
print(sum(1 for r in res if r["hr"] and r["ha"]), "couples avec historique")
