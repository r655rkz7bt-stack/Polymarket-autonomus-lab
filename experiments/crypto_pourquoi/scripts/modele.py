"""28/10/2026 (passage du 27/10 soir) : POURQUOI le NON des marchés crypto à 0,10-0,45 gagne-t-il plus que son prix ? Hypothèse : le prix du OUI paie une prime de
volatilité (le marché croit à plus de mouvement que le spot n'en fait). Test : à chaque instant de décision T (fin − h, h = 3/6/12/24 h), probabilité d'un modèle
sans drift (log-normal, volatilité = écart-type des rendements horaires des 168 dernières heures FINIES, barres Binance) comparée au prix du marché et à l'issue.
Marchés : « above / less than $X on <date> » (réglés à 12 h heure de l'Est), « reach / dip to $X on <date> » (touche dans la journée). Aucun regard vers le futur :
seules les barres horaires terminées avant T servent ; prix du marché = dernier échange du OUI avant T (≤ 1 h) ; prix payé = premier échange réel qui achète le côté
dans l'heure suivante ; frais du marché (rate·p·(1−p)). Usage : PYTHONPATH=src python modele.py marches_2026.jsonl[,autres] [VOL_MIN=5000]"""
import bisect, gzip, json, math, os, re, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_crypto_passe/donnees"); SP = Path("experiments/crypto_pourquoi/donnees")
VOL = float(sys.argv[2]) if len(sys.argv) > 2 else 5000
ASSETS = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "xrp": "XRP", "dogecoin": "DOGE", "bnb": "BNB"}
spot = {}
for a in set(ASSETS.values()):
    p = SP / f"spot_{a}.json"
    if p.exists():
        rows = json.load(open(p)); spot[a] = dict(t=[r[0] for r in rows], o=[r[1] for r in rows], h=[r[2] for r in rows], l=[r[3] for r in rows], c=[r[4] for r in rows])
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    try: return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError: return None
def phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def parse(q):
    ql = q.lower()
    a = next((v for k, v in ASSETS.items() if k in ql), None)
    if not a: return None
    nums = [float(x.replace(",", "")) for x in re.findall(r"\$([\d,]+(?:\.\d+)?)", q)]
    if len(nums) != 1: return None
    if re.search(r"price of \w+ be above", ql): kind = "above"
    elif re.search(r"price of \w+ be less than", ql) or re.search(r"price of \w+ be below", ql): kind = "below"
    elif re.search(r"\b(reach|hit)\b", ql) and " on " in ql: kind = "reach"
    elif re.search(r"\bdip to\b", ql) and " on " in ql: kind = "dip"
    else: return None
    return a, kind, nums[0]
def vol_hourly(s, T, n=168):
    i = bisect.bisect_right(s["t"], T - 3600) - 1   # dernière barre FINIE : début ≤ T − 3600
    if i < n + 1: return None, None
    r = [math.log(s["c"][j] / s["c"][j - 1]) for j in range(i - n + 1, i + 1)]
    m = sum(r) / n
    return math.sqrt(sum((x - m) ** 2 for x in r) / (n - 1)), s["c"][i]
def model_p(a, kind, K, T, end, vmult=1.0, n=168):
    s = spot[a]; sig, S = vol_hourly(s, T, n)
    if sig is None: return None
    sig *= vmult; tau = max((end - T) / 3600, 0.25)
    if kind in ("above", "below"):
        p_above = phi(math.log(S / K) / (sig * math.sqrt(tau)))
        return p_above if kind == "above" else 1 - p_above
    # touche : déjà touché dans la fenêtre (depuis end − 24 h) ? barres finies seulement, avec le haut/bas
    w0 = end - 24 * 3600; i0 = bisect.bisect_left(s["t"], w0); i1 = bisect.bisect_right(s["t"], T - 3600)
    if i1 > i0:
        if kind == "reach" and max(s["h"][i0:i1]) >= K: return 1.0
        if kind == "dip" and min(s["l"][i0:i1]) <= K: return 1.0
    if (kind == "reach" and S >= K) or (kind == "dip" and S <= K): return 1.0
    return min(1.0, 2 * (1 - phi(abs(math.log(K / S)) / (sig * math.sqrt(tau)))))
ms = [json.loads(l) for nom in sys.argv[1].split(",") for l in open(D / nom)]
seen = set(); ms = [m for m in ms if not (m["id"] in seen or seen.add(m["id"]))]
ms = [m for m in ms if (m["vol"] or 0) >= VOL and "up or down" not in m["question"].lower() and sorted(map(str, m["prices"])) == ["0", "1"]]
snaps = []
nm = 0
for m in ms:
    pq = parse(m["question"])
    if not pq or pq[0] not in spot: continue
    p = D / "echanges" / f"{m['id']}.json.gz"
    if not p.exists(): continue
    end = ts(m["end"])
    if end is None: continue
    tr = sorted(json.loads(gzip.decompress(p.read_bytes()))["echanges"])
    if len(tr) < 5: continue
    nm += 1
    yes, no = m["yes"], m["no"]
    ser = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr]; st = [x[0] for x in ser]
    buy_no = [(t[0], t[3] if t[1] == no else 1 - t[3]) for t in tr if (t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")]
    bt = [b[0] for b in buy_no]
    buy_yes = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr if (t[1] == yes and t[2] == "BUY") or (t[1] == no and t[2] == "SELL")]
    bty = [b[0] for b in buy_yes]
    fs = m["feeSchedule"] if isinstance(m["feeSchedule"], dict) else {}
    rate = float(fs.get("rate") or 0) if m["feesEnabled"] else 0.0
    won_yes = 1 if str(m["prices"][0]) == "1" else 0
    a, kind, K = pq
    # heure de règlement : above/below à 12 h ET = `end` ; touche : end = minuit ET du lendemain
    for h in (3, 6, 12, 24):
        T = end - h * 3600
        i = bisect.bisect_left(st, T) - 1
        if i < 0 or T - st[i] > 3600: continue
        pyes = ser[i][1]
        j = bisect.bisect_left(bt, T)
        paid = buy_no[j][1] if j < len(bt) and bt[j] <= T + 3600 else None
        jy = bisect.bisect_left(bty, T)
        paid_yes = buy_yes[jy][1] if jy < len(bty) and bty[jy] <= T + 3600 else None
        pm = {v: model_p(a, kind, K, T, end, vmult=v) for v in (0.8, 1.0, 1.25)}
        if pm[1.0] is None: continue
        snaps.append(dict(id=m["id"], ev=m["event_id"], a=a, kind=kind, K=K, h=h, T=T, pyes=pyes, pm=pm, paid=paid, paid_yes=paid_yes, rate=rate, won=won_yes,
                          mois=dt.datetime.utcfromtimestamp(T).strftime("%Y-%m"), q=m["question"]))
print(f"{len(ms)} marchés réglés, {nm} lus, {len(snaps)} instants de décision")
json.dump(snaps, open(SP / "snaps.json", "w"))
