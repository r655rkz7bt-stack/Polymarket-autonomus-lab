"""27/10/2026 : relevé par ÉTIQUETTES (IA, tech, OpenAI, Claude…) des marchés « d'ici / avant <date> » réglés depuis le 01/01/2025, et de leurs échanges réels.
/events/keyset?tag_id=… (curseur, jamais offset). Sortie : donnees/marches_tags.jsonl (même format que releve.py) ; les échanges vont dans donnees/echanges/ (cache commun)."""
import json, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, "experiments/decroissance_passe/scripts")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
import releve as R
TAGS = [439, 537, 103303, 101999, 1401]
SINCE = "2025-01-01"
def lire(tag):
    out, cur = [], None
    while True:
        p = {"tag_id": tag, "closed": "true", "limit": 100, "order": "endDate", "ascending": "false"}
        if cur: p["after_cursor"] = cur
        d = R.s.get("https://gamma-api.polymarket.com/events/keyset", params=p, timeout=120).json()
        ev = d.get("events") or []
        if not ev: break
        out += ev; cur = d.get("next_cursor")
        if not cur or (ev[-1].get("endDate") and ev[-1]["endDate"][:10] < SINCE and len(out) > 300): break
    return out
if __name__ == "__main__":
    got = {}
    with ThreadPoolExecutor(5) as ex:
        for evs in ex.map(lire, TAGS):
            for e in evs:
                if (e.get("endDate") or "9") [:10] < SINCE: continue
                g = R.garder(e)
                if g: got[e["id"]] = g
    print("événements", len(got), "marchés", sum(len(e["markets"]) for e in got.values()), flush=True)
    with open(R.OUT / "marches_tags.jsonl", "w") as f:
        for e in got.values(): f.write(json.dumps(e) + "\n")
    http = HttpClient(min_interval=0.03)
    def un(e): it.fetch_event_trades(http, R.OUT / "echanges", str(e["id"])); return 1
    with ThreadPoolExecutor(16) as ex: print("échanges", sum(ex.map(un, got.values())), flush=True)
