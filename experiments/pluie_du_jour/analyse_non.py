"""Piste n° 69, côté NON : à `AVANT` heures de la fin du jour climatique (négatif = après la fin), aucun METAR du jour n'a mesuré
≥ 0,01 pouce (trace permise). Achat = premier vrai échange « No / BUY » après cet instant (+10 min), avant le règlement.
Usage : python analyse_non.py AVANT_H [SEUIL_PRIX_MAX]"""
import bisect
import json
import sys
from collections import defaultdict
from datetime import timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from analyse import D, DECALAGE, jour, metar  # noqa: E402
from polymarket_agent.idea_test import verdict  # noqa: E402

AVANT = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
PMAX = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
DANS_H = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0   # achat au plus DANS_H heures après la décision
ms = [m for m in json.load(open(D / "marches.json")) if m["station"] and m["closed"] and m["prix_final"] in (["1", "0"], ["0", "1"])]
tr = defaultdict(list)
for l in open(D / "echanges.jsonl"):
    t = json.loads(l)
    tr[t["cond"]].append(t)
for v in tr.values():
    v.sort(key=lambda t: t["ts"])
met = {st: metar(st) for st in DECALAGE}
paris = []
for m in ms:
    st, j = m["station"], jour(m["titre"])
    non = m["prix_final"][1] == "1"
    debut = j.replace(tzinfo=timezone.utc) - timedelta(hours=DECALAGE[st])
    fin = debut + timedelta(hours=24)
    t_dec = fin - timedelta(hours=AVANT) + timedelta(minutes=10)
    obs = [x for t, x in met[st] if debut <= t < t_dec - timedelta(minutes=10)]
    if not obs or max(obs) >= 0.01:
        continue
    lst = tr.get(m["condition"], [])
    i = bisect.bisect_left([t["ts"] for t in lst], t_dec.timestamp())
    achat = next((t for t in lst[i:] if t["outcome"] == "No" and t["side"] == "BUY" and t["ts"] <= t_dec.timestamp() + 3600 * DANS_H), None)
    if achat is None or achat["price"] > PMAX:
        continue
    px = achat["price"]
    prof = sum(t["size"] for t in lst[i:] if t["outcome"] == "No" and t["side"] == "BUY" and t["price"] <= px + 0.02
               and achat["ts"] <= t["ts"] <= achat["ts"] + 3600)
    frais = 0.05 * px * (1 - px) if m["feeType"] == "weather_fees" else 0.0
    paris.append({"gain": ((1.0 if non else 0.0) - px - frais) / px, "evenement": m["event"], "mois": j.strftime("%Y-%m"),
                  "cout": px, "non": non, "prof": prof, "st": st, "date": j.strftime("%m-%d")})
for nom, f in [("tous", lambda b: True), ("< 0,97", lambda b: b["cout"] < 0.97), ("< 0,90", lambda b: b["cout"] < 0.90),
               ("≥ 20 parts", lambda b: b["prof"] >= 20), ("< 0,97 et ≥ 20 parts", lambda b: b["cout"] < 0.97 and b["prof"] >= 20)]:
    bs = [b for b in paris if f(b)]
    if bs:
        v = verdict(bs, min_bets=10)
        print(f"AVANT {AVANT:+.0f} h {nom:22s} n={len(bs):4d} gagnés {sum(b['non'] for b in bs)} pour {sum(b['cout'] for b in bs):.1f}, "
              f"rendement {100*sum(b['gain'] for b in bs)/len(bs):+.2f} %, verdict {v['verdict']}")
for lo, hi in [(0, 0.5), (0.5, 0.8), (0.8, 0.9), (0.9, 0.97), (0.97, 1.01)]:
    bs = [b for b in paris if lo <= b["cout"] < hi and b["prof"] >= 20]
    if bs:
        v = verdict(bs, min_bets=5)
        print(f"   prix {lo:.2f}-{hi:.2f} (≥ 20 parts) n={len(bs)} gagnés {sum(b['non'] for b in bs)} pour {sum(b['cout'] for b in bs):.1f} "
              f"rendement {100*sum(b['gain'] for b in bs)/len(bs):+.1f} % evts {len(set(b['evenement'] for b in bs))} {v['verdict']} "
              f"t_ev {v.get('t_evenement')} z {v.get('z_prix')} mois {v.get('mois')}")
json.dump(paris, open(D / f"paris_non_{AVANT:+.0f}.json", "w"))
for b in [b for b in paris if not b["non"]][:10]:
    print("   PERDU", b["st"], b["date"], b["cout"], round(b["prof"]))
