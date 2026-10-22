"""Piste n° 3 (marge_coherente), étape 2 : les tranches « marge de victoire » d'un candidat, additionnées, valent-elles le
marché « vainqueur » ? Écarts mesurés aux PRIX RÉELLEMENT PAYÉS, frais compris.

Usage : .venv/bin/python experiments/marge_coherente/prix_payes.py   (après releve_evenements.py)
Paires écrites à la main (PAIRES) après lecture des titres et des règles : même élection, même tour, même quantité
(rattachement fait AVANT de regarder les prix ; « voisine » = le « vainqueur » d'une législative peut se juger aux sièges).
Deux paniers qui paient un montant CONNU quoi qu'il arrive (A = un candidat, n = nombre de ses tranches) :
  - D1 (tranches trop bon marché) : OUI de toutes les tranches de A + NON de « A gagne »  → paie exactement 1 ;
  - D2 (tranches trop chères)     : OUI de « A gagne » + NON de chaque tranche de A       → paie exactement n.
Chaque jour à 18 h UTC pendant les 30 jours avant l'échéance (jusqu'à 12 h avant) : prix connus = derniers échanges réels
dans les 2 h AVANT ; si un panier coûte moins que ce qu'il paie (frais compris) : achat de chaque jambe au PREMIER
échange réel dans l'heure APRÈS ; une jambe sans échange = panier impossible (compté).
"""
import concurrent.futures as cf
import json
import re
import sys
import threading
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
from polymarket_agent.http_client import HttpClient, SourceUnavailable

D = Path("experiments/marge_coherente/donnees")
G = "https://gamma-api.polymarket.com"
# marge (id) : (vainqueur (slug), quantité, {préfixe des tranches : mots à trouver dans la question du marché vainqueur})
PAIRES = {
    "903211": ("presidential-election-winner-2024", "même", {"GOP": ["trump"], "Dems": ["harris", "kamala"]}),
    "11910": ("presidential-election-popular-vote-winner-2024", "même", {"GOP": ["trump", "republican"], "Dems": ["harris", "kamala", "democrat"]}),
    "13251": ("georgia-presidential-election-winner", "même", {"Trump": ["trump", "republican"], "Harris": ["harris", "democrat"]}),
    "175385": ("portugal-presidential-election", "même", {"Seguro": ["seguro"], "Ventura": ["ventura"]}),
    "563121": ("colombia-presidential-election", "même", {"de la Espriella": ["espriella"], "Cepeda Castro": ["cepeda"]}),
    "246812": ("hungary-parliamentary-election-popular-vote-winner", "même", {"Tisza": ["tisza"], "Fidesz-KDNP": ["fidesz"]}),
    "882591": ("massachusetts-democratic-senate-primary-winner", "même", {"Markey": ["markey"], "Moulton": ["moulton"]}),
    "1025426": ("holborn-and-st-pancras-by-election-winner", "même", {"Labour": ["labour"], "Green": ["green"]}),
    "990818": ("sweden-parliamentary-election-winner", "voisine", {"S": ["social democrat"]}),
    "1004899": ("mecklenburg-vorpommern-parliamentary-election-winner", "voisine", {"AfD": ["afd", "alternative"], "SPD": ["spd", "social democratic"]}),
    "1030972": ("berlin-state-election-winner", "voisine", {"Linke": ["linke", "left"], "CDU": ["cdu", "christian democratic"]}),
    "1113950": ("latvian-parliamentary-election-winner", "voisine", {"AS": ["united list", "apvienotais"]}),
    "265316": ("denmark-parliamentary-election-winner", "voisine", {"Social Democrats": ["social democrat"]}),
}
http = HttpClient(timeout=40, min_interval=0.15)
local, lock = threading.local(), threading.Lock()


def label_owner(label, prefixes):
    """Préfixe (candidat) d'une tranche : « GOP by 5-14 » → GOP ; « Ventura Victory » → Ventura ; « Other » → None."""
    for p in sorted(prefixes, key=len, reverse=True):
        if (label or "").strip().lower().startswith(p.lower() + " ") or (label or "").strip().lower() == p.lower():
            return p
    return None


