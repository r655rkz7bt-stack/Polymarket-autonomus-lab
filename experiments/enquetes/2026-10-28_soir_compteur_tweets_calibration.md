# 28/10/2026 (soir) : le modèle de `compteur_tweets` tient-il ses estimations ? (famille 2 et 4)

Question : les achats `compteur_tweets*` annoncent des estimations très au-dessus du prix payé (0,71-0,78 contre 0,42-0,56, ce que le
contrôle `estimation_perimee` signale à chaque passage). Est-ce un modèle qui s'emballe, ou un avantage ?

Script : `experiments/enquetes/scripts/compteur_tweets_calibration_28_10.py` (journaux signés des 9 fantômes `compteur_tweets*`, un
pari par jeton, doublons des filles retirés).

## Constat
- 46 paris réglés = 12 événements, 33,0 gagnés pour **32,8 estimés** et 28,4 attendus par les prix payés ; gain +85 € pour 744 € misés (+11 %).
  **Les estimations sont calibrées** (pas de modèle qui s'emballe) ; l'écart « estimation − prix » est la vraie marge, pas un défaut de carnet.
- Par délai jusqu'à la fin : **moins de 48 h : 22 paris, 12 gagnés pour 15,6 estimés (12,8 par les prix), −29 % par mise** ;
  48-100 h : 15 paris, 12 gagnés pour 9,3 estimés, +52 % ; 100-400 h : 9 paris, 9 gagnés pour 7,8, +18 %. Plus de 48 h : 24 paris,
  21 gagnés pour 17,1 estimés, 15,7 par les prix.
- Par côté : NON 34 paris, 27 gagnés pour 28,3 estimés, +1 % ; OUI 12 paris, 6 gagnés pour 4,5 estimés (3,5 par les prix), +78 % (mises de 8 €).
- Gain par événement : de −29,5 à +32,5 €, 10 événements positifs sur 12.

## Limites
Découpage a posteriori de 46 paris dans 12 événements (le z par événement reste proche de 1) : un **indice**, pas un avantage.
Les 22 paris à moins de 48 h sont 9 événements.

## Correctif
Aucun défaut de code. Fantôme d'expérience `compteur_tweets_48h_audace` (filtre `echeance_min: 48`, Kelly entier) : une perte
apprendrait que le gain venait de quelques événements. Le contrôle `estimation_perimee` reste un « à regarder » (modèle propre).

## Autres contrôles du passage
- `filtres_prix_24_10.py` rejoué : 2 662 achats récents, les écarts hors plage sont des ordres posés servis plus bas que la plage
  (`favori_politique_patiente` 14/22 à 0,84 pour une plage 0,85-0,97 ; `nf_sport` 10/315) : comportement connu du mode patient, pas un défaut nouveau.
- `fenetres_25_10.py` rejoué : mêmes ordres posés servis hors fenêtre (4 à 6 par stratégie) ; rien de nouveau.
- Positions « oubliées » : référendum d'Alberta (5475240, 5475242), toujours ni clos ni contesté 8 jours après l'échéance, prix 0,99 : attente du résultat officiel.
