"""27/10/2026 : mêmes marchés « Over/Under » d'autres jeux : kills de Dota 2 (`kill_over_under_game`), manches de CS2 et Valorant (`round_over_under_game_N`).
Usage : python releve_autres.py dota2|cs2|val -> donnees/marches_<série>.jsonl (même format que marches.jsonl, `jeu` = n° de la carte). Échanges : releve_echanges.py avec SERIE=<série>."""
import gzip, json, re, sys, collections
from pathlib import Path
serie = sys.argv[1]
ev = json.loads(gzip.decompress(Path(f"experiments/bo3_coherence/donnees/evenements_{serie}.json.gz").read_bytes()))
J = lambda x: json.loads(x) if isinstance(x, str) else x
out = []
for e in ev:
    for m in e["markets"]:
        t = m.get("sportsMarketType") or ""
        if t != "kill_over_under_game" and not re.fullmatch(r"round_over_under_game_\d", t):
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
        g = re.search(r"Game (\d)", m["question"]) or re.search(r"game_(\d)", t)
        out.append({"id": m["id"], "cond": m["conditionId"], "event": e["id"], "titre": e["title"], "jeu": int(g.group(1)) if g else None, "type": t,
                    "ligne": float(m["line"]), "debut": m.get("gameStartTime"), "over": tk[0], "under": tk[1], "res": res,
                    "vol": float(m.get("volumeNum") or 0), "ferme": m.get("closedTime"),
                    "taux": float((J(m.get("feeSchedule")) or {}).get("rate") or 0) if m.get("feesEnabled") else 0.0})
with open(f"experiments/lol_kills/donnees/marches_{serie}.jsonl", "w") as f:
    for o in out: f.write(json.dumps(o) + "\n")
print(serie, len(out), collections.Counter(o["res"] for o in out), collections.Counter(o["type"] for o in out))
v = [o["vol"] for o in out]
print(">=100", sum(1 for x in v if x >= 100), ">=1000", sum(1 for x in v if x >= 1000))
