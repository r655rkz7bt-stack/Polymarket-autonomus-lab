# Argent informé : un portefeuille gagnant continue-t-il de gagner ? (16/10/2026)

**Réponse courte : non.** Les meilleurs portefeuilles du passé ne font pas mieux que les autres
ensuite, et les copier avec 5 minutes de retard (notre cycle) perd de l'argent après frais.
Idée écartée ; pas de stratégie.

## Données (publiques, sans clé)
- 16 680 marchés résolus net à 1/0, échéance du 15/09 au 15/10/2026, volume ≥ 20 000 $ (Gamma,
  `/events?closed=true`, jour par jour).
- 2 859 764 échanges d'au moins 100 $ sur ces marchés, 51 232 portefeuilles
  (`data-api.polymarket.com/trades?market=<conditionId>&filterType=CASH&filterAmount=100&takerOnly=false`).

## Méthode (sans regard vers le futur)
- **Classement** : seuls les marchés résolus AVANT le 1er/10 comptent. Gain d'un échange jusqu'à
  la résolution : achat = parts × (issue − prix) ; vente = parts × (prix − issue). Rendement =
  gain / capital engagé. Portefeuilles classés : au moins 20 échanges sur au moins 5 marchés
  (6 227 portefeuilles).
- **Jugement** : les échanges passés APRÈS le 1er/10 par ces mêmes portefeuilles.
- **Copie** : chaque échange est reproduit 5 minutes plus tard, au prix du premier gros échange du
  même jeton au moins 5 minutes après, avec un écart ajouté de 0 / 0,01 / 0,02 et les frais du
  preneur estimés par catégorie (crypto 0,07 ; sport 0,05 ; politique, finance, tech 0,04 ;
  géopolitique 0 ; autres 0,05).

## Résultats
| Groupe (classé avant le 1er/10) | rendement avant | actifs après | échanges après | rendement après |
|---|---|---|---|---|
| top 1 % | +73,3 % | 36 / 62 | 2 475 | **−9,7 %** |
| top 10 % | +30,1 % | 484 / 622 | 33 281 | **−4,3 %** |
| milieu 40-60 % | +0,3 % | 1 017 / 1 246 | 416 725 | −0,1 % |
| pires 10 % | −33,5 % | 459 / 622 | 28 198 | −5,1 % |
| tous | | 20 326 | 1 140 167 | −0,1 % |

Corrélation des rangs avant / après (Spearman, 4 101 portefeuilles actifs des deux côtés avec au
moins 10 échanges après) : **+0,04**, c'est-à-dire presque rien.

| Copie avec 5 minutes de retard | paris | rendement des mises | jours gagnants |
|---|---|---|---|
| top 1 %, sans écart | 2 208 | −11,3 % | 3 / 15 |
| top 1 %, écart 0,02 | 2 265 | −15,0 % | 2 / 15 |
| top 10 %, sans écart | 29 290 | −2,3 % | 3 / 16 |
| top 10 %, écart 0,02 | 30 524 | −6,2 % | 3 / 16 |
| pires 10 %, sans écart | 22 278 | −2,5 % | 5 / 16 |

**Lecture** : le classement d'un mois récompense surtout la chance (et quelques gros paris
gagnants). Les « meilleurs » font ensuite aussi mal que les « pires ». Copier, même sans écart,
perd à peu près les frais.

## Limites (honnêtes)
- Un seul mois de classement et deux semaines de jugement.
- Au plus 5 000 gros échanges par marché (les plus récents) : les plus anciens échanges des très
  gros marchés manquent.
- Seuls les échanges d'au moins 100 $ sont vus. Le prix de copie est celui du gros échange suivant,
  pas le carnet.
- Ce test ne dit rien des portefeuilles « initiés » rares (un seul gros pari avant une nouvelle) :
  il en faudrait une autre mesure (par exemple les gros achats juste avant un mouvement de prix).

## Refaire le test
```
python3 -I experiments/smart_money/collect.py <dossier_de_travail> src   # ≈ 40 min la 1re fois
python3 -I experiments/smart_money/evaluate.py <dossier_de_travail> [AAAA-MM-JJ de coupure]
```
