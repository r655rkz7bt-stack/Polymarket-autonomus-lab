"""Relevé des événements réglés « How high / low will <N>-year Treasury yield go/get in <mois>? » (Gamma public-search) et des prix
horaires de chaque marché (CLOB prices-history, tranches de 14 jours). Sortie : donnees/marches.json, donnees/prix/<token>.json."""
import json, os, re, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
H = {"User-Agent": "curl/8"}
D = os.path.join(os.path.dirname(__file__), "..", "donnees")
os.makedirs(os.path.join(D, "prix"), exist_ok=True)
ev = {}
for q in ["Treasury yield go in", "Treasury yield get in", "Treasury yield go before", "Treasury yield get before"]:
    for page in range(1, 12):
        r = requests.get("https://gamma-api.polymarket.com/public-search", params={"q": q, "events_status": "closed", "limit_per_type": 50,
                         "page": page}, headers=H, timeout=60).json()
        es = r.get("events") or []
        for e in es:
            ev[e["id"]] = e
        if len(es) < 50:
            break
print(len(ev), "événements")
T = re.compile(r"How (high|low) will (\d+)-year Treasury yield (?:go|get) in (\w+)\??", re.I)
rows = []
for eid, e in ev.items():
    g = T.match(e["title"])
    if not g:
        continue
    full = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=60).json()
    for m in full.get("markets", []):
        lv = re.search(r"(\d+\.\d+)%", m["question"])
        if not lv or not m.get("closed"):
            continue
        op = json.loads(m.get("outcomePrices") or "[]")
        rows.append({"event": eid, "titre": e["title"], "sens": g.group(1).lower(), "duree": int(g.group(2)), "mois": g.group(3),
                     "start": full.get("startDate"), "end": full.get("endDate"), "closedTime": m.get("closedTime"),
                     "niveau": float(lv.group(1)), "question": m["question"], "id": m["id"], "oui": json.loads(m["clobTokenIds"])[0],
                     "gagne": float(op[0]) if op else None, "desc": m.get("description", "")[:400], "fee": m.get("feeType")})
json.dump(rows, open(os.path.join(D, "marches.json"), "w"))
print(len(rows), "marchés")
def prix(r):
    out = os.path.join(D, "prix", r["oui"] + ".json")
    if os.path.exists(out):
        return
    a = int(datetime.fromisoformat(r["start"].replace("Z", "+00:00")).timestamp())
    b = int(datetime.fromisoformat((r["closedTime"] or r["end"]).replace(" ", "T").replace("+00", "+00:00").replace("Z", "+00:00")).timestamp())
    pts = []
    while a < b:
        c = min(a + 13 * 86400, b)
        for k in range(3):
            try:
                pts += requests.get("https://clob.polymarket.com/prices-history", params={"market": r["oui"], "startTs": a, "endTs": c,
                                    "fidelity": 60}, headers=H, timeout=60).json().get("history", [])
                break
            except Exception:
                time.sleep(2)
        a = c
    json.dump(pts, open(out, "w"))
with ThreadPoolExecutor(6) as ex:
    list(ex.map(prix, rows))
