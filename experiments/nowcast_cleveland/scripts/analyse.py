"""Prévision de Cleveland (connue la veille) contre le prix, sur les marchés d'inflation réglés.

Pour chaque événement et chaque délai k (jours avant le règlement) : prévision publiée avant le jour de décision,
erreur passée de la prévision au même délai (mois réglés AVANT la décision seulement), chance de chaque tranche
(normale ou erreurs empiriques), prix du OUI à l'instant de décision. Log-score modèle contre marché, puis achats simulés.
Usage : analyse.py [k ...]
"""
import bisect, json, math, statistics, sys, pathlib
from datetime import timedelta
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from commun import D, classify, bounds, ts, nowcasts, nc_before

NC = {"month": nowcasts("month"), "year": nowcasts("year")}
PRIX = json.loads((D / "prix.json").read_text())
EV = [e for e in json.loads((D / "evenements_tags.json").read_text()) if classify(e["title"]) and e.get("closed")]


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def erreurs(serie, freq, k, avant):
    """Erreurs (publié − prévision à k jours du publié) des mois dont le chiffre est sorti avant `avant`."""
    out = []
    for (s, ym), rec in NC[freq].items():
        if s != serie or not rec["actual"] or rec["actual"][0] >= avant:
            continue
        p = nc_before(rec, rec["actual"][0] - timedelta(days=k - 1)) if k >= 1 else None
        if p:
            out.append(rec["actual"][1] - p[1])
    return out


def prix_a(mid, t):
    h = PRIX.get(mid) or []
    tt = [x["t"] for x in h]
    i = bisect.bisect_right(tt, t) - 1
    return h[i]["p"] if i >= 0 else None


def lignes(k, mode="normale", fenetre=None):
    rows = []
    for e in EV:
        serie, freq, (y, mo) = classify(e["title"])
        ms = [m for m in e["markets"] if m.get("closedTime") and bounds(m.get("groupItemTitle") or "")]
        if not ms:
            continue
        rel = min(ts(m["closedTime"]) for m in ms)
        if y is None:
            y = rel.year if mo < rel.month else rel.year - 1
        rec = NC[freq].get((serie, (y, mo)))
        if not rec:
            continue
        T = rel - timedelta(days=k)
        p = nc_before(rec, T.date())
        if not p or (T.date() - p[0]).days > 4:
            continue
        err = erreurs(serie, freq, k, T.date())
        if fenetre:
            err = err[-fenetre:]
        if len(err) < 24:
            continue
        mu, sd = statistics.mean(err), statistics.pstdev(err)
        act = rec["actual"][1] if rec["actual"] else None
        for m in ms:
            lo, hi = bounds(m["groupItemTitle"])
            win = json.loads(m["outcomePrices"])[0] in ("1", 1)
            if mode == "normale":
                pm = phi((hi - p[1] - mu) / sd) - phi((lo - p[1] - mu) / sd)
            else:
                pm = sum(1 for x in err if lo <= p[1] + x < hi) / len(err)
            pm = min(max(pm, 0.005), 0.995)
            px = prix_a(m["id"], T.timestamp())
            rows.append(dict(ev=e["id"], titre=e["title"], serie=serie, freq=freq, ym=(y, mo), tranche=m["groupItemTitle"],
                             mid=m["id"], win=win, pm=pm, px=px, nc=p[1], act=act, lo=lo, hi=hi, T=T.isoformat(),
                             frais=m.get("feeType") or "", sd=sd))
    return rows


def controle(rows):
    """Le chiffre publié par Cleveland (arrondi au dixième) tombe-t-il dans la tranche gagnante ?"""
    ok = bad = 0
    for r in rows:
        if r["win"] and r["act"] is not None:
            v = round(r["act"] + 1e-9, 1)
            if r["lo"] <= v < r["hi"]:
                ok += 1
            else:
                bad += 1
                print("   écart de règlement :", r["titre"], r["tranche"], "Cleveland", round(r["act"], 3))
    return ok, bad


if __name__ == "__main__":
    ks = [float(x) for x in sys.argv[1:]] or [1, 2, 4, 7]
    for k in ks:
        rows = [r for r in lignes(k) if r["px"] is not None]
        evs = {}
        for r in rows:
            evs.setdefault(r["ev"], []).append(r)
        print(f"\n### k = {k} jours : {len(evs)} événements, {len(rows)} tranches")
        if k == ks[0]:
            print("   contrôle du règlement (ok, écarts) :", controle(rows))
        ls_m = ls_x = 0.0
        n = 0
        par = {}
        for ev, rs in evs.items():
            sx = sum(max(r["px"], 0.001) for r in rs)
            w = [r for r in rs if r["win"]]
            if len(w) != 1:
                continue
            w = w[0]
            a, b = math.log(w["pm"]), math.log(max(w["px"], 0.001) / sx)
            ls_m += a; ls_x += b; n += 1
            key = (w["serie"], w["freq"])
            par.setdefault(key, [0, 0.0, 0.0]); par[key][0] += 1; par[key][1] += a; par[key][2] += b
        print(f"   log-score par événement : modèle {ls_m / n:+.3f}, marché {ls_x / n:+.3f} (n = {n})")
        for key, (c, a, b) in sorted(par.items()):
            print(f"     {key[0]:9s} {key[1]:5s} n={c:2d} modèle {a / c:+.3f} marché {b / c:+.3f}")
