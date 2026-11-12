# Film le plus rentable de 2026 : le marché de l'année contre celui du premier week-end (12/11/2026, piste n° 33)

Passage du chercheur de 6 h (12/11/2026). Idée neuve demandée par la feuille de mission (« radicalement différente ») :
**cohérence entre marchés liés** et **lecture de la règle** sur un marché très liquide.

## Le marché et sa règle

« Highest grossing movie in 2026? » (événement Gamma 79831, 2,8 M$ de liquidité, 1,6 M$ échangés sur le seul jeton Doomsday) :
« domestic **calendar** gross in 2026 — dates outside of 2026 will not count », colonne « Gross » de la page de l'année de Box
Office Mojo (`?grossesOption=calendarGrosses`), une fois publiées les données du 31/12.

- Meneur : **Spider-Man: Brand New Day**, 959,0 M$ au 08/11 (sorti le 31/07 ; encore 17-28 k$ par jour sur 190 écrans) ;
  premier week-end 360,1 M$ (record), 715,8 M$ au 14e jour (été, sans fêtes : × 1,99).
- Prétendant : **Avengers: Doomsday**, sortie le **vendredi 18/12/2026** (même jour que Dune: Part Three). Seuls ses 14 premiers
  jours (18 → 31/12, Noël le 8e jour) comptent dans l'année.
- Prix du 12/11 vers 06 h UTC : Spider-Man 0,915 (0,91/0,92), **Doomsday 0,0765 (0,076/0,077)**.

## Ce que disent les marchés liés (même heure)

- « "Avengers: Doomsday" Opening Weekend Box Office » (1285841, 68 k$) : < 260 M$ 0,009 ; 260-300 0,0165 ; 300-340 0,07 ;
  340-360 0,145 ; 360-400 0,265 ; **400 M$+ 0,475**. Loi log-normale ajustée : **médiane 399 M$, écart log 0,135**.
- « Which movie has biggest opening weekend in 2026? » (123 k$) : Doomsday **0,715** (= P(week-end > 360,1 M$)) ; cohérent avec
  le marché des tranches (0,755 normalisé).
- Presse (Google Actualités, 24/10-11/11) : préventes « en train de rattraper Spider-Man: Brand New Day », « 125 M$ de préventes »
  le 31/10, « peut-il faire 400 M$ ? » ; Dune 3 vise un record de franchise le même jour.

## Multiplicateur de Noël : recette au 14e jour / premier week-end

Grosses sorties d'un vendredi de décembre (recettes quotidiennes domestiques relues sur Box Office Mojo ; voir la réserve
plus bas) :

| film | sortie | J10 | J14 | au 31/12 |
|---|---|---|---|---|
| Star Wars VII | ven. 18/12/2015 (**même calendrier**) | 2,18 | **2,63** | 2,63 |
| Spider-Man: No Way Home | ven. 17/12/2021 (Omicron) | 1,81 | 2,14 | 2,20 (J15) |
| Rogue One | ven. 16/12/2016 | 1,84 | 2,42 | 2,63 (J16) |
| The Last Jedi | ven. 15/12/2017 | 1,67 | 2,11 | 2,35 (J17) |
| Rise of Skywalker | ven. 20/12/2019 | 2,04 | 2,35 | 2,20 (J12) |
| Avatar: The Way of Water | ven. 16/12/2022 | 1,95 | 2,67 | 2,99 |
| Avatar: Fire and Ash | ven. 19/12/2025 | 2,43 | 2,99 | 2,81 (J13) |

Grosses sorties de printemps-été, pour comparer : Endgame 1,85, Infinity War 1,89, Deadpool & Wolverine 2,08, The Avengers 1,94
au 14e jour. Les films de fans (Star Wars, Spider-Man) en décembre : **2,11 à 2,63, médiane ≈ 2,35** ; les plus gros records
d'ouverture sont les plus concentrés sur leurs premiers jours (NWH 2,14).

Il faut à Doomsday ≈ 960 M$ au 31/12, donc un premier week-end ≥ 960 / multiplicateur : 365 M$ (× 2,63), 408 M$ (× 2,35),
447 M$ (× 2,15).

## Chance que Doomsday soit n° 1 (week-end log-normal × multiplicateur log-normal d'écart 0,06)

