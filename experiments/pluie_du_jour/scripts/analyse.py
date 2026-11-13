"""Pluie du jour : la pluie déjà tombée (METAR horaire, IEM) contre le prix (13/11/2026, piste n° 55).

Pour chaque marché « ville » réglé : journée climatique = minuit à minuit, heure LOCALE STANDARD (règle NWS CLI).
T_obs = heure du premier METAR de la journée avec p01i ≥ 0,01 (pluie mesurable déjà vue). Contrôle du règlement : OUI ⇔ au
moins un METAR ≥ 0,01 dans la journée. Achats simulés : premier VRAI échange du jeton OUI après T_obs + délai, à un prix ≤
plafond, au moins `min_parts` parts ; gain = paiement − prix − frais (0,05 × p × (1 − p) par part).
Aussi le côté NON : à H heures locales avant la fin, aucune pluie vue → premier échange du jeton NON (référence : le taux).
Usage : python analyse.py [délai_minutes] [min_parts]
"""
import json, os, sys, re, math, collections
from datetime import datetime, timedelta, timezone

D = os.path.join(os.path.dirname(__file__), "..", "donnees")
OFF = {"ATL": -5, "BOS": -5, "DCA": -5, "MIA": -5, "NYC": -5, "PHL": -5, "DFW": -6, "IAH": -6, "MDW": -6, "MSY": -6,
       "DEN": -7, "PHX": -7, "LAX": -8, "SEA": -8, "SFO": -8}
MOIS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September",
                                     "October", "November", "December"], 1)}


def jour(title):
    if "4th of July" in title:
        return datetime(2026, 7, 4)
    m = re.search(r"on (\w+) (\d+)\?", title)
    return datetime(2026, MOIS[m.group(1)], int(m.group(2)))


