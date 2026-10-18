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
- La famille vient du barème de frais (`politics_fees` ; sans frais = `sans_frais`, surtout la géopolitique, mais aussi santé ou séismes) ; le test, lui,
  utilisait les étiquettes Gamma : quelques marchés peuvent changer de famille.
- `naive_favorite` mise en Kelly complet : une seule perte sur un pari à 0,92 peut coûter 40 % du capital.

## 6. Nouvelles pistes (même données, même règle ; script `experiments/favori/pistes.py`)
| Piste | Résultat | Stabilité | Stratégie |
|---|---|---|---|
| Politique : SUIVRE un mouvement de plus de 0,05 en 6 h | +5,4 % (103 paris) ; plus de 0,10 : +10,1 % | +3,2 % puis +7,3 % ; 17 jours gagnants sur 26 | `suivre_politique` |
| Politique : CONTRER ce mouvement | −18 % à −35 % | — | (confirme : en politique, l'information se diffuse lentement) |
| Crypto à seuil : CONTRER un mouvement de plus de 0,05 en 6 h | +14,1 % (199 paris) ; 0,10 en 24 h : +29,8 % | +11,7 % puis +17,4 % ; 17 jours sur 29 ; achète surtout l'issue à moins de 0,30 | `contrer_crypto` (+ patiente) |
| Crypto hausse/baisse : contrer | +51,6 % puis −25,9 % | instable | écartée (`exclure_mots`) |
| Politique 0,97-0,995 (« presque acquis ») | +0,8 % après frais (99,6 % gagnés) ; 0,95-0,98 : +2,8 % | toutes tranches positives | `favori_politique_quasi_certain` |
| Météo : le « quasi certain » (≥ 0,95) des 6 dernières heures se retourne | 11 marchés sur 157 ; l'issue contraire à ≈ 0,005 gagne 4,5 % du temps | 11 cas : très fragile | `loterie_meteo` (mises minuscules) |

Essai à blanc (16/10/2026 au soir) : `contrer_crypto` achèterait 1 issue, la patiente en poserait 3 ;
`favori_politique_quasi_certain` achèterait 3 favoris à 0,97 (cessez-le-feu Russie-Ukraine non,
Lieberman Premier ministre non, accord d'Ormuz non) ; `loterie_meteo` 1 billet ; `suivre_politique`
rien (aucun mouvement de plus de 0,05 ce soir-là).
Famille « sans_frais » : un marché sans frais est surtout de la géopolitique, mais aussi santé ou
séismes ; les variantes politiques l'incluent.

## 7. L'heure de la journée (17/10/2026, `experiments/favori/heure.py`, 303 229 échanges réels)
Pas d'effet général : le favori 0,80-0,97 fait −1,8 % à +0,2 % selon la tranche horaire, et le week-end
ne diffère pas de la semaine (−1,1 % contre −1,0 %). Deux poches faibles, mises à l'essai dans l'arène :
- favori politique la nuit et le matin (4 h-12 h UTC) : +1,5 à +2,0 % → `favori_politique_nuit` ;
- outsider sportif l'après-midi et le soir (12 h-24 h UTC) : +8 à +10 % (négatif le matin) →
  `outsider_sport_apres_midi`.
L'outsider crypto perd à toute heure (−18 à −48 %).

## 6. En direct, deux jours plus tard (18/10/2026 au soir, AMELIORATION)
Journaux fantômes de la branche `data`, toutes les stratégies de la famille naive_favorite ; un
même pari pris par plusieurs variantes n'est compté qu'une fois ; paris réglés seulement.

| Prix payé | paris | gagnés | prix moyen | coût par part (frais) | estimation des stratégies |
|---|---|---|---|---|---|
| 0,50-0,85 | 32 | 78,1 % ± 7,3 | 0,822 | 0,828 | 0,875 |
| 0,85-0,90 | 47 | 91,5 % ± 4,1 | 0,874 | 0,879 | 0,924 |
| 0,90-0,93 | 47 | 78,7 % ± 6,0 | 0,913 | 0,917 | 0,961 |
| 0,93-0,96 | 34 | 100 % | 0,935 | 0,938 | 0,982 |
| **total** | **160** | **86,9 %** | | **0,893** | |

- Le favori ne gagne pas plus souvent que son prix (86,9 % pour 89,3 % payés) : même conclusion que
  le test sur le passé. L'estimation « prix + 5 points » est trop optimiste d'environ 6 points.
- Les fantômes affichent pourtant +11 à +14 % : chance et taille des mises (Kelly sur une
  estimation trop haute), pas un avantage. Le score de confiance de l'arène, calculé sur les
  euros, s'y laissait prendre ; il porte désormais sur le rendement par mise (ARCHITECTURE §41).
- Par stratégie (gagnés / attendus d'après les prix payés) : nf_sport_patiente 40 / 36,2
  (z = 1,7 : ses ordres posés achètent moins cher), nf_sport 24 / 23,4, nf_court 56 / 57,9,
  naive_favorite 13 / 13,9, nf_equipe 8 / 11,1.
- À suivre : si l'avantage de nf_sport_patiente tient (au-delà de 60 opérations), le prix d'entrée
  (ordre posé plutôt qu'achat immédiat) est la vraie source de gain du favori sportif.

