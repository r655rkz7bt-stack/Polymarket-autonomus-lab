"""Contrôle du règlement : le chiffre officiel des emplois (Kalshi `expiration_value`, publié par le BLS) tombe-t-il bien dans la tranche
Polymarket qui a été réglée « Oui » ? Un événement Kalshi = un mois de référence ; date de clôture Kalshi = heure de la publication."""
import json, re, collections, datetime as dt
K = json.load(open('experiments/emploi_nfp/donnees/kalshi_hist.json')) + json.load(open('experiments/emploi_nfp/donnees/kalshi.json'))
val = {}
for m in K:
    v = m.get('expiration_value') or m.get('settlement_value')
    if v: val[m['event_ticker']] = (float(str(v).replace(',', '')), (m.get('close_time') or '')[:16])
D = json.load(open('experiments/emploi_nfp/donnees/marches.json'))
MON = {m: i + 1 for i, m in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])}
byref = {}
for t, (v, close) in val.items():
    mm = re.search(r'(\d\d)([A-Z]{3})', t)
    if mm: byref[(2000 + int(mm.group(1)), MON[mm.group(2)])] = (v, close, t)
def bornes(b):
    """(min, max) en milliers à partir de l'étiquette Polymarket ; None si illisible."""
    s = b.replace(',', '').replace('–', '-').replace('−', '-').lower().replace(' ', '').replace('to', '-')
    nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', s)]
    if s.startswith('<') and nums: return (-1e9, nums[0])
    if (s.startswith(('>', '≥')) or s.endswith('+')) and nums: return (nums[0], 1e9)
    if len(nums) == 2: return (nums[0], nums[1])
    return None
ok = bad = skip = 0
for ev in sorted({r['event'] for r in D if r['kind'] == 'jobs'}):
    ms = [r for r in D if r['event'] == ev]; ref = ms[0]['ref']; win = [r for r in ms if r['yes_final'] > .5]
    if tuple(ref) not in byref: print(ref, 'pas de chiffre officiel Kalshi'); skip += 1; continue
    v, close, t = byref[tuple(ref)]; v /= 1000
    w = win[0]['bucket'] if win else '?'
    b = bornes(w)
    inside = b is not None and b[0] <= v < b[1] + 1e-9
    print(ref, f'officiel {v:7.1f}k  tranche réglée « {w} »  {"OK" if inside else "A VOIR" if b is None else "INCOHÉRENT"}  Kalshi clôt {close}  Polymarket release {ms[0]["release"][:16]}')
    ok += inside; bad += (not inside)
print('ok', ok, 'à voir/incohérent', bad, 'sans chiffre', skip)
