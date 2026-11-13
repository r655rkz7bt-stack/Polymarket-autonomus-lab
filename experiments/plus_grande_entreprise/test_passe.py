"""Test sur le passé : modèle (modele.py) contre le prix horaire du CLOB, marchés « n° k mondial à la fin du mois » réglés."""
import json, math, sys
from collections import Counter, defaultdict
from bisect import bisect_right
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from modele import Univers, sym_of

D = Path(__file__).parent / "donnees"
ms = json.loads((D / "marches.json").read_text())
u = Univers()
RANG = lambda t: 1 if t.lower().startswith("largest") else 2 if t.lower().startswith("2nd") else 3
print(Counter(m["feeType"] for m in ms), file=sys.stderr)

# contrôle du règlement : le classement des clôtures de la date cible redonne-t-il le résultat officiel ?
def cible(m):
    end = datetime.fromisoformat(m["end"].replace("Z", "+00:00"))
    return (end - timedelta(hours=6)).date()

cache = {}
def proba(decision, tgt):
    k = (decision, tgt)
    if k not in cache:
        cache[k] = u.proba_rangs(decision, tgt)
    return cache[k]

ok = bad = 0
for m in ms:
    s = sym_of(m["company"])
    tgt = cible(m)
    if tgt > u.days[-1]:
        continue
    p, caps, H = proba(datetime(tgt.year, tgt.month, tgt.day, 23, tzinfo=timezone.utc), tgt)
    pr = p.get(s, [0, 0, 0])[RANG(m["title"]) - 1] if s else 0.0
    if (pr > 0.5) == (m["won"] == 1):
        ok += 1
    else:
        bad += 1
        print("règlement différent :", m["title"], m["company"], m["won"], pr, {k: round(v / 1e12, 3) for k, v in caps.items()}, file=sys.stderr)
print("contrôle du règlement", ok, "sur", ok + bad, file=sys.stderr)

rows = []
for m in ms:
    s = sym_of(m["company"])
    tgt = cible(m)
    end = datetime.fromisoformat(m["end"].replace("Z", "+00:00"))
    ts = [t for t, _ in m["hist"]]
    for jours in (14, 10, 7, 5, 3, 2, 1):
        T = end - timedelta(days=jours)
        T = T.replace(minute=0, second=0, microsecond=0)
        i = bisect_right(ts, T.timestamp()) - 1
        if i < 0 or T.timestamp() - ts[i] > 6 * 3600:
            continue
        price = m["hist"][i][1]
        p, caps, H = proba(T, tgt)
        pr = p.get(s, [0, 0, 0])[RANG(m["title"]) - 1] if s else 0.0
        rows.append({"event": m["event"], "mois": tgt.strftime("%Y-%m"), "rang": RANG(m["title"]), "co": m["company"], "j": jours,
                     "prix": price, "modele": pr, "won": m["won"], "sym": s})
json.dump(rows, open(D / "lignes.json", "w"))
print(len(rows), "lignes", file=sys.stderr)
