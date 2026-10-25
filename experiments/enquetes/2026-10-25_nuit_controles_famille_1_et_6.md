# 2026-10-25 (passage de minuit) : contrôles à la main, familles 1 et 6 — rien de nouveau, un constat sur la météo

Famille du jour : n° 1 (24 mod 6 + 1) ; déjà faite deux fois le 24/10. Refaite sur les journaux publiés à 23 h 52 UTC, plus un contrôle famille 6.

## Famille 1 : le principal joue-t-il ce que l'arène mesure ? (`scripts/copie_prix_paye.py`, 163 jetons réglés)
- Prix payé par le principal identique à celui du fantôme copié (−0,0007 en moyenne pour la championne, 59 jetons, 0 absent du fantôme) ; gain réalisé −240 € contre −254 € au prix du fantôme.
  Les écarts viennent des jetons d'avant la copie fidèle (PR #76 : `nf_sport` 35 absents, `meteo_prevision` 11, `nf_court` 2, tous du 15-18/10).
- Obligations « champion sans avantage / chance » (`nf_sport_patiente*`, `nf_tennis_12_18h_vainqueur`) : même mécanisme qu'avant (mise ∝ 1/(1 − prix), favoris qui gagnent comme leur prix) ; non refaites.
- Mises de fantômes au-dessus de 25 % du capital : les 3 du 24/10 soir sont à 25,0 % pile (le plafond tient) ; les 45-53 % datent du 22/10, avant le plafond.

## Famille 6 : ce qui ne tourne plus
- `positions_oubliees` : 3 marchés bloqués. Cape Town 17/18 °C du 18/10 (litige UMA, `umaResolutionStatus: disputed`, prix 0,99), référendum de l'Alberta (fin 20/10, pas encore réglé par UMA). Vérifiés sur Gamma `/markets/<id>` : aucun défaut de code, l'argent attend la décision officielle (déjà notée le 24/10).
- `favori_politique*` : le correctif `zero_fees` (soir du 24/10) a bien rouvert la politique : `parking_politique` a acheté deux NON à 0,949 et 0,961 le 24/10 à 21 h 27 ; `favori_politique` voit 218 marchés sur 490 et n'achète rien (121 « hors de la plage de prix », 11 « position déjà ouverte » : il tient encore ses positions du 16/10). Pas un défaut.
- Météo : le scanner lit 261 marchés de température (97 éligibles) mais aucun n'entre dans les 150 surveillés (volume du jour trop bas face au sport et à la crypto) ; ils n'arrivent aux stratégies que par `candidates()`. `meteo_prevision_patiente` est désactivée (éliminée le 22/10) ; `loterie_meteo` voit bien ses marchés (479 exclus par la famille = les marchés non météo). Rien à corriger.
- Source libre vérifiée : XTracker liste `realDonaldTrump` en plateforme TRUTH_SOCIAL : les marchés « posts Truth Social » étaient déjà joués par `compteur_tweets`.

## Famille 3/5 : la comptabilité des journaux est-elle juste ? (`scripts/rejeu_cash_25_10.py`)
Trésorerie rejouée depuis chaque journal signé (1000 − Σ achats − frais + Σ parts réglées × paiement) contre la dernière trésorerie notée par le cycle : **159 journaux sur 159 au centime, aucun règlement en double.**
Devenu contrôle automatique `enquete.tresorerie_rejouee` (grave en cas d'écart) + test qui échoue sans lui (règlement perdu, règlement doublé).

## Obligation « audit »
Les 2 anomalies hors « pas clos » sont toujours les achats à 0,0010 de `crypto_threshold_non` / `_prix_bas` (24/10 15 h 17), déjà corrigés le 24/10 (`TOUCH_MIN_ASK`). Rien de nouveau.

## Résultat
Aucun défaut de code nouveau ; un contrôle ajouté (`tresorerie_rejouee`) et `idea_test.ECARTES_50_50` (compte des marchés 50-50 écartés par un relevé). Piste ouverte au passage : `experiments/truth_social.md` (l'effet n'existe que sur les échanges minces, voir la fiche).
