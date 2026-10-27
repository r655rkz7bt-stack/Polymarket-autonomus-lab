"""28/10/2026 : « <jeton> FDV above $X one day after launch ? » (marchés réglés, relevé contrer_crypto_passe/marches_c.jsonl, vrais échanges data-api). Le prix du OUI est-il
bien calibré à D−1, D−3, D−7, D−14, D−30 avant le RÈGLEMENT (closedTime) ? Un pari par marché, côté acheté au premier échange réel qui l'achète dans les 12 h après l'instant T ;
prix du OUI à T = dernier échange avant T, pas plus vieux que 24 h ; frais du marché ; paris liés par événement (un jeton = une échelle). Usage : PYTHONPATH=src python analyse.py"""
import bisect, gzip, json, statistics, datetime as dt, collections
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_crypto_passe/donnees")
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    try: return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError: return None
ms = [json.loads(l) for l in open(D / "marches_c.jsonl")]
data = []
for m in ms:
    p = D / "echanges" / f"{m['id']}.json.gz"
    if not p.exists(): continue
    tr = sorted(json.loads(gzip.decompress(p.read_bytes()))["echanges"])
    if len(tr) < 5: continue
    yes, no = m["yes"], m["no"]
    ser = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr]
    by = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr if (t[1] == yes and t[2] == "BUY") or (t[1] == no and t[2] == "SELL")]
    bn = [(t[0], t[3] if t[1] == no else 1 - t[3]) for t in tr if (t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")]
    fs = m["feeSchedule"] if isinstance(m["feeSchedule"], dict) else {}
    data.append(dict(m=m, ser=ser, st=[x[0] for x in ser], by=by, bys=[x[0] for x in by], bn=bn, bns=[x[0] for x in bn],
                     won=1 if str(m["prices"][0]) == "1" else 0, rate=float(fs.get("rate") or 0) if m["feesEnabled"] else 0.0, close=ts(m["closed"])))
print(len(data), "marchés avec échanges,", len({d['m']['event_id'] for d in data}), "événements")
def bets(side, lo, hi, days, wait=12 * 3600):
    out = []
    for d in data:
        c = d["close"]
        if not c: continue
        T = c - days * 86400
        i = bisect.bisect_left(d["st"], T) - 1
        if i < 0 or T - d["st"][i] > 86400: continue
        pyes = d["ser"][i][1]; pside = pyes if side == "oui" else 1 - pyes
        if not lo <= pside <= hi: continue
        arr, tt = (d["by"], d["bys"]) if side == "oui" else (d["bn"], d["bns"])
        j = bisect.bisect_left(tt, T)
        if j >= len(tt) or tt[j] > T + wait: continue
        paid = arr[j][1]
        if not lo <= paid <= hi + 0.03 or paid <= 0: continue
        won = d["won"] if side == "oui" else 1 - d["won"]
        out.append(dict(gain=(won - paid - it.fee(paid, d["rate"])) / paid, cout=paid, evenement=d["m"]["event_id"], mois=dt.datetime.utcfromtimestamp(T).strftime("%Y-%m"), gagne=won, p=pside))
    return out
def show(label, b):
    if len(b) < 10: print(f"| {label} | {len(b)} |"); return
    v = it.verdict(b); g = sum(x["gagne"] for x in b); a = sum(x["cout"] for x in b)
    print(f"| {label} | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t évén. {v['confiance_evenements']:+.2f} | gagnés {g} / attendus {a:.1f} (z {v['z_prix']:+.2f}) | {v['mois_gagnants']} mois | {v['verdict']} |")
print("| réglage | paris | évén. | rendement | t | gagnés/attendus | mois | verdict |")
for side in ("oui", "non"):
    for lo, hi in ((0.02, 0.10), (0.10, 0.25), (0.25, 0.45), (0.45, 0.70), (0.70, 0.95)):
        for days in (1, 3, 7, 14, 30):
            show(f"{side.upper()} payé {lo}-{hi} à D−{days}", bets(side, lo, hi, days))

# --- Suite : les dernières heures avant le règlement (le jeton est déjà coté : le FDV est observable) ---
import sys
if len(sys.argv) > 1 and sys.argv[1] == "heures":
    print("\n== dernières heures avant le règlement ==\n| réglage | paris | évén. | rendement | t | gagnés/attendus | mois | verdict |")
    for side in ("oui", "non"):
        for lo, hi in ((0.60, 0.80), (0.80, 0.90), (0.90, 0.97), (0.70, 0.95)):
            for hh in (30, 24, 18, 12, 6, 3, 1):
                show(f"{side.upper()} payé {lo}-{hi} à H−{hh}", bets(side, lo, hi, hh / 24))
