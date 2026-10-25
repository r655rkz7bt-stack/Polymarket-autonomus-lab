"""Contrôle du règlement : le nombre de posts de l'archive retombe-t-il sur la tranche gagnante de Gamma ?"""
import csv, json, re
from datetime import datetime, timedelta, timezone
def lire_posts(path="experiments/truth_social/releves/posts.csv"):
    return sorted(datetime.fromisoformat(r["ts_utc"]) for r in csv.DictReader(open(path)))
def bornes(titre):
    m = re.fullmatch(r"<(\d+)", titre)
    if m: return 0, int(m.group(1)) - 1
    m = re.fullmatch(r"(\d+)\+", titre)
    if m: return int(m.group(1)), 10**9
    m = re.fullmatch(r"(\d+)-(\d+)", titre)
    return (int(m.group(1)), int(m.group(2))) if m else None
def gagnante(ev):
    for m in ev["markets"]:
        p = json.loads(m["outcomePrices"])
        if float(p[0]) > 0.99: return m["groupItemTitle"]
def fenetre(ev):
    fin = datetime.fromisoformat(ev["endDate"].replace("Z", "+00:00"))
    return fin - timedelta(days=7), fin
if __name__ == "__main__":
    import bisect
    posts = lire_posts()
    ev = json.load(open("experiments/truth_social/donnees/evenements.json"))
    ok = n = 0; ecarts = []
    for e in ev:
        d, f = fenetre(e)
        if d < posts[0] + timedelta(days=1) or f > datetime.now(timezone.utc) or not e.get("closed"): continue
        g = gagnante(e)
        if g is None: continue
        c = bisect.bisect_left(posts, f) - bisect.bisect_left(posts, d)
        lo, hi = bornes(g); n += 1; bon = lo <= c <= hi; ok += bon
        ecarts.append((e["slug"][-24:], c, g, "OK" if bon else "écart"))
    for x in ecarts: print(*x)
    print(ok, "sur", n)
