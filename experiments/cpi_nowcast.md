# Piste n° 3 : CPI américain, les tranches improbables (21/10/2026)

Question : sur les événements « inflation US » de Polymarket (une tranche par chiffre), les tranches que le marché prix à 5-30 % gagnent-elles
moins souvent que leur prix (biais des longs tirs) assez pour que leur NON rapporte après frais, écart et prix réellement payés ?
(La piste d'origine « contre le nowcast de Cleveland » n'a pas pu être menée : l'historique des prévisions du nowcast n'est pas
téléchargeable par versions ; le marché lui-même sert de référence.)

## Données (scripts : `experiments/cpi_nowcast/`, données dans `donnees/`, ignoré par Git)
- 48 événements CPI américains réglés (mensuel, annuel, core MoM/YoY), décembre 2024 → octobre 2026, 337 tranches. Prix OUI heure par heure (CLOB
  `prices-history`), 205 703 échanges réels de preneurs (`data-api`).
- **Contrôle du règlement** : 48 événements sur 48 ont exactement une tranche OUI à 1 ; les 337 marchés sont `resolved` (aucun litige).

## Calibration à T-24 h (331 tranches, 47 événements)
| prix OUI | n | gagne | prix moyen |
|---|---|---|---|
| 0,03-0,10 | 56 | 1,8 % | 5,7 % |
| 0,10-0,25 | 34 | 8,8 % | 16,7 % |
| 0,25-0,50 | 55 | 40,0 % | 37,1 % |
| 0,75-1 | 8 | 100 % | 90,7 % |
Les cases à 3-25 % gagnent environ **moitié moins** que leur prix, aux trois délais (T-24, T-72, T-168 h). Les favoris sont légèrement sous-cotés.

## Simulation : acheter le NON (frais 5 % · p(1−p)), 12 réglages (3 délais × 4 plages de prix)
- Prix horaire + écart 0,01 : +1,3 % à +8,0 % par achat, 12 réglages sur 12 positifs ; t par événement +0,8 à +15,9.
- **Aux prix des vrais échanges** (`taker_cost`, fenêtre 2 h) : « dernier échange AVANT la décision » = +0 à +7 % (10 réglages sur 12 positifs, t par événement
  faible en général ; 25 à 83 tranches sans aucun échange dans les 2 h) ; « premier échange APRÈS » = +5 à +16 % (10 sur 12 positifs, souvent t > 3).
  Le vrai prix payé est entre les deux : **≈ +3 à +6 % par achat**. Types : annuel +8,8 % (t +3,1), mensuel +6,1 % ; core (12 achats) négatif.
- Mois par mois : 13 à 19 mois gagnants sur 19-20 selon les réglages.

## Verdict : **indice** (fantôme, pas de capital)
Pour : biais de long tir classique, stable dans le temps et sur les délais, règlement propre, gain positif aussi aux vrais prix.
Contre : seulement 47 événements (les tranches d'un événement sont liées : une seule gagne), gain par achat faible (3-6 %), beaucoup de tranches sans échange
exécutable avant la décision, 12 réglages essayés, core négatif sur 12 achats. Marqué `indice` : stratégie `cpi_tranches` en fantôme (Kelly ¼), à confirmer sur les
prochaines publications (CPI d'octobre le 11/11/2026).
