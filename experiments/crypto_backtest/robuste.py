"""Backtest crypto, étape 3 : contrôles de robustesse AUX PRIX RÉELLEMENT PAYÉS (transactions).

Usage : python3 -I experiments/crypto_backtest/robuste.py <dossier_de_travail> src
1. Étalonnage du marché au dernier prix d'échange (pas au milieu d'un carnet vide).
2. Les mêmes simulations sur l'APPRENTISSAGE et sur le JUGEMENT, détail par cote : une règle
   (« pas de billets de loterie », « seulement le Non »…) n'est retenue que si elle est vue dès
   l'apprentissage, puis confirmée sur le jugement.
3. Effet du prix périmé : modèle évalué à t (prix d'échange jusqu'à 1 h plus ancien) contre
   modèle évalué à l'instant exact de l'échange.
"""
import sys
from collections import defaultdict
from pathlib import Path

WD = sys.argv[1]; sys.path.insert(0, sys.argv[2]); sys.path.insert(0, str(Path(__file__).parent))
from polymarket_agent import idea_test as it
import donnees, modeles as md

cases, _ = donnees.build_cases(WD)
cases = donnees.attach_trades(WD, [c for c in cases if c.iv is not None])
train, test = it.split_by_day(cases)
fam = lambda c: "echelle" if c.typ == "echelle" else "barriere"

# 1. étalonnage au dernier prix d'échange (côté acheteur ou vendeur, le plus récent des deux)
print("== Étalonnage au dernier prix d'échange de l'heure (tous les jours) : prix moyen / fréquence du Oui")
EDGES = (0.0, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0)
for f in ("echelle", "barriere"):
    sel = []
    for c in cases:
        if fam(c) != f:
            continue
        pts = [(x.t, x.price) for x in (c.ask_case, c.bid_case) if x is not None]
        if pts:
            sel.append((max(pts)[1], c.row.won))
    out = []
    for a, b in zip(EDGES, EDGES[1:]):
        g = [(p, w) for p, w in sel if a <= p < b]
        if g:
            out.append(f"[{a:.2f}-{b:.2f}[ n={len(g)} prix {sum(p for p, _ in g) / len(g):.3f} "
                       f"réel {sum(w for _, w in g) / len(g):.3f}")
    print(f"-- {f} ({len(sel)} cas) :\n   " + "\n   ".join(out))

# 2. réglage k sur l'apprentissage (comme evaluate.py), puis simulations des deux côtés de la coupure
def fit_k(vol):
    best = {}
    for f in ("echelle", "barriere"):
        sel = [c for c in train if fam(c) == f]
        best[f] = min((it.log_loss(sel, lambda c: md.prob(c, getattr(c, vol), k)), k)
                      for k in [0.5 + 0.05 * i for i in range(31)])[1]
    return best


k_iv, k_rv = fit_k("iv"), fit_k("rv")
band = md.production_band
models = {
    "production (bande)": (lambda c: band(c)[0], lambda c: band(c)[2]),
    "production (centrale)": (lambda c: md.prob(c, c.rv), None),
    "σ réalisée × k": (lambda c: md.prob(c, c.rv, k_rv[fam(c)]), None),
    "DVOL": (lambda c: md.prob(c, c.iv), None),
    "DVOL × k": (lambda c: md.prob(c, c.iv, k_iv[fam(c)]), None),
}
print(f"\nk réglés sur l'apprentissage : σ implicite {k_iv}, σ réalisée {k_rv}")
for name, (py, pn) in models.items():
    print(f"\n-- {name}")
    for e in (0.03, 0.05, 0.08):
        res = []
        for part in (train, test):
            tot, det = md.simulate_real(part, py, pn, e, 0.0)
            res.append(f"{tot['paris']} paris {tot['rendement_pct']} % ({tot['jours_gagnants']})")
        print(f"   seuil {e} : apprentissage {res[0]} | jugement {res[1]}")
    for part_name, part in (("apprentissage", train), ("jugement", test)):
        tot, det = md.simulate_real(part, py, pn, 0.05, 0.0)
        print(f"   [seuil 0,05, {part_name}] cote : {md.fmt_axis(det, 'cote')}")
        print(f"   [seuil 0,05, {part_name}] type : {md.fmt_axis(det, 'type')}")
        print(f"   [seuil 0,05, {part_name}] actif : {md.fmt_axis(det, 'actif')}")

