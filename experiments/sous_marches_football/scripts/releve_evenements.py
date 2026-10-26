"""Piste « sous-marchés du football » (26/10/2026) : événements de football réglés depuis le 01/02, marchés « moneyline » (1X2 : victoire A,
nul, victoire B) et « soccer_halftime_result » (mi-temps). Écrit donnees/events.jsonl. À lancer depuis experiments/sous_marches_football/.
Adapté de experiments/totaux_sports/scripts/releve_avant.py."""
import json, os, time, datetime, requests
from concurrent.futures import ThreadPoolExecutor
SERIES = {"epl": 10188, "ucl": 10204, "lal": 10193, "bun": 10194, "fl1": 10195, "sea": 10203, "mls": 10189, "uel": 10209, "elc": 10355,
          "ere": 10286, "por": 10330, "tur": 10292, "bra": 10359, "mex": 10290, "lib": 10289, "ja": 10360, "kor": 10444}
TYPES = {"moneyline", "soccer_halftime_result"}
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
                mk = [m for m in e.get("markets") or [] if m.get("sportsMarketType") in TYPES]
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
