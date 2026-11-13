"""Baton Rouge (USGS 07374000, moyenne du jour) : après une onde sur des basses eaux, combien de jours entre la crête et le retour
sous (plus bas d'avant l'onde − marge) ? Sert à juger le marché « 6 ft ou plus d'ici le 30/11 » du 13/11/2026 (plus bas 6,38 le
09/11, onde annoncée à 8,4 ft vers le 22-23/11 : il faudrait passer sous 6,00 en ≈ 8 jours après la crête).
Onde : plus bas L (minimum local sur ±10 j, L ≤ 12 ft), puis crête C ≥ L + montée_min dans les 20 jours suivants (maximum avant
la redescente). Mesure : jours entre la crête et le premier jour < L − marge (None si pas dans les 40 jours).
Usage : python ondes_baton_rouge.py donnees/btr_moy.json [montée_min=1.0] [marge=0.38]"""
import json, sys, datetime as dt

v = json.load(open(sys.argv[1]))['value']['timeSeries'][0]['values'][0]['value']
s = {dt.date.fromisoformat(x['dateTime'][:10]): float(x['value']) for x in v if x['value'] not in ('', '-999999')}
montee = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
marge = float(sys.argv[3]) if len(sys.argv) > 3 else 0.38
jours = sorted(s)
res = []
derniere = None
for d in jours:
    if d.year >= 2026 or s[d] > 12:
        continue
    voisins = [s.get(d + dt.timedelta(days=k)) for k in range(-10, 11)]
    if any(x is None for x in voisins) or s[d] > min(voisins):
        continue
    if derniere and (d - derniere).days < 15:
        continue
    L = s[d]
    # crête : maximum des 20 jours suivants
    fen = [(d + dt.timedelta(days=k), s.get(d + dt.timedelta(days=k))) for k in range(1, 21)]
    fen = [(x, y) for x, y in fen if y is not None]
    if not fen:
        continue
    dc, C = max(fen, key=lambda p: p[1])
    if C < L + montee:
        continue
    derniere = d
    retour = None
    for k in range(1, 41):
        y = s.get(dc + dt.timedelta(days=k))
        if y is not None and y < L - marge:
            retour = k
            break
    res.append((d, L, dc, C, retour))
print(f"{len(res)} ondes (montée ≥ {montee} pi, plus bas ≤ 12 pi), retour sous plus bas − {marge}")
for d, L, dc, C, r in res:
    print(f"  {d} plus bas {L:5.2f} → crête {dc} {C:5.2f} (+{C-L:4.2f}) ; retour sous {L-marge:5.2f} : {r if r is not None else '> 40'} j")
ok = [r for *_, r in res]
for seuil in (8, 10, 14):
    n = sum(1 for r in ok if r is not None and r <= seuil)
    print(f"retour en ≤ {seuil} j après la crête : {n} sur {len(ok)}")
# même chose pour les ondes de taille comparable (+1,5 à +3 pi)
sel = [(L, C, r) for _, L, _, C, r in res if 1.5 <= C - L <= 3.0]
print(f"ondes de +1,5 à +3 pi : {len(sel)} ; retour en ≤ 8 j : {sum(1 for *_, r in sel if r is not None and r <= 8)} ; ≤ 10 j : {sum(1 for *_, r in sel if r is not None and r <= 10)}")
