"""Vague de volume, étape 1 : marchés OUI/NON réglés (Gamma /markets), toutes familles.

Usage : PYTHONPATH=src python experiments/vague_volume_backtest/releve_marches.py 2026-07-15 2026-10-15
Fenêtres d'un jour sur l'échéance annoncée (`endDate`), volume total ≥ 20 000 $ (`volume_num_min`, filtre
côté Gamma : /events renvoie plus de 2 100 événements et 6 Mo par page de 100 un seul jour). Lecture du
règlement : `idea_test.parse_event_market` (binaire réglé net à 1/0, UMA « resolved », barème de frais).
On garde seulement les issues littéralement « Yes »/« No » (règle `_yes_no` de la stratégie en direct) et
les marchés qui ont pu offrir au moins une décision : âge ≥ 3 jours ET échéance réelle ≥ 48 h après.
Échéance réelle : `gameStartTime` pour un match (l'`endDate` d'un match est une date fictive), sinon `endDate`.
-> donnees/marches.json (ignoré par Git)."""
import concurrent.futures as cf
import datetime as dt
import json
import sys
from pathlib import Path

import requests

from polymarket_agent import idea_test as it

H = {"User-Agent": "curl/8"}
OUT = Path("experiments/vague_volume_backtest/donnees/marches.json")
start, end = dt.date.fromisoformat(sys.argv[1]), dt.date.fromisoformat(sys.argv[2])
MIN_VOL = float(sys.argv[3]) if len(sys.argv) > 3 else 20000


def ts(s):
    if not s:
        return None
    s = str(s).replace(" ", "T")
    if s.endswith("+00"):
        s += ":00"
    try:
        return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def family(tags):
    t = set(tags)
    if "sports" in t or "esports" in t or "games" in t:
        return "sport"
    if "crypto" in t or "crypto-prices" in t:
        return "crypto"
    if t & {"politics", "elections", "geopolitics", "us-politics", "world-elections", "global-elections", "trump"}:
        return "politique"
    return "autres"


def day(d):
    rows, seen = [], 0
    for off in range(0, 2100, 100):
        for attempt in range(4):
            try:
                r = requests.get("https://gamma-api.polymarket.com/markets", headers=H, timeout=60, params=dict(
                    closed="true", limit=100, offset=off, end_date_min=f"{d}T00:00:00Z",
                    end_date_max=f"{d}T23:59:59Z", volume_num_min=MIN_VOL, include_tag="true"))
                b = r.json() if r.status_code == 200 else None
                if isinstance(b, list):
                    break
            except (requests.RequestException, ValueError):
                pass
            import time; time.sleep(2 ** attempt)
        else:
            print("échec", d, off, flush=True); break
        seen += len(b)
        for m in b:
            ev = (m.get("events") or [{}])[0]
            outs = [str(o).lower() for o in it._jl(m.get("outcomes"))]
            if outs != ["yes", "no"]:
                continue
            r_ = it.parse_event_market(ev, m)
            if r_ is None:
                continue
            tags = [t.get("slug") for t in m.get("tags") or []]
            created, game = ts(m.get("createdAt")), ts(m.get("gameStartTime"))
            deadline = game or r_.end
            closed = ts(m.get("closedTime")) or r_.end
            if created is None or deadline - created < 5 * 86400 or closed - created < 3 * 86400:
                continue
            toks = [str(t) for t in it._jl(m.get("clobTokenIds"))]
            fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
            r_.extra = dict(no_token=toks[1], condition=m.get("conditionId"), created=created, game=game,
                            deadline=deadline, closed=closed, volume=float(m.get("volumeNum") or 0), tags=tags,
                            famille=family(tags), exposant=fs.get("exponent"))
            rows.append(r_.__dict__)
        if len(b) < 100:
            break
    return d, seen, rows


days = [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
allm, total = {}, 0
with cf.ThreadPoolExecutor(6) as ex:
    for d, seen, rows in ex.map(day, days):
        total += seen
        for r in rows:
            allm[r["market_id"]] = r
        if seen >= 2100:
            print("ATTENTION : fenêtre pleine", d, flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(list(allm.values())))
from collections import Counter
print(total, "marchés ≥", MIN_VOL, "$ lus ;", len(allm), "gardés (OUI/NON, réglés, ≥ 5 jours de vie utile) ;",
      len({r["event_id"] for r in allm.values()}), "événements")
print(Counter(r["extra"]["famille"] for r in allm.values()))
