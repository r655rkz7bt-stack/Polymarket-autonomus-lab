"""Tennis : log-score du modèle « prix recalibré » contre le prix du marché, apprentissage sur la 1re moitié
des matchs (par date), test sur la 2e. Modèle : logit(p') = a·logit(p) (a > 1 : le favori est sous-coté)."""
import json, math, sys
rows = {r["id"]: r for r in json.load(open("donnees/matchs.json"))}
data = [(rows[json.loads(l)["id"]], json.loads(l)) for l in open("donnees/prix.jsonl")]
def snap(h, t, tol=1800):
    pts = [x for x in h if x[0] <= t]
    return pts[-1][1] if pts and t - pts[-1][0] <= tol else None
logit = lambda p: math.log(p / (1 - p)); sig = lambda x: 1 / (1 + math.exp(-x))
def ll(pairs, a):
    return -sum(math.log(min(max(sig(a * logit(q)), 1e-6), 1 - 1e-6)) if y else math.log(min(max(1 - sig(a * logit(q)), 1e-6), 1 - 1e-6)) for q, y in pairs) / len(pairs)
for name, off, lo, hi in (("avant le match (J-1h), tous prix", -3600, 0.02, 0.98), ("avant le match, favori 0,8-0,95", -3600, 0.8, 0.95),
                          ("en jeu +30 min, favori 0,8-0,95", 1800, 0.8, 0.95), ("en jeu +30 min, tous prix", 1800, 0.02, 0.98)):
    cases = []
    for r, p in data:
        q = snap(p["h"], p["st"] + off)
        if q is None: continue
        y = 1 if r["won"] == 0 else 0
        if max(q, 1 - q) < lo or max(q, 1 - q) >= hi and hi < 0.98: continue
        if not (lo <= q <= hi or lo <= 1 - q <= hi) and hi < 0.98: continue
        cases.append((p["st"], q, y, r["circuit"]))
    cases.sort(); half = len(cases) // 2
    train = [(q, y) for _, q, y, _ in cases[:half]]; test = [(q, y) for _, q, y, _ in cases[half:]]
    best = min((a / 100 for a in range(80, 160)), key=lambda a: ll(train, a))
    print(f"{name}: n={len(cases)} a appris={best:.2f}  log-loss test marché={ll(test, 1):.4f} modèle={ll(test, best):.4f} gain={(ll(test, 1) - ll(test, best)) * len(test):+.2f} nats sur {len(test)} matchs")
