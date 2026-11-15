# 15/11/2026 (passage de 6 h) : jambes exemptées par classe, TreasuryDirect interdit aux robots, compteurs relus

Jour 15 → famille 4 (faite à 1 h) ; ici le constat nouveau de l'enquête automatique, familles 3 et 2.

## 1. Constat `jambes_meme_evenement` : `compteur_truth`, 4 marchés d'un événement, 179 € (15/11 02 h 06-02 h 11)
- Achats relus sur Gamma : NON de « 20-39 », « 40-59 », « 60-79 », « 80-99 » posts de Trump du 13 au 20/11 (événement 1354153),
  payés 0,926 / 0,835 / 0,832 / 0,82 pour des chances de 0,97 / 0,967 / 0,94 / 0,866. Tranches **disjointes** : au plus une perd
  (le pire cas coûte la plus grosse jambe, ≈ 83 €), le contraire de paris liés.
- **Défaut du contrôle** : l'exemption `_JAMBES_VOULUES` ne regardait que le NOM du portefeuille (`compteur_tweets…`), pas la
  classe ; `compteur_truth` (classe `compteur_tweets`) sortait à tort. Correctif : `jambes_meme_evenement(..., configs=)` exempte
  aussi par la classe (`enquete.run` passe la config) ; test `test_legs_wanted_by_the_class_not_only_by_the_portfolio_name`.
  Après correctif, le constat disparaît.
- Le fond : le modèle attend ≈ 140 posts (rythme mélangé 0,92/h : 168 h à 0,37/h, 336 h à 1,47/h encore porté par la rafale du
  28/10-03/11), le marché ≈ 100 (médiane). XTracker relu à 05 h 56 : 19 posts au compteur, 62 sur 7 jours, 494 sur 14 jours ;
  la garde `desaccord_max` ne joue pas (mélange 0,92 < 1,6 × médiane 0,71). **Rejeu sur l'archive CNN**
  (`experiments/regime_rafale/sortie_rafale.py`, 356 périodes, décisions à 24-144 h) quand le rythme 336 h vaut ≥ 2 fois celui de
  168 h : 11 décisions (7 périodes), total prévu − réel **+3,6** posts pour le mélange actuel (pas de biais haut), médiane des
  rythmes −1,9 (log-perte 0,068 contre 0,090) ; de 1,5 à 2 fois : 50 décisions, +1,6 contre −6,0. Pas de défaut prouvé ;
  échantillon minuscule. Règlement le 20/11 (un tirage).

## 2. Règle n° 7 : TreasuryDirect `/NP_WS/` interdit par robots.txt
- En relisant la conviction « dette à 41 000 Md$ », `scripts/robots_ok.py` répond **INTERDIT** pour
  `www.treasurydirect.gov/NP_WS/debt/search` et `/NP_WS/debt/current`. Le relevé du 12/11 (`experiments/dette_us/analyse.py`)
  l'a lu sans vérifier (avant l'outil du 14/11). Aucun code de production ne l'appelle (grep).
- Correctifs : `treasurydirect.gov/NP_WS/` ajouté à `INTERDITS_CONNUS` (`tests/test_robots_ok.py`) ; astuce de
  `docs/ROUTINE_CHERCHEUR.md`, `CHANTIERS.md` et le script renvoient à **Fiscal Data « Debt to the Penny »** (permis, JSON,
  répond depuis la routine) : **40 608,5 Md$ au 12/11**, loin du seuil d'abandon de la conviction (40 800 avant le 01/12).

## 3. Famille 2 : les trois `compteur_*` (−90, −81, −51 €)
- `compteur_tweets` 35 paris : 21 gagnés pour 22,0 attendus par les prix (24,8 par le modèle) ; `compteur_truth` 10 : 6 pour 7,1 ;
  `compteur_tweets_72_168h` 10 : 7 pour 6,2. ≈ −69 € de chacun viennent du MÊME événement (semaine de Trump du 6 au 13/11, mêmes
  trois jetons : un tirage compté trois fois). Sans lui, `compteur_tweets` −21 € sur 10 événements. Gagnent comme leurs prix,
  le modèle sur-estime (+2,8 gagnés) : pas de défaut de code, indice faible d'optimisme, à relire au 20/11.

## Vérifié sans défaut
Convictions ouvertes relues avec leurs prix (Google 0,855, Rihanna 0,24, Michigan « pas 55 » NON 0,9625, Rhin NON 0,985, dette
milieu 0,655 sur carnet mince) : rien ne bouge contre elles.
