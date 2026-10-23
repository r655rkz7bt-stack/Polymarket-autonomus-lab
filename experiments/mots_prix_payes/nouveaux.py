"""Mots nouveaux (jamais proposés chez un orateur qui a déjà au moins 10 marchés) aux PRIX PAYÉS (23/10/2026) : NON acheté quand le OUI vaut
`min_yes` à `max_yes` (réglages de MotsNouveaux : 0,30-0,85). Prix payé = premier échange du jeton NON dans les `fenetre` heures après
T = premier échange + `delai` ; +0,01 d'écart ; frais 0,04·p·(1−p). Usage : python nouveaux.py <delai_h> <fenetre_h> [min_yes max_yes]"""
import bisect, collections, gzip, json, math, statistics as st, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import requests

D = Path("donnees")
DELAY, WIN = float(sys.argv[1]), float(sys.argv[2])
MINY, MAXY = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (0.30, 0.85)
rows = json.load(open(D / "rows.json"))["rows"]
cnt = collections.Counter()
nouveaux = []
for r in rows:  # déjà triées par date de clôture
    if r["avant"] == 0 and cnt[r["sp"]] >= 10 and len(r["tok"]) == 2 and r["cond"] and r["sp"] not in ("the announcers", "anyone"):
        nouveaux.append(r)
    cnt[r["sp"]] += 1
print(len(nouveaux), "marchés à mot nouveau", flush=True)
S = requests.Session(); S.headers["User-Agent"] = "curl/8"


def get(url, params):
    for k in range(5):
        try:
            return S.get(url, params=params, timeout=40).json()
        except Exception:
            time.sleep(2 ** k)


def trades(r):
    path = D / "cache" / f"{r['cond']}.json.gz"
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    out = []
    for page in range(10):
        b = get("https://data-api.polymarket.com/trades", {"market": r["cond"], "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list) or not b:
            break
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp")]
        if len(b) < 1000:
            break
    path.write_bytes(gzip.compress(json.dumps(out).encode()))
    return out


with ThreadPoolExecutor(8) as ex:
    allt = list(ex.map(trades, nouveaux))
ts = lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() if x else None
achats = []
for r, tr in zip(nouveaux, allt):
    if not tr:
        continue
    T = min(t[0] for t in tr) + DELAY * 3600
    if T > (ts(r["closed"] or r["end"]) or 1e18) - 3600:
        continue
    yes_t, no_t = r["tok"]
    pts = sorted((t[0], t[3] if t[1] == no_t else 1 - t[3]) for t in tr if (t[1] == no_t and t[2] == "BUY") or (t[1] == yes_t and t[2] == "SELL"))
    i = bisect.bisect_left([a for a, _ in pts], T)
    if i >= len(pts) or pts[i][0] - T > WIN * 3600:
        continue
    paid = pts[i][1] + 0.01
    yes = 1 - paid
    if not (MINY <= yes <= MAXY) or paid >= 0.98:
        continue
    won = not r["yes"]
    achats.append(dict(ev=r["ev"], paid=paid, won=won, gain=((1.0 if won else 0.0) - paid - 0.04 * paid * (1 - paid)) / paid,
                       mois=datetime.fromtimestamp(T).strftime("%Y-%m"), sp=r["sp"]))
g = [x["gain"] for x in achats]
ev = collections.defaultdict(list)
for x in achats:
    ev[x["ev"]].append(x["gain"])
pe = [st.mean(v) for v in ev.values()]
mois = collections.defaultdict(list)
for x in achats:
    mois[x["mois"]].append(x["gain"])
print(f"délai {DELAY} h, fenêtre {WIN} h, OUI {MINY}-{MAXY} : {len(g)} achats NON, {len(pe)} événements | par achat {st.mean(g):+.3f} "
      f"(t {st.mean(g) / st.stdev(g) * math.sqrt(len(g)):+.2f}) | par événement {st.mean(pe):+.3f} (t {st.mean(pe) / st.stdev(pe) * math.sqrt(len(pe)):+.2f}) | "
      f"NON gagne {sum(x['won'] for x in achats)}/{sum(x['paid'] for x in achats):.1f} attendus")
print("  par mois :", " ".join(f"{k}:{st.mean(v):+.2f}(n{len(v)})" for k, v in sorted(mois.items())))
