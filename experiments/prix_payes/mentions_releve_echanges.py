"""Mentions (mots_prononces) : vrais échanges des preneurs pour chaque marché du test historique.
Lit donnees/mn/data.json (écrit par ../vingt_pistes/scripts/mentions_releve.py), retrouve le conditionId
de chaque marché (Gamma, mêmes pages que mentions_releve_evenements.py), puis relève les échanges entre
l'ouverture + 2 h et l'ouverture + 48 h (délais 2 / 12 / 24 h, fenêtre jusqu'à 24 h).
Écrit donnees/prix_payes/mentions_ids.json et le cache des échanges. 3 requêtes à la fois.
Usage : .venv/bin/python experiments/prix_payes/mentions_releve_echanges.py"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
from commun import get, trades  # noqa: E402

IDS = "donnees/prix_payes/mentions_ids.json"
os.makedirs("donnees/prix_payes", exist_ok=True)
if not os.path.exists(IDS):
    ids, offset = {}, 0
    while offset <= 2000:  # au-delà, Gamma refuse
        page = get("https://gamma-api.polymarket.com/events", {"tag_slug": "mention-markets", "closed": "true", "limit": 100,
                                                                "offset": offset, "order": "endDate", "ascending": "false"})
        if not isinstance(page, list) or not page:
            break
        for e in page:
            for m in e.get("markets") or []:
                tok = json.loads(m.get("clobTokenIds") or "[]")
                if tok and m.get("conditionId"):
                    ids[tok[0]] = m["conditionId"]
        offset += 100
    json.dump(ids, open(IDS, "w"))
ids = json.load(open(IDS))
d = json.load(open("donnees/mn/data.json"))
todo = [r for r in d["todo"] if len(r.get("hist") or []) >= 3 and len(r["tok"]) == 2 and not r["sp"].startswith('"')]
print("marchés du test", len(todo), "avec conditionId", sum(r["tok"][0] in ids for r in todo), flush=True)


def one(r):
    cid = ids.get(r["tok"][0])
    if not cid:
        return -1
    h0 = r["hist"][0]["t"]
    return len(trades(cid, h0 + 2 * 3600, h0 + 48 * 3600))


with ThreadPoolExecutor(3) as ex:  # 3 + le relevé des tweets en cours = 4 requêtes au plus
    n = []
    for i, k in enumerate(ex.map(one, todo)):
        n.append(k)
        if i % 250 == 0:
            print(i, flush=True)
ok = sorted(k for k in n if k >= 0)
print("échanges par marché (ouverture + 2 h à + 48 h) : médiane", ok[len(ok) // 2], "aucun", sum(k == 0 for k in ok),
      "sans conditionId", sum(k < 0 for k in n), flush=True)
