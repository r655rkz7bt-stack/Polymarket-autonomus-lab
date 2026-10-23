"""Relevé des événements « k gagnants parmi N » réglés (top 8, qualifiés, relégués, atteindre les huitièmes…).
Idée (piste du 23/10/2026) : dans un événement où exactement k marchés doivent finir OUI, la somme des prix OUI vaut k ;
un écart signale des cases mal cotées. Sortie : donnees/evenements.jsonl (un événement par ligne, avec ses marchés et leurs résultats)."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
import requests
H = {"User-Agent": "curl/8"}
REQ = ["Top 8", "Top 4", "Top 24", "to qualify", "advance to", "Reach Round", "relegated", "Relegation", "make the playoffs", "to make the",
       "Finish Top", "Top 6", "Top 3", "Top 5", "Top 10", "to reach", "promoted", "automatic promotion", "Europa League", "Conference League",
       "Team to advance", "Which teams", "Nation To Reach", "Player to Qualify", "Qualify to"]
seen = {}
def cherche(q):
    out = []
    for page in range(1, 8):
        try:
            r = requests.get("https://gamma-api.polymarket.com/public-search", params=dict(q=q, limit_per_type=50, page=page, events_status="closed"),
                             headers=H, timeout=40).json()
        except Exception as e:
            break
        ev = r.get("events", [])
        out += ev
        if not r.get("pagination", {}).get("hasMore"):
            break
    return out
with ThreadPoolExecutor(6) as ex:
    for evs in ex.map(cherche, REQ):
        for e in evs:
            seen[e["id"]] = e
print(len(seen), "événements trouvés")
keep = []
for e in seen.values():
    ms = e.get("markets", [])
    if not (4 <= len(ms) <= 80) or not e.get("closed"):
        continue
    keep.append(e)
print(len(keep), "événements clos de 4 à 80 marchés")
with open("experiments/k_gagnants/donnees/evenements.jsonl", "w") as f:
    for e in keep:
        f.write(json.dumps(e) + "\n")
