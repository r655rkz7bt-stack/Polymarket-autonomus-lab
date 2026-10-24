"""Échanges réels (data-api, preneurs) des 189 périodes de donnees/xt/marches.json + jetons OUI/NON de chaque tranche
(donnees/xt/jetons.json) : donnees/xt/cache/echanges_<id>.json.gz. PYTHONPATH=src, depuis la racine."""
import json, time, requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from polymarket_agent import idea_test as it
from polymarket_agent.http_client import HttpClient
D = Path("donnees/xt")
slugs = [e["slug"] for e in json.load(open(D / "marches.json"))]
http = HttpClient(timeout=40, min_interval=0.0, user_agent="curl/8")
def go(slug):
    for k in range(4):
        try:
            ev = requests.get("https://gamma-api.polymarket.com/events", params={"slug": slug}, headers={"User-Agent": "curl/8"}, timeout=40).json()[0]
            break
        except Exception:
            time.sleep(2 ** k)
    else:
        return slug, None
    toks = {m["groupItemTitle"]: json.loads(m["clobTokenIds"]) for m in ev["markets"] if m.get("clobTokenIds")}
    n = len(it.fetch_event_trades(http, D / "cache", str(ev["id"])))
    print(slug, ev["id"], n, flush=True)
    return slug, {"id": str(ev["id"]), "jetons": toks, "echanges": n}
with ThreadPoolExecutor(6) as ex:
    out = dict(r for r in ex.map(go, slugs) if r[1])
json.dump(out, open(D / "jetons.json", "w"))
print(len(out), "événements")
