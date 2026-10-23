# Piste 0b : les détroits (Ormuz, Bab el-Mandeb), 23/10/2026

**Question.** Les marchés « Avg. # of ships transiting <détroit> end of <mois> ? » se règlent sur la moyenne sur 7 jours
de passages que le FMI (IMF PortWatch) publie pour la dernière date du mois, avec ≈ 5 jours de retard. Le marché les cote-t-il
mieux qu'une simple prolongation de la série du FMI ?

**Verdict : INDICE (pas de preuve).** La loi calculée sur 2 ans d'historique donne à la tranche favorite du marché deux fois
moins de chance que son prix (Bab el-Mandeb : 0,45-0,51 contre 0,81), mais il n'existe **aucun prix passé** de ce type de marché
(deux événements seulement, tous deux ouverts : fin octobre) : on ne peut pas dire si le marché fait toujours cette erreur.
Fantôme `detroits_tranches` (quart de Kelly) ; le règlement du 31/10 sera la première mesure réelle.

## Données
- `experiments/detroits/scripts/portwatch.py` : historique quotidien PortWatch (`n_total`, ArcGIS public du FMI, sans clé),
  2 848 jours (2019-01-01 → 2026-10-18), sans trou, pour `Bab el-Mandeb Strait` et `Strait of Hormuz`. Le dernier jour connu le
  23/10 est le 18/10.
- `experiments/detroits/scripts/releve_marches.py` : 35 événements Gamma sur Ormuz / Bab el-Mandeb. Les tranches « average daily
  transits » n'existent que pour **deux événements, ouverts** (Bab el-Mandeb 5 tranches, 77 k$ ; Ormuz 7 tranches, 34 k$). Les
  autres (« traffic returns to normal », 10 réglés de 6 à 44 M$) sont des marchés oui/non sur ≥ 60 passages : Ormuz est resté à
  0-12 depuis mars 2026, rien à tester.
- Le suivi AIS (`hormuz.data-tracking.net/api/crossings/daily`) ne couvre qu'Ormuz (18-36 passages par jour, autre échelle que
  PortWatch) : pas de relevé en direct pour Bab el-Mandeb, donc pas de rattrapage des 5 jours manquants.

## Résultats (Bab el-Mandeb, moyenne sur 7 jours, dernier jour connu 18/10 = 26,43, cible 31/10 = +13 jours)
| Loi pour la moyenne du 31/10 | μ | σ | <20 | 20-24 | **25-29** | 30-34 | 35+ |
|---|---|---|---|---|---|---|---|
| marche aléatoire (écarts observés sur 24 mois) | 26,4 | 3,8 | 0,054 | 0,283 | **0,511** | 0,145 | 0,007 |
| idem, 12 mois | 26,4 | 4,1 | 0,076 | 0,312 | 0,456 | 0,147 | 0,008 |
| idem, 6 mois | 26,4 | 4,2 | 0,083 | 0,363 | 0,399 | 0,143 | 0,012 |
| normale, mélange (moyenne d'aujourd'hui + niveau 45 j) | 26,7 | 3,6 | 0,029 | 0,284 | 0,508 | 0,169 | 0,010 |
| **marché Polymarket (milieu du carnet, 23/10)** | | | 0,025 | 0,07 | **0,81** | 0,105 | 0,003 |

- Test de persistance : quand la moyenne sur 7 jours valait 25,9-27,0 (27 cas depuis 2019), elle était encore dans 25-30
  13 jours plus tard **10 fois sur 27 (37 %)** ; 8 fois sur 16 depuis octobre 2025 ; toutes positions confondues, la même tranche
  de 5 revient dans 51 % des cas (1 009 origines depuis 2024). Le marché affiche 81 %.
- Étalonnage de la loi (`comparer_modeles.py`, écart-type tiré des seules erreurs déjà connues) : la tranche de 5 qui contient la
  vraie valeur reçoit en moyenne 0,36-0,40 (Bab el-Mandeb) ; marche aléatoire, niveau récent et mélange donnent des scores voisins
  (log-vraisemblance −2,72 à −2,85). Le mélange est retenu, sans réglage fin (3 modèles essayés, 2 périodes).
- **Ormuz : aucune loi.** Le trafic est passé de 100 à 4 passages par jour en mars 2026 ; l'écart-type calculé sur un an (19) donnerait
  0,10 à la tranche 0-5 cotée 0,93 : une absurdité. Garde-fou de régime dans `references.ma7_forecast` (moyenne sur 7 jours variée de
  plus du simple au double en 120 jours → pas de loi). Les tranches d'Ormuz (7 marchés) ne sont donc pas jouées.

## Pourquoi ce n'est qu'un indice
1. **Aucun prix passé.** Une tranche à 0,81 était peut-être une erreur isolée ou le prix d'acheteurs mieux informés (suivi AIS, flux
   de bateaux déjà visibles) : on ne le saura qu'avec des règlements.
2. **Un seul événement** et des tranches liées (une seule valeur finale) : un règlement = une expérience, pas 4.
3. **Révisions de PortWatch** : les derniers jours publiés peuvent être corrigés ensuite ; les données téléchargées sont la version actuelle.
4. Frontières des tranches : « entre 20 et 24 » est lu comme [20, 25[ (Bab el-Mandeb) ; une valeur de 24,6 n'est pas tranchée par la règle.
5. Les jours manquants (19-31/10) pèsent pour 13 jours sur 13 : aucune information AIS pour ce détroit.

## Arène
`detroits_tranches` : achète le côté que le marché vend d'au moins 0,12 sous la loi (σ d'incertitude 0,12 pour tenir compte de
tout ce qui précède), quart de Kelly, un relevé PortWatch de moins de 12 h. Le 23/10 elle voit : NON de la tranche 25-29 (prix du
OUI 0,81, loi 0,51) et OUI de la tranche 20-24 (0,07 contre 0,28). Le règlement (≈ 5/11) donnera 2 paris réglés : à juger sans
conclure (leçon du 20/10 : un seul événement n'est pas un avantage).

## Reste ouvert
- Rejouer chaque mois : relever les prix Polymarket des tranches « average daily transits » dès leur création (aucun historique
  de prix n'existe), pour mesurer enfin l'erreur du marché.
- Un relevé AIS pour Bab el-Mandeb comblerait les 5 jours manquants (source non trouvée).
