"""28/10/2026 : contrôle du règlement (protocole B.3) des échelles « <actif> price on <date> » : la tranche que Gamma dit gagnante contient-elle le cours Binance de 12 h (Est) lu indépendamment
(barre horaire dont le DÉBUT est l'heure du fix : son ouverture = le cours à 12 h 00) ? Compte les événements dont la tranche gagnante est cohérente, et les écarts (cours à moins de 0,05 % d'une borne = tolérance : la source
de règlement est la clôture de la bougie d'une minute, la barre horaire donne l'ouverture de l'heure). Usage : PYTHONPATH=src python controle_reglement.py marches_a.jsonl,marches_d.jsonl"""
import bisect, json, re, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
D = Path("experiments/contrer_crypto_passe/donnees"); SP = Path("experiments/crypto_pourquoi/donnees")
ASSETS = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "xrp": "XRP"}
spot = {}
for a in set(ASSETS.values()):
    rows = json.load(open(SP / f"spot_{a}.json")); spot[a] = ([r[0] for r in rows], [r[1] for r in rows])
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
ev = defaultdict(list)
for nom in sys.argv[1].split(","):
    for l in open(D / nom):
        m = json.loads(l)
        if "price of" in (m["question"] or "").lower() and sorted(map(str, m["prices"])) == ["0", "1"]: ev[m["event_id"]].append(m)
ok = bad = skipped = 0; details = []
for e, v in ev.items():
    win = [m for m in v if str(m["prices"][0]) == "1"]
    if len(win) != 1 or len(v) < 8: skipped += 1; continue
    m = win[0]; q = m["question"]; ql = q.lower()
    a = next((x for k, x in ASSETS.items() if k in ql), None)
    nums = [float(x.replace(",", "")) for x in re.findall(r"\$([\d,]+(?:\.\d+)?)", q)]
    end = ts(m["end"])
    t, o = spot[a]; i = bisect.bisect_left(t, end)
    if i >= len(t) or t[i] != end: skipped += 1; continue
    p = o[i]
    lo, hi = (sorted(nums) if "between" in ql else (0, nums[0]) if "less than" in ql else (nums[0], 1e18))
    tol = 0.0005 * p
    if lo - tol <= p <= hi + tol: ok += 1
    else: bad += 1; details.append((e, q[-60:], round(p, 4), lo, hi))
print(f"{len(ev)} événements ; {ok} cohérents avec la barre Binance de l'heure du fix (tolérance 0,05 %), {bad} écarts, {skipped} non évalués (tranche gagnante unique absente, < 8 marchés, ou heure hors barres)")
for d in details[:12]: print(d)
