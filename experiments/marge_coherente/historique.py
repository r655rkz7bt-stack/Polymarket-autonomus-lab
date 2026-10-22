"""Piste n° 3 sur le passé : Brésil 1er tour. Somme des tranches « marge » d'un candidat contre son prix « vainqueur du 1er tour » (CLOB, pas de 12 h)."""
import requests, json, bisect, statistics, datetime as dt
H = {"User-Agent": "curl/8"}
def ev(slug): return requests.get("https://gamma-api.polymarket.com/events", headers=H, params={"slug": slug}, timeout=60).json()[0]
def hist(tok, a, b):
    out = []
    while a < b:
        e = min(a + 14 * 86400, b)
        for _ in range(3):
            r = requests.get("https://clob.polymarket.com/prices-history", headers=H, timeout=60, params={"market": tok, "startTs": a, "endTs": e, "fidelity": 720})
            if r.status_code == 200: out += [(x["t"], x["p"]) for x in r.json().get("history", [])]; break
        a = e
    return sorted(set(out))
mar = ev("brazil-presidential-election-first-round-margin-of-victory")["markets"]
win = ev("brazil-presidential-election-first-round-winner")["markets"]
t0 = int(dt.datetime(2026, 2, 12, tzinfo=dt.timezone.utc).timestamp()); t1 = int(dt.datetime(2026, 10, 4, 12, tzinfo=dt.timezone.utc).timestamp())
res = {}
for name, key, wkey in (("Flávio", "Flávio", "Flavio"), ("Lula", "Luiz", "Lula")):
    w = [m for m in win if wkey in m["question"]][0]
    hw = hist(json.loads(w["clobTokenIds"])[0], t0, t1)
    ht = [hist(json.loads(m["clobTokenIds"])[0], t0, t1) for m in mar if key in m["question"]]
    def at(h, t):
        i = bisect.bisect_right([x[0] for x in h], t) - 1
        return h[i][1] if i >= 0 else None
    gaps = []; days = []
    for t, pw in hw:
        s = [at(h, t) for h in ht]
        if None in s: continue
        gaps.append(sum(s) - pw); days.append(t)
    print(f"{name}: {len(gaps)} points de {dt.datetime.utcfromtimestamp(days[0]):%d/%m} à {dt.datetime.utcfromtimestamp(days[-1]):%d/%m}, écart (somme des tranches − vainqueur) moyen {statistics.mean(gaps):+.4f}, médiane {statistics.median(gaps):+.4f}, "
          f"|écart| > 0,02 : {sum(1 for g in gaps if abs(g) > 0.02)/len(gaps):.0%}, > 0,05 : {sum(1 for g in gaps if abs(g) > 0.05)/len(gaps):.0%} ; par mois : "
          + ", ".join(f"{m} {statistics.mean([g for g, t in zip(gaps, days) if dt.datetime.utcfromtimestamp(t).month == m]):+.3f}" for m in sorted({dt.datetime.utcfromtimestamp(t).month for t in days})))
