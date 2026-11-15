"""Piste n° 62 (15/11/2026) : événements Polymarket « Highest temperature in <ville> on <date>? » réglés, pour les villes dont
Kalshi a la même station (KAUS, KMIA, KDEN, KLAX). public-search par pages de 50 (events_status=closed). Sortie :
donnees/poly_events.json (événement, ville, date, tranches, jetons, prix finaux, règle)."""
import json, re, sys, requests
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
VILLES = {"Austin": "KAUS", "Miami": "KMIA", "Denver": "KDEN", "Los Angeles": "KLAX"}
out = {}
for ville in VILLES:
    for page in range(1, 40):
        r = S.get("https://gamma-api.polymarket.com/public-search",
                  params={"q": f"Highest temperature in {ville} on", "events_status": "closed", "limit_per_type": 50, "page": page}, timeout=30)
        evs = (r.json() or {}).get("events") or []
        if not evs: break
        for e in evs:
            m = re.match(rf"Highest temperature in {ville} on (\w+ \d+)\??$", e.get("title") or "")
            if not m: continue
            out[e["id"]] = {"id": e["id"], "ville": ville, "titre": e["title"], "fin": e.get("endDate"), "slug": e.get("slug"),
                            "source": e.get("resolutionSource"), "desc": (e.get("description") or "")[:1500],
                            "marches": [{"id": x["id"], "tranche": x.get("groupItemTitle"), "jetons": json.loads(x.get("clobTokenIds") or "[]"),
                                         "prix": json.loads(x.get("outcomePrices") or "[]"), "cond": x.get("conditionId"),
                                         "volume": x.get("volume"), "cree": x.get("createdAt"), "ferme": x.get("closedTime")}
                                        for x in e.get("markets") or []]}
        print(ville, page, len(out), file=sys.stderr)
json.dump(list(out.values()), open("donnees/poly_events.json", "w"))
print(len(out))
