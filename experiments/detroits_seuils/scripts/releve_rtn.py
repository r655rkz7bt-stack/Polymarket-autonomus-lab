"""Détroits, seuils (25/10/2026) : prix horaire du OUI des marchés « returns to normal by … » et « on any day by … » réglés.
Sortie : experiments/detroits_seuils/releves/seuils.json  {marché: {titre, fin, reglement, prix:[(t,p)]}}"""
import json, sys, os, requests, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
inv = json.load(open("experiments/detroits/donnees/inventaire.json"))
cibles = [e for e in inv if e["type"] == "seuil" and e["clos"] and e["detroit"] == "Strait of Hormuz"]

def prix(tok, t0, t1):
    out, t = [], t0
    while t < t1:
        r = requests.get("https://clob.polymarket.com/prices-history", params=dict(market=tok, startTs=t, endTs=min(t + 13 * 86400, t1), fidelity=60), headers=H, timeout=40)
        out += [(x["t"], x["p"]) for x in r.json().get("history", [])]
        t += 13 * 86400
    return out

def un(e):
    ev = requests.get(f"https://gamma-api.polymarket.com/events/{e['id']}", headers=H, timeout=40).json()
    res = []
    for m in ev["markets"]:
        toks = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"]); pr = json.loads(m["outcomePrices"])
        i = outs.index("Yes")
        t0 = int(__import__("datetime").datetime.fromisoformat((ev.get("startDate") or ev["createdAt"]).replace("Z", "+00:00")).timestamp())
        t1 = int(__import__("datetime").datetime.fromisoformat(m["endDate"].replace("Z", "+00:00")).timestamp()) if m.get("endDate") else t0 + 40 * 86400
        res.append(dict(id=m["id"], event=e["id"], titre=ev["title"], question=m["question"], fin=m.get("endDate"), regl=float(pr[i]), prix=prix(toks[i], t0, t1)))
    return res

with cf.ThreadPoolExecutor(6) as ex:
    tout = [x for r in ex.map(un, cibles) for x in r]
os.makedirs("experiments/detroits_seuils/releves", exist_ok=True)
json.dump(tout, open("experiments/detroits_seuils/releves/seuils.json", "w"))
print(len(tout), "marchés,", sum(len(x["prix"]) for x in tout), "points")
