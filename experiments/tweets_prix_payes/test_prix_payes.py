"""Compteur de tweets aux PRIX PAYÉS (23/10/2026). Refait le test « NON, sans NYC Mayor » de tweets_filles.py
(+12,8 % par période) avec les prix des vrais échanges (data-api) au lieu de l'historique horaire du CLOB + demi-écart.

  décision à t (toutes les 6 h, de début+6 h à fin−3 h), comme avant : modèle de `references.tweet_bucket_probability` ;
  prix connu à t   = dernier échange du jeton NON dans les `AVANT` heures qui précèdent (taker_cost, avant) ;
  prix payé        = premier échange du jeton NON dans les `APRES` heures qui suivent (taker_cost, après) ;
  pas d'échange après t : pas d'achat (on le compte).
Rendement = (gain − prix − frais) / prix ; frais = taux · p · (1 − p) (taux du barème Gamma du marché, 0,05 par défaut).
Lancer depuis experiments/tweets_prix_payes/ : PYTHONPATH=../../src python test_prix_payes.py [dispersion marge prix_min avant apres]"""
import bisect, collections, json, math, statistics as st, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from polymarket_agent import idea_test, references as refs
from polymarket_agent.http_client import HttpClient

D = Path("donnees/xt")
DISP = float(sys.argv[1]) if len(sys.argv) > 1 else 12.0
MARGIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.03
MINP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
AVANT = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0
APRES = float(sys.argv[5]) if len(sys.argv) > 5 else 2.0
R, W = 168, 0.5

periodes = json.load(open(D / "echanges_par_periode.json"))
http = HttpClient()
posts = {}


def P(h):
    if h not in posts:
        posts[h] = sorted(datetime.fromisoformat(t.replace("Z", "+00:00")) for t in json.load(open(D / f"{h}.json")))
    return posts[h]


def count(h, a, b):
    ts = P(h)
    return bisect.bisect_left(ts, b) - bisect.bisect_left(ts, a)


def tracking(h, start, end, t):
    hour = t.replace(minute=0, second=0, microsecond=0)
    hourly = [count(h, hour - timedelta(hours=k + 1), hour - timedelta(hours=k)) for k in range(335, -1, -1)]
    return {"debut": start.isoformat(), "fin": end.isoformat(), "total": count(h, start, t), "vu_le": t.isoformat(),
            "heures": hourly}


class Marche:
    """Échanges triés d'un jeton : prix d'achat de ce jeton à chaque instant (achat direct, ou vente de l'autre issue)."""
    def __init__(self, tok, other, trades):
        pts = sorted((t[0], t[3] if t[1] == tok else 1 - t[3]) for t in trades
                     if (t[1] == tok and t[2] == "BUY") or (t[1] == other and t[2] == "SELL"))
        self.t = [a for a, _ in pts]
        self.p = [b for _, b in pts]

    def avant(self, ts, window):
        i = bisect.bisect_right(self.t, ts) - 1
        return self.p[i] if i >= 0 and ts - self.t[i] <= window else None

    def apres(self, ts, window):
        i = bisect.bisect_left(self.t, ts)
        return self.p[i] if i < len(self.t) and self.t[i] - ts <= window else None


