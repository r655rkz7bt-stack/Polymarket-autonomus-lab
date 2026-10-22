# Piste n° 8 `courbe_de_risque` : le NON des « échelles de dates » (22/10/2026)

**Question** (reformulée) : les marchés « X d'ici <date> ? » (au moins 4 échéances pour un même événement) sont-ils mal cotés selon la distance à l'échéance ?
Le test direct de la piste (ajuster une courbe de risque, acheter la date qui sort de la courbe) demande d'abord de savoir si les prix s'écartent de la réalité d'une façon qu'on peut payer ;
on mesure donc le rendement du NON et du OUI de **chaque** échéance, à H jours avant la sienne, aux prix des vrais échanges.

**Données** : Gamma, événements clos du 01/03 au 22/10/2026 avec ≥ 4 marchés dont la question contient « by / through / before » et un volume ≥ 5 000 $ : **1 062 échelles**,
leurs **échanges réels** (data-api). Prix payé = premier échange de preneur dans les 6 h après T = échéance − H jours (marché déjà né depuis 1 h), plage 0,03-0,97, frais du marché.
Scripts : `experiments/courbe_de_risque/` (`releve.py`, `analyse.py`, `detail.py`, `verdict.py`, `resultats.txt`). Règlement : `outcomePrices` ≥ 0,99 (marchés pas nets écartés).
Catégories par mots du titre (géopolitique, sorties, mots de Trump, autre ; les lancements de jetons n'ont donné qu'un cas : leur échéance Gamma est trop éloignée ou sans échange).

## Résultats (≈ 45 réglages regardés : 2 côtés × 4-6 horizons × 2 bandes de prix, plus catégories et mois)
- **OUI** (acheter la date) à 7 / 14 / 30 jours : **−11,3 % / −13,1 % / −17,0 %** (z des prix −2,5 / −2,3 / −2,9) ; géopolitique −38 à −43 % (z −2,3 à −2,9, 86-60 paris). Le OUI d'une échelle se paie trop cher.
- **NON** : 3 j −0,3 % ; 7 j +0,7 % ; 14 j +0,5 % ; 21 j +5,2 % ; **30 j +9,3 % (z +3,2)** ; 45 j +0,7 % ; 60 j −8,2 % (52 paris).
  Avec `idea_test.verdict` (confiance par événement, rendement par euro misé) : 30 j **indice** (+11,8 %, 352 paris, 185 événements, t événement +1,18, z des prix +3,2, 8 mois sur 11) ;
  prix ≤ 0,85 : +16,3 % (228 paris, 143 événements, t +1,25) ; 21 j +7 à +9 % (t événement +0,3-0,4), **7 et 10 jours négatifs (t événement −1,8 à −2,1)**. Les 10 autres réglages : « écartée ».
- Par tranche de prix du NON à 30 j : < 0,70 +20,1 % (z +2,7), 0,70-0,85 +6,7 %, 0,85-0,95 +6,8 %, ≥ 0,95 −5,2 %. Par mois à 30 j : 8 positifs sur 11 (juin −8 %, mai +25 %).
- Les paris d'une même échelle sont liés (les échéances proches se ressemblent) : le z des paris est surévalué, la confiance par événement (+1,2) est la bonne mesure ; elle reste en dessous de 1,5.

**Verdict : indice, fragile.** Le OUI des échelles est trop cher à 3-5 semaines de l'échéance (cohérent aux horizons 7-30 jours), mais l'avantage du NON n'est net qu'à un seul horizon et tombe
en dessous de 1,5 de confiance par événement ; il n'existe pas à 7-14 jours. Pas de preuve → **fantôme `echelle_non`** (NON, OUI à 15-85 %, 504-960 h avant l'échéance, Kelly 0,25) pour confirmer
sur de nouveaux paris. Pas encore testé : la courbe de risque elle-même (la date qui sort de la courbe), les lancements de jetons (échéances Gamma à revoir), un test hors échantillon (les mois
les plus récents ne sont pas mis de côté ici : il faut les nouveaux paris du fantôme).
