# 31/10/2026 (après-midi) : éliminées encore configurées, et calibration de `mots_prononces`

## 1. Obligation « 43 stratégies éliminées encore configurées »
- Constat : la feuille de mission listait 43 stratégies éliminées par l'arène mais toujours `enabled: true` (les passages du 31/10
  nuit et matin avaient essayé de les couper et renoncé : des tests lisent la config réelle).
- Cause des blocages : `load_strategies` ne rend que les stratégies activées ; 7 tests cherchaient des stratégies coupées.
- Correctif : `enabled: false` pour les 43 (`config/strategies.yaml`), `load_strategies(path, include_disabled=True)` pour les tests
  qui vérifient les paramètres des filles coupées, liste de `test_repository_config_loads` réduite des coupées. 652 tests verts.
- Les 3 filles « 80/20 » demandées (contrer_crypto_audace 72-168 h, contrer_crypto_patiente 12-24 h, nm_long 168 h+) ne sont pas
  créées : 9, 56 et 10 opérations, mère crypto « contrer » écartée sur le passé (`contrer_crypto_passe.md`), z par événement non
  démontré ; la mère `contrer_crypto_audace` est justement éliminée.

## 2. Constat « à regarder » : `mots_prononces` estimé 0,648, payé 0,31 (30/10 20 h 21)
- Le pari (« Affordable » au meeting de Floride) a perdu. Un pari isolé ; on regarde les 84 achats réglés (14 événements).
- Estimé / prix / gagné par bande d'estimation : 0,40-0,60 : 52 paris, 0,504 / 0,406 / 0,385 ; 0,60-0,80 : 22 paris, 0,683 / 0,593 / 0,545.
- Par événement (14) : 7,7 estimés, 6,5 attendus par les prix, 6,0 gagnés ; gain +3,9 € sur 648 € misés (+0,6 %).
- Lecture : le modèle surestime d'environ 12 points (comme l'indice de `compteur_tweets` >= 48 h inversé) mais le prix payé
  reste à peu près juste : pas d'avantage, pas de perte nette. 14 événements : trop peu pour toucher au modèle. À relire à 30.
- Pas de défaut de code : `estimation_perimee` reste un constat, pas une obligation, pour les modèles propres (24/10).

## Vérifié sans rien trouver
Essence : 1 jour de plus (31/10, tranche 4,18-4,19). Rougeole : pas de nouveau mercredi depuis le 29/10.
