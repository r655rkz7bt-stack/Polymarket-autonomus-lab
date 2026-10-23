# Brésil, 2e tour du 25/10/2026 : pistes 15 et 16 (étude du 22/10/2026)

**En bref, pour Etienne.**
- **Piste 15 (`depouillement_officiel`) : non.** Au 1er tour, Polymarket avait déjà fixé le prix du
  vainqueur (0,97 ou plus) **bien avant** que le résultat soit mathématiquement certain. Après ce moment
  (+10 min), sur 31 marchés et toute la soirée, seulement **35,88 $** ont été achetés à 0,97 ou moins.
- **Piste 16 (`etats_comme_avant`) : non.** Dans 22 États sur 28, le prix dit déjà ce que dit
  l'histoire (le 1er du 1er tour à 0,99 ou plus). Dans les 6 États serrés, nos trois références
  officielles ne sont pas d'accord entre elles ; aucune n'est « clairement » contre le marché.
- **Rien n'est donc ajouté à l'arène** : il n'y a pas de preuve d'un avantage. Les scripts restent
  prêts pour la prochaine élection.

## 1. Dates et candidats (vérifiés)

- Fichier officiel du TSE `ele-c.json` : « Eleição Ordinária Federal - 2026 2º Turno », **25/10/2026**,
  code d'élection **6258** (1er tour : 6257, le 04/10/2026).
- Fichier du 2e tour (déjà en ligne, 0 % compté le 22/10) : **FLAVIO BOLSONARO (n° 22)** et **LULA (n° 13)** ;
  499 248 bureaux, 158 745 502 électeurs.
- 1er tour (TSE, officiel) : Flávio 47,03 % (56 104 503 voix), Lula 45,16 % (53 879 538), Augusto Cury
  2,89 %, Renan Santos 2,24 %, Ronaldo Caiado 2,18 %. Flávio 1er dans 15 États, Lula dans 12 + l'étranger.
- Bureaux fermés à 17 h heure de Brasília (20 h UTC) dans tout le pays.

## 2. Marchés Polymarket du 2e tour (Gamma, 22/10)

Tous se terminent le 26/10 à 03:59 UTC, barème `zero_fees` (**aucun frais**, taux 0), marchés « negRisk ».

| Événement | id | Volume | Liquidité | Prix (22/10) |
|---|---|---|---|---|
| Brazil Presidential Election (vainqueur) | 45915 | 191 M$ | 1,47 M$ | Flávio 0,785 ; Lula 0,215 |
| Second Round: Margin of Victory (tranches de 4 points) | 1138953 | 4,3 M$ | 0,92 M$ | Flávio <4 % 0,415 ; 4-8 % 0,335 ; Lula <4 % 0,185 |
| Second Round: Specific Margin of Victory (tranches de 2 points) | 1220826 | 11 k$ | 264 k$ | Flávio 2-4 % 0,315 ; 4-6 % 0,31 |
| Second Round: 1st Place in <État> (27 États + « Abroad ») | 1137666-1137817 | de 2 k$ à 542 k$ (Amapá) | 25-414 k$ | tableau §5 |
| Turnout, Most Votes Ever, São Paulo City, Rio City | 1138935, 1142234, 1220827, 1220828 | petits | | |

Règles (citées comme données, extraits) :
- État : « *This market will resolve according to the listed candidate who receives the most valid votes in
  the second round of this election from <État>* » ; égalité départagée par ordre alphabétique ; source :
  « *a consensus of credible reporting. If there is ambiguity, … the official results as reported by … the
  Superior Electoral Court (TSE) (e.g., https://dadosabertos.tse.jus.br/)* ».
- Marge : « *the absolute difference between the percentages of valid votes received by the first- and
  second-place candidates* » ; valeur exactement sur une borne → tranche supérieure ; « *based on the
  official vote count once the vote count has been made official* ».
- Les marchés « Candidate A…E / Other » des États sont des cases vides (inactives).
- Au 1er tour, les marchés d'État payaient des frais `politics_fees` (0,04 × p × (1 − p)), et le
  plus serré (Amapá) n'a été réglé que le 08/10 (contestation UMA possible quand c'est très serré).