| loi du week-end | × 2,15 | × 2,25 | × 2,35 | × 2,45 | × 2,60 |
|---|---|---|---|---|---|
| prix du marché (médiane 399, 0,135) | 0,22 | 0,33 | 0,44 | 0,55 | 0,70 |
| médiane 375 (presse plus prudente) | 0,12 | 0,19 | 0,28 | 0,39 | 0,54 |
| médiane 360, écart 0,15 (= record de Spider-Man) | 0,09 | 0,15 | 0,22 | 0,30 | 0,44 |

Même le cas le plus défavorable (0,09) dépasse le prix de l'année (0,077). Le marché de l'année se conduit comme si le
multiplicateur était celui d'un film d'été (≈ 1,9), ou comme si le marché du premier week-end se trompait.

## Conviction : étudiée, sous le seuil

Cinq estimations (méthode `prevoir-un-marche`) : fréquence de base des multiplicateurs avec le prix du week-end 0,44 ; données
prudentes (week-end 375) 0,28 ; avocat du NON (week-end 360, × 2,15 comme NWH, salles IMAX prises par Dune 3) 0,09 ; avocat du
OUI (calendrier de Star Wars VII) 0,60 ; vue d'ensemble (375, × 2,25) 0,19. **Médiane 0,28**, rapprochée du prix → **0,18**,
borne basse honnête ≈ 0,12 pour un vendeur à 0,077 : **0,7 point sous le seuil de 5 points**. Pas de conviction aujourd'hui.

Ce que le prix sait peut-être : (1) le marché du premier week-end, plus petit (68 k$), surestime ; (2) un record d'ouverture
encore plus concentré que NWH ; (3) rien (le marché de l'année, détenu par de gros porteurs de Spider-Man, n'a pas suivi la
hausse du week-end : Doomsday 0,04-0,05 en octobre, 0,112 le 09/11, 0,077 le 12/11, pendant que « biggest opening » passait de
0,37 à 0,715).

## Fantôme `box_office_annee` (expérience audacieuse)

`box_office.py` lit le marché des tranches du premier week-end (Gamma, aucune autre source), ajuste la loi, multiplie par 2,35
(écart log 0,08) et compare au meneur (959,5 M$, constante de `settings.yaml`) ; après le règlement de la tranche (20-21/12),
loi uniforme dans la tranche : chance bien plus serrée. Pas de billets sous 0,10 ; borne basse = chance − 0,15 ; demi-Kelly ;
arrêt le 22/12 (les recettes réelles des jours de semaine comptent alors plus que le modèle). Un seul tirage, réglé début
janvier : aucun test sur le passé possible (le seul cas comparable, Star Wars VII contre Jurassic World en 2015, n'avait pas de
marché).

## Le moment qui compte : dimanche 20/12

Le dimanche 20/12 au matin (heure de Paris), les studios annoncent l'estimation du premier week-end (Deadline, Variety :
Google Actualités). À ce moment, la loi du week-end tient en ± 3 % et seul le multiplicateur reste incertain :
week-end 420 M$ → il faut × 2,28 (chance ≈ 0,6-0,65) ; 380 M$ → × 2,52 (≈ 0,2) ; 350 M$ → × 2,74 (≈ 0,05). Si le marché de
l'année tarde, c'est là qu'une conviction peut passer le seuil : **passage du 20/12 vers 11 h 54**, lire l'estimation, recalculer,
écrire une conviction si l'écart tient. Le 21/12 au soir, BOM publie le chiffre réel (même lecture, à la main).

## Réserve sur la source (règle n° 7)

Box Office Mojo (IMDb) **interdit la collecte automatisée** de ses pages (`robots.txt` : « Use of any device, tool, or process
designed to data mine or scrape the content using automated means is prohibited without prior written permission »). Je ne l'ai
lu qu'APRÈS avoir relevé par script les recettes quotidiennes de 15 films (≈ 17 pages). Le script et le relevé ont été
supprimés, ils ne sont pas dans le dépôt ; seuls les rapports ci-dessus (faits publics, aussi dans la presse et Wikipédia) sont
gardés. **Aucune source du cycle ne lit Box Office Mojo** ; the-numbers.com répond 403 aux robots. Règle ajoutée aux astuces de
la routine : lire `robots.txt` et les conditions AVANT le premier appel d'un nouveau site.
