"""Meneur du marché « Billboard 200 #1 Album Week of <samedi X> » à trois instants de la semaine de suivi (vendredi X-15 → jeudi X-9) :
mardi X-11 à 22 h UTC (prévision « Chart Preview » de HITS Daily Double publiée vers 16-17 h UTC), jeudi X-9 22 h, samedi X-7 12 h
(avant l'annonce du dimanche X-6). Prix = dernier point de prices-history (milieu, fidelity 60) avant l'instant ; gagnant = issue Gamma.
Sortie : releves/meneurs.json ; résumé imprimé (gagnés contre attendus, rendement si l'on achète le meneur à son prix)."""
import json, re, datetime as dt
from pathlib import Path
import requests

R = Path(__file__).resolve().parents[1] / "releves"
MOIS = "january february march april may june july august september october november december".split()
evs = json.loads((R / "evenements.json").read_text())


def samedi(e):
    m = re.search(r"Week of (\w+) (\d+)", e["titre"])
    an = int((e.get("fin") or e.get("ferme") or "2026")[:4])
    d = dt.date(an, MOIS.index(m.group(1).lower()) + 1, int(m.group(2)))
    fin = dt.date.fromisoformat((e.get("fin") or "")[:10]) if e.get("fin") else d
    if d > fin + dt.timedelta(days=30):
        d = d.replace(year=an - 1)
    return d


def serie(tok, a, b):
    h = requests.get("https://clob.polymarket.com/prices-history", timeout=30,
                     params={"market": tok, "startTs": int(a.timestamp()), "endTs": int(b.timestamp()), "fidelity": 60}).json()
    return h.get("history", [])


res = []
for e in evs:
    X = samedi(e)
    t = {"mar": dt.datetime.combine(X - dt.timedelta(days=11), dt.time(22), tzinfo=dt.timezone.utc),
         "jeu": dt.datetime.combine(X - dt.timedelta(days=9), dt.time(22), tzinfo=dt.timezone.utc),
         "sam": dt.datetime.combine(X - dt.timedelta(days=7), dt.time(12), tzinfo=dt.timezone.utc)}
    a = t["mar"] - dt.timedelta(days=5)
    prix = {}
    for m in e["marches"]:
        h = serie(m["jeton"], a, t["sam"])
        prix[m["nom"]] = {k: next((x["p"] for x in reversed(h) if x["t"] <= v.timestamp()), None) for k, v in t.items()}
    gagnant = [m["nom"] for m in e["marches"] if m["issue"] > 0.5]
    row = {"titre": e["titre"], "samedi": X.isoformat(), "gagnant": gagnant, "prix": prix}
    for k in t:
        cands = [(p[k], n) for n, p in prix.items() if p[k] is not None]
        if cands:
            pm, nm = max(cands)
            row[f"meneur_{k}"] = (nm, pm, nm in gagnant)
    res.append(row)
    print(X, gagnant, {k: row.get(f"meneur_{k}") for k in t}, flush=True)
(R / "meneurs.json").write_text(json.dumps(res, ensure_ascii=False, indent=0))
for k in ("mar", "jeu", "sam"):
    rows = [r[f"meneur_{k}"] for r in res if r.get(f"meneur_{k}")]
    g = sum(1 for r in rows if r[2]); att = sum(r[1] for r in rows)
    rend = sum((1 / r[1] - 1) if r[2] else -1 for r in rows) / max(len(rows), 1)
    print(k, "meneurs", len(rows), "gagnés", g, "attendus", round(att, 1), "rendement moyen par mise", round(rend, 3),
          "prix moyen", round(att / max(len(rows), 1), 3))
