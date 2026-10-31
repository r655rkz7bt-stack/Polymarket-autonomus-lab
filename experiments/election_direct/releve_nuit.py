"""Piste 15 : relevé en direct de la nuit d'élection (03/11/2026), Géorgie.

Toutes les INTERVALLE secondes : (1) le JSON officiel `results.sos.ga.gov/cdn/results/Georgia/export-<AAAA><Mois>Gen.json`
(courses d'État : gouverneur, Sénat, secrétaire d'État, etc.), (2) le prix de chaque candidat sur les marchés Polymarket
« georgia-governor-winner-2026 » (événement 57161) et « georgia-senate-election-winner » (57642).
Une ligne par relevé dans `releve_nuit.jsonl` (versionné : le passage suivant repart d'un clone neuf).
Usage : python releve_nuit.py [minutes=60] [intervalle=90] [--fichier chemin.json (test sur 2024)]"""
import json, os, sys, time, datetime as dt
import requests

H = {'User-Agent': 'curl/8'}
EVENTS = {'gouverneur': 57161, 'senat': 57642}
COURSES = ('Governor', 'US Senate', 'Senate', 'Secretary of State', 'Attorney General', 'Lieutenant Governor', 'President')
SORTIE = os.path.join(os.path.dirname(__file__), 'releve_nuit.jsonl')
MOIS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def url_ga(annee=2026):
    return f'https://results.sos.ga.gov/cdn/results/Georgia/export-{annee}NovGen.json'


def lire_ga(source):
    """Rend {course: {'reporting': (x, y), 'votes': {candidat: n}}} pour les courses d'État voulues, ou None."""
    if source.startswith('http'):
        r = requests.get(source, headers=H, timeout=60)
        if r.status_code != 200:
            return {'http': r.status_code}
        d = r.json()
    else:
        d = json.load(open(source))
    out = {}
    for b in d['results']['ballotItems']:
        if b.get('type') == 'State' and not b['name'].startswith('State ') and any(c.lower() in b['name'].lower() for c in COURSES):
            out[b['name']] = dict(reporting=(b.get('precinctsReporting'), b.get('precinctsParticipating')),
                                  votes={o['name']: o.get('voteCount') for o in b['ballotOptions']})
    return {'creation': d.get('createdAt'), 'courses': out}


def prix_polymarket():
    out = {}
    for nom, ev in EVENTS.items():
        try:
            e = requests.get(f'https://gamma-api.polymarket.com/events/{ev}', headers=H, timeout=30).json()
            out[nom] = {m.get('groupItemTitle') or m['question']: json.loads(m['outcomePrices'])[0] for m in e['markets']
                        if m.get('outcomePrices') and not m.get('closed')}
        except Exception as x:  # un relevé manqué ne doit pas arrêter la nuit
            out[nom] = {'erreur': str(x)[:80]}
    return out


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    fichier = sys.argv[sys.argv.index('--fichier') + 1] if '--fichier' in sys.argv else None
    if fichier and fichier in args: args.remove(fichier)
    minutes = float(args[0]) if args else 60
    pas = float(args[1]) if len(args) > 1 else 90
    fin = time.time() + minutes * 60
    while True:
        ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
        try:
            ga = lire_ga(fichier or url_ga())
        except Exception as x:
            ga = {'erreur': str(x)[:80]}
        ligne = dict(ts=ts, ga=ga, prix=prix_polymarket())
        with open(SORTIE, 'a') as f:
            f.write(json.dumps(ligne) + '\n')
        print(ts, 'GA', (ga or {}).get('http') or ('ok' if 'courses' in ga else ga), flush=True)
        if time.time() + pas > fin or fichier:
            break
        time.sleep(pas)
