# Dette fédérale américaine : « Peak US National Debt before 2027? » (piste n° 44, 12/11/2026, passage de 21 h)

Suite de l'inventaire des sources officielles (piste n° 32 : « dette publique quotidienne », dernière source de la liste non essayée).

## Marché
Événement 73226, 4 seuils ; ouverts : 41 000 Md$ (marché 665519, carnet OUI 0,46 / 0,86, milieu 0,66, 884 $ de liquidité,
688 $ échangés en un an, derniers échanges de 5 parts) et 42 000 Md$ (0,013 / 0,041). Règle : OUI si la dette atteint le seuil
« at any point » d'ici le 31/12/2026 23 h 59 (heure de l'Est), source `treasurydirect.gov/NP_WS/debt/current` (champ
`totalDebt`). Frais : `economics_fees` (taux 0,05, preneur seulement).

## Données (sans clé)
`www.treasurydirect.gov/NP_WS/debt/search?startdate=2015-01-01&enddate=…&format=json` : 2 977 jours ouvrés,
`totalDebt` = `publicDebt` (dette du public) + `governmentHoldings` (intragouvernementale). `api.fiscaldata.treasury.gov`
répond 200 mais un corps non JSON depuis la routine. Scripts : `dette_us/analyse.py`, `dette_us/trimestre.py`
(données dans `dette_us/donnees/`, ignoré par Git).

## Résultats
1. **Rythme passé** (`analyse.py`) : il faut +440 Md$ du 09/11 au 31/12 (52 jours) ; le maximum de la période est le 31/12
   10 années sur 11. Gain réel divisé par le rythme connu au 09/11 : sur 60 jours, 2 années sur 11 au-dessus du ratio
   demandé (0,99), sur 365 jours 3 sur 10 (ratio demandé 1,26). Les années de plafond (2015-2017, 2019, 2021-2023, 2025)
   brouillent tout : fréquence de base ≈ 0,25.
2. **Estimation officielle d'emprunt** (`trimestre.py`, communiqué du Trésor du 02/11/2026) : 618 Md$ d'emprunt de marché
   (« privately-held net marketable ») pour octobre-décembre, encaisse de 850 Md$ fin décembre. La hausse trimestrielle de
   `publicDebt` colle au chiffre réalisé depuis la fin de la réduction du bilan de la Fed : T3 2026 +744 pour 742 annoncés
   réalisés ; T4 2025 +569 pour 569. Au 09/11 : +339 → 33 043 attendu le 31/12.
3. **Intragouvernementale** : 7 796 au 09/11 (+49 depuis le 30/09, contre +146 à +210 les années récentes) ; hausse du 09/11
   au 31/12 : +13 à +162 Md$ (médiane ≈ 42, hors 2021 : +223 au retour des fonds après le plafond). Crédit d'intérêts du
   31/12 : +11 à +74 en un jour.
4. **Total attendu** ≈ 40 840 + 42 ≈ 40 880 (± 70 en combinant l'erreur d'estimation et l'intragouvernementale) : il manque
   ≈ 120 Md$, chance du OUI ≈ 0,05-0,15 (queues épaisses comprises).
5. Témoin indépendant : le plafond légal est à 41 100 Md$ ; le Bipartisan Policy Center le voit atteint « late winter to
   mid-summer 2027 ».

## Verdict
Pas de test sur plusieurs événements possible (un seul marché vivant, les seuils de 2025 étaient de la même famille mais
sous plafond). **Conviction** `dette-us-41000-avant-2027` : NON, 0,70 (borne basse 0,62), mise maximale 4 %, contre un
vendeur à 0,54 (116 parts). Exception écrite à la méthode du skill `prevoir-un-marche` : le rapprochement se fait vers 0,5
et non vers le milieu d'un carnet sans échanges (0,66 = milieu de 0,46 / 0,86, échanges de 5 parts) ; sinon la borne basse
serait 0,57 et l'avantage 0,02.

**Défaut trouvé en chemin** : la conviction n'aurait jamais été jouée, le scanner ne lisait pas ce marché (631e sur 639 de
l'étiquette economy triée par volume du jour) → `conviction_markets` (fiche
`enquetes/2026-11-12_nuit_conviction_hors_scan.md`).

## À relire
- Chaque passage : dette du jour (`debt/current`) ; si elle dépasse 40 800 avant le 01/12, abandonner la conviction.
- Début février 2027 : le Trésor publie l'emprunt réalisé d'octobre-décembre ; comparer à 618.
- Les marchés de 2027 (« Peak US National Debt in 2027 ») quand ils seront créés : même méthode avec les estimations
  trimestrielles et le plafond de 41 100 (mesures extraordinaires : la dette soumise au plafond ne peut plus monter).
