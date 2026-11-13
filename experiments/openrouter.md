# Jetons d'OpenRouter dans la semaine (piste n° 50, 13/11/2026, passage de 6 h)

**Marchés** : « OpenRouter token usage week of <lundi>? » (événement hebdomadaire, 5 tranches de 10 T, 500-1 100 $ de liquidité par
tranche, frais `tech_fees` 0,04·p(1−p), étiquettes ai 439 / tech 1401 : déjà dans le scan). Règle lue mot à mot : total hebdomadaire
du graphique « Top Models » de openrouter.ai/rankings, semaine du lundi 00 h au dimanche 23 h 59 UTC, figé quand la semaine
suivante apparaît ; arrondi d'affichage compris ; pile sur une borne → tranche du dessus.

## La source, lue directement (robots.txt : « Allow: / »)

La page charge ses données depuis une API sans clé (trouvée dans les fichiers JavaScript de la page) :
- `api/frontend/v1/rankings/model-rankings-chart` : le graphique lui-même, 53 semaines (`x` = lundi, `ys` = jetons par modèle +
  « Others ») ; la semaine en cours = jours FINIS (relevé de 06 h 00 UTC le vendredi : lundi → jeudi, 134,43 T) ;
- `api/frontend/v1/rankings/models?view=week` : 7 derniers jours finis par modèle (6 → 12/11 : 209,67 T) ;
- `api/frontend/v1/rankings/models?view=day` : dernier jour fini (12/11 : 32,63 T).
Relevé du graphique gardé : `openrouter/releve_graphique_2026-11-13T0600.json`.

Semaines récentes (T) : 28/09 165,9 ; 05/10 171,8 ; 12/10 164,0 ; 19/10 188,0 ; 26/10 193,6 ; 02/11 209,5 ; 09/11 134,4 en 4 jours.

## Projection

7 derniers jours − jours finis de la semaine = fin de la semaine précédente (vendredi-dimanche 6-8/11 : 75,24 T) ; semaine
précédente − cette fin = son début (lundi-jeudi 2-5/11 : 134,28 T). Cette semaine a fait 134,43 T du lundi au jeudi (+0,1 % sur la
précédente : la croissance de 4-8 % par semaine s'est arrêtée) ; si elle finit comme la précédente : **209,75 T**, pile sur la borne
210. Autres estimations : même fin de semaine que la précédente en valeur → 209,7 ; fin de semaine poussée par la croissance des 4
dernières semaines (+6 %) → 214,2 ; jeudi (32,63) plus faible que la moyenne lundi-jeudi (33,6) → ≈ 207,5. Médiane ≈ 209,7 ;
marché : « 200-210 » 0,26 / 0,39, « 210-220 » 0,51 / 0,67 (le marché met ≈ 0,74 au-dessus de 210, la projection ≈ 0,5).

(Erreur corrigée en cours de passage : j'avais d'abord additionné une seule des dates de la vue des 7 jours, 206,0 au lieu de
209,67, ce qui donnait 204 T et une fausse certitude sur « 200-210 ». Un total se relit sur toutes les lignes.)

## Semaines réglées (`openrouter/releve_marches.py`, `semaines_passees.py`)

Cinq semaines réglées retrouvées (28/09, 05/10, 19/10, 26/10, 02/11). Prix des tranches le vendredi, le samedi et le dimanche à
06 h UTC : le marché avait la bonne tranche en favori 3 fois (05/10, 19/10, 02/11) ; le 28/09, il préférait 160-165 (0,365) le
dimanche, réglé 165,9 ; le **26/10, « 195-205 » payé 0,575 le vendredi et 0,895 le dimanche, réglé 193,6** (le marché a surestimé le
week-end). Cinq semaines ne prouvent rien ; aucun historique quotidien public (Wayback bloqué par le proxy) : pas de test aux prix
passés possible.

## Verdict : expérience (fantôme `openrouter_semaine`)

Source ajoutée au cycle (`openrouter.py`, relue chaque heure ; journal `openrouter:histo` : un point par jour fini, première et
dernière lecture, pour voir si le graphique est révisé et étalonner la fin de semaine). Fantôme à Kelly entier sur la borne basse
(chance − 0,04), 4 % du fantôme au plus par pari, avantage net exigé 0,06 : le 13/11 il n'achète pas (« 200-210 » ≈ 0,48 contre un
vendeur à 0,39 + frais). Une perte apprendrait que la fin de semaine ne copie pas la précédente, ou que le graphique bouge après coup.

À relire : le total final de la semaine du 9/11 (affiché lundi 16/11) contre 209,75 ; la forme vendredi-dimanche semaine après
semaine dans `openrouter:histo` ; les marchés « Which company has the highest OpenRouter market share » (même API :
`rankings/author-market-share`).