## 3. Accès aux données du TSE (testé d'ici le 22/10)

| Quoi | Adresse (publique, sans clé) | Résultat |
|---|---|---|
| Liste des élections et codes | `https://resultados.tse.jus.br/oficial/comum/config/ele-c.json` | 200, 26 Ko |
| Résultat d'un État (président) | `https://resultados.tse.jus.br/oficial/ele2026/<code>/dados/<uf>/<uf>-c0001-e00<code>-u.json` (`uf` = ac…to, `br`, `zz` = étranger) | 200, 3-9 Ko, 0,3-0,7 s |
| Avancement de chaque État | `…/ele2026/<code>/dados/br/br-e00<code>-ab.json` | 200, 27 Ko |
| Archives officielles (votes par commune, historiques) | `cdn.tse.jus.br/estatistica/sead/…` (portail dadosabertos.tse.jus.br, API CKAN `api/3/action/package_show`) | 200, requêtes partielles acceptées |

- Exemple lu le 22/10 : `ele2026/6258/dados/br/br-c0001-e006258-u.json` → `s.pst = "0,00"` (0 % des
  bureaux), `e.esnt = 158745502` (électeurs pas encore comptés), Flávio et Lula à 0 voix.
- Champs utiles pendant le dépouillement : `s.pst` (% des bureaux comptés), `e.esnt` (électeurs des
  bureaux non comptés), `cand[].vap` (voix). Test « mathématiquement décidé » : avance > `esnt`.
