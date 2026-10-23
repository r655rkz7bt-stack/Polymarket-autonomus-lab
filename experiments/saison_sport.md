# Piste « gagnant de saison » : le NON des candidats à 10-30 % (23/10/2026, passage chercheur de la nuit)

**Question** : dans un marché « Qui gagnera le championnat / le MVP / le Ballon d'Or ? » (un candidat = un marché OUI/NON), le OUI d'un candidat à 10-30 % gagne-t-il moins souvent que son prix,
au point que son NON (80-90 centimes) rapporte après frais et écart ? Naissance de la piste : la championne a pris ce type de marché par erreur (enquête `2026-10-23_marches_de_saison_dans_le_sport.md`,
359 € sur « Mbappé, NON ») sans qu'aucun test ne le couvre.

**Données** (scripts dans `experiments/saison_sport/scripts/`, données dans `donnees/`, ignorées par Git) :
- 120 événements de sport clos (Gamma, `tag_slug=sports`, neg-risk, ≥ 5 candidats, volume ≥ 20 000 $, hors « X vs Y ») : champions NBA/NHL/MLB/NFL, Ligue des champions, Coupe du monde, Premier League, F1, MVP,
  golf, tennis, e-sport ; 3 927 candidats, 2 754 avec ≥ 2 000 $ de volume ; 2024-2026 ;
- prix horaire du OUI (CLOB `prices-history`, fenêtre d'un jour) à 3, 7, 14, 30 et 60 jours avant la clôture de l'événement (8 434 relevés, 6 753 décisions avec un prix de moins de 12 h) ;
- vrais échanges (data-api, par marché) des candidats à 0,10-0,30 à 7 et 14 jours : 196 marchés, premier achat du NON dans les 1/3/6 h après la décision ;
- **contrôle du règlement** : 119 événements sur 120 ont exactement un OUI gagnant (le 120e, « Where will Tyreek Hill play in 2026 ? », n'en a aucun) ; règlement lu dans Gamma (`outcomePrices`),
  donc identique au règlement officiel par construction ;
- pas de regard vers le futur : le prix est le dernier connu à l'instant de décision ; les frais sont `rate × p × (1 − p)` (0 pour les événements de 2025, 0,03 en 2026) ;
- Pas de comparaison avec un bookmaker (Pinnacle : piste n° 1, crédits de cotes limités).

**Résultats**
1. *Gagnés contre attendus par les prix* (NON, tranche de OUI 0,10-0,20) : H = 3 j 46/42,9 ; 7 j 70/63,1 ; 14 j 55/51,9 ; 30 j 100/98,0 ; 60 j 107/108,8. Rendement après écart d'1 ¢ et frais :
   +5,5 %, +9,8 %, +5,8 %, +2,0 %, −2,9 %. Le OUI des candidats à 10-20 % est surtout trop cher près de la fin ; à 2-5 % et 5-10 % rien (±1 %) ; favoris à 50-80 % : le NON perd (−23 % à −43 %), c'est l'inverse (OUI +10 à +18 %).
2. *Robustesse* (72 réglages : horizon 7/14/30, tranches 0,10-0,20 / 0,10-0,30 / 0,15-0,30, écart 0,01/0,02, 2025/2026, sans les 3 meilleurs événements) : à 14 jours 0,10-0,30, rendement +8,2 % (91 gagnés pour 84,2 ; t par événement +3,0),
   +6,5 % sans les 3 meilleurs événements, 2025 +10,9 % et 2026 +8,0 % ; à 30 jours +0,2 % ; à 7 jours +5,8 % mais **tout vient d'un seul événement** (« Uniswap Cup », 32 candidats, somme des OUI > 1,15) : sans lui +2,6 % (61/59,3).
   Gain de l'horizon 14 jours : 5 meilleurs couples (événement, horizon) = 51 % du gain.
3. *Aux prix de vrais échanges* (premier achat du NON dans les 6 h après la décision, 196 marchés) : payé 0,813 contre 0,809 au prix horaire (le prix horaire est exécutable) ; H = 14 j, 0,10-0,30 : n = 75, 67 gagnés pour 61,0, **+9,9 %**
   (t par événement +3,0) ; H = 7 j : n = 59, +9,6 % mais pas robuste (même événement) ; fenêtre 1 h : +8,2 % (n = 46).
4. **Réglages essayés** : environ 120 (30 + 72 + 18), corrélés (les mêmes marchés reviennent à plusieurs horizons). Le meilleur est un maximum parmi ces essais.

**Verdict : indice faible** (pas « retenue », malgré `idea_test.verdict` qui dit « retenue » à 14 jours)
- pour : le sens est le même aux horizons 3 à 14 jours pour les OUI à 10-20 %, aux prix de vrais échanges, en 2025 comme en 2026, et il correspond à un biais connu (candidats « possibles » surcotés près de la fin) ;
- contre : un seul horizon survit à la retraite de l'événement louche (14 jours), pas à 30 ni à 60 jours ; ~120 réglages ; 51 % du gain porté par 5 couples ; z des prix seulement +1,8 sur 75 paris ; 120 événements, quelques sports seulement.

**Arène** : fantôme `saison_non` (NON d'un candidat à 10-30 % dans un marché de saison, 10 à 18 jours avant la fin, quart de Kelly, biais 0,03), via le nouveau filtre `un_match: false`. À confirmer sur ≥ 100 paris réglés avant de la croire.
Les marchés de ce type sont rares (une dizaine d'événements ouverts en même temps) : il faudra des semaines.

**Suite possible** : (a) ajouter les événements non marqués « sports » (prix de la saison des films, élections à plusieurs candidats : même structure, déjà vue dans `queues_tranches.md`) ;
(b) comparer à Pinnacle (The Odds API, piste n° 1) pour savoir si le prix des candidats à 10-20 % est faux ou si c'est un biais favori/outsider ; (c) dès la fin du Ballon d'Or (27/10), regarder les 5 paris ouverts de la championne.

## Autre résultat du même passage : tennis en jeu, hors échantillon
`experiments/tennis_oos/` : même méthode que `tennis.md` (décision à +15 et +30 min, favori à 0,80-0,95, prix du premier échange d'achat dans les 10 min) sur les **matchs commencés après le 20/10 16 h UTC** (629 matchs :
523 ITF, 90 ATP, 16 WTA ; 43 et 51 paris). +30 min : 43 gagnés pour 44,7 attendus, **−4,5 %** (t par événement −0,7) ; +15 min : −9,5 %. Trop peu de matchs pour trancher (écart-type ≈ 5 %) : l'« indice » du 20/10 (+3,1 %) n'est ni confirmé ni infirmé.
Le fantôme `nf_tennis_debut_match` dit la même chose : 46 paris, 40 gagnés pour 40,1 attendus (+70 € = mises plus grosses sur les gagnés, pas un meilleur taux de réussite). À refaire avec ≥ 500 nouveaux matchs ATP/WTA (octobre-novembre : saison indoor, peu de matchs).
