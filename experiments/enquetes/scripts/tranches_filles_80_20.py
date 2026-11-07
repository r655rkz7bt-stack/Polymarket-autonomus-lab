"""Relit les tranches proposées par l'entonnoir 80/20 sur le journal de la MÈRE, avec une date de coupure.

Usage : .venv/bin/python experiments/enquetes/scripts/tranches_filles_80_20.py [AAAA-MM-JJ]
Sans date : tout l'historique (là où la tranche a été choisie). Avec une date : seulement les paris RÉGLÉS
à partir de cette date, donc hors de l'échantillon où la tranche a été choisie (07/11/2026 : coupure 2026-11-08).
Les journaux viennent de `bash scripts/fetch_data.sh` (published_data/ledger/fantome/).
"""
import sys, math, collections
sys.path.insert(0, 'experiments/enquetes/scripts')
from charge_fantome import charger

DIR = 'published_data/ledger/fantome/'
COUPURE = sys.argv[1] if len(sys.argv) > 1 else '0000'

def horizon(p):
    return float(p['achats'][0][3].get('horizon_hours', 0))

def stats(ps, label):
    ps = [p for p in ps if p['reglé_ts'][:10] >= COUPURE]
    if not ps:
        print(f'{label}: 0 pari'); return
    g = sum(float(p['gain']) for p in ps); m = sum(float(p['mise']) for p in ps)
    won = sum(float(p['pay']) for p in ps); exp = sum(float(p['prix']) for p in ps)
    var = sum(float(p['prix']) * (1 - float(p['prix'])) for p in ps)
    z = (won - exp) / math.sqrt(var) if var else 0
    sans3 = g - sum(sorted(float(p['gain']) for p in ps)[-3:])
    jours = collections.defaultdict(float)
    for p in ps:
        jours[p['reglé_ts'][:10]] += float(p['gain'])
    print(f"{label}: n={len(ps)} événements={len({p['event'] for p in ps})} gain={g:.0f} rendement={g/m*100:.1f}% "
          f"gagnés {won:.1f}/{exp:.1f} z={z:.2f} sans les 3 plus gros={sans3:.0f} sans le meilleur jour={g-max(jours.values()):.0f}")

def prix(p):
    return float(p['prix'])

for mere, nom, dans in [
    ('crypto_non_10_20', 'délai 24-72 h', lambda p: 24 <= horizon(p) <= 72),
    ('contrer_crypto_audace', 'délai 72-168 h', lambda p: 72 <= horizon(p) <= 168),
    ('compteur_tweets', 'prix 0,45-0,60', lambda p: 0.45 <= prix(p) <= 0.6),
]:
    ps = charger(f'{DIR}{mere}_v1.0.0.jsonl')
    stats(ps, f'{mere} entière')
    stats([p for p in ps if dans(p)], f'{mere} {nom}')
    stats([p for p in ps if not dans(p)], f'{mere} hors {nom}')
