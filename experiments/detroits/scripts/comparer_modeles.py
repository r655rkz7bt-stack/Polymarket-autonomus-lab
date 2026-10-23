"""Compare, sur tout l'historique PortWatch, des lois pour la moyenne sur 7 jours à h jours :
(a) marche aléatoire (ma7 aujourd'hui), (b) niveau récent (moyenne des L derniers jours), (c) mélange des deux.
Loi normale d'écart-type estimé sur les erreurs PASSÉES (jamais l'avenir). Mesure : log-vraisemblance moyenne et
probabilité attribuée à la tranche de 5 qui contient la vraie valeur."""
import math, sys, datetime as dt
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from modele import charge

def phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def evalue(csv, h=13, debut="2024-01-01", L=45, w=0.5, fen=365):
    jours, v, ma = charge(csv)
    n = len(jours)
    # erreurs passées de chaque modèle, pour estimer l'écart-type sans regarder l'avenir
    def pred(i, kind):
        if kind == "rw": return ma[i]
        lvl = sum(v[i - L + 1:i + 1]) / L
        return lvl if kind == "niveau" else w * ma[i] + (1 - w) * lvl
    res = {}
    for kind in ("rw", "niveau", "mix"):
        ll = pb = k = 0
        errs = []
        for i in range(max(L, 6 + 1), n - h):
            e = ma[i + h] - pred(i, kind)
            connues = errs[: max(0, len(errs) - h)]  # l'erreur de l'origine j n'est connue qu'à j + h
            if jours[i] >= debut and len(connues) >= 60:
                recent = connues[-fen:]
                sd = (sum(x * x for x in recent) / len(recent)) ** .5
                mu = pred(i, kind)
                y = ma[i + h]
                ll += -0.5 * math.log(2 * math.pi * sd * sd) - 0.5 * ((y - mu) / sd) ** 2
                lo = 5 * math.floor(y / 5)
                pb += phi((lo + 5 - mu) / sd) - phi((lo - mu) / sd)
                k += 1
            errs.append(e)
        res[kind] = (ll / k, pb / k, k)
    return res

if __name__ == "__main__":
    for nom in ("bab", "hormuz"):
        for debut in ("2024-01-01", "2025-10-01"):
            r = evalue(f"experiments/detroits/donnees/{nom}.csv", debut=debut)
            print(nom, debut, {k: (round(a, 3), round(b, 3), n) for k, (a, b, n) in r.items()})

    # prévision du jour (dernier jour connu) par le mélange, tranches du marché
    for nom, bornes in (("bab", [("<20", -1e9, 20), ("20-24", 20, 25), ("25-29", 25, 30), ("30-34", 30, 35), ("35+", 35, 1e9)]),):
        jours, v, ma = charge(f"experiments/detroits/donnees/{nom}.csv")
        i = len(jours) - 1
        lvl = sum(v[i - 44:i + 1]) / 45
        for w in (1.0, 0.5, 0.0):
            mu = w * ma[i] + (1 - w) * lvl
            errs = [ma[j + 13] - (w * ma[j] + (1 - w) * sum(v[j - 44:j + 1]) / 45) for j in range(60, i - 13 - 1) if jours[j] >= "2025-10-01"]
            sd = (sum(x * x for x in errs) / len(errs)) ** .5
            print(nom, "w", w, "mu", round(mu, 2), "sd", round(sd, 2), {n: round(phi((hi - mu) / sd) - phi((lo - mu) / sd), 3) for n, lo, hi in bornes})
