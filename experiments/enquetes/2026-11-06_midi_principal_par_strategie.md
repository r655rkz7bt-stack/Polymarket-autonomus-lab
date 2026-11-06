# 06/11 midi : résultat du principal par stratégie copiée

**Question** : le capital principal (≈ 655 € estimés) a perdu 310 € sur 539 paris réglés ; la perte vient-elle d'un défaut encore actif ?

**Méthode** : journal signé du principal (`published_data/ledger/ledger.jsonl`), un pari par jeton, regroupé par `strategy_id`, gagnés (paiement par part) contre attendus (prix payé). Script : `scripts/principal_par_strategie_06_11.py`.

**Constat**
- Les trois plus grosses pertes sont anciennes : `nf_court` −145 € (18 paris, 14 gagnés pour 16 attendus, dernier achat 18/10), `meteo_prevision` −58 € (39 paris, dernier achat 17/10), `nf_sport_patiente_prix_850_875` −28 €.
- Stratégies encore actives au principal : `moins_de_cartes` −26 € (87 paris, 44,5 gagnés pour 50,4 attendus, dernier achat aujourd'hui), `compteur_tweets` +9 € (45 paris), `nf_sport` +12 €. Rien de plus grave que le −6 % global (387,5 gagnés pour 407,6 attendus).
- Pas de pari sans fantôme (voir fiche de la nuit), pas de règlement manquant.

**Verdict** : aucun défaut actif. Le trou vient de stratégies d'octobre déjà coupées ou éliminées ; `moins_de_cartes` (−12 % sur 87 paris) est à surveiller mais reste dans le bruit (z ≈ −0,8 en gagnés/attendus).
