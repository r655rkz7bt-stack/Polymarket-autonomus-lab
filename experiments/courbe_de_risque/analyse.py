"""Piste n° 8 : sur les échelles de dates (« X avant le <date> »), le NON des marchés est-il en moyenne trop bon marché / trop cher
à H jours de l'échéance ? Prix = premier échange réel de preneur dans les 6 h après la décision. Résultats : par événement, par catégorie, par mois."""
import json, gzip, sys, math, re, datetime as dt, collections
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
D = Path("experiments/courbe_de_risque/donnees")
def parse(s):
    s = s.replace(" ", "T").replace("Z", "+00:00")
    if s.endswith("+00"): s += ":00"
    return int(dt.datetime.fromisoformat(s).timestamp())
def categorie(t):
    t = t.lower()
    if "token" in t or "airdrop" in t or "mainnet" in t or "tge" in t: return "crypto_lancement"
    if "ceasefire" in t or "peace" in t or "iran" in t or "israel" in t or "ukraine" in t or "russia" in t or "war" in t: return "geopolitique"
    if "release" in t or "launch" in t or "debut" in t or "gta" in t: return "sorties"
    if "trump" in t or "say" in t or "tweet" in t: return "trump_mots"
    return "autre"
def load():
    out = []
    for l in open(D / "echelles.jsonl"):
        e = json.loads(l); p = D / "echanges" / f"echanges_{e['id']}.json.gz"
        if not p.exists(): continue
        out.append((e, json.loads(gzip.decompress(p.read_bytes()))))
    return out
EV = None
def run(H, side="non", W=6 * 3600, pmin=0.03, pmax=0.97, cat=None):
    global EV
    if EV is None: EV = load()
    res = []
    for e, trades in EV:
        c = categorie(e["title"])
        if cat and c != cat: continue
        for m in e["markets"]:
            try:
                end = parse(m["endDate"]); start = parse(m.get("startDate") or e["startDate"])
                op = [float(x) for x in json.loads(m["outcomePrices"])]; yes, no = json.loads(m["clobTokenIds"])
            except Exception: continue
            if max(op) < 0.99: continue
            T = end - int(H * 86400)
            if T < start + 3600: continue
            tok, oth = (no, yes) if side == "non" else (yes, no)
            p = it.taker_cost(trades, tok, oth, T, window=W, after=True)
            if p is None or p < pmin or p > pmax: continue
            rate = ((m.get("feeSchedule") or {}).get("rate")) or 0.0
            win = (op[1] > 0.5) if side == "non" else (op[0] > 0.5)
            res.append(dict(eid=e["id"], cat=c, p=p, win=win, rate=rate, mois=dt.datetime.fromtimestamp(end, dt.timezone.utc).strftime("%Y-%m")))
    return res
def resume(res):
    n = len(res)
    if not n: return "0 cas"
    cost = sum(r["p"] + it.fee(r["p"], r["rate"]) for r in res); g = sum(r["win"] - r["p"] - it.fee(r["p"], r["rate"]) for r in res)
    w = sum(r["win"] for r in res); ex = sum(r["p"] for r in res); var = sum(r["p"] * (1 - r["p"]) for r in res)
    byev = collections.defaultdict(list)
    for r in res: byev[r["eid"]].append((r["win"] - r["p"] - it.fee(r["p"], r["rate"])) / (r["p"] + it.fee(r["p"], r["rate"])))
    m = [sum(v) / len(v) for v in byev.values()]
    t = it._t_stat(m) if len(m) > 2 else 0
    return f"n={n:5d} évts={len(byev):4d} gagnés={w:5d} attendus={ex:7.1f} z={(w-ex)/math.sqrt(var):+.2f} rendement={100*g/cost:+.1f}% t_par_événement={t:+.2f}"
if __name__ == "__main__":
    for side in ("non", "oui"):
        for H in (3, 7, 14, 30):
            r = run(H, side)
            print(f"== {side.upper()} à {H} j:", resume(r), flush=True)
            for c in sorted({x['cat'] for x in r}): print("    ", c.ljust(18), resume([x for x in r if x['cat'] == c]), flush=True)
