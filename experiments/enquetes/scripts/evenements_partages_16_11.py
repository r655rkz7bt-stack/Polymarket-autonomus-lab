"""Famille 5 (16/11/2026) : paris liés ENTRE stratégies v2. Pour chaque événement, quelles stratégies y ont acheté, combien
d'euros, sur quels jetons (même jeton / jetons différents). Un classement qui compte ces stratégies comme indépendantes
compte le même tirage plusieurs fois."""
import json, os, sys
from collections import defaultdict

D = sys.argv[1] if len(sys.argv) > 1 else "published_data/ledger/fantome_v2"
par_ev = defaultdict(lambda: defaultdict(lambda: {"eur": 0.0, "jetons": set(), "n": 0}))
for f in sorted(os.listdir(D)):
    strat = f.replace(".jsonl", "")
    for l in open(os.path.join(D, f)):
        e = json.loads(l)
        d = e.get("data") or {}
        if e.get("type") != "BUY" and "event_id" not in d:
            continue
        ev = d.get("event_id")
        if not ev:
            continue
        cost = float(d.get("gross") or d.get("cost") or 0) or float(d.get("shares", 0)) * float(d.get("price", 0))
        x = par_ev[ev][strat]
        x["eur"] += cost; x["jetons"].add(d.get("token_id")); x["n"] += 1
partages = {ev: s for ev, s in par_ev.items() if len(s) >= 2}
print(f"{len(par_ev)} événements achetés, {len(partages)} par au moins deux stratégies")
tot = 0.0
for ev, s in sorted(partages.items(), key=lambda kv: -sum(v['eur'] for v in kv[1].values())):
    toks = [v["jetons"] for v in s.values()]
    commun = set.intersection(*toks)
    eur = sum(v["eur"] for v in s.values()); tot += eur
    print(ev, f"{eur:7.1f} €", "même jeton" if commun else "jetons différents",
          "; ".join(f"{k} {v['n']} achats {v['eur']:.1f} €" for k, v in s.items()))
print(f"total misé sur des événements partagés : {tot:.1f} €")
