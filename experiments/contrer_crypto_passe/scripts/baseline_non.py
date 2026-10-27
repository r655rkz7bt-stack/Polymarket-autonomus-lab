"""27/10/2026, piste 0c : « contrer un mouvement de plus de 0,05 en 6 h » sur les marchés crypto réglés, règle en direct rejouée sur le passé.
Usage : PYTHONPATH=src python analyse.py [VOL_MIN=5000]. À chaque instant T (pas de 30 min), seulement avec les échanges d'horodatage < T (aucun regard vers le futur) :
- prix = dernier échange du OUI avant T (≤ 1 h avant), prix 6 h avant = dernier échange avant T − 6 h (≤ 3 h avant) ; mouvement = prix − prix 6 h avant ;
- contrer : si |mouvement| ≥ MIN_MOVE on achète l'autre côté si son prix est dans [LO, HI] et s'il reste ≥ 2 h avant la fin ; un seul pari par marché (position gardée) ;
- prix payé = premier échange réel qui achète ce côté dans l'heure après T (comme `idea_test.taker_cost(after=True)`), frais du marché (rate·p·(1−p)) ;
- gain par euro = (gagné − coût − frais) / (coût + frais)... ici (gagné − coût − frais)/coût comme `idea_test.verdict`. Paris liés : un événement = une échelle de seuils (même date)."""
import bisect, gzip, json, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_crypto_passe/donnees")
VOL = float(sys.argv[1]) if len(sys.argv) > 1 else 5000
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    try: return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
    except ValueError: return None
