# Essai à blanc : règle actuelle contre « confiance progressive » (21/10/2026, demande d'Etienne)

Script : `experiments/regle_confiance/rejouer.py` (journaux publiés du 21/10 à 17 h 11 UTC, `scripts/fetch_data.sh`).
Rejeu heure par heure du 15/10 12 h au 21/10 17 h (149 heures) ; chaque règle ne voit que les opérations
clôturées avant l'heure jugée ; le principal simulé copie les paris réels des fantômes au prorata de sa part
(approximation : ni doublons, ni familles, ni exécutions partielles).

| règle | principal simulé | part engagée moyenne | qui reçoit l'argent |
|---|---|---|---|
| actuelle (t ≥ 1,5, appliquée depuis le 15/10) | **+146 €** | 28 % | nf_sport_patiente (26,5 %), nf_sport_patiente_2crans (1,6 %) |
| proposée, scepticisme 0,5 | +0 € | 2 % | contrer_crypto_patiente (1,4 %) |
| proposée, scepticisme 0,25 | −5 € | 6 % | contrer_crypto_patiente, nf_sport_patiente |
| proposée, sans scepticisme | +18 € | 13 % | contrer_crypto_patiente (4,9 %), nf_sport_patiente (4,6 %) |

Confiance proposée (gagnés contre attendus, regroupés par jour) au 21/10 : nf_sport_patiente **71 %** (98 % avec
le calcul actuel), nf_sport_patiente_2crans 67 % (96 %), nf_tennis_prix_bas 68 % (87 %) ; seules
`contrer_crypto_patiente` (60 paris, 88 %) et `contrer_crypto` (47 paris, 88 %) restent hautes avec les deux calculs.

## Lecture
- Sur cette semaine, la règle actuelle a mieux gagné : elle a suivi nf_sport_patiente après sa journée du
  18/10, et celle-ci a encore gagné le 20/10 (14 paris sur 15). La règle proposée, prudente, l'aurait presque
  laissée de côté.
- Une semaine et une seule stratégie suivie ne permettent pas de dire si la championne a un vrai avantage
  (confiance 71 % sans dépendre d'une journée) ou si elle a eu de la chance deux fois.
- La nouvelle mesure ne fait pas que freiner : elle repère `contrer_crypto_patiente`, jamais suivie par la règle
  actuelle, la seule stratégie solide avec les deux calculs.
- À refaire avec deux à trois semaines de journaux avant de changer la règle.
