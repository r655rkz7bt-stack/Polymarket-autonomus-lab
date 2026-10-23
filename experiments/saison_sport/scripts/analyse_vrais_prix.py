"""NON des candidats à 0,10-0,30 aux PRIX RÉELLEMENT PAYÉS (premier achat du NON dans les W heures qui suivent la décision).
Usage : PYTHONPATH=../../src python scripts/analyse_vrais_prix.py"""
import json, collections
from datetime import datetime, timezone
from polymarket_agent.idea_test import verdict, taker_cost, fee
ev = {e["id"]: e for e in json.load(open("donnees/evenements.json"))}
mk = {m["id"]: (m, e) for e in ev.values() for m in e["markets"]}
rows = [json.loads(l) for l in open("donnees/echanges.jsonl")]
print("lignes", len(rows), {h: sum(r["h"] == h for r in rows) for h in (7, 14)})
for W in (1, 3, 6):
    for h in (7, 14, None):
        for lo, hi in ((0.10, 0.20), (0.10, 0.30)):
            b = []
            for r in rows:
                if (h and r["h"] != h) or not lo <= r["p"] < hi: continue
                m, e = mk[r["id"]]
                paid = taker_cost(r["trades"], r["tok_no"], r["tok_yes"], r["t"], window=W * 3600, after=True)
                if paid is None or not 0.5 < paid < 0.99: continue
                c = paid + fee(paid, float(m["fee"] or 0))
                b.append({"gain": ((0.0 if m["yes_won"] else 1.0) - c) / c, "evenement": e["id"], "mois": datetime.fromtimestamp(r["t"], timezone.utc).strftime("%Y-%m"),
                          "cout": paid, "win": not m["yes_won"], "ref": 1 - r["p"]})
            if len(b) < 20: print(W, h, lo, hi, "n =", len(b)); continue
            v = verdict(b)
            print(f"W={W}h H={h or 'tous'} p_oui {lo}-{hi}: n={len(b)} ev={len({x['evenement'] for x in b})} payé {sum(x['cout'] for x in b)/len(b):.3f} (histo {sum(x['ref'] for x in b)/len(b):.3f}) "
                  f"gagnés {sum(x['win'] for x in b)}/{sum(x['cout'] for x in b):.1f} rend {v['rendement_moyen']:+.3f} t_ev {v['confiance_evenements']:+.2f} mois {sum(1 for x in v['mois'].values() if x>0)}/{len(v['mois'])} -> {v['verdict']}")
