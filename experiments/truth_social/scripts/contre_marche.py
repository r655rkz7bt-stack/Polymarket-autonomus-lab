"""Posts Truth Social de Trump : modèle de comptage contre le marché, puis achats simulés aux vrais prix payés.

Décision à T (de S-2 j à S+5 j, S = début de la fenêtre de 7 jours) : posts déjà comptés dans la fenêtre (archive) + posts restants
attendus = somme, sur les heures restantes, de la moyenne de la même heure de la semaine sur les `HIST` jours AVANT T (aucun regard vers l'avenir).
Loi du total : c + binomiale négative(moyenne restante, dispersion R). Prix : premier échange dans les 2 h après T (idea_test.taker_cost).
"""
import bisect, gzip, json, math, sys, collections, statistics as st
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, "experiments/truth_social/scripts")
from polymarket_agent import idea_test as it
from polymarket_agent.references import negbin_interval
import reglement as rg

posts = rg.lire_posts()
ts_post = [p.timestamp() for p in posts]
ev = json.load(open("experiments/truth_social/donnees/evenements.json"))
cache = Path("experiments/truth_social/donnees/cache")
HIST = int(sys.argv[1]) if len(sys.argv) > 1 else 28
R = float(sys.argv[2]) if len(sys.argv) > 2 else 20
MARGE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
SCALE = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0   # le décompte du tracker dépasse l'archive de quelques %
OFFS = [-2, 0, 1, 2, 3, 4, 5]
FEE = 0.05

def compte(a, b):
    return bisect.bisect_left(ts_post, b) - bisect.bisect_left(ts_post, a)

def restant(T, E):
    """Posts attendus entre T et E d'après la même heure de la semaine sur HIST jours avant T."""
    prof = collections.defaultdict(float)
    n_sem = HIST / 7
    for k in range(HIST * 24):
        h0 = T.replace(minute=0, second=0, microsecond=0) - timedelta(hours=k + 1)
        prof[(h0.weekday(), h0.hour)] += compte(h0.timestamp(), h0.timestamp() + 3600) / n_sem
    tot = 0.0; t = T
    while t < E:
        h0 = t.replace(minute=0, second=0, microsecond=0)
        frac = (min(E, h0 + timedelta(hours=1)) - t).total_seconds() / 3600
        tot += prof[(h0.weekday(), h0.hour)] * frac
        t = h0 + timedelta(hours=1)
    return tot

import os
from polymarket_agent.references import tweet_bucket_probability
PROD = os.environ.get("PROD") == "1"   # formule de production (compteur_tweets : 168 h / 336 h, dispersion R) au lieu du profil par heure de la semaine

def proba_prod(lo, hi, c, T, S0, E):
    h = T.replace(minute=0, second=0, microsecond=0)
    hourly = [compte((h - timedelta(hours=k + 1)).timestamp(), (h - timedelta(hours=k)).timestamp()) for k in range(335, -1, -1)]
    tr = {"debut": S0.isoformat(), "fin": E.isoformat(), "vu_le": T.isoformat(), "total": c, "heures": hourly}
    return tweet_bucket_probability(tr, (lo, hi), T, R, 168, 336, 0.5) or 0.0

def proba(lo, hi, c, rest):
    """P(c + X dans [lo, hi]) avec X ~ NB(rest, R)."""
    if hi < c: return 0.0
    a = max(lo - c, 0); b = hi - c if hi < 10**8 else 10**9
    if rest <= 0.01: return 1.0 if a <= 0 <= b else 0.0
    return negbin_interval(a, b, rest, R)

