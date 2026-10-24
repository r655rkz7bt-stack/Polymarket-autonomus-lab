"""Compteurs de lancements SpaceX (24/10/2026) : « combien de lancements en <mois / année> ? » contre le cumul déjà fait (Launch Library 2)
+ cadence récente. Test sur 9 mois réglés (janv. → sept. 2026, sauf juillet) + l'année 2025, aux prix des vrais échanges.
Décision à 12 h UTC chaque jour ; cumul = lancements dont le NET est avant l'instant de décision (rien du futur) ; cadence = lancements des
120 jours précédents. Modèles : poisson, sous (variance 0,5 × moyenne : SpaceX est très régulier), fenetre (distribution empirique du nombre de
lancements dans des fenêtres de même durée sur les 365 jours précédents). Achat au premier échange réel dans les 2 h après la décision.
Usage : PYTHONPATH=src python backtest.py"""
import collections, datetime as dt, json, math, re, sys
from pathlib import Path
from zoneinfo import ZoneInfo
from polymarket_agent import idea_test as it
from polymarket_agent.http_client import HttpClient
ROOT = Path(__file__).resolve().parents[1]
ET = ZoneInfo("America/New_York"); UTC = dt.timezone.utc
EV = json.load(open(ROOT / "donnees/evenements.json"))
L = sorted(dt.datetime.fromisoformat(x[0].replace("Z", "+00:00")) for x in json.load(open(ROOT / "donnees/lancements.json")))
MOIS = {m: i + 1 for i, m in enumerate("january february march april may june july august september october november december".split())}

def periode(e):
    t = e["title"].lower(); end = dt.datetime.fromisoformat(e["endDate"].replace("Z", "+00:00"))
    m = re.search(r"in (\w+)(?: (\d{4}))?\?", t)
    w, y = m.group(1), m.group(2)
    if w.isdigit():
        yr = int(w); a, b = dt.datetime(yr, 1, 1, tzinfo=ET), dt.datetime(yr + 1, 1, 1, tzinfo=ET)
    else:
        yr = int(y) if y else end.year if end.month != 1 else end.year  # « January » sans année : 2026
        yr = int(y) if y else 2026
        mo = MOIS[w]; a = dt.datetime(yr, mo, 1, tzinfo=ET); b = dt.datetime(yr + (mo == 12), mo % 12 + 1, 1, tzinfo=ET)
    return a.astimezone(UTC), b.astimezone(UTC)

def tranche(q):
    s = q.lower()
    if m := re.search(r"(?:fewer|less) than (\d+)", s): return (-1, int(m.group(1)) - 1)
    if m := re.search(r"between (\d+)-(\d+)", s) or re.search(r"between (\d+) and (\d+)", s): return (int(m.group(1)), int(m.group(2)))
    if m := re.search(r"exactly (\d+)", s): return (int(m.group(1)), int(m.group(1)))
    if m := re.search(r"(\d+)(?:\+| or more)", s): return (int(m.group(1)), 10**6)
    return None

def compte(a, b): return sum(1 for t in L if a <= t < b)

def loi(modele, N, a, b, T):
    d = (b - T).total_seconds() / 86400; lam = compte(T - dt.timedelta(days=120), T) / 120
    mu = lam * d
    if modele == "poisson":
        pk = lambda k: math.exp(-mu + k * math.log(mu) - math.lgamma(k + 1)) if mu > 0 else float(k == 0)
    elif modele == "sous":
        sd = math.sqrt(max(0.5 * mu, 0.05)); pk = lambda k: math.erf((k + 0.5 - mu) / (sd * 2**.5)) / 2 - math.erf((k - 0.5 - mu) / (sd * 2**.5)) / 2
    else:  # fenetre
        w = dt.timedelta(days=d); cnt = collections.Counter(); n = 0; s = T - dt.timedelta(days=365)
        while s + w <= T:
            cnt[compte(s, s + w)] += 1; n += 1; s += dt.timedelta(days=1)
        if n < 10: return None
        pk = lambda k: cnt[k] / n
    return {N + k: pk(k) for k in range(0, 400)}

