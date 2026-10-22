"""Piste n° 11 (non_aux_drames), étape 1 : relevé des marchés RÉGLÉS à longue échéance (Gamma, public, gratuit).

Usage : .venv/bin/python experiments/non_aux_drames/releve_marches.py 2024-01-01 2026-10-20
On lit tous les marchés clos dont l'échéance tombe dans la période (fenêtres de 10 jours, au moins
5 000 $ échangés), et on ne garde que ceux qui ont vécu au moins 30 jours (création → échéance) :
le sport et la crypto du jour disparaissent d'eux-mêmes. Le tri « drame ou pas » se fait plus tard
(selection.py), avec une liste de mots fixée AVANT de regarder les résultats.
Sortie : donnees/marches.jsonl (ignoré par Git), une ligne par marché, relancer complète le fichier.
"""
import concurrent.futures as cf
import datetime as dt
import json
import os
import sys
import time

import requests

H = {"User-Agent": "polymarket-autonomous-lab (etude)"}
OUT = "experiments/non_aux_drames/donnees/marches.jsonl"
start, end = dt.date.fromisoformat(sys.argv[1]), dt.date.fromisoformat(sys.argv[2])


def ts(text):
    if not text:
        return None
    try:
        return int(dt.datetime.fromisoformat(str(text).replace("Z", "+00:00").replace(" ", "T")).timestamp())
    except ValueError:
        try:  # « 2025-01-10 18:27:54+00 »
            return int(dt.datetime.strptime(str(text)[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp())
        except ValueError:
            return None


def window(a, b):
    out = []
    for page in range(40):
        for essai in range(4):
            try:
                r = requests.get("https://gamma-api.polymarket.com/markets", headers=H, timeout=60, params={
                    "closed": "true", "limit": 500, "offset": page * 500, "volume_num_min": 5000,
                    "end_date_min": f"{a}T00:00:00Z", "end_date_max": f"{b}T00:00:00Z"})
                batch = r.json() if r.status_code == 200 else None
                if batch is not None:
                    break
            except (requests.RequestException, ValueError):
                pass
            time.sleep(2 ** essai)
        else:
            print("échec", a, page, file=sys.stderr)
            return out
        if not isinstance(batch, list) or not batch:
            break
        for m in batch:
            t0, t1 = ts(m.get("startDate") or m.get("createdAt")), ts(m.get("endDate"))
            if t0 is None or t1 is None or t1 - t0 < 30 * 86400:
                continue
            ev = (m.get("events") or [{}])[0]
            out.append(dict(id=str(m["id"]), q=m.get("question", ""), slug=m.get("slug"), cid=m.get("conditionId"),
                            toks=m.get("clobTokenIds"), prices=m.get("outcomePrices"), outcomes=m.get("outcomes"),
                            start=t0, end=t1, closed=ts(m.get("closedTime")), vol=float(m.get("volume") or 0),
                            uma=m.get("umaResolutionStatus"), fees=m.get("feesEnabled"), fs=m.get("feeSchedule"),
                            neg=m.get("negRisk"), hold=m.get("holdingRewardsEnabled"),
                            ev_id=str(ev.get("id", "")), ev_slug=ev.get("slug"), ev_title=ev.get("title"),
                            desc=(m.get("description") or "")[:500]))
        if len(batch) < 500:
            break
    return out


wins, d = [], start
while d < end:
    wins.append((d, min(d + dt.timedelta(days=10), end)))
    d += dt.timedelta(days=10)
seen = set()
if os.path.exists(OUT):
    seen = {json.loads(l)["id"] for l in open(OUT)}
n = 0
with cf.ThreadPoolExecutor(4) as ex, open(OUT, "a") as f:
    for res in ex.map(lambda w: window(*w), wins):
        for m in res:
            if m["id"] not in seen:
                seen.add(m["id"])
                f.write(json.dumps(m) + "\n")
                n += 1
print(n, "nouveaux marchés à longue échéance ;", len(seen), "au total")
