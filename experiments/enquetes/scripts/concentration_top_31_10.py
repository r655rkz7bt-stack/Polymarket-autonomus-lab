"""31/10 : famille 2. Le gain des meilleures stratégies de l'arène résiste-t-il sans ses 3 plus gros paris,
son meilleur jour, son meilleur événement ? Gagnés (paiement) contre attendus (prix payés), un événement = un tirage."""
import sys, glob, math, collections
from decimal import Decimal as D
sys.path.insert(0, 'experiments/enquetes/scripts')
from charge_fantome import charger

NOMS = sys.argv[1:]
for nom in NOMS:
    fs = glob.glob(f'published_data/ledger/fantome/{nom}.jsonl')
    if not fs:
        print(nom, 'journal introuvable'); continue
    ps = charger(fs[0])
    if not ps:
        print(nom, 'aucun pari réglé'); continue
    g = sum(float(p['gain']) for p in ps); mise = sum(float(p['mise']) for p in ps)
    tri = sorted(ps, key=lambda p: -float(p['gain']))
    sans3 = g - sum(float(p['gain']) for p in tri[:3])
    jours = collections.defaultdict(float); evs = collections.defaultdict(float)
    for p in ps:
        jours[p['reglé_ts'][:10]] += float(p['gain']); evs[p['event'] or p['token']] += float(p['gain'])
    bj = max(jours, key=jours.get); be = max(evs, key=evs.get)
    pay = sum(float(p['pay']) for p in ps); att = sum(float(p['prix']) for p in ps)
    # z par événement
    byev = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    for p in ps:
        e = byev[p['event'] or p['token']]; e[0] += float(p['pay']); e[1] += float(p['prix']); e[2] += float(p['prix'] * (1 - p['prix']))
    num = sum(e[0] - e[1] for e in byev.values()); den = math.sqrt(sum(e[2] for e in byev.values())) or 1
    print(f"{nom}: {len(ps)} paris/{len(byev)} événements, gain {g:+.0f} € sur {mise:.0f} € misés ({100*g/mise:+.1f} %) | "
          f"sans les 3 plus gros {sans3:+.0f} | meilleur jour {bj} {jours[bj]:+.0f} → sans lui {g-jours[bj]:+.0f} | "
          f"meilleur événement {evs[be]:+.0f} → sans lui {g-evs[be]:+.0f} | payé {pay:.1f} pour {att:.1f} attendus (z événements {num/den:+.2f})")