mk_ls, mo_ls, n_ls = collections.defaultdict(float), collections.defaultdict(float), collections.Counter()
bets = []
for e in ev:
    S0, E = rg.fenetre(e)
    now = datetime.now(timezone.utc)
    if not e.get("closed") or E > now or S0 - timedelta(days=HIST) < posts[0]: continue
    win = rg.gagnante(e)
    if win is None or rg.bornes(win) is None: continue
    path = cache / f"echanges_{e['id']}.json.gz"
    if not path.exists(): continue
    trades = json.loads(gzip.decompress(path.read_bytes()))
    buckets = []
    for m in e["markets"]:
        b = rg.bornes(m["groupItemTitle"] or "")
        if b is None: continue
        yes, no = json.loads(m["clobTokenIds"])
        buckets.append((m["groupItemTitle"], b, yes, no, m["groupItemTitle"] == win))
    if len(buckets) < 6: continue
    for off in OFFS:
        T = S0 + timedelta(days=off)
        if T >= E - timedelta(hours=6): continue
        c = int(round(compte(S0.timestamp(), T.timestamp()) * SCALE)) if off > 0 else 0
        rest = restant(max(T, S0), E) * SCALE
        ts = int(T.timestamp())
        row = []
        for title, (lo, hi), yes, no, won in buckets:
            q = proba_prod(lo, hi, c, T, S0, E) if PROD else proba(lo, hi, c, rest)
            py = it.taker_cost(trades, yes, no, ts, window=2 * 3600, after=True)
            pn = it.taker_cost(trades, no, yes, ts, window=2 * 3600, after=True)
            lastp = [t[3] if t[1] == yes else 1 - t[3] for t in trades if t[0] <= ts and t[0] >= ts - 6 * 3600 and t[1] in (yes, no)]
            mid = lastp[-1] if lastp else None
            row.append((title, q, py, pn, won, mid))
        mids = [r[5] for r in row]
        if all(m is not None for m in mids) and sum(mids) > 0.5:
            tot = sum(mids)
            for r in row:
                if r[4]:
                    mk_ls[off] += math.log(max(r[5] / tot, 1e-3)); mo_ls[off] += math.log(max(r[1], 1e-3)); n_ls[off] += 1
        tok = {b[0]: (b[2], b[3]) for b in buckets}
        for title, q, py, pn, won, _ in row:
            for side, qq, cost in ((0, q, py), (1, 1 - q, pn)):
                if cost is None or not (0.03 <= cost < 0.97): continue
                fee = FEE * cost * (1 - cost)
                if qq - cost - fee > MARGE:
                    mine, autre = tok[title][side], tok[title][1 - side]
                    prof = sum(t[4] for t in trades if ts <= t[0] <= ts + 2 * 3600 and ((t[1] == mine and t[2] == "BUY") or (t[1] == autre and t[2] == "SELL"))
                               and (t[3] if t[1] == mine else 1 - t[3]) <= cost + 0.01)
                    gain = ((1.0 if (won if side == 0 else not won) else 0.0) - cost - fee) / cost
                    bets.append({"gain": gain, "evenement": e["slug"], "mois": E.strftime("%Y-%m"), "cout": cost, "cote": side, "off": off, "tr": title, "q": qq, "parts": prof})
print(f"HIST {HIST} R {R} marge {MARGE} échelle {SCALE}")
for off in OFFS:
    if n_ls[off]: print(f"  T=S{off:+d} j : log-score tranche gagnante, marché {mk_ls[off]/n_ls[off]:.3f} modèle {mo_ls[off]/n_ls[off]:.3f} (n {n_ls[off]})")
print(json.dumps(it.verdict(bets), ensure_ascii=False)[:1400])
for side in (0, 1):
    g = [b["gain"] for b in bets if b["cote"] == side]
    if g: print("  côté", "OUI" if side == 0 else "NON", len(g), f"{st.mean(g):+.3f}")
for off in OFFS:
    g = [b["gain"] for b in bets if b["off"] == off]
    if g: print(f"  T=S{off:+d}: {len(g)} paris {st.mean(g):+.3f}")
json.dump(bets, open("/tmp/claude-0/s/bets_ts.json", "w"))
sans = [b for b in bets if b["cout"] >= 0.10]
v2 = it.verdict(sans)
print(f"RÉSUMÉ HIST {HIST} R {R} marge {MARGE} échelle {SCALE} : tout {len(bets)} paris {st.mean([b['gain'] for b in bets]) if bets else 0:+.3f} | sans billets < 0,10 : {v2['paris']} paris {v2.get('rendement_moyen')} t_évén {v2.get('confiance_evenements')} z_prix {v2.get('z_prix')} mois+ {v2.get('mois_gagnants')} -> {v2['verdict']}")
