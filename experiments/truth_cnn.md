# Secours de XTracker : l'archive CNN des posts de Trump (07/11/2026)

**Problème.** XTracker (`xtracker.polymarket.com`) répond 403 aux robots depuis le 06/11 vers 19 h UTC (cycle et appels à la main, User-Agent
honnête, aucun contournement tenté). Le champion `compteur_tweets` et `compteur_truth` n'avaient plus de compteur : abstention « compteur pas à jour »
depuis ≈ 16 h, six passages du chercheur de suite l'ont signalé sans solution.

**Source trouvée.** `ix.cnn.io/data/truth-social/truth_archive.json` (CNN, JSON public, sans clé, 21 Mo, 37 965 posts de `@realDonaldTrump`
du 14/02/2022 à aujourd'hui, réécrit toutes les ~5 minutes : en-tête `Last-Modified`). Donnée seulement ; pas de licence écrite, pas d'accès
protégé contourné. Elle peut disparaître sans prévenir : le secours ne sert que si XTracker échoue.

**Comparaison avec XTracker** (dernier relevé XTracker sauvegardé, le 06/11 à 22 h 31 UTC ; 336 dernières heures, heure par heure) :
- 332 heures sur 336 identiques ; 810 posts XTracker contre 735 CNN. Les 4 heures qui diffèrent sont des heures de rafale
  (CNN 22/XT 44, 35/39, 41/62, 95/123) ; toutes les heures ≤ 19 posts sont exactes, et plusieurs heures de 28-55 posts aussi.
- Périodes de marché : « 6-13 nov » 3 contre 3, « 3-10 nov » 34 contre 34 (exact), « 30 oct-6 nov » 530 contre 605 (la période de la rafale du 03/11 : −12 %).
- Rythme long (84 jours) : 2 530 contre 2 545 (−0,6 %).

**Ce qui est fait** (`references.fetch_trump_from_archive`, branché dans `data_collector` seulement quand XTracker lève `SourceUnavailable`) :
- les lignes « Trump » ont le même format que XTracker (`total`, `heures` sur 14 jours, `posts_long`) avec `source: cnn_archive` ;
- les périodes viennent du dernier relevé XTracker et des périodes régulières (mardi et vendredi, 12 h heure de l'Est, 7 jours) : le rattachement se fait au `slug`,
  une période sans marché ne rattache rien ; une période d'un autre rythme (ni mardi ni vendredi) ne serait pas vue ;
- `vu_le` = date de réécriture du fichier CNN : si CNN gèle son fichier, les stratégies s'abstiennent comme avant ;
- une période qui contient une heure de **20 posts ou plus** est marquée `incertain` (CNN en rate environ le quart) et `compteur_tweets` s'abstient
  (« compteur de secours incertain ») : on ne parie jamais sur un compte que l'on sait sous-estimé ;
- les autres comptes (Elon Musk, Zelensky, Maison-Blanche…) gardent leur dernier relevé périmé : aucune source de secours pour eux, abstention.

**Reste ouvert.** Le rythme des 14 jours (`heures`) sous-compte aussi les heures de rafale (−25 % sur ces heures seulement) ; effet faible, non corrigé.
Aucun test sur le passé n'est refait ici : le secours ne change pas le modèle, seulement la source du compteur. Si XTracker revient, il reprend la main tout seul.
Scripts : aucun (comparaison faite avec `experiments/truth_cnn/donnees/`, ignoré par Git). Test : `tests/test_references.py::test_trump_backup_counts_on_the_cnn_archive_…`.
