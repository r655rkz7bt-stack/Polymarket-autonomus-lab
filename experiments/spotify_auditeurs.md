# Piste n° 28 : auditeurs mensuels Spotify (« Top / #2 Spotify Artist in <mois> »)

Passage du chercheur du 11/11/2026, 21 h UTC. Idée « radicalement différente » demandée par la feuille de mission (aucun palier
depuis 27 jours) : nouvelle source (kworb.net / profil Spotify), nouveau type de marché (classements de musique mensuels).

## Les marchés

- « Top Spotify Artist in November? » (événement 1274342, 18 k$) et « #2 Spotify Artist in November? » (1274351, 65 k$),
  frais `culture_fees` (5 % × p(1−p), preneur seulement), un marché OUI/NON par artiste.
- Règle (mot à mot) : « the listed artist with the greatest number of monthly listeners according to Spotify on November 30,
  2026, 12:00 PM ET » ; profils principaux seulement ; égalité exacte → ordre alphabétique ; Spotify en panne → dernière donnée.
  Échéance Gamma 30/11 17 h UTC.
- Mois réglés retrouvés (`public-search`, `events_status=closed`) : n° 1 de février à octobre (Bruno Mars chaque fois, 0,96 à J-19),
  n° 2 de mars, avril, mai, juin, octobre.
- Classements de l'année (Wrapped : « Top Spotify Artist / Song 2026 », « #2 / #3 … », « Top US … », 50 k$ à 1,8 M$) : réglés
  début décembre par Spotify ; non étudiés à fond (pas d'historique 2026 complet gratuit : kworb ne garde que 36 semaines et
  31 jours par titre ; les comptes « Wrapped » ne sont pas ceux des classements).

## La source

- `open.spotify.com/artist/<id>` affiche le nombre exact (« 116,993,416 monthly ») ; `kworb.net/spotify/listeners.html`
  (robots : `Allow: /`) le recopie pour ~2 500 artistes avec la variation du jour, identique au profil le 11/11 à 21 h UTC.
  Une valeur par jour. **Aucun historique gratuit** (web.archive.org bloqué depuis la routine).

## Ce que disent les mois réglés (n° 2)

| mois | favori à J-19 (prix) | gagnant |
|---|---|---|
| mars | The Weeknd 0,855 | The Weeknd |
| avril | The Weeknd 0,955 | « Other » (artiste non listé) |
| mai | Drake 0,415 / Rihanna 0,415 | « Other » |
| juin | Bad Bunny 0,44 | « Other » |
| octobre | The Weeknd 0,70 (0,78-0,81 du 10 au 12/10) | Rihanna (0,185 à J-19) |

Le favori à J-19 gagne 1 fois sur 5 (attendu par les prix ≈ 3,4). Cinq mois : un INDICE, pas une preuve. En octobre, le prix a
basculé 6 fois entre The Weeknd et Rihanna (0,20 ↔ 0,80) : le meneur du jour change souvent, et le marché le paie comme sûr.

## Le 11/11 (21 h UTC)

Bruno Mars 124 624 825 (−321 978), **The Weeknd 116 993 416 (−176 227)**, **Rihanna 116 778 078 (−149 631)**, Justin Bieber
111 015 895 (+51 612). Écart des places 2-3 : 215 338 (0,18 %), Rihanna reprend ≈ 26 600 par jour, 19 jours restants.
Marché n° 2 : The Weeknd 0,80/0,81, Rihanna 0,16/0,19 ; il était à 0,91 la veille, 0,18 le 02/11.

Modèle (`spotify_auditeurs.p_rang`, 15 premiers artistes, dérive × `retrait`, bruit `vol` × auditeurs × √jours) :

| vol \ retrait | 0 | 0,5 | 1 |
|---|---|---|---|
| 0,0015 | Rihanna 0,41 | 0,50 | 0,59 |
| 0,003 | 0,45 | 0,49 | 0,49 |
| 0,005 | 0,45 | 0,43 | 0,37 (Bieber 0,14) |

Bruno Mars n° 1 : 0,92-1,00 (marché 0,94/0,993 : rien).

## Décisions

- **Conviction** `spotify-n2-novembre-rihanna` (OUI 0,29, borne 0,25, vendeur 0,19 + frais 0,008) : médiane de cinq estimations
  0,40 rapprochée de moitié du prix. Ce que je ne sais pas : pourquoi le prix est passé de 0,18 à 0,91 du 02 au 10/11 (sans
  historique, je ne vois pas la tendance de The Weeknd sur la semaine).
