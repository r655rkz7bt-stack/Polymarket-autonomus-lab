# 26/10/2026 (soir) : paris d'une même échelle comptés comme indépendants, et deux contrôles qui criaient à tort (familles 2, 5 et 6)

Obligations de la feuille de mission (15 h 48 UTC) : `copie_fidele` (« Team Yandex » 22 h 35 le 25/10 : déjà corrigé cette nuit, aucun nouveau cas), `champion_sans_avantage`
(`nf_court_soir`, `nf_sport_patiente`) et cinq constats « chance » (3 paris font 84-300 % du gain). Les cinq « chance » sont le mécanisme déjà connu (petits gains sur de grosses mises à prix haut) :
`nf_court_football_soir` 38 paris, gagnés 35 pour 34,6 attendus par les prix, +30 € pour 4 689 € misés ; `nf_sport_patiente_6_24h` 34 paris, 30 gagnés pour 29,4 attendus, +90 € pour 3 102 € misés
(`scripts/` : lecture jeton par jeton avec `charge_fantome.charger`). Pas de défaut de code.

## 1. `compteur_tweets` : z +2,56 par pari, +1,0 par événement (famille 2 : la mesure récompense la chance)
Le constat « z = +2,56 sur 28 paris, mais choisie parmi 90 stratégies » (`selection_multiple`) traitait chaque jeton comme un tirage indépendant. Or les 28 paris de `compteur_tweets` sont des
**tranches d'échelles** : 9 événements seulement (« Elon Musk 16-23/10 » porte à lui seul 8 jetons : exactement une tranche gagne, les autres NON gagnent ensemble).

Relu à la main : les 28 règlements du journal redonnent ceux de Gamma (28 sur 28, `scripts/tweets_reglements_26_10.py`) ; les marchés sont bien « Will Elon Musk post X-Y tweets from … » (ou Trump / CZ), bonnes dates.

| stratégie (part du capital principal) | paris | t par pari | événements | t par événement |
|---|---|---|---|---|
| `compteur_tweets` (14,4 %) | 28 | +1,78 | **9** | **+1,03** |
| `moins_de_cartes` (14,6 %) | 62 | +2,08 | 62 | +2,08 |
| `nf_sport_patiente_prix_850_875` (22,2 %) | 54 | +2,18 | 52 | +2,58 |
| `nf_sport_925_950` (11,8 %) | 71 | +1,75 | 61 | +1,67 |
| `compteur_tweets_non` (fantôme) | 21 | +0,71 | 8 | +1,05 |

(`scripts/z_par_evenement_26_10.py`.) Les stratégies à tranches (tweets, mentions, séismes, détroits) paraissent plus sûres qu'elles ne sont tant qu'on compte les jambes une à une.
`compteur_tweets` reste validée sur le passé (177-189 périodes, +12 à +16 %) : sa part du principal tient à ce test, pas à ses 9 événements en direct, qui n'ajoutent presque rien.

**Correctif** : `enquete.selection_multiple` calcule aussi un z « un événement = un tirage » (somme par événement de paiement − prix payé, divisée par la racine de la somme de leurs carrés) et garde le plus
prudent des deux (`_z_by_event`). `compteur_tweets` passe de +2,56 à +1,72. Test : `test_selection_z_counts_the_legs_of_one_event_once` (30 paris, 28 gagnés à 0,8, trois événements : z par pari ≈ +3,3, par événement < 1,6).
Le score de l'arène (`arena.t_stat`) compte encore chaque pari ; la confiance « par jour » (`day_confidence`) regroupe déjà les paris clôturés le même jour, ce qui couvre les échelles : aucun changement du noyau de l'arène.

## 2. Contrôle `mere_muette_fille_active` : 3 mères sur 4 étaient éliminées (famille 6)
Le contrôle écrit à midi signalait `nf_sport_court`, `nf_tennis` (×3 filles) : leurs journaux ne battent plus depuis le 21/10 parce que **ces stratégies sont éliminées** (`published/data.json` → `eliminee: true`,
comme `nf_sport_patiente_tennis`). Ce sont des mères arrêtées, pas muettes. Seule `nf_sport` (suspendue puis relancée par la correction de midi) était un vrai cas, déjà réglé.
**Correctif** : une mère dont le dernier battement a plus de 48 h est ignorée. Test : mère éliminée → rien ; mère suspendue mais vivante → toujours signalée.
(La fiche de midi range ces trois mères parmi les « muettes à prudence ¼ ou ½ » : à lire comme « éliminées » ; seule `nf_sport` était bloquée par le plafond.)

Autre constat sur `nf_sport` : elle est de nouveau **suspendue** (« ne gagne pas ses frais : gains bruts 1,29, frais 25,07 sur 75 opérations ») alors qu'elle venait de se remettre à acheter (mises de 4 à 20 € au quart de Kelly).
La règle `strategy_health.suspension` (net < 0 et brut ≥ 0) bascule dans un sens ou l'autre à chaque clôture : une perte brute de 1,3 € la lève. Pas un défaut de comptabilité, une règle à bord flou ; à surveiller.

## 3. Contrôle `mises` : 47 « mises de fantôme au-dessus de 25 % » (famille 4 : le filtre ne filtre pas)
Le plafond `fantomes.max_mise` (25 % du capital marqué au cycle) a-t-il fui ? Non : le contrôle divisait par le **dernier battement**, qui peut dater de 30 minutes. Exemple : `nf_sport_prix_haut_3_6h`
« No » 355 € le 26/10 à 13 h 42 = 34 % de 1 039 € (battement de 13 h 18) mais 25,0 % de 1 415 € (le capital marqué au cycle d'achat : des positions de matchs finis étaient passées de ~0,9 à ~1 sans aucun achat entre les deux).
Sur 76 achats signalés depuis le 15/10, 67 restent au-dessus de 25 % après correction, **tous** d'avant le 23/10 (le plafond `_cap_ghost` date du 23/10) ou à 25,0-26 % (frais et arrondi des parts) ; plus aucune mise entre le 23/10 et aujourd'hui ne dépasse 26 %.
**Correctif** : capital = le plus grand des deux battements autour de l'achat, tolérance de 5 % comme pour le principal. Test : `test_stake_measured_on_a_stale_heartbeat_is_not_a_breach`.

## Pistes écartées en route
- « La championne gagne sur les marchés hors match » : la coupure par la présence du champ `depuis_coup_d_envoi_h` ne sépare pas les types, elle sépare les ACHATS D'AVANT LE 20/10 (champ ajouté ce soir-là) : 68 des 85 « hors match » sont des vainqueurs de match. Rien à retenir.
- `toucher_metaux` : abstentions vides, mais c'est voulu (ne joue que les marchés nés après le premier relevé gold-api du 24/10 ; premiers achats attendus la semaine du 02/11).

## Contrôles ajoutés / modifiés dans `src/polymarket_agent/enquete.py`
`selection_multiple` (z par événement), `mere_muette_fille_active` (mère arrêtée ≠ muette), `mises` (battement d'après, tolérance 5 %).
