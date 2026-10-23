"""Piste n° 6 (ufc_coherence) : somme des méthodes de victoire d'un combat UFC et accord entre marchés, aux prix des
vrais échanges. Pour chaque combat et chaque heure de J-3 au coup d'envoi, achat simultané (échanges dans les W minutes qui
suivent) de jambes qui paient ensemble un montant connu :
  A  OUI(KO du combat) + OUI(soumission) + OUI(aller à la distance)   paie 1  (KO + soumission + distance = 1, hors disqualification)
  B  NON des trois mêmes marchés                                      paie 2
  C  OUI(KO du combat) + NON(KO A) + NON(KO B)                        paie 2  (KO du combat = KO A + KO B)
  D  NON(KO du combat) + OUI(KO A) + OUI(KO B)                        paie 1
Gain = paiement − prix payés − frais (barème Gamma, 0,05·p·(1−p) par jambe). Usage : PYTHONPATH=../../src python coherence.py [W minutes]"""
import bisect, collections, json, math, statistics as st, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from polymarket_agent import idea_test
from polymarket_agent.http_client import HttpClient

D = Path("donnees")
W = float(sys.argv[1]) * 60 if len(sys.argv) > 1 else 1800
http = HttpClient()
combats = [c for c in json.load(open(D / "combats.json")) if c["fin"] and c["fin"] >= "2025-06"]


class Jeton:
    def __init__(self, tok, other, trades):
        pts = sorted((t[0], t[3] if t[1] == tok else 1 - t[3]) for t in trades
                     if (t[1] == tok and t[2] == "BUY") or (t[1] == other and t[2] == "SELL"))
        self.t, self.p = [a for a, _ in pts], [b for _, b in pts]

    def apres(self, ts, window):
        i = bisect.bisect_left(self.t, ts)
        return self.p[i] if i < len(self.t) and self.t[i] - ts <= window else None


def nom(q):
    q = q.lower()
    if "won by ko or tko" in q and q.startswith("will the fight"): return "K"
    if "won by submission" in q and q.startswith("will the fight"): return "S"
    if "win by ko or tko" in q: return "KO_" + q
    return None


res = collections.defaultdict(list)
n_combats = 0
for c in combats:
    ms = [m for m in c["marches"] if m["type"] in ("ufc_method_of_victory", "ufc_go_the_distance", "moneyline")]
    K = next((m for m in ms if m["type"] == "ufc_method_of_victory" and nom(m["q"]) == "K"), None)
    S = next((m for m in ms if m["type"] == "ufc_method_of_victory" and nom(m["q"]) == "S"), None)
    G = next((m for m in ms if m["type"] == "ufc_go_the_distance"), None)
    ko = [m for m in ms if m["type"] == "ufc_method_of_victory" and (nom(m["q"]) or "").startswith("KO_")]
    ml = next((m for m in ms if m["type"] == "moneyline"), None)
    if not (K and S and G and len(ko) == 2 and ml and ml.get("debut")):
        continue
    start = datetime.fromisoformat(ml["debut"].replace("+00", "+00:00"))
    if start > datetime.now(timezone.utc) or start < datetime(2025, 6, 1, tzinfo=timezone.utc):
        continue
    trades = idea_test.fetch_event_trades(http, D / "cache", str(c["id"]))
    by = collections.defaultdict(list)
    for t in trades: by[t[1]].append(t)
    J = {}
    for key, m in (("K", K), ("S", S), ("G", G), ("A", ko[0]), ("B", ko[1])):
        both = by[m["yes"]] + by[m["no"]]
        J[key] = (Jeton(m["yes"], m["no"], both), Jeton(m["no"], m["yes"], both), m)
    outcome = {k: json.loads(v[2]["final"] or "[0,0]")[0] in ("1", 1) for k, v in J.items()}
    if any(json.loads(v[2]["final"] or "[0,0]")[0] not in ("1", "0", 1, 0) for v in J.values()):
        continue
    taux = float((K.get("frais") or {}).get("rate", 0.05) or 0.05)
    n_combats += 1
    for h in range(72, 0, -1):
        ts = int((start - timedelta(hours=h)).timestamp())
        py = {k: J[k][0].apres(ts, W) for k in J}
        pn = {k: J[k][1].apres(ts, W) for k in J}
        def fee(p): return taux * p * (1 - p)
        def trio(prices, payoff_fn, label):
            if any(p is None or not (0.01 <= p <= 0.99) for p in prices.values()):
                return
            cost = sum(prices.values()) + sum(fee(p) for p in prices.values())
            res[label].append(dict(combat=c["slug"], h=h, gain=payoff_fn() - cost, cost=cost))
        yes = lambda ks: {k: py[k] for k in ks}
        no = lambda ks: {k: pn[k] for k in ks}
        # paiements RÉELS (pas supposés) : somme des jambes gagnantes
        trio(yes("KSG"), lambda: sum(outcome[k] for k in "KSG"), "A OUI K+S+G")
        trio(no("KSG"), lambda: sum(not outcome[k] for k in "KSG"), "B NON K,S,G")
        trio({"K": py["K"], "A": pn["A"], "B": pn["B"]}, lambda: outcome["K"] + (not outcome["A"]) + (not outcome["B"]), "C OUI K, NON KO_A, NON KO_B")
        trio({"K": pn["K"], "A": py["A"], "B": py["B"]}, lambda: (not outcome["K"]) + outcome["A"] + outcome["B"], "D NON K, OUI KO_A, OUI KO_B")
print(f"{n_combats} combats complets, fenêtre d'exécution {W / 60:.0f} min")
for label, rows in sorted(res.items()):
    g = [r["gain"] for r in rows]
    pos = [r for r in rows if r["gain"] > 0]
    pos1 = [r for r in rows if r["gain"] > 0.02]
    # un seul achat par combat : le meilleur instant (regard vers le futur : borne haute irréaliste), le premier instant gagnant
    first = {}
    for r in rows:
        if r["gain"] > 0 and r["combat"] not in first: first[r["combat"]] = r
    print(f"{label:30} {len(rows):6} instants | gain moyen {st.mean(g):+.4f} | gain > 0 : {len(pos)} ({len(first)} combats) | > 0,02 : {len(pos1)} | "
          f"premier instant gagnant : moyenne {st.mean([r['gain'] / r['cost'] for r in first.values()]) if first else float('nan'):+.3f} par euro")