- Cache du serveur : `cache-control: max-age=40` (le fichier a jusqu'à 40 s de retard).
- Les anciens chemins 2022 (`ele2022/544/dados-simplificados/…`) répondent 404 : il faut passer par le
  portail de données ouvertes.
- **Depuis GitHub Actions** : non vérifié. La sortie de cette session est aux États-Unis (ipinfo : US) et
  le site répond ; c'est bon signe, pas une preuve (les adresses de GitHub peuvent être traitées autrement).
- Non joignable d'ici : web.archive.org (connexion coupée), donc pas d'instantanés du soir du 1er tour.

## 4. Piste 15 : vitesse de Polymarket au 1er tour → **non**

Méthode (`bresil_second_tour/vitesse_premier_tour.py`, résultat `vitesse_premier_tour.json`) :
- 31 marchés du 1er tour : 27 États + étranger (1re place), vainqueur national, marge, deux tranches de
  part des voix (Flávio 45-48 %, Lula 44-47 %, qui se décident tard). Échanges RÉELS du vainqueur
  (data-api `/trades`, preneurs ; couverture complète vérifiée pour chaque marché).
- « Achetable à p » = un preneur a vraiment ACHETÉ le vainqueur à p.
- Heure de fin du dépouillement de chaque État : fichier officiel `br-e006257-ab.json`.
- Moment « mathématiquement décidé » : la chronologie officielle 2026 n'est pas publiée ; estimée avec
  la chronologie officielle 2022 du TSE (`Historico_Totalizacao_Presidente_BR_1T_2022.csv`, Brésil entier :
  10 % comptés à +94 min, 50 % à +158 min, 90 % à +215 min, 99 % à +315 min) et la marge finale 2026
  (part à compter f* = 1 / (1 + marge × votes valides / électeurs)), au plus tard à 100 % compté.

Résultats :

| Marché | Marge finale | Décidé (estimé) | Dernier achat ≤ 0,97 | Dernier achat ≤ 0,99 |
|---|---|---|---|---|
| Vainqueur du 1er tour (Flávio) | 1,87 pt | +301 min | **+124 min** | +144 min |
| Tranche Flávio 45-48 % | – | +301 min | +145 min | +186 min |
| Tranche Lula 44-47 % | – | +287 min | +157 min | +1361 min (15 $) |
| Amapá (Lula) | 0,05 pt | +242 min (100 %) | +243,5 min | +1189 min |
| Amazonas (Lula) | 3,2 pts | +275 min | +202 min | +202 min |
| Minas Gerais (Flávio) | 4,9 pts | +260 min | +858 min (36 $) | +1155 min |
| Pará (Lula) | 5,4 pts | +253 min | +74 min | +74 min |
| Tocantins (Flávio) | 7,0 pts | +234 min | +52 min | +207 min |
| 21 autres États | 13 à 48 pts | +170 à +217 min | aucun après 17 h | vainqueur déjà à 0,98-0,999 avant 17 h |

- Le vainqueur national passe de 0,35 (17 h) à 0,88 (+50 min) et 0,99 (+140 min), alors que la
  certitude mathématique n'arrive qu'à environ +300 min : **le marché devine bien avant que le calcul tranche.**
- Achats du vainqueur après « décidé + 10 min », 31 marchés ensemble : **35,88 $ à ≤ 0,97** (1 achat),
  0 $ à ≤ 0,95, 2 017 $ à ≤ 0,99 (13 achats, surtout Amapá et Minas). Gain possible à 0,99 : ~1 % de
  2 000 $, soit ~20 $ pour toute la soirée, avant concurrence.
- Cas le plus favorable (Amapá, 0,05 point d'écart) : dernier achat ≤ 0,97 1,3 min après le 100 % ;
  ensuite 0,987-0,989 (~1 350 $) pendant 20-30 min. Petit, et lié au risque de contestation.
- Au 2e tour, le dépouillement est plus rapide (2022 : 90 % à +129 min, 99 % à +181 min) : le moment
  « décidé » arrive plus tôt, mais le marché converge encore plus tôt. Même conclusion que `fin_de_match`.
- Variante non testée : prévoir le résultat final à partir des résultats PARTIELS (modèle par région,
  comme les médias le soir de l'élection). La fenêtre existe (0,35 → 0,97 en 2 h), mais il faudrait la
  chronologie 2026 bureau par bureau (archives brutes de plusieurs Go) : hors de portée avant le 25/10.

## 5. Piste 16 : un État vote-t-il « comme avant » ? → **non (pas d'écart clair)**

Taux de base officiels (`base_historique.py`, TSE « votação nominal por município e zona », membre
présidence lu à distance, 2006, 2010, 2014, 2018, 2022 ; 140 cas État × élection, sans le « VT » de 2010) :

| Marge du 1er tour entre les deux finalistes | Cas | Le 1er du 1er tour perd au 2e | Garde |
|---|---|---|---|
| 0-2 points | 5 | 3 | 40 % |
| 2-5 points | 16 | 3 | 81 % |
| 5-10 points | 17 | 3 | 82 % |
| 10-20 points | 26 | 1 (GO 2006) | 96 % |
| 20 points et plus | 76 | 0 | 100 % |

Bascules observées : 2006 AC, DF, GO, RO (vers Lula) ; 2010 ES, GO, RS (vers Serra) ; 2014 RS ; 2018 TO ;
2022 AP (Lula +2,3 → Bolsonaro +2,7). Elles suivent presque toujours le sens du mouvement national.

Trois références pour P(Flávio 1er dans l'État) (`etats_comme_avant.py`) :
1. **table** ci-dessus ;
2. **bascule uniforme** : marge du 1er tour + mouvement national + écart propre (σ = 5,5 points, 2006-2022).
   Mouvement national pris au marché « marge » : Flávio +3,1 ± 3,4 points (contre +1,87 au 1er tour) ;
3. **comme en 2022** (même affiche Lula contre un Bolsonaro) : σ de 2022 = 2,0 points et penchant propre
   de chaque État au 2e tour 2022.

Prix exécutables lus le 22/10 à 10:46 UTC (meilleur vendeur, $ disponibles à 1 centime près), frais 0 :

| État | Marge t1 (F − L) | Table | Uniforme | Comme 2022 | Flávio : vendeur ($) | Lula : vendeur ($) |
|---|---|---|---|---|---|---|
| Amapá | −0,05 | 0,60 | 0,57 | 0,74 | 0,73 (122 529 $) | 0,29 (1 517 $) |
| Amazonas | −3,24 | 0,19 | 0,38 | 0,39 | 0,40 (600 $) | 0,62 (5 017 $) |
| Étranger | −4,08 | 0,19 | 0,33 | 0,19 | 0,26 (16 $) | 0,73 (447 $) |
| Minas Gerais | +4,91 | 0,81 | 0,83 | 0,96 | 0,939 (2 856 $) | 0,062 (78 $) |
| Pará | −5,41 | 0,18 | 0,26 | 0,09 | 0,15 (1 174 $) | 0,87 (3 588 $) |
| Tocantins | +7,02 | 0,82 | 0,90 | 0,98 | 0,999 (600 $) | 0,007 (1,5 $) |
| 22 autres (13 à 48 pts) | | 0,96-1,00 ou 0-0,04 | ≈ 1 ou 0 | ≈ 1 ou 0 | 1er du t1 à 0,990-0,999 | l'autre à 0,004-0,03, quelques $ |

Lecture :
- **États tranchés** : le marché est déjà d'accord avec l'histoire (0/76 bascule au-delà de 20 points).
  Acheter le favori à 0,99-0,999 rapporte 0,1 à 1 % en 3 jours, et une seule surprise efface tout : rien à prendre.
- **États serrés** : les écarts dépendent de la référence choisie. Exemple : Amapá, Lula « bon marché »
  de 11-14 points selon la table et la bascule uniforme, mais la référence « comme en 2022 » (l'Amapá avait
  déjà basculé vers Bolsonaro en 2022) donne 0,74 pour un prix de 0,73. Même chose en Amazonas (0,39
  contre 0,40). Les références se contredisent de 10 à 20 points entre elles : on ne peut pas dire que
  le marché se trompe. Il dispose en plus des sondages par État, que nos références ignorent.
- Tocantins : les trois références donnent Lula au-dessus de 0,007, mais il n'y a que 1,5 $ à vendre : inexploitable.
- Mesure en fantôme : au plus 4 à 6 paris liés (le même soir, presque tous « Lula »), loin des 12
  opérations clôturées nécessaires ; pas de valeur de mesure.

## 6. Verdicts et limites

| Piste | Verdict | Chiffre clé |
|---|---|---|
| 15 `depouillement_officiel` | **écartée** | 35,88 $ achetables à ≤ 0,97 après « décidé + 10 min » sur 31 marchés |
| 16 `etats_comme_avant` | **écartée** | 22/28 États déjà au prix de l'histoire ; États serrés : références contradictoires |

Limites honnêtes :
- Chronologie du dépouillement 2026 non publiée ; celle de 2022 ne couvre que le Brésil entier : le
  moment « décidé » de chaque État est une estimation (même vitesse partout, avance constante).
  Cela ne change pas la conclusion : le prix du vainqueur atteint 0,97 bien avant, même pour le national.
- Échanges preneurs seulement ; les offres non exécutées ne sont pas visibles (comme `fin_de_match`).
- Accès au TSE depuis les machines de GitHub non vérifié.
- Taux de base : 140 cas, dont 21 seulement sous 5 points ; les sondages par État ne sont pas utilisés.
- Prix des carnets : un seul instantané (22/10, 10:46 UTC).

## Refaire

```
.venv/bin/python -I experiments/bresil_second_tour/tse.py 6257          # résultats officiels par État
.venv/bin/python -I experiments/bresil_second_tour/vitesse_premier_tour.py
.venv/bin/python -I experiments/bresil_second_tour/base_historique.py   # taux de base 2006-2022
.venv/bin/python -I experiments/bresil_second_tour/etats_comme_avant.py # prix actuels (carnets relus)
```
Téléchargements bruts dans `experiments/bresil_second_tour/donnees/` (ignoré par git). Pour le soir du
25/10, `tse.py 6258` lit le 2e tour.
