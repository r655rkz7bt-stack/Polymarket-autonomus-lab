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
