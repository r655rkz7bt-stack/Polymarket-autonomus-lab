# `decroissance_temps` rejouée sur le passé : le OUI de « d'ici <date> » ne fond pas moins que prévu (27/10/2026)

**Verdict : ÉCARTÉE** (les deux côtés). La stratégie `decroissance_temps` (fantôme depuis le 20/10) est **coupée**.

## Pourquoi cette piste
La stratégie est née le 20/10 dans les « vingt pistes » sans test sur le passé (essai à blanc en direct seulement, `vingt_pistes.md`). L'enquête automatique la signalait (`estimation_perimee` : NON estimé 0,928, payé 0,708 le 27/10 à 6 h).
Relecture des 76 achats du fantôme (journal signé) : son prix de « il y a 6 h » se retrouve par la formule `fair = 1 − (1 − p6)^(h/(h+6))` ; dans **24 achats sur 76 (561 € sur 1 140 € misés)** le OUI avait MONTÉ d'au moins 1,5 fois en 6 h (jusqu'à 10 fois : 0,2 % → 2,1 %).
La règle « acheter le NON quand le OUI n'a pas assez fondu » achète donc surtout des **sauts de prix**, que le filtre d'actualité (`max_spike`, pics de mentions) ne voit pas. Les estimations montent à 0,93-0,97 pour des NON payés 0,71-0,85 (écart net jusqu'à 0,21) et Kelly mise en proportion.
Ce n'est pas un carnet périmé : le prix payé est le vrai prix du carnet. C'est l'estimation qui est fausse : question de test.

## Données et méthode (`experiments/decroissance_passe/scripts/`)
- `releve.py` : Gamma `/events/keyset` (curseur, jamais `offset`), événements réglés dont la date de fin va du 01/02/2026 à demain, plus ceux réglés avant leur date de fin ; hors sport, questions contenant « by » ou « before », volume du marché ≥ 3 000 $ :
  **1 876 événements, 6 080 marchés**, tous leurs vrais échanges (data-api, 1 876 fichiers). Mois de fin répartis de février à octobre (460 à 900 marchés par mois).
- `analyse.py` : à chaque horizon T = fin − H (H = 30, 21, 14, 10, 7, 5, 3, 2, 1, 0,5 jour, de 12 h à 720 h comme la stratégie), prix du OUI = dernier échange dans les 3 h avant T (prix du « milieu » du carnet), `p6` = dernier échange dans les 24 h avant T − 6 h ;
  mêmes réglages que le fantôme (OUI 0,03-0,35, écart `prix − fair ≥ 0,01`) ; **un pari par marché** (premier horizon qui déclenche, du plus loin au plus proche, comme une position ouverte qui n'est pas rachetée) ;
  prix payé = premier échange réel de preneur sur le NON dans les 6 h APRÈS T (0,03-0,97), frais du marché (`feeSchedule`) ; rien d'après T pour décider ; marchés non réglés net (≥ 0,99) écartés ; T ≤ clôture − 1 h.
- `analyse2.py` : étalonnage, réglages voisins, côté OUI, moitiés, horizons ; sorties : `resultats.txt`. **Règlement** : prix de règlement de Gamma (`outcomePrices` ≥ 0,99), la seule source de règlement des marchés « d'ici » ; pas de seconde source.

## Résultats (`resultats.txt`)
- **Règle de la stratégie : 742 paris, 460 événements, 610 gagnés pour 624,7 attendus par les prix payés (z −1,5), −2,6 % par pari (t par événement −2,60)**, 6 mois sur 14 gagnants, première moitié des mois +1,1 %, seconde **−5,6 %**. `idea_test.verdict` : **écartée**.
- **Étalonnage** : estimation moyenne du NON 0,874 ; NON réellement gagné 0,822 ; prix moyen payé 0,842. L'estimation dépasse la réalité de 5 points : c'est elle qui fait grossir les mises (Kelly 0,25 sur des écarts jusqu'à 0,2).
- Par écart : `< 0,02` −4,6 % (227) ; `0,02-0,05` −0,9 % (296) ; `0,05-0,10` +0,6 % (151) ; `≥ 0,10` **−10,8 %** (68, 47 gagnés pour 52,4) : plus la stratégie se croit sûre, moins elle l'est.
- Par saut du OUI (prix / p6) : `< 1` −15,4 % (70), `1-1,25` −2,5 % (356), `1,25-2` −0,3 % (231), `≥ 2` −0,6 % (83). Pas de zone où ça gagne.
- **Pas de « prime d'espoir »** : le NON de tous les marchés « d'ici » à OUI 3-35 %, sans règle de gap : **−3,2 %** (1 255 paris, 1 030 gagnés pour 1 061, z −2,5, t par événement −3,7). OUI 0,15-0,35 : −5,2 % ; OUI 0,03-0,15 : −1,0 %.
- Côté **OUI** (« ça arrivera ») : OUI 0,15-0,35 **+5,5 %** (635 paris, z +1,05, t par événement +1,99) mais première moitié des mois **−12,0 %**, seconde +18,5 % ; sans ses 5 meilleurs événements +1,2 % ; par horizon −21 % à +26 % ; OUI 0,03-0,15 −4,3 %. **Bruit** : rien à jouer.
- Réglages regardés : 14 (6 pour le NON, 6 pour le OUI, p6 sur 6 h et tous horizons) + 12 découpages d'écart / de saut / d'horizon.

## Ce que ça change
- `decroissance_temps` : `enabled: false` (config, tests mis à jour). Ses 60 positions ouvertes se règlent ; elles n'étaient pas copiées par le principal.
- **Leçon** : une stratégie à modèle propre ne doit entrer dans l'arène qu'après un rejeu sur le passé, ne serait-ce que sur ses prix : les « vingt pistes » du 20/10 n'en avaient eu que pour une partie. Reste à rejouer (non testées sur le passé) : `marche_neuf`, `outsiders_surcotes`, `echelle_dates` (arbitrage : voir `courbe_de_risque.md`).
- Piste « les marchés d'échéance à OUI 15-35 % » : à refaire seulement avec plus de cas (la moitié récente seule : 362 paris, +18,5 %, mais la première moitié est négative).
