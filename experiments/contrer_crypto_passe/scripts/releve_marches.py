"""27/10/2026, piste 0c : relevé des marchés crypto réglés (Gamma /events/keyset, jamais offset) pour tester « contrer un mouvement de 0,05 en 6 h ».
Écrit donnees/marches.jsonl : un marché Oui/Non par ligne (condition, jetons, règlement, volume, fin, frais). Lancer depuis la racine du dépôt.
Usage : python releve_marches.py 2026-05-01   (date la plus ancienne de fin d'événement)"""
import json, sys, time, datetime, requests
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
CUT = datetime.datetime.fromisoformat(sys.argv[1]).replace(tzinfo=datetime.timezone.utc)
OUT = sys.argv[2] if len(sys.argv) > 2 else "experiments/contrer_crypto_passe/donnees/marches.jsonl"
def jget(p):
    for k in range(6):
        try:
            r = S.get("https://gamma-api.polymarket.com/events/keyset", params=p, timeout=120)
            if r.status_code == 200: return r.json()
        except Exception: pass
        time.sleep(2 ** k)
def ts(s):
    if not s: return None
    s = str(s).replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    try: return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError: return None
HAUT = datetime.datetime.fromisoformat(sys.argv[3]).replace(tzinfo=datetime.timezone.utc) if len(sys.argv) > 3 else None
cursor, n_ev, n_m, vieux = None, 0, 0, 0
f = open(OUT, "w")
while True:
    p = {"tag_slug": "crypto", "closed": "true", "limit": 100, "order": "endDate", "ascending": "false"}
    if HAUT: p["end_date_max"] = HAUT.strftime("%Y-%m-%dT%H:%M:%SZ")
    if cursor: p["after_cursor"] = cursor
    d = jget(p)
    if not d or not d.get("events"): break
    for e in d["events"]:
        n_ev += 1
        end = ts(e.get("endDate"))
        if end and end < CUT: vieux += 1
        else: vieux = 0
        if end and end < CUT: continue
        if HAUT and end and end >= HAUT: continue
        for m in e.get("markets") or []:
            try:
                outs = json.loads(m["outcomes"]) if isinstance(m.get("outcomes"), str) else m.get("outcomes")
                toks = json.loads(m["clobTokenIds"]) if isinstance(m.get("clobTokenIds"), str) else m.get("clobTokenIds")
                prices = json.loads(m["outcomePrices"]) if isinstance(m.get("outcomePrices"), str) else m.get("outcomePrices")
            except Exception: continue
            if [str(o).lower() for o in outs or []] != ["yes", "no"] or len(toks or []) != 2: continue
            f.write(json.dumps({"event_id": e["id"], "event_title": e.get("title"), "event_slug": e.get("slug"), "event_end": e.get("endDate"),
                "id": m["id"], "cond": m["conditionId"], "question": m.get("question"), "yes": toks[0], "no": toks[1], "prices": prices,
                "vol": m.get("volumeNum"), "start": m.get("startDate") or m.get("createdAt"), "end": m.get("endDate"), "closed": m.get("closedTime"),
                "uma": m.get("umaResolutionStatus"), "feeSchedule": m.get("feeSchedule"), "feesEnabled": m.get("feesEnabled"), "feeType": m.get("feeType"),
                "slug": m.get("slug")}) + "\n"); n_m += 1
    cursor = d.get("next_cursor")
    print(n_ev, n_m, e.get("endDate"), flush=True)
    if not cursor or vieux > 300: break
