"""Famille 5 (14/11 soir) : compteur_tweets (mère) contre sa fille 72_168h et compteur_truth,
sur les MÊMES événements et jetons. Gagnés contre attendus (paiement), rendement par mise."""
import sys, collections
from decimal import Decimal as D
sys.path.insert(0, 'experiments/enquetes/scripts')
from charge_fantome import charger
B = 'published_data/ledger/fantome_v2/'
def st(ps):
    m = sum(p['mise'] for p in ps); g = sum(p['gain'] for p in ps)
    w = sum(p['pay'] for p in ps); e = sum(p['prix'] for p in ps)
    return f"{len(ps):3d} paris, {len({p['event'] for p in ps}):2d} évts, mise {m:7.1f}, gain {g:+7.1f} ({(g/m*100 if m else 0):+.1f} %), gagnés {w} pour {e:.2f} attendus"
mere = charger(B + 'compteur_tweets_v2.0.0.jsonl')
for fille in ('compteur_tweets_72_168h_v2.0.0', 'compteur_truth_v2.0.0'):
    f = charger(B + fille + '.jsonl')
    print('==', fille); print(' fille  :', st(f))
    debut = min(p['ts'] for p in f)
    mm = [p for p in mere if p['ts'] >= debut]
    print(' mère depuis la naissance :', st(mm))
    tm = {p['token'] for p in mere}; tf = {p['token'] for p in f}
    com = tm & tf
    print(' jetons communs', len(com), '| fille seule', len(tf - tm), '| mère seule (période)', len({p['token'] for p in mm} - tf))
    print('  fille sur communs :', st([p for p in f if p['token'] in com]))
    print('  mère  sur communs :', st([p for p in mere if p['token'] in com]))
    em = {p['event'] for p in mere}; ef = {p['event'] for p in f}
    ce = em & ef
    print(' événements communs', len(ce), '| fille seule', len(ef - em))
    print('  fille évts communs :', st([p for p in f if p['event'] in ce]))
    print('  mère  évts communs :', st([p for p in mere if p['event'] in ce]))
    print('  fille évts propres :', st([p for p in f if p['event'] not in em]))
    # sens opposés sur le même marché
    opp = [(p['market'], p['outcome']) for p in f for q in mere if p['market'] == q['market'] and p['outcome'] != q['outcome']]
    print('  marchés achetés en sens opposé :', len(set(opp)))

print('\n== moyenne des rendements par pari (ce que lit filles_periode) contre rendement pondéré')
import statistics
def moy(ps): return statistics.mean([float(p['gain'] / p['mise']) for p in ps]) if ps else float('nan')
for fille in ('compteur_tweets_72_168h_v2.0.0', 'compteur_truth_v2.0.0'):
    f = charger(B + fille + '.jsonl'); debut = min(p['ts'] for p in f); tf = {p['token'] for p in f}
    mm = [p for p in mere if p['ts'] >= debut]
    print(fille, f"fille moyenne {moy(f):+.1%}", f"| mère période {moy(mm):+.1%}",
          f"| mère sur jetons de la fille {moy([p for p in mm if p['token'] in tf]):+.1%}",
          f"| mère hors jetons de la fille {moy([p for p in mm if p['token'] not in tf]):+.1%}")
    print('   paris de la fille :', [(p['outcome'], round(float(p['prix']), 3), round(float(p['mise'])), round(float(p['gain']))) for p in f])
    print('   mère hors fille   :', st([p for p in mm if p['token'] not in tf]))
