"""Stocks d'urgence UE de gazole (Eurostat nrg_stk_oilm, STKCL_EUE, O4671, milliers de tonnes, robots.txt permis le 14/11/2026).
Variation sur h mois (h = 3 : août → novembre ; h = 4 : juillet → novembre) depuis 2010, et dérive récente."""
import requests, statistics, sys
H = {'User-Agent': 'curl/8'}
U = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_stk_oilm'
d = requests.get(U, params=dict(geo='EU27_2020', siec='O4671', unit='THS_T', stk_flow='STKCL_EUE', sinceTimePeriod='2008-01'), headers=H, timeout=60).json()
tk = d['dimension']['time']['category']['index']
s = {t: d['value'].get(str(i)) for t, i in tk.items()}
T = [t for t in sorted(s) if s[t] is not None]
print('premier', T[0], 'dernier', T[-1], s[T[-1]])
for h in (3, 4):
    ch = [s[T[i + h]] - s[T[i]] for i in range(len(T) - h)]
    rec = ch[-36:]
    q = sorted(ch)
    print(f"h={h}: n={len(ch)} moyenne {statistics.mean(ch):+.0f} écart-type {statistics.stdev(ch):.0f} ; 36 derniers : moyenne {statistics.mean(rec):+.0f} écart-type {statistics.stdev(rec):.0f} ; "
          f"5 % {q[int(.05*len(q))]:+.0f} 95 % {q[int(.95*len(q))]:+.0f} ; min {q[0]:+.0f}")
    base = float(sys.argv[1]) if len(sys.argv) > 1 else 37164
    for seuil in (35000, 36000, 37000):
        p_all = sum(base + c >= seuil for c in ch) / len(ch); p_rec = sum(base + c >= seuil for c in rec) / len(rec)
        print(f"   depuis {base:.0f} : P(≥ {seuil}) tous {p_all:.2f}, 36 derniers {p_rec:.2f}")

print('\nsaison : août → novembre et juillet → novembre, année par année')
aa = []
for y in range(2013, 2026):
    a, j, n = s.get(f'{y}-08'), s.get(f'{y}-07'), s.get(f'{y}-11')
    if a and n:
        aa.append(n - a); print(y, f"août {a:.0f} → nov {n:.0f} : {n - a:+.0f} ; juil → nov {n - j:+.0f}")
print(f"août → nov : moyenne {statistics.mean(aa):+.0f}, écart-type {statistics.stdev(aa):.0f}, 5 dernières {statistics.mean(aa[-5:]):+.0f}")
