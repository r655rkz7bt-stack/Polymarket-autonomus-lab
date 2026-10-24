"""« What price will Bitcoin / Ethereum / Solana hit <semaine> ? » (24/10/2026) : même test que backtest.py pour les échelles hebdomadaires de crypto
(« Will Bitcoin reach $80,000 February 23-March 1 ? », « dip to $60,000 »), réglées sur les bougies d'1 minute de Binance (BTC/USDT…), du lundi 0 h ET au
dimanche 23 h 59 ET. Prix horaires Yahoo (BTC-USD, ETH-USD, SOL-USD) pour la recherche. Mêmes règles : barres horaires FINIES, rien du futur, volatilité des
10 derniers jours (ou fixe avec SIGMA_FIXE=1), achat au premier échange réel dans les 2 h. Usage : PYTHONPATH=src python backtest_crypto.py [BTC,ETH,SOL]"""
import bisect, collections, concurrent.futures as cf, datetime as dt, json, math, os, re, sys
from pathlib import Path
from polymarket_agent import idea_test as it
from polymarket_agent.http_client import HttpClient
ROOT = Path(__file__).resolve().parents[1]
UTC = dt.timezone.utc
NAMES = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana"}
NORM = lambda x: 0.5 * math.erfc(-x / math.sqrt(2))
SIGMA_FIXE = os.environ.get("SIGMA_FIXE") == "1"
EV = json.load(open(ROOT / "donnees/evenements_crypto.json"))
tickers = sys.argv[1].split(",") if len(sys.argv) > 1 else ["BTC", "ETH", "SOL"]
ts = lambda x: dt.datetime.fromisoformat(str(x).replace("Z", "+00:00").replace(" ", "T")) if x else None

def parse_q(q):
    m = re.search(r"(reach|dip to) \$([\d,]+(?:\.\d+)?)", q)
    return ("HIGH" if m.group(1) == "reach" else "LOW", float(m.group(2).replace(",", ""))) if m else None

def main():
    http = HttpClient(timeout=40, min_interval=0.15)
    bets, pairs, control = {}, [], collections.Counter()
    for tk in tickers:
        bars = json.load(open(ROOT / f"donnees/{tk}_USD.json")); times = [b[0] for b in bars]
        rr = [abs(math.log(bars[k][4] / bars[k - 1][4])) for k in range(1, len(bars)) if bars[k][4] and bars[k - 1][4] and bars[k][0] - bars[k - 1][0] <= 7200]
        sig_fixe = (sum(x * x for x in rr) / len(rr)) ** 0.5
        evs = [e for e in EV if e["closed"] and e["title"].startswith(f"What price will {NAMES[tk]} hit") and " on " not in e["title"] and "-" in e["title"].split("hit")[-1]]
        with cf.ThreadPoolExecutor(4) as ex:
            trades = dict(ex.map(lambda e: (e["id"], it.fetch_event_trades(http, ROOT / "donnees/echanges", e["id"])), evs))
        print(tk, len(evs), "événements, échanges", sum(len(v) for v in trades.values()), flush=True)
        for e in sorted(evs, key=lambda e: e["endDate"]):
            end = ts(e["endDate"]); wstart = end - dt.timedelta(days=7)
            if wstart.timestamp() < times[0] + 86400 * 12: continue
            create = min(ts(m.get("startDate") or m.get("createdAt") or e.get("startDate")) for m in e["markets"])
            tr = trades[e["id"]]
            for m in e["markets"]:
                if not m.get("outcomePrices") or not m.get("clobTokenIds"): continue
                pq = parse_q(m["question"])
                if not pq: continue
                side, K = pq
                yes, no = json.loads(m["clobTokenIds"]); won = json.loads(m["outcomePrices"])[0] == "1"
                lo = bisect.bisect_left(times, int(wstart.timestamp())); hi = bisect.bisect_right(times, int(end.timestamp()))
                seg = bars[lo:hi]
                if not seg: continue
                touched = (max(b[2] for b in seg) >= K) if side == "HIGH" else (min(b[3] for b in seg) <= K)
                control[(tk, touched == won)] += 1
                T = dt.datetime.combine(max(create, wstart - dt.timedelta(days=1)).date(), dt.time(14), tzinfo=UTC)
                while T < end - dt.timedelta(hours=18):
                    i = bisect.bisect_right(times, int(T.timestamp()) - 3600) - 1
                    if i < 240: break
                    S = bars[i][4]
                    j0 = bisect.bisect_left(times, int(wstart.timestamp()))
                    run = bars[j0:i + 1] if i >= j0 else []
                    if run and ((max(b[2] for b in run) >= K) if side == "HIGH" else (min(b[3] for b in run) <= K)):
                        T += dt.timedelta(days=1); continue
                    rets = [math.log(bars[k][4] / bars[k - 1][4]) for k in range(i - 239, i + 1) if bars[k][4] and bars[k - 1][4] and times[k] - times[k - 1] <= 7200]
                    sig = sig_fixe if SIGMA_FIXE else (sum(r * r for r in rets) / len(rets)) ** 0.5
                    tau = max((end - max(T, wstart)).total_seconds() / 3600, 0.5)
                    p = min(1.0, 2 * (1 - NORM(abs(math.log(K / S)) / (sig * math.sqrt(tau)))))
                    for cote, tok, oth, pc in (("OUI", yes, no, p), ("NON", no, yes, 1 - p)):
                        c = it.taker_cost(tr, tok, oth, int(T.timestamp()), window=2 * 3600, after=True)
                        cprev = it.taker_cost(tr, tok, oth, int(T.timestamp()), window=3 * 3600)
                        if c is None: continue
                        res = won if cote == "OUI" else not won
                        pairs.append((tk, e["id"], m["id"], cote, pc, c, cprev, res))
                        for seuil in (0.05, 0.10, 0.20):
                            key = (tk, seuil, e["id"], m["id"])
                            if key in bets or pc - c <= seuil or c < 0.03 or c > 0.97: continue
                            bets[key] = dict(gain=((1.0 if res else 0.0) - c) / c, evenement=e["id"], mois=e["endDate"][:7], cout=c, cote=cote, proba=pc, tk=tk, seuil=seuil)
                    T += dt.timedelta(days=1)
    print("contrôle du règlement :", dict(control))
    for tk in tickers:
        for seuil in (0.05, 0.10, 0.20):
            bs = [v for k, v in bets.items() if k[0] == tk and k[1] == seuil]
            v = it.verdict(bs, min_bets=20)
            print(f"{tk:4s} seuil {seuil:.2f} : {len(bs):4d} paris, rendement {sum(b['gain'] for b in bs)/max(1,len(bs)):+.3f}, {v.get('verdict')} | {str(v.get('raison',''))[:90]}")
    ll_m = ll_c = 0.0; n = 0
    for tk, ev, mk, cote, pc, c, cprev, res in pairs:
        if cote != "OUI" or cprev is None: continue
        o = 1.0 if res else 0.0; pm = min(max(cprev, 0.01), 0.99); pp = min(max(pc, 0.01), 0.99)
        ll_m += -(o * math.log(pm) + (1 - o) * math.log(1 - pm)); ll_c += -(o * math.log(pp) + (1 - o) * math.log(1 - pp)); n += 1
    print(f"log-score sur {n} couples : marché {ll_m/max(1,n):.4f} contre modèle {ll_c/max(1,n):.4f}")
    json.dump([dict(v, key=list(k)) for k, v in bets.items()], open(ROOT / "donnees/paris_crypto.json", "w"))
main()
