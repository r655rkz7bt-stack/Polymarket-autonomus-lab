"""Relevé en direct : événements « neg-risk » (issues exclusives) ouverts. Panier de tous les OUI (coût = somme des
meilleurs vendeurs, paie 1 si l'événement est complet) et panier de tous les NON (coût = somme des vendeurs NON, paie n-1).
On regarde l'écart au carnet (bestAsk de Gamma), avant frais, puis on relit les carnets CLOB des meilleurs candidats."""
import requests, json, sys
H = {'User-Agent': 'curl/8'}
G = 'https://gamma-api.polymarket.com'
cur = None; evs = []
for _ in range(60):
    p = {'closed': 'false', 'limit': 500, 'order': 'volume24hr', 'ascending': 'false'}
    if cur: p['after_cursor'] = cur
    r = requests.get(G + '/events/keyset', params=p, headers=H, timeout=60).json()
    evs += r.get('events', [])
    cur = r.get('next_cursor')
    if not cur or len(evs) >= 6000: break
print(len(evs), 'événements ouverts lus')
rows = []
for e in evs:
    if not e.get('negRisk'): continue
    ms = [m for m in e.get('markets', []) if m.get('active') and not m.get('closed') and m.get('acceptingOrders', True)]
    if len(ms) < 2: continue
    asks = [m.get('bestAsk') for m in ms]; bids = [m.get('bestBid') for m in ms]
    if any(a is None for a in asks): continue
    sy = sum(float(a) for a in asks)
    sb = sum(float(b) for b in bids if b is not None)
    rows.append((sy, sb, len(ms), e.get('slug'), float(e.get('liquidity') or 0), e.get('enableNegRisk'), e.get('negRiskAugmented')))
rows.sort()
print(len(rows), 'événements neg-risk complets')
print('plus bas total des OUI (acheter tous les OUI paie 1 si le champ est complet) :')
for r in rows[:12]: print('  somme asks %.3f somme bids %.3f n=%d liq=%.0f aug=%s %s' % (r[0], r[1], r[2], r[4], r[6], r[3]))
print('plus haut total des bids (vendre tous les OUI) :')
for r in sorted(rows, key=lambda r: -r[1])[:12]: print('  somme asks %.3f somme bids %.3f n=%d liq=%.0f aug=%s %s' % (r[0], r[1], r[2], r[4], r[6], r[3]))
