"""Piste « après la fin du match » (23/10/2026) : combien d'heures après le coup d'envoi un favori à 0,94-0,985 est-il vraiment gagné ?
Relève, pour les principales ligues, les événements réglés depuis le 30/09 (Gamma, series_id) puis leurs vrais échanges (data-api).
Écrit donnees/events.jsonl et donnees/echanges.jsonl ; à lancer depuis experiments/apres_fin_match/. Reprend où il s'est arrêté."""
import json, os, time, datetime, requests
from concurrent.futures import ThreadPoolExecutor
SERIES = {"nba": 10345, "nhl": 10346, "mlb": 3, "nfl": 12185, "ncaab": 39, "cfb": 12756, "epl": 10188, "ucl": 10204, "lal": 10193, "bun": 10194,
          "fl1": 10195, "sea": 10203, "mls": 10189, "atp": 10365, "wta": 10366, "itf": 11634, "cs2": 10310, "lol": 10311, "dota2": 10309,
          "val": 10369, "khl": 10700, "euroleague": 10371, "wnba": 10105, "uel": 10209, "cbb": 10470, "elc": 10355, "ere": 10286, "por": 10330,
          "tur": 10292, "bra": 10359, "mex": 10290, "lib": 10289, "ja": 10360, "kor": 10444, "npb": 11968, "kbo": 10370, "ahl": 10699}
CUT = datetime.datetime(2026, 9, 30, tzinfo=datetime.timezone.utc)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
os.makedirs("donnees", exist_ok=True)
def jget(url, params):
    for k in range(5):
        try:
            return s.get(url, params=params, timeout=60).json()
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
    out, off, empty_pages = [], 0, 0
    while off < 6000:
        b = jget("https://gamma-api.polymarket.com/events", {"series_id": sid, "closed": "true", "order": "endDate", "ascending": "false", "limit": 100, "offset": off})
        if not isinstance(b, list) or not b: break
        keep = []
        for e in b:
            st = start_of(e)
            if st and st >= CUT:
                keep.append({"sport": name, "id": e["id"], "title": e.get("title"), "start": st.isoformat(), "markets": [
                    {k: m.get(k) for k in ("id", "question", "outcomes", "outcomePrices", "clobTokenIds", "sportsMarketType", "feeSchedule", "feesEnabled", "umaResolutionStatus", "volumeNum")}
                    for m in e.get("markets") or []]})
        out += keep
        empty_pages = empty_pages + 1 if not keep else 0
        if empty_pages >= 3: break
        off += 100
        if len(b) < 100: break
    return out
if not os.path.exists("donnees/events.jsonl"):
    with ThreadPoolExecutor(6) as ex, open("donnees/events.jsonl", "w") as f:
        for res in ex.map(pull, SERIES.items()):
            for e in res: f.write(json.dumps(e) + "\n")
events = [json.loads(l) for l in open("donnees/events.jsonl")]
print("événements", len(events), flush=True)
done = set()
if os.path.exists("donnees/echanges.jsonl"): done = {json.loads(l)["event"] for l in open("donnees/echanges.jsonl")}
todo = [e["id"] for e in events if e["id"] not in done]
if os.environ.get("REV"): todo = todo[::-1]
def get(eid):
    out = []
    for page in range(10):
        b = jget("https://data-api.polymarket.com/trades", {"eventId": eid, "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list): return None
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
        if len(b) < 1000: break
    return {"event": eid, "trades": out}
with open("donnees/echanges.jsonl", "a") as f, ThreadPoolExecutor(6) as ex:
    for i, o in enumerate(ex.map(get, todo)):
        if o: f.write(json.dumps(o) + "\n"); f.flush()
        if i % 200 == 0: print(i, "/", len(todo), flush=True)
