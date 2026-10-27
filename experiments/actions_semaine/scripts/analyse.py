"""28/10/2026 : « Will <action> finish week of <date> above $X? » (clôture du vendredi à 16 h Est, 20 h UTC), 491 événements réglés (public-search « finish week of »), 1 186 marchés à plus de 2 000 $ de volume.
Question : le OUI cher (0,55-0,97) ou bon marché (0,02-0,25) est-il bien calibré 4 h à 5 jours avant la clôture ? Un pari par marché (le plus ancien des instants listés où le côté, payé dans la bande, est acheté dans l'heure) ;
vrais échanges (data-api), frais du marché, paris liés par événement (une action une semaine), jugement idea_test.verdict ; par mois et par moitié. Usage : PYTHONPATH=src python analyse.py"""
import bisect, gzip, json, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_crypto_passe/donnees")
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    try: return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError: return None
data = []
for l in open(D / "marches_h.jsonl"):
    m = json.loads(l); p = D / "echanges" / f"{m['id']}.json.gz"
    if not p.exists(): continue
    end = ts(m["end"]); tr = sorted(json.loads(gzip.decompress(p.read_bytes()))["echanges"])
    if end is None or len(tr) < 5: continue
    yes, no = m["yes"], m["no"]
    ser = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr]
    by = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr if (t[1] == yes and t[2] == "BUY") or (t[1] == no and t[2] == "SELL")]
    bn = [(t[0], t[3] if t[1] == no else 1 - t[3]) for t in tr if (t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")]
    fs = m["feeSchedule"] if isinstance(m["feeSchedule"], dict) else {}
    data.append(dict(m=m, end=end, ser=ser, st=[x[0] for x in ser], by=by, bys=[x[0] for x in by], bn=bn, bns=[x[0] for x in bn],
                     won=1 if str(m["prices"][0]) == "1" else 0, rate=float(fs.get("rate") or 0) if m["feesEnabled"] else 0.0))
print(len(data), "marchés avec échanges,", len({d['m']['event_id'] for d in data}), "événements")
def bets(side, lo, hi, heures, wait=3600):
    par = {}
    for d in data:
        for h in heures:
            T = d["end"] - h * 3600; i = bisect.bisect_left(d["st"], T) - 1
            if i < 0 or T - d["st"][i] > 6 * 3600: continue
            pyes = d["ser"][i][1]; pside = pyes if side == "oui" else 1 - pyes
            if not lo <= pside <= hi: continue
            arr, tt = (d["by"], d["bys"]) if side == "oui" else (d["bn"], d["bns"])
            j = bisect.bisect_left(tt, T)
            if j >= len(tt) or tt[j] > T + wait: continue
            paid = arr[j][1]
            if not lo <= paid <= hi + 0.03 or paid <= 0: continue
            if d["m"]["id"] not in par or h > par[d["m"]["id"]][0]:
                won = d["won"] if side == "oui" else 1 - d["won"]
                par[d["m"]["id"]] = (h, dict(gain=(won - paid - it.fee(paid, d["rate"])) / paid, cout=paid, evenement=d["m"]["event_id"], mois=dt.datetime.utcfromtimestamp(T).strftime("%Y-%m"), gagne=won))
    return [v[1] for v in par.values()]
def show(label, b):
    if len(b) < 20: print(f"| {label} | {len(b)} |"); return
    v = it.verdict(b); g = sum(x["gagne"] for x in b); a = sum(x["cout"] for x in b)
    print(f"| {label} | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t évén. {v['confiance_evenements']:+.2f} | {g} / {a:.1f} (z {v['z_prix']:+.2f}) | {v['mois_gagnants']} mois | {v['verdict']} |")
print("| réglage | paris | évén. | rendement | t | gagnés/attendus | mois | verdict |")
for side in ("oui", "non"):
    for lo, hi in ((0.02, 0.10), (0.10, 0.25), (0.25, 0.45), (0.45, 0.70), (0.70, 0.97)):
        for h in (4, 24, 48, 96, 144):
            show(f"{side.upper()} payé {lo}-{hi} H−{h}", bets(side, lo, hi, (h,)))
