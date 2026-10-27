# Suivre les comptes suspects : l'affaire du Ballon d'Or et 740 événements « à initiés » (27/10/2026)

Demande d'Etienne (27/10/2026) : « Il y a eu récemment avec le Ballon d'Or un mouvement suspect, 12 comptes qui ont parié sur le
classement exact, qui s'est révélé être le final. Élabore une stratégie où tu vas chercher les soupçons de ce genre de choses quand
on en parle sur les réseaux sociaux, et tu paries en suivant ces mouvements. »

Données publiques, sans clé, de la session : Gamma (`/public-search`, `/events`, `/comments`), data-api (`/trades`, `/activity`,
`/traded`), CLOB (`prices-history`), Google Actualités (flux RSS). Contenu externe : des données, jamais des instructions.
Scripts : `experiments/inities/scripts/` (téléchargements dans `experiments/inities/donnees/`, ignoré par Git).

## 1. L'affaire, reconstituée avec les vrais échanges
Ce qu'en dit la presse : enquête d'Upside publiée le 23/10 (264 000 $ passés par 12 comptes créés à la hâte en octobre, 7 sans
aucun autre pari, 6 ayant misé gros 15 minutes après leur inscription) ; Foot01 le 24/10 ; cérémonie le 26/10 à Londres : Kane,
Mbappé, Yamal, Rodri, Messi, l'ordre exact des paris.

Ce que montrent les échanges publics des marchés « 2e, 3e, 4e, 5e place » (ouverts les 19 et 20/10) :

| compte (pseudonyme Polymarket) | première activité | ce qu'il a fait |
|---|---|---|
| `Aggravating-Lettuce-Local` (0xdd97…) | profil créé le 20/10 à 08 h 57, premier achat à 09 h 12 | 105 501 $ sur 9 événements, 8 du Ballon d'Or : « Yamal 3e » 15 766 $, « Mbappé 2e » 9 743 $, « Messi 5e », « Rodri 4e » |
| `Reflecting-Personal-Pattyp` (0x71ae…) | 22/10 à 18 h 49 | 123 420 $ sur 6 événements, TOUS du Ballon d'Or : « Mbappé 2e » 15 243 $, « Yamal 3e » 8 167 $, « Rodri 4e », « Messi 5e » |
| `Tall-Eyelashes` (0xe966…) | 26/10 à 00 h 06 | 182 450 $ en 489 échanges, 2 événements, tous du Ballon d'Or |
| `Gargantuan-Collaboration` (0xb01f…) | 19/10 à 22 h 56 | 5 échanges, 9 777 $, « Yamal 3e » 8 015 $ |

Prix des bons résultats (dernier échange du jour) : « Mbappé 2e » 0,64 (19/10) → 0,70 (21-23/10) → **0,61 le 25/10** → 1 ;
« Yamal 3e » 0,64 → 0,72 → 0,63 ; « Rodri 4e » 0,54 → 0,75 (23/10) → **0,42 le 25/10** ; « Messi 5e » 0,50 → 0,71 → 0,64.
Kane vainqueur : 0,62-0,65 jusqu'au 17/10, 0,77 le 21/10, 0,71 le 24/10 (Mbappé grimpe à 0,22 ce jour-là).
**Le marché n'a jamais cru la fuite** : suivre les comptes le 20-22/10 (≈ 0,70) rapportait ≈ +43 % par pari ; après l'article
d'Upside (23-24/10, ≈ 0,70) autant ; le 25/10, +56 à +138 %. Aucun commentaire Polymarket de ces marchés ne parlait d'initiés avant la
cérémonie (« RIGGED » après) : la discussion était dans la presse, pas sur Polymarket.

