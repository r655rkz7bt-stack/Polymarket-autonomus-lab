"""Séismes hebdomadaires (nombre de séismes M>=5,5 / 6,5) : modèle Gamma-Poisson mis à jour par le compte déjà observé,
comparé aux prix des vrais échanges à plusieurs jours de la fin. Sortie : experiments/seismes/releves/hebdo_cas.json"""
import sys, json, math, gzip, statistics as st
sys.path.insert(0, "experiments/seismes/scripts"); sys.path.insert(0, "src")
from commun import *
from math import lgamma, exp, log

def nb_pmf(k, r, p):  # binomiale négative : k échecs avant r succès, proba de succès p
    return exp(lgamma(k + r) - lgamma(r) - lgamma(k + 1) + r * log(p) + k * log(1 - p))

def prior(mag, a):  # lois Gamma-Poisson d'une semaine, calibrées sur les 3 ans AVANT la fenêtre
    W = 7 * 86400
    cs = [count(t, t + W, mag) for t in range(a - 156 * W, a - W + 1, W)]
    m = st.mean(cs); v = max(st.pvariance(cs), m * 1.05)
    alpha = m * m / (v - m); return alpha, alpha / m

def dist(mag, a, b, T, n_obs=None, shrink=1.0):
    """Loi du compte final connaissant les séismes avant T. f = part écoulée de la fenêtre."""
    alpha, beta = prior(mag, a)
    f = (T - a) / (b - a)
    n = count(a, T, mag) if n_obs is None else n_obs
    r = alpha + n; p = (beta + f) / (beta + 1)  # restant ~ NB(r, p)
    return n, f, lambda K: nb_pmf(K - n, r, p) if K >= n else 0.0

def load_trades(eid):
    return json.load(gzip.open(R + f"releves/echanges/echanges_{eid}.json.gz", "rt"))

def last_price(trades, tok, other, T, back):
    """Prix du OUI = dernier échange dans [T-back, T] (achat du OUI, ou vente du NON à 1-p)."""
    pts = [(t[0], t[3] if t[1] == tok else 1 - t[3]) for t in trades if t[1] in (tok, other) and T - back <= t[0] <= T]
    return max(pts)[1] if pts else None

def buy_price(trades, tok, other, T, win):  # prix payé pour ACHETER le OUI : 1er achat dans (T, T+win]
    pts = sorted((t[0], t[3] if t[1] == tok else 1 - t[3]) for t in trades
                 if T < t[0] <= T + win and ((t[1] == tok and t[2] == "BUY") or (t[1] == other and t[2] == "SELL")))
    return pts[0][1] if pts else None

def sell_no_price(trades, tok, other, T, win):  # prix payé pour acheter le NON (token `other`)
    return buy_price(trades, other, tok, T, win)

if __name__ == "__main__":
    cas = []
    for e in sorted(EV.values(), key=lambda e: e["end"]):
        if not e["closed"]: continue
        w = weekly(e)
        if not w: continue
        mag, a, b = w; win = winner(e)
        if not win: continue
        trades = load_trades(e["id"])
        for days in (1, 2, 3, 4, 5, 6):
            T = b - days * 86400
            n, f, pm = dist(mag, a, b, T)
            for m in e["markets"]:
                lo, hi = bucket_of(m)
                if hi < n: continue
                tok, other = m["tokens"][0], m["tokens"][1]
                p_mod = sum(pm(K) for K in range(max(lo, n), min(hi, n + 60) + 1))
                last = last_price(trades, tok, other, T, 6 * 3600)
                ya = buy_price(trades, tok, other, T, 2 * 3600); na = sell_no_price(trades, tok, other, T, 2 * 3600)
                cas.append(dict(ev=e["id"], mois=datetime.fromtimestamp(b, timezone.utc).strftime("%Y-%m"), mag=mag, jours=days, n=n, f=round(f, 3),
                                lo=lo, hi=hi, gagne=int(m["id"] == win["id"]), p=round(p_mod, 4), last=last, ach_oui=ya, ach_non=na))
    json.dump(cas, open(R + "releves/hebdo_cas.json", "w"))
    print(len(cas), "cas;", sum(1 for c in cas if c["last"] is not None), "avec prix")
