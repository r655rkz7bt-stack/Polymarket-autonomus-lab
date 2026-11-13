"""Écoutes 2026 estimées par titre (mondial ou US) : kworb ne garde que les 36 dernières semaines (depuis le 05/03/2026) ;
les semaines manquantes de janvier-février (8 semaines, 01/01 → 26/02) sont estimées par la moyenne des 4 premières semaines
connues de 2026 SI le titre était déjà sorti (première semaine kworb avant 2026 ou total de toutes les semaines > somme connue),
sinon comptées via le total « toutes semaines » (global_weekly_totals) quand le titre est sorti en 2026.
Usage : python estime_2026.py [global|us] [fin AAAA-MM-JJ] [n]"""
import json, re, sys
from pathlib import Path
D = Path(__file__).parent / "donnees"
col = 1 if len(sys.argv) > 1 and sys.argv[1] == "us" else 0
fin = sys.argv[2] if len(sys.argv) > 2 else "2026-12-31"
n = int(sys.argv[3]) if len(sys.argv) > 3 else 15
tot = {}
t = (D / "global_weekly_totals.html").read_text()
for r in re.findall(r"<tr>(.*?)</tr>", t, re.S):
    m = re.search(r'href="\.\./track/([A-Za-z0-9]+)\.html"', r)
    tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
    if m and len(tds) >= 7:
        tot[m.group(1)] = (int(tds[1]), int(tds[-1].replace(",", "")))
res = []
for l in open(D / "titres.jsonl"):
    x = json.loads(l)
    s = x["semaines"]
    connues = sorted(d for d in s if "2026-03-05" <= d <= fin)
    somme = sum(s[d][col] for d in connues)
    avant = [d for d in s if d < "2026-01-01"]
    wks, total = tot.get(x["id"], (None, None))
    if connues:
        moy4 = sum(s[d][col] for d in connues[:4]) / min(4, len(connues))
    else:
        moy4 = 0
    # sorti avant le 05/03 ? (semaines 2026 connues dès la première semaine de mars, ou historique d'avant 2026)
    if connues and connues[0] == "2026-03-05" and (avant or (col == 0 and total and wks and wks > len([d for d in s if d >= '2026-03-05']) + 2)):
        manque = 8 * moy4      # estimation grossière de janvier-février
        sure = False
    elif col == 0 and total and connues and not avant and wks and wks > len(connues):
        manque = max(0, total - sum(v[0] for v in s.values()))   # sorti en 2026 : le total toutes semaines contient les semaines manquantes
        sure = True
    else:
        manque, sure = 0, True
    res.append((somme + manque, somme, manque, sure, x["titre"], s[connues[-1]][col] if connues else 0))
res.sort(reverse=True)
for i, (e, so, ma, sure, ti, der) in enumerate(res[:n], 1):
    print(f"{i:2d} {e/1e6:8.1f} M = {so/1e6:7.1f} connues + {ma/1e6:6.1f} {'(total kworb)' if sure else '(estimé jan-fév)'} ; dernière sem. {der/1e6:5.1f} M  {ti}")
