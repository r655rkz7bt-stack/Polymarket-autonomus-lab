"""28/10/2026 : les 3 dernières heures avant le règlement à 12 h (heure de l'Est = 16 h UTC) des échelles « <actif> price on <date> » tombent dans l'ouverture de Wall Street : la volatilité
horaire y vaut ≈ 2× la moyenne (variance ; 1,45× en écart-type). Le modèle log-normal à volatilité de 168 h plate est donc trop sûr de lui, et le prix aussi (en partie) : les tranches centrales cotées
≥ 0,55 gagnent 74 % pour un prix moyen de 0,82 à 3 h (z −4,3). Ce script ajoute au modèle un PROFIL horaire de variance estimé sur 2024-2025 SEULEMENT (aucun regard vers le futur : le test porte
sur 2026) et compare au prix, puis joue les écarts. Usage : PYTHONPATH=src python saison_vol.py marches_a.jsonl,marches_e.jsonl"""
import bisect, gzip, json, math, os, re, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_crypto_passe/donnees"); SP = Path("experiments/crypto_pourquoi/donnees")
ASSETS = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "xrp": "XRP"}
spot, profil = {}, {}
DEB2026 = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc).timestamp()
DEB2025 = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp()
for a in set(ASSETS.values()):
    rows = json.load(open(SP / f"spot_{a}.json")); spot[a] = ([r[0] for r in rows], [r[4] for r in rows])
    by = [[] for _ in range(24)]
    for i in range(1, len(rows)):
        if rows[i][0] >= DEB2026: break          # profil estimé AVANT 2026
        lr = math.log(rows[i][4] / rows[i - 1][4]); by[dt.datetime.utcfromtimestamp(rows[i][0]).hour].append(lr * lr)
    allv = sum(sum(x) for x in by) / sum(len(x) for x in by)
    profil[a] = [(sum(x) / len(x)) / allv for x in by]   # variance de l'heure / variance moyenne ; barre dont le DÉBUT est à l'heure h
def phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def sig_base(a, T, n=168):
    t, c = spot[a]; i = bisect.bisect_right(t, T - 3600) - 1
    if i < n + 1: return None, None
    r = [math.log(c[j] / c[j - 1]) for j in range(i - n + 1, i + 1)]; m = sum(r) / n
    return math.sqrt(sum((x - m) ** 2 for x in r) / (n - 1)), c[i]
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    try: return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError: return None
def p_yes(kind, nums, S, sig, tau):
    s = sig * math.sqrt(tau)
    if kind == "between": lo, hi = sorted(nums); return phi(math.log(hi / S) / s) - phi(math.log(lo / S) / s)
    if kind == "less": return phi(math.log(nums[0] / S) / s)
    return 1 - phi(math.log(nums[0] / S) / s)
def lire(q):
    ql = q.lower(); a = next((v for k, v in ASSETS.items() if k in ql), None)
    nums = [float(x.replace(",", "")) for x in re.findall(r"\$([\d,]+(?:\.\d+)?)", q)]
    if not a: return None
    if "between" in ql and len(nums) == 2: return a, "between", nums
    if len(nums) != 1: return None
    if "less than" in ql: return a, "less", nums
    if "greater than" in ql or re.search(r"be above", ql): return a, "greater", nums
    return None
if __name__ == "__main__":
    ms = [json.loads(l) for nom in sys.argv[1].split(",") for l in open(D / nom)]
    seen = set(); ms = [m for m in ms if not (m["id"] in seen or seen.add(m["id"]))]
    snaps = []
    for m in ms:
        pq = lire(m["question"])
        if not pq or not (m["vol"] or 0) >= 5000 or sorted(map(str, m["prices"])) != ["0", "1"]: continue
        p = D / "echanges" / f"{m['id']}.json.gz"
        if not p.exists(): continue
        end = ts(m["end"]); tr = sorted(json.loads(gzip.decompress(p.read_bytes()))["echanges"])
        if end is None or len(tr) < 3: continue
        a, kind, nums = pq
        # TEST (défaut) : 2026 ; HOLDOUT=1 : septembre-décembre 2025 (règle R1 : prix seuls, le profil de volatilité n'entre pas dans les paris)
        if (os.environ.get("HOLDOUT") != "1" and end < DEB2026) or (os.environ.get("HOLDOUT") == "1" and not (DEB2025 <= end < DEB2026)): continue
        yes, no = m["yes"], m["no"]
        ser = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr]; st = [x[0] for x in ser]
        by = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr if (t[1] == yes and t[2] == "BUY") or (t[1] == no and t[2] == "SELL")]
        bn = [(t[0], t[3] if t[1] == no else 1 - t[3]) for t in tr if (t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")]
        bys, bns = [x[0] for x in by], [x[0] for x in bn]
        fs = m["feeSchedule"] if isinstance(m["feeSchedule"], dict) else {}; rate = float(fs.get("rate") or 0) if m["feesEnabled"] else 0.0
        won = 1 if str(m["prices"][0]) == "1" else 0
        for h in (2, 3, 4, 6, 9, 12, 24):
            T = end - h * 3600; i = bisect.bisect_left(st, T) - 1
            if i < 0 or T - st[i] > 3 * 3600: continue
            sig, S = sig_base(a, T)
            if sig is None: continue
            hrs = [dt.datetime.utcfromtimestamp(T + k * 3600).hour for k in range(h)]  # barres à venir, début à chaque heure pleine (T est pleine ou presque)
            var_saison = sum(profil[a][x] for x in hrs)
            pm_flat = p_yes(kind, nums, S, sig, h)
            pm_sais = p_yes(kind, nums, S, sig * math.sqrt(var_saison / h), h)
            jy = bisect.bisect_left(bys, T); jn = bisect.bisect_left(bns, T)
            py = by[jy][1] if jy < len(by) and by[jy][0] <= T + 3600 else None
            pn = bn[jn][1] if jn < len(bn) and bn[jn][0] <= T + 3600 else None
            snaps.append(dict(id=m["id"], ev=m["event_id"], a=a, kind=kind, h=h, pyes=ser[i][1], pf=pm_flat, ps=pm_sais, won=won, py=py, pn=pn, rate=rate,
                              mois=dt.datetime.utcfromtimestamp(T).strftime("%Y-%m"), vs=var_saison / h))
    json.dump(snaps, open(SP / ("snaps_saison_2025.json" if os.environ.get("HOLDOUT") == "1" else "snaps_saison.json"), "w"))
    print(len(snaps), "instants,", len({s['id'] for s in snaps}), "marchés,", len({s['ev'] for s in snaps}), "événements")
    def ls(p, y): p = min(max(p, 1e-3), 1 - 1e-3); return math.log(p if y else 1 - p)
    print("\n== log-score (plus grand = meilleur) : prix, modèle plat, modèle saisonnier ; moyenne par instant, 2026 ==")
    for kind in ("between", "less", "greater", None):
        for h in (2, 3, 4, 6, 9, 12, 24):
            r = [s for s in snaps if s["h"] == h and (kind is None or s["kind"] == kind)]
            if len(r) < 50: continue
            f = lambda k: sum(ls(s[k], s["won"]) for s in r) / len(r)
            print(f"{str(kind):8s} h={h:2d} n={len(r):5d} prix {f('pyes'):+.4f}  plat {f('pf'):+.4f}  saison {f('ps'):+.4f}  | saison − prix {f('ps') - f('pyes'):+.4f}  variance horaire moyenne du créneau ×{sum(s['vs'] for s in r)/len(r):.2f}")
