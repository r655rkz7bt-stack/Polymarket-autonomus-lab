# 07/11/2026 (midi) : XTracker en 403, le champion est aveugle depuis 16 h

**Famille 6 (« qu'est-ce qui ne tourne plus : source en panne »).**

- **Constat** : `xtracker.polymarket.com` répond 403 (HTTP 403, 59 octets, aussi pour `/api/users`) depuis le 06/11 ≈ 19 h UTC. Le dernier achat de `compteur_tweets`
  (champion, copié par le principal) et de `compteur_truth` date du 06/11 à 19 h. Chaque cycle s'abstient (« compteur pas à jour »), ce qui est le bon comportement,
  mais le champion ne peut plus rien acheter ni régler son rythme tant que la source est coupée. Signalé à six passages de suite sans solution.
- **Cause** : un seul fournisseur pour le compteur (aucun secours dans `references.fetch_tweet_trackings`).
- **Correctif** : secours par l'archive CNN pour Trump seulement (`experiments/truth_cnn.md` : 332 heures sur 336 identiques à XTracker, sous-compte de ~25 % dans les heures de rafale,
  période marquée `incertain` et abstention dans ce cas). Test : `tests/test_references.py` (deux tests). Cycle local : XTracker 403 → secours → 2 périodes de Trump rattachées (`source: cnn_archive`).
- **Chiffre** : −12 % sur la période de la rafale (530 contre 605), 0 sur les périodes calmes (3/3, 34/34).
- **Contrôle automatique** : `sources_vides` et `retraits_inactifs` disaient déjà la panne ; rien à ajouter.

## Contrôles à la main faits au même passage (aucun défaut)
- **Règlement (famille 3)** : 12 paris du principal réglés depuis le 25/10 (sur 346, −79 €) tirés au hasard (graine 7), marché relu sur Gamma `/markets/<id>` : le paiement par part du journal
  égale le prix final du jeton dans 12 cas sur 12 (tennis, e-sport, NBA, totaux, séismes, score exact, Elon Musk).
- **Positions jamais réglées (famille 6)** : 65 positions ouvertes du principal (249 € de coût), aucune sur un marché que Gamma dit déjà fermé.
