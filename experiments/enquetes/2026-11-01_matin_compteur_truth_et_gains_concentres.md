# 01/11/2026 (matin) : relecture de `compteur_truth` et concentration des gains (familles 2 et 3)

**Résultat : aucun défaut de code.** Script : `scripts/truth_relecture_01_11.py` ; `concentration_top_31_10.py` relancé sur les 9 premières de l'arène.

## Famille 3 : les 11 paris de `compteur_truth` (posts Truth Social de Trump), relus sur Gamma
- 11 marchés sur 11 : le paiement du journal est celui de Gamma (`outcomePrices`), tous `closed`. Fenêtres « du 23 au 30/10 », « du 27/10 au 03/11 », « du 30/10 au 06/11 » : même source (xtracker), même règle.
- Trois règlements arrivent **avant la fin de la fenêtre** (ex. « 200+ du 27/10 au 03/11 » clos le 31/10 19 h 56, « 200+ du 30/10 au 06/11 » clos le 01/11 05 h 29) : normal, un compteur de posts ne
  décroît pas, « 200+ » et les tranches dépassées se règlent dès que le seuil est franchi. Le journal les règle à l'heure Gamma (`closedTime`), pas avant.
- Les 11 paris ne sont que **3 événements** (fenêtres qui se chevauchent : le 27/10-03/11 et le 30/10-06/11 partagent 4 jours) : +219 € (+61,8 %), 10 gagnés pour 7,7 attendus, z par événement +1,83. Indice, pas preuve.

## Famille 2 : gain sans les 3 plus gros paris / sans le meilleur jour (arène du 01/11)
| stratégie | paris / événements | gain | sans les 3 plus gros | z événements |
|---|---|---|---|---|
| compteur_tweets | 69 / 18 | +229 € | +81 € | **+3,32** (1re parmi ~40 : z attendu ≈ 2) |
| compteur_truth | 11 / 3 | +219 € | +28 € | +1,83 |
| compteur_tweets_oui | 14 / 6 | +191 € | −48 € | −0,23 |
| nf_sport_patiente_6_24h_6_12h | 17 / 13 | +231 € | +145 € | +0,71 |
| nf_sport_patiente_avant_match | 59 / 54 | +165 € | +95 € | −0,81 |
| compteur_tweets_48h_audace | 6 / 4 | +129 € | +23 € | +1,72 |
| seismes_marche | 17 / 7 | +93 € | −10 € | +1,61 |
| moins_de_kills | 16 / 8 | +70 € | +42 € | +2,56 |
`compteur_tweets_oui` (+191 €) et `seismes_marche` (+93 €) ne tiennent pas sans leurs 3 meilleurs paris ; seule `compteur_tweets` bat nettement ses prix. Même lecture que le 31/10.

## Obligations
`crypto_threshold_prix_bas` (éliminée, encore configurée) : coupée (`enabled: false`), test de configuration mis à jour. Les 3 filles « 80/20 » de crypto (9, 16 et 35 opérations, mères crypto écartées sur le
passé : `contrer_crypto_passe.md`) refusées une fois de plus.
