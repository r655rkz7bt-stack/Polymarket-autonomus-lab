# 11/11/2026, passage de 16 h : la perte de `seismes_marche` (−144 €) et les positions qui ne se règlent pas (famille 6)

## Constat
- `seismes_marche` v2 : 3 opérations réglées, −144,51 € (855 € au classement). Deux paris sur la semaine des 2-8/11 (événement 1301713),
  réglés seulement le 11/11 (14 h 05 et 15 h 41 UTC, UMA) : OUI « ≤ 6 séismes ≥ 5,5 » acheté 0,74 (chance notée 0,853, 59 parts) et
  NON « 7 » acheté 0,79 (0,931, 91 parts) ; plus le jour du 07/11 (« 5,5-5,6 », −27 €, déjà vu le 09/11).
- Catalogue USGS relu (fenêtre 02/11 05 h → 09/11 04 h 59 UTC, heure de l'Est en heure d'hiver) : 7 séismes ≥ 5,5 (6,1, 6,1, 5,5,
  5,5, 5,8 le 07/11 à 23 h 17, 6,4 et 5,7 le 09/11 à 03 h 35 et 04 h 53 UTC, soit le 08/11 au soir à l'heure de l'Est). Règlement « 7 » conforme.

## Vérification
- Fenêtre : `horizon_hours` 34,62 du premier achat (18 h 21 UTC le 07/11) mène au 09/11 04 h 58 UTC : la stratégie lit bien l'heure de l'Est.
- Premier achat : 4 séismes comptés, il en fallait au plus 2 de plus en 34,6 h ; la chance 0,853 suppose ≈ 1,3 séisme attendu
  (≈ 0,9 par jour ≥ 5,5 sur 156 semaines), le marché disait 0,74. Deux sont arrivés dans les 90 dernières minutes de la fenêtre :
  malchance dans la queue, pas un défaut de lecture.
- Second achat : le défaut du catalogue en retard (5,8 de 23 h 17 absent), déjà corrigé le 11/11 au matin (témoin EMSC,
  `enquetes/2026-11-11_matin_seismes_catalogue_en_retard.md`).

## Famille 6 (à la main) : ce qui ne tourne plus
Achats par fantôme v2 depuis le 07/11 (journaux signés publiés) : `lid_agenda`, `secheresse_d4`, `suivre_inities` sans achat (attendus :
abstentions expliquées les 10-11/11) ; `non_aux_drames` 43 achats, 0 réglé : horizons de 1 219 à 1 975 h (51 à 82 jours) voulus,
406 € engagés sur 1 000 ; `favori_politique_quasi_certain` : 5 positions ouvertes (Nouvelle-Zélande, résultats officiels le 27/11).

## Défaut trouvé dans le travail du même passage : `ref:fleuves` sans journal
La nouvelle source `fleuves` (prévisions officielles du Rhin et du Danube, PR #226) écrivait son relevé dans `ref:fleuves`, qui est
REMPLACÉ à chaque relevé (`references._save`) : le compte rendu disait pourtant que « le journal garde chaque prévision ». Le test
promis (prévision contre niveau réel, dans 1-2 mois) aurait été impossible, comme `lid:histo` le 11/11 à 1 h. Ampleur : aucun euro,
une heure de relevés perdue (fusion à 16 h 11 UTC). Correctif : `fleuves.keep_history` → `fleuves:histo` (chaque prévision émise, gardée
telle que lue la première fois, et chaque lecture, 400 jours), test `test_history_keeps_every_issued_forecast_while_the_reference_is_replaced`.
Pas de contrôle automatique possible (aucun journal ne dit quel test futur une source doit servir) : règle ajoutée au skill `nouvelle-strategie` (étape 5).

## Conclusion
Aucun défaut de code nouveau dans les journaux. La perte vient d'un défaut déjà corrigé (−65 €) et de la queue de la loi (−44 €). Rien changé.
