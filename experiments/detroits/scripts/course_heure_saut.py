"""Quand le marché apprend-il le résultat ? Pour chaque événement hebdomadaire réglé : heure (UTC, jour de la semaine) du premier
échange où le côté gagnant s'achète ≥ 0,95 après un échange ≤ 0,80 sur le même marché, entre D+1 et le règlement ; et liquidité
réellement échangée sous 0,97 entre la publication supposée (mardi 11 h) + délai et +1 h. Usage : PYTHONPATH=src python …"""
import collections, datetime as dt, gzip, json, sys
from pathlib import Path
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import commun as c
inv = c.charge_inventaire()
series = {n: c.serie(n) for n in ("Strait of Hormuz", "Bab el-Mandeb Strait")}
jours = collections.Counter(); heures = collections.Counter(); rows = []
tot = collections.defaultdict(lambda: [0.0, 0.0, 0])
for ev in inv:
    cb = c.cible(ev)
    if not ev["clos"] or ev["detroit"] not in series or not cb or cb[1] < dt.date(2026, 6, 1):
        continue
    win = c.gagnant(ev)
    f = Path(c.DONNEES) / "echanges" / f"echanges_{ev['id']}.json.gz"
    if win is None or not f.exists():
        continue
    tr = json.loads(gzip.decompress(f.read_bytes()))
    D = cb[1]
    pub = dt.datetime.combine(D + dt.timedelta(days=2), dt.time(11), tzinfo=dt.timezone.utc)
    while c.connu_jusqua(pub, 11) < D:
        pub += dt.timedelta(days=1)
    iv = c.intervalles(ev["questions"], "plancher")
    sauts = []
    for q in ev["questions"]:
        if q["id"] not in iv:
            continue
        yes, no = json.loads(q["clobTokenIds"])
        tok, oth = (yes, no) if q["id"] == win else (no, yes)
        pts = sorted((t[0], t[3] if t[1] == tok else 1 - t[3], t[4]) for t in tr
                     if (t[1] == tok and t[2] == "BUY") or (t[1] == oth and t[2] == "SELL"))
        pts = [p for p in pts if p[0] >= int(dt.datetime.combine(D + dt.timedelta(days=1), dt.time(), tzinfo=dt.timezone.utc).timestamp())]
        bas = False
        for t, p, s in pts:
            if p <= 0.80: bas = True
            elif p >= 0.95 and bas:
                sauts.append(t); break
        for delai in (0, 0.5, 1.0):
            t0 = int(pub.timestamp()) + int(delai * 3600)
            for t, p, s in pts:
                if t0 <= t <= t0 + 3600 and p < 0.97:
                    tot[delai][0] += s * (1 - p); tot[delai][1] += s * p; tot[delai][2] += 1
    if sauts:
        d = dt.datetime.fromtimestamp(min(sauts), dt.timezone.utc)
        jours[d.strftime("%a")] += 1; heures[d.hour] += 1
        rows.append((ev["id"], D.isoformat(), d.strftime("%a %H:%M"), (min(sauts) - pub.timestamp()) / 3600))
print("jour du premier saut du marché :", dict(jours)); print("heure UTC :", dict(sorted(heures.items())))
for r in rows: print(r)
for dl, (g, m, n) in tot.items():
    print(f"délai {dl} h après 11 h : {n} échanges sous 0,97 dans l'heure, gain théorique {g:.0f} $ pour {m:.0f} $ misés ({g/m:+.1%}) sur toute la période")
