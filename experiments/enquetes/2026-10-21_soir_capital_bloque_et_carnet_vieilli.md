# 21/10 (soir) : capital bloqué des mères, et carnets du début de cycle rejetés avant relecture

Famille 6 (« ce qui ne tourne plus ») du jour 21 + 1, puis famille 5 (comparaisons faussées) : l'enquête était partie de 15 stratégies activées
sans aucun achat et de 12 qui n'achetaient plus depuis des jours. Scripts : `scripts/mere_fille_21_10.py` (journaux signés) ; un cycle local complet
(`scripts/run_simulation.py --once --dev-key`, 20 h 14 UTC) pour voir les abstentions et rejets.

## 1. Mères sans argent, filles qui achètent
- `naive_favorite` (mère de nf_court, nf_sport, nf_moyen, nf_oui…) : **0,2 € disponible dès le 16/10 à 23 h**, 861 € bloqués en 16 positions ; même histoire pour
  `favori_politique` (924 € en 15 positions, dernier achat 16/10), `favori_politique_quasi_certain` (0,04 €), `favori_politique_nuit`, `naive_favorite_large`,
  `naive_favorite_sans_fin` : le Kelly complet (`kelly_fraction 1`) engage tout le capital en quelques cycles (cash 710 → 1,6 € en 15 minutes le 16/10), puis
  l'argent revient par bribes au règlement et repart aussitôt (10-18 03 h 29 : dernier achat de la mère).
- Leurs filles filtrées (même classe, **mêmes paramètres**, un filtre de plus) ont continué : sur 122 achats de `nf_court`, 118 jetons que la mère n'a pas
  (cash médian de la mère à ces instants : 0,14 €). Une fille « bat sa mère » alors qu'elle a de l'argent et pas la mère : mêmes règles, pas la même situation
  (famille 5 : « avec le même argent disponible »). Le contrôle `filles_periode` ne regardait que la période.
- Depuis le 18/10 22 h 49 la mère a de nouveau 87 → 257 € et n'a rien acheté en 3 jours (au même moment `nf_court` et `nf_moyen`, sans filtre de famille donc
  même liste de marchés, achètent) : **cause non établie** (un cycle local avec argent neuf : la mère propose 3 achats et les exécute ; le journal publié ne garde
  ni les propositions ni les rejets : la table `decisions` est vidée de la sauvegarde).
- Correctif : aucun changement de règle (les fantômes restent des fantômes) ; contrôle **`capital_bloque`** ajouté à `enquete.py` (moins de 10 % du total
  disponible pendant 48 h, au moins 5 achats), test avec le cas réel. Sorties du jour : favori_politique (81 €), quasi_certain (7,6 €), nuit (0,04 €).
  Ordre de lecture à retenir : avant de comparer une fille à sa mère, regarder leur argent disponible.

## 2. Carnet du début de cycle rejeté « périmé » avant d'être relu (`main._execute`)
- Le cycle local de 20 h 14 a duré 2 min ; 158 propositions, 56 exécutions, **12 rejets « carnet périmé (121-287 s > 120 s) »** décidés par le premier `evaluate`, alors
  que le carnet est relu et recontrôlé juste après. Les portefeuilles traités en dernier perdent donc des achats légitimes : ce n'est pas un défaut de marché
  mais de position dans la boucle (famille 5).
- Correctif : `_execute` ne rejette plus sur le seul motif « carnet périmé » avant la relecture ; le contrôle après relecture garde le même plafond
  d'âge (`max_book_age_seconds`, noyau inchangé). Test : `test_book_aged_by_earlier_portfolios_is_reread_not_rejected` (échoue sans le correctif).
- Ampleur en production : **inconnue** (les rejets ne sont pas publiés). La durée d'un cycle de production n'est pas dans les journaux (tous les battements d'un cycle
  portent la même heure). À mesurer : publier la durée du cycle et le nombre de rejets par motif (proposition ouverte pour Etienne : `cycle.yml` est protégé).

## 3. Autres vérifications
- 15 stratégies activées sans achat (0 achat, nées il y a 25-33 h) : références Kalshi/PredictIt/Manifold, bookmakers, `cpi_tranches`, `statu_quo_ia` : attendues
  (peu de marchés correspondants, première journée) ; `crypto_threshold*` : en pause voulue (`max_proposals_per_cycle 0`, 16/10).
