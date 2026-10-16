"""Backtest crypto, étape 2 : modèles contre le prix Polymarket, réglés sur la 1re moitié des jours, jugés sur la 2de.

Usage : python3 -I experiments/crypto_backtest/evaluate.py <dossier_de_travail> src
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

WD = sys.argv[1]; sys.path.insert(0, sys.argv[2]); sys.path.insert(0, str(Path(__file__).parent))
from polymarket_agent import idea_test as it
import donnees, modeles as md

cases, skipped = donnees.build_cases(WD)
cases = donnees.attach_trades(WD, [c for c in cases if c.iv is not None])
train, test = it.split_by_day(cases)
print(f"cas : {len(cases)} (apprentissage {len(train)}, jugement {len(test)}) ; écartés : {skipped}")
print(f"jours d'échéance : {len({c.day for c in cases})}, coupure au {min(c.day for c in test)}")
print("par type :", dict(Counter(c.typ for c in cases)), "; par actif :", dict(Counter(c.group for c in cases)))
print("barème de frais :", dict(Counter(c.row.fee_rate for c in cases)))
print("marchés distincts :", len({c.row.market_id for c in cases}))

# ---------------------------------------------------------------- 1. le marché est-il bien étalonné ?
print("\n== Étalonnage du prix du marché (tous les cas) : prix moyen du Oui / fréquence réelle du Oui")
EDGES = (0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.991)
for typ in ("echelle", "barriere", None):
    sel = [c for c in cases if typ is None or c.typ.startswith(typ)]
    line = []
    for a, b in zip(EDGES, EDGES[1:]):
        g = [c for c in sel if a <= c.price < b]
        if g:
            line.append(f"[{a:.2f}-{b:.2f}[ n={len(g)} prix {sum(c.price for c in g) / len(g):.3f} "
                        f"réel {sum(c.row.won for c in g) / len(g):.3f}")
    print(f"-- {typ or 'tous'} :\n   " + "\n   ".join(line))

# ---------------------------------------------------------------- 2. réglages sur l'apprentissage
def fam(c):
    return "echelle" if c.typ == "echelle" else "barriere"


def fit(vol_name, with_t):
    """k (multiplicateur de σ) et nu (Student) par famille, au minimum de log loss sur l'apprentissage."""
    out = {}
    for f in ("echelle", "barriere"):
        sel = [c for c in train if fam(c) == f]
        best = None
        for k in [0.5 + 0.05 * i for i in range(31)]:
            for nu in ((2.5, 3, 4, 6, 10, 30) if with_t else (None,)):
                ll = it.log_loss(sel, lambda c: md.prob(c, getattr(c, vol_name), k, nu))
                if best is None or ll < best[0]:
                    best = (ll, k, nu)
        out[f] = best[1:]
    return out


models = {
    "a. production (σ réalisée, estimation centrale)": lambda c: md.prob(c, c.rv),
    "b. DVOL (σ implicite)": lambda c: md.prob(c, c.iv),
}
fits = {}
for name, vol, t in (("c1. σ réalisée × k", "rv", False), ("c2. σ implicite × k", "iv", False),
                     ("c3. Student, σ réalisée × k", "rv", True), ("c4. Student, σ implicite × k", "iv", True)):
    fits[name] = (vol, fit(vol, t))
    models[name] = (lambda vol, pr: lambda c: md.prob(c, getattr(c, vol), *pr[fam(c)]))(vol, fits[name][1])
for name, (vol, pr) in fits.items():
    print(f"réglage {name} : " + ", ".join(f"{f} k={k:.2f} nu={nu}" for f, (k, nu) in pr.items()))

# mélange : logit(p) = a·logit(modèle) + b·logit(marché) + c, par famille, réglé sur l'apprentissage
for base in ("c2. σ implicite × k", "c4. Student, σ implicite × k"):
    w = {}
    for f in ("echelle", "barriere"):
        sel = [c for c in train if fam(c) == f]
        w[f] = md.fit_logistic([[md.logit(models[base](c)), md.logit(c.price), 1.0] for c in sel],
                               [c.row.won for c in sel])
    print(f"mélange ({base}) : " + ", ".join(f"{f} a={a:.2f} b={b:.2f} c={k:.2f}" for f, (a, b, k) in w.items()))
    models[f"d. mélange marché + {base[:3]}"] = (lambda base, w: lambda c: md.sigmoid(
        w[fam(c)][0] * md.logit(models[base](c)) + w[fam(c)][1] * md.logit(c.price) + w[fam(c)][2]))(base, w)
# marché seul ré-étalonné : logit(p) = b·logit(marché) + c (biais des queues du marché ?)
w0 = {}
for f in ("echelle", "barriere"):
    sel = [c for c in train if fam(c) == f]
    w0[f] = md.fit_logistic([[md.logit(c.price), 1.0] for c in sel], [c.row.won for c in sel])