def toks(m):
    t = json.loads(m.get("clobTokenIds") or "[]")
    return (t[0], t[1]) if len(t) == 2 else (None, None)


def rate(m):
    fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
    return float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0


marges = {r["id"]: r for r in json.load(open(D / "marges.json"))}
groups = []   # (paire, quantité, candidat, tranches [(cid, oui, non, taux)], vainqueur (cid, oui, non, taux), échéance)
for mid, (wslug, qty, names) in PAIRES.items():
    if mid not in marges:
        print("marge absente du relevé :", mid)
        continue
    ev = http.get_json(f"{G}/events/{mid}")
    wins = http.get_json(f"{G}/events", params={"slug": wslug})
    if not ev or not wins:
        print("événement introuvable :", mid, wslug)
        continue
    wev = wins[0]
    end = it._ts(ev.get("endDate")) or it._ts(wev.get("endDate"))
    for cand, words in names.items():
        br = [m for m in ev.get("markets") or [] if label_owner(m.get("groupItemTitle"), names) == cand]
        wm = [m for m in wev.get("markets") or [] if any(w in (m.get("question", "") + " " + (m.get("groupItemTitle") or "")).lower() for w in words)]
        if not br or len(wm) != 1:
            print(f"   {ev.get('slug')} / {cand} : {len(br)} tranches, {len(wm)} marché(s) vainqueur → écarté")
            continue
        w = wm[0]
        legs = [(m["conditionId"], *toks(m), rate(m), m.get("groupItemTitle")) for m in br]
        won_b = [json.loads(m.get("outcomePrices") or "[]")[:1] for m in br]
        groups.append(dict(paire=ev.get("slug"), qty=qty, cand=cand, legs=legs, win=(w["conditionId"], *toks(w), rate(w), w.get("question")),
                           end=end, won=json.loads(w.get("outcomePrices") or "[]")[:1], won_b=won_b))
        print(f"   {ev.get('slug')} / {cand} : {len(br)} tranches ↔ « {w.get('question')} » (règlement vainqueur {w.get('outcomePrices')})")

# ---------------------------------------------------------------- échanges réels autour de chaque instant (cache)
CACHE = D / "echanges.json"
cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}


def fetch(job):
    cid, t = job
    key = f"{cid}|{t}"
    if key in cache:
        return
    if not hasattr(local, "http"):
        local.http = HttpClient(timeout=40, min_interval=0.15)
    try:
        b = local.http.get_json(it.TRADES, params={"market": cid, "start": t - 2 * 3600, "end": t + 3600, "limit": 1000})
    except SourceUnavailable:
        return
    rows = [[int(x["timestamp"]), str(x["asset"]), str(x["side"]), float(x["price"])] for x in b or [] if x.get("timestamp")]
    with lock:
        cache[key] = rows


jobs = set()
for g in groups:
    first = g["end"] - 30 * 86400
    first -= first % 86400
    for day in range(30):
        t = first + day * 86400 + 18 * 3600
        if t <= g["end"] - 12 * 3600:
            for leg in g["legs"] + [g["win"]]:
                jobs.add((leg[0], t))
todo = [j for j in jobs if f"{j[0]}|{j[1]}" not in cache]
print(f"\npaires candidat : {len(groups)} ; lectures d'échanges : {len(jobs)} (à faire : {len(todo)})")
with cf.ThreadPoolExecutor(8) as ex:
    list(ex.map(fetch, todo))
CACHE.write_text(json.dumps(cache))


def price(rows, yes, no, t, buy_side, after=False):
    """Prix payé pour acheter le OUI (buy_side='OUI') ou le NON : dernier avant t (2 h) ou premier après t (1 h)."""
    pts = []
    for ts_, asset, side, p in rows:
        if buy_side == "OUI" and ((asset == yes and side == "BUY") or (asset == no and side == "SELL")):
            pts.append((ts_, p if asset == yes else 1 - p))
        if buy_side == "NON" and ((asset == no and side == "BUY") or (asset == yes and side == "SELL")):
            pts.append((ts_, p if asset == no else 1 - p))
    pts.sort()
    if after:
        sel = [p for w, p in pts if t < w <= t + 3600]
        return sel[0] if sel else None
    sel = [p for w, p in pts if t - 2 * 3600 <= w <= t]
    return sel[-1] if sel else None


