"""Compteur de tweets : tous les « cas » du test historique (période, tranche, instant toutes les 6 h), avec la
probabilité du modèle et le prix horaire. Même boucle que ../vingt_pistes/scripts/tweets_contre_marche.py
(contrôle du règlement, prix horaire de moins de 6 h, somme des prix > 0,5, messages lus AVANT l'instant
seulement), mais on garde chaque cas pour pouvoir le payer ensuite au vrai prix.
Écrit donnees/prix_payes/tweets_cas_<dispersion>.json. Usage : tweets_cas.py [dispersion ...] (défaut 8 12 16)."""
import bisect
import json
import sys
from datetime import datetime, timedelta

sys.path.insert(0, "src")
from polymarket_agent import references as refs  # noqa: E402

D = "donnees/xt"
ev = json.load(open(f"{D}/marches.json"))
posts = {}


def P(h):
    if h not in posts:
        posts[h] = sorted(datetime.fromisoformat(t.replace("Z", "+00:00")) for t in json.load(open(f"{D}/{h}.json")))
    return posts[h]


def count(h, a, b):
    ts = P(h)
    return bisect.bisect_left(ts, b) - bisect.bisect_left(ts, a)


def tracking(h, start, end, t):
    hour = t.replace(minute=0, second=0, microsecond=0)
    hourly = [count(h, hour - timedelta(hours=k + 1), hour - timedelta(hours=k)) for k in range(335, -1, -1)]
    return {"debut": start.isoformat(), "fin": end.isoformat(), "total": count(h, start, t), "vu_le": t.isoformat(), "heures": hourly}


def cases(disp):
    out = []
    for e in ev:
        h = e["compte"]
        start = datetime.fromisoformat(e["debut"])
        end = datetime.fromisoformat(e["fin"]) - timedelta(seconds=1)
        if P(h)[0] > start - timedelta(days=14):
            continue
        final = count(h, start, end + timedelta(seconds=1))
        bks = []
        for m in e["marches"]:
            b = refs.bucket_of(m["titre"] or "")
            if b and m["hist"]:
                bks.append((b, [x["t"] for x in m["hist"]], [x["p"] for x in m["hist"]], m["prix_final"], m["titre"]))
        if not bks:
            continue
        win = [b for b in bks if b[0][0] <= final <= b[0][1]]
        paid = [b for b in bks if json.loads(b[3] or "[0]")[0] in ("1", 1)]
        if len(win) != 1 or (paid and paid[0][0] != win[0][0]):
            continue  # écart de règlement : exclu, comme le 20/10
        t = start + timedelta(hours=6)
        while t < end - timedelta(hours=3):
            ts = t.timestamp()
            prices = []
            for b, tt, pp, _, _ in bks:
                i = bisect.bisect_right(tt, ts) - 1
                prices.append(pp[i] if i >= 0 and ts - tt[i] < 6 * 3600 else None)
            if all(p is not None for p in prices) and sum(prices) > 0.5:
                tr = tracking(h, start, end, t)
                for (b, _, _, _, titre), p in zip(bks, prices):
                    q = refs.tweet_bucket_probability(tr, b, t, disp, 168, 336, 0.5)
                    out.append({"h": h, "slug": e["slug"], "t": int(ts), "fin": int(end.timestamp()) + 1, "titre": titre,
                                "b": list(b), "p": p, "q": q, "won": b[0] <= final <= b[1]})
            t += timedelta(hours=6)
    return out


if __name__ == "__main__":
    for disp in [float(x) for x in sys.argv[1:]] or [8.0, 12.0, 16.0]:
        c = cases(disp)
        json.dump(c, open(f"donnees/prix_payes/tweets_cas_{disp}.json", "w"))
        print("dispersion", disp, len(c), "cas", len({x["slug"] for x in c}), "périodes", flush=True)
