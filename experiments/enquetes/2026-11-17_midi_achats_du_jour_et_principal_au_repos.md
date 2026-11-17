# Enquête du 17/11/2026, passage de 11 h : achats du jour relus (famille 4) et principal au repos (famille 1)

Aucune obligation dans la feuille de mission. Jour 17 → famille 6 (faite à 1 h) ; familles 3 et 2 faites à 6 h ; ici familles 4 et 1.

## Constats « à regarder » de l'enquête automatique

- `estimation_perimee` (CA-13 payé 0,70 estimé 0,99) : déjà expliqué à 6 h (marge officielle passée à 25,09 points, vendeur en retard).
- `refus_controleur` : `marges_californie` « carnet périmé » ×2 : même cause que `proposals/2026-11-11_carnet_calme_juge_perime.md`
  (horodatage d'un carnet calme = dernière modification) ; décision d'Etienne toujours attendue, rien à corriger de notre côté.
- `filles_periode` (COPIES CONFORMES), `muettes` (`suivre_inities`), `retraits_inactifs`, `acheteuses_arretees`, `positions_oubliees`
  (Nouvelle-Zélande, officiel le 27/11), `sources_vides`, `sources_indisponibles` (GDELT, PortWatch « Token Required ») : déjà traités
  les 15-17/11, rien de neuf.

## Famille 4 à la main : les 16 achats des fantômes v2 depuis 05 h UTC

Relus contre Gamma (question, prix) et, pour `marges_californie`, contre l'API officielle `api.sos.ca.gov` (lecture du 17/11 11 h UTC,
« ReportingTime » 16/11 19 h 12) :

| stratégie | marché | prix payé | estimé | relu à la source |
|---|---|---|---|---|
| marges_californie | CA-42 « D 20-25 % » | 0,91 | 0,978 | marge 23,89 (ecart_api 23,8) : dans la tranche, conforme |
| marges_californie | CA-02 « D 30-35 % » | 0,92 | 0,99 | 32,88 : conforme |
| marges_californie | CA-18 « D 45 % + » | 0,91 | 0,978 | 46,12 : conforme |
| taux_tresor_empirique | 10 ans « 5,5 % avant 2027 » | 0,09 | 0,185 | plage de prix 0,05-0,90 : conforme ; achat à 05 h 46 (fenêtre 00-12 h UTC) |
| taux_tresor_empirique | 5 ans « 5,03 % en novembre » | 0,36 | 0,468 | conforme ; `max_per_event` 2 respecté (1310114 : 2 jambes, 1310160 : 2) |
| non_aux_drames ×3, favori_politique_quasi_certain ×2 | NON à 0,86-0,97 | — | — | questions et prix conformes à Gamma |

**0 écart** sur 16 achats. Remarque (pas un défaut) : les 8 achats de `taux_tresor_empirique` sont tous du même côté (taux en hausse) :
un seul pari directionnel, comme l'hypothèse le dit ; à juger par événement, pas par achat.

## Famille 1 à la main : le principal

Journal signé : dernier BUY le 07/11 15 h 17, dernier SETTLE le 12/11, RESET le 12/11 13 h 54 ; capital 1 000 €, 0 position, 0 ordre.
Aucune stratégie ne remplit l'entrée (`min_closed_trades` 12, `min_log_growth` 0,02) : `fleuves_prevision` +6,9 % en 2 opérations,
`convictions_claude` +4,4 % en 6, `rt_compte_critiques` +2,2 % en 4. **Conforme aux règles**, mais le capital principal dort depuis
10 jours parce que les stratégies v2 sont lentes (marchés réglés en semaines). Changer le seuil demande un rejeu : noté « reste ouvert ».

## Résultat

Aucun défaut. Rien à corriger, aucun contrôle à ajouter.
