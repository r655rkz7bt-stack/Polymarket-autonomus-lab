# 31/10/2026 (midi) : 34 paris de `moins_de_cartes` sur 53 non copiés par le principal (famille 2 + constat « à regarder »)

Question : depuis le 28/10 12 h, le principal a-t-il refait les paris de `moins_de_cartes` (part 3,1 %) ? Jeton par jeton, journaux signés publiés (`published_data/ledger/`), sauvegarde de la base du jour.

## Constat
53 jetons achetés par le fantôme depuis le 28/10 12 h : 19 copiés, 34 non. Les 34 se répartissent en deux causes très différentes :

| Cause | Jetons | Preuve |
|---|---|---|
| **Budget de la part épuisé** (30-31/10) | 10 | le principal avait 14,2 à 18,2 € engagés dans la stratégie pour un budget d'environ 14-18 € (part × capital) ; les copies reprennent dès que des positions se règlent (30/10 17 h : 0 € engagé → copié) |
| **Hors du principal** (29/10 02 h → 17 h) | **24** | 0 € engagé par le principal, 550 € de liquidités, aucun refus noté (`refus_principal` ne contient que 2 « budget trop juste ») : la stratégie n'était simplement pas dans la composition du principal |

## Cause de la deuxième série (pas un défaut de code)
Rejeu du score de confiance t (rendement par mise des opérations clôturées du fantôme) : **0,99 à 03 h-06 h le 29/10**, pour un seuil d'entrée `min_t_stat: 1.0` (`config/promotion.yaml`), puis 1,16 à 12 h, 1,26 à 16 h (retour du principal : première copie le 29/10 à 17 h 08).
`arena.allocation` ne donne le seuil de MAINTIEN (`keep_t_stat: 0`) qu'au champion (`kept`) : toute autre stratégie du principal doit repasser le seuil d'entrée à chaque recalcul, donc une stratégie qui oscille autour de t = 1,0 sort et rentre (« va-et-vient » que le commentaire du fichier dit vouloir éviter).

## Chiffrage
Les 22 paris réglés du fantôme dans la fenêtre (29/10 02 h → 17 h) : 16 gagnés pour 12,0 attendus par les prix ; copiés à 5 parts (la copie habituelle) : mise 60 €, gain **+12,5 €** manqué. Petit, et en partie de la chance (z ≈ +1,2).

## Décision
Aucun correctif : abaisser le seuil de maintien des non-champions desserre le garde-fou `min_t_stat` (leçon de `meteo_prevision` à t = 0,61, `experiments/promotion.md`) et se prouve par un rejeu de l'historique de l'arène (non publié) avant d'être écrit. Pas de contrôle automatique non plus : l'historique des compositions du principal n'est pas dans les données publiées.
**Reste ouvert** : si ce va-et-vient revient (une stratégie bien étayée absente du principal plus de 6 h alors que son t reste entre 0,8 et 1,0), proposer un seuil de maintien de 0,7 pour les membres, après un rejeu.

## Vérifié sans défaut
- Budget, liquidités, plafond de famille (sport < 25 % du capital pour un plafond de 40 %) : pas en cause.
- Mise copiée : 5 parts à chaque fois (plancher de copie du 26/10), prix identiques au fantôme à ±0,01.
- Part 3,08 % au 31/10, avantage mesuré 4,8 % (ratio 1,36) : la part n'est pas à zéro par construction (`mise_avantage_mesure.part_min: 0`).
Scripts : lignes de calcul dans cette fiche (journaux publiés), aucune donnée à télécharger.
