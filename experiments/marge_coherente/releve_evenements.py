"""Piste n° 3 (marge_coherente), étape 1 : événements « marge de victoire » d'élections RÉGLÉS et leur marché « vainqueur ».

Usage : .venv/bin/python experiments/marge_coherente/releve_evenements.py
1. Recherche publique Gamma (public-search) des événements clos « margin of victory » (sport et UFC écartés).
2. Pour chacun : ses tranches (libellé, prix final, jetons) et les événements « vainqueur » candidats
   (même recherche, mots du titre sans « margin of victory »). Le rattachement final est écrit à la main
   dans `paires.py` après lecture des règles (même élection, même tour, même quantité) : jamais d'après le résultat.
Sortie : donnees/marges.json (ignoré par Git) et un résumé à l'écran.
"""
import json
import re
import time

import requests

H = {"User-Agent": "polymarket-autonomous-lab (etude)"}
G = "https://gamma-api.polymarket.com"
SPORT = re.compile(r"ufc|nfl|cfb|nba|super-bowl|boxing|vs-|mnf|tnf|fight|joshua|canelo|paul|red-vs-blue")


def get(url, params=None):
    """GET avec 4 nouvelles tentatives (2, 4, 8, 16 s) : le réseau coupe parfois (SSL EOF)."""
    for essai in range(5):
        try:
            r = requests.get(url, headers=H, timeout=40, params=params)
            if r.status_code == 200:
                return r.json()
            if r.status_code not in (429, 500, 502, 503, 504):
                return None
        except (requests.RequestException, ValueError):
            pass
        time.sleep(2 ** (essai + 1))
    return None


def search(q, closed=True, pages=3):
    out = {}
    for page in range(1, pages + 1):
        d = get(f"{G}/public-search", {"q": q, "events_status": "closed" if closed else "active",
                                       "limit_per_type": 50, "page": page})
        if not d:
            break
        evs = d.get("events") or []
        for e in evs:
            out[str(e["id"])] = e
        if len(evs) < 50:
            break
    return out


def event(eid):
    return get(f"{G}/events/{eid}")


found = {}
for q in ("margin of victory", "margin", "popular vote margin", "vote share margin", "runoff margin of victory",
          "second round margin of victory", "electoral college margin"):
    for k, e in search(q, pages=6).items():
        if e.get("closed") and not SPORT.search(e.get("slug") or "") and "margin" in (e.get("slug") or ""):
            found[k] = e
rows = []
for k, e in sorted(found.items(), key=lambda x: x[1].get("endDate") or ""):
    full = event(k)
    if not full:
        continue
    ms = []
    for m in full.get("markets") or []:
        try:
            toks, pr = json.loads(m.get("clobTokenIds") or "[]"), json.loads(m.get("outcomePrices") or "[]")
        except ValueError:
            continue
        ms.append(dict(id=m["id"], q=m.get("question"), item=m.get("groupItemTitle"), cid=m.get("conditionId"),
                       yes=toks[0] if toks else None, no=toks[1] if len(toks) > 1 else None,
                       final=pr[0] if pr else None, vol=float(m.get("volume") or 0), uma=m.get("umaResolutionStatus"),
                       fees=m.get("feesEnabled"), fs=m.get("feeSchedule"), start=m.get("startDate"), end=m.get("endDate")))
    title = full.get("title") or ""
    base = re.sub(r"(?i)(popular vote |vote share |electoral college )?margin of victory|\(.*?\)|-|:", " ", title)
    cands = search(base.strip() + " winner") if base.strip() else {}
    cands.update(search(base.strip()))
    winners = [dict(id=c, slug=v.get("slug"), title=v.get("title"), end=v.get("endDate"))
               for c, v in cands.items() if "margin" not in (v.get("slug") or "") and c != k]
    rows.append(dict(id=k, slug=full.get("slug"), title=title, end=full.get("endDate"), neg=full.get("negRisk"),
                     vol=float(full.get("volume") or 0), desc=(full.get("description") or "")[:1200], markets=ms,
                     candidats_vainqueur=winners[:15]))
    print(f"\n### {k} {full.get('slug')} | {title} | fin {full.get('endDate')} | vol {float(full.get('volume') or 0):,.0f}")
    for m in ms:
        print(f"   {m['item']!s:40} final {m['final']} vol {m['vol']:,.0f}")
    for w in winners[:8]:
        print(f"   -> vainqueur ? {w['id']} {w['slug']} ({w['end']})")
json.dump(rows, open("experiments/marge_coherente/donnees/marges.json", "w"))
print(len(rows), "événements marge de victoire")
