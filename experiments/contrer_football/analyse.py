"""Piste n° 13 : après un gros saut de prix pendant un match de football, le prix dépasse-t-il sa juste valeur ?
Prix = échanges réels (data-api). Saut = variation >= J en 5 min sur le marché « X gagne » (X ou le match nul exclu).
Contrarien : on achète le NON de X après un saut à la hausse (ou le OUI après un saut à la baisse), au prix du premier échange réel
de preneur 1 à 5 minutes après le saut + frais. Suiveur : l'inverse. Un seul saut par match (le premier), pour des paris indépendants."""
import json, gzip, glob, sys, math, datetime as dt, collections
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_football/donnees")
def ts(s): return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00").replace(" ", "T") if "T" in s else s.replace(" ", "T")).timestamp()) if False else int(dt.datetime.fromisoformat(s.replace(" ", "T").replace("Z", "+00:00") + ("+00:00" if s.endswith("+00") else "")).timestamp()) if False else None
def parse(s):
    s = s.replace(" ", "T").replace("Z", "+00:00")
    if s.endswith("+00"): s += ":00"
    return int(dt.datetime.fromisoformat(s).timestamp())
def load():
    out = []
    for f in sorted(glob.glob(str(D / "match" / "*.json.gz"))):
        e = json.loads(gzip.decompress(Path(f).read_bytes()))
        if not e or not e.get("closed"): continue
        p = D / "echanges" / f"echanges_{e['id']}.json.gz"
        if not p.exists(): continue
        trades = json.loads(gzip.decompress(p.read_bytes()))
        mk = [m for m in e["markets"] if m.get("sportsMarketType") == "moneyline" and "draw" not in m["question"].lower()]
        if len(mk) != 2 or not trades: continue
        out.append((e, mk, trades))
    return out
def serie(trades, yes, no):
    pts = sorted((t[0], t[3] if t[1] == yes else 1 - t[3]) for t in trades if t[1] in (yes, no))
    return pts
def price_at(pts, times, t, fresh):
    # dernier point <= t (liste triée), frais s'il date de moins de `fresh` secondes
    import bisect
    i = bisect.bisect_right(times, t) - 1
    if i < 0 or t - times[i] > fresh: return None
    return pts[i][1]
def run(J, back, delay, W=300, side="contre", maxmin=125, minp=0.0):
    res = []
    for e, mk, trades in load():
        try: start = parse(mk[0].get("gameStartTime") or e["startTime"])
        except Exception: continue
        series = {}
        for m in mk:
            yes, no = json.loads(m["clobTokenIds"])
            pts = serie(trades, yes, no); series[m["id"]] = (m, yes, no, pts, [p[0] for p in pts])
        # règlement : le dernier prix échangé doit aller dans le sens du résultat
        found = None
        for minute in range(back // 60 + 1, maxmin + 1):
            t = start + minute * 60
            for mid, (m, yes, no, pts, times) in series.items():
                a = price_at(pts, times, t, 240); b = price_at(pts, times, t - back, 240)
                if a is None or b is None: continue
                if abs(a - b) >= J:
                    if found is None or True:
                        found = (t, m, yes, no, a - b, a); break
            if found: break
        if not found: continue
        t, m, yes, no, dlt, pnow = found
        op = json.loads(m["outcomePrices"]); yes_wins = float(op[0]) > 0.5
        if max(float(op[0]), float(op[1])) < 0.99: continue
        # contrarien : après hausse, on achète NON ; après baisse, OUI. suiveur : l'inverse
        buy_yes = (dlt < 0) if side == "contre" else (dlt > 0)
        tok, oth = (yes, no) if buy_yes else (no, yes)
        c = it.taker_cost(trades, tok, oth, t + delay, window=W, after=True)
        if c is None or c < 0.03 or c > 0.97: continue
        rate = ((m.get("feeSchedule") or {}).get("rate")) or 0.03
        win = yes_wins if buy_yes else (not yes_wins)
        cost = c + it.fee(c, rate)
        res.append(dict(eid=e["id"], day=dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m"), p=c, win=win, gain=(1.0 if win else 0.0) - cost, dlt=dlt, fresh=pnow, minute=(t - start) // 60, price=c, rate=rate))
    return res
def resume(res):
    n = len(res)
    if n == 0: return "0 cas"
    cost = sum(r["p"] + it.fee(r["p"], r["rate"]) for r in res); g = sum(r["gain"] for r in res)
    w = sum(r["win"] for r in res); ex = sum(r["p"] for r in res); var = sum(r["p"] * (1 - r["p"]) for r in res)
    z = (w - ex) / math.sqrt(var) if var else 0
    v = it.verdict([dict(group=r["eid"], gain=r["gain"], cost=r["p"] + it.fee(r["p"], r["rate"]), day=r["day"], price=r["p"], win=r["win"]) for r in res]) if False else None
    return f"n={n:4d} gagnés={w:4d} attendus={ex:6.1f} z={z:+.2f} rendement={100*g/cost:+.1f}%"
if __name__ == "__main__":
    for side in ("contre", "suiveur"):
        for J in (0.08, 0.12, 0.18, 0.25):
            for back, delay in ((300, 60), (120, 60), (300, 180)):
                r = run(J, back, delay, side=side)
                print(side, f"J={J} regard={back//60}min délai={delay//60}min", resume(r), flush=True)
