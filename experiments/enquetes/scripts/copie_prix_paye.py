"""Principal contre fantômes copiés : même jeton, même prix ? (enquête du 24/10/2026, après-midi).

Pour chaque jeton acheté par le principal sous la stratégie S, compare son prix moyen payé au prix moyen
payé par le fantôme S sur le même jeton, et le rendement réalisé par part. Données : published_data/ledger/.
"""
import json, sys, collections
from decimal import Decimal as D

def lire(path):
    for l in open(path):
        yield json.loads(l)

def achats_et_reglements(path):
    buys = collections.defaultdict(lambda: [D(0), D(0), D(0)])  # token -> parts, coût, frais
    meta = {}
    settle = {}
    for r in lire(path):
        d = r["data"]
        if r["type"] == "BUY":
            t = d["token_id"]; s = D(d["shares"]); p = D(d["price"])
            b = buys[t]; b[0] += s; b[1] += s * p; b[2] += D(d["fee"])
            meta.setdefault(t, (d["strategy_id"], r["ts"], d.get("outcome")))
        elif r["type"] == "SETTLE":
            settle[d["token_id"]] = D(d["payout_per_share"])
    return buys, meta, settle

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "published_data/ledger"
    pb, pm, ps = achats_et_reglements(f"{base}/ledger.jsonl")
    par = collections.defaultdict(list)
    for t, (strat, ts, out) in pm.items():
        par[strat].append(t)
    tot = collections.Counter()
    for strat, toks in sorted(par.items(), key=lambda kv: -len(kv[1])):
        try:
            fb, fm, fs = achats_et_reglements(f"{base}/fantome/{strat}_v1.0.0.jsonl")
        except FileNotFoundError:
            continue
        n = 0; dp = D(0); gain_p = D(0); gain_f_au_prix_f = D(0); mis = D(0); manque = 0; ecart_ts = []
        for t in toks:
            if t not in fb or t not in ps:
                manque += 1 if t not in fb else 0
                continue
            sp, cp, _ = pb[t]; sf, cf, _ = fb[t]
            pp = cp / sp; pf = cf / sf
            n += 1; dp += (pp - pf)
            pay = ps[t]
            gain_p += sp * (pay - pp); mis += cp
            gain_f_au_prix_f += sp * (pay - pf)   # même parts, prix du fantôme
        if n:
            print(f"{strat:42s} jetons réglés {n:3d} (absents du fantôme {manque}) écart prix principal-fantôme moyen {float(dp/n):+.4f} ; "
                  f"gain principal {float(gain_p):+7.1f} € ; au prix du fantôme {float(gain_f_au_prix_f):+7.1f} € ; misé {float(mis):.0f} €")
            tot["p"] += gain_p; tot["f"] += gain_f_au_prix_f; tot["n"] += n
    print("TOTAL", float(tot["p"]), float(tot["f"]), tot["n"])