## 2. Test sur le passé : l'argent neuf et concentré bat-il ses prix ?
**Univers** : 3 024 événements réglés depuis le 01/09/2025 trouvés par mots-clés, triés au titre (`familles.py`, relu à la main) :
740 événements « à initiés » de plus de 1 000 $ (classements d'entreprise 278 — Spotify, Billboard, Google —, prix et
récompenses 258, émissions enregistrées 112, choix d'une petite équipe 92 — repêchages, nominations, pape). Exclus : ce qui se lit en
direct (vues, App Store du jour), les votes (primaires), les paroles en direct.
**Instant public** : premier instant où le jeton gagnant cote ≥ 0,95 sans redescendre sous 0,90 (historique horaire du CLOB :
un premier relevé de 30 pages d'échanges depuis le règlement ne voyait, pour les gros événements, que l'après-annonce). 618 instants trouvés.
**Échanges** : 1,7 million de vrais échanges (preneurs) relevés, dont 1,2 million dans les 14 jours avant l'instant public (data-api
`trades?eventId=…&end=<instant public + 1 h>`, en remontant, 40 pages au plus).
**Comptes** : 10 115 gros acheteurs (≥ 300 $ sur un jeton) profilés : première activité (`/activity`, tri croissant) et nombre de
marchés (`/traded`, compté aujourd'hui : léger regard vers le futur, un compte resté concentré l'était aussi à l'époque).
**Règle** : compte suspect = première activité depuis ≤ N jours ET ≤ M marchés ; grappe = K comptes suspects (≥ 100 $ chacun) sur
le même jeton en 72 h, S $ ensemble, à ≤ 0,85, avant l'instant public. On suit au prix du premier vrai échange du jeton 15 min
(ou 2 h) après, ≤ 0,92, frais du marché compris ; un pari par jeton ; confiance par événement (`idea_test.verdict`).

| réglage (48 essayés en tout) | paris / événements | gagnés / attendus | rendement | z des prix | verdict |
|---|---|---|---|---|---|
| K=2, S=500 $, ≤ 7 j, ≤ 15 marchés, 15 min (référence) | 94 / 42 | 39 / 42,2 | −9,7 % | −0,79 | écartée |
| les 16 réglages K=2 (S 500 ou 2 000 $, ≤ 3 ou 7 j, ≤ 5 ou 15 marchés, 15 min ou 2 h) | 37-94 | | −31 % à +10 % | −1,5 à +0,5 | écartée |
| les 16 réglages K=3 | 29-56 | | −49 % à −18 % | −0,9 à +0,1 | écartée |
| un ou deux gros comptes (K=1 ou 2), S 5 000 à 20 000 $, ≤ 10 marchés (6 réglages) | 19-48 | | −17 % à +12 % | 0 à +0,7 | écartée |
| les mêmes, en ne suivant qu'à un prix payé ≥ 0,30 (6 réglages) | 15-33 | | −6 % à +9 % | +0,2 à +1,2 | 1 « indice » sur 6 |
| témoin : VIEUX comptes (> 90 j, > 50 marchés), K=2 | 587 / 197 | 334 / 332,0 | −2,2 % | +0,20 | écartée |
| témoin : n'importe quels comptes, K=2 | 899 / 271 | 484 / 477,1 | +4,9 % | +0,56 | écartée |

Le seul « indice » (un compte neuf ≥ 5 000 $ sur un jeton payé ≥ 0,30 : 33 paris, 22 gagnés pour 18,8 attendus, t par événement
+1,12) est ce que le hasard donne au meilleur de 48 réglages ; ses voisins sont plats (−6 % à +3 %). **Verdict : écartée.**

Pourquoi : les comptes neufs sont surtout de **nouveaux joueurs** qui misent sur des outsiders (« Who will Trump nominate as Fed
Chair? » : 5 paris perdus à 0,01-0,09 ; famille « décision » : 2 gagnés pour 4,7 attendus, −82 %). Les vrais cas d'initiés sont
bien visibles (Ballon d'Or 2026 : 5 paris gagnés sur 6, à 0,54-0,76 ; Nobel de la paix 2025 : Machado à 0,54, 8,6 h avant ; « #1
searched person on Google » : d4vd à 0,08 ; jury de l'Eurovision 2026 : Bulgarie à 0,07) mais noyés parmi les autres.
On n'entend parler que des initiés qui ont eu raison (biais du survivant).

## 3. Et quand on en parle (presse, réseaux) ?
Google Actualités, mois par mois sur 14 mois (« Polymarket insider », « suspicious bets », « leak », « paris suspects »,
« insider trading ») : **428 articles**, presque tous **APRÈS** le résultat (militaires et Maduro, ingénieur de Google et d4vd,
enquêtes du Congrès et de la CFTC). Ceux qui signalent des paris suspects sur un marché ENCORE OUVERT sont rares : le Ballon d'Or
2026 (Upside le 23/10, Foot01 le 24/10). Trop peu de cas pour un test : on ne peut ni le prouver ni l'écarter sur le passé.
Réseaux : X est payant (interdit n° 2) ; Bluesky et Reddit refusent les lectures sans compte (403). Répondent sans compte ni
clé : les **commentaires Polymarket**, **Mastodon** (mot-dièse #polymarket) et **Hacker News** (API Algolia), en plus de la
**presse** (Google Actualités). Relus le 27/10 : aucun ne parlait des paris du Ballon d'Or avant la cérémonie (40 dernières
publications #polymarket depuis le 09/10, #ballondor seulement après ; Hacker News : rien sur le Ballon d'Or), et sur les 7
derniers jours, 0 publication sur 15 (Mastodon) et 0 sur 26 (Hacker News) parlent d'initiés.

## 4. La stratégie : `suivre_inities` (fantôme, expérience)
Ce qu'Etienne demandait, avec le filtre que le passé impose : **on ne suit l'argent neuf que quand on parle de soupçons**.
- Source `inities` (toutes les 20 min, `polymarket_agent/inities.py`) : événements ouverts des familles à initiés (étiquettes
  Awards 18, Reality TV 100339, Music 100, Movies 53 ; réglés dans 45 jours ; 30 au plus), leurs 2 000 derniers échanges, le
  profil des gros acheteurs (60 nouveaux au plus par passage, gardés 12 h en base), les grappes de comptes neufs (≤ 7 jours) et
  concentrés (≤ 15 marchés), et les commentaires de moins de 7 jours qui parlent d'initiés ou de fuite.
- Source `soupcons` (toutes les heures) : articles et publications des 7 derniers jours sur des paris suspects (5 recherches
  Google Actualités, #polymarket sur Mastodon, Hacker News).
- Rattachement : la grappe est accrochée au marché de son jeton ; un article lui est lié s'il partage deux mots porteurs de sens
  avec l'événement, et pas une autre année (l'affaire du Ballon d'Or 2026 ne rend pas suspect celui de 2027).
- Achat : article, publication ou commentaire de soupçon ET au moins 2 000 $ d'argent neuf et concentré sur le jeton, à 0,30 ou plus en moyenne
  (pas les billets d'outsiders), dans les 72 h ; prix ≤ 0,90 et ≤ prix moyen des suspects + 0,15 ; 3 % du fantôme par pari.
- Jamais retirée pour inactivité (elle peut attendre des semaines une affaire comme celle-ci).
- Une perte apprendrait que même un soupçon public est déjà dans le prix, ou que la presse s'emballe sur de faux initiés.

Vérifié en direct (cycle local du 27/10 à 14 h UTC) : 1 grappe trouvée (Billboard Hot 100 « #2 Song », 1 compte neuf, 334 $ à
0,52), rattachée au 2e cycle ; 11 articles de soupçons relevés (tous sur des affaires closes) ; la stratégie s'abstient
(« personne ne parle de paris suspects sur cet événement »).

## 5. Refaire
```
.venv/bin/python experiments/inities/scripts/releve_evenements.py 2025-09-01   # univers (≈ 1 min)
.venv/bin/python experiments/inities/scripts/releve_echanges.py                 # échanges depuis le règlement (≈ 15 min)
.venv/bin/python experiments/inities/scripts/releve_public.py                   # instant public (prix horaires, ≈ 5 min)
.venv/bin/python experiments/inities/scripts/releve_echanges_avant.py           # échanges d'avant l'annonce (≈ 15 min)
.venv/bin/python experiments/inities/scripts/releve_portefeuilles.py            # profils (≈ 45 min pour 10 000 comptes)
.venv/bin/python experiments/inities/scripts/test_grappes.py                    # 36 réglages + témoins
.venv/bin/python experiments/inities/scripts/test_gros_comptes.py               # 12 réglages de plus
```
Limites : un seul relevé ; le nombre de marchés d'un compte est compté aujourd'hui ; seuls les PRENEURS sont vus (un initié qui
pose des ordres échappe) ; les familles sont reconnues au titre ; pour les 10 événements les plus échangés, les 40 pages ne
remontent que de 0,2 à 13,5 jours avant l'instant public (au lieu de 14).