- **Fantôme `auditeurs_spotify`** (expérience audacieuse, demi-Kelly sur chance − 0,10) et source `spotify` (toutes les 3 h,
  journal `spotify:histo` : une ligne par nouvelle valeur). Même tirage que la conviction ce mois-ci.
- Étiquette `spotify` (102851) au scanner, horizon 40 jours (les classements de l'année restent dehors).

## À faire

- Dans 7-10 jours : étalonner `vol` et `retrait` sur `spotify:histo` (écart-type des variations à 1, 3, 7 jours des 40 premiers).
- 30/11 : règlement ; décembre : 6e mois réglé pour le tableau ci-dessus.
- Classements de l'année : relever chaque semaine le classement hebdomadaire mondial de kworb (36 semaines gardées) pour
  « #2 Spotify Song 2026 » / « #2 US Spotify Song » (Babydoll 0,73, Man I Need 0,84) avant le Wrapped (début décembre).

## Classements de l'année (premier regard, 11/11 21 h 15)

Pages de titre de kworb (`spotify/track/<id>.html`, tableau hebdomadaire, colonnes Global et US), semaines communes du 05/03 au
05/11 : Babydoll (Dominic Fike) 976 M d'écoutes mondiales, End of Beginning (Djo) 722 M, Man I Need 724 M, Earrings 700 M,
Choosin' Texas 644 M ; aux États-Unis Choosin' Texas 373 M, Earrings 248 M, Babydoll 225 M, Man I Need 203 M. Le marché met
pourtant Djo n° 1 mondial à 0,76 et Babydoll à 0,16. **Les tableaux de kworb sont incomplets** : Djo a 35 jours à la 1re place
du classement quotidien et 2,95 milliards d'écoutes au classement, mais son tableau hebdomadaire saute de 2024/08 à 2026/03 ;
ses semaines de janvier-février 2026 manquent sans doute. Rien à conclure sans les semaines manquantes : **pas de conviction**.
Il faudrait les classements hebdomadaires complets (charts.spotify.com demande un compte).

## Cycle local (11/11 21 h 10)

Premier cycle : la conviction achète 46,39 parts à 0,19. Second cycle : `spotify` rattache 7 marchés ; `auditeurs_spotify` propose
un achat, refusé « carnet périmé (1 584 s > 120 s) » par le contrôleur (même cas que `proposals/2026-11-11_carnet_calme_juge_perime.md` :
carnet calme jugé périmé). Le fantôme achètera quand quelqu'un touchera au carnet.

## Piste n° 29 : classements hebdomadaires = somme des jours (11/11, 21 h 20)

« #1 / #2 Spotify song (in the US) this week? (<vendredi>) » (123 événements réglés depuis le printemps, 2-10 k$ chacun, carnets
de quelques dizaines de parts). Règle : semaine du vendredi au jeudi, playlist du vendredi. **Vérifié** : l'hebdomadaire US de
kworb = somme exacte des 7 jours quotidiens (Housewife et Choosin' Texas, semaines du 22/10, 29/10, 05/11 : 6 sur 6). Le mardi
soir, 4 jours sur 7 sont publics.

- Semaine du 13/11 (US n° 1) : vendredi-lundi Choosin' Texas 4 254 474, Housewife 4 223 820 (+30 654 pour Texas). Mardi-jeudi
  tirés des 2-3 semaines précédentes (Housewife en déclin : 2,72-2,94 × le lundi ; Texas : 3,01-3,38 × le lundi) : Texas
  7,19-7,54 M, Housewife 7,08-7,31 M, Texas gagne dans 4 combinaisons sur 6 (≈ 0,65-0,70). Marché : Texas 0,06/0,44 (2,6 parts
  à 0,44, puis 0,54), derniers prix 0,25-0,35 ; Housewife 0,47/0,92. Après rapprochement de moitié vers le prix (≈ 0,30) :
  0,485, borne 0,435 sous le vendeur 0,44 + frais : **pas de conviction** ; carnet trop mince de toute façon.
- Semaines réglées testables (kworb ne garde que 31 jours) : `experiments/spotify_auditeurs/hebdo_somme_des_jours.py`, meneur de
  la somme ven.-lun. au mardi 22 h UTC, 9 événements rattachés : 6 meneurs gagnent, déjà payés 0,96-0,99 ; 1 piège (US,
  semaine du 06/11 : « Thriller » en tête des 4 jours d'Halloween, battu par Housewife, prix 0,0025 : le marché avait raison) ;
  2 « #2 US » sans gagnant rattaché. **Écartée en l'état** : quand la somme partielle est nette, le marché le sait ; l'information
  ne sert que dans les duels serrés, aux carnets vides.
