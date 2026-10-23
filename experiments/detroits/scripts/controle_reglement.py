"""Contrôle du règlement : la série PortWatch téléchargée (version actuelle, révisions comprises) redonne-t-elle la tranche
gagnante officielle de chaque événement clos ? Et quand les marchés se règlent-ils (rythme de publication de PortWatch) ?
Usage : PYTHONPATH=src python experiments/detroits/scripts/controle_reglement.py"""
import collections
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import commun as c  # noqa: E402

inv = c.charge_inventaire()
series = {n: c.serie(n) for n in ("Strait of Hormuz", "Bab el-Mandeb Strait")}
res = collections.Counter()
retards = []
for ev in inv:
    if not ev["clos"] or ev["detroit"] not in series:
        continue
    cb = c.cible(ev)
    if not cb:
        continue
    type_, d = cb
    win = c.gagnant(ev)
    s7 = c.somme7(series[ev["detroit"]], d)
    if win is None or s7 is None:
        res["sans gagnant ou sans données"] += 1
        continue
    v = c.valeur(type_, s7)
    for lecture in ("plancher", "arrondi"):
        iv = c.intervalles(ev["questions"], lecture)
        mine = [k for k, (a, b) in iv.items() if a <= v < b]
        ok = mine == [win]
        res[(lecture, ok, "jusqu'à mai" if d < c.dt.date(2026, 6, 1) else "depuis juin")] += 1
        if not ok and lecture == "plancher":
            wq = next(q["question"] for q in ev["questions"] if q["id"] == win)
            print(f"ÉCART {ev['id']} {ev['detroit'][:6]} {d} {type_} valeur {v:.2f} ; officiel : {wq[:80]} ; intervalle {iv.get(win)}")
    close = [c.ts(q.get("closedTime")) for q in ev["questions"] if q.get("closedTime")]
    if close:
        t = min(close)
        retards.append(((t.date() - d).days, t.strftime("%a"), t.hour, ev["id"], str(d), type_))
print(dict(res))
print("clôture du premier marché de l'événement, en jours après la date D (jour de la semaine, heure UTC) :")
cnt = collections.Counter((r[0], r[1]) for r in retards)
for k, n in sorted(cnt.items()):
    print("  ", k, n)
heures = collections.Counter(r[2] for r in retards if r[1] == "Tue")
print("heures UTC des clôtures du mardi :", dict(sorted(heures.items())))
