"""Piste n° 11 (non_aux_drames), étape 2 : acheter le NON des « drames » improbables à longue échéance, aux PRIX PAYÉS.

Usage : .venv/bin/python experiments/non_aux_drames/prix_payes.py
Entrée : donnees/marches.jsonl (releve_marches.py). Sorties : donnees/echanges_t0.json (cache), résultats à l'écran.

Question : « Les États-Unis confirmeront-ils les extraterrestres ? », « Poutine quittera-t-il le pouvoir en 2025 ? »,
« La Chine envahira-t-elle Taïwan ? » : quand le OUI vaut 2 à 15 % longtemps avant l'échéance, est-il trop cher
(biais favori-outsider) ? On achète le NON.

Règles fixées AVANT de regarder les résultats :
  - « drame » = la question contient un mot de la liste DRAME (guerre, dirigeant, économie, insolite) et aucun mot
    de statu quo (« remain », « still », « survive »…) : le OUI doit être l'événement spectaculaire ;
  - instant de décision T0 = échéance − 30, 90 ou 180 jours (un pari par marché et par horizon), au moins 2 jours
    après la création, marché pas encore réglé à T0 ;
  - prix connu à T0 = DERNIER échange réel (data-api, toutes issues ramenées au prix du OUI) dans les 7 jours avant T0,
    entre 0,02 et 0,15 ;
  - achat du NON au PREMIER échange réel « achat du NON » (ou vente du OUI) dans les 48 h APRÈS T0, frais du marché ;
    pas d'échange = pas de pari (compté « sans échange »).
  - Le data-api accepte `start` / `end` (secondes) : on lit les échanges autour de T0 même pour les gros marchés
    (la limite de 10 000 échanges ne s'applique plus à la fenêtre).
Rendement par pari = gain / mise ; par jour d'immobilisation = somme des gains / somme (mise × jours jusqu'au règlement).
"""
import concurrent.futures as cf
import json
import math
import re
import sys
import threading
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
from polymarket_agent.http_client import HttpClient, SourceUnavailable

D = Path("experiments/non_aux_drames/donnees")
DAY = 86400
DRAME = {
    "guerre": r"\b(invade|invades|invasion|war\b|wars\b|military action|military clash|strikes? on|attacks?\b|airstrikes?|"
              r"missiles?|nuclear|bomb|troops|blockade|annex|annexes|annexation|ceasefire|cease-fire|truce|clash|"
              r"declares? war|hostilities|drone strike|conflict)",
    "dirigeant": r"\b(out as|out by|out in|ousted|resigns?|resignation|step down|steps down|leaves? office|removed|impeach|"
                 r"impeached|impeachment|coup|assassinat\w*|dies?\b|death|dead\b|jail|prison|arrest(ed)?|indicted|"
                 r"convicted|extradited|detained|captured|25th amendment|deported|expelled)",
    "economie": r"\b(bankrupt\w*|default|recession|collapse|crash|insolven\w*|bank run|hyperinflation|depeg|de-peg|"
                r"delisted|shutdown|nationaliz\w*)",
    "insolite": r"\b(aliens?|ufo|uap|extraterrestrial|non-human|jesus|rapture|asteroid|apocalypse|martial law|secede|"
                r"secession|civil war|pandemic|outbreak|lockdown|state of emergency|meteor)",
}
STATU_QUO = re.compile(r"\b(remain|remains|still|survive|survives|stay|stays|keep|keeps|alive|retain|hold on)\b", re.I)
HORIZONS = (30, 90, 180)
LO, HI = 0.02, 0.15
# --temoin : groupe témoin = les marchés à longue échéance qui ne sont PAS des drames (même règle, horizon 90 j seulement).
# Sert à savoir si l'effet vient des drames ou du biais favori-outsider en général.
TEMOIN = "--temoin" in sys.argv
if TEMOIN:
    HORIZONS = (90,)


def category(q):
    for k, pat in DRAME.items():
        if re.search(pat, q, re.I):
            return k
    return None


