"""« What will <matière> hit Week of … » (24/10/2026) : touche-t-on une barre (HIGH ou LOW) avant la fin de la semaine ? Réglé sur les bougies d'1 minute
de Pyth (règle lue : tout « High » ou « Low » de bougie égal ou au-delà de la barre pendant la séance, après la création du marché).
Modèle : barrière d'un mouvement brownien sans dérive, volatilité horaire des 10 derniers jours (prix horaires Yahoo, contrats à terme), maximum / minimum
déjà atteints depuis la création du marché (rien du futur). Décisions à 14 h UTC chaque jour de la création au jeudi ; achat au premier échange réel dans les
2 h qui suivent. Usage : PYTHONPATH=src python backtest.py [WTI,NG,XAUUSD,XAGUSD]"""
import collections, concurrent.futures as cf, datetime as dt, json, math, re, sys
from pathlib import Path
from polymarket_agent import idea_test as it
from polymarket_agent.http_client import HttpClient
ROOT = Path(__file__).resolve().parents[1]
UTC = dt.timezone.utc
SYM = {"WTI": "CL_F", "NG": "NG_F", "XAUUSD": "GC_F", "XAGUSD": "SI_F"}
NORM = lambda x: 0.5 * math.erfc(-x / math.sqrt(2))
EV = json.load(open(ROOT / "donnees/evenements.json"))
tickers = sys.argv[1].split(",") if len(sys.argv) > 1 else ["WTI", "NG"]
import os
MOIS = os.environ.get("MOIS") == "1"        # échelles mensuelles « hit in <mois> » au lieu des hebdomadaires
PREMIER = os.environ.get("PREMIER") == "1"      # seulement la première décision de chaque marché (rien à savoir du passé de la semaine)
SIGMA_FIXE = os.environ.get("SIGMA_FIXE") == "1"    # volatilité horaire = médiane de la période, pas celle des 10 derniers jours

def load(sym):
    rows = json.load(open(ROOT / f"donnees/{SYM[sym]}.json"))
    return rows

def parse_q(q):
    m = re.search(r"hit \((HIGH|LOW)\) \$([\d,]+(?:\.\d+)?)", q)
    return (m.group(1), float(m.group(2).replace(",", ""))) if m else None

def ts(x):
    return dt.datetime.fromisoformat(str(x).replace("Z", "+00:00").replace(" ", "T")) if x else None

SIG_MED = {}

