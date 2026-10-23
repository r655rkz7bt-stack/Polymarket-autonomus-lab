"""Piste n° 2 (toucher_avant_fin), partie a : « toucher K pendant la période » contre « au-dessus de K à midi le jour J ».

Usage : .venv/bin/python experiments/toucher_avant_fin/coherence.py [dossier_données]
Données : collecte de experiments/crypto_backtest (collect.py + collect_trades.py), copiée dans
donnees/ (ignoré par Git) : marchés réglés du 17/08 au 15/10/2026 (BTC, ETH, SOL, XRP) et échanges réels.

Règles (lues dans Gamma) :
  - échelle « Bitcoin above K on <J> ? » : clôture de la bougie Binance d'une minute de 12 h 00 ET, STRICTEMENT au-dessus de K ;
  - barrière « reach K » (jour, semaine, mois) : un plus haut Binance d'une minute ≥ K pendant la période ;
    « dip to K » : un plus bas ≤ K.
Donc, si midi le jour J tombe dans la période : au-dessus à midi ⇒ touché. Deux paniers qui paient AU MOINS 1 quoi qu'il arrive :
  - « reach K » OUI + « above K on J » NON ;   - « dip to K » OUI + « above K on J » OUI.
Si les deux jambes coûtent moins de 1 (frais compris) : gain sans risque. On le cherche aux prix RÉELLEMENT payés.

Test 1 (arbitrage strict) : toutes les 30 min, prix connus = derniers échanges de preneurs des deux jambes dans les 15 min
AVANT l'instant ; si somme + frais < 1, achat de chaque jambe au PREMIER échange réel de la bonne sorte dans l'heure APRÈS.
Un seul pari par paire (le premier signal) ; paris regroupés par événement barrière (même trajectoire du prix).
Test 2 (règle « environ 2 fois », principe de réflexion) : seulement les paires où la période de la barrière finit au plus 12 h
après midi J. Modèle : P(toucher) = min(1, r × P(au-dessus)) avec le prix payé de l'échelle ; achat du OUI (ou du NON) de la
barrière si l'écart dépasse le seuil après frais. Réglage (r, seuil) sur la première moitié des jours, jugement sur la seconde.
"""
import bisect
import gzip
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
from polymarket_agent.crypto_model import parse_question

WD = Path(sys.argv[1] if len(sys.argv) > 1 else "experiments/toucher_avant_fin/donnees")
H = 3600


def load(name):
    return json.loads(gzip.decompress((WD / name).read_bytes()))


def kind_of(slug):
    if "-above-on-" in slug:
        return "echelle"
    return "jour" if "-hit-on-" in slug else "mois" if "-hit-in-" in slug else "semaine"


def window(r, typ):
    """Période d'une barrière [début, fin] en secondes (fin = 23 h 59 ET = échéance annoncée)."""
    if typ == "jour":
        return r.end - 86400, r.end
    if typ == "semaine":
        return r.end - 7 * 86400, r.end
    end = datetime.fromtimestamp(r.end, tz=timezone.utc)  # 1er du mois suivant, 0 h ET
    month, year = (end.month - 1 or 12), (end.year if end.month > 1 else end.year - 1)
    return int(datetime(year, month, 1, 4, tzinfo=timezone.utc).timestamp()), r.end


rows = [it.Resolved(**r) for r in load("rows.json.gz")]
markets = []
for r in rows:
    q = parse_question(r.question)
    m = re.match(r"^(?:what-price-will-)?(bitcoin|ethereum|solana|xrp)-", r.event_slug)
    if q is None or not m:
        continue
    typ = kind_of(r.event_slug)
    if (typ == "echelle") != (q.kind == "above"):
        continue
    r.q, r.typ, r.asset = q, typ, m.group(1)
    markets.append(r)

# ---------------------------------------------------------------- échanges réels par marché : séries « acheter OUI » et « acheter NON »
by_event = defaultdict(list)
for r in markets:
    by_event[r.event_id].append(r)
buy_yes, buy_no, missing = {}, {}, 0
for ev, group in by_event.items():
    p = WD / "trades" / f"{ev}.json.gz"
    if not p.exists():
        missing += len(group)
        continue
    trades = json.loads(gzip.decompress(p.read_bytes()))  # [heure, marché, issue (0 = Oui), jeton, côté, prix, parts]
    cond_of = {t[3]: t[1] for t in trades if t[2] == 0}
    per = defaultdict(list)
    for t in trades:
        per[t[1]].append(t)
    for r in group:
        y, n = [], []
        for ts_, _, outcome, _, side, price, _ in sorted(per.get(cond_of.get(r.yes_token), []), key=lambda t: t[0]):
            if (outcome == 0) == (side == "BUY"):   # le preneur a acheté le OUI (ou vendu le NON)
                y.append((ts_, price if outcome == 0 else 1 - price))
            else:                                    # le preneur a acheté le NON (ou vendu le OUI)
                n.append((ts_, price if outcome == 1 else 1 - price))
        buy_yes[r.market_id], buy_no[r.market_id] = y, n