def last_any(rows, yes, t):
    sel = sorted((w, p if a == yes else 1 - p) for w, a, s, p in rows if t - 2 * 3600 <= w <= t)
    return sel[-1][1] if sel else None


obs, gaps, signals, fills, bets = 0, [], 0, 0, []
per_pair = defaultdict(lambda: [0, 0, []])
for g in groups:
    first = g["end"] - 30 * 86400
    first -= first % 86400
    for day in range(30):
        t = first + day * 86400 + 18 * 3600
        if t > g["end"] - 12 * 3600:
            continue
        R = lambda leg: cache.get(f"{leg[0]}|{t}", [])
        # écart descriptif : dernier prix échangé (toutes sortes) de chaque jambe
        lasts = [last_any(R(l), l[1], t) for l in g["legs"]]
        lw = last_any(R(g["win"]), g["win"][1], t)
        if lw is not None and all(x is not None for x in lasts):
            gaps.append((sum(lasts) - lw, g["paire"], g["cand"]))
        n = len(g["legs"])
        d1 = [price(R(l), l[1], l[2], t, "OUI") for l in g["legs"]] + [price(R(g["win"]), g["win"][1], g["win"][2], t, "NON")]
        d2 = [price(R(l), l[1], l[2], t, "NON") for l in g["legs"]] + [price(R(g["win"]), g["win"][1], g["win"][2], t, "OUI")]
        rates = [l[3] for l in g["legs"]] + [g["win"][3]]
        for name, known, pay, side_b, side_w in (("D1", d1, 1, "OUI", "NON"), ("D2", d2, n, "NON", "OUI")):
            if any(x is None for x in known):
                continue
            obs += 1
            per_pair[g["paire"]][0] += 1
            cost = sum(p + it.fee(p, r) for p, r in zip(known, rates))
            if cost >= pay:
                continue
            signals += 1
            per_pair[g["paire"]][1] += 1
            done = [price(R(l), l[1], l[2], t, side_b, after=True) for l in g["legs"]] + \
                   [price(R(g["win"]), g["win"][1], g["win"][2], t, side_w, after=True)]
            if any(x is None for x in done):
                per_pair[g["paire"]][2].append(f"{name} {datetime.fromtimestamp(t, tz=timezone.utc):%Y-%m-%d} connu {cost:.3f}/{pay} : jambe sans échange après")
                continue
            fills += 1
            paid = sum(p + it.fee(p, r) for p, r in zip(done, rates))
            bets.append(dict(gain=pay / paid - 1, evenement=g["paire"], cout=min(0.999, paid / pay),
                             mois=datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m")))
            per_pair[g["paire"]][2].append(f"{name} {datetime.fromtimestamp(t, tz=timezone.utc):%Y-%m-%d} connu {cost:.3f}/{pay} payé {paid:.3f}")

print(f"\nobservations complètes (toutes les jambes échangées dans les 2 h) : {obs} ; paniers sous leur paiement (prix connus) : {signals} ;"
      f" exécutables aux prix d'après : {fills}")
if gaps:
    vals = sorted(abs(x[0]) for x in gaps)
    print(f"écart |Σ tranches − vainqueur| au dernier prix échangé : {len(vals)} cas, médiane {vals[len(vals) // 2]:.3f}, "
          f"9e décile {vals[int(len(vals) * 0.9)]:.3f}, max {vals[-1]:.3f}")
    for x in sorted(gaps, key=lambda x: -abs(x[0]))[:6]:
        print(f"   {x[1]} / {x[2]} : Σ tranches − vainqueur = {x[0]:+.3f}")
for p, (o, s, det) in per_pair.items():
    print(f"   {p} : {o} observations complètes, {s} signaux")
    for d in det[:6]:
        print("      ", d)
if bets:
    print(json.dumps(it.verdict(bets, min_bets=10), ensure_ascii=False))
    print("gain moyen par panier exécuté :", round(sum(b["gain"] for b in bets) / len(bets), 4))
