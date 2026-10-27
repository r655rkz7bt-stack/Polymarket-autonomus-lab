# Échelles « <jeton> FDV above $X one day after launch ? » : test sur le passé (28/10/2026, passage du 27/10 au soir)

Piste n° 23 de `vingt_cinq_pistes.md` (`premarche_jetons`), jamais testée. **Verdict : INDICE FORT MAIS NON EXÉCUTABLE EN DIRECT** (le gain n'existe que dans les 6 à 24 dernières heures avant le règlement, dont
l'heure ne s'observe pas par les prix) ; rien dans l'arène. À reprendre avec une source de date de lancement (annonce du TGE) ou de FDV en direct (CoinGecko).

## Données (`experiments/fdv_lancement/scripts/`)
77 événements « FDV above ___ one day after launch » réglés d'octobre 2025 à octobre 2026 (relevé `contrer_crypto_passe/scripts/releve_marches.py`, fin Gamma ≥ 30/07/2026 : ces marchés ont une fin factice en 2027-2028, donc
tous sont dans la fenêtre), 537 marchés (OUI/NON, règlement net 0/1, volume ≥ 2 000 $), 346 037 vrais échanges (data-api). Instant de règlement = `closedTime` (Gamma). Un pari par marché, côté acheté au premier échange réel
qui l'achète dans les 12 h après l'instant T, frais du marché (`feeSchedule`), prix du OUI à T = dernier échange avant T (≤ 24 h). `analyse.py`, `niveau_evenement.py`, `temps_reglement.py`, `declencheur.py`.

## Résultats
1. **Calibration loin du règlement (D−3 à D−30)** : rien (`resultats_calibration.txt` : 70 cellules prix × côté × délai, rendements de −103 % à +327 % sur 3 à 60 paris, tous « écartée » sauf des cellules de 10 paris).
2. **Dans les dernières heures, le côté « presque sûr » (payé 0,70-0,97) bat son prix, des deux côtés** (`resultats_heures.txt`, `resultats_niveau_evenement.txt`) : OUI sous le niveau final et NON au-dessus.
   | avant le règlement | paris (OUI + NON, 0,70-0,97) | gagnés / attendus | rendement | jetons avec une perte / attendu |
   |---|---|---|---|---|
   | H−24 | 157 | 154 / 143,0 | +7,6 % | 3 / 10,9 |
   | **H−18** | 130 | **130 / 119,3** | **+9,3 %** | **0 / 8,7** (P = 0,0001) |
   | H−12 | 103 | 102 / 93,5 | +9,6 % | 1 / 8,5 |
   | H−6 | 61 | 60 / 55,3 | +8,7 % | 1 / 5,4 |
   Les paris d'une même échelle sont emboîtés (les OUI sous le niveau final gagnent ou perdent ensemble) : `niveau_evenement.py` prend le jeton comme unité et le pari le moins sûr de chaque côté comme seul risque
   (borne prudente) ; les deux moitiés (avant / après le 01/04/2026) donnent le même sens (H−18 : 0 jeton perdant sur 27, puis 0 sur 32, attendu 4,2 et 4,5). Bande 0,90-0,97 seule : +4 à +5 % (0 perte pour 2 à 3,5 attendues).
3. **Pourquoi ce n'est pas exécutable** : le résultat devient public en médiane **4,5 h avant `closedTime`** (quartiles 3,1 et 9,7 h ; 36 % des jetons ≥ 6 h, 19 % ≥ 12 h, 6 % ≥ 24 h), donc H−18 est ~14 h avant la
   mesure du FDV, quand le jeton cote depuis peu. Un déclencheur CAUSAL cherché dans les prix (`declencheur.py`) échoue : activité ≥ N échanges en 3 h (N = 20 à 150) ou saut d'un seuil ≥ 0,15-0,60 en 3 h déclenchent
   en médiane 39 à 495 h avant le règlement (les ladders s'agitent des semaines avant le lancement) et rendent −6,5 à +1,8 % (tous « écartée », 4 réglages × 3 côtés). Seule une source du lancement (annonce du TGE, première cotation,
   FDV en direct) donnerait l'heure.
4. Ce que cela dit du marché : près de la mesure, les seuils loin du niveau final restent cotés 0,90-0,95 alors qu'ils gagnent à 100 % (la prime est le coût de l'immobilisation et la peur d'un krach du jeton, jamais réalisé ici
   en 6 à 24 h sur 59 jetons) : même mécanisme que `apres_echeance` / `favori quasi certain`, mais ici l'écart tient sur toute la période.

## Suite
- **Chantier** (piste n° 14 de PISTES.md) : trouver l'heure de lancement sans regarder le règlement : CoinGecko `coins/list/new` / `search` (clé `COINGECKO_API_KEY` si disponible), annonces « TGE » (flux RSS des projets), ou DEX (DexScreener sans clé).
  Tester d'abord l'idée en rétrospective avec les dates de lancement (CoinGecko `genesis_date`), puis en direct.
- Mesure de profondeur à faire avant tout fantôme : parts achetables à ≤ prix + 2 centimes dans l'heure (`contrer_crypto_passe/scripts/profondeur_non_10_20.py` comme modèle) ; volume total moyen par jeton 0,8 M$ (médiane ≈ 0,5 M$).
- Rien n'est ajouté à l'arène : un fantôme sans déclencheur achèterait 0,70-0,97 des semaines avant (z −0,5 à +1,5 par pari, aucun réglage positif).
