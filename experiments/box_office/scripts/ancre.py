"""Même test, mais l'heure est ancrée sur le week-end (dimanche 00 h UTC précédant la fin) et non sur la fin du marché, dont l'heure varie."""
import sys
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
import favori
from favori import *
from datetime import timedelta
def sunday0(end):
    d = datetime.fromtimestamp(end, timezone.utc)
    s = (d - timedelta(days=(d.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)  # dimanche (weekday 6) <= d
    return int(s.timestamp())
orig = [dict(c) for c in favori.C]
for off in (-72, -48, -36, -24, -12, 0, 12):
    favori.C[:] = [dict(c, end=sunday0(c["end"]) - off * 3600) for c in orig]  # h heures avant "fin" fictive = ancre + off
    for h in (0,):
        b = favori.run(h, 0.5, 1.0) if False else favori.run(0, 0.5, 1.0)
        if len(b) < 15: continue
        v = verdict(b)
        print(f"ancre = dimanche 00 h UTC {off:+d} h : n={v['paris']} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} gagnés/attendus {sum(1 for x in b if x['gain']>0)}/{sum(x['cout'] for x in b):.1f} z_prix {v['z_prix']:+.2f}")