def main():
    http = HttpClient(timeout=40, min_interval=0.2)
    bets, pairs, control = {}, [], collections.Counter()
    for tk in tickers:
        bars = load(tk); times = [b[0] for b in bars]
        _r = sorted(abs(math.log(bars[k][4] / bars[k - 1][4])) for k in range(1, len(bars)) if bars[k][4] and bars[k - 1][4] and bars[k][0] - bars[k - 1][0] <= 7200)
        SIG_MED.setdefault(tk, (sum(x * x for x in _r) / len(_r)) ** 0.5)
        import bisect
        evs = [e for e in EV if e["closed"] and f"({tk})" in e["title"] and (("hit in " in e["title"] and "Week of" not in e["title"]) if MOIS else "Week of" in e["title"])]
        with cf.ThreadPoolExecutor(4) as ex:
            trades = dict(ex.map(lambda e: (e["id"], it.fetch_event_trades(http, ROOT / "donnees/echanges", e["id"])), evs))
        for e in sorted(evs, key=lambda e: e["endDate"]):
            end = ts(e["endDate"]).replace(hour=21, minute=0)          # vendredi, clôture ≈ 17 h ET
            create = min(ts(m.get("startDate") or m.get("createdAt") or e.get("startDate")) for m in e["markets"])
            tr = trades[e["id"]]
            for m in e["markets"]:
                if not m.get("outcomePrices") or not m.get("clobTokenIds") or m.get("closed") is False: continue
                pq = parse_q(m["question"]); 
                if not pq: continue
                side, K = pq
                yes, no = json.loads(m["clobTokenIds"]); won = json.loads(m["outcomePrices"])[0] == "1"
                # contrôle du règlement : les barres horaires redonnent-elles l'issue officielle ?
                lo = bisect.bisect_left(times, int(create.timestamp())); hi = bisect.bisect_right(times, int(end.timestamp()))
                seg = bars[lo:hi]
                if not seg: continue
                touched = (max(b[2] for b in seg) >= K) if side == "HIGH" else (min(b[3] for b in seg) <= K)
                control[(tk, touched == won)] += 1
                T = dt.datetime.combine(create.date(), dt.time(14), tzinfo=UTC)
                if T < create: T += dt.timedelta(days=1)
                while T < end - dt.timedelta(hours=18):
                    if MOIS and (T - create) > dt.timedelta(days=60): break
                    i = bisect.bisect_right(times, int(T.timestamp()) - 3600) - 1        # seulement les barres horaires FINIES avant T
                    if i < 240: break
                    S = bars[i][4]
                    j0 = bisect.bisect_left(times, int(create.timestamp()))
                    run = bars[j0:i + 1]
                    if run:
                        hit_already = (max(b[2] for b in run) >= K) if side == "HIGH" else (min(b[3] for b in run) <= K)
                    else: hit_already = False
                    if hit_already: T += dt.timedelta(days=1); continue
                    rets = [math.log(bars[k][4] / bars[k - 1][4]) for k in range(i - 239, i + 1) if bars[k][4] and bars[k - 1][4] and times[k] - times[k - 1] <= 3600 * 2]
                    sig = (sum(r * r for r in rets) / len(rets)) ** 0.5     # écart-type par barre horaire
                    if SIGMA_FIXE: sig = SIG_MED[tk]
                    tau = max(((end - T).total_seconds() / 3600) * 23 / 24, 0.5)
                    d = abs(math.log(K / S)) / (sig * math.sqrt(tau))
                    p = min(1.0, 2 * (1 - NORM(d)))
                    for cote, tok, oth, pc in (("OUI", yes, no, p), ("NON", no, yes, 1 - p)):
                        c = it.taker_cost(tr, tok, oth, int(T.timestamp()), window=2 * 3600, after=True)
                        cprev = it.taker_cost(tr, tok, oth, int(T.timestamp()), window=3 * 3600)
                        if c is None: continue
                        pairs.append((tk, e["id"], m["id"], cote, pc, c, cprev, (won if cote == "OUI" else not won)))
                        for seuil in (0.05, 0.10, 0.20):
                            key = (tk, seuil, e["id"], m["id"])
                            if key in bets or pc - c <= seuil or c < 0.03 or c > 0.97: continue
                            g = ((1.0 if (won if cote == "OUI" else not won) else 0.0) - c) / c
                            bets[key] = dict(gain=g, evenement=e["id"], mois=e["endDate"][:7], cout=c, cote=cote, proba=pc, tk=tk, seuil=seuil)
                    if PREMIER: break
                    T += dt.timedelta(days=1)
    print("contrôle du règlement (touche d'après les barres horaires = issue officielle) :", dict(control))
    for tk in tickers:
        for seuil in (0.05, 0.10, 0.20):
            bs = [v for k, v in bets.items() if k[0] == tk and k[1] == seuil]
            v = it.verdict(bs, min_bets=20)
            print(f"{tk:7s} seuil {seuil:.2f} : {len(bs):3d} paris, rendement {sum(b['gain'] for b in bs)/max(1,len(bs)):+.3f}, {v.get('verdict')} | {str(v.get('raison',''))[:100]}")
    # calibration modèle contre marché (log-score) et par tranche
    ll_m = ll_c = 0.0; n = 0
    for tk, ev, mk, cote, pc, c, cprev, res in pairs:
        if cote != "OUI" or cprev is None: continue
        o = 1.0 if res else 0.0; pm = min(max(cprev, 0.01), 0.99); pp = min(max(pc, 0.01), 0.99)
        ll_m += -(o * math.log(pm) + (1 - o) * math.log(1 - pm)); ll_c += -(o * math.log(pp) + (1 - o) * math.log(1 - pp)); n += 1
    print(f"log-score sur {n} couples (marché, instant) : marché {ll_m/n:.4f} contre modèle {ll_c/n:.4f}")
    json.dump(pairs, open(ROOT / "donnees/pairs.json", "w")); json.dump([dict(v, key=list(k)) for k, v in bets.items()], open(ROOT / "donnees/paris.json", "w"))
main()
