"""« Up or Down » du jour des actions et indices : le prix à H-k suit-il le cours intrajournalier ?

Modèle : p(Up) = Φ(r / σ_restant), r = ln(cours / clôture de la veille) au dernier bar fini, σ_restant = vol de 5 min observée
sur les 10 séances précédentes dans la même fenêtre horaire (jamais le jour même). Prix : achats de preneurs réels (taker_cost).
"""
import json, math, sys, bisect, collections, datetime as dt
from statistics import NormalDist
sys.path.insert(0, 'src')
from polymarket_agent import idea_test as it

Y = json.load(open('experiments/actions_jour/donnees/yahoo_5m.json'))
E = json.load(open('experiments/actions_jour/donnees/echanges.json'))
SYM = {'SPX': '^GSPC', 'SPY': 'SPY', 'RUT': '^RUT', 'DJIA': '^DJI', 'META': 'META', 'NVDA': 'NVDA', 'GOOGL': 'GOOGL', 'TSLA': 'TSLA', 'AAPL': 'AAPL', 'MSFT': 'MSFT',
       'AMZN': 'AMZN', 'PLTR': 'PLTR', 'NFLX': 'NFLX', 'HOOD': 'HOOD', 'COIN': 'COIN', 'RKLB': 'RKLB', 'OPEN': 'OPEN', 'MU': 'MU', 'ABNB': 'ABNB'}
Nd = NormalDist()
MONTHS = {m: i for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], 1)}

def jour(ts): return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime('%Y-%m-%d')

def prep(sym):
    y = Y[sym]; days = collections.OrderedDict()
    for t, c in zip(y['t'], y['c']):
        if c is None: continue
        d = jour(t); sod = t - (t % 86400)
        if 13 * 3600 + 1800 <= t - sod < 20 * 3600:        # séance régulière (EDT jusqu'au 1er novembre)
            days.setdefault(d, []).append((t, c))
    return days
P = {s: prep(v) for s, v in SYM.items()}

def etat(sym, d, T):
    """(cours au dernier bar fini avant T, clôture de la veille, σ restant) ou None."""
    days = P[sym]; ds = sorted(days)
    if d not in days: return None
    i = ds.index(d)
    if i < 11: return None
    prev = days[ds[i - 1]][-1][1]
    bars = days[d]; ts = [b[0] for b in bars]
    j = bisect.bisect_right(ts, T - 300) - 1
    if j < 0: return None
    S = bars[j][1]
    # σ restant : somme des carrés des rendements de 5 min après T-300 (même heure), 10 séances précédentes
    sig = []
    for dd in ds[i - 10:i]:
        b = days[dd]; sod = b[0][0] - (b[0][0] % 86400); Tl = sod + (T % 86400)
        tt = [x[0] for x in b]; k = bisect.bisect_right(tt, Tl - 300) - 1
        seg = [x[1] for x in b[max(k, 0):]]
        sig.append(sum(math.log(seg[m + 1] / seg[m]) ** 2 for m in range(len(seg) - 1)))
    s2 = sum(sig) / len(sig)
    return S, prev, math.sqrt(s2) if s2 > 0 else None, bars[-1][1]

def cas(delai_h):
    out = []
    for c in E:
        if c['ticker'] not in SYM: continue
        mo, dd = c['date'].split(); d = f"2026-{MONTHS[mo]:02d}-{int(dd):02d}"
        if d not in P[SYM[c['ticker']]]: continue
        sod = int(dt.datetime.strptime(d, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp())
        T = sod + 20 * 3600 - int(delai_h * 3600)
        st = etat(SYM[c['ticker']], d, T)
        if not st or not st[2]: continue
        S, prev, sig, clo = st
        r = math.log(S / prev)
        pm = Nd.cdf(r / sig)                      # p(Up) du modèle
        up, dn = c['tokens']
        tr = [[x['ts'], up if x['o'] == c['outcomes'][0] else dn, x['side'], x['p'], x['s']] for x in c['trades']]
        won_up = float(c['prices'][0]) > 0.99; won_dn = float(c['prices'][1]) > 0.99
        pay_up = float(c['prices'][0])
        out.append(dict(c=c, d=d, T=T, r=r, sig=sig, pm=pm, tr=tr, up=up, dn=dn, pay_up=pay_up, clo=clo, S=S, prev=prev))
    return out

def run(delai_h, marge, fenetre=3600):
    cs = cas(delai_h); bets = []; n_prix = 0; ll_m = ll_p = 0
    for x in cs:
        ask_up = it.taker_cost(x['tr'], x['up'], x['dn'], x['T'], window=fenetre, after=True)
        ask_dn = it.taker_cost(x['tr'], x['dn'], x['up'], x['T'], window=fenetre, after=True)
        last_up = it.taker_cost(x['tr'], x['up'], x['dn'], x['T'], window=fenetre, after=False)
        if last_up is not None:
            n_prix += 1; pu = min(.99, max(.01, last_up)); pmv = min(.99, max(.01, x['pm']))
            y = x['pay_up']; ll_m += -(y * math.log(pmv) + (1 - y) * math.log(1 - pmv)); ll_p += -(y * math.log(pu) + (1 - y) * math.log(1 - pu))
        # pari du côté que le modèle juge sous-coté de plus de `marge`
        for cote, ask, pm_c, pay in (('Up', ask_up, x['pm'], x['pay_up']), ('Down', ask_dn, 1 - x['pm'], 1 - x['pay_up'])):
            if ask is None or ask >= 0.99: continue
            if pm_c - ask < marge: continue
            gain = (pay - ask) / ask            # 0 frais (feeSchedule.rate = 0), 1 euro misé
            bets.append(dict(gain=gain, evenement=x['c']['event'], mois=x['d'][:7], cout=ask, cote=cote, ticker=x['c']['ticker'], d=x['d']))
    return cs, bets, n_prix, ll_m, ll_p

if __name__ == '__main__':
    print('marchés pris:', len(E))
    for h in (1, 2, 3, 4, 5, 6):
        cs = cas(h)
        print(f'--- H-{h} : {len(cs)} cas modélisés')
        for marge in (0.03, 0.06, 0.10):
            cs, bets, n, lm, lp = run(h, marge)
            if bets:
                v = it.verdict(bets)
                print(f'marge {marge:.2f}: {len(bets)} paris, rendement {100*sum(b["gain"] for b in bets)/len(bets):+.1f} %, verdict {v.get("verdict")}, t événement {v.get("t_evenement")}, z prix {v.get("z_prix")}')
            else: print(f'marge {marge:.2f}: aucun pari')
        print(f'  log-loss modèle {lm/max(n,1):.3f} contre prix {lp/max(n,1):.3f} sur {n} marchés avec un échange récent')
