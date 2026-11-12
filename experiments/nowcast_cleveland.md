# Piste n° 38 : la prévision d'inflation de la Fed de Cleveland contre les marchés CPI et PCE (12/11/2026, passage de 11 h)

**Idée** (même famille que le Michigan et le PIB canadien : un chiffre presque connu avant sa publication) : la Fed de Cleveland
publie chaque jour, gratuitement, sa prévision (« nowcast ») du CPI, du CPI de base, du PCE et du PCE de base, en variation sur
un mois et sur un an. Le prix des tranches « <mois> Inflation US - Monthly / Annual », « Core CPI MoM / YoY », « Core PCE MoM / YoY »
la suit-il ?

## Données

- **Source** : `www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json` (et `nowcast_year.json`,
  `nowcast_quarter.json`), sans clé, `robots.txt` lu (seul `/errors/*` interdit). 161 mois cibles depuis juillet 2013 ; pour
  chacun, la prévision jour par jour **telle que publiée** et le chiffre publié (« Actual », non arrondi). C'est un historique
  en temps réel : aucune prévision recalculée après coup.
- **Marchés** : `/events/keyset` des étiquettes `cpi` (101701) et `inflation` (702) : 212 événements, 70 d'inflation américaine
  à tranches, **64 réglés** (décembre 2024 à octobre 2026 : CPI sur un mois 21, sur un an 24, CPI de base 5 + 5, PCE de base 4 + 4),
  452 tranches ; prix horaires des 9 derniers jours (`prices-history`).
- Scripts : `nowcast_cleveland/scripts/` (`releve_tags.py`, `prix.py`, `commun.py`, `analyse.py`, `melange.py`).

**Contrôle du règlement** : le chiffre publié par Cleveland, arrondi au dixième, tombe dans la tranche gagnante **61 fois sur 61**.

## Méthode (sans regard vers le futur)

Décision k jours avant la publication (k = 1, 2, 4, 7) ; prévision publiée **la veille** du jour de décision ; erreur de la
prévision au même délai, mesurée sur les seuls mois publiés avant la décision (≥ 24 mois, depuis 2013) ; chance de chaque tranche
par une loi normale (biais et écart-type de ces erreurs) ou par les erreurs elles-mêmes.

## Résultat

| Délai | Log-score de la prévision | Log-score du marché |
|---|---|---|
| 1 jour | −1,319 | **−1,051** |
| 2 jours | −1,318 | **−1,101** |
| 4 jours | −1,319 | **−1,130** |
| 7 jours | −1,319 | **−1,059** |

Le marché fait mieux partout sauf le CPI de base sur un an (5 mois, marché −2,42 contre −1,85 : trop peu pour conclure). Quatre
réglages à 1 jour (normale, normale sur 36 mois, empirique, empirique sur 60 mois) : −1,24 à −1,39, toujours sous le marché.
Mélange géométrique marché × prévision (poids 0,2 / 0,35 / 0,5) : le log-score ne s'améliore jamais (−1,058 à −1,150 contre
−1,051) ; achats simulés à « mélange − prix > 0,05 » : 6 à 36 paris, 1 à 3 gagnés pour 1,0 à 4,8 attendus (−52 % à +49 %,
au hasard). 3 délais × 4 poids × 3 seuils essayés.

## Verdict

**Écartée** : la prévision publique de Cleveland est déjà dans le prix (les consensus des économistes, que le marché suit, la
contiennent). Ce qui reste de la famille « chiffre presque connu » : les cas où la source qui règle publie elle-même un chiffre
anticipé (Michigan, PIB canadien), pas les modèles publics.

Note pour octobre (lu le 12/11) : PCE de base sur un mois, prévision Cleveland 0,267 après le CPI du 10/11 ; marché « 0,3 % » 0,58,
« 0,4 % » 0,35. Le PPI sort le 13/11.
