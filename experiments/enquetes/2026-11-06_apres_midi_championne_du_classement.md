# 06/11 après-midi — la n° 1 du classement (`nf_sport_prix_haut`) gagne-t-elle contre ses prix ? (famille 2)

**Question** : la feuille de mission classe `nf_sport_prix_haut_v1.0.0` première (croissance log +0,298, 670 paris
réglés, 1 347 €). Son gain vient-il d'un avantage ou de la chance ?

**Méthode** : journal signé du fantôme (`published_data/`), un pari par jeton (`charge_fantome.charger`),
paiement réel par part (`pay`), prix moyen payé (`prix`).

| mesure | valeur |
|---|---|
| paris réglés | 670 |
| gain | +346,9 € sur 36 415 € misés (+0,95 % par mise) |
| gain sans ses 3 plus gros paris | +268,4 € |
| payé / attendu par les prix | 612,5 / 609,0 (+3,5 parts sur 670) |
| meilleur jour | 27/10 : +174 € ; pire jour 30/10 : −203 € |

**Lecture** : le gain ne dépend pas de 3 paris et le fantôme n'est pas un coup de chance isolé, mais il gagne
exactement autant que ses prix l'annoncent (+3,5 sur 612). Le +0,95 % par mise est ce que rapporte un favori
à 0,90 quand les prix sont justes et que Kelly pousse la mise ; les deux jours extrêmes (+174 / −203) montrent
la variance. Même constat que `champion_sans_avantage` (README, 26/10) : pas un défaut, pas un avantage prouvé.

**Autres relevés du passage** : `cdc_historique.py` a ajouté la ligne du 05/11 (5 182 cas ; 3 mercredis au total,
il en faut ~8 pour tester la piste rougeole) ; le fichier Géorgie 2026 répond encore 404.

**Aucun défaut.**
