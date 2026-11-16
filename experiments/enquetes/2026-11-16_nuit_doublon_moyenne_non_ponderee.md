# 16/11/2026 (nuit) : le retrait « doublon » des filles jugeait sur la moyenne simple ; deux filles copies conformes de leur mère

Passage chercheur de 1 h (jour 16 → famille 5, « comparaisons faussées »). Aucune obligation dans la feuille de mission.

## Constat « à regarder » mené au bout : `seismes_marche` « n'achète plus depuis le 12/11 »

- Raison affichée au dernier cycle (16/11 00 h 50) : « aucun marché vu n'a la référence » ×358.
- `historique_references` (sauvegarde de la base) : la source `seismes` a rattaché 14 à 16 marchés à chaque heure du 12/11 09 h
  au 15/11 16 h ; puis plus rien : la semaine du 9-15/11 (fin 16/11 05 h UTC) a moins de 0,5 jour devant elle et celle du
  16-22/11 plus de 6,6 jours (`WEEK_MIN_DAYS`, `WEEK_MAX_DAYS`). Polymarket ne crée plus de marché « plus gros séisme du jour ».
- Pourquoi aucun achat du 12 au 15/11 : le journal du fantôme tient déjà deux tranches de chacun des deux événements de la
  semaine (5,5 : achats du 09/11 et du 10-11/11 ; 6,5 : 09/11 et 10/11) ; `max_per_event` 2 → « déjà deux tranches ».
  Exemple relu (15/11 10 h 16) : « ≤ 6 séismes ≥ 5,5 » chance 0,833 pour un vendeur à 0,75 : refusé pour cette raison.
- **Aucun défaut** : stratégie en attente de la semaine suivante (rattachement attendu vers le 16/11 9 h UTC).

## Contrôle à la main, famille 5 : paris liés ENTRE stratégies v2

Script : `experiments/enquetes/scripts/evenements_partages_16_11.py` (journaux signés `published_data/ledger/fantome_v2`).

- 129 événements achetés par les fantômes v2 ; 19 par au moins deux stratégies, 2 343 € misés au total sur ces 19.
- Les trois `compteur_*` jouent **les mêmes jetons aux mêmes prix** : semaine Truth Social 1305849, 892,6 € (≈ 297 € chacune,
  6 achats identiques : NON 0,827, OUI 0,321, NON 0,818, NON 0,892, OUI 0,120, NON 0,833) ; semaine 1354153, 484,8 €.
  `compteur_truth` : 15 jetons sur 15 chez la mère (écart de prix max 0,002) ; `compteur_tweets_72_168h` : 18 sur 19 (0,01).
  Les places 23, 24 et 25 du classement (−49, −81, −89 €) sont **un seul tirage compté trois fois**.
- Les autres recoupements sont attendus (`favori_politique_quasi_certain` et `non_aux_drames` : jetons opposés d'élections ;
  `convictions_claude` et `fleuves_prevision` / `michigan_preliminaire` / `auditeurs_spotify` : même jeton, petites mises).

## Défaut trouvé (code, `arena.retire_daughters`)

- Le retrait « doublon » (fille ≥ 90 % de paris communs avec sa mère, ≥ 20 opérations) compare le **rendement moyen simple par
  opération** (`_mean_return_since`). C'est exactement le défaut corrigé le 14/11 dans le contrôle `filles_periode`, resté dans
  l'arène : `compteur_tweets_72_168h` y affiche +28,7 % contre −6,0 % (un billet de 3 € à 0,18 gagné), alors que pondéré par
  la mise elle fait −14,3 % contre −14,6 %. À 20 opérations, la fille aurait été jugée « meilleure » et gardée à vie.
- Ampleur : aucun euro du principal (au repos) ; deux fantômes qui faussaient le classement et le compte des « preuves ».
- Correctif : `_weighted_return_since` (résultat total / mise totale) dans le test « doublon » ; test du cas réel
  `test_duplicate_daughter_is_judged_on_stake_weighted_return` (échoue avec l'ancien code : vérifié).
- Contrôle automatique : `filles_periode` écrit « COPIE CONFORME » quand ≥ 90 % des jetons de la fille sont chez sa mère avec
  le même rendement pondéré (±2 points) ; il le dit dès 8 opérations, sans attendre les 20 de l'arène.
- Arène : `compteur_truth` et `compteur_tweets_72_168h` **coupées** (`max_proposals_per_cycle` 0 : plus d'achat, leurs positions se
  règlent) ; `compteur_truth` ôtée de `jamais_retirer`. Leurs filtres (créneau 72-168 h, Trump seul) sont des découpages a posteriori
  que la v2 ne refait plus ; la mère garde l'expérience. 26 → 24 vivantes.
