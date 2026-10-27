"""28/10/2026 : rejeu de la règle de la STRATÉGIE `tranche_centrale_non` telle que le cycle la joue : toutes les 30 minutes entre fin − 6,5 h et fin − 2 h, sur chaque tranche « between » dont le NON
(dernier échange avant T, ≤ 1 h) coûte 0,03-0,45 : achat au premier échange réel qui achète le NON dans l'heure ; un seul pari par marché (le premier instant qui convient). Frais payés.
Usage : PYTHONPATH=src python rejeu_regle.py marches_a.jsonl,marches_e.jsonl [2026]   ou   marches_g.jsonl 2025"""
import bisect, gzip, json, re, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_crypto_passe/donnees")
AN = sys.argv[2] if len(sys.argv) > 2 else "2026"
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    try: return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError: return None
ms = [json.loads(l) for nom in sys.argv[1].split(",") for l in open(D / nom)]
seen = set(); ms = [m for m in ms if not (m["id"] in seen or seen.add(m["id"]))]
B = re.compile(r"price of (bitcoin|ethereum|solana|xrp) be between", re.I)
def rejeu(lo=0.03, hi=0.45, h_min=2.0, h_max=6.5, pas=1800, wait=3600):
    out = []
    for m in ms:
        if not B.search(m["question"] or "") or not (m["vol"] or 0) >= 5000 or sorted(map(str, m["prices"])) != ["0", "1"]: continue
        end = ts(m["end"])
        if end is None or dt.datetime.utcfromtimestamp(end).strftime("%Y") != AN: continue
        p = D / "echanges" / f"{m['id']}.json.gz"
        if not p.exists(): continue
        tr = sorted(json.loads(gzip.decompress(p.read_bytes()))["echanges"])
        if len(tr) < 3: continue
        yes, no = m["yes"], m["no"]
        ser = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr]; st = [x[0] for x in ser]
        bn = [(t[0], t[3] if t[1] == no else 1 - t[3]) for t in tr if (t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")]; bns = [x[0] for x in bn]
        fs = m["feeSchedule"] if isinstance(m["feeSchedule"], dict) else {}; rate = float(fs.get("rate") or 0) if m["feesEnabled"] else 0.0
        won_yes = 1 if str(m["prices"][0]) == "1" else 0
        t = end - int(h_max * 3600)
        while t <= end - int(h_min * 3600):
            i = bisect.bisect_left(st, t) - 1
            if i >= 0 and t - st[i] <= 3600:
                pn = 1 - ser[i][1]
                if lo <= pn <= hi:
                    j = bisect.bisect_left(bns, t)
                    if j < len(bn) and bns[j] <= t + wait:
                        paid = bn[j][1]
                        if lo <= paid <= hi + 0.03:
                            out.append(dict(gain=((1 - won_yes) - paid - rate * paid * (1 - paid)) / paid, cout=paid, evenement=m["event_id"], mois=dt.datetime.utcfromtimestamp(t).strftime("%Y-%m"),
                                            gagne=1 - won_yes, h=(end - t) / 3600))
                    break
            t += pas
    return out
def show(label, b):
    if len(b) < 15: print(f"| {label} | {len(b)} |"); return
    v = it.verdict(b); g = sum(x["gagne"] for x in b); a = sum(x["cout"] for x in b)
    print(f"| {label} | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t évén. {v['confiance_evenements']:+.2f} | {g:g} / {a:.1f} (z {v['z_prix']:+.2f}) | {v['mois_gagnants']} mois | {v['verdict']} |")
print(f"année {AN}\n| réglage | paris | évén. | rendement | t | gagnés/attendus | mois | verdict |")
for nom, kw in (("règle du cycle : 2 à 6,5 h, NON 0,03-0,45", {}), ("2 à 4 h", dict(h_max=4)), ("4 à 6,5 h", dict(h_min=4)), ("2 à 6,5 h, NON 0,10-0,25", dict(lo=0.10, hi=0.25)),
                ("1,5 à 8 h", dict(h_min=1.5, h_max=8)), ("2 à 6,5 h, NON 0,03-0,60", dict(hi=0.60))):
    b = rejeu(**kw); show(nom, b)
    if not kw:
        for mo in sorted({x["mois"] for x in b}): show(f"  mois {mo}", [x for x in b if x["mois"] == mo])
        for lo2, hi2 in ((2, 3.5), (3.5, 5), (5, 6.6)): show(f"  entrée à {lo2}-{hi2} h de la fin", [x for x in b if lo2 <= x["h"] < hi2])
