"""Test sport Kalshi, étape 4 : le prix Kalshi prévoit-il mieux que le prix Polymarket ? (hors échantillon)

Usage : python3 -I experiments/sport_kalshi/evaluate.py <dossier_de_travail> src
Lit props.json (étape 2) et prix/ (étape 3). Écrit <dossier>/resultats.json et affiche des tableaux.

Pour chaque proposition et chaque instant de décision (24 h, 6 h, 2 h, 30 min avant le coup d'envoi) :
- prix Polymarket = dernier point de l'historique AU PLUS TARD à l'instant de décision (au plus 6 h avant) ;
- prix Kalshi = milieu (meilleur acheteur + meilleur vendeur) / 2 à la fin de la dernière minute close
  AU PLUS TARD à l'instant de décision (au plus 6 h avant). Match à 2 issues : moyenne de « A gagne » et de
  1 − « B gagne » (les deux marchés Kalshi du match).
Modèles jugés contre le prix Polymarket (harnais `polymarket_agent.idea_test`) :
  (a) Kalshi seul ; (b) moyenne Kalshi / Polymarket ; (c) Polymarket déplacé vers Kalshi d'un facteur k
  réglé sur la première moitié des dates. Jugement sur la seconde moitié des dates ; simulation 1 part par
  pari, achat sur Polymarket du côté que le modèle juge sous-coté, frais réels (taux × p × (1 − p)), écart
  achat-vente simulé.
"""
import bisect, gzip, json, math, sys
from collections import defaultdict
from pathlib import Path
W, SRC = sys.argv[1], sys.argv[2]
sys.path[:0] = [str(Path(__file__).resolve().parent), SRC]
from common import day  # noqa: E402
from polymarket_agent.idea_test import Case, Resolved, brier, log_loss, simulate, split_by_day  # noqa: E402

DECISIONS = {"24 h": 24 * 3600, "6 h": 6 * 3600, "2 h": 2 * 3600, "30 min": 1800}
STALE = 6 * 3600
EDGES, SPREADS = (0.0, 0.02, 0.03, 0.05), (0.0, 0.01, 0.02)  # écart 0 = cas optimiste (irréaliste)
PRIX = Path(W) / "prix"
FAMILY = {"mlb": "baseball", "nfl": "foot US", "cfb": "foot US univ.", "nhl": "hockey", "nba": "basket",
          "wnba": "basket"}


def load(path):
    try:
        return json.loads(gzip.decompress(path.read_bytes()))
    except FileNotFoundError:
        return None


def last_before(rows, t):
    """Dernière ligne dont l'horodatage est <= t (jamais après), et pas plus vieille que STALE."""
    if not rows:
        return None
    i = bisect.bisect_right([r[0] for r in rows], t) - 1
    return rows[i] if i >= 0 and rows[i][0] >= t - STALE else None


def k_mid(rows, t):
    r = last_before(rows, t)
    if not r or r[1] is None or r[2] is None or not (0 < r[1] < r[2] <= 1):
        return None, None
    return (r[1] + r[2]) / 2, r[2] - r[1]


props = json.load(open(f"{W}/props.json"))
cases_by = defaultdict(list)
missing = defaultdict(int)
follow = defaultdict(list)
for p in props:
    pm = load(PRIX / f"pm_{p['pm_token'][:40]}_{p['start']}.json.gz")
    ka = load(PRIX / f"k_{p['k_ticker']}_{p['start']}.json.gz")
    kb = load(PRIX / f"k_{p['k_opp']}_{p['start']}.json.gz") if p["k_opp"] else None
    for name, off in DECISIONS.items():
        t = p["start"] - off
        ppm = last_before(pm, t)
        ma, sa = k_mid(ka, t)
        mb, sb = k_mid(kb, t) if kb is not None else (None, None)
        ks = [x for x in (ma, None if mb is None else 1 - mb) if x is not None]
        if not ppm or not ks:
            missing[name] += 1
            continue
        price, pk = float(ppm[1]), sum(ks) / len(ks)
        if not (0.01 < price < 0.99):
            missing[name] += 1
            continue
        row = Resolved(p["pm_market"], p["pm_event"], p["pm_event"], p["label"], p["pm_token"], p["won"], p["start"],
                       fee_rate=p["fee"], extra={"pk": pk, "kspread": min(s for s in (sa, sb) if s is not None),
                                                 "kind": p["kind"]})
        cases_by[name].append(Case(row, price, group=p["league"], day=day(t)))
        # Qui suit qui : prix Polymarket 15 min plus tard (toujours avant le coup d'envoi).
        later = last_before(pm, t + 900) if off > 900 else None
        if later:
            follow[name].append((pk - price, float(later[1]) - price))

clip = lambda x: min(0.99, max(0.01, x))
kalshi = lambda c: clip(c.row.extra["pk"])
average = lambda c: clip((c.row.extra["pk"] + c.price) / 2)
market = lambda c: c.price


def fit_k(train):
    """Facteur k (prix PM + k × (Kalshi − PM)) qui minimise la log loss sur l'apprentissage."""
    grid = [i / 20 for i in range(0, 31)]
    return min(grid, key=lambda k: log_loss(train, lambda c: clip(c.price + k * (c.row.extra["pk"] - c.price))))


