"""Identité comptable de chaque journal signé (04/11/2026, soir) : on rejoue BUY / SELL / SETTLE depuis 1 000 et on compare
au dernier cash du journal (HEARTBEAT) ; on cherche aussi les règlements doubles, les règlements de parts jamais achetées,
les parts vendues en trop et les paiements hors {0, 0,5, 1}."""
import json, glob, sys, collections
from decimal import Decimal as D
def rejouer(chemin):
    cash = D(0); det = collections.defaultdict(D); regle = collections.Counter(); anomalies = []; hb = None; genesis = None
    for l in open(chemin):
        x = json.loads(l); d = x['data']; t = x['type']
        if t == 'GENESIS': cash = genesis = D(d['initial_capital'])
        elif t == 'BUY':
            cash -= D(d['price']) * D(d['shares']) + D(d['fee']); det[d['token_id']] += D(d['shares'])
        elif t == 'SELL':
            cash += D(d['price']) * D(d['shares']) - D(d['fee']); det[d['token_id']] -= D(d['shares'])
            if det[d['token_id']] < 0: anomalies.append(('vente_en_trop', d['token_id'][:10], str(det[d['token_id']])))
        elif t == 'SETTLE':
            tok = d['token_id']; pay = D(d['payout_per_share']); regle[tok] += 1
            if regle[tok] > 1: anomalies.append(('double_reglement', tok[:10]))
            if pay not in (D(0), D('0.5'), D(1)): anomalies.append(('paiement_bizarre', tok[:10], str(pay)))
            sh = D(d.get('shares', det[tok])) if 'shares' in d else det[tok]
            if det[tok] <= 0: anomalies.append(('reglement_sans_parts', tok[:10]))
            cash += det[tok] * pay; det[tok] = 0
        elif t == 'HEARTBEAT': hb = D(d['cash'])
    return cash, hb, anomalies, genesis
if __name__ == '__main__':
    lots = [('principal', 'published_data/ledger/ledger.jsonl')] + [(p.split('/')[-1][:-6] if p.endswith('.jsonl') else p.split('/')[-1], p) for p in sorted(glob.glob('published_data/ledger/fantome/*'))]
    mal = 0
    for nom, p in lots:
        if p.endswith('/'): continue
        import os
        if os.path.isdir(p):
            cand = glob.glob(p + '/*.jsonl'); 
            if not cand: continue
            p = cand[0]
        cash, hb, an, g = rejouer(p)
        ecart = None if hb is None else cash - hb
        if an or (ecart is not None and abs(ecart) > D('0.01')):
            mal += 1; print(nom, 'rejoué', cash.quantize(D('0.01')), 'journal', hb, 'écart', ecart, an[:4])
    print(len(lots), 'journaux, écarts ou anomalies :', mal)
