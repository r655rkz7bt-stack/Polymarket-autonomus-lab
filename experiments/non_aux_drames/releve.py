"""Piste n° 11 (non_aux_drames) : marchés binaires réglés NON sportifs (événements à 1-3 marchés), Gamma.
Usage : releve.py 2026-04-01 2026-10-22 [pas_en_jours] -> donnees/marches.json (ignoré par Git)."""
import json, sys, os, datetime as dt, requests, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
start = dt.date.fromisoformat(sys.argv[1]); end = dt.date.fromisoformat(sys.argv[2])
step = dt.timedelta(days=int(sys.argv[3]) if len(sys.argv) > 3 else 3)
wins = []
d = start
while d < end:
    wins.append((d, min(d + step, end))); d += step

def window(w):
    out = []
    for page in range(80):
        r = None
        for _ in range(3):
            try:
                r = requests.get("https://gamma-api.polymarket.com/events", headers=H, timeout=60, params={
                    "closed": "true", "limit": 100, "offset": page * 100,
                    "end_date_min": f"{w[0]}T00:00:00Z", "end_date_max": f"{w[1]}T00:00:00Z"})
                if r.status_code == 200: break
            except requests.RequestException:
                pass
        b = r.json() if r is not None and r.status_code == 200 else []
        if not isinstance(b, list) or not b:
            break
        for ev in b:
            tags = [t.get("slug") for t in ev.get("tags") or []]
            if "sports" in tags or "games" in tags:
                continue
            ms = ev.get("markets") or []
            if not 1 <= len(ms) <= 3:
                continue
            for m in ms:
                try:
                    toks = json.loads(m.get("clobTokenIds") or "[]"); pr = json.loads(m.get("outcomePrices") or "[]")
                except ValueError:
                    continue
                if len(toks) != 2 or len(pr) != 2 or sorted(pr) != ["0", "1"] and sorted(map(str, map(float, pr))) != ["0.0", "1.0"]:
                    continue
                if m.get("umaResolutionStatus") not in (None, "", "resolved"):
                    continue
                out.append(dict(id=m["id"], ev=ev["id"], q=m.get("question", ""), yes=toks[0], no=toks[1], won_yes=int(float(pr[0]) == 1.0),
                                vol=float(m.get("volume") or 0), start=m.get("startDate"), end=m.get("endDate"), closed=m.get("closedTime"),
                                fs=m.get("feeSchedule"), fees=m.get("feesEnabled"), tags=tags, nmk=len(ms), neg=m.get("negRisk"),
                                desc=(m.get("description") or "")[:300]))
        if len(b) < 100:
            break
    return out

OUT = "experiments/non_aux_drames/donnees/marches.json"
allm = {m["id"]: m for m in json.load(open(OUT))} if os.path.exists(OUT) else {}
with cf.ThreadPoolExecutor(6) as ex:
    for res in ex.map(window, wins):
        for m in res: allm[m["id"]] = m
json.dump(list(allm.values()), open(OUT, "w"))
print(len(allm), "marchés")
