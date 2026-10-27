"""27/10/2026, piste « totaux de kills du LoL » : extrait de `experiments/bo3_coherence/donnees/evenements_lol.json.gz`
(`python experiments/bo3_coherence/releve_evenements.py lol`, /events/keyset) les marchés `kill_over_under_game`
(« Total Kills Over/Under 30.5 in Game 1? ») réglés net (Over ou Under = 1) ou à 50-50 (partie annulée / égalité sur la ligne).
-> experiments/lol_kills/donnees/marches.jsonl : id, cond, event, titre, jeu (n° de la partie), ligne, coup d'envoi, jetons, résultat, volume."""
import gzip, json, re
from pathlib import Path
R = Path("experiments")
ev = json.loads(gzip.decompress((R / "bo3_coherence/donnees/evenements_lol.json.gz").read_bytes()))
J = lambda x: json.loads(x) if isinstance(x, str) else x
out = []
for e in ev:
    for m in e["markets"]:
        if m.get("sportsMarketType") != "kill_over_under_game":
            continue
        op, oc, tk = J(m.get("outcomePrices")), J(m.get("outcomes")), J(m.get("clobTokenIds"))
        if not op or not oc or not tk or oc != ["Over", "Under"]:
            continue
        op = [float(x) for x in op]
        if sorted(op) == [0.0, 1.0]:
            res = "Over" if op[0] == 1 else "Under"
        elif op == [0.5, 0.5]:
            res = "50-50"
        else:
            continue
        g = re.search(r"in Game (\d)", m["question"])
        out.append({"id": m["id"], "cond": m["conditionId"], "event": e["id"], "titre": e["title"], "jeu": int(g.group(1)) if g else None,
                    "ligne": float(m["line"]), "debut": m.get("gameStartTime"), "over": tk[0], "under": tk[1], "res": res,
                    "vol": float(m.get("volumeNum") or 0), "ferme": m.get("closedTime"), "taux": float((J(m.get("feeSchedule")) or {}).get("rate") or 0) if m.get("feesEnabled") else 0.0})
with open("experiments/lol_kills/donnees/marches.jsonl", "w") as f:
    for o in out:
        f.write(json.dumps(o) + "\n")
import collections
print(len(out), collections.Counter(o["res"] for o in out))
v = sorted(o["vol"] for o in out)
for s in (0, 100, 300, 500, 1000, 2000): print(">=", s, sum(1 for x in v if x >= s))
