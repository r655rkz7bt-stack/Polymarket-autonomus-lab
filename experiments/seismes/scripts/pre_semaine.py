"""16/11/2026 (passage de 11 h) : les marchés « How many 5.5 / 6.5 or above earthquakes worldwide <lundi> - <dimanche> » ouvrent ~3 jours AVANT
la semaine ; `seismes_marche` ne joue qu'entre 6,6 et 0,5 jour avant la fin (fenêtre testée le 24/10). Question : AVANT le début de la semaine
(et dans ses 10 premières heures), la loi a priori (binomiale négative des 156 semaines d'avant, rien d'observé) bat-elle le prix ?
Données : relevés du 24/10 (evenements.json.gz, echanges/, catalogue usgs_m5) ; prix = premier vrai achat dans les 2 h après T.
Sortie : releves/pre_semaine_cas.json et un résumé."""
import sys, json, math
sys.path.insert(0, "experiments/seismes/scripts"); sys.path.insert(0, "src")
from commun import *
from hebdo import prior, dist, nb_pmf, load_trades, last_price, buy_price, sell_no_price
from polymarket_agent.idea_test import verdict

H = 3600
OFFSETS = (-60, -48, -36, -24, -12, 0, 6)   # heures par rapport au début de la semaine (lundi 0 h, heure de l'Est)

def p_bucket(mag, a, b, T, lo, hi):
    if T <= a:
        alpha, beta = prior(mag, a)
        r, p = alpha, beta / (beta + 1)
        return sum(nb_pmf(K, r, p) for K in range(lo, min(hi, 80) + 1))
    n, f, pm = dist(mag, a, b, T)
    if hi < n: return 0.0
    return sum(pm(K) for K in range(max(lo, n), min(hi, n + 60) + 1))

cas = []
for e in sorted(EV.values(), key=lambda e: e["end"]):
    if not e["closed"]: continue
    w = weekly(e)
    if not w: continue
    mag, a, b = w; win = winner(e)
    if not win: continue
    try: trades = load_trades(e["id"])
    except FileNotFoundError: continue
    for off in OFFSETS:
        T = a + off * H
        for m in e["markets"]:
            bk = bucket_of(m)
            if not bk or len(m["tokens"]) < 2: continue
            lo, hi = bk; tok, other = m["tokens"]
            pm = p_bucket(mag, a, b, T, lo, hi)
            cas.append(dict(ev=e["id"], mois=datetime.fromtimestamp(b, timezone.utc).strftime("%Y-%m"), mag=mag, h=off, lo=lo, hi=hi,
                            gagne=int(m["id"] == win["id"]), p=round(pm, 4), last=last_price(trades, tok, other, T, 6 * H),
                            ach_oui=buy_price(trades, tok, other, T, 2 * H), ach_non=sell_no_price(trades, tok, other, T, 2 * H)))
json.dump(cas, open(R + "releves/pre_semaine_cas.json", "w"))
print(len(cas), "cas")

def fee(p, rate): return rate * p * (1 - p)

for mag in (5.5, 6.5):
    for off in OFFSETS:
        cs = [c for c in cas if c["mag"] == mag and c["h"] == off and c["last"] is not None]
        if not cs: continue
        ls_m = sum(math.log(max(1e-3, c["p"] if c["gagne"] else 1 - c["p"])) for c in cs) / len(cs)
        ls_p = sum(math.log(max(1e-3, c["last"] if c["gagne"] else 1 - c["last"])) for c in cs) / len(cs)
        print(f"M{mag} h{off:+d} : {len(cs)} tranches avec prix, log-score modèle {ls_m:.3f} contre prix {ls_p:.3f}")

for rate in (0.0, 0.05):
    for seuil in (0.03, 0.05, 0.10):
        for mag in (5.5, 6.5):
            paris = []
            for c in cas:
                if c["mag"] != mag or c["h"] > 0: continue
                for cote, prix, est, paie in (("oui", c["ach_oui"], c["p"], c["gagne"]), ("non", c["ach_non"], 1 - c["p"], 1 - c["gagne"])):
                    if prix is None or not 0.05 <= prix <= 0.95: continue
                    if est - prix - fee(prix, rate) < seuil: continue
                    paris.append(dict(event=c["ev"], ev=c["ev"], mois=c["mois"], price=prix, prix=prix, won=paie, gagne=paie, pay=paie,
                                      ret=(paie - prix - fee(prix, rate)) / prix, h=c["h"], cote=cote))
            # un pari par (événement, tranche, côté) : le premier instant
            vu, uniques = set(), []
            for p in sorted(paris, key=lambda p: p["h"]):
                k = (p["ev"], p["prix"], p["cote"])
                if k in vu: continue
                vu.add(k); uniques.append(p)
            if not uniques: continue
            n = len(uniques); g = sum(p["won"] for p in uniques); att = sum(p["price"] for p in uniques)
            rend = sum(p["ret"] * p["price"] for p in uniques) / att
            evs = len({p["ev"] for p in uniques})
            print(f"frais {rate} seuil {seuil} M{mag} : {n} paris ({evs} événements), {g} gagnés pour {att:.1f} attendus, rendement {rend:+.1%}")
