"""11/11/2026 : chaque achat de seismes_marche (v1 et v2) refait avec le catalogue USGS d'aujourd'hui À L'INSTANT DE L'ACHAT.
Un écart entre la chance notée à l'achat et la chance recalculée = séisme encore absent de notre relevé (retard de la source) ou révision.
Usage : PYTHONPATH=src .venv/bin/python experiments/enquetes/scripts/seismes_retard_catalogue_11_11.py"""
import json, re, sys, datetime as dt, requests
from polymarket_agent import seismes as s

UA = {"User-Agent": "curl/8"}
L = ["published_data/ledger/fantome/seismes_marche_v1.0.0.jsonl", "published_data/ledger/fantome_v2/seismes_marche_v2.0.0.jsonl"]
buys, settle = [], {}
for f in L:
    for l in open(f):
        x = json.loads(l)
        if x["type"] == "BUY":
            d = x["data"]; buys.append((f.split("/")[-1][15:19], x["ts"], d["market_id"], d["outcome"], float(d["price"]), float(d["shares"]), float(d["extra"]["est_probability"])))
        if x["type"] == "SETTLE":
            settle[x["data"]["token_id"]] = float(x["data"]["payout_per_share"])
q = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query", params={"format": "geojson", "minmagnitude": 5, "starttime": "2026-10-15", "orderby": "time-asc"}, timeout=60).json()
rows = [{"t": f["properties"]["time"] / 1000, "mag": f["properties"]["mag"], "id": f["id"]} for f in q["features"]]
DQ = re.compile(r"biggest earthquake on (\w+) (\d+), (\d{4}) be (.+)\?", re.I)
WQ = re.compile(r"earthquakes? of ([\d.]+) or above", re.I)
tot = 0
for v, ts, mid, outc, px, sh, est in buys:
    m = requests.get(f"https://gamma-api.polymarket.com/markets/{mid}", headers=UA, timeout=30).json()
    qn = m["question"]; now = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    p = None
    dm = DQ.search(qn)
    if dm:
        day = dt.datetime(int(dm.group(3)), s.MONTHS[dm.group(1).capitalize()], int(dm.group(2)), tzinfo=dt.timezone.utc)
        p = s.daily_p(rows, day, now, s.daily_bracket(qn))
    else:
        wm = WQ.search(qn); end = dt.datetime.fromisoformat(m["endDate"].replace("Z", "+00:00"))
        start = dt.datetime.fromisoformat(m["startDate"].replace("Z", "+00:00"))
        # semaine : lundi 00 h ET .. dimanche 24 h ET ; fin Gamma = dimanche 23:59 ET
        e2 = (end + dt.timedelta(minutes=1)).astimezone(s.NEW_YORK); st = (e2 - dt.timedelta(days=7)).astimezone(dt.timezone.utc)
        r = s.weekly_p(rows, float(wm.group(1)), st, e2.astimezone(dt.timezone.utc), now, s.weekly_bracket(qn)) if wm else None
        p = r[0] if r else None
    if p is not None and outc == "No":
        p = 1 - p
    p = None if p is None else min(max(p, 0.03), 0.97)
    oc = json.loads(m.get("outcomePrices") or "[]"); won = None
    if oc: won = float(oc[0 if outc == "Yes" else 1])
    gain = sh * ((won or 0) - px)
    flag = "  <== ECART" if p is not None and abs(p - est) > 0.05 else ""
    print(f"{v} {ts[:16]} {mid} {outc:3} prix {px:.3f} est {est:.3f} recalc {('%.3f' % p) if p is not None else '  -  '} issue {won} gain {gain:+.1f} | {qn[:60]}{flag}")
