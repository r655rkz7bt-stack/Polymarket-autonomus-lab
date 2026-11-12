"""Pari « DeepStateMap touche la commune (zone occupée ou grise) → acheter le OUI des marchés « enter / any territory » encore
ouverts » : prix horaire du OUI 2 h après la publication de la carte (`createdAt` + 2 h, sans regard vers le futur), issue réglée.
Sortie texte. Usage : analyse.py [delai_heures] [mode: touche|occ]"""
import bisect, json, sys
from datetime import datetime
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "donnees"
DELAI = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
MODE = sys.argv[2] if len(sys.argv) > 2 else "touche"


def ts(s):
    s = s.replace("Z", "+00:00").replace(" ", "T")
    if s.endswith("+00"):
        s += ":00"
    if "+" not in s[10:]:
        s += "+00:00"
    return datetime.fromisoformat(s).timestamp()


ms = json.loads((D / "marches.json").read_text())
cv = json.loads((D / "couverture_dsm.json").read_text())
px = json.loads((D / "prix.json").read_text())
rows = []
for m in ms:
    if m["lat"] is None or not m["clos"] or m["prix"] not in ([1.0, 0.0], [0.0, 1.0]):
        continue
    q = m["question"]
    if "Ukraine" in q or "capture all" in q:          # « enter » / « capture <ville> » seulement (une part du territoire suffit souvent)
        continue
    k = f"{m['lat']:.4f},{m['lon']:.4f}"
    a, b = ts(m["creation"]), ts(m["ferme"])
    sig = None
    for t, po, pg, to, tg in cv.get(k, []):
        hit = tg if MODE == "touche" else to
        tt = ts(t) + DELAI * 3600
        if hit:
            if tt <= a:
                sig = "deja"
                break
            if tt < b:
                sig = tt
            break
    if sig is None or sig == "deja":
        rows.append((m, sig, None))
        continue
    h = px.get(m["id"]) or []
    i = bisect.bisect_right([x[0] for x in h], sig) - 1
    rows.append((m, sig, h[i][1] if i >= 0 else None))
n = g = cout = gain = 0
for m, sig, p in rows:
    issue = int(m["prix"][0] == 1.0)
    if isinstance(sig, float) and p is not None:
        n += 1; cout += p; gain += issue - p; g += issue
        print(f"{datetime.utcfromtimestamp(sig):%Y-%m-%d %H}h  {m['question'][:62]:62s} prix {p:.3f} issue {issue}  fermé {m['ferme'][:10]}")
print(f"\n{n} paris, {g} gagnés pour {cout:.2f} attendus, rendement {gain / cout * 100 if cout else 0:+.1f} % par mise")
print("sans signal avant la fermeture :", sum(1 for m, s, p in rows if s is None), "dont OUI :", sum(1 for m, s, p in rows if s is None and m["prix"][0] == 1.0),
      "; déjà touchée à la création :", sum(1 for m, s, p in rows if s == "deja"))
