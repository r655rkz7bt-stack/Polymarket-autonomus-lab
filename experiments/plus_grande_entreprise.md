# Plus grande entreprise du monde à la fin du mois (piste n° 49, 13/11/2026, passage de 6 h)

**Question** : les marchés « Largest / 2nd / 3rd Largest Company end of <mois> » (Gamma, 1-3 M$ de volume par mois, frais
`finance_prices_fees` 0,04·p(1−p)) se règlent sur la capitalisation « à la clôture » du dernier jour. Un modèle qui part des
capitalisations du jour et tire les mouvements futurs dans les vraies fenêtres passées bat-il le prix ?

Déclencheur : le 13/11 à 06 h UTC, Apple 5,157 T$, NVIDIA 4,013 T$ (écart de 25 %), Microsoft 3,884, Alphabet 3,661
(companiesmarketcap.com) ; le marché paie Apple n° 1 **0,934** alors que l'historique de 10 ans donne une hausse relative de
NVIDIA de 25 % en 11 séances 0,5 % du temps (0,5 % aussi dans les fenêtres de résultats de NVIDIA).

## Données (scripts dans `plus_grande_entreprise/`)

- `releve_capis.py` : capitalisations hebdomadaires de companiesmarketcap (pages `/<société>/marketcap/`, `robots.txt` relu :
  autorisées ; tableau `data = [...]` embarqué) et cours quotidiens Yahoo (recherche seulement). Nombre d'actions implicite =
  capitalisation de la semaine / cours, lu AVANT chaque décision.
- `releve_marches.py` : 66 événements trouvés par `public-search`, 318 marchés réglés de sociétés cotées (janvier 2024 → octobre
  2026), prix horaires du CLOB sur les 22 derniers jours.
- `modele.py` : capitalisation du jour × rendements joints de toutes les sociétés sur les fenêtres de H séances des 3 années
  précédentes (corrélations et queues réelles), **sans dérive** (sans cette correction, la hausse de NVIDIA en 2023-2024 se
  prolongeait : NVIDIA n° 2 à 0,72 au lieu de 0,65).
- **Contrôle du règlement** : le classement des clôtures du dernier jour redonne le résultat officiel pour **314 marchés sur 318** ;
  les 4 écarts sont la fin mai 2026 (Apple 4,583 T$, Alphabet 4,565 : 0,4 % d'écart, la « source consensuelle » a mis Alphabet
  devant).

## Résultats (`test_passe.py`, `analyse.py`, `favoris_ecart.py`)

Log-score moyen, modèle contre prix horaire (≈ 290 marchés par délai) :

| délai | 14 j | 10 j | 7 j | 5 j | 3 j | 2 j | 1 j |
|---|---|---|---|---|---|---|---|
| modèle | −0,108 | −0,095 | −0,109 | −0,095 | −0,094 | −0,101 | −0,140 |
| marché | −0,104 | −0,099 | −0,111 | −0,104 | −0,083 | −0,075 | −0,022 |

Le modèle fait jeu égal loin de la fin et perd nettement près de la fin (le marché voit la séance en cours et les courses à 1 %
près). Achats simulés (vendeur = prix horaire + 0,01, frais compris, un pari par mois, rang, société et côté ; 12 réglages
essayés : seuils 0,02 / 0,04 / 0,06 / 0,10 × trois groupes de délais) : de +5,7 % à +32 % selon le réglage, mais
`idea_test.verdict` sur l'ensemble (seuil 0,04, tous délais) : **74 paris, 19 mois, −18 % par pari, confiance par mois −1,15,
z des prix +0,69, 7 mois gagnants sur 19, seconde moitié −33 %** → **écartée**. Les billets sous 0,10 : 0 sur 17.

Cas d'aujourd'hui (le favori que le modèle donne presque sûr) : côtés à modèle ≥ 0,97 payés 0,80-0,96 : 8 sur 8 (+7,5 %, 7,4
attendus) ; mais modèle ≥ 0,95 payés 0,70-0,97 : **23 gagnés pour 25,2 attendus, −8,9 %** (27 paris), ≥ 0,90 : 32 pour 33,8
(−5,6 %). Le « 8 sur 8 » est une tranche choisie après coup : le modèle est trop sûr de lui, le prix ne l'est pas assez peu.

## Verdict

**Écartée** : aucun avantage du modèle de capitalisations contre le prix, ni en général ni sur les favoris à gros écart. Pas de
conviction sur « Apple n° 1 fin novembre » (0,988 au modèle contre 0,934 : sur le passé, ce genre d'écart ne rapportait rien).
Leçon : une hypothèse « le marché sous-estime un favori à 25 % d'écart » se teste sur les mois réglés avant d'y croire ; le
marché paie peut-être un risque que les clôtures ne voient pas (source « consensus », nombre d'actions, introductions géantes
comme SpaceX à 1,9 T$).
