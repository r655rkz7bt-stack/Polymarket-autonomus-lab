# Classements Spotify de l'année (Wrapped) recalculés sur kworb (piste n° 53, 13/11/2026, passage de 11 h)

**Marchés** : « Top / #2 Spotify Song 2026 », « Top / #2 US Spotify Song 2026 », « Top / #2 / #3 Spotify Artist 2026 », « Top US
Spotify Artist 2026 », « Top Spotify Album 2026 » (50 k$ à 1,8 M$), frais `culture_fees` (5 % × p(1−p), preneur), réglés sur la
liste publiée par Spotify (Wrapped, début décembre ; écoutes du 1er janvier à la mi-novembre environ).

## Données (`spotify_annee/releve.py`, `classe.py`, `estime_2026.py`, `prix_2025.py` ; robots.txt de kworb : « Allow: / »)

- Page kworb de chaque titre : historique HEBDOMADAIRE (rang et écoutes par pays) ; pour le mondial, seulement les **36 dernières
  semaines** (depuis le 05/03/2026) plus quelques semaines isolées ; pour un titre qui a toujours été classé dans un pays, toutes
  ses semaines (les États-Unis sont souvent complets). 651 titres relevés (classement du jour + titres restés 3 semaines dans le
  top 10 mondial).
- `country/us_weekly_totals.html` (et `global_weekly_totals.html`) : total de TOUTES les semaines classées d'un titre et nombre de
  semaines : une contrainte exacte sur les semaines manquantes.
- Marchés réglés : 2025 tous trouvés (`prix_2025.py`) ; à J-7 le marché avait le gagnant à 0,96-0,99 partout sauf « #3 artiste »
  (Drake 0,94 le 26/11/2025, The Weeknd gagnant) ; 2024 : seul « Top artiste » (Taylor Swift 0,97).

## Mondial : le prix sait (Djo n° 1, Babydoll n° 2)

Mars-novembre : « Babydoll » (Dominic Fike) 977 M, « End of Beginning » (Djo) 722 M, « back to friends » (sombr) 775 M, « Man I
Need » 725 M, « SWIM » (BTS, sorti fin mars) 988 M. Babydoll a toutes ses semaines (janvier ≈ 0, février 62 M → ≈ 1 064 M). Djo
n'a aucune semaine connue avant mars, mais il était **n° 1 mondial début janvier** (finale de Stranger Things, presse du 03-08/01) :
avec ≈ 45-50 M par semaine en janvier-février, ≈ 1 100-1 150 M. Le marché (Djo n° 1 à 0,78, Babydoll n° 2 à 0,815) est cohérent
avec ces ordres de grandeur ; mon incertitude sur janvier est plus grande que la sienne : rien à prendre.

## États-Unis, place n° 2 : course serrée, marché sûr de lui

| titre | écoutes US 2026 (semaines finies au 05/11) | rythme des 7 derniers jours |
|---|---|---|
| Choosin' Texas (Ella Langley, n° 1 à 0,973) | 447 M (toutes les semaines connues) | 7,2 M / semaine |
| Earrings (Malcolm Todd) | **268,7 M exact** (44 semaines, toutes en 2026 : total kworb = somme) | ≈ 5,0 M (0,72 M / jour) |
| Man I Need (Olivia Dean) | 218,8 M connus + X | ≈ 4,3 M (0,62 M / jour) |
| Babydoll (Dominic Fike) | 251,4 M (toutes connues) | 3,3 M |
| Mr. Brightside (The Killers) | 245,1 M (toutes connues) | 5,0 M |

« Man I Need » : total US de ses 63 semaines classées 406,1 M ; 42 semaines connues (245,4 M dont 26,7 M en 2025) → 160,7 M sur
21 semaines inconnues : 14 de 2025 (septembre-décembre) et **7 de 2026 (X : semaines finies les 01/01, 08/01, 15/01, 22/01,
05/02, 12/02, 19/02)**. Voisines connues : 8,91 (27/11/2025), 6,87 (29/01), 8,09 (26/02), 8,11 (05/03). Jusqu'à la mi-novembre,
« Earrings » reprend ≈ 1 M ; « Man I Need » reste n° 2 si X > ≈ 51 M. Estimations de X : interpolation avec creux de Noël 51,4 ;
contrainte des 160,7 M (sinon décembre 2025 à 10,4 M par semaine) 55-57 ; effet des Grammys du 01/02 (Olivia Dean) 58-62 ; janvier
faible 50 → P(« Man I Need » n° 2) : 0,65 / 0,80 / 0,85 / 0,45, et 0,55 si Spotify compte jusqu'à fin novembre : **médiane 0,65**
contre **0,8445** au marché (« Earrings » 0,161). Rapprochée de moitié : 0,75 ; le NON se vend 0,156 pour une chance ≈ 0,25, borne
≈ 0,20, moins 0,007 de frais : **4 points, sous le seuil de 5 : pas de conviction**. Le doute porte sur 7 semaines de janvier-
février que les nouvelles données ne lèveront pas ; seul un relevé des classements hebdomadaires US de janvier (charts.spotify.com
demande un compte) trancherait.

**Affinage (même passage)** : forme décembre-mars de 3 titres dont toutes les semaines US sont connues, rapportée aux 4 points connus
de « Man I Need » : janvier ≈ 1,0 fois le niveau de référence, février ≈ 1,12 (creux de Noël 0,8) → **X ≈ 57,5 M (54,7-59,9)** ; et
la contrainte des 160,7 M donne alors décembre 2025 trop haut, ou X encore plus grand (≈ 60-67 M) si décembre a eu son creux. Avance
de « Man I Need » à la mi-novembre ≈ +4 à +16 M : **P ≈ 0,8, le marché (0,845) a raison** ; la médiane de 0,65 venait d'un janvier
supposé trop faible. Leçon : avant de croire un écart, reconstruire les semaines manquantes avec la forme de titres complets.

## Verdict : le prix sait (mondial et US) ; rien dans l'arène

Méthode réutilisable : total des semaines classées (`*_weekly_totals.html`) − semaines connues = contrainte sur les semaines
manquantes. À relire le 03/12 (Wrapped) : « Man I Need » contre « Earrings » (≈ 0,8 après affinage, marché 0,845).