print("marché ré-étalonné : " + ", ".join(f"{f} b={b:.2f} c={k:.2f}" for f, (b, k) in w0.items()))
models["e. marché ré-étalonné seul"] = lambda c: md.sigmoid(w0[fam(c)][0] * md.logit(c.price) + w0[fam(c)][1])

# ---------------------------------------------------------------- 3. jugement hors échantillon
print("\n== Jugement (seconde moitié des jours) : Brier / log loss, marché en référence")
mk = lambda c: c.price
print(f"marché : Brier {it.brier(test, mk):.4f}, log loss {it.log_loss(test, mk):.4f}")
for f in ("echelle", "barriere"):
    sel = [c for c in test if fam(c) == f]
    print(f"   marché {f} : Brier {it.brier(sel, mk):.4f}, log loss {it.log_loss(sel, mk):.4f} ({len(sel)} cas)")
for name, p in models.items():
    parts = " ; ".join(f"{f} {it.brier([c for c in test if fam(c) == f], p):.4f}/"
                       f"{it.log_loss([c for c in test if fam(c) == f], p):.4f}" for f in ("echelle", "barriere"))
    print(f"{name} : Brier {it.brier(test, p):.4f}, log loss {it.log_loss(test, p):.4f}  ({parts})")

print("\n== Simulation (jugement), 1 part par pari, frais réels, écart simulé")
band = lambda c: md.production_band(c)
sims = {"a0. RÈGLE DE PRODUCTION (bande σ×0,75..1,5)": (lambda c: band(c)[0], lambda c: band(c)[2])}
sims.update({n: (p, None) for n, p in models.items()})
for name, (py, pn) in sims.items():
    print(f"-- {name}")
    for e in (0.03, 0.05, 0.08):
        line = []
        for s in (0.01, 0.02, 0.04):
            tot, det = md.simulate(test, py, pn, e, s)
            line.append(f"écart {s}: {tot['paris']} paris {tot['rendement_pct']} % (jours + {tot['jours_gagnants']})")
        print(f"   seuil {e} : " + " | ".join(line))
    tot, det = md.simulate(test, py, pn, 0.05, 0.02)
    for axe in ("cote", "type", "actif", "horizon"):
        print(f"   [seuil 0,05 écart 0,02] {axe} : {md.fmt_axis(det, axe)}")

# ---------------------------------------------------------------- 3 bis. aux prix RÉELLEMENT payés
real = [c for c in test if c.ask is not None or c.bid is not None]
both = [c for c in test if c.ask is not None and c.bid is not None]
print(f"\n== Aux prix réellement payés par des preneurs dans l'heure avant t (jugement) : "
      f"{len(real)} cas avec au moins un côté, {len(both)} avec les deux")
print(f"   écart achat-vente médian observé (deux côtés) : "
      f"{sorted(c.ask - c.bid for c in both)[len(both) // 2]:.3f}" if both else "")
print(f"   prix historique 0,50 exactement : {sum(1 for c in test if c.price == 0.5)} cas jugés, "
      f"dont {sum(1 for c in real if c.price == 0.5)} avec une transaction récente")
for name, (py, pn) in sims.items():
    line = []
    for e in (0.03, 0.05, 0.08):
        for sl in (0.0, 0.01):
            tot, det = md.simulate_real(test, py, pn, e, sl)
            line.append(f"seuil {e} gliss. {sl}: {tot['paris']} paris {tot['rendement_pct']} % ({tot['jours_gagnants']})")
    print(f"-- {name}\n   " + "\n   ".join(line))
    tot, det = md.simulate_real(test, py, pn, 0.05, 0.0)
    for axe in ("cote", "type", "actif", "horizon"):
        print(f"   [seuil 0,05] {axe} : {md.fmt_axis(det, axe)}")

# ---------------------------------------------------------------- 4. règles simples sur le prix seul
print("\n== Règles sur le prix seul (sans modèle), écart 0,02 : apprentissage | jugement")
rules = {
    "NON si Oui < 0,10": lambda c: c.price < 0.10,
    "NON si Oui 0,10-0,20": lambda c: 0.10 <= c.price < 0.20,
    "NON si Oui 0,20-0,40": lambda c: 0.20 <= c.price < 0.40,
    "OUI si Oui 0,60-0,80": lambda c: 0.60 <= c.price < 0.80,
    "OUI si Oui 0,80-0,90": lambda c: 0.80 <= c.price < 0.90,
    "OUI si Oui > 0,90": lambda c: c.price >= 0.90,
}
for f in ("echelle", "barriere"):
    for name, cond in rules.items():
        side = "NON" if name.startswith("NON") else "OUI"
        res = []
        for part in (train, test):
            sel = [c for c in part if fam(c) == f and cond(c)]
            always = (lambda c: 1.0) if side == "OUI" else (lambda c: 0.0)
            tot, _ = md.simulate(sel, always, None, -1.0, 0.02, sides=(side,))
            res.append(f"{tot['paris']} paris {tot['rendement_pct']} % (jours + {tot['jours_gagnants']})")
        print(f"{f:8s} {name:22s}: " + " | ".join(res))
