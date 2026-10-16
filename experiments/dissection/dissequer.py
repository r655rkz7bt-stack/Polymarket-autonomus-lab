"""Dissection d'une stratégie mère : quels MORCEAUX de ses paris gagnent ? (17/10/2026)

Usage : python3 -I experiments/dissection/dissequer.py <dossier_de_travail> src naive_favorite news_momentum …
Lit le journal fantôme de chaque stratégie (branche `data`, fichiers publics), retrouve chaque
marché sur Gamma (catégorie, question, prix actuel ou résultat) et range chaque pari selon :
famille de marchés (barème de frais), tranche de prix payé, délai jusqu'à l'échéance, issue
achetée (OUI / NON / autre : équipe, joueur…). Résultat par pari = réglé (paiement − coût) ou,
s'il est encore ouvert, valeur au prix actuel − coût (LATENT : pas un gain acquis).
C'est une photographie sur peu de paris : elle sert à choisir quels morceaux mettre dans l'arène
(variantes « filles », voir config/strategies.yaml), pas à conclure.
"""
import json
import os
import subprocess
import sys
from collections import defaultdict

WD, SRC, names = sys.argv[1], sys.argv[2], sys.argv[3:]
sys.path.insert(0, SRC)
from polymarket_agent.http_client import HttpClient, SourceUnavailable  # noqa: E402

http = HttpClient(min_interval=0.1)
CACHE = os.path.join(WD, "gamma_markets.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def market(mid):
    if mid not in cache:
        try:
            cache[mid] = http.get_json(f"https://gamma-api.polymarket.com/markets/{mid}")
        except SourceUnavailable:
            cache[mid] = None
    return cache[mid]


def family(m):
    if m is None:
        return "inconnue"
    if m.get("feesEnabled") is False:
        return "sans_frais"
    return str(m.get("feeType") or "other").split("_")[0]


def bucket(price):
    return "0,80-0,875" if price < 0.875 else "0,875-0,95" if price < 0.95 else "≥ 0,95" if price >= 0.5 else "< 0,5"


def delay(h):
    return "< 24 h" if h < 24 else "1-7 jours" if h < 168 else "> 7 jours"


for name in names:
    raw = subprocess.run(["git", "show", f"origin/data:ledger/fantome/{name}_v1.0.0.jsonl"],
                         capture_output=True, text=True).stdout
    entries = [json.loads(l) for l in raw.splitlines() if l.strip()]
    settle = {e["data"]["token_id"]: float(e["data"]["payout_per_share"]) for e in entries if e["type"] == "SETTLE"}
    pos = {}
    for e in entries:
        if e["type"] != "BUY":
            continue
        d = e["data"]
        p = pos.setdefault(d["token_id"], {"mid": d["market_id"], "outcome": d["outcome"], "shares": 0.0, "cost": 0.0,
                                           "h": float((d.get("extra") or {}).get("horizon_hours") or 0)})
        p["shares"] += float(d["shares"])
        p["cost"] += float(d["shares"]) * float(d["price"]) + float(d.get("fee") or 0)
    sold = defaultdict(float)
    for e in entries:
        if e["type"] == "SELL":
            sold[e["data"]["token_id"]] += float(e["data"]["shares"]) * float(e["data"]["price"]) - float(e["data"].get("fee") or 0)
    rows = []
    for tok, p in pos.items():
        m = market(p["mid"])
        price = p["cost"] / p["shares"] if p["shares"] else 0
        if tok in settle:
            value, state = settle[tok] * p["shares"], "réglé"
        else:
            try:
                outs, prices = json.loads(m["outcomes"]), json.loads(m["outcomePrices"])
                value, state = float(prices[outs.index(p["outcome"])]) * p["shares"], "latent"
            except (TypeError, ValueError, KeyError):
                value, state = p["cost"], "inconnu"
        value += sold.get(tok, 0)
        side = "OUI" if p["outcome"].lower() == "yes" else "NON" if p["outcome"].lower() == "no" else "autre (équipe, joueur…)"
        rows.append({"famille": family(m), "prix": bucket(price), "délai": delay(p["h"]), "issue": side,
                     "état": state, "gain": value - p["cost"], "coût": p["cost"],
                     "q": (m or {}).get("question", "?")})
    json.dump(cache, open(CACHE, "w"))
    print(f"\n## {name} : {len(rows)} paris ({sum(r['état'] == 'réglé' for r in rows)} réglés)")
    for dim in ("famille", "prix", "délai", "issue"):
        print(f"\n| {dim} | paris (réglés) | mise | résultat réglé | résultat latent | rendement total |\n|---|---|---|---|---|---|")
        groups = defaultdict(list)
        for r in rows:
            groups[r[dim]].append(r)
        for k, v in sorted(groups.items(), key=lambda kv: -sum(r["coût"] for r in kv[1])):
            c = sum(r["coût"] for r in v)
            gs = sum(r["gain"] for r in v if r["état"] == "réglé")
            gl = sum(r["gain"] for r in v if r["état"] != "réglé")
            print(f"| {k} | {len(v)} ({sum(r['état'] == 'réglé' for r in v)}) | {c:.0f} | {gs:+.1f} | {gl:+.1f} | {100 * (gs + gl) / c:+.1f} % |")
