"""28/10/2026 : relevé des événements « <actif> price on <date>? » (11 marchés : « less than », « between » × 9, « greater than », réglés à 12 h heure de l'Est) par la recherche publique de Gamma
(q = « Bitcoin price on », events_status = closed, pages de 50 ; aucun filtre par date côté serveur). Écrit au format de releve_marches.py (un marché Oui/Non par ligne) dans
donnees/marches_d.jsonl, pour les événements dont la fin est entre DEBUT et FIN. Usage : python releve_prix_du_jour.py 2026-01-01 2026-08-20 [sortie.jsonl]"""
import json, sys, time, datetime, requests
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
DEBUT = sys.argv[1]; FIN = sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else "experiments/contrer_crypto_passe/donnees/marches_d.jsonl"
vus, n = set(), 0
with open(OUT, "w") as f:
    for nom in ("Bitcoin", "Ethereum", "Solana", "XRP"):
        page = 1
        while True:
            for k in range(5):
                try:
                    r = S.get("https://gamma-api.polymarket.com/public-search", params={"q": f"{nom} price on", "events_status": "closed", "limit_per_type": 50, "page": page}, timeout=90)
                    if r.status_code == 200: break
                except Exception: pass
                time.sleep(2 ** k)
            j = r.json(); ev = j.get("events") or []
            for e in ev:
                if e["id"] in vus or not e["title"].lower().startswith(nom.lower() + " price on"): continue
                vus.add(e["id"]); end = (e.get("endDate") or "")[:10]
                if not DEBUT <= end <= FIN: continue
                for m in e.get("markets") or []:
                    try:
                        outs = json.loads(m["outcomes"]) if isinstance(m.get("outcomes"), str) else m.get("outcomes")
                        toks = json.loads(m["clobTokenIds"]) if isinstance(m.get("clobTokenIds"), str) else m.get("clobTokenIds")
                        prices = json.loads(m["outcomePrices"]) if isinstance(m.get("outcomePrices"), str) else m.get("outcomePrices")
                    except Exception: continue
                    if [str(o).lower() for o in outs or []] != ["yes", "no"] or len(toks or []) != 2: continue
                    f.write(json.dumps({"event_id": e["id"], "event_title": e.get("title"), "event_slug": e.get("slug"), "event_end": e.get("endDate"), "id": m["id"], "cond": m["conditionId"],
                        "question": m.get("question"), "yes": toks[0], "no": toks[1], "prices": prices, "vol": m.get("volumeNum"), "start": m.get("startDate") or m.get("createdAt"),
                        "end": m.get("endDate"), "closed": m.get("closedTime"), "uma": m.get("umaResolutionStatus"), "feeSchedule": m.get("feeSchedule"), "feesEnabled": m.get("feesEnabled"),
                        "feeType": m.get("feeType"), "slug": m.get("slug")}) + "\n"); n += 1
            print(nom, page, len(vus), n, flush=True)
            if not j.get("pagination", {}).get("hasMore") or not ev: break
            page += 1
print("fini", len(vus), "événements,", n, "marchés")
