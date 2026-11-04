"""Piste 15, suite : comptage officiel de la Caroline du Nord (NCSBE, `dl.ncsbe.gov/ENRS/2026_11_03/results_pct_20261103.zip`,
sans clé). Toutes les INTERVALLE secondes : `Last-Modified` du fichier ; s'il a changé, le télécharge et note les votes
totaux par candidat du Sénat (« US SENATE ») et les précincts qui ont au moins un vote. Une ligne par changement dans
`releve_nc.jsonl`. Usage : python releve_nc.py [minutes=90] [intervalle=60]"""
import io, json, os, re, sys, time, zipfile, datetime as dt, collections
import requests

H = {'User-Agent': 'curl/8'}
URL = 'https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/results_pct_20261103.zip'
SORTIE = os.path.join(os.path.dirname(__file__), 'releve_nc.jsonl')
COURSES = ('US SENATE',)  # + toutes les circonscriptions « US HOUSE OF REPRESENTATIVES DISTRICT nn »


def lire(contenu):
    z = zipfile.ZipFile(io.BytesIO(contenu))
    texte = z.read(z.namelist()[0]).decode('utf-8', 'replace').splitlines()
    en = texte[0].split('\t')
    i = {n: k for k, n in enumerate(en)}
    votes = collections.defaultdict(lambda: collections.defaultdict(int))
    pcts = collections.defaultdict(lambda: collections.defaultdict(int))
    tous = collections.defaultdict(set)
    for l in texte[1:]:
        c = l.split('\t')
        if len(c) < len(en) or not (c[i['Contest Name']] in COURSES or c[i['Contest Name']].startswith('US HOUSE')):
            continue
        nom = c[i['Contest Name']]; v = int(c[i['Total Votes']] or 0)
        votes[nom][c[i['Choice']] + ' ' + c[i['Choice Party']]] += v
        pcts[nom][(c[i['County']], c[i['Precinct']])] += v
        tous[nom].add((c[i['County']], c[i['Precinct']]))
    return {n: dict(votes=dict(votes[n]), precincts=len(tous[n]), avec_votes=sum(1 for p, v in pcts[n].items() if v > 0)) for n in votes}


if __name__ == '__main__':
    minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 90
    pas = float(sys.argv[2]) if len(sys.argv) > 2 else 60
    fin = time.time() + minutes * 60
    vu = None
    vus_liste = None
    while True:
        ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
        try:
            liste = requests.get('https://s3.amazonaws.com/dl.ncsbe.gov/?prefix=ENRS/2026_11_03/', headers=H, timeout=30).text
            neufs = sorted(set(re.findall(r'<Key>([^<]*)</Key><LastModified>(2026-11-0[45][^<]*)', liste)), key=lambda t: t[1])[-5:]
            if neufs != vus_liste:
                vus_liste = neufs
                print(ts, 'fichiers récents', neufs, flush=True)
            lm = requests.head(URL, headers=H, timeout=30).headers.get('Last-Modified')
            if lm != vu:
                vu = lm
                r = requests.get(URL, headers=H, timeout=120)
                with open(SORTIE, 'a') as f:
                    f.write(json.dumps(dict(ts=ts, last_modified=lm, courses=lire(r.content))) + '\n')
                print(ts, 'changé', lm, flush=True)
        except Exception as x:
            print(ts, 'erreur', str(x)[:80], flush=True)
        if time.time() + pas > fin:
            break
        time.sleep(pas)
