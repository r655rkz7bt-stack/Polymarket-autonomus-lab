"""Backtest crypto : modèles candidats, simulation détaillée et utilitaires de réglage (pur Python)."""
import math
from collections import defaultdict

from polymarket_agent import crypto_model as cm
from polymarket_agent import idea_test as it


# ---------------------------------------------------------------- loi de Student (queues épaisses)
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-30 else 1e-30)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-30 else 1e-30)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-30 else 1e-30
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-30 else 1e-30)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-30 else 1e-30
        de = d * c
        h *= de
        if abs(de - 1) < 1e-12:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * _betacf(a, b, x) / a
    return 1 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def t_cdf(x, nu):
    """Fonction de répartition de la loi de Student à nu degrés de liberté."""
    tail = 0.5 * _ibeta(nu / 2, 0.5, nu / (nu + x * x))
    return 1 - tail if x > 0 else tail


def prob(c, vol, k=1.0, nu=None):
    """P(Oui) : log-normale (nu None) ou Student de variance unité (queues épaisses)."""
    q, s = c.q, vol * k * math.sqrt(c.hours)
    z = math.log(q.threshold / c.spot) / s
    if nu is None:
        F = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
    else:
        scale = math.sqrt((nu - 2) / nu)
        F = lambda x: t_cdf(x / scale, nu)
    if q.kind == "above":
        p = 1 - F(z)
    elif q.kind == "below":
        p = F(z)
    elif q.kind == "touch_up":
        p = min(1.0, 2 * (1 - F(z)))
    else:
        p = min(1.0, 2 * F(z))
    return min(0.999, max(0.001, p))


def production_band(c):
    """Bande de la production actuelle (σ réalisée × 0,75 / 1 / 1,5)."""
    return cm.probability_band(c.q, c.spot, c.rv, c.hours)


# ---------------------------------------------------------------- mélange avec le prix du marché
def logit(p):
    p = min(0.999, max(0.001, p))
    return math.log(p / (1 - p))


def fit_logistic(xs, ys, ridge=1e-3, iters=50):
    """Régression logistique (Newton), xs = listes de variables (constante incluse)."""
    n = len(xs[0]); w = [0.0] * n
    for _ in range(iters):
        g = [0.0] * n; Hm = [[ridge if i == j else 0.0 for j in range(n)] for i in range(n)]
        for x, y in zip(xs, ys):
            z = sum(wi * xi for wi, xi in zip(w, x)); p = 1 / (1 + math.exp(-max(-30, min(30, z))))
            for i in range(n):
                g[i] += (p - y) * x[i]
                for j in range(n):
                    Hm[i][j] += p * (1 - p) * x[i] * x[j]
        for i in range(n):
            g[i] += ridge * w[i]
        step = _solve(Hm, g)
        w = [wi - si for wi, si in zip(w, step)]
        if max(abs(s) for s in step) < 1e-9:
            break
    return w


def _solve(A, b):
    n = len(b); M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[piv] = M[piv], M[i]
        for r in range(n):
            if r != i and M[i][i]:
                f = M[r][i] / M[i][i]
                M[r] = [a - f * b2 for a, b2 in zip(M[r], M[i])]
    return [M[i][n] / M[i][i] if M[i][i] else 0.0 for i in range(n)]


def sigmoid(z):
    return 1 / (1 + math.exp(-max(-30, min(30, z))))


# ---------------------------------------------------------------- simulation détaillée
def bucket(p):
    return "<0,2" if p < 0.2 else "0,2-0,8" if p <= 0.8 else ">0,8"


