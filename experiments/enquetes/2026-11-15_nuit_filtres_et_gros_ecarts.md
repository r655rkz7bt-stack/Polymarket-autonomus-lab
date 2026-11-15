# Enquête du 15/11/2026 (passage de 1 h) : filtres des nouveaux achats, achats à gros écart relus à la source, positions « oubliées »

Jour 15 → famille 4 (15 mod 6 + 1). Feuille de mission : **aucune « Enquête obligatoire »**. Ici : famille 4, puis familles 3 et 6.

## 1. Famille 4 (« le filtre ne filtre pas ») : les 13 achats depuis le dernier contrôle (14/11 10 h 52 UTC)
Script : `experiments/enquetes/scripts/filtres_v2_15_11.py [depuis]` (journaux signés publiés à 00 h 47 UTC) contre
`config/strategies.yaml` : plage de prix (pour `non_aux_drames` : 1 − `yes_max` … 1 − `yes_min`), horizon (heures ou jours),
`min_net_edge`, borne basse au-dessus du prix, `mise_max_pari`, mise > 25 %.
**Piège évité** : la première version lisait la config comme une liste et ne trouvait aucun réglage → « 0 écart » sans rien
vérifier. Corrigé (dictionnaire par identifiant, réglages `{value: …}`) et le script signale maintenant « réglages introuvables ».

| Période | Achats | Écarts |
|---|---|---|
| depuis le 14/11 10 h 52 | 13 (`compteur_tweets` 6, `rt_compte_critiques` 3, `non_aux_drames` 2, `mississippi_plus_bas` 1, `rougeole_compteur` 1) | 0 |
| depuis le 07/11 (contre-épreuve) | 208 | 0 |

## 2. Famille 3 : les achats à gros écart relus à la source
- **`rougeole_compteur`** : NON « 6 000+ cas au 30/11 » à 0,30 pour une chance du NON de 0,6455 (écart 0,21). Page du CDC relue :
  « As of November 12, 2026, 5,412 » (+230). `rougeole.p_seuil` refait à la main avec le journal (hausses 264, 330, 230 →
  µ 275, σ 51) : P(≥ 6 000) = **0,3545**, exactement la chance de l'achat. Le marché (milieu 0,78) est un carnet de 10 parts
  (acheteur du OUI à 0,70, vendeur à 0,86, liquidité 208 $) : il faut +588 en deux mises à jour (19/11, 26/11 = Thanksgiving).
  Conforme.
- **`mississippi_plus_bas`** : OUI « Baton Rouge plus bas ≥ 6,00 ft d'ici le 30/11 » à 0,817 (chance 0,975). Règle relue : la
  fenêtre part de la **création du marché (21/09)**, pas d'aujourd'hui ; plus bas USGS (moyenne du jour) depuis le 21/09 =
  6,38 ft (09/11) ; prévision NWPS du 14/11 : remontée à 8,8 ft le 22/11 puis 7,4 ft le 30/11. `mississippi.debut_fenetre` lit
  bien `startDT=2026-09-21` du lien de la règle. Conforme.
- **`rt_compte_critiques`** (3 achats, réglés le 16/11) : NON « Ebenezer 55+ » 0,76 → 0,91 ; NON « Victorian Psycho 75+ » 0,61 →
  0,895 ; OUI « Ebenezer 50+ » 0,849 → 0,93 (milieux à 01 h UTC). Rien d'anormal.

## 3. Famille 6 et constats « à regarder »
- `positions_oubliees` (`favori_politique_quasi_certain`, 5 marchés, « échéance dépassée de 164 h ») : élection législative de
  Nouvelle-Zélande (2116493/94, 2117123/24, 2118145), `closed: false`, résultats officiels attendus le 27/11 : voulu.
  `capital_bloque` (0,06 € disponibles) en découle.
- `muettes` : `el_nino_cpc` voit 4 marchés, « avantage net insuffisant » ×3 (le marché suit les chances publiées du CPC ;
  prochaine mise à jour le 11/12) ; `suivre_inities` : aucune grappe (connu). Voulu.
- Convictions réglées relues : **Danube OUI réglé « Yes »** (6581026, résolu) ; **Rhin NON** : plus haut de Kaub 74 cm le
  14/11 à 07 h 45 (Berlin), seuil 77 non atteint avant le 15/11 00 h, 62 cm à 01 h 45 : la v6 (NON à 0,862) gagnera au règlement.

## 4. Relecture d'une stratégie retenue de la v1 (avant de la relancer)
`detroits_marche_log` (« retenue » sur le passé le 23/10 : +24 %, z 2,83) n'a pas été reprise en v2. Ses 30 achats v1 relus
sur Gamma : **24 positions réglées, 892 € misés, −267 € (−30 %), 11 gagnées pour 12,6 payées**. Le test sur le passé ne
s'est pas confirmé en direct (paris liés : 4 semaines × 2 détroits) : pas de relance. Ligne au carnet d'expériences.

## Bilan
Aucun défaut dans l'arène en service : 0 écart de filtre, 4 achats à gros écart conformes à la source. Un défaut dans MON
contrôle (lecture de config qui rendait « 0 écart » sans rien vérifier), corrigé avant de conclure. Aucun contrôle ajouté à
`enquete.py` (rien qu'il aurait dû trouver). Règle n° 7 : `www.ukmto.org` répond 403 à tout, `robots.txt` compris (marché
« How many UKMTO notices ») : aucun contournement.
