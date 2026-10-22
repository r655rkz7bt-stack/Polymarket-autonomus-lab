# Piste n° 3 `marge_coherente` : tranches « marge de victoire » contre « vainqueur » (Brésil, 22/10/2026)

**Question** : pour un candidat, la somme des prix de ses tranches « gagne par moins de 5 % / 5-10 % / … » doit redonner son prix « vainqueur ». Un écart = achat du côté le moins cher.

**En direct (2e tour, 22/10 15 h UTC, vrais carnets)** : `experiments/marge_coherente/releve.py`.
- Flávio : somme des meilleures ventes des 4 tranches 0,803, meilleur achat « vainqueur » 0,777 : **+0,026** (tailles : 709 parts pour la plus petite tranche, 1 382 pour le vainqueur).
  Montage : achat OUI « vainqueur » + achat NON des 4 tranches (paie 4 dans tous les cas, coûte 3,974) : **+0,65 % sans risque**, jusqu'au 26/10. Côté achat des tranches : 0,828 (écart −0,052 : pas d'arbitrage dans ce sens).
- Lula : tranches 0,196-0,209 contre « vainqueur » 0,220-0,230 : montage inverse +0,011 (taille 120 parts sur la plus petite tranche).

**Sur le passé (1er tour, prix du CLOB à 12 h, 1/09 → 4/10, 67 points)** : `historique.py`. Somme des tranches − vainqueur : Flávio +0,044 en moyenne (septembre +0,053, octobre −0,031),
Lula −0,026 (septembre −0,033, octobre +0,028) ; |écart| > 0,02 dans 78 % / 69 % des points. Le sens change d'un mois à l'autre : pas de biais fixe à jouer, et ce sont des prix du milieu, pas des carnets.
(Le 1er tour n'a qu'un seul événement : aucune confiance statistique possible.)

**Verdict : indice, non exploitable par l'arène** (un seul scrutin ; gain maximal ≈ 0,65 % sur 4 jambes, quelques centaines de parts). À relancer 2-3 fois avant le 25/10 pour voir si l'écart persiste ; si oui, à noter comme chantier de
stratégie à jambes multiples (l'arène achète une jambe à la fois, ce qui ne permet pas de verrouiller l'écart).
