"""Vague de volume, étape 3 : la règle en direct rejouée sur le passé, aux prix RÉELLEMENT payés.

Usage : PYTHONPATH=src python experiments/vague_volume_backtest/analyse.py [heures]   (heures : "0" ou "0,12")
À chaque instant T (chaque jour à 00:00 UTC, ou aussi 12:00), pour chaque marché, seulement avec les
échanges d'horodatage < T (jamais de regard vers le futur) :
- âge = T − création ≥ 3 jours ; échéance réelle − T ≥ 48 h ; marché pas encore clos ; jours couverts ;
- référence = (volume de la fenêtre min(7, âge) jours − volume des 24 h) / max(jours − 1, 1)  (comme
  VagueVolume._surge avec Gamma volume1wk / volume24hr), ≥ 500 $ ; rapport = volume 24 h / référence ;
- mouvement = prix du OUI au dernier échange avant T − prix au dernier échange avant T − 24 h ;
- suivre : achète le côté qui a monté si son prix (dernier échange avant T) est dans [0,55 ; 0,90] ;
  contrer : l'autre côté si son prix est dans [0,10 ; 0,45] ;
- prix payé = premier échange réel APRÈS T qui achète ce côté (taker_cost(after=True), 2 h) + frais du
  marché (idea_test.fee) ; gain par euro = (gagné − coût − frais) / coût ; au plus un pari par marché et
  par jour (variante « comme en direct » : un seul pari par marché, la position étant gardée).
Jugement : idea_test.verdict (paris liés par événement). -> donnees/resultats.json + affichage."""
import bisect
import datetime as dt
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

from polymarket_agent import idea_test as it

HOURS = [int(h) for h in (sys.argv[1] if len(sys.argv) > 1 else "0").split(",")]
D = Path("experiments/vague_volume_backtest/donnees")
markets = json.load(open(D / "marches.json"))
DAY = 86400

