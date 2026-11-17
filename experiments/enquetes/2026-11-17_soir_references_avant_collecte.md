# Les références étaient rattachées AVANT la collecte des sources : chaque lecture neuve ne servait qu'au cycle suivant (17/11/2026, passage de 16 h)

Trouvé par le nouveau contrôle « stratégie neuve, écart ≥ 0,30 » (`enquete.estimation_perimee`, fiche
`2026-11-17_soir_openrouter_jour_en_cours.md`), puis famille 3 à la main.

## Constat
- 16/11, 21 h 27 min 05 s (cycle `20261116T2125Z`) : `seismes_pays` achète le **NON « Will a 6.0+ magnitude earthquake occur in
  Indonesia this month? »** (marché 6422859) : 25 parts à **0,20**, chance du NON estimée **0,581** (fréquence de base des 14 jours restants).
- Catalogue USGS : **M 6,6, 148 km WSW of Tual, Indonesia, 21 h 11 min 20 s** (`us7000tymu`). Journal `ref:usgs` de production :
  première lecture (`vu`) **21 h 25 min 53 s**, dans la collecte du même cycle. L'EMSC (témoin du 11/11) ne l'a vu qu'à 21 h 40 min 59 s.
- Le marché le savait : un vendeur de NON à 0,20 ; OUI à 0,99 aujourd'hui. Perte ≈ 5 € (25 parts × 0,20).

## Cause (`src/polymarket_agent/main.py`, `run_cycle`)
Ordre des étapes : scanner → **4 bis `_attach_references`** (chances calculées sur les relevés en base) → candidats → carnets →
ordres posés → **6 bis collecte des sources** (relevés écrits en base) → stratégies. La lecture USGS de 21 h 25 min 53 s a été écrite
APRÈS que la chance de l'Indonésie a été calculée avec le relevé précédent (≈ 21 h 15, sans le séisme). Le défaut touche toutes les
stratégies à source : chacune décide sur la lecture d'avant, en retard d'un cycle (5 à 10 minutes) — justement au moment où une
nouvelle tombe et où le marché bouge, donc l'achat « bon marché » est celui que la nouvelle vient de rendre mauvais (sélection adverse).
Déjà noté sans être corrigé : astuce du 24/10 (« le rattachement des références passe avant la collecte du même cycle : lancer deux
cycles locaux ») et fiche du 11/11 (« catalogue en retard » : une partie du retard venait de là).

## Ampleur
- Achats v2 des trois stratégies séismes dans les 10 minutes après la première lecture d'un séisme ≥ 5,5 (54 séismes avec `vu`
  depuis le 11/11) : **1** (celui-ci, 5 €).
- Les autres sources (décomptes officiels horaires, OpenRouter, fleuves, taux) : une fois par lecture, la décision du cycle a utilisé la
  lecture d'une heure avant ; le cas CA-13 du 17/11 (05 h 27) a joué dans l'autre sens (le marché était en retard sur nous), aucun autre
  cas chiffré.

## Correctif
`run_cycle`, étape 6 ter : si au moins une source a été lue (« ok ») pendant la collecte, chaque marché repart de ses références d'avant
le premier rattachement et `references.attach_all` est relancé sur les marchés vivants et la liste surveillée : les stratégies voient
la lecture du cycle même, et une référence qui disparaît à la seconde lecture (hors fenêtre, refus) ne reste pas périmée.
Coût mesuré au cycle local : **1,28 s** (étape `references_apres_collecte`, cycle de 54,8 s).
Test : `tests/test_cycle.py::test_references_are_attached_again_after_the_collection` (échoue sans le correctif).
Limite : un marché qui reçoit sa PREMIÈRE référence à la seconde lecture n'entre dans la liste surveillée qu'au cycle suivant
(le choix des candidats se fait avant les carnets) ; ce retard-là ne fait pas acheter sur une chance périmée.

## Contrôle automatique
Le contrôle `estimation_perimee` (stratégie neuve, écart ≥ 0,30) l'a fait trouver ; un contrôle « achat dans les 10 minutes après
la première lecture d'un séisme » serait redondant maintenant que la lecture du cycle est utilisée.