def simulate(cases, p_yes, p_no=None, edge=0.05, spread=0.01, sides=("OUI", "NON")):
    """1 part par pari. p_yes(c) : proba du Oui pour juger l'achat du Oui ; p_no(c) : proba du Oui
    pour juger l'achat du Non (bande : borne basse / haute). Frais réels du marché (barème rate)."""
    p_no = p_no or p_yes
    tot = {"paris": 0, "gagnants": 0, "resultat": 0.0, "mise": 0.0}
    det = defaultdict(lambda: defaultdict(lambda: [0, 0.0, 0.0]))  # axe -> clé -> [paris, résultat, mise]
    for c in cases:
        rate = c.row.fee_rate
        yes, no = c.price + spread, 1 - c.price + spread
        py, pn = p_yes(c), p_no(c)
        if "OUI" in sides and yes < 1 and py - yes - it.fee(yes, rate) > edge:
            side, cost, gain = "OUI", yes, c.row.won - yes - it.fee(yes, rate)
        elif "NON" in sides and no < 1 and (1 - pn) - no - it.fee(no, rate) > edge:
            side, cost, gain = "NON", no, (1 - c.row.won) - no - it.fee(no, rate)
        else:
            continue
        tot["paris"] += 1; tot["gagnants"] += gain > 0; tot["resultat"] += gain; tot["mise"] += cost
        for axe, key in (("cote", f"{side} {bucket(cost)}"), ("type", c.typ), ("actif", c.group),
                         ("horizon", f"{int(c.hours)} h"), ("jour", c.day)):
            d = det[axe][key]; d[0] += 1; d[1] += gain; d[2] += cost
    tot["rendement_pct"] = round(100 * tot["resultat"] / tot["mise"], 1) if tot["mise"] else None
    jours = det["jour"]
    tot["jours_gagnants"] = f"{sum(1 for v in jours.values() if v[1] > 0)} / {len(jours)}"
    return tot, det


def fmt_axis(det, axe):
    rows = []
    for k, (n, g, m) in sorted(det[axe].items()):
        rows.append(f"{k}: {n} paris, {round(100 * g / m, 1) if m else '-'} %")
    return " ; ".join(rows)


def simulate_real(cases, p_yes, p_no=None, edge=0.05, slip=0.0, sides=("OUI", "NON")):
    """Comme simulate, mais au prix RÉELLEMENT payé par un preneur dans l'heure avant t
    (c.ask pour le Oui, 1 − c.bid pour le Non), plus un glissement `slip` ; côté sans transaction
    récente = pas de pari possible. Le modèle est évalué à l'instant de cette transaction
    (c.ask_case, c.bid_case), pas à t : aucun avantage tiré d'un prix périmé."""
    p_no = p_no or p_yes
    tot = {"paris": 0, "gagnants": 0, "resultat": 0.0, "mise": 0.0}
    det = defaultdict(lambda: defaultdict(lambda: [0, 0.0, 0.0]))
    for c in cases:
        rate = c.row.fee_rate
        yes = c.ask + slip if c.ask is not None else None
        no = 1 - c.bid + slip if c.bid is not None else None
        py = p_yes(c.ask_case) if yes is not None else None
        pn = p_no(c.bid_case) if no is not None else None
        if "OUI" in sides and yes is not None and yes < 1 and py - yes - it.fee(yes, rate) > edge:
            side, cost, gain = "OUI", yes, c.row.won - yes - it.fee(yes, rate)
        elif "NON" in sides and no is not None and no < 1 and (1 - pn) - no - it.fee(no, rate) > edge:
            side, cost, gain = "NON", no, (1 - c.row.won) - no - it.fee(no, rate)
        else:
            continue
        tot["paris"] += 1; tot["gagnants"] += gain > 0; tot["resultat"] += gain; tot["mise"] += cost
        for axe, key in (("cote", f"{side} {bucket(cost)}"), ("type", c.typ), ("actif", c.group),
                         ("horizon", f"{int(c.hours)} h"), ("jour", c.day)):
            d = det[axe][key]; d[0] += 1; d[1] += gain; d[2] += cost
    tot["rendement_pct"] = round(100 * tot["resultat"] / tot["mise"], 1) if tot["mise"] else None
    jours = det["jour"]
    tot["jours_gagnants"] = f"{sum(1 for v in jours.values() if v[1] > 0)} / {len(jours)}"
    return tot, det
