# `compteur_tweets_non` re-jugé aux prix des vrais échanges, avec le volume réellement échangé (25/10/2026)

**Question** : la fille « NON sans NYC Mayor » (retenue le 21/10 sur les prix horaires du CLOB, +16 %, t +2,9 à +4,5) tient-elle aux prix qu'on aurait payés, sur plus de mois, et où vit son gain ?
(`tweets_fin_periode.md` du 24/10 avait déjà rejoué les vrais échanges : +14 %, t +2,1, juillet-octobre. Ici : mars-octobre, quatre comptes, et le volume échangé.)

**Données** (`experiments/tweets_prix_payes/scripts/`) : événements réglés de ZelenskyyUa (55 retenus), tedcruz (60), WhiteHouse (61), cz_binance (55), messages XTracker, échanges réels de 254 événements.
Règlement retrouvé par nos messages : 228 périodes sur 231 (Zelensky 52/55). Formule de production (168 h / 336 h, dispersion 12), NON seulement, billet ≥ 0,10, frais 5 % × p × (1 − p), prix = premier échange d'un preneur dans les 2 h suivant la décision,
décisions à début + 6 h, 1, 2, 3, 4, 5, 6 jours, un seul signal par (période, tranche).

## Résultats (dispersion 12, marge 0,04)
| | achats | périodes | par achat | t par période |
|---|---|---|---|---|
| tous les comptes | 333 | 186 | **+10,5 %** | +1,36 (6 mois sur 8) |
| ZelenskyyUa | 84 | 49 | +0,2 % | 0,0 |
| tedcruz | 91 | 44 | +26,9 % | +1,8 |
| WhiteHouse | 117 | 58 | **−6,9 %** | −1,8 |
| cz_binance | 41 | 35 | +44,6 % | +1,9 |
| volume échangé au prix dans les 2 h < 20 parts | 136 | 106 | +13,9 % | +1,7 |
| 20-100 parts | 146 | 109 | +14,5 % | +1,2 |
| **≥ 100 parts** | 51 | 46 | **−10,3 %** | −1,1 |
| prix 0,10-0,30 / 0,30-0,70 / ≥ 0,70 | 26 / 152 / 155 | | +96 % / +9,3 % / −2,7 % | +1,9 / +0,8 / −0,4 |

Autres réglages (5, tous « indice » ou pire) : marge 0,07 +11,0 % (t 1,3) ; dispersion 8 +7,9 % (t 1,0) ; dispersion 16 +9,5 % (t 1,4) ; billet ≥ 0,20 +8,6 % (t 1,5) ; **OUI et NON ensemble +0,7 % (t 0,65, écartée)**.
Dans tous les réglages, les achats avec ≥ 100 parts échangées perdent 8 à 12 %.

## Lecture
- `compteur_tweets_non` n'est pas « retenue » : +8 à +11 % par achat, t par période 1,0 à 1,5 après ~60 découpages + ces 6 réglages (confirme la prudence du 24/10 : fantôme, jamais dans `validated_strategies`).
- Le gain est porté par deux comptes (tedcruz, cz_binance) ; WhiteHouse perd.
- Mise en garde sur la mesure : « parts échangées dans les 2 h au prix payé » est un flux, pas la profondeur du carnet ; un marché où il se passe beaucoup de choses est aussi un marché où les vendeurs sont informés. Les deux lectures (échanges minces = cotations périmées, ou
  échanges abondants = marché efficace) disent la même chose : l'avantage ne se prend pas à taille réelle. Même constat que pour les posts Truth Social (`truth_social.md`).
- À faire quand l'arène aura des mois de vrais carnets : comparer `compteur_tweets_non` (mise en direct) à ce rejeu.
