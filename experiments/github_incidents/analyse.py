"""Plus long incident « critical » du mois (hors Copilot seul, lu au nom) : loi du maximum final sachant le maximum au jour J."""
import json, re, sys, collections, datetime as dt
MOIS = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
def duree(ts, an):
    t = re.sub(r"<[^>]+>", "", ts)
    g = re.match(r"(\w{3}) (\d+), (\d+):(\d+) - (?:(\w{3}) (\d+), )?(\d+):(\d+) UTC", t)
    if not g: return None, None
    a = dt.datetime(an, MOIS[g[1]], int(g[2]), int(g[3]), int(g[4]))
    b = dt.datetime(an, MOIS[g[5] or g[1]], int(g[6] or g[2]), int(g[7]), int(g[8]))
    if b < a: b = b.replace(year=an + 1) if b.month < a.month else b
    return a, (b - a).total_seconds() / 3600
inc = []
for m in json.load(open("donnees/history.json")):
    for i in m.get("incidents") or []:
        if i.get("impact") != "critical": continue
        a, h = duree(i.get("timestamp", ""), int(m["year"]))
        if a is None: continue
        copilot = "copilot" in i["name"].lower() and not re.search(r"actions|git |pull|issues|pages|webhook|api|codespaces|packages", i["name"].lower())
        inc.append((a, h, copilot, i["name"]))
J = int(sys.argv[1]) if len(sys.argv) > 1 else 14
par_mois = collections.defaultdict(list)
for a, h, cp, n in inc:
    if not cp: par_mois[(a.year, a.month)].append((a, h))
BINS = [(0, 1), (1, 3), (3, 6), (6, 12), (12, 1e9)]
def b(x): return next(i for i, (lo, hi) in enumerate(BINS) if lo <= x < hi)
mois = sorted({(a.year, a.month) for a, *_ in inc})
print("mois couverts", mois[0], "→", mois[-1], ";", len(inc), "incidents critiques dont", sum(1 for x in inc if x[2]), "Copilot seul")
tr = collections.Counter(); finals = collections.Counter()
for ym in mois:
    if ym == mois[-1]: continue
    xs = par_mois.get(ym, [])
    avant = max((h for a, h in xs if a.day < J), default=0)
    final = max((h for a, h in xs), default=0)
    print(ym, "max au jour", J, round(avant, 2), "final", round(final, 2), "n", len(xs))
    tr[(b(avant), b(final))] += 1; finals[b(final)] += 1
print("transitions (tranche au jour J → tranche finale) :", dict(tr))
print("tranche finale, tous mois :", dict(finals))
# loi « depuis le jour J » : max des incidents qui DÉBUTENT au jour >= J (moitié de mois restante)
rest = collections.Counter()
for ym in mois[:-1]:
    xs = par_mois.get(ym, []); rest[b(max((h for a, h in xs if a.day >= J), default=0))] += 1
print("max des incidents nés à partir du jour", J, ":", dict(rest))
