"""Chance de chaque société d'être n° k mondial à la clôture d'une date cible, sachant les capitalisations du jour.

Capitalisation quotidienne = cours de clôture (Yahoo) × nombre d'actions implicite (capitalisation hebdomadaire de
companiesmarketcap / cours de la même semaine, dernier relevé AVANT la date). Mouvements futurs : fenêtres réelles de H séances
tirées des 3 années précédant la décision (rendements joints de toutes les sociétés, mêmes dates : corrélations et queues
réelles, aucun regard vers le futur)."""
import json, math
from bisect import bisect_right
from datetime import date, datetime, timezone
from pathlib import Path

D = Path(__file__).parent / "donnees"
SYMS = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "AVGO", "TSLA", "2222.SR"]
NOMS = {"apple": "AAPL", "nvidia": "NVDA", "microsoft": "MSFT", "alphabet": "GOOGL", "google": "GOOGL", "amazon": "AMZN",
        "meta": "META", "broadcom": "AVGO", "tesla": "TSLA", "saudi aramco": "2222.SR", "aramco": "2222.SR"}


def sym_of(name):
    n = (name or "").lower()
    for k, v in NOMS.items():
        if k in n:
            return v
    return None


def _prices(sym):
    r = json.loads((D / f"{sym}.json").read_text())["chart"]["result"][0]
    q = r["indicators"]["quote"][0]["close"]
    return {datetime.fromtimestamp(t, timezone.utc).date(): v for t, v in zip(r["timestamp"], q) if v}


def _shares(sym, px):
    mc = json.loads((D / f"{sym}_mc.json").read_text())
    days = sorted(px)
    out = []
    for x in mc:
        d = datetime.fromtimestamp(x["d"], timezone.utc).date()
        i = bisect_right(days, d) - 1
        if i >= 0 and (d - days[i]).days <= 6:
            out.append((d, x["m"] * 1e5 / px[days[i]]))
    return sorted(out)


class Univers:
    def __init__(self, sans_derive=True):
        self.sans_derive = sans_derive
        self.px = {s: _prices(s) for s in SYMS}
        self.sh = {s: _shares(s, self.px[s]) for s in SYMS}
        self.days = sorted(self.px["AAPL"])            # séances américaines
        self.ffill = {}
        for s in SYMS:                                    # Aramco : dernier cours connu à chaque séance américaine
            p, last, keys = self.px[s], None, sorted(self.px[s])
            j, f = 0, {}
            for d in self.days:
                while j < len(keys) and keys[j] <= d:
                    last = p[keys[j]]; j += 1
                if last:
                    f[d] = last
            self.ffill[s] = f

    def cap(self, s, d):
        sh = self.sh[s]
        i = bisect_right([x[0] for x in sh], d) - 1   # actions connues à cette date (relevé hebdomadaire passé)
        if i < 0 or d not in self.ffill[s]:
            return None
        return self.ffill[s][d] * sh[i][1]

    def proba_rangs(self, decision: datetime, cible: date, annees=3, syms=None):
        """Chances d'être n° 1, 2, 3 à la clôture de `cible` ; seules les clôtures finies avant `decision` sont lues."""
        syms = syms or SYMS
        closes = [d for d in self.days if datetime(d.year, d.month, d.day, 21, tzinfo=timezone.utc) <= decision]
        c0 = closes[-1]
        tgt = [d for d in self.days if d <= cible]
        # nombre de séances jusqu'à la cible : calendrier connu d'avance (jours ouvrés hors fériés)
        H = sum(1 for d in self.days if c0 < d <= cible) if tgt and tgt[-1] >= c0 and cible <= self.days[-1] else None
        if H is None:
            H = _jours_ouvres(c0, cible)
        caps = {s: self.cap(s, c0) for s in syms}
        caps = {s: v for s, v in caps.items() if v}
        if H == 0:
            order = sorted(caps, key=caps.get, reverse=True)
            return {s: [1.0 * (order.index(s) == k) for k in range(3)] for s in caps}, caps, 0
        hist = [d for d in closes if d >= date(c0.year - annees, c0.month, min(c0.day, 28))]
        cnt = {s: [0, 0, 0] for s in caps}
        n = 0
        wins = []
        for i in range(len(hist) - H):
            a, b = hist[i], hist[i + H]
            r = {}
            for s in caps:
                pa, pb = self.ffill[s].get(a), self.ffill[s].get(b)
                if not pa or not pb:
                    break
                r[s] = math.log(pb / pa)
            else:
                wins.append(r)
        # sans dérive : la tendance passée d'une action (NVIDIA ×8 en 2023-2024) n'est pas une prévision
        mu = {s: sum(w[s] for w in wins) / len(wins) for s in caps} if self.sans_derive else {s: 0.0 for s in caps}
        for r in wins:
            new = {s: caps[s] * math.exp(r[s] - mu[s]) for s in caps}
            if True:
                order = sorted(new, key=new.get, reverse=True)
                for k in range(3):
                    cnt[order[k]][k] += 1
                n += 1
        return {s: [c / n for c in cnt[s]] for s in caps}, caps, H


def _jours_ouvres(a, b):
    from datetime import timedelta
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5 and (d.month, d.day) not in ((11, 26), (12, 25), (1, 1)):
            n += 1
    return n


if __name__ == "__main__":
    u = Univers()
    p, caps, H = u.proba_rangs(datetime(2026, 11, 13, 6, tzinfo=timezone.utc), date(2026, 11, 30))
    print("H", H)
    for s in sorted(caps, key=caps.get, reverse=True):
        print(s, round(caps[s] / 1e12, 3), [round(x, 4) for x in p[s]])
