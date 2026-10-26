"""27/10/2026 : début de la saison PRÉCÉDENTE (1er août → 30 novembre 2025) pour les ligues de football : les « Over » des totaux gagnent plus que leur prix depuis
le 15/08/2026 (début de saison) mais pas de février à août (releve_complet.py / analyse_complet.py) ; le même début de saison, un an plus tôt, le confirme-t-il ?
/events/keyset en ordre croissant de date de fin (par défaut) : lecture depuis le plus ancien jusqu'à la date de coupure. Écrit donnees/totaux_2025.jsonl
puis les échanges des marchés de totaux (> 500 $) dans donnees/echanges_2025.jsonl. Lancer depuis la racine du dépôt."""
import json, os, time, datetime, requests
from concurrent.futures import ThreadPoolExecutor
SERIES = {"epl": 10188, "ucl": 10204, "lal": 10193, "bun": 10194, "fl1": 10195, "sea": 10203, "mls": 10189, "uel": 10209, "elc": 10355, "ere": 10286,
          "por": 10330, "tur": 10292, "bra": 10359, "mex": 10290, "lib": 10289, "ja": 10360, "kor": 10444}
A = datetime.datetime(2025, 8, 1, tzinfo=datetime.timezone.utc); B = datetime.datetime(2025, 12, 1, tzinfo=datetime.timezone.utc)
CHAMPS = ("id", "conditionId", "line", "question", "outcomes", "outcomePrices", "clobTokenIds", "sportsMarketType", "feeSchedule", "feesEnabled",
          "umaResolutionStatus", "volumeNum", "closedTime")
D = "experiments/totaux_sports/donnees"
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def jget(url, params):
    for k in range(6):
        try:
            r = s.get(url, params=params, timeout=120)
            if r.status_code == 200: return r.json()
        except Exception:
            pass
        time.sleep(2 ** k)
    return None
def start_of(e):
    for m in e.get("markets") or []:
        if m.get("gameStartTime"):
            return datetime.datetime.fromisoformat(m["gameStartTime"].replace("+00", "+00:00").replace("Z", "+00:00"))
def pull(item):
    name, sid = item
    out, cursor = [], None
    while True:
        p = {"series_id": sid, "closed": "true", "limit": 100}
        if cursor: p["after_cursor"] = cursor
        d = jget("https://gamma-api.polymarket.com/events/keyset", p)
        if not d or not d.get("events"): break
        stop = False
        for e in d["events"]:
            st = start_of(e)
            if st is None: continue
            if st >= B: stop = True
            if not (A <= st < B): continue
            mk = [m for m in e.get("markets") or [] if m.get("sportsMarketType") == "totals"]
            if mk: out.append({"sport": name, "id": e["id"], "title": e.get("title"), "start": st.isoformat(), "markets": [{k: m.get(k) for k in CHAMPS} for m in mk]})
        cursor = d.get("next_cursor")
        if stop or not cursor: break
    print(name, len(out), flush=True)
    return out
if __name__ == "__main__":
    if not os.path.exists(f"{D}/totaux_2025.jsonl"):
        with ThreadPoolExecutor(6) as ex, open(f"{D}/totaux_2025.jsonl", "w") as f:
            for res in ex.map(pull, SERIES.items()):
                for e in res: f.write(json.dumps(e) + "\n")
    marches = [m["conditionId"] for l in open(f"{D}/totaux_2025.jsonl") for m in json.loads(l)["markets"]
               if (m.get("volumeNum") or 0) >= 500 and m.get("umaResolutionStatus") == "resolved"]
    print(len(marches), "marchés à relever", flush=True)
    def get(c):
        out = []
        for page in range(6):
            b = jget("https://data-api.polymarket.com/trades", {"market": c, "limit": 1000, "offset": page * 1000})
            if not isinstance(b, list): return None
            out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp") and t.get("price") is not None]
            if len(b) < 1000: break
        return {"m": c, "trades": out}
    with open(f"{D}/echanges_2025.jsonl", "w") as f, ThreadPoolExecutor(6) as ex:
        for i, o in enumerate(ex.map(get, marches)):
            if o: f.write(json.dumps(o) + "\n")
