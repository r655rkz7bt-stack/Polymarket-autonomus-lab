"""28/10/2026 : relevé des marchés de JOUEURS du football (tirs, tirs cadrés, buteur, passes décisives, arrêts, buts+passes) et des scores exacts,
événements réglés des 14 ligues de football, par /events/keyset (curseur). Écrit donnees/props_evenements.jsonl. Lancer depuis la racine du dépôt."""
import json, os, time, datetime, requests
from concurrent.futures import ThreadPoolExecutor
SERIES = {"epl": 10188, "ucl": 10204, "lal": 10193, "bun": 10194, "fl1": 10195, "sea": 10203, "mls": 10189, "uel": 10209, "elc": 10355, "ere": 10286,
          "por": 10330, "tur": 10292, "bra": 10359, "mex": 10290, "lib": 10289, "ja": 10360, "kor": 10444}
TYPES = {"soccer_player_shots", "soccer_player_shots_on_target", "soccer_player_assists", "soccer_player_goals_plus_assists", "soccer_player_goals",
         "soccer_anytime_goalscorer", "soccer_player_goalkeeper_saves", "soccer_first_to_score", "soccer_exact_score", "soccer_team_total_corners",
         "soccer_first_half_team_totals", "soccer_team_totals"}
CUT = datetime.datetime(2026, 1, 15, tzinfo=datetime.timezone.utc)
CHAMPS = ("id", "conditionId", "line", "question", "groupItemTitle", "outcomes", "outcomePrices", "clobTokenIds", "sportsMarketType", "feeSchedule", "feesEnabled",
          "umaResolutionStatus", "volumeNum", "closedTime")
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
OUT = "experiments/props_football/donnees"
def jget(params):
    for k in range(6):
        try:
            r = s.get("https://gamma-api.polymarket.com/events/keyset", params=params, timeout=120)
            if r.status_code == 200: return r.json()
        except Exception:
            pass
        time.sleep(2 ** k)
def start_of(e):
    for m in e.get("markets") or []:
        if m.get("gameStartTime"):
            return datetime.datetime.fromisoformat(m["gameStartTime"].replace("+00", "+00:00").replace("Z", "+00:00"))
def pull(item):
    name, sid = item
    out, cursor, vieux, vus = [], None, 0, 0
    while True:
        p = {"series_id": sid, "closed": "true", "limit": 100, "order": "endDate", "ascending": "false"}
        if cursor: p["after_cursor"] = cursor
        d = jget(p)
        if not d or not d.get("events"): break
        for e in d["events"]:
            vus += 1
            st = start_of(e)
            if st is None: continue
            vieux = vieux + 1 if st < CUT else 0
            if st < CUT: continue
            mk = [m for m in e.get("markets") or [] if m.get("sportsMarketType") in TYPES]
            if not mk: continue
            out.append({"sport": name, "id": e["id"], "title": e.get("title"), "start": st.isoformat(),
                        "markets": [{k: m.get(k) for k in CHAMPS} for m in mk]})
        cursor = d.get("next_cursor")
        if not cursor or vieux > 1500: break
    print(name, vus, "événements lus,", len(out), "gardés", flush=True)
    return out
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(6) as ex, open(f"{OUT}/props_evenements.jsonl", "w") as f:
        for res in ex.map(pull, SERIES.items()):
            for e in res: f.write(json.dumps(e) + "\n")
