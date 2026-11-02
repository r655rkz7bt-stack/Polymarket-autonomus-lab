"""Dispersion de la formule `compteur_tweets` par compte (XTracker, tous les comptes suivis) : pour des fenêtres de 7 jours dont le début est
à 0 h et 54 h après la décision, log-score d'une bande de ±8 % autour du total réel et part de totaux dans les queues (PIT < 0,1 ou > 0,9, attendu 20 %).
Entrée : donnees/xt/<compte>.json (vingt_pistes/scripts/tweets_releve_messages.py, lancé depuis experiments/vingt_pistes/donnees). 02/11/2026."""
import json, sys, math, bisect
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "src")
from polymarket_agent.references import negbin_interval
D = sys.argv[1]
ACC = ("elonmusk", "realDonaldTrump", "WhiteHouse", "tedcruz", "ZelenskyyUa", "NYCMayor", "cz_binance")
def lire(h):
    return sorted(datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() for t in json.load(open(f"{D}/{h}.json")))
for lead in (54, 0):
    print("délai avant le début (h) :", lead)
    for h in ACC:
        ts = lire(h)
        c = lambda a, b: bisect.bisect_left(ts, b) - bisect.bisect_left(ts, a)
        s = ts[0] + 15 * 86400; fin = ts[-1] - 7 * 86400
        res = {d: [0.0, 0, 0] for d in (3, 5, 8, 12, 20)}
        n = 0
        while s <= fin:
            T = s - lead * 3600
            rec = c(T - 168 * 3600, T) / 168; lon = c(T - 336 * 3600, T) / 336
            m = (0.5 * rec + 0.5 * lon) * 168
            act = c(s, s + 7 * 86400)
            if m > 3 and act > 3:
                w = max(3, int(0.08 * act)); n += 1
                for d in res:
                    p = negbin_interval(max(act - w, 0), act + w, m, d); res[d][0] += math.log(max(p, 1e-6))
                    pit = negbin_interval(0, act, m, d)
                    res[d][1] += pit < 0.1 or pit > 0.9
            s += 12 * 3600
        print(f"  {h:16s} n {n:4d}", " ".join(f"d{d}: {v[0]/n:6.3f} q{v[1]/n:.0%}" for d, v in res.items()))
