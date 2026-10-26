"""27/10/2026 : `contrer_crypto_patiente` (146 paris, z +1,9 par mise mais −28 € en euros) : mise fixe, gagnés contre attendus par les prix payés, par événement, par côté et par prix.
Lancer depuis la racine après `bash scripts/fetch_data.sh`."""
import sys, math, collections, statistics as st
sys.path.insert(0, "experiments/enquetes/scripts")
from charge_fantome import charger
for nom in sys.argv[1:] or ["contrer_crypto_patiente_v1.0.0", "contrer_crypto_v1.0.0"]:
    ps = charger(f"published_data/ledger/fantome/{nom}.jsonl")
    n = len(ps)
    rend = [float(p['gain'] / p['mise']) for p in ps]
    att = sum(float(p['prix']) for p in ps); gag = sum(float(p['pay']) for p in ps)
    var = sum(float(p['prix']) * (1 - float(p['prix'])) for p in ps)
    print(f"\n{nom}: {n} paris, mises {sum(float(p['mise']) for p in ps):.0f} €, gain {sum(float(p['gain']) for p in ps):+.0f} €")
    print(f"  rendement par mise moyen {st.mean(rend):+.1%} (t {st.mean(rend)/ (st.pstdev(rend)/math.sqrt(n)):+.2f}) ; gagnés {gag:.1f} pour {att:.1f} attendus, z {(gag-att)/math.sqrt(var):+.2f}")
    ev = collections.defaultdict(list)
    for p in ps: ev[p['event']].append(float(p['gain'] / p['mise']))
    em = [st.mean(v) for v in ev.values()]
    print(f"  {len(ev)} événements, rendement moyen par événement {st.mean(em):+.1%}, t {st.mean(em)/(st.pstdev(em)/math.sqrt(len(em))):+.2f}")
    for lab, f in [("côté Yes", lambda p: p['outcome'] == 'Yes'), ("côté No", lambda p: p['outcome'] == 'No'),
                   ("prix <0,15", lambda p: p['prix'] < 0.15), ("0,15-0,5", lambda p: 0.15 <= p['prix'] < 0.5), (">=0,5", lambda p: p['prix'] >= 0.5)]:
        sub = [p for p in ps if f(p)]
        if not sub: continue
        r = [float(p['gain'] / p['mise']) for p in sub]
        g = sum(float(p['pay']) for p in sub); a = sum(float(p['prix']) for p in sub); v = sum(float(p['prix']) * (1 - float(p['prix'])) for p in sub)
        print(f"  {lab:12s} {len(sub):4d} paris, rendement {st.mean(r):+.1%}, gagnés {g:.1f} / {a:.1f}, z {(g-a)/math.sqrt(v) if v else 0:+.2f}, gain {sum(float(p['gain']) for p in sub):+.0f} €")
    by_day = collections.defaultdict(float)
    for p in ps: by_day[p['reglé_ts'][:10]] += float(p['gain'])
    print("  gain par jour de règlement:", {k: round(v) for k, v in sorted(by_day.items())})