# ---------------------------------------------------------------- 1. observations à chaque instant T
obs = []  # une ligne par (marché, T) admissible
stats = defaultdict(int)
for m in markets:
    x = m["extra"]
    p = D / "echanges" / f"{m['market_id']}.json.gz"
    if not p.exists():
        stats["sans_fichier"] += 1
        continue
    data = json.loads(gzip.decompress(p.read_bytes()))
    stats["marches_lus"] += 1
    stats["tronques"] += not data["complet"]
    tr = sorted(data["echanges"])
    if not tr:
        stats["sans_echange"] += 1
        continue
    yes, no = m["yes_token"], x["no_token"]
    ts = [t[0] for t in tr]
    cum = [0.0]
    for t in tr:
        cum.append(cum[-1] + t[3] * t[4])
    pyes = [t[3] if t[1] == yes else 1 - t[3] for t in tr]

    def vol(a, b):  # volume des échanges a <= heure < b
        return cum[bisect.bisect_left(ts, b)] - cum[bisect.bisect_left(ts, a)]

    def last_yes(before):
        i = bisect.bisect_left(ts, before)
        return pyes[i - 1] if i else None

    # Achats de chaque côté, même définition que it.taker_cost (achat du jeton à p ou vente de l'autre à 1 − p)
    buys = {}
    for side, (tok, other) in enumerate(((yes, no), (no, yes))):
        pts = sorted((t[0], t[3] if t[1] == tok else 1 - t[3]) for t in tr
                     if (t[1] == tok and t[2] == "BUY") or (t[1] == other and t[2] == "SELL"))
        buys[side] = ([a for a, _ in pts], [b for _, b in pts])

    def paid(side, T):
        when, price = buys[side]
        i = bisect.bisect_left(when, T)
        return price[i] if i < len(when) and when[i] <= T + 2 * 3600 else None

    first = (x["created"] // DAY + 1) * DAY
    for day0 in range(first, x["deadline"], DAY):
        for h in HOURS:
            T = day0 + h * 3600
            age = (T - x["created"]) / DAY
            if age < 3 or x["deadline"] - T < 48 * 3600 or T >= x["closed"]:
                continue
            days = min(7.0, age)
            if data["couvert_depuis"] > T - days * DAY:
                stats["instants_non_couverts"] += 1
                continue
            v24 = vol(T - DAY, T)
            ref = (vol(T - days * DAY, T) - v24) / max(days - 1, 1)
            if ref < 500:
                continue
            p_now, p_before = last_yes(T), last_yes(T - DAY)
            if p_now is None or p_before is None:
                continue
            move = p_now - p_before
            if move == 0:
                continue
            rose = 0 if move > 0 else 1
            row = dict(m=m["market_id"], ev=m["event_id"], fam=x["famille"], T=T, ratio=v24 / ref, move=move,
                       p_yes=p_now, won=m["won"], rate=m["fee_rate"], buy={})
            for side in (0, 1):
                row["buy"][side] = paid(side, T)
                if len(obs) % 500 == 0:  # contrôle : même prix que idea_test.taker_cost
                    tok, other = (yes, no) if side == 0 else (no, yes)
                    assert row["buy"][side] == it.taker_cost(tr, tok, other, T, window=2 * 3600, after=True)
                    stats["controles_taker_cost"] += 1
            row["rose"] = rose
            obs.append(row)
stats["observations"] = len(obs)
print(dict(stats))


# ---------------------------------------------------------------- 2. paris d'un réglage
def bets_for(direction, surge_min, surge_max, min_move, lo, hi, live_like=False, fam=None):
    out, used_day, used_mk, nofill = [], set(), set(), 0
    for r in sorted(obs, key=lambda r: r["T"]):
        if fam and r["fam"] != fam:
            continue
        if not (surge_min <= r["ratio"] < surge_max) or abs(r["move"]) < min_move:
            continue
        side = r["rose"] if direction > 0 else 1 - r["rose"]
        price_known = r["p_yes"] if side == 0 else 1 - r["p_yes"]
        if not lo <= price_known <= hi:
            continue
        key = (r["m"], it.day_of(r["T"]))
        if key in used_day or (live_like and r["m"] in used_mk):
            continue
        cost = r["buy"][side]
        if cost is None:
            nofill += 1
            continue
        if not 0 < cost < 1:
            continue
        used_day.add(key); used_mk.add(r["m"])
        won = r["won"] if side == 0 else 1 - r["won"]
        f = it.fee(cost, r["rate"])
        out.append(dict(gain=(won - cost - f) / cost, evenement=r["ev"], cout=cost, fam=r["fam"],
                        mois=dt.datetime.fromtimestamp(r["T"], dt.timezone.utc).strftime("%Y-%m")))
    return out, nofill


def brief(v):
    return {k: v.get(k) for k in ("paris", "evenements", "rendement_moyen", "confiance_evenements", "z_prix",
                                  "mois_gagnants", "verdict")}


RANGES = {1: (0.55, 0.90), -1: (0.10, 0.45)}
results = {"heures": HOURS, "stats": dict(stats), "reglages": {}}
n = 0
print("\n| sens | vague ≥ | mouvement ≥ | plages | paris | évén. | sans échange | rendement | conf. évén. | z_prix | mois + | verdict |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for direction, name in ((1, "suivre"), (-1, "contrer")):
    for surge in (2.0, 3.0, 5.0):
        for mv in (0.03, 0.05, 0.10):
            for ranged in (True, False):
                lo, hi = RANGES[direction] if ranged else (0.02, 0.98)
                b, nf = bets_for(direction, surge, 1e18, mv, lo, hi)
                v = it.verdict(b); n += 1
                key = f"{name} x{surge:g} mv{mv:g} {'plages' if ranged else 'sans plages'}"
                results["reglages"][key] = dict(v, sans_echange=nf)
                print(f"| {name} | {surge:g} | {mv:g} | {'oui' if ranged else 'non'} | {v['paris']} | {v.get('evenements')} | {nf} | "
                      f"{v.get('rendement_moyen')} | {v.get('confiance_evenements')} | {v.get('z_prix')} | {v.get('mois_gagnants')} | {v['verdict']} |")
results["nombre_reglages"] = n
print("réglages essayés :", n)

print("\n## Réglage en direct (vague ×3, mouvement 0,03, plages) : détail")
for direction, name in ((1, "suivre"), (-1, "contrer")):
    lo, hi = RANGES[direction]
    b, nf = bets_for(direction, 3.0, 1e18, 0.03, lo, hi)
    v = it.verdict(b)
    print(name, json.dumps(v, ensure_ascii=False))
    results[f"{name}_direct"] = v
    bl, _ = bets_for(direction, 3.0, 1e18, 0.03, lo, hi, live_like=True)
    results[f"{name}_un_pari_par_marche"] = brief(it.verdict(bl))
    print("  un seul pari par marché :", brief(it.verdict(bl)))
    for fam in ("sport", "crypto", "politique", "autres"):
        bf, _ = bets_for(direction, 3.0, 1e18, 0.03, lo, hi, fam=fam)
        results[f"{name}_{fam}"] = brief(it.verdict(bf))
        print(f"  {fam} :", brief(it.verdict(bf)))
    # références sans vague : même mouvement, mêmes plages, au même instant
    for lab, a, z in (("sans vague (rapport < 1,5)", 0, 1.5), ("rapport 1,5-3", 1.5, 3.0), ("tous rapports", 0, 1e18)):
        br, _ = bets_for(direction, a, z, 0.03, lo, hi)
        results[f"{name}_reference_{lab}"] = brief(it.verdict(br))
        print(f"  référence {lab} :", brief(it.verdict(br)))
json.dump(results, open(D / f"resultats_{'_'.join(map(str, HOURS))}.json", "w"), ensure_ascii=False, indent=1)