rows = [json.loads(l) for l in open(D / "marches.jsonl")]
cands = []
for m in rows:
    try:
        prices, toks, outs = json.loads(m["prices"] or "[]"), json.loads(m["toks"] or "[]"), json.loads(m["outcomes"] or "[]")
    except (ValueError, TypeError):
        continue
    if sorted(prices) != ["0", "1"] or len(toks) != 2 or [o.lower() for o in outs] != ["yes", "no"]:
        continue
    if m.get("uma") not in (None, "", "resolved") or not m.get("cid"):
        continue
    cat = category(m["q"])
    if TEMOIN:
        if cat is not None:
            continue
        cat = "temoin"
    elif cat is None or STATU_QUO.search(m["q"]):
        continue
    m["yes"], m["no"], m["won"], m["cat"] = toks[0], toks[1], 1 if prices[0] == "1" else 0, cat
    fs = m.get("fs") if isinstance(m.get("fs"), dict) else {}
    m["rate"] = float(fs.get("rate") or 0) if m.get("fees") else 0.0
    cands.append(m)
print(f"marchés à longue échéance : {len(rows)} ; « drames » réglés oui/non : {len(cands)}",
      dict(sorted(defaultdict(int, {c: sum(1 for m in cands if m['cat'] == c) for c in DRAME}).items())))

# ---------------------------------------------------------------- échanges réels autour de T0 (cache)
CACHE = D / "echanges_t0.json"
cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
lock, local = threading.Lock(), threading.local()


def trades(cid, start=None, end=None, limit=500):
    if not hasattr(local, "http"):
        local.http = HttpClient(timeout=40, min_interval=0.15)
    params = {"market": cid, "limit": limit}
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    try:
        batch = local.http.get_json(it.TRADES, params=params)
    except SourceUnavailable:
        return None
    return [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"])] for t in batch or []
            if t.get("timestamp") and t.get("price") is not None]


def around(job):
    m, t0 = job
    key = f"{m['cid']}|{t0}"
    if key in cache:
        return
    bef = trades(m["cid"], end=t0, limit=50)                       # les 50 derniers AVANT T0
    aft = trades(m["cid"], start=t0, end=t0 + 2 * DAY, limit=1000)  # ceux des 48 h APRÈS T0
    if aft is not None and len(aft) >= 1000:                       # fenêtre pleine : on resserre à 6 h
        aft = trades(m["cid"], start=t0, end=t0 + 6 * 3600, limit=1000)
    if bef is None or aft is None:
        return  # panne : pas mis en cache, réessayé la prochaine fois
    with lock:
        cache[key] = {"avant": bef, "apres": aft}


jobs = []
for m in cands:
    for h in HORIZONS:
        t0 = m["end"] - h * DAY
        if t0 >= m["start"] + 2 * DAY and (m.get("closed") or m["end"]) > t0:
            jobs.append((m, t0))
todo = [j for j in jobs if f"{j[0]['cid']}|{j[1]}" not in cache]
print(f"instants de décision : {len(jobs)} (à lire : {len(todo)})")
with cf.ThreadPoolExecutor(8) as ex:
    for i, _ in enumerate(ex.map(around, todo)):
        if i % 500 == 499:
            with lock:
                CACHE.write_text(json.dumps(cache))
CACHE.write_text(json.dumps(cache))

# ---------------------------------------------------------------- paris
def yes_price(t, m):
    return t[3] if t[1] == m["yes"] else 1 - t[3]


bets, stats = [], defaultdict(int)
for m, t0 in jobs:
    c = cache.get(f"{m['cid']}|{t0}")
    if c is None:
        stats["panne"] += 1
        continue
    known = [t for t in c["avant"] if t[0] <= t0 and t0 - t[0] <= 7 * DAY]
    if not known:
        stats["sans échange avant"] += 1
        continue
    p = yes_price(max(known, key=lambda t: t[0]), m)
    if not LO <= p <= HI:
        stats["hors plage"] += 1
        continue
    buys = sorted((t for t in c["apres"] if t[0] >= t0 and ((t[1] == m["no"] and t[2] == "BUY") or (t[1] == m["yes"] and t[2] == "SELL"))),
                  key=lambda t: t[0])
    if not buys:
        stats["sans échange après"] += 1
        continue
    b = buys[0]
    cost = b[3] if b[1] == m["no"] else 1 - b[3]
    cost += it.fee(cost, m["rate"])
    if cost >= 0.995:
        stats["NON trop cher"] += 1
        continue
    settle = m.get("closed") or m["end"]
    days = max(1.0, (settle - b[0]) / DAY)
    bets.append(dict(gain=(1 - m["won"]) / cost - 1, evenement=m["ev_id"] or m["id"], cout=cost, p=p, jours=days,
                     mois=datetime.fromtimestamp(t0, tz=timezone.utc).strftime("%Y-%m"), h=round((m["end"] - t0) / DAY),
                     cat=m["cat"], q=m["q"], won=m["won"], t0=t0, hold=m.get("hold"), vol=m["vol"]))
