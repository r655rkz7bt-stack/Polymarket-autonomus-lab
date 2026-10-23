"""Piste n° 1 (score_exact_poisson), étape 2 : pour un ÉCHANTILLON de matchs « score exact » (tirage fixe, au plus N par
mois), relève le match lui-même (Gamma : vainqueur domicile / nul / extérieur) et ses « autres marchés » (plus/moins de
1,5 / 2,5 / 3,5 buts), puis les ÉCHANGES RÉELS (data-api) :
  - du score exact (par événement : peu d'échanges) ;
  - des 3 marchés vainqueur et des totaux (par marché, échanges d'au moins 5 $ seulement, pour remonter avant le
    coup d'envoi malgré la limite de 10 000 de la data-api).
Seuls les matchs dont au moins un score exact a un volume > 0 sont tirés (sans volume, aucun échange, aucun pari).
Usage : python experiments/score_exact_poisson/releve_matchs.py <N par mois>
    -> donnees/matchs.json.gz, donnees/echanges/*.json.gz (ignorés par Git)"""
import gzip
import json
import random
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bo3_coherence"))
from echanges import en_parallele  # noqa: E402

D = HERE / "donnees"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
S = requests.Session()
S.headers["User-Agent"] = "polymarket-autonomous-lab"
marches = json.loads(gzip.decompress((D / "marches_score_exact.json.gz").read_bytes()))
par_ev = defaultdict(list)
for m in marches:
    if m.get("event_slug", "").endswith("-exact-score"):
        par_ev[m["event_id"]].append(m)
par_mois = defaultdict(list)
for eid, ms in par_ev.items():
    if any((m.get("volumeNum") or 0) > 0 for m in ms) and ms[0].get("gameStartTime"):
        par_mois[ms[0]["gameStartTime"][:7]].append(eid)
print("matchs « score exact » réglés :", len(par_ev), "; avec volume > 0 :", sum(len(v) for v in par_mois.values()),
      "; par mois :", {k: len(v) for k, v in sorted(par_mois.items())}, flush=True)
rng = random.Random(7)
choisis = []
for k in sorted(par_mois):
    ids = sorted(par_mois[k])
    rng.shuffle(ids)
    choisis += ids[:N]


def gamma(slug):
    for k in range(5):
        try:
            r = S.get("https://gamma-api.polymarket.com/events", params={"slug": slug}, timeout=60)
            if r.status_code == 200:
                d = r.json()
                return d[0] if d else None
        except requests.RequestException:
            pass
        time.sleep(2 ** k)
    return None


CH = ("id", "conditionId", "question", "outcomes", "outcomePrices", "clobTokenIds", "volumeNum", "feesEnabled", "feeSchedule",
      "sportsMarketType", "line", "gameStartTime", "umaResolutionStatus", "groupItemTitle")


def un(eid):
    base = par_ev[eid][0]["event_slug"][: -len("-exact-score")]
    parent, autres = gamma(base), gamma(base + "-more-markets")
    pick = lambda e: [{k: m.get(k) for k in CH} for m in (e or {}).get("markets") or []]
    return {"event": eid, "slug": base, "start": par_ev[eid][0]["gameStartTime"], "scores": par_ev[eid],
            "parent_id": (parent or {}).get("id"), "vainqueur": pick(parent), "autres": pick(autres)}


path = D / "matchs.json.gz"
if path.exists():
    matchs = json.loads(gzip.decompress(path.read_bytes()))
else:
    with ThreadPoolExecutor(4) as ex:
        matchs = list(ex.map(un, choisis))
    path.write_bytes(gzip.compress(json.dumps(matchs).encode()))
print("matchs tirés", len(matchs), "; avec vainqueur", sum(1 for m in matchs if m["vainqueur"]),
      "; avec plus/moins 2,5", sum(1 for m in matchs if any(x.get("sportsMarketType") == "totals" and x.get("line") == 2.5 for x in m["autres"])), flush=True)
taches = []
for m in matchs:
    taches.append((f"es_{m['event']}", {"eventId": m["event"]}))
    cids = [x["conditionId"] for x in m["vainqueur"] if x.get("sportsMarketType") == "moneyline"]
    cids += [x["conditionId"] for x in m["autres"] if x.get("sportsMarketType") == "totals" and x.get("line") in (1.5, 2.5, 3.5)]
    if cids:
        taches.append((f"in_{m['event']}", {"market": ",".join(cids), "filterType": "CASH", "filterAmount": 5}))
res = en_parallele(taches, D / "echanges", fils=8)
print("fini :", sum(1 for v in res.values() if v is not None), "listes lues ;", sum(1 for v in res.values() if v and len(v) >= 11000), "tronquées")
