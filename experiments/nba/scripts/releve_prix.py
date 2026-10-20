"""Rattache marchés et matchs NBA, calcule le repos de chaque équipe (calendrier complet) et relève le prix
juste avant le coup d'envoi (CLOB prices-history, pas de 10 min) → donnees/rows.json."""
import json, time, requests
from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor
D = "donnees"
games = json.load(open(f"{D}/matchs.json")); mk = json.load(open(f"{D}/marches.json"))
played = {}
for g in games:
    for t in (g["away"], g["home"]):
        played.setdefault(t, []).append(g["date"])
for t in played: played[t].sort()
def repos(team, d):
    prev = [x for x in played[team] if x < d]
    last = date.fromisoformat(prev[-1]) if prev else None
    dd = date.fromisoformat(d)
    n4 = sum(1 for x in prev if (dd - date.fromisoformat(x)).days <= 3)   # matchs dans les 3 jours précédents (3 en 4 jours = 2 ici)
    return ((dd - last).days if last else 9), n4
by = {}
for e in mk:
    by.setdefault(e["slug"][-10:], []).append(e)
rows = []
for g in games:
    for e in by.get(g["date"], []):
        o = json.loads(e["outcomes"])
        a_ok = [g["away"].endswith(o[0]), g["home"].endswith(o[1])]; b_ok = [g["away"].endswith(o[1]), g["home"].endswith(o[0])]
        if all(a_ok): flip = 0
        elif all(b_ok): flip = 1
        else: continue
        res = json.loads(e["res"])
        away_win = g["pa"] > g["ph"]
        # contrôle du règlement : le jeton « équipe visiteuse » doit valoir 1 si le visiteur a gagné
        pay_away = float(res[flip])
        rows.append({"date": g["date"], "away": g["away"], "home": g["home"], "away_win": away_win, "settle_ok": (pay_away == 1.0) == away_win,
                     "rest_away": repos(g["away"], g["date"]), "rest_home": repos(g["home"], g["date"]),
                     "tok_away": json.loads(e["tok"])[flip], "start": e["start"], "slug": e["slug"], "volume": e["volume"]})
print("rattachés", len(rows), "sur", len(games), "| règlement cohérent", sum(r["settle_ok"] for r in rows), flush=True)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def hist(r):
    st = int(datetime.fromisoformat(r["start"].replace("+00", "+00:00")).timestamp())
    for k in range(4):
        try:
            h = s.get("https://clob.polymarket.com/prices-history", params={"market": r["tok_away"], "startTs": st - 12 * 3600, "endTs": st, "fidelity": 10}, timeout=40).json()
            r["hist"] = h.get("history") or []; r["st"] = st; return
        except Exception: time.sleep(2 ** k)
    r["hist"] = []; r["st"] = st
with ThreadPoolExecutor(5) as ex: list(ex.map(hist, rows))
json.dump(rows, open(f"{D}/rows.json", "w"))
print("avec prix", sum(1 for r in rows if r["hist"]), flush=True)
