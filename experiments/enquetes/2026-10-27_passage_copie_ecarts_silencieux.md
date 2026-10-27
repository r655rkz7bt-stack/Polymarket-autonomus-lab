# 27/10/2026 (passage chercheur, 1 h UTC) : les écarts silencieux de la copie du principal (famille 6 : ce qui ne se voit pas)

## Obligations de la feuille de mission
- `copie_fidele` (« Team Yandex », 25/10 22 h 35, 5,43 parts à 0,83) : le défaut est celui de la fiche `2026-10-26_ordre_pose_perime_du_principal.md`
  (ordre posé périmé, déjà corrigé le 26/10 à 01 h 55) ; l'achat date d'avant le correctif. Rien de nouveau.
- `copie_absente` (`moins_de_cartes`, 0 jeton copié sur 50) : le fantôme n'a **pas acheté depuis le correctif** (dernier pari le 26/10 à 16 h 04,
  le plancher de copie date de 16 h 34). Pas de défaut : la fenêtre est celle de ses paris (1 à 6 h avant un match de CS2/LoL/Dota/Valorant,
  14 à 21 paris par jour ; sur ses 71 paris, aucun entre 17 h et minuit UTC : ses créneaux sont 0 h-16 h). Le plancher marche : 16 copies depuis 16 h 34 (`nf_court_prix_haut` 6 sur 6 à
  5 parts exactes, `compteur_tweets` 4, `nf_sport_patiente_prix_850_875` 4, `nf_sport_925_950` 2), 74 € engagés.

## Contrôle à la main : famille 4 (le filtre ne filtre pas)
Prix payés contre `price_min`/`price_max` de chaque fantôme (toutes les stratégies à plage de prix, tous les achats) : 3 stratégies sortent de leur
plage, toutes par le mécanisme déjà connu des ordres posés (`mots_prononces_patiente` 14 achats sur 45 à 0,27-0,29 pour un plancher de 0,30 ;
`contrer_crypto_patiente` 4 sur 212 à 0,039-0,048 ; `suivre_politique` 3 sur 123 à 0,90-0,91). Aucun défaut de filtre.

## Défaut trouvé : le principal écarte des paris sans le dire (famille 6)
`favori_politique` a **14,3 % du capital principal** (107 €). Le 26/10 entre 12 h 13 et 12 h 22 son fantôme a fait 7 achats (30 à 111 parts) ;
le principal n'en a copié **aucun** et `refus_principal` (refus du principal sur 48 h) ne contient **aucune ligne** pour cette stratégie. Les décisions
du principal ne l'expliquent donc pas : la proposition n'est pas arrivée jusqu'au contrôle de sécurité. Chemins qui jetaient une proposition sans rien écrire :
`Weighted._scale` (budget de la part épuisé, budget trop juste pour le minimum, mise arrondie à 0), `_cap_main` (plafond de famille : un `log.info` seulement),
`_execute` (marché déjà acheté dans ce cycle par une autre stratégie). Ces écarts n'apparaissaient ni dans la base ni dans les journaux publiés :
on ne peut pas dire aujourd'hui lequel a frappé `favori_politique` (le code de l'époque n'avait ni le plafond de 5 % ni le plancher : la copie à l'échelle donnait
9,2 et 10,3 parts pour deux paris, au-dessus du minimum).

## Correctif
`Weighted.drops` (raison → nombre) rempli par `_scale`, `_cap_main` et `_execute` ; publié dans les abstentions du principal (dernier cycle) et gardé 48 h dans la base
(`ecartes_principal`, `main._remember_drops`) ; `dashboard.py` les ajoute à `refus_principal` du tableau de bord (donc de `published/data.json`). Aucune règle de copie ne change.
Test : `tests/test_principal.py::test_silent_drops_of_the_copy_are_counted_and_remembered_for_48_hours`.

## Reste ouvert
- Au prochain achat de `favori_politique` (la fenêtre de la politique en `zero_fees` est ouverte depuis le 24/10), lire `data.json` → `refus_principal.favori_politique` : une raison
  y sera, ou le principal aura copié (plancher et plafond de 5 % sont en place depuis le 26/10).
- Les obligations `copie_fidele` / `copie_absente` du passage sont des constats qui s'éteignent d'eux-mêmes ; je ne touche pas à leurs seuils.
