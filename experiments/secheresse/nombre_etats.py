"""Piste n° 24, suite : « How many states will be in D4 (Exceptional Drought) — week of … » (6 tranches). Loi du nombre d'États
= somme de Bernoulli indépendantes (loi de transition par État, carte publiée la semaine d'avant), règlement relu sur l'USDM,
vrais échanges avant publication (data-api v2)."""
import json
import re
from datetime import datetime, timezone

import requests

import analyse as A

H = {"User-Agent": "curl/8", "Accept": "application/json"}
evs = {}
for page in range(1, 4):
    r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=30,
                     params={"q": "How many states will be in D4", "events_status": "closed", "limit_per_type": 50, "page": page}).json()
    for e in r.get("events") or []:
        if e["title"].startswith("How many states will be in D4"):
            evs[e["id"]] = e
    if len(r.get("events") or []) < 50:
        break
L1 = A.loi(pas=1)


def tranche(q):
    q = q.replace(",", "")
    m = re.search(r"(\d+)\s*(?:-|to|–)\s*(\d+)", q)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d+)\s*(?:\+|or more)", q)
    if m:
        return int(m.group(1)), 99
    m = re.search(r"(?:fewer than|less than|under)\s*(\d+)", q, re.I)
    if m:
        return 0, int(m.group(1)) - 1
    m = re.search(r"\b(\d+)\b", q)
    return (int(m.group(1)), int(m.group(1))) if m else None


rows, ok, bad = [], 0, 0
for eid, e0 in sorted(evs.items()):
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()
    w = A.semaine(e["title"])
    prev = str(w.fromordinal(w.toordinal() - 7))
    # loi du nombre (48 États, indépendants)
    dist = [1.0]
    for etat in A.usdm:
        r = A.carte[etat].get(prev)
        p = L1[A.classe(r)][0] if r else 0.0
        dist = [a * (1 - p) + (dist[i - 1] * p if i else 0) for i, a in enumerate(dist + [0.0])]
    vrai = sum(1 for etat in A.usdm if (A.carte[etat].get(str(w)) or {}).get("d4", 0) >= A.SEUIL)
    trades = []
    cur = None
    while True:
        p_ = {"event_id": eid, "limit": 1000}
        if cur:
            p_["cursor"] = cur
        res = requests.get("https://data-api.polymarket.com/v2/trades", params=p_, headers=H, timeout=30).json()
        trades += res.get("data") or []
        pag = res.get("pagination") or {}
        cur = pag.get("next_cursor") if pag.get("has_more") else None
        if not cur:
            break
    rel = A.publication(w)
    for m in e["markets"]:
        tr = tranche(m.get("groupItemTitle") or m["question"])
        oui = json.loads(m["outcomePrices"])[0] == "1"
        if tr is None:
            print("tranche illisible", m["question"])
            continue
        p_oui = sum(dist[k] for k in range(len(dist)) if tr[0] <= k <= tr[1])
        if (tr[0] <= vrai <= tr[1]) == oui:
            ok += 1
        else:
            bad += 1
            print("règlement différent", e["title"], tr, vrai, oui)
        for t in trades:
            if t["condition_id"] != m["conditionId"]:
                continue
            ts = datetime.fromtimestamp(t["timestamp"], timezone.utc)
            if ts >= rel:
                continue
            achete_oui = (t["outcome"] == "Yes") == (t["side"] == "BUY")
            prix = t["price"] if t["side"] == "BUY" else 1 - t["price"]
            p = p_oui if achete_oui else 1 - p_oui
            rows.append(dict(w=str(w), m=m["id"], prix=prix, p=p, gagne=(oui == achete_oui), parts=t["size"], ts=ts,
                             frais=0.05 * prix * (1 - prix), tr=tr, vrai=vrai))
    print(e["title"][-25:], "vrai", vrai, "loi : moyenne", round(sum(k * d for k, d in enumerate(dist)), 2), "échanges", len(trades))
print(f"règlement {ok} conformes, {bad} différents")
for seuil in (0.02, 0.05, 0.10):
    vus, lot = set(), []
    for r in sorted(rows, key=lambda r: r["ts"]):
        if r["m"] in vus or r["prix"] < 0.10 or r["p"] - r["prix"] - r["frais"] < seuil:
            continue
        vus.add(r["m"])
        lot.append(r)
    if lot:
        g = sum(((1 if r["gagne"] else 0) - r["prix"] - r["frais"]) / r["prix"] for r in lot) / len(lot)
        print(f"seuil {seuil}: {len(lot)} paris, {len({r['w'] for r in lot})} semaines, gagnés {sum(r['gagne'] for r in lot)} pour "
              f"{sum(r['p'] for r in lot):.1f} (loi) / {sum(r['prix'] for r in lot):.1f} (prix), rendement {g:+.1%}")
