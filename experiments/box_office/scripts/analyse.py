"""Box-office du premier week-end : calibration des tranches et achats simulés aux prix des vrais échanges."""
import gzip, json, re, sys, math, bisect
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
R = Path("experiments/box_office/releves")
EV = json.load(gzip.open(R / "evenements.json.gz", "rt"))
def ts(s): 
    from datetime import datetime
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
def load(eid):
    p = R / "echanges" / f"echanges_{eid}.json.gz"
    return json.loads(gzip.decompress(p.read_bytes())) if p.exists() else []
def winner(e):
    w = [m for m in e["markets"] if m["prices"] and float(json.loads(m["prices"])[0]) > 0.99]
    return w[0] if len(w) == 1 else None
def yes_series(trades, tok, other):
    """Prix du OUI de la tranche à chaque échange (échange du jeton, ou 1-p sur l'autre issue)."""
    pts = sorted((t[0], t[3] if t[1] == tok else 1 - t[3]) for t in trades if t[1] in (tok, other))
    return [p[0] for p in pts], [p[1] for p in pts]
def last_before(series, t, win):
    xs, ps = series
    i = bisect.bisect_right(xs, t) - 1
    return ps[i] if i >= 0 and t - xs[i] <= win else None
def taker_buy(trades, tok, other, t, win, side):
    """prix payé pour acheter OUI (side=1) ou NON (side=0) : dernier achat de cette issue (ou vente de l'autre) avant t."""
    want, opp = (tok, other) if side else (other, tok)
    pts = sorted((x[0], x[3] if x[1] == want else 1 - x[3]) for x in trades if (x[1] == want and x[2] == "BUY") or (x[1] == opp and x[2] == "SELL"))
    sel = [p for w, p in pts if t - win <= w <= t]
    return sel[-1] if sel else None
HORIZONS = [168, 96, 72, 48, 24, 12]
def cases(filt=lambda e: True):
    out = []
    for e in EV:
        if not e["closed"] or not e.get("end") or not re.search("Opening Weekend", e["title"]) or not filt(e): continue
        w = winner(e)
        if not w or len(e["markets"]) < 3: continue
        trades = load(e["id"]); end = ts(e["end"])
        if len(trades) < 20: continue
        ms = []
        for m in e["markets"]:
            if len(m["tokens"]) != 2: break
            ms.append(dict(m, series=yes_series(trades, m["tokens"][0], m["tokens"][1]), win=int(m is w)))
        else:
            out.append(dict(e=e, trades=trades, end=end, ms=ms))
    return out
if __name__ == "__main__":
    C = cases(); print(len(C), "événements utilisables")
    for h in HORIZONS:
        # calibration : prix du OUI de chaque tranche (dernier échange avant end-h, au plus 6 h plus tôt) contre issue
        rows = []
        for c in C:
            t = c["end"] - h * 3600
            ps = [(last_before(m["series"], t, 8 * 3600), m["win"]) for m in c["ms"]]
            if any(p is None for p, _ in ps): continue
            s = sum(p for p, _ in ps)
            rows += [(p, w, s) for p, w in ps]
        bins = [(0, .05), (.05, .15), (.15, .3), (.3, .5), (.5, 1.01)]
        print(f"h={h}: {len(rows)//5 if rows else 0} événements-tranches {len(rows)}; somme des OUI médiane {sorted(r[2] for r in rows)[len(rows)//2]:.2f}" if rows else f"h={h}: rien")
        for lo, hi in bins:
            sel = [r for r in rows if lo <= r[0] < hi]
            if sel: print(f"   {lo:.2f}-{hi:.2f}: n={len(sel)} gagnantes {sum(r[1] for r in sel)} attendues {sum(r[0] for r in sel):.1f}")
