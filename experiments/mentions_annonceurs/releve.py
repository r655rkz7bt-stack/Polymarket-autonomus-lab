"""Piste n° 1 (21/10/2026) : mentions « the announcers » et « anyone ». Relève les marchés réglés de ces
deux orateurs depuis donnees/mn/events.json (écrit par ../vingt_pistes/scripts/mentions_releve_evenements.py)
et les prix horaires du jeton OUI (CLOB prices-history). Écrit donnees/mn/annonceurs.json.
À lancer depuis la racine : .venv/bin/python experiments/mentions_annonceurs/releve.py"""
import json
import re
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import requests

D = "donnees/mn"
SPEAKERS = ("the announcers", "anyone")


def speaker(q):
    m = re.match(r'^will (.+?) (?:say|mention|be said)', (q or "").lower())
    return m.group(1) if m else None


rows = []
for e in json.load(open(f"{D}/events.json")):
    for m in e["markets"]:
        sp = speaker(m["q"])
        if sp not in SPEAKERS or not m["t"]:
            continue
        try:
            res = json.loads(m["res"] or "[]")
            tok = json.loads(m["tok"] or "[]")
        except Exception:
            continue
        if res not in (["1", "0"], ["0", "1"]) or not tok:
            continue
        rows.append({"sp": sp, "w": m["t"], "yes": res == ["1", "0"], "end": m["end"] or e["endDate"], "closed": m["closedTime"],
                     "tok": tok[0], "ev": e["slug"], "title": e["title"], "vol": m["vol"], "q": m["q"]})
print("marchés", len(rows), flush=True)
s = requests.Session()


def ts(x):
    return int(datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp()) if x else None


def hist(r):
    # interval=max ne rend presque rien pour les marchés clos depuis longtemps (269 sur 3 555) : fenêtre explicite
    end = max(ts(r["closed"]) or 0, ts(r["end"]) or 0)
    params = {"market": r["tok"], "startTs": end - 12 * 86400, "endTs": end + 86400, "fidelity": 60}
    for k in range(4):
        try:
            h = s.get("https://clob.polymarket.com/prices-history", params=params, timeout=40).json()
            r["hist"] = h.get("history") or []
            return
        except Exception:
            time.sleep(2 ** k)
    r["hist"] = []


with ThreadPoolExecutor(6) as ex:
    for i, _ in enumerate(ex.map(hist, rows)):
        if i % 500 == 0:
            print(i, flush=True)
json.dump(rows, open(f"{D}/annonceurs.json", "w"))
print("avec historique", sum(1 for r in rows if len(r["hist"]) >= 3), flush=True)
