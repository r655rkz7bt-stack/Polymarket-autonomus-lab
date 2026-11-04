"""Piste 15, suite : bande de prix de la nuit d'élection (04/11/2026). Toutes les INTERVALLE secondes, le prix OUI de chaque
marché non clos des événements d'élection les plus échangés (étiquette `midterms` 102289, 40 premiers par volume du jour),
une ligne par relevé dans `bande_prix_nuit.jsonl` (versionné). Sert à dater le moment où le marché « sait » (premier passage
à >= 0,95 puis plus de retour sous 0,90), à comparer aux comptages officiels relevés par `releve_nuit.py`.
Usage : python bande_prix_nuit.py [minutes=90] [intervalle=120]"""
import json, os, sys, time, datetime as dt
import requests

H = {'User-Agent': 'curl/8'}
SORTIE = os.path.join(os.path.dirname(__file__), 'bande_prix_nuit.jsonl')


def evenements(n=40):
    r = requests.get('https://gamma-api.polymarket.com/events/keyset',
                     params=dict(tag_id=102289, closed='false', order='volume24hr', ascending='false', limit=n), headers=H, timeout=60).json()
    return [e['id'] for e in (r.get('events', r) if isinstance(r, dict) else r)]


def releve(ids):
    out = {}
    for i in ids:
        try:
            e = requests.get(f'https://gamma-api.polymarket.com/events/{i}', headers=H, timeout=30).json()
            out[i] = {(m.get('groupItemTitle') or m['question'])[:40]: json.loads(m['outcomePrices'])[0]
                      for m in e['markets'] if m.get('outcomePrices') and not m.get('closed')}
        except Exception as x:
            out[i] = {'erreur': str(x)[:60]}
    return out


if __name__ == '__main__':
    minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 90
    pas = float(sys.argv[2]) if len(sys.argv) > 2 else 120
    fin = time.time() + minutes * 60
    ids = evenements()
    while True:
        ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
        with open(SORTIE, 'a') as f:
            f.write(json.dumps(dict(ts=ts, prix=releve(ids))) + '\n')
        print(ts, len(ids), flush=True)
        if time.time() + pas > fin:
            break
        time.sleep(pas)
