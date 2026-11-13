"""Semaines réglées : prix des tranches le vendredi, le samedi et le dimanche à 06 h UTC contre le total final du graphique."""
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

H = Path(__file__).parent
ms = json.loads((H / "donnees" / "marches.json").read_text())
ch = {r["x"]: sum(r["ys"].values()) / 1e12 for r in json.loads((H / "releve_graphique_2026-11-13T0600.json").read_text())["data"]["data"]}
ev = defaultdict(list)
for m in ms:
    ev[m["title"]].append(m)
for t, L in ev.items():
    mon = next((k for k in ch if datetime.fromisoformat(k).strftime("%B ") + str(datetime.fromisoformat(k).day) + "?" in t), None)
    print(t, "| total final", round(ch[mon], 2) if mon else None)
    if mon is None:
        continue
    m0 = datetime.fromisoformat(mon).replace(tzinfo=timezone.utc)
    for h in (4 * 24 + 6, 5 * 24 + 6, 6 * 24 + 6):
        T = (m0 + timedelta(hours=h)).timestamp()
        row = []
        for m in sorted(L, key=lambda x: x["tranche"]):
            p = [x for x in m["hist"] if x[0] <= T]
            row.append(f"{m['tranche']}:{p[-1][1] if p else '-'}{'*' if m['won'] == '1' else ''}")
        print(f"   lundi + {h} h", " ".join(row))
