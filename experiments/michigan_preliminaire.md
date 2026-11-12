# Sentiment des consommateurs du Michigan : le préliminaire contre les tranches du final (12/11/2026, piste n° 35 : INDICE)

Passage du chercheur de 6 h (12/11/2026), issu de l'inventaire des sources officielles (`sources_officielles.md` :
« data.sca.isr.umich.edu … chiffre préliminaire publié avant le final »). Avantage de RÈGLE et d'INFORMATION.

## Règle

« University of Michigan Consumer Sentiment - <mois> » (7 tranches de 3 points, « below 40.0 » … « at least 55.0 ») : « the bracket
containing the **final** University of Michigan Index of Consumer Sentiment … preliminary results will not be considered », valeur
au dixième. Le préliminaire de la MÊME source sort deux semaines avant (novembre 2026 : préliminaire le vendredi 06/11, final le
vendredi 20/11 à 10 h, heure de l'Est). Frais : barème `economics_fees`.

## Données (`michigan/scripts/`, relevés dans `michigan/releves/`)

- Finales : fichier officiel `www.sca.isr.umich.edu/files/tbmics.csv` (1952 → octobre 2026).
- Préliminaires : titres de presse (Google Actualités, `preliminaires.py`) relus à la main ; 2026 : juin 48,9 → final 49,5 (+0,6),
  juillet 54,4 → 55,2 (+0,8), septembre 47,8 → 48,1 (+0,3), octobre 46,3 → 48,0 (+1,7) ; mai (48,2 → 44,8 ?) et août non
  retrouvés de façon sûre ; les mois d'avant 2026 ne sortent pas de la recherche datée. De mémoire (non relu), 2024-2025 : révisions
  de −3,1 (février 2025) à +2,9 (mars 2024), une sur quatre au-delà de 2 points en valeur absolue → SD ≈ 1,8.
- Page d'accueil `www.sca.isr.umich.edu` (sans clé, pas de `robots.txt`) : « Preliminary Results for November 2026 … Index of
  Consumer Sentiment 51.0 » (même chiffre que la presse) ; elle devient « Final Results » au final.
- Polymarket : 6 événements (juin → novembre 2026, `marches.py`, prix horaires par tranches de 13 jours) et leurs vrais échanges
  (`echanges.py`, Data API v2 par événement : 474 à 5 631 échanges).

## Ce que montrent les prix horaires (à ne pas croire seuls)

Après le préliminaire, les prix horaires des tranches sont absurdes (septembre : somme des 7 tranches ≈ 2,0 ; juillet, préliminaire
54,4 : « 40-42,9 » à 0,36, « ≥ 55 » à 0,13). Ce sont des milieux de carnets vides (défaut du 22/10) : seul le test aux échanges compte.

## Test aux vrais échanges (`test.py SD SEUIL PARTS`)

Décision à partir du jour du préliminaire 16 h UTC (publication à 10 h, heure de l'Est) ; chance d'une tranche =
P(préliminaire + révision ∈ tranche), révision ~ N(0 ; SD) ; premier échange réel de chaque jeton (OUI ou NON) d'au moins PARTS
parts, à un prix ≤ chance − SEUIL − frais (0,05·p·(1−p)), avant le final ; issue = règlement Gamma. Mois testables : juin,
juillet, septembre, octobre (préliminaire sûr).

| réglage (SD, seuil, parts) | paris | gagnés | attendus (prix) | attendus (modèle) | rendement par mise |
|---|---|---|---|---|---|
| 1,8 ; 0,05 ; 10 | 24 | 16 | 11,79 | 15,55 | +34,3 % |
| 1,4 ; 0,05 ; 10 | 24 | 17 | 12,75 | 16,55 | +32,0 % |
| 2,5 ; 0,05 ; 10 | 29 | 17 | 12,86 | 16,90 | +30,7 % |
| 1,8 ; 0,10 ; 10 | 19 | 12 | 7,83 | 11,47 | +51,4 % |
| 1,8 ; 0,05 ; 50 | 19 | 14 | 10,36 | 13,48 | +33,6 % |

Un seul pari par tranche (le premier, OUI ou NON) avec le réglage de départ : **18 paris, 12 gagnés pour 8,91 attendus (z des prix
+2,13), +33,5 % par mise ; juin +27 %, juillet +33 %, septembre +36 %, octobre +58 % (t par mois 5,7 sur 4 mois)**. Les gains
viennent surtout des NON de tranches que le préliminaire exclut, achetés 0,84-0,93 (6 sur 6), et de quelques OUI de la tranche du
préliminaire achetés trop bas. Cinq réglages, tous positifs.

**Verdict : indice** (4 mois seulement, paris d'un même mois liés par une seule révision, préliminaires d'avant 2026 introuvables).
Assez pour un fantôme audacieux et une conviction quand l'écart est énorme ; pas pour le capital principal.

## Novembre 2026 (en direct, 12/11 vers 06 h 30 UTC)

Préliminaire 51,0 (page officielle et presse). Chance (SD 1,8) : 46-48,9 0,124 ; **49-51,9 0,575** ; 52-54,9 0,286 ; **55+ 0,014**.
Marché : 0,115 / 0,4995 / 0,246 / **0,1155** (acheteur du OUI « 55+ » 0,103 pour 92 parts → NON vendu 0,897).
- **Conviction `michigan-novembre-pas-55`** : NON « 55.0+ », 0,98, borne basse 0,96 (le préliminaire de la source du règlement
  tranche presque : pas de rapprochement vers le prix ; la plus forte hausse de révision connue est +2,9).
- « 49-51,9 » OUI à 0,50 pour 0,575 : sous le seuil (rapproché du prix 0,54).

## Fantôme `michigan_preliminaire` (expérience audacieuse)

Source `michigan` (page d'accueil, toutes les heures) ; étiquette `umich` (105176) au scanner ; chance bornée à 0,01-0,99 ; borne
basse = chance − 0,02 ; Kelly entier ; au plus 3 tranches par mois. Se tait dès que la page passe à « Final Results ».

## À faire

1. Relire les révisions 2024-2025 à une source (FRED/ALFRED ne répond pas depuis la routine) pour étalonner SD.
2. Relire le 20/11 : final de novembre, gains de la conviction et du fantôme.
3. Même mécanisme ailleurs ? (préliminaire puis final : PIB américain avance → seconde estimation, PMI flash → final, inflation
   flash de la zone euro → finale) : chercher les marchés Polymarket réglés sur le chiffre FINAL.
