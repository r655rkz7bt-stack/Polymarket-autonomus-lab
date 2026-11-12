# Enquête du 12/11/2026 (passage de 11 h) : une conviction expirée décide encore de la revente

Familles : 1 (le principal joue-t-il ce que l'arène mesure ? jour 12 → 12 mod 6 + 1 = 1) et 3 (la donnée n'est pas celle qu'on croit).

## Obligations et constats de l'enquête automatique

- Aucune « Enquête obligatoire ». Feuille de mission : « aucun palier depuis 27,9 jours : idée radicalement différente » (traitée en
  partie B/C : piste n° 39, El Niño, prévisionniste officiel de la source du règlement).
- `muettes` (`suivre_inities`) et `positions_oubliees` (Nouvelle-Zélande, 5 positions, résultats officiels le 27/11, Gamma non clos,
  vérifié : 2118145, 2116493, 2117123 `closed: false`) : déjà élucidés aux passages précédents.
- `reglements_50_50` : 5 marchés de la v1 (octobre), rien de neuf.

## Constat mené au bout : la revente du Danube (famille 3)

Le journal de `convictions_claude` montre une VENTE le 12/11 à 09 h 32 : 3,36 parts du OUI « Danube avant le 15/11 » (acheté 0,292)
à 0,807, raison « le marché paie 0,81, Claude n'en donne que 0,46 ». La conviction `danube-budapest-avant-15-11` (p = 0,455) avait
**expiré le 11/11** ; elle continue de décider de la revente (`ConvictionsClaude.exits` : vendre quand l'acheteur paie plus que p),
alors que la prévision OVF du 12/11 08 h 42 change la chance (≈ 0,6 ; voir `config/convictions.yaml`, `-v2`). Même chose pour le Rhin
(NON à 0,52 écrit la veille ; ≈ 0,40 avec la prévision WSV/BfG du jour).

**Chiffrage** : 1 vente, 3,36 parts. Ici elle était bonne (0,807 > 0,6 : +1,7 € par rapport à garder au prix juste) ; mais une
probabilité d'hier peut aussi revendre trop tôt ou garder trop longtemps. 2 positions concernées (63,67 + 39,94 parts, ≈ 33 € misés).
Le saut de l'estimation du fantôme (972 → 1 013 → 972 €) à 09 h 32 vient du même carnet mince (un acheteur à 0,807 apparu puis disparu :
le Danube est maintenant 0,16 / 0,90).

**Cause** : `convictions.py` garde la dernière conviction du fichier pour chaque marché, expirée ou non : c'est voulu (une conviction
expirée ne doit pas tout revendre d'un coup), mais rien ne signale au chercheur qu'elle décide sur une information périmée.

**Correctif** : nouvelles convictions du jour pour le Rhin et le Danube (PR n° 232) ; contrôle **`convictions_perimees`** dans
`enquete.py` (positions de `convictions_claude` dont la conviction gouvernante a expiré depuis plus de 6 h, ou qui n'en ont plus),
branché sur `scripts/enquete.py` et la feuille de mission ; test `test_convictions_perimees_cas_du_danube_12_11` (cas réel). Rejoué
sur le journal publié avec l'ancien fichier : il cite les deux positions ; avec le fichier du jour : rien.

## Contrôle à la main, famille 1

Principal : rien acheté depuis le 07/11 (BUY : 12 le 05/11, 13 le 06/11, 5 le 07/11, puis 0) ; règlements des positions v1 jusqu'au
12/11 (2) ; 582,87 € disponibles, 650,60 € estimés (positions v1 encore ouvertes). Champion « aucun », aucune v2 à 12 opérations closes
(meilleure : `compteur_tweets`, 18 closes mais −4,1 %) : conforme aux seuils de `promotion.yaml`. Rien à corriger.