def before(series, t, w):
    """Dernier prix payé dans les `w` secondes AVANT t (connu à la décision)."""
    i = bisect.bisect_right(series, (t, 2.0)) - 1
    return series[i][1] if i >= 0 and t - series[i][0] <= w else None


def after(series, t, w):
    """Premier prix payé dans les `w` secondes APRÈS t (ce qu'on aurait payé)."""
    i = bisect.bisect_right(series, (t, 2.0))
    return series[i][1] if i < len(series) and series[i][0] - t <= w else None


# ---------------------------------------------------------------- paires (même actif, même seuil, midi J dans la période)
ladders = defaultdict(list)
for r in markets:
    if r.typ == "echelle":
        ladders[(r.asset, r.q.threshold)].append(r)
pairs = []
for b in markets:
    if b.typ == "echelle":
        continue
    s, e = window(b, b.typ)
    for l in ladders.get((b.asset, b.q.threshold), []):
        if s <= l.end <= e:
            pairs.append((b, l, s, e))
print(f"marchés : {len(markets)} (sans fichier d'échanges : {missing}) ; paires barrière × échelle : {len(pairs)}")
print("   par type :", dict(sorted(defaultdict(int, {k: sum(1 for p in pairs if p[0].typ == k) for k in ('jour', 'semaine', 'mois')}).items())))


def legs(b, l):
    """(série jambe 1, série jambe 2, gain de la jambe 2) : reach → OUI barrière + NON échelle ; dip → OUI + OUI."""
    if b.q.kind == "touch_up":
        return buy_yes[b.market_id], buy_no[l.market_id], 1 - l.won
    return buy_yes[b.market_id], buy_yes[l.market_id], l.won


def month(ts_):
    return datetime.fromtimestamp(ts_, tz=timezone.utc).strftime("%Y-%m")


# ---------------------------------------------------------------- test 1 : arbitrage strict
obs = viol = viol_fees = 0
bets, no_fill = [], 0
for b, l, s, e in pairs:
    if b.market_id not in buy_yes or l.market_id not in buy_yes:
        continue
    y1, y2, pay2 = legs(b, l)
    if not y1 or not y2:
        continue
    t = max(y1[0][0], y2[0][0]) + 900
    t -= t % 1800
    stop = min(l.end, e) - 1800
    taken = False
    while t < stop:
        k1, k2 = before(y1, t, 900), before(y2, t, 900)
        if k1 is not None and k2 is not None:
            obs += 1
            cost = k1 + k2 + it.fee(k1, b.fee_rate) + it.fee(k2, l.fee_rate)
            viol += k1 + k2 < 1
            viol_fees += cost < 1
            if cost < 1 and not taken:
                a1, a2 = after(y1, t, H), after(y2, t, H)
                if a1 is None or a2 is None:
                    no_fill += 1
                else:
                    paid = a1 + a2 + it.fee(a1, b.fee_rate) + it.fee(a2, l.fee_rate)
                    payoff = b.won + pay2
                    bets.append(dict(gain=payoff / paid - 1, evenement=b.event_id, cout=paid / 2, mois=month(t),
                                     paye=paid, connu=cost, payoff=payoff, typ=b.typ, sens=b.q.kind, t=t,
                                     q=f"{b.question} | {l.question}"))
                taken = True  # un seul signal par paire, même sans échange après
        t += 1800
print("\n== Test 1 : arbitrage strict (deux jambes connues à moins de 15 min l'une de l'autre)")
print(f"observations (paire × demi-heure) : {obs} ; somme des prix payés < 1 : {viol} ({100 * viol / max(obs, 1):.2f} %) ;"
      f" < 1 après frais : {viol_fees} ({100 * viol_fees / max(obs, 1):.2f} %)")
print(f"paires avec un signal : {len(bets) + no_fill} ; exécutées aux prix d'après : {len(bets)} ; sans échange dans l'heure : {no_fill}")
if bets:
    sure = sum(1 for x in bets if x["paye"] < 1)
    print(f"   coût payé moyen {sum(x['paye'] for x in bets) / len(bets):.3f} (connu {sum(x['connu'] for x in bets) / len(bets):.3f}) ;"
          f" exécutions encore sous 1 : {sure} ; gain total {sum(x['payoff'] - x['paye'] for x in bets):+.2f} $ pour {len(bets)} paniers")
    for x in sorted(bets, key=lambda x: x["paye"])[:8]:
        print(f"   {datetime.fromtimestamp(x['t'], tz=timezone.utc):%m-%d %H:%M} connu {x['connu']:.3f} payé {x['paye']:.3f} reçu {x['payoff']} | {x['q'][:110]}")
    print(json.dumps(it.verdict(bets, min_bets=10), ensure_ascii=False))

