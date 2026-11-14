# Enquête du 14/11/2026 (passage de 11 h) : `compteur_truth` muette, filtres des fantômes v2 (famille 4)

Jour 14 → famille 3 (faite au passage de 6 h, avec la famille 6). Ici : un constat « à regarder » mené au bout, puis la famille 4.
Feuille de mission : aucune « Enquête obligatoire ».

## 1. `compteur_truth` n'achète plus depuis le 10/11 (constat « achetaient et n'achètent plus depuis plus de 72 h »)

Abstentions du dernier cycle : « compte écarté » ×29 (marchés d'autres comptes : voulu, `only_trump`) et « rythmes en désaccord » ×6
(les 6 seuils de « Donald Trump # Truth Social posts November 13 - November 20 »).

Relu sur la sauvegarde de la base du 14/11 (`kv` → `ref:tweets`, lu à 23 h 51 UTC le 13/11) : 336 heures relevées, rythmes en posts
par heure : 24 h **0,25**, 72 h **0,32**, 168 h **0,42**, 336 h **1,81**, 84 jours **1,20** ; médiane 0,42, mélange du modèle
(½ × 168 h + ½ × 336 h) **1,11**, soit **2,64 fois** la médiane (garde : 1,6). Les heures 168 à 336 (≈ 31/10 → 06/11) comptent
≈ 3,2 posts par heure : c'est la rafale record du 28/10-03/11. Sans la garde, le modèle prolongerait ≈ 1,1 post/h quand Trump en publie
0,3-0,4 : exactement le défaut du 04/11 (« 200+ » estimé 0,968, `experiments/regime_rafale.md` : 0,275 annoncé pour 0,175 réalisé
au-dessus de 1,6 fois la médiane, 57 seuils).

**Pas un défaut** : la garde fait ce pour quoi elle a été écrite. Elle se lèvera quand la rafale sortira de la fenêtre de 336 h
(il faut ≈ 309 posts au plus sur 14 jours à 0,42/h de médiane : vers le 18-20/11 si Trump garde son rythme). L'événement du 13-20/11
sera donc presque entièrement manqué. Rien à corriger ; noté pour ne pas le rouvrir.

## 2. Famille 4 (« le filtre ne filtre pas ») : tous les achats des fantômes v2

Script à la main sur `published_data/ledger/fantome_v2/*.jsonl` (journaux signés publiés à 10 h 52 UTC) contre les réglages de
`config/strategies.yaml` : **195 achats** de 19 fantômes depuis le 07/11.

| Contrôle | Achats vérifiés | Écarts |
|---|---|---|
| prix payé dans [`min_price`, `max_price`] | 195 (tous les fantômes à plage) | 0 |
| horizon dans [`min_hours`, `max_hours`] (`favori_politique_quasi_certain`) et [`min_days`, `max_days`] (`non_aux_drames`) | 77 | 0 |
| `net_edge` du journal ≥ `min_net_edge` | 195 | 0 |
| borne basse (`prob_low`) au-dessus du prix payé | 195 | 0 |
| mise > 25 % du capital du fantôme | 195 | 0 |

Aucun filtre contourné, y compris par les ordres posés (aucun achat sous la plage depuis la v2). Le seul achat de
`mississippi_plus_bas` (OUI à 0,12 pour 0,277 estimé, horizon 444 h, 93,6 parts, frais 0,49 €) respecte sa plage et son écart.

## 3. Autres constats relus
- Source `tornades` « indisponible » (HTTP 504 du SPC sur un fichier d'octobre) : panne du serveur de la NOAA ; la source est gardée
  volontairement alors que `tornades_mois` est éteinte (le compte tel que publié servira au test sans regard vers le futur).
- `rougeole_compteur` et `suivre_inities` muettes : déjà élucidées (avantage insuffisant ; aucune grappe de comptes neufs).

## Bilan
Dans l'arène en service : aucun défaut chiffré, aucun contrôle ajouté à `enquete.py` (la garde des rythmes écrit déjà sa raison
dans les abstentions ; les filtres sont tenus). Un défaut trouvé et corrigé dans la nouvelle stratégie AVANT sa mise en service
(section 4).

## 4. Défaut trouvé dans ma propre stratégie avant sa mise en service (`rt_compte_critiques`, famille 3)
Premier cycle local de la nouvelle expérience (11 h 11 UTC) : achat de « I Play Rocky 83+ » OUI à 0,80 (24,45 parts, chance 0,973).
Le film n'est sorti qu'en salles LIMITÉES (06/11) et le marché se règle le 23/11, après la sortie large : la donnée (115/133 critiques)
n'est pas celle du règlement, une vague de critiques plus froides arrive (à 75 % de positives pour 80 nouvelles : 82,2 %, sous 83).
Cause : rythme a priori par l'âge du film (0,03 critique/h à 8 jours), aveugle au type de sortie. Correctif : `parse_page` lit
« Release Date (Theaters) …, Limited / Wide » ; aucune chance pour une sortie limitée ; glissement de −5 points de la part positive
des critiques à venir. Test du cas réel : `tests/test_rotten_tomatoes.py::test_collect_attach_and_buy_only_a_cheap_side` (Rocky
sans référence). Coût : 0 € (cycle local, journal ignoré par Git).
