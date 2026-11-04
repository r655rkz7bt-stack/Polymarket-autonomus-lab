# 04/11/2026 (1 h) : copie fidèle du principal et stratégies muettes (familles 5 et 6)

**Question.** Le principal fait-il bien les paris des fantômes qu'il copie, au même prix, et les stratégies qui n'ont
aucune opération disent-elles pourquoi ?

**Copie (famille 5).** `scripts/copie_depuis_28_10_04_11.py` : 233 jetons achetés par le principal depuis le 28/10, comparés
au fantôme copié, jeton par jeton.
- 233 sur 233 ont un achat du fantôme copié (aucun pari « sans fantôme »).
- Écart de prix principal − fantôme : de −0,0028 à +0,0004 en moyenne selon la stratégie, au plus +0,010 (un jeton de
  `contrer_crypto_patiente`). Le principal paie le prix du fantôme à un cran près.
- Rapport de mise principal / fantôme : médiane de 0,03 à 0,53 selon la stratégie (capital du principal 686 € contre
  ≈ 1 200 € pour les fantômes, part confiée à chaque stratégie, prudence) : cohérent, pas de mise démesurée.

**Stratégies muettes (famille 6).** `data.json` → `abstentions.portefeuilles`, 15 stratégies à 0 opération :
chacune dit pourquoi (filtre de familles, fenêtre avant publication, paire cohérente, plage de prix). Les seules sans raison
notée : `detroits_tranches` (PortWatch « Token Required », fiche du 03/11 après-midi), `suivre_inities` et `suivre_inities_seul`
(source `inities` « ok (0 prix relevés) » : aucune grappe de comptes neufs, vérifié en direct le 03/11).

**Résultat.** Aucun défaut de code ; rien à corriger. Contrôles refaits : la copie (déjà `copie_absente`, `copie_prix_paye`),
les muettes (`familles_vides`, `sources_vides`, `retraits_inactifs`).