def pct(sim):
    t = sim["total"]
    days = sim["par_jour"]
    return {"paris": t["paris"], "rendement_pct": t["rendement_pct"], "resultat": t["resultat"],
            "jours_gagnants": sum(1 for v in days.values() if v > 0), "jours": len(days),
            "ligues_gagnantes": sim["groupes_gagnants"], "ligues": sim["groupes"]}


report = {"manquants": dict(missing)}
for name, cases in cases_by.items():
    train, test = split_by_day(cases)
    k = fit_k(train)
    shifted = lambda c, k=k: clip(c.price + k * (c.row.extra["pk"] - c.price))
    models = {"(a) Kalshi seul": kalshi, "(b) moyenne": average, f"(c) PM déplacé k={k}": shifted}
    gap = [abs(c.row.extra["pk"] - c.price) for c in cases]
    r = {"cas": len(cases), "apprentissage": len(train), "test": len(test),
         "coupure": min(c.day for c in test) if test else None, "k": k,
         "ecart_moyen": round(sum(gap) / len(gap), 4), "ecart_sup_3pts": round(sum(g > 0.03 for g in gap) / len(gap), 3),
         "ecarts": {f"> {x}": sum(g > x for g in gap) for x in (0.01, 0.02, 0.03, 0.05, 0.10)},
         # Question simple, sur TOUT l'échantillon (aucun réglage pour ces deux-là) :
         "brier_tout": {"Polymarket": round(brier(cases, market), 4), "Kalshi": round(brier(cases, kalshi), 4)},
         "logloss_tout": {"Polymarket": round(log_loss(cases, market), 4), "Kalshi": round(log_loss(cases, kalshi), 4)},
         "brier_test": {"Polymarket": round(brier(test, market), 4)},
         "logloss_test": {"Polymarket": round(log_loss(test, market), 4)}, "simulations": {}, "par_ligue": {}}
    for mname, f in models.items():
        r["brier_test"][mname] = round(brier(test, f), 4)
        r["logloss_test"][mname] = round(log_loss(test, f), 4)
        for e in EDGES:
            for s in SPREADS:
                r["simulations"][f"{mname} | seuil {e} | écart {s}"] = pct(simulate(test, f, e, s))
    # Détail par ligue (modèle a, sur le test) : Brier et simulation seuil 0,03 / écart 0,01
    by_lg = defaultdict(list)
    for c in test:
        by_lg[c.group].append(c)
    for lg, cs in sorted(by_lg.items()):
        sim = simulate(cs, kalshi, 0.03, 0.01)
        r["par_ligue"][lg] = {"cas": len(cs), "brier_pm": round(brier(cs, market), 4), "brier_k": round(brier(cs, kalshi), 4),
                              "paris": sim["total"]["paris"], "rendement_pct": sim["total"]["rendement_pct"],
                              "resultat": sim["total"]["resultat"]}
    # Kalshi liquide seulement (écart achat-vente Kalshi <= 0,02) : le prix Kalshi est-il plus fiable ?
    liq = [c for c in test if c.row.extra["kspread"] <= 0.02]
    r["kalshi_liquide"] = {"cas": len(liq), "brier_pm": round(brier(liq, market), 4), "brier_k": round(brier(liq, kalshi), 4),
                           **{f"seuil {e} | écart 0.01": pct(simulate(liq, kalshi, e, 0.01)) for e in EDGES}}
    # Qui suit qui : quand Kalshi est au-dessus de Polymarket de plus de 0,02, le prix Polymarket
    # monte-t-il dans les 15 min ? (pente de la régression du mouvement PM sur l'écart.)
    fl = follow.get(name) or []
    if fl:
        sxx = sum(g * g for g, _ in fl)
        big = [(g, d) for g, d in fl if abs(g) > 0.02]
        r["suivi_15min"] = {"n": len(fl), "pente": round(sum(g * d for g, d in fl) / sxx, 3) if sxx else None,
                            "n_ecart_sup_2pts": len(big),
                            "mouvement_moyen_dans_le_sens_de_kalshi": round(sum(d if g > 0 else -d for g, d in big) / len(big), 4) if big else None}
    report[name] = r

json.dump(report, open(f"{W}/resultats.json", "w"), indent=1, ensure_ascii=False)
print("manquants (pas de prix des deux côtés à l'instant de décision) :", dict(missing))
for name in DECISIONS:
    r = report.get(name)
    if not r:
        continue
    print(f"\n## {name} avant le coup d'envoi : {r['cas']} cas (test {r['test']} à partir du {r['coupure']}), k = {r['k']}")
    print(f"écart moyen |Kalshi − PM| {r['ecart_moyen']} ; part des écarts > 0,03 : {r['ecart_sup_3pts']}")
    print("nombre d'écarts :", r["ecarts"], "| suivi 15 min :", r.get("suivi_15min"))
    print("Brier tout l'échantillon :", r["brier_tout"], "| log loss :", r["logloss_tout"])
    print("Brier test :", r["brier_test"])
    print("Log loss test :", r["logloss_test"])
    print("| Modèle / seuil / écart | paris | rendement | jours gagnants | ligues gagnantes |")
    for sname, s in r["simulations"].items():
        print(f"| {sname} | {s['paris']} | {s['rendement_pct']} % | {s['jours_gagnants']}/{s['jours']} | "
              f"{s['ligues_gagnantes']}/{s['ligues']} |")
    print("par ligue (a, seuil 0,03, écart 0,01) :")
    for lg, x in r["par_ligue"].items():
        print(f"  {lg:5s} {x}")
    print("Kalshi liquide :", r["kalshi_liquide"])
