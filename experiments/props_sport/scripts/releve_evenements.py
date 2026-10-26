"""Piste « props de joueurs » (26/10/2026) : événements réglés depuis le 01/02 des grandes ligues américaines ; garde tous les marchés Over/Under qui ne sont pas
des totaux déjà testés (points, rebonds, passes, yards, réceptions… des joueurs). Écrit donnees/events.jsonl. À lancer depuis experiments/props_sport/."""
import json, os, time, datetime, requests
from concurrent.futures import ThreadPoolExecutor
SERIES = {"nba": 10345, "nhl": 10346, "mlb": 3, "nfl": 12185, "ncaab": 39, "cfb": 12756, "wnba": 10105}
DEJA = {"totals", "tennis_match_totals", "tennis_first_set_totals", "first_half_totals", "total_corners", "team_totals", "soccer_team_totals", "tennis_set_games_totals", "second_half_totals"}
CUT = datetime.datetime(2026, 2, 1, tzinfo=datetime.timezone.utc)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
os.makedirs("donnees", exist_ok=True)
def jget(params):
    for k in range(5):
        try:
            return s.get("https://gamma-api.polymarket.com/events", params=params, timeout=60).json()
        except Exception:
            time.sleep(2 ** k)
    return None
def start_of(e):
    for m in e.get("markets") or []:
        if m.get("gameStartTime"):
            return datetime.datetime.fromisoformat(m["gameStartTime"].replace("+00", "+00:00").replace("Z", "+00:00"))
    return None
def pull(item):
    name, sid = item
    out, off = [], 0
    while off < 30000:
        b = jget({"series_id": sid, "closed": "true", "order": "endDate", "ascending": "false", "limit": 100, "offset": off})
        if not isinstance(b, list) or not b: break
        for e in b:
            st = start_of(e)
            if st and st >= CUT:
                mk = [m for m in e.get("markets") or [] if m.get("sportsMarketType") not in DEJA and "over" in str(m.get("outcomes")).lower() and (m.get("volumeNum") or 0) >= 1000]
                if mk:
                    out.append({"sport": name, "id": e["id"], "title": e.get("title"), "start": st.isoformat(), "markets": [
                        {k: m.get(k) for k in ("id", "conditionId", "question", "groupItemTitle", "outcomes", "outcomePrices", "clobTokenIds", "sportsMarketType",
                                               "feeSchedule", "feesEnabled", "umaResolutionStatus", "volumeNum")} for m in mk]})
        off += 100
        if len(b) < 100: break
    return out
if not os.path.exists("donnees/events.jsonl"):
    with ThreadPoolExecutor(6) as ex, open("donnees/events.jsonl", "w") as f:
        for res in ex.map(pull, SERIES.items()):
            for e in res: f.write(json.dumps(e) + "\n")
ev = [json.loads(l) for l in open("donnees/events.jsonl")]
print("événements", len(ev), "marchés", sum(len(e["markets"]) for e in ev))
