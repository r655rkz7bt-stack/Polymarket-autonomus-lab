# Piste n° 1 : `score_exact_poisson` (22/10/2026, midi)

**Question** : les marchés « Exact Score » du football sont-ils mal cotés par rapport aux marchés « vainqueur » (1X2) et « plus/moins 2,5 buts » du même match ?
Un modèle de Poisson (deux espérances de buts ajustées sur 1X2 et O/U 2,5) donne la chance de chaque score ; on achète le OUI sous-coté ou le NON sur-coté.

**Données** (scripts : `experiments/score_exact/`, données ignorées par Git)
- 9 654 matchs avec un événement `-exact-score` réglé (Gamma, tag soccer, 1er août → 21 octobre 2026) ; 3 471 avec au moins 3 000 $ de volume ;
  pour chacun : l'événement du match (1X2), `-more-markets` (totaux) et **les échanges réels des trois** (`data-api.polymarket.com/trades?eventId=`, 10 400 fichiers).
- Utilisables : 2 111 matchs (1X2 et plus/moins 2,5 échangés dans les 6 h avant T0, moins de 10 000 échanges par événement), 36 501 paris candidats (un marché-score, un côté).

**Protocole**
1. Contrôle du règlement : le score gagnant de l'événement (un seul marché à 1) redonne le résultat 1X2 réglé : **1 870 / 1 870** (T0 = coup d'envoi − 3 h) ; 2 249 / 2 249 (−1 h) ; 1 394 / 1 394 (−6 h).
2. Aucun regard vers le futur : probabilités du modèle = dernier échange de chaque issue **avant** T0 ; prix payé = premier échange d'achat (ou vente de l'autre issue) **entre T0 et le coup d'envoi**.
3. Contre le marché : log-score par marché-score (OUI/NON) : modèle −0,2301, marché −0,2307 (T0 = −3 h, n = 12 700) ; −0,2256 contre −0,2265 (−1 h) ; −0,2382 contre −0,2385 (−6 h). Le modèle est à peine meilleur : **les prix des scores exacts sont déjà
   ceux du 1X2 et du plus/moins 2,5** (le marché est cohérent avec Poisson) ; il n'y a presque aucun écart exploitable (80 paris sur 36 501 avec un écart modèle − prix > 0,02 côté OUI).
4. Achats simulés (frais `feeSchedule` du marché, prix = vrais échanges, pas d'écart supplémentaire) et `idea_test.verdict`, **4 réglages** de (T0, fenêtre) × 4 seuils d'écart = 16 cases côté OUI et 16 côté NON.

**Résultats** (T0 = coup d'envoi − 3 h, fenêtre 3 h)
| côté | prix payé | paris | gagnés / attendus par le prix | rendement par mise après frais |
|---|---|---|---|---|
| OUI | < 0,03 | 6 192 | 115 / 114,5 | −2,3 % |
| OUI | 0,03-0,08 | 8 483 | 399 / 432 | −9,7 % |
| OUI | 0,08-0,15 | 7 560 | 757 / 781 | −7,9 % |
| OUI | 0,15-0,30 | 662 | 102 / 122 | −19,5 % |
| NON | 0,70-0,90 | 1 566 | 1 361 / 1 361 | −0,6 % |
| NON | 0,90-0,97 | 8 000 | 7 467 / 7 498 | −0,7 % |
| NON | ≥ 0,97 | 3 876 | 3 801 / 3 808 | −0,3 % |
- Les trois autres réglages donnent la même image (OUI 0,03-0,15 : −3 % à −15 % ; NON 0,70-0,97 : −0,4 % à −4,8 %).
- Modèle > prix + frais + écart : OUI 0,02 : 80 paris (66 matchs), −32 %, t par match −1,3 ; NON 0,02 : 44 paris, −2,7 % ; NON 0,06 : 11 paris, +16 % (t +3,4 mais 9 matchs, et −3 % au réglage −1 h/1 h) → **écartée** dans les 16 cases.
- Par score (OUI à 0,02-0,50) : le modèle sous-estime légèrement les 3-1, 3-2 (gagnés 82 et 47 pour 73 et 40 attendus par les prix) et sur-estime les 2-0 / 1-3 (80 pour 106, 29 pour 43) : écarts de 1 à 2 écarts-types sur ~12 scores, pas de motif régulier.

**Verdict : écartée.** Le OUI des scores exacts perd plus que ses frais (le favori-outsider classique : ils gagnent moins que leur prix après écart achat-vente), le NON gagne exactement son prix moins les frais (−0,3 % à −0,7 %). Aucun écart modèle-marché
exploitable, aucune stratégie dans l'arène.

**Ce que ça dit de l'arène** : les NON d'« Exact Score » ne sont que 2 des 107 paris de `nf_sport_patiente` (relevé du 22/10 par type de marché sur Gamma : 89 « moneyline » = 7 434 € misés, 81 gagnés pour 77 attendus,
**+8 € soit +0,1 %** ; 18 paris « annexes » (child_moneyline, totaux, handicaps, exact score, totaux d'équipe) = +136 €). Le gain de la championne ne vient donc pas des scores exacts mais de 18 paris annexes sur 107 ;
sur 12 000 NON d'exact score de 0,70 à 1,00 le rendement est de −0,3 à −0,7 % : ce type de pari n'a pas d'avantage au prix.

**Reste** : les ~6 000 matchs de moins de 3 000 $ de volume (pas téléchargés, échanges trop rares), les totaux et les handicaps du `-more-markets` (même méthode, ligne par ligne, avec la loi de Poisson), le côté « en jeu ».
Scripts : `releve_evenements.py`, `releve_donnees.py` (reprise possible), `analyse.py DECAL FENETRE`, `simuler.py fichier`.
