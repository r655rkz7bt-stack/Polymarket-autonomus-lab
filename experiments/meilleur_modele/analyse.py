"""Le meneur du classement Text Arena (sans contrôle de style) à J-k garde-t-il la tête à la fin du mois, et le marché le paie-t-il
à sa juste chance ? Classement : jeu officiel lmarena-ai/leaderboard-dataset (Hugging Face, CC-BY-4.0, instantanés publiés).
Lancer avec un Python qui a pandas + pyarrow (environnement de recherche) : python -I analyse.py"""
import json, sys
from bisect import bisect_right
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd

H = Path(__file__).parent
ORG = {"google": "Google", "anthropic": "Anthropic", "openai": "OpenAI", "xai": "xAI", "meta": "Meta", "deepseek": "DeepSeek",
       "alibaba": "Alibaba", "moonshot": "Moonshot", "zhipu": "Zhipu", "mistral": "Mistral"}
d = pd.read_parquet(H / "donnees" / "text_full.parquet", columns=["model_name", "organization", "rating", "category", "leaderboard_publish_date"])
o = d[d.category == "overall"]
snap = {}
for day, g in o.groupby("leaderboard_publish_date"):
    best = g.groupby("organization")["rating"].max().sort_values(ascending=False)
    snap[str(day)] = [(ORG.get(k, k), float(v)) for k, v in best.items()]
days = sorted(snap)


def at(t: datetime):
    i = bisect_right(days, t.date().isoformat()) - 1   # instantané publié au plus tard ce jour-là (date seule : prudence)
    return (days[i], snap[days[i]]) if i >= 0 else (None, None)


ms = json.loads((H / "donnees" / "marches.json").read_text())
ev = defaultdict(list)
for m in ms:
    ev[m["event"]].append(m)
rows = []
for eid, L in sorted(ev.items(), key=lambda x: x[1][0]["end"]):
    end = datetime.fromisoformat(L[0]["end"].replace("Z", "+00:00"))
    winner = [m["company"] for m in L if m["won"] == "1"]
    check = end - timedelta(hours=12)
    day, s = at(check - timedelta(days=1))
    lead = s[0][0] if s else None
    style = "style control off" in (L[0]["description"] or "").lower() or "no-style-control" in (L[0]["description"] or "")
    print(L[0]["title"][:60], end.date(), "gagnant", winner, "| meneur au", day, lead, f"(écart {s[0][1] - s[1][1]:.1f})" if s else "",
          "| règle sans style" if style else "| style ?")
    for k in (21, 14, 10, 7, 3):
        T = end - timedelta(days=k)
        dd, s = at(T - timedelta(days=1))
        if not s:
            continue
        lead, gap = s[0][0], s[0][1] - s[1][1]
        mk = next((m for m in L if (m["company"] or "").lower() == lead.lower()), None)
        if mk is None:
            continue
        p = [x for x in mk["hist"] if x[0] <= T.timestamp()]
        if not p:
            continue
        rows.append({"mois": end.strftime("%Y-%m"), "k": k, "meneur": lead, "ecart": gap, "prix": p[-1][1], "garde": mk["won"] == "1",
                     "style": style})
print()
for k in (21, 14, 10, 7, 3):
    r = [x for x in rows if x["k"] == k]
    if r:
        print(f"J-{k}: {len(r)} mois, meneur garde {sum(x['garde'] for x in r)} fois pour {sum(x['prix'] for x in r):.1f} attendues au prix")
for lo, hi in ((0, 10), (10, 20), (20, 1000)):
    r = [x for x in rows if lo <= x["ecart"] < hi]
    if r:
        print(f"écart {lo}-{hi} points : {len(r)} (mois × délais), garde {sum(x['garde'] for x in r)} pour {sum(x['prix'] for x in r):.1f} attendues")
for x in rows:
    print(x)