# ---------------------------------------------------------------- test 2 : règle « environ 2 fois »
cases = []
for b, l, s, e in pairs:
    if e - l.end > 12 * H or b.q.kind != "touch_up" or b.market_id not in buy_yes or l.market_id not in buy_yes:
        continue
    yb, nb, yl, nl = buy_yes[b.market_id], buy_no[b.market_id], buy_yes[l.market_id], buy_no[l.market_id]
    for hours in (48, 24, 12, 6, 3):
        t = l.end - hours * H
        if t < s - 7 * 86400:
            continue
        pl_a, pl_b = before(yl, t, H), before(nl, t, H)   # échelle : prix connus (achat OUI, achat NON)
        kb_y, kb_n = before(yb, t, H), before(nb, t, H)   # barrière : prix connus
        if pl_a is None or pl_b is None or (kb_y is None and kb_n is None):
            continue
        p_above = (pl_a + 1 - pl_b) / 2                   # milieu des deux derniers prix payés de l'échelle
        if not 0.02 <= p_above <= 0.6:
            continue
        cases.append(dict(b=b, l=l, t=t, h=hours, p_above=p_above, ky=kb_y, kn=kb_n, day=it.day_of(l.end),
                          ay=after(yb, t, H), an=after(nb, t, H)))
days = sorted({c["day"] for c in cases})
cut = days[len(days) // 2] if days else ""


def run(sub, r, edge):
    out = []
    for c in sub:
        b = c["b"]
        model = min(1.0, r * c["p_above"])
        if c["ky"] is not None and model - c["ky"] - it.fee(c["ky"], b.fee_rate) > edge and c["ay"] is not None:
            paid = c["ay"] + it.fee(c["ay"], b.fee_rate)
            out.append(dict(gain=b.won / paid - 1, evenement=b.event_id, cout=paid, mois=month(c["t"]), sens="OUI"))
        elif c["kn"] is not None and (1 - model) - c["kn"] - it.fee(c["kn"], b.fee_rate) > edge and c["an"] is not None:
            paid = c["an"] + it.fee(c["an"], b.fee_rate)
            out.append(dict(gain=(1 - b.won) / paid - 1, evenement=b.event_id, cout=paid, mois=month(c["t"]), sens="NON"))
    return out


print(f"\n== Test 2 : règle « toucher ≈ r × au-dessus » ({len(cases)} cas, {len({c['b'].market_id for c in cases})} barrières ; coupure {cut})")
# Étalonnage descriptif : ce que paie le marché, ce que dit la réflexion, ce qui est arrivé
bins = defaultdict(list)
for c in cases:
    if c["ky"] is None:
        continue
    k = "0,02-0,10" if c["p_above"] < 0.10 else "0,10-0,25" if c["p_above"] < 0.25 else "0,25-0,60"
    bins[k].append(c)
print("   au-dessus (prix payé) | cas | prix du toucher | 2 × au-dessus | toucher réel | au-dessus réel | rapport marché | rapport réel")
for k in sorted(bins):
    v = bins[k]
    n = len(v)
    pt, pa = sum(c["ky"] for c in v) / n, sum(c["p_above"] for c in v) / n
    ft, fa = sum(c["b"].won for c in v) / n, sum(c["l"].won for c in v) / n
    print(f"   {k} | {n} | {pt:.3f} | {2 * pa:.3f} | {ft:.3f} | {fa:.3f} | {pt / pa:.2f} | {ft / fa if fa else float('nan'):.2f}")
train = [c for c in cases if c["day"] < cut]
test = [c for c in cases if c["day"] >= cut]
grid = [(r, e) for r in (1.5, 1.75, 2.0, 2.25) for e in (0.03, 0.05, 0.08)]
print(f"   réglages essayés : {len(grid)} (r × seuil)")
best = None
for r, e in grid:
    tr, te = run(train, r, e), run(test, r, e)
    mt = sum(x["gain"] for x in tr) / len(tr) if tr else float("nan")
    ms = sum(x["gain"] for x in te) / len(te) if te else float("nan")
    print(f"   r {r} seuil {e} : apprentissage {len(tr)} paris {100 * mt:+.1f} % | jugement {len(te)} paris {100 * ms:+.1f} %")
    if tr and len(tr) >= 20 and (best is None or mt > best[0]):
        best = (mt, r, e)
if best:
    _, r, e = best
    te = run(test, r, e)
    print(f"   meilleur réglage sur l'apprentissage : r {r}, seuil {e} → jugement :")
    print("  ", json.dumps(it.verdict(te), ensure_ascii=False))
    for sens in ("OUI", "NON"):
        sub = [x for x in te if x["sens"] == sens]
        if sub:
            print(f"   jugement, achat du {sens} : {len(sub)} paris, {100 * sum(x['gain'] for x in sub) / len(sub):+.1f} %")
