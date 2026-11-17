"""Piste n° 65, barrières (17/11/2026) : jeton Polymarket de chaque sous-jacent, lu dans les échantillons publiés par l indice -> tokens.json."""
import json, requests, gzip
s = requests.Session(); s.headers['User-Agent'] = 'polymarket-autonomous-lab'
B='https://predictionmarketodds.com/'
d=s.get(B+'latest.json',timeout=30).json()
MAP={'Republican House':('house_control_2026','republican_party'),'Republican Senate':('senate_control_2026','republican_party'),
 'Talarico':('senate_texas_2026',None),'Ossoff':('dem_nomination_2028','jon_ossoff'),'Newsom':('dem_nomination_2028','gavin_newsom'),
 'Rubio':('gop_nomination_2028','marco_rubio'),'Vance':('gop_nomination_2028','jd_vance'),'Democratic 2028 presidential':('president_2028_party','democratic_party'),
 "AOC":('dem_nomination_2028','alexandria_ocasio_cortez'),'Carlson':('gop_nomination_2028','tucker_carlson'),'Shapiro':('dem_nomination_2028','josh_shapiro'),
 'Buttigieg':('dem_nomination_2028','pete_buttigieg'),'DeSantis':('gop_nomination_2028','ron_desantis'),'Harris':('dem_nomination_2028','kamala_harris'),
 'Trump Jr':('gop_nomination_2028','donald_trump_jr'),'trifecta':('democratic_trifecta_2028','democratic_trifecta'),"Le Pen":('france_president_2027','marine_le_pen'),
 'You Can See Everything':('oscars_best_picture_2027','you_can_see_everything')}
prints={(p['market_set_id'],p['candidate_id']):p for p in d['prints']}
print([k for k in prints if k[0]=='senate_texas_2026' or k[0]=='house_control_2026'])
out={}
for name,(ms,c) in MAP.items():
    cands=[k for k in prints if k[0]==ms and (c is None or k[1]==c)]
    for k in cands:
        p=prints[k]; ev=p.get('sample_evidence') or {}
        det=s.get(B+p['detail_path'],timeout=30).json(); ev=det.get('sample_evidence') or {}
        raw=s.get(B+ev['path'],timeout=30).content
        try: raw=gzip.decompress(raw)
        except OSError: pass
        smp=json.loads(raw)['samples']
        pm=[x for x in smp if x.get('venue_id')=='polymarket']
        tok=pm[0]['extra'].get('token_id') if pm else None
        out[name+'|'+k[1]]={'set':ms,'cand':k[1],'token':tok,'market':pm[0]['extra'].get('market_id') if pm else None,'valeur':p['print'].get('value'),
                  'histo':[(h.get('window_end') or (h.get('calculation') or {}).get('window_end'), (h.get('print') or {}).get('value') or (h.get('calculation') or {}).get('published_value')) for h in det.get('history') or []]}
        print(name,k[1],p['print'].get('value'),tok and tok[:12], pm[0]['extra'].get('market_id') if pm else None)
json.dump(out,open('tokens.json','w'))
