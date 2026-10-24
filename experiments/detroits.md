# Piste 0b : les détroits (Ormuz, Bab el-Mandeb), 23/10/2026

Deux passages le même jour. Le premier (après-midi, PR #131) n'avait trouvé que 2 événements à tranches, tous deux ouverts :
verdict « indice » et fantôme `detroits_tranches`. Le second (soir, branche `claude/detroits`) a refait l'inventaire avec la
recherche Gamma : **96 événements réglés sur PortWatch, dont 58 événements à tranches clos**. Le test sur le passé devient
possible ; il est ci-dessous. Le compte rendu du premier passage est gardé à la fin.

## En bref
- **Question.** Les tranches « combien de bateaux » (somme sur une semaine, ou moyenne sur 7 jours à une date) sont-elles
  bien cotées ? Le modèle prolonge simplement la série du FMI : la somme d'aujourd'hui, multipliée par chacune des variations
  déjà vues au même horizon depuis 2019.
- **Verdict (`idea_test.verdict`) : RETENUE, mais sur peu d'événements.** 40 événements réglés de juin à octobre 2026,
  150 paris aux prix réellement payés : **+24 % par pari**, confiance par événement **2,13**, **z des prix 2,83**, 5 mois sur 5.
  Le réglage a été choisi parmi **16 essais** (4 modèles × 2 seuils × 2 hypothèses sur l'heure de publication). C'est le seul
  modèle qui tienne à toutes les épreuves ; les autres s'effondrent dès qu'on retire leurs 3 meilleurs paris.
- **Ce que le marché rate.** Il est trop sûr de la tranche du milieu et suit la tendance du moment. La loi tirée des
  variations passées est plus large : elle achète le NON de la tranche favorite trop chère et le OUI des tranches voisines bon marché.
- **Arène.** Nouveau fantôme `detroits_marche_log` (demi-Kelly), qui voit 22 marchés au cycle local et y a fait 7 achats.
  Pas d'inscription dans `validated_strategies` : 40 événements et 5 mois ne suffisent pas.

## Données
- **PortWatch** (`scripts/portwatch.py`, ArcGIS public du FMI, sans clé) : 2 848 jours (01/01/2019 → 18/10/2026), sans trou,
  pour Ormuz, Bab el-Mandeb, Suez et Panama. Le service connaît 28 passages.
- **Rythme de publication (mesuré)** : PortWatch se met à jour **une fois par semaine, le mardi**, jusqu'au dimanche précédent.
  Le 23/10, la dernière modification datait du mardi 20/10 à 10 h 51 UTC (champ `lastEditDate` du service) et le dernier jour
  publié était le 18/10. Les marchés hebdomadaires se règlent surtout le mardi après-midi UTC (20 sur 57 contrôlés à J+2, la plupart des
  autres entre le mercredi et le samedi qui suivent). Le « retard de 5 jours » noté par la veille est donc un retard de **2 à
  9 jours** selon le jour de la semaine.
- **Moniteur AIS** (`hormuz.data-tracking.net`, `/api/crossings/daily` et `/api/bab/daily`, 30 jours) : il couvre aussi
  Bab el-Mandeb, depuis le 23/09. Sur les 26 jours communs, il **ne suit pas** PortWatch. Corrélation des comptes quotidiens :
  0,1 à Bab el-Mandeb et 0,3 à Ormuz. Corrélation des sommes sur 7 jours : −0,42 et +0,5. On le relève, mais il ne sert pas
  à prévoir.
- **Inventaire** (`scripts/inventaire.py`, recherche `public-search` sur 13 mots-clés, ouverts et clos, puis relecture de chaque
  événement) : 234 événements trouvés, **96 citent PortWatch**.

| Type | Détroit | Clos | Ouverts | Grandeur réglée |
|---|---|---|---|---|
| tranches hebdomadaires « How many ships transit … week of … » | Ormuz | 32 | 2 | somme des passages du lundi au dimanche |
| | Bab el-Mandeb | 13 | 2 | idem |
| tranches « Avg. # of ships transiting … » (fin de mois ou un jour donné) | Ormuz | 10 | 1 | moyenne sur 7 jours publiée pour la date |
| | Bab el-Mandeb | 3 | 1 | idem |
| seuil « Will __ ships transit … on any day by … » | Ormuz | 8 | 1 | un jour ≥ N avant la date |
| seuil « traffic returns to normal by … » / « which month » | Ormuz | 11 | 4 | moyenne sur 7 jours ≥ 60 un jour avant la date |
| seuil « 0 ships transit … on any date by » | Ormuz, Bab | 1 | 1 | un jour à 0 |
| seuil « effectively closed by » | Bab, Panama | 0 | 2 | moyenne sur 7 jours ≤ 10 |
| Suez (« recover to pre-Houthi levels », « container ship transits ») | Suez | 4 | 0 | moyenne ≥ 70, sommes de porte-conteneurs |

## Contrôle du règlement (`scripts/controle_reglement.py`)
La somme des 7 jours finissant à la date D, lue dans la série d'aujourd'hui, redonne la tranche officielle :
- **40 événements sur 40 depuis juin 2026**, avec la lecture « plancher » : les tranches entières comme « 25 et 27 »,
  « 28 et 30 » ou « 220-229 » valent [bas, haut + 1[ ; les tranches jointives comme « 0 et 10 », « 10 et 20 » valent
  [bas, haut[. La lecture « arrondi » donne 39 sur 40.
- **7 sur 17 de mars à mai 2026** (Ormuz seulement). PortWatch a révisé ses chiffres depuis : la semaine du 27/04 compte
  86 passages aujourd'hui, contre 25-49 au règlement ; celle du 10/03, 17 contre 35-39. Ces 17 événements sont **exclus** du test.

## Protocole (`scripts/test_passe.py`, `scripts/analyse_paris.py`)
- **Instants de décision** : chaque jour à 12 h UTC, de la création du marché jusqu'à la publication de la date cible.
- **Données connues à T** : jours ≤ dimanche avant le dernier mardi. Hypothèse prudente retenue : la mise à jour du mardi
  n'est connue que le mercredi. L'hypothèse « mardi 11 h » donne des résultats voisins (voir `resultats_test_passe_mardi11h.txt`).
- **Prix connu à T** : dernier prix payé pour acheter ce côté dans les 24 h avant T (data-api).
- **Pari** si chance calculée − prix − frais > seuil. **Achat au premier échange réel dans les 2 h après T**
  (`taker_cost(..., after=True)`), un seul achat par marché (le premier signal), gardé jusqu'au règlement.
- **Frais réels** : 0. Ces marchés ont `feesEnabled` faux (457) ou sont en `zero_fees` (4). L'écart achat-vente est déjà
  dans les prix payés.
- **Événements** : 40 (Ormuz 20 hebdomadaires et 4 mensuels, Bab el-Mandeb 13 et 3), 57 587 échanges relevés.

## Réglages essayés : 16 (4 modèles × seuil 0,05 / 0,10 × publication mardi 11 h / mercredi)
Tableau sous l'hypothèse prudente (publication connue le mercredi) :

| Modèle | seuil | paris | rendement par pari | confiance par événement | z des prix | sans les 3 meilleurs | verdict |
|---|---|---|---|---|---|---|---|
| marche aléatoire, écarts en passages, 365 j | 0,05 | 150 | +15,6 % | 0,89 | 1,73 | −3,2 % | indice |
| idem | 0,10 | 118 | −2,3 % | −0,05 | 0,84 | −18 % | écartée |
| marche aléatoire, écarts relatifs, 90 j | 0,05 | 141 | +4,9 % | 0,49 | 1,19 | −8,8 % | écartée |
| idem | 0,10 | 122 | +22,8 % | 1,24 | 1,81 | +3,5 % | indice |
| **marche aléatoire, écarts relatifs, depuis 2019** | **0,05** | **150** | **+24,2 %** | **2,13** | **2,83** | **+11,8 %** | **retenue** |
| idem | 0,10 | 126 | +25,3 % | 1,86 | 2,80 | +10,5 % | retenue |
| loi normale « mélange » (premier passage, Bab el-Mandeb seul) | 0,05 | 44 | +66,6 % | 2,50 | 2,57 | +23,5 % | retenue |
| idem | 0,10 | 31 | +50,0 % | 1,59 | 1,44 | −4,0 % | indice |

Robustesse du réglage retenu (écarts relatifs depuis 2019, seuil 0,05) :
- **par détroit** : Ormuz +16,6 % (99 paris, 24 événements, t 1,21), Bab el-Mandeb +39 % (51 paris, 16 événements, t 1,88) ;
- **par moitié des dates** : +17,6 % avant le 15/08 (t 0,98), puis +30,3 % ensuite (t 2,08) ;
- sans le meilleur événement : +19,9 % (t 1,88) ;
- **par côté** : OUI +49 % (50 paris, prix moyen 0,31), NON +11,8 % (100 paris, prix moyen 0,77) ;
- **par type** : hebdomadaires +16,5 % (119 paris, 33 événements, t 1,43), mensuels +54 % (31 paris, 7 événements, t 2,4) ;
- **par prix** : < 0,10 : 3 paris, tous perdus ; 0,10-0,30 : +80 % ; 0,30-0,70 : +28 % ; ≥ 0,70 : +7 %.
  La stratégie exclut donc les billets sous 0,10 ;
- **prix payé contre prix connu** : +0,009 en moyenne. Le gain ne vient pas d'un prix périmé.
- **Juge de paix sur la seconde moitié** : si l'on choisit le réglage sur la première moitié des dates (meilleure confiance
  par événement : « mélange » 1,32, puis « relatif depuis 2019 » 1,0), les deux restent positifs sur la seconde moitié
  (+80 % et +30 %, t 2,4 et 2,1).

**Mise en garde.** En log-score, tous les modèles font en moyenne **moins bien que le marché** : de +0,03 à +0,23 par couple
(marché, instant), sur 2 207 couples. Le marché est mieux étalonné presque partout. Le gain vient des seuls endroits où la loi
large s'écarte nettement de lui (tranche du milieu trop chère, voisines trop bon marché). C'est un avantage étroit : il peut
disparaître si le marché apprend, ou si un changement de régime (Ormuz en mars) rend les variations passées trompeuses.

## Verdict et recommandation
- **Retenue, avec prudence.** Les seuils d'`idea_test.verdict` sont passés. Mais il n'y a que 40 événements sur 5 mois ; les
  semaines qui se suivent et les marchés mensuels chevauchent les mêmes jours ; et le modèle a été choisi parmi 4.
- **Fantôme `detroits_marche_log`** (`strategies_v3.DetroitsMarcheLog`, demi-Kelly, seuil 0,05, prix 0,10-0,95), avec les
  données de `references.attach_detroits_log` :
  - il couvre les tranches hebdomadaires et mensuelles des deux détroits, si la description cite PortWatch ;
  - la loi est `references.s7_draws` (rejouée sur les 150 paris du test : écart maximal de probabilité 0,0009,
    `scripts/coherence_production.py`) ;
  - le scanner lit désormais l'étiquette `hormuz` (104139) en plus de `bab-el-mandeb`.
- **Cycle local** (23/10, 18 h 43 UTC) : 22 marchés rattachés, 7 achats simulés. Relus à la main :
  - Bab el-Mandeb, semaine du 26/10 : OUI « 170-189 » à 0,18 (loi 0,49), NON « 190-209 » à 0,63 (loi 0,69),
    NON « 230 or more » à 0,81 (loi 0,99) ;
  - Bab el-Mandeb : NON « 190-209, semaine du 19/10 » à 0,61 (loi 0,70) et NON « 25-29 en moyenne au 31/10 » à 0,21 (loi 0,30) ;
  - Ormuz : OUI « 25-29, semaine du 19/10 » à 0,39 (loi 0,46), NON « fewer than 20, semaine du 26/10 » à 0,86 (loi 0,92).

  Les trois paris de la semaine du 26/10 à Bab el-Mandeb sont liés : ils gagnent tous si la somme tombe entre 170 et 189.
- **Ne pas** inscrire dans `validated_strategies` avant au moins 20 opérations réglées en direct (≈ 3 semaines : 4 événements
  par semaine).

## Le lecteur de source (`src/polymarket_agent/sources/portwatch.py`)
- `PortWatchSource` relève PortWatch, par pages de 1 000 lignes (le plafond du service), pour Ormuz, Bab el-Mandeb et tout
  passage nommé par un marché qui cite PortWatch (Panama, Suez…). Il lit aussi l'AIS en appoint.
- Il produit une observation par détroit, rattachée aux marchés dont la description cite PortWatch, et garde la série
  complète (`ref:portwatch`) pour les deux stratégies.
- Mode dégradé : un détroit en panne est sauté, l'AIS en panne ne bloque rien, et une panne totale rend la source
  « indisponible » sans arrêter le cycle.
- Réglages : `sources.portwatch` (`enabled`, `every_minutes: 120`, `days: 3000`, `ais`, `max_detroits`).
- Tests : `tests/test_portwatch.py`, avec des réponses simulées. Un essai réel a été fait le 23/10 : Ormuz 4 passages le 18/10
  (moyenne sur 7 jours 3,7) et Bab el-Mandeb 32 (moyenne 26,4).

## Reste à faire
1. **Seuils** (« on any day by », « returns to normal », « effectively closed », « 0 ships ») : 20 événements clos, dont
   les plus gros volumes (« returns to normal » : 6 à 44 M$). Ils ne sont pas testés : il faut une loi sur la trajectoire
   (maximum ou minimum d'une période), par exemple des blocs de jours tirés de l'historique.
2. **Course à la publication** : le mardi vers 11 h UTC, la valeur hebdomadaire devient connue, mais les marchés ne se règlent
   que vers 15 h. Il reste à mesurer, aux prix payés, si le marché tarde à s'ajuster entre ces deux heures.
3. **AIS** : refaire la corrélation avec PortWatch quand le recouvrement dépassera 60 jours.
4. Juger `detroits_marche_log` contre `detroits_tranches` dans l'arène : elles achètent parfois le même côté (NON 25-29 au 31/10).

---

## Premier passage (après-midi du 23/10/2026, avant l'inventaire complet)

**Verdict alors : INDICE FAIBLE (pas de preuve).** La loi calculée sur 2 ans d'historique donnait à la tranche favorite du
marché (25-29, Bab el-Mandeb fin octobre) 0,45-0,51, contre 0,81 le 23/10. Mais le marché ne cotait pas 0,81 pendant sa vie :
0,53-0,65 du 12 au 22/10 (loi 0,46-0,50), puis un saut à 0,71 et à 0,81 le 23/10. Fantôme `detroits_tranches` (quart de
Kelly), loi normale « mélange » (`references.ma7_forecast`) avec un garde-fou de régime (pas de loi pour Ormuz). Détail par
jour : `resultats_marche_contre_modele.txt`.

| Loi pour la moyenne du 31/10 | μ | σ | <20 | 20-24 | **25-29** | 30-34 | 35+ |
|---|---|---|---|---|---|---|---|
| marche aléatoire (écarts observés sur 24 mois) | 26,4 | 3,8 | 0,054 | 0,283 | **0,511** | 0,145 | 0,007 |
| normale, mélange (moyenne d'aujourd'hui + niveau 45 j) | 26,7 | 3,6 | 0,029 | 0,284 | 0,508 | 0,169 | 0,010 |
| **marché Polymarket (milieu du carnet, 23/10)** | | | 0,025 | 0,07 | **0,81** | 0,105 | 0,003 |

Le premier passage pensait qu'il n'existait que deux événements à tranches. L'inventaire du soir en trouve 58 clos : la
recherche par volume de `/events` s'arrêtait au décalage 2 100 et ne voyait pas les petits événements hebdomadaires.
