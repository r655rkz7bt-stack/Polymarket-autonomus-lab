# Piste n° 47 : échelles de seuils incohérentes (13/11/2026, passage de 1 h)

**Idée** (cohérence entre marchés liés) : dans une même échelle « at least 6.0 % / 7.0 % », atteindre le seuil difficile implique
atteindre le facile : P(difficile) ≤ P(facile). Si le vendeur du OUI facile + (1 − l'acheteur du OUI difficile) < 1, NON(difficile) +
OUI(facile) paie au moins 1 quoi qu'il arrive. Vu en lisant « How high will US unemployment go in 2026? » : « ≥ 7,0 % » acheté 0,026
pendant que « ≥ 6,0 % » se vend 0,007.

**Relevé** (`echelles_seuils/releve.py`, `echelles.py`) : 6 000 événements ouverts les plus actifs (Gamma `/events/keyset`), 73 546
marchés, regroupés par événement et par question identique au nombre près, sens lu dans la phrase, même date de fin, seuil facile créé
au plus tard un jour après le difficile (fenêtres « depuis la création du marché » de Freddie Mac) : **6 142 paires**.

- Premier passage : 32 paires « incohérentes », jusqu'à 62 points — **faux positifs** : « Will Trump's approval rating hit 30 % » est
  une barrière vers le BAS et « hit 45 % » vers le haut, avec la même phrase. « hit » et « reach » ne disent pas le sens ; seuls « at
  least », « above », « below », « (HIGH) / (LOW) »… sont gardés.
- Après correction : **8 paires sur 6 142** à plus de 0,5 point, au plus **2 points avant frais** (Valantis FDV 300 / 500 M$ : 0,020 ;
  chômage 6 / 7 % : 0,019 bloqués jusqu'en janvier ; Hotstuff 0,010 ; Pacifica, NVIDIA ≤ 0,006).

**Verdict : écartée.** Les échelles sont presque toujours monotones ; ce qui reste vaut 1-2 points immobilisés des semaines, pour des
carnets de quelques centaines de dollars. Rien dans l'arène (les arbitrages de paires de la v1, `echelle_dates`, `paire_oui_non`, avaient
déjà montré la même chose). Leçon de méthode : un regroupement automatique de marchés doit lire le SENS de chaque seuil, pas seulement le
nombre.
