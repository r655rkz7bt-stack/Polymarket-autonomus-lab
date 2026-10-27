# 27/10/2026 (midi) : deux faux positifs de la copie du principal (famille 4, « le principal refait-il les paris des fantômes ? »)

Point de départ : l'enquête automatique du jour donne 8 « copies à 100 % sur une exécution partielle » (`copie_fidele`) et `nf_moyen` « 1 jeton copié sur 36 » (`copie_absente`).
Aucune n'est une obligation, mais elles reviendraient à chaque passage. Vérifié à la main (`scripts/copie_depuis_plancher_27_10.py`, journaux signés du 27/10).

## 1. Les 8 « copies à 100 % » sont le plancher de copie, pas une copie disproportionnée
Les 8 achats du principal (`moins_de_cartes` ×5, `compteur_tweets`, `nf_sport_patiente_prix_850_875`, `nf_court_prix_haut`) font 1,25 à 4,75 parts, soit 0,5 à 4,2 € chacun (au total moins de 15 €).
`settings.yaml` → `principal.plancher_copie` achète au moins 5 parts quand la copie à l'échelle tombe sous le minimum du marché ; quand le fantôme n'est servi que pour 2,5 parts (carnet mince),
le principal l'est pareil (même carnet). Le contrôle comparait seulement « parts du principal ≥ 95 % des parts du fantôme ».
**Correctif** : `enquete.PLANCHER_COPIE_PARTS = 5` : une copie de 5 parts ou moins n'est plus signalée (au-dessus, l'égalité reste signalée). Test : `test_partial_fill_at_the_copy_floor_is_not_a_full_copy`.

## 2. `nf_moyen` : « 1 sur 36 » comptait des paris d'avant sa part
`nf_moyen` (part 8,7 % aujourd'hui) a son premier achat copié à 05 h 17 le 27/10 ; ses 12 paris d'avant (26/10 16 h 22 → 27/10 04 h 32) n'ont sans doute pas été copiés faute de part (la date d'entrée de la part n'est pas dans les journaux publiés ; le premier achat copié date de ce matin). Depuis ce premier achat : 1 jeton du fantôme, 1 copié. **Correctif** : quand le principal a déjà copié la stratégie, les jetons du fantôme ne sont comptés
qu'à partir de sa première copie (moins 10 minutes) ; une stratégie jamais copiée reste « grave », une stratégie copiée une seule fois puis plus jamais reste « à regarder ». Test :
`test_a_share_that_just_started_is_judged_from_its_first_copy`.

## Contrôle d'ensemble (depuis la mise en service du plancher, 26/10 15 h 40 UTC)
Jetons des fantômes qui ont une part, copiés par le principal dans les 6 h : `nf_sport_patiente_prix_850_875` 8/9, `compteur_tweets` 6/8, `nf_court_prix_haut` 17/22, `nf_moyen` 1/13 (13 d'avant son entrée),
`favori_politique` 0/0 (le fantôme n'a pas acheté). Les refus restants (`refus_principal`, 48 h) sont en partie d'avant le plancher (`moins_de_cartes` 18, `nf_sport_patiente_6_24h` 27 « taille inférieure au minimum du marché (5) ») :
à relire dans 24 h, la fenêtre sera alors entièrement postérieure au plancher.