import os
ms = [json.loads(l) for nom in os.environ.get("MARCHES", "marches.jsonl").split(",") for l in open(D / nom)]  # plusieurs fichiers possibles (28/10 : 2024, 2025, 2026)
seen = set(); ms = [m for m in ms if not (m["id"] in seen or seen.add(m["id"]))]
ms = [m for m in ms if (m["vol"] or 0) >= VOL and "up or down" not in m["question"].lower() and sorted(map(str, m["prices"])) == ["0", "1"]]
data = []
for m in ms:
    p = D / "echanges" / f"{m['id']}.json.gz"
    if not p.exists(): continue
    j = json.loads(gzip.decompress(p.read_bytes()))
    tr = sorted(j["echanges"])
    if len(tr) < 5: continue
    yes, no = m["yes"], m["no"]
    series = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr]
    buy_yes = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr if (t[1] == yes and t[2] == "BUY") or (t[1] == no and t[2] == "SELL")]
    buy_no = [(t[0], t[3] if t[1] == no else 1 - t[3]) for t in tr if (t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")]
    fs = m["feeSchedule"] if isinstance(m["feeSchedule"], dict) else {}
    data.append(dict(m=m, ser=series, st=[s[0] for s in series], buy={0: buy_yes, 1: buy_no}, bt={0: [b[0] for b in buy_yes], 1: [b[0] for b in buy_no]},
                     won_yes=1 if str(m["prices"][0]) == "1" else 0, rate=float(fs.get("rate") or 0) if m["feesEnabled"] else 0.0,
                     start=ts(m["start"]), end=ts(m["end"]), complet=j["complet"]))
print(f"{len(ms)} marchés réglés, {len(data)} avec échanges", flush=True)
def last_before(d, t, maxage):
    i = bisect.bisect_left(d["st"], t) - 1
    if i < 0 or t - d["st"][i] > maxage: return None
    return d["ser"][i][1]
def kind(q):
    q = q.lower()
    return "hit" if any(w in q for w in ("hit", "reach", "dip", "touch")) else "above"
def bets_for(lo, hi, move, hours_min=2, horizon_max=None, step=1800, wait=3600, direction=-1, base_side=None):
    out = []
    for d in data:
        m = d["m"]; end = d["end"]
        if end is None or not d["start"]: continue
        t = d["start"] + 6 * 3600
        t_last = end - hours_min * 3600
        # le premier échange donne le début utile
        t = max(t, d["st"][0] + 6 * 3600)
        while t <= t_last:
            now = last_before(d, t, 3600)
            ago = last_before(d, t - 6 * 3600, 3 * 3600) if now is not None else None
            if now is not None and ago is not None and (base_side is not None or abs(now - ago) >= move - 1e-9) and (horizon_max is None or end - t <= horizon_max * 3600):
                side = base_side if base_side is not None else (1 if now - ago > 0 else 0) if direction < 0 else (0 if now - ago > 0 else 1)  # contrer : hausse du OUI -> NON ; suivre : l'inverse ; base : un côté fixe, sans signal
                price = (1 - now) if side == 1 else now
                if lo <= price <= hi:
                    bt = d["bt"][side]; i = bisect.bisect_left(bt, t)
                    if i < len(bt) and bt[i] <= t + wait:
                        paid = d["buy"][side][i][1]
                        if lo <= paid <= hi + 0.03 and paid > 0:
                            won = (d["won_yes"] == 0) if side == 1 else (d["won_yes"] == 1)
                            fee = it.fee(paid, d["rate"])
                            out.append(dict(gain=(int(won) - paid - fee) / paid, cout=paid, evenement=m["event_id"], mois=dt.datetime.utcfromtimestamp(t).strftime("%Y-%m"),
                                            kind=kind(m["question"]), side=side, titre=m["event_title"], h=(end - t) / 3600, t=t, gagne=int(won)))
                    break   # un pari par marché, pris ou pas (le prix servi est hors plage)
            t += step
    return out
def show(label, bets):
    if not bets: print(f"| {label} | 0 | | | | | |"); return
    v = it.verdict(bets)
    g = sum(b["gagne"] for b in bets); a = sum(b["cout"] for b in bets)
    print(f"| {label} | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t paris {v['confiance_paris']:+.2f} / évén. {v['confiance_evenements']:+.2f} | gagnés {g} / attendus {a:.1f} (z {v['z_prix']:+.2f}) | {v['mois_gagnants']} mois | {v['verdict']} |", flush=True)
    return v
# Référence « NON bon marché » sans signal (27/10/2026) : robustesse par genre, mois, délai, actif, événement.
print("| réglage | paris | évén. | rendement | t | gagnés | mois | verdict |\n|---|---|---|---|---|---|---|---|")
import re
for lo, hi in ((0.10, 0.45), (0.05, 0.10), (0.45, 0.90)):
    b = bets_for(lo, hi, 0, base_side=1)
    show(f"NON {lo}-{hi} tous", b)
    if (lo, hi) == (0.10, 0.45): base = b
for k in ("above", "hit"): show(f"NON 0,10-0,45 genre {k}", [b for b in base if b["kind"] == k])
def asset(t):
    t = t.lower()
    return next((a for a in ("bitcoin", "ethereum", "solana", "xrp") if a in t), "autre")
for a in ("bitcoin", "ethereum", "solana", "xrp", "autre"): show(f"NON 0,10-0,45 actif {a}", [b for b in base if asset(b["titre"]) == a])
for lo, hi in ((0, 6), (6, 24), (24, 96), (96, 9999)): show(f"NON 0,10-0,45 heures avant fin {lo}-{hi}", [b for b in base if lo <= b["h"] < hi])
for mo in sorted({b["mois"] for b in base}): show(f"NON 0,10-0,45 mois {mo}", [b for b in base if b["mois"] == mo])
for lo, hi in ((0.10, 0.20), (0.20, 0.30), (0.30, 0.45)): show(f"NON prix payé {lo}-{hi}", [b for b in base if lo <= b["cout"] < hi])
# sans les 3 plus gros jours (par jour de décision)
import datetime as dt2
by_day = defaultdict(list)
for b in base: by_day[dt2.datetime.utcfromtimestamp(b["t"]).strftime("%Y-%m-%d")].append(b)
top = sorted(by_day, key=lambda d: -sum(x["gain"] for x in by_day[d]))[:5]
show("NON 0,10-0,45 sans ses 5 meilleurs jours", [b for d, v in by_day.items() if d not in top for b in v])
