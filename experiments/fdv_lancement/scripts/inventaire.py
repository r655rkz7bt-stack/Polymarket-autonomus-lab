"""28/10/2026 : inventaire des marchés « <jeton> FDV above $X one day after launch » réglés (relevé de contrer_crypto_passe, marches_c.jsonl) : événements, seuils, dates de
règlement, échanges. Usage : python inventaire.py"""
import json, gzip, collections, datetime as dt, re
from pathlib import Path
D = Path("experiments/contrer_crypto_passe/donnees")
ms = [json.loads(l) for l in open(D / "marches_c.jsonl")]
ev = collections.defaultdict(list)
for m in ms: ev[m["event_id"]].append(m)
print(len(ms), "marchés,", len(ev), "événements")
def seuil(q):
    mm = re.search(r"\$([\d.,]+)\s*([KMB]?)", q); 
    if not mm: return None
    return float(mm[1].replace(",", "")) * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[mm[2]]
n_ech = 0
for e, v in sorted(ev.items(), key=lambda kv: kv[1][0]["closed"] or "")[:200]:
    v.sort(key=lambda m: seuil(m["question"]) or 0)
    win = [seuil(m["question"]) for m in v if str(m["prices"][0]) == "1"]
    tot = 0
    for m in v:
        p = D / "echanges" / f"{m['id']}.json.gz"
        if p.exists(): tot += len(json.loads(gzip.decompress(p.read_bytes()))["echanges"])
    n_ech += tot
    print(v[0]["event_title"][:48].ljust(48), (v[0]["closed"] or "")[:10], f"{len(v):2d} seuils", f"OUI max {max(win) if win else 0:>12,.0f}", f"vol {sum(m['vol'] or 0 for m in v):9,.0f} $", f"{tot:5d} échanges")
print(n_ech, "échanges")
