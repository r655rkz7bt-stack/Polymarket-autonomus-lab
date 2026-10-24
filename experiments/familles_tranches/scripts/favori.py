"""Favorite d'un événement à tranches (une seule gagnante), par famille : gagne-t-elle plus que son prix ? Achat au dernier achat réel, frais 5 %."""
import gzip, json, sys, re, bisect
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, "experiments/box_office/scripts")
from polymarket_agent.idea_test import verdict
from analyse import yes_series, last_before, taker_buy, ts
R = Path("experiments/familles_tranches/releves")
EV = json.load(gzip.open(R / "evenements.json.gz", "rt"))
def load(eid):
    p = R / "echanges" / f"echanges_{eid}.json.gz"
    return json.loads(gzip.decompress(p.read_bytes())) if p.exists() else []
def cases(fam):
    out = []
    for e in EV:
        if e["fam"] != fam or not e.get("end"): continue
        w = [m for m in e["markets"] if m["prices"] and float(json.loads(m["prices"])[0]) > 0.99]
        if len(w) != 1 or any(len(m["tokens"]) != 2 for m in e["markets"]): continue
        tr = load(e["id"])
        if len(tr) < 20: continue
        out.append(dict(e=e, trades=tr, end=ts(e["end"]), ms=[dict(m, series=yes_series(tr, *m["tokens"]), win=int(m is w[0])) for m in e["markets"]]))
    return out
def run(C, h, lo=0.5, hi=1.0, rate=0.05, win=2 * 3600):
    bets = []
    for c in C:
        t = c["end"] - h * 3600
        pr = [(last_before(m["series"], t, 8 * 3600), m) for m in c["ms"]]
        pr = [(p, m) for p, m in pr if p is not None]
        if not pr: continue
        p0, m = max(pr, key=lambda x: x[0])
        if p0 < max(0.0, 1 - sum(p for p, _ in pr)) + 0.02: continue  # une tranche sans prix pourrait être la favorite
        if not lo <= p0 < hi: continue
        px = taker_buy(c["trades"], m["tokens"][0], m["tokens"][1], t, win, 1)
        if px is None or not lo <= px < hi + 0.05: continue
        cost = px + rate * px * (1 - px)
        bets.append({"gain": (m["win"] - cost) / cost, "evenement": c["e"]["id"], "mois": datetime.fromtimestamp(c["end"], timezone.utc).strftime("%Y-%m"), "cout": px})
    return bets
if __name__ == "__main__":
    for fam in ("rotten", "netflix", "vues"):
        C = cases(fam); print(fam, len(C), "événements utilisables")
        for h in (96, 48, 24, 12, 6):
            for lo, hi in ((0.5, 1.0), (0.5, 0.8), (0.8, 1.0)):
                b = run(C, h, lo, hi)
                if len(b) < 15: continue
                v = verdict(b)
                print(f"  h={h:3d} {lo}-{hi}: n={v['paris']:3d} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} gagnés/attendus {sum(1 for x in b if x['gain']>0)}/{sum(x['cout'] for x in b):.1f} z_prix {v['z_prix']:+.2f}")
