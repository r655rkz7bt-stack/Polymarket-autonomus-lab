"""Achat du NON à J-30, J-14, J-7 avant la fin, par famille (returns to normal / any day), sans frais ni écart (premier regard)."""
import json, datetime as dt, collections, bisect
d = json.load(open("experiments/detroits_seuils/releves/seuils.json"))
fam = lambda x: "normal" if "normal" in x["titre"].lower() else "anyday"
for f in ("normal", "anyday"):
    print("==", f)
    for jours in (30, 14, 7, 3):
        pas = []
        for x in d:
            if fam(x) != f or not x["prix"] or not x["fin"]: continue
            t_fin = dt.datetime.fromisoformat(x["fin"].replace("Z", "+00:00")).timestamp()
            ts = [p[0] for p in x["prix"]]
            T = t_fin - jours * 86400
            if T < ts[0]: continue
            i = bisect.bisect_right(ts, T) - 1
            oui = x["prix"][i][1]
            non = 1 - oui
            if non <= 0.02 or non >= 0.995: continue
            pas.append((x["event"], x["question"][:40], oui, 1 - x["regl"]))
        if not pas: continue
        cout = sum(1 - p[2] for p in pas); gain = sum(p[3] for p in pas)
        par_ev = collections.defaultdict(list)
        for p in pas: par_ev[p[0]].append(p)
        print(f"J-{jours}: {len(pas)} NON, {len(par_ev)} événements, prix moyen NON {cout/len(pas):.3f}, payé {gain/len(pas):.3f}, rendement {gain/cout-1:+.1%}, OUI gagnés {sum(1 for p in pas if p[3]==0)}")
