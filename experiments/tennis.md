# Piste n° 1 : tennis, d'où vient l'avantage de la championne ? (20/10/2026, passage chercheur ~15 h UTC)

**Question** : le favori d'un match de tennis gagne-t-il plus souvent que son prix, et à quel moment du
match (avant le début, en jeu) ? Les 84 % d'achats « en jeu » de la championne (enquête du même jour)
rendaient la question utile : 90 % de ses paris de tennis sont des favoris à 0,80-0,95.

**Données** (scripts dans `experiments/tennis/scripts/`, données dans `donnees/`, ignorées par Git) :
- 6 131 matchs de tennis réglés, juillet-octobre 2026 (Gamma, séries ATP 10365 / WTA 10366 / ITF 11634,
  marché `moneyline`) : ATP 2 050 (sept.-oct.), WTA 2 026 (juil.-oct.), ITF 2 055 (oct.).
- historique de prix CLOB (pas de 10 min) de J-24 h à +4 h autour du coup d'envoi (`gameStartTime`) ;
- vrais échanges (data-api) de 1 857 événements dont le favori valait 0,80-0,95 à +15 ou +30 min.
- **Contrôle du règlement** : sur 2 263 matchs dont l'historique couvre la fin du match, le dernier prix
  (> 0,97 ou < 0,03) donne le même vainqueur que le règlement Gamma dans 2 261 cas.
- Pas de regard vers le futur : chaque décision utilise le dernier prix connu à son instant ;
  Sackmann (classements) inaccessible depuis cet environnement (dépôt non autorisé), donc pas d'écart
  de classement : question traitée par prix, circuit et moment du match seulement.

**Résultats**
1. *Avant le match* (J-1 h, 5 987 matchs) : le favori gagne 4 050 fois pour 4 092 attendus (z −1,2). Par
   tranche, les favoris à 0,50-0,70 gagnent **moins** que leur prix (−2,6 pts, z −2,4 / −2,0) et ceux à
   0,70-1,00 **plus** (+1 à +3,5 pts ; 0,90-1,00 : +3,4 pts, z +3,2) : le biais « favori sous-coté » est réel
   mais petit. Achats simulés (écart 1 ¢ + frais) : favori 0,80-0,95 **+0,6 %** (t par match +0,6),
   favori 0,50-0,80 −6 %, outsider −9 %. Rien à gagner avant le match.
2. *Contre le marché* (log-score, apprentissage sur la 1re moitié, test sur la 2e) : recalibrer le prix
   (logit × 1,1 à 1,2) **ne bat pas le prix** hors échantillon (−2,2 nats sur 3 037 matchs avant le match ; −0,4
   à +2,5 nats pour les favoris 0,80-0,95). Pas de probabilité meilleure que celle du marché.
3. *En jeu* (instantané à +15 min … +120 min, prix de l'historique) : les favoris à 0,80-0,95 gagnent plus
   souvent que leur prix à +15 et +30 min (z +3,4 / +3,6), mais pas à +60 et +90 min (z +1,8 / +1,5).
4. *En jeu, aux prix réellement payés* (premier échange d'achat dans les 10 min suivant la décision, frais
   `rate × p × (1−p)`) :
   | décision | paris | payé moyen | gagnés | rendement | t par match | mois |
   |---|---|---|---|---|---|---|
   | +15 min, 0,80-0,95 | 793 | 0,865 | 708 | +2,8 % | +2,1 | 4 sur 4 sauf août (−0,8 %) |
   | +30 min, 0,80-0,95 | 1 096 | 0,869 | 986 | **+3,1 %** | **+2,8** | 4 sur 4 positifs |
   | +30 min, 0,875-0,95 | 518 | 0,905 | 486 | +3,3 % | +2,7 | 4 sur 4 |
   Par circuit à +30 min : ATP +3,8 % (452), WTA +2,9 % (535), ITF +0,5 % (109, marchés minces).
   Par moitié de période : 1re +4,5 %, 2e +1,6 % (l'avantage s'érode).

**Combien de réglages essayés** : environ 40 (3 retards × 5 tranches avant le match, 3 × 2 camps × 3 tranches
d'achat, 4 réglages contre le marché, 5 retards × 3 tranches en jeu, 4 réglages aux vrais prix). Le
meilleur (+30 min, t +2,8) est un maximum parmi ces essais : avec ~40 réglages corrélés, un t de 2,8 se
rencontre par hasard environ une fois sur trois à quatre. D'où la prudence du verdict.

**Verdict : indice** (pas « retenue », malgré le critère `idea_test.verdict` qui dit « retenue » à +30 min)
- pour : l'effet a le bon signe pour tous les retards 15-30 min, tous les mois, ATP et WTA, aux prix réellement
  payés ; il correspond au biais favori/outsider connu ;
- contre : +3 % par mise est faible (un écart de 1 à 2 ¢ le fait disparaître), il décroît dans le temps (+4,5 % →
  +1,6 %), il n'apparaît pas hors de la fenêtre 15-30 min, le recalibrage ne bat pas le marché hors échantillon,
  ~40 réglages essayés, 4 mois seulement.
- **Ce que ça dit de la championne** : ses paris de tennis suivent le même biais favori/outsider (+3 % par pari à
  0,80-0,95), pas un avantage caché : son +4,3 % par mise sur l'ensemble du sport est de l'ordre de ce biais,
  sa série du 18/10 est de la chance.

**Arène** : fantôme `nf_tennis_debut_match` (favori de tennis, victoire, 0-36 min après le coup d'envoi, achat
immédiat) ; test de la fenêtre (`tests/test_favori.py`). L'arène confirme ou infirme avec ses propres paris
(≥ 100 paris avant de la croire).

**Reste ouvert** : écart de classement (Sackmann) ; même test sur le tennis de table et le e-sport (en jeu,
mêmes fenêtres) ; tester le biais favori/outsider pour les cartes (CS2) ; refaire ce test dans un mois, avec
les paris de l'arène comme échantillon sans sélection.
