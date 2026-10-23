"""Évalue les relevés d'ensembles Open-Meteo (releve.py) sur les marchés de température DÉJÀ RÉGLÉS, au prix qu'on aurait payé.
Pour chaque marché réglé : résultat (Gamma /markets/<id>), probabilité de l'ensemble (pool GEFS + ECMWF, GEFS seul, ECMWF seul) et du marché
(milieu du carnet relevé), puis log-score et achats simulés (prix vendeur / acheteur du relevé, frais lus dans le relevé : 0 depuis le 20/10).
Usage : python experiments/ensemble_meteo/evalue.py   (depuis la racine du dépôt)"""
import glob, gzip, json, math, sys
from collections import defaultdict
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor

H = {"User-Agent": "curl/8"}
rows = []
for f in sorted(glob.glob(str(Path(__file__).parent / "releves" / "releve_*.json.gz"))):
    d = json.load(gzip.open(f, "rt", encoding="utf-8"))
    for m in d["marches"]:
        m["pris_le"] = d["pris_le"]
        rows.append(m)
print(len(rows), "marchés relevés dans", len(glob.glob(str(Path(__file__).parent / "releves" / "*.gz"))), "fichiers")
def lire(mid):
    try:
        m = requests.get(f"https://gamma-api.polymarket.com/markets/{mid}", headers=H, timeout=30).json()
        pr = [float(x) for x in json.loads(m["outcomePrices"])]
    except Exception:
        return mid, None
    return mid, (pr[0] if m.get("closed") and sorted(pr) == [0.0, 1.0] else None)


with ThreadPoolExecutor(8) as ex:  # ~1 000 marchés : en parallèle (en série, plus de 5 minutes)
    won = {i: y for i, y in ex.map(lire, sorted({r["id"] for r in rows})) if y is not None}
done = [r for r in rows if r["id"] in won]
print(len(done), "relevés de marchés réglés (", len(set(r["id"] for r in done)), "marchés,", len(set(r["event"] for r in done)), "événements )")
if not done:
    sys.exit(0)

def mid(r):
    """Milieu du carnet ; dernier prix si le carnet est vide ou écarté (bid 0,001 / ask 0,999 donnerait un faux 0,50 : 23/10, Moscou « -2 °C ou moins »)."""
    b, a = r.get("bid"), r.get("ask")
    if b is not None and a is not None and float(a) - float(b) <= 0.2:
        return (float(b) + float(a)) / 2
    return float(r["last"])

def ll(p, y):
    p = min(max(p, 0.001), 0.999)
    return math.log(p if y else 1 - p)
for name in ("p_pool", "p_gefs", "p_ecmwf"):
    xs = [(ll(r[name], won[r["id"]]), ll(mid(r), won[r["id"]])) for r in done if r.get(name) is not None]
    print(f"{name} : log-score {sum(a for a, _ in xs)/len(xs):+.4f} contre marché {sum(b for _, b in xs)/len(xs):+.4f}  ({len(xs)} relevés)")
for name in ("p_pool", "p_gefs", "p_ecmwf"):
    for gap in (0.05, 0.10, 0.15):
        per_event = defaultdict(float); stake = gain = n = 0
        for r in done:
            p = r.get(name)
            if p is None or r.get("ask") is None or r.get("bid") is None:
                continue
            ask, bid, y = float(r["ask"]), float(r["bid"]), won[r["id"]]
            if p - ask >= gap and 0.02 <= ask <= 0.98:
                cost, pay = ask, y
            elif (1 - p) - (1 - bid) >= gap and 0.02 <= 1 - bid <= 0.98:
                cost, pay = 1 - bid, 1 - y
            else:
                continue
            stake += cost; gain += pay - cost; n += 1; per_event[r["event"]] += pay - cost
        if n:
            ev = list(per_event.values()); mean = sum(ev) / len(ev)
            sd = (sum((x - mean) ** 2 for x in ev) / max(len(ev) - 1, 1)) ** .5
            print(f"{name} écart ≥ {gap:.2f} : {n} achats, {gain/stake:+.1%} par mise, {len(ev)} événements, t par événement {mean/(sd/len(ev)**.5) if sd else 0:+.2f}")
