# Précipitations du mois : cumul observé + climatologie contre le prix (12/11/2026, piste n° 32 : NYC ÉCARTÉE aux vrais échanges, autres villes à faire)

Passage du chercheur de 1 h (12/11/2026), issu de l'inventaire des sources officielles (`sources_officielles.md`).
Marchés « Precipitation in <ville> in <mois>? » (NYC Central Park, Seattle, Londres Heathrow, Hong Kong, Séoul ; 6-7 tranches,
1-4 k$ de liquidité par événement ; 45 mois réglés de janvier à octobre 2026). Règle NYC : total du mois à Central Park,
« Monthly summarized data » de weather.gov (NOAA) ; valeur pile sur une borne → tranche du dessus.

## Modèle (`precipitations/scripts/`)

Chance d'une tranche = cumul observé du 1er au jour J − 1 (ACIS `data.rcc-acis.org`, sans clé, Central Park = sid 94728) + reste
du mois tiré des mêmes dates de 1951 à 2025 (75 ans). Aucune prévision météo (à ajouter : NWS à 7 jours).

## En direct, 12/11/2026 (NYC novembre, `nyc_novembre.py`)

Cumul du 1er au 10/11 : 0,91" (0,09 le 5, 0,82 le 6 ; le 11 pas encore publié). Modèle : < 2" 0,12 ; 2-3" 0,32 ; 3-3,5" 0,107 ;
3,5-4,25" 0,213 ; 4,25-5,75" 0,147 ; > 5,75" 0,093. Marché (milieu) : 0,15 / 0,21 / 0,195 / 0,225 / 0,215 / 0,125 (carnets
0,08-0,34 d'écart). Écart le plus net : « 2-3" » 0,32 contre 0,21 (vendeur 0,22) ; rapproché de moitié 0,265, borne basse ≈ 0,21 :
**sous le seuil d'une conviction**.

## Test sur le passé, NYC janvier → octobre 2026 (`test_nyc.py`)

Le 11 de chaque mois à 12 h UTC (cumul du 1er au 10 seulement), 10 mois, 60 tranches :
- log-score moyen : **modèle −0,370, marché −0,395** (le modèle fait un peu mieux) ;
- achats simulés quand chance − (prix + 0,02) ≥ 0,08 : **22 paris, 15 gagnés pour 12,5 attendus par les prix (16,3 par le
  modèle), +38 % par mise** ; mois perdants : janvier et février (−3 paris), gagnants : avril à octobre.

**Réserves (ne pas croire ce chiffre en l'état)** : (1) prix = milieu horaire du CLOB sur des carnets de 300-700 $ : le défaut
du 22/10 (« prix milieu sans échange réel ») a déjà transformé +9 à +31 % en −1 à +2 % ; (2) 10 mois seulement, paris d'un même
mois liés (un seul tirage par mois : t par mois à calculer) ; (3) un seul réglage (jour 11, seuil 0,08) ; (4) frais `weather_fees`
non comptés ; (5) une seule ville.

## Aux vrais échanges, même passage (`test_nyc_echanges.py 0.08 11`)

Premier échange réel du jeton dans les 72 h après le 11 à 12 h UTC, à un prix ≤ chance − 0,08 (Data API v2, 1 232 échanges en
octobre, quelques centaines les autres mois) :
- tous les échanges : **28 paris, 13 gagnés pour 9,8 attendus, +108 % par mise, t par mois 0,99 (8 mois)** ; mais le gain vient
  d'échanges de 1 à 5 parts à des prix extrêmes (juillet : NON « 5-6" » à 0,07 pour 9,9 parts, les deux côtés de 4 tranches
  achetés à 0,02-0,07 et 0,38-0,68) ;
- échanges d'au moins 10 parts : **13 paris, 6 gagnés, −23 % par mise**.

**Verdict NYC : écartée** (le gain s'efface dès qu'on demande 10 parts ; même leçon que le NON crypto à 0,10-0,20 du 27/10, règle
« profondeur à tester avant d'écrire exécutable »). Le log-score un peu meilleur que le marché (−0,370 contre −0,395) dit que la
climatologie lit bien le cumul, mais les carnets sont trop minces pour en vivre. Deux réglages regardés (prix milieu, échanges ;
seuil 0,08, jour 11).

## À faire (si on reprend)

1. Refaire aux **vrais échanges** (`data_api.lire` v2, `trades` par marché) : premier échange réel après le 11 à ≤ prix + 2
   centimes, profondeur (parts) ; frais du marché (`feeSchedule`).
2. Seattle (règle : « Seattle City Area », vérifier le sid ACIS), Londres (Met Office `heathrowdata.txt`, mensuel seulement :
   il faut un relevé quotidien, à chercher), Hong Kong (HKO, quotidien), Séoul (KMA).
3. Plusieurs jours de décision (5, 11, 18, 25) et seuils (0,05-0,15) ; t par mois ; `idea_test.verdict`.
4. Si l'indice tient : fantôme (source ACIS quotidienne, étiquette Gamma des précipitations).