def charge():
    ev = json.load(open(os.path.join(D, "marches.json")))
    tr = json.load(open(os.path.join(D, "echanges.json")))
    mt = json.load(open(os.path.join(D, "metar.json")))
    obs = collections.defaultdict(list)
    for st, txt in mt.items():
        for line in (txt or "").splitlines()[1:]:
            s, v, p = line.split(",")
            t = datetime.strptime(v, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            q = 0.0 if p in ("T", "M") else float(p)
            obs[s].append((t, q, p != "M"))
    for s in obs:
        obs[s].sort()
    return ev, tr, obs


def cas(ev, tr, obs, lag_min=10):
    out = []
    for eid, e in ev.items():
        if not e:
            continue
        d = jour(e["title"])
        trades = tr.get(eid) or []
        for m in e["markets"]:
            st = m["station"]
            if st not in OFF or not m["closed"] or not m["final"] or len(m["tokens"]) != 2:
                continue
            fin = [float(x) for x in m["final"]]
            if fin not in ([1.0, 0.0], [0.0, 1.0]):
                continue
            oui = fin[0] == 1.0
            start = d.replace(tzinfo=timezone.utc) - timedelta(hours=OFF[st])
            end = start + timedelta(days=1)
            rows = [(t, q) for t, q, ok in obs[st] if start + timedelta(minutes=55) <= t < end + timedelta(minutes=5)]
            n_ok = len(rows)
            first = next((t for t, q in rows if q >= 0.01), None)
            ty = m["tokens"][0]
            tok = [(datetime.fromtimestamp(x["timestamp"], timezone.utc), x["price"], x["size"], x["token_id"], x["side"])
                   for x in trades if x.get("condition_id") == m["condition"]]
            tok.sort()
            out.append({"eid": eid, "jour": d.date().isoformat(), "st": st, "oui": oui, "first": first, "n_obs": n_ok,
                        "start": start, "end": end, "yes": ty, "no": m["tokens"][1], "trades": tok})
    return out


def fee(p):
    return 0.05 * p * (1 - p)


def achat(c, token, t0, t1, cap, min_parts):
    for t, p, s, tk, side in c["trades"]:
        if tk == token and t0 <= t <= t1 and p <= cap and s >= min_parts:
            return t, p, s
    return None


if __name__ == "__main__":
    lag = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    mp = float(sys.argv[2]) if len(sys.argv) > 2 else 10
    ev, tr, obs = charge()
    cs = cas(ev, tr, obs)
    print("marchés américains réglés net :", len(cs), "jours :", len({c["jour"] for c in cs}))
    ok = [c for c in cs if c["n_obs"] >= 20]
    agree = sum((c["first"] is not None) == c["oui"] for c in ok)
    print(f"contrôle du règlement (≥ 20 METAR dans la journée) : {agree}/{len(ok)}")
    bad = [(c["jour"], c["st"], c["oui"], c["first"]) for c in ok if (c["first"] is not None) != c["oui"]]
    print("  désaccords :", bad[:30])
    # A. pluie déjà vue -> OUI
    res = []
    for c in ok:
        if c["first"] is None:
            continue
        b = achat(c, c["yes"], c["first"] + timedelta(minutes=lag), c["end"] + timedelta(hours=10), 0.985, mp)
        if b:
            t, p, s = b
            pay = 1.0 if c["oui"] else 0.0
            res.append((c["jour"], c["st"], p, pay, (pay - p - fee(p)) / p, (t - c["first"]).total_seconds() / 3600, s))
    if res:
        n = len(res); w = sum(r[3] for r in res); att = sum(r[2] for r in res)
        roi = sum(r[4] * r[2] for r in res) / sum(r[2] for r in res)
        print(f"\nA. pluie vue -> OUI (délai {lag} min, ≥ {mp} parts, prix ≤ 0,985) : {n} paris, {w:.0f} gagnés pour {att:.1f} attendus, "
              f"rendement par mise {roi:+.1%}, prix moyen {att/n:.3f}")
        for lo, hi in ((0, 0.8), (0.8, 0.9), (0.9, 0.95), (0.95, 0.99)):
            sub = [r for r in res if lo <= r[2] < hi]
            if sub:
                print(f"   prix {lo:.2f}-{hi:.2f} : {len(sub)} paris, {sum(r[3] for r in sub):.0f} pour {sum(r[2] for r in sub):.1f}, "
                      f"{sum(r[4]*r[2] for r in sub)/sum(r[2] for r in sub):+.1%}, délai médian {sorted(r[5] for r in sub)[len(sub)//2]:.1f} h")
        json.dump([list(map(str, r)) for r in res], open(os.path.join(D, f"paris_A_{lag}_{int(mp)}.json"), "w"))


def robustesse(cs, lag, mp, side_buy=True, cap=0.985, horizon_h=None):
    """Variante : seulement les échanges où le PRENEUR a acheté le OUI (prix = vendeur, achetable)."""
    res = []
    for c in cs:
        if c["first"] is None or c["n_obs"] < 20:
            continue
        t0 = c["first"] + timedelta(minutes=lag)
        t1 = c["end"] + timedelta(hours=10) if horizon_h is None else t0 + timedelta(hours=horizon_h)
        for t, p, s, tk, side in c["trades"]:
            if tk == c["yes"] and t0 <= t <= t1 and p <= cap and s >= mp and (side == "BUY" or not side_buy):
                pay = 1.0 if c["oui"] else 0.0
                res.append({"jour": c["jour"], "st": c["st"], "p": p, "pay": pay, "g": pay - p - fee(p), "h": (t - c["first"]).total_seconds() / 3600,
                            "t": t, "s": s})
                break
    return res


def resume(res, titre):
    if not res:
        print(titre, ": aucun pari"); return
    n = len(res); w = sum(r["pay"] for r in res); att = sum(r["p"] for r in res)
    roi = sum(r["g"] for r in res) / att
    par_jour = collections.defaultdict(float)
    for r in res:
        par_jour[r["jour"]] += r["g"] / r["p"]
    xs = list(par_jour.values()); m = sum(xs) / len(xs)
    sd = (sum((x - m) ** 2 for x in xs) / max(1, len(xs) - 1)) ** 0.5
    tj = m / (sd / len(xs) ** 0.5) if sd > 0 else float("inf")
    z = (w - att) / max(1e-9, sum(r["p"] * (1 - r["p"]) for r in res)) ** 0.5
    mois = collections.defaultdict(list)
    for r in res:
        mois[r["jour"][:7]].append(r)
    pm = " ".join(f"{k}:{len(v)}/{sum(x['g'] for x in v)/sum(x['p'] for x in v):+.0%}" for k, v in sorted(mois.items()))
    print(f"{titre} : {n} paris, {w:.0f} gagnés pour {att:.1f} attendus (z {z:+.1f}), rendement par mise {roi:+.1%}, "
          f"t par jour {tj:+.2f} ({len(xs)} jours) | {pm}")


def cote_non(cs, heures_avant_fin, mp=10, cap=0.985):
    """Côté NON : `heures_avant_fin` heures avant la fin de la journée climatique, aucune pluie mesurable vue → premier échange
    (preneur acheteur) du jeton NON après cet instant, au plus `cap`."""
    res = []
    for c in cs:
        if c["n_obs"] < 20:
            continue
        t0 = c["end"] - timedelta(hours=heures_avant_fin)
        if c["first"] is not None and c["first"] < t0:
            continue
        for t, p, s, tk, side in c["trades"]:
            if tk == c["no"] and t0 <= t <= c["end"] and p <= cap and s >= mp and side == "BUY":
                pay = 0.0 if c["oui"] else 1.0
                res.append({"jour": c["jour"], "st": c["st"], "p": p, "pay": pay, "g": pay - p - fee(p), "h": 0, "t": t, "s": s})
                break
    return res
