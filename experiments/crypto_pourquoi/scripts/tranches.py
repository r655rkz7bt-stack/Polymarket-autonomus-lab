"""28/10/2026 : marchés « Will the price of Bitcoin be between $A and $B on <date> ? » (tranches du jour, réglées à 12 h heure de l'Est), les paris NEUTRES en direction : un OUI de tranche étroite
gagne quand le cours finit dans la tranche, quelle que soit la direction. Compare le prix du OUI (dernier échange avant T = fin − h) au modèle log-normal sans dérive (volatilité des 168 h finies)
et à l'issue ; bets : OUI et NON payés (premier échange réel qui achète dans l'heure), frais du marché. Usage : PYTHONPATH=src python tranches.py marches_a.jsonl,marches_b.jsonl"""
import bisect, gzip, json, math, re, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_crypto_passe/donnees"); SP = Path("experiments/crypto_pourquoi/donnees")
ASSETS = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "xrp": "XRP"}
spot = {}
for a in set(ASSETS.values()):
    rows = json.load(open(SP / f"spot_{a}.json")); spot[a] = (([r[0] for r in rows]), [r[4] for r in rows])
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    try: return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError: return None
def phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def vol(a, T, n=168):
    t, c = spot[a]; i = bisect.bisect_right(t, T - 3600) - 1
    if i < n + 1: return None, None
    r = [math.log(c[j] / c[j - 1]) for j in range(i - n + 1, i + 1)]; m = sum(r) / n
    return math.sqrt(sum((x - m) ** 2 for x in r) / (n - 1)), c[i]
ms = [json.loads(l) for nom in sys.argv[1].split(",") for l in open(D / nom)]
seen = set(); ms = [m for m in ms if not (m["id"] in seen or seen.add(m["id"]))]
snaps = []
for m in ms:
    q = m["question"]; ql = q.lower()
    if not (m["vol"] or 0) >= 5000 or "between" not in ql or sorted(map(str, m["prices"])) != ["0", "1"]: continue
    a = next((v for k, v in ASSETS.items() if k in ql), None)
    nums = [float(x.replace(",", "")) for x in re.findall(r"\$([\d,]+(?:\.\d+)?)", q)]
    if not a or len(nums) != 2: continue
    p = D / "echanges" / f"{m['id']}.json.gz"
    if not p.exists(): continue
    end = ts(m["end"]); tr = sorted(json.loads(gzip.decompress(p.read_bytes()))["echanges"])
    if end is None or len(tr) < 3: continue
    yes, no = m["yes"], m["no"]
    ser = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr]; st = [x[0] for x in ser]
    by = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr if (t[1] == yes and t[2] == "BUY") or (t[1] == no and t[2] == "SELL")]
    bn = [(t[0], t[3] if t[1] == no else 1 - t[3]) for t in tr if (t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")]
    fs = m["feeSchedule"] if isinstance(m["feeSchedule"], dict) else {}; rate = float(fs.get("rate") or 0) if m["feesEnabled"] else 0.0
    lo, hi = sorted(nums); won = 1 if str(m["prices"][0]) == "1" else 0
    for h in (3, 6, 12, 24):
        T = end - h * 3600; i = bisect.bisect_left(st, T) - 1
        if i < 0 or T - st[i] > 3 * 3600: continue
        sig, S = vol(a, T)
        if sig is None: continue
        tau = h; pm = phi(math.log(hi / S) / (sig * math.sqrt(tau))) - phi(math.log(lo / S) / (sig * math.sqrt(tau)))
        jy = bisect.bisect_left([x[0] for x in by], T); jn = bisect.bisect_left([x[0] for x in bn], T)
        py = by[jy][1] if jy < len(by) and by[jy][0] <= T + 3600 else None
        pn = bn[jn][1] if jn < len(bn) and bn[jn][0] <= T + 3600 else None
        snaps.append(dict(id=m["id"], ev=m["event_id"], a=a, h=h, pyes=ser[i][1], pm=pm, won=won, py=py, pn=pn, rate=rate, mois=dt.datetime.utcfromtimestamp(T).strftime("%Y-%m"), dist=abs(math.log((lo + hi) / 2 / S)) / (sig * math.sqrt(tau))))
print(len(snaps), "instants,", len({s['id'] for s in snaps}), "marchés de tranches,", len({s['ev'] for s in snaps}), "événements")
def ls(p, y): p = min(max(p, 1e-3), 1 - 1e-3); return math.log(p if y else 1 - p)
for h in (3, 6, 12, 24):
    r = [s for s in snaps if s["h"] == h]
    if len(r) < 20: continue
    d = [ls(s["pm"], s["won"]) - ls(s["pyes"], s["won"]) for s in r]
    print(f"h={h:2d} n={len(r):4d} OUI réel {sum(s['won'] for s in r)/len(r):.3f} prix moyen {sum(s['pyes'] for s in r)/len(r):.3f} modèle moyen {sum(s['pm'] for s in r)/len(r):.3f}  log-score modèle − prix {sum(d)/len(d):+.4f}")
print("\n| côté, prix payé, h | paris | évén. | rendement | t | gagnés/attendus | verdict |")
for side in ("oui", "non"):
    for lo_, hi_ in ((0.02, 0.10), (0.10, 0.25), (0.25, 0.45), (0.55, 0.80), (0.80, 0.97)):
        for h in (3, 6, 12, 24):
            b = []
            for s in snaps:
                p = s["py"] if side == "oui" else s["pn"]
                if s["h"] != h or p is None or not lo_ <= p <= hi_: continue
                w = s["won"] if side == "oui" else 1 - s["won"]
                b.append(dict(gain=(w - p - s["rate"] * p * (1 - p)) / p, cout=p, evenement=s["ev"], mois=s["mois"], gagne=w))
            if len(b) < 20: continue
            v = it.verdict(b); g = sum(x["gagne"] for x in b); a_ = sum(x["cout"] for x in b)
            print(f"| {side.upper()} {lo_}-{hi_} h={h} | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t évén. {v['confiance_evenements']:+.2f} | {g} / {a_:.1f} (z {v['z_prix']:+.2f}) | {v['verdict']} |")
print("\n== tranches cotées ≥ 0,55 (OUI) : prix, modèle, issue ==")
for h in (3, 6, 12, 24):
    r = [s for s in snaps if s["h"] == h and s["pyes"] >= 0.55]
    if len(r) >= 10: print(f"h={h:2d} n={len(r):3d} OUI réel {sum(s['won'] for s in r)/len(r):.3f} prix moyen {sum(s['pyes'] for s in r)/len(r):.3f} modèle moyen {sum(s['pm'] for s in r)/len(r):.3f}")
