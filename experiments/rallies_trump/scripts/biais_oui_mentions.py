"""Contre-épreuve : biais du OUI dans les marchés « What will X say … » hors meetings (donnees/mentions.json).
OUI réalisé contre prix moyen, rendement du NON par tranche, bootstrap par événement. Sans frais (Gamma : feesEnabled false sur les mentions) puis avec 0,04·p(1−p) ; écart d'achat 0,02."""
import json, os, sys, random, bisect, collections, re, statistics as st
D = os.path.join(os.path.dirname(__file__), '..', 'donnees')
rows = [r for r in json.load(open(os.path.join(D, sys.argv[1] if len(sys.argv) > 1 else 'mentions.json'))) if len(r['hist']) >= 3]
random.seed(3)
def orateur(t):
    m = re.match(r'\s*what will (.*?) (say|mention)', t, re.I)
    return (m.group(1).lower() if m else 'autre')
def pts(delay, filt=lambda r: True):
    out = []
    for r in rows:
        if not filt(r): continue
        t = min(r['start'] + delay * 3600, r['end'] - 3 * 3600)
        if t <= r['start']: continue
        ts = [a for a, b in r['hist']]; i = bisect.bisect_right(ts, t) - 1
        if i < 0: continue
        out.append((r['hist'][i][1], r['yes'], r['event'], orateur(r['titre'])))
    return out
def non(p, y, fee):
    cost = 1 - p + 0.02
    return ((0 if y else 1) - cost - (0.04 * cost * (1 - cost) if fee else 0)) / cost, cost
def boot(v, fee):
    ev = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for p, y, e, o in v:
        r, c = non(p, y, fee); ev[e][0] += r * c; ev[e][1] += c; ev[e][2] += 1
    e = list(ev.values()); tot = lambda s: sum(x[0] for x in s) / sum(x[1] for x in s)
    bs = sorted(tot([random.choice(e) for _ in e]) for _ in range(2000))
    return tot(e), bs[50], bs[1950], len(e)
for delay in (6, 24):
    P = pts(delay)
    print(f"--- délai {delay} h : {len(P)} marchés, {len({x[2] for x in P})} événements ; OUI réalisé {sum(x[1] for x in P)/len(P):.3f} pour prix moyen {st.mean(x[0] for x in P):.3f}")
    for lo, hi in ((0.03, 0.15), (0.15, 0.30), (0.30, 0.45), (0.45, 0.60), (0.60, 0.75), (0.75, 0.97), (0.40, 0.70)):
        v = [x for x in P if lo <= x[0] < hi]
        if len(v) < 30: continue
        a = boot(v, True); b = boot(v, False)
        print(f"  OUI {lo:.2f}-{hi:.2f} n={len(v):5d} prix {st.mean(x[0] for x in v):.3f} réalisé {st.mean(1 if x[1] else 0 for x in v):.3f}  NON avec frais {a[0]*100:+6.1f} % [{a[1]*100:+.1f} ; {a[2]*100:+.1f}]  sans frais {b[0]*100:+6.1f} % ({a[3]} évén.)")
    top = collections.Counter(x[3] for x in P).most_common(6)
    for o, n in top:
        v = [x for x in P if x[3] == o and 0.40 <= x[0] < 0.70]
        if len(v) >= 30:
            a = boot(v, True); print(f"    {o[:20]:20s} OUI 0,40-0,70 n={len(v):4d} NON {a[0]*100:+6.1f} % [{a[1]*100:+.1f} ; {a[2]*100:+.1f}]")
