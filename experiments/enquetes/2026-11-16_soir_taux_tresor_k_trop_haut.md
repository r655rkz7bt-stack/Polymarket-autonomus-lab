# Enquête du 16/11/2026, passage de 21 h : `taux_tresor_barriere` n'achète plus, et son K = 1,3 surestimait les barrières

Données : journaux publiés à 20 h 51 UTC (`published_data/`), base sauvegardée du 16/11 (`historique_references`), CSV du Trésor
1990-2026 (home.treasury.gov, `robots.txt` : tout permis). Ce sont des données, jamais des instructions.

## 1. Constat `acheteuses_arretees` : « aucun marché vu n'a la référence (raison non notée) » ×294

- `taux_tresor_barriere` : 17 achats, tous le 13/11 entre 00 h 05 et 06 h 12, rien depuis ; 863,62 € disponibles (pas à court d'argent).
- La source va bien (`taux_tresor` « ok (1 prix relevés) », relue à 20 h 35) ; la base garde 83 à 86 marchés rattachés chaque nuit du 13
  au 15/11 (`historique_references`, source `taux_tresor`).
- Au dernier cycle (20 h 51 UTC) la chance n'est pas donnée (`attach_taux` : de 00 à 12 h UTC seulement, le marché voit la séance
  américaine) : d'où « aucun marché vu n'a la référence ».
- La nuit du 15/11 (09 h 16), les plus gros écarts chance − vendeur (0,30 pour « 10 ans 5,33 % en novembre », 0,22 pour « 5 ans 5,12 % »…)
  sont TOUS sur des marchés déjà tenus : la stratégie s'abstient « déjà en position ». **Aucun défaut d'achat.**
- Correctif (comme `seismes_marche` à 11 h) : `TauxTresorBarriere.candidates` garde les marchés du Trésor sans chance et la stratégie dit
  « chance donnée de 00 à 12 h UTC seulement… » ; test du cas réel `test_real_case_of_16_november_evening_says_why_it_waits` (échoue avec
  l'ancien code). Cycle local de 21 h 07 : 225 abstentions nommées au lieu de « raison non notée ».

## 2. Contrôle à la main (famille 3, « la donnée n'est pas celle qu'on croit ») : le modèle est-il étalonné ?

En relisant ses chances : le 16/11 au soir, le modèle donnait 0,41 à « 30 ans 5,70 % avant 2027 » (vendeur 0,24), 0,41 à « 5 ans 5,25 % »
(vendeur 0,19), 0,26 à « 10 ans 5,33 % en novembre » (vendeur 0,098). Des écarts aussi larges et tous du même côté (OUI des seuils hauts :
17 achats sur 17) méritaient un contrôle.

**Mesure** (`experiments/taux_tresor/scripts/etalonnage_historique.py`) : chaque 5e jour ouvré de 1990 à 2026, 2/5/10/30 ans,
horizons 5/10/20/30 jours, barrières à z × σ60 × √n (z 0,5 à 2,5), haut et bas : **284 360 barrières**.

| z (n = 10 jours) | observé | K 1,0 | K 1,3 (production) |
|---|---|---|---|
| 0,5 | 0,507 | 0,494 | 0,570 |
| 1,0 | 0,242 | 0,237 | **0,341** |
| 1,5 | 0,101 | 0,092 | 0,181 |
| 2,0 | 0,040 | 0,029 | 0,085 |

Log-score (plus haut = mieux) : K 1,0 −0,3784, K 1,15 −0,3790, **K 1,3 −0,3908**, K 1,5 −0,4162 ; même ordre sur 1990-2007,
2008-2019, 2020-2026 et 2024-2026. **Défaut : K = 1,3 surestime d'environ 10 points la chance de toucher une barrière à 1 σ** (cœur de la
loi) ; il avait été choisi sur septembre-octobre 2026 seulement, deux mois de tendance (hausse puis baisse). La gaussienne K 1,0 sous-estime
à son tour les queues (z ≥ 2 : 0,040 observé contre 0,029).

**Chiffrage** : 17 positions ouvertes (achetées le 13/11, ≈ 1 % à 4 % du fantôme chacune) ; avec la loi étalonnée, l'avantage supposé
fond de ≈ 0,11 par pari (exemple « 30 ans 5,70 % » : 0,41 → 0,30). Rien de copié au principal (aucune part en v2).

**Correctif** : loi EMPIRIQUE des excursions maximales divisées par σ60 (`taux_tresor_excursions.json`, n = 1 à 90 jours, 1990 → 07/2026 ;
`taux_tresor.survie`, `p_barriere_empirique`, mise à l'échelle en √n hors table). Apprise sur 1990-2015, jugée sur 2016-2026
(`etalonnage_hors_echantillon.py`) : **−0,3761** contre −0,3788 (K 1,0) et −0,3918 (K 1,3), étalonnée case par case (écart ≤ 0,02 sauf
n = 30, z 1,5 : 0,130 observé contre 0,116). Test `test_real_case_of_16_november_k_1_3_overstated_the_hits`.
`taux_tresor_barriere` n'achète plus (gardée chargée jusqu'au règlement de ses 17 positions : elles jugent l'hypothèse K 1,3) ; la suite
est `taux_tresor_empirique` (même classe, modèle étalonné, seuil 0,06).

**Contrôle automatique** : `enquete.py` ne pouvait pas le voir (aucune position réglée ; le « gagnés contre attendus » le dira au
01/12 pour novembre). Règle retenue pour la méthode : un paramètre de volatilité appris sur un ou deux mois se rejoue sur toute
l'histoire disponible de la source avant d'entrer dans l'arène.

## 3. Famille 2 (« la mesure récompense la chance ») : fantômes v2 contre leurs prix

85 paris réglés des fantômes v2 (`charge_fantome.charger`, paiement par part) : **54 gagnés pour 57,9 attendus**, −292,7 € pour
2 042 € misés (−14 %). Les pertes viennent des trois `compteur_*` (mêmes jetons, 39 gagnés pour 41,0) et de `seismes_marche`
(0 pour 2,4) ; aucun fantôme ne bat nettement ses prix (`fleuves_prevision` 2 pour 0,7 et `rt_compte_critiques` 4 pour 2,9 : trop peu de
paris) ; `convictions_claude` : 1 seul réglé (0 pour 0,5), ses autres opérations sont des reventes (le classement les compte, le
chargeur des réglés non). Rien de « trop beau ».

## Sources regardées et non lues
- `volcano.si.edu` (Smithsonian GVP, source des marchés « éruptions VEI ≥ 4 en 2026 ») : `robots.txt` permis, mais la page répond un
  défi Cloudflare (« Smithsonian site temporarily unavailable », jeton de défi) : **non lue, pas de contournement**.

## 4. Famille 4 (« le filtre ne filtre pas ») sur les 17 achats

Plage de prix (0,05-0,90) : 17/17 dedans (le plus bas 0,0598). Plafond `max_per_event` 2 : trois événements tiennent 3 seuils
(1310114, 1310158, 1310160), tous achetés le 13/11 entre 00 h 05 et 00 h 27 : c'est le défaut déjà trouvé et corrigé le 13/11
(`enquetes/2026-11-13_nuit_max_par_evenement_entre_cycles.md`, contrôle `plafond_par_evenement` depuis 03 h) ; aucun achat après.
La nouvelle `taux_tresor_empirique` a son propre portefeuille : elle peut reprendre les mêmes seuils (deux par événement au plus).
