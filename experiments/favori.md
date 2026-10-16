# Pourquoi `naive_favorite` gagne-t-il ? (16/10/2026)

**Question d'Etienne** : « Aujourd'hui, la stratégie qui fonctionne le mieux, c'est la naïve favorite.
Pourquoi ? Développe l'idée, trouve tous les aspects qui peuvent fonctionner. »

## 1. Ce qu'elle a fait en vrai (arène, 15-16/10/2026)
`naive_favorite` achète le favori (l'issue la plus chère, vendue entre 0,80 et 0,95) des marchés
surveillés, en supposant qu'il vaut 5 points de plus que son prix. Elle mise beaucoup (Kelly complet :
jusqu'à 40 % du capital sur un seul pari).
- 26 achats, **8 marchés réglés : 7 gagnés, 1 perdu**, prix moyen d'achat ≈ 0,92.
- Capital estimé : 1 078 (+7,8 %).

**Lecture honnête** : à 0,92 de prix moyen, un marché JUSTE fait gagner 7,4 paris sur 8 en moyenne.
7 sur 8, c'est exactement ce qu'on attend, plus un peu de chance. Le gain vient surtout de la TAILLE des
mises (Kelly complet sur des paris presque sûrs), pas d'un avantage prouvé. 8 paris ne prouvent rien :
il en faut des centaines. D'où le test sur le passé ci-dessous.

## 2. Le test sur le passé (prix réellement payés)
Script : `experiments/favori/analyse.py` (données d'`experiments/smart_money` : 16 680 marchés résolus
du 15/09 au 15/10/2026, 2,86 millions d'échanges d'au moins 100 $). Pour chaque marché et chaque
instant de décision (0,5 h à 7 jours avant l'échéance ANNONCÉE, ce que voit le bot), prix du dernier
échange avant cet instant ; favori = issue la plus chère ; rendement = issue − prix − frais preneur.

**Piège évité** : mesuré par rapport à la clôture RÉELLE (connue après coup), le favori semblait
gagner 30 min avant la fin (+4 %) ; par rapport à l'échéance annoncée, ce gain disparaît (−7 %). Savoir
qu'un match « va finir dans 30 min », c'est déjà connaître l'avenir.

### Résultat général : le favori n'est PAS sous-coté en moyenne
| Prix du favori | paris | prix moyen | gagnés | écart | rendement après frais |
|---|---|---|---|---|---|
| 0,80-0,85 | 1 844 | 0,821 | 0,797 | −2,4 pts | −3,8 % |
| 0,85-0,90 | 1 626 | 0,871 | 0,848 | −2,3 pts | −3,3 % |
| 0,90-0,95 | 2 083 | 0,922 | 0,914 | −0,8 pt | −1,3 % |
| 0,95-0,98 | 2 055 | 0,965 | 0,957 | −0,8 pt | −1,0 % |
(tous instants confondus ; avec l'échéance annoncée, la plage de naive_favorite fait −1 à −8 %).
Le célèbre « biais favori / outsider » (favoris sous-cotés) n'existe pas en général sur Polymarket.

## 3. Les raisons possibles, une par une
| # | Raison | Ce que disent les données | Verdict |
|---|---|---|---|
| 1 | **Chance** (petit échantillon) | 7/8 à 0,92 = attendu | **principale explication du résultat actuel** |
| 2 | **Taille des mises** (Kelly complet) | gros paris presque sûrs : le capital monte vite… et chutera vite à la première perte | vrai, c'est un risque |
| 3 | Biais favori / outsider général | favoris trop chers de 1 à 2 points en moyenne | **non** |
| 4 | **Politique et géopolitique** | favori 0,85-0,97 : 97,6 % gagnés pour 92,2 % de prix, **+5,7 % après frais** ; 379 paris, 47 jours gagnants sur 54, 110 événements ; positif à tous les instants, dans toutes les tranches de prix, sur les deux moitiés de la période (+3,5 % puis +2,8 %) et avec 1 centime d'écart en plus (+4,8 %) ; élections +6,4 %, guerre et décisions +10,7 %, tweets d'Elon Musk +2 % | **oui, la seule poche solide** |
| 5 | « Il ne se passe jamais rien » (favori NON) | favori NON −0,8 %, favori OUI −0,5 % (hors politique, rien) | non (sauf en politique) |
| 6 | Prime de patience (marchés lointains) | 72 h et plus : +4,3 pts mais surtout grâce à la politique ; ailleurs faible (crypto +3,6 % sur 126 paris) ou négatif (sport −3,9 %) | faible |
| 7 | **Fin de partie = piège** | favori 0,80-0,97 dans les 6 dernières heures : sport −7,4 %, crypto −6,5 %, météo −13,6 % (un favori encore à 0,88 si près de la fin a une vraie raison de l'être) | **oui (à éviter)** |
| 8 | **Outsider sportif sous-coté** (miroir) | en sport, le favori 0,80-0,95 gagne 5 points de moins que son prix ; l'outsider gagnerait +34 % des mises… mais surtout avec des prix périmés (+47 %), seulement +12,8 % avec des prix de moins de 10 min, et irrégulier selon les ligues | **fragile, à tester** |
| 9 | Frais faibles sur le favori | frais = taux × p × (1 − p) : 0,4 centime à 0,90 contre 1,25 à 0,50 | aide un peu, ne suffit pas |
| 10 | Marchés peu échangés | prix vieux de plus d'1 h : pires (−4 %) | non |

**Pourquoi la politique ?** Hypothèses (non prouvées, plausibles) : des partisans paient leur
candidat ou le scénario qu'ils espèrent (un outsider politique a des fans, pas un match de tennis) ;
le goût du scénario spectaculaire (guerre, démission) ; moins de bots rapides qu'en sport et en
crypto ; l'argent reste bloqué des semaines, ce que beaucoup refusent pour gagner 5 à 10 %.

## 4. Les stratégies créées (une par raison ; l'arène juge)
| Stratégie | Raison testée | Réglages |
|---|---|---|
| `naive_favorite` (inchangée) | point de comparaison | 0,80-0,95, partout |
| `favori_politique` | n°4 | politique + géopolitique, 0,85-0,97, estimation = milieu + 0,5 × (1 − milieu) (l'écart mesuré vaut 0,7), jamais dans les 6 dernières heures, Kelly 0,5, 40 marchés politiques demandés au scanner |
| `favori_politique_patiente` | n°4 + frais et écart économisés | même chose, achat POSÉ 1 cran au-dessus du meilleur acheteur |
| `naive_favorite_sans_fin` | n°7 | naive_favorite, mais jamais à moins de 24 h de l'échéance (du coup d'envoi en sport) |
| `outsider_sport_patiente` | n°8 | outsider sportif 0,08-0,20, POSÉ, seulement 30 min à 24 h avant le coup d'envoi (Gamma `gameStartTime`) |

Essai à blanc le 16/10/2026 au soir (vrais carnets, rien enregistré) : `favori_politique` aurait
acheté 3 favoris (cessez-le-feu US-Iran au 24/10 à 0,87, île de Perim à 0,90, Bennett pas Premier
ministre à 0,89) ; `outsider_sport_patiente` aurait posé 3 achats d'outsiders avant leur match.

## 5. Limites (honnêtes)
- Un seul mois de données (15/09-15/10/2026) ; les événements politiques de ce mois (élections au
  Brésil, en Russie, en Allemagne ; guerre au Moyen-Orient) ne se répètent pas forcément.
- Plusieurs marchés d'un même événement sont liés (110 événements pour 223 marchés politiques).
- Prix d'échange (≥ 100 $) et non prix du vendeur du carnet : l'écart réel peut être plus grand.
- La famille vient du barème de frais (`politics_fees`, sans frais = géopolitique) ; le test, lui,
  utilisait les étiquettes Gamma : quelques marchés peuvent changer de famille.
- `naive_favorite` mise en Kelly complet : une seule perte sur un pari à 0,92 peut coûter 40 % du capital.
