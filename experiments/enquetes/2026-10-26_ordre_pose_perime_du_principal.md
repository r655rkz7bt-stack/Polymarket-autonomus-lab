# 26/10/2026 (nuit) — un ordre posé du principal survit au changement de prix du fantôme

**Alerte** : contrôle `copie_fidele`, « 1 achat du principal sans jumeau » : 2026-10-25 22:35, `nf_sport_patiente_6_24h`,
« Team Yandex », 5,43 parts à 0,83 (4,5 €).

## Ce qui s'est passé (base sauvegardée, table `pending_orders`)
- 22:27:43 le fantôme `nf_sport_patiente_6_24h` pose un achat à 0,83 ; le principal copie (22:27:44, même prix).
- 22:32:27 le fantôme remet son prix à jour : 0,82 (puis 0,81 à 22:37), ordre précédent `REMPLACE`.
  **La copie du principal n'est pas reposée** (plus de place dans la part de la stratégie / plafond : la source
  place son ordre, le principal écarte le sien) et **l'ancien ordre du principal, à 0,83, reste ouvert**.
- 22:35:57 le marché passe sous 0,83 : l'ancien ordre du principal est servi. Le fantôme, à 0,82, ne l'est pas.
  Le principal a payé un prix que sa source n'acceptait plus.

## Chiffres
- Taux de copie des ordres de `nf_sport_patiente_6_24h` par le principal : 12/12 à 12 h UTC le 25/10, 10/10, 10/11,
  6/12 à 15 h, 17/22, 19/29, 8/12, puis **2/14 à 22 h et 0/24 à 23 h** : la copie s'éteint dans la journée alors que
  le fantôme re-pose toutes les 5 minutes.
- Sur les 42 ordres posés du principal exécutés depuis le 19/10, **2 sont périmés** (prix principal > prix du
  fantôme au moment du fait) : `contrer_crypto_patiente` le 23/10 (0,36 €, déjà noté) et celui-ci (4,5 €).
  Un euro de pertes possibles par ordre : montant faible, mais le principal est censé jouer la stratégie qu'il copie.
- Reste hors de portée des journaux : la raison exacte du refus de la copie à 22:32 (les décisions de cette
  heure sont déjà élaguées de la sauvegarde). Le correctif ne dépend pas de la raison.

## Cause (code)
`main._place_resting` remplace l'ordre ouvert d'un portefeuille (`persistence.add_pending_order`) **seulement
quand le nouvel ordre est posé**. Une copie écartée par la mise (`Weighted._scale`, `_cap_main`), le contrôleur ou le
plafond d'ordres ne remplaçait rien : l'ancien ordre continuait jusqu'à ses 6 h.

## Correctif
`_place_resting(..., source_orders=...)` : pour une stratégie copiée, chaque ordre que le fantôme a posé ce cycle et
dont la copie n'est pas posée **annule** l'ordre ouvert du principal sur ce jeton (`Database.cancel_open_orders`, statut
`ANNULE`). Si le fantôme ne repose rien, rien n'est annulé (même comportement que le fantôme lui-même).
Test : `tests/test_cycle.py::test_principal_drops_its_resting_copy_when_the_ghost_replaces_it_and_the_copy_is_not_placed`
(échoue sans le correctif : le principal gardait son ordre à 0,89 et l'achetait au cycle suivant).

## Contrôle automatique
Le contrôle `copie_fidele` l'avait trouvé (c'est lui qui a donné l'alerte) : rien à ajouter.
