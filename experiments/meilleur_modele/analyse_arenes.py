"""Piste n° 51, autres arènes : Math (jeu `text`, catégorie « math », sans contrôle de style) et WebDev (jeu `webdev`, « overall ») :
le classement redonne-t-il le règlement, et le meneur à J-k garde-t-il la tête ? (python -I, pandas + pyarrow)"""
import json
from bisect import bisect_right
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

H = Path(__file__).parent
ORG = {"google": "Google", "anthropic": "Anthropic", "openai": "OpenAI", "xai": "xAI", "meta": "Meta", "deepseek": "DeepSeek"}


def snaps(fichier, cat):
    d = pd.read_parquet(H / "donnees" / fichier, columns=["organization", "rating", "category", "leaderboard_publish_date"])
    o = d[d.category == cat]
    s = {str(k): [(ORG.get(a, a), float(v)) for a, v in g.groupby("organization")["rating"].max().sort_values(ascending=False).items()]
         for k, g in o.groupby("leaderboard_publish_date")}
    return s, sorted(s)


ARENES = {"math": snaps("text_full.parquet", "math"), "webdev": snaps("webdev_full.parquet", "overall")}
ms = json.loads((H / "donnees" / "marches_math_webdev.json").read_text())
ev = defaultdict(list)
for m in ms:
    if "second" not in m["title"].lower() and "2025?" not in m["title"]:
        ev[m["event"]].append(m)
rows = []
for eid, L in sorted(ev.items(), key=lambda x: x[1][0]["end"]):
    ar = "webdev" if "webdev" in L[0]["title"].lower() else "math"
    s, days = ARENES[ar]
    end = datetime.fromisoformat(L[0]["end"].replace("Z", "+00:00"))

    def at(t):
        i = bisect_right(days, t.date().isoformat()) - 1
        return s[days[i]] if i >= 0 else None
    fin = at(end - timedelta(days=1))
    win = [m["company"] for m in L if m["won"] == "1"]
    print(L[0]["title"][:70], "| gagnant", win, "| meneur final", fin[0][0] if fin else None)
    for k in (14, 7, 3):
        T = end - timedelta(days=k)
        sn = at(T - timedelta(days=1))
        if not sn:
            continue
        mk = next((m for m in L if (m["company"] or "").lower() == sn[0][0].lower()), None)
        p = [x for x in (mk or {}).get("hist", []) if x[0] <= T.timestamp()]
        if mk and p:
            rows.append((ar, end.strftime("%Y-%m"), k, sn[0][0], round(sn[0][1] - sn[1][1], 1), p[-1][1], mk["won"] == "1"))
for k in (14, 7, 3):
    r = [x for x in rows if x[2] == k]
    print(f"J-{k}: {len(r)} mois, garde {sum(x[6] for x in r)} pour {sum(x[5] for x in r):.2f} attendues")
for x in rows:
    if x[2] == 14:
        print(x)
