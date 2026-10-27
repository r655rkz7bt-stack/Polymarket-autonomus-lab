"""27/10/2026 (soir) : relevé des marchés « d'ici / avant <date> » réglés depuis le 01/02/2026 (hors sport) et de leurs échanges réels.
Gamma /events/keyset par fenêtres de 3 jours sur la date de fin (curseur, JAMAIS offset : voir enquetes/2026-10-27_releves_tronques_offset.md),
fenêtre ouverte vers le futur pour les événements réglés avant leur date de fin. Puis data-api (échanges par événement, cache gzip).
Sortie : donnees/marches.jsonl, donnees/echanges/. Lancer depuis la racine du dépôt."""
import json, re, sys, time, datetime as dt, requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
OUT = Path("experiments/decroissance_passe/donnees"); (OUT / "echanges").mkdir(parents=True, exist_ok=True)
D0 = dt.datetime(2026, 2, 1, tzinfo=dt.timezone.utc); D1 = dt.datetime(2026, 10, 28, tzinfo=dt.timezone.utc)
FUTUR = "2099-01-01T00:00:00Z"
DEADLINE = re.compile(r"\b(by|before)\b", re.I)
CHAMPS = ("id", "conditionId", "question", "outcomes", "outcomePrices", "clobTokenIds", "endDate", "startDate", "feeSchedule", "volumeNum",
          "umaResolutionStatus", "closedTime", "sportsMarketType", "groupItemTitle")
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def jget(p):
    for k in range(6):
        try:
            r = s.get("https://gamma-api.polymarket.com/events/keyset", params=p, timeout=120)
            if r.status_code == 200: return r.json()
        except Exception: pass
        time.sleep(2 ** k)
    return None
def fenetre(a):
    b = a + dt.timedelta(days=3); got = []; cur = None
    while True:
        p = dict(closed="true", limit=100, order="endDate", ascending="true", end_date_min=a.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 end_date_max=b.strftime("%Y-%m-%dT%H:%M:%SZ"))
        if cur: p["after_cursor"] = cur
        d = jget(p)
        if not d or not d.get("events"): break
        got += d["events"]; cur = d.get("next_cursor")
        if not cur: break
    return got
def garder(e):
    mk = [m for m in e.get("markets") or [] if DEADLINE.search(m.get("question") or "") and not m.get("sportsMarketType")
          and float(m.get("volumeNum") or 0) >= 3000]
    if not mk: return None
    return {"id": e["id"], "title": e.get("title"), "end": e.get("endDate"), "markets": [{k: m.get(k) for k in CHAMPS} for m in mk]}
if __name__ == "__main__":
    fen = []; a = D0
    while a < D1: fen.append(a); a += dt.timedelta(days=3)
    out = {}; vus = 0
    with ThreadPoolExecutor(8) as ex:
        for evs in ex.map(fenetre, fen):
            for e in evs:
                vus += 1; g = garder(e)
                if g: out[e["id"]] = g
    # événements réglés AVANT leur date de fin (fin Gamma dans le futur)
    cur = None
    while True:
        p = dict(closed="true", limit=100, order="endDate", ascending="true", end_date_min=D1.strftime("%Y-%m-%dT%H:%M:%SZ"), end_date_max=FUTUR)
        if cur: p["after_cursor"] = cur
        d = jget(p)
        if not d or not d.get("events"): break
        for e in d["events"]:
            vus += 1; g = garder(e)
            if g: out[e["id"]] = g
        cur = d.get("next_cursor")
        if not cur: break
    print("événements lus", vus, "gardés", len(out), "marchés", sum(len(e["markets"]) for e in out.values()), flush=True)
    with open(OUT / "marches.jsonl", "w") as f:
        for e in out.values(): f.write(json.dumps(e) + "\n")
    http = HttpClient(min_interval=0.03)
    def un(e): it.fetch_event_trades(http, OUT / "echanges", str(e["id"])); return 1
    with ThreadPoolExecutor(16) as ex: n = sum(ex.map(un, out.values()))
    print("échanges", n, flush=True)
