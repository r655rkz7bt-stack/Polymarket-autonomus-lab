"""« Plus gros séisme du jour » (UTC) : modèle empirique (part des 3 dernières années sans séisme >= x dans les mêmes heures
restantes) + maximum déjà observé, contre les prix des vrais échanges. Sortie : releves/jour_cas.json"""
import sys, json, re, bisect
sys.path.insert(0, "experiments/seismes/scripts")
from commun import *
from hebdo import load_trades, last_price, buy_price
DAY = 86400
SEUILS = [5.25, 5.45, 5.65, 5.85, 6.05]
BORNES = {"under": (-1, 5.25), "5.3 to 5.4": (5.25, 5.45), "5.5 to 5.6": (5.45, 5.65), "5.7 to 5.8": (5.65, 5.85), "5.9 to 6.0": (5.85, 6.05), "6.1 or more": (6.05, 99)}

def borne(q):
    for k, v in BORNES.items():
        if k in q or (k == "under" and "under 5.3" in q): return v

def no_event_prob(d0, h_from, x, years=3):
    """Part des jours des `years` années avant d0 où aucun séisme >= x n'a eu lieu entre h_from h et 24 h (UTC)."""
    n = ok = 0
    for k in range(1, 365 * years + 1):
        a = d0 - k * DAY + h_from * 3600; b = d0 - k * DAY + DAY
        i, j = bisect.bisect_left(TIMES, a), bisect.bisect_left(TIMES, b)
        n += 1; ok += all(c[2] < x for c in CAT[i:j])
    return ok / n

if __name__ == "__main__":
    cas = []
    for e in sorted(EV.values(), key=lambda e: e["end"]):
        if not e["closed"] or "biggest earthquake be on" not in e["title"]: continue
        m = re.search(r"on (\w+) (\d+), (\d+)", e["title"]); d0 = int(datetime(int(m.group(3)), MOIS[m.group(1)], int(m.group(2)), tzinfo=timezone.utc).timestamp())
        win = winner(e); mx = maxmag(d0, d0 + DAY)
        lo_w, hi_w = borne(win["q"]) if win else (None, None)
        trades = load_trades(e["id"])
        ok = win is not None and lo_w <= round(mx, 1) + 0 < hi_w + 1e-9 if win else None
        print(e["title"][-18:], "max", mx, "gagnant", win["q"][-22:] if win else None)
        for h in (0, 6, 12, 18):  # décision à h heures UTC du jour concerné
            T = d0 + h * 3600; mxs = maxmag(d0, T) if h else 0.0
            probs = {x: (no_event_prob(d0, h, x) if h < 24 else 1.0) for x in SEUILS}
            # P(max final < x) = [mxs < x] * P(aucun >= x dans le reste)
            cdf = {x: (1.0 if mxs < x else 0.0) * probs[x] for x in SEUILS}
            for mk in e["markets"]:
                lo, hi = borne(mk["q"])
                p_hi = cdf[hi] if hi in cdf else 1.0
                p_lo = cdf[lo] if lo in cdf else 0.0
                p = max(0.0, p_hi - p_lo)
                tok, other = mk["tokens"][0], mk["tokens"][1]
                cas.append(dict(ev=e["id"], jour=e["title"][-18:], h=h, lo=lo, hi=hi, gagne=int(win is not None and mk["id"] == win["id"]), p=round(p, 4), mxs=mxs,
                                last=last_price(trades, tok, other, T, 6 * 3600), ach_oui=buy_price(trades, tok, other, T, 2 * 3600), ach_non=buy_price(trades, other, tok, T, 2 * 3600)))
    json.dump(cas, open(R + "releves/jour_cas.json", "w"))
    print(len(cas))
