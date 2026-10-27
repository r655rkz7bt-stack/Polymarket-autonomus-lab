"""Piste « decroissance_temps » rejouée sur le passé (27/10/2026) : marchés « d'ici / avant <date> » réglés, vrais échanges, vrais frais.
Règle de la stratégie : OUI dans [yes_min, yes_max], 12 h <= temps restant <= 720 h, p6 = prix du OUI 6 h plus tôt,
fair = 1 - (1 - p6)^(h/(h+6)), achat du NON si prix_OUI - fair >= min_gap. Un pari par marché (premier horizon qui déclenche, du plus loin au plus proche),
prix payé = premier échange de preneur sur le NON dans les 6 h après T. Aucun échange après T n'est utilisé pour décider."""
import json, gzip, sys, math, datetime as dt, collections
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
D = Path("experiments/decroissance_passe/donnees")
def ts(s):
    if not s: return None
    s = s.replace(" ", "T").replace("Z", "+00:00")
    if s.endswith("+00"): s += ":00"
    return int(dt.datetime.fromisoformat(s).timestamp())
def charge(fichiers=("marches.jsonl",)):
    out, vus = [], set()
    for l in (l for f in fichiers for l in open(D / f)):
        e = json.loads(l); p = D / "echanges" / f"echanges_{e['id']}.json.gz"
        if e["id"] in vus: continue
        vus.add(e["id"])
        if not p.exists(): continue
        tr = json.loads(gzip.decompress(p.read_bytes()))
        by = collections.defaultdict(list)
        for t in tr: by[t[1]].append(t)
        out.append((e, by))
    return out
def prix_oui(by, yes, no, a, b):
    """dernier prix du OUI (échange quelconque) dans ]a, b], ou None"""
    best = None
    for t in by.get(yes, []):
        if a < t[0] <= b and (best is None or t[0] >= best[0]): best = (t[0], t[3])
    for t in by.get(no, []):
        if a < t[0] <= b and (best is None or t[0] >= best[0]): best = (t[0], 1 - t[3])
    return None if best is None else best[1]
def premier_achat_non(by, yes, no, T, W):
    pts = [(t[0], t[3]) for t in by.get(no, []) if t[2] == "BUY" and T <= t[0] <= T + W]
    pts += [(t[0], 1 - t[3]) for t in by.get(yes, []) if t[2] == "SELL" and T <= t[0] <= T + W]
    return min(pts)[1] if pts else None
def paris(EV, horizons=(30, 21, 14, 10, 7, 5, 3, 2, 1, 0.5), ymin=0.03, ymax=0.35, gap_min=0.01, fen_now=3 * 3600, fen_p6=24 * 3600, W=6 * 3600, un_par_marche=True, cote="non"):
    res = []
    for e, by_all in EV:
        for m in e["markets"]:
            try:
                op = [float(x) for x in json.loads(m["outcomePrices"])]; yes, no = json.loads(m["clobTokenIds"])
                outs = json.loads(m["outcomes"])
            except Exception: continue
            if outs != ["Yes", "No"] or max(op) < 0.99: continue
            end = ts(m.get("endDate")); closed = ts(m.get("closedTime")); start = ts(m.get("startDate"))
            if not end or not start: continue
            by = {yes: by_all.get(yes, []), no: by_all.get(no, [])}
            rate = ((m.get("feeSchedule") or {}).get("rate")) or 0.0
            for H in horizons:
                T = end - int(H * 86400)
                if T < start + 12 * 3600 or (closed and T > closed - 3600): continue
                h = (end - T) / 3600
                if not (12 <= h <= 720): continue
                now = prix_oui(by, yes, no, T - fen_now, T)
                if now is None or not (ymin <= now <= ymax): continue
                p6 = prix_oui(by, yes, no, T - 6 * 3600 - fen_p6, T - 6 * 3600)
                if p6 is None or p6 <= 0: continue
                fair = 1 - (1 - min(p6, 0.99)) ** (h / (h + 6))
                if now - fair < gap_min: continue
                pay = premier_achat_non(by, yes, no, T, W) if cote == "non" else premier_achat_non(by, no, yes, T, W)
                if pay is None or pay < 0.03 or pay > 0.97: continue
                f = it.fee(pay, rate)
                win = op[1] > 0.5 if cote == "non" else op[0] > 0.5
                res.append(dict(eid=e["id"], mid=m["id"], H=H, now=now, p6=p6, fair=fair, ratio=now / p6, pay=pay, win=win, fee=f,
                                gain=(win - pay - f) / (pay + f), mois=dt.datetime.fromtimestamp(end, dt.timezone.utc).strftime("%Y-%m"),
                                titre=m["question"][:70]))
                if un_par_marche: break
    return res
def resume(res):
    n = len(res)
    if not n: return "0 cas"
    cost = sum(r["pay"] + r["fee"] for r in res); g = sum(r["win"] - r["pay"] - r["fee"] for r in res)
    w = sum(r["win"] for r in res); ex = sum(r["pay"] for r in res); var = sum(r["pay"] * (1 - r["pay"]) for r in res)
    byev = collections.defaultdict(list)
    for r in res: byev[r["eid"]].append(r["gain"])
    mm = [sum(v) / len(v) for v in byev.values()]
    t = it._t_stat(mm) if len(mm) > 2 else 0
    return f"n={n:5d} évts={len(byev):4d} gagnés={w:5d} attendus={ex:7.1f} z={(w-ex)/math.sqrt(var):+.2f} rendement={100*g/cost:+.1f}% t_évt={t:+.2f}"
if __name__ == "__main__":
    EV = charge(); print("événements", len(EV), "marchés", sum(len(e['markets']) for e, _ in EV))
    R = paris(EV)
    print("== règle de la stratégie (un pari par marché):", resume(R))
    for lo, hi in ((0, 0.8), (0.8, 1.0), (1.0, 1.25), (1.25, 2), (2, 4), (4, 1e9)):
        print(f"   ratio prix/p6 {lo}-{hi}:", resume([r for r in R if lo <= r["ratio"] < hi]))
    for lo, hi in ((0, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 1)):
        print(f"   gap {lo}-{hi}:", resume([r for r in R if lo <= r["now"] - r["fair"] < hi]))
    for H in (30, 14, 7, 3, 1):
        print(f"   premier déclenchement à H={H} j:", resume([r for r in R if r["H"] == H]))
    v = it.verdict([dict(gain=r["gain"], evenement=r["eid"], mois=r["mois"], cout=r["pay"] + r["fee"]) for r in R])
    print(json.dumps({k: v[k] for k in v if k in ("paris", "verdict", "rendement", "t_evenement", "z_prix", "mois_gagnants", "moitie_1", "moitie_2")}, ensure_ascii=False))
