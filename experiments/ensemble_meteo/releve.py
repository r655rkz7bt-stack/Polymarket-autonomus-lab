"""Relevé en direct (23/10/2026, chantier 34) : probabilités par tranche des ensembles Open-Meteo (GEFS 31 membres, ECMWF 51 membres)
et prix Polymarket du même instant, pour les marchés de température qui finissent dans les 40 prochaines heures.
Le règlement vient plus tard : `evalue.py` relit les marchés réglés et compare (log-score, achats aux vrais carnets).
Usage : python experiments/ensemble_meteo/releve.py   (depuis la racine du dépôt, PYTHONPATH=src)"""
import gzip, json, re, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests
from polymarket_agent import weather_model as wm

H = {"User-Agent": "curl/8"}
G = "https://gamma-api.polymarket.com"
OUT = Path(__file__).parent / "releves"  # versionné (gz) : le passage suivant les relit, `donnees/` est ignoré par Git
OUT.mkdir(exist_ok=True)


def get(url, params, tries=3):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=H, timeout=60)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(1 + 2 * i)
    return None


now = datetime.now(timezone.utc)
events, off = [], 0
while True:
    page = get(f"{G}/events", dict(tag_id=84, closed="false", end_date_min=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                   end_date_max=(now + timedelta(hours=40)).strftime("%Y-%m-%dT%H:%M:%SZ"), limit=100, offset=off))
    if not page:
        break
    events += page
    if len(page) < 100:
        break
    off += 100
rows = []
for e in events:
    if not re.match(r"(highest|lowest)-temperature-in-", e.get("slug", "")):
        continue
    for m in e.get("markets", []):
        ST = r"(?:site=|metar\?(?:[^\s#]*&)?ids=)([a-z0-9]{3,5})"  # weather.gov/wrh (jusqu'au 18/10) ou aviationweather.gov (19/10 et après)
        st = re.search(ST, m.get("resolutionSource") or "", re.I) or re.search(ST, m.get("description") or "", re.I)
        q = wm.parse_question(m.get("question", ""))
        try:
            toks = json.loads(m["clobTokenIds"])
            yes = float(json.loads(m["outcomePrices"])[0])
        except Exception:
            continue
        if not st or not q or m.get("closed"):
            continue
        rows.append({"id": m["id"], "q": m["question"], "station": st.group(1).upper(), "event": e["slug"], "yes_token": toks[0], "kind": q.kind,
                     "low": q.low, "high": q.high, "unit": q.unit if hasattr(q, "unit") else None, "date": None,
                     "bid": m.get("bestBid"), "ask": m.get("bestAsk"), "last": yes, "end": m.get("endDate"), "fees": m.get("feeSchedule")})
stations = sorted({r["station"] for r in rows})
ll = {}
for i in range(0, len(stations), 30):
    for x in get("https://aviationweather.gov/api/data/metar", {"ids": ",".join(stations[i:i + 30]), "format": "json", "hours": 3}) or []:
        ll[x["icaoId"].upper()] = (x["lat"], x["lon"])
print(len(events), "événements,", len(rows), "marchés,", len(stations), "stations,", len(ll), "localisées")
ens = {}
for s in stations:
    if s not in ll:
        continue
    d = get("https://ensemble-api.open-meteo.com/v1/ensemble", dict(latitude=ll[s][0], longitude=ll[s][1], hourly="temperature_2m",
                                                                      models="gfs025,ecmwf_ifs025", forecast_days=3, timezone="auto"))
    if d:
        ens[s] = d
    time.sleep(0.3)
MONTHS = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}
kept = []
for r in rows:
    d = ens.get(r["station"])
    mm = re.search(r"on (\w+) (\d+)\??$", r["q"])
    if not d or not mm:
        continue
    r["date"] = f"2026-{MONTHS[mm.group(1)]:02d}-{int(mm.group(2)):02d}"
    h = d["hourly"]
    idx = [i for i, t in enumerate(h["time"]) if t.startswith(r["date"])]
    if len(idx) < 24:
        continue
    groups = {"gefs": [], "ecmwf": []}
    for k, v in h.items():
        mem = re.match(r"temperature_2m_member\d+_(ncep_gefs025|ecmwf_ifs025_ensemble)$", k)
        if not mem:
            continue
        vals = [v[i] for i in idx if v[i] is not None]
        if len(vals) >= 24:
            groups["gefs" if "gefs" in k else "ecmwf"].append(max(vals) if r["kind"] == "max" else min(vals))
    q = wm.parse_question(r["q"])
    pool = groups["gefs"] + groups["ecmwf"]
    if not pool:
        continue
    r["n_gefs"], r["n_ecmwf"] = len(groups["gefs"]), len(groups["ecmwf"])
    r["membres"] = {k: [round(x, 1) for x in v] for k, v in groups.items()}
    for name, mem in (("p_pool", pool), ("p_gefs", groups["gefs"]), ("p_ecmwf", groups["ecmwf"])):
        r[name] = wm.probability(q, mem, 0.6) if mem else None
    kept.append(r)
stamp = now.strftime("%Y%m%d_%H%M")
with gzip.open(OUT / f"releve_{stamp}.json.gz", "wt", encoding="utf-8") as f:
    json.dump({"pris_le": now.isoformat(timespec="seconds"), "marches": kept}, f, ensure_ascii=False)
print(len(kept), "marchés avec ensemble ->", OUT / f"releve_{stamp}.json.gz")
