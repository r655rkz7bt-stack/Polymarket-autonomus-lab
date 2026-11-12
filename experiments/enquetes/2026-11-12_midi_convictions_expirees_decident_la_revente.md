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

## Deuxième contrôle à la main, famille 2 (la mesure récompense-t-elle la chance ?)

Fantômes v2 avec des paris réglés (`charge_fantome.charger`, paiement par part) :

| Fantôme | Paris (événements) | Gagnés | Attendus aux prix | Attendus selon le modèle | Rendement |
|---|---|---|---|---|---|
| compteur_tweets | 18 (6) | 10 | 11,2 (z −0,7) | 12,4 (z −1,6) | −19 % ; sans les 3 meilleurs −57,6 € |
| compteur_truth | 4 (1) | 3 | 3,3 | 3,8 (z −2,0) | −14 % |
| seismes_marche | 3 (2) | 0 | 2,4 | — | −100 % (déjà élucidé le 11/11 : catalogue USGS en retard) |
| favori_politique_quasi_certain | 2 (1) | 2 | 2,0 | — | +1,7 % |

Les deux pertes de 15 à 25 € de `compteur_tweets` sont des NON à 0,83-0,93 que le modèle disait à 0,96-0,97 (Trump « 80-99 » du 07/11,
Musk « < 40 » du 09 au 11/11) : le modèle est plus sûr que le marché et que la réalité, sans que ce soit encore prouvé (6 événements).
Aucune stratégie v2 ne passe pour « gagnante par chance » : rien ne gagne. À revoir à 15 événements : si le modèle reste à z < −2
contre lui-même, élargir sa dispersion (rejeu d'abord).
