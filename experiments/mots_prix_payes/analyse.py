"""Mots prononcés (orateurs nommés) aux PRIX PAYÉS (23/10/2026) : refait le test de `MotsPrononces` (vingt_pistes.md : +19 % par achat,
t +2,8, prix CLOB deux heures après l'ouverture) avec les vrais échanges. Même règle : taux historique du mot chez l'orateur
(marchés RÉGLÉS avant l'instant de décision, mélangé au taux de l'orateur avec un poids K), achat quand il dépasse le prix payé de `marge`
et que le billet coûte au moins `prix_min` ; frais du barème Gamma ; +0,01 d'écart (comme le test du 21/10).
Instant de décision T = premier échange du marché + `delai` heures ; prix payé = premier échange du jeton (achat direct, ou vente de
l'autre issue) dans les `fenetre` heures qui suivent T ; aucun échange = pas d'achat.
Usage : python analyse.py <delai_h> <marge> <K> <min_precedents> <fenetre_h> [prix_min]"""
import bisect, collections, gzip, json, math, statistics as st, sys
from datetime import datetime
from pathlib import Path

D = Path("donnees")
A = sys.argv[1:]
DELAY, MARGIN, K, MINN, WIN = float(A[0]), float(A[1]), float(A[2]), int(A[3]), float(A[4])
MINP = float(A[5]) if len(A) > 5 else 0.30
SPREAD = 0.01


def ts(x):
    return datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() if x else None


rows = json.load(open(D / "rows.json"))["rows"]
for r in rows:
    r["c"] = ts(r["closed"] or r["end"]) or 0
cl = sorted(r["c"] for r in rows)
byc = sorted(rows, key=lambda r: r["c"])
cl = [r["c"] for r in byc]
todo = [r for r in byc if r["avant"] >= 3 and len(r["tok"]) == 2 and r["cond"] and r["sp"] not in ("the announcers", "anyone")]

achats, sans, vus = [], 0, 0
for r in todo:
    path = D / "cache" / f"{r['cond']}.json.gz"
    if not path.exists():
        continue
    tr = json.loads(gzip.decompress(path.read_bytes()))
    if not tr:
        continue
    t0 = min(t[0] for t in tr)
    T = t0 + DELAY * 3600
    if T > r["c"] - 3600:
        continue
    j = bisect.bisect_left(cl, T)
    prior = [x for x in byc[:j] if x["sp"] == r["sp"]]
    same = [x for x in prior if x["w"] == r["w"]]
    if len(same) < MINN or r["sp"].startswith('"'):
        continue
    vus += 1
    g = (sum(x["yes"] for x in prior) + 1) / (len(prior) + 2)
    q = (sum(x["yes"] for x in same) + K * g) / (len(same) + K)
    yes_t, no_t = r["tok"]
    for side, tok, other, qq in ((0, yes_t, no_t, q), (1, no_t, yes_t, 1 - q)):
        pts = sorted((t[0], t[3] if t[1] == tok else 1 - t[3]) for t in tr
                     if (t[1] == tok and t[2] == "BUY") or (t[1] == other and t[2] == "SELL"))
        i = bisect.bisect_left([a for a, _ in pts], T)
        if i >= len(pts) or pts[i][0] - T > WIN * 3600:
            sans += 1
            continue
        paid = pts[i][1] + SPREAD
        if not (MINP <= paid < 0.98) or qq - MARGIN <= paid:
            continue
        won = r["yes"] if side == 0 else not r["yes"]
        rate = float((r.get("fees") or {}).get("rate", 0.04) or 0.04) if isinstance(r.get("fees"), dict) else 0.04
        gain = ((1.0 if won else 0.0) - paid - rate * paid * (1 - paid)) / paid
        achats.append(dict(sp=r["sp"], ev=r["ev"], side=side, paid=paid, q=qq, won=won, gain=gain,
                           mois=datetime.fromtimestamp(T).strftime("%Y-%m")))


def resume(rows_, label):
    if len(rows_) < 5:
        print(f"  {label:28} {len(rows_)} achats")
        return
    g = [x["gain"] for x in rows_]
    ev = collections.defaultdict(list)
    for x in rows_:
        ev[x["ev"]].append(x["gain"])
    pe = [st.mean(v) for v in ev.values()]
    te = st.mean(pe) / st.stdev(pe) * math.sqrt(len(pe)) if len(pe) > 2 and st.stdev(pe) > 0 else float("nan")
    t = st.mean(g) / st.stdev(g) * math.sqrt(len(g))
    top = sorted(pe)[:-3]
    mois = collections.defaultdict(list)
    for x in rows_:
        mois[x["mois"]].append(x["gain"])
    print(f"  {label:28} {len(g):4} achats {len(pe):3} événements | par achat {st.mean(g):+.3f} (t {t:+.2f}) | par événement {st.mean(pe):+.3f} "
          f"(t {te:+.2f}) | sans 3 meilleurs événements {st.mean(top) if top else float('nan'):+.3f} | gagnés {sum(x['won'] for x in rows_)}/"
          f"{sum(x['paid'] for x in rows_):.1f} | " + " ".join(f"{k[2:]}:{st.mean(v):+.2f}" for k, v in sorted(mois.items())[-6:]))


print(f"délai {DELAY} h, marge {MARGIN}, K {K}, précédents ≥ {MINN}, fenêtre {WIN} h, billet ≥ {MINP} : {vus} marchés jugés, "
      f"{sans} côtés sans échange dans la fenêtre")
resume(achats, "tous")
resume([x for x in achats if x["side"] == 0], "OUI")
resume([x for x in achats if x["side"] == 1], "NON")
for lo, hi in ((0.3, 0.5), (0.5, 0.7), (0.7, 0.98)):
    resume([x for x in achats if lo <= x["paid"] < hi], f"payé {lo}-{hi}")
top = collections.Counter(x["sp"] for x in achats).most_common(4)
for sp, n in top:
    resume([x for x in achats if x["sp"] == sp], sp[:26])
