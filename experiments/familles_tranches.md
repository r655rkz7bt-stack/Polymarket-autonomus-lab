# Familles de marchés à tranches répétitifs (24/10/2026) : la favorite et le « même gagnant que la dernière fois »

Né du contrôle du box-office (`box_office.md`) : la favorite sous-cotée est-elle un trait général des marchés à une seule gagnante ? Données : `experiments/familles_tranches/releves/` (13 Mo, versionnées ; `scripts/releve.py`, `releve2.py`),
événements réglés, vrais échanges (`data-api` trades), mêmes règles que le box-office (dernier achat réel dans les 2-3 h, frais 5 %, favorite sûre si les tranches sans prix pèsent moins qu'elle).

| Famille | Événements utilisables | Favorite (OUI), selon l'horizon | Verdict |
|---|---|---|---|
| Netflix, meilleure série de la semaine (US et monde, n°1 et n°2) | 174 | −7 % (96 h) à +1 % (48 h), z des prix −1,2 à +0,2 ; gagnants précédents : 8/38, 6/37, 11/46, 7/37 semaines identiques, prix moyen 0,18-0,33 pour une fréquence 0,23-0,34 | écartée (calibré) |
| Vues (bandes-annonces, MrBeast) | 241 | −21 % à +3 % (z −1,8 à +0,9) | écartée |
| Rotten Tomatoes (note du film) | 51 | −1 % à +4 % (n = 21-23) | écartée |
| Billboard (n°1 du Hot 100, du Billboard 200) | 75 | −9 % à 0 % (n = 16-17) | écartée |
| Spotify, chanson n°1 des États-Unis | 38 | +0,3 % à 6 h | écartée |
| App Store (n°1 gratuite, n°2 gratuite, n°1 payante, jour par jour) | 182 | favorite OUI −13 % à +5 % ; **gagnant de la semaine précédente** coté 0,74-0,80 : 48 gagnés pour 59,3 attendus à 24 h (z des prix −4,1) ; son NON (coût 0,16-0,34) : +30 % à +224 % mais sans les 3 meilleurs −48 % à +62 %, 4 horizons sur 5 instables | **écartée** (loterie : gros rendements portés par 3-10 coups sur 39-65 ; le NON de la favorite n'est positif que pour la série « n°1 gratuite », négatif pour « n°2 » et « payante » : 45 cases regardées, z attendu du meilleur ≈ 2,3) |

Lecture : aucun biais général « favorite sous-cotée ». Le box-office reste un indice faible à part, plafonné par ce contrôle. Pistes laissées : App Store en direct (le classement du jour est lisible sur `rss.marketingtools.apple.com`, chantier n°8) ;
rien n'est lancé tant qu'une loi simple (le n°1 d'aujourd'hui reste n°1 demain, de combien ?) n'est pas calibrée sur ses propres données et non sur le simple prix.
Scripts : `scripts/favori.py <famille>`, `scripts/statu_quo.py`, `scripts/appstore.py`.