print("écartés :", dict(stats), "; paris :", len(bets))


def summary(name, sub):
    if not sub:
        print(f"   {name} : aucun pari")
        return
    g = sum(x["gain"] * x["cout"] for x in sub)            # gain en $ pour 1 part par pari
    stake = sum(x["cout"] for x in sub)
    stake_days = sum(x["cout"] * x["jours"] for x in sub)
    yes_won, yes_exp = sum(x["won"] for x in sub), sum(x["p"] for x in sub)
    worst = min(sub, key=lambda x: x["gain"])
    v = it.verdict(sub)
    per_day = g / stake_days if stake_days else 0
    print(f"   {name} : {len(sub)} paris, {v['evenements']} événements | rendement par pari {100 * g / stake:+.2f} % "
          f"(moyenne {100 * v.get('rendement_moyen', 0):+.2f} %) | par jour {100 * per_day:+.4f} % (≈ {100 * per_day * 365:+.1f} %/an) | "
          f"durée moyenne {sum(x['jours'] for x in sub) / len(sub):.0f} j | OUI arrivés {yes_won} pour {yes_exp:.1f} attendus | "
          f"t événements {v.get('confiance_evenements')} | mois gagnants {v.get('mois_gagnants')} | {v['verdict']}")
    return v


for h in HORIZONS:
    print(f"\n== Horizon {h} jours avant l'échéance")
    sub = [x for x in bets if x["h"] == h]
    summary("tous", sub)
    for lo, hi in ((0.02, 0.05), (0.05, 0.10), (0.10, 0.15)):
        summary(f"OUI à {lo:.2f}-{hi:.2f}", [x for x in sub if lo <= x["p"] < hi or (hi == 0.15 and x["p"] == 0.15)])
    for cat in DRAME:
        if not TEMOIN:
            summary(cat, [x for x in sub if x["cat"] == cat])
    days = sorted(x["t0"] for x in sub)
    if days:
        cut = days[len(days) // 2]
        summary("première moitié", [x for x in sub if x["t0"] < cut])
        summary("seconde moitié", [x for x in sub if x["t0"] >= cut])

print("\n== Tous horizons confondus (un marché peut compter jusqu'à 3 fois : paris liés, regroupés par événement)")
v = summary("tous", bets)
if v:
    print(json.dumps(v, ensure_ascii=False))
# Pire cas : événements où le NON a perdu
lost = defaultdict(list)
for x in bets:
    if x["won"]:
        lost[x["evenement"]].append(x)
print("\n== Pires cas (le drame est arrivé) :", sum(len(v) for v in lost.values()), "paris perdus sur", len(bets))
for ev, xs in sorted(lost.items(), key=lambda kv: -sum(x["cout"] for x in kv[1]))[:12]:
    print(f"   {len(xs)} pari(s), mise perdue {sum(x['cout'] for x in xs):.2f} $ | {xs[0]['q'][:90]} | OUI payé {xs[0]['p']:.3f} | {xs[0]['mois']}")
by_month = defaultdict(list)
for x in bets:
    by_month[x["mois"]].append(x)
worst_m = min(by_month.items(), key=lambda kv: sum(x["gain"] * x["cout"] for x in kv[1]))
print(f"   pire mois de décision : {worst_m[0]} ({len(worst_m[1])} paris, {sum(x['gain'] * x['cout'] for x in worst_m[1]):+.2f} $ pour "
      f"{sum(x['cout'] for x in worst_m[1]):.2f} $ misés)")
hold = [x for x in bets if x["hold"]]
print(f"   marchés avec récompense de détention (holdingRewardsEnabled) : {len(hold)} paris")
json.dump(bets, open(D / ("paris_temoin.json" if TEMOIN else "paris.json"), "w"))
