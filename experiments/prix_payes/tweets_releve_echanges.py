"""Compteur de tweets : conditionId des tranches (Gamma, événement par slug) puis vrais échanges des preneurs.
Lit donnees/xt/marches.json (../vingt_pistes/scripts/tweets_releve_marches.py) et les cas écrits par
tweets_cas.py. NYC Mayor est sauté (exclu de compteur_tweets_non).
- tranche « légère » (volume ≤ LOURD $) : tous les échanges de la période (de début + 6 h à la fin) ;
- tranche « lourde » (Elon Musk surtout, des dizaines de milliers d'échanges) : seulement les 24 h qui suivent
  chaque achat de NON décidé au prix horaire (6 réglages), pour rester raisonnable.
Écrit donnees/prix_payes/tweets_ids.json et le cache des échanges. 4 requêtes à la fois au plus."""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from commun import get, trades  # noqa: E402

LOURD = 300_000
IDS = "donnees/prix_payes/tweets_ids.json"
SETTINGS = [(12.0, 0.03, 0.10), (8.0, 0.03, 0.10), (16.0, 0.03, 0.10), (12.0, 0.0, 0.10), (12.0, 0.05, 0.10), (12.0, 0.03, 0.20)]


def no_buys(cases, margin, minp):
    for c in cases:
        cost = 1 - c["p"] + (0.01 if c["h"] == "elonmusk" else 0.02)
        if c["h"] != "NYCMayor" and max(0.01, minp) <= cost < 0.99 and (1 - c["q"]) - margin > cost:
            yield c


if __name__ == "__main__":
    ev = json.load(open("donnees/xt/marches.json"))
    if not os.path.exists(IDS):
        def one_id(slug):
            e = get("https://gamma-api.polymarket.com/events", {"slug": slug})
            if not e:
                e = get("https://gamma-api.polymarket.com/events", {"slug": slug, "closed": "true"})
            return slug, {m.get("groupItemTitle"): {"cid": m.get("conditionId"), "tok": json.loads(m.get("clobTokenIds") or "[]"),
                                                    "vol": float(m.get("volume") or 0)} for m in (e[0].get("markets") or [])} if e else {}
        with ThreadPoolExecutor(4) as ex:
            json.dump(dict(ex.map(one_id, [e["slug"] for e in ev])), open(IDS, "w"))
    ids = json.load(open(IDS))
    jobs = set()
    start6 = {e["slug"]: int(datetime.fromisoformat(e["debut"]).timestamp()) + 6 * 3600 for e in ev}
    for disp in sorted({s[0] for s in SETTINGS}):
        cases = json.load(open(f"donnees/prix_payes/tweets_cas_{disp}.json"))
        for c in cases:
            m = ids.get(c["slug"], {}).get(c["titre"])
            if c["h"] == "NYCMayor" or not m or not m["cid"]:
                continue
            if m["vol"] <= LOURD:
                jobs.add((m["cid"], start6[c["slug"]], c["fin"]))
        for s in SETTINGS:
            if s[0] != disp:
                continue
            for c in no_buys(cases, s[1], s[2]):
                m = ids.get(c["slug"], {}).get(c["titre"])
                if m and m["cid"] and m["vol"] > LOURD:
                    jobs.add((m["cid"], c["t"], min(c["t"] + 24 * 3600, c["fin"])))
    jobs = sorted(jobs)
    print("fenêtres à relever", len(jobs), flush=True)
    with ThreadPoolExecutor(4) as ex:
        n = []
        for i, k in enumerate(ex.map(lambda j: len(trades(*j)), jobs)):
            n.append(k)
            if i % 250 == 0:
                print(i, flush=True)
    print("échanges par fenêtre : médiane", sorted(n)[len(n) // 2], "aucun", sum(k == 0 for k in n), "max", max(n), flush=True)
