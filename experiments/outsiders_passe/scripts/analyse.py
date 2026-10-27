"""`outsiders_surcotes` rejouée sur le passé (27/10/2026) : champs de candidats politiques réglés, somme des OUI > 1, NON des outsiders à 2-15 %.
À T = fin - H : prix du OUI de chaque candidat = dernier échange dans les 12 h avant T (au moins 80 % des candidats doivent en avoir un) ; somme des prix >= 1 + surcote ;
achat du NON de chaque outsider (OUI dans [ymin, ymax]) au premier échange de preneur dans les 6 h après T, frais payés ; règlement Gamma. Un pari par candidat."""
import json, gzip, sys, math, collections, datetime as dt
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
D = Path("experiments/outsiders_passe/donnees")
def ts(s):
    if not s: return None
    s = s.replace(" ", "T").replace("Z", "+00:00")
    if s.endswith("+00"): s += ":00"
    return int(dt.datetime.fromisoformat(s).timestamp())
def charge():
    out = []
    for l in open(D / "evenements.jsonl"):
        e = json.loads(l); p = D / "echanges" / f"echanges_{e['id']}.json.gz"
        if not p.exists(): continue
        tr = json.loads(gzip.decompress(p.read_bytes())); by = collections.defaultdict(list)
        for t in tr: by[t[1]].append(t)
        out.append((e, by))
    return out
def paris(EV, H=7, surcote=0.03, ymin=0.02, ymax=0.15, fen=12 * 3600, W=6 * 3600, part_min=0.8):
    res = []
    for e, by in EV:
        end = ts(e["end"]); T = end - int(H * 86400); items = []
        for m in e["markets"]:
            try: op = [float(x) for x in json.loads(m["outcomePrices"])]; yes, no = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"])
            except Exception: continue
            if outs != ["Yes", "No"]: continue
            closed = ts(m.get("closedTime")); start = ts(m.get("startDate"))
            if (closed and T > closed - 3600) or (start and T < start): items = []; break
            last = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in by.get(yes, []) + by.get(no, []) if T - fen <= t[0] <= T]
            items.append((m, op, yes, no, max(last)[1] if last else None))
        if len(items) < 5 or sum(1 for it_ in items if it_[4] is not None) < part_min * len(items): continue
        if any(max(op) < 0.99 for _, op, *_ in items): continue
        total = sum(p for *_, p in items if p is not None)
        if total < 1 + surcote: continue
        for m, op, yes, no, p in items:
            if p is None or not ymin <= p <= ymax: continue
            buys = sorted((t[0], t[3] if t[1] == no else 1 - t[3]) for t in by.get(no, []) + by.get(yes, []) if T <= t[0] <= T + W and ((t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")))
            if not buys: continue
            pay = buys[0][1]; rate = ((m.get("feeSchedule") or {}).get("rate")) or 0.0; f = it.fee(pay, rate); win = op[1] > 0.5
            res.append(dict(eid=e["id"], total=total, yes=p, pay=pay, win=win, fee=f, gain=(win - pay - f) / (pay + f), mois=(e["end"] or "")[:7], titre=(e["title"] or "")[:50]))
    return res
def resume(res):
    n = len(res)
    if not n: return "0 cas"
    cost = sum(r["pay"] + r["fee"] for r in res); g = sum(r["win"] - r["pay"] - r["fee"] for r in res)
    w = sum(r["win"] for r in res); ex = sum(r["pay"] for r in res); var = sum(r["pay"] * (1 - r["pay"]) for r in res)
    byev = collections.defaultdict(list)
    for r in res: byev[r["eid"]].append(r["gain"])
    mm = [sum(v) / len(v) for v in byev.values()]
    return f"n={n:5d} évts={len(byev):4d} gagnés={w:5d} attendus={ex:7.1f} z={(w - ex) / math.sqrt(var):+.2f} rendement={100 * g / cost:+.1f}% t_évt={(it._t_stat(mm) if len(mm) > 2 else 0):+.2f}"
if __name__ == "__main__":
    EV = charge(); print("événements avec échanges", len(EV))
    for H in (3, 7, 14, 30):
        for surcote in (0.0, 0.03, 0.10):
            print(f"H={H:2d} j surcote>={surcote:.2f} :", resume(paris(EV, H=H, surcote=surcote)))
    R = paris(EV, H=7, surcote=0.03)
    for lo, hi in ((0.02, 0.05), (0.05, 0.10), (0.10, 0.15)): print(f"   OUI {lo}-{hi} (H=7, surcote>=0,03) :", resume([r for r in R if lo <= r["yes"] < hi]))
    v = it.verdict([dict(gain=r["gain"], evenement=r["eid"], mois=r["mois"], cout=r["pay"] + r["fee"]) for r in R]); print({k: v.get(k) for k in ("paris", "verdict", "z_prix", "moitie_1", "moitie_2")})
