"""Backtest météo, étape 1 : collecte (marchés résolus, coordonnées, prévisions passées, prix d'avant)."""
# Données attendues : <dossier>/bt/ev_*.json, pages de https://gamma-api.polymarket.com/events?tag_id=84&closed=true&end_date_min=...&end_date_max=...&limit=100&offset=N
import glob, json, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
SP = sys.argv[1]
sys.path.insert(0, sys.argv[2])
from polymarket_agent import weather_model as wm

def get(url, params, tries=3):
    q = url + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers={"User-Agent": "polymarket-lab-backtest"}), timeout=40) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            time.sleep(1 + i * 2); err = e
    print("échec", q[:120], err); return None

evs = [e for f in glob.glob(f"{SP}/bt/ev_*.json") for e in json.load(open(f))]
rows = []
for e in evs:
    if not re.match(r"(highest|lowest)-temperature-in-", e["slug"]): continue
    for m in e.get("markets", []):
        st = re.search(r"site=([a-z0-9]{3,5})", m.get("resolutionSource") or "", re.I) or re.search(r"site=([a-z0-9]{3,5})", m.get("description") or "", re.I)
        q = wm.parse_question(m.get("question", ""))
        try: prices = [float(x) for x in json.loads(m["outcomePrices"])]; toks = json.loads(m["clobTokenIds"])
        except Exception: continue
        if not st or not q or m.get("umaResolutionStatus") not in (None, "", "resolved") or sorted(prices) != [0.0, 1.0]: continue
        rows.append({"q": m["question"], "station": st.group(1).upper(), "yes": toks[0], "won": prices[0], "event": e["slug"],
                     "kind": q.kind, "date": f"2026-{q.month:02d}-{q.day:02d}", "fee": m.get("feeSchedule"), "fees_on": m.get("feesEnabled")})
print(len(rows), "marchés résolus utilisables")
stations = sorted({r["station"] for r in rows})
ll = {}
for i in range(0, len(stations), 30):
    for x in get("https://aviationweather.gov/api/data/metar", {"ids": ",".join(stations[i:i+30]), "format": "json", "hours": 3}) or []:
        ll[x["icaoId"].upper()] = (x["lat"], x["lon"])
print(len(stations), "stations", len(ll), "localisées", sorted(set(stations) - set(ll)))
fc = {}
st_ok = [s for s in stations if s in ll]
for i in range(0, len(st_ok), 10):
    chunk = st_ok[i:i+10]
    res = get("https://previous-runs-api.open-meteo.com/v1/forecast", {
        "latitude": ",".join(str(ll[s][0]) for s in chunk), "longitude": ",".join(str(ll[s][1]) for s in chunk),
        "hourly": "temperature_2m_previous_day1,temperature_2m_previous_day2", "models": "gfs_seamless,ecmwf_ifs025",
        "start_date": "2026-09-30", "end_date": "2026-10-16", "timezone": "auto"})
    res = res if isinstance(res, list) else [res]
    for s, r in zip(chunk, res):
        if r: fc[s] = r
print(len(fc), "prévisions")
# Prix du « Oui » au début du jour local (et 24 h avant).
def price_at(token, ts):
    h = get("https://clob.polymarket.com/prices-history", {"market": token, "startTs": ts - 6 * 3600, "endTs": ts, "fidelity": 10})
    pts = [p for p in (h or {}).get("history", []) if p["t"] <= ts]
    return pts[-1]["p"] if pts else None
def job(r):
    f = fc.get(r["station"])
    if not f: return r
    off = f["utc_offset_seconds"]
    d0 = datetime.fromisoformat(r["date"]).replace(tzinfo=timezone.utc) - timedelta(seconds=off)
    r["t0"] = int(d0.timestamp()); r["offset"] = off
    r["p0"] = price_at(r["yes"], r["t0"]); r["p_1"] = price_at(r["yes"], r["t0"] - 86400)
    return r
with ThreadPoolExecutor(6) as ex: rows = list(ex.map(job, rows))
json.dump({"rows": rows, "fc": fc, "ll": ll}, open(f"{SP}/bt/data.json", "w"))
print("prix trouvés :", sum(1 for r in rows if r.get("p0") is not None), "/", len(rows))
