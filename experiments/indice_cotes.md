# Tranches de l'indice PredictionMarketOdds (« <X> odds <a>-<b>% on <date>? ») — piste n° 65 (15/11/2026, indice faible)

Passage du chercheur de 21 h (15/11/2026). Idée neuve (« cohérence entre marchés liés » + « lire la règle ») : Polymarket ouvre des
**dérivés** (étiquette `derivatives`, 100418) réglés sur l'indice horaire de PredictionMarketOdds.com, une moyenne pondérée par la
liquidité des médianes horaires de Polymarket, Kalshi, Betfair, PredictIt, Smarkets, Gemini. Le sous-jacent est donc un PRIX
coté toute la journée, très lent (les démocrates en 2028 : 66,4 → 67,8 % en 7 jours) ; les tranches de 2 points sur 5 jours
devraient se calculer, pas se deviner.

## Source
- `predictionmarketodds.com/robots.txt` : 404 (aucune règle) ; `scripts/robots_ok.py` : permis. Page « methodology » lue.
- `latest.json` (toutes les listes, valeur publiée ET valeur brute, poids et médiane de chaque plateforme) ;
  `latest/<liste>.json` ; `details/<liste>__<option>.json` = 168 dernières heures seulement (pas d'historique long).
- Arrondi : « round half up to 0.001 » ; règle Polymarket : une valeur pile sur une borne va à la tranche du dessus ; fenêtre qui
  finit à 12 h (heure de l'Est) le jour dit.

## Données (`experiments/indice_cotes/scripts/`)
- `releve.py` : `public-search` → 104 événements, **35 réglés sur PredictionMarketOdds** (18 clos) : 10 « Democratic Senate odds
  on <date> » (25/09 → 02/11), 1 « Democratic 2028 presidential odds on November 6 », 2 « leader », 5 barrières (« hit __ by »).
- Sous-jacent : `prices-history` du marché Polymarket (Sénat 2026 démocrate, présidentielle 2028 démocrate), pas l'indice
  lui-même (pas d'historique long). **Contrôle du règlement** : la valeur Polymarket à l'heure du règlement redonne la tranche
  gagnante 7 fois sur 11 ; les 4 autres fois (Sénat, septembre-octobre) Polymarket était 0,5-1,5 point AU-DESSUS de l'indice
  (Kalshi, PredictIt plus bas avant l'élection). Aujourd'hui (présidentielle 2028) Polymarket 0,675, Kalshi 0,675, indice 0,6745.
- `rejeu.py` : à J-1, J-2, J-3, J-5, loi empirique des variations du sous-jacent sur le même horizon, apprise sur les 90 jours
  AVANT la décision ; prix de décision = dernier point horaire du CLOB de chaque tranche.
- `vrais_echanges.py` : pour chaque signal, premier achat preneur du côté voulu dans les 6 h après T (3 210 échanges, 60
  tranches) et parts achetées à ≤ ce prix + 0,02 (profondeur).

## Résultats
Log-score (somme sur les tranches, moyenne par événement) :

| délai | événements | modèle | prix |
|---|---|---|---|
| J-1 | 10 | −1,295 | −1,629 |
| J-2 | 8 | −1,559 | −2,890 |
| J-3 | 6 | −2,000 | −2,701 |
| J-5 | 4 | −2,995 | −2,651 |

Achats aux vrais échanges (écart modèle − prix ≥ seuil, 27 cellules : 3 délais × 3 seuils × 3 profondeurs) :

| délai | seuil | tous | ≥ 50 parts | ≥ 200 parts |
|---|---|---|---|---|
| J-1 | 0,08 | 14 paris (8 év.) +18,8 % | 8 paris +12,1 % | 3 paris −8,2 % |
| J-2 | 0,08 | 12 paris (8 év.) +28,9 % | 7 paris +49,8 % | 4 paris +39,6 % |
| J-3 | 0,08 | 9 paris (6 év.) +25,7 % | 5 paris +16,6 % | 2 paris −1,0 % |

Prix horaires (milieux) : +10 à +60 % ; vrais échanges : +7 à +29 % (tous seuils), le signe tient partout sauf à ≥ 200 parts.

## Verdict : **indice faible** → fantôme `indice_cotes` (expérience audacieuse)
- Pour : le modèle bat le prix à J-1/J-2/J-3 malgré un sous-jacent approché (Polymarket seul, biaisé de 0,5-1,5 point avant
  l'élection) ; gains aux vrais échanges à tous les seuils.
- Contre : une seule série (Sénat, 10 dates en 6 semaines, tirages très liés : une trajectoire), J-5 perdant au log-score,
  profondeur faible (≥ 200 parts : 2 à 5 paris), 27 cellules regardées.
- Fantôme : chance = mélange de deux lois normales (cœur calé sur l'écart interquartile des variations à 117 h, 20 % de queue à
  2,5 fois) depuis la valeur BRUTE de l'indice (lue à la source, plus de biais de plateforme) ; achat si écart ≥ 0,08 (rejeu).
  Seulement les tranches « on <date> » ; les barrières (« hit __ by December 31 », 4 valeurs horaires consécutives) et les
  « leader » ne sont pas jouées.

## Le 15/11 à 21 h UTC (aucune conviction)
- « Democratic 2028 presidential odds on November 20 » (indice brut 0,6745, 117 h) : loi empirique 66-68 % = 0,58-0,69 (marché
  0,605), 68-70 % = 0,21-0,33 (0,215), **64-66 % = 0,00-0,05 contre 0,14/0,15**. NON du 64-66 % : médiane de mes cinq
  estimations 0,959, rapprochée 0,907, borne basse 0,877 contre un vendeur à 0,86 : 1,7 point, sous le seuil de 5 → pas de conviction.
- Barrières « Democratic 2028 presidential odds hit __ by December 31 » (1 109 h) : 16 mois d'historique horaire (439 départs,
  ≈ 10 fenêtres indépendantes) : ↑ 70 % touché 4 heures de suite 24-26 % du temps contre 0,455 au marché ; ↓ 60 % jamais (0/439)
  contre 0,105 ; ↑ 75 % 5 % contre 0,027. Mais le régime a changé depuis septembre (0,59 → 0,685 en deux mois) : rapprochées,
  bornes basses sous les vendeurs (NON ↑ 70 % 0,55 contre 0,55 ; NON ↓ 60 % 0,907 contre 0,90) → rien.

## À refaire
- Juger le fantôme sur les prochaines dates (20/11 et suivantes) ; relire chaque règlement contre l'indice brut lu à la source
  (journal de la source dans la base).
- Les barrières (13 événements ouverts, ≈ 300 k$ échangés) : rejeu dès que « hit __ by December 31 » sera réglé.

## Barrières (17/11/2026, passage de 21 h) : **écartée**
Question : « <X> odds hit <b>% / dip to <b>% by <date>? » (4 valeurs horaires CONSÉCUTIVES de l'indice au-delà du seuil) : la chance
calculée sur les trajectoires passées du sous-jacent bat-elle le prix ?

- Données (`scripts/barrieres_releve.py`, `barrieres_jetons.py`, `barrieres_histo.py`, `barrieres_toutes.py`) : 21 événements (7
  réglés, 15 ouverts, ≈ 900 k$), 86 marchés. Le **jeton Polymarket du sous-jacent** se lit dans les échantillons publiés par l'indice
  (`details/<liste>__<option>.json` → `sample_evidence` → `evidence/….samples.json.gz`, champ `token_id`) ; `details` ne garde que
  168 heures d'indice. Sous-jacents horaires sur 400 jours, barrières sur 90 jours (`prices-history`, identité du labo).
- Méthode : à la création + 1 jour puis tous les 3 jours, départs tous les 24 h dans l'historique AVANT la décision, valeur de départ
  = prix du sous-jacent (réglées) ou valeur publiée de l'indice (ouvertes) ; variations absolues ou en logit ; règle des 4 heures ;
  barrière déjà franchie avant la décision : écartée.
- **Réglées** (7 événements : Chambre et Sénat républicains d'ici le 31/10, Talarico, deux du 01/11, Newsom et Vance déjà touchées ;
  19 marchés, 168 décisions très liées) : log-score modèle **−0,370** (logit) / −0,390 (absolu) contre **prix −0,296** ; touchées
  30, attendues aux prix 31,7, au modèle 13,4-19,7. Le marché est juste ; l'historique SOUS-estime les mouvements à l'approche de
  l'élection (Talarico « 75 % » : 0,006-0,017 au modèle, 0,125 au prix, touché).
- **Ouvertes** (56 décisions) : modèle − prix −0,018 en moyenne, mais le modèle change du tout au tout selon l'échelle (Le Pen « dip
  45 % » 0,055 en absolu, 0,415 en logit ; Ossoff « hit 30 % » 0,365 / 0,84) : aucun chiffre sur lequel miser.
- 2 réglages (absolu, logit) × 1 délai ; aucun achat simulé (le modèle perd déjà au log-score). Verdict : **écartée** ; la note du
  15/11 (« ↑ 70 % touché 24-26 % contre 0,455 au marché ») allait dans le même sens trompeur : sur les réglées, c'est le marché qui
  avait raison.
