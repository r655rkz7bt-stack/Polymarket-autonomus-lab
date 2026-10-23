# 23/10/2026 (soir) : `news_momentum` promet 0,999 pour un favori à 0,986

Famille du jour : n° 6 (« ce qui ne tourne plus »), puis les obligations de la feuille de mission.

## Obligations de la feuille de mission
- **`apres_echeance`** (22 gagnés pour 28,9 attendus sur 30) : cause écrite le 23/10 matin (achats 1 à 2 h après le coup d'envoi), stratégie éteinte. Rien de neuf.
- **Championne `nf_sport_patiente`, 18/10 = 132 % du gain** : cause écrite les 22 et 23/10 (3 paris = 95 % du gain, biais fixe). Rien de neuf.
- **`contrer_crypto_patiente`** (4 gagnés pour 5,9 attendus sur 30, −37,7 %), nouveau : sur ses 97 paris réglés, **24 gagnés pour 18,4 attendus par les prix** (au-dessus de ses prix, pas en dessous) et −45,7 € pour 212,9 € misés. Tout le déficit vient de 31 billets
  à moins de 0,10 (0 gagné pour 2,1 attendus, −76,9 € ; probabilité de 0 sur 31 ≈ 12 %) ; les billets de 0,10 à 0,60 gagnent +31 €. Le 22/10 : −48 € sur 62 € misés (11 paris, 1 gagné pour 2,8). Pas de défaut de code : variance de loterie, mises qui
  grossissent avec le capital (8 € le 16/10, 62 € le 22/10). Rien à corriger.

## Défaut trouvé : estimation « prix + continuation » au-delà de la certitude
- **Constat** : les positions « ouvertes bien après l'échéance » (5 marchés, 27 positions, **990 € bloqués** : Cape Town 17 et 18 °C et « Russia target Kyiv » en litige UMA `disputed`, deux marchés du référendum d'Alberta non clos à 0,9925)
  contiennent 188,8 € × 3 fantômes (`nm_hors_crypto`, `nm_demi_mise`, `nm_prix_haut`) sur « Non » à 0,986 pour la température du Cap : 20 % de leur capital, estimation 0,999, 2,7 h avant la fin, **pour un gain possible de 1,3 point**.
- **Cause** : `strategies_v2.NewsMomentum.propose` : `est = prix du camp + continuation (0,04)`, puis `_buy` ramène les trois bornes (estimation − incertitude, estimation, estimation + incertitude) à 0,999. Pour un favori à plus de 0,96 la borne basse est
  donc **fixée à 0,999 quoi qu'on mette comme incertitude** : le Kelly (kelly_fraction 1) mise tout ce que `_cap_ghost` autorise (25 %).
- **Ampleur** (journaux signés, 9 portefeuilles de la famille, 319 paris réglés, 208 jetons) : 205 gagnés pour 216,0 attendus par les prix, −526 € pour 8 685 € misés. Prix ≥ 0,95 : 89 paris, 88 gagnés pour 86,9, **−42 € pour 5 618 €** (65 % des mises) ;
  0,90-0,95 : 35 paris, 26 gagnés pour 32,2, **−362 €** ; sous 0,90 : −121 €. Positions encore ouvertes : 174, 3 630 €. Le principal ne copie aucune de ces stratégies : seule l'arène est faussée.
- **Correctif** : `_bump` (`strategies_v2._Base`) : la continuation est plafonnée à `bump_share` (0,5 par défaut) de l'écart entre le prix et la certitude : à 0,986 l'estimation devient 0,993 et la borne basse 0,973 < prix, donc « avantage net insuffisant ». Loin de la certitude rien ne change
  (0,5975 + 0,06).
- **Test** : `tests/test_strategies_v2.py::test_news_momentum_does_not_claim_an_edge_beyond_certainty` (échoue sans le correctif, vérifié).
- **Contrôle automatique** : `enquete.certitude_promise` (paris promis à 0,995 et plus pour un prix ≤ 0,99, un jeton = un pari, toute l'arène) ; sur les journaux publiés : 27 paris réglés, −154 € pour 1 747 € misés (`tests/test_enquete.py`).

## Non corrigé, noté
- `InformationAdvantage` (`impact × |stance|`) et `SocialSentiment` (`fade`) ajoutaient aussi un bonus au prix du camp, sans plafond ; muettes sans Gemini (en pause), elles n'ont rien acheté, mais elles passent par le même `_bump` (test : échoue sans le plafond, vérifié).
- Le marché du Cap (587 € sur 3 fantômes) attend la décision UMA : un fantôme ne peut pas le vendre. Le litige est un risque de règle subjective, déjà noté le 21/10.
- Une température « 17 °C / 18 °C » ne relève d'aucune « actualité » : le rattachement d'actualités aux marchés météo (`intel.signal`) est à regarder (chantier).
- Référendum d'Alberta (5475240 et 5475242) : ni litige ni proposition UMA (`umaResolutionStatuses: []`), le marché attend le résultat officiel d'Elections Alberta ; 135 € bloqués, rien à corriger.
