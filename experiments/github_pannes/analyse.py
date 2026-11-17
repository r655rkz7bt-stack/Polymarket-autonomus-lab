"""Incidents critiques de GitHub par mois : plus longue durée (règle du marché « Longest GitHub critical incident in <mois> »).
Usage : python analyse.py <incidents.jsonl>"""
import json, re, sys, collections
from datetime import datetime, timedelta

MOIS = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def duree(i):
    t = re.sub(r"<[^>]+>", "", i["timestamp"]).replace(" UTC", "")
    g = re.match(r"(\w{3}) (\d+), (\d\d):(\d\d) - (?:(\w{3}) (\d+), )?(\d\d):(\d\d)", t)
    if not g:
        return None, None
    an = i["annee"]
    d0 = datetime(an, MOIS[g[1]], int(g[2]), int(g[3]), int(g[4]))
    d1 = datetime(an, MOIS[g[5] or g[1]], int(g[6] or g[2]), int(g[7]), int(g[8]))
    if d1 < d0:
        d1 = d1.replace(year=an + 1) if (g[5] and MOIS[g[5]] < MOIS[g[1]]) else d1 + timedelta(days=1)
    return d0, (d1 - d0).total_seconds() / 3600


def charge(path):
    out = []
    for l in open(path):
        i = json.loads(l)
        d0, h = duree(i)
        copilot_seul = bool(re.fullmatch(r"(?i)(incident with |disruption with some )?copilot.*", i["name"])) and "and" not in i["name"]
        out.append(dict(i, debut=d0, heures=h, copilot_seul=copilot_seul))
    return out


if __name__ == "__main__":
    inc = charge(sys.argv[1])
    print("non lus :", sum(1 for i in inc if i["heures"] is None))
    crit = [i for i in inc if i["impact"] == "critical" and i["heures"] is not None and not i["copilot_seul"]]
    par_mois = collections.defaultdict(list)
    for i in crit:
        et = i["debut"] - timedelta(hours=5)   # heure de l'Est (approx. : hiver)
        par_mois[(et.year, et.month)].append(i)
    mois = sorted({(i["debut"].year, i["debut"].month) for i in inc if i["debut"]})
    for m in mois:
        l = par_mois.get(m, [])
        print(m, len(l), " ".join(f"{i['debut']:%d}:{i['heures']:.1f}h" for i in sorted(l, key=lambda x: x["debut"])))
