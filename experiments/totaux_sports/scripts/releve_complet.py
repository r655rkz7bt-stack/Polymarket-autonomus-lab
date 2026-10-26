"""27/10/2026 : relevé COMPLET des événements réglés des 37 ligues, par /events/keyset (curseur `after_cursor`).
Défaut trouvé : les relevés du 23 au 26/10 (releve.py, releve_avant.py…) paginaient /events par `offset`, et Gamma refuse tout décalage au-delà de ≈ 2 100
(« offset too large, use /events/keyset ») : le script prenait cette réponse pour la fin de la liste. Résultat : chaque série n'était lue que sur ses ≈ 2 100
événements les plus récents (par date de fin) ; pour ATP, 2 100 événements = seulement du 14/09 au 26/10, et MLB / NFL / tennis / CS2 manquaient presque
entièrement de la fenêtre février-août (« hors échantillon » du 26/10). Voir experiments/enquetes/2026-10-27_releves_tronques_offset.md.
Écrit donnees/totaux_complet.jsonl (un événement par ligne : marchés de totaux, vainqueur, handicaps, jeux/sets). Lancer depuis la racine du dépôt."""
import json, os, time, datetime, requests
from concurrent.futures import ThreadPoolExecutor
SERIES = {"nba": 10345, "nhl": 10346, "mlb": 3, "nfl": 12185, "ncaab": 39, "cfb": 12756, "epl": 10188, "ucl": 10204, "lal": 10193, "bun": 10194,
          "fl1": 10195, "sea": 10203, "mls": 10189, "atp": 10365, "wta": 10366, "itf": 11634, "cs2": 10310, "lol": 10311, "dota2": 10309,
          "val": 10369, "khl": 10700, "euroleague": 10371, "wnba": 10105, "uel": 10209, "cbb": 10470, "elc": 10355, "ere": 10286, "por": 10330,
          "tur": 10292, "bra": 10359, "mex": 10290, "lib": 10289, "ja": 10360, "kor": 10444, "npb": 11968, "kbo": 10370, "ahl": 10699}
TYPES = {"totals", "tennis_match_totals", "tennis_first_set_totals", "first_half_totals", "total_corners", "team_totals", "soccer_team_totals",
         "tennis_set_games_totals", "tennis_set_totals", "moneyline", "tennis_set_handicap", "spreads"}
CUT = datetime.datetime(2026, 1, 15, tzinfo=datetime.timezone.utc)
CHAMPS = ("id", "conditionId", "line", "question", "outcomes", "outcomePrices", "clobTokenIds", "sportsMarketType", "feeSchedule", "feesEnabled",
          "umaResolutionStatus", "volumeNum", "closedTime")
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
OUT = "experiments/totaux_sports/donnees"
os.makedirs(OUT, exist_ok=True)
def jget(params):
    for k in range(6):
        try:
            r = s.get("https://gamma-api.polymarket.com/events/keyset", params=params, timeout=120)
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
with ThreadPoolExecutor(6) as ex, open(f"{OUT}/totaux_complet.jsonl", "w") as f:
    for res in ex.map(pull, SERIES.items()):
        for e in res: f.write(json.dumps(e) + "\n")
