"""01/11 : famille 3. Les paris de compteur_truth (posts Truth Social) : bon marché, bon règlement ?
Relit chaque marché sur Gamma (question, tranche, résolution officielle) et le compare au paiement du journal."""
import sys, json, requests
sys.path.insert(0, 'experiments/enquetes/scripts')
from charge_fantome import charger
ps = charger('published_data/ledger/fantome/compteur_truth_v1.0.0.jsonl')
H = {'User-Agent': 'curl/8'}
for p in ps:
    r = requests.get(f"https://gamma-api.polymarket.com/markets/{p['market']}", headers=H, timeout=30).json()
    prix = json.loads(r.get('outcomePrices') or '[]'); outs = json.loads(r.get('outcomes') or '[]')
    off = dict(zip(outs, prix)).get(p['outcome'])
    print(f"{p['market']} {p['outcome']:>3} payé {float(p['prix']):.3f} pay journal {p['pay']} | Gamma {off} closed={r.get('closed')} | {r.get('question','')[:90]}")
