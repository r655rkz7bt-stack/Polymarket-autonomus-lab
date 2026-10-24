import sys
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
import favori
from favori import *
from datetime import datetime
full = list(favori.C)
for nom, f in (("fin lundi 12 h", lambda c: datetime.fromtimestamp(c["end"], timezone.utc).strftime("%a%H") == "Mon12"),
               ("fin dimanche (12 h ou 23 h)", lambda c: datetime.fromtimestamp(c["end"], timezone.utc).strftime("%a") == "Sun"),
               ("autres", lambda c: datetime.fromtimestamp(c["end"], timezone.utc).strftime("%a%H") not in ("Mon12",) and datetime.fromtimestamp(c["end"], timezone.utc).strftime("%a") != "Sun")):
    favori.C[:] = [c for c in full if f(c)]
    print(nom, len(favori.C), "événements")
    for h in (48, 36, 24, 12):
        b = favori.run(h, .5, 1.0)
        if len(b) >= 8:
            v = verdict(b); print(f"  h={h}: n={v['paris']} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} gagnés/attendus {sum(1 for x in b if x['gain']>0)}/{sum(x['cout'] for x in b):.1f}")
