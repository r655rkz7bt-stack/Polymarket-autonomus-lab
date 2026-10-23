"""Mots nouveaux aux PRIX PAYÉS, version 2 (23/10/2026) : « nouveau » = aucun marché du même orateur et du même mot dans un événement dont la
date de DÉBUT (startDate Gamma) est antérieure ; orateur avec au moins `min_orateur` marchés dans des événements débutés avant. (nouveaux.py
classait par date de clôture : un mot déjà proposé mais clos plus tard aurait compté comme nouveau.) Même exécution que nouveaux.py.
Usage : python nouveaux2.py <delai_h> <fenetre_h> [min_yes max_yes min_orateur]"""
import bisect, collections, gzip, json, math, statistics as st, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
sys.path.insert(0, "../../src")
from polymarket_agent import idea_test

D = Path("donnees")
A = sys.argv[1:]
DELAY, WIN = float(A[0]), float(A[1])
MINY, MAXY = (float(A[2]), float(A[3])) if len(A) > 3 else (0.30, 0.85)
MINSP = int(A[4]) if len(A) > 4 else 10
ts = lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() if x else None
start = {e["slug"]: ts(e["startDate"]) for e in json.load(open(D / "events.json"))}
rows = [r for r in json.load(open(D / "rows.json"))["rows"] if start.get(r["ev"])]
rows.sort(key=lambda r: start[r["ev"]])
seen_w, seen_sp, nouveaux = set(), collections.Counter(), []
i = 0
while i < len(rows):  # on traite les événements de même début ensemble : rien de ce groupe n'est « connu avant »
    j = i
    while j < len(rows) and start[rows[j]["ev"]] == start[rows[i]["ev"]]:
        j += 1
    group = rows[i:j]
    for r in group:
        if (r["sp"], r["w"]) not in seen_w and seen_sp[r["sp"]] >= MINSP and len(r["tok"]) == 2 and r["cond"] \
                and r["sp"] not in ("the announcers", "anyone") and not r["sp"].startswith('"'):
            nouveaux.append(r)
    for r in group:
        seen_w.add((r["sp"], r["w"]))
        seen_sp[r["sp"]] += 1
    i = j
print(len(nouveaux), "marchés à mot nouveau (début d'événement)", flush=True)


def trades(r):
    path = D / "cache" / f"{r['cond']}.json.gz"
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    import requests, time
    S = requests.Session(); S.headers["User-Agent"] = "curl/8"
    out = []
    for page in range(10):
        for k in range(5):
            try:
                b = S.get("https://data-api.polymarket.com/trades", params={"market": r["cond"], "limit": 1000, "offset": page * 1000}, timeout=40).json(); break
            except Exception:
                b = None; time.sleep(2 ** k)
        if not isinstance(b, list) or not b:
            break
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp")]
        if len(b) < 1000:
            break
    path.write_bytes(gzip.compress(json.dumps(out).encode()))
    return out


with ThreadPoolExecutor(8) as ex:
    allt = list(ex.map(trades, nouveaux))
bets, volumes = [], []
for r, tr in zip(nouveaux, allt):
    if not tr:
        continue
    T = min(t[0] for t in tr) + DELAY * 3600
    if T > (ts(r["closed"] or r["end"]) or 1e18) - 3600:
        continue
    yes_t, no_t = r["tok"]
    pts = sorted((t[0], t[3] if t[1] == no_t else 1 - t[3], t[4]) for t in tr if (t[1] == no_t and t[2] == "BUY") or (t[1] == yes_t and t[2] == "SELL"))
    k = bisect.bisect_left([a for a, _, _ in pts], T)
    if k >= len(pts) or pts[k][0] - T > WIN * 3600:
        continue
    paid = pts[k][1] + 0.01
    if not (MINY <= 1 - paid <= MAXY) or paid >= 0.98:
        continue
    won = not r["yes"]
    rate = float((r.get("fees") or {}).get("rate", 0.04) or 0.04) if isinstance(r.get("fees"), dict) else 0.04
    bets.append({"gain": ((1.0 if won else 0.0) - paid - rate * paid * (1 - paid)) / paid, "evenement": r["ev"],
                 "mois": datetime.fromtimestamp(T).strftime("%Y-%m"), "cout": paid})
    volumes.append(sum(p * q for t, p, q in pts if T <= t <= T + WIN * 3600))
v = idea_test.verdict(bets)
print(f"délai {DELAY} h, fenêtre {WIN} h, OUI {MINY}-{MAXY}, orateur ≥ {MINSP} : {v['paris']} paris, {v['evenements']} événements | rendement {v['rendement_moyen']:+.3f} "
      f"(t paris {v['confiance_paris']:+.2f}, t événements {v['confiance_evenements']:+.2f}, z des prix {v['z_prix']:+.2f}) | mois gagnants {v['mois_gagnants']} | {v['verdict']} : {v['raison']}")
print("  par prix payé :", v["par_prix"])
if volumes:
    print(f"  volume échangé sur le NON dans la fenêtre (USDC) : médiane {st.median(volumes):.0f}, quartiles {st.quantiles(volumes, n=4)[0]:.0f} / {st.quantiles(volumes, n=4)[2]:.0f}")
m = collections.defaultdict(list)
for b in bets:
    m[b["mois"][:4]].append(b["gain"])
print("  par année :", {k: (round(st.mean(x), 3), len(x)) for k, x in sorted(m.items())})