# 3. effet du prix périmé : même prix d'échange, modèle à t au lieu de l'instant de l'échange
print("\n== Effet du prix périmé (DVOL, seuil 0,05, jugement)")
for label, use_t in (("modèle à t (prix d'échange jusqu'à 1 h plus ancien)", True),
                     ("modèle à l'instant de l'échange", False)):
    saved = [(c, c.ask_case, c.bid_case) for c in test]
    if use_t:
        for c in test:
            c.ask_case = c if c.ask_case is not None else None
            c.bid_case = c if c.bid_case is not None else None
    tot, _ = md.simulate_real(test, models["DVOL"][0], None, 0.05, 0.0)
    for c, a, b in saved:
        c.ask_case, c.bid_case = a, b
    print(f"   {label} : {tot['paris']} paris {tot['rendement_pct']} % ({tot['jours_gagnants']})")

# 4. règles sur le prix d'échange seul (sans modèle) : les queues bon marché sont-elles sous-cotées ?
print("\n== Règles sur le prix d'échange seul (achat au prix payé par un preneur), apprentissage | jugement")
RULES = {"OUI si Oui < 0,05": ("OUI", lambda p: p < 0.05), "OUI si Oui 0,05-0,20": ("OUI", lambda p: 0.05 <= p < 0.2),
         "NON si Oui < 0,05": ("NON", lambda p: p < 0.05), "NON si Oui 0,05-0,20": ("NON", lambda p: 0.05 <= p < 0.2),
         "OUI si Oui > 0,95": ("OUI", lambda p: p > 0.95), "NON si Oui > 0,80": ("NON", lambda p: p > 0.8)}
for f in ("echelle", "barriere"):
    for name, (side, cond) in RULES.items():
        res = []
        for part in (train, test):
            sel = [c for c in part if fam(c) == f and
                   ((side == "OUI" and c.ask is not None and cond(c.ask)) or
                    (side == "NON" and c.bid is not None and cond(c.bid)))]
            always = (lambda c: 1.0) if side == "OUI" else (lambda c: 0.0)
            tot, _ = md.simulate_real(sel, always, None, -1.0, 0.0, sides=(side,))
            res.append(f"{tot['paris']} paris {tot['rendement_pct']} % ({tot['jours_gagnants']})")
        print(f"{f:8s} {name:22s}: " + " | ".join(res))
for a in ("bitcoin", "ethereum"):
    s = donnees.Series(donnees._load(WD, "klines.json.gz")[a])
    print(f"{a} : 17/08 {s.spot(donnees.it._ts('2026-08-17T16:00:00Z')):.0f}, 16/09 "
          f"{s.spot(donnees.it._ts('2026-09-16T16:00:00Z')):.0f}, 15/10 {s.spot(donnees.it._ts('2026-10-15T16:00:00Z')):.0f}")

# 5. précision des probabilités À L'INSTANT d'un échange : modèle contre prix de cet échange
print("\n== Brier / log loss à l'instant du dernier échange (modèle et prix vus au même instant)")
for part_name, part in (("apprentissage", train), ("jugement", test)):
    pts = []
    for c in part:
        xs = [x for x in (c.ask_case, c.bid_case) if x is not None]
        if xs:
            pts.append(max(xs, key=lambda x: x.t))
    for f in ("echelle", "barriere"):
        sel = [x for x in pts if fam(x) == f]
        line = [f"marché {it.brier(sel, lambda x: x.price):.4f}/{it.log_loss(sel, lambda x: x.price):.4f}"]
        for name in ("production (centrale)", "σ réalisée × k", "DVOL", "DVOL × k"):
            p = models[name][0]
            line.append(f"{name} {it.brier(sel, p):.4f}/{it.log_loss(sel, p):.4f}")
        print(f"   {part_name} {f} ({len(sel)} cas) : " + " ; ".join(line))
