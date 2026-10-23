# Compteur de tweets aux prix payés (23/10/2026)

**Question** : la fille « NON sans NYC Mayor » du compteur de tweets (+12,8 % par période, t +3,9 au test du 21/10, `tweets_filles.md`) tient-elle
quand on l'achète **aux prix des vrais échanges** et non à l'historique horaire du CLOB + demi-écart ? C'est la seule piste « retenue » du labo qui n'avait pas
passé ce contrôle (règle de `queues_tranches.md` du 22/10 : prix « milieu » de tranches peu liquides non exécutables).

**Données** (scripts : `experiments/tweets_prix_payes/`, données dans `donnees/`, ignorées par Git) : 224 périodes hebdomadaires de 7 comptes (juillet à
21/10/2026), dont 196 trouvées sur Gamma (Elon et Trump n'ont des événements hebdomadaires que depuis août) ; **317 361 échanges réels** (data-api, 11 000
au plus par événement : les événements les plus actifs sont tronqués côté anciens) ; messages XTracker. Modèle de `compteur_tweets` inchangé
(`references.tweet_bucket_probability`, dispersion 12, 7 + 14 jours), décisions toutes les 6 h comme au test d'origine.

**Contrôle du règlement** : la tranche gagnante calculée avec nos messages égale la tranche payée par Polymarket pour toutes les périodes sauf 4 (écartées).

**Méthode** : prix connu à la décision = dernier échange du jeton NON dans les 6 h qui précèdent ; achat si le NON estimé − 0,03 dépasse ce prix et que
le billet vaut au moins 0,10. **Prix payé = premier échange du jeton NON dans les 2 h qui suivent** (pas d'échange : pas d'achat). Frais = barème Gamma
du marché (0,05·p·(1−p)).

## Résultats (A + D : NON, sans NYC Mayor ; moyenne par période, t de la moyenne par période)
| réglage (dispersion / marge / prix min / avant / après) | achats (périodes) | par achat | par période (t) | sans 3 meilleures |
|---|---|---|---|---|
| 12 / 0,03 / 0,10 / 6 h / 2 h (référence) | 1 286 (150) | −2,1 % | **−0,1 % (−0,02)** | −5,5 % |
| 12 / 0,03 / 0,10 / 6 h / 6 h | 1 961 (153) | +0,1 % | −2,7 % (−0,63) | −6,5 % |
| 12 / 0,03 / 0,10 / 6 h / 12 h | 2 290 (157) | +1,8 % | −3,0 % (−0,70) | −6,5 % |
| 12 / 0,03 / 0,10 / 2 h / 1 h | 704 (126) | −3,5 % | −5,3 % (−0,90) | −10,9 % |
| 8 / 0,03 / 0,10 / 6 h / 2 h | 1 320 (149) | −2,9 % | −0,7 % (−0,13) | −6,1 % |
| 16 / 0,03 / 0,10 / 6 h / 2 h | 1 295 (150) | −1,2 % | +1,6 % (+0,32) | −3,6 % |
| 12 / 0 / 0,10 / 6 h / 2 h | 1 811 (155) | −2,5 % | −1,6 % (−0,42) | −5,7 % |
| 12 / 0,05 / 0,10 / 6 h / 2 h | 1 061 (146) | −2,2 % | −0,6 % (−0,10) | −6,2 % |
| 12 / 0,03 / 0,20 / 6 h / 2 h | 1 262 (147) | −1,4 % | +2,9 % (+0,62) | −2,4 % |

Neuf réglages : les neuf sont entre −5,3 % et +2,9 % par période, t entre −0,9 et +0,6 (contre +8,0 à +15,9 %, t +2,9 à +4,5 sur l'historique horaire).
Par mois (référence) : juillet −17 %, août +1 %, septembre +1 %, octobre −1 %. Par compte : aucun ne se détache (WhiteHouse −17 % par période, t −1,6 ;
cz_binance +19 %, t +0,9 sur 26 périodes). Gagnés/attendus par les prix : 870 / 887,7 (le NON gagne un peu **moins** que son prix).
**Témoin** : les mêmes signaux achetés au dernier prix d'échange connu + 0,02, sans exigence d'échange après : −1,6 % par période (t −0,47), 1 887 gagnés
pour 1 891,5 attendus : le prix d'échange suffit à faire disparaître le gain, ce n'est pas l'exigence d'exécution (53 % des signaux n'ont pas d'échange dans les
2 h suivantes : marchés très peu liquides, 100 à 1 400 échanges par événement).

## Verdict : **écartée aux prix payés** (l'« avantage » de +12,8 % était le prix horaire du CLOB, pas un prix qu'on peut payer)
Quatrième piste de suite faussée de la même façon (météo 16/10, mentions 21/10, tranches du 22/10, tweets 23/10) : tout test de marchés à tranches se refait aux
prix des échanges avant d'être appelé « retenu ». Conséquences :
- `compteur_tweets*` restent en arène comme fantômes (l'arène confirmera ou non en direct, 7 + 4 + 12 paris réglés au 23/10) mais **ne sont à mettre ni dans
  `validated_strategies` ni au principal** sur la foi de `vingt_pistes.md` / `tweets_filles.md`.
- Limites : les 100 à 1 400 échanges par événement sont rares ; un acheteur qui poserait un ordre (au lieu d'acheter à l'échange) obtiendrait un meilleur prix,
  non testé ici (la file d'attente est inconnue : voir `chiffres_ronds.md`).