achats, sans_echange, signaux, ignores = [], 0, 0, []
ancien = []  # témoin : mêmes signaux achetés au dernier prix connu + 0,02 (façon test d'origine, sans exigence d'échange après)
for slug, info in periodes.items():
    if info is None:
        continue
    h = info["compte"]
    start, end = datetime.fromisoformat(info["debut"]), datetime.fromisoformat(info["fin"]) - timedelta(seconds=1)
    if P(h)[0] > start - timedelta(days=14):
        continue  # moins de 14 jours de messages avant la période : modèle non calibré (comme dans le test d'origine)
    final = count(h, start, end + timedelta(seconds=1))
    bks = []
    for m in info["marches"]:
        b = refs.bucket_of(m["titre"] or "")
        if b:
            trades_ = m
            bks.append((b, m))
    if not bks:
        continue
    win = [b for b in bks if b[0][0] <= final <= b[0][1]]
    paid = [b for b in bks if json.loads(b[1]["final"] or "[0]")[0] in ("1", 1)]
    if len(win) != 1 or (paid and paid[0][0] != win[0][0]):
        ignores.append(slug)  # le règlement relu ne redonne pas la tranche officielle
        continue
    trades = idea_test.fetch_event_trades(http, D / "cache", str(info["event_id"]))
    by_tok = collections.defaultdict(list)
    for tr in trades:
        by_tok[tr[1]].append(tr)
    t = start + timedelta(hours=6)
    while t < end - timedelta(hours=3):
        ts = int(t.timestamp())
        trk = tracking(h, start, end, t)
        for b, m in bks:
            q = refs.tweet_bucket_probability(trk, b, t, DISP, R, 336, W)
            if q is None:
                continue
            tr_ = by_tok[m["no"]] + by_tok[m["yes"]]
            mk = Marche(m["no"], m["yes"], tr_)
            connu = mk.avant(ts, AVANT * 3600)
            if connu is None or not (max(0.01, MINP) <= connu < 0.99) or (1 - q) - MARGIN <= connu:
                continue
            signaux += 1
            c0 = connu + 0.02
            if c0 < 0.99:
                g0 = not (b[0] <= final <= b[1])
                taux0 = 0.05
                ancien.append(dict(h=h, slug=slug, t=t, gain=((1.0 if g0 else 0.0) - c0 - taux0 * c0 * (1 - c0)) / c0,
                                   gagne=g0, paye=c0))
            paye = mk.apres(ts, APRES * 3600)
            if paye is None or not (0.01 <= paye < 0.99):
                sans_echange += 1
                continue
            taux = ((m.get("frais") or {}).get("rate")) if isinstance(m.get("frais"), dict) else None
            taux = 0.05 if taux is None else float(taux)
            gagne = not (b[0] <= final <= b[1])  # NON gagne si la tranche n'est pas la bonne
            fee = taux * paye * (1 - paye)
            gain = ((1.0 if gagne else 0.0) - paye - fee) / paye
            achats.append(dict(h=h, slug=slug, t=t, b=b, connu=connu, paye=paye, q=1 - q, gain=gain, gagne=gagne,
                               attendu=paye))
        t += timedelta(hours=6)


def resume(rows, label):
    if len(rows) < 5:
        print(f"  {label:32} {len(rows)} achats")
        return
    g = [r["gain"] for r in rows]
    ev = collections.defaultdict(list)
    for r in rows:
        ev[r["slug"]].append(r["gain"])
    pg = [st.mean(v) for v in ev.values()]
    tp = st.mean(pg) / st.stdev(pg) * math.sqrt(len(pg)) if len(pg) > 2 and st.stdev(pg) > 0 else float("nan")
    mois = collections.defaultdict(list)
    for r in rows:
        mois[r["t"].strftime("%m")].append(r["gain"])
    meilleurs = sorted(pg)[:-3]
    gagnes, attendus = sum(r["gagne"] for r in rows), sum(r["paye"] for r in rows)
    print(f"  {label:32} {len(g):5} achats {len(pg):3} périodes | par achat {st.mean(g):+.3f} | par période "
          f"{st.mean(pg):+.3f} (t {tp:+.2f}) | sans 3 meilleures {st.mean(meilleurs):+.3f} | gagnés {gagnes}/{attendus:.1f} | "
          + " ".join(f"{k}:{st.mean(v):+.2f}" for k, v in sorted(mois.items())))


print(f"réglage dispersion {DISP} marge {MARGIN} prix_min {MINP} avant {AVANT} h après {APRES} h ; règlement non relu : {len(ignores)} périodes écartées")
print(f"signaux NON {signaux}, sans échange dans les {APRES} h suivantes {sans_echange} ({sans_echange / max(signaux, 1):.0%})")
resume(achats, "NON, tous comptes")
resume([r for r in achats if r["h"] != "NYCMayor"], "NON sans NYC (A+D)")
for h in sorted({r["h"] for r in achats}):
    resume([r for r in achats if r["h"] == h], f"  {h}")
for lo, hi in ((0.1, 0.3), (0.3, 0.6), (0.6, 0.8), (0.8, 1.0)):
    resume([r for r in achats if r["h"] != "NYCMayor" and lo <= r["paye"] < hi], f"A+D payé {lo}-{hi}")
resume([r for r in ancien if r['h'] != 'NYCMayor'], 'TÉMOIN dernier prix connu + 0,02 (A+D)')
écart = [r["paye"] - r["connu"] for r in achats]
print(f"écart prix payé − prix connu : moyenne {st.mean(écart):+.3f}, médiane {st.median(écart):+.3f}")
json.dump([dict(r, t=r["t"].isoformat()) for r in achats], open(D / f"achats_{DISP}_{MARGIN}_{MINP}_{AVANT}_{APRES}.json", "w"))
