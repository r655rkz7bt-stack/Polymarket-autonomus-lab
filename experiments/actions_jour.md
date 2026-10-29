# « Up or Down » du jour sur actions, indices et métaux : le prix suit-il le cours en séance ? (29/10/2026)

**Verdict : écartée.** Aucun réglage stable ; un seul (H-2) ressort, et ses voisins (H-1, H-3) vont dans l'autre sens.

- Données : 1 516 marchés réglés (août-octobre 2026, 23 titres dont SPX, SPY, RUT, DJIA, 12 actions), 484 769 échanges réels
  (`releve_echanges.py`), cours de 5 minutes Yahoo (`releve_yahoo.py`, recherche seulement). `feeSchedule.rate = 0` (aucun frais).
  Règle : clôture du jour contre clôture de la veille (4 h de l'après-midi, heure de l'Est).
- Modèle (`analyse.py`) : p(Up) = Φ(rendement depuis la clôture de la veille / volatilité de 5 min restante, mesurée sur les 10 séances précédentes).
  Prix payé = premier échange de preneur réel dans l'heure qui suit. Seuls les bars finis servent.
- Résultat, 931 cas, marges de 0,03 / 0,06 / 0,10 (18 réglages essayés au total) :

| Heure avant la clôture | Rendement par pari | Log-loss modèle / prix |
|---|---|---|
| H-1 | −40 / −53 / −65 % | 0,223 / 0,228 |
| H-2 | +25 / +34 / +35 % | 0,254 / 0,254 |
| H-3 | +15 / −19 / −13 % | 0,270 / 0,279 |
| H-4 | +10 / +3 / +7 % | 0,300 / 0,320 |
| H-5 | 0 / −22 / −13 % | 0,360 / 0,372 |
| H-6 | −6 / −6 / −30 % | 0,416 / 0,450 |

- Lecture : le modèle est un peu meilleur que le prix en log-loss à H-3…H-6 (marchés peu liquides, 400 à 3 000 $ par action), mais les achats simulés
  changent de signe d'une heure à l'autre ; `z` des prix entre −1,3 et +1,9. Compatible avec du bruit (18 réglages). Les marchés les plus liquides (SPX, SPY) sont à regarder séparément si on y revient.
- Limites : 58 séances seulement (limite de Yahoo), volatilité intrajournalière approximative, profondeur du carnet non mesurée.
