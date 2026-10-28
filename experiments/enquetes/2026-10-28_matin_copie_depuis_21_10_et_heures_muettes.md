# 28/10/2026 (matin) : copie du principal depuis le 21/10, et filles « hors de leur heure » qui ne disaient rien

Famille 1 (le principal a-t-il fait les paris des fantômes copiés, à la bonne taille ?) et famille 6 (qu'est-ce qui ne tourne plus ?). Scripts : `experiments/enquetes/scripts/copie_depuis_21_10_28_10.py` et `copie_sens_et_plage_28_10.py`.

## 1. Copie du principal, jeton par jeton (journal signé du principal contre chaque fantôme copié)

- Depuis le 21/10 (après la correction des mises 3 fois trop grosses) : **225 jetons** achetés par le principal pour 19 stratégies copiées ; **224 ont un jumeau** dans le journal de la stratégie copiée ;
  le dernier (`nf_sport_patiente_6_24h`, « Team Yandex », 25/10 22 h 35) est celui déjà élucidé (`2026-10-26_ordre_pose_perime_du_principal.md`, contrôle `copie_fidele`).
- Achat par achat (215 achats du principal avec jumeau, `copie_sens_et_plage_28_10.py`) : 0 de côté opposé ; prix du principal moins prix du jumeau : médiane 0,0000, de −0,0105 à +0,0070 ; aucun à plus de 2 centimes.
- Rapport mise du principal / mise du fantôme : médiane 0,03 à 0,30 selon la stratégie (le principal mise une fraction de la mise du fantôme), maximum 1,0 là où le plancher de copie
  achète le minimum du marché (`compteur_tweets` 14 jetons, `moins_de_cartes` 15, `favori_politique_nuit` 4).
- Avant le 21/10 (16 jetons de `nf_court`, tous du 18/10) : le principal perd −149 € (−24,4 %) contre −51 € (−10,0 %) pour le fantôme sur les MÊMES jetons, uniquement parce que ses mises
  étaient 1,5 à 3 fois celles du fantôme sur les trois perdants (défaut des mises du principal, connu et corrigé les 20-21/10). Rien de nouveau.
- **Résultat : copie fidèle, aucun défaut.** Gain du principal sur ses jetons réglés : −279,5 € au total, dont −149 € de `nf_court` (18/10) et −70 € de `meteo_prevision` (retirée), le reste ≈ −60 €.

## 2. Filles hors de leur heure : « abstentions {} » = impossible de distinguer une fille sourde d'une fille en pause

- `data.json` du 28/10 05 h 45 UTC : 15 fantômes affichent `propositions 0, ordres 0, raisons {}` (`nf_sport_18_24h`, `nf_sport_patiente_matin`, `nf_sport_patiente_72_168h_12_18h`, `nf_court_soir`, `nf_court_football_soir`,
  `outsider_sport_apres_midi`, `mots_nouveaux`, `tranche_centrale_non`…). Cause : `Filtered.propose` renvoyait `StrategyOutput()` vide dès que l'heure UTC sortait de `heure_utc`, sans une seule raison. Les contrôles `muettes` et
  `acheteuses_arretees` affichaient « aucune raison notée » : une vraie panne (source morte, filtre trop strict) et une fille qui attend ses 18 h se ressemblaient.
- Pas de perte d'argent (aucun achat n'est manqué : la fille n'a pas le droit d'acheter à cette heure). Mais une fille vraiment sourde et une fille en pause donnaient la même ligne vide, et la liste des muettes ne pouvait pas les séparer.
- **Correctif** : `Filtered.propose` écrit « hors de la plage horaire (heure_utc 18-24) » pour chaque marché de la liste ; test dans `tests/test_favori.py::test_hour_of_day_filter`.
