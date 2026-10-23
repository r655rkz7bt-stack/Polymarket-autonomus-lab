# Fatigue NHL aux prix payés (23/10/2026)

**Question** : l'indice `fatigue_nhl` (équipe qui joue le soir après avoir joué la veille, adversaire reposé : +6,1 %, t +1,2 sur 299 matchs, `vingt_pistes.md`) a été mesuré avec
le prix CLOB « une heure avant le match ». Tient-il aux prix des vrais échanges (même défaut que les tweets, la météo, les mentions) ?

**Données** (scripts : `experiments/nhl_prix_payes/`, données ignorées par Git) : calendrier officiel de la NHL (api-web.nhle.com) du 29/09/2024 au 22/10/2026 : 3 063 matchs, dont
2 894 joués avec score ; 2 404 rattachés à un marché « vainqueur du match » de Polymarket (nom des équipes + date) ; **3 271 545 échanges réels** (data-api, filtre `market=<conditionId>`,
donc tout l'historique du seul marché). Les marchés clos sont lus par `gamma /events/keyset` (le `offset` de `/events` s'arrête à 2 100 depuis peu : il ne rendait que 879 matchs).
**Contrôle du règlement** : le jeton « visiteur » payé par Polymarket redonne le vainqueur du score officiel pour tous les matchs gardés (les autres sont écartés).

**Méthode** : T = coup d'envoi − H ; prix connu = dernier échange dans les `avant` heures qui précèdent ; **prix payé = premier échange du jeton de l'adversaire reposé dans les `après` heures qui
suivent T** ; frais 0,05·p·(1−p) (taux prudent pour le sport). Aucun regard vers le futur (calendrier : seuls les matchs de la veille).

## Résultats (équipe visiteuse fatiguée, adversaire reposé à domicile : on achète l'adversaire)
| H (h) | avant (h) | après (h) | achats | par achat | t | adversaire gagne / attendu | par saison 24-25 / 25-26 / 26-27 |
|---|---|---|---|---|---|---|---|
| 1 | 6 | 1 | 373 | +5,9 % | +1,27 | 230 / 214,6 | +8 % / +4 % / +7 % |
| 3 | 6 | 1 | 364 | +6,7 % | +1,43 | 226 / 209,6 | +8 % / +5 % / +14 % |
| 6 | 12 | 2 | 366 | +5,9 % | +1,26 | 225 / 210,1 | +9 % / +4 % / 0 % |
| 0,5 | 3 | 0,5 | 365 | +6,3 % | +1,35 | 226 / 210,5 | +9 % / +4 % / +7 % |
| 1 | 6 | 3 | 373 | +5,9 % | +1,27 | 230 / 214,6 | idem |

Cinq réglages (H 0,5 à 6 h, délais 0,5 à 3 h) : **+5,9 % à +6,7 %, t +1,26 à +1,43, trois saisons dans le même sens** (la 3e : 28 matchs). Presque aucun match sans échange (NHL liquide :
des centaines d'échanges par match), donc aucune sélection par l'exécution. Témoins : « fatigué à domicile » 128 achats, −2,6 % (t −0,3) ; les deux équipes fatiguées 115 achats, +9,8 % (t +1,1) ;
aucune fatigue 1 749 achats, −1,8 % (t −0,8, les frais du sport).
L'équipe fatiguée en déplacement gagne 5,2 points de moins que son prix (écart du prix connu −0,052).

## Verdict : **indice confirmé aux prix payés, pas retenue**
Le défaut des tweets (prix horaire non exécutable) ne s'applique pas ici, le résultat est le même qu'au test d'origine avec 25 % de matchs en plus (373 contre 299). Mais t reste à +1,3 (z des victoires
+1,6, un seul effet cherché, cinq réglages regardés) : sous le seuil de 2 qui permettrait d'entrer dans `validated_strategies`. Le fantôme `fatigue_nhl` continue ; ~190 matchs par saison :
il faut ~2 saisons de plus pour trancher en direct. Rien à changer dans l'arène.
