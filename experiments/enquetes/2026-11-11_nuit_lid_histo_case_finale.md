# 11/11/2026 (passage de 1 h) — famille 6 : `lid_agenda` tourne-t-il ? et le journal `lid:histo`

**Question (famille 6, « ce qui ne tourne plus »).** Le fantôme `lid_agenda` (né le 10/11 à 21 h) s'abstenait au cycle de 00 h 45 UTC
(« agenda du jour pas encore publié ») : voit-il l'agenda, et son instrument de mesure du regard vers le futur (`lid:histo`) marche-t-il ?

## Ce qui a été vérifié
1. **Source** : `factbase` « ok (20 prix relevés) » ; le calendrier JSON relu à la main à 00 h 56 UTC contient l'agenda du 11/11
   (Veterans Day : 08 h Executive Time, 11 h dépôt de gerbe à Arlington, 11 h 30 discours ; aucune ligne « departs/arrives »). Publié
   après 00 h 45 UTC (19 h 45 à New York) : l'abstention du cycle de 00 h 45 était juste.
2. **Case lue** : « sans voyage, dernier rendez-vous 11:30 » → 0,86 ; marché du 11/11 (6840997) : acheteur 0,61, vendeur 0,94 :
   0,86 − 0,04 < 0,94 + 0,05, pas d'achat attendu (le fantôme a raison de ne rien faire).
3. **Lieu hors de la Maison-Blanche sans ligne de voyage** (cas du jour : Arlington n'apparaît que dans le champ `location`).
   Sur 607 jours d'agenda (mars 2025 → 10/11/2026), case « calme » : lieu à la Maison-Blanche 144 lids sur 166 (0,87) ; lieu ailleurs
   (Mar-a-Lago, Bedminster, Arlington, Capitole…) 60 sur 72 (0,83). Écart de 4 points sur 72 jours : **pas de défaut**, le champ `location`
   n'est pas ajouté à la règle. Exemple proche : 25/05/2026 (Memorial Day, Arlington) → lid. Le 11/11/2025, l'agenda FINAL portait les
   lignes « departs … en route Arlington » (case « voyage avant 17 h ») ; l'agenda de la veille du 11/11/2026 ne les porte pas :
   c'est exactement le regard vers le futur que `lid:histo` doit mesurer.

## Défaut trouvé : `lid:histo` perdait la case finale de l'agenda
- **Constat** (base sauvegardée du 11/11 00 h 01) : pour le 10/11, `premiere` = « case instable (sans voyage, dernier rendez-vous 17:00) »,
  `derniere` = « lid déjà noté à 18:00 ». Dès que le lid est appelé, `record_history` écrivait la case de `assess` (qui renvoie « lid déjà
  noté ») : la case FINALE de l'agenda n'était jamais gardée. La mesure prévue par `experiments/lid_agenda.md` (« comparer la case de
  la veille au soir à la case finale ») aurait été impossible dans 2-3 semaines.
- **Ampleur** : aucun euro (instrument de mesure seulement), 2 jours touchés (09 et 10/11) ; les décisions de la stratégie ne changent pas.
- **Cause** : `src/polymarket_agent/lid.py`, `record_history` appelait `assess` (lid compris).
- **Correctif** : `agenda_case` (case tirée des seules lignes « President Schedule ») ; `assess` l'appelle après le test du lid ;
  `record_history` garde la case d'agenda et l'heure du lid (`lid`) séparément ; un jour vu seulement après son lid : « aucun agenda vu
  avant le lid ». Le 10/11 sera réécrit au prochain cycle (fenêtre d'un jour en arrière).
- **Test** : `tests/test_lid.py::test_history_keeps_the_final_agenda_case_after_the_lid_is_called` (lignes réelles du 10/11).
- **Contrôle automatique** : aucun ajouté (défaut propre à un seul journal ; le test le tient).

## Le reste
- Enquête automatique : constats v1 connus (`sans_test_passe`, concentrations, arène z −13 : stratégies v1 éteintes) ; `gdelt` en panne
  (ReadTimeout, aucune stratégie v2 ne la lit) ; sources à « 0 observation » = météo, MLB, football hors saison/hors surveillance, déjà expliquées le 05/11.

## Deuxième contrôle à la main (famille 3) : règlements des fantômes v2
Les 22 règlements (`SETTLE`) des 9 journaux signés v2 relus sur Gamma (`/markets/<id>`, issue achetée lue dans le `BUY` du même jeton) :
**22 sur 22 conformes** (paiement du journal = `outcomePrices` Gamma, tous `closed` et `resolved`) : Carbon NON 0 (perdue, déjà écrite),
séisme du 07/11 OUI 0, 4 tranches Trump de `compteur_truth`, 14 tranches de `compteur_tweets` (Elon, Trump, CZ, Zelensky), 2 « peace talks »
de `favori_politique_quasi_certain`. Aucun défaut.