def probs(modele, N, a, b, T, tranches):
    P = loi(modele, N, a, b, T)
    if P is None: return None
    tot = sum(P.values()) or 1
    return {mid: sum(p for n, p in P.items() if lo <= n <= hi) / tot for mid, (lo, hi) in tranches.items()}

def main():
    http = HttpClient(timeout=40, min_interval=0.25)
    evs = [e for e in EV if e["closed"]]
    bets = {}
    controle = []
    for e in sorted(evs, key=lambda e: e["endDate"]):
        a, b = periode(e); tr = it.fetch_event_trades(http, ROOT / "donnees/echanges", e["id"])
        tranches = {q["id"]: tranche(q["question"]) for q in e["markets"]}
        gagnante = [q["id"] for q in e["markets"] if json.loads(q["outcomePrices"])[0] == "1"]
        reel = compte(a, b); ok = len(gagnante) == 1 and tranches[gagnante[0]][0] <= reel <= tranches[gagnante[0]][1]
        controle.append((e["title"][-22:], reel, tranches[gagnante[0]] if gagnante else None, ok))
        if not ok: continue
        t0 = min(t[0] for t in tr) if tr else None
        if t0 is None: continue
        T = dt.datetime.combine(dt.datetime.fromtimestamp(t0, UTC).date() + dt.timedelta(days=1), dt.time(12), tzinfo=UTC)
        pas = 1 if (b - a).days < 60 else 7
        fee_rate = float((e["markets"][0].get("feeSchedule") or {}).get("rate") or 0) if e["markets"][0].get("feesEnabled") else 0
        while T < b - dt.timedelta(hours=12):
            N = compte(a, T)
            for modele in ("poisson", "sous", "fenetre"):
                pr = probs(modele, N, a, b, T, {k: v for k, v in tranches.items() if v})
                if pr is None: continue
                for q in e["markets"]:
                    if not tranches[q["id"]]: continue
                    yes, no = json.loads(q["clobTokenIds"])
                    for cote, tok, oth, p in (("OUI", yes, no, pr[q["id"]]), ("NON", no, yes, 1 - pr[q["id"]])):
                        c = it.taker_cost(tr, tok, oth, int(T.timestamp()), window=2 * 3600, after=True)
                        if c is None: continue
                        for seuil in (0.03, 0.05, 0.10):
                            key = (modele, seuil, e["id"], q["id"])
                            if key in bets or p - c - it.fee(c, fee_rate) <= seuil or c > 0.98 or c < 0.03: continue
                            gagne = (q["id"] in gagnante) == (cote == "OUI")
                            bets[key] = dict(gain=((1.0 if gagne else 0.0) - c - it.fee(c, fee_rate)) / c, evenement=e["id"], mois=e["endDate"][:7], cout=c, cote=cote,
                                             jours=(b - T).days, modele=modele, seuil=seuil, proba=p)
            T += dt.timedelta(days=pas)
    print("contrôle du règlement (cumul LL2 dans la tranche gagnante) :"); [print("  ", c) for c in controle]
    reglages = sorted({(k[0], k[1]) for k in bets} | {(m, s) for m in ("poisson", "sous", "fenetre") for s in (0.03, 0.05, 0.10)})
    for modele, seuil in reglages:
        bs = [v for k, v in bets.items() if k[0] == modele and k[1] == seuil]
        v = it.verdict(bs)
        print(f"{modele:8s} seuil {seuil:.2f} : {v.get('paris', 0):3d} paris, rendement {v.get('rendement_moyen', v.get('mean', float('nan'))) if isinstance(v, dict) else ''} {v.get('verdict')} ; {v.get('raison', '')[:90]}")
    json.dump([dict(v, key=list(k)) for k, v in bets.items()], open(ROOT / "donnees/paris.json", "w"))
main()
